from mpi4py import MPI
from random import randrange

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

	def send(self, toProc, message):
		self.communicator.send(message, dest=toProc)

	def receive(self, fromProc):
		return self.communicator.recv(source= fromProc)

	def sendToRandom(self, message):
		self.send(randrange(self.totalProc), message)

	def sendBroadcast(self, message):
		self.commWorld.bcast(message, root = self.procId)

	def receiveBroadcast(self, fromProc):
		return self.commWorld.bcast(None, root=fromProc)
	
	def waitForFeedback(self):
		#non blocking wait function
		#returns None if there is no message waiting
		for fromProc in range(self.totalProc):
			if fromProc != self.procId:
				if self.commWorld.Iprobe(source = fromProc):
					return comm.recv(source = fromProc)
		return None
