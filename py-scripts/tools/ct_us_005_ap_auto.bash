#!/bin/bash

# allow commands to be printed to the terminal

echo "Running ap_auto_basic_cx"
./ct_us_005_ap_auto_basic_cx.bash

echo "Running ap_auto_long_term"
./ct_us_005_ap_auto_long_term.bash

echo "Running ap_auto_mix_stability"
./ct_us_005_ap_auto_mix_stability.bash
