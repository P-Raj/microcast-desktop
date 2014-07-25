
class Communicator:

	def __init__(self, commWorld):
		self.commWorld = commWorld

	def setupCommunicator(self):
        commWorld = MPI.COMM_WORLD
        self.totalProc = commWorld.Get_size()
        self.procId = commWorld.Get_rank()   

	def setupChannel(numProcs):
		pass

	def send(from, to, message):
		pass

	def receive(from, to):
		pass

	def sendToRandom(from, to):
		pass

	def broadcast(from):
		pass

	def sendDownloadRequest():
		pass

	def sendSegment():
		pass

	def requestSegment():
		pass

	def waitForFeedback():
		pass