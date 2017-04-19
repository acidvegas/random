#!/usr/bin/env python
# HUGECOCK (as seen in #efnetnews)
# Developed by acidvegas/vap0r in Python 3
# https://github.com/acidvegas/random
# hugecock.py

'''
Patreon : https://www.patreon.com/efnetnews
Twitter : https://twitter.com/pp4l
YouTube : https://www.youtube.com/channel/UCrB3e00DBKTyVhGLrrGuhOw
'''

import os
import random
import socket
import ssl
import time
import threading

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None
channel  = '#efnetnews'
key      = None

# Identity
nickname = 'HUGECOCK'
username = 'HUGECOCK'
realname = 'HUGECOCK'

# Globals (DO NOT EDIT)
random_file  = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'random.txt')
random_lines = []

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

def debug(msg):
    print('{0} | [~] - {1}'.format(get_time(), msg))

def error(msg, reason=None):
    if reason:
        print('{0} | [!] - {1} ({2})'.format(get_time(), msg, str(reason)))
    else:
        print('{0} | [!] - {1}'.format(get_time(), msg))

def get_time():
    return time.strftime('%I:%M:%S')

class IRC(object):
    server      = server
    port        = port
    use_ipv6    = use_ipv6
    use_ssl     = use_ssl
    vhost       = vhost
    password    = password
    channel     = channel
    key         = key
    username    = username
    realname    = realname

    def __init__(self):
        self.nickname  = nickname
        self.connected = False
        self.last_time = 0
        self.sock      = None

    def action(self, chan, msg):
        self.sendmsg(chan, '\x01ACTION {0}\x01'.format(msg))

    def color(self, msg, foreground, background=None):
        if background:
            return '\x03{0},{1}{2}'.format(foreground, background, msg)
        else:
            return '\x03{0}{1}'.format(foreground, msg)

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((self.server, self.port))
            if self.password:
                self.raw('PASS ' + self.password)
            self.raw('USER {0} 0 * :{1}'.format(self.username, self.realname))
            self.nick(self.nickname)
        except socket.error as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if self.use_ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.vhost:
            self.sock.bind((self.vhost, 0))
        if self.use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def ctcp(self, target, data):
        self.sendmsg(target, '\001{0}\001'.format(data))

    def event_connect(self):
        self.connected = True
        self.join(self.channel, self.key)
        threading.Thread(target=self.loop).start()

    def event_disconnect(self):
        self.connected = False
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_join(self, nick, chan):
        if nick.lower() == 'zardoz':
            self.sendmsg(chan, nick)
        self.notice(nick, 'Thank you for joining EFNETNEWS, you have 3 memos waiting. Please type * /server MemoServ read * to check your messages.')

    def event_kick(self, nick, chan, kicked):
        if kicked == self.nickname and chan == self.channel:
            time.sleep(3)
            self.join(self.channel, self.key)

    def event_message(self, nick, chan, msg):
        if random.choice((True,False,False,False)):
            if 'http://' in msg or 'https://' in msg or 'www.' in msg:
                self.sendmsg(chan, underline + 'not clicking')
            elif msg == 'h':
                self.sendmsg(chan, 'h')
            elif msg == 'pump':
                self.sendmsg(chan, 'penis')
            elif msg == 'penis':
                self.sendmsg(chan, 'pump')
            elif 'ddos' in msg:
                self.sendmsg(chan, 'Dudes Drink Owl Sperm')
            elif 'fag' in msg:
                self.sendmsg(chan, 'i hate faggots more than i hate war in this world')
            elif self.nickname in msg:
                self.action(chan, '8=================================================================D')
            elif msg.lower() == 'lol':
                self.sendmsg(chan, 'lol')
            elif msg == '%%':
                self.sendmsg(chan, '%%')
            elif 'supernets' in msg.lower():
                self.sendmsg(chan, self.color('HAVE YOU HEARD ABOUT IRC.SUPERNETS.ORG ???', light_blue))
            elif 'readerr' in msg.lower():
                if random.choice((True,False)):
                    self.sendmsg(chan, 'can we kill ReadErr')
                else:
                    self.sendmsg(chan, 'can we ban ReadErr')

    def event_nick_in_use(self):
        self.nickname = self.nickname + '_'
        self.nick(self.nickname)

    def event_part(self, nick, chan):
        self.sendmsg(nick, 'bet u wont come back pussy')
        self.sendmsg(chan, self.color('EMOPART DETECTED', red, yellow))

    def event_quit(self, nick):
        if time.time() - self.last_time > 15:
            self.nick(nick)
            self.nickname = nick
            self.sendmsg(self.channel, 'GOT EEEEEm')
            self.last_time = time.time()

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] in (''JOIN','KICK','PART','PRIVMSG','QUIT'):
            nick  = args[0].split('!')[0][1:]
            ident = args[0].split('!')[1] # Not used, but this is the user@host of the nick.
            if nick != self.nickname:
                if args[1] == 'JOIN':
                    chan = args[2][1:]
                    self.event_join(nick, chan)
                elif args[1] == 'KICK':
                    chan   = args[2]
                    kicked = args[3]
                    self.event_kick(nick, chan, kicked)
                elif args[1] == 'PART':
                    chan = args[2]
                    self.event_part(nick, chan)
                elif args[1] == 'PRIVMSG':
                    chan = args[2]
                    msg  = data.split('{0} PRIVMSG {1} :'.format(args[0], chan))[1]
                    if chan != self.nickname
                        self.event_message(nick, chan, msg)
                elif args[1] == 'QUIT':
                    self.event_quit(nick)

    def join(self, chan, key=None):
        if key:
            self.raw('JOIN {0} {1}'.format(chan, key))
        else:
            self.raw('JOIN ' + chan)

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in (line for line in data.split('\r\n') if line):
                        debug(line)
                        if line.startswith('ERROR :Closing Link:'):
                            raise Exception('Connection has closed.')
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    error('No data recieved from server.')
                    break
            except (UnicodeDecodeError,UnicodeEncodeError):
                error('Unicode error has occured.')
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def loop(self):
        while self.connected:
            try:
                time.sleep(60 * random_int(20,60))
                self.sendmsg(self.channel, random.choice(random_lines))
            except Exception as ex:
                error('Error occured in the loop!', ex)
                break

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def notice(self, target, msg):
        self.raw('NOTICE {0} :{1}'.format(target, msg))

    def part(self, chan, msg=None):
        if msg:
            self.raw('PART {0} {1}'.format(chan, msg))
        else:
            self.raw('PART ' + chan)

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw('PRIVMSG {0} :{1}'.format(target, msg))

# Main
if os.path.isfile(random_file):
    with open(random_file, mode='r', encoding='utf8', errors='replace') as random__file:
        lines = random__file.read().splitlines()
        for line in [x for x in lines if x]:
            random_lines.append(line)
    IRC().connect()
else:
    error_exit('Missing random file!')
