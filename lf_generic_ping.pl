#!/usr/bin/perl -w
#
# Use this script to generate a batch of Generic lfping endpoints
# 
# Usage:
# ./lf_generic_ping.pl --mgr $mgr --resource $resource --dest $dest_ip -i $intf -i $intf -i $intf
# You should be able to place 1000 interfaces in the list
#
# Or all interfaces on a radio
# ./lf_generic_ping.pl --mgr $mgr --resource $resource --dest $dest_ip --radio $wiphy
#
# Or all interfaces matching a pattern:
# ./lf_generic_ping.pl -m $mgr -r $resource -d $dest_ip --match sta3+
#
package main;
use strict;
use diagnostics;
use warnings;
use Carp;
$SIG{ __DIE__ }   = sub { Carp::confess( @_ )};
$SIG{ __WARN__ }  = sub { Carp::confess( @_ )};
use Getopt::Long;
use Cwd qw(getcwd);
my $cwd = getcwd();
use lib '/home/lanforge/scripts';
use List::Util qw(first);
use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils;
use Net::Telnet ();

our $dest_ip_addr = "0.0.0.0";
our $log_cli = "unset"; # use ENV{'LOG_CLI'}

our $usage = qq( Usage:
 ./$0 --mgr {host-name | IP} 
   --mgr_port {ip port}
   --resource {resource}
   --dest {destination IP}
   --interface|-intf|-int|-i {source interface}
   --radio {wiphy}
   --match {simple pattern, no stars or questions marks, just '+'}
 You should be able to place 1000 interfaces in the list

 A set of interfaces: 
 ./$0 --mgr localhost --resource 1 --dest 192.168.0.1 -i wlan0 -i sta3000

 All interfaces on a parent radio
 ./$0 --mgr localhost --resource 1 --dest 192.168.0.1 --radio wiphy0

 All interfaces matching a pattern:
 ./$0 -m localhost -r 1 -d 192.168.0.1 --match sta3+
);

my $shelf_num = 1;
our $report_timer = 1000;
our $test_mgr = "default_tm";
our $resource = 1;
our $lfmgr_host = "localhost";
our $lfmgr_port = 4001;
our $quiet = 1;
our $dest_ip = undef;
our @interfaces = ();
our $radio = "";
our $pattern = "";

my $help;

if (@ARGV < 2) {
   print $usage;
   exit 0;
}
GetOptions
(
  'mgr|m=s'                   => \$::lfmgr_host,
  'mgr_port|p=i'              => \$lfmgr_port,
  'resource|r=i'              => \$::resource,
  'quiet|q=s'                 => \$::quiet,
  'radio|o=s'                 => \$::radio,
  'match=s'                   => \$::pattern,
  'interface|intf|int|i=s'    => \@::interfaces,
  'dest_ip|dest|d=s'          => \$::dest_ip,
  'help|h|?'                  => \$help,
) || (print($usage), exit(1));

if ($help) {
   print($usage) && exit(0);
}

if (defined $::radio && $radio ne "") {
   # collect all stations on that radio
   # add them to @interfaces
}

if (defined $::pattern && $pattern ne "") {
   # collect all stations on that resource
   # add them to @interfaces
}


if (@interfaces < 1) {
   print STDERR "One or more interfaces required.\n";
   print $usage;
   exit(1);
}

print "Using these interfaces: \n";
print " ".join(",", @interfaces)."\n";

if ($::quiet eq "0") {
   $::quiet = "no";
}
elsif ($::quiet eq "1") {
   $::quiet = "yes";
}

# Open connection to the LANforge server.
if (defined $log_cli) {
  if ($log_cli ne "unset") {
    # here is how we reset the variable if it was used as a flag
    if ($log_cli eq "") {
      $ENV{'LOG_CLI'} = 1;
    }
    else {
      $ENV{'LOG_CLI'} = $log_cli;
    }
  }
}
our $t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
          Timeout => 20);
$t->open(Host    => $lfmgr_host,
         Port    => $lfmgr_port,
         Timeout => 10);
$t->waitfor("/btbits\>\>/");

# Configure our utils.
our $utils = new LANforge::Utils();
$utils->telnet($t);         # Set our telnet object.
if ($utils->isQuiet()) {
  if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
    $utils->cli_send_silent(0);
  }
  else {
    $utils->cli_send_silent(1); # Do not show input to telnet
  }
  $utils->cli_rcv_silent(1);  # Repress output from telnet
}
else {
  $utils->cli_send_silent(0); # Show input to telnet
  $utils->cli_rcv_silent(0);  # Show output from telnet
}
$utils->log_cli("# $0 ".`date "+%Y-%m-%d %H:%M:%S"`);


#
