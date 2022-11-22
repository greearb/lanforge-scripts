#!/bin/bash
# set -veux

# for ip in "${list[@]}"; do echo $ip ; sshpass -p sitindia123 ssh -o StrictHostKeyChecking=no sitindia@$ip "lsb_release -a"; done | awk '/Release:/{print $2}'
helpFunction() {
    echo "Automated Script for LANforge Server Installation on Ubuntu Systems"
    echo "Usage: $0 -c [manager_ip] -d [interface] -i [realm] -m [mode] -r [resource] -u [y|yes]"
}
while getopts "c:d:i:m:r:u:" opt; do
    case "$opt" in
    c) connect_mgr="$OPTARG" ;;
    d) interface="$OPTARG" ;;
    i) realm="$OPTARG" ;;
    m) mode="$OPTARG" ;;
    r) resource="$OPTARG" ;;
    u) upgrade="$OPTARG" ;;
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
apt update
# libnet-dev should be bundled
# curl should also be bundled, we don't really want it
apt install -y bridge-utils
apt dist-upgrade -y
apt -f install
apt autoremove -y

#Add lanforge user
lf_id=`id -u lanforge` || lf_id=1
if (($lf_id < 2)) ; then
    echo "Adding user lanforge"
    useradd -k /etc/skel -m -d /home/lanforge -G adm,dialout,lpadmin,tty,plugdev,root,sudo,video lanforge
    echo 'lanforge:lanforge' | chpasswd
fi

x=`lsb_release -r | awk '{print $2}'`
echo "VERSION: [$x]"
server_pkg="LANforgeServer-5.4.6_Linux-F27-x64.tar.gz"
cd /home/lanforge
case "$x" in
    16.04)
        server_pkg="LANforgeServer-5.4.6_Linux-F27-x64.tar.gz"
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
    [[ ! -f $server_pkg ]] && rm -f $server_pkg ||:
fi
if [[ ! -f $server_pkg ]]; then
    echo "Downloading new $server_pkg"
    wget http://www.candelatech.com/private/downloads/r5.4.6/$server_pkg
fi
#    "\n"
[[ -f /home/lanforge/lfconfig_answers.txt ]] && rm -f /home/lanforge/lfconfig_answers.txt ||:

cat > /home/lanforge/lfconfig_answers.txt <<EOF
realm $realm
resource $resource
mgt_dev $interface
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

systemctl stop NetworkManager ||:
systemctl disable NetworkManager ||:
systemctl mask NetworkManager ||:

./serverctl.bash start

#