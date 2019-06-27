#!/bin/bash
set -x
set -e
[ -f /root/strongswan-config ] && . /root/strongswan-config
ETC=${ETC:=/etc/strongswan
SWAND="$ETC/strongswan.d"
IPSECD="$ETC/ipsec.d"
SWANC="$ETC/swanctl"
NOWSEC=`date +%s`
SWAN_LIBX=${SWAN_LIBX:=/usr/libexec/strongswan}
[ -d $SWAN_LIBX ] || {
  echo "SWAN_LIBX $SWAN_LIBX not found. Plese set SWAN_LIBX in /root/strongswan-config"
  exit 1
}
export LD_LIBRARY_PATH="$SWAN_LIBX:$LD_LIBRARY_PATH"
WAN_IF=${WAN_IF:=eth1}
WAN_IP=${WAN_IP:=10.1.99.1}
WAN_CONCENTRATOR_IP=${WAN_CONCENTRATOR_IP:=10.1.99.1}
XIF_IP=${XIF_IP:=10.9.99.1}

function initialize() {
  [ -d "$SWANC/peers-available" ] || mkdir "$SWANC/peers-available"
  [ -d "$SWANC/peers-enabled" ] || mkdir "$SWANC/peers-enabled"
  [ -f "$SWANC/secrets.conf" ] || touch "$SWANC/secrets.conf"

  systemctl enable strongswan
  systemctl daemon-reload
  systemct  start strongswan || {
    journalctl -xe
  }
}



function backup_keys() {
  if  [ -f $SWANC/secrets.conf ]; then
    cp $SWANC/secrets.conf $SWANC/.secrets.conf.$NOWSEC
  fi
}

function deactivate_peer() {
  [ -e "$SWANC/peers-enabled/${1}.conf" ] || {
    if [ -e "$SWANC/peers-available/${1}.conf" ]; then
      echo "Peer $1 deactivated."
    else
      echo "No peer config at $SWANC/peers-available/${1}.conf"
    fi
    exit 0
  }

  echo -n "Deactivating $1..."
  rm "$SWANC/peers-enabled/${1}.conf"
  swanctl --load-all
  echo "done"
}


function activate_peer() {
  [ -f "$SWANC/peers-available/${1}.conf" ] || {
    echo "No peer config at $SWANC/peers-available/${1}.conf"
    exit 1
  }

  if [ -e "$SWANC/peers-enabled/${1}.conf" ]; then
    echo "Peer $1 actiated."
  else
    echo -n "Activating $1..."
    ln -s" $SWANC/peers-available/${1}.conf" "$SWANC/peers-enabled/"
    swanctl --load-all
    echo "done"
  fi
}

function create_station_peer() {
  if [ -f "$SWANC/peers-available/${1}.conf" ]; then
    echo "Peer $1 config already exists."
    return;
  fi

  cat > "$SWANC/peers-available/${1}.conf" <<EOF
$1 {
  local_addrs = %any # use any local ip to connect to remote
  remote_addrs = $WAN_CONCENTRATOR_IP
  unique = replace
  local {
    auth = psk
    id = @${1}-master.loc # identifier, use VRF ID
  }
  remote {
    auth = psk
    id = @${1}-slave.loc # remote id, use VRF ID
  }
  children {
    ${1}_sa {
      local_ts = 0.0.0.0/0, ::/0
      remote_ts = 0.0.0.0/0, ::/0
      if_id_out = 1 # xfrm interface id, use VRF ID
      if_id_in = 1  # xfrm interface id, use VRF ID
      start_action = trap
      life_time = 1h
      rekey_time = 55m
      esp_proposals = aes256gcm128-modp3072 # good for Intel HW
      dpd_action = trap
    }
  }
  keyingtries = 0
  dpd_delay = 30
  version = 2
  mobike = yes
  rekey_time = 23h
  over_time = 1h
  proposals = aes256-sha256-modp3072
}
EOF
}

function create_station_key() {
  [ -f "$SWANC/secrets.conf" ] || {
    echo "$SWANC/secrets.conf not found!"
    exit 1
  }
  backup_keys
  k=`dd if=/dev/urandom bs=20 count=1 skip=1004 | base64`
  cat >> "$SWANC/secrets.conf" <<EOF
  ike-${1}-master {
    id = ${1}-slave.loc # use remote id specified in tunnel config
    secret = "$k"
  }
EOF
}

function get_vrf_for_if() {
  echo "1";
}

function enable_ipsec_if() {
  vrfnum=$(get_vrf_for_if $WAN_IF)
  xif="xfrm${vrfnum}"
  $SWAN_LIBX/xfrmi -n $xif  -i ${vrfnum} -d $WAN_IF

  ip link set dev $xif up
  ip link set dev $xif master vrf${vrfnum}
  ip address add $XIF_IP/32 dev $xif scope link
  ip route add default dev $xif vrf $vrfnum
  ip route add 10.0.0.0/8 dev $xif vrf $vrfnum
}

function check_arg() {
  if [ ! -f "$SWANC/secrets.conf" ] ; then
    echo "$SWANC/secrets.conf not found. Suggest running $0 -i, bye."
    exit 1
  fi
  [[ z$1 != z ]] || {
    echo "Please give me a peer name, bye."
    exit 1
  }
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     M   A   I   N
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


while getopts "ibc:a:d:" arg; do
  case $arg in
    i)
      initialize
      echo "Initialized."
      exit 0;
      ;;
    c)
      check_arg $OPTARG
      echo "Creating $OPTARG"
      create_station_peer $OPTARG
      create_station_key $OPTARG
      ;;
    a)
      check_arg $OPTARG
      echo "Activating $OPTARG"
      activate_peer $OPTARG
      ;;
    d)
      check_arg $OPTARG
      echo "Deactivating $OPTARG"
      deactivate_peer $OPTARG
      ;;
    b)
      enable_ipsec_if $WLAN_IF
      ;;
    *) echo "Unknown option: $arg"
  esac
done
