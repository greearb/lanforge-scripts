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

my $usage = qq("$0 --host {ip or hostname} # connect to this
   --port {port number} # defaults to 8080
);


##
##    M A I N
##

GetOptions
(
  'host=s'                   => \$::Host,
  'port=i'                   => \$::Port,
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

# destroy stations on resource 3, 7, 8
my @radios = ();
my @destroy_me = ();
for my $rh_alias_link (@$ra_alias_links) {
   push(@destroy_me, $rh_alias_link)
      if (($rh_alias_link->{'uri'} =~m{^/port/1/[3678]/})
         && ($rh_alias_link->{'alias'} =~m{^sta}));
   push(@radios, $rh_alias_link)
      if (($rh_alias_link->{'uri'} =~m{^/port/1/[3678]/})
         && ($rh_alias_link->{'alias'} =~m{^wiphy}));
}
logg("\nDestroying these: ");
#print Dumper(@destroy_me);
for my $rh_target (@destroy_me) {
   my $alias = $rh_target->{'alias'};
   my @hunks = split(/[\/]/, $rh_target->{'uri'});

   # TODO: create JsonUtils::rm_vlan($eid, $alias)
   my $rh_data = {
      'shelf'=>1, 'resource'=>$hunks[3], 'port'=>$alias
   };
   logg(" $alias");
   json_post("/cli-json/rm_vlan", $rh_data);
   sleep 0.015;
}

# this really should poll for ports to wait for them to disappear
sleep 2;

my @new_stations = ();
logg("\nCreating new stations on these: ");
#print Dumper(\@radios);
my $rh_radio;
my $radio_name;
my $resource;
my $range;
my $radio_num;
for $rh_radio (@radios) {
   $radio_name = $rh_radio->{'alias'};
   my @hunks = split(/[\/]/, $rh_radio->{'uri'});
   ($radio_num) = $radio_name =~ /wiphy(\d+)/;
   $resource = $hunks[3];
   $range = ($resource * 1000) + ($radio_num * 100);
   logg("\n/cli-json/add_sta = ");
   for (my $i = $range; $i < ($range+20); $i++) {
      # TODO: create JsonUtils::add_sta($eid, $alias...)
      my $rh_data = {
         'shelf'=>1,
         'resource'=>$resource,
         'radio'=>$radio_name,
         'sta_name'=>'sta'.$i,
         'flags'=>68862086144, # has port-down set
         'ssid'=>'idtest-1200-wpa2',
         'key'=>'idtest-1200-wpa2',
         'mac'=>'xx:xx:xx:xx:*:xx',
         'mode'=>0,
         'rate'=>'DEFAULT'
      };
      #print Dumper($rh_data);
      logg(" $radio_name/sta$i ");
      json_post("/cli-json/add_sta", $rh_data);
      sleep 0.021;
   }
}
sleep 1;
for $rh_radio (@radios) {
   $radio_name = $rh_radio->{'alias'};
   my @hunks = split(/[\/]/, $rh_radio->{'uri'});
   $resource = $hunks[3];
   $range = ($resource * 1000) + ($radio_num * 100);
   for (my $i = $range; $i < ($range+20); $i++) {
      my $rh_data = {
         'shelf'=>1,
         'resource'=>$resource,
         'port'=>'sta'.$i,
         'cmd_flags'=>0,
         'current_flags'=>2147483648,
         'interest'=>16386
      };
      # TODO: create JsonUtils::set_dhcp($eid, $alias, $on_off)
      json_post("/cli-json/set_port", $rh_data);
      sleep 0.021;
   }
}
sleep 1;
for $uri (@$ra_links) {
   $uri =~ s{/resource}{/port}g;
   $uri .= "/list"
      if ($uri !~ m{/list$});
   $rh = json_request($uri);
   push( @$ra_alias_links, @{get_port_names($rh, 'interfaces')});
   push(@links2, @{get_links_from($rh, 'interfaces')});
}

# ports down
my $set_port = "/cli-json/set_port";
logg("\nsetting ports down: ");
for my $port_uri (@links2) {
   $rh = json_request($port_uri);
   my $device = get_thru('interface', 'device', $rh);
   next if ($device !~ /^sta/);
   logg($device." ");
   my $port = get_thru('interface', 'port', $rh);
   my @hunks = split(/\./, $port);
   my $resource = $hunks[1];
   my %post = (
      "shelf" => 1, "resource" => 0+$resource, "port" => $device,
      "current_flags" => 1, "interest" => 8388610
   );
   my $rh_response = json_post($set_port, \%post);
}
sleep 1;
logg("\nsetting ports up ");
for my $port_uri (@links2) {
   $rh = json_request($port_uri);
   my $device = get_thru('interface', 'device', $rh);
   next if ($device !~ /^sta/);
   logg($device." ");
   my $port = get_thru('interface', 'port', $rh);
   my @hunks = split(/\./, $port);
   my $resource = $hunks[1];
   # 'shelf=1&resource=2&port=vap2000&cmd_flags=0&current_flags=0&interest=8388610'
   my %post = (
      "shelf" => 1, "resource" => 0+$resource, "port" => $device,
      "current_flags" => 0, "interest" => 8388610
   );
   my $rh_response = json_post($set_port, \%post);
}

#
