#!/bin/bash
# copy the wpa_text file to the lanforge and assign it to a station or stations
#set -veu
if [[ -z "$1" ]]; then
    echo "Usage: $0 <gui_ip> <resource_ip> <wpa_txt_filename> <list of station short eids>"
    exit 1
fi
q="'"
Q='"'
POST_DATA="/tmp/post_data"
GUI="${1}"; shift
HOSTIP="${1:-UNSET}"; shift
CONF_FILE="${1:-UNSET}"; shift
PORTS_JSON="/tmp/ports.json"
STA_EIDS=()

URL_WIFI_CUSTOM="cli-json/set_wifi_custom"
URL_ADD_STATION="cli-json/add_sta"
errors=0
if [[ $HOSTIP = UNSET ]]; then
    errors=$(( errors+1 ))
fi
if [[ $CONF_FILE = UNSET ]]; then
    errors=$(( errors+1 ))
fi
if [[ $CONF_FILE = UNSET ]]; then
    errors=$(( errors+1 ))
fi

if (( errors > 0 )); then
    echo "Usage: $0 <gui_ip> <resource_ip> <wpa_txt_filename> <list of station short eids>"
    echo "Example:"
    echo "        $0 localhost 192.168.1.101 wifi.txt 1.1.wlan0 1.wlan 1.sta0000"
    exit 1
fi

while (( $# )); do
    STA_EIDS+=("$1")
    shift
done
if (( "${#STA_EIDS[@]}" < 1 )); then
    echo "no stations provided"
    exit 1
fi


echo "Copying [$CONF_FILE] to [$HOSTIP]:"
scp "$CONF_FILE" "lanforge@$HOSTIP:/home/lanforge/"
if (( $? > 0 )); then
    echo "SCP failed, will not post config changes"
    exit 1
fi

# collect list of ports for this resource
for short_eid in "${STA_EIDS[@]}"; do
    resource="${short_eid%.*}"
    port="${short_eid#*.}"
    eid="1.$resource.$port"
    echo "resource[$resource] port[$port]"
    echo "Clearing wifi_custom for $resource.$port"
    JSON_CLEAN="{'shelf':1,'resource':$resource,'port':$port,'type':'NA','text':'[BLANK]'}"
    curl -sq -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        -X POST -d "$JSON_CLEAN"  \
        "http://$GUI:8080/$URL_WIFI_CUSTOM"
    if (( $? > 0 )); then
        echo "command failed, stopping"
        exit 1
    fi
    curl -sq -o $PORTS_JSON -s -H 'Accept: application/json'\
        "http://$GUI:8080/port/1/$resource/list?fields=port,parent+dev" \
        > $PORTS_JSON
    query=".interfaces[][$Q$eid$Q] | select(. != null).${Q}parent dev$Q"
    radio=$(jq "$query" $PORTS_JSON)
    if (( $? > 0 )); then
        echo "Unable to find record for port[$port]"
        continue
    fi


    echo "Setting $resource.$port radio[$radio] wpa_conf"
    cat > $POST_DATA << __EOF__
{
    "shelf":1,
    "resource":$resource,
    "sta_name":$port,
    "radio":$radio,
    "flags":0x20,
    "ssid":"NA",
    "key":"NA",
    "ap":"NA",
    "wpa_cfg_file":"/home/lanforge/$CONF_FILE",
    "mac":"NA",
    "mode":"NA",
    "rate":"NA",
    "flags_mask":0x20
}
__EOF__
    curl -sq -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        -X POST -d "@$POST_DATA"  \
        "http://$GUI:8080/$URL_ADD_STATION"
    if (( $? > 0 )); then
        echo "command failed, stopping"
        exit 1
    fi
done



#
