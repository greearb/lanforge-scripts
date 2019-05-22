#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
use Data::Dumper;

my @idhunks = split(' ', `id`);
my @hunks = grep { /uid=/ } @idhunks;
die ("Must be root to use this")
   unless( $hunks[0] eq "uid=0(root)" );

my $MgrHostname = "lanforge-srv";

my $config_v = "/home/lanforge/config.values";
# grab the config.values file
die ("Unable to find $config_v" )
   unless ( -f $config_v);

my @configv_lines = `cat $config_v`;
die ("Probably too little data in config.values")
   unless (@configv_lines > 5);
my %configv = ();
foreach my $line (@configv_lines) {
   my ($key, $val) = $line =~ /^(\S+)\s+(.*)$/;
   $configv{$key} = $val;
}
die ("Unable to parse config.values")
   unless ((keys %configv) > 5);
die ("no mgt_dev in config.values")
   unless defined $configv{'mgt_dev'};
print "Found mgt_dev $configv{'mgt_dev'}\n";

my $ipline = `ip -o a show $configv{"mgt_dev"}`;
#print "IPLINE[$ipline]\n";
my ($ip) = $ipline =~ / inet ([0-9.]+)(\/\d+)? /g;
die ("No ip found for mgt_dev")
   unless ((defined $ip) && ($ip ne ""));

print "ip: $ip\n";
my @host_lines = `cat /etc/hosts`;
chomp (@host_lines);
@host_lines = ("127.0.0.1 localhost", @host_lines)
   if (@host_lines < 1);
for (my $i =$#host_lines-1; $i>=0; $i--) {
   my $line = $host_lines[$i];
   if ($line =~ /$MgrHostname/) {
     splice(@host_lines, $i, 1);
   }
}
@host_lines = (@host_lines, ("$ip $MgrHostname", "\n"));
my $dt = `date +%Y%m%d-%H%M%s`;
chomp $dt;
print "dt[$dt]\n";
print "cp /etc/hosts /etc/.hosts.$dt\n";
print "=======================================\n";
print join("\n", @host_lines);
print "=======================================\n";
die ("Unable to write to /etc/hosts: $!")
   unless open(my $fh, ">", "/etc/hosts");
print $fh join("\n", @host_lines);
close $fh;

print "Updated /etc/hosts\n";
# grab the 0000-default.conf file
