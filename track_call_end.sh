#!/bin/bash
#
#------------------------------------------------------------
# Use this script to track traffic on a voip call and end it 
# if the call does not connect.
#------------------------------------------------------------

function usage() {
   echo "$0 {manager} {resource} {CX name} {poll time} [-start]"
   echo "   Use poll time 0 to run just once"
   echo "   Poll time is an argument to sleep(1)"
}

RtpPktsTx="RTP Pkts Tx"
RtpPktsRx="RTP Pkts Rx"
declare -A call_states=([ON_HOOK]=0 
   [REQUESTED_START_CALL]=1 
   [CALL_STARTUP_IN_PROGRESS]=2 
   [CALL_REMOTE_RINGING]=3
   [CALL_IN_PROGRESS]=4)
   
declare -A highest_call_state=()

# pass this the file name
function study_call() {
   [ ! -r "$1" ] && echo "Unable to find Endpoint record: $1" && exit 1
   local call_state="unknown"
   local actual_state="unknown"
   local running_for=0
   local idx=0
   local line
   if [[ $endp = *-B ]]; then
      idx=1
   fi

   while IFS= read -r line ; do
      local chunks
      local shunks=($line)
      IFS=: read -r -a chunks <<< "$line"
      #for h in "${hunks[@]}"; do 
      #   echo -n "$h,"
      #done
      #echo ""
      local lasthunk="${line:63}"
      local lr=($lasthunk)
      local fields=($(echo "${line:34:+12}") "${lr[0]}" "${lr[1]}")

      first=`echo ${chunks[0]}`;
      #echo "first[$first]"
      case $first in
         RegisterState)
            call_state=${shunks[3]}
            #echo "call_state ${call_state} = ${call_states[$call_state]}"
            ;;
         RptTimer)
            running_for=${shunks[3]}
            running_for=${running_for:0:-1} # chop 's' off 
            ;;
      esac
   done < "$1"
   # this is a work around for voip cli bugs in 5.3.7
   if [[ $call_state = ON_HOOK ]]; then
      actual_state=$call_state
   elif [[ $running_for -gt 65535 ]]; then
      actual_state="ON_HOOK"
   elif [[ $running_for -le 65535 ]]; then
      actual_state=$call_state
   fi
   if [[ ${call_states[$actual_state]} -gt ${highest_call_state[$endp]} ]]; then
      highest_call_state[$endp]=${call_states[$actual_state]}
      echo -n "$actual_state "
   fi
}

start=0
stop=0
[ -z "$1" ] && usage && exit 1
[ -z "$2" ] && usage && exit 1
[ -z "$3" ] && usage && exit 1
[ -z "$4" ] && usage && exit 1
[ "$5" == "-start" ] && start=1
[ "$6" == "-stop" ] && stop=1

cd /home/lanforge/scripts
q="--quiet yes"
m="--mgr $1"
r="--resource $2"

fire=$( echo ./lf_firemod.pl $m $q $r )
# find endpoint name
$fire --action list_endp > /tmp/list_endp.$$

# example:
# ./lf_firemod.pl --mgr idtest --quiet yes --action list_endp | grep VoipEndp \
# | while read -r line ; do hunks=($line); echo "${hunks[1]}"; done
#   [v3v2-30000-B]
#   [v3v2-30000-A]
start_sec=`date +%s`
declare -A results_tx
declare -A results_rx
declare -A results_attempted
declare -A results_completed

declare -A cx_names=()
voip_endp_names=()
while IFS= read -r line ; do
   jhunks=($line)
   [[ "${jhunks[0]}" != "VoipEndp" ]] && continue
   name=${jhunks[1]:1:-1} # that trims the brackets
   [[ $name != ${3}-* ]] && continue
   voip_endp_names+=($name)
   cx_n="${name%-[AB]}"
   [[ -z "${cx_names[$cx_n]+unset}" ]] && cx_names+=(["$cx_n"]=1)
done < /tmp/list_endp.$$

if [ $stop -eq 1 ]; then
   echo -n "Stopping ${cn_n}..."
   $fire --action do_cmd --cmd "set_cx_state all '${cx_n}' STOPPED"  &>/dev/null
   sleep 3
   echo "done"
fi

if [ $start -eq 1 ]; then
   echo -n "Starting ${cn_n}..."
   $fire --action do_cmd --cmd "set_cx_state all '${cx_n}' RUNNING"  &>/dev/null
   echo "done"
fi

##
## Wait for A side to connect
##
duration=$(( `date +"%s"` + 120 ))
endp="${cx_n}-A"
echo -n "Endpoint $endp..."
highest_call_state[$endp]=0
while [[ `date +"%s"` -le $duration ]]; do
   $fire --action show_endp --endp_name $endp > /tmp/endp_$$
   study_call /tmp/endp_$$
   rm -f /tmp/endp_$$
   
   echo -n "(${highest_call_state[$endp]}) "
   if [[ ${highest_call_state[$endp]} -ge ${call_states[CALL_IN_PROGRESS]} ]]; then
      echo "$endp connected"
      break;
   fi
   sleep 0.25
done

##
## Wait for B side to connect
##
duration=$(( `date +"%s"` + 2 ))
endp="${cx_n}-B"
highest_call_state[$endp]=0
echo -n "Endpoint $endp..."
while [[ `date +"%s"` -le $duration ]]; do
   $fire --action show_endp --endp_name $endp > /tmp/endp_$$
   study_call /tmp/endp_$$
   rm -f /tmp/endp_$$
   echo -n "(${highest_call_state[$endp]}) "
   if [[ ${highest_call_state[$endp]} -ge ${call_states[CALL_IN_PROGRESS]} ]]; then
      echo "$endp connected"
      break;
   fi

   [ $4 -eq 0 ] && exit
   sleep 0.25
done

if [[ ${highest_call_state[$endp]} -lt ${call_states[CALL_IN_PROGRESS]} ]]; then
   echo -n "call not connected, cancelling..."
   $fire --action do_cmd --cmd "set_cx_state all '${cx_n}' STOPPED" &>/dev/null
   echo "done"
fi
stop_sec=`date +%s`
delta=$(( $stop_sec - $start_sec ))
echo "Test duration: $delta seconds"
#      if [ -z "${results_tx[$endp]+unset}" ]; then
#         results_tx[$endp]="0"
#      fi
#      if [ -z "${results_rx[$endp]+unset}" ]; then
#         results_rx[$endp]="0"
#      fi
#      if [ -z "${results_attempted[$endp]+unset}" ]; then
#         results_attempted[$endp]="0"
#      fi
#      if [ -z "${results_completed[$endp]+unset}" ]; then
#         results_completed[$endp]="0"
#      fi
#function old_stuff() {
#   for cx in "${!cx_names[@]}"; do
#      enda="${cx}-A"
#      endb="${cx}-B"
#
#      if [[ ${results_attempted[$enda]} -gt 1 ]] ; then
#         if [[ ${results_completed[$endb]} < $(( ${results_attempted[$enda]} -1 )) ]]; then
#            echo -n " fewer calls recieved: "
#            echo " attempted ${results_attempted[$enda]} completed ${results_completed[$endb]}"
#         fi
#      fi
#      if [[ ${results_tx[$enda]} -gt 1 ]] ; then
#         if [[ ${results_rx[$endb]} < $(( ${results_tx[$enda]} / 2 )) ]]; then
#            echo -n " fewer packets recieved: "
#            echo " tx ${results_tx[$enda]}               rx ${results_rx[$endb]}"
#         fi
#      fi
#   done
#}
# eof
