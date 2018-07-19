#!/usr/bin/perl -w
#
# Data should be 500 bytes
# Test rig is one upstream wired system, which will be the manager as well as resource
# One ct523b as resource2, and a stand-by ct523b as resource3
# WPA2 PSK encryption

# 3x3 client testing:
# 20 clients uploading for 30 sec
# 20 clients downloading 30 sec
# 40 clients upload + download 1 minute
# Quiesce and wait 30 seconds

# 2x2:  Same
# 1x2:  Same

# Mixed mode:  10 3x3, 15 2x2, 15 1x1  (Same data pattern)

# Mixed With interference: Same as mixed mode
# Assume other test EQ is doing interference?

# Each ct523b has 4 radios.  We will spread stations among them.
# This script can work on systems with fewer radios as well, see comments
# below about naming the 3a,3b,4a,4b radios with duplicate names.

use strict;
use Getopt::Long;

my $pld_size = 500;
my $ssid = "wlanpro";
my $psk = "wlanpro_passwd";
# Default radio setup for 523b with 2ac, 2ac2.
# For something like a 522 with 2 radios, set 3a, 3b to wiphy0, and
# 4a 4b to wiphy1.
my $radio_3a = "wiphy0";
my $radio_3b = "wiphy1";
my $radio_4a = "wiphy2";
my $radio_4b = "wiphy3";
my $sta_max = 40; # For upload/download tests
my $wct_sta_max = 64; # For wifi-capacity-test on single radio (4a)
my $gui_host = "127.0.0.1";
my $gui_port = 7777;
my $resource = 2;
my $speed_dl_tot = 1000000000;
my $speed_ul_tot = 1000000000;
my $testcase = -1;
my $manager = "localhost";
my $log_name = "";

my $endp_type = "lf_udp";
my $security = "wpa2";
my $upstream_resource = 1;
my $upstream_port = "eth1";
my $multicon = 1;
my $rest_time = 20;
my $quiet = "yes";
my $report_timer = 1000; # 1 second report timer
my $one_way_test_time = 30;
my $bi_test_time = 30;

my $usage = "$0
  [--pld_size { bytes } ]
  [--ssid {ssid}]
  [--passphrase {password}]
  [--3a {wiphy-radio-3x3-a}]
  [--3b {wiphy-radio-3x3-b}]
  [--4a {wiphy-radio-4x4-a}]
  [--4b {wiphy-radio-4x4-b}]
  [--resource {resource-number}]
  [--upstream_resource {resource-number}]
  [--upstream_port {port}]
  [--speed_ul_tot {speed-bps}]
  [--speed_dl_tot {speed-bps}]
  [--security {open | wpa2}]
  [--manager {manager-machine IP or hostname}]
  [--testcase {test-case:  -1 all, 0 setup, 1-5, 100 means cleanup}]
  [--log_name {log-file-name}]
  [--rest_time {seconds to sleep between rest runs, dfault is $rest_time}]
  [--gui_host  {LANforge gui_host (127.0.0.1)}]
  [--gui_port  {LANforge gui_port (7777)}]
";


GetOptions (
	    'pld_size=i'     => \$pld_size,
	    'ssid=s'         => \$ssid,
	    'passphrase=s'   => \$psk,
	    '3a=s'           => \$radio_3a,
	    '3b=s'           => \$radio_3b,
	    '4a=s'           => \$radio_4a,
	    '4b=s'           => \$radio_4b,
	    'resource=i'     => \$resource,
	    'upstream_resource=i' => \$upstream_resource,
	    'upstream_port=s' => \$upstream_port,
	    'rest_time=i'    => \$rest_time,
	    'speed_ul_tot=s' => \$speed_ul_tot,
	    'speed_dl_tot=s' => \$speed_dl_tot,
	    'security=s'     => \$security,
	    'manager=s'      => \$manager,
	    'mgr=s'          => \$manager,
	    'testcase=i'     => \$testcase,
	    'log_name=s'     => \$log_name,
	    'gui_host=s'     => \$gui_host,
	    'gui_port=i'     => \$gui_port,
	   ) || (print($usage) && exit(1));

if ($log_name eq "") {
  $log_name = "wlanpro_log_" . $ssid . "_" . time() . ".txt";
}
my @radios = ($radio_3a, $radio_3b, $radio_4a, $radio_4b);
my $radio_count = @radios;
my $i;
my $cmd;
my $log_prefix = "LANforge wlanpro-test\nConfiguration:\n" .
  "  SSID: $ssid  passphrase: $psk  security: $security  resource: $resource\n" .
  "  speed_dl_request: $speed_dl_tot  speed_ul_request: $speed_ul_tot  payload-size: $pld_size  traffic-type: $endp_type\n" .
  "  Test started at: " . `date` . "\n\n";
my $brief_log = "$log_prefix";
my $summary_text = "$log_prefix";
my $mini_summary_text = "$log_prefix";

# Initial setup for test cases, create 40 stations
my @cxs = ();
my @stations = ();
my @stations4a = ();
my $sta_on_4a = 0;

open(LOGF, ">$log_name") or die("Could not open log file: $log_name $!\n");

logp($log_prefix);

# Stop any running tests.
stop_all_cx();

# Set radios to 3x3 mode.
if ($testcase == -1 || $testcase == 0) {
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 7";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }
}

# Find wlanX for 4a radio.
if ($radio_4a =~ /\S+(\d+)/) {
  my $sta_name = "wlan$1";
  @stations4a = (@stations4a, $sta_name);
  my $radio = $radio_4a;
  $sta_on_4a++;
  if ($testcase == -1 || $testcase == 0 || $testcase == 6) {
    $cmd = "./lf_vue_mod.sh --mgr $manager --create_sta --resource $resource --name $sta_name  --radio $radio --security $security --ssid $ssid --passphrase $psk";
    do_cmd($cmd);

    # Set to maximum mode.  The stations might have been
    # previously set to a different mode on an earlier run of this script.
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed DEFAULT --set_ifstate up";
    do_cmd($cmd);
  }
}

for ($i = 0; $i < $sta_max; $i++) {
  my $sta_idx = $i + 100;
  my $radio_idx = $i % $radio_count;
  my $radio = $radios[$radio_idx];
  my $sta_name = "sta$sta_idx";

  if ($radio eq $radio_4a) {
    $sta_on_4a++;
    @stations4a = (@stations4a, $sta_name);
  }

  @stations = (@stations, $sta_name);

  if ($testcase == -1 || $testcase == 0) {
    $cmd = "./lf_vue_mod.sh --mgr $manager --create_sta --resource $resource --name $sta_name  --radio $radio --security $security --ssid $ssid --passphrase $psk";
    do_cmd($cmd);

    # Set to maximum mode.  The stations might have been
    # previously set to a different mode on an earlier run of this script.
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed DEFAULT --set_ifstate up";
    do_cmd($cmd);
  }
  # Create data connection
  my $cxn = "l3-${sta_name}";
  my $endpa = "$cxn-A";
  my $endpb = "$cxn-B";
  my $pkt_sz ="--min_pkt_sz $pld_size --max_pkt_sz $pld_size";
  my $gen_args = "--mgr $manager --multicon $multicon $pkt_sz --endp_type $endp_type --action create_endp --report_timer $report_timer";

  if ($testcase == -1 || $testcase == 0) {
    $cmd = "./lf_firemod.pl --resource $resource $gen_args --endp_name $endpa --speed 0 --port_name $sta_name";
    do_cmd($cmd);

    $cmd = "./lf_firemod.pl --resource $upstream_resource $gen_args --endp_name $endpb --speed 0 --port_name $upstream_port";
    do_cmd($cmd);

    $cmd = "./lf_firemod.pl --mgr $manager --action create_cx --cx_name $cxn --cx_endps $endpa,$endpb --report_timer $report_timer";
    do_cmd($cmd);
  }

  @cxs = (@cxs, $cxn);
}

# Create rest of the 4a-stations for Wifi Capacity Test
while ($sta_on_4a < $wct_sta_max) {
  my $sta_idx = $sta_on_4a + 200;
  my $radio = $radio_4a;
  my $sta_name = "sta$sta_idx";

  @stations4a = (@stations4a, $sta_name);
  $sta_on_4a++;

  if ($testcase == -1 || $testcase == 0 || $testcase == 6) {
    $cmd = "./lf_vue_mod.sh --mgr $manager --create_sta --resource $resource --name $sta_name  --radio $radio --security $security --ssid $ssid --passphrase $psk";
    do_cmd($cmd);

    # Set to maximum mode.  The stations might have been
    # previously set to a different mode on an earlier run of this script.
    # Set them to admin-down, the wifi-capacity-test will bring them up as needed.
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed DEFAULT --set_ifstate down";
    do_cmd($cmd);
  }
}

stop_all_cx();


if ($testcase == -1 || $testcase == 1) {
  wait_for_stations();
  do_test_series("3x3 station upload/download test");
}

if ($testcase == -1 || $testcase == 2) {
  # Test case 2, set stations to 2x2 and re-test
  my $start = time();
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 4";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

  wait_for_stations();
  check_more_rest($testcase, $start);
  do_test_series("2x2 station upload/download test");
}

if ($testcase == -1 || $testcase == 3) {
  # Test case 3, set stations to 1x1 and re-test
  my $start = time();
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 1";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

  wait_for_stations();
  check_more_rest($testcase, $start);
  do_test_series("1x1 station upload/download test");
}


# Mixed mode test:  10 3x3, 15 2x2, 15 1x1  (Same data pattern)
if ($testcase == -1 || $testcase == 4 || $testcase == 5) {
  # Set radio back to full antenna capacity
  my $start = time();
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 0";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

  for ($i = 0; $i<10; $i++) {
    my $sta_name = $stations[$i];
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed \"v-3 Streams /AC\"";
    do_cmd($cmd);
  }
  for ($i = 10; $i<25; $i++) {
    my $sta_name = $stations[$i];
    $cmd = "./lf_portmod.pl --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed \"v-2 Streams /AC\"";
    do_cmd($cmd);
  }
  for ($i = 25;$ i<40; $i++) {
    my $sta_name = $stations[$i];
    $cmd = "./lf_portmod.pl --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed \"v-1 Stream /AC\"";
    do_cmd($cmd);
  }

  wait_for_stations();
  check_more_rest($testcase, $start);

  if ($testcase == -1 || $testcase == 4) {
    do_test_series("Mixed mode: 10 3x3, 15 2x2, 10 1x1 station upload/download test");
    if ($testcase == -1) {
      sleep($rest_time);
    }
  }
}

# Disable this from 'all' runs for now until we figure out how the interference is going to be generated.
if ($testcase == 5) {
  wait_for_stations();
  do_test_series("Mixed mode: 10 3x3, 15 2x2, 10 1x1 station upload/download test with interference");
}

# WiFi capacity test
if ($testcase == -1 || $testcase == 6) {

  for ($i = 0; $i < @stations; $i++) {
    my $sta_name = $stations[$i];
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed DEFAULT --set_ifstate down";
    do_cmd($cmd);
  }

  #wait_for_stations();  WCT takes care of bringing stations up/down
  my $sta_list = join(",", @stations4a);
  # Call to automated wifi capacity test plugin
  do_cmd("./lf_auto_wifi_cap.pl --mgr $manager --resource $resource --radio $radio_4a --speed_dl $speed_dl_tot --ssid $ssid --num_sta $wct_sta_max --upstream $upstream_port --upstream_resource $upstream_resource --percent_tcp 50 --increment 1,5,10,20,30,45,64 --duration 15 --endp_type mix --test_name wlanpro-$ssid --test_text 'Wlan-Pro test case #6 to ssid $ssid' --multicon 1 --use_existing_sta --use_existing_cfg --use_station $sta_list --gui_host $gui_host --gui_port $gui_port");
}

if ($testcase == 100) {
  # Cleanup
  for ($i = 0; $i<@stations; $i++) {
    my $sta_name = $stations[$i];
    $cmd = "./lf_portmod.pl  --quiet $quiet --mgr $manager --resource $resource --cmd delete --port_name $sta_name";
    do_cmd("$cmd\n");
  }

  for ($i = 0; $i<@cxs; $i++) {
    my $cxn = $cxs[$i];
    $cmd = "./lf_firemod.pl --mgr $manager --action delete_cxe --cx_name $cxn";
    do_cmd($cmd);
  }

  # Set radio back to full antenna capacity
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 0";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

}

logpb("Completed test at " . `date` . "\n\n");

# Append brief log and final log to the report.

logf($brief_log);
logp($summary_text);
logp("\n\n$mini_summary_text");

exit 0;

sub check_more_rest {
  my $testcase = shift;
  my $start = shift;

  if ($testcase == -1) {
    # Running tests in series, so we need to add in our rest time
    my $now = time();
    if ($start + $rest_time > $now) {
      my $st = ($start + $rest_time) - $now;
      print "Sleeping $st seconds for rest time...";
      sleep($st);
    }
  }
}

# Wait until all stations are associated and have IP addresses.
sub wait_for_stations {
  # Wait until stations are associated, return count
  my $j;
  for ($j = 0; $j<60; $j++) {
    my $all_up = 1;
    for ($i = 0; $i<@stations; $i++) {
      my $sta_name = $stations[$i];
      $cmd = "./lf_portmod.pl  --quiet $quiet --mgr $manager --resource $resource --show_port AP,IP --port_name $sta_name";
      logp("$cmd\n");
      my @output = `$cmd`;
      if ($output[0] =~ "AP: Not-Associated") {
	logp("Station $sta_name is not associated, waiting...\n");
	sleep(1);
	$all_up = 0;
	last;
      }
      if ($output[1] =~ "IP: 0.0.0.0") {
	logp("Station $sta_name does not have an IP address, waiting...\n");
	sleep(1);
	$all_up = 0;
	last;
      }
    }

    if ($all_up) {
      last;
    }
  }
}

sub do_one_test {
  my $speed_ul = shift;
  my $speed_dl = shift;
  my $cx_cnt = shift;
  my $sleep_sec = shift;
  my $series_desc = shift;

  # Download for X seconds
  for ($i = 0; $i<$cx_cnt; $i++) {
    my $cxn = $cxs[$i];
    my $endpa = "$cxn-A";
    my $endpb = "$cxn-B";

    $cmd = "./lf_firemod.pl --mgr $manager --action set_endp --endp_name $endpa --speed $speed_ul";
    do_cmd($cmd);

    $cmd = "./lf_firemod.pl --mgr $manager --action set_endp --endp_name $endpb --speed $speed_dl";
    do_cmd($cmd);

    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"set_cx_state default_tm $cxn RUNNING\"";
    do_cmd($cmd);
  }

  $cmd =  "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"clear_port_counters\"";
  do_cmd($cmd);

  my $msg = "Waiting $sleep_sec seconds for test to run, $cx_cnt connections, requested per-connection speed, UL: $speed_ul  DL: $speed_dl.\n" .
    " Test-case: $series_desc\n\n";
  logp($msg);
  $mini_summary_text .= "$cx_cnt connections, requested per-connection speed, UL: $speed_ul  DL: $speed_dl\n";

  sleep($sleep_sec);

  logp("Gathering stats for this test run...\n");

  # Gather layer-3 stats data
  my $sp;

  my $tmpfe = "wptest_endp_stats_tmp.txt";
  `./lf_portmod.pl --manager $manager --cli_cmd "nc_show_endp" > $tmpfe`;

  my $tmpf = "wptest_stats_tmp.txt";
  `./lf_portmod.pl --manager $manager --cli_cmd "nc_show_port 1 $resource" > $tmpf`;
  if ($resource != $upstream_resource) {
    `./lf_portmod.pl --manager $manager --cli_cmd "nc_show_port 1 $upstream_resource" >> $tmpf`;
  }

  # Stop the connections while we process stats.
  stop_all_cx();

  logp("Processing stats for this test run...\n");

  # Process stats
  $sp = `cat $tmpfe`;
  logf("$sp\n");

  my $tot_dl_bps = 0;
  my $tot_ul_bps = 0;
  # Our endp names are derived from cx, so use that to our advantage.
  for ($i = 0; $i<$cx_cnt; $i++) {
    my $cxn = $cxs[$i];
    my $epa = "$cxn-A";
    my $epb = "$cxn-B";

    my $ep_stats = `./lf_firemod.pl --endp_name $epa --stats_from_file $tmpfe --endp_vals RealRxRate,RealTxRate`;
    $brief_log .= "Endpoint Stats for $epa:\n$ep_stats\n\n";
    $summary_text .= "$cxn:";
    if ($ep_stats =~ /RealRxRate:\s+(\d+)/) {
      $tot_dl_bps += $1;
      $summary_text .= sprintf(" Download RX: %.3fMbps", $1 / 1000000);
    }
    if ($ep_stats =~ /RealTxRate:\s+(\d+)/) {
      $summary_text .= sprintf(" Upload TX: %.3fMbps", $1 / 1000000);
    }
    $ep_stats = `./lf_firemod.pl --endp_name $epb --stats_from_file $tmpfe --endp_vals RealRxRate,RealTxRate`;
    $brief_log .= "Endpoint Stats for $epb:\n$ep_stats\n\n";
    if ($ep_stats =~ /RealRxRate:\s+(\d+)/) {
      $tot_ul_bps += $1;
      $summary_text .= sprintf(" Upload RX: %.3fMbps", $1 / 1000000);
    }
    if ($ep_stats =~ /RealTxRate:\s+(\d+)/) {
      $summary_text .= sprintf(" Download TX: %.3fMbps", $1 / 1000000);
    }
    $summary_text .= "\n";
  }
  $summary_text .= sprintf("Total Endpoint Upload RX: %.3fMbps  Download RX: %.3fMbps\n\n", $tot_ul_bps / 1000000, $tot_dl_bps / 1000000);
  $mini_summary_text .= sprintf("Total Endpoint Upload RX: %.3fMbps  Download RX: %.3fMbps\n\n", $tot_ul_bps / 1000000, $tot_dl_bps / 1000000);

  # Port
  $sp = `cat $tmpf`;
  logf("$sp\n");

  $tot_dl_bps = 0;
  $tot_ul_bps = 0;
  for ($i = 0; $i<@stations; $i++) {
    my $sta_name = $stations[$i];
    my $sta_stats = `./lf_portmod.pl --card $resource --port_name $sta_name --stats_from_file $tmpf --show_port AP,ESSID,bps_rx,bps_tx,MAC,Mode,RX-Rate,TX-Rate,Signal,Link-Activity,Channel,Bandwidth,NSS`;
    $brief_log .= "Station Stats:\n$sta_stats\n\n";
    $summary_text .= "$sta_name:";
    if ($sta_stats =~ /bps_rx:\s+(\d+)/) {
      $tot_dl_bps += $1;
      $summary_text .= sprintf(" RX: %.3fMbps", $1 / 1000000);
    }
    if ($sta_stats =~ /bps_tx:\s+(\d+)/) {
      $tot_ul_bps += $1;
      $summary_text .= sprintf(" TX: %.3fMbps", $1 / 1000000);
    }
    if ($sta_stats =~ /NSS:\s+(\d+)/) {
      $summary_text .= " NSS: $1";
    }
    if ($sta_stats =~ /RX-Rate:\s+(\S+)/) {
      $summary_text .= " RX-Rate: $1";
    }
    if ($sta_stats =~ /TX-Rate:\s+(\S+)/) {
      $summary_text .= " TX-Rate: $1";
    }
    if ($sta_stats =~ /Signal:\s+(\S+)/) {
      $summary_text .= " Signal: $1";
    }
    $summary_text .= "\n";
  }
  $summary_text .= sprintf("Total station TX: %.3fMbps  RX: %.3fMbps\n\n", $tot_ul_bps / 1000000, $tot_dl_bps / 1000000);

  # Radio stats
  $tot_dl_bps = 0;
  $tot_ul_bps = 0;
  my @rep_ports = uniq(@radios);
  for ($i = 0; $i<@rep_ports; $i++) {
    my $sta_name = $rep_ports[$i];
    my $sta_stats = `./lf_portmod.pl --card $resource --port_name $sta_name --stats_from_file $tmpf --show_port bps_rx,bps_tx,MAC,Mode,NSS`;
    $brief_log .= "Radio Stats for $sta_name:\n$sta_stats\n\n";
    $summary_text .= "$sta_name:";
    if ($sta_stats =~ /bps_rx:\s+(\d+)/) {
      $tot_dl_bps += $1;
      $summary_text .= sprintf(" RX: %.3fMbps", $1 / 1000000);
    }
    if ($sta_stats =~ /bps_tx:\s+(\d+)/) {
      $tot_ul_bps += $1;
      $summary_text .= sprintf(" TX: %.3fMbps", $1 / 1000000);
    }
    if ($sta_stats =~ /Mode:\s+(\S+)/) {
      $summary_text .= " Mode: $1";
    }
    $summary_text .= "\n";
  }
  $summary_text .= sprintf("Total Radio TX: %.3fMbps  RX: %.3fMbps\n\n", $tot_ul_bps / 1000000, $tot_dl_bps / 1000000);

  # Upstream port
  my $p_stats = `./lf_portmod.pl --card $upstream_resource --port_name $upstream_port --stats_from_file $tmpf --show_port bps_rx,bps_tx,MAC,RX-Rate,TX-Rate`;
  $brief_log .= "Upstream Port Stats:\n$p_stats\n\n";
  $summary_text .= "$upstream_port:";
  if ($p_stats =~ /bps_rx:\s+(\d+)/) {
    $tot_dl_bps += $1;
    $summary_text .= sprintf(" RX: %.3fMbps", $1 / 1000000);
  }
  if ($p_stats =~ /bps_tx:\s+(\d+)/) {
    $tot_ul_bps += $1;
    $summary_text .= sprintf(" TX: %.3fMbps", $1 / 1000000);
  }
  if ($p_stats =~ /RX-Rate:\s+(\S+)/) {
    $summary_text .= " RX-Rate: $1";
  }
  if ($p_stats =~ /TX-Rate:\s+(\S+)/) {
    $summary_text .= " TX-Rate: $1";
  }
  $summary_text .= "\n";
}

sub stop_all_cx {
  $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"set_cx_state all all STOPPED\"";
  do_cmd($cmd);
}

sub stop_all_my_cx {
  my $i;

  for ($i = 0; $i<@cxs; $i++) {
    my $cxn = $cxs[$i];
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"set_cx_state default_tm $cxn STOPPED\"";
    do_cmd($cmd);
  }
}

sub logf {
  my $text = shift;
  print LOGF $text;
}

sub logp {
  my $text = shift;
  print LOGF $text;
  print $text; # to std-out too
}

sub logpb {
  my $text = shift;
  print LOGF $text;
  print $text; # to std-out too
  $brief_log .= "$text";
  $summary_text .= "$text"; # Even sparser summary output
}

sub do_test_series {
  my $desc = shift;
  my $msg = "\n" . `date` . "Doing test series: $desc\n";
  logpb($msg);
  $mini_summary_text .= $msg;

  # First test case, 20 stations downloading, 3x3 mode.
  logpb("\nDoing download test with 20 stations.\n");
  do_one_test(0, $speed_dl_tot / 20, 20, $one_way_test_time, $desc);
  # Upload 30 sec
  logpb("\nDoing upload test with 20 stations.\n");
  do_one_test($speed_ul_tot / 20, 0, 20, $one_way_test_time, $desc);
  # Upload/Download 1 minute sec
  logpb("\nDoing upload/download test with 40 stations.\n");
  do_one_test($speed_ul_tot / 40, $speed_dl_tot / 40, 40, $bi_test_time, $desc);
}

sub do_cmd {
  my $cmd = shift;
  logp("$cmd\n");
  return system($cmd);
}

sub uniq {
  my %seen;
  grep !$seen{$_}++, @_;
}

my @array = qw(one two three two three);
my @filtered = uniq(@array);
