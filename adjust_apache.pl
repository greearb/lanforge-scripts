#!/usr/bin/perl

use strict;
use warnings;
use diagnostics;
use Carp;
use Data::Dumper;
use File::Temp qw(tempfile tempdir);
my $Q='"';
my $q="'";
my @idhunks = split(' ', `id`);
my @hunks = grep { /uid=/ } @idhunks;
die ("Must be root to use this")
   unless( $hunks[0] eq "uid=0(root)" );
@idhunks = undef;
@hunks = undef;
my $start_time = `date +%Y%m%d-%H%M%S`;
chomp($start_time);
# print( "start time: [$start_time]\n");

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
my $backup = "/etc/.hosts.$start_time";
`cp $fname $backup`;
my ($fh, $editfile) = tempfile( "t_hosts_XXXX", DIR=>'/tmp', SUFFIX=>'.txt');
if (-f "$fname") {
  my @lines = `cat $fname`;
  #open(FILE, ">$fname") or die "Couldn't open file: $fname for writing: $!\n\n";
  my $foundit = 0;
  my $i;
  # chomp is way to simplistic if we need to weed out \r\n characters as well
  #chomp(@lines);
  for( my $i=0; $i < @lines; $i++) {
     ($lines[$i]) = $lines[$i] =~ /^([^\r\n]+)\r?\n$/;
  }
  # we want to consolidate the $ip $hostname entry for MgrHostname
  my @newlines = ();
  my %more_hostnames = ();
  my $new_entry = "$ip ";
  #my $blank = 0;
  #my $was_blank = 0;
  my $counter = 0;
  my $debug = 0;
  if ((exists $ENV{"DEBUG"}) && ($ENV{"DEBUG"} eq "1")) {
     $debug = 1;
  }
  my %host_map = (
    "localhost.localdomain"     => "127.0.0.1",
    "localhost"                 => "127.0.0.1",
    "localhost4.localdomain4"   => "127.0.0.1",
    "localhost4"                => "127.0.0.1",
    "localhost.localdomain"     => "::1",
    "localhost"                 => "::1",
    "localhost6.loaldomain6"    => "::1",
    "localhost6"                => "::1",
    $MgrHostname                => $ip,
    "lanforge.localnet"         => "192.168.1.101",
    "lanforge.localdomain"      => "192.168.1.101",
  );
  my %comment_map = ();
  my %address_marker_map = ();
  my %address_map = (
     "127.0.0.1" => "localhost.localdomain localhost localhost4.localdomain4 localhost4",
     "::1" => "localhost.localdomain localhost localhost6.loaldomain6 localhost6",
     $ip => $MgrHostname,
     "192.168.1.101" => "lanforge.localnet lanforge.localdomain",
     );
  if ($debug){
      print Dumper(\%address_map);
      print Dumper(\%host_map);
  }

  my $prevname = "";
  my $previp = "";

  for my $ln (@lines) {
    next if (!(defined $ln));
    print "\nLN[$ln]\n" if ($debug);
    next if ($ln =~ /^\s*$/);
    next if ($ln =~ /^\s*#/);
    next if ($ln =~ /LF-HOSTAME-NEXT/); # old typo
    next if ($ln =~ /LF-HOSTNAME-NEXT/);
    my $comment = undef;
    print "PARSING IPv4 ln[$ln]\n" if ($debug);
    if ($ln =~ /#/) {
       ($comment) = $ln =~ /^[^#]+(#.*)$/;
       ($ln) = $ln =~ /^([^#]+)\s*#/;
       print "line with comment becomes [$ln]\n" if ($debug);
    }
    @hunks = split(/\s+/, $ln);
    my $middleip = 0;
    my $counter2 = -1;
    my $linehasip = 0;
    my $lfhostname = 0;
    if ((defined $comment) && ($comment ne "")) {
       $comment_map{$hunks[0]} = $comment;
    }
    for my $hunk (@hunks) {
      print "\n   HUNK",$counter2,"-:$hunk:- " if ($debug);
      $counter2++;
      next if ($hunk =~ /^localhost/);
      next if ($hunk =~ /^lanforge-srv$/);
      next if ($hunk =~ /^lanforge\.local(domain|net)$/);
      next if ($hunk =~ /^extra6?-\d+/);

      if ($hunk =~ /^\s*$/) {
        next;
      }

      if ($hunk =~ /^$ip$/) {
         $linehasip++;
         $lfhostname++;
      }
      elsif ($hunk =~ /^$MgrHostname$/) {
         $lfhostname++;
         $prevname = $hunk;
      }

      $previp = "" if (!defined($previp));

      if (($hunk =~ /^127\.0\.0\.1/)
         || ($hunk =~ /^192\.168\.1\.101/)
         || ($hunk =~ /^::1$/)){
         $previp = $hunk;
         $linehasip++;
      }
      elsif ($hunk =~ /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/) {
         $linehasip++;
         print " IP4($hunk)" if ($debug);
         if ($counter2 > 0) { # we're not first item on line
            $middleip++ if ($counter2 > 0);
            print "middle" if ($debug);
         }
         if (!(defined $address_map{$hunk})) {
            $address_map{$hunk} = "";
         }
         print "+IP4" if ($debug);

         if (("" ne $prevname) && ($counter2 > 0)) {
           print " hunk($hunk)prev($prevname)" if ($debug);
           $address_map{$hunk} .= " $prevname"
             if ($address_map{$hunk} !~ /\s*$prevname\s*/);
           # $host_map{$prevname} .= " $hunk";
           if ($host_map{$prevname} !~ /\b$hunk\b/) {
             $host_map{$prevname} .= " $hunk";
           }
         }
         $previp = $hunk;
      }
      elsif (($hunk =~ /[G-Zg-z]+\.?/) || ($hunk =~ /^[^:A-Fa-f0-9]+/)) {
         print " notIP($hunk)" if ($debug);
         $prevname = $hunk;
         if ($middleip) {
            print " middle($previp)" if ($debug);
            $address_map{$previp} .= " $hunk"
               if ($address_map{$previp} !~ /\b$hunk\b/);
            $prevname = $hunk;
            if ($host_map{$prevname} !~ /\b$hunk\b/) {
                $host_map{$prevname} .= " $previp";
            }
         }
         elsif ($linehasip) {
            print " prev($previp) hunk($hunk)" if ($debug);
            $address_map{$previp} .= " $hunk"
               if ($address_map{$previp} !~ /\s*$hunk\s*/);
            if ((defined $prevname) && (exists $host_map{$prevname}) && ($host_map{$prevname} !~ /\b$hunk\b/)) {
               $host_map{$hunk} .= " $previp";
            }
         }
         elsif ($lfhostname) {
            $more_hostnames{$hunk} = 1;
            if ($host_map{$prevname} !~ /\b$hunk\b/) {
               $host_map{$hunk} .= " $previp";
            }
         }
         else { # strange word
            if ("" eq $previp) {
               print " hunk($hunk) has no IP***" if ($debug);
               $more_hostnames{$hunk} = 1;
            }
            elsif ($address_map{$previp} !~ /\s*$hunk\s*/) {
               $address_map{$previp} .= " $hunk";
               if ($host_map{$prevname} !~ /\b$hunk\b/) {
                  $host_map{$hunk} .= " $previp";
               }
            }
         }
      }
      elsif (($hunk =~ /::/)
         || ($hunk =~ /[0-9A-Fa-f]+:/)) {
         print " hunk6($hunk)" if ($debug);
         $linehasip++;
         if (!(defined $address_map{$hunk})) {
            $address_map{$hunk} = "";
         }
         $previp = $hunk;
      }
      elsif ($address_map{$previp} !~ /\s*$hunk\s*/) { # is hostname and not an ip
         $address_map{$previp} .= " $hunk";
         if ($host_map{$prevname} !~ /\b$hunk\b/) {
            $host_map{$hunk} .= " $previp";
         }
      }
    } # ~foreach hunk
  } # ~foreach line

  if (($host_map{$MgrHostname} !~ /^\s*$/) && ($host_map{$MgrHostname} =~ /\S+\s+\S+/)) {
    print("Multiple IPs for this hostname: ".$host_map{$MgrHostname}."\n") if ($debug);
    my @iphunks = split(/\s+/, $host_map{$MgrHostname});
    print "Changing $MgrHostname for to $ip; line was <<$host_map{$MgrHostname}>> addrmap: <<$address_map{$ip}>>\n"
      if ($debug);
    $host_map{$MgrHostname} = $ip;
  }
  for my $name (sort keys %more_hostnames) {
     $address_map{$ip} .= " $name";
     print "NEWSTUFF $ip $address_map{$ip}\n" if ($debug);
  }

  # this might be premature
  unshift(@newlines, "192.168.1.101 ".$address_map{"192.168.1.101"});
  unshift(@newlines, "127.0.0.1  ".$address_map{"127.0.0.1"});
  unshift(@newlines, "::1  ".$address_map{"::1"});

  my %used_addresses=();

  delete($address_map{"192.168.1.101"});
  $used_addresses{"192.168.1.101"}=1;
  delete($address_map{"127.0.0.1"});
  $used_addresses{"127.0.0.1"}=1;
  delete($address_map{"::1"});
  $used_addresses{"::1"}=1;

  if ($debug) {
     print "# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n";
     print "\nAddress map\n";
     print Dumper(\%address_map);
     print "\nHost map\n";
     print Dumper(\%host_map);
     print "# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n";
     sleep 2;
  }

  # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
  # we want to maintain the original line ordering as faithfully as possible
  # ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
  for my $ln (@lines) {
    $ln = "" if (!(defined $ln));
    print "OLD[$ln]\n" if ($debug);
    # if we are comments or blank lines, preserve them
    next if ($ln =~ /LF-HOSTNAME-NEXT/);
    next if ($ln =~ /^$host_map{$MgrHostname}\s+/);
    if (($ln =~ /^\s*$/) || ($ln =~ /^\s*#/)) {
       push(@newlines, $ln);
       next;
    }
    @hunks = split(/\s+/, $ln);

    if (exists $address_map{$hunks[0]}) {
       if ((exists $address_marker_map{$hunks[0]})
            || (exists $used_addresses{$hunks[0]})) {
          print "already printed $hunks[0]\n" if ($debug);
          next;
       }
       my $comment = "";
       if (exists $comment_map{$hunks[0]}) {
          $comment = " $comment_map{$hunks[0]}";
       }
       push(@newlines, "$hunks[0] $address_map{$hunks[0]}$comment");
       $address_marker_map{$hunks[0]} = 1;
       next;
    }
    if (!(exists $used_addresses{$hunks[0]} )) {
       warn("untracked IP <<$hunks[0]>> Used addresses:\n");
       print Dumper(\%address_marker_map);
       print Dumper(\%used_addresses);
    }
  }
  if ($debug) {
     print "# ----- NEW ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n";
     for my $ln (@newlines) {
        print "$ln\n";
     }
  }

  #for my $key (sort keys %address_map){
  #   next if ($key eq $ip);
  #   if ($address_map{$key} =~ /\s*$MgrHostname\s*/) {
  #       print("SKIPPING $key / $address_map{$key}\n")
  #         if ($debug);
  #       next;
  #   }
  #   push(@newlines, $key."    ".$address_map{$key});
  #}
  push(@newlines, "###-LF-HOSTNAME-NEXT-###");
  push(@newlines, $ip."    ".$address_map{$ip});
  if ($debug) {
     print Dumper(\@newlines);
     sleep 5;
  }
  for my $ln (@newlines) {
    print $fh "$ln\n";
  }

  #print  "\n";
  close $fh;
  my $wc_edit_file = `wc -l < $editfile`;
  chomp($wc_edit_file);
  my $wc_orig_file = `wc -l < $backup`;
  if ( $wc_edit_file == 0) {
    print "Abandoning $editfile, it was blank.\n";
    exit;
  }
  if ( $wc_orig_file > $wc_edit_file ) {
    warn( "Original /etc/hosts file backed up to $backup\n");
    warn( "The new /etc/hosts file has ".($wc_orig_file - $wc_edit_file)."lines.\n");
    warn( "Press Ctrl-C to exit now.\n");
    sleep(2);
  }
  `cp $editfile /etc/hosts`;
} # ~if found file

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
if ( -d "/etc/httpd/conf.d") {
  die($!) unless open(FILE, ">", "/etc/httpd/conf.d/00-ServerName.conf");
  print FILE "ServerName $MgrHostname\n";
  #print FILE "Listen $MgrHostname:80\n";
  #print FILE "Listen $MgrHostname:443\n";
  close FILE;
}

#
