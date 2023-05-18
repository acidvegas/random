# Released into the Public Domain

import random
#from threading import Thread
#from time import sleep
import weechat

SCRIPT_NAME    = "masshl"
SCRIPT_AUTHOR  = "The Krusty Krab <wowaname@volatile.ch>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "Public domain"
SCRIPT_DESC    = "Provides nicklist hooks."

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
	SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
	weechat.hook_command("masshl",
		SCRIPT_DESC,
		"[-do <delay>] text (broken, currently no-op)",
		"-d  Specify a delay at the beginning (e.g. -d 1 for\n"
		"    one second) to insert a delay between messages.\n"
		"    %n - replace with next nick\n"
		"    %N - replace with as many nicks as possible per line\n"
		"    %r - replace with random hex value to thwart antispam\n"
		"-o  Include your own nick in output",
		"-od", "masshl_cmd_cb", "")

class Loop():
	def __init__(self, buffer, nicks, input, input_method, N_param, delay, opts):
		self.buffer = buffer
		self.nicks = nicks
		self.input = input
		self.input_method = input_method
		self.N_param = N_param
		self.delay = delay
		self.opts = opts

	def run(self):
		i = -('o' not in self.opts)
		if i == -1: self.nicks.pop(0)
		N_nicks = ""
		output = self.input
		for nick in self.nicks:
			i += 1
			if self.N_param:
				N_nicks += " %s" % nick
				if (nick != self.nicks[-1] and
				 len(output) + len(N_nicks) + len(self.nicks[i]) < 300):
					continue
			else: output = self.input.replace("%n",nick)
			N_nicks = N_nicks.lstrip()
			output = output.replace("%N",N_nicks)
			output = output.replace("%r","%08x" % random.randint(0,0xffffffff))
			if self.input_method == "keybinding":
				weechat.buffer_set(self.buffer, "input", output)
			else:
				weechat.command(self.buffer, output)
#			sleep(self.delay)
			output = self.input
			N_nicks = ""

def masshl_cmd_cb(data, buffer, args):
	input = args

	input_method = "command"
	server = weechat.buffer_get_string(buffer, 'localvar_server')
	channel = weechat.buffer_get_string(buffer, 'localvar_channel')

	if not input or (input[0] == '-' and input.find(' ') == -1):
		input = (input + ' ' if input else '') + weechat.buffer_get_string(buffer, "input")
		input_method = "keybinding"

	N_param = "%N" in input
	if not N_param and "%n" not in input and "%r" not in input:
		# if we bind this to Enter key, we don't want useless flooding on
		# normal messages
		return weechat.WEECHAT_RC_OK

	optstop = input and input[0] == '-' and input.find(' ')
	opts = input[1:optstop] if optstop else ''
	cmdstop = 'd' in opts and input.find(' ', optstop+1)
	delay = 0
	if 'd' in opts:
		find = input[optstop+1:cmdstop]
		where = input.find(find, cmdstop+1)
		try: delay = float(find)
		except ValueError:
			weechat.prnt(buffer, "delay must be a float value!")
			return weechat.WEECHAT_RC_ERROR
		input = input[where+len(find):]
	else: input = input[optstop+bool(optstop):]

	nicklist = weechat.infolist_get("irc_nick", "", "%s,%s" % (server,channel))

	# dealing with the cursor can get a little tricky. let's use a dict
	# instead, that way we can manipulate just what we need and we can
	# do that with builtins
	nicks = []
	while weechat.infolist_next(nicklist):
		nicks.append(weechat.infolist_string(nicklist, "name"))

	weechat.infolist_free(nicklist)

	workhorse = Loop(buffer, nicks, input, input_method, N_param, delay, opts)
	workhorse.run()

	return weechat.WEECHAT_RC_OK
