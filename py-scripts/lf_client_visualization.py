#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_client_visualization.py

PURPOSE: This client_visualization script is used to Monitor the connection status of all the clients for user specified duration.
         This report shows the connection status of all the clients in the test. This information is very useful
         when running long duration tests with 1000s of WiFi clients connecting across various bands, channels and SSIDs.
         The report shows over time counts of number of clients in scanning, connect and IP address acquired states.
         The report also shows number of clients connected over time per SSID, per Channel, per band and per client type

EXAMPLE:
example 1:
 python3 client_visualization.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge  --test_duration 30s  \
 --time_btw_updates 10s --stations_by_radios --stations_by_Band --stations_by_SSID --stations_by_Bssid --stations_by_Mode \
  --stations_by_Channel --pull_report --live_chart_duration 1h --max_report_data 0 --report_compression_interval 20s


example 2: To delete existing window.
python3 client_visualization.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge  \
--test_duration 30s  --time_btw_updates 10s --stations_by_radios --stations_by_Band --stations_by_SSID --stations_by_Bssid \
--stations_by_Mode --stations_by_Channel --pull_report --delete_existing_instance --live_chart_duration 1h --max_report_data 0 \
--report_compression_interval 20s

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



Example of raw text config for Capacity, to show other possible options:

anonymize_ap: 0
show_events: 0
show_log: 0
log_stdout: 0
port_sorting: 2
kpi_id: Client Visualition
get_csv_cb: 0
auto_save: 1
rpt_path:
rpt_path_make_subdir: 1
bg: 0xE0ECF8
dut_info_override:
dut_info_cmd:
test_rig: Testbed-1
test_tag:
rpt_dir_prefix_textfield:
show_scan: 1
auto_helper: 1
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
multi_cx:
udp_burst: 0
payload_pattern:
sndbuf_tcp:
sndbuf_udp:
rcvbuf_tcp:
rcvbuf_udp:
show_per_loop_totals: 1
clear_ports_too: 0
show_log_scale: 0
realtime_per_port: 0
realtime_per_cx: 0
client_status_duration_msec: 1200000
CliViz_max_samples_combo: 8
CliViz_compression_interval_ms_combo: 0
time_between_updates_msec: 10000
live_chart_duration_msec: 86400000
chart_all_stations: 1
chart_by_radio: 1
chart_by_band: 1
chart_by_ssid: 1
chart_by_bssid: 1
chart_by_mode: 1
chart_by_channel: 1

"""
import sys
import os
import importlib
import argparse
import json
import time
import logging


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test
cv_test_reports = importlib.import_module("py-json.cv_test_reports")
lf_rpt = cv_test_reports.lanforge_reports
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


class Client_Visualization(cv_test):
    def __init__(self,
                 lfclient_host="localhost",
                 lf_port=8080,
                 ssh_port=22,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="Client Visualization",
                 config_name="client_vis_config",
                 duration="500000",
                 pull_report=False,
                 load_old_cfg=False,
                 time_btw_updates="10000",
                 live_chart_duration_msec="86400000",
                 chart_all_stations=False,
                 chart_by_radio=False,
                 chart_by_band=False,
                 chart_by_ssid=False,
                 chart_by_bssid=False,
                 chart_by_mode=False,
                 chart_by_channel=False,
                 CliViz_max_samples_combo="8",
                 CliViz_compression_interval_ms_combo="0",
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 report_dir="",
                 graph_groups=None,
                 test_rig="Testbed-01",
                 local_lf_report_dir="",
                 verbosity="5",
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        self.lfclient_host = lfclient_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.ssh_port = ssh_port
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "Client Visualization"
        self.chart_all_stations = chart_all_stations
        self.chart_by_radio = chart_by_radio
        self.chart_by_band = chart_by_band
        self.chart_by_ssid = chart_by_ssid
        self.chart_by_bssid = chart_by_bssid
        self.chart_by_mode = chart_by_mode
        self.chart_by_channel = chart_by_channel
        self.duration = duration
        self.time_btw_updates = time_btw_updates
        self.live_chart_duration_msec = live_chart_duration_msec
        self.CliViz_max_samples_combo = CliViz_max_samples_combo
        self.CliViz_compression_interval_ms_combo = CliViz_compression_interval_ms_combo
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.report_dir = report_dir
        self.graph_groups = graph_groups
        self.test_rig = test_rig
        self.local_lf_report_dir = local_lf_report_dir
        self.verbosity = verbosity
        self.millisec_conversion()

    def pull_report_from_lanforge(self):  # pulls report from lanforge.
        # check = self.get_report_location(self.instance_name)
        # location = json.dumps(check[0]["LAST"]["response"])
        # print(location,"check1-------")
        location = json.dumps(self.report_name[0]["LAST"]["response"])
        logger.info(location)
        location = location.replace('\"Report Location:::', '')
        location = location.replace('\"', '')

        report = lf_rpt()
        try:
            logger.info("Pulling report to directory: %s from %s@%s/%s" %
                        (self.local_lf_report_dir, self.lf_user, self.lfclient_host, location))
            report.pull_reports(hostname=self.lfclient_host, username=self.lf_user, password=self.lf_password,
                                port=self.ssh_port, report_dir=self.local_lf_report_dir,
                                report_location=location)
            logger.info("Test Completed")
        except Exception as e:
            logger.critical("SCP failed, user %s, password %s, dest %s" % (self.lf_user, self.lf_password, self.lfclient_host))
            raise e  # Exception("Could not find Reports")

    def delete_exixting_window(self):
        self.delete_instance(self.instance_name)  # Deletes existing window of Client Visualization

    def create_scenario(self,scenario_name="Automation", Rawline=""):
        self.pass_raw_lines_to_cv(scenario_name=scenario_name, Rawline=Rawline)  # creates a dummy scenario

    def build_dummy_scenario(self,scenario_name="Automation", Rawline=""):

        # example raw_line "profile_link 1.1 STA-AC 10 'DUT: temp Radio-1' tcp-dl-6m-vi wiphy0,AUTO -1"
        # but passing empty rawline to create dummy scenario.
        self.create_scenario(scenario_name, Rawline)
        self.sync_cv()  # chamberview sync
        time.sleep(2)
        self.apply_cv_scenario(scenario_name)  # Apply scenario
        self.show_text_blob(None, None, False)  # Show changes on GUI
        self.apply_cv_scenario(scenario_name)  # Apply scenario
        self.build_cv_scenario()  # build scenario

    def clean_cv_scenario(self,cv_type="Network-Connectivity",scenario_name=None):
        self.rm_cv_text_blob(cv_type, scenario_name)

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()
        self.rm_text_blob(self.config_name, "Client-Visualization-")  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = []

        self.create_test_config(self.config_name, "Client-Visualization-", "")

        # self.apply_cfg_options(cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        if self.chart_all_stations :
            cfg_options.append("chart_all_stations: " + "1")
        else:
            cfg_options.append("chart_all_stations: " + "0")
        if self.chart_by_radio :
            cfg_options.append("chart_by_radio: " + "1")
        else:
            cfg_options.append("chart_by_radio: " + "0")
        if self.chart_by_band :
            cfg_options.append("chart_by_band: " + "1")
        else:
            cfg_options.append("chart_by_band: " + "0")

        if self.chart_by_ssid :
            cfg_options.append("chart_by_ssid: " + "1")
        else:
            cfg_options.append("chart_by_ssid: " + "0")
        if self.chart_by_bssid :
            cfg_options.append("chart_by_bssid: " + "1")
        else:
            cfg_options.append("chart_by_bssid: " + "0")
        if self.chart_by_mode :
            cfg_options.append("chart_by_mode: " + "1")
        else:
            cfg_options.append("chart_by_mode: " + "0")
        if self.chart_by_channel :
            cfg_options.append("chart_by_channel: " + "1")
        else:
            cfg_options.append("chart_by_channel: " + "0")

        if self.duration != "":
            cfg_options.append("client_status_duration_msec: " + self.duration)

        if self.time_btw_updates != "":
            cfg_options.append("time_between_updates_msec: " + self.time_btw_updates)

        if self.live_chart_duration_msec != "":
            cfg_options.append("live_chart_duration_msec: " + self.live_chart_duration_msec)
        if self.test_rig != "":
            cfg_options.append("test_rig: " + self.test_rig)
        # if self.test_tag != "":
        #     cfg_options.append("test_tag: " + self.test_tag)
        cfg_options.append("CliViz_max_samples_combo: " + self.CliViz_max_samples_combo)
        cfg_options.append("CliViz_compression_interval_ms_combo: " + self.CliViz_compression_interval_ms_combo)
        cfg_options.append("save_csv: 1")
        # cfg_options.append("auto_save: 1")

        blob_test = "Client-Visualization-"

        # We deleted the scenario earlier, now re-build new one line at a time.
        self.build_cfg(self.config_name, blob_test, cfg_options)

        cv_cmds = []

        cmd = "cv set '%s' 'VERBOSITY' '%s'" % (self.instance_name,self.verbosity)
        cv_cmds.append(cmd)
        try:

            self.create_and_run_test(self.load_old_cfg, self.test_name, self.instance_name,
                                     self.config_name, self.sets,
                                     self.pull_report, self.lfclient_host, self.lf_user, self.lf_password,
                                     cv_cmds, ssh_port=self.ssh_port, graph_groups_file=self.graph_groups, local_lf_report_dir=self.local_lf_report_dir)
        except:
            logger.info("There is already an instance of 'Client Visualization' present in GUI. "
                        "To delete the existing window, use --delete_existing_instance")
            logger.info("Before deleting, make sure to save the report of running instance if needed.")
            exit(0)

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name

    def millisec_conversion(self):    # converts required durations to milliseconds
        self.duration = self.convert_to_milliseconds(self.duration)
        self.time_btw_updates = self.convert_to_milliseconds(self.time_btw_updates)
        self.live_chart_duration_msec = self.convert_to_milliseconds(self.live_chart_duration_msec)
        self.CliViz_compression_interval_ms_combo = self.convert_to_milliseconds(self.CliViz_compression_interval_ms_combo)

    @staticmethod
    def convert_to_milliseconds(duration):  # converts given duration to milli seconds, i.e (seconds or minutes or hours) to milli-seconds
        if duration.endswith('s') or duration.endswith('S'):
            return str(int(duration[0:-1]) * 1000)
        elif duration.endswith('m') or duration.endswith('M'):
            return str(int(duration[0:-1]) * 60 * 1000)
        elif duration.endswith('h') or duration.endswith('H'):
            return str(int(duration[0:-1]) * 60 * 60 * 1000)
        elif duration.endswith(''):
            return str(duration)

def main():

    help_summary='''\
         The lf_client_visualization script is used to Monitor the connection status of all the clients for user specified duration.
         This report shows the connection status of all the clients in the test. This information is very useful
         when running long duration tests with 1000s of WiFi clients connecting across various bands, channels and SSIDs.
         The report shows over time counts of number of clients in scanning, connect and IP address acquired states.
         The report also shows number of clients connected over time per SSID, per Channel, per band and per client type
'''

    parser = argparse.ArgumentParser(
        prog="lf_client_visualization.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""

NAME: lf_client_visualization.py

PURPOSE: This client_visualization script is used to Monitor the connection status of all the clients for user specified duration.
         This report shows the connection status of all the clients in the test. This information is very useful
         when running long duration tests with 1000s of WiFi clients connecting across various bands, channels and SSIDs.
         The report shows over time counts of number of clients in scanning, connect and IP address acquired states.
         The report also shows number of clients connected over time per SSID, per Channel, per band and per client type

EXAMPLE:
example 1:
 python3 client_visualization.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge  --test_duration 30s  \
 --time_btw_updates 10s --stations_by_radios --stations_by_Band --stations_by_SSID --stations_by_Bssid --stations_by_Mode \
  --stations_by_Channel --pull_report --live_chart_duration 1h --max_report_data 0 --report_compression_interval 20s


example 2: To delete existing window.
python3 client_visualization.py --mgr 192.168.200.96 --port 8080 --lf_user lanforge --lf_password lanforge  \
--test_duration 30s  --time_btw_updates 10s --stations_by_radios --stations_by_Band --stations_by_SSID --stations_by_Bssid \
--stations_by_Mode --stations_by_Channel --pull_report --delete_existing_instance --live_chart_duration 1h --max_report_data 0 \
--report_compression_interval 20s

   Note: --pull_report == If specified, this will pull reports from lanforge to your code directory,
                    from where you are running this code

Suggested: To have a scenario already built.

SCRIPT_CLASSIFICATION :  Test
SCRIPT_CATEGORIES:   Monitoring,  Functional, Report Generation

STATUS: BETA RELEASE

VERIFIED_ON:
Working date - 19/02/2024
Build version - 5.4.7
kernel version -  6.7.3+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

""")

    parser.add_argument("-m", "--mgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user", type=str, default="lanforge",
                        help="LANforge username to pull reports")
    parser.add_argument("--lf_password", type=str, default="lanforge",
                        help="LANforge Password to pull reports")

    parser.add_argument("-duration", "--test_duration", type=str, default="5m",
                        help="provide the duration in either hours or minutes or seconds,ex: 2h or 30m or 50s")
    parser.add_argument("-live_chart_dur", "--live_chart_duration", type=str, default="24h",
                        help="provide the duration in either hours or minutes or seconds,ex: 24h or 10m or 50s \n"
                             "Charts in the report will be turned into static pictures with this interval,"
                             "This helps balance the Memory")
    parser.add_argument("-time_btw_updates", "--time_btw_updates", type=str, default="10s",
                        help="provide the duration in either hours or minutes or seconds,ex: 1h or 1m or 10s\n"
                             "Station stats will be collected at this interval,"
                             "if test duration is longer than 24 hours then it should be set to 1-minute or longer.")
    parser.add_argument("-max_report_data", "--max_report_data", type=str, default="8",
                        help="Resulting amount of report samples after compression.\n"
                             "A higher sample count gives more graph detail but uses more memory.\n"
                             "A lower sample count uses less memory and is more appropriate for long duration tests.")
    parser.add_argument("-report_compression_interval", "--report_compression_interval", type=str, default="0",
                        help="Time interval to run report compression periodically."
                             "Compression activates when Max Report Data is > 0"
                             "provide the duration in either minutes or seconds,ex:  5m or 10s")

    parser.add_argument("-delete", "--delete_existing_instance", default=False, action='store_true',
                        help="If provided , then the existing instance of Client VIsualization will be deleted (by default: False)")
    parser.add_argument("-pull_report", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")

    parser.add_argument("-stations", "--all_stations", default=True, action='store_true',
                        help="To enable All stations(by default: True)")

    parser.add_argument("-stationsbyRad", "--stations_by_radios", default=False, action='store_true',
                        help="To enable stations_by_radios  (by default: False). i.e stations by radios chart will be included in the report")
    parser.add_argument("-stationsbyBand", "--stations_by_Band", default=False, action='store_true',
                        help="To enable stations_by_Band  (by default: False)  i.e stations by Bands chart will be included in the report")
    parser.add_argument("-stationsbySsid", "--stations_by_SSID", default=False, action='store_true',
                        help="To enable stations_by_SSID  (by default: False)  i.e stations by SSID chart will be included in the report")
    parser.add_argument("-stationsbyBssid", "--stations_by_Bssid", default=False, action='store_true',
                        help="To enable stations_by_Bssid  (by default: False)  i.e stations by BSSIS chart will be included in the report")
    parser.add_argument("-stationsbyMode", "--stations_by_Mode", default=False, action='store_true',
                        help="To enable stations_by_Mode  (by default: False)  i.e stations by Mode chart will be included in the report")
    parser.add_argument("-stationsbyChannel", "--stations_by_Channel", default=False, action='store_true',
                        help="To enable stations_by_Channel  (by default: False)  i.e stations by Channel chart will be included in the report")
    parser.add_argument("--verbosity", default="5", help="Specify verbosity of the report values 1 - 11 default 5, decides the amount of data to be shown in the report.")
    # parser.add_argument("--report_dir", default="",help="By default the report will be saved in the current directory.")
    parser.add_argument("--graph_groups", help="File to save graph groups to", default=None)
    parser.add_argument("--local_report_dir", help="--local_report_dir <where to pull reports to>  default is '' , i.e reports will be saved in the current location.", default="")
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument("-c", "--config_name", type=str, default="cv_dflt_cfg",
                        help="Config file name")
    parser.add_argument("--raw_line", action='append', nargs=1, default=[],
                        help="Specify lines of the raw config file.  Example: --raw_line 'test_rig: Ferndale-01-Basic'  See example raw text config for possible options.  This is catch-all for any options not available to be specified elsewhere.  May be specified multiple times.")
    parser.add_argument("--raw_lines_file", default="",
                        help="Specify a file of raw lines to apply.")
    parser.add_argument("--set", action='append', nargs=2, default=[],
                        help="Specify options to set values based on their label in the GUI. Example: --set 'Basic Client Connectivity' 1  May be specified multiple times.")
    parser.add_argument("--test_rig", default="",
                        help="Specify the test rig info for reporting purposes, for instance:  testbed-01")
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')

    args = parser.parse_args()
    # print(args)
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    Client_Vis = Client_Visualization(lfclient_host=args.mgr,
                                lf_port=args.port,
                                lf_user=args.lf_user,
                                lf_password=args.lf_password,
                                instance_name="Client Visualization",
                                config_name=args.config_name,
                                duration=args.test_duration,
                                pull_report=False,
                                load_old_cfg=False,
                                time_btw_updates=args.time_btw_updates,
                                live_chart_duration_msec=args.live_chart_duration,
                                chart_all_stations=args.all_stations,
                                chart_by_radio=args.stations_by_radios,
                                chart_by_band=args.stations_by_Band,
                                chart_by_ssid=args.stations_by_SSID,
                                chart_by_bssid=args.stations_by_Bssid,
                                chart_by_mode=args.stations_by_Mode,
                                chart_by_channel=args.stations_by_Channel,
                                CliViz_max_samples_combo = args.max_report_data,
                                CliViz_compression_interval_ms_combo = args.report_compression_interval,
                                raw_lines=args.raw_line,
                                raw_lines_file=args.raw_lines_file,
                                sets=args.set,
                                graph_groups=args.graph_groups,
                                test_rig=args.test_rig,
                                local_lf_report_dir=args.local_report_dir,
                                verbosity=args.verbosity
                                )
    if args.delete_existing_instance:
        Client_Vis.delete_exixting_window()

    if not Client_Vis.get_cv_is_built():
        Client_Vis.build_dummy_scenario("dummy_scenario", "")

    Client_Vis.run()

    if not Client_Vis.get_cv_is_built():
        Client_Vis.clean_cv_scenario(cv_type="Network-Connectivity", scenario_name="dummy_scenario")

    if args.pull_report:
        Client_Vis.pull_report_from_lanforge()


if __name__ == "__main__":
    main()
