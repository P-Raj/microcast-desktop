from mpi4py import MPI

class Communicator:

	def __init__(self):
		self.setupCommunicator()

	def setupCommunicator(self):
		self.commWorld = MPI.COMM_WORLD
		self.totalProc = self.commWorld.Get_size()
		self.procId = self.commWorld.Get_rank()   

	def getMyId(self):
		return self.procId

	def informClient(self):
		print("You are process number # %d of %d processes", 
			self.procId, self.totalProc)

	def setupChannel(numProcs):
		pass

	def send(fromProc, toProc, message):
		pass

	def receive(fromProc, toProc):
		pass

	def sendToRandom(fromProc, toProc):
		pass

	def broadcast(fromProc):
		pass

	def sendDownloadRequest():
		pass

	def sendSegment():
		pass

	def requestSegment():
		pass

	def waitForFeedback():
		pass