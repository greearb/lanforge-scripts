#!/usr/bin/env python3
"""
NAME: lf_scale_test.py

PURPOSE: This script is designed to run scale tests under various scenarios.

EXAMPLE:
        # Sample cli to test Scale Test :

        ./lf_scale_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name scale-instance --config_name test_con --dut LISP_VAP_DUT
        --raw_lines_file my_scale_cfg.txt
        --pull_report


Example 2:

        # Sample cli to test Scale Test with <_dp_cli_config_>.json :

        # TODO:  Maybe no good way to use .json to configure Scale test.

SCRIPT_CLASSIFICATION:  Test

SCRIPT_CATEGORIES:   Performance,  Functional,  KPI Generation,  Report Generation

NOTES:
        This script is used to automate running Scale tests.  You may need to view a Scale test
        configured through the GUI to understand the options and how best to input data.

        Note :
                To Run this script gui should be opened with

                path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                        pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                        ./lfclient.bash -cli-socket 3990

        ---> lf_scale_test.py is designed to run scale test using config file
             that user has previously saved from the GUI Scale Test.

            ./lf_scale_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
            --instance_name <instance name> --config_name test_con
            --raw_lines_file <input config file name>
            --pull_report

            *   --raw_line : 'line contents' will add any setting to the test config.  This is useful way to support
                        any options not specifically enabled by the command options.

            *  --set modifications will be applied after the other config has happened, so it can be used to
                        override any other config.

    Example of raw text config for Scale, to show other possible options:

pre_post_anon: 0
pre_post_inline: 0
do_pre_post: 1
anonymize_ap: 0
show_events: 1
show_log: 0
log_stdout: 0
port_sorting: 2
kpi_id: Scale
get_csv_cb: 0
auto_save: 0
rpt_path:
rpt_path_make_subdir: 1
bg: 0xE0ECF8
dut_info_override:
dut_info_cmd:
test_rig:
test_tag:
rpt_name:
rpt_dir_prefix_textfield:
show_scan: 1
auto_helper: 1
allow_11w: 0
use_mcs_histograms: 1
use_mlo_histograms: 1
disable_mlo: 0
extra_tx_status: 0
extra_rx_status: 0
txs_all_status: 0
sae_pwe: 2
skip_ac: 0
skip_be: 0
skip_ax: 0
skip_2: 0
skip_6: 0
skip_mlo: 0
skip_5: 0
skip_5b: 1
skip_dual: 0
skip_tri: 1
skip_tri_5b: 1
skip_rebuild: 0
udp_gro: 0
multi_cx: 1
udp_burst: 0
payload_pattern: 0
sndbuf_tcp: 0
sndbuf_udp: 0
rcvbuf_tcp: 0
rcvbuf_udp: 0
show_per_loop_totals: 1
clear_ports_too: 0
show_log_scale: 0
show_adv_lat_graph: 0
realtime_per_port: 0
realtime_per_cx: 0
sts-0-expanded: 1
sts-0-name: morning
sts-0-duration: 600000
sts-0-is_active: 1
sts-0-0-expanded: 1
sts-0-0-name: student-2
sts-0-0-profile: STA-AC
sts-0-0-amount: 15
sts-0-0-location: Spread-Campus
sts-0-0-ssid: ASUS_2C
sts-0-0-band: 0
sts-0-0-radio_assignment: Unique Profile
sts-0-0-bind_bssid: 0
sts-0-0-0-expanded: 1
sts-0-0-0-name: dl-tcp
sts-0-0-0-upstream_port: 1.1.2 eth2
sts-0-0-0-action: TCP Layer-3 Traffic
sts-0-0-0-concurrent: 1
sts-0-0-0-sniff_packets: 0
sts-0-0-0-min_duration: 480000
sts-0-0-0-max_duration: Same
sts-0-0-0-min_speed_u: 56000
sts-0-0-0-max_speed_u: 0
sts-0-0-0-min_speed_d: 1544000
sts-0-0-0-max_speed_d: 0
sts-0-0-0-url: <Custom>
sts-0-0-0-destination_url: /dev/null
sts-0-0-0-destination: Any
sts-0-0-0-urls_per_ten:
sts-0-0-0-repeat_count: <Custom>
sts-0-0-0-pf_metric: 950000
sts-0-0-0-ul_dl: Download
sts-0-0-0-reset_timer_max: 0
sts-0-0-0-reset_timer_min: 0
sts-0-0-0-max_station_reset: <Custom>
sts-0-0-0-min_station_reset: <Custom>
sts-0-0-1-expanded: 1
sts-0-0-1-name: ping
sts-0-0-1-upstream_port: 1.1.2 eth2
sts-0-0-1-action: Ping a Target
sts-0-0-1-concurrent: 1
sts-0-0-1-sniff_packets: 0
sts-0-0-1-min_duration: 480000
sts-0-0-1-max_duration: Same
sts-0-0-1-min_speed_u: 56000
sts-0-0-1-max_speed_u: 0
sts-0-0-1-min_speed_d: 1544000
sts-0-0-1-max_speed_d: 0
sts-0-0-1-url: 192.168.50.247
sts-0-0-1-destination_url: /dev/null
sts-0-0-1-destination: Any
sts-0-0-1-urls_per_ten:
sts-0-0-1-repeat_count:
sts-0-0-1-pf_metric: 950000
sts-0-0-1-ul_dl: Download
sts-0-0-1-reset_timer_max: 0
sts-0-0-1-reset_timer_min: 0
sts-0-0-1-max_station_reset:
sts-0-0-1-min_station_reset:
sts-0-0-2-expanded: 1
sts-0-0-2-name: voip
sts-0-0-2-upstream_port: 1.1.2 eth2
sts-0-0-2-action: VoIP Traffic
sts-0-0-2-concurrent: 1
sts-0-0-2-sniff_packets: 0
sts-0-0-2-min_duration: 480000
sts-0-0-2-max_duration: Same
sts-0-0-2-min_speed_u: 56000
sts-0-0-2-max_speed_u: 0
sts-0-0-2-min_speed_d: 1544000
sts-0-0-2-max_speed_d: 0
sts-0-0-2-url: 192.168.50.247
sts-0-0-2-destination_url: /dev/null
sts-0-0-2-destination: Any
sts-0-0-2-urls_per_ten:
sts-0-0-2-repeat_count:
sts-0-0-2-pf_metric: 950000
sts-0-0-2-ul_dl: Download
sts-0-0-2-reset_timer_max: 0
sts-0-0-2-reset_timer_min: 0
sts-0-0-2-max_station_reset:
sts-0-0-2-min_station_reset:
sts-0-1-expanded: 1
sts-0-1-name: student-5
sts-0-1-profile: STA-AUTO
sts-0-1-amount: 15
sts-0-1-location: Spread-Campus
sts-0-1-ssid: ASUS_2C_5G-1
sts-0-1-band: 1
sts-0-1-radio_assignment: Unique Profile
sts-0-1-bind_bssid: 0
sts-0-1-0-expanded: 1
sts-0-1-0-name: dl-tcp
sts-0-1-0-upstream_port: 1.1.2 eth2
sts-0-1-0-action: TCP Layer-3 Traffic
sts-0-1-0-concurrent: 1
sts-0-1-0-sniff_packets: 0
sts-0-1-0-min_duration: 480000
sts-0-1-0-max_duration: Same
sts-0-1-0-min_speed_u: 56000
sts-0-1-0-max_speed_u: 0
sts-0-1-0-min_speed_d: 1544000
sts-0-1-0-max_speed_d: 0
sts-0-1-0-url:
sts-0-1-0-destination_url: /dev/null
sts-0-1-0-destination: Any
sts-0-1-0-urls_per_ten:
sts-0-1-0-repeat_count:
sts-0-1-0-pf_metric: 950000
sts-0-1-0-ul_dl: Download
sts-0-1-0-reset_timer_max: 0
sts-0-1-0-reset_timer_min: 0
sts-0-1-0-max_station_reset:
sts-0-1-0-min_station_reset:
sts-0-1-1-expanded: 1
sts-0-1-1-name: ping
sts-0-1-1-upstream_port: 1.1.2 eth2
sts-0-1-1-action: Ping a Target
sts-0-1-1-concurrent: 1
sts-0-1-1-sniff_packets: 0
sts-0-1-1-min_duration: 480000
sts-0-1-1-max_duration: Same
sts-0-1-1-min_speed_u: 56000
sts-0-1-1-max_speed_u: 0
sts-0-1-1-min_speed_d: 1544000
sts-0-1-1-max_speed_d: 0
sts-0-1-1-url: 192.168.50.247
sts-0-1-1-destination_url: /dev/null
sts-0-1-1-destination: Any
sts-0-1-1-urls_per_ten:
sts-0-1-1-repeat_count:
sts-0-1-1-pf_metric: 950000
sts-0-1-1-ul_dl: Download
sts-0-1-1-reset_timer_max: 0
sts-0-1-1-reset_timer_min: 0
sts-0-1-1-max_station_reset:
sts-0-1-1-min_station_reset:
sts-0-1-2-expanded: 1
sts-0-1-2-name: voip
sts-0-1-2-upstream_port: 1.1.2 eth2
sts-0-1-2-action: VoIP Traffic
sts-0-1-2-concurrent: 1
sts-0-1-2-sniff_packets: 0
sts-0-1-2-min_duration: 480000
sts-0-1-2-max_duration: Same
sts-0-1-2-min_speed_u: 56000
sts-0-1-2-max_speed_u: 0
sts-0-1-2-min_speed_d: 1544000
sts-0-1-2-max_speed_d: 0
sts-0-1-2-url: 192.168.50.247
sts-0-1-2-destination_url: /dev/null
sts-0-1-2-destination: Any
sts-0-1-2-urls_per_ten:
sts-0-1-2-repeat_count:
sts-0-1-2-pf_metric: 950000
sts-0-1-2-ul_dl: Download
sts-0-1-2-reset_timer_max: 0
sts-0-1-2-reset_timer_min: 0
sts-0-1-2-max_station_reset:
sts-0-1-2-min_station_reset:
operator: Autobot
start_time: 9
show_dut_totals: 1
num_loops: 0
radio_freq-1.1.wiphy0: -1
radio_freq-1.1.wiphy1: -1
radio_freq-1.1.wiphy2: -1
radio_freq-1.1.wiphy4: -1
radio_freq-1.1.wiphy5: -1
radio_freq-1.1.wiphy6: -1
radio_freq-1.1.wiphy7: -1

STATUS: Functional

VERIFIED_ON:   11-MAY-2023,
             GUI Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

"""
import sys
import os
import importlib
import argparse
import time
import json
import logging


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test
cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


class ScaleTest(cv_test):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 ssh_port=22,
                 local_lf_report_dir="",
                 instance_name="scale_instance",
                 config_name="scale_config",
                 pull_report=False,
                 load_old_cfg=False,
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 verbosity='5'
                 ):
        super().__init__(lfclient_host=lf_host, lfclient_port=lf_port)

        # NOTE: Do not move these into the function definition.
        #       Otherwise, they will become immutable lists
        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []

        self.lf_host = lf_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.instance_name = instance_name
        self.config_name = config_name
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "Scale"
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.graph_groups = graph_groups
        self.ssh_port = ssh_port
        self.local_lf_report_dir = local_lf_report_dir
        self.test_rig = test_rig
        self.test_tag = test_tag
        self.verbosity = verbosity

    def setup(self):
        # Nothing to do at this time.
        return

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        blob_test = "Scale-"

        # To delete old config with same name
        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)
        self.show_text_blob(config_name=None,
                            blob_test_name=None,
                            brief=False)

        # Test related settings
        cfg_options = []

        self.apply_cfg_options(cfg_options=cfg_options,
                               enables=self.enables,
                               disables=self.disables,
                               raw_lines=self.raw_lines,
                               raw_lines_file=self.raw_lines_file)

        # cmd line args take precedence and so come last in the cfg array.
        if self.test_rig != "":
            cfg_options.append("test_rig: " + self.test_rig)
        if self.test_tag != "":
            cfg_options.append("test_tag: " + self.test_tag)

        # We deleted the scenario earlier, now re-build new one line at a time.

        self.build_cfg(config_name=self.config_name,
                       blob_test=blob_test,
                       cfg_options=cfg_options)

        cv_cmds = []

        cmd = "cv set '%s' 'VERBOSITY' '%s'" % (self.instance_name, self.verbosity)
        cv_cmds.append(cmd)

        self.create_and_run_test(load_old_cfg=self.load_old_cfg,
                                 test_name=self.test_name,
                                 instance_name=self.instance_name,
                                 config_name=self.config_name,
                                 sets=self.sets,
                                 pull_report=self.pull_report,
                                 lf_host=self.lf_host,
                                 lf_user=self.lf_user,
                                 lf_password=self.lf_password,
                                 cv_cmds=cv_cmds,
                                 ssh_port=self.ssh_port,
                                 local_lf_report_dir=self.local_lf_report_dir,
                                 graph_groups_file=self.graph_groups)
        # To delete old config with same name
        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)


def main():
    help_summary = "The Candela Tech Scale test is designed to emulate a day in the life " \
                   "of a network, especially a multi-location campus network."

    parser = argparse.ArgumentParser(
        prog='lf_scale_test',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Scale Test
            ''',
        description="""
NAME: lf_scale_test.py

PURPOSE: This script is designed to run scale tests under various scenarios.

EXAMPLE:
        # Sample cli to test Scale Test :

        ./lf_scale_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name scale-instance --config_name test_con
        --raw_lines_file my_scale_test_cfg.txt
        --pull_report

Example 2:

        # Sample cli to test Scale Test with <_dp_cli_config_>.json :

        #TODO

SCRIPT_CLASSIFICATION:  Test

SCRIPT_CATEGORIES:   Performance,  Functional,  KPI Generation,  Report Generation

NOTES:
        This script is used to automate running Scale tests.  You may need to view a Scale test
        configured through the GUI to understand the options and how best to input data.

        Note :
                To Run this script gui should be opened with

                path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                        pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                        ./lfclient.bash -cli-socket 3990

        ---> lf_scale_test.py is designed to run scale tests under various scenarios.

            ./lf_scale_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
            --instance_name <instance name> --config_name test_con
            --raw_lines_file my_scale_test_cfg.txt
            --pull_report

            *   --raw_line : 'line contents' will add any setting to the test config. This is useful way to support
                        any options not specifically enabled by the command options.

            *  --set modifications will be applied after the other config has happened, so it can be used to
                        override any other config.

    Example of raw text config for Scale, to show other possible options:

pre_post_anon: 0
pre_post_inline: 0
do_pre_post: 1
anonymize_ap: 0
show_events: 1
show_log: 0
log_stdout: 0
port_sorting: 2
kpi_id: Scale
get_csv_cb: 0
auto_save: 0
rpt_path:
rpt_path_make_subdir: 1
bg: 0xE0ECF8
dut_info_override:
dut_info_cmd:
test_rig:
test_tag:
rpt_name:
rpt_dir_prefix_textfield:
show_scan: 1
auto_helper: 1
allow_11w: 0
use_mcs_histograms: 1
use_mlo_histograms: 1
disable_mlo: 0
extra_tx_status: 0
extra_rx_status: 0
txs_all_status: 0
sae_pwe: 2
skip_ac: 0
skip_be: 0
skip_ax: 0
skip_2: 0
skip_6: 0
skip_mlo: 0
skip_5: 0
skip_5b: 1
skip_dual: 0
skip_tri: 1
skip_tri_5b: 1
skip_rebuild: 0
udp_gro: 0
multi_cx: 1
udp_burst: 0
payload_pattern: 0
sndbuf_tcp: 0
sndbuf_udp: 0
rcvbuf_tcp: 0
rcvbuf_udp: 0
show_per_loop_totals: 1
clear_ports_too: 0
show_log_scale: 0
show_adv_lat_graph: 0
realtime_per_port: 0
realtime_per_cx: 0
sts-0-expanded: 1
sts-0-name: morning
sts-0-duration: 600000
sts-0-is_active: 1
sts-0-0-expanded: 1
sts-0-0-name: student-2
sts-0-0-profile: STA-AC
sts-0-0-amount: 15
sts-0-0-location: Spread-Campus
sts-0-0-ssid: ASUS_2C
sts-0-0-band: 0
sts-0-0-radio_assignment: Unique Profile
sts-0-0-bind_bssid: 0
sts-0-0-0-expanded: 1
sts-0-0-0-name: dl-tcp
sts-0-0-0-upstream_port: 1.1.2 eth2
sts-0-0-0-action: TCP Layer-3 Traffic
sts-0-0-0-concurrent: 1
sts-0-0-0-sniff_packets: 0
sts-0-0-0-min_duration: 480000
sts-0-0-0-max_duration: Same
sts-0-0-0-min_speed_u: 56000
sts-0-0-0-max_speed_u: 0
sts-0-0-0-min_speed_d: 1544000
sts-0-0-0-max_speed_d: 0
sts-0-0-0-url: <Custom>
sts-0-0-0-destination_url: /dev/null
sts-0-0-0-destination: Any
sts-0-0-0-urls_per_ten:
sts-0-0-0-repeat_count: <Custom>
sts-0-0-0-pf_metric: 950000
sts-0-0-0-ul_dl: Download
sts-0-0-0-reset_timer_max: 0
sts-0-0-0-reset_timer_min: 0
sts-0-0-0-max_station_reset: <Custom>
sts-0-0-0-min_station_reset: <Custom>
sts-0-0-1-expanded: 1
sts-0-0-1-name: ping
sts-0-0-1-upstream_port: 1.1.2 eth2
sts-0-0-1-action: Ping a Target
sts-0-0-1-concurrent: 1
sts-0-0-1-sniff_packets: 0
sts-0-0-1-min_duration: 480000
sts-0-0-1-max_duration: Same
sts-0-0-1-min_speed_u: 56000
sts-0-0-1-max_speed_u: 0
sts-0-0-1-min_speed_d: 1544000
sts-0-0-1-max_speed_d: 0
sts-0-0-1-url: 192.168.50.247
sts-0-0-1-destination_url: /dev/null
sts-0-0-1-destination: Any
sts-0-0-1-urls_per_ten:
sts-0-0-1-repeat_count:
sts-0-0-1-pf_metric: 950000
sts-0-0-1-ul_dl: Download
sts-0-0-1-reset_timer_max: 0
sts-0-0-1-reset_timer_min: 0
sts-0-0-1-max_station_reset:
sts-0-0-1-min_station_reset:
sts-0-0-2-expanded: 1
sts-0-0-2-name: voip
sts-0-0-2-upstream_port: 1.1.2 eth2
sts-0-0-2-action: VoIP Traffic
sts-0-0-2-concurrent: 1
sts-0-0-2-sniff_packets: 0
sts-0-0-2-min_duration: 480000
sts-0-0-2-max_duration: Same
sts-0-0-2-min_speed_u: 56000
sts-0-0-2-max_speed_u: 0
sts-0-0-2-min_speed_d: 1544000
sts-0-0-2-max_speed_d: 0
sts-0-0-2-url: 192.168.50.247
sts-0-0-2-destination_url: /dev/null
sts-0-0-2-destination: Any
sts-0-0-2-urls_per_ten:
sts-0-0-2-repeat_count:
sts-0-0-2-pf_metric: 950000
sts-0-0-2-ul_dl: Download
sts-0-0-2-reset_timer_max: 0
sts-0-0-2-reset_timer_min: 0
sts-0-0-2-max_station_reset:
sts-0-0-2-min_station_reset:
sts-0-1-expanded: 1
sts-0-1-name: student-5
sts-0-1-profile: STA-AUTO
sts-0-1-amount: 15
sts-0-1-location: Spread-Campus
sts-0-1-ssid: ASUS_2C_5G-1
sts-0-1-band: 1
sts-0-1-radio_assignment: Unique Profile
sts-0-1-bind_bssid: 0
sts-0-1-0-expanded: 1
sts-0-1-0-name: dl-tcp
sts-0-1-0-upstream_port: 1.1.2 eth2
sts-0-1-0-action: TCP Layer-3 Traffic
sts-0-1-0-concurrent: 1
sts-0-1-0-sniff_packets: 0
sts-0-1-0-min_duration: 480000
sts-0-1-0-max_duration: Same
sts-0-1-0-min_speed_u: 56000
sts-0-1-0-max_speed_u: 0
sts-0-1-0-min_speed_d: 1544000
sts-0-1-0-max_speed_d: 0
sts-0-1-0-url:
sts-0-1-0-destination_url: /dev/null
sts-0-1-0-destination: Any
sts-0-1-0-urls_per_ten:
sts-0-1-0-repeat_count:
sts-0-1-0-pf_metric: 950000
sts-0-1-0-ul_dl: Download
sts-0-1-0-reset_timer_max: 0
sts-0-1-0-reset_timer_min: 0
sts-0-1-0-max_station_reset:
sts-0-1-0-min_station_reset:
sts-0-1-1-expanded: 1
sts-0-1-1-name: ping
sts-0-1-1-upstream_port: 1.1.2 eth2
sts-0-1-1-action: Ping a Target
sts-0-1-1-concurrent: 1
sts-0-1-1-sniff_packets: 0
sts-0-1-1-min_duration: 480000
sts-0-1-1-max_duration: Same
sts-0-1-1-min_speed_u: 56000
sts-0-1-1-max_speed_u: 0
sts-0-1-1-min_speed_d: 1544000
sts-0-1-1-max_speed_d: 0
sts-0-1-1-url: 192.168.50.247
sts-0-1-1-destination_url: /dev/null
sts-0-1-1-destination: Any
sts-0-1-1-urls_per_ten:
sts-0-1-1-repeat_count:
sts-0-1-1-pf_metric: 950000
sts-0-1-1-ul_dl: Download
sts-0-1-1-reset_timer_max: 0
sts-0-1-1-reset_timer_min: 0
sts-0-1-1-max_station_reset:
sts-0-1-1-min_station_reset:
sts-0-1-2-expanded: 1
sts-0-1-2-name: voip
sts-0-1-2-upstream_port: 1.1.2 eth2
sts-0-1-2-action: VoIP Traffic
sts-0-1-2-concurrent: 1
sts-0-1-2-sniff_packets: 0
sts-0-1-2-min_duration: 480000
sts-0-1-2-max_duration: Same
sts-0-1-2-min_speed_u: 56000
sts-0-1-2-max_speed_u: 0
sts-0-1-2-min_speed_d: 1544000
sts-0-1-2-max_speed_d: 0
sts-0-1-2-url: 192.168.50.247
sts-0-1-2-destination_url: /dev/null
sts-0-1-2-destination: Any
sts-0-1-2-urls_per_ten:
sts-0-1-2-repeat_count:
sts-0-1-2-pf_metric: 950000
sts-0-1-2-ul_dl: Download
sts-0-1-2-reset_timer_max: 0
sts-0-1-2-reset_timer_min: 0
sts-0-1-2-max_station_reset:
sts-0-1-2-min_station_reset:
operator: Autobot
start_time: 9
show_dut_totals: 1
num_loops: 0
radio_freq-1.1.wiphy0: -1
radio_freq-1.1.wiphy1: -1
radio_freq-1.1.wiphy2: -1
radio_freq-1.1.wiphy4: -1
radio_freq-1.1.wiphy5: -1
radio_freq-1.1.wiphy6: -1
radio_freq-1.1.wiphy7: -1

STATUS: Functional

VERIFIED_ON:   11-MAY-2023,
             GUI Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

      """
    )

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument('--json',
                        help="Path to JSON configuration file for test. When specified, JSON takes precedence over command line args.",
                        default="")
    parser.add_argument("--verbosity",
                        default="5",
                        help="Verbosity of the report specified as single value in 1 - 11 range (whole numbers).\n"
                             "The larger the number, the more verbose. Default: 5")
    parser.add_argument("--graph_groups",
                        help="Path to file to save graph_groups to on local system",
                        default=None)
    parser.add_argument("--local_lf_report_dir",
                        help="Path to directory to pull remote report data to on local system",
                        default="")

    parser.add_argument("--lf_logger_config_json",
                        help="Path to logger JSON configuration")
    parser.add_argument('--help_summary',
                        default=None,
                        action="store_true",
                        help='Show summary of what this script does')
    parser.add_argument('--logger_no_file',
                        default=None,
                        action="store_true",
                        help='Show loggingout without the trailing file name and line')

    # TODO:  Add debug and log-level support, and propagate as needed.
    # TODO:  Add ability to pull from a machine that is not running the
    #   GUI, for instance when GUI is running locally against a remote LANforge system.

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    # use json config file
    if args.json:
        if os.path.exists(args.json):
            with open(args.json, 'r') as json_config:
                json_data = json.load(json_config)
        else:
            return FileNotFoundError("Error reading {}".format(args.json))
        # json configuation takes presidence to command line
        if "mgr" in json_data:
            args.mgr = json_data["mgr"]
        if "port" in json_data:
            args.port = json_data["port"]
        if "lf_user" in json_data:
            args.lf_user = json_data["lf_user"]
        if "lf_password" in json_data:
            args.lf_password = json_data["lf_password"]
        if "instance_name" in json_data:
            args.instance_name = json_data["instance_name"]
        if "config_name" in json_data:
            args.config_name = json_data["config_name"]
        if "pull_report" in json_data:
            args.pull_report = json_data["pull_report"]
        if "raw_line" in json_data:
            # the json_data is a list , need to make into a list of lists, to match command line raw_line paramaters
            # https://www.tutorialspoint.com/convert-list-into-list-of-lists-in-python
            json_data_tmp = [[x] for x in json_data["raw_line"]]
            args.raw_line = json_data_tmp

    cv_base_adjust_parser(args)

    if args.logger_no_file:
        f = '%(created)f %(levelname)-8s %(message)s'
        ff = logging.Formatter(fmt=f)
        for handler in logging.getLogger().handlers:
            handler.setFormatter(ff)

    CV_Test = ScaleTest(lf_host=args.mgr,
                        lf_port=args.port,
                        lf_user=args.lf_user,
                        lf_password=args.lf_password,
                        instance_name=args.instance_name,
                        config_name=args.config_name,
                        pull_report=args.pull_report,
                        local_lf_report_dir=args.local_lf_report_dir,
                        load_old_cfg=args.load_old_cfg,
                        enables=args.enable,
                        disables=args.disable,
                        raw_lines=args.raw_line,
                        raw_lines_file=args.raw_lines_file,
                        sets=args.set,
                        graph_groups=args.graph_groups,
                        test_rig=args.test_rig,
                        verbosity=args.verbosity
                        )
    CV_Test.setup()
    CV_Test.run()

    if CV_Test.kpi_results_present():
        logger.info("lf_scale_test generated kpi.csv")
    else:
        logger.info("FAILED: lf_scale_test did not generate kpi.csv)")
        exit(1)

    if CV_Test.passes():
        CV_Test.exit_success()
    else:
        CV_Test.exit_fail()


if __name__ == "__main__":
    main()
