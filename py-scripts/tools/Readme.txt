This Readme.txt is to assist in running the lf_check.py test suites on the various test setups

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 



##########################
TESTBED 007 RVR test runs 
#########################


# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7915e_W0,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_ax210_W2,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7921_W6,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7922_W7  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_mt7915e_W0,./ct_tests_json/ct_perf_rvr_5g_1_007.json:rvr_perf_5g_1_ax210_W2,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_mt7921_W6,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_mt7922_W7  --path /home/lanforge/html-reports/ct_us_007 --log_level debug


#6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_ax210_W2,./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_mt7921_W6,./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_mt7922_W7  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#2G 5G 6G
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_perf_rvr_2g_5g_6g_007.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4  --path /home/lanforge/html-reports/ct_us_007 --log_level debug

#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_007_rig.json --json_dut ./ct_dut_json/ct_ASUS_AXE16000_10_Gbps_eth3.json --json_test ./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7915e_W0,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_ax210_W2,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7921_W6,./ct_tests_json/ct_perf_rvr_2g_007.json:rvr_perf_2g_mt7922_W7,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_1_mt7915e_W0,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_1_ax210_W2,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_1_mt7921_W6,./ct_tests_json/ct_perf_rvr_5g_007.json:rvr_perf_5g_1_mt7922_W7,./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_ax210_W2,./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_mt7921_W6,./ct_tests_json/ct_perf_rvr_6g_007.json:rvr_perf_6g_mt7922_W7,./ct_tests_json/ct_perf_rvr_2g_5g_6g_007.json:rvr_perf_2g_5g_6g_ax210_W2_W3_W4 --path /home/lanforge/html-reports/ct_us_007 --log_level debug

