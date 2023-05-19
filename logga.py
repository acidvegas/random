#!/usr/bin/env python
# logging example - developed by acidvegas in python (https://acid.vegas/random)
import logging
import logging.handlers
import os

log_file=True # Set to False for console logging only

# Set up logging
sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(message)s', '%I:%M %p'))
if log_file:
	if not os.path.exists('logs'):
		os.makedirs('logs')
	fh = logging.handlers.RotatingFileHandler('logs/debug.log', maxBytes=250000, backupCount=7, encoding='utf-8')
	fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(filename)s.%(funcName)s.%(lineno)d | %(message)s', '%Y-%m-%d %I:%M %p'))
	logging.basicConfig(level=logging.NOTSET, handlers=(sh,fh))
	del fh
else:
	logging.basicConfig(level=logging.NOTSET, handlers=(sh,))
finally:
	del sh

# Logging examples
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.critical('ok')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

logging.shutdown()