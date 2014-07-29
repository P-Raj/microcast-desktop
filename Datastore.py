import pickle
from datetime import datetime

class DataStore:

	def __init__(self, name , mode='w'):
		self.file = open(name, mode)

	def store(self, message):
		_dumpMsg = {'data': message, 'log time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		pickle.dump(_dumpMsg, self.file)

	def get(self):
		return picle.load(self.file)
