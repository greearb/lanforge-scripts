#! usr/bin/env python3
"""
NAME: lf_mixed_traffic.py

PURPOSE:
        Mixed traffic test is designed to measure the access point performance and stability by running multiple traffic
        on both virtual & real clients like Android, Linux, Windows, and IOS connected to the access point.
        This test allows the user to choose multiple types of traffic like client ping test, qos test, ftp test, http test,
        multicast test multicast test and run tests both serially and simultaneously.

EXAMPLE:

        # CLI for Mixed Traffic Test: Run with Real Clients without connecting to a specified SSID

            python3 lf_mixed_traffic.py --mgr 192.168.212.100 --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup

        # CLI for Mixed Traffic Test: Run with Real Clients with parallel execution of tests

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup --parallel

        # CLI for Mixed Traffic Test: Run with Real Clients on 2.4GHz & 5GHz Bands, Single Iteration per Band.

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup

        # CLI for Mixed Traffic Test: Run on 2.4GHz & 5GHz Bands Simultaneously with Real Clients in a Single Iteration.

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --all_bands --pre_cleanup

        # CLI for Mixed Traffic Test: Run with Virtual Clients on 2.4GHz & 5GHz Bands, Single Iteration per Band.

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --virtual --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup

        # CLI for Mixed Traffic Test: Run on 2.4GHz & 5GHz Bands Simultaneously with Virtual Clients in a Single Iteration.

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --virtual --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --all_bands --pre_cleanup

SCRIPT_CLASSIFICATION:  Multiples Tests, Creation, Report Generation (Both individual & Overall)

SCRIPT_CATEGORIES:  Performance, Functional

NOTES:
        The primary goal of the script is to execute a series of tests and group their individual test reports into a unified report.

STATUS: Functional

VERIFIED_ON: 30-Apr-2024
             GUI Version:  5.4.8
             Build Date :  Sun Apr 21 01:42:42 PM PDT 2024
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
"""
import argparse
import asyncio
import importlib
import logging
import platform
import sys
import os
import time
import datetime
import pandas as pd
from multiprocessing import Process, Pipe
import traceback

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit(0)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_cleanup = importlib.import_module("py-scripts.lf_cleanup")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
lf_base_interop_profile = importlib.import_module("py-scripts.lf_base_interop_profile")

# importing scripts
ping_test = importlib.import_module("py-scripts.lf_interop_ping")
qos_test = importlib.import_module("py-scripts.lf_interop_qos")
qos_test_virtual = importlib.import_module("py-scripts.throughput_qos")
ftp_test = importlib.import_module("py-scripts.lf_ftp")
http_test = importlib.import_module("py-scripts.lf_webpage")
multicast_test = importlib.import_module("py-scripts.test_l3")

logger = logging.getLogger(__name__)


class Mixed_Traffic(Realm):
    def __init__(self,
                 host="",
                 port=8080,
                 lf_username="",
                 lf_password="",
                 real_client=False,
                 virtual_client=True,
                 selected_test_list="",
                 server_ip="",
                 ssid="",
                 passwd="",
                 security="",

                 twog_ssid="",
                 fiveg_ssid="",
                 sixg_ssid="",
                 twog_password="",
                 fiveg_password="",
                 sixg_password="",
                 twog_security="",
                 fiveg_security="",
                 sixg_security="",

                 twog_radio='',
                 fiveg_radio='',
                 sixg_radio='',

                 twog_mode='',
                 fiveg_mode='',
                 sixg_mode='',

                 twog_num_stations='',
                 fiveg_num_stations='',
                 sixg_num_stations='',

                 twog_start_id='',
                 fiveg_start_id='',
                 sixg_start_id='',

                 selected_bands="",

                 band="",
                 mode="",
                 # radio="",
                 number_template="0000",
                 # sta_list="",
                 num_stations=0,
                 upstream_port="",
                 qos_tos_list="",
                 dut_model="",
                 dut_firmware="",
                 test_duration="",
                 ping_test_duration="",
                 qos_test_duration="",
                 ftp_test_duration="",
                 http_test_duration="",
                 multicast_test_duration="",
                 qos_serial=False,
                 path='',
                 configure=True,
                 parallel=False,
                 target='192.168.1.3',
                 multicast_endp_types=None,
                 multicast_tos=None,
                 debug=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port)

        self.report_path = None
        self.lf_report_mt = None
        self.test_duration1 = None
        self.station_lists = []
        self.wifi_mode_list = []
        self.ssid_security_list = []
        self.ssid_password_list = []
        self.ssid_list = []
        self.num_sta_per_radio_list = []
        self.radio_name_list = []
        self.mc_tos = None
        self.endp_types = None
        self.dataset2 = None
        self.dataset = None
        self.lis = []
        self.data = {}
        self.ping_test_obj = None
        self.ftp_test_obj = None
        self.http_obj = None
        self.multicast_test_obj = None
        self.interval = ""
        self.target = ""
        self.eid_list = []
        self.windows_eids = []
        self.windows_ports = []
        self.hw_list = []
        self.windows_list = []
        self.linux_list = []
        self.mac_list = []
        self.android_list = []
        self.user_query = []
        # self.available_device_list = []
        self.res = None
        self.load = None
        self.data_set = None
        self.debug = debug
        self.host = host
        self.port = port
        self.lf_username = lf_username
        self.lf_password = lf_password
        self.real = real_client
        self.virtual = virtual_client
        self.tests = selected_test_list
        self.ssid = ssid
        self.passwd = passwd
        self.security = security

        self.configure = configure

        self.server_ip = server_ip
        self.ssid_2g = twog_ssid
        self.ssid_5g = fiveg_ssid
        self.ssid_6g = sixg_ssid

        self.passwd_2g = twog_password
        self.passwd_5g = fiveg_password
        self.passwd_6g = sixg_password

        self.security_2g = twog_security
        self.security_5g = fiveg_security
        self.security_6g = sixg_security

        self.radio_2g = twog_radio
        self.radio_5g = fiveg_radio
        self.radio_6g = sixg_radio

        self.mode_2g = twog_mode
        self.mode_5g = fiveg_mode
        self.mode_6g = sixg_mode

        self.num_stations_2g = twog_num_stations
        self.num_stations_5g = fiveg_num_stations
        self.num_stations_6g = sixg_num_stations

        self.start_id_2g = twog_start_id
        self.start_id_5g = fiveg_start_id
        self.start_id_6g = sixg_start_id

        self.selected_bands = selected_bands

        self.band = ''
        self.mode = mode
        # self.radio = radio
        self.number_template = number_template
        self.station_list = []
        self.num_staions = num_stations
        self.upstream_port = upstream_port
        self.dut_model = dut_model
        self.dut_firmware = dut_firmware
        self.test_duration = test_duration
        self.ping_test_duration = ping_test_duration
        self.qos_test_duration = qos_test_duration
        self.ftp_test_duration = ftp_test_duration
        self.http_test_duration = http_test_duration
        self.multicast_test_duration = multicast_test_duration
        self.path = path
        self.station_profile = self.new_station_profile()
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.passwd,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = self.mode

        # parallel test script status
        self.ping_test_status = False
        self.qos_test_status = False
        self.ftp_test_status = False
        self.http_test_status = False
        self.multicast_test_status = False

        self.qos_tos_list = qos_tos_list.split(',')
        self.qos_serial_run = qos_serial

        self.parallel = parallel
        
        self.target = target
        self.multicast_endp_types = multicast_endp_types
        self.multicast_tos = multicast_tos

        # Base Profile obj
        self.base_interop_profile = lf_base_interop_profile.RealDevice(manager_ip=self.host,
                                                                       server_ip=self.server_ip,
                                                                       ssid_2g=self.ssid_2g,
                                                                       passwd_2g=self.passwd_2g,
                                                                       encryption_2g=self.security_2g,
                                                                       ssid_5g=self.ssid_5g,
                                                                       passwd_5g=self.passwd_5g,
                                                                       encryption_5g=self.security_5g,
                                                                       ssid_6g=self.ssid_6g,
                                                                       passwd_6g=self.passwd_6g,
                                                                       encryption_6g=self.security_6g,
                                                                       selected_bands=self.selected_bands)
        # LF Cleanup obj
        self.cleanup = lf_cleanup.lf_clean(host=self.host, port=self.port, resource='all')
        # sorting out the test duration for each test
        duration_suffixes = {'s': 1, 'S': 1, 'm': 60, 'M': 60, 'h': 3600, 'H': 3600}
        if self.parallel:
            if self.test_duration.endswith(tuple(duration_suffixes.keys())):
                self.test_duration_suffix = self.test_duration[-1]
                multiplier = duration_suffixes[self.test_duration_suffix]
                self.test_duration = int(self.test_duration[:-1]) * multiplier
            else:
                self.test_duration = int(self.test_duration)

            self.total_all_test_duration = self.test_duration
            time_obj = time.gmtime(self.total_all_test_duration)
            self.time_formate = time.strftime("%H:%M:%S", time_obj)
        else:
            if self.test_duration:
                if self.test_duration.endswith(tuple(duration_suffixes.keys())):
                    self.test_duration_suffix = self.test_duration[-1]
                    multiplier = duration_suffixes[self.test_duration_suffix]
                    self.test_duration = int(self.test_duration[:-1]) * multiplier
                else:
                    self.test_duration = int(self.test_duration)
                # Setting overall time formatting for report
                if self.qos_serial_run:
                    self.total_all_test_duration = int(self.test_duration * (len(self.tests) - 1 + len(self.qos_tos_list)))
                else:
                    self.total_all_test_duration = int(self.test_duration * len(self.tests))
                time_obj = time.gmtime(self.total_all_test_duration)
                self.time_formate = time.strftime("%H:%M:%S", time_obj)
            elif self.ping_test_duration or self.qos_test_duration or self.ftp_test_duration or self.http_test_duration or self.multicast_test_duration:
                if self.ping_test_duration.endswith(tuple(duration_suffixes.keys())) or self.qos_test_duration.endswith(
                    tuple(duration_suffixes.keys())) or self.ftp_test_duration.endswith(
                    tuple(duration_suffixes.keys())) or self.http_test_duration.endswith(
                    tuple(duration_suffixes.keys())) or self.multicast_test_duration.endswith(
                    tuple(duration_suffixes.keys())):
                    # ping test duration
                    self.ping_test_duration_suffix = self.ping_test_duration[-1]
                    multiplier = duration_suffixes[self.ping_test_duration_suffix]
                    self.ping_test_duration = int(self.ping_test_duration[:-1]) * multiplier
                    # qos test duration
                    self.qos_test_duration_suffix = self.qos_test_duration[-1]
                    multiplier = duration_suffixes[self.qos_test_duration_suffix]
                    self.qos_test_duration = int(self.qos_test_duration[:-1]) * multiplier
                    # ftp test duration
                    self.ftp_test_duration_suffix = self.ftp_test_duration[-1]
                    multiplier = duration_suffixes[self.ftp_test_duration_suffix]
                    self.ftp_test_duration = int(self.ftp_test_duration[:-1]) * multiplier
                    # http test duration
                    self.http_test_duration_suffix = self.http_test_duration[-1]
                    multiplier = duration_suffixes[self.http_test_duration_suffix]
                    self.http_test_duration = int(self.http_test_duration[:-1]) * multiplier
                    # multicast test duration
                    self.multicast_test_duration_suffix = self.multicast_test_duration[-1]
                    multiplier = duration_suffixes[self.multicast_test_duration_suffix]
                    self.multicast_test_duration = int(self.multicast_test_duration[:-1]) * multiplier
                else:
                    logger.info("Please provide the test duration for at least one single test scenario to run...")
                if self.qos_serial_run:
                    self.total_all_test_duration = int(self.ping_test_duration + (self.qos_test_duration * len(
                        self.qos_tos_list)) + self.ftp_test_duration + self.http_test_duration + self.multicast_test_duration)
                else:
                    self.total_all_test_duration = int(
                        self.ping_test_duration + self.qos_test_duration + self.ftp_test_duration + self.http_test_duration + self.multicast_test_duration)
                time_obj = time.gmtime(self.total_all_test_duration)
                self.time_formate = time.strftime("%H:%M:%S", time_obj)

    def report_obj(self, band, path):
        if band is None:
            band = 'all'
        self.lf_report_mt = lf_report_pdf.lf_report(_output_pdf=f"mixed_traffic_test_{band}.pdf",
                                                    _output_html=f"mixed_traffic_test_{band}.html",
                                                    _path=path,
                                                    _results_dir_name=f"Mixed_Traffic_Test_Report_{band}")
        self.report_path = self.lf_report_mt.get_path_date_time()

    def pre_cleanup(self):  # cleaning pre-existing stations and cross connections
        if not self.real:
            self.cleanup.sta_clean()
        resp = self.json_get('/generic?fields=name')
        if 'endpoints' in resp:
            for i in resp['endpoints']:
                if list(i.values())[0]['name']:
                    self.generic_endps_profile.created_cx.append('CX_' + list(i.values())[0]['name'])
                    self.generic_endps_profile.created_endp.append(list(i.values())[0]['name'])
        self.generic_endps_profile.cleanup()
        self.cleanup.cxs_clean()
        self.cleanup.layer3_endp_clean()
        self.cleanup.layer4_endp_clean()

    def virtual_client_creation(self, ssid, password, security, band, radio, num_stations, start_id, all_sta=False):
        start_id = start_id
        station_list = []
        if start_id != 0:
            start_id = int(start_id)

        if (num_stations is not None) and (int(num_stations) > 0):
            num_stations_converted = int(num_stations)
            num_sta = num_stations_converted
            station_list = LFUtils.port_name_series(prefix="sta",
                                                    start_id=start_id,
                                                    end_id=start_id + num_sta - 1,
                                                    padding_number=10000,
                                                    radio=radio)
        # updating num stations and station list
        if not all_sta:
            self.station_list = station_list
            self.num_staions = num_stations
            self.radio = radio
        logger.info("Virtual station list for {band} : {station_list}".format(band=band, station_list=station_list))
        if "2.4G" in band:
            self.station_profile.mode = 13
        elif "5G" in band:
            self.station_profile.mode = 14
        elif "6G" in band:
            self.station_profile.mode = 15
        # station build
        self.station_profile.use_security(security, ssid, password)
        self.station_profile.set_number_template("00")
        logger.info("Creating  Virtual Stations...")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        if self.station_profile.create(radio=radio, sta_names_=station_list, debug=self.debug):
            self._pass("Stations created.")
        else:
            self._fail("Stations not properly created.")
        self.station_profile.admin_up()
        logger.info("Waiting until the all station ports are up. Max time out is 300 seconds.")
        if not LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                                 port_list=station_list,
                                                 debug_=self.debug):
            self._fail("Unable to bring all stations up")
            return
        logger.info("Waiting to get IP for all stations...")
        if Realm.wait_for_ip(self=self, station_list=station_list, timeout_sec=-1):
            self._pass("All stations got IPs", print_=True)
            self._pass("Station build finished", print_=True)
        else:
            self._fail("Stations failed to get IPs", print_=True)
            self._fail("FAIL: Station build failed", print_=True)
            logger.info("Please re-check the configuration applied")
        return station_list

    def convert_seconds(self, seconds):
        if seconds < 60:
            return f"{seconds} sec"
        elif 60 <= seconds < 3600:
            minutes = seconds / 60
            if minutes == 1.0:
                return f"{str(round(abs(minutes), 1))} minute"
            else:
                return f"{str(round(abs(minutes), 1))} minutes"
        else:
            hours = seconds / 3600
            if hours == 1.0:
                return f"{str(round(abs(hours), 1))} hour"
            else:
                return f"{str(round(abs(hours), 1))} hours"

    def selecting_devices_from_available(self):
        selected_serial_list = self.base_interop_profile.query_all_devices_to_configure_wifi()
        logger.info(f"Selected Serial List: {selected_serial_list}")
        return selected_serial_list
    
    def select_real_devices(self, real_devices, real_sta_list=None, base_interop_obj=None):
        self.real_sta_data_dict = {}
        if real_sta_list is None:
            self.user_query = real_devices.query_user()
            self.real_sta_list = self.user_query[0]

            # fetching window's list
            for port in self.user_query[0]:
                if 'wlan0' not in port:
                    port = port + '.wlan0'
                eid = self.name_to_eid(port)
                self.eid_list.append(str(eid[0]) + '.' + str(eid[1]))
            for eid in self.eid_list:
                for device in self.user_query[1]:
                    if ("Win" in device) and (eid + ' ' in device):
                        self.windows_eids.append(eid)
            for eid in self.windows_eids:
                for port in self.user_query[0]:
                    if eid + '.' in port:
                        self.windows_ports.append(port)
        else:
            self.real_sta_list = real_sta_list
        if base_interop_obj is not None:
            self.base_interop_profile = base_interop_obj

        # Need real stations to run interop test
        if (len(self.real_sta_list) == 0):
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        logging.info('{}'.format(*self.real_sta_list))

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logger.error('Real station not in devices data')
                raise ValueError('Real station not in devices data')

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        # Track number of selected devices
        self.android = self.base_interop_profile.android
        self.windows = self.base_interop_profile.windows
        self.mac = self.base_interop_profile.mac
        self.linux = self.base_interop_profile.linux

    def real_client_wifi_config(self, selected_serial_list, all_devices=False):
        self.user_query = []
        logging.info(f"Ready for Connectivity: {selected_serial_list}")
        if not all_devices:
            self.base_interop_profile.selected_devices = []
            self.base_interop_profile.report_labels = []
            self.base_interop_profile.selected_macs = []
        user_query_list = asyncio.run(self.base_interop_profile.configure_wifi(select_serials=selected_serial_list))

        logger.info("Query Result: {}".format(user_query_list))
        # removing the postfix name for the
        for index, sublist in enumerate(user_query_list):
            new_sublist = []
            for item in sublist:
                if index == 0:
                    if '.wlan0' not in item and '.wlan1' not in item and '.en0' not in item and '.sta0' not in item:
                        item += '.wlan0'
                elif index == 1:
                    item = item.replace('.wlan0', '').replace('.en0', '').replace('.sta0', '').replace('wlan1', '')
                new_sublist.append(item)
            self.user_query.append(new_sublist)

        logger.info("UPDATE: Query Result: {}".format(self.user_query))
        # fetching window's list
        for port in self.user_query[0]:
            if 'wlan0' not in port:
                port = port + '.wlan0'
            eid = self.name_to_eid(port)
            self.eid_list.append(str(eid[0]) + '.' + str(eid[1]))
        for eid in self.eid_list:
            for device in self.user_query[1]:
                if ("Win" in device) and (eid + ' ' in device):
                    self.windows_eids.append(eid)
        for eid in self.windows_eids:
            for port in self.user_query[0]:
                if eid + '.' in port:
                    self.windows_ports.append(port)
        return self.user_query

    def ping_test(self, ssid='', password='', security='', target='', interval='', _ping_test=ping_test,
                  all_bands=False, conn=None):
        try:
            # setting ping test duration & converting sec into minutes passing it float values for ping test
            if self.test_duration:
                minutes, seconds = divmod(self.test_duration, 60)
                ping_test_duration = float(minutes)
            else:
                minutes, seconds = divmod(self.ping_test_duration, 60)
                ping_test_duration = float(minutes)
            self.target = target
            self.interval = interval
            # starting part of the ping test
            self.ping_test_obj = ping_test.Ping(host=self.host, port=self.port, ssid=ssid, security=security,
                                                password=password, lanforge_password="lanforge", target=self.target,
                                                interval=self.interval, sta_list=[], virtual=self.virtual, real=self.real,
                                                duration=ping_test_duration)
            if not self.ping_test_obj.check_tab_exists():
                print('Generic Tab is not available for Ping Test.\nAborting the test.')
                exit(0)
            if self.real:
                self.ping_test_obj.select_real_devices(real_devices=self.base_interop_profile,
                                                    real_sta_list=self.user_query[0],
                                                    base_interop_obj=self.base_interop_profile)
                # removing the existing generic endpoints & cxs
                self.ping_test_obj.cleanup()
                self.ping_test_obj.sta_list = self.user_query[0]
            elif self.virtual:
                self.ping_test_obj.sta_list = self.station_list
                print('Virtual Stations: {}'.format(self.station_list).replace('[', '').replace(']', '').replace('\'', ''))
                # #cleanup
                for station in self.station_list:
                    print('Removing the station {} if exists'.format(station))
                    self.ping_test_obj.generic_endps_profile.created_cx.append(
                        'CX_generic-{}'.format(station.split('.')[2]))
                    self.ping_test_obj.generic_endps_profile.created_endp.append(
                        'generic-{}'.format(station.split('.')[2]))
                self.ping_test_obj.generic_endps_profile.cleanup()
                self.ping_test_obj.generic_endps_profile.created_cx = []
                self.ping_test_obj.generic_endps_profile.created_endp = []
            # creating generic endpoints
            self.ping_test_obj.create_generic_endp()
            logger.info("Generic Cross-Connection List: {}".format(self.ping_test_obj.generic_endps_profile.created_cx))
            logger.info('Starting Running the Ping Test for {} minutes'.format(ping_test_duration))
            # start generate endpoint
            self.ping_test_obj.start_generic()
            ports_data_dict = self.ping_test_obj.json_get('/ports/all/')['interfaces']
            ports_data = {}
            for ports in ports_data_dict:
                port, port_data = list(ports.keys())[0], list(ports.values())[0]
                ports_data[port] = port_data
            time.sleep(ping_test_duration * 60)
            logger.info('Stopping the PING Test...')
            self.ping_test_obj.stop_generic()
            # getting result dict
            result_data = self.ping_test_obj.get_results()
            result_json = {}
            if self.real:
                if type(result_data) == dict:
                    for station in self.ping_test_obj.sta_list:
                        current_device_data = self.base_interop_profile.devices_data[station]
                        if station in result_data['name']:
                            result_json[station] = {
                                'command': result_data['command'],
                                'sent': result_data['tx pkts'],
                                'recv': result_data['rx pkts'],
                                'dropped': result_data['dropped'],
                                'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                'mac': current_device_data['mac'],
                                'channel': current_device_data['channel'],
                                'ssid': current_device_data['ssid'],
                                'mode': current_device_data['mode'],
                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                                'remarks': [],
                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]}
                            result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
                else:
                    for station in self.ping_test_obj.sta_list:
                        current_device_data = self.base_interop_profile.devices_data[station]
                        for ping_device in result_data:
                            ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                            if station in ping_endp:
                                result_json[station] = {
                                    'command': ping_data['command'],
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                    'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                    'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                    'mac': current_device_data['mac'],
                                    'channel': current_device_data['channel'],
                                    'ssid': current_device_data['ssid'],
                                    'mode': current_device_data['mode'],
                                    'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                    'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                                    'remarks': [],
                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]}
                                result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
            if self.virtual:
                ports_data_dict = self.ping_test_obj.json_get('/ports/all/')['interfaces']
                ports_data = {}
                for ports in ports_data_dict:
                    port, port_data = list(ports.keys())[0], list(ports.values())[0]
                    ports_data[port] = port_data
                if type(result_data) == dict:
                    for station in self.ping_test_obj.sta_list:
                        if station not in self.ping_test_obj.real_sta_list:
                            current_device_data = ports_data[station]
                            if station.split('.')[2] in result_data['name']:
                                result_json[station] = {
                                    'command': result_data['command'],
                                    'sent': result_data['tx pkts'],
                                    'recv': result_data['rx pkts'],
                                    'dropped': result_data['dropped'],
                                    'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                    'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                    'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                                    'mac': current_device_data['mac'],
                                    'channel': current_device_data['channel'],
                                    'ssid': current_device_data['ssid'],
                                    'mode': current_device_data['mode'],
                                    'name': station,
                                    'os': 'Virtual',
                                    'remarks': [],
                                    'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]}
                                result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
                else:
                    for station in self.ping_test_obj.sta_list:
                        if station not in self.ping_test_obj.real_sta_list:
                            current_device_data = ports_data[station]
                            for ping_device in result_data:
                                ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                                if station.split('.')[2] in ping_endp:
                                    result_json[station] = {
                                        'command': ping_data['command'],
                                        'sent': ping_data['tx pkts'],
                                        'recv': ping_data['rx pkts'],
                                        'dropped': ping_data['dropped'],
                                        'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                        'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                        'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                                        'mac': current_device_data['mac'],
                                        'channel': current_device_data['channel'],
                                        'ssid': current_device_data['ssid'],
                                        'mode': current_device_data['mode'],
                                        'name': station,
                                        'os': 'Virtual',
                                        'remarks': [],
                                        'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]}
                                    result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
            logger.info("Final Result Json For Ping Test: {}".format(result_json))
            if all_bands:
                band = ''
            else:
                band = '_' + self.band
            self.ping_test_obj.generate_report(result_json=result_json, result_dir=f'Ping_Test_Report{band}',
                                            report_path=self.report_path)
            self.ping_test_status = True
            if(conn):
                conn.send([self.ping_test_obj, True])
        except:
            traceback.print_exc()
            if(conn):
                conn.send(['', False])

    def qos_test(self, ssid, password, security, ap_name, upstream, tos, traffic_type, side_a_min=0, side_b_min=0,
                 side_a_max=0, side_b_max=0, _qos_test=qos_test, _qos_test_virtual=qos_test_virtual, all_bands=False, conn=None):
        try:
            if self.test_duration:
                self.qos_test_duration = self.test_duration
            test_results = {'test_results': []}

            # qos test for real clients
            def qos_test_overall_real(qos_tos_real=None):
                self.qos_test_obj = qos_test.ThroughputQOS(host=self.host,
                                                        port=self.port,
                                                        number_template="0000",
                                                        ap_name=ap_name,
                                                        name_prefix="TOS-",
                                                        tos=qos_tos_real if self.qos_serial_run else tos,
                                                        ssid=ssid,
                                                        password=password,
                                                        security=security,
                                                        upstream=upstream,
                                                        test_duration=self.qos_test_duration,
                                                        use_ht160=False,
                                                        side_a_min_rate=int(side_a_min),
                                                        side_b_min_rate=int(side_b_min),
                                                        side_a_max_rate=int(side_a_max),
                                                        side_b_max_rate=int(side_b_max),
                                                        traffic_type=traffic_type,
                                                        _debug_on=False)

                self.qos_test_obj.input_devices_list = self.user_query[0]
                self.qos_test_obj.real_client_list = self.user_query[1]
                self.qos_test_obj.real_client_list1 = self.user_query[1]
                self.qos_test_obj.mac_id_list = self.user_query[2]
                self.qos_test_obj.build()
                self.qos_test_obj.start()
                time.sleep(10)
                try:
                    connections_download, connections_upload, drop_a_per, drop_b_per = self.qos_test_obj.monitor()
                except Exception as e:
                    print(f"Failed at Monitoring the CX... {e}")
                self.qos_test_obj.stop()
                time.sleep(5)
                test_results['test_results'].append(
                    self.qos_test_obj.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                self.data.update(test_results)
                test_end_time = datetime.datetime.now().strftime("%b %d %H:%M:%S")
                logger.info("QOS Test ended at: {}".format(test_end_time))


                self.qos_test_obj.cleanup()
                print("Data", self.data)

                if self.qos_serial_run:
                    self.result1, self.result2, self.result3, self.result4 = {}, {}, {}, {}
                    # separating dictionaries for each value in the list
                    result_dicts = []
                    for item in self.data['test_results']:
                        result_dict = {'test_results': [item]}
                        result_dicts.append(result_dict)

                    if len(result_dicts) == 1:
                        print("yes - 1")
                        self.result1 = result_dicts[0]
                        self.data1 = self.result1
                    if len(result_dicts) == 2:
                        print("yes - 2")
                        self.result1, self.result2 = result_dicts[0], result_dicts[1]
                        self.data1 = self.result2
                    if len(result_dicts) == 3:
                        print("yes - 3")
                        self.result1, self.result2, self.result3 = result_dicts[0], result_dicts[1], result_dicts[2]
                        self.data1 = self.result3
                    if len(result_dicts) == 4:
                        print("yes - 4")
                        self.result1, self.result2, self.result3, self.result4 = result_dicts[0], result_dicts[1], result_dicts[2], result_dicts[3]
                        self.data1 = self.result4
                    self.data = self.data1
                if all_bands:
                    band = ''
                else:
                    band = '_' + self.band
                self.qos_test_obj.generate_report(data=self.data,
                                                input_setup_info={"contact": "support@candelatech.com"},
                                                report_path=self.report_path,
                                                result_dir_name=f"Qos_Test_Report_{qos_tos_real}{band}")

                self.data_set, self.load, self.res = self.qos_test_obj.generate_graph_data_set(self.data)

            # Qos Test for Virtual station
            def qos_test_overall_virtual(qos_tos_virtual=None):
                self.throughput_qos_obj = qos_test_virtual.ThroughputQOS(host=self.host,
                                                                        port=self.port,
                                                                        number_template="0000",
                                                                        ap_name=ap_name,
                                                                        num_stations=self.num_staions,
                                                                        sta_list=self.station_list,
                                                                        create_sta=False,
                                                                        name_prefix="TOS-",
                                                                        upstream=self.upstream_port,
                                                                        ssid=ssid,
                                                                        password=password,
                                                                        security=security,
                                                                        ssid_2g=self.ssid_2g,
                                                                        password_2g=self.passwd_2g,
                                                                        security_2g=self.security_2g,
                                                                        ssid_5g=self.ssid_5g,
                                                                        password_5g=self.passwd_5g,
                                                                        security_5g=self.security_5g,
                                                                        ssid_6g=self.ssid_6g,
                                                                        password_6g=self.passwd_6g,
                                                                        security_6g=self.security_6g,
                                                                        radio_2g=self.radio_2g,
                                                                        radio_5g=self.radio_5g,
                                                                        radio_6g=self.radio_6g,
                                                                        test_duration=self.qos_test_duration,
                                                                        use_ht160=False,
                                                                        side_a_min_rate=int(side_a_min),
                                                                        side_b_min_rate=int(side_b_min),
                                                                        side_a_max_rate=int(side_a_max),
                                                                        side_b_max_rate=int(side_b_max),
                                                                        mode=self.mode,
                                                                        bands=self.band,
                                                                        traffic_type=traffic_type,
                                                                        tos=qos_tos_virtual if self.qos_serial_run else tos,
                                                                        test_case=[self.band])
                # throughput_qos.pre_cleanup()
                self.throughput_qos_obj.build()

                self.throughput_qos_obj.start(False, False)
                time.sleep(10)
                try:
                    connections_download, connections_upload, drop_a_per, drop_b_per = self.throughput_qos_obj.monitor()
                except Exception as e:
                    print(f"Failed at Monitoring the CX... {e}")
                print("connections download", connections_download)
                print("connections upload", connections_upload)
                self.throughput_qos_obj.stop()
                time.sleep(5)
                test_results['test_results'].append(self.throughput_qos_obj.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                self.data.update({self.band: test_results})  # right now it will only work for single band
                self.throughput_qos_obj.cx_profile.cleanup()
                print("DAta", self.data)
                if self.qos_serial_run:
                    self.result1, self.result2, self.result3, self.result4 = {}, {}, {}, {}
                    # separating dictionaries for each value in the list
                    result_dicts = []
                    for item in self.data[self.band]['test_results']:
                        result_dict = {self.band: {'test_results': [item]}}
                        result_dicts.append(result_dict)
                    print("RES", result_dicts)

                    if len(result_dicts) == 1:
                        print("yes - 1")
                        self.result1 = result_dicts[0]
                        self.data1 = self.result1
                    if len(result_dicts) == 2:
                        print("yes - 2")
                        self.result1, self.result2 = result_dicts[0], result_dicts[1]
                        self.data1 = self.result2
                    if len(result_dicts) == 3:
                        print("yes - 3")
                        self.result1, self.result2, self.result3 = result_dicts[0], result_dicts[1], result_dicts[2]
                        self.data1 = self.result3
                    if len(result_dicts) == 4:
                        print("yes - 4")
                        self.result1, self.result2, self.result3, self.result4 = result_dicts[0], result_dicts[1], result_dicts[2], result_dicts[3]
                        self.data1 = self.result4
                    self.data = self.data1

                test_end_time = datetime.datetime.now().strftime("%b %d %H:%M:%S")
                print("Test ended at: ", test_end_time)

                response_port = self.json_get("/port/all")
                self.virtual_mac_list, self.virtual_channel_list = [], []
                for interface in response_port['interfaces']:
                    for port, port_data in interface.items():
                        if port in self.station_list:
                            self.virtual_mac_list.append(port_data['mac'])
                            self.virtual_channel_list.append(port_data['channel'])
                self.throughput_qos_obj.mac_list = self.virtual_mac_list
                self.throughput_qos_obj.channel_list = self.virtual_channel_list
                if all_bands:
                    band = ''
                else:
                    band = '_' + self.band
                self.throughput_qos_obj.generate_report(data=self.data,
                                                        input_setup_info={"contact": "support@candelatech.com"},
                                                        report_path=self.report_path,
                                                        result_dir_name=f"Qos_Test_Report_{qos_tos_virtual}{band}"
                                                        )
                self.data_set, self.load, self.res = self.throughput_qos_obj.generate_graph_data_set(self.data)

            if self.real:
                if self.qos_serial_run:
                    for qos_tos in self.qos_tos_list:
                        qos_test_overall_real(qos_tos)
                else:
                    qos_test_overall_real()
                if(conn):
                    conn.send([self.qos_test_obj, self.data_set, self.load, self.res, True])
            if self.virtual:
                if self.qos_serial_run:
                    for qos_tos in self.qos_tos_list:
                        qos_test_overall_virtual(qos_tos)
                else:
                    qos_test_overall_virtual()
                if(conn):
                    conn.send([self.throughput_qos_obj, self.data_set, self.load, self.res, True])
            self.qos_test_status = True
        except:
            traceback.print_exc()
            if(conn):
                conn.send(['', '', '', '', False])

    def ftp_test(self, ssid, password, security, bands, directions, file_sizes, ftp_test=ftp_test, all_bands=False, conn=None):
        try:
            if self.test_duration:
                self.ftp_test_duration = self.test_duration
            interation_num = 0
            ftp_data = {}
            client_type = ""
            if self.real:
                client_type = "Real"
            if self.virtual:
                client_type = "Virtual"
            # For all combinations ftp_data of directions, file size and client counts, run the test
            for direction in directions:
                for file_size in file_sizes:
                    self.ftp_test_obj = ftp_test.FtpTest(lfclient_host=self.host,
                                                            lfclient_port=self.port,
                                                            upstream=self.upstream_port,
                                                            dut_ssid=ssid,
                                                            dut_passwd=password,
                                                            dut_security=security,
                                                            ap_name=self.dut_model,
                                                            band=self.band,
                                                            file_size=file_size,
                                                            direction=direction,
                                                            twog_radio=self.radio_2g,
                                                            fiveg_radio=self.radio_5g,
                                                            sixg_radio=self.radio_6g,
                                                            lf_username=self.lf_username,
                                                            lf_password=self.lf_password,
                                                            traffic_duration=self.ftp_test_duration,
                                                            ssh_port=22,
                                                            clients_type=client_type)
                    interation_num = interation_num + 1
                    self.ftp_test_obj.file_create()
                    if self.real:
                        self.ftp_test_obj.input_devices_list = self.user_query[0]
                        self.ftp_test_obj.real_client_list1 = self.user_query[1]
                        self.ftp_test_obj.mac_id_list = self.user_query[2]
                        self.ftp_test_obj.windows_ports = self.windows_ports
                        self.ftp_test_obj.set_values()
                        self.ftp_test_obj.precleanup()
                        self.ftp_test_obj.build()
                    if self.virtual:
                        self.ftp_test_obj.station_profile.station_names = self.station_list
                        self.ftp_test_obj.station_list = self.station_list
                        self.ftp_test_obj.band = self.band  # since we will have only single band
                        self.ftp_test_obj.radio = []
                        self.ftp_test_obj.num_sta = self.num_staions
                        self.ftp_test_obj.count = 0
                        self.ftp_test_obj.set_values()
                        # pre cleanup layer-4 endpoints
                        self.cleanup.layer4_endp_clean()
                        self.ftp_test_obj.build()
                    if not self.ftp_test_obj.passes():
                        logger.info(self.ftp_test_obj.get_fail_message())

                    time1 = datetime.datetime.now()
                    logger.info("FTP Traffic started running at {}".format(time1))
                    self.ftp_test_obj.start(False, False)

                    time.sleep(self.ftp_test_duration)

                    self.ftp_test_obj.stop()
                    logger.info("FTP Traffic stopped running")
                    self.ftp_test_obj.my_monitor()
                    self.ftp_test_obj.cx_profile.cleanup()
                    time2 = datetime.datetime.now()
                    logger.info("FTP Test ended at {}".format(time2))
            if all_bands:
                band = ''
            else:
                band = '_' + self.band
            date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            self.ftp_test_obj.generate_report(ftp_data, date, input_setup_info="", test_rig="", test_tag="",
                                            dut_hw_version="", dut_sw_version="", dut_model_num="", dut_serial_num="",
                                            test_id="", bands=bands, csv_outfile=f"ftp_test{band}",
                                            local_lf_report_dir="", _results_dir_name=f'Ftp_Test_Report{band}',
                                            report_path=self.report_path)
            self.ftp_test_status = True
            if(conn):
                conn.send([self.ftp_test_obj, True])
        except:
            traceback.print_exc()
            if(conn):
                conn.send(['', False])

    def http_test(self, ssid, password, security, http_file_size, target_per_ten, http_test=http_test, all_bands=False, conn=None):
        try:
            if self.test_duration:
                self.http_test_duration = self.test_duration
            # Error checking to prevent case issues
            Bands =[self.band]
            for bands in range(len(Bands)):
                Bands[bands] = Bands[bands].upper()
                if Bands[bands] == "BOTH":
                    Bands[bands] = "Both"

            # Error checking for non-existent bands
            valid_bands = ['2.4G', '5G', '6G', 'Both']
            for bands in Bands:
                if bands not in valid_bands:
                    raise ValueError("Invalid band '%s' used in bands argument!" % bands)

            # Check for Both being used independently
            if len(Bands) > 1 and "Both" in Bands:
                raise ValueError("'Both' test type must be used independently!")


            list2G, list2G_bytes, list2G_speed, list2G_urltimes = [], [], [], []
            list5G, list5G_bytes, list5G_speed, list5G_urltimes = [], [], [], []
            list6G, list6G_bytes, list6G_speed, list6G_urltimes = [], [], [], []
            Both, Both_bytes, Both_speed, Both_urltimes = [], [], [], []
            dict_keys = []
            dict_keys.extend(Bands)
            final_dict = dict.fromkeys(dict_keys)
            dict1_keys = ['dl_time', 'min', 'max', 'avg', 'bytes_rd', 'speed', 'url_times']
            for i in final_dict:
                final_dict[i] = dict.fromkeys(dict1_keys)
            min2, min5, min6 = [], [], []
            min_both = []
            max2, max5, max6 = [], [], []
            max_both = []
            avg2, avg5, avg6 = [], [], []
            avg_both = []
            test_time = ""
            client_type = ""
            http_sta_list = []
            num_stations = 0
            if self.real:
                client_type = "Real"
                http_sta_list = self.user_query[0]
                num_stations = len(self.user_query[0])
            if self.virtual:
                client_type = "Virtual"
                http_sta_list = self.station_list
                num_stations = len(self.station_list)
            self.http_obj = http_test.HttpDownload(lfclient_host=self.host, lfclient_port=self.port,
                                                upstream=self.upstream_port,
                                                num_sta=len(self.user_query[0]) if self.real else len(self.station_list),
                                                ap_name=self.dut_model, ssid=ssid, password=password, security=security,
                                                target_per_ten=target_per_ten, file_size=http_file_size, bands=self.band,
                                                client_type=client_type, lf_username=self.lf_username,
                                                lf_password=self.lf_password)
            if self.real:
                self.http_obj.port_list = self.user_query[0]
                self.http_obj.devices_list = self.user_query[1]
                self.http_obj.macid_list = self.user_query[2]
                self.http_obj.user_query = self.user_query
                self.http_obj.windows_ports = self.windows_ports
                num_stations = len(self.user_query[0])
                self.http_obj.file_create(ssh_port=22)
                self.http_obj.set_values()
                self.http_obj.precleanup()
                self.http_obj.build()
            if self.virtual:
                # self.http_obj.station_profile.station_names = self.station_list
                self.http_obj.bands = self.band  # since we will have only single band
                self.http_obj.radio = []
                self.http_obj.num_sta = self.num_staions
                self.http_obj.file_create(ssh_port=22)
                # self.http_obj.set_values()
                # print(self.station_list)
                # self.http_obj.station_list = [[self.station_list]]
                self.cleanup.layer4_endp_clean()
                self.station_profile.admin_up()
                logger.info("Waiting until the all station ports are up. Max time out is 300 seconds.")
                if not LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                                            port_list=self.station_list,
                                                            debug_=self.debug):
                    self._fail("Unable to bring all stations up")
                    return
                logger.info("Waiting to get IP for all stations...")
                logger.info("Admin up all the stations...")
                Realm.wait_for_ip(self=self, station_list=self.station_list, timeout_sec=-1)

                # building layer4   #Todo: Since the lf_webpage script itself only support "download", so need to add upload functionality in future
                self.http_obj.http_profile.direction = 'dl'
                self.http_obj.http_profile.dest = '/dev/null'
                data = self.http_obj.local_realm.json_get("ports/list?fields=IP")

                # getting eth ip
                ip_upstream = None
                eid = self.http_obj.local_realm.name_to_eid(self.upstream_port)
                for i in data["interfaces"]:
                    for j in i:
                        interface = "{shelf}.{resource}.{port}".format(shelf=eid[0], resource=eid[1], port=eid[2])
                        if interface == j:
                            ip_upstream = i[interface]['ip']
                if ip_upstream is not None:
                    self.http_obj.http_profile.create(ports=self.station_list, sleep_time=.5,
                                                        suppress_related_commands_=None, http=True, user=self.lf_username,
                                                        passwd=self.lf_password,
                                                        http_ip=ip_upstream + "/webpage.html", proxy_auth_type=0x200, timeout=1000)
            test_time = datetime.datetime.now().strftime("%b %d %H:%M:%S")
            logger.info("HTTP Test started at {}".format(test_time))
            self.http_obj.start()
            time.sleep(self.http_test_duration)
            self.http_obj.stop()
            uc_avg_val = self.http_obj.my_monitor('uc-avg')
            url_times = self.http_obj.my_monitor('total-urls')
            rx_bytes_val = self.http_obj.my_monitor('bytes-rd')
            rx_rate_val = self.http_obj.my_monitor('rx rate')

            if bands == "2.4G":
                list2G.extend(uc_avg_val)
                list2G_bytes.extend(rx_bytes_val)
                list2G_speed.extend(rx_rate_val)
                list2G_urltimes.extend(url_times)
                final_dict['2.4G']['dl_time'] = list2G
                min2.append(min(list2G))
                final_dict['2.4G']['min'] = min2
                max2.append(max(list2G))
                final_dict['2.4G']['max'] = max2
                avg2.append((sum(list2G) / num_stations))
                final_dict['2.4G']['avg'] = avg2
                final_dict['2.4G']['bytes_rd'] = list2G_bytes
                final_dict['2.4G']['speed'] = list2G_speed
                final_dict['2.4G']['url_times'] = list2G_urltimes
            elif bands == "5G":
                list5G.extend(uc_avg_val)
                list5G_bytes.extend(rx_bytes_val)
                list5G_speed.extend(rx_rate_val)
                list5G_urltimes.extend(url_times)
                print(list5G, list5G_bytes, list5G_speed, list5G_urltimes)
                final_dict['5G']['dl_time'] = list5G
                min5.append(min(list5G))
                final_dict['5G']['min'] = min5
                max5.append(max(list5G))
                final_dict['5G']['max'] = max5
                avg5.append((sum(list5G) / num_stations))
                final_dict['5G']['avg'] = avg5
                final_dict['5G']['bytes_rd'] = list5G_bytes
                final_dict['5G']['speed'] = list5G_speed
                final_dict['5G']['url_times'] = list5G_urltimes
            elif bands == "6G":
                list6G.extend(uc_avg_val)
                list6G_bytes.extend(rx_bytes_val)
                list6G_speed.extend(rx_rate_val)
                list6G_urltimes.extend(url_times)
                final_dict['6G']['dl_time'] = list6G
                min6.append(min(list6G))
                final_dict['6G']['min'] = min6
                max6.append(max(list6G))
                final_dict['6G']['max'] = max6
                avg6.append((sum(list6G) / num_stations))
                final_dict['6G']['avg'] = avg6
                final_dict['6G']['bytes_rd'] = list6G_bytes
                final_dict['6G']['speed'] = list6G_speed
                final_dict['6G']['url_times'] = list6G_urltimes
            elif bands == "Both":
                Both.extend(uc_avg_val)
                Both_bytes.extend(rx_bytes_val)
                Both_speed.extend(rx_rate_val)
                Both_urltimes.extend(url_times)
                final_dict['Both']['dl_time'] = Both
                min_both.append(min(Both))
                final_dict['Both']['min'] = min_both
                max_both.append(max(Both))
                final_dict['Both']['max'] = max_both
                avg_both.append((sum(Both) / num_stations))
                final_dict['Both']['avg'] = avg_both
                final_dict['Both']['bytes_rd'] = Both_bytes
                final_dict['Both']['speed'] = Both_speed
                final_dict['Both']['url_times'] = Both_urltimes

            result_data = final_dict
            logger.info("HTTP Test Result {}".format(result_data))
            test_end = datetime.datetime.now().strftime("%b %d %H:%M:%S")
            logger.info("HTTP Test Finished at {}".format(test_end))
            s1 = test_time
            s2 = test_end  # for example
            FMT = '%b %d %H:%M:%S'
            test_duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
            logger.info("Total HTTP test duration: {}".format(test_duration))
            date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

            test_setup_info = {
                "AP Name": self.dut_model,
                "SSID": ssid,
                "Security": security,
                "No of Devices": len(http_sta_list),
                "File size": http_file_size,
                "File location": "/usr/local/lanforge/nginx/html",
                "Traffic Direction": "Download",
                "Traffic Duration ": self.http_test_duration
            }

            for i in result_data:
                self.dataset = result_data[i]['dl_time']
                self.dataset2 = result_data[i]['url_times']
                self.bytes_rd = result_data[i]['bytes_rd']
            self.dataset1 = [float(f"{(i / 1000000): .4f}") for i in self.bytes_rd]
            logger.info("data sets {} {}".format(self.dataset, self.dataset2))
            if self.band == "Both":
                for i in range(1, len(http_sta_list) * 2 + 1):
                    self.lis.append(i)
            else:
                for i in range(1, len(http_sta_list) + 1):
                    self.lis.append(i)

            if self.virtual:
                self.http_obj.station_list = [self.station_list]
                self.http_obj.devices = self.station_list
            if all_bands:
                band = ''
            else:
                band = '_' + self.band
            self.http_obj.generate_report(date, num_stations=len(http_sta_list), duration=self.http_test_duration,
                                        test_setup_info=test_setup_info, dataset=self.dataset, lis=self.lis,
                                        bands=Bands, threshold_2g="", threshold_5g="", threshold_both="",
                                        dataset1=self.dataset1,
                                        dataset2=self.dataset2, result_data=result_data, test_rig="", test_tag="",
                                        dut_hw_version="", dut_sw_version="", dut_model_num="", dut_serial_num="",
                                        test_id="", test_input_infor="", csv_outfile="",
                                        _results_dir_name=f'Webpage_Test_Report{band}',
                                        report_path=self.report_path)
            self.cleanup.layer4_endp_clean()
            self.http_test_status = True
            if(conn):
                conn.send([self.http_obj, self.dataset, self.dataset1, self.dataset2, self.bytes_rd, self.lis, True])
        except:
            traceback.print_exc()
            if(conn):
                conn.send(
                    [[], [], {}, {}, '', '', False]
                )

    def multicast_test(self, endp_types=None, mc_tos=None, side_a_min=0, side_b_min=0, side_a_pdu=0, side_b_pdu=0,
                       _multicast_test=multicast_test, all_bands=False, conn=None):
        try:
            # use for creating multicast dictionary
            if self.test_duration:
                self.multicast_test_duration = self.test_duration
            else:
                self.multicast_test_duration = self.multicast_test_duration
            self.endp_types = endp_types
            self.mc_tos = mc_tos

            if self.virtual:
                self.radio_name_list = [self.radio]
                self.num_sta_per_radio_list = [self.num_staions]
                self.ssid_list = [self.ssid]
                self.ssid_password_list = [self.passwd]
                self.ssid_security_list = [self.security]
                self.wifi_mode_list = [self.mode]
                self.station_lists = self.station_list

            test_rig = "CT-ID-004"
            test_tag = "test_l3"
            dut_hw_version = "AXE11000"
            dut_sw_version = "3.0.0.4.386_44266"
            dut_model_num = "1.0"
            dut_serial_num = "123456"
            test_id = "test l3"
            if all_bands:
                band = ''
            else:
                band = '_' + self.band
            report = lf_report_pdf.lf_report(_path=self.report_path, _results_dir_name=f"Multicast_Test{band}",
                                            _output_html=f"multicast_test{band}.html",
                                            _output_pdf=f"multicast_test{band}.pdf")
            kpi_path = self.report_path
            logger.info("Report and kpi_path :{kpi_path}".format(kpi_path=kpi_path))
            kpi_csv = lf_kpi_csv.lf_kpi_csv(_kpi_path=kpi_path,
                                            _kpi_test_rig=test_rig,
                                            _kpi_test_tag=test_tag,
                                            _kpi_dut_hw_version=dut_hw_version,
                                            _kpi_dut_sw_version=dut_sw_version,
                                            _kpi_dut_model_num=dut_model_num,
                                            _kpi_dut_serial_num=dut_serial_num,
                                            _kpi_test_id=test_id)

            # TODO: Add try/except if fails
            self.multicast_test_obj = multicast_test.L3VariableTime(endp_types=self.endp_types,
                                                                    args="",
                                                                    tos=self.mc_tos,
                                                                    side_b=self.upstream_port,
                                                                    side_a=None,
                                                                    radio_name_list=[],
                                                                    number_of_stations_per_radio_list=self.num_sta_per_radio_list,
                                                                    ssid_list=self.ssid_list,
                                                                    ssid_password_list=self.ssid_password_list,
                                                                    ssid_security_list=self.ssid_security_list,
                                                                    wifi_mode_list=self.wifi_mode_list,
                                                                    enable_flags_list=[],
                                                                    station_lists=self.station_lists,
                                                                    name_prefix="LT-",
                                                                    outfile="",
                                                                    reset_port_enable_list=[],
                                                                    reset_port_time_min_list=[],
                                                                    reset_port_time_max_list=[],
                                                                    side_a_min_rate=[side_a_min],
                                                                    side_b_min_rate=[side_b_min],
                                                                    side_a_min_pdu=[side_a_pdu],
                                                                    side_b_min_pdu=[side_b_pdu],
                                                                    rates_are_totals=True,
                                                                    mconn=1,
                                                                    attenuators=[],
                                                                    atten_vals=[-1],
                                                                    number_template="00",
                                                                    test_duration=str(self.multicast_test_duration) + "s",
                                                                    polling_interval="5s",
                                                                    lfclient_host=self.host,
                                                                    lfclient_port=self.port,
                                                                    debug=True,
                                                                    kpi_csv=kpi_csv,
                                                                    no_cleanup=True,
                                                                    use_existing_station_lists=True,
                                                                    existing_station_lists=self.user_query[0] if self.real else self.station_lists,
                                                                    wait_for_ip_sec="120s",
                                                                    ap_read=False,
                                                                    ap_module=None,
                                                                    ap_test_mode=True,
                                                                    ap_ip="",
                                                                    ap_user="lanforge",
                                                                    ap_passwd="lanforge",
                                                                    ap_scheme="serial",
                                                                    ap_serial_port='/dev/ttyUSB0',
                                                                    ap_ssh_port='1025',
                                                                    ap_telnet_port='23',
                                                                    ap_serial_baud="115200",
                                                                    ap_if_2g="wl0",
                                                                    ap_if_5g="wl1",
                                                                    ap_if_6g="wl2",
                                                                    ap_report_dir="",
                                                                    ap_file=None,
                                                                    ap_band_list=['2g', '5g', '6g'],
                                                                    key_mgmt_list=[],
                                                                    pairwise_list=[],
                                                                    group_list=[],
                                                                    psk_list=[],
                                                                    wep_key_list=[],
                                                                    ca_cert_list=[],
                                                                    eap_list=[],
                                                                    identity_list=[],
                                                                    anonymous_identity_list=[],
                                                                    phase1_list=[],
                                                                    phase2_list=[],
                                                                    passwd_list=[],
                                                                    pin_list=[],
                                                                    pac_file_list=[],
                                                                    private_key_list=[],
                                                                    pk_password_list=[],
                                                                    hessid_list=[],
                                                                    realm_list=[],
                                                                    client_cert_list=[],
                                                                    imsi_list=[],
                                                                    milenage_list=[],
                                                                    domain_list=[],
                                                                    roaming_consortium_list=[],
                                                                    venue_group_list=[],
                                                                    network_type_list=[],
                                                                    ipaddr_type_avail_list=[],
                                                                    network_auth_type_list=[],
                                                                    anqp_3gpp_cell_net_list=[],
                                                                    ieee80211w_list=[],
                                                                    interopt_mode=True)
            if self.real:
                if self.user_query[0]:
                    logger.info("No station pre clean up any existing cxs on LANforge")
                else:
                    logger.info("clean up any existing cxs on LANforge")
                    self.multicast_test_obj.pre_cleanup()
            # cleaning the existing layer4 endpoints
            self.cleanup.layer3_endp_clean()

            logger.info("create stations or use passed in station_list, build the test")
            # building the endpoints
            self.multicast_test_obj.build()
            if not self.multicast_test_obj.passes():
                logger.critical("build step failed.")
                logger.critical(self.multicast_test_obj.get_fail_message())
                exit(1)
            logger.info("Start the test and run for a duration")
            # TODO: Check return value of start()
            self.multicast_test_obj.start(False)
            csv_results_file = self.multicast_test_obj.get_results_csv()
            report.set_title("Multicast Test")
            report.build_banner_cover()
            report.start_content_div2()
            # set dut information for reporting
            self.multicast_test_obj.set_dut_info(dut_model_num=dut_model_num, dut_hw_version=dut_hw_version,
                                                dut_sw_version=dut_sw_version, dut_serial_num=dut_serial_num)
            self.multicast_test_obj.set_report_obj(report=report)
            # generate report
            self.multicast_test_obj.generate_report()
            # generate html and pdf
            report.write_report_location()
            report.write_html_with_timestamp()
            report.write_index_html()
            if platform.system() == 'Linux':
                report.write_pdf_with_timestamp(_page_size='A3', _orientation='Landscape')

            if not self.multicast_test_obj.passes():
                logger.warning("Test Ended: There were Failures in multicast test.")
                logger.warning(self.multicast_test_obj.get_fail_message())
            self.cleanup.layer3_endp_clean()
            if self.multicast_test_obj.passes():
                logger.info("Full test PASSED, All connections increased rx bytes")
            tos_list = ['VI', 'VO', 'BK', 'BE']
            for tos in tos_list:
                if(tos != mc_tos):
                    self.multicast_test_obj.client_dict_A[tos]['ul_A'] = None
                    self.multicast_test_obj.client_dict_A[tos]['dl_A'] = None

                    self.multicast_test_obj.client_dict_B[tos]['ul_B'] = None
                    self.multicast_test_obj.client_dict_B[tos]['dl_B'] = None
                    
            self.multicast_test_status = True
            if(conn):
                conn.send(
                    [
                        self.multicast_test_obj.client_dict_A,
                        self.multicast_test_obj.client_dict_B,
                        True
                    ]
                )
        except:
            traceback.print_exc()
            if(conn):
                conn.send(
                    [
                        [],
                        [],
                        False
                    ]
                )

    def generate_all_report(self):
        logger.info("To generate the Mixed Traffic report with all tests")
        self.lf_report_mt.set_title("Mixed Traffic Test ({})".format(['Parallel' if self.parallel else 'Serial'][0]))
        self.lf_report_mt.build_banner()
        virtual_sta_count = len(self.station_list)
        windows_count = self.base_interop_profile.windows
        linux_count = self.base_interop_profile.linux
        mac_count = self.base_interop_profile.mac
        android_count = self.base_interop_profile.android
        test_setup_info = {
            "DUT Model": self.dut_model,
            "DUT Firmware": self.dut_firmware,
            "SSID": self.ssid,
            "Security": self.security,
            "No of Devices": f"{len(self.user_query[0]) if self.real else len(self.station_list)} (Virtual Clients: {virtual_sta_count}, Windows: {windows_count}, Linux: {linux_count}, Mac: {mac_count}, Android: {android_count})",
            "Test Duration (HH:MM:SS)": self.time_formate}
        self.lf_report_mt.set_table_title("Test Setup Information")
        self.lf_report_mt.build_table_title()
        self.lf_report_mt.test_setup_table(test_setup_data=test_setup_info, value="Overall Setup Info For all Tests")
        # setting object for the mixed traffic
        self.lf_report_mt.set_obj_html(_obj_title="Objective",
                                       _obj="The  Candela  mixed  traffic  test  is  designed  to  measure  the  access  "
                                            "point  performance  andstability  by  running  multiple  traffic  on  real  "
                                            "clients  like  Android,  Linux,  Windows,  and  IOSconnected  to  the  access  "
                                            "point.  This  test  allows  the  user  to  choose  multiple  types  of  "
                                            "traffic  likeclient   capacity   test,   web   browser   test,   video   "
                                            "streaming   test   ping   test.   Along   with   theperformance measurements "
                                            "are client connection times, Station 4-Way Handshake time, DHCPtimes, "
                                            "and more. The expected behavior is for the AP to be able to handle all types "
                                            "of traffic onthe several stations (within the limitations of the AP specs) "
                                            "and Make sure all clients can run alltypes of traffic.")
        self.lf_report_mt.build_objective()
        self.lf_report_mt.set_table_title("Traffic Details")
        self.lf_report_mt.build_table_title()
        test_duration = {'1': "", '2': "", '3': "", '4': "", '5': ""}
        ping_test_status = ''
        qos_test_status = ''
        ftp_test_status = ''
        http_test_status = ''
        multicast_test_status = ''
        if self.tests:
            for test_option in self.tests:
                if test_option == '1':
                    if self.test_duration:
                        self.test_duration1 = self.convert_seconds(self.test_duration)
                    else:
                        self.test_duration1 = self.convert_seconds(self.ping_test_duration)
                    
                    if(self.ping_test_status):
                        ping_test_status = 'Executed'
                    else:
                        ping_test_status = 'Not Executed'

                if test_option == '2':
                    if self.test_duration:
                        if self.qos_serial_run:
                            self.test_duration1 = self.convert_seconds(self.test_duration * len(self.qos_tos_list))
                        else:
                            self.test_duration1 = self.convert_seconds(self.test_duration)
                    else:
                        if self.qos_serial_run:
                            self.test_duration1 = self.convert_seconds(self.qos_test_duration * len(self.qos_tos_list))
                        else:
                            self.test_duration1 = self.convert_seconds(self.qos_test_duration)
                    
                    if(self.qos_test_status):
                        qos_test_status = 'Executed'
                    else:
                        qos_test_status = 'Not Executed'

                if test_option == '3':
                    if self.test_duration:
                        self.test_duration1 = self.convert_seconds(self.test_duration)
                    else:
                        self.test_duration1 = self.convert_seconds(self.ftp_test_duration)

                    if(self.ftp_test_status):
                        ftp_test_status = 'Executed'
                    else:
                        ftp_test_status = 'Not Executed'

                if test_option == '4':
                    if self.test_duration:
                        self.test_duration1 = self.convert_seconds(self.test_duration)
                    else:
                        self.test_duration1 = self.convert_seconds(self.http_test_duration)

                    if(self.http_test_status):
                        http_test_status = 'Executed'
                    else:
                        http_test_status = 'Not Executed'

                if test_option == '5':
                    if self.test_duration:
                        self.test_duration1 = self.convert_seconds(self.test_duration)
                    else:
                        self.test_duration1 = self.convert_seconds(self.multicast_test_duration)

                    if(self.multicast_test_status):
                        multicast_test_status = 'Executed'
                    else:
                        multicast_test_status = 'Not Executed'  
                test_duration[test_option] = self.test_duration1 

            df = pd.DataFrame({
                                "Sno": [1, 2, 3, 4, 5],
                                "Test Cases": ['Ping Test', 'Quality Of Service(QOS) Test {}'.format(self.qos_tos_list),
                                                'FTP Test', 'HTTP Test', 'Multicast Test'],
                                "Test Duration ": [test_duration['1'], test_duration['2'], test_duration['3'],
                                                    test_duration['4'], test_duration['5']],
                                "Test Status": [ping_test_status, qos_test_status, ftp_test_status, http_test_status, multicast_test_status]
                            })
            self.lf_report_mt.set_table_dataframe(df)
            self.lf_report_mt.build_table()

            if "1" in self.tests and self.ping_test_status:
                # 1.Ping test reporting in mixed traffic
                self.lf_report_mt.set_obj_html(_obj_title="1. Ping Test", _obj="")
                self.lf_report_mt.build_objective()
                self.lf_report_mt.set_table_title("Test Configuration")
                self.lf_report_mt.build_table_title()
                ping_test_config_df = {"IP / Website": self.target}
                self.lf_report_mt.test_setup_table(test_setup_data=ping_test_config_df, value="Test Setup Information")
                self.lf_report_mt.set_table_title('Packets sent vs packets received vs packets dropped')
                self.lf_report_mt.build_table_title()
                x_fig_size = 15
                y_fig_size = len(self.ping_test_obj.device_names) * .5 + 4
                graph = lf_graph.lf_bar_graph_horizontal(
                    _data_set=[self.ping_test_obj.packets_dropped, self.ping_test_obj.packets_received, self.ping_test_obj.packets_sent],
                    _xaxis_name='Packets Count',
                    _yaxis_name='Wireless Clients',
                    _label=['Packets Loss', 'Packets Received', 'Packets Sent'],
                    _graph_image_name='Packets sent vs received vs dropped',
                    _yaxis_label=self.ping_test_obj.report_names,
                    _yaxis_categories=self.ping_test_obj.report_names,
                    _yaxis_step=1,
                    _yticks_font=8,
                    _graph_title='Packets sent vs received vs dropped',
                    _title_size=16,
                    _color=['lightgrey', 'orange', 'steelblue'],
                    _color_edge=['black'],
                    _bar_height=0.15,
                    _figsize=(x_fig_size, y_fig_size),
                    _legend_loc="best",
                    _legend_box=(1.0, 1.0),
                    _dpi=96,
                    _show_bar_value=False,
                    _enable_csv=True,
                    _color_name=['lightgrey', 'orange', 'steelblue'])
                graph_png = graph.build_bar_graph_horizontal()
                logger.info('Ping Test Graph-1: {}'.format(graph_png))
                self.lf_report_mt.set_graph_image(graph_png)
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.set_csv_filename(graph_png)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.build_graph()
                dataframe1 = pd.DataFrame({
                    'Wireless Client': self.ping_test_obj.device_names,
                    'MAC': self.ping_test_obj.device_mac,
                    'Channel': self.ping_test_obj.device_channels,
                    'SSID': self.ping_test_obj.device_ssid,
                    'Mode': self.ping_test_obj.device_modes,
                    'Packets Sent': self.ping_test_obj.packets_sent,
                    'Packets Received': self.ping_test_obj.packets_received,
                    'Packets Loss': self.ping_test_obj.packets_dropped})
                self.lf_report_mt.set_table_dataframe(dataframe1)
                self.lf_report_mt.build_table()
                self.lf_report_mt.set_table_title('Ping Latency Graph')
                self.lf_report_mt.build_table_title()
                graph = lf_graph.lf_bar_graph_horizontal(
                    _data_set=[self.ping_test_obj.device_min, self.ping_test_obj.device_avg,
                               self.ping_test_obj.device_max],
                    _xaxis_name='Time (ms)',
                    _yaxis_name='Wireless Clients',
                    _label=['Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                    _graph_image_name='Ping Latency per client',
                    _yaxis_label=self.ping_test_obj.report_names,
                    _yaxis_categories=self.ping_test_obj.report_names,
                    _yaxis_step=1,
                    _yticks_font=8,
                    _graph_title='Ping Latency per client',
                    _title_size=16,
                    _color=['lightgrey', 'orange', 'steelblue'],
                    _color_edge='black',
                    _bar_height=0.15,
                    _figsize=(x_fig_size, y_fig_size),
                    _legend_loc="best",
                    _legend_box=(1.0, 1.0),
                    _dpi=96,
                    _show_bar_value=False,
                    _enable_csv=True,
                    _color_name=['lightgrey', 'orange', 'steelblue'])
                graph_png = graph.build_bar_graph_horizontal()
                logger.info('Ping Test Graph-2: {}'.format(graph_png))
                self.lf_report_mt.set_graph_image(graph_png)
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.set_csv_filename(graph_png)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.build_graph()
                dataframe2 = pd.DataFrame({
                    'Wireless Client': self.ping_test_obj.device_names,
                    'MAC': self.ping_test_obj.device_mac,
                    'Channel': self.ping_test_obj.device_channels,
                    'SSID': self.ping_test_obj.device_ssid,
                    'Mode': self.ping_test_obj.device_modes,
                    'Min Latency (ms)': self.ping_test_obj.device_min,
                    'Average Latency (ms)': self.ping_test_obj.device_avg,
                    'Max Latency (ms)': self.ping_test_obj.device_max})
                self.lf_report_mt.set_table_dataframe(dataframe2)
                self.lf_report_mt.build_table()
            if "2" in self.tests and self.qos_test_status:
                # 2.QOS test reporting in mixed traffic
                self.lf_report_mt.set_obj_html(_obj_title="2. Quality Of Service(QOS) Test", _obj="")
                self.lf_report_mt.build_objective()
                self.lf_report_mt.set_table_title("Test Configuration")
                self.lf_report_mt.build_table_title()
                qos_obj = None
                if self.real:
                    qos_obj = self.qos_test_obj
                if self.virtual:
                    qos_obj = self.throughput_qos_obj
                qos_test_config_df = {
                    "Protocol": (qos_obj.traffic_type.strip("lf_")).upper(),
                    "Traffic Direction": qos_obj.direction,
                    "Security": self.security,
                    "TOS": self.qos_tos_list,
                    "Per TOS Load": self.load}
                self.lf_report_mt.test_setup_table(test_setup_data=qos_test_config_df, value="Test Setup Information")
                if self.qos_serial_run:
                    result_list = [self.result1, self.result2, self.result3, self.result4]
                    for res, tos in zip(result_list, self.qos_tos_list):
                        if res:
                            self.data_set, self.load, res1 = qos_obj.generate_graph_data_set(res)
                            qos_obj.tos = tos
                            qos_obj.generate_individual_graph(res1, self.lf_report_mt)
                else:
                    df_throughput = pd.DataFrame(self.res["throughput_table_df"])
                    self.lf_report_mt.set_table_dataframe(df_throughput)
                    self.lf_report_mt.set_table_title(
                        f"Overall {qos_obj.direction} Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
                    self.lf_report_mt.build_table_title()
                    graph = lf_graph.lf_bar_graph(_data_set=self.data_set,
                                                  _xaxis_name="Load per Type of Service",
                                                  _yaxis_name="Throughput (Mbps)",
                                                  _xaxis_categories=["BK,BE,VI,VO"],
                                                  _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                                  _graph_image_name=f"tos_",
                                                  _label=["BK", "BE", "VI", "VO"],
                                                  _xaxis_step=1,
                                                  _graph_title=f"Overall {qos_obj.direction} throughput – BK,BE,VO,VI traffic streams",
                                                  _title_size=16,
                                                  _color=['orange', 'lightcoral', 'steelblue', 'lightgrey'],
                                                  _color_edge='black',
                                                  _bar_width=0.15,
                                                  _figsize=(18, 6),
                                                  _legend_loc="best",
                                                  _legend_box=(1.0, 1.0),
                                                  _dpi=96,
                                                  _show_bar_value=True,
                                                  _enable_csv=True,
                                                  _color_name=['orange', 'lightcoral', 'steelblue', 'lightgrey'])
                    graph_png = graph.build_bar_graph()
                    logger.info("QOS test name of the overall graph : {}".format(graph_png))
                    self.lf_report_mt.set_graph_image(graph_png)
                    self.lf_report_mt.move_graph_image()
                    self.lf_report_mt.set_csv_filename(graph_png)
                    self.lf_report_mt.move_csv_file()
                    self.lf_report_mt.build_graph()
                    qos_obj.generate_individual_graph(self.res, self.lf_report_mt)
            if "3" in self.tests and self.ftp_test_status:
                # 3.FTP test reporting in mixed traffic
                self.lf_report_mt.set_obj_html(_obj_title="3. File Transfer Protocol (FTP) Test", _obj="")
                self.lf_report_mt.build_objective()
                self.lf_report_mt.set_table_title("Test Configuration")
                self.lf_report_mt.build_table_title()
                ftp_test_config_df = {
                    "Traffic Direction": self.ftp_test_obj.direction,
                    "File Size": self.ftp_test_obj.file_size,
                    "File Location": "/home/lanforge"}
                self.lf_report_mt.test_setup_table(test_setup_data=ftp_test_config_df, value="Test Setup Information")
                self.lf_report_mt.set_obj_html(_obj_title=f"No.of times file {self.ftp_test_obj.direction}",
                                               _obj=f"The below graph represents number of times a file {self.ftp_test_obj.direction} for each client"
                                                    f" (WiFi) traffic.  X-axis shows “No of times file {self.ftp_test_obj.direction}” and Y-axis shows "
                                                    f"“Client names“.")
                self.lf_report_mt.build_objective()
                sta_list = ""
                if self.real:
                    sta_list = self.user_query[1]
                elif self.virtual:
                    sta_list = self.station_list
                x_fig_size = 15
                y_fig_size = len(sta_list) * .5 + 4
                graph = lf_graph.lf_bar_graph_horizontal(_data_set=[self.ftp_test_obj.url_data],
                                                         _xaxis_name=f"No of times file {self.ftp_test_obj.direction}",
                                                         _yaxis_name="Client names",
                                                         _yaxis_categories=[i for i in sta_list],
                                                         _yaxis_label=[i for i in sta_list],
                                                         _yaxis_step=1,
                                                         _yticks_font=8,
                                                         _yticks_rotation=None,
                                                         _graph_title=f"No of times file {self.ftp_test_obj.direction} (Count)",
                                                         _title_size=16,
                                                         _figsize=(x_fig_size, y_fig_size),
                                                         _legend_loc="best",
                                                         _legend_box=(1.0, 1.0),
                                                         _color_name=['orange'],
                                                         _show_bar_value=True,
                                                         _enable_csv=True,
                                                         _graph_image_name="ftp_total-url", _color_edge=['black'],
                                                         _color=['orange'],
                                                         _label=[self.ftp_test_obj.direction])
                ftp_graph1 = graph.build_bar_graph_horizontal()
                logger.info("FTP Graph-1 Name: {}".format(ftp_graph1))
                self.lf_report_mt.set_graph_image(ftp_graph1)
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.set_csv_filename(ftp_graph1)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.build_graph()
                self.lf_report_mt.set_obj_html(_obj_title=f"Average time taken to {self.ftp_test_obj.direction} file ",
                                               _obj=f"The below graph represents average time taken to {self.ftp_test_obj.direction} for each client  "
                                                    f"(WiFi) traffic.  X-axis shows “Average time taken to {self.ftp_test_obj.direction} a file ” and Y-axis shows “Client names“.")
                self.lf_report_mt.build_objective()
                graph = lf_graph.lf_bar_graph_horizontal(_data_set=[self.ftp_test_obj.uc_avg],
                                                         _xaxis_name=f"Average time taken to {self.ftp_test_obj.direction} file in ms",
                                                         _yaxis_name="Client names",
                                                         _yaxis_categories=[i for i in sta_list],
                                                         _yaxis_label=[i for i in sta_list],
                                                         _yaxis_step=1,
                                                         _yticks_font=8,
                                                         _yticks_rotation=None,
                                                         _graph_title=f"Average time taken to {self.ftp_test_obj.direction} file",
                                                         _title_size=16,
                                                         _figsize=(x_fig_size, y_fig_size),
                                                         _legend_loc="best",
                                                         _legend_box=(1.0, 1.0),
                                                         _color_name=['steelblue'],
                                                         _show_bar_value=True,
                                                         _enable_csv=True,
                                                         _graph_image_name="ftp_ucg-avg", _color_edge=['black'],
                                                         _color=['steelblue'],
                                                         _label=[self.ftp_test_obj.direction])
                ftp_graph2 = graph.build_bar_graph_horizontal()
                logger.info("FTP Graph-2 Name: {}".format(ftp_graph2))
                self.lf_report_mt.set_graph_image(ftp_graph2)
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.set_csv_filename(ftp_graph2)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.build_graph()
                self.lf_report_mt.set_table_title("Overall Results")
                self.lf_report_mt.build_table_title()
                dataframe = {
                    " Clients": sta_list,
                    " MAC ": self.ftp_test_obj.mac_id_list,
                    " Channel": self.ftp_test_obj.channel_list,
                    " SSID ": self.ftp_test_obj.ssid_list,
                    " Mode": self.ftp_test_obj.mode_list,
                    " No of times File downloaded ": self.ftp_test_obj.url_data,
                    " Time Taken to Download file (ms)": self.ftp_test_obj.uc_avg,
                    " Bytes-rd (Mega Bytes)" : self.ftp_test_obj.bytes_rd}
                dataframe1 = pd.DataFrame(dataframe)
                self.lf_report_mt.set_table_dataframe(dataframe1)
                self.lf_report_mt.build_table()
            if "4" in self.tests and self.http_test_status:
                # 4.Http test reporting in mixed traffic
                self.lf_report_mt.set_obj_html(_obj_title="4. Hyper Text Transfer Protocol (HTTP) Test", _obj="")
                self.lf_report_mt.build_objective()
                self.lf_report_mt.set_table_title("Test Configuration")
                self.lf_report_mt.build_table_title()
                http_test_config_df = {"Traffic Direction": "Download",
                                       "File Size": self.http_obj.file_size,
                                       "File location": "/usr/local/lanforge/nginx/html", }
                self.lf_report_mt.test_setup_table(test_setup_data=http_test_config_df, value="Test Setup Information")
                self.lf_report_mt.set_obj_html("No of times file Downloads",
                                               "The below graph represents number of times a file downloads for each client"
                                               ". X- axis shows “No of times file downloads and Y-axis shows "
                                               "Client names.")
                self.lf_report_mt.build_objective()
                http_graph1 = self.http_obj.graph_2(self.dataset2, lis=self.lis, bands=[self.band])
                logger.info("Http Graph-1 Name: {}".format(http_graph1))
                self.lf_report_mt.set_graph_image(http_graph1)
                self.lf_report_mt.set_csv_filename(http_graph1)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.build_graph()
                self.lf_report_mt.set_obj_html("Average time taken to download file ",
                                               "The below graph represents average time taken to download for each client  "
                                               ".  X- axis shows “Average time taken to download a file ” and Y-axis shows "
                                               "Client names.")
                self.lf_report_mt.build_objective()
                http_graph2 = self.http_obj.generate_graph(dataset=self.dataset, lis=self.lis, bands=[self.band])
                logger.info("Http Graph-2 Name: {}".format(http_graph2))
                self.lf_report_mt.set_graph_image(http_graph2)
                self.lf_report_mt.set_csv_filename(http_graph2)
                self.lf_report_mt.move_csv_file()
                self.lf_report_mt.move_graph_image()
                self.lf_report_mt.build_graph()
                self.lf_report_mt.set_table_title("Overall Results")
                self.lf_report_mt.build_table_title()
                dataframe = {
                    " Clients": self.user_query[1] if self.real else self.station_list,
                    " MAC ": self.user_query[2] if self.real else self.http_obj.macid_list,
                    " Channel": self.http_obj.channel_list,
                    " SSID ": self.http_obj.ssid_list,
                    " Mode": self.http_obj.mode_list,
                    " No of times File downloaded ": self.dataset2,
                    " Average time taken to Download file (ms)": self.dataset,
                    " Bytes-rd (Mega Bytes) " : self.dataset1}
                dataframe1 = pd.DataFrame(dataframe)
                self.lf_report_mt.set_table_dataframe(dataframe1)
                self.lf_report_mt.build_table()
            if "5" in self.tests and self.multicast_test_status:
                # 5.Multicast test reporting in mixed traffic
                self.lf_report_mt.set_obj_html(_obj_title="5. Multicast Test", _obj="")
                self.lf_report_mt.build_objective()
                self.lf_report_mt.set_table_title("Test Configuration")
                self.lf_report_mt.build_table_title()
                if self.multicast_endp_types == "mc_udp":
                    protocol = "UDP"
                elif self.multicast_endp_types == "mc_tcp":
                    protocol = "TCP"
                else:
                    protocol = ""
                tos_list = ['BK', 'BE', 'VI', 'VO']
                self.client_dict_A = self.multicast_test_obj.client_dict_A
                self.client_dict_B = self.multicast_test_obj.client_dict_B
                multicast_test_config_df = {"Protocol": protocol,
                                            "Type of Service (TOS)": self.multicast_tos,
                                            "Upstream Port": self.upstream_port,
                                            "Offered Load (Mbps)": int(self.client_dict_A['min_bps_b']) / 1000000}
                self.lf_report_mt.test_setup_table(test_setup_data=multicast_test_config_df, value="Test Setup Information")
                for tos in tos_list:
                    if self.client_dict_A[tos]["ul_A"] and self.client_dict_A[tos]["dl_A"]:
                        min_bps_a = self.client_dict_A["min_bps_a"]
                        min_bps_b = self.client_dict_A["min_bps_b"]

                        client_ul_A_data = []
                        client_dl_A_data = []
                        clients_list = []
                        client_names = []
                        endp_names = []
                        hw_versions = []
                        port_names = []
                        modes = []
                        mac_list = []
                        ssid_list = []
                        channel_list = []
                        per_client_download_rate = []
                        traffic_types = []
                        traffic_protocols = []
                        download_rx_drop_percentages = []
                        total_clients = 0
                        print(self.client_dict_A[tos]["clients_A"], len(self.client_dict_A[tos]["clients_A"]))
                        print(self.client_dict_A[tos]['labels'], len(self.client_dict_A[tos]['labels']))
                        for client_index in range(len(self.client_dict_A[tos]["clients_A"])):
                            if(self.client_dict_A[tos]["clients_A"][client_index].startswith('MLT')):
                                total_clients += 1
                                clients_list.append(self.client_dict_A[tos]["clients_A"][client_index])
                                client_names.append(self.client_dict_A[tos]['resource_alias_A'][client_index])
                                client_ul_A_data.append(self.client_dict_A[tos]["ul_A"][client_index])
                                client_dl_A_data.append(self.client_dict_A[tos]["dl_A"][client_index])
                                hw_versions.append(self.client_dict_A[tos]['resource_hw_ver_A'][client_index])
                                endp_names.append(self.client_dict_A[tos]["clients_A"][client_index])
                                port_names.append(self.client_dict_A[tos]['port_A'][client_index])
                                modes.append(self.client_dict_A[tos]['mode_A'][client_index])
                                mac_list.append(self.client_dict_A[tos]['mac_A'][client_index])
                                ssid_list.append(self.client_dict_A[tos]['ssid_A'][client_index])
                                channel_list.append(self.client_dict_A[tos]['channel_A'][client_index])
                                traffic_types.append(self.client_dict_A[tos]['traffic_type_A'][client_index])
                                traffic_protocols.append(self.client_dict_A[tos]['traffic_protocol_A'][client_index])
                                per_client_download_rate.append(self.client_dict_A[tos]['dl_A'][client_index])
                                download_rx_drop_percentages.append(self.client_dict_A[tos]['download_rx_drop_percent_A'][client_index])



                        dataset_list = [client_ul_A_data, client_dl_A_data]
                        bps_to_mbps_converter = 1000000
                        dataset_list = [[value / bps_to_mbps_converter for value in sublist] for sublist in dataset_list]
                        print("Report Dataset", dataset_list)
                        dataset_length = total_clients
                        x_fig_size = 15
                        y_fig_size = total_clients * .5 + 4

                        self.lf_report_mt.set_obj_html(
                            _obj_title=f"Individual throughput with intended load {int(min_bps_b) / 1000000} Mbps station for traffic {tos} (WiFi).",
                            _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                 f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “Throughput in Mbps”.")
                        self.lf_report_mt.build_objective()
                        graph = lf_graph.lf_bar_graph_horizontal(_data_set=dataset_list,
                                                                 _xaxis_name="Throughput in Mbps",
                                                                 _yaxis_name="Client names",
                                                                 _yaxis_categories=clients_list,
                                                                 _graph_image_name=f"{tos}_A",
                                                                 _label=self.client_dict_A[tos]['labels'],
                                                                 _color_name=self.client_dict_A[tos]['colors'],
                                                                 _color_edge=['black'],
                                                                 _graph_title=f"Individual {tos} client side traffic measurement - side a (downstream)",
                                                                 _title_size=10,
                                                                 _figsize=(x_fig_size, y_fig_size),
                                                                 _show_bar_value=True,
                                                                 _enable_csv=True,
                                                                 _text_font=8,
                                                                 _legend_loc="best",
                                                                 _legend_box=(1.0, 1.0))
                        graph_png = graph.build_bar_graph_horizontal()
                        logger.info("Multicast Test Graph Name: {}".format(graph_png))
                        self.lf_report_mt.set_graph_image(graph_png)
                        self.lf_report_mt.move_graph_image()
                        self.lf_report_mt.build_graph()
                        tos_dataframe_A = {
                            " Client Name ": client_names,
                            " Endp Name": endp_names,
                            " HW Version ": hw_versions,
                            " Port Name ": port_names,
                            " Mode ": modes,
                            " Mac ": mac_list,
                            " SSID ": ssid_list,
                            " Channel ": channel_list,
                            " Type of traffic ": traffic_types,
                            " Traffic Protocol ": traffic_protocols,
                            # " Offered Upload Rate Per Client": self.client_dict_A['min_bps_a'],
                            " Offered Download Rate Per Client (Mbps)": int(self.client_dict_A['min_bps_b']) / 1000000,
                            # " Upload Rate Per Client": self.client_dict_A[tos]['ul_A'],
                            " Download Rate Per Client (Mbps)": [value / 1000000 for value in per_client_download_rate],
                            " Download Drop Percentage (%)": download_rx_drop_percentages
                        }
                        print(tos_dataframe_A)
                        dataframe3 = pd.DataFrame(tos_dataframe_A)
                        self.lf_report_mt.set_table_dataframe(dataframe3)
                        self.lf_report_mt.build_table()
            overall_setup_info = {"contact": "support@candelatech.com"}
            self.lf_report_mt.test_setup_table(test_setup_data=overall_setup_info, value="Overall Info")
            self.lf_report_mt.build_custom()
            self.lf_report_mt.build_footer()
            self.lf_report_mt.write_html()
            self.lf_report_mt.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')


def main():
    help_summary = '''\
    Mixed traffic test is designed to measure the access point performance and stability by running multiple traffic
    on both virtual & real clients like Android, Linux, Windows, and IOS connected to the access point.
    This test allows the user to choose multiple types of traffic like client PING test, QOS test, FTP test, HTTP test,
    and multicast test.
    
    The test will create virtual stations, create CX based on the selected test, run traffic and generate a report.
    '''
    parser = argparse.ArgumentParser(
        prog='lf_mixed_traffic.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
                The Mixed Traffic Test is Used for running the different test in single test
                ''',
        description=''' 
NAME: lf_mixed_traffic.py

PURPOSE:
        Mixed traffic test is designed to measure the access point performance and stability by running multiple traffic
        on both virtual & real clients like Android, Linux, Windows, and IOS connected to the access point.
        This test allows the user to choose multiple types of traffic like client ping test, qos test, ftp test, http test,
        multicast test and run tests both serially and simultaneously.

EXAMPLE:

        # CLI for Mixed Traffic Test: Run with Real Clients without connecting to a specified SSID

            python3 lf_mixed_traffic.py --mgr 192.168.212.100 --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup

        # CLI for Mixed Traffic Test: Run with Real Clients with parallel execution of tests

            python3 lf_mixed_traffic.py --mgr 192.168.212.100
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI"
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s
            --pre_cleanup --parallel

        # CLI for Mixed Traffic Test: Run with Real Clients on 2.4GHz & 5GHz Bands, Single Iteration per Band.
        
            python3 lf_mixed_traffic.py --mgr 192.168.212.100 
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5 
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5 
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1 
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI" 
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s 
            --pre_cleanup
            
        # CLI for Mixed Traffic Test: Run on 2.4GHz & 5GHz Bands Simultaneously with Real Clients in a Single Iteration.
        
            python3 lf_mixed_traffic.py --mgr 192.168.212.100 
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5 
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5 
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1 
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI" 
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --real --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s 
            --all_bands --pre_cleanup
            
        # CLI for Mixed Traffic Test: Run with Virtual Clients on 2.4GHz & 5GHz Bands, Single Iteration per Band.
        
            python3 lf_mixed_traffic.py --mgr 192.168.212.100 
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5 
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5 
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1 
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI" 
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --virtual --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s 
            --pre_cleanup
            
        # CLI for Mixed Traffic Test: Run on 2.4GHz & 5GHz Bands Simultaneously with Virtual Clients in a Single Iteration.
        
            python3 lf_mixed_traffic.py --mgr 192.168.212.100 
            --twog_ssid NETGEAR-2G --twog_passwd Password@123 --twog_security wpa2 --twog_radio wiphy0 --twog_num_stations 5 
            --fiveg_ssid NETGEAR-5G --fiveg_passwd Password@123 --fiveg_security wpa2 --fiveg_radio wiphy1 --fiveg_num_stations 5 
            --band 2.4G,5G --tests 1 2 3 4 5 --target 10.0.0.10 --ping_interval 5 --upstream_port 1.1.eth1 
            --side_b_min_bps 3000000 --side_a_min 1000000 --side_b_min 1000000 --traffic_type lf_tcp --tos "VI" 
            --ftp_file_sizes 10MB --http_file_size 5MB --direction Download --mc_tos "BE" --virtual --qos_serial --mixed_traffic_loop 1
            --ping_test_duration 1m --qos_test_duration 30s --ftp_test_duration 30s --http_test_duration 30s --multicast_test_duration 30s 
            --all_bands --pre_cleanup

SCRIPT_CLASSIFICATION:  Multiples Tests, Creation, Report Generation (Both individual & Overall)

SCRIPT_CATEGORIES:  Performance, Functional

NOTES:
        The primary goal of the script is to execute a series of tests and group their individual test reports into a unified report.

STATUS: Functional

VERIFIED_ON: 30-Apr-2024
             GUI Version:  5.4.8
             Build Date :  Sun Apr 21 01:42:42 PM PDT 2024
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
''')

    required = parser.add_argument_group('Required arguments to run lf_mixed_traffic.py')
    optional = parser.add_argument_group('Optional arguments to run lf_mixed_traffic.py')
    required.add_argument('--mgr', help='hostname for where LANforge GUI is running',
                          default='localhost')
    required.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on',
                          default=8080)
    # required.add_argument('--clients_type',
    #                       help='Enter the type of clients on which the test is to be run. Example: "Virtual","Real"')
    required.add_argument('--real', help='Enable this flag to run the tests on real clients', action='store_true')
    required.add_argument('--virtual', help='Enable this flag to run the tests on virtual clients', action='store_true')
    required.add_argument('--tests', help='To enable Tests \n'
                                          '1 --> Ping Test \n'
                                          '2 --> Qos Test \n'
                                          '3 --> FTP Test \n'
                                          '4 --> HTTP Test \n'
                                          '5 --> Multicast Test \n'
                                          'eg: --tests 1 2 3 4 5', nargs="+", default=["1 2 3 4 5"])
    optional.add_argument('--parallel', action='store_true',
                          help='Use --parallel to run the all the traffics (ftp,http,qos,ping,multicast..) simultaeneously')
    # virtual stations
    # optional.add_argument('--start_id',
    #                       help='Specify the station starting id \n e.g: --start_id <value> default 0',
    #                       default=0)
    optional.add_argument('--upstream_port',
                          help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1',
                          default='eth1')
    optional.add_argument('--server_ip', help='specify the server ip to login to the app',
                          default='10.0.0.10')
    # optional.add_argument('--num_stations', type=int, help='number of virtual stations', default=0)
    # optional.add_argument('--mode', help='Mode for your station (as a number)', default=0)
    optional.add_argument('--lf_username', help='Specify the lanforge ssh user name', default="lanforge")
    optional.add_argument('--lf_password', help='Specify the lanforge ssh password', default="lanforge")
    optional.add_argument('--twog_radio', type=str, help='specify radio for 2.4G clients [default = wiphy1]',
                          default='wiphy1')
    optional.add_argument('--fiveg_radio', type=str, help='specify radio for 5G client [default = wiphy0]',
                          default='wiphy0')
    optional.add_argument('--sixg_radio', type=str, help='specify radio for 6G clients [default = wiphy2]',
                          default='wiphy2')
    optional.add_argument('--twog_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 2.4G clients',
                          default='')
    optional.add_argument('--twog_ssid', help='WiFi SSID for script object to associate for 2.4G clients', default='')
    optional.add_argument('--twog_passwd', help='WiFi passphrase/password/key for 2.4G clients', default='')
    optional.add_argument('--twog_mode', help='Mode for your twog station (as a number)', default=0)
    optional.add_argument('--twog_num_stations', type=int, help='number of virtual stations for twog band', default=0)
    optional.add_argument('--twog_start_id', help='Specify the station starting id for twog stations.\n e.g: '
                                                  '--twog_start_id <value> default 2000', default=2000)

    optional.add_argument('--fiveg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 5G clients',
                          default='')
    optional.add_argument('--fiveg_ssid', help='WiFi SSID for script object to associate for 5G clients', default='')
    optional.add_argument('--fiveg_passwd', help='WiFi passphrase/password/key for 5G clients', default='')
    optional.add_argument('--fiveg_mode', help='Mode for your fiveg station (as a number)', default=0)
    optional.add_argument('--fiveg_num_stations', type=int, help='number of virtual stations for fiveg band', default=0)
    optional.add_argument('--fiveg_start_id', help='Specify the station starting id for fiveg stations.\n e.g: '
                                                   '--fiveg_start_id <value> default 5000', default=5000)

    optional.add_argument('--sixg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 6G clients',
                          default='')
    optional.add_argument('--sixg_ssid', help='WiFi SSID for script object to associate for 6G clients', default='')
    optional.add_argument('--sixg_passwd', help='WiFi passphrase/password/key for 6G clients', default='')
    optional.add_argument('--sixg_mode', help='Mode for your sixg station (as a number)', default=0)
    optional.add_argument('--sixg_num_stations', type=int, help='number of virtual stations for sixg band', default=0)
    optional.add_argument('--sixg_start_id', help='Specify the station starting id for sixg stations.\n e.g: '
                                                  '--sixg_start_id <value> default 6000', default=6000)

    optional.add_argument('--dut_model', help='Specify the Dut Name. eg: --dut_model EAP101', default="Test_DUT")
    optional.add_argument('--dut_firmware', help='Specify the dut firmware. eg: --dut_firmware V1.0.0.10',
                          default="NA")
    optional.add_argument('--mixed_traffic_loop',type=int,help='Specify the number of times mixed traffic test should run',default=1)

    # ping test args
    required.add_argument('--target', type=str, help='Target URL for ping test', default='192.168.1.3')
    required.add_argument('--ping_interval', type=str, help='Interval (in seconds) between the echo requests',
                          default='1')

    optional.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', default='lf_udp')
    optional.add_argument('--qos_serial', help='Use --qos_serial to run the qos test one after another.', action='store_true')
    optional.add_argument('--test_duration', help='--test_duration sets the duration for all the tests', default="")
    optional.add_argument('--ping_test_duration', help='--test_duration sets the duration for ping tests', default="1m")
    optional.add_argument('--qos_test_duration', help='--test_duration sets the duration for qos tests', default="3m")
    optional.add_argument('--ftp_test_duration', help='--test_duration sets the duration for ftp tests', default="3m")
    optional.add_argument('--http_test_duration', help='--test_duration sets the duration for http tests', default="3m")
    optional.add_argument('--multicast_test_duration', help='--test_duration sets the duration for multicast tests', default="5m")
    # qos args
    optional.add_argument('--tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ', default="VO")
    optional.add_argument('--side_a_min', help='Endpoint-a Min Cx Rate', default=6200000)
    optional.add_argument('--side_a_max', help='Endpoint-a Max CX Rate', default=0)
    optional.add_argument('--side_b_min', help='Endpoint-b Min CX Rate', default=6200000)
    optional.add_argument('--side_b_max', help='Endpoint-b Max CX Rate', default=0)
    #ftp test args
    optional.add_argument('--band', nargs="+", help='select bands for virtual clients Example : "5G","2.4G" ',
                          default=["5G"])
    optional.add_argument('--use_default_config',
                        action='store_true',
                        help='specify this flag if wanted to proceed with existing Wi-Fi configuration of the devices')
    required.add_argument('--direction', nargs="+", help='Enter the traffic direction. Example : "Download","Upload"',
                          default=["Download", "Upload"])
    required.add_argument('--ftp_file_sizes', nargs="+", help='File Size Example : "1000MB"',
                          default=["2MB", "500MB", "1000MB"])
    # http test args
    parser.add_argument('--target_per_ten', help='number of request per 10 minutes', default=100)
    parser.add_argument('--http_file_size', type=str, help='specify the size of file you want to download',
                        default='5MB')
    # multicast test args
    parser.add_argument('--mc_traffic_type', help='multicast tos', type=str, default="mc_udp")
    parser.add_argument('--mc_tos', help='multicast tos', type=str, default="BE")
    parser.add_argument('--side_a_min_bps',
                        help='--side_a_min_bps, requested downstream min tx rate, comma separated list for multiple iterations.  Default 256k',
                        default="0")
    parser.add_argument('--side_a_min_pdu',
                        help='--side_a_min_pdu, downstream pdu size, comma separated list for multiple iterations.  Default MTU',
                        default="MTU")
    parser.add_argument('--side_b_min_bps',
                        help='--side_b_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000',
                        default="256000")
    parser.add_argument('--side_b_min_pdu',
                        help='--side_b_min_pdu, upstream pdu size, comma separated list for multiple iterations. Default MTU',
                        default="MTU")
    parser.add_argument('--polling_interval', help="--polling_interval <seconds>", default='60s')

    parser.add_argument('--pre_cleanup', help='Use this if you want to clean Generic, Layer-3, L3 Endps &'
                                              ' Layer 4-7 tabs data', default=None, action="store_true")

    parser.add_argument('--all_bands', help='to run the tests with respective bands',default=None,
                        action="store_true")

    # logging configuration
    optional.add_argument("--lf_logger_config_json",
                          help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    # checking multicast test tos separation
    if ',' in args.mc_tos:
        print(argparse.ArgumentTypeError(
            "--mc_tos <input> should not contain single value not multiple values. eg : --mc_tos \"BE"))
        exit(0)

    radio,ssid,security,password = [],[],[],[]
    Bands = args.band[0].split(',')

    # checking all required arguments for wifi config
    if(args.use_default_config == False):
        if('2.4G' in Bands):
            if(args.twog_ssid is None):
                print('--twog_ssid is required')
                exit(1)
            if(args.twog_passwd is None):
                print('--twog_passwd is required')
                exit(1)
            if(args.twog_security is None):
                print('--twog_security is required')
                exit(1)
            # if(args.virtual):
            #     if(args.twog_radio is None):
            #         print('--twog_radio is required')
            #         exit(1)
            #     if(args.twog_num_stations is None):
            #         print('--twog_num_stations is required')
            #         exit(1)
        if('5G' in Bands):
            if(args.fiveg_ssid is None):
                print('--fiveg_ssid is required')
                exit(1)
            if(args.fiveg_passwd is None):
                print('--fiveg_passwd is required')
                exit(1)
            if(args.fiveg_security is None):
                print('--fiveg_security is required')
                exit(1)
            # if(args.virtual):
            #     if(args.fiveg_radio is None):
            #         print('--fiveg_radio is required')
            #         exit(1)
            #     if(args.fiveg_num_stations is None):
            #         print('--fiveg_num_stations is required')
            #         exit(1)
        if('6G' in Bands):
            if(args.sixg_ssid is None):
                print('--sixg_ssid is required')
                exit(1)
            if(args.sixg_passwd is None):
                print('--sixg_passwd is required')
                exit(1)
            if(args.sixg_security is None):
                print('--sixg_security is required')
                exit(1)
            # if(args.virtual):
            #     if(args.sixg_radio is None):
            #         print('--sixg_radio is required')
            #         exit(1)
            #     if(args.sixg_num_stations is None):
            #         print('--sixg_num_stations is required')
            #         exit(1)
    configure = not args.use_default_config
    # Virtual stations setting up the start_id, num_sta, sta_list
    # num_sta = args.num_stations
    station_list = []
    
    #for creating directory and placing reports
    parent_dir = os.getcwd()
    directory = datetime.datetime.now().strftime("%b %d %H:%M:%S") + str(' mixed_traffic_test')
    overall_path = os.path.join(parent_dir,directory)
    os.mkdir(overall_path)
    mixed_obj = Mixed_Traffic(host=args.mgr,
                              port=args.mgr_port,
                              lf_username=args.lf_username,
                              lf_password=args.lf_password,
                              real_client=args.real,
                              virtual_client=args.virtual,
                              selected_test_list=args.tests,
                              server_ip=args.server_ip,

                              twog_ssid=args.twog_ssid,
                              fiveg_ssid=args.fiveg_ssid,
                              sixg_ssid=args.sixg_ssid,
                              twog_password=args.twog_passwd,
                              fiveg_password=args.fiveg_passwd,
                              sixg_password=args.sixg_passwd,
                              twog_security=args.twog_security,
                              fiveg_security=args.fiveg_security,
                              sixg_security=args.sixg_security,

                              twog_radio=args.twog_radio,
                              fiveg_radio=args.fiveg_radio,
                              sixg_radio=args.sixg_radio,

                              twog_num_stations=args.twog_num_stations,
                              fiveg_num_stations=args.fiveg_num_stations,
                              sixg_num_stations=args.sixg_num_stations,

                              twog_start_id=args.twog_start_id,
                              fiveg_start_id=args.fiveg_start_id,
                              sixg_start_id=args.sixg_start_id,

                              twog_mode=args.twog_mode,
                              fiveg_mode=args.fiveg_mode,
                              sixg_mode=args.sixg_mode,

                              selected_bands=Bands,
                              number_template="",
                              upstream_port=args.upstream_port,
                              qos_tos_list=args.tos,
                              dut_model=args.dut_model,
                              dut_firmware=args.dut_firmware,
                              qos_serial=args.qos_serial,
                              test_duration=args.test_duration,
                              ping_test_duration=args.ping_test_duration,
                              qos_test_duration=args.qos_test_duration,
                              ftp_test_duration=args.ftp_test_duration,
                              http_test_duration=args.http_test_duration,
                              multicast_test_duration=args.multicast_test_duration,
                              configure=configure,
                              parallel=args.parallel,
                              
                              target=args.target,
                              multicast_endp_types=args.mc_traffic_type,
                              multicast_tos=args.mc_tos,
                              # path=path
                              )
    # pre-cleaning & creating / selecting clients for both real and virtual
    twog_selected_devices, fiveg_selected_devices, sixg_selected_devices = None, None, None
    if args.pre_cleanup:
        mixed_obj.pre_cleanup()
    if args.real:
        if(configure):
            selected_serial_list = mixed_obj.selecting_devices_from_available()
            if selected_serial_list:
                twog_selected_devices = selected_serial_list[0] if len(selected_serial_list) > 0 else None
                fiveg_selected_devices = selected_serial_list[1] if len(selected_serial_list) > 1 else None
                sixg_selected_devices = selected_serial_list[2] if len(selected_serial_list) > 2 else None
            if args.all_bands:
                set_2g = set(twog_selected_devices)
                set_5g = set(fiveg_selected_devices)
                set_6g = set(sixg_selected_devices)
                if set_2g & set_5g or set_2g & set_6g or set_5g & set_6g:
                    print("Please Check your selected clients...! Dont select the same clients, if your using --all_bands argument")
                    exit(0)
                else:
                    print("No Duplicates Devices Present.")

    # iteration-based logic
    for times in range(1,args.mixed_traffic_loop+1):
        multiple_directory = datetime.datetime.now().strftime("%b %d %H:%M:%S") + str('Mixed_Traffic_Test_Iteration_') + str(times)
        multiple_directory_path = os.path.join(overall_path,multiple_directory)
        os.mkdir(multiple_directory_path)
        if(not configure):
            args.all_bands = True
        if not args.all_bands:
            for band in Bands:  # band-based logic
                mixed_obj.band = band
                path = os.path.join(parent_dir, directory)
                if band == "2.4G":
                    security = args.twog_security
                    ssid = args.twog_ssid
                    password = args.twog_passwd
                    radio = args.twog_radio
                    directory = str(' 2.4GHz')
                    if args.real:
                        mixed_obj.real_client_wifi_config(selected_serial_list=twog_selected_devices)
                    elif args.virtual:
                        mixed_obj.virtual_client_creation(ssid=ssid, password=password, security=security, band=band,
                                                          radio=radio, num_stations=args.twog_num_stations,
                                                          start_id=args.twog_start_id)
                elif band == "5G":
                    security = args.fiveg_security
                    ssid = args.fiveg_ssid
                    password = args.fiveg_passwd
                    radio = args.fiveg_radio
                    directory = str(' 5GHz')
                    if args.real:
                        mixed_obj.real_client_wifi_config(selected_serial_list=fiveg_selected_devices)
                    elif args.virtual:
                        mixed_obj.virtual_client_creation(ssid=ssid, password=password, security=security, band=band,
                                                          radio=radio, num_stations=args.fiveg_num_stations,
                                                          start_id=args.fiveg_start_id)
                elif band == "6G":
                    security = args.sixg_security
                    ssid = args.sixg_ssid
                    password = args.sixg_passwd
                    radio = args.sixg_radio
                    directory = str(' 6GHz')
                    if args.real:
                        mixed_obj.real_client_wifi_config(selected_serial_list=sixg_selected_devices)
                    elif args.virtual:
                        mixed_obj.virtual_client_creation(ssid=ssid, password=password, security=security, band=band,
                                                          radio=radio, num_stations=args.sixg_num_stations,
                                                          start_id=args.sixg_start_id)
                path = os.path.join(multiple_directory_path, directory)
                os.mkdir(path)
                mixed_obj.report_obj(band=band, path=path)  # setting a report object
                # updating ssid, security's for report
                mixed_obj.ssid = ssid
                mixed_obj.security = security

                logger.info(f"Selected Tests List: {args.tests}")
                if args.tests:
                    if args.parallel:
                        if "1" in args.tests:
                            t1_parent, t1_child = Pipe()
                            t1 = Process(target=mixed_obj.ping_test, 
                                        kwargs={
                                            'ssid': ssid,
                                            'password': password,
                                            'security': security,
                                            'target': args.target,
                                            'interval': args.ping_interval,
                                            'conn': t1_child
                                        }
                                    )
                            t1.start()
                            # mixed_obj.ping_test(ssid=ssid, password=password, security=security, target=args.target,
                            #                     interval=args.ping_interval)
                        if "2" in args.tests:
                            t2_parent, t2_child = Pipe()
                            t2 = Process(target=mixed_obj.qos_test, 
                                        kwargs={
                                            'ssid': ssid,
                                            'password': password,
                                            'security': security,
                                            'ap_name': args.dut_model,
                                            'upstream': args.upstream_port,
                                            'tos': args.tos,
                                            'traffic_type': args.traffic_type,
                                            'side_a_min': args.side_a_min,
                                            'side_b_min': args.side_b_min,
                                            'side_a_max': args.side_a_max,
                                            'side_b_max': args.side_b_min,
                                            'conn': t2_child
                                        }
                                    )
                            t2.start()
                            # mixed_obj.qos_test(ssid=ssid, password=password, security=security, ap_name=args.dut_model,
                            #                 upstream=args.upstream_port, tos=args.tos, traffic_type=args.traffic_type,
                            #                 side_a_min=args.side_a_min, side_b_min=args.side_b_min,
                            #                 side_a_max=args.side_a_max, side_b_max=args.side_b_min)
                        if "3" in args.tests:
                            t3_parent, t3_child = Pipe()
                            t3 = Process(target=mixed_obj.ftp_test, 
                                        kwargs={
                                            'ssid': ssid,
                                            'password': password,
                                            'security': security,
                                            'bands': band,
                                            'directions': args.direction,
                                            'file_sizes': args.ftp_file_sizes,
                                            'conn': t3_child
                                        }
                                    )
                            t3.start()
                            # mixed_obj.ftp_test(ssid=ssid, password=password, security=security, bands=band,
                            #                 directions=args.direction, file_sizes=args.ftp_file_sizes)
                        if "4" in args.tests:
                            t4_parent, t4_child = Pipe()
                            t4 = Process(target=mixed_obj.http_test, 
                                        kwargs={
                                            'ssid': ssid, 
                                            'password': password, 
                                            'security': security,
                                            'http_file_size': args.http_file_size, 
                                            'target_per_ten': args.target_per_ten,
                                            'conn': t4_child
                                        }
                                    )
                            t4.start()
                            # mixed_obj.http_test(ssid=ssid, password=password, security=security,
                            #                     http_file_size=args.http_file_size, target_per_ten=args.target_per_ten)
                        if "5" in args.tests:
                            t5_parent, t5_child = Pipe()
                            t5 = Process(target=mixed_obj.multicast_test, 
                                        kwargs={
                                            'endp_types': args.mc_traffic_type, 
                                            'mc_tos': args.mc_tos,
                                            'side_a_min': args.side_a_min_bps, 
                                            'side_b_min': args.side_b_min_bps,
                                            'side_a_pdu': args.side_a_min_pdu, 
                                            'side_b_pdu': args.side_b_min_pdu,
                                            'conn': t5_child
                                        }
                                    )
                            t5.start()
                            # mixed_obj.multicast_test(endp_types=args.mc_traffic_type, mc_tos=args.mc_tos,
                            #                         side_a_min=args.side_a_min_bps, side_b_min=args.side_b_min_bps,
                            #                         side_a_pdu=args.side_a_min_pdu, side_b_pdu=args.side_b_min_pdu)

                        if "1" in args.tests:
                            mixed_obj.ping_test_obj, mixed_obj.ping_test_status = t1_parent.recv()
                            t1.join()
                        if "2" in args.tests:
                            mixed_obj.qos_test_obj, mixed_obj.data_set, mixed_obj.load, mixed_obj.res, mixed_obj.qos_test_status = t2_parent.recv()
                            t2.join()
                        if "3" in args.tests:
                            mixed_obj.ftp_test_obj, mixed_obj.ftp_test_status = t3_parent.recv()
                            t3.join()
                        if "4" in args.tests:
                            mixed_obj.http_obj, mixed_obj.dataset, mixed_obj.dataset1, mixed_obj.dataset2, mixed_obj.bytes_rd, mixed_obj.lis, mixed_obj.http_test_status = t4_parent.recv()
                            t4.join()
                        if "5" in args.tests:
                            class temp_multi_cast_obj():
                                def __init__(self, client_dict_A, client_dict_B):
                                    self.client_dict_A = client_dict_A
                                    self.client_dict_B = client_dict_B

                            client_dict_A, client_dict_B, mixed_obj.multicast_test_status = t5_parent.recv()
                            mixed_obj.multicast_test_obj = temp_multi_cast_obj(client_dict_A, client_dict_B)
                            t5.join()
                    else:
                        if "1" in args.tests:
                            mixed_obj.ping_test(ssid=ssid, password=password, security=security, target=args.target,
                                                interval=args.ping_interval)
                        if "2" in args.tests:
                            mixed_obj.qos_test(ssid=ssid, password=password, security=security, ap_name=args.dut_model,
                                            upstream=args.upstream_port, tos=args.tos, traffic_type=args.traffic_type,
                                            side_a_min=args.side_a_min, side_b_min=args.side_b_min,
                                            side_a_max=args.side_a_max, side_b_max=args.side_b_min)
                        if "3" in args.tests:
                            mixed_obj.ftp_test(ssid=ssid, password=password, security=security, bands=band,
                                            directions=args.direction, file_sizes=args.ftp_file_sizes)
                        if "4" in args.tests:
                            mixed_obj.http_test(ssid=ssid, password=password, security=security,
                                                http_file_size=args.http_file_size, target_per_ten=args.target_per_ten)
                        if "5" in args.tests:
                            mixed_obj.multicast_test(endp_types=args.mc_traffic_type, mc_tos=args.mc_tos,
                                                    side_a_min=args.side_a_min_bps, side_b_min=args.side_b_min_bps,
                                                    side_a_pdu=args.side_a_min_pdu, side_b_pdu=args.side_b_min_pdu)
                    # generating overall report
                    mixed_obj.generate_all_report()
                else:
                    print("No Test Selected. Please select the Tests.")
                    exit(0)
        else:
            # the tests will run irrespective to bands
            mixed_obj.band = Bands[0]   # since all the test are band specific, passing band first item in the list #Todo: need to modify this , for now hardcoded
            mixed_obj.radio = args.twog_radio   # taking a first twog-radio in a list as a default radio #Todo: need to modify this , for now hardcoded
            path = os.path.join(multiple_directory_path)
            mixed_obj.report_obj(band=None, path=path)  # setting a report object
            if args.real:
                if(configure):
                    selected_serial_list = [twog_selected_devices, fiveg_selected_devices, sixg_selected_devices]
                    logger.info(f"All Selected Clients: {selected_serial_list}")
                    for client_list in selected_serial_list:
                        if client_list:
                            mixed_obj.real_client_wifi_config(selected_serial_list=client_list, all_devices=True)
                else:
                    mixed_obj.base_interop_profile.get_devices()
                    mixed_obj.select_real_devices(real_devices=mixed_obj.base_interop_profile)

            elif args.virtual:
                sta_list_2g, sta_list_5g, sta_list_6g = [], [], []
                if args.twog_num_stations:
                    sta_list_2g = mixed_obj.virtual_client_creation(ssid=args.twog_ssid, password=args.twog_passwd,
                                                      security=args.twog_security, band='2.4G',
                                                      radio=args.twog_radio, num_stations=args.twog_num_stations,
                                                      start_id=args.twog_start_id, all_sta=True)
                if args.fiveg_num_stations:
                    sta_list_5g = mixed_obj.virtual_client_creation(ssid=args.fiveg_ssid, password=args.fiveg_passwd,
                                                      security=args.fiveg_security, band='5G',
                                                      radio=args.fiveg_radio, num_stations=args.fiveg_num_stations,
                                                      start_id=args.fiveg_start_id, all_sta=True)
                if args.sixg_num_stations:
                    sta_list_6g = mixed_obj.virtual_client_creation(ssid=args.sixg_ssid, password=args.sixg_passwd,
                                                      security=args.sixg_security, band='6G',
                                                      radio=args.sixg_radio, num_stations=args.sixg_num_stations,
                                                      start_id=args.sixg_start_id, all_sta=True)
                # updating num stations and station list
                virtual_station_list = sta_list_2g + sta_list_5g + sta_list_6g
                logger.info("Selected Virtual Station List:", virtual_station_list)
                mixed_obj.station_list = virtual_station_list
                mixed_obj.num_staions = args.twog_num_stations + args.fiveg_num_stations + args.sixg_num_stations
            if(args.use_default_config):
                ssid = 'Test Configured'
                security = 'Test Configured'
            else:
                ssid = str(args.twog_ssid + ',' + args.fiveg_ssid + ',' + args.sixg_ssid)
                security = str(args.twog_security + ',' + args.fiveg_security + ',' + args.sixg_security)
            mixed_obj.ssid = ssid
            mixed_obj.security = security
            # tests will run with respect to bands
            logger.info("Selected Tests List: ".format(args.tests))
            if args.tests:
                if args.parallel:
                    if "1" in args.tests:
                        t1_parent, t1_child = Pipe()
                        t1 = Process(target=mixed_obj.ping_test, 
                                    kwargs={
                                        'ssid': ssid,
                                        'password': password,
                                        'security': security,
                                        'target': args.target,
                                        'interval': args.ping_interval,
                                        'conn': t1_child, 
                                        'all_bands': True
                                    }
                                )
                        t1.start()
                        # mixed_obj.ping_test(ssid=ssid, password=password, security=security, target=args.target,
                        #                     interval=args.ping_interval)
                    if "2" in args.tests:
                        t2_parent, t2_child = Pipe()
                        t2 = Process(target=mixed_obj.qos_test, 
                                    kwargs={
                                        'ssid': ssid,
                                        'password': password,
                                        'security': security,
                                        'ap_name': args.dut_model,
                                        'upstream': args.upstream_port,
                                        'tos': args.tos,
                                        'traffic_type': args.traffic_type,
                                        'side_a_min': args.side_a_min,
                                        'side_b_min': args.side_b_min,
                                        'side_a_max': args.side_a_max,
                                        'side_b_max': args.side_b_min,
                                        'conn': t2_child, 
                                        'all_bands': True
                                    }
                                )
                        t2.start()
                        # mixed_obj.qos_test(ssid=ssid, password=password, security=security, ap_name=args.dut_model,
                        #                 upstream=args.upstream_port, tos=args.tos, traffic_type=args.traffic_type,
                        #                 side_a_min=args.side_a_min, side_b_min=args.side_b_min,
                        #                 side_a_max=args.side_a_max, side_b_max=args.side_b_min)
                    if "3" in args.tests:
                        t3_parent, t3_child = Pipe()
                        t3 = Process(target=mixed_obj.ftp_test, 
                                    kwargs={
                                        'ssid': ssid,
                                        'password': password,
                                        'security': security,
                                        'bands': Bands,
                                        'directions': args.direction,
                                        'file_sizes': args.ftp_file_sizes,
                                        'conn': t3_child, 
                                        'all_bands': True
                                    }
                                )
                        t3.start()
                        # mixed_obj.ftp_test(ssid=ssid, password=password, security=security, bands=band,
                        #                 directions=args.direction, file_sizes=args.ftp_file_sizes)
                    if "4" in args.tests:
                        t4_parent, t4_child = Pipe()
                        t4 = Process(target=mixed_obj.http_test, 
                                    kwargs={
                                        'ssid': ssid, 
                                        'password': password, 
                                        'security': security,
                                        'http_file_size': args.http_file_size, 
                                        'target_per_ten': args.target_per_ten,
                                        'conn': t4_child, 
                                        'all_bands': True
                                    }
                                )
                        t4.start()
                        # mixed_obj.http_test(ssid=ssid, password=password, security=security,
                        #                     http_file_size=args.http_file_size, target_per_ten=args.target_per_ten)
                    if "5" in args.tests:
                        t5_parent, t5_child = Pipe()
                        t5 = Process(target=mixed_obj.multicast_test, 
                                    kwargs={
                                        'endp_types': args.mc_traffic_type, 
                                        'mc_tos': args.mc_tos,
                                        'side_a_min': args.side_a_min_bps, 
                                        'side_b_min': args.side_b_min_bps,
                                        'side_a_pdu': args.side_a_min_pdu, 
                                        'side_b_pdu': args.side_b_min_pdu,
                                        'conn': t5_child, 
                                        'all_bands': True
                                    }
                                )
                        t5.start()
                        # mixed_obj.multicast_test(endp_types=args.mc_traffic_type, mc_tos=args.mc_tos,
                        #                         side_a_min=args.side_a_min_bps, side_b_min=args.side_b_min_bps,
                        #                         side_a_pdu=args.side_a_min_pdu, side_b_pdu=args.side_b_min_pdu)


                    # if "5" in args.tests:
                    #     t5.start()
                    # if "4" in args.tests:
                    #     t4.start()
                    # if "3" in args.tests:
                    #     t3.start()
                    # if "2" in args.tests:
                    #     t2.start()
                    # if "1" in args.tests:
                    #     t1.start()

                    if "1" in args.tests:
                        mixed_obj.ping_test_obj, mixed_obj.ping_test_status = t1_parent.recv()
                        t1.join()
                    if "2" in args.tests:
                        mixed_obj.qos_test_obj, mixed_obj.data_set, mixed_obj.load, mixed_obj.res, mixed_obj.qos_test_status = t2_parent.recv()
                        t2.join()
                    if "3" in args.tests:
                        mixed_obj.ftp_test_obj, mixed_obj.ftp_test_status = t3_parent.recv()
                        t3.join()
                    if "4" in args.tests:
                        mixed_obj.http_obj, mixed_obj.dataset, mixed_obj.dataset1, mixed_obj.dataset2, mixed_obj.bytes_rd, mixed_obj.lis, mixed_obj.http_test_status = t4_parent.recv()
                        t4.join()
                    if "5" in args.tests:
                        class temp_multi_cast_obj():
                            def __init__(self, client_dict_A, client_dict_B):
                                self.client_dict_A = client_dict_A
                                self.client_dict_B = client_dict_B

                        client_dict_A, client_dict_B, mixed_obj.multicast_test_status = t5_parent.recv()
                        mixed_obj.multicast_test_obj = temp_multi_cast_obj(client_dict_A, client_dict_B)
                        t5.join()
                else:
                    if "1" in args.tests:
                        mixed_obj.ping_test(ssid=ssid, password=password, security=security, target=args.target,
                                            interval=args.ping_interval, all_bands=True)
                    if "2" in args.tests:
                        mixed_obj.qos_test(ssid=ssid, password=password, security=security, ap_name=args.dut_model,
                                        upstream=args.upstream_port, tos=args.tos, traffic_type=args.traffic_type,
                                        side_a_min=args.side_a_min, side_b_min=args.side_b_min,
                                        side_a_max=args.side_a_max, side_b_max=args.side_b_min, all_bands=True)
                    if "3" in args.tests:
                        mixed_obj.ftp_test(ssid=ssid, password=password, security=security, bands=Bands,
                                        directions=args.direction, file_sizes=args.ftp_file_sizes, all_bands=True)
                    if "4" in args.tests:
                        mixed_obj.http_test(ssid=ssid, password=password, security=security,
                                            http_file_size=args.http_file_size, target_per_ten=args.target_per_ten,
                                            all_bands=True)
                    if "5" in args.tests:
                        mixed_obj.multicast_test(endp_types=args.mc_traffic_type, mc_tos=args.mc_tos,
                                                side_a_min=args.side_a_min_bps, side_b_min=args.side_b_min_bps,
                                                side_a_pdu=args.side_a_min_pdu, side_b_pdu=args.side_b_min_pdu,
                                                all_bands=True)
                # generating overall report
                mixed_obj.generate_all_report()
            else:
                print("No Test Selected. Please select the Tests.")
                exit(0)


if __name__ == "__main__":
    main()
