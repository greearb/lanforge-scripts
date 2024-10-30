#!/bin/bash

# allow commands to be printed to the terminal
set -x
echo "Running Wifi Capacity Tests"
./lf_check.py \
--db_override ./tools/CT_001_WC_PERF_START_AUG_2023.db \
--json_rig ./ct_rig_json/ct_us_001_rig.json \
--json_dut ./ct_dut_json/ct_001_AXE16000_dut.json \
--json_test \
./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001_W0_W2_W4_W5_W7.json:wc_perf_2g_W0_W2_W4_W5_W7,\
./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001_W1_W2_W4_W5_W7.json:wc_perf_5g_W1_W2_W4_W5_W7 \
--path /home/lanforge/html-reports/ct_us_001 \
--log_level debug \
--production