import sys
import re
import PorterStemmer
import math
import time
#setup: collection words:
#(document frequency, collection docs)
#docs: (docnumber, (loc1,loc2,loc3))

#new format: word docfreq docnumber loc1 loc2 loc3 loc4, docnumber loc1 loc2 loc3

words={}
p = PorterStemmer.PorterStemmer()

#collectionString = swf.read()
#swf.close()

#indexFile = open(sys.argv[3],'w')
#titleFile = open(sys.argv[4],'w')

idCheck = re.compile('(.*?)(<id>)(.*?)(</id>)', re.DOTALL)
titleCheck = re.compile('(.*?)(<title>)(.*?)(</title>)', re.DOTALL)
textCheck = re.compile('(.*?)(<text>)(.*?)(</text>)', re.DOTALL)
linkCheck = re.compile('(.*?)(\[\[)(.*?)([\]\|\#])',re.DOTALL)

#USAGE OF LINK CHECK
'''text = '[[Assembly Language|ass]][[gjgjeioaw]][[Allhogp#fewag]]'
m = linkCheck.findall(text)
for x in m:
	print x[2]
'''

docs = {}
linkListsDictionary = {}

'''HERE"S MY TEST'''
words = {}
doclengths = []
docIDS = []
def parsePage(page):
	terms = {}
	ID = idCheck.search(page).group(3)
	title = titleCheck.search(page).group(3)
	#titleFile.write(str((ID,title)) + '\n')
	text = ' ' + textCheck.search(page).group(3)
	text += " " + title;
	text = text.lower()
	text = re.sub('(_|\n)',' ',text)
	text = re.sub(r'\W+',' ',text)
	text = re.sub('\s+',' ',text)
	text = text.split(' ')
	doclengths.append(0)
	docIDS.append(ID)
	for i in range(0,len(text)):
		#doclengths[len(doclengths)-1]+=1
		text[i] = p.stem(text[i], 0, len(text[i])-1)
	text = [t for t in text if t not in stopWords]
	for i in range(0,len(text)):
		if text[i] in terms:
			terms[text[i]] = terms[text[i]]+1
		else:
			terms[text[i]] = 1
		if text[i] in words:
			wordresult = words[text[i]]
			freq = wordresult[0]+1
			if ID in wordresult[1]:
				doclocations = wordresult[1][ID]
				doclocations += ' ' + str(i)
				wordresult[1][ID] = doclocations
				wordresult=(freq,wordresult[1])
			else:
				doclocations = str(i)
				wordresult[1][ID] = doclocations
				wordresult=(freq,wordresult[1])
			words[text[i]] = wordresult
		else:
			wordresult = (1,{ID:str(i)})
			words[text[i]] = wordresult
	for k,v in terms.iteritems():
		doclengths[len(doclengths)-1]+=int(v)*int(v)

	
def makeIDPair(page):
	terms = {}
	ID = idCheck.search(page).group(3)
	title = titleCheck.search(page).group(3)
	docs[title]=ID



def makeDocIDDictionary():
	swf = open(sys.argv[1],'r')
	swf.readline()
	currentPage = ''
	for line in swf:
		if (not (line.find('<page>')>-1 or line.find('</page>')>-1)):
			currentPage += line
		if (line.find('</page>')>-1):
			makeIDPair(currentPage)
			currentPage=''
	swf.close()



def makeAdjacency():
	swf = open(sys.argv[1],'r')
	swf.readline()
	currentPage = ''
	for line in swf:
		if (not (line.find('<page>')>-1 or line.find('</page>')>-1)):
			currentPage += line
		if (line.find('</page>')>-1):
			getLinks(currentPage)
			currentPage=''
	swf.close()
	'''
	for k,v in words.iteritems():
		freq = v[0]
		freq = math.log10(float(totalpages)/float(freq))
		words[k] = (freq, v[1])
	'''
	
			
def descendingCmp(a,b):
	return cmp(int(a),int(b))


def getLinks(page):
	terms = {}
	ID = idCheck.search(page).group(3)
	title = titleCheck.search(page).group(3)
	#titleFile.write(str((ID,title)) + '\n')
	text = ' ' + textCheck.search(page).group(3)
	text += " " + title;
	hits = linkCheck.findall(text)
	linkListsDictionary[ID] = ''
	for link in hits:
		if link[2] in docs:
			linkListsDictionary[ID] = linkListsDictionary[ID] + ' ' + str(docs[link[2]])
	


def makeStopWords():
	swf = open(sys.argv[1],'r')
	stopWords = swf.read()
	stopWords = stopWords.replace('\r','')
	stopWords = stopWords.split('\n')
	swf.close()
	return stopWords


def readFiles():
	swf = open(sys.argv[2],'r')
	swf.readline()
	currentPage = ''
	totalpages = 1
	for line in swf:
		if (not (line.find('<page>')>-1 or line.find('</page>')>-1)):
			currentPage += line
		if (line.find('</page>')>-1):
			parsePage(currentPage)
			totalpages=totalpages+1
			currentPage=''
	swf.close()
	
	for k,v in words.iteritems():
		freq = v[0]
		freq = math.log10(float(totalpages)/float(freq))
		words[k] = (freq, v[1])

def writeIndex(index):
	for k,v in index.iteritems():
		word = str(k)
		freq = v[0]
		indexFile.write(word + ' ' )
		indexFile.write(str(freq) + ' ' )
		docs = v[1]
		for x,y in docs.iteritems():
			indexFile.write(str(x) + ' ' + str(y) + ',')
		indexFile.write('\n')
	indexFile.write('; ')
	for i in range(len(doclengths)):
		length = doclengths[i]
		ID = docIDS[i]
		indexFile.write(str(ID) + ',' + str(length) + ' ')
		
		
start = time.time()
		
makeDocIDDictionary()
makeAdjacency() #python createIndex.py collection output
writefile = open(sys.argv[2],'w')
keys = linkListsDictionary.keys()
keys.sort(descendingCmp)
for k in keys:
	l = linkListsDictionary[k].strip().split(' ')
	l = list(set(l))
	l.sort(descendingCmp)
	writefile.write(str(k))
	for x in l:
		writefile.write(" " + str(x))
	writefile.write('\n')

end = time.time()
elapsed=end-start
print str(elapsed/60)
'''
start = time.time()

totalpages=0
stopWords = makeStopWords()
readFiles()
writeIndex(words)
	
end = time.time()

elapsed= end - start

min = elapsed/60
print('Time elapsed: ' + str(min)) #comment to not print runtime
'''