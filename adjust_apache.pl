#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
use Data::Dumper;

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
chomp (@host_lines0;
@host_lines = ("127.0.0.1 localhost", @host_lines)
   if (@host_lines < 1);
for (my $i =$#host_lines-1; $i>=0; $i--) {
   print "$i\n";
   my $line = $host_lines[$i];
   if ($line =~ /lanforge-mgr/) {
      
   }
}
@host_lines = (@host_lines, 


# grab the 0000-default.conf file
