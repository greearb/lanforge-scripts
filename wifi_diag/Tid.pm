package Tid;

use warnings;
use strict;
use bigint;

my $warn_dup_ba_once = 1;

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

  my $pkt_count = @{$self->{pkts}};

  # If this is a block-ack, then check for previous frames that would match.
  if ($pkt->type_subtype() eq "802.11 Block Ack (0x0019)") {
    my $transmitter = $pkt->transmitter();
    my $starting_seqno = $pkt->{ba_starting_seq};
    my $i;
    my $bitmap = $pkt->{ba_bitmap}; # 0100000000000000 for instance
    my $bi_as_long = 0;
    my $bi_mask = 0;
    my $q;
    for ($q = 0; $q < 8; $q++) {
      my $bmap_octet = substr($bitmap, $q * 2, 2);
      my $bmi = hex($bmap_octet);
      #print "bmap-octet: $bmap_octet bmi: " . hex($bmi) . "\n";
      $bi_as_long |= ($bmi << ($q * 8));
    }

    for ($i = 0; $i<$pkt_count; $i++) {
      my $tmp = $self->{pkts}[$i];
      #print "checking tmp-pkt: " . $tmp->seqno();
      #print " transmitter: " . $tmp->transmitter();
      #print " pkt-rcvr: " . $pkt->receiver() . "\n";
      if ($tmp->transmitter() eq $pkt->receiver()) {
	if ($tmp->seqno() >= $starting_seqno && $tmp->seqno() < ($starting_seqno + 64)) {
	  # tmp pkt might match this BA bitmap..check closer.
	  my $diff = $tmp->seqno() - $starting_seqno;
	  
	  if ($bi_as_long & (1 << $diff)) {
	    # Found a matching frame.
	    $bi_mask |= (1 << $diff);

	    if ($tmp->block_acked_by() != -1) {
	      # This seems to be a common thing, warn once and not again.
	      if ($warn_dup_ba_once) {
		print "WARNING:  block-ack frame: " . $pkt->frame_num() . " acking frame: " .
		  $tmp->frame_num() . " already block-acked by frame: " . $tmp->block_acked_by() . ".  This warning will not be shown again.\n";
		$warn_dup_ba_once = 0;
	      }
	    }
	    elsif ($tmp->acked_by() != -1) {
	      print "WARNING:  block-ack frame: " . $pkt->frame_num() . " acking frame: " .
		$tmp->frame_num() . " already acked by frame: " . $tmp->acked_by() . "\n";
	    }
	    $tmp->set_block_acked_by($pkt->frame_num());
	  }
	}
      }
    }# for all pkts

    # See if we block-acked anything we could not find?
    if ($bi_mask != $bi_as_long) {
      my $missing = $bi_mask ^ $bi_as_long;
      my $missing_str = "";
      for ($i = 0; $i<64; $i++) {
	if ($missing & (1<<$i)) {
	  my $missing_seqno = $starting_seqno + $i;
	  $missing_str .= $missing_seqno . " ";

	  # Add a dummy pkt
	  my $dummy = Packet->new(transmitter => $pkt->receiver(),
				  data_subtype => "DUMMY_BA_ACKED",
				  timestamp => $pkt->timestamp(),
				  seqno => $missing_seqno,
				  tid => $self->tidno());
	  $dummy->block_acked_by($pkt->frame_num());
	  push(@{$self->{pkts}}, $dummy);
	  #print "pushing dummy pkt, seqno: $missing_seqno\n";
	}
      }
      print "WARNING:  block-ack frame: " . $pkt->frame_num() . " acked frames we did not capture, found-these: " . $bi_mask->as_hex .
	" acked these: " . $bi_as_long->as_hex . " missing: " . $missing->as_hex . "($missing_str), starting-seq-no: $starting_seqno\n";
    }
  }

  # Shift off old frames.
  while ($pkt_count > 0) {
    my $tmp = shift(@{$self->{pkts}});
    if (($tmp->timestamp() + 60 < $pkt->timestamp()) ||
	($pkt_count > 1000)) {
      if (! $tmp->was_acked()) {
	if ($tmp->wants_ack()) {
	  print "WARNING:  did not find ack for frame: " . $tmp->frame_num() . ", removing after processing frame: " . $pkt->frame_num() . "\n";
	}
      }
      $pkt_count--;
      next; # Drop frames when we have more than 1000 or they are older than 1 minute ago
    }
    # Put this one back on
    unshift(@{$self->{pkts}}, $tmp);
    last;
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
