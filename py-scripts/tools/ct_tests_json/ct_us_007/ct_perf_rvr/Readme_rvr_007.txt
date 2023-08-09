This Readme.txt is to assist in running the lf_check.py test suites on the various test setups

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 



##################################
TESTBED 007 RVR test runs Transmit
##################################


# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7922_W7_tx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_1_007.json:rvr_perf_5g_1_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7922_W7_tx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug


#6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7922_W7_tx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#2G 5G 6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_tx --path /home/lanforge/html-reports/ct_us_007 --log_level debug


##################################
TESTBED 007 RVR test runs Receive
##################################

# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7922_W7_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_1_007.json:rvr_perf_5g_1_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7922_W7_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug


#6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7922_W7_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#2G 5G 6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_rx --path /home/lanforge/html-reports/ct_us_007 --log_level debug




##############################################
TESTBED 007 RVR test runs Transmit and Receive  Scroll down do the last one
##############################################

# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7915e_W0_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7922_W7_tx_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_mt7915e_W0_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_1_007.json:rvr_perf_5g_1_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_mt7922_W7_tx_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug


#6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_mt7922_W7_tx_rx  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#2G 5G 6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7915e_W0_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx_rx.json:rvr_perf_2g_mt7922_W7_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_mt7915e_W0_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx_rx.json:rvr_perf_5g_1_mt7922_W7_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_ax210_W2_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_mt7921_W6_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx_rx.json:rvr_perf_6g_mt7922_W7_tx_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_tx_rx --path /home/lanforge/html-reports/ct_us_007 --log_level debug



################################
rvr_perf_5g_1_ax210_W2_tx issue
################################

./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_ax210_W2_tx --path /home/lanforge/html-reports/ct_us_007 --log_level debug

################################
rvr_perf_5g_1_ax210_W2_tx issue  using DB override
################################

./lf_check.py --db_override ./tools/CT_007_RVR_AX210_PERF.db --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_ax210_W2_tx --path /home/lanforge/html-reports/ct_us_007 --log_level debug



########################################################
TESTBED 007 RVR test runs Transmit Receive Individually  use this one  <<<<< New Release Regression Test suite 
########################################################
./lf_check.py --db_override ./tools/CT_US_007_RVR_PERF.db --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_rx.json:rvr_perf_2g_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7915e_W0_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_rx.json:rvr_perf_5g_1_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_ax210_W2_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7921_W6_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_rx.json:rvr_perf_6g_mt7922_W7_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_rx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_rx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_007_tx.json:rvr_perf_2g_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7915e_W0_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_5g_007_tx.json:rvr_perf_5g_1_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_ax210_W2_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7921_W6_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_6g_007_tx.json:rvr_perf_6g_mt7922_W7_tx,./ct_tests_json/ct_us_007/ct_perf_rvr/ct_perf_rvr_2g_5g_6g_007_tx.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4_tx --path /home/lanforge/html-reports/ct_us_007 --log_level debug
