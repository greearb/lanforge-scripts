#!/bin/bash
#
# NAME:
#   TR-398_Issue_4.bash
#
# PURPOSE:
#   Automation script to run the 'TR-398 Issue 4' Chamber View test.
#
# USAGE:
#   ./TR-398_Issue_4.bash
#
# SUMMARY:
#   This bash script performs the following:
#     - Creates/updates a DUT
#     - Creates/updates a Chamber View scenario
#     - Loads and builds the scenario
#     - Runs the 'TR-398 Issue 4' test, saving generated reports
#
#   See the README in the 'cv_examples' directory for more information.
set -x

# 0. TEST CONFIGURATION
#
# NOTE: If you change MGR to a remote IP, ensure that the IP address
#       is the same as the machine running the LANforge GUI.
#
# General configuration
MGR=localhost                               # Substitute for manager LANforge IP if running script remotely
MGR_PORT=8080                               # Unlikely this needs to change
TESTBED=Example-Testbed                     # Name of your testbed as it appears in report

LF_SCRIPTS=/home/lanforge/lanforge-scripts  # Modify this to point at your copy of LANforge scripts.
LF_PY_SCRIPTS=$LF_SCRIPTS/py-scripts        # Directory of LANforge Python scripts.
                                            # Useful if running this script in another directory.

TEST_CFG=TR-398_Issue_4.cfg                 # 'TR-398 Issue 4' test config file. If not specified in test script
                                            # CLI, then any unspecified options will use default test values.

RPT_DIR=/tmp/TR-398_Issue_4_reports         # Output directory for generated reports and associated data

# Chamber View Scenario name
CV_SCENARIO_NAME=TR-398_Issue_4_Automated_Test

# Upstream configuration
UPSTREAM_RSRC=1.2                           # In form Shelf.Resource. Shelf is almost always '1'
UPSTREAM_PORT=eth3                          # Name or alias of port. Usually an Ethernet port
UPSTREAM=$UPSTREAM_RSRC.$UPSTREAM_PORT      # Combined to form EID

# DUT configuration
#
# NOTE: Do not put quotes around these values as some of them
#       will be substituted into other strings.
DUT_NAME=TR-398_Issue_4_DUT                 # Name of DUT as it appears in report

SSID_2G=test_ssid_2ghz                      # 2.4GHz radio SSID
BSSID_2G=00:00:00:00:00:02                  # 2.4GHz radio BSSID
PASSWD_2G=test_passwd                       # 2.4GHz radio password
AUTH_2G=WPA2\|WPA3                          # 2.4GHz radio authentication type

SSID_5G=test_ssid_5ghz                      # 5GHz radio SSID
BSSID_5G=00:00:00:00:00:05                  # 5GHz radio BSSID
PASSWD_5G=test_passwd                       # 5GHz radio password
AUTH_5G=WPA2\|WPA3                          # 5GHz radio authentication type

SSID_6G=test_ssid_6ghz                      # 6GHz radio SSID
BSSID_6G=00:00:00:00:00:06                  # 6GHz radio BSSID
PASSWD_6G=test_passwd                       # 6GHz radio password
AUTH_6G=WPA3                                # 6GHz radio authentication type

# Allow sourcing a file to override the configuration values set above.
if [ -f local.cfg ]
then
    . local.cfg
fi


# 1. CREATE/UPDATE NEW DUT
#
# NOTE: Separate SSID option arguments with spaces and ensure the keys are lowercase
echo "Creating/Updating DUT \'$DUT_NAME\'"

$LF_PY_SCRIPTS/create_chamberview_dut.py \
    --lfmgr       $MGR \
    --port        $MGR_PORT \
    --dut_name    $DUT_NAME \
    --ssid        "ssid_idx=0 ssid=$SSID_2G security=$AUTH_2G password=$PASSWD_2G bssid=$BSSID_2G" \
    --ssid        "ssid_idx=1 ssid=$SSID_5G security=$AUTH_5G password=$PASSWD_5G bssid=$BSSID_5G" \
    --ssid        "ssid_idx=2 ssid=$SSID_6G security=$AUTH_6G password=$PASSWD_6G bssid=$BSSID_6G" \
    --sw_version  "beta-beta" \
    --hw_version  "beta-6e" \
    --serial_num  "001" \
    --model_num   "test"


# 2. CREATE/UPDATE AND BUILD CHAMBER VIEW SCENARIO
#
# See README in same directory for instructions on building a
# Chamber View scenario with the `create_chamberview.py` script.
printf "Build Chamber View Scenario with DUT \'$DUT_NAME\' and upstream \'$UPSTREAM_PORT\'"

$LF_PY_SCRIPTS/create_chamberview.py \
    --lfmgr $MGR \
    --port  $MGR_PORT \
    --delete_scenario \
    --create_scenario $CV_SCENARIO_NAME \
    --raw_line "profile_link $UPSTREAM_RSRC upstream 1 'DUT: $DUT_NAME LAN' NA $UPSTREAM_PORT,AUTO -1 NA"


# 3. RUN 'TR-398 Issue 4' TEST
#
# NOTE: The '--dut6' arg is not supported on LANforge pre-5.4.7, so use the '--raw_line' argument to set it.
#
# See README in same directory for instructions on building a
# Chamber View scenario with the 'lf_tr398v4_test.py' script.
printf "Starting TR-398 Issue 4 test"

$LF_PY_SCRIPTS/lf_tr398v4_test.py \
    --mgr                 $MGR \
    --port                $MGR_PORT \
    --lf_user             "lanforge" \
    --lf_password         "lanforge" \
    --instance_name       "tr398-instance" \
    --config_name         "test_con" \
    --test_rig            $TESTBED \
    --pull_report \
    --local_lf_report_dir $RPT_DIR \
    --raw_lines_file      $TEST_CFG \
    --dut2                "$DUT_NAME $SSID_2G $BSSID_2G (1)" \
    --dut5                "$DUT_NAME $SSID_5G $BSSID_5G (2)" \
    --dut6                "$DUT_NAME $SSID_6G $BSSID_6G (3)" \
    --upstream            $UPSTREAM \
    --set 'Calibrate 802.11AX Attenuators'    0 \
    --set 'Calibrate Virt-Sta Attenuators'    0 \
    --set '6.1.1 Receiver Sensitivity'        0 \
    --set '6.2.1 Maximum Connection'          0 \
    --set '6.2.2 Maximum Throughput'          1 \
    --set '6.2.3 Airtime Fairness'            0 \
    --set '6.2.4 Dual-Band Throughput'        0 \
    --set '6.2.5 Bi-Directional Throughput'   0 \
    --set '6.2.6 Latency'                     0 \
    --set '6.2.7 Quality of Service'          0 \
    --set '6.2.8 Multi-Band Throughput'       0 \
    --set '6.3.1 Range Versus Rate'           0 \
    --set '6.3.2 Spatial Consistency'         0 \
    --set '6.3.3 Peak Performance'            0 \
    --set '6.4.1 Multiple STAs Performance'   0 \
    --set '6.4.2 Multiple Assoc Stability'    0 \
    --set '6.4.3 Downlink MU-MIMO'            0 \
    --set '6.4.4 Multicast'                   0 \
    --set '6.5.1 Long Term Stability'         0 \
    --set '6.5.2 AP Coexistence'              0 \
    --set '6.5.3 Automatic Channel Selection' 0 \
    --set '6.5.4 BSS Color'                   0 \
    --set '6.6.1 Mesh Backhaul RvR'           0 \
    --set '6.6.2 Mesh Backhaul Node-2 RvR'    0 \
    --set '7.1.1 RSSI Accuracy'               0 \
    --set '7.1.2 Channel Utilization'         0

echo "Test is complete. Report can be found in $RPT_DIR"
