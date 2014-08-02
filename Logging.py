
import logging
import sys

LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL,
            }

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

level_name = 'debug'

def logChannelOp(chanFrom, chanTo, op, message):
	message = bcolors.HEADER + "C" + str(chanFrom) + str(to) + "." + str(op) 
				+ "(" + str(type(message)) + ")"
	message = message + "    " + bcolors.OKBLUE + "id" + str(message.messageId)

	info(message)

def logProcessOp(processId, op, depQueue = None, _message = None):

	message = bcolors.HEADER + str(processId) + "." + str(op)
	
	if depQueue:
		message = message + "(" + str(depQueue) + "," + str(type(_message) + ")"
	if _message:
		message = message + "    " + bcolors.OKBLUE + "id" + str(message.messageId)

	info(message)

def setLevel(level_name):
	global logging
	level = LEVELS.get(level_name, logging.NOTSET)
	logging.basicConfig(level=level)

def info(message):
	global logging
	logging.info(message)

setLevel(level_name)
