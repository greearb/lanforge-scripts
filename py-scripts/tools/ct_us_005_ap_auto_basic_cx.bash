#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running AP_AUTO_TESTS"
./lf_check.py \
--db_override ./tools/CT_005_AP_AUTO_START_MARCH_2025.db \
--json_rig ./ct_rig_json/ct_us_005_rig_AXE11000.json \
--json_dut ./ct_dut_json/ct_005_AXE11000_dut.json \
--json_test \
./ct_tests_json/ct_us_005/ct_ap_auto/ct_ap_auto_basic_cx_005.json:ct_ap_auto_basic_cx_005 \
--path /home/lanforge/html-reports/ct_us_005 \
--log_level debug \
--new_test_run \
--production
