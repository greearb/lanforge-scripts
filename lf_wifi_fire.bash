#!/bin/bash

#  This script is an attempt to simplify the creation of stations and connections for said stations.
#  One UDP connection will be created for each station.
#  The number of stations, station SSID, encryption type, number of packets to send, and transmit rates
#  can all be configured with the below options.
#  Required values are SSID, radio, and endpoint A port.
#  -m   Manager IP or hostname.
#  -r   Resource IP or hostname.
#  -n   Number of stations to create.
#  -p   Number of packets to send.
#  -e   Encryption type: open|wep|wpa|wpa2.
#  -P   Passphrase for when AP is encrypted.
#  -w   Which radio to use i.e wiphy0 wiphy1 etc.
#  -s   SSID for stations.
#  -A   Transmit rate for non station side (Endpoint A) of connection.
#  -B   Transmit rate for station side (Endpoint B) of connection.
#  -h   Help information.

#  Example usage:
#  ./lf_wifi_fire.bash -m lf0350-1234 -r 1 -w wiphy0 -n 40 -s test-SSID -e wpa2 -P hello123 -a eth1 -A 56000 -B 2000000 -p 10000

#  Station will always be endpoint B so only the name for endpoint A port is needed.

set -e
#set -u
set -o pipefail

#default values
mgr=localhost
resource=1
num_stas=40
num_packets=Infinite
encryption=open
passphrase=''
rate_A=1000000
rate_B=1000000


#other variables
first_sta=100
flag_radio=false
flag_ssid=false
flag_port=false

show_help="This script is an attempt to simplify the creation of stations and connections for said stations.
One UDP connection will be created for each station.
The number of stations, station SSID, encryption type, number of packets to send, and transmit rates
can all be configured with the below options.
Required values are SSID, radio, and endpoint A port.
-m   Manager IP or hostname.
-r   Resource IP or hostname.
-n   Number of stations to create.
-p   Number of packets to send.
-e   Encryption type: open|wep|wpa|wpa2.
-P   Passphrase for when AP is encrypted.
-w   Which radio to use i.e wiphy0 wiphy1 etc.
-s   SSID for stations.
-A   Transmit rate for non station side (Endpoint A) of connection.
-B   Transmit rate for station side (Endpoint B) of connection.
-h   Help information.

Example usage:
./lf_wifi_fire.bash -m lf0350-1234 -r 1 -w wiphy0 -n 40 -s test-SSID -e wpa2 -P hello123 -a eth1 -A 56000 -B 2000000 -p 10000

Station will always be endpoint B so only the name for endpoint A port is needed."

while getopts 'm:r:n:p:a:e:P:w:s:A:B:h' OPTION; do
   case "$OPTION" in
      m)
        #manager
        manager="$OPTARG"
        ;;
      r)
        #resource
        resource="$OPTARG"
        ;;
      n)
        #num stations
        num_stas="$OPTARG"
        ;;
      p)
        #packets
        num_packets="$OPTARG"
        ;;
      a)
        #endpoint A port
        flag_port=true
        port_A="$OPTARG"
        ;;
      e)
        #encryption
        encryption="$OPTARG"
        ;;
      P)
        #encryption passphrase
        passphrase="$OPTARG"
        ;;
      w)
        #radio
        flag_radio=true
        radio="$OPTARG"
        ;;
      s)
        #ssid
        flag_ssid=true
        ssid="$OPTARG"
        ;;
      A)
        #transmit rate for endpoint A
        rate_A="$OPTARG"
        ;;
      B)
        #transmit rate for endpoint B
        rate_B="$OPTARG"
        ;;
      h)
        #send help message
        echo "$show_help"
        exit 1
        ;;
esac
done
shift "$(($OPTIND -1))"

#check for required getopts
if [ "$flag_ssid" = false ] || [ "$flag_radio" = false ] || [ "$flag_port" = false ] ;
then
   echo "Please provide at minimum the port the station will connect to (-a), ssid (-s), and radio (-w)"
   exit 1
fi

. $HOME/lanforge.profile


./lf_associate_ap.pl --mgr $mgr --resource $resource --action del_all_phy --port_del $radio

./lf_firemod.pl --mgr $mgr --resource $resource --quiet yes --action do_cmd \
 --cmd "nc_show_ports 1 $resource all 1" &>/dev/null

sleep 2

./lf_associate_ap.pl --mgr $mgr --resource $resource \
 --ssid $ssid --security $encryption --passphrase $passphrase \
 --num_stations $num_stas --first_sta "sta$first_sta" \
 --first_ip DHCP --radio $radio --action add

function new_cx(){
   local cx=$1
   local portA=$2
   local portB=$3

   ./lf_firemod.pl --mgr $mgr --resource $resource \
    --action create_endp --endp_name "$cx-A" --port_name $portA \
    --speed $rate_A --endp_type lf_udp --report_timer 1000

   ./lf_firemod.pl --mgr $mgr --resource $resource \
    --action create_endp --endp_name "$cx-B" --port_name $portB \
    --speed $rate_B --endp_type lf_udp --report_timer 1000

   ./lf_firemod.pl --mgr $mgr --action create_cx --cx_name $cx --cx_endps "$cx-A,$cx-B" --report_timer 1000

   ./lf_firemod.pl --mgr $mgr --resource $resource --quiet yes --action do_cmd \
    --cmd "set_endp_details $cx-A NA NA NA $num_packets" &>/dev/null

   ./lf_firemod.pl --mgr $mgr --resource $resource --quiet yes --action do_cmd \
    --cmd "set_endp_details $cx-B NA NA NA $num_packets" &>/dev/null
}

# Delete all connections and endpoints that have 'bg' in the name
cx_array=( `./lf_firemod.pl --mgr $mgr --resource $resource --action list_cx | awk '/bg/ { print $ 2 }' | sed 's/,$//'`  )
for i in "${cx_array[@]}"
   do
      :
       ./lf_firemod.pl --mgr $mgr --resource $resource --action delete_cx --cx_name $i
       ./lf_firemod.pl --mgr $mgr --resource $resource --action delete_endp --endp_name "$i-A"
       ./lf_firemod.pl --mgr $mgr --resource $resource --action delete_endp --endp_name "$i-B"
   done

./lf_firemod.pl --mgr $mgr --resource $resource --quiet yes --action do_cmd --cmd 'nc_show_endpoints all' &>/dev/null

sleep 5

last_sta=$((first_sta + num_stas - 1))
for i in `seq $first_sta $last_sta`; do
   new_cx bg$i $port_A sta$i
done

/lf_firemod.pl --mgr $mgr --resource $resource --quiet yes --action do_cmd --cmd 'nc_show_endpoints all' &>/dev/null
