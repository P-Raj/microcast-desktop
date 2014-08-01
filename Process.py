
from JobScheduler import JobScheduler
from Communicator import Communicator
import Logging


# set up the distributed environment
Logging.info('Setting up communicator')
environment = Communicator()
processId = environment.getMyId()
Logging.info('Process id : ' + str(processId))


# set up job scheduler
Logging.info('Setting up jobscheduler')
procJobScheduler = JobScheduler(environment)

procJobScheduler.runMicroDownload()
procJobScheduler.microNC()
