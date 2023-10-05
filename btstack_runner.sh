#! /usr/bin/bash
# example usage: btstack 02 f8:e3:22:b2:2c

echo "arg1: selected USB adapter path: $1"
echo "arg2: target device's BT MAC addr: $2"

if [ ! -d "/home/lanforge/btstack/" ]; then
    mkdir -p /home/lanforge/btstack
fi

CHILD_PID=''
#setup PIDF removal on-exit
PIDFNAME=/home/lanforge/btstack/btstack-$2.pid
on_exit() {
    kill -s SIGINT $CHILD_PID
    rm $PIDFNAME
    exit 0
}
trap on_exit SIGINT SIGTERM

#write out our PID
echo $$ > $PIDFNAME

for (( ; ; ))
do
    # start btstack
    echo "starting btstack w/ cmd: btstack -u $1 -d $2"
    (btstack -u $1 -d $2) &
    CHILD_PID=$!
    wait $!

    echo "btstack exited - sleeping 3s before restarting"
    sleep 3
done