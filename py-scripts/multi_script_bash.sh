#!/bin/bash

atten_vals=(400 500 550 600)
len=${#atten_vals[@]}
pids=()

function runTest() {
    upstream_port = $0
    atten_val = $1
    mate-terminal --title=$upstream_port -- ./test_l3_longevity.py --test_duration 60s --polling_interval 1s --upstream_port $upstream_port --radio 'radio==wiphy0,stations==1,ssid==wactest,ssid_pw==[BLANK],security==open,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)' --endp_type lf_tcp --side_a_min_bps=0 --side_b_min_bps=600000000 --side_a_min_pdu=1500 --side_b_min_pdu=1500 --local_lf_report_dir /home/lanforge --no_pre_cleanup --no_stop_traffic --sta_start_offset 4 &
    
    
}
set -x
for (( i=0; i<$len; i++));
do
    curr_atten = ${#atten_vals[$i]}
    runTest "eth1" $curr_atten
    runTest "eth2" $curr_atten
    pids+=($(pgrep -u lanforge python3))
    processes_running = 0
    while (( $processes_running == 0))
    do
        sleep 5
        pids=()
        pids+=($(pgrep -u lanforge python3))
        if ((${#pids[@]} == 0)) ; then
            processes_running=$((processes_running+1))
        fi
        
    done
    echo "done $i"
done



