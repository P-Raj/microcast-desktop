from mpi4py import MPI
from random import randrange, choice
import Queue
from CheckpointController import CpHandler
import resource
from Message import CheckpointMessage

class Communicator:

	def __init__(self, numSegs):
		self.setupCommunicator()
		self.totalSegs = numSegs
		self.ckptCntrl = CpHandler(self.procId, self.totalProc)

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

	def send(self, toProc, message):

		if self.ckptCntrl.cpEnabled and self.ckptCntrl.cpTaken:
			message.setBB(True)
		else:
			message.setBB(False)

		if self.getMyId() == toProc:
			self.loopChannel.put(message)
		else:
			self.commWorld.isend(message, dest=toProc)

	def _receive(self, fromProc):

		recvdMsg = self.loopChannel.get() if fromProc==self.getMyId() else self.commWorld.recv(source=fromProc)


		if type(recvdMsg)==type(CheckpointMessage):
				self.ckptCntrl.handleRequest(recvdMsg)
				return None

		if self.ckptCntrl.messageConsumptionAllowed(recvdMsg):
			# consume the message
			return recvdMsg

		return None

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
