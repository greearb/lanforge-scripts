#!/usr/bin/perl -w

# Read in a decoded pcap file and generate report
# Usage:  tshark -V -r wifi.pcap | ./wifi_pcap_diag.pl

use strict;
use warnings;
use diagnostics;
use Carp;

use PeerConn;
use Packet;
use Getopt::Long;

my %peer_conns = ();

my $pkts_sofar = 0;
my $start_time = time();

my $cur_pkt = Packet->new(raw_pkt => "");
my $last_pkt = Packet->new(raw_pkt => "");
my $glb_fh_ba;

my $dut = "";
my $report_prefix = "wifi-diag-";
my $non_dut_frames = 0;
my $show_help = 0;

my $usage = "$0
--dut {bssid-of-DUT}   # Orient reports with this as upstream peer (lower-case MAC address)
--report_prefix  {string} # Prefix used for report files (default is $report_prefix)
--help                 # Show this help info.
";


GetOptions
(
 'help|h'            => \$show_help,
 'dut=s'             => \$dut,
 'report_prefix=s'   => \$report_prefix,
 ) || (print($usage) && exit(1));


if ($show_help) {
   print $usage;
   exit 0
}

my $rpt_fname = $report_prefix . "glb-ba-rpt.txt";
open($glb_fh_ba, ">", $rpt_fname) or die("Can't open $rpt_fname for writing: $!\n");


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

printProgress();

# Print out all peer-conns we found
for my $conn (values %peer_conns) {
  $conn->printme();
  $conn->gen_graphs();
}

if ($dut ne "") {
  print "NON-DUT frames in capture: $non_dut_frames\n";
}

exit 0;

sub printProgress {
  my $now = time();
  my $diff_sec = $now - $start_time;
  my $hour = int($diff_sec / (60 * 60));
  my $min = int($diff_sec / 60);
  my $sec = $diff_sec - ($hour * 60 * 60 + $min * 60);
  my $pps = int($pkts_sofar / $diff_sec);
  print STDERR "NOTE:  Processed $pkts_sofar packets in $hour:$min:$sec far ($pps pps).\n";
}

sub processPkt {
  my $pkt = shift;

  # Find which station (or AP) sent this pkt.
  # Add graph point for mcs vs time
  # Add graph point for retransmits
  # Check sequence-no gap

  $pkts_sofar++;
  if (($pkts_sofar % 10000) == 0) {
    printProgress();
  }

  # If pkt is an ACK, it will not have a sender address.  Guess based on
  # previous packet.
  if ($pkt->type_subtype() eq "Acknowledgement (0x001d)") {
    if ($last_pkt->transmitter() eq $pkt->receiver()) {
      $pkt->set_transmitter($last_pkt->receiver());
      if ($last_pkt->acked_by() != -1) {
	print "WARNING:  ack frame: " . $pkt->frame_num() . " acking frame: " .
		$last_pkt->frame_num() . " already acked by frame: " . $last_pkt->acked_by() . "\n";
      }
      elsif ($last_pkt->block_acked_by() != -1) {
	print "WARNING:  ack frame: " . $pkt->frame_num() . " acking frame: " .
		$last_pkt->frame_num() . " already block-acked by frame: " . $last_pkt->block_acked_by() . "\n";
      }
      else {
	$last_pkt->set_acked_by($pkt->frame_num());
      }
    }
    else {
      print "ERROR:  Frame " . $pkt->frame_num() . " is ACK for unknown packet.\n";
      $last_pkt = $pkt;
      return;
    }
  }

  if ($dut ne "") {
    # Ignore frames not to/from DUT
    if (!(($dut eq $pkt->receiver()) ||
	  ($dut eq $pkt->transmitter()))) {
      $non_dut_frames++;
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
      if ($dut eq $pkt->receiver()) {
	$peer_conn = PeerConn->new(glb_fh_ba => $glb_fh_ba,
				   report_prefix => $report_prefix,
				   local_addr => $pkt->transmitter(),
				   peer_addr => $pkt->receiver());
      }
      else {
	$peer_conn = PeerConn->new(glb_fh_ba => $glb_fh_ba,
				   report_prefix => $report_prefix,
				   local_addr => $pkt->receiver(),
				   peer_addr => $pkt->transmitter());
      }
      $peer_conns{$hash} = $peer_conn;
    }
  }

  $peer_conn->add_pkt($pkt);

  $last_pkt = $pkt;

  #print "pkt: rcvr: " . $pkt->receiver() . " transmitter: " . $pkt->transmitter() . "\n";
}
