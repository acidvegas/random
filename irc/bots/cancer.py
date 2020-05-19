#!/usr/bin/env python
# Cancer IRC Bot - Developed by acidvegas in Python (https://acid.vegas/random)

'''
WARNING: This bot highly encourages flooding!

Commands:
	@cancer       | Information about the bot.
	@cancer stats | Return bot statistics for the channel
	!100          | 1 in 100 chance to get a 100 (big !smoke)
	!beer [nick]  | Grab a beer or toss one to someone.
	!chainsmoke   | Start a game of Chain Smoke
	!chug         | Sip beer
	!dragrace     | Start a game of Drag Race
	!extendo      | 1 in 100 chance to get an EXTENDO (big !toke)
	!fatfuck      | 1 in 100 chance to get a  FATFUCK (fat !smoke/!toke)
	!letschug     | LET'S FUCKING CHUG!
	!letstoke     | LET'S FUCKING TOKE!
	!toke         | Hit joint
	!smoke        | Hit cigarette
'''

import os
import random
import socket
import threading
import time

# Connection
server     = 'irc.server.com'
port       = 6697
use_ipv6   = False
use_ssl    = True
ssl_verify = False
vhost      = None
channel    = '#chats'
key        = None

# Certificate
cert_key  = None
cert_file = None
cert_pass = None

# Identity
nickname = 'CANCER'
username = 'smokesome' # vHost can be CIG@ARETTE or C@NCER for vanity purposes
realname = 'acid.vegas/random'

# Login
nickserv_password = None
network_password  = None
operator_password = None

# Settings
user_modes = None

# Globals (DO NOT EDIT)
stat_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'stats.log')

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def color(msg, foreground, background=None):
	return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	print(f'{get_time()} | [!] - {msg} ({reason})') if reason else print(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

def luck(odds):
	return True if random.randint(1,odds) == 1 else False

def stats(stat_type, stat_action):
	option = {'chug':0,'smoke':1,'toke':2}
	if stat_action == 'add':
		stats = [int(stat) for stat in open(stat_file).read().split().split(':')]
		with open(stat_file, 'w') as stats_file:
			stats[option[stat_type]]+=1
			stats_file.write(':'.join([str(stat) for stat in stats]))
	elif stat_action == 'get':
		return int(open(stat_file).read().split(':')[option[stat_type]])

class IRC(object):
	def __init__(self):
		self.chain_smoked    = 0
		self.drag_race_start = 0
		self.fat             = False
		self.event           = None
		self.nicks           = list()
		self.sock            = None
		self.stats           = {'chugged':0,'hits':25,'sips':8,'smoked':0,'toked':0}
		self.status          = True

	def run(self):
		threading.Thread(target=Games.loop).start()
		self.connect()

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((server, port))
			self.register()
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			Events.disconnect()
		else:
			self.listen()

	def create_socket(self):
		self.sock = socket.socket(socket.AF_INET6) if use_ipv6 else socket.socket()
		if vhost:
			self.sock.bind((vhost, 0))
		if use_ssl:
			ctx = ssl.SSLContext()
			if cert_file:
				ctx.load_cert_chain(cert_file, cert_key, cert_pass)
			if ssl_verify:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug(line)
					Events.handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		Events.disconnect()

	def register(self):
		if network_password:
			Commands.raw('PASS ' + network_password)
		Commands.raw(f'USER {username} 0 * :{realname}')
		Commands.raw('NICK ' + nickname)

class Commands:
	def action(chan, msg):
		Commands.sendmsg(chan, f'\x01ACTION {msg}\x01')

	def join_channel(chan, key=None):
		Commands.raw(f'JOIN {chan} {key}') if key else Commands.raw('JOIN ' + chan)

	def kill(nick, reason):
		Commands.raw(f'KILL {nick} {reason}')

	def notice(target, msg):
		Commands.raw(f'NOTICE {target} :{msg}')

	def raw(msg):
		Bot.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(target, msg):
		Commands.raw(f'PRIVMSG {target} :{msg}')

class Events:
	def connect():
		if user_modes:
			Commands.raw(f'MODE {nickname} +{user_modes}')
		if nickserv_password:
			Commands.sendmsg('NickServ', f'IDENTIFY {nickname} {nickserv_password}')
		if operator_password:
			Commands.raw(f'OPER {username} {operator_password}')
		Commands.join_channel(channel, key)

	def disconnect():
		Bot.chain_smoked    = 0
		Bot.drag_race_start = 0
		Bot.event           = None
		Bot.nicks           = list()
		Bot.status          = True
		Bot.sock.close()
		time.sleep(10)
		Bot.connect()

	def message(nick, chan, msg):
		if Bot.status:
			args = msg.split()
			if msg == '@cancer':
				Commands.sendmsg(chan, bold + 'CANCER IRC Bot - Developed by acidvegas in Python - https://acid.vegas/random')
			elif msg == '@cancer stats':
				Commands.sendmsg(chan, 'Chugged : {0} beers      {1}'.format(color('{:,}'.format(stats('chug','get')*24), light_blue), color('({:,} cases)'.format(stats('chug','get')), grey)))
				Commands.sendmsg(chan, 'Smoked  : {0} cigarettes {1}'.format(color('{:,}'.format(stats('smoke','get')*20), light_blue), color('({:,} packs)'.format(stats('smoke','get')), grey)))
				Commands.sendmsg(chan, 'Toked   : {0} joints     {1}'.format(color('{:,}'.format(stats('toke','get')*3), light_blue), color('({:,} grams)'.format(stats('toke','get')), grey)))
			elif msg in ('!100','!extendo') and luck(100):
				Bot.stats['hits'] = 100
				if msg == '!100':
					Commands.sendmsg(chan, '{0}{1}{2}'.format(color(' !!! ', white, red), color('AWWW SHIT, IT\'S TIME FOR THAT NEWPORT 100', red, white), color(' !!! ', white, red)))
				else:
					Commands.sendmsg(chan, '{0}{1}{2}'.format(color(' !!! ', red, green), color('OHHH FUCK, IT\'S TIME FOR THAT 420 EXTENDO', yellow, green), color(' !!! ', red, green)))
			elif args[0] == '!beer':
				if len(args) == 1:
					target = nick
				elif len(args) == 2:
					target = args[1]
				beer = '{0}{1}{2}'.format(color(' ', white, white), color(' BUD ', white, random.choice((blue,brown))), color('c', grey, white))
				Commands.action(chan, f'throws {color(target, white)} an ice cold {beer} =)')
			elif msg == '!chainsmoke' and not Bot.event:
				threading.Thread(target=Games.chain_smoke, args=(chan,)).start()
			elif msg == '!chug':
				if Bot.event == 'letschug':
					if nick in Bot.nicks:
						Commands.sendmsg(chan, color(nick + ' you are already chuggin u wastoid!', light_green))
					else:
						Bot.nicks.append(nick)
						Commands.sendmsg(chan, color(nick + ' joined the CHUG session!', light_green))
				else:
					if Bot.stats['sips'] <= 0:
						Bot.stats['sips'] = 8
						Bot.stats['chugged'] += 1
						if Bot.stats['chugged'] == 24:
							stats('chug','add')
							Bot.stats['chugged'] = 0
					for line in Generate.mug(Bot.stats['sips']):
						Commands.sendmsg(chan, line)
					Bot.stats['sips'] -= random.choice((1,2))
			elif msg == '!dragrace' and not Bot.event:
				threading.Thread(target=Games.drag_race).start()
			elif msg == '!fatfuck' and luck(100):
				Bot.fat = True
				Commands.sendmsg(chan, '{0}{1}{2}'.format(color(' !!! ', red, green), color('AWWW SHIT, IT\'S TIME FOR THAT MARLBORO FATFUCK', black, green), color(' !!! ', red, green)))
			elif msg == '!letschug' and not Bot.event:
				threading.Thread(target=Games.chug, args=(nick,chan)).start()
			elif msg == '!letstoke' and not Bot.event:
				threading.Thread(target=Games.toke, args=(nick,chan)).start()
			elif msg in ('!smoke','!toke'):
				option = 'smoked' if msg == '!smoke' else 'toked'
				if msg == '!toke' and Bot.event == 'letstoke':
					if nick in Bot.nicks:
						Commands.sendmsg(chan, color(nick + ' you are already toking u stoner!', light_green))
					else:
						Bot.nicks.append(nick)
						Commands.sendmsg(chan, color(nick + ' joined the TOKE session!', light_green))
				else:
					if Bot.stats['hits'] <= 0:
						Bot.stats['hits'] = 25
						Bot.stats[option] += 1
						if Bot.fat:
							Bot.fat = False
						if Bot.stats[option] == 20:
							stats(option[:-1],'add')
							Bot.stats[option] = 0
						if Bot.event == 'chainsmoke' and msg == '!smoke':
							Bot.nicks[nick] = Bot.nicks[nick]+1 if nick in Bot.nicks else 1
							Bot.chain_smoked += 1
						elif Bot.event == 'dragrace' and msg == '!smoke':
							Commands.sendmsg(chan, 'It took {0} seconds for {1} to smoke a cigarette!'.format(color('{:.2f}'.format(time.time()-Bot.drag_race_start), light_blue), color(chan, white)))
							Bot.event = None
							Bot.drag_race_start = 0
						elif luck(25):
							Commands.kill(nick, f'CANCER KILLED {nick.upper()} - QUIT SMOKING TODAY! +1 800-QUIT-NOW')
					else:
						object = Generate.cigarette(Bot.stats['hits']) if msg == '!smoke' else Generate.joint(Bot.stats['hits'])
						cigarette = Generate.cigarette(Bot.stats['hits'])
						if Bot.fat:
							Commands.sendmsg(chan, object)
							Commands.sendmsg(chan, object)
							Commands.sendmsg(chan, object)
						else:
							Commands.sendmsg(chan, object)
						Bot.stats['hits'] -= random.choice((1,2))

	def handle(data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			Commands.raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			Events.connect()
		elif args[1] == '433':
			error('The bot is already running or nick is in use.')
		elif args[1] == 'INVITE' and len(args) == 4:
			invited = args[2]
			chan    = args[3][1:]
			if invited == nickname and chan == channel:
				Commands.join_channel(channel, key)
		elif args[1] == 'KICK' and len(args) >= 4:
			chan   = args[2]
			kicked = args[3]
			if kicked == nickname and chan == channel:
				time.sleep(3)
				Commands.join_channel(channel, key)
		elif args[1] == 'PART' and len(args) >= 3:
			chan = args[2]
			if chan == channel:
				nick = args[0].split('!')[0][1:]
				Commands.action(nick, f'blows smoke in {nick}\'s face...')
		elif args[1] == 'PRIVMSG' and len(args) >= 4:
			nick = args[0].split('!')[0][1:]
			chan = args[2]
			msg  = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
			if chan ==  channel:
				Events.message(nick, chan, msg)

class Games:
	def chain_smoke(chan):
		Bot.event  = 'chainsmoke'
		Bot.status = False
		Bot.nicks  = dict()
		try:
			Commands.notice(chan, 'Starting a round of {0} in {1} seconds!'.format(color('ChainSmoke', red), color('10', white)))
			Commands.notice(chan, '[{0}] {1} {2} {3}'.format(color('How To Play', light_blue), color('Type', yellow), color('!smoke', light_green), color('to hit a cigarette. The cigarette goes down a little after each hit. Once you finish a cigarette, a new one will be lit for you. You will have 60 seconds to chain smoke as many cigarettes as possible.', yellow)))
			time.sleep(10)
			Commands.action(chan, 'Round starts in 3...')
			time.sleep(1)
			Commands.action(chan, '2...')
			time.sleep(1)
			Commands.action(chan, '1...')
			time.sleep(1)
			Commands.action(chan, color('GO', light_green))
			Bot.status = True
			time.sleep(60)
			Bot.status = False
			Commands.sendmsg(chan, color('          CHAINSMOKE ROUND IS OVER          ', red, yellow))
			time.sleep(1)
			Commands.sendmsg(chan, color('          CHAINSMOKE ROUND IS OVER          ', red, yellow))
			time.sleep(1)
			Commands.sendmsg(chan, color('          CHAINSMOKE ROUND IS OVER          ', red, yellow))
			Commands.sendmsg(chan, color('Counting cigarette butts...', yellow))
			time.sleep(10)
			Commands.sendmsg(chan, '{0} smoked {1} cigarettes!'.format(chan, color(str(Bot.chain_smoked), light_blue)))
			if Bot.nicks:
				guy = max(Bot.nicks, key=Bot.nicks.get)
				Commands.sendmsg(chan, '{0} smoked the most cigarettes... {1}'.format(guy, Bot.nicks[guy]))
		except Exception as ex:
			error('Error occured in chain smoke event!', ex)
		finally:
			Bot.chain_smoked  = 0
			Bot.nicks  = list()
			Bot.event  = None
			Bot.status = True

	def chug(nick, chan):
		Bot.event = 'letschug'
		Bot.nicks.append(nick)
		try:
			Commands.sendmsg(chan, color(f'OH SHIT {nick} is drunk', light_green))
			Commands.notice(chan, color(f'Time to TOTALLY CHUG in {chan.upper()} in 30 seconds, type !chug to join', light_green))
			time.sleep(10)
			Commands.sendmsg(chan, color('LOL we CHUG in 20 get ready ' + ' '.join(Bot.nicks), light_green))
			time.sleep(10)
			Commands.sendmsg(chan, color('YO we CHUG in 10 get ready ' + ' '.join(Bot.nicks), light_green))
			time.sleep(5)
			Commands.sendmsg(chan, color('alright CHUG in 5', light_green))
			time.sleep(1)
			Commands.sendmsg(chan, color('4..', light_green))
			time.sleep(1)
			Commands.sendmsg(chan, color('3..', light_green))
			time.sleep(1)
			Commands.sendmsg(chan, color('2..', light_green))
			time.sleep(1)
			Commands.sendmsg(chan, color('1..', light_green))
			time.sleep(1)
			Commands.sendmsg(chan, color(' '.join(Bot.nicks) + ' .. CHUG!', light_green))
		except Exception as ex:
			error('Error occured in chug event!', ex)
		finally:
			Bot.event = None
			Bot.nicks = list()

	def drag_race():
		Bot.event  = 'dragrace'
		Bot.status = False
		Bot.hits   = 25
		try:
			Commands.notice(channel, 'Starting a round of {0} in {1} seconds!'.format(color('DragRace', red), color('10', white)))
			Commands.notice(channel, '[{0}] {1} {2} {3}'.format(color('How To Play', light_blue), color('Type', yellow), color('!smoke', light_green), color('to hit a cigarette. The cigarette goes down a little after each hit. You will have 10 seconds to smoke as quickly as possible.', yellow)))
			time.sleep(10)
			Commands.action(channel, 'Round starts in 3...')
			time.sleep(1)
			Commands.action(channel, '2...')
			time.sleep(1)
			Commands.action(channel, '1...')
			time.sleep(1)
			Commands.action(channel, color('GO', light_green))
			Bot.drag_race_start = time.time()
		except Exception as ex:
			error('Error occured in the drag race event!', ex)
		finally:
			Bot.status = True

	def loop():
		while True:
			if get_time()[:-3] == '04:20':
				try:
					Commands.sendmsg(channel, color('S M O K E W E E D E R R D A Y', light_green))
					Commands.sendmsg(channel, color('ITZ DAT MUTHA FUCKN 420 BITCH', yellow))
					Commands.sendmsg(channel, color('LIGHT UP A NICE GOOD FAT FUCK', red))
					time.sleep(43000)
				except Exeption as ex:
					error('Error occured in loop!', ex)
			else:
				time.sleep(30)

	def toke(nick, chan):
		Bot.event = 'letstoke'
		Bot.nicks.append(nick)
		try:
			Commands.sendmsg(channel, color(f'YO {nick} is high', light_green))
			Commands.notice(channel, color(f'Time to FUCKING toke in {chan.upper()}, type !toke to join', light_green))
			time.sleep(10)
			Commands.sendmsg(channel, color('OH SHIT we toke in 20 get ready ' + ' '.join(Bot.nicks), light_green))
			time.sleep(10)
			Commands.sendmsg(channel, color('OH SHIT we toke in 10 get ready ' + ' '.join(Bot.nicks), light_green))
			time.sleep(5)
			Commands.sendmsg(channel, color('alright toke in 5', light_green))
			time.sleep(1)
			Commands.sendmsg(channel, color('4..', light_green))
			time.sleep(1)
			Commands.sendmsg(channel, color('3..', light_green))
			time.sleep(1)
			Commands.sendmsg(channel, color('2..', light_green))
			time.sleep(1)
			Commands.sendmsg(channel, color('1..', light_green))
			time.sleep(1)
			Commands.sendmsg(channel, color(' '.join(Bot.nicks) + ' .. toke!', light_green))
		except Exception as ex:
			error('Error occured in toke event!', ex)
		finally:
			Bot.event = None
			Bot.nicks = list()

class Generate:
	def beer():
		glass = color(' ', light_grey, light_grey)
		return glass + color(''.join(random.choice(('       :.')) for _ in range(9)), orange, yellow) + glass

	def cigarette(size):
		filter    = color(';.`-,:.`;', yellow, orange)
		cigarette = color('|'*size, light_grey, white)
		cherry_a  = color(random.choice(('@#&')), random.choice((red,yellow)), grey)
		cherry_b  = color(random.choice(('@#&')), random.choice((red,yellow)), grey)
		smoke     = color('-' + ''.join(random.choice((';:-.,_`~\'')) for _ in range(random.randint(5,8))), grey)
		return filter + cigarette + cherry_a + cherry_b + smoke

	def joint(size):
		joint    = color('/'*size, light_grey, white)
		cherry_a = color(random.choice(('@#&')), random.choice((green,red,yellow)), grey)
		cherry_b = color(random.choice(('@#&')), random.choice((green,red,yellow)), grey)
		smoke    = color('-' + ''.join(random.choice((';:-.,_`~\'')) for _ in range(random.randint(5,8))), grey)
		return joint + cherry_a + cherry_b + smoke

	def mug(size):
		glass  = color(' ', light_grey, light_grey)
		empty  = f'{glass}         {glass}'
		foam   = glass + color(':::::::::', light_grey, white) + glass
		bottom = color('           ', light_grey, light_grey)
		mug   = [foam,Generate.beer(),Generate.beer(),Generate.beer(),Generate.beer(),Generate.beer(),Generate.beer(),Generate.beer()]
		for i in range(8-size):
			mug.pop()
			mug.insert(0, empty)
		for i in range(len(mug)):
			if i == 2 or i == 7:
				mug[i] += glass + glass
			elif i > 2 and i < 7:
				mug[i] += '  ' + glass
		mug.append(bottom)
		return mug

# Main
if use_ssl:
	import ssl
if not os.path.isfile(stat_file):
	open(stat_file, 'w').write('0:0:0')
Bot = IRC()
Bot.run()
