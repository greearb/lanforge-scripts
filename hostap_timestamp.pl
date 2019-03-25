#!/usr/bin/perl

use POSIX qw( strftime );

while (<>) {
  my $ln = $_;
  if ($ln =~ /^(\d+)\.(\d+): (.*)/) {
    my $time_sec = $1;
    my $usec = $2;
    my $rest = $3;
    my $usec_pad = sprintf("%06d", $usec);
    my $dt = strftime("%Y-%m-%d %H:%M:%S", localtime($time_sec));
    print "$dt.$usec_pad $rest\n";
  }
  else {
    print $ln;
  }
}
