use strict;
use warnings;
no strict 'subs';

my $SCRIPT_NAME = 'banner';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.0';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Banner text';
our (%queue, %timer);

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	weechat::hook_command('banner', 'Banner text',
		"[-nick|-key|-limit] text",
		"-nick: send to /nick command\n".
		"-key: send as /mode +k (doesn't work on all ircds)\n".
		"-limit: send as /mode +l\n",
		'', 'cmd_banner', '');
}

sub cmd_banner
{
	my ($buffer, $cmd) = ($_[1], $_[2]);
	my ($flag, $text) = $cmd =~ /^(-nick|-key|-limit|) *(.*)$/;
	my @output;
	my $prefix = '/msg *';
	my $nick = weechat::info_get('irc_nick',
		weechat::buffer_get_string($buffer, 'localvar_server'));

my @chars = ('````````^',
'XX``XXXXX',
'``````XXX
`````````
``````XXX',
'``X```X``
XXXXXXXXX
``X```X``
XXXXXXXXX
``X```X``',
'`````XX``
`X``X``X`
XX``X``XX
`X``X``X`
``XX`````',
'```X```XX
XX``X``XX
XX```X```',
'```X`X```
X`X`X`X`X
``X```X``',
'``````XXX',
'`XXXXXXX`
X```````X',
'X```````X
`XXXXXXX`',
'``````X`X
```````X`
``````X`X',
'````X````
```XXX```
````X````',
'X````````
`XX``````',
'````X```^
````X````',
'X````````',
'XXX``````
```XXX```
``````XXX',
'`XXXXXXX`
X```````X
`XXXXXXX`',
'X``````X`
XXXXXXXXX
X````````',
'XXX````X`
X``XX```X
X````XXX`',
'`X`````X`
X```X```X
`XXX`XXX`',
'````XXX``
````X``X`
XXXXXXXXX',
'X```XXXXX
X```X```X
`XXX````X',
'`XXXXXXX`
X```X```X
`XXX`````',
'XXX`````X
```XXX``X
``````XXX',
'`XXX`XXX`
X```X```X
`XXX`XXX`',
'`````XXX`
X```X```X
`XXXXXXX`',
'``XX`XX``',
'`X```````
``XX`XX``',
'````X````
```X`X```
``X```X``',
'```X`X```
```X`X``^
```X`X```',
'``X```X``
```X`X```
````X````',
'```````X`
XX``X```X
`````XXX`',
'`XXXXXXX`
X``XXX``X
X`X```X`X
X`XXXXXXX',
'XXXXXXXX`
````X```X
XXXXXXXX`',
'XXXXXXXXX
X```X```X
`XXX`XXX`',
'`XXXXXXX`
X```````X
`X`````X`',
'XXXXXXXXX
X```````X
`XXXXXXX`',
'XXXXXXXXX
X```X```X
X```````X',
'XXXXXXXXX
````X```X
````````X',
'`XXXXXXX`
X```````X
`XXX```X`',
'XXXXXXXXX
````X````
XXXXXXXXX',
'X```````X
XXXXXXXXX
X```````X',
'`X``````X
X```````X
`XXXXXXXX',
'XXXXXXXXX
````X````
```X`X```
XXX```XXX',
'XXXXXXXXX
X````````',
'XXXXXXXXX
``````XX`
``XXXX```
``````XX`
XXXXXXXXX',
'XXXXXXXXX
``````XX`
```XXX```
`XX``````
XXXXXXXXX',
'XXXXXXXXX
X```````X
XXXXXXXXX',
'XXXXXXXXX
````X```X
`````XXX`',
'`XXXXXXXX
XX``````X
XXXXXXXXX
X````````',
'XXXXXXXXX
````X```X
XXXX`XXX`',
'`X```XXX`
X```X```X
`XXX```X`',
'````````X
XXXXXXXXX
````````X',
'XXXXXXXXX
X````````
XXXXXXXXX',
'```XXXXXX
XXX``````
```XXXXXX',
'`XXXXXXXX
X````````
`XXXX````
X````````
`XXXXXXXX',
'XXX```XXX
```XXX```
XXX```XXX',
'`````XXXX
XXXXX````
`````XXXX',
'XXX`````X
X``XXX``X
X`````XXX',
'XXXXXXXXX
X```````X',
'``````XXX
```XXX```
XXX``````',
'X```````X
XXXXXXXXX',
'```````X`
````````X
```````X`',
'X````````
X```````^
X````````',
'````````X
```````X`',
'`X``X````
X`X`X````
XXXX`````',
'XXXXXXXXX
X```X````
`XXX`````',
'`XXX`````
X```X````
X```X````',
'`XXX`````
X```X````
XXXXXXXXX',
'`XXX`````
X`X`X````
X`XX`````',
'XXXXXXXX`
````X```X',
'X``X`````
X`X`X````
`XXXX````',
'XXXXXXXXX
````X````
XXXX`````',
'XXXXX``X`',
'X````````
`XXXX``X`',
'XXXXXXXXX
````X````
XXXX`X```',
'X```````X
XXXXXXXXX
X````````',
'XXXXX````
````X````
XXXX`````
````X````
XXXX`````',
'XXXXX````
````X````
XXXX`````',
'XXXXX````
X```X````
XXXXX````',
'XXXXX````
`X``X````
``XX`````',
'``XX`````
`X``X````
XXXXX````',
'XXXXX````
````X````',
'X``X`````
X`X`X````
`X``X````',
'`XXXXXXX`
X```X````',
'`XXXX````
X````````
XXXXX````',
'``XXX````
XX```````
``XXX````',
'`XXXX````
X````````
`XXX`````
X````````
`XXXX````',
'XX`XX````
``X``````
XX`XX````',
'X``XX````
X`X``````
`XXXX````',
'XX``X````
X`X`X````
X``XX````',
'````X````
XXXX`XXXX
X```````X',
'XXXXXXXXX',
'X```````X
XXXX`XXXX
````X````',
' ```````X`
````````X
```````X`
````````X');

	for ($flag) {
		/-nick/  and $prefix = '/nick', last;
		/-key/   and $prefix = '/mode +k', last;
		/-limit/ and $prefix = '/mode +l', last;
	}

	if ($flag eq '-limit') { $chars[$_] =~ y/`X/18/ for (0 .. (@chars - 1)) }

	for my $char (split //, $text) {
		push @output, $flag eq '-limit' ? '111111111' : '`````````';
		push @output, split /\n/, $chars[ord($char) - 0x20];
	}

	weechat::command($buffer, "$prefix $_") for @output;

	for ($flag) {
		/-nick/  and weechat::command($buffer, "/nick $nick"), last;
		/-key/   and weechat::command($buffer, "/mode +k `````````"),
		             weechat::command($buffer, "/mode -k `````````"),
		             last;
		/-limit/ and weechat::command($buffer, "/mode -l"), last;
	}

	return weechat::WEECHAT_RC_OK;
}
