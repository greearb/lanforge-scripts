#!/bin/bash
set -veu
if [[ -z "$1" ]]; then
    echo "Usage: $0 <gui_ip> <resource> <port> <wpa_txt_filename>"
    exit 1
fi
GUI="${1:-127.0.0.1}"
POST_DATA="/tmp/post_data"

resource="${2:-UNSET}"
port="${3:-UNSET}"
config_file="${4:-UNSET}"
URL="cli-json/set_wifi_custom"
errors=0
if [[ $resource = UNSET ]]; then
    errors=$(( errors+1 ))
fi
if [[ $port = UNSET ]]; then
    errors=$(( errors+1 ))
fi
if [[ $config_file = UNSET ]]; then
    errors=$(( errors+1 ))
fi

if (( errors > 0 )); then
    echo "Usage: $0 <gui_ip> <resource> <port> <wpa_txt_filename>"
    echo "Example:"
    echo "        $0 localhost 1 wlan0 wifi.txt"
    exit 1
fi

CLEAN="{'shelf':1,'resource':$resource,'port':$port,'text':'[BLANK]'}"

echo "Clearing wifi_custom for $resource.$port"
curl -sv -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -X POST -d "$CLEAN"  \
    -sq "http://$GUI:8080/$URL"

# next post each line of the config
while IFS= read -r line; do
    rm -f "$POST_DATA"
    if [[ -z "$line" ]]; then
        continue
    fi
    b64=$(echo -n "$line" | base64 -w0)
    cat > $POST_DATA << _EOF2_
{
    "shelf": 1,
    "resource": $resource,
    "port": $port,
    "text-64": "$b64"
}
_EOF2_
    echo "- - - - - compressed post - -- - - - - - "
    cat $POST_DATA
    echo "- - - - - compressed post - -- - - - - - "

    curl -sv -H 'Accept: application/json' \
        -H 'Content-Type: application/json' \
        -X POST -d @$POST_DATA \
        -sq "http://$GUI:8080/$URL"
done < "$config_file"

#
