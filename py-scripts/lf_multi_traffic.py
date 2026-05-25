#!/usr/bin/env python3
"""
    NAME: lf_multi_traffic.py

    PURPOSE:
    lf_multi_traffic.py is used to execute multiple network and real-application tests
    either in series, parallel, or hybrid mode.

    The script supports running tests sequentially (series), simultaneously (parallel),
    or a combination of both, with configurable execution priority.

    SUPPORTED TESTS:

    Tests supported for series execution:
        ping_test
        qos_test
        ftp_test
        http_test
        mcast_test
        vs_test
        thput_test
        rb_test
        teams_test
        yt_test
        zoom_test

    Tests supported for parallel execution:
        ping_test
        qos_test
        ftp_test
        http_test
        mcast_test
        vs_test
        thput_test

    Real Application Tests (Only Series Supported):
        yt_test        (YouTube)
        rb_test        (Real Browser)
        teams_test     (Microsoft Teams)
        zoom_test      (Zoom Call)


    EXECUTION RULES:

    1. SERIES TESTS:
    - Runs tests one after another
    - Maintains execution order
    - Allows duplicate tests

    2. PARALLEL TESTS:
    - Runs tests simultaneously
    - Duplicate tests are NOT allowed
    - Real application tests are NOT supported

    3. HYBRID MODE:
    - Both --series_tests and --parallel_tests can be used
    - Execution order controlled by --order_priority


    ARGUMENT:

    --order_priority:
        Defines which test group runs first
        Choices:
            series    -> series tests run first
            parallel  -> parallel tests run first


    EXAMPLE-1:
    Command Line Interface to run all series tests with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000 \
    \
    --rb_duration 1m \
    --rb_device_list 1.15,1.4 \
    --rb_webgui_incremental no_increment \
    --rb_count 10 \
    \
    --yt_url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --yt_duration 1m \
    --yt_res 144p \
    --yt_device_list 1.15,1.4 \
    \
    --zoom_signin_email candelatech2@gmail.com \
    --zoom_signin_passwd 'CANDELAtech1@530048' \
    --zoom_duration 2 \
    --zoom_host 1.15 \
    --zoom_participants 2 \
    --zoom_device_list 1.15,1.4 \
    --zoom_audio \
    --zoom_video \
    \
    --teams_duration 2m \
    --teams_device_list 1.15,1.4 \
    --teams_audio \
    --teams_video

    EXAMPLE-2:
    Command Line Interface to run all parallel tests with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --parallel_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000

    EXAMPLE-3:
    Command Line Interface to run all series tests and parallel with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    --parallel_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000 \
    \
    --rb_duration 1m \
    --rb_device_list 1.15,1.4 \
    --rb_webgui_incremental no_increment \
    --rb_count 10 \
    \
    --yt_url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --yt_duration 1m \
    --yt_res 144p \
    --yt_device_list 1.15,1.4 \
    \
    --zoom_signin_email candelatech2@gmail.com \
    --zoom_signin_passwd 'CANDELAtech1@530048' \
    --zoom_duration 2 \
    --zoom_host 1.15 \
    --zoom_participants 2 \
    --zoom_device_list 1.15,1.4 \
    --zoom_audio \
    --zoom_video \
    \
    --teams_duration 2m \
    --teams_device_list 1.15,1.4 \
    --teams_audio \
    --teams_video

    EXAMPLE-4:
    Duplicate tests allowed only in series
    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests http_test,ftp_test,http_test

    NOTE : Add traffic related args from EXAMPLE 1


    NOTES:
    1. Duration format: s (seconds), m (minutes), h (hours)
    2. Parallel execution improves performance but is limited to network tests
    3. Real application tests must always be executed in series
    4. Avoid duplicates in parallel_tests
    5. Use --order_priority to control execution flow

    STATUS : Functional

    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES: Performance, Functional, Automation

    VERIFIED_ON:
    Working date - 21/04/2026
    Build version - 5.5.3
    kernel version - 6.18.14+

    LICENSE :
    Copyright (C) 2020-2026 Candela Technologies Inc
    Free to distribute and modify. LANforge systems must be licensed.

    INCLUDE_IN_README: False
"""
import os
import sys


base_path = os.getcwd()

sys.path.insert(0, os.path.join(base_path, 'py-json'))
sys.path.insert(0, os.path.join(base_path, 'py-json', 'LANforge'))
sys.path.insert(0, os.path.join(base_path, 'py-scripts'))


import argparse  # noqa: E402
import asyncio   # noqa: E402
import csv       # noqa: E402
import datetime  # noqa: E402
import glob      # noqa: E402
import importlib  # noqa: E402
import json      # noqa: E402
import logging   # noqa: E402
import multiprocessing  # noqa: E402
import threading  # noqa: E402
import time      # noqa: E402
import traceback  # noqa: E402
import copy     # noqa: E402
from multiprocessing import Event, Lock, Manager, Value  # noqa: E402
from types import SimpleNamespace  # noqa: E402


import matplotlib  # noqa: E402
matplotlib.use('Agg')  # must be before pyplot
import matplotlib.pyplot as plt  # noqa: E402

import pandas as pd  # noqa: E402
import paramiko       # noqa: E402
from dotenv import load_dotenv  # noqa: E402


import lf_cleanup                    # noqa: E402
import lf_interop_qos as qos_test   # noqa: E402
import lf_webpage as http_test       # noqa: E402
from LANforge import LFUtils          # noqa: E402
from lf_base_interop_profile import RealDevice  # noqa: E402

from lf_ftp import FtpTest            # noqa: E402
from lf_graph import lf_bar_graph, lf_bar_graph_horizontal, lf_line_graph  # noqa: E402
from lf_interop_ping import Ping      # noqa: E402
from lf_interop_throughput import Throughput  # noqa: E402
from lf_interop_video_streaming import VideoStreamingTest  # noqa: E402

from test_l3 import (                  # noqa: E402
    L3VariableTime,
    configure_reporting,
    query_real_clients,
    valid_endp_types,
)


lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")

througput_test = importlib.import_module("py-scripts.lf_interop_throughput")
video_streaming_test = importlib.import_module("py-scripts.lf_interop_video_streaming")

web_browser_test = importlib.import_module(
    "py-scripts.real_application_tests.real_browser.lf_interop_real_browser_test"
)
zoom_test = importlib.import_module(
    "py-scripts.real_application_tests.zoom_automation.lf_interop_zoom"
)
yt_test = importlib.import_module(
    "py-scripts.real_application_tests.youtube.lf_interop_youtube"
)
teams_test = importlib.import_module(
    "py-scripts.real_application_tests.teams_automation.lf_interop_teams"
)

DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")
realm = importlib.import_module("py-json.realm")

Realm = realm.Realm
RealBrowserTest = web_browser_test.RealBrowserTest
Youtube = yt_test.Youtube
ZoomAutomation = zoom_test.ZoomAutomation
TeamsAutomation = teams_test.TeamsAutomation


# --- Logger Setup ---
logger = logging.getLogger(__name__)
lf_logger_config.lf_logger_config()


error_logs = ""
test_results_df = pd.DataFrame(columns=['test_name', 'status'])

manager = Manager()
test_results_list = manager.list()


class MultiTraffic(Realm):
    """
    Multi Traffic Class file to invoke different scripts from py-scripts.
    """

    def __init__(self, ip='localhost', port=8080, order_priority="series", result_dir="", dowebgui=False, test_name='', no_cleanup=False,
                 robot_test=False, robot_ip=None, coordinate=None, rotation=None, do_bandsteering=False, bssids=None, cycles=1, duration_to_skip=None):
        super().__init__(lfclient_host=ip,
                         lfclient_port=port)
        self.lanforge_ip = ip
        self.port = port
        self.api_url = 'http://{}:{}'.format(self.lanforge_ip, self.port)
        self.cleanup = lf_cleanup.lf_clean(host=self.lanforge_ip, port=self.port, resource='all')
        self.ftp_test = None
        self.http_test = None
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.iterations_before_test_stopped_by_user = None
        self.incremental_capacity_list = None
        self.all_dataframes = None
        self.to_run_cxs_len = None
        self.date = None
        self.test_setup_info = None
        self.individual_df = None
        self.cx_order_list = None
        self.dataset2 = None
        self.dataset = None
        self.lis = None
        self.bands = None
        self.total_urls = None
        self.uc_min_value = None
        self.cx_order_list = None
        self.gave_incremental = None
        self.result_path = os.getcwd()
        self.test_count_dict = {}
        self.current_exec = "series"
        self.order_priority = order_priority
        self.dowebgui = dowebgui
        self.result_dir = result_dir
        self.test_name = test_name
        self.overall_csv = []
        self.overall_status = {}
        self.obj_dict = {}
        self.test_stopped = False
        self.no_cleanup = no_cleanup
        self.duration_dict = {}
        # Dictionaries to store objects and data for different test types,
        # categorized by parallel or series execution modes.
        self.http_obj_dict = {"parallel": {}, "series": {}}
        self.ftp_obj_dict = {"parallel": {}, "series": {}}
        self.thput_obj_dict = {"parallel": {}, "series": {}}
        self.qos_obj_dict = {"parallel": {}, "series": {}}
        self.ping_obj_dict = {"parallel": {}, "series": {}}
        self.mcast_obj_dict = {"parallel": {}, "series": {}}
        self.rb_obj_dict = {"parallel": {}, "series": {}}
        self.yt_obj_dict = {"parallel": {}, "series": {}}
        self.zoom_obj_dict = {"parallel": {}, "series": {}}
        self.vs_obj_dict = {"parallel": {}, "series": {}}
        self.teams_obj_dict = {"parallel": {}, "series": {}}
        self.parallel_connect = {}
        self.series_connect = {}
        self.parallel_index = 0
        self.series_index = 0
        self.robot_test = robot_test
        self.robot_ip = robot_ip
        self.coordinate = coordinate if coordinate else []
        self.rotation = rotation if rotation else []
        self.do_bandsteering = do_bandsteering
        self.cycles = cycles
        self.duration_to_skip = duration_to_skip
        self.coordinate_list = coordinate.split(',')
        self.rotation_list = rotation.split(',')
        self.bssids = bssids.split(",") if bssids else []
        self.rotation_enabled = True if rotation != '' else False
        # Multi-threading/multiprocessing synchronization events for individual test completions
        self.ftp_done_event = Event()
        self.qos_done_event = Event()
        self.http_done_event = Event()
        self.thput_done_event = Event()
        self.vs_done_event = Event()
        self.ping_done_event = Event()
        self.mcast_done_event = Event()
        self.yt_done_event = Event()
        self.rb_done_event = Event()
        self.zoom_done_event = Event()

        # Synchronization events to trigger robot movement or rotation during tests required for robot scenarios
        self.robot_move_event = Event()
        self.ftp_rotate = Event()
        self.qos_rotate = Event()
        self.http_rotate = Event()
        self.thput_rotate = Event()
        self.vs_rotate = Event()
        self.ping_rotate = Event()
        self.mcast_rotate = Event()
        self.yt_rotate = Event()
        self.rb_rotate = Event()
        self.zoom_rotate = Event()

        # Events indicating a triggered rotation has been completed by the robot
        self.ftp_rotate_done_event = Event()
        self.qos_rotate_done_event = Event()
        self.http_rotate_done_event = Event()
        self.thput_rotate_done_event = Event()
        self.vs_rotate_done_event = Event()
        self.ping_rotate_done_event = Event()
        self.mcast_rotate_done_event = Event()
        self.yt_rotate_done_event = Event()
        self.rb_rotate_done_event = Event()
        self.zoom_rotate_done_event = Event()

        # General state tracking and locking for robot integration and test control
        self.robot_rotate_move_event = Event()
        self.test_stopped_event = Event()
        self.abort_event = Event()
        self.robo_moved = Value('b', False)
        self.robo_rotated = Value('b', False)
        self.robot_lock = Lock()
        self.robot_rotate_call_counter = Value('i', 0)
        self.robot_call_counter = Value('i', 0)

    def webgui_stop_check(self, test_name):
        """
        Checks the running JSON file generated when a test is executed via the web GUI.
        If the user clicks 'Stop' in the GUI, this JSON file's status gets updated.
        This function detects that change and updates the internal test status accordingly.

        Args:
            test_name (str): The name of the test currently being executed.

        Returns:
            bool: False if the test was stopped by the user, True otherwise.
        """
        try:
            with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name), 'r') as file:
                data = json.load(file)
                if data["status"] != "Running":
                    logging.info('Test is stopped by the user')
                    self.test_stopped = True
            if not self.test_stopped:
                self.overall_status[test_name] = "started"
                self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                self.overall_status["current_mode"] = self.current_exec
                self.overall_status["current_test_name"] = test_name
                self.overall_csv.append(self.overall_status.copy())
                df1 = pd.DataFrame(self.overall_csv)
                df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
        except Exception:
            logger.info(f"Error while running for webui during {test_name} execution")
        if self.test_stopped:
            logger.info("test has been stopped by the user")
            return False
        return True

    def webgui_test_done(self, test_name):
        """
        Sends the 'stopped' status to the web GUI when the test has finished.
        Updates the overall status tracking and writes the final status to a CSV file.

        Args:
            test_name (str): The name of the test that just finished.
        """
        try:
            self.overall_status[test_name] = "stopped"
            self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
            self.overall_csv.append(self.overall_status.copy())
            df1 = pd.DataFrame(self.overall_csv)
            df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
        except Exception as e:
            logger.info(e)

    def port_clean_up(self, port_no):
        """
        Cleans up the specified port by killing any processes using it.

        Args:
            port_no (int): The port number to clean up.
        """
        hostname = self.lanforge_ip
        username = "root"
        password = "lanforge"
        ports = []
        ports.append(port_no)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        for port in ports:
            print(f"\n--- Checking port {port} ---")

            try:
                # Get only the PIDs of processes using this port
                check_cmd = f"lsof -t -i:{port}"
                stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)
                pids = stdout.read().decode().strip().splitlines()

                if pids:
                    logger.info(f"Processes using port {port}: {', '.join(pids)}")

                    # Kill each PID safely
                    for pid in pids:
                        kill_cmd = f"kill -9 {pid}"
                        ssh.exec_command(kill_cmd, timeout=10)
                        print(f"Killed PID {pid} on port {port}")
                else:
                    print(f"No process found on port {port}")

            except Exception as e:
                print(f"Error checking port {port}: {e}")

        ssh.close()

    def misc_clean_up(self, layer3=False, layer4=False, generic=False, port_5000=False, port_5002=False, port_5003=False):
        """
        Use for the cleanup of cross connections
        arguments:
        layer3: (Boolean : optional) Default : False To Delete all layer3 connections
        layer4: (Boolean : optional) Default : False To Delete all layer4 connections
        generic: (Boolean : optional) Default : False To Delete all generic connections
        port_5000: (Boolean : optional) Default : False To Delete all connections on port 5000
        port_5002: (Boolean : optional) Default : False To Delete all connections on port 5002
        port_5003: (Boolean : optional) Default : False To Delete all connections on port 5003
        """
        if self.no_cleanup:
            return
        if layer3:
            self.cleanup.cxs_clean()
            self.cleanup.layer3_endp_clean()
        if layer4:
            self.cleanup.layer4_endp_clean()
        if generic:
            resp = self.json_get('/generic?fields=name')
            if 'endpoints' in resp:
                for i in resp['endpoints']:
                    if list(i.values())[0]['name']:
                        self.generic_endps_profile.created_cx.append('CX_' + list(i.values())[0]['name'])
                        self.generic_endps_profile.created_endp.append(list(i.values())[0]['name'])
            self.generic_endps_profile.cleanup()

        # TODO Need to verify this functionality , currently not required.
        # if port_5000 or port_5002 or port_5003:
        #     print('port cleanup......')
        #     time.sleep(5)
        #     hostname = self.lanforge_ip
        #     username = "root"
        #     password = "lanforge"
        #     ports = []
        #     if port_5003:
        #         ports.append(5003)
        #     if port_5000:
        #         ports.append(5000)
        #     if port_5002:
        #         ports.append(5002)
        #     # ssh = paramiko.SSHClient()
        #     # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #     # ssh.connect(hostname, username=username, password=password)

        #     # for cmd in commands:
        #     #     print(f"--- Running: {cmd} ---")
        #     #     stdin, stdout, stderr = ssh.exec_command(cmd)
        #     #     print("Output:\n", stdout.read().decode())
        #     #     print("Errors:\n", stderr.read().decode())
        #     # ssh.close()

        #     ssh = paramiko.SSHClient()
        #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #     ssh.connect(hostname, username=username, password=password)

        #     # for port in ports:
        #     #     print(f"\n--- Checking port {port} ---")

        #     #     try:
        #     #         check_cmd = f"lsof -i :{port}"
        #     #         stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)  # ⬅ timeout added
        #     #         output = stdout.read().decode().strip()
        #     #         error = stderr.read().decode().strip()

        #     #         if output:
        #     #             print(f"Processes using port {port}:\n{output}")

        #     #             # kill_cmd = f"fuser -kv {port}/tcp"
        #     #             # kill_cmd = f"fuser -k {port}/tcp"
        #     #             kill_cmd = f"fuser -k {port}/tcp || true"
        #     #             stdin, stdout, stderr = ssh.exec_command(kill_cmd, timeout=10)
        #     #             print("Kill Output:\n", stdout.read().decode())
        #     #             print("Kill Errors:\n", stderr.read().decode())
        #     #         else:
        #     #             print(f"No process found on port {port}")

        #     #     except Exception as e:
        #     #         print(f"Error checking port {port}: {e}")

        #     for port in ports:
        #         print(f"\n--- Checking port {port} ---")

        #         try:
        #             # Get only the PIDs of processes using this port
        #             check_cmd = f"lsof -t -i:{port}"
        #             stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)
        #             pids = stdout.read().decode().strip().splitlines()

        #             if pids:
        #                 print(f"Processes using port {port}: {', '.join(pids)}")

        #                 # Kill each PID safely
        #                 for pid in pids:
        #                     kill_cmd = f"kill -9 {pid}"
        #                     ssh.exec_command(kill_cmd, timeout=10)
        #                     print(f"Killed PID {pid} on port {port}")
        #             else:
        #                 print(f"No process found on port {port}")

        #         except Exception as e:
        #             print(f"Error checking port {port}: {e}")

        #     ssh.close()

    def check_all_tests(self):
        """
        Wait for all parallel tests in the current rotation to finish execution.
        This ensures that parallel test instances complete their rotation before proceeding.
        """
        if "qos_test" in self.parallel_tests:
            logger.info("Waiting for QoS test to finish")
            self.qos_rotate.wait()
        if "ftp_test" in self.parallel_tests:
            logger.info("Waiting for FTP test to finish")
            self.ftp_rotate.wait()
        if "http_test" in self.parallel_tests:
            logger.info("Waiting for HTTP test to finish")
            self.http_rotate.wait()
        if "ping_test" in self.parallel_tests:
            logger.info("Waiting for Ping test to finish")
            self.ping_rotate.wait()
        if "thput_test" in self.parallel_tests:
            logger.info("Waiting for Throughput test to finish")
            self.thput_rotate.wait()
        if "vs_test" in self.parallel_tests:
            logger.info("Waiting for Video Streaming test to finish")
            self.vs_rotate.wait()
        if "mcast_test" in self.parallel_tests:
            logger.info("Waiting for Multicast test to finish")
            self.mcast_rotate.wait()
        if "yt_test" in self.parallel_tests:
            logger.info("Waiting for YouTube test to finish")
            self.yt_rotate.wait()
        if "rb_test" in self.parallel_tests:
            logger.info("Waiting for Real Browser test to finish")
            self.rb_rotate.wait()
        if "zoom_test" in self.parallel_tests:
            logger.info("Waiting for Zoom test to finish")
            self.zoom_rotate.wait()
        logger.info("all tests finished")

    def wait_for_all_tests_to_finish_rotation(self, coordinate=None, angle=None):
        """
        Wait for all active parallel tests to finish their current rotation.

        Returns:
            tuple: A tuple containing (test_stopped, robo_moved, abort_event, robo_rotated)
        """
        if "qos_test" in self.parallel_tests:
            logger.info("Waiting for QoS test rotation to finish")
            self.qos_rotate_done_event.wait()
        if "ftp_test" in self.parallel_tests:
            logger.info("Waiting for FTP test rotation to finish")
            self.ftp_rotate_done_event.wait()
        if "http_test" in self.parallel_tests:
            logger.info("Waiting for HTTP test rotation to finish")
            self.http_rotate_done_event.wait()
        if "ping_test" in self.parallel_tests:
            logger.info("Waiting for Ping test rotation to finish")
            self.ping_rotate_done_event.wait()
        if "thput_test" in self.parallel_tests:
            logger.info("Waiting for Throughput test rotation to finish")
            self.thput_rotate_done_event.wait()
        if "vs_test" in self.parallel_tests:
            logger.info("Waiting for Video Streaming test rotation to finish")
            self.vs_rotate_done_event.wait()
        if "mcast_test" in self.parallel_tests:
            logger.info("Waiting for Multicast test rotation to finish")
            self.mcast_rotate_done_event.wait()
        if "yt_test" in self.parallel_tests:
            logger.info("Waiting for YouTube test rotation to finish")
            self.yt_rotate_done_event.wait()
        if "rb_test" in self.parallel_tests:
            logger.info("Waiting for Real Browser test rotation to finish")
            self.rb_rotate_done_event.wait()
        if "zoom_test" in self.parallel_tests:
            logger.info("Waiting for Zoom test rotation to finish")
            self.zoom_rotate_done_event.wait()
        with self.robot_lock:
            if not self.robot_rotate_move_event.is_set():
                self.robot_rotate_move_event.set()
                self.robo_controller(coord=coordinate, angle=angle)

            self.robot_rotate_call_counter.value += 1
            if self.robot_rotate_call_counter.value == len(self.parallel_tests):
                self.robot_rotate_move_event.clear()
                print("clearing the robot_rotate_move_event")
                self.robot_rotate_call_counter.value = 0
            return (
                self.test_stopped_event.is_set(),
                self.robo_moved.value,
                self.abort_event.is_set(),
                self.robo_rotated.value
            )

    def wait_for_all_tests_to_finish(self, coordinate=None, angle=None):
        """
        Wait for all active parallel tests to completely finish their execution.

        Returns:
            tuple: (test_stopped, robo_moved, abort_event_set, robo_rotated)
        """
        # print(self.qos_done_event.is_set(),"---",self.ftp_done_event.is_set(),"---",self.http_done_event.is_set())
        print("parallel tests running", self.parallel_tests)
        if "qos_test" in self.parallel_tests:
            logger.info("Waiting for QoS test to finish")
            self.qos_done_event.wait()
        if "ftp_test" in self.parallel_tests:
            logger.info("Waiting for FTP test to finish")
            self.ftp_done_event.wait()
        if "http_test" in self.parallel_tests:
            logger.info("Waiting for HTTP test to finish")
            self.http_done_event.wait()
        if "ping_test" in self.parallel_tests:
            logger.info("Waiting for Ping test to finish")
            self.ping_done_event.wait()
        if "thput_test" in self.parallel_tests:
            logger.info("Waiting for Throughput test to finish")
            self.thput_done_event.wait()
        if "vs_test" in self.parallel_tests:
            logger.info("Waiting for Video Streaming test to finish")
            self.vs_done_event.wait()
        if "mcast_test" in self.parallel_tests:
            logger.info("Waiting for Multicast test to finish")
            self.mcast_done_event.wait()
        if "yt_test" in self.parallel_tests:
            logger.info("Waiting for YouTube test to finish")
            self.yt_done_event.wait()
        if "rb_test" in self.parallel_tests:
            logger.info("Waiting for Real Browser test to finish")
            self.rb_done_event.wait()
        if "zoom_test" in self.parallel_tests:
            logger.info("Waiting for Zoom test to finish")
            self.zoom_done_event.wait()
        with self.robot_lock:
            if not self.robot_move_event.is_set():
                self.robot_move_event.set()
                self.robo_controller(coord=coordinate, angle=angle)

            self.robot_call_counter.value += 1
            if self.robot_call_counter.value == len(self.parallel_tests):
                self.robot_move_event.clear()
                self.robot_call_counter.value = 0
            return (
                self.test_stopped_event.is_set(),
                self.robo_moved.value,
                self.abort_event.is_set(),
                self.robo_rotated.value
            )

    def robo_controller(self, coord, angle=None):
        """
        Control the robot's movement or rotation.
        Ensures the robot has enough battery before proceeding. If 'angle' is provided,
        the robot will rotate. Otherwise, it will move to the specified 'coord'.
        """
        if not hasattr(self, "robot_obj"):
            raise RuntimeError("Robot not initialized in this process")

        self.robo_moved.value = False
        self.abort_event.clear()
        self.test_stopped_event.clear()

        if angle is None:

            if self.test_stopped_event.is_set():
                return

            _, stopped = self.robot_obj.wait_for_battery(battery=40)

            if stopped:
                logger.info("Test stopped while waiting for battery.")
                self.test_stopped_event.set()
                return

            logger.info(f"Moving robot to coordinate: {coord}")
            moved, abort = self.robot_obj.move_to_coordinate(coord)
            self.robo_moved.value = moved

            if abort:
                logger.warning("Robot movement aborted.")
                self.abort_event.set()
                return

        else:
            if self.rotation_enabled:
                logger.info(f"Rotating robot to angle: {angle}")
                self.robo_rotated.value = False
                _, stopped = self.robot_obj.wait_for_battery(battery=40)
                if stopped:
                    logger.info("Test stopped while waiting for battery before rotation.")
                    self.test_stopped_event.set()
                    return

                rotated = self.robot_obj.rotate_angle(1, 2, angle)
                self.robo_rotated.value = rotated

    def run_ping_test(
        self,
        target: str = '1.1.eth1',
        ping_interval: str = '1',
        ping_duration: float = 1,
        ssid: str = None,
        mgr_passwd: str = 'lanforge',
        server_ip: str = None,
        security: str = 'open',
        passwd: str = '[BLANK]',
        virtual: bool = False,
        num_sta: int = 1,
        radio: str = None,
        real: bool = True,
        use_default_config: bool = True,
        debug: bool = False,
        local_lf_report_dir: str = "",
        log_level: str = None,
        lf_logger_config_json: str = None,
        help_summary: bool = False,
        group_name: str = None,
        profile_name: str = None,
        file_name: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = '',
        ieee8021x: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = '[BLANK]',
        private_key: str = '[BLANK]',
        ca_cert: str = '[BLANK]',
        client_cert: str = '[BLANK]',
        pk_passwd: str = '[BLANK]',
        pac_file: str = '[BLANK]',
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        wait_time: int = 60,
        dev_list: str = None,
        do_bandsteering=False,
        cycles=1,
        bssids=None,
        duration_to_skip=None, robot_test=False,
    ):
        """
        Configure and execute a Ping test across virtual or real clients.
        This handles test configuration, endpoint creation, and generates a ping report upon completion.
        """
        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if log_level:
            logger_config.set_level(level=log_level)

        if lf_logger_config_json:
            # logger_config.lf_logger_config_json = "lf_logger_config.json"
            logger_config.lf_logger_config_json = lf_logger_config_json
            logger_config.load_lf_logger_config()
        # validate_args(args)

        mgr_ip = self.lanforge_ip
        mgr_password = mgr_passwd
        mgr_port = self.port
        server_ip = server_ip
        ssid = ssid
        security = security
        password = passwd
        num_sta = num_sta
        radio = radio
        target = target
        interval = ping_interval
        duration = ping_duration
        configure = not use_default_config
        debug = debug
        group_name = group_name
        file_name = file_name
        profile_name = profile_name
        eap_method = eap_method
        eap_identity = eap_identity
        ieee80211 = ieee8021x
        ieee80211u = ieee80211u
        ieee80211w = ieee80211w
        enable_pkc = enable_pkc
        bss_transition = bss_transition
        power_save = power_save
        disable_ofdma = disable_ofdma
        roam_ft_ds = roam_ft_ds
        key_management = key_management
        pairwise = pairwise
        private_key = private_key
        ca_cert = ca_cert
        client_cert = client_cert
        pk_passwd = pk_passwd
        pac_file = pac_file
        if (debug):
            logger.info('''Specified configuration:
                ip:                       {}
                port:                     {}
                ssid:                     {}
                security:                 {}
                password:                 {}
                target:                   {}
                Ping interval:            {}
                Packet Duration (in min): {}
                virtual:                  {}
                num of virtual stations:  {}
                radio:                    {}
                real:                     {}
                debug:                    {}
                '''.format(mgr_ip, mgr_port, ssid, security, password, target, interval, duration, virtual, num_sta, radio, real, debug))

        ce = self.current_exec  # seires
        if ce == "parallel":
            obj_name = "ping_test"
        else:
            obj_no = 1
            while f"ping_test_{obj_no}" in self.ping_obj_dict[ce]:
                obj_no += 1
            obj_name = f"ping_test_{obj_no}"
        self.ping_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        if self.dowebgui:
            if not self.webgui_stop_check("ping"):
                return False
        self.ping_obj_dict[ce][obj_name]["obj"] = Ping(host=mgr_ip, port=mgr_port, ssid=ssid, security=security, password=password, radio=radio,
                                                       lanforge_password=mgr_password, target=target, interval=interval, sta_list=[], virtual=virtual, real=real, duration=duration, debug=debug,
                                                       csv_name=device_csv_name, expected_passfail_val=expected_passfail_value, wait_time=wait_time, group_name=group_name)

        # changing the target from port to IP
        self.ping_obj_dict[ce][obj_name]["obj"].change_target_to_ip()

        # creating virtual stations if --virtual flag is specified
        if (virtual):

            logging.info('Proceeding to create {} virtual stations on {}'.format(num_sta, radio))
            station_list = LFUtils.portNameSeries(
                prefix_='sta', start_id_=0, end_id_=num_sta - 1, padding_number_=100000, radio=radio)
            self.ping_obj_dict[ce][obj_name]["obj"].sta_list = station_list
            if (debug):
                logging.info('Virtual Stations: {}'.format(station_list).replace(
                    '[', '').replace(']', '').replace('\'', ''))

        # selecting real clients if --real flag is specified
        if (real):
            Devices = RealDevice(manager_ip=mgr_ip, selected_bands=[])
            Devices.get_devices()
            self.ping_obj_dict[ce][obj_name]["obj"].Devices = Devices
            # self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices)
            # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
            if (configure):
                config_devices = {}
                obj = DeviceConfig.DeviceConfig(lanforge_ip=mgr_ip, file_name=file_name, wait_time=wait_time)
                # Case 1: Group name, file name, and profile name are provided
                if group_name and file_name and profile_name:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]
                    obj.initiate_group()
                    group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
                    # Configure devices in the selected group with the selected profile
                    eid_list = asyncio.run(obj.connectivity(config=config_devices, upstream=server_ip))
                    Devices.get_devices()
                    self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=eid_list)
                # Case 2: Device list is empty but config flag is True — prompt the user to input device details for configuration
                else:
                    all_devices = obj.get_all_devices()
                    device_list = []
                    config_dict = {
                        'ssid': ssid,
                        'passwd': password,
                        'enc': security,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee80211,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': server_ip,
                    }
                    for device in all_devices:
                        if device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                        else:
                            device_list.append(device["eid"] + " " + device["serial"])
                    logger.info(f"Available devices: {device_list}")
                    if dev_list is None:
                        dev_list = input("Enter the desired resources to run the test:")
                    dev_list = dev_list.split(',')
                    dev_list = asyncio.run(obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                    Devices.get_devices()
                    self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=dev_list)
            # Case 3: Config is False, no device list is provided, and no group is selected
            # Prompt the user to manually input devices for running the test
            else:
                device_list = self.ping_obj_dict[ce][obj_name]["obj"].Devices.get_devices()
                logger.info(f"Available devices: {device_list}")
                if dev_list is None or dev_list == []:
                    dev_list = input("Enter the desired resources to run the PING test:")
                dev_list = dev_list.split(',')
                # dev_list = input("Enter the desired resources to run the test:").split(',')
                self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=dev_list)

        # station precleanup
        self.ping_obj_dict[ce][obj_name]["obj"].cleanup()  # 11 change

        # building station if virtual
        if (virtual):
            self.ping_obj_dict[ce][obj_name]["obj"].buildstation()

        # check if generic tab is enabled or not
        if (not self.ping_obj_dict[ce][obj_name]["obj"].check_tab_exists()):
            logging.error('Generic Tab is not available.\nAborting the test.')
            return False

        self.ping_obj_dict[ce][obj_name]["obj"].sta_list += self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list

        # creating generic endpoints
        self.ping_obj_dict[ce][obj_name]["obj"].create_generic_endp()

        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].generic_endps_profile.created_cx)
        self.ping_done_event.set()
        self.ping_rotate_done_event.set()

        if self.robot_test and not self.do_bandsteering:
            if self.dowebgui:
                self.ping_obj_dict[ce][obj_name]["obj"].webgui = True

            if self.current_exec != "parallel":
                if self.dowebgui:
                    try:
                        with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name), 'r') as file:
                            data = json.load(file)
                            if data["status"] != "Running":
                                logging.info('Test is stopped by the user')
                                self.test_stopped = True
                        if not self.test_stopped:
                            self.overall_status['ping'] = "started"
                            self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                            self.overall_status["current_mode"] = self.current_exec
                            self.overall_status["current_test_name"] = "ping"
                            self.overall_csv.append(self.overall_status.copy())
                            df1 = pd.DataFrame(self.overall_csv)
                            df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
                    except Exception:
                        logger.info("Error while running for webui during ping execution")
                    if self.test_stopped:
                        logger.info("test has been stopped by the user")
                        return False
                self.ping_obj_dict[ce][obj_name]["obj"].local_lf_report_dir = local_lf_report_dir
                self.ping_obj_dict[ce][obj_name]["obj"].perform_robo_webui(self.ping_obj_dict[ce][obj_name]["obj"], Devices)
                params = {
                    "result_json": None,
                    "result_dir": "Ping_Test_Report",
                    "report_path": "",
                    "config_devices": "",
                    "group_device_map": {}
                }

                if local_lf_report_dir != "":
                    params["report_path"] = local_lf_report_dir

                if group_name:
                    params["config_devices"] = config_devices
                    params["group_device_map"] = group_device_map
                self.ping_obj_dict[ce][obj_name]["data"] = params.copy()
                if self.dowebgui:
                    self.webgui_test_done("ping")
                return True
            else:
                self.ping_obj_dict[ce][obj_name]["obj"].local_lf_report_dir = local_lf_report_dir
                rotation_enabled = bool(self.ping_obj_dict[ce][obj_name]["obj"].rotation_enabled)
                abort = False
                ports_data_dict = self.json_get('/ports/all/')['interfaces']
                ports_data = {}
                for ports in ports_data_dict:
                    port, port_data = list(ports.keys())[0], list(ports.values())[0]
                    ports_data[port] = port_data

                for coord in self.ping_obj_dict[ce][obj_name]["obj"].coordinate_list:
                    test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish(coordinate=coord)
                    if test_stopped_by_user:
                        break
                    if abort or not robo_moved:
                        break
                    self.ping_obj_dict[ce][obj_name]["obj"].coordinates_completed.append(coord)
                    self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate = coord
                    logging.info("rotationlist {}".format(self.ping_obj_dict[ce][obj_name]["obj"].angle_list))
                    self.ping_obj_dict[ce][obj_name]["obj"].result_json = {}
                    for j in range(len(self.ping_obj_dict[ce][obj_name]["obj"].angle_list)):
                        if rotation_enabled:
                            # self.ping_done_event.clear()
                            test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish_rotation(coordinate=coord, angle=self.rotation_list[j])
                            # self.ping_done_event.set()
                            if test_stopped_by_user:
                                break
                            if not robo_rotated:
                                break
                        self.ping_obj_dict[ce][obj_name]["obj"].currentangle = self.ping_obj_dict[ce][obj_name]["obj"].angle_list[j]
                        self.ping_done_event.clear()
                        if rotation_enabled:
                            self.ping_rotate_done_event.clear()
                            self.ping_rotate.set()
                            self.check_all_tests()
                        self.ping_obj_dict[ce][obj_name]["obj"].start_generic()
                        duration = self.ping_obj_dict[ce][obj_name]["obj"].duration * 60
                        time.sleep(duration)
                        logging.info('Stopping the cx')
                        self.ping_obj_dict[ce][obj_name]["obj"].stop_generic()
                        self.ping_done_event.set()
                        if rotation_enabled:
                            self.ping_rotate.clear()
                            self.ping_rotate_done_event.set()
                        result_data = self.ping_obj_dict[ce][obj_name]["obj"].get_results()
                        if (self.ping_obj_dict[ce][obj_name]["obj"].real):
                            if (isinstance(result_data, dict)):
                                for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                                    current_device_data = Devices.devices_data[station]
                                    # logging.info(current_device_data)
                                    if (station in result_data['name']):
                                        try:
                                            # logging.info(result_data['last results'].split('\n'))
                                            self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                                'command': result_data['command'],
                                                'sent': result_data['tx pkts'],
                                                'recv': result_data['rx pkts'],
                                                'dropped': result_data['dropped'],
                                                'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                'mac': current_device_data['mac'],
                                                'ssid': current_device_data['ssid'],
                                                'channel': current_device_data['channel'],
                                                'mode': current_device_data['mode'],
                                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                                'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                                'remarks': [],
                                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                                            }
                                            self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                        except Exception:
                                            logging.error('Failed parsing the result for the station {}'.format(station))
                            else:
                                for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                                    current_device_data = Devices.devices_data[station]
                                    for ping_device in result_data:
                                        ping_endp, ping_data = list(ping_device.keys())[
                                            0], list(ping_device.values())[0]
                                        if (station in ping_endp):
                                            try:
                                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                                    'command': ping_data['command'],
                                                    'sent': ping_data['tx pkts'],
                                                    'recv': ping_data['rx pkts'],
                                                    'dropped': ping_data['dropped'],
                                                    'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                    'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                    'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                                    'mac': current_device_data['mac'],
                                                    'ssid': current_device_data['ssid'],
                                                    'channel': current_device_data['channel'],
                                                    'mode': current_device_data['mode'],
                                                    'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                                    'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                                    'remarks': [],
                                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                                }
                                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                            except Exception:
                                                logging.error('Failed parsing the result for the station {}'.format(station))

                        if self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate not in self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json:

                            self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json[self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate] = {}
                        if self.ping_obj_dict[ce][obj_name]["obj"].rotation_enabled:
                            if self.ping_obj_dict[ce][obj_name]["obj"].currentangle not in self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json[self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate]:  # noqa: E501
                                self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json[self.ping_obj_dict[ce][obj_name]
                                                                                        ["obj"].currentcoordinate][self.ping_obj_dict[ce][obj_name]["obj"].currentangle] = {}
                            self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json[self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate][self.ping_obj_dict[ce]
                                                                                                                                               [obj_name]["obj"].currentangle] = self.ping_obj_dict[ce][obj_name]["obj"].result_json  # noqa: E501
                        else:
                            self.ping_obj_dict[ce][obj_name]["obj"].coordinate_json[self.ping_obj_dict[ce][obj_name]["obj"].currentcoordinate] = self.ping_obj_dict[ce][obj_name]["obj"].result_json

                if self.ping_obj_dict[ce][obj_name]["obj"].local_lf_report_dir == "":
                    self.ping_obj_dict[ce][obj_name]["obj"].generate_report_robo()
                else:
                    self.ping_obj_dict[ce][obj_name]["obj"].generate_report_robo(report_path=self.ping_obj_dict[ce][obj_name]["obj"].local_lf_report_dir)

                params = {
                    "result_json": None,
                    "result_dir": "Ping_Test_Report",
                    "report_path": "",
                    "config_devices": "",
                    "group_device_map": {}
                }

                if local_lf_report_dir != "":
                    params["report_path"] = local_lf_report_dir

                if group_name:
                    params["config_devices"] = config_devices
                    params["group_device_map"] = group_device_map
                self.ping_obj_dict[ce][obj_name]["data"] = params.copy()
                return True
        elif self.do_bandsteering:
            if self.dowebgui:
                start_time = datetime.datetime.now()
                end_time = start_time + datetime.timedelta(seconds=duration * 60)
                self.ping_obj_dict[ce][obj_name]["obj"].result_dir = local_lf_report_dir
            self.ping_obj_dict[ce][obj_name]["obj"].perform_bandsteering()
        # run the test for the given duration
        if not self.robot_test and not self.do_bandsteering:
            logging.info('Running the ping test for {} minutes'.format(duration))

            # start generate endpoint
            self.ping_obj_dict[ce][obj_name]["obj"].start_generic()
            # time_counter = 0
            ports_data_dict = self.ping_obj_dict[ce][obj_name]["obj"].json_get('/ports/all/')['interfaces']
            ports_data = {}
            for ports in ports_data_dict:
                port, port_data = list(ports.keys())[0], list(ports.values())[0]
                ports_data[port] = port_data
            ping_duration = duration
            if self.dowebgui:
                try:
                    with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name), 'r') as file:
                        data = json.load(file)
                        if data["status"] != "Running":
                            logging.info('Test is stopped by the user')
                            self.test_stopped = True
                    if not self.test_stopped:
                        self.overall_status['ping'] = "started"
                        self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                        self.overall_status["current_mode"] = self.current_exec
                        self.overall_status["current_test_name"] = "ping"
                        self.overall_csv.append(self.overall_status.copy())
                        df1 = pd.DataFrame(self.overall_csv)
                        df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
                except Exception:
                    logger.info("Error while running for webui during ping execution")
                if self.test_stopped:
                    logger.info("test has been stopped by the user")
                    return False
                start_time = datetime.datetime.now()
                end_time = start_time + datetime.timedelta(seconds=ping_duration * 60)
                temp_json = []
                while (datetime.datetime.now() < end_time):
                    temp_json = []
                    temp_checked_sta = []
                    temp_result_data = self.ping_obj_dict[ce][obj_name]["obj"].get_results()
                    if isinstance(temp_result_data, dict):
                        for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                            current_device_data = ports_data[station]
                            if (station in temp_result_data['name']):
                                temp_json.append({
                                    'device': station,
                                    'sent': temp_result_data['tx pkts'],
                                    'recv': temp_result_data['rx pkts'],
                                    'dropped': temp_result_data['dropped'],
                                    'status': "Running",
                                    'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                    'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                    "remaining_time": ""
                                })
                    else:
                        for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                            current_device_data = ports_data[station]
                            for ping_device in temp_result_data:
                                ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                                if station.split('-')[-1] in ping_endp and station not in temp_checked_sta:
                                    temp_checked_sta.append(station)
                                    temp_json.append({
                                        'device': station,
                                        'sent': ping_data['tx pkts'],
                                        'recv': ping_data['rx pkts'],
                                        'dropped': ping_data['dropped'],
                                        'status': "Running",
                                        'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                        'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                        "remaining_time": ""
                                    })
                    df1 = pd.DataFrame(temp_json)
                    df1.to_csv('{}/ping_datavalues.csv'.format(self.result_dir), index=False)
                    time.sleep(3)
            else:
                time.sleep(ping_duration * 60)

            logging.info('Stopping the test')
            self.ping_obj_dict[ce][obj_name]["obj"].stop_generic()

        result_data = self.ping_obj_dict[ce][obj_name]["obj"].get_results()
        # logging.info(result_data)
        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].result_json)
        if (virtual):
            ports_data_dict = self.ping_obj_dict[ce][obj_name]["obj"].json_get('/ports/all/')['interfaces']
            ports_data = {}
            for ports in ports_data_dict:
                port, port_data = list(ports.keys())[0], list(ports.values())[0]
                ports_data[port] = port_data
            if (isinstance(result_data, dict)):
                for station in self.ping_obj_dict[ce][obj_name]["obj"].sta_list:
                    if (station not in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list):
                        current_device_data = ports_data[station]
                        if (station.split('.')[2] in result_data['name']):
                            try:
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                    'command': result_data['command'],
                                    'sent': result_data['tx pkts'],
                                    'recv': result_data['rx pkts'],
                                    'dropped': result_data['dropped'],
                                    'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'mac': current_device_data['mac'],
                                    'channel': current_device_data['channel'],
                                    'ssid': current_device_data['ssid'],
                                    'mode': current_device_data['mode'],
                                    'name': station,
                                    'os': 'Virtual',
                                    'remarks': [],
                                    'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                                }
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                            except Exception:
                                logging.error('Failed parsing the result for the station {}'.format(station))

            else:
                for station in self.ping_obj_dict[ce][obj_name]["obj"].sta_list:
                    if (station not in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list):
                        current_device_data = ports_data[station]
                        for ping_device in result_data:
                            ping_endp, ping_data = list(ping_device.keys())[
                                0], list(ping_device.values())[0]
                            if (station.split('.')[2] in ping_endp):
                                try:
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                        'command': ping_data['command'],
                                        'sent': ping_data['tx pkts'],
                                        'recv': ping_data['rx pkts'],
                                        'dropped': ping_data['dropped'],
                                        'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'mac': current_device_data['mac'],
                                        'ssid': current_device_data['ssid'],
                                        'channel': current_device_data['channel'],
                                        'mode': current_device_data['mode'],
                                        'name': station,
                                        'os': 'Virtual',
                                        'remarks': [],
                                        'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                    }
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                        self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                except Exception:
                                    logging.error('Failed parsing the result for the station {}'.format(station))

        if (real):
            if (isinstance(result_data, dict)):
                for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    # logging.info(current_device_data)
                    if (station in result_data['name']):
                        try:
                            # logging.info(result_data['last results'].split('\n'))
                            self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                'command': result_data['command'],
                                'sent': result_data['tx pkts'],
                                'recv': result_data['rx pkts'],
                                'dropped': result_data['dropped'],
                                'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                'mac': current_device_data['mac'],
                                'ssid': current_device_data['ssid'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                'remarks': [],
                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                            }
                            self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                        except Exception:
                            logging.error('Failed parsing the result for the station {}'.format(station))
            else:
                for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    for ping_device in result_data:
                        ping_endp, ping_data = list(ping_device.keys())[
                            0], list(ping_device.values())[0]
                        if (station in ping_endp):
                            try:
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                    'command': ping_data['command'],
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'mac': current_device_data['mac'],
                                    'ssid': current_device_data['ssid'],
                                    'channel': current_device_data['channel'],
                                    'mode': current_device_data['mode'],
                                    'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                    'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                    'remarks': [],
                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                }
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                            except Exception:
                                logging.error('Failed parsing the result for the station {}'.format(station))

        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].result_json)

        # station post cleanup
        self.ping_obj_dict[ce][obj_name]["obj"].cleanup()  # 12 change
        if self.dowebgui:
            temp_json = []
            for station in self.ping_obj_dict[ce][obj_name]["obj"].result_json:
                logging.debug('{} {}'.format(station, self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]))
                temp_json.append({'device': station,
                                  'sent': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['sent'],
                                  'recv': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['recv'],
                                  'dropped': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['dropped'],
                                  'status': "Stopped",
                                  'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                  'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                  "remaining_time": ""})
            df1 = pd.DataFrame(temp_json)
            df1.to_csv('{}/ping_datavalues.csv'.format(self.result_dir), index=False)
        if local_lf_report_dir == "":
            # Report generation when groups are specified but no custom report path is provided
            if group_name:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(config_devices=config_devices, group_device_map=group_device_map)
            # Report generation when no group is specified and no custom report path is provided
            else:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report()
        else:
            # Report generation when groups are specified and a custom report path is provided
            if group_name:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(config_devices=config_devices, group_device_map=group_device_map, report_path=local_lf_report_dir)
            # Report generation when no group is specified but a custom report path is provided
            else:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(report_path=local_lf_report_dir)
        params = {
            "result_json": None,
            "result_dir": "Ping_Test_Report",
            "report_path": "",
            "config_devices": "",
            "group_device_map": {}
        }

        if local_lf_report_dir != "":
            params["report_path"] = local_lf_report_dir

        if group_name:
            params["config_devices"] = config_devices
            params["group_device_map"] = group_device_map
        self.ping_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("ping")
        return True

    def run_http_test(
        self,
        upstream_port='eth2',
        num_stations=0,
        twog_radio='wiphy3',
        fiveg_radio='wiphy0',
        sixg_radio='wiphy2',
        twog_security=None,
        twog_ssid=None,
        twog_passwd=None,
        fiveg_security=None,
        fiveg_ssid=None,
        fiveg_passwd=None,
        sixg_security=None,
        sixg_ssid=None,
        sixg_passwd=None,
        target_per_ten=100,
        file_size='5MB',
        bands=None,
        duration=None,
        client_type="Real",
        threshold_5g="60",
        threshold_2g="90",
        threshold_both="50",
        ap_name="TestAP",
        lf_username="lanforge",
        lf_password="lanforge",
        ssh_port=22,
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="lf_webpage",
        csv_outfile="",
        dowebgui=False,
        result_dir='',
        device_list=None,
        test_name=None,
        get_url_from_file=False,
        file_path=None,
        help_summary=False,
        ssid=None,
        passwd='',
        security=None,
        file_name=None,
        group_name=None,
        profile_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        get_live_view=False,
        total_floors="0",
        do_bandsteering=False,
        cycles=None,
        bssids=None,
        duration_to_skip=None
    ):
        """
        Configure and execute an HTTP test across virtual or real clients.
        This handles test configuration, endpoint creation, and generates an HTTP report upon completion.
        """
        bands = ["5G", "2.4G", "6G"] if bands is None else bands
        device_list = [] if device_list is None else device_list
        if self.dowebgui:
            if not self.webgui_stop_check("http"):
                return False
        bands.sort()

        # Error checking to prevent case issues
        for band in range(len(bands)):
            bands[band] = bands[band].upper()
            if bands[band] == "BOTH":
                bands[band] = "Both"

        # Error checking for non-existent bands
        valid_bands = ['2.4G', '5G', '6G', 'Both']
        for band in bands:
            if band not in valid_bands:
                raise ValueError("Invalid band '%s' used in bands argument!" % band)

        # Check for Both being used independently
        if len(bands) > 1 and "Both" in bands:
            raise ValueError("'Both' test type must be used independently!")

        # validate_args(args)
        if duration.endswith('s') or duration.endswith('S'):
            duration = int(duration[0:-1])
        elif duration.endswith('m') or duration.endswith('M'):
            duration = int(duration[0:-1]) * 60
        elif duration.endswith('h') or duration.endswith('H'):
            duration = int(duration[0:-1]) * 60 * 60
        elif duration.endswith(''):
            duration = int(duration)

        list6G, list6G_bytes, list6G_speed, list6G_urltimes = [], [], [], []
        list5G, list5G_bytes, list5G_speed, list5G_urltimes = [], [], [], []
        list2G, list2G_bytes, list2G_speed, list2G_urltimes = [], [], [], []
        Both, Both_bytes, Both_speed, Both_urltimes = [], [], [], []
        listReal, listReal_bytes, listReal_speed, listReal_urltimes = [], [], [], []  # For real devices (not band specific)
        dict_keys = []
        dict_keys.extend(bands)
        # print(dict_keys)
        final_dict = dict.fromkeys(dict_keys)
        # print(final_dict)
        dict1_keys = ['dl_time', 'min', 'max', 'avg', 'bytes_rd', 'speed', 'url_times']
        for i in final_dict:
            final_dict[i] = dict.fromkeys(dict1_keys)
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
        port_list, dev_list, macid_list = [], [], []
        for band in bands:
            # For real devices while ensuring no blocker for Virtual devices
            if client_type == 'Real':
                ssid = ssid
                passwd = passwd
                security = security
            elif band == "2.4G":
                security = [twog_security]
                ssid = [twog_ssid]
                passwd = [twog_passwd]
            elif band == "5G":
                security = [fiveg_security]
                ssid = [fiveg_ssid]
                passwd = [fiveg_passwd]
            elif band == "6G":
                security = [sixg_security]
                ssid = [sixg_ssid]
                passwd = [sixg_passwd]
            elif band == "Both":
                security = [twog_security, fiveg_security]
                ssid = [twog_ssid, fiveg_ssid]
                passwd = [twog_passwd, fiveg_passwd]
            ce = self.current_exec  # seires
            if ce == "parallel":
                obj_name = "http_test"
            else:
                obj_no = 1
                while f"http_test_{obj_no}" in self.http_obj_dict[ce]:
                    obj_no += 1
                obj_name = f"http_test_{obj_no}"
            self.http_obj_dict[ce][obj_name] = {"obj": None, "data": None}

            self.http_obj_dict[ce][obj_name]["obj"] = http_test.HttpDownload(lfclient_host=self.lanforge_ip, lfclient_port=self.port,
                                                                             upstream=upstream_port, num_sta=num_stations,
                                                                             security=security, ap_name=ap_name,
                                                                             ssid=ssid, password=passwd,
                                                                             target_per_ten=target_per_ten,
                                                                             file_size=file_size, bands=band,
                                                                             twog_radio=twog_radio,
                                                                             fiveg_radio=fiveg_radio,
                                                                             sixg_radio=sixg_radio,
                                                                             client_type=client_type,
                                                                             lf_username=lf_username, lf_password=lf_password,
                                                                             result_dir=result_dir,  # FOR WEBGUI
                                                                             dowebgui=dowebgui,  # FOR WEBGUI
                                                                             device_list=device_list,
                                                                             test_name=test_name,  # FOR WEBGUI
                                                                             get_url_from_file=get_url_from_file,
                                                                             file_path=file_path,
                                                                             file_name=file_name,
                                                                             group_name=group_name,
                                                                             profile_name=profile_name,
                                                                             eap_method=eap_method,
                                                                             eap_identity=eap_identity,
                                                                             ieee80211=ieee8021x,
                                                                             ieee80211u=ieee80211u,
                                                                             ieee80211w=ieee80211w,
                                                                             enable_pkc=enable_pkc,
                                                                             bss_transition=bss_transition,
                                                                             power_save=power_save,
                                                                             disable_ofdma=disable_ofdma,
                                                                             roam_ft_ds=roam_ft_ds,
                                                                             key_management=key_management,
                                                                             pairwise=pairwise,
                                                                             private_key=private_key,
                                                                             ca_cert=ca_cert,
                                                                             client_cert=client_cert,
                                                                             pk_passwd=pk_passwd,
                                                                             pac_file=pac_file,
                                                                             expected_passfail_value=expected_passfail_value,
                                                                             device_csv_name=device_csv_name,
                                                                             wait_time=wait_time,
                                                                             config=config,
                                                                             get_live_view=get_live_view,
                                                                             total_floors=total_floors,
                                                                             robot_test=self.robot_test,
                                                                             robot_ip=self.robot_ip,
                                                                             coordinate=self.coordinate,
                                                                             rotation=self.rotation,
                                                                             duration=duration,
                                                                             do_bandsteering=do_bandsteering,
                                                                             cycles=cycles,
                                                                             bssids=bssids,
                                                                             duration_to_skip=duration_to_skip
                                                                             )
            if client_type == "Real":
                if not isinstance(device_list, list):
                    self.http_obj_dict[ce][obj_name]["obj"].device_list = self.http_obj_dict[ce][obj_name]["obj"].filter_iOS_devices(device_list)
                    if len(self.http_obj_dict[ce][obj_name]["obj"].device_list) == 0:
                        logger.info("There are no devices available")
                        return False
                port_list, dev_list, macid_list, configuration = self.http_obj_dict[ce][obj_name]["obj"].get_real_client_list()
                if dowebgui and group_name:
                    if len(dev_list) == 0:
                        logger.info("No device is available to run the test")
                        obj = {
                            "status": "Stopped",
                            "configuration_status": "configured"
                        }
                        self.http_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj)
                        return
                    else:
                        obj = {
                            "configured_devices": dev_list,
                            "configuration_status": "configured"
                        }
                        self.http_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj)
                num_stations = len(port_list)
            if not get_url_from_file:
                self.http_obj_dict[ce][obj_name]["obj"].file_create(ssh_port=ssh_port)
            else:
                if file_path is None:
                    logger.warning("Please Specify the path of the file, if you select the --get_url_from_file")
                    return False
            self.http_obj_dict[ce][obj_name]["obj"].set_values()
            self.http_obj_dict[ce][obj_name]["obj"].precleanup()
            self.http_obj_dict[ce][obj_name]["obj"].build()
            if client_type == 'Real':
                self.http_obj_dict[ce][obj_name]["obj"].monitor_cx()
                self.http_done_event.set()
                self.http_rotate_done_event.set()
                logger.info(f'Test started on the devices : {self.http_obj_dict[ce][obj_name]["obj"].port_list}')
            test_time = datetime.datetime.now()
            # Solution For Leap Year conflict changed it to %Y
            test_time = test_time.strftime("%Y %d %H:%M:%S")
            logger.info(f"Test started at {test_time}")
            if self.http_obj_dict[ce][obj_name]["obj"].robot_test:
                if self.current_exec != "parallel":
                    self.http_obj_dict[ce][obj_name]["obj"].perform_robo()
                else:
                    if self.http_obj_dict[ce][obj_name]["obj"].rotation_list[0] != "":
                        self.http_obj_dict[ce][obj_name]["obj"].rotation_enabled = True

                    test_stopped_by_user = False
                    for coordinate in range(len(self.http_obj_dict[ce][obj_name]["obj"].coordinate_list)):
                        # print("Moving to coordinate:", coordinate)
                        # self.robot_move_event.clear()
                        if test_stopped_by_user:
                            break
                        test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish(coordinate=self.http_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate])
                        if test_stopped_by_user:
                            break

                        if abort or not robo_moved:
                            break
                        # If robot reached the coordinate
                        if robo_moved:
                            self.http_obj_dict[ce][obj_name]["obj"].current_coordinate = self.http_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate]
                            # if no rotation mode
                            if not self.http_obj_dict[ce][obj_name]["obj"].rotation_enabled:
                                # Start the test
                                self.http_done_event.clear()
                                self.http_obj_dict[ce][obj_name]["obj"].start()
                                test_stopped_by_user_http = self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(self.http_obj_dict[ce][obj_name]["obj"].duration)
                                self.http_obj_dict[ce][obj_name]["obj"].stop()
                                self.http_done_event.set()
                                self.http_obj_dict[ce][obj_name]["obj"].update_stop_status_robot()
                                if test_stopped_by_user_http:
                                    break

                            # if rotation mode
                            else:
                                for angle in range(len(self.http_obj_dict[ce][obj_name]["obj"].rotation_list)):
                                    test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish_rotation(
                                        coordinate=self.http_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate], angle=self.http_obj_dict[ce][obj_name]["obj"].rotation_list[angle])
                                    if test_stopped_by_user:
                                        break
                                    if robo_rotated:
                                        self.http_obj_dict[ce][obj_name]["obj"].current_angle = self.http_obj_dict[ce][obj_name]["obj"].rotation_list[angle]
                                        # self.http_monitor = True
                                        self.http_done_event.clear()
                                        self.http_rotate_done_event.clear()
                                        self.http_rotate.set()
                                        self.check_all_tests()
                                        self.http_obj_dict[ce][obj_name]["obj"].start()
                                        test_stopped_by_user_http = self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(self.http_obj_dict[ce][obj_name]["obj"].duration)
                                        self.http_obj_dict[ce][obj_name]["obj"].stop()
                                        self.http_done_event.set()
                                        self.http_rotate_done_event.set()
                                        self.http_rotate.clear()
                                        # self.http_monitor = False
                                        self.http_obj_dict[ce][obj_name]["obj"].update_stop_status_robot()
                                        # If test is stopped by user
                                        if test_stopped_by_user_http:
                                            break
            else:
                self.http_obj_dict[ce][obj_name]["obj"].start()
                if dowebgui:
                    # FOR WEBGUI, -This fumction is called to fetch the runtime data from layer-4
                    self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(duration)
                elif client_type == 'Real':
                    # To fetch runtime csv during runtime
                    self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(duration)
                else:
                    time.sleep(duration)
                self.http_obj_dict[ce][obj_name]["obj"].stop()
            # taking self.http_obj_dict[ce][obj_name]["obj"].data, which got updated in the monitor_for_runtime_csv method
            if client_type == 'Real':
                uc_avg_val = self.http_obj_dict[ce][obj_name]["obj"].data['uc_avg']
                url_times = self.http_obj_dict[ce][obj_name]["obj"].data['url_data']
                rx_bytes_val = self.http_obj_dict[ce][obj_name]["obj"].data['bytes_rd']
                rx_rate_val = list(self.http_obj_dict[ce][obj_name]["obj"].data['rx rate (1m)'])
            else:
                uc_avg_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('uc-avg')
                url_times = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('total-urls')
                rx_bytes_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('bytes-rd')
                rx_rate_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('rx rate')
            if dowebgui:
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["url_data"] = url_times  # storing the layer-4 url data at the end of test
            if client_type == 'Real':  # for real clients
                listReal.extend(uc_avg_val)
                listReal_bytes.extend(rx_bytes_val)
                listReal_speed.extend(rx_rate_val)
                listReal_urltimes.extend(url_times)
                logger.info("%s %s %s", listReal, listReal_bytes, listReal_speed)
                final_dict[band]['dl_time'] = listReal
                min2.append(min(listReal))
                final_dict[band]['min'] = min2
                max2.append(max(listReal))
                final_dict[band]['max'] = max2
                avg2.append((sum(listReal) / num_stations))
                final_dict[band]['avg'] = avg2
                final_dict[band]['bytes_rd'] = listReal_bytes
                final_dict[band]['speed'] = listReal_speed
                final_dict[band]['url_times'] = listReal_urltimes
            else:
                if band == "5G":
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
                    avg5.append((sum(list5G) / num_stations))
                    final_dict['5G']['avg'] = avg5
                    final_dict['5G']['bytes_rd'] = list5G_bytes
                    final_dict['5G']['speed'] = list5G_speed
                    final_dict['5G']['url_times'] = list5G_urltimes
                elif band == "6G":
                    list6G.extend(uc_avg_val)
                    list6G_bytes.extend(rx_bytes_val)
                    list6G_speed.extend(rx_rate_val)
                    list6G_urltimes.extend(url_times)
                    final_dict['6G']['dl_time'] = list6G
                    min6.append(min(list6G))
                    final_dict['6G']['min'] = min6
                    max6.append(max(list6G))
                    final_dict['6G']['max'] = max6
                    avg6.append((sum(list6G) / num_stations))
                    final_dict['6G']['avg'] = avg6
                    final_dict['6G']['bytes_rd'] = list6G_bytes
                    final_dict['6G']['speed'] = list6G_speed
                    final_dict['6G']['url_times'] = list6G_urltimes
                elif band == "2.4G":
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
                    avg2.append((sum(list2G) / num_stations))
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
                    avg_both.append((sum(Both) / num_stations))
                    final_dict['Both']['avg'] = avg_both
                    final_dict['Both']['bytes_rd'] = Both_bytes
                    final_dict['Both']['speed'] = Both_speed
                    final_dict['Both']['url_times'] = Both_urltimes

        result_data = final_dict
        logger.info(f"result: {result_data}")
        logger.info("Test Finished")
        test_end = datetime.datetime.now()
        test_end = test_end.strftime("%Y %d %H:%M:%S")
        logger.info(f"Test ended at {test_end}")
        s1 = test_time
        s2 = test_end  # for example
        FMT = '%Y %d %H:%M:%S'
        test_duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)

        info_ssid = []
        info_security = []
        # For real clients
        if client_type == 'Real':
            info_ssid.append(ssid)
            info_security.append(security)
        else:
            for band in bands:
                if band == "2.4G":
                    info_ssid.append(twog_ssid)
                    info_security.append(twog_security)
                elif band == "5G":
                    info_ssid.append(fiveg_ssid)
                    info_security.append(fiveg_security)
                elif band == "6G":
                    info_ssid.append(sixg_ssid)
                    info_security.append(sixg_security)
                elif band == "Both":
                    info_ssid.append(fiveg_ssid)
                    info_security.append(fiveg_security)
                    info_ssid.append(twog_ssid)
                    info_security.append(twog_security)

        logger.info(f"total test duration {test_duration}")
        date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
        duration = duration
        if int(duration) < 60:
            duration = str(duration) + "s"
        elif int(duration == 60) or (int(duration) > 60 and int(duration) < 3600):
            duration = str(duration / 60) + "m"
        else:
            if int(duration == 3600) or (int(duration) > 3600):
                duration = str(duration / 3600) + "h"

        android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
        all_devices_names = []
        device_type = []
        total_devices = ""
        for i in self.http_obj_dict[ce][obj_name]["obj"].devices_list:
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
        if client_type == "Real":
            if group_name:
                group_names = ', '.join(configuration.keys())
                profile_names = ', '.join(configuration.values())
                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                test_setup_info = {
                    "AP name": ap_name,
                    "Configuration": configmap,
                    "Configured Devices": ", ".join(all_devices_names),
                    "No of Devices": "Total" + f"({len(all_devices_names)})" + total_devices,
                    "Traffic Direction": "Download",
                    "Traffic Duration ": duration
                }
            else:
                test_setup_info = {
                    "AP Name": ap_name,
                    "SSID": ssid,
                    "Device List": ", ".join(all_devices_names),
                    "Security": security,
                    "No of Devices": "Total" + f"({len(all_devices_names)})" + total_devices,
                    "Traffic Direction": "Download",
                    "Traffic Duration ": duration
                }
        else:
            test_setup_info = {
                "AP Name": ap_name,
                "SSID": ssid,
                "Security": security,
                "No of Devices": num_stations,
                "Traffic Direction": "Download",
                "Traffic Duration ": duration
            }
        test_input_infor = {
            "LANforge ip": self.lanforge_ip,
            "Bands": bands,
            "Upstream": upstream_port,
            "Stations": num_stations,
            "SSID": ','.join(filter(None, info_ssid)) if info_ssid else "",
            "Security": ', '.join(filter(None, info_security)) if info_security else "",
            "Duration": duration,
            "Contact": "support@candelatech.com"
        }
        if not file_path:
            test_setup_info["File size"] = file_size
            test_setup_info["File location"] = "/usr/local/lanforge/nginx/html"
            test_input_infor["File size"] = file_size
        else:
            test_setup_info["File location (URLs from the File)"] = file_path
        if client_type == "Real":
            test_setup_info["failed_cx's"] = self.http_obj_dict[ce][obj_name]["obj"].failed_cx if self.http_obj_dict[ce][obj_name]["obj"].failed_cx else "NONE"
        # dataset = self.http_obj_dict[ce][obj_name]["obj"].download_time_in_sec(result_data=result_data)
        rx_rate = []
        for i in result_data:
            dataset = result_data[i]['dl_time']
            dataset2 = result_data[i]['url_times']
            bytes_rd = result_data[i]['bytes_rd']
            rx_rate = result_data[i]['speed']
        dataset1 = [round(x / 1000000, 4) for x in bytes_rd]
        rx_rate = [round(x / 1000000, 4) for x in rx_rate]  # converting bps to mbps

        self.lis = []
        if band == "Both":
            for i in range(1, num_stations * 2 + 1):
                self.lis.append(i)
        else:
            for i in range(1, num_stations + 1):
                self.lis.append(i)

        if dowebgui:
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["status"] = ["STOPPED"] * len(self.http_obj_dict[ce][obj_name]["obj"].devices_list)
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui['rx rate (1m)'] = self.http_obj_dict[ce][obj_name]["obj"].data['rx rate (1m)']
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui['total_err'] = self.http_obj_dict[ce][obj_name]["obj"].data['total_err']
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["start_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["start_time"]
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["end_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["end_time"]
            self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["remaining_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["remaining_time"]
            df1 = pd.DataFrame(self.http_obj_dict[ce][obj_name]["obj"].data_for_webui)
            df1.to_csv('{}/http_datavalues.csv'.format(self.http_obj_dict[ce][obj_name]["obj"].result_dir), index=False)

        self.http_obj_dict[ce][obj_name]["obj"].generate_report(date, num_stations=num_stations,
                                                                duration=duration, test_setup_info=test_setup_info, dataset=dataset, lis=self.lis,
                                                                bands=bands, threshold_2g=threshold_2g, threshold_5g=threshold_5g,
                                                                threshold_both=threshold_both, dataset2=dataset2, dataset1=dataset1,
                                                                # summary_table_value=summary_table_value,
                                                                result_data=result_data, rx_rate=rx_rate,
                                                                test_rig=test_rig, test_tag=test_tag, dut_hw_version=dut_hw_version,
                                                                dut_sw_version=dut_sw_version, dut_model_num=dut_model_num,
                                                                dut_serial_num=dut_serial_num, test_id=test_id,
                                                                test_input_infor=test_input_infor, csv_outfile=csv_outfile, report_path=self.result_path if not self.dowebgui else self.result_dir)
        params = {
            "date": date,
            "num_stations": num_stations,
            "duration": duration,
            "test_setup_info": test_setup_info,
            "dataset": dataset,
            "lis": self.lis,
            "bands": bands,
            "threshold_2g": threshold_2g,
            "threshold_5g": threshold_5g,
            "threshold_both": threshold_both,
            "dataset2": dataset2,
            "dataset1": dataset1,
            # "summary_table_value": summary_table_value,  # optional
            "result_data": result_data,
            "rx_rate": rx_rate,
            "test_rig": test_rig,
            "test_tag": test_tag,
            "dut_hw_version": dut_hw_version,
            "dut_sw_version": dut_sw_version,
            "dut_model_num": dut_model_num,
            "dut_serial_num": dut_serial_num,
            "test_id": test_id,
            "test_input_infor": test_input_infor,
            "csv_outfile": csv_outfile,
            "report_path": self.result_path
        }
        self.http_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("http")

        self.http_obj_dict[ce][obj_name]["obj"].postcleanup()
        if dowebgui:
            self.http_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        return True

    def run_ftp_test(
        self,
        mgr='localhost',
        mgr_port=8080,
        upstream_port='eth1',
        ssid=None,
        passwd=None,
        security=None,
        group_name=None,
        profile_name=None,
        file_name=None,
        ap_name=None,
        traffic_duration=None,
        clients_type="Real",
        dowebgui=False,
        directions=None,
        file_sizes=None,
        local_lf_report_dir="",
        ap_ip=None,
        twog_radio='wiphy1',
        fiveg_radio='wiphy0',
        sixg_radio='wiphy2',
        lf_username='lanforge',
        lf_password='lanforge',
        ssh_port=22,
        bands=None,
        num_stations=0,
        result_dir='',
        device_list=None,
        test_name=None,
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="FTP Data",
        csv_outfile="",
        eap_method="DEFAULT",
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management="DEFAULT",
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        get_live_view=False,
        total_floors="0",
        lf_logger_config_json=None,
        help_summary=False,
        do_bandsteering=False,
        cycles=None,
        bssids=None,
        duration_to_skip=None

    ):
        """
        Configure and execute an FTP test.
        This handles argument processing and delegates execution to `run_ftp_test1`.
        """
        directions = ["Download"] if directions is None else directions
        file_sizes = ["2MB", "500MB", "1000MB"] if file_sizes is None else file_sizes
        bands = ["5G", "2.4G", "6G", "Both"] if bands is None else bands
        device_list = [] if device_list is None else device_list
        args = SimpleNamespace(**locals())
        args.mgr = self.lanforge_ip
        args.mgr_port = int(self.port)
        return self.run_ftp_test1(args)

    def run_ftp_test1(self, args):
        """
        Execute an FTP test across virtual or real clients.
        This handles test configuration, endpoint creation, and generates an FTP report upon completion.
        """
        if self.dowebgui:
            if not self.webgui_stop_check("ftp"):
                return False
        # 1st time stamp for test duration
        # use for creating ftp_test dictionary
        interation_num = 0

        # empty dictionary for whole test data
        ftp_data = {}

        # validate_args(args)
        if args.traffic_duration.endswith('s') or args.traffic_duration.endswith('S'):
            args.traffic_duration = int(args.traffic_duration[0:-1])
        elif args.traffic_duration.endswith('m') or args.traffic_duration.endswith('M'):
            args.traffic_duration = int(args.traffic_duration[0:-1]) * 60
        elif args.traffic_duration.endswith('h') or args.traffic_duration.endswith('H'):
            args.traffic_duration = int(args.traffic_duration[0:-1]) * 60 * 60
        elif args.traffic_duration.endswith(''):
            args.traffic_duration = int(args.traffic_duration)
        ce = self.current_exec  # seires
        if ce == "parallel":
            obj_name = "ftp_test"
        else:
            obj_no = 1
            while f"ftp_test_{obj_no}" in self.ftp_obj_dict[ce]:
                obj_no += 1
            obj_name = f"ftp_test_{obj_no}"
        self.ftp_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        # For all combinations ftp_data of directions, file size and client counts, run the test
        for band in args.bands:
            for direction in args.directions:
                for file_size in args.file_sizes:
                    # Start Test
                    self.ftp_obj_dict[ce][obj_name]["obj"] = FtpTest(lfclient_host=args.mgr,
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
                                                                     config=args.config,
                                                                     get_live_view=args.get_live_view,
                                                                     total_floors=args.total_floors,
                                                                     robot_test=self.robot_test,
                                                                     robot_ip=self.robot_ip,
                                                                     coordinate=self.coordinate,
                                                                     rotation=self.rotation,
                                                                     do_bandsteering=args.do_bandsteering,
                                                                     cycles=args.cycles,
                                                                     bssids=args.bssids,
                                                                     duration_to_skip=args.duration_to_skip
                                                                     )

                    interation_num = interation_num + 1
                    self.ftp_obj_dict[ce][obj_name]["obj"].file_create()
                    if args.clients_type == "Real":
                        if not isinstance(args.device_list, list):
                            self.ftp_obj_dict[ce][obj_name]["obj"].device_list = self.ftp_obj_dict[ce][obj_name]["obj"].filter_iOS_devices(args.device_list)
                            if len(self.ftp_obj_dict[ce][obj_name]["obj"].device_list) == 0:
                                logger.info("There are no devices available")
                                return False
                        configured_device, configuration = self.ftp_obj_dict[ce][obj_name]["obj"].query_realclients()

                    if args.dowebgui and args.group_name:
                        # If no devices are configured,update the Web UI with "Stopped" status
                        if len(configured_device) == 0:
                            logger.warning("No device is available to run the test")
                            obj1 = {
                                "status": "Stopped",
                                "configuration_status": "configured"
                            }
                            self.ftp_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                            return
                        # If devices are configured, update the Web UI with the list of configured devices
                        else:
                            obj1 = {
                                "configured_devices": configured_device,
                                "configuration_status": "configured"
                            }
                            self.ftp_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                    self.ftp_obj_dict[ce][obj_name]["obj"].set_values()
                    self.ftp_obj_dict[ce][obj_name]["obj"].precleanup()
                    self.ftp_obj_dict[ce][obj_name]["obj"].build()
                    if not self.ftp_obj_dict[ce][obj_name]["obj"].passes():
                        logger.info(self.ftp_obj_dict[ce][obj_name]["obj"].get_fail_message())
                        return False

                    if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == 'Real':
                        self.ftp_obj_dict[ce][obj_name]["obj"].monitor_cx()
                        logger.info(f'Test started on the devices : {self.ftp_obj_dict[ce][obj_name]["obj"].input_devices_list}')
                    self.ftp_done_event.set()
                    self.ftp_rotate_done_event.set()
                    # First time stamp
                    time1 = datetime.datetime.now()
                    logger.info("Traffic started running at %s", time1)
                    if self.ftp_obj_dict[ce][obj_name]["obj"].robot_test:
                        if self.current_exec != "parallel":
                            self.ftp_obj_dict[ce][obj_name]["obj"].perform_robo()
                        else:
                            if self.ftp_obj_dict[ce][obj_name]["obj"].rotation_list[0] != "":
                                self.ftp_obj_dict[ce][obj_name]["obj"].rotation_enabled = True
                            for coordinate in range(len(self.ftp_obj_dict[ce][obj_name]["obj"].coordinate_list)):
                                # self.robot_move_event.clear()
                                # test_stopped_by_user,robo_moved, abort, robo_rotated = self.robo_controller(coord=coordinate)
                                test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish(coordinate=self.ftp_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate])
                                if test_stopped_by_user:
                                    break
                                if abort or not robo_moved:
                                    break
                                # If robot reached the coordinate
                                if robo_moved:
                                    # if no rotation mode
                                    self.ftp_obj_dict[ce][obj_name]["obj"].current_coordinate = self.ftp_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate]
                                    if not self.ftp_obj_dict[ce][obj_name]["obj"].rotation_enabled:
                                        # Start the test
                                        # self.ftp_monitor = True
                                        self.ftp_done_event.clear()
                                        self.ftp_obj_dict[ce][obj_name]["obj"].start(False, False)
                                        test_stopped_by_user_ftp = self.ftp_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv()
                                        self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor_for_real_devices()
                                        self.ftp_obj_dict[ce][obj_name]["obj"].stop()
                                        self.ftp_done_event.set()
                                        # self.ftp_monitor = False
                                        self.ftp_obj_dict[ce][obj_name]["obj"].update_stop_status_robot()
                                        if test_stopped_by_user_ftp:
                                            break
                                    # if rotation mode
                                    else:
                                        for angle in range(len(self.ftp_obj_dict[ce][obj_name]["obj"].rotation_list)):
                                            test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish_rotation(
                                                coordinate=self.ftp_obj_dict[ce][obj_name]["obj"].coordinate_list[coordinate], angle=self.ftp_obj_dict[ce][obj_name]["obj"].rotation_list[angle])
                                            # If test is stopped by user during battery wait
                                            if test_stopped_by_user:
                                                break
                                            if robo_rotated:
                                                self.ftp_obj_dict[ce][obj_name]["obj"].current_angle = self.ftp_obj_dict[ce][obj_name]["obj"].rotation_list[angle]
                                                # self.ftp_monitor = True
                                                self.ftp_done_event.clear()
                                                self.ftp_rotate_done_event.clear()
                                                self.ftp_rotate.set()
                                                self.check_all_tests()
                                                self.ftp_obj_dict[ce][obj_name]["obj"].start(False, False)
                                                test_stopped_by_user_ftp = self.ftp_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv()
                                                self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor_for_real_devices()
                                                self.ftp_obj_dict[ce][obj_name]["obj"].stop()
                                                self.ftp_done_event.set()
                                                self.ftp_rotate.clear()
                                                self.ftp_rotate_done_event.set()
                                                # self.ftp_monitor = False
                                                self.ftp_obj_dict[ce][obj_name]["obj"].update_stop_status_robot()
                                                # If test is stopped by user
                                                if test_stopped_by_user_ftp:
                                                    break

                    else:
                        self.ftp_obj_dict[ce][obj_name]["obj"].start(False, False)
                        # to fetch runtime values during the execution and fill the csv.
                        if args.dowebgui or args.clients_type == "Real":
                            self.ftp_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv()
                            self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor_for_real_devices()
                        else:
                            time.sleep(args.traffic_duration)
                            self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor()
                        self.ftp_obj_dict[ce][obj_name]["obj"].stop()
                        logger.info("Traffic stopped running")

                    self.ftp_obj_dict[ce][obj_name]["obj"].postcleanup()
                    time2 = datetime.datetime.now()
                    logger.info("Test ended at %s", time2)

        date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

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
        if self.robot_test:
            input_setup_info["Robot IP"] = self.robot_ip
            input_setup_info["Coordinate"] = self.coordinate
            if not self.ftp_obj_dict[ce][obj_name]["obj"].do_bandsteering:
                input_setup_info["Rotation"] = args.rotation
            else:
                input_setup_info["Band Steering Cycles"] = args.cycles
        if args.dowebgui and (not self.robot_test or self.do_bandsteering):
            self.ftp_obj_dict[ce][obj_name]["obj"].data_for_webui["status"] = ["STOPPED"] * len(self.ftp_obj_dict[ce][obj_name]["obj"].url_data)

            df1 = pd.DataFrame(self.ftp_obj_dict[ce][obj_name]["obj"].data_for_webui)
            df1.to_csv('{}/ftp_datavalues.csv'.format(self.ftp_obj_dict[ce][obj_name]["obj"].result_dir), index=False)
            # copying to home directory i.e home/user_name
            # self.ftp_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        # Report generation when groups are specified
        if args.group_name:
            self.ftp_obj_dict[ce][obj_name]["obj"].generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                                                                   test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                                                                   dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                                                                   dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                                                                   bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir, config_devices=configuration, report_path=self.result_path if not self.dowebgui else self.result_dir)  # noqa: E501
        # Generating report without group-specific device configuration
        else:
            self.ftp_obj_dict[ce][obj_name]["obj"].generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                                                                   test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                                                                   dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                                                                   dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                                                                   bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir, report_path=self.result_path if not self.dowebgui else self.result_dir)  # noqa: E501

        params = {
            "ftp_data": ftp_data,
            "date": date,
            "input_setup_info": input_setup_info,
            "test_rig": args.test_rig,
            "test_tag": args.test_tag,
            "dut_hw_version": args.dut_hw_version,
            "dut_sw_version": args.dut_sw_version,
            "dut_model_num": args.dut_model_num,
            "dut_serial_num": args.dut_serial_num,
            "test_id": args.test_id,
            "bands": args.bands,
            "csv_outfile": args.csv_outfile,
            "local_lf_report_dir": args.local_lf_report_dir,
            "report_path": self.result_path
        }

        if args.group_name:
            params["config_devices"] = configuration
        self.ftp_obj_dict[ce][obj_name]["data"] = params.copy()

        if self.dowebgui:
            self.webgui_test_done("ftp")
        return True

    def run_qos_test(
        self,
        device_list=None,
        test_name=None,
        result_dir='',
        upstream_port='eth1',
        security="open",
        ssid=None,
        passwd='[BLANK]',
        traffic_type=None,
        upload=None,
        download=None,
        test_duration="2m",
        ap_name="Test-AP",
        tos=None,
        dowebgui=False,
        debug=False,
        help_summary=False,
        group_name=None,
        profile_name=None,
        file_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        get_live_view=False,
        total_floors="0",
        do_bandsteering=False,
        cycles=None,
        bssids=None,
        duration_to_skip=None
    ):
        """
        Configure and execute a QoS (Quality of Service) throughput test.
        This handles test configuration, client setup, coordinates/rotation if using a robot, and generates a QoS report upon completion.
        """
        dowebgui = True if dowebgui == "True" else False
        if self.dowebgui:
            if not self.webgui_stop_check("qos"):
                return False
        test_results = {'test_results': []}
        loads = {}
        data = {}
        if download and upload:
            loads = {'upload': str(upload).split(","), 'download': str(download).split(",")}
            loads_data = loads["download"]
        elif download:
            loads = {'upload': [], 'download': str(download).split(",")}
            for _i in range(len(download)):
                loads['upload'].append(0)
            loads_data = loads["download"]
        else:
            if upload:
                loads = {'upload': str(upload).split(","), 'download': []}
                for _i in range(len(upload)):
                    loads['download'].append(0)
                loads_data = loads["upload"]
        if download and upload:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_BiDi'
        elif upload:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_UL'
        else:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_DL'

        # validate_args(args)
        if test_duration.endswith('s') or test_duration.endswith('S'):
            test_duration = int(test_duration[0:-1])
        elif test_duration.endswith('m') or test_duration.endswith('M'):
            test_duration = int(test_duration[0:-1]) * 60
        elif test_duration.endswith('h') or test_duration.endswith('H'):
            test_duration = int(test_duration[0:-1]) * 60 * 60
        elif test_duration.endswith(''):
            test_duration = int(test_duration)
        ce = self.current_exec  # seires
        if ce == "parallel":
            obj_name = "qos_test"
        else:
            obj_no = 1
            while f"qos_test_{obj_no}" in self.qos_obj_dict[ce]:
                obj_no += 1
            obj_name = f"qos_test_{obj_no}"
        self.qos_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        for index in range(len(loads_data)):
            self.qos_obj_dict[ce][obj_name]["obj"] = qos_test.ThroughputQOS(host=self.lanforge_ip,
                                                                            ip=self.lanforge_ip,
                                                                            port=self.port,
                                                                            number_template="0000",
                                                                            ap_name=ap_name,
                                                                            name_prefix="TOS-",
                                                                            upstream=upstream_port,
                                                                            ssid=ssid,
                                                                            password=passwd,
                                                                            security=security,
                                                                            test_duration=test_duration,
                                                                            use_ht160=False,
                                                                            side_a_min_rate=int(loads['upload'][index]),
                                                                            side_b_min_rate=int(loads['download'][index]),
                                                                            traffic_type=traffic_type,
                                                                            tos=tos,
                                                                            csv_direction=direction,
                                                                            dowebgui=dowebgui,
                                                                            test_name=test_name,
                                                                            result_dir=result_dir,
                                                                            device_list=device_list,
                                                                            _debug_on=debug,
                                                                            group_name=group_name,
                                                                            profile_name=profile_name,
                                                                            file_name=file_name,
                                                                            eap_method=eap_method,
                                                                            eap_identity=eap_identity,
                                                                            ieee80211=ieee8021x,
                                                                            ieee80211u=ieee80211u,
                                                                            ieee80211w=ieee80211w,
                                                                            enable_pkc=enable_pkc,
                                                                            bss_transition=bss_transition,
                                                                            power_save=power_save,
                                                                            disable_ofdma=disable_ofdma,
                                                                            roam_ft_ds=roam_ft_ds,
                                                                            key_management=key_management,
                                                                            pairwise=pairwise,
                                                                            private_key=private_key,
                                                                            ca_cert=ca_cert,
                                                                            client_cert=client_cert,
                                                                            pk_passwd=pk_passwd,
                                                                            pac_file=pac_file,
                                                                            expected_passfail_val=expected_passfail_value,
                                                                            csv_name=device_csv_name,
                                                                            wait_time=wait_time,
                                                                            config=config,
                                                                            get_live_view=get_live_view,
                                                                            total_floors=total_floors,
                                                                            robot_test=self.robot_test,
                                                                            robot_ip=self.robot_ip,
                                                                            coordinate=self.coordinate,
                                                                            rotation=self.rotation,
                                                                            rotation_enabled=True if self.rotation else False,
                                                                            angle_list=self.rotation.split(",") if self.rotation else [],
                                                                            do_bandsteering=do_bandsteering,
                                                                            cycles=cycles,
                                                                            bssids=bssids,
                                                                            duration_to_skip=duration_to_skip
                                                                            )
            self.qos_obj_dict[ce][obj_name]["obj"].os_type()
            _, configured_device, _, configuration = self.qos_obj_dict[ce][obj_name]["obj"].phantom_check()
            if dowebgui and group_name:
                if len(configured_device) == 0:
                    logger.warning("No device is available to run the test")
                    obj1 = {
                        "status": "Stopped",
                        "configuration_status": "configured"
                    }
                    self.qos_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                    return
                else:
                    obj1 = {
                        "configured_devices": configured_device,
                        "configuration_status": "configured"
                    }
                    self.qos_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
            # checking if we have atleast one device available for running test
            if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui == "True":
                if self.qos_obj_dict[ce][obj_name]["obj"].device_found is False:
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
                        "timestamp": datetime.datetime.now().strftime('%H:%M:%S'),
                        'status': 'Stopped'
                    }]
                    )
                    df1.to_csv('{}/overall_throughput.csv'.format(self.qos_obj_dict[ce][obj_name]["obj"].result_dir), index=False)
                    raise ValueError("Aborting the test....")
            self.qos_obj_dict[ce][obj_name]["obj"].build()
            self.qos_obj_dict[ce][obj_name]["obj"].monitor_cx()
            self.qos_done_event.set()
            if self.robot_test:
                if self.current_exec != "parallel":
                    self.qos_obj_dict[ce][obj_name]["obj"].qos_data["configuration"] = {}
                    self.qos_obj_dict[ce][obj_name]["obj"].dowebgui = True if self.dowebgui else False
                    # self.qos_obj_dict[ce][obj_name]["obj"].result_dir=self.report_path
                    self.qos_obj_dict[ce][obj_name]["obj"].perform_robo()
                else:
                    self.qos_obj_dict[ce][obj_name]["obj"].qos_data["configuration"] = {}
                    self.qos_obj_dict[ce][obj_name]["obj"].dowebgui = True if self.dowebgui else False
                    # self.qos_obj_dict[ce][obj_name]["obj"].result_dir=self.qos_obj_dict[ce][obj_name]["obj"].report_path

                    if (self.qos_obj_dict[ce][obj_name]["obj"].rotation_list[0] != ""):
                        self.qos_obj_dict[ce][obj_name]["obj"].rotation_enabled = True
                    coord_list = []
                    test_stopped_by_user = False
                    if self.qos_obj_dict[ce][obj_name]["obj"].coordinate:
                        coord_list = self.qos_obj_dict[ce][obj_name]["obj"].coordinate_list
                        passed_coord_list = []
                        abort = False
                    for coordinate in coord_list:
                        if self.qos_obj_dict[ce][obj_name]["obj"].robot_ip:
                            if self.qos_obj_dict[ce][obj_name]["obj"].test_stopped_by_user:
                                break
                            test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish(coordinate=coordinate)
                            if test_stopped_by_user:
                                break
                            if abort or not robo_moved:
                                break
                            passed_coord_list.append(coordinate)

                            if robo_moved:
                                self.qos_obj_dict[ce][obj_name]["obj"].overall = []
                                self.qos_obj_dict[ce][obj_name]["obj"].df_for_webui = []
                                # If rotations are not allowed
                                if not self.rotation_enabled:
                                    test_results = {'test_results': []}
                                    data = {}
                                    input_setup_info = {
                                        "contact": "support@candelatech.com"
                                    }
                                    self.qos_obj_dict[ce][obj_name]["obj"].current_coordinate = coordinate
                                    self.qos_done_event.clear()
                                    self.qos_obj_dict[ce][obj_name]["obj"].start(False, False)
                                    time.sleep(10)
                                    connections_download, connections_upload, drop_a_per, drop_b_per, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b = self.qos_obj_dict[ce][obj_name]["obj"].monitor(curr_coordinate=coordinate)  # noqa: E501
                                    logger.info("connections download {}".format(connections_download))
                                    logger.info("connections upload {}".format(connections_upload))
                                    self.qos_obj_dict[ce][obj_name]["obj"].stop()
                                    self.qos_done_event.set()
                                    time.sleep(5)
                                    test_results['test_results'].append(self.qos_obj_dict[ce][obj_name]["obj"].evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                                    data.update(test_results)
                                    params = {
                                        "data": None,
                                        "input_setup_info": None,
                                        "connections_download_avg": None,
                                        "connections_upload_avg": None,
                                        "avg_drop_a": None,
                                        "avg_drop_b": None,
                                        "report_path": "",
                                        "result_dir_name": "Qos_Test_report",
                                        "selected_real_clients_names": None,
                                        "config_devices": ""
                                    }

                                    params.update({
                                        "data": data,
                                        "input_setup_info": input_setup_info,
                                        "report_path": (
                                            self.qos_obj_dict[ce][obj_name]["obj"].result_dir
                                            if self.dowebgui else ""
                                        ),
                                        "connections_upload_avg": connections_upload_avg,
                                        "connections_download_avg": connections_download_avg,
                                        "avg_drop_a": avg_drop_a,
                                        "avg_drop_b": avg_drop_b
                                    })
                                    self.qos_obj_dict[ce][obj_name]["obj"].qos_data[coordinate] = params

                                # If rotations are enabled
                                else:
                                    self.qos_rotate_done_event.set()
                                    for angle in range(len(self.qos_obj_dict[ce][obj_name]["obj"].rotation_list)):
                                        test_results = {'test_results': []}
                                        data = {}
                                        input_setup_info = {
                                            "contact": "support@candelatech.com"
                                        }
                                        self.qos_obj_dict[ce][obj_name]["obj"].last_rotated_angles = []
                                        self.qos_obj_dict[ce][obj_name]["obj"].current_coordinate = coordinate
                                        self.qos_obj_dict[ce][obj_name]["obj"].current_angle = self.qos_obj_dict[ce][obj_name]["obj"].angle_list[angle]
                                        # pause_angle, test_stopped_by_user = self.robot.wait_for_battery(battery=40,stop=self.stop)
                                        test_stopped_by_user, robo_moved, abort, robo_rotated = self.wait_for_all_tests_to_finish_rotation(coordinate=coordinate, angle=self.rotation_list[angle])
                                        if test_stopped_by_user:
                                            break

                                        final_angle = self.qos_obj_dict[ce][obj_name]["obj"].angle_list[angle]
                                        if robo_rotated:
                                            if final_angle not in self.qos_obj_dict[ce][obj_name]["obj"].last_rotated_angles:
                                                self.qos_obj_dict[ce][obj_name]["obj"].last_rotated_angles.append(final_angle)
                                            self.qos_done_event.clear()
                                            self.qos_rotate_done_event.clear()
                                            self.qos_rotate.set()
                                            self.check_all_tests()
                                            self.qos_obj_dict[ce][obj_name]["obj"].start(False, False)
                                            monitor_charge_time = datetime.datetime.now()
                                            (
                                                connections_download,
                                                connections_upload,
                                                drop_a_per,
                                                drop_b_per,
                                                connections_download_avg,
                                                connections_upload_avg,
                                                avg_drop_a,
                                                avg_drop_b,
                                            ) = self.qos_obj_dict[ce][obj_name]["obj"].monitor(
                                                curr_coordinate=coordinate,
                                                curr_rotation=self.qos_obj_dict[ce][obj_name]["obj"].current_angle,
                                                monitor_charge_time=monitor_charge_time,
                                            )
                                            logger.info("connections download {}".format(connections_download))
                                            logger.info("connections upload {}".format(connections_upload))
                                            self.qos_obj_dict[ce][obj_name]["obj"].stop()
                                            self.qos_done_event.set()
                                            self.qos_rotate.clear()
                                            self.qos_rotate_done_event.set()
                                            time.sleep(5)
                                            test_results['test_results'].append(self.qos_obj_dict[ce][obj_name]["obj"].evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                                            data.update(test_results)
                                            params = {
                                                "data": None,
                                                "input_setup_info": None,
                                                "connections_download_avg": None,
                                                "connections_upload_avg": None,
                                                "avg_drop_a": None,
                                                "avg_drop_b": None,
                                                "report_path": "",
                                                "result_dir_name": "Qos_Test_report",
                                                "selected_real_clients_names": None,
                                                "config_devices": ""
                                            }

                                            params.update({
                                                "data": data,
                                                "input_setup_info": input_setup_info,
                                                "report_path": (
                                                    self.result_dir
                                                    if self.dowebgui else ""
                                                ),
                                                "connections_upload_avg": connections_upload_avg,
                                                "connections_download_avg": connections_download_avg,
                                                "avg_drop_a": avg_drop_a,
                                                "avg_drop_b": avg_drop_b
                                            })
                                            if coordinate not in self.qos_obj_dict[ce][obj_name]["obj"].qos_data:
                                                self.qos_obj_dict[ce][obj_name]["obj"].qos_data[coordinate] = {}
                                            self.qos_obj_dict[ce][obj_name]["obj"].qos_data[coordinate][self.rotation_list[angle]] = params

                    self.qos_obj_dict[ce][obj_name]["obj"].generate_report_for_robo(coordinate_list=coord_list, angle_list=self.rotation_list, passed_coordinates=passed_coord_list)
                    if self.dowebgui:
                        self.webgui_test_done("qos")
                return True
            self.qos_obj_dict[ce][obj_name]["obj"].start(False, False)
            time.sleep(10)
            connections_download, connections_upload, drop_a_per, drop_b_per, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b = self.qos_obj_dict[ce][obj_name]["obj"].monitor(
            )
            logger.info("connections download {}".format(connections_download))
            logger.info("connections upload {}".format(connections_upload))
            self.qos_obj_dict[ce][obj_name]["obj"].stop()
            time.sleep(5)
            test_results['test_results'].append(self.qos_obj_dict[ce][obj_name]["obj"].evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
            data.update(test_results)
        test_end_time = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
        logger.info(f"Test ended at: {test_end_time}")

        input_setup_info = {
            "contact": "support@candelatech.com"
        }
        self.qos_obj_dict[ce][obj_name]["obj"].cleanup()

        # Update webgui running json with latest entry and test status completed
        if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui == "True":
            last_entry = self.qos_obj_dict[ce][obj_name]["obj"].overall[len(self.qos_obj_dict[ce][obj_name]["obj"].overall) - 1]
            last_entry["status"] = "Stopped"
            last_entry["timestamp"] = datetime.datetime.now().strftime("%d/%m %I:%M:%S %p")
            last_entry["remaining_time"] = "0"
            last_entry["end_time"] = last_entry["timestamp"]
            self.qos_obj_dict[ce][obj_name]["obj"].df_for_webui.append(
                last_entry
            )
            df1 = pd.DataFrame(self.qos_obj_dict[ce][obj_name]["obj"].df_for_webui)
            df1.to_csv('{}/overall_throughput.csv'.format(result_dir, ), index=False)

            # copying to home directory i.e home/user_name
            self.qos_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        if group_name:
            self.qos_obj_dict[ce][obj_name]["obj"].generate_report(
                data=data,
                input_setup_info=input_setup_info,
                report_path=self.qos_obj_dict[ce][obj_name]["obj"].result_dir if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path,
                connections_upload_avg=connections_upload_avg,
                connections_download_avg=connections_download_avg,
                avg_drop_a=avg_drop_a,
                avg_drop_b=avg_drop_b, config_devices=configuration)
        else:
            self.qos_obj_dict[ce][obj_name]["obj"].generate_report(
                data=data,
                input_setup_info=input_setup_info,
                report_path=self.qos_obj_dict[ce][obj_name]["obj"].result_dir if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path,
                connections_upload_avg=connections_upload_avg,
                connections_download_avg=connections_download_avg,
                avg_drop_a=avg_drop_a,
                avg_drop_b=avg_drop_b)
        params = {
            "data": None,
            "input_setup_info": None,
            "connections_download_avg": None,
            "connections_upload_avg": None,
            "avg_drop_a": None,
            "avg_drop_b": None,
            "report_path": "",
            "result_dir_name": "Qos_Test_report",
            "selected_real_clients_names": None,
            "config_devices": ""
        }

        params.update({
            "data": data,
            "input_setup_info": input_setup_info,
            "report_path": (
                self.qos_obj_dict[ce][obj_name]["obj"].result_dir
                if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path
            ),
            "connections_upload_avg": connections_upload_avg,
            "connections_download_avg": connections_download_avg,
            "avg_drop_a": avg_drop_a,
            "avg_drop_b": avg_drop_b
        })

        if group_name:
            params["config_devices"] = configuration
        self.qos_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("qos")
        return True

    def run_vs_test(self, args):
        """
        Execute a Video Streaming (VS) test across specified devices.
        This handles test configuration, Android client coordination, and generates a video streaming report.
        """
        if self.dowebgui:
            if not self.webgui_stop_check("vs"):
                return False
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

        if args.file_name:
            args.file_name = args.file_name.removesuffix('.csv')

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
        ce = self.current_exec  # seires
        if ce == "parallel":
            obj_name = "vs_test"
        else:
            obj_no = 1
            while f"vs_test_{obj_no}" in self.vs_obj_dict[ce]:
                obj_no += 1
            obj_name = f"vs_test_{obj_no}"
        self.vs_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        self.vs_obj_dict[ce][obj_name]["obj"] = VideoStreamingTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                                                                   suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                                                                   url=args.url, urls_per_tenm=args.urls_per_tenm, duration=args.duration,
                                                                   resource_ids=args.device_list, dowebgui=args.dowebgui, media_quality=args.media_quality, media_source=args.media_source,
                                                                   result_dir=args.result_dir, test_name=args.test_name, incremental=args.incremental, postcleanup=args.postcleanup,
                                                                   precleanup=args.precleanup,
                                                                   pass_fail_val=args.expected_passfail_value,
                                                                   csv_name=args.device_csv_name,
                                                                   groups=args.group_name,
                                                                   profiles=args.profile_name,
                                                                   config=args.config,
                                                                   file_name=args.file_name,
                                                                   floors=args.floors,
                                                                   get_live_view=args.get_live_view,

                                                                   # for robot execution
                                                                   robot_test=self.robot_test,
                                                                   robot_ip=self.robot_ip,
                                                                   coordinate=self.coordinate,
                                                                   rotation=self.rotation,
                                                                   rotation_enabled=True if self.rotation else False,
                                                                   angle_list=self.rotation.split(",") if self.rotation else [],
                                                                   do_bandsteering=args.do_bandsteering,
                                                                   total_cycles=args.total_cycles,
                                                                   bssids=args.bssids.split(",") if args.bssids else [],
                                                                   duration_to_skip=args.duration_to_skip
                                                                   )
        args.upstream_port = self.vs_obj_dict[ce][obj_name]["obj"].change_port_to_ip(args.upstream_port)
        self.vs_obj_dict[ce][obj_name]["obj"].validate_args()
        config_obj = DeviceConfig.DeviceConfig(lanforge_ip=args.host, file_name=args.file_name)
        # if not args.expected_passfail_value and args.device_csv_name is None:
        #     config_obj.device_csv_file(csv_name="device.csv")

        resource_ids_sm = []
        resource_set = set()
        resource_list = []
        resource_ids_generated = ""

        if args.group_name and args.file_name and args.profile_name:
            selected_groups = args.group_name.split(',')
            selected_profiles = args.profile_name.split(',')
            config_devices = {}
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]
            config_obj.initiate_group()
            asyncio.run(config_obj.connectivity(config_devices, upstream=args.upstream_port))

            adbresponse = config_obj.adb_obj.get_devices()
            resource_manager = config_obj.laptop_obj.get_devices()
            all_res = {}
            df1 = config_obj.display_groups(config_obj.groups)
            groups_list = df1.to_dict(orient='list')
            group_devices = {}
            for adb in adbresponse:
                group_devices[adb['serial']] = adb['eid']
            for res in resource_manager:
                all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
            eid_list = []
            for grp_name in groups_list.keys():
                for g_name in selected_groups:
                    if grp_name == g_name:
                        for j in groups_list[grp_name]:
                            if j in group_devices.keys():
                                eid_list.append(group_devices[j])
                            elif j in all_res.keys():
                                eid_list.append(all_res[j])
            args.device_list = ",".join(id for id in eid_list)
        else:
            # When group/profile are not provided
            config_dict = {
                'ssid': args.ssid,
                'passwd': args.passwd,
                'enc': args.encryp,
                'eap_method': args.eap_method,
                'eap_identity': args.eap_identity,
                'ieee80211': args.ieee8021x,
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
                'server_ip': args.upstream_port
            }
            if args.device_list:
                all_devices = config_obj.get_all_devices()
                if args.group_name is None and args.file_name is None and args.profile_name is None:
                    dev_list = args.device_list.split(',')
                    if args.config:
                        asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
            else:
                if args.config:
                    all_devices = config_obj.get_all_devices()
                    device_list = []
                    for device in all_devices:
                        if device["type"] != 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                        elif device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                    logger.info("Available devices:")
                    for device in device_list:
                        logger.info(device)
                    args.device_list = input("Enter the desired resources to run the test:")
                    dev1_list = args.device_list.split(',')
                    asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))
                else:
                    self.vs_obj_dict[ce][obj_name]["obj"].android_devices = self.vs_obj_dict[ce][obj_name]["obj"].devices.get_devices(only_androids=True)
                    selected_devices, report_labels, selected_macs = self.vs_obj_dict[ce][obj_name]["obj"].devices.query_user()
                    if not selected_devices:
                        logging.info("devices donot exist..!!")
                        return

                    self.vs_obj_dict[ce][obj_name]["obj"].android_list = selected_devices
                    # Verify if all resource IDs are valid for Android devices
                    if self.vs_obj_dict[ce][obj_name]["obj"].android_list:
                        resource_ids = ",".join([item.split(".")[1] for item in self.vs_obj_dict[ce][obj_name]["obj"].android_list])

                        num_list = list(map(int, resource_ids.split(',')))

                        # Sort the list
                        num_list.sort()

                        # Join the sorted list back into a string
                        sorted_string = ','.join(map(str, num_list))

                        self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = sorted_string
                        resource_ids1 = list(map(int, sorted_string.split(',')))
                        modified_list = list(map(lambda item: int(item.split('.')[1]), self.vs_obj_dict[ce][obj_name]["obj"].android_devices))
                        if not all(x in modified_list for x in resource_ids1):
                            logging.info("Verify Resource ids, as few are invalid...!!")
                            return False
                        resource_ids_sm = self.vs_obj_dict[ce][obj_name]["obj"].resource_ids
                        resource_list = resource_ids_sm.split(',')
                        resource_set = set(resource_list)
                        resource_list_sorted = sorted(resource_set)
                        resource_ids_generated = ','.join(resource_list_sorted)
                        available_resources = list(resource_set)

        if args.dowebgui:
            resource_ids_sm = args.device_list.split(',')
            resource_set = set(resource_ids_sm)
            resource_list = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list)
            resource_list_sorted = resource_list
            selected_devices, report_labels, selected_macs = self.vs_obj_dict[ce][obj_name]["obj"].devices.query_user(dowebgui=args.dowebgui, device_list=resource_ids_generated)
            self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = ",".join(id.split(".")[1] for id in args.device_list.split(","))
            available_resources = [int(num) for num in self.vs_obj_dict[ce][obj_name]["obj"].resource_ids.split(',')]
        else:
            self.vs_obj_dict[ce][obj_name]["obj"].android_devices = self.vs_obj_dict[ce][obj_name]["obj"].devices.get_devices(only_androids=True)
            if args.device_list:
                device_list = args.device_list.split(',')
                # Extract resource IDs (after the dot), remove duplicates, and sort them
                resource_ids = sorted(set(int(item.split('.')[1]) for item in device_list if '.' in item))
                resource_list_sorted = resource_ids
                self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = ','.join(map(str, resource_ids))
                # Create a set of Android device IDs (e.g., "resource.123")
                android_device_ids = set(self.vs_obj_dict[ce][obj_name]["obj"].android_devices)
                android_device_short_ids = {device.split('.')[0] + '.' + device.split('.')[1] for device in android_device_ids}
                self.vs_obj_dict[ce][obj_name]["obj"].android_list = [dev for dev in android_device_short_ids if dev in device_list]
                # Log any devices in the list that are not available
                for dev in device_list:
                    if dev not in android_device_short_ids:
                        logger.info(f"{dev} device is not available")
                # Final list of available Android resource IDs
                available_resources = sorted(set(int(dev.split('.')[1]) for dev in self.vs_obj_dict[ce][obj_name]["obj"].android_list))
                logger.info(f"Available devices: {available_resources}")
        if len(available_resources) != 0:
            available_resources = self.vs_obj_dict[ce][obj_name]["obj"].filter_ios_devices(available_resources)
        if len(available_resources) == 0:
            logger.info("No devices which are selected are available in the lanforge")
            return False
        gave_incremental = False
        if args.incremental and not args.webgui_incremental:
            if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
                logging.info("The total available devices are {}".format(len(available_resources)))
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = input('Specify incremental values as 1,2,3 : ')
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = [int(x) for x in self.vs_obj_dict[ce][obj_name]["obj"].incremental.split(',')]
            else:
                logging.info("incremental Values are not needed as Android devices are not selected..")
        elif not args.incremental:
            gave_incremental = True
            self.vs_obj_dict[ce][obj_name]["obj"].incremental = [len(available_resources)]

        if args.webgui_incremental:
            incremental = [int(x) for x in args.webgui_incremental.split(',')]
            if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = incremental

        if self.vs_obj_dict[ce][obj_name]["obj"].incremental and self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental[-1] > len(available_resources):
                logging.info("Exiting the program as incremental values are greater than the resource ids provided")
                return False
            elif self.vs_obj_dict[ce][obj_name]["obj"].incremental[-1] < len(available_resources) and len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) > 1:
                logging.info("Exiting the program as the last incremental value must be equal to selected devices")
                return False

        # To create cx for selected devices
        self.vs_obj_dict[ce][obj_name]["obj"].build()

        # To set media source and media quality
        time.sleep(10)

        # self.vs_obj_dict[ce][obj_name]["obj"].run
        test_time = datetime.datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logging.info("Initiating Test...")

        individual_dataframe_columns = []

        keys = list(self.vs_obj_dict[ce][obj_name]["obj"].http_profile.created_cx.keys())

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
                f'Video Quality_{keys[i]}',
                f'BSSID_{keys[i]}',
                f'Channel_{keys[i]}',
            ])

        individual_dataframe_columns.extend(['overall_video_format_bitrate', 'timestamp', 'iteration', 'start_time', 'end_time', 'remaining_Time', 'status'])
        if self.robot_test and args.do_bandsteering:
            individual_dataframe_columns.extend(['Robot X', 'Robot Y', 'From Coordinate', 'To Coordinate'])
        elif self.robot_test and args.rotation:
            individual_dataframe_columns.append('angle')
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

        incremental_capacity_list_values = self.vs_obj_dict[ce][obj_name]["obj"].get_incremental_capacity_list()
        self.vs_obj_dict[ce][obj_name]["obj"].process_incremental_capacity(incremental_capacity_list_values, available_resources, gave_incremental)
        if incremental_capacity_list_values[-1] != len(available_resources):
            logger.error("Incremental capacity doesnt match available devices")
            if args.postcleanup:
                self.vs_obj_dict[ce][obj_name]["obj"].postcleanup()
            return False
        # Process resource IDs and incremental values if specified
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental:
                test_setup_info_incremental_values = ','.join([str(n) for n in incremental_capacity_list_values])
                if len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == len(available_resources):
                    test_setup_info_total_duration = args.duration
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and len(available_resources) > 1:
                    if self.vs_obj_dict[ce][obj_name]["obj"].incremental[0] == len(available_resources):
                        test_setup_info_total_duration = args.duration
                    else:
                        div = len(available_resources) // self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
                        mod = len(available_resources) % self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
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
            self.vs_obj_dict[ce][obj_name]["obj"].total_duration = test_setup_info_total_duration

        actual_start_time = datetime.datetime.now()

        iterations_before_test_stopped_by_user = []

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            # Check if incremental  is specified
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental:

                # Case 1: Incremental list has only one value and it equals the length of keys
                if len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and self.vs_obj_dict[ce][obj_name]["obj"].incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])

                # Case 2: Incremental list has only one value but length of keys is greater than 1
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and len(keys) > 1:
                    incremental_value = self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index

                # Case 3: Incremental list has multiple values and length of keys is greater than 1
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) != 1 and len(keys) > 1:

                    index = 0
                    for num in self.vs_obj_dict[ce][obj_name]["obj"].incremental:

                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])

                # Iterate over cx_order_list to start tests incrementally
                for i in range(len(cx_order_list)):
                    if i == 0:
                        if self.robot_test:
                            self.vs_obj_dict[ce][obj_name]["obj"].perform_robo(args, individual_dataframe_columns, cx_order_list, i, actual_start_time, iterations_before_test_stopped_by_user)

                            return True
                        self.vs_obj_dict[ce][obj_name]["obj"].data["start_time_webGUI"] = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        end_time_webGUI = (datetime.datetime.now() + datetime.timedelta(minutes=self.vs_obj_dict[ce][obj_name]["obj"].total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        self.vs_obj_dict[ce][obj_name]["obj"].data['end_time_webGUI'] = [end_time_webGUI]

                    # time.sleep(10)

                    # Start specific devices based on incremental capacity
                    self.vs_obj_dict[ce][obj_name]["obj"].start_specific(cx_order_list[i])
                    if cx_order_list[i]:
                        logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                    else:
                        logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                    file_path = "video_streaming_realtime_data.csv"
                    if end_time_webGUI < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        self.vs_obj_dict[ce][obj_name]["obj"].data['remaining_time_webGUI'] = ['0:00']
                    else:
                        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.vs_obj_dict[ce][obj_name]["obj"].data['remaining_time_webGUI'] = [datetime.datetime.strptime(
                            end_time_webGUI, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")]

                    if args.dowebgui:
                        file_path = os.path.join(self.vs_obj_dict[ce][obj_name]["obj"].result_dir,
                                                 "../../Running_instances/{}_{}_running.json".format(self.vs_obj_dict[ce][obj_name]["obj"].host,
                                                                                                     self.vs_obj_dict[ce][obj_name]["obj"].test_name))
                        if os.path.exists(file_path):
                            with open(file_path, 'r') as file:
                                data = json.load(file)
                                if data["status"] != "Running":
                                    break
                        test_stopped_by_user = self.vs_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(
                            args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                    else:
                        test_stopped_by_user = self.vs_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(
                            args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                    if not test_stopped_by_user:
                        # Append current iteration index to iterations_before_test_stopped_by_user
                        iterations_before_test_stopped_by_user.append(i)
                    else:
                        # Append current iteration index to iterations_before_test_stopped_by_user
                        iterations_before_test_stopped_by_user.append(i)
                        break
        self.vs_obj_dict[ce][obj_name]["obj"].stop()

        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:

            date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            username = []

            try:
                eid_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
            except KeyError:
                logger.error("Error: 'interfaces' key not found in port data")
                return False

            resource_ids = list(map(int, self.vs_obj_dict[ce][obj_name]["obj"].resource_ids.split(',')))
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
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
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids and self.vs_obj_dict[ce][obj_name]["obj"].incremental:
            self.vs_obj_dict[ce][obj_name]["obj"].generate_report(
                date,
                list(
                    set(iterations_before_test_stopped_by_user)),
                test_setup_info=test_setup_info,
                realtime_dataset=individual_df,
                report_path=self.result_path if not self.dowebgui else self.result_dir)
        elif self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            self.vs_obj_dict[ce][obj_name]["obj"].generate_report(
                date,
                list(
                    set(iterations_before_test_stopped_by_user)),
                test_setup_info=test_setup_info,
                realtime_dataset=individual_df,
                report_path=self.result_path if not self.dowebgui else self.result_dir)

        params = {
            "date": None,
            "iterations_before_test_stopped_by_user": None,
            "test_setup_info": None,
            "realtime_dataset": None,
            "report_path": "",
            "cx_order_list": []
        }
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids and self.vs_obj_dict[ce][obj_name]["obj"].incremental:
            params.update({
                "date": date,
                "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
                "test_setup_info": test_setup_info,
                "realtime_dataset": individual_df,
                "report_path": self.result_path,
                "cx_order_list": cx_order_list
            })
        elif self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            params.update({
                "date": date,
                "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
                "test_setup_info": test_setup_info,
                "realtime_dataset": individual_df,
                "report_path": self.result_path
            })
        self.vs_obj_dict[ce][obj_name]["data"] = params.copy()
        # Perform post-cleanup operations
        if args.postcleanup:
            self.vs_obj_dict[ce][obj_name]["obj"].postcleanup()

        if args.dowebgui:
            self.vs_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
            self.webgui_test_done("vs")
        return True

    def run_vs_test1(
        self,
        ssid=None,
        passwd="something",
        encryp="psk",
        url="www.google.com",
        max_speed=0,
        urls_per_tenm=100,
        duration=None,
        test_name="video_streaming_test",
        dowebgui=False,
        result_dir='',
        lf_logger_config_json=None,
        log_level=None,
        debug=False,
        media_source='1',
        media_quality='0',
        device_list=None,
        webgui_incremental=None,
        incremental=False,
        no_laptops=True,
        postcleanup=False,
        precleanup=False,
        help_summary=False,
        group_name=None,
        profile_name=None,
        file_name=None,
        eap_method='DEFAULT',
        eap_identity='DEFAULT',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        upstream_port='NA',
        expected_passfail_value=None,
        csv_name=None,
        wait_time=60,
        config=False,
        device_csv_name=None,
        get_live_view=False,
        floors=0,
        do_bandsteering=False,
        total_cycles=1,
        bssids=None,
        duration_to_skip=None,
    ):
        """
        Configure and execute a Video Streaming test.
        This handles argument processing and delegates execution to `run_vs_test`.
        """
        args = SimpleNamespace(**locals())
        args.host = self.lanforge_ip
        return self.run_vs_test(args)

    def run_throughput_test(
        self,
        device_list=None,
        upstream_port='eth1',
        ssid=None,
        passwd='[BLANK]',
        traffic_type=None,
        upload='2560',
        download='2560',
        test_duration='',
        report_timer='1s',
        ap_name='Test-AP',
        dowebgui=False,
        tos='Best_Efforts',
        packet_size='-1',
        incremental_capacity=None,
        load_type='wc_per_client_load',
        do_interopability=False,
        postcleanup=False,
        precleanup=False,
        incremental=False,
        security='open',
        test_name=None,
        result_dir='',
        get_live_view=False,
        total_floors='0',
        expected_passfail_value=None,
        device_csv_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        file_name=None,
        group_name=None,
        profile_name=None,
        wait_time=60,
        config=False,
        default_config=True,
        tput_mbps=False,
        help_summary=False,
        do_bandsteering=False,
        total_cycles=1,
        bssids=None,
        duration_to_skip=None
    ):
        """
        Configure and execute a Throughput test.
        This handles test parameters setup, client configuration, and coordinates execution either locally or using a robot.
        """
        device_list = [] if device_list is None else device_list
        incremental_capacity = [] if incremental_capacity is None else incremental_capacity
        if dowebgui:
            if (upload == '0'):
                upload = '2560'
            if (download == '0'):
                download = '2560'
        if self.dowebgui:
            if not self.webgui_stop_check("thput"):
                return False

        lf_logger_config.lf_logger_config()

        if (tput_mbps):
            if download != '2560' and download != '0' and upload != '0' and upload != '2560':
                download = str(int(download) * 1000000)
                upload = str(int(upload) * 1000000)
            elif upload != '2560' and upload != '0':
                upload = str(int(upload) * 1000000)
            else:
                download = str(int(download) * 1000000)
        loads = {}
        iterations_before_test_stopped_by_user = []
        gave_incremental = False
        # Case based on download and upload arguments are provided
        if download and upload:
            loads = {'upload': str(upload).split(","), 'download': str(download).split(",")}
            loads_data = loads["download"]
        elif download:
            loads = {'upload': [], 'download': str(download).split(",")}
            for _i in range(len(download)):
                loads['upload'].append(2560)
            loads_data = loads["download"]
        else:
            if upload:
                loads = {'upload': str(upload).split(","), 'download': []}
                for _i in range(len(upload)):
                    loads['download'].append(2560)
                loads_data = loads["upload"]

        if download != '2560' and download != '0' and upload != '0' and upload != '2560':
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_BiDi'
        elif upload != '2560' and upload != '0':
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_UL'
        else:
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_DL'

        # validate_args(args)
        if incremental_capacity == 'no_increment' and dowebgui:
            incremental_capacity = str(len(device_list.split(",")))
            gave_incremental = True

        if do_interopability:
            incremental_capacity = "1"

        # Parsing test_duration
        if test_duration.endswith('s') or test_duration.endswith('S'):
            test_duration = int(test_duration[0:-1])

        elif test_duration.endswith('m') or test_duration.endswith('M'):
            test_duration = int(test_duration[0:-1]) * 60

        elif test_duration.endswith('h') or test_duration.endswith('H'):
            test_duration = int(test_duration[0:-1]) * 60 * 60

        elif test_duration.endswith(''):
            test_duration = int(test_duration)

        # Parsing report_timer
        if report_timer.endswith('s') or report_timer.endswith('S'):
            report_timer = int(report_timer[0:-1])

        elif report_timer.endswith('m') or report_timer.endswith('M'):
            report_timer = int(report_timer[0:-1]) * 60

        elif report_timer.endswith('h') or report_timer.endswith('H'):
            report_timer = int(report_timer[0:-1]) * 60 * 60

        elif test_duration.endswith(''):
            report_timer = int(report_timer)
        if (int(packet_size) < 16 or int(packet_size) > 65507) and int(packet_size) != -1:
            logger.error("Packet size should be greater than 16 bytes and less than 65507 bytes incorrect")
            return
        ce = self.current_exec  # series
        if ce == "parallel":
            obj_name = "thput_test"
        else:
            obj_no = 1
            while f"thput_test_{obj_no}" in self.thput_obj_dict[ce]:
                obj_no += 1
            obj_name = f"thput_test_{obj_no}"
        self.thput_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        for index in range(len(loads_data)):
            self.thput_obj_dict[ce][obj_name]["obj"] = Throughput(host=self.lanforge_ip,
                                                                  ip=self.lanforge_ip,
                                                                  port=self.port,
                                                                  number_template="0000",
                                                                  ap_name=ap_name,
                                                                  name_prefix="TOS-",
                                                                  upstream=upstream_port,
                                                                  ssid=ssid,
                                                                  password=passwd,
                                                                  security=security,
                                                                  test_duration=test_duration,
                                                                  use_ht160=False,
                                                                  side_a_min_rate=int(loads['upload'][index]),
                                                                  side_b_min_rate=int(loads['download'][index]),
                                                                  side_a_min_pdu=int(packet_size),
                                                                  side_b_min_pdu=int(packet_size),
                                                                  traffic_type=traffic_type,
                                                                  tos=tos,
                                                                  dowebgui=dowebgui,
                                                                  test_name=test_name,
                                                                  result_dir=result_dir,
                                                                  device_list=device_list,
                                                                  incremental_capacity=incremental_capacity,
                                                                  report_timer=report_timer,
                                                                  load_type=load_type,
                                                                  do_interopability=do_interopability,
                                                                  incremental=incremental,
                                                                  precleanup=precleanup,
                                                                  get_live_view=get_live_view,
                                                                  total_floors=total_floors,
                                                                  csv_direction=csv_direction,
                                                                  expected_passfail_value=expected_passfail_value,
                                                                  device_csv_name=device_csv_name,
                                                                  file_name=file_name,
                                                                  group_name=group_name,
                                                                  profile_name=profile_name,
                                                                  eap_method=eap_method,
                                                                  eap_identity=eap_identity,
                                                                  ieee80211=ieee8021x,
                                                                  ieee80211u=ieee80211u,
                                                                  ieee80211w=ieee80211w,
                                                                  enable_pkc=enable_pkc,
                                                                  bss_transition=bss_transition,
                                                                  power_save=power_save,
                                                                  disable_ofdma=disable_ofdma,
                                                                  roam_ft_ds=roam_ft_ds,
                                                                  key_management=key_management,
                                                                  pairwise=pairwise,
                                                                  private_key=private_key,
                                                                  ca_cert=ca_cert,
                                                                  client_cert=client_cert,
                                                                  pk_passwd=pk_passwd,
                                                                  pac_file=pac_file,
                                                                  wait_time=wait_time,
                                                                  config=config,
                                                                  interopability_config=default_config,

                                                                  # for Robot execution
                                                                  rotation_enabled=True if self.rotation else False,
                                                                  robo_ip=self.robot_ip,
                                                                  coordinate_list=self.coordinate.split(",") if self.coordinate else [],
                                                                  angle_list=self.rotation.split(",") if self.rotation else [],
                                                                  # for bandsteering
                                                                  do_bandsteering=do_bandsteering,
                                                                  total_cycles=total_cycles if total_cycles else 1,
                                                                  bssids=bssids if bssids else None,
                                                                  duration_to_skip=duration_to_skip if duration_to_skip else None,
                                                                  )

            if gave_incremental:
                self.thput_obj_dict[ce][obj_name]["obj"].gave_incremental = True
            self.thput_obj_dict[ce][obj_name]["obj"].os_type()

            check_condition, clients_to_run = self.thput_obj_dict[ce][obj_name]["obj"].phantom_check()

            if not check_condition:
                return

            check_increment_condition = self.thput_obj_dict[ce][obj_name]["obj"].check_incremental_list()

            if not check_increment_condition:
                logger.error("Incremental values given for selected devices are incorrect")
                return

            elif (len(incremental_capacity) > 0 and not check_increment_condition):
                logger.error("Incremental values given for selected devices are incorrect")
                return

            created_cxs = self.thput_obj_dict[ce][obj_name]["obj"].build()
            time.sleep(10)
            created_cxs = list(created_cxs.keys())

            # To execute the throughput test using ROBO
            if self.robot_test:
                self.thput_obj_dict[ce][obj_name]["obj"].postcleanup = True
                self.thput_obj_dict[ce][obj_name]["obj"].coordinate = self.thput_obj_dict[ce][obj_name]["obj"].coordinate_list
                self.thput_obj_dict[ce][obj_name]["obj"].mgr = self.thput_obj_dict[ce][obj_name]["obj"].ip
                self.thput_obj_dict[ce][obj_name]["obj"].perform_robo(self.thput_obj_dict[ce][obj_name]["obj"], clients_to_run)
                params = {
                    "iterations_before_test_stopped_by_user": list(set(self.thput_obj_dict[ce][obj_name]["obj"].base_class_iterations_data)),
                    "incremental_capacity_list": self.thput_obj_dict[ce][obj_name]["obj"].base_class_incremental_capacity_list,
                    "data": self.thput_obj_dict[ce][obj_name]["obj"].base_class_all_dataframes,
                    "data1": self.thput_obj_dict[ce][obj_name]["obj"].base_class_to_run_cxs_len,
                    "report_path": self.result_path if not self.thput_obj_dict[ce][obj_name]["obj"].dowebgui else self.thput_obj_dict[ce][obj_name]["obj"].result_dir
                }
                self.thput_obj_dict[ce][obj_name]["data"] = params.copy()
                if self.dowebgui:
                    self.webgui_test_done("thput")
                return True

            individual_dataframe_column = []

            to_run_cxs, to_run_cxs_len, created_cx_lists_keys, incremental_capacity_list = self.thput_obj_dict[ce][obj_name]["obj"].get_incremental_capacity_list()

            for i in range(len(clients_to_run)):

                # Extend individual_dataframe_column with dynamically generated column names
                individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop  {clients_to_run[i]}',
                                                    f'Tx % Drop{clients_to_run[i]}', f'Average RTT {clients_to_run[i]} ', f'RSSI {clients_to_run[i]} ', f'Tx-Rate {clients_to_run[i]} ',
                                                    f'Rx-Rate {clients_to_run[i]} ', f'BSSID {clients_to_run[i]}', f'Channel {clients_to_run[i]}'])

            individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop ', 'Overall Tx % Drop', 'Iteration',
                                                'TIMESTAMP', 'Start_time', 'End_time', 'Remaining_Time', 'Incremental_list', 'status'])
            individual_df = pd.DataFrame(columns=individual_dataframe_column)

            overall_start_time = datetime.datetime.now()
            overall_end_time = overall_start_time + datetime.timedelta(seconds=int(test_duration) * len(incremental_capacity_list))

            for i in range(len(to_run_cxs)):
                is_device_configured = True
                if do_interopability:
                    # To get resource of device under test in interopability
                    device_to_run_resource = self.thput_obj_dict[ce][obj_name]["obj"].extract_digits_until_alpha(to_run_cxs[i][0])

                # Check the load type specified by the user
                if load_type == "wc_intended_load":
                    # Perform intended load for the current iteration
                    self.thput_obj_dict[ce][obj_name]["obj"].perform_intended_load(i, incremental_capacity_list)
                    if i != 0:

                        # Stop throughput testing if not the first iteration
                        self.thput_obj_dict[ce][obj_name]["obj"].stop()

                    # Start specific connections for the current iteration
                    self.thput_obj_dict[ce][obj_name]["obj"].start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
                else:
                    if (do_interopability and i != 0):
                        self.thput_obj_dict[ce][obj_name]["obj"].stop_specific(to_run_cxs[i - 1])
                        time.sleep(5)
                    if not default_config:
                        if (do_interopability and i == 0):
                            self.thput_obj_dict[ce][obj_name]["obj"].disconnect_all_devices()
                        if do_interopability and "iOS" not in to_run_cxs[i][0]:
                            logger.info("Configuring device of resource{}".format(to_run_cxs[i][0]))
                            is_device_configured = self.thput_obj_dict[ce][obj_name]["obj"].configure_specific([device_to_run_resource])
                    if is_device_configured:
                        self.thput_obj_dict[ce][obj_name]["obj"].start_specific(to_run_cxs[i])

                # Determine device names based on the current iteration
                device_names = created_cx_lists_keys[:to_run_cxs_len[i][-1]]

                # Monitor throughput and capture all dataframes and test stop status
                all_dataframes, test_stopped_by_user = self.thput_obj_dict[ce][obj_name]["obj"].monitor(
                    i, individual_df, device_names, incremental_capacity_list, overall_start_time, overall_end_time, is_device_configured)
                if do_interopability and "iOS" not in to_run_cxs[i][0] and not default_config:
                    # logger.info("Disconnecting device of resource{}".format(to_run_cxs[i][0]))
                    self.thput_obj_dict[ce][obj_name]["obj"].disconnect_all_devices([device_to_run_resource])
                # Check if the test was stopped by the user
                if not test_stopped_by_user:

                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                else:

                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                    break

        #     logger.info("connections download {}".format(connections_download))
        #     logger.info("connections upload {}".format(connections_upload))
        self.thput_obj_dict[ce][obj_name]["obj"].stop()
        if postcleanup:
            self.thput_obj_dict[ce][obj_name]["obj"].cleanup()
        self.thput_obj_dict[ce][obj_name]["obj"].generate_report(
            list(
                set(iterations_before_test_stopped_by_user)),
            incremental_capacity_list,
            data=all_dataframes,
            data1=to_run_cxs_len,
            report_path=self.result_path if not self.thput_obj_dict[ce][obj_name]["obj"].dowebgui else self.thput_obj_dict[ce][obj_name]["obj"].result_dir)
        if self.thput_obj_dict[ce][obj_name]["obj"].dowebgui:
            # copying to home directory i.e home/user_name
            self.thput_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        params = {
            "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
            "incremental_capacity_list": incremental_capacity_list,
            "data": all_dataframes,
            "data1": to_run_cxs_len,
            "report_path": self.result_path if not self.thput_obj_dict[ce][obj_name]["obj"].dowebgui else self.thput_obj_dict[ce][obj_name]["obj"].result_dir
        }
        self.thput_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("thput")
        return True

    def run_mc_test(self, args):
        endp_types = "lf_udp"

        if self.dowebgui:
            if not self.webgui_stop_check("mc"):
                return False
        test_name = ""
        ip = ""
        # print('newww',args.local_lf_report_dir)
        # exit(0)
        if args.dowebgui:
            logger.info("In webGUI execution")
            if args.dowebgui:
                test_name = args.test_name
                ip = args.lfmgr
                logger.info(" dowebgui %s %s %s", args.dowebgui, test_name, ip)

        # initialize pass / fail
        test_passed = False

        # Configure logging
        logger_config = lf_logger_config.lf_logger_config()

        # set the logger level to debug
        if args.log_level:
            logger_config.set_level(level=args.log_level)

        # lf_logger_config_json will take presidence to changing debug levels
        if args.lf_logger_config_json:
            # logger_config.lf_logger_config_json = "lf_logger_config.json"
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        # validate_args(args)
        endp_input_list = []
        graph_input_list = []
        if args.real:
            endp_input_list, graph_input_list, config_devices, group_device_map = query_real_clients(args)
        # Validate existing station list configuration if specified before starting test
        if not args.use_existing_station_list and args.existing_station_list:
            logger.error("Existing stations specified, but argument \'--use_existing_station_list\' not specified")
            return False
        elif args.use_existing_station_list and not args.existing_station_list:
            logger.error(
                "Argument \'--use_existing_station_list\' specified, but no existing stations provided. See \'--existing_station_list\'")
            return False

        # Gather data for test reporting and KPI generation
        logger.info("Read in command line paramaters")
        interopt_mode = args.interopt_mode

        if args.endp_type:
            endp_types = args.endp_type

        if args.radio:
            radios = args.radio
        else:
            radios = None

        MAX_NUMBER_OF_STATIONS = 1000

        # Lists to help with station creation
        radio_name_list = []
        number_of_stations_per_radio_list = []
        ssid_list = []
        ssid_password_list = []
        ssid_security_list = []
        station_lists = []
        existing_station_lists = []

        # wifi settings configuration
        wifi_mode_list = []
        wifi_enable_flags_list = []

        # optional radio configuration
        reset_port_enable_list = []
        reset_port_time_min_list = []
        reset_port_time_max_list = []

        # wifi extra configuration
        key_mgmt_list = []
        pairwise_list = []
        group_list = []
        psk_list = []
        wep_key_list = []
        ca_cert_list = []
        eap_list = []
        identity_list = []
        anonymous_identity_list = []
        phase1_list = []
        phase2_list = []
        passwd_list = []
        pin_list = []
        pac_file_list = []
        private_key_list = []
        pk_password_list = []
        hessid_list = []
        realm_list = []
        client_cert_list = []
        imsi_list = []
        milenage_list = []
        domain_list = []
        roaming_consortium_list = []
        venue_group_list = []
        network_type_list = []
        ipaddr_type_avail_list = []
        network_auth_type_list = []
        anqp_3gpp_cell_net_list = []
        ieee80211w_list = []

        logger.debug("Parse radio arguments used for station configuration")
        if radios is not None:
            logger.info("radios {}".format(radios))
            for radio_ in radios:
                radio_keys = ['radio', 'stations', 'ssid', 'ssid_pw', 'security']
                logger.info("radio_dict before format {}".format(radio_))
                radio_info_dict = dict(
                    map(
                        lambda x: x.split('=='),
                        str(radio_).replace(
                            '"',
                            '').replace(
                            '[',
                            '').replace(
                            ']',
                            '').replace(
                            "'",
                            "").replace(
                                ",",
                            " ").split()))

                logger.debug("radio_dict {}".format(radio_info_dict))

                for key in radio_keys:
                    if key not in radio_info_dict:
                        logger.critical(
                            "missing config, for the {}, all of the following need to be present {} ".format(
                                key, radio_keys))
                        return False

                radio_name_list.append(radio_info_dict['radio'])
                number_of_stations_per_radio_list.append(
                    radio_info_dict['stations'])
                ssid_list.append(radio_info_dict['ssid'])
                ssid_password_list.append(radio_info_dict['ssid_pw'])
                ssid_security_list.append(radio_info_dict['security'])

                # check for set_wifi_extra
                # check for wifi_settings
                wifi_extra_keys = ['wifi_extra']
                wifi_extra_found = False
                for wifi_extra_key in wifi_extra_keys:
                    if wifi_extra_key in radio_info_dict:
                        logger.info("wifi_extra_keys found")
                        wifi_extra_found = True
                        break

                if wifi_extra_found:
                    logger.debug("wifi_extra: {extra}".format(
                        extra=radio_info_dict['wifi_extra']))

                    wifi_extra_dict = dict(
                        map(
                            lambda x: x.split('&&'),
                            str(radio_info_dict['wifi_extra']).replace(
                                '"',
                                '').replace(
                                '[',
                                '').replace(
                                ']',
                                '').replace(
                                "'",
                                "").replace(
                                ",",
                                " ").replace(
                                "!!",
                                " "
                            )
                            .split()))

                    logger.info("wifi_extra_dict: {wifi_extra}".format(
                        wifi_extra=wifi_extra_dict))

                    if 'key_mgmt' in wifi_extra_dict:
                        key_mgmt_list.append(wifi_extra_dict['key_mgmt'])
                    else:
                        key_mgmt_list.append('[BLANK]')

                    if 'pairwise' in wifi_extra_dict:
                        pairwise_list.append(wifi_extra_dict['pairwise'])
                    else:
                        pairwise_list.append('[BLANK]')

                    if 'group' in wifi_extra_dict:
                        group_list.append(wifi_extra_dict['group'])
                    else:
                        group_list.append('[BLANK]')

                    if 'psk' in wifi_extra_dict:
                        psk_list.append(wifi_extra_dict['psk'])
                    else:
                        psk_list.append('[BLANK]')

                    if 'wep_key' in wifi_extra_dict:
                        wep_key_list.append(wifi_extra_dict['wep_key'])
                    else:
                        wep_key_list.append('[BLANK]')

                    if 'ca_cert' in wifi_extra_dict:
                        ca_cert_list.append(wifi_extra_dict['ca_cert'])
                    else:
                        ca_cert_list.append('[BLANK]')

                    if 'eap' in wifi_extra_dict:
                        eap_list.append(wifi_extra_dict['eap'])
                    else:
                        eap_list.append('[BLANK]')

                    if 'identity' in wifi_extra_dict:
                        identity_list.append(wifi_extra_dict['identity'])
                    else:
                        identity_list.append('[BLANK]')

                    if 'anonymous' in wifi_extra_dict:
                        anonymous_identity_list.append(
                            wifi_extra_dict['anonymous'])
                    else:
                        anonymous_identity_list.append('[BLANK]')

                    if 'phase1' in wifi_extra_dict:
                        phase1_list.append(wifi_extra_dict['phase1'])
                    else:
                        phase1_list.append('[BLANK]')

                    if 'phase2' in wifi_extra_dict:
                        phase2_list.append(wifi_extra_dict['phase2'])
                    else:
                        phase2_list.append('[BLANK]')

                    if 'passwd' in wifi_extra_dict:
                        passwd_list.append(wifi_extra_dict['passwd'])
                    else:
                        passwd_list.append('[BLANK]')

                    if 'pin' in wifi_extra_dict:
                        pin_list.append(wifi_extra_dict['pin'])
                    else:
                        pin_list.append('[BLANK]')

                    if 'pac_file' in wifi_extra_dict:
                        pac_file_list.append(wifi_extra_dict['pac_file'])
                    else:
                        pac_file_list.append('[BLANK]')

                    if 'private_key' in wifi_extra_dict:
                        private_key_list.append(wifi_extra_dict['private_key'])
                    else:
                        private_key_list.append('[BLANK]')

                    if 'pk_password' in wifi_extra_dict:
                        pk_password_list.append(wifi_extra_dict['pk_password'])
                    else:
                        pk_password_list.append('[BLANK]')

                    if 'hessid' in wifi_extra_dict:
                        hessid_list.append(wifi_extra_dict['hessid'])
                    else:
                        hessid_list.append("00:00:00:00:00:00")

                    if 'realm' in wifi_extra_dict:
                        realm_list.append(wifi_extra_dict['realm'])
                    else:
                        realm_list.append('[BLANK]')

                    if 'client_cert' in wifi_extra_dict:
                        client_cert_list.append(wifi_extra_dict['client_cert'])
                    else:
                        client_cert_list.append('[BLANK]')

                    if 'imsi' in wifi_extra_dict:
                        imsi_list.append(wifi_extra_dict['imsi'])
                    else:
                        imsi_list.append('[BLANK]')

                    if 'milenage' in wifi_extra_dict:
                        milenage_list.append(wifi_extra_dict['milenage'])
                    else:
                        milenage_list.append('[BLANK]')

                    if 'domain' in wifi_extra_dict:
                        domain_list.append(wifi_extra_dict['domain'])
                    else:
                        domain_list.append('[BLANK]')

                    if 'roaming_consortium' in wifi_extra_dict:
                        roaming_consortium_list.append(
                            wifi_extra_dict['roaming_consortium'])
                    else:
                        roaming_consortium_list.append('[BLANK]')

                    if 'venue_group' in wifi_extra_dict:
                        venue_group_list.append(wifi_extra_dict['venue_group'])
                    else:
                        venue_group_list.append('[BLANK]')

                    if 'network_type' in wifi_extra_dict:
                        network_type_list.append(wifi_extra_dict['network_type'])
                    else:
                        network_type_list.append('[BLANK]')

                    if 'ipaddr_type_avail' in wifi_extra_dict:
                        ipaddr_type_avail_list.append(
                            wifi_extra_dict['ipaddr_type_avail'])
                    else:
                        ipaddr_type_avail_list.append('[BLANK]')

                    if 'network_auth_type' in wifi_extra_dict:
                        network_auth_type_list.append(
                            wifi_extra_dict['network_auth_type'])
                    else:
                        network_auth_type_list.append('[BLANK]')

                    if 'anqp_3gpp_cell_net' in wifi_extra_dict:
                        anqp_3gpp_cell_net_list.append(
                            wifi_extra_dict['anqp_3gpp_cell_net'])
                    else:
                        anqp_3gpp_cell_net_list.append('[BLANK]')

                    if 'ieee80211w' in wifi_extra_dict:
                        ieee80211w_list.append(wifi_extra_dict['ieee80211w'])
                    else:
                        ieee80211w_list.append('Optional')

                    '''
                    # wifi extra configuration
                    key_mgmt_list.append(key_mgmt)
                    pairwise_list.append(pairwise)
                    group_list.append(group)
                    psk_list.append(psk)
                    eap_list.append(eap)
                    identity_list.append(identity)
                    anonymous_identity_list.append(anonymous_identity)
                    phase1_list.append(phase1)
                    phase2_list.append(phase2)
                    passwd_list.append(passwd)
                    pin_list.append(pin)
                    pac_file_list.append(pac_file)
                    private_key_list.append(private)
                    pk_password_list.append(pk_password)
                    hessid_list.append(hssid)
                    realm_list.append(realm)
                    client_cert_list.append(client_cert)
                    imsi_list.append(imsi)
                    milenage_list.append(milenage)
                    domain_list.append(domain)
                    roaming_consortium_list.append(roaming_consortium)
                    venue_group_list.append(venue_group)
                    network_type_list.append(network_type)
                    ipaddr_type_avail_list.append(ipaddr_type_avail)
                    network_auth_type_list.append(network_ath_type)
                    anqp_3gpp_cell_net_list.append(anqp_3gpp_cell_net)

                    '''
                # no wifi extra for this station
                else:
                    key_mgmt_list.append('[BLANK]')
                    pairwise_list.append('[BLANK]')
                    group_list.append('[BLANK]')
                    psk_list.append('[BLANK]')
                    # for testing
                    # psk_list.append(radio_info_dict['ssid_pw'])
                    wep_key_list.append('[BLANK]')
                    ca_cert_list.append('[BLANK]')
                    eap_list.append('[BLANK]')
                    identity_list.append('[BLANK]')
                    anonymous_identity_list.append('[BLANK]')
                    phase1_list.append('[BLANK]')
                    phase2_list.append('[BLANK]')
                    passwd_list.append('[BLANK]')
                    pin_list.append('[BLANK]')
                    pac_file_list.append('[BLANK]')
                    private_key_list.append('[BLANK]')
                    pk_password_list.append('[BLANK]')
                    hessid_list.append("00:00:00:00:00:00")
                    realm_list.append('[BLANK]')
                    client_cert_list.append('[BLANK]')
                    imsi_list.append('[BLANK]')
                    milenage_list.append('[BLANK]')
                    domain_list.append('[BLANK]')
                    roaming_consortium_list.append('[BLANK]')
                    venue_group_list.append('[BLANK]')
                    network_type_list.append('[BLANK]')
                    ipaddr_type_avail_list.append('[BLANK]')
                    network_auth_type_list.append('[BLANK]')
                    anqp_3gpp_cell_net_list.append('[BLANK]')
                    ieee80211w_list.append('Optional')

                # check for wifi_settings
                wifi_settings_keys = ['wifi_settings']
                wifi_settings_found = True
                for key in wifi_settings_keys:
                    if key not in radio_info_dict:
                        logger.debug("wifi_settings_keys not enabled")
                        wifi_settings_found = False
                        break

                if wifi_settings_found:
                    # Check for additional flags
                    if {'wifi_mode', 'enable_flags'}.issubset(
                            radio_info_dict.keys()):
                        logger.debug("wifi_settings flags set")
                    else:
                        logger.debug("wifi_settings is present wifi_mode, enable_flags need to be set "
                                     "or remove the wifi_settings or set wifi_settings==False flag on "
                                     "the radio for defaults")
                        return False
                    wifi_mode_list.append(radio_info_dict['wifi_mode'])
                    enable_flags_str = radio_info_dict['enable_flags'].replace(
                        '(', '').replace(')', '').replace('|', ',').replace('&&', ',')
                    enable_flags_list = list(enable_flags_str.split(","))
                    wifi_enable_flags_list.append(enable_flags_list)
                else:
                    wifi_mode_list.append(0)
                    wifi_enable_flags_list.append(
                        ["wpa2_enable", "80211u_enable", "create_admin_down"])
                    # 8021x_radius is the same as Advanced/8021x on the gui

                # check for optional radio key , currently only reset is enabled
                # update for checking for reset_port_time_min, reset_port_time_max
                optional_radio_reset_keys = ['reset_port_enable']
                radio_reset_found = True
                for key in optional_radio_reset_keys:
                    if key not in radio_info_dict:
                        # logger.debug("port reset test not enabled")
                        radio_reset_found = False
                        break

                if radio_reset_found:
                    reset_port_enable_list.append(
                        radio_info_dict['reset_port_enable'])
                    reset_port_time_min_list.append(
                        radio_info_dict['reset_port_time_min'])
                    reset_port_time_max_list.append(
                        radio_info_dict['reset_port_time_max'])
                else:
                    reset_port_enable_list.append(False)
                    reset_port_time_min_list.append('0s')
                    reset_port_time_max_list.append('0s')

            index = 0
            for (radio_name_, number_of_stations_per_radio_) in zip(
                    radio_name_list, number_of_stations_per_radio_list):
                number_of_stations = int(number_of_stations_per_radio_)
                if number_of_stations > MAX_NUMBER_OF_STATIONS:
                    logger.critical("number of stations per radio exceeded max of : {}".format(
                        MAX_NUMBER_OF_STATIONS))
                    quit(1)
                station_list = LFUtils.portNameSeries(
                    prefix_="sta",
                    start_id_=0 + index * 1000 + int(args.sta_start_offset),
                    end_id_=number_of_stations - 1 + index *
                    1000 + int(args.sta_start_offset),
                    padding_number_=10000,
                    radio=radio_name_)
                station_lists.append(station_list)
                index += 1

        # create a secondary station_list
        if args.use_existing_station_list:
            if args.existing_station_list is not None:
                # these are entered stations
                for existing_sta_list in args.existing_station_list:
                    existing_stations = str(existing_sta_list).replace(
                        '"',
                        '').replace(
                        '[',
                        '').replace(
                        ']',
                        '').replace(
                        "'",
                        "").replace(
                            ",",
                        " ").split()

                    for existing_sta in existing_stations:
                        existing_station_lists.append(existing_sta)
            else:
                logger.error(
                    "--use_station_list set true, --station_list is None Exiting")
                raise Exception(
                    "--use_station_list is used in conjunction with a --station_list")

        logger.info("existing_station_lists: {sta}".format(
            sta=existing_station_lists))

        # logger.info("endp-types: %s"%(endp_types))
        ul_rates = args.side_a_min_bps.replace(',', ' ').split()
        dl_rates = args.side_b_min_bps.replace(',', ' ').split()
        ul_pdus = args.side_a_min_pdu.replace(',', ' ').split()
        dl_pdus = args.side_b_min_pdu.replace(',', ' ').split()
        if args.attenuators == "":
            attenuators = []
        else:
            attenuators = args.attenuators.split(",")
        if args.atten_vals == "":
            atten_vals = [-1]
        else:
            atten_vals = args.atten_vals.split(",")

        if len(ul_rates) != len(dl_rates):
            # todo make fill assignable
            logger.info(
                "ul_rates %s and dl_rates %s arrays are of different length will fill shorter list with 256000\n" %
                (len(ul_rates), len(dl_rates)))
        if len(ul_pdus) != len(dl_pdus):
            logger.info(
                "ul_pdus %s and dl_pdus %s arrays are of different lengths will fill shorter list with size AUTO \n" %
                (len(ul_pdus), len(dl_pdus)))

        # Configure reporting
        logger.info("Configuring report")
        report, kpi_csv, csv_outfile = configure_reporting(**vars(args))
        ce = self.current_exec  # seires
        if ce == "parallel":
            obj_name = "mcast_test"
        else:
            obj_no = 1
            while f"mcast_test_{obj_no}" in self.mcast_obj_dict[ce]:
                obj_no += 1
            obj_name = f"mcast_test_{obj_no}"
        self.mcast_obj_dict[ce][obj_name] = {"obj": None, "data": None}
        logger.info("Configure test object")
        bssids_mcast = ','.join(f for f in self.bssids)
        self.mcast_obj_dict[ce][obj_name]["obj"] = L3VariableTime(
            endp_types=endp_types,
            args=args,
            tos=args.tos,
            side_b=args.upstream_port,
            side_a=args.downstream_port,
            radio_name_list=radio_name_list,
            number_of_stations_per_radio_list=number_of_stations_per_radio_list,
            ssid_list=ssid_list,
            ssid_password_list=ssid_password_list,
            ssid_security_list=ssid_security_list,
            wifi_mode_list=wifi_mode_list,
            enable_flags_list=wifi_enable_flags_list,
            station_lists=station_lists,
            name_prefix="LT-",
            outfile=csv_outfile,
            reset_port_enable_list=reset_port_enable_list,
            reset_port_time_min_list=reset_port_time_min_list,
            reset_port_time_max_list=reset_port_time_max_list,
            side_a_min_rate=ul_rates,
            side_b_min_rate=dl_rates,
            side_a_min_pdu=ul_pdus,
            side_b_min_pdu=dl_pdus,
            rates_are_totals=args.rates_are_totals,
            mconn=args.multiconn,
            attenuators=attenuators,
            atten_vals=atten_vals,
            number_template="00",
            test_duration=args.test_duration,
            polling_interval=args.polling_interval,
            lfclient_host=args.lfmgr,
            lfclient_port=args.lfmgr_port,
            debug=args.debug,
            kpi_csv=kpi_csv,
            no_cleanup=args.no_cleanup,
            use_existing_station_lists=args.use_existing_station_list,
            existing_station_lists=existing_station_lists,
            wait_for_ip_sec=args.wait_for_ip_sec,
            exit_on_ip_acquired=args.exit_on_ip_acquired,
            ap_read=args.ap_read,
            ap_module=args.ap_module,
            ap_test_mode=args.ap_test_mode,
            ap_ip=args.ap_ip,
            ap_user=args.ap_user,
            ap_passwd=args.ap_passwd,
            ap_scheme=args.ap_scheme,
            ap_serial_port=args.ap_serial_port,
            ap_ssh_port=args.ap_ssh_port,
            ap_telnet_port=args.ap_telnet_port,
            ap_serial_baud=args.ap_serial_baud,
            ap_if_2g=args.ap_if_2g,
            ap_if_5g=args.ap_if_5g,
            ap_if_6g=args.ap_if_6g,
            ap_report_dir="",
            ap_file=args.ap_file,
            ap_band_list=args.ap_band_list.split(','),

            # for webgui execution
            test_name=test_name,
            dowebgui=args.dowebgui,
            ip=ip,
            get_live_view=args.get_live_view,
            total_floors=args.total_floors,
            # for uniformity from webGUI result_dir as variable is used insead of local_lf_report_dir
            result_dir=args.local_lf_report_dir,

            # wifi extra configuration
            key_mgmt_list=key_mgmt_list,
            pairwise_list=pairwise_list,
            group_list=group_list,
            psk_list=psk_list,
            wep_key_list=wep_key_list,
            ca_cert_list=ca_cert_list,
            eap_list=eap_list,
            identity_list=identity_list,
            anonymous_identity_list=anonymous_identity_list,
            phase1_list=phase1_list,
            phase2_list=phase2_list,
            passwd_list=passwd_list,
            pin_list=pin_list,
            pac_file_list=pac_file_list,
            private_key_list=private_key_list,
            pk_password_list=pk_password_list,
            hessid_list=hessid_list,
            realm_list=realm_list,
            client_cert_list=client_cert_list,
            imsi_list=imsi_list,
            milenage_list=milenage_list,
            domain_list=domain_list,
            roaming_consortium_list=roaming_consortium_list,
            venue_group_list=venue_group_list,
            network_type_list=network_type_list,
            ipaddr_type_avail_list=ipaddr_type_avail_list,
            network_auth_type_list=network_auth_type_list,
            anqp_3gpp_cell_net_list=anqp_3gpp_cell_net_list,
            ieee80211w_list=ieee80211w_list,
            interopt_mode=interopt_mode,
            endp_input_list=endp_input_list,
            graph_input_list=graph_input_list,
            real=args.real,
            expected_passfail_value=args.expected_passfail_value,
            device_csv_name=args.device_csv_name,
            group_name=args.group_name,

            # for Robot execution
            robot_test=self.robot_test,
            robot_ip=self.robot_ip,
            coordinate=self.coordinate,
            rotation=self.rotation,

            do_bandsteering=self.do_bandsteering,
            cycles=self.cycles,
            bssids=bssids_mcast,
            duration_to_skip=self.duration_to_skip

        )

        # Perform pre-test cleanup, if configured to do so
        if args.no_pre_cleanup:
            logger.info("Skipping pre-test cleanup, '--no_pre_cleanup' specified")
        elif args.use_existing_station_list:
            logger.info("Skipping pre-test cleanup, '--use_existing_station_list' specified")
        else:
            logger.info("Performing pre-test cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].pre_cleanup()

        # Build test configuration
        logger.info("Building test configuration")
        self.mcast_obj_dict[ce][obj_name]["obj"].build()
        if not self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            logger.critical("Test configuration build failed")
            logger.critical(self.mcast_obj_dict[ce][obj_name]["obj"].get_fail_message())
            return False

        # Run test
        logger.info("Starting test")
        if (self.robot_test and any(etype in args.endp_type for etype in ["mc_udp", "mc_udp6"])):
            logger.info("Multicast robot test detected")
            if self.do_bandsteering:
                self.mcast_obj_dict[ce][obj_name]["obj"].perform_bandsteering()
            else:
                self.mcast_obj_dict[ce][obj_name]["obj"].perform_robo()
        else:
            self.mcast_obj_dict[ce][obj_name]["obj"].start(False)

        if args.wait > 0:
            logger.info(f"Pausing {args.wait} seconds for manual inspection before test conclusion and "
                        "possible traffic stop/post-test cleanup")
            time.sleep(args.wait)

        # Admin down the stations
        if args.no_stop_traffic:
            logger.info("Test complete, '--no_stop_traffic' specified, traffic continues to run")
        else:
            if args.quiesce_cx:
                logger.info("Test complete, quiescing traffic")
                self.mcast_obj_dict[ce][obj_name]["obj"].quiesce_cx()
                time.sleep(3)
            else:
                logger.info("Test complete, stopping traffic")
                self.mcast_obj_dict[ce][obj_name]["obj"].stop()

        # Set DUT information for reporting
        self.mcast_obj_dict[ce][obj_name]["obj"].set_dut_info(
            dut_model_num=args.dut_model_num,
            dut_hw_version=args.dut_hw_version,
            dut_sw_version=args.dut_sw_version,
            dut_serial_num=args.dut_serial_num)
        self.mcast_obj_dict[ce][obj_name]["obj"].set_report_obj(report=report)
        if args.dowebgui:
            self.mcast_obj_dict[ce][obj_name]["obj"].webgui_finalize()
        # Generate and write out test report
        logger.info("Generating test report")
        if args.real:
            self.mcast_obj_dict[ce][obj_name]["obj"].generate_report(config_devices, group_device_map)
        else:
            self.mcast_obj_dict[ce][obj_name]["obj"].generate_report()
        params = {
            "config_devices": None,
            "group_device_map": None
        }
        params["group_device_map"] = group_device_map
        params["config_devices"] = config_devices
        self.mcast_obj_dict[ce][obj_name]["data"] = params.copy()
        self.mcast_obj_dict[ce][obj_name]["obj"].write_report()

        # TODO move to after reporting
        if not self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            logger.warning("Test Ended: There were Failures")
            logger.warning(self.mcast_obj_dict[ce][obj_name]["obj"].get_fail_message())

        if args.no_cleanup:
            logger.info("Skipping post-test cleanup, '--no_cleanup' specified")
        elif args.no_stop_traffic:
            logger.info("Skipping post-test cleanup, '--no_stop_traffic' specified")
        else:
            logger.info("Performing post-test cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].cleanup()

        # TODO: This is redundant if '--no_cleanup' is not specified (already taken care of there)
        if args.cleanup_cx:
            logger.info("Performing post-test CX traffic pair cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].cleanup_cx()

        if self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            test_passed = True
            logger.info("Full test passed, all connections increased rx bytes")

        # Run WebGUI-specific post test logic
        if args.dowebgui:
            self.mcast_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()

        if test_passed:
            self.mcast_obj_dict[ce][obj_name]["obj"].exit_success()
        else:
            self.mcast_obj_dict[ce][obj_name]["obj"].exit_fail()
        if self.dowebgui:
            self.webgui_test_done("mc")
        return True

    def run_mc_test1(
        self,
        local_lf_report_dir="",
        results_dir_name="test_l3",
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="test l3",
        csv_outfile="",
        tty="",
        baud="9600",
        test_duration="3m",
        tos="BE",
        debug=False,
        log_level=None,
        interopt_mode=False,
        endp_type="mc_udp",
        upstream_port="eth1",
        downstream_port=None,
        polling_interval="5s",
        radio=None,
        side_a_min_bps="0",
        side_a_min_pdu="MTU",
        side_b_min_bps="256000",
        side_b_min_pdu="MTU",
        rates_are_totals=True,
        multiconn=1,
        attenuators="",
        atten_vals="",
        wait=0,
        sta_start_offset="0",
        no_pre_cleanup=False,
        no_cleanup=True,
        cleanup_cx=False,
        csv_data_to_report=False,
        no_stop_traffic=False,
        quiesce_cx=False,
        use_existing_station_list=False,
        existing_station_list=None,
        wait_for_ip_sec="120s",
        exit_on_ip_acquired=False,
        lf_logger_config_json=None,
        ap_read=False,
        ap_module=None,
        ap_test_mode=True,
        ap_scheme="serial",
        ap_serial_port="/dev/ttyUSB0",
        ap_serial_baud="115200",
        ap_ip="192.168.50.1",
        ap_ssh_port="1025",
        ap_telnet_port="23",
        ap_user="lanforge",
        ap_passwd="lanforge",
        ap_if_2g="wl0",
        ap_if_5g="wl1",
        ap_if_6g="wl2",
        ap_file=None,
        ap_band_list="2g,5g,6g",
        dowebgui=False,
        test_name=None,
        ssid=None,
        passwd=None,
        security=None,
        device_list=None,
        expected_passfail_value=None,
        device_csv_name=None,
        file_name=None,
        group_name=None,
        profile_name=None,
        eap_method="DEFAULT",
        eap_identity="",
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management="DEFAULT",
        pairwise="NA",
        private_key="NA",
        ca_cert="NA",
        client_cert="NA",
        pk_passwd="NA",
        pac_file="NA",
        config=False,
        wait_time=60,
        real=True,
        get_live_view=False,
        total_floors="0",
        help_summary=False,
        result_dir=''
    ):
        """
        Configure and execute a Layer 3 Multicast (MC) test.
        This handles argument processing and delegates execution to `run_mc_test`.
        """
        args = SimpleNamespace(**locals())
        args.lfmgr_port = self.port
        args.lfmgr = self.lanforge_ip
        args.local_lf_report_dir = os.getcwd() if not args.dowebgui else result_dir
        return self.run_mc_test(args)

    def run_yt_test(
            self,
            url=None,
            duration=None,
            ap_name="TIP",
            sec="wpa2",
            band="5GHZ",
            test_name=None,
            upstream_port=None,
            resource_list=None,
            no_pre_cleanup=False,
            no_post_cleanup=False,
            debug=False,
            log_level=None,
            res="Auto",
            lf_logger_config_json=None,
            ui_report_dir=None,
            do_webUI=False,
            file_name=None,
            group_name=None,
            profile_name=None,
            ssid=None,
            passwd=None,
            encryp=None,
            eap_method="DEFAULT",
            eap_identity="DEFAULT",
            ieee8021x=False,
            ieee80211u=False,
            ieee80211w=1,
            enable_pkc=False,
            bss_transition=False,
            power_save=False,
            disable_ofdma=False,
            roam_ft_ds=False,
            key_management="DEFAULT",
            pairwise="NA",
            private_key="NA",
            ca_cert="NA",
            pac_file="NA",
            client_cert="NA",
            pk_passwd="NA",
            help_summary=None,
            expected_passfail_value=None,
            device_csv_name=None,
            config=False,
            exec_type=None
    ):
        """
        Configure and execute a YouTube (YT) streaming test.
        This handles test configuration, client setup, and monitors the video streaming session using a Flask server API.
        """
        try:
            if self.do_bandsteering:
                duration = 999999
            if self.dowebgui:
                if not self.webgui_stop_check("yt"):
                    return False
            if isinstance(duration, int):
                pass
            elif duration.endswith('s') or duration.endswith('S'):
                duration = int(duration[0:-1]) / 60
            elif duration.endswith('m') or duration.endswith('M'):
                duration = int(duration[0:-1])
            elif duration.endswith('h') or duration.endswith('H'):
                duration = int(duration[0:-1]) * 60
            else:
                duration = int(duration)

            # set the logger level to debug
            logger_config = lf_logger_config.lf_logger_config()

            if log_level:
                logger_config.set_level(level=log_level)

            if lf_logger_config_json:
                logger_config.lf_logger_config_json = lf_logger_config_json
                logger_config.load_lf_logger_config()

            mgr_ip = self.lanforge_ip
            mgr_port = self.port
            url = url
            duration = duration

            do_webUI = do_webUI
            ui_report_dir = ui_report_dir
            debug = debug
            # Print debug information if debugging is enabled
            if debug:
                logging.info('''Specified configuration:
                ip:                       {}
                port:                     {}
                Duration:                 {}
                debug:                    {}
                '''.format(mgr_ip, mgr_port, duration, debug))

            if True:
                if group_name is not None:
                    group_name = group_name.strip()
                    selected_groups = group_name.split(',')
                else:
                    selected_groups = []

                if profile_name is not None:
                    profile_name = profile_name.strip()
                    selected_profiles = profile_name.split(',')
                else:
                    selected_profiles = []

                Devices = RealDevice(manager_ip=mgr_ip,
                                     server_ip='192.168.1.61',
                                     ssid_2g='Test Configured',
                                     passwd_2g='',
                                     encryption_2g='',
                                     ssid_5g='Test Configured',
                                     passwd_5g='',
                                     encryption_5g='',
                                     ssid_6g='Test Configured',
                                     passwd_6g='',
                                     encryption_6g='',
                                     selected_bands=['5G'])
                Devices.get_devices()

                self.yt_test_obj = Youtube(
                    host=mgr_ip,
                    port=mgr_port,
                    url=url,
                    duration=duration,
                    lanforge_password='lanforge',
                    sta_list=[],
                    do_webUI=do_webUI,
                    ui_report_dir=ui_report_dir,
                    debug=debug,
                    resolution=res,
                    ap_name=ap_name,
                    ssid=ssid,
                    security=encryp,
                    band=band,
                    test_name=test_name,
                    upstream_port=upstream_port,
                    config=config,
                    selected_groups=selected_groups,
                    selected_profiles=selected_profiles,
                    robo_ip=self.robot_ip,
                    coordinates_list=self.coordinate_list,
                    angles_list=self.rotation_list,
                    do_robo=self.robot_test,
                    rotations_enabled=self.rotation_enabled,
                    do_bandsteering=self.do_bandsteering,
                    # bssids=self.bssids,
                    bssids=[b.strip() for b in self.bssids.split(",")] if isinstance(self.bssids, str) else (self.bssids or []),
                    cycles=self.cycles
                )

                logging.info('CHECKING PORT AVAILBILITY for YT TEST')
                self.port_clean_up(5002)
                self.yt_test_obj.start_flask_server()
                upstream_port = self.yt_test_obj.change_port_to_ip(upstream_port)

                resources = []
                self.yt_test_obj.Devices = Devices
                if file_name:
                    new_filename = file_name.removesuffix(".csv")
                else:
                    new_filename = file_name
                config_obj = DeviceConfig.DeviceConfig(lanforge_ip=self.lanforge_ip, file_name=new_filename)
                # if not expected_passfail_value and device_csv_name is None:
                #     config_obj.device_csv_file(csv_name="device.csv")
                if group_name is not None and file_name is not None and profile_name is not None:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    config_devices = {}
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]

                    config_obj.initiate_group()

                    asyncio.run(config_obj.connectivity(config_devices))

                    adbresponse = config_obj.adb_obj.get_devices()
                    resource_manager = config_obj.laptop_obj.get_devices()
                    all_res = {}
                    df1 = config_obj.display_groups(config_obj.groups)
                    groups_list = df1.to_dict(orient='list')
                    group_devices = {}

                    for adb in adbresponse:
                        group_devices[adb['serial']] = adb['eid']
                    for res in resource_manager:
                        all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
                    eid_list = []
                    for grp_name in groups_list.keys():
                        for g_name in selected_groups:
                            if grp_name == g_name:
                                for j in groups_list[grp_name]:
                                    if j in group_devices.keys():
                                        eid_list.append(group_devices[j])
                                    elif j in all_res.keys():
                                        eid_list.append(all_res[j])
                    resource_list = ",".join(id for id in eid_list)
                else:
                    config_dict = {
                        'ssid': ssid,
                        'passwd': passwd,
                        'enc': encryp,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee8021x,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': upstream_port,
                    }
                    if resource_list:
                        all_devices = config_obj.get_all_devices()
                        if group_name is None and file_name is None and profile_name is None:
                            dev_list = resource_list.split(',')
                            if config:
                                asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                    else:
                        all_devices = config_obj.get_all_devices()
                        device_list = []
                        for device in all_devices:
                            if device["type"] != 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                            elif device["type"] == 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])

                        logging.info("Available devices:")
                        for device in device_list:
                            logging.info(device)

                        resource_list = input("Enter the desired resources to run the test:")
                        dev1_list = resource_list.split(',')
                        if config:
                            asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

                if not do_webUI:
                    if resource_list:
                        resources = [r.strip() for r in resource_list.split(',')]
                        resources = [r for r in resources if len(r.split('.')) > 1]

                        self.yt_test_obj.select_real_devices(real_devices=Devices, real_sta_list=resources, base_interop_obj=Devices)

                    else:
                        self.yt_test_obj.select_real_devices(real_devices=Devices)
                else:
                    resources = [r.strip() for r in resource_list.split(',')]

                    extracted_parts = [res.split('.')[:2] for res in resources]
                    formatted_parts = ['.'.join(parts) for parts in extracted_parts]
                    self.yt_test_obj.select_real_devices(real_devices=Devices, real_sta_list=formatted_parts, base_interop_obj=Devices)

                # Perform pre-test cleanup if not skipped
                if not no_pre_cleanup:
                    self.yt_test_obj.cleanup()

                # Check if the required tab exists, and exit if not
                if not self.yt_test_obj.check_tab_exists():
                    logging.error('Generic Tab is not available.\nAborting the test.')
                    return False

                if len(self.yt_test_obj.real_sta_list) > 0:
                    logging.info(f"checking real sta list while creating endpionts {self.yt_test_obj.real_sta_list}")
                    self.yt_test_obj.create_generic_endp()
                else:
                    logging.info(f"checking real sta list while creating endpionts {self.yt_test_obj.real_sta_list}")
                    logging.error("No Real Devies Available")
                    return False

                if do_webUI:
                    self.yt_test_obj.update_webui()
                logging.info("TEST STARTED")
                logging.info('Running the youtube Streaming test for {} minutes'.format(duration))

                time.sleep(10)

                self.yt_test_obj.start_time = datetime.datetime.now()
                if self.robot_test:
                    if self.do_bandsteering:
                        self.yt_test_obj.perform_robo_bandsteering_test()
                    else:
                        self.yt_test_obj.perform_robo_test()
                else:
                    self.yt_test_obj.start_generic()
                    logging.info(f"yt_test_obj: {self.yt_test_obj}")
                    logging.info(f"generic_endps_profile: {getattr(self.yt_test_obj, 'generic_endps_profile', None)}")
                    logging.info(f"device_names: {getattr(self.yt_test_obj, 'device_names', None)}")
                    # logging.info(f"stats_api_response: {getattr(self.yt_test_obj, 'stats_api_response', None)}")

                    # duration = duration
                    # end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)

                    # while datetime.datetime.now() < end_time or not self.yt_test_obj.check_gen_cx():

                    #     time.sleep(5)
                    # if initial_data:
                    #     end_time_webgui = []
                    #     for i in range(len(self.yt_test_obj.device_names)):
                    #         end_time_webgui.append(initial_data['result'].get(self.yt_test_obj.device_names[i], {}).get('stop', False))
                    # else:
                    #     for i in range(len(self.yt_test_obj.device_names)):
                    #         end_time_webgui.append("")

                    end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)

                    while datetime.datetime.now() < end_time or not self.yt_test_obj.check_gen_cx():
                        # self.yt_test_obj.get_data_from_api()
                        time.sleep(5)
                    self.yt_test_obj.generic_endps_profile.stop_cx()
                    logging.info("Duration ended")

                    logging.info('Stopping the test')

                    # if getattr(self.yt_test_obj, "generic_endps_profile", None):
                    #     logger.info("Stopping all the endpoints")
                    # else:
                    #     logging.warning("⚠️ generic_endps_profile is None — skipping stop_cx()")
                if not (self.robot_test) and do_webUI:
                    # print("hii here data",self.yt_test_obj.stats_api_response)
                    self.yt_test_obj.create_report()
                else:
                    if self.robot_test and not self.do_bandsteering:
                        # self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time = self.report_path_date_time
                        # os.chdir("../real_application_tests/youtube/")
                        os.chdir("real_application_tests/youtube")
                        self.yt_test_obj.report_path_date_time = os.getcwd()
                        if do_webUI:
                            self.yt_test_obj.stop_webui_test()
                        self.yt_test_obj.create_robo_report()
                    else:
                        self.yt_test_obj.create_report()

                # Perform post-test cleanup if not skipped
                # if not no_post_cleanup:
                #     self.yt_test_obj.generic_endps_profile.cleanup()
        except Exception as e:
            logging.error(f"Error occured {e}")
            # traceback.print_exc()
        finally:
            if not ('--help' in sys.argv or '-h' in sys.argv):
                # traceback.print_exc()
                self.yt_test_obj.stop()
                if self.current_exec == "parallel":
                    self.yt_obj_dict["parallel"]["yt_test"]["obj"] = self.yt_test_obj
                else:
                    for i in range(len(self.yt_obj_dict["series"])):
                        if self.yt_obj_dict["series"][f"yt_test_{i + 1}"]["obj"] is None:
                            self.yt_obj_dict["series"][f"yt_test_{i + 1}"]["obj"] = self.yt_test_obj
                            break
                # Stopping the Youtube test
                if do_webUI:
                    self.yt_test_obj.stop()
                if self.dowebgui:
                    self.webgui_test_done("yt")
                logging.info("Waiting for Cleanup of Browsers in Devices")
                time.sleep(10)
        return True

    def run_zoom_test(
        self,
        duration: int,
        signin_email: str,
        signin_passwd: str,
        participants: int,
        audio: bool = False,
        video: bool = False,
        wait_time: int = 30,
        log_level: str = None,
        lf_logger_config_json: str = None,
        resource_list: str = None,
        do_webUI: bool = False,
        report_dir: str = None,
        testname: str = None,
        zoom_host: str = None,
        file_name: str = None,
        group_name: str = None,
        profile_name: str = None,
        ssid: str = None,
        passwd: str = None,
        encryp: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = 'DEFAULT',
        ieee8021x: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = 'NA',
        private_key: str = 'NA',
        ca_cert: str = 'NA',
        client_cert: str = 'NA',
        pk_passwd: str = 'NA',
        pac_file: str = 'NA',
        upstream_port: str = 'NA',
        help_summary: str = None,
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        config: bool = False,
        exec_type: str = None,
        api_stats_collection: bool = False,
        env_file: str = None,
        account_id: str = None,
        client_id: str = None,
        client_secret: str = None
    ):
        """
        Configure and execute a Zoom automation test.
        This handles Zoom client configuration, meeting participation, and API stats collection.
        """
        try:
            lanforge_ip = self.lanforge_ip
            if self.dowebgui:
                if not self.webgui_stop_check("zoom"):
                    return False
            if True:

                if group_name is not None:
                    group_name = group_name.strip()
                    selected_groups = group_name.split(',')
                else:
                    selected_groups = []

                if profile_name is not None:
                    profile_name = profile_name.strip()
                    selected_profiles = profile_name.split(',')
                else:
                    selected_profiles = []

                # upstream_port = "10.253.8.126"
                self.zoom_test_obj = ZoomAutomation(audio=audio, video=video, lanforge_ip=lanforge_ip, wait_time=wait_time, testname=testname,
                                                    upstream_port=upstream_port, config=config, selected_groups=selected_groups, selected_profiles=selected_profiles,
                                                    robo_ip=self.robot_ip, coordinates_list=self.coordinate_list, angles_list=self.rotation_list, do_robo=self.robot_test,
                                                    rotations_enabled=self.rotation_enabled, api_stats_collection=api_stats_collection, participants_req=participants,
                                                    signin_email=signin_email, signin_passwd=signin_passwd, duration=duration, do_webui=self.dowebgui, do_bs=self.do_bandsteering, bssids=self.bssids, cycles=self.cycles)  # noqa: E501
                upstream_port = self.zoom_test_obj.change_port_to_ip(upstream_port)
                self.zoom_test_obj.upstream_port = upstream_port
                realdevice = RealDevice(manager_ip=lanforge_ip,
                                        server_ip="192.168.1.61",
                                        ssid_2g='Test Configured',
                                        passwd_2g='',
                                        encryption_2g='',
                                        ssid_5g='Test Configured',
                                        passwd_5g='',
                                        encryption_5g='',
                                        ssid_6g='Test Configured',
                                        passwd_6g='',
                                        encryption_6g='',
                                        selected_bands=['5G'])
                laptops = realdevice.get_devices()
                logging.info('CHECKING PORT AVAILBILITY for ZOOM TEST')
                self.port_clean_up(5000)

                if file_name:
                    new_filename = file_name.removesuffix(".csv")
                else:
                    new_filename = file_name
                config_obj = DeviceConfig.DeviceConfig(lanforge_ip=lanforge_ip, file_name=new_filename)

                # if not expected_passfail_value and device_csv_name is None:
                #     config_obj.device_csv_file(csv_name="device.csv")
                if group_name is not None and file_name is not None and profile_name is not None:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    config_devices = {}
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]

                    config_obj.initiate_group()
                    asyncio.run(config_obj.connectivity(config_devices))

                    adbresponse = config_obj.adb_obj.get_devices()
                    resource_manager = config_obj.laptop_obj.get_devices()
                    all_res = {}
                    df1 = config_obj.display_groups(config_obj.groups)
                    groups_list = df1.to_dict(orient='list')
                    group_devices = {}

                    for adb in adbresponse:
                        group_devices[adb['serial']] = adb['eid']
                    for res in resource_manager:
                        all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
                    eid_list = []
                    for grp_name in groups_list.keys():
                        for g_name in selected_groups:
                            if grp_name == g_name:
                                for j in groups_list[grp_name]:
                                    if j in group_devices.keys():
                                        eid_list.append(group_devices[j])
                                    elif j in all_res.keys():
                                        eid_list.append(all_res[j])
                    if zoom_host in eid_list:
                        # Remove the existing instance of zoom_host from the list
                        eid_list.remove(zoom_host)
                        # Insert zoom_host at the beginning of the list
                        eid_list.insert(0, zoom_host)

                    resource_list = ",".join(id for id in eid_list)
                else:
                    config_dict = {
                        'ssid': ssid,
                        'passwd': passwd,
                        'enc': encryp,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee8021x,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': upstream_port,

                    }
                    if resource_list:
                        all_devices = config_obj.get_all_devices()
                        if group_name is None and file_name is None and profile_name is None:
                            dev_list = resource_list.split(',')
                            if not do_webUI:
                                zoom_host = zoom_host.strip()
                                if zoom_host in dev_list:
                                    dev_list.remove(zoom_host)
                                dev_list.insert(0, zoom_host)
                            if config:
                                asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                            resource_list = ",".join(id for id in dev_list)
                    else:
                        # If no resources provided, prompt user to select devices manually
                        if config:
                            all_devices = config_obj.get_all_devices()
                            device_list = []
                            for device in all_devices:
                                if device["type"] != 'laptop':
                                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                                elif device["type"] == 'laptop':
                                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                            logging.info("Available Devices For Testing")
                            for device in device_list:
                                logging.info(device)
                            zm_host = input("Enter Host Resource for the Test : ")
                            zm_host = zm_host.strip()
                            resource_list = input("Enter client Resources to run the test :")
                            resource_list = zm_host + "," + resource_list
                            dev1_list = resource_list.split(',')
                            asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

                result_list = []
                if not do_webUI:
                    if resource_list:
                        resources = resource_list.split(',')
                        resources = [r for r in resources if len(r.split('.')) > 1]
                        # resources = sorted(resources, key=lambda x: int(x.split('.')[1]))
                        get_data = self.zoom_test_obj.select_real_devices(real_device_obj=realdevice, real_sta_list=resources)
                        for item in get_data:
                            item = item.strip()
                            # Find and append the matching lap to result_list
                            matching_laps = [lap for lap in laptops if lap.startswith(item)]
                            result_list.extend(matching_laps)
                        if not result_list:
                            logging.info("Resources donot exist hence Terminating the test.")
                            return
                        if len(result_list) != len(get_data):
                            logging.info("Few Resources donot exist")
                    else:
                        resources = self.zoom_test_obj.select_real_devices(real_device_obj=realdevice)
                else:
                    if do_webUI:
                        self.zoom_test_obj.path = report_dir
                    resources = resource_list.split(',')
                    extracted_parts = [res.split('.')[:2] for res in resources]
                    formatted_parts = ['.'.join(parts) for parts in extracted_parts]

                    self.zoom_test_obj.select_real_devices(real_device_obj=realdevice, real_sta_list=formatted_parts)
                    if do_webUI:

                        if len(self.zoom_test_obj.real_sta_hostname) == 0:
                            logging.info("No device is available to run the test")
                            obj = {
                                "status": "Stopped",
                                "configuration_status": "configured"
                            }
                            self.zoom_test_obj.updating_webui_runningjson(obj)
                            return False
                        else:
                            obj = {
                                "configured_devices": self.zoom_test_obj.real_sta_hostname,
                                "configuration_status": "configured",
                                "no_of_devices": f' Total({len(self.zoom_test_obj.real_sta_os_type)}) : W({self.zoom_test_obj.windows}),L({self.zoom_test_obj.linux}),M({self.zoom_test_obj.mac})',
                                "device_list": self.zoom_test_obj.hostname_os_combination,
                                # "zoom_host":self.zoom_test_obj.zoom_host

                            }
                            self.zoom_test_obj.updating_webui_runningjson(obj)

                if not self.zoom_test_obj.check_tab_exists():
                    logging.error('Generic Tab is not available.\nAborting the test.')
                    return False

                self.zoom_test_obj.handle_flask_server()
                self.zoom_test_obj.get_resource_data()
                self.zoom_test_obj.get_ports_data()
                self.zoom_test_obj.get_interop_data()

                if api_stats_collection:
                    if env_file:
                        if os.path.exists(env_file):
                            load_dotenv(env_file)
                            logging.info(f"Loaded environment variables from {env_file}")
                        else:
                            raise FileNotFoundError(f"Environment file {env_file} not found.")

                    # Fetching zoom credentials for account
                    self.zoom_test_obj.account_id = account_id or os.environ.get(
                        "ACCOUNT_ID"
                    )
                    self.zoom_test_obj.client_id = client_id or os.environ.get(
                        "CLIENT_ID"
                    )
                    self.zoom_test_obj.client_secret = client_secret or os.environ.get(
                        "CLIENT_SECRET"
                    )

                    if not all(
                        [
                            self.zoom_test_obj.account_id,
                            self.zoom_test_obj.client_id,
                            self.zoom_test_obj.client_secret,
                        ]
                    ):
                        logger.info("Exiting test.")
                        raise ValueError(
                            "Missing Zoom API credentials. Please provide ACCOUNT_ID, CLIENT_ID, and CLIENT_SECRET as environment variables or through function arguments."
                        )
                if self.robot_test and not self.do_bandsteering:
                    self.zoom_test_obj.report_path_date_time = os.path.join(os.getcwd(), "zoom_test_results")
                    self.zoom_test_obj.run_robo_test()
                else:
                    # self.zoom_test_obj.report_path_date_time = os.path.join(os.getcwd() , "zoom_test_results")
                    self.zoom_test_obj.run()
                    # self.zoom_test_obj.run(duration, upstream_port, signin_email, signin_passwd, participants)

                self.zoom_test_obj.data_store.clear()
                if not api_stats_collection:
                    self.zoom_test_obj.generate_report()
                logging.info("Test Completed Sucessfully")
        except Exception as e:
            logging.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
            traceback.print_exc()
        finally:
            if not ('--help' in sys.argv or '-h' in sys.argv):

                # self.zoom_test_obj.redis_client.set('login_completed', 0)
                self.zoom_test_obj.stop_signal = True
                logger.info("Waiting for Browser Cleanup in Laptops")
                time.sleep(10)
                self.zoom_test_obj.app = None
                if self.dowebgui:
                    self.zoom_test_obj.stop_webui()

                if self.robot_test and api_stats_collection and not self.do_bandsteering:
                    self.zoom_test_obj.generate_report_from_data()
                elif api_stats_collection:
                    self.zoom_test_obj.generate_report_from_api()
                # self.zoom_test_obj.redis_client = None
                if self.dowebgui:
                    self.webgui_test_done("zoom")
                if self.current_exec == "parallel":
                    self.zoom_obj_dict["parallel"]["zoom_test"]["obj"] = self.zoom_test_obj
                else:
                    for i in range(len(self.zoom_obj_dict["series"])):
                        if self.zoom_obj_dict["series"][f"zoom_test_{i + 1}"]["obj"] is None:
                            self.zoom_obj_dict["series"][f"zoom_test_{i + 1}"]["obj"] = self.zoom_test_obj
                            break
                logging.info("Waiting for Browser Cleanup in Laptops")
                self.zoom_test_obj.generic_endps_profile.cleanup()
                # self.zoom_test_obj.generic_endps_profile.cleanup()
                time.sleep(10)

        return True

    def run_rb_test1(self, args):
        """
        Execute a Real Browser (RB) test.
        This configures and monitors real browser web traffic on devices.
        """
        try:
            if self.dowebgui:
                if not self.webgui_stop_check("rb"):
                    return False
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
            bssids_rb = ','.join(f for f in self.bssids)
            self.rb_test = RealBrowserTest(host=args.host,
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
                                           no_postcleanup=args.no_postcleanup,
                                           no_precleanup=args.no_precleanup,
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
                                           selected_profiles=args.profile_name,
                                           robo_ip=self.robot_ip,
                                           coordinates_list=self.coordinate_list,
                                           angles_list=self.rotation_list,
                                           do_robo=self.robot_test,
                                           rotations_enabled=self.rotation_enabled,
                                           do_bandsteering=self.do_bandsteering,
                                           bssids=bssids_rb,
                                           cycles=self.cycles,
                                           duration_to_skip=self.duration_to_skip if self.duration_to_skip else None
                                           )
            logging.info('CHECKING PORT AVAILBILITY for RB TEST')
            self.port_clean_up(5003)
            self.rb_test.change_port_to_ip()
            self.rb_test.validate_and_process_args()
            self.rb_test.config_obj = DeviceConfig.DeviceConfig(lanforge_ip=self.rb_test.host, file_name=self.rb_test.file_name, wait_time=self.rb_test.wait_time)
            # if not self.rb_test.expected_passfail_value and self.rb_test.device_csv_name is None:
            #     self.rb_test.config_self.rb_test.device_csv_file(csv_name="device.csv")
            self.rb_test.run_flask_server()
            if self.rb_test.group_name and self.rb_test.profile_name and self.rb_test.file_name:
                available_resources = self.rb_test.process_group_profiles()
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
                    'server_ip': self.rb_test.upstream_port,
                }
                available_resources = self.rb_test.process_resources(config_dict)
            if len(available_resources) != 0:
                available_resources = self.rb_test.filter_ios_devices(available_resources)
            if len(available_resources) == 0:
                logging.error("No devices available to run the test. Exiting...")
                return False

            # --- Print available resources ---
            logging.info("Devices available: {}".format(available_resources))
            if self.rb_test.expected_passfail_value or self.rb_test.device_csv_name:
                self.rb_test.update_passfail_value(available_resources)
            # --- Handle incremental values ---
            self.rb_test.handle_incremental(args, self.rb_test, available_resources, available_resources)
            self.rb_test.handle_duration()
            self.rb_test.run_test(available_resources)

        except Exception as e:
            logging.error("Error occured", e)
            # traceback.print_exc()
        finally:
            if '--help' not in sys.argv and '-h' not in sys.argv:
                if self.rb_test.do_robo and not self.do_bandsteering:
                    if self.rb_test.dowebgui:
                        self.rb_test.stop_webui_test()
                    self.rb_test.create_robo_report()
                else:
                    self.rb_test.create_report()
                    if self.rb_test.dowebgui:
                        self.rb_test.stop_webui_test()
                self.rb_test.stop()

                # if not args.no_postcleanup:
                #     self.rb_test_obj.postcleanup()
            if self.dowebgui:
                self.webgui_test_done("rb")
            self.rb_test.app = None
            if self.current_exec == "parallel":
                self.rb_obj_dict["parallel"]["rb_test"]["obj"] = self.rb_test
            else:
                for i in range(len(self.rb_obj_dict["series"])):
                    if self.rb_obj_dict["series"][f"rb_test_{i + 1}"]["obj"] is None:
                        self.rb_obj_dict["series"][f"rb_test_{i + 1}"]["obj"] = self.rb_test
                        break

        return True

    def run_rb_test(
        self,
        ssid: str = None,
        passwd: str = None,
        encryp: str = None,
        url: str = "https://google.com",
        max_speed: int = 0,
        count: int = 1,
        duration: str = None,
        test_name: str = None,
        dowebgui: bool = False,
        result_dir: str = '',
        lf_logger_config_json: str = None,
        log_level: str = None,
        debug: bool = False,
        device_list: str = None,
        webgui_incremental: str = None,
        incremental: bool = False,
        no_laptops: bool = False,
        no_postcleanup: bool = False,
        no_precleanup: bool = False,
        file_name: str = None,
        group_name: str = None,
        profile_name: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = 'DEFAULT',
        ieee80211: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = 'NA',
        private_key: str = 'NA',
        ca_cert: str = 'NA',
        client_cert: str = 'NA',
        pk_passwd: str = 'NA',
        pac_file: str = 'NA',
        upstream_port: str = 'NA',
        help_summary: str = None,
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        wait_time: int = 60,
        config: bool = False,
        exec_type: str = None,
    ):
        """
        Configure and execute a Real Browser (RB) test.
        This handles test configuration setup and delegates to `run_rb_test1`.
        """
        args = SimpleNamespace(**locals())
        args.host = self.lanforge_ip
        return self.run_rb_test1(args)

    def run_teams_test(self,
                       mgr: str = "localhost",
                       upstream_port: str = "eth1",
                       duration: int = None,
                       resources: str = None,
                       no_pre_cleanup: bool = False,
                       no_post_cleanup: bool = False,
                       log_level: str = "info",
                       lf_logger_config_json: str = None,
                       audio: bool = False,
                       video: bool = False,
                       do_webUI: bool = False,
                       testname: str = None,
                       report_dir: str = None,
                       enable_mobile_stats: bool = False,
                       robo_ip: str = None,
                       coordinates: str = None,
                       rotations: str = None,
                       do_robo: bool = False,
                       do_bs: bool = False,
                       cycles: int = 1,
                       bssids: str = None,):
        """
        Configure and execute a Microsoft Teams automation test.
        This handles Teams client configuration and interaction over devices.
        """
        try:
            if self.dowebgui:
                if not self.webgui_stop_check("teams"):
                    return False
            teams = None
            logger_config = lf_logger_config.lf_logger_config()
            self.port_clean_up(5005)
            if log_level:
                logger_config.set_level(level=log_level)

            if lf_logger_config_json:
                logger_config.lf_logger_config_json = lf_logger_config_json
                logger_config.load_lf_logger_config()

            rotations_enabled = False
            if do_robo or do_bs:
                coordinates = coordinates.split(",") if coordinates else []
                rotations = (
                    [float(angle) for angle in rotations.split(",")]
                    if rotations
                    else []
                )
                if rotations:
                    rotations_enabled = True

                if bssids:
                    bssids = bssids.split(",") if bssids else []

            teams = TeamsAutomation(
                lanforge_ip=self.lanforge_ip,
                duration=duration,
                upstream_port=upstream_port,
                no_pre_cleanup=no_pre_cleanup,
                no_post_cleanup=no_post_cleanup,
                audio=audio,
                video=video,
                do_webui=do_webUI,
                test_name=testname,
                report_dir=report_dir,
                robo_ip=robo_ip,
                coordinates=coordinates,
                rotations=rotations,
                do_robo=do_robo,
                do_bs=do_bs,
                cycles=cycles,
                bssids=bssids,
                rotations_enabled=rotations_enabled,
                enable_mobile_stats=enable_mobile_stats,
            )

            teams.upstream_port = teams.change_port_to_ip(upstream_port)

            teams.realdevice = RealDevice(
                manager_ip=self.lanforge_ip,
                server_ip="192.168.1.61",
                ssid_2g="Test Configured",
                passwd_2g="",
                encryption_2g="",
                ssid_5g="Test Configured",
                passwd_5g="",
                encryption_5g="",
                ssid_6g="Test Configured",
                passwd_6g="",
                encryption_6g="",
                selected_bands=["5G"],
            )

            teams.select_real_devices(real_sta_list=resources)
            if do_webUI:
                teams.path = report_dir
                teams.update_webui_data()
            teams.load_credentials()
            teams.handle_flask_server()
            if do_robo:
                teams.run_robo_test()
            else:
                teams.run()
                time.sleep(10)
                teams.create_avg_data()
        except Exception as e:
            logger.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
            traceback.print_exc()

        finally:
            if teams is not None:
                teams.stop_signal = True
                if do_webUI:
                    teams.stop_test_in_webui()
                teams.generate_report()
                logger.info("Waiting for Browser Cleanup at Client Side")
                time.sleep(10)
                logger.info("Browser Cleanup Completed")
                if not teams.no_post_cleanup:
                    teams.generic_endps_profile.cleanup()
                logger.info(" Teams Test Completed")
                teams.app = None
                if self.current_exec == "parallel":
                    self.teams_obj_dict["parallel"]["teams_test"]["obj"] = teams
                else:
                    for i in range(len(self.teams_obj_dict["series"])):
                        if self.teams_obj_dict["series"][f"teams_test_{i + 1}"]["obj"] is None:
                            self.teams_obj_dict["series"][f"teams_test_{i + 1}"]["obj"] = teams
                            break
        return True

    # TODO This function can be useful in future to enable real application tests to run in parallel
    def browser_cleanup(self, rb_test=False, yt_test=False):
        """
        Clean up browser processes for Real Browser (RB) or YouTube (YT) tests.
        Terminates Chrome and Chromedriver processes on Windows, Linux, and macOS endpoints.
        """
        # time.sleep(20)
        if rb_test:
            logging.info(f"laptop_os_types: {self.rb_test_obj.laptop_os_types}")
            logging.info(f"endpoints: {self.rb_test_obj.generic_endps_profile.created_endp}")
            for i in range(0, len(self.rb_test_obj.laptop_os_types)):
                if self.rb_test_obj.laptop_os_types[i] == 'windows':
                    cmd = "echo Performing POST cleanup of browser processes... & taskkill /F /IM chrome.exe /T >nul 2>&1 & taskkill /F /IM chromedriver.exe /T >nul 2>&1 & echo Browser processes terminated."  # noqa: E501
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.rb_test_obj.laptop_os_types[i] == 'linux':
                    # cmd = "su -l lanforge  ctrb.bash %s %s %s %s" % (self.rb_test_obj.new_port_list[i], self.rb_test_obj.url, self.rb_test_obj.upstream_port, self.rb_test_obj.duration)
                    cmd = "pkill -f chrome; pkill -f chromedriver"
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.rb_test_obj.laptop_os_types[i] == 'macos':
                    cmd = "pkill -f Google Chrome; pkill -f chromedriver;"
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                    if self.rb_test_obj.browser_precleanup:
                        cmd += " precleanup"
                    if self.rb_test_obj.browser_postcleanup:
                        cmd += " postcleanup"

            for _i, cx_batch in enumerate(self.rb_test_obj.cx_order_list):
                self.rb_test_obj.start_specific(cx_batch)
                logging.info(f"browser cleanup on {cx_batch}")
            logging.info('Realbrowser test laptop cleaning...')
            time.sleep(20)

        if yt_test:
            for i in range(0, len(self.yt_test_obj.real_sta_os_types)):
                if self.yt_test_obj.real_sta_os_types[i] == 'windows':
                    cmd = "echo Performing POST cleanup of browser processes... & taskkill /F /IM chrome.exe /T >nul 2>&1 & taskkill /F /IM chromedriver.exe /T >nul 2>&1 & echo Browser processes terminated."  # noqa: E501
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.yt_test_obj.real_sta_os_types[i] == 'linux':
                    cmd = "pkill -f chrome; pkill -f chromedriver"
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)

                elif self.yt_test_obj.real_sta_os_types[i] == 'macos':
                    cmd = "pkill -f Google Chrome; pkill -f chromedriver;"
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)

            self.yt_test_obj.generic_endps_profile.start_cx()
            logging.info('Youtube test laptop cleaning...')
            time.sleep(20)

        # if zoom_test:
        #     for i in range(len(self.zoom_test_obj.real_sta_os_type)):
        #         if self.zoom_test_obj.real_sta_os_type[i] == "windows":
        #             cmd = f"py zoom_client.py --ip {self.zoom_test_obj.upstream_port}"
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)
        #         elif self.zoom_test_obj.real_sta_os_type[i] == 'linux':
        #             cmd = "su -l lanforge ctzoom.bash %s %s %s" % (self.zoom_test_obj.new_port_list[i], self.zoom_test_obj.upstream_port, "client")
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)
        #         elif self.zoom_test_obj.real_sta_os_type[i] == 'macos':
        #             cmd = "sudo bash ctzoom.bash %s %s" % (self.zoom_test_obj.upstream_port, "client")
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)

        #     self.zoom_test_obj.generic_endps_profile.start_cx()

    def render_each_test(self, ce):
        """
        Renders reports and logs for each test based on whether they are run in series or parallel.
        Parses test objects and generates corresponding report structures and visualizations.
        """
        unq_tests = []
        test_map = {}
        if ce == "series":
            series_tests = self.series_tests.copy()
            for test in series_tests:
                if test not in test_map:
                    test_map[test] = 1
                    unq_tests.append(test)
                else:
                    test_map[test] += 1
        else:
            unq_tests = self.parallel_tests.copy()
        logging.info(f"series_tests: {self.series_tests}")
        logging.info(f"test_map: {test_map}")
        logging.info(f"unq_tests: {unq_tests}")
        for test_name in unq_tests:
            try:
                if test_name == "http_test":
                    """Processes HTTP test reporting and visualizations."""
                    obj_no = 1
                    obj_name = 'http_test'
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.http_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        http_data = self.http_obj_dict[ce][obj_name]["data"]

                        self.overall_report.set_obj_html(_obj_title=f'HTTP Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Setup Information")
                        self.overall_report.build_table_title()
                        curr_http_obj = copy.copy(self.http_obj_dict[ce][obj_name]["obj"])
                        if curr_http_obj.robot_test:
                            # If robot test, add robot specific info to test setup
                            http_data["test_setup_info"]["Robot IP"] = curr_http_obj.robot_ip
                            http_data["test_setup_info"]["Coordinates"] = curr_http_obj.coordinate
                            if not curr_http_obj.do_bandsteering:
                                http_data["test_setup_info"]["Rotation"] = curr_http_obj.rotation
                            else:
                                if "Traffic Duration " in http_data["test_setup_info"]:
                                    del http_data["test_setup_info"]["Traffic Duration "]
                                http_data["test_setup_info"]["No of Cycles"] = curr_http_obj.cycles
                        self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=http_data["test_setup_info"])

                        if not curr_http_obj.do_bandsteering and self.robot_test:
                            if self.dowebgui and curr_http_obj.get_live_view:
                                curr_http_obj.add_live_view_images_to_report(self.overall_report)
                            if curr_http_obj.rotation_enabled:
                                for coord, rotation_dict in curr_http_obj.robot_data.items():
                                    for rotation, _robot_info in rotation_dict.items():
                                        curr_http_obj.build_graphs_and_table(coord, rotation, self.overall_report, self.lis, [curr_http_obj.bands])
                            else:
                                for coord, _robot_info in curr_http_obj.robot_data.items():
                                    curr_http_obj.build_graphs_and_table(coord, "", self.overall_report, self.lis, [curr_http_obj.bands])
                        else:
                            if curr_http_obj.do_bandsteering:
                                curr_http_obj.get_bandsteering_stats(self.overall_report)
                            self.overall_report.set_obj_html("No of times file Downloads", "The below graph represents number of times a file downloads for each client"
                                                             ". X- axis shows “No of times file downloads and Y-axis shows "
                                                             "Client names.")
                            self.overall_report.build_objective()
                            graph2 = curr_http_obj.graph_2(http_data["dataset2"], lis=http_data["lis"], bands=http_data["bands"], graph_name=f'http_file_download_{obj_no}')
                            logging.info("graph name %s", graph2)
                            self.overall_report.set_graph_image(graph2)
                            self.overall_report.set_csv_filename(graph2)
                            self.overall_report.move_csv_file()
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_obj_html(
                                "Average time taken to download file ",
                                "The below graph represents average time taken to download for each client  "
                                ".  X- axis shows “Average time taken to download a file ” and Y-axis shows "
                                "Client names."
                            )
                            self.overall_report.build_objective()

                            graph = curr_http_obj.generate_graph(
                                dataset=http_data["dataset"], lis=http_data["lis"], bands=http_data["bands"], graph_image_name=f'http_average_time_{obj_no}')
                            self.overall_report.set_graph_image(graph)
                            self.overall_report.set_csv_filename(graph)
                            self.overall_report.move_csv_file()
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_obj_html(
                                "Download Time Table Description",
                                "This Table will provide you information of the "
                                "minimum, maximum and the average time taken by clients to download a webpage in seconds"
                            )
                            self.overall_report.build_objective()

                            curr_http_obj.response_port = curr_http_obj.local_realm.json_get("/port/all")
                            curr_http_obj.channel_list, curr_http_obj.mode_list, curr_http_obj.ssid_list = [], [], []

                            if curr_http_obj.client_type == "Real":
                                curr_http_obj.devices = curr_http_obj.devices_list
                                for interface in curr_http_obj.response_port['interfaces']:
                                    for port, port_data in interface.items():
                                        if port in curr_http_obj.port_list:
                                            curr_http_obj.channel_list.append(str(port_data['channel']))
                                            curr_http_obj.mode_list.append(str(port_data['mode']))
                                            curr_http_obj.ssid_list.append(str(port_data['ssid']))
                            elif curr_http_obj.client_type == "Virtual":
                                curr_http_obj.devices = curr_http_obj.station_list[0]
                                for interface in curr_http_obj.response_port['interfaces']:
                                    for port, port_data in interface.items():
                                        if port in curr_http_obj.station_list[0]:
                                            curr_http_obj.channel_list.append(str(port_data['channel']))
                                            curr_http_obj.mode_list.append(str(port_data['mode']))
                                            curr_http_obj.macid_list.append(str(port_data['mac']))
                                            curr_http_obj.ssid_list.append(str(port_data['ssid']))

                            z, z1, z2 = [], [], []
                            for fcc in list(http_data["result_data"].keys()):
                                z.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["min"]])
                                z1.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["max"]])
                                z2.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["avg"]])

                            download_table_value_dup = {"Minimum": z, "Maximum": z1, "Average": z2}
                            download_table_value = {"Band": http_data["bands"], "Minimum": z, "Maximum": z1, "Average": z2}

                            kpi_path = self.overall_report.get_report_path()
                            logging.info("kpi_path :%s", kpi_path)

                            kpi_csv = lf_kpi_csv.lf_kpi_csv(
                                _kpi_path=kpi_path,
                                _kpi_test_rig=http_data["test_rig"],
                                _kpi_test_tag=http_data["test_tag"],
                                _kpi_dut_hw_version=http_data["dut_hw_version"],
                                _kpi_dut_sw_version=http_data["dut_sw_version"],
                                _kpi_dut_model_num=http_data["dut_model_num"],
                                _kpi_dut_serial_num=http_data["dut_serial_num"],
                                _kpi_test_id=http_data["test_id"]
                            )
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

                            if http_data["csv_outfile"] is not None:
                                current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                                http_data["csv_outfile"] = "{}_{}-test_l3_longevity.csv".format(http_data["csv_outfile"], current_time)
                                http_data["csv_outfile"] = self.overall_report.file_add_path(http_data["csv_outfile"])
                                logging.info("csv output file : %s", http_data["csv_outfile"])

                            test_setup = pd.DataFrame(download_table_value_dup)
                            self.overall_report.set_table_dataframe(test_setup)
                            self.overall_report.build_table()

                            if curr_http_obj.group_name:
                                self.overall_report.set_table_title("Overall Results for Groups")
                            else:
                                self.overall_report.set_table_title("Overall Results")
                            self.overall_report.build_table_title()

                            if curr_http_obj.client_type == "Real":
                                if curr_http_obj.expected_passfail_value or curr_http_obj.device_csv_name:
                                    test_input_list, pass_fail_list = curr_http_obj.get_pass_fail_list(http_data["dataset2"])

                                if curr_http_obj.group_name:
                                    for key, val in curr_http_obj.group_device_map.items():
                                        if curr_http_obj.expected_passfail_value or curr_http_obj.device_csv_name:
                                            dataframe = curr_http_obj.generate_dataframe(
                                                val, curr_http_obj.devices, curr_http_obj.macid_list, curr_http_obj.channel_list,
                                                curr_http_obj.ssid_list, curr_http_obj.mode_list, http_data["dataset2"], test_input_list,
                                                http_data["dataset"], http_data["dataset1"], http_data["rx_rate"], pass_fail_list, curr_http_obj.data["total_err"]
                                            )
                                        else:
                                            dataframe = curr_http_obj.generate_dataframe(
                                                val, curr_http_obj.devices, curr_http_obj.macid_list, curr_http_obj.channel_list,
                                                curr_http_obj.ssid_list, curr_http_obj.mode_list, http_data["dataset2"], [], http_data["dataset"],
                                                http_data["dataset1"], http_data["rx_rate"], [], curr_http_obj.data["total_err"]
                                            )
                                        if dataframe:
                                            self.overall_report.set_obj_html("", "Group: {}".format(key))
                                            self.overall_report.build_objective()
                                            dataframe1 = pd.DataFrame(dataframe)
                                            self.overall_report.set_table_dataframe(dataframe1)
                                            self.overall_report.build_table()
                                else:
                                    dataframe = {
                                        " Clients": curr_http_obj.devices,
                                        " MAC ": curr_http_obj.macid_list,
                                        " Channel": curr_http_obj.channel_list,
                                        " SSID ": curr_http_obj.ssid_list,
                                        " Mode": curr_http_obj.mode_list,
                                        " No of times File downloaded ": http_data["dataset2"],
                                        " Average time taken to Download file (ms)": http_data["dataset"],
                                        " Bytes-rd (Mega Bytes) ": http_data["dataset1"],
                                        "Rx Rate (Mbps)": http_data["rx_rate"],
                                        "Failed url's": curr_http_obj.data["total_err"]
                                    }
                                    if curr_http_obj.expected_passfail_value or curr_http_obj.device_csv_name:
                                        dataframe[" Expected value of no of times file downloaded"] = test_input_list
                                        dataframe["Status"] = pass_fail_list
                                    dataframe1 = pd.DataFrame(dataframe)
                                    self.overall_report.set_table_dataframe(dataframe1)
                                    self.overall_report.build_table()
                            else:
                                dataframe = {
                                    " Clients": curr_http_obj.devices,
                                    " MAC ": curr_http_obj.macid_list,
                                    " Channel": curr_http_obj.channel_list,
                                    " SSID ": curr_http_obj.ssid_list,
                                    " Mode": curr_http_obj.mode_list,
                                    " No of times File downloaded ": http_data["dataset2"],
                                    " Average time taken to Download file (ms)": http_data["dataset"],
                                    " Bytes-rd (Mega Bytes) ": http_data["dataset1"]
                                }
                                dataframe1 = pd.DataFrame(dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                        # self.http_obj_dict[ce]
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"http_test_{obj_no}"
                        else:
                            break

                elif test_name == "ftp_test":
                    """Processes FTP test reporting and visualizations."""
                    obj_no = 1
                    obj_name = "ftp_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.ftp_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        params = self.ftp_obj_dict[ce][obj_name]["data"].copy()
                        input_setup_info = params["input_setup_info"].copy() if isinstance(params["input_setup_info"], (list, dict, set)) else params["input_setup_info"]
                        csv_outfile = params["csv_outfile"].copy() if isinstance(params["csv_outfile"], (list, dict, set)) else params["csv_outfile"]
                        report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]

                        # Optional parameter
                        config_devices = ""
                        if "config_devices" in params:
                            config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]

                        no_of_stations = ""
                        duration = ""
                        x_fig_size = 18
                        curr_ftp_obj = copy.copy(self.ftp_obj_dict[ce][obj_name]["obj"])
                        y_fig_size = len(curr_ftp_obj.real_client_list1) * .5 + 4

                        if int(curr_ftp_obj.traffic_duration) < 60:
                            duration = str(curr_ftp_obj.traffic_duration) + "s"
                        elif int(curr_ftp_obj.traffic_duration == 60) or (int(curr_ftp_obj.traffic_duration) > 60 and int(curr_ftp_obj.traffic_duration) < 3600):
                            duration = str(curr_ftp_obj.traffic_duration / 60) + "m"
                        else:
                            if int(curr_ftp_obj.traffic_duration == 3600) or (int(curr_ftp_obj.traffic_duration) > 3600):
                                duration = str(curr_ftp_obj.traffic_duration / 3600) + "h"

                        client_list = []
                        if curr_ftp_obj.clients_type == "Real":
                            client_list = curr_ftp_obj.real_client_list1
                            android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            total_devices = ""
                            for i in curr_ftp_obj.real_client_list:
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

                            if android_devices > 0:
                                total_devices += f" Android({android_devices})"
                            if windows_devices > 0:
                                total_devices += f" Windows({windows_devices})"
                            if linux_devices > 0:
                                total_devices += f" Linux({linux_devices})"
                            if mac_devices > 0:
                                total_devices += f" Mac({mac_devices})"
                        else:
                            if curr_ftp_obj.clients_type == "Virtual":
                                client_list = curr_ftp_obj.station_list
                        if 'ftp_test' not in self.test_count_dict:
                            self.test_count_dict['ftp_test'] = 0
                        self.test_count_dict['ftp_test'] += 1
                        self.overall_report.set_obj_html(_obj_title=f'FTP Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Setup Information")
                        self.overall_report.build_table_title()

                        if curr_ftp_obj.clients_type == "Virtual":
                            no_of_stations = str(len(curr_ftp_obj.station_list))
                        else:
                            no_of_stations = str(len(curr_ftp_obj.input_devices_list))

                        if curr_ftp_obj.clients_type == "Real":
                            if config_devices == "":
                                test_setup_info = {
                                    "AP Name": curr_ftp_obj.ap_name,
                                    "SSID": curr_ftp_obj.ssid,
                                    "Security": curr_ftp_obj.security,
                                    "Device List": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                                    "Failed CXs": curr_ftp_obj.failed_cx if curr_ftp_obj.failed_cx else "NONE",
                                    "File size": curr_ftp_obj.file_size,
                                    "File location": "/home/lanforge",
                                    "Traffic Direction": curr_ftp_obj.direction,
                                    "Traffic Duration ": duration
                                }
                            else:
                                group_names = ', '.join(config_devices.keys())
                                profile_names = ', '.join(config_devices.values())
                                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                                test_setup_info = {
                                    "AP Name": curr_ftp_obj.ap_name,
                                    'Configuration': configmap,
                                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                                    "File size": curr_ftp_obj.file_size,
                                    "File location": "/home/lanforge",
                                    "Traffic Direction": curr_ftp_obj.direction,
                                    "Traffic Duration ": duration
                                }
                        else:
                            test_setup_info = {
                                "AP Name": curr_ftp_obj.ap_name,
                                "SSID": curr_ftp_obj.ssid,
                                "Security": curr_ftp_obj.security,
                                "No of Devices": no_of_stations,
                                "File size": curr_ftp_obj.file_size,
                                "File location": "/home/lanforge",
                                "Traffic Direction": curr_ftp_obj.direction,
                                "Traffic Duration ": duration
                            }
                        if curr_ftp_obj.robot_test:
                            # Added Robot details in Test setup information table
                            test_setup_info["Robot IP"] = curr_ftp_obj.robot_ip
                            test_setup_info["Coordinates"] = curr_ftp_obj.coordinate
                            if not curr_ftp_obj.do_bandsteering:
                                if curr_ftp_obj.rotation_enabled:
                                    test_setup_info["Rotations"] = curr_ftp_obj.rotation
                            else:
                                if "Traffic Duration " in test_setup_info:
                                    del test_setup_info["Traffic Duration "]
                                test_setup_info["Total Cycles"] = curr_ftp_obj.cycles
                        self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

                        if not curr_ftp_obj.do_bandsteering and curr_ftp_obj.robot_test:
                            curr_ftp_obj.report = self.overall_report
                            if self.dowebgui and curr_ftp_obj.get_live_view:
                                curr_ftp_obj.add_live_view_images_to_report()
                            logging.info("real_client_list1: %s", curr_ftp_obj.real_client_list1)
                            if curr_ftp_obj.rotation_enabled:
                                for coord, rotation_dict in curr_ftp_obj.robot_data.items():
                                    for rotation, robot_info in rotation_dict.items():
                                        curr_ftp_obj.build_graphs_and_table(coord, rotation, robot_info, curr_ftp_obj.real_client_list1)
                            else:
                                for coord, robot_info in curr_ftp_obj.robot_data.items():
                                    curr_ftp_obj.build_graphs_and_table(coord, None, robot_info, curr_ftp_obj.real_client_list1)
                        else:
                            if curr_ftp_obj.do_bandsteering:
                                curr_ftp_obj.report = self.overall_report
                                curr_ftp_obj.get_bandsteering_stats()
                            self.overall_report.set_obj_html(
                                _obj_title=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}",
                                _obj=f"The below graph represents number of times a file {self.ftp_obj_dict[ce][obj_name]['obj'].direction} for each client"
                                f"(WiFi) traffic.  X- axis shows “No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}” and Y-axis shows "
                                f"Client names.")

                            self.overall_report.build_objective()
                            graph = lf_bar_graph_horizontal(_data_set=[curr_ftp_obj.url_data], _xaxis_name=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}",
                                                            _yaxis_name="Client names",
                                                            _yaxis_categories=[i for i in client_list],
                                                            _yaxis_label=[i for i in client_list],
                                                            _yaxis_step=1,
                                                            _yticks_font=8,
                                                            _yticks_rotation=None,
                                                            _graph_title=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction} (Count)",
                                                            _title_size=16,
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _color_name=['orange'],
                                                            _show_bar_value=True,
                                                            _enable_csv=True,
                                                            _graph_image_name=f"Total-url_ftp_{obj_no}", _color_edge=['black'],
                                                            _color=['orange'],
                                                            _label=[curr_ftp_obj.direction])
                            graph_png = graph.build_bar_graph_horizontal()
                            logging.info("graph name %s", graph_png)
                            self.overall_report.set_graph_image(graph_png)
                            # need to move the graph image to the results
                            self.overall_report.move_graph_image()
                            self.overall_report.set_csv_filename(graph_png)
                            self.overall_report.move_csv_file()
                            self.overall_report.build_graph()
                            self.overall_report.set_obj_html(
                                _obj_title=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file ",
                                _obj=f"The below graph represents average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} for each client  "
                                f"(WiFi) traffic.  X- axis shows “Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} a file ” and Y-axis shows "
                                f"Client names.")

                            self.overall_report.build_objective()
                            graph = lf_bar_graph_horizontal(_data_set=[curr_ftp_obj.uc_avg], _xaxis_name=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file in ms",
                                                            _yaxis_name="Client names",
                                                            _yaxis_categories=[i for i in client_list],
                                                            _yaxis_label=[i for i in client_list],
                                                            _yaxis_step=1,
                                                            _yticks_font=8,
                                                            _yticks_rotation=None,
                                                            _graph_title=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file",
                                                            _title_size=16,
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _color_name=['steelblue'],
                                                            _show_bar_value=True,
                                                            _enable_csv=True,
                                                            _graph_image_name=f"ucg-avg_ftp_{obj_no}", _color_edge=['black'],
                                                            _color=['steelblue'],
                                                            _label=[curr_ftp_obj.direction])
                            graph_png = graph.build_bar_graph_horizontal()
                            logging.info("graph name %s", graph_png)
                            self.overall_report.set_graph_image(graph_png)
                            self.overall_report.move_graph_image()
                            # need to move the graph image to the results
                            self.overall_report.set_csv_filename(graph_png)
                            self.overall_report.move_csv_file()
                            self.overall_report.build_graph()
                            if (curr_ftp_obj.dowebgui and curr_ftp_obj.get_live_view):
                                for floor in range(0, int(curr_ftp_obj.total_floors)):
                                    script_dir = os.path.dirname(os.path.abspath(__file__))
                                    throughput_image_path = os.path.join(script_dir, "heatmap_images", f"ftp_{self.ftp_obj_dict[ce][obj_name]['obj'].test_name}_{floor + 1}.png")
                                    # rssi_image_path = os.path.join(script_dir, "heatmap_images", f"{self.test_name}_rssi_{floor+1}.png")
                                    timeout = 60  # seconds
                                    start_time = time.time()

                                    while not (os.path.exists(throughput_image_path)):
                                        if time.time() - start_time > timeout:
                                            logging.warning("Timeout: Images not found within 60 seconds.")
                                            break
                                        time.sleep(1)
                                    while not os.path.exists(throughput_image_path):
                                        if os.path.exists(throughput_image_path):
                                            break
                                        # time.sleep(10)
                                    if os.path.exists(throughput_image_path):
                                        self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
                                        self.overall_report.build_custom()
                            self.overall_report.set_obj_html("File Download Time (sec)", "The below table will provide information of "
                                                             "minimum, maximum and the average time taken by clients to download a file in seconds")
                            self.overall_report.build_objective()
                            dataframe2 = {
                                "Minimum": [str(round(min(curr_ftp_obj.uc_min) / 1000, 1))],
                                "Maximum": [str(round(max(curr_ftp_obj.uc_max) / 1000, 1))],
                                "Average": [str(round((sum(curr_ftp_obj.uc_avg) / len(client_list)) / 1000, 1))]
                            }
                            dataframe3 = pd.DataFrame(dataframe2)
                            self.overall_report.set_table_dataframe(dataframe3)
                            self.overall_report.build_table()
                            self.overall_report.set_table_title("Overall Results")
                            self.overall_report.build_table_title()
                            if curr_ftp_obj.clients_type == 'Real':
                                # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
                                if curr_ftp_obj.expected_passfail_val or curr_ftp_obj.csv_name:
                                    curr_ftp_obj.get_pass_fail_list(client_list)
                                # When groups are provided a seperate table will be generated for each group using generate_dataframe
                                if curr_ftp_obj.group_name:
                                    for key, val in curr_ftp_obj.group_device_map.items():
                                        if curr_ftp_obj.expected_passfail_val or curr_ftp_obj.csv_name:
                                            dataframe = curr_ftp_obj.generate_dataframe(val, client_list, curr_ftp_obj.mac_id_list, curr_ftp_obj.channel_list, curr_ftp_obj.ssid_list, curr_ftp_obj.mode_list, curr_ftp_obj.url_data, curr_ftp_obj.test_input_list, curr_ftp_obj.uc_avg, curr_ftp_obj.bytes_rd, curr_ftp_obj.rx_rate, curr_ftp_obj.pass_fail_list, curr_ftp_obj.total_err)  # noqa: E501
                                        else:
                                            dataframe = curr_ftp_obj.generate_dataframe(val, client_list, curr_ftp_obj.mac_id_list, curr_ftp_obj.channel_list, curr_ftp_obj.ssid_list,
                                                                                        curr_ftp_obj.mode_list, curr_ftp_obj.url_data, [], curr_ftp_obj.uc_avg, curr_ftp_obj.bytes_rd, curr_ftp_obj.rx_rate, [], curr_ftp_obj.total_err)  # noqa: E501

                                        if dataframe:
                                            self.overall_report.set_obj_html("", "Group: {}".format(key))
                                            self.overall_report.build_objective()
                                            dataframe1 = pd.DataFrame(dataframe)
                                            self.overall_report.set_table_dataframe(dataframe1)
                                            self.overall_report.build_table()
                                else:
                                    dataframe = {
                                        " Clients": client_list,
                                        " MAC ": curr_ftp_obj.mac_id_list,
                                        " Channel": curr_ftp_obj.channel_list,
                                        " SSID ": curr_ftp_obj.ssid_list,
                                        " Mode": curr_ftp_obj.mode_list,
                                        " No of times File downloaded ": curr_ftp_obj.url_data,
                                        " Time Taken to Download file (ms)": curr_ftp_obj.uc_avg,
                                        " Bytes-rd (Mega Bytes)": curr_ftp_obj.bytes_rd,
                                        " RX RATE (Mbps) ": curr_ftp_obj.rx_rate,
                                        "Failed Urls": curr_ftp_obj.total_err
                                    }
                                    if curr_ftp_obj.expected_passfail_val or curr_ftp_obj.csv_name:
                                        dataframe[" Expected output "] = curr_ftp_obj.test_input_list
                                        dataframe[" Status "] = curr_ftp_obj.pass_fail_list

                                    dataframe1 = pd.DataFrame(dataframe)
                                    self.overall_report.set_table_dataframe(dataframe1)
                                    self.overall_report.build_table()

                            else:
                                dataframe = {
                                    " Clients": client_list,
                                    " MAC ": curr_ftp_obj.mac_id_list,
                                    " Channel": curr_ftp_obj.channel_list,
                                    " SSID ": curr_ftp_obj.ssid_list,
                                    " Mode": curr_ftp_obj.mode_list,
                                    " No of times File downloaded ": curr_ftp_obj.url_data,
                                    " Time Taken to Download file (ms)": curr_ftp_obj.uc_avg,
                                    " Bytes-rd (Mega Bytes)": curr_ftp_obj.bytes_rd,
                                }
                                dataframe1 = pd.DataFrame(dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                        if csv_outfile is not None:
                            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                            csv_outfile = "{}_{}-test_l4_ftp.csv".format(
                                csv_outfile, current_time)
                            csv_outfile = self.overall_report.file_add_path(csv_outfile)
                            logger.info("csv output file : {}".format(csv_outfile))
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"ftp_test_{obj_no}"
                        else:
                            break

                elif test_name == "thput_test":
                    """Processes throughput test reporting and visualizations."""
                    obj_no = 1
                    obj_name = "thput_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.thput_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'THROUGHPUT Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        # obj_name = f"thput_test_{obj_no}"
                        params = self.thput_obj_dict[ce][obj_name]["data"].copy()
                        iterations_before_test_stopped_by_user = params["iterations_before_test_stopped_by_user"].copy() if isinstance(
                            params["iterations_before_test_stopped_by_user"], (list, dict, set)) else params["iterations_before_test_stopped_by_user"]
                        incremental_capacity_list = params["incremental_capacity_list"].copy() if isinstance(
                            params["incremental_capacity_list"], (list, dict, set)) else params["incremental_capacity_list"]
                        data = params["data"].copy() if isinstance(params["data"], (list, dict, set)) else params["data"]
                        data1 = params["data1"].copy() if isinstance(params["data1"], (list, dict, set)) else params["data1"]
                        report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]
                        curr_thpt_obj = copy.copy(self.thput_obj_dict[ce][obj_name]["obj"])
                        curr_thpt_obj.ssid_list = curr_thpt_obj.get_ssid_list(curr_thpt_obj.input_devices_list)
                        curr_thpt_obj.signal_list, curr_thpt_obj.channel_list, curr_thpt_obj.mode_list, self.thput_obj_dict[ce][
                            obj_name]["obj"].link_speed_list, rx_rate_list, bssid_list = curr_thpt_obj.get_signal_and_channel_data(curr_thpt_obj.input_devices_list)
                        selected_real_clients_names = params["selected_real_clients_names"] if "selected_real_clients_names" in params else None
                        if selected_real_clients_names is not None:
                            curr_thpt_obj.num_stations = selected_real_clients_names

                        # Initialize the report object
                        if (not curr_thpt_obj.do_interopability and not self.robot_test) or (not self.thput_obj_dict[ce]
                                                                                             [obj_name]["obj"].do_interopability and self.robot_test and curr_thpt_obj.do_bandsteering):
                            # df.to_csv(os.path.join(report_path_date_time, 'throughput_data.csv'))
                            # For groups and profiles configuration through webgui

                            self.overall_report.set_obj_html(_obj_title="Input Parameters",
                                                             _obj="The below tables provides the input parameters for the test")
                            self.overall_report.build_objective()

                            # Initialize counts and lists for device types
                            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            packet_size_text = ''
                            total_devices = ""
                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                packet_size_text = 'AUTO'
                            else:
                                packet_size_text = str(curr_thpt_obj.cx_profile.side_a_min_pdu) + ' Bytes'
                            # Determine load type name based on curr_thpt_obj.load_type
                            if curr_thpt_obj.load_type == "wc_intended_load":
                                load_type_name = "Intended Load"
                            else:
                                load_type_name = "Per Client Load"
                            for i in curr_thpt_obj.real_client_list:
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

                            # Determine incremental_capacity_data based on curr_thpt_obj.incremental_capacity
                            if curr_thpt_obj.gave_incremental:
                                incremental_capacity_data = "No Incremental values provided"
                            elif len(curr_thpt_obj.incremental_capacity) == 1:
                                if len(incremental_capacity_list) == 1:
                                    incremental_capacity_data = str(curr_thpt_obj.incremental_capacity[0])
                                else:
                                    incremental_capacity_data = ','.join(map(str, incremental_capacity_list))
                            elif (len(curr_thpt_obj.incremental_capacity) > 1):
                                curr_thpt_obj.incremental_capacity = curr_thpt_obj.incremental_capacity.split(',')
                                incremental_capacity_data = ', '.join(curr_thpt_obj.incremental_capacity)
                            else:
                                incremental_capacity_data = "None"

                            # Construct test_setup_info dictionary for test setup table
                            if curr_thpt_obj.group_name:
                                group_names = ', '.join(curr_thpt_obj.configdevices.keys())
                                profile_names = ', '.join(curr_thpt_obj.configdevices.values())
                                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                                test_setup_info = {
                                    "Test name": curr_thpt_obj.test_name,
                                    "Configuration": configmap,
                                    "Configured Devices": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                    "Increment": incremental_capacity_data,
                                    "Traffic Duration in minutes": round(int(curr_thpt_obj.test_duration) * len(incremental_capacity_list) / 60, 2),
                                    "Traffic Type": (curr_thpt_obj.traffic_type.strip("lf_")).upper(),
                                    "Traffic Direction": curr_thpt_obj.direction,
                                    "Upload Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                    "Download Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                    "Load Type": load_type_name,
                                    "Packet Size": packet_size_text
                                }
                            else:
                                test_setup_info = {
                                    "Test name": curr_thpt_obj.test_name,
                                    "Device List": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                    "Increment": incremental_capacity_data,
                                    "Traffic Duration in minutes": round(int(curr_thpt_obj.test_duration) * len(incremental_capacity_list) / 60, 2),
                                    "Traffic Type": (curr_thpt_obj.traffic_type.strip("lf_")).upper(),
                                    "Traffic Direction": curr_thpt_obj.direction,
                                    "Upload Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                    "Download Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                    "Load Type": load_type_name,
                                    "Packet Size": packet_size_text
                                }
                            self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

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

                                # for sig in curr_thpt_obj.signal_list[0:int(incremental_capacity_list[i])]:
                                #     signal_data.append(int(sig)*(-1))
                                # rssi_signal_data.append(signal_data)

                                # Fetch devices_on_running from real_client_list
                                for j in range(data1[i][-1]):
                                    devices_on_running.append(curr_thpt_obj.real_client_list[j].split(" ")[-1])

                                # Fetch download_data and upload_data based on load_type and direction
                                for k in devices_on_running:
                                    # individual_device_data=[]

                                    # Checking individual device download and upload rate by searching device name in dataframe
                                    columns_with_substring = [col for col in data_iter.columns if k in col]
                                    filtered_df = data_iter[columns_with_substring]
                                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()
                                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()
                                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                                    if curr_thpt_obj.load_type == "wc_intended_load":
                                        if curr_thpt_obj.direction == "Bi-direction":

                                            # Append average download and upload data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append average upload and download drop from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)

                                        elif curr_thpt_obj.direction == 'Download':

                                            # Append average download data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))

                                            # Append 0 for upload data
                                            upload_data.append(0)

                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                            # Append average download drop data from filtered dataframe

                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)

                                        elif curr_thpt_obj.direction == 'Upload':

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))

                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                            # Append Average upload data from filtered dataframe
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append 0 for download data
                                            download_data.append(0)
                                            # Append average upload drop data from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)

                                    else:

                                        if curr_thpt_obj.direction == "Bi-direction":
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
                                            upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                            download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))

                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)
                                        elif curr_thpt_obj.direction == 'Download':

                                            # Append average download data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))
                                            # Append 0 for upload data
                                            upload_data.append(0)
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                            download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))
                                            # Append average download drop data from filtered dataframe
                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)
                                        elif curr_thpt_obj.direction == 'Upload':

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                                            download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            # Append average upload data from filtered dataframe
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append average upload drop data from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))

                                            # Append 0 for download data
                                            download_data.append(0)

                                            if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                            direction_in_table.append(curr_thpt_obj.direction)
                                data_set_in_graph = []

                                # Depending on the test direction, retrieve corresponding throughput data,
                                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                                if curr_thpt_obj.direction == "Bi-direction":
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

                                elif curr_thpt_obj.direction == 'Download':
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    label_data = ['Download']
                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))), 2)} Mbps"

                                elif curr_thpt_obj.direction == 'Upload':
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Upload']
                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])), 2)} Mbps"

                                if len(incremental_capacity_list) > 1:
                                    self.overall_report.set_custom_html(f"<h2><u>Iteration-{i + 1}: Number of Devices Running : {len(devices_on_running)}</u></h2>")
                                    self.overall_report.build_custom()

                                self.overall_report.set_obj_html(
                                    _obj_title=f"{real_time_data}",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph_png = curr_thpt_obj.build_line_graph(
                                    data_set=data_set_in_graph,
                                    xaxis_name="Time",
                                    yaxis_name="Throughput (Mbps)",
                                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                                    label=label_data,
                                    graph_image_name=f"line_graph{i}"
                                )
                                logger.info("graph name {}".format(graph_png))
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()

                                self.overall_report.build_graph()
                                x_fig_size = 15
                                y_fig_size = len(devices_on_running) * .5 + 4
                                self.overall_report.set_obj_html(
                                    _obj_title="Per Client Avg-Throughput",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                                _xaxis_name="Avg Throughput(Mbps)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"image_name{i}_{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_obj_html(
                                    _obj_title="RSSI Of The Clients Connected",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                                _xaxis_name="Signal(-dBm)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"signal_image_name{i}_{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                if (curr_thpt_obj.do_bandsteering):
                                    curr_thpt_obj.get_bandsteering_stats(self.overall_report, data, devices_on_running_trimmed)
                                if (curr_thpt_obj.dowebgui and curr_thpt_obj.get_live_view):
                                    curr_thpt_obj.add_live_view_images_to_report(self.overall_report)

                                if curr_thpt_obj.group_name:
                                    self.overall_report.set_obj_html(
                                        _obj_title="Detailed Result Table For Groups ",
                                        _obj="The below tables provides detailed information for the throughput test on each group.")
                                else:

                                    self.overall_report.set_obj_html(
                                        _obj_title="Detailed Result Table ",
                                        _obj="The below tables provides detailed information for the throughput test on each device.")
                                self.overall_report.build_objective()
                                curr_thpt_obj.mac_id_list = [item.split()[-1] if ' ' in item else item for item in curr_thpt_obj.mac_id_list]
                                if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                    test_input_list, pass_fail_list = curr_thpt_obj.get_pass_fail_list(
                                        device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                                if curr_thpt_obj.group_name:
                                    for key, val in curr_thpt_obj.group_device_map.items():
                                        if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                            # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                                            dataframe = curr_thpt_obj.generate_dataframe(val,
                                                                                         device_type[0:int(incremental_capacity_list[i])],
                                                                                         devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.ssid_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.mac_id_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.channel_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.mode_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                         download_list[0:int(incremental_capacity_list[i])],
                                                                                         [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                         [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                         upload_list[0:int(incremental_capacity_list[i])],
                                                                                         [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                         ['' if n == 0 else '-' +
                                                                                          str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                         test_input_list,
                                                                                         curr_thpt_obj.link_speed_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                         pass_fail_list,
                                                                                         upload_drop,
                                                                                         download_drop)
                                        # Generating Dataframe for groups when pass_fail case is not specified
                                        else:
                                            dataframe = curr_thpt_obj.generate_dataframe(val,
                                                                                         device_type[0:int(incremental_capacity_list[i])],
                                                                                         devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.ssid_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.mac_id_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.channel_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         curr_thpt_obj.mode_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                         download_list[0:int(incremental_capacity_list[i])],
                                                                                         [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                         [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                         upload_list[0:int(incremental_capacity_list[i])],
                                                                                         [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                         ['' if n == 0 else '-' +
                                                                                          str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                         [],
                                                                                         curr_thpt_obj.link_speed_list[0:int(
                                                                                             incremental_capacity_list[i])],
                                                                                         [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                         [],
                                                                                         upload_drop,
                                                                                         download_drop)
                                        if dataframe:
                                            self.overall_report.set_obj_html("", "Group: {}".format(key))
                                            self.overall_report.build_objective()
                                            dataframe1 = pd.DataFrame(dataframe)
                                            self.overall_report.set_table_dataframe(dataframe1)
                                            self.overall_report.build_table()
                                else:
                                    bk_dataframe = {
                                        " Device Type ": device_type[0:int(incremental_capacity_list[i])],
                                        " Username": devices_on_running[0:int(incremental_capacity_list[i])],
                                        " SSID ": curr_thpt_obj.ssid_list[0:int(incremental_capacity_list[i])],
                                        " MAC ": curr_thpt_obj.mac_id_list[0:int(incremental_capacity_list[i])],
                                        " Channel ": curr_thpt_obj.channel_list[0:int(incremental_capacity_list[i])],
                                        " Mode": curr_thpt_obj.mode_list[0:int(incremental_capacity_list[i])],
                                        # " Direction":direction_in_table[0:int(incremental_capacity_list[i])],
                                        " Offered download rate (Mbps) ": download_list[0:int(incremental_capacity_list[i])],
                                        " Observed Average download rate (Mbps) ": [str(n) for n in download_data[0:int(incremental_capacity_list[i])]],
                                        " Offered upload rate (Mbps) ": upload_list[0:int(incremental_capacity_list[i])],
                                        " Observed Average upload rate (Mbps) ": [str(n) for n in upload_data[0:int(incremental_capacity_list[i])]],
                                        " RSSI (dBm) ": ['' if n == 0 else '-' + str(n) for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                        # " Link Speed ":curr_thpt_obj.link_speed_list[0:int(incremental_capacity_list[i])],
                                        " Average RTT (ms)": avg_rtt_data[0:int(incremental_capacity_list[i])],
                                        " Packet Size(Bytes) ": [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                    }
                                    if curr_thpt_obj.direction == "Bi-direction":
                                        bk_dataframe[" Average Tx Drop % "] = upload_drop
                                        bk_dataframe[" Average Rx Drop % "] = download_drop
                                    elif curr_thpt_obj.direction == 'Download':
                                        bk_dataframe[" Average Rx Drop % "] = download_drop
                                        # adding rx drop while uploading as 0
                                        bk_dataframe[" Average Tx Drop % "] = [0.0] * len(download_drop)

                                    else:
                                        bk_dataframe[" Average Tx Drop % "] = upload_drop
                                        # adding rx drop while downloading as 0
                                        bk_dataframe[" Average Rx Drop % "] = [0.0] * len(upload_drop)
                                    if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                        bk_dataframe[" Expected " + curr_thpt_obj.direction + " rate "] = [str(n) + " Mbps" for n in test_input_list]
                                        bk_dataframe[" Status "] = pass_fail_list
                                    dataframe1 = pd.DataFrame(bk_dataframe)
                                    self.overall_report.set_table_dataframe(dataframe1)
                                    self.overall_report.build_table()

                                self.overall_report.set_custom_html('<hr>')
                                self.overall_report.build_custom()

                        elif not curr_thpt_obj.do_interopability and self.robot_test:
                            if curr_thpt_obj.do_interopability is False:
                                self.overall_report.set_obj_html(_obj_title="Input Parameters",
                                                                 _obj="The below tables provides the input parameters for the test")
                                self.overall_report.build_objective()

                                # Initialize counts and lists for device types
                                android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
                                all_devices_names = []
                                device_type = []
                                packet_size_text = ''
                                total_devices = ""
                                if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                    packet_size_text = 'AUTO'
                                else:
                                    packet_size_text = str(curr_thpt_obj.cx_profile.side_a_min_pdu) + ' Bytes'
                                # Determine load type name based on curr_thpt_obj.load_type
                                if curr_thpt_obj.load_type == "wc_intended_load":
                                    load_type_name = "Intended Load"
                                else:
                                    load_type_name = "Per Client Load"
                                for i in curr_thpt_obj.real_client_list:
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

                                # Determine incremental_capacity_data based on curr_thpt_obj.incremental_capacity
                                if curr_thpt_obj.gave_incremental:
                                    incremental_capacity_data = "No Incremental values provided"
                                elif len(curr_thpt_obj.incremental_capacity) == 1:
                                    if len(incremental_capacity_list) == 1:
                                        incremental_capacity_data = str(curr_thpt_obj.incremental_capacity[0])
                                    else:
                                        incremental_capacity_data = ','.join(map(str, incremental_capacity_list))
                                elif (len(curr_thpt_obj.incremental_capacity) > 1):
                                    curr_thpt_obj.incremental_capacity = curr_thpt_obj.incremental_capacity.split(',')
                                    incremental_capacity_data = ', '.join(curr_thpt_obj.incremental_capacity)
                                else:
                                    incremental_capacity_data = "None"

                                # Construct test_setup_info dictionary for test setup table
                                if curr_thpt_obj.group_name:
                                    group_names = ', '.join(curr_thpt_obj.configdevices.keys())
                                    profile_names = ', '.join(curr_thpt_obj.configdevices.values())
                                    configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                                    test_setup_info = {
                                        "Test name": curr_thpt_obj.test_name,
                                        "Configuration": configmap,
                                        "Configured Devices": ", ".join(all_devices_names),
                                        # "No of Devices": "Total" + f"({str(curr_thpt_obj.num_stations)})" + total_devices,
                                        "No of Devices": f"Total ({self.thput_obj_dict[ce][obj_name]['obj'].num_stations}) {total_devices}",
                                        "Increment": incremental_capacity_data,
                                        "Traffic Duration in minutes": round(int(curr_thpt_obj.test_duration) * len(incremental_capacity_list) / 60, 2),
                                        "Traffic Type": (curr_thpt_obj.traffic_type.strip("lf_")).upper(),
                                        "Traffic Direction": curr_thpt_obj.direction,
                                        "Upload Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                        "Download Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                        "Load Type": load_type_name,
                                        "Packet Size": packet_size_text
                                    }
                                else:
                                    test_setup_info = {
                                        "Test name": curr_thpt_obj.test_name,
                                        "Device List": ", ".join(all_devices_names),
                                        # "No of Devices": "Total" + f"({str(curr_thpt_obj.num_stations)})" + total_devices,
                                        "No of Devices": f"Total ({self.thput_obj_dict[ce][obj_name]['obj'].num_stations}) {total_devices}",
                                        "Increment": incremental_capacity_data,
                                        "Traffic Duration in minutes": round(int(curr_thpt_obj.test_duration) * len(incremental_capacity_list) / 60, 2),
                                        "Traffic Type": (curr_thpt_obj.traffic_type.strip("lf_")).upper(),
                                        "Traffic Direction": curr_thpt_obj.direction,
                                        "Upload Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                        "Download Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                        "Load Type": load_type_name,
                                        "Packet Size": packet_size_text
                                    }
                                # Add robot IP, completed coordinates, and selected angles to the test summary
                                test_setup_info["ROBOT IP"] = curr_thpt_obj.robo_ip
                                test_setup_info["Selected Coordinates"] = ",".join(curr_thpt_obj.coordinates_completed)
                                if curr_thpt_obj.rotation_enabled:
                                    test_setup_info["Selected Angles"] = ",".join(curr_thpt_obj.angle_list)

                                self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

                                # Add live view images in case of robot testing from webui
                                if curr_thpt_obj.dowebgui:

                                    throughput_image_path = os.path.join(
                                        curr_thpt_obj.result_dir,
                                        "live_view_images",
                                        f"{curr_thpt_obj.test_name}_throughput.png"
                                    )

                                    rssi_image_path = os.path.join(
                                        curr_thpt_obj.result_dir,
                                        "live_view_images",
                                        f"{curr_thpt_obj.test_name}_rssi.png"
                                    )
                                    timeout = 300  # seconds
                                    start_time = time.time()

                                    while not (os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path)):
                                        if time.time() - start_time > timeout:
                                            logging.warning("Timeout: Images not found within 300 seconds.")
                                            break
                                        time.sleep(1)

                                    if os.path.exists(throughput_image_path):
                                        self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html("<h2>Average Throughput Heatmap: </h2>")
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}" style="width:1500px; height:900px;"></img>')
                                        self.overall_report.build_custom()

                                    if os.path.exists(rssi_image_path):
                                        self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html("<h2>Average RSSI Heatmap: </h2>")
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html(f'<img src="file://{rssi_image_path}" style="width:1500px; height:900px;"></img>')
                                        self.overall_report.build_custom()
                                # Loop through each coordinate
                                for i, coordinate in enumerate(curr_thpt_obj.coordinates_completed):

                                    self.overall_report.set_obj_html(
                                        _obj_title=f"<h3 style='text-decoration: underline;'>Throughput Test Details – Robot Position: Point {coordinate}</h3>",
                                        _obj=" ")
                                    self.overall_report.build_objective()
                                    logging.info("Result directory: %s", curr_thpt_obj.result_dir)
                                    coordinate_csv = f"{coordinate}_throughput_data.csv"
                                    file_path = os.path.join(curr_thpt_obj.result_dir, coordinate_csv)
                                    data = pd.read_csv(file_path)

                                    for angle in curr_thpt_obj.angle_list:
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

                                            # for sig in curr_thpt_obj.signal_list[0:int(incremental_capacity_list[i])]:
                                            #     signal_data.append(int(sig)*(-1))
                                            # rssi_signal_data.append(signal_data)

                                            # Fetch devices_on_running from real_client_list
                                            for j in range(data1[i][-1]):
                                                devices_on_running.append(curr_thpt_obj.real_client_list[j].split(" ")[-1])

                                            # Fetch download_data and upload_data based on load_type and direction
                                            for k in devices_on_running:
                                                # individual_device_data=[]

                                                # Checking individual device download and upload rate by searching device name in dataframe
                                                columns_with_substring = [col for col in data_iter.columns if k in col]
                                                if curr_thpt_obj.rotation_enabled:
                                                    angle = float(angle)
                                                    filtered_df = data_iter.loc[data_iter["Angle"] == angle, columns_with_substring]
                                                else:
                                                    filtered_df = data_iter[columns_with_substring]
                                                download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                                                upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                                                upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()
                                                download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()
                                                rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                                                if curr_thpt_obj.load_type == "wc_intended_load":
                                                    if curr_thpt_obj.direction == "Bi-direction":

                                                        # Append average download and upload data from filtered dataframe
                                                        download_data.append(round(sum(download_col) / len(download_col), 2))
                                                        upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                                        # Append average upload and download drop from filtered dataframe
                                                        upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                                        download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                                        rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                                        # Calculate and append upload and download throughput to lists
                                                        upload_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                                        download_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)

                                                    elif curr_thpt_obj.direction == 'Download':

                                                        # Append average download data from filtered dataframe
                                                        download_data.append(round(sum(download_col) / len(download_col), 2))

                                                        # Append 0 for upload data
                                                        upload_data.append(0)

                                                        rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                                        # Calculate and append upload and download throughput to lists
                                                        upload_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                                        download_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                                        # Append average download drop data from filtered dataframe

                                                        download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)

                                                    elif curr_thpt_obj.direction == 'Upload':

                                                        # Calculate and append upload and download throughput to lists
                                                        upload_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                                        download_list.append(
                                                            str(round((int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))

                                                        rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                                        # Append Average upload data from filtered dataframe
                                                        upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                                        # Append 0 for download data
                                                        download_data.append(0)
                                                        # Append average upload drop data from filtered dataframe
                                                        upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)

                                                else:

                                                    if curr_thpt_obj.direction == "Bi-direction":
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
                                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))

                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)
                                                    elif curr_thpt_obj.direction == 'Download':

                                                        # Append average download data from filtered dataframe
                                                        download_data.append(round(sum(download_col) / len(download_col), 2))
                                                        # Append 0 for upload data
                                                        upload_data.append(0)
                                                        rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                                        # Calculate and append upload and download throughput to lists
                                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))
                                                        # Append average download drop data from filtered dataframe
                                                        download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)
                                                    elif curr_thpt_obj.direction == 'Upload':

                                                        # Calculate and append upload and download throughput to lists
                                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                                                        rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                                        # Append average upload data from filtered dataframe
                                                        upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                                        # Append average upload drop data from filtered dataframe
                                                        upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))

                                                        # Append 0 for download data
                                                        download_data.append(0)

                                                        if curr_thpt_obj.cx_profile.side_a_min_pdu == -1:
                                                            packet_size_in_table.append('AUTO')
                                                        else:
                                                            packet_size_in_table.append(curr_thpt_obj.cx_profile.side_a_min_pdu)
                                                        direction_in_table.append(curr_thpt_obj.direction)

                                            data_set_in_graph = []
                                            data_for_angle = []
                                            if curr_thpt_obj.rotation_enabled:
                                                angle = float(angle)
                                                data_for_angle = data[data["Angle"] == angle]
                                            # Depending on the test direction, retrieve corresponding throughput data,
                                            # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                                            if curr_thpt_obj.direction == "Bi-direction":
                                                if curr_thpt_obj.rotation_enabled:
                                                    download_values_list = data_for_angle['Overall Download'][data_for_angle['Iteration'] == i + 1].values.tolist()
                                                    upload_values_list = data_for_angle['Overall Upload'][data_for_angle['Iteration'] == i + 1].values.tolist()
                                                else:
                                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                                data_set_in_graph.append(download_values_list)
                                                data_set_in_graph.append(upload_values_list)
                                                devices_data_to_create_bar_graph.append(download_data)
                                                devices_data_to_create_bar_graph.append(upload_data)
                                                label_data = ['Download', 'Upload']
                                                if not curr_thpt_obj.rotation_enabled:
                                                    real_time_data = (
                                                        f"Real Time Throughput: Achieved Throughput: Download:{round(sum(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "
                                                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                                    )
                                                else:
                                                    real_time_data = (
                                                        f"Real Time Throughput: Achieved Throughput At Angle {angle}: Download: {round(sum(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "  # noqa: E501
                                                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                                    )

                                            elif curr_thpt_obj.direction == 'Download':
                                                if curr_thpt_obj.rotation_enabled:
                                                    download_values_list = data_for_angle['Overall Download'][data_for_angle['Iteration'] == i + 1].values.tolist()
                                                else:
                                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                                data_set_in_graph.append(download_values_list)
                                                devices_data_to_create_bar_graph.append(download_data)
                                                label_data = ['Download']
                                                if not curr_thpt_obj.rotation_enabled:
                                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))), 2)} Mbps"  # noqa E501
                                                else:
                                                    real_time_data = (
                                                        f"Real Time Throughput: Achieved Throughput At Angle {angle}: "
                                                        f"Download : "
                                                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                                    )

                                            elif curr_thpt_obj.direction == 'Upload':
                                                if curr_thpt_obj.rotation_enabled:
                                                    upload_values_list = data_for_angle['Overall Upload'][data_for_angle['Iteration'] == i + 1].values.tolist()
                                                else:
                                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                                data_set_in_graph.append(upload_values_list)
                                                devices_data_to_create_bar_graph.append(upload_data)
                                                label_data = ['Upload']
                                                if not curr_thpt_obj.rotation_enabled:
                                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])), 2)} Mbps"
                                                else:
                                                    real_time_data = (
                                                        f"Real Time Throughput: Achieved Throughput At Angle {angle}: "
                                                        f"Upload : "
                                                        f"{round(sum(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                                    )

                                            if len(incremental_capacity_list) > 1:
                                                self.overall_report.set_custom_html(f"<h2><u>Iteration-{i + 1}: Number of Devices Running : {len(devices_on_running)}</u></h2>")
                                                self.overall_report.build_custom()

                                            self.overall_report.set_obj_html(
                                                _obj_title=f"{real_time_data}",
                                                _obj=" ")
                                            self.overall_report.build_objective()
                                            if curr_thpt_obj.rotation_enabled:
                                                xaxis_categories = data_for_angle['TIMESTAMP'][data_for_angle['Iteration'] == i + 1].values.tolist()
                                                graph_image_name = "line_graph{}_{}_{}".format(coordinate, angle, i)
                                            else:
                                                xaxis_categories = data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist()
                                                graph_image_name = "line_graph{}_{}".format(coordinate, i)
                                            graph_png = curr_thpt_obj.build_line_graph(
                                                data_set=data_set_in_graph,
                                                xaxis_name="Time",
                                                yaxis_name="Throughput (Mbps)",
                                                xaxis_categories=xaxis_categories,
                                                label=label_data,
                                                graph_image_name=graph_image_name
                                            )
                                            logger.info("graph name {}".format(graph_png))
                                            self.overall_report.set_graph_image(graph_png)
                                            self.overall_report.move_graph_image()

                                            self.overall_report.build_graph()

                                            if curr_thpt_obj.group_name:
                                                self.overall_report.set_obj_html(
                                                    _obj_title="Detailed Result Table For Groups ",
                                                    _obj="The below tables provides detailed information for the throughput test on each group.")
                                            else:

                                                self.overall_report.set_obj_html(
                                                    _obj_title="Detailed Result Table ",
                                                    _obj="The below tables provides detailed information for the throughput test on each device.")
                                            self.overall_report.build_objective()
                                            curr_thpt_obj.mac_id_list = [
                                                item.split()[-1] if ' ' in item else item for item in curr_thpt_obj.mac_id_list]
                                            if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                                test_input_list, pass_fail_list = curr_thpt_obj.get_pass_fail_list(
                                                    device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                                            if curr_thpt_obj.group_name:
                                                for key, val in curr_thpt_obj.group_device_map.items():
                                                    if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                                        # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                                                        dataframe = curr_thpt_obj.generate_dataframe(val,
                                                                                                     device_type[0:int(incremental_capacity_list[i])],
                                                                                                     devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.ssid_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.mac_id_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.channel_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.mode_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                                     download_list[0:int(incremental_capacity_list[i])],
                                                                                                     [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                                     [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                                     upload_list[0:int(incremental_capacity_list[i])],
                                                                                                     [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                                     ['' if n == 0 else '-' +
                                                                                                      str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                                     test_input_list,
                                                                                                     curr_thpt_obj.link_speed_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                                     pass_fail_list,
                                                                                                     upload_drop,
                                                                                                     download_drop)
                                                    # Generating Dataframe for groups when pass_fail case is not specified
                                                    else:
                                                        dataframe = curr_thpt_obj.generate_dataframe(val,
                                                                                                     device_type[0:int(incremental_capacity_list[i])],
                                                                                                     devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.ssid_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.mac_id_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.channel_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     curr_thpt_obj.mode_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                                     download_list[0:int(incremental_capacity_list[i])],
                                                                                                     [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                                     [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                                     upload_list[0:int(incremental_capacity_list[i])],
                                                                                                     [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                                     ['' if n == 0 else '-' +
                                                                                                      str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                                     [],
                                                                                                     curr_thpt_obj.link_speed_list[0:int(
                                                                                                         incremental_capacity_list[i])],
                                                                                                     [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                                     [],
                                                                                                     upload_drop,
                                                                                                     download_drop)
                                                    if dataframe:
                                                        self.overall_report.set_obj_html("", "Group: {}".format(key))
                                                        self.overall_report.build_objective()
                                                        dataframe1 = pd.DataFrame(dataframe)
                                                        self.overall_report.set_table_dataframe(dataframe1)
                                                        self.overall_report.build_table()
                                            else:
                                                bk_dataframe = {
                                                    " Device Type ": device_type[0:int(incremental_capacity_list[i])],
                                                    " Username": devices_on_running[0:int(incremental_capacity_list[i])],
                                                    " SSID ": curr_thpt_obj.ssid_list[0:int(incremental_capacity_list[i])],
                                                    " MAC ": curr_thpt_obj.mac_id_list[0:int(incremental_capacity_list[i])],
                                                    " Channel ": curr_thpt_obj.channel_list[0:int(incremental_capacity_list[i])],
                                                    " Mode": curr_thpt_obj.mode_list[0:int(incremental_capacity_list[i])],
                                                    # " Direction":direction_in_table[0:int(incremental_capacity_list[i])],
                                                    " Offered download rate (Mbps) ": download_list[0:int(incremental_capacity_list[i])],
                                                    " Observed Average download rate (Mbps) ": [str(n) for n in download_data[0:int(incremental_capacity_list[i])]],
                                                    " Offered upload rate (Mbps) ": upload_list[0:int(incremental_capacity_list[i])],
                                                    " Observed Average upload rate (Mbps) ": [str(n) for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                    " RSSI (dBm) ": ['' if n == 0 else '-' + str(n) for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                    # " Link Speed ":self.link_speed_list[0:int(incremental_capacity_list[i])],
                                                    " Average RTT (ms)": avg_rtt_data[0:int(incremental_capacity_list[i])],
                                                    " Packet Size(Bytes) ": [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                }
                                                if curr_thpt_obj.direction == "Bi-direction":
                                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                                elif curr_thpt_obj.direction == 'Download':
                                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                                    # adding rx drop while uploading as 0
                                                    bk_dataframe[" Average Tx Drop % "] = [0.0] * len(download_drop)

                                                else:
                                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                                    # adding rx drop while downloading as 0
                                                    bk_dataframe[" Average Rx Drop % "] = [0.0] * len(upload_drop)
                                                if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                                    bk_dataframe[" Expected " + curr_thpt_obj.direction + " rate "] = [str(n) + " Mbps" for n in test_input_list]
                                                    bk_dataframe[" Status "] = pass_fail_list
                                                dataframe1 = pd.DataFrame(bk_dataframe)
                                                self.overall_report.set_table_dataframe(dataframe1)
                                                self.overall_report.build_table()

                                                if coordinate in curr_thpt_obj.battery_log:
                                                    if curr_thpt_obj.rotation_enabled and (angle in curr_thpt_obj.battery_log[coordinate]):
                                                        self.overall_report.set_custom_html(
                                                            f"<h2>Robot went to charging Dock at {curr_thpt_obj.battery_log[coordinate][angle]}</h2>"
                                                        )
                                                        self.overall_report.build_custom()
                                                    else:
                                                        self.overall_report.set_custom_html(
                                                            f"<h2>Robot went to charging Dock at {curr_thpt_obj.battery_log[coordinate]}</h2>"
                                                        )
                                                        self.overall_report.build_custom()

                                            self.overall_report.set_custom_html('<hr>')
                                            self.overall_report.build_custom()

                        elif curr_thpt_obj.do_interopability:

                            self.overall_report.set_obj_html(_obj_title="Input Parameters",
                                                             _obj="The below tables provides the input parameters for the test")
                            self.overall_report.build_objective()

                            # Initialize counts and lists for device types
                            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            total_devices = ""

                            for i in curr_thpt_obj.real_client_list:
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
                                "Test name": curr_thpt_obj.test_name,
                                "Device List": ", ".join(all_devices_names),
                                "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                "Traffic Duration in minutes": round(int(curr_thpt_obj.test_duration) * len(incremental_capacity_list) / 60, 2),
                                "Traffic Type": (curr_thpt_obj.traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": curr_thpt_obj.direction,
                                "Upload Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                "Download Rate(Mbps)": str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                # "Packet Size" : str(curr_thpt_obj.cx_profile.side_a_min_pdu) + " Bytes"
                            }
                            self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

                            if (curr_thpt_obj.interopability_config):

                                self.overall_report.set_obj_html(_obj_title="Configuration Status of Devices",
                                                                 _obj="The table below shows the configuration status of each device (except iOS) with respect to the SSID connection.")
                                self.overall_report.build_objective()

                                configured_dataframe = curr_thpt_obj.convert_to_table(curr_thpt_obj.configured_devices_check)
                                dataframe1 = pd.DataFrame(configured_dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

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
                                devices_on_running.append(curr_thpt_obj.real_client_list[data1[i][-1] - 1].split(" ")[-1])

                                if curr_thpt_obj.interopability_config and devices_on_running[0] in self.thput_obj_dict[ce][obj_name][
                                        "obj"].configured_devices_check and not curr_thpt_obj.configured_devices_check[devices_on_running[0]]:
                                    continue

                                for k in devices_on_running:
                                    # individual_device_data=[]

                                    # Checking individual device download and upload rate by searching device name in dataframe
                                    columns_with_substring = [col for col in data_iter.columns if k in col]
                                    filtered_df = data_iter[columns_with_substring]
                                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()
                                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop" in col][0]].values.tolist()
                                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                                    dl_len = len(filtered_df)
                                    ul_len = len(filtered_df)
                                    if curr_thpt_obj.direction == "Bi-direction":

                                        # Append download and upload data from filtered dataframe
                                        download_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        upload_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        upload_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        download_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                                   len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))

                                        direction_in_table.append(curr_thpt_obj.direction)
                                    elif curr_thpt_obj.direction == 'Download':

                                        # Append download data from filtered dataframe
                                        download_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))

                                        # Append 0 for upload data
                                        upload_data.append(0)
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                                   len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        download_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))

                                        direction_in_table.append(curr_thpt_obj.direction)
                                    elif curr_thpt_obj.direction == 'Upload':

                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(curr_thpt_obj.cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(curr_thpt_obj.cx_profile.side_b_min_bps) / 1000000, 2)))
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                                   len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        upload_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Append upload data from filtered dataframe
                                        upload_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))

                                        # Append 0 for download data
                                        download_data.append(0)

                                        direction_in_table.append(curr_thpt_obj.direction)
                                data_set_in_graph = []

                                # Depending on the test direction, retrieve corresponding throughput data,
                                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                                if curr_thpt_obj.direction == "Bi-direction":
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

                                elif curr_thpt_obj.direction == 'Download':
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    label_data = ['Download']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Download: "
                                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]) / len(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                elif curr_thpt_obj.direction == 'Upload':
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Upload']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Upload: "
                                        f"{round(sum(upload_data[0:int(incremental_capacity_list[i])]) / len(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                self.overall_report.set_custom_html(f"<h2><u>{i + 1}. Test On Device {', '.join(devices_on_running)}:</u></h2>")
                                self.overall_report.build_custom()

                                self.overall_report.set_obj_html(
                                    _obj_title=f"{real_time_data}",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph_png = curr_thpt_obj.build_line_graph(
                                    data_set=data_set_in_graph,
                                    xaxis_name="Time",
                                    yaxis_name="Throughput (Mbps)",
                                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                                    label=label_data,
                                    graph_image_name=f"line_graph{i}"
                                )
                                logger.info("graph name {}".format(graph_png))
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()

                                self.overall_report.build_graph()
                                x_fig_size = 15
                                y_fig_size = len(devices_on_running) * .5 + 4
                                self.overall_report.set_obj_html(
                                    _obj_title="Per Client Avg-Throughput",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                                _xaxis_name="Avg Throughput(Mbps)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"image_name{i}_{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_obj_html(
                                    _obj_title="RSSI Of The Clients Connected",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                                _xaxis_name="Signal(-dBm)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"signal_image_name{i}_{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_obj_html(
                                    _obj_title="Detailed Result Table ",
                                    _obj="The below tables provides detailed information for the throughput test on each device.")
                                self.overall_report.build_objective()
                                curr_thpt_obj.mac_id_list = [item.split()[-1] if ' ' in item else item for item in curr_thpt_obj.mac_id_list]
                                if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                    test_input_list, pass_fail_list = curr_thpt_obj.get_pass_fail_list(
                                        device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                                bk_dataframe = {}

                                # Dataframe changes with respect to groups and profiles in case of interopability
                                if curr_thpt_obj.group_name:
                                    interop_tab_data = curr_thpt_obj.json_get('/adb/')["devices"]
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
                                    for key, value in curr_thpt_obj.group_device_map.items():
                                        if res_list[-1] in value:
                                            grp_name.append(key)
                                            break
                                    bk_dataframe["Group Name"] = grp_name[-1]

                                bk_dataframe[" Device Type "] = device_type[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Username"] = devices_on_running[-1]
                                bk_dataframe[" SSID "] = curr_thpt_obj.ssid_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" MAC "] = curr_thpt_obj.mac_id_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Channel "] = curr_thpt_obj.channel_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Mode"] = curr_thpt_obj.mode_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Offered download rate (Mbps)"] = download_list[-1]
                                bk_dataframe[" Observed Average download rate (Mbps)"] = [str(download_data[-1])]
                                bk_dataframe[" Offered upload rate (Mbps)"] = upload_list[-1]
                                bk_dataframe[" Observed Average upload rate (Mbps)"] = [str(upload_data[-1])]
                                bk_dataframe[" Average RTT (ms) "] = avg_rtt_data[-1]
                                bk_dataframe[" RSSI (dBm)"] = ['' if rssi_data[-1] == 0 else '-' + str(rssi_data[-1])]
                                if curr_thpt_obj.direction == "Bi-direction":
                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                elif curr_thpt_obj.direction == 'Download':
                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                    bk_dataframe[" Average Tx Drop % "] = [0.0] * len(download_drop)
                                else:
                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                    bk_dataframe[" Average Rx Drop % "] = [0.0] * len(upload_drop)
                                # When pass fail criteria is specified
                                if curr_thpt_obj.expected_passfail_value or curr_thpt_obj.device_csv_name:
                                    bk_dataframe[" Expected " + curr_thpt_obj.direction + " rate "] = test_input_list
                                    bk_dataframe[" Status "] = pass_fail_list
                                dataframe1 = pd.DataFrame(bk_dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                                self.overall_report.set_custom_html('<hr>')
                                self.overall_report.build_custom()

                            if (curr_thpt_obj.dowebgui and self.thput_obj_dict[ce][obj_name]
                                    ["obj"].get_live_view and curr_thpt_obj.do_interopability):
                                curr_thpt_obj.add_live_view_images_to_report(self.overall_report)
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"thput_test_{obj_no}"
                        else:
                            break

                elif test_name == "ping_test":
                    """Processes ping test reporting and visualizations."""
                    obj_no = 1
                    obj_name = 'ping_test'
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.ping_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        params = self.ping_obj_dict[ce][obj_name]["data"].copy()
                        result_json = params["result_json"]
                        report_path = params["report_path"]
                        config_devices = params["config_devices"]
                        group_device_map = params["group_device_map"]
                        curr_ping_obj = copy.copy(self.ping_obj_dict[ce][obj_name]["obj"])
                        if result_json is not None:
                            curr_ping_obj.result_json = result_json
                        self.overall_report.set_obj_html(_obj_title=f'PING Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        # Test setup information table for devices in device list
                        if config_devices == '':
                            test_setup_info = {
                                'SSID': curr_ping_obj.ssid,
                                'Security': curr_ping_obj.security,
                                'Website / IP': curr_ping_obj.target,
                                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(curr_ping_obj.sta_list), len(curr_ping_obj.sta_list) - len(curr_ping_obj.real_sta_list), curr_ping_obj.android, curr_ping_obj.windows, curr_ping_obj.linux, curr_ping_obj.mac),  # noqa E501
                                'Duration (in minutes)': curr_ping_obj.duration
                            }
                        # Test setup information table for devices in groups
                        else:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_setup_info = {
                                'Configuration': configmap,
                                'Website / IP': curr_ping_obj.target,
                                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(curr_ping_obj.sta_list), len(curr_ping_obj.sta_list) - len(curr_ping_obj.real_sta_list), curr_ping_obj.android, curr_ping_obj.windows, curr_ping_obj.linux, curr_ping_obj.mac), # noqa E501
                                'Duration (in minutes)': curr_ping_obj.duration
                            }
                        if self.robot_test and not self.do_bandsteering:
                            coordinate_map = curr_ping_obj.generate_overall_data()
                            logging.info("coordinate_map: %s", coordinate_map)
                            for key, value in coordinate_map.items():
                                if curr_ping_obj.rotation_enabled:
                                    self.overall_report.set_table_title("Overall Packetssent vs Received vs dropped of all coordinates at angle {}".format(key))
                                else:
                                    self.overall_report.set_table_title("Overall Packetssent vs Received vs dropped of all coordinates")
                                self.overall_report.build_table_title()
                                x_fig_size = 19
                                y_fig_size = len(curr_ping_obj.device_names) * .5 + 4

                                overallgraph = lf_bar_graph(_data_set=value,
                                                            _yaxis_name='Packets Count',
                                                            _xaxis_name='Coordinates',
                                                            _label=[
                                                                'Packets Loss', 'Packets Received', 'Packets Sent'],
                                                            _graph_image_name=f'Packets sent vs received vs dropped {obj_no}',
                                                            # _xaxis_label=self.coordinates_completed,
                                                            _xaxis_categories=curr_ping_obj.coordinates_completed,
                                                            _xaxis_step=1,
                                                            _xticks_font=8,
                                                            _graph_title='OverallPackets sent vs received vs dropped',
                                                            _title_size=16,
                                                            _color=['lightgrey',
                                                                    'orange', 'steelblue'],
                                                            _color_edge=['black'],
                                                            _bar_width=0.15,
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _dpi=96,
                                                            _show_bar_value=False,
                                                            _enable_csv=False,
                                                            _color_name=['lightgrey', 'orange', 'steelblue']
                                                            )

                                overallgraph_png = overallgraph.build_bar_graph()
                                self.overall_report.set_graph_image(overallgraph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                            last_interation = False
                            for coord in curr_ping_obj.coordinates_completed:
                                for angle in curr_ping_obj.angle_list:
                                    if coord == len(curr_ping_obj.coordinates_completed) - \
                                            1 and curr_ping_obj.angle_list[angle] == curr_ping_obj.currentangle:
                                        last_interation = True

                                    if curr_ping_obj.rotation_enabled:
                                        self.overall_report.set_table_title("Coordinate {} : Angle {}".format(coord, angle))
                                        self.overall_report.build_table_title()
                                        self.result_json = curr_ping_obj.coordinate_json[coord][angle]
                                    else:
                                        self.overall_report.set_table_title("Coordinate {}".format(coord))
                                        self.overall_report.build_table_title()
                                        self.result_json = curr_ping_obj.coordinate_json[coord]

                                    # packets sent vs received vs dropped
                                    self.overall_report.set_table_title(
                                        'Packets sent vs packets received vs packets dropped')
                                    self.overall_report.build_table_title()
                                    # graph for the above
                                    self.packets_sent = []
                                    self.packets_received = []
                                    self.packets_dropped = []
                                    self.device_names = []
                                    self.device_modes = []
                                    self.device_channels = []
                                    self.device_min = []
                                    self.device_max = []
                                    self.device_avg = []
                                    self.device_mac = []
                                    self.device_names_with_errors = []
                                    self.devices_with_errors = []
                                    self.report_names = []
                                    self.remarks = []
                                    self.device_ssid = []
                                    # packet_count_data = {}
                                    os_type = []
                                    for device, device_data in self.result_json.items():
                                        if not isinstance(device_data, dict):
                                            continue
                                        logging.info('Device data: {} {}'.format(device, device_data))
                                        os_type.append(device_data['os'])
                                        self.packets_sent.append(int(device_data['sent']))
                                        self.packets_received.append(int(device_data['recv']))
                                        self.packets_dropped.append(int(device_data['dropped']))
                                        self.device_names.append(device_data['name'] + ' ' + device_data['os'])
                                        self.device_modes.append(device_data['mode'])
                                        self.device_channels.append(device_data['channel'])
                                        self.device_mac.append(device_data['mac'])
                                        self.device_ssid.append(device_data['ssid'])
                                        self.device_min.append(float(device_data['min_rtt'].replace(',', '')))
                                        self.device_max.append(float(device_data['max_rtt'].replace(',', '')))
                                        self.device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
                                        if (device_data['os'] == 'Virtual'):
                                            self.report_names.append('{} {}'.format(device, device_data['os'])[0:25])
                                        else:
                                            self.report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name']))
                                        if (device_data['remarks'] != []):
                                            self.device_names_with_errors.append(device_data['name'])
                                            self.devices_with_errors.append(device)
                                            self.remarks.append(','.join(device_data['remarks']))
                                        # logging.info(self.packets_sent,
                                        #       self.packets_received,
                                        #       self.packets_dropped)
                                        # logging.info(self.device_min,
                                        #       self.device_max,
                                        #       self.device_avg)

                                        # packet_count_data[device] = {
                                        #     'MAC': device_data['mac'],
                                        #     'Channel': device_data['channel'],
                                        #     'Mode': device_data['mode'],
                                        #     'Packets Sent': device_data['sent'],
                                        #     'Packets Received': device_data['recv'],
                                        #     'Packets Loss': device_data['dropped'],
                                        # }
                                    x_fig_size = 19
                                    y_fig_size = len(self.device_names) * .5 + 4
                                    graph = lf_bar_graph_horizontal(_data_set=[self.packets_dropped, self.packets_received, self.packets_sent],
                                                                    _xaxis_name='Packets Count',
                                                                    _yaxis_name='Wireless Clients',
                                                                    _label=[
                                                                        'Packets Loss', 'Packets Received', 'Packets Sent'],
                                                                    _graph_image_name='Packets sent vs received vs dropped',
                                                                    _yaxis_label=self.report_names,
                                                                    _yaxis_categories=self.report_names,
                                                                    _yaxis_step=1,
                                                                    _yticks_font=8,
                                                                    _graph_title='Packets sent vs received vs dropped',
                                                                    _title_size=16,
                                                                    _color=['lightgrey',
                                                                            'orange', 'steelblue'],
                                                                    _color_edge=['black'],
                                                                    _bar_height=0.15,
                                                                    _figsize=(x_fig_size, y_fig_size),
                                                                    _legend_loc="best",
                                                                    _legend_box=(1.0, 1.0),
                                                                    _dpi=96,
                                                                    _show_bar_value=False,
                                                                    _enable_csv=True,
                                                                    _color_name=['lightgrey', 'orange', 'steelblue'])
                                    if curr_ping_obj.rotation_enabled:
                                        graph.graph_image_name = 'Packets sent vs received vs dropped_{}_{}'.format(coord, angle)
                                    else:
                                        graph.graph_image_name = 'Packets sent vs received vs dropped_{}'.format(coord)

                                    graph_png = graph.build_bar_graph_horizontal()
                                    logging.info('graph name {}'.format(graph_png))
                                    self.overall_report.set_graph_image(graph_png)
                                    # need to move the graph image to the results directory
                                    self.overall_report.move_graph_image()
                                    self.overall_report.set_csv_filename(graph_png)
                                    self.overall_report.move_csv_file()
                                    self.overall_report.build_graph()

                                    if curr_ping_obj.real:
                                        dataframe1 = pd.DataFrame({
                                            'Wireless Client': self.device_names,
                                            'MAC': self.device_mac,
                                            'Channel': self.device_channels,
                                            'SSID ': self.device_ssid,
                                            'Mode': self.device_modes,
                                            'Packets Sent': self.packets_sent,
                                            'Packets Received': self.packets_received,
                                            'Packets Loss': self.packets_dropped,
                                        })
                                        self.overall_report.set_table_dataframe(dataframe1)
                                        self.overall_report.build_table()
                                        if curr_ping_obj.get_live_view:
                                            report_path = self.overall_report.get_path()
                                            curr_ping_obj.add_live_view_images_to_report(report=self.overall_report, report_path=report_path)
                                    else:
                                        dataframe1 = pd.DataFrame({
                                            'Wireless Client': self.device_names,
                                            'MAC': self.device_mac,
                                            'Channel': self.device_channels,
                                            'SSID ': self.device_ssid,
                                            'Mode': self.device_modes,
                                            'Packets Sent': self.packets_sent,
                                            'Packets Received': self.packets_received,
                                            'Packets Loss': self.packets_dropped,
                                        })
                                        self.overall_report.set_table_dataframe(dataframe1)
                                        self.overall_report.build_table()

                                    # packets latency graph
                                    self.overall_report.set_table_title('Ping Latency Graph')
                                    self.overall_report.build_table_title()

                                    graph = lf_bar_graph_horizontal(_data_set=[self.device_min, self.device_avg, self.device_max],
                                                                    _xaxis_name='Time (ms)',
                                                                    _yaxis_name='Wireless Clients',
                                                                    _label=[
                                                                        'Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                                                                    _graph_image_name='Ping Latency per client',
                                                                    _yaxis_label=self.report_names,
                                                                    _yaxis_categories=self.report_names,
                                                                    _yaxis_step=1,
                                                                    _yticks_font=8,
                                                                    _graph_title='Ping Latency per client',
                                                                    _title_size=16,
                                                                    _color=['lightgrey',
                                                                            'orange', 'steelblue'],
                                                                    _color_edge='black',
                                                                    _bar_height=0.15,
                                                                    _figsize=(x_fig_size, y_fig_size),
                                                                    _legend_loc="best",
                                                                    _legend_box=(1.0, 1.0),
                                                                    _dpi=96,
                                                                    _show_bar_value=False,
                                                                    _enable_csv=True,
                                                                    _color_name=['lightgrey', 'orange', 'steelblue'])

                                    if curr_ping_obj.rotation_enabled:
                                        graph.graph_image_name = 'Ping Latency per client_{}_{}'.format(coord, angle)
                                    else:
                                        graph.graph_image_name = 'Ping Latency per client_{}'.format(coord)

                                    graph_png = graph.build_bar_graph_horizontal()
                                    logging.info('graph name {}'.format(graph_png))
                                    self.overall_report.set_graph_image(graph_png)
                                    # need to move the graph image to the results directory
                                    self.overall_report.move_graph_image()
                                    self.overall_report.set_csv_filename(graph_png)
                                    self.overall_report.move_csv_file()
                                    self.overall_report.build_graph()

                                    dataframe2 = pd.DataFrame({
                                        'Wireless Client': self.device_names,
                                        'MAC': self.device_mac,
                                        'Channel': self.device_channels,
                                        'SSID ': self.device_ssid,
                                        'Mode': self.device_modes,
                                        'Min Latency (ms)': self.device_min,
                                        'Average Latency (ms)': self.device_avg,
                                        'Max Latency (ms)': self.device_max
                                    })
                                    self.overall_report.set_table_dataframe(dataframe2)
                                    self.overall_report.build_table()

                                    # check if there are remarks for any device. If there are remarks, build table else don't
                                    if (self.remarks != []):
                                        self.overall_report.set_table_title('Notes')
                                        self.overall_report.build_table_title()
                                        dataframe3 = pd.DataFrame({
                                            'Wireless Client': self.device_names_with_errors,
                                            'Port': self.devices_with_errors,
                                            'Remarks': self.remarks
                                        })
                                        self.overall_report.set_table_dataframe(dataframe3)
                                        self.overall_report.build_table()

                                if last_interation:
                                    break

                        else:
                            if self.robot_test:
                                test_setup_info["Robot IP"] = curr_ping_obj.robo_ip
                                test_setup_info["Coordinates"] = str(curr_ping_obj.coordinate_list)
                                if curr_ping_obj.do_bandsteering:
                                    del test_setup_info["Duration (in minutes)"]
                                    test_setup_info["Cycles"] = str(curr_ping_obj.cycles)
                                    test_setup_info["BSSIDs for Bandsteering"] = str(curr_ping_obj.bssids)
                                else:
                                    if curr_ping_obj.rotation_enabled:
                                        test_setup_info["Rotations"] = curr_ping_obj.rotation
                                    test_setup_info["Rotation Enabled"] = str(curr_ping_obj.rotation_enabled)
                            self.overall_report.test_setup_table(
                                test_setup_data=test_setup_info, value='Test Setup Information')

                            # packets sent vs received vs dropped
                            self.overall_report.set_table_title(
                                'Packets sent vs packets received vs packets dropped')
                            self.overall_report.build_table_title()
                            # graph for the above
                            curr_ping_obj.packets_sent = []
                            curr_ping_obj.packets_received = []
                            curr_ping_obj.packets_dropped = []
                            curr_ping_obj.device_names = []
                            curr_ping_obj.device_modes = []
                            curr_ping_obj.device_channels = []
                            curr_ping_obj.device_min = []
                            curr_ping_obj.device_max = []
                            curr_ping_obj.device_avg = []
                            curr_ping_obj.device_mac = []
                            curr_ping_obj.device_names_with_errors = []
                            curr_ping_obj.devices_with_errors = []
                            curr_ping_obj.report_names = []
                            curr_ping_obj.remarks = []
                            curr_ping_obj.device_ssid = []
                            # packet_count_data = {}
                            os_type = []
                            for device, device_data in curr_ping_obj.result_json.items():
                                logging.info('Device data: {} {}'.format(device, device_data))
                                os_type.append(device_data['os'])
                                curr_ping_obj.packets_sent.append(int(device_data['sent']))
                                curr_ping_obj.packets_received.append(int(device_data['recv']))
                                curr_ping_obj.packets_dropped.append(int(device_data['dropped']))
                                curr_ping_obj.device_names.append(device_data['name'] + ' ' + device_data['os'])
                                curr_ping_obj.device_modes.append(device_data['mode'])
                                curr_ping_obj.device_channels.append(device_data['channel'])
                                curr_ping_obj.device_mac.append(device_data['mac'])
                                curr_ping_obj.device_ssid.append(device_data['ssid'])
                                curr_ping_obj.device_min.append(float(device_data['min_rtt'].replace(',', '')))
                                curr_ping_obj.device_max.append(float(device_data['max_rtt'].replace(',', '')))
                                curr_ping_obj.device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
                                if (device_data['os'] == 'Virtual'):
                                    curr_ping_obj.report_names.append('{} {}'.format(device, device_data['os'])[0:25])
                                else:
                                    curr_ping_obj.report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name']))
                                if (device_data['remarks'] != []):
                                    curr_ping_obj.device_names_with_errors.append(device_data['name'])
                                    curr_ping_obj.devices_with_errors.append(device)
                                    curr_ping_obj.remarks.append(','.join(device_data['remarks']))
                            x_fig_size = 15
                            y_fig_size = len(curr_ping_obj.device_names) * .5 + 4
                            graph = lf_bar_graph_horizontal(_data_set=[curr_ping_obj.packets_dropped, curr_ping_obj.packets_received, curr_ping_obj.packets_sent],
                                                            _xaxis_name='Packets Count',
                                                            _yaxis_name='Wireless Clients',
                                                            _label=[
                                                                'Packets Loss', 'Packets Received', 'Packets Sent'],
                                                            _graph_image_name=f'Packets sent vs received vs dropped {obj_no}',
                                                            _yaxis_label=curr_ping_obj.report_names,
                                                            _yaxis_categories=curr_ping_obj.report_names,
                                                            _yaxis_step=1,
                                                            _yticks_font=8,
                                                            _graph_title='Packets sent vs received vs dropped',
                                                            _title_size=16,
                                                            _color=['lightgrey',
                                                                    'orange', 'steelblue'],
                                                            _color_edge=['black'],
                                                            _bar_height=0.15,
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _dpi=96,
                                                            _show_bar_value=False,
                                                            _enable_csv=True,
                                                            _color_name=['lightgrey', 'orange', 'steelblue'])

                            graph_png = graph.build_bar_graph_horizontal()
                            logging.info('graph name {}'.format(graph_png))
                            self.overall_report.set_graph_image(graph_png)
                            # need to move the graph image to the results directory
                            self.overall_report.move_graph_image()
                            self.overall_report.set_csv_filename(graph_png)
                            self.overall_report.move_csv_file()
                            self.overall_report.build_graph()
                            if curr_ping_obj.real:
                                # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
                                if curr_ping_obj.expected_passfail_val or curr_ping_obj.csv_name:
                                    curr_ping_obj.get_pass_fail_list(os_type)
                                # When groups are provided a seperate table will be generated for each group using generate_dataframe
                                if curr_ping_obj.group_name:
                                    for key, val in group_device_map.items():
                                        if curr_ping_obj.expected_passfail_val or curr_ping_obj.csv_name:
                                            dataframe = curr_ping_obj.generate_dataframe(
                                                val,
                                                curr_ping_obj.device_names,
                                                curr_ping_obj.device_mac,
                                                curr_ping_obj.device_channels,
                                                curr_ping_obj.device_ssid,
                                                curr_ping_obj.device_modes,
                                                curr_ping_obj.packets_sent,
                                                curr_ping_obj.packets_received,
                                                curr_ping_obj.packets_dropped,
                                                curr_ping_obj.percent_pac_loss,
                                                curr_ping_obj.test_input_list,
                                                curr_ping_obj.pass_fail_list)
                                        else:
                                            dataframe = curr_ping_obj.generate_dataframe(val, curr_ping_obj.device_names, curr_ping_obj.device_mac, curr_ping_obj.device_channels, curr_ping_obj.device_ssid,  # noqa E501
                                                                                         curr_ping_obj.device_modes, curr_ping_obj.packets_sent, curr_ping_obj.packets_received, curr_ping_obj.packets_dropped, [], [], [])  # noqa E501
                                        if dataframe:
                                            self.overall_report.set_obj_html("", "Group: {}".format(key))
                                            self.overall_report.build_objective()
                                            dataframe1 = pd.DataFrame(dataframe)
                                            self.overall_report.set_table_dataframe(dataframe1)
                                            self.overall_report.build_table()

                                else:
                                    dataframe1 = pd.DataFrame({
                                        'Wireless Client': curr_ping_obj.device_names,
                                        'MAC': curr_ping_obj.device_mac,
                                        'Channel': curr_ping_obj.device_channels,
                                        'SSID ': curr_ping_obj.device_ssid,
                                        'Mode': curr_ping_obj.device_modes,
                                        'Packets Sent': curr_ping_obj.packets_sent,
                                        'Packets Received': curr_ping_obj.packets_received,
                                        'Packets Loss': curr_ping_obj.packets_dropped,
                                    })
                                    if curr_ping_obj.expected_passfail_val or curr_ping_obj.csv_name:
                                        dataframe1[" Percentage of Packet loss %"] = curr_ping_obj.percent_pac_loss
                                        dataframe1['Expected Packet loss %'] = curr_ping_obj.test_input_list
                                        dataframe1['Status'] = curr_ping_obj.pass_fail_list
                                    self.overall_report.set_table_dataframe(dataframe1)
                                    self.overall_report.build_table()
                            else:
                                dataframe1 = pd.DataFrame({
                                    'Wireless Client': curr_ping_obj.device_names,
                                    'MAC': curr_ping_obj.device_mac,
                                    'Channel': curr_ping_obj.device_channels,
                                    'SSID ': curr_ping_obj.device_ssid,
                                    'Mode': curr_ping_obj.device_modes,
                                    'Packets Sent': curr_ping_obj.packets_sent,
                                    'Packets Received': curr_ping_obj.packets_received,
                                    'Packets Loss': curr_ping_obj.packets_dropped,
                                })
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                            # packets latency graph
                            self.overall_report.set_table_title('Ping Latency Graph')
                            self.overall_report.build_table_title()

                            graph = lf_bar_graph_horizontal(_data_set=[curr_ping_obj.device_min, curr_ping_obj.device_avg, curr_ping_obj.device_max],
                                                            _xaxis_name='Time (ms)',
                                                            _yaxis_name='Wireless Clients',
                                                            _label=[
                                                                'Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                                                            _graph_image_name=f'Ping Latency per client {obj_no}',
                                                            _yaxis_label=curr_ping_obj.report_names,
                                                            _yaxis_categories=curr_ping_obj.report_names,
                                                            _yaxis_step=1,
                                                            _yticks_font=8,
                                                            _graph_title='Ping Latency per client',
                                                            _title_size=16,
                                                            _color=['lightgrey',
                                                                    'orange', 'steelblue'],
                                                            _color_edge='black',
                                                            _bar_height=0.15,
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _dpi=96,
                                                            _show_bar_value=False,
                                                            _enable_csv=True,
                                                            _color_name=['lightgrey', 'orange', 'steelblue'])

                            graph_png = graph.build_bar_graph_horizontal()
                            logging.info('graph name {}'.format(graph_png))
                            self.overall_report.set_graph_image(graph_png)
                            # need to move the graph image to the results directory
                            self.overall_report.move_graph_image()
                            self.overall_report.set_csv_filename(graph_png)
                            self.overall_report.move_csv_file()
                            self.overall_report.build_graph()

                            dataframe2 = pd.DataFrame({
                                'Wireless Client': curr_ping_obj.device_names,
                                'MAC': curr_ping_obj.device_mac,
                                'Channel': curr_ping_obj.device_channels,
                                'SSID ': curr_ping_obj.device_ssid,
                                'Mode': curr_ping_obj.device_modes,
                                'Min Latency (ms)': curr_ping_obj.device_min,
                                'Average Latency (ms)': curr_ping_obj.device_avg,
                                'Max Latency (ms)': curr_ping_obj.device_max
                            })
                            self.overall_report.set_table_dataframe(dataframe2)
                            self.overall_report.build_table()
                            if self.do_bandsteering and self.robot_test:
                                curr_ping_obj.get_bandsteering_stats(report=self.overall_report)
                            # check if there are remarks for any device. If there are remarks, build table else don't
                            if (curr_ping_obj.remarks != []):
                                self.overall_report.set_table_title('Notes')
                                self.overall_report.build_table_title()
                                dataframe3 = pd.DataFrame({
                                    'Wireless Client': curr_ping_obj.device_names_with_errors,
                                    'Port': curr_ping_obj.devices_with_errors,
                                    'Remarks': curr_ping_obj.remarks
                                })
                                self.overall_report.set_table_dataframe(dataframe3)
                                self.overall_report.build_table()

                        # closing
                        # self.overall_report.build_custom()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"ping_test_{obj_no}"
                        else:
                            break

                elif test_name == "qos_test":
                    """Processes Quality of Service (QoS) test reporting and visualizations."""
                    obj_no = 1
                    obj_name = 'qos_test'
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.qos_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        curr_qos_obj = copy.copy(self.qos_obj_dict[ce][obj_name]["obj"])
                        if (self.robot_test):
                            load = ''
                            rate_down = str(str(int(curr_qos_obj.cx_profile.side_b_min_bps) / 1000000) + ' ' + 'Mbps')
                            rate_up = str(str(int(curr_qos_obj.cx_profile.side_a_min_bps) / 1000000) + ' ' + 'Mbps')
                            logging.debug("QOS Direction: %s", curr_qos_obj.direction)
                            if curr_qos_obj.direction == "download":
                                load = rate_down
                            elif curr_qos_obj.direction == "upload":
                                load = rate_up
                            else:
                                load = 'Upload' + ':' + rate_up + ',' + 'Download' + ':' + rate_down
                            config_devices = ""
                        if not self.robot_test:
                            params = self.qos_obj_dict[ce][obj_name]["data"]
                            data = params["data"].copy() if isinstance(params["data"], (list, dict, set)) else params["data"]
                            input_setup_info = params["input_setup_info"].copy() if isinstance(params["input_setup_info"], (list, dict, set)) else params["input_setup_info"]
                            connections_download_avg = params["connections_download_avg"].copy() if isinstance(
                                params["connections_download_avg"], (list, dict, set)) else params["connections_download_avg"]
                            connections_upload_avg = params["connections_upload_avg"].copy() if isinstance(params["connections_upload_avg"], (list, dict, set)) else params["connections_upload_avg"]
                            avg_drop_a = params["avg_drop_a"].copy() if isinstance(params["avg_drop_a"], (list, dict, set)) else params["avg_drop_a"]
                            avg_drop_b = params["avg_drop_b"].copy() if isinstance(params["avg_drop_b"], (list, dict, set)) else params["avg_drop_b"]
                            report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]
                            config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]
                            selected_real_clients_names = params["selected_real_clients_names"].copy() if isinstance(
                                params["selected_real_clients_names"], (list, dict, set)) else params["selected_real_clients_names"]
                            curr_qos_obj.ssid_list = curr_qos_obj.get_ssid_list(curr_qos_obj.input_devices_list)
                            if selected_real_clients_names is not None:
                                curr_qos_obj.num_stations = selected_real_clients_names
                            data_set, load, res = curr_qos_obj.generate_graph_data_set(data)
                        # Initialize counts and lists for device types
                        android_devices, windows_devices, linux_devices, ios_devices, ios_mob_devices = 0, 0, 0, 0, 0
                        all_devices_names = []
                        device_type = []
                        total_devices = ""
                        for i in curr_qos_obj.real_client_list:
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

                        # Test setup information table for devices in device list
                        if config_devices == "":
                            test_setup_info = {
                                "Device List": ", ".join(all_devices_names),
                                "Number of Stations": "Total" + f"({self.qos_obj_dict[ce][obj_name]['obj'].num_stations})" + total_devices,
                                "AP Model": curr_qos_obj.ap_name,
                                "SSID": curr_qos_obj.ssid,
                                "Traffic Duration in hours": round(int(curr_qos_obj.test_duration) / 3600, 2),
                                "Security": curr_qos_obj.security,
                                "Protocol": (curr_qos_obj.traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": curr_qos_obj.direction,
                                "TOS": curr_qos_obj.tos,
                                "Per TOS Load in Mbps": load
                            }
                        # Test setup information table for devices in groups
                        else:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_setup_info = {
                                "AP Model": curr_qos_obj.ap_name,
                                'Configuration': configmap,
                                "Traffic Duration in hours": round(int(curr_qos_obj.test_duration) / 3600, 2),
                                "Security": curr_qos_obj.security,
                                "Protocol": (curr_qos_obj.traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": curr_qos_obj.direction,
                                "TOS": curr_qos_obj.tos,
                                "Per TOS Load in Mbps": load
                            }
                        if self.robot_test:
                            test_setup_info["Robot IP"] = self.robot_ip
                            test_setup_info["Selected Coordinated"] = self.coordinate_list
                            if self.rotation_enabled:
                                test_setup_info["Rotation Enabled"] = self.rotation_list
                            if self.do_bandsteering:
                                del test_setup_info["Traffic Duration in hours"]
                                test_setup_info["no of cycles"] = self.cycles
                        self.overall_report.set_obj_html(_obj_title=f'QOS Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

                        if self.robot_test and not self.do_bandsteering:
                            if self.dowebgui:
                                tos_for_report = curr_qos_obj.tos
                                tos_images, rssi_images = curr_qos_obj.get_live_view_images()
                                for tos_val in tos_for_report:
                                    for image_path in tos_images[tos_val]:
                                        self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html(f'<img src="file://{image_path}" style="width: 1200px; height: 800px;"></img>')
                                        self.overall_report.build_custom()
                                for _floor, rssi_image_path in rssi_images.items():
                                    if os.path.exists(rssi_image_path):
                                        self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                        self.overall_report.build_custom()
                                        self.overall_report.set_custom_html(f'<img src="file://{rssi_image_path}" style="width: 1000px; height: 800px;"></img>')
                                        self.overall_report.build_custom()
                            for coordinate in range(len(curr_qos_obj.coordinate_list)):
                                if curr_qos_obj.rotation_enabled:
                                    for angle in range(len(curr_qos_obj.rotation_list)):
                                        self.overall_report.set_obj_html(
                                            _obj_title=(
                                                f"Coordinate: "
                                                f"{self.qos_obj_dict[ce][obj_name]['obj'].coordinate_list[coordinate]} | "
                                                f"Rotation Angle: "
                                                f"{self.qos_obj_dict[ce][obj_name]['obj'].rotation_list[angle]}°"
                                            ),
                                            _obj=""
                                        )
                                        self.overall_report.build_objective()
                                        data = curr_qos_obj.qos_data[self.qos_obj_dict[ce][obj_name]
                                                                     ["obj"].coordinate_list[coordinate]][curr_qos_obj.rotation_list[angle]]["data"]
                                        connections_download_avg = curr_qos_obj.qos_data[self.qos_obj_dict[ce][obj_name]
                                                                                         ["obj"].coordinate_list[coordinate]][curr_qos_obj.rotation_list[angle]]["connections_download_avg"]
                                        connections_upload_avg = curr_qos_obj.qos_data[self.qos_obj_dict[ce][obj_name]
                                                                                       ["obj"].coordinate_list[coordinate]][curr_qos_obj.rotation_list[angle]]["connections_upload_avg"]
                                        avg_drop_a = curr_qos_obj.qos_data[self.qos_obj_dict[ce][obj_name]
                                                                           ["obj"].coordinate_list[coordinate]][curr_qos_obj.rotation_list[angle]]["avg_drop_a"]
                                        avg_drop_b = curr_qos_obj.qos_data[self.qos_obj_dict[ce][obj_name]
                                                                           ["obj"].coordinate_list[coordinate]][curr_qos_obj.rotation_list[angle]]["avg_drop_b"]
                                        curr_qos_obj.generate_individual_coordinate(
                                            self.overall_report, data, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b, coordinate, angle)
                                else:
                                    self.overall_report.set_obj_html(_obj_title=f"Coordinate: {self.qos_obj_dict[ce][obj_name]['obj'].coordinate_list[coordinate]}",
                                                                     _obj="")
                                    self.overall_report.build_objective()
                                    data = curr_qos_obj.qos_data[curr_qos_obj.coordinate_list[coordinate]]["data"]
                                    connections_download_avg = curr_qos_obj.qos_data[self.qos_obj_dict[ce]
                                                                                     [obj_name]["obj"].coordinate_list[coordinate]]["connections_download_avg"]
                                    connections_upload_avg = curr_qos_obj.qos_data[self.qos_obj_dict[ce]
                                                                                   [obj_name]["obj"].coordinate_list[coordinate]]["connections_upload_avg"]
                                    avg_drop_a = curr_qos_obj.qos_data[curr_qos_obj.coordinate_list[coordinate]]["avg_drop_a"]
                                    avg_drop_b = curr_qos_obj.qos_data[curr_qos_obj.coordinate_list[coordinate]]["avg_drop_b"]
                                    curr_qos_obj.generate_individual_coordinate(
                                        self.overall_report, data, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b, coordinate, None)

                        else:
                            self.overall_report.set_table_title(
                                f"Overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
                            self.overall_report.build_table_title()
                            if self.do_bandsteering:
                                upload = []
                                download = []
                                drop_a = []
                                drop_b = []
                                avg_upload = []
                                avg_download = []
                                avg_drop_a = []
                                avg_drop_b = []
                                for _ in range(len(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx)):
                                    upload.append([])
                                    download.append([])
                                    drop_a.append([])
                                    drop_b.append([])
                                    avg_upload.append([])
                                    avg_download.append([])
                                    avg_drop_a.append([])
                                    avg_drop_b.append([])
                                dropa_connections = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                dropb_connections = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                connections_upload = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                connections_download = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                connections_upload_avg = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                connections_download_avg = dict.fromkeys(list(self.qos_obj_dict[ce][obj_name]['obj'].cx_profile.created_cx.keys()), float(0))
                                # # rx_rate list is calculated
                                for thpt in self.qos_obj_dict[ce][obj_name]['obj'].throughput_data:
                                    for ind, _k in enumerate(thpt):
                                        avg_upload[ind].append(thpt[ind][1])
                                        avg_download[ind].append(thpt[ind][0])
                                        avg_drop_a[ind].append(thpt[ind][2])
                                        avg_drop_b[ind].append(thpt[ind][3])
                                        upload[ind].append(thpt[ind][1])
                                        download[ind].append(thpt[ind][0])
                                        drop_a[ind].append(thpt[ind][2])
                                        drop_b[ind].append(thpt[ind][3])

                                # Rounding of the results upto 2 decimals
                                upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in upload]
                                download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in download]
                                drop_a_per = [float(round(sum(i) / len(i), 2)) for i in drop_a]
                                drop_b_per = [float(round(sum(i) / len(i), 2)) for i in drop_b]
                                avg_upload_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in avg_upload]
                                avg_download_throughput = [float(f"{(sum(i) / 1000000) / len(i): .2f}") for i in avg_download]
                                avg_drop_a_per = [float(round(sum(i) / len(i), 2)) for i in avg_drop_a]
                                avg_drop_b_per = [float(round(sum(i) / len(i), 2)) for i in avg_drop_b]
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
                                test_results = {'test_results': []}
                                data = {}
                                test_results['test_results'].append(self.qos_obj_dict[ce][obj_name]['obj'].evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                                data.update(test_results)
                                avg_drop_a = dropa_connections
                                avg_drop_b = dropb_connections
                                input_setup_info = {
                                    "contact": "support@candelatech.com"
                                }
                                data_set, load, res = curr_qos_obj.generate_graph_data_set(data)

                            df_throughput = pd.DataFrame(res["throughput_table_df"])
                            self.overall_report.set_table_dataframe(df_throughput)
                            self.overall_report.build_table()
                            for _key in res["graph_df"]:
                                self.overall_report.set_obj_html(
                                    _obj_title=(
                                        f"Overall "
                                        f"{self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput for "
                                        f"{len(self.qos_obj_dict[ce][obj_name]['obj'].input_devices_list)} "
                                        f"clients with different TOS."
                                    ),
                                    _obj=(
                                        f"The below graph represents overall "
                                        f"{self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput for all "
                                        "connected stations running BK, BE, VO, VI traffic with different "
                                        f"intended loads {load} per TOS"
                                    )
                                )
                            self.overall_report.build_objective()
                            graph = lf_bar_graph(_data_set=data_set,
                                                 _xaxis_name="Load per Type of Service",
                                                 _yaxis_name="Throughput (Mbps)",
                                                 _xaxis_categories=["BK,BE,VI,VO"],
                                                 _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                                 _graph_image_name=f"tos_download_{_key}Hz {obj_no}",
                                                 _label=["BK", "BE", "VI", "VO"],
                                                 _xaxis_step=1,
                                                 _graph_title=f"Overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput – BK,BE,VO,VI traffic streams",
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
                            logging.info("graph name %s", graph_png)
                            self.overall_report.set_graph_image(graph_png)
                            # need to move the graph image to the results directory
                            self.overall_report.move_graph_image()
                            self.overall_report.set_csv_filename(graph_png)
                            self.overall_report.move_csv_file()
                            self.overall_report.build_graph()
                            if self.do_bandsteering:
                                self.qos_obj_dict[ce][obj_name]['obj'].get_bandsteering_stats(report=self.overall_report, data=self.qos_obj_dict[ce][obj_name]['obj'].band_steering_df)
                            curr_qos_obj.generate_individual_graph(res, self.overall_report, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b, obj_no)
                            self.overall_report.test_setup_table(test_setup_data=input_setup_info, value="Information")
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"qos_test_{obj_no}"
                        else:
                            break

                elif test_name == "mcast_test":
                    """Processes multicast test reporting and visualizations."""
                    obj_no = 1
                    obj_name = "mcast_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.mcast_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        logging.debug("mcast_obj_dict: %s", self.mcast_obj_dict)
                        params = self.mcast_obj_dict[ce][obj_name]["data"].copy()
                        config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]
                        group_device_map = params["group_device_map"].copy() if isinstance(params["group_device_map"], (list, dict, set)) else params["group_device_map"]
                        curr_mcast_obj = copy.copy(self.mcast_obj_dict[ce][obj_name]["obj"])
                        test_setup_info = {
                            "DUT Name": curr_mcast_obj.dut_model_num,
                            "DUT Hardware Version": curr_mcast_obj.dut_hw_version,
                            "DUT Software Version": curr_mcast_obj.dut_sw_version,
                            "DUT Serial Number": curr_mcast_obj.dut_serial_num,
                        }
                        self.overall_report.set_obj_html(_obj_title=f'MULTICAST Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        # For real devices when groups specified for configuration
                        if curr_mcast_obj.real and curr_mcast_obj.group_name:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_input_info = {
                                "LANforge ip": curr_mcast_obj.lfmgr,
                                "LANforge port": curr_mcast_obj.lfmgr_port,
                                "Upstream": curr_mcast_obj.upstream_port,
                                "Test Duration": curr_mcast_obj.test_duration,
                                "Test Configuration": configmap,
                                "Polling Interval": curr_mcast_obj.polling_interval,
                                "Total No. of Devices": curr_mcast_obj.station_count,
                            }
                        else:
                            test_input_info = {
                                "LANforge ip": curr_mcast_obj.lfmgr,
                                "LANforge port": curr_mcast_obj.lfmgr_port,
                                "Upstream": curr_mcast_obj.upstream_port,
                                "Test Duration": curr_mcast_obj.test_duration,
                                "Polling Interval": curr_mcast_obj.polling_interval,
                                "Total No. of Devices": curr_mcast_obj.station_count,
                            }

                        self.overall_report.set_table_title("Test Configuration")
                        self.overall_report.build_table_title()
                        self.overall_report.test_setup_table(value="Test Configuration",
                                                             test_setup_data=test_input_info)

                        self.overall_report.set_table_title("Radio Configuration")
                        self.overall_report.build_table_title()

                        wifi_mode_dict = {
                            0: 'AUTO',  # 802.11g
                            1: '802.11a',  # 802.11a
                            2: '802.11b',  # 802.11b
                            3: '802.11g',  # 802.11g
                            4: '802.11abg',  # 802.11abg
                            5: '802.11abgn',  # 802.11abgn
                            6: '802.11bgn',  # 802.11bgn
                            7: '802.11bg',  # 802.11bg
                            8: '802.11abgnAC',  # 802.11abgn-AC
                            9: '802.11anAC',  # 802.11an-AC
                            10: '802.11an',  # 802.11an
                            11: '802.11bgnAC',  # 802.11bgn-AC
                            12: '802.11abgnAX',  # 802.11abgn-A+
                            #     a/b/g/n/AC/AX (dual-band AX) support
                            13: '802.11bgnAX',  # 802.11bgn-AX
                            14: '802.11anAX',  # 802.11an-AX
                            15: '802.11aAX',  # 802.11a-AX (6E disables /n and /ac)
                            16: '802.11abgnEHT',  # 802.11abgn-EHT  a/b/g/n/AC/AX/EHT (dual-band AX) support
                            17: '802.11bgnEHT',  # 802.11bgn-EHT
                            18: '802.11anEHT',  # 802.11an-ETH
                            19: '802.11aBE',  # 802.11a-EHT (6E disables /n and /ac)
                        }

                        for (
                                radio_,
                                ssid_,
                                _ssid_password_,  # do not print password
                                ssid_security_,
                                mode_,
                                wifi_enable_flags_list_,
                                _reset_port_enable_,
                                _reset_port_time_min_,
                                _reset_port_time_max_) in zip(
                                curr_mcast_obj.radio_name_list,
                                curr_mcast_obj.ssid_list,
                                curr_mcast_obj.ssid_password_list,
                                curr_mcast_obj.ssid_security_list,
                                curr_mcast_obj.wifi_mode_list,
                                curr_mcast_obj.enable_flags_list,
                                curr_mcast_obj.reset_port_enable_list,
                                curr_mcast_obj.reset_port_time_min_list,
                                curr_mcast_obj.reset_port_time_max_list):

                            mode_value = wifi_mode_dict[int(mode_)]

                            radio_info = {
                                "SSID": ssid_,
                                "Security": ssid_security_,
                                "Wifi mode set": mode_value,
                                'Wifi Enable Flags': wifi_enable_flags_list_
                            }
                            self.overall_report.test_setup_table(value=radio_, test_setup_data=radio_info)

                        # TODO move the graphing to the class so it may be called as a service

                        # Graph TOS data
                        # Once the data is stopped can collect the data for the cx's both multi cast and uni cast
                        # if the traffic is still running will gather the running traffic
                        # curr_mcast_obj.evaluate_qos()

                        # graph BK A
                        # try to do as a loop
                        tos_list = ['BK', 'BE', 'VI', 'VO']
                        if curr_mcast_obj.real:
                            tos_types = ['BE', 'BK', 'VI', 'VO']
                            logging.debug("client_dict_B is client_dict_A: %s", curr_mcast_obj.client_dict_B is curr_mcast_obj.client_dict_A)
                            for tos_key in tos_types:
                                if tos_key in curr_mcast_obj.client_dict_A:
                                    tos_data = curr_mcast_obj.client_dict_A[tos_key]

                                    # Filter A side
                                    traffic_proto_A = tos_data.get("traffic_protocol_A", [])
                                    indices_to_keep_A = [i for i, proto in enumerate(traffic_proto_A) if proto == "Mcast"]

                                    # Filter B side
                                    traffic_proto_B = tos_data.get("traffic_protocol_B", [])
                                    indices_to_keep_B = [i for i, proto in enumerate(traffic_proto_B) if proto == "Mcast"]

                                    for key in list(tos_data.keys()):
                                        if key in ["colors", "labels"]:
                                            continue  # Keep as-is

                                        if key.endswith('_A'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_A if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list

                                        elif key.endswith('_B'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_B if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list
                            for tos_key in tos_types:
                                if tos_key in curr_mcast_obj.client_dict_B:
                                    tos_data = curr_mcast_obj.client_dict_B[tos_key]

                                    # Filter A side
                                    traffic_proto_A = tos_data.get("traffic_protocol_A", [])
                                    indices_to_keep_A = [i for i, proto in enumerate(traffic_proto_A) if proto == "Mcast"]

                                    # Filter B side
                                    traffic_proto_B = tos_data.get("traffic_protocol_B", [])
                                    indices_to_keep_B = [i for i, proto in enumerate(traffic_proto_B) if proto == "Mcast"]

                                    for key in list(tos_data.keys()):
                                        if key in ["colors", "labels"]:
                                            continue  # Keep as-is

                                        if key.endswith('_A'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_A if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list

                                        elif key.endswith('_B'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_B if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list

                        if self.robot_test and not self.do_bandsteering:
                            logger.info("Building per-coordinate/rotation graphs and tables for robot test (from memory dict)")
                            if curr_mcast_obj.dowebgui:
                                curr_mcast_obj.add_live_view_images_to_report()
                            if not hasattr(curr_mcast_obj, "multicast_robot_results") or not curr_mcast_obj.multicast_robot_results:
                                self.overall_report.set_custom_html("<p><i>No robot test results found.</i></p>")
                                self.overall_report.build_custom()
                            else:
                                # Iterate through each coordinate/rotation result
                                for _, result in curr_mcast_obj.multicast_robot_results.items():
                                    coord = result.get("coordinate", "NA")
                                    rot = result.get("rotation", "NA")
                                    stations = result.get("stations", [])
                                    upstream = result.get("upstream", {})
                                    summary = result.get("summary", {})

                                    # Section header
                                    if rot is not None:
                                        self.overall_report.set_custom_html(
                                            f"<h2 style='margin-top:25px;color:darkgreen;'>Coordinate: {coord} | Rotation: {rot}°</h2>"
                                        )
                                    else:
                                        self.overall_report.set_custom_html(
                                            f"<h2 style='margin-top:25px;color:darkgreen;'>Coordinate: {coord}</h2>"
                                        )
                                    self.overall_report.build_custom()

                                    if upstream:
                                        tx_rate = upstream.get("tx_rate_bps", 0)
                                        dataset_list = [[tx_rate]]
                                        labels = ["TX (bps)"]
                                        yaxis_categories = [upstream.get("endpoint", "eth-unknown")]

                                        graph = lf_bar_graph_horizontal(
                                            _data_set=dataset_list,
                                            _xaxis_name="TX Throughput (bps)",
                                            _yaxis_name="Upstream Endpoint",
                                            _yaxis_categories=yaxis_categories,
                                            _graph_image_name=f"robot_coord_{coord}_rot_{rot}_upstream_tx",
                                            _label=labels,
                                            _color_name=["darkorange"],
                                            _color_edge=["black"],
                                            _graph_title=f"Upstream TX Throughput — Coord {coord}, Rot {rot}",
                                            _title_size=10,
                                            _figsize=(14, 4.5),
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _text_font=6,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0)
                                        )
                                        graph_png = graph.build_bar_graph_horizontal()
                                        self.overall_report.set_graph_image(graph_png)
                                        self.overall_report.move_graph_image()
                                        self.overall_report.build_graph()
                                        self.overall_report.set_csv_filename(graph_png)
                                        self.overall_report.move_csv_file()

                                        df_up = pd.DataFrame([upstream])
                                        self.overall_report.set_table_title("Upstream (Ethernet TX) Data")
                                        self.overall_report.build_table_title()
                                        self.overall_report.set_table_dataframe(df_up)
                                        self.overall_report.build_table()

                                    if stations:
                                        df_stations = pd.DataFrame(stations)

                                        dataset_list = [df_stations["rx_rate_bps"].tolist()]
                                        labels = ["RX (bps)"]
                                        yaxis_categories = df_stations["station"].tolist()

                                        graph = lf_bar_graph_horizontal(
                                            _data_set=dataset_list,
                                            _xaxis_name="RX Throughput (bps)",
                                            _yaxis_name="Stations",
                                            _yaxis_categories=yaxis_categories,
                                            _graph_image_name=f"robot_coord_{coord}_rot_{rot}_station_rx",
                                            _label=labels,
                                            _color_name=["teal"],
                                            _color_edge=["black"],
                                            _graph_title=f"Receiver Station RX Throughput — Coord {coord}, Rot {rot}",
                                            _title_size=10,
                                            _figsize=(16, max(4.5, len(yaxis_categories) * 0.5)),
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _text_font=6,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0)
                                        )
                                        graph_png = graph.build_bar_graph_horizontal()
                                        self.overall_report.set_graph_image(graph_png)
                                        self.overall_report.move_graph_image()
                                        self.overall_report.build_graph()
                                        self.overall_report.set_csv_filename(graph_png)
                                        self.overall_report.move_csv_file()

                                        avg_rx = df_stations["rx_rate_bps"].mean()
                                        avg_drop = df_stations["drop_percent"].mean()
                                        self.overall_report.set_custom_html(
                                            f"<p style='font-size:12px;'>Average RX Throughput: <b>{avg_rx / 1e6:.2f} Mbps</b><br>"
                                            f"Average Drop Rate: <b>{avg_drop:.2f}%</b><br>"
                                            f"Total Stations: <b>{len(df_stations)}</b></p>"
                                        )
                                        self.overall_report.build_custom()

                                        self.overall_report.set_table_title("Receiver Station Data")
                                        self.overall_report.build_table_title()
                                        self.overall_report.set_table_dataframe(df_stations)
                                        self.overall_report.build_table()

                                    if summary:
                                        df_summary = pd.DataFrame([summary])
                                        self.overall_report.set_table_title("Coordinate Summary")
                                        self.overall_report.build_table_title()
                                        self.overall_report.set_table_dataframe(df_summary)
                                        self.overall_report.build_table()

                                    self.overall_report.set_custom_html("<hr style='border:none;border-top:1px solid #ccc;margin:20px 0;'>")
                                    self.overall_report.build_custom()

                                all_summary = []
                                for _pos_key, res in curr_mcast_obj.multicast_robot_results.items():
                                    sm = res.get("summary")
                                    if sm:
                                        all_summary.append(sm)
                                # Generate aggregated rotation summary across all coordinates
                                if all_summary:
                                    df_all = pd.DataFrame(all_summary)
                                    try:
                                        rot_summary = (
                                            df_all.groupby("rotation")[["total_rx_rate_bps", "total_tx_rate_bps"]]
                                            .mean()
                                            .reset_index()
                                            .sort_values(by="rotation")
                                        )
                                        dataset = [
                                            rot_summary["total_rx_rate_bps"].tolist(),
                                            rot_summary["total_tx_rate_bps"].tolist()
                                        ]
                                        labels = ["Avg RX (bps)", "Avg TX (bps)"]
                                        rotations = rot_summary["rotation"].astype(str).tolist()

                                        graph = lf_bar_graph_horizontal(
                                            _data_set=dataset,
                                            _xaxis_name="Average Throughput (bps)",
                                            _yaxis_name="Rotation (°)",
                                            _yaxis_categories=rotations,
                                            _graph_image_name="robot_avg_rotation_summary",
                                            _label=labels,
                                            _color_name=["steelblue", "orange"],
                                            _color_edge=["black"],
                                            _graph_title="Average RX/TX Throughput vs Rotation",
                                            _title_size=10,
                                            _figsize=(15, max(4, len(rotations) * 0.5)),
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _text_font=6,
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0)
                                        )
                                        graph_png = graph.build_bar_graph_horizontal()
                                        self.overall_report.set_graph_image(graph_png)
                                        self.overall_report.move_graph_image()
                                        self.overall_report.build_graph()
                                        self.overall_report.set_csv_filename(graph_png)
                                        self.overall_report.move_csv_file()

                                        self.overall_report.set_custom_html(
                                            "<p style='font-size:12px;'>The above chart shows average RX/TX throughput aggregated "
                                            "by rotation across all coordinates.</p>"
                                        )
                                        self.overall_report.build_custom()
                                    except Exception as e:
                                        logger.warning(f"Could not aggregate rotation summary: {e}")

                        else:
                            for tos in tos_list:
                                logging.debug("TOS: %s", curr_mcast_obj.tos)
                                if tos not in curr_mcast_obj.tos:
                                    continue
                                if (curr_mcast_obj.client_dict_A[tos]["ul_A"] and curr_mcast_obj.client_dict_A[tos]["dl_A"]):
                                    min_bps_a = curr_mcast_obj.client_dict_A["min_bps_a"]
                                    min_bps_b = curr_mcast_obj.client_dict_A["min_bps_b"]

                                    dataset_list = [curr_mcast_obj.client_dict_A[tos]["ul_A"], curr_mcast_obj.client_dict_A[tos]["dl_A"]]
                                    # TODO possibly explain the wording for upload and download
                                    dataset_length = len(curr_mcast_obj.client_dict_A[tos]["ul_A"])
                                    x_fig_size = 20
                                    y_fig_size = len(curr_mcast_obj.client_dict_A[tos]["clients_A"]) * .4 + 5
                                    logger.debug("length of clients_A {clients} resource_alias_A {alias_A}".format(
                                        clients=len(curr_mcast_obj.client_dict_A[tos]["clients_A"]), alias_A=len(curr_mcast_obj.client_dict_A[tos]["resource_alias_A"])))
                                    logger.debug("clients_A {clients}".format(clients=curr_mcast_obj.client_dict_A[tos]["clients_A"]))
                                    logger.debug("resource_alias_A {alias_A}".format(alias_A=curr_mcast_obj.client_dict_A[tos]["resource_alias_A"]))

                                    if int(min_bps_a) != 0:
                                        self.overall_report.set_obj_html(
                                            _obj_title=(
                                                f"Individual throughput measured upload tcp or udp bps: {min_bps_a}, "
                                                f"download tcp, udp, or mcast bps: {min_bps_b} "
                                                f"station for traffic {tos} (WiFi)."
                                            ),
                                            _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                            f"Throughput in Mbps”.")
                                    else:
                                        self.overall_report.set_obj_html(
                                            _obj_title=f"Individual throughput mcast download bps: {min_bps_b} traffic {tos} (WiFi).",
                                            _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                            f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                            f"Throughput in Mbps”.")

                                    self.overall_report.build_objective()

                                    graph = lf_bar_graph_horizontal(_data_set=dataset_list,
                                                                    _xaxis_name="Throughput in bps",
                                                                    _yaxis_name="Client names",
                                                                    # _yaxis_categories=curr_mcast_obj.client_dict_A[tos]["clients_A"],
                                                                    _yaxis_categories=curr_mcast_obj.client_dict_A[tos]["resource_alias_A"],
                                                                    _graph_image_name=f"{tos}_A{obj_no}",
                                                                    _label=curr_mcast_obj.client_dict_A[tos]['labels'],
                                                                    _color_name=curr_mcast_obj.client_dict_A[tos]['colors'],
                                                                    _color_edge=['black'],
                                                                    # traditional station side -A
                                                                    _graph_title=f"Individual {tos} client side traffic measurement - side a (downstream)",
                                                                    _title_size=10,
                                                                    _figsize=(x_fig_size, y_fig_size),
                                                                    _show_bar_value=True,
                                                                    _enable_csv=True,
                                                                    _text_font=8,
                                                                    _legend_loc="best",
                                                                    _legend_box=(1.0, 1.0)
                                                                    )
                                    graph_png = graph.build_bar_graph_horizontal()
                                    self.overall_report.set_graph_image(graph_png)
                                    self.overall_report.move_graph_image()
                                    self.overall_report.build_graph()
                                    self.overall_report.set_csv_filename(graph_png)
                                    self.overall_report.move_csv_file()
                                    if (curr_mcast_obj.dowebgui and curr_mcast_obj.get_live_view):
                                        for floor in range(0, int(curr_mcast_obj.total_floors)):
                                            script_dir = os.path.dirname(os.path.abspath(__file__))
                                            throughput_image_path = os.path.join(script_dir, "heatmap_images", f"{self.mcast_obj_dict[ce][obj_name]['obj'].test_name}_throughput_{floor + 1}.png")
                                            rssi_image_path = os.path.join(script_dir, "heatmap_images", f"{self.mcast_obj_dict[ce][obj_name]['obj'].test_name}_rssi_{floor + 1}.png")
                                            timeout = 60  # seconds
                                            start_time = time.time()

                                            while not (os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path)):
                                                if time.time() - start_time > timeout:
                                                    logging.warning("Timeout: Images not found within 60 seconds.")
                                                    break
                                                time.sleep(1)
                                            while not os.path.exists(throughput_image_path) and not os.path.exists(rssi_image_path):
                                                if os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path):
                                                    break
                                            if os.path.exists(throughput_image_path):
                                                self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                                self.overall_report.build_custom()
                                                self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
                                                self.overall_report.build_custom()

                                            if os.path.exists(rssi_image_path):
                                                self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                                self.overall_report.build_custom()
                                                self.overall_report.set_custom_html(f'<img src="file://{rssi_image_path}"></img>')
                                                self.overall_report.build_custom()

                                    # For real devices appending the required data for pass fail criteria
                                    if curr_mcast_obj.real:
                                        up, down, off_up, off_down = [], [], [], []
                                        for i in curr_mcast_obj.client_dict_A[tos]['ul_A']:
                                            up.append(int(i) / 1000000)
                                        for i in curr_mcast_obj.client_dict_A[tos]['dl_A']:
                                            down.append(int(i) / 1000000)
                                        for i in curr_mcast_obj.client_dict_A[tos]['offered_upload_rate_A']:
                                            off_up.append(int(i) / 1_000_000)
                                        for i in curr_mcast_obj.client_dict_A[tos]['offered_download_rate_A']:
                                            off_down.append(int(i) / 1000000)
                                        # if either 'expected_passfail_value' or 'device_csv_name' is provided for pass/fail evaluation
                                        if curr_mcast_obj.expected_passfail_value or curr_mcast_obj.device_csv_name:
                                            test_input_list, pass_fail_list = curr_mcast_obj.get_pass_fail_list(tos, up, down)

                                    if curr_mcast_obj.real:
                                        # When groups and profiles specifed for configuration
                                        if curr_mcast_obj.group_name:
                                            for key, val in group_device_map.items():
                                                # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                                                if curr_mcast_obj.expected_passfail_value or curr_mcast_obj.device_csv_name:
                                                    dataframe = curr_mcast_obj.generate_dataframe(
                                                        val,
                                                        curr_mcast_obj.client_dict_A[tos]['resource_alias_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_eid_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_host_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_hw_ver_A'],
                                                        curr_mcast_obj.client_dict_A[tos]["clients_A"],
                                                        curr_mcast_obj.client_dict_A[tos]['port_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['mode_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['mac_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['ssid_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['channel_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['traffic_type_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['traffic_protocol_A'],
                                                        off_up,
                                                        off_down,
                                                        up,
                                                        down,
                                                        test_input_list,
                                                        curr_mcast_obj.client_dict_A[tos]['download_rx_drop_percent_A'],
                                                        pass_fail_list)
                                                # Generating Dataframe for groups when pass_fail case is not specified
                                                else:
                                                    dataframe = curr_mcast_obj.generate_dataframe(
                                                        val,
                                                        curr_mcast_obj.client_dict_A[tos]['resource_alias_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_eid_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_host_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['resource_hw_ver_A'],
                                                        curr_mcast_obj.client_dict_A[tos]["clients_A"],
                                                        curr_mcast_obj.client_dict_A[tos]['port_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['mode_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['mac_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['ssid_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['channel_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['traffic_type_A'],
                                                        curr_mcast_obj.client_dict_A[tos]['traffic_protocol_A'],
                                                        off_up,
                                                        off_down,
                                                        up,
                                                        down,
                                                        [],
                                                        curr_mcast_obj.client_dict_A[tos]['download_rx_drop_percent_A'],
                                                        [],)
                                                # When the client exists in either group.
                                                if dataframe:
                                                    self.overall_report.set_obj_html("", "Group: {}".format(key))
                                                    self.overall_report.build_objective()
                                                    dataframe1 = pd.DataFrame(dataframe)
                                                    self.overall_report.set_table_dataframe(dataframe1)
                                                    self.overall_report.build_table()
                                        else:
                                            tos_dataframe_A = {
                                                " Client Alias ": curr_mcast_obj.client_dict_A[tos]['resource_alias_A'],
                                                " Host eid ": curr_mcast_obj.client_dict_A[tos]['resource_eid_A'],
                                                " Host Name ": curr_mcast_obj.client_dict_A[tos]['resource_host_A'],
                                                " Device Type / Hw Ver ": curr_mcast_obj.client_dict_A[tos]['resource_hw_ver_A'],
                                                " Endp Name": curr_mcast_obj.client_dict_A[tos]["clients_A"],
                                                # TODO : port A being set to many times
                                                " Port Name ": curr_mcast_obj.client_dict_A[tos]['port_A'],
                                                " Mode ": curr_mcast_obj.client_dict_A[tos]['mode_A'],
                                                " Mac ": curr_mcast_obj.client_dict_A[tos]['mac_A'],
                                                " SSID ": curr_mcast_obj.client_dict_A[tos]['ssid_A'],
                                                " Channel ": curr_mcast_obj.client_dict_A[tos]['channel_A'],
                                                " Type of traffic ": curr_mcast_obj.client_dict_A[tos]['traffic_type_A'],
                                                " Traffic Protocol ": curr_mcast_obj.client_dict_A[tos]['traffic_protocol_A'],
                                                " Offered Upload Rate Per Client": curr_mcast_obj.client_dict_A[tos]['offered_upload_rate_A'],
                                                " Offered Download Rate Per Client": curr_mcast_obj.client_dict_A[tos]['offered_download_rate_A'],
                                                " Upload Rate Per Client": curr_mcast_obj.client_dict_A[tos]['ul_A'],
                                                " Download Rate Per Client": curr_mcast_obj.client_dict_A[tos]['dl_A'],
                                                " Drop Percentage (%)": curr_mcast_obj.client_dict_A[tos]['download_rx_drop_percent_A'],
                                            }
                                            # When pass_Fail criteria specified
                                            if curr_mcast_obj.expected_passfail_value or curr_mcast_obj.device_csv_name:
                                                tos_dataframe_A[" Expected " + 'Download' + " Rate"] = [float(x) * 10**6 for x in test_input_list]
                                                tos_dataframe_A[" Status "] = pass_fail_list

                                            dataframe3 = pd.DataFrame(tos_dataframe_A)
                                            self.overall_report.set_table_dataframe(dataframe3)
                                            self.overall_report.build_table()

                                    # For virtual clients
                                    else:
                                        tos_dataframe_A = {
                                            " Client Alias ": curr_mcast_obj.client_dict_A[tos]['resource_alias_A'],
                                            " Host eid ": curr_mcast_obj.client_dict_A[tos]['resource_eid_A'],
                                            " Host Name ": curr_mcast_obj.client_dict_A[tos]['resource_host_A'],
                                            " Device Type / Hw Ver ": curr_mcast_obj.client_dict_A[tos]['resource_hw_ver_A'],
                                            " Endp Name": curr_mcast_obj.client_dict_A[tos]["clients_A"],
                                            " Port Name ": curr_mcast_obj.client_dict_A[tos]['port_A'],
                                            " Mode ": curr_mcast_obj.client_dict_A[tos]['mode_A'],
                                            " Mac ": curr_mcast_obj.client_dict_A[tos]['mac_A'],
                                            " SSID ": curr_mcast_obj.client_dict_A[tos]['ssid_A'],
                                            " Channel ": curr_mcast_obj.client_dict_A[tos]['channel_A'],
                                            " Type of traffic ": curr_mcast_obj.client_dict_A[tos]['traffic_type_A'],
                                            " Traffic Protocol ": curr_mcast_obj.client_dict_A[tos]['traffic_protocol_A'],
                                            " Offered Upload Rate Per Client": curr_mcast_obj.client_dict_A[tos]['offered_upload_rate_A'],
                                            " Offered Download Rate Per Client": curr_mcast_obj.client_dict_A[tos]['offered_download_rate_A'],
                                            " Upload Rate Per Client": curr_mcast_obj.client_dict_A[tos]['ul_A'],
                                            " Download Rate Per Client": curr_mcast_obj.client_dict_A[tos]['dl_A'],
                                            " Drop Percentage (%)": curr_mcast_obj.client_dict_A[tos]['download_rx_drop_percent_A'],
                                        }
                                        dataframe3 = pd.DataFrame(tos_dataframe_A)
                                        self.overall_report.set_table_dataframe(dataframe3)
                                        self.overall_report.build_table()

                            # TODO both client_dict_A and client_dict_B contains the same information
                            for tos in tos_list:
                                if (curr_mcast_obj.client_dict_B[tos]["ul_B"] and curr_mcast_obj.client_dict_B[tos]["dl_B"]):
                                    min_bps_a = curr_mcast_obj.client_dict_B["min_bps_a"]
                                    min_bps_b = curr_mcast_obj.client_dict_B["min_bps_b"]

                                    dataset_list = [curr_mcast_obj.client_dict_B[tos]["ul_B"], curr_mcast_obj.client_dict_B[tos]["dl_B"]]
                                    dataset_length = len(curr_mcast_obj.client_dict_B[tos]["ul_B"])

                                    x_fig_size = 20
                                    y_fig_size = len(curr_mcast_obj.client_dict_B[tos]["clients_B"]) * .4 + 5

                                    self.overall_report.set_obj_html(
                                        _obj_title=f"Individual throughput upstream endp,  offered upload bps: {min_bps_a} offered download bps: {min_bps_b} /station for traffic {tos} (WiFi).",
                                        _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                        f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                        f"Throughput in Mbps”.")
                                    self.overall_report.build_objective()

                                    graph = lf_bar_graph_horizontal(_data_set=dataset_list,
                                                                    _xaxis_name="Throughput in bps",
                                                                    _yaxis_name="Client names",
                                                                    # _yaxis_categories=curr_mcast_obj.client_dict_B[tos]["clients_B"],
                                                                    _yaxis_categories=curr_mcast_obj.client_dict_B[tos]["resource_alias_B"],
                                                                    _graph_image_name=f"{tos}_B{obj_no}",
                                                                    _label=curr_mcast_obj.client_dict_B[tos]['labels'],
                                                                    _color_name=curr_mcast_obj.client_dict_B[tos]['colors'],
                                                                    _color_edge=['black'],
                                                                    _graph_title=f"Individual {tos} upstream side traffic measurement - side b (WIFI) traffic",
                                                                    _title_size=10,
                                                                    _figsize=(x_fig_size, y_fig_size),
                                                                    _show_bar_value=True,
                                                                    _enable_csv=True,
                                                                    _text_font=8,
                                                                    _legend_loc="best",
                                                                    _legend_box=(1.0, 1.0)
                                                                    )
                                    graph_png = graph.build_bar_graph_horizontal()
                                    self.overall_report.set_graph_image(graph_png)
                                    self.overall_report.move_graph_image()
                                    self.overall_report.build_graph()
                                    self.overall_report.set_csv_filename(graph_png)
                                    self.overall_report.move_csv_file()

                                    tos_dataframe_B = {
                                        " Client Alias ": curr_mcast_obj.client_dict_B[tos]['resource_alias_B'],
                                        " Host eid ": curr_mcast_obj.client_dict_B[tos]['resource_eid_B'],
                                        " Host Name ": curr_mcast_obj.client_dict_B[tos]['resource_host_B'],
                                        " Device Type / HW Ver ": curr_mcast_obj.client_dict_B[tos]['resource_hw_ver_B'],
                                        " Endp Name": curr_mcast_obj.client_dict_B[tos]["clients_B"],
                                        # TODO get correct size
                                        " Port Name ": curr_mcast_obj.client_dict_B[tos]['port_B'],
                                        " Mode ": curr_mcast_obj.client_dict_B[tos]['mode_B'],
                                        " Mac ": curr_mcast_obj.client_dict_B[tos]['mac_B'],
                                        " SSID ": curr_mcast_obj.client_dict_B[tos]['ssid_B'],
                                        " Channel ": curr_mcast_obj.client_dict_B[tos]['channel_B'],
                                        " Type of traffic ": curr_mcast_obj.client_dict_B[tos]['traffic_type_B'],
                                        " Traffic Protocol ": curr_mcast_obj.client_dict_B[tos]['traffic_protocol_B'],
                                        " Offered Upload Rate Per Client": curr_mcast_obj.client_dict_B[tos]['offered_upload_rate_B'],
                                        " Offered Download Rate Per Client": curr_mcast_obj.client_dict_B[tos]['offered_download_rate_B'],
                                        " Upload Rate Per Client": curr_mcast_obj.client_dict_B[tos]['ul_B'],
                                        " Download Rate Per Client": curr_mcast_obj.client_dict_B[tos]['dl_B'],
                                        " Drop Percentage (%)": curr_mcast_obj.client_dict_B[tos]['download_rx_drop_percent_B']
                                    }

                                    dataframe3 = pd.DataFrame(tos_dataframe_B)
                                    self.overall_report.set_table_dataframe(dataframe3)
                                    self.overall_report.build_table()

                            if self.robot_test and self.do_bandsteering:
                                curr_mcast_obj.report = self.overall_report
                                curr_mcast_obj.get_bandsteering_stats()
                            # empty dictionarys evaluate to false , placing tables in output
                            if bool(curr_mcast_obj.dl_port_csv_files):
                                for key, value in curr_mcast_obj.dl_port_csv_files.items():
                                    if curr_mcast_obj.csv_data_to_report:
                                        # read the csv file
                                        self.overall_report.set_table_title("Layer 3 Cx Traffic  {key}".format(key=key))
                                        self.overall_report.build_table_title()
                                        self.overall_report.set_table_dataframe_from_csv(value.name)
                                        self.overall_report.build_table()

                                    # read in column heading and last line
                                    df = pd.read_csv(value.name)
                                    last_row = df.tail(1)
                                    self.overall_report.set_table_title(
                                        "Layer 3 Cx Traffic Last Reporting Interval {key}".format(key=key))
                                    self.overall_report.build_table_title()
                                    self.overall_report.set_table_dataframe(last_row)
                                    self.overall_report.build_table()

                        if ce == "series":
                            obj_no += 1
                            obj_name = f"mcast_test_{obj_no}"
                        else:
                            break

                elif test_name == "vs_test":
                    """Processes video streaming test reporting and visualizations."""
                    obj_no = 1
                    obj_name = "vs_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.vs_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''

                        curr_vs_obj = copy.copy(self.vs_obj_dict[ce][obj_name]["obj"])
                        if not self.robot_test or (self.robot_test and self.do_bandsteering):
                            if not self.do_bandsteering:
                                params = self.vs_obj_dict[ce][obj_name]["data"].copy()
                                iterations_before_test_stopped_by_user = (
                                    params["iterations_before_test_stopped_by_user"].copy()
                                    if isinstance(params["iterations_before_test_stopped_by_user"], (list, dict, set))
                                    else params["iterations_before_test_stopped_by_user"]
                                )

                                test_setup_info = (
                                    params["test_setup_info"].copy()
                                    if isinstance(params["test_setup_info"], (list, dict, set))
                                    else params["test_setup_info"]
                                )

                                realtime_dataset = (
                                    params["realtime_dataset"].copy()
                                    if isinstance(params["realtime_dataset"], (list, dict, set))
                                    else params["realtime_dataset"]
                                )

                                report_path = (
                                    params["report_path"].copy()
                                    if isinstance(params["report_path"], (list, dict, set))
                                    else params["report_path"]
                                )

                            else:
                                test_setup_info = curr_vs_obj.create_test_setup_info(
                                    media_source=curr_vs_obj.media_source, media_quality=curr_vs_obj.media_quality)
                                iterations_before_test_stopped_by_user = [0]
                                realtime_dataset = curr_vs_obj.vs_stats
                                report_path = ''
                            self.overall_report.set_obj_html(_obj_title=f'Video Streaming Test {obj_no}', _obj="")
                            self.overall_report.build_objective()
                            created_incremental_values = curr_vs_obj.get_incremental_capacity_list()
                            keys = list(curr_vs_obj.http_profile.created_cx.keys())

                            self.overall_report.set_table_title("Input Parameters")
                            self.overall_report.build_table_title()
                            if curr_vs_obj.config:
                                test_setup_info["SSID"] = curr_vs_obj.ssid
                                test_setup_info["Password"] = curr_vs_obj.passwd
                                test_setup_info["ENCRYPTION"] = curr_vs_obj.encryp
                            elif len(curr_vs_obj.selected_groups) > 0 and len(curr_vs_obj.selected_profiles) > 0:
                                # Map each group with a profile
                                gp_pairs = zip(curr_vs_obj.selected_groups, curr_vs_obj.selected_profiles)
                                # Create a string by joining the mapped pairs
                                gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)
                                test_setup_info["Configuration"] = gp_map

                            self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

                            device_type = []
                            username = []
                            ssid = []
                            mac = []
                            channel = []
                            mode = []
                            rssi = []
                            channel = []
                            tx_rate = []
                            resource_ids = list(map(int, curr_vs_obj.resource_ids.split(',')))
                            try:
                                eid_data = curr_vs_obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")
                            except KeyError:
                                logger.error("Error: 'interfaces' key not found in port data")
                                exit(1)

                            # Loop through interfaces
                            for alias in eid_data["interfaces"]:
                                for i in alias:
                                    # Check interface index and alias
                                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':

                                        # Get resource data for specific interface
                                        resource_hw_data = curr_vs_obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
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
                            total_urls = curr_vs_obj.data["total_urls"]
                            total_err = curr_vs_obj.data["total_err"]
                            total_buffer = curr_vs_obj.data["total_buffer"]
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
                                    min_val = curr_vs_obj.process_list(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist())
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
                                    trimmed_data_set_in_graph.append(curr_vs_obj.trim_data(len(data_set_in_graph[_]), data_set_in_graph[_]))

                                # If there are multiple incremental values, add custom HTML content to the report for the current iteration
                                if len(created_incremental_values) > 1:
                                    self.overall_report.set_custom_html(f"<h2><u>Iteration-{iter + 1}</u></h2>")
                                    self.overall_report.build_custom()

                                self.overall_report.set_obj_html(
                                    _obj_title=f"Realtime Video Rate: Number of devices running: {len(device_names_on_running)}",
                                    _obj="")
                                self.overall_report.build_objective()

                                # Create a line graph for video rate over time
                                graph = lf_line_graph(_data_set=trimmed_data_set_in_graph,
                                                      _xaxis_name="Time",
                                                      _yaxis_name="Video Rate (Mbps)",
                                                      _xaxis_categories=curr_vs_obj.trim_data(len(realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
                                                                                              realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
                                                      _label=['Rate'],
                                                      _graph_image_name=f"vs_line_graph{iter}{obj_no}"
                                                      )
                                graph_png = graph.build_line_graph()
                                logger.info("graph name {}".format(graph_png))
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()

                                self.overall_report.build_graph()

                                # Define figure size for horizontal bar graphs
                                x_fig_size = 15
                                y_fig_size = len(devices_on_running_state) * .5 + 4

                                self.overall_report.set_obj_html(
                                    _obj_title="Total Urls Per Device",
                                    _obj="")
                                self.overall_report.build_objective()
                                # Create a horizontal bar graph for total URLs per device
                                graph = lf_bar_graph_horizontal(_data_set=[total_urls[:created_incremental_values[iter]]],
                                                                _xaxis_name="Total Urls",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"total_urls_image_name{iter}{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_obj_html(
                                    _obj_title="Max/Min Video Rate Per Device",
                                    _obj="")
                                self.overall_report.build_objective()

                                # Create a horizontal bar graph for max and min video rates per device
                                graph = lf_bar_graph_horizontal(_data_set=[max_video_rate, min_video_rate],
                                                                _xaxis_name="Max/Min Video Rate(Mbps)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"max-min-video-rate_image_name{iter}{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_obj_html(
                                    _obj_title="Wait Time Per Device",
                                    _obj="")
                                self.overall_report.build_objective()

                                # Create a horizontal bar graph for wait time per device
                                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_wait_time_bar_graph,
                                                                _xaxis_name="Wait Time(seconds)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"wait_time_image_name{iter}{obj_no}",
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
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                if curr_vs_obj.dowebgui and curr_vs_obj.get_live_view and not curr_vs_obj.do_bandsteering:
                                    script_dir = os.path.dirname(os.path.abspath(__file__))

                                    self.overall_report.set_custom_html("<h2>No of Buffers and Wait Time %</h2>")
                                    self.overall_report.build_custom()

                                    for floor in range(int(curr_vs_obj.floors)):
                                        # Construct expected image paths
                                        vs_buffer_image = os.path.join(script_dir, "heatmap_images", f"{self.vs_obj_dict[ce][obj_name]['obj'].test_name}_vs_buffer_{floor + 1}.png")
                                        vs_wait_time_image = os.path.join(script_dir, "heatmap_images", f"{self.vs_obj_dict[ce][obj_name]['obj'].test_name}_vs_wait_time_{floor + 1}.png")

                                        # Wait for all required images to be generated (up to timeout)
                                        timeout = 60  # seconds
                                        start_time = time.time()

                                        while not (os.path.exists(vs_buffer_image) and os.path.exists(vs_wait_time_image)):
                                            if time.time() - start_time > timeout:
                                                logging.warning("Timeout: Heatmap images for floor %d not found within %d seconds.", floor + 1, timeout)
                                                break
                                            time.sleep(1)

                                        # Generate report sections for each image if it exists
                                        for image_path in [vs_buffer_image, vs_wait_time_image]:
                                            if os.path.exists(image_path):
                                                self.overall_report.set_custom_html(f'<img src="file://{image_path}"  style="width:1200px; height:800px;"></img>')
                                                self.overall_report.build_custom()

                                # Table 1
                                self.overall_report.set_obj_html("Overall - Detailed Result Table", "The below tables provides detailed information for the Video Streaming test.")
                                self.overall_report.build_objective()
                                test_data = {
                                    "iter": iter,
                                    "created_incremental_values": created_incremental_values,
                                    "device_type": device_type,
                                    "username": username,
                                    "ssid": ssid,
                                    "mac": mac,
                                    "channel": channel,
                                    "mode": mode,
                                    "total_buffer": total_buffer,
                                    "wait_time_data": wait_time_data,
                                    "min_video_rate": min_video_rate,
                                    "avg_video_rate": avg_video_rate,
                                    "max_video_rate": max_video_rate,
                                    "total_urls": total_urls,
                                    "total_err": total_err,
                                    "rssi_data": rssi_data,
                                    "tx_rate": tx_rate,
                                    "max_bytes_rd_list": max_bytes_rd_list,
                                    "avg_rx_rate_list": avg_rx_rate_list
                                }

                                dataframe = curr_vs_obj.handle_passfail_criteria(test_data)

                                dataframe1 = pd.DataFrame(dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                                # Set and build title for the overall results table
                                self.overall_report.set_obj_html("Detailed Total Errors Table", "The below tables provides detailed information of total errors for the web browsing test.")
                                self.overall_report.build_objective()
                                dataframe2 = {
                                    " DEVICE": username[:created_incremental_values[iter]],
                                    " TOTAL ERRORS ": total_err[:created_incremental_values[iter]],
                                }
                                dataframe3 = pd.DataFrame(dataframe2)
                                self.overall_report.set_table_dataframe(dataframe3)
                                self.overall_report.build_table()
                                if curr_vs_obj.do_bandsteering:
                                    devices_on_running_state = []
                                    device_names_on_running = []
                                    for j in range(created_incremental_values[iter]):
                                        devices_on_running_state.append(keys[j])
                                        device_names_on_running.append(username[j])
                                    curr_vs_obj.get_bandsteering_stats(self.overall_report, realtime_dataset, devices_on_running_state, device_names_on_running)
                        else:
                            params = curr_vs_obj.vs_data
                            test_setup_info_vs = params[self.coordinate_list[0]]["test_setup_info"]
                            self.overall_report.set_obj_html(_obj_title=f'Video Streaming Test {obj_no}', _obj="")
                            self.overall_report.build_objective()
                            created_incremental_values = curr_vs_obj.get_incremental_capacity_list()
                            keys = list(curr_vs_obj.http_profile.created_cx.keys())
                            self.overall_report.set_table_title("Input Parameters")
                            self.overall_report.build_table_title()
                            test_setup_info_vs["SSID"] = curr_vs_obj.ssid
                            test_setup_info_vs["Password"] = curr_vs_obj.passwd
                            test_setup_info_vs["ENCRYPTION"] = curr_vs_obj.encryp
                            self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info_vs)
                            device_type = []
                            username = []
                            ssid = []
                            mac = []
                            channel = []
                            mode = []
                            rssi = []
                            tx_rate = []
                            resource_ids = list(map(int, curr_vs_obj.resource_ids.split(',')))
                            try:
                                eid_data = curr_vs_obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")
                            except KeyError:
                                logger.error("Error: 'interfaces' key not found in port data")
                                exit(1)

                            # Loop through interfaces
                            for alias in eid_data["interfaces"]:
                                for i in alias:
                                    # Check interface index and alias
                                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':

                                        # Get resource data for specific interface
                                        resource_hw_data = curr_vs_obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
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
                            curr_vs_obj.get_live_view = True
                            curr_vs_obj.add_buffer_and_wait_time_images(report=self.overall_report)
                            for coordinate in range(len(self.coordinate_list)):
                                curr_vs_obj.current_coordinate = curr_vs_obj.coordinate_list[coordinate]
                                if curr_vs_obj.rotation_enabled:
                                    for angle in range(len(curr_vs_obj.rotation_list)):
                                        curr_vs_obj.current_angle = curr_vs_obj.rotation_list[angle]
                                        coord, ang = curr_vs_obj.coordinate_list[coordinate], curr_vs_obj.rotation_list[angle]
                                        curr_vs_obj.data = curr_vs_obj.vs_data[int(coord)][ang]["self_data"]
                                        curr_vs_obj.generate_individual_coordinate(
                                            self.overall_report, device_type, username, ssid, mac, channel, mode, rssi, tx_rate, created_incremental_values, keys)
                                else:
                                    curr_vs_obj.data = curr_vs_obj.vs_data[self.vs_obj_dict[ce]
                                                                           [obj_name]["obj"].coordinate_list[coordinate]]["self_data"]
                                    curr_vs_obj.generate_individual_coordinate(
                                        self.overall_report, device_type, username, ssid, mac, channel, mode, rssi, tx_rate, created_incremental_values, keys)
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"vs_test_{obj_no}"
                        else:
                            break

                elif test_name == "rb_test":
                    """
                    Generates the test report for Real Browser (rb_test) streams.
                    Processes URL access success rates, time taken per URL, and BSSID transitions.
                    """
                    obj_no = 1
                    obj_name = "rb_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.rb_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'Real Browser Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()
                        curr_rb_obj = copy.copy(self.rb_obj_dict[ce][obj_name]["obj"])
                        if not self.robot_test or self.do_bandsteering:
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
                            csv_paths = curr_rb_obj.report_path_date_time if not self.dowebgui else self.result_dir
                            if self.do_bandsteering and self.dowebgui:
                                csv_paths = curr_rb_obj.report_path_date_time

                            final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = curr_rb_obj.extract_device_data(
                                '{}/real_time_data.csv'.format(csv_paths))

                            test_setup_info = curr_rb_obj.generate_test_setup_info()
                            self.overall_report.test_setup_table(
                                test_setup_data=test_setup_info, value='Test Parameters')
                            curr_rb_obj.csv_file_names
                            for i in range(0, len(curr_rb_obj.csv_file_names)):
                                if curr_rb_obj.csv_file_names[i].startswith("real_time_data.csv") and not self.do_bandsteering:
                                    continue

                                final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = curr_rb_obj.extract_device_data(
                                    "{}/{}".format(csv_paths, curr_rb_obj.csv_file_names[i]))
                                self.overall_report.set_graph_title("Successful URL's per Device")
                                self.overall_report.build_graph_title()

                                data = pd.read_csv("{}/{}".format(csv_paths, curr_rb_obj.csv_file_names[i]))

                                # Extract device names from CSV
                                if 'total_urls' in data.columns:
                                    total_urls = data['total_urls'].tolist()
                                else:
                                    raise ValueError("The 'total_urls' column was not found in the CSV file.")
                                x_fig_size = 18
                                y_fig_size = len(device_type_data) * 1 + 4
                                logging.info(f"Device names for {self.rb_obj_dict[ce][obj_name]['obj'].csv_file_names[i]}: {device_names}")
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
                                    _graph_image_name=f"{self.rb_obj_dict[ce][obj_name]['obj'].csv_file_names[i]}_urls_per_device{obj_no}",
                                    _label=["URLs"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_graph_title(f"Time Taken Vs Device For Completing {self.rb_obj_dict[ce][obj_name]['obj'].count} RealTime URLs")
                                self.overall_report.build_graph_title()

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
                                    _graph_image_name=f"{self.rb_obj_dict[ce][obj_name]['obj'].csv_file_names[i]}_time_taken_for_urls{obj_no}",
                                    _label=["Time (in sec)"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

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

                            self.overall_report.set_table_title("Final Test Results")
                            self.overall_report.build_table_title()
                            if curr_rb_obj.expected_passfail_value or curr_rb_obj.device_csv_name:
                                pass_fail_list, test_input_list = curr_rb_obj.generate_pass_fail_list(device_type_data, device_names, total_urls)

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
                            logger.info(f"dataframe realbrowser {final_test_results}")
                            test_results_df = pd.DataFrame(final_test_results)
                            self.overall_report.set_table_dataframe(test_results_df)
                            self.overall_report.build_table()
                            folder = csv_paths  # report folder

                            band_files = [
                                os.path.join(folder, f)
                                for f in os.listdir(folder)
                                if f.endswith("_bandsteering.csv")
                            ]
                            self.overall_report.set_table_title("Band Steering – BSSID Transition Analysis")
                            self.overall_report.build_table_title()

                            for file in band_files:
                                logging.info(f"Processing band steering file: {file}")

                                df = pd.read_csv(file)

                                if df.empty or "bssid" not in df.columns:
                                    continue

                                device_name = os.path.basename(file).replace("_bandsteering.csv", "")

                                df["bssid"] = df["bssid"].astype(str).str.upper().str.strip()

                                df["prev_bssid"] = df["bssid"].shift()

                                transition_mask = (
                                    (df["bssid"] != df["prev_bssid"]) &
                                    (df["bssid"] != "NA")
                                )

                                transition_rows = df[transition_mask]

                                bssid_counts = {}

                                transitions = []

                                for _, row in transition_rows.iterrows():
                                    curr_bssid = row["bssid"]

                                    if curr_bssid not in bssid_counts:
                                        bssid_counts[curr_bssid] = 0

                                    bssid_counts[curr_bssid] += 1

                                    transitions.append({
                                        "BSSID": curr_bssid,
                                        "Timestamp": row.get("timestamp", "NA"),
                                        "From Coordinate": row.get("from_coordinate", "NA"),
                                        "To Coordinate": row.get("to_coordinate", "NA"),
                                        "Channel": row.get("channel", "NA")
                                    })

                                bssid_list = list(bssid_counts.keys())
                                count_list = list(bssid_counts.values())

                                if not bssid_list:
                                    bssid_list = ["No Transition"]
                                    count_list = [0]

                                self.overall_report.set_graph_title(f"BSSID Change Count – {device_name}")
                                self.overall_report.build_graph_title()

                                graph = lf_bar_graph_horizontal(
                                    _data_set=[count_list],
                                    _xaxis_name="Transition Count",
                                    _yaxis_name="BSSID",
                                    _yaxis_label=bssid_list,
                                    _yaxis_categories=bssid_list,
                                    _bar_height=0.25,
                                    _show_bar_value=True,
                                    _figsize=(18, max(4, len(bssid_list))),
                                    _graph_title="BSSID Transitions",
                                    _graph_image_name=f"{device_name}_bssid_transitions",
                                    _label=["Transitions"]
                                )

                                graph_image = graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_table_title(f"Band Steering Results for {device_name}")
                                self.overall_report.build_table_title()

                                if not transitions:
                                    first_row = df.iloc[0]
                                    last_row = df.iloc[-1]

                                    transitions.append({
                                        "BSSID": first_row.get("bssid", "NA"),
                                        "Timestamp": last_row.get("timestamp", "NA"),
                                        "From Coordinate": first_row.get("from_coordinate", "NA"),
                                        "To Coordinate": last_row.get("to_coordinate", "NA"),
                                        "Channel": first_row.get("channel", "NA")
                                    })

                                transition_df = pd.DataFrame(transitions)

                                self.overall_report.set_table_dataframe(transition_df)
                                self.overall_report.build_table()

                        else:
                            test_setup_info = curr_rb_obj.generate_test_setup_info()
                            self.overall_report.test_setup_table(
                                test_setup_data=test_setup_info, value='Test Parameters')
                            if self.dowebgui:
                                if self.robot_test:
                                    url_image_path = os.path.join(self.rb_obj_dict[ce][obj_name]['obj'].result_dir, "live_view_images", f"rb_{self.rb_obj_dict[ce][obj_name]['obj'].test_name}_1.png")
                                    timeout = 60  # seconds
                                    start_time = time.time()
                                    while not os.path.exists(url_image_path):
                                        if time.time() - start_time > timeout:
                                            logging.error("Timeout: Images not found within 60 seconds.")
                                            break
                                        time.sleep(1)
                                    if os.path.exists(url_image_path):
                                        html_content = (
                                            '<div style="page-break-before: always;"></div>'
                                            f'<img src="file://{url_image_path}" style="width:1200px; height:800px;"></img>'
                                        )
                                        self.overall_report.set_custom_html(html_content)
                                        self.overall_report.build_custom()
                            curr_rb_obj.report = self.overall_report
                            for coordinate in curr_rb_obj.coordinates_list:
                                if curr_rb_obj.rotations_enabled:
                                    for angle in curr_rb_obj.angles_list:
                                        try:
                                            if (self.dowebgui):
                                                csv_file = os.path.join(
                                                    f"{coordinate}_{angle}_webBrowser.csv"
                                                )
                                            else:
                                                csv_file = os.path.join(
                                                    curr_rb_obj.report_path_date_time,
                                                    f"{coordinate}_{angle}_webBrowser.csv"
                                                )
                                            _, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = curr_rb_obj.extract_device_data(
                                                csv_file)
                                            if curr_rb_obj.rotations_enabled:
                                                self.overall_report.set_graph_title(f"Successful URL's per Device at coordinate {coordinate} and angle {angle}")
                                            else:
                                                self.overall_report.set_graph_title(f"Successful URL's per Device at coordinate {coordinate}")
                                            self.overall_report.build_graph_title()
                                            data = pd.read_csv(csv_file)
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
                                                _graph_image_name=f"{coordinate}_{angle}_urls_per_device",
                                                _label=["URLs"]
                                            )
                                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                            self.overall_report.set_graph_image(graph_image)
                                            self.overall_report.move_graph_image()
                                            self.overall_report.build_graph()
                                            if curr_rb_obj.rotations_enabled:
                                                self.overall_report.set_graph_title(
                                                    f"Time Taken Vs Device For Completing "
                                                    f"{curr_rb_obj.count} RealTime URLs "
                                                    f"at coordinate {coordinate} and angle {angle}"
                                                )
                                            else:
                                                self.overall_report.set_graph_title(
                                                    f"Time Taken Vs Device For Completing "
                                                    f"{curr_rb_obj.count} RealTime URLs "
                                                    f"at coordinate {coordinate}"
                                                )

                                            self.overall_report.build_graph_title()

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
                                                _graph_image_name=f"{coordinate}_{angle}_time_taken_for_urls",
                                                _label=["Time (in sec)"]
                                            )
                                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                            self.overall_report.set_graph_image(graph_image)
                                            self.overall_report.move_graph_image()
                                            self.overall_report.build_graph()

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

                                            if curr_rb_obj.rotations_enabled:
                                                self.overall_report.set_table_title(f"Final Test Results at coordinate {coordinate} and angle {angle}:")
                                            else:
                                                self.overall_report.set_table_title(f"Final Test Results at coordinate {coordinate}:")
                                            self.overall_report.build_table_title()
                                            if curr_rb_obj.expected_passfail_value or curr_rb_obj.device_csv_name:
                                                pass_fail_list, test_input_list = curr_rb_obj.generate_pass_fail_list(device_type_data, device_names, total_urls)

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
                                                    "Total Errors": total_err_data,
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
                                                    "Total Errors": total_err_data,
                                                    "RSSI": signal_data,
                                                    "Link Speed": tx_rate_data,

                                                }
                                            test_results_df = pd.DataFrame(final_test_results)
                                            self.overall_report.set_table_dataframe(test_results_df)
                                            self.overall_report.build_table()

                                        except Exception as e:
                                            logging.error(f"Error in create_robo_graphs_test_results {e}", exc_info=True)

                                else:
                                    if (self.dowebgui):
                                        csv_file = os.path.join(curr_rb_obj.report.path,
                                                                f"{coordinate}_webBrowser.csv"
                                                                )
                                    else:
                                        csv_file = os.path.join(
                                            curr_rb_obj.report_path_date_time,
                                            f"{coordinate}_webBrowser.csv"
                                        )
                                    try:
                                        angle = None
                                        _, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = curr_rb_obj.extract_device_data(
                                            csv_file)
                                        if curr_rb_obj.rotations_enabled:
                                            self.overall_report.set_graph_title(f"Successful URL's per Device at coordinate {coordinate} and angle {angle}")
                                        else:
                                            self.overall_report.set_graph_title(f"Successful URL's per Device at coordinate {coordinate}")
                                        self.overall_report.build_graph_title()
                                        data = pd.read_csv(csv_file)
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
                                            _graph_image_name=f"{coordinate}_{angle}_urls_per_device",
                                            _label=["URLs"]
                                        )
                                        graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                        self.overall_report.set_graph_image(graph_image)
                                        self.overall_report.move_graph_image()
                                        self.overall_report.build_graph()
                                        if curr_rb_obj.rotations_enabled:
                                            self.overall_report.set_graph_title(
                                                f"Time Taken Vs Device For Completing "
                                                f"{curr_rb_obj.count} RealTime URLs "
                                                f"at coordinate {coordinate} and angle {angle}"
                                            )
                                        else:
                                            self.overall_report.set_graph_title(
                                                f"Time Taken Vs Device For Completing "
                                                f"{curr_rb_obj.count} RealTime URLs "
                                                f"at coordinate {coordinate}"
                                            )
                                        self.overall_report.build_graph_title()

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
                                            _graph_image_name=f"{coordinate}_{angle}_time_taken_for_urls",
                                            _label=["Time (in sec)"]
                                        )
                                        graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                        self.overall_report.set_graph_image(graph_image)
                                        self.overall_report.move_graph_image()
                                        self.overall_report.build_graph()

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

                                        if curr_rb_obj.rotations_enabled:
                                            self.overall_report.set_table_title(f"Final Test Results at coordinate {coordinate} and angle {angle}:")
                                        else:
                                            self.overall_report.set_table_title(f"Final Test Results at coordinate {coordinate}:")
                                        self.overall_report.build_table_title()
                                        if curr_rb_obj.expected_passfail_value or curr_rb_obj.device_csv_name:
                                            pass_fail_list, test_input_list = curr_rb_obj.generate_pass_fail_list(device_type_data, device_names, total_urls)

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
                                                "Total Errors": total_err_data,
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
                                                "Total Errors": total_err_data,
                                                "RSSI": signal_data,
                                                "Link Speed": tx_rate_data,

                                            }
                                        test_results_df = pd.DataFrame(final_test_results)
                                        self.overall_report.set_table_dataframe(test_results_df)
                                        self.overall_report.build_table()

                                    except Exception as e:
                                        logging.error(f"Error in create_robo_graphs_test_results {e}", exc_info=True)

                                os.chdir(curr_rb_obj.original_dir)
                            curr_rb_obj.report.build_custom()
                            curr_rb_obj.report.build_footer()
                            curr_rb_obj.report.write_html()
                            curr_rb_obj.report.write_pdf()

                        if curr_rb_obj.dowebgui:

                            os.chdir(curr_rb_obj.original_dir)

                        if ce == "series":
                            obj_no += 1
                            obj_name = f"rb_test_{obj_no}"
                        else:
                            break

                elif test_name == "yt_test":
                    """
                    Generates the test report for YouTube (yt_test) streams.
                    Collects and plots buffer health, dropped frames, and total frames.
                    """
                    obj_no = 1
                    obj_name = "yt_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.yt_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        curr_yt_obj = copy.copy((self.yt_obj_dict[ce][obj_name]["obj"]))
                        result_data = curr_yt_obj.stats_api_response
                        for device, stats in result_data.items():
                            curr_yt_obj.mydatajson.setdefault(device, {}).update({
                                "Viewport": stats.get("Viewport", ""),
                                "DroppedFrames": stats.get("DroppedFrames", "0"),
                                "TotalFrames": stats.get("TotalFrames", "0"),
                                "CurrentRes": stats.get("CurrentRes", ""),
                                "OptimalRes": stats.get("OptimalRes", ""),
                                "BufferHealth": stats.get("BufferHealth", "0.0"),
                                "Timestamp": stats.get("Timestamp", ""),
                            })

                        if curr_yt_obj.config:

                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': curr_yt_obj.duration,
                                'Resolution': curr_yt_obj.resolution,
                                'Configured Devices': curr_yt_obj.hostname_os_combination,
                                'No of Devices :': f' Total({len(curr_yt_obj.real_sta_os_types)}) : W({curr_yt_obj.windows}),L({curr_yt_obj.linux}),M({curr_yt_obj.mac})',
                                "Video URL": curr_yt_obj.url,
                                "SSID": curr_yt_obj.ssid,
                                "Security": curr_yt_obj.security,

                            }

                        elif len(curr_yt_obj.selected_groups) > 0 and len(curr_yt_obj.selected_profiles) > 0:
                            gp_pairs = zip(curr_yt_obj.selected_groups, curr_yt_obj.selected_profiles)
                            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': curr_yt_obj.duration,
                                'Resolution': curr_yt_obj.resolution,
                                "Configuration": gp_map,
                                'Configured Devices': curr_yt_obj.hostname_os_combination,
                                'No of Devices :': f' Total({len(curr_yt_obj.real_sta_os_types)}) : W({curr_yt_obj.windows}),L({curr_yt_obj.linux}),M({curr_yt_obj.mac})',
                                "Video URL": curr_yt_obj.url,

                            }
                        else:
                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': curr_yt_obj.duration,
                                'Resolution': curr_yt_obj.resolution,
                                'Configured Devices': curr_yt_obj.hostname_os_combination,
                                'No of Devices :': f' Total({len(curr_yt_obj.real_sta_os_types)}) : W({curr_yt_obj.windows}),L({curr_yt_obj.linux}),M({curr_yt_obj.mac})',
                                "Video URL": curr_yt_obj.url,

                            }
                        self.overall_report.set_obj_html(_obj_title=f'Youtube Streaming Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.test_setup_table(
                            test_setup_data=test_setup_info, value='Test Parameters')
                        if self.robot_test and not self.do_bandsteering:
                            def add_frames_graphs_to_report(current_cord, current_angle, curr_yt_obj=curr_yt_obj):
                                """
                                    Reads all CSV files in the current directory that start with '<current_cord>_',
                                    filters rows up to current_angle, and collects stats:
                                    - Instance Name
                                    - Max Total Frames
                                    - Max Dropped Frames
                                    - Viewport
                                    - Current Resolution
                                    - Optimal Resolution
                                    - Max Buffer Health
                                    - Min Buffer Health
                                """
                                prefix = f"{current_cord}_"
                                target_folder = os.path.join(os.getcwd(), "..", "real_application_tests", "youtube", curr_yt_obj.report_path_date_time)
                                all_csv_files = glob.glob(os.path.join(target_folder, "*.csv"))
                                filtered_csv_files = [
                                    f for f in all_csv_files
                                    if os.path.basename(f).startswith(prefix)
                                ]

                                if not filtered_csv_files:
                                    logging.info(f"No CSV files found starting with '{prefix}'.")
                                    return {}

                                result_dict = {}

                                for csv_file in filtered_csv_files:
                                    try:
                                        df = pd.read_csv(csv_file)

                                        # Ensure necessary columns exist
                                        required_cols = {
                                            "Angle", "Instance Name", "TotalFrames", "DroppedFrames",
                                            "Viewport", "CurrentRes", "OptimalRes", "BufferHealth"
                                        }
                                        missing = required_cols - set(df.columns)
                                        if missing:
                                            logging.info(f"Skipping {csv_file}: missing columns {missing}")
                                            continue

                                        df["Angle"] = pd.to_numeric(df["Angle"], errors="coerce")
                                        if current_angle == "NA":
                                            df_filtered = df
                                        else:
                                            df_filtered = df[df["Angle"] == float(current_angle)]

                                        if df_filtered.empty:
                                            logging.info(f"No data <= {current_angle}° in {csv_file}.")
                                            continue

                                        # Extract values
                                        instance_name = df_filtered["Instance Name"].iloc[0]
                                        viewport = df_filtered["Viewport"].iloc[-1]                # latest viewport seen
                                        current_res = df_filtered["CurrentRes"].iloc[-1]          # latest current resolution
                                        optimal_res = df_filtered["OptimalRes"].iloc[-1]          # latest optimal resolution
                                        max_total_frames = df_filtered["TotalFrames"].max()
                                        max_dropped_frames = df_filtered["DroppedFrames"].max()
                                        max_buffer_health = df_filtered["BufferHealth"].max()
                                        min_buffer_health = df_filtered["BufferHealth"].min()

                                        # Store stats in dictionary
                                        result_dict[instance_name] = {
                                            "Viewport": viewport,
                                            "Current Resolution": current_res,
                                            "Optimal Resolution": optimal_res,
                                            "Total Frames": int(max_total_frames),
                                            "Dropped Frames": int(max_dropped_frames),
                                            "Max Buffer Health": round(float(max_buffer_health), 2),
                                            "Min Buffer Health": round(float(min_buffer_health), 2),
                                        }
                                        logging.info(f"Processed {csv_file}: {instance_name}")

                                    except Exception as e:
                                        logging.info(f"Error reading {csv_file}: {e}")

                                # graph of frames dropped
                                if current_angle == "NA":
                                    self.overall_report.set_graph_title(f"Total Frames vs Dropped Frames at coordinate: {current_cord}")
                                else:
                                    self.overall_report.set_graph_title(f"Total Frames vs Dropped Frames at coordinate: {current_cord} and angle: {current_angle}°")
                                self.overall_report.build_graph_title()
                                x_fig_size = 25
                                y_fig_size = len(result_dict) * .5 + 4

                                hostnames = list(result_dict.keys())
                                total_frames_list = [result_dict[host]["Total Frames"] for host in hostnames]
                                dropped_frames_list = [result_dict[host]["Dropped Frames"] for host in hostnames]
                                viewport_list = [result_dict[host]["Viewport"] for host in hostnames]
                                current_res_list = [result_dict[host]["Current Resolution"] for host in hostnames]
                                max_buffer_health_list = [result_dict[host]["Max Buffer Health"] for host in hostnames]
                                min_buffer_health_list = [result_dict[host]["Min Buffer Health"] for host in hostnames]

                                graph = lf_bar_graph_horizontal(_data_set=[dropped_frames_list, total_frames_list],
                                                                _xaxis_name="No of Frames",
                                                                _yaxis_name="Devices",
                                                                _yaxis_categories=hostnames,
                                                                _graph_image_name=f"Dropped Frames vs Total Frames_{current_cord}_{current_angle}",
                                                                _label=["dropped Frames", "Total Frames"],
                                                                _color=None,
                                                                _color_edge='red',
                                                                _figsize=(x_fig_size, y_fig_size),
                                                                _show_bar_value=True,
                                                                _text_font=6,
                                                                _text_rotation=True,
                                                                _enable_csv=True,
                                                                _legend_loc="upper right",
                                                                _legend_box=(1.1, 1),
                                                                )
                                graph_image = graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                # self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_table_title(f'Test Results for coordinate: {current_cord} and angle: {current_angle}°')
                                self.overall_report.build_table_title()

                                test_results = {
                                    "Hostname": hostnames,
                                    "ViewPort": viewport_list,
                                    "Video Resoultion": current_res_list,
                                    "Max Buffer Health (Seconds)": max_buffer_health_list,
                                    "Min Buffer health (Seconds)": min_buffer_health_list,
                                    "Total Frames": total_frames_list,
                                    "Dropped Frames": dropped_frames_list,

                                }

                                test_results_df = pd.DataFrame(test_results)
                                self.overall_report.set_table_dataframe(test_results_df)
                                self.overall_report.build_table()

                                logging.info("\n📊 Summary for all devices:")
                                for k, v in result_dict.items():
                                    logging.info(f"{k}: {v}")

                            logging.info(f"Directory: {os.getcwd()}, YouTube report path: {self.yt_obj_dict[ce][obj_name]['obj'].report_path_date_time}")
                            os.chdir(self.report_path_date_time)
                            for coordinate in self.coordinate_list:
                                if self.rotation_enabled:
                                    for angle in self.rotation_list:
                                        add_frames_graphs_to_report(coordinate, angle)
                                else:
                                    add_frames_graphs_to_report(coordinate, "NA")
                            for hostname in curr_yt_obj.real_sta_hostname:
                                # target_folder = curr_yt_obj.report_path_date_time
                                target_folder = os.path.join(os.getcwd(), "..", "real_application_tests", "youtube", curr_yt_obj.report_path_date_time)
                                all_csv_files = glob.glob(os.path.join(target_folder, "*.csv"))
                                filtered_csv_files = [f for f in all_csv_files if f.endswith(f"{hostname}_youtube_stats_report.csv")]

                                if not filtered_csv_files:
                                    logging.warning(f"No CSV files found for hostname: {hostname}")
                                    return
                                logging.info(f"Filtered CSV files for {hostname}: {filtered_csv_files}")
                                combined_data = pd.DataFrame()
                                for coord in self.coordinate_list:
                                    for file_path in filtered_csv_files:
                                        file_name = os.path.basename(file_path)
                                        if file_name.startswith(f"{coord}_"):
                                            try:
                                                df = pd.read_csv(file_path)
                                                df["SourceFile"] = file_name  # Track which file it came from
                                                combined_data = pd.concat([combined_data, df], ignore_index=True)
                                            except Exception as e:
                                                logging.error(f"Error reading {file_name}: {e}")
                                                continue

                                # Convert timestamps
                                try:
                                    logging.debug(f"Combined data columns before timestamp conversion: {combined_data.columns}")
                                    combined_data['TimeStamp'] = pd.to_datetime(combined_data['TimeStamp'], format="%H:%M:%S").dt.time
                                except Exception as e:
                                    logging.error(f"Error converting timestamps: {e}")
                                    return

                                combined_data = combined_data.drop_duplicates(subset='TimeStamp', keep='first')

                                # Extract plotting data
                                timestamps = combined_data['TimeStamp'].apply(lambda t: t.strftime('%H:%M:%S'))
                                buffer_health = combined_data['BufferHealth']

                                # Plot all combined data
                                fig, ax = plt.subplots(figsize=(20, 10))
                                plt.plot(timestamps, buffer_health, color='blue', linewidth=2)

                                plt.xlabel('Time', fontweight='bold', fontsize=15)
                                plt.ylabel('Buffer Health', fontweight='bold', fontsize=15)
                                plt.title(f'Buffer Health vs Time Graph for {hostname}', fontsize=18)

                                # Manage x-ticks for readability
                                if len(timestamps) > 30:
                                    tick_interval = len(timestamps) // 30
                                    selected_ticks = timestamps[::tick_interval]
                                    ax.set_xticks(selected_ticks)
                                else:
                                    ax.set_xticks(timestamps)

                                plt.xticks(rotation=45, ha='right')
                                plt.tight_layout()

                                output_file = f"{hostname}_combined_buffer_health_vs_time.png"
                                plt.savefig(output_file, dpi=96)
                                plt.close()

                                logging.info(f"Combined graph saved for {hostname}: {output_file}")

                                # Add to report
                                self.overall_report.set_graph_title(f'Buffer Health vs Time Graph for {hostname}')
                                self.overall_report.build_graph_title()
                                logging.info(f"Buffer health graph path: {output_file}, exists: {os.path.exists(output_file)}")
                                self.overall_report.set_graph_image(output_file)
                                self.overall_report.build_graph()
                            if self.dowebgui:
                                url_image_path = os.path.join(self.yt_obj_dict[ce][obj_name]['obj'].ui_report_dir, "live_view_images", f"yt_{self.yt_obj_dict[ce][obj_name]['obj'].test_name}_1.png")
                                timeout = 60  # seconds
                                start_time = time.time()

                                while not os.path.exists(url_image_path):
                                    if time.time() - start_time > timeout:
                                        logging.info("Timeout: Images not found within 60 seconds.")
                                        break
                                    time.sleep(1)
                                if os.path.exists(url_image_path):
                                    # Combine the HTML into a single string
                                    html_content = (
                                        '<div style="page-break-before: always;"></div>'
                                        f'<img src="file://{url_image_path}" style="width:1200px; height:800px;"></img>'
                                    )
                                    self.overall_report.set_custom_html(html_content)
                            self.overall_report.build_custom()
                            self.overall_report.write_html()
                            self.overall_report.write_pdf()
                            original_dir = os.getcwd()
                        else:

                            viewport_list = []
                            current_res_list = []
                            optimal_res_list = []

                            dropped_frames_list = []
                            total_frames_list = []
                            max_buffer_health_list = []
                            min_buffer_health_list = []

                            for hostname in curr_yt_obj.real_sta_hostname:
                                if hostname in curr_yt_obj.mydatajson:
                                    stats = curr_yt_obj.mydatajson[hostname]
                                    viewport_list.append(stats.get("Viewport", ""))
                                    current_res_list.append(stats.get("CurrentRes", ""))
                                    optimal_res_list.append(stats.get("OptimalRes", ""))

                                    dropped_frames = stats.get("DroppedFrames", "0")
                                    total_frames = stats.get("TotalFrames", "0")
                                    max_buffer_health = stats.get("maxbufferhealth", "0,0")
                                    min_buffer_health = stats.get("minbufferhealth", "0.0")
                                    try:
                                        dropped_frames_list.append(int(dropped_frames))
                                    except ValueError:
                                        dropped_frames_list.append(0)

                                    try:
                                        total_frames_list.append(int(total_frames))
                                    except ValueError:
                                        total_frames_list.append(0)
                                    try:
                                        max_buffer_health_list.append(float(max_buffer_health))
                                    except ValueError:
                                        max_buffer_health_list.append(0.0)

                                    try:
                                        min_buffer_health_list.append(float(min_buffer_health))
                                    except ValueError:
                                        min_buffer_health_list.append(0.0)

                                else:
                                    viewport_list.append("NA")
                                    current_res_list.append("NA")
                                    optimal_res_list.append("NA")
                                    dropped_frames_list.append(0)
                                    total_frames_list.append(0)
                                    max_buffer_health_list.append(0.0)
                                    min_buffer_health_list.append(0.0)

                            # graph of frames dropped
                            self.overall_report.set_graph_title("Total Frames vs Frames dropped")
                            self.overall_report.build_graph_title()
                            x_fig_size = 25
                            y_fig_size = len(curr_yt_obj.device_names) * .5 + 4

                            graph = lf_bar_graph_horizontal(_data_set=[dropped_frames_list, total_frames_list],
                                                            _xaxis_name="No of Frames",
                                                            _yaxis_name="Devices",
                                                            _yaxis_categories=curr_yt_obj.real_sta_hostname,
                                                            _graph_image_name=f"Dropped Frames vs Total Frames{obj_no}",
                                                            _label=["dropped Frames", "Total Frames"],
                                                            _color=None,
                                                            _color_edge='red',
                                                            _figsize=(x_fig_size, y_fig_size),
                                                            _show_bar_value=True,
                                                            _text_font=6,
                                                            _text_rotation=True,
                                                            _enable_csv=True,
                                                            _legend_loc="upper right",
                                                            _legend_box=(1.1, 1),
                                                            )
                            graph_image = graph.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_table_title('Test Results')
                            self.overall_report.build_table_title()

                            test_results = {
                                "Hostname": curr_yt_obj.real_sta_hostname,
                                "OS Type": curr_yt_obj.real_sta_os_types,
                                "MAC": curr_yt_obj.mac_list,
                                "RSSI": curr_yt_obj.rssi_list,
                                "Link Rate": curr_yt_obj.link_rate_list,
                                "ViewPort": viewport_list,
                                "SSID": curr_yt_obj.ssid_list,
                                "Video Resoultion": current_res_list,
                                "Max Buffer Health (Seconds)": max_buffer_health_list,
                                "Min Buffer health (Seconds)": min_buffer_health_list,
                                "Total Frames": total_frames_list,
                                "Dropped Frames": dropped_frames_list,


                            }

                            test_results_df = pd.DataFrame(test_results)
                            self.overall_report.set_table_dataframe(test_results_df)
                            self.overall_report.build_table()

                            original_dir = os.getcwd()

                            if curr_yt_obj.do_webUI:
                                csv_files = [f for f in os.listdir(curr_yt_obj.report_path_date_time) if f.endswith('.csv')]
                                os.chdir(curr_yt_obj.report_path_date_time)
                            else:
                                csv_files = [f for f in os.listdir(curr_yt_obj.report_path_date_time) if f.endswith('.csv')]
                                os.chdir(curr_yt_obj.report_path_date_time)
                            scp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.report_path_date_time)
                            for file_name in csv_files:
                                data = pd.read_csv(file_name)
                                self.overall_report.set_graph_title('Buffer Health vs Time Graph for {}'.format(file_name.split('_')[0]))
                                self.overall_report.build_graph_title()

                                try:
                                    data['TimeStamp'] = pd.to_datetime(data['TimeStamp'], format="%H:%M:%S").dt.time
                                except Exception as e:
                                    logging.error(f"Error in timestamp conversion for {file_name}: {e}")
                                    continue

                                data = data.drop_duplicates(subset='TimeStamp', keep='first')

                                data = data.sort_values(by='TimeStamp')

                                timestamps = data['TimeStamp'].apply(lambda t: t.strftime('%H:%M:%S'))
                                buffer_health = data['BufferHealth']

                                fig, ax = plt.subplots(figsize=(20, 10))
                                plt.plot(timestamps, buffer_health, color='blue', linewidth=2)

                                # Customize the plot
                                plt.xlabel('Time', fontweight='bold', fontsize=15)
                                plt.ylabel('Buffer Health', fontweight='bold', fontsize=15)
                                plt.title('Buffer Health vs Time Graph for {}'.format(file_name.split('_')[0]), fontsize=18)

                                if len(timestamps) > 30:
                                    tick_interval = len(timestamps) // 30
                                    selected_ticks = timestamps[::tick_interval]
                                    ax.set_xticks(selected_ticks)
                                else:
                                    ax.set_xticks(timestamps)

                                plt.xticks(rotation=45, ha='right')

                                output_file = os.path.join(scp_path, f"{file_name.split('_')[0]}buffer_health_vs_time{obj_no}.png")
                                plt.tight_layout()
                                plt.savefig(output_file, dpi=96)
                                plt.close()
                                abs_path = os.path.abspath(output_file)
                                logging.info(f"Graph saved PATH {file_name}: {abs_path}")

                                logging.info(f"Graph saved for {file_name}: {output_file}")

                                self.overall_report.set_graph_image(output_file)

                                self.overall_report.build_graph()

                        os.chdir(original_dir)
                        yt_obj = curr_yt_obj
                        if self.do_bandsteering:
                            yt_obj.add_bandsteering_report_section(report=self.overall_report)

                        if ce == "series":
                            obj_no += 1
                            obj_name = f"yt_test_{obj_no}"
                        else:
                            break

                elif test_name == "zoom_test":
                    '''
                    Zoom Test Reporting Block
                    -------------------------
                    Processes results for Zoom testing scenarios.
                    Constructs parameter tables, metrics graphs (audio/video, latency, jitter, loss),
                    and integrates band steering analysis if configured.
                    '''
                    obj_no = 1
                    obj_name = "zoom_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.zoom_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'ZOOM Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()
                        testtype = ""
                        curr_zoom_obj = copy.copy(self.zoom_obj_dict[ce][obj_name]["obj"])
                        if curr_zoom_obj.audio and curr_zoom_obj.video:
                            testtype = "AUDIO & VIDEO"
                        elif curr_zoom_obj.audio:
                            testtype = "AUDIO"
                        elif curr_zoom_obj.video:
                            testtype = "VIDEO"

                        if curr_zoom_obj.config:
                            test_parameters = pd.DataFrame([{
                                "Configured Devices": curr_zoom_obj.hostname_os_combination,
                                'No of Clients': f'W({curr_zoom_obj.windows}),L({curr_zoom_obj.linux}),M({curr_zoom_obj.mac})',
                                'Test Duration(min)': curr_zoom_obj.duration,
                                'EMAIL ID': curr_zoom_obj.signin_email,
                                "PASSWORD": curr_zoom_obj.signin_passwd,
                                "HOST": curr_zoom_obj.real_sta_list[0],
                                "TEST TYPE": testtype,
                                "SSID": curr_zoom_obj.ssid,
                                "Security": curr_zoom_obj.security

                            }])
                        elif len(curr_zoom_obj.selected_groups) > 0 and len(curr_zoom_obj.selected_profiles) > 0:
                            # Map each group with a profile
                            gp_pairs = zip(curr_zoom_obj.selected_groups, curr_zoom_obj.selected_profiles)

                            # Create a string by joining the mapped pairs
                            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

                            test_parameters = pd.DataFrame([{
                                "Configuration": gp_map,
                                "Configured Devices": curr_zoom_obj.hostname_os_combination,
                                'No of Clients': f'W({curr_zoom_obj.windows}),L({curr_zoom_obj.linux}),M({curr_zoom_obj.mac})',
                                'Test Duration(min)': curr_zoom_obj.duration,
                                'EMAIL ID': curr_zoom_obj.signin_email,
                                "PASSWORD": curr_zoom_obj.signin_passwd,
                                "HOST": curr_zoom_obj.real_sta_list[0],
                                "TEST TYPE": testtype,

                            }])
                        else:

                            test_parameters = pd.DataFrame([{
                                "Configured Devices": curr_zoom_obj.hostname_os_combination,
                                'No of Clients': f'W({curr_zoom_obj.windows}),L({curr_zoom_obj.linux}),M({curr_zoom_obj.mac})',
                                'Test Duration(min)': curr_zoom_obj.duration,
                                'EMAIL ID': curr_zoom_obj.signin_email,
                                "PASSWORD": curr_zoom_obj.signin_passwd,
                                "HOST": curr_zoom_obj.real_sta_list[0],
                                "TEST TYPE": testtype,

                            }])

                        test_parameters = pd.DataFrame([{

                            'No of Clients': f'W({curr_zoom_obj.windows}),L({curr_zoom_obj.linux}),M({curr_zoom_obj.mac})',
                            'Test Duration(min)': curr_zoom_obj.duration,
                            'EMAIL ID': curr_zoom_obj.signin_email,
                            "PASSWORD": curr_zoom_obj.signin_passwd,
                            "HOST": curr_zoom_obj.real_sta_list[0],
                            "TEST TYPE": testtype

                        }])
                        self.overall_report.set_table_dataframe(test_parameters)
                        self.overall_report.build_table()
                        if self.robot_test and self.dowebgui and not self.do_bandsteering:
                            curr_zoom_obj.report = self.overall_report
                            curr_zoom_obj.add_live_view_images_to_report()
                        if not self.robot_test or self.do_bandsteering:
                            client_array = []
                            accepted_clients = []
                            no_csv_client = []
                            rejected_clients = []
                            final_dataset = []
                            accepted_ostypes = []
                            max_audio_jitter_s, min_audio_jitter_s = [], []
                            max_audio_jitter_r, min_audio_jitter_r = [], []
                            max_audio_latency_s, min_audio_latency_s = [], []
                            max_audio_latency_r, min_audio_latency_r = [], []
                            max_audio_pktloss_s, min_audio_pktloss_s = [], []
                            max_audio_pktloss_r, min_audio_pktloss_r = [], []

                            max_video_jitter_s, min_video_jitter_s = [], []
                            max_video_jitter_r, min_video_jitter_r = [], []
                            max_video_latency_s, min_video_latency_s = [], []
                            max_video_latency_r, min_video_latency_r = [], []
                            max_video_pktloss_s, min_video_pktloss_s = [], []
                            max_video_pktloss_r, min_video_pktloss_r = [], []
                            for i in range(0, len(curr_zoom_obj.device_names)):
                                temp_max_audio_jitter_s, temp_min_audio_jitter_s = 0.0, 0.0
                                temp_max_audio_jitter_r, temp_min_audio_jitter_r = 0.0, 0.0
                                temp_max_audio_latency_s, temp_min_audio_latency_s = 0.0, 0.0
                                temp_max_audio_latency_r, temp_min_audio_latency_r = 0.0, 0.0
                                temp_max_audio_pktloss_s, temp_min_audio_pktloss_s = 0.0, 0.0
                                temp_max_audio_pktloss_r, temp_min_audio_pktloss_r = 0.0, 0.0

                                temp_max_video_jitter_s, temp_min_video_jitter_s = 0.0, 0.0
                                temp_max_video_jitter_r, temp_min_video_jitter_r = 0.0, 0.0
                                temp_max_video_latency_s, temp_min_video_latency_s = 0.0, 0.0
                                temp_max_video_latency_r, temp_min_video_latency_r = 0.0, 0.0
                                temp_max_video_pktloss_s, temp_min_video_pktloss_s = 0.0, 0.0
                                temp_max_video_pktloss_r, temp_min_video_pktloss_r = 0.0, 0.0
                                per_client_data = {
                                    "audio_jitter_s": [],
                                    "audio_jitter_r": [],
                                    "audio_latency_s": [],
                                    "audio_latency_r": [],
                                    "audio_pktloss_s": [],
                                    "audio_pktloss_r": [],
                                    "video_jitter_s": [],
                                    "video_jitter_r": [],
                                    "video_latency_s": [],
                                    "video_latency_r": [],
                                    "video_pktloss_s": [],
                                    "video_pktloss_r": [],
                                }
                                try:
                                    if not self.do_bandsteering:
                                        if self.dowebgui:
                                            file_path = os.path.join(curr_zoom_obj.report.path_date_time, f'{curr_zoom_obj.device_names[i]}.csv')
                                        else:
                                            file_path = os.path.join(curr_zoom_obj.report.path_date_time, f'{curr_zoom_obj.device_names[i]}.csv')
                                        if not os.path.exists(file_path):
                                            logger.error(
                                                f'File not found for client {curr_zoom_obj.device_names[i]}: {file_path}'
                                            )
                                            continue
                                        with open(
                                            file_path, mode="r", encoding="utf-8", errors="ignore"
                                        ) as file:
                                            csv_reader = csv.DictReader(file)
                                            for row in csv_reader:

                                                per_client_data["audio_jitter_s"].append(
                                                    float(row["Sent Audio Jitter (ms)"])
                                                )
                                                per_client_data["audio_jitter_r"].append(
                                                    float(row["Receive Audio Jitter (ms)"])
                                                )
                                                per_client_data["audio_latency_s"].append(
                                                    float(row["Sent Audio Latency (ms)"])
                                                )
                                                per_client_data["audio_latency_r"].append(
                                                    float(row["Receive Audio Latency (ms)"])
                                                )
                                                per_client_data["audio_pktloss_s"].append(
                                                    float(
                                                        (row["Sent Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                )
                                                per_client_data["audio_pktloss_r"].append(
                                                    float(
                                                        (row["Receive Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                )
                                                per_client_data["video_jitter_s"].append(
                                                    float(row["Sent Video Jitter (ms)"])
                                                )
                                                per_client_data["video_jitter_r"].append(
                                                    float(row["Receive Video Jitter (ms)"])
                                                )
                                                per_client_data["video_latency_s"].append(
                                                    float(row["Sent Video Latency (ms)"])
                                                )
                                                per_client_data["video_latency_r"].append(
                                                    float(row["Receive Video Latency (ms)"])
                                                )
                                                per_client_data["video_pktloss_s"].append(
                                                    float(
                                                        (row["Sent Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                )
                                                per_client_data["video_pktloss_r"].append(
                                                    float(
                                                        (row["Receive Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                )

                                                temp_max_audio_jitter_s = max(
                                                    temp_max_audio_jitter_s,
                                                    float(row["Sent Audio Jitter (ms)"]),
                                                )
                                                temp_max_audio_jitter_r = max(
                                                    temp_max_audio_jitter_r,
                                                    float(row["Receive Audio Jitter (ms)"]),
                                                )
                                                temp_max_audio_latency_s = max(
                                                    temp_max_audio_latency_s,
                                                    float(row["Sent Audio Latency (ms)"]),
                                                )
                                                temp_max_audio_latency_r = max(
                                                    temp_max_audio_latency_r,
                                                    float(row["Receive Audio Latency (ms)"]),
                                                )
                                                temp_max_audio_pktloss_s = max(
                                                    temp_max_audio_pktloss_s,
                                                    float(
                                                        (row["Sent Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    ),
                                                )
                                                temp_max_audio_pktloss_r = max(
                                                    temp_max_audio_pktloss_r,
                                                    float(
                                                        (row["Receive Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    ),
                                                )

                                                temp_max_video_jitter_s = max(
                                                    temp_max_video_jitter_s,
                                                    float(row["Sent Video Jitter (ms)"]),
                                                )
                                                temp_max_video_jitter_r = max(
                                                    temp_max_video_jitter_r,
                                                    float(row["Receive Video Jitter (ms)"]),
                                                )
                                                temp_max_video_latency_s = max(
                                                    temp_max_video_latency_s,
                                                    float(row["Sent Video Latency (ms)"]),
                                                )
                                                temp_max_video_latency_r = max(
                                                    temp_max_video_latency_r,
                                                    float(row["Receive Video Latency (ms)"]),
                                                )
                                                temp_max_video_pktloss_s = max(
                                                    temp_max_video_pktloss_s,
                                                    float(
                                                        (row["Sent Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    ),
                                                )
                                                temp_max_video_pktloss_r = max(
                                                    temp_max_video_pktloss_r,
                                                    float(
                                                        (row["Receive Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    ),
                                                )

                                                temp_min_audio_jitter_s = (
                                                    min(
                                                        temp_min_audio_jitter_s,
                                                        float(row["Sent Audio Jitter (ms)"]),
                                                    )
                                                    if temp_min_audio_jitter_s > 0
                                                    and float(row["Sent Audio Jitter (ms)"]) > 0
                                                    else (
                                                        float(row["Sent Audio Jitter (ms)"])
                                                        if float(row["Sent Audio Jitter (ms)"]) > 0
                                                        else temp_min_audio_jitter_s
                                                    )
                                                )
                                                temp_min_audio_jitter_r = (
                                                    min(
                                                        temp_min_audio_jitter_r,
                                                        float(row["Receive Audio Jitter (ms)"]),
                                                    )
                                                    if temp_min_audio_jitter_r > 0
                                                    and float(row["Receive Audio Jitter (ms)"]) > 0
                                                    else (
                                                        float(row["Receive Audio Jitter (ms)"])
                                                        if float(row["Receive Audio Jitter (ms)"]) > 0
                                                        else temp_min_audio_jitter_r
                                                    )
                                                )
                                                temp_min_audio_latency_s = (
                                                    min(
                                                        temp_min_audio_latency_s,
                                                        float(row["Sent Audio Latency (ms)"]),
                                                    )
                                                    if temp_min_audio_latency_s > 0
                                                    and float(row["Sent Audio Latency (ms)"]) > 0
                                                    else (
                                                        float(row["Sent Audio Latency (ms)"])
                                                        if float(row["Sent Audio Latency (ms)"]) > 0
                                                        else temp_min_audio_jitter_s
                                                    )
                                                )
                                                temp_min_audio_latency_r = (
                                                    min(
                                                        temp_min_audio_latency_r,
                                                        float(row["Receive Audio Latency (ms)"]),
                                                    )
                                                    if temp_min_audio_latency_r > 0
                                                    and float(row["Receive Audio Latency (ms)"]) > 0
                                                    else (
                                                        float(row["Receive Audio Latency (ms)"])
                                                        if float(row["Receive Audio Latency (ms)"]) > 0
                                                        else temp_min_audio_jitter_r
                                                    )
                                                )

                                                temp_min_audio_pktloss_s = (
                                                    min(
                                                        temp_min_audio_pktloss_s,
                                                        float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        ),
                                                    )
                                                    if temp_min_audio_pktloss_s > 0
                                                    and float(
                                                        (row["Sent Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                    > 0
                                                    else (
                                                        float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        if float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        > 0
                                                        else temp_min_audio_pktloss_s
                                                    )
                                                )
                                                temp_min_audio_pktloss_r = (
                                                    min(
                                                        temp_min_audio_pktloss_r,
                                                        float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        ),
                                                    )
                                                    if temp_min_audio_pktloss_r > 0
                                                    and float(
                                                        (row["Sent Audio Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                    > 0
                                                    else (
                                                        float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        if float(
                                                            (row["Sent Audio Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        > 0
                                                        else temp_min_audio_pktloss_r
                                                    )
                                                )

                                                temp_min_video_jitter_s = (
                                                    min(
                                                        temp_min_video_jitter_s,
                                                        float(row["Sent Video Jitter (ms)"]),
                                                    )
                                                    if temp_min_video_jitter_s > 0
                                                    and float(row["Sent Video Jitter (ms)"]) > 0
                                                    else (
                                                        float(row["Sent Video Jitter (ms)"])
                                                        if float(row["Sent Video Jitter (ms)"]) > 0
                                                        else temp_min_video_jitter_s
                                                    )
                                                )
                                                temp_min_video_jitter_r = (
                                                    min(
                                                        temp_min_video_jitter_r,
                                                        float(row["Receive Video Jitter (ms)"]),
                                                    )
                                                    if temp_min_video_jitter_r > 0
                                                    and float(row["Receive Video Jitter (ms)"]) > 0
                                                    else (
                                                        float(row["Receive Video Jitter (ms)"])
                                                        if float(row["Receive Video Jitter (ms)"]) > 0
                                                        else temp_min_video_jitter_r
                                                    )
                                                )
                                                temp_min_video_latency_s = (
                                                    min(
                                                        temp_min_video_latency_s,
                                                        float(row["Sent Video Latency (ms)"]),
                                                    )
                                                    if temp_min_video_latency_s > 0
                                                    and float(row["Sent Video Latency (ms)"]) > 0
                                                    else (
                                                        float(row["Sent Video Latency (ms)"])
                                                        if float(row["Sent Video Latency (ms)"]) > 0
                                                        else temp_min_video_latency_s
                                                    )
                                                )
                                                temp_min_video_latency_r = (
                                                    min(
                                                        temp_min_video_latency_r,
                                                        float(row["Receive Video Latency (ms)"]),
                                                    )
                                                    if temp_min_video_latency_r > 0
                                                    and float(row["Receive Video Latency (ms)"]) > 0
                                                    else (
                                                        float(row["Receive Video Latency (ms)"])
                                                        if float(row["Receive Video Latency (ms)"]) > 0
                                                        else temp_min_video_latency_r
                                                    )
                                                )

                                                temp_min_video_pktloss_s = (
                                                    min(
                                                        temp_min_video_pktloss_s,
                                                        float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        ),
                                                    )
                                                    if temp_min_video_pktloss_s > 0
                                                    and float(
                                                        (row["Sent Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                    > 0
                                                    else (
                                                        float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        if float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        > 0
                                                        else temp_min_video_pktloss_s
                                                    )
                                                )
                                                temp_min_video_pktloss_r = (
                                                    min(
                                                        temp_min_video_pktloss_r,
                                                        float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        ),
                                                    )
                                                    if temp_min_video_pktloss_r > 0
                                                    and float(
                                                        (row["Sent Video Packet loss (%)"])
                                                        .split(" ")[0]
                                                        .replace("%", "")
                                                    )
                                                    > 0
                                                    else (
                                                        float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        if float(
                                                            (row["Sent Video Packet loss (%)"])
                                                            .split(" ")[0]
                                                            .replace("%", "")
                                                        )
                                                        > 0
                                                        else temp_min_video_pktloss_r
                                                    )
                                                )

                                    elif self.do_bandsteering:
                                        if not self.dowebgui:
                                            file_path = os.path.join(
                                                curr_zoom_obj.report.path_date_time,
                                                f'{curr_zoom_obj.device_names[i]}.csv'
                                            )
                                        else:
                                            file_path = os.path.join(
                                                curr_zoom_obj.report.path_date_time,
                                                f'{curr_zoom_obj.device_names[i]}.csv'
                                            )
                                        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as file:
                                            csv_reader = csv.DictReader(file)

                                            for row in csv_reader:

                                                ai_jit = float(row["audio_input_jitter_avg"] or 0)
                                                ao_jit = float(row["audio_output_jitter_avg"] or 0)

                                                ai_lat = float(row["audio_input_latency_avg"] or 0)
                                                ao_lat = float(row["audio_output_latency_avg"] or 0)

                                                ai_loss = float(row["audio_input_avg_loss_avg"] or 0)
                                                ao_loss = float(row["audio_output_avg_loss_avg"] or 0)

                                                vi_jit = float(row["video_input_jitter_avg"] or 0)
                                                vo_jit = float(row["video_output_jitter_avg"] or 0)

                                                vi_lat = float(row["video_input_latency_avg"] or 0)
                                                vo_lat = float(row["video_output_latency_avg"] or 0)

                                                vi_loss = float(row["video_input_avg_loss_avg"] or 0)
                                                vo_loss = float(row["video_output_avg_loss_avg"] or 0)

                                                per_client_data["audio_jitter_s"].append(ai_jit)
                                                per_client_data["audio_jitter_r"].append(ao_jit)

                                                per_client_data["audio_latency_s"].append(ai_lat)
                                                per_client_data["audio_latency_r"].append(ao_lat)

                                                per_client_data["audio_pktloss_s"].append(ai_loss)
                                                per_client_data["audio_pktloss_r"].append(ao_loss)

                                                per_client_data["video_jitter_s"].append(vi_jit)
                                                per_client_data["video_jitter_r"].append(vo_jit)

                                                per_client_data["video_latency_s"].append(vi_lat)
                                                per_client_data["video_latency_r"].append(vo_lat)

                                                per_client_data["video_pktloss_s"].append(vi_loss)
                                                per_client_data["video_pktloss_r"].append(vo_loss)

                                                temp_max_audio_jitter_s = max(temp_max_audio_jitter_s, ai_jit)
                                                temp_max_audio_jitter_r = max(temp_max_audio_jitter_r, ao_jit)

                                                temp_max_audio_latency_s = max(temp_max_audio_latency_s, ai_lat)
                                                temp_max_audio_latency_r = max(temp_max_audio_latency_r, ao_lat)

                                                temp_max_audio_pktloss_s = max(temp_max_audio_pktloss_s, ai_loss)
                                                temp_max_audio_pktloss_r = max(temp_max_audio_pktloss_r, ao_loss)

                                                temp_max_video_jitter_s = max(temp_max_video_jitter_s, vi_jit)
                                                temp_max_video_jitter_r = max(temp_max_video_jitter_r, vo_jit)

                                                temp_max_video_latency_s = max(temp_max_video_latency_s, vi_lat)
                                                temp_max_video_latency_r = max(temp_max_video_latency_r, vo_lat)

                                                temp_max_video_pktloss_s = max(temp_max_video_pktloss_s, vi_loss)
                                                temp_max_video_pktloss_r = max(temp_max_video_pktloss_r, vo_loss)

                                                if ai_jit > 0:
                                                    temp_min_audio_jitter_s = ai_jit if temp_min_audio_jitter_s == 0 else min(temp_min_audio_jitter_s, ai_jit)

                                                if ao_jit > 0:
                                                    temp_min_audio_jitter_r = ao_jit if temp_min_audio_jitter_r == 0 else min(temp_min_audio_jitter_r, ao_jit)

                                                if ai_lat > 0:
                                                    temp_min_audio_latency_s = ai_lat if temp_min_audio_latency_s == 0 else min(temp_min_audio_latency_s, ai_lat)

                                                if ao_lat > 0:
                                                    temp_min_audio_latency_r = ao_lat if temp_min_audio_latency_r == 0 else min(temp_min_audio_latency_r, ao_lat)

                                                if ai_loss > 0:
                                                    temp_min_audio_pktloss_s = ai_loss if temp_min_audio_pktloss_s == 0 else min(temp_min_audio_pktloss_s, ai_loss)

                                                if ao_loss > 0:
                                                    temp_min_audio_pktloss_r = ao_loss if temp_min_audio_pktloss_r == 0 else min(temp_min_audio_pktloss_r, ao_loss)

                                                if vi_jit > 0:
                                                    temp_min_video_jitter_s = vi_jit if temp_min_video_jitter_s == 0 else min(temp_min_video_jitter_s, vi_jit)

                                                if vo_jit > 0:
                                                    temp_min_video_jitter_r = vo_jit if temp_min_video_jitter_r == 0 else min(temp_min_video_jitter_r, vo_jit)

                                                if vi_lat > 0:
                                                    temp_min_video_latency_s = vi_lat if temp_min_video_latency_s == 0 else min(temp_min_video_latency_s, vi_lat)

                                                if vo_lat > 0:
                                                    temp_min_video_latency_r = vo_lat if temp_min_video_latency_r == 0 else min(temp_min_video_latency_r, vo_lat)

                                                if vi_loss > 0:
                                                    temp_min_video_pktloss_s = vi_loss if temp_min_video_pktloss_s == 0 else min(temp_min_video_pktloss_s, vi_loss)

                                                if vo_loss > 0:
                                                    temp_min_video_pktloss_r = vo_loss if temp_min_video_pktloss_r == 0 else min(temp_min_video_pktloss_r, vo_loss)

                                except Exception as e:
                                    logging.error(f"Error in reading data in client {self.zoom_obj_dict[ce][obj_name]['obj'].device_names[i]}", e)
                                    no_csv_client.append(curr_zoom_obj.device_names[i])
                                    rejected_clients.append(curr_zoom_obj.device_names[i])
                                if curr_zoom_obj.device_names[i] not in no_csv_client:
                                    client_array.append(curr_zoom_obj.device_names[i])
                                    accepted_clients.append(curr_zoom_obj.device_names[i])
                                    accepted_ostypes.append(curr_zoom_obj.real_sta_os_type[i])
                                    max_audio_jitter_s.append(temp_max_audio_jitter_s)
                                    min_audio_jitter_s.append(temp_min_audio_jitter_s)
                                    max_audio_jitter_r.append(temp_max_audio_jitter_r)
                                    min_audio_jitter_r.append(temp_min_audio_jitter_r)
                                    max_audio_latency_s.append(temp_max_audio_latency_s)
                                    min_audio_latency_s.append(temp_min_audio_latency_s)
                                    max_audio_latency_r.append(temp_max_audio_latency_r)
                                    min_audio_latency_r.append(temp_min_audio_latency_r)
                                    max_video_jitter_s.append(temp_max_video_jitter_s)
                                    min_video_jitter_s.append(temp_min_video_jitter_s)
                                    max_video_jitter_r.append(temp_max_video_jitter_r)
                                    min_video_jitter_r.append(temp_min_video_jitter_r)
                                    max_video_latency_s.append(temp_max_video_latency_s)
                                    min_video_latency_s.append(temp_min_video_latency_s)
                                    max_video_latency_r.append(temp_max_video_latency_r)
                                    min_video_latency_r.append(temp_min_video_latency_r)

                                    max_audio_pktloss_s.append(temp_max_audio_pktloss_s)
                                    min_audio_pktloss_s.append(temp_min_audio_pktloss_s)
                                    max_audio_pktloss_r.append(temp_max_audio_pktloss_r)
                                    min_audio_pktloss_r.append(temp_min_audio_pktloss_r)
                                    max_video_pktloss_s.append(temp_max_video_pktloss_s)
                                    min_video_pktloss_s.append(temp_min_video_pktloss_s)
                                    max_video_pktloss_r.append(temp_max_video_pktloss_r)
                                    min_video_pktloss_r.append(temp_min_video_pktloss_r)

                                    final_dataset.append(per_client_data.copy())

                            self.overall_report.set_table_title("Test Devices:")
                            self.overall_report.build_table_title()

                            device_details = pd.DataFrame({
                                'Hostname': curr_zoom_obj.real_sta_hostname,
                                'OS Type': curr_zoom_obj.real_sta_os_type,
                                "MAC": curr_zoom_obj.mac_list,
                                "RSSI": curr_zoom_obj.rssi_list,
                                "Link Rate": curr_zoom_obj.link_rate_list,
                                "SSID": curr_zoom_obj.ssid_list,

                            })
                            self.overall_report.set_table_dataframe(device_details)
                            self.overall_report.build_table()

                            if curr_zoom_obj.audio:
                                self.overall_report.set_graph_title("Audio Latency (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_audio_latency_s.copy(), min_audio_latency_s.copy(), max_audio_latency_r.copy(), min_audio_latency_r.copy()]
                                y_data_set = client_array

                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Latency (ms)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Audio Latency(sent/received)",
                                    _graph_image_name=f"Audio Latency(sent and received){obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_graph_title("Audio Jitter (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_audio_jitter_s.copy(), min_audio_jitter_s.copy(), max_audio_jitter_r.copy(), min_audio_jitter_r.copy()]
                                y_data_set = client_array

                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Jitter (ms)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Audio Jitter(sent/received)",
                                    _graph_image_name=f"Audio Jitter(sent and received) {obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_graph_title("Audio Packet Loss (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_audio_pktloss_s.copy(), min_audio_pktloss_s.copy(), max_audio_pktloss_r.copy(), min_audio_pktloss_r.copy()]
                                y_data_set = client_array

                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Packet Loss (%)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Audio Packet Loss(sent/received)",
                                    _graph_image_name=f"Audio Packet Loss(sent and received){obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_table_title("Test Audio Results Table:")
                                self.overall_report.build_table_title()
                                audio_test_results_dict = pd.DataFrame({
                                    'Device Name': [client for client in accepted_clients],
                                    'Avg Latency Sent (ms)': [
                                        round(sum(data["audio_latency_s"]) / len(data["audio_latency_s"]), 2) if len(data["audio_latency_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Latency Recv (ms)': [
                                        round(sum(data["audio_latency_r"]) / len(data["audio_latency_r"]), 2) if len(data["audio_latency_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Jitter Sent (ms)': [
                                        round(sum(data["audio_jitter_s"]) / len(data["audio_jitter_s"]), 2) if len(data["audio_jitter_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Jitter Recv (ms)': [
                                        round(sum(data["audio_jitter_r"]) / len(data["audio_jitter_r"]), 2) if len(data["audio_jitter_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Pkt Loss Sent': [
                                        round(sum(data["audio_pktloss_s"]) / len(data["audio_pktloss_s"]), 2) if len(data["audio_pktloss_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Pkt Loss Recv': [
                                        round(sum(data["audio_pktloss_r"]) / len(data["audio_pktloss_r"]), 2) if len(data["audio_pktloss_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'CSV link': [
                                        '<a href="{}.csv" target="_blank">csv data</a>'.format(client)
                                        for client in accepted_clients
                                    ]
                                })
                                self.overall_report.set_table_dataframe(audio_test_results_dict)
                                self.overall_report.dataframe_html = self.overall_report.dataframe.to_html(index=False,
                                                                                                           justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
                                self.overall_report.html += self.overall_report.dataframe_html
                            if curr_zoom_obj.video:
                                self.overall_report.set_graph_title("Video Latency (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_video_latency_s.copy(), min_video_latency_s.copy(), max_video_latency_r.copy(), min_video_latency_r.copy()]
                                y_data_set = client_array
                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Latency (ms)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Video Latency(sent/received)",
                                    _graph_image_name=f"Video Latency(sent and received){obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_graph_title("Video Jitter (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_video_jitter_s.copy(), min_video_jitter_s.copy(), max_video_jitter_r.copy(), min_video_jitter_r.copy()]
                                y_data_set = client_array
                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Jitter (ms)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Video Jitter(sent/received)",
                                    _graph_image_name=f"Video Jitter(sent and received){obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_graph_title("Video Packet Loss (Sent/Received)")
                                self.overall_report.build_graph_title()
                                x_data_set = [max_video_pktloss_s.copy(), min_video_pktloss_s.copy(), max_video_pktloss_r.copy(), min_video_pktloss_r.copy()]
                                y_data_set = client_array
                                x_fig_size = 18
                                y_fig_size = len(client_array) * 1 + 4
                                bar_graph_horizontal = lf_bar_graph_horizontal(
                                    _data_set=x_data_set,
                                    _xaxis_name="Packet Loss (%)",
                                    _yaxis_name="Devices",
                                    _yaxis_label=y_data_set,
                                    _yaxis_categories=y_data_set,
                                    _yaxis_step=1,
                                    _yticks_font=8,
                                    _bar_height=.20,
                                    _color_name=["yellow", "blue", "orange", "grey"],
                                    _show_bar_value=True,
                                    _figsize=(x_fig_size, y_fig_size),
                                    _graph_title="Video Packet Loss(sent/received)",
                                    _graph_image_name=f"Video Packet Loss(sent and received){obj_no}",
                                    _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                                )
                                graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_image)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_table_title("Test Video Results Table:")
                                self.overall_report.build_table_title()
                                video_test_results_dict = pd.DataFrame({
                                    'Device Name': [client for client in accepted_clients],
                                    'Avg Latency Sent (ms)': [
                                        round(sum(data["video_latency_s"]) / len(data["video_latency_s"]), 2) if len(data["video_latency_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Latency Recv (ms)': [
                                        round(sum(data["video_latency_r"]) / len(data["video_latency_r"]), 2) if len(data["video_latency_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Jitter Sent (ms)': [
                                        round(sum(data["video_jitter_s"]) / len(data["video_jitter_s"]), 2) if len(data["video_jitter_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Jitter Recv (ms)': [
                                        round(sum(data["video_jitter_r"]) / len(data["video_jitter_r"]), 2) if len(data["video_jitter_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Pkt Loss Sent': [
                                        round(sum(data["video_pktloss_s"]) / len(data["video_pktloss_s"]), 2) if len(data["video_pktloss_s"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'Avg Pkt Loss Recv': [
                                        round(sum(data["video_pktloss_r"]) / len(data["video_pktloss_r"]), 2) if len(data["video_pktloss_r"]) != 0 else 0
                                        for data in final_dataset
                                    ],
                                    'CSV link': [
                                        '<a href="{}.csv" target="_blank">csv data</a>'.format(client)
                                        for client in accepted_clients
                                    ]
                                })
                                self.overall_report.set_table_dataframe(video_test_results_dict)

                                self.overall_report.dataframe_html = self.overall_report.dataframe.to_html(index=False,
                                                                                                           justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
                                self.overall_report.html += self.overall_report.dataframe_html
                            self.overall_report.set_custom_html("<br/><hr/>")
                            self.overall_report.build_custom()
                            # band steering section
                            if self.do_bandsteering:

                                self.overall_report.set_table_title("Band Steering – BSSID Transition Analysis")
                                self.overall_report.build_table_title()

                                folder = curr_zoom_obj.report.path_date_time

                                for device in accepted_clients:

                                    file_path = os.path.join(folder, f"{device}.csv")

                                    if not os.path.exists(file_path):
                                        continue

                                    df = pd.read_csv(file_path)

                                    if df.empty or "bssid" not in df.columns:
                                        continue

                                    device_name = device

                                    df["bssid"] = df["bssid"].astype(str).str.strip().str.upper()
                                    df["prev_bssid"] = df["bssid"].shift()

                                    transition_rows = df[
                                        (df["bssid"] != df["prev_bssid"]) &
                                        (df["bssid"] != "") &
                                        (df["bssid"] != "NA")
                                    ]

                                    transitions = []
                                    bssid_counts = {}

                                    for _, row in transition_rows.iterrows():

                                        curr_bssid = row["bssid"]

                                        if curr_bssid not in bssid_counts:
                                            bssid_counts[curr_bssid] = 0

                                        bssid_counts[curr_bssid] += 1

                                        transitions.append({
                                            "BSSID": curr_bssid,
                                            "Timestamp": row.get("timestamp", "NA"),
                                            "From Coordinate": row.get("From_Coord", "NA"),
                                            "To Coordinate": row.get("To_Coord", "NA"),
                                            "Channel": row.get("channel", "NA"),
                                            "Signal": row.get("signal", "NA")
                                        })

                                    bssid_list = list(bssid_counts.keys())
                                    count_list = list(bssid_counts.values())

                                    if not bssid_list:
                                        bssid_list = ["No Transition"]
                                        count_list = [0]

                                    # BSSID transition graph
                                    self.overall_report.set_graph_title(
                                        f"BSSID Change Count - {device_name}"
                                    )
                                    self.overall_report.build_graph_title()

                                    graph = lf_bar_graph_horizontal(
                                        _data_set=[count_list],
                                        _xaxis_name="Transition Count",
                                        _yaxis_name="BSSID",
                                        _yaxis_label=bssid_list,
                                        _yaxis_categories=bssid_list,
                                        _bar_height=.25,
                                        _show_bar_value=True,
                                        _figsize=(18, max(4, len(bssid_list))),
                                        _graph_title="BSSID Transitions",
                                        _graph_image_name=f"{device_name}_bssid_transitions",
                                        _label=["Transitions"]
                                    )

                                    graph_image = graph.build_bar_graph_horizontal()

                                    self.overall_report.set_graph_image(graph_image)
                                    self.overall_report.move_graph_image()
                                    self.overall_report.build_graph()

                                    # Transition table
                                    self.overall_report.set_table_title(
                                        f"Band Steering Results for {device_name}"
                                    )
                                    self.overall_report.build_table_title()

                                    if not transitions:
                                        first_row = df.iloc[0]
                                        last_row = df.iloc[-1]

                                        transitions.append({
                                            "BSSID": first_row.get("bssid", "NA"),
                                            "Timestamp": last_row.get("timestamp", "NA"),
                                            "From Coordinate": first_row.get("From_Coord", "NA"),
                                            "To Coordinate": last_row.get("To_Coord", "NA"),
                                            "Channel": first_row.get("channel", "NA"),
                                            "Signal": first_row.get("signal", "NA")
                                        })

                                    transition_df = pd.DataFrame(transitions)

                                    self.overall_report.set_table_dataframe(transition_df)
                                    self.overall_report.build_table()
                        else:
                            def _build_metric_graph(media_type, metric_name, unit, data, input_key, output_key, suffix="", curr_zoom_obj=curr_zoom_obj):
                                """
                                Helper to build standard horizontal bar graphs with Device Names on Y-Axis.
                                suffix: used for Robo graphs to ensure unique image names per coordinate.
                                """
                                self.overall_report.set_graph_title(f"{media_type} {metric_name} (Sent/Received)")
                                self.overall_report.build_graph_title()

                                sent_vals = []
                                recv_vals = []

                                # Iterate directly through hostnames
                                for client in curr_zoom_obj.real_sta_hostname:
                                    # Use the hostname directly as the key to fetch data
                                    device_key = client

                                    # Safe Get
                                    def get_val(key):  # noqa: B023
                                        val = data.get(device_key, {}).get(key)  # noqa: B023
                                        return val if val is not None else 0

                                    sent_vals.append(get_val(output_key))
                                    recv_vals.append(get_val(input_key))

                                # Generate Graph
                                bar_graph = lf_bar_graph_horizontal(
                                    _data_set=[sent_vals, recv_vals],
                                    _xaxis_name=f"{metric_name} ({unit})",
                                    _yaxis_name="Devices",
                                    _yaxis_categories=curr_zoom_obj.real_sta_hostname,  # Device Names on Y-Axis
                                    _graph_title=f"{media_type} {metric_name}",
                                    _graph_image_name=f"{media_type}_{metric_name}{suffix}",
                                    _label=["Avg Sent", "Avg Recv"],
                                    _figsize=(18, len(curr_zoom_obj.real_sta_hostname) * 1 + 4),
                                    _color_name=["blue", "orange"],
                                )
                                self.overall_report.set_graph_image(bar_graph.build_bar_graph_horizontal())
                                self.overall_report.move_graph_image()
                                logging.debug(f"Report path date time: {self.overall_report.path_date_time}")
                                self.overall_report.build_graph()

                            def _build_results_table(data, media_type, curr_zoom_obj=curr_zoom_obj):
                                """Helper for Summary Table"""

                                def fmt_val(client, key):
                                    val = data.get(client, {}).get(key)  # noqa: B023
                                    return val if val is not None else 0

                                p = media_type

                                details = pd.DataFrame(
                                    {
                                        "Device Name": curr_zoom_obj.real_sta_hostname,
                                        # FIXED: Sent uses 'output', Received uses 'input'
                                        "Avg Bitrate (kbps) [S/R]": [
                                            f"{fmt_val(c, f'{p}_output_bitrate_avg')}/{fmt_val(c, f'{p}_input_bitrate_avg')}"
                                            for c in curr_zoom_obj.real_sta_hostname
                                        ],
                                        "Avg Latency (ms) [S/R]": [
                                            f"{fmt_val(c, f'{p}_output_latency_avg')}/{fmt_val(c, f'{p}_input_latency_avg')}"
                                            for c in curr_zoom_obj.real_sta_hostname
                                        ],
                                        "Avg Jitter (ms) [S/R]": [
                                            f"{fmt_val(c, f'{p}_output_jitter_avg')}/{fmt_val(c, f'{p}_input_jitter_avg')}"
                                            for c in curr_zoom_obj.real_sta_hostname
                                        ],
                                        "Avg Pkt Loss (%) [S/R]": [
                                            f"{fmt_val(c, f'{p}_output_avg_loss_avg')}/{fmt_val(c, f'{p}_input_avg_loss_avg')}"
                                            for c in curr_zoom_obj.real_sta_hostname
                                        ],
                                    }
                                )
                                self.overall_report.set_table_dataframe(details)
                                self.overall_report.dataframe_html = self.overall_report.dataframe.to_html(
                                    index=False, justify="center", render_links=True, escape=False
                                )
                                self.overall_report.html += self.overall_report.dataframe_html

                            coords = curr_zoom_obj.coordinates_list if curr_zoom_obj.coordinates_list else ["0,0,0"]

                            for coord in coords:
                                # Determine angles loop
                                if curr_zoom_obj.rotations_enabled and curr_zoom_obj.angles_list:
                                    angles_loop = curr_zoom_obj.angles_list
                                else:
                                    angles_loop = [curr_zoom_obj.current_angle]

                                for angle in angles_loop:
                                    # 1. Heading for this Location
                                    if curr_zoom_obj.rotations_enabled:
                                        heading = f"Audio and Video graphs at coordinate {coord} and angle {angle}"
                                    else:
                                        heading = f"Audio and Video graphs at coordinate {coord}"
                                    self.overall_report.set_table_title(heading)
                                    self.overall_report.build_table_title()

                                    # 2. Load Data
                                    json_pattern = f"*_{coord}_{angle}_qos.json"
                                    file_path = os.path.join("zoom_api_responses", json_pattern)
                                    file_path_1 = os.path.join(curr_zoom_obj.report.path_date_time, json_pattern)
                                    found_files = glob.glob(file_path_1)
                                    logging.debug(f"Checking found files: {found_files}")

                                    device_data = {}
                                    if found_files:
                                        try:
                                            with open(found_files[0], "r") as f:
                                                raw_data = json.load(f)
                                            # Parse data to get per-device averages
                                            device_data = curr_zoom_obj.summarize_audio_video(raw_data)
                                            logging.debug(f"Checking device data in robo report: {device_data}")
                                        except Exception as e:
                                            logger.error(f"Error reading {found_files[0]}: {e}")
                                            self.overall_report.set_text(f"Error loading data for {coord}/{angle}")
                                            self.overall_report.build_text_simple()
                                            continue
                                    else:
                                        self.overall_report.set_text(f"No data found for {coord}/{angle}")
                                        self.overall_report.build_text_simple()
                                        continue

                                    # 3. Generate Audio Graphs (Device on Y-Axis)
                                    if curr_zoom_obj.audio:
                                        # if self.rotations_enabled:
                                        #     self.report.set_text(
                                        #         f"Audio Performance at {coord} coordinate - {angle} degrees angle"
                                        #     )
                                        # else:
                                        #     self.report.set_text(f"Audio Performance at {coord} coordinate")
                                        # self.report.build_text_simple()

                                        suffix = f"_{coord}_{angle}"  # Unique suffix for image names
                                        _build_metric_graph(
                                            "Audio",
                                            "Bitrate",
                                            "Kbps",
                                            device_data,
                                            "audio_input_bitrate_avg",
                                            "audio_output_bitrate_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Audio",
                                            "Latency",
                                            "ms",
                                            device_data,
                                            "audio_input_latency_avg",
                                            "audio_output_latency_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Audio",
                                            "Jitter",
                                            "ms",
                                            device_data,
                                            "audio_input_jitter_avg",
                                            "audio_output_jitter_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Audio",
                                            "Packet Loss",
                                            "%",
                                            device_data,
                                            "audio_input_avg_loss_avg_avg",
                                            "audio_output_avg_loss_avg_avg",
                                            suffix,
                                        )

                                        _build_results_table(device_data, "audio")

                                    # 4. Generate Video Graphs (Device on Y-Axis)
                                    if curr_zoom_obj.video:
                                        # if self.rotations_enabled:
                                        #     self.report.set_text(
                                        #         f"Video Performance at {coord} coordinate - {angle} degrees angle"
                                        #     )
                                        # else:
                                        #     self.report.set_text(f"Video Performance at {coord} coordinate")
                                        # self.report.build_text_simple()

                                        suffix = f"_{coord}_{angle}"
                                        _build_metric_graph(
                                            "Video",
                                            "Bitrate",
                                            "Kbps",
                                            device_data,
                                            "video_input_bitrate_avg",
                                            "video_output_bitrate_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Video",
                                            "Latency",
                                            "ms",
                                            device_data,
                                            "video_input_latency_avg",
                                            "video_output_latency_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Video",
                                            "Jitter",
                                            "ms",
                                            device_data,
                                            "video_input_jitter_avg",
                                            "video_output_jitter_avg",
                                            suffix,
                                        )
                                        _build_metric_graph(
                                            "Video",
                                            "Packet Loss",
                                            "%",
                                            device_data,
                                            "video_input_avg_loss_avg",
                                            "video_output_avg_loss_avg",
                                            suffix,
                                        )
                                        _build_results_table(device_data, "video")

                                    # Add a separator between coordinates
                                    self.overall_report.set_custom_html("<hr>")
                                    self.overall_report.build_custom()

                            if curr_zoom_obj.do_webui:
                                curr_zoom_obj.add_live_view_images_to_report()

                            # --- Finalize Report ---
                            # self.overall_report.build_custom()
                            # self.overall_report.write_html()
                            # self.overall_report.write_pdf(_page_size="Legal", _orientation="Landscape")
                            # curr_zoom_obj._move_report_files(report_1.get_path_date_time())
                        zoom_obj = curr_zoom_obj
                        if self.do_bandsteering:
                            zoom_obj.add_bandsteering_report_section(report=self.overall_report)
                            logging.info(f"Band steering report added for {obj_name}")
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"zoom_test_{obj_no}"
                        else:
                            break

                elif test_name == "teams_test":
                    obj_no = 1
                    obj_name = "teams_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.teams_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''

                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()
                        testtype = ""
                        obj = self.teams_obj_dict[ce][obj_name]["obj"]
                        if obj.audio and obj.video:
                            testtype = "AUDIO & VIDEO"
                        elif obj.audio:
                            testtype = "AUDIO"
                        elif obj.video:
                            testtype = "VIDEO"
                        curr_teams_obj = copy.copy(self.teams_obj_dict[ce][obj_name]['obj'])
                        test_parameters = pd.DataFrame(
                            [
                                {
                                    "No of Clients": f"W({curr_teams_obj.windows}),L({curr_teams_obj.linux}),M({curr_teams_obj.mac}),A({curr_teams_obj.android})",
                                    "Test Duration(min)": curr_teams_obj.duration,
                                    "HOST": curr_teams_obj.real_sta_list[0],
                                    "TEST TYPE": testtype,
                                }
                            ]
                        )
                        self.overall_report.set_table_dataframe(test_parameters)
                        self.overall_report.build_table()

                        self.overall_report.set_table_title("Test Devices:")
                        self.overall_report.build_table_title()

                        device_details = pd.DataFrame(
                            {
                                "Hostname": obj.real_sta_hostname,
                                "OS Type": obj.real_sta_os_types,
                            }
                        )
                        self.overall_report.set_table_dataframe(device_details)
                        self.overall_report.build_table()

                        if obj.audio:
                            metrics = [
                                ("Audio RTT(ms)", "Audio RTT (ms)"),
                                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                                ("Sent Audio Bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
                            ]

                        if obj.video:
                            # Create bar graphs for each metric
                            metrics = [
                                ("Sent Video Bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                                ("Received Video Bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                                ("Sent Video Packets", "Sent Video Packets"),
                            ]
                        if obj.audio and obj.video:
                            # Create bar graphs for each metric
                            metrics = [
                                ("Audio RTT(ms)", "Audio RTT (ms)"),
                                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                                ("Sent Audio Bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
                                ("Sent Video Bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                                ("Received Video Bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                                ("Sent Video Packets", "Sent Video Packets"),
                            ]

                        # Read per-device average metrics

                        new_list = []

                        for avg_csvs in obj.avg_csv_files_list:
                            file_name = os.path.basename(avg_csvs["file"])

                            updated_dict = dict(avg_csvs)
                            updated_dict["file"] = os.path.join(
                                obj.report_path_date_time,
                                file_name
                            )

                            new_list.append(updated_dict)

                        obj.avg_csv_files_list = new_list

                        # VERY IMPORTANT → reassign full object back
                        obj.path = obj.report_path_date_time
                        obj.report = self.overall_report
                        obj.generate_graphs_and_tables(metrics)
                        if obj.do_robo and obj.do_webui:
                            obj.add_live_view_images_to_report()
                        if obj.do_bs:
                            obj.add_bandsteering_report_section()

                        self.teams_obj_dict[ce][obj_name]["obj"] = obj
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"rb_test_{obj_no}"
                        else:
                            break

            except Exception as e:
                traceback.print_exc()
                logger.info(f"failed to generate report for {test_name} {e}")

    def generate_test_exc_df(self, test_results_df, args_dict):
        '''
        Generate Test Execution DataFrames
        ----------------------------------
        Splits and formats the main test_results_df into sequential (series_df)
        and parallel (parallel_df) dataframes based on the configured order priority.
        '''
        series_df = {}
        parallel_df = {}
        if self.order_priority == "series":
            if len(self.series_tests) != 0:
                series_df = test_results_df[:len(self.series_tests)].copy()
                series_df["s/no"] = range(1, len(series_df) + 1)
                series_df = series_df[["s/no", "test_name", "Duration", "status"]]
            if len(self.parallel_tests) != 0:
                parallel_df = test_results_df[len(self.series_tests):].copy()
                parallel_df["s/no"] = range(1, len(parallel_df) + 1)
                parallel_df = parallel_df[["s/no", "test_name", "Duration", "status"]]
        else:
            if len(self.parallel_tests) != 0:
                parallel_df = test_results_df[:len(self.parallel_tests)].copy()
                parallel_df["s/no"] = range(1, len(parallel_df) + 1)
                parallel_df = parallel_df[["s/no", "test_name", "Duration", "status"]]

            if len(self.series_tests) != 0:
                series_df = test_results_df[len(self.parallel_tests):].copy()
                series_df["s/no"] = range(1, len(series_df) + 1)
                series_df = series_df[["s/no", "test_name", "Duration", "status"]]
        return series_df, parallel_df

    def generate_overall_report(self, test_results_df='', args_dict=None):
        '''
        Generate Overall Report
        -----------------------
        Initializes the overall report, adds banners and tables for
        series/parallel test execution sets, and renders each test block.
        Finally builds the footer, writes the HTML and PDF reports.
        '''
        args_dict = {} if args_dict is None else args_dict
        self.overall_report = lf_report.lf_report(_results_dir_name="lf_multi_traffic_Test_Overall_report", _output_html="lf_multi_traffic_overall.html",
                                                  _output_pdf="lf_multi_traffic_overall.pdf", _path=self.result_path if not self.dowebgui else self.result_dir)
        self.report_path_date_time = self.overall_report.get_path_date_time()
        self.overall_report.set_title("MULTI TRAFFIC TEST")
        self.overall_report.set_date(datetime.datetime.now())
        self.overall_report.build_banner()
        try:
            series_df, parallel_df = self.generate_test_exc_df(test_results_df, args_dict)
        except Exception:
            logging.error('Exception failed dataframe creation', exc_info=True)
        if self.order_priority == "series":
            if len(self.series_tests) != 0:
                self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Series Tests</h1>')
                self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                self.overall_report.set_custom_html(series_df.to_html(index=False, justify='center'))
                self.overall_report.build_custom()
                self.render_each_test(ce="series")
            if len(self.parallel_tests) != 0:
                self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Parallel Tests</h1>')
                self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                self.overall_report.set_custom_html(parallel_df.to_html(index=False, justify='center'))
                self.overall_report.build_custom()
                self.render_each_test(ce="parallel")
        else:
            if len(self.parallel_tests) != 0:
                self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Parallel Tests</h1>')
                self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                self.overall_report.set_custom_html(parallel_df.to_html(index=False, justify='center'))
                self.overall_report.build_custom()
                self.render_each_test(ce="parallel")
            if len(self.series_tests) != 0:
                self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Series Tests</h1>')
                self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                self.overall_report.set_custom_html(series_df.to_html(index=False, justify='center'))
                self.overall_report.build_custom()
                self.render_each_test(ce="series")
        self.overall_report.build_footer()
        html_file = self.overall_report.write_html()
        logging.info(f"Generated HTML report file: {html_file}")
        self.overall_report.write_pdf()


def validate_individual_args(args, test_name):
    '''
    Validate Individual Arguments
    -----------------------------
    Validates required arguments specific to each test type.
    Returns True if all required arguments are present, False otherwise.
    '''
    if test_name == 'ping_test':
        return True
    elif test_name == 'http_test':
        return True
    elif test_name == 'ftp_test':
        return True
    elif test_name == 'thput_test':
        return True
    elif test_name == 'qos_test':
        return True
    elif test_name == 'vs_test':
        return True
    elif test_name == "zoom_test":
        if args["zoom_signin_email"] is None:
            return False
        if args["zoom_signin_passwd"] is None:
            return False
        if args["zoom_participants"] is None:
            return False
        return True
    elif test_name == "yt_test":
        if args["yt_url"] is None:
            return False
        return True
    elif test_name == "rb_test":
        return True


def validate_time(n: str) -> str:
    '''
    Validate Time String
    --------------------
    Parses a time string (e.g. '10s', '5m', '2h', or a raw digit for seconds)
    and normalizes it into a human-readable string representation (secs, mins, or hours).
    Returns 'wrong type' if the input format is invalid.
    '''
    try:
        if isinstance(n, type(n)) == str and n.isdigit():
            seconds = int(n)
        elif n.endswith("s"):
            seconds = int(n[:-1])
        elif n.endswith("m"):
            seconds = int(n[:-1]) * 60
        elif n.endswith("h"):
            seconds = int(n[:-1]) * 3600
        else:
            return "wrong type"

        if seconds < 60:
            return f"{seconds} secs"
        elif seconds < 3600:
            return f"{seconds // 60} mins"
        else:
            return f"{seconds // 3600} hours"
    except ValueError:
        return "wrong type"


def validate_args(args):
    '''
    Validate Arguments
    ------------------
    Validates general arguments for pass/fail, configurations,
    and groups/profiles across all specified series and parallel tests.
    '''
    tests = ["http_test", "ping_test", "ftp_test", "thput_test", "qos_test", "vs_test", "mcast_test", "yt_test", "rb_test", "zoom_test"]

    series_tests_list = []
    if args.get("series_tests"):
        series_tests_list = args["series_tests"].split(',')

    parallel_tests_list = []
    if args.get("parallel_tests"):
        parallel_tests_list = args["parallel_tests"].split(',')

    for test in tests:
        flag_test = True
        if test in series_tests_list or test in parallel_tests_list:
            logger.info(f"validating args for {test}...")
            flag_test = validate_individual_args(args, test)
            test = test.split('_')[0]
            if args[f'{test}_expected_passfail_value'] and args[f'{test}_device_csv_name']:
                logger.error(f"Specify either --{test}_expected_passfail_value or --{test}_device_csv_name")
                flag_test = False
            if args[f'{test}_group_name']:
                selected_groups = args[f'{test}_group_name'].split(',')
            else:
                selected_groups = []
            if args[f'{test}_profile_name']:
                selected_profiles = args['profile_name'].split(',')
            else:
                selected_profiles = []

            if len(selected_groups) != len(selected_profiles):
                logger.error("Number of groups should match number of profiles")
                flag_test = False
            elif args[f'{test}_group_name'] and args[f'{test}_profile_name'] and args[f'{test}_file_name'] and args[f'{test}_device_list'] != []:
                logger.error(f"Either --{test}_group_name or --{test}_device_list should be entered not both")
                flag_test = False
            elif args[f'{test}_ssid'] and args[f'{test}_profile_name']:
                logger.error(f"Either --{test}_ssid or --{test}_profile_name should be given")
                flag_test = False

            elif args[f'{test}_file_name'] and (args.get(f'{test}_group_name') is None or args.get(f'{test}_profile_name') is None):
                logger.error("Please enter the correct set of arguments for configuration")
                flag_test = False

            if args[f'{test}_config'] and args.get(f'{test}_group_name') is None:
                if args.get(f'{test}_ssid') and args.get(f'{test}_security') and args[f'{test}_security'].lower() == 'open' and (args.get(f'{test}_passwd') is None or args[f'{test}_passwd'] == ''):
                    args[f'{test}_passwd'] = '[BLANK]'

                if args.get(f'{test}_ssid') is None or args.get(f'{test}_passwd') is None or args[f'{test}_passwd'] == '':
                    logger.error(f'For configuration need to Specify --{test}_ssid , --{test}_passwd (Optional for "open" type security) , --{test}_security')
                    flag_test = False

                elif args.get(f'{test}_ssid') and args[f'{test}_passwd'] == '[BLANK]' and args.get(f'{test}_security') and args[f'{test}_security'].lower() != 'open':
                    logger.error(f'Please provide valid --{test}_passwd and --{test}_security configuration')
                    flag_test = False

                elif args.get(f'{test}_ssid') and args.get(f'{test}_passwd'):
                    if args.get(f'{test}_security') is None:
                        logger.error(f'Security must be provided when --{test}_ssid and --{test}_password specified')
                        flag_test = False
                    elif args[f'{test}_passwd'] == '[BLANK]' and args[f'{test}_security'].lower() != 'open':
                        logger.error('Please provide valid passwd and security configuration')
                        flag_test = False
                    elif args[f'{test}_security'].lower() == 'open' and args[f'{test}_passwd'] != '[BLANK]':
                        logger.error("For an open type security, the password should be left blank (i.e., set to '' or [BLANK]).")
                        flag_test = False
            if flag_test:
                logger.info(f"Arg validation check done for {test}")


def normalise_time(value):
    if value is None:
        return value

    value = str(value).strip()

    if not value:
        return value

    # Pure number → return int
    if value.isnumeric():
        return int(value)

    num_part = ''
    unit_part = ''

    for ch in value:
        if ch.isdigit() or ch == '.':
            num_part += ch
        else:
            unit_part += ch

    if not num_part:
        return value  # leave as is if invalid

    num = float(num_part)
    unit = unit_part.lower()

    if unit == 'm':
        return int(num)
    elif unit == 'h':
        return int(num * 60)
    elif unit == 's':
        return int(num / 60)   # will become 0 for values < 60s
    else:
        return value  # unknown suffix → unchanged


def parse_args():
    parser = argparse.ArgumentParser(
        prog="lf_multi_traffic.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''

    NAME: lf_multi_traffic.py

    PURPOSE:
    lf_multi_traffic.py is used to execute multiple testcases
    either in series, parallel, or hybrid mode.

    The script supports running tests sequentially (series), simultaneously (parallel),
    or a combination of both, with configurable execution priority.

    SUPPORTED TESTS:

    Tests supported for series execution:
        ping_test
        qos_test
        ftp_test
        http_test
        mcast_test
        vs_test
        thput_test
        rb_test
        teams_test
        yt_test
        zoom_test

    Tests supported for parallel execution:
        ping_test
        qos_test
        ftp_test
        http_test
        mcast_test
        vs_test
        thput_test

    Real Application Tests (Only Series Supported):
        yt_test        (YouTube)
        rb_test        (Real Browser)
        teams_test     (Microsoft Teams)
        zoom_test      (Zoom Call)


    EXECUTION RULES:

    1. SERIES TESTS:
    - Runs tests one after another
    - Maintains execution order
    - Allows duplicate tests

    2. PARALLEL TESTS:
    - Runs tests simultaneously
    - Duplicate tests are NOT allowed
    - Real application tests are NOT supported

    3. HYBRID MODE:
    - Both --series_tests and --parallel_tests can be used
    - Execution order controlled by --order_priority


    ARGUMENT:

    --order_priority:
        Defines which test group runs first
        Choices:
            series    -> series tests run first
            parallel  -> parallel tests run first

    EXAMPLE-1:
    Command Line Interface to run all series tests with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000 \
    \
    --rb_duration 1m \
    --rb_device_list 1.15,1.4 \
    --rb_webgui_incremental no_increment \
    --rb_count 10 \
    \
    --yt_url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --yt_duration 1m \
    --yt_res 144p \
    --yt_device_list 1.15,1.4 \
    \
    --zoom_signin_email candelatech2@gmail.com \
    --zoom_signin_passwd 'CANDELAtech1@530048' \
    --zoom_duration 2 \
    --zoom_host 1.15 \
    --zoom_participants 2 \
    --zoom_device_list 1.15,1.4 \
    --zoom_audio \
    --zoom_video \
    \
    --teams_duration 2m \
    --teams_device_list 1.15,1.4 \
    --teams_audio \
    --teams_video

    EXAMPLE-2:
    Command Line Interface to run all parallel tests with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --parallel_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000

    EXAMPLE-3:
    Command Line Interface to run all series tests and parallel with full arguments

    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    --parallel_tests ping_test,qos_test,ftp_test,http_test,mcast_test,vs_test,thput_test,rb_test,yt_test,teams_test,zoom_test \
    \
    --ping_target www.google.com \
    --ping_interval 5 \
    --ping_duration 1 \
    --ping_device_list 1.10,1.11,1.20 \
    \
    --qos_tos VO,VI,BE,BK \
    --qos_duration 1m \
    --qos_device_list 1.10,1.11,1.20 \
    --qos_traffic_type lf_tcp \
    --qos_download 10000000 \
    \
    --ftp_duration 1m \
    --ftp_file_size 5MB \
    --ftp_device_list 1.10,1.11,1.20 \
    --ftp_bands 5G \
    \
    --http_duration 1m \
    --http_file_size 5MB \
    --http_device_list 1.10,1.11,1.20 \
    --http_bands 5G \
    \
    --mcast_tos VO \
    --mcast_test_duration 1m \
    --mcast_side_b_min_bps 10000000 \
    --mcast_device_list 1.10,1.11,1.20 \
    --mcast_endp_type mc_udp \
    \
    --vs_url https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8 \
    --vs_media_source hls \
    --vs_media_quality 4k \
    --vs_duration 1m \
    --vs_device_list 1.10,1.11,1.20 \
    \
    --thput_test_duration 1m \
    --thput_traffic_type lf_udp \
    --thput_device_list 1.10,1.11,1.20 \
    --thput_upload 10000000 \
    \
    --rb_duration 1m \
    --rb_device_list 1.15,1.4 \
    --rb_webgui_incremental no_increment \
    --rb_count 10 \
    \
    --yt_url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --yt_duration 1m \
    --yt_res 144p \
    --yt_device_list 1.15,1.4 \
    \
    --zoom_signin_email candelatech2@gmail.com \
    --zoom_signin_passwd 'CANDELAtech1@530048' \
    --zoom_duration 2 \
    --zoom_host 1.15 \
    --zoom_participants 2 \
    --zoom_device_list 1.15,1.4 \
    --zoom_audio \
    --zoom_video \
    \
    --teams_duration 2m \
    --teams_device_list 1.15,1.4 \
    --teams_audio \
    --teams_video

    EXAMPLE-4:
    Duplicate tests allowed only in series
    python3 lf_multi_traffic.py \
    --mgr 192.168.207.78 \
    --upstream_port eth1 \
    --series_tests http_test,ftp_test,http_test

    NOTE : Add traffic related args from EXAMPLE 1



    NOTES:
    1. Duration format: s (seconds), m (minutes), h (hours)
    2. Parallel execution improves performance but is limited to network tests
    3. Real application tests must always be executed in series
    4. Avoid duplicates in parallel_tests
    5. Use --order_priority to control execution flow

    STATUS : Functional

    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES: Performance, Functional, Automation

    VERIFIED_ON:
    Working date - 21/04/2026
    Build version - 5.5.3
    kernel version - 6.18.14+

    LICENSE :
    Copyright (C) 2020-2026 Candela Technologies Inc
    Free to distribute and modify. LANforge systems must be licensed.

    INCLUDE_IN_README: False
    ''',
    )
    # Always Common
    parser.add_argument('--mgr', '--lfmgr', default='localhost', help='hostname for where LANforge GUI is running')
    parser.add_argument('--mgr_port', '--port', default=8080, help='port LANforge GUI HTTP service is running on')
    parser.add_argument('--upstream_port', '-u', default='eth1', help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    # Common
    parser.add_argument('--device_list', help="Enter the devices on which the test should be run", default=[])
    parser.add_argument('--duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--parallel',
                        action="store_true",
                        help='to run in parallel')
    parser.add_argument("--tests", type=str, help="Comma-separated ordered list of tests to run (e.g., ping_test,http_test,ping_test)")
    parser.add_argument('--series_tests', help='Comma-separated list of tests to run in series')
    parser.add_argument('--parallel_tests', help='Comma-separated list of tests to run in parallel')
    parser.add_argument('--order_priority', choices=['series', 'parallel'], default='series',
                        help='Which tests to run first: series or parallel')
    parser.add_argument('--test_name', help='Name of the Test')
    parser.add_argument('--dowebgui', help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--result_dir', help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')
    parser.add_argument('--no_cleanup', help='Do not cleanup before exit', action='store_true')
    parser.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')
    # PING ARGS
    # without config
    parser.add_argument('--ping_test',
                        action="store_true",
                        help='ping_test consists')
    parser.add_argument('--ping_target',
                        type=str,
                        help='Target URL or port for ping test',
                        default='1.1.eth1')
    parser.add_argument('--ping_interval',
                        type=str,
                        help='Interval (in seconds) between the echo requests',
                        default='1')

    parser.add_argument('--ping_duration',
                        help='Duration (in minutes) to run the ping test',
                        default="1")
    parser.add_argument('--ping_use_default_config',
                        action='store_true',
                        help='specify this flag if wanted to proceed with existing Wi-Fi configuration of the devices')
    parser.add_argument('--ping_device_list', help="Enter the devices on which the ping test should be run", default=[])
    # ping pass fail value
    parser.add_argument("--ping_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--ping_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # ping with groups and profile configuration
    parser.add_argument('--ping_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--ping_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--ping_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # ping configuration with --config
    parser.add_argument("--ping_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--ping_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--ping_passwd', '--ping_password', '--ping_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--ping_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--ping_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--ping_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ping_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ping_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ping_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--ping_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--ping_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--ping_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--ping_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--ping_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--ping_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--ping_pairwise", type=str, default='NA')
    parser.add_argument("--ping_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--ping_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--ping_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--ping_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--ping_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--ping_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    # HTTP ARGS
    parser.add_argument('--http_test',
                        action="store_true",
                        help='http consists')
    parser.add_argument('--http_bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                        default=["5G", "2.4G", "6G"])
    parser.add_argument('--http_duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--http_file_size', type=str, help='specify the size of file you want to download', default='5MB')
    parser.add_argument('--http_device_list', help="Enter the devices on which the http test should be run", default=[])
    # http pass fail value
    parser.add_argument("--http_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--http_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # http with groups and profile configuration
    parser.add_argument('--http_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--http_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--http_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # http configuration with --config
    parser.add_argument("--http_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--http_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--http_passwd', '--http_password', '--http_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--http_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--http_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--http_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--http_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--http_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--http_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--http_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--http_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--http_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--http_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--http_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--http_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--http_pairwise", type=str, default='NA')
    parser.add_argument("--http_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--http_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--http_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--http_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--http_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--http_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    # ftp
    parser.add_argument('--ftp_test',
                        action="store_true",
                        help='ftp_test consists')
    parser.add_argument('--ftp_bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                        default=["5G", "2.4G", "6G"])
    parser.add_argument('--ftp_duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--ftp_file_size', type=str, help='specify the size of file you want to download', default='5MB')
    parser.add_argument('--ftp_device_list', help="Enter the devices on which the ftp test should be run", default=[])
    # ftp pass fail value
    parser.add_argument("--ftp_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--ftp_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # ftp with groups and profile configuration
    parser.add_argument('--ftp_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--ftp_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--ftp_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # ftp configuration with --config
    parser.add_argument("--ftp_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--ftp_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--ftp_passwd', '--ftp_password', '--ftp_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--ftp_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--ftp_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--ftp_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ftp_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ftp_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ftp_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--ftp_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--ftp_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--ftp_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--ftp_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--ftp_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--ftp_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--ftp_pairwise", type=str, default='NA')
    parser.add_argument("--ftp_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--ftp_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--ftp_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--ftp_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--ftp_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--ftp_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    # QOS ARGS
    parser.add_argument('--qos_test',
                        action="store_true",
                        help='qos_test consists')
    parser.add_argument('--qos_duration', help='--qos_duration sets the duration of the test', default="2m")
    parser.add_argument('--qos_upload', help='--upload traffic load per connection (upload rate)')
    parser.add_argument('--qos_download', help='--download traffic load per connection (download rate)')
    parser.add_argument('--qos_traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    parser.add_argument('--qos_tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    parser.add_argument('--qos_device_list', help="Enter the devices on which the qos test should be run", default=[])
    # qos pass fail value
    parser.add_argument("--qos_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--qos_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # qos with groups and profile configuration
    parser.add_argument('--qos_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--qos_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--qos_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # qos configuration with --config
    parser.add_argument("--qos_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--qos_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--qos_passwd', '--qos_password', '--qos_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--qos_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional qos config args
    parser.add_argument("--qos_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--qos_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--qos_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--qos_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--qos_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--qos_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--qos_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--qos_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--qos_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--qos_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--qos_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--qos_pairwise", type=str, default='NA')
    parser.add_argument("--qos_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--qos_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--qos_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--qos_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--qos_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--qos_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    # VS ARGS
    parser.add_argument('--vs_test',
                        action="store_true",
                        help='vs_test consists')
    parser.add_argument("--vs_url", default="www.google.com", help='specify the url you want to test on')
    parser.add_argument("--vs_media_source", type=str, default='1')
    parser.add_argument("--vs_media_quality", type=str, default='0')
    parser.add_argument('--vs_duration', type=str, help='time to run traffic')
    parser.add_argument('--vs_device_list', help="Enter the devices on which the vs test should be run", default=[])
    # vs pass fail value
    parser.add_argument("--vs_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--vs_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # vs with groups and profile configuration
    parser.add_argument('--vs_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--vs_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--vs_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # vs configuration with --config
    parser.add_argument("--vs_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--vs_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--vs_passwd', '--vs_password', '--vs_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--vs_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional vs config args
    parser.add_argument("--vs_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--vs_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--vs_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--vs_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--vs_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--vs_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--vs_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--vs_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--vs_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--vs_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--vs_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--vs_pairwise", type=str, default='NA')
    parser.add_argument("--vs_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--vs_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--vs_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--vs_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--vs_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--vs_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    # THPUT ARGS
    parser.add_argument('--thput_test',
                        action="store_true",
                        help='thput_test consists')
    parser.add_argument('--thput_test_duration', help='--thput_test_duration sets the duration of the test', default="")
    parser.add_argument('--thput_download', help='--thput_download traffic load per connection (download rate)', default='2560')
    parser.add_argument('--thput_traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    parser.add_argument('--thput_upload', help='--thput_upload traffic load per connection (upload rate)', default='2560')
    parser.add_argument('--thput_device_list', help="Enter the devices on which the thput test should be run", default=[])
    parser.add_argument('--thput_do_interopability', action='store_true', help='Ensures test on devices run sequentially, capturing each device’s data individually for plotting in the final report.')
    parser.add_argument("--thput_default_config", action="store_true", help="To stop configuring the devices in interoperability")
    # thput pass fail value
    parser.add_argument("--thput_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--thput_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # thput with groups and profile configuration
    parser.add_argument('--thput_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--thput_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--thput_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument('--thput_load_type', help="Determine the type of load: < wc_intended_load | wc_per_client_load >", default="wc_per_client_load")
    parser.add_argument('--thput_packet_size', help='Determine the size of the packet in which Packet Size Should be Greater than 16B or less than 64KB(65507)', default="-1")

    # thput configuration with --config
    parser.add_argument("--thput_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--thput_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--thput_passwd', '--thput_password', '--thput_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--thput_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional thput config args
    parser.add_argument("--thput_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--thput_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--thput_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--thput_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--thput_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--thput_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--thput_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--thput_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--thput_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--thput_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--thput_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--thput_pairwise", type=str, default='NA')
    parser.add_argument("--thput_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--thput_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--thput_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--thput_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--thput_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--thput_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    # MCAST TEST
    parser.add_argument('--mcast_test',
                        action="store_true",
                        help='mcast_test consists')
    parser.add_argument(
        '--mcast_test_duration',
        help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',
        default='3m')
    parser.add_argument(
        '--mcast_endp_type',
        help=(
            '--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\" '
            ' Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6'),
        default='lf_udp',
        type=valid_endp_types)
    parser.add_argument(
        '--mcast_upstream_port',
        help='--mcast_upstream_port <cross connect upstream_port> example: --mcast_upstream_port eth1',
        default='eth1')
    parser.add_argument(
        '--mcast_side_b_min_bps',
        help='''--side_b_min_bps or --download_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000
                When runnign with tcp/udp and mcast will use this value''',
        default="256000")
    parser.add_argument(
        '--mcast_tos',
        help='--tos:  Support different ToS settings: BK,BE,VI,VO,numeric',
        default="BE")
    parser.add_argument(
        '--mcast_device_list',
        action='append',
        help='Specify the Resource IDs for real clients. Accepts a comma-separated list (e.g., 1.11,1.95,1.360).'
    )
    # mcast pass fail value
    parser.add_argument("--mcast_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--mcast_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # mcast with groups and profile configuration
    parser.add_argument('--mcast_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--mcast_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--mcast_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # mcast configuration with --config
    parser.add_argument("--mcast_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--mcast_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--mcast_passwd', '--mcast_password', '--mcast_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--mcast_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional mcast config args
    parser.add_argument("--mcast_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--mcast_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--mcast_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--mcast_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--mcast_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--mcast_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--mcast_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--mcast_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--mcast_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--mcast_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--mcast_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--mcast_pairwise", type=str, default='NA')
    parser.add_argument("--mcast_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--mcast_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--mcast_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--mcast_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--mcast_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--mcast_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    # YOUTUBE ARGS
    parser.add_argument('--yt_test',
                        action="store_true",
                        help='yt_test consists')
    parser.add_argument('--yt_url', type=str, help='youtube url')
    parser.add_argument('--yt_duration', help='duration to run the test in sec')
    parser.add_argument('--yt_res', default='Auto', help="to set resolution to  144p,240p,720p")
    # parser.add_argument('--yt_upstream_port', type=str, help='Specify The Upstream Port name or IP address', required=True)
    parser.add_argument('--yt_device_list', help='Specify the real device ports seperated by comma')
    # yt pass fail value
    parser.add_argument("--yt_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--yt_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # yt with groups and profile configuration
    parser.add_argument('--yt_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--yt_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--yt_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # yt configuration with --config
    parser.add_argument("--yt_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--yt_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--yt_passwd', '--yt_password', '--yt_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--yt_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional yt config args
    parser.add_argument("--yt_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--yt_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--yt_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--yt_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--yt_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--yt_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--yt_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--yt_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--yt_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--yt_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--yt_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--yt_pairwise", type=str, default='NA')
    parser.add_argument("--yt_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--yt_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--yt_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--yt_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--yt_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--yt_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    # REAL BROWSER ARGS
    parser.add_argument('--rb_test',
                        action="store_true",
                        help='rb_test consists')
    parser.add_argument("--rb_url", default="https://google.com", help='specify the url you want to test on')
    parser.add_argument('--rb_duration', type=str, help='time to run traffic')
    parser.add_argument('--rb_device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
    parser.add_argument('--rb_webgui_incremental', '--rb_incremental_capacity', help="Specify the incremental values <1,2,3..>", dest='rb_webgui_incremental', type=str)
    parser.add_argument('--rb_incremental', help="to add incremental capacity to run the test", action='store_true')
    parser.add_argument("--rb_count", type=int, default=100, help='specify the number of url you want to test on '
                        'per minute')
    # rb pass fail value
    parser.add_argument("--rb_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--rb_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # rb with groups and profile configuration
    parser.add_argument('--rb_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--rb_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--rb_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # rb configuration with --config
    parser.add_argument("--rb_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--rb_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--rb_passwd', '--rb_password', '--rb_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--rb_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional rb config args
    parser.add_argument("--rb_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--rb_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--rb_ieee80211", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--rb_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--rb_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--rb_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--rb_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--rb_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--rb_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--rb_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--rb_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--rb_pairwise", type=str, default='NA')
    parser.add_argument("--rb_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--rb_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--rb_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--rb_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--rb_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--rb_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    # ZOOM ARGS
    parser.add_argument('--zoom_test',
                        action="store_true",
                        help='zoom_test consists')
    parser.add_argument('--zoom_duration', help="Duration of the Zoom meeting in minutes", default="1")
    parser.add_argument('--zoom_signin_email', type=str, help="Sign-in email")
    parser.add_argument('--zoom_signin_passwd', type=str, help="Sign-in password")
    parser.add_argument('--zoom_participants', type=int, help="no of participanrs")
    parser.add_argument('--zoom_audio', action='store_true')
    parser.add_argument('--zoom_video', action='store_true')
    parser.add_argument('--zoom_device_list', help="resources participated in the test")
    parser.add_argument('--zoom_host', help="Host of the test")
    # zoom pass fail value
    parser.add_argument("--zoom_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--zoom_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    # zoom with groups and profile configuration
    parser.add_argument('--zoom_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--zoom_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--zoom_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    # zoom configuration with --config
    parser.add_argument("--zoom_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--zoom_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--zoom_passwd', '--zoom_password', '--zoom_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--zoom_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    # Optional zoom config args
    parser.add_argument("--zoom_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--zoom_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--zoom_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--zoom_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--zoom_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--zoom_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--zoom_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--zoom_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--zoom_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--zoom_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--zoom_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--zoom_pairwise", type=str, default='NA')
    parser.add_argument("--zoom_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--zoom_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--zoom_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--zoom_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--zoom_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--zoom_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    parser.add_argument("--api_stats_collection", action="store_true", help='Specify if using business account to get the stats using api')
    parser.add_argument("--account_id", help="Zoom Account ID")
    parser.add_argument("--client_id", help="Zoom Client ID")
    parser.add_argument("--client_secret", help="Zoom Client Secret")
    parser.add_argument("--env_file", type=str, default='.env', help='Path to .env file for credentials')

    # TEAMS ARGS
    parser.add_argument(
        "--teams_duration", help="duration to run the test in min", default="1"
    )
    parser.add_argument(
        "--teams_device_list", help="Specify the real device ports seperated by comma"
    )
    parser.add_argument(
        "--teams_no_pre_cleanup",
        action="store_true",
        help="specify this flag to stop cleaning up generic cxs before the test",
    )
    parser.add_argument(
        "--teams_no_post_cleanup",
        action="store_true",
        help="specify this flag to stop cleaning up generic cxs after the test",
    )
    parser.add_argument(
        "--teams_log_level", help="Level of the logs to be displayed", default="info"
    )
    parser.add_argument("--teams_lf_logger_config_json", help="lf_logger config json")
    parser.add_argument("--teams_audio", action="store_true")
    parser.add_argument("--teams_video", action="store_true")
    parser.add_argument(
        "--teams_do_webUI",
        action="store_true",
        help="useful to specify whether we are running through webui or cli",
    )
    parser.add_argument(
        "--teams_testname", help="Name of the test"
    )
    parser.add_argument(
        "--teams_report_dir", help="report directory while running test through web ui"
    )
    parser.add_argument(
        "--teams_enable_mobile_stats",
        action="store_true",
        help="Used to specify whether to collect mobile stats through chrome browser based UI automation or not",
    )

    parser.add_argument("--teams_robo_ip", type=str, help="Specify the robo ip")
    parser.add_argument(
        "--teams_coordinates",
        help="Comma-separated list of coordinate point names (e.g. 1,2,3), each mapping to x and y values",
    )

    parser.add_argument(
        "--teams_rotations",
        help="Comma-separated list of rotation angles (in degrees) to apply at respective points",
    )
    parser.add_argument(
        "--teams_do_robo",
        help="Specify this flag to perform the test with robo",
        action="store_true",
    )
    parser.add_argument(
        "--teams_do_bs",
        help="Specify this flag to perform the test with robo for band steering",
        action="store_true",
    )
    parser.add_argument(
        "--teams_cycles", type=int, default=1, help="Number of cycles to run the test"
    )

    parser.add_argument(
        "--teams_bssids",
        type=str,
        help="Comma-separated list of BSSIDs for bandsteering test",
    )
    # Arguments to run robot tests
    parser.add_argument("--robot_test", help='to trigger robot test', action='store_true')
    parser.add_argument('--robot_ip', type=str, default='', help='hostname for where Robot server is running')
    parser.add_argument('--coordinate', type=str, default='', help="The coordinate contains list of coordinates to be ")
    parser.add_argument('--rotation', type=str, default='', help="The set of angles to rotate at a particular point")
    parser.add_argument('--do_bandsteering', help='Enable bandsteering', action='store_true')
    parser.add_argument('--cycles', type=int, default=1, help='No of cycles to perform band steering')
    parser.add_argument('--bssids', type=str, default='', help='hostname for where Robot server is running')
    parser.add_argument("--duration_to_skip", type=int, help='Specify the maximum time in seconds to skip a point if there is an obstacle', default=60)
    #

    args = parser.parse_args()
    return args


def main():
    '''
    Main Execution Block
    --------------------
    Initializes the command-line argument parser, defines argument flags,
    and orchestrates test suite execution for the MULTI TRAFFIC TEST.
    '''
    args = parse_args()
    help_summary = '''\
lf_multi_traffic.py is used to execute multiple testcases
either in series, parallel, or hybrid mode.
The script supports running tests sequentially (series), simultaneously (parallel),
or a combination of both, with configurable execution priority.
'''
    if args.help_summary:
        print(help_summary)
        exit(0)
    args.zoom_duration = normalise_time(args.zoom_duration)
    args.ping_duration = normalise_time(args.ping_duration)
    args.teams_duration = normalise_time(args.teams_duration)
    args_dict = vars(args)
    duration_dict = {}
    multi_traffic_obj = MultiTraffic(
        ip=args.mgr,
        port=args.mgr_port,
        order_priority=args.order_priority,
        test_name=args.test_name,
        result_dir=args.result_dir,
        dowebgui=args.dowebgui,
        no_cleanup=args.no_cleanup,
        robot_test=args.robot_test,
        robot_ip=args.robot_ip,
        coordinate=args.coordinate,
        rotation=args.rotation,
        do_bandsteering=args.do_bandsteering,
        bssids=args.bssids,
        cycles=args.cycles,
        duration_to_skip=args.duration_to_skip)
    # Map available test flags to their respective execution methods
    test_map = {
        "ping_test": (run_ping_test, "PING TEST"),
        "http_test": (run_http_test, "HTTP TEST"),
        "ftp_test": (run_ftp_test, "FTP TEST"),
        "qos_test": (run_qos_test, "QoS TEST"),
        "vs_test": (run_vs_test, "VIDEO STREAMING TEST"),
        "thput_test": (run_thput_test, "THROUGHPUT TEST"),
        "mcast_test": (run_mcast_test, "MULTICAST TEST"),
        "yt_test": (run_yt_test, "YOUTUBE TEST"),
        "rb_test": (run_rb_test, "REAL BROWSER TEST"),
        "zoom_test": (run_zoom_test, "ZOOM TEST"),
        "teams_test": (run_teams_test, "TEAMS TEST"),
    }

    # Ensure at least one test suite is provided
    if not args.series_tests and not args.parallel_tests:
        logger.error("Please provide tests cases --parallel_tests or --series_tests")
        logger.info(f"Available tests are {list(test_map.keys())}")
        exit(0)

    flag = 1
    tests_to_run_series = []
    tests_to_run_parallel = []

    # Parse and validate series tests
    if args.series_tests:
        tests_to_run_series = args.series_tests.split(',')
        for test in tests_to_run_series:
            if test not in test_map:
                logger.error(f"{test} is not available in test suite")
                flag = 0

    # Parse and validate parallel tests
    if args.parallel_tests:
        tests_to_run_parallel = args.parallel_tests.split(',')
        for test in tests_to_run_parallel:
            if test not in test_map:
                logger.error(f"{test} is not available in test suite")
                flag = 0
        if any(test in tests_to_run_parallel for test in ("rb_test", "teams_test", "yt_test", "zoom_test")):
            logger.error("Real application tests are not supported in parallel execution.")
            exit(0)

    # Abort execution if invalid tests were requested
    if not flag:
        logger.info(f"Available tests are {list(test_map.keys())}")
        exit(0)

    # Prevent duplicate tests from running in parallel
    if args.parallel_tests and (len(tests_to_run_parallel) != len(set(tests_to_run_parallel))):
        logger.error("in --parallel dont specify duplicate tests")
        exit(0)

    duration_flag = False
    if args.series_tests:
        for test in args.series_tests.split(','):
            if test == "thput_test":
                duration_dict[test] = validate_time(args_dict[f"{test}_duration"])
            elif test == "mcast_test":
                duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_test_duration"])
            elif test == "ping_test" or test == "zoom_test" or test == "teams_test":
                duration_dict[test] = "{} mins".format(args_dict["{}_duration".format(test.split('_')[0])])
            else:
                duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_duration"])
    if args.parallel_tests:
        for test in args.parallel_tests.split(','):
            if test == "thput_test":
                duration_dict[test] = validate_time(args_dict[f"{test}_duration"])
            elif test == "mcast_test":
                duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_test_duration"])
            elif test == "ping_test" or test == "zoom_test" or test == "teams_test":
                duration_dict[test] = "{} mins".format(args_dict["{}_duration".format(test.split('_')[0])])
            else:
                duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_duration"])
    for test_name, duration in duration_dict.items():
        if duration == "wrong type":
            duration_flag = True
            logger.error(f"wrong duration type for {test_name}")
    if duration_flag:
        exit(1)
    multi_traffic_obj.duration_dict = duration_dict.copy()
    # args.current = "series"
    iszoom = 'zoom_test' in tests_to_run_parallel or 'zoom_test' in tests_to_run_series
    isrb = 'rb_test' in tests_to_run_parallel or 'rb_test' in tests_to_run_series
    isyt = 'yt_test' in tests_to_run_parallel or 'yt_test' in tests_to_run_series
    multi_traffic_obj.series_tests = tests_to_run_series
    multi_traffic_obj.parallel_tests = tests_to_run_parallel
    multi_traffic_obj.misc_clean_up(layer3=True, layer4=True, generic=True, port_5000=iszoom, port_5002=isyt, port_5003=isrb)
    if args.series_tests or args.parallel_tests:
        series_threads = []
        parallel_threads = []
        # Process series tests
        if args.series_tests:
            ordered_series_tests = args.series_tests.split(',')
            if args.dowebgui:
                gen_order = ["ping_test", "qos_test", "ftp_test", "http_test", "mcast_test", "vs_test", "thput_test", "yt_test", "rb_test", "zoom_test", "teams_test"]
                temp_ord_list = []
                for test_name in gen_order:
                    if test_name in ordered_series_tests:
                        temp_ord_list.append(test_name)
                ordered_series_tests = temp_ord_list.copy()
            for idx, test_name in enumerate(ordered_series_tests):
                test_name = test_name.strip().lower()
                if test_name in test_map:
                    func, label = test_map[test_name]
                    args.current = "series"
                    if test_name in ['rb_test', 'zoom_test', 'yt_test', 'teams_test']:
                        if test_name == "rb_test":
                            obj_no = 1
                            while f"rb_test_{obj_no}" in multi_traffic_obj.rb_obj_dict["series"]:
                                obj_no += 1
                            obj_name = f"rb_test_{obj_no}"
                            multi_traffic_obj.rb_obj_dict["series"][obj_name] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding rb_test object to parallel execution")
                        elif test_name == "yt_test":
                            obj_no = 1
                            while f"yt_test_{obj_no}" in multi_traffic_obj.yt_obj_dict["series"]:
                                obj_no += 1
                            obj_name = f"yt_test_{obj_no}"
                            multi_traffic_obj.yt_obj_dict["series"][obj_name] = manager.dict({"obj": None, "data": None})
                        elif test_name == "zoom_test":
                            obj_no = 1
                            while f"zoom_test_{obj_no}" in multi_traffic_obj.zoom_obj_dict["series"]:
                                obj_no += 1
                            obj_name = f"zoom_test_{obj_no}"
                            multi_traffic_obj.zoom_obj_dict["series"][obj_name] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding zoom_test object to parallel execution")
                        elif test_name == "teams_test":
                            obj_no = 1
                            while f"teams_test_{obj_no}" in multi_traffic_obj.teams_obj_dict["series"]:
                                obj_no += 1
                            obj_name = f"teams_test_{obj_no}"
                            multi_traffic_obj.teams_obj_dict["series"][obj_name] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding teams_test object to parallel execution")
                        series_threads.append(multiprocessing.Process(target=run_test_safe(func, f"{label} [Series {idx + 1}]", args, multi_traffic_obj, duration_dict[test_name])))
                    else:
                        series_threads.append(threading.Thread(
                            target=run_test_safe(func, f"{label} [Series {idx + 1}]", args, multi_traffic_obj, duration_dict[test_name])
                        ))
                else:
                    logging.warning(f"Unknown test '{test_name}' in --series_tests")

        # Process parallel tests
        if args.parallel_tests:
            """
            Process parallel test configurations, enforcing order when web GUI reporting is enabled.
            Initializes appropriate threading or multiprocessing workers based on test type requirements.
            """
            ordered_parallel_tests = args.parallel_tests.split(',')

            if args.dowebgui:
                gen_order = ["ping_test", "qos_test", "ftp_test", "http_test", "mcast_test", "vs_test", "thput_test", "yt_test", "rb_test", "zoom_test", "teams_test"]
                ordered_parallel_tests = [t for t in gen_order if t in ordered_parallel_tests]

            for idx, test_name in enumerate(ordered_parallel_tests):
                test_name = test_name.strip().lower()
                if test_name in test_map:
                    func, label = test_map[test_name]
                    args.current = "parallel"
                    if test_name in ['rb_test', 'zoom_test', 'yt_test', 'teams_test']:
                        if test_name == "rb_test":
                            multi_traffic_obj.rb_obj_dict["parallel"]["rb_test"] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding rb_test object to parallel execution")
                        elif test_name == "yt_test":
                            multi_traffic_obj.yt_obj_dict["parallel"]["yt_test"] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding yt_test object to parallel execution")
                        elif test_name == "zoom_test":
                            multi_traffic_obj.zoom_obj_dict["parallel"]["zoom_test"] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding zoom_test object to parallel execution")
                        elif test_name == "teams_test":
                            multi_traffic_obj.teams_obj_dict["parallel"]["teams_test"] = manager.dict({"obj": None, "data": None})
                            logging.debug("Adding teams_test object to parallel execution")

                        parallel_threads.append(multiprocessing.Process(
                            target=run_test_safe(func, f"{label} [Parallel {idx + 1}]", args, multi_traffic_obj, duration_dict[test_name])
                        ))
                    else:
                        parallel_threads.append(threading.Thread(
                            target=run_test_safe(func, f"{label} [Parallel {idx + 1}]", args, multi_traffic_obj, duration_dict[test_name])
                        ))
                else:
                    logging.warning(f"Unknown test '{test_name}' in --parallel_tests")

        if args.dowebgui:
            """
            Initialize overall execution status and tracking CSV for Web GUI reporting.
            """
            multi_traffic_obj.overall_status = {
                "ping": "notstarted", "qos": "notstarted", "ftp": "notstarted", "http": "notstarted",
                "mc": "notstarted", "vs": "notstarted", "thput": "notstarted", "rb": "notstarted",
                "zoom": "notstarted", "yt": "notstarted", "teams": "notstarted",
                "time": datetime.datetime.now().strftime("%Y %d %H:%M:%S"),
                "status": "running", "current_mode": "tbd", "current_test_name": "tbd"
            }
            multi_traffic_obj.overall_csv.append(multi_traffic_obj.overall_status.copy())
            df1 = pd.DataFrame(multi_traffic_obj.overall_csv)
            df1.to_csv(f'{args.result_dir}/overall_status.csv', index=False)

        """
        Execute scheduled test scenarios sequentially and/or in parallel according to priority.
        """
        if args.order_priority == 'series':
            multi_traffic_obj.current_exec = "series"
            for t in series_threads:
                t.start()
                t.join()
                multi_traffic_obj.series_index += 1

            # Then run parallel tests
            if parallel_threads:
                multi_traffic_obj.misc_clean_up(layer3=True, layer4=True, generic=True, port_5000=iszoom, port_5002=isyt, port_5003=isrb)
                logging.info('Starting parallel tests...')
                time.sleep(10)

            multi_traffic_obj.current_exec = "parallel"
            for t in parallel_threads:
                t.start()

            multi_traffic_obj.parallel_index = 0
            for t in parallel_threads:
                t.join()
                multi_traffic_obj.parallel_index += 1

        else:
            multi_traffic_obj.current_exec = "parallel"
            for t in parallel_threads:
                t.start()

            for t in parallel_threads:
                t.join()

            if series_threads:
                multi_traffic_obj.misc_clean_up(layer3=True, layer4=True, generic=True, port_5000=iszoom, port_5002=isyt, port_5003=isrb)
                logging.info('Starting series tests...')
                time.sleep(5)

            multi_traffic_obj.current_exec = "series"
            for t in series_threads:
                t.start()
                t.join()
    else:
        logger.error("Provide either --parallel_tests or --series_tests")
        exit(1)

    """
    Finalize test execution: perform cleanup, save logs, generate the overall report,
    and update the Web GUI status if applicable.
    """
    multi_traffic_obj.misc_clean_up(layer3=True, layer4=True, generic=True, port_5000=iszoom, port_5002=isyt, port_5003=isrb)
    log_file = save_logs()
    logging.info(f"Logs saved to: {log_file}")

    test_results_df = pd.DataFrame(list(test_results_list))
    multi_traffic_obj.generate_overall_report(test_results_df=test_results_df, args_dict=args_dict)

    if multi_traffic_obj.dowebgui:
        try:
            multi_traffic_obj.overall_status["status"] = "completed"
            multi_traffic_obj.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
            multi_traffic_obj.overall_csv.append(multi_traffic_obj.overall_status.copy())
            df1 = pd.DataFrame(multi_traffic_obj.overall_csv)
            df1.to_csv(f'{multi_traffic_obj.result_dir}/overall_status.csv', index=False)
        except Exception as e:
            logging.error(f"Error while writing status file for webui: {e}")

    logging.info(f"\nTest Results Summary:\n{test_results_df}")


def run_test_safe(test_func, test_name, args, multi_traffic_obj, duration):
    """
    Creates a safe wrapper around a test function to capture execution status and exceptions.

    Args:
        test_func (callable): The test function to execute.
        test_name (str): The name of the test being executed.
        args (object): The arguments passed to the test function.
        multi_traffic_obj (object): The MultiTraffic instance passed to the test function.
        duration (int/str): The duration of the test run.

    Returns:
        callable: A wrapper function that safely executes the test and logs results.
    """
    global error_logs  # noqa: F824

    def wrapper():
        """Executes the test function and captures its result or error state."""
        global error_logs  # noqa: F824

        try:
            result = test_func(args, multi_traffic_obj)
            if not result:
                status = "NOT EXECUTED"
                logger.error(f"{test_name} NOT EXECUTED")
            else:
                status = "EXECUTED"
                logger.info(f"{test_name} EXECUTED")

            test_results_list.append({"test_name": test_name, "Duration": duration, "status": status})

        except SystemExit as e:
            if e.code != 0:
                status = "NOT EXECUTED"
            else:
                status = "EXECUTED"
            tb = traceback.format_exc()
            print(tb)
            error_msg = f"{test_name} exited with code {e.code}\n"
            logger.error(error_msg)
            error_logs += error_msg
            test_results_list.append({"test_name": test_name, "Duration": duration, "status": status})

        except Exception:
            status = "NOT EXECUTED"
            error_msg = f"{test_name} crashed unexpectedly\n"
            logger.exception(error_msg)
            tb_str = traceback.format_exc()
            full_error = error_msg + tb_str + "\n"
            error_logs += full_error
            test_results_list.append({"test_name": test_name, "Duration": duration, "status": status})

    return wrapper


def save_logs():
    """
    Saves accumulated error logs to a timestamped file in the 'base_class_logs' directory.

    Returns:
        str: The path to the newly created log file.
    """
    global error_logs  # noqa: F824

    # Ensure the target directory exists
    log_dir = "base_class_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate a timestamp for a unique file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_dir}/test_logs_{timestamp}.txt"

    # Dump accumulated logs
    with open(log_filename, 'w') as f:
        f.write(error_logs)

    logger.info(f"Test logs saved to {log_filename}")
    return log_filename


def run_ping_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a ping test using the provided arguments."""
    return multi_traffic_obj.run_ping_test(
        real=True,
        target=args.ping_target,
        ping_interval=args.ping_interval,
        ping_duration=args.ping_duration,
        use_default_config=False if args.ping_config else True,
        dev_list=args.ping_device_list,
        expected_passfail_value=args.ping_expected_passfail_value,
        device_csv_name=args.ping_device_csv_name,
        file_name=args.ping_file_name,
        group_name=args.ping_group_name,
        profile_name=args.ping_profile_name,
        ssid=args.ping_ssid,
        passwd=args.ping_passwd,
        security=args.ping_security,
        eap_method=args.ping_eap_method,
        eap_identity=args.ping_eap_identity,
        ieee8021x=args.ping_ieee8021x,
        ieee80211u=args.ping_ieee80211u,
        ieee80211w=args.ping_ieee80211w,
        enable_pkc=args.ping_enable_pkc,
        bss_transition=args.ping_bss_transition,
        power_save=args.ping_power_save,
        disable_ofdma=args.ping_disable_ofdma,
        roam_ft_ds=args.ping_roam_ft_ds,
        key_management=args.ping_key_management,
        pairwise=args.ping_pairwise,
        private_key=args.ping_private_key,
        ca_cert=args.ping_ca_cert,
        client_cert=args.ping_client_cert,
        pk_passwd=args.ping_pk_passwd,
        pac_file=args.ping_pac_file,
        wait_time=args.ping_wait_time,
        local_lf_report_dir=multi_traffic_obj.result_path if not args.dowebgui else args.result_dir,
        do_bandsteering=args.do_bandsteering,
        cycles=args.cycles,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip,
        robot_test=args.robot_test
    )


def run_http_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a http test using the provided arguments."""
    return multi_traffic_obj.run_http_test(
        upstream_port=args.upstream_port,
        bands=args.http_bands,
        duration=args.http_duration,
        file_size=args.http_file_size,
        device_list=args.http_device_list,
        expected_passfail_value=args.http_expected_passfail_value,
        device_csv_name=args.http_device_csv_name,
        file_name=args.http_file_name,
        group_name=args.http_group_name,
        profile_name=args.http_profile_name,
        config=args.http_config,
        ssid=args.http_ssid,
        passwd=args.http_passwd,
        security=args.http_security,
        eap_method=args.http_eap_method,
        eap_identity=args.http_eap_identity,
        ieee8021x=args.http_ieee8021x,
        ieee80211u=args.http_ieee80211u,
        ieee80211w=args.http_ieee80211w,
        enable_pkc=args.http_enable_pkc,
        bss_transition=args.http_bss_transition,
        power_save=args.http_power_save,
        disable_ofdma=args.http_disable_ofdma,
        roam_ft_ds=args.http_roam_ft_ds,
        key_management=args.http_key_management,
        pairwise=args.http_pairwise,
        private_key=args.http_private_key,
        ca_cert=args.http_ca_cert,
        client_cert=args.http_client_cert,
        pk_passwd=args.http_pk_passwd,
        pac_file=args.http_pac_file,
        wait_time=args.http_wait_time,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir,
        do_bandsteering=args.do_bandsteering,
        cycles=args.cycles,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip
    )


def run_ftp_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a ftp test using the provided arguments."""
    return multi_traffic_obj.run_ftp_test(
        device_list=args.ftp_device_list,
        file_sizes=[args.ftp_file_size],
        traffic_duration=args.ftp_duration,
        bands=args.ftp_bands,
        expected_passfail_value=args.ftp_expected_passfail_value,
        device_csv_name=args.ftp_device_csv_name,
        file_name=args.ftp_file_name,
        group_name=args.ftp_group_name,
        profile_name=args.ftp_profile_name,
        config=args.ftp_config,
        ssid=args.ftp_ssid,
        passwd=args.ftp_passwd,
        security=args.ftp_security,
        eap_method=args.ftp_eap_method,
        eap_identity=args.ftp_eap_identity,
        ieee8021x=args.ftp_ieee8021x,
        ieee80211u=args.ftp_ieee80211u,
        ieee80211w=args.ftp_ieee80211w,
        enable_pkc=args.ftp_enable_pkc,
        bss_transition=args.ftp_bss_transition,
        power_save=args.ftp_power_save,
        disable_ofdma=args.ftp_disable_ofdma,
        roam_ft_ds=args.ftp_roam_ft_ds,
        key_management=args.ftp_key_management,
        pairwise=args.ftp_pairwise,
        private_key=args.ftp_private_key,
        ca_cert=args.ftp_ca_cert,
        client_cert=args.ftp_client_cert,
        pk_passwd=args.ftp_pk_passwd,
        pac_file=args.ftp_pac_file,
        wait_time=args.ftp_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir,
        upstream_port=args.upstream_port,
        do_bandsteering=args.do_bandsteering,
        cycles=args.cycles,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip
    )


def run_qos_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a qos test using the provided arguments."""
    return multi_traffic_obj.run_qos_test(
        upstream_port=args.upstream_port,
        test_duration=args.qos_duration,
        download=args.qos_download,
        upload=args.qos_upload,
        traffic_type=args.qos_traffic_type,
        tos=args.qos_tos,
        device_list=args.qos_device_list,
        expected_passfail_value=args.qos_expected_passfail_value,
        device_csv_name=args.qos_device_csv_name,
        file_name=args.qos_file_name,
        group_name=args.qos_group_name,
        profile_name=args.qos_profile_name,
        config=args.qos_config,
        ssid=args.qos_ssid,
        passwd=args.qos_passwd,
        security=args.qos_security,
        eap_method=args.qos_eap_method,
        eap_identity=args.qos_eap_identity,
        ieee8021x=args.qos_ieee8021x,
        ieee80211u=args.qos_ieee80211u,
        ieee80211w=args.qos_ieee80211w,
        enable_pkc=args.qos_enable_pkc,
        bss_transition=args.qos_bss_transition,
        power_save=args.qos_power_save,
        disable_ofdma=args.qos_disable_ofdma,
        roam_ft_ds=args.qos_roam_ft_ds,
        key_management=args.qos_key_management,
        pairwise=args.qos_pairwise,
        private_key=args.qos_private_key,
        ca_cert=args.qos_ca_cert,
        client_cert=args.qos_client_cert,
        pk_passwd=args.qos_pk_passwd,
        pac_file=args.qos_pac_file,
        wait_time=args.qos_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir,
        do_bandsteering=args.do_bandsteering,
        cycles=args.cycles,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip
    )


def run_vs_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a video streaming test using the provided arguments."""
    return multi_traffic_obj.run_vs_test1(
        url=args.vs_url,
        media_source=args.vs_media_source,
        media_quality=args.vs_media_quality,
        duration=args.vs_duration,
        device_list=args.vs_device_list,
        expected_passfail_value=args.vs_expected_passfail_value,
        device_csv_name=args.vs_device_csv_name,
        file_name=args.vs_file_name,
        group_name=args.vs_group_name,
        profile_name=args.vs_profile_name,
        config=args.vs_config,
        ssid=args.vs_ssid,
        passwd=args.vs_passwd,
        encryp=args.vs_security,
        eap_method=args.vs_eap_method,
        eap_identity=args.vs_eap_identity,
        ieee8021x=args.vs_ieee8021x,
        ieee80211u=args.vs_ieee80211u,
        ieee80211w=args.vs_ieee80211w,
        enable_pkc=args.vs_enable_pkc,
        bss_transition=args.vs_bss_transition,
        power_save=args.vs_power_save,
        disable_ofdma=args.vs_disable_ofdma,
        roam_ft_ds=args.vs_roam_ft_ds,
        key_management=args.vs_key_management,
        pairwise=args.vs_pairwise,
        private_key=args.vs_private_key,
        ca_cert=args.vs_ca_cert,
        client_cert=args.vs_client_cert,
        pk_passwd=args.vs_pk_passwd,
        pac_file=args.vs_pac_file,
        wait_time=args.vs_wait_time,
        upstream_port=args.upstream_port,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir,
        do_bandsteering=args.do_bandsteering,
        total_cycles=args.cycles,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip
    )


def run_thput_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a throughput test using the provided arguments."""
    if args.thput_do_interopability and args.thput_config:
        args.thput_default_config = False
        args.thput_config = False
    elif args.thput_do_interopability:
        args.thput_default_config = True
    return multi_traffic_obj.run_throughput_test(
        upstream_port=args.upstream_port,
        test_duration=args.thput_test_duration,
        download=args.thput_download,
        upload=args.thput_upload,
        traffic_type=args.thput_traffic_type,
        device_list=args.thput_device_list,
        do_interopability=args.thput_do_interopability,
        default_config=args.thput_default_config,
        expected_passfail_value=args.thput_expected_passfail_value,
        device_csv_name=args.thput_device_csv_name,
        file_name=args.thput_file_name,
        group_name=args.thput_group_name,
        profile_name=args.thput_profile_name,
        config=args.thput_config,
        ssid=args.thput_ssid,
        passwd=args.thput_passwd,
        security=args.thput_security,
        eap_method=args.thput_eap_method,
        eap_identity=args.thput_eap_identity,
        ieee8021x=args.thput_ieee8021x,
        ieee80211u=args.thput_ieee80211u,
        ieee80211w=args.thput_ieee80211w,
        enable_pkc=args.thput_enable_pkc,
        bss_transition=args.thput_bss_transition,
        power_save=args.thput_power_save,
        disable_ofdma=args.thput_disable_ofdma,
        roam_ft_ds=args.thput_roam_ft_ds,
        key_management=args.thput_key_management,
        pairwise=args.thput_pairwise,
        private_key=args.thput_private_key,
        ca_cert=args.thput_ca_cert,
        client_cert=args.thput_client_cert,
        pk_passwd=args.thput_pk_passwd,
        pac_file=args.thput_pac_file,
        wait_time=args.thput_wait_time,
        load_type=args.thput_load_type,
        packet_size=args.thput_packet_size,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir,
        do_bandsteering=args.do_bandsteering,
        total_cycles=args.cycles,
        duration_to_skip=args.duration_to_skip,
        bssids=args.bssids.split(",") if args.bssids else []
    )


def run_mcast_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a mukticast test using the provided arguments."""
    return multi_traffic_obj.run_mc_test1(
        test_duration=args.mcast_test_duration,
        upstream_port=args.upstream_port,
        endp_type=args.mcast_endp_type,
        side_b_min_bps=args.mcast_side_b_min_bps,
        tos=args.mcast_tos,
        device_list=args.mcast_device_list,
        expected_passfail_value=args.mcast_expected_passfail_value,
        device_csv_name=args.mcast_device_csv_name,
        file_name=args.mcast_file_name,
        group_name=args.mcast_group_name,
        profile_name=args.mcast_profile_name,
        config=args.mcast_config,
        ssid=args.mcast_ssid,
        passwd=args.mcast_passwd,
        security=args.mcast_security,
        eap_method=args.mcast_eap_method,
        eap_identity=args.mcast_eap_identity,
        ieee8021x=args.mcast_ieee8021x,
        ieee80211u=args.mcast_ieee80211u,
        ieee80211w=args.mcast_ieee80211w,
        enable_pkc=args.mcast_enable_pkc,
        bss_transition=args.mcast_bss_transition,
        power_save=args.mcast_ieee8021x,
        disable_ofdma=args.mcast_disable_ofdma,
        roam_ft_ds=args.mcast_roam_ft_ds,
        key_management=args.mcast_key_management,
        pairwise=args.mcast_pairwise,
        private_key=args.mcast_private_key,
        ca_cert=args.mcast_ca_cert,
        client_cert=args.mcast_client_cert,
        pk_passwd=args.mcast_pk_passwd,
        pac_file=args.mcast_pac_file,
        wait_time=args.mcast_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir
    )


def run_yt_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a Youtube test using the provided arguments."""
    return multi_traffic_obj.run_yt_test(
        url=args.yt_url,
        duration=args.yt_duration,
        res=args.yt_res,
        upstream_port=args.upstream_port,
        resource_list=args.yt_device_list,
        expected_passfail_value=args.yt_expected_passfail_value,
        device_csv_name=args.yt_device_csv_name,
        file_name=args.yt_file_name,
        group_name=args.yt_group_name,
        profile_name=args.yt_profile_name,
        config=args.yt_config,
        ssid=args.yt_ssid,
        passwd=args.yt_passwd,
        encryp=args.yt_security,
        eap_method=args.yt_eap_method,
        eap_identity=args.yt_eap_identity,
        ieee8021x=args.yt_ieee8021x,
        ieee80211u=args.yt_ieee80211u,
        ieee80211w=args.yt_ieee80211w,
        enable_pkc=args.yt_enable_pkc,
        bss_transition=args.yt_bss_transition,
        power_save=args.yt_ieee8021x,
        disable_ofdma=args.yt_disable_ofdma,
        roam_ft_ds=args.yt_roam_ft_ds,
        key_management=args.yt_key_management,
        pairwise=args.yt_pairwise,
        private_key=args.yt_private_key,
        ca_cert=args.yt_ca_cert,
        client_cert=args.yt_client_cert,
        pk_passwd=args.yt_pk_passwd,
        pac_file=args.yt_pac_file,
        exec_type=args.current,
        do_webUI="True" if args.dowebgui else False,
        ui_report_dir=args.result_dir,
        test_name=args.test_name
    )


def run_rb_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a real browser test using the provided arguments."""
    return multi_traffic_obj.run_rb_test(
        url=args.rb_url,
        upstream_port=args.upstream_port,
        device_list=args.rb_device_list,
        expected_passfail_value=args.rb_expected_passfail_value,
        device_csv_name=args.rb_device_csv_name,
        file_name=args.rb_file_name,
        group_name=args.rb_group_name,
        profile_name=args.rb_profile_name,
        config=args.rb_config,
        ssid=args.rb_ssid,
        passwd=args.rb_passwd,
        encryp=args.rb_security,
        eap_method=args.rb_eap_method,
        eap_identity=args.rb_eap_identity,
        ieee80211=args.rb_ieee80211,
        ieee80211u=args.rb_ieee80211u,
        ieee80211w=args.rb_ieee80211w,
        enable_pkc=args.rb_enable_pkc,
        bss_transition=args.rb_bss_transition,
        power_save=args.rb_power_save,
        disable_ofdma=args.rb_disable_ofdma,
        roam_ft_ds=args.rb_roam_ft_ds,
        key_management=args.rb_key_management,
        pairwise=args.rb_pairwise,
        private_key=args.rb_private_key,
        ca_cert=args.rb_ca_cert,
        client_cert=args.rb_client_cert,
        pk_passwd=args.rb_pk_passwd,
        pac_file=args.rb_pac_file,
        wait_time=args.rb_wait_time,
        duration=args.rb_duration,
        exec_type=args.current,
        count=args.rb_count,
        dowebgui=args.dowebgui,
        result_dir=args.result_dir,
        test_name=args.test_name,
        webgui_incremental=args.rb_webgui_incremental
    )


def run_zoom_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a zoom test using the provided arguments."""
    return multi_traffic_obj.run_zoom_test(
        duration=args.zoom_duration,
        signin_email=args.zoom_signin_email,
        signin_passwd=args.zoom_signin_passwd,
        participants=args.zoom_participants,
        audio=args.zoom_audio,
        video=args.zoom_video,
        upstream_port=args.upstream_port,
        resource_list=args.zoom_device_list,
        zoom_host=args.zoom_host,
        expected_passfail_value=args.zoom_expected_passfail_value,
        device_csv_name=args.zoom_device_csv_name,
        file_name=args.zoom_file_name,
        group_name=args.zoom_group_name,
        profile_name=args.zoom_profile_name,
        config=args.zoom_config,
        ssid=args.zoom_ssid,
        passwd=args.zoom_passwd,
        encryp=args.zoom_security,
        eap_method=args.zoom_eap_method,
        eap_identity=args.zoom_eap_identity,
        ieee8021x=args.zoom_ieee8021x,
        ieee80211u=args.zoom_ieee80211u,
        ieee80211w=args.zoom_ieee80211w,
        enable_pkc=args.zoom_enable_pkc,
        bss_transition=args.zoom_bss_transition,
        power_save=args.zoom_power_save,
        disable_ofdma=args.zoom_disable_ofdma,
        roam_ft_ds=args.zoom_roam_ft_ds,
        key_management=args.zoom_key_management,
        pairwise=args.zoom_pairwise,
        private_key=args.zoom_private_key,
        ca_cert=args.zoom_ca_cert,
        client_cert=args.zoom_client_cert,
        pk_passwd=args.zoom_pk_passwd,
        pac_file=args.zoom_pac_file,
        wait_time=args.zoom_wait_time,
        exec_type=args.current,
        do_webUI=args.dowebgui,
        report_dir=args.result_dir,
        testname=args.test_name,
        env_file=args.env_file,
        api_stats_collection=args.api_stats_collection,
        client_id=args.client_id,
        client_secret=args.client_secret,
        account_id=args.account_id,
    )


def run_teams_test(args, multi_traffic_obj: MultiTraffic):
    """Executes a teams test using the provided arguments."""
    is_robot = args.robot_test and not args.do_bandsteering
    return multi_traffic_obj.run_teams_test(
        duration=args.teams_duration,
        resources=args.teams_device_list,
        audio=args.teams_audio,
        video=args.teams_video,
        do_webUI=args.dowebgui,
        testname=args.test_name,
        report_dir=args.result_dir,
        enable_mobile_stats=args.teams_enable_mobile_stats,
        robo_ip=args.robot_ip,
        coordinates=args.coordinate,
        rotations=args.rotation,
        do_robo=is_robot,
        do_bs=args.do_bandsteering,
        cycles=args.cycles,
        bssids=args.bssids,
        upstream_port=args.upstream_port,
    )


if __name__ == "__main__":
    main()
