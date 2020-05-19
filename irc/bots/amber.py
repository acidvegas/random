#!/usr/bin/env python
# Amber Alert IRC Bot - Developed by acidvegas & blowfish in Python (https://acid.vegas/amber)
# amber.py

import asyncio
import random
import ssl
import textwrap
import time

import config

class config:
	server   = 'irc.supernets.org'
	channel  = '#superbowl'
	nickname = 'AMBERALERT'
	ident      = {'nickname':'AMBERALERT', 'username':'missing', 'realname':'IRC Amber Alert Bot', 'nickserv':None}

def ascii(nick):
	age    = '{0!s}{1}'.format(random.randint(12,90), random.choice(['',' AND HALF']))
	height = '{0!s}\' {1!s}"'.format(random.randint(3,6), random.randint(1,12))
	weight = '{0!s}LBS'.format(random.randint(90,500)) # >200 = (FNO)
	eyes   = random.choice(['BLUE','BROWN','GREEN'])
	return textwrap.dedent(f'''1,4                                                  
		1,4  1,8^^^^^^1,4  1,1   1,4 1,1     1,4 1,1  1,4  1,1  1,4 1,1  1,4   1,1   1,4 1,1 1,4  1,1  1,4 1,1  1,4  1,1   1,4 
		1,4 1,8<0,2 **** 1,8>1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4  1,1 1,4 1,1 1,4  1,1 1,4 1,1 1,4 1,1 1,4  1,1 1,4  1,1 1,4 1,1 1,4  1,1 1,4  
		1,4 1,8<0,2*CFLC*1,8>1,4 1,1   1,4 1,1 1,4 1,1 1,4 1,1 1,4 1,1  1,4  1,1  1,4 1,1  1,4   1,1   1,4 1,1 1,4  1,1  1,4 1,1  1,4   1,1 1,4  
		1,4 1,8<0,2 **** 1,8>1,4 1,1 1,4 1,1 1,4 1,1 1,4   1,1 1,4 1,1 1,4 1,1 1,4 1,1 1,4  1,1 1,4 1,1 1,4  1,1 1,4 1,1 1,4 1,1 1,4  1,1 1,4  1,1 1,4 1,1 1,4  1,1 1,4  
		1,4  1,8VVVVVV1,4  1,1 1,4 1,1 1,4 1,1 1,4   1,1 1,4 1,1  1,4  1,1  1,4 1,1 1,4 1,1 1,4  1,1 1,4 1,1 1,4 1,1  1,4 1,1  1,4 1,1 1,4 1,1 1,4  1,1 1,4  
		1,4                                                  
		1,1                                                  
		1,0                                                  
		1,0                                                  
		1,0  1,1                    1,0                            
		1,0  1,1 1,10                  1,1 1,0   12NAME   1: {nick.ljust(16)}
		1,0  1,1 1,10 5,7,;',;',,5,10 1        1,1 1,0                            
		1,0  1,1 1,10 5,7.;'.  ( _5,10 1       1,1 1,0  12 AGE    1: {age.ljust(16)}
		1,0  1,1 1,10 5,7.1@5;;1  0O O 1,10       1,1 1,0                            
		1,0  1,1 1,10 5,7.1 5; 1    > 1,10       1,1 1,0  12 HEIGHT1 : {height.ljust(16)}
		1,0  1,1 1,10 5,7;1    5 ;;;;5,10  1     1,1 1,0                            
		1,0  1,1 1,10 1,7      1,1___1,10 1,6\  1,10    1,1 1,0  12 WEIGHT1 : {weight.ljust(16)}
		1,0  1,1 1,7          1,10 1,6  1,7   1,10  1,1 1,0                            
		1,0  1,1 1,7     1,10         1,7   1,10 1,1 1,0   12EYES  1 : {eyes.ljust(16)}
		1,0  1,1                    1,0                            
		1,0                                                  
		1,0  Missing from #superbowl, SuperNETs since 2007   
		1,0                                                  
		1,0  ANY INFORMATION REGARDING THE WHERE-ABOUTS OF   
		1,0  THIS CHATTER SHOULD REPORT IT TO THE OFFICAL    
		1,0  CENTER FOR LOST CHATTERS 14(CFLC)1 AS SOON AS OK.  
		1,0                                                  
		1,0  1-800-5MISSING1                 missing@cflc.gov  
		1,0                                                  ''')

def ssl_ctx():
	ctx = ssl.create_default_context()
	ctx.check_hostname = False
	ctx.verify_mode = ssl.CERT_NONE
	return ctx

class IRC:
	def __init__(self):
		self.options  = {'host':'irc.supernets.org','port':6697,'limit':1024,'ssl':ssl_ctx(),'family':2}
		self.reader   = None
		self.writer   = None
		self.names    = {'found':list(), 'idle':list()}
		self.scanning = False
		self.looping  = False

	def _event_names(self, names):
		if self.scanning:
			for name in names:
				if name[:1] in '~!@%&+:':
					name = name[1:]
				if name not in ('AMBERALERT','CANCER','ChanServ','DickServ','EliManning','FUCKYOU','scroll'):
					self.names['found'].append(name)

	async def _event_end_of_names(self):
		self.scanning = False
		for name in self.names['found']:
			self._raw('WHOIS ' + name)
			await asyncio.sleep(2)
		if self.names['idle']:
			target = random.choice(self.names['idle'])
			for line in ascii(target).split('\n'):
				self._raw(f'PRIVMSG #superbowl :{line}')
				self._raw(f'PRIVMSG {target} :{line}')
		self.names = {'found':list(), 'idle':list()}

	async def _loop(self):
		while self.looping:
			if not self.scanning:
				self.scanning = True
				self._raw('NAMES #superbowl')
			await asyncio.sleep(random.randint(43200,86400)) # 12H-1D

	def _raw(self, data):
		self.writer.write(data[:510].encode('utf-8') + b'\r\n')

	async def _connect(self):
		try:
			self.reader, self.writer = await asyncio.open_connection(**self.options)
			self._raw(f'USER missing 0 * :Amber Alert IRC Bot')
			self._raw('NICK AMBERALERT')
		except Exception as ex:
			print(f'[!] - Failed to connect to IRC server! ({ex!s})')
		else:
			while not self.reader.at_eof():
				line = await self.reader.readline()
				line = line.decode('utf-8').strip()
				print('[~] - '+line)
				args = line.split()
				if args[0] == 'PING':
					self._raw('PONG ' + args[1][1:])
				elif args[1] == '001': # RPL_WELCOME
					self._raw('MODE AMBERALERT +BDd')
					self._raw('PRIVMSG NickServ IDENTIFY AMBERALERT CHANGEME')
					await asyncio.sleep(3)
					self._raw('JOIN #superbowl')
				elif args[1] == '353' and len(args) >= 6: # RPL_NAMREPLY
					chan = args[4]
					if chan == '#superbowl':
						names = ' '.join(args[5:])[2:].split()
						self._event_names(names)
				elif args[1] == '366' and len(args) >= 4: # RPL_ENDOFNAMES
					chan = args[3]
					if chan == '#superbowl':
						if self.scanning:
							asyncio.create_task(self._event_end_of_names())
						elif not self.looping:
							self.looping = True
							asyncio.create_task(self._loop())
				elif args[1] == '317' and len(args) >= 5: # RPL_WHOISIDLE
					nick = args[3]
					idle = args[4]
					if int(idle) >= 604800: # 1W
						self.names['idle'].append(nick)

# Start
if __name__ == '__main__':
	Bot = IRC()
	asyncio.run(Bot._connect())