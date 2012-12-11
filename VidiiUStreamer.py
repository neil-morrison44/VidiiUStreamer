import Tkinter as tk
import tkMessageBox
import tkFileDialog
from socket import gethostname
import serverCore
import time
import permanence
import webbrowser

#import pdb
#pdb.set_trace()

class ServerGUI(tk.Frame):
	hostname = gethostname()
	storage = permanence.localStorage()
	running = False
	def __init__(self,sM,master=None):
		self.running = False
		self.dir_opt = options = {}
		self.serverManager = sM
		self.path = " "*80
		self.path = str(self.storage.read("path"))
		if (self.path != " "*80):
			self.serverManager.setPath(self.path)
			print self.path
		
		tk.Frame.__init__(self,master)
		self.grid()
		self["bg"] = "white"
		self.label_directory = tk.Label(self,text="Video Directory:")
		self.label_directory.grid(row=0,column=0)
		
		self.button_directory = tk.Button(self,text="Browse",command=self.getDirectory)
		self.button_directory.grid(row=1,column=2)
		
		self.text_directory = tk.Label(self,text=self.path,bg="white",bd=1,relief="solid")
		self.text_directory.grid(row=1,column=1,columnspan=1)
		
		self.button_stopServer = tk.Button(self, text="Start Server", fg="red",command=self.onStop)
		self.button_refreshShows = tk.Button(self, text="Refresh Shows", fg="red",command=self.quit)
		self.button_refreshShows.grid(row=4,column=0)
		self.button_stopServer.grid(row=4,column=2)
		
		self.status_l1 = tk.Label(self,text="Server Stopped at:")
		self.status_l1.grid(row=2,column=0)
		self.status_l2 = tk.Label(self,text="http://%s:8000"%(self.hostname),fg="gray")
		self.status_l2.grid(row=3,column=1)
		
		self.warningLabel = tk.Label(self,text="WARNING: When you start the server this window will minimise then appear to crash. This means it's working.", fg="red")
		self.warningLabel.grid(row=6,columnspan=3)
		
		self.warningLabel2 = tk.Label(self,text="Sorry about that. There'll be an update to make it nicer soon...",fg="red")
		self.warningLabel2.grid(row=7,columnspan=3)
		
		#update check on launch
		update = permanence.checkUpdate()
		if (update != False):
			if (tkMessageBox.askyesno("Download Update?",update[0])):
				webbrowser.open_new(update[1])
			
	def getDirectory(self):
		newpath = tkFileDialog.askdirectory(**self.dir_opt)
		if newpath != "":
			self.path = newpath
		self.text_directory["text"] = self.path
		self.serverManager.setPath(self.path)
		print self.path
		self.storage.store({"path":self.path})
		if (self.storage.read("FirstRun") == 1):
			tkMessageBox.showinfo("First Run...","This looks like the first time you've run this, your computer will work quite hard generating the thumbnail images for all the videos.")
			self.storage.store({"FirstRun":0})
	def onStop(self):
		if self.running:
			self.serverManager.stop()
			self.status_l1["text"] = "Server Stopped at:"
			self.status_l2["fg"] = "gray"
			self.button_stopServer["text"] = "Start Server"
			self.running = False
		else:
			if (self.path != " "*80):
				self.status_l1["text"] = "Server Running at:"
				self.status_l2["fg"] = "black"
				self.button_stopServer["text"] = "Stop Server"
				self.button_stopServer["state"] = tk.DISABLED
				self.button_refreshShows["state"] = tk.DISABLED
				self.button_directory["state"] = tk.DISABLED
				self.button_stopServer["fg"] = "red"
				self.running = True
				#self.master.wm_state('iconic')
				self.master.update_idletasks()
				time.sleep(4)
				self.master.iconify()
				self.serverManager.run()
			else:
				tkMessageBox.showinfo("No Path Set","Please set the location for your videos by clicking 'Browse'.")
	
#tkinter doesn't thread well...twisted doesn't thread well. Bugger.


root = ServerGUI(serverCore.serverManager())
root.master.title("VidiiU Streamer [Beta]")
root.mainloop()