import subprocess,os
import shlex
def convert(filename):
    cmd = "ffmpeg -i %s input -acodec aac -ab 128kb -vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv+trell -aic 2 -cmp 2 -subcmp 2 -s 320x180 -title X %s.tmp.mp4"%(filename,filename)
    print cmd
    subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def getFrame(filepath,outputname):
	if not (os.path.exists(outputname+'.png')):
		command = "ffmpeg -i %s -ss 00:02:30 -f image2 -vframes 1 -s \"160x120\" %s.png"%(filepath,outputname)
		subprocess.call(shlex.split(command))