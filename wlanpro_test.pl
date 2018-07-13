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

use strict;
use Getopt::Long;

my $pld_size = 500;
my $ssid = "wlanpro";
my $psk = "wlanpro_passwd";
my $radio_3a = "wiphy0";
my $radio_3b = "wiphy0";
my $radio_4a = "wiphy1";
my $radio_4b = "wiphy1";
my $sta_max = 40;
my $resource = 2;
my $speed_dl_tot = 1000000000;
my $speed_ul_tot = 1000000000;
my $testcase = -1;
my $manager = "localhost";
my $log_name = "wlanpro_log_" . time() . ".txt";

my $endp_type = "lf_udp";
my $security = "wpa2";
my $upstream_resource = 1;
my $upstream_port = "eth1";
my $multicon = 1;
my $rest_time = 30;
my $quiet = "yes";
my $report_timer = 1000; # 1 second report timer

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
  [--manager {manager-machine IP or hostname}]
  [--testcase {test-case:  -1 all, 0 setup, 1 case 1 ..}]
  [--log_name {log-file-name}]
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
	    'speed_ul_tot=s' => \$speed_ul_tot,
	    'speed_dl_tot=s' => \$speed_dl_tot,
	    'manager=s'      => \$manager,
	    'mgr=s'          => \$manager,
	    'testcase=i'     => \$testcase,
	    'log_name=s'     => \$log_name,
	   ) || (print($usage) && exit(1));

my @radios = ($radio_3a, $radio_3b, $radio_4a, $radio_4b);
my $radio_count = @radios;
my $i;
my $cmd;

# Initial setup for test cases, create 40 stations
my @cxs = ();
my @stations = ();

open(LOGF, ">$log_name") or die("Could not open log file: $log_name $!\n");

# Set radios to 3x3 mode.
if ($testcase == -1 || $testcase == 0) {
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 7";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }
}

for ($i = 0; $i < $sta_max; $i++) {
  my $sta_idx = $i + 100;
  my $radio_idx = $i % $radio_count;
  my $radio = $radios[$radio_idx];
  my $sta_name = "sta$sta_idx";

  @stations = (@stations, $sta_name);

  if ($testcase == -1 || $testcase == 0) {
    $cmd = "./lf_vue_mod.sh --mgr $manager --create_sta --resource $resource --name $sta_name  --radio $radio --security $security --ssid $ssid --passphrase $psk";
    do_cmd($cmd);

    # Set to maximum mode.  The stations might have been
    # previously set to a different mode on an earlier run of this script.
    $cmd = "./lf_portmod.pl  --quiet $quiet --manager $manager --card $resource --port_name $sta_name --wifi_mode 8 --set_speed DEFAULT";
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

stop_all_my_cx();

if ($testcase == -1 || $testcase == 1) {
  wait_for_stations();
  do_test_series();
}

if ($testcase == -1 || $testcase == 2) {
  # Test case 2, set stations to 2x2 and re-test
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 4";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

  wait_for_stations();
  do_test_series();
}

if ($testcase == -1 || $testcase == 3) {
  # Test case 3, set stations to 1x1 and re-test
  for ($i = 0; $i<$radio_count; $i++) {
    my $radio = $radios[$i];
    my $set_cmd = "set_wifi_radio 1 $resource $radio NA NA NA NA NA NA NA NA NA 1";
    $cmd = "./lf_firemod.pl --mgr $manager --action do_cmd --cmd \"$set_cmd\"";
    do_cmd($cmd);
  }

  wait_for_stations();
  do_test_series();
}


# Mixed mode test:  10 3x3, 15 2x2, 15 1x1  (Same data pattern)
if ($testcase == -1 || $testcase == 4 || $testcase == 5) {
  # Set radio back to full antenna capacity
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

  if ($testcase == -1 || $testcase == 4) {
    wait_for_stations();
    do_test_series();
  }
}

if ($testcase == -1 || $testcase == 5) {
  wait_for_stations();
  do_test_series();
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

exit 0;

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

  logp("Waiting $sleep_sec seconds for test to run, $cx_cnt connections, configured speed, UL: $speed_ul  DL: $speed_dl....\n\n");
  sleep($sleep_sec);

  logp("Gathering stats for this test run...\n");

  # Gather stats data
  my $sp;
  for ($i = 0; $i<$cx_cnt; $i++) {
    my $cxn = $cxs[$i];
    $sp = `./lf_portmod.pl --manager $manager --cli_cmd "show_cxe $cxn"`;
    logf("$sp\n");
  }

  # Station stats
  for ($i = 0; $i<@stations; $i++) {
    my $sta_name = $stations[$i];
    $sp = `./lf_portmod.pl --manager $manager --cli_cmd "show_port 1 $resource $sta_name"`;
    logf("$sp\n");
  }

  # Radio stats
  for ($i = 0; $i<@radios; $i++) {
    my $name = $radios[$i];
    $sp = `./lf_portmod.pl --manager $manager --cli_cmd "show_port 1 $resource $name"`;
    logf("$sp\n");
  }

  # Upstream port
  $sp = `./lf_portmod.pl --manager $manager --cli_cmd "show_port 1 $upstream_resource $upstream_port"`;
  logf("$sp\n");

  # TODO: Gather specific stats?

  stop_all_my_cx();
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

sub do_test_series {
  # First test case, 20 stations downloading, 3x3 mode.
  logp("\nDoing download test with 20 stations.\n");
  do_one_test(0, $speed_dl_tot / 20, 20, 30);
  # Upload 30 sec
  logp("\nDoing upload test with 20 stations.\n");
  do_one_test($speed_ul_tot / 20, 0, 20, 30);
  # Upload/Download 1 minute sec
  logp("\nDoing upload/download test with 40 stations.\n");
  do_one_test($speed_ul_tot / 40, $speed_dl_tot / 40, 40, 60);

  logp("Sleeping $rest_time seconds at end of test series...\n\n");
  sleep($rest_time);
}

sub do_cmd {
  my $cmd = shift;
  logp("$cmd\n");
  return system($cmd);
}
