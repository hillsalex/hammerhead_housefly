import PorterStemmer
import sys
from math import log, sqrt

# Check for valid arguments
if len(sys.argv) < 7:
	print "format: "+sys.argv[0]+" -mnb/-r features vectorRep trainingSet docs results"
	exit()
elif not (sys.argv[1]=="-mnb" or sys.argv[1]=="-r"):
	print "First argument is invalid; valid method types are '-mnb' and '-r'."
	exit()

# Read arguments
featuresArg = sys.argv[2]
vecrepArg = sys.argv[3]
trainingArg = sys.argv[4]
docsArg = sys.argv[5]
resultsArg = sys.argv[6]

""" Returns the list of classes from the training data """
def getClasses(T):
	classes = set()
	trainingFile = open(T, 'r')
	for line in trainingFile:
		words = line.rstrip('\n').split(' ')
		classes = classes.union([int(words[1])])
	return list(classes)

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

""" Returns a normalized dictionary representation of the document-term occurrence vectors listed in file V.
E.g. {d0:{t1:p1, t2:p2}} gives the positions for terms t1 and t2 in document d0."""
def vecToDicNormalized(V):
	docDic = {}
	lineNum = 0	
	Vfile = open(V, 'r')
	for line in Vfile:
		words = line.rstrip('\n').split(' ')
		lineDic = dict([(int(words[i].split(':')[0]), (int(words[i].split(':')[1])+0.0)/int(words[1])) for i in range(2,len(words))])
		docDic[lineNum] = lineDic
		lineNum += 1
	return docDic

""" Returns a dictionary mapping docID to its length using the vector representation file. """
def vecLens(V):
	docDic = {}
	lineNum = 0	
	Vfile = open(V, 'r')
	for line in Vfile:
		words = line.rstrip('\n').split(' ',2)
		docDic[lineNum] = sqrt(int(words[1]))
		lineNum += 1
	return docDic

""" Returns a list of vocabulary words from features file F. """
def extractVocabulary(F):
	Ffile = open(F, 'r')
	return [x.rstrip('\n') for x in Ffile]

""" Returns the number of documents using the vector representation file. """
def countDocs(V):
	lineNum= 0
	for line in V:
		lineNum += 1
	return lineNum

""" Returns the number of docs in class c using training data file T. """
def countDocsInClass(T, c):
	Tfile = open(T, 'r')
	count = 0	
	for line in Tfile:
		if int(line.split(' ')[1]) == c:
			count += 1
	return count

""" Returns a list of docs in class c using training data file T. """
def getDocsInClass(T, c):
	Tfile = open(T, 'r')
	clist = []
	for line in Tfile:
		docID, classID = [int(x) for x in line.split(' ')]
		if classID == c:
			clist.append(docID)
	return clist

""" Returns the number of occurrences of t in training file T from class c. 
v is the vector representation, d is the list of docs. """
def countTokensOfTerm(T,t,c,v,d):
	count = 0	
	for doc in d:
		try:
			count += v[doc][t]
		except KeyError:
			continue
	return count

""" Returns a list of terms in a doc d from the vector representation """
def extractTokensFromDoc(v,d):
	return v[d].keys()

""" Returns the magnitude of a dict representation of a vector """
def magVec(vec):
	return sqrt(sum([val**2 for val in vec.values()]))

""" Returns the item in elements which is a key for the greatest value in dic """
def argmax(elements, dic):
	score = dic[elements[0]]
	top = elements[0]
	for element in elements:
		if dic[element] > score:
			top = element
			score = dic[element]
	return top

""" Returns the item in elements which is a key for the lowest value in dic """
def argmin(elements, dic):
	score = dic[elements[0]]
	bottom = elements[0]
	for element in elements:
		if dic[element] < score:
			bottom = element
			score = dic[element]
	return bottom

""" T is the training data file, V is the vector representation file, v is the vector representation, F is the features file """
def TrainMultinomialNB(T,V,v,F,C):
	Vfile = open(V, 'r')
	Vlist = extractVocabulary(F)
	N = countDocs(Vfile)
	prior = {}
	Tct = dict((i,{}) for i in C)
	condprob = dict((i,{}) for i in C)
	for c in C:
		print "On class "+str(c)
		Nc = countDocsInClass(T,c)
		docList = getDocsInClass(T,c)
		prior[c] = (0.0 + Nc)/N
		for t in range(len(Vlist)):
			Tct[c][t] = countTokensOfTerm(T,t,c,v,docList)
		numTermsInClass = sum(Tct[c].itervalues())
		for t in range(len(Vlist)):
			condprob[c][t] = (Tct[c][t] + 1.0)/(numTermsInClass + len(Vlist))
	return (Vlist, prior, condprob)

def ApplyMultinomialNB(T,v,prior,condprob,d,C):
	W = extractTokensFromDoc(v,d)
	#print "W: "+str(W)
	score = {}	
	for c in C:
		score[c] = log(prior[c])
		for t in W:
			score[c] += log(condprob[c][t])
	#print "Scores for doc "+str(d)+": "+str(score)
	return argmax(C,score) 

def trainRocchio(T,V,v,C):
	D = [[] for x in C]
	u = [{} for x in C]
	for j in C:
		D[j] = getDocsInClass(T,j)
		classvec = {}
		for doc in D[j]:
			terms = extractTokensFromDoc(v,doc)
			for term in terms:
				classvec[term] = classvec.get(term,0) + v[doc][term]
				#classvec[term] = classvec.get(term,0) + (v[doc][term] + 0.0)
		Nc = countDocsInClass(T,j)
		u[j] = dict((key,((val+0.0)/Nc)) for key,val in classvec.iteritems())
	return u

def applyRocchio(T,v,u,doc,C):
	termsInDoc = v[doc].keys()
	u2 = [{} for x in C]
	for j in C:
		termsInCentroid = u[j].keys()
		allTerms = set(termsInDoc + termsInCentroid)
		diffvec = {}
		for term in allTerms:
			try: classFreq = u[j][term]
			except: classFreq = 0
			try: docFreq = v[doc][term]
			except: docFreq = 0
			diffvec[term] = classFreq - docFreq
		u2[j] = magVec(diffvec)
	return argmin(C, u2)
		

def runMNB():
	vecrep = vecToDic(vecrepArg)
	classes = getClasses(trainingArg)
	Vlist, prior, condprob = TrainMultinomialNB(trainingArg, vecrepArg, vecrep, featuresArg, classes)
	"""f = open('vecrep', 'w')
	f.write(str(vecrep))
	f = open('Vlist', 'w')
	f.write(str(Vlist))
	f = open('prior', 'w')
	f.write(str(prior))
	f = open('condprob', 'w')
	f.write(str(condprob))
	prior = eval(open('prior', 'r').read())
	condprob = eval(open('condprob', 'r').read())"""

	docs = open(docsArg, 'r')
	total = 0
	resultsFile = open(resultsArg, 'w')
	for line in docs:
		docID = int(line.split(' ')[0])
		resultsFile.write(str(docID)+" "+str(ApplyMultinomialNB(trainingArg, vecrep, prior, condprob, docID, classes))+"\n")
		total += 1
		if total%100==0:
			print "On "+str(total)
	return

def runRocchio():
	vecrep = vecToDicNormalized(vecrepArg)
	print "Done creating vector representation."
	classes = getClasses(trainingArg)
	u = trainRocchio(trainingArg, vecrepArg, vecrep, classes)
	print "Done training."
	docs = open(docsArg, 'r')
	total = 0
	resultsFile = open(resultsArg, 'w')
	for line in docs:
		docID = int(line.split(' ')[0])
		resultsFile.write(str(docID)+" "+str(applyRocchio(trainingArg, vecrep,u,docID,classes))+"\n")
		total += 1
		if total%100==0:
			print "On "+str(total)
	return

if sys.argv[1]=="-mnb":
	runMNB()
elif sys.argv[1]=="-r":
	runRocchio()
