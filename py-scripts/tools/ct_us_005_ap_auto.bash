#!/bin/bash

# allow commands to be printed to the terminal

# Basic Client Connectivity
echo "Running ap_auto_basic_cx"
./ct_us_005_ap_auto_basic_cx.bash

# Band Steering

# Capacity
echo "Running ap_auto_capacity"
./ct_us_005_ap_capacity.bash

# Channel Switching

# Long Term
echo "Running ap_auto_long_term"
./ct_us_005_ap_auto_long_term.bash

# Stability
echo "Running ap_auto_mix_stability"
./ct_us_005_ap_auto_mix_stability.bash

# Signal STA Throughput vs Pkt Size
echo "Running ap_auto_single_sta"
./ct_us_005_ap_auto_tput_single_sta.bash

# Multi STA Throughput vs Pkt Size
echo "Running ap_auto_signal_sta"
./ct_us_005_ap_auto_tput_multi_sta.bash

# Multi Band Throughput
