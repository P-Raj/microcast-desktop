import pickle
from datetime import datetime
import time
import sys
import urllib
import json
from colorama import *

class Datastore:

    def __init__(self, filename, meta):
        self.downloadedSegments = {}
        self.filename = filename
        self.bufferSize =  10 #number of segments downloaded before storing
        self.buffer = []
        self.meta = meta
        self.createFile()

    def createFile(self):
        with open(self.filename,"w") as fp:
            fp.write("X"*self.meta["size"])


    def store(self, forceStore=False):

        if len(self.buffer) == self.bufferSize or forceStore:
            for msg in self.buffer:
                startFrom = self.meta[str(msg[0])]["segmentFrom"]
                with open(self.filename,"r+b") as fp:
                    fp.seek(startFrom)
                    fp.write(msg[1])
            self.buffer = []
            # emptying the buffer

    def get(self):
        return picle.load(self.file)

    def addSegment(self, segmentId, segmentProperty):
        self.downloadedSegments[segmentId] = None
        self.buffer.append((segmentId,segmentProperty))
        self.printProgress()

    def getProgressBar(self):
        pBar = ''
        for i in range(0,int(self.meta["numSegments"]),int(self.meta["numSegments"])/100):
            if i in self.downloadedSegments:
                pBar = pBar + Fore.GREEN + '#'
            else:
                pBar = pBar + Fore.RED + '#'
        return pBar	


    def printProgress(self):
        percent = len(self.downloadedSegments.keys())/ float(self.meta["numSegments"])
        sys.stdout.write("\r" + Fore.BLUE + "%0.2f Complete | %s" % (percent*100,str(self.getProgressBar())))
        sys.stdout.flush()
        sys.stdout.write(Fore.RESET+Back.RESET+Style.RESET_ALL)
        sys.stdout.flush()
        
    def __str__(self):
        pcDwnld = float(len(self.downloadedSegments.keys()))
        return str(1)

    def getSegment(self, segmentId):
        self.downloadedSegments.get(segmentId, None)

    def downlodedAll(self):
        #print self.downloadedSegments.keys()
        for x in range(self.meta["numSegments"]):
            if x not in self.downloadedSegments.keys():
                return False
        return True
        #return all([self.getSegment(x) for x in range(numSegments)])
