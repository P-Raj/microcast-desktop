import logging
import sys

LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL,
            }

level_name = 'debug'
level = LEVELS.get(level_name, logging.NOTSET)
logging.basicConfig(level=level)

def info(message):
	global logging
	logging.info(message)
