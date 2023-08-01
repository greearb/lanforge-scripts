#!/usr/bin/env python3

"""
NAME: lf_interop_qos.py

        PURPOSE: lf_interop_qos.py will provide the available devices and allows user to run the qos traffic
        with particular tos on particular devices in upload, download directions.

        EXAMPLE-1:
        Command Line Interface to run download scenario with tos : Voice
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 0 
        --traffic_type lf_udp --tos "VO"

        EXAMPLE-2:
        Command Line Interface to run download scenario with tos : Voice and Video
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 0 
        --traffic_type lf_udp --tos "VO,VI"

        EXAMPLE-3:
        Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 0 --upload 1000000
        --traffic_type lf_udp --tos "BK,BE,VI,VO"

        SCRIPT_CLASSIFICATION :  Test

        SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

        NOTES:
        1.Use './lf_interop_qos.py --help' to see command line usage and options
        2.Please pass tos in CAPITALS as shown :"BK,VI,BE,VO"
        3.Please enter the download or upload rate in bps
        4.After passing cli, a list will be displayed on terminal which contains available resources to run test.
        The following sentence will be displayed
        Enter the desired resources to run the test:
        Please enter the port numbers seperated by commas ','.
        Example: 
        Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date - 01/07/2023
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
import logging

logger = logging.getLogger(__name__)

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
from lf_graph import lf_bar_graph
from lf_graph import lf_bar_graph_horizontal
from datetime import datetime, timedelta


class ThroughputQOS(Realm):
    def __init__(self,
                 tos,
                 ssid=None,
                 security=None,
                 password=None,
                 name_prefix=None,
                 upstream=None,
                 num_stations=10,
                 host="localhost",
                 port=8080,
                 ap_name="",
                 traffic_type=None,
                 direction="",
                 side_a_min_rate=0, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="2m",
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 user_list=[],real_client_list=[],hw_list=[],laptop_list=[],android_list=[],mac_list=[],windows_list=[],linux_list=[],
                 total_resources_list=[],working_resources_list=[],hostname_list=[],username_list=[],eid_list=[],
                 devices_available=[],input_devices_list=[],mac_id1_list=[],mac_id_list=[]):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.ap_name = ap_name
        self.traffic_type = traffic_type
        self.direction = direction
        self.tos = tos.split(",")
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
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate
        self.hw_list = hw_list
        self.laptop_list = laptop_list
        self.android_list = android_list
        self.mac_list = mac_list
        self.windows_list = windows_list
        self.linux_list = linux_list
        self.total_resources_list = total_resources_list
        self.working_resources_list = working_resources_list
        self.hostname_list = hostname_list
        self.username_list = username_list
        self.eid_list = eid_list
        self.devices_available = devices_available
        self.input_devices_list = input_devices_list
        self.real_client_list = real_client_list
        self.user_list = user_list
        self.mac_id_list = mac_id_list
        self.mac_id1_list = mac_id1_list

    def os_type(self):
        response = self.json_get("/resource/all")
        for key,value in response.items():
            if key == "resources":
                for element in value:
                    for a,b in element.items():
                        self.hw_list.append(b['hw version'])
        for hw_version in self.hw_list:                       
            if "Win" in hw_version:
                self.windows_list.append(hw_version)
            elif "Linux" in hw_version:
                self.linux_list.append(hw_version)
            elif "Apple" in hw_version:
                self.mac_list.append(hw_version)
            else:
                if hw_version != "":
                    self.android_list.append(hw_version)
        self.laptop_list = self.windows_list + self.linux_list + self.mac_list
        #print("laptop_list :",self.laptop_list)
        #print("android_list :",self.android_list)

    def phantom_check(self):
        port_eid_list, same_eid_list,original_port_list=[],[],[]
        response = self.json_get("/resource/all")
        for key,value in response.items():
            if key == "resources":
                for element in value:
                    for a,b in element.items():
                        if b['phantom'] == False :
                            self.working_resources_list.append(b["hw version"])
                            if "Win" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.windows_list.append(b['hw version'])
                                self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                self.devices_available.append(b['eid'] +" "+ b['hw version'] +" " +'Windows')
                            elif "Linux" in b['hw version']:
                                if ('ct' or 'lf') not in b['hostname']:
                                    self.eid_list.append(b['eid'])
                                    self.linux_list.append(b['hw version'])
                                    self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                    self.devices_available.append(b['eid'] +" "+ b['hw version'] +" " +'Linux')
                            elif "Apple" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.mac_list.append(b['hw version'])
                                self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                self.devices_available.append(b['eid'] +" "+ b['hw version'] +" " +'Apple')
                            else:
                                self.eid_list.append(b['eid'])
                                self.android_list.append(b['hw version'])  
                                self.username_list.append(b['eid']+ " " +b['user'])
                                self.devices_available.append(b['eid'] +" "+ b['hw version'] +" " +'android')
        #print("hostname list :",self.hostname_list)
        #print("username list :", self.username_list)
        #print("Available resources in resource tab :", self.devices_available)
        #print("eid_list : ",self.eid_list)
        #All the available resources are fetched from resource mgr tab ----

        response_port = self.json_get("/port/all")
        #print(response_port)
        mac_id1_list=[]
        for interface in response_port['interfaces']:
            for port,port_data in interface.items():
                if(not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0"):
                    for id in self.eid_list:
                        if(id+'.' in port):
                            original_port_list.append(port)
                            port_eid_list.append(str(self.name_to_eid(port)[0])+'.'+str(self.name_to_eid(port)[1]))
                            self.mac_id1_list.append(str(self.name_to_eid(port)[0])+'.'+str(self.name_to_eid(port)[1])+' '+port_data['mac'])
        #print("port eid list",port_eid_list)
        for i in range(len(self.eid_list)):
            for j in range(len(port_eid_list)):
                if self.eid_list[i] == port_eid_list[j]:
                    same_eid_list.append(self.eid_list[i])
        same_eid_list = [_eid + ' ' for _eid in same_eid_list]
        print("same eid list",same_eid_list)  
        #print("mac_id list",self.mac_id_list)
        #All the available ports from port manager are fetched from port manager tab ---

        for eid in same_eid_list:
            for device in self.devices_available:
                if eid in device:
                    print(eid + ' ' + device)
                    self.user_list.append(device)
        print("Available resources to run test : ",self.user_list)

        devices_list = input("Enter the desired resources to run the test:")
        #print("devices list",devices_list)
        resource_eid_list = devices_list.split(',')
        resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]
        resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
        #print("resource eid list",resource_eid_list)

        #User desired eids are fetched ---

        for eid in resource_eid_list1:
            for ports_m in original_port_list:
                if eid in ports_m:
                    self.input_devices_list.append(ports_m)
        print("input devices list",self.input_devices_list)
        
        # user desired real client list 1.1 wlan0 ---
        
        for i in resource_eid_list2:
            for j in range(len(self.devices_available)):
                if i in self.devices_available[j]:
                    self.real_client_list.append(self.devices_available[j])
        print("real client list", self.real_client_list)
        self.num_stations = len(self.real_client_list)

        for eid in resource_eid_list2:
            for i in self.mac_id1_list:
                if eid in i:
                    self.mac_id_list.append(i.strip(eid+' '))
        print("mac_id_list",self.mac_id_list)

        # user desired real client list 1.1 OnePlus, 1.1 Apple for report generation ---

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
    
    def cleanup(self):
        self.cx_profile.cleanup()
        
    def build(self):
        self.create_cx()
        print("cx build finished")

    def create_cx(self):
        print("tos: {}".format(self.tos))
        for ip_tos in self.tos:
            print("## ip_tos: {}".format(ip_tos))
            print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
                self.traffic_type, ip_tos, self.cx_profile.get_cx_count()))
            self.cx_profile.create(endp_type=self.traffic_type, side_a=self.input_devices_list,
                                   side_b=self.upstream,
                                   sleep_time=0, tos=ip_tos)
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

    def evaluate_qos(self, connections_download, connections_upload):
        case_upload = ""
        case_download = ""
        tos_download = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_download = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_download = {}
        rx_endps_download = {}
        tos_upload = {'VI': [], 'VO': [], 'BK': [], 'BE': []}
        tx_b_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        rx_a_upload = {'BK': [], 'BE': [], 'VI': [], 'VO': []}
        tx_endps_upload = {}
        rx_endps_upload = {}
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
                    if temp in range(0, len(self.input_devices_list)):
                        if int(self.cx_profile.side_b_min_bps) != 0:
                            tos_download[self.tos[0]].append(connections_download[sta])
                            tx_b_download[self.tos[0]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_download[self.tos[0]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                        else:
                            tos_download[self.tos[0]].append(float(0))
                            tx_b_download[self.tos[0]].append(int(0))
                            rx_a_download[self.tos[0]].append(int(0))
                    elif temp in range(len(self.input_devices_list), 2 * len(self.input_devices_list)):
                        if len(self.tos) < 2:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[1]].append(connections_download[sta])
                                tx_b_download[self.tos[1]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[1]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_download[self.tos[i+1]].append(float(0))
                                tx_b_download[self.tos[1]].append(int(0))
                                rx_a_download[self.tos[1]].append(int(0))
                    elif temp in range(2 * len(self.input_devices_list), 3 * len(self.input_devices_list)):
                        if len(self.tos) < 3:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[2]].append(connections_download[sta])
                                tx_b_download[self.tos[2]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[2]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_download[self.tos[2]].append(float(0))
                                tx_b_download[self.tos[2]].append(int(0))
                                rx_a_download[self.tos[2]].append(int(0))
                    elif temp in range(3 * len(self.input_devices_list), 4 * len(self.input_devices_list)):
                        if len(self.tos) < 4:
                            break
                        else:
                            if int(self.cx_profile.side_b_min_bps) != 0:
                                tos_download[self.tos[3]].append(connections_download[sta])
                                tx_b_download[self.tos[3]].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_download[self.tos[3]].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_download[self.tos[3]].append(float(0))
                                tx_b_download[self.tos[3]].append(int(0))
                                rx_a_download[self.tos[3]].append(int(0))
                tos_download.update({"bkQOS": float(f"{sum(tos_download['BK']):.2f}")})
                tos_download.update({"beQOS": float(f"{sum(tos_download['BE']):.2f}")})
                tos_download.update({"videoQOS": float(f"{sum(tos_download['VI']):.2f}")})
                tos_download.update({"voiceQOS": float(f"{sum(tos_download['VO']):.2f}")})
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
                    if temp in range(0, len(self.input_devices_list)):
                        if int(self.cx_profile.side_a_min_bps) != 0:
                            tos_upload[self.tos[0]].append(connections_upload[sta])
                            tx_b_upload[self.tos[0]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_upload[self.tos[0]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                        else:
                            tos_upload[self.tos[0]].append(float(0))
                            tx_b_upload[self.tos[0]].append(int(0))
                            rx_a_upload[self.tos[0]].append(int(0))
                    elif temp in range(len(self.input_devices_list), 2 * len(self.input_devices_list)):
                        if len(self.tos) < 2:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[1]].append(connections_upload[sta])
                                tx_b_upload[self.tos[1]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[1]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_upload[self.tos[i+1]].append(float(0))
                                tx_b_upload[self.tos[1]].append(int(0))
                                rx_a_upload[self.tos[1]].append(int(0))
                    elif temp in range(2 * len(self.input_devices_list), 3 * len(self.input_devices_list)):
                        if len(self.tos) < 3:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[2]].append(connections_upload[sta])
                                tx_b_upload[self.tos[2]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[2]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_upload[self.tos[2]].append(float(0))
                                tx_b_upload[self.tos[2]].append(int(0))
                                rx_a_upload[self.tos[2]].append(int(0))
                    elif temp in range(3 * len(self.input_devices_list), 4 * len(self.input_devices_list)):
                        if len(self.tos) < 4:
                            break
                        else:
                            if int(self.cx_profile.side_a_min_bps) != 0:
                                tos_upload[self.tos[3]].append(connections_upload[sta])
                                tx_b_upload[self.tos[3]].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                                rx_a_upload[self.tos[3]].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                            else:
                                tos_upload[self.tos[3]].append(float(0))
                                tx_b_upload[self.tos[3]].append(int(0))
                                rx_a_upload[self.tos[3]].append(int(0))
                
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
        return {key_download: tos_download},{key_upload: tos_upload}

    def set_report_data(self, data):
        rate_down= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        rate_up= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')
        res = {}
        if data is not None:
            res.update(data)
        else:
            print("No Data found to generate report!")
            exit(1)
        table_df = {}
        graph_df = {}
        throughput = []
        throughput_df = [[], [], [], []]
        if int(self.cx_profile.side_a_min_bps) != 0:
            print(res['test_results'][0][1])
            throughput.append(
                "BK : {}, BE : {}, VI: {}, VO: {}".format(res['test_results'][0][1][rate_up]["bkQOS"],
                                                            res['test_results'][0][1][rate_up]["beQOS"],
                                                            res['test_results'][0][1][rate_up][
                                                                "videoQOS"],
                                                            res['test_results'][0][1][rate_up][
                                                                "voiceQOS"]))
            throughput_df[0].append(res['test_results'][0][1][rate_up]['bkQOS'])
            throughput_df[1].append(res['test_results'][0][1][rate_up]['beQOS'])
            throughput_df[2].append(res['test_results'][0][1][rate_up]['videoQOS'])
            throughput_df[3].append(res['test_results'][0][1][rate_up]['voiceQOS'])               
            table_df.update({"No of Stations": []})
            table_df.update({"Throughput for Load {}".format(rate_up): []})
            graph_df.update({rate_up: [throughput_df]})
            
            table_df.update({"No of Stations": str(len(self.input_devices_list))})
            table_df["Throughput for Load {}".format(rate_up)].append(throughput)
            res_copy=copy.copy(res)
            res_copy.update({"throughput_table_df": table_df})
            res_copy.update({"graph_df": graph_df})
        if int(self.cx_profile.side_b_min_bps) != 0:
            print(res['test_results'][0][0])
            throughput.append(
                "BK : {}, BE : {}, VI: {}, VO: {}".format(res['test_results'][0][0][rate_down]["bkQOS"],
                                                            res['test_results'][0][0][rate_down]["beQOS"],
                                                            res['test_results'][0][0][rate_down][
                                                                "videoQOS"],
                                                            res['test_results'][0][0][rate_down][
                                                                "voiceQOS"]))
            throughput_df[0].append(res['test_results'][0][0][rate_down]['bkQOS'])
            throughput_df[1].append(res['test_results'][0][0][rate_down]['beQOS'])
            throughput_df[2].append(res['test_results'][0][0][rate_down]['videoQOS'])
            throughput_df[3].append(res['test_results'][0][0][rate_down]['voiceQOS'])               
            table_df.update({"No of Stations": []})
            table_df.update({"Throughput for Load {}".format(rate_down): []})
            graph_df.update({rate_down: [throughput_df]})
            
            table_df.update({"No of Stations": str(len(self.input_devices_list))})
            table_df["Throughput for Load {}".format(rate_down)].append(throughput)
            res_copy=copy.copy(res)
            res_copy.update({"throughput_table_df": table_df})
            res_copy.update({"graph_df": graph_df})
        return res_copy

    def generate_report(self,data, input_setup_info):
        load=''
        rate_down= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        rate_up= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')
        if self.direction == 'Upload':
            load=rate_up
        else:
            if self.direction =="Download":
                load=rate_down
        res = self.set_report_data(data)
        print("res",res)
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
        "SSID": self.ssid,
        "Traffic Duration in hours" : round(int(self.test_duration)/3600,2),
        "Security" : self.security,
        "Protocol" : (self.traffic_type.strip("lf_")).upper(),
        "Traffic Direction" : self.direction,
        "TOS" : self.tos,
        "Per TOS Load in Mbps" : load
        }

        report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
        report.set_table_title(
            f"Overall {self.direction} Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
        report.build_table_title()
        df_throughput = pd.DataFrame(res["throughput_table_df"])
        report.set_table_dataframe(df_throughput)
        report.build_table()
        for key in res["graph_df"]:
            report.set_obj_html(
                _obj_title=f"Overall {self.direction} throughput for {len(self.input_devices_list)} clients with different TOS.",
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
                                 _graph_image_name=f"tos_download_{key}Hz",
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
        if self.direction == 'Upload':
            load=rate_up
            data_set=res['test_results'][0][1]
        else:
            if self.direction =="Download":
                load=rate_down
                data_set=res['test_results'][0][0]
        tos_type = ['Background','Besteffort','Video','Voice']
        load_list = []
        traffic_type_list = []
        traffic_direction_list = []
        bk_tos_list = [] 
        be_tos_list = []
        vi_tos_list = [] 
        vo_tos_list = []
        traffic_type=(self.traffic_type.strip("lf_")).upper()
        for client in range(len(self.real_client_list)):
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
                print(res)
                print(load)   
                print(data_set)  
                if "BK" in self.tos:
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BK(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running BK "
                                f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows “"
                                f"Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['BK']], _xaxis_name="Throughput in Mbps",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in self.real_client_list],
                                            _yaxis_label=[i for i in self.real_client_list],
                                            _label=["BK"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title=f"Individual {self.direction} throughput for BK(WIFI) traffic",
                                            _title_size=16,
                                            _figsize= (18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['orange'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="bk_{}".format(load), _color_edge=['black'],
                                            _color=['orange'])
                    graph_png = graph.build_bar_graph_horizontal()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    bk_dataframe = {
                        " Client Name " : self.real_client_list,
                        " MAC " : self.mac_id_list,
                        " Type of traffic " : bk_tos_list,
                        " Traffic Direction " : traffic_direction_list,
                        " Traffic Protocol " : traffic_type_list,
                        " Intended Load (Mbps) " : load_list,
                        " Throughput (Mbps) " : data_set[load]['BK']
                    }

                    dataframe1 = pd.DataFrame(bk_dataframe)
                    report.set_table_dataframe(dataframe1)
                    report.build_table()
                logger.info("Graph and table for BK tos are built")
                if "BE" in self.tos:
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BE(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running BE "
                                f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                                f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['BE']], _yaxis_name="Client names",
                                            _xaxis_name="Throughput in Mbps",
                                            _yaxis_categories=[i for i in self.real_client_list],
                                            _yaxis_label=[i for i in self.real_client_list],
                                            _label=["BE"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title=f"Individual {self.direction} throughput for BE(WIFI) traffic",
                                            _title_size=16,
                                            _figsize=(18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['olivedrab'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="be_{}".format(load), _color_edge=['black'],
                                            _color=['olivedrab'])
                    graph_png = graph.build_bar_graph_horizontal()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    be_dataframe = {
                        " Client Name " : self.real_client_list,
                        " MAC " : self.mac_id_list,
                        " Type of traffic " : be_tos_list,
                        " Tra_xaxis_categories=[i for i in self.real_client_list],ffic Direction " : traffic_direction_list,
                        " Traffic Protocol " : traffic_type_list,
                        " Intended Load (Mbps) " : load_list,
                        " Throughput (Mbps) " : data_set[load]['BE']
                    }
                    
                    dataframe2 = pd.DataFrame(be_dataframe)
                    report.set_table_dataframe(dataframe2)
                    report.build_table()
                logger.info("Graph and table for BE tos are built")
                if "VI" in self.tos:
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VI(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running VI "
                                f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                                f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['VI']], _yaxis_name="Client names",
                                            _xaxis_name="Throughput in Mbps",
                                            _yaxis_categories=[i for i in self.real_client_list],
                                            _yaxis_label=[i for i in self.real_client_list],
                                            _label=["VI"],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title=f"Individual {self.direction} throughput for VI(WIFI) traffic",
                                            _title_size=16,
                                            _figsize=(18, 12),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
                                            _color_name=['steelblue'],
                                            _enable_csv=True,
                                            _graph_image_name="video_{}".format(load),
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
                    vi_dataframe = {
                        " Client Name " : self.real_client_list,
                        " MAC " : self.mac_id_list,
                        " Type of traffic " : vi_tos_list,
                        " Traffic Direction " : traffic_direction_list,
                        " Traffic Protocol " : traffic_type_list,
                        " Intended Load (Mbps) " : load_list,
                        " Throughput (Mbps) " : data_set[load]['VI']
                    }
                    
                    dataframe3 = pd.DataFrame(vi_dataframe)
                    report.set_table_dataframe(dataframe3)
                    report.build_table()
                logger.info("Graph and table for VI tos are built")
                if "VO" in self.tos:
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VO(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running VO "
                                f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                                f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=[data_set[load]['VO']], _yaxis_name="Client names",
                                            _xaxis_name="Throughput in Mbps",
                                            _yaxis_categories=[i for i in self.real_client_list],
                                            _yaxis_label=[i for i in self.real_client_list],
                                            _label=['VO'],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _graph_title=f"Individual {self.direction} throughput for VO(WIFI) traffic",
                                            _title_size=16,
                                            _figsize=(18, 12),
                                            _yticks_rotation=None,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
                                            _color_name=['blueviolet'],
                                            _enable_csv=True,
                                            _graph_image_name="voice_{}".format(load),
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
                    vo_dataframe = {
                        " Client Name " : self.real_client_list,
                        " MAC " : self.mac_id_list,
                        " Type of traffic " : vo_tos_list,
                        " Traffic Direction " : traffic_direction_list,
                        " Traffic Protocol " : traffic_type_list,
                        " Intended Load (Mbps) " : load_list,
                        " Throughput (Mbps) " : data_set[load]['VO']
                    }
                    
                    dataframe4 = pd.DataFrame(vo_dataframe)
                    report.set_table_dataframe(dataframe4)
                    report.build_table() 
                logger.info("Graph and table for VO tos are built")
        else:
            print("No individual graph to generate.")


def main():
    parser = argparse.ArgumentParser(
        prog='throughput_QOS.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Provides the available devices list and allows user to run the qos traffic
            with particular tos on particular devices in upload, download directions.
            ''',
        description='''\
        
        NAME: lf_interop_qos.py

        PURPOSE: lf_interop_qos.py will provide the available devices and allows user to run the qos traffic
        with particular tos on particular devices in upload, download directions.

        EXAMPLE-1:
        Command Line Interface to run download scenario with tos : Voice
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 0 
        --traffic_type lf_udp --tos "VO"

        EXAMPLE-2:
        Command Line Interface to run download scenario with tos : Voice and Video
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 0 
        --traffic_type lf_udp --tos "VO,VI"

        EXAMPLE-3:
        Command Line Interface to run upload scenario with tos : Background, Besteffort, Video and Voice
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco 
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 0 --upload 1000000
        --traffic_type lf_udp --tos "BK,BE,VI,VO"

        SCRIPT_CLASSIFICATION :  Test

        SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

        NOTES:
        1.Use './lf_interop_qos.py --help' to see command line usage and options
        2.Please pass tos in CAPITALS as shown :"BK,VI,BE,VO"
        3.Please enter the download or upload rate in bps
        4.After passing cli, a list will be displayed on terminal which contains available resources to run test.
        The following sentence will be displayed
        Enter the desired resources to run the test:
        Please enter the port numbers seperated by commas ','.
        Example: 
        Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date - 01/07/2023
        Build version - 5.4.6
        kernel version - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.

''')
    
    required = parser.add_argument_group('Required arguments to run lf_interop_qos.py')
    optional = parser.add_argument_group('Optional arguments to run lf_interop_qos.py')
    required.add_argument('--mgr',
                              '--lfmgr',
                              default='localhost',
                              help='hostname for where LANforge GUI is running')
    required.add_argument('--mgr_port',
                            '--port',
                            default=8080,
                            help='port LANforge GUI HTTP service is running on')
    required.add_argument('--upstream_port',
                          '-u',
                            default='eth1',
                            help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    required.add_argument('--security',
                            default="open",
                            help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >')
    required.add_argument('--ssid',
                            help='WiFi SSID for script objects to associate to')
    required.add_argument('--passwd',
                            '--password',
                            '--key',
                            default="[BLANK]",
                            help='WiFi passphrase/password/key')
    required.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=True)
    required.add_argument('--upload', help='--upload traffic load per connection (upload rate)')
    required.add_argument('--download', help='--download traffic load per connection (download rate)')
    required.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    required.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    required.add_argument('--tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    optional.add_argument('-d',
                              '--debug',
                              action="store_true",
                              help='Enable debugging')
    args = parser.parse_args()
    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    
    test_results ={'test_results':[]}

    loads = {}
    station_list = []
    data= {}

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
    if args.test_duration.endswith('s') or args.test_duration.endswith('S'):
        args.test_duration = int(args.test_duration[0:-1])
    elif args.test_duration.endswith('m') or args.test_duration.endswith('M'):
        args.test_duration = int(args.test_duration[0:-1]) * 60
    elif args.test_duration.endswith('h') or args.test_duration.endswith('H'):
        args.test_duration = int(args.test_duration[0:-1]) * 60 * 60
    elif args.test_duration.endswith(''):
        args.test_duration = int(args.test_duration)

    for index in range(len(loads["download"])):
        throughput_qos = ThroughputQOS(host=args.mgr,
                                        port=args.mgr_port,
                                        number_template="0000",
                                        ap_name=args.ap_name,
                                        name_prefix="TOS-",
                                        upstream=args.upstream_port,
                                        ssid=args.ssid,
                                        password=args.passwd,
                                        security=args.security,
                                        test_duration=args.test_duration,
                                        use_ht160=False,
                                        side_a_min_rate=int(loads['upload'][index]),
                                        side_b_min_rate=int(loads['download'][index]),
                                        traffic_type=args.traffic_type,
                                        tos=args.tos,
                                        _debug_on=args.debug)
        throughput_qos.pre_cleanup()
        throughput_qos.os_type()
        throughput_qos.phantom_check()
        throughput_qos.build()
        throughput_qos.start(False, False)
        time.sleep(10)
        connections_download,connections_upload= throughput_qos.monitor()
        print("connections download",connections_download)
        print("connections upload",connections_upload)
        throughput_qos.stop()
        time.sleep(5)
        test_results['test_results'].append(throughput_qos.evaluate_qos(connections_download,connections_upload))
        data.update(test_results)
    test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test ended at: ", test_end_time)
    
    input_setup_info = {
        "contact": "support@candelatech.com"
    }
    throughput_qos.generate_report(data=data, input_setup_info=input_setup_info)



if __name__ == "__main__":
    main()

