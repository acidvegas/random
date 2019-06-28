#!/usr/bin/env python
# CLI Twitter - Developed by acidvegas in Python (https://acid.vegas/random)

'''
Requirements:
	Tweepy (http://pypi.python.org/pypi/tweepy)
'''

import sys

consumer_key        = 'CHANGEME'
consumer_secret     = 'CHANGEME'
access_token        = 'CHANGEME'
access_token_secret = 'CHANGEME'

if len(sys.argv) < 2:
	raise SystemExit('[!] - Missing command line arguments! (Usage: clitter.py <tweet>)')
else:
	tweet = ' '.join(sys.argv[1:])
try:
	import tweepy
except ImportError:
	raise SystemExit('[!] - Failed to import the Tweepy library! (http://pypi.python.org/pypi/tweepy)')
try:
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	if not api.verify_credentials():
		raise tweepy.TweepError
except tweepy.TweepError as ex:
	raise SystemExit(f'[!] - Failed to login to Twitter! ({ex})')
else:
	me = api.me()
if len(tweet) > 280:
	raise SystemExit('[!] - Tweet is too long!')
else:
	try:
		api.update_status(tweet)
		tweet = api.user_timeline(id=me.id, count=1)[0]
		print(f'[+] - Tweet has been posted! (https://twitter.com/{me.screen_name}/status/{tweet.id})')
	except tweepy.TweepError as ex:
		raise SystemExit(f'Failed to post Tweet! ({ex})')