#!/usr/bin/perl -w
=pod
Use this script to create a large number of L3 connections for emulating video
traffic. This script is going to assume that all the connections are going to
use the same traffic type and same traffic speed. This test will collect all the
L3 connections into a test group.
=cut

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
# Un-buffer output
$| = 1;
if (-f "LANforge/Endpoint.pm" ) {
   use lib "./";
}
else {
  use lib '/home/lanforge/scripts';
}
use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils;
use Net::Telnet ();
use Getopt::Long;
our $resource   = 1;
our $quiet           = "yes";
our $action          = "";
our $lfmgr_host      = "localhost";
our $lfmgr_port      = 4001;
our $buffer_size     = (3 * 1024 * 1024);
our $upstream        = "";
our $clear_group     = -1;
my $cmd;
our $cx_name         = "NA";
our $endp_type       = "tcp";
our $first_sta       = "";
my $log_cli          = "unset"; # use ENV{LOG_CLI} elsewhere
our $num_cx          = 1;
my $show_help        = 0;
our $speed           = 1000 * 1000 * 1000;
our $use_ports_str   = "NA";
our $use_speeds_str  = "NA";
our $use_max_speeds  = "NA";
our $test_grp;

our $usage = <<"__EndOfUsage__";
Usage: $0 # create a large group of Layer 3 creations that emulate video traffic
 --action -a      { create | destroy | start | stop }
 --buffer_size -b {bytes K|M} # size of emulated RX buffer, default 3MB
 --clear_group -z  # empty test group first
 --cx_name -c     {connection prefix}
 --endp_type -t   {tcp|udp|lf_tcp|lf_udp}
 --first_sta -i   {name}
 --log_cli        {1|filename}   # log cli commands
 --mgr -m         {lanforge server} # default localhost
 --mgr_port -p    {lanforge port} # default 4002
 --num_cx -n      {number} # default 1
 --resource -r    {station resource}
 --speed -s       {bps K|M|G} # maximum speed of tx side, default 1Gbps
 --stream -e      {stream resolution name|list} # default yt-sdr-1080p30
                  # list of streams maintained in l3_video_em.pl
 --test_grp -g    {test group name} # all connections placed in this group
                  # default is {cx_name}_tg
 --upstream -u    {port short-EID} # video transmitter port;
                  # use 1.1.eth1 or 1.2.br0 for example
                  # upstream port does not need to be on same resource
Examples:
# create 30 stations emulating 720p HDR 60fps transmitted from resource 2:
 $0 --action create --buffer_size 8M --clear_group --cx_name yt1080p60.1 \\
   --endp_type udp --first_sta sta0000 --num_cx 30 \\
   --resource 2 --speed 200M --stream yt-hdr-720p60 --test_group yt60fps \\
   --upstream 1.2.br0

# start test group:
 $0 -a start -g yt60fps

# stop test group:
 $0 -a stop -g yt60fps

# add 30 more stations on resource 3 to group
 $0 -a create -b 8M -c yt1080p60.3 -t udp -i sta0100 -n 30 -r 3 \\
   -s 200M -e yt-hdr-720p60 -g yt60fps -u 1.2.br0

# destroy test group
 $0 -a destroy -g yt60fps
__EndOfUsage__

if (@ARGV < 2) {
   print $usage;
   exit 0;
}
our $debug = 0;
GetOptions
(
   'action|a=s'         => \$::action,
   'buffer_size|b=s'    => \$::buffer_size,
   'clear_group|z'      => \$::clear_group,
   'cx_name|c=s'        => \$::cx_name,
   'debug|d'            => \$::debug,
   'endp_type=s'        => \$::endp_type,
   'first_sta|i=s'      => \$::first_sta,
   'help|h'             => \$show_help,

   'log_cli=s{0,1}'     => \$log_cli,
   'manager|mgr|m=s'    => \$::lfmgr_host,
   'mgr_port|p=i'       => \$::lfmgr_port,
   'num_cx|n=i'         => \$::num_cx,
   'quiet|q=s'          => \$::quiet,
   'resource|r=i'       => \$::resource,
   'speed|s=i'          => \$::speed,
   'test_grp|g=s'       => \$::test_grp,
   'upstream|u=s'       => \$::upstream,

) || die($::usage);

if ($show_help) {
   print $usage;
   exit 0;
}

if (defined $ENV{DEBUG}) {
  use Data::Dumper;
}

if ($::debug) {
  use Data::Dumper;
  $ENV{DEBUG} = 1 if (!(defined $ENV{DEBUG}));
}

if ($::quiet eq "0") {
  $::quiet = "no";
}
elsif ($::quiet eq "1") {
  $::quiet = "yes";
}

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


# ------ ------ ------ ------ ------ ------ ------ ------ ------ ------ ------
#     M  A  I  N
# ------ ------ ------ ------ ------ ------ ------ ------ ------ ------ ------

# Apply defaults

if (!(defined $::test_grp) || ("" eq $::test_grp) || ("NA" eq $::test_grp)) {
   # use cx_name as prefix
   if (!(defined $::cx_name) || ("" eq $::cx_name) || ("NA" eq $::cx_name)) {
      die("No test_grp or cx_name is defined. Bye.");
   }
   $::test_grp = $::cx_name ."_tg";
}

if ($::clear_group) {
   print "will clear group $::test_grp\n";
   $::utils->doCmd(
}

if ($::action eq "create") {
   print "we will create!";
   exit 0;
}
if ($::action eq "destroy") {
   print "we will destroy!";
   exit 0;
}
if ($::action eq "start") {
   print "we will start!";
   exit 0;
}
if ($::action eq "stop") {
   print "we will stop!";
   exit 0;
}
else {
   die "What kind of action is [$::action]?";
}

# ------ ------ ------ ------ ------ ------ ------ ------ ------ ------ ------
