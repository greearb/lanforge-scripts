#!/usr/bin/env python3
"""
    NAME: lf_interop_throughput.py

    PURPOSE: lf_interop_throughput.py will provide the available devices and allows user to run the wifi capacity test
    on particular devices by specifying direction as upload, download and bidirectional including different types of loads and incremental capacity.
    Will also run the interopability test on particular devices by specifying direction as upload, download and bidirectional.

    TO PERFORM THROUGHPUT TEST:

        EXAMPLE-1:
        Command Line Interface to run download scenario with desired resources
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --device_list 1.10,1.12

        EXAMPLE-2:
        Command Line Interface to run download scenario with incremental capacity
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000
        --traffic_type lf_udp --incremental_capacity 1,2

        EXAMPLE-3:
        Command Line Interface to run upload scenario with packet size
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 0 --upload 1000000 --traffic_type lf_udp --packet_size 17  # noqa: E501

        EXAMPLE-4:
        Command Line Interface to run bi-directional scenario with load_type intended load
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
        --traffic_type lf_udp --load_type wc_intended_load

        EXAMPLE-5:
        Command Line Interface to run bi-directional scenario with report_timer
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
        --traffic_type lf_udp --report_timer 5s

        EXAMPLE-6:
        Command Line Interface to run bi-directional scenario in Interop web-GUI
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
        --traffic_type lf_udp --report_timer 5s --dowebgui

        EXAMPLE-7:
        Command Line Interface to run the test with precleanup
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --precleanup

        EXAMPLE-8:
        Command Line Interface to run the test with postcleanup
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --postcleanup

        EXAMPLE-9:
        Command Line Interface to run the test with incremental_capacity by raising incremental flag
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --incremental

        EXAMPLE-10:
        Command Line Interface to run the test with expected pass/fail value
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp
        --device_list 1.11,1.12,1.360,1.400 --expected_passfail_value 5

        EXAMPLE-11:
        Command Line Interface to run the test with expected pass/fail csv for individual device
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp
        --device_list 1.11,1.12,1.360,1.400 --device_csv_name clab.csv

        EXAMPLE-12:
        Command Line Interface to run download scenario for Real clients with Groups and Profiles
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 100000000 --upload 100000000
        --traffic_type lf_udp --report_timer 1s --device_csv clab.csv --file_name gr204 --group_name g3,g4 --profile_name n1,n1

        EXAMPLE-13:
        Command Line Interface to run download scenario for Real clients with device list and config
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000
        --traffic_type lf_udp --ssid NETGEAR_2G_wpa2 --passwd Password@123 --security wpa2 --config --device_list 1.10,1.11,1.12

    TO PERFORM INTEROPABILITY TEST:

        EXAMPLE-1:
        Command Line Interface to run download scenario with desired resources
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --device_list 1.10,1.12  # noqa: E501

        EXAMPLE-2:
        Command Line Interface to run bi-directional scenario in Interop web-GUI
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
        --traffic_type lf_udp --do_interopability --dowebgui

        EXAMPLE-3:
        Command Line Interface to run the test with precleanup
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --precleanup

        EXAMPLE-4:
        Command Line Interface to run the test with postcleanup
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --postcleanup

        EXAMPLE-5:
        Command Line Interface to run the test with expected pass/fail value
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp
        --device_list 1.11,1.12,1.360,1.400 --expected_passfail_value 5 --do_interopability

        EXAMPLE-6:
        Command Line Interface to run the test with expected pass/fail csv for individual device
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp
        --device_list 1.11,1.12,1.360,1.400 --device_csv_name clab.csv --do_interopability

        EXAMPLE-7:
        Command Line Interface to run download scenario for Real clients with Groups and Profiles
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 100000000 --upload 100000000
        --traffic_type lf_udp --report_timer 1s --device_csv clab.csv --file_name gr204 --group_name g3,g4 --profile_name n1,n1 --do_interopability

        EXAMPLE-8:
        Command Line Interface to run download scenario for Real clients with device list and config
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp
        --ssid NETGEAR_2G_wpa2 --passwd Password@123 --security wpa2 --config --device_list 1.10,1.11,1.12 --do_interopability

        EXAMPLE-9:
        Command Line Interface to run the test with individual configuration
        python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth0 --test_duration 30s --traffic_type lf_udp --ssid NETGEAR_2G_wpa2 
        --passwd Password@123 --security wpa2 --do_interopability --device_list 1.15,1.400 --download 10000000 --interopability_config

    SCRIPT_CLASSIFICATION :  Test

    SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

    NOTES:
    1.Use './lf_interop_throughput.py --help' to see command line usage and options
    2.Please enter the download or upload rate in bps
    3.Inorder to perform intended load please pass 'wc_intended_load' in load_type argument.
    4.Please pass incremental values seperated by commas ',' in incremental_capacity argument
    5.Please enter packet_size in bps.
    6.After passing cli, a list will be displayed on terminal which contains available resources to run test.
    The following sentence will be displayed
    Enter the desired resources to run the test:
    Please enter the port numbers seperated by commas ','.
    Example:
    Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

    STATUS: BETA RELEASE

    VERIFIED_ON:
    Working date - 26/07/2024
    Build version - 5.4.8
    kernel version - 6.2.16+

    License: Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc.

"""


import sys
import os
import pandas as pd
import importlib
import logging
import json
import shutil
import asyncio
import csv
import matplotlib.pyplot as plt
import re

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import time  # noqa: E402
import argparse  # noqa: E402
from LANforge import LFUtils  # noqa: F401 E402
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
from lf_report import lf_report  # noqa: E402
from lf_graph import lf_bar_graph_horizontal  # noqa: E402
# from lf_graph import lf_line_graph  # noqa: E402

from datetime import datetime, timedelta  # noqa: E402

DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class Throughput(Realm):
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
                 device_list=None,
                 result_dir=None,
                 ap_name="",
                 traffic_type=None,
                 incremental_capacity=None,
                 incremental=False,
                 # packet_size=None,
                 report_timer="2m",
                 direction="",
                 side_a_min_rate=0, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 side_a_min_pdu=-1, side_b_min_pdu=-1,
                 number_template="00000",
                 test_duration="2m",
                 use_ht160=False,
                 load_type=None,
                 _debug_on=False,
                 dowebgui=False,
                 precleanup=False,
                 do_interopability=False,
                 get_live_view=False,
                 total_floors=0,
                 interopability_config = False,
                 ip="localhost",
                 csv_direction='',
                 device_csv_name=None,
                 expected_passfail_value=None,
                 file_name=None, group_name=None, profile_name=None,
                 eap_method=None,
                 eap_identity=None,
                 ieee80211=None,
                 ieee80211u=None,
                 ieee80211w=None,
                 enable_pkc=None,
                 bss_transition=None,
                 power_save=None,
                 disable_ofdma=None,
                 roam_ft_ds=None,
                 key_management=None,
                 pairwise=None,
                 private_key=None,
                 ca_cert=None,
                 client_cert=None,
                 pk_passwd=None,
                 pac_file=None,
                 wait_time=60,
                 config=False,
                 user_list=None, real_client_list=None, real_client_list1=None, hw_list=None, laptop_list=None, android_list=None, mac_list=None, windows_list=None, linux_list=None,
                 total_resources_list=None, working_resources_list=None, hostname_list=None, username_list=None, eid_list=None,
                 devices_available=None, input_devices_list=None, mac_id1_list=None, mac_id_list=None, overall_avg_rssi=None):
        super().__init__(lfclient_host=host,
                         lfclient_port=port)
        self.ssid_list = []
        self.signal_list = []
        self.channel_list = []
        self.mode_list = []
        self.link_speed_list = []
        self.background_run = None
        self.stop_test = False
        self.upstream = upstream
        self.host = host
        self.port = port
        self.test_name = test_name
        self.device_list = device_list if device_list is not None else []
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
        self.incremental_capacity = incremental_capacity
        self.load_type = load_type
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.report_timer = report_timer
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
        self.cx_profile.side_a_min_pdu = side_a_min_pdu
        self.cx_profile.side_b_min_pdu = side_b_min_pdu
        self.hw_list = hw_list if hw_list is not None else []
        self.laptop_list = laptop_list if laptop_list is not None else []
        self.android_list = android_list if android_list is not None else []
        self.mac_list = mac_list if mac_list is not None else []
        self.windows_list = windows_list if windows_list is not None else []
        self.linux_list = linux_list if linux_list is not None else []
        self.total_resources_list = total_resources_list if total_resources_list is not None else []
        self.working_resources_list = working_resources_list if working_resources_list is not None else []
        self.hostname_list = hostname_list if hostname_list is not None else []
        self.username_list = username_list if username_list is not None else []
        self.eid_list = eid_list if eid_list is not None else []
        self.devices_available = devices_available if devices_available is not None else []
        self.input_devices_list = input_devices_list if input_devices_list is not None else []
        self.real_client_list = real_client_list if real_client_list is not None else []
        self.real_client_list1 = real_client_list1 if real_client_list1 is not None else []
        self.user_list = user_list if user_list is not None else []
        self.mac_id_list = mac_id_list if mac_id_list is not None else []
        self.mac_id1_list = mac_id1_list if mac_id1_list is not None else []
        self.overall_avg_rssi = overall_avg_rssi if overall_avg_rssi is not None else []
        self.dowebgui = dowebgui
        self.do_interopability = do_interopability
        self.get_live_view = get_live_view
        self.total_floors = total_floors
        self.ip = ip
        self.device_found = False
        self.gave_incremental = False
        self.incremental = incremental
        self.precleanup = precleanup
        self.csv_direction = csv_direction
        self.expected_passfail_value = expected_passfail_value
        self.device_csv_name = device_csv_name
        self.file_name = file_name
        self.group_name = group_name
        self.profile_name = profile_name
        # for advanced config
        self.eap_method = eap_method
        self.eap_identity = eap_identity
        self.ieee80211 = ieee80211
        self.ieee80211u = ieee80211u
        self.ieee80211w = ieee80211w
        self.enable_pkc = enable_pkc
        self.bss_transition = bss_transition
        self.power_save = power_save
        self.disable_ofdma = disable_ofdma
        self.roam_ft_ds = roam_ft_ds
        self.key_management = key_management
        self.pairwise = pairwise
        self.private_key = private_key
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.pk_passwd = pk_passwd
        self.pac_file = pac_file
        self.wait_time = wait_time
        self.config = config
        self.configdevices = {}
        self.group_device_map = {}
        self.config_dict = {}
        self.configured_devices_check = {}
        self.interopability_config = interopability_config

    def os_type(self):
        """
        Determines OS type of selected devices.

        """
        response = self.json_get("/resource/all")
        if "resources" not in response.keys():
            logger.error("There are no real devices.")
            exit(1)

        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for _, b in element.items():
                        if "Apple" in b['hw version']:
                            if b['kernel'] == '':
                                self.hw_list.append('iOS')
                            else:
                                self.hw_list.append(b['hw version'])
                        else:
                            self.hw_list.append(b['hw version'])
        # print(self.hw_list)
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

    def disconnect_all_devices(self,devices_to_disconnect=[]):
        """
        Disconnects either all devices or a specific list of devices from Wi-Fi networks.
        """
        obj = DeviceConfig.DeviceConfig(lanforge_ip=self.host, file_name=self.file_name, wait_time=self.wait_time)
        # all_devices = obj.get_all_devices()
        # GET ANDROIDS FROM DEVICE LIST
        adb_obj = DeviceConfig.ADB_DEVICES(lanforge_ip=self.host)

        async def do_disconnect():
            all_devices = obj.get_all_devices()
            # TO DISCONNECT ALL DEVICES
            if len(devices_to_disconnect) == 0:
                android_resources = [d for d in all_devices if d.get('os') == 'Android' and d.get('eid') in self.device_list]
                if(len(android_resources)>0):
                    # TO STOP APP FOR ALL DEVICES FOR ANDROIDS
                    await adb_obj.stop_app(port_list=android_resources)
                # TO FORGET ALL NETWORKS FOR ALL OS TYPES
                await obj.connectivity(device_list=self.device_list, wifi_config=self.config_dict, disconnect=True)
                if(len(android_resources)>0):
                    adb_obj.set_wifi_state(port_list=android_resources, state = 'disable')
                
            # TO DISCONNECT SPECIFIC DEVICES
            else:
                android_resources = [d for d in all_devices if d.get('os') == 'Android' and d.get('eid') in devices_to_disconnect]
                if(len(android_resources)>0):
                    # To disable stop app for androids
                    await adb_obj.stop_app(port_list=android_resources)
                await obj.connectivity(device_list=devices_to_disconnect, wifi_config=self.config_dict, disconnect=True)
                if(len(android_resources)>0):
                    # To disable wifi for androids
                    adb_obj.set_wifi_state(port_list=android_resources, state = 'disable')

        asyncio.run(do_disconnect())
    
    def configure_specific(self,device_to_configure_list):
        """
        Configure specific devices using the provided list of device IDs or names.
        """
        obj = DeviceConfig.DeviceConfig(lanforge_ip=self.host, file_name=self.file_name, wait_time=self.wait_time)
        all_devices = obj.get_all_devices()
        android_resources = [d for d in all_devices if (d.get('os') == 'Android') and d.get('eid') in device_to_configure_list]
        laptop_resources = [d for d in all_devices if (d.get('os') != 'Android'  ) and '1.' + d.get('resource') in device_to_configure_list]
        devices_connected = asyncio.run(obj.connectivity(device_list=device_to_configure_list, wifi_config=self.config_dict))
        if len(devices_connected) > 0:
            if android_resources:
                self.configured_devices_check[android_resources[0]['user-name']] = True
            elif laptop_resources:
                self.configured_devices_check[laptop_resources[0]['hostname']] = True
            return True
        else:
            if android_resources:
                self.configured_devices_check[android_resources[0]['user-name']] = False
            elif laptop_resources:
                self.configured_devices_check[laptop_resources[0]['hostname']] = False
            return False

    def extract_digits_until_alpha(self,s):
        """
        Extracts digits (including decimals) from the start of a string until the first alphabet.
        """
        match = re.match(r'^[\d.]+', s)
        return match.group() if match else ''

    def phantom_check(self):
        """
        Checks for non-phantom resources and ports, categorizes them, and prepares a list of available devices for testing.

        """
        port_eid_list, same_eid_list, original_port_list = [], [], []
        interop_response = self.json_get("/adb")
        obj = DeviceConfig.DeviceConfig(lanforge_ip=self.host, file_name=self.file_name, wait_time=self.wait_time)
        upstream_port_ip = self.change_port_to_ip(self.upstream)
        config_devices = {}
        self.config_dict = {
            'ssid': self.ssid,
            'passwd': self.password,
            'enc': self.security,
            'eap_method': self.eap_method,
            'eap_identity': self.eap_identity,
            'ieee80211': self.ieee80211,
            'ieee80211u': self.ieee80211u,
            'ieee80211w': self.ieee80211w,
            'enable_pkc': self.enable_pkc,
            'bss_transition': self.bss_transition,
            'power_save': self.power_save,
            'disable_ofdma': self.disable_ofdma,
            'roam_ft_ds': self.roam_ft_ds,
            'key_management': self.key_management,
            'pairwise': self.pairwise,
            'private_key': self.private_key,
            'ca_cert': self.ca_cert,
            'client_cert': self.client_cert,
            'pk_passwd': self.pk_passwd,
            'pac_file': self.pac_file,
            'server_ip': upstream_port_ip
        }
        # When groups and profiles specified for configuration
        if self.group_name and self.file_name and self.device_list == [] and self.profile_name:
            selected_groups = self.group_name.split(',')
            selected_profiles = self.profile_name.split(',')
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]
            self.configdevices = config_devices
            obj.initiate_group()
            self.group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
            # Configuration of group of devices for the corresponding profiles
            self.device_list = asyncio.run(obj.connectivity(config_devices, upstream=upstream_port_ip))
        # Configuration of devices with SSID,Password and Security when device list is specified
        elif self.device_list != []:

            all_devices = obj.get_all_devices()

            self.device_list = self.device_list.split(',')
            if self.config:
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=self.config_dict))
        # Configuration of devices with SSID , Password and Security when the device list is not specified
        elif self.device_list == [] and self.config:
            all_devices = obj.get_all_devices()
            device_list = []
            for device in all_devices:
                if device["type"] == 'laptop':
                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                else:
                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
            logger.info("AVAILABLE RESOURCES", device_list)
            self.device_list = input("Enter the desired resources to run the test:").split(',')
            if self.config:
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=self.config_dict))

        # Retrieve all resources from the LANforge
        response = self.json_get("/resource/all")

        if "resources" not in response.keys():
            logger.error("There are no real devices.")
            exit(1)

        # Iterate over the response to categorize resources
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for (_, b) in element.items():

                        # Check if the resource is not phantom
                        if b['phantom'] is False:
                            self.working_resources_list.append(b["hw version"])

                            # Categorize based on hw version (type of device)
                            if "Win" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.windows_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] + " " + 'Win' + " " + b['hostname'])
                            elif "Linux" in b['hw version']:
                                if 'ct' not in b['hostname']:
                                    if 'lf' not in b['hostname']:
                                        self.eid_list.append(b['eid'])
                                        self.linux_list.append(b['hw version'])
                                        self.devices_available.append(b['eid'] + " " + 'Lin' + " " + b['hostname'])
                            elif "Apple" in b['hw version']:
                                if b['kernel'] == '':
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    if "devices"  in interop_response.keys():
                                        interop_devices = interop_response['devices']
                                        # Extract usernames of devices that match the current eid
                                        if(len([v['user-name'] for d in interop_devices for k, v in d.items() if v.get('resource-id') == b['eid']]) == 0):
                                            self.devices_available.append(b['eid'] + " " + 'iOS' + " " + b['hostname'])
                                        # If username is found
                                        else:
                                            ios_username = [v['user-name'] for d in interop_devices for k, v in d.items() if v.get('resource-id') == b['eid']][0]
                                            self.devices_available.append(b['eid'] + " " + 'iOS' + " " + ios_username)
                                    else:
                                        self.devices_available.append(b['eid'] + " " + 'iOS' + " " + b['hostname'])
                                else:
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                    self.devices_available.append(b['eid'] + " " + 'Mac' + " " + b['hostname'])
                            else:
                                self.eid_list.append(b['eid'])
                                self.android_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] + " " + 'android' + " " + b['user'])

        # Retrieve all ports from the endpoint
        response_port = self.json_get("/port/all")
        if "interfaces" not in response_port.keys():
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        # mac_id1_list=[]

        # Iterate over port information to filter and categorize ports
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():

                # Check conditions for non-phantom ports
                if (not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0" and port_data['alias'] != 'p2p0'):
                    # Check if the port's parent device matches with an eid in the eid_list
                    for id in self.eid_list:
                        if id + '.' in port:
                            original_port_list.append(port)
                            port_eid_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]))
                            self.mac_id1_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]) + ' ' + port_data['mac'])

        # Check for matching eids between eid_list and port_eid_list
        for i in range(len(self.eid_list)):
            for j in range(len(port_eid_list)):
                if self.eid_list[i] == port_eid_list[j]:
                    same_eid_list.append(self.eid_list[i])
        same_eid_list = [_eid + ' ' for _eid in same_eid_list]

        for eid in same_eid_list:
            for device in self.devices_available:
                if eid in device:
                    self.user_list.append(device)

        configure_list = []
        if len(self.device_list) == 0 and self.config is False and self.group_name is None:
            logger.info("AVAILABLE DEVICES TO RUN TEST : {}".format(self.user_list))
            self.device_list = input("Enter the desired resources to run the test:").split(',')
        # If self.device_list is provided, check availability against devices_available
        if len(self.device_list) != 0:
            devices_list = self.device_list
            available_list = []
            not_available = []

            # Iterate over each input device in devices_list
            for input_device in devices_list:
                found = False

                # Check if input_device exists in devices_available
                for device in self.devices_available:
                    if input_device + " " in device:
                        available_list.append(input_device)
                        found = True
                        break
                if found is False:
                    not_available.append(input_device)
                    if self.device_list != "all":
                        logger.warning(input_device + " is not available to run the test")

            for dev in available_list:
                for user in self.user_list:
                    if dev == user.split(" ")[0]:
                        if user not in configure_list:
                            configure_list.append(user)
            # If available_list is not empty, log info and set self.device_found to True
            if len(available_list) > 0:
                logger.info("Test is intiated on these devices {}".format(available_list))
                devices_list = ','.join(available_list)
                self.device_found = True
            else:
                devices_list = ""
                self.device_found = False
                if self.device_list != "all":
                    logger.warning("Test can not be initiated on any selected devices")
                    exit(1)

        else:
            devices_list = ","

        # If no devices are selected or only comma is entered, log an error and return False
        if devices_list == "all":
            devices_list = ""
        if (devices_list == ","):
            logger.error("Selected Devices are not available in the lanforge")
            return False, self.real_client_list

        # Split devices_list into resource_eid_list
        resource_eid_list = devices_list.split(',')
        logger.info("devices list {} {}".format(devices_list, resource_eid_list))
        resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]

        # Create resource_eid_list1 by appending dot to each eid in resource_eid_list
        resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
        logger.info("resource eid list {}".format(resource_eid_list1))

        # print("resource_eid_list2",resource_eid_list2)

        # Iterate over resource_eid_list1 and original_port_list to populate input_devices_list
        for eid in resource_eid_list1:
            for ports_m in original_port_list:
                if eid in ports_m:
                    self.input_devices_list.append(ports_m)
        logger.info("INPUT DEVICES LIST {}".format(self.input_devices_list))

        for i in resource_eid_list2:
            for j in range(len(self.user_list)):
                if i in self.user_list[j]:
                    self.real_client_list.append(self.user_list[j])
                    self.real_client_list1.append(self.user_list[j][:25])
        # print("real_client_list",self.real_client_list)
        # print("real_client_list1",self.real_client_list1)

        self.num_stations = len(self.real_client_list)

        # Iterate over resource_eid_list2 and mac_id1_list to populate mac_id_list
        for eid in resource_eid_list2:
            for i in self.mac_id1_list:
                if eid in i:
                    self.mac_id_list.append(i.strip(eid + ' '))
        # Runtime data for webui for configuration
        if self.dowebgui:
            if len(configure_list) == 0:
                logger.info("No device is available to run the test")
                obj = {
                    "status": "Stopped",
                    "configuration_status": "configured"
                }
                self.updating_webui_runningjson(obj)
                return
            else:
                obj = {
                    "configured_devices": configure_list,
                    "configuration_status": "configured"
                }
                self.updating_webui_runningjson(obj)

        # Check if incremental_capacity is provided and ensure selected devices are sufficient
        if (len(self.incremental_capacity) > 0 and int(self.incremental_capacity.split(',')[-1]) > len(self.mac_id_list)):
            logger.error("Devices selected is less than given incremental capacity")
            return False, self.real_client_list

        else:
            return True, self.real_client_list

    # Updates the status in the running.json file while running a test from the Web UI
    def updating_webui_runningjson(self, obj):
        data = {}
        with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name),
                  'r') as file:
            data = json.load(file)
            for key in obj:
                data[key] = obj[key]
        with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name),
                  'w') as file:
            json.dump(data, file, indent=4)

    def get_signal_and_channel_data(self, station_names):
        """
        Retrieves signal strength, channel, mode, and link speed data for the specified stations.

        """

        signal_list, channel_list, mode_list, link_speed_list, rx_rate_list = [], [], [], [], []
        interfaces_dict = dict()
        try:
            port_data = self.json_get('/ports/all/')['interfaces']
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        for port in port_data:
            interfaces_dict.update(port)
        for sta in station_names:
            if sta in interfaces_dict:
                if "dBm" in interfaces_dict[sta]['signal']:
                    signal_list.append(interfaces_dict[sta]['signal'].split(" ")[0])
                else:
                    signal_list.append(interfaces_dict[sta]['signal'])
            else:
                signal_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                channel_list.append(interfaces_dict[sta]['channel'])
            else:
                channel_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                mode_list.append(interfaces_dict[sta]['mode'])
            else:
                mode_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                link_speed_list.append(interfaces_dict[sta]['tx-rate'])
            else:
                link_speed_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                rx_rate_list.append(interfaces_dict[sta]['rx-rate'])
            else:
                rx_rate_list.append('-')
        return signal_list, channel_list, mode_list, link_speed_list, rx_rate_list

    def get_ssid_list(self, station_names):
        """
        Retrieves the SSID for the specified stations.

        """
        ssid_list = []

        try:
            port_data = self.json_get('/ports/all/')['interfaces']
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        interfaces_dict = dict()
        for port in port_data:
            interfaces_dict.update(port)
        for sta in station_names:
            if sta in interfaces_dict:
                ssid_list.append(interfaces_dict[sta]['ssid'])
            else:
                ssid_list.append('-')
        return ssid_list

    def build(self):
        """
        Builds and creates the connection profile.

        """
        self.create_cx()
        logger.info("cx build finished")
        return self.cx_profile.created_cx

    def create_cx(self):
        direction = ''

        # Determine direction based on side_a_min_bps and side_b_min_bps
        if int(self.cx_profile.side_b_min_bps) != 2560 and int(self.cx_profile.side_a_min_bps) != 2560:
            self.direction = "Bi-direction"
            direction = 'Bi-di'
        elif int(self.cx_profile.side_b_min_bps) != 2560:
            self.direction = "Download"
            direction = 'DL'
        else:
            if int(self.cx_profile.side_a_min_bps) != 2560:
                self.direction = "Upload"
                direction = 'UL'
        traffic_type = (self.traffic_type.strip("lf_")).upper()
        traffic_direction_list, cx_list, traffic_type_list = [], [], []
        for _ in range(len(self.real_client_list)):
            traffic_direction_list.append(direction)
            traffic_type_list.append(traffic_type)

        # Construct connection names
        for _ in self.tos:
            for i in self.real_client_list1:
                for j in traffic_direction_list:
                    for k in traffic_type_list:
                        cxs = "%s_%s_%s" % (i, k, j)
                        cx_names = cxs.replace(" ", "")
                cx_list.append(cx_names)
        logger.info('cx_list{}'.format(cx_list))
        count = 0

        # creating duplicate created_cx's for precleanup of CX's if there are already existed
        if self.precleanup is True:
            self.cx_profile.created_cx = {k: [k + '-A', k + '-B'] for k in cx_list}
            self.pre_cleanup()

        # for ip_tos in range(len(self.tos)):
        for device in range(len(self.input_devices_list)):
            logger.info("Creating connections for endpoint type: %s cx-count: %s" % (
                self.traffic_type, self.cx_profile.get_cx_count()))
            self.cx_profile.create(endp_type=self.traffic_type, side_a=[self.input_devices_list[device]],
                                   side_b=self.upstream, sleep_time=0, cx_name="%s" % (cx_list[count]))
            count += 1
        logger.info("cross connections with created")

    # def start(self,print_pass=False, print_fail=False):
    #     if(len(self.cx_profile.created_cx))>0:
    #         # print(type(self.cx_profile.created_cx),self.cx_profile.created_cx.keys())
    #         for cx in self.cx_profile.created_cx.keys():
    #             req_url = "cli-json/set_cx_report_timer"
    #             data = {
    #                 "test_mgr": "all",
    #                 "cx_name": cx,
    #                 "milliseconds": 1000
    #             }
    #             self.json_post(req_url, data)
    #     self.cx_profile.start_cx()

    def start_specific(self, cx_list):
        """
        Starts specific connections from the given list and sets a report timer for them.

        """
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if len(self.cx_profile.created_cx) > 0:
            for cx in cx_list:
                req_url = "cli-json/set_cx_report_timer"
                data = {
                    "test_mgr": "all",
                    "cx_name": cx,
                    "milliseconds": 1000
                }
                self.json_post(req_url, data)
        logger.info("Starting CXs...")
        for cx_name in cx_list:
            if self.debug:
                logger.debug("cx-name: {cx_name}".format(cx_name=cx_name))
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=self.debug)
        # self.cx_profile.start_cx_specific(cx_list)

    def stop_specific(self, cx_list):
        logger.info("Stopping specific CXs...")
        for cx_name in cx_list:
            if self.debug:
                logger.debug("cx-name: {cx_name}".format(cx_name=cx_name))
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }, debug_=self.debug)

    def stop(self):

        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup()

    def cleanup(self):
        logger.info("cleanup done")
        self.cx_profile.cleanup()

    def get_layer3_endp_data(self):
        """
        Fetches Layer 3 endpoint data for all created cross connections.

        Returns:
            dict: A dictionary with  Each key corresponds to
            the index of a each device in the order of cx_list, and its value is a list of 5 elements:
            [0]: RX rate (last) at the A endpoint
            [1]: RX rate (last) at the B endpoint
            [2]: RX drop percentage at the A endpoint
            [3]: RX drop percentage at the B endpoint
            [4]: Status of the Device ("Run" or "Stopped")
        """
        cx_list_endp = []
        cx_list_l3 = []
        for i in self.cx_profile.created_cx.keys():
            cx_list_endp.append(i + '-A')
            cx_list_endp.append(i + '-B')
            cx_list_l3.append(i)
        # Fetch required throughput data from Lanforge
        try:
            # for dynamic data, taken rx rate lasts from layer3 endp tab
            l3_endp_data = list(self.json_get('/endp/{}/list?fields=rx rate (last),rx drop %25,name,run,name'.format(','.join(cx_list_endp)))['endpoint'])
            l3_cx_data = self.json_get('/cx/all')
        except Exception as e:
            cx_data = self.json_get('/cx/all/')
            logger.info(cx_data)
            logger.error(f"Endpoint not fetched from API {e}")
        # Extracting and storing throughput data
        cx_list = list(self.cx_profile.created_cx.keys())
        i = 0
        throughput = {}
        # mapping the data based upon the cx_list order
        for cx in cx_list:
            throughput[i] = [0, 0, 0, 0, "Stopped",0]
            for j in l3_endp_data:
                key, value = next(iter(j.items()))
                endp_a = cx + '-A'
                endp_b = cx + '-B'
                if value['name'] == endp_a:
                    throughput[i][0] = value['rx rate (last)']
                    throughput[i][2] = value['rx drop %']
                elif value['name'] == endp_b:
                    throughput[i][1] = value['rx rate (last)']
                    throughput[i][3] = value['rx drop %']
                if value['name'] == endp_a or value['name'] == endp_b:
                    throughput[i][4] = 'Run' if value['run'] else 'Stopped'
            # To add average RTT
            for j in l3_cx_data:
                if(j == "handler" or j == "uri"):
                    continue
                if cx == l3_cx_data[j]['name']:
                    throughput[i][5] = l3_cx_data[j]['avg rtt']
            i += 1
        return throughput

    def monitor(self, iteration, individual_df, device_names, incremental_capacity_list, overall_start_time, overall_end_time, is_device_configured):
        individual_df_for_webui = individual_df.copy()  # for webui
        throughput, upload, download, upload_throughput, download_throughput, connections_upload, connections_download = {}, [], [], [], [], {}, {}
        drop_a, drop_a_per, drop_b, drop_b_per, state, state_of_device, avg_rtt = [], [], [], [], [], [], [] # noqa: F841
        test_stopped_by_user = False
        if (self.test_duration is None) or (int(self.test_duration) <= 1):
            raise ValueError("Monitor test duration should be > 1 second")
        if self.cx_profile.created_cx is None:
            raise ValueError("Monitor needs a list of Layer 3 connections")

        start_time = datetime.now()

        logger.info("Monitoring cx and endpoints")
        end_time = start_time + timedelta(seconds=int(self.test_duration))
        self.overall = []

        # Initialize variables for real-time connections data
        index = -1
        connections_upload = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_upload_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))

        # Initialize lists for throughput and drops for each connection
        [(upload.append([]), download.append([]), drop_a.append([]), drop_b.append([]), state.append([]), avg_rtt.append([])) for i in range(len(self.cx_profile.created_cx))]

        # If using web GUI, set runtime directory
        if self.dowebgui:
            runtime_dir = self.result_dir
        previous_time = datetime.now()
        time_break = 0
        # Continuously collect data until end time is reached
        while datetime.now() < end_time:
            index += 1
            current_time = datetime.now()
            signal_list, channel_list, mode_list, link_speed_list, rx_rate_list = self.get_signal_and_channel_data(self.input_devices_list)
            signal_list = [int(i) if i != "" else 0 for i in signal_list]
            throughput[index] = self.get_layer3_endp_data()
            # Check if next sleep would overshoot the end_time
            is_last_iteration = ((current_time + timedelta(seconds=1 if self.dowebgui else self.report_timer)) >= end_time)
            # For the WebUI, data is appended as "STOPPED" outside the loop.
            # To prevent the last record from being duplicated, break before exiting the loop.
            if is_last_iteration:
                break

            if self.dowebgui:
                time.sleep(1)  # for each second data in csv while ensuring webgui
                individual_df_data = []
                temp_upload, temp_download, temp_drop_a, temp_drop_b, temp_avg_rtt = [], [], [], [], []

                # Initialize temporary lists for each connection
                [(temp_upload.append([]), temp_download.append([]), temp_drop_a.append([]), temp_drop_b.append([]), temp_avg_rtt.append([])) for
                    i in range(len(self.cx_profile.created_cx))]

                # Populate temporary lists with current throughput data
                for i in range(len(throughput[index])):
                    if throughput[index][i][4] != 'Run':
                        temp_upload[i].append(0)
                        temp_download[i].append(0)
                        temp_drop_a[i].append(0)
                        temp_drop_b[i].append(0)
                        temp_avg_rtt[i].append(0)
                    else:
                        temp_upload[i].append(throughput[index][i][1])
                        temp_download[i].append(throughput[index][i][0])
                        temp_drop_a[i].append(throughput[index][i][2])
                        temp_drop_b[i].append(throughput[index][i][3])
                        temp_avg_rtt[i].append(throughput[index][i][5])
                # Calculate average throughput and drop percentages
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
                # time_difference = abs(end_time - datetime.now())
                overall_time_difference = abs(overall_end_time - datetime.now())
                overall_total_hours = overall_time_difference.total_seconds() / 3600
                overall_remaining_minutes = (overall_total_hours % 1) * 60
                timestamp = datetime.now().strftime("%d/%m %I:%M:%S %p")
                remaining_minutes_instrf = [str(int(overall_total_hours)) + " hr and " + str(int(overall_remaining_minutes)) +
                                            " min" if int(overall_total_hours) != 0 or int(overall_remaining_minutes) != 0 else '<1 min'][0]
                if remaining_minutes_instrf != '<1 min':
                    remaining_minutes_instrf = str(overall_time_difference).split(".")[0]
                # Storing individual device throughput data(download, upload, Rx % drop , Tx % drop) to dataframe
                for i in range(len(download_throughput)):
                    individual_df_data.extend([download_throughput[i], upload_throughput[i], drop_a_per[i], drop_b_per[i], temp_avg_rtt[i][0], int(signal_list[i]), link_speed_list[i], rx_rate_list[i]])

                # Storing Overall throughput data for all devices and also start time, end time, remaining time and status of test running
                individual_df_data.extend([round(sum(download_throughput),
                                                 2),
                                           round(sum(upload_throughput),
                                                 2),
                                           sum(drop_a_per),
                                           sum(drop_a_per),
                                           iteration + 1,
                                           timestamp,
                                           overall_start_time.strftime("%d/%m %I:%M:%S %p"),
                                           overall_end_time.strftime("%d/%m %I:%M:%S %p"),
                                           remaining_minutes_instrf,
                                           ', '.join(str(n) for n in incremental_capacity_list),
                                           'Running'])
                # Appending the data according to the time gap (for webgui)
                if (current_time - previous_time).total_seconds() >= time_break:
                    individual_df_for_webui.loc[len(individual_df_for_webui)] = individual_df_data
                    if self.group_name is None:
                        individual_df.to_csv('{}/throughput_data.csv'.format(runtime_dir), index=False)
                    else:
                        individual_df.to_csv('{}/overall_throughput.csv'.format(runtime_dir), index=False)
                    previous_time = current_time

                # Append data to individual_df and save to CSV
                individual_df.loc[len(individual_df)] = individual_df_data

                # Check if test was stopped by the user
                with open(runtime_dir + "/../../Running_instances/{}_{}_running.json".format(self.ip, self.test_name),
                          'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logger.warning('Test is stopped by the user')
                        test_stopped_by_user = True
                        break

                # Adjust time_gap based on elapsed time since start (for webui)
                d = datetime.now()
                if d - start_time <= timedelta(hours=1):
                    time_break = 5
                elif d - start_time > timedelta(hours=1) or d - start_time <= timedelta(
                        hours=6):
                    if end_time - d < timedelta(seconds=10):
                        time_break = 5
                    else:
                        time_break = 10
                elif d - start_time > timedelta(hours=6) or d - start_time <= timedelta(
                        hours=12):
                    if end_time - d < timedelta(seconds=30):
                        time_break = 5
                    else:
                        time_break = 30
                elif d - start_time > timedelta(hours=12) or d - start_time <= timedelta(
                        hours=24):
                    if end_time - d < timedelta(seconds=60):
                        time_break = 5
                    else:
                        time_break = 60
                elif d - start_time > timedelta(hours=24) or d - start_time <= timedelta(
                        hours=48):
                    if end_time - d < timedelta(seconds=60):
                        time_break = 5
                    else:
                        time_break = 90
                elif d - start_time > timedelta(hours=48):
                    if end_time - d < timedelta(seconds=120):
                        time_break = 5
                    else:
                        time_break = 120
            else:

                # If not using web GUI, sleep based on report timer
                individual_df_data = []
                time.sleep(self.report_timer)

                # Aggregate data from throughput

                for _, key in enumerate(throughput):
                    for i in range(len(throughput[key])):
                        upload[i], download[i], drop_a[i], drop_b[i], avg_rtt[i] = [], [], [], [], []
                        if throughput[key][i][4] != 'Run':
                            upload[i].append(0)
                            download[i].append(0)
                            drop_a[i].append(0)
                            drop_b[i].append(0)
                            avg_rtt[i].append(0)
                        else:
                            upload[i].append(throughput[key][i][1])
                            download[i].append(throughput[key][i][0])
                            drop_a[i].append(throughput[key][i][2])
                            drop_b[i].append(throughput[key][i][3])
                            avg_rtt[i].append(throughput[key][i][5])
                # Calculate average throughput and drop percentages
                upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
                download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
                drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
                drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]

                # Calculate overall time difference and timestamp
                timestamp = datetime.now().strftime("%d/%m %I:%M:%S %p")
                # # time_difference = abs(end_time - datetime.now())
                overall_time_difference = abs(overall_end_time - datetime.now())
                # # total_hours = time_difference.total_seconds() / 3600
                overall_total_hours = overall_time_difference.total_seconds() / 3600
                overall_remaining_minutes = (overall_total_hours % 1) * 60
                remaining_minutes_instrf = [str(int(overall_total_hours)) + " hr and " + str(int(overall_remaining_minutes)) +
                                            " min" if int(overall_total_hours) != 0 or int(overall_remaining_minutes) != 0 else '<1 min'][0]
                if remaining_minutes_instrf != '<1 min':
                    remaining_minutes_instrf = str(overall_time_difference).split(".")[0]
                # Storing individual device throughput data(download, upload, Rx % drop , Tx % drop) to dataframe
                for i in range(len(download_throughput)):
                    individual_df_data.extend([download_throughput[i], upload_throughput[i], drop_a_per[i], drop_b_per[i], avg_rtt[i][0], int(signal_list[i]), link_speed_list[i], rx_rate_list[i]])

                # Storing Overall throughput data for all devices and also start time, end time, remaining time and status of test running
                individual_df_data.extend([round(sum(download_throughput),
                                                 2),
                                           round(sum(upload_throughput),
                                                 2),
                                           sum(drop_a_per),
                                           sum(drop_a_per),
                                           iteration + 1,
                                           timestamp,
                                           overall_start_time.strftime("%d/%m %I:%M:%S %p"),
                                           overall_end_time.strftime("%d/%m %I:%M:%S %p"),
                                           remaining_minutes_instrf,
                                           ', '.join(str(n) for n in incremental_capacity_list),
                                           'Running'])
                individual_df.loc[len(individual_df)] = individual_df_data
                individual_df.to_csv('throughput_data.csv', index=False)

            if self.stop_test:
                test_stopped_by_user = True
                break
            if not self.background_run and self.background_run is not None:
                break
            # Exit the loop if the device is not connected or configured to match the provided SSID
            if not is_device_configured and self.interopability_config:
                break

        individual_df = individual_df[1:-1]
        individual_df_for_webui = individual_df_for_webui[1:-1]
        for _, key in enumerate(throughput):
            for i in range(len(throughput[key])):
                upload[i], download[i], drop_a[i], drop_b[i], avg_rtt[i] = [], [], [], [], []
                if throughput[key][i][4] != 'Run':
                    upload[i].append(0)
                    download[i].append(0)
                    drop_a[i].append(0)
                    drop_b[i].append(0)
                    avg_rtt[i].append(0)
                else:
                    upload[i].append(throughput[key][i][1])
                    download[i].append(throughput[key][i][0])
                    drop_a[i].append(throughput[key][i][2])
                    drop_b[i].append(throughput[key][i][3])
                    avg_rtt[i].append(throughput[key][i][5])

        individual_df_data = []
        upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
        download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
        drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
        drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
        signal_list, channel_list, mode_list, link_speed_list, rx_rate_list = self.get_signal_and_channel_data(self.input_devices_list)
        signal_list = [int(i) if i != "" else 0 for i in signal_list]

        # Storing individual device throughput data(download, upload, Rx % drop , Tx % drop) to dataframe after test stopped
        for i in range(len(download_throughput)):
            individual_df_data.extend([download_throughput[i], upload_throughput[i], drop_a_per[i], drop_b_per[i], avg_rtt[i][0], int(signal_list[i]), link_speed_list[i], rx_rate_list[i]])
        timestamp = datetime.now().strftime("%d/%m %I:%M:%S %p")

        # If it's the last iteration, append final metrics and 'Stopped' status
        if iteration + 1 == len(incremental_capacity_list):

            individual_df_data.extend([round(sum(download_throughput), 2), round(sum(upload_throughput), 2), sum(drop_a_per), sum(drop_a_per), iteration + 1, timestamp,
                                      overall_start_time.strftime("%d/%m %I:%M:%S %p"), timestamp, 0, ', '.join(str(n) for n in incremental_capacity_list), 'Stopped'])

        # If the test was stopped by the user, append metrics and 'Stopped' status
        elif test_stopped_by_user:

            individual_df_data.extend([round(sum(download_throughput), 2), round(sum(upload_throughput), 2), sum(drop_a_per), sum(drop_a_per), iteration + 1, timestamp,
                                      overall_start_time.strftime("%d/%m %I:%M:%S %p"), timestamp, 0, ', '.join(str(n) for n in incremental_capacity_list), 'Stopped'])

        # Otherwise, append metrics and 'Stopped' status with overall end time
        else:
            individual_df_data.extend([round(sum(download_throughput),
                                             2),
                                       round(sum(upload_throughput),
                                             2),
                                       sum(drop_a_per),
                                       sum(drop_a_per),
                                       iteration + 1,
                                       timestamp,
                                       overall_start_time.strftime("%d/%m %I:%M:%S %p"),
                                       overall_end_time.strftime("%d/%m %I:%M:%S %p"),
                                       remaining_minutes_instrf,
                                       ', '.join(str(n) for n in incremental_capacity_list),
                                       'Stopped'])
        individual_df.loc[len(individual_df)] = individual_df_data
        if self.dowebgui:
            individual_df_for_webui.loc[len(individual_df_for_webui)] = individual_df_data

        # Save individual_df to CSV based on web GUI status
        if self.dowebgui:
            if self.group_name:
                individual_df_for_webui.to_csv('{}/overall_throughput.csv'.format(runtime_dir), index=False)
                individual_df.to_csv('overall_throughput.csv', index=False)
            else:
                individual_df.to_csv('{}/throughput_data.csv'.format(runtime_dir), index=False)
                individual_df.to_csv('throughput_data.csv', index=False)
        else:
            individual_df.to_csv('throughput_data.csv', index=False)

        keys = list(connections_upload.keys())
        keys = list(connections_download.keys())

        for i in range(len(download_throughput)):
            connections_download.update({keys[i]: float(f"{(download_throughput[i]):.2f}")})
        for i in range(len(upload_throughput)):
            connections_upload.update({keys[i]: float(f"{(upload_throughput[i]):.2f}")})

        logger.info("connections download {}".format(connections_download))
        logger.info("connections upload {}".format(connections_upload))

        return individual_df, test_stopped_by_user

    def perform_intended_load(self, iteration, incremental_capacity_list):
        """
        Configures the intended load for each connection endpoint based on the provided iteration and incremental capacity.

        """

        for k in self.cx_profile.created_cx.values():
            endp_side_a = {
                "alias": k[0],
                # # "shelf": side_a_shelf,
                # # "resource": side_a_resource,
                # # "port": side_a_info[2],
                # # "type": endp_type,
                "min_rate": int(int(self.cx_profile.side_a_min_bps) / int(incremental_capacity_list[iteration])),
                # # "max_rate": int(int(self.cx_profile.side_a_max_bps)/int(incremental_capacity_list[iteration])),
                # # "min_pkt": self.side_a_min_pdu,
                # # "max_pkt": self.side_a_max_pdu,
                # # "ip_port": ip_port_a,
                # # "multi_conn": self.mconn_A,
            }
            endp_side_b = {
                "alias": k[1],
                # # "shelf": side_b_shelf,
                # # "resource": side_b_resource,
                # # "port": side_b_info[2],
                # # "type": endp_type,
                "min_rate": int(int(self.cx_profile.side_b_min_bps) / int(incremental_capacity_list[iteration])),
                # # "max_rate": int(int(self.cx_profile.side_b_max_bps)/int(incremental_capacity_list[iteration])),
                # # "min_pkt": self.side_b_min_pdu,
                # # "max_pkt": self.side_b_max_pdu,
                # # "ip_port": ip_port_b,
                # # "multi_conn": self.mconn_B,
            }

            # POST endpoint configuration for side_a and side_b

            url = "/cli-json/add_endp"
            self.json_post(_req_url=url,
                           _data=endp_side_a,
                           # #   debug_=debug_,
                           # #  suppress_related_commands_=suppress_related_commands
                           )
            self.json_post(_req_url=url,
                           _data=endp_side_b,
                           # # debug_=debug_,
                           # # suppress_related_commands_=suppress_related_commands
                           )

    def check_incremental_list(self):
        """
        Checks and generates a list of incremental capacities for connections.

        """
        if (len(self.incremental_capacity) == 0 and self.do_interopability is not True and self.incremental):
            self.incremental_capacity = input("Enter the incremental load to run the test:")

        cx_incremental_capacity_lists = []
        incremental_capacity_list_values = []
        device_list_length = len(self.mac_id_list)

        # Check if 'incremental_capacity' is not specified

        if len(self.incremental_capacity) == 0:
            incremental_capacity_1 = [device_list_length]

        elif (device_list_length != 0 and len(self.incremental_capacity.split(",")) > 0):
            device_list_length = len(self.mac_id_list)
            incremental_capacity_length = len(self.incremental_capacity.split(","))

            # Handle single incremental capacity specification

            if incremental_capacity_length == 1:
                temp_incremental_capacity_list = []
                incremental_capacity = int(self.incremental_capacity.split(",")[0])

                # Generate incremental capacity list

                for i in range(incremental_capacity, device_list_length):
                    if i % incremental_capacity == 0:
                        temp_incremental_capacity_list.append(i)

                # Ensure the last capacity covers all devices

                if device_list_length not in temp_incremental_capacity_list:
                    temp_incremental_capacity_list.append(device_list_length)
                incremental_capacity_1 = temp_incremental_capacity_list

            # Handle multiple incremental capacities specification

            else:
                incremental_capacity_1 = self.incremental_capacity.split(",")
        # Generate lists of incremental capacities

        for i in range(len(incremental_capacity_1)):
            new_cx_list = []
            if i == 0:
                x = 1
            else:
                x = cx_incremental_capacity_lists[-1][-1] + 1
            for j in range(x, int(incremental_capacity_1[i]) + 1):
                new_cx_list.append(j)
            incremental_capacity_list_values.append(new_cx_list[-1])
            cx_incremental_capacity_lists.append(new_cx_list)

        # Check completeness: last capacity list should cover all devices
        if incremental_capacity_list_values[-1] == device_list_length:
            return True
        else:
            return False

    def get_incremental_capacity_list(self):
        """

        Generates lists of incremental capacities and connection names for the created connections.

        """

        cx_incremental_capacity_lists, cx_incremental_capacity_names_lists, incremental_capacity_list_values = [], [], []

        created_cx_lists_keys = list(self.cx_profile.created_cx.keys())
        device_list_length = len(created_cx_lists_keys)

        # Check if incremental capacity is not provided
        if len(self.incremental_capacity) == 0:
            incremental_capacity_1 = [device_list_length]

        # Check if device list is not empty and incremental capacity is provided
        elif (device_list_length != 0 and len(self.incremental_capacity.split(",")) > 0):
            device_list_length = len(created_cx_lists_keys)
            incremental_capacity_length = len(self.incremental_capacity.split(","))

            # Handle case with a single incremental capacity value
            if incremental_capacity_length == 1:
                temp_incremental_capacity_list = []
                incremental_capacity = int(self.incremental_capacity.split(",")[0])

                # Calculate increments based on the provided capacity
                for i in range(incremental_capacity, device_list_length):
                    if i % incremental_capacity == 0:
                        temp_incremental_capacity_list.append(i)

                # Ensure the device list length itself is included in the increments
                if device_list_length not in temp_incremental_capacity_list:
                    temp_incremental_capacity_list.append(device_list_length)
                incremental_capacity_1 = temp_incremental_capacity_list

            # Handle case with multiple incremental capacity values
            else:
                incremental_capacity_1 = self.incremental_capacity.split(",")

        # Generate lists of incremental capacities and connection names

        for i in range(len(incremental_capacity_1)):
            new_cx_list = []
            new_cx_names_list = []
            if i == 0:
                x = 1
            else:
                x = cx_incremental_capacity_lists[-1][-1] + 1

            # Generate capacity list and corresponding names

            for j in range(x, int(incremental_capacity_1[i]) + 1):
                new_cx_list.append(j)
                new_cx_names_list.append(created_cx_lists_keys[j - 1])

            # Track the last capacity value for each list
            incremental_capacity_list_values.append(new_cx_list[-1])
            cx_incremental_capacity_lists.append(new_cx_list)
            cx_incremental_capacity_names_lists.append(new_cx_names_list)
        return cx_incremental_capacity_names_lists, cx_incremental_capacity_lists, created_cx_lists_keys, incremental_capacity_list_values

    # Ensures maximum of 60 plots in line graph
    def build_line_graph(self, data_set, xaxis_name, yaxis_name, xaxis_categories, label, graph_image_name):
        """
        Creates and saves a line graph showing throughput over time.

        - Plots each data point for all throughput data in dataset.
        - Shows only up to 60 labels on the x-axis to keep it readable.

        Returns:
        The name of the saved image file.
        """
        figsize = (10, 5)
        plt.figure(figsize=(figsize[0] + 5, figsize[1] + 2))

        color = ['forestgreen', 'c', 'r', 'g', 'b', 'p']
        marker = ['s', 'o', 'v']
        xaxis_categories = xaxis_categories[:-1]
        data_set = [data[:-1] for data in data_set]
        # Plot each dataset
        for i, data in enumerate(data_set):
            plt.plot(
                xaxis_categories,
                data,
                color=color[i % len(color)],  # Ensure no index error
                label=label[i],
                marker=marker[i % len(marker)]
            )

        plt.xlabel(xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(yaxis_name, fontweight='bold', fontsize=15)

        # Handle x-axis ticks dynamically based on data size
        data_size = len(xaxis_categories)
        if data_size <= 60:
            tick_positions = list(range(data_size))
        else:
            # Ensure 60 points including the first and last
            tick_count = min(60, data_size)
            interval = data_size / (tick_count - 1)
            tick_positions = [round(i * interval) for i in range(tick_count)]
            tick_positions = sorted(set(min(data_size - 1, max(0, pos)) for pos in tick_positions))
        tick_labels = [xaxis_categories[i] for i in tick_positions]

        plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=90)

        plt.grid(True, linestyle=':')  # Grid with dotted lines

        # Legend settings
        plt.legend(loc="best", ncol=1)

        plt.suptitle("", fontsize=16)
        plt.tight_layout()

        # Save the graph as an image
        plt.savefig(f"{graph_image_name}.png", dpi=96, bbox_inches="tight")
        plt.close()

        logger.debug("{}.png".format(graph_image_name))
        logger.debug("{}.csv".format(graph_image_name))

        return f"{graph_image_name}.png"
    
    def convert_to_table(self,configured_devices_check):
        """
        Returns usernames and their config status ('Pass' or 'Fail') as a dictionary.
        """
        return {
            "Username": list(configured_devices_check.keys()),
            "Configuration Status": ["Pass" if status else "Fail" for status in configured_devices_check.values()]
        }

    def generate_report(self, iterations_before_test_stopped_by_user, incremental_capacity_list, data=None, data1=None, report_path='', result_dir_name='Throughput_Test_report',
                        selected_real_clients_names=None):

        if self.do_interopability:
            result_dir_name = "Interopability_Test_report"

        self.ssid_list = self.get_ssid_list(self.input_devices_list)
        self.signal_list, self.channel_list, self.mode_list, self.link_speed_list, rx_rate_list = self.get_signal_and_channel_data(self.input_devices_list)

        if selected_real_clients_names is not None:
            self.num_stations = selected_real_clients_names

        # Initialize the report object
        if self.do_interopability is False:
            report = lf_report(_output_pdf="throughput.pdf", _output_html="throughput.html", _path=report_path,
                               _results_dir_name=result_dir_name)
            report_path = report.get_path()
            report_path_date_time = report.get_path_date_time()
            # df.to_csv(os.path.join(report_path_date_time, 'throughput_data.csv'))
            # For groups and profiles configuration through webgui
            if self.dowebgui is True and self.group_name:
                shutil.move('overall_throughput.csv', report_path_date_time)
            else:
                shutil.move('throughput_data.csv', report_path_date_time)
            logger.info("path: {}".format(report_path))
            logger.info("path_date_time: {}".format(report_path_date_time))
            report.set_title("Throughput Test")
            report.build_banner()

            # objective title and description
            report.set_obj_html(_obj_title="Objective",
                                _obj="The Candela Client Capacity test is designed to measure an Access Point’s client capacity and performance when handling different amounts of Real clients like android, Linux,"  # noqa: E501
                                " windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and measure the per client and the overall throughput for"  # noqa: E501
                                " this test, we aim to assess the capacity of network to handle high volumes of traffic while"
                                " each trial. Along with throughput other measurements made are client connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the"  # noqa: E501
                                " AP to be able to handle several stations (within the limitations of the AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that"  # noqa: E501
                                "scales well will not show a significant overall throughput decrease as more Real clients are added.")
            report.build_objective()
            report.set_obj_html(_obj_title="Input Parameters",
                                _obj="The below tables provides the input parameters for the test")
            report.build_objective()

            # Initialize counts and lists for device types
            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
            all_devices_names = []
            device_type = []
            packet_size_text = ''
            total_devices = ""
            if self.cx_profile.side_a_min_pdu == -1:
                packet_size_text = 'AUTO'
            else:
                packet_size_text = str(self.cx_profile.side_a_min_pdu) + ' Bytes'
            # Determine load type name based on self.load_type
            if self.load_type == "wc_intended_load":
                load_type_name = "Intended Load"
            else:
                load_type_name = "Per Client Load"
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
                    mac_devices += 1
                elif 'iOS' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                    device_type.append("iOS")
                    ios_devices += 1

            # Build total_devices string based on counts
            if android_devices > 0:
                total_devices += f" Android({android_devices})"
            if windows_devices > 0:
                total_devices += f" Windows({windows_devices})"
            if linux_devices > 0:
                total_devices += f" Linux({linux_devices})"
            if mac_devices > 0:
                total_devices += f" Mac({mac_devices})"
            if ios_devices > 0:
                total_devices += f" iOS({ios_devices})"

            # Determine incremental_capacity_data based on self.incremental_capacity
            if self.gave_incremental:
                incremental_capacity_data = "No Incremental values provided"
            elif len(self.incremental_capacity) == 1:
                if len(incremental_capacity_list) == 1:
                    incremental_capacity_data = str(self.incremental_capacity[0])
                else:
                    incremental_capacity_data = ','.join(map(str, incremental_capacity_list))
            elif (len(self.incremental_capacity) > 1):
                self.incremental_capacity = self.incremental_capacity.split(',')
                incremental_capacity_data = ', '.join(self.incremental_capacity)
            else:
                incremental_capacity_data = "None"

            # Construct test_setup_info dictionary for test setup table
            if self.group_name:
                group_names = ', '.join(self.configdevices.keys())
                profile_names = ', '.join(self.configdevices.values())
                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                test_setup_info = {
                    "Test name": self.test_name,
                    "Configuration": configmap,
                    "Configured Devices": ", ".join(all_devices_names),
                    "No of Devices": "Total" + f"({str(self.num_stations)})" + total_devices,
                    "Increment": incremental_capacity_data,
                    "Traffic Duration in minutes": round(int(self.test_duration) * len(incremental_capacity_list) / 60, 2),
                    "Traffic Type": (self.traffic_type.strip("lf_")).upper(),
                    "Traffic Direction": self.direction,
                    "Upload Rate(Mbps)": str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                    "Download Rate(Mbps)": str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                    "Load Type": load_type_name,
                    "Packet Size": packet_size_text
                }
            else:
                test_setup_info = {
                    "Test name": self.test_name,
                    "Device List": ", ".join(all_devices_names),
                    "No of Devices": "Total" + f"({str(self.num_stations)})" + total_devices,
                    "Increment": incremental_capacity_data,
                    "Traffic Duration in minutes": round(int(self.test_duration) * len(incremental_capacity_list) / 60, 2),
                    "Traffic Type": (self.traffic_type.strip("lf_")).upper(),
                    "Traffic Direction": self.direction,
                    "Upload Rate(Mbps)": str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                    "Download Rate(Mbps)": str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                    "Load Type": load_type_name,
                    "Packet Size": packet_size_text
                }
            report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

            # Loop through iterations and build graphs, tables for each iteration
            for i in range(len(iterations_before_test_stopped_by_user)):
                # rssi_signal_data=[]
                devices_on_running = []
                download_data = []
                upload_data = []
                upload_drop = []
                download_drop = []
                devices_data_to_create_bar_graph = []
                # signal_data=[]
                direction_in_table = []
                packet_size_in_table = []
                upload_list, download_list = [], []
                rssi_data = []
                data_iter = data[data['Iteration'] == i + 1]
                avg_rtt_data = []

                # for sig in self.signal_list[0:int(incremental_capacity_list[i])]:
                #     signal_data.append(int(sig)*(-1))
                # rssi_signal_data.append(signal_data)

                # Fetch devices_on_running from real_client_list
                for j in range(data1[i][-1]):
                    devices_on_running.append(self.real_client_list[j].split(" ")[-1])

                # Fetch download_data and upload_data based on load_type and direction
                for k in devices_on_running:
                    # individual_device_data=[]

                    # Checking individual device download and upload rate by searching device name in dataframe
                    columns_with_substring = [col for col in data_iter.columns if k in col]
                    filtered_df = data_iter[columns_with_substring]
                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop B" in col][0]].values.tolist()
                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop A" in col][0]].values.tolist()
                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                    if self.load_type == "wc_intended_load":
                        if self.direction == "Bi-direction":

                            # Append average download and upload data from filtered dataframe
                            download_data.append(round(sum(download_col) / len(download_col), 2))
                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                            # Append average upload and download drop from filtered dataframe
                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")
                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                        elif self.direction == 'Download':

                            # Append average download data from filtered dataframe
                            download_data.append(round(sum(download_col) / len(download_col), 2))

                            # Append 0 for upload data
                            upload_data.append(0)

                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                            # Append average download drop data from filtered dataframe

                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                        elif self.direction == 'Upload':

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)) + "Mbps")

                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                            # Append Average upload data from filtered dataframe
                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                            # Append 0 for download data
                            download_data.append(0)
                            # Append average upload drop data from filtered dataframe
                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                    else:

                        if self.direction == "Bi-direction":
                            # Append average download and upload data from filtered dataframe
                            download_data.append(round(sum(download_col) / len(download_col), 2))
                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                            # Append average download and upload drop data from filtered dataframe
                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                            # upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])
                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")

                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)
                        elif self.direction == 'Download':

                            # Append average download data from filtered dataframe
                            download_data.append(round(sum(download_col) / len(download_col), 2))
                            # Append 0 for upload data
                            upload_data.append(0)
                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                            # Append average download drop data from filtered dataframe
                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)
                        elif self.direction == 'Upload':

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                            # Append average upload data from filtered dataframe
                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                            # Append average upload drop data from filtered dataframe
                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))

                            # Append 0 for download data
                            download_data.append(0)

                            if self.cx_profile.side_a_min_pdu == -1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                data_set_in_graph = []

                # Depending on the test direction, retrieve corresponding throughput data,
                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                if self.direction == "Bi-direction":
                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data = ['Download', 'Upload']
                    real_time_data = (
                        f"Real Time Throughput: Achieved Throughput: Download: {round(sum(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "
                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                    )

                elif self.direction == 'Download':
                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    label_data = ['Download']
                    real_time_data = f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))), 2)} Mbps"

                elif self.direction == 'Upload':
                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data = ['Upload']
                    real_time_data = f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])), 2)} Mbps"

                if len(incremental_capacity_list) > 1:
                    report.set_custom_html(f"<h2><u>Iteration-{i + 1}: Number of Devices Running : {len(devices_on_running)}</u></h2>")
                    report.build_custom()

                report.set_obj_html(
                    _obj_title=f"{real_time_data}",
                    _obj=" ")
                report.build_objective()
                graph_png = self.build_line_graph(
                    data_set=data_set_in_graph,
                    xaxis_name="Time",
                    yaxis_name="Throughput (Mbps)",
                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                    label=label_data,
                    graph_image_name=f"line_graph{i}"
                )
                logger.info("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                report.move_graph_image()

                report.build_graph()
                x_fig_size = 15
                y_fig_size = len(devices_on_running) * .5 + 4
                report.set_obj_html(
                    _obj_title="Per Client Avg-Throughput",
                    _obj=" ")
                report.build_objective()
                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                _xaxis_name="Avg Throughput(Mbps)",
                                                _yaxis_name="Devices",
                                                _graph_image_name=f"image_name{i}",
                                                _label=label_data,
                                                _yaxis_categories=devices_on_running_trimmed,
                                                _legend_loc="best",
                                                _legend_box=(1.0, 1.0),
                                                _show_bar_value=True,
                                                _figsize=(x_fig_size, y_fig_size)
                                                )

                graph_png = graph.build_bar_graph_horizontal()
                logger.info("graph name {}".format(graph_png))
                graph.build_bar_graph_horizontal()
                report.set_graph_image(graph_png)
                report.move_graph_image()
                report.build_graph()
                report.set_obj_html(
                    _obj_title="RSSI Of The Clients Connected",
                    _obj=" ")
                report.build_objective()
                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                _xaxis_name="Signal(-dBm)",
                                                _yaxis_name="Devices",
                                                _graph_image_name=f"signal_image_name{i}",
                                                _label=['RSSI'],
                                                _yaxis_categories=devices_on_running_trimmed,
                                                _legend_loc="best",
                                                _legend_box=(1.0, 1.0),
                                                _show_bar_value=True,
                                                _figsize=(x_fig_size, y_fig_size)
                                                #    _color=['lightcoral']
                                                )
                graph_png = graph.build_bar_graph_horizontal()
                logger.info("graph name {}".format(graph_png))
                graph.build_bar_graph_horizontal()
                report.set_graph_image(graph_png)
                report.move_graph_image()
                report.build_graph()
                if(self.dowebgui and self.get_live_view):
                    # To add live view images coming from the Web-GUI in report
                    self.add_live_view_images_to_report(report)
                    
                if self.group_name:
                    report.set_obj_html(
                        _obj_title="Detailed Result Table For Groups ",
                        _obj="The below tables provides detailed information for the throughput test on each group.")
                else:

                    report.set_obj_html(
                        _obj_title="Detailed Result Table ",
                        _obj="The below tables provides detailed information for the throughput test on each device.")
                report.build_objective()
                self.mac_id_list = [item.split()[-1] if ' ' in item else item for item in self.mac_id_list]
                if self.expected_passfail_value or self.device_csv_name:
                    test_input_list, pass_fail_list = self.get_pass_fail_list(device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                if self.group_name:
                    for key, val in self.group_device_map.items():
                        if self.expected_passfail_value or self.device_csv_name:
                            # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                            dataframe = self.generate_dataframe(val,
                                                                device_type[0:int(incremental_capacity_list[i])],
                                                                devices_on_running[0:int(incremental_capacity_list[i])],
                                                                self.ssid_list[0:int(incremental_capacity_list[i])],
                                                                self.mac_id_list[0:int(incremental_capacity_list[i])],
                                                                self.channel_list[0:int(incremental_capacity_list[i])],
                                                                self.mode_list[0:int(incremental_capacity_list[i])],
                                                                direction_in_table[0:int(incremental_capacity_list[i])],
                                                                download_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                upload_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                test_input_list,
                                                                self.link_speed_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                pass_fail_list,
                                                                upload_drop,
                                                                download_drop)
                        # Generating Dataframe for groups when pass_fail case is not specified
                        else:
                            dataframe = self.generate_dataframe(val,
                                                                device_type[0:int(incremental_capacity_list[i])],
                                                                devices_on_running[0:int(incremental_capacity_list[i])],
                                                                self.ssid_list[0:int(incremental_capacity_list[i])],
                                                                self.mac_id_list[0:int(incremental_capacity_list[i])],
                                                                self.channel_list[0:int(incremental_capacity_list[i])],
                                                                self.mode_list[0:int(incremental_capacity_list[i])],
                                                                direction_in_table[0:int(incremental_capacity_list[i])],
                                                                download_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                upload_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                [],
                                                                self.link_speed_list[0:int(incremental_capacity_list[i])],
                                                                [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                [],
                                                                upload_drop,
                                                                download_drop)
                        if dataframe:
                            report.set_obj_html("", "Group: {}".format(key))
                            report.build_objective()
                            dataframe1 = pd.DataFrame(dataframe)
                            report.set_table_dataframe(dataframe1)
                            report.build_table()
                else:
                    bk_dataframe = {
                        " Device Type ": device_type[0:int(incremental_capacity_list[i])],
                        " Username": devices_on_running[0:int(incremental_capacity_list[i])],
                        " SSID ": self.ssid_list[0:int(incremental_capacity_list[i])],
                        " MAC ": self.mac_id_list[0:int(incremental_capacity_list[i])],
                        " Channel ": self.channel_list[0:int(incremental_capacity_list[i])],
                        " Mode": self.mode_list[0:int(incremental_capacity_list[i])],
                        # " Direction":direction_in_table[0:int(incremental_capacity_list[i])],
                        " Offered download rate ": download_list[0:int(incremental_capacity_list[i])],
                        " Observed Average download rate ": [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                        " Offered upload rate ": upload_list[0:int(incremental_capacity_list[i])],
                        " Observed Average upload rate ": [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                        " RSSI ": ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                        # " Link Speed ":self.link_speed_list[0:int(incremental_capacity_list[i])],
                        " Average RTT (ms)" : avg_rtt_data[0:int(incremental_capacity_list[i])],
                        " Packet Size(Bytes) ": [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                    }
                    if self.direction == "Bi-direction":
                        bk_dataframe[" Average Rx Drop B% "] = upload_drop
                        bk_dataframe[" Average Rx Drop A% "] = download_drop
                    elif self.direction == 'Download':
                        bk_dataframe[" Average Rx Drop A% "] = download_drop
                        # adding rx drop while uploading as 0
                        bk_dataframe[" Average Rx Drop B% "] = [0.0] * len(download_drop)

                    else:
                        bk_dataframe[" Average Rx Drop B% "] = upload_drop
                        # adding rx drop while downloading as 0
                        bk_dataframe[" Average Rx Drop A% "] = [0.0] * len(upload_drop)
                    if self.expected_passfail_value or self.device_csv_name:
                        bk_dataframe[" Expected " + self.direction + " rate "] = [str(n) + " Mbps" for n in test_input_list]
                        bk_dataframe[" Status "] = pass_fail_list
                    dataframe1 = pd.DataFrame(bk_dataframe)
                    report.set_table_dataframe(dataframe1)
                    report.build_table()

                report.set_custom_html('<hr>')
                report.build_custom()

        elif self.do_interopability:

            report = lf_report(_output_pdf="interopability.pdf", _output_html="interopability.html", _path=report_path,
                               _results_dir_name=result_dir_name)
            report_path = report.get_path()

            # To store throughput_data.csv in report folder
            report_path_date_time = report.get_path_date_time()
            shutil.move('throughput_data.csv', report_path_date_time)

            logger.info("path: {}".format(report_path))
            logger.info("path_date_time: {}".format(report_path_date_time))
            report.set_title("Interoperability Test")
            report.build_banner()
            # objective title and description
            report.set_obj_html(_obj_title="Objective",
                                _obj="The Candela Interoperability test is designed to measure an Access Point’s client performance when handling different amounts of Real clients"
                                " like android, Linux, windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and"
                                " measure the per-client throughput for each trial. Along with throughput other measurements made are client connection times, Station 4-Way"
                                " Handshake time, DHCP times, and more. The expected behavior is for the AP to be able to handle several stations (within the limitations of the"
                                " AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that scales well will not show a"
                                " significant overall throughput decrease as more Real clients are added.")
            report.build_objective()
            report.set_obj_html(_obj_title="Input Parameters",
                                _obj="The below tables provides the input parameters for the test")
            report.build_objective()

            # Initialize counts and lists for device types
            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
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
                    mac_devices += 1
                elif 'iOS' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                    device_type.append("iOS")
                    ios_devices += 1

            # Build total_devices string based on counts
            if android_devices > 0:
                total_devices += f" Android({android_devices})"
            if windows_devices > 0:
                total_devices += f" Windows({windows_devices})"
            if linux_devices > 0:
                total_devices += f" Linux({linux_devices})"
            if mac_devices > 0:
                total_devices += f" Mac({mac_devices})"
            if ios_devices > 0:
                total_devices += f" iOS({ios_devices})"

            # Construct test_setup_info dictionary for test setup table
            test_setup_info = {
                "Test name": self.test_name,
                "Device List": ", ".join(all_devices_names),
                "No of Devices": "Total" + f"({str(self.num_stations)})" + total_devices,
                "Traffic Duration in minutes": round(int(self.test_duration) * len(incremental_capacity_list) / 60, 2),
                "Traffic Type": (self.traffic_type.strip("lf_")).upper(),
                "Traffic Direction": self.direction,
                "Upload Rate(Mbps)": str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                "Download Rate(Mbps)": str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                # "Packet Size" : str(self.cx_profile.side_a_min_pdu) + " Bytes"
            }
            report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

            if(self.interopability_config):

                report.set_obj_html(_obj_title="Configuration Status of Devices",
                                    _obj="The table below shows the configuration status of each device (except iOS) with respect to the SSID connection.")
                report.build_objective()

                configured_dataframe = self.convert_to_table(self.configured_devices_check)
                dataframe1 = pd.DataFrame(configured_dataframe)
                report.set_table_dataframe(dataframe1)
                report.build_table()

            # Loop through iterations and build graphs, tables for each device
            for i in range(len(iterations_before_test_stopped_by_user)):
                # rssi_signal_data = []
                devices_on_running = []
                download_data = []
                upload_data = []
                devices_data_to_create_bar_graph = []
                # signal_data = []
                upload_drop = []
                download_drop = []
                direction_in_table = []
                # packet_size_in_table=[]
                upload_list, download_list = [], []
                rssi_data = []
                data_iter = data[data['Iteration'] == i + 1]
                avg_rtt_data = []

                # Fetch devices_on_running from real_client_list
                devices_on_running.append(self.real_client_list[data1[i][-1] - 1].split(" ")[-1])
                # If the device fails to configure, skip its data in the report
                if self.interopability_config and devices_on_running[0] in self.configured_devices_check and not self.configured_devices_check[devices_on_running[0]]:
                    continue

                for k in devices_on_running:
                    # individual_device_data=[]

                    # Checking individual device download and upload rate by searching device name in dataframe
                    columns_with_substring = [col for col in data_iter.columns if k in col]
                    filtered_df = data_iter[columns_with_substring]
                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop B" in col][0]].values.tolist()
                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop A" in col][0]].values.tolist()
                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                    if self.direction == "Bi-direction":

                        # Append download and upload data from filtered dataframe
                        download_data.append(round(sum(download_col) / len(download_col), 2))
                        upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                        upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                        download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                         len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")

                        direction_in_table.append(self.direction)
                    elif self.direction == 'Download':

                        # Append download data from filtered dataframe
                        download_data.append(round(sum(download_col) / len(download_col), 2))

                        # Append 0 for upload data
                        upload_data.append(0)
                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                         len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                        download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")

                        direction_in_table.append(self.direction)
                    elif self.direction == 'Upload':

                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                         len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                        upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                        # Append upload data from filtered dataframe
                        upload_data.append(round(sum(upload_col) / len(upload_col), 2))

                        # Append 0 for download data
                        download_data.append(0)

                        direction_in_table.append(self.direction)

                data_set_in_graph = []

                # Depending on the test direction, retrieve corresponding throughput data,
                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                if self.direction == "Bi-direction":
                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data = ['Download', 'Upload']
                    real_time_data = (
                        f"Real Time Throughput: Achieved Throughput: Download: "
                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]) / len(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "
                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]) / len(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                    )

                elif self.direction == 'Download':
                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    label_data = ['Download']
                    real_time_data = (
                        f"Real Time Throughput: Achieved Throughput: Download: "
                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]) / len(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                    )

                elif self.direction == 'Upload':
                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data = ['Upload']
                    real_time_data = (
                        f"Real Time Throughput: Achieved Throughput: Upload: "
                        f"{round(sum(upload_data[0:int(incremental_capacity_list[i])]) / len(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                    )

                report.set_custom_html(f"<h2><u>{i + 1}. Test On Device {', '.join(devices_on_running)}:</u></h2>")
                report.build_custom()

                report.set_obj_html(
                    _obj_title=f"{real_time_data}",
                    _obj=" ")
                report.build_objective()
                graph_png = self.build_line_graph(
                    data_set=data_set_in_graph,
                    xaxis_name="Time",
                    yaxis_name="Throughput (Mbps)",
                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                    label=label_data,
                    graph_image_name=f"line_graph{i}"
                )
                logger.info("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                report.move_graph_image()

                report.build_graph()
                x_fig_size = 15
                y_fig_size = len(devices_on_running) * .5 + 4
                report.set_obj_html(
                    _obj_title="Per Client Avg-Throughput",
                    _obj=" ")
                report.build_objective()
                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                _xaxis_name="Avg Throughput(Mbps)",
                                                _yaxis_name="Devices",
                                                _graph_image_name=f"image_name{i}",
                                                _label=label_data,
                                                _yaxis_categories=devices_on_running_trimmed,
                                                _legend_loc="best",
                                                _legend_box=(1.0, 1.0),
                                                _show_bar_value=True,
                                                _figsize=(x_fig_size, y_fig_size)
                                                )

                graph_png = graph.build_bar_graph_horizontal()
                logger.info("graph name {}".format(graph_png))
                graph.build_bar_graph_horizontal()
                report.set_graph_image(graph_png)
                report.move_graph_image()
                report.build_graph()
                report.set_obj_html(
                    _obj_title="RSSI Of The Clients Connected",
                    _obj=" ")
                report.build_objective()
                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                _xaxis_name="Signal(-dBm)",
                                                _yaxis_name="Devices",
                                                _graph_image_name=f"signal_image_name{i}",
                                                _label=['RSSI'],
                                                _yaxis_categories=devices_on_running_trimmed,
                                                _legend_loc="best",
                                                _legend_box=(1.0, 1.0),
                                                _show_bar_value=True,
                                                _figsize=(x_fig_size, y_fig_size)
                                                #    _color=['lightcoral']
                                                )
                graph_png = graph.build_bar_graph_horizontal()
                logger.info("graph name {}".format(graph_png))
                graph.build_bar_graph_horizontal()
                report.set_graph_image(graph_png)
                report.move_graph_image()
                report.build_graph()

                report.set_obj_html(
                    _obj_title="Detailed Result Table ",
                    _obj="The below tables provides detailed information for the throughput test on each device.")
                report.build_objective()
                self.mac_id_list = [item.split()[-1] if ' ' in item else item for item in self.mac_id_list]
                if self.expected_passfail_value or self.device_csv_name:
                    test_input_list, pass_fail_list = self.get_pass_fail_list(device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                bk_dataframe = {}

                # Dataframe changes with respect to groups and profiles in case of interopability
                if self.group_name:
                    interop_tab_data = self.json_get('/adb/')["devices"]
                    res_list = []
                    grp_name = []
                    if device_type[int(incremental_capacity_list[i]) - 1] != 'Android':
                        res_list.append(devices_on_running[-1])
                    else:
                        for dev in interop_tab_data:
                            for item in dev.values():
                                if item['user-name'] == devices_on_running[-1]:
                                    res_list.append(item['name'].split('.')[2])
                                    break
                    for key, value in self.group_device_map.items():
                        if res_list[-1] in value:
                            grp_name.append(key)
                            break
                    bk_dataframe["Group Name"] = grp_name[-1]

                bk_dataframe[" Device Type "] = device_type[int(incremental_capacity_list[i]) - 1]
                bk_dataframe[" Username"] = devices_on_running[-1]
                bk_dataframe[" SSID "] = self.ssid_list[int(incremental_capacity_list[i]) - 1]
                bk_dataframe[" MAC "] = self.mac_id_list[int(incremental_capacity_list[i]) - 1]
                bk_dataframe[" Channel "] = self.channel_list[int(incremental_capacity_list[i]) - 1]
                bk_dataframe[" Mode"] = self.mode_list[int(incremental_capacity_list[i]) - 1]
                bk_dataframe[" Offered download rate "] = download_list[-1]
                bk_dataframe[" Observed Average download rate "] = [str(download_data[-1]) + " Mbps"]
                bk_dataframe[" Offered upload rate "] = upload_list[-1]
                bk_dataframe[" Observed Average upload rate "] = [str(upload_data[-1]) + " Mbps"]
                bk_dataframe[" Average RTT (ms) "] = avg_rtt_data[-1]
                bk_dataframe[" RSSI "] = ['' if rssi_data[-1] == 0 else '-' + str(rssi_data[-1]) + " dbm"]

                if self.direction == "Bi-direction":
                    bk_dataframe[" Average Rx Drop B% "] = upload_drop
                    bk_dataframe[" Average Rx Drop A% "] = download_drop
                elif self.direction == 'Download':
                    bk_dataframe[" Average Rx Drop A% "] = download_drop
                    bk_dataframe[" Average Rx Drop B% "] = [0.0] * len(download_drop)
                else:
                    bk_dataframe[" Average Rx Drop B% "] = upload_drop
                    bk_dataframe[" Average Rx Drop A% "] = [0.0] * len(upload_drop)
                # When pass fail criteria is specified
                if self.expected_passfail_value or self.device_csv_name:
                    bk_dataframe[" Expected " + self.direction + " rate "] = test_input_list
                    bk_dataframe[" Status "] = pass_fail_list
                dataframe1 = pd.DataFrame(bk_dataframe)
                report.set_table_dataframe(dataframe1)
                report.build_table()

                report.set_custom_html('<hr>')
                report.build_custom()

            if(self.dowebgui and self.get_live_view and self.do_interopability):
                self.add_live_view_images_to_report(report)
            
        # report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf(_orientation="Landscape")

    # Creates a separate DataFrame for each group of devices.
    def generate_dataframe(self, groupdevlist, typeofdevice, devusername, devssid, devmac, devchannel, devmode, devdirection, devofdownload, devobsdownload,
                           devoffupload, devobsupload, devrssi, devExpected, devlinkspeed, devpacketsize, devstatus, upload_drop, download_drop):
        """
        Creates a separate DataFrame for each group of devices.

        Returns:
            DataFrame: A DataFrame for each device group.
            Returns None if neither device in a group is configured.
        """

        device_type = []
        username = []
        ssid = []
        mac = []
        channel = []
        mode = []
        direction = []
        offdownload = []
        obsdownload = []
        offupload = []
        obsupload = []
        rssi = []
        input_list = []
        linkspeed = []
        packetsize = []
        statuslist = []
        avg_updrop = []
        avg_dndrop = []
        interop_tab_data = self.json_get('/adb/')["devices"]
        for i in range(len(typeofdevice)):
            for j in groupdevlist:
                if j == devusername[i] and typeofdevice[i] != 'Android':
                    device_type.append(typeofdevice[i])
                    username.append(devusername[i])
                    ssid.append(devssid[i])
                    mac.append(devmac[i])
                    channel.append(devchannel[i])
                    mode.append(devmode[i])
                    direction.append(devdirection[i])
                    offdownload.append(devofdownload[i])
                    obsdownload.append(devobsdownload[i])
                    offupload.append(devoffupload[i])
                    obsupload.append(devobsupload[i])
                    rssi.append(devrssi[i])
                    linkspeed.append(devlinkspeed[i])
                    if len(upload_drop) != 0:
                        avg_updrop.append(upload_drop[i])
                    if len(download_drop) != 0:
                        avg_dndrop.append(download_drop[i])
                    if devpacketsize != []:
                        packetsize.append(devpacketsize[i])
                    if self.expected_passfail_value or self.device_csv_name:
                        statuslist.append(devstatus[i])
                        input_list.append(devExpected[i])

                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] == devusername[i] and j == item['name'].split('.')[2]:
                                device_type.append(typeofdevice[i])
                                username.append(devusername[i])
                                ssid.append(devssid[i])
                                mac.append(devmac[i])
                                channel.append(devchannel[i])
                                mode.append(devmode[i])
                                direction.append(devdirection[i])
                                offdownload.append(devofdownload[i])
                                obsdownload.append(devobsdownload[i])
                                offupload.append(devoffupload[i])
                                obsupload.append(devobsupload[i])
                                rssi.append(devrssi[i])

                                linkspeed.append(devlinkspeed[i])
                                if len(upload_drop) != 0:
                                    avg_updrop.append(upload_drop[i])
                                if len(download_drop) != 0:
                                    avg_dndrop.append(download_drop[i])
                                if devpacketsize != []:
                                    packetsize.append(devpacketsize[i])
                                if self.expected_passfail_value or self.device_csv_name:
                                    statuslist.append(devstatus[i])
                                    input_list.append(devExpected[i])
        if devpacketsize != []:
            if len(username) != 0:
                dataframe = {
                    " Device Type ": device_type,
                    " Username": username,
                    " SSID ": ssid,
                    " MAC ": mac,
                    " Channel ": channel,
                    " Mode": mode,
                    " Direction": direction,
                    " Offered download rate ": offdownload,
                    " Observed download rate ": obsdownload,
                    " Offered upload rate ": offupload,
                    " Observed upload rate ": obsupload,
                    " RSSI ": rssi,
                    " Link Speed ": linkspeed,
                    " Packet Size(Bytes) ": packetsize,
                }

                if self.direction == "Bi-direction":
                    dataframe[" Average Rx Drop B% "] = avg_updrop
                    dataframe[" Average Rx Drop A% "] = avg_dndrop
                elif self.direction == 'Download':
                    dataframe[" Average Rx Drop A% "] = avg_dndrop
                    # adding rx drop while uploading as 0
                    dataframe[" Average Rx Drop B% "] = [0.0] * len(avg_dndrop)

                else:
                    dataframe[" Average Rx Drop B% "] = avg_updrop

                    # adding rx drop while downloading as 0
                    dataframe[" Average Rx Drop A% "] = [0.0] * len(avg_updrop)
                if self.expected_passfail_value or self.device_csv_name:
                    dataframe[" Expected " + self.direction + " rate "] = input_list
                    dataframe[" Status "] = statuslist
                return dataframe
        else:
            if len(username) != 0:
                dataframe = {
                    " Device Type ": device_type,
                    " Username": username,
                    " SSID ": ssid,
                    " MAC ": mac,
                    " Channel ": channel,
                    " Mode": mode,
                    " Direction": direction,
                    " Offered download rate ": offdownload,
                    " Observed download rate ": obsdownload,
                    " Offered upload rate ": offupload,
                    " Observed upload rate ": obsupload,
                    " RSSI ": rssi,
                    " Link Speed ": linkspeed,
                }
                if self.direction == "Bi-direction":
                    dataframe[" Average Rx Drop B% "] = avg_updrop
                    dataframe[" Average Rx Drop A% "] = avg_dndrop
                elif self.direction == 'Download':
                    dataframe[" Average Rx Drop A% "] = avg_dndrop
                    # adding rx drop while uploading as 0
                    dataframe[" Average Rx Drop B% "] = [0.0] * len(avg_dndrop)

                else:
                    dataframe[" Average Rx Drop B% "] = avg_updrop

                    # adding rx drop while downloading as 0
                    dataframe[" Average Rx Drop A% "] = [0.0] * len(avg_updrop)
                if self.expected_passfail_value or self.device_csv_name:
                    dataframe[" Expected " + self.direction + " rate "] = input_list
                    dataframe[" Status "] = statuslist
                return dataframe

        return None

    def get_pass_fail_list(self, device_type, curr_incremental_capacity, devices_on_running, download_data, upload_data):
        test_input_list = []
        pass_fail_list = []
        if not self.do_interopability:
            # When pass_fail csv specified
            if self.expected_passfail_value == '' or self.expected_passfail_value is None:
                res_list = []
                interop_tab_data = self.json_get('/adb/')["devices"]
                for j in range(len(device_type[0:int(curr_incremental_capacity)])):
                    if device_type[0:int(curr_incremental_capacity)][j] != 'Android':
                        res_list.append(devices_on_running[0:int(curr_incremental_capacity)][j])
                    else:
                        for dev in interop_tab_data:
                            for item in dev.values():
                                if item['user-name'] == devices_on_running[0:int(curr_incremental_capacity)][j]:
                                    res_list.append(item['name'].split('.')[2])

                with open(self.device_csv_name, mode='r') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)
                for device in res_list:
                    found = False
                    for row in rows:
                        if row['DeviceList'] == device and row[self.csv_direction + ' Mbps'].strip() != '':
                            test_input_list.append(row[self.csv_direction + ' Mbps'])
                            found = True
                            break
                    if not found:
                        logger.info(f'Pass/Fail threshold for device {device} not found in the CSV. Using default threshold of 5 Mbps.')
                        test_input_list.append(5)
            # When expected_pass_fail value specified
            else:
                test_input_list = [self.expected_passfail_value for val in range(len(devices_on_running[0:int(curr_incremental_capacity)]))]

            for k in range(len(test_input_list)):
                if self.csv_direction.split('_')[2] == 'BiDi':
                    if float(test_input_list[k]) <= (float([n for n in upload_data[0:int(curr_incremental_capacity)]][k]) + float([n for n in download_data[0:int(curr_incremental_capacity)]][k])):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')
                elif self.csv_direction.split('_')[2] == 'UL':
                    if float(test_input_list[k]) <= float([n for n in upload_data[0:int(curr_incremental_capacity)]][k]):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')
                else:

                    if float(test_input_list[k]) <= float([n for n in download_data[0:int(curr_incremental_capacity)]][k]):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')
        else:
            if self.expected_passfail_value == '' or self.expected_passfail_value is None:
                res_list = []
                interop_tab_data = self.json_get('/adb/')["devices"]
                if device_type[int(curr_incremental_capacity) - 1] != 'Android':
                    res_list.append(devices_on_running[-1])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] == devices_on_running[-1]:
                                res_list.append(item['name'].split('.')[2])
                                break

                with open(self.device_csv_name, mode='r') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                for device in res_list:
                    found = False
                    for row in rows:
                        if row['DeviceList'] == device and row[self.csv_direction + ' Mbps'].strip() != '':
                            test_input_list.append(row[self.csv_direction + ' Mbps'])
                            found = True
                            break
                    if not found:
                        logger.info(f'Pass/Fail threshold for device {device} not found in the CSV. Using default threshold of 5 Mbps.')
                        test_input_list.append(5)
            # when expected_pass_fail value specified
            else:
                for _ in [devices_on_running[-1]]:
                    test_input_list.append(self.expected_passfail_value)
            for k in range(len(test_input_list)):
                if self.csv_direction.split('_')[2] == 'BiDi':
                    if float(test_input_list[k]) <= (float([n for n in [(upload_data[-1])]][k]) + float([n for n in [(download_data[-1])]][k])):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')
                elif self.csv_direction.split('_')[2] == 'UL':
                    if float(test_input_list[k]) <= float([n for n in [(upload_data[-1])]][k]):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')
                else:

                    if float(test_input_list[k]) <= float([n for n in [(download_data[-1])]][k]):
                        pass_fail_list.append('PASS')
                    else:
                        pass_fail_list.append('FAIL')

        return test_input_list, pass_fail_list

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

    # Converting the upstream_port to IP address for configuration purposes
    def change_port_to_ip(self, upstream_port):
        if upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except Exception:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def add_live_view_images_to_report(self,report):
        """
        This function looks for live view images for each floor
        in the 'live_view_images' folder within `self.result_dir`.
        It waits up to **60 seconds** for each image. If an image is found,
        it's added to the `report` on a new page; otherwise, it's skipped.
        """
        for floor in range(0,int(self.total_floors)):
            throughput_image_path = os.path.join(self.result_dir, "live_view_images", f"{self.test_name}_throughput_{floor+1}.png")
            rssi_image_path = os.path.join(self.result_dir, "live_view_images", f"{self.test_name}_rssi_{floor+1}.png")
            timeout = 60  # seconds
            start_time = time.time()

            while not (os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path)):
                if time.time() - start_time > timeout:
                    print("Timeout: Images not found within 60 seconds.")
                    break
                time.sleep(1)
            while not os.path.exists(throughput_image_path) and not os.path.exists(rssi_image_path):
                if os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path):
                    break
            if os.path.exists(throughput_image_path):
                report.set_custom_html('<div style="page-break-before: always;"></div>')
                report.build_custom()
                report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
                report.build_custom()

            if os.path.exists(rssi_image_path):
                report.set_custom_html('<div style="page-break-before: always;"></div>')
                report.build_custom()
                report.set_custom_html(f'<img src="file://{rssi_image_path}"></img>')
                report.build_custom()

# To validate the input args
def validate_args(args):
    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []
    if args.expected_passfail_value and args.device_csv_name:
        logger.error("Specify either expected_passfail_value or device_csv_name")
        exit(1)
    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)
    elif args.group_name and args.profile_name and args.file_name and args.device_list != []:
        logger.error("Either group name or device list should be entered not both")
        exit(1)
    elif args.ssid and args.profile_name:
        logger.error("Either ssid or profile name should be given")
        exit(1)
    elif args.file_name and (args.group_name is None or args.profile_name is None):
        logger.error("Please enter the correct set of groups and profiles")
        exit(1)
    if args.config and args.group_name is None:
        if args.ssid is None:
            logger.error('For configuration need to Specify SSID , Password(Optional for "open" type security) and Security')
            exit(1)
        else:
            if args.passwd == '[BLANK]' and args.security.lower() != 'open' or args.passwd != '[BLANK]' and args.security.lower() == 'open':
                logger.error('Please provide valid passwd and security configuration')
                exit(1)


def main():
    help_summary = '''\
    The Client Capacity test and Interopability test is designed to measure an Access Point’s client capacity and performance when handling different amounts of Real clients like android, Linux,
    windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and measure the per client and the overall throughput for
    this test, we aim to assess the capacity of network to handle high volumes of traffic while
    each trial. Along with throughput other measurements made are client connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the
    AP to be able to handle several stations (within the limitations of the AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that
    scales well will not show a significant overall throughput decrease as more Real clients are added.
    '''
    parser = argparse.ArgumentParser(
        prog="lf_interop_throughputput.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Provides the available devices and allows user to run the wifi capacity test
            on particular devices by specifying direction as upload, download and bidirectional including different types of loads and incremental capacity.
            ''',
        description='''\

NAME: lf_interop_throughputput.py

PURPOSE: lf_interop_throughput.py will provide the available devices and allows user to run the wifi capacity test
on particular devices by specifying direction as upload, download and bidirectional including different types of loads and incremental capacity.
Will also run the interopability test on particular devices by specifying direction as upload, download and bidirectional.

TO PERFORM THROUGHPUT TEST:

EXAMPLE-1:
Command Line Interface to run download scenario with desired resources
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --device_list 1.10,1.12

EXAMPLE-2:
Command Line Interface to run download scenario with incremental capacity
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000
--traffic_type lf_udp --incremental_capacity 1,2

EXAMPLE-3:
Command Line Interface to run upload scenario with packet size
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 0 --upload 1000000 --traffic_type lf_udp --packet_size 17

EXAMPLE-4:
Command Line Interface to run bi-directional scenario with load_type
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
--traffic_type lf_udp --load_type wc_intended_load

EXAMPLE-5:
Command Line Interface to run bi-directional scenario with report_timer
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
--traffic_type lf_udp --report_timer 5s

EXAMPLE-6:
Command Line Interface to run bi-directional scenario in Interop web-GUI
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
--traffic_type lf_udp --report_timer 5s --dowebgui

EXAMPLE-7:
Command Line Interface to run the test with precleanup
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --precleanup

EXAMPLE-8:
Command Line Interface to run the test with postcleanup
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --postcleanup

EXAMPLE-9:
Command Line Interface to run the test with incremental_capacity by raising incremental flag
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --incremental

TO PERFORM INTEROPABILITY TEST:

EXAMPLE-1:
Command Line Interface to run download scenario with desired resources
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --device_list 1.10,1.12

EXAMPLE-2:
Command Line Interface to run bi-directional scenario in Interop web-GUI
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 1000000 --upload 1000000
--traffic_type lf_udp --do_interopability --dowebgui

EXAMPLE-3:
Command Line Interface to run the test with precleanup
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --precleanup

EXAMPLE-4:
Command Line Interface to run the test with postcleanup
python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080  --upstream_port eth1 --test_duration 1m --download 1000000 --traffic_type lf_udp --do_interopability --postcleanup

EXAMPLE-5:
Command Line Interface to run the test with individual device configuration
python3 lf_interop_throughput.py --mgr 192.168.204.74 --mgr_port 8080 --upstream_port eth0 --test_duration 30s --traffic_type lf_udp --ssid NETGEAR_2G_wpa2 --passwd Password@123 --security wpa2 --do_interopability --device_list 1.15,1.400 --download 10000000 --interopability_config
SCRIPT_CLASSIFICATION :  Test

SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

NOTES:
1.Use './lf_interop_qos.py --help' to see command line usage and options
2.Please enter the download or upload rate in bps
3.Inorder to perform intended load please pass 'wc_intended_load' in load_type argument.
4.Please pass incremental values seperated by commas ',' in incremental_capacity argument.
5.Please enter packet_size in bps.
6.After passing cli, a list will be displayed on terminal which contains available resources to run test.
The following sentence will be displayed
Enter the desired resources to run the test:
Please enter the port numbers seperated by commas ','.
Example:
Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

STATUS: BETA RELEASE

VERIFIED_ON:
Working date - 26/07/2024
Build version - 5.4.8
kernel version - 6.2.16+

License: Free to distribute and modify. LANforge systems must be licensed.
Copyright 2023 Candela Technologies Inc.

''')

    required = parser.add_argument_group('Required arguments to run throughput.py')
    optional = parser.add_argument_group('Optional arguments to run throughput.py')

    required.add_argument('--device_list', help="Enter the devices on which the test should be run", default=[])
    required.add_argument('--mgr', '--lfmgr', default='localhost', help='hostname for where LANforge GUI is running')
    required.add_argument('--mgr_port', '--port', default=8080, help='port LANforge GUI HTTP service is running on')
    required.add_argument('--upstream_port', '-u', default='eth1', help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    required.add_argument('--ssid', help='WiFi SSID for script objects to associate to')
    required.add_argument('--passwd', '--password', '--key', default="[BLANK]", help='WiFi passphrase/password/key')
    required.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    required.add_argument('--upload', help='--upload traffic load per connection (upload rate)', default='2560')
    required.add_argument('--download', help='--download traffic load per connection (download rate)', default='2560')
    required.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="")
    required.add_argument('--report_timer', help='--duration to collect data', default="5s")
    required.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    required.add_argument('--dowebgui', help="If true will execute script for webgui", action='store_true')
    required.add_argument('--tos', default="Best_Efforts")
    required.add_argument('--packet_size', help='Determine the size of the packet in which Packet Size Should be Greater than 16B or less than 64KB(65507)', default="-1")
    required.add_argument('--incremental_capacity',
                          help='Specify the incremental values for network load testing as a comma-separated list (e.g., 10,20,30). This defines the increments in bandwidth to evaluate performance under varying load conditions.',  # noqa: E501
                          default=[])
    required.add_argument('--load_type', help="Determine the type of load: < wc_intended_load | wc_per_client_load >", default="wc_per_client_load")
    required.add_argument('--do_interopability', action='store_true', help='Ensures test on devices run sequentially, capturing each device’s data individually for plotting in the final report.')

    # optional.add_argument('--no_postcleanup', help="Cleanup the cross connections after test is stopped", action = 'store_true')
    # optional.add_argument('--no_precleanup', help="Cleanup the cross connections before test is started", action = 'store_true')
    optional.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action='store_true')
    optional.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action='store_true')
    optional.add_argument('--incremental', help='gives an option to the user to enter incremental values', action='store_true')
    optional.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    optional.add_argument('--test_name', help='Specify test name to store the runtime csv results', default=None)
    optional.add_argument('--result_dir', help='Specify the result dir to store the runtime logs', default='')
    optional.add_argument('--get_live_view', help="If true will heatmap will be generated from testhouse automation WebGui ", action='store_true')
    optional.add_argument('--total_floors', help="Total floors from testhouse automation WebGui ", default="0")
    optional.add_argument("--expected_passfail_value", help="Specify the expected number of urls", default=None)
    optional.add_argument("--device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    optional.add_argument("--eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    optional.add_argument("--eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    optional.add_argument("--ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    optional.add_argument("--ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    optional.add_argument("--ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    optional.add_argument("--enable_pkc", action="store_true", help='Enables pkc support.')
    optional.add_argument("--bss_transition", action="store_true", help='Enables BSS transition support.')
    optional.add_argument("--power_save", action="store_true", help='Enables power-saving features.')
    optional.add_argument("--disable_ofdma", action="store_true", help='Disables OFDMA support.')
    optional.add_argument("--roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    optional.add_argument("--key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    optional.add_argument("--pairwise", type=str, default='NA')
    optional.add_argument("--private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    optional.add_argument("--ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    optional.add_argument("--client_cert", type=str, default='NA', help='Specify the client certificate file name')
    optional.add_argument("--pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    optional.add_argument("--pac_file", type=str, default='NA', help='Specify the pac file name')
    optional.add_argument('--file_name', type=str, help='Specify the file name containing group details. Example:file1')
    optional.add_argument('--group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    optional.add_argument('--profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    optional.add_argument("--wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    optional.add_argument("--config", action="store_true", help="Specify for configuring the devices")
    optional.add_argument("--interopability_config", action="store_true", help="To do individual configuration for each device in interoperability")
    parser.add_argument('--help_summary', help='Show summary of what this script does', action="store_true")

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    if args.dowebgui:
        if (args.upload == '0'):
            args.upload = '2560'
        if (args.download == '0'):
            args.download = '2560'

    # logger_config = lf_logger_config.lf_logger_config()
    lf_logger_config.lf_logger_config()

    loads = {}
    iterations_before_test_stopped_by_user = []
    gave_incremental = False
    # Case based on download and upload arguments are provided
    if args.download and args.upload:
        loads = {'upload': str(args.upload).split(","), 'download': str(args.download).split(",")}
        loads_data = loads["download"]
    elif args.download:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for _ in range(len(args.download)):
            loads['upload'].append(2560)
        loads_data = loads["download"]
    else:
        if args.upload:
            loads = {'upload': str(args.upload).split(","), 'download': []}
            for _ in range(len(args.upload)):
                loads['download'].append(2560)
            loads_data = loads["upload"]

    if args.download != '2560' and args.download != '0' and args.upload != '0' and args.upload != '2560':
        csv_direction = 'L3_' + args.traffic_type.split('_')[1].upper() + '_BiDi'
    elif args.upload != '2560' and args.upload != '0':
        csv_direction = 'L3_' + args.traffic_type.split('_')[1].upper() + '_UL'
    else:
        csv_direction = 'L3_' + args.traffic_type.split('_')[1].upper() + '_DL'

    validate_args(args)
    if args.incremental_capacity == 'no_increment' and args.dowebgui:
        args.incremental_capacity = str(len(args.device_list.split(",")))
        gave_incremental = True

    if args.do_interopability:
        args.incremental_capacity = "1"

    # Parsing test_duration
    if args.test_duration.endswith('s') or args.test_duration.endswith('S'):
        args.test_duration = int(args.test_duration[0:-1])

    elif args.test_duration.endswith('m') or args.test_duration.endswith('M'):
        args.test_duration = int(args.test_duration[0:-1]) * 60

    elif args.test_duration.endswith('h') or args.test_duration.endswith('H'):
        args.test_duration = int(args.test_duration[0:-1]) * 60 * 60

    elif args.test_duration.endswith(''):
        args.test_duration = int(args.test_duration)

    # Parsing report_timer
    if args.report_timer.endswith('s') or args.report_timer.endswith('S'):
        args.report_timer = int(args.report_timer[0:-1])

    elif args.report_timer.endswith('m') or args.report_timer.endswith('M'):
        args.report_timer = int(args.report_timer[0:-1]) * 60

    elif args.report_timer.endswith('h') or args.report_timer.endswith('H'):
        args.report_timer = int(args.report_timer[0:-1]) * 60 * 60

    elif args.test_duration.endswith(''):
        args.report_timer = int(args.report_timer)

    if (int(args.packet_size) < 16 or int(args.packet_size) > 65507) and int(args.packet_size) != -1:
        logger.error("Packet size should be greater than 16 bytes and less than 65507 bytes incorrect")
        return

    for index in range(len(loads_data)):
        throughput = Throughput(host=args.mgr,
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
                                side_a_min_pdu=int(args.packet_size),
                                side_b_min_pdu=int(args.packet_size),
                                traffic_type=args.traffic_type,
                                tos=args.tos,
                                dowebgui=args.dowebgui,
                                test_name=args.test_name,
                                result_dir=args.result_dir,
                                device_list=args.device_list,
                                incremental_capacity=args.incremental_capacity,
                                report_timer=args.report_timer,
                                load_type=args.load_type,
                                do_interopability=args.do_interopability,
                                incremental=args.incremental,
                                precleanup=args.precleanup,
                                get_live_view= args.get_live_view,
                                total_floors = args.total_floors,
                                csv_direction=csv_direction,
                                expected_passfail_value=args.expected_passfail_value,
                                device_csv_name=args.device_csv_name,
                                file_name=args.file_name,
                                group_name=args.group_name,
                                profile_name=args.profile_name,
                                eap_method=args.eap_method,
                                eap_identity=args.eap_identity,
                                ieee80211=args.ieee8021x,
                                ieee80211u=args.ieee80211u,
                                ieee80211w=args.ieee80211w,
                                enable_pkc=args.enable_pkc,
                                bss_transition=args.bss_transition,
                                power_save=args.power_save,
                                disable_ofdma=args.disable_ofdma,
                                roam_ft_ds=args.roam_ft_ds,
                                key_management=args.key_management,
                                pairwise=args.pairwise,
                                private_key=args.private_key,
                                ca_cert=args.ca_cert,
                                client_cert=args.client_cert,
                                pk_passwd=args.pk_passwd,
                                pac_file=args.pac_file,
                                wait_time=args.wait_time,
                                config=args.config,
                                interopability_config = args.interopability_config
                                )

        if gave_incremental:
            throughput.gave_incremental = True
        throughput.os_type()

        check_condition, clients_to_run = throughput.phantom_check()

        if check_condition is False:
            return

        check_increment_condition = throughput.check_incremental_list()

        if check_increment_condition is False:
            logger.error("Incremental values given for selected devices are incorrect")
            return

        elif (len(args.incremental_capacity) > 0 and check_increment_condition is False):
            logger.error("Incremental values given for selected devices are incorrect")
            return

        created_cxs = throughput.build()
        time.sleep(10)
        created_cxs = list(created_cxs.keys())
        individual_dataframe_column = []

        to_run_cxs, to_run_cxs_len, created_cx_lists_keys, incremental_capacity_list = throughput.get_incremental_capacity_list()

        for i in range(len(clients_to_run)):

            # Extend individual_dataframe_column with dynamically generated column names
            individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop A {clients_to_run[i]}',
                                               f'Rx % Drop B{clients_to_run[i]}', f'RSSI {clients_to_run[i]} ', f'Tx-Rate {clients_to_run[i]} ', f'Rx-Rate {clients_to_run[i]} ', f'Rx-Rate {clients_to_run[i]} '])

        individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop A', 'Overall Rx % Drop B', 'Iteration',
                                           'TIMESTAMP', 'Start_time', 'End_time', 'Remaining_Time', 'Incremental_list', 'status'])
        individual_df = pd.DataFrame(columns=individual_dataframe_column)

        overall_start_time = datetime.now()
        overall_end_time = overall_start_time + timedelta(seconds=int(args.test_duration) * len(incremental_capacity_list))

        for i in range(len(to_run_cxs)):
            is_device_configured = True
            if args.do_interopability:
                # To get resource of device under test in interopability
                device_to_run_resource = throughput.extract_digits_until_alpha(to_run_cxs[i][0])

            # Check the load type specified by the user
            if args.load_type == "wc_intended_load":
                # Perform intended load for the current iteration
                throughput.perform_intended_load(i, incremental_capacity_list)
                if i != 0:

                    # Stop throughput testing if not the first iteration
                    throughput.stop()

                # Start specific connections for the current iteration
                throughput.start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
            else:
                if (args.do_interopability and i != 0):
                    throughput.stop_specific(to_run_cxs[i - 1])
                    time.sleep(5)
                if args.interopability_config:
                    if (args.do_interopability and i == 0):
                        # To disconnect all the selected devices at the starting selected 
                        throughput.disconnect_all_devices()
                    if args.do_interopability and "iOS" not in to_run_cxs[i][0]:
                        logger.info("Configuring device of resource{}".format(to_run_cxs[i][0]))
                        # To configure device which is under test
                        is_device_configured = throughput.configure_specific([device_to_run_resource])
                if is_device_configured:
                    throughput.start_specific(to_run_cxs[i])

            # Determine device names based on the current iteration
            device_names = created_cx_lists_keys[:to_run_cxs_len[i][-1]]

            # Monitor throughput and capture all dataframes and test stop status
            all_dataframes, test_stopped_by_user = throughput.monitor(i, individual_df, device_names, incremental_capacity_list, overall_start_time, overall_end_time, is_device_configured)
            if args.do_interopability and "iOS" not in to_run_cxs[i][0] and args.interopability_config:
                # Disconnecting device after running the test
                throughput.disconnect_all_devices([device_to_run_resource])
            # Check if the test was stopped by the user
            if test_stopped_by_user is False:

                # Append current iteration index to iterations_before_test_stopped_by_user
                iterations_before_test_stopped_by_user.append(i)
            else:

                # Append current iteration index to iterations_before_test_stopped_by_user
                iterations_before_test_stopped_by_user.append(i)
                break

    #     logger.info("connections download {}".format(connections_download))
    #     logger.info("connections upload {}".format(connections_upload))
    throughput.stop()
    if args.postcleanup:
        throughput.cleanup()
    throughput.generate_report(list(set(iterations_before_test_stopped_by_user)), incremental_capacity_list, data=all_dataframes, data1=to_run_cxs_len, report_path=throughput.result_dir)
    if throughput.dowebgui:
        # copying to home directory i.e home/user_name
        throughput.copy_reports_to_home_dir()


if __name__ == "__main__":
    main()
