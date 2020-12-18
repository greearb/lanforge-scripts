#!/bin/bash
#This bash script aims to automate the test process of all Candela Technologies's test_* scripts in the lanforge-scripts directory. The script can be run 2 ways and may include (via user input) the "start_num" and "stop_num" variables to select which tests should be run.
# OPTION ONE: ./test_all_scripts.sh : this command runs all the scripts in the array "testCommands"
# OPTION TWO: ./test_all_scripts.sh 4 5 :  this command runs py-script commands (in testCommands array) that include the py-script options beginning with 4 and 5 (inclusive) in case function ret_case_num.
#Variables
NUM_STA=4
SSID_USED="jedway-wpa2-x2048-5-3"
PASSWD_USED="jedway-wpa2-x2048-5-3"
RADIO_USED="wiphy1"
SECURITY="wpa2"
CURR_TEST_NAME="BLANK"
CURR_TEST_NUM=0
STOP_NUM=9
START_NUM=0
#Test array
testCommands=("./example_wpa_connection.py --num_stations $NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio $RADIO_USED --security wpa"
    "./example_wpa2_connection.py --num_stations $NUM_STA --ssid $SSID_USED --passwd $SSID_USED --radio $RADIO_USED --security wpa2"
    "./example_wep_connection.py --num_stations $NUM_STA --ssid jedway-wep-48 --passwd jedway-wep-48 --radio $RADIO_USED --security wep"
    "./example_wpa3_connection.py --num_stations $NUM_STA --ssid jedway-wpa3-1 --passwd jedway-wpa3-1 --radio $RADIO_USED --security wpa3"
    "./test_ipv4_connection.py --radio wiphy2 --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --upstream_port eth1"
    "./test_generic.py --mgr localhost --mgr_port 4122 --radio $RADIO_USED --ssid SSID_USED --passwd $PASSWD_USED --num_stations $NUM_STA --type lfping --dest 10.40.0.1 --security $SECURITY"
    "./test_generic.py --mgr localhost --mgr_port 4122 --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --num_stations $NUM_STA --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security $SECURITY"
    "./test_ipv4_l4_urls_per_ten.py --upstream_port eth1 --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED  --num_tests 1 --requests_per_ten 600 --target_per_ten 600"
    "./test_ipv4_l4_wifi.py --upstream_port eth1 --radio wiphy0 --num_stations $NUM_STA --security $SECURITY --ssid jedway-wpa2-x2048-4-4 --passwd jedway-wpa2-x2048-4-4  --test_duration 3m"
    "./test_ipv4_l4.py --radio wiphy3 --num_stations 4 --security wpa2 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1  --url \"dl http://10.40.0.1 /dev/null\"  --test_duration 2m --debug"
)
function ret_case_num() {
    case $1 in
    "example_wpa_connection")
        echo 1
        ;;
    "example_wpa2_connection")
        echo 2
        ;;
    "example_wpa3_connection")
        echo 4
        ;;
    "example_wep_connection")
        echo 3
        ;;
    "test_ipv4_connection")
        echo 5
        ;;
    "test_generic")
        echo 6
        ;;
    "test_ipv4_l4_urls_per_ten")
        echo 7
        ;;
    "test_ipv4_l4_wifi")
        echo 8
        ;;
    "test_ipv4_l4")
        echo 9
        ;;
    esac
}
function blank_db() {
    echo "Loading blank scenario..." >>~/test_all_output_file.txt
    ./scenario.py --load BLANK >>~/test_all_output_file.txt
    #check_blank.py
}
function echo_print() {
    echo "Beginning $CURR_TEST_NAME test..." >>~/test_all_output_file.txt
}
function run_test() {
    for i in "${testCommands[@]}"; do
        CURR_TEST_NAME=${i%%.py*}
        CURR_TEST_NAME=${CURR_TEST_NAME#./*}
        CURR_TEST_NUM=$(ret_case_num $CURR_TEST_NAME)
        if [[ $CURR_TEST_NUM -gt $STOP_NUM ]] || [[ $STOP_NUM -eq $CURR_NUM && $STOP_NUM -ne 0 ]]; then
            exit 1
        fi
        if [[ $CURR_TEST_NUM -gt $START_NUM ]] || [[ $CURR_TEST_NUM -eq $START_NUM ]]; then
            echo_print
            eval $i >>~/test_all_output_file.txt
            if [ $? -ne 0 ]; then
                echo $CURR_TEST_NAME failure
            else
                echo $CURR_TEST_NAME success
            fi
            if [[ "${CURR_TEST_NAME}" = @(example_wpa_connection|example_wpa2_connection|example_wpa3_connection|example_wep_connection) ]]; then
                blank_db
            fi
        fi
    done
}
function check_args() {
    if [ ! -z $1 ]; then
        START_NUM=$1
    fi
    if [ ! -z $2 ]; then
        STOP_NUM=$2
    fi
}
true >~/test_all_output_file.txt
check_args $1 $2
run_test
#test generic and fileio are for macvlans
