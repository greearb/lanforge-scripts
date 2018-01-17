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
use Data::Dumper;
$SIG{ __DIE__ }   = sub { Carp::confess( @_ )};
$SIG{ __WARN__ }  = sub { Carp::confess( @_ )};
use Getopt::Long;
use Cwd qw(getcwd);
my $cwd = getcwd();
use lib '/home/lanforge/scripts';
use List::Util qw(first);
use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils qw(fmt_cmd);
use Net::Telnet ();

our $dest_ip_addr = "0.0.0.0";
our $log_cli = "unset"; # use ENV{'LOG_CLI'}

our $usage = qq(Usage:
$0 --mgr {host-name | IP}
   --mgr_port {ip port}
   --resource {resource}
   --dest {destination IP}
   --interface|-intf|-int|-i {source interface}
    # You should be able to place 1000 interfaces in the list
   --radio {wiphy}
   --match {simple pattern, no stars or questions marks}

 Examples:
  $0 --mgr localhost --resource 1 --dest 192.168.0.1 -i wlan0 -i sta3000
  This will match just sta3000

 All interfaces on a parent radio
  $0 --mgr localhost --resource 1 --dest 192.168.0.1 --radio wiphy0
  This will match all stations whos parent is wiphy0: sta3 wlan0

 All interfaces matching a pattern:
  $0 -m localhost -r 1 -d 192.168.0.1 --match sta3
  This will match sta3 sta30 sta31 sta3000

 If only a few of your generic commands start, check journalctl for
 errors containing: 'cgroup: fork rejected by pids controller'
 You want to set DefaultTasksMax=unlimited in /etc/systemd/system.conf
 then do a systemctl daemon-restart
 https://www.novell.com/support/kb/doc.php?id=7018594
);

our $shelf_num    = 1;
our $report_timer = 1000;
our $test_mgr     = "default_tm";
our $resource     = 1;
our $lfmgr_host   = "localhost";
our $lfmgr_port   = 4001;
our $quiet        = "yes";
our $quiesce      = 3;
our $clear_on_start = 0;
our $dest_ip;
our @interfaces   = ();
our $radio        = '';
our $pattern      = '';

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
  'quiet|q'                   => \$::quiet,
  'radio|o=s'                 => \$::radio,
  'match=s'                   => \$::pattern,
  'interface|intf|int|i=s'    => \@::interfaces,
  'dest_ip|dest|d=s'          => \$::dest_ip,
  'help|h|?'                  => \$help,
) || (print($usage), exit(1));

#print "radio: $::radio, match: $::pattern, $::quiet, $::resource, $::dest_ip\n";

if ($help) {
   print($usage) && exit(0);
}
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

our @ports_lines = split("\n", $::utils->doAsyncCmd("nc_show_ports 1 $::resource ALL"));
chomp(@ports_lines);
our %eid_map = ();
my ($eid, $card, $port, $type, $mac, $dev, $rh_eid, $parent);
foreach my $line (@ports_lines) {
  # collect all stations on that radio add them to @interfaces
  if ($line =~ /^Shelf: /) {
    $card = undef; $port = undef;
    $type = undef; $parent = undef;
    $eid = undef; $mac = undef;
    $dev = undef; $rh_eid = undef;
  }

  # careful about that comma after card!
  ($card, $port, $type) = $line =~ m/ Card: (\d+), +Port: (\d+) +Type: (\w+) /;
  if ((defined $card) && ($card ne "") && (defined $port) && ($port ne "")) {
    $eid = "1.${card}.${port}";
    $rh_eid = {
      eid => $eid,
      type => $type,
      parent => undef,
      dev => undef,
    };
    $eid_map{$eid} = $rh_eid;
  }

  ($mac, $dev) = $line =~ / MAC: ([0-9:a-fA-F]+)\s+DEV: (\w+)/;
  if ((defined $mac) && ($mac ne "")) {
    $rh_eid->{mac} = $mac;
    $rh_eid->{dev} = $dev;
  }

  ($parent) = $line =~ / Parent.Peer: (\w+) /;
  if ((defined $parent) && ($parent ne "")) {
    $rh_eid->{parent} = $parent;
  }
}

#foreach $eid (keys %eid_map) {
#  print "eid $eid ";
#}

if (defined $::radio) {
  while (($eid, $rh_eid) = each %eid_map) {
    if ((defined $rh_eid->{parent}) && ($rh_eid->{parent} eq $::radio)) {
      push(@interfaces, $rh_eid->{dev});
    }
  }
}

if (defined $::pattern && $pattern ne "") {
   my $pat = $::pattern;
   $pat =~ s/[+]//g;
   # collect all stations on that resource add them to @interfaces
   while (($eid, $rh_eid) = each %eid_map) {
     if ((defined $rh_eid->{dev}) && ($rh_eid->{dev} =~ /$pat/)) {
       push(@interfaces, $rh_eid->{dev});
     }
   }
}

if (@interfaces < 1) {
   print STDERR "One or more interfaces required.\n";
   print $usage;
   exit(1);
}

print "Creating generic lfping endpoints using these interfaces: \n";
print " ".join(", ", @interfaces)."\n";

=pod
Example of generic created by GUI:
   add_gen_endp test-1 1 3 sta3000 gen_generic
   set_gen_cmd test-1 lfping  -p deadbeef -I sta3000 10.41.1.2
   set_endp_quiesce test-1 3
   set_endp_report_timer test-1 1000
   set_endp_flag test-1 ClearPortOnStart 0
   add_gen_endp D_test-1 1 3 sta3000 gen_generic
   set_endp_flag D_test-1 unmanaged 1
   set_endp_quiesce D_test-1 3
   set_endp_report_timer D_test-1 1000
   set_endp_flag D_test-1 ClearPortOnStart 0

=cut
sub create_generic {
   my ($name, $port_name)=@_;
   my $endp_name = "lfping_$port_name";
   my $type = "gen_generic";
   my $ping_cmd = "lfping -I $port_name -p deadbeef $::dest_ip";

   $::utils->doCmd($::utils->fmt_cmd("add_gen_endp", $endp_name, 1, $::resource, $port_name, $type));
   $::utils->doCmd("set_gen_cmd $endp_name $ping_cmd");
   $::utils->doCmd("set_endp_quiesce $endp_name $::quiesce");
   $::utils->doCmd("set_endp_flag $endp_name ClearPortOnStart $::clear_on_start");
   $::utils->doCmd("set_endp_report_timer $endp_name $::report_timer");

   # we also need to add the opposite unmanaged endpoint
   $::utils->doCmd("add_gen_endp D_$endp_name 1 $::resource $port_name gen_generic");
   $::utils->doCmd("set_endp_flag D_$endp_name unmanaged 1");
   $::utils->doCmd("set_endp_quiesce D_$endp_name $::quiesce");
   $::utils->doCmd("set_endp_flag D_$endp_name ClearPortOnStart $::clear_on_start");
   $::utils->doCmd("set_endp_report_timer D_$endp_name $::report_timer");

   # tie the knot with a CX
   $::utils->doCmd("add_cx CX_$endp_name default_tm $endp_name D_$endp_name");
   $::utils->doCmd("set_cx_report_timer default_tm CX_$endp_name $::report_timer cxonly");
}

my %command_map = ();
for my $port (sort @interfaces) {
   my $endp_name = "lfping_$port";
   my $type = "gen_generic";
   create_generic($endp_name, $port)
}


#
