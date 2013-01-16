import os, re, time
import ffmpegHandler
import threading, Queue

class show():
	name = ""
	seasons = []
	episodes = []
	def addSeason(self,num):
		self.seasons.append(num)
	def __init__(self):
		self.episodes = []
		self.seasons = []
		self.name = ""
	
	def addEpisode(self,episode):
		self.episodes.append(episode)
	def getEpisodesForSeason(self,seasonnum):
		eplist = []
		for episode in self.episodes:
			if episode.season is seasonnum:
				 eplist.append(episode)
		return eplist
	def __unicode__(self):
		return "%s: %d episodes "%(self.name,len(self.episodes)) + self.seasons + ""
	def printInfo(self):
		print("show %s has the seasons %s and %d episodes"%(self.name,self.seasons,len(self.episodes)))
	

class episode():
	number = 0
	name = ""
	fullpath = ""
	season = 0
	osdate = 0
	misc = False
	image = ""
	fileformat = ""
	filename = ""
	def setDetails(self,number,name,season,ff,fn,path):
		self.number = number
		self.name = name
		self.season = season
		self.osdate = 0
		self.fileformat = ff
		self.filename = fn
		self.fullpath = path
	def __unicode__(self):
		return ""
		
		
		
class imageThread(threading.Thread):
	#thread runner will use "emptyRuns" so it doesn't just run for ever - if the queue's empty for 220 times in a row it'll quit
	def run(self):
		emptyRuns = 0
		while (emptyRuns < 220):
			if (self.queue.empty()):
				emptyRuns += 1
			else:
				emptyRuns = 0
			movie = self.queue.get()
			path = movie['path']
			moviefile = movie['mv']
			#print "just got %s on the %s path"%(moviefile,path)
			ffmpegHandler.getFrame(path+'/'+moviefile,"./images/"+moviefile)
			self.queue.task_done()
		
	def __init__(self, queue):
		#print "thread started"
		threading.Thread.__init__(self)
		self.queue = queue
		
		
class showStore():
	store = {}
	path = ""
	filelist = ""
	def __init__(self):
		self.store = {}
		self.path = ""
		self.filelist = ""
	
	def add(self,item):
		self.store[item] = []
		
	def fillStore(self,path):
		self.store = {}
		self.path = path
		
		queue = Queue.Queue()
		for i in range(2):
			t = imageThread(queue)
			t.start()
		
		filelist = self.getFileList(path)
		self.filelist = filelist
		for moviefile in filelist:
			#print moviefile
			d = detailPlucker(moviefile)
			thisEpisode = episode()
			thisEpisode.setDetails(d['episode'],d['show'],d['season'],d['filetype'],moviefile,os.path.join(self.path,moviefile))
			thisEpisode.osdate = os.path.getctime(os.path.join(self.path,moviefile))
			##print details['show']
			showname = str.upper(str(d['show']))
			
			queue.put({'path':path,'mv':moviefile})
			
			if showname not in self.store:
				self.store[showname] = show()
				self.store[showname].name = showname
				self.store[showname].addEpisode(thisEpisode)
			else:
				self.store[showname].addEpisode(thisEpisode)
			if d['season'] not in self.store[showname].seasons:
				self.store[showname].seasons.append(d['season'])
		for showp in self.store.keys():
			self.store[showp].printInfo()
	
	def updateStore(self):
		newfilelist = []
		queue = Queue.Queue()
		for i in range(2):
			t = imageThread(queue)
			t.start()
		allfilelist = self.getFileList(self.path)
		for filename in allfilelist:
			if filename not in self.filelist:
				newfilelist.append(filename)
		for moviefile in newfilelist:
			#print moviefile
			d = detailPlucker(moviefile)
			thisEpisode = episode()
			thisEpisode.setDetails(d['episode'],d['show'],d['season'],d['filetype'],moviefile,os.path.join(self.path,moviefile))
			thisEpisode.osdate = os.path.getctime(os.path.join(self.path,moviefile))
			##print details['show']
			showname = str.upper(d['show'])
			
			queue.put({'path':self.path,'mv':moviefile})
			
			if showname not in self.store:
				self.store[showname] = show()
				self.store[showname].name = showname
				self.store[showname].addEpisode(thisEpisode)
			else:
				self.store[showname].addEpisode(thisEpisode)
			if d['season'] not in self.store[showname].seasons:
				self.store[showname].seasons.append(d['season'])
		for showp in self.store.keys():
			self.store[showp].printInfo()
		
		
	def __unicode__(self):
		return self.store.name
	
	def getFileList(self,path):
		filelist = os.listdir(path)
		return [file for file in filelist if (file.split('.')[-1] == 'mp4' or file.split('.')[-1] == 'mkv')]
		

def detailPlucker(episodeString):
	#Supports SHOW s01e01 ect
	
	#Support SHOW - SEE - TITLE
	show = ""
	episode = 0
	season = 0
	filename = episodeString
	# Error checking omitted!
	parts = episodeString.split('.')
	known = False
	index = 0
	for part in parts:
		match = re.search(r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})", part,re.I)
		if match is not None:
			episode = int(match.group(2))
			season = int(match.group(1))
			show = ' '.join(parts[:index])
			known = True
		index += 1
	if known is False:
		show = "unknown"
	
	filetype = parts[-1]
	##print episode,season,filetype
	##print show
	return {'show':show,'season':season,'episode':episode,'filetype':filetype}

