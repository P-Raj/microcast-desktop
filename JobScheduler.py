from Peers import Peers
from SegmentHandler import SegmentHandler
from Communicator import Communicator
import Message
import Datastore
import Queue
import random
import Logging
import time
import LogViewer
import subprocess
import os
from datetime import datetime, timedelta
import threading
import urllib


class JobScheduler:

    def __init__(self, environment):

        self.MAX_BACKLOG = 5

        self.environment = environment

        self.SegmentAssignProcId = self.environment.totalProcs - 1

        self.segmentHandler = SegmentHandler()
        self.peers = Peers(self.environment.totalProcs)
        self.dataHandler = Datastore.Datastore()

        self.isDownloading = False
        self.downloadingSegment = None
        self.dwnldStartTime = None

        self.video_url = "http://192.168.21.20:8888/"
        self.video_name = "music.mp4"

        self.peerLock = threading.Lock()

    def isSegmentAssigner(self):

        return self.environment.procId == self.SegmentAssignProcId

    def initLocalQueue(self):

        self.toBeAdvertised = Queue.Queue()
        self.requestQueue = Queue.Queue()
        self.downloadRequests = Queue.Queue()

    """ <Functions to handle local queues> """

    def handleAdvertisementQueue(self):

        while True:

            if not self.toBeAdvertised.empty():

                adMessage = self.toBeAdvertised.get()
                segmentId = adMessage.messageId
                Logging.logProcessOp(processId=self.environment.procId,
                                     op="pop",
                                     depQueue="AdQ",
                                     message=adMessage)

                # broadcast
                # should change to bcast
                for _ in range(self.environment.totalProcs-1):
                    if _ != self.environment.getMyId():
                        reqMessage = adMessage.getResponse()
                        reqMessage.receiver = _
                        self.environment.send(_, reqMessage)
                        Logging.logChannelOp(self.environment.procId,
                                             _,
                                             "bcast",
                                             reqMessage)

    def handleDownloadRequestQueue(self):

        while True:

            if not self.downloadRequests.empty() and not self.isDownloading:

                segment = self.downloadRequests.get()

                Logging.logProcessOp(processId=self.environment.procId,
                                     op="pop",
                                     depQueue="DwnReqQ",
                                     message=segment)

                downloadThread = threading.Thread(target=self.download,
                                                  args=[segment])
                self.isDownloading = True
                downloadThread.start()

    def handleRequestQueue(self):

        while True:

            if not self.requestQueue.empty():

                    reqMessage = self.requestQueue.get()
                    responseMsg = reqMessage.getResponse()
                    Logging.logProcessOp(processId=self.environment.procId,
                                         op="pop",
                                         depQueue="ReqQ",
                                         message=reqMessage)
                    self.environment.send(responseMsg.receiver, responseMsg)

    """ </Functions to handle local queues> """

    """ Function to handle incoming channel"""

    def handleIncomingChannelMNc(self):

        while True:

            _message = self.environment._receive()

            if _message:

                Logging.logChannelOp(_message.sender,
                                     _message.receiver,
                                     'receive',
                                     _message)

                if isinstance(_message, Message.DownloadRequestMessage):
                    assert(_message.sender == self.SegmentAssignProcId)
                    self.handleDownloadRequestMessage(_message)

                elif isinstance(_message, Message.AdvertisementMessage):
                    self.handleAdvertisementMessage(_message)

                elif isinstance(_message, Message.RequestMessage):
                    self.handleRequestMessage(_message)

                elif isinstance(_message, Message.SegmentMessage):
                    self.handleSegmentMessage(_message)

                elif isinstance(_message, Message.TerminateMessage):
                    break

                else:
                    raise Exception("Undefined message \
                                    found in the channel")

    """ <Functions to handle incoming microDownload Messages> """

    def handleDownloadRequestMessage(self, _message):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="push",
                             depQueue="DwnReqQ",
                             message=_message)
        self.downloadRequests.put(_message)

    def handleAdvertisementMessage(self, _message):

        if not self.dataHandler.getSegment(_message.messageId):
            _response = _message.getResponse()
            Logging.logChannelOp(_message.sender,
                                 _message.receiver,
                                 'send',
                                 _response)
            self.environment.send(_response.receiver,
                                  _response)

    def handleRequestMessage(self, _message):
        Logging.logProcessOp(processId=self.environment.procId,
                             op="push",
                             depQueue="ReQ",
                             message=_message)
        self.requestQueue.put(_message)

    def handleSegmentMessage(self, _message):
        Logging.logProcessOp(processId=self.environment.procId,
                             op="receivedSegments")
        self.dataHandler.addSegment(_message.messageId,
                                    _message.content)
        self.dataHandler.store(_message)

    """ </Functions to handle incoming microNC Messages> """

    def runMicroNC(self):
        self.microNC()

    def isMicroNCComplete(self):

        return (self.toBeAdvertised.empty() and self.requestQueue.empty() and
                self.downloadRequests.empty() and
                self.dataHandler.downlodedAll())

    def detectMicroNCCompetion(self):

        while True:
            if float(str(self.dataHandler)) == 100:
                # all segments have been downloaded
                completionMsg = Message.DownloadCompleteMessage(
                    senderId=self.environment.procId,
                    receiverId=self.SegmentAssignProcId)
                self.environment.send(self.SegmentAssignProcId,
                                      completionMsg)

            if self.isMicroNCComplete():
                time.sleep(20)
                return

    def microNC(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroNC")

        self.initLocalQueue()

        readingReqQ = self.handleRequestQueue
        readingDnldReqQ = self.handleDownloadRequestQueue
        readingAdQ = self.handleAdvertisementQueue

        chanThread = threading.Thread(target=self.handleIncomingChannelMNc)
        chanThread.start()

        reqThread = threading.Thread(target=readingReqQ)
        reqThread.start()

        dnldThread = threading.Thread(target=readingDnldReqQ)
        dnldThread.start()

        adThread = threading.Thread(target=readingAdQ)
        adThread.start()

        chanThread.join()

        termThread = threading.Thread(tarket=self.detectMicroNCCompetion)
        termThread.start()
        termThread.join()

        # TODO: make the following threads non-daemonic
        reqThread.exit()
        dnldThread.exit()
        adThread.exit()

    def runMicroDownload(self):
        self.microDownload()

    def download(self, segment):

        self.dwnldStartTime = datetime.now()

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startDownloading",
                             depQueue="",
                             message=segment)

        #TODO : Change the following line
        segFilename = "music.mp4"
        segStart = 0
        dataSeg = urllib.urlopen(self.video_url +
                                 urllib.urlencode(dict((("request", "True"),
                                                       ("file", segFilename),
                                                       ("start", segStart))))
                                 ).read()
        #datsSeg in memory

        Logging.logProcessOp(processId=self.environment.procId,
                             op="downloadComplete",
                             depQueue="",
                             message=segment)

        self.dataHandler.addSegment(segment.messageId,
                                    dataSeg)

        #self.dataHandler.store(self.downloadingSegment)

        self.isDownloading = False
        self.dwnldStartTime = None

        #push it to the ad Queue
        Logging.logProcessOp(processId=self.environment.procId,
                             op="push",
                             depQueue="AdQ",
                             message=segment)

        self.toBeAdvertised.put(segment)
        #send response to the initiator

        _response = Message.RequestResponseMessage(
            senderId=self.environment.procId,
            messageId=segment.messageId,
            receiverId=self.SegmentAssignProcId)

        self.environment.send(self.SegmentAssignProcId, _response)

        Logging.logChannelOp(self.environment.procId,
                             self.SegmentAssignProcId,
                             "sendConfirmation",
                             _response)

    def downloadingOver(self):
        return not self.isDownloading

    def handleRequestResponseMessage(self, _message):

        self.peerLock.acquire()
        self.peers.removeBackLog(_message.sender)
        self.peerLock.release()

        if not _message.status:

            self.segmentHandler.unassignSegment(
                _message.messageId)

            reqSegId = self.segmentHandler.getNextUnassigned()

            requestSegment = Message.DownloadRequestMessage(
                self.SegmentAssignProcId,
                reqSegId,
                _message.sender)

            requestSegment.initMessage(
                msgProperty=None,
                msgContent=self.segmentHandler.getMetadata(
                    reqSegId))

            self.environment.send(_message.sender,
                                  requestSegment)

            self.segmentHandler.assignSegment(reqSegId)

        else:
            self.segmentHandler.isDownloaded(_message.messageId)

    def sendDownloadRequest(self, peerId):

        requestSegmentId = self.segmentHandler.getNextUnassigned()
        requestSegment = Message.DownloadRequestMessage(
            self.SegmentAssignProcId,
            requestSegmentId,
            peerId)

        requestSegment.initMessage(
            msgProperty=None,
            msgContent=self.segmentHandler.getMetadata(
                requestSegmentId))

        self.environment.send(peerId, requestSegment)

        self.segmentHandler.assignSegment(requestSegmentId)

        self.peerLock.acquire()
        self.peers.addBackLog(peerId)
        self.peerLock.release()

        Logging.logChannelOp(chanFrom=self.SegmentAssignProcId,
                             chanTo=peerId,
                             op="send",
                             message=requestSegment)

    def handleIncomingChannelMD(self):

        while True:

            _message = self.environment._receive()

            if _message:

                if isinstance(_message, Message.RequestResponseMessage):
                    Logging.logChannelOp(_message.sender,
                                         _message.receiver,
                                         "recieve",
                                         _message)
                    self.handleRequestResponseMessage(_message)

                else:
                    raise Exception("microDownload received \
                        undefined message" + str(_message))

                if self.segmentHandler.allDownloaded():

                    for _ in range(self.environment.totalProcs-1):
                        if _ != self.environment.getMyId():
                            terminationMsg = Message.TerminateMessage(self.environment.procId, _)
                            self.environment.send(_, terminationMsg)
                            Logging.logChannelOp(self.environment.procId,
                                                 _,
                                                 "terminateSignal",
                                                 terminationMsg)

    def handleOutgoingChannelMD(self):

        while not self.segmentHandler.allAssigned():

            self.peerLock.acquire()
            peerId = self.peers.leastBusyPeer()
            peerBackLog = self.peers.getBackLog(peerId)
            self.peerLock.release()

            if peerBackLog < self.MAX_BACKLOG:
                self.sendDownloadRequest(peerId)

    def microDownload(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroDownload")

        assert(self.environment.procId == self.SegmentAssignProcId)

        self.segmentHandler.downloadMetadata(self.video_url, self.video_name)
        print "Metadata download complete"

        self.peers.initPeers(self.environment.totalProcs - 1)

        tIn = threading.Thread(target=self.handleIncomingChannelMD)
        tOut = threading.Thread(target=self.handleOutgoingChannelMD)

        tIn.start()
        tOut.start()

        tIn.join()
        tOut.join()
