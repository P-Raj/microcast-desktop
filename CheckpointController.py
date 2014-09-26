import dmtcp
import datetime
import Queue
import resource
import random
import Logging
from Message import *
import sys
import threading
import os

class CpHandler:

    def __init__(self, procId, totalProcs ):

        self.procId = procId
        self.totalProcs = totalProcs

        self.dependency = []

        self.cpEnabled = True
        self.cpTaken = False
        self.cpAlert = False
        self.cp = None
        self.confirmReceived = {}
        self.BQ = [Queue.Queue() for _ in range(self.totalProcs)]

        self.delayCheckpoint = False
        self.delayCheckpointTime = 10 #seconds

    def _union(self, listA, listB):
        return list(set(listA+listB))

    def _takeCheckpoint(self):

        if not self.cpTaken:

            startTime = datetime.datetime.now()
            session = dmtcp.checkpoint()
            self.cp = (session, datetime.datetime.now()-startTime,
                            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

            self.cpTaken = True

    def handleDownloadComplete(self):

        if self.cpAlert and not self.cpTaken:
            self.cpTimer.cancel()
            self._takeCheckpoint()

    def handleRequests(self, reqMsg):

        assert(isinstance(reqMsg, CheckpointMessage))

	print str(reqMsg), " Received"

        if isinstance(reqMsg, CheckpointReqMessage):

            if self.cpTaken:
                return

            cpReqMsgs = self._handleCpRequest(reqMsg)

            cpTimer = threading.Timer(self.delayCheckpointTime, self._takeCheckpoint)
            cpTimer.start()

            return cpReqMsgs

        elif isinstance(reqMsg, CheckpointConfirmMessage):

            assert(self.isCheckpointInitiator())

            self._handleCpConfirmation(reqMsg)

            return None

        else:
            raise Exception("Unknown checkpoint message")

    def isCheckpointInitiator(self):

        return self.procId == 0

    def checkpointInitAllowed(self):

        if self.isCheckpointInitiator() and random.randrange(10) == 0 and \
           self.cpEnabled and not self.cpAlert and len(self.dependency) > 0:
            return True

        return False

    def checkpointInit(self):

        self.cpAlert = True

	print "initiated Checkpointig"
        print "setting alert"
        self._takeCheckpoint()
	print "taken"

        newCpReqs = []

        for nrecs in (x for x in self.dependency):
            newCpReqs.append(
                CheckpointReqMessage(self.procId,
                                     self.procId,
                                     nrecs,
                                     self.dependency,
                                     1.00))
        self.recWeights = 0.00
        return newCpReqs

    def storeCp(self):

	print "storing cp"
        for ickpt,ckp in enumerate(self.cp):
            with open(str(ickpt)+".checkpoint","wb") as fp:
                fp.write(ckpt)

      

    def _handleCpRequest(self, cpReq):

        self.cpAlert = True

        cpRqWeight = cpReq.weight

        newCpReqs = []

        newDeps = [x for x in self.dependency
                   if x not in cpReq.dependency and x!=self.procId]

        myWeight = cpRqWeight/(len(newDeps)+1)

        for nrecs in newDeps:
            newCpReqs.append(
                CheckpointReqMessage(
                    self.procId,
                    cpReq.initiatorId,
                    nrecs,
                    self._union(self.dependency, cpReq.dependency),
                    myWeight)
                )

        newCpReqs.append(
            CheckpointConfirmMessage(
                self.procId,
                cpReq.initiatorId,
                newDeps,
                myWeight))

        print "Checkpoint message rceived ...."

        return newCpReqs

    def _handleCpConfirmation(self, cpCnf):


        self.recWeights += cpCnf.weight


        if self.recWeights == 1:
            self.storeCp()
            self.recConfirmation.append(cpCnf.sender)
            print "Checkpoint Initiator: All dep processes have taken the checkpoint"

    
    def _updateDependency(self, depProcId):

        if depProcId not in self.dependency:
            self.dependency.append(depProcId)

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
