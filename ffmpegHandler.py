import subprocess,os
import shlex
import time
import threading

windows = False
converter = None
shush = True

class Converter():
	qualities = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
	def __init__(self):
		self.converting = False
		self.convFile = ""
		self.q = 3
		self.converter = None
		self.crf = 27 
		self.recentSegment = ""
		self.playlist = ""
		self.plineCount = 0 
		self.skipper = 0
		self.timer = 0
		self.checkingThread  = None
		
	def start(self,filepath):
		self.fullTerminate()
		print(filepath + 'started new transcoding')
		
		cmd = u"./ffmpeg -i inputfile -map 0 -map -0:s -dn -codec:v libx264 -preset quality -profile:v high444 -codec:a aac -ac 2 -crf constantRateFactor -flags -global_header -strict experimental -f segment -segment_list playlist.m3u8 -segment_list_flags +live -segment_time 10 tmp/out%03d.ts".replace('inputfile',quoterise(filepath)).replace('quality',self.qualities[self.q]).replace('constantRateFactor',str(self.crf))
		
		self.checkingThread = minCheckThread(self)
		self.checkingThread.daemon = True
		self.checkingThread.start()
		
		#cmd = 'ls'
		
		global windows
		if windows:
			cmd.replace('ffmpeg','ffmpeg.exe')
		
		s = cmd.encode('utf-8')
		cmd = decodeShlex(shlex.split(s))
		
		print cmd
		fh = open("NUL","w")
		self.converter = subprocess.Popen(cmd,shell=False,stdout = fh, stderr = fh)
		#self.converter = subprocess.Popen(cmd,shell=False)
		
		self.playlist = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-ALLOWCACHE:1
#EXT-X-TARGETDURATION:10"""
		self.plineCount = 0
		self.convFile = filepath
		self.converting = True

		
	def checkStatus(self,filename):
		return (self.convFile != filename)
	
	def changeQuality(self,quality):
		self.q = quality
	def changeCRF(self,c):
		self.crf = c
	
	def fullTerminate(self):
		if (self.converting):
			self.converter.terminate()
			time.sleep(1)
		self.recentSegment = ""
		self.convFile = ""
		self.playlist = ""
		self.plineCount = 0
		self.skipper = 0 
		if os.path.isfile('./playlist.m3u8'):
			os.unlink('./playlist.m3u8')
		folder = './tmp'
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception, e:
				print e
		self.converting = False
	
	def updateRecentSeg(self,segPath):
		self.recentSegment = segPath;
		self.timer = time.mktime(time.gmtime())
	
	def getPlaylist(self):
		
		passedPrevious = False
		newCount = 0
		#code to keep playlist files only 2 ahead of the most recently requested file
		#seems to help adverting a bug that causes the WiiU to need to refresh
		#also helps as the stream won't be too far from where we left it when you play again
		
		
		#to be changed to point to non-continuous buffering video at start
		try:
			copylines = []
			with open('./playlist.m3u8','r') as f:
				copylines = []
				lineCount = 0
				for line in f.readlines():
					if (line == self.recentSegment):
						#only do 2 more lines
						passedPrevious = True;
					#the linecount > 6... in the next line skips the header + first two lines (to stop the speedup), change to 4 for speed up glitch
					if ((newCount < 4) and (lineCount > 6+self.plineCount)):
						copylines.append(line)
						if (passedPrevious):
							newCount += 1
					lineCount +=1
				#print copylines
				if len(copylines) < 2:
					raise Exception('Not enough segments')
				else:
					for line in copylines:
						self.playlist += line
						self.plineCount+=1
						
		except:
			if (self.skipper == 0 and self.plineCount == 0):
				#print ('IO Error, adding')
				#self.playlist+="\n#EXTINF:7.674333,\nloading.ts\n#EXT-X-DISCONTINUITY\n\n"
				self.playlist+="\n#EXTINF:5.500000,\nloading.ts\n#EXT-X-DISCONTINUITY\n\n"
				
				self.skipper = 2
			self.skipper -=1
		poll = self.converter.returncode
		#print self.converter.poll()
		
		if (poll is not None and poll > 0):
			print 'ffmpeg failed'
			self.converting = False
			self.fullTerminate()
			return "failed"	
		#print self.playlist				
		return self.playlist
	
	
class minCheckThread(threading.Thread):
	daemon = True
	#thread runner will use "emptyRuns" so it doesn't just run for ever - if the queue's empty for 220 times in a row it'll quit
	def run(self):
		#print 'checking thread running'
		while (self.running):
			time.sleep(6)
			if (self.converter.timer < (time.mktime(time.gmtime())-60)):
				#print 'full termination from Thread because %d < %d'%(self.converter.timer,(time.mktime(time.gmtime())-60))
				self.converter.fullTerminate()
			#else:
			#print 'no termination from Thread because %d > %d'%(self.converter.timer,(time.mktime(time.gmtime())-60))
			if (self.converter.converting == False):
				#print 'the converter ain\'t running so i ain\'t too' 
				self.running = False
			
		
	def __init__(self, converter):
		#print "thread started"
		threading.Thread.__init__(self)
		self.converter = converter
		self.running = True
		
def quoterise(s): 
	return '"'+s+'"'
def decodeShlex(shellparts):
	return [unicode(spart,'utf-8') for spart in shellparts]

def getFrame(filepath,outputname):
	if not (os.path.exists(outputname+'.png')):
		cmd = u"./ffmpeg -ss 00:02:30 -i %s -f image2 -vframes 1 -s \"160x120\" %s.png"%(quoterise(filepath),quoterise(outputname))
		global windows
		if windows:
			cmd.replace('ffmpeg','ffmpeg.exe')
			
		fh = open("NUL","w")
		
		s = cmd.encode('utf-8')
		cmd = decodeShlex(shlex.split(s))
			
		subprocess.call(cmd,shell=False,stdout = fh, stderr = fh)
		#subprocess.call(shlex.split(cmd),shell=False)
		fh.close()