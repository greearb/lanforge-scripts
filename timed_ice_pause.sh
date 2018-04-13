#!/bin/bash

# scripts
cd /home/lanforge/scripts
trap do_sigint INT

function do_sigint() {
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $link_name-A NA NA NA NA NA 0" &>/dev/null
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $link_name-B NA NA NA NA NA 0" &>/dev/null

   exit 0 
}

function stop_cx() {
   [ -z "$1" ] && echo "No connection name, bye." && exit 1
   local name=$1
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd \
      --cmd "set_cx_state all $name QUIESCE" &>/dev/null
}

function start_cx() {
   [ -z "$1" ] && echo "No connection name, bye." && exit 1
   local name=$1
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd \
      --cmd "set_cx_state all $name RUNNING" &>/dev/null
}

function pause_wl() {
   [ -z "$1" ] && echo "No connection name, bye." && exit 1
   [ -z "$2" ] && echo "No sleep seconds, bye." && exit 1
   local name=$1
   local pause_time=$2

   # read the max-drop-rate
   local formerDrA=-1
   local formerDrB=-1
   local info
   mapfile -t info < <(./lf_firemod.pl --mgr localhost --quiet on --action do_cmd \
      --cmd "show_endpoints $name-A")
   for L in "${info[@]}"; do
      #echo "L: $L"
      if [[ $L == *DropFreq:* ]]; then
         formerDrA=`echo $L | grep -oP 'DropFreq: (\S+)'`
         formerDrA=${formerDrA/DropFreq: /}
         #echo "formerDrA: $formerDrA"
      fi
   done
   if [ $formerDrA -lt 0 ]; then
      echo "DropFreq not found for $name-A"
      exit 1
   fi

   mapfile -t info < <(./lf_firemod.pl --mgr localhost --quiet on --action do_cmd \
      --cmd "show_endpoints $name-B")
   for L in "${info[@]}"; do
      #echo "L: $L"
      if [[ $L == *DropFreq:* ]]; then
         formerDrB=`echo $L | grep -oP 'DropFreq: (\S+)'`
         formerDrB=${formerDrB/DropFreq: /}
         #echo "formerDrB: $formerDrB"
      fi
   done
   if [ $formerDrB -lt 0 ]; then
      echo "DropFreq not found for $name-B"
      exit 1
   fi

   if [ -z "$formerDrA" -o $formerDrA -lt 0 ] ; then 
      echo "Unable to read wanlink-A speed, or wanlink already paused."
      exit 1
   fi
   if [ -z "$formerDrB" -o $formerDrB -lt 0 ] ; then 
      echo "Unable to read wanlink-B speed, or wanlink already paused."
      exit 1
   fi


   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-A NA NA NA NA NA 1000000" &>/dev/null

   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-B NA NA NA NA NA 1000000" &>/dev/null

   echo -n "Pausing $pause_time"
   sleep $pause_time

   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-A NA NA NA NA NA $formerDrA" &>/dev/null
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-B NA NA NA NA NA $formerDrB" &>/dev/null

   echo -n " go "
}

show_help=0
run_time_sec=0
pause_time_sec=0
link_name=''

while getopts "h:n:r:p:" arg; do
   #echo "ARG[$arg] OPTARG[$OPTARG]"
   case $arg in 
   n) link_name=$OPTARG
      ;;
   r) run_time_sec=$OPTARG
      ;;
   p) pause_time_sec=$OPTARG
      ;;
   h) show_help=1
      ;;
   *)
      echo "Ignoring option $arg $OPTARG"
   esac
done

if [ -z "$link_name" -o $run_time_sec -eq 0 -o $pause_time_sec -eq 0 ]; then
   show_help=1
fi

if [ $show_help -gt 0 ]; then
   echo "Usage: $0 -n {CX name} -r {run time in seconds} -p {pause time in seconds}"
   exit 1
fi


echo "Starting connection $link_name..."
start_cx $link_name
while true; do
   sleep $run_time_sec
   #echo "pausing..."
   pause_wl $link_name $pause_time_sec
   #echo "resumed"
done
#
