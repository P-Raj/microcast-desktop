import random
peers = None


def initPeers(numPeers):
	#initializes peers
	peers = dict([(peerId, []) for peerId in range(numPeers)])

def getAPeer():
	return random.choice(peers.keys())


def leastBusyPeer():
	return min(peers, key=peers.get)

def getBackLog(peerId):
	return peers[peerId]

def addBackLog(peerId):
	peers[peerId] += 1

def removeBackLog(peer):
	peers[peerId] -= 1
