#!/usr/bin/env python
# requires: https://pypi.org/project/lyricsgenius/
import sys, lyricsgenius
genius = lyricsgenius.Genius('CLIENT ACCESS TOKEN') # http://genius.com/api-clients
genius.verbose = False
song = genius.search_song(sys.argv[2], sys.argv[1])
print(song.lyrics) if song else print('no lyrics found')