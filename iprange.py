#!/usr/bin/env python

import ipaddress

donotscan = {
	'0.0.0.0/8',          # "This" network
	'10.0.0.0/8',         # Private networks
	'100.64.0.0/10',      # Carrier-grade NAT - RFC 6598
	'127.0.0.0/8',        # Host loopback
	'169.254.0.0/16',     # Link local
	'172.16.0.0/12',      # Private networks
	'192.0.0.0/24',       # IETF Protocol Assignments
	'192.0.0.0/29',       # DS-Lite
	'192.0.0.170/32',     # NAT64
	'192.0.0.171/32',     # DNS64
	'192.0.2.0/24',       # Documentation (TEST-NET-1)
	'192.88.99.0/24',     # 6to4 Relay Anycast
	'192.168.0.0/16',     # Private networks
	'198.18.0.0/15',      # Benchmarking
	'198.51.100.0/24',    # Documentation (TEST-NET-2)
	'203.0.113.0/24',     # Documentation (TEST-NET-3)
	'240.0.0.0/4',        # Reserved
	'255.255.255.255/32', # Limited Broadcast
	'6.0.0.0/8',          # Army Information Systems Center
	'7.0.0.0/8',          # DoD Network Information Center
	'11.0.0.0/8',         # DoD Intel Information Systems
	'21.0.0.0/8',         # DDN-RVN
	'22.0.0.0/8',         # Defense Information Systems Agency
	'26.0.0.0/8',         # Defense Information Systems Agency
	'28.0.0.0/8',         # DSI-North
	'29.0.0.0/8',         # Defense Information Systems Agency
	'30.0.0.0/8',         # Defense Information Systems Agency
	'33.0.0.0/8',         # DLA Systems Automation Center
	'55.0.0.0/8',         # DoD Network Information Center
	'205.0.0.0/8',        # US-DOD
	'214.0.0.0/8',        # US-DOD
	'215.0.0.0/8'         # US-DOD
}

total = ipaddress.IPv4Network('0.0.0.0/0').num_addresses
print(f'Total IPv4 Addresses : {total:,}')
for i in donotscan:
	total -= ipaddress.IPv4Network(i).num_addresses
print(f'Total After Clean    : {total:,}')
