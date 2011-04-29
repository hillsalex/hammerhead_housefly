import random
import os
import math
import shutil


########INSTRUCTIONS##########
##Put whatever version of svm in a folder final/svm. 
##i.e. linux version goes in final/svm/svm_learn etc...

f0 = open('svmpredict0temp.dat')
f1 = open('svmpredict1temp.dat')
f2= open('svmpredict2temp.dat')
f3 = open('svmpredict3temp.dat')
f4 = open('svmpredict4temp.dat')
f5 = open('svmpredict5temp.dat')
f6 = open('svmpredict6temp.dat')
f7 = open('svmpredict7temp.dat')
f8 = open('svmpredict8temp.dat')
f9 = open('svmpredict9temp.dat')
f10 = open('svmpredict10temp.dat')

labels = open('labelSMV.dat','w')

for line in f0:
	a0 = line
	a1 = f1.readline()
	a2 = f2.readline()
	a3 = f3.readline()
	a4 = f4.readline()
	a5 = f5.readline()
	a6 = f6.readline()
	a7 = f7.readline()
	a8 = f8.readline()
	a9 = f9.readline()
	a10 = f10.readline()
	if float(a0) > 0.1:
		labels.write(str(0) + ' ')
	if float(a1) > 0.1:
		labels.write(str(1) + ' ')
	if float(a2) > 0.1:
		labels.write(str(2) + ' ')
	if float(a3) > 0.1:
		labels.write(str(3) + ' ')
	if float(a4) > 0.1:
		labels.write(str(4) + ' ')
	if float(a5) > 0.1:
		labels.write(str(5) + ' ')
	if float(a6) > 0.1:
		labels.write(str(6) + ' ')
	if float(a7) > 0.1:
		labels.write(str(7) + ' ')
	if float(a8) > 0.1:
		labels.write(str(8) + ' ')
	if float(a9) > 0.1:
		labels.write(str(9) + ' ')
	if float(a10) > 0.1:
		labels.write(str(10) + ' ')
	labels.write('\n')
	
	
	
	