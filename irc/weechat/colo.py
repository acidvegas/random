# -*- coding: utf-8 -*-
#
# Released into the Public Domain

"""colo: make your chats noticable"""

import random
import re
import weechat

SCRIPT_NAME    = "colo"
SCRIPT_AUTHOR  = "The Krusty Krab <wowaname@volatile.ch>"
SCRIPT_VERSION = "2.2"
SCRIPT_LICENSE = "Public domain"
SCRIPT_DESC    = "Makes your chats noticable"

# script options
settings = {
	"fmt": (
		"%c13♥ %0%s%o %c13♥",
		"Format string for text. %0 - %9 are different colours, %s is text, "
		"%c %b %u %r %o are ^C ^B ^U ^R ^O respectively, and %% is a literal "
		"percent sign. %0 is the primary colour that should be used with %s.",
		),
	"fgs": (
		"04,05,06,13",
		"Colour codes to cycle for the foreground. "
		"Leave blank for no foreground colours.",
		),
	"bgs": (
		"",
		"Colour codes to cycle for the background. "
		"Leave blank for no background colours.",
		),
	"ignore_buffers": (
		"bitlbee.*,scripts",
		"List of buffers to ignore. Glob matches unless "
		"you prefix the name with 're:'.",
		),
	"whitelist_buffers": (
		"",
		"List of buffers to whitelist. Glob match unless "
		"you prefix the name with 're:'. Useful with "
		"ignore_buffers = \"*\"",
		),
	"whitelist_cmds": (
		"me,amsg,say",
		"Commands to colour.",
		),
	"profiles": (
		"> greentext,! alert",
		"List of prefix/profile pairs. If you type one of "
		"these prefixes at the beginning of your message, "
		"the options will switch to (profile)_pre, "
		"(profile)_suf, (profile)_fgs, and (profile)_bgs. ",
		),
	"greentext_fmt": "%c3> %s",
	"alert_fmt": "%c1,8/!\\%c8,1 %s %o%c1,8/!\\"
}


if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE,
 SCRIPT_DESC, "", ""):
	for opt, val in settings.iteritems():
		setting, desc = val if type(val) == tuple else (val, "")
		if desc: weechat.config_set_desc_plugin(opt, desc)
		if weechat.config_is_set_plugin(opt): continue
		weechat.config_set_plugin(opt, setting)

	weechat.hook_modifier("input_text_for_buffer", "cb_colo", "")

# prevent looping
nest = False

def glob_match (haystack, needle):
	return re.search("^%s$" %
	 re.escape(haystack).replace(r"\?", ".").replace(r"\*", ".*?"),
	 needle)

def is_command (string):
	return (string.startswith("/") and not string.startswith("/ ") and
	 string != "/" and string.split(" ", 1)[0].split("\n", 1)[0].find("/", 1)
	 < 0)

def cb_colo (data, mod, buf, input):
	global nest
	if nest:
		nest = False
	#	return input
	buffer_name = weechat.buffer_get_string(buf, "name").lower()
	output = ""
	profile = ""

	for pattern in weechat.config_get_plugin("whitelist_buffers").lower().split(","):
		if (pattern.startswith("re:") and
		 re.search(pattern[3:], buffer_name)) or glob_match(pattern, buffer_name):
			break
	else:
		for pattern in weechat.config_get_plugin("ignore_buffers").lower().split(","):
			if (pattern.startswith("re:") and
			 re.search(pattern[3:], buffer_name)) or glob_match(pattern, buffer_name):
				return input

	if not input:
		return input

	if is_command(input):
		for cmd in weechat.config_get_plugin("whitelist_cmds").lower().split(","):
			if not input.startswith("/%s " % cmd): continue
			output = "/%s " % cmd
			input = input.split(" ", 1)[1] if " " in input else ""
			break
		else:
			# XXX
			return input.replace('\r','')

	if input.startswith("//"): input = input[1:]

	for profile_pairs in weechat.config_get_plugin("profiles").split(","):
		prefix, name = profile_pairs.split()
		if not input.startswith("%s " % prefix): continue
		profile = "%s_" % name
		input = input.split(" ",1)[1] if " " in input else ""
		for opt in ("fmt", "fgs", "bgs"):
			if weechat.config_is_set_plugin(profile + opt): continue
			weechat.config_set_plugin(profile + opt, "")
		break

	fgs = weechat.config_get_plugin("%sfgs" % profile).split(",")
	bgs = weechat.config_get_plugin("%sbgs" % profile).split(",")
	fmt = weechat.config_get_plugin("%sfmt" % profile).split("%%")
	
	for i in xrange(len(fmt)):
		fmt[i] = fmt[i].replace("%c", "\x03").replace("%b",
		 "\x02").replace("%u", "\x1f").replace("%r",
		 "\x16").replace("%o", "\x0f")
		if fgs == [""] and bgs == [""]: continue
		for j in xrange(10):
			base = "\x03%s%s%s" % (
				random.choice(fgs),
				"," if bgs != [""] else "",
				random.choice(bgs),
				)
			fmt[i] = fmt[i].replace("%%%d" % j, base)
			if j: continue
			input = re.sub(
				"\x03([^0-9])",
				"\x03%s\\1" % base,
				input.replace("\x0f","\x0f%s" % base))

	fmt = "%".join(fmt)
	nest = is_command(fmt)
	servername = weechat.buffer_get_string(buf, "localvar_server")
	iptr = weechat.infolist_get("irc_server", "", servername)
	weechat.infolist_next(iptr)
	long_lines = weechat.infolist_integer(iptr, "cap_long_lines")
	weechat.infolist_free(iptr)

	nicklen = weechat.info_get("irc_server_isupport_value", "%s,NICKLEN" %
	 servername)
	if not nicklen: nicklen = 9

	l = ((512 if long_lines else 0) + 409 - len(fmt) - int(nicklen))
	o = []
	for line in input.replace("\r", "\n").split("\n"):
		if not line: continue
		for i in xrange(0, len(line), l):
			o.append(fmt.replace("%s", line[i:i+l].rstrip()))

	return output + "\n".join(o)
