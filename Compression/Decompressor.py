import sys
import re
import time
import heapq
import StringIO
import os.path
import os
import math
import string

''' Mode constants '''
READING_INIT_NEWLINE = 0
READING_LINE_NUMBER = 1
READING_NEWLINE = 2
READING_DATA = 3

queries = sys.stdin.readlines()
to_decode = 'test.txt'

def bits(f):
    x = ""
    for i in reversed(xrange(8)):
        x += str((f >> i) & 1)
    return x

def parseResult(expr):
    b = expr.split('  ')
    for i in range(len(b)):
        b[i] = b[i].split(' ')
    for i in range(len(b)):
        for j in range(len(b[i])):
            b[i][j] = int(b[i][j])
    for i in range(1,len(b)):
        b[i][0] = b[i][0] + b[i-1][0]
    for i in range(len(b)):
        for j in range(2,len(b[i])):
            b[i][j] = b[i][j] + b[i][j-1]
    results_list = ['' for i in b]
    for i in range(len(b)):
        results_list[i] = str(b[i][0]) + ":" + ','.join([str(b[i][j]) for j in range(1, len(b[i]))])
    return ' '.join(results_list)
        

def query(num):
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
                                                                    #reads first 8 bits. we can't read in a different amount than 8...
    currentbits = bits(ord(file.read(1))) 				#bit buffer

    line_num = 0
    while not(complete):								#while the file isn't parsed...
        #print "-----------"
        #print "mode: "+str(mode)
        #print "@position: "+str(file.tell())
        currentCharBits = ''
        jump = 0
        roll = 0
        gotChar = 0
        #print "CurrentCharBits: "+str(currentCharBits)+" and currentbits: "+str(currentbits)
        while not gotChar:								#while we haven't decompressed an entire character...
            if (len(currentbits)==0):					#if our bit buffer is empty
                ch = file.read(1)						#get some more
                if len(ch)!=0: 							#if it's not the end of the file
                    currentbits = bits(ord(ch))			#store those bits
                    if just_jumped_num > 0:
                        currentbits = currentbits[just_jumped_num:]
                        just_jumped_num = 0
                    #print "Just read "+currentbits
                else: 					#if it is the end of the file, set our buffer to zero
                    currentbits = []
            if len(currentbits)==0: 					#if our buffer is zero
                gotChar = 1								#we're done
                complete = 1 							#done everything
                print ""
            else:
                currentCharBits += currentbits[0]		#grab the first bit in the buffer
                currentbits = currentbits[1::]			#reduce our buffer size                
                if (currentCharBits in huff):			#if the bits we're currently storing match a huffman encoding
                    gotChar = 1 						#we have a char
                    #print "FOUND CHARACTER: '"+ huff[currentCharBits]+"' i.e. "+currentCharBits
                    if mode==READING_INIT_NEWLINE:
                        if huff[currentCharBits]=='\n':
                            mode = READING_LINE_NUMBER
                            continue
                        else:
                            #print "Expected newline."
                            exit()
                    if mode==READING_LINE_NUMBER:
                        if huff[currentCharBits]=='\n':
                            #print "Line num is "+str(line_num)+" and num is "+str(num)
                            if line_num == num: # If this is the line matching the query
                                mode = READING_DATA # Set mode to reading data
                                currentLine='' # line length doesn't matter
                                continue
                            else:   # Otherwise, jump forward to next line
                                bitsToJump = int(currentLine)
                                jump = int(math.ceil(int(bitsToJump)/8.0))-1;
                                file.seek(jump, os.SEEK_CUR)
                                #print "Jumped "+str(jump)+" to "+str(file.tell())
                                just_jumped_num = 8-len(currentbits)
                                rem1 = int(math.ceil(bitsToJump/8.0)*8-bitsToJump)
                                rem2 = int(math.floor(bitsToJump/8.0)*8-bitsToJump)
                                if just_jumped_num > rem1:
                                    just_jumped_num -= rem1;
                                else:
                                    just_jumped_num += rem2
                                #print "Just jumped number: "+str(just_jumped_num)
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

for q in queries:
    query(int(q))
