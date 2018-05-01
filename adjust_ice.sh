#!/bin/bash
#
# adjust_ice.sh
#
# This script takes a csv data file with downlink, uplink and rtt values
# and uses the values to adjust an existing running wanlink.
#
# Each value is checked against the committed information rate (CIR) limits
# and when the limit is exceeded a shuffled value is chosen between a default
# min and max.
#
# Inputs are:
# csv filename
# name of wanlink
# run time between value changes

cd /home/lanforge/scripts

file=$1
name=$2
run_time=$3


print_help() {
   echo "Usage: $0 {csv filename} {wanlink name} {run time}"
   echo "   Use this on lanforge localhost"
   echo "   Run time units are seconds"
   echo " $0 values.csv wanlink-01 60"
   echo ""
}

if [ $# -eq 0 ]; then
   print_help
   exit 1
fi

cir_dn=3500000
cir_up=2000000
min=20000
max=200000
downlink=()
uplink=()
delay=()

function get_values() {
   while read -r line
   do
       if [[ $line != "" ]]; then
         if [[ $line == *DATE* ]]; then
           continue;
         fi
         if [[ $line != *-* ]]; then
           continue;
         fi

         dl=(`echo $line |cut -d '"' -f2 |sed 's/,//g'`)
         if [[ $dl < $cir_dn ]]; then
           let dl=$(expr $cir_dn - $dl)
           downlink+=( "$dl" )
         else
           let bas=$(shuf -i "$min-$max" -n1)
           downlink+=( "$bas" )
         fi

         ul=(`echo $line |cut -d '"' -f6 |sed 's/,//g'`)
         if [[ $ul < $cir_up ]]; then
           let ul=$(expr $cir_up - $ul)
           uplink+=( "$ul" )
         else
           let bas=$(shuf -i "$min-$max" -n1)
           uplink+=( "$bas" )
         fi

         lat=(`echo $line |cut -d '"' -f9 |sed 's/,//g' |cut -d '.' -f1`)
         let lat=$(expr $lat/2)
         delay+=( "$lat" )

       fi
   done < $file
}

function modify_values {
   for ((j=0;j<10;++j)); do 
      let dl_now=(`echo ${RANDOM:0:8}`)+${downlink[i]}
      let ul_now=(`echo ${RANDOM:0:8}`)+${uplink[i]}
      let lt_now=(`echo ${RANDOM:0:2}`)+${delay[i]}

      #echo "set wanlink $name: $dl_now $ul_now $lt_now"
      echo "set wanlink $name-A: Downlink $dl_now, Delay $lt_now"
      ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
         "set_wanlink_info $name-A $dl_now $lt_now NA NA NA NA" &>/dev/null
      echo "set wanlink $name-B: Uplink $ul_now, Delay $lt_now"
      ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
         "set_wanlink_info $name-B $ul_now $lt_now NA NA NA NA" &>/dev/null

      echo "Running for $run_time seconds."
      sleep $run_time
   done
}


get_values
for ((i=0;i<${#downlink[@]};++i)); do
   
   #echo "set wanlink $name: ${downlink[i]} ${uplink[i]} ${delay[i]}"
   echo "set wanlink $name-A: Downlink ${downlink[i]}, Delay ${delay[i]}"
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-A ${downlink[i]} ${delay[i]} NA NA NA NA" &>/dev/null
   echo "set wanlink $name-B: Uplink ${uplink[i]}, Delay ${delay[i]}"
   ./lf_firemod.pl --mgr localhost --quiet on --action do_cmd --cmd \
      "set_wanlink_info $name-B ${uplink[i]} ${delay[i]} NA NA NA NA" &>/dev/null

   echo "Running for $run_time seconds."
   sleep $run_time

   modify_values
done

