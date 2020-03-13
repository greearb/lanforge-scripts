#!/bin/bash
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Create ten stations and ten udp L3 cxes. Create a tcp CX that has a
# better ToS and check the latency on that tcp connection.
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

station_host="ct524-genia.jbr"
num_stations=1
resource=1
upstream="1.${resource}.eth1"
radio="wiphy2"
first_sta=1000
ssid="jedway-wpa2-x64-3-1"
key="jedway-wpa2-x64-3-1"
poll_sec=1

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
#
function portmod() {
   local action="$1"
   if [[ x$action != x--* ]]; then
      action="--${action}"
   fi
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
      --first_sta "sta$1" --first_ip DHCP "$@"

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
   mapfile -t port_name_lines done < <(portmod --list_port_names | grep -P 'sta\d+')
   count=${#port_name_lines[@]}
   echo "$count stations created"
   #echo "${names[@]}"
   [[ $count -lt $num_stations ]] && ./countdown.bash 3
done
# convert those lines into names
names=()
for line in "${port_name_lines[@]}"; do
   hunks=($line)
   names+=(${hunks[1]})
done

# create UDP CX and then a TCP CX
if [[ x$upstream = x ]]; then
   echo "no upstream port, bye."
fi
firemod do_cmd --cmd "add_group udpcx"
for name in "${names[@]}"; do
   portname="1.${resource}.${name}"
   firemod create_cx --cx_name "udpten-${name}" \
      --use_ports $portname,$upstream --use_speeds 0,3500000 \
      --endp_type udp
done
sleep 0.1
for name in "${names[@]}"; do
   firemod do_cmd --cmd "add_tgcx udpcx udpten-${name}"
done
firemod do_cmd --cmd "add_group tcpcx"
for name in "${names[@]}"; do
   portname="1.${resource}.${name}"
   firemod create_cx --cx_name "tcpten-${name}" \
      --use_ports $portname,$upstream --use_speeds 35000,35000 \
      --endp_type tcp  --tos VO
done
sleep 0.1
for name in "${names[@]}"; do
   firemod do_cmd --cmd "add_tgcx tcpcx tcpten-${name}"
done

# poll for the port to come up
stations=0
while [[ $stations -lt $num_stations ]]; do
   for name in "${names[@]}"; do
      ap=`portmod --port_name $name --show_port AP`
      if [[ x$ap != x ]] && [[ $ap != NA ]]; then
         stations=$(( stations + 1))
      fi
   done
   if [[ $stations -lt $num_stations ]]; then
      sleep 1
   fi
done

# start the test groups
firemod do_cmd --cmd "start_group udpcx"
firemod do_cmd --cmd "start_group tcpcx"

# poll them for 20 seconds
for sec in `seq 1 20`; do
   firemod show_endp --endp_name tcpten-sta0000 --endp_vals tx_bps,rx_bps
   sleep 1
done

# stop the test groups
firemod do_cmd --cmd "stop_group udpcx"
firemod do_cmd --cmd "stop_group tcpcx"


###
###
###