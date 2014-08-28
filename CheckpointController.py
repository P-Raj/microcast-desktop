import dmtcp
import datetime
import Queue
import resource
import random
import Logging
from Message import *


class CpHandler:

    def __init__(self, procId, totalProcs):

        self.procId = procId
        self.totalProcs = totalProcs
        self.dependency = []
        self.cpEnabled = False
        self.cpTaken = False
        self.cpAlert = False
        self.cp = []
        self.confirmReceived = {}
        self.BQ = [Queue.Queue() for _ in range(self.totalProcs)]

    def _union(self, listA, listB):
        return list(set(listA+listB))

    def handleRequests(self, reqMsg):

        assert(isinstance(reqMsg, CheckpointMessage))

        if isinstance(reqMsg, CheckpointReqMessage):
            cpReqMsgs = self._handleCpRequest(reqMsg)
            return cpReqMsgs

        elif isinstance(reqMsg, CheckpointConfirmMessage):
            self._handleCpConfirmation(reqMsg)
            return None

        else:
            raise Exception("Unknown checkpoint message")

    def checkpointInitAllowed(self):

        if self.procId == 0 and random.randrange(10) == 0 and \
           self.cpEnabled and not self.cpAlert and len(self.dependency) > 0:
            return True

        return False

    def checkpointInit(self):

        self.cpAlert = True
        self.cpTaken = True

        self._takeCheckpoint()

        newCpReqs = []

        for nrecs in (x for x in self.dependency):
            newCpReqs.append(
                CheckpointReqMessage(self.procId,
                                     self.procId,
                                     nrecs,
                                     self.dependency))
            self.confirmReceived[nrecs] = False

        return newCpReqs

    def _handleCpRequest(self, cpReq):

        self.cpAlert = True
        self.cpTaken = True

        self._takeCheckpoint()

        newCpReqs = []

        newDeps = (x for x in self.dependency
                   if x not in cpReq.dependency)

        for nrecs in newDeps:
            newCpReqs.append(
                CheckpointReqMessage(
                    self.procId,
                    cpReq.initiatorId,
                    nrecs,
                    self._union(self.dependency, cpReq.dependency)))

        newCpReqs.append(
            CheckpointConfirmMessage(
                self.procId,
                cpReq.initiatorId,
                newDeps))

        return newCpReqs

    def _handleCpConfirmation(self, cpCnf):

        assert(cpCnf.sender in self.confirmReceived)

        self.confirmReceived[cpCnf.sender] = True

        for proc in cpCnf.reqSentto:
            self.confirmReceived[cpCnf.sender] = self.confirmReceived.get(
                cpCnf.sender,
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
            assert(all(x.empty() for x in self.BQ))
            return True

    def blockMessage(self, blockMsg):

        self.BQ[blockMsg.sender].put(blockMsg)

    def getBlockedMessages(self):

        blockedMessages = []
        for queue in self.BQ:
            while not queue.empty:
                blockedMessages.append(queue.get())
        return blockedMessages
