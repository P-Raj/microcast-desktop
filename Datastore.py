import pickle
from datetime import datetime

class Datastore:

	def __init__(self, totalSegs):
		self.downloadedSegments = {}
		self.totalSegs = totalSegs
		#self.file = open(name, mode)

	def store(self, message):
		_dumpMsg = {'data': message, 'log time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		#pickle.dump(_dumpMsg, self.file)

	def get(self):
		return picle.load(self.file)

	def addSegment(self, segmentId , segmentProperty):
		self.downloadedSegments[segmentId] = segmentProperty
	
	def __str__(self):
		return str(float(len(self.downloadedSegments.keys()))/self.totalSegs * 100)

	def getSegment(self, segmentId):
		self.downloadedSegments.get(segmentId,None)

	def downlodedAll(self):
		#print self.downloadedSegments.keys()
		for x in range(self.totalSegs):
			if x not in self.downloadedSegments.keys():
				return False
		return True	
		#return all([self.getSegment(x) for x in range(numSegments)])
