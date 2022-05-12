#!/usr/bin/perl -w
use strict;
use warnings;
use diagnostics;
use JSON::Parse qw(parse_json);
use Data::Dumper;

sub mb {
    my $kb = shift;
    if ($kb < 1024) {
        return "${kb}KB";
    }
    my $mb = $kb / 1024;
    return sprintf("%0.1fMB", $mb);
}

foreach my $line (<>) {
    chomp $line;
    #print "line[$line]\n";
    my $lc_pos = index($line, '[{');
    # print "lc at $lc_pos\n";
    next if ($lc_pos < 0);
    my $loadmon_line = substr($line, $lc_pos);
    my $ra_loadmon = parse_json($loadmon_line);
    #print Dumper($ra_loadmon);

    for my $rh_item ( @$ra_loadmon) {
        next if ($rh_item == 0);
        if (defined($rh_item->{basename})) {
            printf("%-15s: %3d pids use %9s memory\n",
                    $rh_item->{basename},
                    $rh_item->{num_pids},
                    mb($rh_item->{total_mem_KB}));
        }
        else {
            printf("TT pids: %5d use %9s ram and %-7d FH\n\n",
                    $rh_item->{tt_num_pids},
                    mb($rh_item->{tt_mem_kb}),
                    $rh_item->{tt_fh});
        }
    }
}
