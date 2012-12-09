import Tkinter as tk
import tkFileDialog
from socket import gethostname
import serverCore
import threading

class ServerGUI(tk.Frame):
	hostname = gethostname()
	running = False
	def __init__(self,sM,master=None):
		self.running = False
		self.dir_opt = options = {}
		self.path = " "*80
		self.serverManager = sM
		
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
		
		
	def getDirectory(self):
		self.path = tkFileDialog.askdirectory(**self.dir_opt)
		self.text_directory["text"] = self.path
		self.serverManager.setPath(self.path)
		print self.path
	def onStop(self):
		if self.running:
			self.serverManager.stop()
			self.status_l1["text"] = "Server Stopped at"
			self.status_l2["fg"] = "gray"
			self.button_stopServer["text"] = "Start Server"
			self.running = False
		else:
			
			self.status_l1["text"] = "Server Running at"
			self.status_l2["fg"] = "black"
			self.button_stopServer["text"] = "Stop Server"
			self.button_stopServer["fg"] = "red"
			self.running = True
			self.serverManager.run()
	
#tkinter doesn't thread well...twisted doesn't thread well. Bugger.
class GUIThread(threading.Thread):
	#thread runner will use "emptyRuns" so it doesn't just run for ever - if the queue's empty for 220 times in a row it'll quit
	def run(self):
		self.root = ServerGUI(self.serverManager)
		self.root.master.title("VidiiU Streamer")
		self.root.mainloop()
		
	def __init__(self, sM,root):
		#print "thread started"
		self.root = root
		threading.Thread.__init__(self)
		self.serverManager = sM
root = {}
t = GUIThread(serverCore.serverManager(),root)
t.start()


#root = ServerGUI(serverCore.serverManager())
#root.master.title("VidiiU Streamer")
#root.mainloop()