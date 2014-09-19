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

def writeLog(string):
	if string['type'] == 'channel':
		op = "C" + str(string["from"]) + str(string["to"])
		op += "."
		op += string["op"]
		op = op + "(" + str(string["message"]) + ")" 
	elif string['type'] == 'process':
		op = "P" + str(string["procId"]) + "."
		op += string["op"]
		op = op + "(" + string.get("queue","None") + "," + str(string.get("message","None")) + ")"
	else:
		raise Exception("Uidentified log")
	print op


class File:

	def __init__(self, fileName):
		self.ext = ".log"
		if not os.path.exists(fileOpFolder):
   			os.makedirs(fileOpFolder)
		self.file = open(fileOpFolder + fileName + self.ext ,'w')

	def write(self,buffer):
		self.file.write(buffer)

