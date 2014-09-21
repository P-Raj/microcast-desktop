import subprocess,os


def dumpMemory(memoryFile):

	with open(memoryFile,"w") as fp:

		while True:

			out = subprocess.Popen(['ps', 'v', '-p', str(os.getpid())],
								   stdout=subprocess.PIPE
								   ).communicate()[0].split(b'\n')
			
			vsz_index = out[0].split().index(b'RSS')
			
			mem = float(out[1].split()[vsz_index]) / 1024

			fp.write(str(mem) + "\n")


