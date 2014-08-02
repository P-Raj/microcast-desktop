
from JobScheduler import JobScheduler
from Communicator import Communicator
import Logging
import threading

# set up the distributed environment
#Logging.info('Setting up communicator')
environment = Communicator()
processId = environment.getMyId()
#Logging.info('Process id : ' + str(processId))

if processId != 1:
	Logging.setLevel('debug')

else:
	Logging.setLevel('debug')

# set up job scheduler
#Logging.info('Setting up jobscheduler')
procJobScheduler = JobScheduler(environment)

mdThread = threading.Thread(target=procJobScheduler.runMicroDownload())
mnThread = threading.Thread(target=procJobScheduler.runMicroNC())

mdThread.daemon = True
mnThread.daemon = True

mdThread.start()
mnThread.start()
mnThread.join()
mdThread.join()

