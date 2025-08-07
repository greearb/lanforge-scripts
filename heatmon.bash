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
]
EOF
)
if [[ -n "${1:-}" ]] && [[ -r "$1" ]]; then
    grep -v ERROR < "$1" | jq -c "$JQ_FORMULA"
fi
/usr/bin/sensors -u -j 2>/dev/null \
  | jq -c "$JQ_FORMULA"

#