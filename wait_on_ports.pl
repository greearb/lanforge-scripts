#!/usr/bin/perl -w
## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ##
## Use this script wait on list of ports until they are up                 ##
## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ##
use strict;
use warnings;
use diagnostics;

$| = 1;
use Net::Telnet ();
use LANforge::Utils;
use Getopt::Long;

package main;
# if number of ports to probe is greater than this, probe all ports on card
# so as to reduce chance of timeout
our $batch_thresh = 3;
# if caching_ok > 0, use a c_show_port to get older results faster
our $use_caching  = 0;
our $card         = 1; # resource id
my $mgr           = "localhost";
my $mgr_port      = "4001";
our @port_list    = ();
our $quiet        = 1;
our $require_ip   = 1;
our $verbose      = -1;
our %down_count   = ();
our $shove_level  = 4; # count at which a lf_portmod trigger gets called

sub help() {
   print "$0 --mgr      # manager [$mgr] [default values] in brackets \\
      --mgr_port              # manager port [$mgr_port] \\
      --resource|resrc|card   # resource id [$card] \\
      --quiet yes|no|0|1      # show CLI protocol [$::quiet] \\
      --require_ip 0|1        # require a port to have an IP to be 'up' [$require_ip] \\
      --shove_level           # retry up/down ports [$shove_level] \\
      --verbose 0|1+          # debugging output  [$verbose] \\
      --batch_level           # query all port statuses if querying more than this many [$batch_thresh] \\
      --use_caching 0|1       # faster to use older port status [$use_caching] \\
      --port sta1 -p sta2 -p sta3... \\
      --help|-h \n";
}

if (@ARGV < 1) {
   help();
   exit 0;
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

my $show_help = 0;
my $p = new Getopt::Long::Parser;
$p->configure('pass_through');

GetOptions (
   'mgr:s'           => \$mgr,
   'mgr_port:i'      => \$mgr_port,
   'card|resource:i' => \$::card,
   'quiet|q:s'       => \$::quiet,
   'ports|p:s@'      => \@::port_list,
   'require_ip:i'    => \$::require_ip,
   'batch_level:i'   => \$::batch_thresh,
   'use_caching:i'   => \$::use_caching,
   'shove_level:i'   => \$::shove_level,
   'v:i'             => \$::verbose,
   'help|h'          => \$show_help,
) || die help();

if ($show_help) {
   help();
   exit 0;
}
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
my $num_ports_down = @::port_list;
my $state = undef;
my $ip = undef;
if ($verbose > 2) {
   print "\nWe have ".(0+@::port_list)." ports: ".join(",", sort @::port_list), "\n";
}
# performance and timeouts: just probing a port or two is pretty easy, but repeatedly calling nc_show_port
# can chance a timeout, which is pretty messy. Setting a batch-level threshold to check nc_show_port 1 $c ALL
# should reduce chances of timeout

while( $num_ports_down > 0 ) {
   my @ports_up = ();
   my @ports_down = ();
   for my $port (sort @::port_list) {
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
      my $num_ports = @::port_list;
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
      $num_ports_down = @::port_list;
      print " ";
      print "Napping...\n" if ($verbose > 1);
      sleep 4;
   }
}
print "All ports up.\n" if ($verbose > 0);
#
