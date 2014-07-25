
from JobScheduler import JobScheduler
from Communicator import Communicator
from Queues import LocalQueue

# set up the distributed environment
environment = Communicator()

#set up local queues
advts = LocalQueue()
requests = LocalQueue()

# set up job scheduler
procJobScheduler = JobScheduler(environment)

procJobScheduler.runMicroDownload(advts, requests)
procJobScheduler.runMicroNC(advts, requests)
