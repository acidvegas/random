#!/usr/bin/env python
# CoinGecko API Class - Developed by acidvegas in Python (https://acid.vegas/coinmarketcap)

'''
API Reference: https://www.coingecko.com/en/api#explore-api
'''

import http.client
import json
import time

class CoinGecko():
	def __init__(self):
		self.cache = dict()
		self.last  = 0

	def api(self, endpoint):
		conn = http.client.HTTPSConnection('api.coingecko.com', timeout=15)
		conn.request('GET', '/api/v3/' + endpoint, headers={'Accept':'application/json',})
		response = conn.getresponse().read().decode('utf-8')
		conn.close()
		return json.loads(response)

	def market(self):
		if time.time() - self.last > 300:
			page = 1
			while True:
				data = self.api('coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=' + str(page) + '&sparkline=true&price_change_percentage=1h%2C24h%2C7d%2C30d%2C1y')
				if not data:
					break
				for coin in data:
					self.cache[coin['symbol']] = {
						'name'       : coin['name'],
						'price'      : coin['current_price'],
						'market_cap' : coin['market_cap'],
						'rank'       : coin['market_cap_rank'],
						'volume'     : coin['total_volume'],
						'change'     : {
							'1h' : coin['price_change_percentage_1h_in_currency'],
							'1d' : coin['price_change_percentage_24h_in_currency'],
							'1w' : coin['price_change_percentage_7d_in_currency'],
							'1m' : coin['price_change_percentage_30d_in_currency'],
							'1y' : coin['price_change_percentage_1h_in_currency']
						}
					}
				page += 1
			self.last = time.time()
		return self.cache

	def trending(self):
		return [coin['item']['symbol'] for coin in self.api('search/trending')['coins']]

	def global_(self):
		data = self.api('global')['data']
		results = {
			'cryptocurrencies' : data['active_cryptocurrencies']
			'markets'          : data['markets']
			'btc_dominance'    : data['market_cap_percentage']['btc']
		}
		return results