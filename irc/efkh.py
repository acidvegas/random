#!/usr/bin/env python
# EFKnockr Helper - Developed by acidvegas in Python (https://acid.vegas/random)

import json

_bnc     = list()
_irc     = list()
_unknown = list()

def _parse_data():
	with open('netking.json','r') as _data_file:
		for _line in _data_file:
			_data = json.loads(_line)
			if 'product' in _data:
				if _data['product'] in ('BitlBee IRCd','psyBNC','Minbif','ShroudBNC irc-proxy'):
					_bnc.append(_line)
				else:
					_irc.append(_line)
			else:
				if 'data' in _data:
					if 'bitlbee' in _data['data'].lower() or 'psybnc' in _data['data'].lower() or 'shroudbnc' in _data['data'].lower():
						_bnc.append(_line)
					else:
						if ':***' in _data['data'] or 'Looking up your hostname' in _data['data']:
							_irc.append(_line)
						else:
							if 'PHP Notice' not in _data['data']:
								if 'NOTICE' in _data['data']:
									_irc.append(_line)
								else:
									_unknown.append(_line)
				else:
					_unknown.append(_line)

def _write_data():
	with open('bnc.json','w') as _bnc_file:
		for _line in _bnc:
			_bnc_file.write(_line)
	with open('irc.json','w') as _irc_file:
		for _line in _irc:
			_irc_file.write(_line)
	with open('unknown.json','w') as _unknown_file:
		for _line in _unknown:
			_unknown_file.write(_line)

_parse_data()
_write_data()

print('BNC: ' + str(len(_bnc    )))
print('IRC: ' + str(len(_irc    )))
print('???: ' + str(len(_unknown)))

_ips = list()

def _parse_ips():
    with open('irc.json','r') as _data_file:
        for _line in _data_file:
            _data = json.loads(_line)
            _ips.append(_data['ip_str'])

def _write_ips():
    with open('clean.txt','w') as _clean_file:
        for _line in _ips:
            _clean_file.write(_line + '\n')

_parse_ips()
_ips = sorted(set(_ips))
_write_ips()
