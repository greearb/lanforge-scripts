#!/bin/bash
set -eu
# Create multiple L3 cross-connects, monitor them for a while and exit
KBPS=1000
MBPS=1000000
GBPS=1000000000
# DBG="--debug"
DBG=''
# test prefix must be a single word, no punctuation or spaces
TEST_PREFIX="spiderman"
TEST_DURATION_SEC=20
GUI="localhost"
if [[ ! -z "${1:-}" ]]; then
    GUI="$1"
fi
NUM_CX=${NUM_CX:-3}
UPSTREAM_PORT=${UPSTREAM:-"1.1.eth1"}
RADIOS=(
    1.1.wiphy0
    1.1.wiphy1
    1.2.wiphy0
    1.2.wiphy1
)
STATIONS=(
    1.1.sta0000
    1.1.sta0001
    1.2.sta0000
    1.2.sta0001
)
SSID="jedway-r7800-5G"
PASSWD="jedway-r7800-5G"
SEC="wpa2"
UPLOAD_BPS=(
    $((  2 * $MBPS))
    $((  1 * $MBPS))
    $((750 * $KBPS))
    $((750 * $KBPS))
)
DOWNLOAD_BPS=(
    $((  1 * $MBPS))
    $((  2 * $MBPS))
    $((250 * $KBPS))
    $((250 * $KBPS))
)
cd ./py-scripts
LAST_STA_IDX=$(( ${#STATIONS[@]}- 1))
EXISTING_STATIONS=( $(./modify_station.py --mgr "$GUI" --list_stations) )
echo "Existing Stations: ${EXISTING_STATIONS[@]}"
# check for connection group name
EXISTING_GROUPS=( $(./testgroup.py --mgr "$GUI" --list_groups) )
ADD_GROUP=0
if echo "${EXISTING_GROUPS[@]}" | grep -q 'No test groups found'; then
    ADD_GROUP=1
elif ! echo "${EXISTING_GROUPS[@]}" | grep -q "$TEST_PREFIX"; then
    ADD_GROUP=1
fi
if (( ADD_GROUP > 0 )); then
    ./testgroup.py --mgr "$GUI" --add_group --group_name "$TEST_PREFIX"
    ./raw_cli.py --mgr "$GUI" --cmd show_group --param "group $TEST_PREFIX"
fi
shelf=1
for i in $(seq 0 $LAST_STA_IDX); do
    resource="${STATIONS[$i]}"
    resource="${resource#1.}"
    resource="${resource%.*}"
    short_sta="${STATIONS[$i]}"
    short_sta="${short_sta##*.}" # need to turn 1.1.sta0000 to sta0000, not the same below
    if echo "${EXISTING_STATIONS[@]}" | grep -q "${STATIONS[$i]}" ; then
        echo "      Station ${STATIONS[$i]} exists"
    else
        echo "      Creating ${STATIONS[$i]} ..."
        ./create_station.py --mgr "$GUI" $DBG \
            --radio         "${RADIOS[$i]}" \
            --security      "$SEC" \
            --ssid          "$SSID" \
            --passwd        "$PASSWD" \
            --mode          anAC \
            --radio_channel 153 \
            --country_code  840 \
            --no_pre_cleanup \
            --no_cleanup \
         || echo "problem creating station ${STATIONS[$i]}] "
         ./raw_cli.py --mgr "$GUI" --cmd nc_show_ports \
            --arg "shelf 1" \
            --arg "resource $resource" \
            --arg "port $short_sta"
    fi
    ./create_l3.py --mgr "$GUI" $DBG \
        --cx_type       "${TYPE:-lf_udp}" \
        --cx_prefix     "${TEST_PREFIX}_$i-" \
        --endp_a        "${STATIONS[$i]}" \
        --endp_b        "${UPSTREAM_PORT}" \
        --min_rate_a    "${UPLOAD_BPS[$i]}" \
        --min_rate_b    "${DOWNLOAD_BPS[$i]}" \
        --no_pre_cleanup --no_cleanup
    ./raw_cli.py --mgr "$GUI" --cmd nc_show_endpoints --arg "endpoint all"
done
CX_NAMES=()
for i in $(seq 0 $LAST_STA_IDX); do
    short_sta="${STATIONS[$i]}"
    short_sta="${short_sta##*.}-0" # need to turn 1.1.sta0000 to sta0000-0
    CX_NAMES+=("${TEST_PREFIX}_${i}-${short_sta}")
    ./testgroup.py --mgr "$GUI" $DBG \
        --group_name    "$TEST_PREFIX" \
        --add_cx        "${TEST_PREFIX}_${i}-${short_sta}" \
        --use_existing
done
./raw_cli.py --mgr "$GUI" --cmd show_group --arg "group $TEST_PREFIX"
sleep 1

./testgroup.py --mgr "$GUI" $DBG \
    --group_name    $TEST_PREFIX \
    --start_group   $TEST_PREFIX \
    --use_existing
# connections don't all start at once, so if we don't pause and refresh
# then there's a good chance that monitor_cx.py is going to not see any
# running endpoints
sleep 1
./raw_cli.py --mgr "$GUI" --cmd nc_show_endpoints --arg "endpoint all"

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
# Monitor Connections
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
comma_str="${CX_NAMES[@]}"
comma_str="${comma_str// /,}"
# Be careful, this filename gets overwritten!
./monitor_cx.py --mgr "$GUI" \
    --csv_file      "$HOME/report-data/${TEST_PREFIX}.csv" \
    --cx_names      "$comma_str" \
    --quit          all_cx_stopped \
    --log_level     DEBUG \
    &
monitor_pid=$!

countdown=$TEST_DURATION_SEC
while (( $countdown >= 0)); do
    echo -n "."
    sleep 1
    if kill -0 "$monitor_pid"; then
        countdown=$(( countdown - 1))
    else # \process has exited
        remaining_sec=$(( $TEST_DURATION_SEC - $countdown))
        if (( $remaining_sec > 0 )); then
            echo "monitor_py exited $remaining_sec seconds early."
        fi
        countdown=0
    fi
done


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   Stop connections
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
echo ""
echo "Quiescing connections..."
./testgroup.py --mgr "$GUI" \
    --group_name    $TEST_PREFIX \
    --quiesce_group $TEST_PREFIX \
    --use_existing

sleep 3 # assumes 3sec quiesce time

# wait for monitor_cx.py in background
wait
echo "Done with test. CSV results at ~/report-data/${TEST_PREFIX}.csv"