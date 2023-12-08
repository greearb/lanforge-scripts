#!/bin/perl

use strict;

my $header = "<?php require_once \"lib.php\"; title(\"Candela Technologies Script Help\");
require_once(\"javascript_hdr.php\"); ?>
  </head>
  <BODY>
<?php require_once(\"header.php\"); ?>
<?php require_once(\"menu.php\"); ?>

<div id=\"contentDiv\">
<h1 id='top' class='big_heading'>LANforge Scripts Users Guide</h1>

";

my $footer = "<?php require_once(\"footer.php\"); ?>
</div>
</BODY>
</html>
";

my %reports = (
    "py-scripts/lf_interop_ping.py" => "interop_ping.pdf",
    "py-scripts/lf_wifi_capacity_test.py" => "wifi_capacity.pdf",
    "py-scripts/lf_dataplane_test.py" => "dataplane.pdf",
    "py-scripts/lf_rvr_test.py" => "rate_vs_range.pdf",
    );


my $i;

print $header;

my $toc = "";
my $script_help = "";

for ($i = 0; $i<@ARGV; $i++) {
    my $script = $ARGV[$i];
    my $script_printable = $script;
    $script_printable =~ s/\//_/g;
    my $exe = $script;
    my $cd = 0;
    if ($exe =~ /^py-scripts\/(.*)/) {
	$exe = $1;
	$cd = 1;
	chdir("py-scripts");
    }
    my $script_help_content = `./$exe --help`;
    $script_help_content =~ s/</&lt;/g;
    $script_help_content =~ s/>/&gt;/g;

    my $summary = `./$exe --help_summary`;
    if ($summary =~ /unrecognized arguments/) {
	$summary = "";
    }
    $summary =~ s/\n\n/<P>/g;

    if ($cd) {
	chdir("..");
    }

    my $rpt = $reports{$script};
    #print("rpt: $rpt  script: $script\n");
    if ($rpt eq undef) {
	$rpt = "";
    }
    else {
	$rpt = "<a href=\"examples/script_results/$rpt\">Example report: $rpt</a><br>";
    }
    #print("rpt2: $rpt  script: $script\n");

    $toc .= "<dt><a href=\"#$script_printable\"</a>$script</a></dt><dd>$rpt " . "$summary</dd>\n";
    $script_help .= "<dt><a name=\"$script_printable\">$script</dt>\n";
    $script_help .= "<dd>$rpt<pre>$script_help_content</pre></dd>\n";
}

print "Script Table of Contents<br><dl>
$toc
</dl>
<P>\n\n";

print "Script Information<br><dl>
$script_help
</dl>\n\n";

print $footer;
