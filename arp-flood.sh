#!/bin/bash
echo "----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- "
echo "      This script will issue local arp flushes. "
echo "      Those commands cannot be issued against a remote lanforge."
echo "----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- "
sleep 2
mgr=localhost
port=4001
station=wlan0
upstream=eth1
num_mvlans=20
cxlist=()
ports=($station)
trap do_sigint ABRT
trap do_sigint INT
trap do_sigint KILL
trap do_sigint PIPE
trap do_sigint QUIT
trap do_sigint SEGV
trap do_sigint TERM

function do_sigint() {
    echo ""
    for cx in "${cxlist[@]}"; do
        echo -n "stopping $cx "
        fire_cmd set_cx_state default_tm $cx STOPPED >/dev/null
    done
    for cx in "${cxlist[@]}"; do
        echo -n "removing $cx "
        fire_cmd rm_cx default_tm $cx STOPPED >/dev/null
    done
    for cx in "${cxlist[@]}"; do
        echo -n "removing $cx-A $cx-B "
        fire_cmd rm_endp ${cx}-A STOPPED >/dev/null
        fire_cmd rm_endp ${cx}-B STOPPED >/dev/null
    done
    exit 0
}

function fire_cmd() {
    ./lf_firemod.pl --mgr $mgr --mgr_port $port --quiet yes --action do_cmd \
    --cmd "$*" \
     &>/dev/null
}
function fire_newcx() {
    local cxname=$1; shift
    local sta=$1; shift
    local eth=$1; shift
    ./lf_firemod.pl --mgr $mgr --mgr_port $port --action create_cx --quiet yes \
        --cx_name $cxname --use_ports $sta,$eth --use_speeds 2600,2600 --endp_type udp \
         &>/dev/null
}

# create new set of vlans, this will also recreate them using random mac addresses
for i in `seq 0 $num_mvlans`; do
    mvlan="${upstream}#${i}"
    echo -n " $mvlan"
    fire_cmd rm_vlan 1 1 $mvlan
    echo -n "-"
    fire_cmd add_mvlan 1 1 $upstream 'xx:xx:xx:*:*:xx' $i
    echo -n "+"
    fire_cmd set_port 1 1 "$mvlan" NA NA NA NA 2147483648 NA NA NA NA 67125250
    echo -n "."
    fire_newcx "udp-$i" $station $mvlan
    echo -n "o"
    cxlist+=("udp-$i")
    ports+=($mvlan)
done
sleep 4
for i in `seq 0 $num_mvlans`; do
    echo -n "!"
    fire_cmd set_cx_state default_tm "udp-$i" RUNNING
done

sleep 4
echo ""
echo -n "Starting arp flushing "
while : ; do
    for p in "${ports[@]}"; do
        ip neigh flush dev $p@$upstream

    done
    echo -n "."
    sleep 0.2
done
