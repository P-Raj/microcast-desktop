from time import gmtime, strftime, sleep


#TODO : get the segmentmessage right

class Message(object):

    numMsg = 0

    def __init__(self, senderId, messageId, receiverId):
        self.sender = senderId
        self.receiver = receiverId
        self.messageId = messageId
        self.createdTime = self.getCurrentTime()
        self.property = None
        self.content = None
        self.num = Message.numMsg
        Message.numMsg += 1

    def getBB(self):
        return self.bb

    def setBB(self, bb):
        self.bb = bb

    def getCurrentTime(self):
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def initMessage(self, msgProperty, msgContent):
        self.property = msgProperty
        self.content = msgContent

    def isPacket(self):
        return self.property["type"] == "Packet"

    def isSegment(self):
        return False

    def isAdvertisement(self):
        return False

    def isRequest(self):
        return False

    def isDimensionOfSegment(self):
        return False


class AdvertisementMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def isAdvertisement(self):
        return True

    def getResponse(self):
        _adResponse = RequestMessage(self.receiver,
                                     self.messageId,
                                     self.sender)
        return _adResponse

    def __str__(self):
        return "AdMsg" + str((self.messageId))


class RequestMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def isRequest(self):
        return True

    def getResponse(self, metadata):
        _response = SegmentMessage(self.receiver,
                                   self.messageId,
                                   self.sender)
        with open(metadata["filename"], "rb") as fp:
            fp.seek(metadata[str(self.messageId)]["segmentFrom"])
            _response.content = fp.read(metadata["0"]["segmentFrom"])
        return _response

    def __str__(self):
        return "ReqMsg" + str((self.messageId))


class DownloadRequestMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def download(self):
        sleep(self.content['segmentDownloadtime'])

    def getResponse(self):
        # is an advertisement
        _responseAd = AdvertisementMessage(self.receiver,
                                           self.messageId,
                                           None)
        return _responseAd

    def __str__(self):
        return "DwnReqMsg" + str((self.messageId))


class RequestResponseMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        # messageId is the messageId of the Request message
        Message.__init__(self, senderId, messageId, receiverId)
        self.status = True

    def setStatus(self, status):
        self.status = status
        # True if the Request was successful
        # False otherwise

    def isRequestResponse(self):
        return True

    def __str__(self):
        return "ReqResMsg" + str((self.messageId))


class SegmentMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def __str__(self):
        return "SegMsg" + str((self.messageId))

class DownloadCompleteMessage(Message):

    def __init__(self, senderId, receiverId):
        Message.__init__(self, senderId, None, receiverId)

    def __str__(self):
        return "DwnldCmpMsg" + str(senderId) 

class TerminateMessage(Message):

    def __init__(self, senderId, receiverId):
        Message.__init__(self, senderId, None, receiverId)

    def __str__(self):
        return "MicroCastCompleteMsg"


class CheckpointMessage(Message):

    def __init__(self, senderId, initiatorId, receiverId , weight):
        Message.__init__(self, senderId, initiatorId, receiverId)
        self.initiatorId = initiatorId
        self.weight = weight


class CheckpointReqMessage(CheckpointMessage):

    def __init__(self, senderId, initiatorId, receiverId, depVector, weight):
        CheckpointMessage.__init__(self, senderId, initiatorId, receiverId, weight)
        self.dependency = depVector

    def __str__(self):
        return "CkptReqMsg" + str((self.initiatorId))


class CheckpointConfirmMessage(CheckpointMessage):

    def __init__(self, senderId, receiverId, reqSentTo, weight):
        CheckpointMessage.__init__(self, senderId, None, receiverId, weight)
        self.reqSentTo = reqSentTo

    def __str__(self):
        return "CkptCnfMsg" + str(self.sender)
