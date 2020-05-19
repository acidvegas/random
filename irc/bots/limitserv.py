#!/usr/bin/env python
# LimitServ IRC Service Bot - Developed by acidvegas in Python (https://acid.vegas/random)

import socket
import threading
import time

# Configuration
_connection = {'server':'irc.server.com', 'port':6697, 'ssl':True, 'ssl_verify':False, 'ipv6':False, 'vhost':None}
_cert       = {'file':None, 'key':None, 'password':None}
_ident      = {'nickname':'LimitServ', 'username':'services', 'realname':'Channel Limit Service'}
_login      = {'nickserv':None, 'network':None, 'operator':None}
_throttle   = {'limit':300, 'queue':0.5, 'voice':10}
_settings   = {'anope':False, 'honeypot':'#blackhole', 'limit':10, 'modes':None}

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason):
	print(f'{get_time()} | [!] - {msg} ({reason})')

def get_time():
	return time.strftime('%I:%M:%S')

class IRC(object):
	def __init__(self):
		self._channels = list()
		self._names = list()
		self._queue = list()
		self._voices = dict()
		self._sock = None

	def _run(self):
		Loop._loops()
		self._connect()

	def _connect(self):
		try:
			self._create_socket()
			self._sock.connect((_connection['server'], _connection['port']))
			self._register()
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			Event._disconnect()
		else:
			self._listen()

	def _create_socket(self):
		self._sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) if _connection['ipv6'] else socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if _connection['vhost']:
			self._sock.bind((_connection['vhost'], 0))
		if _connection['ssl']:
			ctx = ssl.SSLContext()
			if _cert['file']:
				ctx.load_cert_chain(_cert['file'], _cert['key'], _cert['password'])
			if _connection['ssl_verify']:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self._sock = ctx.wrap_socket(self._sock)

	def _listen(self):
		while True:
			try:
				data = self._sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug(line)
					Event._handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		Event._disconnect()

	def _register(self):
		if _login['network']:
			Bot._queue.append('PASS ' + _login['network'])
		Bot._queue.append('USER {0} 0 * :{1}'.format(_ident['username'], _ident['realname']))
		Bot._queue.append('NICK ' + _ident['nickname'])

class Command:
	def _join(chan, key=None):
		Bot._queue.append('JOIN {chan} {key}') if key else Bot._queue.append('JOIN ' + chan)

	def _kick(chan, nick, msg=None):
		Bot._queue.append(f'KICK {chan} {nick} {msg}') if msg else Bot._queue.append(f'KICK {chan} {nick}')

	def _mode(target, mode):
		Bot._queue.append(f'MODE {target} {mode}')

	def _raw(msg):
		Bot._sock.send(bytes(msg[:510] + '\r\n', 'utf-8'))

	def _sendmsg(target, msg):
		Bot._queue.append(f'PRIVMSG {target} :{msg}')

class Event:
	def _connect():
		if _settings['modes']:
			Command._mode(_ident['nickname'], '+' + _settings['modes'])
		if _login['nickserv']:
			Command._sendmsg('NickServ', 'IDENTIFY {0} {1}'.format(_ident['nickname'], _login['nickserv']))
		if _login['operator']:
			Bot._queue.append('OPER {0} {1}'.format(_ident['username'], _login['operator']))

	def _disconnect():
		Bot._sock.close()
		Bot._names = list()
		Bot._queue = list()
		Bot._voices = dict()
		time.sleep(15)
		Bot.connect()

	def _end_of_names(chan):
		limit = str(len(Bot._names) + _settings['limit'])
		if settings['anope']:
			Command._sendmsg('ChanServ', 'MODE {0} LOCK ADD +lL {1} {2}'.format(chan, limit, _settings['honeypot']))
		else:
			Command._mode(chan, '+lL {0} {1}'.format(limit, _settings['honeypot']))
		Bot._names = list()

	def _join(nick, chan):
		if nick == _ident['nickname'].lower():
			if chan not in Bot._channels:
				Bot._channels.append(chan)
			if chan not in Bot._voices:
				Bot._voices[chan] = dict()
		elif chan in Bot._channels:
			if nick not in Bot._voices[chan]:
				Bot._voices[chan][nick] = time.time()

	def _kick(nick, chan, kicked):
		if nick == _ident['nickname'].lower():
			Bot._channels.remove(chan)
			del Bot._voices[chan]
			time.sleep(3)
			Command._join(chan)
		elif chan in Bot._channels:
			if nick in Bot._voices[chan]:
				del Bot._voices[chan][nick]

	def _names(chan, nicks):
		for name in nicks:
			if name[:1] in '~!@%&+':
				name = name[1:]
			Bot._names.append(name)

	def _nick(nick, new_nick):
		for chan in Bot._voices:
			if nick in Bot._voices[chan]:
				Bot._voices[chan][new_nick] = Bot._voices[chan][nick]
				del Bot._voices[chan][nick]

	def _no_such_nick(nick):
		for chan in Bot._voices:
			if nick in Bot._voices[chan]:
				del Bot.voices[chan][nick]

	def _part(nick, chan):
		if nick == _ident['nickname'].lower():
			Bot._channels.remove(chan)
			del Bot._voices[chan]
		elif chan in Bot._channels:
			if nick in Bot._voices[chan]:
				del Bot._voices[chan][nick]

	def _quit(nick):
		for chan in Bot._voices:
			if nick in Bot._voices[chan]:
				del Bot._voices[chan][nick]

	def _handle(data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif data.startswith('ERROR :Reconnecting too fast, throttled.'):
			raise Exception('Connection has closed. (throttled)')
		elif args[0] == 'PING':
			Command._raw('PONG ' + args[1][1:])
		elif args[1] == '001': # RPL_WELCOME
			Event._connect()
		elif args[1] == '401': # ERR_NOSUCHNICK
			nick = args[3].lower()
			Event._no_such_nick(nick)
		elif args[1] == '433': # ERR_NICKNAMEINUSE
			raise Exception('Bot is already running or nick is in use.')
		elif args[1] == '353' and len(args) >= 6: #RPL_NAMREPLY
			chan = args[4].lower()
			names = ' '.join(args[5:]).lower()[1:].split()
			Event._names(chan, names)
		elif args[1] == '366' and len(args) >= 4: # RPL_ENDOFNAMES
			chan = args[3].lower()
			Event._end_of_names(chan)
		elif args[1] == 'JOIN' and len(args) == 3:
			nick = args[0].split('!')[0][1:].lower()
			chan = args[2][1:].lower()
			Event._join(nick, chan)
		elif args[1] == 'KICK' and len(args) >= 4:
			nick = args[0].split('!')[0][1:].lower()
			chan = args[2].lower()
			kicked = args[3].lower()
			Event._kick(nick, chan, kicked)
		elif args[1] == 'NICK' and len(args) == 3:
			nick = args[0].split('!')[0][1:].lower()
			new_nick = args[2][1:].lower()
			Event._nick(nick, new_nick)
		elif args[1] == 'PART' and len(args) >= 3:
			nick = args[0].split('!')[0][1:].lower()
			chan = args[2].lower()
			Event._part(nick, chan)
		elif args[1] == 'QUIT':
			nick = args[0].split('!')[0][1:].lower()
			Event._quit(nick)

class Loop:
	def _loops():
		threading.Thread(target=Loop._queue).start() # start first to handle incoming data
		threading.Thread(target=Loop._limit).start()
		threading.Thread(target=Loop._voice).start()

	def _limit():
		while True:
			try:
				for chan in Bot._channels:
					Bot._queue.append('NAMES ' + chan)
			except Exception as ex:
				error('Error occured in the loop!', ex)
			finally:
				time.sleep(_throttle['limit'])

	def _queue():
		while True:
			try:
				if Bot._queue:
					Command._raw(Bot._queue.pop(0))
			except Exception as ex:
				error('Error occured in the queue loop!', ex)
			finally:
				time.sleep(_throttle['queue'])

	def _voice():
		while True:
			try:
				for chan in Bot._voices:
					nicks = [nick for nick in Bot._voices[chan] if time.time() - Bot._voices[chan][nick] > _throttle['voice']]
					for item in [nicks[i:i + 4] for i in range(0, len(nicks), 4)]:
						Command._mode(chan, '+{0} {1}'.format('v'*len(item), ' '.join(item)))
						for subitem in item:
							del Bot._voices[chan][subitem]
			except Exception as ex:
				error('Error occured in the voice loop!', ex)
			finally:
				time.sleep(1)

# Main
if _connection['ssl']:
	import ssl
else:
	del cert, _connection['verify']
Bot = IRC()
Bot._run()
