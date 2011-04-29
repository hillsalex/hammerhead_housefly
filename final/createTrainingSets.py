from random import random

def vecToDic(V):
	docDic = {}
	lineNum = 0	
	Vfile = open(V, 'r')
	for line in Vfile:
		words = line.rstrip('\n').split(' ')
		lineDic = dict([(int(words[i].split(':')[0]), int(words[i].split(':')[1])) for i in range(2,len(words))])
		docDic[lineNum] = lineDic
		lineNum += 1
	return docDic

v = vecToDic('vecrep.dat')

print "Done making vec dictionary."

# Classes
C = range(11)

for c in C:
	newFile = open('svmtraining'+str(c)+'.dat', 'w')
	f = open('training.dat','r')
	count = 0
	for line in f:
		if count%1000==0: print "Count = "+str(count)
		docID, classID = line.rstrip('\n').split(' ')
		doc = int(docID)
		if int(classID)==c:
			newFile.write("+1 ")
			for term in sorted(v[doc].keys()):
				newFile.write(str(term)+":"+str(v[doc][term])+" ")
			newFile.write("\n")
		else:
			if int(random()*100)==0: # Write 1/100 of the 10000 negative examples
				newFile.write("-1 ")
				for term in sorted(v[doc].keys()):
					newFile.write(str(term)+":"+str(v[doc][term])+" ")
				newFile.write("\n")
		count += 1
	# @ repeat N times...
	"""f = open('training.dat','r')
	for line in f:
		docID, classID = line.rstrip('\n').split(' ')
		doc = int(docID)
		if not int(classID)==c:
			if int(random()*10)==0: # 1/10th of negative examples
				# write to some temp file
				# run svm_learn on that temp file
				# run svm_classify on the resulting model
				# iterate through prediction to find lowest score
				# write that doc and its features to svmtrainingX with -1"""
				

