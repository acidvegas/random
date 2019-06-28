# -*- coding: utf-8 -*-
#!/usr/bin/env python
# THEGAME IRC Bot - Developed by acidvegas in Python (https://acid.vegas/random)
import random,socket,ssl,threading,time

# Config
admin_ident       = 'ak!ak@super.nets'
channel           = '#anythinggoes'
nickserv_password = 'CHANGEME'
operator_password = 'CHANGEME'
throttle_msg      = 0.15

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

def color(msg,foreground,background=None):return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'
def error(msg,reason):print(f'{get_time()} | [!] - {msg} ({reason})')
def get_time():return time.strftime('%I:%M:%S')
def random_str(size):return ''.join(random.choice('aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ') for _ in range(size))

class Functions:
	def banana_bomb():
		for i in range(random.randint(5,10)):
			spaces=random.randint(1,120)
			for line in banana_data:
				Bot.sendmsg(channel,' '*spaces+line)

	def chat_rain(amount):
		words = ('ok','tru','same','wow','nice','XD','ok','np','sup','cool','nmu','lol','ah','srry','jk')
		for i in range(amount):
			Bot.sendmsg(channel,' '*random.randint(3,25)+random.choice(words)+' '*random.randint(10,50)+random.choice(words)+' '*random.randint(10,50)+random.choice(words))

	def crab_flood(amount):
		counter=1
		notify=random.randint(100,999)
		if amount>=1000000:
			amount=1000000
			Bot.sendmsg(channel,color('GENTLEMEN! BEHOLD!',red))
			Bot.sendmsg(channel,color('THE MILLION CRAB MARCH!',red))
		for i in range(amount):
			spaces=random.randint(1,120)
			for line in crab_data:
				Bot.sendmsg(channel,' '*spaces+line)
			counter+=1
			if counter==notify:
				spaces=random.randint(1,120)
				Bot.sendmsg(channel,color(' '*spaces+str(i)+' MOTHER FUCKING CRABS !!!',red))
				counter=1

	def grave(nick):
		length=len(nick)
		Bot.sendmsg(channel,color(' '*(length+8),light_blue,light_blue))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('    ',light_blue,light_blue),color(' ',grey,grey),color(' '*length,light_grey,light_grey),color('    ',light_blue,light_blue)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('   ',light_blue,light_blue),color(' ', grey),color(' '*(length+2),light_grey,light_grey),color('   ',light_blue,light_blue)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('   ',light_green,light_green),color(' ', grey),color('R I P'.center(length+2),black,light_grey),color('   ',light_green,light_green)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('   ',green,green),color(' ', grey),color(nick.upper().center(length+2),black,light_grey),color('   ',light_green,light_green)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('   ',green,green),color(' ', grey),color(' '*(length+2),light_grey,light_grey),color('   ',light_green,light_green)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}{4}'.format(color(' ',light_green,light_green),color('  ',green,green),color(' ',grey),color('2018'.center(length+2),black,light_grey),color('   ', light_green,light_green)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}{4}'.format(color('  ',light_green,light_green),color(' ',green,green),color(' ',grey),color(' '*(length+2),light_grey,light_grey),color('   ',light_green,light_green)))
		Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(color('   ',light_green,light_green),color(' ', grey),color(' '*(length+2),light_grey,light_grey),color('   ', light_green,light_green)))

	def rain(word,amount):
		for i in range(amount):
			Bot.sendmsg(channel,' '*random.randint(3,25)+word+' '*random.randint(10,50)+word+' '*random.randint(10,50)+word)

	def rope(length):
		spaces=50
		prev=None
		for i in range(length):
			if random.choice((True,False)):
				if prev!='╱':spaces+=1
				char='╲'
			else:
				if prev!='╲':spaces-=1
				char='╱'
			Bot.sendmsg(channel,' '*spaces+char)
			prev=char
		Bot.sendmsg(channel,' '*(spaces-2)+'(;))')

	def wave(msg,lines,spaces,hilite):
		rainbow=['04','08','09','11','12','13']
		spacer=15
		spaces+=spacer
		toggle=True
		data=list()
		for i in range(lines):
			if hilite:
				Bot.sendmsg(channel,'{0}{1}{2}{3}'.format((Bot.nicks[0]+': ').ljust(spacer),color('░▒▓',rainbow[1]),color(f' {msg} ',rainbow[0],rainbow[1]),color('▓▒░',rainbow[1])))
				Bot.nicks.append(Bot.nicks.pop(0))
			else:
				Bot.sendmsg(channel, '{0}{1}{2}{3}'.format(' '*spacer,color('░▒▓',rainbow[1]),color(f' {msg} ',rainbow[0],rainbow[1]),color('▓▒░',rainbow[1])))
			rainbow.append(rainbow.pop(0))
			if toggle:spacer+=1
			else:spacer-=1
			if spacer==spaces:toggle=False
			elif spacer==15:toggle=True

	def worm(length):
		spacer=random.randint(10,100)
		Bot.sendmsg(channel,'{0}   {1}{2}'.format(' '*spacer,color('░▒▓',pink),color('▓▒░',pink)))
		Bot.sendmsg(channel,'{0}  {1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('  ',black,pink),color('▓▒░',pink)))
		Bot.sendmsg(channel,'{0} {1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('    ',black,pink),color('▓▒░',pink)))
		for i in range(length):
			Bot.sendmsg(channel,'{0}{1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('      ',black,pink),color('▓▒░',pink)))
			if random.choice((True,False)):spacer += 1
			else:spacer-=1
		Bot.sendmsg(channel,'{0} {1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('_  _',black,pink),color('▓▒░',pink)))
		Bot.sendmsg(channel,'{0} {1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('o  o',black,pink),color('▓▒░',pink)))
		Bot.sendmsg(channel,'{0}  {1}{2}{3}'.format(' '*spacer,color('░▒▓',pink),color('  ',black,pink),color('▓▒░',pink)))

class WormNet(threading.Thread):
	def __init__(self):
		self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		threading.Thread.__init__(self)
	def run(self):
		Bot.wormnet=True
		try:
			self.sock.connect(('wormnet1.team17.com',6667))
			self.raw('PASS ELSILRACLIHP')
			self.raw('USER Username hostname servername :48 0 US 3.7.2.1')
			self.raw('NICK SUPERNETS')
			while True:
				data=self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split())>=2):
					Bot.sendmsg_wormnet('raw',cyan,line)
					args=line.split()
					if line.startswith('ERROR :Closing Link:'):raise Exception('Connection has closed.')
					elif args[0]=='PING':self.raw('PONG '+args[1][1:])
					elif args[1]=='001':self.raw('JOIN '+channel)
					elif args[1]=='366':Bot.sendmsg_wormnet('join',green,'Joined #anythinggoes channel!')
		except (UnicodeDecodeError,UnicodeEncodeError):pass
		except Exception as ex:
			Bot.sendmsg_wormnet('error',red,'Unknown error occured!',ex)
			self.sock.close()
			Bot.wormnet=False
			Bot.sendmsg_wormnet('disconnected',red,'Lost connection to the WormNet relay!')
	def raw(self,msg):self.sock.send(bytes(msg+'\r\n','utf-8'))
	def sendmsg(self,target,msg):self.raw(f'PRIVMSG {target} :{msg}')

class IRC(object):
	def __init__(self):
		self.nicks=list()
		self.echo=False
		self.sock=None
		self.wormnet=False

	def connect(self):
		try:
			self.sock=ssl.wrap_socket(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
			self.sock.connect(('irc.supernets.org',6697))
			self.raw(f'USER THEG 0 * :YOU LOST THE GAME')
			self.raw('NICK THEGAME')
			while True:
				data = self.sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					print(f'{get_time()} | [~] - {line}')
					args = line.split()
					if args[0]=='PING':self.raw('PONG '+args[1][1:])
					elif args[1]=='001':
						self.raw('MODE THEGAME +BDd')
						self.sendmsg('NickServ','IDENTIFY THEGAME '+nickserv_password)
						self.raw(f'OPER thegame {operator_password}')
						self.raw('JOIN '+channel)
					elif args[1]=='433':self.raw('NICK THE_GAME_'+str(random.randint(10,99)))
					elif args[1]=='353' and len(args)>=6:self.nicks+=' '.join(args[5:])[2:].split()
					elif args[1]=='JOIN' and len(args)==3:self.raw('NOTICE {0} :Thank you for joining #AnythingGoes, you have {1} memo(s) waiting. Please type /server MemoServ read to check your messages.'.format(args[0].split('!')[0][1:],color(random.randint(1,3),red)))
					elif args[1]=='PART' and len(args)>=3:
						self.sendmsg(args[2],color('EMO-PART DETECTED',red))
						self.sendmsg(args[0].split('!')[0][1:],'bet u wont come back pussy...')
					elif args[1]=='PRIVMSG' and len(args)>=4:
						ident=args[0][1:]
						nick=args[0].split('!')[0][1:]
						chan=args[2]
						msg= ' '.join(args[3:])[1:]
						if chan==channel:self.event_message(ident,nick,chan,msg)
					elif args[1]=='QUIT':Functions.grave(args[0].split('!')[0][1:])
		except(UnicodeDecodeError,UnicodeEncodeError):pass
		except:self.sock.close()
		time.sleep(15)
		self.connect()

	def event_message(self,ident,nick,chan,msg):
		args=msg.split()
		if msg[:1]=='!':
			if msg=='!bananabomb':Functions.banana_bomb()
			elif msg=='!crate':
				for line in crate_data:self.sendmsg(channel,line)
			elif msg=='!echo':
				self.echo=False if self.echo else True
			elif msg=='refresh':
				self.nicks=list()
				self.raw('NAMES #anythinggoes')
			elif msg=='!wormnet' and not self.wormnet and ident==admin_ident:WORMS.start()
			elif msg=='!worms':
				for line in worms_data:self.sendmsg(channel, line)
			elif len(args)==2:
				if args[1].isdigit():
					amount=int(args[1])
					if args[0]=='!chatrain':
						if amount<=100 or ident==admin_ident:Functions.chat_rain(amount)
						else:self.sendmsg(chan,'Max: 100')
					elif msg.startswith('!crabflood'):
						if amount<=10 or ident==admin_ident:Functions.crab_flood(amount)
						else:self.sendmsg(chan,'Max: 10')
					elif msg.startswith('!rope'):
						if amount<=100 or ident==admin_ident:Functions.rope(amount)
						else:self.sendmsg(chan,'Max: 100')
					elif msg.startswith('!worm'):
						if amount<=100 or ident==admin_ident:Functions.worm(amount)
						else:self.sendmsg(chan,'Max: 100')
			elif args[0]=='!rain' and len(args)>=3:
				amount=args[1]
				data=' '.join(args[2:])
				if args[1].isdigit():
					if int(args[1])<=100 or ident==admin_ident:Functions.rain(data,int(args[1]))
					else:self.sendmsg(chan,'Max: 100')
			elif args[0] in ('!wave','!wavehl') and len(args)>=4:
				lines =args[1]
				spaces=args[2]
				data=' '.join(args[3:])
				if lines.isdigit() and spaces.isdigit():
					if int(lines)<=100 or ident==admin_ident:
						if args[0]=='!wave':
							Functions.wave(data,int(lines),int(spaces),False)
						else:
							Functions.wave(data,int(lines),int(spaces),True)
					else:self.sendmsg(chan,'Max: 100')
		elif self.echo:self.sendmsg(chan,msg)

	def raw(self,msg):self.sock.send(bytes(msg+'\r\n','utf-8'))
	def sendmsg(self,target,msg):
		time.sleep(throttle_msg)
		self.raw(f'PRIVMSG {target} :{msg}')
	def sendmsg_wormnet(self,title,title_color,msg,extra=None):
		if extra:self.sendmsg(channel,'[{0}] [{1}] {2} {3}'.format(color('WORMNET',pink),color(title,title_color),msg,color('({0})'.format(extra),grey)))
		else:self.sendmsg(channel,'[{0}] [{1}] {2}'.format(color('WORMNET',pink),color(title,title_color),msg))

# Main
banana_data=open('data/banana.txt').readlines()
crab_data=open('data/crab.txt').readlines()
crate_data=open('data/crate.txt').readlines()
worms_data=open('data/worms.txt').readlines()
Bot=IRC()
WORMS=WormNet()
Bot.connect()
