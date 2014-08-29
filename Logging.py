import logging
import sys
from Message import CheckpointMessage
import LogStore
import LogViewer

level = 'critical'
onlyCp = False

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
          }


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def logChannelOp(chanFrom, chanTo, op, message):

    _message = bcolors.HEADER + "C" + str(chanFrom) \
        + str(chanTo) + "." + str(op) \
        + "(" + str(message) + ")"

    _op = {}
    _op["type"] = "channel"
    _op["from"] = chanFrom
    _op["to"] = chanTo
    _op["op"] = op
    _op["message"] = message

    LogStore.writeLog(_op)

    if onlyCp:
        if type(message) == type(CheckpointMessage):
            info(_message)
    else:
        info(_message)


def logProcessOp(processId, op, depQueue=None, message=None):

    _message = bcolors.HEADER + str(processId) + "." + str(op)
    _op = {}
    _op["type"] = "process"
    _op["procId"] = processId
    _op["op"] = op
    if depQueue:
        _op["queue"] = depQueue
    if message:
        _op["message"] = message

    LogStore.writeLog(_op)

    if depQueue:
        _message = _message + "(" + str(depQueue) + "," + str(_message) + ")"

    if onlyCp:
        if type(message) == type(CheckpointMessage):
            info(_message)
    else:
        info(_message)


def setLevel(level):
    global logging
    level = LEVELS.get(level, logging.NOTSET)
    logging.basicConfig(level=level)


def info(message):
    global logging
    logging.info(message)
