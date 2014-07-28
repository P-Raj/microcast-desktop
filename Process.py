
from JobScheduler import JobScheduler
from Communicator import Communicator
from Queues import LocalQueue

# set up the distributed environment
environment = Communicator()
processId = environment.getMyId()

# prints the details of the environemnt
environment.informClient()

<<<<<<< HEAD
#set up local queues
=======
>>>>>>> origin/master

# set up job scheduler
procJobScheduler = JobScheduler(environment)

procJobScheduler.runMicroDownload()
procJobScheduler.runMicroNC()
