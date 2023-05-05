#!/usr/bin/env python
# developed by acidvegas in Python (https://acid.vegas/random)

import socket, struct, random, threading

scan_ports = {
	17    : 'qotd',         # 140.3
	19    : 'chargen',      # 358.8
	53    : 'dns',          # 28-54
	69    : 'tftp',         # 60
	111   : 'portmap',      # 7 to 28
	123   : 'ntp',          # 556.9
	137   : 'netbios',      # 3.8
	139   : 'ws-discovery', # 15k
	161   : 'snmpv2',       # 6.3
	520   : 'ripv1',        # 131.24
	389   : 'ldap',         # 46-55 (TCP)
	389   : 'cldap',        # 56-70
	445   : 'ws-discovery', # 15k
	751   : 'kad',          # 16.3
	1900  : 'ssdp',         # 30.8
	3283  : 'apple remote', # 35.5
	1434  : 'mssql',        # 25
	5353  : 'mdns',         # 2-10
	6881  : 'bittorrent',   # 3.8
	26000 : 'quake',        # 63.9
	27015 : 'steam',        # 5.5
	11211 : 'memcached',    # 10k-51k
}

def scan():
	while True:
		ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
		for port in scan_ports:
		    sock = socket.socket()
		    sock.settimeout(3)
		    try:
		        code = sock.connect((ip, port))
		    except socket.error:
		        pass
		    else:
		        if not code:
		            print('FOUND ' + ip + ':' + str(port) + ' (' + scan_ports[port] + ')')
		    finally:
		        sock.close()

for i in range(100):
	threading.Thread(target=scan).start()

while True:
	input('')
