#!/usr/bin/env python3
"""
Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
    For now the test script supports Real Browser test for Androids. 

Pre-requisites: Real clients should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge


Example: (python3 or ./)lf_interop_real_browser_test.py --mgr 192.168.214.219 --duration 10m --url "www.google.com"

Example-1 :
Command Line Interface to run url in the Browser with specified URL and duration:
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --debug

    CASE-1:
    If not specified it takes the default url (default url is www.google.com)

Example-2:
Command Line Interface to run url in the Browser with specified Resources:
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --debug

Example-3:
Command Line Interface to run url in the Browser with specified urls_per_tennm (specify the number of url you want to test in the given duration):
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --debug

    CASE-1:
    If not specified it takes the default count value (default count is 100)

Example-4:
Command Line Interface to run the the Real Browser test with incremental Capacity by specifying the --incremental flag
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --incremental --debug


Example-5:
Command Line Interface to run the the Real Browser test in webGUI by specifying the --dowebgui flag
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --dowebgui --debug

Example-6:
Command Line Interface to run url in the Browser with precleanup:
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --precleanup --debug

Example-7:
Command Line Interface to run url in the Browser with postcleanup:
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --postcleanup --debug

Example-8:
Command Line Interface to run url in the Browser with incremental capacity:
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --incremental_capacity 1 --debug

SCRIPT CLASSIFICATION: Test

SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

NOTES:
    1. Use './lf_interop_real_browser_test.py --help' to see command line usage and options.
    2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
    3. If --device_list are not given after passing the CLI, a list of available devices will be displayed on the terminal.
    4. For --url, you can specify the URL (e.g., www.google.com).
    5. To run the test by specifying the incremental capacity, enable the --incremental flag. 

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
import datetime     
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt  
import logging     
import json      
import shutil
from datetime import datetime, timedelta  
from lf_graph import lf_bar_graph_horizontal  



# Check Python version compatibility
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

# Add parent directory to the system path
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

# Import specific modules from custom paths using importlib
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
base = importlib.import_module('py-scripts.lf_base_interop_profile')
lf_csv = importlib.import_module("py-scripts.lf_csv")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
base_RealDevice = base.RealDevice
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
port_utils = importlib.import_module("py-json.port_utils")
PortUtils = port_utils.PortUtils

# Set up logging configuration for the script
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")




class RealBrowserTest(Realm):
    def __init__(self, host, ssid, passwd, encryp, suporrted_release=None, max_speed=None, url=None,
                count=None, duration=None, resource_ids = None, dowebgui = False,result_dir = "",test_name = None, incremental = None,postcleanup=False,precleanup=False):
        super().__init__(lfclient_host=host, lfclient_port=8080)
        # Initialize attributes with provided parameters
        self.host = host 
        self.ssid = ssid 
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
        self.postCleanUp=postcleanup
        self.preCleanUp=precleanup
        self.direction = "dl"
        self.dest = "/dev/null"
        
        # Initialize additional attributes
        self.adb_device_list = None 
        self.phn_name = [] 
        self.device_name = []   
        self.android_devices = []
        self.other_os_list = [] 
        self.android_list = []   
        self.other_list = [] 
        self.real_sta_data_dict = {} 
        self.ip_map={}
        self.health = None  
        self.phone_data = None  
        self.background_run = None  
        self.test_stopped_by_user=False
        self.stop_test=False  
        self.max_speed = 0  # infinity
        self.quiesce_after = 0  # infinity

        # Initialize RealDevice instance      
        self.devices = base_RealDevice(manager_ip = self.host, selected_bands = [])
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
        # Initialize generic endpoints profile 
        # self.generic_endps_profile = self.new_generic_endp_profile()
        # self.generic_endps_profile.type = 'youtube'
        # self.generic_endps_profile.name_prefix = "yt"


    @property
    def run(self):
        """
            Property method to execute the browser test.
            This method performs several actions:
            1. Checks various configurations on the Interop tab using lf_base_interop_profile.py library.
            2. Retrieves details of connected devices and logs them.
            3. Stops ongoing processes on devices.
            4. Applies batch modifications and sets user names.
            5. Forgets network connections on devices.
            6. Retrieves health status for each device and logs it.
            7. Launches the Interop UI for devices connected to the expected SSID.
            8. Retrieves and logs resource data of phones.
        """
        # Check various configuration things on Interop tab, Uses lf_base_interop_profile.py library
        self.adb_device_list = self.interop.check_sdk_release()

        # Get device details for each adb device in the list
        for i in self.adb_device_list:
            self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
        logging.info(self.device_name)

        # Stop ongoing processes on devices
        self.interop.stop()
        # Apply batch modifications and set user names
        for i in self.adb_device_list:
            self.interop.batch_modify_apply(i)
            time.sleep(5)
        self.interop.set_user_name(device=self.adb_device_list)

        # Forget network connections on devices
        for i in self.adb_device_list:
            self.utility.forget_netwrk(i)

        # Initialize health dictionary for each device
        health = dict.fromkeys(self.adb_device_list)

        # Getting Health for each device
        for i in self.adb_device_list:
            # Get the state of the device
            dev_state = self.utility.get_device_state(device=i)
            logging.info("Device State : {dev_state}".format(dev_state = dev_state))

            logging.info("device state" + dev_state)
            # Check if the device state indicates it is connected
            if dev_state == "COMPLETED,":
                logging.info("phone is in connected state")
                logging.info("phone is in connected state")
                # Get the SSID of the connected device
                ssid = self.utility.get_device_ssid(device=i)
                # Check if the device is connected to the expected SSID
                if ssid == self.ssid:
                    logging.info("device is connected to expected ssid")
                    logging.info("device is connected to expected ssid")
                    # Retrieve and log the health status of the device
                    health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                    logging.info("health health:: ", health)
                    logging.info("Launching Interop UI")
                    logging.info("health :: {health}".format(health = health))
                    # Launch the Interop UI for the device
                    logging.info("Launching Interop UI")
                    self.interop.launch_interop_ui(device=i)
        # Store the health dictionary in the instance variable
        self.health = health
        logging.info("Health:: ", health)
        #  Retrieve and log resource data of phones
        self.phone_data = self.get_resource_data()
        logging.info("Phone List : ", self.phone_data)
        logging.info("Phone List : {phone_data}".format(phone_data = self.phone_data))

        time.sleep(5)   # Pause for 5 seconds before completing

    def build(self):
        """
            If the pre-requisites are satisfied, this function gets the list of real devices connected to LANforge
            and processes them for Layer 4-7 traffic profile creation.
        """

        # Initialize dictionaries and lists for data storage
        self.data = {}
        self.total_urls_dict = {}
        self.data_for_webui = {}
        self.all_cx_list = []

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
        self.mac = []
        self.mode = []
        self.rssi = []
        self.channel = []
        self.tx_rate = []
        self.time_data = []
        self.temp = []
        self.total_duration = ""
        self.formatted_endtime_str = ""

        # Retrieve resource data for phones
        self.phone_data = self.get_resource_data()
        logging.info("Creating Layer-4 endpoints from the user inputs as test parameters")
        time.sleep(5)
        # Configure HTTP profile settings
        self.direction = 'dl'
        self.dest = '/dev/null'
        self.max_speed = self.max_speed
        self.requests_per_ten = 100
        self.created_cx=self.http_profile.created_cx=self.convert_to_dict(self.phone_data)
        if self.preCleanUp==True:
            self.precleanup()
        self.http_profile.created_cx.clear()
        # for i in self.phone_data:
        # self.phone_data = ['1.16.wlan0', '1.17.xlan0', '1.20.ylan0']
        # Create HTTP profile
        upload_name=self.phone_data[-1].split('.')[-1]
        if 'https' in self.url :
            self.url = self.url.replace("http://", "").replace("https://", "")
            self.create_real(ports=self.phone_data, sleep_time=.5,
                                suppress_related_commands_=None, https=True,
                                https_ip=self.url, interop=True,timeout=1000,media_source='1',media_quality='0',upload_name=upload_name)
        elif 'http' in self.url :
            self.url = self.url.replace("http://", "").replace("https://", "")
            self.create_real(ports=self.phone_data, sleep_time=.5,
                                suppress_related_commands_=None, http=True,
                                http_ip=self.url, interop=True,timeout=1000,media_source='1',media_quality='0',upload_name=upload_name)
        
        else:
            self.create_real(ports=self.phone_data, sleep_time=.5,
                                suppress_related_commands_=None, real=True,
                                http_ip=self.url, interop=True,timeout=1000,media_source='1',media_quality='0',upload_name=upload_name)


        
    def map_sta_ips_real(self, sta_list=None):
        if sta_list is None:
            sta_list = []
        for sta_eid in sta_list:
            eid = self.name_to_eid(sta_eid)
            sta_list = self.json_get("/port/%s/%s/%s?fields=alias,ip" % (eid[0], eid[1], eid[2]))
            # print("map_sta_ips - sta_list:{sta_list}".format(sta_list=sta_list))
            '''
            sta_list_tmp = self.json_get("/port/%s/%s/%s?fields=ip" % (eid[0], eid[1], eid[2]))
            print("map_sta_ips - sta_list_tmp:{sta_list_tmp}".format(sta_list_tmp=sta_list_tmp))
            '''
            if sta_list['interface'] is not None:
                # print("map_sta_ips - sta_list_2:{sta_list_2}".format(sta_list_2=sta_list['interface']))
                # self.ip_map[sta_list['interface']['alias']] = sta_list['interface']['ip']
                eid_key = "{eid0}.{eid1}.{eid2}".format(eid0=eid[0], eid1=eid[1], eid2=eid[2])
                self.ip_map[eid_key] = sta_list['interface']['ip']

    def create_real(self, ports=None, sleep_time=.5, debug_=False, suppress_related_commands_=None, http=False, ftp=False, real=False,
               https=False, user=None, passwd=None, source=None, ftp_ip=None, upload_name=None, http_ip=None,
               https_ip=None, interop=None,media_source=None,media_quality=None,timeout=10,proxy_auth_type=0x2200,windows_list=[], get_url_from_file=False):
        if ports is None:
            ports = []
        cx_post_data = []
        # print("http_profile - ports:{ports}".format(ports=ports))
        self.map_sta_ips_real(ports)
        logger.info("Create HTTP CXs..." + __name__)
        # print("http_profile - self.ip_map:{ip_map}".format(ip_map=self.ip_map))

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

            # print("http_profile - port_name:{port_name}".format(port_name=port_name))
            rv = self.local_realm.name_to_eid(port_name)
            # print("http_profile - rv:{rv}".format(rv=rv))
            '''
            shelf = self.local_realm.name_to_eid(port_name)[0]
            resource = self.local_realm.name_to_eid(port_name)[1]
            name = self.local_realm.name_to_eid(port_name)[2]
            '''
            shelf = rv[0]
            resource = rv[1]
            name = rv[2]
            # eid_port = "{shelf}.{resource}.{name}".format(shelf=rv[0], resource=rv[1], name=rv[2])

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
                # print("create() - eid_port:{eid_port}".format(eid_port=eid_port))
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
                set_endp_data={
                    "alias": cx_name + str(resource) + "_l4",
                    "media_source":media_source,
                    "media_quality":media_quality,
                    # "media_playbacks":'0'
                }
                url = "cli-json/add_l4_endp"
                self.json_post(url, endp_data, debug_=debug_,
                                           suppress_related_commands_=suppress_related_commands_)
                time.sleep(sleep_time)
                # If media source and media quality is given then this code will set media source and media quality for CX
                if media_source and media_quality:
                    url1="cli-json/set_l4_endp"
                    self.json_post(url1, set_endp_data, debug_=debug_,
                                            suppress_related_commands_=suppress_related_commands_)

                endp_data = {
                    "alias": "CX_" + cx_name + "_l4",
                    "test_mgr": "default_tm",
                    "tx_endp": cx_name + "_l4",
                    "rx_endp": "NA"
                }
                # print("http_profile - endp_data:{endp_data}".format(endp_data=endp_data))
                cx_post_data.append(endp_data)
                self.created_cx[cx_name + "_l4"] = "CX_" + cx_name + "_l4"
            else: # If Interop is enabled then this code will work
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
                set_endp_data={
                    "alias": cx_name + str(resource) + "_l4",
                    "media_source":media_source,
                    "media_quality":media_quality,
                    # "media_playbacks":'0'
                }
                url = "cli-json/add_l4_endp"
                self.json_post(url, endp_data, debug_=debug_,
                                           suppress_related_commands_=suppress_related_commands_)
                time.sleep(sleep_time)
                # If media source and media quality is given then this code will set media source and media quality for CX
                if media_source and media_quality:
                    url1="cli-json/set_l4_endp"
                    self.json_post(url1, set_endp_data, debug_=debug_,
                                            suppress_related_commands_=suppress_related_commands_)

                endp_data = {  # Added resource id to alias and End point name as all real clients have same name(wlan0)
                    "alias": "CX_" + cx_name + str(resource) + "_l4",
                    "test_mgr": "default_tm",
                    "tx_endp": cx_name + str(resource) + "_l4",
                    "rx_endp": "NA"
                }
                # print("http_profile - endp_data:{endp_data}".format(endp_data=endp_data))
                cx_post_data.append(endp_data)
                self.created_cx[cx_name + str(resource) + "_l4"] = "CX_" + cx_name + str(resource) + "_l4"
        self.http_profile.created_cx=self.created_cx

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

    
    def convert_to_dict(self,input_list):
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
        keys=list(self.created_cx.keys())
        incremental_temp = []
        created_incremental_values = []
        index = 0
        if len(self.incremental) == 1 and self.incremental[0] == len(keys):
            incremental_temp.append(len(keys[index:]))
        elif len(self.incremental) == 1 and len(keys) > 1:
            incremental_value = self.incremental[0]
            div = len(keys)//incremental_value 
            mod = len(keys)%incremental_value 

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
        try:
            # Loop through each CX endpoint and wait until it reaches the 'Run' state
            for i in self.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass
    
    def start_specific(self,cx_start_list):
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
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.http_profile.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
        logging.info("Setting Cx State to Runnning")
        try:
            # Loop through each CX endpoint and wait until it reaches the 'Run' state
            for i in self.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    # def create_generic_endp(self,query_resources,os_types_dict):
    #     """
    #         Creates generic endpoints for Real clients based on specified resources and operating system types.

    #         Parameters:
    #         - query_resources (list): List of resource identifiers to query.
    #         - os_types_dict (dict): Dictionary mapping resource identifiers to their respective operating system types.

    #         This method performs the following actions:
    #         1. Retrieves information about available resources from LANforge.
    #         2. Matches queried resources with available resources and retrieves their details.
    #         3. Identifies matching ports based on control IPs and creates a list of ports.
    #         4. Filters out Android devices from the list of operating system types.
    #         5. Creates generic endpoints for Real clients using the generic endpoint profile.
    #     """
    #     ports_list = []
    #     eid = ""
    #     resource_ip = ""
    #     # Extract only the first two octets of each query resource identifier
    #     user_resources = ['.'.join(item.split('.')[:2]) for item in query_resources]
    #     exit_loop = False
    #     # Retrieve all resources from LANforge
    #     response = self.json_get("/resource/all")
    #     # Iterate through the response to find matching resources
    #     for key, value in response.items():
    #         if key == "resources" and user_resources:
    #             for element in value:
    #                 if user_resources:
    #                     for resource_key, resource_values in element.items():
    #                         if resource_key in user_resources:
    #                             eid = resource_values["eid"]
    #                             resource_ip = resource_values['ctrl-ip']
    #                             ports_list.append({'eid': eid, 'ctrl-ip': resource_ip})
    #                             resource_key_index = user_resources.index(resource_key)
    #                             del user_resources[resource_key_index]
    #                 else:
    #                     exit_loop = True
    #                     break
    #         if exit_loop:
    #             break

    #     gen_ports_list = []
    #     # Retrieve all ports from LANforge
    #     response_port = self.json_get("/port/all")
    #     # Iterate through interfaces and ports to find matching ports based on control IPs -  to retrieve the management port of the resources
    #     for interface in response_port['interfaces']:
    #         for port, port_data in interface.items():
    #             result = '.'.join(port.split('.')[:2])
                
    #             # Check if the result exists in ports_list
    #             matching_entry = next((entry for entry in ports_list if entry['eid'] == result), None)
                
    #             if matching_entry:
    #                 port_ip = port_data['ip']                    
    #                 if port_ip == matching_entry['ctrl-ip']:
    #                     gen_ports_list.append(port.split('.')[-1])
    #                     break

    #     gen_ports_list = ",".join(gen_ports_list)
        
    #     # Retrieve OS types excluding Android
    #     real_sta_os_types = [os_types_dict[resource_id] for resource_id in os_types_dict if os_types_dict[resource_id] != 'android']
        
    #     # Create generic endpoints using generic_endps_profile
    #     if (self.generic_endps_profile.create(ports=self.other_list, sleep_time=.5, real_client_os_types=real_sta_os_types, gen_port = gen_ports_list, from_script = "realbrowser")):
    #         logging.info('Real client generic endpoint creation completed.')
    #     else:
    #         logging.error('Real client generic endpoint creation failed.')
    #         exit(0)
        
    #     # Set endpoint report time to ping packet interval
    #     for endpoint in self.generic_endps_profile.created_endp:
    #         self.generic_endps_profile.set_report_timer(endp_name=endpoint, timer=250)

    def stop(self):
        """
            Stops the layer 4-7 traffic for created CX endpoints.

            This method performs the following actions:
            1. If resource IDs are provided, sets the remaining time in webGUI to "0:00:00".
            2. Logs a message indicating the intention to set the CX state to 'Stopped'.
            3. Stops the CX for HTTP profile.
        """
        # Stops the layer 4-7 traffic for created CX end points
        # Set remaining time in webGUI to "0:00:00" if resource IDs are provided
        if self.resource_ids:
            self.data['remaining_time_webGUI'] = ["0:00:00"] * len(self.data['status']) 
        logging.info("Setting Cx State to Stopped")
        # Stop the CX for HTTP profile
        self.http_profile.stop_cx()
    
    def precleanup(self):
        self.http_profile.cleanup()

    def postcleanup(self):
        # Cleans the layer 4-7 traffic for created CX end points
        self.http_profile.cleanup()

    def cleanup(self,os_types_dict):
        """
        Cleans up generic endpoints and associated CX endpoints based on operating system types.

        Parameters:
        - os_types_dict (dict): Dictionary mapping station identifiers to their respective operating system types.

        This method performs the following actions:
        1. Checks each station in os_types_dict against self.other_os_list.
        2. If a match is found, appends 'CX_yt-{station}' and 'yt-{station}' to created_cx and created_endp lists respectively.
        3. Logs a message indicating the start of generic endpoint cleanup.
        4. Calls cleanup method of generic_endps_profile to remove created endpoints.
        5. Clears created_cx and created_endp lists.
        6. Logs a message indicating successful cleanup.
        """
        # Check each station in os_types_dict against self.other_os_list
        for station in os_types_dict:
            if any(item.startswith(station) for item in self.other_os_list):
                # Append CX and endpoint names to created_cx and created_endp lists
                self.generic_endps_profile.created_cx.append(
                    'CX_yt-{}'.format(station))
                self.generic_endps_profile.created_endp.append(
                    'yt-{}'.format(station))
        logging.info('Cleaning up generic endpoints if exists')
        # Call cleanup method of generic_endps_profile to remove created endpoints
        # self.generic_endps_profile.cleanup()
        # # Clear created_cx and created_endp lists
        # self.generic_endps_profile.created_cx = []
        # self.generic_endps_profile.created_endp = []
        logging.info('Cleanup Successful')
    
    def my_monitor_runtime(self):
        """
            Retrieves monitoring data for the created CX endpoints based on specified data metrics.

            Parameters:
            - data_mon (str): Data metrics to monitor, provided as a string.

            Returns:
            - data1 (list): List containing monitoring data for the specified metrics across all created CX endpoints.

            This method performs the following actions:
            1. Constructs a URL to retrieve monitoring data from LANforge layer 4 API for all created CX endpoints.
            2. Retrieves JSON-formatted monitoring data using the constructed URL and specified metrics.
            3. Iterates through the retrieved data to extract and append the specified metric values ('data_mon') to 'data1' list.
            4. Returns 'data1', which contains monitoring data for the specified metrics across all created CX endpoints.
        """
        # data in json format
        # Construct URL to retrieve monitoring data for all created CX endpoints
        data = self.local_realm.json_get("layer4/%s/list?fields=name,status,total-urls,urls/s,uc-min,uc-avg,uc-max,total-err,bad-proto,bad-url,rslv-p,rslv-h,!conn,timeout" %
                                        (','.join(self.created_cx.keys())))
       
        
        # print("dataaa",data)
        data1 = []
        
        names = []
        statuses = []
        total_urls = []
        urls_per_sec = []
        uc_min = []
        uc_avg = []
        uc_max = []
        total_err = []
        bad_proto = []
        bad_url = []
        rslv_p = []
        rslv_h = []
        conn = []
        timeouts = []
        # Check if only one CX endpoint is created
        if len(self.created_cx.keys()) >1:
            data = data['endpoint']
            for endpoint in data:
                for key, value in endpoint.items():
                    names.append(value['name'])
                    statuses.append(value['status'])
                    total_urls.append(value['total-urls'])
                    urls_per_sec.append(value['urls/s'])
                    uc_min.append(value['uc-min'])
                    uc_avg.append(value['uc-avg'])
                    uc_max.append(value['uc-max'])
                    total_err.append(value['total-err'])
                    bad_proto.append(value['bad-proto'])
                    bad_url.append(value['bad-url'])
                    rslv_p.append(value['rslv-p'])
                    rslv_h.append(value['rslv-h'])
                    conn.append(value['!conn'])
                    timeouts.append(value['timeout'])
        elif len(self.created_cx.keys()) == 1:
            endpoint = data.get('endpoint', {})
            names = [endpoint.get('name', '')]
            statuses = [endpoint.get('status', '')]
            total_urls = [endpoint.get('total-urls', 0)]
            urls_per_sec = [endpoint.get('urls/s', 0.0)]
            uc_min = [endpoint.get('uc-min', 0)]
            uc_avg = [endpoint.get('uc-avg', 0.0)]
            uc_max = [endpoint.get('uc-max', 0)]
            total_err = [endpoint.get('total-err', 0)]
            bad_proto = [endpoint.get('bad-proto', 0)]
            bad_url = [endpoint.get('bad-url', 0)]
            rslv_p = [endpoint.get('rslv-p', 0)]
            rslv_h = [endpoint.get('rslv-h', 0)]
            conn = [endpoint.get('!conn', 0)]
            timeouts = [endpoint.get('timeout', 0)]



        # Print the results
        # print("Names:", names)
        # print("Statuses:", statuses)
        # print("Total URLs:", total_urls)
        # print("URLs/s:", urls_per_sec)
        # print("UC Min:", uc_min)
        # print("UC Avg:", uc_avg)
        # print("UC Max:", uc_max)
        # print("Total Errors:", total_err)
        # print("Bad Proto:", bad_proto)
        # print("Bad URL:", bad_url)
        # print("RSLV P:", rslv_p)
        # print("RSLV H:", rslv_h)
        # print("!Conn:", conn)
        # print("Timeouts:", timeouts)
        # print("data",data)

        self.data['status'] = statuses
        self.data["total_urls"] = total_urls
        self.data["urls_per_sec"] = urls_per_sec
        self.data["uc_min"] = uc_min
        self.data["uc_avg"] = uc_avg
        self.data["uc_max"] = uc_max
        self.data["name"] = names
        self.data["total_err"] = total_err
        self.data["bad_proto"] = bad_proto
        self.data["bad_url"] =  bad_url
        self.data["rslv_p"] = rslv_p
        self.data["rslv_h"] = rslv_h
        self.data["!conn"] = conn
        self.data["timeout"] = timeouts
        # if len(self.created_cx.keys()) == 1 :
        #     for cx in self.created_cx.keys():
        #         if cx in data['name']:
        #             data1.append(data[data_mon])
        # else:
        #     # Iterate through each created CX endpoint
        #     for cx in self.created_cx.keys():
        #         for info in data:
        #             if cx in info:
        #                 data1.append(info[cx][data_mon])
        # return data1

    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        data1 = []
        
        if "endpoint" not in data.keys():
            logger.error("Error: 'endpoint' key not found in port data")
            exit(1)
        data = data['endpoint']
    
        if len(self.http_profile.created_cx.keys()) == 1 :
            for cx in self.http_profile.created_cx.keys():
                if cx in data['name']:
                    data1.append(data[data_mon])
        else:
            for cx in self.http_profile.created_cx.keys():
                for info in data:
                    if cx in info:
                        data1.append(info[cx][data_mon])
        return data1
    
    def set_available_resources_ids(self,available_list):
        self.resource_ids=available_list
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
        # print("ssss",self.resource_ids)
        resource_id_list = []
        phone_name_list = []
        mac_address = []
        user_name = []
        phone_radio = []
        rx_rate = []
        tx_rate = []
        station_name = []
        ssid = []

        # Retrieve data from LANforge port Manager tab including alias, MAC address, mode, parent device, RX rate, TX rate, SSID, and signal strength
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,phantom")
        resource_ids = []
        if self.resource_ids:
            # Convert self.resource_ids to a list of integers if provided
            resource_ids = list(map(int, self.resource_ids.split(',')))
        # Iterate through each row in eid_data["interfaces"]
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and not alias[i]["phantom"]:
                    resource_id_list.append(i.split(".")[1])
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    # Check if the hardware version does not start with ('Win', 'Linux', 'Apple') and the resource ID is in resource_ids
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        station_name.append(i)
                    mac = alias[i]["mac"]
                    rx = "Unknown" if (alias[i]["rx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["rx-rate"]
                    tx = "Unknown" if (alias[i]["tx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["tx-rate"]
                    ssid.append(alias[i]["ssid"])
                    rx_rate.append(rx)
                    tx_rate.append(tx)
                    # Get username from resource_hw_data
                    user = resource_hw_data['resource']['user']
                    user_name.append(user)
                    # Get user hardware details/name from resource_hw_data
                    hw_name = resource_hw_data['resource']['hw version'].split(" ")
                    name = " ".join(hw_name[0:2])
                    phone_name_list.append(name)
                    mac_address.append(mac)
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and alias[i]["parent dev"] == 'wiphy0':
                    # Map radio name to human-readable format
                    if 'a' not in alias[i]['mode'] or "20" in alias[i]['mode']:
                        phone_radio.append('2G')
                    elif 'AUTO' in alias[i]['mode']:
                        phone_radio.append("AUTO")
                    else:
                        phone_radio.append('2G/5G')
        return station_name

    def monitor_for_runtime_csv(self,duration,file_path,iteration,resource_list_sorted = [],cx_list = [], ):
        """
            Monitors runtime data for a specified duration and saves it to a CSV file.

            Parameters:
            - duration: int, duration in minutes for monitoring
            - file_path: str, path to save the CSV file
            - resource_list_sorted: list, sorted list of resource IDs
            - cx_list: list, list of CX (connection) IDs to monitor

            Returns: None
        """
        # if not self.all_cx_list :
        #     final_end_time_webGUI = datetime.now() + timedelta(minutes=int(self.total_duration))
        #     final_end_time_webGUI = str(final_end_time_webGUI.isoformat()[0:19])
        #     dt = datetime.strptime(final_end_time_webGUI, "%Y-%m-%dT%H:%M:%S")
        #     self.formatted_endtime_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        #     print("formatted_endtime_str",self.formatted_endtime_str)


        self.all_cx_list.extend(cx_list) 

        resource_ids = list(map(int, self.resource_ids.split(',')))
        self.data_for_webui['resources'] = resource_ids
        starttime = datetime.now()
        # Get names of connections (CX) from my_monitor method
        self.data["name"] = self.my_monitor('name')
        df = pd.DataFrame(self.data)
        # If 'start_time' column not present, initialize it to 0
        # if 'start_time' not in df.columns:
        #     df['start_time'] = 0 

        # self.data['start_time'] = [starttime] * len(self.data["name"])
        # self.data['start_time'] = df.apply(
        #     lambda row: (
        #         datetime.now()  # Accumulate inc_value
        #         if row['start_time'] == 0 and row['name'] in cx_list 
        #         else row['start_time']  # Keep existing inc_value
        #     ), 
        #     axis=1
        # ) 

        current_time = datetime.now()
        endtime = ""
        endtime = starttime + timedelta(minutes=duration)
        # final_end_time_webGUI = str(starttime + timedelta(minutes=self.total_duration))
        endtime = endtime.isoformat()[0:19]

        # dt = datetime.strptime(final_end_time_webGUI, "%Y-%m-%d %H:%M:%S")
        # formatted_endtime_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        # if 'end_time' not in df.columns:
        #     df['end_time'] = 0

        # Set end_time and remaining_time_webGUI if dowebgui is True
        if self.dowebgui:
            # self.data['end_time'] = [endtime] * len(self.data["name"])
            end_time = datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S") 
            self.data["remaining_time"] = [end_time - current_time] * len(self.data['name'])
        # else:
        #     # Set end_time based on conditions for items in cx_list
        #     # self.data['end_time'] = [0] * len(self.data["name"])
        #     self.data['end_time'] = df.apply(
        #         lambda row: (
        #             endtime  # Set endtime if end_time is 0 and name is in cx_list
        #             if row['end_time'] == 0 and row['name'] in cx_list 
        #             else row['end_time'] # Keep existing end_time
        #         ), 
        #         axis=1
        #     )
 
        endtime_check = datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S")
        self.data['status'] = self.my_monitor('status')
        self.data['required_count'] = [self.count] * len(self.data['name'])
        self.data['duration'] = [duration] * len(self.data['name'])
        self.data['url'] = [self.url] * len(self.data['name'])

        # Retrieve device information from LANforge ports
        device_type = []
        username = []
        ssid = []
        mac = []
        channel = []
        mode = []
        rssi = []
        channel = []
        tx_rate = []
        rx_rate = []

        resource_ids = list(map(int, self.resource_ids.split(',')))
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")

        for alias in eid_data["interfaces"]:
            for i in alias:
                # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    # Filter based on hw_version and resource_ids
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids :
                        # Collect device information
                        device_type.append('Android')
                        username.append(resource_hw_data['resource']['user'] )
                        ssid.append(alias[i]['ssid'])
                        mac.append(alias[i]['mac'])
                        mode.append(alias[i]['mode'])
                        rssi.append(alias[i]['signal'])
                        channel.append(alias[i]['channel'])
                        tx_rate.append(alias[i]['tx-rate'])
                        rx_rate.append(alias[i]['rx-rate'])
        # Store device information in self.data
        self.data['device_type'] = device_type
        self.data['username'] = username
        self.data['ssid'] = ssid
        self.data['mac'] = mac 
        self.data['mode'] = mode 
        self.data['rssi'] = rssi
        self.data['channel'] = channel
        # self.data['tx_rate'] = tx_rate 
        # self.data['rx_rate'] = rx_rate

        temp = []
        # Initialize temp list for storing time data
        for i in range(len(self.all_cx_list)):
            temp.append(-1)

        iterator = []
        # Monitoring loop until current_time exceeds endtime
        start_time_check=datetime.now()
        while current_time < endtime_check or self.background_run:
            # Update end_time_webGUI
            if self.data['end_time_webGUI'][0] < current_time.strftime('%Y-%m-%d %H:%M:%S'):
                self.data['end_time_webGUI'] = [current_time.strftime('%Y-%m-%d %H:%M:%S')] * len(self.data['name'])
            curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            endtime_dt = datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S")
            curr_time_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
            remaining_time_dt = endtime_dt - curr_time_dt
            one_minute = timedelta(minutes=1)
            # Update remaining_time_webGUI
            if remaining_time_dt < one_minute:
                self.data['remaining_time_webGUI'] = ["< 1 min"] * len(self.data['status']) 
            else:
                self.data['remaining_time_webGUI'] = [str(datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S"))] * len(self.data['status']) 

            c = 0
            # Update status and other metrics using my_monitor method
            # self.data['status'] = self.my_monitor('status')
            # self.data["total_urls"] = self.my_monitor('total-urls')
            # self.data["urls_per_sec"] = self.my_monitor('urls/s')
            # self.data["uc_min"] = self.my_monitor('uc-min')
            # self.data["uc_avg"] = self.my_monitor('uc-avg')
            # self.data["uc_max"] = self.my_monitor('uc-max')
            # self.data["name"] = self.my_monitor('name')
            # self.data["total_err"] = self.my_monitor('total-err')
            # self.data["bad_proto"] = self.my_monitor('bad-proto')
            # self.data["bad_url"] = self.my_monitor('bad-url')
            # self.data["rslv_p"] = self.my_monitor('rslv-p')
            # self.data["rslv_h"] = self.my_monitor('rslv-h')
            # self.data["!conn"] = self.my_monitor('!conn')
            # self.data["timeout"] = self.my_monitor('timeout')
            self.my_monitor_runtime()


            # Store metrics specific to this iteration
            if cx_list:
                iterator = self.all_cx_list
            else:
                iterator = resource_ids 

            # len_cx_list = len(cx_list)
            # len_all_cx_list = len(self.all_cx_list)
            for i in range(len(iterator)):
                
                if self.all_cx_list[i] in cx_list:
                   
                    # Handle present value conditions
                    if self.data['total_urls'][i] == self.count or self.data['total_urls'][i] > self.count:
                        if temp[i] == -1:
                            temp[i] = int(abs(( datetime.now() - start_time_check ).total_seconds()))
                    else:
                        
                        if temp[i] == 0:
                            temp[i] = 0
                else:   
                    # Handle conditions based on total_urls_dict varibale
                    # print(self.total_urls_dict)
                    if self.total_urls_dict:
                        if ((self.data['total_urls'][i] - self.total_urls_dict[self.all_cx_list[i]][-1]) == self.count or (self.data['total_urls'][i] - self.total_urls_dict[self.all_cx_list[i]][-1]) > self.count):
                            
                            if temp[i] == -1:
                                temp[i] = int(abs(( datetime.now() - start_time_check ).total_seconds()))



            # Check if the test is stopped by the user via web GUI
            if self.dowebgui == True:
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                self.test_name),'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logging.info('Test is stopped by the user')
                        k = 0
                        # Reset time_data if test is stopped
                        for num in self.time_data:                                
                            for j in range(len(num)):
                                if self.time_data[k][j] == -1:
                                    self.time_data[k][j] = 0 
                            k+=1
                        self.data["end_time"] = [datetime.now().strftime("%d/%m %I:%M:%S %p")] * len(self.data["end_time"])
                        break

            elif self.stop_test:
                logging.info('Test is stopped by the user')
                k = 0
                # Reset time_data if test is stopped
                for num in self.time_data:                                
                    for j in range(len(num)):
                        if self.time_data[k][j] == -1:
                            self.time_data[k][j] = 0 
                    k+=1
                # self.data["end_time"] = [datetime.now().strftime("%d/%m %I:%M:%S %p")] * len(self.data["end_time"])
                self.test_stopped_by_user=True
                break


            # Update DataFrame with current data
            # print(self.data)
            try:
                df1 = pd.DataFrame(self.data)
            except Exception as e:
                print(self.data)
                logger.exception("Exception occured while monitoring real time data")
                exit(1)
            

            # Save data to CSV file based on dowebgui condition
            if self.dowebgui == True:
                df1.to_csv('{}/rb_datavalues.csv'.format(self.result_dir), index=False)
            else:
                df1.to_csv(file_path, mode='w', index=False)

            # Sleep for 1 second before next iteration
            time.sleep(1)
            
            current_time = datetime.now()

            if not self.background_run and self.background_run is not None:
                break
        
        # Finalize end_time_webGUI
        if self.data['end_time_webGUI'][0] < current_time.strftime('%Y-%m-%d %H:%M:%S'):
            self.data['end_time_webGUI'] = [current_time.strftime('%Y-%m-%d %H:%M:%S') ] * len(self.data['name'])

            curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            curr_time_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
            endtime_dt = datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S")
            self.data['remaining_time_webGUI'] = ["< 1 min"] * len(self.data['status']) 
        else:
            self.data['remaining_time_webGUI'] = [str(datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S"))] * len(self.data['status']) 

        
        # self.my_monitor_runtime()


        if cx_list:
            name = self.data['name']
            total_urls = self.data['total_urls']
            def add_to_dict(index):
                for num in index:
                    key = name[num]
                    value = total_urls[num] 
                    if key in self.total_urls_dict:
                        self.total_urls_dict[key].append(value)
                    else:
                        self.total_urls_dict[key] = [value]

            # Iterate through the name and total_urls lists
            index = []
            for name_1 in self.all_cx_list:
                i = 0
                for name_2 in name:
                    if name_1 == name_2:
                        index.append(i)
                        break 
                    i += 1
            add_to_dict(index)

        # len_cx_list = len(cx_list)
        # len_all_cx_list = len(self.all_cx_list)

        # Store time data in self.time_data and reset end_time if stopped
      
        for i in range(len(iterator)):
            if self.all_cx_list[i] in cx_list: 
                # present value
                if self.data['total_urls'][i] == self.count or self.data['total_urls'][i] > self.count:
                    if temp[i] == -1:
                        temp[i] = int(abs(( datetime.now() - start_time_check ).total_seconds()))
                else:
                    if temp[i] == 0:
                        temp[i] = 0
            else:   
                if self.total_urls_dict:
                    if (self.data['total_urls'][i] - self.total_urls_dict[self.all_cx_list[i]][-1]) == self.count or (self.data['total_urls'][i] - self.total_urls_dict[self.all_cx_list[i]][-1]) > self.count:
                        if temp[i] == -1:
                            temp[i] = int(abs(( datetime.now() - start_time_check ).total_seconds()))
        
        prev_cx_list = len(self.all_cx_list) - len(cx_list)
        for i in range(prev_cx_list):
            if temp[i] == -1:
                temp[i] = 0
        if -1 in temp:
            for i in range(len(temp)):
                if temp[i] == -1:
                    temp[i] = 0
        self.time_data.append(temp) 

        # Storing the necessary data to generate the graph for multiple incremetnal values
        labels = []
        total_urls_dict_copy = self.total_urls_dict.copy()
        keys = list(total_urls_dict_copy.keys())

        usernames_csv = {}
        
        try:
            df = pd.DataFrame(self.data)
        except Exception as e:
            print(self.data)
            logger.exception("Exception occured while monitoring real time data")
            exit(1)
        df.apply(
            lambda row: (
                usernames_csv.update({row['name']: row['username']})
                if row['name'] in self.all_cx_list
                else None
            ),
            axis=1
        )

        
        temp_usernames = []
        idx = 0
        for i in self.all_cx_list:
            if idx < len(keys) and keys[idx] in total_urls_dict_copy and total_urls_dict_copy[keys[idx]]:
                if keys[idx] in usernames_csv:
                    temp_usernames.append(usernames_csv[keys[idx]])
                    labels.append(temp_usernames)
            idx+=1

        if labels:
            device_type = []
            username = []
            ssid = []
            mac = []
            channel = []
            mode = []
            rssi = []
            channel = []
            tx_rate = []

            resource_ids = list(map(int, self.resource_ids.split(',')))
            eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")

            temp_username = []
            temp_device_type = []
            temp_ssid = []
            temp_mac = []
            temp_mode = []
            temp_rssi = []
            temp_channel = []
            temp_tx_rate = []
            for alias in eid_data["interfaces"]:
                for i in alias:
                    # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids and resource_hw_data['resource']['user'] in labels[-1]:
                            temp_device_type.append('Android')
                            temp_username.append(resource_hw_data['resource']['user'] )
                            temp_ssid.append(alias[i]['ssid'])
                            temp_mac.append(alias[i]['mac'])
                            temp_mode.append(alias[i]['mode'])
                            temp_rssi.append(alias[i]['signal'])
                            temp_channel.append(alias[i]['channel'])
                            temp_tx_rate.append(alias[i]['tx-rate']) 
            self.username.append(temp_username)
            self.device_type.append(temp_device_type)
            self.ssid.append(temp_ssid)
            self.mac.append(temp_mac)
            self.mode.append(temp_mode)
            self.rssi.append(temp_rssi)
            self.channel.append(temp_channel)
            self.tx_rate.append(temp_tx_rate)

            total_urls = self.data['total_urls']
            uc_min_val = self.data['uc_min']
            uc_max_val = self.data['uc_max']
            uc_avg_val = self.data['uc_avg']
            total_err = self.data['total_err']
            status = self.my_monitor('status')
            temp_total_urls = []
            temp_uc_min_val = []
            temp_uc_max_val = []
            temp_uc_avg_val = []
            temp_total_err = []
            for k in range(len(status[0:iteration])):
                # if status[k] == 'Run':
                temp_total_urls.append(total_urls[k])
                temp_uc_min_val.append(uc_min_val[k])
                temp_uc_avg_val.append(uc_avg_val[k])
                temp_uc_max_val.append(uc_max_val[k])
                temp_total_err.append(total_err[k])
                

            self.req_total_urls.append(temp_total_urls)
            self.req_uc_min_val.append(temp_uc_min_val)
            self.req_uc_avg_val.append(temp_uc_avg_val)
            self.req_uc_max_val.append(temp_uc_max_val)
            self.req_total_err.append(temp_total_err)
        try:
            df = pd.DataFrame(self.data)
        except Exception as e:
            print(self.data)
            logger.exception("Exception occured while monitoring real time data")
            exit(1)

        # Store final data in CSV file based on dowebgui condition
        if self.dowebgui == True:   
            df.to_csv('{}/rb_datavalues.csv'.format(self.result_dir), index=False)
        else:
            df.to_csv(file_path, mode='w', index=False)     

    def generate_graph(self, dataset, lis, bands, graph_image_name = "Time_taken_to_reach_urls"):
        bands=["Time (in sec)"]
        x_fig_size = 18
        y_fig_size = len(lis)*.5 + 4
        graph = lf_bar_graph_horizontal(_data_set=[dataset], _xaxis_name="Time (in seconds)",
                                            _yaxis_name="Devices",
                                            _yaxis_categories=[i for i in lis],
                                            _yaxis_label=[i for i in lis],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="Time Taken",
                                            _title_size=16,
                                            _figsize= (x_fig_size,y_fig_size),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['steelblue'],
                                            _bar_height=.50,
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name=graph_image_name,
                                            _color_edge=['black'],
                                            _color=['steelblue'],
                                            _label=bands)
        graph_png = graph.build_bar_graph_horizontal()
        return graph_png

    def graph_2(self, dataset2, lis, bands,graph_image_name = "Total-url"):
        x_fig_size = 18
        y_fig_size = len(lis)*.5 + 4
        graph_2 = lf_bar_graph_horizontal(_data_set=[dataset2], _xaxis_name="URLs",
                                            _yaxis_name="Devices",
                                            _yaxis_categories=[i for i in lis],
                                            _yaxis_label=[i for i in lis],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="URLs",
                                            _title_size=16,
                                            _figsize= (x_fig_size,y_fig_size),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['orange'],
                                            _bar_height=.50,
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name=graph_image_name,
                                            _color_edge=['black'],
                                            _color=['orange'],
                                            _label=bands)
        graph_png = graph_2.build_bar_graph_horizontal()
        return graph_png

    def generate_multiple_graphs(self, report, cx_order_list,gave_incremental):
        """
            Generates multiple graphs and reports based on monitored data.

            Parameters:
            - report: Report object for generating and storing reports
            - cx_order_list: List specifying the order of connections (CX)

            Returns: None
        """
        bands = ['URLs']
        # total_urls = self.my_monitor('total-urls')
        usernames_csv = {}
        # df = pd.DataFrame(self.data)
        try:
            df = pd.DataFrame(self.data)
        except Exception as e:
            print(self.data)
            logger.exception("Exception occured while monitoring real time data")
            exit(1)
        # Update usernames_csv with names and usernames in the dataframe df, if name is in all_cx_list
        df.apply(
            lambda row: (
                usernames_csv.update({row['name']: row['username']})
                if row['name'] in self.all_cx_list
                else None
            ),
            axis=1
        )
        

        # Copy total_urls_dict for manipulation
        total_urls_dict_copy = self.total_urls_dict.copy()

        # Initialize lists and variables for incremental graph data
        dataset2 = []
        labels = []
        incremental_temp = []
        created_incremental_values = []

        keys = list(total_urls_dict_copy.keys())
        index = 0
        # Handle different scenarios for setting incremental values
        if len(self.incremental) == 1 and self.incremental[0] == len(keys):
            incremental_temp.append(len(keys[index:]))
        elif len(self.incremental) == 1 and len(keys) > 1:
            incremental_value = self.incremental[0]
            div = len(keys)//incremental_value 
            mod = len(keys)%incremental_value 

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

        # Iterate over created_incremental_values to generate dataset2 and labels
        for i in created_incremental_values:
            temp_urls = []
            temp_usernames = []
            idx = 0
            # Fetch URLs and usernames for each incremental value
            for j in range(i):
                if j < len(keys) and keys[j] in total_urls_dict_copy and total_urls_dict_copy[keys[j]]:
                    temp_urls.append(total_urls_dict_copy[keys[j]][0])
                    total_urls_dict_copy[keys[j]].pop(0)
                    if keys[j] in usernames_csv:
                        if usernames_csv[keys[j]]:
                            temp_usernames.append(usernames_csv[keys[j]])
            # Append temp_urls to dataset2 and temp_usernames to labels
            if temp_urls:
                dataset2.append(temp_urls)
            if temp_usernames:
                labels.append(temp_usernames)

        # Initialize final_dataset to store processed incremental values
        final_dataset = []
        idx = 0
        prev_list = []
        to_break = 0
        # Iterate over dataset2 to calculate incremental values and prepare final_dataset
        for num_list in dataset2:
            temp = []
            if idx == 0:
                final_dataset.append(num_list)
            else:
                for j in range(len(prev_list)):
                    if num_list:
                        if num_list != 0:
                            temp.append(num_list[j] - prev_list[j])
                        else:
                            temp.append(0)
                    else:
                        to_break = 1
                        break
                temp.extend(num_list[len(prev_list):])
                final_dataset.append(temp)
            if num_list:
                prev_list = []
                prev_list.extend(num_list)
            idx+=1
            if to_break:
                break
        
        bands = ['URLs']

        # Iterate over labels to generate graphs and reports
        for i in range(len(labels)):
            if gave_incremental:
                report.set_obj_html(f'Iteration {i+1}',"")
                report.build_objective()
                report.set_obj_html(f"RealTime URL per device- Number of Devices on running {created_incremental_values[i]}","")
                report.build_objective()
            else:
                report.set_obj_html(f"RealTime URL per device- Number of Devices on running {created_incremental_values[i]}","")
                report.build_objective()
            # Generate and set graph 2 (Total URLs vs Labels) using graph_2 method
            graph2 = self.graph_2(dataset2=final_dataset[i], lis=labels[i], bands=bands,graph_image_name =  f'Total-url-{i}.png' )

            report.set_graph_image(graph2)
            report.set_csv_filename(graph2)
            report.move_csv_file()
            report.move_graph_image()
            report.build_graph()
            # Set objective HTML for time vs device completion and build objective
            if gave_incremental:
                report.set_obj_html(f"Iteration {i+1} - Time taken Vs Device For Completing {self.count} RealTime URLs","")
                report.build_objective()
            else:
                report.set_obj_html(f"Time taken Vs Device For Completing {self.count} RealTime URLs","")
                report.build_objective()

            # Generate and set graph (Time vs Device) using generate_graph method
            graph = self.generate_graph(dataset=self.time_data[i], lis = labels[i], bands = bands,graph_image_name =  f'Time_taken_to_reach_url{i}.png')
            report.set_graph_image(graph)
            report.set_csv_filename(graph)
            report.move_csv_file()
            report.move_graph_image()
            report.build_graph()

            if gave_incremental:
                report.set_obj_html(f"Detailed Result Table - Iteration {i+1} ", f"The below tables provides detailed information for the incremental value {created_incremental_values[i]} of the web browsing test.")
                report.build_objective()
            else:
                report.set_obj_html(" Detailed Result Table", "The below tables provides detailed information for the web browsing test.")
                report.build_objective()
            

            # Prepare dataframe with detailed result information
            dataframe = {
                " DEVICE TYPE " : self.device_type[i],
                " Username " : self.username[i],
                " SSID " : self.ssid[i] ,
                " MAC " : self.mac[i],
                " Channel " : self.channel[i],
                " Mode " : self.mode[i],
                " UC-MIN (ms) " : self.req_uc_min_val[i],
                " UC-MAX (ms) " : self.req_uc_max_val[i],
                " UC-AVG (ms) " : self.req_uc_avg_val[i],
                " Total URLs " : self.req_total_urls[i],
                " Total Errors " : self.req_total_err[i],
                " RSSI " : self.rssi[i],
                'Link Speed': self.tx_rate[i]
            }

            
            try:
                dataframe1 = pd.DataFrame(dataframe)
                report.set_table_dataframe(dataframe1)
                report.build_table()
            except Exception as e:
                print(dataframe)
                logger.exception("Exception occured while monitoring real time data")
                exit(1)
            

    def generate_report(self, date, file_path,test_setup_info, dataset2, dataset, lis, bands, total_urls, uc_min_value, report_path = '', cx_order_list = [],gave_incremental=True):
        logging.info("Creating Reports")
        if self.dowebgui == True and report_path == '':
            report = lf_report.lf_report(_results_dir_name="Web_Browser_Test_report", _output_html="web_browser.html",
                                        _output_pdf="Webbrowser.pdf", _path=self.result_dir)
        else:
            report = lf_report.lf_report(_results_dir_name="Web_Browser_Test_report", _output_html="web_browser.html",
                                        _output_pdf="Webbrowser.pdf", _path=report_path)
        report_path_date_time = report.get_path_date_time()
        shutil.move('webBrowser.csv',report_path_date_time)
        report.set_title("Web Browser Test")
        report.set_date(date)
        report.build_banner()
        report.set_obj_html("Objective", "The Candela Web browser test is designed to measure the Access Point performance and stability by browsing multiple websites in real clients like"
        "android, Linux, windows, and IOS which are connected to the access point. This test allows the user to choose the options like website link, the"
        "number of times the page has to browse, and the Time taken to browse the page. Along with the performance other measurements made are client"
        "connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the AP to be able to handle several stations"
        "(within the limitations of the AP specs) and make sure all clients can browse the page.")
        report.build_objective()
        report.set_table_title("Input Parameters")
        report.build_table_title()

        report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        
        
        
       
        # Graph 1
        if cx_order_list:
            self.generate_multiple_graphs(report, cx_order_list,gave_incremental) 
        else:
            graph2 = self.graph_2(dataset2 = dataset2, lis=lis, bands=bands)
            report.set_graph_image(graph2)
            report.set_csv_filename(graph2)
            report.move_csv_file()
            report.move_graph_image()
            report.build_graph()

            # Graph 2
            report.set_obj_html(f"Time taken Vs Device For Completing {self.count} RealTime URLs","")
            report.build_objective()
            graph = self.generate_graph(dataset=dataset, lis = lis, bands = bands)
            report.set_graph_image(graph)
            report.set_csv_filename(graph)
            report.move_csv_file()
            report.move_graph_image()
            report.build_graph()

        # Table 1
        report.set_obj_html("Detailed Total Errors Table", "The below tables provides detailed information of total errors for the web browsing test.")
        report.build_objective()

        device_type = []
        username = []
        ssid = []
        mac = []
        channel = []
        mode = []
        rssi = []
        channel = []
        tx_rate = []
        resource_ids = list(map(int, self.resource_ids.split(',')))
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")


        for alias in eid_data["interfaces"]:
            for i in alias:
                # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        device_type.append('Android')
                        username.append(resource_hw_data['resource']['user'] )
                        ssid.append(alias[i]['ssid'])
                        mac.append(alias[i]['mac'])
                        mode.append(alias[i]['mode'])
                        rssi.append(alias[i]['signal'])
                        channel.append(alias[i]['channel'])
                        tx_rate.append(alias[i]['tx-rate']) 
        total_urls = self.data["total_urls"]
        urls_per_sec = self.data["urls_per_sec"]
        uc_min_val = self.data['uc_min']
        uc_avg_val = self.data['uc_avg']
        uc_max_val = self.data['uc_max']
        total_err = self.data['total_err'] 
        # dataframe = {
        #     " DEVICE TYPE " : device_type,
        #     " Username " : username,
        #     " SSID " : ssid ,
        #     " MAC " : mac,
        #     " Channel " : channel,
        #     " Mode " : mode,
        #     " UC-MIN (ms) " : uc_min_val,
        #     " UC-MAX (ms) " : uc_max_val,
        #     " UC-AVG (ms) " : uc_avg_val,
        #     " Total URLs " : total_urls,
        #     " Total Errors " : total_err,
        #     " RSSI " : rssi,
        #     'Link Speed': tx_rate
        # }

        # dataframe1 = pd.DataFrame(dataframe)
        # report.set_table_dataframe(dataframe1)
        # report.build_table()

        # # Table 2
        # report.set_table_title("Overall Results")
        # report.build_table_title()
        dataframe2 = {
                        " DEVICE" : username,
                        " TOTAL ERRORS " : total_err,
                    }

        dataframe3 = pd.DataFrame(dataframe2)
        report.set_table_dataframe(dataframe3)
        report.build_table()
        report.build_footer()
        html_file = report.write_html()
        report.write_pdf()

        if self.dowebgui == True:
            for i in range(len(self.data["end_time_webGUI"])):
                if self.data["status"][i] == "Run":
                    self.data["status"][i] = "Completed"
            df = pd.DataFrame(self.data)
            if self.dowebgui == True:
                df.to_csv('{}/rb_datavalues.csv'.format(self.result_dir), index=False)

def main():
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
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --debug

            CASE-1:
            If not specified it takes the default url (default url is www.google.com)

        Example-2:
        Command Line Interface to run url in the Browser with specified Resources:
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --debug

        Example-3:
        Command Line Interface to run url in the Browser with specified urls_per_tennm (specify the number of url you want to test in the given duration):
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --debug

            CASE-1:
            If not specified it takes the default count value (default count is 100)

        Example-4:
        Command Line Interface to run the the Real Browser test with incremental Capacity by specifying the --incremental flag
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --incremental --debug

        Example-5:
        Command Line Interface to run the the Real Browser test in webGUI by specifying the --dowebgui flag
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --count 10 --dowebgui --debug

        Example-6:
        Command Line Interface to run url in the Browser with precleanup:
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --precleanup --debug

        Example-7:
        Command Line Interface to run url in the Browser with postcleanup:
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --postcleanup --debug

        Example-8:
        Command Line Interface to run url in the Browser with incremental capacity:
        python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "www.google.com" --duration 10m --device_list 1.10,1.12 --incremental_capacity 1 --debug
        
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

        
    optional=parser.add_argument_group('Optional arguments to run lf_interop_real_browser_test.py')
    parser.add_argument("--host", "--mgr", required = True, help='specify the GUI to connect to, assumes port '
                                                                        '8080')
    parser.add_argument("--ssid", default="ssid_wpa_2g", help='specify ssid on which the test will be running')
    parser.add_argument("--passwd", default="something", help='specify encryption password  on which the test will '
                                                        'be running')
    parser.add_argument("--encryp", default="psk", help='specify the encryption type  on which the test will be '
                                                        'running eg :open|psk|psk2|sae|psk2jsae')
    parser.add_argument("--url", default="www.google.com", help='specify the url you want to test on')
    parser.add_argument("--max_speed", type=int, default=0, help='specify the max speed you want in bytes')
    parser.add_argument("--count", type=int, default=1, help='specify the number of url you want to calculate time to reach'
                                                                    )
    parser.add_argument('--duration', type=str, help='time to run traffic')
    optional.add_argument('--test_name',help='Specify test name to store the runtime csv results', default=None)
    parser.add_argument('--dowebgui',help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--result_dir',help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')

    parser.add_argument("--lf_logger_config_json", help="[log configuration] --lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument("--log_level", help="[log configuration] --log_level  debug info warning error critical")
    parser.add_argument("--debug", help="[log configuration] --debug store_true , used by lanforge client ", action='store_true')

    parser.add_argument('--device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
    parser.add_argument('--webgui_incremental','--incremental_capacity', help="Specify the incremental values <1,2,3..>",dest='webgui_incremental', type=str)
    parser.add_argument('--incremental', help="to add incremental capacity to run the test", action = 'store_true')
    optional.add_argument('--no_laptops', help="run the test without laptop devices", action = 'store_false')
    parser.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action = 'store_true')
    parser.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action = 'store_true')
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)

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

    # TODO refactor to be logger for consistency
    logg = logging.getLogger(__name__)


    # Extract the URL from args and remove 'http://' or 'https://'
    # url = args.url.replace("http://", "").replace("https://", "")

    # Initialize an instance of RealBrowserTest with various parameters
    obj = RealBrowserTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                        url=args.url, count=args.count, duration=args.duration, 
                        resource_ids = args.device_list, dowebgui = args.dowebgui,
                        result_dir = args.result_dir,test_name = args.test_name, incremental = args.incremental,postcleanup=args.postcleanup,
                        precleanup=args.precleanup)
    
    # Initialize empty lists and dictionaries for resource management
    resource_ids_sm = []
    resource_set = set()
    resource_list = []
    os_types_dict = {}
    # android_devices = []
    # other_os_list = []
    # android_list = []
    # other_list = []
    resource_ids_generated = ""
    #  Process resource IDs when web GUI is enabled
    if args.dowebgui == True :
        # Split resource IDs from args into a list
        resource_ids_sm = args.device_list.split(',')
        # Convert list to set to remove duplicates
        resource_set = set(resource_ids_sm)
        # Sort the set to maintain order
        resource_list = sorted(resource_set)
        # Generate a comma-separated string of sorted resource IDs
        resource_ids_generated = ','.join(resource_list)
        resource_list_sorted = resource_list
        # Query devices based on the generated resource IDs
        selected_devices,report_labels,selected_macs = obj.devices.query_user(dowebgui = args.dowebgui, device_list = resource_ids_generated)
        # Modify obj.resource_ids to include only the second part of each ID (after '.')
        obj.resource_ids = ",".join(id.split(".")[1] for id in args.device_list.split(","))
    else :
        # Case where args.no_laptops flag is set
        # if args.no_laptops:
            # Retrieve all Android devices if no_laptops flag is True
        obj.android_devices = obj.devices.get_devices(only_androids=True)
        # else:
        #     # Retrieve all devices and their OS types if no_laptops flag is False
        #     devices,os_types_dict = obj.devices.get_devices(androids=True,laptops=True)
        #     # Extract prefixes from device interfaces
        #     device_prefixes = ['.'.join(interface.split('.')[:2]) for interface in devices]
        #     # Categorize devices into Android and other OS types based on prefixes
        #     for index, prefix in enumerate(device_prefixes):
        #         os_type = os_types_dict.get(prefix)
        #         if os_type == 'android':
        #             obj.android_devices.append(devices[index])
        #         else:
        #             obj.other_os_list.append(devices[index])
        
        # Process resource IDs if provided
        if args.device_list:
            # Extract second part of resource IDs and sort them
            obj.resource_ids = ",".join(id.split(".")[1] for id in args.device_list.split(","))
            resource_ids_sm = obj.resource_ids
            resource_list = resource_ids_sm.split(',')            
            resource_set = set(resource_list)
            resource_list_sorted = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list_sorted)

            # Convert resource IDs into a list of integers
            num_list = list(map(int, obj.resource_ids.split(',')))

            # Sort the list
            num_list.sort()

            # Join the sorted list back into a string
            sorted_string = ','.join(map(str, num_list))
            obj.resource_ids = sorted_string

            # Extract the second part of each Android device ID and convert to integers
            modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))
            modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), obj.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
            # print(obj.resource_ids,obj.android_devices, modified_list, modified_other_os_list)
            # if not args.no_laptops:
            #     new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in obj.android_devices]
            #     new_list_other = [item.split('.')[0] + '.' + item.split('.')[1] for item in obj.other_os_list]
            #     resources_list = args.device_list.split(",")
            #     # Filter Android devices based on resource IDs
            #     for element in resources_list:
            #         if element in new_list_android:
            #             for ele in obj.android_devices:
            #                 if ele.startswith(element):
            #                     obj.android_list.append(ele)
            #         else:
            #             for ele in obj.other_os_list:
            #                 if ele.startswith(element):
            #                     obj.other_list.append(ele) 
            #     # Extract the second part of each Android device ID and sort them
            #     new_android = [int(item.split('.')[1]) for item in obj.android_list]

            #     resource_ids = sorted(new_android)
            #     resource_list = sorted(new_android)
            #     obj.resource_ids = ','.join(str(num) for num in sorted(new_android))
            #     resource_set = set(resource_list)
            #     resource_list_sorted = sorted(resource_set)

            # else:
            # Process Android devices when no_laptops flag is True
            new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in obj.android_devices]

            resources_list = args.device_list.split(",")
            for element in resources_list:
                if element in new_list_android:
                    for ele in obj.android_devices:
                        if ele.startswith(element):
                            obj.android_list.append(ele)
                else:
                    logger.info("{} device is not available".format(element))
            new_android = [int(item.split('.')[1]) for item in obj.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(set(resource_ids))
              
        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices,report_labels,selected_macs = obj.devices.query_user()
            # Handle cases where no devices are selected
            if not selected_devices:
                logging.info("devices donot exist..!!")
                return 
            # Categorize selected devices into Android and other OS types if no_laptops flag is False
            # if not args.no_laptops:
            #     for device in selected_devices:
            #         if device in obj.android_devices:
            #             obj.android_list.append(device)
            #         else:
            #             obj.other_list.append(device)
            # else:
            # Assign all selected devices as Android devices if no_laptops flag is True
            obj.android_list = selected_devices
            
            # if args.incremental and  (not obj.android_list):
            #     logging.info("Incremental Values are not needed as no android devices are selected")
            
            # Verify if all resource IDs are valid for Android devices
            if obj.android_list:
                resource_ids = ",".join([item.split(".")[1] for item in obj.android_list])

                num_list = list(map(int, resource_ids.split(',')))

                # Sort the list
                num_list.sort()

                # Join the sorted list back into a string
                sorted_string = ','.join(map(str, num_list))

                obj.resource_ids = sorted_string
                resource_ids1 = list(map(int, sorted_string.split(',')))
                modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))

                # Check for invalid resource IDs
                if not all(x in modified_list for x in resource_ids1):
                    logging.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = obj.resource_ids
                resource_list = resource_ids_sm.split(',')            
                resource_set = set(resource_list)
                resource_list_sorted = sorted(resource_set)
                resource_ids_generated = ','.join(resource_list_sorted)
                available_resources=list(resource_set)

    logger.info("Devices available: {}".format(available_resources))
    if len(available_resources)==0:
        logging.info("There no devices available which are selected")
        exit()
    # Handle incremental values input if resource IDs are specified and in not specified case.
    if args.incremental and not args.webgui_incremental :
        if obj.resource_ids:
            obj.incremental = input('Specify incremental values as 1,2,3 : ')
            obj.incremental = [int(x) for x in obj.incremental.split(',')]
        else:
            logging.info("incremental Values are not needed as Android devices are not selected..")
    
    # Handle webgui_incremental argument
    if args.webgui_incremental:
        incremental = [int(x) for x in args.webgui_incremental.split(',')]
        # Validate the length and assign incremental values
        if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
            obj.incremental = incremental
        elif len(args.webgui_incremental) == 1:
            obj.incremental = incremental

    # if obj.incremental and (not obj.resource_ids):
    #     logging.info("incremental values are not needed as Android devices are not selected.")
    #     exit()
    
    # Validate incremental and resource IDs combination
    if (obj.incremental and obj.resource_ids) or (args.webgui_incremental):
        resources_list1 = [str(x) for x in obj.resource_ids.split(',')]
        if resource_list_sorted:
            resources_list1 = resource_list_sorted
        # Check if the last incremental value is greater or less than resources provided
        if obj.incremental[-1] > len(available_resources):
            logging.info("Exiting the program as incremental values are greater than the resource ids provided")
            exit()
        elif obj.incremental[-1] < len(available_resources) and len(obj.incremental) > 1:
            logging.info("Exiting the program as the last incremental value must be equal to selected devices")
            exit()

    # obj.run
    test_time = datetime.now()
    test_time = test_time.strftime("%b %d %H:%M:%S")

    logging.info("Initiating Test...")
    available_resources= [int(n) for n in available_resources]
    available_resources.sort()
    available_resources_string=",".join([str(n) for n in available_resources])
    obj.set_available_resources_ids(available_resources_string)
    # obj.set_available_resources_ids([int(n) for n in available_resources].sort())
    obj.build()
    time.sleep(10)
    #TODO : To create cx for laptop devices
    # Create end-points for devices other than Android if specified
    # if (not args.no_laptops) and obj.other_list:
    #     obj.create_generic_endp(obj.other_list,os_types_dict)

    keys = list(obj.http_profile.created_cx.keys())
    if len(keys)==0:
        logger.error("Selected Devices are not available in the lanforge")
        exit(1)
    cx_order_list = []
    index = 0
    file_path = ""

    if args.duration.endswith('s') or args.duration.endswith('S'):
        args.duration = round(int(args.duration[0:-1])/60,2)
    
    elif args.duration.endswith('m') or args.duration.endswith('M'):
        args.duration = int(args.duration[0:-1]) 
 
    elif args.duration.endswith('h') or args.duration.endswith('H'):
        args.duration = int(args.duration[0:-1]) * 60  
    
    elif args.duration.endswith(''):
        args.duration = int(args.duration)

    if args.incremental or args.webgui_incremental:
        incremental_capacity_list_values=obj.get_incremental_capacity_list()
        if incremental_capacity_list_values[-1]!=len(available_resources):
            logger.error("Incremental capacity doesnt match available devices")
            if args.postcleanup==True:
                obj.postcleanup()
            exit(1)

    # Process resource IDs and incremental values if specified
    if obj.resource_ids:
        if obj.incremental:
            test_setup_info_incremental_values =  ','.join(map(str, incremental_capacity_list_values))
            if len(obj.incremental) == len(available_resources):
                test_setup_info_total_duration = args.duration
            elif len(obj.incremental) == 1 and len(available_resources) > 1:
                if obj.incremental[0] == len(available_resources):
                    test_setup_info_total_duration = args.duration
                else:
                    div = len(available_resources)//obj.incremental[0] 
                    mod = len(available_resources)%obj.incremental[0] 
                    if mod == 0:
                        test_setup_info_total_duration = args.duration * (div )
                    else:
                        test_setup_info_total_duration = args.duration * (div + 1)
            else:
                test_setup_info_total_duration = args.duration * len(incremental_capacity_list_values)
            # test_setup_info_duration_per_iteration= args.duration 
        elif args.webgui_incremental:
            test_setup_info_incremental_values = ','.join(map(str, incremental_capacity_list_values))
            test_setup_info_total_duration = args.duration * len(incremental_capacity_list_values)
        else:
            test_setup_info_incremental_values = "No Incremental Value provided"
            test_setup_info_total_duration = args.duration
        obj.total_duration = test_setup_info_total_duration

    # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
    gave_incremental,iteration_number=True,0
    if obj.resource_ids:
        if not obj.incremental:
            obj.incremental=[len(keys)]
            gave_incremental=False
        if obj.incremental or not gave_incremental:
            if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                cx_order_list.append(keys[index:])
            elif len(obj.incremental) == 1 and len(keys) > 1:
                incremental_value = obj.incremental[0]
                max_index = len(keys)
                index = 0

                while index < max_index:
                    next_index = min(index + incremental_value, max_index)
                    cx_order_list.append(keys[index:next_index])
                    index = next_index
            elif len(obj.incremental) != 1 and len(keys) > 1:
                
                index = 0
                for num in obj.incremental:
                    
                    cx_order_list.append(keys[index: num])
                    index = num

                if index < len(keys):
                    cx_order_list.append(keys[index:])
                    start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update start and end times for webGUI
            for i in range(len(cx_order_list)):
                if i == 0:
                    obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(keys)
                    # if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = args.duration)).strftime('%Y-%m-%d %H:%M:%S')
                    # elif len(obj.incremental) == 1 and len(keys) > 1:
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = args.duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                    # elif len(obj.incremental) != 1 and len(keys) > 1:
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = args.duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                    # if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                    # elif len(obj.incremental) == 1 and len(keys) > 1:
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                    # elif len(obj.incremental) != 1 and len(keys) > 1:
                    #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')

                    end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['end_time_webGUI'] = [end_time_webGUI] * len(keys)


                obj.start_specific(cx_order_list[i])
                
                iteration_number+=len(cx_order_list[i])
                if cx_order_list[i]:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                else:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                
                # duration = 60 * args.duration
                file_path = "webBrowser.csv"

                start_time = time.time()
                df = pd.DataFrame(obj.data)

                if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    obj.data['remaining_time_webGUI'] = ['0:00'] * len(keys)
                else:
                    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] * len(keys)
                # Monitor runtime and save results
                if args.dowebgui == True:
                    file_path = os.path.join(obj.result_dir, "../../Running_instances/{}_{}_running.json".format(obj.host, obj.test_name))
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            if data["status"] != "Running":
                                break 

                    obj.monitor_for_runtime_csv(args.duration,file_path,iteration_number,resource_list_sorted,cx_order_list[i])
                else:
                    obj.monitor_for_runtime_csv(args.duration,file_path,iteration_number,resource_list_sorted,cx_order_list[i])
                    # time.sleep(duration)
            
        # else:
        #     cx_order_list.append(keys[index:])
        #     obj.start()
        #     if obj.resource_ids:
        #         logging.info("Test started on Devices with resource Ids : {selected}".format(selected = available_resources))
        #     else:
        #         logging.info("Test started on Devices with resource Ids : {selected}".format(selected = available_resources))
            
        #     # Set duration and file path for monitoring
        #     duration = 60 * args.duration
        #     file_path = "webBrowser.csv"
            
            

        #     start_time = time.time()
            
        #     obj.data["name"] = obj.my_monitor('name')

        #     obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(keys)
        #     obj.data['end_time_webGUI'] = [(datetime.now() + timedelta(minutes = args.duration)).strftime('%Y-%m-%d %H:%M:%S')] * len(keys)

        #     # Monitor runtime and save results
        #     if args.dowebgui == True:
        #         # FOR WEBGUI, -This fumction is called to fetch the runtime data from layer-4
        #         obj.monitor_for_runtime_csv(args.duration,file_path,resource_list_sorted,cx_order_list)
        #     else:
        #         obj.monitor_for_runtime_csv(args.duration,file_path,resource_list_sorted,cx_order_list)
        # as test not running on laptop devices --- no waiting for time to complete
            # time.sleep(duration)

    # Stop the test execution
    obj.stop()

    # Generate CSV for webGUI results if dowebgui is True
    if args.dowebgui == True:
        df = pd.DataFrame(obj.data)
        df.to_csv('{}/rb_datavalues.csv'.format(obj.result_dir), index=False)

    # Additional setup for generating reports and post-cleanup
    if obj.resource_ids:
        # uc_avg_val = obj.my_monitor('uc-avg')
        total_urls = obj.my_monitor('total-urls')
        # rx_bytes_val = obj.my_monitor('bytes-rd')
        # rx_rate_val = obj.my_monitor('rx rate')

        if args.dowebgui == True:
            obj.data_for_webui["total_urls"] = total_urls  # storing the layer-4 url data at the end of test


        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

        # Retrieve resource data for Android devices
        phone_list = obj.get_resource_data() 

        # Initialize and retrieve username data
        username = []
        eid_data = obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")

        resource_ids = list(map(int, obj.resource_ids.split(',')))
        # Extract username information from resource data
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        username.append(resource_hw_data['resource']['user'] )

        # Construct device list string for report
        device_list_str = ','.join([f"{name} ( Android )" for name in username])

        # Setup test setup information for report
        test_setup_info = {
            "Testname" : args.test_name,
            "Device List" : device_list_str ,
            "No of Devices" : "Total" + "( " + str(len(phone_list)) + " ): Android(" +  str(len(phone_list)) +")" ,
            "Incremental Values" : "",
            "Required URL Count" : args.count,
            "URL" : args.url 
        }
        # if obj.incremental:
        #     test_setup_info['Duration per Iteration (min)']= str(test_setup_info_duration_per_iteration)+ " (min)"
        test_setup_info['Incremental Values'] = test_setup_info_incremental_values
        test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration) + " (min)"

        # Retrieve additional monitoring data
        # total_urls = obj.my_monitor('total-urls')
        uc_min_val = obj.my_monitor('uc-min')
        timeout = obj.my_monitor('timeout')
        uc_min_value = uc_min_val
        dataset2 = total_urls
        dataset = timeout
        lis = username
        bands = ['URLs']
        obj.data['total_urls'] = total_urls
        obj.data['uc_min_val'] = uc_min_val 
        obj.data['timeout'] = timeout
    logging.info("Test Completed")

    # Handle incremental values and generate reports accordingly
    prev_inc_value = 0
    if obj.resource_ids and obj.incremental :
        for i in range(len(cx_order_list)):
            df = pd.DataFrame(obj.data)
            names_to_increment = cx_order_list[i] 

            if 'inc_value' not in df.columns:
                df['inc_value'] = 0
            if i == 0:
                prev_inc_value = len(cx_order_list[i])
            else:
                prev_inc_value = prev_inc_value + len(cx_order_list[i])
                
            obj.data['inc_value'] = df.apply(
                lambda row: (
                    prev_inc_value  # Accumulate inc_value
                    if row['inc_value'] == 0 and row['name'] in names_to_increment 
                    else row['inc_value']  # Keep existing inc_value
                ), 
                axis=1
            )

            df1 = pd.DataFrame(obj.data)
            if args.dowebgui == True:
                df1.to_csv('{}/rb_datavalues.csv'.format(obj.result_dir), index=False)
                df1.to_csv(file_path, mode='w', index=False) 
            else:
                df1.to_csv(file_path, mode='w', index=False)     
        # Generate report for the test
        obj.generate_report(date,"webBrowser.csv",test_setup_info = test_setup_info, dataset2 = dataset2, dataset = dataset, lis = lis, bands = bands, total_urls = total_urls, uc_min_value = uc_min_value , cx_order_list = cx_order_list,gave_incremental=gave_incremental) 
    # elif obj.resource_ids:
    #     obj.generate_report(date,"webBrowser.csv", test_setup_info = test_setup_info, dataset2 = dataset2, dataset = dataset, lis = lis, bands = bands, total_urls = total_urls, uc_min_value = uc_min_value) 

    # Perform post-cleanup operations
    if args.postcleanup:
        obj.postcleanup()

    # Clean up resources based on operating system types
    # if args.postcleanup==True:
    #     obj.cleanup(os_types_dict)

    # Save webGUI data if dowebgui is True
    if args.dowebgui == True and obj.resource_ids: 
        resource_ids = list(map(int, obj.resource_ids.split(',')))
        obj.data_for_webui["status"] = ["Completed"] * len(resource_ids)
        obj.data_for_webui["start_time_webGUI"] = obj.data["start_time_webGUI"]
        obj.data_for_webui["end_time_webGUI"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obj.data_for_webui["remaining_time_webGUI"] = "0"
        df1 = pd.DataFrame(obj.data_for_webui)
        df1.to_csv('{}/rb_datavalues.csv'.format(obj.result_dir), index=False)
if __name__ == '__main__':
    main() 