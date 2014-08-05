import pickle
import datetime

def startRecording(fileId):
	fp = open(str(fileId)+".history", "w")
	pickle.dump([],fp)
	fp.close()

def addHistory(processId, instruction, fileId):
	existingHist = getHistory(fileId)
	fp = open(str(fileId)+".history", "w")
	existingHist.append([processId, datetime.datetime.now(), instruction])
	pickle.dump(existingHist, fp)
	fp.close()

def getHistory(fileId):
	try:
		fp = open(str(fileId)+".history" , "r")
	except:
		return []
	hist = pickle.load(fp)
	fp.close()
	return hist