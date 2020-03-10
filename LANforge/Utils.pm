package LANforge::Utils;
use strict;
use warnings;
use Carp;
use Net::Telnet;
$| = 1;
#$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
#$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
if ($ENV{DEBUG}) {
  use Data::Dumper;
}

##################################################
## the object constructor                       ##
## To use:  $ep = LANforge::Utils->new();       ##
##     or:  $ep2 = $ep->new();                  ##
##################################################

sub new {
   my $proto = shift;
   my $class = ref($proto) || $proto;
   my $self  = {};

   $self->{telnet}          = undef;
   $self->{cli_send_silent} = 0;
   $self->{cli_rcv_silent}  = 0;
   $self->{error}           = "";
   $self->{async_waitfor}   = '/btbits>> $/';
   $self->{prompt}          = '/btbits>> $/';

   bless( $self, $class );
   return $self;
}

sub connect {
   my ($self, $host, $port) = @_;
   my $t = new Net::Telnet(Prompt   => '/btbits>> $/',
                           Timeout  => 2);
   $self->{telnet} = \$t;
   $t->open(Host     => $host,
            Port     => $port,
            Timeout  => 2);
   $t->max_buffer_length(16 * 1024 * 1000); # 16 MB buffer
   $t->waitfor($self->{prompt});
   $t->print("set_flag brief 0"); # If we leave it brief, RSLT prompt is not shown.
   if ($self->isQuiet()) {
      if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
         $self->cli_send_silent(0);
         $self->log_cli("# $0 ".`date "+%Y-%m-%d %H:%M:%S"`);
      }
      else {
         $self->cli_send_silent(1); # Do not show input to telnet
      }
      $self->cli_rcv_silent(1);  # Repress output from telnet
   }
   else {
      $self->cli_send_silent(0); # Show input to telnet
      $self->cli_rcv_silent(0);  # Show output from telnet
   }
   return ${$self->{telnet}};
}

sub telnet {
  my $self = shift;

  die("Utils::telnet -- telnet object undefined")
    if (!(defined $self->{telnet}));
  my $t = ${$self->{telnet}};
  $t->max_buffer_length(50 * 1024 * 1024);
  $t->print("\n");
  $t->waitfor($self->{prompt});

  return $t;
}

# This submits the command and returns the success/failure
# of the command.  If the results from the command are not
# immediately available (say, if LANforge needs to query a remote
# resource for endpoint stats, then that results may NOT be
# in the returned string.  In that case, you must wait for the
# prompt to be seen, so use the doAsyncCmd below instead.
# doCmd is good for rapidly doing lots of configuration without
# waiting for each step (port creation, for example) to fully
# complete.
sub doCmd {
   my $self = shift;
   my $cmd  = shift;
   print "CMD[[$cmd]]\n";
   my $t = ${$self->{telnet}};
   if ( !$self->cli_send_silent() || (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "")) {
      $self->log_cli($cmd);
   }
   $t->print($cmd);

   my @rslt = $t->waitfor('/ >>RSLT:(.*)/');
   if ( !$self->cli_rcv_silent() ) {
      print "**************\n@rslt\n................\n\n";
   }
   return join( "\n", @rslt );
}

#  This will wait for the prompt, not just for the results.
# Use this instead of doCmd if you are unsure.
sub doAsyncCmd {
   my $self = shift;
   my $cmd  = shift;
   my $t    = $self->telnet();
   my @rv   = ();

   if ( !$self->cli_send_silent() || (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "")) {
      $self->log_cli($cmd);
   }
   $t->print($cmd);
   my @rslt = $t->waitfor('/ \>\>RSLT:(.*)/');
   my @rslt2 = $t->waitfor( $self->async_waitfor() );
   @rv = ( @rslt, @rslt2 );

   if ( !$self->cli_rcv_silent() ) {
      print "**************\n @rv \n................\n\n";
   }
   return join( "\n", @rv );
} # ~doAsyncCmd

sub normalize_bucket_hdr {
  my $self  = shift;
  my $amt = shift;
  my $rv = "Min Max Avg ";
  my $i;
  for ($i = 0; $i<$amt; $i++) {
    if ($i == 0) {
      $rv .= "0-0 ";
    }
    else {
      $rv .= 2**($i-1) . "-" . (2**($i) - 1) . " ";
    }
  }
  return $rv;
}

# Normalize lat1, taking peer latency (lat2) into account for negative latency and such.
sub normalize_latency {
  my $self = shift;
  my $lat1 = shift;
  my $lat2 = shift;

  #print "lat1 -:$lat1:-\n";
  #print "lat2 -:$lat2:-\n";

  my $min1 = 0;
  my $min2 = 0;

  # Looks like this: 5 -:5:- 6  [ 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ] (1)
  if ($lat1 =~ /(\S+)\s+-:(\S+):-\s+(\S+)\s+\[\s+(.*)\s+\]\s+\((\S+)\)/) {
    $min1 = $1;
  }
  if ($lat2 =~ /(\S+)\s+-:(\S+):-\s+(\S+)\s+\[\s+(.*)\s+\]\s+\((\S+)\)/) {
    $min2 = $1;
  }

  # For instance, min1 is -5, min2 is 25, rt-latency is 20.
  # Adjust lat1 by (25 - -5) / 2
  # For instance, min1 is 25, min2 is -5, rt-latency is 20.
  # Adjust lat1 by (-5 -25) / 2
  #print "min1: $min1  min2: $min2  half: " . int(($min2 - $min1) / 2) . "\n";
  # So, the above seems nice, but often we have a small negative value due to
  # clock drift in one direction, and large latency in the other (due to real one-way latency)
  # So, we will just adjust enough to make the smallest value positive.
  my $adjust = 0;
  if ($min1 < 0) {
    $adjust = -$min1;
  }
  elsif ($min2 < 0) {
    $adjust = -$min2;
  }
  return $self->normalize_bucket($lat1, $adjust);
}

sub normalize_bucket {
  my $self = shift;
  my $line = shift;
  my $adjust = shift;

  #print "line -:$line:-\n";

  # Looks like this: 5 -:5:- 6  [ 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ] (1)
  if ($line =~ /(\S+)\s+-:(\S+):-\s+(\S+)\s+\[\s+(.*)\s+\]\s+\((\S+)\)/) {
    my $min = $1;
    my $avg = $2;
    my $max = $3;
    my $bks = $4;
    my $width = $5; # Assumes one currently
    if (!($width eq "1")) {
      return $line;
    }
    else {
      my @bkts = split(/\s+/, $bks);
      @bkts = (@bkts, "0");
      my $i;
      my $rv = ($min + $adjust) . " " . ($max + $adjust) . " " . ($avg + $adjust) . " ";
      #print "bkts len: " . @bkts . "\n";
      my @nbkts = (0) x (@bkts);
      for ($i = 0; $i<@bkts; $i++) {
	# Figure out the bkt range
	my $minv = 0;
	my $maxv = 2 ** $i;
	if ($i > 0) {
	  $minv = 2 ** ($i - 1);
	}
	# Adjust by the min value, which is treated as an offset
	$minv += $min;
	$maxv += $min;

	# And adjust based on round-trip time to deal with clock lag
	$minv += $adjust;
	$maxv += $adjust;

	# And now find the normalized bucket this fits in
	#print "maxv: $maxv\n";
	my $z;
	my $idx = 0;
	for ($z = 1; $z < 32; $z++) {
	  if ($maxv < (2 ** $z)) {
	    #print "maxv: $maxv  z: $z  2^$z: " . 2 ** $z . + "\n";
	    $idx = $z;
	    # Everything else falls in the last bucket
	    if ($idx >= @bkts) {
	      $idx = (@bkts - 1);
	    }
	    last;
	  }
	}

	#print "idx: $idx i: $i ";
	#print "nbkts: " . $nbkts[$idx];
        #print " bkts: " . $bkts[$i] . "\n";
	my $nv = $nbkts[$idx] + $bkts[$i];
	@nbkts[$idx] = $nv;
      }

      for ($i = 0; $i < @nbkts; $i++) {
	$rv .= ($nbkts[$i] . " ");
      }
      return $rv;
    }
  }
  else {
    return $line;
  }
}

#  Uses cached values (so it will show Phantom ones too)
sub getPortListing {
   my $self  = shift;
   my $shelf = shift;
   my $card  = shift;

   my @rv   = ();
   my $prts = $self->doAsyncCmd( "show_port " . $shelf . " " . $card );

   if ( $prts =~ /Timed out waiting for/g ) {
      $self->error("Partial Failure: Timed out");
   }

   my @ta = split( /\n/, $prts );

   my $i;
   for ( $i = 0 ; $i < @ta ; $i++ ) {
      my $ln = $ta[$i];
      if ( $ln =~ /Shelf:\s+\d+,\s+Card:\s+\d+,\s+Port:\s+\d+\s+Type/ ) {
         my $ptxt;
         while ( $ln =~ /\S+/ ) {
            $ptxt .= "$ln\n";
            $i++;
            $ln = $ta[$i];
         }

         my $p1 = new LANforge::Port();
         $p1->decode($ptxt);
         @rv = ( @rv, $p1 );
      }
   }
   return @rv;
} #~getPortListing

sub updatePortRetry {
   my $self = shift;
   return $self->updatePort( shift, shift, shift, shift, shift, 10000 );
}

# Call with args: Port, (these next ones are optional): Shelf-id, Card-id, Port-Id
sub updatePort {
   my $self        = shift;
   my $port        = shift;
   my $sid         = shift;    #shelf-id
   my $max_retries = undef;
   if ( defined($sid) ) {
      $port->shelf_id($sid);
      $port->card_id(shift);
      $port->port_id(shift);

      $max_retries = shift;
   }

   if ( !defined($max_retries) ) {
      $max_retries = 10;
   }

 # Since I use this for testing, I'm going to obliterate the port's data so that
 # there will be no question as to whether or not the update worked.
   $port->initDataMembers();   #Shouldn't mess with the shelf, card, or port id.

   my $cmd =
       "nc_show_port "
     . $port->shelf_id() . " "
     . $port->card_id() . " "
     . $port->port_id;

   #print "cmd -:$cmd:-\n";

   # Use the non-caching port show.
   my $prt = $self->doAsyncCmd($cmd);

# There is a small race condition, where one report may be on the way back to the
# main server when the first request is still being sent.  So, we'll ask again.  This
# one will definately be up to date.
   $prt = "";
   my $i = 0;
   while (1) {
      $prt = $self->doAsyncCmd($cmd);
      if ( !$self->cli_rcv_silent() ) {    # added by Adam - 8/9/2004
         print "prt: $prt\n";
      }

      if ( $i++ > $max_retries ) {
         last;
      }

      if (  ( $prt =~ /Could not find that Port/g )
         || ( $prt =~ /Timed out waiting/g )
         || ( !( $prt =~ /, Port:/g ) ) )
      {
         sleep(5);
      }
      else {
         last;
      }
   }

   if ( !$self->cli_rcv_silent() ) {    # added by Adam - 8/9/2004
      print "decoding port -:$prt:-\n";
   }
   $port->decode($prt);
}    #updatePort

sub updateEndpoint {
   my $self = shift;
   my $endp = shift;
   my $name = shift;
   my $fast = shift;

   if ( defined($name) ) {
      $endp->name($name);
   }

# Since I use this for testing, I'm going to obliterate the Endpoint's data so that
# there will be no question as to whether or not the update worked.
   $endp->initDataMembers();   #Shouldn't mess with the shelf, card, or port id.

   my $ep;
   if ($fast) {
      $ep = $self->doAsyncCmd( "show_endpoint " . $endp->name() );
   }
   else {

      # Use the non-caching endpoint show.
      $ep = $self->doAsyncCmd( "nc_show_endpoint " . $endp->name() );

# There is a small race condition, where one report may be on the way back to the
# main server when the first request is still being sent.  So, we'll ask again.  This
# one will definately be up to date.
      $ep = $self->doAsyncCmd( "nc_show_endpoint " . $endp->name() );
   }

   #print "EP show_endp results for cmd: " . $endp->name() . "\n-:$ep:-\n";

   $endp->decode($ep);

   if ( $endp->isCustom() ) {
      $ep = $self->doCmd( "show_endp_pay " . $endp->name() . " 5000" );
      $endp->decodePayload($ep);
   }
}    #updateEndpoint

sub log_cli {
  my $self = shift;
  my $cmd = shift;
  my $using_stdout = 0;
  #print "utils::log_cli: $ENV{'LOG_CLI'}\n";
  if (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "") {
    if ($ENV{'LOG_CLI'} =~ /^--/) {
      die("Incorrect format for LOG_CLI, it should be '1' or  filename like '/tmp/cmdlog.txt'");
    }
    if ($ENV{'LOG_CLI'} eq "1" || $ENV{'LOG_CLI'} =~ /STDOUT/i) {
      $using_stdout = 1;
      #print "STDOUT utils::log_cli: $ENV{'LOG_CLI'}\n";
    }
    else { # write to a file
      if ( ! -f $ENV{'LOG_CLI'}) {
        print "Creating new file $ENV{'LOG_CLI'}\n";
        `touch $ENV{'LOG_CLI'}`;
        chmod(0666, $ENV{'LOG_CLI'});
      }
      if ( -w $ENV{'LOG_CLI'}) {
        open(my $fh, ">>", $ENV{'LOG_CLI'});
        if (defined $fh) {
          #print "FILE utils::log_cli: \n";
          print $fh "$cmd\n";
          close $fh;
        }
        else {
          warn ("$ENV{'LOG_CLI'} not writable");
          $using_stdout=1;
          #print "ELSE STDOUT utils::log_cli: $ENV{'LOG_CLI'}\n";
        }
      }
    }
  }
  if ($using_stdout == 1 || !isQuiet() ) {
    print "\nCMD: $cmd\n"
  }
}

# returns 1 if we're quiet, 0 if we're verbose
# if $::quiet is undefined, we assume verbose
sub isQuiet {
  my $self = shift;
  return 0
    if (! defined $::quiet);

  if (length( do { no warnings "numeric"; $::quiet & "" } )) {
    # we're numeric
    if ($::quiet != 0) {
      #print "numeric and quiet [$::quiet]\n";
      return 1;
    }
    #print "numeric and verbose [$::quiet]\n";
    return 0;
  }

  # else we're textual
  if ($::quiet =~ /(1|yes|on)/i) {
    #print "textual and quiet [$::quiet]\n";
    return 1;
  }
  #print "textual and verbose [$::quiet]\n";
  return 0;
}

sub async_waitfor {
   my $self = shift;
   if (@_) { $self->{async_waitfor} = shift }
   return $self->{async_waitfor};
}

sub error {
   my $self = shift;
   if (@_) { $self->{error} = shift }
   return $self->{error};
}

sub cli_rcv_silent {
   my $self = shift;
   if (@_) { $self->{cli_rcv_silent} = shift }
   return $self->{cli_rcv_silent};
}

sub cli_send_silent {
   my $self = shift;
   if (@_) { $self->{cli_send_silent} = shift }
   return $self->{cli_send_silent};
}

sub fmt_cmd {
   #print Dumper(@_);
   my $self = shift;
   my $rv;
   my $mod_hunk;
   my $show_err = 0;
   my $item = 1;
   my $prev_item;
   for my $hunk (@_) {
      if (defined $hunk && $hunk eq '') {
         print STDERR "\nfmt_cmd() arg $item blank, converting to NA\n";
         print STDERR "            prev argument was [$prev_item]\n" if (defined $prev_item);
         $show_err = 1;
      }
      die("rv[${rv}]\n --> fmt_cmd passed an array, bye.")  if (ref($hunk) eq 'ARRAY');
      die("rv[${rv}]\n --> fmt_cmd passed a hash, bye.")    if (ref($hunk) eq 'HASH');
      $mod_hunk = $hunk;
      $mod_hunk = "0" if ($hunk eq "0" || $hunk eq "+0");

      if( $hunk eq "" ) {
         #print "hunk[".$hunk."] --> ";
         $mod_hunk = 'NA';
         #print "hunk[".$hunk."]\n";
         #print "fmt_cmd: warning: hunk was blank, now NA. Prev hunks: $rv\n"
      }
      $prev_item = $hunk;
      $item++;
      $rv .= ( $mod_hunk =~m/ +/) ? "'$mod_hunk' " : "$mod_hunk ";
   }
   chomp $rv;
   print STDERR "\ncmd: $rv\n" if($show_err or $::quiet ne "yes");
   return $rv;
}

##
## Check if usleep() exists
##
our $has_usleep = 0;
if (defined &usleep) {
   print("I see usleep\n");
   $LANforge::Utils::has_usleep=1;
}


sub sleep_ms {
  my $self;
  my $millis = 0;
  if (@_ > 1) {
    ($self, $millis) = @_;
  }
  else {
    $millis = pop(@_);
  }
  return if (!(defined $millis) || ($millis == 0));

  my $secs = $millis / 1000;

  if ($LANforge::Utils::has_usleep) {
    usleep($millis);
  }
  else {
    select(undef, undef, undef, $secs);
  }
}

sub sleep_sec {
  my $self;
  my $secs = 0;
  if (@_ > 1) {
    ($self, $secs) = @_;
  }
  else {
    ($secs) = @_;
  }
  return if (!(defined $secs) || ($secs == 0));

  if ($LANforge::Utils::has_usleep) {
    usleep($secs);
  }
  else {
    select(undef, undef, undef, $secs);
  }
}

##
##  Returns ref to map of all stations maching a parent device
##  EG: $rh_eid_map = $u->get_eid_map($::resource)
##

sub get_eid_map {
  my ($self, $resource) = @_;
  my $rh_eid_map = {};
  my @ports_lines = split("\n", $self->doAsyncCmd("nc_show_ports 1 $resource ALL"));
  sleep_ms(100);
  chomp(@ports_lines);

  my ($eid, $card, $port, $type, $mac, $dev, $parent, $ip);
  foreach my $line (@ports_lines) {
    # collect all stations on that radio add them to @interfaces
    if ($line =~ /^Shelf: /) {
      $card = undef; $port = undef;
      $type = undef; $parent = undef;
      $eid = undef; $mac = undef;
      $dev = undef;
      $ip = undef;
    }

    # careful about that comma after card!
    # NO EID for Shelf: 1, Card: 1, Port: 2  Type: WIFI-Radio  Alias:
    ($card, $port, $type) = $line =~ m/^Shelf: 1, Card: (\d+),\s+Port: (\d+)\s+Type: (\w+)/;
    if ((defined $card) && ($card ne "") && (defined $port) && ($port ne "") && ($type ne "VRF")) {
      $eid = "1.".$card.".".$port;
      my $rh_eid = {
        eid => $eid,
        type => $type,
        parent => undef,
        dev => undef,
      };
      $rh_eid_map->{$eid} = $rh_eid;
    }
    #elsif ($line =~ /^Shelf/) {
    #  #print "NO EID for $line\n";
    #}

    if (!(defined $eid) || ($eid eq "")) {
      #print "NO EID for $line\n";
      next;
    }
    ($mac, $dev) = $line =~ / MAC: ([0-9:a-fA-F]+)\s+DEV: (\S+)/;
    if ((defined $mac) && ($mac ne "")) {
      #print "$eid MAC: $line\n";
      $rh_eid_map->{$eid}->{mac} = $mac;
      $rh_eid_map->{$eid}->{dev} = $dev;
    }

    ($parent) = $line =~ / Parent.Peer: (\S+) /;
    if ((defined $parent) && ($parent ne "")) {
      #print "$eid PARENT: $line\n";
      $rh_eid_map->{$eid}->{parent} = $parent;
    }

    ($ip) = $line =~ m/ IP: *([^ ]+) */;
    if ((defined $ip) && ($ip ne "")) {
      #print "$eid IP: $line\n";
      $rh_eid_map->{$eid}->{ip} = $ip;
    }
  } # foreach

  #foreach $eid (keys %eid_map) {
  #  print "eid $eid ";
  #}
  return $rh_eid_map;
}

##
##
##
sub find_by_name {
  my ($self, $rh_eid_map, $devname) = @_;
  while (my ($eid, $rh_rec) = each %{$rh_eid_map}) {
    #print "fbn: ".$rh_rec->{dev}."\n";
    if ((defined $rh_rec->{dev}) && ($rh_rec->{dev} eq $devname)) {
      return $rh_rec;
    }
  }
  return -1;
}

##
## retrieve ports on radio from EID map
## EG: $ra_interfaces = $u->ports_on_radio($rh_eid_map, $radio_name);
##
sub ports_on_radio {
  my ($self, $rh_rec2_map, $radio) = @_;
  my $ra_ifs = [];
  #print "PARENT IS $radio\n";

  foreach my $rh_rec2 (values %{$rh_rec2_map}) {
    next if (!(defined $rh_rec2->{parent}));
    #print "\npor: ".$rh_rec2->{parent}.">".$rh_rec2->{dev}."\n";
    if ($rh_rec2->{parent} eq $radio) {
      #print $rh_rec2->{dev}."<-".$rh_rec2->{parent}." ";
      my $devn = $rh_rec2->{dev};
      push(@$ra_ifs, $devn);
    }
  }
  return $ra_ifs;
}

sub test_groups {
  my ($self) = @_;
  my @group_lines = split(/\r?\n/, $self->doAsyncCmd("show_group all"));
  sleep_ms(10);

  #print Dumper(\@group_lines);
  my @matches = grep {/TestGroup name:\s+/} @group_lines;
  #print Dumper(\@matches);
  my $ra_group_names = [];
  for my $line (@matches) {
    push(@$ra_group_names, ($line =~ /TestGroup name:\s+(\S+)\s+\[/));
  }
  #print Dumper($ra_group_names);

  return $ra_group_names;
}

sub group_items {
   my ($self, $tg_name) = @_;
   die("Utils::group_items wants a test group name, bye.")
      if (!(defined $tg_name) || ("" eq $tg_name));
   my @lines = split(/\r?\n/, $self->doAsyncCmd( "show_group '$tg_name'"));
   sleep_ms(100);

   my @cx_line = grep {/\s*Cross Connects:/} @lines;
   if (@cx_line < 1) {
     print "No cross connects found for test group $::test_grp. Bye.\n";
     exit(1);
   }
   my $trimmed = $cx_line[0];
   $trimmed =~ s/^\s*Cross Connects:\s*//;
   my $ra_items = [split(/\s+/, $trimmed)];
   #print Dumper($ra_items);
   return $ra_items;
}

####
1;
__END__


=head1 NAME
  Port - class to implement various LANforge utility and helper functions.

=head1 SYNOPSIS

  use LANforge::Utils

  #################
  # class methods #
  #################
  $ob    = LANforge::Utils->new;

  #######################
  # object data methods #
  #######################

  ### get versions ###
  $telnet = $ob->telnet();

  ### set versions ###
  $ob->telnet($t);

  ########################
  # other object methods #
  ########################

  $ob->doCmd("$Some CLI command\n");
  $ob->doAsyncCmd("$Some Asynchronous CLI command\n");

=head1 DESCRIPTION
  The Utils class gives you some powerful and packaged access to various
  LANforge CLI objects.

=head1 AUTHOR
  Ben Greear (greearb@candelatech.com)
  Copyright (c) 2020  Candela Technologies.  All rights reserved.
  This program is free software; you can redistribute it and/or
  modify it under the same terms as Perl itself.

=end
