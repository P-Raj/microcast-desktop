from mpi4py import MPI
from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
from Message import RequestMessage

class JobScheduler:

    def __init__(self, environment):

        MAX_BACKLOG = 5
        SegmentAssignProcId = 0
        
        self.environment = environment
        self.segmentHandler = SegmentHandler()
        self.peers = self.peers()

    def isSegmentAssigner(self):
    	
        return self.environment.procId == SegmentAssignProcId

    def runMicroDownload(self):
	if self.isSegmentAssigner():
		self.microDownload()

    def runMicroNC(self):
	MN.microNC()

    def microDownload(self):


        self.segmentHandler.downloadMetadata()
        self.peers.initself.peers(self.environment.Get_size())

        while not self.segmentHandler.allAssigned():

            peerId = self.peers.leastBusyPeer()
            peerBackLog = self.peers.getBackLog(peerId)

            if peerBackLog < MAX_BACKLOG:

                requestSegmentId = self.segmentHandler.getNextUnassigned()
                requestSegment = RequestMessage(SegmentAssignProcId, requestSegmentId)
                requestSegment.initMessage(msgProperty=None, 
                    msgContent=self.segmentHandler.getMetadata(requestSegmentId))

                Connection.sendDownloadRequest(peerId, requestSegment)
                
                self.segmentHandler.assignSegment(feedback["segment"]["id"])
                self.peers.addBackLog(peerId, requestSegment)

            else:
                feedback = Connection.waitForFeedback()

            self.peers.removeBackLog(peerId, feedback["segment"])

            if feedback["Status"] == "Failure":
                requestSegment = self.segmentHandler.getNextUnassigned()
                Connection.sendDownloadRequest(feedback["from"], requestSegment)
                self.segmentHandler.assignSegment(feedback["segment"]["id"])
