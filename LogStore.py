import LogViewer
import os

terminalOpEnabled = True
fileOpEnabled = True
fileOpFolder = "output/"



def initRunHistory(procId):
	global historyFile
	historyFile = File(procId,"history")

def initDataHistory(procId):
	global dataFile


class File:

	def __init__(self, fileName):
		self.ext = ".log"
		if not os.path.exists(fileOpFolder):
   			os.makedirs(fileOpFolder)
		self.file = open(fileOpFolder + fileName + self.ext ,'w')

	def write(self,buffer):
		self.file.write(buffer)

