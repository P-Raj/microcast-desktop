import pickle
from datetime import datetime
import time
import sys


class Datastore:

    def __init__(self):
        self.downloadedSegments = {}
        #self.file = open(name, mode)

    def store(self, message):
        _dumpMsg = {'data': message,
                    'log time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        #pickle.dump(_dumpMsg, self.file)

    def get(self):
        return picle.load(self.file)

    def addSegment(self, segmentId, segmentProperty):
        self.downloadedSegments[segmentId] = segmentProperty
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
