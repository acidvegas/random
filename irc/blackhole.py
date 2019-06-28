#!/usr/bin/env python
# Blackhole IRC Bot - Developed by acidvegas in Python - (https://acid.vegas/random)

'''
WARNING: This script it entirely unfinished and should not be used for anything other than testing!

This is an advanced master/honeypot(s) bot system designed to combat advanced flooding techniques on IRC
'''

import random, ssl, socket, time, threading

# Config
nickserv_password = None
operator_password = None
user_modes        = None #BdZ

class HoneyPot(threading.Thread):
	def __init__(self):
		self.nickname = random.choice(BlackHole.db['honeypot_nicks'])
		self.sock = None
		threading.Thread.__init__(self)

	def connect(self):
		try:
			self.sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
			self.sock.connect(('localhost', 6697))
			self.raw(f'USER {username} 0 * :{realname}')
			self.raw('NICK ' + self.nickname)
		except socket.error:
			self.event_disconnect()
		else:
			self.listen()

	def event_disconnect(self):
		self.sock.close()
		time.sleep(15)
		self.connect()

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			for chan in channels:
				self.raw('JOIN ' + chan)
				time.sleep(1)
		elif args[1] == '433':
			self.nickname = random.choice(BlackHole.db['honeypot_nicks'])
			self.raw('NICK ' + self.nickname)
		elif args[1] == 'INVITE':
			nick = args[0].split('!')[0][1:]
			self.sendmsg('blackhole', '!' + nick)
		elif args[1] == 'KICK' and len(args) >= 4:
			chan   = args[2]
			kicked = args[3]
			if chan in channels and kicked == self.nickname:
				time.sleep(1)
				self.raw('JOIN ' + chan)
		elif args[1] == 'NOTICE':
			nick = args[0].split('!')[0][1:]
			self.sendmsg('blackhole', '!' + nick)
		elif args[1] == 'PRIVMSG' and len(args) >= 3:
			nick = args[0].split('!')[0][1:]
			chan = args[2]
			if chan == self.nickname or '\001' in data:
				self.sendmsg('blackhole', '!' + nick)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except:
				break
		self.event_disconnect()

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

class IRC(object):
	def __init__(self):
		self.db   = {'ident':list(),'nick':list(),:'protect':list()}
		self.sock = None

	def run(self):
		with open('blackhole.pkl','rb') as db_file:
			self.db = pickle.load(db_file)
		self.connect()

	def connect(self):
		try:
			self.sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
			self.sock.connect(('localhost', 6697))
			self.raw(f'USER BL 0 * :ENTER THE VOID')
			self.raw('NICK blackhole')
		except socket.error:
			self.event_disconnect()
		else:
			self.listen()

	def evemt_connect(self):
		self.mode(nickname, '+' + user_modes)
		self.identify(nickname, nickserv_password)
		self.oper(username, operator_password)

	def event_disconnect(self):
		self.sock.close()
		time.sleep(15)
		self.connect()

	def event_private(self, ident, nick, msg):
		if ident == admin:
			args = msg.split()
			cmd  = args[0][1:]
			if msg[:1] == '.':
				if cmd in self.db.keys():
					if len(args) == 1:
						for item in self.db[cmd]:
							self.sendmsg(nick, '\x0310' + item)
					elif len(args) == 2:
						option = args[1][1:]
						change = args[1][:1]
						if change == '+':
							if option not in self.db[cmd]:
								self.db[cmd].append(option)
								self.sendmsg(nick, '\x033added')
						elif change == '-':
							if option in self.db[cmd]:
								self.db[cmd].remove(option)
								self.sendmsg(nick, '\x035removed')
		elif ident not in self.db['protected_hosts']:
			self.raw('KILL {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			self.event_connect()
		elif args[1] == 'INVITE' or args[1] == 'NOTICE':
			nick = args[0].split('!')[0][1:]
			host = args[0].split('@')[1]
			self.raw('KILL {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')
		elif args[1] == 'KICK' and len(args) >= 4:
			nick   = args[0].split('!')[0][1:].lower()
			host   = args[0].split('@')[1]
			chan   = args[2]
			kicked = args[3].lower()
			if kicked == 'blackhole':
				time.sleep(1)
				self.raw('JOIN ' + chan)
			else:
				for item in self.db['nick']:
					if kicked == item:
						self.raw(f'KICK {chan} {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')
						self.mode(chan, '+b *!*@' + host)
						break
		elif args[1] == 'PRIVMSG' and len(args) == 4:
			ident = args[0].split('!')[1].lower()
			host  = args[0].split('@')[1]
			nick  = args[0].split('!')[0][1:].lower()
			chan  = args[2]
			msg   = ' '.join(args[3:])[1:].lower()
			if '\001' in msg:
				self.raw('KILL {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')
			elif chan == 'blackhole':
			 	if ident in self.db['ident'] and msg.startswith('!'):
					self.raw('KILL {msg[1:]} \x038,4          E N T E R   T H E   V O I D          \x0f')
				elif ident == admin:
					self.event_private(ident, nick, msg)
				else:
					self.raw('KILL {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')
			elif host not in self.db['protect']:
				for item in self.db['nick']:
					if item in msg:
						self.raw('KICK {chan} {nick} \x038,4          E N T E R   T H E   V O I D          \x0f')
						break

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					if len(line.split()) >= 2:
						self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except:
				break
		self.event_disconnect()

	def raw(self, msg):
		self.sock.send(bytes(msg + '\r\n', 'utf-8'))

# Main
BlackHole = IRC()
BlackHole.run()
