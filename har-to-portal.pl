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
use constant NL => "\n";
#use constant Q => '"';
#use constant q => "'";
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
#print Dumper(\$json);

my %ordered_entries = ();
print "I see ".(length($json->{log}->{entries}))." entries\n";

foreach my $entry (@{$json->{log}->{entries}}) {
  my $request_start = $entry->{startedDateTime};
  $ordered_entries{$request_start} = \$entry;
  #print Dumper(\$entry);
  #print "------------------------------------------------------------------------------------\n";
}
print "------------------------------------------------------------------------------------\n";
print "------------------------------------------------------------------------------------\n";
print "------------------------------------------------------------------------------------\n";
print "------------------------------------------------------------------------------------\n";
for my $request_start ( sort keys %ordered_entries ) {
  print "Start: $request_start\n";
  my $entry = $ordered_entries{$request_start};
  #print Dumper($entry);
  #print "REF: ".ref($entry);
  my $request = $$entry->{request};
  print Dumper($request);
  my $ra_headers = $request->{headers}; 
  
  my $url = $request->{url};
  print "URL: $url\n";
  for my $header_e (@$ra_headers) {
    print "H: ".$header_e->{name} .": ".$header_e->{value} .NL;
  }
  last;
}

#die("unable to open $::outfile: $!")  unless open($fh, ">", $::outfile);
  # create find_redirect_url()
  
  # create submit_login()
  
  # create interpret_login_response()
  
  # create submit_logout()
close $fh;
###
###
###