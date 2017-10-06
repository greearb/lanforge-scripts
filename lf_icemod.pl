#!/usr/bin/perl

# This program is used to stress test the LANforge system, and may be used as
# an example for others who wish to automate LANforge tests.

# Written by Candela Technologies Inc.
#  Updated by: greearb@candelatech.com
#
#

use strict;

# Un-buffer output
$| = 1;

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

my $fail_msg = "";
my $manual_check = 0;

my $cmd_log_name = "lf_icemod.txt";

########################################################################
# Nothing to configure below here, most likely.
########################################################################

my $usage = "$0  --endp_name {name}
                 [--cx {name}]
                 [--speed {speed in bps}]
                 [--drop_pm { 0 - 1000000}]
                 [--latency { 0 - 1000000}]
                 [--switch new_cx_to_run ]
                 [--manager { network address of LANforge manager} ]
                 [--pcap { dir-name | off } ]
                 [--load { db-name } ]
                 [--state { running | switch | quiesce | stopped | deleted } ]

Example:
 lf_icemod.pl --manager lanforge1 --endp_name t1-A --speed 154000 --drop_pm 10000 --latency 35
 lf_icemod.pl --manager 192.168.100.223 --switch t3
 lf_icemod.pl --state running --cx t3
 lf_icemod.pl --pcap /tmp/endp-a --endp_name t1-A
 lf_icemod.pl --load my_db
";

my $i = 0;

GetOptions 
(
        'endp_name|e=s'  => \$endp_name,
        'speed|s=i'     => \$speed,
        'cx|c=s'   => \$cx,
        'drop_pm|d=i'   => \$drop_pm,
        'latency|l=i'   => \$latency,
        'jitter|j=i'    => \$jitter,
        'switch|w=s'    => \$switch,
        'manager|m=s'    => \$lfmgr_host,
        'pcap|p=s'    => \$pcap,
        'load|L=s'    => \$load,
        'state|S=s'    => \$state,
        'quiet|q=i'    => \$quiet,

) || die("$usage");

if (! ($quiet == 0xffff)) {
  open(CMD_LOG, ">$cmd_log_name") or die("Can't open $cmd_log_name for writing...\n");
  if (! ($quiet & 0x2)) {
    print "History of all commands can be found in $cmd_log_name\n";
  }
}

# Open connection to the LANforge server.

my $t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
			Timeout => 20);

$t->open(Host    => $lfmgr_host,
	 Port    => $lfmgr_port,
	 Timeout => 10);

$t->waitfor("/btbits\>\>/");

my $dt = "";

# Configure our utils.
my $utils = new LANforge::Utils();
$utils->telnet($t);         # Set our telnet object.
$utils->cli_send_silent(0); # Do show input to CLI
if ($quiet & 0x1) {
  $utils->cli_rcv_silent(1);  # Repress output from CLI ??
}
else {
  $utils->cli_rcv_silent(0);  # Repress output from CLI ??
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
  if (($pcap eq "OFF") ||
      ($pcap eq "off")) {
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

