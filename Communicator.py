from mpi4py import MPI
from random import randrange, choice

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
		print("You are process number #", self.procId , " of " ,self.totalProc, " processes")

	def send(self, toProc, message):
		if toProc == 0:
			raise Exception("Not sending to 0")
		self.commWorld.isend(message, dest=toProc)

	def receive(self, fromProc):
		return self.commWorld.recv(source= fromProc)

	def sendToRandom(self, message):
		self.send(randrange(self.totalProc), message)

	def sendBroadcast(self, message):
		self.commWorld.bcast(message, root = self.procId)

	def receiveBroadcast(self, fromProc):
		return self.commWorld.bcast(None, root=fromProc)
	
	def getNonEmptyChannels(self):
		_channels = []
		for procId in range(self.totalProc):
			if procId != self.procId and self.commWorld.Iprobe(source = procId):
				_channels.append(procId)
		return _channels

	def blockingReceive(self):
		#blocking wait function
		#returns None if there is no message waiting
		nonEmptyChannels = self.getNonEmptyChannels()
		while not nonEmptyChannels:
			nonEmptyChannels = self.getNonEmptyChannels()
		return self.receive(choice(nonEmptyChannels))

	def nonBlockingReceive(self):

		nonEmptyChannels = self.getNonEmptyChannels()
		if nonEmptyChannels:
			return self.receive(choice(nonEmptyChannels))
		return None
