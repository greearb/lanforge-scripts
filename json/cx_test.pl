#!/usr/bin/perl -w
use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;
use Getopt::Long;
use JSON::XS;
use HTTP::Request;
use LWP;
use LWP::UserAgent;
use Data::Dumper;
use JSON;
use lib '/home/lanforge/scripts';
use LANforge::JsonUtils qw(logg err json_request get_links_from get_thru json_post get_port_names);

package main;
# Default values for ye ole cmd-line args.
our $Resource  = 1;
our $quiet     = "yes";
our $Host      = "localhost";
our $Port      = 8080;
our $HostUri   = "http://$Host:$Port";
our $Web       = LWP::UserAgent->new;
our $Decoder   = JSON->new->utf8;
our $ssid;
our $security;
our $passphrase;

my $usage = qq("$0 --host {ip or hostname} # connect to this
   --port {port number} # defaults to 8080
);


##
##    M A I N
##

GetOptions
(
  'host=s'        => \$::Host,
  'port=i'        => \$::Port
) || (print($usage) && exit(1));

$::HostUri = "http://$Host:$Port";

my $uri = "/shelf/1";
my $rh = json_request($uri);
my $ra_links = get_links_from($rh, 'resources');
my @links2= ();
my $ra_alias_links = [];
# TODO: make this a JsonUtils::list_ports()
for $uri (@$ra_links) {
   $uri =~ s{/resource}{/port}g;
   $uri .= "/list";
   #logg("requesting $uri");
   $rh = json_request($uri);
   #print Dumper($rh);
   push( @$ra_alias_links, @{get_port_names($rh, 'interfaces')});
   push(@links2, @{get_links_from($rh, 'interfaces')});
   #logg("\nfound: ");
   #logg(@links2);
}
#print Dumper($ra_alias_links);

# find first station
my $rh_sta;
for my $rh_alias_link (@$ra_alias_links) {
   #print Dumper($rh_alias_link);
   if ($rh_alias_link->{'alias'} =~/^sta\d+/) {
      $rh_sta=$rh_alias_link;
      last;
   }
}
if (!defined $rh_sta) {
   die("Unable to find a virtual station. Is one up?");
}

# assume resource 1, eth1 is present, and create an endpoint to it
# -A and -B are expected convention for endpoint names
my $rh_endp_A = {
      'alias'           => 'udp_ex-A',
      'shelf'           => 1,
      'resource'        => 1,
      'port'            => 'b1000', # or eth1
      'type'            => 'lf_udp',
      'ip_port'         => -1,
      'is_rate_bursty'  => 'NO',
      'min_rate'        => 1000000,
      'min_pkt'         => -1,
      'max_pkt'         => -1,
      'payload_pattern' => 'increasing',
      'multi_conn'      => 0
   };
json_post("/cli-json/add_endp", $rh_endp_A);

my $resourceB_uri = $rh_sta->{'uri'};
my ($resourceB) = $resourceB_uri =~ m{/port/1/(\d+)/};
my $rh_endp_B = {
      'alias'           => 'udp_ex-B',
      'shelf'           => 1,
      'resource'        => $resourceB,
      'port'            => $rh_sta->{'alias'},
      'type'            => 'lf_udp',
      'ip_port'         => -1,
      'is_rate_bursty'  => 'NO',
      'min_rate'        => 12800,
      'min_pkt'         => -1,
      'max_pkt'         => -1,
      'payload_pattern' => 'increasing',
      'multi_conn'      => 0
   };
json_post("/cli-json/add_endp", $rh_endp_B);

sleep(2);
my $rh_cx ={
   'alias'     => 'udp_ex',
   'test_mgr'  => 'default_tm',
   'tx_endp'   => 'udp_ex-A',
   'rx_endp'   => 'udp_ex-B'
};
json_post("/cli-json/add_cx", $rh_cx);
$rh_cx = {
   'test_mgr'  => 'default_tm',
   'cx_name'   => 'udp_ex',
   'milliseconds'=> 1000,
};
json_post("/cli-json/set_cx_report_timer", $rh_cx);

my $set_state = {
   'test_mgr'  => 'default_tm',
   'cx_name'   => 'udp_ex',
   'cx_state'  => 'RUNNING'
};
json_post("/cli-json/set_cx_state", $set_state);


my $rh_result;
for(my $i = 0; $i < 60; $i++) {
   $rh_result = json_request("/cx/udp_ex?fields=eid,state");
   print Dumper($rh_result);
   sleep(1);
}
$set_state = {
   'test_mgr'  => 'default_tm',
   'cx_name'   => 'udp_ex',
   'cx_state'  => 'STOPPED'
};
json_post("/cli-json/set_cx_state", $set_state);
#
