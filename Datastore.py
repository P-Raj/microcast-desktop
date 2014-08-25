import pickle
from datetime import datetime

class Datastore:

	def __init__(self, name , mode='w'):
		self.downloadedSegments = {}
		self.file = open(name, mode)

	def __init__(self):
		self.downloadedSegments = {}
		self.file = None#open("temp.txt", 'w')

	def store(self, message):
		_dumpMsg = {'data': message, 'log time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		#pickle.dump(_dumpMsg, self.file)

	def get(self):
		return picle.load(self.file)

	def addSegment(self, segmentId , segmentProperty):
		self.downloadedSegments[segmentId] = segmentProperty
	
	def __str__(self):
		return str(sorted(self.downloadedSegments.keys()))
		l = ['-']*max(self.downloadedSegments.keys())
		for j in self.downloadedSegments.keys():
			l[j-1] = 'X'
		return str(l)

	def getSegment(self, segmentId):
		self.downloadedSegments.get(segmentId,None)

	def downlodedAll(self, numSegments):
		#print self.downloadedSegments.keys()
		for x in range(numSegments):
			if x not in self.downloadedSegments.keys():
				return False
		return True	
		#return all([self.getSegment(x) for x in range(numSegments)])
