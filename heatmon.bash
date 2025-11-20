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
if ($line // "" ) != "" then
   ( $line | split(",") | map(gsub(" "; "")) ) as $f
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
device="/dev/ttyACM0"

getAmbientTempReading() {
    if ! exec 3< "$device"; then
        echo "Unable to open fd 3"
        exit -1
    fi
    if ! read -r line <&3; then
        echo "Unable to read line from serial port on Trinkey SHT41"
        exit -1
    fi
    # When the device first boots, it outputs three lines of header and ID info
    # Detect the first header line then report the first reading from the fouth line.
    # Lines have \r\n suffix, read once for first line then twice for last two lines.
    HEADER_LINE="# Adafruit SHT4x Trinkey Factory Test"
    if [[ "$line" =~ "$HEADER_LINE" ]]; then
        read -r _ <&3
        read -r _ <&3
        read -r _ <&3
        read -r _ <&3
        read -r _ <&3
        read -r line <&3
    fi
    exec 3<&-
}

# Check if the Adafruit device exists
if [[ ! -e $device && ! -c $device ]]; then
    echo "Unable to find Trinkey SHT41 device"
    /usr/bin/sensors -u -j 2>/dev/null \
      | jq -c "$JQ_FORMULA"
else
    getAmbientTempReading
    /usr/bin/sensors -u -j 2>/dev/null \
      | jq --arg line "$line" -c "$JQ_FORMULA"
fi
#
