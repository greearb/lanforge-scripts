#!/bin/bash
#
# Use this script to report sensors output to journalctl. This script
# should be invoked from a systemd-timer. Use lf_kinstall.pl --do_heatmon to create
# the systemd timer unit. The timer should probably only run once a minute.
#
if [[ ! -x /usr/bin/jq ]]; then
    echo "Unable to find jq."
    exit 1
fi
if [[ ! -x /usr/bin/sensors ]]; then
    echo "Unable to find sensors"
    exit 1
fi
/usr/bin/sensors -u -j \
  | jq -c '[.| to_entries |.[] | {A: .key, T: .value.temp1.temp1_input}]'

#