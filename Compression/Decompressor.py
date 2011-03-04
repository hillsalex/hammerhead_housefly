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

queries = sys.stdin.readlines()
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


    '''HERE IS WHERE WE BEGIN READING'''
    currentLine = ''
    complete = 0
    mode = READING_INIT_NEWLINE
    just_jumped_num = 0
    roll = 0
    jump = 0
                                                                    
    currentbits = bits(ord(file.read(1))) 				#bit buffer

    line_num = 0
    while not(complete):								#while the file isn't parsed...
        currentCharBits = ''
        jump = 0
        roll = 0
        gotChar = 0
        while not gotChar:					#while we haven't decompressed an entire character...
            if (len(currentbits)==0):			#if our bit buffer is empty
                ch = file.read(1)					#get some more
                if len(ch)!=0: 					#if it's not the end of the file
                    currentbits = bits(ord(ch))			#store those bits
                    if just_jumped_num > 0:
                        currentbits = currentbits[just_jumped_num:]
                        just_jumped_num = 0
                else: 					#if it is the end of the file, set our buffer to zero
                    currentbits = []
            if len(currentbits)==0: 					#if our buffer is zero
                gotChar = 1							    
                complete = 1 							#done everything
                print ""
            else:
                currentCharBits += currentbits[0]		#grab the first bit in the buffer
                currentbits = currentbits[1::]			#reduce our buffer size                
                if (currentCharBits in huff):			#if the bits we're currently storing match a huffman encoding
                    gotChar = 1 						#we have a char

                    if mode==READING_INIT_NEWLINE:
                        if huff[currentCharBits]=='\n':
                            mode = READING_LINE_NUMBER
                            continue
                        else:
                            print "Error: expected newline."
                            break
                    if mode==READING_LINE_NUMBER:
                        if huff[currentCharBits]=='\n':

                            if line_num == num:         # If this is the line matching the query
                                mode = READING_DATA     # Set mode to reading data
                                currentLine=''          # line length doesn't matter
                                continue
                            else:                       # Otherwise, jump forward to next line
                                bitsToJump = int(currentLine)
                                jump = int(math.ceil(int(bitsToJump)/8.0))-1;
                                file.seek(jump, os.SEEK_CUR)
                                just_jumped_num = 8-len(currentbits)
                                rem1 = int(math.ceil(bitsToJump/8.0)*8-bitsToJump)
                                rem2 = int(math.floor(bitsToJump/8.0)*8-bitsToJump)
                                if just_jumped_num > rem1:
                                    just_jumped_num -= rem1;
                                else:
                                    just_jumped_num += rem2
                                mode = READING_INIT_NEWLINE
                                currentLine=''
                                currentbits = ''
                                currentCharBits = ''
                                line_num += 1
                                continue
                        else:   # found a number char
                            currentLine+=huff[currentCharBits]	#add that char
                            continue
                    if mode==READING_DATA:
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
    
    
    '''HERE IS WHERE WE BEGIN READING'''
    currentLine = ''
    complete = 0
    line_num = 0
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

for q in queries:
    if ctype == POSITIONAL_TYPE:
        queryP(int(q))
    elif ctype == NONPOSITIONAL_TYPE:
        queryNP(int(q))
