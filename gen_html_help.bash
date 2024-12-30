#!/bin/bash

# this script does not know where btbits/html lives in relation to your
# lanforge-scripts checkout directory. The location below is correct in 
# the case where this script is executed from btbits/x64_btbits/server/lf-scripts
# (eg, a server build).
# DESTF=${1:-./scripts_ug.php}  use for testing and local scripts_ug.ph generation in lanforge-scripts
DESTF=${1:-../../html/scripts_ug.php}
if [[ -z ${1:-} ]]; then
    echo "Using $DESTF as the default target."
fi
if [[ ! -f $DESTF ]]; then
    echo "* * $DESTF not found? Suggest setting env varialble DESTF first."
    echo "exit with [ctrl-c]"
    sleep 3
    echo "...proceeding"
fi
#DESTF=/var/www/html/greearb/lf/scripts_ug.php

scripts=(
    py-scripts/attenuator_serial.py
    py-scripts/bandsteering.py
    py-scripts/bssid_to_dut.py
    py-scripts/chamber_ctl.py
    py-scripts/create_bond.py
    py-scripts/create_bridge.py
    py-scripts/create_chamberview_dut.py
    py-scripts/create_chamberview.py
    py-scripts/create_l3.py
    py-scripts/create_l3_stations.py
    py-scripts/create_l4.py
    py-scripts/create_macvlan.py
    py-scripts/create_qvlan.py
    py-scripts/create_station_from_df.py
    py-scripts/create_station.py
    py-scripts/create_vap.py
    py-scripts/create_vr.py
    py-scripts/csv_convert.py
    py-scripts/csv_processor.py
    py-scripts/cv_manager.py
    py-scripts/lf_add_profile.py
    py-scripts/lf_ap_auto_test.py
    py-scripts/lf_atten_mod_test.py
    py-scripts/lf_base_interop_profile.py
    py-scripts/lf_chamberview_tools.py
    py-scripts/lf_cleanup.py
    py-scripts/lf_client_visualization.py
    py-scripts/lf_continuous_throughput_test.py
    py-scripts/lf_create_vap_cv.py
    py-scripts/lf_create_wanlink.py
    py-scripts/lf_dataplane_test.py
    py-scripts/lf_ftp.py
    py-scripts/lf_interop_modify.py
    py-scripts/lf_interop_port_reset_test.py
    py-scripts/lf_interop_ping.py
    py-scripts/lf_interop_ping_plotter.py
    py-scripts/lf_interop_pdu_automation.py
    py-scripts/lf_interop_qos.py
    py-scripts/lf_interop_real_browser_test.py
    py-scripts/lf_interop_rvr_test.py
    py-scripts/lf_interop_throughput.py
    py-scripts/lf_json_api.py
    py-scripts/lf_kpi_csv.py
    py-scripts/lf_mesh_test.py
    py-scripts/lf_pcap.py
    py-scripts/lf_rfgen_info.py
    py-scripts/lf_rssi_process.py
    py-scripts/lf_rvr_test.py
    py-scripts/lf_sniff_radio.py
    py-scripts/lf_snp_test.py
    py-scripts/lf_test_generic.py
    py-scripts/lf_tr398_test.py
    py-scripts/lf_tr398v2_test.py
    py-scripts/lf_tr398v4_test.py
    py-scripts/lf_webpage.py
    py-scripts/lf_we_can_wifi_capacity.py
    py-scripts/lf_wifi_capacity_test.py
    py-scripts/monitor_cx.py
    py-scripts/raw_cli.py
    py-scripts/run_cv_scenario.py
    py-scripts/run_voip_cx.py
    py-scripts/rvr_scenario.py
    py-scripts/ssh_remote.py
    py-scripts/sta_connect2.py
    py-scripts/sta_connect_example.py
    py-scripts/sta_connect_multi_example.py
    py-scripts/sta_scan_test.py
    py-scripts/test_client_admission.py
    py-scripts/test_fileio.py
    py-scripts/test_generic.py
    py-scripts/test_l3.py
    py-scripts/test_l3_longevity.py
    py-scripts/test_l3_scenario_throughput.py
    py-scripts/test_l3_unicast_traffic_gen.py
    py-scripts/test_l3_WAN_LAN.py
    py-scripts/test_l4.py
    py-scripts/test_status_msg.py
    py-scripts/test_wanlink.py
    py-scripts/update_dependencies.py
    py-scripts/tip_station_powersave.py
    py-scripts/webGUI_update_dependencies.py
)
./gen_html_help.pl "${scripts[@]}" > $DESTF
echo "...created $DESTF"
