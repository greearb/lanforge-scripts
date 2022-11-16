#!/bin/bash
# set -x
force=0
if [[ x$1 == x-f ]]; then
    force=1
    echo "Will remove .pyc files..."
    sleep 1
else
    echo "These are your .pyc files. Use $0 -f to erase them."
fi
diir=`pwd`
if [[ `pwd` != /home/lanforge/scripts ]]; then
    echo "# ==== pycache files under $diir ==== #"
fi
if (( $force == 0 )); then
    find "$diir" -type f -iname '*.pyc' | less
else
    find "$diir" -type f -iname '*.pyc' | sudo xargs rm -f
fi
#
