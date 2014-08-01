
from JobScheduler import JobScheduler
from Communicator import Communicator


# set up the distributed environment
environment = Communicator()
processId = environment.getMyId()

# prints the details of the environemnt
environment.informClient()

# set up job scheduler
procJobScheduler = JobScheduler(environment)

procJobScheduler.runMicroDownload()
procJobScheduler.microNC()
