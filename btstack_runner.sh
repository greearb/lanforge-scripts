#! /usr/bin/bash
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
## btstack_runner.sh                                                       ##
##                                                                         ##
## Use this script to start a Bluetooth Keyboard connection,               ##
##     via btstack operating on a USB dongle.                              ##
##                                                                         ##
##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####

usage="$0 -u 01-02 -d f8:e3:22:b2:2c:ab -e /home/lanforge/vr_conf/mgt_pipe_1_helper
 OR
$0 -c e0:d3:62:56:09:b3 -d f8:e3:22:b2:2c:ab -e /home/lanforge/vr_conf/mgt_pipe_1_helper
 -u: usb path of bluetooth dongle
 -c: MAC address of bluetooth dongle
 -d: bluetooth mac of target device
 -e: file for writing out important btstack events
"

OPTIONAL_ARGS=''
CMD=''

while getopts ":d:e:u:c:" opts; do
    case "$opts" in
        d) TARGET_DEVICE="$OPTARG";;
        e) EVENTS_FNAME="$OPTARG";;
        u) USB_PATH="$OPTARG";;
        c) MAC_ADDR="$OPTARG";;
        *) echo "Unknown Option [$opts]"
    esac
done

[ -z "$TARGET_DEVICE" ] && {
    echo -e "-d: TARGET DEVICE required\n"
    echo "$usage"
    exit 1
}

if [[ -z "$MAC_ADDR"  && -z "$USB_PATH" ]]; then
   echo -e "Must provide either a USB bus path or a dongle MAC address\n"
   echo "$usage"
   exit 1
fi

if [[ -n "$MAC_ADDR" && -n "$USB_PATH" ]]; then
   echo -e "Cannot specify -u with -c\n"
   echo "$usage"
   exit 1
fi

if [ -n "$EVENTS_FNAME" ]; then
    OPTIONAL_ARGS+="-e $EVENTS_FNAME"
fi

if [[ -n "$MAC_ADDR" ]]; then
   CMD="btstack -c $MAC_ADDR -d $TARGET_DEVICE $OPTIONAL_ARGS"
fi

if [[ -n "$USB_PATH" ]]; then
   CMD="btstack -u $USB_PATH -d $TARGET_DEVICE $OPTIONAL_ARGS"
fi


if [ ! -d "/home/lanforge/btstack/" ]; then
    mkdir -p /home/lanforge/btstack
fi

CHILD_PID=''
#setup PIDF removal on-exit
PIDFNAME="./btstack/btstack-$TARGET_DEVICE.pid"
do_exit() {
    rm $PIDFNAME
    exit $1
}
on_interrupt() {
    echo "btstack_runner got SIGINT!\n"
    kill -s SIGINT $CHILD_PID
    do_exit 0
}
trap on_interrupt SIGINT SIGTERM

#write out our PID
echo $$ > $PIDFNAME

for (( ; ; ))
do
    # start btstack
    echo "starting btstack w/ cmd: $CMD"
    ($CMD) &
    CHILD_PID=$!
    wait $CHILD_PID
    RET_CODE=$?

    # ignore retval of 1 which indicates that connection was failing or the device disconnected.
    # retval of 2 means the program was unable to start with the given configuration
    if [[ $RET_CODE -eq 2 ]]; then
        do_exit $RET_CODE
    fi

    echo "btstack exited - sleeping 3s before restarting"
    sleep 3
done
