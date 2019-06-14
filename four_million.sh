#!/bin/bash
export PATH=".:$PATH"
FM="./lf_firemod.pl"
max=1000
connections=()
for c in `seq 1 $max`; do
  n=$(( (10 * $max) + $c ))
  connections[$c]="con${n:1:${#max}}"
done

index=0
portnum=0
for c in "${connections[@]}"; do
  echo $FM --mgr localhost --resource 1 --action create_endp --endp_name ${c}-A --speed 25000 --endp_type lf_tcp --port_name "eth1#$portnum"

  echo $FM --mgr localhost --resource 1 --action create_endp --endp_name ${c}-B --speed 25000 --endp_type lf_tcp --port_name "eth2"
  
  echo $FM --mgr localhost --resource 1 --action create_cx --cx_name ${c}  --endps ${c}-A,${c}-B

  # set report timer

  index=$((index + 1))
  portnum=$((index % 100))
done
echo "done"


#
