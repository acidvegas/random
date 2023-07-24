#!/usr/bin/env python
# BuyVM inventory checker - developed by acidvegas in python (https://acid.vegas/random)

''' BuyVM servers go out of stock fast, this is a script to parse all the server availability '''

import re,time,urllib.request

nodes = {
	'Las Vegas'  : '37',
	'New York'   : '38',
	'Luxembourg' : '39',
	'Miami'      : '48'
}

for node in nodes:
	data     = urllib.request.urlopen('https://my.frantech.ca/cart.php?gid=' + nodes[node]).read().decode()
	packages = re.findall(r'<h3 class="package-name">(.+?)Available\n', data, re.I | re.M | re.S | re.U)
	print(f'Servers in \033[34m{node}\033[0m:')
	for server in packages:
		name     = server.split('</h3>')[0].ljust(18)
		price    = server.split('</span>')[1].split('<span ')[0].ljust(10)
		features = server.split('<ul class="package-features"><li><b>')[1].split('</ul>')[0].split('NVME')[0]
		for item in ('<li>','</li>','<b>','</b>'):
			features = features.replace(item,'')
		features = features.ljust(39)
		stock    = server.split()[-1][0]
		if stock == '0':
			stock = f'\033[31m{stock}\033[0m'
		else:
			stock = f'\033[32m{stock}\033[0m'
		print(f'{name} \033[1;30m|\033[0m {price} \033[1;30m|\033[0m {features} \033[1;30m|\033[0m {stock}')

