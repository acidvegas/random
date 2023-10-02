#!/usr/bin/env python
# phish - developed by acidvegas in python (https://git.acid.vegas/random)

'''
This is just a Python fork of https://git.supernets.org/hgw/phishies)

This project was inspired entirely by https://botsin.space/@EmojiAquarium, source code found at https://gitlab.com/JoeSondow/fishies
'''

import random

fish_types = ['🐟', '🐡', '🐠']
rare_swimmer_types = ['🐙', '🐬', '🦑', '🦈']
plant_types = ['🌱', '🌾', '🌿']
rare_bottom_dwellers = ['🪨', '🐌', '🏰', '🦀', '🐚', '⚓️', '☘️']
exceedingly_rare_junk = ['🎱', '🎲', '🎮', '🗿', '🔱', '🎷', '🗽', '💎', '💰', '🔔', '💀', '💩']

def aquarium(height=5, width=10):
	aquarium_array = []
	for i in range(height):
		line_arr = []
		if i != height - 1:
			# Ensure at least 2 fish
			fish_positions = random.sample(range(width), 2)
			for j in range(width):
				rand_num = random.random() * 100
				if j in fish_positions:
					line_arr.append(random.choice(fish_types))
				elif rand_num < 2:
					line_arr.append(random.choice(rare_swimmer_types))
				else:
					line_arr.append('　')
		if i == height - 1:
			# Ensure at least 2 plant types
			plant_positions = random.sample(range(width), 2)
			for j in range(width):
				rand_num = random.random() * 100
				if j in plant_positions:
					line_arr.append(random.choice(plant_types))
				elif rand_num < 2:
					line_arr.append(random.choice(rare_bottom_dwellers))
				elif rand_num < 0.5:
					line_arr.append(random.choice(exceedingly_rare_junk))
				else:
					line_arr.append('　')
		aquarium_array.append(''.join(line_arr))
	return aquarium_array

if __name__ == '__main__':
	while True:
		for i in aquarium():
			print(i)
