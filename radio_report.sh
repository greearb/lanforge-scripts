#!/bin/bash

radio_list=(`ls -d /sys/class/ieee80211/*`)

for radio_path in "${radio_list[@]}"; do
    radio="${radio_path##*/}"
    #echo -n "$radio_path: $radio "
    if [ -d "/sys/kernel/debug/ieee80211/${radio}/ath9k/" ]; then
        echo "ath9k Vsta:200 APs:32 apclients:2048"
    elif [ -d "/sys/kernel/debug/ieee80211/${radio}/ath10k/" ]; then
        echo "ath10k Vsta:64 APs:24 ap-clients:127"
    else 
        echo "other Vsta:1 APs:0 ap-clients:0"
    fi
done
