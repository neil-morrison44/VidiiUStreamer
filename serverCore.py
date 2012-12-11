from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource
import ffmpegHandler, showManager, templateHandler, os


class VidiiUServer(Resource):
	filepath = '../../Torrents'
	children = []
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
			self.store.updateStore()
			return self.template.fillTemplate(self.store.store)
		else:
			return self.accessFile(request.prepath[0],request)
			

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
				#f = ffmpegHandler.convert('test/'+name)
				print 'failed to get %s'%(name)
			return f.read()
		except:
			request.setHeader('Content-Type',"text/plain")
			print name + ' failed'
			return 'failed'


 
		
	
class TransCodingFile(static.File):
	def render(self,request):
		#print request
		#print dir(request)
		#print request.path
		if (request.path.split('.')[-1] != 'mp4'):
			print request.path.split('.')[-1]
			ffmpegHandler.convert('../../Torrents'+request.path)
		request.path = request.path + ".tmp.mp4"
		return static.File.render(self,request)



class serverManager():
	t = {}
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
		
		 
