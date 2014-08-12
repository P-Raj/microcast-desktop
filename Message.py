from time import gmtime, strftime, sleep


class Message(object):

    def __init__(self, senderId, messageId, receiverId):
        self.sender = senderId
        self.receiver = receiverId
        self.messageId = messageId
        self.createdTime = self.getCurrentTime()
        self.property = None
        self.content = None

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
	return "AdvtsMsg" + str([self.messageId])


class RequestMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def isRequest(self):
        return True

    def getResponse(self):
        _response = SegmentMessage(self.receiver,
                                   self.messageId,
                                   self.sender)
        return _response

    def __str__(self):
	return "ReqMsg" + str([self.messageId])


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
	return "DwnldReqMsg" + str([self.messageId])


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
	return "ReqResponseMsg" + str([self.messageId])


class SegmentMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)

    def __str__(self):
	return "SegmentMsg" + str([self.messageId])

class CheckpointMessage(Message):

	def __init__(self, senderId, initiatorId, receiverId):
		Message.__init__(self, senderId, initiatorId, receiverId)
		self.initiatorId = initiatorId

	def __str__(self):
		return "CheckpointMsg" + str(self.initiatorId)
