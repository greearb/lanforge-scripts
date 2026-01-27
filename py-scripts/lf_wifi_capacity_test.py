#!/usr/bin/env python3
"""
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

            # Run 5 minute second 1 Gbps DL rate TCP IPv4 traffic-based test with
            # pre-existing and pre-configured stations 'sta0000' and 'sta0001'
            # together
                ./lf_wifi_capacity_test.py \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --protocol      TCP \
                    --duration      5m \
                    --batch_size    2

            # Run test using values and options as defined in pre-existing config
            # Can use additional options like '--duration', '--batch_size', etc.
            # to override those in config
                ./lf_wifi_capacity_test.py \
                    --pull_report   \
                    --config_name   existing_wct_config

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional,  KPI Generation,  Report Generation

STATUS:     Functional

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc.

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
                 protocol="UDP-IPv4",
                 duration="5000",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_rate="10Mbps",
                 download_rate="1Gbps",
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
                 local_lf_report_dir="",
                 sta_list="",
                 verbosity="5",
                 force: bool = False,
                 **kwargs):
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
        self.station_profile = self.new_station_profile()
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "WiFi Capacity"
        self.batch_size = batch_size
        self.loop_iter = loop_iter
        self.protocol = protocol
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
        elif self.create_stations and self.stations_list is not None:
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

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = []

        if self.upstream != "":
            eid = LFUtils.name_to_eid(self.upstream)
            port = "%i.%i.%s" % (eid[0], eid[1], eid[2])

            port_list = [port]
            if self.stations != "" or self.stations_list != []:
                stas = None
                if self.stations:
                    stas = self.stations.split(",")
                elif self.stations_list:
                    stas = self.stations_list
                for s in stas:
                    port_list.append(s)
            else:
                stas = self.station_map()  # See realm
                for eid in stas.keys():
                    port_list.append(eid)
            logger.info(f"Selected Port list: {port_list}")

            idx = 0
            for eid in port_list:
                add_port = "sel_port-" + str(idx) + ": " + eid
                self.create_test_config(self.config_name, "Wifi-Capacity-", add_port)
                idx += 1
        if self.batch_size != "":
            cfg_options.append("batch_size: " + self.batch_size)
        if self.loop_iter != "":
            cfg_options.append("loop_iter: " + self.loop_iter)
        if self.protocol != "":
            cfg_options.append("protocol: " + str(self.protocol))
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

        cfg_options.append("save_csv: 1")

        self.apply_cfg_options(cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        blob_test = "Wifi-Capacity-"

        # We deleted the scenario earlier, now re-build new one line at a time.
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

        self.create_and_run_test(lf_host=self.lfclient_host,
                                 cv_cmds=cv_cmds,
                                 **vars(self))

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name


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

            # Run 5 minute second 1 Gbps DL rate TCP IPv4 traffic-based test with
            # pre-existing and pre-configured stations 'sta0000' and 'sta0001'
            # together
                ./lf_wifi_capacity_test.py \
                    --pull_report   \
                    --upstream      1.1.eth1 \
                    --stations      1.1.sta0000,1.1.sta0001 \
                    --protocol      TCP \
                    --duration      5m \
                    --batch_size    2

            # Run test using values and options as defined in pre-existing config
            # Can use additional options like '--duration', '--batch_size', etc.
            # to override those in config
                ./lf_wifi_capacity_test.py \
                    --pull_report   \
                    --config_name   existing_wct_config

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional,  KPI Generation,  Report Generation

STATUS:     Functional

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc.

INCLUDE_IN_README:
            False
               """)

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("-u", "--upstream", type=str, default="",
                        help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("-b", "--batch_size", type=str, default="",
                        help="station increment ex. 1,2,3")
    parser.add_argument("-l", "--loop_iter", type=str, default="",
                        help="Loop iteration ex. 1")
    parser.add_argument("-p", "--protocol", type=str, default="",
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("-d", "--duration", type=str, default="",
                        help="duration in ms. ex. 5000")
    parser.add_argument("--verbosity", default="5", help="Specify verbosity of the report values 1 - 11 default 5")
    parser.add_argument("--download_rate", type=str, default="1Gbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 1Gbps")
    parser.add_argument("--upload_rate", type=str, default="10Mbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--sort", type=str, default="interleave",
                        help="Select station sorting behaviour:  none | interleave | linear  Default is interleave.")
    parser.add_argument("-s", "--stations", type=str, default="",
                        help="If specified, these stations will be used.  If not specified, all available stations will be selected.  Example: 1.1.sta001,1.1.wlan0,...")
    parser.add_argument("-cs", "--create_stations", default=False, action='store_true',
                        help="create stations in lanforge (by default: False)")
    parser.add_argument("-radio", "--radio", default="wiphy0",
                        help="create stations in lanforge at this radio (by default: wiphy0)")
    parser.add_argument("-ssid", "--ssid", default="",
                        help="ssid name")
    parser.add_argument("-security", "--security", default="open",
                        help="ssid Security type")
    parser.add_argument("-paswd", "--paswd", "-passwd", "--passwd", default="[BLANK]",
                        help="ssid Password")
    parser.add_argument("--report_dir", default="")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--graph_groups", help="File to save graph groups to", default=None)
    parser.add_argument("--local_lf_report_dir", help="--local_lf_report_dir <where to pull reports to>  default '' put where dataplane script run from", default="")
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument("--num_stations", help="Specify the number of stations need to be create.", type=int,
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
                        help='Show loggingout without the trailing file name and line')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    cv_base_adjust_parser(args)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
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

    # add addtional configuration to raw_line
    if (args.per_station_upload_rate):
        if "ul_rate_sel: Per-Station Upload Rate:" not in args.raw_line:
            args.raw_line.append("ul_rate_sel: Per-Station Upload Rate")

    if (args.per_station_download_rate):
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
