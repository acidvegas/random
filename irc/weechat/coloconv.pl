#!/usr/bin/perl

=pod

Reads plugins.conf from stdin, writes new plugins.conf to stdout, and
writes commands to restore the rest of the config options to stderr

Suggested operation:
cd .weechat
./coloconv.pl < plugins.conf > plugins.conf.new 2> commands
diff plugins.conf plugins.conf.new # to make sure nothing got clobbered

Then in WeeChat:
/exec -o .weechat/commands

=cut

my %profs;
my $desc = 0;

while (<>) {
	$desc and print, next;
	$_ !~ /^python\.embellish\./ and print, next;
	s/^python\.embellish/python.colo/;
	$_ !~ /^python\.colo\..*(?:pre|suf)/ and print, next;
	$_ eq '[desc]' and ($desc = 1), print, next;

	my ($prof, $k, $v) = /^python\.colo\.(.*)(pre|suf) = "(.*)"$/;
	$v =~ s/\x02/%b/g;
	$v =~ s/\x03/%c/g;
	$v =~ s/\x0f/%o/g;
	$v =~ s/\x16/%r/g;
	$v =~ s/\x1f/%u/g;

	if ($k eq 'pre') {
		$profs{$prof} = "%0$v%o%0 %s%o%0 ";
	} elsif ($k eq 'suf') {
		$profs{$prof} .= $v;
	}
}

for my $prof (keys %profs) {
	print STDERR "/reload\n";
	print STDERR "/set plugins.var.python.colo.${prof}fmt $profs{$prof}\n";
}
