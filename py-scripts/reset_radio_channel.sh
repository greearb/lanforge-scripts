#!/bin/bash

usage() {
    echo "$0: [host] [resource] [radio]"
    echo "Example:  $0 localhost 1 wiphy3"
    echo "  [host] indicates system running a LANforgeGUI connected to the realm holding your resource"
}

if [[ x$1 == x ]] || [[ x$2 == x ]] || [[ x$3 == x ]]; then
    usage
    exit 1
fi
host="$1"
resource="$2"
radio="$3"

python3 lf_modify_radio.py --host "$host" \
    --radio "1.${resource}.${radio}" \
    --channel "-1" \
    --antenna 0

#
