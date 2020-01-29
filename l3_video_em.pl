#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

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

our $resource        = 1;
our $quiet           = "yes";
our $endp_name       = "";
our $speed           = "-1";
our $action          = "";
our $do_cmd          = "NA";
our $lfmgr_host      = "localhost";
our $lfmgr_port      = 4001;
our $tx_style        = "";
our $cx_name         = "";
our $tx_side         = "B";
our $min_tx          = undef;
our $max_tx          = -1;
our $buf_size        = -1;
our $log_cli         = "unset"; # do not set to 0, it turns into logfile "./0"
our $stream_res      = undef;
our @frame_rates     = ( 10, 12, 15, 24, 25, 29.97, 30, 50, 59.94, 60);
our $frame_rates_desc = join(", ", @::frame_rates);
our $frame_rate      = 30;
our $audio_rate      = 32000; # 128k is used on Blueray DVDs
our @audio_rates      = 128000; # 128k

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
  "sqvga-4:3"     => [  160,  120,    0,        16000,    32000,      48000,    30],
  "sqvga-16:9"    => [  160,   90,    0,        16000,    32000,      48000,    30],
  "qvga-4:3"      => [  320,  240,    0,        16000,    32000,      48000,    30],
  "qvga-16:9"     => [  320,  180,    0,        16000,    32000,      48000,    30],
  "qcif-48k-4:3"  => [  144,  108,    0,        16000,    32000,      48000,    30],
  "qcif-48k-16:9" => [  192,  108,    0,        16000,    32000,      48000,    30],
  "qcif-96k-4:3"  => [  192,  144,    0,        16000,    80000,      96000,    30],
  "qcif-96k-16:9" => [  256,  144,    0,        16000,    80000,      96000,    30],
  "cif"           => [  352,  288,    0,        32000,   268000,     300000,    30],
  "cif-300k-4:3"  => [  288,  216,    0,        32000,   268000,     300000,    30],
  "cif-300k-16:9" => [  384,  216,    0,        32000,   268000,     300000,    30],
  "cif-500k-4:3"  => [  320,  240,    0,        32000,   468000,     500000,    30],
  "cif-500k-16:9" => [  384,  216,    0,        32000,   468000,     500000,    30],
  "d1-800k-4:3"   => [  640,  480,    0,        32000,   768000,     800000,    30],
  "d1-800k-16:9"  => [  852,  480,    0,        32000,   768000,     800000,    30],
  "d1-1200k-4:3"  => [  640,  480,    0,        32000,  1168000,    1200000,    30],
  "d1-1200k-16:9" => [  852,  480,    0,        32000,  1168000,    1200000,    30],
  "hd-1800k-16:9" => [ 1280,  720,    0,        64000,  1736000,    1800000,    59.94],
  "hd-2400k-16:9" => [ 1280,  720,    0,        64000,  2272000,    2336000,    59.94],


  "108p4:3"       => [  144,  108,    0,        16000,    32000,      48000,    30],
  "144p16:9"      => [  192,  144,    0,        16000,    80000,      96000,    30],
  "216p4:3"       => [  288,  216,    0,        32000,   268000,     300000,    30],
  "216p16:9"      => [  384,  216,    0,        32000,   268000,     300000,    30],
  "240p4:3"       => [  320,  240,    0,        32000,   468000,     500000,    30],

  "360p4:3"       => [  480,  360,    0,        32000,   768000,     800000,    30],
  "480i4:3"       => [  640,  480,    1,        32000,   768000,     800000,    30],
  "480p4:3"       => [  640,  480,    0,        32000,   768000,     800000,    30],
  "480p16:9"      => [  852,  480,    0,        32000,  1168000,    1200000,    30],

  # unadopted standard
  #"720i"          => [ 1280,  720,    1,        64000,  1736000,    1800000,    30],

  # 0.92 megapixels, 2.76MB per frame
  "720p"          => [ 1280,  720,    0,        64000,  1736000,    1800000,    59.94],

  # https://support.google.com/youtube/answer/1722171?hl=en
  # h.264 stream rates, SDR quality
  "yt-sdr-360p30"  => [  640,  360,    0,       128000,  1000000,   1128000,    30],
  "yt-sdr-480p30"  => [  852,  480,    0,       128000,  2500000,   2628000,    30],
  "yt-sdr-720p30"  => [ 1280,  720,    0,       384000,  5000000,   5384000,    30],
  "yt-sdr-1080p30" => [ 1920, 1080,    0,       384000,  8000000,   8384000,    30],
  "yt-sdr-1440p30" => [ 2560, 1440,    0,       512000, 16000000,  16512000,    30],
  "yt-sdr-2160p30" => [ 3840, 2160,    0,       512000, 40000000,  40512000,    30],

  "yt-sdr-360p60"  => [  640,  360,    0,       128000,  1500000,   1628000,    60],
  "yt-sdr-480p60"  => [  852,  480,    0,       128000,  4000000,   4128000,    60],
  "yt-sdr-720p60"  => [ 1280,  720,    0,       384000,  7500000,   7884000,    60],
  "yt-sdr-1080p60" => [ 1920, 1080,    0,       384000, 12000000,  12384000,    60],
  "yt-sdr-1440p60" => [ 2560, 1440,    0,       512000, 24000000,  24512000,    60],
  "yt-sdr-2160p60" => [ 3840, 2160,    0,       512000, 61000000,  61512000,    60],

  #"yt-hdr-360p60"  => [ 1280,  720,    0,        32000,  1000000,   1800000,    60], # yt unsupported
  #"yt-hdr-480p60"  => [ 1280,  720,    0,        32000,  1000000,   1800000,    60], # yt unsupported

  "yt-hdr-720p30"  => [ 1280,  720,    0,       384000,  6500000,   6884000,    30],
  "yt-hdr-1080p30" => [ 1920, 1080,    0,       384000, 10000000,  10384000,    30],
  "yt-hdr-1440p30" => [ 2560, 1440,    0,       512000, 20000000,  20512000,    30],
  "yt-hdr-2160p30" => [ 3840, 2160,    0,       512000, 50000000,  50512000,    30],

  "yt-hdr-720p60"  => [ 1280,  720,    0,       384000,  9500000,   9884000,    60],
  "yt-hdr-1080p60" => [ 1920, 1080,    0,       384000, 15000000,  15384000,    60],
  "yt-hdr-1440p60" => [ 2560, 1440,    0,       512000, 30000000,  30512000,    60],
  "yt-hdr-2160p60" => [ 3840, 2160,    0,       512000, 75500000,  76012000,    60],


  "raw720p30"      => [ 1280,  720,    0,        64000,  221120000,  221184000,    30],
  "raw720p60"      => [ 1280,  720,    0,        64000,  442304000,  442368000,    60],

  # frame size 6.2MB
  # 1080i60 1920x1080 186MBps
  "raw1080i"       => [ 1920,  540,    1,       128000,  1486384000, 1486512000,    59.94],
  "raw1080i30"     => [ 1920,  540,    1,       128000,  1487872000, 1488000000,    30],
  "raw1080i60"     => [ 1920,  540,    1,       128000,  1487872000, 1488000000,    60],

  # 1080p60 1920x1080 373MBps, 6.2Mbps frame size
  "raw1080p"       => [ 1920, 1080,    0,       128000,  2975872000, 2976000000,    60],

);

our $avail_stream_desc = join(", ", keys(%avail_stream_res));
our $resolution = "720p";
my $list_streams = 0;

our $usage = "$0  # modulates a Layer 3 CX to emulate a video server
  --mgr        {hostname | IP}
  --mgr_port   {ip port}
  --tx_style   { constant | bufferfill }
  --cx_name    {name}
  --set_tx     {A|B}          # which side is emulating the server,
    # default $tx_side
  --min_tx     {speed in bps}
  --max_tx     {speed in bps|SAME}
  --buf_size   {kilobytes}  # fill a buffer at max_tx for this long

    # default $frame_rate
  --stream_res {$avail_stream_desc}
  --list_streams # show stream bps table and exit
    # default $resolution
  --log_cli {0|1}
";
#  --frame_rate {$frame_rates_desc} # not really applicable
# the stream resolution (kbps) is really a better burn rate

my $show_help = 0;

if (@ARGV < 2) {
   print $usage;
   exit 0;
}
GetOptions
(
   'help|h'             => \$show_help,
   'mgr|m=s'            => \$::lfmgr_host,
   'mgr_port|p=i'       => \$::lfmgr_port,
   'log_cli=s{0,1}'     => \$log_cli,
   'tx_style|style=s'   => \$::tx_style,
   'cx_name|e=s'        => \$::cx_name,
   'set_tx|side|s=s'    => \$::tx_side,
   'min_tx=i'           => \$::min_tx,
   'max_tx=i'           => \$::max_tx,
   'buf_size|buf=i'     => \$::buf_size,
   'stream_res=s'       => \$::stream_res,
   'list_streams'       => \$list_streams,
) || die($::usage);


if ($show_help) {
   print $usage;
   exit 0;
}

if ($list_streams) {
  print "Predefined Video Streams\n";
  print "=" x 72;
  print "\n";
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
    printf("[ %15s ]  %5s x %5s using %13s", $key, $x, $y, $bps);
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


die ("Please provide cx_name")
  unless((defined $::cx_name) && ("" ne $::cx_name));
# print out choices for now
print $::utils->doAsyncCmd($::utils->fmt_cmd("show_cx", "all", $::cx_name));
#