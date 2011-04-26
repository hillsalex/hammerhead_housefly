import sys
ans = open(sys.argv[1], 'r')
res = open(sys.argv[2], 'r')

lines = 0
matches = 0
for ansLine in ans:
	ansDoc, ansClass = ansLine.rstrip('\n').split(' ')
	resDoc, resClass = res.readline().rstrip('\n').split(' ')
	if not ansDoc==resDoc:
		sys.exit("DocID mismatch")
	if ansClass == resClass:
		matches += 1
	lines += 1

accuracy = (matches+0.0)/lines
error = 1-accuracy
print "Classification is "+str(accuracy*100)+"% accurate ("+str(matches)+" of "+str(lines)+")"
print "Error: "+str(error*100)+"%"
