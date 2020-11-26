#!/bin/bash
#Variables
NUM_STA=4
SSID_USED="jedway-wpa2-x2048-4-1"
PASSWD_USED="jedway-wpa2-x2048-4-1"
RADIO_USED="wiphy1"
SECURITY="wpa2"
CURR_TEST_NAME="BLANK"
CURR_TEST_NUMBER=0
STOP_NUM=0
START_NUM=0
#Test array
testCommands=("./example_wpa_connection.py --num_stations $NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio $RADIO_USED --security wpa" 
"./example_wpa2_connection.py --num_stations $NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio $RADIO_USED --security wpa2"
"./example_wep_connection.py --num_stations $NUM_STA --ssid jedway-wep-48 --passwd jedway-wep-48 --radio $RADIO_USED --security wep"
"./example_wpa3_connection.py --num_stations $NUM_STA --ssid jedway-wpa3-1 --passwd jedway-wpa3-1 --radio $RADIO_USED --security wpa3"
"./test_ipv4_connection.py --radio $RADIO_USED --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --upstream_port eth1"
"./test_generic.py --mgr localhost --mgr_port 4122 --radio $RADIO_USED --ssid SSID_USED --passwd $PASSWD_USED --num_stations $NUM_STA --type lfping --dest 10.40.0.1 --security $SECURITY"
"./test_generic.py --mgr localhost --mgr_port 4122 --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --num_stations $NUM_STA --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security $SECURITY"
"./test_ipv4_l4_urls_per_ten.py --upstream_port eth1 --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED  --num_tests 1 --requests_per_ten 600 --target_per_ten 600"
"./test_ipv4_l4_wifi.py --upstream_port eth1 --radio wiphy0 --num_stations $NUM_STA --security $SECURITY --ssid jedway-wpa2-x2048-4-4 --passwd jedway-wpa2-x2048-4-4  --test_duration 3m"
"./test_ipv4_l4.py --radio wiphy3 --num_stations 4 --security wpa2 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1  --url \"dl http://10.40.0.1 /dev/null\"  --test_duration 2m --debug"
)
function ret_case_num(){
    echo "The script name that was successful passed in is $1"
    case "$1" in
        "example_wpa_connection")
            return 1
        "example_wpa2_connection")
            return 2
        "example_wpa3_connection")
            return 4
        "example_wep_connection")
            return 3
        "test_generic")
            return 5
        "test_ipv4_l4_urls_per_ten")
            return 6
        "test_ipv4_l4_wifi")
            return 7
        "test_ipv4_l4")
            return 8
    esac
}
function blank_db() {
	echo "Loading blank scenario..."
	./scenario.py --load BLANK
	#check_blank.py
}
function echo_print(){
	echo "Beginning $CURR_TEST_NAME ..."
}
function run_test(){
	for i in "${testCommands[@]}"; do
		CURR_TEST_NAME=${i%%.py*}
		CURR_TEST_NAME=${CURR_TEST_NAME#./*}
		#works til here
		CURR_TEST_NUM= ret_case_num $CURR_TEST_NAME
		if ($STOP_NUM > $CURR_TEST_NUM &&  ); then
		    exit 1
		fi
		echoPrint
        eval $i &>/home/Documents/txtfile 
        if [ $? -ne 0 ]; then 
            echo $CURR_TEST_NAME fail 
        fi
        #tail -f /tmp/testx
    	if  [[ "${CURR_TEST_NAME}" = @(example_wpa_connection|example_wpa2_connection|example_wpa3_connection|example_wep_connection) ]]; then 
    	    blank_db 
    	fi
    done
}
function check_args(){
    if [ ! -z $1 ]; then
        START_NUM=$1
    fi
    if [ ! -z $2 ]; then
        STOP_NUM=$2
    fi    
}
check_args $1 $2 
run_test
#test generic and fileio are for macvlans 
#all tests should return 0 for success and !0 for fail --almost complete
#case switch for tests to be run --almost complete
