import os, time, json, string

class template():
	videobox = """ """
	FileAddress = 'template.html'
	templateFile = open(FileAddress)
	templateString = templateFile.read()
	templateFile.close()
	def update(self):
		self.templateString = open(self.FileAddress).read()
	
	def getVideoBox(self,episode):
		classes = ""
		filename = episode.filename
		if os.path.exists('images/'+episode.filename+'.png'):
			image = episode.filename + '.png'
		else:
			image = '404.png'
		number = episode.number
		date = episode.osdate
		if episode.name is "unknown":
			title = filename
		else:
			title = "Episode %02d"%(number)
		if ((time.mktime(time.gmtime()) - date) < 172800):
			classes += " new"
		transcode = 'false'
		if (episode.fileformat != 'mp4'):
			##print episode.fileformat
			classes += " trans"
			transcode = 'true'
		return r"""<div id="%s" class="videobox %s" onclick="getVideo('%s',%s)">
 <img class="posterimg" src="%s"></img> 
 <h3 class="title">%s</h3>
 <h4 class="date">%s</h4>
 </div>"""%(filename,classes,filename,transcode,image,title,time.ctime(date))


	def getSeason(self,show,season):
		episodes = show.getEpisodesForSeason(season)
		[leftCol,rightCol] = self.unzip(episodes)
		##print rightCol,leftCol
		rightColString = ""
		leftColString = ""
		for episode in rightCol:
			rightColString += self.getVideoBox(episode)
		for episode in leftCol:
			leftColString += self.getVideoBox(episode)
		seasonString = r"""<div class="cols"><H2 class="season">Season %02d</H2>
 <div class="leftcol">
 %s
 
 </div>
 
 <div class="rightcol">
 %s
	 
 </div></div>"""%(season,rightColString,leftColString)
		##print seasonString
		return seasonString
		
		
	def getShow(self,showname,store):
		show = store[showname]
		#print show.seasons
		showString = r"""<div id="%s" class="show">
 <h1 class="showname">%s</h1>"""%(showname.replace(' ',''),showname)
		for season in sorted(show.seasons):
			showString += self.getSeason(show,int(season))
		showString += "</div></div>"
		return showString
		
	#used to start filling the template, will call getShow()	
	def fillTemplate(self,store):
		self.update()
		showsString = ""
		sortedkeys = sorted(store.keys())
		for show in sortedkeys:
			string = self.getShow(show,store)
			if string is not None:
				showsString += string
		if len(showsString) < 2:
			showsString += '<div id="noShows">No shows found <span id="sadFace">:(</span>, please check your path settings.</div>'
		filledTemplate = self.templateString.replace('[[dunstable]]',showsString)
		return str(filledTemplate.encode('utf-8'))
		
	#when given a list will return two lists, one with odd items and one with even within a list 
	def unzip(self,zippedlist):
		left = []
		right = []
		for i in range(0,len(zippedlist)):
			if i % 2 == 0:
				left.append(zippedlist[i])
			if i % 2 == 1:
				right.append(zippedlist[i])
		return [right,left]
	
	
class filmTemplate():
	FileAddress = 'films.html'
	templateFile = open(FileAddress)
	templateString = templateFile.read()
	templateFile.close()
	def updateTemplate(self):
		self.templateString = open(self.FileAddress).read()
	def buildFilmObject(self,episode):
		fileformat = episode.fileformat
		filename = episode.filename
		filmObject = {}
		filmObject['filename'] = filename
		filmObject['id'] = filename.replace(' ','')
		if os.path.exists('images/'+filename+'.png'):
			filmObject['image'] = filename + '.png'
		else:
			filmObject['image'] = '404.png'
		filmObject['title'] = filename.replace('.',' ').replace('-',' ').replace('_',' ').lower().replace('mkv','').replace('mp4','').replace('avi','').strip()
		nonletterIndex = len(filmObject['title']) - len(filmObject['title'].lstrip(string.letters+' '))
		filmObject['title'] = filmObject['title'][:nonletterIndex]
		if fileformat != 'mp4':
			filmObject['trans'] = 1
		else:
			filmObject['trans'] = 0
		return filmObject
	
	def fillTemplate(self,store):
		self.updateTemplate()
		filmObjects = []
		show = store['UNKNOWN']
		#print show.seasons
		showString = ""
		for episode in sorted(show.episodes):				
			filmObjects.append(self.buildFilmObject(episode))
		
		
		return str(self.templateString.replace('[[DUNSTABLE]]',json.dumps(filmObjects)))
	

class settingsTemplate():
	FileAddress = 'settings.html'
	templateFile = open(FileAddress)
	templateString = templateFile.read()
	templateFile.close()
	def update(self):
		self.templateString = open(self.FileAddress).read()

		
		
	def fillTemplate(self,paths,sub,qual,crf):
		pathString = str(paths).replace('[u','[').replace(', u',', ')
		splitter = os.path.join('foo','bar')
		splitter = splitter.replace('foo','"').replace('bar','"')
		if splitter is not '"\"':
			splitter = '"//"'
		return ((((self.templateString.replace('{{PATHS HERE}}',pathString)).replace('{{SUB HERE}}',str(sub))).replace('{{QUAL HERE}}',str(qual))).replace('{{CRF HERE}}',str(crf)).replace('{{PLATFORM SEPERATOR HERE}}',splitter))

	
	
