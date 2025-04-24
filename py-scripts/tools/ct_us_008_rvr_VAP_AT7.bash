#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running RVR tests against VAP"
./lf_check.py \
--db_override ./tools/CT_US_008_RVR_PERF_VAP_AT7.db \
--json_rig ./ct_rig_json/ct_us_008_rig_AT7_MTK7996e.json \
--json_dut ./ct_dut_json/ct_008_VAP_AT7_mtk7996e_dut.json \
--json_test \
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_2g_W0_UDP_tx_vap.json:ct_perf_vap_rvr_2g_W0_UDP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_5g_W1_UDP_tx_vap.json:ct_perf_vap_rvr_5g_W1_UDP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_6g_W2_UDP_tx_vap.json:ct_perf_vap_rvr_6g_W2_UDP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_2g_W0_UDP_rx_vap.json:ct_perf_vap_rvr_2g_W0_UDP_rx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_5g_W1_UDP_rx_vap.json:ct_perf_vap_rvr_5g_W1_UDP_rx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_6g_W2_UDP_rx_vap.json:ct_perf_vap_rvr_6g_W2_UDP_rx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_2g_W0_TCP_tx_vap.json:ct_perf_vap_rvr_2g_W0_TCP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_5g_W1_TCP_tx_vap.json:ct_perf_vap_rvr_5g_W1_TCP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_6g_W2_TCP_tx_vap.json:ct_perf_vap_rvr_6g_W2_TCP_tx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_2g_W0_TCP_rx_vap.json:ct_perf_vap_rvr_2g_W0_TCP_rx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_5g_W1_TCP_rx_vap.json:ct_perf_vap_rvr_5g_W1_TCP_rx,\
./ct_tests_json/ct_us_008/ct_perf_rvr/vap_dut/ct_perf_rvr_6g_W2_TCP_rx_vap.json:ct_perf_vap_rvr_6g_W2_TCP_rx \
--path /home/lanforge/html-reports/ct_us_008 \
--log_level debug \
--production
