#!/usr/bin/env python3
# flake8: noqa

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

    EXAMPLE-4:
    Command Line Interface to run bi-directional scenario with tos : Video and Voice
    python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco
    --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 1000000
    --traffic_type lf_udp --tos "VI,VO"

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
    Working date - 26/07/2023
    Build version - 5.4.8
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
import json
import pandas as pd
import shutil
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

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


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
                 test_name=None,
                 device_list=[],
                 result_dir=None,
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
                 dowebgui=False,
                 ip="localhost",
                 user_list=[], real_client_list=[], real_client_list1=[], hw_list=[], laptop_list=[], android_list=[], mac_list=[], windows_list=[], linux_list=[],
                 total_resources_list=[], working_resources_list=[], hostname_list=[], username_list=[], eid_list=[],
                 devices_available=[], input_devices_list=[], mac_id1_list=[], mac_id_list=[]):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.ssid_list = []
        self.upstream = upstream
        self.host = host
        self.port = port
        self.test_name = test_name
        self.device_list = device_list
        self.result_dir = result_dir
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
        self.real_client_list1 = real_client_list1
        self.user_list = user_list
        self.mac_id_list = mac_id_list
        self.mac_id1_list = mac_id1_list
        self.dowebgui = dowebgui
        self.ip = ip
        self.device_found = False

    def os_type(self):
        response = self.json_get("/resource/all")
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for a, b in element.items():
                        if "Apple" in b['hw version']:
                            if b['kernel'] == '':
                                self.hw_list.append('iOS')
                            else:
                                self.hw_list.append(b['hw version'])
                        else:
                            self.hw_list.append(b['hw version'])
        for hw_version in self.hw_list:
            if "Win" in hw_version:
                self.windows_list.append(hw_version)
            elif "Linux" in hw_version:
                self.linux_list.append(hw_version)
            elif "Apple" in hw_version:
                self.mac_list.append(hw_version)
            elif "iOS" in hw_version:
                self.mac_list.append(hw_version)
            else:
                if hw_version != "":
                    self.android_list.append(hw_version)
        self.laptop_list = self.windows_list + self.linux_list + self.mac_list

    def phantom_check(self):
        port_eid_list, same_eid_list, original_port_list = [], [], []
        response = self.json_get("/resource/all")
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for a, b in element.items():
                        if b['phantom'] == False:
                            self.working_resources_list.append(b["hw version"])
                            if "Win" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.windows_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] + " " + 'Win' + " " + b['hostname'])
                            elif "Linux" in b['hw version']:
                                if ('ct' not in b['hostname']):
                                    if ('lf' not in b['hostname']):
                                        self.eid_list.append(b['eid'])
                                        self.linux_list.append(b['hw version'])
                                        self.devices_available.append(b['eid'] + " " + 'Lin' + " " + b['hostname'])
                            elif "Apple" in b['hw version']:
                                if b['kernel'] == '':
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    self.devices_available.append(b['eid'] + " " + 'iOS' + " " + b['hostname'])
                                else:
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    self.devices_available.append(b['eid'] + " " + 'Mac' + " " + b['hostname'])
                            else:
                                self.eid_list.append(b['eid'])
                                self.android_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] + " " + 'android' + " " + b['user'])

        # All the available resources are fetched from resource mgr tab ----

        response_port = self.json_get("/port/all")

        mac_id1_list = []
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if (not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0" and port_data['alias'] != 'p2p0'):
                    for id in self.eid_list:
                        if (id + '.' in port):
                            original_port_list.append(port)
                            port_eid_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]))
                            self.mac_id1_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]) + ' ' + port_data['mac'])

        for i in range(len(self.eid_list)):
            for j in range(len(port_eid_list)):
                if self.eid_list[i] == port_eid_list[j]:
                    same_eid_list.append(self.eid_list[i])
        same_eid_list = [_eid + ' ' for _eid in same_eid_list]

        # All the available ports from port manager are fetched from port manager tab ---

        for eid in same_eid_list:
            for device in self.devices_available:
                if eid in device:
                    print(eid + ' ' + device)
                    self.user_list.append(device)
        # checking for the availability of slected devices to run test
        if len(self.device_list) != 0:
            devices_list = self.device_list
            available_list = []
            not_available = []
            for input_device in devices_list.split(','):
                found = False
                for device in self.devices_available:
                    if input_device + " " in device:
                        available_list.append(input_device)
                        found = True
                        break
                if found == False:
                    not_available.append(input_device)
                    logger.warning(input_device + " is not available to run test")

            if len(available_list) > 0:

                logger.info("Test is initiated on devices: {}".format(available_list))
                devices_list = ','.join(available_list)
                self.device_found = True
            else:
                devices_list = ""
                self.device_found = False
                logger.warning("Test can not be initiated on any selected devices")
        else:
            logger.info("AVAILABLE DEVICES TO RUN TEST : {}".format(self.user_list))

            devices_list = input("Enter the desired resources to run the test:")
        resource_eid_list = devices_list.split(',')
        logger.info("devices list {}".format(devices_list, resource_eid_list))
        resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]
        resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
        logger.info("resource eid list {}".format(resource_eid_list1, original_port_list))

        # User desired eids are fetched ---

        for eid in resource_eid_list1:
            for ports_m in original_port_list:
                if eid in ports_m:
                    self.input_devices_list.append(ports_m)
        logger.info("INPUT DEVICES LIST {}".format(self.input_devices_list))

        # user desired real client list 1.1 wlan0 ---

        for i in resource_eid_list2:
            for j in range(len(self.user_list)):
                if i in self.user_list[j]:
                    self.real_client_list.append(self.user_list[j])
                    self.real_client_list1.append((self.user_list[j])[:25])
        logger.info("REAL CLIENT LIST{}".format(self.real_client_list))

        self.num_stations = len(self.real_client_list)

        for eid in resource_eid_list2:
            for i in self.mac_id1_list:
                if eid in i:
                    self.mac_id_list.append(i.strip(eid + ' '))
        logger.info("MAC ID LIST {}" .format(self.mac_id_list))
        return self.input_devices_list, self.real_client_list, self.mac_id_list
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
        # self.cx_profile.cleanup_prefix()
        self.cx_profile.cleanup()

    def cleanup(self):
        self.cx_profile.cleanup()

    def build(self):
        self.create_cx()
        print("cx build finished")

    def create_cx(self):
        direction = ''
        if (int(self.cx_profile.side_b_min_bps)) != 0 and (int(self.cx_profile.side_a_min_bps)) != 0:
            self.direction = "Bi-direction"
            direction = 'Bi-di'
        elif int(self.cx_profile.side_b_min_bps) != 0:
            self.direction = "Download"
            direction = 'DL'
        else:
            if int(self.cx_profile.side_a_min_bps) != 0:
                self.direction = "Upload"
                direction = 'UL'
        traffic_type = (self.traffic_type.strip("lf_")).upper()
        traffic_direction_list, cx_list, traffic_type_list = [], [], []
        for client in range(len(self.real_client_list)):
            traffic_direction_list.append(direction)
            traffic_type_list.append(traffic_type)
        logger.info("tos: {}".format(self.tos))

        for ip_tos in self.tos:
            for i in self.real_client_list1:
                for j in traffic_direction_list:
                    for k in traffic_type_list:
                        cxs = "%s_%s_%s_%s" % (i, k, j, ip_tos)
                        cx_names = cxs.replace(" ", "")
                cx_list.append(cx_names)
        logger.info('cx_list {}'.format(cx_list))
        count = 0
        for ip_tos in range(len(self.tos)):
            for device in range(len(self.input_devices_list)):
                logger.info("## ip_tos: {}".format(ip_tos))
                logger.info("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
                    self.traffic_type, self.tos[ip_tos], self.cx_profile.get_cx_count()))
                self.cx_profile.create(endp_type=self.traffic_type, side_a=[self.input_devices_list[device]],
                                       side_b=self.upstream,
                                       sleep_time=0, tos=self.tos[ip_tos], cx_name="%s-%i" % (cx_list[count], len(self.cx_profile.created_cx)))
                count += 1
            logger.info("cross connections with TOS type created.")

    def monitor(self):
        throughput, upload, download, upload_throughput, download_throughput, connections_upload, connections_download, avg_upload, avg_download, avg_upload_throughput, avg_download_throughput, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b, dropa_connections, dropb_connections = {
        }, [], [], [], [], {}, {}, [], [], [], [], {}, {}, [], [], {}, {}
        # Initialized seperate variables for average values for report changes
        drop_a, drop_a_per, drop_b, drop_b_per, avg_drop_b_per, avg_drop_a_per = [], [], [], [], [], []
        if (self.test_duration is None) or (int(self.test_duration) <= 1):
            raise ValueError("Monitor test duration should be > 1 second")
        if self.cx_profile.created_cx is None:
            raise ValueError("Monitor needs a list of Layer 3 connections")
        # monitor columns
        start_time = datetime.now()
        test_start_time = datetime.now().strftime("%Y %d %H:%M:%S")
        print("Test started at: ", test_start_time)
        print("Monitoring cx and endpoints")
        end_time = start_time + timedelta(seconds=int(self.test_duration))
        self.overall = []
        index = -1
        connections_upload = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_upload_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        # Initialize dictionaries for average values of connections (upload, download and drop)
        connections_upload_avg = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download_avg = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        dropa_connections = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        dropb_connections = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        [(upload.append([]), download.append([]), drop_a.append([]), drop_b.append([]), avg_upload.append([]), avg_download.append([]), avg_drop_a.append([]), avg_drop_b.append([])) for i in
         range(len(self.cx_profile.created_cx))]
        if self.dowebgui == "True":
            runtime_dir = self.result_dir
        # added a dictionary to store real time data
        self.real_time_data = {}
        for endp in connections_download_realtime.keys():
            self.real_time_data.update(
                {
                    endp: {
                        'BE': {
                            'time': [],
                            'bps rx a': [],
                            'bps rx b': [],
                            'rx drop % a': [],
                            'rx drop % b': []
                        },
                        'BK': {
                            'time': [],
                            'bps rx a': [],
                            'bps rx b': [],
                            'rx drop % a': [],
                            'rx drop % b': []
                        },
                        'VI': {
                            'time': [],
                            'bps rx a': [],
                            'bps rx b': [],
                            'rx drop % a': [],
                            'rx drop % b': []
                        },
                        'VO': {
                            'time': [],
                            'bps rx a': [],
                            'bps rx b': [],
                            'rx drop % a': [],
                            'rx drop % b': []
                        }
                    }
                }
            )
        # Added background_run to allow the test to continue running, bypassing the duration limit for nile requirement.
        while datetime.now() < end_time or getattr(self, "background_run", None):
            index += 1
            # removed the fields query from endp so that the cx names will be given in the reponse as keys instead of cx_ids
            t_response = {}
            overallresponse = self.json_get('/cx/all')

            try:
                response = self.json_get('/cx/%s?' % (
                    ','.join(self.cx_profile.created_cx.keys())))
                del response['handler'], response['uri']
                for item in response.items():
                    cx_name, cx_data = item
                    t_response[cx_name] = []
                    for key in cx_data.keys():
                        if key in ['bps rx a', 'bps rx b', 'rx drop % a', 'rx drop % b']:
                            t_response[cx_name].append(cx_data[key])
                        traffic_tos = cx_name.split('_')[-1].split('-')[0]
                        self.real_time_data[cx_name][traffic_tos]['time'].append(datetime.now().strftime('%H:%M:%S'))
                        self.real_time_data[cx_name][traffic_tos]['bps rx a'].append(cx_data['bps rx a'] / 1000000)
                        self.real_time_data[cx_name][traffic_tos]['bps rx b'].append(cx_data['bps rx b'] / 1000000)
                        self.real_time_data[cx_name][traffic_tos]['rx drop % a'].append(cx_data['rx drop % a'])
                        self.real_time_data[cx_name][traffic_tos]['rx drop % b'].append(cx_data['rx drop % b'])
            except Exception as e:
                logger.info(overallresponse)
                logger.error(f"None type response{e}")
            response = t_response
            response_values = list(response.values())
            for value_index in range(len(response.values())):
                throughput[value_index] = response_values[value_index]
            temp_upload = []
            temp_download = []
            temp_drop_a = []
            temp_drop_b = []
            for i in range(len(self.cx_profile.created_cx)):
                temp_upload.append([])
                temp_download.append([])
                temp_drop_a.append([])
                temp_drop_b.append([])
            for i in range(len(throughput)):
                temp_upload[i].append(throughput[i][1])
                temp_download[i].append(throughput[i][0])
                temp_drop_a[i].append(throughput[i][2])
                temp_drop_b[i].append(throughput[i][3])
            upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in temp_upload]
            download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in temp_download]
            drop_a_per = [float(round(sum(i) / len(i), 2)) for i in temp_drop_a]
            drop_b_per = [float(round(sum(i) / len(i), 2)) for i in temp_drop_b]
            keys = list(connections_upload_realtime.keys())
            keys = list(connections_download_realtime.keys())
            for i in range(len(download_throughput)):
                connections_download_realtime.update({keys[i]: float(f"{(download_throughput[i]):.2f}")})
            for i in range(len(upload_throughput)):
                connections_upload_realtime.update({keys[i]: float(f"{(upload_throughput[i]):.2f}")})
            real_time_qos = self.evaluate_qos(connections_download_realtime, connections_upload_realtime,
                                              drop_a_per, drop_b_per)
            time_difference = abs(end_time - datetime.now())
            total_hours = time_difference.total_seconds() / 3600
            remaining_minutes = (total_hours % 1) * 60
            for key1, key2 in zip(real_time_qos[0], real_time_qos[1]):
                if self.direction == "Bi-direction":
                    self.overall.append({
                        "BE_dl": real_time_qos[0][key1]["beQOS"],
                        "BE_ul": real_time_qos[1][key2]["beQOS"],
                        "BK_dl": real_time_qos[0][key1]["bkQOS"],
                        "BK_ul": real_time_qos[1][key2]["bkQOS"],
                        "VI_dl": real_time_qos[0][key1]["videoQOS"],
                        "VI_ul": real_time_qos[1][key2]["videoQOS"],
                        "VO_dl": real_time_qos[0][key1]["voiceQOS"],
                        "VO_ul": real_time_qos[1][key2]["voiceQOS"],
                        "timestamp": datetime.now().strftime("%d/%m %I:%M:%S %p"),
                        "start_time": start_time.strftime("%d/%m %I:%M:%S %p"),
                        "end_time": end_time.strftime("%d/%m %I:%M:%S %p"),
                        "remaining_time": [
                            str(int(total_hours)) + " hr and " + str(int(remaining_minutes)) + " min" if int(
                                total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][0],
                        'status': 'Running'
                    })
                elif self.direction == "Upload":
                    self.overall.append({
                        "BE_dl": 0,
                        "BE_ul": real_time_qos[1][key2]["beQOS"],
                        "BK_dl": 0,
                        "BK_ul": real_time_qos[1][key2]["bkQOS"],
                        "VI_dl": 0,
                        "VI_ul": real_time_qos[1][key2]["videoQOS"],
                        "VO_dl": 0,
                        "VO_ul": real_time_qos[1][key2]["voiceQOS"],
                        "timestamp": datetime.now().strftime("%d/%m %I:%M:%S %p"),
                        "start_time": start_time.strftime("%d/%m %I:%M:%S %p"),
                        "end_time": end_time.strftime("%d/%m %I:%M:%S %p"),
                        "remaining_time": [
                            str(int(total_hours)) + " hr and " + str(int(remaining_minutes)) + " min" if int(
                                total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][0],
                        'status': 'Running'
                    })
                else:
                    self.overall.append({
                        "BE_dl": real_time_qos[0][key1]["beQOS"],
                        "BE_ul": 0,
                        "BK_dl": real_time_qos[0][key1]["bkQOS"],
                        "BK_ul": 0,
                        "VI_dl": real_time_qos[0][key1]["videoQOS"],
                        "VI_ul": 0,
                        "VO_dl": real_time_qos[0][key1]["voiceQOS"],
                        "VO_ul": 0,
                        "timestamp": datetime.now().strftime("%d/%m %I:%M:%S %p"),
                        "start_time": start_time.strftime("%d/%m %I:%M:%S %p"),
                        "end_time": end_time.strftime("%d/%m %I:%M:%S %p"),
                        "remaining_time": [
                            str(int(total_hours)) + " hr and " + str(int(remaining_minutes)) + " min" if int(
                                total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][0],
                        'status': 'Running'
                    })
            if self.dowebgui == "True":
                df1 = pd.DataFrame(self.overall)
                df1.to_csv('{}/overall_throughput.csv'.format(runtime_dir), index=False)

                with open(runtime_dir + "/../../Running_instances/{}_{}_running.json".format(self.ip, self.test_name), 'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logger.warning('Test is stopped by the user')
                        break
                d = datetime.now()
                if d - start_time <= timedelta(hours=1):
                    time.sleep(5)
                elif d - start_time > timedelta(hours=1) or d - start_time <= timedelta(
                        hours=6):
                    if end_time - d < timedelta(seconds=10):
                        time.sleep(5)
                    else:
                        time.sleep(10)
                elif d - start_time > timedelta(hours=6) or d - start_time <= timedelta(
                        hours=12):
                    if end_time - d < timedelta(seconds=30):
                        time.sleep(5)
                    else:
                        time.sleep(30)
                elif d - start_time > timedelta(hours=12) or d - start_time <= timedelta(
                        hours=24):
                    if end_time - d < timedelta(seconds=60):
                        time.sleep(5)
                    else:
                        time.sleep(60)
                elif d - start_time > timedelta(hours=24) or d - start_time <= timedelta(
                        hours=48):
                    if end_time - d < timedelta(seconds=60):
                        time.sleep(5)
                    else:
                        time.sleep(90)
                elif d - start_time > timedelta(hours=48):
                    if end_time - d < timedelta(seconds=120):
                        time.sleep(5)
                    else:
                        time.sleep(120)
            else:
                time.sleep(1)
            # average upload download and drop is calculated
            for ind, k in enumerate(throughput):
                avg_upload[ind].append(throughput[ind][1])
                avg_download[ind].append(throughput[ind][0])
                avg_drop_a[ind].append(throughput[ind][2])
                avg_drop_b[ind].append(throughput[ind][3])
        # # rx_rate list is calculated
        for index, key in enumerate(throughput):
            upload[index].append(throughput[index][1])
            download[index].append(throughput[index][0])
            drop_a[index].append(throughput[index][2])
            drop_b[index].append(throughput[index][3])
        # Rounding of the results upto 2 decimals
        upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
        download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
        drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
        drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
        avg_upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in avg_upload]
        avg_download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in avg_download]
        avg_drop_a_per = [float(round(sum(i) / len(i), 2)) for i in avg_drop_a]
        avg_drop_b_per = [float(round(sum(i) / len(i), 2)) for i in avg_drop_b]
        keys = list(connections_upload.keys())
        keys = list(connections_download.keys())
        # Updated the calculated values to the respective connections in dictionary
        for i in range(len(download_throughput)):
            connections_download.update({keys[i]: download_throughput[i]})
        for i in range(len(upload_throughput)):
            connections_upload.update({keys[i]: upload_throughput[i]})
        for i in range(len(avg_download_throughput)):
            connections_download_avg.update({keys[i]: avg_download_throughput[i]})
        for i in range(len(avg_upload_throughput)):
            connections_upload_avg.update({keys[i]: avg_upload_throughput[i]})
        for i in range(len(avg_drop_a_per)):
            dropa_connections.update({keys[i]: avg_drop_a_per[i]})
        for i in range(len(avg_drop_b_per)):
            dropb_connections.update({keys[i]: avg_drop_b_per[i]})
        logger.info("connections download {}".format(connections_download))
        logger.info("connections {}".format(connections_upload))
        self.connections_download, self.connections_upload, self.drop_a_per, self.drop_b_per = connections_download, connections_upload, drop_a_per, drop_b_per
        return connections_download, connections_upload, drop_a_per, drop_b_per, connections_download_avg, connections_upload_avg, dropa_connections, dropb_connections

    def evaluate_qos(self, connections_download, connections_upload, drop_a_per, drop_b_per):
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
        tos_drop_dict = {'rx_drop_a': {'BK': [], 'BE': [], 'VI': [], 'VO': []},
                         'rx_drop_b': {'BK': [], 'BE': [], 'VI': [], 'VO': []}}
        if int(self.cx_profile.side_b_min_bps) != 0:
            case_download = str(int(self.cx_profile.side_b_min_bps) / 1000000)
        if int(self.cx_profile.side_a_min_bps) != 0:
            case_upload = str(int(self.cx_profile.side_a_min_bps) / 1000000)
        if len(self.cx_profile.created_cx.keys()) > 0:
            # added tos value in the fields query
            endp_data = self.json_get('endp/all?fields=name,tx+pkts+ll,rx+pkts+ll,delay,tos')
            endp_data.pop("handler")
            endp_data.pop("uri")
            if ('endpoint' not in endp_data.keys()):
                logging.warning('Malformed response for /endp/all?fields=name,tx+pkts+ll,rx+pkts+ll,delay,tos')
            else:
                endps = endp_data['endpoint']
                if int(self.cx_profile.side_b_min_bps) != 0:
                    for endp in endps:
                        if (list(endp.keys())[0].endswith('-A')):
                            rx_endps_download.update(endp)
                        elif (list(endp.keys())[0].endswith('-B')):
                            tx_endps_download.update(endp)
                    # for i in range(len(endps)):
                    #     if i < len(endps) // 2:
                    #         tx_endps_download.update(endps[i])
                    #     if i >= len(endps) // 2:
                    #         rx_endps_download.update(endps[i])
                    for sta in self.cx_profile.created_cx.keys():
                        temp = sta.rsplit('-', 1)
                        current_tos = temp[0].split('_')[-1]  # slicing TOS from CX name
                        temp = int(temp[1])
                        if int(self.cx_profile.side_b_min_bps) != 0:
                            tos_download[current_tos].append(connections_download[sta])
                            tos_drop_dict['rx_drop_a'][current_tos].append(drop_a_per[temp])
                            tx_b_download[current_tos].append(int(f"{tx_endps_download['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_download[current_tos].append(int(f"{rx_endps_download['%s-A' % sta]['rx pkts ll']}"))
                        else:
                            tos_download[current_tos].append(float(0))
                            tos_drop_dict['rx_drop_a'][current_tos].append(float(0))
                            tx_b_download[current_tos].append(int(0))
                            rx_a_download[current_tos].append(int(0))
                    tos_download.update({"bkQOS": float(f"{sum(tos_download['BK']):.2f}")})
                    tos_download.update({"beQOS": float(f"{sum(tos_download['BE']):.2f}")})
                    tos_download.update({"videoQOS": float(f"{sum(tos_download['VI']):.2f}")})
                    tos_download.update({"voiceQOS": float(f"{sum(tos_download['VO']):.2f}")})
                    tos_download.update({'tx_b': tx_b_download})
                    tos_download.update({'rx_a': rx_a_download})
                if int(self.cx_profile.side_a_min_bps) != 0:
                    for endp in endps:
                        if (list(endp.keys())[0].endswith('-A')):
                            rx_endps_upload.update(endp)
                        elif (list(endp.keys())[0].endswith('-B')):
                            tx_endps_upload.update(endp)
                    # for i in range(len(endps)):
                    #     if i < len(endps) // 2:
                    #         tx_endps_upload.update(endps[i])
                    #     if i >= len(endps) // 2:
                    #         rx_endps_upload.update(endps[i])
                    for sta in self.cx_profile.created_cx.keys():
                        temp = sta.rsplit('-', 1)
                        current_tos = temp[0].split('_')[-1]
                        temp = int(temp[1])
                        if int(self.cx_profile.side_a_min_bps) != 0:
                            tos_upload[current_tos].append(connections_upload[sta])
                            tos_drop_dict['rx_drop_b'][current_tos].append(drop_b_per[temp])
                            tx_b_upload[current_tos].append(int(f"{tx_endps_upload['%s-B' % sta]['tx pkts ll']}"))
                            rx_a_upload[current_tos].append(int(f"{rx_endps_upload['%s-A' % sta]['rx pkts ll']}"))
                        else:
                            tos_upload[current_tos].append(float(0))
                            tos_drop_dict['rx_drop_b'][current_tos].append(float(0))
                            tx_b_upload[current_tos].append(int(0))
                            rx_a_upload[current_tos].append(int(0))
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
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        res = {}
        if data is not None:
            res.update(data)
        else:
            print("No Data found to generate report!")
            exit(1)
        table_df = {}
        graph_df = {}
        download_throughput, upload_throughput = [], []
        upload_throughput_df, download_throughput_df = [[], [], [], []], [[], [], [], []]
        if int(self.cx_profile.side_a_min_bps) != 0:
            print(res['test_results'][0][1])
            upload_throughput.append(
                "BK : {}, BE : {}, VI: {}, VO: {}".format(res['test_results'][0][1][rate_up]["bkQOS"],
                                                          res['test_results'][0][1][rate_up]["beQOS"],
                                                          res['test_results'][0][1][rate_up][
                    "videoQOS"],
                    res['test_results'][0][1][rate_up][
                    "voiceQOS"]))
            upload_throughput_df[0].append(res['test_results'][0][1][rate_up]['bkQOS'])
            upload_throughput_df[1].append(res['test_results'][0][1][rate_up]['beQOS'])
            upload_throughput_df[2].append(res['test_results'][0][1][rate_up]['videoQOS'])
            upload_throughput_df[3].append(res['test_results'][0][1][rate_up]['voiceQOS'])
            table_df.update({"No of Stations": []})
            table_df.update({"Throughput for Load {}".format(rate_up + "-upload"): []})
            graph_df.update({rate_up: upload_throughput_df})

            table_df.update({"No of Stations": str(len(self.input_devices_list))})
            table_df["Throughput for Load {}".format(rate_up + "-upload")].append(upload_throughput[0])
            res_copy = copy.copy(res)
            res_copy.update({"throughput_table_df": table_df})
            res_copy.update({"graph_df": graph_df})
        if int(self.cx_profile.side_b_min_bps) != 0:
            print(res['test_results'][0][0])
            download_throughput.append(
                "BK : {}, BE : {}, VI: {}, VO: {}".format(res['test_results'][0][0][rate_down]["bkQOS"],
                                                          res['test_results'][0][0][rate_down]["beQOS"],
                                                          res['test_results'][0][0][rate_down][
                    "videoQOS"],
                    res['test_results'][0][0][rate_down][
                    "voiceQOS"]))
            download_throughput_df[0].append(res['test_results'][0][0][rate_down]['bkQOS'])
            download_throughput_df[1].append(res['test_results'][0][0][rate_down]['beQOS'])
            download_throughput_df[2].append(res['test_results'][0][0][rate_down]['videoQOS'])
            download_throughput_df[3].append(res['test_results'][0][0][rate_down]['voiceQOS'])
            table_df.update({"No of Stations": []})
            table_df.update({"Throughput for Load {}".format(rate_down + "-download"): []})
            graph_df.update({rate_down + "download": download_throughput_df})
            # print("...........graph_df",graph_df)
            table_df.update({"No of Stations": str(len(self.input_devices_list))})
            table_df["Throughput for Load {}".format(rate_down + "-download")].append(download_throughput[0])
            res_copy = copy.copy(res)
            res_copy.update({"throughput_table_df": table_df})
            res_copy.update({"graph_df": graph_df})
        return res_copy

    def generate_graph_data_set(self, data):
        data_set, overall_list = [], []
        overall_throughput = [[], [], [], []]
        load = ''
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        if self.direction == 'Upload':
            load = rate_up
        else:
            if self.direction == "Download":
                load = rate_down
        res = self.set_report_data(data)
        if self.direction == "Bi-direction":
            load = 'Upload' + ':' + rate_up + ',' + 'Download' + ':' + rate_down
            for key in res["graph_df"]:
                for j in range(len(res['graph_df'][key])):
                    overall_list.append(res['graph_df'][key][j])
            overall_throughput[0].append(round(sum(overall_list[0] + overall_list[4]), 2))
            overall_throughput[1].append(round(sum(overall_list[1] + overall_list[5]), 2))
            overall_throughput[2].append(round(sum(overall_list[2] + overall_list[6]), 2))
            overall_throughput[3].append(round(sum(overall_list[3] + overall_list[7]), 2))
            data_set = overall_throughput
        else:
            data_set = list(res["graph_df"].values())[0]
        return data_set, load, res

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

    def generate_report(self, data, input_setup_info, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b, report_path='', result_dir_name='Qos_Test_report',
                        selected_real_clients_names=None):
        # getting ssid list for devices, on which the test ran
        self.ssid_list = self.get_ssid_list(self.input_devices_list)

        if selected_real_clients_names is not None:
            self.num_stations = selected_real_clients_names
        data_set, load, res = self.generate_graph_data_set(data)
        report = lf_report(_output_pdf="interop_qos.pdf", _output_html="interop_qos.html", _path=report_path,
                           _results_dir_name=result_dir_name)
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))
        report.set_title("Interop QOS")
        report.build_banner()
        # objective title and description
        report.set_obj_html(_obj_title="Objective",
                            _obj="The objective of the QoS (Quality of Service) traffic throughput test is to measure the maximum"
                            " achievable throughput of a network under specific QoS settings and conditions.By conducting"
                            " this test, we aim to assess the capacity of network to handle high volumes of traffic while"
                            " maintaining acceptable performance levels,ensuring that the network meets the required QoS"
                            " standards and can adequately support the expected user demands.")
        report.build_objective()
        # Initialize counts and lists for device types
        android_devices, windows_devices, linux_devices, ios_devices, ios_mob_devices = 0, 0, 0, 0, 0
        all_devices_names = []
        device_type = []
        total_devices = ""
        for i in self.real_client_list:
            split_device_name = i.split(" ")
            if 'android' in split_device_name:
                all_devices_names.append(split_device_name[2] + ("(Android)"))
                device_type.append("Android")
                android_devices += 1
            elif 'Win' in split_device_name:
                all_devices_names.append(split_device_name[2] + ("(Windows)"))
                device_type.append("Windows")
                windows_devices += 1
            elif 'Lin' in split_device_name:
                all_devices_names.append(split_device_name[2] + ("(Linux)"))
                device_type.append("Linux")
                linux_devices += 1
            elif 'Mac' in split_device_name:
                all_devices_names.append(split_device_name[2] + ("(Mac)"))
                device_type.append("Mac")
                ios_devices += 1
            elif 'iOS' in split_device_name:
                all_devices_names.append(split_device_name[2] + ("(iOS)"))
                device_type.append("iOS")
                ios_mob_devices += 1

        # Build total_devices string based on counts
        if android_devices > 0:
            total_devices += f" Android({android_devices})"
        if windows_devices > 0:
            total_devices += f" Windows({windows_devices})"
        if linux_devices > 0:
            total_devices += f" Linux({linux_devices})"
        if ios_devices > 0:
            total_devices += f" Mac({ios_devices})"
        if ios_mob_devices > 0:
            total_devices += f" iOS({ios_mob_devices})"

        test_setup_info = {
            "Device List": ", ".join(all_devices_names),
            "Number of Stations": "Total" + f"({self.num_stations})" + total_devices,
            "AP Model": self.ap_name,
            "SSID": self.ssid,
            "Traffic Duration in hours": round(int(self.test_duration) / 3600, 2),
            "Security": self.security,
            "Protocol": (self.traffic_type.strip("lf_")).upper(),
            "Traffic Direction": self.direction,
            "TOS": self.tos,
            "Per TOS Load in Mbps": load
        }
        print(res["throughput_table_df"])

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
                     f"intended loads{load} per tos")
        report.build_objective()
        graph = lf_bar_graph(_data_set=data_set,
                             _xaxis_name="Load per Type of Service",
                             _yaxis_name="Throughput (Mbps)",
                             _xaxis_categories=["BK,BE,VI,VO"],
                             _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                             _graph_image_name=f"tos_download_{key}Hz",
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
        self.generate_individual_graph(res, report, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b)
        report.test_setup_table(test_setup_data=input_setup_info, value="Information")
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()

    def generate_individual_graph(self, res, report, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b):
        load = ""
        upload_list, download_list, individual_upload_list, individual_download_list = [], [], [], []
        individual_set, colors, labels = [], [], []
        individual_drop_a_list, individual_drop_b_list = [], []
        list = [[], [], [], []]
        data_set = {}
        # Initialized dictionaries to store average upload ,download and drop values with respect to tos
        avg_res = {'Upload': {
            'VO': [],
            'VI': [],
            'BE': [],
            'BK': []
        },
            'Download': {
            'VO': [],
                'VI': [],
                'BE': [],
                'BK': []
        }
        }
        drop_res = {'drop_a': {
            'VO': [],
            'VI': [],
            'BE': [],
            'BK': []
        },
            'drop_b': {
            'VO': [],
                'VI': [],
                'BE': [],
                'BK': []
        }
        }
        rate_down = str(str(int(self.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
        rate_up = str(str(int(self.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
        # Updated the dictionaries with the respective average upload download and drop values for a particular tos
        # EXAMPLE DATA FOR UPLOAD:
        # {'1.10androidSamsung_M21_UDP_UL_VI-0': 1.0, '1.10androidSamsung_M21_UDP_UL_VO-1': 0.96,'1.10androidSamsung_M21_UDP_UL_BE- 2': 0.78,'1.10androidSamsung_M21_UDP_UL_BK-3': 1.0}
        if self.direction == 'Upload':
            load = rate_up
            data_set = res['test_results'][0][1]
            for client in range(len(self.real_client_list)):
                individual_download_list.append('0.0')
                individual_drop_a_list.append('0.0')
            for key, val in connections_upload_avg.items():
                tos = key.split('_')[-1].split('-')[0]
                avg_res[self.direction][tos].append(val)
            for key, val in avg_drop_b.items():
                tos = key.split('_')[-1].split('-')[0]
                drop_res['drop_b'][tos].append(val)
        else:
            if self.direction == 'Download':
                load = rate_down
                data_set = res['test_results'][0][0]
                for client in range(len(self.real_client_list)):
                    individual_upload_list.append('0.0')
                    individual_drop_b_list.append('0.0')
                for key, val in connections_download_avg.items():
                    tos = key.split('_')[-1].split('-')[0]
                    avg_res[self.direction][tos].append(val)
                for key, val in avg_drop_a.items():
                    tos = key.split('_')[-1].split('-')[0]
                    drop_res['drop_a'][tos].append(val)
        tos_type = ['Background', 'Besteffort', 'Video', 'Voice']
        load_list = []
        traffic_type_list = []
        traffic_direction_list = []
        bk_tos_list = []
        be_tos_list = []
        vi_tos_list = []
        vo_tos_list = []
        traffic_type = (self.traffic_type.strip("lf_")).upper()
        for client in range(len(self.real_client_list)):
            upload_list.append(rate_up)
            download_list.append(rate_down)
            traffic_type_list.append(traffic_type.upper())
            bk_tos_list.append(tos_type[0])
            be_tos_list.append(tos_type[1])
            vi_tos_list.append(tos_type[2])
            vo_tos_list.append(tos_type[3])
            load_list.append(load)
            traffic_direction_list.append(self.direction)
        # print(traffic_type_list,traffic_direction_list,bk_tos_list,be_tos_list,vi_tos_list,vo_tos_list)
        if self.direction == "Bi-direction":
            load = 'Upload' + ':' + rate_up + ',' + 'Download' + ':' + rate_down
            for key in res['test_results'][0][0]:
                list[0].append(res['test_results'][0][0][key]['VI'])
                list[1].append(res['test_results'][0][0][key]['VO'])
                list[2].append(res['test_results'][0][0][key]['BK'])
                list[3].append(res['test_results'][0][0][key]['BE'])
            for key in res['test_results'][0][1]:
                list[0].append(res['test_results'][0][1][key]['VI'])
                list[1].append(res['test_results'][0][1][key]['VO'])
                list[2].append(res['test_results'][0][1][key]['BK'])
                list[3].append(res['test_results'][0][1][key]['BE'])
            for key, val in connections_upload_avg.items():
                tos = key.split('_')[-1].split('-')[0]
                avg_res['Upload'][tos].append(val)
            for key, val in connections_download_avg.items():
                tos = key.split('_')[-1].split('-')[0]
                avg_res['Download'][tos].append(val)
            for key, val in avg_drop_b.items():
                tos = key.split('_')[-1].split('-')[0]
                drop_res['drop_b'][tos].append(val)
            for key, val in avg_drop_a.items():
                tos = key.split('_')[-1].split('-')[0]
                drop_res['drop_a'][tos].append(val)
        x_fig_size = 15
        y_fig_size = len(self.real_client_list1) * .5 + 4
        if len(res.keys()) > 0:
            if "throughput_table_df" in res:
                res.pop("throughput_table_df")
            if "graph_df" in res:
                res.pop("graph_df")
                logger.info(res)
                logger.info(load)
                logger.info(data_set)
                if "BK" in self.tos:
                    if self.direction == "Bi-direction":
                        individual_set = list[2]
                        individual_download_list = avg_res['Download']['BK']
                        individual_upload_list = avg_res['Upload']['BK']
                        individual_drop_a_list = drop_res['drop_a']['BK']
                        individual_drop_b_list = drop_res['drop_b']['BK']
                        colors = ['orange', 'wheat']
                        labels = ["Download", "Upload"]
                    else:
                        individual_set = [data_set[load]['BK']]
                        colors = ['orange']
                        labels = ['BK']
                        if self.direction == "Upload":
                            individual_upload_list = avg_res['Upload']['BK']
                            individual_drop_b_list = drop_res['drop_b']['BK']
                        elif self.direction == "Download":
                            individual_download_list = avg_res['Download']['BK']
                            individual_drop_a_list = drop_res['drop_a']['BK']
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BK(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running BK "
                        f"(WiFi) traffic.  X- axis shows “Throughput in Mbps” and Y-axis shows “number of clients”.")
                    report.build_objective()
                    # print(upload_list, download_list, individual_download_list, individual_upload_list)
                    graph = lf_bar_graph_horizontal(_data_set=individual_set, _xaxis_name="Throughput in Mbps",
                                                    _yaxis_name="Client names",
                                                    _yaxis_categories=[i for i in self.real_client_list1],
                                                    _yaxis_label=[i for i in self.real_client_list1],
                                                    _label=labels,
                                                    _yaxis_step=1,
                                                    _yticks_font=8,
                                                    _yticks_rotation=None,
                                                    _graph_title=f"Individual {self.direction} throughput for BK(WIFI) traffic",
                                                    _title_size=16,
                                                    _figsize=(x_fig_size, y_fig_size),
                                                    _legend_loc="best",
                                                    _legend_box=(1.0, 1.0),
                                                    _color_name=colors,
                                                    _show_bar_value=True,
                                                    _enable_csv=True,
                                                    _graph_image_name="bk_{}".format(self.direction), _color_edge=['black'],
                                                    _color=colors)
                    graph_png = graph.build_bar_graph_horizontal()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    individual_avgupload_list = []
                    individual_avgdownload_list = []
                    for i in range(len(individual_upload_list)):
                        individual_avgupload_list.append(str(str(individual_upload_list[i]) + ' ' + 'Mbps'))
                    for j in range(len(individual_download_list)):
                        individual_avgdownload_list.append(str(str(individual_download_list[j]) + ' ' + 'Mbps'))
                    bk_dataframe = {
                        " Client Name ": self.real_client_list,
                        " MAC ": self.mac_id_list,
                        " SSID ": self.ssid_list,
                        " Type of traffic ": bk_tos_list,
                        # " Traffic Direction " : traffic_direction_list,
                        # " Traffic Protocol " : traffic_type_list,
                        " Offered upload rate ": upload_list,
                        " Offered download rate ": download_list,
                        " Observed average upload rate ": individual_avgupload_list,
                        " Observed average download rate": individual_avgdownload_list
                    }
                    if self.direction == "Bi-direction":
                        bk_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                        bk_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    else:
                        if self.direction == "Upload":
                            bk_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            bk_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        elif self.direction == "Download":
                            bk_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            bk_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    dataframe1 = pd.DataFrame(bk_dataframe)
                    report.set_table_dataframe(dataframe1)
                    report.build_table()
                logger.info("Graph and table for BK tos are built")
                if "BE" in self.tos:
                    if self.direction == "Bi-direction":
                        individual_set = list[3]
                        individual_download_list = avg_res['Download']['BE']
                        individual_upload_list = avg_res['Upload']['BE']
                        individual_drop_a_list = drop_res['drop_a']['BE']
                        individual_drop_b_list = drop_res['drop_b']['BE']
                        colors = ['lightcoral', 'mistyrose']
                        labels = ['Download', 'Upload']
                    else:
                        individual_set = [data_set[load]['BE']]
                        colors = ['violet']
                        labels = ['BE']
                        if self.direction == "Upload":
                            individual_upload_list = avg_res['Upload']['BE']
                            individual_drop_b_list = drop_res['drop_b']['BE']
                        elif self.direction == "Download":
                            individual_download_list = avg_res['Download']['BE']
                            individual_drop_a_list = drop_res['drop_a']['BE']
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic BE(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running BE "
                        f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                        f"“Throughput in Mbps”.")
                    # print("individual set",individual_set)
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=individual_set, _yaxis_name="Client names",
                                                    _xaxis_name="Throughput in Mbps",
                                                    _yaxis_categories=[i for i in self.real_client_list1],
                                                    _yaxis_label=[i for i in self.real_client_list1],
                                                    _label=labels,
                                                    _yaxis_step=1,
                                                    _yticks_font=8,
                                                    _yticks_rotation=None,
                                                    _graph_title=f"Individual {self.direction} throughput for BE(WIFI) traffic",
                                                    _title_size=16,
                                                    _figsize=(x_fig_size, y_fig_size),
                                                    _legend_loc="best",
                                                    _legend_box=(1.0, 1.0),
                                                    _color_name=colors,
                                                    _show_bar_value=True,
                                                    _enable_csv=True,
                                                    _graph_image_name="be_{}".format(self.direction), _color_edge=['black'],
                                                    _color=colors)
                    graph_png = graph.build_bar_graph_horizontal()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    individual_avgupload_list = []
                    individual_avgdownload_list = []
                    for i in range(len(individual_upload_list)):
                        individual_avgupload_list.append(str(str(individual_upload_list[i]) + ' ' + 'Mbps'))
                    for j in range(len(individual_download_list)):
                        individual_avgdownload_list.append(str(str(individual_download_list[j]) + ' ' + 'Mbps'))
                    be_dataframe = {
                        " Client Name ": self.real_client_list,
                        " MAC ": self.mac_id_list,
                        " SSID ": self.ssid_list,
                        " Type of traffic ": be_tos_list,
                        # " Traffic Direction " : traffic_direction_list,
                        # " Traffic Protocol " : traffic_type_list,
                        " Offered upload rate ": upload_list,
                        " Offered download rate ": download_list,
                        " Observed average upload rate ": individual_avgupload_list,
                        " Observed average download rate": individual_avgdownload_list
                    }
                    if self.direction == "Bi-direction":
                        be_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                        be_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    else:
                        if self.direction == "Upload":
                            be_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            be_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        elif self.direction == "Download":
                            be_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            be_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    dataframe2 = pd.DataFrame(be_dataframe)
                    report.set_table_dataframe(dataframe2)
                    report.build_table()
                logger.info("Graph and table for BE tos are built")
                if "VI" in self.tos:
                    if self.direction == "Bi-direction":
                        individual_set = list[0]
                        individual_download_list = avg_res['Download']['VI']
                        individual_upload_list = avg_res['Upload']['VI']
                        individual_drop_a_list = drop_res['drop_a']['VI']
                        individual_drop_b_list = drop_res['drop_b']['VI']
                        colors = ['steelblue', 'lightskyblue']
                        labels = ['Download', 'Upload']
                    else:
                        individual_set = [data_set[load]['VI']]
                        colors = ['steelblue']
                        labels = ['VI']
                        if self.direction == "Upload":
                            individual_upload_list = avg_res['Upload']['VI']
                            individual_drop_b_list = drop_res['drop_b']['VI']
                        elif self.direction == "Download":
                            individual_download_list = avg_res['Download']['VI']
                            individual_drop_a_list = drop_res['drop_a']['VI']
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VI(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running VI "
                        f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                        f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=individual_set, _yaxis_name="Client names",
                                                    _xaxis_name="Throughput in Mbps",
                                                    _yaxis_categories=[i for i in self.real_client_list1],
                                                    _yaxis_label=[i for i in self.real_client_list1],
                                                    _label=labels,
                                                    _yaxis_step=1,
                                                    _yticks_font=8,
                                                    _yticks_rotation=None,
                                                    _graph_title=f"Individual {self.direction} throughput for VI(WIFI) traffic",
                                                    _title_size=16,
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
                    individual_avgupload_list = []
                    individual_avgdownload_list = []
                    for i in range(len(individual_upload_list)):
                        individual_avgupload_list.append(str(str(individual_upload_list[i]) + ' ' + 'Mbps'))
                    for j in range(len(individual_download_list)):
                        individual_avgdownload_list.append(str(str(individual_download_list[j]) + ' ' + 'Mbps'))
                    vi_dataframe = {
                        " Client Name ": self.real_client_list,
                        " MAC ": self.mac_id_list,
                        " SSID ": self.ssid_list,
                        " Type of traffic ": vi_tos_list,
                        # " Traffic Direction " : traffic_direction_list,
                        # " Traffic Protocol " : traffic_type_list,
                        " Offered upload rate ": upload_list,
                        " Offered download rate ": download_list,
                        " Observed average upload rate ": individual_avgupload_list,
                        " Observed average download rate": individual_avgdownload_list
                    }
                    if self.direction == "Bi-direction":
                        vi_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                        vi_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    else:
                        if self.direction == "Upload":
                            vi_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            vi_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        elif self.direction == "Download":
                            vi_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            vi_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    print("Df", vi_dataframe)
                    dataframe3 = pd.DataFrame(vi_dataframe)
                    report.set_table_dataframe(dataframe3)
                    report.build_table()
                logger.info("Graph and table for VI tos are built")
                if "VO" in self.tos:
                    if self.direction == "Bi-direction":
                        individual_set = list[1]
                        individual_download_list = avg_res['Download']['VO']
                        individual_upload_list = avg_res['Upload']['VO']
                        individual_drop_a_list = drop_res['drop_a']['VO']
                        individual_drop_b_list = drop_res['drop_b']['VO']
                        colors = ['grey', 'lightgrey']
                        labels = ['Download', 'Upload']
                    else:
                        individual_set = [data_set[load]['VO']]
                        colors = ['grey']
                        labels = ['VO']
                        if self.direction == "Upload":
                            individual_upload_list = avg_res['Upload']['VO']
                            individual_drop_b_list = drop_res['drop_b']['VO']
                        elif self.direction == "Download":
                            individual_download_list = avg_res['Download']['VO']
                            individual_drop_a_list = drop_res['drop_a']['VO']
                    report.set_obj_html(
                        _obj_title=f"Individual {self.direction} throughput with intended load {load}/station for traffic VO(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.input_devices_list)} clients running VO "
                        f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                        f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph_horizontal(_data_set=individual_set, _yaxis_name="Client names",
                                                    _xaxis_name="Throughput in Mbps",
                                                    _yaxis_categories=[i for i in self.real_client_list1],
                                                    _yaxis_label=[i for i in self.real_client_list1],
                                                    _label=labels,
                                                    _yaxis_step=1,
                                                    _yticks_font=8,
                                                    _graph_title=f"Individual {self.direction} throughput for VO(WIFI) traffic",
                                                    _title_size=16,
                                                    _figsize=(x_fig_size, y_fig_size),
                                                    _yticks_rotation=None,
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
                    individual_avgupload_list = []
                    individual_avgdownload_list = []
                    for i in range(len(individual_upload_list)):
                        individual_avgupload_list.append(str(str(individual_upload_list[i]) + ' ' + 'Mbps'))
                    for j in range(len(individual_download_list)):
                        individual_avgdownload_list.append(str(str(individual_download_list[j]) + ' ' + 'Mbps'))
                    vo_dataframe = {
                        " Client Name ": self.real_client_list,
                        " MAC ": self.mac_id_list,
                        " SSID ": self.ssid_list,
                        " Type of traffic ": vo_tos_list,
                        # " Traffic Direction " : traffic_direction_list,
                        # " Traffic Protocol " : traffic_type_list,
                        " Offered upload rate ": upload_list,
                        " Offered download rate ": download_list,
                        " Observed average upload rate ": individual_avgupload_list,
                        " Observed average download rate": individual_avgdownload_list
                    }
                    if self.direction == "Bi-direction":
                        vo_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                        vo_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    else:
                        if self.direction == "Upload":
                            vo_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            vo_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                        elif self.direction == "Download":
                            vo_dataframe[" Observed Upload Drop (%)"] = individual_drop_b_list
                            vo_dataframe[" Observed Download Drop (%)"] = individual_drop_a_list
                    print("Df", vo_dataframe)
                    dataframe4 = pd.DataFrame(vo_dataframe)
                    report.set_table_dataframe(dataframe4)
                    report.build_table()
                logger.info("Graph and table for VO tos are built")
        else:
            print("No individual graph to generate.")
        # storing overall throughput CSV in the report directory
        logger.info('Storing real time values in a CSV')
        df1 = pd.DataFrame(self.overall)
        df1.to_csv('{}/overall_throughput.csv'.format(report.path_date_time))
        # storing real time data for CXs in seperate CSVs
        for cx in self.real_time_data:
            for tos in self.real_time_data[cx]:
                if tos in self.tos and len(self.real_time_data[cx][tos]['time']) != 0:
                    cx_df = pd.DataFrame(self.real_time_data[cx][tos])
                    cx_df.to_csv('{}/{}_{}_realtime_data.csv'.format(report.path_date_time, cx, tos), index=False)

    def copy_reports_to_home_dir(self):
        curr_path = self.result_dir
        home_dir = os.path.expanduser("~")
        out_folder_name = "WebGui_Reports"
        new_path = os.path.join(home_dir, out_folder_name)
        # webgui directory creation
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        test_name = self.test_name
        test_name_dir = os.path.join(new_path, test_name)
        # in webgui-reports DIR creating a directory with test name
        if not os.path.exists(test_name_dir):
            os.makedirs(test_name_dir)
        shutil.copytree(curr_path, test_name_dir, dirs_exist_ok=True)


def main():
    help_summary = '''\
    The Interop QoS test is designed to measure performance of an Access Point
    while running traffic with different types of services like voice, video, best effort, background.
    The test allows the user to run layer3 traffic for different ToS in upload, download and bi-direction scenarios between AP and real devices.
    Throughputs for all the ToS are reported for individual devices along with the overall throughput for each ToS.
    The expected behavior is for the AP to be able to prioritize the ToS in an order of voice,video,best effort and background.

    The test will create stations, create CX traffic between upstream port and stations, run traffic and generate a report.
    '''
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

        EXAMPLE-4:
        Command Line Interface to run bi-directional scenario with tos : Video and Voice
        python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.209.223 --mgr_port 8080 --ssid Cisco
        --passwd cisco@123 --security wpa2 --upstream eth1 --test_duration 1m --download 1000000 --upload 1000000
        --traffic_type lf_udp --tos "VI,VO"

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
        Working date - 26/07/2023
        Build version - 5.4.8
        kernel version - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.

''')

    required = parser.add_argument_group('Required arguments to run lf_interop_qos.py')
    optional = parser.add_argument_group('Optional arguments to run lf_interop_qos.py')
    optional.add_argument('--device_list',
                          help='Enter the devices on which the test should be run', default=[])
    optional.add_argument('--test_name',
                          help='Specify test name to store the runtime csv results', default=None)
    optional.add_argument('--result_dir',
                          help='Specify the result dir to store the runtime logs', default='')
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
    required.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    required.add_argument('--upload', help='--upload traffic load per connection (upload rate)')
    required.add_argument('--download', help='--download traffic load per connection (download rate)')
    required.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    required.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    required.add_argument('--tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    required.add_argument('--dowebgui', help="If true will execute script for webgui", default=False)
    optional.add_argument('-d',
                          '--debug',
                          action="store_true",
                          help='Enable debugging')
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)
    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    test_results = {'test_results': []}

    loads = {}
    station_list = []
    data = {}

    if args.download and args.upload:
        loads = {'upload': str(args.upload).split(","), 'download': str(args.download).split(",")}
        loads_data = loads["download"]
    elif args.download:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for i in range(len(args.download)):
            loads['upload'].append(0)
        loads_data = loads["download"]
    else:
        if args.upload:
            loads = {'upload': str(args.upload).split(","), 'download': []}
            for i in range(len(args.upload)):
                loads['download'].append(0)
            loads_data = loads["upload"]
    print(loads)
    if args.test_duration.endswith('s') or args.test_duration.endswith('S'):
        args.test_duration = int(args.test_duration[0:-1])
    elif args.test_duration.endswith('m') or args.test_duration.endswith('M'):
        args.test_duration = int(args.test_duration[0:-1]) * 60
    elif args.test_duration.endswith('h') or args.test_duration.endswith('H'):
        args.test_duration = int(args.test_duration[0:-1]) * 60 * 60
    elif args.test_duration.endswith(''):
        args.test_duration = int(args.test_duration)

    for index in range(len(loads_data)):
        throughput_qos = ThroughputQOS(host=args.mgr,
                                       ip=args.mgr,
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
                                       dowebgui=args.dowebgui,
                                       test_name=args.test_name,
                                       result_dir=args.result_dir,
                                       device_list=args.device_list,
                                       _debug_on=args.debug)
        throughput_qos.os_type()
        throughput_qos.phantom_check()
        # checking if we have atleast one device available for running test
        if throughput_qos.dowebgui == "True":
            if throughput_qos.device_found == False:
                logger.warning("No Device is available to run the test hence aborting the test")
                df1 = pd.DataFrame([{
                    "BE_dl": 0,
                    "BE_ul": 0,
                    "BK_dl": 0,
                    "BK_ul": 0,
                    "VI_dl": 0,
                    "VI_ul": 0,
                    "VO_dl": 0,
                    "VO_ul": 0,
                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                    'status': 'Stopped'
                }]
                )
                df1.to_csv('{}/overall_throughput.csv'.format(throughput_qos.result_dir), index=False)
                raise ValueError("Aborting the test....")
        throughput_qos.build()
        throughput_qos.start(False, False)
        time.sleep(10)
        connections_download, connections_upload, drop_a_per, drop_b_per, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b = throughput_qos.monitor()
        logger.info("connections download {}".format(connections_download))
        logger.info("connections upload {}".format(connections_upload))
        throughput_qos.stop()
        time.sleep(5)
        test_results['test_results'].append(throughput_qos.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
        data.update(test_results)
    test_end_time = datetime.now().strftime("%Y %d %H:%M:%S")
    print("Test ended at: ", test_end_time)

    input_setup_info = {
        "contact": "support@candelatech.com"
    }
    throughput_qos.cleanup()
    throughput_qos.generate_report(
        data=data,
        input_setup_info=input_setup_info,
        report_path=throughput_qos.result_dir,
        connections_upload_avg=connections_upload_avg,
        connections_download_avg=connections_download_avg,
        avg_drop_a=avg_drop_a,
        avg_drop_b=avg_drop_b)
   # updating webgui running json with latest entry and test status completed
    if throughput_qos.dowebgui == "True":
        last_entry = throughput_qos.overall[len(throughput_qos.overall) - 1]
        last_entry["status"] = "Stopped"
        last_entry["timestamp"] = datetime.now().strftime("%d/%m %I:%M:%S %p")
        last_entry["remaining_time"] = "0"
        last_entry["end_time"] = last_entry["timestamp"]
        throughput_qos.overall.append(
            last_entry
        )
        df1 = pd.DataFrame(throughput_qos.overall)
        df1.to_csv('{}/overall_throughput.csv'.format(args.result_dir, ), index=False)

        # copying to home directory i.e home/user_name
        throughput_qos.copy_reports_to_home_dir()


if __name__ == "__main__":
    main()
