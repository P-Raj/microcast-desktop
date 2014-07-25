from mpi4py import MPI
import MicroDownload as MD
import MicroNC as MN

SegmentAssignProcId = 0

class JobScheduler:

    def __init__(self, name="default"):
        self.name = name
        self.setUpEnvironment()

    def setUpEnvironment(self):
        self.setupCommunicator()

    def setupCommunicator(self):
        commWorld = MPI.COMM_WORLD
        self.totalProc = commWorld.Get_size()
        self.procId = commWorld.Get_rank()   

    def isSegmentAssigner(self):
    	return self.procId == SegmentAssignProcId

	def runMicroDownload(self):
		if self.isSegmentAssigner():
			MD.microDownload()

	def runMicroNC(self):
		MN.microNC()
