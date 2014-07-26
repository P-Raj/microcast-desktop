import Peers
import SegmentHandler as Segments

MAX_BACKLOG = 5

def microDownload():

	while not Segments.allAssigned():

	    peerId = Peers.leastBusyPeer()

	    peerBackLog = Peers.getBackLog(peerId)

	    if peerBackLog < MAX_BACKLOG:
	        requestSegment = Segments.getNextUnassigned()
	        Connection.sendDownloadRequest(peerId, requestSegment)
	        Segments.assignSegment(feedback["segment"]["id"])
	        Peers.addBackLog(peerId, requestSegment)

	    else:
	        feedback = Connection.waitForFeedback()

	    Peers.removeBackLog(peerId, feedback["segment"])

	    if feedback["Status"] == "Failure":
	        requestSegment = Segments.getNextUnassigned()
	        Connection.sendDownloadRequest(feedback["from"], requestSegment)
	        Segments.assignSegment(feedback["segment"]["id"])
