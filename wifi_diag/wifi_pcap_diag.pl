#!/usr/bin/perl -w

# Read in a decoded pcap file and generate report
# Usage:  tshark -V -r wifi.pcap | ./wifi_pcap_diag.pl

use strict;
use warnings;
use diagnostics;
use Carp;

use PeerConn;
use Packet;

my %peer_conns = ();

my $cur_pkt = Packet->new(raw_pkt => "");
my $last_pkt = Packet->new(raw_pkt => "");

while (<>) {
  my $ln = $_;
  if ($ln =~ /^Frame (\d+):/) {
    if ($cur_pkt->raw_pkt() ne "") {
      processPkt($cur_pkt);
    }
    $cur_pkt = Packet->new(frame_num => $1,
			   raw_pkt => $ln);
  }
  else {
    $cur_pkt->append($ln);
  }
}

if ($cur_pkt->raw_pkt() ne "") {
  processPkt($cur_pkt);
}

# Print out all peer-conns we found
for my $conn (values %peer_conns) {
  $conn->printme();
  $conn->gen_graphs();
}

exit 0;


sub processPkt {
  my $pkt = shift;

  # Find which station (or AP) sent this pkt.
  # Add graph point for mcs vs time
  # Add graph point for retransmits
  # Check sequence-no gap

  # If pkt is an ACK, it will not have a sender address.  Guess based on
  # previous packet.
  if ($pkt->type_subtype() eq "Acknowledgement (0x001d)") {
    if ($last_pkt->transmitter() eq $pkt->receiver()) {
      $pkt->set_transmitter($last_pkt->receiver());
    }
    else {
      print "ERROR:  Frame " . $pkt->frame_num() . " is ACK for unknown packet.\n";
      $last_pkt = $pkt;
      return;
    }
  }

  my $hash = $pkt->receiver() . "." . $pkt->transmitter();
  my $hash2 = $pkt->transmitter() . "." . $pkt->receiver();

  my $peer_conn;
  if (exists $peer_conns{$hash}) {
    $peer_conn = $peer_conns{$hash};
  }
  else {
    if (exists $peer_conns{$hash2}) {
      $peer_conn = $peer_conns{$hash2};
    }
    else {
      $peer_conn = PeerConn->new(local_addr => $pkt->receiver(),
				 peer_addr => $pkt->transmitter());
      $peer_conns{$hash} = $peer_conn;
    }
  }

  $peer_conn->add_pkt($pkt);

  $last_pkt = $pkt;

  #print "pkt: rcvr: " . $pkt->receiver() . " transmitter: " . $pkt->transmitter() . "\n";
}
