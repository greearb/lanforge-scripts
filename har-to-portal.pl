#!/usr/bin/perl
use strict;
use warnings;
use diagnostics;
use Carp;
#use Time::HiRes;
# wow, this would have been cool but ... nope
use Archive::Har();
use Try::Tiny;
use Getopt::Long;
use utf8;
require JSON;
require JSON::XS;
#use JSON::XS;
use Data::Dumper;
$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
#use constant NA => "NA";
use constant NL   => "\n";
use constant Q    => q(");
use constant a    => q(');
use constant qQ => qq('");
use constant CS   => q(: );
use constant c    => q(,);
use constant dQH  => q(      ." -H ');
use constant CA   => q(=>$::curl_args);
use constant MP   => q(    'method'=>'POST',);
use constant PD   => q(    'post_data'=>);
#use constant nbsp => "&nbsp;";
$| = 1;

package main;

my $usage = qq($0 --har {file.jar} # HAR file saved from browser
  --out {bot.pm}      # portal bot module to create
  --help|-h           # this
  );
our $quiet = 1;
our $help = 0;
our $outfile;
our $harfile;

GetOptions (
   'quiet|q:s'          => \$quiet,
   'help|h'             => \$help,
   'har=s'              => \$::harfile,
   'out|o=s'            => \$::outfile,
) || (print($usage) && exit(1));

if ($help) {
  print($usage);
  exit(0);
}

if (!(defined $::harfile) || !(defined $::outfile)) {
  print $usage;
  exit(1);
}

die("unable to open $::harfile: $!")  unless open(my $fh, "<", $::harfile);
read $fh, my $har_txt, -s $fh; # should yank that into LANforge::Utils
close $fh;
our $Decoder = JSON->new->utf8;
#print "** $har_txt".NL;


## ----- ----- ----- ----- ----- ----- ----- ----- -----
##  Creating an Archive::HAR is not very efficient
## ----- ----- ----- ----- ----- ----- ----- ----- -----
#$::harfile = Archive::Har->new();
#$::harfile->string($har_txt);
#print Dumper($::harfile);
#foreach my $log_entry ($::harfile->entries()) {
#  print "Log Entry: ".$log_entry->pageref() .NL if ($log_entry->pageref());
#  print "DT: ".$log_entry->started_date_time() .NL if ($log_entry->started_date_time());
#  #print "Request: ".Dumper($log_entry->request()) .NL;
#  print "Request Url:".$log_entry->request()->{url} .NL;
#  my $headers = $log_entry->request()->{headers};
#  foreach my $header (@$headers) {
#    print "Header: ".$header->{name} .NL;
#  }
#  #print "Response: ".Dumper($log_entry->response()) .NL;
#  #print "Server: ".$log_entry->server_ip_address() .NL;
#}

## ----- ----- ----- ----- ----- ----- ----- ----- -----
##  Creating a plain JSON object is more efficient,
##  and more compatible with FF
## ----- ----- ----- ----- ----- ----- ----- ----- -----
my $json = $::Decoder->decode($har_txt);
$::Decoder->canonical(1);
$::Decoder->allow_blessed(1);
my %ordered_entries = ();
print "I see ".(length($json->{log}->{entries}))." entries\n";

foreach my $entry (@{$json->{log}->{entries}}) {
  my $request_start = $entry->{startedDateTime};
  $ordered_entries{$request_start} = \$entry;
}
print "------------------------------------------------------------------------------------\n";
my $found_redirect = 0;
my $found_login_post = 0;
die("unable to open $::outfile: $!")  unless open($fh, ">", $::outfile);
for my $request_start ( sort keys %ordered_entries ) {
  print "Start: $request_start\n";
  my $entry       = $ordered_entries{$request_start};
  my $request     = $$entry->{request};
  my $response    = $$entry->{response};

  my $req_headers = $request->{headers};
  my $res_headers = $response->{headers};

  my $req_cookies = $request->{cookies} if (defined $request->{cookies}) || [];
  my $res_cookies = $response->{cookies} if (defined $response->{cookies}) || [];

  my $url         = $request->{url};
  my $method      = $request->{method};
  print $fh "------------------------------------------------------------------------------------\n";
  print $fh "$method: $url\n";
  print $fh "------------------------------------------------------------------------------------\n";
  print $fh "request({'curl_args'".CA;

  for my $header_e (@$req_headers) {
    print $fh NL.dQH. $header_e->{name} .CS. $header_e->{value} .qQ;
  }
  print $fh c.NL;
  if ($method eq "POST") {
    $found_login_post++;
    print $fh MP.NL;
    print $fh PD.a. $request->{'postData'}->{text} .a.c.NL;
  }
  print $fh q(    'url'=>).Q. $url .Q.c.NL;
  print $fh q(    'print'=>1).NL;
  print $fh q[}, \@response);].NL.NL;
  for my $req_cookie(@$req_cookies) {
    print $fh "    request_cookie ";
    print $fh "{'".$req_cookie->{name}."'} = '".$req_cookie->{value}."';\n";
  }
  print $fh NL;
  if ($response->{status} == 301 || $response->{status} == 302) {
    $found_redirect++;
    print $fh "Expect redirect: ".$response->{status}.NL;
  }
  for my $header_e (@$res_headers) {
    print $fh "    response_header: ".$header_e->{name} .": ".$header_e->{value} .NL;
  }
  for my $res_cookie(@$res_cookies) {
    print $fh "    response_cookie";
    print $fh "{'".$res_cookie->{name}."'} = '".$res_cookie->{value}."';\n";
  }
} # ~for each request sorted by time

#
  # create find_redirect_url()

  # create submit_login()

  # create interpret_login_response()

  # create submit_logout()
close $fh;
###
###
###
