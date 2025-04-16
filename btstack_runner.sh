#! /usr/bin/bash
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
## btstack_runner.sh                                                       ##
##                                                                         ##
## Use this script to start a Bluetooth Keyboard connection,               ##
##     via btstack operating on a USB dongle.                              ##
##                                                                         ##
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

usage="$0 -u 01-02 -d f8:e3:22:b2:2c -e /home/lanforge/vr_conf/mgt_pipe_1_helper
 -u: usb path of bluetooth dongle
 -d: bluetooth mac of target device
 -e: file for writing out important btstack events
"

OPTIONAL_ARGS=''

while getopts ":d:e:u:" opts; do
    case "$opts" in
        d) TARGET_DEVICE="$OPTARG";;
        e) EVENTS_FNAME="$OPTARG";;
        u) USB_PATH="$OPTARG";;
        *) echo "Unknown Option [$opts]"
    esac
done

[ -z "$TARGET_DEVICE" ] && {
    echo -e "-d: TARGET DEVICE required\n"
    echo "$usage"
    exit 1
}

[ -z "$USB_PATH" ] && {
    echo -e "-u USB PATH of controlling BT dongle required\n"
    echo "$usage"
    exit 1
}

if [ -n "$EVENTS_FNAME" ]; then
    OPTIONAL_ARGS+="-e $EVENTS_FNAME"
fi

if [ ! -d "/home/lanforge/btstack/" ]; then
    mkdir -p /home/lanforge/btstack
fi

CHILD_PID=''
#setup PIDF removal on-exit
PIDFNAME="./btstack/btstack-$TARGET_DEVICE.pid"
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
    CMD="btstack -u $USB_PATH -d $TARGET_DEVICE $OPTIONAL_ARGS"
    echo "starting btstack w/ cmd: $CMD"
    ($CMD) &
    CHILD_PID=$!
    wait $!

    echo "btstack exited - sleeping 3s before restarting"
    sleep 3
done