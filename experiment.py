import os

totalProcs = 13
numSegs = 15

for proc in range(2,totalProcs):
	command = "mpiexec -n " + str(proc) + " python main.py -s " + str(numSegs)
	print "executing command :", command
	os.system(command)
	print "Completed"
