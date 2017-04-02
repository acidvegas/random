#!/usr/bin/env python
# IRC Class
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/random
# blackhole.py

import socket
import ssl
import time

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None

# Identity
nickname = 'blackhole'
username = 'blackhole'
realname = 'ENTER THE VOID'

# Login
nickserv    = None
oper_passwd = 'CHANGEME'

# Message
kick_message = 'ENTER THE VOID'
kill_message = 'ENTER THE VOID'

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
    def __init__(self):
        self.sock = None

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((server, port))
            if password:
                self.raw('PASS ' + password)
            self.raw('USER {0} 0 * :{1}'.format(username, realname))
            self.nick(nickname)
        except socket.error as ex:
            error('Failed to connect to IRC server.', ex)
            self.event_disconnect()
        else:
            self.listen()

    def create_socket(self):
        if use_ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if vhost:
            self.sock.bind((vhost, 0))
        if use_ssl:
            self.sock = ssl.wrap_socket(self.sock)

    def event_connect(self):
        if nickserv:
            self.identify(username, nickserv)
        if oper_passwd:
            self.oper(username, oper_passwd)

    def event_disconnect(self):
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_kick(self, nick, chan, kicked):
        if kicked == nickname:
            self.join(chan)

    def event_message(self, nick, chan, msg):
        if nickname in msg:
            self.kick(chan, nick, 'ENTER THE VOID')

    def event_nick_in_use(self):
        error('The bot is already running or nick is in use.')

    def event_private(self, nick, msg):
        self.kill(nick, 'ENTER THE VOID')

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == 'KICK':
            nick  = args[0].split('!')[0][1:]
            chan  = args[2]
            kicked = args[3]
            self.event_kick(nick, chan, kicked)
        elif args[1] == 'PRIVMSG':
            nick  = args[0].split('!')[0][1:]
            if nick != nickname:
                chan = args[2]
                msg  = data.split('{0} PRIVMSG {1} :'.format(args[0], chan))[1]
                if chan == nickname:
                    self.event_private(nick, msg)
                else:
                    self.event_message(nick, chan, msg)

    def identify(self, username, password):
        self.sendmsg('nickserv', 'identify {0} {1}'.format(username, password))

    def kick(self, chan, nick, reason):
        self.raw('KICK {0} {1} :{2}'.format(chan, nick, reason))

    def kill(self, nick, reason):
        self.raw('KILL {0} {1}'.format(nick, reason))

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

    def nick(self, nick):
        self.raw('NICK ' + nick)

    def oper(self, nick, password):
        self.raw('OPER {0} {1}'.format(nick, password))

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw('PRIVMSG {0} :{1}'.format(target, msg))

IRC().connect()