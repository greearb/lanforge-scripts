#!/bin/bash
# set -veux

# for ip in "${list[@]}"; do echo $ip ; sshpass -p sitindia123 ssh -o StrictHostKeyChecking=no sitindia@$ip "lsb_release -a"; done | awk '/Release:/{print $2}'
helpFunction() {
    echo "Automated Script for LANforge Server Installation on Ubuntu Systems"
    echo "Usage: $0 -c [manager_ip] -d [interface] -i [realm] -m [mode] -r [resource] -u [y|yes] -l [y|yes]"
}
while getopts "c:d:i:m:r:u:l:" opt; do
    case "$opt" in
    c) connect_mgr="$OPTARG" ;;
    d) interface="$OPTARG" ;;
    i) realm="$OPTARG" ;;
    m) mode="$OPTARG" ;;
    r) resource="$OPTARG" ;;
    u) upgrade="$OPTARG" ;;
    l) local="$OPTARG" ;;
    ?) helpFunction ;; # Print helpFunction in case parameter is non-existent
    esac
done

if [[ x${connect_mgr:-} == x ]]; then
    echo "No manager? please use -c [192.168.1.101]"
    exit 1
fi
if [[ x${interface:-} == x ]]; then
    echo "No interface? please use -d [enp1s0]"
    exit 1
fi
if [[ x${realm:-} == x ]]; then
    echo "No realm? please use -r [2...256]"
    exit 1
fi
if [[ x${resource:-} == x ]]; then
    echo "No resource? please use -r [2...256]"
    exit 1
fi
if [[ x${mode:-} == x ]]; then
    echo "No mode? please use -m [both|resource]"
    exit 1
fi
do_upgrade=0
if [[ x${upgrade:-} =~ [Yy]* ]]; then
    do_upgrade=1
fi
local_install=0
if [[ $local == [Yy]* ]]; then
    local_install=1
fi

echo $local_install

if [[ $local_install == 0 ]]; then
  apt update
  ## libnet-dev should be bundled
  ## curl should also be bundled, we don't really want it
  apt install -y bridge-utils libnet-dev
  apt dist-upgrade -y
  apt -f install
  apt autoremove -y
fi

#Add lanforge user
lf_id=`id -u lanforge` || lf_id=1
if (($lf_id < 2)) ; then
    echo "Adding user lanforge"
    useradd -k /etc/skel -m -d /home/lanforge -G adm,dialout,lpadmin,tty,plugdev,root,sudo,video lanforge
    mkdir /home/lanforge
    echo 'lanforge:lanforge' | chpasswd
fi
mkdir /home/lanforge
#
x=`lsb_release -r | awk '{print $2}'`
echo "VERSION: [$x]"
server_pkg="LANforgeServer-5.4.6_Linux-F27-x64.tar.gz"
download_these=(
    libcrypto.so.1.1
    libcrypt.so.2
    libnet.so.1
    libpcap.so.1
    libssh2.so.1
    libssl.so.1.1
    libstdc++.so.6
    libtinfo.so.6
)
case "$x" in
    16.04)
        server_pkg="LANforgeServer-5.4.6_Linux-F21-x64.tar.gz"
        ;;
    18.04)
        server_pkg="LANforgeServer-5.4.6_Linux-F27-x64.tar.gz"
        ;;
    20.04)
        server_pkg="LANforgeServer-5.4.6_Linux-F30-x64.tar.gz"
        ;;
    *)
        echo "Ubuntu version [$x] is not Configured in this script, Only supports 16, 18 and 20 as of now"
        exit 1
        ;;
esac
if ((do_upgrade == 1)); then
    [[ ! -f $server_pkg ]] && rm -f /home/lanforge/$server_pkg ||:
fi
if [[ $local_install == 1 ]]; then
  cp libs/* /home/lanforge/
  cp $server_pkg /home/lanforge/
fi
cd /home/lanforge/
if [[ $local_install == 0 ]]; then
  if [[ ! -f $server_pkg ]]; then
      echo "Downloading new $server_pkg"
      wget https://www.candelatech.com/private/downloads/r5.4.6/$server_pkg
  fi

  for f in "${download_these[@]}"; do
      if [[ ! -f "/home/lanforge/$f" ]]; then
          wget -O "/home/lanforge/$f" https://www.candelatech.com/downloads/f21/$f
      fi
  done
fi

systemctl stop NetworkManager ||:
systemctl disable NetworkManager ||:
systemctl mask NetworkManager ||:
[[ -f /home/lanforge/lfconfig_answers.txt ]] && rm -f /home/lanforge/lfconfig_answers.txt ||:
if [[ $interface == "default" ]]; then
  export port=`ip route show to default | grep -Eo "dev\s*[[:alnum:]]+" | sed 's/dev\s//g'`
else
  port=$interface
fi
cat > /home/lanforge/lfconfig_answers.txt <<EOF
realm $realm
resource $resource
mgt_dev $port
mode $mode
connect_mgr $connect_mgr
config

EOF

tar -xf $server_pkg
cd LANforgeServer-5.4.6/
export LD_LIBRARY_PATH="/home/lanforge:/home/lanforge/LANforgeServer-5.4.6/lib:/home/lanforge/local/lib:/usr/local/lib:/usr/lib:/usr/lib/x86_64-linux-gnu"
LF_AUTO_INSTALL=1 ./install.bash /home/lanforge

# copy_to_home=(libcrypt.so.2)
# missing=0
# for f in "${copy_to_home[@]}"; do
#     if [[ -f $f ]]; then
#         echo "File [$f] missing"
#         missing=$((missing + 1))
#     fi
#     mv -v "$f" /home/lanforge/
# done
# if (( $missing > 0)); then
#     echo "some files could not be copied, bye"
#     exit 1
# fi

cd /home/lanforge/
# echo "====== ====== ====== ====== ====== ====== ====== ====== ====== ====== ====== "
./lfconfig < /home/lanforge/lfconfig_answers.txt
# echo "====== ====== ====== ====== ====== ====== ====== ====== ====== ====== ====== "


./serverctl.bash start

#
