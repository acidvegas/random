# CLI Tweeter
# Developed by acidvegas in Python 3
# https://github.com/acidvegas
# clitter.py

import sys

# API Settings
consumer_key        = 'CHANGEME'
consumer_secret     = 'CHANGEME'
access_token        = 'CHANGEME'
access_token_secret = 'CHANGEME'

# Main
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
    raise SystemExit('[!] - Failed to login to Twitter! ({0})'.format(str(ex)))
else:
    me = api.me()
if len(tweet) > 140:
    raise SystemExit('[!] - Tweet is too long!')
else:
    try:
        api.update_status(tweet)
        tweet = api.user_timeline(id=me.id, count=1)[0]
        print('[+] - Tweet has been posted! (https://twitter.com/{0}/status/{1})'.format(me.screen_name, tweet.id))
    except tweepy.TweepError as ex:
        raise SystemExit('Failed to post Tweet! ({0})'.format(str(ex)))
