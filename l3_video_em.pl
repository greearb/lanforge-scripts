#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;
if ( -f "LANforge/Endpoint.pm" ) {
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

our $resource        = 1;
our $quiet           = "yes";
our $endp_name       = "";
our $speed           = "-1";
our $action          = "";
our $do_cmd          = "NA";
our $lfmgr_host      = "localhost";
our $lfmgr_port      = 4001;
our $tx_style        = "";
our $cx_name         = "";
our $min_tx          = undef;
our $max_tx          = -1;
our $est_buf_size    = -1;

our $usage = "$0  --tx_style { constant | bufferfill }
  --cx_name    {name}
  --mgr        {hostname | IP}
  --mgr_port   {ip port}
  --min_tx     {speed in bps}
  --max_tx     {speed in bps|SAME}
  --est_buff_size {kilobytes} # fill a buffer at max_tx for this long
";

my $show_help = 0;

if (@ARGV < 2) {
   print $usage;
   exit 0;
}
GetOptions
(
   'help|h'        => \$show_help,
   'cx_name|e=s' => \$::endp_name,
) || die($::usage);


if ($show_help) {
   print $usage;
   exit 0;
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

if ($::quiet eq "1" ) {
   $::quiet = "yes";
}
# Wait up to 60 seconds when requesting info from LANforge.
$t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
          Timeout => 60);

$t->open(Host    => $::lfmgr_host,
   Port    => $::lfmgr_port,
   Timeout => 10);

$t->max_buffer_length(16 * 1024 * 1000); # 16 MB buffer
$t->waitfor("/btbits\>\>/");

# Configure our utils.
our $utils = new LANforge::Utils();
$::utils->telnet($t);         # Set our telnet object.
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
$::utils->log_cli("# $0 ".`date "+%Y-%m-%d %H:%M:%S"`);


if
