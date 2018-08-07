#!/usr/bin/perl -w
use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;
#use lib '/home/lanforge/scripts';
#use LANforge::Endpoint;
#use LANforge::Port;
#use LANforge::Utils;
#use Net::Telnet ();
use Getopt::Long;
use JSON::XS;
use HTTP::Request;
use LWP;
use LWN::UserAgent;

use constant      NA          => "NA";
use constant      NL          => "\n";
use constant      shelf_num   => 1;

package main;
# Default values for ye ole cmd-line args.
our $Resource  = 1;
our $quiet     = "yes";
our $Host      = "localhost";
our $Port      = 8080;
our $HostUri   = "http://$Host:$Port";
our $Web       = new UserAgent();

sub err {
   my $i;
   for $i (@_) {
      print STDERR "$i";
   }
   print STDERR NL;
}

sub logg {
   my $i;
   for $i (@_) {
      print STDOUT "$i";
   }
   print STDOUT NL;
}

sub xpand {
   my ($rrl) = @_;
   die("Will not expand a blank URI") if ("" eq $rrl || $rrl =~ m/^\s*$/);
   return $rrl if ($rrl =~ /^http/);
   return $rrl if ($rrl =~ m{^$main::HostUri/});
   return "${main::HostUri}$rrl" if ($rrl =~ m{^/});
   return "${main::HostUri}/$rrl";
}

sub json_request {
   my ($uri) = @_;
   my $url = xpand($uri);
   logg("$uri becomes $url\n");
   my $req = new HTTP::Request->("GET", $url);
   $req->header("Accept" => "application/json");

   my $thing = $::Web->request($req);

   print Dumper::dump($thing);
}

logg(" this is a thing");
logg("with a line ending\n");

my $uri = "/shelf/1";
json_request($uri);

#