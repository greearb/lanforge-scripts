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
my $MgrHostname = `cat /etc/hostname`;
chomp($MgrHostname);
print "Will be setting hostname to $MgrHostname\n";
sleep 3;

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
print "LANforge config states mgt_dev $configv{'mgt_dev'}\n";

if ( ! -d "/sys/class/net/$configv{'mgt_dev'}") {
   print "Please run lfconfig again with your updated mgt_port value.\n";
   exit(1);
}
my $ipline = `ip -o a show $configv{"mgt_dev"}`;
#print "IPLINE[$ipline]\n";
my ($ip) = $ipline =~ / inet ([0-9.]+)(\/\d+)? /g;
die ("No ip found for mgt_dev; your config.values file is out of date: $!")
   unless ((defined $ip) && ($ip ne ""));

print "ip: $ip\n";

# This must be kept in sync with similar code in lf_kinstall.
my $fname = "/etc/hosts";
if (-f "$fname") {
  my @lines = `cat $fname`;
  open(FILE, ">$fname") or die "Couldn't open file: $fname for writing: $!\n\n";
  my $foundit = 0;
  my $i;
  chomp(@lines);
  # we want to consolidate the $ip $hostname entry for MgrHostname
  my @newlines = ();
  my %more_hostnames = ("lanforge-srv" => 1);
  my $new_entry = "$ip ";
  my $blank = 0;
  my $was_blank = 0;

  for my $ln (@lines) {
    $was_blank = $blank;
    $blank = ($ln =~ /^\s*$/) ? 1 : 0;
    next if ($blank && $was_blank);
    next if ($ln =~/^$ip $MgrHostname$/);
    next if ($ln =~ /^###-LF-HOSTAME-NEXT-###/); # old typo
    next if ($ln =~ /^###-LF-HOSTNAME-NEXT-###/);
    if ($ln =~ /\b($MgrHostname|lanforge-srv|$ip)\b/) {
       print "Matching LINE $ln\n";
       my @hunks = split(/\s+/, $ln);
       for my $hunk (@hunks) {
         #print "HUNK{$hunk} ";
         next if ($hunk =~ /^($ip|lanforge-srv|$MgrHostname)$/);
         $more_hostnames{$hunk} = 1;
       }
       next;
    }
    print "ok ln[$ln]\n";
    push(@newlines, $ln);
  }
  push(@newlines, "###-LF-HOSTNAME-NEXT-###");

  for my $ln (@newlines) {
    print FILE "$ln\n";
  }

  print FILE "$ip $MgrHostname";
  for my $name (keys %more_hostnames) {
    print FILE " $name";
  }
  print FILE "\n\n";
  close FILE;
}

my $local_crt ="";
my $local_key ="";
my $hostname_crt ="";
my $hostname_key ="";
# check for hostname shaped cert files
if ( -f "/etc/pki/tls/certs/localhost.crt") {
   $local_crt = "/etc/pki/tls/certs/localhost.crt";
}
if ( -f "/etc/pki/tls/private/localhost.key") {
   $local_key = "/etc/pki/tls/private/localhost.key";
}

if ( -f "/etc/pki/tls/certs/$MgrHostname.crt") {
   $hostname_crt = "/etc/pki/tls/certs/$MgrHostname.crt";
}
if ( -f "/etc/pki/tls/private/$MgrHostname.key") {
   $hostname_key = "/etc/pki/tls/private/$MgrHostname.key";
}

# grab the 0000-default.conf file
my @places_to_check = (
   "/etc/apache2/apache2.conf",
   "/etc/apache2/ports.conf",
   "/etc/apache2/sites-available/000-default.conf",
   "/etc/apache2/sites-available/0000-default.conf",
   "/etc/httpd/conf/http.conf",
   "/etc/httpd/conf/httpd.conf",
   "/etc/httpd/conf.d/ssl.conf",
   "/etc/httpd/conf.d/00-ServerName.conf",
);
foreach my $file (@places_to_check) {
   if ( -f $file) {
      print "Checking $file...\n";
      my @lines = `cat $file`;
      chomp @lines;
      # we want to match Listen 80$ or Listen 443 https$
      # we want to replace with Listen lanforge-mgr:80$ or Listen lanforge-mgr:443 https$
      @hunks = grep { /^\s*(Listen|SSLCertificate)/ } @lines;
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
            elsif ($confline =~ /^\s*Listen\s+(?:[^:]+:(80|443)) */) {
               $confline =~ s/Listen [^:]+:/Listen ${MgrHostname}:/;
               print "$confline\n";
            }
            if ($confline =~ /^\s*SSLCertificateFile /) {
               $confline = "SSLCertificateFile $hostname_crt" if ("" ne $hostname_crt);
            }
            if ($confline =~ /^\s*SSLCertificateKeyFile /) {
               $confline = "SSLCertificateKeyFile $hostname_key" if ("" ne $hostname_key);
            }
            push @newlines, $confline;
            $edited++ if ($confline =~ /# modified by lanforge/);
         }
         push(@newlines, "# modified by lanforge\n") if ($edited == 0);

	 my $fh;
         die ($!) unless open($fh, ">", $file);
         print $fh join("\n", @newlines);
         close $fh;
      }
      else {
         print "Nothing looking like [Listen 80|443] in $file\n";
      }
   }
} # ~for places_to_check

#
