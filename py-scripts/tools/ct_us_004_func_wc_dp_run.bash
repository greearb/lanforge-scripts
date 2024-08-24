#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Functional Tests"
./ct_us_004_func.bash

echo "Running Wifi Capacity Tests"
./ct_us_004_wc.bash

echo "Running Dataplane Tests"
./ct_us_004_dp.bash