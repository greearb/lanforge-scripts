#!/usr/bin/perl -w
# This script tests scripts
use strict;
use warnings;
use diagnostics;
use Carp;

$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
$| = 1;

#use JSON;
package main;
use Net::Telnet;
use lib '.';
use lib './LANforge';
use LANforge::Utils;
use LANforge::Port;
use LANforge::Endpoint;
use Getopt::Long;
use JSON::XS;
use HTTP::Request;
use LWP;
use LWP::UserAgent;
use JSON;
use Data::Dumper;
use LANforge::JsonUtils;

our $LFUtils;
our $lfmgr_host = "ct524-debbie";
our $lfmgr_port = 4001;
our $resource = 1;
our $quiet = 1;
our @specific_tests = ();
our %test_subs = ();
my $help = 0;
my $list = 0;
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

our $lf_mgr;
$lf_mgr = $lfmgr_host;
#----------------------------------------------------------------------
#   Tests
#----------------------------------------------------------------------

sub t_create_telnet {
  my $rv = 0;
  print "This is a test!\n";
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
  my $expected = 4;
  my $rv = 0;
  my $cmd = $::LFUtils->fmt_cmd("nc_show_port", 1, $::resource, "eth0");
  my $res = $::LFUtils->doAsyncCmd($cmd);
  #die "Insufficient results $!" if (@res < 5);
  my ($port_ip) = $res =~ / IP:\s+([^ ]+) /;
  if ((defined $port_ip) && length($port_ip) >= 7) {
    $rv++
  }
  else {
    print "port_ip [$port_ip] incorrect\n";
  }

  my $lf_port = LANforge::Port->new;
  $lf_port->decode($res);
  if ($lf_port->ip_addr() eq $port_ip) {
    $rv++
  }
  else {
    print "port_ip ".$lf_port->ip_addr()." doesn't match above $port_ip\n";
  }

  my $port_json = JsonUtils->json_request("http://$::{lf_mgr}:8080/port/1/1/eth0");

  $res = `./lf_portmod.pl --manager $::lf_mgr --card $::resource --port_name eth0 --show_port`;
  if ($res) {
    my ($port_ip2) = $res =~ / IP:\s+([^ ]+) /;
    if ((defined $port_ip2) && length($port_ip2) >= 7) {
      $rv++
    }
    else {
      print "port_ip [$port_ip] incorrect\n";
    }
  }
  else {
    print "Insufficient output from lf_portmod.pl.\n";
  }
  return ($rv == $expected) ? 1 : 0;
}

sub t_set_port_up {
}

sub t_set_port_down {
}

sub t_create_mvlan {
}

sub t_destroy_mvlan {
}

sub t_query_radio {
}

sub t_del_all_stations {
}

sub t_add_station_to_radio {
}

sub t_station_up {
}

sub t_station_down {
}

sub t_remove_radio {
}

sub t_add_sta_L3_udp {
}

sub t_sta_L3_start {
}

sub t_sta_L3_stop {
}

sub t_rm_sta_L3 {
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
            print "test $test_name found...";
            die("Failed on $test_name")
               unless &{$::test_subs{$test_name}}();
          }
          else {
            print "test $test_name not found ";
          }
      }
  }
  else {
     for my $test_name (sort keys %::test_subs) {
       if (defined &{$::test_subs{$test_name}}) {
         print "test $test_name found...";
         die("Failed on $test_name")
            unless &{$::test_subs{$test_name}}();
       }
       else {
         print "test $test_name not found ";
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

RunTests();
print "done\n";
#
