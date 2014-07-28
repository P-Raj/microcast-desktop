from time import gmtime, strftime

class Message(object):

    def __init__(self, procId, messageId):
        self.sender = procId
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

    def __init__(self, procId, messageId):
        Message.__init__(self, procId, messageId)

    def isSegment(self):
        return True

class AdvertisementMessage(Message):

    def __init__(self, procId, messageId):
        Message.__init__(self, procId, messageId)

    def isAdvertisement(self):
        return True

class RequestMessage(Message):

    def __init__(self, procId, messageId):
        Message.__init__(self, procId, messageId)

    def isRequest(self):
        return True

class DimensionOfMessage(Message):

    def __init__(self, procId, messageId):
        Message.__init__(self, procId, messageId)

    def isDimensionOfSegment(self):
        return True