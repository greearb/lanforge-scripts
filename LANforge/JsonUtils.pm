# JsonUtils
package LANforge::JsonUtils;
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
use JSON;

if (defined $ENV{'DEBUG'}) {
   use Data::Dumper;
   use diagnostics;
   use Carp;
   $SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
}

our $NL="\n";

our @EXPORT_OK=qw(err logg xpand json_request get_links_from);

sub err {
   my $i;
   for $i (@_) {
      print STDERR "$i";
   }
   print STDERR $::NL;
}

sub logg {
   my $i;
   for $i (@_) {
      print STDOUT "$i";
   }
   print STDOUT $::NL;
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
   my $req = new HTTP::Request("GET", $url);
   $req->header("Accept" => "application/json");
   my $response = $::Web->request($req);
   return $::Decoder->decode($response->content);
}

sub get_links_from {
   my ($rh_glf, $arrayname) = @_;
   my $ra_glf2 = $rh_glf->{$arrayname};
   my $ra_glf_links2 = [];
   for my $rh_glf2 (@$ra_glf2) {
      for my $key (keys %$rh_glf2) {
         my $v = $rh_glf2->{$key};
         next if (!(defined $v->{'_links'}));
         push(@$ra_glf_links2, $v->{'_links'});
      }
   }
   #print Dumper($ra_links2);
   return $ra_glf_links2;
}
1;