#!/bin/bash
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Create ten stations and ten udp L3 cxes. Create a tcp CX that has a
# better ToS and check the latency on that tcp connection.
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

station_host="ct524-genia.jbr"
num_stations=10
resource=1
upstream="1.${resource}.eth1"
radio="wiphy2"
first_sta="sta1000"
ssid="jedway-wpa2-x64-3-1"
key="jedway-wpa2-x64-3-1"
poll_sec=1

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
#
function portmod() {
   local action="$1"
   shift
   ./lf_portmod.pl -m $station_host -r $resource $action "$@"
}

function firemod() {
   local action="$1"
   shift
   ./lf_firemod.pl -m $station_host -r $resource --action $action "$@"
}

function create_sta() {
   ./lf_associate_ap.pl -m $station_host --resource $resource --radio $radio \
      --action add --security wpa2 --ssid "$ssid" --passphrase "$key" --wifi_mode anAC \
      --first_sta "$1" --first_ip DHCP "$@"

}
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

# flush the system by loading a blank database, then check for ports
portmod --load BLANK
sleep 1
count=1
while [[ $count -gt 0 ]]; do
   names=(`portmod --list_port_names | grep -P 'sta\d+'`)
   count=${#names[@]}
   echo "Count $count"
   [[ $count -gt 0 ]] && ./countdown.bash 3
done
prefix=90000
last_sta=$((prefix + $num_stations))
last_sta="sta${last_sta#9}"
#for n in `seq $prefix $last_sta`; do
#   portmod --port_name sta${n#9}
#done
create_sta "$first_sta" --num_stations $num_stations

while [[ $count -lt $num_stations ]]; do
   names=(`portmod --list_port_names | grep -P 'sta\d+'`)
   count=${#names[@]}
   echo "Count $count"
   [[ $count -lt $num_stations ]] && ./countdown.bash 3
done

###
###
###