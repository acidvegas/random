# Released into the Public Domain

use strict;
use warnings;

no strict 'subs';

my $SCRIPT_NAME = 'antifuck';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.1';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Defend against forcejoins (e.g. from fuckyou.pl) and '.
	'forceparts (e.g. from /remove)';

my %OPTIONS = (
	autopart => ['Whether to automatically part forcejoined channels. '.
		'You can always do this manually with /antifuck part', '0'],
	delay => ['Delay in milliseconds to wait before autoparting', '5000'],
	forward => ['Whether to allow channel forwards (+f on freenode)', '1'],
	ignore => ['Servers to ignore (e.g. for bouncers), separated by comma', ''],
	nobufs => ['If 1, do not create buffers for forcejoined channels', '0'],
	timeout =>
		['Delay in milliseconds to wait for server to send JOIN after join',
		'60000'],
	);

# %channels: channels we joined and received JOIN / NAMES for
# %zombie: channels we joined but aren't yet in
# %part: channels we were forced into and will part soon
# %partbuf: buffers belonging to parted channels, we'll close these on
#           /antifuck part
our (%channels, %zombie, %part, %partbuf, $fuckbuf, $timeout_cb, $gc_cb);

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	weechat::hook_command('antifuck', $SCRIPT_DESC, 'part', <<'HELP',
This script defends against forced joins, such as from irssi's fuckyou.pl or
from channel forwards, as well as forced parts, such as from the /remove
command. You can configure certain behaviour using the options under
"plugins.var.perl.antifuck.*". Configure rejoin-on-/remove with the
irc.server_default.autorejoin and .autorejoin_delay commands.

Running "/antifuck part" will close all forcejoined channels and part them where
appropriate.
HELP
		'part', 'cmd_antifuck', '');
	weechat::hook_signal('irc_server_connected', 'irc_connect', '');
	weechat::hook_signal('irc_server_disconnected', 'irc_disconnect', '');
	weechat::hook_signal('irc_channel_opened', 'buffer_opened', '');
	weechat::hook_signal('buffer_closed', 'buffer_closed', '');
	weechat::hook_signal('*,irc_out1_join', 'client_join', '');
	weechat::hook_signal('*,irc_out1_part', 'client_part', '');
	weechat::hook_signal('*,irc_raw_in_001', 'irc_001', '');
	weechat::hook_signal('*,irc_raw_in_470', 'irc_470', '');
	weechat::hook_modifier('irc_in_366', 'irc_366', '');
	weechat::hook_modifier('irc_in_join', 'irc_join', '');
	weechat::hook_modifier('irc_in_part', 'irc_part', '');

	for my $option (keys %OPTIONS) {
		weechat::config_set_plugin($option, $OPTIONS{$option}[1])
		 unless weechat::config_is_set_plugin($option);
		weechat::config_set_desc_plugin($option, $OPTIONS{$option}[0]);
	}

	my $iptr = weechat::infolist_get('buffer', '', '');

	while (weechat::infolist_next($iptr)) {
		next unless weechat::infolist_string($iptr, 'plugin_name') eq 'irc';
		my $buf = weechat::infolist_pointer($iptr, 'pointer');
		$channels{
			lc weechat::buffer_get_string($buf, 'localvar_server')}{
			lc weechat::buffer_get_string($buf, 'localvar_channel')} = 1;
	}
	weechat::infolist_free($iptr);
}

sub mynick
{
	my ($buf, $nick) = ($_[0], $_[1]);

	return lc weechat::buffer_get_string($buf, 'localvar_nick') eq lc $nick;
}

sub ignored
{
	my $server = shift;
	my $ignore_conf = lc weechat::config_get_plugin('ignore');

	return $ignore_conf =~ /(^|,)$server($|,)/;
}

sub nobufs { weechat::config_get_plugin('nobufs') }

sub ircbuf { weechat::buffer_search('irc', "(?i)".(join '.', @_)) }
sub ircparse { weechat::info_get_hashtable(irc_message_parse =>
	{ message => shift }) }

sub servchan
{
	my $buf = shift;

	return (lc weechat::buffer_get_string($buf, 'localvar_server'),
		lc weechat::buffer_get_string($buf, 'localvar_channel'));
}

sub reset_gc
{
	weechat::unhook($gc_cb) if $gc_cb;
	$gc_cb = weechat::hook_timer(weechat::config_get_plugin('timeout'), 0, 1,
		'run_gc', '');
}

sub cmd_antifuck
{
	my (undef, $buffer, $args) = @_;

	if ($args eq 'part') {
		# TODO: we really need to spend more time here making sure we send the
		# fewest PARTs possible, a la irc_join_delay
		weechat::buffer_close($fuckbuf);
	}

	return weechat::WEECHAT_RC_OK;
}

sub fuckbuf_input { return weechat::WEECHAT_RC_OK; }

sub fuckbuf_close
{
	weechat::buffer_close($_) for (keys %partbuf);
	%partbuf = ();
	$fuckbuf = '';

	return weechat::WEECHAT_RC_OK;
}

sub irc_connect
{
	my $server = pop;
	my ($autojoin) = (weechat::config_string(weechat::config_get(
		"irc.server.$server.autojoin")) =~ /^([^ ]*)/);

	$zombie{$server}{$_} = 1 for (split ',', lc($autojoin));

	return weechat::WEECHAT_RC_OK;
}

sub irc_disconnect
{
	my $server = pop;

	$server = lc $server;
	delete $channels{$server};
	delete $zombie{$server};
	delete $part{$server};

	return weechat::WEECHAT_RC_OK;
}

sub buffer_opened {
	my $buffer = pop;
	my ($server, $channel) = servchan($buffer);
	return weechat::WEECHAT_RC_OK if exists $channels{$server}{$channel};
	return weechat::WEECHAT_RC_OK if ignored($server);

	$fuckbuf = weechat::buffer_new(
		'antifuck',
		'fuckbuf_input',
		'',
		'fuckbuf_close',
		''
		) unless $fuckbuf;

	weechat::buffer_merge($buffer, $fuckbuf);
	#return weechat::WEECHAT_RC_OK unless weechat::config_get_plugin('autopart');

	$partbuf{$buffer} = 1;
	return weechat::WEECHAT_RC_OK;
}

sub buffer_closed {
	my $buffer = pop;

	delete $partbuf{$buffer};
	return weechat::WEECHAT_RC_OK;
}

sub client_join
{
	my (undef, $server, $channel) = (shift,
		shift =~ /(.+),irc_out1_join/i,
		shift =~ /^join :?([^ ]*)/i);
	($server, $channel) = (lc $server, lc $channel);

	reset_gc();

	($_ eq '0' ? %{$channels{$server}} = () : $zombie{$server}{$_} = 1)
		for (split ',', $channel);
	return weechat::WEECHAT_RC_OK;
}

sub client_part
{
	my (undef, $server, $channel) = (shift,
		shift =~ /(.+),irc_out1_part/i,
		shift =~ /^part ([^ ]*)/i);
	($server, $channel) = (lc $server, lc $channel);

	delete $channels{$server}{$_} for (split ',', $channel);
	return weechat::WEECHAT_RC_OK;
}

# RPL_WELCOME
sub irc_001
{
	my (undef, $server, $message) = (shift,
		shift =~ /(.+),irc_raw_in_001/, shift);

	$server = lc $server;
	return weechat::WEECHAT_RC_OK unless $message =~ / :- Welcome to ZNC -$/;

	my $ignore_conf = lc weechat::config_get_plugin('ignore');
	return weechat::WEECHAT_RC_OK if $ignore_conf =~ /(^|,)$server($|,)/;

	weechat::config_set_plugin('ignore', "$ignore_conf,$server");

	return weechat::WEECHAT_RC_OK;
}

sub irc_join
{
	my ($server, $message, $msghash) = (lc $_[2], $_[3], ircparse($_[3]));
	my ($nick, $channel) = ($msghash->{nick}, lc $msghash->{channel});
	my $buffer = ircbuf("$server.$channel");

	return $message if exists $channels{$server}{$channel};
	if (exists $zombie{$server}{$channel} || ignored($server)) {
		delete $zombie{$server}{$channel};
		$channels{$server}{$channel} = 1;
		return $message;
	}
	# XXX return $message unless mynick($buffer, $nick);

	$part{$server}{$channel} = 1;
	$timeout_cb = weechat::hook_timer(
		weechat::config_get_plugin('delay'), 0, 1, 'irc_join_delay', $buffer)
		unless $timeout_cb || !weechat::config_get_plugin('autopart');

	return $message unless nobufs();

	$fuckbuf = weechat::buffer_new(
		'antifuck',
		'fuckbuf_input',
		'',
		'fuckbuf_close',
		''
		) unless $fuckbuf;
	weechat::print($fuckbuf, weechat::prefix('join').
		weechat::color('irc.color.message_join').
		'You were forced to join '.weechat::color('chat_channel').$channel.
		weechat::color('irc.color.message_join').', leaving');

	return '';
}

# RPL_ENDOFNAMES
sub irc_366
{
	my ($server, $message) = ($_[2], $_[3]);
	my ($nick, $channel) = $message =~ /^:[^ ]* 366 ([^ ]*) ([^ ]*)/i;
	my $buffer = ircbuf("$server.$channel");
	($server, $channel) = (lc $server, lc $channel);

	return $message if exists $channels{$server}{$channel};
	return '' if nobufs();

	weechat::print($buffer, weechat::prefix('network').
		'Forcejoined, not syncing modes');

	return '';
}

# ERR_LINKCHANNEL
sub irc_470
{
	my (undef, $server, $oldchan, $newchan) = (shift,
		shift =~ /(.+),irc_raw_in_470/,
		shift =~ /^:[^ ]* 470 [^ ]+ ([^ ]+) ([^ ]+)/);
	($server, $oldchan, $newchan) = (lc $server, lc $oldchan, lc $newchan);

	delete $channels{$server}{$oldchan};
	$channels{$server}{$newchan} = 1 if weechat::config_get_plugin('forward');
	return weechat::WEECHAT_RC_OK;
}

sub irc_join_delay
{
	my $buffer = shift;

	for my $server (keys %part) {
		my $chans = '';

		for my $chan (keys %{$part{$server}}) {
			if (length($chans) + length($chan) > 500) {
				weechat::hook_signal_send('irc_input_send',
					weechat::WEECHAT_HOOK_SIGNAL_STRING,
					"$server;;priority_low;;/part $chans");
				$chans = '';
			}

			$chans .= "$chan,";
		}

		weechat::hook_signal_send('irc_input_send',
			weechat::WEECHAT_HOOK_SIGNAL_STRING,
			"$server;;priority_low;;/part $chans");
	}
	$timeout_cb = '';
	%part = ();
	return weechat::WEECHAT_RC_OK;
}

sub run_gc
{
	%zombie = ();
	return weechat::WEECHAT_RC_OK;
}

sub irc_part
{
	my ($server, $message, $msghash) = ($_[2], $_[3], ircparse($_[3]));
	my ($arj, $arj_delay, $arjd, $arjd_delay) = (
		weechat::config_get("irc.server.$server.autorejoin"),
		weechat::config_get("irc.server.$server.autorejoin_delay"),
		weechat::config_get("irc.server_default.autorejoin"),
		weechat::config_get("irc.server_default.autorejoin_delay")
		);
	return $message unless (
		weechat::config_option_is_null($arj) ?
		weechat::config_boolean($arjd) :
		weechat::config_boolean($arj)
		);

	my ($nick, $channel, $reason) = ($msghash->{nick}, $msghash->{channel},
		$msghash->{text});

	my $buffer = ircbuf("$server.$channel");
	my ($lserver, $lchannel) = (lc $server, lc $channel);

	return $message unless mynick($buffer, $nick);
	return $message unless exists $channels{$lserver}{$lchannel};
	return $message if ignored($lserver);

	weechat::print($buffer, weechat::prefix('quit').
		weechat::color('irc.color.message_quit').
		'You were forced to part '.weechat::color('chat_channel').$channel.
		weechat::color('chat_delimiters').' ('.weechat::color('reset').
		$reason.weechat::color('chat_delimiters').')'.
		weechat::color('irc.color.message_quit').', rejoining');
	my $delay = (
		weechat::config_option_is_null($arj_delay) ?
		weechat::config_integer($arjd_delay) :
		weechat::config_integer($arj_delay)
		);
	weechat::command($buffer, ($delay ? "/wait $delay " : "").
		"/join $channel");

	return '';
}
