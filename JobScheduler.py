from mpi4py import MPI
import MicroDownload as MD
import MicroNC as MN

SegmentAssignProcId = 0

class JobScheduler:

    def __init__(self, environment):
        self.environment = environment   

    def isSegmentAssigner(self):
    	return self.environment.procId == SegmentAssignProcId

    def runMicroDownload(self):
		if self.isSegmentAssigner():
			MD.microDownload()

	def runMicroNC(self):
		MN.microNC()
