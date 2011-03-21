'''
Created on Feb 15, 2011

@author: Alex
'''

#input: stop words, pages, index to build, title index to build

#get pageID, title, text by parsing page
#store pageID and title in title doc..
#for title and text: concat total, with a newline. get stream of words.
#lower case it all
#get all the tokens
#filter out tokens matching stop words
#stem tokens with porter stemmer

import sys
import re
import PorterStemmer
import time

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