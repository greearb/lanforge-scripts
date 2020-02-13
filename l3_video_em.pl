#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
use Data::Dumper;

# Un-buffer output
$| = 1;
if ( -f "LANforge/Endpoint.pm" ) {
  use lib "./";
}
else {
  use lib '/home/lanforge/scripts';
}
use LANforge::Endpoint;
use LANforge::Port;
use LANforge::Utils;
use Net::Telnet ();
use Getopt::Long;
use Time::HiRes qw(usleep gettimeofday);
our $has_usleep = (defined &usleep) ? 1 : 0;

sub sleep_ms {
  my ($millis) = @_;
  return if (!(defined $millis) || ($millis == 0));

  my $secs = $millis / 1000;

  if ($::has_usleep) {
    #print ",";
    usleep($millis * 1000);
  }
  else {
    print ";";
    select(undef, undef, undef, $secs);
  }
}
sub sleep_sec {
  my ($secs) = @_;
  return if (!(defined $secs) || ($secs == 0));

  if ($::has_usleep) {
    #print ",";
    usleep($secs * 1000000);
  }
  else {
    print ";";
    select(undef, undef, undef, $secs);
  }
}

my  $NA              ='NA';
our $resource        = 1;
our $quiet           = "yes";
our $silent          = 0;
our $endp_name       = "";
our $speed           = "-1";
our $action          = "";
our $do_cmd          = "NA";
our $lfmgr_host      = "localhost";
our $lfmgr_port      = 4001;
our $tx_style        = "";
our $cx_name         = "";
our $tx_side         = "B";
our $min_tx          = 0;
our $max_tx          = -1;
our $buf_size        = -1;
our $log_cli         = "unset"; # do not set to 0, it turns into logfile "./0"
our $stream_key      = undef;
#our @frame_rates     = ( 10, 12, 15, 24, 25, 29.97, 30, 50, 59.94, 60);
#our $frame_rates_desc = join(", ", @::frame_rates);
#our $frame_rate      = 30;
#our $audio_rate      = 32000; # 128k is used on Blueray DVDs
#our @audio_rates     = 128000; # 128k

# https://en.wikipedia.org/wiki/Standard-definition_television
# https://www.adobe.com/devnet/adobe-media-server/articles/dynstream_live/popup.html
# https://en.wikipedia.org/wiki/ISDB-T_International
# https://en.wikipedia.org/wiki/Frame_rate
# https://en.wikipedia.org/wiki/List_of_broadcast_video_formats
# https://blog.forret.com/2006/09/27/hd-720p-1080i-and-1080p/
# Framerate is highly subjective in digital formats, because there are
# variable frame rates dictated by min- and max-frame rate.
our %stream_keys = (
  'w'           => 0,
  'width'       => 0,
  'x'           => 0,
  'h'           => 1,
  'height'      => 1,
  'y'           => 1,
  'i'           => 2,
  'interlaced'  => 2,
  'audio'       => 3,
  'audio_bps'   => 3,
  'video'       => 4,
  'video_bps'   => 4,
  'stream'      => 5,
  'stream_bps'  => 5,
  'fps'         => 6,
  'frames'      => 6,
  'framerate'   => 6,
  );

our %avail_stream_res = (
  # nicname             w,    h,  interlaced,   audio,    vid bps,   tt bps   framerate
  "sqvga-4:3"     => [  160,  120,    0,         16000,    32000,        48000,    30],
  "sqvga-16:9"    => [  160,   90,    0,         16000,    32000,        48000,    30],
  "qvga-4:3"      => [  320,  240,    0,         16000,    32000,        48000,    30],
  "qvga-16:9"     => [  320,  180,    0,         16000,    32000,        48000,    30],
  "qcif-48k-4:3"  => [  144,  108,    0,         16000,    32000,        48000,    30],
  "qcif-48k-16:9" => [  192,  108,    0,         16000,    32000,        48000,    30],
  "qcif-96k-4:3"  => [  192,  144,    0,         16000,    80000,        96000,    30],
  "qcif-96k-16:9" => [  256,  144,    0,         16000,    80000,        96000,    30],
  "cif"           => [  352,  288,    0,         32000,   268000,       300000,    30],
  "cif-300k-4:3"  => [  288,  216,    0,         32000,   268000,       300000,    30],
  "cif-300k-16:9" => [  384,  216,    0,         32000,   268000,       300000,    30],
  "cif-500k-4:3"  => [  320,  240,    0,         32000,   468000,       500000,    30],
  "cif-500k-16:9" => [  384,  216,    0,         32000,   468000,       500000,    30],
  "d1-800k-4:3"   => [  640,  480,    0,         32000,   768000,       800000,    30],
  "d1-800k-16:9"  => [  852,  480,    0,         32000,   768000,       800000,    30],
  "d1-1200k-4:3"  => [  640,  480,    0,         32000,  1168000,      1200000,    30],
  "d1-1200k-16:9" => [  852,  480,    0,         32000,  1168000,      1200000,    30],
  "hd-1800k-16:9" => [ 1280,  720,    0,         64000,  1736000,      1800000,    59.94],
  "hd-2400k-16:9" => [ 1280,  720,    0,         64000,  2272000,      2336000,    59.94],

  "108p4:3"       => [  144,  108,    0,         16000,    32000,        48000,    30],
  "144p16:9"      => [  192,  144,    0,         16000,    80000,        96000,    30],
  "216p4:3"       => [  288,  216,    0,         32000,   268000,       300000,    30],
  "216p16:9"      => [  384,  216,    0,         32000,   268000,       300000,    30],
  "240p4:3"       => [  320,  240,    0,         32000,   468000,       500000,    30],

  "360p4:3"       => [  480,  360,    0,         32000,   768000,       800000,    30],
  "480i4:3"       => [  640,  480,    1,         32000,   768000,       800000,    30],
  "480p4:3"       => [  640,  480,    0,         32000,   768000,       800000,    30],
  "480p16:9"      => [  852,  480,    0,         32000,  1168000,      1200000,    30],

  # unadopted standard
  #"720i"          => [ 1280,  720,    1,        64000,  1736000,    1800000,    30],
  # 0.92 megapixels, 2.76MB per frame
  "720p"          => [ 1280,  720,    0,         64000,   1736000,     1800000,    59.94],

  # https://support.google.com/youtube/answer/1722171?hl=en
  # h.264 stream rates, SDR quality
  "yt-sdr-360p30"  => [  640,  360,    0,       128000,   1000000,     1128000,    30],
  "yt-sdr-480p30"  => [  852,  480,    0,       128000,   2500000,     2628000,    30],
  "yt-sdr-720p30"  => [ 1280,  720,    0,       384000,   5000000,     5384000,    30],
  "yt-sdr-1080p30" => [ 1920, 1080,    0,       384000,   8000000,     8384000,    30],
  "yt-sdr-1440p30" => [ 2560, 1440,    0,       512000,  16000000,    16512000,    30],
  "yt-sdr-2160p30" => [ 3840, 2160,    0,       512000,  40000000,    40512000,    30],

  "yt-sdr-360p60"  => [  640,  360,    0,       128000,   1500000,     1628000,    60],
  "yt-sdr-480p60"  => [  852,  480,    0,       128000,   4000000,     4128000,    60],
  "yt-sdr-720p60"  => [ 1280,  720,    0,       384000,   7500000,     7884000,    60],
  "yt-sdr-1080p60" => [ 1920, 1080,    0,       384000,  12000000,    12384000,    60],
  "yt-sdr-1440p60" => [ 2560, 1440,    0,       512000,  24000000,    24512000,    60],
  "yt-sdr-2160p60" => [ 3840, 2160,    0,       512000,  61000000,    61512000,    60],
  #"yt-hdr-360p60"  => [ 1280,  720,    0,        32000,  1000000,   1800000,    60], # yt unsupported
  #"yt-hdr-480p60"  => [ 1280,  720,    0,        32000,  1000000,   1800000,    60], # yt unsupported

  "yt-hdr-720p30"  => [ 1280,  720,    0,       384000,   6500000,     6884000,    30],
  "yt-hdr-1080p30" => [ 1920, 1080,    0,       384000,  10000000,    10384000,    30],
  "yt-hdr-1440p30" => [ 2560, 1440,    0,       512000,  20000000,    20512000,    30],
  "yt-hdr-2160p30" => [ 3840, 2160,    0,       512000,  50000000,    50512000,    30],

  "yt-hdr-720p60"  => [ 1280,  720,    0,       384000,   9500000,     9884000,    60],
  "yt-hdr-1080p60" => [ 1920, 1080,    0,       384000,  15000000,    15384000,    60],
  "yt-hdr-1440p60" => [ 2560, 1440,    0,       512000,  30000000,    30512000,    60],
  "yt-hdr-2160p60" => [ 3840, 2160,    0,       512000,  75500000,    76012000,    60],

  "raw720p30"      => [ 1280,  720,    0,        64000,  221120000,  221184000,    30],
  "raw720p60"      => [ 1280,  720,    0,        64000,  442304000,  442368000,    60],

  # frame size 6.2MB
  # 1080i60 1920x1080 186MBps
  "raw1080i"       => [ 1920,  540,    1,       128000, 1486384000, 1486512000,    59.94],
  "raw1080i30"     => [ 1920,  540,    1,       128000, 1487872000, 1488000000,    30],
  "raw1080i60"     => [ 1920,  540,    1,       128000, 1487872000, 1488000000,    60],

  # 1080p60 1920x1080 373MBps, 6.2Mbps frame size
  "raw1080p"       => [ 1920, 1080,    0,       128000, 2975872000, 2976000000,    60],

);

our $avail_stream_desc = join(", ", keys(%avail_stream_res));
our $resolution = "yt-sdr-1080p30";
my $list_streams = undef;

our $usage = "$0:    # modulates a Layer 3 CX to emulate a video server
    # Expects an existing L3 connection
  --mgr         {hostname | IP}
  --mgr_port    {ip port}
  --tx_style    { constant | bufferfill }
  --cx_name     {name}
  --tx_side     {A|B} # which side is emulating the server,
                      # default $tx_side
  --max_tx      {speed in bps [K|M|G]} # use this to fill buffer
  --min_tx      {speed in bps [K|M|G]} # use when not filling buffer, default 0
  --buf_size    {size[K|M|G]}  # fill a buffer at max_tx for this long
  --stream_res  {$avail_stream_desc}
  --list_streams  # show stream bps table and exit
                  # default $resolution
  --log_cli {0|1} # use this to record cli commands
  --quiet {0|1|yes|no} # print CLI commands
  --silent        # do not print status output

  Example:
  1) create the L3 connection:
    ./lf_firemod.pl --resource 1 --action create_endp bursty-udp-A --speed 0 --endp_type lf_udp --port_name eth1 --report_timer 500
    ./lf_firemod.pl --resource 1 --action create_endp bursty-udp-B --speed 0 --endp_type lf_udp --port_name eth2 --report_timer 500
    ./lf_firemod.pl --resource 1 --action create_cx --cx_name bursty-udp  --cx_endps bursty-udp-A,bursty-udp-B
   $0  --cx_name bursty-udp --stream 720p --buf_size 8M --max_tx 40M
";
#  --frame_rate {$frame_rates_desc} # not really applicable
# the stream resolution (kbps) is really a better burn rate

my $show_help = undef;

$::stream_key = $resolution;
GetOptions
(
   'help|h'               => \$show_help,
   'quiet|q=s'            => \$::quiet,
   'silent+'              => \$::silent,
   'mgr|m=s'              => \$::lfmgr_host,
   'mgr_port|p:i'         => \$::lfmgr_port,
   'log_cli:s{0,1}'       => \$log_cli,
   'tx_style|style:s'     => \$::tx_style,
   'cx_name|e=s'          => \$::cx_name,
   'tx_side|side|s:s'     => \$::tx_side,
   'max_tx=s'             => \$::max_tx,
   'min_tx:s'             => \$::min_tx,
   'buf_size|buf=s'       => \$::buf_size,
   'stream_res|stream=s'  => \$::stream_key,
   'list_streams+'        => \$list_streams,
) || die($!);


if ($show_help) {
   print $usage;
   exit 0;
}

if ($list_streams) {
  print "Predefined Video Streams\n";
  print "=" x 72, "\n";
  print "         Stream         W      H         Audio+Video\n";
  my %sortedkeys = ();
  foreach my $oldkey (keys(%::avail_stream_res)) {
    my $ra_row  = $::avail_stream_res{$oldkey};
    my $x       =    10000000 + int(@$ra_row[$stream_keys{x}]);
    my $y       =    10000000 + int(@$ra_row[$stream_keys{y}]);
    my $b       = 10000000000 + int(@$ra_row[$stream_keys{video_bps}]);
    my $newkey = "${b}_${x}_${y}_${oldkey}";
    $sortedkeys{$newkey} = $oldkey;
  }
  foreach my $sorted_key (sort(keys(%sortedkeys))) {
    my $key = $sortedkeys{$sorted_key};
    my $ra_row1 = $::avail_stream_res{$key};
    my $x       = @$ra_row1[$stream_keys{x}];
    my $y       = @$ra_row1[$stream_keys{y}];
    my $bps     = int(@$ra_row1[$stream_keys{stream_bps}]);
    my $bps_sum = int(@$ra_row1[$stream_keys{video_bps}]) + int(@$ra_row1[$stream_keys{audio_bps}]);
    #my $warning = "";
    printf("[ %15s ]  %4s x %4s using %8s kbps", $key, $x, $y, ($bps/1000));
    if ($bps != $bps_sum) {
      print " Invalid BPS $bps, correct to $bps_sum";
    }
    print "\n";
  }
  exit 0;
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
      #print "LOG_CLI now 1\n";
    }
    else {
      $ENV{'LOG_CLI'} = $log_cli;
      #print "LOG_CLI now $log_cli\n";
    }
  }
}
$SIG{INT} = \&cleanexit;
# ========================================================================
sub cleanexit {
  if ((defined $::cx_name) && ("" ne $::cx_name)) {
    if (defined $::utils->telnet) {
      print STDERR "\nStopping $::cx_name\n";
      $::utils->doAsyncCmd($::utils->fmt_cmd("set_cx_state", "all", $::cx_name, "STOPPED"));
    }
  }
  exit 0;
}

# ========================================================================
our $est_fill_time_sec = 0;
our $last_fill_time_sec = 0;

sub filltime {
  my () = @_;

}

# ========================================================================

sub rxbytes {
  my ($endp) = @_;
  die ("called rxbytes with no endp name, bye")
    unless((defined $endp) && ("" ne $endp));

  my @lines = split("\n", $::utils->doAsyncCmd("nc_show_endpoints $endp"));
  #Tx Bytes:           Total: 0           Time: 60s   Cur: 0         0/s
  my $bytes = 0;
  my @matches = grep {/^\s+Rx Bytes/} @lines;
  if (@matches < 1) {
    warn "rx-bytes not found for [$endp]\n";
    print join("\n> ", @lines), "\n";
    return 0;
  }
  ($bytes) = $matches[0] =~ /Rx Bytes:\s+Total: (\d+)/;
  if (!(defined $bytes)) {
    warn "no rx-bytes match for [$endp]\n";
    print "="x72, "\n";
    print $matches[0], "\n";
    print "="x72, "\n";
    print join("\n> ", @lines), "\n";
    return 0;
  }
  return $bytes;
}


# ========================================================================

sub txbytes {
  my ($endp) = @_;
  die ("called txbytes with no endp name, bye")
    unless((defined $endp) && ("" ne $endp));

  my @lines = split("\n", $::utils->doAsyncCmd("nc_show_endpoints $endp"));
  #Tx Bytes:           Total: 0           Time: 60s   Cur: 0         0/s
  my $bytes = 0;
  my @matches = grep {/^\s+Tx Bytes/} @lines;
  if (@matches < 1) {
    warn "tx-bytes not found for [$endp]\n";
    print join("\n> ", @lines), "\n";
    return 0;
  }
  ($bytes) = $matches[0] =~ /Tx Bytes:\s+Total: (\d+)/;
  if (!(defined $bytes)) {
    warn "no tx-bytes match for [$endp]\n";
    print "="x72, "\n";
    print $matches[0], "\n";
    print "="x72, "\n";
    print join("\n> ", @lines), "\n";
    return 0;
  }
  return $bytes;
}

# ========================================================================
#     M A I N
# ========================================================================

if ($::quiet eq "1" ) {
   $::quiet = "yes";
}

# Wait up to 60 seconds when requesting info from LANforge.
my $t = new Net::Telnet(Prompt => '/default\@btbits\>\>/',
          Timeout => 60);

$t->open(Host    => $::lfmgr_host,
         Port    => $::lfmgr_port,
         Timeout => 10);

$t->max_buffer_length(16 * 1024 * 1000); # 16 MB buffer
$t->waitfor("/btbits\>\>/");

# Configure our utils.
our $utils = new LANforge::Utils();
$::utils->telnet($t);         # Set our telnet object.
if ($::utils->isQuiet()) {
 if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
   $::utils->cli_send_silent(0);
 }
 else {
   $::utils->cli_send_silent(1); # Do not show input to telnet
 }
 $::utils->cli_rcv_silent(1);  # Repress output from telnet
}
else {
 $::utils->cli_send_silent(0); # Show input to telnet
 $::utils->cli_rcv_silent(0);  # Show output from telnet
}
$::utils->log_cli("# $0 ".`date "+%Y-%m-%d %H:%M:%S"`);


die ("Please provide buffer size")
  unless((defined $buf_size) && ("" ne $buf_size));
if ($buf_size =~ /[kmg]$/i) {
  my($n) = $buf_size =~ /(\d+)/;
  if ($buf_size =~ /k$/i) {
    $buf_size = $n * 1024;
  }
  elsif ($buf_size =~ /m$/i) {
    $buf_size = $n * 1024 * 1024;
  }
  elsif ($buf_size =~ /g$/i) {
    $buf_size = $n * 1024 * 1024 * 1024;
  }
  else {
    die("Whhhhhuuuuuut?");
  }
}

die("Please specify max tx bps")
  unless("" ne $::max_tx);
if ($::max_tx =~ /[kmg]$/i) {
  my($n) = $::max_tx =~ /(\d+)/;
  if ($::max_tx =~ /k$/i) {
    $::max_tx = $n * 1000;
  }
  elsif ($::max_tx =~ /m$/i) {
    $::max_tx = $n * 1000 * 1000;
  }
  elsif ($::max_tx =~ /g$/i) {
    $::max_tx = $n * 1000 * 1000 * 1000;
  }
  else {
    die("Whhhhhuuuuuut?");
  }
}
if ($::min_tx =~ /[kmg]$/i) {
  my($n) = $::min_tx =~ /(\d+)/;
  if ($::min_tx =~ /k$/i) {
    $::min_tx = $n * 1000;
  }
  elsif ($::min_tx =~ /m$/i) {
    $::min_tx = $n * 1000 * 1000;
  }
  elsif ($::min_tx =~ /g$/i) {
    $::min_tx = $n * 1000 * 1000 * 1000;
  }
  else {
    die("Whhhhhuuuuuut?");
  }
}

my $stream_bps = 0;
die("Unknown stream key $::stream_key")
  unless(exists $::avail_stream_res{$::stream_key});

$stream_bps = @{$::avail_stream_res{$stream_key}}[$stream_keys{stream_bps}];

$::est_fill_time_sec  = (8 * $::buf_size) / $max_tx;
my $drain_time_sec = (8 * $::buf_size) / $stream_bps;
my $drain_wait_sec = $drain_time_sec - $est_fill_time_sec;

if ($drain_wait_sec <= 0) {
  my $stream_kbps = $stream_bps / 1000;
  print "Warning: constant transmit! Raise max_tx to at least $stream_kbps Kbps\n";
  $drain_wait_sec = 0;
}

my $buf_kB = $::buf_size / 1024;
print "Filling $buf_kB KB buffer for $::stream_key takes $est_fill_time_sec s, empties in $drain_time_sec s\n"
  unless($::silent);


die ("Please provide cx_name")
  unless((defined $::cx_name) && ("" ne $::cx_name));
# print out choices for now
my @lines = split("\r?\n", $::utils->doAsyncCmd($::utils->fmt_cmd("show_cx", "all", $::cx_name)));
my @matches = grep {/Could not find/} @lines;
die($matches[0])
  unless (@matches == 0);

print "\nStopping and configuring $::cx_name\n" unless($silent);
$::utils->doCmd($::utils->fmt_cmd("set_cx_state", "all", $::cx_name, "STOPPED"));

my $endp = "$::cx_name-${tx_side}";
@lines = split("\r?\n", $::utils->doAsyncCmd($::utils->fmt_cmd("nc_show_endp", $endp)));

@matches = grep {/ Shelf: 1, Card: /} @lines;
die ("No matches for show endp $endp")
  unless($matches[0]);

my ($res, $port, $type) = $matches[0] =~ /, Card: (\d+)\s+Port: (\d+)\s+Endpoint: \d+ Type: ([^ ]+)\s+/;

my $cmd = $::utils->fmt_cmd("add_endp", $endp, 1, $res, $port, $type,
    $NA, # ip_port
    $NA, # is_rate_bursty
    $::min_tx, # min_rate
    $::min_tx # max_rate
  );

$::utils->doAsyncCmd($cmd);
print "Starting $::cx_name..." unless($silent);
$::utils->doCmd($::utils->fmt_cmd("set_cx_state", "all", $::cx_name, "RUNNING"));
$cmd = $::utils->fmt_cmd("add_endp", $endp, 1, $res, $port, $type, $NA, $NA, $::max_tx, $::max_tx);
$::utils->doAsyncCmd($cmd);

my $startbytes = txbytes($endp);
do {
  print "+" unless ($silent);
  my ($starttime_sec, $starttime_usec) = gettimeofday();
  my $starttime = $starttime_sec + ($starttime_usec / 1000000 );
  my $bytes = 0;
  while($bytes < ($buf_size + $startbytes)) {
    $bytes = txbytes($endp);
    sleep_ms(200);
    #print " +$bytes" unless ($silent);
  }
  my ($finishtime_sec, $finishtime_usec) = gettimeofday();
  $last_fill_time_sec = ($finishtime_sec + ($finishtime_usec / 1000000)) - $starttime;
  if ($bytes > $buf_size) {
    print "\n +", ($bytes - $startbytes), " took $last_fill_time_sec\n";
  }
  $drain_wait_sec = $drain_time_sec - $last_fill_time_sec;
  if ($drain_wait_sec < 0) {
    print "\n Constant TX\n";
  }
  print "\n drain_wait_seconds now $drain_wait_sec v $est_fill_time_sec = ", ($est_fill_time_sec - $last_fill_time_sec ), "\n";

  if ($drain_wait_sec > 0) {
    $cmd = $::utils->fmt_cmd("add_endp", $endp, 1, $res, $port, $type, $NA, $NA, $::min_tx, $::min_tx);
    print "-" unless($silent);
    $::utils->doCmd($cmd);
    sleep_sec($drain_wait_sec);
    $startbytes = txbytes($endp);
    $cmd = $::utils->fmt_cmd("add_endp", $endp, 1, $res, $port, $type, $NA, $NA, $::max_tx, $::max_tx);
    $::utils->doCmd($cmd);
  }
} while(1);

#
