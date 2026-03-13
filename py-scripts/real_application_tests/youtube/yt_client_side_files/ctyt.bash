#!/bin/bash
# flake8: noqa
# Launch selenium YouTube viewer on a particular VRF.
# Usage: ./yt.bash <iface> <url> <host> <device_name> <duration> <res>




# Kill any Chrome process
if [[ "$(uname)" == "Linux" ]]; then
    # Linux: Terminate Chrome processes
    pkill -f chrome 
    pkill -f chromedriver
    sleep 5

    # Assign command line arguments to variables
    IFACE=$1
    URL=$2
    HOST=$3
    DEVICE_NAME=$4
    DURATION=$5
    RES=$6

    # Kill any Chrome process
    if [[ "$(uname)" == "Linux" ]]; then
        # Linux: Terminate Chrome processes
        pkill -f chrome
        pkill -f chromedriver
    elif [[ "$(uname)" == "Darwin" ]]; then
        # macOS: Terminate Chrome processes
        pkill -f "Google Chrome" || echo "No Google Chrome processes found."
        pkill -f chromedriver || echo "No ChromeDriver processes found."
    else
        # Unsupported OS
        echo "Unsupported operating system."
        exit 1
    fi

    if [ -z "${DISPLAY}" ]; then
        DISPLAY=:1
    fi

    YTENV="--env SERVERS_CSV=$SERVERS_CSV --env LOCAL_DEV=$LOCAL_DEV --env LD_PRELOAD=$LD_PRELOAD"

    # Display is set to the VNC display.
    DISPLAY=$DISPLAY ./vrf_exec.bash $IFACE "python3 youtube.py --url $URL --host $HOST --device_name $DEVICE_NAME --duration $DURATION --res $RES $YTENV" > youtube_test.log 2>&1

    # Linux: Terminate Chrome processes
    pkill -f chrome
    pkill -f chromedriver

elif [[ "$(uname)" == "Darwin" ]]; then
    # macOS: Terminate Chrome processes
    pkill -f "Google Chrome" 
    pkill -f chromedriver
    sleep 5

    # Initialize variables
    echo "Batch started"
    url=""
    host=""
    port=""
    device_name=""
    duration=""
    res=""
    args=""
    
    # Parse command line arguments
    parseArgs() {
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --url)
                    url="$2"
                    shift 2
                    ;;
                --host)
                    host="$2"
                    shift 2
                    ;;
                --port)
                    port="$2"
                    shift 2
                    ;;
                --device_name)
                    device_name="$2"
                    shift 2
                    ;;
                --duration)
                    duration="$2"
                    shift 2
                    ;;
                --res)
                    res="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
    }

    parseArgs "$@"

    echo "Batch started1"

    # Construct arguments for Python script
    args=""
    [[ -n "$url" ]] && args="$args --url $url"
    [[ -n "$host" ]] && args="$args --host $host"
    [[ -n "$port" ]] && args="$args --port $port"
    [[ -n "$device_name" ]] && args="$args --device_name $device_name"
    [[ -n "$duration" ]] && args="$args --duration $duration"
    [[ -n "$res" ]] && args="$args --res $res"

    echo "Running with arguments: $args"
    #python3 youtube.py $args
    export DISPLAY=:0 && python3 youtube.py $args > youtube_test.log 2>&1

    # macOS: Terminate Chrome processes
    pkill -f "Google Chrome"
    pkill -f chromedriver
else
    # Unsupported OS
    echo "Unsupported operating system."
    exit 1
fi