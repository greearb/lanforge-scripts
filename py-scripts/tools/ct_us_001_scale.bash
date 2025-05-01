#!/bin/bash

# allow commands to be printed to the terminal
#
set -x

echo "Running Dataplane Tests"
./lf_check.py \
--db_override ./tools/CT_001_SCALE_2025.db \
--json_dut ./ct_dut_json/ct_001_AXE16000_dut.json \
--json_rig ./ct_rig_json/ct_us_001_rig.json \
--json_test \
./ct_tests_json/ct_us_001/ct_scale/ct_scale_001.json:ct_scale_001 \
--path /home/lanforge/html-reports/ct_us_001 \
--log_level debug
