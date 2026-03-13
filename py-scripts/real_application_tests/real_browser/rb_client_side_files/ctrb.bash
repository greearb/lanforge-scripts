#!/bin/bash
# flake8: noqa
# Launch selenium YouTube viewer on a particular VRF.
# Usage: ./ctrb.bash <iface> <url> <host> <device_name> <duration> <res>

# Assign command line arguments to variables

# Kill any Chrome process
if [[ "$(uname)" == "Linux" ]]; then
    # Linux: Terminate Chrome processes
    pkill -f chrome
    pkill -f chromedriver
    sleep 5

    IFACE=$1
    URL=$2
    HOST=$3
    DURATION=$4

    if [ -z "${DISPLAY}" ]; then
        DISPLAY=:1
    fi

    YTENV="--env SERVERS_CSV=$SERVERS_CSV --env LOCAL_DEV=$LOCAL_DEV --env LD_PRELOAD=$LD_PRELOAD"

    # Display is set to the VNC display.
    DISPLAY=$DISPLAY ./vrf_exec.bash $IFACE "python3 real_browser.py --url $URL --server $HOST  --duration $DURATION  $YTENV" > real_browser_test.log 2>&1

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
    server=""
    duration=""
    args=""

    parseArgs() {
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --url)
                    url="$2"
                    shift 2
                    ;;
                --server)
                    server="$2"
                    shift 2
                    ;;
                --duration)
                    duration="$2"
                    shift 2
                    ;;
                --help)
                    echo "Usage: $0 --url <url> --server <server> --duration <duration>"
                    exit 0
                    ;;
                *)
                    echo "Unknown argument: $1"
                    exit 1
                    ;;
            esac
        done
    }

    parseArgs "$@"

    # Validate required arguments
    if [[ -z "$url" ]]; then
        echo "Error: --url is required."
        exit 1
    fi

    if [[ -z "$duration" ]]; then
        echo "Error: --duration is required."
        exit 1
    fi

    # Debugging output
    echo "URL: $url"
    echo "Server: $server"
    echo "Duration: $duration"

    # Construct arguments for Python script
    args=""
    [[ -n "$url" ]] && args="$args --url $url"
    [[ -n "$server" ]] && args="$args --server $server"
    [[ -n "$duration" ]] && args="$args --duration $duration"

    echo "Running with arguments: $args"

    # Export DISPLAY if necessary
    if [[ -z "$DISPLAY" ]]; then
        export DISPLAY=:0
    fi

    # Run the Python script
    python3 real_browser.py $args > real_browser_test.log 2>&1

    # Mac: Terminate Chrome processes
    pkill -f "Google Chrome"
    pkill -f chromedriver

else
    # Unsupported OS
    echo "Unsupported operating system."
    exit 1
fi