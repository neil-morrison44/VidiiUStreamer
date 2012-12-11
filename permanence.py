import urllib, os,json

thisVersion = 0.8
#manually changing this bit for the Mac/Windows builds...I know it's ugly but shuttup.
thisPlatform = 'Mac'

def checkUpdate():
	url = "http://www.vidiiUstreamer.com/updateManifest.json"
	try:
		updateManif = urllib.urlopen(url)
		updateObject = json.loads(updateManif.read())
		print updateObject["version"]
		global thisVersion
		global thisPlatform
		link = str(updateObject["link"]).replace('%s',thisPlatform)
		if thisVersion < updateObject["version"]:
			updateString = "Changes include... %s"%(updateObject["changes"])
		else:
			print "latest"
			raise Exception("This version is latest.")
		return [updateString,link]
	except:
		#either not connected to the internet or what we got wasn't JSON. no biggy.
		print "update failed"
		return False


class localStorage():
	datadict = {}
	datafile = "config.txt"
	def __init__(self):
		self.datadict = {}
		if not (os.path.exists(self.datafile)):
			open("config.txt",'w+').write("{}")
			self.datadict = {}
		self.datadict = json.load(open("config.txt",'r'))
		
	
	
	def store(self,newdict):
		for key in newdict.keys():
			self.datadict[key] = newdict[key]
		self.write()
	def read(self,key):
		try:
			return self.datadict[key]
		except:
			return " "*80
	def clear(self):
		self.datadict = {}
		open("config.txt",'w+').write("{}")
	
	def write(self):
		open("config.txt",'w+').write(json.dumps(self.datadict))

