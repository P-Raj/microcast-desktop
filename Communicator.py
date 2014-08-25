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

		# assert variables
		self.assertSendId = 0
		self.assertReceiveId = [-1] * self.totalProc

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

	def trySendingCp(self):

		if self.ckptCntrl.checkpointInitAllowed():
			for msg in self.ckptCntrl.checkpointInit():

				#asserts that message sent is in order i.e. m0 < m1 < m2
				assert(self.assertSendId == msg.num)
				self.assertSendId+=1

				if self.getMyId() == msg.receiver:
					self.loopChannel.put(msg)
				else:
					self.commWorld.isend(msg, dest=msg.receiver)


	def send(self, toProc, message):

		self.trySendingCp()

		#asserts that message sent is in order i.e. m0 < m1 < m2
		assert(self.assertSendId == message.num)
		self.assertSendId+=1

		message.setBB(self.ckptCntrl.cpEnabled and self.ckptCntrl.cpTaken)

		if self.getMyId() == toProc: self.loopChannel.put(message)
		else: self.commWorld.isend(message, dest=toProc)

	def _receive(self, fromProc):

		recvdMsg = self.loopChannel.get() if fromProc==self.getMyId() else self.commWorld.recv(source=fromProc)

		#assert that the message received has a higher id than the previously received message
		assert(self.assertReceiveId[recvdMsg.sender] < recvdMsg.num)
		self.assertReceiveId[recvdMsg.sender] = recvdMsg.num

		if isinstance(recvdMsg,CheckpointMessage):
			self.ckptCntrl.handleRequests(recvdMsg)
			return None

		if self.ckptCntrl.messageConsumptionAllowed(recvdMsg):
			return recvdMsg # consume the message

		return None

	def sendToRandom(self, message):

		self.send(randrange(self.totalProc), message)

	def sendBroadcast(self, message):

		self.commWorld.bcast(message, root = self.procId)

	def receiveBroadcast(self, fromProc):

		return self.commWorld.bcast(None, root=fromProc)

	def getNonEmptyChannels(self):

		_channels = [procId for procId in range(self.totalProc) if procId!=self.getMyId() and self.commWorld.Iprobe(source = procId)]

		if not self.loopChannel.empty(): _channels.append(self.getMyId())

		return _channels

	def blockingReceive(self):
		#blocking wait function
		#returns None if there is no message waiting

		nonEmptyChannels = self.getNonEmptyChannels()

		while not nonEmptyChannels:
			nonEmptyChannels = self.getNonEmptyChannels()

		return self._receive(choice(nonEmptyChannels))

	def nonBlockingReceive(self):

		self.trySendingCp()

		nonEmptyChannels = self.getNonEmptyChannels()

		if nonEmptyChannels: return self._receive(choice(nonEmptyChannels))
		return None
