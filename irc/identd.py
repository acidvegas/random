#!/usr/bin/env python
# ident protocol daemon - developed by acidvegas in Python (https://acid.vegas/random)

import os
import random
import re
import socket
import string
import threading
import pwd

def check_privledges():
	if os.getuid() == 0 or os.geteuid() == 0:
		return True
	else:
		return False

def is_valid_port(port):
	if port > 0 and port <= 65535:
		return True
	else:
		return False

def random_str(size):
	return ''.join(random.choice(string.ascii_letters) for _ in range(size))

class Identd(threading.Thread):
	def __init__(self, protocol, address, port):
		self.protocol = protocol
		self.address  = address
		self.port     = port
		self.sock     = None
		threading.Thread.__init__(self)

	def run(self):
		try:
			self._create_sockets()
			self._drop_privledges()
			self._listen()
		except Exception as ex:
			print('error: ' + str(ex))

	def _create_sockets(self):
		self.sock = socket.socket(self.protocol)
		self.sock.bind((self.address, self.port))
		self.sock.listen(5)
		self.sock.setblocking(0)

	def _drop_privledges(self):
		os.setgroups([])
		os.setgid(pwd.getpwnam('nobody').pw_gid)
		os.setuid(pwd.getpwnam('nobody').pw_uid)

	def _listen(self):
		while True:
			client, addr = self.sock.accept()
			data = client.recv(1024).decode('ascii').rstrip()
			source_ip = addr[0][7:] if addr[0][:7] == '::ffff:' else addr[0]
			print(f'[REQUEST] {source_ip}: {data}')
			response = self._parse_data(data)
			client.send(f'{response}\r\n'.encode('ascii'))
			print(f'[ REPLY ] {source_ip}: {response}')
			client.close()

	def _parse_data(self, data):
		if not re.match(r'(\d+).*,.*(\d+)', data):
			return data + ' : ERROR : INVALID-PORT'
		lport, rport = data.split(',')
		lport = int(re.sub(r'\D', '', lport))
		rport = int(re.sub(r'\D', '', rport))
		if not is_valid_port(lport) or not is_valid_port(rport):
			return data + ' : ERROR : INVALID-PORT'
		return data + ' : USERID : UNIX : ' + random_str(5)

# Main
if not check_privledges():
	raise SystemExit('requires sudo privledges to bind to port 113')
Identd(socket.AF_INET,  '0.0.0.0', 113).start()
Identd(socket.AF_INET6, '::',      113).start()
while True:
	input('')