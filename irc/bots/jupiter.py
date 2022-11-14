#!/usr/bin/env python
# Jupiter IRC Botnet - Developed by acidvegas in Python (https://acid.vegas/jupiter)

'''
Jupiter will create a botnet by connecting a defined number of clones to every EFMet server.
A single host could potentially create over 30 clones.
It is meant to monitor/jupe/hold nicks & be controlled to do just about anything.
The bot is designed to be very minimal, secure, & trustless by nature.
This means anyone can run a copy of your script on their server to help build your botnet.

Commands
	id                   | Send bot identity
	raw     [-d] <data>  | Send \<data> to server. optionally delayed with -d argument
	monitor list         | Return MONITOR list
	monitor reset        | Reset MONITOR list
	monitor <+/-><nicks> | Add (+) or Remove (-) <nicks> from MONITOR list. (Can be a single nick or comma seperated list)

All commands must be prefixed with @all or the bots nick & will work in a channel or private message.
Raw data must be IRC RFC compliant data & any nicks in the MONITOR list will be juped as soon as they become available.

It is highly recommended that you use a random spoofing ident protocol daemon:
	https://github.com/acidvegas/random/blob/master/irc/identd.py
'''

import random
import re
import socket
import ssl
import time
import threading

# Connection
servers = (
	'efnet.deic.eu',         # IPv6
	'efnet.port80.se',       # IPv6
	'efnet.portlane.se',     # IPv6
	'irc.choopa.net',        # IPv6
	'irc.colosolutions.net',
	'irc.du.se',
	'irc.efnet.fr',          # IPv6
	'irc.efnet.nl',          # IPv6 +6669
	'irc.homelien.no',       # IPv6
	'irc.mzima.net',         # IPv6 +6697
	'irc.nordunet.se',       # IPv6
	'irc.prison.net',
	'irc.underworld.no',     # IPv6
	'irc.servercentral.net'  # +9999
)
ipv6    = False
vhosts  = None # Use (line.rstrip() for line in open('vhosts.txt','r').readlines() if line) for reading from a file.
channel = '#jupiter'
key     = None

# Settings
admin           = 'nick!user@host' # Can use wildcards (Must be in nick!user@host format)
concurrency     = 3                # Number of clones to load per server
id              = 'TEST'           # Unique ID so you can tell which bots belong what server

# Formatting Control Characters / Color Codes
bold        = '\x02'
reset       = '\x0f'
green       = '03'
red         = '04'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'

# Globals
bots = list()

def botlist(nick):
	global bots
	if nick[:1] == '+':
		bots.append(nick[1:])
	elif nick[:1] == '-':
		bots.remove(nick[1:])

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	print(f'{get_time()} | [!] - {msg} ({reason})') if reason else print(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

def is_admin(ident):
	return re.compile(admin.replace('*','.*')).search(ident)

def random_nick():
	prefix = random.choice(['st','sn','cr','pl','pr','qu','br','gr','sh','sk','kl','wr']+list('bcdfgklmnprstvwz'))
	midfix = random.choice(('aeiou'))+random.choice(('aeiou'))+random.choice(('bcdfgklmnprstvwz'))
	suffix = random.choice(['ed','est','er','le','ly','y','ies','iest','ian','ion','est','ing','led']+list('abcdfgklmnprstvwz'))
	return prefix+midfix+suffix

class clone(threading.Thread):
	def __init__(self, server, vhost):
		self.monlist  = list()
		self.nickname = random_nick()
		self.server   = server
		self.sock     = None
		self.vhost    = vhost
		threading.Thread.__init__(self)

	def run(self):
		time.sleep(random.randint(300,900))
		self.connect()

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((server, 6667))
			self.raw(f'USER {random_nick()} 0 * :{random_nick()}')
			self.nick(self.nickname)
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			self.event_disconnect()
		else:
			self.listen()

	def create_socket(self):
		ipv6_check = set([ip[4][0] for ip in socket.getaddrinfo(server,6667) if ':' in ip[4][0]])
		self.sock  = socket.socket(socket.AF_INET6) if ipv6 and ipv6_check else socket.socket()
		if self.vhost:
			self.sock.bind((self.vhost,0))
		#self.sock = ssl.wrap_socket(self.sock)

	def event_connect(self):
		if self.nickname not in bots:
			botlist('+'+self.nickname)
		if self.monlist:
			self.monitor('+', self.monlist)
		self.join_channel(channel, key)

	def event_ctcp(self, nick, target, msg):
		if target == self.nickname:
			self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('CTCP', green), color('<', grey), color(nick, yellow), color('>', grey), msg))

	def event_disconnect(self):
		if self.nickname in bots:
			botlist('-'+self.nickname)
		self.sock.close()
		time.sleep(86400+random.randint(1800,3600))
		self.connect()

	def event_nick(self, nick, new_nick):
		if nick == self.nickname:
			self.nickname = new_nick
			if new_nick in self.monlist:
				self.monitor('C')
				self.monlist = list()
		elif nick in self.monlist:
			self.nick(nick)

	def event_nick_in_use(self, nick, target_nick):
		if nick == '*':
			self.nickname = random_nick()
			self.nick(self.nickname)

	def event_notice(self, nick, target, msg):
		if target == self.nickname:
			self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('NOTICE', purple), color('<', grey), color(nick, yellow), color('>', grey), msg))

	def event_message(self, ident, nick, target, msg):
		if is_admin(ident):
			args = msg.split()
			if args[0] in ('@all',self.nickname) and len(args) >= 2:
				if len(args) == 2:
					if args[1] == 'id':
						self.sendmsg(target, id)
				elif len(args) == 3 and args[1] == 'monitor':
					if args[2] == 'list' and self.monlist:
						self.sendmsg(target, '[{0}] {1}'.format(color('Monitor', light_blue), ', '.join(self.monlist)))
					elif args[2] == 'reset' and self.monlist:
						self.monitor('C')
						self.monlist = list()
						self.sendmsg(target, '{0} nick(s) have been {1} from the monitor list.'.format(color(str(len(self.monlist)), cyan), color('removed', red)))
					elif args[2][:1] == '+':
						nicks = [mon_nick for mon_nick in set(args[2][1:].split(',')) if mon_nick not in self.monlist]
						if nicks:
							self.monitor('+', nicks)
							self.monlist += nicks
							self.sendmsg(target, '{0} nick(s) have been {1} to the monitor list.'.format(color(str(len(nicks)), cyan), color('added', green)))
					elif args[2][:1] == '-':
						nicks = [mon_nick for mon_nick in set(args[2][1:].split(',')) if mon_nick in self.monlist]
						if nicks:
							self.monitor('-', nicks)
							for mon_nick in nicks:
								self.monlist.remove(mon_nick)
							self.sendmsg(target, '{0} nick(s) have been {1} from the monitor list.'.format(color(str(len(nicks)), cyan), color('removed', red)))
				elif len(args) >= 4 and args[1] == 'raw':
					if args[2] == '-d':
						data = ' '.join(args[3:])
						threading.Thread(target=self.raw, args=(data,True)).start()
					else:
						data = ' '.join(args[2:])
						self.raw(data)
		elif target == self.nickname:
			if msg.startswith('\x01ACTION'):
				self.sendmsg(channel, '[{0}] {1}{2}{3} * {4}'.format(color('PM', red), color('<', grey), color(nick, yellow), color('>', grey), msg[8:][:-1]))
			else:
				self.sendmsg(channel, '[{0}] {1}{2}{3} {4}'.format(color('PM', red), color('<', grey), color(nick, yellow), color('>', grey), msg))

	def event_mode(self, nick, chan, modes):
		pass # Don't know what we are doing with this yet.

	def event_quit(self, nick):
		if nick in self.monlist:
			self.nick(nick)

	def handle_events(self, data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif data.startswith('ERROR :Reconnecting too fast'):
			raise Exception('Connection has closed. (throttled)')
		elif args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001': # RPL_WELCOME
			self.event_connect()
		elif args[1] == '433' and len(args) >= 4: # ERR_NICKNAMEINUSE
			nick = args[2]
			target_nick = args[3]
			self.event_nick_in_use(nick, target_nick)
		elif args[1] == '731' and len(args) >= 4: # RPL_MONOFFLINE
			nick = args[3][1:]
			self.nick(nick)
		elif args[1] == 'MODE' and len(args) >= 4:
			nick  = args[0].split('!')[0][1:]
			chan  = args[2]
			modes = ' '.join(args[:3])
			self.event_mode(nick, chan, modes)
		elif args[1] == 'NICK' and len(args) == 3:
			nick = args[0].split('!')[0][1:]
			new_nick = args[2][1:]
			self.event_nick(nick, new_nick)
		elif args[1] == 'NOTICE':
			nick   = args[0].split('!')[0][1:]
			target = args[2]
			msg    = ' '.join(args[3:])[1:]
			self.event_notice(nick, target, msg)
		elif args[1] == 'PRIVMSG' and len(args) >= 4:
			ident  = args[0][1:]
			nick   = args[0].split('!')[0][1:]
			target = args[2]
			msg    = ' '.join(args[3:])[1:]
			if msg[:1] == '\001':
				msg = msg[1:]
				self.event_ctcp(nick, target, msg)
			else:
				self.event_message(ident, nick, target, msg)
		elif args[1] == 'QUIT':
			nick = args[0].split('!')[0][1:]
			self.event_quit(nick)

	def join_channel(self, chan, key=None):
		self.raw(f'JOIN {chan} {key}') if key else self.raw('JOIN ' + chan)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug(line)
					self.handle_events(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		self.event_disconnect()

	def mode(self, target, mode):
		self.raw(f'MODE {target} {mode}')

	def monitor(self, action, nicks=list()):
		self.raw(f'MONITOR {action} ' + ','.join(nicks))

	def nick(self, nick):
		self.raw('NICK ' + nick)

	def raw(self, data, delay=False):
		if delay:
			time.sleep(random.randint(300,900))
		self.sock.send(bytes(data + '\r\n', 'utf-8'))

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

# Main
if type(vhosts) == list:
	for vhost in vhosts:
		for i in range(concurrency):
			for server in servers:
				clone(server, vhost).start()
else:
	for i in range(concurrency):
		for server in servers:
			clone(server, vhosts).start()
while True:input('')
