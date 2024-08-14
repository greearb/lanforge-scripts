#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running RVR tests"
./lf_check.py --db_override ./tools/CT_US_007_DP_PERF.db --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_TPLINK_CE22_10_Gbps_eth3.json \
--json_test \
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_2g_W6_W10_UCP_tx.json:ct_perf_dp_2g_W6_W10_UCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_5g_W6_W10_UCP_tx.json:ct_perf_dp_5g_W6_W10_UCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_6g_W6_W10_UCP_tx.json:ct_perf_dp_6g_W6_W10_UCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_2g_W6_W10_UCP_rx.json:ct_perf_dp_2g_W6_W10_UCP_rx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_5g_W6_W10_UCP_rx.json:ct_perf_dp_5g_W6_W10_UCP_rx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_6g_W6_W10_UCP_rx.json:ct_perf_dp_6g_W6_W10_UCP_rx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_2g_W6_W10_TCP_tx.json:ct_perf_dp_2g_W6_W10_TCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_5g_W6_W10_TCP_tx.json:ct_perf_dp_5g_W6_W10_TCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_6g_W6_W10_TCP_tx.json:ct_perf_dp_6g_W6_W10_TCP_tx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_2g_W6_W10_TCP_rx.json:ct_perf_dp_2g_W6_W10_TCP_rx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_5g_W6_W10_TCP_rx.json:ct_perf_dp_5g_W6_W10_TCP_rx,\
./ct_tests_json/ct_us_007/ct_perf_dp/ct_perf_dp_6g_W6_W10_TCP_rx.json:ct_perf_dp_6g_W6_W10_TCP_rx \
--path /home/lanforge/html-reports/ct_us_007 \
--log_level debug \
--production


