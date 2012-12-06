from twisted.internet import reactor
from twisted.web import static, server
from twisted.web.resource import Resource
import ffmpegHandler, showManager, templateHandler, os

class Hello(Resource):
	path = '../../Torrents'
	store = showManager.showStore()
	store.fillStore(path)
	print store
	template = templateHandler.template()
	def getChild(self, name, request):
		return self

	def render_GET(self, request):
		print request.prepath
		if len(request.prepath[0]) < 2:
			return self.template.fillTemplate(self.store.store)
		else:
			return Hello.accessFile(self,request.prepath[0],request)
			

	def accessFile(self,name,request):
		try:
			fileType = (name.split('.')[-1])
			request.setHeader('Content-Type',"video/%s"%fileType)
			if fileType == 'mp4':
				f = file(self.path+'/'+name)
			elif fileType == 'png':
				f = file('images/'+name)
			else:
				#f = ffmpegHandler.convert('test/'+name)
				print 'tried to get %s'%(name)
			return f.read()
		except:
			request.setHeader('Content-Type',"text/plain")
			print name + ' failed'
			return 'failed'

site = server.Site(Hello())
reactor.listenTCP(8000, site)

MovieSite = server.Site(static.File('../../Torrents',defaultType='video/octet-stream'))
reactor.listenTCP(8800, MovieSite)
reactor.run()