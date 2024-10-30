package parse_heatmon.pl;
use strict;
use warnings FATAL => 'all';

sub parse_line {
    my $line = $_;

     my ($date, $data) = $line =~ /(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) +(\d+:\d+:\d+) \S+ heatmon\[\d+\]: (\[\{.*\}\])/;
}
1;

package main;
