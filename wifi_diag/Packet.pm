package Packet;

use warnings;
use strict;

sub new {
  my $class = shift;
  my %options = @_;

  my $self = {
	      type_subtype => "UNKNOWN",
	      receiver => "UNKNOWN",
	      transmitter => "UNKNOWN",
	      %options,
	      amsdu_frame_count => 0,
	      ssi_sig_found => 0,
	      tid => 17, # anything that does not specify a tid gets this.
	     };

  bless($self, $class);
  return($self);
}

sub raw_pkt {
  my $self = shift;
  return $self->{raw_pkt};
}

sub append {
  my $self = shift;
  my $ln = shift;

  $self->{raw_pkt} .= $ln;

  if ($ln =~ /\s*Transmitter address: .*\((\S+)\)/) {
    $self->{transmitter} = $1;
  }
  elsif ($ln =~ /\s*Receiver address: .*\((\S+)\)/) {
    $self->{receiver} = $1;
  }
  elsif ($ln =~ /\s*Fragment number: (\d+)/) {
    $self->{fragno} = $1;
  }
  elsif ($ln =~ /\s*Sequence number: (\d+)/) {
    $self->{seqno} = $1;
  }
  elsif ($ln =~ /\s*Type\/Subtype: (.*)/) {
    $self->{type_subtype} = $1;
  }
  elsif ($ln =~ /.* = Starting Sequence Number: (\d+)/) {
    $self->{ba_starting_seq} = $1;
  }
  elsif ($ln =~ /.* = TID for which a Basic BlockAck frame is requested: (\S+)/) {
    $self->{ba_tid} = $1;
  }
  elsif ($ln =~ /.*Block Ack Bitmap: (\S+)/) {
    $self->{ba_bitmap} = $1;
  }
  elsif ($ln =~ /\s*Data Rate: (.*)/) {
    $self->{datarate} = $1;
  }
  elsif ($ln =~ /\s*VHT information/) {
    $self->{is_vht} = 1;
  }
  elsif ($ln =~ /\s*Bandwidth: (.*)/) {
    $self->{bandwidth} = $1;
  }
  elsif ($ln =~ /\s*User 0: MCS (.*)/) {
    $self->{mcs} = $1;
  }
  elsif ($ln =~ /.* = Spatial streams 0: (.*)/) {
    $self->{nss} = $1;
  }
  elsif ($ln =~ /.* = TID: (.*)/) {
    $self->{tid} = $1;
  }
  elsif ($ln =~ /.* = Payload Type: (.*)/) {
    $self->{payload_type} = $1;
  }
  elsif ($ln =~ /\s+\[Data Rate: (.*)\]/) {
    $self->{datarate} = $1;
  }
  elsif ($ln =~ /\s*SSI Signal: (.*)/) {
    if ($self->{ssi_sig_found} == 0) {
      $self->{ssi_combined} = $1;
      $self->{ssi_sig_found}++;
    }
    elsif ($self->{ssi_sig_found} == 1) {
      $self->{ssi_ant_0} = $1;
      $self->{ssi_sig_found}++;
    }
    elsif ($self->{ssi_sig_found} == 2) {
      $self->{ssi_ant_1} = $1;
      $self->{ssi_sig_found}++;
    }
    elsif ($self->{ssi_sig_found} == 3) {
      $self->{ssi_ant_2} = $1;
      $self->{ssi_sig_found}++;
    }
    elsif ($self->{ssi_sig_found} == 4) {
      $self->{ssi_ant_3} = $1;
      $self->{ssi_sig_found}++;
    }
  }
  # AMPDU and such...
  elsif ($ln =~ /\s*A-MSDU Subframe #(\d+)/) {
    if ($1 > $self->{amsdu_frame_count}) {
      $self->{amsdu_frame_count} = $1;
    }
  }
}

sub frame_num {
  my $self = shift;
  return $self->{frame_num};
}

sub type_subtype {
  my $self = shift;
  return $self->{type_subtype};
}

sub transmitter {
  my $self = shift;
  return $self->{transmitter};
}

sub receiver {
  my $self = shift;
  return $self->{receiver};
}

sub tid {
  my $self = shift;
  return $self->{tid};
}

sub set_transmitter {
  my $self = shift;
  my $tx = shift;
  $self->{transmitter} = $tx;
}

sub set_receiver {
  my $self = shift;
  my $rx = shift;
  $self->{receiver} = $rx;
}

1;
