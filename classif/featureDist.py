""" Returns a dictionary representation of the document-term occurrence vectors listed in file V.
E.g. {d0:{t1:p1, t2:p2}} gives the positions for terms t1 and t2 in document d0."""
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

vecs1 = vecToDic('vecrep1.dat')

"""numDocs = 0
numTerms = 0
for doc in vecs1.keys():
	for termFreq in vecs1[doc].values():
		numTerms += termFreq
	numDocs += 1

print "Vecrep with features1: "+str((numTerms+0.0)/numDocs)+" terms per document."
"""

#Get number of features
numFeatures = 0
features = open('features1.dat', 'r')
for line in features:
	numFeatures += 1

featureTotals = dict([(i,0) for i in range(numFeatures)])

f = open('featuresDist1.dat', 'w')

for doc in vecs1.keys():
	for term in vecs1[doc].keys():
		featureTotals[term] += 1

features = open('features1.dat', 'r')
termNum = 0
for line in features:
	f.write(line.rstrip('\n').split(' ',1)[0]+": "+str(featureTotals[termNum])+"\n");
	termNum += 1



"""vecs2 = vecToDic('vecrep2.dat')
numDocs = 0
numTerms = 0
for doc in vecs2.keys():
	for termFreq in vecs2[doc].values():
		numTerms += termFreq
	numDocs += 1

print "Vecrep with features2: "+str((numTerms+0.0)/numDocs)+" terms per document."
"""

