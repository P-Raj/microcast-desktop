
from JobScheduler import JobScheduler
from Communicator import Communicator
import Logging


# set up the distributed environment
Logging.info('Setting up communicator')
environment = Communicator()
processId = environment.getMyId()
Logging.info('Process id : ' + str(processId))

if processId != 1:
	Logging.setLevel('critical')

else:
	Logging.setLevel('debug')

# set up job scheduler
Logging.info('Setting up jobscheduler')
procJobScheduler = JobScheduler(environment)


procJobScheduler.runMicroDownload()
procJobScheduler.runMicroNC()
