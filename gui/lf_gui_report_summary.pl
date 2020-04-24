#!/usr/bin/perl -w
# Generate HTML summary page for a collection of GUI reports (with kpi.csv)
# (C) 2020 Candela Technologies Inc.
#

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;

# use lib prepends to @INC, so put lower priority first
# This is before run-time, so cannot condition this with normal 'if' logic.
use lib '/home/lanforge/scripts';
use lib "../";
use lib "./";

use Getopt::Long;

our $dir = "";
our $title = "Automated test results.";


########################################################################
# Nothing to configure below here, most likely.
########################################################################

our $usage = <<"__EndOfUsage__";
$0 [ --dir directory-to-process ]

Example:
 $0 --dir ~/tmp/results --title "My Title"
__EndOfUsage__

my $i = 0;
my $show_help = 0;

GetOptions
(
   'dir|d=s'            => \$::dir,
   'title|t=s'          => \$::title,
   'help|h'             => \$show_help,
) || die("$::usage");

if ($show_help) {
   print $usage;
   exit 0;
}

chdir($dir);

my @files = `ls`;
chomp(@files);

my $line;

# Find some html helpers and copy them to current dir.
foreach $line (@files) {
   if ( -d $line) {
      if ( -f "$line/canvil.ico") {
         `cp $line/canvil.ico ./`;
         `cp $line/*.css ./`;
         `cp $line/candela_swirl* ./`;
         `cp $line/CandelaLogo* ./`;
         last;
      }
   }
}

my $dut_tr = "";
my $kpi_tr = "";
my $tests_tr = "";

foreach my $line (@files) {
   if ( -d $line) {
      if ( -d "$line/logs") {
         $tests_tr .= "<tr><td><a href=\"$line/index.html\">$line</html></td><td><a href=\"$line/logs\">Logs</td></tr>\n";
      }
      else {
         $tests_tr .= "<tr><td><a href=\"$line/index.html\">$line</html></td><td></td></tr>\n";
      }

      if ( -f "$line/kpi.csv") {
         my @kpi = `cat $line/kpi.csv`;
         chomp(@kpi);
         my $i = 0;
         foreach my $k (@kpi) {
            $i++;
            if ($i == 1) {
               next; # skip header
            }

            my @cols = split(/\t/, $k);
            if ($dut_tr eq "") {
               $dut_tr = "<tr><td>$cols[1]</td><td>$cols[2]</td><td>$cols[3]</td><td>$cols[4]</td><td>$cols[5]</td></tr>\n";
            }

            $kpi_tr .= "<tr><td>$cols[7]</td><td>$cols[8]</td><td>$cols[9]</td><td>$cols[10]</td><td>$cols[11]</td></tr>\n";
         }
      }
   }
}

my $date = `date`;

while (<>) {
   my $ln = $_;
   chomp($ln);

   $ln =~ s/___TITLE___/$title/g;
   $ln =~ s/___DATE___/$date/g;
   $ln =~ s/___TR_DUT___/$dut_tr/g;
   $ln =~ s/___TR_KPI___/$kpi_tr/g;
   $ln =~ s/___TR_TESTS___/$tests_tr/g;
   print "$ln\n";
}

exit(0);

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
