
import Peers

toBeAdvertised = []

def microNC():

	while True:

	    message = Connection.receive()

	    if message.isSegment():
	        if message.requestedByMe():
	            # Send segment to a neighbor
	            peer = Peers.getAPeer()
	            Connection.sendSegment(peer, message)
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
