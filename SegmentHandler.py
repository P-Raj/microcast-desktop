# contains information about the segments
# to be used only by the MicroDownload.py

import time
import random




""" self.metadata fields
~~~~~~~~~~~~~~~~~~~~~~
{
	numSegments :  N,
	1 : {
			segmentDownloadtime: K0, 
			segmentFrom : K1, 
			segmentTo : K2
		}
	.......
}
"""
class SegmentHandler:

	def __init__(self):
		self.metadata = None
		self.segmentAssignList = []

	def downloadMetadata(self, url=None):
	    # Static data as of now
	    self.metadata =  { "numSegments" : 4}
	    for i in range(4):
	    	self.metadata[i] = {"segmentDownloadtime" : 2,
	    				"segmentFrom" : 10*i,
	    				"segmentTo" : 10*(i+1)}
	    	self.segmentAssignList.append(False)

	def downloadSegment(self, segmentId):
		time.sleep(self.metadata[segmentId])

	def allAssigned(self):
		return all(self.segmentAssignList)

	def assignSegment(self, segmentId):
		self.segmentAssignList[segmentId] = True

	def getNextUnassigned(self):
		if not allAssigned():
			return random.choice(
				[i for i,x in enumerate(self.segmentAssignList) if not x]
				)
		return -1
