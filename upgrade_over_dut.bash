#!/bin/bash

# This script is used to upgrade LANforge over the eth1 (non-managment)
# interface connected to some DUT.  This may be helpful in cases where
# the management interface is off the network for security or other reasons.

LFVER=4.3.8
KVER=4.16.18+

# Echo the commands to stdout for debugging purposes.
set -x

# Stop lanforge
/home/lanforge/serverctl.bash stop

# Remove other LANforge routing rules
./clean_route_rules.pl

# Remove default route from mgt port
ip route del 0.0.0.0/0 dev eth0

# Remove all the wireless interfaces
rmmod ath10k_pci
rmmod ath9k

# Assume eth1 is connected to a network that can route to internet
ifconfig eth1 down
pkill -f "dhclient eth1"

ifconfig eth1 up
dhclient eth1
curl -o lf_kinstall.pl http://www.candelatech.com/lf_kinstall.txt || exit 1
chmod a+x lf_kinstall.pl

./lf_kinstall.pl --do_all_ct --lfver $LFVER --kver $KVER  || exit 2

echo "Reboot now to complete upgrade."
