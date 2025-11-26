#!/bin/bash
#
# Use this script to report sensors output to journalctl. This script
# should be invoked from a systemd-timer. Use lf_kinstall.pl --do_heatmon to create
# the systemd timer unit. The timer should probably only run once a minute.
#
if [[ ! -x /usr/bin/jq ]]; then
    echo "Unable to find jq."
    exit 1
fi
if [[ ! -x /usr/bin/sensors ]]; then
    echo "Unable to find sensors"
    exit 1
fi
# JQ_FORMULA='[.| to_entries |.[] | {A: .key, T: .value.temp1.temp1_input}]'
JQ_FORMULA=$( cat <<- 'EOF'
[ to_entries[]
  | .key as $chip
  | .value
  | to_entries[]
  | select(.value | type == "object")
  | .key as $core
  | .value
  | to_entries[]
  | select(.key | test("temp.*input"))
  | {
      # ($chip +"."+ $core):(.value),
      A: ($chip +"."+ $core+"."+.key),
      T: .value
    }
] + (
if ($ARGS.named.trinkey_reading // "" ) != "" then
   ( $ARGS.named.trinkey_reading | split(",") | map(gsub(" "; "")) ) as $f
   | [{
       A: "TrinkeySHT41_Ambient",
       T: ($f[1] | tonumber)
      }]
else
   []
end
)
EOF
)
if [[ -n "${1:-}" ]] && [[ -r "$1" ]]; then
    grep -v ERROR < "$1" | jq -c "$JQ_FORMULA"
fi

# Get a reading from the Adafruit Trinkey SHT41 USB Controller
device="/dev/TrinkeySHT41"
trinkey_dev=''
trinkey_reading=''

getAmbientTempReading() {
    stty -F "$device" raw 115200 cs8 clocal -icanon -echo min 1 time 1
    if ! exec 3< "$device"; then
        echo "Unable to open fd 3"
        return 1
    fi
    if ! read -r trinkey_reading <&3; then
        echo "Unable to read line from serial port on Trinkey SHT41"
        return 1
    fi
    # echo "DEBUG: Current line: $trinkey_reading"
    # When the device first boots, it outputs three lines of header and ID info
    HEADER_PATTERN=".*Adafruit\s.*"
    if [[ $trinkey_reading =~ $HEADER_PATTERN ]]; then
        if mapfile -t -n 6 -u 3 readings; then
            trinkey_reading=${readings[5]}
            # echo "DEBUG: trinkey_reading after mapfile is: $trinkey_reading"
        else
           echo "ERROR: Failed to read header lines from Trinkey SHT41 device"
           exec 3<&-
           return 1
        fi
    fi
    # echo "DEBUG: closing serial port FD"
    exec 3<&-
    return 0
}

# Device path exists and is a character device file
if [[ -e $device && -c $device ]]; then
   trinkey_dev=$device
else
   echo "ERROR: Trinkey SHT41 device path doesn't exist or isn't a serial device"
fi
# Non-empty string if SHT sensor controller found
if [[ -n "$trinkey_dev" ]]; then
   getAmbientTempReading
   trinkey_read_status=$?
else
   echo "ERROR: Trinkey SHT41 device path is an empty string"
fi
if [[ -n "$trinkey_reading" && trinkey_read_status -eq 0 ]]; then
   /usr/bin/sensors -u -j 2>/dev/null | jq --arg trinkey_reading "$trinkey_reading" -c "$JQ_FORMULA"
else
   /usr/bin/sensors -u -j 2>/dev/null | jq -c "$JQ_FORMULA"
fi
#
