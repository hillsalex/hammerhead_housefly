import sys
import re
import PorterStemmer
import math
import time

features = {}
docs = {}
p = PorterStemmer.PorterStemmer()


idCheck = re.compile('(.*?)(<id>)(.*?)(</id>)', re.DOTALL)
titleCheck = re.compile('(.*?)(<title>)(.*?)(</title>)', re.DOTALL)
textCheck = re.compile('(.*?)(<text>)(.*?)(</text>)', re.DOTALL)

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
	for i in range(0,len(text)):
		#doclengths[len(doclengths)-1]+=1
		text[i] = p.stem(text[i], 0, len(text[i])-1)
	text = [t for t in text if t not in stopWords]
	for i in range(0,len(text)):
		if text[i] in features:
			if text[i] in terms:
				terms[text[i]] = terms[text[i]]+1
			else:
				terms[text[i]] = 1
	docs[ID] = terms
				
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

def makeFeatures():
	swf = open(sys.argv[3],'r')
	index = 0
	for line in swf:
		text = line.strip()
		features[text]=index
		index = index + 1

def descendingCmp(a,b):
	return cmp(int(a),int(b))
		
def writeIndex():
	swf = open(sys.argv[4],'w')
	keys = docs.keys()
	keys.sort(descendingCmp)
	for k in keys:
		newfeatures = {}
		featureset = docs[k]
		sum = 0
		toPrint = ""
		for feature,number in featureset.iteritems():
			newfeatures[int(features[feature])] = number
			sum = sum + number*number
		fsorted = newfeatures.keys()
		fsorted.sort(descendingCmp) #sorted(newfeatures.keys())
		for feature in fsorted:
			toPrint = toPrint + " " + str(feature) + ":" + str(newfeatures[feature])
		docs[k] = str(sum) + str(toPrint)
		swf.write(str(k) + " " + str(docs[k]) + '\n')
	swf.flush()
	swf.close()
	

	
start = time.time()

stopWords = makeStopWords()
makeFeatures()
readFiles()
writeIndex()
	
end = time.time()

elapsed= end - start

min = elapsed/60
print('Time elapsed: ' + str(min)) #comment to not print runtime