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

C = range(1)

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
			for term in v[doc].keys():
				newFile.write(str(term)+":"+str(v[doc][term])+" ")
		else:
			newFile.write("-1 ")
			for term in v[doc].keys():
				newFile.write(str(term)+":"+str(v[doc][term])+" ")
		count += 1
