import random
peers = None


def initPeers(numPeers):
	#initializes peers
	global peers
	peers = dict([(peerId, []) for peerId in range(numPeers)])

def getAPeer():
	global peers
	return random.choice(peers.keys())

def leastBusyPeer():
	global peers
	return min(peers, key=peers.get)

def getBackLog(peerId):
	global peers
	return peers[peerId]

def addBackLog(peerId):
	global peers
	peers[peerId] += 1

def removeBackLog(peer):
	global peers
	peers[peerId] -= 1
