'''
Created on Feb 15, 2011

@author: Alex
'''

#input: stop words, pages, index to build, title index to build

#Line 1: Descriptors
#Line 2: # bits in line 3
#line 3: bits + padding zeros to equal byte
#line 4: #bits in line 5


#Decode:
#Decode function, takes in (Bytes bytes, int numBits)
#Getline function, gets the line of bytes corresponding to the input line number (int linenum)
#	line 1 = line 3
#	line bytes = line 1(descript) + line 2(bits in 3) + bytes in 3 + line 4(bits in 5) + bytes in 5...
#
#	readline
#	1: read(bytes in readline)
#	2: read(bytes in readline)
#	3: read(bytes in readline)
#etc...

import sys
import re
import time
import heapq
from BitVector import BitVector

#globals
frequencyHash = {}
frequencyList = []
testOutput = open('test.txt','wb')


def encode(f):
	file = open(f,'r')
	c = file.read(1)
	while len(c)>0:
		addToList(c)
		c = file.read(1)
	for k,v in frequencyHash.iteritems():
		frequencyList.append((v,k))
	freqTree = getTree(frequencyList)
	printTree(freqTree,testOutput)
	file.seek(0)
	#testOutput.write(
	#file.write('filename','wb')

def printTree(huffTree, file, prefix = ''):
	if len(huffTree) == 2:
		file.write('('+str(huffTree[1]) + "," + prefix+')')
	else:
		printTree(huffTree[1], file,prefix + '0')
		printTree(huffTree[2], file,prefix + '1')

def decode(b,numBits):
	print('decode file')

def getLine(lineNum):
	print ('getLine')
	
def getTree(freqlist):
	tree = list(freqlist)
	heapq.heapify(tree)
	while len(tree) > 1:
		left = heapq.heappop(tree)
		right = heapq.heappop(tree)
		next = (left[0]+right[0],left,right)
		heapq.heappush(tree,next)
	return tree[0]

def addToList(char):
	if char in frequencyHash:
            frequencyHash[char] = frequencyHash[char]+1
        else:
            frequencyHash[char] = 0

encode('small.dat.np')

'''
words = {}
p = PorterStemmer.PorterStemmer()

swf = open(sys.argv[1],'r')
stopWords = swf.read()
stopWords = stopWords.split('\n')
swf.close()
swf = open(sys.argv[2],'r')
collectionString = swf.read()
swf.close()

indexFile = open(sys.argv[3],'w')
titleFile = open(sys.argv[4],'w')

idCheck = re.compile('(.*?)(<id>)(.*?)(</id>)', re.DOTALL)
titleCheck = re.compile('(.*?)(<title>)(.*?)(</title>)', re.DOTALL)
textCheck = re.compile('(.*?)(<text>)(.*?)(</text>)', re.DOTALL)
pageSplit = re.compile('(</page>)(.*?)(<page>)', re.DOTALL)

stopWordString = ''
for i in range(0,len(stopWords)-1):
    stopWordString += r'\b' + stopWords[i] + r'\b' + '|'
stopWordString = stopWordString[:-1]

def parsePage(page):
    ID = idCheck.search(page).group(3)
    title = titleCheck.search(page).group(3)
    titleFile.write(str((ID,title)) + '\n')
    text = ' ' + textCheck.search(page).group(3)
    text += " " + title;
    text = text.lower()
    text = re.sub('(_|\n)',' ',text)
    text = re.sub(r'\W+',' ',text)
    text = re.sub(stopWordString,' ',text)
    text = re.sub('\s+',' ',text)
    text = text.split(' ')
    for i in range(1,len(text)):
        text[i] = p.stem(text[i], 0, len(text[i])-1)
        idpair = (ID,i)
        if text[i] in words:
            words[text[i]].append(idpair)
        else:
            words[text[i]] = [idpair]
def parseCollection(col,words):
    pages = re.split('</page>\s*?<page>', col)
    map(parsePage,pages)

start = time.time()

parseCollection(collectionString,stopWords)
for k,v in words.iteritems():
        indexFile.write(str(k) + ' ' + str(v) + '\n')
end = time.time()
 
elapsed= end - start
 
min = elapsed/60
#print(min) #comment to not print runtime
'''