import History


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

	def getTabSize(self):
		return " " * tabSize * self.colNum

	def update(self):
		self.activities = History.getHistory(self.colNum)

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
			return self.getTabSize() + str(self.segDownloaded)
			self.printSegs = False
		else:
			self.activityCounter += 1
			return self.getTabSize()  + self.activities[self.activityCounter-1]


class Terminal :

	def __init__(self, numProcs, numSegs):
		self.numProcs = numProcs
		self.numSegs = numSegs
		self.columns = []
		self.initColumns()

	def initColumns(self):
		self.columns = [ TColumn(numProc, self.numSegs) for numProc in range(self.numProcs) ]

	def update(self):
		for col in self.columns:
			col.update()

	def show(self):
		nColumn = self.findNextColumn()
		if not nColumn:
			print str(nColumn)
			return True
		return False

	def findNextColumn(self):
		nextCol = self.columns[0]
		for col in self.columns[1:]:
			if col < nextCol:
				nextCol = col

		if nextCol > self.column[0]:
			return None

		return nextCol
