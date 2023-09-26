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


my $i;

print $header;

my $toc = "";
my $script_help = "";

for ($i = 0; $i<@ARGV; $i++) {
    my $script = $ARGV[$i];
    my $script_printable = $script;
    $script_printable =~ s/\//_/g;
    my $script_help_content = `./$script --help`;
    $script_help_content =~ s/</&lt;/g;
    $script_help_content =~ s/>/&gt;/g;

    my $summary = `./$script --help_summary`;
    if ($summary =~ /unrecognized arguments/) {
	$summary = "";
    }
    $summary =~ s/\n\n/<P>/g;

    $toc .= "<dt><a href=\"#$script_printable\"</a>$script</a></dt><dd>$summary</dd>\n";
    $script_help .= "<dt><a name=\"$script_printable\">$script</dt>\n";
    $script_help .= "<dd><pre>$script_help_content</pre></dd>\n";
}

print "Script Table of Contents<br><dl>
$toc
</dl>
<P>\n\n";

print "Script Information<br><dl>
$script_help
</dl>\n\n";

print $footer;
