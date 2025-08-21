#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Functional tests"
./lf_check.py \
--db_override ./tools/ct_us_009_FUNC_ASUS_BE96U.db \
--json_rig ./ct_rig_json/ct_us_009_ASUS_BE96U_rig.json \
--json_dut ./ct_dut_json/ct_009_ASUS_BE96U_dut.json \
--json_test \
./ct_tests_json/ct_us_009/ct_perf_functional/ASUS_BE96U/ct_test_l3.json:ct_test_l3 \
--path /home/lanforge/html-reports/ct_us_009 \
--log_level debug
