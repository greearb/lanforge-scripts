#!/bin/bash

# This bash script creates/updates a DUT, creates/updates a chamberview scenario,
# loads and builds that scenario, runs wifi capacity test, and runs tr398v2 test

set -x

# Define some common variables.  This will need to be changed to match your own testbed.
# MGR is LANforge GUI machine
#MGR=192.168.100.209
MGR=localhost

GROUP_FILE=/tmp/lf_cv_rpt_filelocation.txt
TESTBED=Testbed-71
DUT=tr398-root
UPSTREAM_R=1.2
UPSTREAM_P=eth3
MGR_PORT=8080
SSID=test_ssid
PASSWD=test_passwd
BSSID2=00:00:00:00:00:02
BSSID5=00:00:00:00:00:05
BSSID6=00:00:00:00:00:06
TR398_CFG=my_tr398_71_cfg.txt
TR398_RPT_DIR=/tmp/my-report

UPSTREAM=${UPSTREAM_R}.${UPSTREAM_P}

# Allow sourcing a file to override the values set above.
if [ -f local.cfg ]
then
    . local.cfg
fi

# Create/update new DUT.
#Replace my arguments with your setup.  Separate your ssid arguments with spaces and ensure the names are lowercase
echo "Make new DUT"
./create_chamberview_dut.py --lfmgr ${MGR} --port ${MGR_PORT} --dut_name ${DUT} \
  --ssid "ssid_idx=0 ssid=$SSID security=WPA2 password=$PASSWD bssid=$BSSID2" \
  --ssid "ssid_idx=1 ssid=$SSID security=WPA2 password=$PASSWD bssid=$BSSID5" \
  --ssid "ssid_idx=2 ssid=$SSID security=WPA3 password=$PASSWD bssid=$BSSID6" \
  --sw_version "beta-beta" --hw_version beta-6e --serial_num 666 --model_num test

# Create/update chamber view scenario and apply and build it.
# Easiest way to get these lines is to build the scenario in the LANforge GUI and then
# copy/tweak what it shows in the 'Text Output' tab after saving and re-opening
# the scenario.
echo "Build Chamber View Scenario"
#change the lfmgr to your system, set the radio to a working radio on your LANforge system, same with the ethernet port.

./create_chamberview.py --lfmgr ${MGR} --port ${MGR_PORT} --delete_scenario \
  --create_scenario tr398-automated \
  --raw_line "profile_link 1.1 STA-AUTO 1 'DUT: tr398-root Radio-1' NA wiphy0,AUTO -1 NA" \
  --raw_line "profile_link 1.1 STA-AUTO 1 'DUT: tr398-root Radio-2' NA ALL-AX,AUTO -1 NA" \
  --raw_line "profile_link ${UPSTREAM_R} upstream 1 'DUT: tr398-root LAN' NA ${UPSTREAM_P},AUTO -1 NA" \
  --raw_line "profile_link 1.2 peer 1 'DUT: tr398-root LAN' NA eth2,AUTO -1 NA" \
  --raw_line "profile_link 1.2 STA-AUTO 1 'DUT: tr398-root Radio-2' NA wiphy0,AUTO -1 NA" \
  --raw_line "profile_link 1.2 STA-AUTO 1 'DUT: tr398-root Radio-2' NA ALL-AX,AUTO -1 NA" \
  --raw_line "profile_link 1.3 STA-AUTO 1 'DUT: tr398-root Radio-3' NA ALL-AX,AUTO -1 NA" \
  --raw_line "chamber root 429 269 NA 10.0" \
  --raw_line "chamber node-2 689 323 NA 10.0" \
  --raw_line "chamber sta 191 185 NA 10.0" \
  --raw_line "chamber node-1 685 146 NA 10.0"

# Run capacity test on the stations created by the chamber view scenario.
#config_name doesn't matter
echo "run wifi capacity test"
./lf_wifi_capacity_test.py --config_name Custom --pull_report \
  --mgr ${MGR} \
  --port ${MGR_PORT} \
  --instance_name testing --upstream $UPSTREAM --test_rig ${TESTBED} --graph_groups ${GROUP_FILE} \
  --batch_size "100" --protocol "TCP-IPv4" --duration 20000

rm ${GROUP_FILE}


# Run tr398 automated test
# NOTE:  --dut6 arg not supported in 5.4.6, so we use a RAW_LINE to set it.
# TR398_CFG file is a dump of the 'Show Config' text from TR398 Advanced
# Configuration tab.  This includes calibration data, so make sure you use the proper
# config file for your testbed.
# the first argument to --set is the configuration-key from the TR398 field's tooltip
# or the text of the label for the field.
./lf_tr398v2_test.py --mgr ${MGR} --port ${MGR_PORT} --lf_user lanforge --lf_password lanforge \
      --instance_name tr398-instance --config_name test_con \
      --upstream $UPSTREAM \
      --test_rig ${TESTBED} --pull_report \
      --local_lf_report_dir ${TR398_RPT_DIR} \
      --dut5 '${DUT} ${SSID} ${BSSID5} (2)' \
      --dut2 '${DUT} ${SSID} ${BSSID2} (1)' \
      --raw_lines_file ${TR398_CFG} \
      --raw_line "selected_dut6: ${DUT} ${SSID} ${BSSID6} (3)" \
      --set 'Calibrate 802.11AX Attenuators' 0 \
      --set 'Calibrate Virt-Sta Attenuators' 0 \
      --set '6.1.1 Receiver Sensitivity' 0 \
      --set '6.2.1 Maximum Connection' 0 \
      --set '6.2.2 Maximum Throughput' 1 \
      --set '6.2.3 Airtime Fairness' 0 \
      --set '6.2.4 Dual-Band Throughput' 0 \
      --set '6.2.5 Bi-Directional Throughput' 0 \
      --set '6.3.1 Range Versus Rate' 0 \
      --set '6.3.2 Spatial Consistency' 0 \
      --set '6.3.3 AX Peak Performance' 0 \
      --set '6.4.1 Multiple STAs Performance' 0 \
      --set '6.4.2 Multiple Assoc Stability' 0 \
      --set '6.4.3 Downlink MU-MIMO' 0 \
      --set '6.5.2 AP Coexistence' 0 \
      --set '6.5.1 Long Term Stability' 0

echo "TR398 report is found in ${TR398_RPT_DIR}"
