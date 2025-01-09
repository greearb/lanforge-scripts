#!/usr/bin/env python3

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


class ContinuousThroughput(cv_test):
    def __init__(self,
                 mgr="localhost",
                 port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 ssh_port=22,
                 local_lf_report_dir="/tmp/Continuous_Throughput_reports",
                 instance_name="ctt_instance",
                 config_name="ctt_config",
                 upstream=None,
                 pull_report=False,
                 load_old_cfg=False,
                 upload_speed="0",
                 download_speed="85%",
                 duration="15s",
                 station=None,
                 dut="NA",
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 verbosity='5',
                 **kwargs):
        super().__init__(lfclient_host=mgr, lfclient_port=port)

        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []

        self.mgr = mgr
        self.port = port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.instance_name = instance_name
        self.config_name = config_name
        self.dut = dut
        self.duration = duration
        self.upstream = upstream
        self.station = station
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "Continuous Throughput"
        self.upload_speed = upload_speed
        self.download_speed = download_speed
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
        return

    def run(self):
        print(self.local_lf_report_dir)
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        # this test name MUST match what the GUI expects
        blob_test = "continuous-tput-test-latest-"

        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)
        self.show_text_blob(config_name=None,
                            blob_test_name=None,
                            brief=False)

        cfg_options = []

        self.apply_cfg_options(cfg_options=cfg_options,
                               enables=self.enables,
                               disables=self.disables,
                               raw_lines=self.raw_lines,
                               raw_lines_file=self.raw_lines_file)

        if self.upstream != "":
            cfg_options.append(f"upstream_port: {self.upstream}")
        if self.station != "":
            cfg_options.append(f"traffic_port: {self.station}")
        if self.download_speed != "":
            cfg_options.append(f"speed: {self.download_speed}")
        if self.upload_speed != "":
            cfg_options.append(f"speed2: {self.upload_speed}")
        if self.duration != "":
            cfg_options.append(f"duration: {self.duration}")
        if self.dut != "":
            cfg_options.append(f"selected_dut: {self.dut}")
        if self.test_rig != "":
            cfg_options.append(f"test_rig: {self.test_rig}")
        if self.test_tag != "":
            cfg_options.append(f"test_tag: {self.test_tag}")

        self.build_cfg(config_name=self.config_name,
                       blob_test=blob_test,
                       cfg_options=cfg_options)

        cv_cmds = []

        cmd = f"cv set '{self.instance_name}' 'VERBOSITY' '{self.verbosity}'"
        cv_cmds.append(cmd)

        self.create_and_run_test(load_old_cfg=self.load_old_cfg,
                                 test_name=self.test_name,
                                 instance_name=self.instance_name,
                                 config_name=self.config_name,
                                 sets=self.sets,
                                 pull_report=self.pull_report,
                                 lf_host=self.mgr,
                                 lf_user=self.lf_user,
                                 lf_password=self.lf_password,
                                 cv_cmds=cv_cmds,
                                 ssh_port=self.ssh_port,
                                 local_lf_report_dir=self.local_lf_report_dir,
                                 graph_groups_file=self.graph_groups)

        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)


def help_summary_txt():
    return '''\
    The Candela WiFi Continuous Rotation test is designed to quickly test throughput
    and other metrics at different rotations, attenuation, and other configured values.
    For each combination of settings, it will start traffic and rotate the turntable,
    gathering stats often to generate report data at different rotations.
    The traffic test will be stopped only at the end of each rotation.
    '''


def init_argparse():
    return argparse.ArgumentParser(
        prog='lf_continuous_throughput_test',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Continuous Throughput Test
            ''',
        description="""
NAME: lf_continuous_throughput_test.py

PURPOSE: This script is designed to run continuous throughput tests under various scenarios.

EXAMPLE:
        # Sample cli to test Continuous Throughput Test:

        ./lf_continuous_throughput_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name continuous-throughput-instance --config_name test_con --upstream 1.1.eth1 --dut LISP_VAP_DUT
        --duration 30s --station 1.1.wlan0 --download_speed 85% --upload_speed 0 --raw_line 'pkts: 60'
        --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit' --raw_line 'traffic_types: UDP'
        --raw_line 'bandw_options: 20' --raw_line 'spatial_streams: 2' --raw_line 'modes: 802.11bgn-AX' --pull_report

        # Sample cli to test continuous_throughput Test with influx db (Optional):

        ./lf_continuous_throughput_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name continuous-throughput-instance --config_name test_con --upstream 1.1.eth2 --dut linksys-8450
        --duration 15s --station 1.1.sta01500 --download_speed 85% --upload_speed 0
        --raw_line 'pkts: Custom;60;142;256;512;1024;MTU' --raw_line 'cust_pkt_sz: 88 1200'
        --raw_line 'directions: DUT Transmit;DUT Receive' --raw_line 'traffic_types: UDP;TCP'
        --test_rig Testbed-01 --pull_report


Example 2:

        # Sample cli to test Continuous Throughput Test with <_ct_cli_config_>.json:

        ./lf_continuous_throughput_test.py --json <name>.json

        The Example/Sample json file should be:

            "lf_continuous_throughput_config.json"

            Sample <name>.json between using eth1 and eth2
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"continuous-throughput-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.eth2",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP", "bandw_options: 20", "spatial_streams: 1"]
            }

            Sample <name>.json between using eth1 and station 1.1.sta0002
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"continuous-throughput-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.sta0002",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP", "bandw_options: 20", "spatial_streams: 1"]
            }

SCRIPT_CLASSIFICATION:  Test

SCRIPT_CATEGORIES:   Performance,  Functional,  KPI Generation,  Report Generation

NOTES:
        This script is used to automate running continuous_throughput tests.  You may need to view
        a continuous_throughput test configured through the GUI to understand the options and how best to input data.

        Note :
                To Run this script gui should be opened with

                path: cd LANforgeGUI_5.4.7 (5.4.7 can be changed with GUI version)
                        pwd (Output : /home/lanforge/LANforgeGUI_5.4.7)
                        ./lfclient.bash -cli-socket 3990

        ---> lf_continuous_throughput_test.py is designed to run continuous_throughput tests under various scenarios.

            ./lf_continuous_throughput_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
            --instance_name <instance name> --config_name test_con --upstream <upstream port> --dut <dut name>
            --duration <test duration> --station <staion name> --download_speed <download rate>
            --upload_speed <opposite rate>
            --raw_line 'pkts: 60' --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit'
            --raw_line 'traffic_types: UDP' --raw_line 'bandw_options: 20' --raw_line 'spatial_streams: 2'
            --raw_line 'modes: 802.11bgn-AX' --pull_report

            *   --raw_line : 'line contents' will add any setting to the test config. This is useful way to support
                        any options not specifically enabled by the command options.

            *  --set modifications will be applied after the other config has happened, so it can be used to
                        override any other config.

    Example of raw text config for continuous_throughput, to show other possible options:

    show_events: 1
    show_log: 0
    log_stdout: 0
    get_csv_cb: 0
    auto_save: 1
    rpt_path:
    rpt_path_make_subdir: 1
    test_rig:
    test_tag:
    rpt_name:
    rpt_dir_prefix_textfield:
    show_scan: 1
    auto_helper: 0
    allow_11w: 0
    use_mcs_histograms: 1
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
    skip_5: 0
    skip_5b: 1
    skip_dual: 0
    skip_tri: 1
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
    realtime_per_port: 0
    realtime_per_cx: 0
    selected_dut: eero-root
    rvr_bringup_wait: 30000
    first_byte_wait: 30000
    duration: 300000
    settle_time: 10000
    sndbuf: 0
    rvr_helper:
    rcvbuf: 0
    traffic_port: 1.1.wlan0
    upstream_port: 1.1.eth3
    path_loss: 10
    ap_txpower: 0
    speed: 85%
    speed2: 0
    min_rssi_bound: -150
    max_rssi_bound: 0
    channels: AUTO
    modes: Auto
    pkts: Custom;60;MTU
    spatial_streams: 1
    security_options: AUTO
    bandw_options: AUTO
    traffic_types: UDP
    directions: DUT Transmit
    txo_preamble: OFDM
    txo_mcs: 0 CCK, OFDM, HT, VHT
    txo_retries: No Retry
    txo_sgi: OFF
    txo_txpower: 17
    attenuator: 0
    attenuator2: 0
    attenuator_mod: 255
    attenuator_mod2: 255
    attenuations: 0..+50..950
    attenuations2: 0..+50..950
    chamber: Root
    cust_pkt_sz: 88 1200
    show_bar_labels: 1
    show_prcnt_tput: 0
    show_passfail: 1
    show_last: 0
    show_gp_graphs: 1
    show_polar_graphs: 1
    show_line_graphs: 1
    pause_iter: 0
    max_unused_atten: 0
    adb_modify_wifi: 0
    aggregate_arc_count: 4
    show_realtime: 1
    mconn: 1
    mpkt: 1000
    tos: 0
    loop_iterations: 1



STATUS: Functional

VERIFIED_ON: 05-June-2024,
             GUI Version:  5.4.8
             Kernel Version: 6.9.0+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: False

      """
    )


def setup_logger(args):
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


def main():
    help_summary = help_summary_txt()

    parser = init_argparse()

    cv_add_base_parser(parser)

    parser.add_argument('--json',
                        help="Path to JSON configuration file for test."
                             " When specified, JSON takes precedence over command line args.",
                        default="")
    parser.add_argument("-u", "--upstream",
                        type=str,
                        default="",
                        help="Upstream port used in test. For example, \'1.1.eth2\'")
    parser.add_argument("--station",
                        type=str,
                        default="",
                        help="Station used in test. Example: \'1.1.sta01500\'")
    parser.add_argument("--dut",
                        default="",
                        help="Name of DUT used in test."
                             " Assumes DUT is already configured in LANforge. Example: \'linksys-8450\'")
    parser.add_argument("--download_speed",
                        default="",
                        help="Requested download speed used in test."
                             " Percentage of theoretical is also supported. Default: 85%%.")
    parser.add_argument("--upload_speed",
                        default="",
                        help="Requested upload speed used in test."
                             " Percentage of theoretical is also supported. Default: 0")
    parser.add_argument("--duration",
                        default="",
                        help="Duration of each traffic run")
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
    parser.add_argument("--log_level",
                        default=None,
                        help="Set logging level: debug | info | warning | error | critical")
    parser.add_argument('--help_summary',
                        default=None,
                        action="store_true",
                        help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    setup_logger(args)

    if args.json:
        if os.path.exists(args.json):
            with open(args.json, 'r') as json_config:
                json_data = json.load(json_config)
        else:
            return FileNotFoundError("Error reading {}".format(args.json))
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
        if "upstream" in json_data:
            args.upstream = json_data["upstream"]
        if "dut" in json_data:
            args.dut = json_data["dut"]
        if "duration" in json_data:
            args.duration = json_data["duration"]
        if "station" in json_data:
            args.station = json_data["station"]
        if "download_speed" in json_data:
            args.download_speed = json_data["download_speed"]
        if "upload_speed" in json_data:
            args.upload_speed = json_data["upload_speed"]
        if "pull_report" in json_data:
            args.pull_report = json_data["pull_report"]
        if "raw_line" in json_data:
            json_data_tmp = [[x] for x in json_data["raw_line"]]
            args.raw_line = json_data_tmp

    cv_base_adjust_parser(args)
    cv_test_inst = ContinuousThroughput(**vars(args), raw_lines=args.raw_line)
    cv_test_inst.setup()
    cv_test_inst.run()

    if cv_test_inst.kpi_results_present():
        logger.info("lf_continuous_throughput_test generated kpi.csv")
    else:
        logger.info("FAILED: lf_continuous_throughput_test did not generate kpi.csv")
        exit(1)

    if cv_test_inst.passes():
        cv_test_inst.exit_success()
    else:
        cv_test_inst.exit_fail()


if __name__ == "__main__":
    main()
