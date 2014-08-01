from time import gmtime, strftime

class Message(object):

    def __init__(self, senderId, messageId, receiverId = None):
        self.sender = senderId
        self.receiver = receiverId
        self.messageId = messageId
        self.createdTime = self.getCurrentTime()

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

class SegmentMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        super(Message,self).__init__(senderId, messageId, receiverId)

    def isSegment(self):
        return True

class AdvertisementMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        super(Message,self).__init__(senderId, messageId, receiverId)

    def isAdvertisement(self):
        return True

    def getResponse(self):
        _adResponse = RequestMessage(self.receiver, self.messageId, self.sender)
        return _adResponse

class RequestMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        super(Message,self).__init__(senderId, messageId, receiverId)

    def isRequest(self):
        return True

    def getResponse(self):
        _response = SegmentMessage(self.receiver, self.messageId, self.sender)
        return response

def DownloadRequestMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        super(Message,self).__init__(senderId, messageId, receiverId)

    def download(self):
        time.sleep(self.content['segmentDownloadtime'])    

class RequestResponseMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        # messageId is the messageId of the Request message
        super(Message,self).__init__(senderId, messageId, receiverId)

    def setStatus(self, status):
        self.status = status
        # True if the Request was successful
        # False otherwise

    def isRequestResponse(self):
        return True

class SegmentMessage(Message):

    def __init__(self, senderId, messageId, receiverId = None):
        super(Message,self).__init__(senderId, messageId, receiverId)

