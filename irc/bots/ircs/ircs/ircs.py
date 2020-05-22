#!/usr/bin/env python
# IRC Services (IRCS) - Developed by acidvegas in Python (https://acid.vegas/ircs)
# ircs.py

import os
import sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or '.')
sys.path += ('core',)

import debug
import irc

debug.info()
if not debug.check_version(3):
    debug.error_exit('IRCS requires Python 3!')
if debug.check_privileges():
    debug.error_exit('Do not run IRCS as admin/root!')
irc.IRCS.connect()
