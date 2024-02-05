#!/bin/bash
set -veu
TEN="10.42."
QU=6
NUM_MVL=125
PF="/home/lanforge/scripts/py-scripts"
CR="$PF/create_macvlan.py"
PARENTS_1=(  6  7  8  9 10 11 12 13)
PARENTS_2=( 06 07 08 09 10 11 12 13)
TX_PORTS=()
RX_PORTS=()

do_create_mv=0
do_create_cx=0

while getopts cm opt; do
    case $opt in
        c) do_create_cx=1;;
        m) do_create_mv=1;;
        *) echo "huh? [$opt]"; exit 1;;
    esac
done

if (( ($do_create_cx + $do_create_mv) == 0)); then
    echo -e "$0: \n  -m create mvlans\n  -c create cx\n"
    exit
fi

for parent in "${PARENTS_1[@]}"; do
    for mvl in $(seq 0 $NUM_MVL); do
        TX_PORTS+=("1.2.eth${parent}#${mvl}")
    done
    if (( $do_create_mv == 1 )); then
        portname="1.2.eth${parent}#0"
        echo "r2] Creating series starting with [$portname] ..."
        # set -x
        $CR --macvlan_parent "1.2.eth$parent" \
            --first_port        "$portname" \
            --num_ports         $NUM_MVL \
            --first_mvlan_ip    "10.42.${parent}.126" \
            --netmask           255.255.255.0 \
            --gateway           0.0.0.0
        sleep 5
        # set +x
    fi
done
# echo "N E X T, RX PORTS"
#sleep 5
for parent in "${PARENTS_1[@]}"; do
    for mvl in $(seq 0 $NUM_MVL); do
        RX_PORTS+=("1.1.eth${parent}#${mvl}")
    done
    
    if (( $do_create_mv == 1 )); then
        portname="1.1.eth${parent}#0"
        echo "r1] Creating series starting with [$portname] ..."
        # set -x
        $CR --macvlan_parent "1.1.eth$parent" \
            --first_port        "$portname" \
            --num_ports         $NUM_MVL \
            --first_mvlan_ip    "10.42.${parent}.1" \
            --netmask           255.255.255.0 \
            --gateway           0.0.0.0
        sleep 5
        # set +x
    fi
done
# sleep 5

num_cx=$(( ${#TX_PORTS[@]} - 1 ))
echo "Will create $NUM_MVL per parent"
#sleep 2
if (( $do_create_cx == 1 )); then
    port_index=0
    for parent in "${PARENTS_1[@]}"; do
        for txport in "${TX_PORTS[@]}"; do
            # rxport="${RX_PORTS[$port_index]}"
            rxport=${txport/1.2./1.1.}
            ep_num="${PARENTS_2[$port_index]}"
            # tx_pref="${txport/\#*/}"
            # rx_pref="${rxport/\#*/}"
            # echo " <$ep_num> parent[$parent] match txport[$txport] rxport[$rxport]?     [$tx_pref][$rx_pref]"
            # echo "  YES epnum[$ep_num] rxport[$rxport] txport[$txport]"
            # echo -n "+"

            # batch_qty does not appear to work "$NUM_MVL"
            set -x
            $PF/create_l3.py --mgr localhost \
                --min_rate_a        9600 \
                --min_rate_b        0 \
                --cx_prefix         "y-e${ep_num}-" \
                --cx_type           lf_tcp \
                --multi_con_a       10 \
                --multi_con_b       1 \
                --batch_quantity    1 \
                --endp_a            "$txport" \
                --endp_b            "$rxport" \
                --min_ip_port_a     0 \
                --min_ip_port_b     -1 \
                --ip_port_increment_a 1 \
                --ip_port_increment_b 1 \
                --endp_a_increment  1 \
                --endp_b_increment  1 \
                --no_cleanup \
                --no_pre_cleanup \
                --debug --log_level debug
            set +x
        done
        port_index=$(( $port_index + 1 ))
    done
fi