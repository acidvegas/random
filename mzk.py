#!/usr/bin/env python
# MZK (IRC Music Theory Bot)
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/mzk
# mzk.py

import os
import random
import socket
import ssl
import threading
import time

# Connection
server   = 'irc.server.com'
port     = 6667
use_ipv6 = False
use_ssl  = False
vhost    = None
password = None
channel  = '#music'
key      = None

# Identity
nickname = 'mzk'
username = 'mzk'
realname = 'MZK Music Theory IRC Bot'

# Login
nickserv    = None
oper_passwd = None

# Scale Patterns
scales = {
    'algerian'              : 'w h wh h h wh h',
    'aeolian'               : 'w h w w h w w',
    'blues'                 : 'wh w h h wh w',
    'chromatic'             : 'h h h h h h h',
    'dorian'                : 'w h w w w h w',
    'half_whole_diminished' : 'h w h w h w h w',
    'harmonic_minor'        : 'w h w w h wh h',
    'ionian'                : 'w w h w w w h',
    'locrian'               : 'h w w h w w w',
    'lydian'                : 'w w w h w w h',
    'major'                 : 'w w h w w w h',
    'major_pentatonic'      : 'w w wh w wh',
    'melodic_minor'         : 'w h w w w w h',
    'mixolydian'            : 'w w h w w h w',
    'natural_minor'         : 'w h w w h w w',
    'persian'               : 'h wh h h w wh h',
    'phrygian'              : 'h w w w h w w',
    'whole_half_diminished' : 'w h w h w h w h',
    'whole_tone'            : 'w w w w w w w'
}

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

def error_exit(msg):
    raise SystemExit('{0} | [!] - {1}'.format(get_time(), msg))

def get_time():
    return time.strftime('%I:%M:%S')

def generate_notes(key):
    string_notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    while string_notes[0] != key:
        string_notes.append(string_notes.pop(0))
    return string_notes

def generate_scale(string, scale_notes):
    string_notes = generate_notes(string.upper())
    string_notes.append(string_notes[0])
    for index,note in enumerate(string_notes):
        if note in scale_notes:
            if len(note) == 1:
                string_notes[index] = '--' + string_notes[index] + '--'
            elif len(note) == 2:
                string_notes[index] = '--' + string_notes[index] + '-'
        else:
            string_notes[index] = '-----'
    return string_notes

def scale(type, key):
    notes       = generate_notes(key)
    last        = 0
    scale_notes = [notes[0],]
    for step in scales[type].split():
        if step == 'h':
            last += 1
        elif step == 'w':
            last += 2
        elif step == 'wh':
            last += 3
        if last >= len(notes):
            last = last-len(notes)
        scale_notes.append(notes[last])
    return scale_notes

class IRC(object):
    def __init__(self):
        self.server       = server
        self.port         = port
        self.use_ipv6     = use_ipv6
        self.use_ssl      = use_ssl
        self.vhost        = vhost
        self.password     = password
        self.channel      = channel
        self.key          = key
        self.nickname     = nickname
        self.username     = username
        self.realname     = realname
        self.nickserv     = nickserv
        self.oper_passwd  = oper_passwd
        self.sock         = None

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
            self.raw('NICK '+ self.nickname)
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

    def error(self, chan, msg, reason=None):
        if reason:
            self.sendmsg(chan, '[{0}] {1} {2}'.format(self.color('ERROR', red), msg, self.color('({0})'.format(str(reason)), grey)))
        else:
            self.sendmsg(chan, '[{0}] {1}'.format(self.color('ERROR', red), msg))

    def event_connect(self):
        self.mode(self.nickname, '+Bd')
        if self.nickserv:
            self.identify(self.username, self.nickserv)
        if self.oper_passwd:
            self.oper(self.username, self.oper_passwd)
        self.join(self.channel, self.key)

    def event_disconnect(self):
        self.sock.close()
        time.sleep(10)
        self.connect()

    def event_kick(self, nick, chan, kicked):
        if kicked == self.nickname and chan == self.channel:
            time.sleep(3)
            self.join(chan, self.key)

    def event_message(self, nick, chan, msg):
        if chan == self.channel:
            args = msg.split()
            if msg == '.scales':
                count = 1
                for item in scales:
                    self.sendmsg(chan, '{0} {1}'.format(self.color(str(count) + '.', light_blue), self.color(item, light_green)))
                    count += 1
            elif args[0] == '.scale':
                if len(args) == 3:
                    root = args[1]
                    if root.lower() in ('a','a#','b','c','c#','d','d#','e','f','f#','g','g#'):
                        type = args[2]
                        if type in scales:
                            self.play_scale(chan, root.upper(), type)
                        else:
                            self.error(chan, 'Invalid scale type.')
                    else:
                        self.error(chan, 'Invalid root note.')
                else:
                    self.error(chan, 'Invalid arguments.')

    def event_nick_in_use(self):
        error_exit('MZK is already running.')

    def handle_events(self, data):
        args = data.split()
        if args[0] == 'PING':
            self.raw('PONG ' + args[1][1:])
        elif args[1] == '001':
            self.event_connect()
        elif args[1] == '433':
            self.event_nick_in_use()
        elif args[1] == 'KICK':
            nick   = args[0].split('!')[0][1:]
            chan   = args[2]
            kicked = args[3]
            self.event_kick(nick, chan, kicked)
        elif args[1] == 'PRIVMSG':
            nick  = args[0].split('!')[0][1:]
            chan  = args[2]
            msg   = data.split('{0} PRIVMSG {1} :'.format(args[0], chan))[1]
            self.event_message(nick, chan, msg)

    def identify(self, username, password):
        self.sendmsg('nickserv', 'identify {0} {1}'.format(username, password))

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
                pass
            except Exception as ex:
                error('Unexpected error occured.', ex)
                break
        self.event_disconnect()

    def mode(self, target, mode):
        self.raw('MODE {0} {1}'.format(target, mode))

    def oper(self, nick, password):
        self.raw('OPER {0} {1}'.format(nick, password))

    def play_scale(self, chan, root, type):
        lines = []
        lines.append('  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐')
        line = '0 │  1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │  9  │  10 │  11 │  12 │'
        for i in (' 1 ',' 2 ',' 3 ',' 4 ',' 5 ',' 6 ',' 7 ',' 8 ',' 9 ',' 10 ',' 11 ',' 12 '):
            line = line.replace(i, self.color(i, red))
        lines.append(line)
        lines.append('  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤')
        scale_notes = scale(type, root)
        for string in ('eBGDAE'):
            string_notes = generate_scale(string, scale_notes)
            line = '{0} │{1}│{2}│{3}│{4}│{5}│{6}│{7}│{8}│{9}│{10}│{11}│{12}│'.format(string, string_notes[1], string_notes[2], string_notes[3], string_notes[4], string_notes[5], string_notes[6], string_notes[7], string_notes[8], string_notes[9], string_notes[10], string_notes[11], string_notes[12])
            line = line.replace('-----', self.color('-----', grey))
            for i in ('--A--','--A#-','--B--','--C--','--C#-','--D--','--D#-','--E--','--F--','--F#-','--G--','--G#-'):
                if '#' in i:
                    line = line.replace(i, self.color('--', grey) + self.color(i.replace('-', ''), orange) + self.color('-', grey))
                else:
                    line = line.replace(i, self.color('--', grey) + self.color(i.replace('-', ''), orange) + self.color('--', grey))
                line = line.replace(self.color(root, orange), self.color(root, yellow))
            lines.append(line)
        lines.append('  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘')
        for item in lines:
            self.sendmsg(chan, item)

    def raw(self, msg):
        self.sock.send(bytes(msg + '\r\n', 'utf-8'))

    def sendmsg(self, target, msg):
        self.raw('PRIVMSG {0} :{1}'.format(target, msg))

IRC().connect()