import Tkinter as tk
import tkFileDialog

root = tk.Tk()


class ServerGUI:
	def __init__(self,master):
		self.dir_opt = options = {}
		self.path = ""
		
		frame = tk.Frame(master,height=3)
		
		
		frame.columnconfigure(0, pad=3)
		frame.columnconfigure(1, pad=3)
		frame.columnconfigure(2, pad=3)
		frame.columnconfigure(3, pad=3)
		
		frame.rowconfigure(0, pad=3)
		frame.rowconfigure(1, pad=3)
		frame.rowconfigure(2, pad=3)
		frame.rowconfigure(3, pad=3)
		frame.rowconfigure(4, pad=3)
		
		frame.pack()
		self.label_directory = tk.Label(frame,text="Content Directory:")
		self.label_directory.grid(row=0,column=0)
		self.label_directory.pack(side=tk.LEFT)
		
		self.button_directory = tk.Button(frame,text="Browse",command=self.getDirectory)
		self.button_directory.pack(side=tk.RIGHT)
		
		self.text_directory = tk.Label(frame,text="//"+self.path,bg="white",bd=1)
		self.text_directory.pack(side=tk.LEFT,fill=tk.X)
		
		self.button_stopServer = tk.Button(frame, text="Stop Server", fg="red",command=frame.quit)
		self.button_refreshShows = tk.Button(frame, text="Refresh Shows", fg="red",command=frame.quit)
		self.button_refreshShows.pack(side=tk.LEFT)
		self.button_stopServer.pack(side=tk.BOTTOM)
		
		self.status = tk.Label(frame,text="Server Running")
		self.status.pack(side=tk.BOTTOM)
		
		
	def getDirectory(self):
		self.path = tkFileDialog.askdirectory(**self.dir_opt)
		print self.path
	

controls = ServerGUI(root)
root.geometry("300x280")
root.title("VidiiU Streamer")
root.mainloop()