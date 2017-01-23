# Random Name Generator
# Developed by acidvegas in Python 3
# https://github.com/acidvegas/random
# names.py

'''
The script is just an example of how to interact with the `names.db` database.
Compiled in the database is the top 1000 first (male & female) names aand last names.
The names are sorted by its popularity. All data is from http://names.mongabay.com/
'''

import os
import random
import sqlite3

# Data Directory & Files
data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
db_file  = os.path.join(data_dir, 'names.db')

# Controllers
db  = sqlite3.connect(db_file)
sql = db.cursor()

# Globals
male   = list(item[0] for item in sql.execute('SELECT NAME FROM MALE_NAMES').fetchall())
female = list(item[0] for item in sql.execute('SELECT NAME FROM FEMALE_NAMES').fetchall())
last   = list(item[0] for item in sql.execute('SELECT NAME FROM LAST_NAMES').fetchall())

while True:
    gender     = random.choice((male,female))
    first_name = random.choice(gender)
    last_name  = random.choice(last)
    print('{0} {1}'.format(first_name, last_name))
    input('')
