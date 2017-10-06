package LANforge::Utils;
use strict;
use warnings;
use Carp;
#$SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
#$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };
#use Data::Dumper;

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
   $self->{async_waitfor}   = '/default\@btbits\>\>/';

   bless( $self, $class );
   return $self;
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
   my $t    = $self->telnet();
   if ( !$self->cli_send_silent() || (defined $ENV{'LOG_CLI'} && $ENV{'LOG_CLI'} ne "")) {
      $self->log_cli($cmd);
   }

   $t->print($cmd);
   my @rslt = $t->waitfor('/ \>\>RSLT:(.*)/');
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
   my @rslt2 = $t->waitfor( $self->async_waitfor() ); #'/default\@btbits\>\>/');
   @rv = ( @rslt, @rslt2 );

   if ( !$self->cli_rcv_silent() ) {
      print "**************\n @rv \n................\n\n";
   }
   return join( "\n", @rv );
}    #doAsyncCmd

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
}    #getPortListing

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

sub telnet {
   my $self = shift;
   if (@_) { $self->{telnet} = shift }

   $self->{telnet}->max_buffer_length(50 * 1024 * 1024);
   return $self->{telnet};
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
   for my $hunk (@_) {
      if (defined $hunk && $hunk eq '') {
         print STDERR "\nfmt_cmd() found blank argument. Converting to NA\n";
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
      $rv .= ( $mod_hunk =~m/ +/) ? "'$mod_hunk' " : "$mod_hunk ";
   }
   chomp $rv;
   print STDERR "\ncmd: $rv\n" if($show_err or $::quiet ne "yes");
   return $rv;
}

1; # So the require or use succeeds (perl stuff)
__END__


# Plain Old Documentation (POD)

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

  Copyright (c) 2001  Candela Technologies.  All rights reserved.
  This program is free software; you can redistribute it and/or
  modify it under the same terms as Perl itself.


=head1 VERSION
  Version 0.0.1  May 26, 2001

=end
