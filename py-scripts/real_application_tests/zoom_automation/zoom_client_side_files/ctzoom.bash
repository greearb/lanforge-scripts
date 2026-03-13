#!/bin/bash
# flake8: noqa
# Launch selenium zoom viewer on a particular VRF.
# Usage: ./ctzoom.bash <IP> <TYPE>

if [[ "$(uname)" == "Linux" ]]; then
    # Linux: Terminate Chrome processes
    pkill -f chrome 
    pkill -f chromedriver

    sleep 5

    # Assign command line arguments to variables
    IFACE=$1
    IP=$2
    TYPE=$3

    if [ -z "${DISPLAY}" ]; then
        DISPLAY=:1
    fi

    # Display is set to the VNC display.

    YTENV="--env SERVERS_CSV=$SERVERS_CSV --env LOCAL_DEV=$LOCAL_DEV --env LD_PRELOAD=$LD_PRELOAD"
    if [ "$TYPE" == "host" ]; then
        DISPLAY=$DISPLAY ./vrf_exec.bash $IFACE "python3 zoom_host.py --ip $IP $YTENV" > zoom_host.log 2>&1
    
    elif [ "$TYPE" == "client" ]; then

        DISPLAY=$DISPLAY ./vrf_exec.bash $IFACE "python3 zoom_client.py --ip $IP $YTENV" > zoom_client.log 2>&1
    else
        echo "Invalid TYPE specified. Please use 'host' or 'client'."
        exit 1
    fi

    # Linux: Terminate Chrome processes
    pkill -f chrome 
    pkill -f chromedriver

elif [[ "$(uname)" == "Darwin" ]]; then
    # macOS: Terminate Chrome processes
    pkill -f "Google Chrome" 
    pkill -f chromedriver

    sleep 5

    # Assign command line arguments to variables

    IP=$1
    TYPE=$2

    if [ "$TYPE" == "host" ]; then
        python3 zoom_host.py --ip $IP > zoom_host.log 2>&1
    elif [ "$TYPE" == "client" ]; then
        python3 zoom_client.py --ip $IP > zoom_client.log 2>&1
    else
        echo "Invalid TYPE specified. Please use 'host' or 'client'."
        exit 1
    fi

    # Mac: Terminate Chrome processes
    pkill -f "Google Chrome"
    pkill -f chromedriver
else
    # Unsupported OS
    echo "Unsupported operating system."
    exit 1
fi