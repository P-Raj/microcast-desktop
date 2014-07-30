from mpi4py import MPI
from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
from Message import AdvertisementMessage, RequestMessage, RequestResponseMessage, DimensionOfMessage
import Datastore

class JobScheduler:

    def __init__(self, environment):

        MAX_BACKLOG = 5
        SegmentAssignProcId = 0
        
        self.environment = environment
        self.segmentHandler = SegmentHandler()
        self.peers = Peers(self.environment.totalProc)

    def isSegmentAssigner(self):
    	
        return self.environment.procId == SegmentAssignProcId

    def runMicroDownload(self):
	if self.isSegmentAssigner():
		self.microDownload()

    def initLocalQueue(self):
        self.toBeAdvertised = Queue.Queue()
        self.requestQueue = Queue.Queue()

    def microNC(self):

        self.initLocalQueue()

        while True:

            _message = self.environment.nonblockingReceive()

            if isinstance(_message, SegmentMessage):
                if _message.procId == self.environment.getMyId():
                    #  The message was requested by the current process
                    self.environment.sendToRandom(_message)
                    # Send the message to one of th eneighbors
                self.toBeAdvertised.add(_message)

            if _message.isPacket():
                receivedFrom = _message.sender

                if isinstance(_message, AdvertisementMessage):
                    
                    # Request sender for the segment
                    _request = RequestMessage(receivedFrom, _message.messageId)
                    _request.initMessage(None, _message.content)

                    self.environment.send(receivedFrom, _request)

                elif isinstance(_message, RequestMessage):
                    self.requestQueue.add(_message)

                elif isinstance(_message, DimensionOfMessage):
                    DataStore.store(_message)


    def microDownload(self):


        self.segmentHandler.downloadMetadata()
        self.peers.initPeers(self.environment.Get_size())

        while not self.segmentHandler.allAssigned():

            peerId = self.peers.leastBusyPeer()
            peerBackLog = self.peers.getBackLog(peerId)

            if peerBackLog < MAX_BACKLOG:

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
