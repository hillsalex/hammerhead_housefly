import random
import os
import math
import shutil


########INSTRUCTIONS##########
##Put whatever version of svm in a folder final/svm. 
##i.e. linux version goes in final/svm/svm_learn etc...

def vecToDic(V):
	docDic = {}
	lineNum = 0	
	Vfile = open(V, 'r')
	for line in Vfile:
		words = line.rstrip('\n').split(' ')
		magnitude = math.sqrt(float(words[1]))
		lineDic = dict([(int(words[i].split(':')[0]), int(words[i].split(':')[1])/magnitude) for i in range(2,len(words))])
		docDic[lineNum] = lineDic
		lineNum += 1
	return docDic

v = vecToDic('vecrep.dat')


print "Done making vec dictionary."

# Classes

trainDocs = {}
trainingPairs = {}

def getDocs():
	f = open('training.dat','r')
	for line in f:
		docID, classID = line.rstrip('\n').split(' ')
		trainingPairs[docID]=classID
		
def makeClassSVM(classID):
	shutil.copyfile('svmtraining' + str(classID)+'.dat','svmtraining'+str(classID)+'temp.dat')
	training = open('svmtraining'+str(classID)+'.dat','r')
	tempTraining = open('svmtraining'+str(c)+'temp.dat', 'a')
	training.seek(0)
	count = 0
	addedDocs = []

	for docID, classx in trainingPairs.iteritems():
		docID = int(docID)
		if not (docID in trainDocs[classID]):
			trainDocs[classID][docID]=1
			count += 1
			tempTraining.write("-1 ")
			for term in sorted(v[int(docID)].keys()):
				tempTraining.write(str(term)+":"+str(v[int(docID)][term])+" ")
			tempTraining.write("\n")
			if count == 100:
				break
	training.close()
	tempTraining.close()
	os.system('./svm/svm_learn -v 0 svmtraining'+str(c)+'temp.dat svmmodel'+str(c)+'temp.dat')
	
	for i in range(20):
		count = 0
		print 'iteration ' + str(i)
		tester = open('svmtest'+str(c)+'temp.dat','w')
		for docID, classx in trainingPairs.iteritems():
			docID = int(docID)
			if not (docID in trainDocs[classID]):
				count += 1
				tester.write("0 ")
				for term in sorted(v[int(docID)].keys()):
					tester.write(str(term)+":"+str(v[int(docID)][term])+" ")
				tester.write("\n")
				addedDocs.append(int(docID))
				if count == 500:
					break
		tester.close()
		os.system('./svm/svm_classify -v 0 svmtest'+str(c)+'temp.dat svmmodel'+str(c)+'temp.dat svmpredict'+str(c)+'temp.dat')
		
		tempTraining = open('svmtraining'+str(c)+'temp.dat', 'a')
		results = open('svmpredict'+str(c)+'temp.dat')
		reslist = []
		for line in results:
			if float(line) > 0:
				reslist.append(1)
			else:
				reslist.append(math.fabs(float(line)))
		for i in range(20):
			index = reslist.index(min(reslist))
			docID = int(reslist[index])
			tempTraining.write("-1 ")
			for term in sorted(v[int(docID)].keys()):
				tempTraining.write(str(term)+":"+str(v[int(docID)][term])+" ")
			tempTraining.write("\n")
			trainDocs[classID][docID] = 1
		results.close()
		tempTraining.close()
		os.system('./svm/svm_learn svmtraining'+str(c)+'temp.dat svmmodel'+str(c)+'temp.dat')
	os.remove('svmtraining' + str(classID)+'.dat')
	os.remove('svmpredict'+str(c)+'temp.dat')
	os.remove('svmtest'+str(c)+'temp.dat')
	shutil.copyfile('svmtraining' + str(classID)+'temp.dat','svmtraining'+str(classID)+'.dat')
	os.system('./svm/svm_learn svmtraining'+str(c)+'temp.dat svmmodel'+str(c)+'temp.dat')

getDocs()
C = range(11)

for c in C:
	trainDocs[c]={}
	newFile = open('svmtraining'+str(c)+'.dat', 'w')
	f = open('training.dat','r')
	count = 0
	nonClass = 0
	for line in f:
		docID, classID = line.rstrip('\n').split(' ')
		doc = int(docID)
		if int(classID)==c:
			newFile.write("1 ")
			trainDocs[c][docID] = 1
			for term in sorted(v[doc].keys()):
				newFile.write(str(term)+":"+str(v[doc][term])+" ")
			newFile.write("\n")
		'''
		else:
			nonClass += 1
			if (nonClass==99):
				newFile.write("-1 ")
				trainDocs[c][doc]=1
				for term in sorted(v[doc].keys()):
					newFile.write(str(term)+":"+str(v[doc][term])+" ")
				newFile.write("\n")
				nonClass = 0
		'''
		count += 1
	print "done class " + str(c)
	f.close()
	newFile.close()
	makeClassSVM(c)
	print "really done class " + str(c)
	# @ repeat N times...
	'''f = open('training.dat','r')
	for line in f:
		docID, classID = line.rstrip('\n').split(' ')
		doc = int(docID)
		if not int(classID)==c:
			if int(random()*10)==0: # 1/10th of negative examples
				# write to some temp file
				# run svm_learn on that temp file
				# run svm_classify on the resulting model
				# iterate through prediction to find lowest score
				# write that doc and its features to svmtrainingX with -1'''
				

