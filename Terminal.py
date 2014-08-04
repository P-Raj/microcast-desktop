
class Terminal :

	class TColumn:

		tabSize = 10

		def __init__(self, colNum, totalSegs):
			self.segDownloaded = []
			self.toalSegs = totalSegs
			self.activities = []
			self.activityCounter = 0
			self.colNum = colNum
			self.printSegs = True

		def reachedEnd(self):
			return self.activityCounter == len(self.activities)

		def __gt__(self,other):
			if not isinstance(other,TColumn):
				raise Exception("Incomparable")
				sys.exit(1)
			if self.reachedEnd():
				return True
			return self.getTopTimestamp() > other.getTopTimestamp()

		def __lt__(self,other):
			if not instance(other,TColumn):
				raise Exception("Incomparable")
			if self.reachedEnd():
				return False
			return self.getTopTimestamp() < other.getTopTimestamp()

		def getTopTimestamp(self):
			return self.activities[self.activityCounter][1]

		def addSegment(self, segId):
			self.segDownloaded.append(segId)
		
		def __str__(self):
			if self.printSegs:
				return str(self.segDownloaded)
				self.printSegs = False
			else:
				self.activityCounter += 1
				return self.activities[self.activityCounter-1]
		
			

	def __init__(self, numProcs):
		self.numProcs = numProcs

	
