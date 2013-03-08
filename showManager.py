import os, re, time, copy
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
		return sorted([ episode for episode in self.episodes if (episode.season is seasonnum)], key = lambda episode: episode.number)
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
	daemon = True
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
	filelist = []
	pathMap = {}
	def __init__(self,storage):
		self.store = {}
		self.path = ""
		self.filelist = ""
		self.storage = storage
		self.filelist = []
	
	def add(self,item):
		self.store[item] = []
		
	def updateStore(self,paths=None):
		infoTime = False
		if (paths is not None):
			self.paths = paths
			infoTime = True
		newfilelist = []
		queue = Queue.Queue()
		for i in range(3):
			t = imageThread(queue)
			t.daemon = True
			t.start()
		allfilelist = []
		subfolders = True;
		if(self.storage.read('settings')['sub'] == 0):
			subfolders = False;
		tmppaths = copy.copy(self.paths)
		
		pathDisconnected = False
		
		for path in tmppaths:
			fileandsublist = self.getFileList(path)
			if (fileandsublist == False):
				#we get here if a drive has been disconnected or the shows can't be accessed for some other reason
				#empty the store since it now contains links that won't lead anywhere
				self.store = {}
				#and the out of date filelist too
				self.filelist = []
				#the rest will only fill using things that were found
				
			elif(fileandsublist is not False):
				allfilelist.extend(fileandsublist[0])
				if(subfolders):
					tmppaths.extend(fileandsublist[1])
					
			
		for filenameandpath in allfilelist:
			if filenameandpath[0] not in [filename[0] for filename in self.filelist ]:
				newfilelist.append(filenameandpath)
				self.filelist.append(filenameandpath)
		
		for moviefile in newfilelist:
			d = detailPlucker(moviefile)
			thisEpisode = episode()
			fullpath = os.path.join(moviefile[1],moviefile[0])
			thisEpisode.setDetails(d['episode'],d['show'],d['season'],d['filetype'],moviefile[0],fullpath)
			thisEpisode.osdate = os.path.getctime(fullpath)
			self.pathMap[moviefile[0]] = fullpath
			##print details['show']
			showname = str.upper(str(d['show']))
			
			queue.put({'path':moviefile[1],'mv':moviefile[0]})
			
			if showname not in self.store:
				self.store[showname] = show()
				self.store[showname].name = showname
				self.store[showname].addEpisode(thisEpisode)
			else:
				self.store[showname].addEpisode(thisEpisode)
			if d['season'] not in self.store[showname].seasons:
				self.store[showname].seasons.append(d['season'])
		if (infoTime):
			for showp in self.store.keys():
				self.store[showp].printInfo()
		
		
	def __unicode__(self):
		return self.store.name
	
	def getFileList(self,path):
		#if the path is not accessable return false
		if not (os.path.exists(path)):
			return False
		#when given a path return an array of all videos within said path
		filelist = os.listdir(path)
		files = [file for file in filelist if ((file.split('.')[-1]).lower() in ['mp4','mkv','avi','wmv','mov','mpg','3gp','flv','m4v','m2v','mpeg','ogg'])]
		
		i = 0
		while (i < len(files)):
			files[i] = [files[i],path]
			i+=1;
		#also return list of directories
		
		subdirs = [ os.path.join(path,name) for name in filelist if (os.path.isdir(os.path.join(path, name)) and not (name.startswith('.')) and not name.endswith('app') and not name in ['dev','bin','etc','cores','opt','private','usr','sbin','var','tmp'])]
		
		return [files,subdirs]

def detailPlucker(episodeDetails):
	#Supports SHOW s01e01 ect
	#Support SHOW - SEE - TITLE
	episodeString = episodeDetails[0]
	show = ""
	episode = 0
	season = 0
	filename = episodeString
	episodeString = episodeString.replace('a.k.a.','aka').replace('e.g','eg')
	# Error checking omitted!
	parts = episodeString.split('.')
	filetype = parts[-1]
	#some ugly code to get around a problem with files conatining a.k.a. ect if there's more than 1 single letter elements kill it
	if (len(parts) < 3):
		parts = episodeString.split('-')
	if (len(parts) < 3):
		parts = episodeString.split('_')
	known = False
	index = 0
	
	regexes = [r"(?:s|season)(\d{2})(?:e|x|episode|\n)(\d{2})",r"^(\d{1,2})(?:e|x|episode|\n)(\d{1,2})$",r"^(\d{2})(\d{2})$",r"^(\d{1})(\d{2})$"]
	
	for part in parts:
		if(known):
			break
		part = part.strip()
		match = None
		i = 0
		while (((match is None)) and i < len(regexes)):
			match = re.search(regexes[i], part,re.I)
			i+=1
			
		if match is not None:	
			episode = int(match.group(2))
			season = int(match.group(1))
			show = (' '.join(parts[:index])).strip()
			known = True
			if (i==3):
				#hacky clunge to support shows like the daily show, if films have .2013. in them this will cause problems...hmm.
				try:
					episode = int(parts[index]+parts[index+1]+parts[index+2])
				except:
					episode = 4000
					known = False
				season = 0
			
		index += 1
	if known is False:
		show = "unknown"
	
	
	##print episode,season,filetype
	##print show
	return {'show':show,'season':season,'episode':episode,'filetype':filetype,'path':episodeDetails[1]}

