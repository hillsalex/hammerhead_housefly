import random
import os
import math
import shutil


########INSTRUCTIONS##########
##Put whatever version of svm in a folder final/svm. 
##i.e. linux version goes in final/svm/svm_learn etc...

for c in range(11):
	os.system('./svm/svm_classify -v 0 finalDocs.dat svmmodel'+str(c)+'temp.dat svmpredict'+str(c)+'temp.dat')
	print str(float(c+1)/float(11)*100) + '% done'