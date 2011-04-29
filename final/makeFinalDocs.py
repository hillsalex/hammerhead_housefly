import random
import os
import math
import shutil


########INSTRUCTIONS##########
##Put whatever version of svm in a folder final/svm. 
##i.e. linux version goes in final/svm/svm_learn etc...


def vecToDic(V):
	docDic = {}
	Vfile = open(V, 'r')
	global lineNum
	for line in Vfile:
		words = line.rstrip('\n').split(' ')
		magnitude = math.sqrt(float(words[1]))
		lineDic = dict([(int(words[i].split(':')[0]), int(words[i].split(':')[1])/magnitude) for i in range(2,len(words))])
		docDic[lineNum] = lineDic
		lineNum += 1
	return docDic

lineNum=0
v = vecToDic('vecrep.dat')
finalDocs = open('finalDocs.dat','w')

for docID in range(lineNum):
	finalDocs.write("0 ")
	for term in sorted(v[int(docID)].keys()):
		finalDocs.write(str(term)+":"+str(v[int(docID)][term])+" ")
	finalDocs.write('\n')