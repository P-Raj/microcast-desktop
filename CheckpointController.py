import dmtcp
import datetime

class CheckpointHandler:

	def __init__(self, procId, totalProcs):

		self.procId = procId
		self.totalProcs = totalProcs
		self.dependency = []
		self.cpEnabled = True
		self.cpTaken = False
		self.cpAlert = False
		self.cp = []
		self.confirmReceived = {}

	def handleRequests(self, reqMsg):

		assert(type(reqMsg)==type(CheckpointMessage))

		if reqMsg.type == "CheckpointRequest":
			cpReqMsgs, cpConfirmMsg = self._handleCpRequest(reqMsg)
			return cpReqMsgs, cpConfirmMsg

		elif reqMsg.type == "CheckpointConfirmation":
			self._handleCpConfirmation(reqMsg)

		else:
			raise Exception("Unknown checkpoint message")

	def _handleCpRequest(self, cpReq):

		sel.cpAlert = True
		self.cpTaken = True

		startTime = datetime.datetime.now()
		session = dmtcp.checkpoint()
		self.cp.append((session,
						datetime.datetime.now()-startTime))

		newCpReqs = []

		for nrecs in (x for x in self.dependency \
						if x not in cpReq.dependency):
			newCpReqs.append(CheckpointMessage(self.procId,cpReq.initiatorId,x))

		return newCpReqs


	def _handleCpConfirmation(self, cpCnf):

		assert(cpCnf.sender in self.confirmReceived)

		self.confirmReceived[cpCnf.sender] = True

		for proc in cpCnf.reqSentto:
			self.confirmReceived[cpCnf.sender] = self.confirmReceived.get(cpCnf.sender,
																			False)

	def completeCheckpointing(self):
		return self.cpTaken and all(self.confirmReceived.values())

	def updateDependency(self, depProcId):

		if depProcId not in self.dependency:
			self.dependency.append(depProcId)

	def _takeCheckpoint(self):
		pass

	def blockMessage(self, blockMsg):
		pass

