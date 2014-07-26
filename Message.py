
class Message:

    def __init__(self, procId, messageId = -1):
        self.sender = procId
        self.messageId = messageId

    def initMessage(self, msgProperty, msgContent):
        self.property = msgProperty
        self.content = msgContent

    def isPacket(self):
        pass

    def isSegment(self):
        pass

    def isAdvertisement(self):
        pass

    def isRequest(self):
        pass

    def isDimensionOfSegment(self):
        pass

    def initContents(self):


