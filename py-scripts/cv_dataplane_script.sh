#!/bin/bash

# Define some common variables.  Change these to match the current testbed.
MGR=192.168.102.211
PORT=8080
DUT_NAME="TEST_DUT"
STA_PROFILE="STA-AX"

# Create/update new DUT.
#Replace my arguments with your setup.  Separate your ssid arguments with spaces and ensure the names are lowercase
echo "========Make DUT============"
./create_chamberview_dut.py --lfmgr ${MGR} -o ${PORT} --dut_name ${DUT_NAME} \
--ssid "ssid_idx=0 ssid=eero-mesh-lanforge security=WPA2 password=lanforge bssid=64:97:14:64:D9:06" 
#--ssid "ssid_idx=0 ssid=eero-mesh-lanforge security=WPA2 password=lanforge bssid=64:97:14:64:D9:06"


# Create/update chamber view scenario and apply and build it.
echo "========Build Chamber View Scenario=========="
#change the lfmgr to your system, set the radio to a working radio on your LANforge system, same with the ethernet port.
./create_chamberview.py --mgr ${MGR} --mgr_port ${PORT} -cs "TEST_SCENARIO"\
--line "Resource=1.1 Profile=STA-AX Amount=1 Uses-1=wiphy0 DUT="${DUT_NAME}" DUT_Radio=Radio-1 Freq=-1 " \
--line "Resource=1.1 Profile=upstream-dhcp Amount=1 Uses-1=eth2 Freq=-1 " \
--line "Resource=1.1 Profile=uplink-nat Amount=1 Uses-1=eth3 Uses-2=eth2 DUT=upstream DUT_Radio=LAN Freq=-1"

#Run dataplane test
echo "=============Run Dataplane Test==============="
./lf_dataplane_test.py --mgr ${MGR} -o ${PORT} --instance_name dataplane-inst --upstream 1.01.eth2 --download_speed "85%" --upload_speed "10%" --station 1.01.wlan0 \
 --dut {$DUT_NAME} --raw_line "pkts: Custom;60;MTU" --raw_line "cust_pkt_sz: 88 1200" --raw_line "directions: DUT Transmit" --raw_line "traffic_types:UDP"
--raw_line --duration "30s"
