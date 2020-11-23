#!/bin/bash
declare -i NUM_STA="5"
SSID_USED="jedway-open-1"
PASSWD_USED=None
RADIO_USED="wiphy0"
DEF_SECURITY=""
#declare -i CURR_TEST_NUM=0
CURR_TEST_NAME=""
declare -a testCommands=("./example_wpa_connection.py --num_stations NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio RADIO_USED --security wpa" 
"./example_wpa_connection.py --num_stations NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio RADIO_USED --security wpa" 
"./example_wpa2_connection.py --num_stations NUM_STA --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio RADIO_USED --security wpa2"
"./example_wep_connection.py --num_stations NUM_STA --ssid jedway-wep-48 --passwd jedway-wep-48 --radio RADIO_USED --security wep"
"./example_wpa3_connection.py --num_stations NUM_STA --ssid jedway-wpa3-1 jedway-wpa3-1 --radio RADIO_USED --security wpa3")

function blank_db() {
	echo "Loading blank scenario..."
   	./scenario.py --load BLANK
   	#check_blank.py
}
function stop_script() {
	echo "Stopping bash script here."
	exit 1
}
function start_script{
	echo "Starting bash script at test...insert test name here"

}
function echoPrint{
     echo "Beginning $CURR_TEST ..."
}
function runTest{
	#get first test
	for i in "${testCommands[@]}"
	do
		$CURR_TEST= "${i%%.py*}"
		echoPrint()
    		eval "$i"   
    		sleep 15
    		if ! [[ "$CURR_TEST_NAME" =~ ^(example_wpa_connection|example_wpa2_connection|example_wpa3_connection|example_wep_connection)$ ]]; then blank_db() ; fi

}

#TODO
#check_blank.py
#edit scenario.py
#add stop and start 








