This Readme_func_001.txt is to assist in running the lf_check.py test suites on the various test setups 

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 

Quick verification of the script (suite quick)
./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_funtional/ct_funtional.json:suite_quick  --path /home/lanforge/html-reports/ct_us_001 --log_level debug


###########################
TESTBED 001 funct test runs
###########################

./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_functional/ct_functional.json:funct_tests  --path /home/lanforge/html-reports/ct_us_001 --log_level debug

