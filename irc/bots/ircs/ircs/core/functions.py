#!/usr/bin/env python
# IRC Services (IRCS) - Developed by acidvegas in Python (https://acid.vegas/ircs)
# functions.py

import inspect
import os
import sqlite3
import string

# Database
database_dir  = os.path.join(os.path.dirname(os.path.realpath(inspect.stack()[-1][1])), 'data')
database_file = os.path.join(database_dir, 'ircs.db')

# Globals
db  = sqlite3.connect(database_file)
sql = db.cursor()

class Database:
    def check():
        tables = sql.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()
        if len(tables):
            return True
        else:
            return False

    def create():
        sql.execute('CREATE TABLE CHANSERV (CHANNEL TEXT NOT NULL, IDENT TEXT NOT NULL, MODE TEXT NOT NULL);')
        sql.execute('CREATE TABLE HOSTSERV (IDENT TEXT NOT NULL, VHOST TEXT NOT NULL, STATUS TEXT NOT NULL);')
        db.commit()



class ChanServ:
    def add_mode(chan, ident, mode):
        sql.execute('INSERT INTO CHANSERV (CHANNEL,IDENT,MODE) VALUES (?, ?, ?)', (chan, ident, mode))
        db.commit()

    def channels():
        return set(list(item[0] for item in sql.execute('SELECT CHANNEL FROM CHANSERV ORDER BY CHANNEL ASC').fetchall()))

    def del_mode(chan, ident):
        sql.execute('DELETE FROM CHANSERV WHERE CHANNEL=? AND IDENT=?', (chan, ident))
        db.commit()

    def drop(chan):
        sql.execute('DELETE FROM CHANSERV WHERE CHANNEL=?', (chan,))
        db.commit()

    def get_mode(chan, ident):
        data = sql.execute('SELECT MODE FROM CHANSERV WHERE CHANNEL=? AND IDENT=?', (chan, ident)).fetchone()
        if data:
            return data[0]
        else:
            return None

    def hosts():
        return set(list(item[0].split('@')[1] for item in sql.execute('SELECT IDENT FROM CHANSERV', (channel,)).fetchall()))

    def idents(chan, mode=None):
        if mode:
            return list(item[0] for item in sql.execute('SELECT IDENT FROM CHANSERV WHERE CHANNEL=? AND MODE=?', (channel, mode)).fetchall())
        else:
            return list(item[0] for item in sql.execute('SELECT IDENT FROM CHANSERV WHERE CHANNEL=?', (channel,)).fetchall())

    def read(channel, mode=None):
        if mode:
            return sql.execute('SELECT IDENT FROM CHANSERV WHERE CHANNEL=? AND MODE=? ORDER BY CHANNEL ASC, MODE ASC, IDENT ASC', (channel, mode)).fetchall()
        else:
            return sql.execute('SELECT IDENT,MODE FROM CHANSERV WHERE CHANNEL=? ORDER BY CHANNEL ASC, MODE ASC, IDENT ASC', (channel,)).fetchall()



class HostServ:
    def add(ident, vhost):
        sql.execute('INSERT INTO HOSTSERV (IDENT,VHOST,STATUS) VALUES (?, ?, \'pending\')', (ident, vhost))
        db.commit()

    def delete(ident):
        sql.execute('DELETE FROM HOSTSERV WHERE IDENT=?', (ident,))
        db.commit()

    def get_vhost(ident, active=False):
        data = sql.execute('SELECT VHOST FROM HOSTSERV WHERE IDENT=? AND STATUS=\'on\'', (ident,)).fetchone()
        if data:
            return data[0]
        else:
            return None

    def get_status(ident):
        data =  sql.execute('SELECT STATUS FROM HOSTSERV WHERE IDENT=?', (ident,)).fetchone()
        if data:
            return data[0]
        else:
            return None

    def hosts():
        return set(list(item[0].split('@')[1] for item in sql.execute('SELECT IDENT FROM CHANSERV', (channel,)).fetchall()))

    def idents():
        return list(item[0] for item in sql.execute('SELECT IDENT FROM HOSTSERV').fetchall())

    def pending():
        return sql.execute('SELECT IDENT,VHOST FROM HOSTSERV WHERE STATUS=\'pending\' ORDER BY IDENT ASC').fetchall()

    def read():
        return sql.execute('SELECT IDENT,VHOST FROM HOSTSERV ORDER BY IDENT ASC').fetchall()

    def set_status(ident, status):
        sql.execute('UPDATE HOSTSERV SET STATUS=? WHERE IDENT=?', (status, ident))
        db.commit()

    def vhosts():
        return list(item[0] for item in sql.execute('SELECT VHOST FROM HOSTSERV').fetchall())