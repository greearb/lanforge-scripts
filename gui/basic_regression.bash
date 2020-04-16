#!/bin/bash

# Run some automated GUI tests, save the results
# Example of how to run this and override LFMANAGER default settings.  Other values can
# be over-ridden as well.
#
#  LFMANAGER=192.168.100.156 ./basic_regression.bash
#
# Run subset of tests
#  LFMANAGER=192.168.100.156 DEFAULT_ENABLE=0 DO_SHORT_AP_STABILITY_RESET=1 ./basic_regression.bash
#
#

AP_AUTO_CFG_FILE=${AP_AUTO_CFG_FILE:-test_configs/AP-Auto-ap-auto-32-64-dual.txt}

# LANforge target machine
LFMANAGER=${LFMANAGER:-localhost}

# LANforge GUI machine (may often be same as target)
GMANAGER=${GMANAGER:-localhost}
GMPORT=${GMPORT:-3990}
MY_TMPDIR=${MY_TMPDIR:-/tmp}

# Test configuration (10 minutes by default, in interest of time)
STABILITY_DURATION=${STABILITY_DURATION:-600}

# Tests to run
DEFAULT_ENABLE=${DEFAULT_ENABLE:-1}
DO_SHORT_AP_BASIC_CX=${DO_SHORT_AP_BASIC_CX:-$DEFAULT_ENABLE}
DO_SHORT_AP_TPUT=${DO_SHORT_AP_TPUT:-$DEFAULT_ENABLE}
DO_SHORT_AP_STABILITY_RESET=${DO_SHORT_AP_STABILITY_RESET:-$DEFAULT_ENABLE}
DO_SHORT_AP_STABILITY_RADIO_RESET=${DO_SHORT_AP_STABILITY_RADIO_RESET:-$DEFAULT_ENABLE}
DO_SHORT_AP_STABILITY_NO_RESET=${DO_SHORT_AP_STABILITY_NO_RESET:-$DEFAULT_ENABLE}

DATESTR=$(date +%F-%T)
RSLTS_DIR=${RSLTS_DIR:-basic_regression_results_$DATESTR}


# Probably no config below here
AP_AUTO_CFG=ben
RPT_TMPDIR=${MY_TMPDIR}/lf_reports

mkdir -p $RSLTS_DIR

# Load AP-Auto config file
../lf_testmod.pl --mgr $LFMANAGER --action set --test_name AP-Auto-$AP_AUTO_CFG --file $AP_AUTO_CFG_FILE

# Clean out temp report directory
if [ -d $RPT_TMPDIR ]
then
    rm -fr $RPT_TMPDIR/*
fi

# Run basic-cx test
if [ "_$DO_SHORT_AP_BASIC_CX" == "_1" ]
then
    ../lf_gui_cmd.pl --manager $GMANAGER --port $GMPORT --ttype "AP-Auto" --tname ap-auto-ben --tconfig $AP_AUTO_CFG \
        --rpt_dest $RPT_TMPDIR > $MY_TMPDIR/basic_regression_log.txt 2>&1
    mv $RPT_TMPDIR/* $RSLTS_DIR/ap_auto_basic_cx
    mv $MY_TMPDIR/basic_regression_log.txt $RSLTS_DIR/ap_auto_basic_cx/test_automation.txt
fi

# Run Throughput, Dual-Band, Capacity test in a row, the Capacity will use results from earlier
# tests.
if [ "_$DO_SHORT_AP_TPUT" == "_1" ]
then
    ../lf_gui_cmd.pl --manager $GMANAGER --port $GMPORT --ttype "AP-Auto" --tname ap-auto-ben --tconfig $AP_AUTO_CFG \
        --modifier_key "Basic Client Connectivity" --modifier_val false \
        --modifier_key "Throughput vs Pkt Size" --modifier_val true \
        --modifier_key "Dual Band Performance" --modifier_val true \
        --modifier_key "Capacity" --modifier_val true \
        --rpt_dest $RPT_TMPDIR > $MY_TMPDIR/basic_regression_log.txt 2>&1
    mv $RPT_TMPDIR/* $RSLTS_DIR/ap_auto_capacity
    mv $MY_TMPDIR/basic_regression_log.txt $RSLTS_DIR/ap_auto_capacity/test_automation.txt
fi

# Run Stability test (single port resets, voip, tcp, udp)
if [ "_$DO_SHORT_AP_STABILITY_RESET" == "_1" ]
then
    ../lf_gui_cmd.pl --manager $GMANAGER --port $GMPORT --ttype "AP-Auto" --tname ap-auto-ben --tconfig $AP_AUTO_CFG \
        --modifier_key "Basic Client Connectivity" --modifier_val false \
        --modifier_key "Stability" --modifier_val true \
        --modifier_key "Stability Duration:" --modifier_val $STABILITY_DURATION \
        --rpt_dest  $RPT_TMPDIR > $MY_TMPDIR/basic_regression_log.txt 2>&1
    mv $RPT_TMPDIR/* $RSLTS_DIR/ap_auto_stability_reset_ports
    mv $MY_TMPDIR/basic_regression_log.txt $RSLTS_DIR/ap_auto_stability_reset_ports/test_automation.txt
fi

# Run Stability test (radio resets, voip, tcp, udp)
if [ "_$DO_SHORT_AP_STABILITY_RADIO_RESET" == "_1" ]
then
    ../lf_gui_cmd.pl --manager $GMANAGER --port $GMPORT --ttype "AP-Auto" --tname ap-auto-ben --tconfig $AP_AUTO_CFG \
        --modifier_key "Basic Client Connectivity" --modifier_val false \
        --modifier_key "Stability" --modifier_val true \
        --modifier_key "Stability Duration:" --modifier_val $STABILITY_DURATION \
        --modifier_key "Reset Radios" --modifier_val true \
        --rpt_dest  $RPT_TMPDIR > $MY_TMPDIR/basic_regression_log.txt 2>&1
    mv $RPT_TMPDIR/* $RSLTS_DIR/ap_auto_stability_reset_radios
    mv $MY_TMPDIR/basic_regression_log.txt $RSLTS_DIR/ap_auto_stability_reset_radios/test_automation.txt
fi

# Run Stability test (no resets, no voip, tcp, udp)
if [ "_$DO_SHORT_AP_STABILITY_NO_RESET" == "_1" ]
then
    ../lf_gui_cmd.pl --manager $GMANAGER --port $GMPORT --ttype "AP-Auto" --tname ap-auto-ben --tconfig $AP_AUTO_CFG \
        --modifier_key "Basic Client Connectivity" --modifier_val false \
        --modifier_key "Stability" --modifier_val true \
        --modifier_key "Stability Duration:" --modifier_val $STABILITY_DURATION \
        --modifier_key "VOIP Call Count:" --modifier_val 0 \
        --modifier_key "Concurrent Ports To Reset:" --modifier_val 0 \
        --rpt_dest  $RPT_TMPDIR > $MY_TMPDIR/basic_regression_log.txt 2>&1
    mv $RPT_TMPDIR/* $RSLTS_DIR/ap_auto_stability_no_reset
    mv $MY_TMPDIR/basic_regression_log.txt $RSLTS_DIR/ap_auto_stability_no_reset/test_automation.txt
fi
