
class CpHandler:

	def __init__(self, processId, numProcs, cpInitiator, cpEnabled=False):
		self.processId = processId
		self.numProcs = numProcs
		self.cpEnabled = cpEnabled
		self.cpTaken = False
		self.cpInitiator = cpInitiator

	def initiateCheckpoint(self):
		pass

	def takeCheckpoint(self):
		pass

	def handleIncomingMsg(self, msg):
		pass

	def handleOutgoingMsg(self, msg):
		pass

	def _getDependentProcs(self):
		pass

	def sendCpRequest(self):
		pass