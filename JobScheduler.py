from mpi4py import MPI
from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
import Message
import Datastore
import Queue
import random
import Logging
import time
import LogViewer

class JobScheduler:

    def __init__(self, environment):

        self.MAX_BACKLOG = 5
        self.environment = environment
        self.SegmentAssignProcId = self.environment.totalProc - 1
        self.segmentHandler = SegmentHandler(self.environment.getNumSegs())
        self.peers = Peers(self.environment.totalProc)
        self.dataHandler = Datastore.Datastore()

    def isSegmentAssigner(self):

        return self.environment.procId == self.SegmentAssignProcId

    def initLocalQueue(self):

        self.toBeAdvertised = Queue.Queue()
        self.requestQueue = Queue.Queue()
        self.downloadRequests = Queue.Queue()

    def handleAdvertisementQueue(self):

        if not self.toBeAdvertised.empty():

            adMessage = self.toBeAdvertised.get()
            segmentId = adMessage.messageId
            Logging.logProcessOp(processId=self.environment.procId,
                                 op="pop",
                                 depQueue="AdQ",
                                 message=adMessage)

            # broadcast
            # should change to bcast
            for _ in range(self.environment.totalProc-1):
                if _ != self.environment.getMyId():
                    reqMessage = adMessage.getResponse()
                    reqMessage.receiver = _
                    self.environment.send(_, reqMessage)
                    Logging.logChannelOp(self.environment.procId,
					_,
					"bcast",
					reqMessage)

    def handleDownloadRequestQueue(self):

        if not self.downloadRequests.empty():

            dwnldReqMessage = self.downloadRequests.get()
            dwnldReqMessage.download()
            Logging.logProcessOp(processId=self.environment.procId,
                                 op="pop",
                                 depQueue="DwnReqQ",
                                 message=dwnldReqMessage)
            self.dataHandler.addSegment(dwnldReqMessage.messageId,
                                        dwnldReqMessage.content)
            self.dataHandler.store(dwnldReqMessage)
            print  " "*8*self.environment.procId + str(self.dataHandler) + "\r"

	    Logging.logProcessOp(processId=self.environment.procId,
				op="push",
				depQueue="AdQ",
				message=dwnldReqMessage)
            self.toBeAdvertised.put(dwnldReqMessage)
	    _response = Message.RequestResponseMessage(senderId=self.environment.procId,
					       messageId=dwnldReqMessage.messageId,
					       receiverId=self.SegmentAssignProcId)
	    self.environment.send(self.SegmentAssignProcId, _response)
	    Logging.logChannelOp(self.environment.procId,
				 self.SegmentAssignProcId,
				 "sendConfirmation",
				 _response)
            # get response and send it to the inititor

    def handleRequestQueue(self):
        if not self.requestQueue.empty():
            reqMessage = self.requestQueue.get()
            responseMsg = reqMessage.getResponse()
            Logging.logProcessOp(processId=self.environment.procId,
                                 op="pop",
                                 depQueue="ReqQ",
                                 message=reqMessage)
            self.environment.send(responseMsg.receiver, responseMsg)

    def handleDownloadRequestMessage(self, _message):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="push",
                             depQueue="DwnReqQ",
                             message=_message)
        self.downloadRequests.put(_message)

    def handleAdvertisementMessage(self, _message):

        if not self.dataHandler.getSegment(_message.messageId):
            _response = _message.getResponse()
            Logging.logChannelOp(_message.sender,
                                 _message.receiver,
                                 'send',
                                 _response)
            self.environment.send(_response.receiver,
                                  _response)

    def handleRequestMessage(self, _message):
        Logging.logProcessOp(processId=self.environment.procId,
                             op="push",
                             depQueue="ReQ",
                             message=_message)
        self.requestQueue.put(_message)

    def handleSegmentMessage(self, _message):
        Logging.logProcessOp(processId=self.environment.procId,
                             op="receivedSegments")
        self.dataHandler.addSegment(_message.messageId,
                                    _message.content)
        self.dataHandler.store(_message)
        print  " "*8*self.environment.procId + str(self.dataHandler) + "\r"


    def runMicroNC(self):
        self.microNC()

    def stopMicroNC(self):

        if self.toBeAdvertised.empty() and self.requestQueue.empty() and \
           self.downloadRequests.empty() and \
           self.dataHandler.downlodedAll(self.environment.getNumSegs()):
            return True

        return False

    def microNC(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroNC")

        self.initLocalQueue()

        while not self.stopMicroNC():


            nonDetchoice = random.randrange(4)

            if nonDetchoice == 0:

                _message = self.environment.nonBlockingReceive()

                if _message:
                    Logging.logChannelOp(_message.sender,
                                         _message.receiver,
                                         'receive',
                                         _message)

                    if isinstance(_message, Message.DownloadRequestMessage):
                        self.handleDownloadRequestMessage(_message)

                    elif isinstance(_message, Message.AdvertisementMessage):
                        self.handleAdvertisementMessage(_message)

                    elif isinstance(_message, Message.RequestMessage):
                        self.handleRequestMessage(_message)

                    elif isinstance(_message, Message.SegmentMessage):
                        self.handleSegmentMessage(_message)

                    else:
                        raise Exception("Undefined message found in the channel")



            elif nonDetchoice == 1:
                self.handleRequestQueue()

            elif nonDetchoice == 2:
                self.handleDownloadRequestQueue()

            else:
                self.handleAdvertisementQueue()

    def runMicroDownload(self):
         self.microDownload()

    def handleRequestResponseMessage(self, _message):


        self.peers.removeBackLog(_message.sender)

        if not _message.status:

            self.segmentHandler.unassignSegment(
                _message.messageId)

            reqSegId = self.segmentHandler.getNextUnassigned()

            requestSegment = Message.DownloadRequestMessage(
                    self.SegmentAssignProcId,
                    reqSegId,
                    _message.sender)


            requestSegment.initMessage(
                msgProperty=None,
                msgContent=self.segmentHandler.getMetadata(
                    reqSegId))

            self.environment.send(_message.sender,
                                  requestSegment)

            self.segmentHandler.assignSegment(reqSegId)

    def sendDownloadRequest(self, peerId):

        requestSegmentId = self.segmentHandler.getNextUnassigned()
        requestSegment = Message.DownloadRequestMessage(
            self.SegmentAssignProcId,
            requestSegmentId,
            peerId)

        requestSegment.initMessage(
            msgProperty=None,
            msgContent=self.segmentHandler.getMetadata(
                requestSegmentId))

        self.environment.send(peerId, requestSegment)

        self.segmentHandler.assignSegment(requestSegmentId)

        self.peers.addBackLog(peerId)

        Logging.logChannelOp(chanFrom=self.SegmentAssignProcId,
                             chanTo=peerId,
                             op="send",
                             message=requestSegment)

    def microDownload(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroDownload")

        self.segmentHandler.downloadMetadata()
        self.peers.initPeers(self.environment.totalProc - 1)

        while not self.segmentHandler.allAssigned():

            nonDetChoice = random.randrange(2)

            if nonDetChoice == 0:

                _message = self.environment.nonBlockingReceive()

                if _message:

                    if isinstance(_message, Message.RequestResponseMessage):
                        self.handleRequestResponseMessage(_message)

                    else:
                        raise Exception ("microDownload received undefined message" + str(_message))

            else:

                peerId = self.peers.leastBusyPeer()
                peerBackLog = self.peers.getBackLog(peerId)

                if peerBackLog < self.MAX_BACKLOG:

                    self.sendDownloadRequest(peerId)
