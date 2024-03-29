#!/bin/bash

# this script does not know where btbits/html lives in relation to your
# lanforge-scripts checkout directory. The location below is correct in 
# the case where this script is executed from btbits/x64_btbits/server/lf-scripts
# (eg, a server build).
# DESTF=${1:-./scripts_ug.php}  use for testing and local scripts_ug.ph generation in lanforge-scripts
DESTF=${1:-../../html/scripts_ug.php}
if [[ -z ${1:-} ]]; then
    echo "Using $DESTF as the default target."
fi
if [[ ! -f $DESTF ]]; then
    echo "* * $DESTF not found? Suggest setting env varialble DESTF first."
    echo "exit with [ctrl-c]"
    sleep 3
    echo "...proceeding"
fi
#DESTF=/var/www/html/greearb/lf/scripts_ug.php

scripts=(
    py-scripts/lf_dataplane_test.py
    py-scripts/lf_interop_ping.py
    py-scripts/lf_rvr_test.py
    py-scripts/lf_wifi_capacity_test.py
    py-scripts/lf_tr398v4_test.py
    py-scripts/raw_cli.py
    py-scripts/sta_connect2.py
    py-scripts/test_l3.py
    py-scripts/test_l3_longevity.py
)
./gen_html_help.pl "${scripts[@]}" > $DESTF
echo "...created $DESTF"
