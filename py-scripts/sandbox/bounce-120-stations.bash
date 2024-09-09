#!/bin/bash
# set -veux
# * Create 120 clients in down state (on 11n radio)
# * Bring the clients upWait until they get an IP
# * Bring the clients down.
# * Delete the clients
# * Bring down the radio interface for 120 seconds,
# * then bring it up.
#
export LF_SCRIPTS=/home/lanforge/scripts/py-scripts
CreateSta="$LF_SCRIPTS/create_station.py"
ModifySta="$LF_SCRIPTS/modify_station.py"
RawCli="$LF_SCRIPTS/raw_cli.py"
JAPI="http://localhost:8080"
PortsJson="$HOME/tmp/ports.json"
Radio10=1.1.wiphy0
Radio11=1.1.wiphy1
Radio20=1.2.wiphy0
Radio21=1.2.wiphy1
SSID="205a1-ch36"
USE_R1=1
USE_R2=1
BackgroundLimit=16

function ListPorts() {
   curl  -sq \
      -H 'Accept: application/json' \
      -o $PortsJson \
      "${JAPI}/ports/list?fields=port,alias,ip,phantom,down"
}

function CreateStations() {
   $CreateSta \
      --mgr           localhost \
      --radio         $1 \
      --num_stations  $2 \
      --start_id      $3 \
      --ssid          $SSID \
      --passwd        $SSID \
      --security      wpa2 \
      --radio_channel 36 \
      --radio_antenna 0 \
      --no_pre_cleanup \
      --create_admin_down
}

echo ""
echo ""
echo "Creating stations..."
echo ""
echo ""
if (( USE_R1 == 1 )); then
   CreateStations $Radio10 128 1000 &
   CreateStations $Radio11 128 1500 &
fi
if (( USE_R2 == 1 )); then
   CreateStations $Radio20 64 2000 &
   CreateStations $Radio21 64 2500 &
fi
wait
echo ""
echo ""
echo "Bringing all ports up..."
echo ""
echo ""
StaList=($( $ModifySta --mgr localhost --list_stations ))
if (( $? != 0 )); then
   echo "Failed to list stations."
   exit 1
fi
counter=0
for sta_eid in "${StaList[@]}"; do
   sta="${sta_eid:4}"
   echo -n " $sta_eid -> $sta"
 
   if [[ $sta > sta2499 ]]; then
      $ModifySta --mgr localhost --radio $Radio21 --station $sta --set_state up &
   elif [[ $sta > sta1999 ]]; then
      $ModifySta --mgr localhost --radio $Radio20 --station $sta --set_state up &
   elif [[ $sta > sta1499 ]]; then
      $ModifySta --mgr localhost --radio $Radio11 --station $sta --set_state up &
   elif [[ $sta > sta0999 ]]; then
      $ModifySta --mgr localhost --radio $Radio10 --station $sta --set_state up &
   else
      echo "What radio does $sta live on?"
   fi
   counter=$(( counter + 1 ))
   if (( (counter % BackgroundLimit) == 0 )); then
      wait
   fi
done
wait
echo ""
echo ""
echo "waiting for a bit"
sleep 30
echo ""
echo ""
# query all the ports until we have all the IPs

#while true; do
#   ListPorts
#   jq '.interfaces|.[]|.[]|select(.ip != "0.0.0.0") | length'
#   sleep 10
#done
#
echo "Setting stations down..."
counter=0
for sta_eid in "${StaList[@]}"; do
  sta="${sta_eid:4}"
  echo -n " $sta_eid -> $sta"
  if [[ $sta > sta2499 ]]; then
      $ModifySta --mgr localhost --radio $Radio21 --station $sta --set_state down &
   elif [[ $sta > sta1999 ]]; then
      $ModifySta --mgr localhost --radio $Radio20 --station $sta --set_state down &
   elif [[ $sta > sta1499 ]]; then
      $ModifySta --mgr localhost --radio $Radio11 --station $sta --set_state down &
   elif [[ $sta > sta0999 ]]; then
      $ModifySta --mgr localhost --radio $Radio10 --station $sta --set_state down &
   else
      echo "What radio does $sta live on?"
   fi
   counter=$(( counter + 1 ))
   if (( (counter % BackgroundLimit) == 0 )); then
      wait
   fi
done
wait
echo ""
echo ""
echo "Deleting Stations..."
echo ""
echo ""
counter=0
set -veux
for sta_eid in "${StaList[@]}"; do
   sta="${sta_eid:4}"
   resource="${sta_eid:2:1}"
   echo -n " $sta_eid -> $sta"
   $RawCli --mgr localhost --cmd rm_vlan \
      --arg "shelf 1" \
      --arg "resource $resource" \
      --arg "port $sta" &

   counter=$(( counter + 1 ))
   if (( (counter % BackgroundLimit) == 0 )); then
      wait
   fi
done
wait
echo "...deleted stations"

