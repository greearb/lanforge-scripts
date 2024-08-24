#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Functional Tests"
./lf_check.py \
--db_override ./tools/CT_001_FUNCTIONALSTART_AUG_2023.db \
--json_rig ./ct_rig_json/ct_us_001_rig.json \
--json_dut ./ct_dut_json/ct_001_AX88U_dut.json \
--json_test ./ct_tests_json/ct_us_001/ct_functional/ct_functional.json:funct_tests \
--path /home/lanforge/html-reports/ct_us_001 \
--log_level debug \
--new_test_run \
--production