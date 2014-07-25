
import Peers

toBeAdvertised = []

def microNC():

	while True:

	    message = Connection.receive()

	    if message.isSegment():
	        if message.requestedByMe():
	            # Send segment to a neighbor
	            peerId = Peers.getAPeer()
	            Connection.sendSegment(peerId, message)
	        toBeAdvertised.append(message)

	    if message.isPacket():
	        recceivedFrom = message.sender

	        if message.isAdvertisement():
	            # Request sender for the segment
	            Connection.requestSegment(message)

	        elif message.isRequest():
	            requestQueue.append(message)

	        elif message.isDimensionOfSegment():
	            VM.write(message)
