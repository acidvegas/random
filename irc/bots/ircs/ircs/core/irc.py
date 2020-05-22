#!/usr/bin/env python
# IRC Services (IRCS) - Developed by acidvegas in Python (https://acid.vegas/ircs)
# irc.py

import socket
import ssl
import time

import config
import debug
from functions import Database, ChanServ, HostServ

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

class IRC(object):
    server       = config.server
    port         = config.port
    use_ipv6     = config.use_ipv6
    use_ssl      = config.use_ssl
    vhost        = config.vhost
    password     = config.password
    nickname     = config.nickname
    username     = config.username
    realname     = config.realname
    oper_passwd  = config.oper_passwd
    admin_host   = config.admin_host

    def __init__(self):
        self.husers = list()
        self.last   = dict()
        self.sock   = None

    def action(self, chan, msg):
        self.sendmsg(chan, '\x01ACTION {0}\x01'.format(msg))

    def chghost(self, nick, host):
        self.raw('CHGHOST {0} {1}'.format(nick, host))

    def color(self, msg, foreground, background=None):
        if background:
            return '\x03{0},{1}{2}{3}'.format(foreground, background, msg, reset)
        else:
            return '\x03{0}{1}{2}'.format(foreground, msg, reset)

    def connect(self):
        try:
            self.create_socket()
            self.sock.connect((self.server, self.port))
            if self.password:
                self.raw('PASS ' + self.password)
            self.raw('USER {0} 0 * :{1}'.format(self.username, self.realname))
            self.raw('NICK ' + self.nickname)
        except socket.error as ex:
            debug.error('Failed to connect to IRC server.', ex)
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

    def error(self, target, msg, reason=None):
        if reason:
            self.sendmsg(target, '[{0}] {1} {2}'.format(self.color('ERROR', red), msg, self.color('({0})'.format(str(reason)), grey)))
        else:
            self.sendmsg(target, '[{0}] {1}'.format(self.color('ERROR', red), msg))

    def event_connect(self):
        self.mode(self.nickname, '+Bd')
        self.oper(self.username, self.oper_passwd)
        if Database.check():
            for channel in ChanServ.channels():
                self.join(channel)
        else:
            Database.create()

    def event_connection(self, nick, ident):
        vhost = HostServ.get_vhost(ident, True)
        if vhost:
            self.chghost(nick, vhost)

    def event_disconnect(self):
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_end_of_who(self):
        if self.last['cmd'] == 'husers':
            if self.husers:
                self.sendmsg(self.last['nick'], '{0} {1}'.format(self.color('Total:', light_blue), self.color(len(self.husers), grey)))
            else:
                self.error(self.last['nick'], 'No hidden users found.')

    def event_join(self, nick, ident, chan):
        mode = ChanServ.get_mode(chan, ident)
        if mode:
            self.mode(chan, '+{0} {1}'.format(mode, nick))

    def event_kick(self, chan, kicked):
        if kicked == self.nickname:
            if chan in Database.channels():
                self.join(chan)

    def event_nick_in_use(self):
        debug.error_exit('IRCS is already running.')

    def event_notice(self, nick, data):
        if '.' in nick or nick == self.server:
            args = data.split()
            if 'Client connecting' in data:
                nick  = args[6]
                ident = args[7][1:][:-1]
                self.event_connection(nick, ident)

    def event_private(self, nick, ident, msg):
        try:
            args = msg.split()
            cmd  = args[0][1:]
            host = ident.split('@')[1]
            if cmd == 'husers' and host == self.admin_host:
                if len(args) == 1:
                    self.husers = list()
                    self.last   = {'nick':nick,'cmd':'husers'}
                    self.who('I', '*')
                elif len(args) == 2:
                    if args[1] == 'kill':
                        if self.husers:
                            self.action(nick, 'Killing all hidden users...')
                            for item in self.husers:
                                self.kill(item['nick'], 'Killed by IRCS anti-bot protection.')
                        else:
                            self.error(nick, 'Hidden users list is empty.', 'Make sure you run !husers first')
                    elif args[1] == 'gzline':
                        if self.husers:
                            self.action(nick, 'Z:Lining all hidden users...')
                            for item in self.husers:
                                self.gzline(item['host'], '1d', 'Banned by IRCS anti-bot protection.')
                        else:
                            self.error(nick, 'Hidden users list is empty.', 'Make sure you run !husers first')
                elif len(args) == 3:
                    if args [1] == 'join':
                        channel = args[2]
                        if channel.startswith('#') and len(channel) <= 20:
                            if self.husers:
                                self.action(nick, 'Joining all hidden users to {0}...'.format(channel))
                                for item in self.husers:
                                    self.sajoin(item['nick'], channel)
                            else:
                                self.error(nick, 'Hidden users list is empty.', 'Make sure you run !husers first')
                        else:
                            self.error(nick, 'Invalid arguments.')
                    else:
                        self.error(nick, 'Invalid arguments.')
                else:
                    self.error(nick, 'Invalid arguments.')
            elif cmd == 'mode':
                if len(args) > 1:
                    channel = args[1]
                    if channel[:1] == '#' and len(channel) <= 20 and debug.check_data(channel):
                        if ChanServ.get_mode(channel, ident) == 'q' or host == self.admin_host:
                            if len(args) == 2:
                                if channel in ChanServ.channels():
                                    data = ChanServ.read(channel)
                                    self.sendmsg(nick, '[{0}]'.format(self.color(channel, purple)))
                                    for row in data:
                                        self.sendmsg(nick, '{0} | {1}'.format(self.color('+' + row[1], grey), self.color(row[0], yellow)))
                                    self.sendmsg(nick, '{0} {1}'.format(self.color('Total:', light_blue), self.color(len(data), grey)))
                                else:
                                    self.error(nick, self.color(channel, purple) + ' does not exist.')
                            elif len(args) == 3:
                                if args[2] in ('a','h','o','v','q'):
                                    if channel in ChanServ.channels():
                                        mode = args[2]
                                        data = ChanServ.read(channel, mode)
                                        if data:
                                            self.sendmsg(nick, '[{0}] {1}'.format(self.color(channel, purple) , self.color('(+{0})'.format(mode), grey)))
                                            for row in data:
                                                self.sendmsg(nick, self.color(row[0], yellow))
                                            self.sendmsg(nick, '{0} {1}'.format(self.color('Total:', light_blue), self.color(len(data), grey)))
                                        else:
                                            self.error(nick, self.color('+{0}'.format(mode), grey) + ' is empty.')
                                    else:
                                        self.error(nick, self.color(channel, purple) + ' does not exist.')
                                else:
                                    self.error(nick, 'Invalid arguments.')
                            elif len(args) == 4:
                                if args[2] in ('a','h','o','v','q') and args[3][:1] in '+-' and len(args[3]) <= 63 and debug.check_data(args[3]):
                                    mode = args[2]
                                    if mode == 'q' and host != self.admin_host:
                                        self.error(nick, 'You do not have permission to change this mode.')
                                    else:
                                        action = args[3][:1]
                                        ident  = args[3][1:]
                                        if action == '+':
                                            if not ChanServ.get_mode(channel, ident):
                                                ChanServ.add_mode(channel, ident, mode)
                                                self.sendmsg(nick, '{0} {1} has been {2} to the {3} database.'.format(self.color(ident, light_blue), self.color('(+{0})'.format(mode), grey), self.color('added', green), self.color(channel, purple)))
                                            else:
                                                self.error(nick, '{0} already exists in the {1} database.'.format(self.color(ident, light_blue), self.color(channel, purple)))
                                        elif action == '-':
                                            if ChanServ.get_mode(channel, ident):
                                                ChanServ.del_mode(channel, ident)
                                                self.sendmsg(nick, '{0} {1} has been {2} from the {3} database.'.format(self.color(ident, light_blue), self.color('(+{0})'.format(mode), grey), self.color('removed', red), self.color(channel, purple)))
                                            else:
                                                self.error(nick, '{0} does not exist in the {1} database.'.format(self.color(ident, light_blue), self.color(channel, purple)))
                                else:
                                    self.error(nick, 'Invalid arguments.')
                            else:
                                self.error(nick, 'Invalid arguments.')
                        else:
                            self.error(nick, 'You do not have permission to use this command.')
                    else:
                        self.error(nick, 'Invalid arguments.')
                else:
                    self.error(nick, 'Invalid arguments.')
            elif cmd == 'sync':
                if len(args) == 2:
                    channel = args[1]
                    if channel[:1] == '#' and len(channel) <= 20 and debug.check_data(channel):
                        if channel in ChanServ.channels():
                            if ChanServ.get_mode(channel, ident) == 'q' or host == self.admin_host:
                                self.action(nick, 'Syncing all modes in {0}...'.format(color(channel, purple)))
                                self.last['cmd'] = 'sync ' + channel
                                self.who('h', '*')
                            else:
                                self.error(nick, 'You do not have permission to use this command.')
                        else:
                            self.error(nick, '{0} does not exist.'.format(color(channel, purple)))
                    else:
                        self.error(nick, 'Invalid arguments.')
                else:
                    self.error(nick, 'Invalid arguments.')
            elif cmd == 'vhost':
                if len(args) == 2:
                    if args[1] == 'list':
                        if host == self.admin_host:
                            vhosts = HostServ.read()
                            if vhosts:
                                self.sendmsg(nick, '[{0}]'.format(self.color('Registered Vhosts', purple)))
                                for vhost in vhosts:
                                    self.sendmsg(nick, '{0} {1}'.format(self.color(vhost[0], yellow), self.color('({0})'.format(vhost[1]), grey)))
                                self.sendmsg(nick, '{0} {1}'.format(self.color('Total:', light_blue), self.color(len(vhosts), grey)))
                            else:
                                self.error(nick, 'Vhost list is empty.')
                        else:
                            self.error(nick, 'You do not have permission to use this command.')
                    elif args[1] == 'off':
                        status = HostServ.get_status(ident)
                        if status == 'off':
                            self.error(nick, 'VHOST is already turned off.')
                        elif status == 'on':
                            HostServ.set_status(ident, 'off')
                            self.sendmsg(nick, 'VHOST has been turned ' + color('off', red))
                        else:
                            self.error(nick, 'You do not have a registered VHOST.')
                    elif args[1] == 'on':
                        status = HostServ.get_status(ident)
                        if status == 'off':
                            HostServ.set_status(ident, 'on')
                            self.sendmsg(nick, 'VHOST has been turned ' + color('on', green))
                        elif status == 'on':
                            self.error(nick, 'Your VHOST is already turned on.')
                        else:
                            self.error(nick, 'You do not have a registered VHOST.')
                    elif args[1] == 'sync':
                        vhost = HostServ.get_vhost(ident)
                        if host == vhost:
                            self.error(nick, 'Your VHOST is already synced and working.')
                        elif vhost:
                            self.action(nick, 'Syncing VHOST...')
                            self.chghost(nick, vhost)
                        else:
                            self.error(nick, 'You do not have a registered VHOST.')
                elif len(args) == 3:
                    if args[1] == 'drop':
                        if host == self.admin_host:
                            ident = args[2]
                            if ident in HostServ.idents():
                                HostServ.delete(ident)
                                self.sendmsg(nick, '{0} has been {1} from the vhost database.'.format(self.color(ident, light_blue), self.color('removed', red)))
                            else:
                                self.error(nick, '{0} does not have a vhost.'.format(self.color(ident, light_blue)))
                        else:
                            self.error(nick, 'You do not have permission to use this command.')
                elif len(args) == 4:
                    if args[1] == 'add':
                        if host == self.admin_host:
                            ident = args[2]
                            vhost = args[3]
                            if ident not in HostServ.idents():
                                HostServ.add(ident, vhost)
                                self.sendmsg(nick, '{0} has been {1} from the database.'.format(self.color(ident, light_blue), self.color('added', green)))
                            else:
                                self.error(nick, '{0} is already registered.'.format(color(ident, light_blue)))
                        else:
                            self.error(nick, 'You do not have permission to use this command.')
                    else:
                        self.error(nick, 'Invalid arguments.')
                else:
                    self.error(nick, 'Invalid arguments.')
        except Exception as ex:
            self.error(nick, 'Unexpected error has occured.', ex)

    def event_who(self, chan, user, host, nick):
        if self.last:
            if self.last['cmd'] == 'husers':
                if chan == '*':
                    self.husers.append({'user':user,'host':host,'nick':nick})
                    self.sendmsg(self.last['nick'], '{0} {1}'.format(self.color(nick, yellow), self.color('({0}@{1})'.format(user, host), grey)))
            elif self.last['cmd'].startswith('sync'):
                channel = self.last['cmd'].split()[1]
                if chan == channel:
                    mode = ChanServ.mode(chan, '{0}@{1]'.format(user, host))
                    if mode:
                        self.mode(chan, '+{0} {1}'.format(mode, nick))

    def gzline(self, host, duration, msg):
        self.raw('gzline *@{1} {2} {3}'.format(user, host, duration, msg))

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '315':
           self.event_end_of_who()
        elif args[1] == '352':
            chan = args[3]
            user = args[4]
            host = args[5]
            nick = args[7]
            self.event_who(chan, user, host, nick)
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == 'NOTICE':
            nick = args[0][1:]
            self.event_notice(nick, data)
        elif args[1] in ('JOIN','KICK','PRIVMSG'):
            nick = args[0].split('!')[0][1:]
            if nick != self.nickname:
                chan = args[2]
                if args[1] == 'JOIN':
                    host = args[0].split('!')[1]
                    self.event_join(nick, host, chan[1:])
                elif args[1] == 'KICK':
                    kicked = args[3]
                    self.event_kick(chan, kicked)
                elif args[1] == 'PRIVMSG':
                    ident = args[0].split('!')[1]
                    msg   = data.split('{0} PRIVMSG {1} :'.format(args[0], chan))[1]
                    if msg.startswith('!'):
                        if chan == self.nickname:
                            self.event_private(nick, ident, msg)

    def join(self, chan):
        self.raw('JOIN ' + chan)
        self.mode(chan, '+q ' + self.nickname)

    def kill(self, nick, reason):
        self.raw('KILL {0} {1}'.format(nick, reason))

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in (line for line in data.split('\r\n') if line):
                        debug.irc(line)
                        if line.startswith('ERROR :Closing Link:'):
                            raise Exception('Connection has closed.')
                        elif len(line.split()) >= 2:
                            self.handle_events(line)
                else:
                    debug.error('No data recieved from server.')
                    break
            except (UnicodeDecodeError,UnicodeEncodeError):
                debug.error('Unicode error has occured.')
            except Exception as ex:
                debug.error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def mode(self, target, mode):
        self.raw('MODE {0} {1}'.format(target, mode))

    def oper(self, nick, password):
        self.raw('OPER {0} {1}'.format(nick, password))

    def part(self, chan, msg):
        self.raw('PART {0} {1}'.format(chan, msg))

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sajoin(self, nick, chan):
        self.raw('SAJOIN {0} {1}'.format(nick, chan))

    def sendmsg(self, target, msg):
        self.raw('PRIVMSG {0} :{1}'.format(target, msg))

    def who(self, flag, args):
        self.raw('who +{0} {1}'.format(flag, args))

IRCS = IRC()