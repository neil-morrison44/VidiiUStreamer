import tkMessageBox
import socket
import serverCore
import time
import permanence
import webbrowser
import threading

#import pdb
#pdb.set_trace()
def getIPaddress():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8',80))
	IP = s.getsockname()[0]
	s.close()
	return IP

class openBrowserThread(threading.Thread):
	def run(self):
		time.sleep(1)
		webbrowser.open('http://'+self.hostname+':8000/settings',new=1,autoraise=True)
	def __init__(self,hostname):
		threading.Thread.__init__(self)
		self.hostname = hostname


class ServerLauncher():
	hostname = getIPaddress()
	storage = permanence.localStorage()
	running = False
	def __init__(self,sM):
		self.running = False
		self.dir_opt = options = {}
		self.serverManager = sM
		self.paths = self.storage.read("paths")
		self.serverManager.grabStorage(self.storage)
		if (self.paths != []):
			self.serverManager.setPath(self.paths)
			print self.paths
			
		#update check on launch
		update = permanence.checkUpdate()
		if (update != False):
			if (tkMessageBox.askyesno("Download Update?",update[0])):
				webbrowser.open_new(update[1])
				
		#webbrowser.open_new('http://'+self.hostname+':8000/settings')
		thread = openBrowserThread(self.hostname)
		thread.start()
		#webbrowser.open('http://'+self.hostname+':8000/settings',new=1,autoraise=True)
		self.serverManager.run()
		print 'goodbye'
		
		
			

ServerLauncher(serverCore.serverManager())

