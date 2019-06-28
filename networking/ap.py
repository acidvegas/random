#!/usr/bin/env python
import re, subprocess

interface = 'wlp1s0'

def between(source, start, stop):
	data = re.compile(start + '(.*?)' + stop, re.IGNORECASE|re.MULTILINE).search(source)
	if data : return data.group(1)
	else    : return False

output = subprocess.check_output(f'sudo iwlist {interface} scanning  | egrep \'Cell |Channel|Frequency|Encryption|Quality|ESSID|Mode\'', shell=True).decode()
access_points = output.split(' Cell ')[1:]
print('\033[30m\033[47mMAC Address         Channel   Frequency   Quality   Signal    Mode     Encryption   ESSID\033[0m')
for ap in access_points:
	address    = between(ap, 'Address: ',             '\n')
	channel    = between(ap, 'Channel:',              '\n').ljust(7)
	frequency  = between(ap, 'Frequency:',          ' GHz')[:3]
	quality    = between(ap, 'Quality=',        '  Signal')
	signal     = between(ap, 'Signal level=',       ' dBm')
	encryption = between(ap, 'Encryption key:',       '\n').ljust(10)
	essid      = between(ap, 'ESSID:\"',            '\"\n')
	mode       = between(ap, 'Mode:',                 '\n')
	print(f'{address} | {channel} | {frequency} GHz   | {quality}   | {signal} dBm | {mode} | {encryption} | {essid}')