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
use Time::HiRes qw(usleep);
use JSON;
use lib '/home/lanforge/scripts';
use LANforge::JsonUtils qw(logg err json_request get_links_from get_thru json_post get_port_names flatten_list);

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

my $des_resource = 6;

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
my @ports_up= ();

# TODO: make this a JsonUtils::list_ports()
$uri = "/port/1/6/list?fields=alias,device,down,phantom,port";
#logg("requesting $uri");
$rh = json_request($uri);
flatten_list($rh, 'interfaces');
for my $rh_p (keys %{$rh->{'flat_list'}}) {
   if (!$rh->{'flat_list'}->{$rh_p}->{'down'}) {
      push(@ports_up, $rh_p);
   }
}
# find first station
my $rh_sta;
for my $rh_up (@ports_up) {
   my $eid = $rh->{'flat_list'}->{$rh_up}->{'port'};
   my @hunks = split(/[.]/, $eid);
   if ($hunks[1]) {
      $rh_sta = $rh_up;
   }
}
if (!defined $rh_sta) {
   die("Unable to find a virtual station. Is one up?");
}

# delete old CXes and old endpoints
# TODO: collect_l4cx_names

my $rh_endplist = json_request("/layer4/list");
print "\nRemoving L4: ";
my @endp_names = ();
print Dumper($rh_endplist);

if (defined $rh_endplist->{"endpoint"}
   && (ref $rh_endplist->{"endpoint"} eq "HASH")) {
   # indicates we only have one
   push(@endp_names, $rh_endplist->{"endpoint"}->{"name"});
}
elsif (defined $rh_endplist->{"endpoint"}) {
   flatten_list($rh_endplist, 'endpoint');
   print "FLAT LIST:\n";
   print Dumper($rh_endplist->{'flat_list'});
   for my $ep_name (keys %{$rh_endplist->{'flat_list'}}) {
      next if (!defined $ep_name);
      next if ($ep_name eq "");
      next if ((ref $ep_name) eq "ARRAY");
      next if (!defined $rh_endplist->{'flat_list'}->{$ep_name}->{"name"});
      next if ($rh_endplist->{'flat_list'}->{$ep_name}->{"name"} eq "");
      print "epn:".Dumper($rh_endplist->{'flat_list'}->{$ep_name}->{"name"});
      push(@endp_names, $ep_name);
   }
}
if ((@endp_names < 1) && (defined $rh_endplist->{"endpoint"})) {
   # check for mutated L4endp entries that only exist in EID form
   #die "Unknown L4 endpoint state"
   #   if (!(defined $rh_endplist->{"endpoint"}));
   die "No endpoint entries"
      if (scalar @{$rh_endplist->{"endpoint"}} < 1);
   for $rh (@{$rh_endplist->{"endpoint"}}) {
      print Dumper($rh);
      my @k = keys(%$rh);
      print "$k[0] ";
      push(@endp_names, $k[0]);
   }
}
#print Dumper(\@endp_names);

my @cx_names = ();
if (@endp_names > 0) {
   for my $endp_name (@endp_names) {
      print " endp_name[$endp_name]";
      push(@cx_names, "CX_".$endp_name);
   }
}
my $rh_req = { "test_mgr" => "all" };
for my $cx_name (@cx_names) {
   $rh_req->{"cx_name"} = $cx_name;
   json_post("/cli-json/rm_cx", $rh_req);
}
my $rh_show_cxe = { "test_mgr"=>"all", "cross_connect"=>"all"};
json_post("/cli-json/show_cxe", $rh_show_cxe);
sleep 1;

$uri = "/cli-json/rm_endp";
for my $ep_name (@endp_names) {
   if (!defined $ep_name || $ep_name =~/^\s*$/ || (ref $ep_name) eq "ARRAY") {
      print " [$ep_name]"; #skipping
      print Dumper(\$ep_name);
      next;
   }
   print "-$ep_name ";
   $rh = { "endp_name" => $ep_name };
   json_post($uri, $rh);
}

print "\nRefreshing...";
my $h = {"endpoint"=>"all"};
json_request("/cli-json/nc_show_endpoints", $h);
sleep 1;
$h = {"test_mgr"=>"all", "cross_connect"=>"all"};
json_request("/cli-json/show_cxe", $h);

# assume resource 1, eth1 is present, and create an endpoint to it
# -A and -B are expected convention for endpoint names

# create 10 endpoints
my $rh_ports = json_request("/port/1/${des_resource}/list");
flatten_list($rh_ports, 'interfaces');

my $rh_endp_A = {
      'alias'           => 'udp_json',
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

my $rh_endp_B = {
      'alias'           => "untitled",
      'shelf'           => 1,
      'resource'        => $des_resource,
      #'port'            => 'unset',
      'type'            => 'l4_generic',
      'timeout'         => '2000',
      'url_rate'        => '600',
      'url'             => 'DL http://10.41.0.3/',
      'max_speed'       => '1000000'
   };

$h = {"endpoint"=>"all"};
json_request("/cli-json/nc_show_endpoints", $h);
$h = {"test_mgr"=>"all", "cross_connect"=>"all"};
json_request("/cli-json/show_cxe", $h);
sleep 1;
print "\nConstructing new Endpoints: ";
my $num_ports = scalar keys(%{$rh_ports->{'flat_list'}});
my $num_cx = 0;
my $disp_num = $des_resource * 1000;
for my $rh_p (values %{$rh_ports->{'flat_list'}}) {

   last if ($num_cx >= ($num_ports-1));
   next if ($rh_p->{'alias'} !~ /^v*sta/);

   #my $end_a_alias = "udp_json_${disp_num}-A";
   my $end_b_alias = "l4json_${disp_num}"; 
   my $port_b = $rh_p->{'alias'};
   print " ${port_b}:$end_b_alias";
   $rh_endp_B->{'port'} = $port_b;
   $rh_endp_B->{'alias'} = $end_b_alias;
   $num_cx++;
   $disp_num++;

   #json_post("/cli-json/add_endp", $rh_endp_A);
   print Dumper($rh_endp_B);
   sleep 5;
   
   json_post("/cli-json/add_l4_endp", $rh_endp_B);
}
print "\nRefreshing...";
$h = {"endpoint"=>"all"};
json_request("/cli-json/nc_show_endpoints", $h);
sleep 1;
print "\nConstructing new CX: ";
$num_cx = 0;
my $rh_endpoints = json_request("/layer4/list");
flatten_list($rh_endpoints, 'endpoint');
for my $rh_e (values %{$rh_endpoints->{'flat_list'}}) {
   last if ($num_cx >= ($num_ports-1));
   #next if ($rh_e->{'alias'} !~ /^v*sta/);
   print Dumper($rh_e);
   # my $end_a_alias = "udp_json_${num_cx}-A";
   # my $end_b_alias = "udp_json_${num_cx}-B"; 
   # my $port_b = $rh_p->{'alias'};
   # my $cx_alias = "udp_json_".$num_cx;
   # $rh_cx->{'alias'} = $cx_alias; 
   # $rh_cx->{'tx_endp'} = $end_a_alias;
   # $rh_cx->{'rx_endp'} = $end_b_alias;
   # json_post("/cli-json/add_cx", $rh_cx);
   # print " $cx_alias";
   # $num_cx++;
}
# print "\nRefreshing...";
$h = {"endpoint"=>"all"};
json_request("/cli-json/nc_show_endpoints", $h);

#my $rh_cxlist = json_request("/cx/list");
#@cx_names = ();
#for my $cx_name (sort keys %$rh_cxlist) {
#   next if (ref $rh_cxlist->{$cx_name} ne "HASH");
#   next if (!defined $rh_cxlist->{$cx_name}->{"name"});
#   push(@cx_names, $rh_cxlist->{$cx_name}->{"name"});
#}
#for my $cx_alias (sort @cx_names) {
#   my $rh_cx_t = {
#      'test_mgr'  => 'default_tm',
#      'cx_name'   => $cx_alias,
#      'milliseconds'=> 1000,
#   };
#   json_post("/cli-json/set_cx_report_timer", $rh_cx_t);
#}
print "\nRefreshing...";
$h = {"endpoint"=>"all"};
json_request("/cli-json/nc_show_endpoints", $h);
sleep 1;
$h = {"test_mgr"=>"all", "cross_connect"=>"all"};
json_request("/cli-json/show_cxe", $h);

#my $set_state = {
#   'test_mgr'  => 'default_tm',
#   'cx_name'   => 'udp_ex',
#   'cx_state'  => 'RUNNING'
#};
#my @cx_names = ();
#$rh_cxlist = json_request("/cx/list");
#for my $cx_name (sort keys %$rh_cxlist) {
#   next if (ref $rh_cxlist->{$cx_name} ne "HASH");
#   next if (!defined $rh_cxlist->{$cx_name}->{"name"});
#   push(@cx_names, $rh_cxlist->{$cx_name}->{"name"});
#}
#print "\nStarting: ";
#for my $cxname (@cx_names) {
#   print " $cxname";
#   $set_state->{'cx_name'} = $cxname;
#   json_post("/cli-json/set_cx_state", $set_state);
#}
#sleep 10;

#my $set_state = {
#   'test_mgr'  => 'default_tm',
#   'cx_name'   => 'udp_ex',
#   'cx_state'  => 'STOPPED'
#};
#print "\nStopping: ";
#for my $cxname (@cx_names) {
#   $set_state->{'cx_name'} = $cxname;
#   print " $cxname";
#   json_post("/cli-json/set_cx_state", $set_state);
#}
#print "...done\n";
#
#
