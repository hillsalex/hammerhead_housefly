import PorterStemmer
import sys
from math import log

""" Returns true if a character is [a-z0-9] """
def isAlphaNumeric(char):
	if (ord(char) > 96 and ord(char) < 123) or (ord(char) > 47 and ord(char) < 58):
		return True
	else:
		return False

""" Returns a stream of characters into a stream of tokens """
def tokenize(query):
	query = query + " "
	tokens = []
	word = []
	for char in query:
		if isAlphaNumeric(char):
			word.append(char)
		else:
			word = "".join(char)
			tokens.append(word)
			word = []
	stream = " ".join(tokens)
	return stream.replace("  ", " ")

""" Replaces every word in a string with its corresponding stem """
def stemWords(query):
	query = query + " "
	p = PorterStemmer.PorterStemmer()
	output = ''
	word = ''
	for c in query:
		if c.isalpha():
			word += c
		else:
			if word:
				output += p.stem(word, 0, len(word)-1)
				word = ''
			output += c
	output = output.rstrip() #remove any trailing whitespace
	return output


""" Returns a dictionary representation of the document-term occurrence vectors listed in file V.
E.g. {d0:{t1:p1, t2:p2}} gives the positions for terms t1 and t2 in document d0."""
def vecToDic(V):
	docDic = {}
	lineNum = 0	
	for line in V:
		words = line.rstrip('\n').split(' ')
		lineDic = dict([(int(words[i].split(':')[0]), int(words[i].split(':')[1])) for i in range(2,len(words))])
		docDic[lineNum] = lineDic
		lineNum += 1
	return docDic

""" Returns a list of vocabulary words from features file F. """
def extractVocabulary(F):
	return [x for x in F]

""" Returns the number of documents using the vector representation file. """
def countDocs(V):
	lineNum= 0
	for line in V:
		lineNum += 1
	return lineNum

""" Returns the number of docs in class c using training data file T. """
def countDocsInClass(T, c):
	count = 0	
	for line in T:
		if int(line.split(' ')[1]) == c:
			count += 1
	return count

""" Returns a list of docs in class c using training data file T. """
def getDocsInClass(T, c):
	clist = []
	for line in T:
		docID, classID = [int(x) for x in line.split(' ')]
		if classID == c:
			clist.append(docID)
	return clist

""" Returns the number of occurrences of t in training file T from class c. 
V is the vector representation. """
def countTokensOfTerm(T,t,c,v):
	count = 0	
	docs = getDocsInClass(T,c)
	for doc in docs:
		count += v[doc][t]
	return count

""" Returns a list of terms in a doc d from the vector representation """
def extractTokensFromDoc(v,d):
	return v[d].keys()

def argmax(elements, dic):
	score = dic[elements[0]]
	top = elements[0]
	for element in elements:
		if dic[element] > score:
			top = element
			score = dic[element]
	return top

""" T is the training data file, V is the vector representation file, F is the features file """
def TrainMultinomialNB(T,V,F):
	Vlist = extractVocabulary(F)
	N = countDocs(V)
	C = [i for i in range(11)] # categoryIDs
	v = vecToDic(vecRepFile)
	prior = {}
	Tct = dict((i,{}) for i in C)
	condprob = dict((i,{}) for i in C)
	for c in C:
		Nc = countDocsInClass(T,c)
		prior[c] = (0.0 + Nc)/N
		for term in Vlist:
			Tct[c][t] = countTokensOfTerm(T,term,c,v)
		for term in vlist:
			condprob[c][t] = (Tct[c][t] + 1.0)/(sum([x for x in Tct[c].values()]))
	return (Vlist, prior, condprob)

def ApplyMultinomialNB(T,V,prior,condprob,d):
	W = extractTokensFromDoc(V,d)
	C = [i for i in range(11)] # categoryIDs
	score = {}	
	for c in C:
		score[c] = log(prior[c])
	for t in W:
		score[c] += log(condprob[c][t])
	return argmax(C,score) 
		

if len(sys.argv) < 7:
	print "format: "+sys.argv[0]+" method features vectorRep trainingSet docs results"
	exit()

# Open files for reading and writing
featuresFile = open(sys.argv[2], 'r')
vecrepFile = open(sys.argv[3], 'r')
trainingFile = open(sys.argv[4], 'r')
docsFile = open(sys.argv[5], 'r')
resultsFile = open(sys.argv[6], 'w')

