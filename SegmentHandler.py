# contains information about the segments
# to be used only by the MicroDownload.py

import time
import random

metadata = None
segmentAssignList = []


""" metadata fields
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


def downloadMetadata(url=None):
    # Static data as of now
    global metadata, segmentAssignList
    metadata =  { "numSegments" : 4}
    for i in range(4):
    	metadata[i] = {"segmentDownloadtime" : 2,
    				"segmentFrom" : 10*i,
    				"segmentTo" : 10*(i+1)}
    	segmentAssignList.append(False)

def downloadSegment(segmentId):
	global metadata
	time.sleep(metadata[segmentId])

def allAssigned():
	global segmentAssignList
	return all(segmentAssignList)

def assignSegment(segmentId):
	global segmentAssignList
	segmentAssignList[segmentId] = True

def getNextUnassigned():
	global segmentAssignList
	if not allAssigned():
		return random.choice(
			[i for i,x in enumerate(segmentAssignList) if not x]
			)
	return -1
