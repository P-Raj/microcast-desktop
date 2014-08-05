import History
import sys


class Monitor:

	def __init__(self, numProcs):
		self.numProcs = numProcs
		self.history = History.getHistory(self.numProcs)
		self.tabSize = 20

	def getTab(self,procId):
		return " "*self.tabSize*procId 
			
	def show(self):
		for hist in self.history:
			tab = self.getTab(hist[0])
			content = str(hist[2])
			print tab + content
