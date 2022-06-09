#!/usr/bin/env python3
'''
NAME: lf_test_max_association.py

NOTE: Script still in progress. Requires modification to l3_cxprofile.py (ln 227) to alleviate url > 2048 bytes error.

PURPOSE:

This script will provide the following features for the ct521a system:
- create the maximum supported stations per installed radio.
- associate the created stations to their prospective SSID's.
- create sta-to-eth Layer-3 CX for 9.6Kbps bidirectional overnight maximum-client wifi test.

EXAMPLE:
./lf_test_max_association.py --mgr localhost --upstream_port <eth2> --wiphy0_ssid <ssid0> --wiphy1_ssid <ssid1>
    --security <security> --passwd <passwd> --traffic_type <lf_udp>

TODO: add '--upstream_port <eth2>' argument and have the script create sta-to-eth Layer-3 cross-connections
      for the overnight max-client test at 9.6Kbps bidirectional that system builders perform.

'''

import argparse
import sys
import os
import logging
import importlib
from pprint import pformat
import time
import csv

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
removeCX = LFUtils.removeCX
removeEndps = LFUtils.removeEndps
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_radio_info = importlib.import_module("py-scripts.smw_lf_radio_info")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)

OPEN = "open"
WEP = "wep"
WPA = "wpa"
WPA2 = "wpa2"
WPA3 = "wpa3"
MODE_AUTO = 0


class max_associate(Realm):
    def __init__(self, _host, _port, wiphy0_ssid, wiphy1_ssid,
                 passwd="NA",
                 security=OPEN,
                 resource=1,
                 upstream_port="eth1",
                 download_bps=9830,
                 upload_bps=9830,
                 wiphy_info=None,
                 traffic_type=None,
                 name_prefix=None,
                 _test_duration="21600s",
                 monitor_interval='10s',
                 layer3_columns=None,
                 report_file=None,
                 kpi_csv=None,
                 kpi_path=None,
                 output_format=None,
                 port_mgr_columns=None,
                 compared_report=None,
                 outfile=None,
                 debug_=False,
                 _exit_on_fail=False):
        if layer3_columns is None:
            layer3_columns = ['name', 'tx bytes', 'rx bytes', 'tx rate', 'rx rate']
        super().__init__(_host, _port, debug_=debug_, _exit_on_fail=_exit_on_fail)
        self.host = _host
        self.port = _port
        self.debug = debug_
        self.security = security
        self.wiphy0_ssid = wiphy0_ssid
        self.wiphy1_ssid = wiphy1_ssid
        self.password = passwd
        self.resource = resource
        self.upstream_port = upstream_port
        self.download_bps = download_bps
        self.wiphy_info = wiphy_info
        self.upload_bps = upload_bps
        self.traffic_type = traffic_type
        self.name_prefix = name_prefix
        self.test_duration = _test_duration
        self.monitor_interval = monitor_interval
        self.layer3_columns = layer3_columns
        self.report_file = report_file
        self.kpi_csv = kpi_csv
        self.kpi_path = kpi_path
        self.output_format = output_format
        self.port_mgr_columns = port_mgr_columns
        self.compared_report = compared_report
        self.outfile = outfile
        self.epoch_time = int(time.time())

        self.systeminfopath = None
        self.report_path_format = None
        self.report_file_format = None
        self.layer3connections = None
        self.name_prefix = "MA"

        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = self.download_bps
        self.cx_profile.side_b_min_bps = self.upload_bps

        if self.outfile is not None:
            results = self.outfile[:-4]
            results = results + "-results.csv"
            self.csv_results_file = open(results, "w")
            self.csv_results_writer = csv.writer(self.csv_results_file, delimiter=",")

    def get_kpi_results(self):
        # make json call to get kpi results
        endp_list = self.json_get(
            "endp?fields=name,eid,delay,jitter,rx+rate,rx+rate+ll,rx+bytes,rx+drop+%25,rx+pkts+ll",
            debug_=False)
        logger.info("endp_list: {endp_list}".format(endp_list=endp_list))

    def get_csv_name(self):
        logger.info("self.csv_results_file {}".format(self.csv_results_file.name))
        return self.csv_results_file.name

    # Common code to generate timestamp for CSV files.
    def time_stamp(self):
        return time.strftime('%m_%d_%Y_%H_%M_%S', time.localtime(self.epoch_time))

    def format_report_path(self):
        if self.report_file is None:
            # new_file_path = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%M-m-%S-s")).replace(':','-') + '_test_ip_variable_time'
            # create path name
            new_file_path = self.kpi_path
            if os.path.exists('/home/lanforge/report-data'):
                path = os.path.join('/home/lanforge/report-data/', new_file_path)
                os.mkdir(path)
            else:
                logger.info(new_file_path)
                # curr_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # curr_dir_path += '/py-scripts'
                # path = os.path.join(curr_dir_path, new_file_path)
                # os.mkdir(path)
            # systeminfopath = str(path) + '/systeminfo.txt'
            self.systeminfopath = str(new_file_path) + '/systeminfo.txt'

            if self.output_format in ['csv', 'json', 'html', 'hdf', 'stata', 'pickle', 'pdf', 'png', 'parquet',
                                      'xlsx']:
                # self.report_path_format = str(path) + '/data.' + self.output_format
                self.report_path_format = str(new_file_path) + '/data.' + self.output_format
                self.report_file_format = self.output_format
            else:
                logger.info(
                    'Not supporting this report format or cannot find report format provided. Defaulting to csv data file '
                    'output type, naming it data.csv.')
                # report_f = str(path) + '/data.csv'
                self.report_path_format = str(new_file_path) + '/data.csv'
                self.report_file_format = 'csv'
        else:
            self.systeminfopath = str(self.report_file).split('/')[-1]
            self.report_path_format = self.report_file
            if self.output_format is None:
                self.report_file_format = str(self.report_file).split('.')[-1]
            else:
                self.report_file_format = self.output_format

    def layer3_connections(self):
        try:
            self.layer3connections = ','.join([[*x.keys()][0] for x in self.json_get('endp')['endpoint']])
        except ValueError:
            raise ValueError('Try setting the upstream port flag if your device does not have an eth1 port')

        if type(self.layer3_columns) is not list:
            self.layer3_columns = list(self.layer3_columns.split(","))
            # send col names here to file to reformat
        else:
            self.layer3_columns = self.layer3_columns
            # send col names here to file to reformat
        if type(self.port_mgr_columns) is not list:
            self.port_mgr_columns = list(self.port_mgr_columns.split(","))
            # send col names here to file to reformat
        else:
            self.port_mgr_columns = self.port_mgr_columns
            # send col names here to file to reformat
        if self.debug:
            logger.debug("Layer 3 Endp column names are...")
            logger.debug(self.layer3_columns)
            logger.debug("Port Manager column names are...")
            logger.debug(self.port_mgr_columns)

        try:
            self.monitor_interval = Realm.parse_time(self.monitor_interval).total_seconds()
        except ValueError as error:
            logger.critical(error)
            logger.critical(
                "The time string provided for monitor_interval argument is invalid. Please see supported time stamp increments and inputs for monitor_interval in --help. ")
            return ValueError(
                "The time string provided for monitor_interval argument is invalid. Please see supported time stamp increments and inputs for monitor_interval in --help. ")

    # Query all endpoints to generate rx and other stats, returned
    # as an array of objects.
    def get_rx_values(self):
        endp_list = self.json_get(
            "endp?fields=name,eid,delay,jitter,rx+rate,rx+rate+ll,rx+bytes,rx+drop+%25,rx+pkts+ll",
            debug_=True)
        # logger.info("endp_list: {endp_list}".format(endp_list=endp_list))
        endp_rx_drop_map = {}
        endp_rx_map = {}
        endps = []

        total_ul_rate = 0
        total_ul_ll = 0
        total_ul_pkts_ll = 0
        total_dl_rate = 0
        total_dl_ll = 0
        total_dl_pkts_ll = 0

        '''
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e
        print("our_endps {our_endps}".format(our_endps=our_endps))
        '''
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, endp_value in endp_name.items():
                    # if item in our_endps:
                    if True:
                        endps.append(endp_value)
                        logger.debug("endpoint: {item} value:\n".format(item=item))
                        logger.debug(endp_value)

                        logger.info(endps)
                        logger.info(len(endps))  # if this == 528, then use it to solve the avg for 'rx rate' below
                        # logger.info("item {item}".format(item=item))

                        for value_name, value in endp_value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value
                                # logger.info("rx_bytes {value}".format(value=value))
                            if value_name == 'rx rate':
                                endp_rx_map[item] = value
                                logger.info("rx_rate {value}".format(value=value))
                                # This hack breaks for mcast or if someone names endpoints weirdly.
                                # logger.info("item: ", item, " rx-bps: ", value_rx_bps)
                                # info for upload test data
                                logger.info(self.traffic_type)
                                if item.endswith("-A"):
                                    total_ul_rate += int(value)
                                    # logger.info(udp_ul_rate_bps)
                                else:
                                    total_dl_rate += int(value)
                                    # logger.info(udp_dl_rate_bps)

                            if value_name == 'rx rate ll':
                                endp_rx_map[item] = value
                                logger.info("rx_rate_ll {value}".format(value=value))
                            if value_name == 'rx pkts ll':
                                endp_rx_map[item] = value

                                if item.endswith("-A"):
                                    total_ul_pkts_ll += int(value)
                                    # logger.info(total_ul_pkts_ll)
                                if value == '':
                                    value = '0'
                                else:
                                    total_dl_pkts_ll += int(value)
                                    # logger.info(total_dl_pkts_ll)

                            if value_name == 'rx drop %':
                                endp_rx_drop_map[item] = value
                            if value_name == 'rx rate ll':
                                # This hack breaks for mcast or if someone
                                # names endpoints weirdly.
                                if item.endswith("-A"):
                                    total_ul_ll += int(value)
                                else:
                                    total_dl_ll += int(value)

        # logger.debug("total-dl: ", total_dl, " total-ul: ", total_ul, "\n")
        return endp_rx_map, endp_rx_drop_map, endps, total_ul_rate, total_dl_rate, total_dl_ll, total_ul_ll, total_ul_pkts_ll, total_dl_pkts_ll

    def cleanup(self):
        self.cx_profile.cleanup()
        if not self.use_existing_sta:
            self.station_profile.cleanup()
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                               debug=self.debug)

    def build(self):
        # query system radios
        # if radio == wiphy0:
        # query lf_radio_info.get_radio_max_station(wiphy_radio)
        # build station amount that is returned
        # list = self.lf_radio_info.RadioInfo.get_lanforge_radio_information()
        # get_lanforge_radio_information
        all_wiphy_data = self.wiphy_info.get_lanforge_radio_information()
        logger.info(all_wiphy_data)
        wiphy_radio_list = self.wiphy_info.get_radios()
        logger.info(wiphy_radio_list)

        for wiphy_radio in wiphy_radio_list:

            if wiphy_radio == "1." + self.resource + ".wiphy0":
                # TODO: smw
                num_stations = self.wiphy_info.get_max_vifs(wiphy_radio)
                # num_stations = 2
                logger.info(num_stations)
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0,
                                                      end_id_=int(num_stations) - 1,
                                                      padding_number_=10000,
                                                      radio=wiphy_radio)

                logger.info(station_list)
                self.station_profile.lfclient_url = self.lfclient_url
                self.station_profile.ssid = self.wiphy0_ssid
                logger.info(self.password)
                self.station_profile.ssid_pass = self.password
                self.station_profile.security = self.security
                # self.station_profile.number_template_ = self.number_template
                self.station_profile.debug = self.debug
                self.station_profile.use_security(self.security, self.wiphy0_ssid, self.password)
                # self.station_profile.set_number_template(self.number_template)
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

                logger.info("Creating stations")
                self.station_profile.create(radio=wiphy_radio, sta_names_=station_list, debug=self.debug)
                self._pass("PASS: Station build finished")

                self.cx_profile.create(endp_type=self.traffic_type,
                                       side_a=station_list,
                                       side_b=self.upstream_port,
                                       sleep_time=0)

            if wiphy_radio == "1." + self.resource + ".wiphy1":
                # TODO: smw
                start_num_stations = self.wiphy_info.get_max_vifs("1.1.wiphy0")
                # start_num_stations = 2
                end_num_stations = self.wiphy_info.get_max_vifs(wiphy_radio)
                # end_num_stations = 2
                logger.info(num_stations)
                # TODO: make start_id = end_id + 1 of wiphy0 created stations, make dynamic:
                station_list = LFUtils.portNameSeries(prefix_="sta",
                                                      start_id_=int(start_num_stations),
                                                      end_id_=int(end_num_stations) + int(start_num_stations) - 1,
                                                      padding_number_=10000,
                                                      radio=wiphy_radio)

                logger.info(station_list)
                self.station_profile.lfclient_url = self.lfclient_url
                self.station_profile.ssid = self.wiphy1_ssid
                self.station_profile.ssid_pass = self.password
                self.station_profile.security = self.security
                # self.station_profile.number_template_ = self.number_template
                self.station_profile.debug = self.debug
                self.station_profile.use_security(self.security, self.wiphy1_ssid, self.password)
                # self.station_profile.set_number_template(self.number_template)
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

                logger.info("Creating stations")
                self.station_profile.create(radio=wiphy_radio, sta_names_=station_list, debug=self.debug)
                self._pass("PASS: Station build finished")

                self.cx_profile.create(endp_type=self.traffic_type,
                                       side_a=station_list,
                                       side_b=self.upstream_port,
                                       sleep_time=0)

    def start_cxs(self):
        if self.station_profile is None:
            self._fail("Incorrect setup")
        logger.debug(pformat(self.station_profile))
        if self.station_profile.up is None:
            self._fail("Incorrect station profile, missing profile.up")
        if not self.station_profile.up:
            logger.info("Bringing ports up...")
            # logger.info("start() - self.lf_client_url: %s", self.lfclient_url)
            data = {"shelf": 1,
                    "resource": self.resource,
                    "port": "ALL",
                    "probe_flags": 1}
            # logger.info("start() - data1: %s", data)
            self.json_post("/cli-json/nc_show_ports", data)
            # print("start() - ln 252 - self.j")
            self.station_profile.admin_up()
            self.csv_add_column_headers()
            station_names = []
            station_names.extend(self.station_profile.station_names.copy())
            logger.info(station_names)
            LFUtils.waitUntilPortsAdminUp(self.resource, self.lfclient_url, station_names)

        time.sleep(10)
        self.cx_profile.start_cx()

    # guide script during test run & collect data
    def run(self):
        self.start_cxs()
        start_time = time.ctime()
        logger.info("Test Start: %s",  start_time)
        # time.sleep(int(self.test_duration))
        station_names = []
        station_names.extend(self.station_profile.station_names.copy())

        # Retrieve last data file
        compared_rept = None
        if self.compared_report:
            compared_report_format = self.compared_report.split('.')[-1]
            # if compared_report_format not in ['csv', 'json', 'dta', 'pkl','html','xlsx','parquet','h5']:
            if compared_report_format != 'csv':
                logger.critical("Cannot process this file type. Please select a different file and re-run script.")
                raise ValueError("Cannot process this file type. Please select a different file and re-run script.")
            else:
                compared_rept = self.compared_report

        # remove endpoints from layer3connections that do not begin with 'MA' prefix:
        logger.info(self.layer3connections)
        # convert layer3connections to list:
        split_l3_endps = self.layer3connections.split(",")
        # logger.info(split_l3_endps)
        new_l3_endps_list = []

        for item in split_l3_endps:
            if item.startswith('MA'):
                new_l3_endps_list.append(item)
                # logger.info(new_l3_endps_list)
                # convert new_l3_endps_list to str:
                layer3endps = ','.join(str(l3endps) for l3endps in new_l3_endps_list)
                # logger.info(layer3endps)

        logger.info(self.layer3_columns)
        self.cx_profile.monitor(layer3_cols=self.layer3_columns,
                                # sta_list=self.sta_list,
                                sta_list=station_names,
                                port_mgr_cols=self.port_mgr_columns,
                                report_file=self.report_path_format,
                                systeminfopath=self.systeminfopath,
                                duration_sec=self.test_duration,
                                monitor_interval_ms=self.monitor_interval,
                                created_cx=layer3endps,
                                output_format=self.report_file_format,
                                compared_report=compared_rept,
                                script_name='lf_test_max_association',
                                debug=self.debug)

        # fill out data kpi.csv and results reports
        temp_stations_list = []
        temp_stations_list.extend(self.station_profile.station_names.copy())
        total_test = len(self.get_result_list())
        total_pass = len(self.get_passed_result_list())
        endp_rx_map, endp_rx_drop_map, endps, total_ul_rate, total_dl_rate, total_dl_ll, total_ul_ll, total_ul_pkts_ll, total_dl_pkts_ll = self.get_rx_values()
        self.record_kpi_csv(temp_stations_list, total_test, total_pass, total_ul_rate, total_dl_rate, total_ul_pkts_ll, total_dl_pkts_ll, endp_rx_drop_map, endp_rx_map)
        self.record_results(len(temp_stations_list), total_ul_rate, total_dl_rate, total_ul_pkts_ll, total_dl_pkts_ll)

        logger.info(self.report_path_format)
        logger.info(compared_rept)
        logger.info(self.port_mgr_columns)
        logger.info(self.report_file_format)

        logger.info("Leaving existing stations...")
        logger.info("IP Variable Time Test Report Data: {}".format(self.report_path_format))

        self.cx_profile.stop_cx()
        end_time = time.ctime()
        logger.info("Test End: %s",  end_time)

    # builds test data into kpi.csv report
    def record_kpi_csv(
            self,
            sta_list,
            total_test,
            total_pass,
            total_ul_rate,
            total_dl_rate,
            total_ul_pkts_ll,
            total_dl_pkts_ll,
            endp_rx_drop_map,
            endp_rx_map):

        # the short description will allow for more data to show up in one test-tag graph

        sta_list_len = len(sta_list)
        # logger.info(sta_list_len)
        total_ul_dl_rate = total_ul_rate+total_dl_rate

        # logic for Subtest-Pass & Subtest-Fail columns
        subpass_udp_ul = 0
        subpass_udp_dl = 0
        subfail_udp_ul = 1
        subfail_udp_dl = 1
        subpass_pkts_ul = 0
        subpass_pkts_dl = 0
        subfail_pkts_ul = 1
        subfail_pkts_dl = 1

        if total_ul_rate > 0:
            subpass_udp_ul = 1
            subfail_udp_ul = 0
        if total_dl_rate > 0:
            subpass_udp_dl = 1
            subfail_udp_dl = 0
        if total_ul_pkts_ll > 0:
            subpass_pkts_ul = 1
            subfail_pkts_ul = 0
        if total_dl_pkts_ll > 0:
            subpass_pkts_dl = 1
            subfail_pkts_dl = 0

        # logic for pass/fail column
        # total_test & total_pass values from lfcli_base.py
        if total_test == total_pass:
            pass_fail = "PASS"
        else:
            pass_fail = "FAIL"

        # logic for stations that drop > 1% traffic:
        station_drops = []
        drop_value_sum = 0.0
        for endp_drop in endp_rx_drop_map.keys():
            logger.info(endp_rx_drop_map[endp_drop])
            if endp_rx_drop_map[endp_drop] > 1.0:
                drop_value_sum += endp_rx_drop_map[endp_drop]
                station_drops.append(endp_drop)
                total_sta_drops = len(station_drops)
                avg_drop = drop_value_sum / total_sta_drops
                logger.info(avg_drop)
        avg_drop_round = round(avg_drop, 2)

        results_dict = self.kpi_csv.kpi_csv_get_dict_update_time()

        # kpi data for UDP upload traffic
        results_dict['Graph-Group'] = "Total UDP Upload Rate"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_udp_ul
        results_dict['Subtest-Fail'] = subfail_udp_ul
        results_dict['short-description'] = "UDP-UL {upload_bps} bps  {sta_list_len} STA".format(
            upload_bps=self.upload_bps, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(total_ul_rate)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        # kpi data for UDP download traffic
        results_dict['Graph-Group'] = "Total UDP Download Rate"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_udp_dl
        results_dict['Subtest-Fail'] = subfail_udp_dl
        results_dict['short-description'] = "UDP-DL {download_bps} bps  {sta_list_len} STA".format(
            download_bps=self.download_bps, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(total_dl_rate)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        # kpi data for total upload & download traffic rate
        logger.info(endp_rx_drop_map)
        results_dict['Graph-Group'] = "Total UDP-UL/DL Rate"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_udp_ul
        results_dict['Subtest-Fail'] = subfail_udp_ul
        results_dict['short-description'] = "UDP-UL {upload_bps} bps  UDP-DL {download_bps} bps  {sta_list_len} STA".format(
            upload_bps=self.upload_bps, download_bps=self.download_bps, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(total_ul_dl_rate)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        # kpi data for UDP upload packets ll
        results_dict['Graph-Group'] = "Total Transmitted Packet Count"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_pkts_ul
        results_dict['Subtest-Fail'] = subfail_pkts_ul
        results_dict['short-description'] = "UDP-UL {upload_bps} bps  {sta_list_len} STA".format(
            upload_bps=self.upload_bps, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(total_ul_pkts_ll)
        results_dict['Units'] = "pkts"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        # kpi data for UDP download packets ll
        results_dict['Graph-Group'] = "Total Received Packet Count"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_pkts_dl
        results_dict['Subtest-Fail'] = subfail_pkts_dl
        results_dict['short-description'] = "UDP-DL {download_bps} bps  {sta_list_len} STA".format(
            download_bps=self.download_bps, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(total_dl_pkts_ll)
        results_dict['Units'] = "pkts"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        # kpi data for stations drop over 1%
        results_dict['Graph-Group'] = "Avg Traffic Drop"
        results_dict['pass/fail'] = pass_fail
        results_dict['Subtest-Pass'] = subpass_udp_dl
        results_dict['Subtest-Fail'] = subfail_udp_dl
        results_dict['short-description'] = "{total_sta_drops} of {sta_list_len} STA Over 1% Traffic Loss".format(
            total_sta_drops=total_sta_drops, sta_list_len=sta_list_len)
        results_dict['numeric-score'] = "{}".format(avg_drop_round)
        results_dict['Units'] = "percent"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

    # record results for .html & .pdf reports
    def record_results(
            self,
            sta_count,
            udp_dl_rate_bps,
            udp_ul_rate_bps,
            total_ul_pkts_ll,
            total_dl_pkts_ll):

        dl = self.download_bps
        ul = self.upload_bps

        tags = dict()
        tags['requested-ul-bps'] = ul
        tags['requested-dl-bps'] = dl
        tags['station-count'] = sta_count
        # tags['attenuation'] = atten
        tags["script"] = 'lf_test_max_association'

        '''
        # Add user specified tags
        for k in self.user_tags:
            tags[k[0]] = k[1]
        '''

        if self.csv_results_file:
            row = [self.epoch_time, self.time_stamp(), sta_count,
                   ul, ul, dl, dl,
                   udp_ul_rate_bps, udp_dl_rate_bps,
                   (udp_ul_rate_bps + udp_dl_rate_bps),
                   total_ul_pkts_ll, total_dl_pkts_ll,
                   (total_ul_pkts_ll + total_dl_pkts_ll)
                   ]
            '''
            # Add values for any user specified tags
            for k in self.user_tags:
                row.append(k[1])
            '''

            self.csv_results_writer.writerow(row)
            self.csv_results_file.flush()

    def csv_generate_results_column_headers(self):
        csv_rx_headers = [
            'Time epoch',
            'Time',
            'Station-Count',
            'UL-Min-Requested',
            'UL-Max-Requested',
            'DL-Min-Requested',
            'DL-Max-Requested',
            # 'Attenuation',
            'UDP-Upload-bps',
            # 'TCP-Upload-bps',
            'UDP-Download-bps',
            # 'TCP-Download-bps',
            # 'Total-UDP/TCP-Upload-bps',
            # 'Total-UDP/TCP-Download-bps',
            'Total-UDP-UL/DL-bps',
            'UL-Rx-Pkts-ll',
            'DL-Rx-Pkts-ll',
            'Total-UL/DL-Pkts-ll']

        return csv_rx_headers

    # Write initial headers to csv file.
    def csv_add_column_headers(self):
        if self.csv_results_file is not None:
            self.csv_results_writer.writerow(
                self.csv_generate_results_column_headers())
            self.csv_results_file.flush()

    # ~class


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def main():
    parser = argparse.ArgumentParser(
        prog="lf_test_max_association.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
---------------------------
LANforge Unit Test:  Create max stations per wihpy radio - lf_test_max_association.py
---------------------------
Summary:
This script will provide the following features for the ct521a system:
- create the maximum supported stations per installed radio.
- associate the created stations to their prospective SSID's.
- create sta-to-eth Layer-3 CX for 9.6Kbps bidirectional overnight maximum-client wifi test.
---------------------------
CLI Example:
./lf_test_max_association.py --mgr localhost --upstream_port <eth2> --wiphy0_ssid <ssid0> --wiphy1_ssid <ssid1>
    --security <security> --passwd <passwd> --traffic_type <lf_udp> --runtime <8hours>

---------------------------
""")
    parser.add_argument("-m", "--mgr", type=str, help="address of the LANforge GUI machine (localhost is default)",
                        default='localhost')
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp, udp, tcp], type will be '
                                               'adjusted automatically between ipv4 and ipv6 based on use of --ipv6 flag',
                        default="lf_udp")
    parser.add_argument("--port", type=str, help="LANforge Manager port", default='8080')
    parser.add_argument("--wiphy0_ssid", type=str, help="DUT SSID that the wiphy0 stations will associate with.")
    parser.add_argument("--wiphy1_ssid", type=str, help="DUT SSID that the wiphy1 stations will associate with.")
    parser.add_argument("--security", type=str, help="DUT security: openLF, wpa, wpa2, wpa3")
    parser.add_argument("--passwd", type=str, help="DUT PSK password.  Do not set for OPEN auth")
    parser.add_argument("--download_bps", type=int, help="Set the minimum bps value on test endpoint A. Default: 9.6Kbps", default=9830)
    parser.add_argument("--upload_bps", type=int, help="Set the minimum bps value on test endpoint B. Default: 9.6Kbps", default=9830)
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test, default is 8 hours', default="28800s")
    parser.add_argument("--debug", help="enable debugging", action="store_true")
    parser.add_argument('--report_file', help='where you want to store results', default=None)
    parser.add_argument('--output_format', help='choose either csv or xlsx')
    parser.add_argument("--prefix", type=str, help="Station prefix. Default: 'sta'", default='sta')
    parser.add_argument("--resource", type=str, help="LANforge Station resource ID to use, default is 1", default="1")
    parser.add_argument("--upstream_port", type=str, help="LANforge Ethernet port name, default is eth1",
                        default='1.1.eth1')
    parser.add_argument("--sta_mode", type=str,
                        help="LANforge station-mode setting (see add_sta LANforge CLI documentation, default is 0 (auto))",
                        default=0)
    parser.add_argument("--bringup_time", type=int,
                        help="Seconds to wait for stations to associate and aquire IP. Default: 300", default=300)
    parser.add_argument('--debug_log', default=None, help="Specify a file to send debug output to")
    parser.add_argument('--local_lf_report_dir', help='--local_lf_report_dir override the report path, primary use when running test in test suite', default="")
    parser.add_argument('--monitor_interval',
                        help='how frequently do you want your monitor function to take measurements, 35s, 2h',
                        default='10s')
    parser.add_argument('--compared_report', help='report path and file which is wished to be compared with new report',
                        default=None)
    parser.add_argument('--layer3_cols', help='Columns wished to be monitored from layer 3 endpoint tab',
                        default=['name', 'tx bytes', 'rx bytes', 'tx rate', 'rx rate'])
    parser.add_argument('--port_mgr_cols', help='Columns wished to be monitored from port manager tab',
                        default=['alias', 'ap', 'ip', 'parent dev', 'rx-rate'])

    # kpi_csv arguments:
    parser.add_argument(
        "--test_rig",
        default="",
        help="test rig for kpi.csv, testbed that the tests are run on")
    parser.add_argument(
        "--test_tag",
        default="",
        help="test tag for kpi.csv,  test specific information to differenciate the test")
    parser.add_argument(
        "--dut_hw_version",
        default="",
        help="dut hw version for kpi.csv, hardware version of the device under test")
    parser.add_argument(
        "--dut_sw_version",
        default="",
        help="dut sw version for kpi.csv, software version of the device under test")
    parser.add_argument(
        "--dut_model_num",
        default="",
        help="dut model for kpi.csv,  model number / name of the device under test")
    parser.add_argument(
        "--dut_serial_num",
        default="",
        help="dut serial for kpi.csv, serial number / serial number of the device under test")
    parser.add_argument(
        "--test_priority",
        default="",
        help="dut model for kpi.csv,  test-priority is arbitrary number")
    parser.add_argument(
        "--test_id",
        default="L3 Data",
        help="test-id for kpi.csv,  script or test name")
    parser.add_argument(
        '--csv_outfile',
        help="--csv_outfile <Output file for csv data>",
        default="")

    # logging configuration:
    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    # TODO: Try to start with: --radio 'radio==wiphy4,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2':
    parser.add_argument(
        '-r', '--radio',
        action='append',
        nargs=1,
        help=(' --radio'
              ' "radio==<number_of_wiphy stations=<=number of stations>'
              ' ssid==<ssid> ssid_pw==<ssid password> security==<security> '
              ' wifi_settings==True wifi_mode==<wifi_mode>'
              ' enable_flags==<enable_flags> '
              ' reset_port_enable==True reset_port_time_min==<min>s'
              ' reset_port_time_max==<max>s" ')
    )

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    if (args.log_level):
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    if args.debug:
        logger_config.set_level("debug")

    CX_TYPES = ("tcp", "udp", "lf_tcp", "lf_udp")
    if not args.traffic_type or (args.traffic_type not in CX_TYPES):
        logger.error("cx_type needs to be lf_tcp, lf_udp, tcp, or udp, bye")
        exit(1)

    # for kpi.csv generation
    local_lf_report_dir = args.local_lf_report_dir
    test_rig = args.test_rig
    test_tag = args.test_tag
    dut_hw_version = args.dut_hw_version
    dut_sw_version = args.dut_sw_version
    dut_model_num = args.dut_model_num
    dut_serial_num = args.dut_serial_num
    # test_priority = args.test_priority  # this may need to be set per test
    test_id = args.test_id

    if local_lf_report_dir != "":
        report = lf_report.lf_report(
            _path=local_lf_report_dir,
            _results_dir_name="lf_test_max_association",
            _output_html="lf_test_max_association.html",
            _output_pdf="lf_test_max_association.pdf")
    else:
        report = lf_report.lf_report(
            _results_dir_name="lf_test_max_association",
            _output_html="lf_test_max_association.html",
            _output_pdf="lf_test_max_association.pdf")

    kpi_path = report.get_report_path()
    # kpi_filename = "kpi.csv"
    logger.info("kpi_path :{kpi_path}".format(kpi_path=kpi_path))

    kpi_csv = lf_kpi_csv.lf_kpi_csv(
        _kpi_path=kpi_path,
        _kpi_test_rig=test_rig,
        _kpi_test_tag=test_tag,
        _kpi_dut_hw_version=dut_hw_version,
        _kpi_dut_sw_version=dut_sw_version,
        _kpi_dut_model_num=dut_model_num,
        _kpi_dut_serial_num=dut_serial_num,
        _kpi_test_id=test_id)

    if args.csv_outfile is None:
        current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        csv_outfile = "{}_{}-test_ip_variable_time.csv".format(
            args.csv_outfile, current_time)
        csv_outfile = report.file_add_path(csv_outfile)
        logger.info("csv output file : {}".format(csv_outfile))

    # create here & pass in w/ MaxAssociate, or
    wiphy_info = lf_radio_info.radio_information(args.mgr,
                                                 _resource=args.resource,
                                                 debug_=args.debug,
                                                 _exit_on_fail=True)

    # add: ssid, passwd, wifi settings, enabled flags
    max_association = max_associate(args.mgr, args.port,
                                    wiphy0_ssid=args.wiphy0_ssid,
                                    wiphy1_ssid=args.wiphy1_ssid,
                                    passwd=args.passwd,
                                    security=args.security,
                                    resource=args.resource,
                                    upstream_port=args.upstream_port,
                                    download_bps=args.download_bps,
                                    upload_bps=args.upload_bps,
                                    wiphy_info=wiphy_info,
                                    traffic_type=args.traffic_type,
                                    name_prefix="sta",
                                    _test_duration=args.test_duration,
                                    monitor_interval=args.monitor_interval,
                                    layer3_columns=args.layer3_cols,
                                    report_file=args.report_file,
                                    kpi_csv=kpi_csv,
                                    kpi_path=kpi_path,
                                    output_format=args.output_format,
                                    port_mgr_columns=args.port_mgr_cols,
                                    compared_report=args.compared_report,
                                    outfile=args.csv_outfile,
                                    debug_=args.debug,
                                    _exit_on_fail=True)

    max_association.format_report_path()
    max_association.build()
    max_association.layer3_connections()
    max_association.run()

    # Reporting Results (.pdf & .html)
    csv_results_file = max_association.get_csv_name()
    logger.info("csv_results_file: {}".format(csv_results_file))
    # csv_results_file = kpi_path + "/" + kpi_filename
    report.set_title("L3 Test Max Association")
    report.build_banner()
    report.set_table_title("L3 Test Max Association Key Performance Indexes")
    report.build_table_title()
    report.set_table_dataframe_from_csv(csv_results_file)
    report.build_table()
    report.write_html_with_timestamp()
    report.write_index_html()
    # report.write_pdf(_page_size = 'A3', _orientation='Landscape')
    # report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
    report.write_pdf_with_timestamp(_page_size='A4', _orientation='Landscape')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
