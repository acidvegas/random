use strict;
use warnings;

no strict 'subs';

my $SCRIPT_NAME = 'parrot';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.0';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Relay channel messages and modes';

# %cbs{server}{hook_name} = $hook_ptr:
#     stores hook pointers to unhook() on exit
# %chans{server}{channel} = @groups:
#     stores groups associated with a channel
# %groups{groupname}{server}{channel} = $flags:
#     stores channels associated with a group, as well as the channel's flags
# $READ, $STAT, $MODE:
#     flags for -read, -stat, -mode switches
our (%cbs, %chans, %groups);
our ($READ, $STAT, $MODE) = (0x1, 0x2, 0x4);
our $confpath;

sub servchan
{
	my $buffer = shift;
	return (lc weechat::buffer_get_string($buffer, 'localvar_server'),
		lc weechat::buffer_get_string($buffer, 'localvar_channel'));
}

sub ircbuf { weechat::buffer_search('irc', "(?i)".(join '.', @_)) }

sub getgroup
{
	my ($server, $channel) = @_;
	my @ret;

	for my $group (@{ $chans{$server}{$channel} }) {
	for my $to_serv (keys %{ $groups{$group} }) {
	for my $to_chan (keys %{ $groups{$group}{$to_serv} }) {
		# don't send to myself
		next if $to_serv eq $server and $to_chan eq $channel;
		push @ret, [$to_serv, $to_chan, $groups{$group}{$to_serv}{$to_chan}, $group]
	} } }

	return @ret;
}

sub sendto
{
	my ($server, $command) = @_;
	weechat::hook_signal_send('irc_input_send',
		weechat::WEECHAT_HOOK_SIGNAL_STRING,
		"$server;;1;;$command");
}

sub add_relay
{
	my ($groupname, $server, $channel, $flags) = @_;
	return if exists $cbs{$server};
	push @{ $chans{$server}{$channel} }, $groupname;
	$groups{$groupname}{$server}{$channel} = $flags;
	$cbs{$server}{PRIVMSG} =
		weechat::hook_signal("$server,irc_raw_in_privmsg", 'irc_privmsg_notice', '');
	$cbs{$server}{NOTICE} =
		weechat::hook_signal("$server,irc_raw_in_notice", 'irc_privmsg_notice', '');
	$cbs{$server}{OUT_PRIVMSG} =
		weechat::hook_signal("$server,irc_out1_privmsg", 'ircout_privmsg_notice', '');
	$cbs{$server}{OUT_NOTICE} =
		weechat::hook_signal("$server,irc_out1_notice", 'ircout_privmsg_notice', '');
	if ($flags & $STAT) {
		$cbs{$server}{JOIN} =
			weechat::hook_signal("$server,irc_raw_in_join", 'irc_join', '');
		$cbs{$server}{PART} =
			weechat::hook_signal("$server,irc_raw_in_part", 'irc_part', '');
		$cbs{$server}{KICK} =
			weechat::hook_signal("$server,irc_raw_in_kick", 'irc_kick', '');
		$cbs{$server}{NICK} =
			weechat::hook_signal("$server,irc_raw_in_nick", 'irc_nick', '');
		$cbs{$server}{QUIT} =
			weechat::hook_signal("$server,irc_raw_in_quit", 'irc_quit', '');
	}
	if ($flags & $MODE) {
#		$cbs{$server}{MODE} =
#			weechat::hook_signal("$server,irc_raw_in_mode", 'irc_mode', '');
		$cbs{$server}{TOPIC} =
			weechat::hook_signal("$server,irc_raw_in_topic", 'irc_topic', '');
	}
}

sub read_conf
{
	open FH, '<', $confpath or weechat::print('', weechat::prefix('error').
		"Error opening $confpath for reading: $!"), return;
	while (<FH>) {
		chomp;
		add_relay(split ' ');
	}
	close FH;
}

sub write_conf
{
	open FH, '>', $confpath or weechat::print('', weechat::prefix('error').
		"Error opening $confpath for writing: $!"), return;
	for my $server (keys %chans) {
	for my $channel (keys %{ $chans{$server} }) {
	for my $group (@{ $chans{$server}{$channel} }) {
		my $flags = $groups{$group}{$server}{$channel};
		print FH "$group $server $channel $flags\n";
	} } }
	close FH;
}

sub irc_privmsg_notice
{
	my (undef, $server, $cmd, $nick, $channel, $message) = (shift,
		shift =~ /(.+),irc_raw_in_(privmsg|notice)/i,
		shift =~ /:([^! ]*)[^ ]* [^ ]+ ([^ ]+) :?(.*)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		if ($message =~ /^\x01ACTION /i) {
			$message =~ s/^\x01ACTION |\x01$//g;
			sendto($to_serv, "/msg $to_chan * \x02$nick\x0f $message");
			next;
		}
		my $prefix = lc $cmd eq 'notice' ? "[\x02$nick\x0f]" : "<\x02$nick\x0f>";
		sendto($to_serv, "/msg $to_chan $prefix $message");
	}

	return weechat::WEECHAT_RC_OK;
}

sub ircout_privmsg_notice
{
	my (undef, $server, $cmd, $channel, $message) = (shift,
		shift =~ /(.*),irc_out1_(privmsg|notice)/i,
		shift =~ /[^ ]+ ([^ ]+) :?(.*)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		my $prefix = lc $cmd eq 'notice' ? 'notice' : 'msg';
		if ($message =~ /^\x01ACTION /i) {
			$message =~ s/^\x01ACTION |\x01$//g;
			sendto($to_serv, "/$prefix $to_chan \x01ACTION $message\x01");
			next;
		}
		sendto($to_serv, "/$prefix $to_chan $message");
	}

	return weechat::WEECHAT_RC_OK;
}

sub irc_join
{
	my (undef, $server, $nick, $host, $channel) = (shift,
		shift =~ /(.+),irc_raw_in_join/i,
		shift =~ /:([^! ]*)([^ ]*) join :?([^ ]+)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $STAT;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/notice $to_chan \x02$nick\x0f$host joined $server/$channel\x0f");
	}

	return weechat::WEECHAT_RC_OK;
}

sub irc_part
{
	my (undef, $server, $nick, $channel, $message) = (shift,
		shift =~ /(.+),irc_raw_in_part/i,
		shift =~ /:([^! ]*)[^ ]* part ([^ ]+) ?:?(.*)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $STAT;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/notice $to_chan \x02$nick\x0f left $server/$channel\x0f: $message");
	}

	return weechat::WEECHAT_RC_OK;
}

sub irc_kick
{
	my (undef, $server, $nick, $channel, $target, $message) = (shift,
		shift =~ /(.+),irc_raw_in_kick/i,
		shift =~ /:([^! ]*)[^ ]* kick ([^ ]+) ([^ ]+) :?(.*)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $STAT;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/notice $to_chan \x02$nick\x0f kicked $target\x0f from $server/$channel\x0f: $message");
	}

	return weechat::WEECHAT_RC_OK;
}

sub irc_nick
{
	my (undef, $server, $nick, $newnick) = (shift,
		shift =~ /(.+),irc_raw_in_nick/i,
		shift =~ /:([^! ]*)[^ ]* nick :?(.*)/i);

	for my $channel (keys %{ $chans{$server} }) {
	my $iptr = weechat::infolist_get('irc_nick', '', "$server,$channel,$nick");
	next unless $iptr;
	weechat::infolist_free($iptr);
	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $STAT;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/notice $to_chan \x02$nick\x0f is now \x02$newnick\x0f");
	} }

	return weechat::WEECHAT_RC_OK;
}

sub irc_quit
{
	my (undef, $server, $nick, $message) = (shift,
		shift =~ /(.+),irc_raw_in_quit/i,
		shift =~ /:([^! ]*)[^ ]* quit :?(.*)/i);

	for my $channel (keys %{ $chans{$server} }) {
	my $iptr = weechat::infolist_get('irc_nick', '', "$server,$channel,$nick");
	next unless $iptr;
	weechat::infolist_free($iptr);
	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $STAT;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/notice $to_chan \x02$nick\x0f left $server: $message");
	} }

	return weechat::WEECHAT_RC_OK;
}

sub irc_mode
{
	my (undef, $server, $nick, $channel, $modes) = (shift,
		shift =~ /(.+),irc_raw_in_mode/i,
		shift =~ /:([^! ]*)[^ ]* mode ([^ ]+) (.*)/i);
	($server, $channel) = (lc $server, lc $channel);
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};

	return weechat::WEECHAT_RC_OK;
}

sub irc_topic
{
	my (undef, $server, $nick, $channel, $message) = (shift,
		shift =~ /(.+),irc_raw_in_topic/i,
		shift =~ /:([^! ]*)[^ ]* topic ([^ ]+) :?([^ ]+)/i);
	($server, $channel) = (lc $server, lc $channel);
	weechat::print('',"$server $channel");
	return weechat::WEECHAT_RC_OK unless exists $chans{$server}{$channel};
	return weechat::WEECHAT_RC_OK if lc $nick eq lc weechat::info_get('irc_nick', $server);

	for (getgroup($server, $channel)) {
		my ($to_serv, $to_chan, $flags, undef) = @$_;
		next unless $flags & $MODE;
		next if $flags & $READ;
		next unless ircbuf("$to_serv.$to_chan");
		sendto($to_serv, "/topic $to_chan $message");
	}

	return weechat::WEECHAT_RC_OK;
}

sub cmd_parrot
{
	my (undef, $buffer, $command) = @_;
	my ($server, $channel) = servchan($buffer);
	my ($flags, $remove, $groupname) =
	   (     0,       0,         '');
	for (split / +/, $command) {
		/^-read$/   and ($flags |= $READ), next;
		/^-stat$/   and ($flags |= $STAT), next;
		/^-mode$/   and ($flags |= $MODE), next;
		/^-remove$/ and ($remove = 1), next;
		$groupname = $_; last;
	}

	unless ($groupname) {
		if ($chans{$server}{$channel}) {
			for (getgroup($server, $channel)) {
				my ($to_serv, $to_chan, $flags, $group) = @$_;
				my $flag_str = $flags ? ':' : '';
				$flag_str .= ' readonly' if $flags & $READ;
				$flag_str .= ' statusmsg' if $flags & $STAT;
				$flag_str .= ' sendmodes' if $flags & $MODE;
				weechat::print($buffer, weechat::prefix('server').
					"Relaying to $to_serv/$to_chan in group $group$flag_str");
			}
		} else {
			weechat::print($buffer, weechat::prefix('server').
				"This channel is not being relayed");
		}
		return weechat::WEECHAT_RC_OK;
	}

	# clear hooks first (if they exist)
	if (exists $cbs{$server}) {
		weechat::unhook($cbs{$server}{$_}) for (keys %{ $cbs{$server} });
		delete $cbs{$server};
	}
	@{ $chans{$server}{$channel} } =
		grep { $_ ne $groupname } @{ $chans{$server}{$channel} };

	if ($remove) {
		delete $groups{$groupname}{$server}{$channel};
		delete $groups{$groupname}{$server} unless $groups{$groupname}{$server};
		delete $groups{$groupname} unless $groups{$groupname};
		delete $chans{$server}{$channel} unless $chans{$server}{$channel};
		delete $chans{$server} unless $chans{$server};

		write_conf();
		weechat::print($buffer, weechat::prefix('server').
			"Removed relay from group $groupname");
		return weechat::WEECHAT_RC_OK;
	}

	add_relay($groupname, $server, $channel, $flags);

	write_conf();
	weechat::print($buffer, weechat::prefix('server').
		"Added relay to group $groupname");
	return weechat::WEECHAT_RC_OK;
}

sub completion_groupnames
{
	my $completion = pop;
	weechat::hook_completion_list_add($completion, $_, 0,
		weechat::WEECHAT_LIST_POS_SORT) for keys %groups;
}

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	$confpath = weechat::info_get('weechat_dir', '') . '/parrot.db';
	weechat::hook_completion('perl_parrot_groupname', 'parrot.pl group names',
		'completion_groupnames', '');
	weechat::hook_command('parrot', $SCRIPT_DESC,
		"[-read] [-stat] [-mode] groupname\n".
		"-remove",
		"-read: relay from this channel to others, but do not relay to\n".
		"       this channel\n".
		"-stat: show status messages (join/part) in this channel\n".
		"-mode: transfer modes to this channel, even if you are op".
		"groupname: all channels with the same group name are relayed together\n".
		"-remove: remove this channel from the relay group",
		'-remove %(perl_parrot_groupname) %-'.
		'||-read|-stat|-mode|%(perl_parrot_groupname)|%*',
		'cmd_parrot', '');
	read_conf();
}
