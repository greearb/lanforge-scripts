#!/usr/bin/perl -w
# This script tests scripts
use strict;
use warnings;
use diagnostics;
use Carp;

$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
$| = 1;

use Net::Telnet;
use lib '.';
use lib './LANforge';

use Getopt::Long;
use JSON::XS;
use HTTP::Request;
use LWP;
use LWP::UserAgent;
use JSON;
use Data::Dumper;

use LANforge::Utils;
use LANforge::Port;
use LANforge::Endpoint;
use LANforge::JsonUtils qw(err logg xpand json_request get_links_from get_thru json_post get_port_names flatten_list);

package main;
our $LFUtils;
our $lfmgr_host       = "ct524-debbie";
our $lfmgr_port       = 4001;
our $http_port        = 4001;
our $resource         = 1;
our $quiet            = 1;
our @specific_tests   = ();
our %test_subs        = ();
our $lf_mgr           = undef;
our $HostUri          = undef;
our $Web              = undef;
our $Decoder          = undef;
our @test_errs        = ();
my $help              = 0;
my $list              = 0;
my $usage = qq($0 --mgr {lanforge hostname/IP}
  --mgr_port|p {lf socket (4001)}
  --resource|r {resource number (1)}
  --quiet {0,1,yes,no}
  --test|t {test-name} # repeat for test names
  --list|l # list test names
);

GetOptions (
   'mgr|m=s'            => \$::lfmgr_host,
   'mgr_port|p:s'       => \$::lfmgr_port,
   'card|resource|r:i'  => \$resource,
   'quiet|q:s'          => \$quiet,
   'test|t:s'           => \@specific_tests,
   'help|h'             => \$help,
   'list|l'             => \$list,
) || (print($usage) && exit(1));

if ($help) {
  print($usage) && exit(0);
}


$lf_mgr = $lfmgr_host;
$::HostUri   = "http://$lf_mgr:$http_port";
$::Web       = LWP::UserAgent->new;
$::Decoder   = JSON->new->utf8;

sub test_err {
  for my $e (@_) {
    my $ref = "".(caller(1))[3].":".(caller(1))[2]."";
    
    push (@test_errs, "$ref: $e");
  }
}
#----------------------------------------------------------------------
#   Tests
#----------------------------------------------------------------------

sub t_create_telnet {
  my $rv = 0;
  my $t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
                          Timeout => 20);
  $t->open(Host    => $::lf_mgr,
           Port    => $::lfmgr_port,
           Timeout => 10);
  $t->waitfor("/btbits\>\>/");
  $::LFUtils = new LANforge::Utils();
  $::LFUtils->telnet($t);         # Set our telnet object.
  if ($::LFUtils->isQuiet()) {
    if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
      $::LFUtils->cli_send_silent(0);
    }
    else {
      $::LFUtils->cli_send_silent(1); # Do not show input to telnet
    }
    $::LFUtils->cli_rcv_silent(1);  # Repress output from telnet
  }
  else {
    $::LFUtils->cli_send_silent(0); # Show input to telnet
    $::LFUtils->cli_rcv_silent(0);  # Show output from telnet
  }
  $rv = 1;
}

#----------------------------------------------------------------------
# multiple ways of querying a port:
# * CLI
# * Port.pm
# * JSON
# * shell out to perl script
#----------------------------------------------------------------------

sub t_query_port {
  my $expected = 3;
  my $rv = 0;
  ## test CLI
  my $cmd = $::LFUtils->fmt_cmd("nc_show_port", 1, $::resource, "eth0");
  my $res = $::LFUtils->doAsyncCmd($cmd);
  #die "Insufficient results $!" if (@res < 5);
  my ($port_ip) = $res =~ / IP:\s+([^ ]+) /;
  if ((defined $port_ip) && length($port_ip) >= 7) {
    $rv++;
  }
  else {
    test_err("port_ip [$port_ip] incorrect\n");
  }

  ## test LANforge::Port
  my $lf_port = LANforge::Port->new;
  $lf_port->decode($res);
  if ($lf_port->ip_addr() eq $port_ip) {
    $rv++;
  }
  else {
    test_err( "port_ip ".$lf_port->ip_addr()." doesn't match above $port_ip");
  }

  ## test JsonUtils/port
  print "http://".$::lf_mgr.":8080/port/1/1/eth0 \n";
  my $port_json = json_request("http://".$::lf_mgr.":8080/port/1/1/eth0");

  ## test lf_portmod.pl
  print "Trying: ./lf_portmod.pl --manager $::lf_mgr --card $::resource --port_name eth0 --show_port\n";
  $res = `./lf_portmod.pl --manager $::lf_mgr --card $::resource --port_name eth0 --show_port`;
  if ($res) {
    my ($port_ip2) = $res =~ / IP:\s+([^ ]+) /;
    if ((defined $port_ip2) && length($port_ip2) >= 7) {
      $rv++;
    }
    else {
      test_err("port_ip [$port_ip] incorrect\n");
    }
  }
  else {
    test_err("Insufficient output from lf_portmod.pl.\n");
  }
  
  if ($rv == $expected) {
    return 1;
  }
  test_err("Insuffient tests run");
  return 0;
}

sub t_set_port_up {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_set_port_down {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_create_mvlan {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_destroy_mvlan {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_query_radio {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_del_all_stations {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_add_station_to_radio {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_station_up {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_station_down {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_remove_radio {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_add_sta_L3_udp {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_sta_L3_start {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_sta_L3_stop {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

sub t_rm_sta_L3 {
  ## test CLI
  ## test LANforge::Port
  ## test JsonUtils/port
  ## test lf_portmod.pl
}

#----------------------------------------------------------------------
#----------------------------------------------------------------------
%test_subs = (
  '00_create_telnet'          => \&{'t_create_telnet'},
  '01_query_port'             => \&{'t_query_port'},
  '02_set_port_up'            => 0,
  '03_set_port_down'          => 0,
  '04_create_mvlan'           => 0,
  '05_destroy_mvlan'          => 0,
  '06_query_radio'            => 0,
  '07_del_all_stations'       => 0,
  '08_add_station_to_radio'   => 0,
  '09_station_up'             => 0,
  '10_station_down'           => 0,
  '11_remove_radio'           => 0,
  '12_add_sta_L3_udp'         => 0,
  '13_sta_L3_start'           => 0,
  '14_sta_L3_stop'            => 0,
  '15_rm_sta_L3'              => 0,
);


sub RunTests {
  my $rf_test = undef;

  if (@specific_tests > 0) {
      for my $test_name (sort @specific_tests) {
          if (defined &{$::test_subs{$test_name}}) {
            test_err("Failed on $test_name") unless &{$::test_subs{$test_name}}();
          }
          else {
            test_err( "test $test_name not found");
          }
      }
  }
  else {
     for my $test_name (sort keys %::test_subs) {
       if (defined &{$::test_subs{$test_name}}) {
         test_err("Failed on $test_name")
            unless &{$::test_subs{$test_name}}();
       }
       else {
         test_err("test $test_name not found");
       }
     }
  }
}

# ====== ====== ====== ====== ====== ====== ====== ======
#   M A I N
# ====== ====== ====== ====== ====== ====== ====== ======

if ($list) {
  my $av="";
  print "Test names:\n";
  for my $test_name (sort keys %::test_subs) {
      $av=" ";
      if (defined &{$::test_subs{$test_name}}) {
         $av='*';
      }
      print " ${av} ${test_name}\n";
  }
  exit(0);
}
else {
  RunTests();
}
if (@test_errs > 1) {
  print "Test errors:\n";
  print join("\n", @::test_errs);
}
print "\ndone\n";
#
