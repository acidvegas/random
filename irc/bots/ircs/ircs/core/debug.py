#!/usr/bin/env python
# IRC Services (IRCS) - Developed by acidvegas in Python (https://acid.vegas/ircs)
# debug.py

import ctypes
import os
import sys
import time
import string

def check_data(data):
    if all(c in string.printable for c in data):
        return True
    else:
        return False

def check_privileges():
    if check_windows():
        if ctypes.windll.shell32.IsUserAnAdmin() != 0:
            return True
        else:
            return False
    else:
        if os.getuid() == 0 or os.geteuid() == 0:
            return True
        else:
            return False

def check_version(major):
    if sys.version_info.major == major:
        return True
    else:
        return False

def check_windows():
    if os.name == 'nt':
        return True
    else:
        return False

def clear():
    if check_windows():
        os.system('cls')
    else:
        os.system('clear')

def error(msg, reason=None):
    if reason:
        print('{0} | [!] - {1} ({2})'.format(get_time(), msg, str(reason)))
    else:
        print('{0} | [!] - {1}'.format(get_time(), msg))

def error_exit(msg):
    raise SystemExit('{0} | [!] - {1}'.format(get_time(), msg))

def get_time():
    return time.strftime('%I:%M:%S')

def info():
    clear()
    print(''.rjust(56, '#'))
    print('#{0}#'.format(''.center(54)))
    print('#{0}#'.format('IRC Services (IRCS)'.center(54)))
    print('#{0}#'.format('Developed by acidvegas in Python'.center(54)))
    print('#{0}#'.format('https://acid.vegas/ircs'.center(54)))
    print('#{0}#'.format(''.center(54)))
    print(''.rjust(56, '#'))

def irc(msg):
    print('{0} | [~] - {1}'.format(get_time(), msg))