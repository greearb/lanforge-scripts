#!/bin/bash

# This bash script will modify the layer 3 endp traffic 
#    1. Small bursts of data of about 1K (can be configurable) at a 30 second long ransom interval
#    2. Emulate a brief upstream video (e.g. when someone is at the door)

# main idea is to provide easy way for user to automate changing a l3 cx behavior via bash / python

set -x

# Define some common variables.  This will need to be changed to match your own testbed.
# MGR is LANforge GUI machine
MGR=192.168.0.103
#MGR=localhost

PORT=4001
# sample command
# CMD='set_endp_tx_bounds LT-sta0000-0-BE-A 200000 300000'
CMD='set_endp_tx_bounds LT-sta0000-0-BE-A 0 0'



# you can start/stop/reconfigure requested tx/rx bandwidth for layer-3 connections with a few milisecond precision.  
# So creating a single connection and then modifying it via a longer lived script should give you a lot of control.
# like:  create tcp cx, set rate to 'idle', where it sends 1k chunks of data (pdu-size 1024) at 10kbps 
# (so a frame every few seconds), sleep 1 minute, set tx rate to 2Mbps to emulate traffic for 30 seconds, set back to idle...etc.
# we used to have perl scripts that could create and modify an existing layer-3 connection, 
# hopefully there is some python that can do the same, 
# then someone can easily write a bash script to do the above behaviour by just calling our existing helper scripts.


(echo open ${MGR} ${PORT}
# sleep 1
# echo "help"
sleep .1
echo ${CMD}
# sleep 1
echo "quit"
) | telnet
