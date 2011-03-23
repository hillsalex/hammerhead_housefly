from bool_parser import bool_expr_ast
import sys
import PorterStemmer
import time
import math

MIN_WILD_LENGTH = 2
LONG_WORD_LENGTH = 30

""" Query-type constants """
ONE_WORD_QUERY = 1
FREE_TEXT_QUERY = 2
PHRASE_QUERY = 3
BOOLEAN_QUERY = 4
WILDCARD_QUERY = 5

if len(sys.argv) < 4:
	print "format: "+sys.argv[0]+" stopwords index titles"
	exit()
	
queries = sys.stdin.readlines()

""" Returns a list of permutations for single wildcard queries """
def permute_single(s):
	result = []
	s = s + '$'
	for i in range(len(s)):
		sp = s[i+1:] + s[:i+1]
		result.append(sp)
	return result

""" Returns a list of permutations for double wildcard queries """
def permute_double(s):
	result = []
	for i in range(len(s)):
		for j in range(i+1,len(s)+1):
			new = s[j:] + '$' + s[:i]
			if len(new) >= MIN_WILD_LENGTH:
				result.append(new)
	return result

""" Returns a list of all necessary permutations for a query """
def do_permute(s):
	result = permute_single(s)
	result.extend(permute_double(s))
	return result

""" Adds an element to hash table """
def htable_add(s, line_num):
	if len(s) > LONG_WORD_LENGTH: 
		long_words[s] = line_num
		return
	for x in do_permute(s): 
		#if len(x) < MIN_WILD_LENGTH + 2: continue
		if ht.has_key(x):
			ht[x] = ht[x] + " " + str(line_num)
			a = 1
		else:
			ht[x] = str(line_num)

""" Given a rotated query, returns the list of rows of long word matches """
def checkLongWords(query):
	result = []
	for word in long_words.keys():
		for permuterm in do_permute(word):
			if permuterm==query:
				result.append(long_words[word])
	return result

""" Returns rotated form of query with one wildcard """    
def rotate1wild(s):
	s = s + '$'
	b = list(s)
	return s[b.index('*')+1:] + s[:b.index('*')]
	
""" Returns (rotated form, middle) of query with two wildcards as tuple """    
def rotate2wild(s):
	s = s + '$'
	b = list(s)    
	i = b.index('*')
	s = s[:i] + s[i+1:]
	b = list(s)
	j = b.index('*')
	return (s[j+1:] + s[:i], s[i:j])

""" Returns a list of row numbers matching the wildcard query """
def getWildcardRows(s):
	b = list(s)
	result = []
	if b.count('*')==1:
		res = rotate1wild(s)
		result = checkLongWords(res)
		if ht.has_key(res):
			result.extend(str(ht[res]).split(" "))
	if b.count('*')==2:
		if s[0]=='*' and s[len(s)-1]=='*':
			result = rowsWithSubstring(s[1:len(s)-1])
		else:
			res = rotate2wild(s)
			result = checkLongWords(res[0])
			if ht.has_key(res[0]):
				result.extend(str(ht[res[0]]).split(" "))
			result = postProcess(result, res[1])
	return result
	
""" Filters and returns only the rows corresponding to words which contain the substring 'sub' """
def postProcess(rows, sub):
	return [row for row in rows if getQueryByNumber(row)[0].find(sub)!=-1]
	
""" Returns all rows in index with word containing substring 'sub' """
def rowsWithSubstring(sub):
	index = open(sys.argv[2], 'r')
	line_num = 0
	result = []
	for line in index:
		words = line.split(' ', 1)
		if words[0].find(sub)!=-1:
			result.append(line_num)
		line_num += 1
	return result
	
""" Returns a (query, docs) tuple for a given line number """
def getQueryByNumber(num):
	num = int(num)
	index = open(sys.argv[2], 'r')
	line_num = 0
	for line in index:
		if line_num==num:
			words = line.split(' ', 1)
			return (words[0], words[1])
		line_num += 1

""" Returns the query type (e.g. boolean query) """
def getQueryType(query):
	if query[0]=="\"" and query[len(query)-1]=="\"":
		return PHRASE_QUERY
	if type(bool_expr_ast(query)).__name__=='tuple':
		return BOOLEAN_QUERY
	for i in range(len(query)):
		if query[i] == " ":
			return FREE_TEXT_QUERY
		if query[i] == "*":
			return WILDCARD_QUERY
	return ONE_WORD_QUERY

""" Returns all the index data associated with a given word (as a string) """
def getDataWithWord(word):
	docs = []
	index = open(sys.argv[2])
	for line in index:
		words = line.split(" ", 1)
		if words[0]==word:
			return line.strip('\n')

""" Given parsed index data (word, idf, docs/positions list), returns a list of docs """
def getDocsFromData(data):
	return removeDuplicatesAndSort([x[0] for x in data[2]])
	
def getDocLocsFromData(data):
	return [(x[0], x[i]) for x in data[2] for i in range(1,len(x))]

""" Returns a list of documents containing the given word """
def getDocsWithWord(word):
	data = getDataWithWord(word)
	if not data:
		return []
	else:
		return getDocsFromData(parseDocData(data))

""" Returns a list of (document, location) tuples corresponding to the given word, which may contain wildcards """
def getDocLocsWithWord(word):
	data = getDataWithWord(word)
	if not data:
		return []
	wildcard = False
	for letter in word:
		if letter=='*':
			wildcard = True
	if wildcard:
		rows = getWildcardRows(word)
		for row in rows:
			line = getQueryByNumber(getWildcardRows(word))
			result_list.append(line[1].strip('\n'))
	else:
		return getDocLocsFromData(parseDocData(data))

def parseDocData(docdata):
	if not docdata:
		return []
	docdata = docdata.split(" ",2)
	docdata = (docdata[0], docdata[1], docdata[2].split(","))
	docdata[2].pop() # remove element created by trailing comma
	for i in range(len(docdata[2])):
		docdata[2][i] = docdata[2][i].split(" ")
	result = [[] for x in docdata[2]]
	for i in range(len(docdata[2])):
		for num in docdata[2][i]:
			result[i].append(int(num))
	return (docdata[0], float(docdata[1]), result)

""" Returns a list of documents that satisfy the given boolean expression """
def getDocsFromBool(expr):
	if type(expr).__name__=='str':
		return getDocsWithWord(expr)
	elif type(expr).__name__=='tuple':
		if expr[0]=='OR':
			docs = []
			for elem in expr[1]:
				docs.extend(getDocsFromBool(elem))
			return removeDuplicatesAndSort(docs)
		if expr[0]=='AND':
			docset = {}
			for i in range(len(expr[1])):
				elem = expr[1][i]
				if i==0:
					docset = set(getDocsFromBool(elem))
				else:
					docset = docset.intersection(set(getDocsFromBool(elem)))
			return removeDuplicatesAndSort(list(docset))

""" Given a list of (word, idf, docs/positions list) index data, returns the data with only docs included in 'docs' """
def removeDocsFromData(data, docs):
	return [(x[0], x[1], [y for y in x[2] if y[0] in docs]) for x in data]
				
""" Removes operators from a string """
def removeOperators(query):
	query = query.replace("AND ", "")
	query = query.replace("OR ", "")
	query = query.replace("(", "")
	query = query.replace(")", "")
	query = query.replace("\"", "")
	return query

""" Converts a stream of characters into a stream of tokens """
def tokenize(query):
	query = query + " "
	tokens = []
	word = []
	for char in query:
		if isAlphaNumeric(char):
			word.append(char)
		else:
			word = "".join(word)
			tokens.append(word)
			word = []
	stream = " ".join(tokens)
	return stream.replace("  ", " ")

""" Returns true if a character is [a-z0-9] """
def isAlphaNumeric(char):
	if (ord(char) > 96 and ord(char) < 123) or (ord(char) > 47 and ord(char) < 58):
		return True
	else:
		return False

""" Removes stop words from a string """
def removeStopWords(query):
	stop_words = open(sys.argv[1])
	query = query.split(" ")
	for stop_word in stop_words:
		stop_word = stop_word.strip('\n')
		query = [word for word in query if word!=stop_word]
	query = " ".join(query)
	return query

""" Removes duplicates from and sorts a list """
def removeDuplicatesAndSort(a_list):
	a_list = list(set(a_list)) # remove duplicates
	a_list.sort() # sort
	return a_list

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
				output += p.stem(word,0,len(word)-1)
				word = ''
			output += c
	output = output.rstrip() # remove any trailing whitespace
	return output

""" Parse a one word query and return matching documents """
def parseOneWordQuery(query):
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	output = []
	output.append(parseDocData(getDataWithWord(query)))
	return output

""" Parse a free text query and return matching documents """
def parseFreeTextQuery(query):
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	query_list = query[0:len(query)].split(" ")
	docs = []
	for word in query_list:
		docs.append(parseDocData(getDataWithWord(word)))
	return docs

""" Parse a phrase query and return matching documents """
def parsePhraseQuery(query):
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	query_list = query[0:len(query)].split(" ")
	if len(query_list) < 2:
		return getDocsWithWord(query)
	docloc_list = [getDocLocsWithWord(query_list[i]) for i in range(len(query_list))]
	possible_docs = docloc_list[0]
	delete_flags = {}
	for i in range(len(possible_docs)):
		delete_flags[i] = False
		docloc_poss = possible_docs[i]
		for j in range(1, len(query_list)):
			found_one = False
			for docloc in docloc_list[j]:
				if docloc[0]==docloc_poss[0] and docloc[1]==docloc_poss[1]+j:
					found_one = True
					break
			if not found_one:
				delete_flags[i] = True
				break    
	docs = [possible_docs[i][0] for i in range(len(possible_docs)) if delete_flags[i]==False]
	#docs = removeDuplicatesAndSort(docs)
	data = parseFreeTextQuery(query)
	return removeDocsFromData(data, docs)

""" Parse a boolean query and return matching documents """
def parseBooleanQuery(query):
	# Escape AND/OR operators
	query = query.replace("AND", "1and")
	query = query.replace("OR", "1or")
	query = query.lower()
	#query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	query = query.replace("1and", "AND")
	query = query.replace("1or", "OR")
	queryWords = query.replace("AND", "").replace("OR", "").replace("(", "").replace(")", "").replace("  ", " ")
	data = parseFreeTextQuery(queryWords)
	query = bool_expr_ast(query)    
	return removeDocsFromData(data, getDocsFromBool(query))

""" Parse a wildcard query and return matching documents """
def parseWildcardQuery(query):
	#print "On query "+query
	rows = getWildcardRows(query)
	doclist = []
	for row in rows:
		#print "row: "+str(row)
		result = getQueryByNumber(row)
		#print result[0]
		doclist.append(parseDocData(result[1].strip('\n')))
	return doclist


def oneWordQueryVector(query):
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	output = {}
	output[query[0]] = 1
	
def createWildcardVector(query,docs):
	print 'f'

def getOWQDocRank(docs,query):
	docscores = {}
	for termdocs in docs:
		if len(termdocs)>0:
			term = termdocs[0]
			doclocations = termdocs[2:]
			for doc in doclocations[0]:
				count=len(doc[1:])
				#docscores[str(int(doc[0])+1)]=queryweights[term]*count/docweights[str(int(doc[0])+1)]
				docscores[str(int(doc[0])+1)]=count/docweights[str(int(doc[0])+1)]
				
def getFTQDocRank(docs,query):
	queryweights = {}
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	query_list = query[0:len(query)].split(" ")
	docscores = {}
	for termdocs in docs:
		if len(termdocs)>0:
			term = termdocs[0]
			idf = termdocs[1]+1
			doclocations = termdocs[2:]
			for doc in doclocations[0]:
				count=len(doc[1:])
				docscores[str(int(doc[0])+1)]=math.log10(len(query_list)/idf)*count/docweights[str(int(doc[0])+1)]
				#docscores[str(int(doc[0])+1)]=count/docweights[str(int(doc[0])+1)]

def getPQDocRank(docs,query):
	queryweights = {}
	query = removeOperators(query)
	query = query.lower()
	query = tokenize(query)
	query = removeStopWords(query)
	query = stemWords(query)
	query_list = query[0:len(query)].split(" ")
	docscores = {}
	for termdocs in docs:
		if len(termdocs)>0:
			term = termdocs[0]
			idf = termdocs[1]+1
			doclocations = termdocs[2:]
			for doc in doclocations[0]:
				count=len(doc[1:])
				docscores[str(int(doc[0])+1)]=math.log10(len(query_list)/idf)*count/docweights[str(int(doc[0])+1)]
				#docscores[str(int(doc[0])+1)]=count/docweights[str(int(doc[0])+1)]
	for k,v in docscores.iteritems():
		print str(k) + ' ' + str(v)
	
	
#print "Preprocessing"
start = time.time()
start2 = time.time()

''' Preprocessing - generate hash table '''
ht = {}
long_words = {}
docweights = {}
index = open(sys.argv[2], 'r');
line_num = 0
for line in index:
	if line[0]!=';':
		words = line.split(' ')
		if line_num%20000==0:
			#print str(line_num) + " on "+ str(time.time() - start2)
			start2 = time.time()
		htable_add(words[0], line_num)
		line_num += 1
	else:
		weights = line.split(' ')[1:-1]
		for weight in weights:
			weight = weight.split(',')
			docweights[str(int(weight[0])+1)]=math.sqrt(float(weight[1]))

#print "Done preprocessing ("+str(time.time() - start)+" seconds)."

for query in queries:
	query = query.rstrip('\n')
	docs = []
	qtype = getQueryType(query)
	if qtype==ONE_WORD_QUERY:
		docs = parseOneWordQuery(query)
		
		getOWQDocRank(docs,query)
	elif qtype==FREE_TEXT_QUERY:
		docs = parseFreeTextQuery(query)
		getFTQDocRank(docs,query)
	elif qtype==PHRASE_QUERY:
		docs = parsePhraseQuery(query)
		getPQDocRank(docs,query)
	elif qtype==BOOLEAN_QUERY:
		docs = parseBooleanQuery(query)
	elif qtype==WILDCARD_QUERY:
		docs = parseWildcardQuery(query)
	print docs