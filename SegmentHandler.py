# contains information about the segments
# to be used only by the MicroDownload.py

import random
import urllib
import json


class SegmentHandler:

    def __init__(self):
        self.metadata = None
        self.segmentAssignList = []
        self.downloadedList = []

    def downloadMetadata(self, url, videoName):
        # Static data as of now
        url = url + urllib.urlencode({'init': 'True', 'file': videoName})
        print "Downloading metadata from : ", url
        meta = json.loads(urllib.urlopen(url).read())

        self.metadata = dict(
            ("numSegments", len(meta["Segments"])),
            ("size", meta["size"]))

        self.numSegs = self.metadata["numSegments"]

        self.segmentAssignList = [False] * self.numSegs
        self.downloadedList = [False] * self.numSegs

        self.metadata.update(
            dict(
                (str(x), dict(("segmentFrom", meta["Segments"][x])))
                for x in meta["segments"]))

    def getMetadata(self, segmentId):
        return self.metadata[str(segmentId)]

    def allAssigned(self):
        return all(self.segmentAssignList)

    def allDownloaded(self):
        return all(self.downloadedList)

    def isDownloaded(self, segmentId):
        self.downloadedList[segmentId] = True

    def assignSegment(self, segmentId):
        self.segmentAssignList[segmentId] = True

    def unassignSegment(self, segmentId):
        self.segmentAssignList[segmentId] = False

    def getNextUnassigned(self):
        # used only by microDownload
        if not self.allAssigned():
            return random.choice(
                [i for i, x in enumerate(self.segmentAssignList) if not x])
        return -1
