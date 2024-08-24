#!/bin/bash

#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Wifi Capacity Tests"
./ct_us_002_wc.bash

echo "Running Dataplane Tests"
./ct_us_002_dp.bash