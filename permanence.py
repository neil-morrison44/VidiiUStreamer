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
		if thisVersion < updateObject["version"]:
			print "update available, download at %s. Changes include... %s"%(updateObject["link"],updateObject["changes"])
		
		return [updateString,updateObject["link"]]
	except:
		#either not connected to the internet or what we got wasn't JSON. no biggy.
		print "update failed"
		return False

#test
checkUpdate()

class localStorage():
	datadict = {}
	def __init__():
		datafile = "settings.txt"
		datadict = json.load(open("settings.txt").read())
		
	
	
	def store(self,valuepair):
		pass
	def read(self,key):
		pass