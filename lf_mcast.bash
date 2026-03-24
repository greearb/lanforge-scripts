#!/bin/bash
#
# NAME:     lf_mcast.bash
#
# PURPOSE:  Example script to demonstrate creation and activation of multicast traffic endpoints using lf_firemod.pl
#
# NOTES:    Much of this script is hard-coded which could could become command-line switches or re-implemented using
#           another scripting language.

# General configuration
LF_SCRIPTS=/home/lanforge/scripts
lf_mgr=localhost
report_timer=1000
quiet=yes

# Transmitter configuration
xmit_count=2
xmit_resource=1
xmit_port=eth3
xmit_rate=10000000   # 10 Mbps
xmit_tos=BE          # Can give either tag name abbreviation or number here (e.g. VO, VI, BE, BK). See lf_firemod.pl for more info

# Receiver configuration
rcv_count=3
rcv_resource=1
rcv_port_prefix=wlan

# TODO: The lf_firemod.pl script needs adjustments possibly to delete individual endpoints
delete_endpoints() {
  echo "> Removing any conflicting named endpoints"

  # Delete any existing and receivers transmitters w/ same name
  for ((i=1; i<${xmit_count}+1; i+=1))
  do
    xmit_endp_name=mcast_xmit_${i}

    $LF_SCRIPTS/lf_firemod.pl \
      --mgr        ${lf_mgr} \
      --action     delete_cxe \
      --endp_name  ${xmit_endp_name}

    for ((j=1; j<${rcv_count}+1; j+=1))
    do
      rcv_endp_name=mcast_rcv_grp${i}_${j}

      $LF_SCRIPTS/lf_firemod.pl \
        --mgr        ${lf_mgr} \
        --action     delete_cxe \
        --endp_name  ${rcv_endp_name}
    done
  done
}

create_endpoints() {
  echo "> Creating ${xmit_count} multicast group transmitter(s) with ${rcv_count} receiver endpoint(s) per transmitter"

  # Create transmitters
  for ((i=1; i<${xmit_count}+1; i+=1))
  do
    xmit_port_num=$((10000 + i))            # Transmit and receive port numbers must be same
    xmit_endp_name=mcast_xmit_grp${i}

    # Create transmitter endpoint
    $LF_SCRIPTS/lf_firemod.pl \
      --mgr          ${lf_mgr} \
      --action       create_endp \
      --resource     ${xmit_resource} \
      --port_name    ${xmit_port} \
      --endp_name    ${xmit_endp_name} \
      --endp_type    mc_udp \
      --rcv_mcast    NO \
      --mcast_addr   224.9.9.${i} \
      --mcast_port   ${xmit_port_num} \
      --speed        ${xmit_rate} \
      --tos          ${xmit_tos} \
      --quiet        ${quiet} \
      --report_timer ${report_timer}
  done

  # Create receivers endpoints, grouped as ${rcv_count} many per transmitter
  for ((i=1; i<${xmit_count}+1; i+=1))
  do
    for ((j=1; j<${rcv_count}+1; j+=1))
    do
      rcv_port_num=$((10000 + i))          # Transmit and receive port numbers must be same
      rcv_port=${rcv_port_prefix}${j}      # Port here means network interface
      rcv_endp_name=mcast_rcv_grp${i}_${j}

      $LF_SCRIPTS/lf_firemod.pl \
        --mgr          ${lf_mgr} \
        --action       create_endp \
        --resource     ${rcv_resource} \
        --port_name    ${rcv_port} \
        --endp_name    ${rcv_endp_name} \
        --endp_type    mc_udp \
        --rcv_mcast    YES \
        --mcast_addr   224.9.9.${i} \
        --mcast_port   ${rcv_port_num} \
        --speed        0 \
        --quiet        ${quiet} \
        --report_timer ${report_timer}
    done
  done
}

start_endpoints() {
  # Start all endpoints in this group (transmitter and receivers)
  for ((i=1; i<$xmit_count+1; i+=1))
  do
    xmit_endp_name=mcast_xmit_grp${i}

    # Start transmitter
    echo "> Starting multicast group ${i} transmitter endpoint '${xmit_endp_name}'"
    $LF_SCRIPTS/lf_firemod.pl \
      --mgr       $lf_mgr \
      --action    start_endp \
      --endp_name $xmit_endp_name

    # Start receivers
    echo "> Starting multicast group ${i} receiver endpoint(s) (${rcv_count} total) "
    for ((j=1; j<$rcv_count+1; j+=1))
    do
       rcv_endp_name=mcast_rcv_grp${i}_${j}

       $LF_SCRIPTS/lf_firemod.pl \
           --mgr       $lf_mgr \
           --action    start_endp \
           --endp_name $rcv_endp_name
    done
  done
}

#delete_endpoints
create_endpoints
start_endpoints

# Script could then randomly start and stop the receivers to cause multicast join and leave messages.
