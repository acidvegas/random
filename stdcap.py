#!/usr/bin/env python
# CoinMarketCap Standard Deviation - Developed by acidvegas in Python (https://acid.vegas/random)

'''
The script will calculate the mean, median, mode, high, low & std for the entire cryptocurrency market over the last 7 days.

API Documentation:
	https://coinmarketcap.com/api/
'''

import datetime
import http.client
import json
import math
import time
import statistics

class CoinMarketCap(object):
	def __init__(self):
		self.cache = {'ticker':{'BTC':{'last_updated':0}}}

	def _ticker(self):
		conn = http.client.HTTPSConnection('api.coinmarketcap.com')
		conn.request('GET', '/v1/ticker/?limit=0')
		data = json.loads(conn.getresponse().read().replace(b': null', b': "0"'))
		conn.close()
		return data

	def _markets():
		conn = http.client.HTTPSConnection('s2.coinmarketcap.com')
		conn.request('GET', '/generated/search/quick_search.json')
		data = json.loads(conn.getresponse().read())
		conn.close()
		results = dict()
		for item in data:
			results[item['id']] = item['name']
		return results

	def _graph(self, name, start_time, end_time):
		conn = http.client.HTTPSConnection('graphs2.coinmarketcap.com', timeout=60)
		conn.request('GET', f'/currencies/{name}/{start_time}/{end_time}/')
		return json.loads(conn.getresponse().read())

def generate_table(data):
	matrix = dict()
	keys = data[0].keys()
	for item in keys:
		matrix[item] = list()
	del keys
	for item in data:
		for subitem in item:
			matrix[subitem].append(item[subitem])
	for item in matrix:
		matrix[item] = len(max(matrix[item], key=len))
	columns = [item.ljust(matrix[item]) for item in matrix.keys()]
	print('   '.join(columns))
	del columns
	for item in data:
		row_columns = [item[subitem].ljust(matrix[subitem]) for subitem in item]
		print(' | '.join(row_columns))

def stddev(data):
	n = len(data)
	if n <= 1:
		return 0.0
	mean = avg_calc(data)
	sd = 0.0
	for el in data:
		sd += (float(el)-mean)**2
	sd = math.sqrt(sd/float(n-1))
	return sd

def avg_calc(ls):
	n = len(ls)
	mean = 0.0
	if n <= 1:
		return ls[0]
	for el in ls:
		mean = mean+float(el)
	mean = mean/float(n)
	return mean

def get_data(coin, start_time, end_time):
	try:
		time.sleep(4)
		data = [item[1] for item in CMC._graph(coin, start_time, end_time)['price_usd']]
		return {'name':coin,'mean':f'{sum(data)/len(data):.2f}','median':f'{statistics.median(data):.2f}','mode':f'{max(set(data),key=data.count):.2f}','high':f'{max(data):.2f}','low':f'{min(data):.2f}','std':f'{stddev(data):.2f}'}
	except:
		return {'name':'none','mean':'none','median':'none','mode':'none','high':'none','low':'none','std':'0'}

CMC         = CoinMarketCap()
ticker_data = CMC._ticker()
start_time  = int((datetime.datetime.now()-datetime.timedelta(days=180)).timestamp()*1000)
end_time    = int(datetime.datetime.now().timestamp()*1000)
coins       = [item['id'] for item in ticker_data][:10]
data        = [get_data(coin, start_time, end_time) for coin in coins]
data        = sorted(data, key=lambda k: float(k['std']), reverse=True)
generate_table(data)
size=len(CMC._graph('bitcoin', start_time, end_time)['price_usd'])
print('Spread acrosss 7 days - ' + str(size) + ' points')