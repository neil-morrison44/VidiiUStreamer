import urllib, os,json

thisVersion = 0.8
thisPlatform = 'Mac'

def checkUpdate():
	url = "updateManifest.json"
	updateManif = urllib.urlopen(url)
	updateObject = json.loads(updateManif.read())
	print updateObject["version"]
	global thisVersion
	if thisVersion < updateObject["version"]:
		print "update available, download at %s. Changes include... %s"%(updateObject["link"],updateObject["changes"])
	
	return [updateString,updateObject["link"]]

#test
checkUpdate()

class localStorage():
	datadict = {}
	def __init__():
		datafile = "settings.txt"
		datadict = json.load(open("settings.txt").read())
		
	
	
	def store(self,valuepair):
	
	def read(self,key):
		