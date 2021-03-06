from JobScheduler import JobScheduler
from Communicator import Communicator
import sys
import getopt
from config import DEFAULT_CMD_ARGS
import Logging


def readCmdArgs():

    cmdArgs = {}

    cmdArgs["logLevel"] = DEFAULT_CMD_ARGS["logLevel"]
    cmdArgs["onlyCp"] = DEFAULT_CMD_ARGS["onlyCp"]
    cmdArgs["peers"] = []
    cmdArgs["totalProcs"] = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:p:",
                                   [ "log_level", "only_cp"])
    except geopt.GetoptError:
        print sys.argv[0] + ' -s <number of segments>'
        sys.exit(2)


    for opt, arg in opts:

        if opt == '-h':
            print """mpiexec -n <num of processes> python
                    <main file>.py -s <number of segemnts>
                    -l <(d)ebug,(i)nfo,(e)roor,(w)arning,(c)ritical>"""
            sys.exit()



        elif opt == '-p':
            peerInfo = arg.split(":")
            peerInfo[-1] = int(peerInfo[-1]) #port number to int
            peerInfo.append(peerInfo[-1]+1)
            cmdArgs["peers"].append(peerInfo)
            #(ip,port)

        elif opt in ('-l', "--log_level"):

            levels = dict((('d', 'debug'), ('i', 'info'),
                           ('w', 'warning'), ('e', 'error'),
                           ('c', 'critical')))

            if arg in levels.keys() + ("--"+x for x in levels.values()):
                cmdArgs["logLevel"] = levels.get(arg, arg.replace("--", ""))

            else:
                print "Unknown log level (-l, --log_level)"
                print "Setting it to ", DEFAULT_CMD_ARGS["logLevel"]

        elif opt == '--only_cp':
            cmdArgs["onlyCp"] = True

        else:
            print "unknown symbol -" + opt
            print "Skipping -" + opt + " " + arg

    cmdArgs["numProcs"] = len(cmdArgs["peers"])
    return cmdArgs


cmdArgs = readCmdArgs()

Logging.level = cmdArgs["logLevel"]
Logging.onlyCp = cmdArgs["onlyCp"]

# set up the distributed environment
environment = Communicator(cmdArgs)

processId = environment.getMyId()
initiator = environment.totalProcs - 1


procJobScheduler = JobScheduler(environment)

if processId == initiator:
    procJobScheduler.runMicroDownload()
else:
    procJobScheduler.runMicroNC()

