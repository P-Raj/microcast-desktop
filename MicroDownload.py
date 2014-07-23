import Peers
import Segments

MAX_BACKLOG = 5

while not Segments.allAssigned():

	peer = Peers.leastBusyPeer()

	peerBackLog = Peers.getBackLog(peer)

	if peerBackLog < MAX_BACKLOG:
		requestSegment = Segments.getNext()
		Connection.sendDownloadRequest(peer, requestSegment)
		Peers.addBackLog(peer, requestSegment)
	
	else:
		feedback = Connection.waitForFeedback()

	Peers.removeBackLog(peer, feedback["segment"])

	if feedback["Status"] == "Failure":
		requestSegment = Segments.getNext()
		Connection.sendDownloadRequest(feedback["from"], requestSegment)
		Segments.add(feedback["segment"])
