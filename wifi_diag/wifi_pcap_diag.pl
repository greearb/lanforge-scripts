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
my $glb_fh_ba_tx;
my $glb_fh_ba_rx;
my $glb_fh_mcs_ps;
my $glb_fh_mcs_tx;
my $glb_fh_mcs_rx;
my $glb_fh_rtx_tx;
my $glb_fh_rtx_rx;

my %glb_mcs_tx_hash = ();
my %glb_mcs_rx_hash = ();

my $dut = "";
my $report_prefix = "wifi-diag-";
my $non_dut_frames = 0;
my $show_help = 0;
my $gen_report = 0;
my $report_html = "";

my $usage = "$0
--dut {bssid-of-DUT}   # Orient reports with this as upstream peer (lower-case MAC address)
--gen_report           # Generate report off previously generated global data
--report_prefix  {string} # Prefix used for report files (default is $report_prefix)
--help                 # Show this help info.
";


GetOptions
(
 'help|h'            => \$show_help,
 'dut=s'             => \$dut,
 'report_prefix=s'   => \$report_prefix,
 'gen_report'        => \$gen_report,
 ) || (print STDERR $usage && exit(1));


if ($show_help) {
   print $usage;
   exit 0
}

my $glb_ba_tx_fname = $report_prefix . "glb-ba-tx-rpt.txt";
my $glb_ba_rx_fname = $report_prefix . "glb-ba-rx-rpt.txt";
my $glb_mcs_ps_fname = $report_prefix . "glb-mcs-ps-rpt.txt";
my $glb_mcs_tx_fname = $report_prefix . "glb-mcs-tx-rpt.txt";
my $glb_mcs_rx_fname = $report_prefix . "glb-mcs-rx-rpt.txt";
my $glb_rtx_tx_fname = $report_prefix . "glb-rtx-tx-rpt.txt";
my $glb_rtx_rx_fname = $report_prefix . "glb-rtx-rx-rpt.txt";

if ($gen_report) {
  $report_html .= genGlobalReports();
  saveHtmlReport();
  exit 0;
}

open($glb_fh_ba_tx,  ">", $glb_ba_tx_fname) or die("Can't open $glb_ba_tx_fname for writing: $!\n");
open($glb_fh_ba_rx,  ">", $glb_ba_rx_fname) or die("Can't open $glb_ba_rx_fname for writing: $!\n");
open($glb_fh_mcs_ps, ">", $glb_mcs_ps_fname) or die("Can't open $glb_mcs_ps_fname for writing: $!\n");
open($glb_fh_mcs_tx, ">", $glb_mcs_tx_fname) or die("Can't open $glb_mcs_tx_fname for writing: $!\n");
open($glb_fh_mcs_rx, ">", $glb_mcs_rx_fname) or die("Can't open $glb_mcs_rx_fname for writing: $!\n");
open($glb_fh_rtx_tx, ">", $glb_rtx_tx_fname) or die("Can't open $glb_rtx_tx_fname for writing: $!\n");
open($glb_fh_rtx_rx, ">", $glb_rtx_rx_fname) or die("Can't open $glb_rtx_rx_fname for writing: $!\n");

my $hdr =  "#timestamp\ttid\ttime_diff\tperiod_tot_pkts_ps\t" .
      "period_rx_pkts_ps\tperiod_rx_retrans_pkts_ps\tperiod_rx_amsdu_pkts_ps\tperiod_rx_retrans_amsdu_pkts_ps\tperiod_dummy_rx_pkts_ps\t" .
      "period_tx_pkts_ps\tperiod_tx_retrans_pkts_ps\tperiod_tx_amsdu_pkts_ps\tperiod_tx_retrans_amsdu_pkts_ps\tperiod_dummy_tx_pkts_ps\n";
print $glb_fh_mcs_ps $hdr;

# Global stats logic.
my $last_ps_timestamp = 0;
my $tot_pkts = 0;
my $rx_pkts = 0;
my $rx_amsdu_pkts = 0;
my $rx_retrans_pkts = 0;
my $rx_amsdu_retrans_pkts = 0;
my $dummy_rx_pkts = 0;
my $tx_pkts = 0;
my $tx_amsdu_pkts = 0;
my $tx_retrans_pkts = 0;
my $tx_amsdu_retrans_pkts = 0;
my $dummy_tx_pkts = 0;

my $last_tot_pkts = 0;
my $last_rx_pkts = 0;
my $last_rx_amsdu_pkts = 0;
my $last_rx_retrans_pkts = 0;
my $last_rx_amsdu_retrans_pkts = 0;
my $last_dummy_rx_pkts = 0;
my $last_tx_pkts = 0;
my $last_tx_amsdu_pkts = 0;
my $last_tx_retrans_pkts = 0;
my $last_tx_amsdu_retrans_pkts = 0;
my $last_dummy_tx_pkts = 0;

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

$report_html .= genGlobalReports();

# Print out all peer-conns we found
for my $conn (values %peer_conns) {
  $conn->printme();
  $conn->gen_graphs();
}

saveHtmlReport();

if ($dut ne "") {
  print "NON-DUT frames in capture: $non_dut_frames\n";
}

exit 0;

sub saveHtmlReport {
  my $html = "<HTML>
<HEAD>
   <TITLE>WiFi Diag Report</TITLE>
</HEAD>
<BODY TEXT=\"#3366AA\" BGCOLOR=\"#FFFFFF\" LINK=\"#AA7700\" VLINK=\"#AA7700\"
ALINK=\"#FF0000\">

<CENTER>
<br>
<b><font color=\"006666\">WiFi Diag Report.</font></b>
<P>
";

  $html .= $report_html;

  $html .= "</BODY>
</HTML>\n";

  my $tmp = "$report_prefix/index.html";
  open(my $IDX, ">", $tmp) or die("Can't open $tmp for writing: $!\n");
  print $IDX $html;
  close $IDX;

  print STDERR "Report saved to: $tmp\n";
}

sub genTimeGnuplot {
  my $ylabel = shift;
  my $title = shift;
  my $cols = shift;
  my $graph_data = shift;

  my $text ="# auto-generated gnuplot script
#!/usr/bin/gnuplot
reset
set terminal png

set xdata time
set timefmt \"\%s\"
set format x \"\%M:\%S\"

set xlabel \"Date\"
set ylabel \"$ylabel\"

set title \"$title\"
set key below
set grid
plot \"$graph_data\" using $cols title \"$title\"\n";
  return $text;
}

sub doTimeGraph {
  my $ylabel = shift;
  my $title = shift;
  my $cols = shift;
  my $data_file = shift;
  my $out_file = shift;

  my $html = "";

  my $text = genTimeGnuplot($ylabel, $title, $cols, $data_file);
  my $png_fname = "$report_prefix$out_file";
  my $tmp = $report_prefix . "_gnuplot_tmp_script.txt";
  open(my $GP, ">", $tmp) or die("Can't open $tmp for writing: $!\n");
  print $GP $text;
  close $GP;
  my $cmd = "gnuplot $tmp > $png_fname";
  print "cmd: $cmd\n";
  system($cmd);

  $html .= "<img src=\"$out_file\" alt=\"$title\"><br>\n";
  return $html;
}

sub htmlMcsHistogram {
  my $html = "TX Encoding rate histogram.\n
<table><tr><th>Rate Mbps</th><th>Packets</th><th>Percentage</th></tr>";
  foreach my $name (sort {$a <=> $b} keys %glb_mcs_tx_hash) {
    $html .= sprintf("<tr><td>%s</dt><td>%s</td><td>%f</td></tr>\n", $name, $glb_mcs_tx_hash{$name}, $glb_mcs_tx_hash{$name} / $tx_pkts);
  }
  $html .= "</table><P>\n";

  $html .= "RX Ecoding rate histogram.\n
<table><tr><th>Rate Mbps</th><th>Packets</th><th>Percentage</th></tr>";
  foreach my $name (sort {$a <=> $b} keys %glb_mcs_rx_hash) {
    $html .= sprintf("<tr><td>%s</dt><td>%s</td><td>%f</td></tr>\n", $name, $glb_mcs_rx_hash{$name}, $glb_mcs_rx_hash{$name} / $rx_pkts);
  }
  $html .= "</table><P>\n";
  return $html;
}

sub genGlobalReports {
  my $html = "";

  $html .= htmlMcsHistogram();

  # General idea is to write out gnumeric scripts and run them.

  $html .= "\n\n<P>MCS/Encoding Rates over time<P>\n";
  $html .= doTimeGraph("Encoding Rate Mbps", "TX Packet encoding rate over time", "1:2", $glb_mcs_tx_fname, "glb-mcs-tx.png");
  $html .= doTimeGraph("Encoding Rate Mbps", "RX Packet encoding rate over time", "1:2", $glb_mcs_rx_fname, "glb-mcs-rx.png");
  $html .= doTimeGraph("Retransmits", "TX Packet Retransmits over time", "1:2", $glb_rtx_tx_fname, "glb-mcs-tx-retrans.png");
  $html .= doTimeGraph("Retransmits", "RX Packet Retransmits over time", "1:2", $glb_rtx_rx_fname, "glb-mcs-rx-retrans.png");

  # Global per-second stats
  $html .= doTimeGraph("Total-pps", "Total Packet per sec", "1:4", $glb_mcs_ps_fname, "glb-mcs-tot-ps.png");
  $html .= doTimeGraph("RX-pps", "RX Packet per sec", "1:5", $glb_mcs_ps_fname, "glb-mcs-rx-ps.png");
  $html .= doTimeGraph("RX-retrans-ps", "RX Retrans per sec", "1:6", $glb_mcs_ps_fname, "glb-mcs-rx-amsdu-ps.png");
  $html .= doTimeGraph("RX-amsdu-pps", "RX AMSDU per sec", "1:7", $glb_mcs_ps_fname, "glb-mcs-rx-amsdu-ps.png");
  $html .= doTimeGraph("RX-retrans-amsdu-pps", "RX Retrans AMSDU per sec", "1:8", $glb_mcs_ps_fname, "glb-mcs-rx-rtx-amsdu-ps.png");
  $html .= doTimeGraph("RX-dummy pps", "RX Dummy Packets per sec", "1:9", $glb_mcs_ps_fname, "glb-mcs-rx-dummy-pps.png");
  $html .= doTimeGraph("TX-pps", "TX Packet per sec", "1:10", $glb_mcs_ps_fname, "glb-mcs-tx-ps.png");
  $html .= doTimeGraph("TX-retrans-ps", "TX Retrans per sec", "1:11", $glb_mcs_ps_fname, "glb-mcs-tx-amsdu-ps.png");
  $html .= doTimeGraph("TX-amsdu-pps", "TX AMSDU per sec", "1:12", $glb_mcs_ps_fname, "glb-mcs-tx-amsdu-ps.png");
  $html .= doTimeGraph("TX-retrans-amsdu-pps", "TX Retrans AMSDU per sec", "1:13", $glb_mcs_ps_fname, "glb-mcs-tx-rtx-amsdu-ps.png");
  $html .= doTimeGraph("TX-dummy pps", "TX Dummy Packets per sec", "1:14", $glb_mcs_ps_fname, "glb-mcs-tx-dummy-pps.png");

  # Local peer sending BA back to DUT
  $html .= "\n\n<P>Block-Acks sent from all local endpoints to DUT.<P>\n";
  $html .= doTimeGraph("BA Latency", "Block-Ack latency from last known frame", "1:6", $glb_ba_tx_fname, "glb-ba-tx-latency.png");
  $html .= doTimeGraph("Packets Acked", "Block-Ack packets Acked per Pkt", "1:3", $glb_ba_tx_fname, "glb-ba-tx-pkts-per-ack.png");
  $html .= doTimeGraph("Duplicate Packets Acked", "Block-Ack packets DUP-Acked per Pkt", "1:4", $glb_ba_tx_fname, "glb-ba-tx-pkts-dup-per-ack.png");

  # DUT sending BA to local peer
  $html .= "\n\n<P>Block-Acks sent from DUT to all local endpoints.<P>\n";
  $html .= doTimeGraph("BA Latency", "Block-Ack latency from last known frame", "1:6", $glb_ba_rx_fname, "glb-ba-rx-latency.png");
  $html .= doTimeGraph("Packets Acked", "Block-Ack packets Acked per Pkt", "1:3", $glb_ba_rx_fname, "glb-ba-rx-pkts-per-ack.png");
  $html .= doTimeGraph("Duplicate Packets Acked", "Block-Ack packets DUP-Acked per Pkt", "1:4", $glb_ba_rx_fname, "glb-ba-rx-pkts-dup-per-ack.png");

  return $html;
}

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
	$peer_conn = PeerConn->new(glb_fh_ba_tx => $glb_fh_ba_tx,
				   glb_fh_ba_rx => $glb_fh_ba_rx,
				   report_prefix => $report_prefix,
				   local_addr => $pkt->transmitter(),
				   peer_addr => $pkt->receiver());
      }
      else {
	$peer_conn = PeerConn->new(glb_fh_ba_tx => $glb_fh_ba_tx,
				   glb_fh_ba_rx => $glb_fh_ba_rx,
				   report_prefix => $report_prefix,
				   local_addr => $pkt->receiver(),
				   peer_addr => $pkt->transmitter());
      }
      $peer_conns{$hash} = $peer_conn;
    }
  }

  $peer_conn->add_pkt($pkt);

  # Gather some global stats

  # Add mcs to histogram.

  $tot_pkts++;
  my $dr = $pkt->{datarate};
  if ($pkt->{is_rx}) {
    if (exists $glb_mcs_rx_hash{$dr}) {
      $glb_mcs_rx_hash{$dr}++;
    }
    else {
      $glb_mcs_rx_hash{$dr} = 1;
    }
    $rx_pkts++;
    $rx_amsdu_pkts += $pkt->{amsdu_frame_count};
    if ($pkt->retrans()) {
      $rx_retrans_pkts++;
      $rx_amsdu_retrans_pkts += $pkt->{amsdu_frame_count};
    }
    my $ln = "" . $pkt->timestamp() . "\t" . $pkt->datarate() . "\n";
    print $glb_fh_mcs_rx $ln;
    if ($pkt->retrans()) {
      $ln = "" . $pkt->timestamp() . "\t" . $pkt->retrans() . "\n";
      print $glb_fh_rtx_rx $ln;
    }
  }
  else {
    if (exists $glb_mcs_tx_hash{$dr}) {
      $glb_mcs_tx_hash{$dr}++;
    }
    else {
      $glb_mcs_tx_hash{$dr} = 1;
    }
    $tx_pkts++;
    $tx_amsdu_pkts += $pkt->{amsdu_frame_count};
    if ($pkt->retrans()) {
      $tx_retrans_pkts++;
      $tx_amsdu_retrans_pkts += $pkt->{amsdu_frame_count};
    }
    my $ln = "" . $pkt->timestamp() . "\t" . $pkt->datarate() . "\n";
    print $glb_fh_mcs_tx $ln;
    if ($pkt->retrans()) {
      $ln = "" . $pkt->timestamp() . "\t" . $pkt->retrans() . "\n";
      print $glb_fh_rtx_tx $ln;
    }
  }

  $dummy_rx_pkts += $pkt->{dummy_rx_pkts};
  $dummy_tx_pkts += $pkt->{dummy_tx_pkts};

  my $gen_ps = ($last_ps_timestamp + 1.0) < $pkt->{timestamp};
  if ($gen_ps) {
    my $diff =  $pkt->{timestamp} - $last_ps_timestamp;
    my $period_tot_pkts = $tot_pkts - $last_tot_pkts;
    my $period_rx_pkts = $rx_pkts - $last_rx_pkts;
    my $period_rx_amsdu_pkts = $rx_amsdu_pkts - $last_rx_amsdu_pkts;
    my $period_rx_retrans_pkts = $rx_retrans_pkts - $last_rx_retrans_pkts;
    my $period_rx_retrans_amsdu_pkts = $rx_amsdu_retrans_pkts - $last_rx_amsdu_retrans_pkts;
    my $period_tx_pkts = $tx_pkts - $last_tx_pkts;
    my $period_tx_amsdu_pkts = $tx_amsdu_pkts - $last_tx_amsdu_pkts;
    my $period_tx_retrans_pkts = $tx_retrans_pkts - $last_tx_retrans_pkts;
    my $period_tx_retrans_amsdu_pkts = $tx_amsdu_retrans_pkts - $last_tx_amsdu_retrans_pkts;
    my $period_dummy_rx_pkts = $dummy_rx_pkts - $last_dummy_rx_pkts;
    my $period_dummy_tx_pkts = $dummy_tx_pkts - $last_dummy_tx_pkts;

    my $period_tot_pkts_ps = ($period_tot_pkts + $period_dummy_tx_pkts + $period_dummy_rx_pkts) / $diff;
    my $period_rx_pkts_ps = ($period_rx_pkts + $period_dummy_rx_pkts) / $diff;
    my $period_rx_amsdu_pkts_ps = $period_rx_amsdu_pkts / $diff;
    my $period_rx_retrans_pkts_ps = $period_rx_retrans_pkts / $diff;
    my $period_rx_retrans_amsdu_pkts_ps = $period_rx_retrans_amsdu_pkts / $diff;
    my $period_tx_pkts_ps = ($period_tx_pkts + $period_dummy_tx_pkts) / $diff;
    my $period_tx_amsdu_pkts_ps = $period_tx_amsdu_pkts / $diff;
    my $period_tx_retrans_pkts_ps = $period_tx_retrans_pkts / $diff;
    my $period_tx_retrans_amsdu_pkts_ps = $period_tx_retrans_amsdu_pkts / $diff;
    my $period_dummy_rx_pkts_ps = $period_dummy_rx_pkts / $diff;
    my $period_dummy_tx_pkts_ps = $period_dummy_tx_pkts / $diff;

    $last_ps_timestamp = $pkt->timestamp();
    $last_tot_pkts = $tot_pkts;
    $last_rx_pkts = $rx_pkts;
    $last_rx_amsdu_pkts = $rx_amsdu_pkts;
    $last_rx_retrans_pkts = $rx_retrans_pkts;
    $last_rx_amsdu_retrans_pkts = $rx_amsdu_retrans_pkts;
    $last_tx_pkts = $tx_pkts;
    $last_tx_amsdu_pkts = $tx_amsdu_pkts;
    $last_tx_retrans_pkts = $tx_retrans_pkts;
    $last_tx_amsdu_retrans_pkts = $tx_amsdu_retrans_pkts;
    $last_dummy_rx_pkts = $dummy_rx_pkts;
    $last_dummy_tx_pkts = $dummy_tx_pkts;

    # 'tidno is -1 here, keeping format similar to the per-tid data to make generating reports easier.
    my $ln =  "" . $pkt->timestamp() . "\t-1\t$diff\t$period_tot_pkts_ps\t" .
      "$period_rx_pkts_ps\t$period_rx_retrans_pkts_ps\t$period_rx_amsdu_pkts_ps\t$period_rx_retrans_amsdu_pkts_ps\t$period_dummy_rx_pkts_ps\t" .
      "$period_tx_pkts_ps\t$period_tx_retrans_pkts_ps\t$period_tx_amsdu_pkts_ps\t$period_tx_retrans_amsdu_pkts_ps\t$period_dummy_tx_pkts_ps\n";
    print $glb_fh_mcs_ps $ln;
  }

  $last_pkt = $pkt;

  #print "pkt: rcvr: " . $pkt->receiver() . " transmitter: " . $pkt->transmitter() . "\n";
}
