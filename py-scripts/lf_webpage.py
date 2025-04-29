#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_webpage.py

PURPOSE:
lf_webpage.py will verify that N clients are connected on a specified band and can download
some amount of file data from the HTTP server while measuring the time taken by clients to download the file and number of
times the file is downloaded.

EXAMPLE-1:
Command Line Interface to run download scenario for Real clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --ssid Cisco-5g --security wpa2 --passwd sharedsecret
--upstream_port eth1 --duration 10m --bands 5G --client_type Real --file_size 2MB

EXAMPLE-2:
Command Line Interface to run download scenario on 5GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --fiveg_ssid Cisco-5g --fiveg_security wpa2 --fiveg_passwd sharedsecret
--fiveg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 5G --client_type Virtual --file_size 2MB --num_stations 3

EXAMPLE-3:
Command Line Interface to run download scenario on 2.4GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --twog_ssid Cisco-2g --twog_security wpa2 --twog_passwd sharedsecret
--twog_radio wiphy0 --upstream_port eth1 --duration 1h --bands 2.4G --client_type Virtual --file_size 2MB --num_stations 3

EXAMPLE-4:
Command Line Interface to run download scenario on 6GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --sixg_ssid Cisco-6g --sixg_security wpa3 --sixg_passwd sharedsecret
--sixg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 6G --client_type Virtual --file_size 2MB --num_stations 3

EXAMPLE-5:
Command Line Interface to run download scenario for Real clients with device list
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.214.219 --ssid Cisco-5g --security wpa2 --passwd sharedsecret  --upstream_port eth1
--duration 1m --bands 5G --client_type Real --file_size 2MB --device_list 1.12,1.22

EXAMPLE-6:
Command Line Interface to run download scenario for Real clients with device list and Expected Pass/Fail CSV
python3 lf_webpage.py  --file_size 1MB --mgr 192.168.213.218 --duration 1m --client_type Real --bands 5G --upstream_port eth1 --device_list 1.11,1.95 --device_csv_name test.csv

EXAMPLE-7:
Command Line Interface to run download scenario for Real clients with device list and expected passfail value
python3 lf_webpage.py  --file_size 1MB --mgr 192.168.204.74 --duration 1m --client_type Real --bands 5G --upstream_port eth1 --device_list 1.11,1.95 --expected_passfail_value 5

EXAMPLE-8:
Command Line Interface to run download scenario for Real clients with Groups and Profiles
python3 lf_webpage.py  --file_size 1MB --mgr 192.168.213.218 --duration 1m --client_type Real --bands 5G --upstream_port eth1 --file_name grp218 --group_name laptops --profile_name Opensd

EXAMPLE-9:
Command Line Interface to run download scenario for Real clients with device list and config
python3 lf_webpage.py --file_size 1MB --mgr 192.168.244.97 --duration 1m --client_type Real --bands 5G --upstream_port eth1 --ssid
xiab_2G_WPA2 --passwd lanforge --security wpa2 --device_list 1.160,1.146,1.13,1.20 --config

SCRIPT_CLASSIFICATION : Test

SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

NOTES:
1.Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h.
2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
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

# from lf_interop_qos import ThroughputQOS
import sys
import os
import importlib
import time
import argparse
import paramiko
from datetime import datetime, timedelta
import pandas as pd
import logging
import requests
import shutil
import json
from lf_graph import lf_bar_graph_horizontal

import asyncio
from typing import List, Optional
import csv

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
PortUtils = realm.PortUtils
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HttpDownload(Realm):
    def __init__(self, lfclient_host, lfclient_port, upstream, num_sta, security, ssid, password, ap_name,
                 target_per_ten, file_size, bands, start_id=0, twog_radio=None, fiveg_radio=None, sixg_radio=None, _debug_on=False, _exit_on_error=False,
                 test_name=None, _exit_on_fail=False, client_type="", port_list=[], devices_list=[], macid_list=[], lf_username="lanforge", lf_password="lanforge", result_dir="", dowebgui=False,
                 device_list=[], get_url_from_file=None, file_path=None, device_csv_name='', expected_passfail_value=None, file_name=None, group_name=None, profile_name=None, eap_method=None,
                 eap_identity=None, ieee80211=None, ieee80211u=None, ieee80211w=None, enable_pkc=None, bss_transition=None, power_save=None, disable_ofdma=None, roam_ft_ds=None, key_management=None,
                 pairwise=None, private_key=None, ca_cert=None, client_cert=None, pk_passwd=None, pac_file=None, config=False, wait_time=60):
        # super().__init__(lfclient_host=lfclient_host,
        #                  lfclient_port=lfclient_port)
        self.ssid_list = []
        self.devices = []
        self.mode_list = []
        self.channel_list = []
        self.host = lfclient_host
        self.port = lfclient_port
        self.upstream = upstream
        self.num_sta = num_sta
        self.security = security
        self.ssid = ssid
        self.sta_start_id = start_id
        self.password = password
        self.twog_radio = twog_radio
        self.fiveg_radio = fiveg_radio
        self.sixg_radio = sixg_radio
        self.target_per_ten = target_per_ten
        self.file_size = file_size
        self.bands = bands
        self.debug = _debug_on
        self.port_list = port_list
        self.result_dir = result_dir
        self.test_name = test_name
        self.dowebgui = dowebgui
        self.device_list = device_list
        self.eid_list = []
        self.devices_list = devices_list
        self.macid_list = []
        self.client_type = client_type
        self.lf_username = lf_username
        self.lf_password = lf_password
        self.ap_name = ap_name
        self.windows_ports = []
        self.windows_eids = []
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.http_profile = self.local_realm.new_http_profile()
        self.http_profile.requests_per_ten = self.target_per_ten
        # self.http_profile.url = self.url
        self.port_util = PortUtils(self.local_realm)
        self.http_profile.debug = _debug_on
        self.created_cx = {}
        self.station_list = []
        self.radio = []
        self.get_url_from_file = get_url_from_file
        self.file_path = file_path
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
        self.expected_passfail_value = expected_passfail_value
        self.device_csv_name = device_csv_name
        self.wait_time = wait_time
        self.config = config
        self.api_url = 'http://{}:{}'.format(self.host, self.port)
        self.group_device_map = {}

# The 'phantom_check' will be handled within the 'get_real_client_list' function
    def get_real_client_list(self):
        user_list = []
        real_client_list1 = []
        real_client_list2 = []
        android_list = []
        mac_list = []
        windows_list = []
        linux_list = []
        working_resources_list = []
        eid_list = []
        devices_available = []
        input_devices_list = []
        mac_id_list1 = []
        mac_id_list2 = []
        port_eid_list = []
        same_eid_list = []
        original_port_list = []
        device_found = False
        obj = DeviceConfig.DeviceConfig(lanforge_ip=self.host, file_name=self.file_name, wait_time=self.wait_time)
        config_devices = {}
        # upstream port IP for configuration
        upstream_port_ip = self.change_port_to_ip(self.upstream)
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
            'server_ip': upstream_port_ip,
        }
        # When groups and profiles specified for configuration
        if self.group_name and self.file_name and self.device_list == [] and self.profile_name:
            selected_groups = self.group_name.split(',')
            selected_profiles = self.profile_name.split(',')
            if len(selected_groups) == len(selected_profiles):
                for i in range(len(selected_groups)):
                    config_devices[selected_groups[i]] = selected_profiles[i]
            obj.initiate_group()
            self.group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
            # Configuration of group of devices for the corresponding profiles
            self.device_list = asyncio.run(obj.connectivity(config_devices, upstream=upstream_port_ip))
            if len(self.device_list) == 0:
                devices_list = ""
        elif self.device_list != []:
            obj.get_all_devices()
            self.device_list = self.device_list.split(',')
            # Configuration of devices with SSID,Password and Security when device list is specified
            if self.config:
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=config_dict))

        elif self.device_list == [] and self.config:
            all_devices = obj.get_all_devices()
            device_list = []
            for device in all_devices:
                if device["type"] == 'laptop':
                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                else:
                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
            logger.info("Available devices: %s", device_list)
            self.device_list = input("Enter the desired resources to run the test:").split(',')
            # Configuration of devices with SSID , Password and Security when the device list is not specified
            if self.config:
                self.device_list = asyncio.run(obj.connectivity(device_list=self.device_list, wifi_config=config_dict))

        response = self.local_realm.json_get("/resource/all")
        for key, value in response.items():
            if key == "resources":
                for element in value:
                    for a, b in element.items():
                        if not b['phantom']:
                            working_resources_list.append(b["hw version"])
                            if "Win" in b['hw version']:
                                eid_list.append(b['eid'])
                                windows_list.append(b['hw version'])
                                # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                devices_available.append(b['eid'] + " " + 'Win' + " " + b['hostname'])
                            elif "Linux" in b['hw version']:
                                if ('ct' not in b['hostname']):
                                    if ('lf' not in b['hostname']):
                                        eid_list.append(b['eid'])
                                        linux_list.append(b['hw version'])
                                        # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                        devices_available.append(b['eid'] + " " + 'Lin' + " " + b['hostname'])
                            elif "Apple" in b['hw version']:
                                if b['kernel'] == '':
                                    continue
                                else:
                                    eid_list.append(b['eid'])
                                    mac_list.append(b['hw version'])
                                    # self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                    devices_available.append(b['eid'] + " " + 'Mac' + " " + b['hostname'])
                            else:
                                eid_list.append(b['eid'])
                                android_list.append(b['hw version'])
                                # self.username_list.append(b['eid']+ " " +b['user'])
                                devices_available.append(b['eid'] + " " + 'android' + " " + b['user'])
        # print("hostname list :",self.hostname_list)
        # print("username list :", self.username_list)
        # print("Available resources in resource tab :", devices_available)
        # print("eid_list : ",eid_list)
        # All the available resources are fetched from resource mgr tab ----

        response_port = self.local_realm.json_get("/port/all")
        # print(response_port)
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if (not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0" and port_data['alias'] != 'p2p0'):
                    for id in eid_list:
                        if (id + '.' in port):
                            original_port_list.append(port)
                            port_eid_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]))
                            mac_id_list1.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]) + ' ' + port_data['mac'])
        # print("port eid list",port_eid_list)
        for i in range(len(eid_list)):
            for j in range(len(port_eid_list)):
                if eid_list[i] == port_eid_list[j]:
                    same_eid_list.append(eid_list[i])
        same_eid_list = [_eid + ' ' for _eid in same_eid_list]
        # print("same eid list",same_eid_list)
        # print("mac_id list",mac_id_list)
        # All the available ports from port manager are fetched from port manager tab ---
        for eid in same_eid_list:
            for device in devices_available:
                if eid in device:
                    logger.info("%s %s", eid, device)
                    user_list.append(device)
        if not self.config and len(self.device_list) == 0 and self.group_name is None:
            logger.info("AVAILABLE DEVICES TO RUN TEST : {}".format(user_list))
            self.device_list = input("Enter the desired resources to run the test:")
            self.device_list = self.filter_iOS_devices(self.device_list).split(',')
        # checking for the availability of slected devices to run test
        if len(self.device_list) != 0:
            devices_list = self.device_list
            available_list = []
            not_available = []
            for input_device in devices_list:
                found = False
                for device in user_list:
                    if input_device + " " in device:
                        available_list.append(input_device)
                        found = True
                        break
                if not found:
                    not_available.append(input_device)
                    logger.warning(input_device + " is not available to run test")
            if len(available_list) > 0:
                logger.info("Test is initiated on devices: {}".format(available_list))
                devices_list = ','.join(available_list)
                device_found = True
            else:
                devices_list = ""
                device_found = False
                logger.warning("Test can not be initiated on any selected devices")

        else:
            devices_list = ""

        if devices_list == "" or devices_list == ",":
            logger.error("Selected Devices are not available in the lanforge")
            exit(1)
        resource_eid_list = devices_list.split(',')
        logger.info("devices list {} {}".format(devices_list, resource_eid_list))
        resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]
        resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
        logger.info("resource eid list {} {}".format(resource_eid_list1, original_port_list))

        # User desired eids are fetched ---

        for eid in resource_eid_list1:
            for ports_m in original_port_list:
                if eid in ports_m:
                    input_devices_list.append(ports_m)
        logger.info("INPUT DEVICES LIST {}".format(input_devices_list))

        # user desired real client list 1.1 wlan0 ---

        for i in resource_eid_list2:
            for j in range(len(user_list)):
                if i in user_list[j]:
                    real_client_list1.append(user_list[j])
                    real_client_list2.append((user_list[j])[:25])
        logger.info("REAL CLIENT LIST: %s", real_client_list1)

        self.num_sta = len(real_client_list1)

        for eid in resource_eid_list2:
            for i in mac_id_list1:
                if eid in i:
                    mac_id_list2.append(i.strip(eid + ' '))
        logger.info("MAC ID LIST: %s", mac_id_list2)
        self.port_list, self.devices_list, self.macid_list = input_devices_list, real_client_list1, mac_id_list2
        # user desired real client list 1.1 OnePlus, 1.1 Apple for report generation ---
    # Todo- Make use of lf_base_interop_profile.py : Real device class to fetch available devices data

        for port in self.port_list:
            eid = self.name_to_eid(port)
            self.eid_list.append(str(eid[0]) + '.' + str(eid[1]))
        for eid in self.eid_list:
            for device in self.devices_list:
                if ("Win" in device) and (eid + ' ' in device):
                    self.windows_eids.append(eid)

        for eid in self.windows_eids:
            for port in self.port_list:
                if eid + '.' in port:
                    self.windows_ports.append(port)
        if self.dowebgui == "True":
            if not device_found:
                print("No Device is available to run the test hence aborting the testllmlml")
                df1 = pd.DataFrame([{
                    "client": [],
                    "status": "Stopped",
                    "url_data": 0
                }]
                )
                df1.to_csv('{}/http_datavalues.csv'.format(self.result_dir), index=False)
                raise ValueError("Aborting the test....")
        return self.port_list, self.devices_list, self.macid_list, config_devices

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

    def set_values(self):
        # This method will set values according user input
        if self.bands == "5G":
            self.radio = [self.fiveg_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                        end_id_=self.num_sta - 1, padding_number_=10000,
                                                        radio=self.fiveg_radio)]
        elif self.bands == "6G":
            self.radio = [self.sixg_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                        end_id_=self.num_sta - 1, padding_number_=10000,
                                                        radio=self.sixg_radio)]
        elif self.bands == "2.4G":
            self.radio = [self.twog_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                        end_id_=self.num_sta - 1, padding_number_=10000,
                                                        radio=self.twog_radio)]
        elif self.bands == "Both":
            self.radio = [self.twog_radio, self.fiveg_radio]
            # self.num_sta = self.num_sta // 2
            self.station_list = [
                LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                       end_id_=self.num_sta - 1, padding_number_=10000,
                                       radio=self.twog_radio),
                LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                       end_id_=self.num_sta - 1, padding_number_=10000,
                                       radio=self.fiveg_radio)
            ]

    def precleanup(self):
        self.count = 0
        for rad in range(len(self.radio)):
            if self.radio[rad] == self.fiveg_radio:
                # select an mode
                self.station_profile.mode = 14
                self.count = self.count + 1
            elif self.radio[rad] == self.sixg_radio:
                # select an mode
                self.station_profile.mode = 15
                self.count = self.count + 1
            elif self.radio[rad] == self.twog_radio:
                # select an mode
                self.station_profile.mode = 13
                self.count = self.count + 1

            if self.count == 2:
                self.sta_start_id = self.num_sta
                self.num_sta = 2 * (self.num_sta)
                self.station_profile.mode = 10
                self.http_profile.cleanup()
                # cleanup station list which started sta_id 20
                self.station_profile.cleanup(self.station_list[rad], debug_=self.local_realm.debug)
                LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                                   port_list=self.station_list[rad],
                                                   debug=self.local_realm.debug)
                return
            # clean dlayer4 ftp traffic
            self.http_profile.cleanup()

            # cleans stations
            self.station_profile.cleanup(self.station_list[rad], delay=1, debug_=self.local_realm.debug)
            LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                               port_list=self.station_list[rad],
                                               debug=self.local_realm.debug)
            time.sleep(1)
        print("precleanup done")

    def build(self):
        # enable http on ethernet
        self.port_util.set_http(port_name=self.local_realm.name_to_eid(self.upstream)[2],
                                resource=self.local_realm.name_to_eid(self.upstream)[1], on=True)
        if self.client_type == "Virtual":
            if self.bands == "2.4G":
                self.station_profile.mode = 13
            elif self.bands == "5G":
                self.station_profile.mode = 14
            elif self.bands == "6G":
                self.station_profile.mode = 15
            for rad in range(len(self.radio)):
                self.station_profile.use_security(self.security[rad], self.ssid[rad], self.password[rad])
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                self.station_profile.create(radio=self.radio[rad], sta_names_=self.station_list[rad], debug=self.local_realm.debug)
                self.local_realm.wait_until_ports_appear(sta_list=self.station_list[rad])
                self.station_profile.admin_up()
                if self.local_realm.wait_for_ip(self.station_list[rad], timeout_sec=60):
                    self.local_realm._pass("All stations got IPs")
                else:
                    self.local_realm._fail("Stations failed to get IPs")
                # building layer4
                self.http_profile.direction = 'dl'
                self.http_profile.dest = '/dev/null'
                data = self.local_realm.json_get("ports/list?fields=IP")

                # getting eth ip
                eid = self.local_realm.name_to_eid(self.upstream)
                for i in data["interfaces"]:
                    for j in i:
                        if "{shelf}.{resource}.{port}".format(shelf=eid[0], resource=eid[1], port=eid[2]) == j:
                            ip_upstream = i["{shelf}.{resource}.{port}".format(
                                shelf=eid[0], resource=eid[1], port=eid[2])]['ip']

                # create http profile
                if self.get_url_from_file:  # enabling the GET-URL-FROM-FILE flag if its ture
                    self.http_profile.create(ports=self.station_profile.station_names, sleep_time=.5,
                                             suppress_related_commands_=None, http=True, user=self.lf_username,
                                             passwd=self.lf_password, http_ip=self.file_path, proxy_auth_type=0x200,
                                             timeout=1000, get_url_from_file=True)
                else:
                    self.http_profile.create(ports=self.station_profile.station_names, sleep_time=.5,
                                             suppress_related_commands_=None, http=True, user=self.lf_username,
                                             passwd=self.lf_password, http_ip=ip_upstream + "/webpage.html",
                                             proxy_auth_type=0x200, timeout=1000)
                if self.count == 2:
                    self.station_profile.mode = 6
        else:
            if self.client_type == "Real":
                self.http_profile.direction = 'dl'
                data = self.local_realm.json_get("ports/list?fields=IP")

                # getting eth ip
                eid = self.local_realm.name_to_eid(self.upstream)
                for i in data["interfaces"]:
                    for j in i:
                        if "{shelf}.{resource}.{port}".format(shelf=eid[0], resource=eid[1], port=eid[2]) == j:
                            ip_upstream = i["{shelf}.{resource}.{port}".format(
                                shelf=eid[0], resource=eid[1], port=eid[2])]['ip']

                self.http_profile.create(ports=self.port_list, sleep_time=.5,
                                         suppress_related_commands_=None, http=True, interop=True,
                                         user=self.lf_username, passwd=self.lf_password,
                                         http_ip=ip_upstream + "/webpage.html", proxy_auth_type=0x200, timeout=1000, windows_list=self.windows_ports)

        print("Test Build done")

    def start(self):
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    def stop(self):
        self.http_profile.stop_cx()
        # To update status of devices and remaining_time in ftp_datavalues.csv file to stopped and 0 respectively.
        if self.client_type == 'Real':
            self.data["status"] = ["STOPPED"] * len(self.macid_list)
            self.data["remaining_time"] = ["0"] * len(self.macid_list)
            df1 = pd.DataFrame(self.data)
            df1.to_csv("http_datavalues.csv", index=False)

    def monitor_for_runtime_csv(self, duration):

        time_now = datetime.now()
        starttime = time_now.strftime("%d/%m %I:%M:%S %p")
        # duration = self.traffic_duration
        endtime = time_now + timedelta(seconds=duration)
        end_time = endtime
        endtime = endtime.isoformat()[0:19]
        current_time = datetime.now().isoformat()[0:19]
        self.data = {}
        self.data["client"] = self.devices_list
        # self.data["url_data"] = []
        self.data_for_webui = {}
        self.data_for_webui["client"] = self.devices_list
        self.get_device_port_details()
        max_bytes_rd = []
        rx_rate_val = []
        while (current_time < endtime):

            # data in json format
            # data = self.json_get("layer4/list?fields=bytes-rd")
            # uc_avg_data = self.json_get("layer4/list?fields=uc-avg")
            # uc_max_data = self.json_get("layer4/list?fields=uc-max")
            # uc_min_data = self.json_get("layer4/list?fields=uc-min")
            # total_url_data = self.json_get("layer4/list?fields=total-urls")
            # bytes_rd = self.json_get("layer4/list?fields=bytes-rd")
            uc_avg_data = self.my_monitor('uc-avg')
            uc_max_data = self.my_monitor('uc-max')
            uc_min_data = self.my_monitor('uc-min')
            url_times = self.my_monitor('total-urls')
            rx_rate = self.my_monitor('rx rate')
            bytes_rd = self.my_monitor('bytes-rd')
            self.data["MAC"] = self.macid_list
            self.data["SSID"] = self.ssid_list
            self.data["Channel"] = self.channel_list
            self.data["Mode"] = self.mode_list

            if len(max_bytes_rd) == 0:
                max_bytes_rd = list(bytes_rd)
            for i in range(len(max_bytes_rd)):
                bytes_rd[i] = max(max_bytes_rd[i], bytes_rd[i])
            max_bytes_rd = list(bytes_rd)
            # bytes_rd = [round(x / 1000000,4) for x in bytes_rd]
            rx_rate_val.append(list(rx_rate))
            # taking average of rx-rate from the previous and current in the first row
            for j in range(len(rx_rate_val[0])):
                rx_rate_sum = 0
                non_zero = 0
                for i in range(len(rx_rate_val)):
                    if rx_rate_val[i][j] != 0:
                        rx_rate_sum += rx_rate_val[i][j]
                        non_zero += 1
                rx_rate_avg = rx_rate_sum / non_zero if non_zero > 0 else 0  # updating each device's rx rate average in 1st row
                rx_rate[j] = round(rx_rate_avg, 4)
            # dataset = [round(x / 1000000,4) for x in dataset] #converting bps to mbps

            if len(url_times) == len(self.devices_list):

                self.data["status"] = ["RUNNING"] * len(self.devices_list)
                self.data["url_data"] = url_times
                self.data["uc_min"] = uc_min_data
                self.data["uc_max"] = uc_max_data
                self.data["uc_avg"] = uc_avg_data
                self.data["bytes_rd"] = bytes_rd
                self.data["rx_rate"] = rx_rate
            else:
                self.data["status"] = ["RUNNING"] * len(self.devices_list)
                self.data["url_data"] = [0] * len(self.devices_list)
                self.data["uc_avg"] = [0] * len(self.devices_list)
                self.data["uc_max"] = [0] * len(self.devices_list)
                self.data["uc_min"] = [0] * len(self.devices_list)
                self.data["bytes_rd"] = [0] * len(self.devices_list)
                self.data["rx_rate"] = [0] * len(self.devices_list)
            time_difference = abs(end_time - datetime.now())
            total_hours = time_difference.total_seconds() / 3600
            remaining_minutes = (total_hours % 1) * 60
            self.data["start_time"] = [starttime] * len(self.devices_list)
            self.data["end_time"] = [end_time.strftime("%d/%m %I:%M:%S %p")] * len(self.devices_list)
            self.data["remaining_time"] = [[str(int(total_hours)) + " hr and " + str(
                int(remaining_minutes)) + " min" if int(total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][
                0]] * len(self.devices_list)
            df1 = pd.DataFrame(self.data)
            if self.dowebgui:
                df1.to_csv('{}/http_datavalues.csv'.format(self.result_dir), index=False)
            elif self.client_type == 'Real':
                df1.to_csv("http_datavalues.csv", index=False)
            time.sleep(5)
            if self.dowebgui == "True":
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                 self.test_name),
                          'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        print('Test is stopped by the user')
                        self.data["end_time"] = [datetime.now().strftime("%d/%m %I:%M:%S %p")] * len(self.devices_list)
                        break

            current_time = datetime.now().isoformat()[0:19]

    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        # print(data)
        data1 = []
        try:
            data = data['endpoint']
            if self.client_type == "Real":
                self.num_sta = len(self.port_list)
            if self.num_sta == 1:
                data1.append(data[data_mon])
            else:
                for cx in self.http_profile.created_cx.keys():
                    for info in data:
                        if cx in info:
                            data1.append(info[cx][data_mon])
            return data1
        except Exception as e:
            total_data = self.local_realm.json_get("layer4/all")
            logger.error(f"no endpoint found: {e}")
            logger.error(total_data)

    def postcleanup(self):
        self.http_profile.cleanup()
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def file_create(self, ssh_port):
        ip = self.host
        user = "root"
        pswd = "lanforge"
        port = ssh_port
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=port, username=user, password=pswd, banner_timeout=600)
        cmd = '[ -f /usr/local/lanforge/nginx/html/webpage.html ] && echo "True" || echo "False"'
        stdin, stdout, stderr = ssh.exec_command(str(cmd))
        output = stdout.readlines()
        if output == ["True\n"]:
            cmd1 = "rm /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd1))
            output = stdout.readlines()
            time.sleep(10)
            cmd2 = "sudo fallocate -l " + self.file_size + " /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            print("File creation done", self.file_size)
            output = stdout.readlines()
        else:
            cmd2 = "sudo fallocate -l " + self.file_size + " /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            print("File creation done", self.file_size)
            output = stdout.readlines()
        ssh.close()
        time.sleep(1)
        return output

    def download_time_in_sec(self, result_data):
        self.result_data = result_data
        download_time = dict.fromkeys(result_data.keys())
        for i in download_time:
            try:
                download_time[i] = result_data[i]['dl_time']
            except BaseException:
                download_time[i] = []
        print("dl_times: ", download_time)
        lst = []
        lst1 = []
        lst2 = []
        lst3 = []
        dwnld_time = dict.fromkeys(result_data.keys())
        dataset = []
        for i in download_time:
            if i == "6G":
                logger.info("download time[%d]: %s", i, download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst3.append(y)
                dwnld_time["6G"] = lst3
                dataset.append(dwnld_time["6G"])
            if i == "5G":
                logger.info("download time[%d]: %s", i, download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst.append(y)
                dwnld_time["5G"] = lst
                dataset.append(dwnld_time["5G"])
            if i == "2.4G":
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst1.append(y)
                dwnld_time["2.4G"] = lst1
                dataset.append(dwnld_time["2.4G"])
            if i == "Both":
                # print("yes", download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst2.append(y)
                # print(lst2)
                dwnld_time["Both"] = lst2
                dataset.append(dwnld_time["Both"])
        return dataset

    def speed_in_Mbps(self, result_data):
        self.result_data = result_data
        speed = dict.fromkeys(result_data.keys())
        for i in speed:
            try:
                speed[i] = result_data[i]['speed']
            except BaseException:
                speed[i] = []
        lst = []
        lst1 = []
        lst2 = []
        speed_ = dict.fromkeys(result_data.keys())
        dataset = []
        for i in speed:
            if i == "5G":
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst.append(y)
                speed_["5G"] = lst
                dataset.append(speed_["5G"])
            if i == "2.4G":
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst1.append(y)
                speed_["2.4G"] = lst1
                dataset.append(speed_["2.4G"])
            if i == "Both":
                # print("yes", speed[i])
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst2.append(y)
                speed_["Both"] = lst2
                dataset.append(speed_["Both"])
        return dataset

    def summary_calculation(self, result_data, bands, threshold_5g, threshold_2g, threshold_both):
        self.result_data = result_data

        avg_dl_time = []
        html_struct = dict.fromkeys(list(result_data.keys()))
        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["avg"]
            for i in fcc_type:
                avg_dl_time.append(i)

        avg_dl_time_per_thou = []
        for i in avg_dl_time:
            i = i / 1000
            avg_dl_time_per_thou.append(i)

        avg_time_rounded = []
        for i in avg_dl_time_per_thou:
            i = str(round(i, 1))
            avg_time_rounded.append(i)

        pass_fail_list = []
        sumry2 = []
        sumry5 = []
        sumryB = []
        data = []

        for band in range(len(bands)):
            if bands[band] == "2.4G":
                # 2.4G
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_2g):
                    var = "FAIL"
                    pass_fail_list.append(var)
                    sumry2.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_2g):
                    pass_fail_list.append("PASS")
                    sumry2.append("PASS")
                data.append(','.join(sumry2))

            elif bands[band] == "5G":
                # 5G
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_5g):
                    print("FAIL")
                    pass_fail_list.append("FAIL")
                    sumry5.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_5g):
                    print("PASS")
                    pass_fail_list.append("PASS")
                    sumry5.append("PASS")
                data.append(','.join(sumry5))

            elif bands[band] == "Both":
                # BOTH
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_both):
                    var = "FAIL"
                    pass_fail_list.append(var)
                    sumryB.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_both):
                    pass_fail_list.append("PASS")
                    sumryB.append("PASS")
                data.append(','.join(sumryB))

        return data

    def check_station_ip(self):
        pass

    def generate_graph(self, dataset, lis, bands):
        bands = ['Download']
        if self.client_type == "Real":
            lis = self.devices_list
        elif self.client_type == "Virtual":
            lis = self.station_list[0]
        logger.info("%s %s", dataset, lis)
        x_fig_size = 18
        y_fig_size = len(lis) * .5 + 4
        # graph = lf_graph.lf_bar_graph(_data_set=dataset, _xaxis_name="Stations", _yaxis_name="Time in Seconds",
        #                               _xaxis_categories=lis, _label=bands, _xticks_font=8,
        #                               _graph_image_name="webpage download time graph",
        #                               _color=['forestgreen', 'darkorange', 'blueviolet'], _color_edge='black', _figsize=(14, 5),
        #                               _grp_title="Download time taken by each client", _xaxis_step=1, _show_bar_value=True,
        #                               _text_font=6, _text_rotation=60,
        #                               _legend_loc="upper right",
        #                               _legend_box=(1, 1.15),
        #                               _enable_csv=True
        #                               )
        graph = lf_bar_graph_horizontal(_data_set=[dataset], _xaxis_name="Average time taken to Download file in ms",
                                        _yaxis_name="Client names",
                                        _yaxis_categories=[i for i in lis],
                                        _yaxis_label=[i for i in lis],
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _yticks_rotation=None,
                                        _graph_title="Average time taken to Download file",
                                        _title_size=16,
                                        _figsize=(x_fig_size, y_fig_size),
                                        _legend_loc="best",
                                        _legend_box=(1.0, 1.0),
                                        _color_name=['steelblue'],
                                        _show_bar_value=True,
                                        _enable_csv=True,
                                        _graph_image_name="ucg-avg", _color_edge=['black'],
                                        _color=['steelblue'],
                                        _label=bands)
        graph_png = graph.build_bar_graph_horizontal()
        print("graph name {}".format(graph_png))
        return graph_png

    def graph_2(self, dataset2, lis, bands):
        bands = ['Download']
        if self.client_type == "Real":
            lis = self.devices_list
        elif self.client_type == "Virtual":
            lis = self.station_list[0]
        print(dataset2)
        print(lis)
        x_fig_size = 18
        y_fig_size = len(lis) * .5 + 4
        graph_2 = lf_bar_graph_horizontal(_data_set=[dataset2], _xaxis_name="No of times file Download",
                                          _yaxis_name="Client names",
                                          _yaxis_categories=[i for i in lis],
                                          _yaxis_label=[i for i in lis],
                                          _yaxis_step=1,
                                          _yticks_font=8,
                                          _yticks_rotation=None,
                                          _graph_title="No of times file Download (Count)",
                                          _title_size=16,
                                          _figsize=(x_fig_size, y_fig_size),
                                          _legend_loc="best",
                                          _legend_box=(1.0, 1.0),
                                          _color_name=['orange'],
                                          _show_bar_value=True,
                                          _enable_csv=True,
                                          _graph_image_name="Total-url", _color_edge=['black'],
                                          _color=['orange'],
                                          _label=bands)
        graph_png = graph_2.build_bar_graph_horizontal()
        return graph_png
    # This function is called to get details of devices during runtime

    def get_device_port_details(self):
        self.response_port = self.local_realm.json_get("/port/all")
        if self.client_type == "Real":
            self.devices = self.devices_list
            for interface in self.response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.port_list:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.ssid_list.append(str(port_data['ssid']))

    def generate_report(self, date, num_stations, duration, test_setup_info, dataset, lis, bands, threshold_2g,
                        threshold_5g, threshold_both, dataset2, dataset1,  # summary_table_value,
                        result_data, test_rig, rx_rate,
                        test_tag, dut_hw_version, dut_sw_version, dut_model_num, dut_serial_num, test_id,
                        test_input_infor, csv_outfile, _results_dir_name='webpage_test', report_path=''):
        if self.dowebgui == "True" and report_path == '':
            report = lf_report.lf_report(_results_dir_name="webpage_test", _output_html="Webpage.html",
                                         _output_pdf="Webpage.pdf", _path=self.result_dir)
        else:
            report = lf_report.lf_report(_results_dir_name="webpage_test", _output_html="Webpage.html",
                                         _output_pdf="Webpage.pdf", _path=report_path)

        # To store http_datavalues.csv in report folder
        report_path_date_time = report.get_path_date_time()
        # It ensures no blocker for virtual clients
        if self.client_type == 'Real':
            shutil.move('http_datavalues.csv', report_path_date_time)
        if bands == "Both":
            num_stations = num_stations * 2
        report.set_title("HTTP DOWNLOAD TEST")
        report.set_date(date)
        report.build_banner()
        report.set_table_title("Test Setup Information")
        report.build_table_title()

        report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        report.set_obj_html("Objective", "The HTTP Download Test is designed to verify that N clients connected on specified band can "
                            "download some amount of file from HTTP server and measures the "
                            "time taken by the client to Download the file.")
        report.build_objective()
        report.set_obj_html("No of times file Downloads", "The below graph represents number of times a file downloads for each client"
                            ". X- axis shows “No of times file downloads and Y-axis shows "
                            "Client names.")
        report.build_objective()
        graph2 = self.graph_2(dataset2, lis=lis, bands=bands)
        print("graph name {}".format(graph2))
        report.set_graph_image(graph2)
        report.set_csv_filename(graph2)
        report.move_csv_file()
        report.move_graph_image()
        report.build_graph()
        report.set_obj_html("Average time taken to download file ", "The below graph represents average time taken to download for each client  "
                            ".  X- axis shows “Average time taken to download a file ” and Y-axis shows "
                            "Client names.")
        report.build_objective()
        graph = self.generate_graph(dataset=dataset, lis=lis, bands=bands)
        report.set_graph_image(graph)
        report.set_csv_filename(graph)
        report.move_csv_file()
        report.move_graph_image()
        report.build_graph()

        # report.set_obj_html("Summary Table Description", "This Table shows you the summary "
        #                     "result of Webpage Download Test as PASS or FAIL criteria. If the average time taken by " +
        #                     str(num_stations) + " clients to access the webpage is less than " + str( threshold_2g) +
        #                     "s it's a PASS criteria for 2.4 ghz clients, If the average time taken by " + "" +
        #                     str( num_stations) + " clients to access the webpage is less than " + str( threshold_5g) +
        #                     "s it's a PASS criteria for 5 ghz clients and If the average time taken by " + str( num_stations) +
        #                     " clients to access the webpage is less than " + str(threshold_both) +
        #                     "s it's a PASS criteria for 2.4 ghz and 5ghz clients")

        # report.build_objective()
        # test_setup1 = pd.DataFrame(summary_table_value)
        # report.set_table_dataframe(test_setup1)
        # report.build_table()

        report.set_obj_html("Download Time Table Description", "This Table will provide you information of the "
                            "minimum, maximum and the average time taken by clients to download a webpage in seconds")

        report.build_objective()
        self.response_port = self.local_realm.json_get("/port/all")
        # print(response_port)
        # print("port list",self.port_list)
        # To set channel_list,mode_list,port_list to append once again
        self.channel_list, self.mode_list, self.ssid_list = [], [], []
        if self.client_type == "Real":
            self.devices = self.devices_list
            for interface in self.response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.port_list:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.ssid_list.append(str(port_data['ssid']))
        elif self.client_type == "Virtual":
            self.devices = self.station_list[0]
            for interface in self.response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.station_list[0]:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.macid_list.append(str(port_data['mac']))
                        self.ssid_list.append(str(port_data['ssid']))

        x = []
        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["min"]
            # print(fcc_type)
            for i in fcc_type:
                x.append(i)
            # print(x)
        y = []
        for i in x:
            i = i / 1000
            y.append(i)
        z = []
        for i in y:
            i = str(round(i, 1))
            z.append(i)
        # rint(z)
        x1 = []

        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["max"]
            # print(fcc_type)
            for i in fcc_type:
                x1.append(i)
            # print(x1)
        y1 = []
        for i in x1:
            i = i / 1000
            y1.append(i)
        z1 = []
        for i in y1:
            i = str(round(i, 1))
            z1.append(i)
        # print(z1)
        x2 = []

        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["avg"]
            # print(fcc_type)
            for i in fcc_type:
                x2.append(i)
            # print(x2)
        y2 = []
        for i in x2:
            i = i / 1000
            y2.append(i)
        z2 = []
        for i in y2:
            i = str(round(i, 1))
            z2.append(i)

        download_table_value_dup = {
            # "Band": bands,
            "Minimum": z,
            "Maximum": z1,
            "Average": z2
        }

        download_table_value = {
            "Band": bands,
            "Minimum": z,
            "Maximum": z1,
            "Average": z2
        }

        # Get the report path to create the kpi.csv path
        kpi_path = report.get_report_path()
        print("kpi_path :{kpi_path}".format(kpi_path=kpi_path))

        kpi_csv = lf_kpi_csv.lf_kpi_csv(
            _kpi_path=kpi_path,
            _kpi_test_rig=test_rig,
            _kpi_test_tag=test_tag,
            _kpi_dut_hw_version=dut_hw_version,
            _kpi_dut_sw_version=dut_sw_version,
            _kpi_dut_model_num=dut_model_num,
            _kpi_dut_serial_num=dut_serial_num,
            _kpi_test_id=test_id)
        kpi_csv.kpi_dict['Units'] = "Mbps"
        for band in range(len(download_table_value["Band"])):
            kpi_csv.kpi_csv_get_dict_update_time()
            kpi_csv.kpi_dict['Graph-Group'] = "Webpage Download {band}".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Minimum".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=download_table_value['Minimum'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Maximum".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=download_table_value['Maximum'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Average".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=download_table_value['Average'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

        if csv_outfile is not None:
            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            csv_outfile = "{}_{}-test_l3_longevity.csv".format(
                csv_outfile, current_time)
            csv_outfile = report.file_add_path(csv_outfile)
            print("csv output file : {}".format(csv_outfile))

        test_setup = pd.DataFrame(download_table_value_dup)
        report.set_table_dataframe(test_setup)
        report.build_table()
        if self.group_name:
            report.set_table_title("Overall Results for Groups")
        else:
            report.set_table_title("Overall Results")
        report.build_table_title()
        if self.client_type == "Real":
            # When pass_fail criteria specified (expected_passfail_value / device_csv_name)
            if self.expected_passfail_value or self.device_csv_name:
                test_input_list, pass_fail_list = self.get_pass_fail_list(dataset2)
            if self.group_name:
                for key, val in self.group_device_map.items():
                    # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                    if self.expected_passfail_value or self.device_csv_name:
                        dataframe = self.generate_dataframe(
                            val,
                            self.devices,
                            self.macid_list,
                            self.channel_list,
                            self.ssid_list,
                            self.mode_list,
                            dataset2,
                            test_input_list,
                            dataset,
                            dataset1,
                            rx_rate,
                            pass_fail_list)
                    # Generating Dataframe for groups when pass_fail case is not specified
                    else:
                        dataframe = self.generate_dataframe(val, self.devices, self.macid_list, self.channel_list, self.ssid_list, self.mode_list, dataset2, [], dataset, dataset1, rx_rate, [])

                    if dataframe:
                        report.set_obj_html("", "Group: {}".format(key))
                        report.build_objective()
                        dataframe1 = pd.DataFrame(dataframe)
                        report.set_table_dataframe(dataframe1)
                        report.build_table()
            else:
                dataframe = {
                    " Clients": self.devices,
                    " MAC ": self.macid_list,
                    " Channel": self.channel_list,
                    " SSID ": self.ssid_list,
                    " Mode": self.mode_list,
                    " No of times File downloaded ": dataset2,
                    " Average time taken to Download file (ms)": dataset,
                    " Bytes-rd (Mega Bytes) ": dataset1,
                    "Rx Rate (Mbps)": rx_rate
                }
                if self.expected_passfail_value or self.device_csv_name:
                    dataframe[" Expected value of no of times file downloaded"] = test_input_list
                    dataframe["Status"] = pass_fail_list
                dataframe1 = pd.DataFrame(dataframe)
                report.set_table_dataframe(dataframe1)
                report.build_table()
        else:
            dataframe = {
                " Clients": self.devices,
                " MAC ": self.macid_list,
                " Channel": self.channel_list,
                " SSID ": self.ssid_list,
                " Mode": self.mode_list,
                " No of times File downloaded ": dataset2,
                " Average time taken to Download file (ms)": dataset,
                " Bytes-rd (Mega Bytes) ": dataset1

            }
            dataframe1 = pd.DataFrame(dataframe)
            report.set_table_dataframe(dataframe1)
            report.build_table()
        report.build_footer()
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)
        report.write_pdf()

    def copy_reports_to_home_dir(self):
        curr_path = self.result_dir
        home_dir = os.path.expanduser("~")  # it returns the home directory [ base : home/username]
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
        rxratelist = []
        interop_tab_data = self.local_realm.json_get('/adb/')["devices"]
        for i in range(len(clients_list)):
            for j in groupdevlist:
                if j == clients_list[i].split(" ")[2] and clients_list[i].split(" ")[1] != 'android':
                    clients.append(clients_list[i])
                    macids.append(mac[i])
                    channels.append(channel[i])
                    ssids.append(ssid[i])
                    modes.append(mode[i])
                    downloadtimes.append(file_download[i])
                    avgtimes.append(averagetime[i])
                    readbytes.append(bytes_read[i])
                    rxratelist.append(rx_rate[i])
                    if self.expected_passfail_value or self.device_csv_name:
                        input_list.append(test_input[i])
                        statuslist.append(status[i])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] == clients_list[i].split(' ')[2] and j == item['name'].split('.')[2]:
                                clients.append(clients_list[i])
                                macids.append(mac[i])
                                channels.append(channel[i])
                                ssids.append(ssid[i])
                                modes.append(mode[i])
                                downloadtimes.append(file_download[i])
                                avgtimes.append(averagetime[i])
                                readbytes.append(bytes_read[i])
                                rxratelist.append(rx_rate[i])
                                if self.expected_passfail_value or self.device_csv_name:
                                    input_list.append(test_input[i])
                                    statuslist.append(status[i])
        # Checks if either device in the group is configured
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
                "Rx Rate (Mbps)": rxratelist
            }
            if self.expected_passfail_value or self.device_csv_name:
                dataframe[" Expected value of no of times file downloaded"] = input_list
                dataframe[" Status "] = statuslist
            return dataframe
        # if neither device in the group is configured returns 0
        else:
            return None

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

    # Converting the upstream_port to IP address for configuration purposes
    def change_port_to_ip(self, upstream_port):
        if upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.local_realm.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except BaseException:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def get_pass_fail_list(self, dataset2):
        # When device csv specified for pass_fail criteria
        if self.expected_passfail_value == '' or self.expected_passfail_value is None:
            res_list = []
            test_input_list = []
            pass_fail_list = []

            interop_tab_data = self.local_realm.json_get('/adb/')["devices"]
            for client in self.devices:
                # Check if the client type (second word in "1.15 android samsungmob") is 'android'
                if client.split(' ')[1] != 'android':
                    res_list.append(client.split(' ')[2])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            # Extract the username from the client string (e.g., 'samsungmob' from "1.15 android samsungmob")
                            if item['user-name'] == client.split(' ')[2]:
                                res_list.append(item['name'].split('.')[2])
            with open(self.device_csv_name, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            for device in res_list:
                found = False
                for row in rows:
                    if row['DeviceList'] == device and row['HTTP URLcount'].strip() != '':
                        test_input_list.append(row['HTTP URLcount'])
                        found = True
                        break
                # appending default value when not found in csv
                if not found:
                    logger.info(f'Pass/Fail value for device {device} not found in the CSV. Defaulting to a pass threshold of 5 URL counts.')
                    test_input_list.append(5)
            for i in range(len(test_input_list)):
                if int(test_input_list[i]) <= dataset2[i]:
                    pass_fail_list.append('PASS')
                else:
                    pass_fail_list.append('FAIL')
        # When expected pass_fail value specified for pass_fail criteria
        else:
            test_input_list = [self.expected_passfail_value for val in range(len(self.devices))]
            pass_fail_list = []
            for i in range(len(test_input_list)):
                if int(self.expected_passfail_value) <= dataset2[i]:
                    pass_fail_list.append("PASS")
                else:
                    pass_fail_list.append("FAIL")

        return test_input_list, pass_fail_list


def validate_args(args):
    if args.expected_passfail_value and args.device_csv_name:
        logger.error("Specify either --expected_passfail_value or --device_csv_name")
        exit(1)
    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []

    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)
    elif args.group_name and args.profile_name and args.file_name and args.device_list != []:
        logger.error("Either --group_name or --device_list should be entered not both")
        exit(1)
    elif args.ssid and args.profile_name:
        logger.error("Either --ssid or --profile_name should be given")
        exit(1)
    elif args.file_name and (args.group_name is None or args.profile_name is None):
        logger.error("Please enter the correct set of arguments for configuration")
        exit(1)
    if args.client_type == 'Real' and args.config and args.group_name is None:
        if args.ssid and args.security and args.security.lower() == 'open' and (args.passwd is None or args.passwd == ''):
            args.passwd = '[BLANK]'
        if args.ssid is None or args.passwd is None or args.passwd == '':
            logger.error('For configuration need to Specify --ssid , --passwd (Optional for "open" type security) , --security')
            exit(1)
        elif args.ssid and args.passwd == '[BLANK]' and args.security and args.security.lower() != 'open':
            logger.error('Please provide valid --passwd and --security configuration')
            exit(1)
        elif args.ssid and args.passwd:
            if args.security is None:
                logger.error('Security must be provided when --ssid and --password specified')
                exit(1)
            elif args.ssid and args.passwd == '[BLANK]' and args.security and args.security.lower() != 'open':
                logger.error('Please provide valid passwd and security configuration')
                exit(1)
            elif args.security.lower() == 'open' and args.passwd != '[BLANK]':
                logger.error("For a open type security there will be no password or the password should be left blank (i.e., set to '' or [BLANK]).")
                exit(1)


def main():
    # set up logger
    logger_config = lf_logger_config.lf_logger_config()
    parser = argparse.ArgumentParser(
        prog="lf_webpage.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
    NAME: lf_webpage.py

    PURPOSE:
    lf_webpage.py will verify that N clients are connected on a specified band and can download
    some amount of file data from the HTTP server while measuring the time taken by clients to download the file and number of
    times the file is downloaded.

    EXAMPLE-1:
    Command Line Interface to run download scenario for Real clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --ssid Cisco-5g --security wpa2 --passwd sharedsecret
    --upstream_port eth1 --duration 10m --bands 5G --client_type Real --file_size 2MB

    EXAMPLE-2:
    Command Line Interface to run download scenario on 5GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --fiveg_ssid Cisco-5g --fiveg_security wpa2 --fiveg_passwd sharedsecret
    --fiveg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 5G --client_type Virtual --file_size 2MB --num_stations 3

    EXAMPLE-3:
    Command Line Interface to run download scenario on 2.4GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --twog_ssid Cisco-2g --twog_security wpa2 --twog_passwd sharedsecret
    --twog_radio wiphy0 --upstream_port eth1 --duration 1h --bands 2.4G --client_type Virtual --file_size 2MB --num_stations 3

    EXAMPLE-4:
    Command Line Interface to run download scenario on 6GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --sixg_ssid Cisco-6g --sixg_security wpa3 --sixg_passwd sharedsecret
    --sixg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 6G --client_type Virtual --file_size 2MB --num_stations 3

    EXAMPLE-5:
    Command Line Interface to run the download or upload HTTP urls from a file using Virtual clients on 5GHz band
    Note: The file should contain the the URLs in following mentioned formate
            formate : "dl https://google.com /dev/null"

    EXAMPLE-6:
    Command Line Interface to run download scenario for Real clients with device list
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.214.219 --fiveg_ssid Cisco-5g --fiveg_security wpa2 --fiveg_passwd sharedsecret  --upstream_port eth1
    --duration 1m --bands 5G --client_type Real --file_size 2MB --device_list 1.12,1.22

    Verified CLI:
    python3 lf_webpage.py --ap_name "Netgear1234" --mgr 192.168.200.38 --fiveg_ssid NETGEAR_5G --fiveg_security wpa2
    --fiveg_passwd Password@123 --fiveg_radio 1.1.wiphy1 --upstream_port 1.1.eth2 --duration 1m --bands 5G
    --client_type Virtual --num_stations 5 --get_url_from_file --file_path /home/lanforge/Desktop/dummy.txt

    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

    NOTES:
    1.Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h.
    2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
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
    required = parser.add_argument_group('Required arguments to run lf_webpage.py')
    optional = parser.add_argument_group('Optional arguments to run lf_webpage.py')

    required.add_argument('--mgr', help='hostname for where LANforge GUI is running', default='localhost')
    required.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on', default=8080)
    required.add_argument('--upstream_port', help='non-station port that generates traffic: eg: eth1', default='eth2')
    optional.add_argument('--num_stations', type=int, help='number of stations to create for virtual clients', default=0)
    optional.add_argument('--twog_radio', help='specify radio for 2.4G clients', default='wiphy3')
    optional.add_argument('--fiveg_radio', help='specify radio for 5 GHz client', default='wiphy0')
    optional.add_argument('--sixg_radio', help='Specify radio for 6GHz client', default='wiphy2')
    optional.add_argument('--twog_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 2.4G clients')
    optional.add_argument('--twog_ssid', help='WiFi SSID for script object to associate for 2.4G clients')
    optional.add_argument('--twog_passwd', help='WiFi passphrase/password/key for 2.4G clients')
    optional.add_argument('--fiveg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 5G clients')
    optional.add_argument('--fiveg_ssid', help='WiFi SSID for script object to associate for 5G clients')
    optional.add_argument('--fiveg_passwd', help='WiFi passphrase/password/key for 5G clients')
    optional.add_argument('--sixg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 2.4G clients')
    optional.add_argument('--sixg_ssid', help='WiFi SSID for script object to associate for 2.4G clients')
    optional.add_argument('--sixg_passwd', help='WiFi passphrase/password/key for 2.4G clients')
    optional.add_argument('--target_per_ten', help='number of request per 10 minutes', default=100)
    required.add_argument('--file_size', type=str, help='specify the size of file you want to download', default='5MB')
    required.add_argument('--bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                          default=["5G", "2.4G", "6G"])
    required.add_argument('--duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    required.add_argument('--client_type', help='Enter the type of client. Example:"Real","Virtual"')
    optional.add_argument('--threshold_5g', help="Enter the threshold value for 5G Pass/Fail criteria", default="60")
    optional.add_argument('--threshold_2g', help="Enter the threshold value for 2.4G Pass/Fail criteria", default="90")
    optional.add_argument('--threshold_both', help="Enter the threshold value for Both Pass/Fail criteria", default="50")
    required.add_argument('--ap_name', help="specify the ap model ", default="TestAP")
    optional.add_argument('--lf_username', help="Enter the lanforge user name. Example : 'lanforge' ", default="lanforge")
    optional.add_argument('--lf_password', help="Enter the lanforge password. Example : 'lanforge' ", default="lanforge")
    optional.add_argument('--ssh_port', type=int, help="specify the ssh port eg 22", default=22)
    optional.add_argument("--test_rig", default="", help="test rig for kpi.csv, testbed that the tests are run on")
    optional.add_argument("--test_tag", default="",
                          help="test tag for kpi.csv,  test specific information to differentiate the test")
    optional.add_argument("--dut_hw_version", default="",
                          help="dut hw version for kpi.csv, hardware version of the device under test")
    optional.add_argument("--dut_sw_version", default="",
                          help="dut sw version for kpi.csv, software version of the device under test")
    optional.add_argument("--dut_model_num", default="",
                          help="dut model for kpi.csv,  model number / name of the device under test")
    optional.add_argument("--dut_serial_num", default="",
                          help="dut serial for kpi.csv, serial number / serial number of the device under test")
    optional.add_argument("--test_priority", default="", help="dut model for kpi.csv,  test-priority is arbitrary number")
    optional.add_argument("--test_id", default="lf_webpage", help="test-id for kpi.csv,  script or test name")
    optional.add_argument('--csv_outfile', help="--csv_outfile <Output file for csv data>", default="")
    # ARGS for webGUI
    required.add_argument('--dowebgui', help="If true will execute script for webgui", default=False)  # FOR WEBGUI
    optional.add_argument('--result_dir',
                          help='Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>',
                          default='')
    optional.add_argument('--web_ui_device_list', '--device_list',
                          help='Enter the devices on which the test should be run <Do not use in CLI,--used by webui>', dest='device_list',
                          default=[])
    optional.add_argument('--test_name',
                          help='Specify test name to store the runtime csv results <Do not use in CLI, --used by webui>',
                          default=None)
    optional.add_argument('--get_url_from_file', help='Specify to enable the get url from file flag for cx',
                          action='store_true')
    optional.add_argument('--file_path', help='Specify the path of the file, which has the URLs to download'
                                              ' or upload the URLs', default=None)
    optional.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')
    # Arguments for Configurations and pass_fail criteria (Applicable for real cleints)
    optional.add_argument('--ssid', help='WiFi SSID for script object to associate for Real clients')
    optional.add_argument('--passwd', type=str, nargs='?', const='', help="Specify password for ssid provided")
    optional.add_argument('--security', help='Specify the security')
    optional.add_argument('--file_name', type=str, help='Specify the file name containing group details. Example:file1')
    optional.add_argument('--group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    optional.add_argument('--profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
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
    optional.add_argument("--expected_passfail_value", help="Specify the expected number of urls", default=None)
    optional.add_argument("--device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    optional.add_argument("--wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    optional.add_argument("--config", action="store_true", help="Specify for configuring the devices")

    help_summary = '''\
lf_webpage.py will verify that N clients are connected on a specified band and can download
some amount of file data from the HTTP server while measuring the time taken by clients to download the file and number of
times the file is downloaded.
'''
    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    args.bands.sort()

    # Error checking to prevent case issues
    for band in range(len(args.bands)):
        args.bands[band] = args.bands[band].upper()
        if args.bands[band] == "BOTH":
            args.bands[band] = "Both"

    # Error checking for non-existent bands
    valid_bands = ['2.4G', '5G', '6G', 'Both']
    for band in args.bands:
        if band not in valid_bands:
            raise ValueError("Invalid band '%s' used in bands argument!" % band)

    # Check for Both being used independently
    if len(args.bands) > 1 and "Both" in args.bands:
        raise ValueError("'Both' test type must be used independently!")

    validate_args(args)
    if args.duration.endswith('s') or args.duration.endswith('S'):
        args.duration = int(args.duration[0:-1])
    elif args.duration.endswith('m') or args.duration.endswith('M'):
        args.duration = int(args.duration[0:-1]) * 60
    elif args.duration.endswith('h') or args.duration.endswith('H'):
        args.duration = int(args.duration[0:-1]) * 60 * 60
    elif args.duration.endswith(''):
        args.duration = int(args.duration)

    list6G, list6G_bytes, list6G_speed, list6G_urltimes = [], [], [], []
    list5G, list5G_bytes, list5G_speed, list5G_urltimes = [], [], [], []
    list2G, list2G_bytes, list2G_speed, list2G_urltimes = [], [], [], []
    Both, Both_bytes, Both_speed, Both_urltimes = [], [], [], []
    listReal, listReal_bytes, listReal_speed, listReal_urltimes = [], [], [], []  # For real devices (not band specific)
    dict_keys = []
    dict_keys.extend(args.bands)
    # print(dict_keys)
    final_dict = dict.fromkeys(dict_keys)
    # print(final_dict)
    dict1_keys = ['dl_time', 'min', 'max', 'avg', 'bytes_rd', 'speed', 'url_times']
    for i in final_dict:
        final_dict[i] = dict.fromkeys(dict1_keys)
    print(final_dict)
    min6 = []
    min5 = []
    min2 = []
    min_both = []
    max6 = []
    max5 = []
    max2 = []
    max_both = []
    avg6 = []
    avg2 = []
    avg5 = []
    avg_both = []
    port_list, device_list, macid_list = [], [], []
    for bands in args.bands:
        # For real devices while ensuring no blocker for Virtual devices
        if args.client_type == 'Real':
            ssid = args.ssid
            passwd = args.passwd
            security = args.security
        elif bands == "2.4G":
            security = [args.twog_security]
            ssid = [args.twog_ssid]
            passwd = [args.twog_passwd]
        elif bands == "5G":
            security = [args.fiveg_security]
            ssid = [args.fiveg_ssid]
            passwd = [args.fiveg_passwd]
        elif bands == "6G":
            security = [args.sixg_security]
            ssid = [args.sixg_ssid]
            passwd = [args.sixg_passwd]
        elif bands == "Both":
            security = [args.twog_security, args.fiveg_security]
            ssid = [args.twog_ssid, args.fiveg_ssid]
            passwd = [args.twog_passwd, args.fiveg_passwd]
        http = HttpDownload(lfclient_host=args.mgr, lfclient_port=args.mgr_port,
                            upstream=args.upstream_port, num_sta=args.num_stations,
                            security=security, ap_name=args.ap_name,
                            ssid=ssid, password=passwd,
                            target_per_ten=args.target_per_ten,
                            file_size=args.file_size, bands=bands,
                            twog_radio=args.twog_radio,
                            fiveg_radio=args.fiveg_radio,
                            sixg_radio=args.sixg_radio,
                            client_type=args.client_type,
                            lf_username=args.lf_username, lf_password=args.lf_password,
                            result_dir=args.result_dir,  # FOR WEBGUI
                            dowebgui=args.dowebgui,  # FOR WEBGUI
                            device_list=args.device_list,
                            test_name=args.test_name,  # FOR WEBGUI
                            get_url_from_file=args.get_url_from_file,
                            file_path=args.file_path,
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
                            expected_passfail_value=args.expected_passfail_value,
                            device_csv_name=args.device_csv_name,
                            wait_time=args.wait_time,
                            config=args.config
                            )
        if args.client_type == "Real":
            if not isinstance(args.device_list, list):
                http.device_list = http.filter_iOS_devices(args.device_list)
                if len(http.device_list) == 0:
                    logger.info("There are no devices available")
                    exit(1)
            port_list, device_list, macid_list, configuration = http.get_real_client_list()
            if args.dowebgui and args.group_name:
                if len(device_list) == 0:
                    logger.info("No device is available to run the test")
                    obj = {
                        "status": "Stopped",
                        "configuration_status": "configured"
                    }
                    http.updating_webui_runningjson(obj)
                    return
                else:
                    obj = {
                        "configured_devices": device_list,
                        "configuration_status": "configured"
                    }
                    http.updating_webui_runningjson(obj)
            android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
            all_devices_names = []
            device_type = []
            total_devices = ""
            for i in device_list:
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
            args.num_stations = len(port_list)
        if not args.get_url_from_file:
            http.file_create(ssh_port=args.ssh_port)
        else:
            if args.file_path is None:
                print("WARNING: Please Specify the path of the file, if you select the --get_url_from_file")
                exit(0)
        http.set_values()
        http.precleanup()
        http.build()
        test_time = datetime.now()
        # Solution For Leap Year conflict changed it to %Y
        test_time = test_time.strftime("%Y %d %H:%M:%S")
        print("Test started at ", test_time)
        http.start()
        if args.dowebgui:
            # FOR WEBGUI, -This fumction is called to fetch the runtime data from layer-4
            http.monitor_for_runtime_csv(args.duration)
        elif args.client_type == 'Real':
            # To fetch runtime csv during runtime
            http.monitor_for_runtime_csv(args.duration)
        else:
            time.sleep(args.duration)
        http.stop()
        # taking http.data, which got updated in the monitor_for_runtime_csv method
        if args.client_type == 'Real':
            uc_avg_val = http.data['uc_avg']
            url_times = http.data['url_data']
            rx_bytes_val = http.data['bytes_rd']
            rx_rate_val = http.data['rx_rate']
        else:
            uc_avg_val = http.my_monitor('uc-avg')
            url_times = http.my_monitor('total-urls')
            rx_bytes_val = http.my_monitor('bytes-rd')
            rx_rate_val = http.my_monitor('rx rate')
        if args.dowebgui:
            http.data_for_webui["url_data"] = url_times  # storing the layer-4 url data at the end of test
        if args.client_type == 'Real':  # for real clients
            listReal.extend(uc_avg_val)
            listReal_bytes.extend(rx_bytes_val)
            listReal_speed.extend(rx_rate_val)
            listReal_urltimes.extend(url_times)
            logger.info("%s %s %s", listReal, listReal_bytes, listReal_speed)
            final_dict[bands]['dl_time'] = listReal
            min2.append(min(listReal))
            final_dict[bands]['min'] = min2
            max2.append(max(listReal))
            final_dict[bands]['max'] = max2
            avg2.append((sum(listReal) / args.num_stations))
            final_dict[bands]['avg'] = avg2
            final_dict[bands]['bytes_rd'] = listReal_bytes
            final_dict[bands]['speed'] = listReal_speed
            final_dict[bands]['url_times'] = listReal_urltimes
        else:
            if bands == "5G":
                list5G.extend(uc_avg_val)
                list5G_bytes.extend(rx_bytes_val)
                list5G_speed.extend(rx_rate_val)
                list5G_urltimes.extend(url_times)
                logger.info("%s %s %s %s", list5G, list5G_bytes, list5G_speed, list5G_urltimes)
                final_dict['5G']['dl_time'] = list5G
                min5.append(min(list5G))
                final_dict['5G']['min'] = min5
                max5.append(max(list5G))
                final_dict['5G']['max'] = max5
                avg5.append((sum(list5G) / args.num_stations))
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
                avg6.append((sum(list6G) / args.num_stations))
                final_dict['6G']['avg'] = avg6
                final_dict['6G']['bytes_rd'] = list6G_bytes
                final_dict['6G']['speed'] = list6G_speed
                final_dict['6G']['url_times'] = list6G_urltimes
            elif bands == "2.4G":
                list2G.extend(uc_avg_val)
                list2G_bytes.extend(rx_bytes_val)
                list2G_speed.extend(rx_rate_val)
                list2G_urltimes.extend(url_times)
                logger.info("%s %s %s", list2G, list2G_bytes, list2G_speed)
                final_dict['2.4G']['dl_time'] = list2G
                min2.append(min(list2G))
                final_dict['2.4G']['min'] = min2
                max2.append(max(list2G))
                final_dict['2.4G']['max'] = max2
                avg2.append((sum(list2G) / args.num_stations))
                final_dict['2.4G']['avg'] = avg2
                final_dict['2.4G']['bytes_rd'] = list2G_bytes
                final_dict['2.4G']['speed'] = list2G_speed
                final_dict['2.4G']['url_times'] = list2G_urltimes
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
                avg_both.append((sum(Both) / args.num_stations))
                final_dict['Both']['avg'] = avg_both
                final_dict['Both']['bytes_rd'] = Both_bytes
                final_dict['Both']['speed'] = Both_speed
                final_dict['Both']['url_times'] = Both_urltimes

    result_data = final_dict
    print("result", result_data)
    print("Test Finished")
    test_end = datetime.now()
    test_end = test_end.strftime("%Y %d %H:%M:%S")
    print("Test ended at ", test_end)
    s1 = test_time
    s2 = test_end  # for example
    FMT = '%Y %d %H:%M:%S'
    test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

    info_ssid = []
    info_security = []
    # For real clients
    if args.client_type == 'Real':
        info_ssid.append(args.ssid)
        info_security.append(args.security)
    else:
        for band in args.bands:
            if band == "2.4G":
                info_ssid.append(args.twog_ssid)
                info_security.append(args.twog_security)
            elif band == "5G":
                info_ssid.append(args.fiveg_ssid)
                info_security.append(args.fiveg_security)
            elif band == "6G":
                info_ssid.append(args.sixg_ssid)
                info_security.append(args.sixg_security)
            elif band == "Both":
                info_ssid.append(args.fiveg_ssid)
                info_security.append(args.fiveg_security)
                info_ssid.append(args.twog_ssid)
                info_security.append(args.twog_security)

    print("total test duration ", test_duration)
    date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    duration = args.duration
    if int(duration) < 60:
        duration = str(duration) + "s"
    elif int(duration == 60) or (int(duration) > 60 and int(duration) < 3600):
        duration = str(duration / 60) + "m"
    else:
        if int(duration == 3600) or (int(duration) > 3600):
            duration = str(duration / 3600) + "h"

    if args.client_type == "Real":
        if args.group_name:
            group_names = ', '.join(configuration.keys())
            profile_names = ', '.join(configuration.values())
            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
            test_setup_info = {
                "AP name": args.ap_name,
                "Configuration": configmap,
                "Configured Devices": ", ".join(all_devices_names),
                "No of Devices": "Total" + f"({args.num_stations})" + total_devices,
                "Traffic Direction": "Download",
                "Traffic Duration ": duration
            }
        else:
            test_setup_info = {
                "AP Name": args.ap_name,
                "SSID": ssid,
                "Device List": ", ".join(all_devices_names),
                "Security": security,
                "No of Devices": "Total" + f"({args.num_stations})" + total_devices,
                "Traffic Direction": "Download",
                "Traffic Duration ": duration
            }
    else:
        test_setup_info = {
            "AP Name": args.ap_name,
            "SSID": ssid,
            "Security": security,
            "No of Devices": args.num_stations,
            "Traffic Direction": "Download",
            "Traffic Duration ": duration
        }
    test_input_infor = {
        "LANforge ip": args.mgr,
        "Bands": args.bands,
        "Upstream": args.upstream_port,
        "Stations": args.num_stations,
        "SSID": ','.join(filter(None, info_ssid)) if info_ssid else "",
        "Security": ', '.join(filter(None, info_security)) if info_security else "",
        "Duration": args.duration,
        "Contact": "support@candelatech.com"
    }
    if not args.file_path:
        test_setup_info["File size"] = args.file_size
        test_setup_info["File location"] = "/usr/local/lanforge/nginx/html"
        test_input_infor["File size"] = args.file_size
    else:
        test_setup_info["File location (URLs from the File)"] = args.file_path
    # dataset = http.download_time_in_sec(result_data=result_data)
    rx_rate = []
    for i in result_data:
        dataset = result_data[i]['dl_time']
        dataset2 = result_data[i]['url_times']
        bytes_rd = result_data[i]['bytes_rd']
        rx_rate = result_data[i]['speed']
    dataset1 = [round(x / 1000000, 4) for x in bytes_rd]
    rx_rate = [round(x / 1000000, 4) for x in rx_rate]  # converting bps to mbps

    lis = []
    if bands == "Both":
        for i in range(1, args.num_stations * 2 + 1):
            lis.append(i)
    else:
        for i in range(1, args.num_stations + 1):
            lis.append(i)

    # dataset2 = http.speed_in_Mbps(result_data=result_data)

    # data = http.summary_calculation(
        # result_data=result_data,
        # bands=args.bands,
        # threshold_5g=args.threshold_5g,
        # threshold_2g=args.threshold_2g,
        # threshold_both=args.threshold_both)
    # summary_table_value = {
        # "": args.bands,
        # "PASS/FAIL": data
    # }
    http.generate_report(date, num_stations=args.num_stations,
                         duration=args.duration, test_setup_info=test_setup_info, dataset=dataset, lis=lis,
                         bands=args.bands, threshold_2g=args.threshold_2g, threshold_5g=args.threshold_5g,
                         threshold_both=args.threshold_both, dataset2=dataset2, dataset1=dataset1,
                         # summary_table_value=summary_table_value,
                         result_data=result_data, rx_rate=rx_rate,
                         test_rig=args.test_rig, test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                         dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                         dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                         test_input_infor=test_input_infor, csv_outfile=args.csv_outfile)
    http.postcleanup()
    # FOR WEBGUI, filling csv at the end to get the last terminal logs
    if args.dowebgui:
        http.data_for_webui["status"] = ["STOPPED"] * len(http.devices_list)
        http.data_for_webui["start_time"] = http.data["start_time"]
        http.data_for_webui["end_time"] = http.data["end_time"]
        http.data_for_webui["remaining_time"] = http.data["remaining_time"]
        df1 = pd.DataFrame(http.data_for_webui)
        df1.to_csv('{}/http_datavalues.csv'.format(http.result_dir), index=False)

        http.copy_reports_to_home_dir()


if __name__ == '__main__':
    main()
