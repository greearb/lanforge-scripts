#!/bin/bash
DESTF=../../html/scripts_ug.php
#DESTF=/var/www/html/greearb/lf/scripts_ug.php

./gen_html_help.pl py-scripts/test_l3.py py-scripts/test_l3_longevity.py py-scripts/sta_connect2.py py-scripts/lf_interop_ping.py > $DESTF
