# Netspliter EFKnockr Config Generator
# Developed by acidvegas in Python 3
# http://github.com/acidvegas/random
# netsplitter_efknockr_conf_gen.py
import os, sqlite3
db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'netsplit.db')
db      = sqlite3.connect(db_file)
sql     = db.cursor()
servers = list()
def read()     : return sql.execute('SELECT NAME,ADDRESS,PORT,SSL FROM SERVERS ORDER BY NAME ASC').fetchall()
with open('config.py', mode='w', encoding='utf-8') as config_file:
    for server in read():
        name, address, port, ssl = server
        if name not in servers:
            if ssl : config_file.write("    '%s' : {'port':%d, 'ipv6':False, 'ssl':True, 'password':None, 'channels':None},\n"  % (address, port))
            else   : config_file.write("    '%s' : {'port':%d, 'ipv6':False, 'ssl':False, 'password':None, 'channels':None},\n" % (address, port))
            servers.append(name)