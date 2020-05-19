######
# hueg.pl PRO MODE
# modded by ma0 and others
# respekts 2 jakk and others
# 2020 upd: ported for HexChat by anon
######

use Xchat qw(:all);

$VERSION = ord 'LOL';

register('hueg', $VERSION, 'make text hueg LOL');

hook_command( "hueg", \&hueg );

my $maxchars = 10; #num of chars b4 split
my $reverse = 0;
my $flip = 0;
my $mirror = 0;
my $scale = 1;
my $k = chr 3;
my $OO = pack('H*', '0f');

sub hueg {
  my $target =  context_info()->{channel};
	my $data = $_[1][1];

  $in = $data;
  my $rep;

  if ($in =~ /-rep (\d+)/i) {
    $rep = $1;
    $in =~ s/-rep \d+//i;
  } else {
    $rep = 1;
  }
  if($in =~ /-scale (\d+)/i) {
    $scale = $1;
    $in =~ s/-scale \d+//i;
  } else {
    $scale = 1;
  }
  if($in =~ /-re/i) {
    $reverse = 1;
    $in =~ s/-re//i;
  } else {
  $reverse = 0;
  }
  if($in =~ /-flip/i){
    $flip = 1;
    $in =~ s/-flip//i;
  } else { 
    $flip = 0;
  }
  if($in =~ /-mir/i) {
    $mirror = 1;
    $in =~ s/-mir//i; 
  } else {
    $mirror = 0;
  }

  $in =~ s/\s+$//;
  if ($in eq '') {
		Xchat::print "/hueg <string> [options]";
		Xchat::print "      -rep <num>     num of times to scroll msg";
		Xchat::print "      -re            reverses text";
		Xchat::print "      -flip          flips text";
		Xchat::print "      -mir           mirrors your text [NOT WORKIN LOL]";
		Xchat::print "      -scale <num>   scales shit";      
		Xchat::print "      num,num,num    fg, shadow, bg colors (bg optional)";
  } else {

    until ($rep==0) {

		# colors();
		if ($data =~ /(\d+),(\d+),(\d+)/) {
			$c2 = "$k$1,$1";   #fg
			$c1 = "$k$2,$2";   #sh
			$c3 = "$k$3,$3";   #bg
			$in =~ s/\d+,\d+,\d+//;
		} elsif ($data =~ /(\d+),(\d+)/) {
			$c2 = "$k$1,$1";   #fg
			$c1 = "$k$2,$2";   #sh
			$c3 = "$OO";        #bg (trans)
			$in =~ s/\d+,\d+//;
		} else {
			$r1 = $r2 = 0;
			until ($r1 > 1) { $r1 = int rand(15); }
			until ($r2 > 1 && $r2 != $r1) { $r2 = int rand(15); }
			$c2 = "$k$r1,$r1"; #fg (rand)
			$c1 = "$k$r2,$r2"; #sh (rand)
			$c3 = "$OO";        #bg (trans)
		}
		## // colors();

		my %db = db1();
  
		## parse();
		$in =~ s/(\S{$maxchars})/$1 /g;
		undef @s0;
		@s0 = split(' ',$in);
		undef @s1;
		$s1n = 0;
		for $n (@s0) {
			$nlen = length($n);
			$slen = length($s1[$s1n]) + $nlen;
			if ($slen <= $maxchars) {
			  $s1[$s1n] .= "$n ";
			} else {
			  $s1n++;
			  $s1[$s1n] .= "$n ";
			}
		}
		### // parse()
		
		## process();
		for $n (@s1) { #each line
			if($reverse) {
				$n = reverse $n;
			}
			$n =~ s/\s$//;
			$n =~ s/^\s//;
			undef @s2;
			@s2 = split(undef,$n);
			my $cur; # current string
			my $tmp;
			for $f (0..8*$scale) {
				for $l (@s2) { #each letter
					$all .= "$c3 $OO";
					if($flip) { $cur = "$db{$l}[(9-$f)/$scale]"; } #line of letter
					else { $cur = "$db{$l}[$f/$scale]"; }
					$whitespace = " " x $scale;
					$cur =~ s/ /$whitespace/g;
					$all .= $cur;
				}
				$all .= "${c3} ";
			
				# Xchat::print $all;
			
				if($mirror) { $all = reverse $all; }
				delaycommand('say '.$all);
				$all = '';
			}
		}
		### // process() 

		select(undef,undef,undef,.1); # probably not necessary unless we care if the loop goes forever 
		$rep--;
    }
  }
  
  return EAT_HEXCHAT;

}



# this just makes it so it looks right on your side
sub delaycommand {
	my $command = $_[0];
	hook_timer( 0,
		sub {
			command($command);
			return REMOVE;
		}
	); 
	return EAT_NONE;
}



#------------------#
#   character db   #
#       lol        #
#------------------#

sub db1 {
return (
" " => [
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
"$c3      ",
],
"\cC" => [
"$c3             ",
"$c1 $c2  $c3  $c1 $c2       $c3",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2            $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2       $c3  $c1 $c2  $c3",
"$c3             ",
],
"\cB" => [
"$c3             ",
"$c1 $c2  $c3  $c1 $c2       $c3",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2            $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2       $c3  $c1 $c2  $c3",
"$c3             ",
],
"\cO" => [
"$c3             ",
"$c1 $c2  $c3  $c1 $c2       $c3",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2  $c3  $c1 $c2  $c3     ",
"$c1 $c2            $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c3     $c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2       $c3  $c1 $c2  $c3",
"$c3             ",
],
"0" => [
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"1" => [
"$c3       ",
"$c3  $c1 $c2  $c3  ",
"$c3 $c1 $c2   $c3  ",
"$c1 $c2    $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c1 $c2      $c3",
"$c3       ",
],
"2" => [
"$c3        ",
"$c3 $c1 $c2     $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3    $c1 $c2  $c3 ",
"$c3   $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3   ",
"$c3 $c1 $c2  $c3    ",
"$c1 $c2       $c3",
"$c3        ",
],
"3" => [
"$c3        ",
"$c3 $c1 $c2     $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3     $c1 $c2  $c3",
"$c3   $c1 $c2   $c3 ",
"$c3     $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2     $c3 ",
"$c3        ",
],
"4" => [
"$c3        ",
"$c3    $c1 $c2  $c3 ",
"$c3   $c1 $c2   $c3 ",
"$c3  $c1 $c2 $c1 $c2  $c3 ",
"$c3 $c1 $c2 $c3 $c1 $c2  $c3 ",
"$c1 $c2       $c3",
"$c3    $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3 ",
"$c3        ",
],
"5" => [
"$c3        ",
"$c1 $c2      $c3 ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2      $c3 ",
"$c3     $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2     $c3 ",
"$c3        ",
],
"6" => [
"$c3        ",
"$c3   $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3   ",
"$c3 $c1 $c2  $c3    ",
"$c1 $c2      $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2     $c3 ",
"$c3        ",
],
"7" => [
"$c3         ",
"$c1 $c2        $c3",
"$c3      $c1 $c2  $c3",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3  $c1 $c2  $c3    ",
"$c3 $c1 $c2  $c3     ",
"$c3         ",
],
"8" => [
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"9" => [
"$c3        ",
"$c3 $c1 $c2     $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2      $c3",
"$c3    $c1 $c2  $c3 ",
"$c3   $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3   ",
"$c3        ",
],
"A" => [
"$c3        ",
"$c3  $c1 $c2   $c3  ",
"$c3 $c1 $c2  $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2       $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3        ",
],
"a" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2     $c3  ",
"$c3     $c1 $c2  $c3 ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3 ",
"$c3 $c1 $c2       $c3",
"$c3         ",
],
"B" => [
"$c3         ",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2       $c3 ",
"$c3         ",
],
"b" => [
"$c3         ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c1 $c2      $c3  ",
"$c1 $c2  $c3  $c1 $c2  $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3 ",
"$c1 $c2      $c3  ",
"$c3         ",
],
"C" => [
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"c" => [
"$c3        ",
"$c3        ",
"$c3        ",
"$c3  $c1 $c2     $c3",
"$c3 $c1 $c2  $c3    ",
"$c1 $c2  $c3     ",
"$c3 $c1 $c2  $c3    ",
"$c3  $c1 $c2     $c3",
"$c3        ",
],
"D" => [
"$c3          ",
"$c1 $c2       $c3  ",
"$c1 $c2  $c3   $c1 $c2  $c3 ",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3 ",
"$c1 $c2       $c3  ",
"$c3          ",
],
"d" => [
"$c3         ",
"$c3      $c1 $c2  $c3",
"$c3      $c1 $c2  $c3",
"$c3  $c1 $c2      $c3",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3",
"$c3  $c1 $c2      $c3",
"$c3         ",
],
"E" => [
"$c3        ",
"$c1 $c2       $c3",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2      $c3 ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2       $c3",
"$c3        ",
],
"e" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  ",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3      ",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"F" => [
"$c3        ",
"$c1 $c2       ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2      $c3 ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c3        ",
],
"f" => [
"$c3      ",
"$c3      ",
"$c3  $c1 $c2   ",
"$c3 $c1 $c2  $c3  ",
"$c1 $c2     ",
"$c3 $c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3  ",
"$c3      ",
],
"G" => [
"$c3          ",
"$c3  $c1 $c2      $c3 ",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3       ",
"$c1 $c2  $c3  $c1 $c2    $c3",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3",
"$c3  $c1 $c2      $c3 ",
"$c3          ",
],
"g" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2       $c3",
"$c3      $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
],
"H" => [
"$c3         ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2        $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3         ",
],
"h" => [
"$c3         ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3         ",
],
"I" => [
"$c3       ",
"$c1 $c2      $c3",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3  ",
"$c1 $c2      $c3",
"$c3       ",
],
"i" => [
"$c3     ",
"$c3 $c1 $c2  $c3 ",
"$c3     ",
"$c1 $c2   $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2    ",
"$c3     ",
],
"J" => [
"$c3        ",
"$c3 $c1 $c2      ",
"$c3    $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3 ",
"$c1 $c2  $c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2    $c3  ",
"$c3        ",
],
"j" => [
"$c3       ",
"$c3    $c1 $c2  ",
"$c3       ",
"$c3   $c1 $c2   ",
"$c3    $c1 $c2  ",
"$c3    $c1 $c2  ",
"$c3    $c1 $c2  ",
"$c1 $c2  $c3 $c1 $c2  ",
"$c3 $c1 $c2    $c3 ",
],
"K" => [
"$c3        ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2  $c3 ",
"$c1 $c2  $c1 $c2  $c3  ",
"$c1 $c2    $c3   ",
"$c1 $c2  $c1 $c2  $c3  ",
"$c1 $c2  $c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3        ",
],
"k" => [
"$c3        ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3  $c1 $c2  ",
"$c1 $c2  $c3 $c1 $c2  $c3 ",
"$c1 $c2     $c3  ",
"$c1 $c2  $c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  ",
"$c3        ",
],
"L" => [
"$c3        ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2       $c3",
"$c3        ",
],
"l" => [
"$c3     ",
"$c1 $c2   $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2    ",
"$c3     ",
],
"M" => [
"$c3            ",
"$c1 $c2  $c3      $c1 $c2  $c3",
"$c1 $c2   $c3    $c1 $c2   $c3",
"$c1 $c2    $c3  $c1 $c2    $c3",
"$c1 $c2  $c1 $c2  $c1 $c2  $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2   $c3 $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2 $c3  $c1 $c2  $c3",
"$c1 $c2  $c3      $c1 $c2  $c3",
"$c3            ",
],
"m" => [
"$c3          ",
"$c3          ",
"$c3          ",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3 ",
"$c1 $c2    $c1 $c2    $c3",
"$c1 $c2  $c1 $c2   $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2 $c3 $c1 $c2  $c3",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c3          ",
],
"N" => [
"$c3           ",
"$c1 $c2   $c3    $c1 $c2  ",
"$c1 $c2    $c3   $c1 $c2  ",
"$c1 $c2  $c1 $c2  $c3  $c1 $c2  ",
"$c1 $c2  $c3 $c1 $c2  $c3 $c1 $c2  ",
"$c1 $c2  $c3  $c1 $c2  $c1 $c2  ",
"$c1 $c2  $c3   $c1 $c2    ",
"$c1 $c2  $c3    $c1 $c2   ",
"$c3           ",
],
"n" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3         ",
],
"O" => [
"$c3           ",
"$c3  $c1 $c2      $c3  ",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c3  $c1 $c2      $c3  ",
"$c3           ",
],
"o" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"P" => [
"$c3         ",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
"$c3         ",
],
"p" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2       $c3 ",
"$c1 $c2  $c3      ",
"$c1 $c2  $c3      ",
],
"Q" => [
"$c3           ",
"$c3  $c1 $c2      $c3  ",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c1 $c2  $c3",
"$c3 $c1 $c2  $c3  $c1 $c2   $c3 ",
"$c3  $c1 $c2      $c3  ",
"$c3       $c1 $c2  $c3 ",
],
"q" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3 $c1 $c2      $c3 ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2       $c3",
"$c3      $c1 $c2  $c3",
"$c3      $c1 $c2  $c3",
],
"R" => [
"$c3           ",
"$c1 $c2       $c3   ",
"$c1 $c2  $c3   $c1 $c2  $c3  ",
"$c1 $c2  $c3   $c1 $c2  $c3  ",
"$c1 $c2       $c3   ",
"$c1 $c2  $c3   $c1 $c2  $c3  ",
"$c1 $c2  $c3    $c1 $c2  $c3 ",
"$c1 $c2  $c3     $c1 $c2  ",
"$c3           ",
],
"r" => [
"$c3        ",
"$c3        ",
"$c3        ",
"$c3 $c1 $c2     $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c1 $c2  $c3     ",
"$c3        ",
],
"S" => [
"$c3        ",
"$c3 $c1 $c2     $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3     ",
"$c3 $c1 $c2     $c3 ",
"$c3     $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2     $c3 ",
"$c3        ",
],
"s" => [
"$c3       ",
"$c3       ",
"$c3       ",
"$c3 $c1 $c2     $c3",
"$c1 $c2  $c3    ",
"$c3 $c1 $c2    $c3 ",
"$c3    $c1 $c2  $c3",
"$c1 $c2     $c3 ",
"$c3       ",
],
"T" => [
"$c3         ",
"$c1 $c2        $c3",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3         ",
],
"t" => [
"$c3       ",
"$c3       ",
"$c3 $c1 $c2  $c3   ",
"$c1 $c2     $c3 ",
"$c3 $c1 $c2  $c3   ",
"$c3 $c1 $c2  $c3   ",
"$c3 $c1 $c2  $c1 $c2  ",
"$c3  $c1 $c2   $c3 ",
"$c3       ",
],
"U" => [
"$c3           ",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c3  $c1 $c2      $c3  ",
"$c3           ",
],
"u" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c1 $c2  $c3   $c1 $c2  $c3",
"$c3 $c1 $c2      $c3 ",
"$c3         ",
],
"V" => [
"$c3             ",
"$c1 $c2 $c3         $c1 $c2 ",
"$c1 $c2  $c3       $c1 $c2  ",
"$c3 $c1 $c2  $c3     $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3   $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3 $c1 $c2  $c3   ",
"$c3    $c1 $c2    $c3    ",
"$c3     $c1 $c2  $c3     ",
"$c3             ",
],
"v" => [
"$c3            ",
"$c3            ",
"$c3            ",
"$c1 $c2  $c3      $c1 $c2  ",
"$c3 $c1 $c2  $c3    $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3  $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c1 $c2  $c3   ",
"$c3    $c1 $c2   $c3    ",
"$c3            ",
],
"W" => [
"$c3           ",
"$c1 $c2  $c3     $c1 $c2  ",
"$c1 $c2  $c3     $c1 $c2  ",
"$c1 $c2  $c3     $c1 $c2  ",
"$c1 $c2  $c3 $c1 $c2  $c3 $c1 $c2  ",
"$c1 $c2  $c1 $c2    $c1 $c2  ",
"$c1 $c2    $c3 $c1 $c2    ",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c3           ",
],
"w" => [
"$c3          ",
"$c3          ",
"$c3          ",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2 $c3 $c1 $c2  $c3",
"$c1 $c2  $c1 $c2   $c1 $c2  $c3",
"$c1 $c2    $c1 $c2    $c3",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3 ",
"$c3          ",
],
"X" => [
"$c3          ",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c1 $c2  $c3  ",
"$c3   $c1 $c2   $c3   ",
"$c3  $c1 $c2  $c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3  $c1 $c2  $c3 ",
"$c1 $c2  $c3    $c1 $c2  $c3",
"$c3          ",
],
"x" => [
"$c3        ",
"$c3        ",
"$c3        ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3 $c1 $c2  $c1 $c2  $c3 ",
"$c3   $c2   $c3  ",
"$c3 $c1 $c2  $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3        ",
],
"Y" => [
"$c3           ",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c3   $c1 $c2    $c3   ",
"$c3    $c1 $c2  $c3    ",
"$c3    $c1 $c2  $c3    ",
"$c3    $c1 $c2  $c3    ",
"$c3           ",
],
"y" => [
"$c3           ",
"$c3           ",
"$c3           ",
"$c1 $c2  $c3     $c1 $c2  $c3",
"$c3 $c1 $c2  $c3   $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c3   $c1 $c2    $c3   ",
"$c3    $c1 $c2  $c3    ",
"$c3   $c1 $c2  $c3     ",
],
"Z" => [
"$c3         ",
"$c1 $c2        $c3",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3  $c1 $c2  $c3    ",
"$c3 $c1 $c2  $c3     ",
"$c1 $c2        $c3",
"$c3         ",
],
"z" => [
"$c3          ",
"$c3          ",
"$c3          ",
"$c1 $c2        $c3 ",
"$c3     $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3    ",
"$c3 $c1 $c2  $c3      ",
"$c1 $c2        $c3 ",
"$c3          ",
],
"\~" => [
"$c3             ",
"$c3             ",
"$c3             ",
"$c3  $c1 $c2    $c3   $c1 $c2  $c3",
"$c3 $c1 $c2  $c3 $c1 $c2  $c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3   $c1 $c2    $c3  ",
"$c3             ",
"$c3             ",
"$c3             ",
],
"\`" => [
"$c3    ",
"$c1 $c2  $c3 ",
"$c3 $c1 $c2  ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
],
"\!" => [
"$c3         ",
"$c3      $c1 $c2  $c3",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3  $c1 $c2  $c3    ",
"$c3         ",
"$c1 $c2  $c3      ",
"$c3         ",
],
"\@" => [
"$c3            ",
"$c3  $c1 $c2       $c3  ",
"$c3 $c1 $c2  $c3    $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3 $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2  $c3  $c1 $c2  $c3",
"$c1 $c2  $c3  $c1 $c2     $c3 ",
"$c3 $c1 $c2  $c3        ",
"$c3  $c1 $c2       $c3  ",
"$c3            ",
],
"\#" => [
"$c3           ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c1 $c2          ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c1 $c2          ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c3  $c1 $c2  $c3 $c1 $c2  $c3  ",
"$c3           ",
],
"\$" => [
"$c3    $c1 $c2 $c3    ",
"$c3 $c1 $c2       $c3 ",
"$c1 $c2  $c3 $c1 $c2 $c3 $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2 $c3    ",
"$c3 $c1 $c2       $c3 ",
"$c3    $c1 $c2 $c3 $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2 $c3 $c1 $c2  $c3",
"$c3 $c1 $c2       $c3 ",
"$c3    $c1 $c2 $c3    ",
],
"\%" => [
"$c3         ",
"$c1 $c2  $c3   $c1 $c2  ",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3  $c1 $c2  $c3    ",
"$c3 $c1 $c2  $c3     ",
"$c1 $c2  $c3   $c1 $c2  ",
"$c3         ",
],
"\^" => [
"$c3        ",
"$c3        ",
"$c3  $c1 $c2   $c3  ",
"$c3 $c1 $c2  $c1 $c2  $c3 ",
"$c1 $c2  $c3  $c1 $c2  $c3",
"$c3        ",
"$c3        ",
"$c3        ",
"$c3        ",
],
"\&" => [
"$c3           ",
"$c3  $c1 $c2    $c3    ",
"$c3 $c1 $c2  $c3 $c1 $c2  $c3   ",
"$c3  $c1 $c2    $c3    ",
"$c3 $c1 $c2  $c3 $c1 $c2  $c3   ",
"$c1 $c2  $c3   $c1 $c2  $c3  ",
"$c1 $c2  $c3    $c1 $c2  $c3 ",
"$c3 $c1 $c2      $c1 $c2  $c3",
"$c3           ",
],
"\*" => [
"$c3     ",
"$c3     ",
"$c1 $c2 $c3 $c1 $c2 ",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2 $c3 $c1 $c2 ",
"$c3     ",
"$c3     ",
"$c3     ",
"$c3     ",
],
"\(" => [
"$c3     ",
"$c3  $c1 $c2  $c3",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3",
"$c3     ",
],
"\)" => [
"$c3     ",
"$c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  ",
"$c3     ",
],
"_" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
"$c1 $c2        $c3",
"$c3         ",
],
"\-" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
"$c1 $c2        $c3",
"$c3         ",
"$c3         ",
"$c3         ",
"$c3         ",
],
"\+" => [
"$c3         ",
"$c3         ",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c1 $c2        $c3",
"$c3   $c1 $c2  $c3   ",
"$c3   $c1 $c2  $c3   ",
"$c3         ",
"$c3         ",
],
"\=" => [
"$c3         ",
"$c3         ",
"$c3         ",
"$c1 $c2        $c3",
"$c3         ",
"$c1 $c2        $c3",
"$c3         ",
"$c3         ",
"$c3         ",
],
"\|" => [
"$c3   ",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c1 $c2  $c3",
"$c3   ",
],
"\\" => [
"$c3         ",
"$c1 $c2  $c3      ",
"$c3 $c1 $c2  $c3     ",
"$c3  $c1 $c2  $c3    ",
"$c3   $c1 $c2  $c3   ",
"$c3    $c1 $c2  $c3  ",
"$c3     $c1 $c2  $c3 ",
"$c3      $c1 $c2  $c3",
"$c3         ",
],
"\[" => [
"$c3     ",
"$c1 $c2    $c3",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c1 $c2  $c3  ",
"$c1 $c2    $c3",
"$c3     ",
],
"\]" => [
"$c3     ",
"$c1 $c2    $c3",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c3  $c1 $c2  $c3",
"$c1 $c2    $c3",
"$c3     ",
],
"\{" => [
"$c3     ",
"$c3 $c1 $c2   $c3",
"$c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  ",
"$c3 $c1 $c2  $c3 ",
"$c1 $c2  $c3  ",
"$c3 $c1 $c2   $c3",
"$c3     ",
],
"\}" => [
"$c3     ",
"$c1 $c2   $c3 ",
"$c3  $c1 $c2  $c3",
"$c3 $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3",
"$c3 $c1 $c2  $c3 ",
"$c3  $c1 $c2  $c3",
"$c1 $c2   $c3 ",
"$c3     ",
],
"\:" => [
"$c3     ",
"$c3     ",
"$c3     ",
"$c3 $c1 $c2  $c3 ",
"$c3     ",
"$c3     ",
"$c3 $c1 $c2  $c3 ",
"$c3     ",
"$c3     ",
],
"\;" => [
"$c3     ",
"$c3     ",
"$c3     ",
"$c3 $c1 $c2  $c3 ",
"$c3     ",
"$c3     ",
"$c3 $c1 $c2  $c3 ",
"$c3  $c1 $c2 $c3 ",
"$c3     ",
],
"\'" => [
"$c3    ",
"$c3 $c1 $c2  ",
"$c1 $c2  $c3 ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
"$c3    ",
],
"\"" => [
"$c3       ",
"$c1 $c2  $c3 $c1 $c2  $c3",
"$c1 $c2  $c3 $c1 $c2  $c3",
"$c3       ",
"$c3       ",
"$c3       ",
"$c3       ",
"$c3       ",
"$c3       ",
],
"\<" => [
"$c3       ",
"$c3       ",
"$c3    $c1 $c2  $c3",
"$c3  $c1 $c2  $c3  ",
"$c1 $c2  $c3    ",
"$c3  $c1 $c2  $c3  ",
"$c3    $c1 $c2  $c3",
"$c3       ",
"$c3       ",
],
"\>" => [
"$c3       ",
"$c3       ",
"$c1 $c2  $c3    ",
"$c3  $c1 $c2  $c3  ",
"$c3    $c1 $c2  $c3",
"$c3  $c1 $c2  $c3  ",
"$c1 $c2  $c3    ",
"$c3       ",
"$c3       ",
],
"\?" => [
"$c3         ",
"$c3  $c1 $c2     $c3 ",
"$c3 $c1 $c2  $c3  $c1 $c2  ",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3         ",
"$c3 $c1 $c2  $c3     ",
"$c3         ",
],
"\," => [
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c1 $c2  $c3",
"$c3 $c1 $c2 $c3",
],
"\." => [
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c3   ",
"$c1 $c2  ",
"$c3   ",
],
"\/" => [
"$c3         ",
"$c3      $c1 $c2  $c3",
"$c3     $c1 $c2  $c3 ",
"$c3    $c1 $c2  $c3  ",
"$c3   $c1 $c2  $c3   ",
"$c3  $c1 $c2  $c3    ",
"$c3 $c1 $c2  $c3     ",
"$c1 $c2  $c3      ",
"$c3         ",
],
);
}
