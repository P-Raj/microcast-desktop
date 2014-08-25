class File:

	def __init__(self, procId, comm, mode="r"):
		self.id = str(procId)
		self.comm = comm
		self.mode = mode
		self.setupFile()

	def setupFile(self):
		if self.mode == "r":
			self.mpi_file = MPI.File.Open(self.comm,self.id)

	def write(self,buffer):
		pass

	def read(self):
		pass
