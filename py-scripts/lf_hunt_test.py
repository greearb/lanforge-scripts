#!/usr/bin/env python3
"""
NAME: lf_hunt_test.py

PURPOSE: This script is designed to run hunt tests under various scenarios.

EXAMPLE:
        # Sample cli to test Hunt Test :

        ./lf_hunt_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name hunt-instance --config_name test_con --upstream 1.1.eth1 --dut LISP_VAP_DUT
        --duration 30s --station 1.1.wlan0 --download_speed 85% --upload_speed 0 --raw_line 'pkts: 60'
        --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit' --raw_line 'traffic_types: UDP'
        --pull_report


Example 2:

        # Sample cli to test Hunt Test with <_dp_cli_config_>.json :

        ./lf_hunt_test.py --json <name>.json

        The Example/Sample json file should be :

            "lf_hunt_config.json"

            Sample <name>.json between using eth1 and eth2
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"hunt-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.eth2",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP"]
            }

            Sample <name>.json between using eth1 and station 1.1.sta0002
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"hunt-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.sta0002",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP"]
            }

SCRIPT_CLASSIFICATION:  Test

SCRIPT_CATEGORIES:   Performance,  Functional,  KPI Generation,  Report Generation

NOTES:
        This script is used to automate running Hunt tests.  You may need to view a Hunt test
        configured through the GUI to understand the options and how best to input data.

        Note :
                To Run this script gui should be opened with

                path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                        pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                        ./lfclient.bash -cli-socket 3990

        ---> lf_hunt_test.py is designed to run hunt tests under various scenarios.

            ./lf_hunt_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
            --instance_name <instance name> --config_name test_con --upstream <upstream port> --dut <dut name>
            --duration <test duration> --station <staion name> --download_speed <download rate> --upload_speed <Opposit rate>
            --raw_line 'pkts: 60' --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit'
            --raw_line 'traffic_types: UDP' --pull_report

            *   --raw_line : 'line contents' will add any setting to the test config.  This is useful way to support
                        any options not specifically enabled by the command options.

            *  --set modifications will be applied after the other config has happened, so it can be used to
                        override any other config.

    Example of raw text config for Hunt, to show other possible options:

pre_post_anon: 0
pre_post_inline: 0
do_pre_post: 1
anonymize_ap: 0
show_events: 1
show_log: 0
log_stdout: 0
port_sorting: 2
kpi_id: Hunt
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
auto_helper: 0
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
multi_cx: 3
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
selected_dut: ASUSRT-AX88U
duration: 15000
traffic_port: 1.1.wlan7
upstream_port: 1.1.eth2
path_loss: 10
speed: 85%
speed2: 0Kbps
min_rssi_bound: -150
max_rssi_bound: 0
pkts: 256
traffic_types: UDP
directions: DUT Transmit;DUT Receive
attenuator: 0
attenuator2: 0
attenuator_mod: 255
attenuator_mod2: 255
attenuations: 0..+50..950
attenuations2: 0..+50..950
chamber: 0
tt_deg: 0..+45..359
cust_pkt_sz:
show_3s: 0
show_ll_graphs: 1
show_gp_graphs: 1
show_1m: 1
pause_iter: 0
show_realtime: 1
operator: Autobot
mconn: 1
mpkt: 1000
cutoff_percentage: 20000
pkt_loss_thresh: 10000
txspeed_adjust: 1000000
overdrive: 100000
tos: 0
loop_iterations: 1

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


class HuntTest(cv_test):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 ssh_port=22,
                 local_lf_report_dir="",
                 instance_name="hunt_instance",
                 config_name="hunt_config",
                 upstream="1.1.eth2",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_speed="0",
                 download_speed="85%",
                 duration="15s",
                 station="1.1.sta01500",
                 dut="NA",
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 verbosity='5'):
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
        self.dut = dut
        self.duration = duration
        self.upstream = upstream
        self.station = station
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "Hunt"
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
        # Nothing to do at this time.
        return

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        blob_test = "hunt-test-"

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
        if self.upstream != "":
            cfg_options.append("upstream_port: " + self.upstream)
        if self.station != "":
            cfg_options.append("traffic_port: " + self.station)
        if self.download_speed != "":
            cfg_options.append("speed: " + self.download_speed)
        if self.upload_speed != "":
            cfg_options.append("speed2: " + self.upload_speed)
        if self.duration != "":
            cfg_options.append("duration: " + self.duration)
        if self.dut != "":
            cfg_options.append("selected_dut: " + self.dut)
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
    help_summary = "The Candela Tech Hunt test is designed to find the maximum throughput " \
                   "that passes the configured pass/fail metrics (packet loss currently)."

    parser = argparse.ArgumentParser(
        prog='lf_hunt_test',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Hunt Test
            ''',
        description="""
NAME: lf_hunt_test.py

PURPOSE: This script is designed to run hunt tests under various scenarios.

EXAMPLE:
        # Sample cli to test Hunt Test :

        ./lf_hunt_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --instance_name hunt-instance --config_name test_con --upstream 1.1.eth1 --dut LISP_VAP_DUT
        --duration 30s --station 1.1.wlan0 --download_speed 85% --upload_speed 0 --raw_line 'pkts: 60'
        --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit' --raw_line 'traffic_types: UDP'
        --pull_report

Example 2:

        # Sample cli to test Hunt Test with <_dp_cli_config_>.json :

        ./lf_hunt_test.py --json <name>.json

        The Example/Sample json file should be :

            "lf_hunt_config.json"

            Sample <name>.json between using eth1 and eth2
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"hunt-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.eth2",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP"]
            }

            Sample <name>.json between using eth1 and station 1.1.sta0002
            {
                "mgr":"192.168.0.101",
                "port":"8080",
                "lf_user":"lanforge",
                "lf_password":"lanforge",
                "instance_name":"hunt-instance",
                "config_name":"test_con",
                "upstream":"1.1.eth1",
                "dut":"asus_5g",
                "duration":"15s",
                "station":"1.1.sta0002",
                "download_speed":"85%",
                "upload_speed":"0",
                "raw_line":  ["pkts: Custom;60;MTU", "cust_pkt_sz: 88 1200", "directions: DUT Transmit",
                "traffic_types: UDP"]
            }

SCRIPT_CLASSIFICATION:  Test

SCRIPT_CATEGORIES:   Performance,  Functional,  KPI Generation,  Report Generation

NOTES:
        This script is used to automate running Hunt tests.  You may need to view a Hunt test
        configured through the GUI to understand the options and how best to input data.

        Note :
                To Run this script gui should be opened with

                path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                        pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                        ./lfclient.bash -cli-socket 3990

        ---> lf_hunt_test.py is designed to run hunt tests under various scenarios.

            ./lf_hunt_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
            --instance_name <instance name> --config_name test_con --upstream <upstream port> --dut <dut name>
            --duration <test duration> --station <staion name> --download_speed <download rate> --upload_speed <Opposit rate>
            --raw_line 'pkts: 60' --raw_line 'cust_pkt_sz: 88 1200' --raw_line 'directions: DUT Transmit'
            --raw_line 'traffic_types: UDP' --pull_report

            *   --raw_line : 'line contents' will add any setting to the test config. This is useful way to support
                        any options not specifically enabled by the command options.

            *  --set modifications will be applied after the other config has happened, so it can be used to
                        override any other config.

    Example of raw text config for Hunt, to show other possible options:

pre_post_anon: 0
pre_post_inline: 0
do_pre_post: 1
anonymize_ap: 0
show_events: 1
show_log: 0
log_stdout: 0
port_sorting: 2
kpi_id: Hunt
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
auto_helper: 0
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
multi_cx: 3
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
selected_dut: ASUSRT-AX88U
duration: 15000
traffic_port: 1.1.wlan7
upstream_port: 1.1.eth2
path_loss: 10
speed: 85%
speed2: 0Kbps
min_rssi_bound: -150
max_rssi_bound: 0
pkts: 256
traffic_types: UDP
directions: DUT Transmit;DUT Receive
attenuator: 0
attenuator2: 0
attenuator_mod: 255
attenuator_mod2: 255
attenuations: 0..+50..950
attenuations2: 0..+50..950
chamber: 0
tt_deg: 0..+45..359
cust_pkt_sz:
show_3s: 0
show_ll_graphs: 1
show_gp_graphs: 1
show_1m: 1
pause_iter: 0
show_realtime: 1
operator: Autobot
mconn: 1
mpkt: 1000
cutoff_percentage: 20000
pkt_loss_thresh: 10000
txspeed_adjust: 1000000
overdrive: 100000
tos: 0
loop_iterations: 1


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
                        help="Name of DUT used in test. Assumes DUT is already configured in LANforge. Example: \'linksys-8450\'")
    parser.add_argument("--download_speed",
                        default="",
                        help="Requested download speed used in test. Percentage of theoretical is also supported. Default: 85%%.")
    parser.add_argument("--upload_speed",
                        default="",
                        help="Requested upload speed used in test. Percentage of theoretical is also supported. Default: 0")
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

    CV_Test = HuntTest(lf_host=args.mgr,
                       lf_port=args.port,
                       lf_user=args.lf_user,
                       lf_password=args.lf_password,
                       instance_name=args.instance_name,
                       config_name=args.config_name,
                       upstream=args.upstream,
                       pull_report=args.pull_report,
                       local_lf_report_dir=args.local_lf_report_dir,
                       load_old_cfg=args.load_old_cfg,
                       download_speed=args.download_speed,
                       upload_speed=args.upload_speed,
                       duration=args.duration,
                       dut=args.dut,
                       station=args.station,
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
        logger.info("lf_hunt_test generated kpi.csv")
    else:
        logger.error('''\
        The test has finished but did not complete successfully,
        and no KPI.csv file could be generated. Possible causes
        could be displayed by the GUI CV test, a station could
        have the wrong SSID, passphrase or attempting to connect
        to the wrong BSSID. Please check error messages outputted
        earlier by this script, or check for exceptions in journalctl.
        ''')
        exit(1)

    if CV_Test.passes():
        CV_Test.exit_success()
    else:
        CV_Test.exit_fail()


if __name__ == "__main__":
    main()
