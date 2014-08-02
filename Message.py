from time import gmtime, strftime, sleep


class Message(object):

    def __init__(self, senderId, messageId, receiverId):
        self.sender = senderId
        self.receiver = receiverId
        self.messageId = messageId
        self.createdTime = self.getCurrentTime()
        self.property = None
        self.content = None

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


class RequestResponseMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        # messageId is the messageId of the Request message
        Message.__init__(self, senderId, messageId, receiverId)

    def setStatus(self, status):
        self.status = status
        # True if the Request was successful
        # False otherwise

    def isRequestResponse(self):
        return True


class SegmentMessage(Message):

    def __init__(self, senderId, messageId, receiverId):
        Message.__init__(self, senderId, messageId, receiverId)
