
from JobScheduler import JobScheduler
from Communicator import Communicator
import Logging
import sys
import getopt


def readCmdArgs():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hs:", ["num_seg"])
	except geopt.GetoptError:
		print sys.argv[0] + ' -s <number of segments>'
		sys.exit(2)
	
	#default values
	numSeg = 3
	initiator = 2
		
	for opt,arg in opts:
		if opt == '-h':
			print "mpiexec -n <num of processes> python <main file>.py -s <number of segemnts> "
			sys.exit()
		elif opt in ("-s", "--num_seg"):
			numSeg = arg
			initiator = arg-1
	return (numSeg,initiator)
	
numSegs, initiator = readCmdArgs()

# set up the distributed environment
environment = Communicator(numSegs)
processId = environment.getMyId()

Logging.setLevel('debug')

procJobScheduler = JobScheduler(environment)


if processId == initiator:
	procJobScheduler.runMicroDownload()
else:
	procJobScheduler.runMicroNC()

