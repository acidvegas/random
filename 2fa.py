#!/usr/bin/env python
# Two-factor Authentication (2FA) Helper - Developed by acidvegas in Python (https://acid.vegas/random)

'''
Requirements:
	pyotp  (https://pypi.org/project/pyotp/)
	qrcode (https://pypi.org/project/qrcode/)
'''

import io, sys, time

try:
	import pyotp, qrcode
except ImportError:
	raise SystemExit('missing required \'pyotp\' module! (https://pypi.org/project/pyotp/)')
try:
	import qrcode
except ImportError:
	raise SystemExit('missing required \'qrcode\' module! (https://pypi.org/project/qrcode/)')

def qrgen(data):
	stdout = sys.stdout
	sys.stdout = io.StringIO()
	qr = qrcode.QRCode(border=1)
	qr.add_data(data)
	qr.make(fit=True)
	qr.print_ascii(invert=True)
	output = sys.stdout.getvalue()
	sys.stdout = stdout
	return output

name = input('name   : ')
issuer = input('issuer : ')
secret = input('secret : ') or pyotp.random_base32()
uri = pyotp.totp.TOTP(secret).provisioning_uri(name, issuer)
qr = qrgen(uri).replace(' ', ' ')[:-1]
max_len = len(qr.split('\n')[1])
print(uri+'\n'+qr)
del name, issuer, uri, qr
while True:
	code = pyotp.TOTP(secret).now()
	seconds = int(time.strftime('%S'))
	remain = 60-seconds if seconds >= 30 else 30-seconds
	print(f'{code} ({remain})'.center(max_len),  end='\r')
	time.sleep(1)