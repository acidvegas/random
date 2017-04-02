# NetSplit Parser
# Developed by acidvegas in Python 3
# http://github.com/acidvegas
# netsplit.py

import os
import re
import sqlite3
import time
import urllib.request

# Settings
throttle = 3

# Globals
db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'netsplit.db')
db      = sqlite3.connect(db_file)
sql     = db.cursor()

def db_add(name, address, port, ssl):
    sql.execute('INSERT INTO SERVERS (NAME,ADDRESS,PORT,SSL) VALUES (\'{0}\', \'{1}\', \'{2}\', \'{3}\')'.format(name, address, port, ssl))
    db.commit()

def db_setup():
    tables = sql.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()
    if len(tables):
        sql.execute('DROP TABLE SERVERS')
    sql.execute('CREATE TABLE SERVERS (NAME TEXT NOT NULL, ADDRESS TEXT NOT NULL, PORT INTEGER NOT NULL, SSL INTEGER NOT NULL);')
    db.commit()

def get_source(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    source  = urllib.request.urlopen(req, timeout=15)
    charset = source.headers.get_content_charset()
    if charset:
        return source.read().decode(charset)
    else:
        return source.read().decode()

# Main
db_setup()
source   = get_source('http://irc.netsplit.de/networks/')
networks = re.findall('<a class=".*?" href="/networks/(.*?)/"', source, re.IGNORECASE|re.MULTILINE)
print('[~] - Found {0} networks on NetSplit.'.format(len(networks)))
for network in networks:
    source  = get_source('http://irc.netsplit.de/networks/status.php?net=' + network)
    source  = source.replace('style=\'color:#666666;\'', '')
    source  = source.replace('&#8203;', '')
    while '  ' in source:
        source  = source.replace('  ', ' ')
    checker = re.findall('<td valign="top">.*?<br>((.*?))</td>', source, re.IGNORECASE|re.MULTILINE)
    if checker:
        servers = re.findall(r'<td valign="top">(.*?)<br>.*?</td><td align=\'center\' valign=\'top\'>(.*?)</td>', source, re.IGNORECASE|re.MULTILINE)
    else:
        servers = re.findall(r'<td valign="top">(.*?)</td><td align=\'center\' valign=\'top\'>(.*?)</td>', source, re.IGNORECASE|re.MULTILINE)
    servers = list(set(servers))
    for server in servers:
        address = server[0].split(':')[0]
        port    = int(server[0].split(':')[1])
        if server[1] == 'off':
            ssl = 0
        else:
            ssl = 1
        db_add(network, address, port, ssl)
        print('{0}{1}:{2}'.format(network.ljust(30), address, port))
    time.sleep(throttle)
