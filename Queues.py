
#local queues for processes
import Queue

class LocalQueue:
	def __init__(self):
		self.queue = Queue.Queue()

	def add(message):
		self.queue.put(message)

	def get(message):
		if self.queue.empty():
			return None
		return self.queue.get()
