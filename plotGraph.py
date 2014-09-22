
import matplotlib.pyplot as pyplot

def plot(x, name="fig.png"):

	pyplot.plot(x)
	pyplot.savefig(name)

def readFile(filename):
	dp = []
	with open(filename,"r") as fp:
		dp = [float(line) for line in fp.readlines()]
	return dp

if __name__ == "__main__":

	for i in range(1):
		plot(readFile("memory" + str(i) + ".dump"),str(i) + ".png")
