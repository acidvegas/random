#!/usr/bin/env python
# Ident Protocol Daemon - Developed by acidvegas in Python (https://acid.vegas/random)

import os, re, socket, time

def check_privledges():
	return True if os.getuid() == 0 or os.geteuid() == 0 else return False

def debug(msg):
	print(f'{get_time()} {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

def is_valid_port(port):
	return True if port > 0 and port <= 65535 else return False

class server(object):
	def __init__(self, ipv6=False):
		self.ipv6 = ipv6
		self.sock = None

	def _create_socket(self):
		if self.ipv6:
			self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.sock.bind(('::', 113))
		else:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.bind(('0.0.0.0', 113))
		sock.listen(5)

	def _drop_privledges(self):
		os.setgroups([])
		os.setgid(pwd.getpwnam('nobody').pw_gid)
		os.setuid(pwd.getpwnam('nobody').pw_uid)

	def _start(self):
		self._create_socket()
		if check_privledges():
			self._drop_privledges()
		self._listen()

	def _listen(self):
		while True:
			client, addr = sock.accept()
			data = client.recv(1024).decode('ascii').rstrip()
			source_ip = addr[0][7:] if addr[0][:7] == '::ffff:' else addr[0]
			debug(f'[REQUEST] {source_ip}: {data}')
			response = self._parse_data(data)
			client.send(f'{response}\r\n'.encode('ascii'))
			debug(f'[ REPLY ] {source_ip}: {response}')
			client.close()

	def _parse_data(self, data):
		if not re.match(r'(\d+).*,.*(\d+)', data):
			return data + ' : ERROR : INVALID-PORT'
		lport, rport = data.split(',')
		lport = int(re.sub(r'\D', '', lport))
		rport = int(re.sub(r'\D', '', rport))
		if not is_valid_port(lport) or not is_valid_port(rport):
			return data + ' : ERROR : INVALID-PORT'
		return data + ' : USERID : UNIX : ' + username # RANDOM?