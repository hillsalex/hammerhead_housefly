from bool_parser import bool_expr_ast
import sys
import PorterStemmer

ONE_WORD_QUERY = 1
FREE_TEXT_QUERY = 2
PHRASE_QUERY = 3
BOOLEAN_QUERY = 4


if len(sys.argv) < 4:
    print "format: "+sys.argv[0]+" stopwords index titles"
    exit()

queries = sys.stdin.readlines()

""" Returns the query type (e.g. boolean query) """
def getQueryType(query):
    if query[0]=="\"" and query[len(query)-1]=="\"":
        return PHRASE_QUERY
    if type(bool_expr_ast(query)).__name__=='tuple':
        return BOOLEAN_QUERY
    for i in range(len(query)):
        if query[i] == " ":
            return FREE_TEXT_QUERY
    return ONE_WORD_QUERY

""" Returns a list of documents containing the given word """
def getDocsWithWord(word):
    docs = []
    index = open(sys.argv[2])
    for line in index:
        line = line.split(" ", 1)
        if line[0]==word:
            doclist = eval(line[1].strip('\n'))
            for word_instance in doclist:
                docs.append(int(word_instance[0]))
    docs = removeDuplicatesAndSort(docs)
    return docs

""" Returns a list of (document, location) tuples corresponding to the given word """
def getDocLocsWithWord(word):
    docs = []
    index = open(sys.argv[2])
    for line in index:
        line = line.split(" ", 1)
        if line[0]==word:
            doclist = eval(line[1].strip('\n'))
            for word_instance in doclist:
                docs.append((int(word_instance[0]), word_instance[1]))
    docs = removeDuplicatesAndSort(docs)
    return docs

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
    return getDocsWithWord(query)

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
        docs.extend(getDocsWithWord(word))
    return removeDuplicatesAndSort(docs)

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
    return removeDuplicatesAndSort(docs)

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
    query = bool_expr_ast(query)
    return getDocsFromBool(query)

for query in queries:
    query = query.rstrip('\n')
    docs = []
    qtype = getQueryType(query)
    if qtype==ONE_WORD_QUERY:
        docs = parseOneWordQuery(query)
    elif qtype==FREE_TEXT_QUERY:
        docs = parseFreeTextQuery(query)
    elif qtype==PHRASE_QUERY:
        docs = parsePhraseQuery(query)
    elif qtype==BOOLEAN_QUERY:
        docs = parseBooleanQuery(query)
    print " ".join([str(i) for i in docs])
