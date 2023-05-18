use strict;
use warnings;
use File::Find::Rule;
no strict 'subs';

my $SCRIPT_NAME = 'play';
my $SCRIPT_AUTHOR = 'The Krusty Krab <wowaname@volatile.ch>';
my $SCRIPT_VERSION = '1.2';
my $SCRIPT_LICENCE = 'Public domain';
my $SCRIPT_DESC = 'Play ASCII art';
our (%queue, %timer);

if (weechat::register($SCRIPT_NAME, $SCRIPT_AUTHOR, $SCRIPT_VERSION,
 $SCRIPT_LICENCE, $SCRIPT_DESC, '', '')) {
	weechat::hook_command('play', 'Play ASCII art',
		'[-delay ms] [-repeat times] [-pipe "command"] [-fmt "list"] filename'.
		"\n-find pattern\n-stop\n",
		"-delay: delay in milliseconds between lines\n".
		"-find: list matching files, don't play\n".
		"-pipe: pipe output into command\n".
		"-fmt: treat file as a format string and replace with arguments in\n".
		"    list. Arguments are separated by semicolons (;)\n".
		"filename: file to play. Supports wildcards. By default, searches\n".
		"    subdirectories as well unless '/' is found in the filename\n".
		"-stop: stop currently playing file in buffer",
		'-delay|-pipe|-fmt|-repeat|%*'.
		' || -find'.
		' || -stop',
		'cmd_play', '');

	my %OPTIONS = (
		delay => ['Default delay between lines, in milliseconds', 0],
		dir => ['Art directory',
			weechat::info_get('weechat_dir', '').'/ascii'],
		find_limit => ['Maximum number of results returned by -find. '.
			'-1 = unlimited (may lock up WeeChat with many results!)', 32],
		);

	for my $option (keys %OPTIONS) {
		weechat::config_set_plugin($option, $OPTIONS{$option}[1])
		 unless weechat::config_is_set_plugin($option);
		weechat::config_set_desc_plugin($option, $OPTIONS{$option}[0]);
	}
}

sub parse
{
	my ($input, $delay, $pipe, $find, $repeat, $fmt) =
		(shift, weechat::config_get_plugin('delay'), '/msg *', 0, 1, '');

	if ($input =~ / *-delay +([0-9]+) /) {
		$delay = $1;
		$input =~ s/-delay +[0-9]+//;
	}
	if ($input =~ / *-find /) {
		$find = 1;
		$input =~ s/-find//;
	}
	if ($input =~ / *-fmt +("(?:[^"\\]|\\.)+"|[^ ]+) /) {
		$fmt = $1;
		$fmt =~ s/^"(.+)"$/$1/ if $fmt =~ /^".+"$/;
		$input =~ s/-fmt +("(?:[^"\\]|\\.)+"|[^ ]+)//;
	}
	if ($input =~ / *-repeat +([0-9]+) /) {
		$repeat = $1;
		$input =~ s/-repeat +[0-9]+//;
	}
	if ($input =~ / *-pipe +("(?:[^"\\]|\\.)+"|[^ ]+) /) {
		$pipe = $1;
		$pipe =~ s/^"(.+)"$/$1/ if $pipe =~ /^".+"$/;
		$input =~ s/-pipe +("(?:[^"\\]|\\.)+"|[^ ]+)//;
	}

	return ($delay, $pipe, $find, $repeat, $fmt, $input =~ s/^ +| +$//r);
}

sub play
{
	my $buffer = shift;

	weechat::command($buffer, shift @{ $queue{$buffer} });
	delete $queue{$buffer} unless @{ $queue{$buffer} };

	return weechat::WEECHAT_RC_OK;
}

sub cmd_play
{
	my $buffer = $_[1];

	if ($_[2] eq '-stop') {
		if (exists $timer{$buffer}) {
			weechat::unhook($timer{$buffer});
			delete $queue{$buffer};
		}
		return weechat::WEECHAT_RC_OK;
	}

	my ($delay, $pipe, $find, $repeat, $fmt, $file) = parse($_[2]);
	my $server = weechat::info_get($buffer, 'localvar_server');
	my ($prio_s, $prio_d) = (
		weechat::config_get("irc.server.$server.anti_flood_prio_high"),
		weechat::config_get("irc.server_default.anti_flood_prio_high"),
		);
	$delay = ($delay or 1000 * (
		weechat::config_option_is_null($prio_s)
		? weechat::config_integer($prio_d)
		: weechat::config_integer($prio_s)
		) or 10);

	my $rule = File::Find::Rule
		->file
		->name($file)
		->start(weechat::config_get_plugin('dir'));

	if ($find) {
		my $i = weechat::config_get_plugin('find_limit');
		weechat::print($buffer, " \t$_")
			while defined( $_ = $rule->match ) and --$i;
		weechat::print($buffer, weechat::prefix('error').
			"Too many results; please narrow your search") unless $i;
		weechat::print($buffer, " \tEnd of file listing for '$file'");
		return weechat::WEECHAT_RC_OK;
	}

	my $path;
	if ($file =~ m"/") { $path = weechat::config_get_plugin('dir')."/$file" }
	else { $path = $rule->match }

	if ($path and -z $path) {
		weechat::print($buffer, weechat::prefix('error').
			"File '$file' is empty");
	} elsif ($path and open FH, "<", $path) {
		my @lines;
		while (<FH>) {
			no warnings; # sprintf barks if there's nothing to replace
			$_ = sprintf $_, split ';', $fmt if $fmt;
			push @lines, s/[\r\n]*$//r
		}
		close FH;
		for (1 .. $repeat) {
			push @{ $queue{$buffer} }, "$pipe \x0f$_\x0f" for @lines;
		}

		weechat::unhook($timer{$buffer}) if exists $timer{$buffer};
		$timer{$buffer} =
			weechat::hook_timer($delay, 0, scalar @{ $queue{$buffer} },
			'play', $buffer);
	} else {
		weechat::print($buffer, weechat::prefix('error').
			"Cannot open '$file'".($! ? ": $!" : ""));
		return weechat::WEECHAT_RC_ERROR;
	}

	return weechat::WEECHAT_RC_OK;
}
