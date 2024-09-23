#!/usr/bin/perl -w

# Follow these message through journalctl using this technique:
#
#   Read from a pipe or a fifo:
#       sudo ./loadmon | ./parse_loadmon.pl
#
#       mkfifo /tmp/load.fifo
#       ./parse_loadmon.pl < /tmp/load.fifo
#       sudo ./loadmon > /tmp/load.fifo
#
#   Loadmon output is now longer than journalctl line limits, so the
#   below example will not work:
#   sudo ./loadmon.pl | logger -t loadmon
# ...new terminal...
#   watch -n15 'journalctl --since "20 sec ago" -t loadmon | ./parse_loadmon.pl'

#

use strict;
use warnings;
use diagnostics;
use JSON::Parse qw(parse_json);
use Data::Dumper;
use Time::Local;
use Date::Parse;
use DateTime;

$| = 1;

sub mb {
    my $kb = shift;
    if ($kb < 1024) {
        return "${kb}KB";
    }
    my $mb = $kb / 1024;
    return sprintf("%0.1f MB", $mb);
}

my %mem_histo = ();
my $epoch = 0;
my $prev_epoch = 0;
my %MONTHS = (
    "Jan" => 0,
    "Feb" => 1,
    "Mar" => 2,
    "Apr" => 3,
    "May" => 4,
    "Jun" => 5,
    "Jul" => 6,
    "Aug" => 7,
    "Sep" => 8,
    "Oct" => 9,
    "Nov" => 10,
    "Dec" => 11,
);

while (my $line=<STDIN>) {
    chomp $line;
    # print "line[$line]\n";
    my $lc_pos = index($line, '[{');
    # print "lc at $lc_pos\n";
    next if ($lc_pos < 0);
    # more informative not to have the current date but the date of the record
    # print `date`;
    my ($date_str) = $line =~ /^(\w+ \d+ \d+:\d+:\d+) /;
    print "Date: $date_str \n";
    my $prev_epoch = $epoch;
    my $epoch = 0;
    my ($month, $day, $hour, $min, $sec) = $date_str =~ /(\w+) (\d+) (\d+):(\d+):(\d+)/;
    if (defined $month && defined $day && defined $hour && defined $min && defined $sec) {
        if (! exists $MONTHS{$month}) {
            die("WTF: month[$month]");
        }
        $epoch = str2time($date_str);
        # $epoch = timelocal_modern($sec, $min, $hour, undef, $MONTHS{$month}, 2024);
        if (defined $epoch && $epoch > $prev_epoch) {
            $mem_histo{$epoch} = 0;
        }
        else {
            print STDERR "Unable to parse date [$date_str]\n";
        }
    }
    else {
        print STDERR "Date_str lacks a column: $date_str\n";
    }
    my $loadmon_line = substr($line, $lc_pos);
    # print "LOADMON_LINE: $loadmon_line\n";
    # detect bug where "tt_threads:X}{" and add comma
    $loadmon_line =~ s/\}\{/},{/mg;
    my $ra_loadmon = parse_json($loadmon_line);
    #print Dumper$ra_loadmon);

    for my $rh_item ( @$ra_loadmon) {
        next if ($rh_item == 0);
        if (defined($rh_item->{basename})) {
            printf("%-15s: %3d pids (%4d thr) use %9s memory\n",
                    $rh_item->{basename},
                    $rh_item->{num_pids},
                    $rh_item->{total_threads},
                    mb($rh_item->{total_mem_KB}));
        }
        else {
            printf("TOTALS : %11d pids (%4d thr) use %9s ram and %7d FH\n\n",
                    $rh_item->{tt_num_pids},
                    $rh_item->{tt_threads},
                    mb($rh_item->{tt_mem_kb}),
                    $rh_item->{tt_fh});
            if ($epoch > 0) {
                $mem_histo{$epoch} = $rh_item->{tt_mem_kb};
            }
        }
    }
}
# determine average of the values in the array
my $average_kbytes = 0;
my $t_sum = 0;
my $min_kbytes = 0;
my $max_kbytes = 0;
for my $epoch (sort keys %mem_histo) {
    $t_sum += $mem_histo{$epoch};
    if ($min_kbytes == 0) {
        $min_kbytes = $mem_histo{$epoch};
        $max_kbytes = $mem_histo{$epoch};
        next;
    }
    $min_kbytes = $mem_histo{$epoch} if ($mem_histo{$epoch} < $min_kbytes);
    $max_kbytes = $mem_histo{$epoch} if ($max_kbytes < $mem_histo{$epoch});
}
$average_kbytes = int($t_sum / (keys(%mem_histo)));
my $relative_zero = $average_kbytes - $min_kbytes;

print "ave_kbytes:$average_kbytes, $min_kbytes, $max_kbytes, z:$relative_zero\n";
# my $prev_kbytes = $average_kbytes;
my $delta_kbytes = 0;
my %condensed_histo = ();
my $prev_bars = "";
my $prev_kbytes = 0;
for my $epoch (sort keys %mem_histo) {
    # $delta_kbytes = $mem_histo{$epoch} - $relative_zero - $min_kbytes;
    $delta_kbytes = 1 + $mem_histo{$epoch} - $min_kbytes;

    my $bars_hgt = int(log($delta_kbytes));
    my $bars = ("#" x $bars_hgt);
    my $formated_line = sprintf("%10s %s", mb($delta_kbytes), $bars);

    if ($bars ne $prev_bars) {
        $condensed_histo{$epoch} = $formated_line;
        $prev_bars = $bars;
        $prev_epoch = $epoch;
    }
    elsif ($prev_kbytes < $delta_kbytes) {
        delete $condensed_histo{$prev_epoch};
        $condensed_histo{$epoch} = $formated_line;
        $prev_kbytes = $delta_kbytes;
        $prev_epoch = $epoch;
    }
}
for my $epoch (sort keys %condensed_histo) {
    my $line = DateTime->from_epoch($epoch);
    $line .= " ".$condensed_histo{$epoch}."\n";
    print $line;
}
