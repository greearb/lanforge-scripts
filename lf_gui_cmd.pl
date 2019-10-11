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
# Un-buffer output
$| = 1;

use Net::Telnet ();
use Getopt::Long;

my $lfmgr_host = "localhost";
my $lfmgr_port = 3990;

# Default values for ye ole cmd-line args.
my $port = "";
my $cmd = "";
my $show_help = 0;

########################################################################
# Nothing to configure below here, most likely.
########################################################################

my $usage = qq($0  [--manager { hostname or address of LANforge GUI machine } ]
                 [--port {port name} ]
                 [--cmd { command to send to the GUI } ]

Example:
 lf_gui_cmd.pl --manager localhost --port 3990 --cmd \"help\"
);

if (@ARGV < 2) {
   print "$usage\n";
   exit 0;
}

GetOptions (
   'help|h'                => \$show_help,
   'manager|mgr|m=s'       => \$lfmgr_host,
   'port=s'                => \$port,
   'cmd|c=s'               => \$cmd,
) || die("$usage");

if ($show_help) {
   print $usage;
   exit 0;
}

# Open connection to the LANforge server.
my $t = new Net::Telnet(Prompt => '/lfgui\# /',
         Timeout => 20);

$t->open( Host    => $lfmgr_host,
          Port    => $lfmgr_port,
          Timeout => 10);

$t->waitfor("/lfgui\# /");

$t->print($cmd);
my @rslt = $t->waitfor('/lfgui\#/');

print join( "\n", @rslt );

exit(0);
