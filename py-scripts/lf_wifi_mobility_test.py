#!/usr/bin/env python3
"""
NAME: lf_wifi_mobility_test.py

PURPOSE: The Candela Roam test uses the forced roam method to create and roam hundreds of WiFi stations between two
or more APs with the same SSID on the same channel or different channels. The user can run thousands of roams over
long durations and the test measures roaming delay for each roam, station connection times, network down time,
packet loss etc.. The user can run this test using different security methods and compare the roaming performance.
The expected behavior is the roaming delay should be 50ms or less for all various kinds of fast roaming methods to
avoid any form of service interruption to real-time delay sensitive applications

EXAMPLE:
example 1:
 python3 lf_wifi_mobility.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge
 --bssid_list "90:3c:b3:9d:69:3e,34:EF:B6:AF:49:08" --stations "1.1.sta0000"

   --pull_report == If specified, this will pull reports from lanforge to your code directory,
                    from where you are running this code

Suggested: To have a scenario already built.

SCRIPT_CLASSIFICATION :  Test
SCRIPT_CATEGORIES:   Monitoring, Functional, Report Generation.

STATUS: BETA RELEASE

VERIFIED_ON:
Working date - 19/02/2024
Build version - 5.4.7
kernel version -  6.7.3+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False



Example of raw text config for WiFi Mobility, to show other possible options:

sel_port-0: 1.1.sta0000
sel_port-1: 1.1.sta0001
show_events: 1
show_log: 0
log_stdout: 0
port_sorting: 0
kpi_id: WiFi Mobility
bg: 0xE0ECF8
dut_info_override:
test_rig:
test_tag:
show_scan: 1
auto_helper: 1
allow_11w: 0
skip_ac: 0
skip_ax: 0
skip_2: 0
skip_6: 1
skip_5: 0
skip_5b: 1
skip_dual: 0
skip_tri: 1
default_sleep: 250
auto_verify: 30000
max_rpt_time: 500
skip_roam_self: 1
loop_check: 1
clear_on_start: 0
ap_editor0: do_cli scan 1 1 sta1 NA 'trigger freq 5180'
ap_editor1: sleep 2.0
ap_editor2: roam 1 sta1 34:ef:b6:af:49:07
ap_editor3: sleep 10.0
ap_editor4: do_cli scan 1 1 sta1 NA 'trigger freq 5180'
ap_editor5: sleep 2.0
ap_editor6: roam 1 sta1 90:3c:b3:9d:69:2e
ap_editor7: sleep 10.0
bss_query_reason: 16
url: https://candelatech.com
beacon_req_ie: 51000000000002ffffffffffff
sta_addrs_ap: 04:f0:21:c3:b4:cc 1.1.12 sta0000
sta_ports_sta: 1.1.sta0000
ap_addrs_sta: 00:00:c1:01:88:15 DUT-bssid1: 0000c1018812
ap_addrs_ap: 00:00:c1:01:88:15 DUT-bssid1: 0000c1018812
use_civic: 0
use_lci: 0
gen_sleep_interval: 10000
gen_scan_sleep_interval: 2000
gen_scan_freqs: 5180
gen_ds: 0
gen_aps0: # Queried via RRM
gen_aps1: 90:3c:b3:9d:69:2e
gen_aps2: 34:EF:B6:AF:49:07
run_traffic: 0
upstream_port: 1.1.upstream0
traffic_type: UDP
dl_rate: 10000000
ul_rate: 0

"""
import random
import sys
import os
import importlib
import argparse
import time
import logging

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test
cv_test_reports = importlib.import_module("py-json.cv_test_reports")
lf_report = cv_test_reports.lanforge_reports
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


class WifiMobility(cv_test):
    def __init__(self,
                 lfclient_host="localhost",
                 lf_port=8080,
                 ssh_port=22,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 blob_test="WiFi-Mobility-",
                 instance_name="roam-inst-0",
                 config_name="roam_test_cfg",
                 pull_report=True,
                 load_old_cfg=False,
                 raw_lines=None,
                 raw_lines_file="",
                 enables=None,
                 disables=None,
                 sets=None,
                 cfg_options=None,
                 sort="interleave",
                 stations="1.1.sta0000",
                 bssid_list=None,
                 gen_scan_freqs=None,
                 gen_sleep_interval="10000",
                 gen_scan_sleep_interval="2000",
                 gen_ds=0,
                 duration="60000",
                 default_sleep="250",
                 auto_verify="30000",
                 max_rpt_time='500',
                 skip_roam_self='1',
                 loop_check='1',
                 clear_on_start='1',
                 show_events='1',
                 report_dir="",
                 graph_groups=None,
                 test_rig="Testbed-01",
                 test_tag="",
                 local_lf_report_dir="",
                 verbosity="5",
                 run_traffic=False,
                 upstream_port="",
                 traffic_type="UDP",
                 dl_rate="10000000",
                 ul_rate="0",
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []

        self.lfclient_host = lfclient_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.ssh_port = ssh_port
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.blob_test = blob_test
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "Roam Test"
        self.stations = stations
        self.bssid_list = bssid_list
        self.gen_scan_freqs = gen_scan_freqs
        self.gen_sleep_interval = gen_sleep_interval
        self.gen_scan_sleep_interval = gen_scan_sleep_interval
        self.gen_ds = gen_ds
        self.sort = sort
        self.duration = duration
        self.default_sleep = default_sleep
        self.auto_verify = auto_verify
        self.max_rpt_time = max_rpt_time
        self.skip_roam_self = skip_roam_self
        self.loop_check = loop_check
        self.clear_on_start = clear_on_start
        self.show_events = show_events
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.enables = enables
        self.disables = disables
        self.cfg_options = cfg_options
        self.report_dir = report_dir
        self.graph_groups = graph_groups
        self.test_rig = test_rig
        self.test_tag = test_tag
        self.local_lf_report_dir = local_lf_report_dir
        self.verbosity = verbosity
        self.run_traffic = run_traffic
        self.upstream_port = upstream_port
        self.traffic_type = traffic_type
        self.dl_rate = dl_rate
        self.ul_rate = ul_rate

    def create_scenario(self, scenario_name="Automation", raw_line=""):
        self.pass_raw_lines_to_cv(scenario_name=scenario_name, Rawline=raw_line)  # creates a dummy scenario

    def clean_cv_scenario(self, cv_type="Network-Connectivity", scenario_name=None):
        self.rm_cv_text_blob(cv_type, scenario_name)

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()
        self.rm_text_blob(self.config_name, "WiFi-Mobility-")  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        if self.cfg_options is None:
            self.cfg_options = []

        port_list = []
        if self.stations != "":
            stas = None
            if self.stations:
                stas = self.stations.split(",")
            for s in stas:
                port_list.append(s)
        else:
            stas = self.station_map()  # See realm
            for eid in stas.keys():
                port_list.append(eid)
        logger.info(f"Selected Port list: {port_list}")

        idx = 0
        for eid in port_list:
            self.cfg_options.append("sel_port-" + str(idx) + ": " + str(eid))
            idx += 1

        if self.bssid_list is not None:
            bssid_list = self.bssid_list.split(",")
            for i, v in enumerate(bssid_list, 0):
                # For example:
                #   gen_aps0: 04:42:1a:51:49:90
                #   gen_aps1: 04:42:1a:51:49:94
                self.cfg_options.append("gen_aps" + str(i) + ": " + str(v))

        # TODO: Scan sleep interval
        if self.gen_scan_freqs:
            # For example:
            #   gen_scan_freqs: 2412 5180
            gen_scan_freqs = self.gen_scan_freqs.split(",")
            gen_scan_freqs = "gen_scan_freqs: " + " ".join(gen_scan_freqs)
            self.cfg_options.append(gen_scan_freqs)

        if self.gen_sleep_interval != "":
            self.cfg_options.append("gen_sleep_interval: " + str(self.gen_sleep_interval))
        if self.gen_scan_sleep_interval != "":
            self.cfg_options.append("gen_scan_sleep_interval: " + str(self.gen_scan_sleep_interval))
        if self.gen_ds != 0:
            self.cfg_options.append("gen_ds: " + str(self.gen_ds))
        if self.duration != "":
            self.cfg_options.append("duration: " + str(self.duration))
        if self.default_sleep != "":
            self.cfg_options.append("default_sleep: " + str(self.default_sleep))
        if self.auto_verify != "":
            self.cfg_options.append("auto_verify: " + str(self.auto_verify))
        if self.max_rpt_time != "":
            self.cfg_options.append("max_rpt_time: " + str(self.max_rpt_time))
        if self.skip_roam_self != "":
            self.cfg_options.append("skip_roam_self: " + str(self.skip_roam_self))
        if self.loop_check != "":
            self.cfg_options.append("loop_check: " + str(self.loop_check))
        if self.clear_on_start != "":
            self.cfg_options.append("clear_on_start: " + str(self.clear_on_start))
        if self.test_rig != "":
            self.cfg_options.append("test_rig: " + self.test_rig)
        if self.test_tag != "":
            self.cfg_options.append("test_tag: " + self.test_tag)

        if self.run_traffic:
            self.cfg_options.append("run_traffic: " + str(1))
            self.cfg_options.append("traffic_type: " + str(self.traffic_type))
            self.cfg_options.append("dl_rate: " + str(self.dl_rate))
            self.cfg_options.append("ul_rate: " + str(self.ul_rate))
            self.cfg_options.append("upstream_port: " + str(self.upstream_port))


        # self.apply_cfg_options(self.cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        # blob_test = "WiFi-Mobility-"

        # Build config & set values to pass into test parameters
        self.build_cfg(self.config_name, self.blob_test, self.cfg_options)

        cv_cmds = []

        if not self.bssid_list:
            cmd = "cv click '%s' 'Query Neighbors'" % self.instance_name
            cv_cmds.append(cmd)

        cmd = "cv set '%s' 'VERBOSITY' '%s'" % (self.instance_name, self.verbosity)
        cv_cmds.append(cmd)

        cmd = "cv click '%s' 'Generate Script'" % self.instance_name
        cv_cmds.append(cmd)

        try:
            self.create_and_run_test(self.load_old_cfg, self.test_name, self.instance_name,
                                     self.config_name, self.sets,
                                     self.pull_report, self.lfclient_host, self.lf_user, self.lf_password,
                                     cv_cmds, ssh_port=self.ssh_port, graph_groups_file=self.graph_groups,
                                     local_lf_report_dir=self.local_lf_report_dir)
        except Exception as e:
            logger.error(str(e))
            exit(0)

        self.rm_text_blob(self.config_name, self.blob_test)  # To delete old config with same name


def main():
    help_summary = '''\
         The lf_wifi_mobility_test script is used to Monitor the connection status of all the clients for user specified duration.
         This report shows the connection status of all the clients in the test. This information is very useful
         when running long duration tests with 1000s of WiFi clients connecting across various bands, channels and SSIDs.
         The report shows over time counts of number of clients in scanning, connect and IP address acquired states.
         The report also shows number of clients connected over time per SSID, per Channel, per band and per client type
'''

    parser = argparse.ArgumentParser(
        prog="lf_wifi_mobility_test.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
                    lf_wifi_mobility_test.py
            ''',
        description="""

NAME: lf_wifi_mobility_test.py

PURPOSE: The Candela Roam test uses the forced roam method to create and roam hundreds of WiFi stations between two 
or more APs with the same SSID on the same channel or different channels. The user can run thousands of roams over 
long durations and the test measures roaming delay for each roam, station connection times, network down time, 
packet loss etc.. The user can run this test using different security methods and compare the roaming performance. 
The expected behavior is the roaming delay should be 50ms or less for all various kinds of fast roaming methods to 
avoid any form of service interruption to real-time delay sensitive applications

EXAMPLE:
example 1:
 python3 lf_wifi_mobility.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge
 --bssid_list "90:3c:b3:9d:69:3e,34:EF:B6:AF:49:08" --stations "1.1.sta0000"

   --pull_report == If specified, this will pull reports from lanforge to your code directory,
                    from where you are running this code

Suggested: To have a scenario already built.

SCRIPT_CLASSIFICATION :  Test
SCRIPT_CATEGORIES:   Monitoring,  Functional, Report Generation

STATUS: BETA RELEASE

VERIFIED_ON:
Working date - 7/05/2024
Build version - 5.4.7
kernel version -  6.7.3+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

""")

    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    required.add_argument("-m", "--mgr", type=str, default="localhost",
                          help="address of the LANforge GUI machine (localhost is default)")
    required.add_argument("-p", "--port", type=int, default=8080,
                          help="IP Port the LANforge GUI is listening on (8080 is default)")
    required.add_argument("--lf_user", type=str, default="lanforge",
                          help="LANforge username to pull reports")
    required.add_argument("--lf_password", type=str, default="lanforge",
                          help="LANforge Password to pull reports")
    required.add_argument("-s", "--stations", type=str, default="",
                          help="If specified, these stations will be used.  If not specified, all available stations "
                               "will be selected.  Example: 1.1.sta001,1.1.wlan0,...")
    required.add_argument("--bssid_list", type=str, help="pass the list of bssid's of AP1,AP2,etc.,",
                          default="90:3c:b3:9d:69:2e,34:EF:B6:AF:49:07")
    required.add_argument("-pull_report", "--pull_report", default=True, action='store_true',
                          help="pull reports from lanforge reports directory to current working directory")
    required.add_argument('--help_summary', default=None, action="store_true",
                          help='Show summary of what this script does')
    optional.add_argument("-i", "--instance_name", type=str, default="roam-inst-0",
                          help="Instance name of the ROAM Test Window")
    optional.add_argument('--test_duration', type=str, help='Test Duration (in ms)',
                          default="60000")
    optional.add_argument('--default_sleep', type=str, help='delay to pause between roam commands (in ms)',
                          default="250")
    optional.add_argument('--auto_verify', type=str,
                          help='check the stations to verify that the migration was successful or not (in ms)',
                          default="30000")
    optional.add_argument('--max_rpt_time', type=str,
                          help='Maximum roam time to be set as an upper bound in graphs (in ms)', default="500")
    optional.add_argument('--skip_roam_self', type=str, help='flag to skip roam to current AP', default="1")
    optional.add_argument('--loop_check', type=str, help='flag to run the roaming script in Wifi Mobility in a loop',
                          default="1")
    optional.add_argument('--clear_on_start', type=str, help='flag to clear counter on start', default="0")
    optional.add_argument('--show_events', type=str, help='show LF events in the text Log window', default="1")
    optional.add_argument('--gen_sleep_interval', type=str, help='sleep interval between a roam (in ms)',
                          default="10000")
    optional.add_argument('--gen_scan_sleep_interval', type=str, help='sleep interval after each scan (in ms)',
                          default="2000")
    required.add_argument('--gen_scan_freqs', type=str, help='List of frequencies to scan, eg: 5180,5300 (pass as '
                                                             'per the bssid list sequence provided)', default="5180,2437")
    optional.add_argument('--gen_ds', type=str, help='flag to enable FT-DS roam', default="0")
    optional.add_argument("--local_report_dir",
                          help="--local_report_dir <where to pull reports to>  default is '' , i.e reports will be "
                               "saved in the current location.",
                          default="")
    optional.add_argument("--lf_logger_config_json",
                          help="--lf_logger_config_json <json file> , json configuration of logger")
    optional.add_argument("--graph_groups", help="File to save graph groups to", default=None)
    optional.add_argument("--verbosity", default="5", help="Specify verbosity of the report values 1 - 11 default 5")
    optional.add_argument("-c", "--config_name", type=str, default="roam_test_cfg",
                          help="Config file name")
    optional.add_argument("--raw_lines", action='append', nargs=1, default=[],
                          help="Specify lines of the raw config file.  Example: --raw_line 'test_rig: "
                               "Ferndale-01-Basic'  See example raw text config for possible options.  This is "
                               "catch-all for any options not available to be specified elsewhere.  May be specified "
                               "multiple times.")
    optional.add_argument("--raw_lines_file", default="",
                          help="Specify a file of raw lines to apply.")
    optional.add_argument("--sets", action='append', nargs=2, default=[],
                          help="Specify options to set values based on their label in the GUI. Example: --set 'Basic "
                               "Client Connectivity' 1  May be specified multiple times.")
    optional.add_argument("--test_rig", default="",
                          help="Specify the test rig info for reporting purposes, for instance:  testbed-01")
    optional.add_argument('--log_level', default='info',
                          help='Set logging level: debug | info | warning | error | critical')
    optional.add_argument("--run_traffic", help="Specify the traffic mode to run traffic on", action="store_true")
    optional.add_argument("--upstream_port", default="", help="Specify the upstream port to run traffic on")
    optional.add_argument("--traffic_type", default="UDP", help="Specify the traffic type to run traffic on")
    optional.add_argument("--dl_rate", default=10000000, help="Specify the download rate for traffic")
    optional.add_argument("--ul_rate", default=0, help="Specify the upload rate for traffic")

    args = parser.parse_args()
    print(args)
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidency to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    if args.run_traffic and not args.upstream_port:
        logger.error("'--upstream_port' is required when '--run_traffic' is enabled")
        exit(1)

    wifi_mobility_obj = WifiMobility(lfclient_host=args.mgr,
                                     lf_port=args.port,
                                     lf_user=args.lf_user,
                                     lf_password=args.lf_password,
                                     instance_name=args.instance_name,
                                     config_name=args.config_name,
                                     stations=args.stations,
                                     bssid_list=args.bssid_list,
                                     gen_scan_freqs=args.gen_scan_freqs,
                                     gen_sleep_interval=args.gen_sleep_interval,
                                     gen_scan_sleep_interval=args.gen_scan_sleep_interval,
                                     gen_ds=args.gen_ds,
                                     duration=args.test_duration,
                                     default_sleep=args.default_sleep,
                                     auto_verify=args.auto_verify,
                                     max_rpt_time=args.max_rpt_time,
                                     skip_roam_self=args.skip_roam_self,
                                     loop_check=args.loop_check,
                                     clear_on_start=args.clear_on_start,
                                     show_events=args.show_events,
                                     raw_lines=args.raw_lines,
                                     raw_lines_file=args.raw_lines_file,
                                     pull_report=args.pull_report,
                                     load_old_cfg=False,
                                     sets=args.sets,
                                     graph_groups=args.graph_groups,
                                     test_rig=args.test_rig,
                                     local_lf_report_dir=args.local_report_dir,
                                     verbosity=args.verbosity,
                                     run_traffic=args.run_traffic,
                                     upstream_port=args.upstream_port,
                                     traffic_type=args.traffic_type,
                                     dl_rate=args.dl_rate,
                                     ul_rate=args.ul_rate,
                                     )
    if wifi_mobility_obj.instance_name.endswith('-0'):
        wifi_mobility_obj.instance_name = wifi_mobility_obj.instance_name + str(random.randint(1, 9999))

    wifi_mobility_obj.run()

    if wifi_mobility_obj.get_exists(wifi_mobility_obj.instance_name):
        wifi_mobility_obj.delete_instance(instance_name=wifi_mobility_obj.instance_name)


if __name__ == "__main__":
    main()