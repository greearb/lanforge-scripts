#!/usr/bin/perl -w

# This program is used to create, show, and modify existing connections
# and get some basic information from LANforge.
# (C) 2020 Candela Technologies Inc.
#
#

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;

# use lib prepends to @INC, so put lower priority first
# This is before run-time, so cannot condition this with normal 'if' logic.
use lib '/home/lanforge/scripts';
use lib "./";

use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils;
use Net::Telnet ();
use Getopt::Long;

our $NA        = 'NA';
our $NL        = "\n";
our $shelf_num = 1;

# Default values for ye ole cmd-line args.
our $resource         = 1;
our $quiet            = "yes";
our $endp_name        = "";
our $endp_cmd         = "";
our $port_name        = "";
our $speed            = "-1";
our $action           = "";
our $do_cmd           = "NA";
our $lfmgr_host       = "localhost";
our $lfmgr_port       = 4001;
our $endp_vals        = undef;
our $ip_port          = "-1"; # let lf choose
our $multicon         = "0"; #no multicon

# For creating multicast endpoints
our $endp_type        = undef; #"mc_udp"; this needs to be explicit
our $mcast_addr       = "224.9.9.9";
our $mcast_port       = "9999";
our $max_speed        = "-1";
our $rcv_mcast        = "YES";
our $min_pkt_sz       = "-1";
our $max_pkt_sz       = "-1";
our $use_csums        = "NO";  # Use LANforge checksums in payload?
our $ttl              = 32;
our $report_timer     = 5000;
our $tos              = "";
our $lat1             = "";
our $lat2             = "";
our $arm_pps          = "";
our $arm_cpu_id       = "NA";
# For cross connects
our $cx_name          = "";
our $cx_endps         = "";
our $list_cx_name     = "all";
our $test_mgr         = "default_tm";
our $list_test_mgr    = "all";
our $stats_from_file  = "";

our $fail_msg         = "";
our $manual_check     = 0;

our @known_endp_types = qw(generic lf_tcp lf_tcp6 lf_udp lf_udp6 mc_udp mc_udp6);
our @known_tos        = qw(DONT-SET LOWCOST LOWDELAY  RELIABILITY THROUGHPUT BK BE VI VO);

########################################################################
# Nothing to configure below here, most likely.
########################################################################

my $endp_type_str = join(' | ', @::known_endp_types);
my $tos_str = join(' | ', @::known_tos);

our $usage = <<"__EndOfUsage__";
$0 [ --action {
     create_cx | create_endp  | create_arm   |
     delete_cx | delete_cxe   | delete_endp  | do_cmd    |
     list_cx   | list_endp    | list_ports   |
     set_endp  | show_cx      | show_endp    | show_port |
     start_cx  | start_endp   | stop_cx      | stop_endp
  } ]
  [--arm_pps      {packets per second}]
  [--cmd          {lf-cli-command text}]
  [--cx_name      {connection name}]
  [--cx_endps     {endp1},{endp2}]
  [--endp_cmd     {generic-endp-command}]
  [--endp_name    {name}]
  [--endp_type    { $endp_type_str }]
  [--endp_vals {key,key,key,key}]
      # show_endp output can be narrowed with key-value arguments
      # Examples:
      #  --action show_endp --endp_vals MinTxRate,DestMAC,Avg-Jitter
      # Not available: Latency,Pkt-Gaps, or rows below steps-failed.
      # Special Keys:
      #  --endp_vals tx_bytes         (Tx Bytes)
      #  --endp_vals rx_bytes         (Rx Bytes)
  [--ip_port      {-1 (let LF choose, AUTO) | 0 (let OS choose, ANY) | specific IP port}]
  [--max_pkt_sz   {maximum payload size in bytes}]
  [--max_speed    {speed in bps}]
  [--min_pkt_sz   {minimum payload size in bytes}]
  [--mcast_addr   {multicast address, for example: 224.4.5.6}]
  [--mcast_port   {multicast port number}]
  [--mgr          {host-name | IP}]
  [--mgr_port     {ip port}]
  [--multicon     {0 (no multi-conn, Normal) | number of connections (TCP only)}]
  [--port_name    {name}]
  [--quiet        { yes | no }]
  [--rcv_mcast    {yes (receiver) | no (transmitter)}]
  [--report_timer {miliseconds}]
  [--resource     {number}]
  [--speed        {speed in bps}]
  [--stats_from_file {file-name}]
      # Read 'show-endp' ouput from a file instead of direct query from LANforge.
      # This can save a lot of time if we already have the output available.
  [--tos          { $tos_str },{priority}]
  [--use_csums    {yes | no, should we checksum the payload}]
  [--use_ports    {port-A,port-B}     # Example: 1.1.eth1,1.2.sta0
      # notation is <shelf>.<resource>.<port-name>
      # if this option is present, you can skip the create_endp action
  [--use_speeds   {speed-A,speed-B}    # Example: 54000,1000000
      # if this option is present, you can skip the create_endp action
  [--log_cli      {1|filename}]
  [--test_mgr     {default_tm|all|other-tm-name}]
  [--ttl          {time-to-live}]

Example:
 $0 --action set_endp --endp_name udp1-A --speed 154000

 $0 --action normalize_latency --lat1 "latency-buckets info for endpA" --lat2 "latency-buckets-info for endpB"

 $0 --action create_endp --endp_name mcast_xmit_1 --speed 154000 \\
   --endp_type mc_udp   --mcast_addr 224.9.9.8    --mcast_port 9998 \\
   --rcv_mcast NO       --port_name eth1 \\
   --min_pkt_sz 1072    --max_pkt_sz 1472 \\
   --use_csums NO       --ttl 32 \\
   --quiet no --report_timer 1000

 $0 --action create_endp --endp_name bc1 --speed 256000 \\
   --endp_type lf_tcp   --tos THROUGHPUT,100 --port_name rd0#1

 $0 --action create_endp --endp_name ping1 --port_name sta0 --endp_cmd \"lfping -p deadbeef000 -I sta0 8.8.4.4\"
   --endp_type generic

 $0 --action list_cx --test_mgr all --cx_name all

 # Unlikely example of creating a CX from differently named endpoints:
 $0 --action create_cx --cx_name L301 \\
   --cx_endps ep_rd0a,ep_rd1a --report_timer 1000

   # Or, skip explicit endpoint creation with the using-ports feature:
 $0 --action create_cx --cx_name banana \\
   --use_ports sta0,eth1 --use_speeds 15000,10000000 --report_timer 1200

 Example of creating an Armageddon connection:
 $0 --action create_arm --endp_name arm01-A --port_name eth1 \\
   --arm_pps 80000 --min_pkt_sz 1472 --max_pkt_sz 1514 --tos LOWDELAY,100

 $0 --mgr jedtest --action create_cx --cx_name arm-01 --cx_endps arm01-A,arm01-B

 Example of creating endpoints and joining them:
 $0 --mgr localhost --action create_endp --endp_name test1a --speed 10000000 \\
   --endp_type lf_tcp --port_name eth5 --ip_port 0 --multicon 10

 $0 --mgr localhost --resource 3 --action create_endp --endp_name test1b --speed 0 \\
   --endp_type lf_tcp --port_name wlan2 --multicon 1

 $0 --mgr localhost --action create_cx --cx_name test1 --cx_endps test1a,test1b

 $0 -m vm-48e4 -p 4001 --action create_cx --cx_name testo --endp_type tcp \\
   --use_ports r0b,r1b --use_speeds 9600,9600 --report_timer 250
__EndOfUsage__

my $i = 0;
my $cmd;

my $log_cli = "unset"; # use ENV{LOG_CLI} elsewhere
my $show_help = 0;
our $use_ports_str = "NA";
our $use_speeds_str = "NA";
our $use_max_speeds = "NA";
our @use_ports = ();
our @use_speeds = ();

if (@ARGV < 2) {
   print $usage;
   exit 0;
}

our $debug = 0;

GetOptions
(
   'action|a=s'         => \$::action,
   'arm_pps=i'          => \$::arm_pps,
   'cmd|c=s'            => \$::do_cmd,
   'cx_endps=s'         => \$::cx_endps,
   'cx_name=s'          => \$::cx_name,
   'debug|d'            => \$::debug,
   'help|h'             => \$show_help,
   'ip_port=i'          => \$::ip_port,
   'endp_cmd=s'         => \$::endp_cmd,
   'endp_name|e=s'      => \$::endp_name,
   'endp_type=s'        => \$::endp_type,
   'endp_vals|o=s'      => \$::endp_vals,
   'log_cli=s{0,1}'     => \$log_cli,
   'manager|mgr|m=s'    => \$::lfmgr_host,
   'max_speed=s'        => \$::speed,
   'min_pkt_sz=s'       => \$::min_pkt_sz,
   'max_pkt_sz=s'       => \$::max_pkt_sz,
   'mcast_addr=s'       => \$::mcast_addr,
   'mcast_port=s'       => \$::mcast_port,
   'lfmgr_port|mgr_port|port|p=i' => \$::lfmgr_port,
   'multicon=i'         => \$::multicon,
   'port_name=s'        => \$::port_name,
   'quiet|q=s'          => \$::quiet,
   'rcv_mcast=s'        => \$::rcv_mcast,
   'report_timer=i'     => \$::report_timer,
   'resource|r=i'       => \$::resource,
   'speed|s=i'          => \$::speed,
   'stats_from_file=s'  => \$::stats_from_file,
   'ttl=i'              => \$::ttl,
   'use_csums=s'        => \$::use_csums,
   'use_ports=s'        => \$::use_ports_str,
   'use_speeds=s'       => \$::use_speeds_str,
   'use_max_speeds=s'   => \$::use_max_speeds,
   'test_mgr=s'         => \$::test_mgr,
   'tos=s'              => \$::tos,
   'lat1=s'             => \$::lat1,
   'lat2=s'             => \$::lat2,

) || die("$::usage");

if ($show_help) {
   print $usage;
   exit 0;
}

# Convert some TOS values that the server likely doesn't understand.
if ($tos eq "BK") {
  $tos = 64;
}
elsif ($tos eq "BE") {
  $tos = 96;
}
elsif ($tos eq "VI") {
  $tos = 128;
}
elsif ($tos eq "VO") {
  $tos = 192;
}

if (defined $ENV{DEBUG}) {
  use Data::Dumper;
}

if ($::debug) {
  use Data::Dumper;
  $ENV{DEBUG} = 1 if (!(defined $ENV{DEBUG}));
}

if ($::quiet eq "0") {
  $::quiet = "no";
}
elsif ($::quiet eq "1") {
  $::quiet = "yes";
}

if (defined $log_cli) {
  if ($log_cli ne "unset") {
    # here is how we reset the variable if it was used as a flag
    if ($log_cli eq "") {
      $ENV{'LOG_CLI'} = 1;
    }
    else {
      $ENV{'LOG_CLI'} = $log_cli;
    }
  }
}

if ($::do_cmd ne "NA") {
  $::action = "do_cmd";
}
our @valid_actions = qw(
   create_arm create_cx create_endp normalize_latency
   delete_cx delete_cxe delete_endp do_cmd
   list_cx list_endp list_ports
   set_endp show_cx show_endp show_port start_endp stop_endp
   );

if (($::action eq "") && ((defined $::endp_vals) && ("$::endp_vals" ne ""))) {
  $::action = "show_endp";
}

if (! (grep {$_ eq $::action} @::valid_actions )) {
  die("Invalid action: $::action\n$::usage\n");
}
our @actions_needing_endp = qw(
   create_arm create_endp
   delete_endp
   set_endp start_endp stop_endp
   );
if (grep {$_ eq $::action} @actions_needing_endp) {
  if (length($::endp_name) == 0) {
    print "ERROR:  Must specify endp_name.\n";
    die("$::usage");
  }
}
if ($::quiet eq "1" ) {
   $::quiet = "yes";
}

# Open connection to the LANforge server.
our $utils = new LANforge::Utils();
if (!defined $::stats_from_file || ("" eq $::stats_from_file)) {
   $::utils->connect($lfmgr_host, $lfmgr_port);
}

if (grep {$_ eq $::action} split(',', "show_endp,set_endp,create_endp,create_arm,list_endp,normalize_latency")) {

   $::max_speed = $::speed if ($::max_speed eq "-1");
   if ($::action eq "normalize_latency") {
      my $val = $::utils->normalize_latency($::lat1, $::lat2);
      print("Normalized-Latency: $val\n");
   }
   elsif ($::action eq "list_endp") {
      $::utils->cli_rcv_silent(0);
      $::quiet = "no";
      my @lines = split(/\r?\n/, $::utils->doAsyncCmd("nc_show_endpoints all"));
      for my $line (@lines) {
         if ($line =~ /^([A-Z]\w+)\s+\[(.*?)\]/) {
            print "** $line\n";
         }
      }
   }
   elsif ($::action eq "show_endp") {
      if ((defined $::endp_vals) && ("$::endp_vals" ne "")) {

         my %option_map    = ();
         my $option        = '';
         for $option (split(',', $::endp_vals)) {
            #print "OPTION[$option]\n";
            #next if ($option =~ /\s/);
            if ($option =~ /rx_pps/    ) { $option = "Rx Pkts"; }
            if ($option =~ /tx_pps/    ) { $option = "Tx Pkts"; }
            if ($option =~ /rx_pkts/   ) { $option = "Rx Pkts"; }
            if ($option =~ /tx_pkts/   ) { $option = "Tx Pkts"; }

            # we don't know if we're armageddon or layer 3
            if ($option =~ /tx_bytes/  ) {
               $option_map{ "Tx Bytes" } = '';
               $option = "Bytes Transmitted";
            }
            if ($option =~ /rx_b(ps|ytes)/  ) {
               $option_map{ "Rx Bytes" } = '';
               $option = "Bytes Rcvd";
            }
            if ($option =~ /tx_packets/) {
               $option_map{ "Tx Pkts" } = '';
               $option = "Packets Transmitted";
            }
            if ($option =~ /rx_packets/) {
               $option_map{ "Rx Pkts" } = '';
               $option = "Packets Rcvd";
            }

            $option_map{ $option } = '';
         }
         # options are reformatted

         my $i;
         my @lines = ();
         if ($stats_from_file ne "") {
           @lines = split(/\r?\n/, get_stats_from_file($stats_from_file, $endp_name));
         }
         else {
           @lines = split(/\r?\n/, $::utils->doAsyncCmd("nc_show_endp $endp_name"));
         }

         for($i=0; $i<@lines; $i++) {
            $lines[$i] = $lines[$i]." #";
         }
         my $matcher = " (".join('|', keys %option_map)."):";
         my @parts;
         my @matches = grep( /$matcher/, @lines);
         my $match;
         #print "MATCHER $matcher  matches:\n" . join("\n", @matches) . NL;
         for my $end_val (split(',', $::endp_vals)) {
            my $endval_done = 0;
            for $match (@matches) {
               last if ($endval_done);
               #print "\nMatch-line: $end_val> $match\n";

               # no value between colon separated tags can be very
               # confusing to parse, let's force a dumb value in if we find that
               if ($match =~ /[^ ]+:\s+[^ ]+:/) {
                  $match =~ s/([^ ]+:)\s+([^ ]+:\s+)/$1 ""  $2/g;
                  #print "\n M> $match\n";
               }

               ## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
               ##    special cases                                                  #
               ## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
               if ($end_val =~ /Latency/) {
                  if ($match =~ /.*Latency:\s+(.*)\s+#/) {
                     my $val = $1;
                     #print "val -:$val:-\n";
                     $option_map{"Normalized-Hdr"} = $::utils->normalize_bucket_hdr(17);
                     $option_map{"Latency"} = $val;
                  }
               }
               elsif ($end_val =~ /Pkt-Gaps/) {
                  if ($match =~ /.*Pkt-Gaps:\s+(.*)\s+#/) {
                     my $val = $1;
                     $option_map{"Normalized-Hdr"} = $::utils->normalize_bucket_hdr(17);
                     $option_map{"Pkt-Gaps"} = $val;
                  }
               }
               elsif ($end_val =~ /RX-Silence/) {
                  if ($match =~ /.*RX-Silence:\s+(.*)\s+#/) {
                     my $val = $1;
                     $option_map{"Normalized-Hdr"} = $::utils->normalize_bucket_hdr(17);
                     $option_map{"RX-Silence"} = $val;
                  }
               }
               elsif ($end_val =~ /Cx Detected/) {
                  my $value = 0;
                  #print "# case 2\n";
                  ($option) = ($match =~ /(Cx Detected)/);
                  if (defined $option_map{ $option } ) {
                     $value = 0 + ($match =~ /:\s+(\d+)/)[0];
                     $option_map{ $option } = $value;
                     $endval_done++;
                     last;
                  }
               }
               elsif (($match =~ /Tx (Bytes|Pkts)/ && (($end_val =~ /tx_(bps|pps)/) || ($end_val =~ /Tx (Bytes|Pkts)/) || ($end_val =~ /(Pkts|Bytes) Sent/))) ||
                     ($match =~ /Rx (Bytes|Pkts)/ && (($end_val =~ /rx_(bps|pps)/) || ($end_val =~ /Rx (Bytes|Pkts)/)|| ($end_val =~ /(Pkts|Bytes) Rcvd/)))) {
                  my $value = 0;
                  ($option) = ($match =~ /([TR]x (Bytes|Pkts))/);
                  #print "# case 3, Option: $option" . NL;
                  @parts      = ($match =~ m{ Total: (\d+) +Time: \d+s\s+ Cur: (\d+) +(\d+)\/s \#$});
                  #print "\n TX: ".join(",",@parts)."\n";
                  if (defined $option_map{ $option } ) {
                     if (($end_val =~ /tx_(bps|pps)/ ) ||
                         ($end_val =~ /rx_(bps|pps)/ )) {
                        $value = 0 + $parts[2];
                        if ($end_val =~ /bps/) {
                          $value *= 8;
                        }
                     }
                     else {
                        $value = 0 + $parts[0];
                     }
                     print "\n    B end_val[$end_val] option[$option] now ".$value."\n";
                     $option_map{ $end_val } = $value;

                     # For backwards compat with older logic
                     if (defined($option_map{"Bytes Rcvd"})) {
                       if ($end_val eq "Rx Bytes") {
                         $option_map{"Bytes Rcvd"} = $value;
                       }
                     }
                     $endval_done++;
                     last;
                  }
               }
               elsif ($match =~ / [TR][Xx] (((OOO|Duplicate|Failed) (Bytes|Pkts))|Wrong Dev|CRC Failed|Bit Errors|Dropped)/
                     || $match =~ /Conn (Established|Timeouts)|TCP Retransmits/) {
                  my $value = 0;
                  ($option) = ($match =~ /([TR][Xx] (((OOO|Duplicate|Failed) (Bytes|Pkts))|Wrong Dev|CRC Failed|Bit Errors|Dropped)|Conn (Established|Timeouts)|TCP Retransmits)/);
                  @parts      = $match =~ m{ Total: (\d+) +Time: \d+s\s+ Cur: (\d+) +(\d+)\/s \#$};
                  #print "\n# case 4 TX: ".join(",",@parts)."\n";
                  if (defined $option_map{ $option } ) {
                     #print "$match\n";
                     $match =~ s/""/ /g;
                     ($option_map{ $option }) = $match =~/.*?:\s+(.*?)\s+\#$/;
                     $endval_done++;
                     last;
                  }
               }
               elsif ($match =~ /(Bytes|Packets) (Rcvd|Transmitted)/ ) {
                  ($option) = ($match =~ /((Bytes|Packets) (Rcvd|Transmitted))/);
                  @parts      = ($match =~ m{ Total: (\d+) +Time: \d+s\s+ Cur: (\d+) +(\d+)\/s \#$});
                  #print "\n# case 5 TX: ".join(",",@parts)."\n";
                  my $value = 0;
                  if (defined $option_map{ $option } ) {
                     if ($end_val =~ /rx_(bps|pps)/ ) {
                        $value = 0 + $parts[2];
                     }
                     elsif ($end_val =~ /rx_(byte|pkt|packet)s/ ) {
                        $value = 0 + $parts[0];
                     }
                     if ($option eq "Bytes Rcvd") {
                        if ($end_val =~ /rx_bps/ ) {
                           $value   *= 8;
                        }
                     }
                     $option_map{ $option } = $value;
                     $endval_done++;
                     last;
                  }
               }
               else {
                  $match =~ s/Shelf: (\d+), /Shelf: $1  /
                     if ($match =~ /^\s*Shelf:/ );

                  $match =~ s/(Endpoint|PktsToSend): (\d+) /$1: $2  /
                     if ($match =~ /\s*(Endpoint|PktsToSend):/ );

                  if ($match =~ /((Src|Dst)Mac): /) {
                     my ($name1, $mac1) = ( $match =~ /(...Mac): (.*?)  /);
                     $mac1 =~ s/ /-/g;
                     $match =~ s/(...Mac): (.. .. .. .. .. ..) /$1: $mac1 /;
                  }
                  if ($match =~ /FileName: .*? SendBadCrc: /) {
                     my $filename1 = '';
                     ($filename1) =~ /FileName: (.*?) SendBadCrc.*$/;
                     $filename1 = '""' if ($filename1 =~ /^ *$/);
                     $match =~ s/(FileName): (.*?) (SendBadCrc.*)$/$1: $filename1  $3/;
                  }
                  $match =~ s/CWND: (\d+) /CWND: $1  /
                     if ($match =~/CWND: (\d+) /);
                  # ~specials

                  #print "  match: $match\n";
                  if ($match =~ /.*$end_val:\s+(\S+)/) {
                    my $value = $1;
                    #print " Found value: $value for key: $end_val\n";
                    $option_map{ $end_val } = $value;
                    $endval_done++;
                  }
               }
            } # ~matches
         } # ~endp_vals
         for $option ( sort keys %option_map ) {
            print $option.": ".$option_map{ $option }.$::NL;
         }
      }
      else {
        if ($stats_from_file ne "") {
          print get_stats_from_file($stats_from_file, $endp_name);
        }
        else {
          print $::utils->doAsyncCmd("nc_show_endp $::endp_name");
        }
      }
   }
   elsif ($::action eq "create_arm") {
      die("Must choose packets per second: --arm_pps\n$::usage")
         if (! defined $::arm_pps || $::arm_pps eq "");

      $::min_pkt_sz = "1472" if ($::min_pkt_sz eq "-1");
      $::max_pkt_sz = $::min_pkt_sz if ($::max_pkt_sz eq "-1");
      my $ip_port   = "-1"; # let lf choose
      $cmd = $::utils->fmt_cmd("add_arm_endp",   $::endp_name,  $shelf_num,     $::resource,
                              $::port_name,     "arm_udp",     $::arm_pps,
                              $::min_pkt_sz,    $::max_pkt_sz, $::arm_cpu_id, $::tos);
      $::utils->doCmd($cmd);

      $cmd = "set_endp_report_timer $::endp_name $::report_timer";
      $::utils->doCmd($cmd);
   }
   elsif ($::action eq "create_endp") {
     create_endp($::endp_name, $::resource, $::port_name, $::endp_type, $::speed, $::max_speed);
   }
   else {
      # Set endp
      if ($speed ne "NA") {
         # Read the endpoint in...
         #my $endp1 = new LANforge::Endpoint();
         #$::utils->updateEndpoint($endp1, $endp_name);

         # Assume Layer-3 for now
         $cmd = $::utils->fmt_cmd("add_endp", $endp_name, $::NA, $::NA, $::NA,
            $::NA, $::NA, $::NA, $speed,  $max_speed);
         #print("cmd: $cmd\n");
         $::utils->doCmd($cmd);
      }
   }
}
elsif ($::action eq "start_endp") {
   $cmd = "start_endp $::endp_name";
   $::utils->doCmd($cmd);
}
elsif ($::action eq "stop_endp") {
   $cmd = "stop_endp $::endp_name";
   $::utils->doCmd($cmd);
}
elsif ($::action eq "delete_endp") {
   $cmd = "rm_endp $::endp_name";
   $::utils->doCmd($cmd);
}
elsif ($::action eq "show_port") {
  print $::utils->doAsyncCmd("nc_show_port 1 $::resource $::port_name") . "\n";
}
elsif ($::action eq "do_cmd") {
  print $::utils->doAsyncCmd("$::do_cmd") . "\n";
}
elsif ($::action eq "list_ports") {
  my @ports = $::utils->getPortListing($::shelf_num, $::resource);
  my $i;
  for ($i = 0; $i<@ports; $i++) {
    my $cur = $ports[$i]->cur_flags();
    #print "cur-flags -:$cur:-\n";

    print $ports[$i]->dev();
    if ($cur =~ /LINK\-UP/) {
      print " link=UP";
    }
    else {
      print " link=DOWN";
    }
    # Guess speed..need better CLI output API for more precise speed.
    if ($cur =~ /10G\-FD/) {
      print " speed=10G";
    }
    elsif ($cur =~ /1000\-/) {
      print " speed=1G";
    }
    elsif ($cur =~ /100bt\-/) {
      print " speed=100M";
    }
    elsif ($cur =~ /10bt\-/) {
      print " speed=10M";
    }
    else {
      print " speed=UNKNOWN";
    }
    print "\n";
  }
}
elsif ($::action eq "list_cx") {
   $::cx_name  = $::list_cx_name    if ($::cx_name  eq "");
   $::test_mgr = $::list_test_mgr   if ($::test_mgr eq "");

   my $cmd = $::utils->fmt_cmd("show_cxe", $::test_mgr, $::cx_name );
   my @lines = split(/\r?\n/, $::utils->doAsyncCmd($cmd));
   my $out = '';
   my $num_ep = 0;
   for my $line (@lines) {
      #print "      |||$line\n";
      if ($line =~ /\s*WAN_LINK CX:\s+([^ ]+)\s+id:.*$/ ) {
         $out .= "WL $1";
      }
      if ($line =~ /^WanLink\s+\[([^ ]+)\] .*$/ ) {
         $out .= ", wanlink $1";
         $num_ep++;
      }
      if ($line =~ /^\s*(WanLink|LANFORGE.*? CX):\s+([^ ]+) .*$/ ) {
         $out .= "CX $2";
      }
      if ($line =~ /^ARM_.*? CX:\s+([^ ]+) .*$/ ) {
         $out .= "CX $1";
      }
      if ($line =~ /^(Endpoint|ArmEndp) \[([^ \]]+)\].*$/) {
         $out .= ", endpoint $2";
         $num_ep++;
      }
      if (($line =~ /^ *$/) && ($num_ep >1)) {
         print "$out\n";
         $out = '';
         $num_ep = 0;
      }
   }
}
elsif ($::action eq "show_cx") {
   # require a cx_name
   die("Please specify cx_name\n$::usage") if (length($::cx_name) < 1);
   if (length($::test_mgr) <1) {
      $::test_mgr = "default_tm";
   }
   my $cmd = $::utils->fmt_cmd("show_cxe", $::test_mgr, $::cx_name );
   print $::utils->doAsyncCmd($cmd)."\n";
}
elsif ($::action eq "create_cx") {
   # require cx_name, test_mgr, two endpoints
   my $end_a = "";
   my $end_b = "";
   my $port_a = "";
   my $port_b = "";
   my $speed_a = 0;
   my $speed_b = 0;
   my $max_speed_a = $::max_speed;
   my $max_speed_b = $::max_speed;

   if ("NA" ne $::use_ports_str) {
     ($port_a, $port_b) = split(',', $::use_ports_str);
     if (!(defined $port_a) || !(defined $port_b)) {
       die("Error with port names. Please format as short EIDs: 1.1.sta0000,1.2.eth1");
     }
     die("Please name your cross connect: --cx_name\n$::usage")
        if ($::cx_name  eq "");
     $end_a = "${main::cx_name}-A";
     $end_b = "${main::cx_name}-B";
     $::cx_endps = "$end_a,$end_b";
   }
   elsif ((defined $::cx_endps) && ("" ne $::cx_endps)) {
     ($end_a, $end_b) = split(/,/, $::cx_endps);
     die("Specify two endpoints like: tcp123-A,tcp123-B \n$::usage")
        if ((length($end_a) < 1) || (length($end_b) < 1));
   }
   else {
     die("please use --cx_endps a,b or --use_ports portA,portB");
   }

   if ("NA" ne $::use_speeds_str) {
     ($speed_a, $speed_b) = split(',', $::use_speeds_str);
     $max_speed_a = $speed_a;
     $max_speed_b = $speed_b;
   }
   if ("NA" ne $::use_max_speeds) {
     ($max_speed_a, $max_speed_b) = split(',', $::use_speeds_str);
   }

   # create endpoints
   my $resource_a = $::resource;
   my $resource_b = $::resource;
   my $shelf;
   my @hunks;
   if ($port_a =~ /1\.\d+\.\S+/) {
     @hunks = split(/[.]/, $port_a);
     ($shelf, $resource_a, $port_a) = @hunks;
   }
   if ($port_b =~ /1\.\d+\.\S+/) {
     @hunks = split(/[.]/, $port_b);
     ($shelf, $resource_b, $port_b) = @hunks;
   }
   print ("end_a[$end_a] resource_a[$resource_a] port_a[$port_a], type[$::endp_type] speed[$speed_a] max[$max_speed_a]\n");
   print ("end_b[$end_b] resource_b[$resource_b] port_b[$port_b], type[$::endp_type] speed[$speed_b] max[$max_speed_b]\n");
   create_endp($end_a, $resource_a, $port_a, $::endp_type, $speed_a, $max_speed_a);
   create_endp($end_b, $resource_b, $port_b, $::endp_type, $speed_b, $max_speed_b);

   my $cmd = $::utils->fmt_cmd("add_cx", $::cx_name, $::test_mgr, $end_a, $end_b);
   $::utils->doCmd($cmd);
   my $cxonly = $::NA;
   $cmd = $::utils->fmt_cmd("set_cx_report_timer", $::test_mgr, $::cx_name, $::report_timer, $cxonly);
   $::utils->doCmd($cmd);
}
elsif ($::action eq "delete_cx") {
   # require cx_name
   die("Which test manager?: --test_mgr\n$::usage") if ($::test_mgr eq "");
   die("Which cross connect? --cx_name\n$::usage")  if ($::cx_name eq "");
   $::utils->doCmd($::utils->fmt_cmd("rm_cx", $::test_mgr, $::cx_name));
}
elsif ($::action eq "delete_cxe") {
   # require cx_name
   die("Which test manager?: --test_mgr\n$::usage") if ($::test_mgr eq "");
   die("Which cross connect? --cx_name\n$::usage")  if ($::cx_name eq "");
   $::utils->doCmd($::utils->fmt_cmd("rm_cx", $::test_mgr, $::cx_name));
   $::utils->doCmd($::utils->fmt_cmd("rm_endp", "$::cx_name-A"));
   $::utils->doCmd($::utils->fmt_cmd("rm_endp", "$::cx_name-B"));
}
else {
  die("Unknown action: $::action\n$::usage\n");
}

exit(0);
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
sub create_endp {
   my ($my_endp_name, $my_resource, $my_port_name, $my_endp_type, $my_speed, $my_max_speed) = @_;


   die("Must choose endpoint protocol type: --endp_type\n$::usage")
         if (! defined $::endp_type|| $::endp_type eq "");

   if ($my_endp_type eq "tcp") {
     $my_endp_type = "lf_tcp";
   }
   if ($my_endp_type eq "udp") {
     $my_endp_type = "lf_udp";
   }

   if ($my_endp_type ne "NA") {
     die("Endpoint protocol type --endp_type must be among "
        .join(', ', @::known_endp_types)."\n".$::usage)
       if (! grep {$_ eq $my_endp_type } @::known_endp_types);
   }

  if ($my_endp_type eq "generic") {
    if ($::endp_cmd eq "") {
      die("Must specify endp_cmd if creating a generic endpoint.\n");
    }
    $cmd = $::utils->fmt_cmd("add_gen_endp",   $my_endp_name,  1, $my_resource,
                              $my_port_name,  "gen_generic");
    $::utils->doCmd($cmd);

    # Create the dummy
    #my $dname = "D_" . $::endp_name;
    #$cmd = $::utils->fmt_cmd("add_gen_endp",   $dname,  shelf_num,     $::resource,
    #                          $::port_name,  "gen_generic");
    #$::utils->doCmd($cmd);

    $cmd = "set_gen_cmd " . $my_endp_name . " " . $::endp_cmd;
    $::utils->doCmd($cmd);

    $cmd = "set_endp_report_timer $my_endp_name $::report_timer";
    $::utils->doCmd($cmd);

    $::cx_name = "CX_" . $my_endp_name;
    $cmd = "add_cx $::cx_name $::test_mgr $my_endp_name";
    $::utils->doCmd($cmd);

    my $cxonly = $::NA;
    $cmd = $::utils->fmt_cmd("set_cx_report_timer", $::test_mgr, $::cx_name, $::report_timer, $cxonly);
    $::utils->doCmd($cmd);
  }
  elsif ($my_endp_type eq "mc_udp") {
    # For instance:
    # add_endp mcast-xmit-eth1 1 3 eth1 mc_udp 9999 NO 9600 0 NO 1472 1472 INCREASING NO 32 0 0
    # set_mc_endp mcast-xmit-eth1 32 224.9.9.9 9999 NO
    # Assume Layer-3 for now

    $cmd = $::utils->fmt_cmd("add_endp",    $my_endp_name,  1,     $my_resource,
                             $my_port_name, $my_endp_type,  $::mcast_port, $::NA,
                             $my_speed,     $my_max_speed,  $::NA,         $::min_pkt_sz,
                             $::max_pkt_sz, "increasing",   $::use_csums,  $::ttl, "0", "0");
    $::utils->doCmd($cmd);

    $cmd = $::utils->fmt_cmd("set_mc_endp", $::endp_name, $::ttl, $::mcast_addr, $::mcast_port, $::rcv_mcast);
    $::utils->doCmd($cmd);

    $cmd = "set_endp_report_timer $::endp_name $::report_timer";
    $::utils->doCmd($cmd);
  }
  elsif (grep { $_ eq $my_endp_type} split(/,/, "lf_udp,lf_tcp,lf_udp6,lf_tcp6,NA")) {
     if ($::use_ports_str ne "NA") {
       ($::port_name,) = split(',', $::use_ports_str);
     }
     die("Which port is this? --port_name")
         if (!defined $::port_name || $port_name eq "" || $port_name eq "0" );

     if ($::use_speeds_str ne "NA") {
       ($::speed,) = split(',', $::use_speeds_str);
     }
     die("Please set port speed: --speed")
         if ($::speed eq "-1"|| $::speed eq $::NA);

     if ($::min_pkt_sz =~ /^\s*auto\s*$/i) {
         $::min_pkt_sz = "-1";
     }
     if ($::max_pkt_sz =~ /^\s*same\s*$/i ) {
        $::max_pkt_sz = "0";
     }
     elsif ($::max_pkt_sz =~ /^\s*auto\s*$/i) {
        $::max_pkt_sz = "-1";
     }

     # Assume Layer-3 for now
     my $bursty    = $::NA;
     my $random_sz = $::NA;
     my $payld_pat = "increasing";
     $::ttl        = $::NA;
     my $bad_ppm   = "0";
     $cmd = $::utils->fmt_cmd("add_endp",   $my_endp_name,  1,   $my_resource,
                              $my_port_name, $my_endp_type,  $::ip_port,   $bursty,
                              $my_speed,     $my_max_speed,
                              $random_sz,    $::min_pkt_sz, $::max_pkt_sz,
                              $payld_pat,    $::use_csums,  $::ttl,
                              $bad_ppm,      $::multicon);
     $::utils->doCmd($cmd);

     $cmd = "set_endp_report_timer $my_endp_name $::report_timer";
     $::utils->doCmd($cmd);

     if ($::tos ne "") {
        my($service, $priority) = split(',', $::tos);
        if (!$priority) {
          $priority = "NA";
        }
        $::utils->doCmd("set_endp_tos $my_endp_name $service $priority");
     }
  }
  else {
    die( "ERROR:  Endpoint type: $::endp_type is not currently supported.");
  }
} # ~create_endp()

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
sub get_stats_from_file {
  my $fname = shift;
  my $endp_name = shift;

  open(F, "<$fname") or die("Can't open $fname for reading: $!\n");

  my $endp_text = "";
  my $ep = "";

  my @lines = ();
  while ( my $line = <F>) {
    @lines = (@lines, $line);
  }
  # Append dummy line to make it easier to terminate the parse logic.
  @lines = (@lines, "Endpoint [________] (NOT_RUNNING)\n");

  my $i;
  for ($i = 0; $i<@lines;$i++) {
    my $line = $lines[$i];
    chomp($line);
    if (($line =~ /Endpoint\s+\[(.*)\]/) ||
        ($line =~ /WanLink\s+\[(.*)\]/) ||
        ($line =~ /ArmEndp\s+\[(.*)\]/) ||
        # TODO: Layer-4 ?
        ($line =~ /VoipEndp\s+\[(.*)\]/)) {

      my $m1 = $1;
      #print "Found starting line: $line  name: $m1  endp_name: $endp_name\n";
      if ($endp_text ne "") {
        # See if existing endp entry matches?
        if ($ep eq $endp_name) {
          return $endp_text;
        }
      }
      $endp_text = "$line\n";
      $ep = $m1;
    }
    else {
      if ($endp_text ne "") {
        $endp_text .= "$line\n";
      }
    }
  }
  return "";
}
