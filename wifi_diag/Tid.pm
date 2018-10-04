package Tid;

use warnings;
use strict;

sub new {
  my $class = shift;
  my %options = @_;

  my $self = {
	      pkts => [],
	      %options,
	     };

  bless($self, $class);
  return($self);
}

sub tidno {
  my $self = shift;
  return $self->{tidno};
}

sub add_pkt {
  my $self = shift;
  my $pkt = shift;

  push(@{$self->{pkts}}, $pkt);
}

sub get_pkts {
  my $self = shift;
  return @{$self->{pkts}};
}

sub printme {
  my $self = shift;
  print "  tidno: " . $self->tidno() . "\n";
  print "   pkt-count: " . $self->get_pkts() . "\n";
}

1;
