
import matplotlib.pyplot as pyplot

def plot(x,y,name="fig.png"):

	pyplot.plot(x,y)
	pyplot.savefig(name)

def readFile(filename):
	dp = []
	with open(filename,"r") as fp:
		dp = [float(line) for line in fp.readlines()]
	return dp

import pickle 
f = open("msg.log",'r')
d = {}
while True:
	try:
		l =  pickle.load(f)
	except:
		break
	d[l["procs"]] = d.get(l["procs"],0) + l["Message"]
	print l

print d

y = d.values().sorted()


plot(y,"nummsgs.png")
	
"""
if __name__ == "__main__":

	for i in range(5):
		plot(readFile("memory" + str(i) + ".dump"),str(i) + ".png")
"""
