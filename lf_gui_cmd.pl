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
my $ttype = ""; # Test type
my $tname = "lfgui-test";
my $tconfig = "";  # test config
my $rpt_dest = "";
my $show_help = 0;

########################################################################
# Nothing to configure below here, most likely.
########################################################################

my $usage = qq($0  [--manager { hostname or address of LANforge GUI machine } ]
                 [--port {port name} ]
                 [--ttype {test instance type} ]
                 [--tname {test instance name} ]
                 [--tconfig {test configuration name, use defaults if not specified} ]
                 [--rpt_dest {Copy report to destination once it is complete} ]
                 [--cmd { command to send to the GUI } ]

Example:
 lf_gui_cmd.pl --manager localhost --port 3990 --ttype TR-398 --tname mytest --tconfig comxim --rpt_dest /var/www/html/lf_reports
 lf_gui_cmd.pl --manager localhost --port 3990 --cmd \"help\"
);

if (@ARGV < 2) {
   print "$usage\n";
   exit 0;
}

GetOptions (
   'help|h'                => \$show_help,
   'manager|mgr|m=s'       => \$lfmgr_host,
   'ttype=s'               => \$ttype,
   'tname=s'               => \$tname,
   'tconfig=s'             => \$tconfig,
   'rpt_dest=s'            => \$rpt_dest,
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

if ($cmd ne "") {
  print doCmd("$cmd");
}

if ($ttype ne "") {
  doCmd("cv create '$ttype' '$tname'");
  if ($tconfig ne "") {
    doCmd("cv load 'tname' '$tconfig'");
  }
  doCmd("cv click '$tname' 'Auto Save Report'");
  doCmd("cv click '$tname' 'Start'");
  while (1) {
    my $rslt = doCmd("cv get '$tname' 'Report Location:'");
    print "Result-:$rslt:-\n";
    if ($rslt =~ /^\s*Report Location:::(.*)/) {
      my $loc = $1;
      if ($loc eq "") {
	# Wait longer
	sleep(1);
      }
      else {
	# Copy some place it can be seen easily?
	if ($rpt_dest ne "") {
	  my $cp = "cp -ar $loc $rpt_dest";
	  print "Copy test results: $cp\n";
	  system($cp);
	}
	last;
      }
    }
  }
}

exit(0);

sub doCmd {
  my $cmd = shift;

  print ">>>Sending:$cmd\n";

  $t->print($cmd);
  my @rslt = $t->waitfor('/lfgui\#/');
  if ($rslt[@rslt-1] eq "lfgui\#") {
    $rslt[@rslt-1] = "";
  }
  return join("\n", @rslt);
}

