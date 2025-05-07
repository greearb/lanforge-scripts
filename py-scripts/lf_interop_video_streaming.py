#!/usr/bin/env python3
"""
    NAME: lf_interop_video_streaming.py
    Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
    For now the test script supports for Video streaming of real devices.

    Pre-requisites: Real devices should be connected to the LANforge MGR and Interop app should be open on the real clients which are connected to Lanforge

    Prints the list of data from layer4-7 such as uc-avg time, total url's, url's per sec

    Example-1:
    Command Line Interface to run Video Streaming test with media source HLS and media quality 1080P :
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test

    Example-2:
    Command Line Interface to run Video Streaming test with media source DASH and media quality 4K :
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd" --media_source dash
    --media_quality 4K --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test

    Example-3:
    Command Line Interface to run the Video Streaming test with specified Resources:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P --duration 1m --device_list 1.10,1.11 --debug --test_name video_streaming_test


    Example-4:
    Command Line Interface to run the Video Streaming test with incremental Capacity by specifying the --incremental flag
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P --duration 1m --device_list 1.10,1.11 --incremental --debug --test_name video_streaming_test

    Example-5:
    Command Line Interface to run Video Streaming test with precleanup:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P  --duration 1m --device_list 1.10,1.11 --precleanup --debug --test_name video_streaming_test

    Example-6:
    Command Line Interface to run Video Streaming test with postcleanup:
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P --duration 1m --device_list 1.10,1.11 --postcleanup --debug --test_name video_streaming_test

    Example-7:
    Command Line Interface to run the Video Streaming test with incremental Capacity
    python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
    --media_quality 1080P --duration 1m --device_list 1.10,1.11 --incremental_capacity 1,2 --debug --test_name video_streaming_test



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
import pandas as pd
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
port_utils = importlib.import_module("py-json.port_utils")
PortUtils = port_utils.PortUtils


class VideoStreamingTest(Realm):
    def __init__(self, host, ssid, passwd, encryp, media_source, media_quality, suporrted_release=None, max_speed=None, url=None,
                 urls_per_tenm=None, duration=None, resource_ids=None, dowebgui=False, result_dir="", test_name=None, incremental=None, postcleanup=False, precleanup=False):
        super().__init__(lfclient_host=host, lfclient_port=8080)
        self.adb_device_list = None
        self.host = host
        self.phn_name = []
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        self.media_source = media_source
        self.media_quality = media_quality
        self.supported_release = suporrted_release
        self.device_name = []
        self.android_devices = []
        self.other_os_list = []
        self.android_list = []
        self.other_list = []
        self.real_sta_data_dict = {}
        self.ip_map = {}
        self.max_speed = 0  # infinity
        self.quiesce_after = 0  # infinity
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
        self.postCleanUp = postcleanup
        self.preCleanUp = precleanup
        self.devices = base_RealDevice(manager_ip=self.host, selected_bands=[])
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=8080)
        self.port_util = PortUtils(self.local_realm)
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
        self.background_run = None
        self.stop_test = False

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
            logging.info("Device State : {dev_state}".format(dev_state=dev_state))

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
                    logging.info("health :: {health}".format(health=health))
                    logging.info("Launching Interop UI")

                    self.interop.launch_interop_ui(device=i)
        self.health = health
        logging.info("Health:: ", health)

        self.phone_data = self.get_resource_data()
        logging.info("Phone List : ", self.phone_data)
        logging.info("Phone List : {phone_data}".format(phone_data=self.phone_data))

        time.sleep(5)

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

        self.direction = 'dl'
        self.dest = '/dev/null'
        self.max_speed = self.max_speed
        self.requests_per_ten = self.urls_per_tenm
        upload_name = self.phone_data[-1].split('.')[-1]
        self.created_cx = self.http_profile.created_cx = self.convert_to_dict(self.phone_data)
        if self.preCleanUp:
            self.precleanup()
        logging.info("Creating Layer-4 endpoints from the user inputs as test parameters")
        time.sleep(5)
        self.http_profile.created_cx.clear()

        if 'https' in self.url:
            self.url = self.url.replace("http://", "").replace("https://", "")
            self.create_real(ports=self.phone_data, sleep_time=.5, upload_name=upload_name,
                             suppress_related_commands_=None, https=True,
                             https_ip=self.url, interop=True, proxy_auth_type=74240, media_source=self.media_source, media_quality=self.media_quality, timeout=1000)
        elif 'http' in self.url:
            self.url = self.url.replace("http://", "").replace("https://", "")
            self.create_real(ports=self.phone_data, sleep_time=.5, upload_name=upload_name,
                             suppress_related_commands_=None, http=True,
                             http_ip=self.url, interop=True, proxy_auth_type=74240, media_source=self.media_source, media_quality=self.media_quality, timeout=1000)

        else:
            self.create_real(ports=self.phone_data, sleep_time=.5, upload_name=upload_name,
                             suppress_related_commands_=None, http=True,
                             http_ip=self.url, interop=True, proxy_auth_type=74240, media_source=self.media_source, media_quality=self.media_quality, timeout=1000)
        time.sleep(5)

    def start(self):
        logging.info("Setting Cx State to Runnning")
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            logger.info(f"Exception Occured {e}")

    def start_specific(self, cx_start_list):
        logging.info("Setting Cx State to Runnning")
        for cx_name in cx_start_list:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.http_profile.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
        logging.info("Setting Cx State to Runnning")
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            logger.info(f"Exception occured: {e}")
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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
                        # proxy auth flag 0x200 for BIND DNS check
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
                        # proxy auth flag 0x200 for BIND DNS check
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
                # print("http_profile - endp_data:{endp_data}".format(endp_data=endp_data))
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
                # print("http_profile - endp_data:{endp_data}".format(endp_data=endp_data))
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

    def my_monitor_runtime(self):
        try:

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
            data = self.local_realm.json_get(
                "layer4/{}/list?fields={}".format(
                    ','.join(self.created_cx.keys()),
                    "name,status,total-urls,urls/s,total-err,video-format-bitrate,"
                    "bytes-rd,total-wait-time,total-buffers,total-err,rx rate,frame-rate,video-quality"
                )
            )
            names = []
            statuses = []
            total_urls = []
            urls_per_sec = []
            total_err = []
            video_format_bitrate = []
            bytes_rd = []
            total_wait_time = []
            total_buffer = []
            rx_rate = []
            frame_rate = []
            video_quality = []

            if len(self.created_cx.keys()) > 1:
                data = data['endpoint']
                for endpoint in data:
                    for key, value in endpoint.items():
                        names.append(value['name'])
                        statuses.append(value['status'])
                        total_urls.append(value['total-urls'])
                        urls_per_sec.append(value['urls/s'])
                        total_err.append(value['total-err'])
                        video_format_bitrate.append(value['video-format-bitrate'])
                        bytes_rd.append(value['bytes-rd'])
                        total_wait_time.append(value['total-wait-time'])
                        total_buffer.append(value['total-buffers'])
                        rx_rate.append(value['rx rate'])
                        frame_rate.append(value['frame-rate'])
                        video_quality.append(value['video-quality'])
            elif len(self.created_cx.keys()) == 1:
                endpoint = data.get('endpoint', {})
                names = [endpoint.get('name', '')]
                statuses = [endpoint.get('status', '')]
                total_urls = [endpoint.get('total-urls', 0)]
                urls_per_sec = [endpoint.get('urls/s', 0.0)]
                total_err = [endpoint.get('total-err', 0)]
                video_format_bitrate = [endpoint.get('video-format-bitrate', 0)]
                bytes_rd.append(endpoint.get('bytes-rd', 0))
                total_wait_time.append(endpoint.get('total-wait-time', 0))
                total_buffer.append(endpoint.get('total-buffers', 0))
                rx_rate.append(endpoint.get('rx rate', 0))
                frame_rate.append(endpoint.get('frame-rate', 0))
                video_quality.append(endpoint.get('video-quality', 0))

            self.data['status'] = statuses
            self.data["total_urls"] = total_urls
            self.data["urls_per_sec"] = urls_per_sec
            self.data["name"] = names
            self.data["total_err"] = total_err
            self.data["video_format_bitrate"] = video_format_bitrate
            self.data["bytes_rd"] = bytes_rd
            self.data["total_wait_time"] = total_wait_time
            self.data["total_buffer"] = total_buffer
            self.data["rx_rate"] = rx_rate
            self.data['frame_rate'] = frame_rate
            self.data['video_quality'] = video_quality
        except Exception as e:
            logger.error(f"Error in my_monitor_runtime function: {e}", exc_info=True)
            logger.info(f"Layer 4 cx data {data}")

    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        data1 = []

        if "endpoint" not in data.keys():
            logger.error("error in my_monitor function")
            logger.error("Error: 'endpoint' key not found in port data")
            logger.info(f"layer4 cx data {data}")
            exit(1)
        data = data['endpoint']

        if len(self.http_profile.created_cx.keys()) == 1:
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

        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,phantom")
        if "interfaces" not in eid_data.keys():
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)
        resource_ids = []
        if self.resource_ids:
            resource_ids = list(map(int, self.resource_ids.split(',')))
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and not alias[i]["phantom"]:
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
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:

                        if "dBm" in alias[i]['signal']:
                            rssi.append(alias[i]['signal'].split(" ")[0])
                        else:
                            rssi.append(alias[i]['signal'])

                        tx_rate.append(alias[i]['tx-rate'])
                        rx_rate.append(alias[i]['rx-rate'])

        rssi = [0 if i.strip() == "" else int(i) for i in rssi]
        return rssi, tx_rate

    def monitor_for_runtime_csv(self, duration, file_path, individual_df, iteration, actual_start_time, resource_list_sorted=[], cx_list=[]):
        try:

            self.all_cx_list.extend(cx_list)
            test_stopped_by_user = False
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
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            device_type.append('Android')
                            username.append(resource_hw_data['resource']['user'])
                            ssid.append(alias[i]['ssid'])
                            mac.append(alias[i]['mac'])
                            mode.append(alias[i]['mode'])
                            rssi.append(alias[i]['signal'])
                            channel.append(alias[i]['channel'])
                            tx_rate.append(alias[i]['tx-rate'])
                            rx_rate.append(alias[i]['rx-rate'])

            incremental_capacity_list = self.get_incremental_capacity_list()
            video_rate_dict = {i: [] for i in range(len(device_type))}

            # Loop until the current time is less than the end time
            while current_time < endtime_check or self.background_run:

                # Get signal data for RSSI and link speed
                rssi_data, link_speed_data = self.get_signal_data()

                individual_df_data = []

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
                present_time = datetime.now().strftime("%H:%M:%S")
                self.my_monitor_runtime()

                overall_video_rate = []
                # Iterate through the total wait time data
                for i in range(len(self.data["total_wait_time"])):
                    # If the status is 'Stopped', append 0 to the video rate dictionary and overall video rate
                    if self.data['status'][i] != 'Run':

                        video_rate_dict[i].append(0)
                        overall_video_rate.append(0)
                        min_value_video_rate = self.process_list(video_rate_dict[i])
                        individual_df_data.extend([0, 0, self.data["total_urls"][i], rssi_data[i], link_speed_data[i], self.data["total_buffer"][i], self.data["total_err"][i],
                                                   min_value_video_rate, max(video_rate_dict[i]), sum(video_rate_dict[i]) / len(video_rate_dict[i]), self.data["bytes_rd"][i],
                                                   self.data["rx_rate"][i], self.data['frame_rate'][i], self.data['video_quality'][i]])

                    # If the status is not 'Stopped', append the calculated video rate to the video rate dictionary and overall video rate
                    else:

                        video_rate_dict[i].append(round(self.data["video_format_bitrate"][i] / 1000000, 2))
                        overall_video_rate.append(round(self.data["video_format_bitrate"][i] / 1000000, 2))
                        min_value_video_rate = self.process_list(video_rate_dict[i])
                        individual_df_data.extend([round(self.data["video_format_bitrate"][i] / 1000000,
                                                         2),
                                                   round(self.data["total_wait_time"][i] / 1000,
                                                         2),
                                                   self.data["total_urls"][i],
                                                   int(rssi_data[i]),
                                                   link_speed_data[i],
                                                   self.data["total_buffer"][i],
                                                   self.data["total_err"][i],
                                                   min_value_video_rate,
                                                   max(video_rate_dict[i]),
                                                   sum(video_rate_dict[i]) / len(video_rate_dict[i]),
                                                   self.data["bytes_rd"][i],
                                                   self.data["rx_rate"][i],
                                                   self.data['frame_rate'][i],
                                                   self.data['video_quality'][i]])

                individual_df_data.extend([sum(overall_video_rate), present_time, iteration + 1, actual_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                          self.data['end_time_webGUI'][0], self.data['remaining_time_webGUI'][0], "Running"])
                individual_df.loc[len(individual_df)] = individual_df_data
                individual_df.to_csv('video_streaming_realtime_data.csv', index=False)

                if self.dowebgui:
                    with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                     self.test_name), 'r') as file:
                        data = json.load(file)
                        if data["status"] != "Running":
                            logging.info('Test is stopped by the user')
                            test_stopped_by_user = True
                            break

                if self.dowebgui:
                    individual_df.to_csv('{}/video_streaming_realtime_data.csv'.format(self.result_dir), index=False)
                else:
                    individual_df.to_csv(file_path, mode='w', index=False)

                time.sleep(1)

                current_time = datetime.now()
                if self.stop_test:
                    test_stopped_by_user = True
                    break
                if not self.background_run and self.background_run is not None:
                    break
            present_time = datetime.now().strftime("%H:%M:%S")
            individual_df_data = []
            overall_video_rate = []

            # Collecting data when test is stopped
            for i in range(len(self.data["total_wait_time"])):
                if self.data['status'][i] != 'Run':
                    video_rate_dict[i].append(0)
                    overall_video_rate.append(0)
                    min_value_video_rate = self.process_list(video_rate_dict[i])
                    individual_df_data.extend([0, 0, self.data["total_urls"][i], rssi_data[i], link_speed_data[i], self.data["total_buffer"][i], self.data["total_err"][i], min_value_video_rate,
                                               max(video_rate_dict[i]), sum(video_rate_dict[i]) / len(video_rate_dict[i]), self.data["bytes_rd"][i], self.data["rx_rate"][i],
                                               self.data['frame_rate'][i], self.data['video_quality'][i]])
                else:
                    overall_video_rate.append(round(self.data["video_format_bitrate"][i] / 1000000, 2))
                    video_rate_dict[i].append(round(self.data["video_format_bitrate"][i] / 1000000, 2))
                    min_value_video_rate = self.process_list(video_rate_dict[i])
                    individual_df_data.extend([round(self.data["video_format_bitrate"][i] / 1000000,
                                                     2),
                                               round(self.data["total_wait_time"][i] / 1000,
                                                     2),
                                               self.data["total_urls"][i],
                                               int(rssi_data[i]),
                                               link_speed_data[i],
                                               self.data["total_buffer"][i],
                                               self.data["total_err"][i],
                                               min_value_video_rate,
                                               max(video_rate_dict[i]),
                                               sum(video_rate_dict[i]) / len(video_rate_dict[i]),
                                               self.data["bytes_rd"][i],
                                               self.data["rx_rate"][i],
                                               self.data['frame_rate'][i],
                                               self.data['video_quality'][i]])

            if iteration + 1 == len(incremental_capacity_list):
                individual_df_data.extend([sum(overall_video_rate), present_time, iteration + 1, actual_start_time.strftime('%Y-%m-%d %H:%M:%S'), self.data['end_time_webGUI'][0], 0, "Stopped"])
            else:
                individual_df_data.extend([sum(overall_video_rate), present_time, iteration + 1, actual_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                          self.data['end_time_webGUI'][0], self.data['remaining_time_webGUI'][0], "Stopped"])
            individual_df.loc[len(individual_df)] = individual_df_data

            if self.dowebgui:
                individual_df.to_csv('{}/video_streaming_realtime_data.csv'.format(self.result_dir), index=False)
            else:
                individual_df.to_csv('video_streaming_realtime_data.csv', index=False)

            if self.data['end_time_webGUI'][0] < current_time.strftime('%Y-%m-%d %H:%M:%S'):
                self.data['end_time_webGUI'] = [current_time.strftime('%Y-%m-%d %H:%M:%S')]

            curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            curr_time_dt = datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
            endtime_dt = datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S")

            remaining_time_dt = endtime_dt - curr_time_dt
            one_minute = timedelta(minutes=1)

            if remaining_time_dt < one_minute:
                self.data['remaining_time_webGUI'] = ["< 1 min"]
            else:
                self.data['remaining_time_webGUI'] = [str(datetime.strptime(self.data['end_time_webGUI'][0], "%Y-%m-%d %H:%M:%S") - datetime.strptime(curr_time, "%Y-%m-%d %H:%M:%S"))]

            return test_stopped_by_user
        except Exception as e:
            logger.error(f"Error in monitor_for_runtime_csv function: {e}", exc_info=True)
            logger.info(f"eid_data {eid_data}")
            return test_stopped_by_user

    def get_incremental_capacity_list(self):
        keys = list(self.http_profile.created_cx.keys())
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

    def trim_data(self, array_size, to_updated_array):
        if array_size < 6:
            updated_array = to_updated_array
        else:
            middle_elements_count = 4
            step = (array_size - 1) / (middle_elements_count + 1)
            middle_elements = [int(i * step) for i in range(1, middle_elements_count + 1)]
            new_array = [0] + middle_elements + [array_size - 1]
            updated_array = [to_updated_array[index] for index in new_array]
        return updated_array

    def process_list(self, lst):
        # This function filters out initial zero values in the test video rate.
        # Before the video starts running, the rate is temporarily zero,
        # which should not be considered in the final analysis in order to get the min and max video rate
        # This ensures only valid video rate data is processed.

        if all(item == 0 for item in lst):
            return 0
        else:
            non_zero_values = [item for item in lst if item != 0]
            return min(non_zero_values)

    def generate_report(self, date, iterations_before_test_stopped_by_user, test_setup_info, realtime_dataset, report_path='', cx_order_list=[]):
        logging.info("Creating Reports")
        # Initialize the report object
        if self.dowebgui and report_path == '':

            report = lf_report.lf_report(_results_dir_name="VideoStreaming_test", _output_html="VideoStreaming_test.html",
                                         _output_pdf="VideoStreaming_test.pdf", _path=self.result_dir)
        else:
            report = lf_report.lf_report(_results_dir_name="VideoStreaming_test", _output_html="VideoStreaming_test.html",
                                         _output_pdf="VideoStreaming_test.pdf", _path=report_path)

        # To store throughput_data.csv in report folder
        report_path_date_time = report.get_path_date_time()
        shutil.move('video_streaming_realtime_data.csv', report_path_date_time)

        # Getting incremental capacity in lists
        created_incremental_values = self.get_incremental_capacity_list()
        keys = list(self.http_profile.created_cx.keys())

        # Set report title, date, and build banner
        report.set_title("Video Streaming Test")
        report.set_date(date)
        report.build_banner()
        report.set_obj_html("Objective", " The Candela Video streaming test is designed to measure the access point performance and stability by streaming the videos from the local browser"
                            "or from over the Internet in real clients like android which are connected to the access point,"
                            "this test allows the user to choose the options like video link, type of media source, media quality, number of playbacks."
                            "Along with the performance other measurements like No of Buffers, Wait-Time, per client Video Bitrate, Video Quality, and more. "
                            "The expected behavior is for the DUT to be able to handle several stations (within the limitations of the AP specs)"
                            "and make sure all capable clients can browse the video. ")
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
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':

                    # Get resource data for specific interface
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    hw_version = resource_hw_data['resource']['hw version']

                    # Filter based on OS and resource ID
                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                        device_type.append('Android')
                        username.append(resource_hw_data['resource']['user'])
                        ssid.append(alias[i]['ssid'])
                        mac.append(alias[i]['mac'])
                        mode.append(alias[i]['mode'])
                        rssi.append(alias[i]['signal'])
                        channel.append(alias[i]['channel'])
                        tx_rate.append(alias[i]['tx-rate'])
        total_urls = self.data["total_urls"]
        total_err = self.data["total_err"]
        total_buffer = self.data["total_buffer"]
        max_bytes_rd_list = []
        avg_rx_rate_list = []
        # Iterate through the length of cx_order_list
        for iter in range(len(iterations_before_test_stopped_by_user)):
            data_set_in_graph, wait_time_data, devices_on_running_state, device_names_on_running = [], [], [], []
            devices_data_to_create_wait_time_bar_graph = []
            max_video_rate, min_video_rate, avg_video_rate = [], [], []
            total_url_data, rssi_data = [], []
            trimmed_data_set_in_graph = []
            max_bytes_rd_list = []
            avg_rx_rate_list = []
            # Retrieve data for the previous iteration, if it's not the first iteration
            if iter != 0:
                before_data_iter = realtime_dataset[realtime_dataset['iteration'] == iter]
            # Retrieve data for the current iteration
            data_iter = realtime_dataset[realtime_dataset['iteration'] == iter + 1]

            # Populate the list of devices on running state and their corresponding usernames
            for j in range(created_incremental_values[iter]):
                devices_on_running_state.append(keys[j])
                device_names_on_running.append(username[j])

            # Iterate through each device currently running
            for k in devices_on_running_state:
                # Filter columns related to the current device
                columns_with_substring = [col for col in data_iter.columns if k in col]
                filtered_df = data_iter[columns_with_substring]
                min_val = self.process_list(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist())
                if iter != 0:
                    # Filter columns related to the current device from the previous iteration
                    before_iter_columns_with_substring = [col for col in before_data_iter.columns if k in col]
                    before_filtered_df = before_data_iter[before_iter_columns_with_substring]

                # Extract and compute max, min, and average video rates
                max_video_rate.append(max(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()))
                min_video_rate.append(min_val)
                avg_video_rate.append(round(sum(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()) /
                                      len(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()), 2))
                wait_time_data.append(filtered_df[[col for col in filtered_df.columns if "total_wait_time" in col][0]].values.tolist()[-1])
                rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                 len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                # Extract maximum bytes read for the device
                max_bytes_rd = max(filtered_df[[col for col in filtered_df.columns if "bytes_rd" in col][0]].values.tolist())
                max_bytes_rd_list.append(max_bytes_rd)

                # Calculate and append the average RX rate in Mbps
                rx_rate_values = filtered_df[[col for col in filtered_df.columns if "rx rate" in col][0]].values.tolist()
                avg_rx_rate_list.append(round((sum(rx_rate_values) / len(rx_rate_values)) / 1_000_000, 2))  # Convert bps to Mbps

                if iter != 0:
                    # Calculate the difference in total URLs between the current and previous iterations
                    total_url_data.append(abs(filtered_df[[col for col in filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1] -
                                          before_filtered_df[[col for col in before_filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1]))
                else:
                    # Append the total URLs for the first iteration
                    total_url_data.append(filtered_df[[col for col in filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1])

            # Append the wait time data to the list for creating the wait time bar graph
            devices_data_to_create_wait_time_bar_graph.append(wait_time_data)

            # Extract overall video format bitrate values for the current iteration and append to data_set_in_graph
            video_streaming_values_list = realtime_dataset['overall_video_format_bitrate'][realtime_dataset['iteration'] == iter + 1].values.tolist()
            data_set_in_graph.append(video_streaming_values_list)

            # Trim the data in data_set_in_graph and append to trimmed_data_set_in_graph
            for _ in range(len(data_set_in_graph)):
                trimmed_data_set_in_graph.append(self.trim_data(len(data_set_in_graph[_]), data_set_in_graph[_]))

            # If there are multiple incremental values, add custom HTML content to the report for the current iteration
            if len(created_incremental_values) > 1:
                report.set_custom_html(f"<h2><u>Iteration-{iter + 1}</u></h2>")
                report.build_custom()

            report.set_obj_html(
                _obj_title=f"Realtime Video Rate: Number of devices running: {len(device_names_on_running)}",
                _obj="")
            report.build_objective()

            # Create a line graph for video rate over time
            graph = lf_line_graph(_data_set=trimmed_data_set_in_graph,
                                  _xaxis_name="Time",
                                  _yaxis_name="Video Rate (Mbps)",
                                  _xaxis_categories=self.trim_data(len(realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
                                                                   realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
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
            graph = lf_bar_graph_horizontal(_data_set=[total_urls[:created_incremental_values[iter]]],
                                            _xaxis_name="Total Urls",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"total_urls_image_name{iter}",
                                            _label=["Total Urls"],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
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
            graph = lf_bar_graph_horizontal(_data_set=[max_video_rate, min_video_rate],
                                            _xaxis_name="Max/Min Video Rate(Mbps)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"max-min-video-rate_image_name{iter}",
                                            _label=['Max Video Rate', 'Min Video Rate'],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
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
            graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_wait_time_bar_graph,
                                            _xaxis_name="Wait Time(seconds)",
                                            _yaxis_name="Devices",
                                            _graph_image_name=f"wait_time_image_name{iter}",
                                            _label=['Wait Time'],
                                            _yaxis_categories=device_names_on_running,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _show_bar_value=True,
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
                " DEVICE TYPE ": device_type[:created_incremental_values[iter]],
                " Username ": username[:created_incremental_values[iter]],
                " SSID ": ssid[:created_incremental_values[iter]],
                " MAC ": mac[:created_incremental_values[iter]],
                " Channel ": channel[:created_incremental_values[iter]],
                " Mode ": mode[:created_incremental_values[iter]],
                " Buffers": total_buffer[:created_incremental_values[iter]],
                " Wait-Time(Sec)": wait_time_data,
                " Min Video Rate(Mbps) ": min_video_rate[:created_incremental_values[iter]],
                " Avg Video Rate(Mbps) ": avg_video_rate[:created_incremental_values[iter]],
                " Max Video Rate(Mbps) ": max_video_rate[:created_incremental_values[iter]],
                " Total URLs ": total_urls[:created_incremental_values[iter]],
                " Total Errors ": total_err[:created_incremental_values[iter]],
                " RSSI (dbm)": ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[:created_incremental_values[iter]]],
                " Link Speed ": tx_rate[:created_incremental_values[iter]],
                "Bytes Read (bytes)": max_bytes_rd_list,  # Added here
                'Average Rx Rate (Mbps)': avg_rx_rate_list
            }
            dataframe1 = pd.DataFrame(dataframe)
            report.set_table_dataframe(dataframe1)
            report.build_table()

            # Set and build title for the overall results table
            report.set_obj_html("Detailed Total Errors Table", "The below tables provides detailed information of total errors for the web browsing test.")
            report.build_objective()
            dataframe2 = {
                " DEVICE": username[:created_incremental_values[iter]],
                " TOTAL ERRORS ": total_err[:created_incremental_values[iter]],
            }
            dataframe3 = pd.DataFrame(dataframe2)
            report.set_table_dataframe(dataframe3)
            report.build_table()
        report.build_footer()
        report.write_html()
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


def main():
    help_summary = '''\
    The Candela Video streaming test is designed to measure the access point performance and stability by streaming the videos from the local browser"
    "or from over the Internet in real clients like android which are connected to the access point,
    this test allows the user to choose the options like video link, type of media source, media quality, number of playbacks.
    Along with the performance other measurements like No of Buffers, Wait-Time, per client Video Bitrate, Video Quality, and more.
    The expected behavior is for the DUT to be able to handle several stations (within the limitations of the AP specs)"
    "and make sure all capable clients can browse the video.
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
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test

        Example-2:
        Command Line Interface to run Video Streaming test with media source DASH and media quality 4K :
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd" --media_source dash
        --media_quality 4K --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test

        Example-3:
        Command Line Interface to run the Video Streaming test with specified Resources:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P --duration 1m --device_list 1.10,1.12 --debug --test_name video_streaming_test


        Example-4:
        Command Line Interface to run the Video Streaming test with incremental Capacity by specifying the --incremental flag
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P --duration 1m --device_list 1.10,1.12 --incremental --debug --test_name video_streaming_test

        Example-5:
        Command Line Interface to run Video Streaming test with precleanup:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P  --duration 1m --device_list 1.10,1.12 --precleanup --debug --test_name video_streaming_test

        Example-6:
        Command Line Interface to run Video Streaming test with postcleanup:
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P --duration 1m --device_list 1.10,1.12 --postcleanup --debug --test_name video_streaming_test

        Example-7:
        Command Line Interface to run the Video Streaming test with incremental Capacity
        python3 lf_interop_video_streaming.py --mgr 192.168.214.219 --url "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8" --media_source hls
        --media_quality 1080P --duration 1m --device_list 1.10,1.11 --incremental_capacity 1,2 --debug --test_name video_streaming_test

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

    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port '
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
    parser.add_argument('--test_name',  help='Name of the Test')
    parser.add_argument('--dowebgui', help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--result_dir', help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')
    parser.add_argument("--lf_logger_config_json", help="[log configuration] --lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument("--log_level", help="[log configuration] --log_level  debug info warning error critical")
    parser.add_argument("--debug", help="[log configuration] --debug store_true , used by lanforge client ", action='store_true')
    parser.add_argument("--media_source", type=str, default='1')
    parser.add_argument("--media_quality", type=str, default='0')

    parser.add_argument('--device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
    parser.add_argument('--webgui_incremental', '--incremental_capacity', help="Specify the incremental values <1,2,3..>", type=str, dest="webgui_incremental")
    parser.add_argument('--incremental', help="--incremental to add incremental values", action='store_true')
    parser.add_argument('--no_laptops', help="--to not use laptops", action='store_false')
    parser.add_argument('--postcleanup', help="Cleanup the cross connections after test is stopped", action='store_true')
    parser.add_argument('--precleanup', help="Cleanup the cross connections before test is started", action='store_true')
    parser.add_argument('--help_summary', help='Show summary of what this script does', action='store_true')
    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    if args.host is None:
        print("--host/--mgr required")
        exit(1)

    if args.test_name is None:
        print("--test_name required")
        exit(1)

    media_source_dict = {
        'dash': '1',
        'smooth_streaming': '2',
        'hls': '3',
        'progressive': '4',
        'rtsp': '5'
    }
    media_quality_dict = {
        '4k': '0',
        '8k': '1',
        '1080p': '2',
        '720p': '3',
        '360p': '4'
    }

    media_source, media_quality = args.media_source.capitalize(), args.media_quality
    args.media_source = args.media_source.lower()
    args.media_quality = args.media_quality.lower()

    if any(char.isalpha() for char in args.media_source):
        args.media_source = media_source_dict[args.media_source]

    if any(char.isalpha() for char in args.media_quality):
        args.media_quality = media_quality_dict[args.media_quality]

    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    logger = logging.getLogger(__name__)

    obj = VideoStreamingTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                             suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                             url=args.url, urls_per_tenm=args.urls_per_tenm, duration=args.duration,
                             resource_ids=args.device_list, dowebgui=args.dowebgui, media_quality=args.media_quality, media_source=args.media_source,
                             result_dir=args.result_dir, test_name=args.test_name, incremental=args.incremental, postcleanup=args.postcleanup,
                             precleanup=args.precleanup)

    resource_ids_sm = []
    resource_set = set()
    resource_list = []
    resource_ids_generated = ""

    if args.dowebgui:
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
        selected_devices, report_labels, selected_macs = obj.devices.query_user(dowebgui=args.dowebgui, device_list=resource_ids_generated)
        # Modify obj.resource_ids to include only the second part of each ID (after '.')
        obj.resource_ids = ",".join(id.split(".")[1] for id in args.device_list.split(","))
        available_resources = [int(num) for num in obj.resource_ids.split(',')]
    else:
        # Case where args.no_laptops flag is set
        # if args.no_laptops:
        # Retrieve all Android devices if no_laptops flag is True
        obj.android_devices = obj.devices.get_devices(only_androids=True)

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
            available_resources = list(set(resource_ids))

        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices, report_labels, selected_macs = obj.devices.query_user()
            # Handle cases where no devices are selected

            if not selected_devices:
                logging.info("devices donot exist..!!")
                return

            obj.android_list = selected_devices

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
                available_resources = list(resource_set)
    if len(available_resources) == 0:
        logger.info("No devices which are selected are available in the lanforge")
        exit()
    gave_incremental = False
    if len(resource_list_sorted) == 0:
        logger.error("Selected Devices are not available in the lanforge")
        exit(1)
    if args.incremental and not args.webgui_incremental:
        if obj.resource_ids:
            logging.info("The total available devices are {}".format(len(available_resources)))
            obj.incremental = input('Specify incremental values as 1,2,3 : ')
            obj.incremental = [int(x) for x in obj.incremental.split(',')]
        else:
            logging.info("incremental Values are not needed as Android devices are not selected..")
    elif not args.incremental:
        gave_incremental = True
        obj.incremental = [len(available_resources)]

    if args.webgui_incremental:
        incremental = [int(x) for x in args.webgui_incremental.split(',')]
        if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
            obj.incremental = incremental

    if obj.incremental and obj.resource_ids:
        if obj.incremental[-1] > len(available_resources):
            logging.info("Exiting the program as incremental values are greater than the resource ids provided")
            exit()
        elif obj.incremental[-1] < len(available_resources) and len(obj.incremental) > 1:
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

    individual_dataframe_columns = []

    keys = list(obj.http_profile.created_cx.keys())

    # Extend individual_dataframe_column with dynamically generated column names
    for i in range(len(keys)):
        individual_dataframe_columns.extend([
            f'video_format_bitrate_{keys[i]}',
            f'total_wait_time_{keys[i]}',
            f'total_urls_{keys[i]}',
            f'RSSI_{keys[i]}',
            f'Link Speed_{keys[i]}',
            f'Total Buffer_{keys[i]}',
            f'Total Errors_{keys[i]}',
            f'Min_Video_Rate_{keys[i]}',
            f'Max_Video_Rate_{keys[i]}',
            f'Avg_Video_Rate_{keys[i]}',
            f'bytes_rd_{keys[i]}',
            f'rx rate_{keys[i]} bps',
            f'frame_rate_{keys[i]}',
            f'Video Quality_{keys[i]}'
        ])

    individual_dataframe_columns.extend(['overall_video_format_bitrate', 'timestamp', 'iteration', 'start_time', 'end_time', 'remaining_Time', 'status'])
    individual_df = pd.DataFrame(columns=individual_dataframe_columns)

    cx_order_list = []
    index = 0
    file_path = ""

    # Parsing test_duration
    if args.duration.endswith('s') or args.duration.endswith('S'):
        args.duration = round(int(args.duration[0:-1]) / 60, 2)

    elif args.duration.endswith('m') or args.duration.endswith('M'):
        args.duration = int(args.duration[0:-1])

    elif args.duration.endswith('h') or args.duration.endswith('H'):
        args.duration = int(args.duration[0:-1]) * 60

    elif args.duration.endswith(''):
        args.duration = int(args.duration)

    incremental_capacity_list_values = obj.get_incremental_capacity_list()
    if incremental_capacity_list_values[-1] != len(available_resources):
        logger.error("Incremental capacity doesnt match available devices")
        if args.postcleanup:
            obj.postcleanup()
        exit(1)
    # Process resource IDs and incremental values if specified
    if obj.resource_ids:
        if obj.incremental:
            test_setup_info_incremental_values = ','.join([str(n) for n in incremental_capacity_list_values])
            if len(obj.incremental) == len(available_resources):
                test_setup_info_total_duration = args.duration
            elif len(obj.incremental) == 1 and len(available_resources) > 1:
                if obj.incremental[0] == len(available_resources):
                    test_setup_info_total_duration = args.duration
                else:
                    div = len(available_resources) // obj.incremental[0]
                    mod = len(available_resources) % obj.incremental[0]
                    if mod == 0:
                        test_setup_info_total_duration = args.duration * (div)
                    else:
                        test_setup_info_total_duration = args.duration * (div + 1)
            else:
                test_setup_info_total_duration = args.duration * len(incremental_capacity_list_values)
        else:
            test_setup_info_total_duration = args.duration

        if args.webgui_incremental:
            test_setup_info_incremental_values = ','.join([str(n) for n in incremental_capacity_list_values])
        elif gave_incremental:
            test_setup_info_incremental_values = "No Incremental Value provided"
        obj.total_duration = test_setup_info_total_duration

    actual_start_time = datetime.now()

    iterations_before_test_stopped_by_user = []

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

            # Iterate over cx_order_list to start tests incrementally
            for i in range(len(cx_order_list)):
                if i == 0:
                    obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    end_time_webGUI = (datetime.now() + timedelta(minutes=obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['end_time_webGUI'] = [end_time_webGUI]

                # time.sleep(10)

                # Start specific devices based on incremental capacity
                obj.start_specific(cx_order_list[i])
                if cx_order_list[i]:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                else:
                    logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                file_path = "video_streaming_realtime_data.csv"
                if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    obj.data['remaining_time_webGUI'] = ['0:00']
                else:
                    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    obj.data['remaining_time_webGUI'] = [datetime.strptime(end_time_webGUI, "%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")]

                if args.dowebgui:
                    file_path = os.path.join(obj.result_dir, "../../Running_instances/{}_{}_running.json".format(obj.host, obj.test_name))
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            if data["status"] != "Running":
                                break
                    test_stopped_by_user = obj.monitor_for_runtime_csv(args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                else:
                    test_stopped_by_user = obj.monitor_for_runtime_csv(args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                if not test_stopped_by_user:
                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                else:
                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                    break
    obj.stop()

    if obj.resource_ids:

        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
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
                        username.append(resource_hw_data['resource']['user'])

        device_list_str = ','.join([f"{name} ( Android )" for name in username])

        test_setup_info = {
            "Testname": args.test_name,
            "Device List": device_list_str,
            "No of Devices": "Total" + "( " + str(len(keys)) + " ): Android(" + str(len(keys)) + ")",
            "Incremental Values": "",
            "URL": args.url,
            "Media Source": media_source.upper(),
            "Media Quality": media_quality
        }
        test_setup_info['Incremental Values'] = test_setup_info_incremental_values
        test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration)

    logging.info("Test Completed")

    # prev_inc_value = 0
    if obj.resource_ids and obj.incremental:
        obj.generate_report(date, list(set(iterations_before_test_stopped_by_user)), test_setup_info=test_setup_info, realtime_dataset=individual_df, cx_order_list=cx_order_list)
    elif obj.resource_ids:
        obj.generate_report(date, list(set(iterations_before_test_stopped_by_user)), test_setup_info=test_setup_info, realtime_dataset=individual_df)

    # Perform post-cleanup operations
    if args.postcleanup:
        obj.postcleanup()

    if args.dowebgui:
        obj.copy_reports_to_home_dir()


if __name__ == '__main__':
    main()
