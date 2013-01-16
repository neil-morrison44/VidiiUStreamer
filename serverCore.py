from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource
from twisted.web.error import NoResource
import ffmpegHandler, showManager, templateHandler, os, json
from twisted.web.server import NOT_DONE_YET

from twisted.python.log import err
from twisted.protocols.basic import FileSender

platform = 'Mac'
def fileType(fileName):
	return fileName.split('.')[-1]

class VidiiUServer(static.File):
	filepath = ''
	children = []
	converter = ffmpegHandler.Converter()
	def __init__(self,path):
		self.filepath = path
		self.store = {}
		self.template = {}
		
	def getShows(self):
		self.store = showManager.showStore()
		self.store.fillStore(self.filepath)
		self.template = templateHandler.template()
		
	def getChild(self, name, request):
		return self

	def render_GET(self, request):
		#print request.prepath
		if len(request.prepath[0]) < 2:
			#index page requested
			self.store.updateStore()
			return self.template.fillTemplate(self.store.store)
		elif fileType(request.prepath[0]) in ['png','ico']:
			return self.accessFile(request.prepath[0],request)
		else:
			pass
	
	def render_POST(self,request):
		print request.__dict__
		postedData = request.content.getvalue()
		print (postedData)
		postedData = json.loads(postedData)
		if 'dir' in postedData:
			self.getDir(postedData)
		elif 'end' in postedData:
			#fire termination of video
			print('video ended')
			return 'video ended'
			
	def getDir(self,postedData):
		reqDir = postedData['dir']
		if reqDir == "":
			#return the base directory (Volumes / Drives)
			global platform
			if (platform == 'Win'):
				dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
				drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
				data = {'reqDir':drives}
				return str(json.dumps(data))
				
			elif (platform == 'Mac'):
				reqDir = "/Volumes"
		data = {'reqDir':[ name for name in os.listdir(reqDir) if (os.path.isdir(os.path.join(reqDir, name)) and not (name.startswith('.')))]}
		
		return str(json.dumps(data))
	
	def accessFile(self,name,request):
		try:
			fileType = (name.split('.')[-1])
			request.setHeader('Content-Type',"image/octet-stream")
			if fileType == 'png':
				request.setHeader('Content-Type',"image/png")
				f = open('images/'+name,'rb')
			elif fileType == 'ico':
				request.setHeader('Content-Type',"image/ico")
				f = open('images/favicon.ico','rb')
			else:
				print 'failed to get %s'%(name)
			def cbFinished(ignored):
					f.close()
					request.finish()
			d = FileSender().beginFileTransfer(f,request)
			d.addErrback(err).addCallback(cbFinished)
			return NOT_DONE_YET
		except:
			request.setHeader('Content-Type',"text/plain")
			print name + ' failed'
			return 'failed'


 
once = True		
	
class TransCodingFile(static.File):
	isLeaf = True
	converter = ffmpegHandler.Converter()
	
	def render_GET(self,request):
		self.isLeaf = False
		print request
		if (fileType(request.path) in ['mkv','avi','wmv','mov','mpg','3gp','flv','m4v','m2v','mpeg','ogg'] or ('trans' in request.args and request.args['trans'][0] == 'True')):
			#if the video is of the kind to get transcoded or transcoding has been requested
			request.setHeader('Content-Type',"application/x-mpegurl")
				
			if (self.converter.checkStatus(request.path)):
				self.converter.start(self.path,request.path)
				
			playlist = self.converter.getPlaylist()
			print playlist
			return playlist
			
			
		elif(fileType(request.path) == 'ts'):
		
			request.setHeader('Content-Type','video/MP2T')
			self.converter.updateRecentSeg(request.path)
			f = open(request.path[1:],'rb')
			
			def cbFinished(ignored):
				f.close()
				request.finish()
			
			d = FileSender().beginFileTransfer(f,request)
			d.addErrback(err).addCallback(cbFinished)
			return NOT_DONE_YET
			
		else:
			request.setHeader('Content-Type','video/octet-stream')
			self.isLeaf = False
			return static.File.render_GET(self,request)



class serverManager():
	def __init__(self,path=""):
		self.path = path
		self.movieSite = {}
		self.site = {}
		self.vidiiUServer = {}
		
	def run(self):

		self.vidiiUServer = VidiiUServer(self.path)
		self.vidiiUServer.getShows()
		self.site = server.Site(self.vidiiUServer)
		self.movieSite = server.Site(TransCodingFile(self.path,defaultType='video/octet-stream'))
		reactor.listenTCP(8800, self.movieSite)
		reactor.listenTCP(8000, self.site)
		print "listening on both TCPs"
		reactor.run()
		print "reactor running"
		
	def stop(self):
		reactor.stop()
	
	def setPath(self,path):
		#self.stop()
		self.path = path
		
		 
