#!/bin/bash

# allow commands to be printed to the terminal

set -x

echo "Running Port Reset"
./lf_check.py \
--db_override ./tools/CT_002_CV_MAY_2025.db \
--json_rig ./ct_rig_json/ct_us_002_rig.json \
--json_dut ./ct_dut_json/ct_002_AX16K_dut.json \
--json_test \
./ct_tests_json/ct_us_002/ct_port_reset/ct_port_reset_2g_5g_6g_002.json:cv_tests,\
./ct_tests_json/ct_us_002/ct_scale/ct_scale_002.json:ct_scale \
--path /home/lanforge/html-reports/ct_us_002 \
--log_level debug \
--new_test_run
# --production
