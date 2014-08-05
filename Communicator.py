from mpi4py import MPI
from random import randrange, choice
import Queue


class Communicator:

	def __init__(self, numSegs):
		self.setupCommunicator()
		self.totalSegs = numSegs
		
	def setupCommunicator(self):
		self.commWorld = MPI.COMM_WORLD
		self.totalProc = self.commWorld.Get_size()
		self.procId = self.commWorld.Get_rank()
		self.loopChannel = Queue.Queue()

	def getMyId(self):
		return self.procId

	def getNumSegs(self):
		return self.totalSegs

	def setUpBarrier(self):
		self.commWorld.Barrier()

	def informClient(self):
		print("You are process number #", self.procId , " of " ,self.totalProc, " processes")

	def send(self, toProc, message):
		if self.getMyId() == toProc:
			self.loopChannel.put(message)
		else:
			self.commWorld.isend(message, dest=toProc)

	def _receive(self, fromProc):
		if self.getMyId() == fromProc:
			return self.loopChannel.get()
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
			if procId!=self.getMyId() and self.commWorld.Iprobe(source = procId):
				_channels.append(procId)

		if not self.loopChannel.empty():
			_channels.append(self.getMyId())

		return _channels

	def blockingReceive(self):
		#blocking wait function
		#returns None if there is no message waiting
		nonEmptyChannels = self.getNonEmptyChannels()
		while not nonEmptyChannels:
			nonEmptyChannels = self.getNonEmptyChannels()
		return self._receive(choice(nonEmptyChannels))

	def nonBlockingReceive(self):

		nonEmptyChannels = self.getNonEmptyChannels()
		if nonEmptyChannels:
			return self._receive(choice(nonEmptyChannels))
		return None
