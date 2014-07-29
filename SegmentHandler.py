# contains information about the segments
# to be used only by the MicroDownload.py

import random
import urllib
import json
import threading

class SegmentHandler:

    def __init__(self):
        self.metadata = None
        self.segmentAssignList = []
        self.segmentAssignListLock = threading.Lock()
        self.downloadedList = []

    def downloadMetadata(self, url, videoName):
        # Static data as of now
        url = url + urllib.urlencode({'init': 'True', 'file': videoName})
        print "Downloading metadata from : ", url
        meta = json.loads(urllib.urlopen(url).read())

        self.metadata = dict((
            ("numSegments", len(meta["Segments"])),
            ("size", meta["size"]),
            ("filename", videoName))
        )

        self.numSegs = self.metadata["numSegments"]

        self.segmentAssignList = [False] * self.numSegs
        self.downloadedList = [False] * self.numSegs

        for x in meta["Segments"]:
            self.metadata[str(x)] = {"segmentFrom":meta["Segments"][x]}

    def getMetadata(self, segmentId):
        return self.metadata[str(segmentId)]

    def allAssigned(self):
        self.segmentAssignListLock.acquire()
        op = all(self.segmentAssignList)
        self.segmentAssignListLock.release()
        return op

    def allDownloaded(self):
        return all(self.downloadedList)

    def isDownloaded(self, segmentId):
        self.downloadedList[segmentId] = True

    def assignSegment(self, segmentId):
        self.segmentAssignListLock.acquire()
        self.segmentAssignList[segmentId] = True
        self.segmentAssignListLock.release()

    def unassignSegment(self, segmentId):
        self.segmentAssignListLock.acquire()
        self.segmentAssignList[segmentId] = False
        self.segmentAssignListLock.release()
        
    def getNextUnassigned(self):
        # used only by microDownload
        if not self.allAssigned():
            for i,x in enumerate(self.segmentAssignList):
                if not x:
                    return i
            #return random.choice(
            #    [i for i, x in enumerate(self.segmentAssignList) if not x])
        return None
