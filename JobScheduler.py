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


class JobScheduler:

    def __init__(self, environment):

        self.MAX_BACKLOG = 5
        self.environment = environment
        self.SegmentAssignProcId = self.environment.totalProcs - 1
        self.segmentHandler = SegmentHandler()
        self.peers = Peers(self.environment.totalProcs)
        self.dataHandler = Datastore.Datastore()
        self.memoryFile = "memory" + str(self.environment.getMyId()) + ".dump"
        open(self.memoryFile, "w").close()

        self.isDownloading = False
        self.downloadingSegment = None
        self.dwnldStartTime = None
        self.dwnldLag = 0

        self.video_url = "http://127.1.1:8888/"
        self.video_name = "music.mp4"


    def dumpMemory(self):
        out = subprocess.Popen(['ps', 'v', '-p', str(os.getpid())],
                               stdout=subprocess.PIPE
                               ).communicate()[0].split(b'\n')
        vsz_index = out[0].split().index(b'RSS')
        mem = float(out[1].split()[vsz_index]) / 1024
        with open(self.memoryFile, "a") as fp:
            fp.write(str(mem) + "\n")

    def isSegmentAssigner(self):

        return self.environment.procId == self.SegmentAssignProcId

    def initLocalQueue(self):

        self.toBeAdvertised = Queue.Queue()
        self.requestQueue = Queue.Queue()
        self.downloadRequests = Queue.Queue()

    def handleAdvertisementQueue(self):

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

    def download(self, segment):
        self.isDownloading = True
        self.dwnldStartTime = datetime.now()
        threading.Thread(target=download, args=[segment])
        
        Logging.logProcessOp(processId=self.environment.procId,
                             op="startDownloading",
                             depQueue="",
                             message=segment)


        dataSeg = urllib.urlopen(self.video_url+"/request=True&file=music.mp4&start=0").read()
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

        
    def handleDownloadRequestQueue(self):

        segment = self.downloadRequests.get()

        Logging.logProcessOp(processId=self.environment.procId,
                             op="pop",
                             depQueue="DwnReqQ",
                             message=segment)

        downloadThread = threading.Thread(target=download, args =[segment])
        downloadThread.start()


        
    def handleRequestQueue(self):
        if not self.requestQueue.empty():
            reqMessage = self.requestQueue.get()
            responseMsg = reqMessage.getResponse()
            Logging.logProcessOp(processId=self.environment.procId,
                                 op="pop",
                                 depQueue="ReqQ",
                                 message=reqMessage)
            self.environment.send(responseMsg.receiver, responseMsg)

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

    def runMicroNC(self):
        self.microNC()

    def stopMicroNC(self):

        if self.toBeAdvertised.empty() and self.requestQueue.empty() and \
           self.downloadRequests.empty() and \
           self.dataHandler.downlodedAll():
            return True

        return False

    def microNC(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroNC")

        self.initLocalQueue()

        while True:

            self.dumpMemory()

            if float(str(self.dataHandler)) == 100:
                completionMsg = Message.DownloadCompleteMessage(
                    senderId=self.environment.procId,
                    receiverId=self.SegmentAssignProcId)
                self.environment.send(self.SegmentAssignProcId,
                    completionMsg)


            nonDetchoice = random.randrange(4)

            if nonDetchoice == 0:

                _message = self.environment.nonBlockingReceive()

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

            elif nonDetchoice == 1:
                self.handleRequestQueue()

            elif nonDetchoice == 2:
                self.handleDownloadRequestQueue()

            else:
                self.handleAdvertisementQueue()

    def runMicroDownload(self):
        self.microDownload()

    def handleRequestResponseMessage(self, _message):

        self.peers.removeBackLog(_message.sender)

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

        self.peers.addBackLog(peerId)

        Logging.logChannelOp(chanFrom=self.SegmentAssignProcId,
                             chanTo=peerId,
                             op="send",
                             message=requestSegment)

    def microDownload(self):

        Logging.logProcessOp(processId=self.environment.procId,
                             op="startMicroDownload")

        assert(self.environment.procId == self.SegmentAssignProcId)

        self.segmentHandler.downloadMetadata(self.video_url, self.video_name)
        self.peers.initPeers(self.environment.totalProcs - 1)

        while not self.segmentHandler.allAssigned():

            nonDetChoice = random.randrange(2)
            self.dumpMemory()

            if nonDetChoice == 0:

                _message = self.environment.nonBlockingReceive()

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

            else:

                peerId = self.peers.leastBusyPeer()
                peerBackLog = self.peers.getBackLog(peerId)

                if peerBackLog < self.MAX_BACKLOG:

                    self.sendDownloadRequest(peerId)
