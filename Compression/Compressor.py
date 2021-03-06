'''
Created on Feb 15, 2011

@author: Alex
'''
'''
#input: stop words, pages, index to build, title index to build

format of .p file:
text that is encoded: (substitute ' ' for _)
docid1_pos1_(pos2-pos1)_(pos3-pos2)_(docid2-docid1)_pos1_(pos2-pos1)__(docid3-docid2)_pos1__docid...
docid1_pos1__(docid2-docid1)_pos1__(docid3-docid2)_pos1_(pos2-pos1)_(pos3-pos2)__docid...
etc
What this means:
The orignal line 1:1,3,6 2:1 6:1,5,20 translates to:
1 1 2 3  1 1  4 1 4 15


Format of .np file



The lines are arranged, bit-wise, as follows:
newline
numbers... (if you start counting RIGHT HERE, it ends...)
newline
posting		(HERE). 
newline
newline
numbers...

#Line 1: Descriptors
#Everything else is encoded. Read encoded '\n', then get a bit-encoded int until next '\n' 
Then read that many bits (padded to make bytes, i.e.... 6 bits + 2 padding zeros for bytes, and decode
the bits. Shouldn't be hard, convert to string and strip the extra bits and then decode it
So:
Descriptors (including a newline, remember to account for that)
ALL DATA, encoded. Decode newlines and numbers of bits to get a pointer to the next newline
'''

import sys
import re
import time
import heapq
import StringIO
import os.path
import os
import string
import math

if len(sys.argv) < 3:
    print "format: "+sys.argv[0]+" uncompressedPostings compressedPostings"
    exit()

#globals
BREAK_NUM = 1000
frequencyHash = {}
frequencyList = []
huffHash = {}
tempEncodeName = 'tempencode.txt'
tempFile = open('temp.txt','wb')
tempEncode = open(tempEncodeName, 'wb')
testOutput = open(sys.argv[2],'wb')
tempDecode = open('decode.txt','wb')

def printbits(f):
	file = open(f,'r')
	bytes = (ord(b) for b in file.read())
	s=''
	for b in bytes:
		s+=bits(b)
	print(s)


def encode(f):
	file = open(f,'r')
	huffNums = '0123456789'
	for c in huffNums:
		addToList(c)
	c = file.read(1)
	while len(c)>0:
	#Get frequencies
		addToList(c)
		c = file.read(1)
	for k,v in frequencyHash.iteritems():
		frequencyList.append((v,k))
	
	#Make frequency tree
	freqTree = getTree(frequencyList)
	makeHuffHash(freqTree)
	
	#Write encodings to file
	for k,v in huffHash.iteritems():
		testOutput.write('('+k+','+v+')')
	
	#restart file
	file.seek(0)
	#print("Hash Done")
	c=0
	ss = ''
	line_num = 0
	bit_num = 0
	for line in file:
		s=''
		if line_num % BREAK_NUM == 0:
                    testOutput.write(str(bit_num)+'\n')
		for char in line:
			#get encoded char
			s += huffHash[char]
		length = ''
		
		for char in str(len(s)):
			#get length of encoded line in bits, encode that number
			length += huffHash[char]
			#and print that number, surrounded by encoded newlines
		
		s = huffHash['\n'] + length + huffHash['\n'] + s
		ss += s
		bit_num += len(s)
		if (len(ss)%8)==0:
			ss = [int(ss[x:x+8], 2) for x in range(0,len(ss),8)]
			ss = ''.join(chr(i) for i in ss)
			tempEncode.write(ss)
			ss=''
                line_num += 1
	ss = [int(ss[x:x+8], 2) for x in range(0,len(ss),8)]
	ss = ''.join(chr(i) for i in ss)
	tempEncode.write(ss)
	tempEncode.flush()
	tempEncode.close()
	testOutput.write('\n\n')
	tempEncodeRead = open(tempEncodeName, 'r')
	for line in tempEncodeRead:
            testOutput.write(line)
        tempEncodeRead.close()
        os.remove(tempEncodeName)
	testOutput.flush()
	testOutput.close()

def bits(f):
	x = ""
        for i in reversed(xrange(8)):
            x += str((f >> i) & 1)
	return x
	
	
def makeHuffHash(tree, bits = ''):
	if len(tree) == 2:
		huffHash[tree[1]] = bits
	else:
		makeHuffHash(tree[1], bits + '0')
		makeHuffHash(tree[2], bits + '1')
	
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
			
def convertFile(f):
	file = open(f,'r')
	#check if it's positional or not
	positional=0
	if (string.find(file.readline(),':')!=-1):
		positional=1
	file.seek(0)
	if positional:
		for line in file:
			#convert semis to commas for faster encoding. We dont need different ones,
			#the first term is always the docID, and the rest are positions
			line = string.replace(line,':',',')
			
			#split the line by whitespace
			docs = line.split()				
			#store docID
			docID = int(docs[0].split(',')[0])
			tempFile.write
			for doc in docs:
				tempDoc = doc.split(',')
			#Write difference in docID (if the past was doc 10 and this is doc 12, write 2)
				if int(tempDoc[0]) == docID:
					tempFile.write(str(docID))
				else:
					f = int(tempDoc[0]) - docID
					docID = int(tempDoc[0])
					tempFile.write(' ' + str(f))
			
			#write difference in positions
				count = int(tempDoc[1])
				tempFile.write(' ' + str(count))
				for num in tempDoc[2:len(doc)]:
					f = int(num) - count
					count = int(num)
					tempFile.write(' ' + str(f))
				tempFile.write(' ')
			tempFile.write('\n')
	else: 
		for line in file:
			#split whitespace in line...
			nums = line.split()
			i = int(nums[0])
			tempFile.write(str(i))

			#Write difference in docID (if the past was doc 10 and this is doc 12, write 2)
			for num in nums[1:len(nums)]:
				f = int(num) - i
				i = int(num)
				tempFile.write(" " + str(f))
			tempFile.write('\n')
	tempFile.flush()
	tempFile.close()
	
#Compress...
start = time.time()


'''TO RUN:

convertFile(filenamehere)
encode('temp.txt') <this filename is set in the top of the file
decode('test.txt') <this also is, but its just the result of encode. so whatever.
'''

convertFile(sys.argv[1])
#temporary file. We need to delete it
encode('temp.txt')
os.remove('temp.txt')
#decode('tests.np')
end = time.time()
 
elapsed= end - start
 
min = elapsed/60
#print(min)
