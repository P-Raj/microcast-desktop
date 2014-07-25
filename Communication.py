import datetime


class Communication:

    def __init__(self, name="default"):
        self.name = name
        self.originTime = datetime.currentTime()
