
class Channel:

	def __init__(self, fromProc, toProc, communicator):
		self.fromProc = fromProc
		self.toProc = toProc
		self.communicator = communicator

	def send(message, destination):
		self.communicator.send(message, dest=destination)
