#!/bin/bash

# Variables
WATCH_DIR="$(pwd)"                  # Directory to watch (current directory)
HOST_FILE="zoom_host.py"           # Host file to watch for (Python script)
CLIENT_FILE="zoom_client.py"   # Client file to watch for if the host file is not found

# Function to watch for the file
watch_for_file() {
    while true; do
        if [ -f "$WATCH_DIR/$HOST_FILE" ]; then
            echo "Host file detected: $WATCH_DIR/$HOST_FILE"
            execute_and_cleanup "$HOST_FILE" "host"
        elif [ -f "$WATCH_DIR/$CLIENT_FILE" ]; then
            echo "Client file detected: $WATCH_DIR/$CLIENT_FILE"
            execute_and_cleanup "$CLIENT_FILE" "client"
        else
            echo "No target files detected in $WATCH_DIR. Retrying in 5 seconds..."
        fi
        sleep 5
    done
}

# Function to execute the script, delete it, and perform necessary cleanup
execute_and_cleanup() {
    FILE_TO_EXECUTE=$1
    EXECUTION_TYPE=$2
    
    # kill any chrome process
    if [[ "$(uname)" == "Linux" ]]; then
        # Linux: Terminate Chrome processes using pkill -f chrome
        pkill -f chrome
        pkill -f chromedriver
        pkill -f "chrome for testing"
        
    elif [[ "$(uname)" == "Darwin" ]]; then
        # macOS: Terminate Chrome processes using pkill -9 chrome
        pkill -f chrome for testing
        pkill -f chrome
        pkill -f chromedriver
    else
        # Unsupported OS
        echo "Unsupported operating system."
    fi
   
    sleep 2
    # Execute the script
    python3 "$WATCH_DIR/$FILE_TO_EXECUTE"
    EXECUTION_SUCCESS=$?

    # Always attempt to delete the script file regardless of execution success
    if [ -f "$WATCH_DIR/$FILE_TO_EXECUTE" ]; then
        rm "$WATCH_DIR/$FILE_TO_EXECUTE"
        echo "Removed the script: $WATCH_DIR/$FILE_TO_EXECUTE"
    else
        echo "Script file already removed: $WATCH_DIR/$FILE_TO_EXECUTE"
    fi

    
        MEETING_LINK_FILE="$WATCH_DIR/credentials.csv"
        if [ -f "$MEETING_LINK_FILE" ]; then
            rm "$MEETING_LINK_FILE"
            echo "Cleared the meeting link file: $MEETING_LINK_FILE"
        else
            echo "Meeting link file not located: $MEETING_LINK_FILE"
        fi
    

    # Provide feedback and continue script execution regardless of execution success
    if [ $EXECUTION_SUCCESS -ne 0 ]; then
        echo "Continuing after failed script execution."
    else
        echo "Script executed successfully."
    fi
}

# Start watching for the file
watch_for_file
