import subprocess,os
import shlex
import time

windows = False
converter = None
def convert(path,filename):
	global converter
	if (converter is not None):
		converter.terminate()
	print(path+filename)
	cmd = "./ffmpeg -threads 4 -i inputfile -map 0 -codec:v libx264 -preset superfast -codec:a aac -ac 2 -crf 23 -flags -global_header -strict experimental -f segment -segment_list playlist.m3u8 -segment_list_flags +live -segment_time 10 tmp/out%03d.ts".replace('inputfile',path+filename)
	

	
	#cmd = 'ls'
	global windows
	if windows:
		cmd.replace('ffmpeg','ffmpeg.exe')
	
	cmd = shlex.split(cmd)
	
	print cmd
	converter = subprocess.Popen(cmd)
	time.sleep(10)

class Converter():
	qualities = ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
	def __init__(self):
		self.converting = False
		self.convFile = ""
		self.q = 3
		self.converter = None
		self.crf = 27 
		self.recentSegment = ""
		
	def start(self,path,filename):
		self.fullTerminate()
		print(path+filename)
		cmd = "./ffmpeg -i inputfile -map 0 -codec:v libx264 -preset quality -codec:a aac -ac 2 -crf constantRateFactor -flags -global_header -strict experimental -f segment -segment_list playlist.m3u8 -segment_list_flags +live -segment_time 10 tmp/out%03d.ts".replace('inputfile',path+filename).replace('quality',self.qualities[self.q]).replace('constantRateFactor',str(self.crf))
		
	
		
		#cmd = 'ls'
		global windows
		if windows:
			cmd.replace('ffmpeg','ffmpeg.exe')
		
		cmd = shlex.split(cmd)
		
		print cmd
		self.converter = subprocess.Popen(cmd)
		self.convFile = filename
		self.converting = True;
		#sleep for a little while so the transcoding can get at leas the first segment done
		sleeptime = 0
		while (os.path.isfile('./tmp/out004.ts') == False):
			time.sleep(2)
			sleeptime+= 2
		print ('slept for %d'%(sleeptime))
		
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
		folder = './tmp'
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception, e:
				print e
	
	def updateRecentSeg(self,segPath):
		self.recentSegment = segPath;
	
	def getPlaylist(self):
		playlist = ""
		passedPrevious = False
		newCount = 0
		#code to keep playlist files only 2 ahead of the most recently requested file
		#seems to help adverting a bug that causes the WiiU to need to refresh
		#also helps as the stream won't be too far from where we left it when you play again
		with open('./playlist.m3u8','r') as f:
			for line in f.readlines():
				if (newCount < 4):
					playlist += line
					if (line == self.recentSegment):
						#only do 4 more lines
						passedPrevious = True;
					if (passedPrevious):
						newCount += 1
					
		return playlist
	
	
# store last sent ts, when asked for new m3u8 give file up to last ts + next two (if they exist)
#include dummy in all .m3u8 files

def getFrame(filepath,outputname):
	if not (os.path.exists(outputname+'.png')):
		cmd = "./ffmpeg -i %s -ss 00:02:30 -f image2 -vframes 1 -s \"160x120\" %s.png"%(filepath,outputname)
		global windows
		if windows:
			cmd.replace('ffmpeg','ffmpeg.exe')
		subprocess.call(shlex.split(cmd))