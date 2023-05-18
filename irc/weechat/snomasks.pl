# Released into the Public Domain

# Note: After loading the script and adding snomasks into one of your bars, you
# must request /umode once on each server you have server notices masks set on.
# After that, the script will automatically update the bar item.

use strict;
use warnings;

no strict 'subs';

my $SCRIPT_NAME = 'snomasks';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.1';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Server notice mask bar item for opers';

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	weechat::bar_item_new('snomasks', 'bar_snomasks', '');
	weechat::hook_signal('buffer_switch', 'buffer_switch', '');
	weechat::hook_signal('irc_server_disconnected', 'irc_disconnected', '');
	weechat::hook_signal('*,irc_raw_in_008', 'irc_008', '');
}

my %snomask;

sub bar_snomasks {
	my $buffer = weechat::current_buffer();

	return ''
		if weechat::buffer_get_string($buffer, 'localvar_plugin') ne 'irc';

	my $server = weechat::buffer_get_string($buffer, 'localvar_server');
	return $snomask{$server} // '';
}

sub buffer_switch {
	weechat::bar_item_update('snomasks');
	return weechat::WEECHAT_RC_OK;
}

sub irc_008 {
	my (undef, $server, $modes) = (shift,
		shift =~ /^(.+),irc_raw_in_008$/,
		shift =~ /:[^ ]* 008 [^ ]* (?::Server notice mask \()?([^ )]*)/);
	$server = lc $server;

	$snomask{$server} = $modes;
	weechat::bar_item_update('snomasks');
	return weechat::WEECHAT_RC_OK;
}

sub irc_disconnected {
	my $server = pop;
	delete $snomask{lc $server};
	return weechat::WEECHAT_RC_OK;
}
