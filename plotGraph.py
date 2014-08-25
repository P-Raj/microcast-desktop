
import matplotlib.pyplot as pyplot

def plot(x, name="fig.png"):

	pyplot.plot([0.1*i for i in range(len(x))], x)
	pyplot.savefig(name)

def readFile(filename):
	dp = []
	with open(filename,"r") as fp:
		dp = [float(line) for line in fp.readlines()]
	return dp

if __name__ == "__main__":

	plot(readFile(),"")