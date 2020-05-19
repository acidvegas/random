#!/usr/bin/env python
import re,sys,urllib.request
if len(sys.argv)!=2:raise SystemExit('error: invalid arguments')
source=urllib.request.urlopen(f'https://{sys.argv[1]}.bandcamp.com/music').read().decode('utf-8')
for album in re.compile('<a href="/album/(.*?)">').findall(source):
	print(f'found album "{album}"')
	source=urllib.request.urlopen(f'http://downloadbandcamp.com/{sys.argv[1]}.bandcamp.com/album/{album}').read().decode('utf-8')
	for song in re.findall('(https?://t4\S+).*download="(.*?)"',source):
		print(f'downloading "{song[1]}"')
		urllib.request.urlretrieve(song[0][:-1],song[1])