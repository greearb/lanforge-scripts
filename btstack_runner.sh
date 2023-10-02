#! /usr/bin/bash
# example usage: btstack 02 'f8:e3:22:b2:2c'

echo "arg1: selected USB adapter path: $1"
echo "arg2: target device's BT MAC addr: $2"

if [ ! -d "btstack/" ]; then
    mkdir -p btstack
fi

for (( ; ; ))
do
    # start btstack
    echo "starting btstack w/ cmd: btstack -u $1 -d $2"
    btstack -u $1 -d $2
    #@TODO: process return value

    echo "btstack exited - sleeping 3s before restarting"
    sleep 3
done