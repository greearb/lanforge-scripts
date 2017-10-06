#!/usr/bin/perl -w
use strict;
use warnings;
use diagnostics;

$| = 1;
use Net::Telnet ();
use LANforge::Utils;
use Getopt::Long;

package main;
# we want to take the list of ports on ARGV and wait until they are up

exit 0 if (@ARGV < 1);

my $card       = 1;
my $mgr        = "localhost";
my $mgr_port   = "4001";
my @port_list  = ();
our $quiet     = 1;
my $require_ip = 1;
our $verbose   = -1;
my %down_count = ();
my $shove_level = 4; # count at which a lf_portmod trigger gets called

sub help() {
   print "$0 --mgr $mgr \\
      --mgr_port $mgr_port \\
      --card $card \\
      --quiet $::quiet \\
      --require_ip $require_ip \\
      --verbose 0|1 \\
      --port sta1 -p sta2 -p sta3...\n";
}

# should move to Utils
sub fmt_port_up_down {
   my ($resource, $port_id, $state) = @_;

   my $cur_flags        = 0;
   if ($state eq "down") {
      $cur_flags        |= 0x1;       # port down
   }

   # Specify the interest flags so LANforge knows which flag bits to pay attention to.
   my $ist_flags        = 0;
   $ist_flags           |= 0x2;       # check current flags
   $ist_flags           |= 0x800000;  # port down

   my $cmd = $::utils->fmt_cmd("set_port", 1, $resource, $port_id, "NA",
           "NA", "NA", "NA", "$cur_flags",
           "NA", "NA", "NA", "NA", "$ist_flags");
   return $cmd;
}


my $p = new Getopt::Long::Parser;
$p->configure('pass_through');

GetOptions (
   'mgr:s'           => \$mgr,
   'mgr_port:i'      => \$mgr_port,
   'card|resource:i' => \$card,
   'quiet|q:s'       => \$::quiet,
   'ports|p:s@'      => \@port_list,
   'require_ip:i'    => \$require_ip,
   'v:i'             => \$verbose,
) || die help();

if ($::quiet eq "0") {
   $::quiet = "no";
}
elsif ($::quiet eq "1") {
   $::quiet = "yes";
}

my $t = new Net::Telnet(
   Prompt   => '/default\@btbits\>\>/',
   Timeout  => 20);

$t->open(Host => $mgr,
      Port    => $mgr_port,
      Timeout => 10);

$t->waitfor("/btbits\>\>/");
# Configure our utils.
our $utils = new LANforge::Utils();
$::utils->telnet($t);
$::utils{'quiet'} = $::quiet;
if ($::utils->isQuiet()) {
  if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
    $::utils->cli_send_silent(0);
  }
  else {
    $::utils->cli_send_silent(1); # Do not show input to telnet
  }
  $::utils->cli_rcv_silent(1);  # Repress output from telnet
}
else {
  $::utils->cli_send_silent(0); # Show input to telnet
  $::utils->cli_rcv_silent(0);  # Show output from telnet
}

die("No resource defined, bye.") if (! defined $card);
my $num_ports_down = @port_list;
my $state = undef;
my $ip = undef;
if ($verbose > 2) {
   print "\nWe have ".(0+@port_list)." ports: ".join(",", sort @port_list), "\n";
}

while( $num_ports_down > 0 ) {
   my @ports_up = ();
   my @ports_down = ();
   for my $port (sort @port_list) {
      my $statblock = $utils->doAsyncCmd($utils->fmt_cmd("nc_show_port", 1, $card, $port));
      #print $statblock;
      
      print " $port " if ($verbose > 3);
      ($state) = $statblock =~ /^\s+Current:\s+([^ ]+)/m;
      ($ip)    = $statblock =~ /^\s+IP:\s+([^ ]+)/m;

      if (! defined $state) {
         print "STATE undefined: $statblock\n"; 
      }
      if (! defined $ip) {
         print "IP undefined: $statblock\n"; 
      }

      #print "\n$port is [$state] ";# if ($quiet =~ /0|no/i);
      #print "\n$ip has [$ip] "   ;#if ($quiet =~ /0|no/i);
      if ($require_ip) {
         if (($state !~ /down/i) && ($ip !~ /0\.0\.0\.0/)) {
            $num_ports_down--;
            push(@ports_up, $port);
            print "+" if ($verbose > 0);
            $down_count{$port} = 0;
         }
         else {
            print "-" if ($verbose > 0);
            push(@ports_down, $port);
            $down_count{$port}++;
         }
      }
      else {
         if ($state =~ /down/i) {
            push(@ports_down, $port);
            print "-" if ($verbose > 0);
            $down_count{$port}++;
         }
         else {
            $num_ports_down--;
            print "=" if ($verbose > 0);
            push(@ports_up, $port);
            $down_count{$port} = 0;
         }
      }
   }
   if ($verbose > 1) {
      my $num_ports = @port_list;
      my $num_ports_up = @ports_up;
      print "\n\n${num_ports_up}/${num_ports}  Ports up:   ".join(", ", @ports_up   )."\n"
         if ($verbose > 2);
      print "\n${num_ports_down}/${num_ports} Ports down: ".join(", ", @ports_down )."\n";
   }
   if ($num_ports_down > 0) {
      for my $port (sort keys %down_count) {
         my $strikes = $down_count{$port};
         if ($strikes >= $shove_level) {
            print "Shoving port $port\n";
            my $cli_cmd = fmt_port_up_down($card, $port, "down");
            $utils->doCmd($cli_cmd);
            sleep(0.5);
            $cli_cmd = fmt_port_up_down($card, $port, "up");
            $utils->doCmd($cli_cmd);
            $down_count{$port} = 0;
         }
      }
      $num_ports_down = @port_list;
      print " ";
      print "Napping...\n" if ($verbose > 1);
      sleep 4;
   }
}
print "All ports up.\n" if ($verbose > 0);
#
