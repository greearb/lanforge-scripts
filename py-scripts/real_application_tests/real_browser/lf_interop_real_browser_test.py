#!/usr/bin/env python3
"""
Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
    For now the test script supports Real Browser test for Androids and Laptops.

Pre-requisites: Real clients should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge

            Name: lf_interop_real_browser_test.py

            Example-1 :
            Command Line Interface to run url in the Browser with specified URL and duration:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --debug --upstream_port 1.1.eth1

                CASE-1:
                If not specified it takes the default url (default url is www.google.com)

            Example-2:
            Command Line Interface to run url in the Browser with specified Resources:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --debug --upstream_port 1.1.eth1

            Example-3:
            Command Line Interface to run url in the Browser with specified urls_per_tennm (specify the number of url you want to test in the given duration):
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --debug --upstream_port 1.1.eth1

                CASE-1:
                If not specified it takes the default count value (default count is 1)


            Example-4:
            Command Line Interface to run url in the Browser with precleanup:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --precleanup --debug --upstream_port 1.1.eth1

            Example-5:
            Command Line Interface to run url in the Browser with postcleanup:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --postcleanup --debug --upstream_port 1.1.eth1

            Example-4:
            Command Line Interface to run the Real Browser Test with Device Configuration
            python3 lf_interop_real_browser_test.py --mgr 192.168.204.74 --url "https://google.com" --duration 1m --debug --upstream_port 1.1.eth1
            --ssid NETGEAR_5G_wpa2 --passwd Password@123 --encryp wpa2 --config

            Example-5:
            Command Line Interface to run the Real Browser Test with groups and profiles
            python3 lf_interop_real_browser_test.py --mgr 192.168.204.74 --url "https://google.com" --duration 1m --debug --upstream_port 1.1.eth1
            --file_name grplaptops --group_name group1,group2 --profile_name netgear2g,netgear2g


            SCRIPT CLASSIFICATION: Test

            SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

            NOTES:
                1. Use './lf_interop_real_browser_test.py --help' to see command line usage and options.
                2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
                3. If --device_list are not given after passing the CLI, a list of available devices will be displayed on the terminal.
                4. Enter the resource numbers separated by commas (,) in the resource argument and also enclose in double quotes (e.g. : 1.10,1.12).
                5. For --url, you can specify the URL (e.g., www.google.com).
                6. To run the test by specifying the incremental capacity, enable the --incremental flag.

            STATUS: BETA RELEASE

            VERIFIED_ON:
            Working date - 29/07/2024
            Build version - 5.4.8
            kernel version - 6.2.16+

            License: Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2023 Candela Technologies Inc.



"""

import sys
import os
import importlib
import argparse
import time
import pandas as pd
import logging
import json
import shutil
import asyncio
from datetime import datetime, timedelta
# from lf_graph import lf_bar_graph_horizontal
from flask import Flask, request, jsonify
import threading
import csv
import re
import traceback
import requests


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import specific modules from custom paths using importlib
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
base = importlib.import_module('py-scripts.lf_base_interop_profile')
lf_csv = importlib.import_module("py-scripts.lf_csv")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
base_RealDevice = base.RealDevice
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report


lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph = lf_graph.lf_bar_graph
lf_scatter_graph = lf_graph.lf_scatter_graph
lf_bar_graph_horizontal = lf_graph.lf_bar_graph_horizontal
lf_line_graph = lf_graph.lf_line_graph
lf_stacked_graph = lf_graph.lf_stacked_graph
lf_horizontal_stacked_graph = lf_graph.lf_horizontal_stacked_graph

DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")
port_utils = importlib.import_module("py-json.port_utils")
PortUtils = port_utils.PortUtils

# Set up logging configuration for the script
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class RealBrowserTest(Realm):
    def __init__(self,
                 host,
                 ssid,
                 passwd,
                 encryp,
                 suporrted_release=None,
                 max_speed=None,
                 url=None,
                 count=None,
                 duration=None,
                 resource_ids=None,
                 dowebgui=False,
                 result_dir="",
                 test_name=None,
                 incremental=None,
                 postcleanup=False,
                 precleanup=False,
                 file_name=None,
                 group_name=None,
                 profile_name=None,
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
                 upstream_port=None,
                 device_csv_name=None,
                 expected_passfail_value=None,
                 wait_time=60,
                 config=None,
                 selected_groups=None,
                 selected_profiles=None):
        super().__init__(lfclient_host=host, lfclient_port=8080)
        # Initialize attributes with provided parameters
        self.host = host
        self.ssid = ssid
        self.report_ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        self.supported_release = suporrted_release
        self.max_speed = max_speed
        self.url = url
        self.count = count
        self.duration = duration
        self.resource_ids = resource_ids
        self.dowebgui = dowebgui
        self.result_dir = result_dir
        self.test_name = test_name
        self.incremental = incremental
        self.postCleanUp = postcleanup
        self.preCleanUp = precleanup
        self.direction = "dl"
        self.dest = "/dev/null"

        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.WARNING)
        self.laptop_stats = {}
        self.user_name = None
        self.hw = None
        self.mac_list = None
        self.csv_file_names = []
        self.stop_signal = False
        self.device_targets = {}
        self.mac = 0
        self.windows = 0
        self.linux = 0
        self.android = 0
        self.iteration_value = 0

        self.webui_hostnames = []
        self.webui_ostypes = []
        self.webui_devices = None
        self.hostname_os_combination = None
        self.stop_mobile_cx = True

        # Initialize additional attributes
        self.adb_device_list = None
        self.phn_name = []
        self.device_name = []
        self.android_devices = []
        self.other_os_list = []
        self.android_list = []
        self.other_list = []
        self.real_sta_data_dict = {}
        self.ip_map = {}
        self.health = None
        self.phone_data = None
        self.max_speed = 0  # infinity
        self.quiesce_after = 0  # infinity
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'real_browser'
        self.generic_endps_profile.name_prefix = "rb"
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
        self.upstream_port = upstream_port
        self.expected_passfail_value = expected_passfail_value
        self.device_csv_name = device_csv_name
        self.wait_time = wait_time
        self.config = config
        self.selected_groups = selected_groups
        self.selected_profiles = selected_profiles
        self.config_obj = None
        # Initialize RealDevice instance
        self.devices = base_RealDevice(manager_ip=self.host, selected_bands=[])
        # Initialize local realm
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=8080)
        self.port_util = PortUtils(self.local_realm)
        # Initialize HTTP profile for testing
        self.http_profile = self.local_realm.new_http_profile()
        # Initialize interoperability instance for WiFi testing
        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=8080,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        # Initialize utility
        self.utility = base.UtilityInteropWifi(host_ip=self.host)

    def build(self):
        """
            If the pre-requisites are satisfied, this function gets the list of real devices connected to LANforge
            and processes them for Layer 4-7 traffic profile creation.
        """

        # # Initialize dictionaries and lists for data storage
        self.data = {}
        self.total_urls_dict = {}
        self.data_for_webui = {}
        self.all_cx_list = []
        self.prev_data = []
        self.present_data = []

        # Initialize lists for required parameters
        self.req_total_urls = []
        self.req_urls_per_sec = []
        self.req_uc_min_val = []
        self.req_uc_avg_val = []
        self.req_uc_max_val = []
        self.req_total_err = []
        self.device_type = []
        self.username = []
        self.ssid = []

        self.mode = []
        self.rssi = []
        self.channel = []
        self.tx_rate = []
        self.time_data = []
        self.temp = []
        self.total_duration = ""
        self.formatted_endtime_str = ""
        self.test_setup_info_incremental_values = None

        # Retrieve resource data for phones
        self.phone_data, self.laptops, self.laptop_os_types, self.user_name, self.mac_list = self.get_resource_data()

        self.direction = 'dl'
        self.dest = '/dev/null'
        self.max_speed = self.max_speed
        self.requests_per_ten = 100
        self.created_cx = self.http_profile.created_cx = self.convert_to_dict(self.phone_data)
        if self.preCleanUp:
            self.precleanup()
        self.http_profile.created_cx.clear()

        self.new_port_list = [item.split('.')[2] for item in self.laptops]

        if (self.generic_endps_profile.create(ports=self.laptops, sleep_time=.5, real_client_os_types=self.laptop_os_types,)):

            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        for i in range(0, len(self.laptop_os_types)):
            if self.laptop_os_types[i] == 'windows':
                cmd = "real_browser.bat --url %s --server %s --duration %s" % (self.url, self.upstream_port, self.duration)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.laptop_os_types[i] == 'linux':
                cmd = "su -l lanforge  ctrb.bash %s %s %s %s" % (self.new_port_list[i], self.url, self.upstream_port, self.duration)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.laptop_os_types[i] == 'macos':
                cmd = "sudo bash ctrb.bash --url %s --server %s  --duration %s" % (self.url, self.upstream_port, self.duration)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

        if len(self.phone_data) != 0:
            logging.info("Creating Layer-4 endpoints from the user inputs as test parameters")
            upload_name = self.phone_data[-1].split('.')[-1]

            if 'https' in self.url:
                self.url = self.url.replace("http://", "").replace("https://", "")
                self.create_real(ports=self.phone_data, sleep_time=.5,
                                 suppress_related_commands_=None, https=True,
                                 https_ip=self.url, interop=True, timeout=1000, media_source='1', media_quality='0', upload_name=upload_name)
            elif 'http' in self.url:
                self.url = self.url.replace("http://", "").replace("https://", "")
                self.create_real(ports=self.phone_data, sleep_time=.5,
                                 suppress_related_commands_=None, http=True,
                                 http_ip=self.url, interop=True, timeout=1000, media_source='1', media_quality='0', upload_name=upload_name)

            else:
                self.create_real(ports=self.phone_data, sleep_time=.5,
                                 suppress_related_commands_=None, real=True,
                                 http_ip=self.url, interop=True, timeout=1000, media_source='1', media_quality='0', upload_name=upload_name)

    def map_sta_ips_real(self, sta_list=None):
        if sta_list is None:
            sta_list = []
        for sta_eid in sta_list:
            eid = self.name_to_eid(sta_eid)
            sta_list = self.json_get("/port/%s/%s/%s?fields=alias,ip" % (eid[0], eid[1], eid[2]))
            if sta_list['interface'] is not None:
                eid_key = "{eid0}.{eid1}.{eid2}".format(eid0=eid[0], eid1=eid[1], eid2=eid[2])
                self.ip_map[eid_key] = sta_list['interface']['ip']

    def create_real(self, ports=None, sleep_time=.5, debug_=False, suppress_related_commands_=None, http=False, ftp=False, real=False,
                    https=False, user=None, passwd=None, source=None, ftp_ip=None, upload_name=None, http_ip=None,
                    https_ip=None, interop=None, media_source=None, media_quality=None, timeout=10, proxy_auth_type=0x2200, windows_list=[], get_url_from_file=False):
        if ports is None:
            ports = []
        cx_post_data = []
        self.map_sta_ips_real(ports)
        logger.info("Create HTTP CXs..." + __name__)

        for i in range(len(list(self.ip_map))):
            url = None
            if i != len(list(self.ip_map)) - 1:
                port_name = list(self.ip_map)[i]
                ip_addr = self.ip_map[list(self.ip_map)[i + 1]]
            else:
                port_name = list(self.ip_map)[i]
                ip_addr = self.ip_map[list(self.ip_map)[0]]

            if (ip_addr is None) or (ip_addr == ""):
                raise ValueError("HTTPProfile::create encountered blank ip/hostname")
            if interop:
                if list(self.ip_map)[i] in windows_list:
                    self.dest = 'NUL'
                if list(self.ip_map)[i] not in windows_list:
                    self.dest = '/dev/null'

            rv = self.local_realm.name_to_eid(port_name)
            '''
            shelf = self.local_realm.name_to_eid(port_name)[0]
            resource = self.local_realm.name_to_eid(port_name)[1]
            name = self.local_realm.name_to_eid(port_name)[2]
            '''
            shelf = rv[0]
            resource = rv[1]
            name = rv[2]

            if upload_name is not None:
                name = upload_name

            if http:
                if http_ip is not None:
                    if get_url_from_file:
                        self.port_util.set_http(port_name=name, resource=resource, on=True)
                        url = "%s %s %s" % ("", http_ip, "")
                        logger.info("HTTP url:{}".format(url))
                    else:
                        self.port_util.set_http(port_name=name, resource=resource, on=True)
                        url = "%s http://%s %s" % (self.direction, http_ip, self.dest)
                        logger.info("HTTP url:{}".format(url))
                else:
                    self.port_util.set_http(port_name=name, resource=resource, on=True)
                    url = "%s http://%s/ %s" % (self.direction, ip_addr, self.dest)
                    logger.info("HTTP url:{}".format(url))
            if https:
                if https_ip is not None:
                    self.port_util.set_http(port_name=name, resource=resource, on=True)
                    url = "%s https://%s %s" % (self.direction, https_ip, self.dest)
                else:
                    self.port_util.set_http(port_name=name, resource=resource, on=True)
                    url = "%s https://%s/ %s" % (self.direction, ip_addr, self.dest)

            if real:
                if http_ip is not None:
                    if get_url_from_file:
                        self.port_util.set_http(port_name=name, resource=resource, on=True)
                        url = "%s %s %s" % ("", http_ip, "")
                        logger.info("HTTP url:{}".format(url))
                    else:
                        self.port_util.set_http(port_name=name, resource=resource, on=True)
                        url = "%s %s %s" % (self.direction, http_ip, self.dest)
                        logger.info("HTTP url:{}".format(url))
                else:
                    self.port_util.set_http(port_name=name, resource=resource, on=True)
                    url = "%s %s/ %s" % (self.direction, ip_addr, self.dest)
                    logger.info("HTTP url:{}".format(url))

            if ftp:
                self.port_util.set_ftp(port_name=name, resource=resource, on=True)
                if user is not None and passwd is not None and source is not None:
                    if ftp_ip is not None:
                        ip_addr = ftp_ip
                    url = "%s ftp://%s:%s@%s%s %s" % (self.direction, user, passwd, ip_addr, source, self.dest)
                    logger.info("###### url:{}".format(url))
                else:
                    raise ValueError("user: %s, passwd: %s, and source: %s must all be set" % (user, passwd, source))
            if not http and not ftp and not https and not real:
                raise ValueError("Please specify ftp and/or http")

            if (url is None) or (url == ""):
                raise ValueError("HTTPProfile::create: url unset")
            if ftp:
                cx_name = name + "_ftp"
            else:

                cx_name = name + "_http"

            if interop is None:
                if upload_name is None:
                    endp_data = {
                        "alias": cx_name + "_l4",
                        "shelf": shelf,
                        "resource": resource,
                        "port": name,
                        "type": "l4_generic",
                        "timeout": timeout,
                        "url_rate": self.requests_per_ten,
                        "url": url,
                        "proxy_auth_type": 0x200,
                        "quiesce_after": self.quiesce_after,
                        "max_speed": self.max_speed
                    }
                else:
                    endp_data = {
                        "alias": cx_name + "_l4",
                        "shelf": shelf,
                        "resource": resource,
                        # "port": ports[0],
                        "port": rv[2],
                        "type": "l4_generic",
                        "timeout": timeout,
                        "url_rate": self.requests_per_ten,
                        "url": url,
                        "ssl_cert_fname": "ca-bundle.crt",
                        "proxy_port": 0,
                        "max_speed": self.max_speed,
                        "proxy_auth_type": 0x200,
                        "quiesce_after": self.quiesce_after
                    }
                set_endp_data = {
                    "alias": cx_name + str(resource) + "_l4",
                    "media_source": media_source,
                    "media_quality": media_quality,
                    # "media_playbacks":'0'
                }
                url = "cli-json/add_l4_endp"
                self.json_post(url, endp_data, debug_=debug_,
                               suppress_related_commands_=suppress_related_commands_)
                time.sleep(sleep_time)
                # If media source and media quality is given then this code will set media source and media quality for CX
                if media_source and media_quality:
                    url1 = "cli-json/set_l4_endp"
                    self.json_post(url1, set_endp_data, debug_=debug_,
                                   suppress_related_commands_=suppress_related_commands_)

                endp_data = {
                    "alias": "CX_" + cx_name + "_l4",
                    "test_mgr": "default_tm",
                    "tx_endp": cx_name + "_l4",
                    "rx_endp": "NA"
                }
                cx_post_data.append(endp_data)
                self.created_cx[cx_name + "_l4"] = "CX_" + cx_name + "_l4"
            else:  # If Interop is enabled then this code will work
                if upload_name is None:
                    endp_data = {
                        "alias": cx_name + str(resource) + "_l4",
                        "shelf": shelf,
                        "resource": resource,
                        "port": name,
                        "type": "l4_generic",
                        "timeout": timeout,
                        "url_rate": self.requests_per_ten,
                        "url": url,
                        "proxy_auth_type": proxy_auth_type,
                        "quiesce_after": self.quiesce_after,
                        "max_speed": self.max_speed
                    }
                else:
                    endp_data = {
                        "alias": cx_name + str(resource) + "_l4",
                        "shelf": shelf,
                        "resource": resource,
                        # "port": ports[0],
                        "port": rv[2],
                        "type": "l4_generic",
                        "timeout": timeout,
                        "url_rate": self.requests_per_ten,
                        "url": url,
                        "ssl_cert_fname": "ca-bundle.crt",
                        "proxy_port": 0,
                        "max_speed": self.max_speed,
                        "proxy_auth_type": proxy_auth_type,
                        "quiesce_after": self.quiesce_after
                    }
                set_endp_data = {
                    "alias": cx_name + str(resource) + "_l4",
                    "media_source": media_source,
                    "media_quality": media_quality,
                    # "media_playbacks":'0'
                }
                url = "cli-json/add_l4_endp"
                self.json_post(url, endp_data, debug_=debug_,
                               suppress_related_commands_=suppress_related_commands_)
                time.sleep(sleep_time)
                # If media source and media quality is given then this code will set media source and media quality for CX
                if media_source and media_quality:
                    url1 = "cli-json/set_l4_endp"
                    self.json_post(url1, set_endp_data, debug_=debug_,
                                   suppress_related_commands_=suppress_related_commands_)

                endp_data = {  # Added resource id to alias and End point name as all real clients have same name(wlan0)
                    "alias": "CX_" + cx_name + str(resource) + "_l4",
                    "test_mgr": "default_tm",
                    "tx_endp": cx_name + str(resource) + "_l4",
                    "rx_endp": "NA"
                }
                cx_post_data.append(endp_data)
                self.created_cx[cx_name + str(resource) + "_l4"] = "CX_" + cx_name + str(resource) + "_l4"
        self.http_profile.created_cx = self.created_cx

        for cx_data in cx_post_data:
            url = "/cli-json/add_cx"
            self.json_post(url, cx_data, debug_=debug_,
                           suppress_related_commands_=suppress_related_commands_)
            time.sleep(sleep_time)

        # enabling geturl from file for each endpoint
        if get_url_from_file:
            for cx in list(self.created_cx.keys()):
                self.json_post("/cli-json/set_endp_flag", {"name": cx,
                                                           "flag": "GetUrlsFromFile",
                                                           "val": 1
                                                           }, suppress_related_commands_=True)

    def convert_to_dict(self, input_list):
        """
            Creating dictionary for devices for pre_cleanup
        """
        output_dict = {}

        for item in input_list:
            parts = item.split('.')
            device = parts[2]
            key = f"{device}_http{parts[1]}_l4"
            value = f"CX_{device}_http{parts[1]}_l4"
            output_dict[key] = value

        return output_dict

    def get_incremental_capacity_list(self):
        keys = list(self.created_cx.keys())
        generic_keys = self.generic_endps_profile.created_cx
        keys = keys + generic_keys
        incremental_temp = []
        created_incremental_values = []
        index = 0
        if len(self.incremental) == 1 and self.incremental[0] == len(keys):
            incremental_temp.append(len(keys[index:]))
        elif len(self.incremental) == 1 and len(keys) > 1:
            incremental_value = self.incremental[0]
            div = len(keys) // incremental_value
            mod = len(keys) % incremental_value

            for i in range(div):
                if len(incremental_temp):
                    incremental_temp.append(incremental_temp[-1] + incremental_value)
                else:
                    incremental_temp.append(incremental_value)

            if mod:
                incremental_temp.append(incremental_temp[-1] + mod)
            created_incremental_values = incremental_temp

        if not created_incremental_values:
            created_incremental_values = self.incremental
        return created_incremental_values

    def start(self):
        # Starts the layer 4-7 traffic for created CX end points
        """
            Starts the layer 4-7 traffic for created CX endpoints.

            This method performs the following actions:
            1. Sets the CX state to 'Running'.
            2. Waits for each CX endpoint to reach the 'Running' state.
        """
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logging.info("Setting Cx State to Runnning")
        # Start the CX for HTTP profile
        self.http_profile.start_cx()
        self.generic_endps_profile.start_cx()
        try:
            # Loop through each CX endpoint and wait until it reaches the 'Run' state
            for i in self.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            logging.info(e)
            pass

    def start_specific(self, cx_start_list):
        """
            Starts the layer 4-7 traffic for specific CX endpoints.

            Parameters:
            - cx_start_list (list): List of CX endpoints to start.

            performs the following actions:
            1. Starts the specified CX endpoints using the provided list.
            2. Sets the CX state to 'Running' for each specified CX endpoint.
        """
        # Start specific CX endpoints using the provided list
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        logger.info("Starting CXs...")
        for cx_name in cx_start_list:
            cx_name = cx_name.strip()

            if "http" in cx_name:

                self.json_post("/cli-json/set_cx_state", {
                    "test_mgr": "default_tm",
                    "cx_name": self.http_profile.created_cx[cx_name],
                    "cx_state": "RUNNING"
                }, debug_=self.debug)
            else:
                self.json_post("/cli-json/set_cx_state", {
                    "test_mgr": "default_tm",
                    "cx_name": cx_name,
                    "cx_state": "RUNNING"
                }, debug_=self.debug)

    def stop(self):
        """
            Stops the layer 4-7 traffic for created CX endpoints.
            Stops the generic cross connections
        """
        self.http_profile.stop_cx()
        self.generic_endps_profile.stop_cx()
        self.stop_signal = True
        time.sleep(10)

    def precleanup(self):
        self.http_profile.cleanup()
        self.generic_endps_profile.cleanup()

    def postcleanup(self):
        self.http_profile.cleanup()
        self.generic_endps_profile.cleanup()

    def set_available_resources_ids(self, available_list):
        self.resource_ids = available_list

    def get_resource_data(self):
        """
            Retrieves data for Real devices connected to LANforge.

            Returns:
            - station_name (list): List of station names corresponding to the Real devices connected to LANforge.

            This method performs the following actions:
            1. Retrieves information about LANforge ports including alias, MAC address, mode, parent device, RX rate, TX rate,
            SSID, and signal strength.
            2. If self.resource_ids is provided, converts it into a list of integers.
            3. Iterates through the retrieved data to extract relevant information for devices connected to WLAN (alias 'wlan0').
            4. Filters and collects station names based on specific criteria, appending them to 'station_name'.
            5. Returns 'station_name', a list containing station names of Real devices connected to LANforge.
        """
        # Gets the list of Real devices connected to LANforge
        resource_id_list = []
        mac_address = []
        user_name = []
        station_name = []
        laptops = []
        laptop_os_types = []
        ssid = []

        webui_android = 0
        webui_windows = 0
        webui_linux = 0
        webui_mac = 0

        # Retrieve data from LANforge port Manager tab including alias, MAC address, mode, parent device, RX rate, TX rate, SSID, and signal strength
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,ssid,signal,phantom,down,ip")
        resource_ids = []
        if self.resource_ids:

            resource_ids = list(map(int, self.resource_ids.split(',')))

        for item in resource_ids:
            item = str(item)

            for alias in eid_data["interfaces"]:
                for i in alias:

                    resource_id = i.split('.')[1]
                    if resource_id == item:

                        resource_id_list.append(i.split(".")[1])
                        resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        # Check if the hardware version does not start with ('Win', 'Linux', 'Apple') and the resource ID is in resource_ids
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and alias[i]["parent dev"] == 'wiphy0' and not alias[i]["down"] and alias[i]['ip'] != '0.0.0.0':
                            station_name.append(i)
                            mac_address.append(alias[i].get("mac", "NA"))
                            ssid.append(alias[i].get("ssid", "NA"))
                            user_name.append(resource_hw_data['resource'].get('user', 'NA'))
                            self.webui_hostnames.append(resource_hw_data['resource'].get('user', 'NA'))
                            self.webui_ostypes.append("Android")
                            webui_android += 1

                        elif hw_version.startswith('Win') and alias[i]["parent dev"] == 'wiphy0' and not alias[i]["down"] and alias[i]['ip'] != '0.0.0.0':
                            laptops.append(i)
                            laptop_os_types.append("windows")
                            mac_address.append(alias[i].get("mac", "NA"))
                            ssid.append(alias[i].get("ssid", "NA"))
                            # user_name.append(resource_hw_data['resource'].get('user', 'NA'))
                            self.webui_hostnames.append(resource_hw_data['resource'].get('hostname', 'NA'))
                            self.webui_ostypes.append("windows")
                            webui_windows += 1

                        elif hw_version.startswith('Linux') and alias[i]["parent dev"] == 'wiphy0' and not alias[i]["down"] and alias[i]['ip'] != '0.0.0.0':
                            laptops.append(i)
                            laptop_os_types.append("linux")
                            mac_address.append(alias[i].get("mac", "NA"))
                            ssid.append(alias[i].get("ssid", "NA"))
                            # user_name.append(resource_hw_data['resource'].get('user', 'NA'))
                            self.webui_hostnames.append(resource_hw_data['resource'].get('hostname', 'NA'))
                            self.webui_ostypes.append("Linux")
                            webui_linux += 1
                        elif hw_version.startswith('Apple') and alias[i]["parent dev"] == 'wiphy0' and not alias[i]["down"] and alias[i]['ip'] != '0.0.0.0':
                            laptops.append(i)
                            laptop_os_types.append("macos")
                            mac_address.append(alias[i].get("mac", "NA"))
                            ssid.append(alias[i].get("ssid", "NA"))
                            # user_name.append(resource_hw_data['resource'].get('user', 'NA'))
                            self.webui_hostnames.append(resource_hw_data['resource'].get('hostname', 'NA'))
                            self.webui_ostypes.append("Mac")
                            webui_mac += 1
        self.webui_devices = f'Total({len(self.webui_ostypes)}) : A({webui_android}), W({webui_windows}),L({webui_linux}),M({webui_mac})'
        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.webui_hostnames, self.webui_ostypes)
        ]

        for os_type in self.webui_ostypes:
            if os_type == "windows":
                self.windows = self.windows + 1
            elif os_type == "Linux":
                self.linux = self.linux + 1
            elif os_type == "Mac":
                self.mac = self.mac + 1
            elif os_type == "Android":
                self.android = self.android + 1

        return station_name, laptops, laptop_os_types, user_name, mac_address,

    def start_flask_server(self):

        @self.app.route('/stop_rb', methods=['GET'])
        def stop_rb():
            logging.info("Stopping the test through WEB GUI")
            response = jsonify({"message": "Stopping Zoom Test"})
            response.status_code = 200
            self.stop()

            def shutdown():
                os._exit(0)
            response.call_on_close(shutdown)
            return response

        @self.app.route('/upload_stats', methods=['POST'])
        def upload_stats():
            temp_data = request.get_json()
            for hostname, stats in temp_data.items():
                self.laptop_stats[hostname] = stats
            return jsonify({"status": "success"}), 200

        # New route to check the health of the Flask server
        @self.app.route('/check_health', methods=['GET'])
        def check_health():
            return jsonify({"status": "healthy"}), 200

        @self.app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        try:
            self.app.run(host='0.0.0.0', port=5003, debug=True, threaded=True, use_reloader=False)

        except Exception as e:
            logging.info(f"Error starting Flask server: {e}")
            sys.exit(0)

    def run_flask_server(self):

        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        self.wait_for_flask()

    def check_gen_cx(self):
        """
        Check if all endpoints have a status of 'Stopped' or 'WAITING'.

        Returns:
            bool: True if all endpoints are either 'Stopped' or 'WAITING', False otherwise.
        """
        for gen_endp in self.generic_endps_profile.created_endp:
            generic_endpoint = self.json_get(f'/generic/{gen_endp}')
            if not generic_endpoint or "endpoint" not in generic_endpoint:
                logging.info(f"Error fetching endpoint data for {gen_endp}")
                return False  # Handle case where endpoint data is not available
            endp_status = generic_endpoint["endpoint"].get("status", "")
            # If the endpoint status is not 'Stopped' or 'WAITING', return False
            if endp_status not in ["Stopped", "WAITING"]:
                return False
        # If all endpoints are in 'Stopped' or 'WAITING', return True
        return True

    def update_webui_json(self):
        """
        Update web GUI status based on available devices.
        Returns True if execution should continue, False if it should exit.
        """
        if self.dowebgui:
            if len(self.webui_hostnames) == 0:
                logging.info("No device is available to run the test")
                data_obj = {
                    "status": "Stopped",
                    "configuration_status": "configured"
                }
                self.updating_webui_runningjson(data_obj)
                return False
            else:
                data_obj = {
                    "configured_devices": self.webui_hostnames,
                    "configuration_status": "configured",
                    "no_of_devices": self.webui_devices,
                    "device_list": self.hostname_os_combination,
                }
                self.updating_webui_runningjson(data_obj)
        return True

    def process_incremental_values(self, available_resources):
        """
        Process resource IDs and incremental values if specified.
        """
        if self.incremental or self.dowebgui:
            incremental_capacity_list_values = self.get_incremental_capacity_list()
            if incremental_capacity_list_values[-1] != len(available_resources):
                logger.error("Incremental capacity doesn't match available devices")
                if self.postCleanUp:
                    self.postcleanup()
                exit(1)

        if self.resource_ids:
            if self.incremental:
                self.test_setup_info_incremental_values = ','.join(map(str, incremental_capacity_list_values))
                if len(self.incremental) == len(available_resources):
                    self.total_duration = self.duration
                elif len(self.incremental) == 1 and len(available_resources) > 1:
                    div, mod = divmod(len(available_resources), self.incremental[0])
                    self.total_duration = self.duration * (div + (1 if mod else 0))
                else:
                    self.total_duration = self.duration * len(incremental_capacity_list_values)
            elif self.dowebgui:
                self.test_setup_info_incremental_values = ','.join(map(str, incremental_capacity_list_values))
                self.total_duration = self.duration * len(incremental_capacity_list_values)
            else:
                self.test_setup_info_incremental_values = "No Incremental Value provided"
                self.total_duration = self.duration

    def handle_duration(self):
        """
        Convert duration string to minutes.
        """
        if isinstance(self.duration, str):
            if self.duration.endswith(('s', 'S')):
                self.duration = round(int(self.duration[:-1]) / 60, 2)
            elif self.duration.endswith(('m', 'M')):
                self.duration = int(self.duration[:-1])
            elif self.duration.endswith(('h', 'H')):
                self.duration = int(self.duration[:-1]) * 60
            else:
                self.duration = int(self.duration)

    def run_test(self, available_resources):
        """
        Runs the test with calculated parameters.
        """
        logging.info("Initiating Test...")
        available_resources.sort()
        self.set_available_resources_ids(",".join(map(str, available_resources)))
        self.build()
        self.process_incremental_values(available_resources)
        if not self.update_webui_json():
            sys.exit(1)

        cx_order_list = self.calculate_cx_order_list()

        for i, cx_batch in enumerate(cx_order_list):
            self.start_specific(cx_batch)
            logging.info(f"Test started on Devices with resource Ids : {cx_batch}")
            try:
                self.get_stats(self.duration, "webBrowser.csv", i, available_resources, cx_batch, i, self.count)
            except Exception as e:
                logging.error(f"Error while monitoring stats {e}", exc_info=True)

    def calculate_cx_order_list(self):
        """
        Calculate and manage cx_order_list (list of cross connections to run) based on incremental values.
        """
        cx_order_list = []
        keys = list(self.created_cx.keys()) + self.generic_endps_profile.created_cx
        index = 0

        if self.resource_ids:
            if not self.incremental:
                self.incremental = [len(keys)]

            if len(self.incremental) == 1 and self.incremental[0] == len(keys):
                cx_order_list.append(keys[index:])
            elif len(self.incremental) == 1 and len(keys) > 1:
                incremental_value = self.incremental[0]
                max_index = len(keys)
                while index < max_index:
                    next_index = min(index + incremental_value, max_index)
                    cx_order_list.append(keys[index:next_index])
                    index = next_index
            else:
                for num in self.incremental:
                    cx_order_list.append(keys[index:num])
                    index = num
                if index < len(keys):
                    cx_order_list.append(keys[index:])

        return cx_order_list

    def validate_and_process_args(self):
        """
        Processes and validates the provided arguments.
        Returns:
            selected_groups (list): List of groups parsed from args.group_name.
            selected_profiles (list): List of profiles parsed from args.profile_name.
        """
        # Process group_name and profile_name into lists
        if self.group_name:
            self.group_name = self.group_name.strip()
            self.selected_groups = self.group_name.split(',')
        else:
            self.selected_groups = []

        if self.profile_name:
            self.profile_name = self.profile_name.strip()
            self.selected_profiles = self.profile_name.split(',')
        else:
            self.selected_profiles = []

        # Validation checks
        if self.expected_passfail_value and self.device_csv_name:
            logging.error("Specify either expected_passfail_value or device_csv_name")
            os._exit(1)

        if len(self.selected_groups) != len(self.selected_profiles):
            logging.error("Number of groups should match number of profiles")
            os._exit(1)

        if self.group_name and self.profile_name and self.file_name and self.resource_ids:
            logging.error("Either group name or device list should be entered not both")
            os._exit(1)

        if self.ssid and self.profile_name:
            logging.error("Either ssid or profile name should be given")
            exit(1)

        if self.file_name and (self.group_name is None or self.profile_name is None):
            logging.error("Please enter the correct set of arguments")
            os._exit(1)

        if self.config and ((self.ssid is None or
                            (self.passwd is None and self.encryp and self.encryp.lower() != 'open') or
                            (self.passwd is None and self.encryp is None))):
            logging.error("Please provide ssid password and security for configuration of devices")
            os._exit(1)

        if self.file_name:
            self.file_name = self.file_name.removesuffix(".csv")
        else:
            self.file_name = None

    def process_group_profiles(self):
        """
        Process group and profile names and update the device_list in args if provided.
        """
        if self.group_name and self.file_name and self.profile_name:
            config_devices = {}
            for i in range(len(self.selected_groups)):
                config_devices[self.selected_groups[i]] = self.selected_profiles[i]
            self.config_obj.initiate_group()
            config_list = asyncio.run(self.config_obj.connectivity(config_devices, upstream=self.upstream_port))
            resource_ids = sorted(set(int(item.split('.')[1]) for item in config_list if '.' in item))
            return resource_ids

    def process_resources(self, config_dict):
        """
        Processes resource IDs and returns:
            available_resources (list): List of available resource IDs (integers)
            resource_list_sorted (list): Sorted list of resource IDs (as strings)
            resource_ids_generated (str): Resource IDs joined as a comma-separated string
        """
        available_resources = []

        # Web GUI Mode: Extract and sort resources from the given device list
        if self.dowebgui and self.group_name:
            resource_list = sorted(set(self.resource_ids.split(',')))
            resource_ids_generated = ','.join(resource_list)

            # Query additional device info using webgui
            selected_devices, report_labels, selected_macs = self.devices.query_user(
                dowebgui=self.dowebgui, device_list=resource_ids_generated)

            self.resource_ids = ",".join(id.split(".")[1] for id in self.resource_ids.split(","))
            available_resources = sorted(set(int(num) for num in self.resource_ids.split(',')))

        else:
            # Fetch all available devices
            all_devices = self.config_obj.get_all_devices()

            # If device_list is provided, process it
            if self.resource_ids:
                device_list = self.resource_ids.split(',')

                # Establish connectivity if required
                if self.config:
                    _ = asyncio.run(self.config_obj.connectivity(device_list=device_list, wifi_config=config_dict))

                # Extract resource IDs and filter them
                self.devices = self.devices.get_devices()
                resource_ids = sorted(set(int(item.split('.')[1]) for item in device_list if '.' in item))
                available_resources = [res_id for res_id in resource_ids if any(
                    int(device.split('.')[1]) == res_id for device in self.devices if '.' in device
                )]

            else:
                # Display available devices for manual selection
                if self.config:
                    device_info_list = [
                        f"{device['shelf']}.{device['resource']} {device.get('serial', device.get('hostname', 'Unknown'))}"
                        for device in all_devices
                    ]

                    for device in device_info_list:
                        print(device)

                    # Get user input for selecting resources
                    self.resource_ids = input("Enter the desired resources to run the test (comma-separated, e.g., 1.10,1.12): ")
                    device_list = self.resource_ids.split(',')
                else:
                    self.devices.get_devices()
                    self.resource_ids, _, _ = self.devices.query_user()
                    device_list = self.resource_ids

                # Establish connectivity if required
                if self.config:
                    _ = asyncio.run(self.config_obj.connectivity(device_list=device_list, wifi_config=config_dict))

                self.devices = self.devices.get_devices()
                resource_ids = sorted(set(int(item.split('.')[1]) for item in device_list if '.' in item))
                # obj.resource_ids = ','.join(map(str, resource_ids))

                available_resources = [res_id for res_id in resource_ids if any(
                    int(device.split('.')[1]) == res_id for device in self.devices if '.' in device
                )]

        return available_resources

    def update_passfail_value(self, available_resources):
        """
        If no expected_passfail_value and no device_csv_name provided, ask for expected values
        and update the device CSV.
        """
        if len(available_resources) == 0:
            logging.info("There are no devices available which are selected")
            exit()
        device_map = {}
        if (not self.expected_passfail_value) and (self.device_csv_name is None):
            expected_val = input("Enter the expected value for the following devices {} eg 8,6,2: ".format(available_resources)).split(',')
            if len(available_resources) == len(expected_val):
                for i in range(len(available_resources)):
                    # Using the first two parts (shelf.resource) as key from android_list
                    key = self.android_list[i].split('.')[0] + '.' + self.android_list[i].split('.')[1]
                    device_map[key] = expected_val[i]
                self.config_obj.update_device_csv('device.csv', 'RealBrowser URLcount', device_map)
            else:
                logging.error("Enter correct number of values")
                exit(0)

    def handle_incremental(self, args, obj, available_resources, resource_list_sorted):
        """
        Process incremental values from user input or args.
        """
        if args.incremental and not args.webgui_incremental:
            if obj.resource_ids:
                inc_input = input('Specify incremental values as 1,2,3 : ')
                obj.incremental = [int(x) for x in inc_input.split(',')]
            else:
                logging.info("Incremental values are not needed as Android devices are not selected.")
        if args.webgui_incremental:
            if args.webgui_incremental == "no_increment":
                args.webgui_incremental = str(len(available_resources))
            incremental = [int(x) for x in args.webgui_incremental.split(',')]
            # Validate length and assign incremental values
            if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
                obj.incremental = incremental
            elif len(args.webgui_incremental) == 1:
                obj.incremental = incremental
        if (obj.incremental and obj.resource_ids) or args.webgui_incremental:
            # Check if the last incremental value is valid
            if obj.incremental[-1] > len(available_resources):
                logging.info("Exiting the program as incremental values are greater than the resource ids provided")
                exit()
            elif obj.incremental[-1] < len(available_resources) and len(obj.incremental) > 1:
                logging.info("Exiting the program as the last incremental value must be equal to selected devices")
                exit()

    def wait_for_flask(self, url="http://127.0.0.1:5003/check_health", timeout=10):
        """Wait until the Flask server is up, but exit if it takes longer than `timeout` seconds."""
        start_time = time.time()  # Record the start time
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    logging.info("✅ Flask server is up and running!")
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        logging.error("❌ Flask server did not start within 10 seconds. Exiting.")
        sys.exit(1)

    def get_stats(self, duration, file_path, iteration_number, resource_list_sorted, cx_order_list, i, initial_target_urls):

        try:
            test_time = timedelta(minutes=duration)
            end_time = datetime.now() + test_time
            est_end_time = end_time + timedelta(minutes=1)
            logging.info(f"End time of the Test {end_time}")
            logging.info(f"Estimated End time of the Test {est_end_time}")
            headers = ['device_type', 'device_name', 'total_urls', 'uc_min', 'uc_avg', 'uc_max', 'total_err', 'time_to_target_urls', 'cx_name']
            last_data = []
            mobile_data = {}
            time_taken = {}
            self.original_dir = os.getcwd()
            if self.dowebgui:
                os.chdir(self.result_dir)

            start_time = datetime.now()
            while datetime.now() <= end_time or not self.check_gen_cx():
                try:

                    if datetime.now() > est_end_time:
                        break
                    if datetime.now() > end_time and self.stop_mobile_cx:
                        self.http_profile.stop_cx()
                        self.stop_mobile_cx = False
                    last_data = []
                    with open('real_time_data.csv', mode='w', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=headers)
                        writer.writeheader()
                        if self.laptop_stats is not None:
                            for laptop, stats in self.laptop_stats.items():
                                if laptop not in self.device_targets:
                                    self.device_targets[laptop] = initial_target_urls
                                # Check if the device reaches the current target URL count
                                if stats.get('total_urls', 0) >= self.device_targets[laptop] and laptop not in time_taken:
                                    time_taken[laptop] = (datetime.now() - datetime.fromisoformat(stats.get("start_time", start_time.isoformat()))).total_seconds()
                                row = {
                                    'device_type': 'laptop',
                                    'device_name': stats.get('name', 'NA'),
                                    'total_urls': stats.get('total_urls', 0),
                                    'uc_min': stats.get('uc_min', 0.0),
                                    'uc_avg': stats.get('uc_avg', 0.0),
                                    'uc_max': stats.get('uc_max', 0.0),
                                    'total_err': stats.get('total_err', 0),
                                    'time_to_target_urls': time_taken.get(laptop, 0.0),
                                    'cx_name': "NA",
                                }
                                # Check if the device reaches the current target URL count
                                if stats.get('total_urls', 0) >= self.device_targets[laptop] and laptop not in time_taken:
                                    time_taken[laptop] = (datetime.now() - datetime.fromisoformat(stats.get("start_time", start_time.isoformat()))).total_seconds()
                                    row['time_to_target_urls'] = time_taken[laptop]
                                writer.writerow(row)
                                last_data.append(row)
                        # Collect data for mobile devices
                        if True:
                            mobile_data = self.local_realm.json_get("layer4/%s/list?fields=name,status,total-urls,uc-min,uc-avg,uc-max,total-err,bad-url" %
                                                                    (','.join(self.created_cx.keys())))
                            total_urls = []
                            uc_min = []
                            uc_avg = []
                            uc_max = []
                            total_err = []
                            hostnames = []
                            cx_names = []
                            # Check if multiple CX endpoints are created
                            if len(self.created_cx.keys()) > 1:
                                data = mobile_data['endpoint']
                                for endpoint in data:
                                    for key, value in endpoint.items():
                                        if True:
                                            cx_name = value.get('name', 'NA')
                                            match = re.search(r'http(\d+)', cx_name)
                                            res_no = match.group(1) if match else 'NA'
                                            hostname = self.local_realm.json_get("resource/1/%s/list?fields=user" % (res_no))
                                            hostname = hostname["resource"]["user"]
                                            pass_url = value.get('total-urls', 0)
                                            total_urls.append(pass_url)
                                            uc_min.append(value.get('uc-min', 0.0))
                                            uc_avg.append(value.get('uc-avg', 0.0))
                                            uc_max.append(value.get('uc-max', 0.0))
                                            total_err.append(value.get('total-err', 0))
                                            hostnames.append(hostname)
                                            cx_names.append(cx_name)
                                            if hostname not in self.device_targets:
                                                self.device_targets[hostname] = initial_target_urls
                                            # Check if the mobile device reaches the current target URL count
                                            if pass_url >= self.device_targets[hostname] and hostname not in time_taken:
                                                time_taken[hostname] = (datetime.now() - start_time).total_seconds()
                                # Save each mobile device's data to the CSV
                                for i in range(len(total_urls)):
                                    row = {
                                        'device_type': 'mobile',
                                        'device_name': hostnames[i],
                                        'total_urls': total_urls[i],
                                        'uc_min': float(uc_min[i]) / 1000,
                                        'uc_avg': float(uc_avg[i]) / 1000,
                                        'uc_max': float(uc_max[i]) / 1000,
                                        'total_err': total_err[i],
                                        'time_to_target_urls': time_taken.get(hostnames[i], 0.0),
                                        'cx_name': cx_names[i],
                                    }
                                    writer.writerow(row)
                                    last_data.append(row)
                            # Handle the case where only one CX endpoint is created
                            elif len(self.created_cx.keys()) == 1:
                                endpoint = mobile_data.get('endpoint', {})
                                if True:
                                    cx_name = endpoint.get('name', 'NA')
                                    match = re.search(r'http(\d+)', cx_name)
                                    res_no = match.group(1) if match else 'NA'
                                    hostname = self.local_realm.json_get("resource/1/%s/list?fields=user" % (res_no))
                                    hostname = hostname["resource"]["user"]
                                    if hostname not in self.device_targets:
                                        self.device_targets[hostname] = initial_target_urls
                                    # Check if the mobile device reaches the current target URL count
                                    pass_url = endpoint.get('total-urls', 0)
                                    if pass_url >= self.device_targets[hostname]:
                                        if hostname not in time_taken:
                                            time_taken[hostname] = (datetime.now() - start_time).total_seconds()
                                    row = {
                                        'device_type': 'mobile',
                                        'device_name': hostname,
                                        'total_urls': pass_url,
                                        'uc_min': float(endpoint.get('uc-min', 0.0)) / 1000,
                                        'uc_avg': float(endpoint.get('uc-avg', 0.0)) / 1000,
                                        'uc_max': float(endpoint.get('uc-max', 0.0)) / 1000,
                                        'total_err': endpoint.get('total-err', 0),
                                        'time_to_target_urls': time_taken.get(hostname, 0.0),
                                        'cx_name': cx_name
                                    }
                                    writer.writerow(row)
                                    last_data.append(row)
                    time.sleep(1)
                except Exception as e:
                    logging.exception(f"Error in get_stats function {e}", exc_info=True)
                    logging.info(f"layer4 cx data {mobile_data}")
                    time.sleep(1)
            for device in self.device_targets:

                # Update the target URLs based on the last fetched total_urls value
                for row in last_data:
                    if row['device_name'] == device:
                        self.device_targets[device] = row['total_urls'] + initial_target_urls

            # After the loop ends, write the last collected data to a separate file with iteration number
            last_file_name = f'iteration_{self.iteration_value}_final_data.csv'
            with open(last_file_name, mode='w', newline='') as last_file:
                last_writer = csv.DictWriter(last_file, fieldnames=headers)
                last_writer.writeheader()
                for row in last_data:
                    last_writer.writerow(row)

            # Append the file name to the csv_file_names list
            self.csv_file_names.append(last_file_name)

            self.iteration_value = self.iteration_value + 1
        except Exception as e:
            logging.error(f"Error in get_stats function {e}", exc_info=True)
            logging.info(f"layer4 cx data {mobile_data}")

    def updating_webui_runningjson(self, obj):
        data = {}
        file_path = self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name)
        # Wait until the file exists
        while not os.path.exists(file_path):
            logging.info("Waiting for the Running Json file to be created")
            time.sleep(1)
        logging.info("Running Json file created")
        with open(file_path, 'r') as file:
            data = json.load(file)
        for key in obj:
            data[key] = obj[key]
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def webui_stop(self):
        "Sends a POST request to the web UI to update the test status to 'Completed'."
        try:
            url = f"http://{self.host}:5454/update_status_yt"
            # url = "http://localhost:5454/update_status_yt"
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'status': 'Completed',
                'name': self.test_name
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                logging.info("Successfully updated STOP status to 'Completed'")
                pass
            else:
                logging.error(f"Failed to update STOP status: {response.status_code} - {response.text}")

        except Exception as e:
            logging.error(f"An error occurred while updating status: {e}")

    def change_port_to_ip(self):
        """
        Convert a given port name to its corresponding IP address if it's not already an IP.

        This function checks whether the provided `upstream_port` is a valid IPv4 address.
        If it's not, it attempts to extract the IP address of the port by resolving it
        via the internal `name_to_eid()` method and then querying the IP using `json_get()`.

        Args:
            upstream_port (str): The name or IP of the upstream port. This could be a
            LANforge port name like '1.1.eth1' or an IP address.

        Returns:
            str: The resolved IP address if the port name was converted successfully,
            otherwise returns the original input if it was already an IP or
            if resolution fails.

        Logs:
            - A warning if the port is not Ethernet or IP resolution fails.
            - Info logs for the resolved or passed IP.

        """
        if self.upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(self.upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                self.upstream_port = target_port_ip
            except BaseException:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {self.upstream_port}.')
            logging.info(f"Upstream port IP {self.upstream_port}")
        else:
            logging.info(f"Upstream port IP {self.upstream_port}")

        return self.upstream_port

    def filter_ios_devices(self, device_list):
        """
        Filters out iOS devices from the given device list based on hardware and software identifiers.

        This method accepts a list or comma-separated string of device identifiers and removes
        devices identified as iOS (Apple) based on their hardware version, app ID, and kernel info
        fetched via the `/resource/{shelf}/{resource}` API endpoint.

        Supported input formats for each device:
        - "shelf.resource"
        - "shelf.resource.port"
        - "resource" (assumes shelf = 1)

        iOS devices are identified if:
        - 'Apple' is found in the hardware version, and
        - `app-id` is not empty and is either non-zero or the kernel is empty

        Args:
            device_list (Union[list[str], str]): A list or comma-separated string of devices to be filtered.

        Returns:
            Union[list[int], str]: A list of valid (non-iOS) device IDs as integers,
            or a comma-separated string if the input was a string.

        Logs:
            - Warnings for invalid formats or missing device data.
            - Info when an iOS device is skipped.
            - Exceptions if errors occur during processing.

        """
        modified_device_list = device_list
        if isinstance(device_list, str):
            modified_device_list = device_list.split(',')

        filtered_list = []

        for device in modified_device_list:
            device = str(device).strip()
            try:
                if device.count('.') == 1:
                    shelf, resource = device.split('.')
                elif device.count('.') == 2:
                    shelf, resource, port = device.split('.')
                elif device.count('.') == 0:
                    shelf, resource = 1, device
                else:
                    logger.warning("Invalid device format: %s", device)
                    continue

                device_data_resp = self.json_get(f'/resource/{shelf}/{resource}')
                if not device_data_resp or 'resource' not in device_data_resp:
                    logger.warning("Device data not found for %s", device)
                    continue

                device_data = device_data_resp['resource']
                hw_version = device_data.get('hw version', '')
                app_id = device_data.get('app-id', '')
                kernel = device_data.get('kernel', '')

                if 'Apple' in hw_version and app_id != '' and (app_id != '0' or kernel == ''):
                    logger.info("%s is an iOS device. Currently, we do not support iOS devices.", device)
                else:
                    device = int(device)
                    filtered_list.append(device)

            except Exception as e:
                logger.exception(f"Error processing device {device}: {e}")
                continue

        if isinstance(device_list, str):
            filtered_list = ','.join(filtered_list)

        self.device_list = filtered_list
        return filtered_list

    def generate_test_setup_info(self):
        """
        Generate a dictionary containing the test setup information
        based on the configuration mode or selected group/profile mapping.

        Returns:
            dict: Test setup information.
        """
        if self.config:
            test_setup_info = {
                'Configured Devies': self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac}), A({self.android})',
                # 'Incremental Values': self.test_setup_info_incremental_values,
                'Required URL Count': self.count,
                'URL': self.url,
                'Test Duration (min)': self.duration,
                'SSID': self.report_ssid,
                "Security": self.encryp
            }
        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            # Map each group with a profile
            gp_pairs = zip(self.selected_groups, self.selected_profiles)

            # Create a string by joining the mapped pairs
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

            test_setup_info = {
                'Configuration': gp_map,
                'Configured Devies': self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac}), A({self.android})',
                # 'Incremental Values': self.test_setup_info_incremental_values,
                'Required URL Count': self.count,
                'URL': self.url,
                'Test Duration (min)': self.duration,
            }
        else:
            test_setup_info = {
                'Configured Devies': self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac}), A({self.android})',
                # 'Incremental Values': self.test_setup_info_incremental_values,
                'Required URL Count': self.count,
                'URL': self.url,
                'Test Duration (min)': self.duration,
            }

        return test_setup_info

    def generate_pass_fail_list(self, device_type_data, device_names, total_urls):
        """
        Generate the pass/fail list and expected URL count list for the devices.

        Args:
            device_type_data (list): List of device types (e.g., Android, Windows).
            device_names (list): List of device names.
            total_urls (list): List of total URLs accessed by each device.

        Returns:
            tuple: (pass_fail_list, test_input_list)
        """
        pass_fail_list = []
        test_input_list = []

        if not self.expected_passfail_value:
            res_list = []
            interop_tab_data = self.json_get('/adb/')["devices"]

            for i in range(len(device_type_data)):
                if device_type_data[i] != 'Android':
                    res_list.append(device_names[i])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] in device_names:
                                name_to_append = item['name'].split('.')[2]
                                if name_to_append not in res_list:
                                    res_list.append(name_to_append)

            if self.dowebgui:
                os.chdir(self.original_dir)

            if self.device_csv_name is None:
                self.device_csv_name = "device.csv"

            file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", self.device_csv_name))
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            for device in res_list:
                found = False
                for row in rows:
                    if row['DeviceList'] == device and row['RealBrowser URLcount'].strip() != '':
                        test_input_list.append(row['RealBrowser URLcount'])
                        found = True
                        break
                if not found:
                    logging.info(f"Pass Fail Value for Device {device} not found in CSV. Using default value 5")
                    test_input_list.append(5)  # Default value

            if self.dowebgui:
                os.chdir(self.result_dir)

        else:
            test_input_list = [self.expected_passfail_value for _ in range(len(device_type_data))]

        for j in range(len(test_input_list)):
            if float(test_input_list[j]) <= float(total_urls[j]):
                pass_fail_list.append('PASS')
            else:
                pass_fail_list.append('FAIL')

        return pass_fail_list, test_input_list

    def create_report(self):
        try:
            if self.dowebgui:
                report = lf_report(_output_pdf='Real_Browser_Report',
                                   _output_html='Real_Browser_Report.html',
                                   _results_dir_name="Real_Browser_Report",
                                   _path=self.result_dir)
                self.report_path_date_time = report.get_path_date_time()
            else:

                report = lf_report(_output_pdf='Real_Browser_Report',
                                   _output_html='Real_Browser_Report.html',
                                   _results_dir_name="Real_Browser_Report",
                                   _path='')
                self.report_path_date_time = report.get_path_date_time()

            report.set_title("Web Browser Test")
            report.build_banner()

            report.set_table_title("Objective:")
            report.build_table_title()
            report.set_text("The Candela Web browser test is designed to measure the Access Point performance and stability by browsing multiple websites in real clients" +
                            " like android, Linux, windows" +
                            "and IOS which are connected to the access point. This test allows the user to choose the options like website link," +
                            "the number of times the page has to browse, and the Time taken to browse the page." +
                            "The expected behavior is for the AP to be able to handle several stations(within the limitations of the AP specs) and make sure all clients can browse the page.")
            report.build_text_simple()

            report.set_table_title("Test Parameters:")
            report.build_table_title()

            final_eid_data = []
            mac_data = []
            channel_data = []
            signal_data = []
            ssid_data = []
            tx_rate_data = []
            device_type_data = []
            device_names = []
            total_urls = []
            time_to_target_urls = []
            uc_min_data = []
            uc_max_data = []
            uc_avg_data = []
            total_err_data = []

            final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = self.extract_device_data('real_time_data.csv')

            test_setup_info = self.generate_test_setup_info()
            report.test_setup_table(
                test_setup_data=test_setup_info, value='Test Parameters')

            for i in range(0, len(self.csv_file_names)):

                final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = self.extract_device_data(self.csv_file_names[i])
                report.set_graph_title("Successful URL's per Device")
                report.build_graph_title()

                data = pd.read_csv(self.csv_file_names[i])

                # Extract device names from CSV
                if 'total_urls' in data.columns:
                    total_urls = data['total_urls'].tolist()
                else:
                    raise ValueError("The 'total_urls' column was not found in the CSV file.")

                x_fig_size = 18
                y_fig_size = len(device_type_data) * 1 + 4
                bar_graph_horizontal = lf_bar_graph_horizontal(
                    _data_set=[total_urls],
                    _xaxis_name="URL",
                    _yaxis_name="Devices",
                    _yaxis_label=device_names,
                    _yaxis_categories=device_names,
                    _yaxis_step=1,
                    _yticks_font=8,
                    _bar_height=.20,
                    _show_bar_value=True,
                    _figsize=(x_fig_size, y_fig_size),
                    _graph_title="URLs",
                    _graph_image_name=f"{self.csv_file_names[i]}_urls_per_device",
                    _label=["URLs"]
                )
                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                report.set_graph_image(graph_image)
                report.move_graph_image()
                report.build_graph()

                report.set_graph_title(f"Time Taken Vs Device For Completing {self.count} RealTime URLs")
                report.build_graph_title()

                # Extract device names from CSV
                if 'time_to_target_urls' in data.columns:
                    time_to_target_urls = data['time_to_target_urls'].tolist()
                else:
                    raise ValueError("The 'time_to_target_urls' column was not found in the CSV file.")

                x_fig_size = 18
                y_fig_size = len(device_type_data) * 1 + 4
                bar_graph_horizontal = lf_bar_graph_horizontal(
                    _data_set=[time_to_target_urls],
                    _xaxis_name="Time (in Seconds)",
                    _yaxis_name="Devices",
                    _yaxis_label=device_names,
                    _yaxis_categories=device_names,
                    _yaxis_step=1,
                    _yticks_font=8,
                    _bar_height=.20,
                    _show_bar_value=True,
                    _figsize=(x_fig_size, y_fig_size),
                    _graph_title="Time Taken",
                    _graph_image_name=f"{self.csv_file_names[i]}_time_taken_for_urls",
                    _label=["Time (in sec)"]
                )
                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                report.set_graph_image(graph_image)
                report.move_graph_image()
                report.build_graph()

                if 'uc_min' in data.columns:
                    uc_min_data = data['uc_min'].tolist()
                else:
                    raise ValueError("The 'uc_min' column was not found in the CSV file.")

                if 'uc_max' in data.columns:
                    uc_max_data = data['uc_max'].tolist()
                else:
                    raise ValueError("The 'uc_max' column was not found in the CSV file.")

                if 'uc_avg' in data.columns:
                    uc_avg_data = data['uc_avg'].tolist()
                else:
                    raise ValueError("The 'uc_avg' column was not found in the CSV file.")

                if 'total_err' in data.columns:
                    total_err_data = data['total_err'].tolist()
                else:
                    raise ValueError("The 'total_err' column was not found in the CSV file.")

            report.set_table_title("Final Test Results")
            report.build_table_title()
            if self.expected_passfail_value or self.device_csv_name:
                pass_fail_list, test_input_list = self.generate_pass_fail_list(device_type_data, device_names, total_urls)

                final_test_results = {

                    "Device Type": device_type_data,
                    "Hostname": device_names,
                    "SSID": ssid_data,
                    "MAC": mac_data,
                    "Channel": channel_data,
                    "UC-MIN (ms)": uc_min_data,
                    "UC-MAX (ms)": uc_max_data,
                    "UC-AVG (ms)": uc_avg_data,
                    "Total Successful URLs": total_urls,
                    "Expected URLS": test_input_list,
                    "Total Erros": total_err_data,
                    "RSSI": signal_data,
                    "Link Speed": tx_rate_data,
                    "Status ": pass_fail_list

                }
            else:
                final_test_results = {

                    "Device Type": device_type_data,
                    "Hostname": device_names,
                    "SSID": ssid_data,
                    "MAC": mac_data,
                    "Channel": channel_data,
                    "UC-MIN (ms)": uc_min_data,
                    "UC-MAX (ms)": uc_max_data,
                    "UC-AVG (ms)": uc_avg_data,
                    "Total Successful URLs": total_urls,
                    "Total Erros": total_err_data,
                    "RSSI": signal_data,
                    "Link Speed": tx_rate_data,

                }
            test_results_df = pd.DataFrame(final_test_results)
            report.set_table_dataframe(test_results_df)
            report.build_table()

            if self.dowebgui:

                os.chdir(self.original_dir)

            report.build_custom()
            report.build_footer()
            report.write_html()
            report.write_pdf()
        except Exception as e:
            logging.error(f"Error in create_report function {e}", exc_info=True)
        finally:
            if not self.dowebgui:
                source_dir = "."
                destination_dir = self.report_path_date_time
                self.csv_file_names.append('real_time_data.csv')
                for filename in self.csv_file_names:
                    source_path = os.path.join(source_dir, filename)
                    destination_path = os.path.join(destination_dir, filename)
                    if os.path.isfile(source_path):
                        shutil.move(source_path, destination_path)
                        logging.info(f"Moved {filename} to {destination_dir}")
                    else:
                        logging.info(f"{filename} not found in the current directory")

    def extract_device_data(self, file_path):
        # Load the CSV file
        data = pd.read_csv(file_path)

        # Initialize lists to store data
        final_eid_data = []
        mac_data = []
        channel_data = []
        signal_data = []
        ssid_data = []
        tx_rate_data = []
        device_type_data = []

        # Extract device names from CSV
        if 'device_name' in data.columns:
            device_names = data['device_name'].tolist()
        else:
            raise ValueError("The 'device_name' column was not found in the CSV file.")

        if 'device_type' in data.columns:
            device_type_data = data['device_type'].tolist()
        else:
            raise ValueError("The 'device_type' column was not found in the CSV file.")

        # Collect data for mobile devices
        rm_data = self.local_realm.json_get("resource/list/?fields=eid,Hostname,device type,user")

        for i in range(0, len(device_names)):
            for resource in rm_data['resources']:
                for key, value in resource.items():
                    if value['hostname'] == device_names[i] and device_type_data[i] == "laptop":
                        final_eid_data.append(value['eid'])
                        device_type_data[i] = value["device type"]
                    elif value["user"] == device_names[i] and device_type_data[i] == "mobile":
                        final_eid_data.append(value['eid'])
                        device_type_data[i] = value["device type"]

        # Collect port data for each eid
        logging.info(f"Checking final eid data {final_eid_data}")
        for eid in final_eid_data:
            port_data = self.local_realm.json_get("port/list?fields=ssid,mac,parent dev,signal,tx-rate,channel,down,ip")
            for interface in port_data['interfaces']:
                for key, value in interface.items():
                    temp_eid = key.split(".")
                    comb_eid = temp_eid[0] + "." + temp_eid[1]
                    if (comb_eid == eid) and (value["parent dev"] != "") and (not value["down"]) and (value["ip"] != "0.0.0.0"):
                        logging.info("checking whether we are able to fetch device data from port manager")
                        mac_data.append(value.get("mac", 'None'))
                        channel_data.append(value.get("channel", 'None'))
                        signal_data.append(value.get("signal", 'None'))
                        ssid_data.append(value.get("ssid", 'None'))
                        tx_rate_data.append(value.get("tx-rate", 'None'))

        return final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data


def main():
    try:

        help_summary = '''\
        The Candela Web browser test is designed to measure the Access Point performance and stability by browsing multiple websites in real clients like
        android, Linux, windows, and IOS which are connected to the access point. This test allows the user to choose the options like website link, the
        number of times the page has to browse, and the Time taken to browse the page. Along with the performance other measurements made are client
        connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the AP to be able to handle several stations
        (within the limitations of the AP specs) and make sure all clients can browse the page.
        '''

        parser = argparse.ArgumentParser(
            prog=__file__,
            formatter_class=argparse.RawTextHelpFormatter,
            description='''\

            Name: lf_interop_real_browser_test.py

            Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
            For now the test script supports Real Browser test for Androids.

            Pre-requisites: Real devices should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge

            Example: (python3 or ./)lf_interop_real_browser_test.py --mgr 192.168.214.219 --duration 1 --url "www.google.com"

            Example-1 :
            Command Line Interface to run url in the Browser with specified URL and duration:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --debug --upstream_port 1.1.eth1

                CASE-1:
                If not specified it takes the default url (default url is www.google.com)

            Example-2:
            Command Line Interface to run url in the Browser with specified Resources:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --debug --upstream_port 1.1.eth1

            Example-3:
            Command Line Interface to run url in the Browser with specified urls_per_tennm (specify the number of url you want to test in the given duration):
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --debug --upstream_port 1.1.eth1

                CASE-1:
                If not specified it takes the default count value (default count is 1)


            Example-4:
            Command Line Interface to run url in the Browser with precleanup:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --precleanup --debug --upstream_port 1.1.eth1

            Example-5:
            Command Line Interface to run url in the Browser with postcleanup:
            python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --postcleanup --debug --upstream_port 1.1.eth1

            Example-4:
            Command Line Interface to run the Real Browser Test with Device Configuration
            python3 lf_interop_real_browser_test.py --mgr 192.168.204.74 --url "https://google.com" --duration 1m --debug --upstream_port 1.1.eth1
            --ssid NETGEAR_5G_wpa2 --passwd Password@123 --encryp wpa2 --config

            Example-5:
            Command Line Interface to run the Real Browser Test with groups and profiles
            python3 lf_interop_real_browser_test.py --mgr 192.168.204.74 --url "https://google.com" --duration 1m --debug --upstream_port 1.1.eth1
            --file_name grplaptops --group_name group1,group2 --profile_name netgear2g,netgear2g


            SCRIPT CLASSIFICATION: Test

            SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

            NOTES:
                1. Use './lf_interop_real_browser_test.py --help' to see command line usage and options.
                2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
                3. If --device_list are not given after passing the CLI, a list of available devices will be displayed on the terminal.
                4. Enter the resource numbers separated by commas (,) in the resource argument and also enclose in double quotes (e.g. : 1.10,1.12).
                5. For --url, you can specify the URL (e.g., www.google.com).
                6. To run the test by specifying the incremental capacity, enable the --incremental flag.

            STATUS: BETA RELEASE

            VERIFIED_ON:
            Working date - 29/07/2024
            Build version - 5.4.8
            kernel version - 6.2.16+

            License: Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2023 Candela Technologies Inc.

            ''')

        optional = parser.add_argument_group('Optional arguments to run lf_interop_real_browser_test.py')
        parser.add_argument("--host", "--mgr", required=True, help='specify the GUI to connect to, assumes port '
                            '8080')
        parser.add_argument("--ssid", default=None, help='specify ssid on which the test will be running')
        parser.add_argument("--passwd", default=None, help='specify encryption password  on which the test will '
                            'be running')
        parser.add_argument("--encryp", default=None, help='specify the encryption type  on which the test will be '
                            'running eg :open|psk|psk2|sae|psk2jsae')
        parser.add_argument("--url", default="https://google.com", help='specify the url you want to test on')
        parser.add_argument("--max_speed", type=int, default=0, help='specify the max speed you want in bytes')
        parser.add_argument("--count", type=int, default=1, help='specify the number of url you want to calculate time to reach'
                            )
        parser.add_argument('--duration', type=str, help='time to run traffic')
        optional.add_argument('--test_name', help='Specify test name to store the runtime csv results', default=None)
        parser.add_argument('--dowebgui', help="If true will execute script for webgui", default=False, type=bool)
        parser.add_argument('--result_dir', help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')

        parser.add_argument("--lf_logger_config_json", help="[log configuration] --lf_logger_config_json <json file> , json configuration of logger")
        parser.add_argument("--log_level", help="[log configuration] --log_level  debug info warning error critical")
        parser.add_argument("--debug", help="[log configuration] --debug store_true , used by lanforge client ", action='store_true')

        parser.add_argument('--device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
        parser.add_argument('--webgui_incremental', '--incremental_capacity', help="Specify the incremental values <1,2,3..>", dest='webgui_incremental', type=str)
        parser.add_argument('--incremental', help="to add incremental capacity to run the test", action='store_true')
        optional.add_argument('--no_laptops', help="run the test without laptop devices", action='store_false')
        parser.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action='store_true')
        parser.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action='store_true')
        parser.add_argument('--file_name', type=str, help='specify the file name')
        parser.add_argument('--group_name', type=str, help='specify the group name')
        parser.add_argument('--profile_name', type=str, help='specify the profile name')

        parser.add_argument("--eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
        parser.add_argument("--eap_identity", type=str, default='DEFAULT', help="Specify the EAP identity for authentication.")
        parser.add_argument("--ieee80211", action="store_true", help='Enables IEEE 802.11 support.')
        parser.add_argument("--ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
        parser.add_argument("--ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
        parser.add_argument("--enable_pkc", action="store_true", help='Enables pkc support.')
        parser.add_argument("--bss_transition", action="store_true", help='Enables BSS transition support.')
        parser.add_argument("--power_save", action="store_true", help='Enables power-saving features.')
        parser.add_argument("--disable_ofdma", action="store_true", help='Disables OFDMA support.')
        parser.add_argument("--roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
        parser.add_argument("--key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP)')
        parser.add_argument("--pairwise", type=str, default='NA', help="Specify the pairwise cipher")
        parser.add_argument("--private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
        parser.add_argument("--ca_cert", type=str, default='NA', help='Specify the CA certificate file name')
        parser.add_argument("--client_cert", type=str, default='NA', help='Specify the client certificate file name')
        parser.add_argument("--pk_passwd", type=str, default='NA', help='Specify the password for the private key')
        parser.add_argument("--pac_file", type=str, default='NA', help='Specify the pac file name')
        parser.add_argument("--upstream_port", type=str, default='NA', help='Specify the Upstream Port', required=True)
        parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)
        parser.add_argument("--expected_passfail_value", help="Specify the expected urlcount value for pass/fail")
        parser.add_argument("--device_csv_name", type=str, help="Specify the device csv name for pass/fail", default=None)
        parser.add_argument("--wait_time", type=int, help="Specify the time for configuration", default=60)
        parser.add_argument('--config', action='store_true', help='specify this flag whether to config devices or not')

        args = parser.parse_args()
        if args.help_summary:
            print(help_summary)
            exit(0)

        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()
        if args.url.lower().startswith("www."):
            args.url = "https://" + args.url
        if args.url.lower().startswith("http://"):
            args.url = "https://" + args.url.removeprefix("http://")

        # Initialize an instance of RealBrowserTest with various parameters
        obj = RealBrowserTest(host=args.host,
                              ssid=args.ssid,
                              passwd=args.passwd,
                              encryp=args.encryp,
                              suporrted_release=["7.0", "10", "11", "12"],
                              max_speed=args.max_speed,
                              url=args.url, count=args.count,
                              duration=args.duration,
                              resource_ids=args.device_list,
                              dowebgui=args.dowebgui,
                              result_dir=args.result_dir,
                              test_name=args.test_name,
                              incremental=args.incremental,
                              postcleanup=args.postcleanup,
                              precleanup=args.precleanup,
                              file_name=args.file_name,
                              group_name=args.group_name,
                              profile_name=args.profile_name,
                              eap_method=args.eap_method,
                              eap_identity=args.eap_identity,
                              ieee80211=args.ieee80211,
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
                              upstream_port=args.upstream_port,
                              expected_passfail_value=args.expected_passfail_value,
                              device_csv_name=args.device_csv_name,
                              wait_time=args.wait_time,
                              config=args.config,
                              selected_groups=args.group_name,
                              selected_profiles=args.profile_name
                              )
        obj.change_port_to_ip()
        obj.validate_and_process_args()
        obj.config_obj = DeviceConfig.DeviceConfig(lanforge_ip=obj.host, file_name=obj.file_name, wait_time=obj.wait_time)
        if not obj.expected_passfail_value and obj.device_csv_name is None:
            obj.config_obj.device_csv_file(csv_name="device.csv")
        obj.run_flask_server()
        if obj.group_name and obj.profile_name and obj.file_name:
            available_resources = obj.process_group_profiles()
        else:
            # --- Build configuration dictionary for WiFi parameters ---
            config_dict = {
                'ssid': args.ssid,
                'passwd': args.passwd,
                'enc': args.encryp,
                'eap_method': args.eap_method,
                'eap_identity': args.eap_identity,
                'ieee80211': args.ieee80211,
                'ieee80211u': args.ieee80211u,
                'ieee80211w': args.ieee80211w,
                'enable_pkc': args.enable_pkc,
                'bss_transition': args.bss_transition,
                'power_save': args.power_save,
                'disable_ofdma': args.disable_ofdma,
                'roam_ft_ds': args.roam_ft_ds,
                'key_management': args.key_management,
                'pairwise': args.pairwise,
                'private_key': args.private_key,
                'ca_cert': args.ca_cert,
                'client_cert': args.client_cert,
                'pk_passwd': args.pk_passwd,
                'pac_file': args.pac_file,
                'server_ip': obj.upstream_port,
            }
            available_resources = obj.process_resources(config_dict)
        if len(available_resources) != 0:
            available_resources = obj.filter_ios_devices(available_resources)
        if len(available_resources) == 0:
            logging.error("No devices available to run the test. Exiting...")
            exit(1)

        # --- Print available resources ---
        logging.info("Devices available: {}".format(available_resources))
        if obj.expected_passfail_value or obj.device_csv_name:
            obj.update_passfail_value(available_resources)
        # --- Handle incremental values ---
        obj.handle_incremental(args, obj, available_resources, available_resources)
        obj.handle_duration()
        obj.run_test(available_resources)

    except Exception as e:
        logging.error("Error occured", e)
        traceback.print_exc()
    finally:
        if not ('--help' in sys.argv or '-h' in sys.argv):
            obj.create_report()
            if (obj.dowebgui):
                obj.webui_stop()
            obj.stop()

            if args.postcleanup:
                obj.postcleanup()


if __name__ == '__main__':
    main()
