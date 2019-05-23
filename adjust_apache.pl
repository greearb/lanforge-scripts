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
@idhunks = undef;
@hunks = undef;
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
my $removed = 0;
for (my $i =$#host_lines-1; $i>=0; $i--) {
   my $line = $host_lines[$i];
   if ($line =~ /$MgrHostname/) {
     splice(@host_lines, $i, 1);
     $removed++;
   }
   if (($removed < 2) && ( $line eq "" || $line eq "\n")) {
     splice(@host_lines, $i, 1);
     $removed++;
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
my @places_to_check = (
   "/etc/apache2/apache2.conf",
   "/etc/apache2/ports.conf",
   "/etc/apache2/sites-available/0000-default.conf",
   "/etc/httpd/conf/http.conf",
   "/etc/httpd/conf/httpd.conf",
   "/etc/httpd/conf.d/ssl.conf",
);
foreach my $file (@places_to_check) {
   if ( -f $file) {
      print "Checking $file...\n";
      my @lines = `cat $file`;
      chomp @lines;
      # we want to match Listen 80$ or Listen 443 https$
      # we want to replace with Listen lanforge-mgr:80$ or Listen lanforge-mgr:443 https$
      @hunks = grep { /^\s*Listen\s+(?:80|443) */ } @lines;
      if (@hunks) {
         my $edited = 0;
         my @newlines = ();
         @hunks = (@hunks, "\n");
         print "Something to change in $file\n";
         print "These lines are interesting:\n";
         print join("\n", @hunks);
         foreach my $confline (@lines) {
            if ($confline =~ /^\s*Listen\s+(?:80|443) */) {
               $confline =~ s/Listen /Listen ${MgrHostname}:/;
               print "$confline\n";
            }
            push @newlines, $confline;
            $edited++ if ($confline =~ /# modified by lanforge/);
         }
         push(@newlines, "# modified by lanforge\n") if ($edited == 0);
         
         die ($!) unless open($fh, ">", $file);
         print $fh join("\n", @newlines);
         close $fh;
      }
      else {
         print "Nothing to change in $file\n";
      }
   }
} # ~for places_to_check

#
