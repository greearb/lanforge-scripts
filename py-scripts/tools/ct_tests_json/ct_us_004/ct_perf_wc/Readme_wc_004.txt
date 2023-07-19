This Readme_wc_004.txt is to assist in running the lf_check.py test suites on the various test setups 

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 


########################
TESTBED 004 WC test runs
########################

# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_004_rig.json --json_dut ./ct_dut_json/ct_004_AX88U_dut.json --json_test ./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ax200_W4,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_2g_mtk7921_W5,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ax210_W6,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_004 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_004_rig.json --json_dut ./ct_dut_json/ct_004_AX88U_dut.json --json_test ./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_mtk7921_W5,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ax210_W6,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_004 --log_level debug


#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_004_rig.json --json_dut ./ct_dut_json/ct_004_AX88U_dut.json --json_test ./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_mtk7921_W5,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_ax210_W6,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_mtk7915_W7,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ax200_W4,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_5g_004.json:wc_perf_5g_mtk7921_W5,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_ax210_W6,./ct_tests_json/ct_us_004/ct_perf_wc/ct_perf_wc_2g_004.json:wc_perf_2g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_004 --log_level debug


