import pickle
from datetime import datetime
import time
import sys


class Datastore:

    def __init__(self):
        self.downloadedSegments = {}
        self.file = open("DataFile","w")
        self.bufferSize =  10 #number of segments downloaded before storing
        self.buffer = []
        #self.file = open(name, mode)

    def store(self, forceStore=False):

        if len(self.buffer) == self.bufferSize or forceStore:
            for msg in self.buffer:
                _dumpMsg = {'id': msg[0],
                            'content': msg[1],
                            'log time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                pickle.dump(_dumpMsg, self.file)
            self.buffer = []
            # emptying the buffer

    def get(self):
        return picle.load(self.file)

    def addSegment(self, segmentId, segmentProperty):
        self.downloadedSegments[segmentId] = None
        self.buffer.append((segmentId,segmentProperty))
        self.printProgress()

    def printProgress(self):

        sys.stdout.write("\r%d Segments Downloaded" % len(self.downloadedSegments.keys()))
        sys.stdout.flush()

    def __str__(self):
        pcDwnld = float(len(self.downloadedSegments.keys()))
        return str(1)

    def getSegment(self, segmentId):
        self.downloadedSegments.get(segmentId, None)

    def downlodedAll(self):
        #print self.downloadedSegments.keys()
        for x in range(self.totalSegs):
            if x not in self.downloadedSegments.keys():
                return False
        return True
        #return all([self.getSegment(x) for x in range(numSegments)])
