#!/bin/bash
set -veux
# Create multiple L3 cross-connects, monitor them for a while and exit
KBPS=1000
MBPS=1000000
GBPS=1000000000
DBG="--debug"
TEST_PREFIX="Glorfindel"
[[ -z "${GUI:-}" ]] && GUI="${1:-localhost}"
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
)
DOWNLOAD_BPS=(
    $((  1 * $MBPS))
    $((  2 * $MBPS))
    $((250 * $KBPS))
)
cd ./py-scripts
LAST_STA_IDX=$(( ${#STATIONS[@]}- 1))
EXISTING_STATIONS=( $(./modify_station.py --mgr "$GUI" --list_stations) )
# check for connection group name
EXISTING_GROUPS=( $(./testgroup.py --mgr "$GUI" --list_groups) )
if echo "${EXISTING_GROUPS[@]}" | grep -q 'No test groups found'; then
    ./testgroup.py --mgr "$GUI" --add_group --group_name "$TEST_PREFIX"
fi

for i in $(seq 0 $LAST_STA_IDX); do
    if echo "${EXISTING_STATIONS[@]}" | grep -q "${STATIONS[$i]}" ; then
        echo "station ${STATIONS[$i]} exists"
    else
        ./create_station.py --mgr "$GUI" \
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
    fi
    ./create_l3.py --mgr "$GUI" \
        --cx_type       "${TYPE:-lf_udp}" \
        --cx_prefix     "${TEST_PREFIX}-" \
        --endp_a        "${STATIONS[$i]}" \
        --endp_b        "${UPSTREAM_PORT}" \
        --min_rate_a    "${UPLOAD_BPS[$i]}" \
        --min_rate_b    "${DOWNLOAD_BPS[$i]}" \
        --no_pre_cleanup --no_cleanup ||:

    ./testgroup.py --mgr ${GUI} \
        --group_name    ${TEST_PREFIX} \
        --add_cx        "${TEST_PREFIX}-${STATIONS[$i]}" ||:
done
./testgroup.py --mgr "$GUI" \
    --use_existing \
    --group_name $TEST_PREFIX \
    --start_group $TEST_PREFIX
sleep 10
./testgroup.py --mgr "$GUI" \
    --use_existing \
    --quiesce_group $TEST_PREFIX
