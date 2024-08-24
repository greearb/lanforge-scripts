#!/bin/bash

# allow commands to be printed to the terminal
set -x

#echo "Running Functional Tests"
./lf_check.py \
--db_override ./tools/CT_004_FUNCTIONAL_START_AUG_2023.db \
--json_rig ./ct_rig_json/ct_us_004_rig.json \
--json_dut ./ct_dut_json/ct_004_AX88U_dut.json \
--json_test ./ct_tests_json/ct_us_004/ct_functional/ct_functional.json:funct_tests \
--path /home/lanforge/html-reports/ct_us_004 \
--log_level debug \
--new_test_run \
--production