use strict;
use warnings;

no strict 'subs';

my $SCRIPT_NAME = 'sighup';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.0';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Reload config on SIGHUP';

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	weechat::hook_signal('signal_sighup', 'cb_sighup', '');
}

sub cb_sighup {
	weechat::command('', '/reload');

	return weechat::WEECHAT_RC_OK_EAT;
}

