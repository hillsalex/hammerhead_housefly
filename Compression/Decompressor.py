import sys
import re
import time
import heapq
import StringIO
import os.path
import os
import math
import string

if len(sys.argv) < 2:
	print "format: "+sys.argv[0]+" compressedPostings"
	exit()

''' Mode constants '''
READING_INIT_NEWLINE = 0
READING_LINE_NUMBER = 1
READING_NEWLINE = 2
READING_DATA = 3

''' File types '''
NONPOSITIONAL_TYPE = 0
POSITIONAL_TYPE = 1

BREAK_NUM = 1000 # bit index jumps

to_decode = sys.argv[1]
dec_file = sys.argv[1].split('.')
exten = dec_file[len(dec_file)-1]
ctype = NONPOSITIONAL_TYPE # default
if exten == "np":
	ctype = NONPOSITIONAL_TYPE
elif exten == "p":
	ctype = POSITIONAL_TYPE
else:
	print "Unknown file type '."+exten+"': assuming nonpositional postings list."

def bits(f):
	x = ""
	for i in reversed(xrange(8)):
		x += str((f >> i) & 1)
	return x

def parseResult(expr):
	if ctype==POSITIONAL_TYPE:
		b = expr.split('  ')
		for i in range(len(b)):
			b[i] = b[i].split(' ')
		for i in range(len(b)):
			for j in range(len(b[i])):
				if b[i][j]!='':
					b[i][j] = int(b[i][j])
		for i in range(len(b)):
			b[i] = [x for x in b[i] if type(x).__name__=='int']
		for i in range(1,len(b)):
			b[i][0] = b[i][0] + b[i-1][0]
		for i in range(len(b)):
			for j in range(2,len(b[i])):
				b[i][j] = b[i][j] + b[i][j-1]
		results_list = ['' for i in b]
		for i in range(len(b)):
			results_list[i] = str(b[i][0]) + ":" + ','.join([str(b[i][j]) for j in range(1, len(b[i]))])
		return ' '.join(results_list)
	elif ctype==NONPOSITIONAL_TYPE:
		b = expr.split(' ')
		for i in range(len(b)):
			if b[i]!='':
				b[i] = int(b[i])
		b = [x for x in b if type(x).__name__=='int']
		for i in range(1,len(b)):
			b[i] = b[i] + b[i-1]
		return ' '.join([str(x) for x in b])


def queryP(num):
	f = to_decode
	file = open(f,'rb')
	last = file.read(1)
	complete=0
	huffstring = ''
	bytesread=1
	while not(complete):
		huffstring+=last
		temp = last
		last = file.read(1)
		if (temp==')' and last!='('):
			file.seek(bytesread)
			complete=1
		else:
			bytesread=bytesread+1
	huffstring = string.replace(huffstring,')(','|')
	huffstring = string.replace(huffstring,')','')
	huffstring = string.replace(huffstring,'(','')
	huffstring = huffstring.split('|')
	huff = {}
	for s in huffstring:
                toAdd = s.split(',')
                huff[toAdd[1]] = toAdd[0]

        bitStart = 0 # The bit to jump to
        bitLineToFind = math.floor(num/BREAK_NUM)
        currBitLine = 0
	while 1:
                lin = file.readline()
                if lin=='\n':
                        if file.readline()=='\n': # got two newlines in a row
                                break
                else:
                        if currBitLine == bitLineToFind:
                                bitStart = int(lin.rstrip('\n'))
                        currBitLine += 1
        file.seek(int(math.floor(bitStart/8.0)), os.SEEK_CUR)
        

	'''HERE IS WHERE WE BEGIN READING'''
	currentLine = ''
	complete = 0
	mode = READING_INIT_NEWLINE
	just_jumped_num = 0
	bitsleft=0
	bitRoll = (bitStart % 8)
	jump = 0
																	
	currentbits = bits(ord(file.read(1))) 				#bit buffer
	currentbits = currentbits[bitRoll:]

	line_num = int(math.floor(num/BREAK_NUM))*BREAK_NUM
	totalbits=8
	while not(complete):								#while the file isn't parsed...
		currentCharBits = ''
		jump = 0
		bitRoll = 0
		gotChar = 0
		while not gotChar:					#while we haven't decompressed an entire character...
			if (len(currentbits)==0):			#if our bit buffer is empty
				ch = file.read(1)					#get some more
				totalbits+=8
				if len(ch)!=0: 					#if it's not the end of the file
					currentbits = bits(ord(ch))			#store those bits
				else: 					#if it is the end of the file, set our buffer to zero
					currentbits = []
			if len(currentbits)==0: 					#if our buffer is zero
				gotChar = 1								
				complete = 1 							#done everything
				print ""
			if bitsleft > 0 and not complete:
				currentbits = currentbits[bitsleft:]
				bitsleft = 0
				continue
			if not complete:
				#print('buffer ' + currentbits)
				currentCharBits += currentbits[0]		#grab the first bit in the buffer
				currentbits = currentbits[1::]			#reduce our buffer size
				#print('current char' + currentCharBits)				
				if (currentCharBits in huff):			#if the bits we're currently storing match a huffman encoding
					gotChar = 1 						#we have a char
					#print(huff[currentCharBits])

					if mode==READING_INIT_NEWLINE:
						#print('ReadingInitNewline: ' + huff[currentCharBits])
						if huff[currentCharBits]=='\n':
							mode = READING_LINE_NUMBER
							continue
						else:
							print "Error: expected newline (got "+huff[currentCharBits]+")"
							exit()
					if mode==READING_LINE_NUMBER:
						#print('ReadingLineNumber: ' + huff[currentCharBits])
						if huff[currentCharBits]=='\n':
							#print('should jump')
							if line_num == num:		 # If this is the line matching the query
								mode = READING_DATA	 # Set mode to reading data
								currentLine=''		  # line length doesn't matter
								continue
							else:					   # Otherwise, jump forward to next line
								#print('bits ' + currentLine + ' bits ' + currentbits)
								bitsToJump = int(currentLine) - int(len(currentbits))
								if (bitsToJump < 0):
									bitsToJump = int(currentLine)
								if (int(len(currentbits)) - int(currentLine)) < 0:
									currentbits = ''
								#print(totalbits)
								#print("Jump bits: " + str(bitsToJump))
								jump = int(math.floor(int(bitsToJump)/8.0))
								#print(str(int(bitsToJump)) + " " + str(int(bitsToJump)/8.0))
								if (jump!=0):
									
									bitsleft = (int(bitsToJump))%(jump*8)
								else:
									bitsleft = int(bitsToJump)
								#print("Jump bytes: " + str(jump))
								#print("Jump bits: " + str(bitsleft))
								file.seek(jump, os.SEEK_CUR)
								mode = READING_INIT_NEWLINE
								currentLine=''
								currentCharBits = ''
								line_num += 1
								continue
						else:   # found a number char
							currentLine+=huff[currentCharBits]	#add that char
							continue
					if mode==READING_DATA:
						#print('ReadingData: ' + huff[currentCharBits])
						if huff[currentCharBits]=='\n':
							print parseResult(currentLine) # End of reading data - dump and exit function
							return
						else: 
							currentLine+=huff[currentCharBits]	#add that char
							continue

def queryNP(num):
	f = to_decode
	file = open(f,'r')
	last = file.read(1)
	complete=0
	huffstring = ''
	bytesread=1
	while not(complete):
		huffstring+=last
		temp = last
		last = file.read(1)
		if (temp==')' and last!='('):
			file.seek(bytesread)
			complete=1
		else:
			bytesread=bytesread+1
	huffstring = string.replace(huffstring,')(','|')
	huffstring = string.replace(huffstring,')','')
	huffstring = string.replace(huffstring,'(','')
	huffstring = huffstring.split('|')
	huff = {}
	for s in huffstring:
		toAdd = s.split(',')
		huff[toAdd[1]] = toAdd[0]

	bitStart = 0 # The bit to jump to
        bitLineToFind = math.floor(num/BREAK_NUM)
        currBitLine = 0
	while 1:
                lin = file.readline()
                if lin=='\n':
                        if file.readline()=='\n': # got two newlines in a row
                                break
                else:
                        if currBitLine == bitLineToFind:
                                bitStart = int(lin.rstrip('\n'))
                        currBitLine += 1
        
        file.seek(int(math.floor(bitStart/8.0)), os.SEEK_CUR)
	
	'''HERE IS WHERE WE BEGIN READING'''
	currentLine = ''
	complete = 0
	line_num = int(math.floor(num/BREAK_NUM))*BREAK_NUM
	mode = READING_INIT_NEWLINE
																	
	currentbits = bits(ord(file.read(1))) 				#bit buffer
	

	while not(complete):								
		currentCharBits = ''
		gotChar = 0
		while not gotChar:						#while we haven't decompressed an entire character...
			if (len(currentbits)==0):					#if our bit buffer is empty
				ch = file.read(1)				#get some more
				if len(ch)!=0: 				#if it's not the end of the file
					currentbits = bits(ord(ch))			#store those bits

				else: 					#if it is the end of the file, set our buffer to zero
					currentbits = []
			if len(currentbits)==0: 					#if our buffer is zero
				gotChar = 1				#we're done
				complete = 1 				#done everything
				print parseResult(currentLine)
			else:
				currentCharBits += currentbits[0]		#grab the first bit in the buffer
				currentbits = currentbits[1::]			#reduce our buffer size
				
				if (currentCharBits in huff):			#if the bits we're currently storing match a huffman encoding
					gotChar = 1 						#we have a char
					if huff[currentCharBits]=='\n':
						if mode==READING_INIT_NEWLINE: 
							if line_num==num:
								mode = READING_DATA
								continue
							else:
								line_num+=1
						elif mode==READING_DATA:
							print parseResult(currentLine)
							return
					else:
						if mode==READING_DATA:
							currentLine+=huff[currentCharBits]	#add that char
					currentCharBits = ''				#restart 
while 1:
	next = sys.stdin.readline()
	start = time.time()
	if not next:
		break
	if ctype == POSITIONAL_TYPE:
		queryP(int(next))
	elif ctype == NONPOSITIONAL_TYPE:
		queryP(int(next))
	end = time.time()
	#print (end - start)
