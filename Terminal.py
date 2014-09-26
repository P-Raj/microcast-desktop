import os
from subprocess import Popen, PIPE
import time, threading

class Monitor:

	def __init__(self, procId):

		self.pipe_path = "/tmp/pipe_" + str(procId)

		if not os.path.exists(self.pipe_path):
			os.mkfifo(self.pipe_path)

		Popen(['xterm', '-e', 'tail', '-f', self.pipe_path])


	def write(self, output):

		with open(self.pipe_path, "w") as ptr:
			ptr.write(output)
			ptr.flush()


		