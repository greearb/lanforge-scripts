#!/usr/bin/perl -w

use strict;
use warnings;
use diagnostics;
use JSON;
use Data::Dumper;
use LANforge::GuiJson qw(GuiResponseToHash GetHeaderMap GetRecordsMatching GetFields);
package main;

my $respdata=`curl -s http://localhost:8080/PortTab`;
#my $ra_ports_data = decode_json($respdata);
my $ra_resp_map = GuiResponseToHash($respdata);
my $ra_header = GetHeaderMap($ra_resp_map->{'header'});
#print Dumper($ra_header);

my $ra_matches = GetRecordsMatching($ra_resp_map, 'Port', ["eth0", "wlan0"]);
#print "Records matching Port:\n";
#print Dumper($ra_matches);

my @port_names = ("eth0", "wlan0");
$ra_matches = GetRecordsMatching($ra_resp_map, 'Device', \@port_names);
#print "Records matching Port:\n";
#print Dumper($ra_matches);

my @field_names = ("bps TX", "bps RX");
my $ra_fields = GetFields($ra_resp_map, 'Device', \@port_names, \@field_names);
print "Fields (".join(", ", @field_names).") from records matching Device (".join(", ", @port_names)."):\n";
print Dumper($ra_fields);
