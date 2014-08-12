import dmtcp
import datetime
import Queue
import resource

class CpHandler:

	def __init__(self, procId, totalProcs):

		self.procId = procId
		self.totalProcs = totalProcs
		self.dependency = []
		self.cpEnabled = True
		self.cpTaken = False
		self.cpAlert = False
		self.cp = []
		self.confirmReceived = {}
		self.BQ = [Queue.Queue() for _ in range(self.totalProcs)]

	def handleRequests(self, reqMsg):

		assert(type(reqMsg)==type(CheckpointMessage))

		if reqMsg.type == "CheckpointRequest":
			cpReqMsgs, cpConfirmMsg = self._handleCpRequest(reqMsg)
			return cpReqMsgs, cpConfirmMsg

		elif reqMsg.type == "CheckpointConfirmation":
			self._handleCpConfirmation(reqMsg)
			return None, None

		else:
			raise Exception("Unknown checkpoint message")

	def _handleCpRequest(self, cpReq):

		sel.cpAlert = True
		self.cpTaken = True

		self._takeCheckpoint()

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

	def _updateDependency(self, depProcId):

		if depProcId not in self.dependency:
			self.dependency.append(depProcId)

	def _takeCheckpoint(self):

		startTime = datetime.datetime.now()
		session = dmtcp.checkpoint()
		self.cp.append((session,
						datetime.datetime.now()-startTime,
						resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

	def messageConsumptionAllowed(self, message):

		if message.bb and not self.cpAlert:
			self.blockMessage(message)
			return False

		elif not message.bb and not self.cpAlert:
			self._updateDependency(message.sender)
			return True

		elif self.cpAlert and not self.cpTaken:
			self.blockMessage(message)
			return False

		elif self.cpTaken:
			assert(all (x.empty() for x in self.BQ()))
			return True

	def blockMessage(self, blockMsg):

		self.BQ[blockMsg.sender].put(blockMsg)

	def getBlockedMessages(self):

		blockedMessages = []
		for queue in self.BQ:
			while not queue.empty:
				blockedMessages.append(queue.get())
		return blockedMessages
