import Queue

class CpMessage:

	def __init__(self, message):
		self.message = message
		self.blockBit = False
		self.senderDependency = []

	def setBlockBit(self):
		self.blockBit = True

	def setDependency(self, senderDependency):
		self.senderDependency = senderDependency


class CpHandler:

	def __init__(self, processId, numProcs, cpInitiator, communicator, cpEnabled=False):
		self.processId = processId
		self.numProcs = numProcs
		self.cpEnabled = cpEnabled
		self.cpTaken = False
		self.cpInitiator = cpInitiator
		self.dependency = []
		self.BQ = self.initBQ()
		self.communicator = communicator

	def addDependency(self, procId):
		if procId not in self.dependency:
			self.dependency.append(procId)

	def initBQ(self):
		self.BQ = []
		for _ in range(self.numProcs):
			self.BQ.append(Queue.Queue())

	def initiateCheckpoint(self):
		pass

	def takeCheckpoint(self):
		pass

	def sendCheckpointingReqs(self):
		for proc in self._getDependentProcs():
			communicator.send(proc, CheckpointRequest(self.processId, self._getDependentProcs()))

	def augmentOutgoingMsg(self, msg):
		if not self.cpEnabled:
			return msg
		else:
			augMsg = CpMessage(msg)
			if self.cpTaken:
				augMsg.setBlockBit()
			return augMsg

	def _pushToBQ(self, fromProc, msg):
		self.BQ[fromProc].put(msg)

	def _getFromBQ(self, fromProc):
		self.BQ[fromProc].get()

	def _isEmptyBQ(self, fromProc):
		return self.BQ[fromProc].Empty()

	def handleIncomingMsg(self, msg):
		if type(msg)==type(CpMessage):
			assert(self.cpEnabled)
		else:
			assert(not self.cpEnabled)
		self.addDependency(msg.message.sender)

	def _getDependentProcs(self):
		pass

	def sendCpRequest(self):
		pass