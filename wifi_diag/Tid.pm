package Tid;

use warnings;
use strict;

sub new {
  my $class = shift;
  my %options = @_;

  my $self = {
	      pkts => [],
	      tx_retrans => 0,
	      rx_retrans => 0,
	      rx_pkts => 0,
	      tx_pkts => 0,
	      tot_pkts => 0,
	      %options,
	     };

  bless($self, $class);

  my $rpt_fname = $self->{addr_a} . "." . $self->{addr_b} . "-" . $self->tidno() . "-" . "rpt.txt";
  open(my $MCS, ">", $rpt_fname) or die("Can't open $rpt_fname for writing: $!\n");
  $self->{mcs_fh} = $MCS;

  return $self;
}

sub tidno {
  my $self = shift;
  return $self->{tidno};
}

sub add_pkt {
  my $self = shift;
  my $pkt = shift;

  $self->{tot_pkts}++;
  if ($pkt->receiver() eq $self->{addr_a}) {
    $self->{rx_pkts}++;
    if ($pkt->retrans()) {
      $self->{rx_retrans}++;
    }
  }
  else {
    $self->{tx_pkts}++;
    $self->{tx_retrans}++;
  }

  # Generate reporting data for this pkt
  my $fh = $self->{mcs_fh};
  print $fh "" . $pkt->timestamp() . "\t" . $self->tidno() . "\t" . $pkt->datarate() . "\t" . $pkt->retrans() . "\n";

  push(@{$self->{pkts}}, $pkt);
}

sub get_pkts {
  my $self = shift;
  return @{$self->{pkts}};
}

sub printme {
  my $self = shift;
  print "   tidno: " . $self->tidno() . " pkt-count: " . $self->get_pkts()
    . " tx-pkts: " . $self->{tx_pkts} . " tx-retrans: " . $self->{tx_retrans}
    . " rx-pkts: " . $self->{rx_pkts} . " rx-retrans: " . $self->{rx_retrans} . "\n";
}

1;
