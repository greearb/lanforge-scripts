# test utilities for LANforge scripts
package LANforge::Test;
use strict;
use warnings;
use diagnostics;
use Carp;
use Test2::V0;
$SIG{ __DIE__  } = sub { Carp::confess( @_ ) };
$SIG{ __WARN__ } = sub { Carp::confess( @_ ) };

# Un-buffer output
$| = 1;
use Data::Dumper;

if (defined $ENV{'DEBUG'}) {
   use Data::Dumper;
   use diagnostics;
   use Carp;
   $SIG{ __DIE__ } = sub { Carp::confess( @_ ) };
}

require Exporter;
our @EXPORT_OK=qw(new test);

our $FAIL   = 0;
our $OK     = 1;

sub new {
   my $class = shift;
   my $self = {};
   my %parm = @_;
   $self->{'Name'} = $parm{'Name'};
   $self->{'Desc'} = $parm{'Desc'};
   $self->{'Errors'} = [];
   $self->{'ExpectedNumber'} = 1;
   $self->{'Test'} = undef;
   if (defined $parm{'Test'}) {
      $self->{'Test'} = $parm{'Test'};
   }
   if (defined $parm{'ExpectedNumber'}) {
      $self->{'ExpectedNumber'} = $parm{'ExpectedNumber'};
   }
   bless $self, $class;
   return $self;
}

sub test {
   my $self = shift;
   if (! (defined $self->{'Test'})) {
      return $::FAIL;
   }
   return &{$self->{'Test'}}();
}
sub test_err {
  my $self = shift;
  for my $e (@_) {
    my $ref = "".(caller(1))[3].":".(caller(1))[2]."";
    push (@{$self->{'Errors'}}, "$ref: $e");
  }
}
1;