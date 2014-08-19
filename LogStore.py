import pickle

log_file_name = "store.log"

def writeLog(data):
	try:
		with open(log_file_name,"a") as fp:
			pickle.dump(obj=data,file=fp)
	except:
		with open(log_file_name,"w") as fp:
			pickle.dump(obj=data,file=fp)

def readLog():
	data = []
	try:
		with open(log_file_name,"r") as fp:
			while True:
				data.append(pickle.load(fp))
		return data
	except EOFError:
		return data

	
