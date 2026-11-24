#!/usr/bin/env python3
"""
NAME:       lf_wifi_capacity_test.py

PURPOSE:    This script runs LANforge GUI-based Wi-Fi Capacity test.

NOTES:      Upon successful termination, the test PDF and HTML reports are saved.
            The report is optionally copied to the current directory on the executing system
            when the '--pull_report' option is specified.

EXAMPLE:    # Run 60 second default DL/UL-rate UDP IPv4 traffic-based test with
            # pre-existing and pre-configured station 'sta0000'
            #
            # Report is copied to current directory on executing system given
            # the '--pull_report' option from remote LANforge 192.168.1.101
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000 \
                    --protocol      UDP \
                    --duration      60s

            # Run 5 minute 1 Gbps DL rate TCP IPv4 traffic-based test with
            # pre-existing and pre-configured stations 'sta0000' and 'sta0001'
            # together
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --protocol      TCP \
                    --duration      5m \
                    --batch_size    2

            # Run test using values and options as defined in pre-existing config
            # Additional options like '--duration', '--batch_size', etc. can be used
            # to override values in the saved config
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --config_name   existing_wct_config \
                    --load_old_cfg  \
                    --batch_size    1,4,8

            # Create 10 stations (sta1000 - sta1009) on radio wiphy0 that connect to a
            # WPA2 network, then run the test on them with 1.1.eth1 as upstream port
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --create_stations \
                    --radio         wiphy0 \
                    --start_id      1000 \
                    --num_stations  10 \
                    --ssid          test_ssid \
                    --security      wpa2 \
                    --paswd         test_password

            # Create stations with custom names that connect to an OWE network
            # (no password needed for open or owe security), then run the test on them
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --create_stations \
                    --radio         wiphy0 \
                    --stations      1.1.sta1010,1.1.sta2020 \
                    --ssid          test_owe_ssid \
                    --security      owe

            # Run test on multiple stations and report individual station upload and download rates
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --per_station_upload_rate \
                    --per_station_download_rate

            # Run test on multiple stations, adding 2 stations in each iteration
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001,1.1.sta0002,1.1.sta0003,1.1.sta0004,1.1.sta0005 \
                    --batch_size    2

            # Run test and save the reports in a specific directory on the executing system
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --local_lf_report_dir /home/user/lf_reports

            # Run test with custom download / upload rates
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --download_rate 100Mbps \
                    --upload_rate   1Mbps

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional,  KPI Generation,  Report Generation

STATUS:     Functional

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright (C) 2020-2026 Candela Technologies Inc.

INCLUDE_IN_README:
            False
"""
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
cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


class WiFiCapacityTest(cv_test):
    def __init__(self,
                 lfclient_host="localhost",
                 lf_port=8080,
                 ssh_port=22,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="wct_instance",
                 config_name="wifi_config",
                 upstream="eth1",
                 batch_size="1",
                 loop_iter="1",
                 traffic_type="UDP-IPv4",
                 duration="5000",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_rate="",
                 download_rate="",
                 sort="interleave",
                 stations="",
                 create_stations=False,
                 radio="wiphy0",
                 security="open",
                 paswd="[BLANK]",
                 ssid="",
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 report_dir="",
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 payload_size="",
                 sock_buffer_size="",
                 local_lf_report_dir="",
                 sta_list=None,
                 verbosity="5",
                 force: bool = False,
                 **kwargs):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        if sta_list is None:
            sta_list = []
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
        self.station_profile = self.new_station_profile()
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "WiFi Capacity"
        self.batch_size = batch_size
        self.loop_iter = loop_iter
        self.traffic_type = traffic_type
        self.duration = duration
        self.upload_rate = upload_rate
        self.download_rate = download_rate
        self.upstream = upstream
        self.sort = sort
        self.stations = stations
        self.create_stations = create_stations
        self.security = security
        self.ssid = ssid
        self.paswd = paswd
        self.ssh_port = ssh_port
        self.radio = radio
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.report_dir = report_dir
        self.graph_groups = graph_groups
        self.test_rig = test_rig
        self.test_tag = test_tag
        self.payload_size = payload_size
        self.sock_buffer_size = sock_buffer_size
        self.local_lf_report_dir = local_lf_report_dir
        self.stations_list = sta_list
        self.verbosity = verbosity
        self.force = force

    def setup(self):
        if self.create_stations and self.stations != "":
            sta_names = self.stations.split(",")
            self.station_profile.cleanup(sta_names)
            self.station_profile.use_security(self.security, self.ssid, self.paswd)
            self.station_profile.create(radio=self.radio, sta_names_=sta_names, debug=self.debug)
            self.station_profile.admin_up()
            self.wait_for_ip(station_list=sta_names)
            logger.info("Stations created and got the ips...")
        elif self.create_stations and self.stations_list:
            sta_names = self.stations_list
            self.station_profile.cleanup(sta_names)
            self.station_profile.use_security(self.security, self.ssid, self.paswd)
            self.station_profile.create(radio=self.radio, sta_names_=sta_names, debug=self.debug)
            self.station_profile.admin_up()
            self.wait_for_ip(station_list=sta_names)
            logger.info("Stations created and got the ips...")

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        blob_test = "Wifi-Capacity-"

        if not self.load_old_cfg:
            self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name
            self.show_text_blob(None, None, False)
            if self.download_rate == "":
                self.download_rate = "1Gbps"
            if self.upload_rate == "":
                self.upload_rate = "10Mbps"

        # Test related settings
        cfg_options = []
        if self.upstream != "":
            eid = LFUtils.name_to_eid(self.upstream)
            port = "%i.%i.%s" % (eid[0], eid[1], eid[2])
            port_list = [port]
            if self.stations or self.stations_list:
                stas = None
                if self.stations:
                    stas = self.stations.split(",")
                elif self.stations_list:
                    stas = self.stations_list
                for s in stas:
                    port_list.append(s)
            else:
                stas = self.station_map()
                for eid in stas.keys():
                    port_list.append(eid)
            logger.info(f"Selected Port list: {port_list}")

            idx = 0
            for eid in port_list:
                add_port = "sel_port-" + str(idx) + ": " + eid
                self.create_test_config(self.config_name, blob_test, add_port)
                idx += 1
        if self.batch_size != "":
            cfg_options.append("batch_size: " + self.batch_size)
        if self.loop_iter != "":
            cfg_options.append("loop_iter: " + self.loop_iter)
        if self.traffic_type != "":
            cfg_options.append("protocol: " + str(self.traffic_type))
        if self.duration != "":
            cfg_options.append("duration: " + self.duration)
        if self.upload_rate != "":
            cfg_options.append("ul_rate: " + self.upload_rate)
        if self.download_rate != "":
            cfg_options.append("dl_rate: " + self.download_rate)
        if self.test_rig != "":
            cfg_options.append("test_rig: " + self.test_rig)
        if self.test_tag != "":
            cfg_options.append("test_tag: " + self.test_tag)
        if self.payload_size != "":
            cfg_options.append("pdu_sz: " + self.payload_size)
        if self.sock_buffer_size != "":
            cfg_options.append("sock_buffer: " + self.sock_buffer_size)

        if not self.load_old_cfg:
            cfg_options.append("save_csv: 1")

        self.apply_cfg_options(cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        if cfg_options:
            self.build_cfg(self.config_name, blob_test, cfg_options)

        cv_cmds = []

        cmd = "cv set '%s' 'VERBOSITY' '%s'" % (self.instance_name, self.verbosity)
        cv_cmds.append(cmd)

        if self.sort == 'linear':
            cmd = "cv click '%s' 'Linear Sort'" % self.instance_name
            cv_cmds.append(cmd)
        if self.sort == 'interleave':
            cmd = "cv click '%s' 'Interleave Sort'" % self.instance_name
            cv_cmds.append(cmd)

        self.create_and_run_test(load_old_cfg=self.load_old_cfg,
                                 test_name=self.test_name,
                                 instance_name=self.instance_name,
                                 config_name=self.config_name,
                                 sets=self.sets,
                                 pull_report=self.pull_report,
                                 lf_host=self.lfclient_host,
                                 lf_user=self.lf_user,
                                 lf_password=self.lf_password,
                                 cv_cmds=cv_cmds,
                                 ssh_port=self.ssh_port,
                                 local_lf_report_dir=self.local_lf_report_dir,
                                 graph_groups_file=self.graph_groups)

        if not self.load_old_cfg:
            self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name


def validate_args(args):
    if args.create_stations:
        if not args.num_stations and not args.stations:
            logger.error("Either mention names to stations to be created(--stations) or number of stations to be created(--num_stations). [Same precedence order]")
            exit(1)
        if not args.ssid:
            logger.error("Requires ssid to create station, mention with --ssid")
            exit(1)
    if args.ssid:
        if not args.security:
            logger.error("Requires security to connect to wifi, mention with --security")
            exit(1)
    if args.security.lower() not in ('open', 'owe'):
        if not args.paswd:
            logger.error("Requires password to connect to wifi whose security is not open/owe, mention with --password")
            exit(1)


def main():
    help_summary = "The Candela WiFi Capacity test is designed to measure performance of an " \
                   "Access Point when handling different amounts of WiFi Stations. " \
                   "The test allows the user to increase the number of stations in user defined " \
                   "steps for each test iteration and measure the per station and the overall " \
                   "throughput for each trial. Along with throughput other measurements made are " \
                   "client connection times, Fairness, % packet loss, DHCP times and more. " \
                   "The expected behavior is for the AP to be able to handle several stations " \
                   "(within the limitations of the AP specs) and make sure all stations get " \
                   "a fair amount of airtime both in the upstream and downstream. " \
                   "An AP that scales well will not show a significant over-all throughput " \
                   "decrease as more stations are added."

    parser = argparse.ArgumentParser(
        prog="lf_wifi_capacity_test.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description=r"""
NAME:       lf_wifi_capacity_test.py

PURPOSE:    This script runs LANforge GUI-based WiFi Capacity test.

NOTES:      Upon successful termination, the test PDF and HTML reports are saved.
            The report is optionally copied to the current directory on the executing system
            when the '--pull_report' option is specified.

EXAMPLE:    # Run 60 second default DL/UL-rate UDP IPv4 traffic-based test with
            # pre-existing and pre-configured station 'sta0000'
            #
            # Report is copied to current directory on executing system given
            # the '--pull_report' option from remote LANforge 192.168.1.101
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000 \
                    --protocol      UDP \
                    --duration      60s

            # Run 5 minute 1 Gbps DL rate TCP IPv4 traffic-based test with
            # pre-existing and pre-configured stations 'sta0000' and 'sta0001'
            # together
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --protocol      TCP \
                    --duration      5m \
                    --batch_size    2

            # Run test using values and options as defined in pre-existing config
            # Additional options like '--duration', '--batch_size', etc. can be used
            # to override values in the saved config
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --config_name   existing_wct_config \
                    --load_old_cfg  \
                    --batch_size    1,4,8

            # Create 10 stations (sta1000 - sta1009) on radio wiphy0 that connect to a
            # WPA2 network, then run the test on them with 1.1.eth1 as upstream port
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --create_stations \
                    --radio         wiphy0 \
                    --start_id      1000 \
                    --num_stations  10 \
                    --ssid          test_ssid \
                    --security      wpa2 \
                    --paswd         test_password

            # Create stations with custom names that connect to an OWE network
            # (no password needed for open or owe security), then run the test on them
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --create_stations \
                    --radio         wiphy0 \
                    --stations      1.1.sta1010,1.1.sta2020 \
                    --ssid          test_owe_ssid \
                    --security      owe

            # Run test on multiple stations and report individual station upload and download rates
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --per_station_upload_rate \
                    --per_station_download_rate

            # Run test on multiple stations, adding 2 stations in each iteration
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001,1.1.sta0002,1.1.sta0003,1.1.sta0004,1.1.sta0005 \
                    --batch_size    2

            # Run test and save the reports in a specific directory on the executing system
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --local_lf_report_dir /home/user/lf_reports

            # Run test with custom download / upload rates
                ./lf_wifi_capacity_test.py \
                    --mgr           192.168.1.101 \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --download_rate 100Mbps \
                    --upload_rate   1Mbps

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional,  KPI Generation,  Report Generation

STATUS:     Functional

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright (C) 2020-2026 Candela Technologies Inc.

INCLUDE_IN_README:
            False
               """)

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("-u", "--upstream", "--upstream_port", dest="upstream", type=str, default="",
                        help="Upstream port used in the test, e.g. 1.1.eth2. This is the LANforge (non-station) port\n"
                             "connected to the AP under test, through which traffic is sent to and received from the AP.\n"
                             "Format: <shelf>.<resource>.<port>\n"
                             "If not set, the port selection already in the test config is used (e.g. with --load_old_cfg).")
    parser.add_argument("-b", "--batch_size", type=str, default="",
                        help="Number of stations to add per iteration, or a comma separated list, e.g. 1,4,8.\n"
                             "For example, with 10 stations and a batch size of 2, the test runs 5 iterations,\n"
                             "adding 2 stations in each iteration.\n"
                             "If not set, the value from the test config is used (the saved value with --load_old_cfg).")
    parser.add_argument("-l", "--loop_iter", type=str, default="",
                        help="Number of times the test is run, e.g. 1.\n"
                             "For example, with 10 stations and a loop iteration of 2, the test runs 2 times\n"
                             "with all 10 stations in each run.\n"
                             "If not set, the value from the test config is used (the saved value with --load_old_cfg).")
    parser.add_argument("-p", "--protocol", "--type", "--types", "--traffic_type", "--traffic_types", dest="traffic_type", type=str, default="",
                        help="Traffic type for the test, e.g. UDP-IPv4, TCP-IPv4. Only one can be selected at a time.\n"
                             "UDP, TCP, TCP&UDP and layer4-7 are available options.\n"
                             "If not set, the value from the test config is used (the saved value with --load_old_cfg).")
    parser.add_argument("-d", "--duration", type=str, default="",
                        help="Duration of each traffic run, in ms or with units, e.g. 5000, 5s, 1m, 2h.\n"
                             "Each iteration runs for this duration.\n"
                             "If not set, the value from the test config is used (the saved value with --load_old_cfg).")
    parser.add_argument("--payload_size", default="", help="Specify payload size for the test")
    parser.add_argument("--sock_buffer_size", default="", help="Specify socket buffer size for the test")
    parser.add_argument("--verbosity", default="5",
                        help="Verbosity of the report, a whole number in the range 1 - 11.\n"
                             "The larger the number, the more verbose. Default: 5")
    parser.add_argument("--download_rate", "--download_speed", "--speed", "--rate", dest="download_rate", type=str, default="",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 1Gbps (with --load_old_cfg, the saved value is kept)")
    parser.add_argument("--upload_rate", "--upload_speed", "--opposite_speed", "--opposite_rate", dest="upload_rate", type=str, default="",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps (with --load_old_cfg, the saved value is kept)")
    parser.add_argument("--sort", type=str, default="interleave",
                        help="Select station sorting behaviour:  none | interleave | linear  Default is interleave.")
    parser.add_argument("-s", "--stations", "--station", dest="stations", type=str, default="",
                        help="If specified, these stations will be used.  If not specified, all available stations will be selected.\n"
                             "Example: 1.1.sta001,1.1.wlan0,...  Format: <shelf>.<resource>.<alias>\n"
                             "Can also be used to specify custom names for the stations created with --create_stations")
    parser.add_argument("-cs", "--create_stations", default=False, action='store_true',
                        help="Create stations in LANforge (by default: False).\n"
                             "If specified, mention either --stations or --num_stations to create stations.\n"
                             "If both are specified, --stations is used.\n"
                             "Also mention --radio, --ssid, --security and --paswd to create stations with these parameters")
    parser.add_argument("-radio", "--radio", default="wiphy0",
                        help="create stations in lanforge at this radio (by default: wiphy0)")
    parser.add_argument("-ssid", "--ssid", default="",
                        help="SSID of the network the created stations connect to. Required if --create_stations is specified")
    parser.add_argument("-security", "--security", default="open",
                        help="WiFi security type: open | owe | wep | wpa | wpa2 | wpa3. Default: open. If not open/owe, also mention --paswd")
    parser.add_argument("-paswd", "--paswd", "-passwd", "--passwd", "--password", "--key", dest="paswd", default="[BLANK]",
                        help="WiFi passphrase/password/key. Default: [BLANK]. Required when --security is not open/owe")
    parser.add_argument("--report_dir", default="",
                        help="Directory name to use for the Chamber View report.")
    parser.add_argument("--scenario", default="",
                        help="Chamber View Scenario name to apply before running the test.")
    parser.add_argument("--graph_groups", help="Path to file to save graph_groups to on local system", default=None)
    parser.add_argument("--local_lf_report_dir", help="--local_lf_report_dir <where to pull reports to>  default '' means put in current working directory.\n"
                        "Requires --pull_report to be set", default="")
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> : Path to logger JSON configuration of logger")
    parser.add_argument("--num_stations", help="Specify the number of stations to be created. Used with --create_stations.\n"
                        "Use --start_id to specify the starting ID of the stations.", type=int,
                        default=None)
    parser.add_argument('--start_id', help='Specify the station starting id \n e.g: --start_id <value> default 0',
                        default=0)
    parser.add_argument("--per_station_upload_rate",
                        default=False, action='store_true', help="will report Per-Station Upload Rate (Default: Total Upload Rate)")
    parser.add_argument("--per_station_download_rate",
                        default=False, action='store_true', help="will report Per-Station Download Rate (Default: Total Download Rate)")
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')
    parser.add_argument('--logger_no_file',
                        default=None,
                        action="store_true",
                        help='Show logging out without the trailing file name and line')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    cv_base_adjust_parser(args)
    validate_args(args)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidency to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    if args.logger_no_file:
        f = '%(created)f %(levelname)-8s %(message)s'
        ff = logging.Formatter(fmt=f)
        for handler in logging.getLogger().handlers:
            handler.setFormatter(ff)

    # getting station list if number of stations provided.
    start_id = 0
    if args.start_id != 0:
        start_id = int(args.start_id)

    num_sta = 1
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_stations_converted = int(args.num_stations)
        num_sta = num_stations_converted
    if args.num_stations:
        station_list = LFUtils.port_name_series(prefix="sta",
                                                start_id=start_id,
                                                end_id=start_id + num_sta - 1,
                                                padding_number=10000,
                                                radio=args.radio)
    else:
        station_list = []

    # add additional configuration to raw_line
    if args.per_station_upload_rate:
        if "ul_rate_sel: Per-Station Upload Rate:" not in args.raw_line:
            args.raw_line.append("ul_rate_sel: Per-Station Upload Rate")

    if args.per_station_download_rate:
        if "dl_rate_sel: Per-Station Download Rate:" not in args.raw_line:
            args.raw_line.append("dl_rate_sel: Per-Station Download Rate")

    WFC_Test = WiFiCapacityTest(lfclient_host=args.mgr,
                                lf_port=args.port,
                                enables=args.enable,
                                disables=args.disable,
                                raw_lines=args.raw_line,
                                sets=args.set,
                                sta_list=station_list,
                                **vars(args))
    WFC_Test.setup()
    WFC_Test.run()

    if WFC_Test.kpi_results_present():
        logger.info("lf_wifi_capacity_test generated kpi.csv")
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


if __name__ == "__main__":
    main()
