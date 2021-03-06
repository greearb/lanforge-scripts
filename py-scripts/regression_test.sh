#!/bin/bash
##########################
# Help
##########################
Help()
{
  echo "This bash script aims to automate the test process of all Candela Technologies's test_* scripts in the lanforge-scripts directory. The script can be run 2 ways and may include (via user input) the \"start_num\" and \"stop_num\" variables to select which tests should be run."
  echo "OPTION ONE: ./regression_test.sh : this command runs all the scripts in the array \"testCommands\""
  echo "OPTION TWO: ./regression_test.sh 4 5 :  this command runs py-script commands (in testCommands array) that include the py-script options beginning with 4 and 5 (inclusive) in case function ret_case_num."
  echo "Optional Variables:"
  echo "SSID is the name of the network you are testing against"
  echo "PASSWD is the password of said network"
  echo "SECURITY is the security protocol of the network"
  echo "MGR is the IP address of the device which has LANforge installed, if different from the system you are using."
  echo "A is used to call to test a specific command based on"
  echo "F is used to pass in an RC file which can store the credentials for running regression multiple times on your system"
  echo "Example command: ./regression_test.sh -s SSID -p PASSWD -w SECURITY -m MGR"
}

while getopts ":h:s:p:w:m:A:r:" option; do
  case "${option}" in
    h) # display Help
      Help
      exit 1
      ;;
    s)
      SSID_USED=${OPTARG}
      ;;
    p)
      PASSWD_USED=${OPTARG}
      ;;
    w)
      SECURITY=${OPTARG}
      ;;
    m)
      MGR=${OPTARG}
      ;;
    A)
      A=${OPTARG}
      ;;
    r)
      RADIO_USED=${OPTARG}
      ;;
    F)
      RC_FILE=${OPTARG}
      ;;
    *)

      ;;
  esac
done

if [[ ${#SSID_USED} -eq 0 ]]; then #Network credentials
  SSID_USED="jedway-wpa2-x2048-5-3"
  PASSWD_USED="jedway-wpa2-x2048-5-3"
  SECURITY="wpa2"
fi

if [[ ${#RADIO_USED} -eq 0 ]]; then # Allow the user to change the radio they test against
  RADIO_USED="wiphy1"
fi

FILE="/tmp/gui-update.lock"
if test -f "$FILE"; then
  echo "Finish updating your GUI"
  exit 0
fi

HOMEPATH=$(realpath ~)

if [[ ${#RC_FILE} -gt 0 ]]; then
  source "$RC_FILE"
fi

if [[ ${#SSID_USED} -gt 0 ]]; then
  if [ -f ./regression_test.rc ]; then
    source ./regression_test.rc # this version is a better unix name
  elif [ -f ./regression_test.txt ]; then
    source ./regression_test.txt # this less unixy name was discussed earlier
  fi
fi
NUM_STA=${NUM_STA:-4}
TEST_HTTP_IP=${TEST_HTTP_IP:-10.40.0.1}
MGRLEN=${#MGR}
COL_NAMES="name,tx_bytes,rx_bytes,dropped"

#START_NUM=0
CURR_TEST_NUM=0
CURR_TEST_NAME="BLANK"
#STOP_NUM=9

REPORT_DIR="${HOMEPATH}/html-reports"
if [ ! -d "$REPORT_DIR" ]; then
    echo "Report directory [$REPORT_DIR] not found, bye."
    exit 1
fi
REPORT_DATA="${HOMEPATH}/report-data"
if [ ! -d "${REPORT_DATA}" ]; then
    echo "Data directory [$REPORT_DATA] not found, bye."
    exit 1
fi
TEST_DIR="${REPORT_DATA}/${NOW}"

function run_l3_longevity() {
  ./test_l3_longevity.py --test_duration 15s --upstream_port eth1 --radio "radio==wiphy0 stations==4 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY" --radio "radio==wiphy1 stations==4 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY" --mgr "$MGR"
}
function testgroup_list_groups() {
  ./scenario.py --load test_l3_scenario_throughput
  ./testgroup.py --group_name group1 --add_group --add_cx cx0000,cx0001,cx0002 --remove_cx cx0003 --list_groups --debug --mgr "$MGR"
}
function testgroup_list_connections() {
  ./scenario.py --load test_l3_scenario_throughput
  ./testgroup.py --group_name group1 --add_group --add_cx cx0000,cx0001,cx0002 --remove_cx cx0003 --show_group --debug --mgr "$MGR"
}
function testgroup_delete_group() {
  ./scenario.py --load test_l3_scenario_throughput
  ./testgroup.py --group_name group1 --add_group --add_cx cx0000,cx0001,cx0002 --remove_cx cx0003
  ./testgroup.py --group_name group1--del_group --debug --mgr "$MGR"
}
if [[ $MGRLEN -gt 0 ]]; then
  testCommands=(
      "./example_security_connection.py --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --radio $RADIO_USED --security wpa2 --debug --mgr $MGR"
      "./sta_connect2.py --dut_ssid $SSID_USED --dut_passwd $PASSWD_USED --dut_security $SECURITY --mgr $MGR"
      # want if [[ $DO_FILEIO = 1 ]]
      "./test_fileio.py --macvlan_parent eth2 --num_ports 3 --use_macvlans --first_mvlan_ip 192.168.92.13 --netmask 255.255.255.0 --gateway 192.168.92.1 --test_duration 30s --mgr $MGR" # Better tested on Kelly, where VRF is turned off
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfping --dest $TEST_HTTP_IP --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security $SECURITY --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type iperf3 --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfcurl --dest $TEST_HTTP_IP --file_output ${HOMEPATH}/Documents/lfcurl_output.txt --debug --mgr $MGR"
      "./testgroup.py --group_name group1 --add_group --list_groups --debug --mgr $MGR"
      testgroup_list_groups
      testgroup_list_connections
      testgroup_delete_group
      "./testgroup2.py --num_stations 4 --ssid lanforge --passwd password --security wpa2 --radio wiphy0 --group_name group0 --add_group --mgr $MGR"
      "./test_ipv4_connection.py --radio $RADIO_USED --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./test_ipv4_l4_urls_per_ten.py --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --num_tests 1 --requests_per_ten 600 --target_per_ten 600 --debug --mgr $MGR"
      "./test_ipv4_l4_wifi.py --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug --mgr $MGR"
      "./test_ipv4_l4.py --radio $RADIO_USED --num_stations 4 --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug --mgr $MGR"
      "./test_ipv4_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format excel --layer3_cols $COL_NAMES --debug --mgr $MGR"
      "./test_ipv4_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format csv --layer3_cols $COL_NAMES --debug --mgr $MGR"
      "./test_ipv4_l4_ftp_upload.py --upstream_port eth1 --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug --mgr $MGR"
      "./test_ipv6_connection.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./test_ipv6_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --cx_type tcp6 --debug --mgr $MGR"
      run_l3_longevity
      "./test_l3_powersave_traffic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./test_l3_scenario_throughput.py -t 15s -sc test_l3_scenario_throughput --mgr $MGR"
      "./test_status_msg.py --debug --mgr $MGR" #this is all which is needed to run
      "./test_wanlink.py --debug --mgr $MGR"
      #"./ws_generic_monitor_test.py --mgr $MGR"
      "./create_bridge.py --radio $RADIO_USED --upstream_port eth1 --target_device sta0000 --debug --mgr $MGR"
      "./create_l3.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_l4.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_macvlan.py --radio $RADIO_USED --macvlan_parent eth1 --debug --mgr $MGR"
      "./create_qvlan.py --first_qvlan_ip 192.168.1.50"
      "./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_vap.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_vr.py --vr_name 2.vr0 --ports 2.br0,2.vap2 --services"
      "./wlan_capacity_calculator.py -sta 11abg -t Voice -p 48 -m 106 -e WEP -q Yes -b 1 2 5.5 11 -pre Long -s N/A -co G.711 -r Yes -c Yes --mgr $MGR"
      "./wlan_capacity_calculator.py -sta 11n -t Voice -d 17 -ch 40 -gu 800 -high 9 -e WEP -q Yes -ip 5 -mc 42 -b 6 9 12 24 -m 1538 -co G.729 -pl Greenfield -cw 15 -r Yes -c Yes --mgr $MGR"
      "./wlan_capacity_calculator.py -sta 11ac -t Voice -d 9 -spa 3 -ch 20 -gu 800 -high 1 -e TKIP -q Yes -ip 3 -mc 0 -b 6 12 24 54 -m 1518 -co Greenfield -cw 15 -rc Yes --mgr $MGR"
  )
elif [[ $MGR == "short" ]]; then
  testCommands=(
      run_l3_longevity
      "./test_ipv4_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format excel --layer3_cols $COL_NAMES --debug --mgr $MGR"
  )
else
  testCommands=(
       #"../cpu_stats.py --duration 15"
      "./example_security_connection.py --num_stations $NUM_STA --ssid jedway-wpa-1 --passwd jedway-wpa-1 --radio $RADIO_USED --security wpa --debug"
      "./example_security_connection.py --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --radio $RADIO_USED --security wpa2 --debug"
      "./example_security_connection.py --num_stations $NUM_STA --ssid jedway-wep-48 --passwd 0123456789 --radio $RADIO_USED --security wep --debug"
      "./example_security_connection.py --num_stations $NUM_STA --ssid jedway-wpa3-1 --passwd jedway-wpa3-1 --radio $RADIO_USED --security wpa3 --debug"
      "./sta_connect2.py --dut_ssid $SSID_USED --dut_passwd $PASSWD_USED --dut_security $SECURITY"
      "./sta_connect_example.py"
      # want if [[ $DO_FILEIO = 1 ]]
      "./test_fileio.py --macvlan_parent eth2 --num_ports 3 --use_macvlans --first_mvlan_ip 192.168.92.13 --netmask 255.255.255.0 --test_duration 30s --gateway 192.168.92.1" # Better tested on Kelly, where VRF is turned off
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfping --dest $TEST_HTTP_IP --debug"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security $SECURITY --debug"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type iperf3 --debug"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfcurl --dest $TEST_HTTP_IP --file_output ${HOMEPATH}/Documents/lfcurl_output.txt --debug"
      "./testgroup.py --group_name group1 --add_group --list_groups --debug"
      testgroup_list_groups
      testgroup_list_connections
      testgroup_delete_group
      "./testgroup2.py --num_stations 4 --ssid lanforge --passwd password --security wpa2 --radio wiphy0 --group_name group0 --add_group"
      "./test_ipv4_connection.py --radio $RADIO_USED --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./test_ipv4_l4_urls_per_ten.py --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --num_tests 1 --requests_per_ten 600 --target_per_ten 600 --debug"
      "./test_ipv4_l4_wifi.py --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug"
      "./test_ipv4_l4.py --radio $RADIO_USED --num_stations 4 --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug"
      "./test_ipv4_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format excel --layer3_cols $COL_NAMES --traffic_type lf_udp --debug"
      "./test_ipv4_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format csv --layer3_cols $COL_NAMES --traffic_type lf_udp --debug"
      "./test_ipv4_l4_ftp_upload.py --upstream_port eth1 --radio $RADIO_USED --num_stations $NUM_STA --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED --test_duration 15s --debug"
      "./test_ipv6_connection.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./test_ipv6_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --cx_type tcp6 --debug"
      run_l3_longevity
      "./test_l3_powersave_traffic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      #"./test_l3_scenario_throughput.py -t 15s -sc test_l3_scenario_throughput" #always hangs the regression
      "./test_status_msg.py --action run_test " #this is all which is needed to run
      "./test_wanlink.py --debug"
      #"./ws_generic_monitor_test.py"
      #"../py-json/ws-sta-monitor.py --debug"
      "./create_bridge.py --radio $RADIO_USED --upstream_port eth1 --target_device sta0000 --debug"
      "./create_l3.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./create_l4.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./create_macvlan.py --radio $RADIO_USED --macvlan_parent eth1 --debug"
      "./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./create_vap.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug"
      "./create_vr.py --vr_name 2.vr0 --ports 2.br0,2.vap2 --services"
      "./create_qvlan.py --radio $RADIO_USED --qvlan_parent eth1"
      "./wlan_capacity_calculator.py -sta 11abg -t Voice -p 48 -m 106 -e WEP -q Yes -b 1 2 5.5 11 -pre Long -s N/A -co G.711 -r Yes -c Yes"
      "./wlan_capacity_calculator.py -sta 11n -t Voice -d 17 -ch 40 -gu 800 -high 9 -e WEP -q Yes -ip 5 -mc 42 -b 6 9 12 24 -m 1538 -co G.729 -pl Greenfield -cw 15 -r Yes -c Yes"
      "./wlan_capacity_calculator.py -sta 11ac -t Voice -d 9 -spa 3 -ch 20 -gu 800 -high 1 -e TKIP -q Yes -ip 3 -mc 0 -b 6 12 24 54 -m 1518 -co Greenfield -cw 15 -rc Yes"
  )
fi
#declare -A name_to_num
#if you want to run just one test as part of regression_test, you can call one test by calling its name_to_num identifier.
name_to_num=(
    ["example_security_connection"]=1
    ["test_ipv4_connection"]=2
    ["test_generic"]=3
    ["test_ipv4_l4_urls_per_ten"]=4
    ["test_ipv4_l4_wifi"]=5
    ["test_ipv4_l4"]=6
    ["test_ipv4_variable_time"]=7
    ["create_bridge"]=8
    ["create_l3"]=9
    ["create_l4"]=10
    ["create_macvlan"]=11
    ["create_station"]=12
    ["create_vap"]=13
    ["cpu_stats"]=14
    ["test_fileio"]=15
    ["testgroup"]=16
    ["test_ipv6_connection"]=17
    ["test_ipv6_variable_time"]=18
    ["test_l3_longevity"]=19
    ["test_l3_powersave_traffic"]=20
    ["test_l3_scenario_throughput"]=21
    ["test_status_msg"]=22
    ["test_wanlink"]=23
    ["wlan_theoretical_sta"]=24
    ["ws_generic_monitor_test"]=25
    ["sta_connect2"]=26
    ["wlan_capacity_calculator"]=27
    ["new_script"]=28
    ["sta_connect_example"]=29
)

function blank_db() {
    echo "Loading blank scenario..." >>"${HOMEPATH}/regression_file.txt"
    ./scenario.py --load BLANK >>"${HOMEPATH}/regression_file.txt"
    #check_blank.py
}

function echo_print() {
    echo "Beginning $CURR_TEST_NAME test..." >>"${HOMEPATH}/regression_file.txt"
}

function test() {
  if [[ $MGRLEN -gt 0 ]]; then
    ./scenario.py --load FACTORY_DFLT --mgr "${MGR}"
  else
    ./scenario.py --load FACTORY_DFLT
  fi

  echo ""
  echo "Test $CURR_TEST_NUM: $CURR_TEST_NAME"

  echo_print
  echo "$i"
  $i > "${TEST_DIR}/${NAME}.txt" 2> "${TEST_DIR}/${NAME}_stderr.txt"
  chmod 664 "${TEST_DIR}/${NAME}.txt"
  FILESIZE=$(stat -c%s "${TEST_DIR}/${NAME}_stderr.txt") || 0
  if (( FILESIZE > 0)); then
      results+=("<tr><td>${CURR_TEST_NAME}</td><td class='scriptdetails'>${i}</td>
                <td class='failure'>Failure</td>
                <td><a href=\"${URL2}/${NAME}.txt\" target=\"_blank\">STDOUT</a></td>
                <td><a href=\"${URL2}/${NAME}_stderr.txt\" target=\"_blank\">STDERR</a></td></tr>")
  else
      results+=("<tr><td>${CURR_TEST_NAME}</td><td class='scriptdetails'>${i}</td>
                <td class='success'>Success</td>
                <td><a href=\"${URL2}/${NAME}.txt\" target=\"_blank\">STDOUT</a></td>
                <td></td></tr>")
  fi
}

function run_test()  {
  if [[ ${#A} -gt 0 ]]; then
    for i in "${testCommands[@]}"; do
      NAME=$(cat < /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
      CURR_TEST_NAME=${i%%.py*}
      CURR_TEST_NAME=${CURR_TEST_NAME#./*}
      CURR_TEST_NUM="${name_to_num[$CURR_TEST_NAME]}"
      if [[ $A == "$CURR_TEST_NAME" ]]; then
        test
      fi
    done
  else
    for i in "${testCommands[@]}"; do
      NAME=$(cat < /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
      CURR_TEST_NAME=${i%%.py*}
      CURR_TEST_NAME=${CURR_TEST_NAME#./*}
      CURR_TEST_NUM="${name_to_num[$CURR_TEST_NAME]}"
      test
    done
  fi
}

function html_generator() {
    LAST_COMMIT=$(git log --pretty=oneline | tail -n 1)
    header="<html>
		<head>
		<title>Regression Test Results $NOW</title>
		<style>
		.success {
			background-color:green;
		}
		.failure {
			background-color:red;
		}
		table {
			border: 1px solid gray;
		}
		td {
			margin: 0;
			padding: 2px;
			font-family: 'Courier New',courier,sans-serif;
		}
		h1, h2, h3, h4 {
			font-family: 'Century Gothic',Arial,sans,sans-serif;
		}
		.scriptdetails {
			font-size: 10px;
		}
		</style>
		<script src=\"sortabletable.js\"></script>
		</head>
		<body>
		<h1>Regression Results</h1>
		<h4>$NOW</h4>
		<h4>$LAST_COMMIT</h4>
		<table border ='1' id='myTable2'>
		<tr>
        <th onclick=\"sortTable(0)\">Command Name</th>
        <th onclick=\"sortTable(1)\">Command</th>
        <th onclick=\"sortTable(2)\">Status</th>
        <th onclick=\"sortTable(3)\">STDOUT</th>
        <th onclick=\"sortTable(4)\">STDERR</th>
    </tr>"
    tail="</body>
		</html>"

    fname="${HOMEPATH}/html-reports/regression_file-${NOW}.html"
    echo "$header"  >> "$fname"
    echo "${results[@]}"  >> "$fname"
    echo "</table>" >> "$fname"
    echo "$tail" >> "$fname"
    if [ -f "${HOMEPATH}/html-reports/latest.html" ]; then
        rm -f "${HOMEPATH}/html-reports/latest.html"
    fi
    ln -s "${fname}" "${HOMEPATH}/html-reports/latest.html"
    HOSTNAME=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    content="View the latest regression report at ${HOSTNAME}/html-reports/latest.html"
    mail -s "Regression Results" scripters@candelatech.com <<<$content
}

results=()
NOW=$(date +"%Y-%m-%d-%H-%M")
NOW="${NOW/:/-}"
TEST_DIR="${REPORT_DATA}/${NOW}"
URL2="/report-data/${NOW}"
mkdir "${TEST_DIR}"
echo "Recording data to ${TEST_DIR}"

run_test
html_generator
#test generic and fileio are for macvlans
