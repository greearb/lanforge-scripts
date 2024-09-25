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
        python3 lf_interop_throughput.py --mgr 192.168.214.219 --mgr_port 8080 --security wpa2 --upstream_port eth1 --test_duration 1m --download 0 --upload 1000000 --traffic_type lf_udp --packet_size 17

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
from lf_graph import lf_bar_graph_horizontal
from lf_graph import lf_line_graph

from datetime import datetime, timedelta

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
                device_list=[],
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
                side_a_min_pdu=-1,side_b_min_pdu=-1,
                number_template="00000",
                test_duration="2m",
                use_ht160=False,
                load_type=None,
                _debug_on=False,
                dowebgui=False,
                precleanup=False,
                do_interopability=False,
                ip="localhost",
                user_list=[], real_client_list=[], real_client_list1=[], hw_list=[], laptop_list=[], android_list=[], mac_list=[], windows_list=[], linux_list=[],
                total_resources_list=[], working_resources_list=[], hostname_list=[], username_list=[], eid_list=[],
                devices_available=[], input_devices_list=[], mac_id1_list=[], mac_id_list=[],overall_avg_rssi=[]):
        super().__init__(lfclient_host=host,
                        lfclient_port=port),
        self.ssid_list = []
        self.signal_list=[]
        self.channel_list=[]
        self.mode_list=[]
        self.link_speed_list=[]
        self.background_run = None
        self.stop_test=False
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
        self.incremental_capacity=incremental_capacity
        self.load_type=load_type
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.report_timer=report_timer
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
        self.cx_profile.side_a_min_pdu= side_a_min_pdu
        self.cx_profile.side_b_min_pdu= side_b_min_pdu
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
        self.overall_avg_rssi=overall_avg_rssi
        self.dowebgui = dowebgui
        self.do_interopability=do_interopability
        self.ip = ip
        self.device_found = False
        self.incremental=incremental
        self.precleanup=precleanup

    def os_type(self):
        """
        Determines OS type of selected devices.

        """
        response = self.json_get("/resource/all")
        if "resources" not in response.keys():
            logger.error("There are no real devices.")
            exit(1)

        for key,value in response.items():
            if key == "resources":
                for element in value:
                    for a,b in element.items():
                        if "Apple" in b['hw version']:
                            if b['kernel']=='':
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

                        
    def phantom_check(self):
        """
        Checks for non-phantom resources and ports, categorizes them, and prepares a list of available devices for testing.

        """
        port_eid_list,same_eid_list,original_port_list=[],[],[]

        # Retrieve all resources from the LANforge
        response=self.json_get("/resource/all")

        if "resources" not in response.keys():
            logger.error("There are no real devices.")
            exit(1)

        # Iterate over the response to categorize resources
        for key,value in response.items():
            if key == "resources":
                for element in value:
                    for(a,b) in element.items():

                        # Check if the resource is not phantom
                        if b['phantom'] == False:
                            self.working_resources_list.append(b["hw version"])

                            # Categorize based on hw version (type of device)
                            if "Win" in b['hw version']:
                                self.eid_list.append(b['eid'])
                                self.windows_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] +" " +'Win'+" "+ b['hostname'])
                            elif "Linux" in b['hw version']:
                                if 'ct' not in b['hostname']:
                                    if 'lf' not in b['hostname']:
                                        self.eid_list.append(b['eid'])
                                        self.linux_list.append(b['hw version'])
                                        self.devices_available.append(b['eid'] +" " +'Lin'+" "+ b['hostname'])
                            elif "Apple" in b['hw version']:
                                if b['kernel']=='':
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    self.devices_available.append(b['eid'] +" " +'iOS'+" "+ b['hostname'])
                                else:
                                    self.eid_list.append(b['eid'])
                                    self.mac_list.append(b['hw version'])
                                    #self.hostname_list.append(b['eid']+ " " +b['hostname'])
                                    self.devices_available.append(b['eid'] +" " +'Mac'+" "+ b['hostname'])
                            else:
                                self.eid_list.append(b['eid'])
                                self.android_list.append(b['hw version'])
                                self.devices_available.append(b['eid'] +" " +'android'+" "+ b['user'])
        
        # Retrieve all ports from the endpoint
        response_port=self.json_get("/port/all")
        if "interfaces" not in response_port.keys():
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)
        

        # mac_id1_list=[]  

        # Iterate over port information to filter and categorize ports     
        for interface in response_port['interfaces']:
            for port,port_data in interface.items():

                # Check conditions for non-phantom ports
                if(not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0" and port_data['alias'] != 'p2p0'):
                    # Check if the port's parent device matches with an eid in the eid_list
                    for id in self.eid_list:
                        if id+'.' in port:
                            original_port_list.append(port)
                            port_eid_list.append(str(self.name_to_eid(port)[0])+'.'+str(self.name_to_eid(port)[1]))
                            self.mac_id1_list.append(str(self.name_to_eid(port)[0])+'.'+str(self.name_to_eid(port)[1])+' '+port_data['mac'])

        # Check for matching eids between eid_list and port_eid_list
        for i in range(len(self.eid_list)):
            for j in range(len(port_eid_list)):
                if self.eid_list[i]==port_eid_list[j]:
                    same_eid_list.append(self.eid_list[i])
        same_eid_list=[_eid + ' ' for _eid in same_eid_list]

        for eid in same_eid_list:
            for device in self.devices_available:
                if eid in device:
                    self.user_list.append(device)



        # If self.device_list is provided, check availability against devices_available
        if len(self.device_list) != 0:
            devices_list=self.device_list
            available_list=[]
            not_available=[]

            # Iterate over each input device in devices_list
            for input_device in devices_list.split(','):
                found=False

                # Check if input_device exists in devices_available
                for device in self.devices_available:
                    if input_device + " " in device:
                        available_list.append(input_device)
                        found =True
                        break
                if found == False:
                    not_available.append(input_device)
                    logger.warning(input_device + " is not available to run the test")
            
            # If available_list is not empty, log info and set self.device_found to True
            if len(available_list)>0:
                logger.info("Test is intiated on these devices {}".format(available_list))
                devices_list=','.join(available_list)
                self.device_found=True
            else:
                devices_list=""
                self.device_found=False
                logger.warning("Test can not be initiated on any selected devices")
        else:

            # If self.device_list is not provided, prompt user to select devices from user_list
            logger.info("AVAILABLE DEVICES TO RUN TEST : {}".format(self.user_list))
            devices_list = input("Select the devices to run the test(e.g. 1.10,1.11 or all to run the test on all devices: ")

        # If no devices are selected or only comma is entered, log an error and return False
        if devices_list =="all":
            devices_list=""
        if(devices_list==","):
            logger.error("Selected Devices are not available in the lanforge")
            return False,self.real_client_list
        
        # Split devices_list into resource_eid_list
        resource_eid_list=devices_list.split(',')
        logger.info("devices list {}".format(devices_list, resource_eid_list))
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
                if i in  self.user_list[j]:
                    self.real_client_list.append(self.user_list[j])
                    self.real_client_list1.append(self.user_list[j][:25])
        # print("real_client_list",self.real_client_list)
        # print("real_client_list1",self.real_client_list1)

        self.num_stations=len(self.real_client_list)

        # Iterate over resource_eid_list2 and mac_id1_list to populate mac_id_list
        for eid in resource_eid_list2:
            for i in self.mac_id1_list:
                if eid in i:
                    self.mac_id_list.append(i.strip(eid+' '))

        # Check if incremental_capacity is provided and ensure selected devices are sufficient
        if (len(self.incremental_capacity)>0 and int(self.incremental_capacity.split(',')[-1])>len(self.mac_id_list)):
            logger.error("Devices available are less than given incremental capacity")
            return False,self.real_client_list

        else:
            return True,self.real_client_list

    def get_signal_and_channel_data(self,station_names):
        """
        Retrieves signal strength, channel, mode, and link speed data for the specified stations.

        """
   
        signal_list,channel_list,mode_list,link_speed_list=[],[],[],[]
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
        return signal_list,channel_list,mode_list,link_speed_list



    def get_ssid_list(self,station_names):
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
        direction=''

        # Determine direction based on side_a_min_bps and side_b_min_bps
        if int(self.cx_profile.side_b_min_bps)!=2560 and int(self.cx_profile.side_a_min_bps)!=2560:
            self.direction = "Bi-direction"
            direction = 'Bi-di'
        elif int(self.cx_profile.side_b_min_bps) != 2560:
            self.direction = "Download"
            direction = 'DL'
        else:
            if int(self.cx_profile.side_a_min_bps) != 2560:
                self.direction = "Upload"
                direction = 'UL'
        traffic_type=(self.traffic_type.strip("lf_")).upper()
        traffic_direction_list,cx_list,traffic_type_list=[],[],[]
        for client in range(len(self.real_client_list)):
            traffic_direction_list.append(direction)
            traffic_type_list.append(traffic_type)

        # Construct connection names
        for ip_tos in self.tos:
            for i in self.real_client_list1:
                for j in traffic_direction_list:
                    for k in traffic_type_list:
                        cxs="%s_%s_%s"% (i,k,j)
                        cx_names=cxs.replace(" ","")
                cx_list.append(cx_names)
        logger.info('cx_list{}'.format(cx_list))
        count=0

        # creating duplicate created_cx's for precleanup of CX's if there are already existed
        if self.precleanup==True:
            self.cx_profile.created_cx={k:[k+'-A',k+'-B'] for k in cx_list}
            self.pre_cleanup()

        # for ip_tos in range(len(self.tos)):
        for device in range(len(self.input_devices_list)):
            logger.info("Creating connections for endpoint type: %s cx-count: %s" % (
                self.traffic_type, self.cx_profile.get_cx_count()))
            self.cx_profile.create(endp_type=self.traffic_type, side_a=[self.input_devices_list[device]],
                                    side_b=self.upstream,sleep_time=0,cx_name="%s" % (cx_list[count]))
            count +=1
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

    def start_specific(self,cx_list):
        """
        Starts specific connections from the given list and sets a report timer for them.

        """
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if len(self.cx_profile.created_cx) >0:
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

    def stop_specific(self,cx_list):
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

    def monitor(self,iteration,individual_df,device_names,incremental_capacity_list,overall_start_time,overall_end_time):
        

        throughput, upload,download,upload_throughput,download_throughput,connections_upload, connections_download = {}, [], [],[],[],{},{}
        drop_a, drop_a_per, drop_b, drop_b_per,state,state_of_device= [], [], [], [], [], []
        test_stopped_by_user=False
        if (self.test_duration is None) or (int(self.test_duration) <= 1):
            raise ValueError("Monitor test duration should be > 1 second")
        if self.cx_profile.created_cx is None:
            raise ValueError("Monitor needs a list of Layer 3 connections")
        
        
        start_time = datetime.now()

        logger.info("Monitoring cx and endpoints")
        end_time = start_time + timedelta(seconds=int(self.test_duration))
        self.overall=[]
        
        # Initialize variables for real-time connections data
        index=-1
        connections_upload = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_upload_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        connections_download_realtime = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        
        # Initialize lists for throughput and drops for each connection
        [(upload.append([]), download.append([]), drop_a.append([]), drop_b.append([]),state.append([])) for i in range(len(self.cx_profile.created_cx))]
        
        # If using web GUI, set runtime directory
        if self.dowebgui:
            runtime_dir = self.result_dir
        
        # Continuously collect data until end time is reached
        while datetime.now() < end_time:
            index += 1
            
            signal_list,channel_list,mode_list,link_speed_list=self.get_signal_and_channel_data(self.input_devices_list)
            signal_list = [int(i) if i != "" else 0 for i in signal_list]

            # Fetch required throughput data from Lanforge
            response = list(
                self.json_get('/cx/%s?fields=%s' % (
                    ','.join(self.cx_profile.created_cx.keys()), ",".join(['bps rx a', 'bps rx b', 'rx drop %25 a', 'rx drop %25 b','state']))).values())[2:]
            # Extracting and storing throughput data
            throughput[index] = list(
                map(lambda i: [x for x in i.values()], response))
            if self.dowebgui:
                individual_df_data=[]
                temp_upload, temp_download, temp_drop_a, temp_drop_b= [], [], [], []
                
                # Initialize temporary lists for each connection
                [(temp_upload.append([]), temp_download.append([]), temp_drop_a.append([]), temp_drop_b.append([])) for
                    i in range(len(self.cx_profile.created_cx))]
                
                # Populate temporary lists with current throughput data
                for i in range(len(throughput[index])):
                    if throughput[index][i][4]!='Run':
                            temp_upload[i].append(0)
                            temp_download[i].append(0)
                            temp_drop_a[i].append(0)
                            temp_drop_b[i].append(0)
                    else:
                        temp_upload[i].append(throughput[index][i][1])
                        temp_download[i].append(throughput[index][i][0])
                        temp_drop_a[i].append(throughput[index][i][2])
                        temp_drop_b[i].append(throughput[index][i][3])
                    
                
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
                time_difference = abs(end_time - datetime.now())
                overall_time_difference=abs(overall_end_time-datetime.now())
                overall_total_hours=overall_time_difference.total_seconds() / 3600
                overall_remaining_minutes=(overall_total_hours % 1) * 60
                timestamp=datetime.now().strftime("%d/%m %I:%M:%S %p")
                remaining_minutes_instrf=[str(int(overall_total_hours)) + " hr and " + str(int(overall_remaining_minutes)) + " min" if int(overall_total_hours) != 0 or int(overall_remaining_minutes) != 0 else '<1 min'][0]
                
                # Storing individual device throughput data(download, upload, Rx % drop A, Rx % drop B) to dataframe
                for i in range(len(download_throughput)):
                    individual_df_data.extend([download_throughput[i],upload_throughput[i],drop_a_per[i],drop_b_per[i],int(signal_list[i]),link_speed_list[i]])                
               
                # Storing Overall throughput data for all devices and also start time, end time, remaining time and status of test running
                individual_df_data.extend([round(sum(download_throughput),2),round(sum(upload_throughput),2),sum(drop_a_per),sum(drop_a_per),iteration+1,timestamp,overall_start_time.strftime("%d/%m %I:%M:%S %p"),overall_end_time.strftime("%d/%m %I:%M:%S %p"),remaining_minutes_instrf,', '.join(str(n) for n in incremental_capacity_list),'Running'])
                
                # Append data to individual_df and save to CSV
                individual_df.loc[len(individual_df)]=individual_df_data
                individual_df.to_csv('{}/throughput_data.csv'.format(runtime_dir), index=False)

                # Check if test was stopped by the user
                with open(runtime_dir + "/../../Running_instances/{}_{}_running.json".format(self.ip, self.test_name),
                          'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logger.warning('Test is stopped by the user')
                        test_stopped_by_user=True
                        break
                
                # Adjust sleep time based on elapsed time since start
                d=datetime.now()
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

                # If not using web GUI, sleep based on report timer
                individual_df_data=[]
                time.sleep(self.report_timer)

                # Aggregate data from throughput
                
                for index, key in enumerate(throughput):
                    for i in range(len(throughput[key])):
                        upload[i],download[i],drop_a[i],drop_b[i]=[],[],[],[]
                        if throughput[key][i][4]!='Run':
                            upload[i].append(0)
                            download[i].append(0)
                            drop_a[i].append(0)
                            drop_b[i].append(0)
                           
                        else:
                            upload[i].append(throughput[key][i][1])
                            download[i].append(throughput[key][i][0])
                            drop_a[i].append(throughput[key][i][2])
                            drop_b[i].append(throughput[key][i][3])
                            

                # Calculate average throughput and drop percentages
                upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
                download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
                drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
                drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
               
              

                # Calculate overall time difference and timestamp
                timestamp=datetime.now().strftime("%d/%m %I:%M:%S %p")
                # # time_difference = abs(end_time - datetime.now())
                overall_time_difference=abs(overall_end_time-datetime.now())
                # # total_hours = time_difference.total_seconds() / 3600
                overall_total_hours=overall_time_difference.total_seconds() / 3600
                overall_remaining_minutes=(overall_total_hours % 1) * 60
                remaining_minutes_instrf=[str(int(overall_total_hours)) + " hr and " + str(int(overall_remaining_minutes)) + " min" if int(overall_total_hours) != 0 or int(overall_remaining_minutes) != 0 else '<1 min'][0]
                
                # Storing individual device throughput data(download, upload, Rx % drop A, Rx % drop B) to dataframe
                for i in range(len(download_throughput)):
                    individual_df_data.extend([download_throughput[i],upload_throughput[i],drop_a_per[i],drop_b_per[i],int(signal_list[i]),link_speed_list[i]])

                # Storing Overall throughput data for all devices and also start time, end time, remaining time and status of test running
                individual_df_data.extend([round(sum(download_throughput),2),round(sum(upload_throughput),2),sum(drop_a_per),sum(drop_a_per),iteration+1,timestamp,overall_start_time.strftime("%d/%m %I:%M:%S %p"),overall_end_time.strftime("%d/%m %I:%M:%S %p"),remaining_minutes_instrf,', '.join(str(n) for n in incremental_capacity_list),'Running'])
                individual_df.loc[len(individual_df)]=individual_df_data
                individual_df.to_csv('throughput_data.csv', index=False)

            if self.stop_test :
                test_stopped_by_user=True
                break
            if not self.background_run and self.background_run is not None:
                break
        
        for index, key in enumerate(throughput):
            for i in range(len(throughput[key])):
                upload[i],download[i],drop_a[i],drop_b[i]=[],[],[],[]
                if throughput[key][i][4]!='Run':
                    upload[i].append(0)
                    download[i].append(0)
                    drop_a[i].append(0)
                    drop_b[i].append(0)
                else:
                    upload[i].append(throughput[key][i][1])
                    download[i].append(throughput[key][i][0])
                    drop_a[i].append(throughput[key][i][2])
                    drop_b[i].append(throughput[key][i][3])
              
             
        individual_df_data=[]
        upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
        download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
        drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
        drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
        signal_list,channel_list,mode_list,link_speed_list=self.get_signal_and_channel_data(self.input_devices_list)
        signal_list = [int(i) if i != "" else 0 for i in signal_list]

        # Storing individual device throughput data(download, upload, Rx % drop A, Rx % drop B) to dataframe after test stopped
        for i in range(len(download_throughput)):
            individual_df_data.extend([download_throughput[i],upload_throughput[i],drop_a_per[i],drop_b_per[i],int(signal_list[i]),link_speed_list[i]])
        timestamp=datetime.now().strftime("%d/%m %I:%M:%S %p") 


        # If it's the last iteration, append final metrics and 'Stopped' status 
        if iteration+1 == len(incremental_capacity_list):     

            individual_df_data.extend([round(sum(download_throughput),2),round(sum(upload_throughput),2),sum(drop_a_per),sum(drop_a_per),iteration+1,timestamp,overall_start_time.strftime("%d/%m %I:%M:%S %p"),timestamp,0,', '.join(str(n) for n in incremental_capacity_list),'Stopped'])
        
        # If the test was stopped by the user, append metrics and 'Stopped' status
        elif test_stopped_by_user:

            individual_df_data.extend([round(sum(download_throughput),2),round(sum(upload_throughput),2),sum(drop_a_per),sum(drop_a_per),iteration+1,timestamp,overall_start_time.strftime("%d/%m %I:%M:%S %p"),timestamp,0,', '.join(str(n) for n in incremental_capacity_list),'Stopped'])
        
        # Otherwise, append metrics and 'Stopped' status with overall end time
        else:
            individual_df_data.extend([round(sum(download_throughput),2),round(sum(upload_throughput),2),sum(drop_a_per),sum(drop_a_per),iteration+1,timestamp,overall_start_time.strftime("%d/%m %I:%M:%S %p"),overall_end_time.strftime("%d/%m %I:%M:%S %p"),remaining_minutes_instrf,', '.join(str(n) for n in incremental_capacity_list),'Stopped'])          
        individual_df.loc[len(individual_df)]=individual_df_data

        # Save individual_df to CSV based on web GUI status
        if self.dowebgui :
            individual_df.to_csv('{}/throughput_data.csv'.format(runtime_dir), index=False)
            individual_df.to_csv('throughput_data.csv', index=False)
        else:
            individual_df.to_csv('throughput_data.csv', index=False)

        keys = list(connections_upload.keys())
        keys = list(connections_download.keys())

        for i in range(len(download_throughput)):
            connections_download.update({keys[i]: float(f"{(download_throughput[i] ):.2f}")})
        for i in range(len(upload_throughput)):
            connections_upload.update({keys[i]: float(f"{(upload_throughput[i] ):.2f}")})

        logger.info("connections download {}".format(connections_download))
        logger.info("connections upload {}".format(connections_upload))

        return individual_df,test_stopped_by_user

    def perform_intended_load(self,iteration,incremental_capacity_list):
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
                    "min_rate": int(int(self.cx_profile.side_a_min_bps)/int(incremental_capacity_list[iteration])),
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
                    "min_rate": int(int(self.cx_profile.side_b_min_bps)/int(incremental_capacity_list[iteration])),
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
        if (len(self.incremental_capacity)==0 and self.do_interopability!=True and  self.incremental):
            self.incremental_capacity=input("Enter the incremental load to run the test:")

        cx_incremental_capacity_lists=[]
        incremental_capacity_list_values=[]
        device_list_length=len(self.mac_id_list)

        # Check if 'incremental_capacity' is not specified

        if len(self.incremental_capacity)==0:
            incremental_capacity_1=[device_list_length]
        
        elif(device_list_length!=0 and len(self.incremental_capacity.split(","))>0):
            device_list_length=len(self.mac_id_list)
            incremental_capacity_length=len(self.incremental_capacity.split(","))

            # Handle single incremental capacity specification

            if incremental_capacity_length==1:
                temp_incremental_capacity_list=[]
                incremental_capacity=int(self.incremental_capacity.split(",")[0])

                # Generate incremental capacity list

                for i in range(incremental_capacity,device_list_length):
                    if i % incremental_capacity == 0:
                        temp_incremental_capacity_list.append(i)
                
                # Ensure the last capacity covers all devices

                if device_list_length not in temp_incremental_capacity_list:
                    temp_incremental_capacity_list.append(device_list_length)
                incremental_capacity_1=temp_incremental_capacity_list

            # Handle multiple incremental capacities specification

            else:
                incremental_capacity_1=self.incremental_capacity.split(",")
        # Generate lists of incremental capacities

        for i in range(len(incremental_capacity_1)):
            new_cx_list=[]
            if i==0:
                x=1
            else:
                x=cx_incremental_capacity_lists[-1][-1]+1
            for j in range(x,int(incremental_capacity_1[i])+1):
                new_cx_list.append(j)
            incremental_capacity_list_values.append(new_cx_list[-1])
            cx_incremental_capacity_lists.append(new_cx_list)

        # Check completeness: last capacity list should cover all devices
        if incremental_capacity_list_values[-1]==device_list_length:
            return True
        else:
            return False
        



    def get_incremental_capacity_list(self):
        """
        
        Generates lists of incremental capacities and connection names for the created connections.

        """
        
        cx_incremental_capacity_lists,cx_incremental_capacity_names_lists,incremental_capacity_list_values=[],[],[]

        created_cx_lists_keys = list(self.cx_profile.created_cx.keys())
        device_list_length=len(created_cx_lists_keys)

        # Check if incremental capacity is not provided
        if len(self.incremental_capacity)==0:
            incremental_capacity_1=[device_list_length]
        
        # Check if device list is not empty and incremental capacity is provided
        elif(device_list_length!=0 and len(self.incremental_capacity.split(","))>0):
            device_list_length=len(created_cx_lists_keys)
            incremental_capacity_length=len(self.incremental_capacity.split(","))

            # Handle case with a single incremental capacity value
            if incremental_capacity_length==1:
                temp_incremental_capacity_list=[]
                incremental_capacity=int(self.incremental_capacity.split(",")[0])

                # Calculate increments based on the provided capacity
                for i in range(incremental_capacity,device_list_length):
                    if i % incremental_capacity == 0:
                        temp_incremental_capacity_list.append(i)

                # Ensure the device list length itself is included in the increments
                if device_list_length not in temp_incremental_capacity_list:
                    temp_incremental_capacity_list.append(device_list_length)
                incremental_capacity_1=temp_incremental_capacity_list

            # Handle case with multiple incremental capacity values
            else:
                incremental_capacity_1=self.incremental_capacity.split(",")

        # Generate lists of incremental capacities and connection names

        for i in range(len(incremental_capacity_1)):
            new_cx_list=[]
            new_cx_names_list=[]
            if i==0:
                x=1
            else:
                x=cx_incremental_capacity_lists[-1][-1]+1

            # Generate capacity list and corresponding names

            for j in range(x,int(incremental_capacity_1[i])+1):
                new_cx_list.append(j)
                new_cx_names_list.append(created_cx_lists_keys[j-1])

            # Track the last capacity value for each list
            incremental_capacity_list_values.append(new_cx_list[-1])
            cx_incremental_capacity_lists.append(new_cx_list)
            cx_incremental_capacity_names_lists.append(new_cx_names_list)
        return cx_incremental_capacity_names_lists,cx_incremental_capacity_lists,created_cx_lists_keys,incremental_capacity_list_values

    def generate_report(self,iterations_before_test_stopped_by_user,incremental_capacity_list,data=None,data1=None,report_path='',result_dir_name='Throughput_Test_report',
                        selected_real_clients_names=None):

        if self.do_interopability:
            result_dir_name="Interopability_Test_report"

        self.ssid_list = self.get_ssid_list(self.input_devices_list)
        self.signal_list,self.channel_list,self.mode_list,self.link_speed_list=self.get_signal_and_channel_data(self.input_devices_list)

        if selected_real_clients_names is not None:
            self.num_stations = selected_real_clients_names

        # Initialize the report object    
        if self.do_interopability==False:
            report = lf_report(_output_pdf="throughput.pdf", _output_html="throughput.html", _path=report_path,
                            _results_dir_name=result_dir_name)
            report_path = report.get_path()
            report_path_date_time = report.get_path_date_time()
            # df.to_csv(os.path.join(report_path_date_time, 'throughput_data.csv'))
            shutil.move('throughput_data.csv',report_path_date_time)
            logger.info("path: {}".format(report_path))
            logger.info("path_date_time: {}".format(report_path_date_time))
            report.set_title("Throughput Test")
            report.build_banner()
            
            # objective title and description
            report.set_obj_html(_obj_title="Objective",
                                _obj="The Candela Client Capacity test is designed to measure an Access Point’s client capacity and performance when handling different amounts of Real clients like android, Linux,"
                                    " windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and measure the per client and the overall throughput for"
                                    " this test, we aim to assess the capacity of network to handle high volumes of traffic while"
                                    " each trial. Along with throughput other measurements made are client connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the"
                                    " AP to be able to handle several stations (within the limitations of the AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that"
                                    "scales well will not show a significant overall throughput decrease as more Real clients are added.")
            report.build_objective()
            report.set_obj_html(_obj_title="Input Parameters",
                                _obj="The below tables provides the input parameters for the test")
            report.build_objective()

            # Initialize counts and lists for device types
            android_devices,windows_devices,linux_devices,mac_devices,ios_devices=0,0,0,0,0
            all_devices_names=[]
            device_type=[]
            packet_size_text=''
            total_devices=""
            if self.cx_profile.side_a_min_pdu==-1:
               packet_size_text='AUTO'
            else:
                packet_size_text=str(self.cx_profile.side_a_min_pdu)+' Bytes'
            # Determine load type name based on self.load_type
            if self.load_type=="wc_intended_load":
                load_type_name="Intended Load"
            else:
                load_type_name="Per Client Load"
            for i in self.real_client_list:
                split_device_name=i.split(" ")
                if 'android' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Android)") )
                    device_type.append("Android")
                    android_devices+=1
                elif 'Win' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                    device_type.append("Windows")
                    windows_devices+=1
                elif 'Lin' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                    device_type.append("Linux")
                    linux_devices+=1
                elif 'Mac' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                    device_type.append("Mac")
                    mac_devices+=1
                elif 'iOS' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                    device_type.append("iOS")
                    ios_devices+=1

            # Build total_devices string based on counts
            if android_devices>0:
                total_devices+= f" Android({android_devices})" 
            if windows_devices>0:
                total_devices+= f" Windows({windows_devices})" 
            if linux_devices>0:
                total_devices+= f" Linux({linux_devices})" 
            if mac_devices>0:
                total_devices+= f" Mac({mac_devices})"
            if ios_devices>0:
                total_devices+= f" iOS({ios_devices})"

            # Determine incremental_capacity_data based on self.incremental_capacity
            if len(self.incremental_capacity)==1:
                if len(incremental_capacity_list)==1:
                    incremental_capacity_data=str(self.incremental_capacity[0])
                else:
                    incremental_capacity_data=','.join(map(str, incremental_capacity_list))
            elif(len(self.incremental_capacity)>1):
                self.incremental_capacity=self.incremental_capacity.split(',')
                incremental_capacity_data=', '.join(self.incremental_capacity)
            else:
                incremental_capacity_data="None"
            
            # Construct test_setup_info dictionary for test setup table
            test_setup_info = {
            "Test name" : self.test_name,
            "Device List": ", ".join(all_devices_names),
            "No of Devices": "Total"+ f"({str(self.num_stations)})" + total_devices,
            "Increment":incremental_capacity_data,
            "Traffic Duration in minutes" : round(int(self.test_duration)*len(incremental_capacity_list)/60,2),
            "Traffic Type" : (self.traffic_type.strip("lf_")).upper(),
            "Traffic Direction" : self.direction,
            "Upload Rate(Mbps)" : str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps",
            "Download Rate(Mbps)" : str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps",
            "Load Type" : load_type_name,
            "Packet Size" : packet_size_text
            }
            report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
            
            # Loop through iterations and build graphs, tables for each iteration
            for i in range(len(iterations_before_test_stopped_by_user)):
                # rssi_signal_data=[]
                devices_on_running=[]
                download_data=[]
                upload_data=[]
                devices_data_to_create_bar_graph=[]
                # signal_data=[]
                direction_in_table=[]
                packet_size_in_table=[]
                upload_list,download_list=[],[]
                rssi_data=[]
                data_iter=data[data['Iteration']==i+1]
                
                # for sig in self.signal_list[0:int(incremental_capacity_list[i])]:
                #     signal_data.append(int(sig)*(-1))
                # rssi_signal_data.append(signal_data)

                # Fetch devices_on_running from real_client_list  
                for j in range(data1[i][-1]):
                    devices_on_running.append(self.real_client_list[j].split(" ")[-1])

                # Fetch download_data and upload_data based on load_type and direction
                for k in  devices_on_running:
                    # individual_device_data=[]

                    # Checking individual device download and upload rate by searching device name in dataframe
                    columns_with_substring = [col for col in data_iter.columns if k in col]
                    filtered_df = data_iter[columns_with_substring]
                    if self.load_type=="wc_intended_load":
                        if self.direction=="Bi-direction": 

                            # Append download and upload data from filtered dataframe
                            download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])
                            upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])

                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)
                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                        elif self.direction=='Download':

                            # Append download data from filtered dataframe
                            download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])

                            # Append 0 for upload data
                            upload_data.append(0)

                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                        elif self.direction=='Upload':

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round((int(self.cx_profile.side_a_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            download_list.append(str(round((int(self.cx_profile.side_b_min_bps)/1000000)/int(incremental_capacity_list[i]),2)) + "Mbps")
                            
                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                            # Append upload data from filtered dataframe
                            upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])

                            # Append 0 for download data
                            download_data.append(0)

                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)
                            
                    else:
                        
                        if self.direction=="Bi-direction": 

                            # Append download and upload data from filtered dataframe
                            download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])
                            upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])
                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")

                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)
                        elif self.direction=='Download':

                            # Append download data from filtered dataframe
                            download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])

                            # Append 0 for upload data
                            upload_data.append(0)
                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")

                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)
                        elif self.direction=='Upload':

                            # Calculate and append upload and download throughput to lists
                            upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                            download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")
                            rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                            # Append upload data from filtered dataframe
                            upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])

                            # Append 0 for download data
                            download_data.append(0)

                            if self.cx_profile.side_a_min_pdu==-1:
                                packet_size_in_table.append('AUTO')
                            else:
                                packet_size_in_table.append(self.cx_profile.side_a_min_pdu)
                            direction_in_table.append(self.direction)

                data_set_in_graph,trimmed_data_set_in_graph=[],[]

                # Depending on the test direction, retrieve corresponding throughput data,
                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                if self.direction=="Bi-direction": 
                    download_values_list=data['Overall Download'][data['Iteration']==i+1].values.tolist()
                    upload_values_list=data['Overall Upload'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data=['Download','Upload']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))),2)} Mbps, Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])),2)} Mbps"
                
                elif self.direction=='Download':
                    download_values_list=data['Overall Download'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    label_data=['Download']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))),2)} Mbps"
                
                elif self.direction=='Upload':
                    upload_values_list=data['Overall Upload'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data=['Upload']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])),2)} Mbps"
                
                if len(incremental_capacity_list)>1:
                    report.set_custom_html(f"<h2><u>Iteration-{i+1}: Number of Devices Running : {len(devices_on_running)}</u></h2>")
                    report.build_custom()
                logger
                for _ in range(len(data_set_in_graph)):
                    trimmed_data_set_in_graph.append(self.trim_data(len(data_set_in_graph[_]),data_set_in_graph[_]))
                
                
                report.set_obj_html(
                            _obj_title=f"{real_time_data}",
                            _obj=" ")
                report.build_objective()
                graph=lf_line_graph(_data_set=trimmed_data_set_in_graph,
                                    _xaxis_name="Time",
                                    _yaxis_name="Throughput (Mbps)",
                                    _xaxis_categories=self.trim_data(len(data['TIMESTAMP'][data['Iteration']==i+1].values.tolist()),data['TIMESTAMP'][data['Iteration']==i+1].values.tolist()),
                                    _label=label_data,
                                    _graph_image_name=f"line_graph{i}"
                                    
                                    )
                graph_png = graph.build_line_graph()
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
                graph=lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                            _xaxis_name="Avg Throughput(Mbps)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"image_name{i}",
                                            _label=label_data,
                                            _yaxis_categories= devices_on_running_trimmed,
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
                graph=lf_bar_graph_horizontal(_data_set=[rssi_data],
                                            _xaxis_name="Signal(-dBm)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"signal_image_name{i}",
                                            _label=['RSSI'],
                                            _yaxis_categories= devices_on_running_trimmed,
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
                bk_dataframe = {
                            " Device Type " : device_type[0:int(incremental_capacity_list[i])],
                            " Username": devices_on_running[0:int(incremental_capacity_list[i])],
                            " SSID " : self.ssid_list[0:int(incremental_capacity_list[i])],
                            " MAC ": [mac.split(' ')[1] for mac in self.mac_id_list[0:int(incremental_capacity_list[i])]],
                            " Channel ":self.channel_list[0:int(incremental_capacity_list[i])],
                            " Mode" : self.mode_list[0:int(incremental_capacity_list[i])],
                            " Direction":direction_in_table[0:int(incremental_capacity_list[i])],
                            " Offered download rate(Mbps) " : download_list[0:int(incremental_capacity_list[i])],
                            " Observed download rate(Mbps)" : [str(n)+" Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                            " Offered upload rate(Mbps) " : upload_list[0:int(incremental_capacity_list[i])],
                            " Observed upload rate(Mbps) " : [str(n)+" Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                            " RSSI ": ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                            " Link Speed ":self.link_speed_list[0:int(incremental_capacity_list[i])],
                            " Packet Size(Bytes) ":[str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]]
                        }
    
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
            shutil.move('throughput_data.csv',report_path_date_time)
            
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
            android_devices,windows_devices,linux_devices,mac_devices,ios_devices=0,0,0,0,0
            all_devices_names=[]
            device_type=[]
            total_devices=""

            for i in self.real_client_list:
                split_device_name=i.split(" ")
                if 'android' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Android)") )
                    device_type.append("Android")
                    android_devices+=1
                elif 'Win' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                    device_type.append("Windows")
                    windows_devices+=1
                elif 'Lin' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                    device_type.append("Linux")
                    linux_devices+=1
                elif 'Mac' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                    device_type.append("Mac")
                    mac_devices+=1
                elif 'iOS' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                    device_type.append("iOS")
                    ios_devices+=1

            # Build total_devices string based on counts
            if android_devices>0:
                total_devices+= f" Android({android_devices})" 
            if windows_devices>0:
                total_devices+= f" Windows({windows_devices})" 
            if linux_devices>0:
                total_devices+= f" Linux({linux_devices})" 
            if mac_devices>0:
                total_devices+= f" Mac({mac_devices})"
            if ios_devices>0:
                total_devices+= f" iOS({ios_devices})"
            
            # Construct test_setup_info dictionary for test setup table
            test_setup_info = {
            "Test name" : self.test_name,
            "Device List": ", ".join(all_devices_names),
            "No of Devices": "Total"+ f"({str(self.num_stations)})" + total_devices,
            "Traffic Duration in minutes" : round(int(self.test_duration)*len(incremental_capacity_list)/60,2),
            "Traffic Type" : (self.traffic_type.strip("lf_")).upper(),
            "Traffic Direction" : self.direction,
            "Upload Rate(Mbps)" : str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps",
            "Download Rate(Mbps)" : str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps",
            # "Packet Size" : str(self.cx_profile.side_a_min_pdu) + " Bytes"
            }
            report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
            
            # Loop through iterations and build graphs, tables for each device
            for i in range(len(iterations_before_test_stopped_by_user)):
                rssi_signal_data=[]
                devices_on_running=[]
                download_data=[]
                upload_data=[]
                devices_data_to_create_bar_graph=[]
                signal_data=[]
                direction_in_table=[]
                # packet_size_in_table=[]
                upload_list,download_list=[],[]
                rssi_data=[]
                data_iter=data[data['Iteration']==i+1]

                # Fetch devices_on_running from real_client_list  
                devices_on_running.append(self.real_client_list[data1[i][-1]-1].split(" ")[-1])

                for k in  devices_on_running:
                    # individual_device_data=[]

                    # Checking individual device download and upload rate by searching device name in dataframe
                    columns_with_substring = [col for col in data_iter.columns if k in col]
                    filtered_df = data_iter[columns_with_substring]
   
                    if self.direction=="Bi-direction": 

                        # Append download and upload data from filtered dataframe
                        download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])
                        upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])
                        rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")

                        direction_in_table.append(self.direction)
                    elif self.direction=='Download':

                        # Append download data from filtered dataframe
                        download_data.append(filtered_df[[col for col in  filtered_df.columns if "Download" in col][0]].values.tolist()[-1])

                        # Append 0 for upload data
                        upload_data.append(0)
                        rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")

                        direction_in_table.append(self.direction)
                    elif self.direction=='Upload':

                        # Calculate and append upload and download throughput to lists
                        upload_list.append(str(round(int(self.cx_profile.side_a_min_bps)/1000000,2)) + "Mbps")
                        download_list.append(str(round(int(self.cx_profile.side_b_min_bps)/1000000,2)) + "Mbps")
                        rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                        # Append upload data from filtered dataframe
                        upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])

                        # Append 0 for download data
                        download_data.append(0)

                        direction_in_table.append(self.direction)

                data_set_in_graph,trimmed_data_set_in_graph=[],[]

                # Depending on the test direction, retrieve corresponding throughput data,
                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                if self.direction=="Bi-direction": 
                    download_values_list=data['Overall Download'][data['Iteration']==i+1].values.tolist()
                    upload_values_list=data['Overall Upload'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data=['Download','Upload']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))/len(download_data[0:int(incremental_capacity_list[i])])),2)} Mbps, Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])/len(upload_data[0:int(incremental_capacity_list[i])])),2)} Mbps"
                
                elif self.direction=='Download':
                    download_values_list=data['Overall Download'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(download_values_list)
                    devices_data_to_create_bar_graph.append(download_data)
                    label_data=['Download']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))/len(download_data[0:int(incremental_capacity_list[i])])),2)} Mbps"
                
                elif self.direction=='Upload':
                    upload_values_list=data['Overall Upload'][data['Iteration']==i+1].values.tolist()
                    data_set_in_graph.append(upload_values_list)
                    devices_data_to_create_bar_graph.append(upload_data)
                    label_data=['Upload']
                    real_time_data=f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])/len(upload_data[0:int(incremental_capacity_list[i])])),2)} Mbps"
                
                report.set_custom_html(f"<h2><u>{i+1}. Test On Device {', '.join(devices_on_running)}:</u></h2>")
                report.build_custom()
                
                for _ in range(len(data_set_in_graph)):
                    trimmed_data_set_in_graph.append(self.trim_data(len(data_set_in_graph[_]),data_set_in_graph[_]))
                
                
                report.set_obj_html(
                            _obj_title=f"{real_time_data}",
                            _obj=" ")
                report.build_objective()
                graph=lf_line_graph(_data_set=trimmed_data_set_in_graph,
                                    _xaxis_name="Time",
                                    _yaxis_name="Throughput (Mbps)",
                                    _xaxis_categories=self.trim_data(len(data['TIMESTAMP'][data['Iteration']==i+1].values.tolist()),data['TIMESTAMP'][data['Iteration']==i+1].values.tolist()),
                                    _label=label_data,
                                    _graph_image_name=f"line_graph{i}"
                                    
                                    )
                graph_png = graph.build_line_graph()
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
                graph=lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
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
                graph=lf_bar_graph_horizontal(_data_set=[rssi_data],
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
                bk_dataframe = {
                            " Device Type " : device_type[int(incremental_capacity_list[i])-1],
                            " Username": devices_on_running[-1],
                            " SSID " : self.ssid_list[int(incremental_capacity_list[i])-1],
                            " MAC " : str(self.mac_id_list[int(incremental_capacity_list[i])-1]).split(' ')[-1],
                            " Channel ":self.channel_list[int(incremental_capacity_list[i])-1],
                            " Mode" : self.mode_list[int(incremental_capacity_list[i])-1],
                            " Direction":direction_in_table[-1],
                            " Offered download rate(Mbps) " : download_list[-1],
                            " Observed download rate(Mbps)" : [str(download_data[-1])+" Mbps"],
                            " Offered upload rate(Mbps) " : upload_list[-1],
                            " Observed upload rate(Mbps) " : [str(upload_data[-1])+" Mbps" ],
                            " RSSI ":  ['' if rssi_data[-1] == 0 else '-'+str(rssi_data[-1])+ " dbm"],
                            " Link Speed ":self.link_speed_list[int(incremental_capacity_list[i])-1],
                            # " Packet Size(Bytes) ":[str(n)+" Bytes" for n in packet_size_in_table[0:int(incremental_capacity_list[i])]]
                        }
    
                dataframe1 = pd.DataFrame(bk_dataframe)
                report.set_table_dataframe(dataframe1)
                report.build_table()

                report.set_custom_html('<hr>')
                report.build_custom()
            
        # report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf(_orientation="Landscape")

    def trim_data(self,array_size,to_updated_array):
        if array_size < 6:
            updated_array=to_updated_array
        else:
            middle_elements_count = 4
            step = (array_size - 1) / (middle_elements_count + 1)  
            middle_elements = [int(i * step) for i in range(1, middle_elements_count + 1)]
            new_array = [0] + middle_elements + [array_size - 1]
            updated_array=[to_updated_array[index] for index in new_array]
        return updated_array

def main():
    help_summary = '''\
    The Client Capacity test and Interopability test is designed to measure an Access Point’s client capacity and performance when handling different amounts of Real clients like android, Linux,
    windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and measure the per client and the overall throughput for
    this test, we aim to assess the capacity of network to handle high volumes of traffic while
    each trial. Along with throughput other measurements made are client connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the
    AP to be able to handle several stations (within the limitations of the AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that
    scales well will not show a significant overall throughput decrease as more Real clients are added.
    '''
    parser=argparse.ArgumentParser(
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
    

    required=parser.add_argument_group('Required arguments to run throughput.py')
    optional=parser.add_argument_group('Optional arguments to run throughput.py')

    required.add_argument('--device_list',help="Enter the devices on which the test should be run",default=[])
    required.add_argument('--mgr','--lfmgr',default='localhost',help='hostname for where LANforge GUI is running')
    required.add_argument('--mgr_port','--port',default=8080,help='port LANforge GUI HTTP service is running on')
    required.add_argument('--upstream_port','-u',default='eth1',help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    required.add_argument('--ssid', help='WiFi SSID for script objects to associate to')
    required.add_argument('--passwd','--password','--key',default="[BLANK]", help='WiFi passphrase/password/key')
    required.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    required.add_argument('--upload', help='--upload traffic load per connection (upload rate)',default='2560')
    required.add_argument('--download', help='--download traffic load per connection (download rate)',default='2560')
    required.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="")
    required.add_argument('--report_timer', help='--duration to collect data', default="5s")
    required.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    required.add_argument('--dowebgui', help="If true will execute script for webgui", action='store_true')
    required.add_argument('--tos', default="Best_Efforts")
    required.add_argument('--packet_size',help='Determine the size of the packet in which Packet Size Should be Greater than 16B or less than 64KB(65507)',default="-1")
    required.add_argument('--incremental_capacity',
    help='Specify the incremental values for network load testing as a comma-separated list (e.g., 10,20,30). This defines the increments in bandwidth to evaluate performance under varying load conditions.',
    default=[])
    required.add_argument('--load_type',help="Determine the type of load: < wc_intended_load | wc_per_client_load >", default="wc_per_client_load")
    required.add_argument('--do_interopability', action = 'store_true')

    # optional.add_argument('--no_postcleanup', help="Cleanup the cross connections after test is stopped", action = 'store_true')
    # optional.add_argument('--no_precleanup', help="Cleanup the cross connections before test is started", action = 'store_true')
    optional.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action = 'store_true')
    optional.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action = 'store_true')
    optional.add_argument('--incremental',help='gives an option to the user to enter incremental values',action='store_true')
    optional.add_argument('--security',help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >',default="open")
    optional.add_argument('--test_name',help='Specify test name to store the runtime csv results', default=None)
    optional.add_argument('--result_dir',help='Specify the result dir to store the runtime logs', default='')

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)

    args=parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    
    loads={}
    iterations_before_test_stopped_by_user=[]

    # Case based on download and upload arguments are provided
    if args.download and args.upload:
        loads = {'upload': str(args.upload).split(","), 'download': str(args.download).split(",")}
        loads_data=loads["download"]
    elif args.download:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for i in range(len(args.download)):
            loads['upload'].append(2560)
        loads_data=loads["download"]
    else:
        if args.upload:
            loads = {'upload': str(args.upload).split(","), 'download': []}
            for i in range(len(args.upload)):
                loads['download'].append(2560)
            loads_data=loads["upload"]

    if args.do_interopability:
        args.incremental_capacity="1"
   

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
    if args.report_timer.endswith('s') or args.report_timer.endswith('S') :
        args.report_timer=int(args.report_timer[0:-1]) 

    elif args.report_timer.endswith('m') or args.report_timer.endswith('M')   :
        args.report_timer=int(args.report_timer[0:-1]) * 60

    elif args.report_timer.endswith('h') or args.report_timer.endswith('H')  :
        args.report_timer=int(args.report_timer[0:-1]) * 60 * 60

    elif args.test_duration.endswith(''):        
        args.report_timer=int(args.report_timer)

    
    if (int(args.packet_size)<16 or int(args.packet_size)>65507) and int(args.packet_size)!=-1:
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
                                precleanup=args.precleanup
                                )

        throughput.os_type()

        check_condition,clients_to_run=throughput.phantom_check()

        if check_condition==False:
            return

        check_increment_condition=throughput.check_incremental_list()

        if check_increment_condition==False:
            logger.error("Incremental values given for selected devices are incorrect")
            return
        
        elif(len(args.incremental_capacity)>0 and check_increment_condition==False):
            logger.error("Incremental values given for selected devices are incorrect")
            return
        
        created_cxs = throughput.build()
        time.sleep(10)
        created_cxs=list(created_cxs.keys())
        individual_dataframe_column=[]
        
        to_run_cxs,to_run_cxs_len,created_cx_lists_keys,incremental_capacity_list = throughput.get_incremental_capacity_list()
        
        for i in range(len(clients_to_run)):

            # Extend individual_dataframe_column with dynamically generated column names
            individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop A {clients_to_run[i]}', f'Rx % Drop B{clients_to_run[i]}',f'RSSI {clients_to_run[i]} ',f'Link Speed {clients_to_run[i]} '])
        
        individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop A', 'Overall Rx % Drop B','Iteration','TIMESTAMP','Start_time','End_time','Remaining_Time','Incremental_list','status'])
        individual_df=pd.DataFrame(columns=individual_dataframe_column)

        overall_start_time=datetime.now()
        overall_end_time=overall_start_time + timedelta(seconds=int(args.test_duration)*len(incremental_capacity_list))

        for i in range(len(to_run_cxs)):
            # Check the load type specified by the user
            if args.load_type == "wc_intended_load":
                # Perform intended load for the current iteration
                throughput.perform_intended_load(i,incremental_capacity_list)
                if i!=0:

                    # Stop throughput testing if not the first iteration
                    throughput.stop()

                # Start specific connections for the current iteration
                throughput.start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
            else:
                if (args.do_interopability and i!=0):
                    throughput.stop_specific(to_run_cxs[i-1])
                    time.sleep(5)
                throughput.start_specific(to_run_cxs[i])

            # Determine device names based on the current iteration
            device_names=created_cx_lists_keys[:to_run_cxs_len[i][-1]]

            # Monitor throughput and capture all dataframes and test stop status
            all_dataframes,test_stopped_by_user = throughput.monitor(i,individual_df,device_names,incremental_capacity_list,overall_start_time,overall_end_time)
            
            # Check if the test was stopped by the user
            if test_stopped_by_user==False:

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
    throughput.generate_report(list(set(iterations_before_test_stopped_by_user)),incremental_capacity_list,data=all_dataframes,data1=to_run_cxs_len,report_path=throughput.result_dir)
if __name__ == "__main__":
    main()

    