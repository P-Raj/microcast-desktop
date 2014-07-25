
#local queues for processes
import Queue

class LocalQueue:
	def __init__(self, name):
		self.name = name
		self.queue = Queue.Queue()

	def add(message):
		self.queue.put(message)

	def getFromAdvertisement(message):
		if self.queue.empty():
			return None
		return self.queue.get()



