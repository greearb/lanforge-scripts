#!/bin/bash
#

PING=/usr/bin/ping
SUBNET100=192.168.100
SUBNET1=192.168

for JUMP in 116 200 181 152 192 194 27 29 00
do
    IP100="${SUBNET100}.${JUMP}"
    echo -n " ${IP100} - "
    RESULT100=$( ${PING} -4 -q -w2 -c1 ${IP100} &> /dev/null )
    RESULT100=$?
    # echo -n " ${RESULT100}"
    echo " ${RESULT100}"

    #IP1="${SUBNET1}.${JUMP}.1"
    #echo -n " ${IP1} - "
    #RESULT1=$( ${PING} -4 -q -W2 -c1 ${IP1} &> /dev/null )
    #RESULT1=$?
    #echo " ${RESULT1}"
done
