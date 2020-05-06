#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
use Data::Dumper;
my $Q='"';
my $q="'";
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
my $found_localhost = 0;
my $fname = "/etc/hosts";
if (-f "$fname") {
  my @lines = `cat $fname`;
  open(FILE, ">$fname") or die "Couldn't open file: $fname for writing: $!\n\n";
  my $foundit = 0;
  my $i;
  chomp(@lines);
  # we want to consolidate the $ip $hostname entry for MgrHostname
  my @newlines = ();
  my %more_hostnames = ();
  my $new_entry = "$ip ";
  #my $blank = 0;
  #my $was_blank = 0;
  my $counter = 0;
  #my $found_defaultip = 0;
  my %address_map = (
     "127.0.0.1" => "localhost.localdomain localhost localhost4.localdomain4 localhost4",
     "::1" => "localhost.localdomain localhost localhost6.loaldomain6 localhost6",
     $ip => $MgrHostname,
     "192.168.1.101" => "lanforge.localnet lanforge.localdomain",
     );
  print Dumper(\%address_map);
  my $prevname = "";
  my $previp = "";

  for my $ln (@lines) {
    print "\nLN[$ln]\n";
    next if ($ln =~ /^\s*$/);
    next if ($ln =~ /^###-LF-HOSTAME-NEXT-###/); # old typo
    next if ($ln =~ /^###-LF-HOSTNAME-NEXT-###/);

    print "PARSING IPv4 ln[$ln]\n";
    @hunks = split(/\s+/, $ln);
    my $middleip = 0;
    my $counter2 = -1;
    my $linehasip = 0;
    my $lfhostname = 0;
    for my $hunk (@hunks) {
      print "\n   ZUNK",$counter2,"-:$hunk:- ";
      $counter2++;
      next if ($hunk =~ /^localhost/);
      next if ($hunk =~ /^lanforge-srv\b/);
      next if ($hunk =~ /^lanforge\.local(domain|net)\b/);
      next if ($hunk =~ /^extra6?-\d+/);

      if (($hunk =~ /^$ip\b/)
         || ($hunk =~ /^$MgrHostname\b/)
         ){
         $linehasip++;
         $lfhostname++;
         $prevname = $hunk;
      }

      if (($hunk =~ /^127\.0\.0\.1/)
         || ($hunk =~ /^192\.168\.1\.101/)
         || ($hunk =~ /^::1\b/)
         ){
         $previp = $hunk;
         $linehasip++;
      }

      if ($hunk =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/) {
         $linehasip++;
         print " IP4($hunk)";
         $previp = $hunk;
         if ($counter2 > 0) { # we're not first item on line
            $middleip++ if ($counter2 > 0);
            print "MIDDLE";
         }
         if (!(defined $address_map{$hunk})) {
            $address_map{$hunk} = "";
         }
         print "+IP4";
         $previp = $hunk;
      }
      elsif (($hunk =~ /[G-Zg-z]+\.?/) || ($hunk =~ /^[^:A-Fa-f0-9]+/)) {
         print " notIP($hunk)";
         $prevname = $hunk;
         if ($middleip) {
            print " middle($previp)";
            $address_map{$previp} .= " $hunk"
               if ($address_map{$previp} !~ /\b$hunk\b/);
            $prevname = $hunk;
         }
         elsif ($linehasip) {
            print " prev($previp $hunk)";
            $address_map{$previp} .= " $hunk"
               if ($address_map{$previp} !~ /\b$hunk\b/);
         }
         elsif ($lfhostname) {
            $more_hostnames{$hunk} = 1;
         }
         else { # strange word
            print " hunk($hunk) has no IP***";
            if ("" eq $previp) {
               $more_hostnames{$hunk} = 1;
            }
            elsif ($address_map{$previp} !~ /\b$hunk\b/) {
               $address_map{$previp} .= " $hunk"
            }
         }
      }
      elsif (($hunk =~ /::/)
         || ($hunk =~ /[0-9A-Fa-f]+:/)) {
         print " hunk6($hunk)";
         $linehasip++;
         if (!(defined $address_map{$hunk})) {
            $address_map{$hunk} = "";
         }
         $previp = $hunk;
      }
      elsif ($hunk =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/) {
         print " hunk($hunk)prev($prevname)";
         $address_map{$hunk} .= " $prevname"
            if ($address_map{$hunk} !~ /\b$prevname\b/);
         $previp = $hunk;
      }
      elsif ($address_map{$previp} !~ /\b$hunk\b/) { # is hostname and not an ip
         $address_map{$previp} .= " $hunk";
      }

    } # ~foreach hunk

  } # ~foreach line

  for my $name (sort keys %more_hostnames) {
     $address_map{$ip} .=" $name";
     print "NEWSTUFF $ip $address_map{$ip}\n";
  }

  print Dumper(\%address_map);

  unshift(@newlines, "192.168.1.101 ".$address_map{"192.168.1.101"});
  unshift(@newlines, "127.0.0.1  ".$address_map{"127.0.0.1"});
  unshift(@newlines, "::1  ".$address_map{"::1"});

  delete($address_map{"192.168.1.101"});
  delete($address_map{"127.0.0.1"});
  delete($address_map{"::1"});

  for my $key (sort keys %address_map){
     next if ($key eq $ip);
     push(@newlines, $key."    ".$address_map{$key});
  }
  push(@newlines, "###-LF-HOSTNAME-NEXT-###");
  push(@newlines, $ip."    ".$address_map{$ip});
  print Dumper(\@newlines);
  sleep 5;
  for my $ln (@newlines) {
    print FILE "$ln\n";
  }

  #print FILE "$ip $MgrHostname";
  #for my $name (keys %more_hostnames) {
  #  print FILE " $name";
  #}
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
