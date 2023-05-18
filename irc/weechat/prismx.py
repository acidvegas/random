# Copyright (c) 2010 Alex Barrett <al.barrett@gmail.com>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
# TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.

import weechat as w
import random
import re

SCRIPT_NAME	= "prismx"
SCRIPT_AUTHOR  = "Alex Barrett <al.barrett@gmail.com>"
SCRIPT_VERSION = "0.3.1"
SCRIPT_LICENSE = "WTFPL"
SCRIPT_DESC	= "Taste the rainbow."

# red, lightred, brown, yellow, green, lightgreen, cyan,
# lightcyan, blue, lightblue, magenta, lightmagenta
ncolors = [5, 4, 7, 8, 3, 9, 10, 11, 2, 12, 6, 13]
xcolors = [
16,28,40,52,64,65,53,41,29,17,18,30,42,54,66,67,55,43,31,19,20,32,44,
56,68,69,57,45,33,21,22,34,46,58,70,71,59,47,35,23,24,36,48,60,72,73,
61,49,37,25,26,38,50,62,74,75,63,51,39,27]
xxcolors = range(100)

# we set this later
color_count = 0

# keeping a global index means the coloring will pick up where it left off
color_index = 0

# spaces don't need to be colored and commas cannot be because mIRC is dumb
chars_neutral = " ,"
chars_control = "\x01-\x1f\x7f-\x9f"

regex_chars = "[^%(n)s%(s)s][%(n)s%(s)s]*" % { 'n': chars_neutral, 's': chars_control }
regex_words = "[^%(n)s]+[%(n)s%(s)s]*" % { 'n': chars_neutral, 's': chars_control }


if w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
			  SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
	w.hook_command("prism",
		SCRIPT_DESC,
		"[-rwmbexsp] [palette] text|-c[wbexsp] [palette] <sep> <command> <sep>text",
		"    -r: randomizes the order of the color sequence\n"
		"    -w: color entire words instead of individual characters\n"
		"    -m: append /me to beginning of output\n"
		"    -b: backwards text (entire string is reversed)\n"
		"    -e: eye-destroying colors (randomized background colors)\n"
		"    -c: specify a separator to turn on colorization\n"
		"        eg. -c : /topic :howdy howdy howdy\n"
		"    -x: extended color set, requires 256color terminal\n"
		"    -s: stretch to fit text\n"
		"    -p: specify color palette to use, comma separated\n"
		"  text: text to be colored",
		"-r|-w|-m|-b|-e|-c", "prism_cmd_cb", "")

def prism_cmd_cb(data, buffer, args):
	global color_index
	color_local = color_index
	color_index += 1

	input = args.decode("UTF-8")
	input_method = "command"

	if not input or (input[0] == '-' and input.find(' ') == -1):
		input = (input + ' ' if input else '') + w.buffer_get_string(buffer, "input")
		input = input.decode("UTF-8")
		input_method = "keybinding"

	if not input:
		return w.WEECHAT_RC_OK

	optstop = input and input[0] == '-' and input.find(' ')
	opts = input[1:optstop] if optstop else ''
	cmdstop = 'c' in opts and input.find(' ', optstop+1)
	cmd = ''
	if 'm' in opts: cmd = '/me '
	if 'c' in opts:
		find = input[optstop+1:cmdstop]
		where = input.find(find, cmdstop+1)
		cmd = input[cmdstop+1:where]
		input = input[where+len(find):]
	else:
		input = input[optstop+bool(optstop):]
	regex = regex_words if 'w' in opts else regex_chars
	inc = 'r' not in opts
	bs = 'e' in opts
	colors = ncolors if 'x' not in opts else (xxcolors if bs or not inc else xcolors)
	if 'p' in opts:
		i = input.find(' ')
		colors = input[:i].split(',')
		input = input[i+1:]
	input = input[::-1] if 'b' in opts else input
	output = u""
	tokens = re.findall(regex, input)

	if 's' in opts:
		color_local = 0
		colors = [colors[int(float(i)/len(tokens)*len(colors))]
		 for i in xrange(len(tokens))]

	color_count = len(colors)
	for token in tokens:
		# prefix each token with a color code
		c1 = unicode(colors[color_local % color_count]).rjust(2, "0")
		if bs:
			c2 = random.randint(1, color_count - 1) % color_count
			c2 = unicode(colors[c2 + 1 if c2 == color_local % color_count else c2]).rjust(2,"0")
			output += u'\x03' + c1 + ',' + c2 + token
		else:
			output += u"\x03" + c1 + token

		# select the next color or another color at
		# random depending on the options specified
		if not inc:
			color_local += random.randint(1, color_count - 1)
		else:
			color_local += inc
	output += u'\x0f'

	# output starting with a / will be executed as a
	# command unless we escape it with a preceding /
	# Commands should use the -c flag
	if len(output) > 0 and output[0] == "/":
		output = "/" + output
	if len(cmd) > 0:
		output = cmd + output
	if input_method == "keybinding":
		w.buffer_set(buffer, "input", output.encode("UTF-8"))
	else:
		w.command(buffer, output.encode("UTF-8"))
	return w.WEECHAT_RC_OK
