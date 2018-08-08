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
use LANforge::JsonUtils;

package main;
# Default values for ye ole cmd-line args.
our $Resource  = 1;
our $quiet     = "yes";
our $Host      = "atlas";
our $Port      = 8080;
our $HostUri   = "http://$Host:$Port";
our $Web       = LWP::UserAgent->new;
our $Decoder   = JSON->new->utf8;



##
##    M A I N
##

GetOptions
(
  'host=s'                   => \$::Host,
) || (print($usage) && exit(1));

"http://$Host:$Port";

my $uri = "/shelf/1";
my $rh = json_request($uri);
my $ra_links = get_links_from($rh, 'resources');

#print Dumper($ra_links);
for $uri (@$ra_links) {
   $uri =~ s{/resource}{/port}g;
   $uri .= "/list";
   logg("requesting $uri");

   $rh = json_request($uri);
   print Dumper($rh);
   my $ra_links2 = get_links_from($rh, 'interfaces');
   for my $uri2 (@$ra_links2) {
      logg("found $uri2");
   }
}

#