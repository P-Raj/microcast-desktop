from mpi4py import MPI
from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
import Message
import Datastore
import Queue
import random
import Logging


class JobScheduler:

    def __init__(self, environment):
        self.MAX_BACKLOG = 5
        self.SegmentAssignProcId = 0
        self.environment = environment
        self.segmentHandler = SegmentHandler()
        self.peers = Peers(self.environment.totalProc)
        self.dataHandler = Datastore.Datastore()

    def isSegmentAssigner(self):
        return self.environment.procId == self.SegmentAssignProcId

    def runMicroDownload(self):
        if self.isSegmentAssigner():
            self.microDownload()

    def initLocalQueue(self):
        self.toBeAdvertised = Queue.Queue()
        self.requestQueue = Queue.Queue()
        self.downloadRequests = Queue.Queue()

    def handleAdvertisementQueue(self):
        if not self.toBeAdvertised.empty():
            adMessage = self.toBeAdvertised.get()
            segmentId = adMessage.messageId
            Logging.logProcessOP(self.environment.procId,
                                 "pop",
                                 self.toBeAdvertised,
                                 adMessage)
            reqMessage = adMessage.getResponse()

            # broadcast
            for _ in range(self.environment.totalProc):
                if _ != self.SegmentAssignProcId:
                    reqMessage.receiver = _
                    self.environment.send(_, reqMessage)

    def handleDownloadRequestQueue(self):
        if not self.downloadRequests.empty():
            dwnldReqMessage = self.downloadRequests.get()
            dwnldReqMessage.download()
            Logging.logProcessOP(self.environment.procId,
                                 "pop",
                                 self.downloadRequests,
                                 dwnldReqMessage)
            self.dataHandler.addSegment(dwnldReqMessage.messageId,
                                        dwnldReqMessage.content)
            self.dataHandler.store(dwnldReqMessage)
            self.toBeAdvertised.put(dwnldReqMessage)
            # get response and send it to the inititor

    def handleRequestQueue(self):
        if not self.requestQueue.empty():
            reqMessage = self.requestQueue.get()
            responseMsg = reqMessage.getResponse()
            Logging.logProcessOP(self.environment.procId,
                                 "pop",
                                 self.requestQueue,
                                 reqMessage)
            self.environment.send(responseMsg.receiver, responseMsg)

    def runMicroNC(self):
        if self.environment.procId != self.SegmentAssignProcId:
            self.microNC()

    def stopMicroNC(self):

        if self.toBeAdvertised.empty() and self.requestQueue.empty() and \
           self.downloadRequests.empty() and \
           self.dataHandler.downlodedAll(4):
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
                        Logging.logProcessOp(processId=self.environment.procId,
                                             op="push",
                                             depQueue=self.downloadRequests,
                                             _message=_message)
                        self.downloadRequests.put(_message)

                    if isinstance(_message, Message.AdvertisementMessage):
                        # request the sender for the segments
                        if not self.dataHandler.getSegment(_message.messageId):
                            _response = _message.getResponse()
                            Logging.logChannelOp(_message.sender,
                                                 _message.receiver,
                                                 'send',
                                                 _response)
                            self.environment.send(_response.receiver,
                                                  _response)

                    if isinstance(_message, Message.RequestMessage):
                        # add this to the request queue
                        Logging.logProcessOp(processId=self.environment.procId,
                                             op="push",
                                             depQueue=self.requestQueue,
                                             _message=_message)
                        self.requestQueue.put(_message)

                    if isinstance(_message, Message.SegmentMessage):
                        Logging.logProcessOp(processId=self.environment.procId,
                                             op="receivedSegments")
                        self.dataHandler.addSegment(_message.messageId,
                                                    _message.content)
                        self.dataHandler.store(_message)

            elif nonDetchoice == 1:
                self.handleRequestQueue()

            elif nonDetchoice == 2:
                self.handleDownloadRequestQueue()

            else:
                self.handleAdvertisementQueue()

    def microDownload(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroNC")

        self.segmentHandler.downloadMetadata()
        self.peers.initPeers(self.environment.totalProc)

        while not self.segmentHandler.allAssigned():

            peerId = self.peers.leastBusyPeer()
            peerBackLog = self.peers.getBackLog(peerId)
            feedback = None

            if peerBackLog < self.MAX_BACKLOG:

                requestSegmentId = self.segmentHandler.getNextUnassigned()
                requestSegment = Message.DownloadRequestMessage(
                    self.SegmentAssignProcId,
                    requestSegmentId,
                    peerId)
                requestSegment.initMessage(
                    msgProperty=None,
                    msgContent=self.segmentHandler.getMetadata(
                        requestSegmentId))
                self.segmentHandler.assignSegment(requestSegmentId)
                self.peers.addBackLog(peerId)
                Logging.info("Done sending")
                feedback = self.environment.nonBlockingReceive()

            else:
                Logging.info("Waiting for feedback")
                feedback = self.environment.blockingReceive()

        if feedback:
            self.peers.removeBackLog(peerId, feedback.messageId)

            if not feedback.status:

                self.segmentHandler.unassignSegment(requestSegmentId)
                requestSegmentId = self.segmentHandler.getNextUnassigned()

                requestSegment = RequestMessage(self.SegmentAssignProcId,
                                                requestSegmentId)
                requestSegment.initMessage(
                    msgProperty=None,
                    msgContent=self.segmentHandler.getMetadata(
                        requestSegmentId))

                self.environment.send(feedback.fromId, requestSegment)
                self.segmentHandler.assignSegment(requestSegmentId)
