#!/usr/bin/env python
# IPv6 Generator - Developed by acidvegas in Python (https://acid.vegas/random))
import os,random
interface = 'eth0'
subnet    = '2607:5300:201:3000:'
def randstr(size)                : return ''.join(random.sample(('1234567890ABCDEF'), size))
def randv6(subnet)               : return f'{subnet}{randstr(4)}:{randstr(4)}:{randstr(4)}:{randstr(4)}'
def v6(action,address,interface) : os.system(f'sudo ip addr {action} {address} dev {interafce}')
for i in range(50):
	v6('add',randv6(subnet),interface)
	print(ip)
#for ip in [line.rstrip() for line in open('ipv6.txt','r').readlines() if line]:
#	v6('del',ip,interface