import sys
import math
import time

classes = {}
classtotals = {}

trainFile = open(sys.argv[4],'r')
featureFile = open(sys.argv[2],'r')
vecrepFile = open(sys.argv[3],'r')
docFile = open(sys.argv[5],'r')
results = open(sys.argv[6],'w')

def trainRoc():
	curline = 0
	for line in trainFile:
		if curline%100==0:
			print curline
		curline = curline + 1
		trainInfo = line.strip().split(' ',2)
		vec = getVecRep(trainInfo[0])
		if trainInfo[1] in classes:
			for key,value in vec.iteritems():
				if key in classes[trainInfo[1]]:
					(classes[trainInfo[1]])[key] = (classes[trainInfo[1]])[key] + value
				else:
					(classes[trainInfo[1]])[key]=value
		else:
			classes[trainInfo[1]] = vec
			classtotals[trainInfo[1]] = 1
	for key,value in classes.iteritems():
		v = {}
		total = classtotals[key]
		for k,val in value.iteritems():
			v[k]=float(val)/float(total)
		classes[key]=v
		
def getVecRep(docNum):
	vecrepFile.seek(0)
	vec = {}
	for line in vecrepFile:
		info = line.split(' ')
		if (info[0]!=docNum):
			continue
		magnitude = math.sqrt(float(info[1]))
		for termpair in info[2:]:
			termpair = termpair.strip().split(':')
			vec[termpair[0]]=float(termpair[1])/float(magnitude)
	return vec
	
def applyRoc():
	featureFile.seek(0)
	totalFeatures = 0
	for line in featureFile:
		totalFeatures = totalFeatures + 1
	curline = 0
	for line in docFile:
		if curline%10000==0:
			print curline
		curline = curline + 1
		trainInfo = line.strip().split(' ')
		vec = getVecRep(trainInfo[0])
		currentBestID = 0
		currentBest = sys.maxint
		for docclass,centroid in classes.iteritems():
			total = 0
			for i in range(totalFeatures):
				x = 0
				y = 0
				if str(i) in centroid:
					x = centroid[str(i)]
				if str(i) in vec:
					y = vec[str(i)]
				total = total + float(x)-float(y)
			total = math.fabs(total)
			if float(total) < float(currentBest):
				currentBest = total
				currentBestID = docclass
		results.write(trainInfo[0] + " " + currentBestID + '\n')

start = time.time()	
trainRoc()

end = time.time()

elapsed= end - start

min = elapsed/60
print('Time elapsed to train: ' + str(min))

start = time.time()
applyRoc()

end = time.time()

elapsed= end - start

min = elapsed/60
print('Time elapsed to classify: ' + str(min))