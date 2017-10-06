package LANforge::GuiJson;
use strict;
use warnings;
use JSON;
use base 'Exporter';

if (defined $ENV{'DEBUG'}) {
   use Data::Dumper;
   use diagnostics;
   use Carp;
   $SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
}

our $NL="\n";

our @EXPORT_OK=qw(GetHeaderMap GuiResponseToArray GuiResponseToHash GetRecordsMatching GetFields);
our $refs_example = q( \@portnames or ["sta1", "sta2"] not ("sta1", "sta2"));
=pod
=head1 GuiResponseToArray
=cut
sub GuiResponseToArray {
   my $response = shift;
   my $ra_data = decode_json($response);
   return $ra_data;
}

=pod
=head1 GuiResponseToHash
=cut
sub GuiResponseToHash {
   my $response = shift;
   my $ra_data = decode_json($response);
   my $rh_data = {};
   $rh_data->{'handler'} = $ra_data->[0]->{'handler'};
   $rh_data->{'uri'} = $ra_data->[1]->{'uri'};
   $rh_data->{'header'} = $ra_data->[2]->{'header'};
   $rh_data->{'data'} = $ra_data->[3]->{'data'};
   #print Dumper($rh_data);
   return $rh_data;
}

=pod
=head1 GetHeaderMap
GuiJson::GenHeaderMap expects a reference to a header array like
{ 'header' => ['a', 'b', 'c']}
=cut
sub GetHeaderMap {
   my $r_header = shift;
   my $ra_header = undef;
   #if (defined $ENV{'DEBUG'}) {
   #   print "DEBUGGING a:".ref($r_header)."\n";
   #   print Dumper($r_header);
   #}
   if (ref($r_header) eq 'ARRAY') {
      $ra_header = $r_header;
   }
   elsif (ref($r_header) eq 'HASH' ) {
      if( defined $r_header->{'header'}) {
         $ra_header = $r_header->{'header'};
      }
   }

   my $rh_headermap = {};
   if (!defined $ra_header) {
      print STDERR "GetHeaderMap: arg1 needs to be an array of header names, you get an empty hash\n";
      return $rh_headermap;
   }
   my $index = 0;
   for my $headername (@$ra_header) {
      $rh_headermap->{$headername} = $index;
      $index++;
   }
   return $rh_headermap;
}

=pod
=head1 GetRecordsMatching
GetRecordsMatching expects results of GetGuiResponseToHash and a list of port EIDs or names
$ra_ports = GetRecordsMatching($rh_data, $header_name, $value)
=cut
sub GetRecordsMatching {
   my $rh_resp_map = shift;
   my $header_name = shift;
   my $ra_needles = shift;
   my $ra_results = [];
   if (!defined $rh_resp_map || ref($rh_resp_map) ne 'HASH') {
      print STDERR "GetRecordsMatching wants arg1: json data structure\n";
      return $ra_results;
   }
   if (!defined $header_name || $header_name eq '') {
      print STDERR "GetRecordsMatching wants arg2: header name\n";
      return $ra_results;
   }
   my $rh_headers = GetHeaderMap($rh_resp_map);
   if (!defined $rh_headers->{$header_name}) {
      print STDERR "GetRecordsMatching cannot find header named <$header_name>\n";
      return $ra_results;
   }
   #print "GetRecordsMatching arg3 is ".ref($ra_needles)."\n";
   if (!defined $ra_needles || ref($ra_needles) ne 'ARRAY') {
      print Dumper($ra_needles);
      my $example = q( \@portnames or ["sta1", "sta2"] not ("sta1", "sta2"));
      print STDERR "GetRecordsMatching wants arg3: list values to match against <$header_name>.\nPass array references, eg:\n$example\n";
      return $ra_results;
   }
   #print STDERR Dumper($ra_needles);
   #print Dumper($rh_headers);

   my $value = undef;
   my @matches = undef;
   for my $ra_port (@{$rh_resp_map->{'data'}}) {
      $value = $ra_port->[ $rh_headers->{$header_name}];
      #print "$header_name: $value\n";
      @matches = grep { /$value/ } @$ra_needles;
      if (@matches) {
         push(@$ra_results, $ra_port);
      }
   }

   return $ra_results;
}

=pod
=head1 GetFields
Returns matching fields from a record;
$ra_needles are an array of strings to match to select records
$ra_field_names are field names to return from those records
$rh = GetFields($rh_response_map, $header_name, $ra_needles, $ra_field_names)
=cut
sub GetFields {
  my $rh_resp_map = shift;
  my $header_name = shift;
  my $ra_needles = shift;
  my $ra_field_names = shift;
  my $ra_records = [];
  my $rh_field_values = {};

  if (!defined $rh_resp_map || ref($rh_resp_map) ne 'HASH') {
     print STDERR "GetFields wants arg1: json data structure\n";
     return $rh_field_values;
  }
  if (!defined $header_name || $header_name eq '') {
     print STDERR "GetFields wants arg2: header name\n";
     return $rh_field_values;
  }
  my $rh_headers = GetHeaderMap($rh_resp_map);
  #print "Header names: ". Dumper($rh_headers);
  
  if (!defined $rh_headers->{$header_name}) {
     print STDERR "GetFields cannot find header named <$header_name>\n";
     return $rh_field_values;
  }
  if (!defined $ra_needles || ref($ra_needles) ne 'ARRAY') {
     print Dumper($ra_needles);

     print STDERR "GetFields wants arg3: list values to match against <$header_name>.\nPass array references, eg:\n$::refs_example\n";
     return $rh_field_values;
  }
  if (!defined $ra_field_names || ref($ra_field_names) ne 'ARRAY') {
     my $arg_str = join(", ", @$ra_needles);
     print STDERR "GetFields wants arg4: list field names to return if <$header_name> matches <$arg_str>\nPass array references, eg:\n$::refs_example\n";
     return $rh_field_values;
  }

  $ra_records = GetRecordsMatching($rh_resp_map, $header_name, $ra_needles);
  return $rh_field_values if (@$ra_records < 1);

  for my $ra_record (@$ra_records) {
    next if (@$ra_record < 1);
    next if (! defined @$ra_record[$rh_headers->{$header_name}]);
    my $record_name = @$ra_record[$rh_headers->{$header_name}];
    next if (!defined $record_name || "$record_name" eq "");
    #print "record name[$record_name]\n";

    #print Dumper($ra_record);
    my $rh_record_vals = {};
    $rh_field_values->{$record_name} = $rh_record_vals;
    #print Dumper($ra_field_names);

    for my $field_name (@$ra_field_names) {
      next if (!defined $rh_headers->{$field_name});
      my $field_idx = $rh_headers->{$field_name};
      next if (!defined $field_name || "$field_name" eq "");
      next if (!defined @$ra_record[$rh_headers->{$field_name}]);
      #print "Field Name $field_name [".@$ra_record[$field_idx]."] ";
      $rh_record_vals->{$field_name} = @$ra_record[$field_idx];
    }
    #print Dumper($rh_record_vals);
  }
  return $rh_field_values;
}
1;
