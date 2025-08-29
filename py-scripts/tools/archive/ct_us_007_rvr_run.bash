#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running RVR tests"
./lf_check.py \
--db_override ./tools/CT_US_007_RVR_PERF.db \
--json_rig ./ct_rig_json/ct_us_007_rig.json \
--json_dut ./ct_dut_json/ct_TPLINK_CE22_10_Gbps_eth3.json \
--json_test \
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7915e_W0_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_ax210_W2_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7925e_W6_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7925e_W7_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:ct_perf_rvr_2g_be200_W10_UDP_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_ax210_W2_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7925e_W6_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7925e_W7_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7925e_W7_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:ct_perf_rvr_5g_be200_W10_UDP_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_ax210_W2_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7925e_W6_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7925e_W7_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:ct_perf_rvr_6g_be200_W10_UDP_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_rx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7915e_W0_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_ax210_W2_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7925e_W6_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7925e_W7_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:ct_perf_rvr_2g_be200_W10_UDP_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7915e_W0_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_ax210_W2_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7925e_W6_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7925e_W7_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:ct_perf_rvr_5g_be200_W10_UDP_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_ax210_W2_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7925e_W6_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7925e_W7_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:ct_perf_rvr_6g_be200_W10_UDP_tx,\
./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_tx \
--path /home/lanforge/html-reports/ct_us_007 \
--log_level debug \
--production
