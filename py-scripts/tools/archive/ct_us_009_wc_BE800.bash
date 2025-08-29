#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Wifi Capacity tests"
./lf_check.py \
--db_override ./tools/CT_US_009_WC_PERF_BE800.db \
--json_rig ./ct_rig_json/ct_us_009_TP_LINK_BE800_rig.json \
--json_dut ./ct_dut_json/ct_009_TP_LINK_BE800_dut.json \
--json_test \
./ct_tests_json/ct_us_009/ct_perf_wc/TP_LINK_BE800/ct_perf_wc_2g_W0_W1_W2_W3_W4_W5_W6_W7_W8_DL_UL_TCP_UDP.json:ct_perf_wc_2g_W0_W1_W2_W3_W4_W5_W6_W7_W8_DL_UL_TCP_UDP,\
./ct_tests_json/ct_us_009/ct_perf_wc/TP_LINK_BE800/ct_perf_wc_5g_W0_W1_W2_W3_W4_W5_W6_W7_W9_DL_UL_TCP_UDP.json:ct_perf_wc_5g_W0_W1_W2_W3_W4_W5_W6_W7_W9_DL_UL_TCP_UDP,\
./ct_tests_json/ct_us_009/ct_perf_wc/TP_LINK_BE800/ct_perf_wc_6g_W0_W1_W2_W3_W4_W5_W6_W7_W10_DL_UL_TCP_UDP.json:ct_perf_wc_6g_W0_W1_W2_W3_W4_W5_W6_W7_W10_DL_UL_TCP_UDP \
--path /home/lanforge/html-reports/ct_us_009 \
--log_level debug
