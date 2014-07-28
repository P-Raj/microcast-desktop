import random

class Peers:

	def __init__(self):
		self.peers = None

	def initPeers(self, numPeers):
		#initializes self.peers
		self.peers = dict([(peerId, []) for peerId in range(numPeers)])

	def getAPeer(self):
		return random.choice(self.peers.keys())

	def leastBusyPeer(self):
		return min(self.peers, key=self.peers.get)

	def getBackLog(self, peerId):
		return self.peers[peerId]

	def addBackLog(self, peerId):
		self.peers[peerId] += 1

	def removeBackLog(self, peer):
		self.peers[peerId] -= 1
