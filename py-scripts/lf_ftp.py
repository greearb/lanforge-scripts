#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_ftp.py

PURPOSE:
lf_ftp.py will verify that N clients are connected on a specified band and can simultaneously download/upload
some amount of file data from the FTP server while measuring the time taken by clients to download/upload the file.

EXAMPLE-1:
Command Line Interface to run download scenario for Real clients
python3 lf_ftp.py --ssid Netgear-5g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --directions Download --clients_type Real --ap_name Netgear --bands 5G --upstream_port eth1

EXAMPLE-2:
Command Line Interface to run upload scenario on 6GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-6g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa3 --fiveg_radio wiphy2 --directions Upload --clients_type Virtual --ap_name Netgear --bands 6G --num_stations 2
--upstream_port eth1

EXAMPLE-3:
Command Line Interface to run download scenario on 5GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-5g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --fiveg_radio wiphy2 --directions Download --clients_type Virtual --ap_name Netgear --bands 5G --num_stations 2
--upstream_port eth1

EXAMPLE-4:
Command Line Interface to run upload scenario for Real clients
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --directions Download --clients_type Real --ap_name Netgear --bands 2.4G --upstream_port eth1

EXAMPLE-5:
Command Line Interface to run upload scenario on 2.4GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --twog_radio wiphy1 --directions Upload --clients_type Virtual --ap_name Netgear --bands 2.4G --num_stations 2
--upstream_port eth1

EXAMPLE-6:
Command Line Interface to run download scenario for Real clients with device list
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.214.219 --traffic_duration 1m --security wpa2
--directions Download --clients_type Real --ap_name Netgear --bands 2.4G --upstream_port eth1 --device_list 1.12,1.22

EXAMPLE-7:
Command Line Interface to run download scenario by setting the same expected Pass/Fail value for all devices
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --expected_passfail_value 4

EXAMPLE-8:
Command Line Interface to run download scenario by setting device specific Pass/Fail values in the csv file
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.204.74 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --device_csv_name device.csv

EXAMPLE-9:
Command Line Interface to run download scenario by Configuring Real Devices with SSID, Password, and Security
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_5G --passwd Password@123 --security wpa2 --config

EXAMPLE-10:
Command Line Interface to run download scenario by setting the same expected Pass/Fail value for all devices with configuration
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_2G --passwd Password@123 --security wpa2 --expected_passfail_value 4 --config

EXAMPLE-11:
Command Line Interface to run download scenario by setting device specific Pass/Fail values in the csv file without configuration
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_2G --passwd Password@123 --security wpa2 --device_csv_name device.csv

EXAMPLE-12:
Command Line Interface to run download scenario by Configuring Devices in Groups with Specific Profiles
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218  --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --file_name g219 --group_name grp1 --profile_name Open3

EXAMPLE-13:
Command Line Interface to run download scenario by Configuring Devices in Groups with Specific Profiles and expected Pass/Fail values
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --file_name g219 --group_name grp1 --profile_name Open3 --expected_passfail_value 3 --wait_time 30

SCRIPT_CLASSIFICATION : Test

SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

NOTES:
After passing cli, a list will be displayed on terminal which contains available resources to run test.
The following sentence will be displayed
Enter the desired resources to run the test:
Please enter the port numbers seperated by commas ','.
Example:
Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

STATUS : Functional

VERIFIED_ON:
26-JULY-2024,
GUI Version:  5.4.8
Kernel Version: 6.2.16+

LICENSE :
Copyright 2023 Candela Technologies Inc
Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README: False

"""
import sys
import importlib
import paramiko
import argparse
from datetime import datetime, timedelta
import time
import os
import requests
import json
import matplotlib.patches as mpatches
import pandas as pd
import logging
import shutil
from lf_graph import lf_bar_graph_horizontal
from typing import List, Optional
import asyncio
import csv

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
# Importing DeviceConfig to apply device configurations for ADB devices and laptops
DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class FtpTest(LFCliBase):
    def __init__(self, lfclient_host="localhost", lfclient_port=8080, sta_prefix="sta", start_id=0, num_sta=0, radio="",
                 dut_ssid=None, dut_security=None, dut_passwd=None, file_size=None, band=None, twog_radio=None,
                 file_name=None,
                 profile_name=None, group_name=None,
                 sixg_radio=None, fiveg_radio=None, upstream="eth1", _debug_on=False, _exit_on_error=False, _exit_on_fail=False, ap_name="",
                 direction=None, duration=None, traffic_duration=None, ssh_port=None, kpi_csv=None, kpi_results=None,
                 lf_username="lanforge", lf_password="lanforge", clients_type="Virtual", dowebgui=False, device_list=[], test_name=None, result_dir=None,
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
                 wait_time=60,
                 pk_passwd=None,
                 pac_file=None,
                 expected_passfail_val=None,
                 config=False,
                 csv_name=None):
        super().__init__(lfclient_host, lfclient_port, _debug=_debug_on, _exit_on_fail=_exit_on_fail)
        logger.info("Test is about to start")
        self.ssid_list = []
        self.host = lfclient_host
        self.port = lfclient_port
        # self.radio = radio
        self.profile_name = profile_name
        self.file_name = file_name
        self.group_name = group_name
        self.ap_name = ap_name
        self.result_dir = result_dir
        self.test_name = test_name
        self.upstream = upstream
        self.sta_prefix = sta_prefix
        self.sta_start_id = start_id
        self.num_sta = num_sta
        self.ssid = dut_ssid
        self.security = dut_security
        self.password = dut_passwd
        self.requests_per_ten = 600
        self.band = band
        self.lf_username = lf_username
        self.lf_password = lf_password
        self.kpi_csv = kpi_csv
        self.kpi_results = kpi_results
        self.file_size = file_size
        self.direction = direction
        self.twog_radio = twog_radio
        self.fiveg_radio = fiveg_radio
        self.sixg_radio = sixg_radio
        self.duration = duration
        self.dowebgui = dowebgui
        self.device_list = device_list
        self.traffic_duration = traffic_duration
        self.ssh_port = ssh_port
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.cx_profile = self.local_realm.new_http_profile()
        self.port_util = realm.PortUtils(self.local_realm)
        self.cx_profile.requests_per_ten = self.requests_per_ten
        self.clients_type = clients_type
        self.real_client_list = []
        self.working_resources_list = []
        self.hw_list = []
        self.windows_list = []
        self.windows_eid_list = []
        self.windows_ports = []
        self.mac_list = []
        self.linux_list = []
        self.android_list = []
        self.eid_list = []
        self.devices_available = []
        self.user_list = []
        self.input_devices_list = []
        self.mac_id1_list = []
        self.mac_id_list = []
        self.real_client_list1 = []
        self.uc_avg = []
        self.uc_min = []
        self.uc_max = []
        self.url_data = []
        self.bytes_rd = []
        self.rx_rate = []
        self.channel_list = []
        self.mode_list = []
        self.cx_list = []
        self.rssi_list = []
        self.tx_rate = []
        self.port_rx_rate = []
        self.individual_device_csv_names = []
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
        self.expected_passfail_val = expected_passfail_val
        self.csv_name = csv_name
        self.wait_time = wait_time
        self.config = config
        self.group_device_map = {}
        self.pass_fail_list = []
        self.test_input_list = []
        self.api_url = 'http://{}:{}'.format(self.host, self.port)

        logger.info("Test is Initialized")

    def query_realclients(self):
        config_devices = {}
        obj = DeviceConfig.DeviceConfig(lanforge_ip=self.host, file_name=self.file_name, wait_time=self.wait_time)
        upstream = self.change_port_to_ip(self.upstream)
        config_dict = {
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
            'server_ip': upstream,
        }
        # Case 1: Group name, file name, and profile name are provided, but device list is empty
        if self.group_name and self.file_name and self.device_list == [] and self.profile_name:
            selected_groups = self.group_name.split(',')
            selected_profiles = self.profile_name.split(',')
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]
            obj.initiate_group()
            self.group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
            # Configure devices in the selected group with the selected profile
            self.device_list = asyncio.run(obj.connectivity(config_devices, upstream=upstream))
        # Case 2: Device list is already provided
        elif self.device_list != []:
            all_devices = obj.get_all_devices()
            # self.device_list can be a string like "dev1,dev2" or a list; convert to list if it's a string
            if isinstance(self.device_list, str):
                self.device_list = self.device_list.split(',')
            # If config is false, the test will exclude all inactive devices
            if self.config:
                # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
                # Configure devices in the device list with the provided SSID, Password and Security
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=config_dict))
        # Case 3: Device list is empty but config flag is True — prompt the user to input device details for configuration
        elif self.device_list == [] and self.config:
            all_devices = obj.get_all_devices()
            device_list = []
            for device in all_devices:
                if device["type"] == 'laptop':
                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                else:
                    device_list.append(device["eid"] + " " + device["serial"])
            logger.info(f"Available devices: {device_list}")
            self.device_list = input("Enter the desired resources to run the test:").split(',')
            # If config is false, the test will exclude all inactive devices
            if self.config:
                # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
                # Configure devices entered by the user with the provided SSID, Password and Security
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=config_dict))
        response = self.json_get("/resource/all")
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for a, b in element.items():
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
        port_eid_list, same_eid_list, original_port_list = [], [], []
        response = self.json_get("/resource/all")
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for a, b in element.items():
                        if b['phantom'] is False:
                            self.working_resources_list.append(b["hw version"])
                            if "Win" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.windows_list.append(b['hw version'])
                                self.windows_eid_list.append(b['eid'])
                                # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                self.devices_available.append(b['eid'] + " " + 'Win' + " " + b['hostname'])
                            elif "Linux" in b['hw version']:
                                if ('ct' not in b['hostname']):
                                    if ('lf' not in b['hostname']):
                                        self.eid_list.append(b['eid'])
                                        self.linux_list.append(b['hw version'])
                                        # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                        self.devices_available.append(b['eid'] + " " + 'Lin' + " " + b['hostname'])
                            elif 'Apple' in b['hw version'] and (b['app-id'] != '') and (b['app-id'] != '0' or b['kernel'] == ''):
                                continue
                            elif "Apple" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.mac_list.append(b['hw version'])
                                # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                self.devices_available.append(b['eid'] + " " + 'Mac' + " " + b['hostname'])
                            else:
                                self.eid_list.append(b['eid'])
                                self.android_list.append(b['hw version'])
                                # self.username_list.append(b['eid']+ " " +b['user'])
                                self.devices_available.append(b['eid'] + " " + 'android' + " " + b['user'])
        # print("hostname list :",self.hostname_list)
        # print("username list :", self.username_list)
        # print("Available resources in resource tab :", self.devices_available)
        # print("eid_list : ",self.eid_list)
        # All the available resources are fetched from resource mgr tab ----

        response_port = self.json_get("/port/all")
        # print(response_port)
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if 'p2p0' not in port:
                    if (not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0"):
                        for id in self.eid_list:
                            if (id + '.' in port):
                                original_port_list.append(port)
                                port_eid_list.append(str(LFUtils.name_to_eid(port)[0]) + '.' + str(LFUtils.name_to_eid(port)[1]))
                                self.mac_id1_list.append(str(LFUtils.name_to_eid(port)[0]) + '.' + str(LFUtils.name_to_eid(port)[1]) + ' ' + port_data['mac'])
        # print("port eid list",port_eid_list)
        for i in range(len(self.eid_list)):
            for j in range(len(port_eid_list)):
                if self.eid_list[i] == port_eid_list[j]:
                    same_eid_list.append(self.eid_list[i])
        same_eid_list = [_eid + ' ' for _eid in same_eid_list]
        # print("same eid list",same_eid_list)
        # print("mac_id list",self.mac_id_list)
        # All the available ports from port manager are fetched from port manager tab ---

        for eid in same_eid_list:
            for device in self.devices_available:
                if eid in device:
                    print(eid + ' ' + device)
                    self.user_list.append(device)
        logger.info("AVAILABLE DEVICES TO RUN TEST: %s", self.user_list)
        logging.info(self.user_list)
        # Case 4: Config is False, no device list is provided, and no group is selected
        if not self.config and len(self.device_list) == 0 and self.group_name is None:
            logger.info("AVAILABLE DEVICES TO RUN TEST : {}".format(self.user_list))
            # Prompt the user to manually input devices for running the test
            self.device_list = input("Enter the desired resources to run the test:").split(',')
        if len(self.device_list) != 0:
            devices_list = self.device_list
            available_list = []
            not_available = []
            for input_device in devices_list:
                found = False
                for device in self.devices_available:
                    if input_device + " " in device:
                        available_list.append(input_device)
                        found = True
                        break
                if found is False:
                    not_available.append(input_device)
                    logging.warning(device + " is not available to run test")

            if len(available_list) > 0:

                logging.info("Test is initiated on devices: %s", available_list)
                devices_list = ','.join(available_list)
            else:
                devices_list = ""
                logging.warning("Test can not be initiated on any selected devices hence aborting the test")
                df1 = pd.DataFrame({
                    "client": self.client_list,
                    "url_data": 0,
                    "bytes_rd": 0,
                    "uc_min": 0,
                    "uc_max": 0,
                    "uc_avg": 0,
                    'status': 'Stopped'
                }
                )
                df1.to_csv('{}/ftp_datavalues.csv'.format(self.result_dir), index=False)
                raise ValueError("No Device is available to run the test hence aborting the test")
            logging.info("device got from webui are: %s", devices_list)
        else:
            devices_list = ""
        # print("devices list",devices_list)
        resource_eid_list = devices_list.split(',')
        resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]
        resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
        # print("resource eid list",resource_eid_list)

        if devices_list == "" or devices_list == ",":
            logger.warning(f"Can't run test on the selected devices. devices_list: '{devices_list}'")
            exit(1)
        # User desired eids are fetched ---

        for eid in resource_eid_list1:
            for ports_m in original_port_list:
                if eid in ports_m and 'p2p0' not in ports_m:
                    self.input_devices_list.append(ports_m)
        logging.info("INPUT DEVICES LIST %s", self.input_devices_list)

        # user desired real client list 1.1 wlan0 ---
        for port in self.input_devices_list:
            for eid in self.windows_eid_list:
                if eid + '.' in port:
                    self.windows_ports.append(port)
        for i in resource_eid_list2:
            for j in range(len(self.user_list)):
                if i in self.user_list[j]:
                    self.real_client_list.append(self.user_list[j])
                    self.real_client_list1.append((self.user_list[j]))
        print("REAL CLIENT LIST", self.real_client_list)
        # print("REAL CLIENT LIST1", self.real_client_list1)

        for eid in resource_eid_list2:
            for i in self.mac_id1_list:
                if eid in i:
                    self.mac_id_list.append(i.strip(eid + ' '))
        logging.info("MAC ID LIST %s", self.mac_id_list)
        return self.real_client_list, config_devices

    def set_values(self):
        '''This method will set values according user input'''
        if self.band == "6G":
            self.radio = [self.sixg_radio]
        elif self.band == "5G":
            self.radio = [self.fiveg_radio]
        elif self.band == "2.4G":
            self.radio = [self.twog_radio]
        elif self.band == "Both":
            self.radio = [self.fiveg_radio, self.twog_radio]

            # if Both then number of stations are half for 2.4G and half for 5G
            self.num_sta = self.num_sta // 2

        # converting minutes into time stamp
        self.pass_fail_duration = self.duration
        # self.duration = self.convert_min_in_time(self.duration)
        # self.traffic_duration = self.convert_min_in_time(self.traffic_duration)

        # file size in Bytes
        self.file_size_bytes = int(self.convert_file_size_in_Bytes(self.file_size))

    # Converts an upstream port name to its corresponding IP address if it's not already in IP format.
    def change_port_to_ip(self, upstream_port):
        if upstream_port.count('.') != 3:
            target_port_list = LFUtils.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except BaseException:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def precleanup(self):
        self.count = 0

        # delete everything in the GUI before starting the script
        '''try:
            self.local_realm.load("BLANK")
        except:
            print("Couldn't load 'BLANK' Test configurations")'''

        for rad in self.radio:
            if rad == self.sixg_radio:
                self.station_profile.mode = 15
                self.count = self.count + 1

            elif rad == self.fiveg_radio:

                # select mode(All stations will connects to 5G)
                self.station_profile.mode = 14
                self.count = self.count + 1

            elif rad == self.twog_radio:

                # select mode(All stations will connects to 2.4G)
                self.station_profile.mode = 13
                self.count = self.count + 1

            # check Both band if both band then for 2G station id start with 20
            if self.count == 2:
                self.sta_start_id = self.num_sta
                self.num_sta = 2 * (self.num_sta)

                # if Both band then first 20 stations will connects to 5G
                self.station_profile.mode = 14

                self.cx_profile.cleanup()

                # create station list with sta_id 20
                self.station_list1 = LFUtils.portNameSeries(prefix_=self.sta_prefix, start_id_=self.sta_start_id,
                                                            end_id_=self.num_sta - 1, padding_number_=10000,
                                                            radio=rad)

                # cleanup station list which started sta_id 20
                self.station_profile.cleanup(self.station_list1, debug_=self.debug)
                LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,
                                                   port_list=self.station_list,
                                                   debug=self.debug)

            # clean layer4 ftp traffic
            self.cx_profile.cleanup()
            self.station_list = LFUtils.portNameSeries(prefix_=self.sta_prefix, start_id_=self.sta_start_id,
                                                       end_id_=self.num_sta - 1, padding_number_=10000,
                                                       radio=rad)

            # cleans stations
            self.station_profile.cleanup(self.station_list, delay=1.5, debug_=self.debug)
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,
                                               port_list=self.station_list,
                                               debug=self.debug)
            time.sleep(1)

        logger.info("precleanup done")

    def build(self):
        # set ftp
        # self.port_util.set_ftp(port_name=self.local_realm.name_to_eid(self.upstream)[2], resource=2, on=True)
        rv = self.local_realm.name_to_eid(self.upstream)
        # rv[0]=shelf, rv[1]=resource, rv[2]=port
        self.port_util.set_ftp(port_name=rv[2], resource=rv[1], on=True)
        # self.port_util.set_ftp(port_name=rv, resource=rv[1], on=True)
        eth_list = []
        # list of upstream port
        eth_list.append(self.upstream)

        if (self.clients_type == "Virtual"):
            if self.band == "2.4G":
                self.station_profile.mode = 13
            elif self.band == "5G":
                self.station_profile.mode = 14
            elif self.band == "6G":
                self.station_profile.mode = 15
            for rad in self.radio:
                # station build
                self.station_profile.use_security(self.security, self.ssid, self.password)
                self.station_profile.set_number_template("00")
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                self.station_profile.create(radio=rad, sta_names_=self.station_list, debug=self.debug)
                self.local_realm.wait_until_ports_appear(sta_list=self.station_list)
                self.station_profile.admin_up()
                if self.local_realm.wait_for_ip(self.station_list):
                    self._pass("All stations got IPs")
                else:
                    self._fail("Stations failed to get IPs")
                    # exit(1)

            # building layer4
            logger.info("Build Layer4")
            self.cx_profile.direction = "dl"
            self.cx_profile.dest = "/dev/null"
            logger.info('Direction: %s', self.direction)

            if self.direction == "Download":
                # data from GUI for find out ip addr of upstream port
                data = self.json_get("ports/list?fields=IP")
                rv = self.local_realm.name_to_eid(self.upstream)
                # rv[0]=shelf, rv[1]=resource, rv[2]=port
                ip_upstream = None
                for i in data["interfaces"]:
                    for j in i:
                        # if "1.1." + self.upstream == j:
                        # ip_upstream = i["1.1." + self.upstream]['ip']
                        interface = "{shelf}.{resource}.{port}".format(shelf=rv[0], resource=rv[1], port=rv[2])
                        if interface == j:
                            ip_upstream = i[interface]['ip']
                            # print("ip_upstream:{ip_upstream}".format(ip_upstream=ip_upstream))

                        '''
                        elif self.upstream == j:
                            ip_upstream = i[self.upstream]['ip']
                        '''

                if ip_upstream is not None:
                    # print("station:{station_names}".format(station_names=self.station_profile.station_names))
                    # print("ip_upstream:{ip_upstream}".format(ip_upstream=ip_upstream))
                    self.cx_profile.create(ports=self.station_profile.station_names, ftp_ip=ip_upstream +
                                           "/ftp_test.txt",
                                           sleep_time=.5, debug_=self.debug, suppress_related_commands_=True, timeout=1000, ftp=True,
                                           user=self.lf_username,
                                           passwd=self.lf_password, source="", proxy_auth_type=0x200)

            elif self.direction == "Upload":
                dict_sta_and_ip = {}
                # data from GUI for find out ip addr of each station
                data = self.json_get("ports/list?fields=IP")

                # This loop for find out proper ip addr and station name
                for i in self.station_list:
                    for j in data['interfaces']:
                        for k in j:
                            if i == k:
                                dict_sta_and_ip[k] = j[i]['ip']

                # list of ip addr of all stations
                ip = list(dict_sta_and_ip.values())
                # print("build() - ip:{ip}".format(ip=ip))
                client_list = []

                # list of all stations
                for i in range(len(self.station_list)):
                    client_list.append(self.station_list[i][4:])
                # create layer four connection for upload
                for client_num in range(len(self.station_list)):
                    self.cx_profile.create(ports=eth_list, ftp_ip=ip[client_num] + "/ftp_test.txt", sleep_time=.5,
                                           debug_=self.debug, suppress_related_commands_=True, timeout=1000, ftp=True,
                                           user=self.lf_username, passwd=self.lf_password,
                                           source="", upload_name=client_list[client_num], proxy_auth_type=0x200)

        # check Both band present then build stations with another station list
        if self.count == 2:
            self.station_list = self.station_list1

            # if Both band then another 20 stations will connects to 2.4G
            self.station_profile.mode = 6
        logger.info("Test Build done")

        if self.clients_type == "Real":
            if self.direction == "Download":
                # data from GUI for find out ip addr of upstream port
                data = self.json_get("ports/list?fields=IP")
                rv = self.local_realm.name_to_eid(self.upstream)
                # rv[0]=shelf, rv[1]=resource, rv[2]=port
                ip_upstream = None
                for i in data["interfaces"]:
                    for j in i:
                        # if "1.1." + self.upstream == j:
                        # ip_upstream = i["1.1." + self.upstream]['ip']
                        interface = "{shelf}.{resource}.{port}".format(shelf=rv[0], resource=rv[1], port=rv[2])
                        if interface == j:
                            ip_upstream = i[interface]['ip']
                            # print("ip_upstream:{ip_upstream}".format(ip_upstream=ip_upstream))

                        '''
                        elif self.upstream == j:
                            ip_upstream = i[self.upstream]['ip']
                        '''

                if ip_upstream is not None:
                    # print("station:{station_names}".format(station_names=self.station_profile.station_names))
                    # print("ip_upstream:{ip_upstream}".format(ip_upstream=ip_upstream))
                    self.cx_profile.create(ports=self.input_devices_list, ftp_ip=ip_upstream +
                                           "/ftp_test.txt",
                                           sleep_time=.5, debug_=self.debug, suppress_related_commands_=True, interop=True, timeout=1000, ftp=True,
                                           user=self.lf_username,
                                           passwd=self.lf_password, source="", proxy_auth_type=0x200, windows_list=self.windows_ports)

            elif self.direction == "Upload":
                # list of upstream port
                # data from GUI for find out ip addr of each station
                data = self.json_get("ports/list?fields=IP")
                dict_sta_and_ip = {}

                # This loop for find out proper ip addr and station name
                for i in self.input_devices_list:
                    for j in data['interfaces']:
                        for k in j:
                            if i == k:
                                dict_sta_and_ip[k] = j[i]['ip']

                # list of ip addr of all stations
                ip = list(dict_sta_and_ip.values())
                # print("build() - ip:{ip}".format(ip=ip))
                # create layer four connection for upload
                for client in range(len(self.input_devices_list)):
                    self.cx_profile.create(ports=eth_list, ftp_ip=ip[client] + "/ftp_test.txt", sleep_time=.5,
                                           debug_=self.debug, suppress_related_commands_=True, timeout=1000, interop=True, ftp=True,
                                           user=self.lf_username, passwd=self.lf_password,
                                           source="", upload_name=self.input_devices_list[client], proxy_auth_type=0x200)

            # check Both band present then build stations with another station list
            # if self.count == 2:
            #     self.station_list = self.station_list1

            #     # if Both band then another 20 stations will connects to 2.4G
            #     self.station_profile.mode = 6
        self.cx_list = list(self.cx_profile.created_cx.keys())
        logger.info("Test Build done")

    def api_get(self, endp: str):
        """
        Sends a GET request to fetch data

        Args:
            endp (str): API endpoint

        Returns:
            response: response code for the request
            data: data returned in the response
        """
        if endp[0] != '/':
            endp = '/' + endp
        response = requests.get(url=self.api_url + endp)
        data = response.json()
        return response, data

    def start(self, print_pass=False, print_fail=False):
        for rad in self.radio:
            self.cx_profile.start_cx()

        logger.info("Test Started")

    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()
        # To update status of devices and remaining_time in ftp_datavalues.csv file to stopped and 0 respectively.
        if self.clients_type == 'Real':
            self.data["status"] = ["STOPPED"] * len(self.mac_id_list)
            self.data["remaining_time"] = ["0"] * len(self.mac_id_list)
            df1 = pd.DataFrame(self.data)
            df1.to_csv("ftp_datavalues.csv", index=False)

    def postcleanup(self):
        self.cx_profile.cleanup()
        # self.local_realm.load("BLANK")
        self.station_profile.cleanup(self.station_profile.station_names, delay=1.5, debug_=self.debug)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def filter_iOS_devices(self, device_list):
        modified_device_list = device_list
        if type(device_list) is str:
            modified_device_list = device_list.split(',')
        filtered_list = []
        for device in modified_device_list:
            if device.count('.') == 1:
                shelf, resource = device.split('.')
            elif device.count('.') == 2:
                shelf, resource, port = device.split('.')
            elif device.count('.') == 0:
                shelf, resource = 1, device
            response_code, device_data = self.api_get('/resource/{}/{}'.format(shelf, resource))
            if 'status' in device_data and device_data['status'] == 'NOT_FOUND':
                logger.info("Device %s is not found.", device)
                continue
            device_data = device_data['resource']
            # print(device_data)
            if 'Apple' in device_data['hw version'] and (device_data['app-id'] != '') and (device_data['app-id'] != '0' or device_data['kernel'] == ''):
                logger.info("%s is an iOS device. Currently, we do not support iOS devices.", device)
            else:
                filtered_list.append(device)
        if type(device_list) is str:
            filtered_list = ','.join(filtered_list)
        self.device_list = filtered_list
        return filtered_list

    def file_create(self):
        '''This method will Create file for given file size'''

        ip = self.host
        entity_id = self.local_realm.name_to_eid(self.upstream)
        # entity_id[0]=shelf, entity_id[1]=resource, entity_id[2]=port

        user = "root"
        pswd = "lanforge"
        port = self.ssh_port
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key

        # get upstream port ip-address from test ftp server
        if entity_id[1] > 1:
            resource_val = str(entity_id[1])
            ftp_resource_url = self.json_get("ports/1/" + resource_val + "/0/list?fields=IP")
            ftp_server_ip = ftp_resource_url["interface"]["ip"]
            ip = ftp_server_ip

        ssh.connect(ip, port=port, username=user, password=pswd, banner_timeout=600)
        cmd = '[ -f /home/lanforge/ftp_test.txt ] && echo "True" || echo "False"'
        stdin, stdout, stderr = ssh.exec_command(str(cmd))
        output = stdout.readlines()
        logger.info(output)
        if output == ["True\n"]:
            cmd1 = "rm /home/lanforge/ftp_test.txt"
            stdin, stdout, stderr = ssh.exec_command(str(cmd1))
            output = stdout.readlines()
            time.sleep(10)
            cmd2 = "sudo fallocate -l " + self.file_size + " /home/lanforge/ftp_test.txt"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            logger.info("File creation done %s", self.file_size)
            output = stdout.readlines()
        else:
            cmd2 = "sudo fallocate -l " + self.file_size + " /home/lanforge/ftp_test.txt"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            logger.info("File creation done %s", self.file_size)
            output = stdout.readlines()
        ssh.close()
        time.sleep(1)
        return output

    def convert_file_size_in_Bytes(self, size):
        '''convert file size MB or GB into Bytes'''

        '''
        if (size.endswith("MB")) or (size.endswith("Mb")) or (size.endswith("GB")) or (size.endswith("Gb")):
            if (size.endswith("MB")) or (size.endswith("Mb")):
                return float(size[:-2]) * 10 ** 6
            elif (size.endswith("GB")) or (size.endswith("Gb")):
                return float(size[:-2]) * 10 ** 9
        '''

        upper = size.upper()
        if upper.endswith("MB"):
            return float(upper[:-2]) * 10 ** 6
        elif upper.endswith("GB"):
            return float(upper[:-2]) * 10 ** 9
        # assume data is MB if no designator is on end of str
        else:
            return float(upper[:-2]) * 10 ** 6
    # FOR WEB-UI // function usd to fetch runtime values and fill the csv.

    def monitor_for_runtime_csv(self):

        time_now = datetime.now()
        start_time = time_now.strftime("%d/%m %I:%M:%S %p")
        duration = self.traffic_duration
        endtime = time_now + timedelta(seconds=duration)
        end_time = endtime
        endtime = endtime.isoformat()[0:19]
        current_time = datetime.now().isoformat()[0:19]
        self.data = {}
        self.data["url_data"] = []
        temp_data = {}
        max_bytes_rd = []
        rx_rate_val = []
        individual_device_data = {}
        for port in self.input_devices_list:
            columns = ['TIMESTAMP', 'Bytes-rd', 'total urls', 'download_rate', 'rx_rate', 'tx_rate', 'RSSI']
            individual_device_data[port] = pd.DataFrame(columns=columns)
        while (current_time < endtime):

            # data in json format
            # data = self.json_get("layer4/list?fields=bytes-rd")
            # uc_avg_data = self.json_get("layer4/list?fields=uc-avg")
            # uc_max_data = self.json_get("layer4/list?fields=uc-max")
            # uc_min_data = self.json_get("layer4/list?fields=uc-min")
            total_url_data = self.json_get("layer4/list?fields=total-urls")
            # bytes_rd = self.json_get("layer4/list?fields=bytes-rd")
            # Calling function to get devices data to append in ftp_datavalues.csv during runtime
            self.get_device_details()
            self.data["client"] = self.cx_list
            self.data["MAC"] = self.mac_id_list
            self.data["Channel"] = self.channel_list
            self.data["SSID"] = self.ssid_list
            self.data["Mode"] = self.mode_list
            self.data['UC-MIN'] = self.uc_min
            self.data['UC-AVG'] = self.uc_avg
            self.data['UC-MAX'] = self.uc_max

            rx_rate_val.append(list(self.rx_rate))
            for i, port in enumerate(self.input_devices_list):
                row_data = [current_time, self.bytes_rd[i], self.url_data[i], self.rx_rate[i], self.port_rx_rate[i], self.tx_rate[i], self.rssi_list[i]]
                individual_device_data[port].loc[len(individual_device_data[port])] = row_data
            # calculating average for rx_rate
            for j in range(len(rx_rate_val[0])):
                rx_rate_sum = 0
                non_zero = 0
                for i in range(len(rx_rate_val)):
                    if rx_rate_val[i][j] != 0:
                        rx_rate_sum += rx_rate_val[i][j]
                        non_zero += 1
                rx_rate_average = rx_rate_sum / non_zero if non_zero > 0 else 0
                self.rx_rate[j] = round(rx_rate_average, 4)
            dataset = self.rx_rate
            dataset = [round(x / 1000000, 4) for x in dataset]  # converting bps to mbps
            self.rx_rate = dataset
            self.data['Rx Rate(1m)'] = self.rx_rate
            # calculating max in bytes rd
            if len(max_bytes_rd) == 0:
                max_bytes_rd = list(self.bytes_rd)
            for i in range(len(max_bytes_rd)):
                self.bytes_rd[i] = max(max_bytes_rd[i], self.bytes_rd[i])
            max_bytes_rd = list(self.bytes_rd)

            self.data['Bytes RD'] = self.bytes_rd

            if 'endpoint' in total_url_data.keys():
                # list of layer 4 connections name
                # temp_data can be used to check data as well as check whether the endpoint has data
                if type(total_url_data['endpoint']) is dict:
                    temp_data[self.cx_list[0]] = total_url_data['endpoint']['total-urls']
                else:
                    for cx in total_url_data['endpoint']:
                        for CX in cx:
                            for created_cx in self.cx_list:
                                if CX == created_cx:
                                    temp_data[created_cx] = cx[CX]['total-urls']

                if temp_data != {}:

                    self.data["status"] = ["RUNNING"] * len(list(temp_data.keys()))
                    # self.data["url_data"] = list(temp_data.values())
                    self.data["url_data"] = self.url_data
                else:
                    self.data["status"] = ["RUNNING"] * len(self.cx_list)
                    self.data["url_data"] = [0] * len(self.cx_list)
                time_difference = abs(end_time - datetime.now())
                total_hours = time_difference.total_seconds() / 3600
                remaining_minutes = (total_hours % 1) * 60
                self.data["start_time"] = [start_time] * len(self.cx_list)
                self.data["end_time"] = [end_time.strftime("%d/%m %I:%M:%S %p")] * len(self.cx_list)
                self.data["remaining_time"] = [[str(int(total_hours)) + " hr and " + str(
                    int(remaining_minutes)) + " min" if int(total_hours) != 0 or int(
                    remaining_minutes) != 0 else '<1 min'][0]] * len(self.cx_list)
                df1 = pd.DataFrame(self.data)
                if self.dowebgui:
                    df1.to_csv('{}/ftp_datavalues.csv'.format(self.result_dir), index=False)
                if self.clients_type == 'Real':
                    df1.to_csv("ftp_datavalues.csv", index=False)

            else:

                logger.info("No layer 4-7 endpoints - No endpoint in reponse")

            time.sleep(5)
            if self.dowebgui == "True":
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                 self.test_name),
                          'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logging.info('Test is stopped by the user')
                        self.data["end_time"] = [datetime.now().strftime("%d/%m %I:%M:%S %p")] * len(self.cx_list)
                        break

            current_time = datetime.now().isoformat()[0:19]
        individual_device_csv_names = []
        for port, df in individual_device_data.items():
            df.to_csv(f"{endtime}-ftp-{port}.csv", index=False)
            individual_device_csv_names.append(f'{endtime}-ftp-{port}')
        self.individual_device_csv_names = individual_device_csv_names

    # Created a function to get uc-avg,uc,min,uc-max,ssid and all other details of the devices

    def get_device_details(self):
        dataset = []
        self.channel_list, self.mode_list, self.ssid_list, self.uc_avg, self.uc_max, self.url_data, self.uc_min, self.bytes_rd, self.rx_rate = [], [], [], [], [], [], [], [], []
        if self.clients_type == "Real":
            self.get_port_data()
        # data in json format
        # data = self.json_get("layer4/list?fields=bytes-rd")
        uc_avg_data = self.json_get("layer4/list?fields=uc-avg")
        uc_max_data = self.json_get("layer4/list?fields=uc-max")
        uc_min_data = self.json_get("layer4/list?fields=uc-min")
        total_url_data = self.json_get("layer4/list?fields=total-urls")
        bytes_rd = self.json_get("layer4/list?fields=bytes-rd")
        rx_rate = self.json_get("layer4/list?fields=rx rate (1m)")
        if 'endpoint' in uc_avg_data.keys():
            # list of layer 4 connections name
            if type(uc_avg_data['endpoint']) is dict:
                self.uc_avg.append(uc_avg_data['endpoint']['uc-avg'])
                self.uc_max.append(uc_max_data['endpoint']['uc-max'])
                self.uc_min.append(uc_min_data['endpoint']['uc-min'])
                self.rx_rate.append(rx_rate['endpoint']['rx rate (1m)'])
                # reading uc-avg data in json format
                self.url_data.append(total_url_data['endpoint']['total-urls'])
                dataset.append(bytes_rd['endpoint']['bytes-rd'])
                self.bytes_rd = [float(f"{(int(i) / 1000000): .4f}") for i in dataset]
            else:
                for created_cx in self.cx_list:
                    for cx in uc_avg_data['endpoint']:
                        if created_cx in cx:
                            self.uc_avg.append(cx[created_cx]['uc-avg'])
                            break

                    for cx in uc_max_data['endpoint']:
                        if created_cx in cx:
                            self.uc_max.append(cx[created_cx]['uc-max'])
                            break

                    for cx in uc_min_data['endpoint']:
                        if created_cx in cx:
                            self.uc_min.append(cx[created_cx]['uc-min'])
                            break

                    for cx in total_url_data['endpoint']:
                        if created_cx in cx:
                            self.url_data.append(cx[created_cx]['total-urls'])
                            break

                    for cx in bytes_rd['endpoint']:
                        if created_cx in cx:
                            dataset.append(cx[created_cx]['bytes-rd'])
                            break

                    for cx in rx_rate['endpoint']:
                        if created_cx in cx:
                            self.rx_rate.append(cx[created_cx]['rx rate (1m)'])
                            break
                self.bytes_rd = [float(f"{(i / 1000000): .4f}") for i in dataset]
                # for cx in uc_avg_data['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 self.uc_avg.append(cx[CX]['uc-avg'])
                # for cx in uc_max_data['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 self.uc_max.append(cx[CX]['uc-max'])
                # for cx in uc_min_data['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 self.uc_min.append(cx[CX]['uc-min'])
                # for cx in total_url_data['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 self.url_data.append(cx[CX]['total-urls'])
                # for cx in bytes_rd['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 dataset.append(cx[CX]['bytes-rd'])
                #                 self.bytes_rd=[float(f"{(i / 1000000): .4f}") for i in dataset]
                # for cx in rx_rate['endpoint']:
                #     for CX in cx:
                #         for created_cx in self.cx_list:
                #             if CX == created_cx:
                #                 self.rx_rate.append(cx[CX]['rx rate'])
        else:
            total_data = self.json_get("layer4/all")
            logger.info("No endpoint found")
            logger.info(total_data)

    def get_port_data(self):
        """
        Retrieves signal strength, rx rate, link speed(tx-rate), mode, ssid data for the specified devices from port.

        """
        station_names = self.input_devices_list
        interfaces_dict = dict()
        try:
            port_data = self.local_realm.json_get('/ports/all/')['interfaces']
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        for port in port_data:
            interfaces_dict.update(port)

        for sta in station_names:
            if sta in interfaces_dict:
                if "dBm" in interfaces_dict[sta]['signal']:
                    self.rssi_list.append(interfaces_dict[sta]['signal'].split(" ")[0])
                else:
                    self.rssi_list.append(interfaces_dict[sta]['signal'])
            else:
                self.rssi_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                self.tx_rate.append(interfaces_dict[sta]['tx-rate'])
            else:
                self.tx_rate.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                self.port_rx_rate.append(interfaces_dict[sta]['rx-rate'])
            else:
                self.port_rx_rate.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                self.channel_list.append(interfaces_dict[sta]['channel'])
            else:
                self.channel_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                self.mode_list.append(interfaces_dict[sta]['mode'])
            else:
                self.mode_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                self.ssid_list.append(interfaces_dict[sta]['ssid'])
            else:
                self.ssid_list.append('-')

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

    def my_monitor(self):
        dataset = []
        self.channel_list, self.mode_list, self.ssid_list, self.uc_avg, self.uc_max, self.url_data, self.uc_min, self.bytes_rd = [], [], [], [], [], [], [], []
        if self.clients_type == "Virtual":
            response_port = self.json_get("/port/all")
            for interface in response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.station_list:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.mac_id_list.append(str(port_data['mac']))
                        self.ssid_list.append(str(port_data['ssid']))
        elif self.clients_type == "Real":
            response_port = self.json_get("/port/all")
            for interface in response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.input_devices_list:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.ssid_list.append(str(port_data['ssid']))

        # data in json format
        # data = self.json_get("layer4/list?fields=bytes-rd")
        uc_avg_data = self.json_get("layer4/list?fields=uc-avg")
        uc_max_data = self.json_get("layer4/list?fields=uc-max")
        uc_min_data = self.json_get("layer4/list?fields=uc-min")
        total_url_data = self.json_get("layer4/list?fields=total-urls")
        bytes_rd = self.json_get("layer4/list?fields=bytes-rd")
        print(uc_avg_data)
        print(total_url_data)
        self.data_for_webui = {}

        if 'endpoint' in uc_avg_data.keys():
            # list of layer 4 connections name
            self.data_for_webui["client"] = self.cx_list
            if type(uc_avg_data['endpoint']) is dict:
                self.uc_avg.append(uc_avg_data['endpoint']['uc-avg'])
                self.uc_max.append(uc_max_data['endpoint']['uc-max'])
                self.uc_min.append(uc_min_data['endpoint']['uc-min'])
                # reading uc-avg data in json format
                self.url_data.append(total_url_data['endpoint']['total-urls'])
                dataset.append(bytes_rd['endpoint']['bytes-rd'])
                if self.dowebgui == "True":
                    self.data_for_webui["url_data"] = self.url_data
                    self.data_for_webui["start_time"] = self.data["start_time"]
                    self.data_for_webui["end_time"] = self.data["end_time"]
                    self.data_for_webui["remaining_time"] = [0] * len(self.cx_list)
                    self.data_for_webui["status"] = ["STOPPED"] * len(self.url_data)
                self.bytes_rd = [float(f"{(i / 1000000): .4f}") for i in dataset]
            else:
                for cx in uc_avg_data['endpoint']:
                    for CX in cx:
                        for created_cx in self.cx_list:
                            if CX == created_cx:
                                self.uc_avg.append(cx[CX]['uc-avg'])
                for cx in uc_max_data['endpoint']:
                    for CX in cx:
                        for created_cx in self.cx_list:
                            if CX == created_cx:
                                self.uc_max.append(cx[CX]['uc-max'])
                for cx in uc_min_data['endpoint']:
                    for CX in cx:
                        for created_cx in self.cx_list:
                            if CX == created_cx:
                                self.uc_min.append(cx[CX]['uc-min'])
                for cx in total_url_data['endpoint']:
                    for CX in cx:
                        for created_cx in self.cx_list:
                            if CX == created_cx:
                                self.url_data.append(cx[CX]['total-urls'])
                for cx in bytes_rd['endpoint']:
                    for CX in cx:
                        for created_cx in self.cx_list:
                            if CX == created_cx:
                                dataset.append(cx[CX]['bytes-rd'])
                                self.bytes_rd = [float(f"{(i / 1000000): .4f}") for i in dataset]
                if self.dowebgui == "True":
                    # FOR WEB-UI // storing values in self which is used to update the csv at the end.
                    self.data_for_webui["url_data"] = self.url_data
                    self.data_for_webui["bytes_rd"] = self.bytes_rd
                    self.data_for_webui["uc_min"] = self.uc_min
                    self.data_for_webui["uc_max"] = self.uc_max
                    self.data_for_webui["uc_avg"] = self.uc_avg
                    self.data_for_webui["start_time"] = self.data["start_time"]
                    self.data_for_webui["end_time"] = self.data["end_time"]
                    self.data_for_webui["remaining_time"] = [0] * len(self.cx_list)
            logger.info(f"uc_min,uc_max,uc_avg {self.uc_min},{self.uc_max},{self.uc_avg}")
            logger.info("total urls: %s", self.url_data)
        else:
            if self.dowebgui == "True":
                self.data["status"] = ["STOPPED"] * len(self.cx_list)
                if len(self.data["url_data"]) == 0:
                    self.data["url_data"] = [0] * len(self.cx_list)
                df1 = pd.DataFrame(self.data)
                df1.to_csv('{}/ftp_datavalues.csv'.format(self.result_dir), index=False)
            logger.info("No layer 4-7 endpoints")
            exit()

    def my_monitor_for_real_devices(self):
        self.channel_list, self.mode_list, self.ssid_list = [], [], []
        response_port = self.json_get("/port/all")
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if port in self.input_devices_list:
                    self.channel_list.append(str(port_data['channel']))
                    self.mode_list.append(str(port_data['mode']))
                    self.ssid_list.append(str(port_data['ssid']))
        if self.dowebgui:
            self.data_for_webui = {
                "client": self.cx_list,
                "url_data": self.url_data,
                "bytes rd": self.bytes_rd,
                "uc_min": self.uc_min,
                "uc_max": self.uc_max,
                "uc_avg": self.uc_avg,
                "start_time": self.data["start_time"],
                "end_time": self.data["end_time"],
                "remaining_time": [0] * len(self.cx_list)
            }

        logger.info("Monitoring complete")
        # exit()

    # The below method is useful when traffic is to be run for one url and stop - virtual clients and when pass/fail criteria is required
    # def my_monitor(self, time1):
    #     # data in json format
    #     data = self.json_get("layer4/list?fields=bytes-rd")

    #     if 'endpoint' in data.keys():
    #         # list of layer 4 connections name
    #         self.data1 = []
    #         if type(data['endpoint']) is dict:
    #             for i in range(self.num_sta):
    #                 self.data1.append((str(data['endpoint']['name'])))
    #         else:
    #             for i in range(self.num_sta):
    #                 self.data1.append((str(list(data['endpoint'][i].keys())))[2:-2])
    #         data2 = self.data1
    #         list_of_time = []
    #         list1 = []
    #         list2 = []
    #         counter = 0

    #         for i in range(self.num_sta):
    #             list_of_time.append(0)
    #         # running layer 4 traffic upto user given time
    #         while str(datetime.now() - time1) <= self.traffic_duration:
    #             if list_of_time.count(0) == 0:
    #                 break

    #             while list_of_time.count(0) != 0:

    #                 # run script upto given time
    #                 if counter == 0:
    #                     if str(datetime.now() - time1) >= self.duration:
    #                         counter = counter + 1
    #                         break
    #                 else:
    #                     if str(datetime.now() - time1) >= self.traffic_duration:
    #                         break

    #                 for i in range(self.num_sta):
    #                     data = self.json_get("layer4/list?fields=bytes-rd")
    #                     #print("data1",data)
    #                     # reading uc-avg data in json format
    #                     uc_avg = self.json_get("layer4/list?fields=uc-avg")
    #                     #print("uc_avg",uc_avg)
    #                     if type(data['endpoint']) is dict:
    #                         if int(data['endpoint']['bytes-rd']) <= self.file_size_bytes:
    #                             data = self.json_get("layer4/list?fields=bytes-rd")
    #                         if int(data['endpoint']['bytes-rd']) >= self.file_size_bytes:
    #                             list1.append(i)
    #                             if list1.count(i) == 1:
    #                                 list2.append(i)
    #                                 list1 = list2

    #                                 # stop station after download or upload file with particular size
    #                                 self.json_post("/cli-json/set_cx_state", {
    #                                     "test_mgr": "default_tm",
    #                                     "cx_name": "CX_" + data2[i],
    #                                     "cx_state": "STOPPED"
    #                                 }, debug_=self.debug)

    #                                 list_of_time[i] = round(int(uc_avg['endpoint']['uc-avg']) / 1000, 1)
    #                     else:
    #                         if int(data['endpoint'][i][data2[i]]['bytes-rd']) <= self.file_size_bytes:
    #                             data = self.json_get("layer4/list?fields=bytes-rd")
    #                         if int(data['endpoint'][i][data2[i]]['bytes-rd']) >= self.file_size_bytes:
    #                             list1.append(i)
    #                             if list1.count(i) == 1:
    #                                 list2.append(i)
    #                                 list1 = list2

    #                                 # stop station after download or upload file with particular size
    #                                 self.json_post("/cli-json/set_cx_state", {
    #                                     "test_mgr": "default_tm",
    #                                     "cx_name": "CX_" + data2[i],
    #                                     "cx_state": "STOPPED"
    #                                 }, debug_=self.debug)

    #                                 list_of_time[i] = round(int(uc_avg['endpoint'][i][data2[i]]['uc-avg']) / 1000, 1)
    #                 time.sleep(0.5)

    #         # method calling for throughput calculation
    #         self.throughput_calculation()

    #         # return list of download/upload time in seconds
    #         return list_of_time
    #     else:
    #         logger.info("No layer 4-7 endpoints")
    #         exit()

    def throughput_calculation(self):
        '''Method for calculate throughput of each station'''

        self.list_of_throughput = []
        data = self.json_get("layer4/list?fields=bytes-rd")
        for i in range(self.num_sta):
            if type(data['endpoint']) is dict:
                throughput = data['endpoint']['bytes-rd'] / 10 ** 6
            else:
                throughput = data['endpoint'][i][self.data1[i]]['bytes-rd'] / 10 ** 6
            if isinstance(throughput, float):
                self.list_of_throughput.append(round(throughput, 2))
            else:
                self.list_of_throughput.append(throughput)

    def ftp_test_data(self, list_time, pass_fail, bands, file_sizes, directions, num_stations):
        '''Method for arrange ftp download/upload time data in dictionary'''

        # creating dictionary for single iteration
        create_dict = {}

        create_dict["band"] = self.band
        create_dict["direction"] = self.direction
        create_dict["file_size"] = self.file_size
        create_dict["time"] = list_time
        create_dict["duration"] = self.pass_fail_duration
        create_dict["result"] = pass_fail
        create_dict["bands"] = bands
        create_dict["file_sizes"] = file_sizes
        create_dict["directions"] = directions
        create_dict["num_stations"] = num_stations
        create_dict["throughput"] = self.list_of_throughput

        return create_dict

    def convert_min_in_time(self, total_minutes):
        '''
        # Get hours with floor division
        hours = total_minutes // 60
        # Get additional minutes with modulus
        minutes = total_minutes % 60
        '''

        # Create time as a string
        time_string = str("%d:%02d" % (divmod(total_minutes, 60))) + ":00" + ":000000"

        return time_string

    def pass_fail_check(self, time_list):
        if max(time_list) < (self.pass_fail_duration * 60):
            return "Pass"
        else:
            return "Fail"

    def add_pass_fail_table(self, result_data):
        '''Method for create dict for pass/fail table for report'''

        self.column_head = []
        self.rows_head = []
        self.bands = result_data[1]["bands"]
        self.file_sizes = result_data[1]["file_sizes"]
        self.directions = result_data[1]["directions"]
        self.num_stations = result_data[1]["num_stations"]

        for size in self.file_sizes:
            for direction in self.directions:
                self.column_head.append(size + " " + direction)
        for band in self.bands:
            if band != "Both":
                self.rows_head.append(str(self.num_stations) + " Clients-" + band)
            else:
                self.rows_head.append(str(self.num_stations // 2) + "+" + str(self.num_stations // 2) + " Clients-2.4G+5G")

        # creating dict for a table
        table_dict_pass_fail = {}
        i = 0
        table_dict_pass_fail[""] = self.rows_head
        for size in self.file_sizes:
            for d in self.directions:
                list_data = []
                for b in self.bands:
                    for data in result_data.values():
                        if data["band"] == b and data["direction"] == d and data["file_size"] == size:
                            list_data.append(data["result"])

                table_dict_pass_fail[self.column_head[i]] = list_data
                i = i + 1

        return table_dict_pass_fail

    def download_upload_time_table(self, result_data):
        '''Method for create dict for download/upload table for report'''
        # print("download_upload_time_table - result_data:{result_data}".format(result_data=result_data))
        table_dict_time = {}
        string_data = ""
        i = 0
        table_dict_time[""] = self.rows_head
        self.kpi_results = []

        for size in self.file_sizes:
            for d in self.directions:
                list_data = []
                for b in self.bands:
                    for data in result_data.values():
                        data_time = data['time']
                        if data_time.count(0) == 0:
                            Min = min(data_time)
                            Max = max(data_time)
                            Sum = int(sum(data_time))
                            Len = len(data_time)
                            Avg = round(Sum / Len, 2)
                        elif data_time.count(0) == len(data_time):
                            Min = "-"
                            Max = "-"
                            Avg = "-"
                        else:
                            data_time = [i for i in data_time if i != 0]
                            Min = min(data_time)
                            Max = max(data_time)
                            Sum = int(sum(data_time))
                            Len = len(data_time)
                            Avg = round(Sum / Len, 2)

                        string_data = "Min=" + str(Min) + ",Max=" + str(Max) + ",Avg=" + str(Avg) + " (sec)"

                        if data["band"] == b and data["direction"] == d and data["file_size"] == size:
                            # print("download_upload_time_table - data:{data}".format(data=data))
                            list_data.append(string_data)

                table_dict_time[self.column_head[i]] = list_data
                i = i + 1
                self.kpi_results.append(list_data)

        return table_dict_time

    def generate_graph_time(self, result_data, x_axis, band, size):
        '''Method for generating graph for time'''

        num_stations = result_data[1]["num_stations"]
        dataset = []
        labels = []
        color = []
        graph_name = ""
        graph_description = ""
        count = 0
        handles = []
        for data in result_data.values():
            if data["band"] == band and data["file_size"] == size and data["direction"] == "Download":
                dataset.append(data["time"])
                labels.append("Download")

                # Adding red bar if client unable to download/upload file
                color_list = []
                # converting minutes in seconds
                duration = data["duration"] * 60
                for i in data["time"]:
                    if i < duration:
                        color_list.append("orange")
                    else:
                        color_list.append("red")
                if color_list.count("red") == 0:
                    handles.append(mpatches.Patch(color='orange', label='Download <= threshold time'))
                    num_col = 1
                    box = (1, 1.15)
                else:
                    handles.append(mpatches.Patch(color='orange', label='Download <= threshold time'))
                    handles.append(mpatches.Patch(color='red', label='Download > threshold time'))
                    num_col = 2
                    box = (1, 1.15)
                color.append(color_list)
                graph_name = "File size " + size + " " + str(
                    num_stations) + " Clients " + band + "-File Download Times(secs)"
                fail_count = len([i for i in data["time"] if i > (data["duration"] * 60)])
                graph_description = "Out of " + str(data["num_stations"]) + " clients, " + str(
                    data["num_stations"] - fail_count) + " are able to download " + "within " + str(
                    data["duration"]) + " min."
                count = count + 1
            if data["band"] == band and data["file_size"] == size and data["direction"] == "Upload":
                dataset.append(data["time"])
                labels.append("Upload")

                # Adding red bar if client unable to download/upload file
                color_list = []
                duration = data["duration"] * 60
                for i in data["time"]:
                    if i < duration:
                        color_list.append("blue")
                    else:
                        color_list.append("red")
                if color_list.count("red") == 0:
                    handles.append(mpatches.Patch(color='blue', label='Upload <= threshold time'))
                    num_col = 1
                    box = (1, 1.15)
                else:
                    handles.append(mpatches.Patch(color='blue', label='Upload <= threshold time'))
                    handles.append(mpatches.Patch(color='red', label='Upload < threshold time'))
                    num_col = 2
                    box = (1, 1.15)
                color.append(color_list)

                graph_name = "File size " + size + " " + str(
                    num_stations) + " Clients " + band + "-File Upload Times(secs)"
                fail_count = len([i for i in data["time"] if i > (data["duration"] * 60)])
                graph_description = graph_description + "Out of " + str(data["num_stations"]) + " clients, " + str(
                    data["num_stations"] - fail_count) + " are able to upload " + "within " + str(
                    data["duration"]) + " min."
                count = count + 1
        if count == 2:
            graph_name = "File size " + size + " " + str(
                num_stations) + " Clients " + band + "-File Download and Upload Times(secs)"
            handles = []
            for i in labels:
                if i == "Upload":
                    c = "blue"
                else:
                    c = "orange"
                handles.append(mpatches.Patch(color=c, label=i + " <= threshold time"))
            num_col = 2
            box = (1, 1.15)
            if (color[0].count("red") >= 1) or (color[1].count("red") >= 1):
                num_col = 3
                box = (1, 1.15)
                if labels[0] == "Download":
                    handles.append(mpatches.Patch(color='red', label='Download/Upload > threshold time'))
                else:
                    handles.append(mpatches.Patch(color='red', label='Upload/Download > threshold time'))

        self.report.set_obj_html(graph_name, graph_description)
        self.report.build_objective()
        image_name = "image" + band + size
        x_axis_name = "Stations"
        y_axis_name = "Time in seconds"
        self.bar_graph(x_axis, image_name, dataset, color, labels, x_axis_name, y_axis_name, handles, ncol=num_col, box=box, fontsize=12)

    def generate_graph_throughput(self, result_data, x_axis, band, size):
        '''Method for generating graph for time'''

        num_stations = result_data[1]["num_stations"]
        dataset = []
        labels = []
        color = []
        graph_name = ""
        graph_description = ""
        count = 0
        for data in result_data.values():
            if data["band"] == band and data["file_size"] == size and data["direction"] == "Download":
                dataset.append(data["throughput"])
                labels.append("Download")
                color.append("Orange")
                graph_name = "File size " + size + " " + str(
                    num_stations) + " Clients " + band + "-File Download Throughput(MB)"
                graph_description = str(data["num_stations"] - data["time"].count(0)) + \
                    " clients are able to download " + data["file_size"] + " file."
                count = count + 1
            if data["band"] == band and data["file_size"] == size and data["direction"] == "Upload":
                dataset.append(data["throughput"])
                labels.append("Upload")
                color.append("Blue")
                graph_name = "File size " + size + " " + str(
                    num_stations) + " Clients " + band + "-File Upload Throughput(MB)"
                graph_description = graph_description + str(data["num_stations"] - data["time"].count(0)) + \
                    " clients are able to upload " + data["file_size"] + " file."
                count = count + 1
        if count == 2:
            graph_name = "File size " + size + " " + str(
                num_stations) + " Clients " + band + "-File Download and Upload Throughput(MB)"

        self.report.set_obj_html(graph_name, graph_description)
        self.report.build_objective()
        image_name = "image" + band + size + "throughput"
        x_axis_name = "Stations"
        y_axis_name = "Throughput in MB"
        box = (1.1, 1.05)
        self.bar_graph(x_axis, image_name, dataset, color, labels, x_axis_name, y_axis_name, handles=None, ncol=1, box=box, fontsize=None)

    def bar_graph(self, x_axis, image_name, dataset, color, labels, x_axis_name, y_axis_name, handles, ncol, box, fontsize):
        '''This Method will plot bar graph'''

        graph = lf_graph.lf_bar_graph(_data_set=dataset,
                                      _xaxis_name=x_axis_name,
                                      _yaxis_name=y_axis_name,
                                      _xaxis_categories=x_axis,
                                      _label=labels,
                                      _graph_image_name=image_name,
                                      _figsize=(18, 6),
                                      _color=color,
                                      _show_bar_value=False,
                                      _xaxis_step=None,
                                      _legend_handles=handles,
                                      _color_edge=None,
                                      _text_rotation=40,
                                      _legend_loc="upper right",
                                      _legend_box=box,
                                      _legend_ncol=ncol,
                                      _legend_fontsize=fontsize,
                                      _enable_csv=True)

        graph_png = graph.build_bar_graph()

        logger.info("graph name {}".format(graph_png))

        self.report.set_graph_image(graph_png)
        # need to move the graph image to the results
        self.report.move_graph_image()
        self.report.set_csv_filename(graph_png)
        self.report.move_csv_file()

        self.report.build_graph()

    def generate_graph(self, result_data):
        '''This method will generate bar graph of time and throughput'''

        x_axis = []
        for i in range(1, self.num_stations + 1, 1):
            x_axis.append(i)

        for b in self.bands:
            for size in self.file_sizes:
                self.generate_graph_time(result_data, x_axis, b, size)
                # self.generate_graph_throughput(result_data, x_axis, b, size)

    def generate_report(self, ftp_data, date, input_setup_info, test_rig, test_tag, dut_hw_version,
                        dut_sw_version, dut_model_num, dut_serial_num, test_id, bands,
                        csv_outfile, local_lf_report_dir, _results_dir_name='ftp_test', report_path='', config_devices=""):
        no_of_stations = ""
        duration = ""
        x_fig_size = 18
        y_fig_size = len(self.real_client_list1) * .5 + 4
        if int(self.traffic_duration) < 60:
            duration = str(self.traffic_duration) + "s"
        elif int(self.traffic_duration == 60) or (int(self.traffic_duration) > 60 and int(self.traffic_duration) < 3600):
            duration = str(self.traffic_duration / 60) + "m"
        else:
            if int(self.traffic_duration == 3600) or (int(self.traffic_duration) > 3600):
                duration = str(self.traffic_duration / 3600) + "h"

        '''Method for generate the report'''
        # print(self.real_client_list,self.station_list,self.url_data,self.uc_avg,self.mac_id_list,self.channel_list,self.mode_list)
        client_list = []
        if self.clients_type == "Real":
            client_list = self.real_client_list1
            android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
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

            # Build total_devices string based on counts
            if android_devices > 0:
                total_devices += f" Android({android_devices})"
            if windows_devices > 0:
                total_devices += f" Windows({windows_devices})"
            if linux_devices > 0:
                total_devices += f" Linux({linux_devices})"
            if mac_devices > 0:
                total_devices += f" Mac({mac_devices})"
        else:
            if self.clients_type == "Virtual":
                client_list = self.station_list
        self.report = lf_report.lf_report(_results_dir_name="ftp_test", _output_html="ftp_test.html", _output_pdf="ftp_test.pdf", _path=report_path)
        if self.dowebgui == "True" and report_path == '':
            self.report = lf_report.lf_report(_results_dir_name="ftp_test", _output_html="ftp_test.html",
                                              _output_pdf="ftp_test.pdf", _path=self.result_dir)
        else:
            self.report = lf_report.lf_report(_results_dir_name="ftp_test", _output_html="ftp_test.html",
                                              _output_pdf="ftp_test.pdf", _path=report_path)

        # To move ftp_datavalues.csv in report folder
        report_path_date_time = self.report.get_path_date_time()
        if self.clients_type == "Real":
            shutil.move('ftp_datavalues.csv', report_path_date_time)
            for csv_name in self.individual_device_csv_names:
                shutil.move(f"{csv_name}.csv", report_path_date_time)
        self.report.set_title("FTP Test")
        self.report.set_date(date)
        self.report.build_banner()
        self.report.set_table_title("Test Setup Information")
        self.report.build_table_title()

        if self.clients_type == "Virtual":
            no_of_stations = str(len(self.station_list))
        else:
            no_of_stations = str(len(self.input_devices_list))

        if self.clients_type == "Real":
            # Test setup information table for devices in device list
            if config_devices == "":
                test_setup_info = {
                    "AP Name": self.ap_name,
                    "SSID": self.ssid,
                    "Security": self.security,
                    "Device List": ", ".join(all_devices_names),
                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                    "File size": self.file_size,
                    "File location": "/home/lanforge",
                    "Traffic Direction": self.direction,
                    "Traffic Duration ": duration
                }
            # Test setup information table for devices in groups
            else:
                group_names = ', '.join(config_devices.keys())
                profile_names = ', '.join(config_devices.values())
                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                test_setup_info = {
                    "AP Name": self.ap_name,
                    'Configuration': configmap,
                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                    "File size": self.file_size,
                    "File location": "/home/lanforge",
                    "Traffic Direction": self.direction,
                    "Traffic Duration ": duration
                }
        else:
            test_setup_info = {
                "AP Name": self.ap_name,
                "SSID": self.ssid,
                "Security": self.security,
                "No of Devices": no_of_stations,
                "File size": self.file_size,
                "File location": "/home/lanforge",
                "Traffic Direction": self.direction,
                "Traffic Duration ": duration
            }
        self.report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        self.report.set_obj_html("Objective",
                                 "This FTP Test is used to Verify that N clients connected on Specified band and can "
                                 "simultaneously download some amount of file from FTP server and measuring the "
                                 "time taken by client to Download the file.")
        self.report.build_objective()
        # self.report.set_obj_html("PASS/FAIL Results",
        #                          "This Table will give Pass/Fail results.")
        # self.report.build_objective()
        # dataframe1 = pd.DataFrame(self.add_pass_fail_table(ftp_data))
        # self.report.set_table_dataframe(dataframe1)
        # self.report.build_table()
        # self.report.set_obj_html("File Download/Upload Time (sec)",
        #                          "This Table will  give FTP Download/Upload Time of Clients.")
        # self.report.build_objective()
        # dataframe2 = pd.DataFrame(self.download_upload_time_table(ftp_data))
        # self.report.set_table_dataframe(dataframe2)
        # self.report.build_table()
        # self.generate_graph(ftp_data)
        self.report.set_obj_html(
            _obj_title=f"No of times file {self.direction}",
            _obj=f"The below graph represents number of times a file {self.direction} for each client"
            f"(WiFi) traffic.  X- axis shows “No of times file {self.direction}” and Y-axis shows "
            f"Client names.")

        self.report.build_objective()
        graph = lf_bar_graph_horizontal(_data_set=[self.url_data], _xaxis_name=f"No of times file {self.direction}",
                                        _yaxis_name="Client names",
                                        _yaxis_categories=[i for i in client_list],
                                        _yaxis_label=[i for i in client_list],
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _yticks_rotation=None,
                                        _graph_title=f"No of times file {self.direction} (Count)",
                                        _title_size=16,
                                        _figsize=(x_fig_size, y_fig_size),
                                        _legend_loc="best",
                                        _legend_box=(1.0, 1.0),
                                        _color_name=['orange'],
                                        _show_bar_value=True,
                                        _enable_csv=True,
                                        _graph_image_name="Total-url_ftp", _color_edge=['black'],
                                        _color=['orange'],
                                        _label=[self.direction])
        graph_png = graph.build_bar_graph_horizontal()
        print("graph name {}".format(graph_png))
        self.report.set_graph_image(graph_png)
        # need to move the graph image to the results
        self.report.move_graph_image()
        self.report.set_csv_filename(graph_png)
        self.report.move_csv_file()
        self.report.build_graph()
        self.report.set_obj_html(
            _obj_title=f"Average time taken to {self.direction} file ",
            _obj=f"The below graph represents average time taken to {self.direction} for each client  "
            f"(WiFi) traffic.  X- axis shows “Average time taken to {self.direction} a file ” and Y-axis shows "
            f"Client names.")

        self.report.build_objective()
        graph = lf_bar_graph_horizontal(_data_set=[self.uc_avg], _xaxis_name=f"Average time taken to {self.direction} file in ms",
                                        _yaxis_name="Client names",
                                        _yaxis_categories=[i for i in client_list],
                                        _yaxis_label=[i for i in client_list],
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _yticks_rotation=None,
                                        _graph_title=f"Average time taken to {self.direction} file",
                                        _title_size=16,
                                        _figsize=(x_fig_size, y_fig_size),
                                        _legend_loc="best",
                                        _legend_box=(1.0, 1.0),
                                        _color_name=['steelblue'],
                                        _show_bar_value=True,
                                        _enable_csv=True,
                                        _graph_image_name="ucg-avg_ftp", _color_edge=['black'],
                                        _color=['steelblue'],
                                        _label=[self.direction])
        graph_png = graph.build_bar_graph_horizontal()
        print("graph name {}".format(graph_png))
        self.report.set_graph_image(graph_png)
        self.report.move_graph_image()
        # need to move the graph image to the results
        self.report.set_csv_filename(graph_png)
        self.report.move_csv_file()
        self.report.build_graph()
        self.report.set_obj_html("File Download Time (sec)", "The below table will provide information of "
                                 "minimum, maximum and the average time taken by clients to download a file in seconds")
        self.report.build_objective()
        dataframe2 = {
            "Minimum": [str(round(min(self.uc_min) / 1000, 1))],
            "Maximum": [str(round(max(self.uc_max) / 1000, 1))],
            "Average": [str(round((sum(self.uc_avg) / len(client_list)) / 1000, 1))]
        }
        dataframe3 = pd.DataFrame(dataframe2)
        self.report.set_table_dataframe(dataframe3)
        self.report.build_table()
        self.report.set_table_title("Overall Results")
        self.report.build_table_title()
        # self.report.test_setup_table(value="Information", test_setup_data=input_setup_info)
        if self.clients_type == 'Real':
            # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
            if self.expected_passfail_val or self.csv_name:
                self.get_pass_fail_list(client_list)
            # When groups are provided a seperate table will be generated for each group using generate_dataframe
            if self.group_name:
                for key, val in self.group_device_map.items():
                    if self.expected_passfail_val or self.csv_name:
                        dataframe = self.generate_dataframe(val, client_list, self.mac_id_list, self.channel_list, self.ssid_list, self.mode_list,
                                                            self.url_data, self.test_input_list, self.uc_avg, self.bytes_rd, self.rx_rate, self.pass_fail_list)
                    else:
                        dataframe = self.generate_dataframe(val, client_list, self.mac_id_list, self.channel_list, self.ssid_list,
                                                            self.mode_list, self.url_data, [], self.uc_avg, self.bytes_rd, self.rx_rate, [])

                    if dataframe:
                        self.report.set_obj_html("", "Group: {}".format(key))
                        self.report.build_objective()
                        dataframe1 = pd.DataFrame(dataframe)
                        self.report.set_table_dataframe(dataframe1)
                        self.report.build_table()
            else:
                dataframe = {
                    " Clients": client_list,
                    " MAC ": self.mac_id_list,
                    " Channel": self.channel_list,
                    " SSID ": self.ssid_list,
                    " Mode": self.mode_list,
                    " No of times File downloaded ": self.url_data,
                    " Time Taken to Download file (ms)": self.uc_avg,
                    " Bytes-rd (Mega Bytes)": self.bytes_rd,
                    " RX RATE (Mbps) ": self.rx_rate
                }
                if self.expected_passfail_val or self.csv_name:
                    dataframe[" Expected output "] = self.test_input_list
                    dataframe[" Status "] = self.pass_fail_list

                dataframe1 = pd.DataFrame(dataframe)
                self.report.set_table_dataframe(dataframe1)
                self.report.build_table()

        else:
            dataframe = {
                " Clients": client_list,
                " MAC ": self.mac_id_list,
                " Channel": self.channel_list,
                " SSID ": self.ssid_list,
                " Mode": self.mode_list,
                " No of times File downloaded ": self.url_data,
                " Time Taken to Download file (ms)": self.uc_avg,
                " Bytes-rd (Mega Bytes)": self.bytes_rd,
            }
            dataframe1 = pd.DataFrame(dataframe)
            self.report.set_table_dataframe(dataframe1)
            self.report.build_table()
        self.report.build_footer()
        html_file = self.report.write_html()
        logger.info("returned file {}".format(html_file))
        logger.info(html_file)
        self.report.write_pdf()

        # The following lines can be used when the kpi results are needed
        # self.kpi_results
        # print("generate_report - self.kpi_results:{kpi_results}".format(kpi_results=self.kpi_results))

        # # Begin kpi.csv
        # # start splicing data from self.kpi_results to feed table dicts
        # for dwnld_rts in self.kpi_results[0]:
        #     split_download_rates = dwnld_rts.split(',')

        #     # split download data rates for download_table_values dict
        #     x_fin = []
        #     y_fin = []
        #     z_fin = []

        #     x = split_download_rates[0]
        #     y = split_download_rates[1]
        #     z = split_download_rates[2]

        #     split_min = x.split('=')
        #     split_max = y.split('=')
        #     split_avg = z.split('=')

        #     x1 = split_min[1]
        #     y1 = split_max[1]
        #     z1 = split_avg[1]
        #     z2 = z1.split()
        #     z3 = z2[0]

        #     x_fin.append(x1)
        #     y_fin.append(y1)
        #     z_fin.append(z3)

        #     download_table_value = {
        #         "Band": bands,
        #         "Minimum": x_fin,
        #         "Maximum": y_fin,
        #         "Average": z_fin
        #     }
        #     # print("download_table_value:{download_table_value}".format(download_table_value=download_table_value))

        # # if upload tests are being ran as well:
        # if len(self.kpi_results) > 0:
        #     for upload_rts in self.kpi_results[0]:
        #         split_upload_rates = upload_rts.split(',')
        #         # print("split_upload_rates:{split_upload_rates}".format(split_upload_rates=split_upload_rates))
        #         # split upload data rates for upload_table_values dict

        #         up_x_fin = []
        #         up_y_fin = []
        #         up_z_fin = []

        #         up_x = split_upload_rates[0]
        #         up_y = split_upload_rates[1]
        #         up_z = split_upload_rates[2]

        #         up_split_min = up_x.split('=')
        #         up_split_max = up_y.split('=')
        #         up_split_avg = up_z.split('=')

        #         up_x1 = up_split_min[1]
        #         up_y1 = up_split_max[1]
        #         up_z1 = up_split_avg[1]
        #         up_z2 = up_z1.split()
        #         up_z3 = up_z2[0]

        #         up_x_fin.append(up_x1)
        #         up_y_fin.append(up_y1)
        #         up_z_fin.append(up_z3)

        #         upload_table_value = {
        #             "Band": bands,
        #             "Minimum": up_x_fin,
        #             "Maximum": up_y_fin,
        #             "Average": up_z_fin
        #         }
        #         print("upload_table_value:{upload_table_value}".format(upload_table_value=upload_table_value))

        # if local_lf_report_dir != "":
        #     report = lf_report.lf_report(
        #         _path=local_lf_report_dir,
        #         _results_dir_name="lf_ftp",
        #         _output_html="lf_ftp.html",
        #         _output_pdf="lf_ftp.pdf")
        # else:
        #     report = lf_report.lf_report(
        #         _results_dir_name="lf_ftp",
        #         _output_html="lf_ftp.html",
        #         _output_pdf="lf_ftp.pdf")

        # Get the report path to create the kpi.csv path
        # kpi_path = report.get_report_path()
        # print("kpi_path :{kpi_path}".format(kpi_path=kpi_path))

        # self.kpi_csv = lf_kpi_csv.lf_kpi_csv(
        #     _kpi_path=kpi_path,
        #     _kpi_test_rig=test_rig,
        #     _kpi_test_tag=test_tag,
        #     _kpi_dut_hw_version=dut_hw_version,
        #     _kpi_dut_sw_version=dut_sw_version,
        #     _kpi_dut_model_num=dut_model_num,
        #     _kpi_dut_serial_num=dut_serial_num,
        #     _kpi_test_id=test_id)

        # self.kpi_csv.kpi_dict['Units'] = "Mbps"
        # for band in range(len(download_table_value["Band"])):
        #     self.kpi_csv.kpi_csv_get_dict_update_time()

        #     # ftp download data for kpi.csv
        #     self.kpi_csv.kpi_dict['Graph-Group'] = "FTP Download {band}".format(
        #         band=download_table_value['Band'][band])
        #     self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Minimum".format(
        #         band=download_table_value['Band'][band])
        #     self.kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=download_table_value['Minimum'][band])
        #     self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #     self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Maximum".format(
        #         band=download_table_value['Band'][band])
        #     self.kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=download_table_value['Maximum'][band])
        #     self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #     self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Average".format(
        #         band=download_table_value['Band'][band])
        #     self.kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=download_table_value['Average'][band])
        #     self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)

        #     if 'Upload' in self.directions:
        #         for band in range(len(upload_table_value["Band"])):
        #     # ftp upload data for kpi.csv
        #             self.kpi_csv.kpi_dict['Graph-Group'] = "FTP Upload {band}".format(
        #                 band=upload_table_value['Band'][band])
        #             self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Minimum".format(
        #                 band=upload_table_value['Band'][band])
        #             print("self.kpi_csv.kpi_dict['numeric-score']",self.kpi_csv.kpi_dict['numeric-score'])
        #             self.kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=upload_table_value['Minimum'][band])
        #             self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #             self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Maximum".format(
        #                 band=upload_table_value['Band'][band])
        #             print(self.kpi_csv.kpi_dict['numeric-score'])
        #             self.kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=upload_table_value['Maximum'][band])
        #             self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #             self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Average".format(
        #                 band=upload_table_value['Band'][band])
        #             self.kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=upload_table_value['Average'][band])
        #             self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)

        #     '''
        #     # ftp download data for kpi.csv
        #     if self.direction == "Download":
        #         self.kpi_csv.kpi_dict['Graph-Group'] = "FTP Download {band}".format(
        #             band=download_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Minimum".format(
        #             band=download_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=download_table_value['Minimum'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Maximum".format(
        #             band=download_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=download_table_value['Maximum'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Download {band} Average".format(
        #             band=download_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=download_table_value['Average'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)

        #     # ftp upload data for kpi.csv
        #     if self.direction == "Upload":
        #         self.kpi_csv.kpi_dict['Graph-Group'] = "FTP Upload {band}".format(
        #             band=upload_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Minimum".format(
        #             band=upload_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=upload_table_value['Minimum'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Maximum".format(
        #             band=upload_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=upload_table_value['Maximum'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #         self.kpi_csv.kpi_dict['short-description'] = "FTP Upload {band} Average".format(
        #             band=upload_table_value['Band'][band])
        #         self.kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=upload_table_value['Average'][band])
        #         self.kpi_csv.kpi_csv_write_dict(self.kpi_csv.kpi_dict)
        #     '''

        if csv_outfile is not None:
            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            csv_outfile = "{}_{}-test_l4_ftp.csv".format(
                csv_outfile, current_time)
            csv_outfile = self.report.file_add_path(csv_outfile)
            logger.info("csv output file : {}".format(csv_outfile))

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
        # in webgui-reports DIR creating a directory with test_name
        if not os.path.exists(test_name_dir):
            os.makedirs(test_name_dir)
        shutil.copytree(curr_path, test_name_dir, dirs_exist_ok=True)

    # Calculates pass/fail status for each client based on their result compared to the expected value.
    def get_pass_fail_list(self, client_list):
        # When csv_name is provided, for pass/fail criteria, respective values for each client will be used
        if self.expected_passfail_val == '' or self.expected_passfail_val is None:
            res_list = []
            test_input_list = []
            pass_fail_list = []
            for client in client_list:
                # Check if the client type (second word in "1.15 android samsungmob") is 'android'
                if client.split(' ')[1] != 'android':
                    res_list.append(client.split(' ')[2])
                else:
                    interop_tab_data = self.json_get('/adb/')["devices"]
                    for dev in interop_tab_data:
                        for item in dev.values():
                            # Extract the username from the client string (e.g., 'samsungmob' from "1.15 android samsungmob")
                            if item['user-name'] == client.split(' ')[2]:
                                res_list.append(item['name'].split('.')[2])

            with open(self.csv_name, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            for device in res_list:
                found = False
                for row in rows:
                    if row['DeviceList'] == device and row['FTP URLcount'].strip() != '':
                        test_input_list.append(row['FTP URLcount'])
                        found = True
                        break
                # appending default value when not found in csv
                if not found:
                    logging.info(f"Pass/fail status for device {device} not found in CSV. Using default FTP URL count = 5")
                    test_input_list.append(5)
            for i in range(len(test_input_list)):
                if float(test_input_list[i]) <= self.url_data[i]:
                    pass_fail_list.append('PASS')
                else:
                    pass_fail_list.append('FAIL')
            self.pass_fail_list = pass_fail_list
            self.test_input_list = test_input_list
        # When expected_passfail_val is provided, for pass/fail criteria, the same value will be used for all clients
        else:
            self.test_input_list = [self.expected_passfail_val for val in range(len(client_list))]
            pass_fail_list = []
            for i in range(len(self.test_input_list)):
                if int(self.expected_passfail_val) <= self.url_data[i]:
                    pass_fail_list.append("PASS")
                else:
                    pass_fail_list.append("FAIL")
            self.pass_fail_list = pass_fail_list

    def generate_dataframe(self, groupdevlist: List[str], clients_list: List[str], mac: List[str], channel: List[str], ssid: List[str], mode: List[str], file_download: List[int],
                           test_input: List[int], averagetime: List[float], bytes_read: List[float], rx_rate: List[float], status: List[str]) -> Optional[pd.DataFrame]:
        """
        Creates a separate DataFrame for each group of devices.

        Returns:
            DataFrame: A DataFrame for each device group.
            Returns None if neither device in a group is configured.
        """
        clients = []
        macids = []
        channels = []
        ssids = []
        modes = []
        downloadtimes = []
        input_list = []
        avgtimes = []
        readbytes = []
        statuslist = []
        rate_rx = []
        interop_tab_data = self.json_get('/adb/')["devices"]
        for i in range(len(clients_list)):
            for j in groupdevlist:
                # For a string like "1.360 Lin test3":
                # - clients_list[i].split(" ")[2] gives 'test3' (device name)
                # - clients_list[i].split(" ")[1] gives 'Lin' (OS type)
                # This condition filters out Android clients and matches device name with j
                if j == clients_list[i].split(" ")[2] and clients_list[i].split(" ")[1] != 'android':
                    clients.append(clients_list[i])
                    macids.append(mac[i])
                    channels.append(channel[i])
                    ssids.append(ssid[i])
                    modes.append(mode[i])
                    downloadtimes.append(file_download[i])
                    avgtimes.append(averagetime[i])
                    readbytes.append(bytes_read[i])
                    rate_rx.append(rx_rate[i])
                    if self.expected_passfail_val or self.csv_name:
                        input_list.append(test_input[i])
                        statuslist.append(status[i])

                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            # For a string like 1.15 android samsungmob:
                            # - clients_list[i].split(' ')[2] (e.g., 'samsungmob') matches item['user-name']
                            # - The group name (e.g., 'RZCTA09CTXF') matches with item['name'].split('.')[2]
                            if item['user-name'] == clients_list[i].split(' ')[2] and j == item['name'].split('.')[2]:
                                clients.append(clients_list[i])
                                macids.append(mac[i])
                                channels.append(channel[i])
                                ssids.append(ssid[i])
                                modes.append(mode[i])
                                downloadtimes.append(file_download[i])
                                avgtimes.append(averagetime[i])
                                readbytes.append(bytes_read[i])
                                rate_rx.append(rx_rate[i])
                                if self.expected_passfail_val or self.csv_name:
                                    input_list.append(test_input[i])
                                    statuslist.append(status[i])
        if len(clients) != 0:
            dataframe = {
                " Clients": clients,
                " MAC ": macids,
                " Channel": channels,
                " SSID ": ssids,
                " Mode": modes,
                " No of times File downloaded ": downloadtimes,
                " Average time taken to Download file (ms)": avgtimes,
                " Bytes-rd (Mega Bytes) ": readbytes,
                " RX RATE (Mbps) ": rate_rx
            }
            if self.expected_passfail_val or self.csv_name:
                dataframe[" Expected value of no of times file downloaded"] = input_list
                dataframe[' Status '] = statuslist

            return dataframe
        else:
            return None


def validate_args(args):
    """Validate CLI arguments."""
    # Get group and profile values from arguments and convert comma-separated strings into lists
    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []  # Default to empty list if group name is not provided
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []  # Default to empty list if profile name is not provided

    if args.device_csv_name and args.expected_passfail_value:
        logger.error("Enter either --device_csv_name or --expected_passfail_value")
        exit(1)
    if args.clients_type == 'Real' and args.config and args.group_name is None:
        if args.ssid and args.security and args.security.lower() == 'open' and (args.passwd is None or args.passwd == ''):
            args.passwd = '[BLANK]'
        if args.ssid is None:
            logger.error('Specify SSID for confiuration, Password(Optional for "open" type security) , Security')
            exit(1)
        elif args.ssid and args.passwd:
            if args.security is None:
                logger.error('Security must be provided when SSID and Password specified')
                exit(1)
            elif args.security.lower() == 'open' and args.passwd != '[BLANK]':
                logger.error("For a open type security there will be no password or the password should be left blank (i.e., set to '' or [BLANK]).")
                exit(1)
        elif args.ssid and args.passwd == '[BLANK]' and args.security and args.security.lower() != 'open':
            logger.error('Please provide valid passwd and security configuration')
            exit(1)
    if args.group_name and (args.file_name is None or args.profile_name is None):
        logger.error("Please provide file name and profile name for group configuration")
        exit(1)
    elif args.file_name and (args.group_name is None or args.profile_name is None):
        logger.error("Please provide group name and profile name for file configuration")
        exit(1)
    elif args.profile_name and (args.group_name is None or args.file_name is None):
        logger.error("Please provide group name and file name for profile configuration")
        exit(1)
    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)
    elif args.group_name and args.profile_name and args.file_name and args.device_list != []:
        logger.error("Either group name or device list should be entered, not both")
        exit(1)
    elif args.ssid and args.profile_name:
        logger.error("Either SSID or profile name should be given")
        exit(1)
    elif args.config and args.group_name is None and ((args.ssid is None or (args.passwd is None and args.security != 'open') or (args.passwd is None and args.security is None))):
        logger.error("Please provide SSID, password, and security for configuration of devices")
        exit(1)
    elif args.config and args.device_list != [] and (args.ssid is None or args.passwd is None or args.security is None):
        logger.error("Please provide SSID, password, and security when device list is given")
        exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='lf_ftp.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description='''\
---------------------------

NAME: lf_ftp.py

PURPOSE:
lf_ftp.py will verify that N clients are connected on a specified band and can simultaneously download/upload
some amount of file data from the FTP server while measuring the time taken by clients to download/upload the file.

EXAMPLE-1:
Command Line Interface to run download scenario for Real clients
python3 lf_ftp.py --ssid Netgear-5g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --directions Download --clients_type Real --ap_name Netgear --bands 5G --upstream_port eth1

EXAMPLE-2:
Command Line Interface to run upload scenario on 6GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-6g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa3 --fiveg_radio wiphy2 --directions Upload --clients_type Virtual --ap_name Netgear --bands 6G --num_stations 2
--upstream_port eth1

EXAMPLE-3:
Command Line Interface to run download scenario on 5GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-5g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --fiveg_radio wiphy2 --directions Download --clients_type Virtual --ap_name Netgear --bands 5G --num_stations 2
--upstream_port eth1

EXAMPLE-4:
Command Line Interface to run upload scenario for Real clients
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --directions Download --clients_type Real --ap_name Netgear --bands 2.4G --upstream_port eth1

EXAMPLE-5:
Command Line Interface to run upload scenario on 2.4GHz band for Virtual clients
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.200.165 --traffic_duration 1m
--security wpa2 --twog_radio wiphy1 --directions Upload --clients_type Virtual --ap_name Netgear --bands 2.4G --num_stations 2
--upstream_port eth1

EXAMPLE-6:
Command Line Interface to run download scenario for Real clients with device list
python3 lf_ftp.py --ssid Netgear-2g --passwd sharedsecret --file_sizes 10MB --mgr 192.168.214.219 --traffic_duration 1m --security wpa2
--directions Download --clients_type Real --ap_name Netgear --bands 2.4G --upstream_port eth1 --device_list 1.12,1.22

EXAMPLE-7:
Command Line Interface to run download scenario by setting the same expected Pass/Fail value for all devices
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --expected_passfail_value 4

EXAMPLE-8:
Command Line Interface to run download scenario by setting device specific Pass/Fail values in the csv file
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.204.74 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --device_csv_name device.csv

EXAMPLE-9:
Command Line Interface to run download scenario by Configuring Real Devices with SSID, Password, and Security
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_5G --passwd Password@123 --security wpa2 --config

EXAMPLE-10:
Command Line Interface to run download scenario by setting the same expected Pass/Fail value for all devices with configuration
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_2G --passwd Password@123 --security wpa2 --expected_passfail_value 4 --config

EXAMPLE-11:
Command Line Interface to run download scenario by setting device specific Pass/Fail values in the csv file without configuration
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --ssid NETGEAR_2G --passwd Password@123 --security wpa2 --device_csv_name device.csv

EXAMPLE-12:
Command Line Interface to run download scenario by Configuring Devices in Groups with Specific Profiles
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218  --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --file_name g219 --group_name grp1 --profile_name Open3

EXAMPLE-13:
Command Line Interface to run download scenario by Configuring Devices in Groups with Specific Profiles and expected Pass/Fail values
python3 lf_ftp.py --file_sizes 1MB --mgr 192.168.213.218 --traffic_duration 1m  --directions Download --clients_type Real  --bands 5G
 --upstream_port eth1 --file_name g219 --group_name grp1 --profile_name Open3 --expected_passfail_value 3 --wait_time 30

SCRIPT_CLASSIFICATION : Test

SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

NOTES:
After passing cli, a list will be displayed on terminal which contains available resources to run test.
The following sentence will be displayed
Enter the desired resources to run the test:
Please enter the port numbers seperated by commas ','.
Example:
Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

STATUS : Functional

VERIFIED_ON:
26-JULY-2024,
GUI Version:  5.4.8
Kernel Version: 6.2.16+

LICENSE :
Copyright 2023 Candela Technologies Inc
Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README: False

                    ''')
    required = parser.add_argument_group('Required arguments to run lf_ftp.py')
    optional = parser.add_argument_group('Optional arguments to run lf_ftp.py')

    required.add_argument('--mgr', help='hostname for where LANforge GUI is running [default = localhost]', default='localhost')
    required.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on [default = 8080]', default=8080)
    optional.add_argument('--local_lf_report_dir', help='--local_lf_report_dir override the report path, primary use when running test in test suite', default="")
    required.add_argument('--upstream_port', help='non-station port that generates traffic: eg: eth1 [default = eth1]', default='eth1')
    required.add_argument('--ssid', type=str, help='Enter ssid')
    required.add_argument('--passwd', type=str, help='Enter password for ssid provided')
    required.add_argument('--security', type=str, help='Enter the security')
    required.add_argument('--group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    required.add_argument('--profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    required.add_argument('--file_name', type=str, help='Specify the file name containing group details. Example:file1')
    required.add_argument('--ap_name', type=str, help='Enter the Access point or router name')
    optional.add_argument('--ap_ip', type=str, help='Enter ip of accesspoint or router')
    optional.add_argument('--twog_radio', type=str, help='specify radio for 2.4G clients [default = wiphy1]', default='wiphy1')
    optional.add_argument('--fiveg_radio', type=str, help='specify radio for 5G client [default = wiphy0]', default='wiphy0')
    optional.add_argument('--sixg_radio', type=str, help='specify radio for 6G clients [default = wiphy2]', default='wiphy2')
    optional.add_argument('--lf_username', help="Enter the lanforge user name. Example : 'lanforge' ", default="lanforge")
    optional.add_argument('--lf_password', help="Enter the lanforge password. Example : 'lanforge' ", default="lanforge")
    # parser.add_argument('--twog_duration', nargs="+", help='Pass and Fail duration for 2.4G band in minutes')
    # parser.add_argument('--fiveg_duration', nargs="+", help='Pass and Fail duration for 5G band in minutes')
    # parser.add_argument('--both_duration', nargs="+", help='Pass and Fail duration for Both band in minutes')
    required.add_argument('--traffic_duration', help='duration for layer 4 traffic running in minutes or seconds or hours. Example : 30s,3m,48h')
    required.add_argument('--clients_type', help='Enter the type of clients on which the test is to be run. Example: "Virtual","Real"')
    # webGUI ARGS
    required.add_argument('--dowebgui', help="If true will execute script for webgui", default=False)
    # allow for test run as seconds, minutes, etc
    # TODO: add --debug support
    optional.add_argument('--ssh_port', type=int, help="specify the shh port: eg 22 [default = 22]", default=22)

    # Test variables
    optional.add_argument('--bands', nargs="+", help='select bands for virtul clients Example : "5G","2.4G","6G" ',
                          default=["5G", "2.4G", "6G" "Both"])
    required.add_argument('--directions', nargs="+", help='Enter the traffic direction. Example : "Download","Upload"',
                          default=["Download", "Upload"])
    required.add_argument('--file_sizes', nargs="+", help='File Size Example : "1000MB"',
                          default=["2MB", "500MB", "1000MB"])
    optional.add_argument('--num_stations', type=int, help='number of virtual stations', default=0)
    # parser.add_argument('--num_stations_real', type=int, help='--num_stations_real is number of stations', default=0)
    optional.add_argument('--result_dir', help='Specify the result dir to store the runtime logs', default='')
    optional.add_argument('--device_list', help='Enter the devices on which the test should be run', default=[])
    optional.add_argument('--test_name', help='Specify test name to store the runtime csv results', default=None)
    optional.add_argument('--expected_passfail_value', help='Enter the expected number of urls ', default=None)
    optional.add_argument('--device_csv_name', type=str, help='Enter the csv name to store expected url values', default=None)
    optional.add_argument('--wait_time', type=int, help='Enter the maximum wait time for configurations to apply', default=60)
    optional.add_argument('--config', action="store_true", help='Specify for configuring the devices')
    # kpi_csv arguments
    optional.add_argument(
        "--test_rig",
        default="",
        help="test rig for kpi.csv, testbed that the tests are run on")
    optional.add_argument(
        "--test_tag",
        default="",
        help="test tag for kpi.csv,  test specific information to differenciate the test")
    optional.add_argument(
        "--dut_hw_version",
        default="",
        help="dut hw version for kpi.csv, hardware version of the device under test")
    optional.add_argument(
        "--dut_sw_version",
        default="",
        help="dut sw version for kpi.csv, software version of the device under test")
    optional.add_argument(
        "--dut_model_num",
        default="",
        help="dut model for kpi.csv,  model number / name of the device under test")
    optional.add_argument(
        "--dut_serial_num",
        default="",
        help="dut serial for kpi.csv, serial number / serial number of the device under test")
    optional.add_argument(
        "--test_priority",
        default="",
        help="dut model for kpi.csv,  test-priority is arbitrary number")
    optional.add_argument(
        "--test_id",
        default="FTP Data",
        help="test-id for kpi.csv,  script or test name")
    optional.add_argument(
        '--csv_outfile',
        help="--csv_outfile <Output file for csv data>",
        default="")
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

    # logging configuration
    optional.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")

    # help summary
    optional.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')

    args = parser.parse_args()

    help_summary = '''\
lf_ftp.py will verify that N clients are connected on a specified band and can simultaneously download/upload
some amount of file data from the FTP server while measuring the time taken by clients to download/upload the file.
'''
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    # 1st time stamp for test duration
    time_stamp1 = datetime.now()

    # use for creating ftp_test dictionary
    interation_num = 0

    # empty dictionary for whole test data
    ftp_data = {}

    def pass_fail_duration(band, file_size):
        '''Method for set duration according file size and band which are given by user'''

        if band == "2.4G":
            if len(args.file_sizes) is not len(args.twog_duration):
                raise Exception("Give proper Pass or Fail duration for 2.4G band")

            for size in args.file_sizes:
                if size == file_size:
                    index = list(args.file_sizes).index(size)
                    duration = args.twog_duration[index]
        elif band == "5G":
            if len(args.file_sizes) is not len(args.fiveg_duration):
                raise Exception("Give proper Pass or Fail duration for 5G band")
            for size in args.file_sizes:
                if size == file_size:
                    index = list(args.file_sizes).index(size)
                    duration = args.fiveg_duration[index]
        else:
            if len(args.file_sizes) is not len(args.both_duration):
                raise Exception("Give proper Pass or Fail duration for 5G band")
            for size in args.file_sizes:
                if size == file_size:
                    index = list(args.file_sizes).index(size)
                    duration = args.both_duration[index]
        if duration.isdigit():
            duration = int(duration)
        else:
            duration = float(duration)

        return duration

    validate_args(args)
    if args.traffic_duration.endswith('s') or args.traffic_duration.endswith('S'):
        args.traffic_duration = int(args.traffic_duration[0:-1])
    elif args.traffic_duration.endswith('m') or args.traffic_duration.endswith('M'):
        args.traffic_duration = int(args.traffic_duration[0:-1]) * 60
    elif args.traffic_duration.endswith('h') or args.traffic_duration.endswith('H'):
        args.traffic_duration = int(args.traffic_duration[0:-1]) * 60 * 60
    elif args.traffic_duration.endswith(''):
        args.traffic_duration = int(args.traffic_duration)

    # For all combinations ftp_data of directions, file size and client counts, run the test
    for band in args.bands:
        for direction in args.directions:
            for file_size in args.file_sizes:
                # Start Test
                obj = FtpTest(lfclient_host=args.mgr,
                              lfclient_port=args.mgr_port,
                              result_dir=args.result_dir,
                              upstream=args.upstream_port,
                              dut_ssid=args.ssid,
                              group_name=args.group_name,
                              profile_name=args.profile_name,
                              file_name=args.file_name,
                              dut_passwd=args.passwd,
                              dut_security=args.security,
                              num_sta=args.num_stations,
                              band=band,
                              ap_name=args.ap_name,
                              file_size=file_size,
                              direction=direction,
                              twog_radio=args.twog_radio,
                              fiveg_radio=args.fiveg_radio,
                              sixg_radio=args.sixg_radio,
                              lf_username=args.lf_username,
                              lf_password=args.lf_password,
                              # duration=pass_fail_duration(band, file_size),
                              traffic_duration=args.traffic_duration,
                              ssh_port=args.ssh_port,
                              clients_type=args.clients_type,
                              dowebgui=args.dowebgui,
                              device_list=args.device_list,
                              test_name=args.test_name,
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
                              expected_passfail_val=args.expected_passfail_value,
                              csv_name=args.device_csv_name,
                              wait_time=args.wait_time,
                              config=args.config
                              )

                interation_num = interation_num + 1
                obj.file_create()
                if args.clients_type == "Real":
                    if not isinstance(args.device_list, list):
                        obj.device_list = obj.filter_iOS_devices(args.device_list)
                        if len(obj.device_list) == 0:
                            logger.info("There are no devices available")
                            exit(1)
                    configured_device, configuration = obj.query_realclients()

                if args.dowebgui and args.group_name:
                    # If no devices are configured,update the Web UI with "Stopped" status
                    if len(configured_device) == 0:
                        logger.warning("No device is available to run the test")
                        obj1 = {
                            "status": "Stopped",
                            "configuration_status": "configured"
                        }
                        obj.updating_webui_runningjson(obj1)
                        return
                    # If devices are configured, update the Web UI with the list of configured devices
                    else:
                        obj1 = {
                            "configured_devices": configured_device,
                            "configuration_status": "configured"
                        }
                        obj.updating_webui_runningjson(obj1)
                obj.set_values()
                obj.precleanup()
                obj.build()
                if not obj.passes():
                    logger.info(obj.get_fail_message())
                    exit(1)

                # First time stamp
                time1 = datetime.now()
                logger.info("Traffic started running at %s", time1)
                obj.start(False, False)
                # to fetch runtime values during the execution and fill the csv.
                if args.dowebgui or args.clients_type == "Real":
                    obj.monitor_for_runtime_csv()
                    obj.my_monitor_for_real_devices()
                else:
                    time.sleep(args.traffic_duration)
                    obj.my_monitor()

                # # return list of download/upload completed time stamp
                # time_list = obj.my_monitor(time1)
                # # print("pass_fail_duration - time_list:{time_list}".format(time_list=time_list))
                # # check pass or fail
                # pass_fail = obj.pass_fail_check(time_list)

                # # dictionary of whole data
                # ftp_data[interation_num] = obj.ftp_test_data(time_list, pass_fail, args.bands, args.file_sizes,
                #                                              args.directions, args.num_stations)
                # # print("pass_fail_duration - ftp_data:{ftp_data}".format(ftp_data=ftp_data))
                obj.stop()
                print("Traffic stopped running")

                obj.postcleanup()
                time2 = datetime.now()
                logger.info("Test ended at %s", time2)

    # 2nd time stamp for test duration
    time_stamp2 = datetime.now()

    # total time for test duration
    # test_duration = str(time_stamp2 - time_stamp1)[:-7]

    date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

    # print(ftp_data)

    input_setup_info = {
        "AP IP": args.ap_ip,
        "File Size": args.file_sizes,
        "Bands": args.bands,
        "Direction": args.directions,
        "Stations": args.num_stations,
        "Upstream": args.upstream_port,
        "SSID": args.ssid,
        "Security": args.security,
        "Contact": "support@candelatech.com"
    }
    # Report generation when groups are specified
    if args.group_name:
        obj.generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                            test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                            dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                            dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                            bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir, config_devices=configuration)
    # Generating report without group-specific device configuration
    else:
        obj.generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                            test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                            dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                            dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                            bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir)
# FOR WEB-UI // to fetch the last logs of the execution.
    if args.dowebgui:
        obj.data_for_webui["status"] = ["STOPPED"] * len(obj.url_data)

        df1 = pd.DataFrame(obj.data_for_webui)
        df1.to_csv('{}/ftp_datavalues.csv'.format(obj.result_dir), index=False)
        # copying to home directory i.e home/user_name
        obj.copy_reports_to_home_dir()


if __name__ == '__main__':
    main()
