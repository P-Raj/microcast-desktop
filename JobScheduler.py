from mpi4py import MPI
from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
from Message import *
import Datastore
import Queue


class JobScheduler:

    MAX_BACKLOG = 5
    SegmentAssignProcId = 0

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
        if not self.toBeAdvertised.Empty():
            adMessage = self.toBeAdvertised.get()
            segmentId = adMessage.messageId
            if not self.dataHandler.getSegment():
                reqMessage = adMessage.getResponse()
                self.environment.send(adMessage.sender, reqMessage)

    def handleDownloadRequestQueue(self):
        if not self.downloadRequests.Empty():
            dwnldReqMessage = self.downloadRequests.get()
            dwnldReqMessage.download()
            self.dataHandler.addSegment(dwnldReqMessage.messageId, dwnldReqMessage.content)
            self.toBeAdvertised.put(dwnldReqMessage)
            # get response and send it to the inititor

    def handleRequestQueue(self):
        if not self.requestQueue.Empty():
            reqMessage = self.requestQueue.get()
            responseMsg = reqMessage.getResponse()
            self.environment.send(responseMsg.receiver, responseMsg)

    def microNC(self):
        print "microNC initiated by process ", self.environment.procId

        self.initLocalQueue()
        
        while True:

            nonDetchoice = random.randrange(4)

            if nonDetchoice == 0:

                _message = self.environment.nonblockingReceive()

                if _message:

                    if isinstance(_message, DownloadRequestMessage):
                        self.downloadRequests.put(_message)

                    if isinstance(_message, AdvertisementMessage):
                        # request the sender for the segments
                        if not self.getSegment(_message.messageId):
                            _response = _message.getResponse()
                            self.environment.send(_response.receiver, _response)

                    if isinstance(_message, RequestMessage):
                        # add this to the request queue
                        self.requestQueue.put(_message)

                    if isinstance(_message, SegmentMessage):
                        self.dataHandler.addSegment(_message.messageId,_message.content)


            elif nonDetchoice == 1:
                handleRequestQueue()

            elif nonDetchoice == 2:
                handleDownloadRequestQueue()

            else:
                handleAdvertisementQueue()

    def microDownload(self):

        print "microDownload initiated by process ", self.environment.procId
        self.segmentHandler.downloadMetadata()
        self.peers.initPeers(self.environment.totalProc)

        while not self.segmentHandler.allAssigned():

            peerId = self.peers.leastBusyPeer()
            peerBackLog = self.peers.getBackLog(peerId)

            if peerBackLog < self.MAX_BACKLOG:

                requestSegmentId = self.segmentHandler.getNextUnassigned()
                requestSegment = RequestMessage(SegmentAssignProcId, requestSegmentId)
                requestSegment.initMessage(msgProperty=None, 
                    msgContent=self.segmentHandler.getMetadata(requestSegmentId))


                self.environment.send(peerId, requestSegment)
                
                self.segmentHandler.assignSegment(requestSegmentId)
                self.peers.addBackLog(peerId, requestSegmentId)

            else:
                feedback = self.environment.blockingReceive()

            self.peers.removeBackLog(peerId, feedback.messageId)

            if not feedback.status:
                
                self.segmentHandler.unassignSegment(requestSegmentId)

                requestSegmentId = self.segmentHandler.getNextUnassigned()
                
                requestSegment = RequestMessage(SegmentAssignProcId, requestSegmentId)
                requestSegment.initMessage(msgProperty=None, 
                    msgContent=self.segmentHandler.getMetadata(requestSegmentId))

                self.environment.send(feedback.fromId, requestSegment)
                self.segmentHandler.assignSegment(requestSegmentId)
