#!/usr/bin/env python3
"""
NAME:       throughput_qos.py

PURPOSE:    Configure WiFi throughput tests with varying ToS, rate, direction and more.
            Includes support for creating basic stations (open and personal authentication).

NOTES:      Desired TOS must be specified with abbreviated name in all capital letters,
            for example '--tos "BK,VI,BE,VO"'

            Stations will not be created unless the '--create_sta' argument is specified.

            For running the test in dual-band and tri-band configurations, --bands dualband,
            the number of stations used on each band will be split across the number of utilized bands.
            For example, if '--num_stations 64' is specified, then 32 2.4GHz and 32 5GHz stations will be used.

EXAMPLES:   # Run download scenario with Voice TOS in 2.4GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --bands 2.4g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_udp --tos "VO" --create_sta

            # Run download scenario with Voice and Video TOS in 5GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_5g wiphy1
                --ssid_5g Cisco --passwd_5g cisco@123 --security_5g wpa2 --bands 5g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

            # Run download scenario with Voice and Video TOS in 6GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_6g wiphy1
                --ssid_6g Cisco --passwd_6g cisco@123 --security_6g wpa2 --bands 6g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

            # Run upload scenario with Background, Best Effort, Video, and Voice TOS in 2.4GHz and 5GHz bands
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g cisco@123
                --security_5g wpa2 --bands dualband --upstream eth1 --test_duration 1m --download 0 --upload 1000000
                --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

            # Run upload scenario with Background, Best Effort, Video and Voice TOS in 2.4GHz and 5GHz bands with 'Open' security
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g [BLANK] --security_2g open --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g [BLANK]
                --security_5g open --bands dualband --upstream eth1 --test_duration 1m --download 0 --upload 1000000
                --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

            # Run bi-directional scenario with Video and Voice TOS in 6GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_6g wiphy1
                --ssid_6g Cisco --passwd_6g cisco@123 --security_6g wpa2 --bands 6g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 10000000 --traffic_type lf_udp --tos "VO,VI" --create_sta

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional, Report Generation

STATUS:     Beta Release

VERIFIED_ON:
            Working date:   03/08/2023
            Build version:  5.4.6
            kernel version: 6.2.16+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc
"""

from datetime import datetime, timedelta
import argparse
import time
import sys
import os
import pandas as pd
import importlib
import copy

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from lf_graph import lf_bar_graph
from lf_graph import lf_bar_graph_horizontal
from lf_report import lf_report
from LANforge import LFUtils

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm


class ThroughputQOS(Realm):
    def __init__(self,
                 tos,
                 ssid=None,
                 security=None,
                 password=None,
                 ssid_2g=None,
                 security_2g=None,
                 password_2g=None,
                 ssid_5g=None,
                 security_5g=None,
                 password_5g=None,
                 ssid_6g=None,
                 security_6g=None,
                 password_6g=None,
                 create_sta=True,
                 name_prefix=None,
                 upstream=None,
                 num_stations_2g=1,
                 num_stations_5g=0,
                 num_stations_6g=0,
                 sta_list=None,
                 radio_2g="wiphy0",
                 radio_5g="wiphy1",
                 radio_6g="wiphy2",
                 host="localhost",
                 port=8080,
                 mode=0,
                 ap_name="",
                 direction="",
                 initial_band_pref=False,
                 traffic_type=None,
                 side_a_min_rate=0, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="2m",
                 bands="2.4G, 5G, DUALBAND, TRIBAND",
                 test_case=None,
                 channel_list=None,
                 mac_list=None,
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=host, lfclient_port=port)

        # https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
        if not sta_list:
            sta_list = []
        if not test_case:
            test_case = {}
        if not channel_list:
            channel_list = []
        if not mac_list:
            mac_list = []

        self.ssid_list = []
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.ssid_2g = ssid_2g
        self.security_2g = security_2g
        self.password_2g = password_2g
        self.ssid_5g = ssid_5g
        self.security_5g = security_5g
        self.password_5g = password_5g
        self.ssid_6g = ssid_6g
        self.security_6g = security_6g
        self.password_6g = password_6g
        self.radio_2g = radio_2g
        self.radio_5g = radio_5g
        self.radio_6g = radio_6g
        self.num_stations_2g = num_stations_2g
        self.num_stations_5g = num_stations_5g
        self.num_stations_6g = num_stations_6g
        self.sta_list = sta_list
        self.channel_list = channel_list
        self.mac_list = mac_list
        self.create_sta = create_sta
        self.initial_band_pref = initial_band_pref
        self.mode = mode
        self.ap_name = ap_name
        self.direction = direction
        self.traffic_type = traffic_type
        self.tos = tos.split(",")
        self.bands = bands.split(",")
        self.test_case = test_case
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 14
        # self.station_profile.mode = mode
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def start(self, print_pass=False, print_fail=False):
        if len(self.cx_profile.created_cx) > 0:
            for cx in self.cx_profile.created_cx.keys():
                req_url = "cli-json/set_cx_report_timer"
                data = {
                    "test_mgr": "all",
                    "cx_name": cx,
                    "milliseconds": 1000
                }
                self.json_post(req_url, data)
        self.cx_profile.start_cx()

    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.cx_profile.cleanup()
        if self.create_sta:
            for sta in self.sta_list:
                self.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.cx_profile.cleanup()
        if self.create_sta:
            self.station_profile.cleanup()
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                               debug=self.debug)

    def build(self):
        for key in self.bands:
            if self.create_sta:
                band_pref = 0
                if key == "2.4G" or key == "2.4g":
                    self.station_profile.mode = 13
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 2
                        print("Set initial band preference to 2.4GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_2g, sta_names_=self.sta_list, debug=self.debug)
                if key == "5G" or key == "5g":
                    self.station_profile.mode = 14
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 5
                        print("Set initial band preference to 5GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list, debug=self.debug)
                if key == "6G" or key == "6g":
                    self.station_profile.mode = 15
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_6g, self.ssid_6g, self.password_6g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 6
                        print("Set initial band preference to 6GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_6g, sta_names_=self.sta_list, debug=self.debug)
                if key == "DUALBAND" or key == "dualband":
                    split = len(self.sta_list) // 2
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 13
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 2
                        print("Set initial band preference to 2.4GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_2g, sta_names_=self.sta_list[:split],
                                                debug=self.debug)
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 14
                    self.station_profile.set_number_template(self.number_template)
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 5
                        print("Set initial band preference to 5GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list[split:],
                                                debug=self.debug)
                if key == "TRIBAND" or key == "triband":
                    split_1 = len(self.sta_list) // 3
                    split_2 = 2 * (len(self.sta_list) // 3)  # Ensures 3rd band gets remaining stations
                    # Assign stations to 2.4GHz
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 13
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations for 2.4GHz")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 2
                        print("Set initial band preference to 2.4GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_2g, sta_names_=self.sta_list[:split_1], debug=self.debug)

                    # Assign stations to 5GHz
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 14
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations for 5GHz")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 5
                        print("Set initial band preference to 5GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list[split_1:split_2], debug=self.debug)

                    # Assign stations to 6GHz
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_6g, self.ssid_6g, self.password_6g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 15
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations for 6GHz")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    if self.initial_band_pref:
                        band_pref = 6
                        print("Set initial band preference to 6GHz")
                    self.station_profile.set_wifi_extra2(initial_band_pref=band_pref)
                    self.station_profile.create(radio=self.radio_6g, sta_names_=self.sta_list[split_2:], debug=self.debug)

                # Bring all stations up
                self.station_profile.admin_up()
                # check here if upstream port got IP
                temp_stations = self.station_profile.station_names.copy()
                if self.wait_for_ip(temp_stations):
                    self._pass("All stations got IPs")
                else:
                    self._fail("Stations failed to get IPs")
                    self.exit_fail()
                self._pass("PASS: Station build finished")
            self.create_cx()
            print("cx build finished")
        response_port = self.json_get("/port/all")
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if port in self.sta_list:
                    self.mac_list.append(port_data['mac'])
                    self.channel_list.append(port_data['channel'])

    def create_cx(self):
        direction = ''
        if int(self.cx_profile.side_b_min_bps) != 0 and int(self.cx_profile.side_a_min_bps) != 0:
            self.direction = "Bi-direction"
            direction = 'Bi-di'
        elif int(self.cx_profile.side_b_min_bps) != 0:
            self.direction = "Download"
            direction = 'DL'
        else:
            if int(self.cx_profile.side_a_min_bps) != 0:
                self.direction = "Upload"
                direction = 'UL'
        print("direction", self.direction)
        traffic_type = (self.traffic_type.strip("lf_")).upper()
        traffic_direction_list, cx_list, traffic_type_list = [], [], []
        for _ in range(len(self.sta_list)):
            traffic_direction_list.append(direction)
            traffic_type_list.append(traffic_type)
        print("tos: {}".format(self.tos))
        for ip_tos in self.tos:
            for i in self.sta_list:
                for j in traffic_direction_list:
                    for k in traffic_type_list:
                        cxs = "%s_%s_%s_%s" % (i, k, j, ip_tos)
                        cx_names = cxs.replace(" ", "")
                        # print(cx_names)
                cx_list.append(cx_names)
        print('cx_list', cx_list)
        count = 0
        print("tos: {}".format(self.tos))
        for ip_tos in range(len(self.tos)):
            for sta in range(len(self.sta_list)):
                print("## ip_tos: {}".format(self.tos[ip_tos]))
                print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
                    self.traffic_type, self.tos[ip_tos], self.cx_profile.get_cx_count()))
                self.cx_profile.create(endp_type=self.traffic_type, side_a=[self.sta_list[sta]],
                                       side_b=self.upstream,
                                       sleep_time=0, tos=self.tos[ip_tos], cx_name="%s-%i" % (cx_list[count], len(self.cx_profile.created_cx)))
                count += 1
        print("cross connections with TOS type created.")

    def monitor(self):
        throughput, upload, download, upload_throughput, download_throughput, connections_upload, connections_download = {}, [], [], [], [], {}, {}
        drop_a, drop_a_per, drop_b, drop_b_per = [], [], [], []
        if int(self.cx_profile.side_b_min_bps) != 0 and int(self.cx_profile.side_a_min_bps) != 0:
            self.direction = "Bi-direction"
        elif int(self.cx_profile.side_b_min_bps) != 0:
            self.direction = "Download"
        else:
            if int(self.cx_profile.side_a_min_bps) != 0:
                self.direction = "Upload"
        print("direction", self.direction)
        if self.test_duration is None or int(self.test_duration) <= 1:
            raise ValueError("Monitor test duration should be > 1 second")
        if self.cx_profile.created_cx is None:
            raise ValueError("Monitor needs a list of Layer 3 connections")
        # monitor columns
        start_time = datetime.now()
        test_start_time = datetime.now().strftime("%b %d %H:%M:%S")
        print("Test started at: ", test_start_time)
        print("Monitoring cx and endpoints")
        end_time = start_time + timedelta(seconds=int(self.test_duration))
        index = -1
        connections_upload = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        [(upload.append([]), download.append([]), drop_a.append([]), drop_b.append([])) for i in range(len(self.cx_profile.created_cx))]
        while datetime.now() < end_time:
            index += 1
            response = list(self.json_get('/cx/%s?fields=%s' % (','.join(self.cx_profile.created_cx.keys()), ",".join(['bps rx a', 'bps rx b', 'rx drop %25 a', 'rx drop %25 b']))).values())[2:]
            throughput[index] = list(
                map(lambda i: [x for x in i.values()], response))
            time.sleep(1)
        print("throughput", throughput)
        # # rx_rate list is calculated
        for _, key in enumerate(throughput):
            for i in range(len(throughput[key])):
                upload[i].append(throughput[key][i][1])
                download[i].append(throughput[key][i][0])
                drop_a[i].append(throughput[key][i][2])
                drop_b[i].append(throughput[key][i][3])
        upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
        download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
        drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
        drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
        keys = list(connections_upload.keys())
        keys = list(connections_download.keys())

        for i in range(len(download_throughput)):
            connections_download.update({keys[i]: float(f"{(download_throughput[i] ):.2f}")})
        for i in range(len(upload_throughput)):
            connections_upload.update({keys[i]: float(f"{(upload_throughput[i] ):.2f}")})
        return connections_download, connections_upload, drop_a_per, drop_b_per

    def evaluate_qos(self, connections_download, connections_upload, drop_a_per, drop_b_per):
        case_upload = ""
        case_download = ""
        tos_download = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_download = {}
        rx_endps_download = {}
        delay = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tos_upload = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_upload = {}
        rx_endps_upload = {}
        tos_drop_dict = {'rx_drop_a': {'BK': [], 'BE': [], 'VI': [], 'VO': []},
                         'rx_drop_b': {'BK': [], 'BE': [], 'VI': [], 'VO': []}}
        num_stations = int(self.num_stations_2g) + int(self.num_stations_5g) + int(self.num_stations_6g)
        if int(self.cx_profile.side_b_min_bps) != 0:
            case_download = str(int(self.cx_profile.side_b_min_bps) / 1000000)
        if int(self.cx_profile.side_a_min_bps) != 0:
            case_upload = str(int(self.cx_profile.side_a_min_bps) / 1000000)
        if len(self.cx_profile.created_cx.keys()) > 0:
            endp_data = self.json_get('endp/all?fields=name,tx+pkts+ll,rx+pkts+ll,delay')
            endp_data.pop("handler")
            endp_data.pop("uri")
            endps = endp_data['endpoint']
            if int(self.cx_profile.side_b_min_bps) != 0:
                for i in range(len(endps)):
                    if i < len(endps) // 2:
                        tx_endps_download.update(endps[i])
                    if i >= len(endps) // 2:
                        rx_endps_download.update(endps[i])
                for sta in self.cx_profile.created_cx.keys():
                    temp = sta.rsplit('-', 1)
                    temp = int(temp[1])
                    if temp in range(0, num_stations):
                        if int(self.cx_profile.side_b_min_bps) != 0:
                            tos_download[self.tos[0]].append(connections_download[sta])
                            tos_drop_dict['rx_drop_a'][self.tos[0]].append(drop_a_per[temp])
                            tx_b_download[self.tos[0]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_download[self.tos[0]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                            delay[self.tos[0]].append(rx_endps_download['%s-A' % sta]['delay'])
                        else:
                            tos_download[self.tos[0]].append(float(0))
                            tos_drop_dict['rx_drop_a'][self.tos[0]].append(float(0))
                            tx_b_download[self.tos[0]].append(int(0))
                            rx_a_download[self.tos[0]].append(int(0))
                            delay[self.tos[0]].append(int(0))
                    elif temp in range(num_stations, 2 * num_stations):
                        if len(self.tos) < 2:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[1]].append(connections_download[sta])
                                tos_drop_dict['rx_drop_a'][self.tos[1]].append(drop_a_per[temp])
                                tx_b_download[self.tos[1]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[1]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[1]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[1]].append(float(0))
                                tos_drop_dict['rx_drop_a'][self.tos[1]].append(float(0))
                                tx_b_download[self.tos[1]].append(int(0))
                                rx_a_download[self.tos[1]].append(int(0))
                                delay[self.tos[1]].append(int(0))
                    elif temp in range(2 * num_stations, 3 * num_stations):
                        if len(self.tos) < 3:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[2]].append(connections_download[sta])
                                tos_drop_dict['rx_drop_a'][self.tos[2]].append(drop_a_per[temp])
                                tx_b_download[self.tos[2]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[2]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[2]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[2]].append(float(0))
                                tos_drop_dict['rx_drop_a'][self.tos[2]].append(float(0))
                                tx_b_download[self.tos[2]].append(int(0))
                                rx_a_download[self.tos[2]].append(int(0))
                                delay[self.tos[2]].append(int(0))
                    elif temp in range(3 * num_stations, 4 * num_stations):
                        if len(self.tos) < 4:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[3]].append(connections_download[sta])
                                tos_drop_dict['rx_drop_a'][self.tos[3]].append(drop_a_per[temp])
                                tx_b_download[self.tos[3]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[3]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[3]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[3]].append(float(0))
                                tos_drop_dict['rx_drop_a'][self.tos[3]].append(float(0))
                                tx_b_download[self.tos[3]].append(int(0))
                                rx_a_download[self.tos[3]].append(int(0))
                                delay[self.tos[3]].append(int(0))
                tos_download.update({"bkQOS": float(f"{sum(tos_download['BK']):.2f}")})
                tos_download.update({"beQOS": float(f"{sum(tos_download['BE']):.2f}")})
                tos_download.update({"videoQOS": float(f"{sum(tos_download['VI']):.2f}")})
                tos_download.update({"voiceQOS": float(f"{sum(tos_download['VO']):.2f}")})
                tos_download.update({"bkDELAY": sum(delay['BK'])})
                tos_download.update({"beDELAY": sum(delay['BE'])})
                tos_download.update({"videoDELAY": sum(delay['VI'])})
                tos_download.update({"voiceDELAY": sum(delay['VO'])})
                if sum(tx_b_download['BK']) != 0 or sum(tx_b_download['BE']) != 0 or sum(tx_b_download['VI']) != 0 or sum(tx_b_download['VO']) != 0:
                    if sum(tx_b_download['BK']) > sum(rx_a_download['BK']):
                        tos_download.update(
                            {"bkLOSS": float(f"{((sum(tx_b_download['BK']) - sum(rx_a_download['BK'])) / sum(tx_b_download['BK'])) * 100:.2f}")})
                    else:
                        if sum(rx_a_download['BK']) != 0:
                            tos_download.update({"bkLOSS": float(f"{((sum(rx_a_download['BK']) - sum(tx_b_download['BK'])) / sum(rx_a_download['BK'])) * 100:.2f}")})
                        else:
                            tos_download.update({"bkLOSS": float(0)})
                    if sum(tx_b_download['BE']) > sum(rx_a_download['BE']):
                        tos_download.update(
                            {"beLOSS": float(f"{((sum(tx_b_download['BE']) - sum(rx_a_download['BE'])) / sum(tx_b_download['BE'])) * 100:.2f}")})
                    else:
                        if sum(rx_a_download['BE']) != 0:
                            tos_download.update(
                                {"beLOSS": float(f"{((sum(rx_a_download['BE']) - sum(tx_b_download['BE'])) / sum(rx_a_download['BE'])) * 100:.2f}")})
                        else:
                            tos_download.update({"beLOSS": float(0)})
                    if sum(tx_b_download['VI']) > sum(rx_a_download['VI']):
                        tos_download.update(
                            {"videoLOSS": float(f"{((sum(tx_b_download['VI']) - sum(rx_a_download['VI'])) / sum(tx_b_download['VI'])) * 100:.2f}")})
                    else:
                        if sum(rx_a_download['VI']) != 0:
                            tos_download.update(
                                {"videoLOSS": float(f"{((sum(rx_a_download['VI']) - sum(tx_b_download['VI'])) / sum(rx_a_download['VI'])) * 100:.2f}")})
                        else:
                            tos_download.update({"videoLOSS": float(0)})
                    if sum(tx_b_download['VO']) > sum(rx_a_download['VO']):
                        tos_download.update(
                            {"voiceLOSS": float(f"{((sum(tx_b_download['VO']) - sum(rx_a_download['VO'])) / sum(tx_b_download['VO'])) * 100:.2f}")})
                    else:
                        if sum(rx_a_download['VO']) != 0:
                            tos_download.update(
                                {"voiceLOSS": float(
                                    f"{((sum(rx_a_download['VO']) - sum(tx_b_download['VO'])) / sum(rx_a_download['VO'])) * 100:.2f}")})
                        else:
                            tos_download.update({"voiceLOSS": float(0)})
                tos_download.update({'tx_b': tx_b_download})
                tos_download.update({'rx_a': rx_a_download})
            if int(self.cx_profile.side_a_min_bps) != 0:
                for i in range(len(endps)):
                    if i < len(endps) // 2:
                        tx_endps_upload.update(endps[i])
                    if i >= len(endps) // 2:
                        rx_endps_upload.update(endps[i])
                for sta in self.cx_profile.created_cx.keys():
                    temp = sta.rsplit('-', 1)
                    temp = int(temp[1])
                    if temp in range(0, num_stations):
                        if int(self.cx_profile.side_a_min_bps) != 0:
                            tos_upload[self.tos[0]].append(connections_upload[sta])
                            tos_drop_dict['rx_drop_b'][self.tos[0]].append(drop_b_per[temp])
                            tx_b_upload[self.tos[0]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_upload[self.tos[0]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                            delay[self.tos[0]].append(rx_endps_upload['%s-A' % sta]['delay'])
                        else:
                            tos_upload[self.tos[0]].append(float(0))
                            tos_drop_dict['rx_drop_b'][self.tos[0]].append(float(0))
                            tx_b_upload[self.tos[0]].append(int(0))
                            rx_a_upload[self.tos[0]].append(int(0))
                            delay[self.tos[0]].append(int(0))
                    elif temp in range(num_stations, 2 * num_stations):
                        if len(self.tos) < 2:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[1]].append(connections_upload[sta])
                                tos_drop_dict['rx_drop_b'][self.tos[1]].append(drop_b_per[temp])
                                tx_b_upload[self.tos[1]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[1]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[1]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[1]].append(float(0))
                                tos_drop_dict['rx_drop_b'][self.tos[1]].append(float(0))
                                tx_b_upload[self.tos[1]].append(int(0))
                                rx_a_upload[self.tos[1]].append(int(0))
                                delay[self.tos[1]].append(int(0))
                    elif temp in range(2 * num_stations, 3 * num_stations):
                        if len(self.tos) < 3:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[2]].append(connections_upload[sta])
                                tos_drop_dict['rx_drop_b'][self.tos[2]].append(drop_b_per[temp])
                                tx_b_upload[self.tos[2]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[2]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[2]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[2]].append(float(0))
                                tos_drop_dict['rx_drop_b'][self.tos[2]].append(float(0))
                                tx_b_upload[self.tos[2]].append(int(0))
                                rx_a_upload[self.tos[2]].append(int(0))
                                delay[self.tos[2]].append(int(0))
                    elif temp in range(3 * num_stations, 4 * num_stations):
                        if len(self.tos) < 4:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[3]].append(connections_upload[sta])
                                tos_drop_dict['rx_drop_b'][self.tos[3]].append(drop_b_per[temp])
                                tx_b_upload[self.tos[3]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[3]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[3]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[3]].append(float(0))
                                tos_drop_dict['rx_drop_b'][self.tos[3]].append(float(0))
                                tx_b_upload[self.tos[3]].append(int(0))
                                rx_a_upload[self.tos[3]].append(int(0))
                                delay[self.tos[3]].append(int(0))
                tos_upload.update({"bkQOS": float(f"{sum(tos_upload['BK']):.2f}")})
                tos_upload.update({"beQOS": float(f"{sum(tos_upload['BE']):.2f}")})
                tos_upload.update({"videoQOS": float(f"{sum(tos_upload['VI']):.2f}")})
                tos_upload.update({"voiceQOS": float(f"{sum(tos_upload['VO']):.2f}")})
                tos_upload.update({'tx_b': tx_b_upload})
                tos_upload.update({'rx_a': rx_a_upload})
        else:
            print("no RX values available to evaluate QOS")
        key_upload = case_upload + " " + "Mbps"
        key_download = case_download + " " + "Mbps"
        return {key_download: tos_download}, {key_upload: tos_upload}, {"drop_per": tos_drop_dict}

    def set_report_data(self, data):
        print("data", data)
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        res = {}
        if data is not None:
            res.update(data)
        else:
            print("No Data found to generate report!")
            exit(1)
        if self.test_case is not None:
            table_df = {}
            num_stations = []
            mode = []
            graph_df = {}
            download_throughput, upload_throughput = [], []
            upload_throughput_df, download_throughput_df = [[], [], [], []], [[], [], [], []]
            for case in self.test_case:
                if case == "2.4g" or case == "2.4G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("bgn-AX")
                elif case == "5g" or case == "5G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("an-AX")
                elif case == "6g" or case == "6G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                elif case == "dualband" or case == "DUALBAND":
                    num_stations.append("{} + {}".format(str(len(self.sta_list) // 2), str(len(self.sta_list) // 2)))
                    mode.append("bgn-AX + an-AX")
                elif case == "triband" or case == "TRIBAND":
                    split_1 = len(self.sta_list) // 3
                    num_stations.append("{} + {} + {}".format(str(split_1), str(split_1), str(len(self.sta_list) - 2 * split_1)))
                    mode.append("bgn-AX + an-AX + AX-BE")
                for _ in res[case]['test_results'][0][1]:
                    if int(self.cx_profile.side_a_min_bps) != 0:
                        print(res[case]['test_results'][0][1])
                        upload_throughput.append(
                            "BK : {}, BE : {}, VI: {}, VO: {}".format(res[case]['test_results'][0][1][rate_up]["bkQOS"],
                                                                      res[case]['test_results'][0][1][rate_up]["beQOS"],
                                                                      res[case]['test_results'][0][1][rate_up][
                                "videoQOS"],
                                res[case]['test_results'][0][1][rate_up][
                                "voiceQOS"]))
                        upload_throughput_df[0].append(res[case]['test_results'][0][1][rate_up]['bkQOS'])
                        upload_throughput_df[1].append(res[case]['test_results'][0][1][rate_up]['beQOS'])
                        upload_throughput_df[2].append(res[case]['test_results'][0][1][rate_up]['videoQOS'])
                        upload_throughput_df[3].append(res[case]['test_results'][0][1][rate_up]['voiceQOS'])
                        table_df.update({"No of Stations": []})
                        table_df.update({"Throughput for Load {}".format(rate_up + "-upload"): []})
                        graph_df.update({rate_up + "-upload": upload_throughput_df})

                        table_df.update({"No of Stations": num_stations})
                        table_df["Throughput for Load {}".format(rate_up + "-upload")].append(upload_throughput[0])
                        # table_df.update({"Mode": mode})
                        # for i in self.test_case:
                        #     count = 0
                        #     for key in res[i]:
                        #         table_df["Throughput for Load {}".format(rate_up)].append(throughput[count])
                        #         count += 1
                        res_copy = copy.copy(res)
                        res_copy.update({"throughput_table_df": table_df})
                        res_copy.update({"graph_df": graph_df})
                for _ in res[case]['test_results'][0][0]:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        print(res[case]['test_results'][0][0])
                        download_throughput.append(
                            "BK : {}, BE : {}, VI: {}, VO: {}".format(res[case]['test_results'][0][0][rate_down]["bkQOS"],
                                                                      res[case]['test_results'][0][0][rate_down]["beQOS"],
                                                                      res[case]['test_results'][0][0][rate_down][
                                "videoQOS"],
                                res[case]['test_results'][0][0][rate_down][
                                "voiceQOS"]))
                        download_throughput_df[0].append(res[case]['test_results'][0][0][rate_down]['bkQOS'])
                        download_throughput_df[1].append(res[case]['test_results'][0][0][rate_down]['beQOS'])
                        download_throughput_df[2].append(res[case]['test_results'][0][0][rate_down]['videoQOS'])
                        download_throughput_df[3].append(res[case]['test_results'][0][0][rate_down]['voiceQOS'])
                        table_df.update({"No of Stations": []})
                        # table_df.update({"Mode": []})
                        table_df.update({"Throughput for Load {}".format(rate_down + "-download"): []})
                        graph_df.update({rate_down + "-download": download_throughput_df})
                        table_df.update({"No of Stations": num_stations})
                        table_df["Throughput for Load {}".format(rate_down + "-download")].append(download_throughput[0])
                        # table_df.update({"Mode": mode})
                        # for i in self.test_case:
                        #     count = 0
                        #     for key in res[i]:
                        #         table_df["Throughput for Load {}".format(rate_down+"-download")].append(throughput[count])
                        #         count += 1
                        res_copy = copy.copy(res)
                        res_copy.update({"throughput_table_df": table_df})
                        res_copy.update({"graph_df": graph_df})
                        print("table_df", table_df)
        return res_copy

    def generate_graph_data_set(self, data):
        load = ''
        data_set, overall_list = [], []
        overall_throughput = [[], [], [], []]
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        if self.direction == 'Upload':
            load = rate_up
        else:
            if self.direction == "Download":
                load = rate_down
        res = self.set_report_data(data)
        print("res", res)
        if self.direction == "Bi-direction":
            load = 'Upload' + ':' + rate_up + ',' + 'Download' + ':' + rate_down
            for key in res["graph_df"]:
                for j in range(len(res['graph_df'][key])):
                    overall_list.append(res['graph_df'][key][j])
            print(overall_list)
            overall_throughput[0].append(round(sum(overall_list[0] + overall_list[4]), 2))
            overall_throughput[1].append(round(sum(overall_list[1] + overall_list[5]), 2))
            overall_throughput[2].append(round(sum(overall_list[2] + overall_list[6]), 2))
            overall_throughput[3].append(round(sum(overall_list[3] + overall_list[7]), 2))
            print("overall thr", overall_throughput)
            data_set = overall_throughput
        else:
            data_set = list(res["graph_df"].values())[0]
        print("data set", data_set)
        return data_set, load, res

    # to get the ssid from the station name
    def get_ssid_list(self, station_names):
        ssid_list = []
        port_data = self.json_get('/ports/all/')['interfaces']
        interfaces_dict = dict()
        for port in port_data:
            interfaces_dict.update(port)
        for sta in station_names:
            if sta in interfaces_dict:
                ssid_list.append(interfaces_dict[sta]['ssid'])
            else:
                ssid_list.append('-')
        return ssid_list

    def generate_report(self, data, input_setup_info, report_path='', result_dir_name='Throughput_Qos_Test_report'):
        # getting ssid list for devices, on which the test ran
        self.ssid_list = self.get_ssid_list(self.sta_list)

        data_set, load, res = self.generate_graph_data_set(data)

        report = lf_report(_output_pdf="throughput_qos.pdf", _output_html="throughput_qos.html", _path=report_path,
                           _results_dir_name=result_dir_name)
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))
        report.set_title("Throughput QOS")
        report.build_banner()
        # objective title and description
        report.set_obj_html(_obj_title="Objective",
                            _obj="The objective of the QoS (Quality of Service) traffic throughput test is to measure the maximum"
                            " achievable throughput of a network under specific QoS settings and conditions.By conducting"
                            " this test, we aim to assess the capacity of network to handle high volumes of traffic while"
                            " maintaining acceptable performance levels,ensuring that the network meets the required QoS"
                            " standards and can adequately support the expected user demands.")
        report.build_objective()

        test_setup_info = {
            "Number of Stations": self.num_stations_2g + self.num_stations_5g + self.num_stations_6g,
            "AP Model": self.ap_name,
            "SSID_2.4GHz": self.ssid_2g,
            "SSID_5GHz": self.ssid_5g,
            "SSID_6GHz": self.ssid_6g,
            "Traffic Duration in hours": round(int(self.test_duration) / 3600, 2),
            "Security_2.4GHz": self.security_2g,
            "Security_5GHz": self.security_5g,
            "Security_6GHz": self.security_6g,
            "Protocol": (self.traffic_type.strip("lf_")).upper(),
            "Traffic Direction": self.direction,
            "TOS": self.tos,
            "Per TOS Load in Mbps": load
        }
        report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
        report.set_table_title(
            f"Overall {self.direction} throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
        report.build_table_title()
        df_throughput = pd.DataFrame(res["throughput_table_df"])
        report.set_table_dataframe(df_throughput)
        report.build_table()
        for key in res["graph_df"]:
            report.set_obj_html(
                _obj_title=f"Overall {self.direction} throughput for {len(self.sta_list)} clients for {key} band with different TOS.",
                _obj=f"The below graph represents overall {self.direction} throughput for all "
                     "connected stations running BK, BE, VO, VI traffic with different "
                     "intended loads per station – {}".format(
                         "".join(str(key))))
        report.build_objective()
        print("data set", res["graph_df"][key][0])
        graph = lf_bar_graph(_data_set=data_set,
                             _xaxis_name="Load per Type of Service",
                             _yaxis_name="Throughput (Mbps)",
                             _xaxis_categories=["BK,BE,VI,VO"],
                             _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                             _graph_image_name=f"tos_{self.direction}_{key}Hz",
                             _label=["BK", "BE", "VI", "VO"],
                             _xaxis_step=1,
                             _graph_title=f"Overall {self.direction} throughput – BK,BE,VO,VI traffic streams",
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

        print("graph name {}".format(graph_png))

        report.set_graph_image(graph_png)
        # need to move the graph image to the results directory
        report.move_graph_image()
        report.set_csv_filename(graph_png)
        report.move_csv_file()
        report.build_graph()
        self.generate_individual_graph(res, report)
        report.test_setup_table(test_setup_data=input_setup_info, value="Information")
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()

    def generate_individual_graph(self, res, report):
        print("res", res)
        load = ""
        upload_list, download_list, individual_upload_list, individual_download_list = [], [], [], []
        individual_set, colors, labels = [], [], []
        individual_drop_a_list, individual_drop_b_list = [], []

        list = [[], [], [], []]
        data_set = {}
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        for case in self.test_case:
            print("case", case)
            if self.direction == 'Upload':
                load = rate_up
                data_set = res[case]['test_results'][0][1]
                for _ in range(len(self.sta_list)):
                    individual_download_list.append('0')
            else:
                if self.direction == "Download":
                    load = rate_down
                    data_set = res[case]['test_results'][0][0]
                    for _ in range(len(self.sta_list)):
                        individual_upload_list.append('0')
            print("data set", data_set)
            tos_type = ['Background', 'Besteffort', 'Video', 'Voice']
            load_list = []
            traffic_type_list = []
            traffic_direction_list = []
            bk_tos_list = []
            be_tos_list = []
            vi_tos_list = []
            vo_tos_list = []
            traffic_type = (self.traffic_type.strip("lf_")).upper()
            for client in range(len(self.sta_list)):
                upload_list.append(rate_up)
                download_list.append(rate_down)
                traffic_type_list.append(traffic_type.upper())
                bk_tos_list.append(tos_type[0])
                be_tos_list.append(tos_type[1])
                vi_tos_list.append(tos_type[2])
                vo_tos_list.append(tos_type[3])
                load_list.append(load)
                traffic_direction_list.append(self.direction)
            print(traffic_type_list, traffic_direction_list, bk_tos_list, be_tos_list, vi_tos_list, vo_tos_list)
            if self.direction == "Bi-direction":
                load = 'Upload' + ':' + rate_up + ',' + 'Download' + ':' + rate_down
                for key in res[case]['test_results'][0][0]:
                    list[0].append(res[case]['test_results'][0][0][key]['VI'])
                    list[1].append(res[case]['test_results'][0][0][key]['VO'])
                    list[2].append(res[case]['test_results'][0][0][key]['BK'])
                    list[3].append(res[case]['test_results'][0][0][key]['BE'])
                for key in res[case]['test_results'][0][1]:
                    list[0].append(res[case]['test_results'][0][1][key]['VI'])
                    list[1].append(res[case]['test_results'][0][1][key]['VO'])
                    list[2].append(res[case]['test_results'][0][1][key]['BK'])
                    list[3].append(res[case]['test_results'][0][1][key]['BE'])
            x_fig_size = 15
            y_fig_size = (self.num_stations_2g + self.num_stations_5g + self.num_stations_6g) * .5 + 4
            if len(res.keys()) > 0:
                if "throughput_table_df" in res:
                    res.pop("throughput_table_df")
                if "graph_df" in res:
                    res.pop("graph_df")
                    print("res", res)
                    print("load", load)
                for key in res:
                    if "BK" in self.tos:
                        if self.direction == "Bi-direction":
                            individual_set = list[2]
                            individual_download_list = individual_set[0]
                            individual_upload_list = individual_set[1]
                            individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['BK']
                            individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['BK']
                            colors = ['orange', 'wheat']
                            labels = ["Download", "Upload"]
                        else:
                            individual_set = [data_set[load]['BK']]
                            colors = ['orange']
                            labels = ['BK']
                            if self.direction == "Upload":
                                individual_upload_list = [data_set[load]['BK']][0]
                                individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['BK']
                            elif self.direction == "Download":
                                individual_download_list = [data_set[load]['BK']][0]
                                individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['BK']
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BK(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BK "
                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                            f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=individual_set, _xaxis_name="Throughput in Mbps",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in self.sta_list],
                                                        _yaxis_label=[i for i in self.sta_list],
                                                        _label=labels,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _yticks_rotation=None,
                                                        _graph_title="Individual {} throughput for BK(WIFI) traffic - {} clients".format(
                                                            self.direction, key),
                                                        _title_size=16,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _color_name=colors,
                                                        _show_bar_value=True,
                                                        _enable_csv=True,
                                                        _graph_image_name="bk_{}".format(self.direction),
                                                        _color_edge=['black'],
                                                        _color=colors)
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        report.set_graph_image(graph_png)
                        # need to move the graph image to the results
                        report.move_graph_image()
                        report.set_csv_filename(graph_png)
                        report.move_csv_file()
                        report.build_graph()
                        report.set_table_title(" TOS : Background ")
                        report.build_table_title()
                        bk_dataframe = {
                            " Client Name ": self.sta_list,
                            " Mac ": self.mac_list,
                            " Channel ": self.channel_list,
                            " SSID ": self.ssid_list,
                            " Type of traffic ": bk_tos_list,
                            " Traffic Direction ": traffic_direction_list,
                            " Traffic Protocol ": traffic_type_list,
                            " Offered upload rate(Mbps) ": upload_list,
                            " Offered download rate(Mbps) ": download_list,
                            " Observed upload rate(Mbps) ": individual_upload_list,
                            " Observed download rate(Mbps)": individual_download_list
                        }
                        if self.direction == "Bi-direction":
                            bk_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            bk_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        else:
                            if self.direction == "Upload":
                                bk_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            elif self.direction == "Download":
                                bk_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        dataframe1 = pd.DataFrame(bk_dataframe)
                        report.set_table_dataframe(dataframe1)
                        report.build_table()
                    if "BE" in self.tos:
                        if self.direction == "Bi-direction":
                            individual_set = list[3]
                            individual_download_list = individual_set[0]
                            individual_upload_list = individual_set[1]
                            individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['BE']
                            individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['BE']
                            colors = ['lightcoral', 'mistyrose']
                            labels = ['Download', 'Upload']
                        else:
                            individual_set = [data_set[load]['BE']]
                            colors = ['violet']
                            labels = ['BE']
                            if self.direction == "Upload":
                                individual_upload_list = [data_set[load]['BE']][0]
                                individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['BE']
                            elif self.direction == "Download":
                                individual_download_list = [data_set[load]['BE']][0]
                                individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['BE']
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BE(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BE "
                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                            f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=individual_set, _xaxis_name="Throughput in Mbps",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in self.sta_list],
                                                        _yaxis_label=[i for i in self.sta_list],
                                                        _label=labels,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _graph_title="Individual {} throughput for BE(WIFI) traffic - {} clients".format(
                                                            self.direction, key),
                                                        _title_size=16,
                                                        _yticks_rotation=None,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _color_name=colors,
                                                        _show_bar_value=True,
                                                        _enable_csv=True,
                                                        _graph_image_name="be_{}".format(self.direction),
                                                        _color_edge=['black'],
                                                        _color=colors)
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        report.set_graph_image(graph_png)
                        # need to move the graph image to the results
                        report.move_graph_image()
                        report.set_csv_filename(graph_png)
                        report.move_csv_file()
                        report.build_graph()
                        report.set_table_title(" TOS : Besteffort ")
                        report.build_table_title()
                        be_dataframe = {
                            " Client Name ": self.sta_list,
                            " Mac ": self.mac_list,
                            " Channel ": self.channel_list,
                            " SSID ": self.ssid_list,
                            " Type of traffic ": be_tos_list,
                            " Traffic Direction ": traffic_direction_list,
                            " Traffic Protocol ": traffic_type_list,
                            " Offered upload rate(Mbps) ": upload_list,
                            " Offered download rate(Mbps) ": download_list,
                            " Observed upload rate(Mbps) ": individual_upload_list,
                            " Observed download rate(Mbps)": individual_download_list
                        }
                        if self.direction == "Bi-direction":
                            be_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            be_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        else:
                            if self.direction == "Upload":
                                be_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            elif self.direction == "Download":
                                be_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        dataframe2 = pd.DataFrame(be_dataframe)
                        report.set_table_dataframe(dataframe2)
                        report.build_table()
                    if "VI" in self.tos:
                        if self.direction == "Bi-direction":
                            individual_set = list[0]
                            individual_download_list = individual_set[0]
                            individual_upload_list = individual_set[1]
                            individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['VI']
                            individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['VI']
                            colors = ['steelblue', 'lightskyblue']
                            labels = ['Download', 'Upload']
                        else:
                            individual_set = [data_set[load]['VI']]
                            colors = ['steelblue']
                            labels = ['VI']
                            if self.direction == "Upload":
                                individual_upload_list = [data_set[load]['VI']][0]
                                individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['VI']
                            elif self.direction == "Download":
                                individual_download_list = [data_set[load]['VI']][0]
                                individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['VI']
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VI(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VI "
                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                            f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=individual_set, _xaxis_name="Throughput in Mbps",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in self.sta_list],
                                                        _yaxis_label=[i for i in self.sta_list],
                                                        _label=labels,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _graph_title="Individual {} throughput for VI(WIFI) traffic - {} clients".format(
                                                            self.direction, key),
                                                        _title_size=16,
                                                        _yticks_rotation=None,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _show_bar_value=True,
                                                        _color_name=colors,
                                                        _enable_csv=True,
                                                        _graph_image_name="video_{}".format(self.direction),
                                                        _color_edge=['black'],
                                                        _color=colors)
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        report.set_graph_image(graph_png)
                        # need to move the graph image to the results
                        report.move_graph_image()
                        report.set_csv_filename(graph_png)
                        report.move_csv_file()
                        report.build_graph()
                        report.set_table_title(" TOS : Video ")
                        report.build_table_title()
                        video_dataframe = {
                            " Client Name ": self.sta_list,
                            " Mac ": self.mac_list,
                            " Channel ": self.channel_list,
                            " SSID ": self.ssid_list,
                            " Type of traffic ": vi_tos_list,
                            " Traffic Direction ": traffic_direction_list,
                            " Traffic Protocol ": traffic_type_list,
                            " Offered upload rate(Mbps) ": upload_list,
                            " Offered download rate(Mbps) ": download_list,
                            " Observed upload rate(Mbps) ": individual_upload_list,
                            " Observed download rate(Mbps)": individual_download_list
                        }
                        if self.direction == "Bi-direction":
                            video_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            video_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        else:
                            if self.direction == "Upload":
                                video_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            elif self.direction == "Download":
                                video_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        dataframe3 = pd.DataFrame(video_dataframe)
                        report.set_table_dataframe(dataframe3)
                        report.build_table()
                    if "VO" in self.tos:
                        if self.direction == "Bi-direction":
                            individual_set = list[1]
                            individual_download_list = individual_set[0]
                            individual_upload_list = individual_set[1]
                            individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['VO']
                            individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['VO']
                            colors = ['grey', 'lightgrey']
                            labels = ['Download', 'Upload']
                        else:
                            individual_set = [data_set[load]['VO']]
                            colors = ['grey']
                            labels = ['VO']
                            if self.direction == "Upload":
                                individual_upload_list = [data_set[load]['VO']][0]
                                individual_drop_b_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_b']['VO']
                            elif self.direction == "Download":
                                individual_download_list = [data_set[load]['VO']][0]
                                individual_drop_a_list = res[case]['test_results'][0][2]['drop_per']['rx_drop_a']['VO']
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VO(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VO "
                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                            f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=individual_set, _xaxis_name="Throughput in Mbps",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in self.sta_list],
                                                        _yaxis_label=[i for i in self.sta_list],
                                                        _label=labels,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _yticks_rotation=None,
                                                        _graph_title="Individual {} throughput for VO(WIFI) traffic - {} clients".format(
                                                            self.direction, key),
                                                        _title_size=16,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _show_bar_value=True,
                                                        _color_name=colors,
                                                        _enable_csv=True,
                                                        _graph_image_name="voice_{}".format(self.direction),
                                                        _color_edge=['black'],
                                                        _color=colors)
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        report.set_graph_image(graph_png)
                        # need to move the graph image to the results
                        report.move_graph_image()
                        report.set_csv_filename(graph_png)
                        report.move_csv_file()
                        report.build_graph()
                        report.set_table_title(" TOS : Voice ")
                        report.build_table_title()
                        voice_dataframe = {
                            " Client Name ": self.sta_list,
                            " Mac ": self.mac_list,
                            " Channel ": self.channel_list,
                            " SSID ": self.ssid_list,
                            " Type of traffic ": vo_tos_list,
                            " Traffic Direction ": traffic_direction_list,
                            " Traffic Protocol ": traffic_type_list,
                            " Offered upload rate(Mbps) ": upload_list,
                            " Offered download rate(Mbps) ": download_list,
                            " Observed upload rate(Mbps) ": individual_upload_list,
                            " Observed download rate(Mbps)": individual_download_list
                        }

                        if self.direction == "Bi-direction":
                            voice_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            voice_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        else:
                            if self.direction == "Upload":
                                voice_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            elif self.direction == "Download":
                                voice_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        dataframe4 = pd.DataFrame(voice_dataframe)
                        report.set_table_dataframe(dataframe4)
                        report.build_table()

            else:
                print("No individual graph to generate.")


def parse_args():
    """Parse CLI arguments."""
    parser = Realm.create_basic_argparse(
        prog='throughput_QOS.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations and endpoints and runs L3 traffic with various IP type of service(BK |  BE | Video | Voice)
            ''',
        description='''\
NAME:       throughput_qos.py

PURPOSE:    Configure WiFi throughput tests with varying ToS, rate, direction and more.
            Includes support for creating basic stations (open and personal authentication).

NOTES:      Desired TOS must be specified with abbreviated name in all capital letters,
            for example '--tos "BK,VI,BE,VO"'

            Stations will not be created unless the '--create_sta' argument is specified.

            For running the test in dual-band and tri-band configurations, --bands dualband,
            the number of stations used on each band will be split across the number of utilized bands.
            For example, if '--num_stations 64' is specified, then 32 2.4GHz and 32 5GHz stations will be used.

EXAMPLES:   # Run download scenario with Voice TOS in 2.4GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --bands 2.4g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_udp --tos "VO" --create_sta

            # Run download scenario with Voice and Video TOS in 5GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_5g wiphy1
                --ssid_5g Cisco --passwd_5g cisco@123 --security_5g wpa2 --bands 5g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

            # Run download scenario with Voice and Video TOS in 6GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_6g wiphy1
                --ssid_6g Cisco --passwd_6g cisco@123 --security_6g wpa2 --bands 6g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

            # Run upload scenario with Background, Best Effort, Video, and Voice TOS in 2.4GHz and 5GHz bands
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g cisco@123
                --security_5g wpa2 --bands dualband --upstream eth1 --test_duration 1m --download 0 --upload 1000000
                --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

            # Run upload scenario with Background, Best Effort, Video and Voice TOS in 2.4GHz and 5GHz bands with 'Open' security
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
                --ssid_2g Cisco --passwd_2g [BLANK] --security_2g open --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g [BLANK]
                --security_5g open --bands dualband --upstream eth1 --test_duration 1m --download 0 --upload 1000000
                --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

            # Run bi-directional scenario with Video and Voice TOS in 6GHz band
            ./throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_6g wiphy1
                --ssid_6g Cisco --passwd_6g cisco@123 --security_6g wpa2 --bands 6g --upstream eth1 --test_duration 1m
                --download 1000000 --upload 10000000 --traffic_type lf_udp --tos "VO,VI" --create_sta

SCRIPT_CLASSIFICATION:
            Test

SCRIPT_CATEGORIES:
            Performance,  Functional, Report Generation

STATUS:     Beta Release

VERIFIED_ON:
            Working date:   03/08/2023
            Build version:  5.4.6
            kernel version: 6.2.16+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc
''')
    parser.add_argument('--mode', help='Used to force mode of stations', default="0")
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    parser.add_argument('--download', help='--download traffic load per connection (download rate)', default="0")
    parser.add_argument('--upload', help='--upload traffic load per connection (upload rate)', default="0")
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    parser.add_argument('--create_sta', help='Used to force a connection to a particular AP', action='store_true')
    parser.add_argument('--sta_names', help='Used to force a connection to a particular AP', default="sta0000")
    parser.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    parser.add_argument('--bands', help='used to run on multiple radio bands,can be used with multiple stations', default="2.4G, 5G, 6G, DUALBAND, TRIBAND", required=False)
    parser.add_argument('--tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    parser.add_argument('--ssid_2g', help="ssid for  2.4Ghz band")
    parser.add_argument('--security_2g', help="security type for  2.4Ghz band")
    parser.add_argument('--passwd_2g', help="password for 2.4Ghz band")
    parser.add_argument('--ssid_6g', help="ssid for  6Ghz band")
    parser.add_argument('--security_6g', help="security type for  6Ghz band")
    parser.add_argument('--passwd_6g', help="password for 6Ghz band")
    parser.add_argument('--ssid_5g', help="ssid for  5Ghz band")
    parser.add_argument('--security_5g', help="security type  for  5Ghz band")
    parser.add_argument('--passwd_5g', help="password for  5Ghz band")
    parser.add_argument('--num_stations_2g', help="number of 2GHz band stations", type=int, default=0, required=False)
    parser.add_argument('--num_stations_5g', help="number of 5GHz band stations", type=int, default=0, required=False)
    parser.add_argument('--num_stations_6g', help="number of 6GHz band stations", type=int, default=0, required=False)
    parser.add_argument('--radio_2g', help="radio which supports 2.4G bandwidth", default="wiphy0")
    parser.add_argument('--radio_5g', help="radio which supports 5G bandwidth", default="wiphy1")
    parser.add_argument('--radio_6g', help="radio which supports 6G bandwidth", default="wiphy2")
    parser.add_argument('--initial_band_pref', help="if given,2G clients would have only 2G band preference, so on for 5G and 6G", required=False, action='store_true', default=False)

    return parser.parse_args()


def main():
    args = parse_args()

    help_summary = "The Throughput QoS test is designed to measure performance of an Access Point " \
                   "while running traffic with different types of services like voice, video, best effort, background. " \
                   "The test allows the user to run layer3 traffic for different ToS in upload, download and bi-direction " \
                   "scenarios between AP and virtual devices. Throughputs for all the ToS are reported for individual clients " \
                   "along with the overall throughput for each ToS. The expected behavior is for the AP to be able to prioritize " \
                   "the ToS in an order of voice, video, best effort and background. The test will create stations, create CX " \
                   "traffic between upstream port and stations, run traffic and generate a report."
    if args.help_summary:
        print(help_summary)
        exit(0)

    if args.num_stations_2g == 0 and args.num_stations_5g == 0 and args.num_stations_6g == 0:
        print('NUMBER OF STATIONS CANNOT BE EMPTY')
        exit(1)

    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    args.test_case = args.bands.split(',')
    test_results = {'test_results': []}
    loads = {}
    bands = []
    station_list = []
    data = {}

    if args.download and args.upload:
        loads = {'upload': str(args.upload).split(","), 'download': str(args.download).split(",")}

    elif args.download:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for _ in range(len(args.download)):
            loads['upload'].append(0)
    else:
        if args.upload:
            loads = {'upload': str(args.upload).split(","), 'download': []}
            for _ in range(len(args.upload)):
                loads['download'].append(0)
    print(loads)

    if args.bands is not None:
        bands = args.bands.split(',')

    if args.test_duration.endswith('s') or args.test_duration.endswith('S'):
        args.test_duration = int(args.test_duration[0:-1])
    elif args.test_duration.endswith('m') or args.test_duration.endswith('M'):
        args.test_duration = int(args.test_duration[0:-1]) * 60
    elif args.test_duration.endswith('h') or args.test_duration.endswith('H'):
        args.test_duration = int(args.test_duration[0:-1]) * 60 * 60
    elif args.test_duration.endswith(''):
        args.test_duration = int(args.test_duration)

    test_start_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test started at: ", test_start_time)

    for i in range(len(bands)):
        if bands[i] == "2.4G" or bands[i] == "2.4g":
            args.bands = bands[i]
            args.mode = 13
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations_2g) - 1,
                                                      padding_number_=10000, radio=args.radio_2g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "5G" or bands[i] == "5g":
            args.bands = bands[i]
            args.mode = 14
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations_5g) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_5g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "6G" or bands[i] == "6g":
            args.bands = bands[i]
            args.mode = 14
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations_6g) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_6g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "dualband" or bands[i] == "DUALBAND":
            args.bands = bands[i]
            args.mode = 0
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=(int(args.num_stations_2g)) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_2g)
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=int(args.num_stations_2g),
                                                           end_id_=((int(args.num_stations_2g)) + (int(args.num_stations_5g))) - 1,
                                                           padding_number_=10000,
                                                           radio=args.radio_5g))
        elif bands[i] == "triband" or bands[i] == "TRIBAND":
            args.bands = bands[i]
            args.mode = 0
            if args.create_sta:
                # 2.4GHz stations
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0,
                                                      end_id_=int(args.num_stations_2g) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_2g)

                # 5GHz stations
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=int(args.num_stations_2g),
                                                           end_id_=int(args.num_stations_2g) + int(args.num_stations_5g) - 1,
                                                           padding_number_=10000,
                                                           radio=args.radio_5g))

                # 6GHz stations (Fixed to use `radio_6g`)
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=int(args.num_stations_2g) + int(args.num_stations_5g),
                                                           end_id_=int(args.num_stations_2g) + int(args.num_stations_5g) + int(args.num_stations_6g) - 1,
                                                           padding_number_=10000,
                                                           radio=args.radio_6g))

                print(station_list)

            else:
                station_list = args.sta_names.split(",")
        else:
            print("Band " + bands[i] + " Not Exist")
            exit(1)
        # ---------------------------------------#
        for index in range(len(loads["download"])):
            throughput_qos = ThroughputQOS(host=args.mgr,
                                           port=args.mgr_port,
                                           number_template="0000",
                                           ap_name=args.ap_name,
                                           num_stations_2g=int(args.num_stations_2g),
                                           num_stations_5g=int(args.num_stations_5g),
                                           num_stations_6g=int(args.num_stations_6g),
                                           sta_list=station_list,
                                           create_sta=args.create_sta,
                                           name_prefix="TOS-",
                                           upstream=args.upstream_port,
                                           ssid=args.ssid,
                                           password=args.passwd,
                                           security=args.security,
                                           ssid_2g=args.ssid_2g,
                                           password_2g=args.passwd_2g,
                                           security_2g=args.security_2g,
                                           ssid_5g=args.ssid_5g,
                                           password_5g=args.passwd_5g,
                                           security_5g=args.security_5g,
                                           ssid_6g=args.ssid_6g,
                                           password_6g=args.passwd_6g,
                                           security_6g=args.security_6g,
                                           radio_2g=args.radio_2g,
                                           radio_5g=args.radio_5g,
                                           radio_6g=args.radio_6g,
                                           test_duration=args.test_duration,
                                           use_ht160=False,
                                           side_a_min_rate=int(loads['upload'][index]),
                                           side_b_min_rate=int(loads['download'][index]),
                                           mode=args.mode,
                                           bands=args.bands,
                                           traffic_type=args.traffic_type,
                                           tos=args.tos,
                                           test_case=args.test_case,
                                           initial_band_pref=args.initial_band_pref,
                                           _debug_on=args.debug
                                           )
            throughput_qos.pre_cleanup()
            throughput_qos.build()

            # if args.create_sta:
            #     if not throughput_qos.passes():
            #         print(throughput_qos.get_fail_message())
            #         throughput_qos.exit_fail()

            throughput_qos.start(False, False)
            time.sleep(10)
            connections_download, connections_upload, drop_a_per, drop_b_per = throughput_qos.monitor()
            print("connections download", connections_download)
            print("connections upload", connections_upload)
            throughput_qos.stop()
            time.sleep(5)
            test_results['test_results'].append(throughput_qos.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
            data.update({bands[i]: test_results})
            input_setup_info = {
                "contact": "support@candelatech.com"
            }
            throughput_qos.generate_report(data=data, input_setup_info=input_setup_info)
            if args.create_sta:
                if not throughput_qos.passes():
                    print(throughput_qos.get_fail_message())
                    throughput_qos.exit_fail()
                # LFUtils.wait_until_ports_admin_up(port_list=station_list)
                if throughput_qos.passes():
                    throughput_qos.success()
                throughput_qos.cleanup()

    test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test ended at: ", test_end_time)


if __name__ == "__main__":
    main()
