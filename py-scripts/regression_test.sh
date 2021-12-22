#!/bin/bash
##########################
# Help
##########################
Help()
{
  echo "This bash script aims to automate the test process of all Candela Technologies test_* scripts in the lanforge-scripts directory to detect software regressions. The script can be run 2 ways and may include (via user input) the \"start_num\" and \"stop_num\" variables to select which tests should be run."
  echo "OPTION ONE: ./regression_test.sh : this command runs all the scripts in the array \"testCommands\""
  echo "OPTION TWO: ./regression_test.sh 4 5 :  this command runs py-script commands (in testCommands array) that include the py-script options beginning with 4 and 5 (inclusive) in case function ret_case_num."
  echo "Optional Variables:"
  echo "SSID is the name of the network you are testing against"
  echo "PASSWD is the password of said network"
  echo "SECURITY is the security protocol of the network"
  echo "MGR is the IP address of the device which has LANforge installed, if different from the system you are using."
  echo "A is used to call to test a specific command based on"
  echo "F is used to pass in an RC file which can store the credentials for running regression multiple times on your system"
  echo "H is used to test the help feature of each script, to make sure it renders properly."
  echo "L is used to give the IP address of the LANforge device which is under test"
  echo "Example command: ./regression_test.sh -s SSID -p PASSWD -w SECURITY -m MGR"
  echo "If using the help flag, put the H flag at the end of the command after other flags."
}


while getopts ":h:s:S:p:w:m:A:r:F:B:U:D:H:M:C:" option; do
  case "${option}" in
    h) # display Help
      Help
      exit 1
      ;;
    s)
      SSID_USED=${OPTARG}
      ;;
    S)
      SHORT="yes"
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
    B)
      BSSID=${OPTARG}
      ;;
    U)
      UPSTREAM=${OPTARG}
      ;;
    D)
      DUT5=${OPTARG}
      DUT2=${OPTARG}
      ;;
    H)
      ./lf_help_check.bash
      ;;
    M)
      RADIO2=${OPTARG}
      ;;
    C)
      RESOURCE=${OPTARG}
      ;;
    *)

      ;;
  esac
done

if [[ ${#MGR} -eq 0 ]]; then # Allow the user to change the radio they test against
  MGR="localhost"
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version)')

BuildVersion=$(wget $MGR:8080 -q -O - | jq '.VersionInfo.BuildVersion')
BuildDate=$(wget $MGR:8080 -q -O - | jq '.VersionInfo.BuildDate')
OS_Version=$(cat /etc/os-release | grep 'VERSION=')
HOSTNAME=$(cat /etc/hostname)
IP_ADDRESS=$(ip a sho eth0 | grep 'inet ' | cut -d "/" -f1 | cut -d "t" -f2)
PYTHON_ENVIRONMENT=$(which python3)

#SCENARIO_CHECK="$(python3 -c "import requests; print(requests.get('http://${MGR}:8080/events/').status_code)")"
#if [[ ${SCENARIO_CHECK} -eq 200 ]]; then
#  :
#else
#  echo "${SCENARIO_CHECK}"
#  echo "Your LANforge Manager is out of date. Regression test requires LANforge version 5.4.4 or higher in order to run"
#  echo "Please upgrade your LANforge using instructions found at https://www.candelatech.com/downloads.php#releases"
#  exit 1
#fi

python3 -m pip install --upgrade pip
if [ -d "/home/lanforge/lanforge_env" ]
then
  pip3 install --upgrade lanforge-scripts
else
  pip3 install --user -r ../requirements.txt --upgrade
fi

if [[ ${#SSID_USED} -eq 0 ]]; then #Network credentials
  SSID_USED="jedway-wpa2-x2048-5-3"
  PASSWD_USED="jedway-wpa2-x2048-5-3"
  SECURITY="wpa2"
fi

if [[ ${#RADIO_USED} -eq 0 ]]; then # Allow the user to change the radio they test against
  RADIO_USED="1.1.wiphy1"
fi

if [[ ${#RADIO2} -eq 0 ]]; then # Allow the user to change the radio they test against
  RADIO2="1.1.wiphy0"
fi
if [[ ${#UPSTREAM} -eq 0 ]]; then
  UPSTREAM="1.1.eth1"
fi

if [[ ${#BSSID} -eq 0 ]]; then
  BSSID="04:f0:21:2c:41:84"
fi

if [[ $RESOURCE -eq 0 ]]; then
  RESOURCE="1.1"
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

if [[ ${#DUT2} -eq 0 ]]; then
  DUT5="linksys-8450 j-wpa2-153 c4:41:1e:f5:3f:25 (1)"
  DUT2="linksys-8450 j-wpa2-153 c4:41:1e:f5:3f:25 (1)"
fi
#CURR_TEST_NUM=0
CURR_TEST_NAME="BLANK"

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
  ./test_l3_longevity.py --test_duration 15s --upstream_port $UPSTREAM --radio "radio==wiphy0 stations==4 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY" --radio "radio==wiphy1 stations==4 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY" --lfmgr "$MGR"
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
function create_bridge_and_station() {
  ./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR
  ./create_bridge.py --radio $RADIO_USED --upstream_port $UPSTREAM --target_device $RESOURCE.sta0000 --debug --mgr $MGR
}
function create_station_and_dataplane() {
      ./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR
      ./lf_dataplane_test.py --mgr $MGR --lf_user lanforge --lf_password lanforge \
          --instance_name dataplane-instance --config_name test_con --upstream $UPSTREAM \
          --dut linksys-8450 --duration 15s --station $RESOURCE.sta0001 \
          --download_speed 85% --upload_speed 0 \
          --test_rig Testbed-01 --pull_report \
          #--influx_host 192.168.100.153 --influx_port 8086 --influx_org Candela \
          #--influx_token=-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ== \
          #--influx_bucket ben \
          #--influx_tag testbed Ferndale-01
}
function create_dut_and_chamberview() {
        ./create_chamberview.py -m $MGR -cs 'regression_test' --delete_scenario \
        --line "Resource=$RESOURCE Profile=STA-AC Amount=1 Uses-1=$RADIO_USED Freq=-1 DUT=regression_dut DUT_RADIO=$RADIO_USED Traffic=http" \
        --line "Resource=$RESOURCE Profile=upstream Amount=1 Uses-1=$UPSTREAM Uses-2=AUTO Freq=-1 DUT=regression_dut DUT_RADIO=$RADIO_USED Traffic=http"
        ./create_chamberview_dut.py --lfmgr $MGR --dut_name regression_dut \
        --ssid "ssid_idx=0 ssid='$SSID_USED' security='$SECURITY' password='$PASSWD_USED' bssid=04:f0:21:2c:41:84"
    }

function create_station_and_sensitivity {
  ./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR
  ./lf_rx_sensitivity_test.py --mgr $MGR --port 8080 --lf_user lanforge --lf_password lanforge \
                      --instance_name rx-sensitivity-instance --config_name test_con --upstream $UPSTREAM \
                      --dut linksys-8450 --duration 15s --station $RESOURCE.sta0001 \
                      --download_speed 85% --upload_speed 0 \
                      --raw_line 'txo_preamble\: VHT' \
                      --raw_line 'txo_mcs\: 4 OFDM, HT, VHT;5 OFDM, HT, VHT;6 OFDM, HT, VHT;7 OFDM, HT, VHT' \
                      --raw_line 'spatial_streams\: 3' \
                      --raw_line 'bandw_options\: 80' \
                      --raw_line 'txo_sgi\: ON' \
                      --raw_line 'txo_retries\: No Retry' \
                      --raw_line 'txo_txpower\: 17' \
                      --test_rig Testbed-01 --pull_report \
                      #--influx_host 192.168.100.153 --influx_port 8086 --influx_org Candela \
                      #--influx_token=-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ== \
                      #--influx_bucket ben \
                      #--influx_tag testbed Ferndale-01
}
if [[ ${#SHORT} -gt 0 ]]; then
  testCommands=(
      "./lf_ap_auto_test.py \
              --mgr $MGR --port 8080 --lf_user lanforge --lf_password lanforge \
              --instance_name ap-auto-instance --config_name test_con --upstream $UPSTREAM \
              --dut5_0 '$DUT5' \
              --dut2_0 '$DUT2' \
              --radio2 $RADIO_USED \
              --radio2 $RADIO2 \
              --radio2 $RADIO2 \
              --set 'Basic Client Connectivity' 1 \
              --set 'Multi Band Performance' 1 \
              --set 'Skip 2.4Ghz Tests' 1 \
              --set 'Skip 5Ghz Tests' 1 \
              --set 'Throughput vs Pkt Size' 0 \
              --set 'Capacity' 0 \
              --set 'Stability' 0 \
              --set 'Band-Steering' 0 \
              --set 'Multi-Station Throughput vs Pkt Size' 0 \
              --set 'Long-Term' 0 \
              --pull_report \
              --local_lf_report_dir /home/matthew/html-reports/"


  )
else
  testCommands=(
      "./create_bond.py --network_dev_list $RESOURCE.eth0,$UPSTREAM --debug --mgr $MGR"
      create_bridge_and_station
      create_dut_and_chamberview
      "./create_l3.py --radio $RADIO_USED --ssid $SSID_USED --password $PASSWD_USED --security $SECURITY --debug --mgr $MGR --endp_a wiphy0 --endp_b wiphy1"
      "./create_l3_stations.py --mgr $MGR --radio $RADIO_USED --ssid $SSID_USED --password $PASSWD_USED --security $SECURITY --debug"
      "./create_l4.py --radio $RADIO_USED --ssid $SSID_USED --password $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_macvlan.py --radio 1.$RADIO_USED --macvlan_parent $UPSTREAM --debug --mgr $MGR"
      "./create_qvlan.py --first_qvlan_ip 192.168.1.50 --mgr $MGR --qvlan_parent $UPSTREAM"
      "./create_station.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./create_vap.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      #"./create_vr.py --mgr $MGR --vr_name 2.vr0 --ports 2.br0,2.vap2 --services 1.br0=dhcp,nat --services 1.vr0=radvd --debug"
      #./csv_convert
      #./csv_processor
      #./csv_to_grafana
      #./csv_to_influx
      #"./cv_manager.py --mgr $MGR --scenario FACTORY_DFLT"
      #"./cv_to_grafana --mgr $MGR "
      #"./docstrings.py --mgr $MGR"
      #"./scripts_deprecated/event_break_flood.py --mgr $MGR"
      "./example_security_connection.py --num_stations $NUM_STA --ssid $SSID_USED \
      --passwd $PASSWD_USED --radio $RADIO_USED --security wpa2 --debug --mgr $MGR"
      #./ftp_html.py
      #./grafana_profile
      "./lf_ap_auto_test.py \
        --mgr $MGR --port 8080 --lf_user lanforge --lf_password lanforge \
        --instance_name ap-auto-instance --config_name test_con --upstream $UPSTREAM \
        --dut5_0 '$DUT5' \
        --dut2_0 '$DUT2' \
        --max_stations_2 64 \
        --max_stations_5 64 \
        --max_stations_dual 64 \
        --radio2 $RADIO_USED \
        --radio2 $RADIO2 \
        --set 'Basic Client Connectivity' 1 \
        --set 'Multi Band Performance' 1 \
        --set 'Skip 2.4Ghz Tests' 1 \
        --set 'Skip 5Ghz Tests' 1 \
        --set 'Throughput vs Pkt Size' 0 \
        --set 'Capacity' 0 \
        --set 'Stability' 0 \
        --set 'Band-Steering' 0 \
        --set 'Multi-Station Throughput vs Pkt Size' 0 \
        --set 'Long-Term' 0 \
        --pull_report"
      #"./lf_atten_mod_test.py --host $MGR --debug"
      #./lf_csv
      #./lf_dataplane_config
      create_station_and_dataplane
      #"./lf_dut_sta_vap_test.py --manager $MGR --radio $RADIO_USED \
      #    --num_sta 1 --sta_id 1 --ssid $SSID_USED --security $SECURITY --upstream $UPSTREAM \
      #    --protocol lf_udp --min_mbps 1000 --max_mbps 10000 --duration 1"
      "./lf_graph.py --mgr $MGR"
      "./lf_mesh_test.py --mgr $MGR --upstream $UPSTREAM --raw_line 'selected_dut2 RootAP wactest $BSSID'"
      "./lf_multipsk.py --mgr $MGR --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --radio $RADIO_USED --debug"
      "./lf_report.py"
      "./lf_report_test.py"
      # "./lf_rvr_test.py"
      create_station_and_sensitivity
      "./lf_sniff_radio.py \
                               --mgr $MGR \
                               --mgr_port 8080 \
                               --outfile /home/lanforge/test_sniff.pcap \
                               --duration 20 \
                               --channel 52 \
                               --radio_mode AUTO"
      "./lf_snp_test.py --help"
      "./lf_tr398_test.py --mgr $MGR --upstream $UPSTREAM"
      #./lf_webpage
      "./lf_wifi_capacity_test.py --mgr $MGR --port 8080 --lf_user lanforge --lf_password lanforge \
             --instance_name this_inst --config_name test_con --upstream $UPSTREAM --batch_size 1,5,25,50,100 --loop_iter 1 \
             --protocol UDP-IPv4 --duration 6000 --pull_report --ssid $SSID_USED --paswd $PASSWD_USED --security $SECURITY\
             --test_rig Testbed-01 --create_stations --stations $RESOURCE.sta0000,$RESOURCE.sta0001"
      "./measure_station_time_up.py --radio $RADIO_USED --num_stations 3 --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED \
      --debug --report_file measure_station_time_up.pkl --radio2 wiphy1 --mgr $MGR"
      "./create_station.py --mgr $MGR --radio $RADIO_USED --security $SECURITY --ssid $SSID_USED --passwd $PASSWD_USED && ./modify_station.py \
                   --mgr $MGR \
                   --radio $RADIO_USED \
                   --station $RESOURCE.sta0000 \
                   --security $SECURITY \
                   --ssid $SSID_USED \
                   --passwd $PASSWD_USED \
                   --enable_flag osen_enable \
                   --disable_flag ht160_enable \
                   --debug"
      #recordinflux.py
      #"./run_cv_scenario.py --lfmgr $MGR --lanforge_db 'handsets' --cv_test 'WiFi Capacity' --test_profile 'test-20' --cv_scenario ct-us-001"
      #"./rvr_scenario.py --lfmgr $MGR --lanforge_db 'handsets' --cv_test Dataplane --test_profile http --cv_scenario ct-us-001"
      #scenario.py
      #./sta_connect_bssid_mac.py
      "./sta_connect_example.py --mgr $MGR --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --radio $RADIO_USED --upstream_port $UPSTREAM --test_duration 15s --debug"
      "./sta_connect.py --mgr $MGR --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --radio $RADIO_USED --upstream_port $UPSTREAM --test_duration 15s --dut_bssid 04:F0:21:CB:01:8B --debug"
      "./sta_connect2.py --dest $MGR --dut_ssid $SSID_USED --dut_passwd $PASSWD_USED --dut_security $SECURITY --radio $RADIO_USED --upstream_port $UPSTREAM"
      "./sta_scan_test.py --mgr $MGR --ssid $SSID_USED --security $SECURITY --passwd $PASSWD_USED --radio $RADIO_USED --debug"
      #station_layer3.py
      #stations_connected.py
      #"./test_1k_clients_jedtest.py
      # --mgr $MGR
      # --mgr_port 8080
      # --sta_per_radio 300
      # --test_duration 3m
      # --a_min 1000
      # --b_min 1000
      # --a_max 0
      # --b_max 0
      # --debug"
      #test_client_admission.py
      "./test_fileio.py --macvlan_parent $UPSTREAM --num_ports 3 --use_macvlans --first_mvlan_ip 10.40.92.13 --netmask 255.255.255.0 --gateway 192.168.92.1 --test_duration 30s --mgr $MGR" # Better tested on Kelly, where VRF is turned off
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfping --dest $TEST_HTTP_IP --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security $SECURITY --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type iperf3 --debug --mgr $MGR"
      "./test_generic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED  --security $SECURITY --num_stations $NUM_STA --type lfcurl --dest $TEST_HTTP_IP --file_output ${HOMEPATH}/Documents/lfcurl_output.txt --debug --mgr $MGR"
      "./testgroup.py --group_name group1 --add_group --list_groups --debug --mgr $MGR"
      "./testgroup2.py --num_stations 4 --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --radio $RADIO_USED --group_name group0 --add_group --mgr $MGR"
      "./test_ip_connection.py --radio $RADIO_USED --num_stations $NUM_STA --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./test_ip_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format excel --layer3_cols $COL_NAMES --debug --mgr $MGR  --traffic_type lf_udp"
      "./test_ip_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --output_format csv --layer3_cols $COL_NAMES --debug --mgr $MGR  --traffic_type lf_udp"
      "./test_ip_connection.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR --ipv6"
      "./test_ip_variable_time.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --test_duration 15s --debug --mgr $MGR --ipv6 --traffic_type lf_udp"
      "./test_ipv4_ps.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR --radio2 $RADIO2"
      "./test_ipv4_ttls.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      "./test_l3_longevity.py --mgr $MGR --endp_type 'lf_tcp' --upstream_port $UPSTREAM --radio \
      'radio==$RADIO_USED stations==10 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY' --radio \
      'radio==$RADIO2 stations==1 ssid==$SSID_USED ssid_pw==$PASSWD_USED security==$SECURITY' --test_duration 5s --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000  -o longevity.csv"
      "./test_l3_powersave_traffic.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR"
      #"./test_l3_scenario_throughput.py -t 15s -sc test_l3_scenario_throughput -m $MGR"
      #./test_l3_unicast_traffic_gen
      #./test_l3_unicast_traffic_gen
      #./test_l3_WAN_LAN
      "./test_l4.py --radio $RADIO_USED --ssid $SSID_USED --passwd $PASSWD_USED --security $SECURITY --debug --mgr $MGR --test_duration 15s"
      "./test_status_msg.py --debug --mgr $MGR" #this is all which is needed to run
      #"./test_wanlink.py --name my_wanlink4 --latency_A 20 --latency_B 69 --rate 1000 --jitter_A 53 --jitter_B 73 --jitter_freq 6 --drop_A 12 --drop_B 11 --debug --mgr $MGR"
      #./test_wpa_passphrases
      #./tip_station_powersave
      #./video_rates
      "./wlan_capacity_calculator.py -sta 11abg -t Voice -p 48 -m 106 -e WEP -q Yes -b 1 2 5.5 11 -pre Long -s N/A -co G.711 -r Yes -c Yes"
      "./wlan_capacity_calculator.py -sta 11n -t Voice -d 17 -ch 40 -gu 800 -high 9 -e WEP -q Yes -ip 5 -mc 42 -b 6 9 12 24 -m 1538 -co G.729 -pl Greenfield -cw 15 -r Yes -c Yes"
      "./wlan_capacity_calculator.py -sta 11ac -t Voice -d 9 -spa 3 -ch 20 -gu 800 -high 1 -e TKIP -q Yes -ip 3 -mc 0 -b 6 12 24 54 -m 1518 -co Greenfield -cw 15 -rc Yes"
      #"./ws_generic_monitor_test.py --mgr $MGR"
      "python3 -c 'import lanforge_scripts'"
  )
fi
#declare -A name_to_num
#if you want to run just one test as part of regression_test, you can call one test by calling its name_to_num identifier.
name_to_num=(
    ["create_bond"]=1
    ["create_bridge"]=2
    ["create_l3"]=3
    ["create_l4"]=4
    ["create_macvlan"]=5
    ["create_qvlan"]=6
    ["create_station"]=7
    ["create_va"]=8
    ["create_vr"]=9
    ["create_wanlink"]=10
    ["csv_convert"]=11
    ["csv_processor"]=12
    ["csv_to_grafana"]=13
    ["csv_to_influx"]=14
    ["cv_manager"]=15
    ["cv_to_grafana"]=16
    ["docstrings"]=17
    ["event_breaker"]=18
    ["event_flood"]=19
    ["example_security_connection"]=20
    ["ftp_html"]=21
    ["ghost_profile"]=22
    ["grafana_profile"]=23
    ["html_template"]=24
    ["influx"]=25
    ["layer3_test"]=26
    ["layer4_test"]=27
    ["lf_ap_auto_test"]=28
    ["lf_atten_mod_test"]=29
    ["lf_csv"]=30
    ["lf_dataplane_config"]=31
    ["lf_dataplane_test"]=32
    ["lf_dut_sta_vap_test"]=34
    ["lf_ft"]=35
    ["lf_ftp_test"]=36
    ["lf_graph"]=37
    ["lf_influx_db"]=38
    ["lf_mesh_test"]=39
    ["lf_multipsk"]=40
    ["lf_report"]=41
    ["lf_report_test"]=42
    ["lf_rvr_test"]=43
    ["lf_rx_sensitivity_test"]=44
    ["lf_sniff_radio"]=45
    ["lf_snp_test"]=46
    ["lf_tr398_test"]=47
    ["lf_webpage"]=48
    ["lf_wifi_capacity_test"]=49
    ["measure_station_time_u"]=50
    ["modify_station"]=51
    ["modify_va"]=52
    ["run_cv_scenario"]=53
    ["rvr_scenario"]=54
    ["scenario"]=55
    ["sta_connect"]=56
    ["sta_connect2"]=57
    ["sta_connect_bssid_mac"]=58
    ["sta_connect_example"]=59
    ["sta_connect_multi_example"]=60
    ["sta_connect_bssid_mac"]=61
    ["sta_connect_example"]=62
    ["sta_connect_multi_example"]=63
    ["sta_scan_test"]=64
    ["station_layer3"]=65
    ["stations_connected"]=66
    ["sta_scan_test"]=67
    ["station_layer3"]=68
    ["stations_connected"]=69
    ["test_1k_clients_jedtest"]=70
    ["test_client_admission"]=71
    ["test_fileio"]=72
    ["test_generic"]=73
    ["test_generic"]=74
    ["test_generic"]=75
    ["test_generic"]=76
    ["testgrou"]=77
    ["testgroup_list_groups"]=78
    ["testgroup_list_connections"]=79
    ["testgroup_delete_grou"]=80
    ["testgroup2"]=81
    ["test_ip_connection"]=82
    ["test_ip_variable_time"]=83
    ["test_ip_variable_time"]=84
    ["test_ip_connection"]=85
    ["test_ip_variable_time"]=86
    ["test_ipv4_ps"]=87
    ["test_ipv4_ttls"]=88
    ["test_l3_longevit"]=89
    ["test_l3_powersave_traffic"]=90
    ["test_l3_scenario_throughput"]=91
    ["test_l3_unicast_traffic_gen"]=92
    ["test_l3_unicast_traffic_gen"]=93
    ["test_l3_WAN_LAN"]=94
    ["test_l4"]=95
    ["test_status_msg"]=96
    ["test_wanlink"]=97
    ["test_wpa_passphrases"]=98
    ["tip_station_powersave"]=99
    ["vap_stations_example"]=100
    ["video_rates"]=101
    ["wlan_capacity_calculator"]=102
    ["wlan_capacity_calculator"]=103
    ["wlan_capacity_calculator"]=104
    ["ws_generic_monitor_test"]=105
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
    ./scenario.py --load BLANK --mgr "${MGR}"
  else
    ./scenario.py --load BLANK
  fi

  echo ""
  echo "Test $CURR_TEST_NAME"

  echo_print
  echo "$testcommand"
  start=$(date +%s)
  # this command saves stdout and stderr to the stdout file, and has a special file for stderr text.
  # Modified from https://unix.stackexchange.com/a/364176/327076
  FILENAME="${TEST_DIR}/${NAME}"
  { eval "$testcommand" 2>&1 >&3 3>&- | tee "${FILENAME}_stderr.txt" 3>&-; } > "${FILENAME}.txt" 3>&1
  chmod 664 "${FILENAME}.txt"
  FILESIZE=$(stat -c%s "${FILENAME}_stderr.txt") || 0
  # Check to see if the error is due to LANforge
  ERROR_DATA=$(cat "${FILENAME}_stderr.txt")
  if [[ $ERROR_DATA =~ "LANforge Error Messages" ]]
  then
    LANforgeError="Lanforge Error"
    echo "LANforge Error"
  else
    LANforgeError=""
  fi
  end=$(date +%s)
  execution="$((end-start))"
  TEXT=$(cat "${FILENAME}".txt)
  STDERR=""
  if [[ $TEXT =~ "tests failed" ]]
  then 
    TEXTCLASS="partial_failure"
    TDTEXT="Partial Failure"
    echo "Partial Failure"
  elif [[ $TEXT =~ "FAILED" ]]
  then
    TEXTCLASS="partial_failure"
    TDTEXT="ERROR"
    echo "ERROR"
  else 
    TEXTCLASS="success"
    TDTEXT="Success"
    echo "No errors detected"
  fi

  if (( FILESIZE > 0))
  then
    TEXTCLASS="failure"
    TDTEXT="Failure"
    STDERR="<a href=\"${URL2}/${NAME}_stderr.txt\" target=\"_blank\">STDERR</a>"
  fi
  results+=("<tr><td>${CURR_TEST_NAME}</td>
                       <td class='scriptdetails'>${testcommand}</td>
                       <td class='${TEXTCLASS}'>$TDTEXT</td>
                       <td>${execution}</td>
                       <td><a href=\"${URL2}/${NAME}.txt\" target=\"_blank\">STDOUT</a></td>
                       <td>${STDERR}</td>
                       <td>${LANforgeError}</td>
                       </tr>")
}

function start_tests()  {
  if [[ ${#A} -gt 0 ]]; then
    for testcommand in "${testCommands[@]}"; do
      NAME=$(cat < /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
      CURR_TEST_NAME=${testcommand%%.py*}
      CURR_TEST_NAME=${CURR_TEST_NAME#./*}
      #CURR_TEST_NUM="${name_to_num[$CURR_TEST_NAME]}"
      if [[ $A == "$CURR_TEST_NAME" ]]; then
        test
      fi
    done
  else
    for testcommand in "${testCommands[@]}"; do
      NAME=$(cat < /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
      CURR_TEST_NAME=${testcommand%%.py*}
      CURR_TEST_NAME=${CURR_TEST_NAME#./*}
      #CURR_TEST_NUM="${name_to_num[$CURR_TEST_NAME]}"
      test
    done
  fi
}

function html_generator() {
    LAST_COMMIT=$(git log --pretty=oneline | head -n 1)
    header="<!DOCTYPE html>
<html>
<head>
<title>${HOSTNAME} Regression Test Results $NOW</title>
<link rel='stylesheet' href='report.css' />
<style>
body {
    font-family: 'Century Gothic';
}
.success {
    background-color:green;
}
.failure {
    background-color:red;
}
.partial_failure {
  background-color:yellow;
}
table {
    border: 0 none;
    border-collapse: collapse;
}
td {
    margin: 0;
    padding: 2px;
    font-family: 'Century Gothic',Arial,Verdana,Tahoma,'Trebuchet MS',Impact,sans-serif;
    border: 1px solid gray;
}
h1, h2, h3, h4 {
    font-family: 'Century Gothic',Arial,Verdana,Tahoma,'Trebuchet MS',Impact,sans-serif;
}
.scriptdetails {
    font-size: 10px;
    font-family:'Lucida Typewriter','Andale Mono','Courier New',Courier,FreeMono,monospace;
}
td.testname {
    font-size:14px;
    font-weight: bold;
}
</style>
<script src=\"sortabletable.js\"></script>
</head>
<body>
    <h1>Regression Results</h1>
    <h4 id=\"timestamp\">$NOW</h4>
    <h4 id=\"Git Commit\">$LAST_COMMIT</h4>
    <h4>Test results</h4>
    <table border ='1' id='myTable2' id='SuiteResults'>
    <thead>
        <tr>
            <th onclick=\"sortTable('myTable2', 0)\">Command Name</th>
            <th onclick=\"sortTable('myTable2', 1)\">Command</th>
            <th onclick=\"sortTable('myTable2', 2)\">Status</th>
            <th onclick=\"sortTable('myTable2', 3)\">Execution time</th>
            <th onclick=\"sortTable('myTable2', 4)\">STDOUT</th>
            <th onclick=\"sortTable('myTable2', 5)\">STDERR</th>
            <th onclick=\"sortTable('myTable2', 6)\">LANforge Error</th>
        </tr>
    </thead>
    <tbody>"
    f="</body></html>"

    fname="${HOMEPATH}/html-reports/regression_file-${NOW}.html"
    echo "$header"  >> "$fname"
    echo "${results[@]}"  >> "$fname"
    echo "</tbody>
    </table>
    <br />
    <h3>System information</h3>
    <table id=\"SystemInformation\" border ='1'>
    <thead>
      <tr>
        <th>Python version</th>
        <th>LANforge version</th>
        <th>LANforge build date</th>
        <th>OS Version</th>
        <th>Hostname</th>
        <th>IP Address</th>
        <th>Python Environment</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td id='PythonVersion'>${PYTHON_VERSION}</td>
        <td id='LANforgeVersion'>${BuildVersion}</td>
        <td id='LANforgeBuildDate'>${BuildDate}</td>
        <td id='OS_Version'>${OS_Version}</td>
        <td id='Hostname'>${HOSTNAME}</td>
        <td id='ip_address'>${IP_ADDRESS}</td>
        <td id='python_environment'>${PYTHON_ENVIRONMENT}</td>
      </tr>
    </tbody>
    </table>
    <script> sortTable('myTable2', 2); </script>
" >> "$fname"
    echo "$tail" >> "$fname"
    if [ -f "${HOMEPATH}/html-reports/latest.html" ]; then
        rm -f "${HOMEPATH}/html-reports/latest.html"
    fi
    ln -s "${fname}" "${HOMEPATH}/html-reports/latest.html"
    echo "Saving HTML file to disk"
    #HOSTNAME=$(ip -4 addr show enp3s0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    #content="View the latest regression report at /html-reports/latest.html"
    #echo "${content}"
    #mail -s "Regression Results" scripters@candelatech.com <<<$content
}

results=()
NOW=$(date +"%Y-%m-%d-%H-%M")
NOW="${NOW/:/-}"
TEST_DIR="${REPORT_DATA}/${NOW}"
URL2="/report-data/${NOW}"
mkdir "${TEST_DIR}"
echo "Recording data to $TEST_DIR"

start_tests
html_generator
