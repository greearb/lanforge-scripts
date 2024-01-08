#!/bin/bash
# This script runs both loadmon.pl and parse-loadmon.pl
# set -veu

LM="/home/lanforge/scripts/loadmon.pl"
# start loadmon in the background
function run_loadmon() {
    if [[ ! -x "$LM" ]]; then
        echo "$LM not found or not executable, bye"
        exit 1
    fi
    sudo $LM | systemd-cat -t loadmon
}

function show_loadmon() {
    journalctl -t loadmon --since "35 sec ago" | ./parse_loadmon.pl
}

echo "Starting loadmon in background..."
run_loadmon &

echo "Waiting for output..."
sleep 5

while true; do
  show_loadmon
  sleep 30
done

kill %1

echo "...done"