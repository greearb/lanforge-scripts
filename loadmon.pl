#!/usr/bin/perl -w
#
# Log the traffic generating processing processes that LANforge creates
# This script will increase system logging usage (journalctl via logger)
# so if you need to add runtime constraints for disk usage, please add these
# runtime settings to you /etc/systemd/journald.conf file:
#   SystemMaxUse=100M
#   RuntimeMaxUse=1024M
#   RuntimeKeepFree=500M
#   RuntimeMaxFiles=5
#   RuntimeMaxFileSize=256M
#
# Follow these message through journalctl using this technique:
#
#   sudo ./loadmon.pl | logger -t loadmon
# ...new terminal...
#   watch -n15 'journalctl --since "20 sec ago" -t loadmon | ./parse_loadmon.pl'
#

use diagnostics;
use warnings;
use strict;
use Getopt::Long;
use POSIX;
use Data::Dumper;

$| = 1;

package main;

our $QQ=q{"};
our $Q=q{'};
our $LC=q({);
our $RC=q(});

our $do_fork = 0;
our $default_interval = 30;
our $interval = -1;
our $do_syslog = 0;
my $help = 0;

our @prog_names = (
    "btserver",
    "curl",
    "dhclient",
    "dnsmasq",
    "hostapd",
    "httpd",
    "iw",
    "java",
    "l4helper",
    # "logchopper",
    "nginx",
    "perl",
    "php-fpm",
    "pipe_helper",
    "vsftpd",
    "wget",
    "wpa_cli",
    "wpa_supplicant",
);
our %monitor_map = ();

## - - - Define loadmon - - - ##
package loadmon;
sub new {
    my $class = shift;
    my ( $basename ) = @_;
    my $self = {
        basename => $basename,
        ra_pid_list => [],
        total_mem => 0,
        total_fh => 0,
        total_thr => 0,
    };
    bless $self, $class;
    return $self;
}

sub monitor {
    my $self = shift;
    $self->{total_mem} = 0;
    $self->{total_fh} = 0;
    $self->{total_threads} = 0;

    my $cmd = qq(pgrep -f $self->{basename});
    # print "CMD[$cmd]\n";
    my @lines = `$cmd`;
    chomp(@lines);
    # print Data::Dumper->Dump(\@lines);
    $self->{ra_pid_list} = [];
    splice @{$self->{ra_pid_list}}, 0, 0, @lines;
    if ( scalar( @{$self->{ra_pid_list}} ) < 1) {
        return;
    }
    # print Data::Dumper->Dump(['ra_pid_list', $self->{ra_pid_list}] ), "\n";
    my $pidlist = join(" ", @{$self->{ra_pid_list}});
    $cmd = qq(echo $pidlist | xargs ps -o rss -p | tail -n+2);
    # print "CMD2: $cmd\n";
    my @mem_lines=`$cmd`;
    chomp(@mem_lines);
    #print Data::Dumper->Dump(['mem_lines', \@mem_lines]), "\n";
    for my $mem (@mem_lines) {
        $self->{total_mem} += int($mem);
    }

    for my $pid (@{$self->{ra_pid_list}}) {
        next unless ( -d "/proc/$pid/fd" );
        $cmd = "ls /proc/$pid/fd 2>/dev/null | wc -l";
        @lines=`$cmd`;
        chomp(@lines);
        # print Data::Dumper->Dump(['fh_lines', \@lines]), "\n";
        if (@lines > 0 ) {
            $self->{total_fh} += int($lines[0]);
        }
        $cmd = "ls /proc/$pid/task/ 2>/dev/null | wc -l";
        my $threads = `$cmd`;
        chomp $threads;
        $self->{total_threads} += int($threads);
    }

    #die("testing");
}

sub report {
    my ($self, $fh) = @_;
    my $num_pids = 0 + @{$self->{ra_pid_list}};

    # print Data::Dumper->Dump(['report', $self] ), "\n";
    if ($num_pids < 1) {
        # print $fh "0";
        return;
    }
    if (!$fh) {
        $fh = *STDOUT;
    }
    print $fh qq(${LC}"basename":"$self->{basename}",);
    print $fh qq("num_pids":$num_pids,);
    print $fh qq("total_mem_KB":$self->{total_mem},);
    print $fh qq("total_fh":$self->{total_fh},);
    print $fh qq("total_threads":$self->{total_threads}${RC});
}
1;
## - - - End loadmon - - - ##

## - - - Define main - - - ##
package main;

sub print_totals {
    my $fh = shift;
    if (!$fh) {
        $fh = *STDOUT;
    }
    my $tt_num_pids = 0;
    my $tt_mem_kb = 0;
    my $tt_fh = 0;
    my $tt_threads = 0;
    for my $name (@main::prog_names) {
        my $monitor = $main::monitor_map{$name};
        #print Data::Dumper->Dump(["mm_name", $monitor ]);
        my $ra_pl = $monitor->{ra_pid_list};
        #print Data::Dumper->Dump(["ra_pl", $ra_pl]);
        $tt_num_pids += @$ra_pl;
        if (defined $main::monitor_map{$name}->{total_mem}) {
            $tt_mem_kb += $main::monitor_map{$name}->{total_mem};
        }
        $tt_fh += $main::monitor_map{$name}->{total_fh};
        $tt_threads += $main::monitor_map{$name}->{total_threads};
    }
    print $fh qq(${LC}"tt_num_pids":$tt_num_pids, "tt_mem_kb":$tt_mem_kb, "tt_fh":$tt_fh, "tt_threads":$tt_threads${RC});
}

sub mainloop {
    my ($_syslog, $_interv) = @_;
    my $out_fh;
    if ($_syslog) {
        open($out_fh, "|-", "systemd-cat -t loadmon")
            or die("Unable to open systemd-cat: $!");
    }
    else {
        $out_fh = *STDOUT;
    }

    while (1) {
        print $out_fh '[';
        for my $name (@main::prog_names) {
            my $lmonitor = $monitor_map{$name};
            # print "$name ";
            $lmonitor->monitor();
            $lmonitor->report(*$out_fh);
            # print ",";
        }
        print_totals(*$out_fh);
        print $out_fh "]\n";
        sleep($_interv);
    }
}

## - - -
#           M A I N
## - - -
for my $name (@main::prog_names) {
    $monitor_map{$name} = loadmon->new($name);
}

my $usage = qq{$0 # utility to record system load
  --interval <seconds>      # default 30 sec
  --syslog                  # report results to syslog/journalctl
  --background              # place self into background
  Pipe this to syslog using "| logger -t loadmon" or better yet:
  "| systemd-cat -t loadmon" or use --syslog.
  Format this data using journalctl:
    journalctl -t loadmon | tail -1 | ./parse_loadmon.pl
};

if (! GetOptions(
    'background' => \$do_fork,
    'interval=i' => \$interval,
    'syslog'     => \$do_syslog,
    'help'       => \$help)
) {
    print $usage;
    exit 1;
}
if ($help) {
    print $usage;
    exit 0;
}

if ($interval < 1) {
    $interval = $default_interval;
}
if ($do_fork) {
    my $pid = fork;
    die "Failure to fork: $!" unless defined $pid;

    if ($pid == 0) {
        mainloop($do_syslog, $interval);
    }
    else {
        print STDERR "Placing progress in background...\n";
    }
    exit;
}
else {
    print STDERR "Monitor output to STDOUT...\n";
    mainloop($do_syslog, $interval);
}
#
