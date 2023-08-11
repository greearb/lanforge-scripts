#!/usr/bin/env python3

"""
NAME: throughput_qos.py

PURPOSE: throughput_qos.py will create stations, layer3 cross connections and allows user to run the qos traffic
with particular tos on 2.4GHz and 5GHz bands in upload, download directions.

EXAMPLE-1:
Command Line Interface to run download scenario with tos : Voice , bands : 2.4GHz
python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_2g wiphy0
--ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --bands 2.4g --upstream eth1 --test_duration 1m
--download 1000000 --upload 0 --traffic_type lf_udp --tos "VO" --create_sta

EXAMPLE-2:
Command Line Interface to run download scenario with tos : Voice and Video , bands : 5GHz
python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_5g wiphy1
--ssid_5g Cisco --passwd_5g cisco@123 --security_5g wpa2 --bands 5g --upstream eth1 --test_duration 1m
--download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

EXAMPLE-3:
Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice , bands : 2.4GHz and 5GHz
python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
--ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g cisco@123
--security_5g wpa2 --bands both --upstream eth1 --test_duration 1m --download 0 --upload 1000000
--traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

EXAMPLE-4:
Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice , bands : 2.4GHz and 5GHz , security : open
python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
--ssid_2g Cisco --passwd_2g [BLANK] --security_2g open --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g [BLANK]
--security_5g open --bands both --upstream eth1 --test_duration 1m --download 0 --upload 1000000
--traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

SCRIPT_CLASSIFICATION :  Test

SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

NOTES:
1.Use './throughput_qos.py --help' to see command line usage and options
2.Please pass tos in CAPITALS as shown :"BK,VI,BE,VO" Eg : --tos "BK,BE,VO,VI"
3.Please enter the download or upload intended rate in bps
4.For running the test with --bands both, the number of stations created on each band will be based on entered --num_stations 
Eg: if --num_stations 64 is given then 32 stations will be created on 2.4GHz and 32 stations will be created on 5GHz band.

STATUS: BETA RELEASE

VERIFIED_ON:
Working date - 03/08/2023
Build version - 5.4.6
kernel version - 6.2.16+

License: Free to distribute and modify. LANforge systems must be licensed.
Copyright 2023 Candela Technologies Inc.

"""

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

import time
import argparse
from LANforge import LFUtils
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
from lf_report import lf_report
from lf_graph import lf_bar_graph_horizontal
from lf_graph import lf_bar_graph
from datetime import datetime, timedelta


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
                 create_sta=True,
                 name_prefix=None,
                 upstream=None,
                 num_stations=1,
                 sta_list=[],
                 radio_2g="wiphy0",
                 radio_5g="wiphy1",
                 host="localhost",
                 port=8080,
                 mode=0,
                 ap_name="",
                 direction="",
                 traffic_type=None,
                 side_a_min_rate=0, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="2m",
                 bands="2.4G, 5G, BOTH",
                 test_case={},
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
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
        self.radio_2g = radio_2g
        self.radio_5g = radio_5g
        self.num_stations = num_stations
        self.sta_list = sta_list
        self.create_sta = create_sta
        self.mode = mode
        self.ap_name = ap_name
        self.direction=direction
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
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list, debug=self.debug)
                if key == "BOTH" or key == "both":
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
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list[split:],
                                                debug=self.debug)
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

    def create_cx(self):
        count =0
        print("tos: {}".format(self.tos))
        for sta in range(len(self.sta_list)):
            for ip_tos in range(len(self.tos)):
                print("## ip_tos: {}".format(ip_tos))
                print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
                self.traffic_type, ip_tos, self.cx_profile.get_cx_count()))
                self.cx_profile.create(endp_type=self.traffic_type, side_a=[self.sta_list[sta]],
                                    side_b=self.upstream,
                                    sleep_time=0, tos=self.tos[ip_tos])
                count += 1
        print("cross connections with TOS type created.")

    def monitor(self):
        throughput, upload,download,upload_throughput,download_throughput,connections_upload, connections_download = {}, [], [],[],[],{},{}
        if (int(self.cx_profile.side_b_min_bps))!=0 and (int(self.cx_profile.side_a_min_bps))!=0:
            self.direction = "Bi-direction"
        elif int(self.cx_profile.side_b_min_bps) != 0:
            self.direction = "Download"
        else:
            if int(self.cx_profile.side_a_min_bps) != 0:
                self.direction = "Upload"
        print("direction",self.direction)
        if (self.test_duration is None) or (int(self.test_duration) <= 1):
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
        [(upload.append([]), download.append([])) for i in range(len(self.cx_profile.created_cx))]
        while datetime.now() < end_time:
            index += 1
            response = list(
                self.json_get('/cx/%s?fields=%s' % (
                    ','.join(self.cx_profile.created_cx.keys()), ",".join(['bps rx a', 'bps rx b']))).values())[2:]
            throughput[index] = list(
                map(lambda i: [x for x in i.values()], response))
            time.sleep(1)
        print("throughput", throughput)
        # # rx_rate list is calculated
        for index, key in enumerate(throughput):
            for i in range(len(throughput[key])):
                upload[i].append(throughput[key][i][1])
                download[i].append(throughput[key][i][0])
        print("Upload values", upload)
        print("Download Values", download)
        upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
        download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
        keys = list(connections_upload.keys())
        keys = list(connections_download.keys())

        for i in range(len(download_throughput)):
            connections_download.update({keys[i]: float(f"{(download_throughput[i] ):.2f}")})
        for i in range(len(upload_throughput)):
            connections_upload.update({keys[i]: float(f"{(upload_throughput[i] ):.2f}")})
        print("upload: ", upload_throughput)
        print("download: ", download_throughput)
        print("connections download",connections_download)
        print("connections",connections_upload)

        return connections_download,connections_upload
        
    def evaluate_qos(self, connections_download,connections_upload):
        case_upload = ""
        case_download = ""
        tos_download = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_download = {}
        rx_endps_download = {}
        delay = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps = {}
        rx_endps = {}
        tos_upload = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_upload = {}
        rx_endps_upload = {}
        if int(self.cx_profile.side_b_min_bps) != 0:
            case_download = str(int(self.cx_profile.side_b_min_bps) / 1000000)
        elif int(self.cx_profile.side_a_min_bps) != 0:
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
                    if temp in range(0, self.num_stations):
                        if int(self.cx_profile.side_b_min_bps) != 0:
                            tos_download[self.tos[0]].append(connections_download[sta])
                            tx_b_download[self.tos[0]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_download[self.tos[0]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                            delay[self.tos[0]].append(rx_endps_download['%s-A' % sta]['delay'])
                        else:
                            tos_download[self.tos[0]].append(float(0))
                            tx_b_download[self.tos[0]].append(int(0))
                            rx_a_download[self.tos[0]].append(int(0))
                            delay[self.tos[0]].append(int(0))
                    elif temp in range(self.num_stations, 2 * self.num_stations):
                        if len(self.tos) < 2:
                                break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[1]].append(connections_download[sta])
                                tx_b_download[self.tos[1]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[1]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[1]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[1]].append(float(0))
                                tx_b_download[self.tos[1]].append(int(0))
                                rx_a_download[self.tos[1]].append(int(0))
                                delay[self.tos[1]].append(int(0))
                    elif temp in range(2 * self.num_stations, 3 * self.num_stations):
                        if len(self.tos) < 3:
                                break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[2]].append(connections_download[sta])
                                tx_b_download[self.tos[2]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[2]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[2]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[2]].append(float(0))
                                tx_b_download[self.tos[2]].append(int(0))
                                rx_a_download[self.tos[2]].append(int(0))
                                delay[self.tos[2]].append(int(0))
                    elif temp in range(3 * self.num_stations, 4 * self.num_stations):
                        if len(self.tos) < 4:
                                break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[3]].append(connections_download[sta])
                                tx_b_download[self.tos[3]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[3]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[3]].append(rx_endps_download['%s-A' % sta]['delay'])
                            else:
                                tos_download[self.tos[3]].append(float(0))
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
                tos_download.update({'delay': delay})
            if int(self.cx_profile.side_a_min_bps) != 0:
                for i in range(len(endps)):
                    if i < len(endps) // 2:
                        tx_endps_upload.update(endps[i])
                    if i >= len(endps) // 2:
                        rx_endps_upload.update(endps[i])
                for sta in self.cx_profile.created_cx.keys():
                    temp = sta.rsplit('-', 1)
                    temp = int(temp[1])
                    if temp in range(0, self.num_stations):
                        if int(self.cx_profile.side_a_min_bps) != 0:
                            tos_upload[self.tos[0]].append(connections_upload[sta])
                            tx_b_upload[self.tos[0]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_upload[self.tos[0]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                            delay[self.tos[0]].append(rx_endps_upload['%s-A' % sta]['delay'])
                        else:
                            tos_upload[self.tos[0]].append(float(0))
                            tx_b_upload[self.tos[0]].append(int(0))
                            rx_a_upload[self.tos[0]].append(int(0))
                            delay[self.tos[0]].append(int(0))
                    elif temp in range(self.num_stations, 2 * self.num_stations):
                        if len(self.tos) < 2:
                                break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[1]].append(connections_upload[sta])
                                tx_b_upload[self.tos[1]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[1]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[1]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[1]].append(float(0))
                                tx_b_upload[self.tos[1]].append(int(0))
                                rx_a_upload[self.tos[1]].append(int(0))
                                delay[self.tos[1]].append(int(0))
                    elif temp in range(2 * self.num_stations, 3 * self.num_stations):
                        if len(self.tos) < 3:
                                break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[2]].append(connections_upload[sta])
                                tx_b_upload[self.tos[2]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[2]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[2]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[2]].append(float(0))
                                tx_b_upload[self.tos[2]].append(int(0))
                                rx_a_upload[self.tos[2]].append(int(0))
                                delay[self.tos[2]].append(int(0))
                    elif temp in range(3 * self.num_stations, 4 * self.num_stations):
                        if len(self.tos) < 4:
                                break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[3]].append(connections_upload[sta])
                                tx_b_upload[self.tos[3]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[3]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                                delay[self.tos[3]].append(rx_endps_upload['%s-A' % sta]['delay'])
                            else:
                                tos_upload[self.tos[3]].append(float(0))
                                tx_b_upload[self.tos[3]].append(int(0))
                                rx_a_upload[self.tos[3]].append(int(0))
                                delay[self.tos[3]].append(int(0))
                tos_upload.update({"bkQOS": float(f"{sum(tos_upload['BK']):.2f}")})
                tos_upload.update({"beQOS": float(f"{sum(tos_upload['BE']):.2f}")})
                tos_upload.update({"videoQOS": float(f"{sum(tos_upload['VI']):.2f}")})
                tos_upload.update({"voiceQOS": float(f"{sum(tos_upload['VO']):.2f}")})
                tos_upload.update({"bkDELAY": sum(delay['BK'])})
                tos_upload.update({"beDELAY": sum(delay['BE'])})
                tos_upload.update({"videoDELAY": sum(delay['VI'])})
                tos_upload.update({"voiceDELAY": sum(delay['VO'])})
                tos_upload.update({'tx_b': tx_b_upload})
                tos_upload.update({'rx_a': rx_a_upload})
        else:
            print("no RX values available to evaluate QOS")
        key_upload = case_upload + " " + "Mbps"
        key_download = case_download + " " + "Mbps"
        return {key_download: tos_download},{key_upload: tos_upload}

    def set_report_data(self, data):
        print(data)
        rate_down= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        rate_up= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')
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
            throughput = []
            for case in self.test_case:
                throughput_df = [[], [], [], []]
                pkt_loss_df = [[], [], [], []]
                latency_df = [[], [], [], []]
                if case == "2.4g" or case == "2.4G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("bgn-AX")
                elif case == "5g" or case == "5G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("an-AX")
                elif case == "both" or case == "BOTH":
                    num_stations.append("{} + {}".format(str(len(self.sta_list) // 2), str(len(self.sta_list) // 2)))
                    mode.append("bgn-AX + an-AX")
                for key in res[case]['test_results'][0][1]:
                    # if case == "both" or case == "BOTH":
                    #     key
                    if int(self.cx_profile.side_a_min_bps) != 0:
                        print(res[case]['test_results'][0][1])
                        throughput.append(
                            "BK : {}, BE : {}, VI: {}, VO: {}".format(res[case]['test_results'][0][1][rate_up]["bkQOS"],
                                                                    res[case]['test_results'][0][1][rate_up]["beQOS"],
                                                                    res[case]['test_results'][0][1][rate_up][
                                                                        "videoQOS"],
                                                                    res[case]['test_results'][0][1][rate_up][
                                                                        "voiceQOS"]))
                        throughput_df[0].append(res[case]['test_results'][0][1][rate_up]['bkQOS'])
                        throughput_df[1].append(res[case]['test_results'][0][1][rate_up]['beQOS'])
                        throughput_df[2].append(res[case]['test_results'][0][1][rate_up]['videoQOS'])
                        throughput_df[3].append(res[case]['test_results'][0][1][rate_up]['voiceQOS'])
                        
                        table_df.update({"No of Stations": []})
                        #table_df.update({"Mode": []})
                        table_df.update({"Throughput for Load {}".format(rate_up): []})
                        graph_df.update({case: [throughput_df, pkt_loss_df, latency_df]})
                        print(throughput)
                        table_df.update({"No of Stations": num_stations})
                        #table_df.update({"Mode": mode})
                        for i in self.test_case:
                            count = 0
                            for key in res[i]:
                                table_df["Throughput for Load {}".format(rate_up)].append(throughput[count])
                                count += 1
                        res_copy=copy.copy(res)
                        res_copy.update({"throughput_table_df": table_df})
                        res_copy.update({"graph_df": graph_df})
                for key in res[case]['test_results'][0][0]:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        print(res[case]['test_results'][0][0])
                        throughput.append(
                                "BK : {}, BE : {}, VI: {}, VO: {}".format(res[case]['test_results'][0][0][rate_down]["bkQOS"],
                                                                        res[case]['test_results'][0][0][rate_down]["beQOS"],
                                                                        res[case]['test_results'][0][0][rate_down][
                                                                            "videoQOS"],
                                                                        res[case]['test_results'][0][0][rate_down][
                                                                            "voiceQOS"]))
                        throughput_df[0].append(res[case]['test_results'][0][0][rate_down]['bkQOS'])
                        throughput_df[1].append(res[case]['test_results'][0][0][rate_down]['beQOS'])
                        throughput_df[2].append(res[case]['test_results'][0][0][rate_down]['videoQOS'])
                        throughput_df[3].append(res[case]['test_results'][0][0][rate_down]['voiceQOS'])
                    
                        table_df.update({"No of Stations": []})
                        #table_df.update({"Mode": []})
                        table_df.update({"Throughput for Load {}".format(rate_down): []})
                        graph_df.update({case: [throughput_df, pkt_loss_df, latency_df]})
                        print(throughput)
                        table_df.update({"No of Stations": num_stations})
                        #table_df.update({"Mode": mode})
                        for i in self.test_case:
                            count = 0
                            for key in res[i]:
                                table_df["Throughput for Load {}".format(rate_down)].append(throughput[count])
                                count += 1
                        res_copy=copy.copy(res)
                        res_copy.update({"throughput_table_df": table_df})
                        res_copy.update({"graph_df": graph_df})
                        print("table_df",table_df)
        return res_copy

    def generate_report(self, data, input_setup_info):
        load=''
        rate_down= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        rate_up= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')
        if self.direction == 'Upload':
            load=rate_up
        else:
            if self.direction =="Download":
                load=rate_down
        res = self.set_report_data(data)
        report = lf_report(_output_pdf="throughput_qos.pdf", _output_html="throughput_qos.html")
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
        "Number of Stations" : self.num_stations,
        "AP Model": self.ap_name,
        "SSID_2.4GHz": self.ssid_2g,
        "SSID_5GHz": self.ssid_5g,
        "Traffic Duration in hours" : round(int(self.test_duration)/3600,2),
        "Security_2.4GHz" : self.security_2g,
        "Security_5GHz" : self.security_5g,
        "Protocol" : (self.traffic_type.strip("lf_")).upper(),
        "Traffic Direction" : self.direction,
        "TOS" : self.tos,
        "Per TOS Load in Mbps" : load
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
            print("data set",res["graph_df"][key][0])
            xaxis_list=list(res["graph_df"].keys())
            print("keys",xaxis_list)

            graph = lf_bar_graph(_data_set=res["graph_df"][key][0],
                                 _xaxis_name="Load per Type of Service",
                                 _yaxis_name="Throughput (Mbps)",
                                 _xaxis_categories=xaxis_list,
                                 _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                 _graph_image_name=f"tos_{self.direction}_{key}Hz",
                                 _label=["BK", "BE", "VI", "VO"],
                                 _xaxis_step=1,
                                 _graph_title=f"Overall {self.direction} throughput – BK,BE,VO,VI traffic streams",
                                 _title_size=16,
                                 _color=['orange', 'olivedrab', 'steelblue', 'blueviolet'],
                                 _color_edge='black',
                                 _bar_width=0.15,
                                 _figsize=(18, 6),
                                 _legend_loc="best",
                                 _legend_box=(1.0, 1.0),
                                 _dpi=96,
                                 _show_bar_value=True,
                                 _enable_csv=True,
                                 _color_name=['orange', 'olivedrab', 'steelblue', 'blueviolet'])
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
        load=""
        data_set={}
        rate_down= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        rate_up= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')
        for case in self.test_case:
            if self.direction == 'Upload':
                load=rate_up
                data_set=res[case]['test_results'][0][1]
            else:
                if self.direction =="Download":
                    load=rate_down
                    data_set=res[case]['test_results'][0][0]
            tos_type = ['Background','Besteffort','Video','Voice']
            load_list = []
            traffic_type_list = []
            traffic_direction_list = []
            bk_tos_list = [] 
            be_tos_list = []
            vi_tos_list = [] 
            vo_tos_list = []
            traffic_type=(self.traffic_type.strip("lf_")).upper()
            for client in range(len(self.sta_list)):
                traffic_type_list.append(traffic_type.upper())
                bk_tos_list.append(tos_type[0])
                be_tos_list.append(tos_type[1])
                vi_tos_list.append(tos_type[2])
                vo_tos_list.append(tos_type[3])
                load_list.append(load)
                traffic_direction_list.append(self.direction)
            print(traffic_type_list,traffic_direction_list,bk_tos_list,be_tos_list,vi_tos_list,vo_tos_list)
            if len(res.keys()) > 0:
                if "throughput_table_df" in res:
                    res.pop("throughput_table_df")
                if "graph_df" in res:
                    res.pop("graph_df")
                    print("res",res)
                    print("load",load)
                    print("data set",data_set[load]['BE'])
                for key in res:
                    if "BK" in self.tos:
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BK(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BK "
                                f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['BK']], _xaxis_name="Throughput in Mbps",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in self.sta_list],
                                            _yaxis_label=[i for i in self.sta_list],
                                            _label=["BK"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="Individual {} throughput for BK(WIFI) traffic - {} clients".format(
                                                self.direction,key),
                                            _title_size=16,
                                            _figsize= (18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['orange'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="{}_bk_{}".format(key, load), _color_edge=['black'],
                                            _color=['orange'])
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
                            " Client Name " : self.sta_list,
                            " Type of traffic " : bk_tos_list,
                            " Traffic Direction " : traffic_direction_list,
                            " Traffic Protocol " : traffic_type_list,
                            " Intended Load (Mbps) " : load_list,
                            " Throughput (Mbps) " : data_set[load]['BK']
                        }

                        dataframe1 = pd.DataFrame(bk_dataframe)
                        report.set_table_dataframe(dataframe1)
                        report.build_table()
                    if "BE" in self.tos:
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BE(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BE "
                                f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['BE']], _xaxis_name="Throughput in Mbps",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in self.sta_list],
                                            _yaxis_label=[i for i in self.sta_list],
                                            _label=["BE"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _graph_title="Individual {} throughput for BE(WIFI) traffic - {} clients".format(
                                                self.direction,key),
                                            _title_size=16, 
                                            _yticks_rotation=None,
                                            _figsize=(18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['olivedrab'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="{}_be_{}".format(key, load), _color_edge=['black'],
                                            _color=['olivedrab'])
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
                            " Client Name " : self.sta_list,
                            " Type of traffic " : be_tos_list,
                            " Traffic Direction " : traffic_direction_list,
                            " Traffic Protocol " : traffic_type_list,
                            " Intended Load (Mbps) " : load_list,
                            " Throughput (Mbps) " : data_set[load]['BE']
                        }

                        dataframe2 = pd.DataFrame(be_dataframe)
                        report.set_table_dataframe(dataframe2)
                        report.build_table()
                    if "VI" in self.tos:
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VI(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VI "
                                f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['VI']], _xaxis_name="Throughput in Mbps",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in self.sta_list],
                                            _yaxis_label=[i for i in self.sta_list],
                                            _label=["Video"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _graph_title="Individual {} throughput for VI(WIFI) traffic - {} clients".format(
                                                self.direction,key),
                                            _title_size=16,
                                            _yticks_rotation=None,
                                            _figsize=(18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
                                            _color_name=['steelblue'],
                                            _enable_csv=True,
                                            _graph_image_name="{}_video_{}".format(key, load),
                                            _color_edge=['black'],
                                            _color=['steelblue'])
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
                            " Client Name " : self.sta_list,
                            " Type of traffic " : vi_tos_list,
                            " Traffic Direction " : traffic_direction_list,
                            " Traffic Protocol " : traffic_type_list,
                            " Intended Load (Mbps) " : load_list,
                            " Throughput (Mbps) " : data_set[load]['VI']
                        }

                        dataframe3 = pd.DataFrame(video_dataframe)
                        report.set_table_dataframe(dataframe3)
                        report.build_table()
                    if "VO" in self.tos:
                        report.set_obj_html(
                            _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VO(WiFi).",
                            _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VO "
                                f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                f"Throughput in Mbps”.")
                        report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['VO']], _xaxis_name="Throughput in Mbps",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in self.sta_list],
                                            _yaxis_label=[i for i in self.sta_list],
                                            _label=['Voice'],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="Individual {} throughput for VO(WIFI) traffic - {} clients".format(
                                                self.direction,key),
                                            _title_size=16,
                                            _figsize=(18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
                                            _color_name=['blueviolet'],
                                            _enable_csv=True,
                                            _graph_image_name="{}_voice_{}".format(key, load),
                                            _color_edge=['black'],
                                            _color=['blueviolet'])
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
                            " Client Name " : self.sta_list,
                            " Type of traffic " : vo_tos_list,
                            " Traffic Direction " : traffic_direction_list,
                            " Traffic Protocol " : traffic_type_list,
                            " Intended Load (Mbps) " : load_list,
                            " Throughput (Mbps) " : data_set[load]['VO']
                        }

                        dataframe4 = pd.DataFrame(voice_dataframe)
                        report.set_table_dataframe(dataframe4)
                        report.build_table()
                   
            else:
                print("No individual graph to generate.")


def main():
    parser = Realm.create_basic_argparse(
        prog='throughput_QOS.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations and endpoints and runs L3 traffic with various IP type of service(BK |  BE | Video | Voice)
            ''',
        description='''\
        
        NAME: throughput_qos.py

        PURPOSE: throughput_qos.py will create stations, layer3 cross connections and allows user to run the qos traffic
        with particular tos on 2.4GHz and 5GHz bands in upload, download directions.

        EXAMPLE-1:
        Command Line Interface to run download scenario with tos : Voice , bands : 2.4GHz
        python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_2g wiphy0
        --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --bands 2.4g --upstream eth1 --test_duration 1m 
        --download 1000000 --upload 0 --traffic_type lf_udp --tos "VO" --create_sta

        EXAMPLE-2:
        Command Line Interface to run download scenario with tos : Voice and Video , bands : 5GHz
        python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 32 --radio_5g wiphy1 
        --ssid_5g Cisco --passwd_5g cisco@123 --security_5g wpa2 --bands 5g --upstream eth1 --test_duration 1m 
        --download 1000000 --upload 0 --traffic_type lf_tcp --tos "VO,VI" --create_sta

        EXAMPLE-3:
        Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice , bands : 2.4GHz and 5GHz
        python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
        --ssid_2g Cisco --passwd_2g cisco@123 --security_2g wpa2 --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g cisco@123 
        --security_5g wpa2 --bands both --upstream eth1 --test_duration 1m --download 0 --upload 1000000
        --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

        EXAMPLE-4:
        Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice , bands : 2.4GHz and 5GHz , security : open
        python3 throughput_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --num_stations 64 --radio_2g wiphy0
        --ssid_2g Cisco --passwd_2g [BLANK] --security_2g open --radio_5g wiphy1 --ssid_5g Cisco --passwd_5g [BLANK] 
        --security_5g open --bands both --upstream eth1 --test_duration 1m --download 0 --upload 1000000
        --traffic_type lf_udp --tos "BK,BE,VI,VO" --create_sta

        SCRIPT_CLASSIFICATION :  Test

        SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

        NOTES:
        1.Use './throughput_qos.py --help' to see command line usage and options
        2.Please pass tos in CAPITALS as shown :"BK,VI,BE,VO" Eg : --tos "BK,BE,VO,VI"
        3.Please enter the download or upload intended rate in bps
        4.For running the test with --bands both, the number of stations created on each band will be based on entered --num_stations 
        Eg: if --num_stations 64 is given then 32 stations will be created on 2.4GHz and 32 stations will be created on 5GHz band.

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date - 03/08/2023
        Build version - 5.4.6
        kernel version - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.

''')
    parser.add_argument('--mode', help='Used to force mode of stations', default="0")
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=True)
    parser.add_argument('--download', help='--download traffic load per connection (download rate)',default="0")
    parser.add_argument('--upload', help='--upload traffic load per connection (upload rate)',default="0")
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    parser.add_argument('--create_sta', help='Used to force a connection to a particular AP', action='store_true')
    parser.add_argument('--sta_names', help='Used to force a connection to a particular AP', default="sta0000")
    parser.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    parser.add_argument('--bands', help='used to run on multiple radio bands,can be used with multiple stations',
                        default="2.4G, 5G, BOTH", required=True)
    parser.add_argument('--tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    parser.add_argument('--ssid_2g', help="ssid for  2.4Ghz band")
    parser.add_argument('--security_2g', help="security type for  2.4Ghz band")
    parser.add_argument('--passwd_2g', help="password for 2.4Ghz band")
    parser.add_argument('--ssid_5g', help="ssid for  5Ghz band")
    parser.add_argument('--security_5g', help="security type  for  5Ghz band")
    parser.add_argument('--passwd_5g', help="password for  5Ghz band")
    parser.add_argument('--radio_2g', help="radio which supports 2.4G bandwidth", default="wiphy0")
    parser.add_argument('--radio_5g', help="radio which supports 5G bandwidth", default="wiphy1")
    args = parser.parse_args()
    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    args.test_case = args.bands.split(',')
    test_results = {'test_results':[]}
    loads = {}
    bands = []
    station_list = []
    data = {}

    print(args.upload)
    if args.download and args.upload:
        loads = {'upload': str(args.upload).split(","), 'download': str(args.download).split(",")}

    elif args.download:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for i in range(len(args.download)):
            loads['upload'].append(0)
    else:
        if args.upload:
            loads = {'upload': str(args.upload).split(","), 'download': []}
            for i in range(len(args.upload)):
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
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000, radio=args.radio_2g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "5G" or bands[i] == "5g":
            args.bands = bands[i]
            args.mode = 14
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_5g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "BOTH" or bands[i] == "both":
            args.bands = bands[i]
            args.mode = 0
            if (int(args.num_stations) % 2) != 0:
                print("Number of stations for Both Band should be even in number.")
                exit(1)
            mid = int(args.num_stations) // 2
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=mid - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_2g)
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=mid,
                                                           end_id_=int(args.num_stations) - 1,
                                                           padding_number_=10000,
                                                           radio=args.radio_5g))
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
                                           num_stations=int(args.num_stations),
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
                                           radio_2g=args.radio_2g,
                                           radio_5g=args.radio_5g,
                                           test_duration=args.test_duration,
                                           use_ht160=False,
                                           side_a_min_rate=int(loads['upload'][index]),
                                           side_b_min_rate=int(loads['download'][index]),
                                           mode=args.mode,
                                           bands=args.bands,
                                           traffic_type=args.traffic_type,
                                           tos=args.tos,
                                           test_case=args.test_case,
                                           _debug_on=args.debug)
            throughput_qos.pre_cleanup()
            throughput_qos.build()

            # if args.create_sta:
            #     if not throughput_qos.passes():
            #         print(throughput_qos.get_fail_message())
            #         throughput_qos.exit_fail()

            throughput_qos.start(False, False)
            time.sleep(10)
            connections_download,connections_upload = throughput_qos.monitor()
            print("connections download",connections_download)
            print("connections upload",connections_upload)
            throughput_qos.stop()
            time.sleep(5)
            test_results['test_results'].append(throughput_qos.evaluate_qos(connections_download,connections_upload))
            data.update({bands[i]: test_results})
            if args.create_sta:
                if not throughput_qos.passes():
                    print(throughput_qos.get_fail_message())
                    throughput_qos.exit_fail()
                #LFUtils.wait_until_ports_admin_up(port_list=station_list)
                if throughput_qos.passes():
                    throughput_qos.success()
                throughput_qos.cleanup()

    test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test ended at: ", test_end_time)
   
    input_setup_info = {
        "contact": "support@candelatech.com"
    }
    throughput_qos.generate_report(data=data, input_setup_info=input_setup_info)


if __name__ == "__main__":
    main()

