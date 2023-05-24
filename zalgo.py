#!/usr/bin/env python
# -*- coding: utf-8 -*-
# zalgo text - developed by acidvegas in python (https://acid.vegas/random)

from random import randint, choice

def zalgo(text, intensity=50):
	zalgo_chars = [chr(i) for i in range(0x0300, 0x036F + 1)]
	zalgo_chars.extend([u'\u0488', u'\u0489'])
	if not _is_narrow_build:
		text = _insert_randoms(text)
	zalgoized = []
	for letter in text:
		zalgoized.append(letter)
		for _ in range(randint(0, intensity) + 1):
			zalgoized.append(choice(zalgo_chars))
	response = choice(zalgo_chars).join(zalgoized)
	return response

def _insert_randoms(text):
	random_extras = [unichr(i) for i in range(0x1D023, 0x1D045 + 1)]
	newtext = []
	for char in text:
		newtext.append(char)
		if randint(1, 5) == 1:
			newtext.append(choice(random_extras))
	return u''.join(newtext)

def _is_narrow_build():
	try:
		chr(0x10000)
	except ValueError:
		return True
	return False

for i in range(100):
	print(zalgo('This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test '))