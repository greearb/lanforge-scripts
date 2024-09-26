# #!/usr/bin/env python3
# flake8: noqa



"""
    NAME: lf_interop_video_streaming.py
    Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
    For now the test script supports for Video streaming of real devices.

    Pre-requisites: Real devices should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge

    Prints the list of data from layer4-7 such as uc-avg time, total url's, url's per sec

    Example-1:
    Command Line Interface to run Video Streaming test with media source HLS and media quality 1080P :
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test

    Example-2:
    Command Line Interface to run Video Streaming test with media source DASH and media quality 4K :
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd" --media_source dash --media_quality 4K --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test

    Example-3:
    Command Line Interface to run the Video Streaming test with specified Resources:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test


    Example-4:
    Command Line Interface to run the Video Streaming test with incremental Capacity by specifying the --incremental flag
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.11 --incremental --debug --test_name video_streaming_test

    Example-5:
    Command Line Interface to run Video Streaming test with precleanup:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P  --duration 1m --device_list 1.10,1.11 --precleanup --debug --test_name video_streaming_test

    Example-6:
    Command Line Interface to run Video Streaming test with postcleanup:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.11 --postcleanup --debug --test_name video_streaming_test

    SCRIPT CLASSIFICATION: Test

    SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

    NOTES:
        1. Use './lf_interop_video_streaming.py --help' to see command line usage and options.
        2. If --device_list are not given after passing the CLI, a list of available devices will be displayed on the terminal.
        3. To run the test by specifying the incremental capacity, enable the --incremental flag. 
        
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
from lf_graph import lf_line_graph



if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
base = importlib.import_module('py-scripts.lf_base_interop_profile')
lf_csv = importlib.import_module("py-scripts.lf_csv")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
base_RealDevice = base.RealDevice
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")




class VideoStreamingTest(Realm):
    def __init__(self, host, ssid, passwd, encryp,media_source,media_quality, suporrted_release=None, max_speed=None, url=None,
                urls_per_tenm=None, duration=None, resource_ids = None, dowebgui = False,result_dir = "",test_name = None, incremental = None,postcleanup=False,precleanup=False):
        super().__init__(lfclient_host=host, lfclient_port=8080)
        self.adb_device_list = None
        self.host = host
        self.phn_name = []
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        self.media_source=media_source
        self.media_quality=media_quality
        self.supported_release = suporrted_release
        self.device_name = []
        self.android_devices = []
        self.other_os_list = []
        self.android_list = []
        self.other_list = []
        self.real_sta_data_dict = {}
        self.health = None
        self.phone_data = None
        self.max_speed = max_speed
        self.url = url
        self.urls_per_tenm = urls_per_tenm
        self.duration = duration
        self.resource_ids = resource_ids
        self.dowebgui = dowebgui
        self.result_dir = result_dir
        self.test_name = test_name
        self.incremental = incremental
        self.postCleanUp=postcleanup
        self.preCleanUp=precleanup
        self.devices = base_RealDevice(manager_ip = self.host, selected_bands = [])
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=8080)
        self.http_profile = self.local_realm.new_http_profile()
        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=8080,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        self.utility = base.UtilityInteropWifi(host_ip=self.host)
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'youtube'
        self.generic_endps_profile.name_prefix = "yt"

    @property
    def run(self):
        # Checks various configuration things on Interop tab, Uses lf_base_interop_profile.py library
        self.adb_device_list = self.interop.check_sdk_release()
        for i in self.adb_device_list:
            self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
        logging.info(self.device_name)


        self.interop.stop()
        for i in self.adb_device_list:
            self.interop.batch_modify_apply(i)
            time.sleep(5)
        self.interop.set_user_name(device=self.adb_device_list)

        for i in self.adb_device_list:
            self.utility.forget_netwrk(i)

        health = dict.fromkeys(self.adb_device_list)
        # Getting Health for each device
        for i in self.adb_device_list:
            # post = self.utility.post_adb_(device=i,cmd="shell ip addr show wlan0  | grep 'inet ' | cut -d ' ' -f 6 | cut -d / -f 1")
            # print("POST IP ", post)
            dev_state = self.utility.get_device_state(device=i)
            logging.info("Device State : {dev_state}".format(dev_state = dev_state))

            logging.info("device state" + dev_state)
            if dev_state == "COMPLETED,":
                logging.info("phone is in connected state")
                logging.info("phone is in connected state")
                ssid = self.utility.get_device_ssid(device=i)
                if ssid == self.ssid:
                    logging.info("device is connected to expected ssid")
                    logging.info("device is connected to expected ssid")
                    health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                    logging.info("health health:: ", health)
                    logging.info("Launching Interop UI")
                    logging.info("health :: {health}".format(health = health))
                    logging.info("Launching Interop UI")

                    self.interop.launch_interop_ui(device=i)
        self.health = health
        logging.info("Health:: ", health)

        self.phone_data = self.get_resource_data()
        logging.info("Phone List : ", self.phone_data)
        logging.info("Phone List : {phone_data}".format(phone_data = self.phone_data))

        time.sleep(5)
    
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
    
    def build(self):
        """If the Pre-requisites are satisfied then this function gets the list of Real devices connected to LANforge
        and processes them for Layer 4-7 traffic profile creation
        """

        self.data = {}
        self.total_urls_dict = {}
        self.data_for_webui = {}
        self.all_cx_list = []

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
        self.phone_data = self.get_resource_data()
        
        self.http_profile.direction = 'dl'
        self.http_profile.dest = '/dev/null'
        self.http_profile.max_speed = self.max_speed
        self.http_profile.requests_per_ten = self.urls_per_tenm
        upload_name=self.phone_data[-1].split('.')[-1]
        if self.preCleanUp:
            self.http_profile.created_cx=self.convert_to_dict(self.phone_data)
            self.precleanup()
        logging.info("Creating Layer-4 endpoints from the user inputs as test parameters")
        time.sleep(5)
        self.http_profile.created_cx.clear()
        self.http_profile.create(ports=self.phone_data, sleep_time=.5,upload_name=upload_name,
                                 suppress_related_commands_=None, http=True,
                                 http_ip=self.url, interop=True, proxy_auth_type=74240,media_source=self.media_source,media_quality=self.media_quality,timeout=1000)
        
    def start(self):
        # Starts the layer 4-7 traffic for created CX end points
        # print("Test Started")
        logging.info("Setting Cx State to Runnning")
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass
    
    def start_specific(self,cx_start_list):
        # Starts the layer 4-7 traffic for created CX end points
        # print("Test Started")
        # self.http_profile.start_cx_specific(cx_start_list)
        logging.info("Setting Cx State to Runnning")
        for cx_name in cx_start_list:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name":self.http_profile.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
        logging.info("Setting Cx State to Runnning")
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    # def create_generic_endp(self,query_resources,os_types_dict):
    #     ports_list = []
    #     eid = ""
    #     resource_ip = ""
    #     user_resources = ['.'.join(item.split('.')[:2]) for item in query_resources]
    #     exit_loop = False
    #     response = self.json_get("/resource/all")
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

    #     response_port = self.json_get("/port/all")
    #     if "interfaces" not in response_port.keys():
    #         logger.error("Error: 'interfaces' key not found in port data")
    #         exit(1)

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
        
    #     real_sta_os_types = [os_types_dict[resource_id] for resource_id in os_types_dict if os_types_dict[resource_id] != 'android']
        
    #     # if (self.generic_endps_profile.create(ports=self.other_list, sleep_time=.5, real_client_os_types=real_sta_os_types, url = self.url, gen_port = gen_ports_list)):
    #     if (self.generic_endps_profile.create(ports=self.other_list, sleep_time=.5, real_client_os_types=real_sta_os_types, gen_port = gen_ports_list, from_script = "videostream")):
    #         logging.info('Real client generic endpoint creation completed.')
    #     else:
    #         logging.error('Real client generic endpoint creation failed.')
    #         exit(0)
        
    #     # setting endpoint report time to ping packet interval
    #     for endpoint in self.generic_endps_profile.created_endp:
    #         self.generic_endps_profile.set_report_timer(endp_name=endpoint, timer=250)

    def stop(self):
        # Stops the layer 4-7 traffic for created CX end points
        if self.resource_ids:
            self.data['remaining_time_webGUI'] = ["0:00:00"] 
        logging.info("Setting Cx State to Stopped")
        self.http_profile.stop_cx()
    
    def precleanup(self):
        self.http_profile.cleanup()
    
    def postcleanup(self):
        # Cleans the layer 4-7 traffic for created CX end points
        self.http_profile.cleanup()

    # def cleanup(self,os_types_dict):
    #     for station in os_types_dict:
    #         if any(item.startswith(station) for item in self.other_os_list):
    #             self.generic_endps_profile.created_cx.append(
    #                 'CX_yt-{}'.format(station))
    #             self.generic_endps_profile.created_endp.append(
    #                 'yt-{}'.format(station))
    #     logging.info('Cleaning up generic endpoints if exists')
    #     self.generic_endps_profile.cleanup()
    #     self.generic_endps_profile.created_cx = []
    #     self.generic_endps_profile.created_endp = []
    #     logging.info('Cleanup Successful')
    
    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        data1 = []
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


    def get_resource_data(self):
        # Gets the list of Real devices connected to LANforge
        resource_id_list = []
        phone_name_list = []
        mac_address = []
        user_name = []
        phone_radio = []
        rx_rate = []
        tx_rate = []
        station_name = []
        ssid = []

        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
        if "interfaces" not in eid_data.keys():
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)
        resource_ids = []
        if self.resource_ids:
            resource_ids = list(map(int, self.resource_ids.split(',')))
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_id_list.append(i.split(".")[1])
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        station_name.append(i)

                    mac = alias[i]["mac"]

                    rx = "Unknown" if (alias[i]["rx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["rx-rate"]
                    tx = "Unknown" if (alias[i]["tx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["tx-rate"]
                    ssid.append(alias[i]["ssid"])
                    rx_rate.append(rx)
                    tx_rate.append(tx)
                    # Getting username
                    user = resource_hw_data['resource']['user']
                    user_name.append(user)
                    # Getting user Hardware details/Name
                    hw_name = resource_hw_data['resource']['hw version'].split(" ")
                    name = " ".join(hw_name[0:2])
                    phone_name_list.append(name)
                    mac_address.append(mac)
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and alias[i]["parent dev"] == 'wiphy0':
                   
                    # Mapping Radio Name in human readable format
                    if 'a' not in alias[i]['mode'] or "20" in alias[i]['mode']:
                        phone_radio.append('2G')
                    elif 'AUTO' in alias[i]['mode']:
                        phone_radio.append("AUTO")
                    else:
                        phone_radio.append('2G/5G')
        return station_name
    
    def get_signal_data(self):
        resource_ids = list(map(int, self.resource_ids.split(',')))
        rssi = []
        tx_rate = []
        rx_rate = []

        try:
            eid_data = self.json_get("ports?fields=alias,rx-rate,tx-rate,ssid,signal")
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)
        for alias in eid_data["interfaces"]:
            for i in alias:
                # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids :
                        
                        rssi.append(alias[i]['signal'])
                        tx_rate.append(alias[i]['tx-rate'])
                        rx_rate.append(alias[i]['rx-rate'])
        
        rssi=[int(i) for i in rssi]
        return rssi,tx_rate

    def monitor_for_runtime_csv(self,duration,file_path,individual_df,iteration,actual_start_time,resource_list_sorted = [],cx_list = [] ):        
        self.all_cx_list.extend(cx_list) 
        resource_ids = list(map(int, self.resource_ids.split(',')))
        self.data_for_webui['resources'] = resource_ids
        starttime = datetime.now()
        self.data["name"] = self.my_monitor('name')
        current_time = datetime.now()
        endtime = ""
        endtime = starttime + timedelta(minutes=duration)
        endtime = endtime.isoformat()[0:19]
        endtime_check = datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%S")
        self.data['status'] = self.my_monitor('status')

        # # self.data['required_count'] = [self.urls_per_tenm] * len(self.data['name'])
        # self.data['duration'] = [duration] * len(self.data['name'])
        # self.data['url'] = [self.url] * len(self.data['name'])

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
        if "interfaces" not in eid_data.keys():
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        for alias in eid_data["interfaces"]:
            for i in alias:
                # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids :
                        device_type.append('Android')
                        username.append(resource_hw_data['resource']['user'] )
                        ssid.append(alias[i]['ssid'])
                        mac.append(alias[i]['mac'])
                        mode.append(alias[i]['mode'])
                        rssi.append(alias[i]['signal'])
                        channel.append(alias[i]['channel'])
                        tx_rate.append(alias[i]['tx-rate'])
                        rx_rate.append(alias[i]['rx-rate'])
   
        incremental_capacity_list=self.get_incremental_capacity_list()
        video_rate_dict= {i: [] for i in range(len(device_type))}

        # Loop until the current time is less than the end time
        while current_time < endtime_check:
            
            # Get signal data for RSSI and link speed
            rssi_data,link_speed_data=self.get_signal_data()

            # Monitor total buffers and total errors
            total_buffer=self.my_monitor('total-buffers')
            total_err = self.my_monitor('total-err')

            # Initialize a list to store individual dataframe data
            individual_df_data=[]

            # Update the end time for the web GUI if necessary
            if self.data['end_time_webGUI'][0] < current_time.strftime('%Y-%m-%d %H:%M:%S'):
                self.data['end_time_webGUI'] = [current_time.strftime('%Y-%m-%d %H:%M:%S')] 

            # Get the current time and calculate the remaining time
            curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            endtime_dt = datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S")
            curr_time_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
            remaining_time_dt = endtime_dt - curr_time_dt
            one_minute = timedelta(minutes=1)

            # Update the remaining time for the web GUI
            if remaining_time_dt < one_minute:
                self.data['remaining_time_webGUI'] = ["< 1 min"] 
            else:
                self.data['remaining_time_webGUI'] = [str(datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S"))] 
            
            # Get the present time
            present_time=datetime.now().strftime("%H:%M:%S")

            # Monitor various metrics
            self.data['status'] = self.my_monitor('status')
            self.data["total_urls"] = self.my_monitor('total-urls')
            self.data["name"] = self.my_monitor('name')
            self.data["total_err"] = self.my_monitor('total-err')
            # self.data["timeout"] = self.my_monitor('timeout')
            self.data["video_format_bitrate"]=self.my_monitor('video-format-bitrate')
            self.data["bytes_rd"]=self.my_monitor("bytes-rd")
            self.data["total_wait_time"]=self.my_monitor("total-wait-time")
       
            overall_video_rate=[]

            # Iterate through the total wait time data
            for i in range(len(self.my_monitor("total-wait-time"))):
                
                # If the status is 'Stopped', append 0 to the video rate dictionary and overall video rate
                if self.data['status'][i]=='Stopped':

                    video_rate_dict[i].append(0)
                    overall_video_rate.append(0)
                    individual_df_data.extend([0,0,0,rssi_data[i],link_speed_data[i],total_buffer[i],total_err[i],min(video_rate_dict[i]),max(video_rate_dict[i]),sum(video_rate_dict[i])/len(video_rate_dict[i])])
                
                # If the status is not 'Stopped', append the calculated video rate to the video rate dictionary and overall video rate
                else:

                    video_rate_dict[i].append(round(self.data["video_format_bitrate"][i]/1000000,2))
                    overall_video_rate.append(round(self.data["video_format_bitrate"][i]/1000000,2))
                    individual_df_data.extend([round(self.data["video_format_bitrate"][i]/1000000,2),round(self.data["total_wait_time"][i]/1000,2),self.data["total_urls"][i],int(rssi_data[i]),link_speed_data[i],total_buffer[i],total_err[i],min(video_rate_dict[i]),max(video_rate_dict[i]),sum(video_rate_dict[i])/len(video_rate_dict[i])])
            
            individual_df_data.extend([sum(overall_video_rate),present_time,iteration+1,actual_start_time.strftime('%Y-%m-%d %H:%M:%S'),self.data['end_time_webGUI'][0],self.data['remaining_time_webGUI'][0],"Running"])
            individual_df.loc[len(individual_df)]=individual_df_data
            individual_df.to_csv('video_streaming_realtime_data.csv', index=False)

            
            if self.dowebgui == True:
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                self.test_name),'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logging.info('Test is stopped by the user')
                        break

            # df1 = pd.DataFrame(self.data)

            if self.dowebgui == True:
                individual_df.to_csv('{}/video_streaming_realtime_data.csv'.format(self.result_dir), index=False)
            else:
                individual_df.to_csv(file_path, mode='w', index=False)

            time.sleep(1)
            
            current_time = datetime.now()

        present_time=datetime.now().strftime("%H:%M:%S")
        individual_df_data=[]
        overall_video_rate=[]

        # Collecting data when test is stopped
        for i in range(len(self.my_monitor("total-wait-time"))):
            if self.data['status'][i]=='Stopped':
                video_rate_dict[i].append(0)
                overall_video_rate.append(0)
                individual_df_data.extend([0,0,0,rssi_data[i],link_speed_data[i],total_buffer[i],total_err[i],min(video_rate_dict[i]),max(video_rate_dict[i]),sum(video_rate_dict[i])/len(video_rate_dict[i])])
            else:
                overall_video_rate.append(round(self.data["video_format_bitrate"][i]/1000000,2))
                video_rate_dict[i].append(round(self.data["video_format_bitrate"][i]/1000000,2))
                individual_df_data.extend([round(self.data["video_format_bitrate"][i]/1000000,2),round(self.data["total_wait_time"][i]/1000,2),self.data["total_urls"][i],int(rssi_data[i]),link_speed_data[i],total_buffer[i],total_err[i],min(video_rate_dict[i]),max(video_rate_dict[i]),sum(video_rate_dict[i])/len(video_rate_dict[i])])

        if iteration+1 == len(incremental_capacity_list): 
            individual_df_data.extend([sum(overall_video_rate),present_time,iteration+1,actual_start_time.strftime('%Y-%m-%d %H:%M:%S'),self.data['end_time_webGUI'][0],0,"Stopped"])
        else:
            individual_df_data.extend([sum(overall_video_rate),present_time,iteration+1,actual_start_time.strftime('%Y-%m-%d %H:%M:%S'),self.data['end_time_webGUI'][0],self.data['remaining_time_webGUI'][0],"Stopped"])
        individual_df.loc[len(individual_df)]=individual_df_data
        individual_df.to_csv('video_streaming_realtime_data.csv', index=False)

        if self.data['end_time_webGUI'][0] < current_time.strftime('%Y-%m-%d %H:%M:%S'):
            self.data['end_time_webGUI'] = [current_time.strftime('%Y-%m-%d %H:%M:%S') ] 

        curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        curr_time_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
        endtime_dt = datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S")

        remaining_time_dt = endtime_dt - curr_time_dt
        one_minute = timedelta(minutes=1)


        if remaining_time_dt < one_minute:
            self.data['remaining_time_webGUI'] = ["< 1 min"] 
        else:
            self.data['remaining_time_webGUI'] = [str(datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S"))] 

    def get_incremental_capacity_list(self):
        keys=list(self.http_profile.created_cx.keys())
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

    def generate_report(self, date, test_setup_info, realtime_dataset, report_path = '', cx_order_list = []):
        logging.info("Creating Reports")
         # Initialize the report object  
        if self.dowebgui == True and report_path == '':
           
            report = lf_report.lf_report(_results_dir_name="VideoStreaming_test", _output_html="VideoStreaming_test.html",
                                        _output_pdf="VideoStreaming_test.pdf", _path=self.result_dir)
        else:
            report = lf_report.lf_report(_results_dir_name="VideoStreaming_test_test", _output_html="VideoStreaming_test.html",
                                        _output_pdf="VideoStreaming_test.pdf", _path=report_path)

        # To store throughput_data.csv in report folder    
        report_path_date_time = report.get_path_date_time()
        shutil.move('video_streaming_realtime_data.csv',report_path_date_time)
        
        # Getting incremental capacity in lists
        created_incremental_values=self.get_incremental_capacity_list()
        keys=list(self.http_profile.created_cx.keys())

        # Set report title, date, and build banner
        report.set_title("Video Streaming Test")
        report.set_date(date)
        report.build_banner()
        report.set_obj_html("Objective", "The Candela Web browser test is designed to measure the Access Point performance and stability by browsing multiple websites in real clients like"
        "Android, Linux, windows, and IOS which are connected to the access point. This test allows the user to choose the options like website link, the"
        "number of times the page has to browse, and the Time taken to browse the page. Along with the performance other measurements made are client"
        "connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the AP to be able to handle several stations"
        "(within the limitations of the AP specs) and make sure all clients can browse the page.")
        report.build_objective()
        report.set_table_title("Input Parameters")
        report.build_table_title()

        report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        
       

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
        try:
            eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        # Loop through interfaces
        for alias in eid_data["interfaces"]:
            for i in alias:
                # Check interface index and alias
                # alias[i]['mac'] alias[i]['ssid'] alias[i]['mode'] resource_hw_data['resource']['user']  
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    
                    # Get resource data for specific interface
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    
                    # Filter based on OS and resource ID
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        device_type.append('Android')
                        username.append(resource_hw_data['resource']['user'] )
                        ssid.append(alias[i]['ssid'])
                        mac.append(alias[i]['mac'])
                        mode.append(alias[i]['mode'])
                        rssi.append(alias[i]['signal'])
                        channel.append(alias[i]['channel'])
                        tx_rate.append(alias[i]['tx-rate']) 
        total_urls = self.my_monitor('total-urls')
        total_err = self.my_monitor('total-err')
        total_buffer=self.my_monitor('total-buffers')
        
        # Iterate through the length of cx_order_list
        for iter in range(len(cx_order_list)):
            data_set_in_graph,wait_time_data,devices_on_running_state,device_names_on_running=[],[],[],[]
            devices_data_to_create_wait_time_bar_graph=[]
            max_video_rate,min_video_rate,avg_video_rate=[],[],[]
            total_url_data,rssi_data=[],[]
            trimmed_data_set_in_graph=[]
             # Retrieve data for the previous iteration, if it's not the first iteration
            if iter !=0:
                before_data_iter=realtime_dataset[realtime_dataset['iteration']==iter]
            # Retrieve data for the current iteration
            data_iter=realtime_dataset[realtime_dataset['iteration']==iter+1]

             # Populate the list of devices on running state and their corresponding usernames
            for j in range(created_incremental_values[iter]):
                devices_on_running_state.append(keys[j])
                device_names_on_running.append(username[j])

            # Iterate through each device currently running
            for k in devices_on_running_state:
                # Filter columns related to the current device
                columns_with_substring = [col for col in data_iter.columns if k in col]
                filtered_df = data_iter[columns_with_substring]
                if iter !=0:
                    # Filter columns related to the current device from the previous iteration
                    before_iter_columns_with_substring = [col for col in before_data_iter.columns if k in col]
                    before_filtered_df=before_data_iter[before_iter_columns_with_substring]
                
                # Extract and compute max, min, and average video rates
                max_video_rate.append(max(filtered_df[[col for col in  filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()))
                min_video_rate.append(min(filtered_df[[col for col in  filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()))
                avg_video_rate.append(round(sum(filtered_df[[col for col in  filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()),2))
                wait_time_data.append(filtered_df[[col for col in  filtered_df.columns if "total_wait_time" in col][0]].values.tolist()[-1])
                rssi_data.append(int(round(sum(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist())/len(filtered_df[[col for col in  filtered_df.columns if "RSSI" in col][0]].values.tolist()),2))*-1)

                if iter !=0:
                    # Calculate the difference in total URLs between the current and previous iterations
                    total_url_data.append(abs(filtered_df[[col for col in  filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1]-before_filtered_df[[col for col in  before_filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1]))
                else:
                    # Append the total URLs for the first iteration
                    total_url_data.append(filtered_df[[col for col in  filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1])
            
            # Append the wait time data to the list for creating the wait time bar graph
            devices_data_to_create_wait_time_bar_graph.append(wait_time_data)
            
           
            # Extract overall video format bitrate values for the current iteration and append to data_set_in_graph
            video_streaming_values_list=realtime_dataset['overall_video_format_bitrate'][realtime_dataset['iteration']==iter+1].values.tolist()
            data_set_in_graph.append(video_streaming_values_list)


            # Trim the data in data_set_in_graph and append to trimmed_data_set_in_graph
            for _ in range(len(data_set_in_graph)):
                trimmed_data_set_in_graph.append(self.trim_data(len(data_set_in_graph[_]),data_set_in_graph[_]))

            # If there are multiple incremental values, add custom HTML content to the report for the current iteration
            if len(created_incremental_values)>1:
                report.set_custom_html(f"<h2><u>Iteration-{iter+1}: test running on devices : {', '.join(device_names_on_running)}</u></h2>")
                report.build_custom()

            report.set_obj_html(
                            _obj_title="Realtime Video Rate",
                            _obj="")
            report.build_objective()

            # Create a line graph for video rate over time 
            graph=lf_line_graph(_data_set=trimmed_data_set_in_graph,
                        _xaxis_name="Time",
                        _yaxis_name="Video Rate (Mbps)",
                        _xaxis_categories=self.trim_data(len(realtime_dataset['timestamp'][realtime_dataset['iteration']==iter+1].values.tolist()),realtime_dataset['timestamp'][realtime_dataset['iteration']==iter+1].values.tolist()),
                        _label=['Rate'],
                        _graph_image_name=f"line_graph{iter}"
                        )
            graph_png = graph.build_line_graph()
            logger.info("graph name {}".format(graph_png))
            report.set_graph_image(graph_png)
            report.move_graph_image()
            
            report.build_graph()

            # Define figure size for horizontal bar graphs
            x_fig_size = 15
            y_fig_size = len(devices_on_running_state) * .5 + 4
            
            report.set_obj_html(
                            _obj_title="Total Urls Per Device",
                            _obj="")
            report.build_objective()
            # Create a horizontal bar graph for total URLs per device 
            graph=lf_bar_graph_horizontal(_data_set=[total_url_data],
                                            _xaxis_name="Total Urls",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"total_urls_image_name{iter}",
                                            _label=["Total Urls"],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _figsize=(x_fig_size, y_fig_size)
                                            #    _color=['lightcoral']
                                                )
            graph_png = graph.build_bar_graph_horizontal()
            logger.info("wait time graph name {}".format(graph_png))
            graph.build_bar_graph_horizontal()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()

            report.set_obj_html(
                            _obj_title="Max/Min Video Rate Per Device",
                            _obj="")
            report.build_objective()
            
            # Create a horizontal bar graph for max and min video rates per device
            graph=lf_bar_graph_horizontal(_data_set=[max_video_rate,min_video_rate],
                                            _xaxis_name="Max/Min Video Rate(Mbps)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"max-min-video-rate_image_name{iter}",
                                            _label=['Max Video Rate','Min Video Rate'],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _figsize=(x_fig_size, y_fig_size)
                                            #    _color=['lightcoral']
                                                )
            graph_png = graph.build_bar_graph_horizontal()
            logger.info("max/min graph name {}".format(graph_png))
            graph.build_bar_graph_horizontal()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()

            report.set_obj_html(
                            _obj_title="Wait Time Per Device",
                            _obj="")
            report.build_objective()

            # Create a horizontal bar graph for wait time per device
            graph=lf_bar_graph_horizontal(_data_set=devices_data_to_create_wait_time_bar_graph,
                                            _xaxis_name="Wait Time(seconds)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"wait_time_image_name{iter}",
                                            _label=['Wait Time'],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _figsize=(x_fig_size, y_fig_size)
                                            #    _color=['lightcoral']
                                                )
            graph_png = graph.build_bar_graph_horizontal()
            logger.info("wait time graph name {}".format(graph_png))
            graph.build_bar_graph_horizontal()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()

        # Table 1
            report.set_obj_html("Overall - Detailed Result Table", "The below tables provides detailed information for the web browsing test.")
            report.build_objective()

            




            # Create a dataframe for the detailed result table and append it to the report
            dataframe = {
                " DEVICE TYPE " : device_type[:created_incremental_values[iter]],
                " Username " : username[:created_incremental_values[iter]],
                " SSID " : ssid[:created_incremental_values[iter]] ,
                " MAC " : mac[:created_incremental_values[iter]],
                " Channel " : channel[:created_incremental_values[iter]],
                " Mode " : mode[:created_incremental_values[iter]],
                " Buffers" : total_buffer[:created_incremental_values[iter]],
                " Wait-Time(Sec)": wait_time_data,
                " Min Video Rate(Mbps) " : min_video_rate[:created_incremental_values[iter]],
                " Avg Video Rate(Mbps) " : avg_video_rate[:created_incremental_values[iter]],
                " Max Video Rate(Mbps) " : max_video_rate[:created_incremental_values[iter]],
                " Total URLs " : total_urls[:created_incremental_values[iter]],
                " Total Errors " : total_err[:created_incremental_values[iter]],
                " RSSI (dbm)" : ['-'+ str(n) for n in rssi_data[:created_incremental_values[iter]]],
                " Link Speed ": tx_rate[:created_incremental_values[iter]]
            }
            dataframe1 = pd.DataFrame(dataframe)
            report.set_table_dataframe(dataframe1)
            report.build_table()
            



            # Set and build title for the overall results table
            report.set_table_title("Overall Results")
            report.build_table_title()
            dataframe2 = {
                            " DEVICE" : username[:created_incremental_values[iter]],
                            " TOTAL ERRORS " : total_err[:created_incremental_values[iter]],
                        }
            dataframe3 = pd.DataFrame(dataframe2)
            report.set_table_dataframe(dataframe3)
            report.build_table()
        report.build_footer()
        html_file = report.write_html()
        report.write_pdf()

        # if self.dowebgui == True:
        #     for i in range(len(self.data["end_time"])):
        #         if self.data["status"][i] == "Run":
        #             self.data["status"][i] = "Completed"
        #     df = pd.DataFrame(self.data)
        #     if self.dowebgui == True:
        #         df.to_csv('{}/rb_datavalues.csv'.format(self.result_dir), index=False)

def main():
    help_summary = '''\
    The Candela Web browser test is designed to measure an Access Point’s client capacity and performance when handling different amounts of Real clients like android, Linux,
    windows, and IOS. The test allows the user to increase the number of clients in user-defined steps for each test iteration and measure the per client and the overall throughput for
    this test, we aim to assess the capacity of network to handle high volumes of traffic while
    each trial. Along with throughput other measurements made are client connection times, Station 4-Way Handshake time, DHCP times, and more. The expected behavior is for the
    AP to be able to handle several stations (within the limitations of the AP specs) and make sure all Clients get a fair amount of airtime both upstream and downstream. An AP that
    scales well will not show a significant overall throughput decrease as more Real clients are added.
    '''

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description="""\
        
        NAME: lf_interop_video_streaming.py

        Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
        For now the test script supports for Video streaming of real devices.

        Pre-requisites: Real devices should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge


        Prints the list of data from layer4-7 such as uc-avg time, total url's, url's per sec

        Example-1:
        Command Line Interface to run Video Streaming test with media source HLS and media quality 1080P :
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test

        Example-2:
        Command Line Interface to run Video Streaming test with media source DASH and media quality 4K :
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd" --media_source dash --media_quality 4K --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test

        Example-3:
        Command Line Interface to run the Video Streaming test with specified Resources:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test


        Example-4:
        Command Line Interface to run the Video Streaming test with incremental Capacity by specifying the --incremental flag
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.12 --incremental --debug --test_name video_streaming_test

        Example-5:
        Command Line Interface to run Video Streaming test with precleanup:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P  --duration 1m --device_list 1.10,1.12 --precleanup --debug --test_name video_streaming_test

        Example-6:
        Command Line Interface to run Video Streaming test with postcleanup:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls --media_quality 1080P --duration 1m --device_list 1.10,1.12 --postcleanup --debug --test_name video_streaming_test

        SCRIPT CLASSIFICATION: Test

        SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

        NOTES:
            1. Use './lf_interop_video_streaming.py --help' to see command line usage and options.
            2. If --device_list are not given after passing the CLI, a list of available devices will be displayed on the terminal.
            3. To run the test by specifying the incremental capacity, enable the --incremental flag. 
            
        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date - 29/07/2024
        Build version - 5.4.8
        kernel version - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.


    """)

        
    parser.add_argument("--host", "--mgr", required = True, help='specify the GUI to connect to, assumes port '
                                                                        '8080')
    parser.add_argument("--ssid", default="ssid_wpa_2g", help='specify ssid on which the test will be running')
    parser.add_argument("--passwd", default="something", help='specify encryption password  on which the test will '
                                                        'be running')
    parser.add_argument("--encryp", default="psk", help='specify the encryption type  on which the test will be '
                                                        'running eg :open|psk|psk2|sae|psk2jsae')
    parser.add_argument("--url", default="www.google.com", help='specify the url you want to test on')
    parser.add_argument("--max_speed", type=int, default=0, help='specify the max speed you want in bytes')
    parser.add_argument("--urls_per_tenm", type=int, default=100, help='specify the number of url you want to test on '
                                                                    'per minute')
    parser.add_argument('--duration', type=str, help='time to run traffic')
    parser.add_argument('--test_name',required = True, help='Name of the Test')
    parser.add_argument('--dowebgui',help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--result_dir',help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')
    # parser.add_argument('--incremental',help="Specify the incremental values <1,2,3..>", required = True, type=str)

    parser.add_argument("--lf_logger_config_json", help="[log configuration] --lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument("--log_level", help="[log configuration] --log_level  debug info warning error critical")
    parser.add_argument("--debug", help="[log configuration] --debug store_true , used by lanforge client ", action='store_true')
    parser.add_argument("--media_source",type=str,default='1')
    parser.add_argument("--media_quality",type=str,default='0')
   
    parser.add_argument('--device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
    parser.add_argument('--webgui_incremental', help="Specify the incremental values <1,2,3..>", type=str)
    parser.add_argument('--incremental', help="--incremental to add incremental values", action = 'store_true')
    parser.add_argument('--no_laptops', help="--to not use laptops", action = 'store_false')
    parser.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action = 'store_true')
    parser.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action = 'store_true')
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)
    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    media_source_dict={
                       'dash':'1',
                       'smooth_streaming':'2',
                       'hls':'3',
                       'progressive':'4',
                       'rtsp':'5'
                       }
    media_quality_dict={
                        '4k':'0',
                        '8k':'1',
                        '1080p':'2',
                        '720p':'3',
                        '360p':'4'
                        }

    media_source,media_quality=args.media_source.capitalize(),args.media_quality
    args.media_source=args.media_source.lower()
    args.media_quality=args.media_quality.lower()

    if any(char.isalpha() for char in args.media_source):
        args.media_source=media_source_dict[args.media_source]

    if any(char.isalpha() for char in args.media_quality):
        args.media_quality=media_quality_dict[args.media_quality]

    

    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    
    logger = logging.getLogger(__name__)

    url = args.url.replace("http://", "").replace("https://", "")

    obj = VideoStreamingTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                        url=url, urls_per_tenm=args.urls_per_tenm, duration=args.duration, 
                        resource_ids = args.device_list, dowebgui = args.dowebgui,media_quality=args.media_quality,media_source=args.media_source,
                        result_dir = args.result_dir,test_name = args.test_name, incremental = args.incremental,postcleanup=args.postcleanup,
                        precleanup=args.precleanup)

    resource_ids_sm = []
    resource_set = set()
    resource_list = []
    # os_types_dict = {}
    # android_devices = []
    # other_os_list = []
    # android_list = []
    # other_list = []
    resource_ids_generated = ""

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
        #     devices,os_types_dict = obj.devices.get_devices(androids=True,laptops = True)

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
            # modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), obj.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
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
            new_android = [int(item.split('.')[1]) for item in obj.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(resource_ids)

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
                if not all(x in modified_list for x in resource_ids1):
                    logging.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = obj.resource_ids
                resource_list = resource_ids_sm.split(',')            
                resource_set = set(resource_list)
                resource_list_sorted = sorted(resource_set)
                resource_ids_generated = ','.join(resource_list_sorted)
                available_resources=list(resource_set)
    if len(available_resources)==0:
        logger.info("No devices which are selected are available in the lanforge")
        exit()
    gave_incremental=False
    if len(resource_list_sorted)==0:
        logger.error("Selected Devices are not available in the lanforge")
        exit(1)
    if args.incremental and not args.webgui_incremental :
        if obj.resource_ids:
            obj.incremental = input('Specify incremental values as 1,2,3 : ')
            obj.incremental = [int(x) for x in obj.incremental.split(',')]
        else:
            logging.info("incremental Values are not needed as Android devices are not selected..")
    elif args.incremental==False:
        gave_incremental=True
        obj.incremental=[len(available_resources)]
    
    if args.webgui_incremental:
        incremental = [int(x) for x in args.webgui_incremental.split(',')]
        if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
            obj.incremental = incremental
    
    # if obj.incremental and (not obj.resource_ids):
    #     logging.info("incremental values are not needed as Android devices are not selected.")
    #     exit()
    
    if obj.incremental and obj.resource_ids:
        resources_list1 = [str(x) for x in obj.resource_ids.split(',')]
        if resource_list_sorted:
            resources_list1 = resource_list_sorted
        if obj.incremental[-1] > len(resources_list1):
            logging.info("Exiting the program as incremental values are greater than the resource ids provided")
            exit()
        elif obj.incremental[-1] < len(resources_list1) and len(obj.incremental) > 1:
            logging.info("Exiting the program as the last incremental value must be equal to selected devices")
            exit()
    
    # To create cx for selected devices
    obj.build()

    # To set media source and media quality 
    time.sleep(10)

    # obj.run
    test_time = datetime.now()
    test_time = test_time.strftime("%b %d %H:%M:%S")

    logging.info("Initiating Test...")

    individual_dataframe_columns=[]

    keys = list(obj.http_profile.created_cx.keys())
  
    #TODO : To create cx for laptop devices
    # if (not args.no_laptops) and obj.other_list:
    #     obj.create_generic_endp(obj.other_list,os_types_dict)

    # Extend individual_dataframe_column with dynamically generated column names
    for i in range(len(keys)):
        individual_dataframe_columns.extend([f'video_format_bitrate{keys[i]}', f'total_wait_time{keys[i]}',f'total_urls{keys[i]}',f'RSSI{keys[i]}',f'Link Speed{keys[i]}',f'Total Buffer {keys[i]}',f'Total Errors {keys[i]}',f'Min_Video_Rate{keys[i]}',f'Max_Video_Rate{keys[i]}',f'Avg_Video_Rate{keys[i]}'])
    individual_dataframe_columns.extend(['overall_video_format_bitrate','timestamp','iteration','start_time','end_time','remaining_Time','status'])
    individual_df=pd.DataFrame(columns=individual_dataframe_columns)
    
    cx_order_list = []
    index = 0
    file_path = ""

    # Parsing test_duration
    if args.duration.endswith('s') or args.duration.endswith('S'):
        args.duration = round(int(args.duration[0:-1])/60,2)
    
    elif args.duration.endswith('m') or args.duration.endswith('M'):
        args.duration = int(args.duration[0:-1]) 
 
    elif args.duration.endswith('h') or args.duration.endswith('H'):
        args.duration = int(args.duration[0:-1]) * 60  
    
    elif args.duration.endswith(''):
        args.duration = int(args.duration)

    incremental_capacity_list_values=obj.get_incremental_capacity_list()
    if incremental_capacity_list_values[-1]!=len(available_resources):
        logger.error("Incremental capacity doesnt match available devices")
        if args.postcleanup==True:
            obj.postcleanup()
        exit(1)
    # Process resource IDs and incremental values if specified
    if obj.resource_ids:
        if obj.incremental:
            test_setup_info_incremental_values =  ','.join(map(str, obj.incremental))
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
            # if incremental_capacity_list_values[-1] != len(available_resources):
            #     test_setup_info_duration_per_iteration= args.duration 
        else:
            test_setup_info_total_duration = args.duration
        if gave_incremental:
            test_setup_info_incremental_values = "No Incremental Value provided"
        obj.total_duration = test_setup_info_total_duration

    actual_start_time=datetime.now()

    # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
    if obj.resource_ids:
        # Check if incremental  is specified
        if obj.incremental:

            # Case 1: Incremental list has only one value and it equals the length of keys
            if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                cx_order_list.append(keys[index:])

            # Case 2: Incremental list has only one value but length of keys is greater than 1
            elif len(obj.incremental) == 1 and len(keys) > 1:
                incremental_value = obj.incremental[0]
                max_index = len(keys)
                index = 0

                while index < max_index:
                    next_index = min(index + incremental_value, max_index)
                    cx_order_list.append(keys[index:next_index])
                    index = next_index

            # Case 3: Incremental list has multiple values and length of keys is greater than 1
            elif len(obj.incremental) != 1 and len(keys) > 1:
                
                index = 0
                for num in obj.incremental:
                    
                    cx_order_list.append(keys[index: num])
                    index = num

                if index < len(keys):
                    cx_order_list.append(keys[index:])
                    start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Iterate over cx_order_list to start tests incrementally
            for i in range(len(cx_order_list)):
                if i == 0:
                    obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] 
                    end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['end_time_webGUI'] = [end_time_webGUI] 


                # time.sleep(10)

                # Start specific devices based on incremental capacity
                obj.start_specific(cx_order_list[i])
                if cx_order_list[i]:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                else:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                
                # duration = 60 * args.duration
                file_path = "video_streaming_realtime_data.csv"

                # start_time = time.time()
                # df = pd.DataFrame(obj.data)

                if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    obj.data['remaining_time_webGUI'] = ['0:00'] 
                else:
                    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] 
                
                if args.dowebgui == True:
                    file_path = os.path.join(obj.result_dir, "../../Running_instances/{}_{}_running.json".format(obj.host, obj.test_name))
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            if data["status"] != "Running":
                                break 
                    obj.monitor_for_runtime_csv(args.duration,file_path,individual_df,i,actual_start_time,resource_list_sorted,cx_order_list[i])
                else:
                    obj.monitor_for_runtime_csv(args.duration,file_path,individual_df,i,actual_start_time,resource_list_sorted,cx_order_list[i])
                    # time.sleep(duration)        
    obj.stop()

    if obj.resource_ids:
        
        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

        phone_list = obj.get_resource_data() 

        username = []
        
        try:
            eid_data = obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        resource_ids = list(map(int, obj.resource_ids.split(',')))
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_hw_data = obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        username.append(resource_hw_data['resource']['user'] )

        device_list_str = ','.join([f"{name} ( Android )" for name in username])

        test_setup_info = {
            "Testname" : args.test_name,
            "Device List" : device_list_str ,
            "No of Devices" : "Total" + "( " + str(len(phone_list)) + " )",
            "Incremental Values" : "",
            "URL" : args.url,
            "Media Source":media_source.upper(),
            "Media Quality":media_quality
        }
        # if obj.incremental:
        #     if len(incremental_capacity_list_values) != len(available_resources):
        #         test_setup_info['Duration per Iteration (min)']= str(test_setup_info_duration_per_iteration)
        test_setup_info['Incremental Values'] = test_setup_info_incremental_values
        test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration) 


       
    logging.info("Test Completed")

    # prev_inc_value = 0
    if obj.resource_ids and obj.incremental :  
        obj.generate_report(date, test_setup_info = test_setup_info,realtime_dataset=individual_df, cx_order_list = cx_order_list) 
    elif obj.resource_ids:
        obj.generate_report(date, test_setup_info = test_setup_info,realtime_dataset=individual_df) 


    # Perform post-cleanup operations
    if args.postcleanup==True:
        obj.postcleanup()

    # Clean up resources based on operating system types
    # if args.postcleanup==True:
    #     obj.cleanup(os_types_dict)

if __name__ == '__main__':
    main() 