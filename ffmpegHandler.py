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
	time.sleep(15)

def getFrame(filepath,outputname):
	if not (os.path.exists(outputname+'.png')):
		cmd = "./ffmpeg -i %s -ss 00:02:30 -f image2 -vframes 1 -s \"160x120\" %s.png"%(filepath,outputname)
		global windows
		if windows:
			cmd.replace('ffmpeg','ffmpeg.exe')
		subprocess.call(shlex.split(cmd))