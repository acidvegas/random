#!/usr/bin/env python
# guitar scales generator - developed by acidvegas in python (https://acid.vegas/random)

scales = {
	'algerian'              :  '2131131', # 1 = Half-step | 2 = Whole-step | 3 = Whole-step-Half-step
	'aeolian'               :  '2122122',
	'blues'                 :   '321132',
	'chromatic'             :  '1111111',
	'dorian'                :  '2122212',
	'half_whole_diminished' : '12121212',
	'harmonic_minor'        :  '2122131',
	'ionian'                :  '2212221',
	'locrian'               :  '1221222',
	'lydian'                :  '2221221',
	'major'                 :  '2212221',
	'major_pentatonic'      :    '22323',
	'melodic_minor'         :  '2122221',
	'mixolydian'            :  '2212212',
	'natural_minor'         :  '2122122',
	'persian'               :  '1311231',
	'phrygian'              :  '1222122',
	'whole_half_diminished' : '21212121',
	'whole_tone'            :  '2222222'
}

def generate_notes(key):
	notes = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
	while notes[0] != key:
		notes.append(notes.pop(0))
	return notes

def generate_scale(string, scale_notes, full=False):
	notes = generate_notes(string.upper())*2 if full else generate_notes(string.upper())
	notes.append(notes[0])
	for index,note in enumerate(notes):
		if note in scale_notes:
			notes[index] = notes[index].center(5, '-')
		else:
			notes[index] = '-'*5
	return notes

def get_pattern(pattern):
	new_pattern = list()
	for step in pattern:
		if   step == '1' : new_pattern.append('H')
		elif step == '2' : new_pattern.append('W')
		elif step == '3' : new_pattern.append('WH')
	return ' '.join(new_pattern)

def scale(type, key):
	last = 0
	notes = generate_notes(key)
	scale_notes = [notes[0],]
	for step in scales[type]:
		last += int(step)
		if last >= len(notes):
			last -= len(notes)
		scale_notes.append(notes[last])
	return scale_notes

def print_scale(root, type, full=False):
	if root.upper() not in ('A','A#','B','C','C#','D','D#','E','F','F#','G','G#'):
		raise SystemExit('invalid root note')
	elif type.lower() not in scales:
		raise SystemExit('invalid scale type')
	else:
		frets = (24,147) if full else (12,75)
		print(f'{root.upper()} {type.upper()} SCALE'.center(frets[1]))
		print('  ┌' + '┬'.join('─'*5 for x in range(frets[0])) + '┐')
		print('0 │' + '│'.join(str(x).center(5) for x in range(1,frets[0]+1)) + '│')
		print('  ├' + '┼'.join('─'*5 for x in range(frets[0])) + '┤')
		scale_notes = scale(type, root)
		for string in ('eBGDAE'):
			string_notes = generate_scale(string, scale_notes, full)
			print(string + ' │' + '│'.join(note.center(5, '-') for note in string_notes[1:]) + '│')
		print('  └' + '┴'.join('─'*5 for x in range(frets[0])) + '┘')
		print((', '.join(scale_notes) + ' / ' + get_pattern(scales[type])).rjust(frets[1]))

def print_scales():
	max_key = max(len(x) for x in scales)
	max_value = max(len(get_pattern(scales[x])) for x in scales)
	print('NAME'.ljust(max_key+3) + 'PATTERN'.rjust(max_value))
	for name, pattern in scales.items():
		print(name.ljust(max_key) + ' │ ' + get_pattern(pattern).rjust(max_value))

# Main
print_scales()
print_scale('F#','major')
