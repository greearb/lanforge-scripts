#!/usr/bin/perl -w

# This program is used to stress test the LANforge system, and may be used as
# an example for others who wish to automate LANforge tests.

# Written by Candela Technologies Inc.
#  Updated by: greearb@candelatech.com
#
#

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
our $q = q(');
our $Q = q(");
# Un-buffer output
$| = 1;

if ( -d "./LANforge" ) {
   use lib ".";
   use lib "./LANforge";
}
elsif ( -d "/home/lanforge/scripts/LANforge" ) {
   use lib "/home/lanforge/scripts";
   use lib "/home/lanforge/scripts/LANforge";
}

use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils;
use Net::Telnet ();
use Getopt::Long;

my $lfmgr_host = "localhost";
my $lfmgr_port = 4001;

my $shelf_num = 1;

# Specify 'card' numbers for this configuration.
my $ice_card = 1;

# The ICE ports, on ice_card
my $ice1 = 1;
my $ice2 = 2;

my $test_mgr = "vanilla-ice"; # Couldn't resist!

my $report_timer = 1000; # XX/1000 seconds

# Default values for ye ole cmd-line args.


my $port = "";
my $endp_name = "";
my $speed = "";
my $drop_pm = "";
my $latency = "";
my $jitter = "";
my $switch = "";
my $pcap = "";
my $load = "";
my $state = "";
my $cx = "";
my $quiet = 0;
my $description = "";
my $fail_msg = "";
my $manual_check = 0;
my $cpu_id = "NA";
my $wle_flags = 0;

########################################################################
# Nothing to configure below here, most likely.
########################################################################

my $usage = qq($0  [--manager { hostname or address of LANforge manager } ]
                 [--resource { resource number } ]
                 [--port {port name} ]
                 [--endp_name { name } ]
                 [--description { ${Q}stuff in quotes${Q} } ]
                 [--cx { name } ]
                 [--speed { speed in bps } ]
                 [--drop_pm { 0 - 1000000 } ]
                 [--latency { 0 - 1000000 } ]
                 [--switch new_cx_to_run ]
                 [--pcap { dir-name | off } ]
                 [--load { db-name } ]
                 [--state { running | switch | quiesce | stopped | deleted } ]

Example:
 lf_icemod.pl --manager lanforge1 --new_endp t1-A --speed 256000 --drop_pm 100 --latency 35 --description ${Q}link one${Q}
 lf_icemod.pl --mgr lanforge1 --new_cx "t1" --endps t1-A,t1-B
 lf_icemod.pl --mgr lanforge1 --endp_name t1-A --speed 154000 --drop_pm 10000 --latency 35
 lf_icemod.pl --mgr 192.168.100.223 --switch t3
 lf_icemod.pl --state running --cx t3
 lf_icemod.pl --pcap /tmp/endp-a --endp_name t1-A
 lf_icemod.pl --load my_db
);

if (@ARGV < 2) {
   print "$usage\n";
   exit 0;
}

my $i = 0;
my $show_help;
my $resource = 1;
my $new_endp = "";
my $new_cx = "";
my $endps = "";

GetOptions (
   'help|h'          => \$show_help,
   'endp_name|e=s'   => \$endp_name,
   'desc|description=s'   => \$description,
   'speed|s=i'       => \$speed,
   'cx|c=s'          => \$cx,
   'drop_pm|d=i'     => \$drop_pm,
   'latency|l=i'     => \$latency,
   'jitter|j=i'      => \$jitter,
   'switch|w=s'      => \$switch,
   'new_endp=s'      => \$new_endp,
   'new_cx=s'        => \$new_cx,
   'endps=s'         => \$endps,
   'port=s'          => \$port,
   'manager|mgr|m=s' => \$lfmgr_host,
   'pcap|p=s'        => \$pcap,
   'load|o=s'        => \$load,
   'state|a=s'       => \$state,
   'card|resource|r=i' => \$resource,
   'wle_flags=i'     => \$wle_flags,
   'quiet|q=i'       => \$quiet,
) || die("$usage");

if ($show_help) {
   print $usage;
   exit 0;
}

# Open connection to the LANforge server.
my $t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
         Timeout => 20);

$t->open( Host    => $lfmgr_host,
          Port    => $lfmgr_port,
          Timeout => 10);

$t->waitfor("/btbits\>\>/");

my $dt = "";

my $utils = new LANforge::Utils();
$utils->telnet($t);
$utils->cli_send_silent(0); # Show input to CLI
if ($quiet & 0x1) {
  $utils->cli_rcv_silent(1);
}
else {
  $utils->cli_rcv_silent(0);
}

# $utils->doCmd("log_level 63");
my $cmd;

if ($load ne "") {
  $cmd = "load $load overwrite";
  $utils->doCmd($cmd);
  my @rslt = $t->waitfor("/LOAD-DB:  Load attempt has been completed./");
  if (!($quiet & 0x1)) {
    print @rslt;
    print "\n";
  }
  exit(0);
}

if ($new_cx ne "") {
   die("please set the endpoints for new wanlink cx; $usage")
      unless ((defined $endps) && ($endps ne ""));

   die("please specify two endpoints joined by a comma: end1-A,end1-B; $usage")
      unless ($endps =~ /^\S+,\S+$/);
   my @ends= split(',', $endps);
   $cmd = "add_cx $new_cx default_tm $ends[0] $ends[1]";
   $utils->doCmd($cmd);
   exit(0);
}

if ($new_endp ne "") {
   die("please set the resource for new wanlink endpoint; $usage")
      unless ((defined $resource) && ($resource ne ""));
   die("please set latency for new wanlink endpoint; $usage")
      unless ((defined $latency) && ($latency ne ""));
   die("please set drop_pm for new wanlink endpoint; $usage")
      unless ((defined $drop_pm) && ($drop_pm ne ""));
   die("please set port for new wanlink endpoint; $usage")
      unless ((defined $port) && ($port ne ""));

   $wle_flags = "NA"
      if (($wle_flags == 0) || ($wle_flags eq ""));
   $cpu_id = "NA"
      if ($cpu_id eq "");
   $description = "NA"
      if ($description eq "");

   $cmd = "add_wl_endp $new_endp 1 $resource $port $latency $speed '$description' $cpu_id $wle_flags";
   $utils->doCmd($cmd);
   exit(0);
}

if ($switch ne "") {
  $cmd = "set_cx_state all $switch SWITCH";
  $utils->doCmd($cmd);
  exit(0);
}

if ((length($endp_name) == 0) && (length($cx) == 0)) {
  print "ERROR:  Must specify endp or cx name.\n";
  die("$usage");
}

if ($pcap ne "") {
  if ($pcap =~ /^OFF$/i) {
    $cmd = "set_wanlink_pcap $endp_name off";
  }
  else {
    $cmd = "set_wanlink_pcap $endp_name ON $pcap";
  }
  $utils->doCmd($cmd);
  exit(0);
}

if ($state ne "") {
  $cmd = "set_cx_state all $cx $state";
  $utils->doCmd($cmd);
  exit(0);
}

# Assumes that the endpoint already exists.
if ($latency eq "") {
  $latency = "NA";
}
if ($speed eq "") {
  $speed = "NA";
}
if ($jitter eq "") {
  $jitter = "NA";
}

if ($drop_pm eq "") {
  $drop_pm = "NA";
}

$cmd = "set_wanlink_info $endp_name $speed $latency $jitter NA NA $drop_pm NA";
$utils->doCmd($cmd);

exit(0);
