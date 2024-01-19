#!/bin/bash
# copy the wpa_text file to the lanforge and assign it to a station or stations
# set -veu
if [[ -z "$1" ]]; then
    echo "Usage: $0 <gui_ip> <resource_ip> <wpa_txt_filename> <list of station short eids>"
    exit 1
fi
q="'"
Q='"'


CONF_FILE="UNSET"
GUI="UNSET"
HOSTIP="UNSET"
PORTS_JSON="/tmp/ports.json"
POST_DATA="/tmp/post_data"
STA_EIDS=()
URL_WIFI_CUSTOM="cli-json/set_wifi_custom"
URL_ADD_STATION="cli-json/add_sta"

while getopts "f:g:r:s:" OPTION; do
    case "$OPTION" in
        f) CONF_FILE="$OPTARG";;
        g) GUI="$OPTARG";;
        r) HOSTIP="$OPTARG";;
        s) STA_EIDS+=("$OPTARG");;
        *) echo "Unknown option [$OPTION]"
    esac
done

errors=0
#if [[ $HOSTIP = UNSET ]]; then
#    errors=$(( errors+1 ))
#fi
if [[ $CONF_FILE = UNSET ]]; then
    errors=$(( errors+1 ))
fi
if [[ $CONF_FILE = UNSET ]]; then
    errors=$(( errors+1 ))
fi

if (( errors > 0 )); then
    echo "Usage: $0 -g <gui_ip> -r <resource_ip> -f <wpa_txt_filename> -s <list of station short eids>"
    echo "Example:"
    echo "        $0 -g localhost -r 192.168.1.101 -f wifi.txt -s 1.1.wlan0 -s 1.wlan1 -s 1.sta0000"
    echo " Please do not list radios from multiple chassis, that will not work."
    exit 1
fi

if (( "${#STA_EIDS[@]}" < 1 )); then
    echo "no stations provided"
    exit 1
fi

function post() {
    if [[ -z "${1:-}" ]]; then
        echo "Post wants URL-path and DATA string. Example: "
        echo "    post ${Q}json-cli/add_sta$Q ${Q}{'shelf':1,'resource':1,'radio':'wiphy0'}$Q "
        exit 1
    fi
    local url="$1"; shift
    if [[ -z "${1:-}" ]]; then
        echo "Post: no data"
        exit 1
    fi
    local post_data="$1"
    curl -sq -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        -X POST -d "$post_data"  \
        "http://$GUI:8080/$url" > /tmp/post_response
    echo -n "    "
    jq '.LAST|{command,response}' /tmp/post_response | tr -d "\n"

    echo "."
}

if [[ ! -z "$HOSTIP" ]] && [[ $HOSTIP != UNSET ]]; then
    echo "Copying [$CONF_FILE] to [$HOSTIP]:"
    scp "$CONF_FILE" "lanforge@$HOSTIP:/home/lanforge/"
    if (( $? > 0 )); then
        echo "SCP failed, will not post config changes"
        exit 1
    fi
fi
rm -f $PORTS_JSON

# collect list of ports for this resource
for short_eid in "${STA_EIDS[@]}"; do
    resource="${short_eid%.*}"
    port="${short_eid#*.}"
    eid="1.$resource.$port"
    #echo "resource[$resource] port[$port]"
    echo "Clearing wifi_custom for $resource.$port"
    JSON_CLEAN="{'shelf':1,'resource':$resource,'port':$port,'type':'NA','text':'[BLANK]'}"
    post "$URL_WIFI_CUSTOM" "$JSON_CLEAN"

    if (( $? > 0 )); then
        echo "command failed, stopping"
        exit 1
    fi
    if [[ ! -f $PORTS_JSON ]]; then
        curl -sq -o $PORTS_JSON -s -H 'Accept: application/json'\
            "http://$GUI:8080/port/1/$resource/list?fields=port,parent+dev"
    fi
    query=".interfaces[][$Q$eid$Q] | select(. != null).${Q}parent dev$Q"
    radio=$(jq "$query" $PORTS_JSON)
    if (( $? > 0 )); then
        echo "Unable to find radio record for port[$port]"
        continue
    fi

    echo "Setting $resource.$port radio[$radio] wpa_conf..."
    cat > $POST_DATA << __EOF__
{
    "shelf":1,
    "resource":$resource,
    "sta_name":$port,
    "radio":$radio,
    "flags": 0,
    "wpa_cfg_file":"DEFAULT",
    "mac":"NA",
    "mode":"0",
    "rate":"OS Default",
    "flags_mask":"32"
}
__EOF__
    post $URL_ADD_STATION "@$POST_DATA"

    cat > $POST_DATA << __EOF__
{
    "shelf":1,
    "resource":$resource,
    "sta_name":$port,
    "radio":$radio,
    "flags": 32,
    "wpa_cfg_file":"$CONF_FILE",
    "mac":"NA",
    "mode":"0",
    "rate":"OS Default",
    "flags_mask":"32"
}
__EOF__
    post $URL_ADD_STATION "@$POST_DATA"


    post "cli-json/nc_show_ports" "{'shelf':1, 'resource':$resource, 'port':$port}"
    if (( $? > 0 )); then
        echo "command failed, stopping"
        exit 1
    fi
done

#