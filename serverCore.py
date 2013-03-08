from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource
from twisted.web.error import NoResource
import ffmpegHandler, showManager, templateHandler, RottenTomatoHandler
import os, json
from twisted.web.server import NOT_DONE_YET

from twisted.python.log import err
from twisted.protocols.basic import FileSender

platform = 'Mac'
def fileType(fileName):
	return (fileName.split('.')[-1]).lower()



class VidiiUServer(Resource):
	filepath = ''
	children = []
	converter = ffmpegHandler.Converter()
	
	def __init__(self,paths,storage):
		self.filepaths = paths
		self.store = showManager.showStore(storage)
		self.templates = {}
		self.storage = storage
		self.templates['tv'] = templateHandler.template()
		self.templates['settings'] = templateHandler.settingsTemplate()
		self.templates['films'] = templateHandler.filmTemplate()
		self.updateShows();
		self.settings = storage.read('settings')
		
	def updateShows(self):
		print len(self.filepaths)
		if (len(self.filepaths) > 0):
			self.store.updateStore(paths=self.filepaths)
		
	 
	def getChild(self, name, request):
		return self
	

	def render_GET(self, request):
		#print request.path
		if '.' not in request.path:
			#pages not files
			if (request.prepath[0] == 'settings'):
				self.templates['settings'].update()
				qualSettings = self.storage.read('settings')
				return self.templates['settings'].fillTemplate(self.filepaths,qualSettings['sub'],qualSettings['quality'],qualSettings['crf'])
			elif (request.prepath[0] == 'films'):
				#film page
				self.store.updateStore()
				return self.templates['films'].fillTemplate(self.store.store)
			else:
				#index page requested
				self.store.updateStore()
				return self.templates['tv'].fillTemplate(self.store.store)
		
		elif fileType(request.path) in ['png','ico']:
			return self.accessFile(request.prepath[0],request)
		elif (fileType(request.path) in ['mp4','mkv','avi','wmv','mov','mpg','3gp','flv','m4v','m2v','mpeg','ogg','ts'] or ('trans' in request.args and request.args['trans'][0] == 'True')):
			print request
			return self.render_video_GET(request);
	
	def render_POST(self,request):
		postedRAW = "/".join(request.prepath)
		print (postedRAW)
		postData = json.loads(postedRAW)
		if 'dir' in postData:
			return self.getDir(postData)
		elif 'shutdown' in postData:
			#end reactor
			#system exit
			reactor.stop()
			return 'shutdown'
		elif 'rotten' in postData:
			data = RottenTomatoHandler.getJSONForRequest(postData['rotten'])
			#print data
			return data
		elif 'settings' in postData:
			subfolder = postData['settings']['sub']
			crf = postData['settings']['crf']
			quality = postData['settings']['quality']
			self.storage.store({'settings':{'sub':subfolder,'crf':crf,'quality':quality}})
			self.converter.changeQuality(quality)
			self.converter.changeCRF(crf)
			return 'ok'
		elif 'paths' in postData:
			#passback all paths every time (why not)
			#remember to add in paths to the template
			return self.setPaths(postData['paths'])
			
	def setPaths(self,paths):
		print paths
		self.filepaths = paths
		
		self.storage.store({"paths":paths})
		
		self.updateShows()
		return paths
			
	def getDir(self,postedData):
		reqDir = postedData['dir']
		if reqDir == "~":
			#return the base directory (Volumes / Drives)
			global platform
			if (platform == 'Win'):
				dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
				drives = ['%s:\\' % d for d in dl if os.path.exists('%s:' % d)]
				data = {'content':drives,'dirName':''}
				return str(json.dumps(data))
				
			elif (platform == 'Mac'):
				reqDir = "/Volumes"
		try:
			data = {'content':[ name for name in os.listdir(reqDir) if (os.path.isdir(os.path.join(reqDir, name)) and not (name.startswith('.')) and not name.endswith('app') and not name in ['dev','bin','etc','cores','opt','private','usr','sbin','var','tmp'])],'dirName':reqDir}
		except:
			data = {'content':[],'dirName':reqDir}
		returnedData = str(json.dumps(data))
		print returnedData
		return returnedData
	
	def accessFile(self,filepath,request):
		try:
			fileType = (filepath.split('.')[-1])
			request.setHeader('Content-Type',"image/octet-stream")
			if fileType == 'png':
				request.setHeader('Content-Type',"image/png")
				f = open('images/'+filepath,'rb')
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
			print request.path + ' failed'
			return 'failed'

	def render_video_GET(self,request):
		self.isLeaf = False
		if (fileType(request.path) in ['mkv','avi','wmv','mov','mpg','3gp','flv','m4v','m2v','mpeg','ogg'] or ('trans' in request.args and request.args['trans'][0] == 'True')):
			#if the video is of the kind to get transcoded or transcoding has been requested
			request.setHeader('Content-Type',"application/x-mpegurl")
				
			if (self.converter.checkStatus(self.store.pathMap[request.prepath[0]])):
				self.converter.start(self.store.pathMap[request.prepath[0]])
				
			playlist = self.converter.getPlaylist()
			#print playlist
			return playlist
			
			
		elif(fileType(request.path) == 'ts'):
			print request.path
			request.setHeader('Content-Type','video/MP2T')
			self.converter.updateRecentSeg(request.path)
			rangedFile = static.File(request.path[1:],defaultType='video/MP2T')
			return rangedFile.render_GET(request)
			
		else:
			request.setHeader('Content-Type','video/octet-stream')
			print request.getAllHeaders()
			self.isLeaf = False
			rangedFile = static.File(self.store.pathMap[request.prepath[0]],defaultType='video/octet-stream')
			print ('path to ' + self.store.pathMap[request.prepath[0]])
			return rangedFile.render_GET(request)

 



class serverManager():
	def __init__(self,paths=[]):
		self.paths = paths
		self.movieSite = {}
		self.site = {}
		self.vidiiUServer = {}
		self.storage = None
		
	def grabStorage(self,storage):
		self.storage = storage;	
	def run(self):

		self.vidiiUServer = VidiiUServer(self.paths,self.storage)
		self.site = server.Site(self.vidiiUServer)

		reactor.listenTCP(8000, self.site)
		print "listening on both TCPs"
		reactor.run()
		#no code after this point will be run untill the app is quit
		
	def stop(self):
		reactor.stop()
	
	def setPath(self,paths):
		#self.stop()
		self.paths = paths
		
		
		 
