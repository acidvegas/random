#!/usr/bin/env python
# table plotter - developed by acidvegas in python (https://acid.vegas/random)
# tableplot.py

data = {
	'number' : ('1','2','3','4','5'),
	'name'   : ('mark', 'steven', 'fredrick', 'bronzel', 'billy'),
	'race'   : ('simpson', 'WHITE BOI', 'peckerwood', 'bird', 'fartman')
}

def table(data):
	columns = len(data)
	for item in data:
		max(data[item], key=len)
	print('┌' + '─'*amount + '┐')
	print('│ ' + title + ' '*amounnt + ' │ ')
	print('├───────────┼────────────────┼───────┤')

	print('└───────────┴────────────────┴───────┘')