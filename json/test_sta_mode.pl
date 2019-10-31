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
use LANforge::JsonUtils qw(err logg xpand json_request);


package main;
# Default values for ye ole cmd-line args.
our $Resource  = 1;
our $quiet     = "yes";
our $Host      = "localhost";
our $Port      = 8080;
our $HostUri   = "http://$Host:$Port";
our $Web       = LWP::UserAgent->new;
our $Decoder   = JSON->new->utf8;

my $usage = qq($0: --host [hostname] # hostname or IP to query
     --port [port]   # port like 8080
);

##
##    M A I N
##
GetOptions
(
   'port=i'    => \$::Port,
   'host=s'    => \$::Host,
) || (print($usage) && exit(1));

$HostUri   = "http://$Host:$Port";

my $uri = "/port/1/1/sta0200";
my $rh = json_request($uri);
print Dumper($rh);


#
