import pickle
import datetime

class History:


	def addHistory(procId, instruction):
		existingHist = self.getHistory(procId)
		fp = open(str(procId), "w")
		existingHist.append([datetime.datetime.now(), instruction])
		pickle.dump(existingHist, fp)
		fp.close()

	def getHistory(procId):
		try:
			fp = open(str(procId)+".history" , "r")
		except:
			return []
		hist = pickle.load(fp)
		fp.close()
		return hist