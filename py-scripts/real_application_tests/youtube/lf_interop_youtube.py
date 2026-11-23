#!/usr/bin/env python3
"""
    NAME: lf_interop_youtube.py

    PURPOSE: lf_interop_youtube.py provides the available devices and allows the user to run YouTube on selected devices by specifying the video URL and duration.

    EXAMPLE-1:
    Command Line Interface to run YouTube with the specified URL and duration:
    python3 lf_interop_youtube.py \
    --mgr 192.168.214.219 \
    --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --duration 1 \
    --res 1080p \
    --upstream_port 1.1.eth1

        CASE-1:
        If the given duration is longer than the actual video duration, the video will loop.

        CASE-2:
        If the given duration is shorter than the actual video duration, the video will stop after the specified duration.

    EXAMPLE-2:
    Command Line Interface to run YouTube on multiple devices:
    python3 lf_interop_youtube.py \
    --mgr 192.168.214.219 \
    --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --duration 2 \
    --res 1080p \
    --upstream_port 1.1.eth1 \
    --resources 1.13,1.14


    EXAMPLE-3:
    Command Line Interface to run YouTube without post-cleanup of cross-connections:
    python3 lf_interop_youtube.py \
    --mgr 192.168.214.219 \
    --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --duration 2 \
    --res 1080p \
    --upstream_port 1.1.eth1 \
    --resources 1.13,1.14 \
    --no_post_cleanup

    EXAMPLE-4:
    Command Line Interface to run YouTube with multiple groups and profiles:
    python3 lf_interop_youtube.py --mgr 192.168.204.74 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1
    --group_name group1,group2 --profile_name netgear5g,netgear2g --file_name grplaptops.csv --upstream_port 1.1.eth1

    EXAMPLE-5:
    Command Line Interface to run YouTube with Device Configuration:
    python3 lf_interop_youtube.py --mgr 192.168.204.74 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1
    --ssid NETGEAR_2g_wpa2 --passwd Password@123 --encryp wpa2 --upstream_port 1.1.eth1 --config

    EXAMPLE-6:
    Command Line Interface to run the Test along with IOT without device list
    python3 lf_interop_youtube.py --mgr 192.168.207.78 --url https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1 --duration 1
    --test_name Youtube --res 144p --upstream_port 192.168.200.191 --iot_test --iot_testname "youtubeIot"

    EXAMPLE-7:
    Command Line Interface to run the Test along with IOT with device list
    python3 lf_interop_youtube.py --mgr 192.168.207.78 --url https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1 --duration 1
    --test_name Youtube --res 144p --upstream_port 192.168.200.191 --iot_test --iot_testname "youtubeIot" --iot_device_list "switch.smart_plug_1_socket_1"

    Example-8:
    Command Line Interface to run the new Test at each coordinate with Robo

    python3 lf_interop_youtube.py \
    --mgr 192.168.214.219 \
    --upstream_port 1.1.eth1 \
    --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --duration 1 \
    --res 1080p \
    --resources 1.13,1.14 \
    --do_robo \
    --robo_ip 192.168.50.10 \
    --coordinates c1,c2,c3


    Example-9:
    Command Line Interface to run the new Test with Robo and rotating to user specified angles at each coordinate

    python3 py-scripts/real_application_tests/youtube/lf_interop_youtube.py \
    --mgr 192.168.214.219 \
    --upstream_port 1.1.eth1 \
    --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
    --duration 1 \
    --res 1080p \
    --resources 1.13,1.14 \
    --do_robo \
    --robo_ip 192.168.50.10 \
    --coordinates c1,c2,c3 \
    --rotations 0,90,180,270

    Example-9:
    Command Line Interface to run the Test with Robo bandsteering
    python3 lf_interop_youtube.py --mgr 192.168.207.78 --url "https://youtu.be/BHACKCNDMW8?si=mjPduPJ5a7KmCUAS" --duration 1  --upstream_port 192.168.204.90 --res 144p
    --do_robo --robo_ip 192.168.200.101 --coordinates 3,2,1 --rotations "" --robot_wait_duration 1 --do_bandsteering --cycles 2
    --bssids 94:A6:7E:74:26:22,94:A6:7E:74:26:31

    Example-10:
    Command Line Interface to run the Test while the robot moves through the points (continuous robot run, no band steering)
    python3 lf_interop_youtube.py --mgr 192.168.207.78 --url "https://youtu.be/BHACKCNDMW8?si=mjPduPJ5a7KmCUAS" --upstream_port 192.168.204.90 --res 144p
    --do_robo --robo_ip 192.168.200.101 --coordinates 3,2,1 --robot_wait_duration 1 --measurement_mode continuous --cycles 2



    SCRIPT CLASSIFICATION: Test

    NOTES:
    1. Use './lf_interop_youtube.py --help' to see command line usage and options.
    2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
    3. If --resources are not given after passing the CLI, a list of available devices (laptops) will be displayed on the terminal.
    4. Enter the resource numbers separated by commas (,) in the resource argument.
    5. For --url, you can specify the YouTube URL (e.g., https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1).

"""
import argparse
import time
import sys
import os
import pandas as pd
import importlib
import logging
import csv
import asyncio
import json
import shutil
import glob
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import pickle
from threading import Event, Lock, Thread
import traceback
import platform
import signal
import shlex
import subprocess
from collections import Counter
from html import escape
import re
from urllib import error as urllib_error
from urllib import request as urllib_request
logger = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
YOUTUBE_STATS_URL = "http://127.0.0.1:5002/youtube_stats"

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../py-json")))


# Import LANforge-related modules

# Import LF logger configuration module
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

# Import realm module
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

# Import base interop profile module
base = importlib.import_module('py-scripts.lf_base_interop_profile')
base_RealDevice = base.RealDevice

DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")

# Importing report and LANforge modules
from report_v2.lf_report_v2 import lf_report  # noqa: E402
from report_v2.lf_graph_v2 import lf_bar_graph, lf_bar_graph_horizontal  # noqa: E402
lf_base_interop_profile = importlib.import_module("py-scripts.lf_base_interop_profile")
robo_base_class = importlib.import_module("py-scripts.lf_base_robo")
lf_interop_ping = importlib.import_module("py-scripts.lf_interop_ping")
ClientAnalysis = importlib.import_module("py-scripts.lf_wifi_msgs").ClientAnalysis

# Accessing specific classes
InteropPing = lf_interop_ping.Ping
RealDevice = lf_base_interop_profile.RealDevice

from IOT.iot_helper import start_iot_thread, with_iot_params_in_table, add_iot_report_section  # noqa: E402

WINDOWS_REAL_APP_DIR = r".\local\real_application_test\youtube"
LINUX_REAL_APP_DIR = "./local/real_application_test/youtube"
MACOS_REAL_APP_DIR = "./local/real_application_test/youtube"
YOUTUBE_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANDROID_TEST_SCRIPT = os.path.join(
    YOUTUBE_SCRIPT_DIR,
    "youtube_android_test.py",
)


class WebUIStopRequested(Exception):
    """Unwind the active test loop and continue through final reporting."""


class AllEndpointsUnreachable(Exception):
    """Unwind after every monitored endpoint is absent for 40 seconds."""


class Youtube(Realm):
    """
    Class for automating YouTube streaming tests using LANforge.
    """

    def __init__(self,
                 host=None,
                 port=None,
                 url=None,
                 duration=0,
                 lanforge_password='lanforge',
                 sta_list=None,
                 do_webUI=False,
                 ui_report_dir=None,
                 debug=False,
                 stats_api_response=None,
                 resolution=None,
                 ap_name=None,
                 ssid=None,
                 security=None,
                 band=None,
                 base_dir=None,
                 test_name=None,
                 upstream_port=None,
                 config=None,
                 selected_groups=None,
                 selected_profiles=None,
                 config_obj=None,
                 robo_ip="127.0.0.1",
                 coordinates_list=None,
                 angles_list=None,
                 do_robo=False,
                 cycles=None,
                 bssids=None,
                 do_bandsteering=False,
                 measurement_mode="per_point",
                 current_cord="",
                 current_angle="NA",
                 rotations_enabled=False,
                 scoring=False,
                 windows_dir=WINDOWS_REAL_APP_DIR,
                 linux_dir=LINUX_REAL_APP_DIR,
                 mac_dir=MACOS_REAL_APP_DIR
                 ):
        """
        Initialize the YouTube streaming test parameters.
        Args:
            host (str): Hostname or IP address of the LANforge GUI.
            port (int): Port number for LANforge HTTP service.
            url (str): YouTube URL for streaming.
            duration (int): Duration of the test in seconds.
            lanforge_password (str): LANforge password for authentication.
            sta_list (list): List of station names or identifiers.
            do_webUI (bool): Flag indicating if triggered from LANforge webUI.
            ui_report_dir (str): Directory path to store webUI reports.
            debug (bool): Enable debugging output if True.
            stats_api_response (dict): Placeholder for API response statistics.
            windows_dir (str): YouTube application directory on Windows clients.
            linux_dir (str): YouTube application directory on Linux clients.
            mac_dir (str): YouTube application directory on macOS clients.
        """
        super().__init__(lfclient_host=host,
                         lfclient_port=port)
        self.host = host
        self.lanforge_password = lanforge_password
        self.port = port
        self.url = url
        self.duration = duration
        self.lfclient_host = host
        self.lfclient_port = port
        self.debug = debug
        self.scoring = scoring
        self.windows_dir = windows_dir
        self.linux_dir = linux_dir
        self.mac_dir = mac_dir
        self.sta_list = sta_list
        self.real_sta_list = []
        self.real_sta_data_dict = {}
        self.linux = 0
        self.windows = 0
        self.mac = 0
        self.to_coordinate = ""
        self.from_coordinate = ""
        self.result_json = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'youtube'
        self.generic_endps_profile.name_prefix = "yt"
        self.endpoint_last_status = {}
        self.Devices = None
        self.start_time = None
        self.stop_time = None
        self.do_webUI = do_webUI
        self.ui_report_dir = ui_report_dir
        self.devices = base_RealDevice(manager_ip=self.host, selected_bands=[])
        self.device_names = []
        self.resolution = resolution
        self.do_bandsteering = do_bandsteering
        # measurement mode: 'per_point' plays at each point, 'continuous' keeps the video playing while the robot moves.
        # Band steering always moves continuously; do_bandsteering only adds the BSSID tracking report.
        self.is_continuous_run = do_bandsteering or (do_robo and measurement_mode == "continuous")
        self.bssids = bssids or []
        self.ap_name = ap_name
        self.ssid = ssid
        self.security = security
        self.band = band
        self.est_end_time = None
        self.all_stop = False
        self.keys = []
        self.hostname_os_combination = None
        self.test_name = test_name
        if self.do_webUI:
            self.base_dir = os.path.abspath(os.path.join(ui_report_dir, "../../"))
            self.test_name = test_name

        self.final_data = None
        self.stats_api_response = {}
        self.upstream_port = upstream_port
        self.stop_signal = False
        self.config = config
        self.selected_groups = selected_groups
        self.selected_profiles = selected_profiles
        self.config_obj = config_obj
        self.serial_list = []
        self.user_list = []
        self.lanforge_port_list = set()
        self.lanforge_os_type = list()
        self.android = 0
        self.android_log_received = Event()
        self.playback_stats_lock = Lock()
        self.playback_stats_start_time = None
        self.playback_stats_end_time = None
        self.windowed_ping_stats = None
        self.connectivity_started = False
        self.connectivity_end_time = None
        self.background_ping = None
        self.wifi_interface_list = []
        self.devices_list = []
        self.hostname_to_station_map = {}
        self.csv_headers = [
            "Instance Name", "TimeStamp", "Viewport", "DroppedFrames",
            "TotalFrames", "CurrentRes", "OptimalRes", "BufferHealth",
            "VideoCodec", "AudioCodec", "ConnectionSpeedKbps",
            "NetworkActivityKB", "LiveLatency(sec)", "bandwidth (kbps)"
        ]
        if do_robo and not self.is_continuous_run:
            self.csv_headers.append("Angle")
        if self.is_continuous_run:
            self.csv_headers.extend([
                "BSSID", "Channel", "X", "Y", "From_Coord", "To_Coord"
            ])

        self.do_robo = do_robo
        self.robo_ip = robo_ip
        self.coordinates_list = coordinates_list or []
        self.angles_list = angles_list or []
        self.current_cord = current_cord
        self.current_angle = current_angle
        self.rotations_enabled = rotations_enabled
        self.pause = False
        self.cycles = cycles
        if self.do_robo:
            self.robo_obj = robo_base_class.RobotClass(
                robo_ip=self.robo_ip,
                angle_list=angles_list
            )

    def stop(self):
        self.stop_signal = True

    def cleanup(self):
        """
        Cleans up generic endpoints associated with the YouTube streaming test.

        This method iterates through the list of real stations (STA) and appends
        corresponding endpoint names to the `created_cx` and `created_endp` lists
        of the `generic_endps_profile`. It then performs cleanup operations on
        these endpoints and clears the lists afterwards.

        """
        # Append CX and endpoint names for each real station to be cleaned up
        for station in self.real_sta_list:
            self.generic_endps_profile.created_cx.append(
                'CX_yt-{}'.format(station))
            self.generic_endps_profile.created_endp.append(
                'yt-{}'.format(station))

        # Log cleanup initiation
        # Perform cleanup on generic endpoints
        self.generic_endps_profile.cleanup()
        # Clear the lists of created CX and endpoints after cleanup
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []
        # Log cleanup completion

    def check_tab_exists(self):
        """
        Checks if the 'generic' tab exists by making a JSON GET request.
        Returns:
        - True if the 'generic' tab exists (response is not None).
        - False if the 'generic' tab does not exist (response is None).
        """
        # Make a JSON GET request to check the existence of the 'generic' tab
        response = self.json_get("generic")
        # Check if the response is None (indicating the tab does not exist)
        if response is None:
            return False
        else:
            return True

    def generic_endpoint_exists(self, endpoint_name):
        """Return whether LANforge currently has the generic endpoint."""
        response = self.json_get(f"/generic/{endpoint_name}")
        return bool(response and "endpoint" in response)

    def pre_cleanup_stale_youtube_endpoints(self, ports):
        """Remove stale YouTube CX/endpoint pairs before creating them.

        YouTube creates desktop and Android LANforge endpoints through
        GenCXProfile.create() with real-client OS types, so both use names
        based on the complete port EID, for example ``yt-1.40.wlan0`` and
        ``CX_yt-1.40.wlan0``.
        """
        prefix = self.generic_endps_profile.name_prefix
        for port_name in ports:
            endpoint_name = f"{prefix}-{port_name}"
            cx_name = f"CX_{prefix}-{port_name}"

            if not self.generic_endpoint_exists(endpoint_name):
                continue

            logging.info(
                "Removing stale YouTube CX %s before endpoint creation",
                cx_name,
            )
            self.json_post(
                "cli-json/rm_cx",
                {"test_mgr": "default_tm", "cx_name": cx_name},
            )
            logging.info(
                "Removing stale YouTube endpoint %s before endpoint creation",
                endpoint_name,
            )
            self.json_post(
                "cli-json/rm_endp",
                {"endp_name": endpoint_name},
            )

    def create_generic_endp(self):
        """
        Create and configure generic endpoints for real client YouTube tests.

        This method creates generic endpoints for all real client stations defined
        in `self.real_sta_list` using the generic endpoints profile. Once endpoints
        are successfully created, it assigns an OS-specific YouTube streaming
        command to each endpoint based on the client operating system.

        Behavior:
        - Creates generic endpoints with a small delay between creations
        - Applies different execution commands for Windows, Linux, and macOS clients
        - Associates each command with the corresponding created endpoint

        OS-specific command handling:
        - Windows: Executes 'youtube_stream.bat'
        - Linux: Executes 'ctyt.bash' as the 'lanforge' user
        - macOS: Executes 'ctyt.bash' as the 'lanforge' user

        Dependencies:
        - self.real_sta_list: List of real client stations
        - self.real_sta_os_types: Operating system type for each client
        - self.real_sta_hostname: Hostnames for real clients
        - self.generic_endps_profile: Generic endpoint profile object
        - self.wifi_interface_list: Wifi interface names used for Linux clients

        Side Effects:
        - Creates generic endpoints via the profile
        - Sets execution commands for each created endpoint
        - Terminates the process if endpoint creation fails

        Returns:
            None
        """
        self.get_device_data()
        self.get_android_device_data()
        self.process_device_data()

        self.pre_cleanup_stale_youtube_endpoints(self.real_sta_list)
        if self.generic_endps_profile.create(ports=self.real_sta_list, sleep_time=.5, real_client_os_types=self.real_sta_os_types,):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        for i in range(0, len(self.real_sta_os_types)):
            if self.real_sta_os_types[i] == 'windows':
                cmd = (
                    fr'"{self.windows_dir}\youtube_stream.bat" '
                    '--url "%s" --host "%s" --device_name "%s" --duration %s --res "%s"'
                    % (
                        self.url,
                        self.upstream_port,
                        self.real_sta_hostname[i],
                        self.duration,
                        self.resolution,
                    )
                )
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_types[i] == 'linux':
                linux_command = " ".join(shlex.quote(str(argument)) for argument in [
                    os.path.join(self.linux_dir, "ctyt.bash"),
                    self.wifi_interface_list[i],
                    self.url,
                    self.upstream_port,
                    self.real_sta_hostname[i],
                    self.duration,
                    self.resolution,
                ])
                cmd = f"su -l lanforge -c {shlex.quote(linux_command)}"
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

            elif self.real_sta_os_types[i] == 'macos':
                cmd = " ".join(shlex.quote(str(argument)) for argument in [
                    "sudo", "-H", "-u", "lanforge", "bash",
                    os.path.join(self.mac_dir, "ctyt.bash"),
                    "--url",
                    self.url,
                    "--host",
                    self.upstream_port,
                    "--device_name",
                    self.real_sta_hostname[i],
                    "--duration",
                    self.duration,
                    "--res",
                    self.resolution,
                ])
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

        self.pre_cleanup_stale_youtube_endpoints(self.lanforge_port_list)
        if self.generic_endps_profile.create(ports=self.lanforge_port_list, sleep_time=.5, real_client_os_types=self.lanforge_os_type,):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        for i in range(0, len(self.lanforge_os_type)):
            cmd = (
                "su - lanforge -c "
                "\"cd '%s' && "
                "python3 '%s' "
                "--url '%s' --duration '%s' --devices '%s' --upstream_port '%s' --resolution '%s'\""
            ) % (
                YOUTUBE_SCRIPT_DIR,
                ANDROID_TEST_SCRIPT,
                self.url,
                self.duration,
                self.serial_list_str,
                self.host,
                self.resolution,
            )
            logging.info(
                "Configured YouTube streaming command for %d Android device(s)",
                len(self.lanforge_os_type),
            )
            logger.debug("Android YouTube command: %s", cmd)
            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[-(i + 1)], cmd)

    def select_real_devices(self, real_devices, real_sta_list=None, base_interop_obj=None):
        final_device_list = []
        """
        Selects real devices for testing.

        Args:
        - real_devices (RealDevice): Instance of RealDevice containing devices information.
        - real_sta_list (list, optional): List of specific real station names to select for testing.
        - base_interop_obj (object, optional): Base interop object to set for Devices.

        Returns:
        - list: list of selected real station names for testing.

        Steps:
        1. If `real_sta_list` is not provided, queries and retrieves all user-defined real stations from `real_devices`.
        2. Otherwise, assigns the provided `real_sta_list` to `self.real_sta_list`.
        3. If `base_interop_obj` is provided, assigns it to `self.Devices`.
        4. Sorts `self.real_sta_list` based on the second part of each station name.
        5. Logs an error and exits if no real stations are selected for testing.
        6. Logs the selected real station names.
        7. Adds real station data to `self.real_sta_data_dict`.
        8. Returns the list of selected real station names.
        """
        real_devices.get_devices()
        # Query and retrieve all user-defined real stations if `real_sta_list` is not provided
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_devices.query_user()
        else:
            interface_data = self.json_get_with_retry("/port/all")
            interfaces = interface_data["interfaces"]
            final_device_list = []  # Initialize the list

            for device in real_sta_list:
                for interface_dict in interfaces:
                    for key, value in interface_dict.items():
                        key_parts = key.split(".")
                        extracted_key = ".".join(key_parts[:2])
                        if (
                            extracted_key == device
                            and not value["phantom"]
                            and not value["down"]
                            and value["parent dev"] != ""
                            and value["ip"] != "0.0.0.0"
                        ):
                            final_device_list.append(key)
                            break

            self.real_sta_list = final_device_list

        if base_interop_obj is not None:
            self.Devices = base_interop_obj

        # Log an error and exit if no real stations are selected for testing
        if len(self.real_sta_list) == 0:
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        real_devices.get_devices()
        self.real_sta_list = self.filter_ios_devices(self.real_sta_list)

        if len(self.real_sta_list) == 0:
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logger.error(f"Real station '{sta_name}' not in devices data, ignoring it from testing")
                self.real_sta_list.remove(sta_name)

                continue

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        return self.real_sta_list

    @staticmethod
    def sum_reset_counter(values):
        """Sum cumulative-counter segment maxima, ignoring unavailable samples."""
        valid_values = []
        for value in values:
            try:
                counter = int(float(value))
            except (TypeError, ValueError, OverflowError):
                continue
            if counter >= 0:
                valid_values.append(counter)

        if not valid_values:
            return 0

        previous = valid_values[0]
        segment_max = previous
        total = 0

        for current in valid_values[1:]:
            if current < previous:
                total += segment_max
                segment_max = current
            else:
                segment_max = max(segment_max, current)
            previous = current

        return int(total + segment_max)

    def calculate_device_score(self, df, os_type="laptop"):
        """
        Calculate device score based on YouTube streaming metrics.

        Metrics:
        - Connection Speed
        - Buffer Health
        - Dropped Frames
        - Resolution Stability
        - Network Activity (Laptop only)
        - Protocol
        - Bandwidth
        """
        # 1. CONFIGURABLE SPEED TABLE
        speed_db = {
            "2160p": 20,
            "1440p": 12,
            "1080p": 8,
            "720p": 5,
            "480p": 3,
            "240p": 1
        }

        # 2. AVERAGES
        if os_type.lower() == "android":
            if "bandwidth (kbps)" in df:
                speed_series = pd.to_numeric(
                    df["bandwidth (kbps)"],
                    errors="coerce"
                )
                avg_speed = speed_series.mean()
            else:
                avg_speed = 0
        else:
            if "ConnectionSpeedKbps" in df:
                speed_series = pd.to_numeric(
                    df["ConnectionSpeedKbps"],
                    errors="coerce"
                ) / 1000
                avg_speed = speed_series.mean()
            else:
                avg_speed = 0

        if pd.isna(avg_speed):
            avg_speed = 0
        avg_buffer = df["BufferHealth"].mean() if "BufferHealth" in df else 0
        resolution = self.resolution
        recommended_speed = speed_db.get(resolution, 5)

        # 3. CONNECTION SPEED SCORE
        if avg_speed >= recommended_speed:
            speed_score = 5
        else:
            speed_score = (avg_speed / recommended_speed) * 5

        # 4. BUFFER HEALTH SCORE
        if avg_buffer >= 10:
            buffer_score = 5
        else:
            buffer_score = (avg_buffer / 10) * 5

        # 5. DROPPED FRAME LOGIC (RESET SAFE)
        total_dropped = self.sum_reset_counter(df["DroppedFrames"])
        total_frames = self.sum_reset_counter(df["TotalFrames"])

        drop_percent = (total_dropped / total_frames) * 100 if total_frames > 0 else 0

        if drop_percent >= 10:
            drop_score = 0
        else:
            drop_score = ((10 - drop_percent) / 10) * 5
        # 6. RESOLUTION STABILITY
        if os_type.lower() == "android":

            resolution_map = {
                "2160p": "2160",
                "1440p": "1440",
                "1080p": "1080",
                "720p": "720",
                "480p": "480",
                "240p": "240"
            }

            target_res = resolution_map.get(self.resolution, "720")

            matches = 0

            for val in df["CurrentRes"]:
                if isinstance(val, str):
                    match = re.search(r'(\d{3,4})x(\d{3,4})', val)
                    if match:
                        current_res = match.group(2)
                        if current_res == target_res:
                            matches += 1

            stability_percent = (matches / len(df)) * 100 if len(df) > 0 else 0

        else:
            # existing logic for laptops
            if "CurrentRes" in df and "OptimalRes" in df:
                matches = (df["CurrentRes"] == df["OptimalRes"]).sum()
                stability_percent = (matches / len(df)) * 100
            else:
                stability_percent = 0

        resolution_score = (stability_percent / 100) * 5

        # 7. NETWORK ACTIVITY (Laptop Only)
        if os_type.lower() != "android" and "NetworkActivityKB" in df:
            net_series = df["NetworkActivityKB"]
            net_series = net_series[net_series > 0]

            if len(net_series) > 0:
                avg_net = net_series.mean()
                deviation = abs(net_series - avg_net)
                avg_dev = deviation.mean()
                fluctuation = (avg_dev / avg_net) * 100
            else:
                fluctuation = 0

            if fluctuation <= 10:
                network_score = 5
            elif fluctuation <= 20:
                network_score = 4
            elif fluctuation <= 30:
                network_score = 3
            elif fluctuation <= 40:
                network_score = 2
            elif fluctuation <= 50:
                network_score = 1
            else:
                network_score = 0
        else:
            network_score = None

        # 8. PROTOCOL
        protocol_score = 5

        # 9. WEIGHT HANDLING
        laptop_weights = {
            "speed": 30,
            "buffer": 20,
            "drop": 20,
            "resolution": 15,
            "network": 10,
            "protocol": 5
        }

        if os_type.lower() == "android":
            multiplier = 100 / 90
            weights = {
                "speed": 30 * multiplier,
                "buffer": 20 * multiplier,
                "drop": 20 * multiplier,
                "resolution": 15 * multiplier,
                "protocol": 5 * multiplier
            }
        else:
            weights = laptop_weights

        # 10. FINAL WEIGHTED SCORE
        weighted_total = (
            speed_score * weights["speed"] +
            buffer_score * weights["buffer"] +
            drop_score * weights["drop"] +
            resolution_score * weights["resolution"] +
            protocol_score * weights["protocol"]
        )

        if os_type.lower() != "android":
            weighted_total += network_score * weights["network"]

        overall_score = weighted_total / 5

        return {
            "avg_speed": round(avg_speed, 2),
            "avg_buffer": round(avg_buffer, 2),
            "drop_percent": round(drop_percent, 2),
            "stability_percent": round(stability_percent, 2),
            "fluctuation": round(fluctuation if os_type.lower() != "android" else 0, 2),

            "speed_score": round(speed_score, 2),
            "buffer_score": round(buffer_score, 2),
            "drop_score": round(drop_score, 2),
            "resolution_score": round(resolution_score, 2),
            "network_score": network_score,
            "protocol_score": protocol_score,

            "weights": weights,
            "overall_score": round(overall_score, 2)
        }

    def process_device_data(self):
        """
        Populate hostnames, OS types, and per-OS device counts for real stations.

        Android devices use serial numbers as hostnames (mapped sequentially),
        while other OS types use their reported hostnames. Also builds a combined
        hostname-OS list for display and updates OS counters.

        Returns:
            None
        """

        self.real_sta_os_types = []
        self.real_sta_hostname = []

        serial_idx = 0  # separate counter just for Android devices

        for _, sta_info in self.real_sta_data_dict.items():
            os_type = sta_info.get('ostype', '')
            self.real_sta_os_types.append(os_type)

            if os_type.lower() == "android":
                if serial_idx < len(self.serial_list):
                    self.real_sta_hostname.append(self.serial_list[serial_idx])
                    serial_idx += 1  # advance only for Androids
                else:
                    self.real_sta_hostname.append("NA")
            else:
                self.real_sta_hostname.append(sta_info.get('hostname', 'NA'))

        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_types)
        ]
        self.hostname_to_station_map = dict(
            zip(self.real_sta_hostname, self.real_sta_list)
        )

        for i in range(0, len(self.real_sta_os_types)):

            if self.real_sta_os_types[i] == 'windows':
                self.windows = self.windows + 1
            elif self.real_sta_os_types[i] == 'linux':
                self.linux = self.linux + 1
            elif self.real_sta_os_types[i] == 'macos':
                self.mac = self.mac + 1
            elif self.real_sta_os_types[i] == 'android':
                self.android = self.android + 1

    def update_webui(self):
        """
        Updates the WebUI with the current device configuration information.
        Displays the configured device list and operating system summary.
        """
        if len(self.real_sta_hostname) == 0:
            logging.error("No device is available to run the test")
            obj = {
                "status": "Stopped",
                "configuration_status": "configured"
            }
            self.updating_webui_runningjson(obj)
            return
        else:
            obj = {
                "configured_devices": self.real_sta_hostname,
                "configuration_status": "configured",
                "no_of_devices": f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac})',
                "device_list": self.hostname_os_combination

            }
            self.updating_webui_runningjson(obj)

    def start_generic(self):
        """
        Starts the generic endpoints' connections and sets the start time.

        Steps:
        1. Starts the connections of generic endpoints using `self.generic_endps_profile.start_cx()`.
        2. Sets the start time (`self.start_time`) to the current datetime.

        """
        # A robot test can reuse endpoint names across coordinates and angles.
        # Do not carry completion-wait timers from an earlier run into this one.
        self._gen_cx_stall_since = {}
        self._gen_cx_timed_out = set()

        if self.android:
            self.android_log_received.clear()

        # Start the connections of generic endpoints
        self.generic_endps_profile.start_cx()
        # Set the start time to the current datetime
        self.start_time = datetime.now()
        logging.info(
            "YouTube streaming started at %s",
            datetime.now().astimezone().isoformat(timespec="seconds"),
        )

    def stop_generic_cx(self,):
        self.generic_endps_profile.stop_cx()
        self.stop_time = datetime.now()

    def wait_for_android_shutdown(self, timeout=30):
        """Give Android time to stop YouTube and upload its combined log."""
        if not self.android:
            return True
        if self.android_log_received.wait(timeout=timeout):
            logger.info("Android shutdown completed and test log was received.")
            return True
        logger.warning(
            "Android did not upload its test log within %s seconds; "
            "force-stopping the generic CX.",
            timeout,
        )
        return False

    def wait_stop_aware(self, duration, context, poll_interval=0.25):
        """Wait for a fixed delay while honoring WebUI stop requests."""
        deadline = time.monotonic() + duration
        while True:
            if self.stop_signal:
                logger.info("WebUI stop requested %s.", context)
                raise WebUIStopRequested
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(poll_interval, remaining))

    def check_robo_stop(self):
        """Robot callback that immediately unwinds a WebUI-stopped test."""
        if self.stop_signal:
            logger.info(
                "WebUI stop requested during robot battery/movement handling; "
                "unwinding directly to report generation."
            )
            raise WebUIStopRequested
        return {}

    def finalize_test_run(self, args, iot_summary=None):
        """Stop clients, generate the report, then clean up the test."""
        self.stop()
        # Stop collection before WebUI completion triggers the final live image.
        if args.do_webUI:
            self.stop_webui_test()
        logger.info("Waiting 10 seconds for client cleanup and log uploads")
        time.sleep(10)
        self.stop_connectivity_monitoring()
        self.stop_wifi_analysis()
        try:
            if args.do_robo and not self.is_continuous_run:
                self.create_robo_report()
            else:
                self.create_report(
                    self.stats_api_response,
                    self.ui_report_dir if args.do_webUI else "",
                    iot_summary=iot_summary,
                )
            logger.info("YouTube report generated: %s", self.report_path_date_time)
        finally:
            try:
                self.generic_endps_profile.stop_cx()
            except Exception:
                logger.exception("Unable to stop all YouTube CXs during cleanup")
            if not args.no_post_cleanup:
                try:
                    self.generic_endps_profile.cleanup()
                except Exception:
                    logger.exception("Unable to clean up all YouTube endpoints")
                if getattr(self, 'background_ping', None):
                    try:
                        self.background_ping.cleanup()
                    except (Exception, SystemExit):
                        logger.exception("Unable to clean up background ping endpoints")

    def get_youtube_lf_wifi_stats(self):
        """
        Returns dict: { sta_name : { BSSID, RSSI, channel, mode, tx_rate, rx_rate } }
        """
        lf_stats_map = {}
        interfaces_dict = {}

        try:
            port_data = self.json_get("/ports/all/")["interfaces"]
            for port in port_data:
                interfaces_dict.update(port)
        except Exception as e:
            logger.error(f"Error fetching port data: {e}")
            return lf_stats_map

        for sta in self.real_sta_list:
            lf_stats_map[sta] = {
                "BSSID": "NA",
                "RSSI": "NA",
                "Channel": "NA",
                "Mode": "NA",
                "TxRate": "NA",
                "RxRate": "NA",
            }

            if sta in interfaces_dict:
                data = interfaces_dict[sta]

                sig = data.get("signal", "NA")
                if "dBm" in str(sig):
                    lf_stats_map[sta]["RSSI"] = sig.split(" ")[0]
                else:
                    lf_stats_map[sta]["RSSI"] = sig

                lf_stats_map[sta]["Channel"] = data.get("channel", "NA")
                lf_stats_map[sta]["Mode"] = data.get("mode", "NA")
                lf_stats_map[sta]["TxRate"] = data.get("tx-rate", "NA")
                lf_stats_map[sta]["RxRate"] = data.get("rx-rate", "NA")
                lf_stats_map[sta]["BSSID"] = data.get("ap", "NA")

        return lf_stats_map

    def __getstate__(self):
        """lf_multi_traffic.py copies this object to its main process (multiprocessing pickles it).
        Attributes that can't be pickled (locks, events, live monitoring objects with threads) become None;
        __setstate__ makes fresh locks. Collected results (stats, CSV paths, report paths) are kept."""
        state = {}
        for key, value in self.__dict__.items():
            try:
                pickle.dumps(value)
                state[key] = value
            except Exception:
                state[key] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.android_log_received = Event()
        self.playback_stats_lock = Lock()

    def start_flask_server(self):
        """
        Starts a Flask server with API endpoints for YouTube statistics.
        """
        app = Flask(__name__)

        @app.route('/upload_youtube_log', methods=['POST'])
        def upload_youtube_log():
            """Store a client log for inclusion in the active test report."""
            device_name = request.form.get('device_name', '').strip()
            device_type = request.form.get('device_type', 'client').strip().lower()
            log_kind = request.form.get('log_kind', 'test').strip().lower()
            log_file = request.files.get('log_file')

            if not device_name or log_file is None:
                return jsonify({"error": "device_name and log_file are required"}), 400

            safe_device_name = re.sub(r'[^A-Za-z0-9_.-]+', '_', device_name)
            safe_device_type = re.sub(r'[^A-Za-z0-9_.-]+', '_', device_type)
            safe_log_kind = re.sub(r'[^A-Za-z0-9_.-]+', '_', log_kind)
            log_directory = (
                self.ui_report_dir
                if self.do_webUI and self.ui_report_dir
                else os.path.dirname(os.path.abspath(__file__))
            )
            os.makedirs(log_directory, exist_ok=True)
            if safe_device_type == 'android':
                log_filename = "android_youtube_test.log"
            elif safe_log_kind == 'debug':
                log_filename = f"{safe_device_name}_client_youtube_debug.log"
            else:
                log_filename = (
                    f"{safe_device_name}_{safe_device_type}_youtube_test.log"
                )
            log_path = os.path.join(log_directory, log_filename)

            try:
                log_file.save(log_path)
            except OSError as exc:
                logger.exception("Unable to store YouTube log for %s", device_name)
                return jsonify({"error": str(exc)}), 500

            if log_path not in self.devices_list:
                self.devices_list.append(log_path)
            if safe_device_type == 'android':
                self.android_log_received.set()
            logger.info("Received YouTube test log for %s: %s", device_name, log_path)
            return jsonify({"message": "Log uploaded successfully"}), 200

        @app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        @app.route('/stop_yt', methods=['GET'])
        def stop_yt():
            """
            Request that the main test flow stop and perform its normal cleanup
            and report generation.
            """
            if self.stop_signal:
                return jsonify({"message": "YouTube test stop is already in progress"}), 200

            logger.info("Stopping the test through WebUI")
            self.stop_signal = True

            return jsonify({"message": "YouTube test stop requested"}), 200

        @app.route('/youtube_stats', methods=['GET', 'POST'])
        def youtube_stats():
            """
            API endpoint to get or post YouTube statistics.
            - GET: Returns the current YouTube stats.
            - POST: Updates the stats or clears them based on the provided data.
            """
            if request.method == 'POST':
                data = request.json
                received_at = time.time()

                # Clear data if requested
                if data.get("clear_data"):
                    self.stats_api_response = {}
                    with self.playback_stats_lock:
                        self.playback_stats_start_time = None
                        self.playback_stats_end_time = None
                        self.windowed_ping_stats = None
                    return jsonify({"message": "Data cleared"}), 200

                received_stats = False
                for key, value in data.items():
                    if key == "stop":
                        continue
                    received_stats = True
                    device_name = key
                    stats = value
                    stop = data.get("stop", False)

                    if device_name not in self.stats_api_response:
                        self.stats_api_response[device_name] = {}
                    self.stats_api_response[device_name] = {
                        **stats,
                        "stop": stop
                    }

                    if self.do_robo:
                        self.stats_api_response[device_name]["current_angle"] = self.current_angle
                        self.stats_api_response[device_name]["current_cord"] = self.current_cord
                        self.stats_api_response[device_name]["rotations_enabled"] = self.rotations_enabled
                        stats["Angle"] = self.current_angle

                    if self.do_robo and self.is_continuous_run:
                        lf_wifi_map = self.get_youtube_lf_wifi_stats()
                        sta_name = self.hostname_to_station_map.get(device_name)
                        if sta_name in lf_wifi_map:
                            stats["BSSID"] = lf_wifi_map[sta_name]["BSSID"]
                            stats["Channel"] = lf_wifi_map[sta_name]["Channel"]
                        else:
                            stats["BSSID"] = "NA"
                            stats["Channel"] = "NA"

                        x, y, _fromc, _toc = self.robo_obj.get_robot_pose()
                        stats["X"] = x
                        stats["Y"] = y
                        stats["From_Coord"] = self.from_coordinate
                        stats["To_Coord"] = self.to_coordinate

                    if self.do_robo and self.current_cord != "" and not self.is_continuous_run:
                        csv_filename = f"{self.current_cord}_{device_name}_youtube_stats_report.csv"
                    else:
                        csv_filename = f"{device_name}_youtube_stats_report.csv"

                    if self.do_webUI:
                        csv_file_path = os.path.join(self.ui_report_dir, csv_filename)
                    else:
                        current_path = os.path.dirname(os.path.abspath(__file__))
                        csv_file_path = os.path.join(current_path, csv_filename)

                    first_sample_for_run = csv_file_path not in self.devices_list
                    if first_sample_for_run:
                        self.devices_list.append(csv_file_path)

                    file_exists = os.path.isfile(csv_file_path)
                    timestamp = stats.get("Timestamp", "")

                    mode = 'w' if first_sample_for_run else 'a'
                    with open(csv_file_path, mode=mode, newline='') as file:
                        writer = csv.writer(file)
                        if first_sample_for_run or not file_exists:
                            writer.writerow(self.csv_headers)
                        row = [device_name, timestamp]
                        for header in self.csv_headers[2:]:
                            row.append(stats.get(header, "NA"))
                        writer.writerow(row)

                if received_stats:
                    with self.playback_stats_lock:
                        if (self.playback_stats_start_time is None
                                or received_at < self.playback_stats_start_time):
                            self.playback_stats_start_time = received_at
                        if (self.playback_stats_end_time is None
                                or received_at > self.playback_stats_end_time):
                            self.playback_stats_end_time = received_at

                return jsonify({"message": "Stats updated"}), 200

            elif request.method == 'GET':
                return jsonify(self.stats_api_response), 200

            return jsonify({"error": "Invalid request"}), 400

        @app.route('/read_youtube_data_from_csv', methods=['GET'])
        def read_youtube_data_from_csv():
            """
            API endpoint to read YouTube data from CSV files and return the last row for each device.
            """
            device_data = {}
            for csv_file_path in list(self.devices_list):
                if not csv_file_path.endswith("_youtube_stats_report.csv"):
                    continue
                if not os.path.isfile(csv_file_path):
                    continue

                try:
                    df = pd.read_csv(csv_file_path)
                except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
                    logger.warning(
                        "Unable to read live YouTube data from %s: %s",
                        csv_file_path,
                        exc,
                    )
                    continue

                if not df.empty:
                    # Convert NumPy scalars and NaN into values Flask can encode.
                    last_row = json.loads(df.iloc[-1].to_json())
                    device_name = os.path.basename(csv_file_path).split('_youtube_stats_report')[0]
                    device_data[device_name] = last_row
            return jsonify({"result": device_data}), 200

        # useful to simulate wait for battery charging
        @app.route('/pause_true', methods=['GET'])
        def pause_true():
            self.pause = True
            return jsonify({"pause": self.pause})

        # useful to simulate wait for battery charging
        @app.route('/pause_false', methods=['GET'])
        def pause_false():
            self.pause = False
            return jsonify({"pause": self.pause})

        def run_flask():
            app.run(host="0.0.0.0", port=5002, debug=False, use_reloader=False)

        # Run the Flask server in a separate thread to avoid blocking
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

    def stop_previous_flask_server(self, port=5002):
        """Stop processes already listening on the YouTube statistics port."""
        current_os = platform.system()
        if current_os not in ["Linux", "Darwin"]:
            logger.warning(
                "Unsupported OS %s; cannot automatically clear port %s.",
                current_os,
                port,
            )
            return

        logger.info("Checking whether port %s is already in use.", port)
        try:
            result = subprocess.run(
                ["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            logger.warning("Unable to inspect port %s: %s", port, exc)
            return

        pids = [pid for pid in result.stdout.splitlines() if pid.strip()]
        if not pids:
            logger.info("Port %s is clear and ready for the Flask server.", port)
            return

        for pid_text in pids:
            try:
                pid = int(pid_text)
                logger.warning(
                    "Stopping previous process %s listening on port %s.",
                    pid,
                    port,
                )
                os.kill(pid, signal.SIGKILL)
            except (OSError, ValueError) as exc:
                logger.warning(
                    "Could not stop process %s on port %s: %s",
                    pid_text,
                    port,
                    exc,
                )

    def wait_for_flask(
        self,
        url=YOUTUBE_STATS_URL,
        timeout=10,
    ):
        """Wait until the YouTube statistics server responds successfully."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with urllib_request.urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        logger.info("YouTube statistics server is ready on port 5002.")
                        return
            except (urllib_error.URLError, OSError):
                time.sleep(1)

        raise RuntimeError(
            f"YouTube statistics server did not start within {timeout} seconds"
        )

    def handle_flask_server(self):
        """Clear port 5002, start Flask, and verify it before the test starts."""
        self.stop_previous_flask_server(port=5002)
        time.sleep(5)
        self.start_flask_server()
        self.wait_for_flask()

    def move_files(self, source_file, dest_dir):
        # Ensure the source file exists
        if not os.path.isfile(source_file):
            logger.warning(
                "Skipping report artifact because source file does not exist or "
                "is not a regular file: %s",
                source_file,
            )
            return

        # Keep uploaded client logs separate from reports, CSVs, and graphs.
        filename = os.path.basename(source_file)
        if filename.endswith(("_youtube_test.log", "_youtube_debug.log")):
            dest_dir = os.path.join(dest_dir, "client_logs")

        # Ensure the destination directory exists
        if not os.path.exists(dest_dir) and os.path.basename(dest_dir) == "client_logs":
            try:
                os.makedirs(dest_dir, exist_ok=True)
            except OSError as exc:
                logger.error(
                    "Cannot create client log directory %s: %s",
                    dest_dir,
                    exc,
                )
                return

        if not os.path.exists(dest_dir):
            logger.error(
                "Cannot move report artifact %s because destination directory "
                "does not exist: %s",
                source_file,
                dest_dir,
            )
            return

        try:
            dest_file = os.path.join(dest_dir, filename)
            shutil.move(source_file, dest_file)

            logging.info(f"Successfully moved '{source_file}' to '{dest_file}'.")

        except (OSError, shutil.Error) as e:
            logger.error(
                "Failed to move report artifact %s to %s: %s",
                source_file,
                dest_dir,
                e,
            )

    def updating_webui_runningjson(self, obj):
        data = {}
        file_path = self.ui_report_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name)

        # Wait up to three minutes for the WebGUI to create the running file.
        wait_timeout = 180
        wait_deadline = time.monotonic() + wait_timeout
        while not os.path.exists(file_path):
            if time.monotonic() >= wait_deadline:
                logging.error(
                    "Running JSON file was not created by the WebGUI within %s "
                    "seconds: %s. Skipping this status update.",
                    wait_timeout,
                    file_path,
                )
                return
            logging.info("Waiting for Running JSON file to be created")
            time.sleep(1)
        logging.info("Running JSON file created")
        # the WebGUI may still be writing the file (it is created empty first); retry briefly
        for attempt in range(10):
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                break
            except ValueError:
                if attempt == 9:
                    logging.error("Running JSON file is not valid JSON: %s. Skipping this status update.", file_path)
                    return
                time.sleep(0.5)

        for key in obj:
            data[key] = obj[key]

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_bandsteering_report_section(self, report=None):
        """
        Bandsteering reporting (Robo-style):
        Reads all youtube stats CSVs from report directory and builds:
        - BSSID change count graph per device
        - Table of BSSID change events
        """
        if report is None:
            logging.error("Bandsteering report: report object is None")
            return

        if not self.do_bandsteering:
            logging.info("Bandsteering report skipped: do_bandsteering is False")
            return

        report_dir = self.report_path_date_time
        if not report_dir or not os.path.isdir(report_dir):
            logging.error(f"Bandsteering report: invalid report dir: {report_dir}")
            return

        logging.info(f"Bandsteering report dir: {report_dir}")

        csv_files = glob.glob(os.path.join(report_dir, "*_youtube_stats_report.csv"))
        logging.info(f"Bandsteering CSV files found: {csv_files}")

        if not csv_files:
            logging.warning("No youtube_stats_report CSVs found in report dir for bandsteering")
            return

        report.set_obj_html(
            _obj_title="Band Steering Statistics",
            _obj="This section summarizes BSSID changes observed while the robot moved between coordinates."
        )
        report.build_objective()

        allowed_bssids = set(self.bssids)

        for csv_file_path in csv_files:
            try:
                df = pd.read_csv(csv_file_path)
            except Exception as e:
                logging.error(f"Unable to read CSV {csv_file_path}: {e}", exc_info=True)
                continue

            required_cols = {"TimeStamp", "BSSID", "From_Coord", "To_Coord", "Channel"}
            if not required_cols.issubset(df.columns):
                logging.warning(f"Skipping {csv_file_path}: missing {required_cols - set(df.columns)}")
                continue

            device_name = os.path.basename(csv_file_path).split("_youtube_stats_report")[0]

            df["BSSID"] = df["BSSID"].fillna("NA").astype(str)
            df["TimeStamp"] = df["TimeStamp"].fillna("NA").astype(str)
            df["From_Coord"] = df["From_Coord"].fillna("NA").astype(str)
            df["To_Coord"] = df["To_Coord"].fillna("NA").astype(str)
            df["Channel"] = df["Channel"].fillna("NA").astype(str)

            if allowed_bssids:
                df = df[df["BSSID"].isin(allowed_bssids)]

            if df.empty:
                logging.info(f"No matching BSSID rows for {device_name}")

            df["prev_bssid"] = df["BSSID"].shift()

            mask = (
                (df["BSSID"] != df["prev_bssid"]) &
                (df["BSSID"] != "NA")
            )

            bssid_list = df.loc[mask, "BSSID"].tolist()
            timestamp_list = df.loc[mask, "TimeStamp"].tolist()
            from_coordinate_list = df.loc[mask, "From_Coord"].tolist()
            to_coordinate_list = df.loc[mask, "To_Coord"].tolist()
            channel_list = df.loc[mask, "Channel"].tolist()

            skip_table = not mask.any()

            if skip_table:
                bssid_counts = {bssid: 0 for bssid in self.bssids}
            else:
                bssid_counts = Counter(bssid_list)

            final_bssid_counts = {
                bssid: bssid_counts.get(bssid, 0)
                for bssid in self.bssids
            }

            x_axis = list(final_bssid_counts.keys())
            y_axis = [[float(value)] for value in final_bssid_counts.values()]

            report.set_obj_html(
                _obj_title=f"BSSID Change Count Of The Client {device_name}",
                _obj=" "
            )
            report.build_objective()

            graph = lf_bar_graph(
                _data_set=y_axis,
                _xaxis_name="BSSID",
                _yaxis_name="Number of Changes",
                _xaxis_categories=[""],
                _xaxis_label=x_axis,
                _graph_image_name=f"youtube_bssid_change_count_{device_name}",
                _label=x_axis,
                _xaxis_step=1,
                _graph_title=f"YouTube Bandsteering: BSSID change count for device : {device_name}",
                _title_size=16,
                _bar_width=0.15,
                _figsize=(18, 6),
                _dpi=96,
                _show_bar_value=True,
                _enable_csv=True,
            )

            graph_png = graph.build_bar_graph()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.set_csv_filename(f"{graph.graph_image_name}.csv")
            report.move_csv_file()
            report.build_graph()

            if skip_table:
                report.set_obj_html(
                    _obj_title=f"Band Steering Results for {device_name}",
                    _obj="No band steering events observed for the configured BSSID list."
                )
                report.build_objective()
                continue

            report.set_obj_html(
                _obj_title=f"Band Steering Results for {device_name}",
                _obj=" "
            )
            report.build_objective()

            table_df = pd.DataFrame({
                "TimeStamp": timestamp_list,
                "BSSID": bssid_list,
                "Channel": channel_list,
                "From Coordinate": from_coordinate_list,
                "To Coordinate": to_coordinate_list,
            })

            report.set_table_dataframe(table_df)
            report.build_table()

        if self.do_robo and len(self.robo_obj.charging_timestamps) != 0:
            report.set_obj_html(_obj_title="Charging Timestamps",
                                _obj="")
            report.build_objective()
            df = pd.DataFrame(
                self.robo_obj.charging_timestamps,
                columns=[
                    "charge_dock_arrival_timestamp",
                    "charging_completion_timestamp"
                ]
            )
            df.insert(0, "S.No", range(1, len(df) + 1))
            report.set_table_dataframe(df)
            report.build_table()
        elif self.do_robo:
            report.set_obj_html(_obj_title="Charging Timestamps",
                                _obj="Robot did not went to charge during this test")
            report.build_objective()

    @staticmethod
    def _resolution_label(value):
        """Return a comparable vertical resolution label such as ``1080p``."""
        dimensions = re.search(r"(\d+)\s*x\s*(\d+)", str(value), re.IGNORECASE)
        label = re.fullmatch(r"\s*(\d+)p\s*", str(value), re.IGNORECASE)
        if dimensions:
            return f"{dimensions.group(2)}p"
        if label:
            return f"{label.group(1)}p"
        return "Unknown"

    @staticmethod
    def _elapsed_seconds(values):
        """Preserve sampling gaps and unwrap midnight in time-only CSV timestamps."""
        times = pd.to_datetime(values, format="%H:%M:%S", errors="coerce")
        seconds = times.dt.hour * 3600 + times.dt.minute * 60 + times.dt.second
        rollover = (seconds.diff() < -43200).cumsum() * 86400
        elapsed = seconds + rollover
        valid = elapsed.dropna()
        return elapsed - valid.iloc[0] if not valid.empty else elapsed

    @staticmethod
    def _score_rating(score):
        """Rate scores as Excellent >=90, Good >=75, Average >=60, otherwise Poor."""
        if score >= 90:
            return "Excellent"
        if score >= 75:
            return "Good"
        if score >= 60:
            return "Average"
        return "Poor"

    @staticmethod
    def _rating_html(rating):
        """Use the same rating colors for the overall verdict and client tables."""
        colors = {
            "Excellent": "#1e7e34", "Good": "#28a745",
            "Average": "#f1c40f", "Poor": "#e74c3c",
        }
        label = escape(str(rating))
        color = colors.get(rating)
        return (f"<span style='color:{color}; font-weight:800;'>{label}</span>"
                if color else label)

    def _build_client_metrics_table(self, rows):
        frame = pd.DataFrame(rows)
        for column in frame.columns:
            frame[column] = frame[column].map(
                self._rating_html if column == "Rating" else lambda value: escape(str(value)))
        self.report.set_custom_html(frame.to_html(index=False, escape=False, justify="center"))
        self.report.build_custom()
        self.report.set_custom_html("")

    @staticmethod
    def _overall_score_rating(score):
        """Rate the test average separately from individual client scores."""
        if score >= 90:
            return "Excellent"
        if score >= 80:
            return "Good"
        if score >= 70:
            return "Average"
        return "Poor"

    def _youtube_report_metrics(self):
        """Build per-client report metrics strictly from collected raw CSV rows."""
        # Cache each file only for this report build; preserve file and row order.
        client_frames = {}
        file_groups = {}
        for csv_file_path in self.devices_list:
            if not csv_file_path.endswith("_youtube_stats_report.csv"):
                continue
            if csv_file_path not in file_groups:
                try:
                    frame = pd.read_csv(csv_file_path)
                except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
                    logger.warning("Unable to read report data %s: %s", csv_file_path, exc)
                    file_groups[csv_file_path] = {}
                    continue
                file_groups[csv_file_path] = (
                    dict(tuple(frame.groupby(frame["Instance Name"].astype(str), sort=False)))
                    if "Instance Name" in frame.columns else {})
            for name, frame in file_groups[csv_file_path].items():
                client_frames.setdefault(name, []).append(frame)

        metrics = {}
        for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_types):
            frames = client_frames.get(str(hostname), [])

            if not frames:
                metrics[hostname] = None
                continue

            data = pd.concat(frames, ignore_index=True)
            for column in ("BufferHealth", "ConnectionSpeedKbps", "NetworkActivityKB", "bandwidth (kbps)"):
                if column in data:
                    data[column] = pd.to_numeric(data[column], errors="coerce")
            if "TotalFrames" not in data or self.sum_reset_counter(data["TotalFrames"]) <= 0:
                logger.warning("Skipping %s report metrics: no rendered frames were recorded", hostname)
                metrics[hostname] = None
                continue
            required = ["BufferHealth", "DroppedFrames", "TotalFrames", "CurrentRes"]
            required += (["bandwidth (kbps)"] if os_type.lower() == "android"
                         else ["ConnectionSpeedKbps", "NetworkActivityKB", "OptimalRes"])
            missing = [column for column in required
                       if column not in data or data[column].isna().all()]
            score_input = data.copy()
            for column in required:
                if column not in score_input:
                    score_input[column] = float("nan")
            score_data = self.calculate_device_score(score_input, os_type=os_type)
            resolution_counts = {}
            if "CurrentRes" in data and "TimeStamp" in data:
                labels = data["CurrentRes"].map(self._resolution_label)
                elapsed = self._elapsed_seconds(data["TimeStamp"])
                # Attribute each observed interval to its starting resolution.
                # Do not invent a duration after the final sample.
                durations = elapsed.shift(-1) - elapsed
                valid = durations.gt(0) & elapsed.notna()
                if valid.any():
                    totals = durations[valid].groupby(labels[valid]).sum()
                    resolution_counts = (totals / totals.sum() * 100).to_dict()
            network = data["NetworkActivityKB"].mean() if "NetworkActivityKB" in data else float("nan")
            metrics[hostname] = {
                "data": data,
                "score": score_data["overall_score"] if not missing else None,
                "rating": self._score_rating(score_data["overall_score"]) if not missing else "Incomplete data",
                "missing": missing,
                "drop_percent": score_data["drop_percent"],
                "avg_buffer": score_data["avg_buffer"],
                "network_activity": round(network, 2) if pd.notna(network) else None,
                "resolutions": resolution_counts,
            }
        return metrics

    def _client_observations(self, hostname, item, rssi):
        """Reference-style observations; thresholds affect wording only, not scores.

        RSSI: strong >=-67, moderate >=-75 dBm. Buffer reserve: >=10 s.
        Frame drops: zero, <=0.1 negligible, <1 low, <10 elevated,
        <50 very high, otherwise extremely high. Ping loss <=2% is low.
        """
        signal = pd.to_numeric(re.sub(r"\s*dBm\s*$", "", str(rssi), flags=re.IGNORECASE), errors="coerce")
        valid_signal = pd.notna(signal) and -127 <= signal < 0
        if valid_signal:
            strength = "Strong" if signal >= -67 else "Moderate" if signal >= -75 else "Weak"
            network_text = f"{strength} measured RSSI ({signal:g} dBm)"
        else:
            network_text = "RSSI unavailable"
        station = self.hostname_to_station_map.get(hostname)
        row = self._windowed_ping_results().get(station, {})
        sent = pd.to_numeric(row.get("sent"), errors="coerce")
        received = pd.to_numeric(row.get("recv"), errors="coerce")
        loss = None
        if pd.notna(sent) and pd.notna(received) and sent > 0 and 0 <= received <= sent:
            loss = 100 * (sent - received) / sent
            network_text += f"; {'low' if loss <= 2 else 'elevated'} ping packet loss ({loss:.2f}%)"
        else:
            network_text += "; connectivity unverified (no valid playback-window ping measurements)"
        observations = [network_text]

        data = item["data"]
        values = pd.to_numeric(data.get("BufferHealth", pd.Series(dtype=float)), errors="coerce")
        buffers = values.dropna()
        healthy_buffer = not buffers.empty and not values.isna().any() and bool((buffers >= 10).all())
        if buffers.empty:
            observations.append("Buffer health unavailable")
        elif healthy_buffer:
            observations.append(f"Healthy sampled buffer reserve (average {buffers.mean():.2f}s; minimum {buffers.min():.2f}s)")
        else:
            text = f"Average buffer health {buffers.mean():.2f}s; minimum {buffers.min():.2f}s"
            if (buffers < 10).any():
                text += "; low-buffer samples below 10s observed"
            if values.isna().any():
                text += "; some buffer samples unavailable"
            observations.append(text)

        drop = None
        if not {"DroppedFrames", "TotalFrames"}.intersection(item["missing"]):
            total = self.sum_reset_counter(data["TotalFrames"])
            if total > 0:
                drop = 100 * self.sum_reset_counter(data["DroppedFrames"]) / total
        if drop is None:
            observations.append("Dropped-frame measurements unavailable")
        else:
            description = ("No" if drop == 0 else "Negligible" if drop <= 0.1 else
                           "Low" if drop < 1 else "Elevated" if drop < 10 else
                           "Very high" if drop < 50 else "Extremely high")
            percentage = "<0.01" if 0 < drop < 0.005 else f"{drop:.2f}"
            observations.append(f"{description} dropped frames ({percentage}%)")

        if drop is not None and drop >= 10:
            if healthy_buffer and valid_signal and signal >= -67 and loss is not None and loss <= 2:
                observations.append("High frame loss indicates playback degradation despite healthy buffer reserve, strong measured RSSI, and low ping loss")
            else:
                observations.append("High frame loss indicates playback degradation; review client and network conditions")
        elif drop is not None and drop < 1 and healthy_buffer:
            observations.append("Sampled buffer and frame measurements are consistent with smooth playback")
        elif drop is not None and (drop >= 1 or (not buffers.empty and (buffers < 10).any())):
            observations.append("Elevated frame loss or low buffer reserve may affect playback smoothness")
        else:
            observations.append("Available measurements are insufficient to assess playback smoothness")

        if item["missing"]:
            labels = {"ConnectionSpeedKbps": "connection speed", "NetworkActivityKB": "network activity",
                      "BufferHealth": "buffer health", "DroppedFrames": "dropped frames",
                      "TotalFrames": "total frames", "CurrentRes": "current resolution",
                      "OptimalRes": "optimal resolution", "bandwidth (kbps)": "bandwidth"}
            observations.append("Score unavailable; missing: " + ", ".join(
                labels.get(column, column) for column in item["missing"]))
        return observations

    def _test_summary_findings(self, metrics, overall_rating):
        """Describe this run in the reference's five-point order, without changing scores.

        Summary-only thresholds: low buffer <10 s (the scorer's full-credit
        boundary), minimal frame drops <1%, low ping loss <=2%, strong RSSI
        >=-67 dBm. These describe observations, not proof of uninterrupted video
        or a diagnosis of the AP. Zero transmitted packets are missing evidence.
        """
        names = self.real_sta_hostname
        measured = [metrics[name] for name in names if metrics.get(name)]
        scored = [item for item in measured if item["score"] is not None]
        good = sum(item["rating"] in ("Good", "Excellent") for item in scored)
        if scored:
            ratings = (f"{good} of {len(scored)} scored clients ({100 * good / len(scored):.0f}%) "
                       "achieved Good or Excellent ratings. ")
        else:
            ratings = "No clients had sufficient measurements for a streaming score. "
        ratings += (f"{len(measured)} of {len(names)} configured clients supplied streaming data; "
                    f"{len(scored)} of {len(names)} could be scored.")
        drops = [item["drop_percent"] for item in measured
                 if "DroppedFrames" not in item["missing"] and pd.notna(item["drop_percent"])]
        if drops:
            ratings += (f" Dropped frames remained below 1% on {sum(value < 1 for value in drops)} "
                        f"of {len(drops)} clients with frame measurements.")

        averages = [item["avg_buffer"] for item in measured if pd.notna(item["avg_buffer"])]
        buffers = []
        missing_buffer_samples = False
        for item in measured:
            data = item["data"]
            if "BufferHealth" not in data:
                missing_buffer_samples = True
                continue
            values = pd.to_numeric(data["BufferHealth"], errors="coerce")
            missing_buffer_samples |= bool(values.isna().any())
            if values.notna().any():
                buffers.append(values.dropna())
        low_buffer_clients = sum(bool((values < 10).any()) for values in buffers)
        if averages:
            buffer_text = (f"Per-client average buffer health ranged from {min(averages):.2f} to "
                           f"{max(averages):.2f} seconds. ")
            if low_buffer_clients:
                buffer_text += (f"Buffer fell below 10 seconds on {low_buffer_clients} of "
                                f"{len(buffers)} clients.")
            else:
                buffer_text += "All available buffer samples remained at or above 10 seconds, indicating healthy playback reserve."
        else:
            buffer_text = "Buffer health could not be assessed because no valid buffer measurements were collected."
        if missing_buffer_samples:
            buffer_text += " Some buffer samples were unavailable."

        ping_stats = self._windowed_ping_results()
        losses = []
        for name in names:
            station = self.hostname_to_station_map.get(name)
            row = ping_stats.get(station, {})
            sent = pd.to_numeric(row.get("sent"), errors="coerce")
            received = pd.to_numeric(row.get("recv"), errors="coerce")
            if pd.notna(sent) and pd.notna(received) and sent > 0 and 0 <= received <= sent:
                losses.append(100 * (sent - received) / sent)
        if losses:
            low_loss = sum(loss <= 2 for loss in losses)
            connectivity = (f"Packet loss was 2% or less on {low_loss} of {len(losses)} measured clients "
                            f"(loss range: {min(losses):.2f}% to {max(losses):.2f}%).")
            if low_loss < len(losses):
                connectivity += f" {len(losses) - low_loss} clients exceeded 2% packet loss."
            if len(losses) < len(names):
                connectivity += f" Connectivity could not be assessed for {len(names) - len(losses)} clients."
        else:
            connectivity = "Wireless connectivity could not be assessed because no valid transmitted-packet measurements were available."

        signals = []
        for index, _ in enumerate(names):
            raw = self.rssi_list[index] if index < len(self.rssi_list) else None
            value = pd.to_numeric(re.sub(r"\s*dBm\s*$", "", str(raw), flags=re.IGNORECASE), errors="coerce")
            if pd.notna(value) and -127 <= value < 0:
                signals.append(value)
        if signals:
            strong = sum(value >= -67 for value in signals)
            signal = (f"Measured signal strength ranged from {min(signals):g} to {max(signals):g} dBm; "
                      f"{strong} of {len(signals)} clients with RSSI measurements met the strong-signal "
                      "summary threshold (at least -67 dBm).")
            if len(signals) < len(names):
                signal += f" RSSI was unavailable or invalid for {len(names) - len(signals)} configured clients."
        else:
            signal = "Signal strength could not be assessed because no valid RSSI measurements were available."

        if overall_rating in ("Excellent", "Good", "Average", "Poor"):
            overall = (f"Overall, the AP demonstrated {overall_rating.lower()} "
                       "YouTube streaming performance.")
        else:
            overall = "Overall, insufficient scoring data was available to rate the AP's YouTube streaming performance."
        return [ratings, buffer_text, connectivity, signal, overall]

    def _build_dropped_frames_percentage_graph(self, report, metrics):
        names = [name for name in self.real_sta_hostname if metrics.get(name)]
        if not names:
            return
        values = [metrics[name]["drop_percent"] for name in names]
        graph = lf_bar_graph_horizontal(
            _data_set=[values],
            _xaxis_name="Dropped Frames (%)",
            _yaxis_name="Wireless Clients",
            _yaxis_categories=names,
            _graph_image_name="youtube-dropped-frames",
            _label=["Dropped Frames (%)"])
        report.set_graph_image(graph.build_bar_graph_horizontal())
        report.build_graph()

    def _build_resolution_distribution_graph(self, report, metrics):
        names = [name for name in self.real_sta_hostname if metrics.get(name)]
        observed = {resolution for name in names for resolution in metrics[name]["resolutions"]}
        resolutions = sorted(observed - {"Unknown"}, key=lambda value: int(value[:-1]))
        if "Unknown" in observed:
            resolutions.append("Unknown")
        if not names or not any(metrics[name]["resolutions"] for name in names):
            return
        graph = lf_bar_graph_horizontal(
            _data_set=[
                [round(metrics[name]["resolutions"].get(resolution, 0.0), 2) for name in names]
                for resolution in resolutions],
            _xaxis_name="VIDEO RESOLUTION PERCENTAGE",
            _yaxis_name="WIRELESS CLIENTS",
            _yaxis_categories=names,
            _graph_image_name="youtube-resolution-distribution",
            _label=resolutions,
            _stacked=True)
        report.set_graph_image(graph.build_bar_graph_horizontal())
        report.build_graph()

    def _build_buffer_health_graph(self, report, hostname, timestamps, buffer_health, suffix="", clock_times=None):
        """Use numeric elapsed seconds so irregular sampling gaps remain visible."""
        values = pd.to_numeric(buffer_health, errors="coerce")
        valid = timestamps.notna() & values.notna()
        if not valid.any():
            return
        chart_id = re.sub(r"[^A-Za-z0-9_-]+", "_", f"youtube-buffer-{hostname}{suffix}")
        clock_options = {}
        if clock_times is not None:
            clocks = pd.to_datetime(clock_times, format="%H:%M:%S", errors="coerce").dropna()
            if not clocks.empty:
                first = clocks.iloc[0]
                clock_options["clockOffsetSeconds"] = first.hour * 3600 + first.minute * 60 + first.second
        payload = {
            "xAxisType": "value", **clock_options,
            "series": [{"name": "Buffer Health", "data": [
                [float(timestamp), float(value)]
                for timestamp, value in zip(timestamps[valid], values[valid])
            ]}],
        }
        x_name = "Time (HH:MM:SS)" if clock_options else "Elapsed Time (s)"
        chart_html = """
            <div class='chart-card'>
              <h3>{title}</h3>
              <div id='{chart_id}' class='chart'></div>
              <script>
                window.__lfModernReport.renderLineChart({chart_id_json}, {payload}, {y_name}, {x_name});
              </script>
            </div>
            """.format(
                title=escape(f"Buffer Health vs Time Graph for {hostname}"),
                chart_id=chart_id,
                chart_id_json=json.dumps(chart_id),
                payload=json.dumps(payload),
                y_name=json.dumps("Buffer Health (Seconds)"),
                x_name=json.dumps(x_name))
        report.set_graph_image(chart_html)
        report.build_graph()

    def resolve_wifi_analysis_device_names(self, devices):
        """Resolve analyzed station ports to the configured YouTube client names."""
        station_to_hostname = {
            station: hostname for hostname, station in self.hostname_to_station_map.items()
        }
        resource_to_hostname = {
            ".".join(station.split(".")[:2]): hostname
            for station, hostname in station_to_hostname.items()
        }
        return [station_to_hostname.get(
            device, resource_to_hostname.get(".".join(device.split(".")[:2]), device))
            for device in devices]

    def start_connectivity_monitoring(self, args):
        """Start requested connectivity monitoring once for this test."""
        wifi_analysis_requested = getattr(args, "wifi_analysis", False)
        if self.connectivity_started or not (args.enable_bg_ping or wifi_analysis_requested):
            return

        self.connectivity_started = True
        logger.info("Starting requested YouTube connectivity monitoring")
        if args.enable_bg_ping:
            try:
                self.background_ping = InteropPing(
                    host=args.mgr, port=args.mgr_port,
                    target=args.bg_ping_target or args.upstream_port,
                    interval=args.bg_ping_interval,
                    sta_list=[], duration=0,
                    real=True, virtual=False,
                    debug=getattr(args, "debug", False))
                if not self.background_ping.start_background_ping(self.real_sta_list):
                    self.background_ping = None
            except (Exception, SystemExit) as error:
                logger.warning("Background ping could not be started: %s", error)
                self.background_ping = None
        if wifi_analysis_requested:
            self.start_wifi_analysis(
                host=args.mgr, port=args.mgr_port, device_list=self.real_sta_list)

    def stop_connectivity_monitoring(self):
        """Freeze the Wi-Fi window and stop ping before report/cleanup work."""
        if self.connectivity_end_time is not None:
            return
        self.connectivity_end_time = int(time.time() * 1000)
        if self.background_ping:
            try:
                self.background_ping.stop_background_ping()
            except (Exception, SystemExit) as error:
                logger.warning("Background ping could not be stopped cleanly: %s", error)

    def start_wifi_analysis(self, host, port, device_list):
        """Start live Wi-Fi message monitoring for the devices under test."""
        self.wifi_analysis = None
        self.wifi_analysis_stats = {}
        self.wifi_analysis_log = None
        self.wifi_analysis_monitoring = False
        if not device_list:
            return
        try:
            resource_ids = list(dict.fromkeys(
                ".".join(device.split(".")[:2]) for device in device_list))
            self.wifi_analysis = ClientAnalysis(
                host=host, port=port, device_list=resource_ids,
                debug=getattr(self, "debug", False))
            self.wifi_analysis.start_monitoring()
            self.wifi_analysis_monitoring = True
        except (Exception, SystemExit) as error:
            logger.warning("Wifi connectivity analysis could not be started: %s", error)
            self.wifi_analysis = None

    def stop_wifi_analysis(self):
        """Stop live Wi-Fi monitoring and retain its per-device statistics."""
        if not getattr(self, 'wifi_analysis_monitoring', False):
            return
        self.wifi_analysis_monitoring = False
        if self.wifi_analysis._monitor_file_name:
            self.wifi_analysis_log = os.path.join(
                "Wifi_Messages", self.wifi_analysis._monitor_file_name)
        try:
            self.wifi_analysis_stats = self.wifi_analysis.stop_monitoring()
        except (Exception, SystemExit) as error:
            logger.warning("Wifi connectivity analysis results could not be collected: %s", error)

    def _playback_stats_window(self):
        """Return the server-observed first/latest playback-stat arrival times."""
        with self.playback_stats_lock:
            start_time = self.playback_stats_start_time
            end_time = self.playback_stats_end_time
        if start_time is None or end_time is None or end_time < start_time:
            return None
        return start_time, end_time

    def _filtered_wifi_analysis(self, window):
        """Limit collected Wi-Fi messages and derived counts to the playback window."""
        stats = getattr(self, 'wifi_analysis_stats', None)
        analysis = getattr(self, 'wifi_analysis', None)
        messages = getattr(analysis, 'device_messages', None) if analysis else None
        if not stats or not messages:
            return stats, None

        start_ms, end_ms = (int(value * 1000) for value in window)
        filtered_messages = {}
        filtered_stats = {device: dict(values) for device, values in stats.items()}
        for device, categories in messages.items():
            filtered_messages[device] = {}
            for category, entries in categories.items():
                filtered_messages[device][category] = []
                for entry in entries:
                    try:
                        timestamp = int(entry.get("timestamp"))
                    except (TypeError, ValueError):
                        continue
                    if start_ms <= timestamp <= end_ms:
                        filtered_messages[device][category].append(entry)

            if device in filtered_stats:
                counts = {
                    category: len(entries)
                    for category, entries in filtered_messages[device].items()
                }
                filtered_stats[device].update(
                    analysis._finalize_device_counts(device, counts))
        return filtered_stats, filtered_messages

    def add_wifi_analysis_to_report(self, report, window):
        """Append Wi-Fi events measured during the playback-stat window."""
        wifi_stats, filtered_messages = self._filtered_wifi_analysis(window)
        wifi_analysis_log = getattr(self, 'wifi_analysis_log', None)
        if filtered_messages is not None:
            try:
                with open(os.path.join(report.path_date_time, "wifi_analysis_messages.json"),
                          "w", encoding="utf-8") as log_file:
                    json.dump(filtered_messages, log_file)
            except OSError as error:
                logger.warning("Filtered wifi analysis messages could not be saved: %s", error)
        elif wifi_analysis_log and os.path.exists(wifi_analysis_log):
            try:
                shutil.copy(wifi_analysis_log, os.path.join(
                    report.path_date_time, "wifi_analysis_messages.json"))
            except OSError as error:
                logger.warning("Wifi analysis messages could not be copied to the report folder: %s", error)
        if not wifi_stats:
            return
        try:
            devices, connect_attempt, disconnected, scanning, association_rejection, connected, remarks, cx_time = \
                ClientAnalysis.stats_to_lists(wifi_stats)
            devices = self.resolve_wifi_analysis_device_names(devices)

            categories = ["Disconnected", "Scans", "Association Attempts", "Association Rejected", "Connected"]
            totals = [sum(disconnected), sum(scanning), sum(connect_attempt), sum(association_rejection), sum(connected)]
            # Red=Disconnected, Yellow=Scans, Orange=Association Attempts, Grey=Rejected, Green=Connected.
            colors = ['#e74c3c', '#f1c40f', '#e67e22', '#95a5a6', '#27ae60']

            report.set_obj_html(
                _obj_title="Client Connectivity Event Summary",
                _obj="This graph summarizes connection-related events observed between the first and latest "
                     "YouTube playback statistics received by the test. "
                     "These metrics provide insight into client stability and wireless connectivity performance.")
            report.build_objective()
            # One named+colored series per category (stacked, so still full bar width) instead of one combined series, so each category gets its own legend entry.
            data_set = [[value if i == series_index else 0 for i, value in enumerate(totals)]
                        for series_index in range(len(categories))]
            graph = lf_bar_graph(_data_set=data_set,
                                 _xaxis_name="",
                                 _yaxis_name="Count",
                                 _xaxis_categories=categories,
                                 _graph_image_name="wifi_connectivity_status",
                                 _label=categories,
                                 _graph_title="Client Connectivity Status",
                                 _title_size=16,
                                 _color_edge='black',
                                 _bar_width=0.5,
                                 _figsize=(10, 6),
                                 _legend_loc="best",
                                 _dpi=96,
                                 _show_bar_value=True,
                                 _enable_csv=True,
                                 _stacked=True,
                                 _color=colors,
                                 _color_name=colors)
            graph_png = graph.build_bar_graph()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.set_csv_filename(f"{graph.graph_image_name}.csv")
            report.move_csv_file()
            report.build_graph()

            dataframe = pd.DataFrame({
                "Device": devices,
                "Association Attempts": connect_attempt,
                "Disconnected": disconnected,
                "Scanning": scanning,
                "Association Rejection": association_rejection,
                "Connected": connected,
            })
            report.set_table_title("Wifi Connectivity Analysis")
            report.build_table_title()
            report.set_table_dataframe(dataframe)
            report.build_table()
        except Exception as e:
            logger.warning("Wifi connectivity analysis could not be added to the report: %s", e)

    def _add_connectivity_report(self, report):
        """Include connectivity results limited to the observed playback-stat window."""
        window = self._playback_stats_window()
        if window is None:
            report.set_obj_html(
                _obj_title="Client Connectivity Status Throughout the Test Duration",
                _obj="No playback-statistics window is available, so connectivity results cannot be aligned "
                     "with the actual YouTube playback period.")
            report.build_objective()
            return

        self.add_wifi_analysis_to_report(report, window)
        ping = getattr(self, "background_ping", None)
        if not ping or not ping.bg_stats:
            report.set_obj_html(
                _obj_title="Client Connectivity Status Throughout the Test Duration",
                _obj="No background-ping results are available. Enable --enable_bg_ping and verify that ping starts "
                     "successfully on the clients to collect the connectivity timeline and ping statistics.")
            report.build_objective()
            return
        self._add_background_ping_timeline_to_report(report, window)
        self._add_background_ping_stats_to_report(report, window)

    @staticmethod
    def _ping_window_offsets(ping, window):
        """Return collector-relative start/end offsets for the playback window."""
        if ping.bg_start_time is None or ping.bg_stop_time is None:
            return None
        start_time = max(window[0], ping.bg_start_time)
        end_time = min(window[1], ping.bg_stop_time)
        if end_time < start_time:
            return None
        return (start_time - ping.bg_start_time,
                end_time - ping.bg_start_time,
                end_time - start_time)

    def _windowed_ping_results(self):
        """Return cached per-client ping results for the playback-stat window."""
        if self.windowed_ping_stats is not None:
            return self.windowed_ping_stats

        self.windowed_ping_stats = {}
        ping = getattr(self, "background_ping", None)
        window = self._playback_stats_window()
        offsets = self._ping_window_offsets(ping, window) if ping and window else None
        if offsets is None:
            return self.windowed_ping_stats

        window_start, window_end, _ = offsets
        interval = float(ping.interval)
        for device in ping.real_sta_list:
            metadata = ping.bg_stats.get(device, {})
            samples = {
                sequence: value
                for sequence, value in (ping.bg_packet_results.get(device) or {}).items()
                if sequence * interval > window_start
                and (sequence - 1) * interval < window_end
            }
            received_samples = [value for value in samples.values() if value > 0]
            sent = len(samples)
            received = len(received_samples)
            self.windowed_ping_stats[device] = {
                **metadata,
                "samples": samples,
                "sent": sent,
                "recv": received,
                "loss_percent": round(100 * (sent - received) / sent, 2) if sent else None,
                "avg_rtt": round(sum(received_samples) / received, 3) if received else None,
            }
        return self.windowed_ping_stats

    def _add_background_ping_stats_to_report(self, report, window):
        """Build ping statistics only from samples inside the playback window."""
        ping = self.background_ping
        offsets = self._ping_window_offsets(ping, window)
        if offsets is None:
            return
        _, _, duration = offsets
        rows = []
        for device in ping.real_sta_list:
            result = self._windowed_ping_results().get(device, {})
            rows.append({
                "Wireless Client": result.get("name", device),
                "MAC": result.get("mac", ""),
                "RSSI (dBm)": result.get("rssi", ""),
                "Channel": result.get("channel", ""),
                "Packets Sent": result.get("sent", 0),
                "Packets Received": result.get("recv", 0),
                "Packet Loss %": result.get("loss_percent") if result.get("sent") else "NA",
                "AVG RTT (ms)": result.get("avg_rtt") if result.get("recv") else "NA",
            })
        report.set_table_title(
            "Ping statistics during observed YouTube playback "
            "(target {}, duration {}, {}s interval)".format(
                ping.target, str(timedelta(seconds=int(duration))), ping.interval))
        report.build_table_title()
        report.set_table_dataframe(pd.DataFrame(rows))
        report.build_table()

    def _add_background_ping_timeline_to_report(self, report, window):
        """Add the ping timeline cropped to the playback-stat window."""
        ping = self.background_ping
        if not ping or not ping.bg_stats or ping.bg_start_time is None or ping.bg_stop_time is None:
            return
        try:
            offsets = self._ping_window_offsets(ping, window)
            if offsets is None:
                return
            window_start, window_end, test_seconds = offsets
            interval = float(ping.interval)
            clients, stations, segments = [], [], []
            for device in ping.real_sta_list:
                result = self._windowed_ping_results().get(device, {})
                sequences = result.get("samples", {})
                spans = []
                for sequence in sorted(sequences):
                    start = max(window_start, (sequence - 1) * interval)
                    end = min(window_end, sequence * interval)
                    if end <= start:
                        continue
                    spans.append([
                        "drop" if sequences[sequence] == 0 else "up",
                        start - window_start,
                        end - window_start,
                    ])
                merged = []
                for span in spans:
                    if (merged and merged[-1][0] == span[0]
                            and span[1] <= merged[-1][2]):
                        merged[-1][2] = span[2]
                    else:
                        merged.append(span)
                segments.extend({
                    "clientIndex": len(clients), "start": round(start, 3),
                    "end": round(end, 3), "status": status,
                } for status, start, end in merged)
                clients.append(result.get("name", device))
                stations.append(device)
            payload = {
                "clients": clients, "stations": stations, "segments": segments,
                "duration": round(test_seconds, 3),
                "emptyMessage": "No time-series ping samples were collected",
            }
            report.set_obj_html(
                _obj_title="Client Connectivity Results Throughout the Test Duration",
                _obj="The graph illustrates connectivity between the first and latest YouTube playback "
                     "statistics received by the test. Green segments represent "
                     "successful responses, while red segments indicate packet loss or connectivity drops "
                     "observed during the test.")
            report.build_objective()
            report.set_custom_html("""
                <div class='chart-card'>
                  <h3>Wireless Client Connectivity Status vs Time</h3>
                  <div id='background-ping-connectivity-timeline' class='chart'></div>
                  <script>
                    window.__lfModernReport.renderConnectivityTimeline(
                        'background-ping-connectivity-timeline', {payload});
                  </script>
                </div>
                """.format(payload=json.dumps(payload)))
            report.build_custom()
            report.set_custom_html("")
        except Exception as error:
            logger.warning("Background ping timeline could not be added to the report: %s", error)

    def _build_configuration_card(self, report, configuration):
        items = []
        for label, value in configuration.items():
            if label in {"Configured Devices", "Number of Devices", "No of Devices :"}:
                continue
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(part) for part in value)
            items.append({"label": escape(str(label)), "value": escape(str(value))})
        report.build_info_card(title="Test Configuration", items=items)
        platforms = {"android": "Android", "windows": "Windows", "linux": "Linux",
                     "macos": "macOS", "ios": "iOS"}
        report.build_device_summary_card([
            {"name": name, "platform": platforms.get(str(platform).lower(), str(platform))}
            for name, platform in zip(self.real_sta_hostname, self.real_sta_os_types)
        ])

    @staticmethod
    def _add_youtube_report_style(report):
        report.set_custom_html("""<style>
            .table-wrap { width: 100%; box-shadow: var(--shadow); }
            .youtube-observations { width: 100%; table-layout: fixed; }
            .youtube-observations th:nth-child(1) { width: 23%; }
            .youtube-observations th:nth-child(2) { width: 60%; }
            .youtube-observations th:nth-child(3) { width: 17%; }
            table.data-table.youtube-observations td { overflow-wrap: anywhere; text-align: left; }
            .info-item-value { overflow-wrap: anywhere; }
            .youtube-results-heading {
                margin: 24px 0 12px; padding-bottom: 8px;
                font-size: 24px; font-weight: 700;
                border-bottom: 1px solid #dbe2ea;
                break-after: avoid; page-break-after: avoid;
            }
            .youtube-results-heading + .info-card { margin-top: 0; padding-top: 8px; }
        </style>""")
        report.build_custom()
        report.set_custom_html("")

    def create_report(self, data=None, ui_report_dir=None, iot_summary=None):
        ui_report_dir = ui_report_dir or self.ui_report_dir

        if self.do_webUI:
            self.report = lf_report(_output_pdf='youtube_streaming.pdf',
                                    _output_html='youtube_streaming.html',
                                    _results_dir_name="youtube_streaming_report",
                                    _path=ui_report_dir)
        else:
            self.report = lf_report(_output_pdf='youtube_streaming.pdf',
                                    _output_html='youtube_streaming.html',
                                    _results_dir_name="youtube_streaming_report",
                                    _path='')
        self.report_path = self.report.path
        self.report_path_date_time = self.report.path_date_time

        # setting report title
        self.report.set_title(
            'LANforge Interop<br>YouTube Streaming Test Including IoT Devices'
            if iot_summary else
            'LANforge Interop<br>YouTube Streaming Test<br>'
            '<span style="font-size:0.55em;">(Real Client Performance Validation)</span>')
        self.report.build_banner()
        self._add_youtube_report_style(self.report)
        # objective and description
        if iot_summary:
            self.report.set_obj_html(
                _obj_title='Test Overview',
                _obj=(
                    "The Candela YouTube Streaming Test Including IoT Devices is designed to evaluate an Access Point's "
                    "performance and stability when handling both Real clients (Windows, Linux, MacBook, Android, iOS) and IoT "
                    "devices (controlled via Home Assistant). "
                    "For Real clients, the test simulates real-world streaming scenarios by playing YouTube videos and "
                    "collecting key statistics such as video resolution, buffer health, total frames, and dropped frames to "
                    "validate smooth playback across multiple devices and operating systems. "
                    "For IoT clients, the test concurrently executes device-specific actions (e.g., camera streaming, switch "
                    "toggling, lock/unlock) and monitors success rate, latency, and failure rate. The goal is to ensure that "
                    "the AP can sustain high-quality YouTube streaming performance for Real clients while reliably supporting "
                    "IoT device operations with consistent responsiveness and control."
                )
            )
        else:
            self.report.set_obj_html(
                _obj_title='Test Overview',
                _obj=(
                    "The objective is to conduct an automated YouTube streaming test across multiple Android devices and laptops "
                    "to gather streaming performance statistics. The test will collect key metrics related to video playback "
                    "behavior, quality, buffering, and stability. Additionally, automated graphs will be generated using the collected data."
                )
            )
        self.report.build_objective()

        if self.config:

            # Test setup info
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration,
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,
                "SSID": self.ssid,
                "Security": self.security,

            }

        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            gp_pairs = zip(self.selected_groups, self.selected_profiles)
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

            # Test setup info
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration,
                'Resolution': self.resolution,
                "Configuration": gp_map,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,

            }
        else:
            # Test setup info
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration,
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,

            }
        if iot_summary:
            test_setup_info['Test Name'] = 'YouTube Streaming Test with IoT Devices'
            test_setup_info = with_iot_params_in_table(test_setup_info, iot_summary)
        if self.is_continuous_run:
            test_setup_info['Traffic Duration (hh:mm:ss)'] = "NA"
        else:
            total_seconds = int(float(self.duration) * 60)
            test_setup_info['Traffic Duration (hh:mm:ss)'] = (
                f"{total_seconds // 3600:02d}:{total_seconds % 3600 // 60:02d}:{total_seconds % 60:02d}")
        test_setup_info['Video Resolution'] = test_setup_info.pop('Resolution')
        test_setup_info['Number of Devices'] = test_setup_info.pop('No of Devices :')
        test_setup_info.pop('Duration (in Minutes)', None)
        if self.is_continuous_run:
            test_setup_info['Coordinates'] = self.coordinates_list
            test_setup_info['Total Cycles'] = self.cycles

        metrics = self._youtube_report_metrics()
        measured = [(name, item) for name, item in metrics.items() if item]
        scored = [(name, item) for name, item in measured if item["score"] is not None]
        average_score = sum(item["score"] for _, item in scored) / len(scored) if scored else None
        average_text = f"{average_score:.2f}%" if average_score is not None else "Unavailable"
        # Rate the same scored clients used in the average, even if others lack data.
        overall_rating = (self._overall_score_rating(average_score)
                          if scored else "Incomplete data")
        rating_html = self._rating_html(overall_rating)
        self.report.build_info_card(title="Overall Test Verdict", items=[
            {"label": "Total Devices Configured", "value": len(self.real_sta_hostname)},
            {"label": "Devices with Streaming Data", "value": len(measured)},
            {"label": "Devices with Complete Scoring Data", "value": len(scored)},
            {"label": "Average YouTube Streaming Score (Scored Devices)", "value": average_text},
            {"label": "Overall Rating", "value": rating_html},
        ])
        findings = self._test_summary_findings(metrics, overall_rating)
        self.report.set_obj_html(_obj_title="Key Findings", _obj="<ul>" + "".join(
            f"<li>{escape(finding)}</li>" for finding in findings) + "</ul>")
        self.report.build_objective()

        self.report.set_custom_html('<h2 class="youtube-results-heading">Test Results</h2>')
        self.report.build_custom()
        self.report.set_custom_html("")
        self.report.set_obj_html(
            _obj_title="Dropped Frames per Device (%)",
            _obj="The graph below illustrates the percentage of dropped video frames observed for each wireless "
                 "device during the test. The X-axis represents the dropped frame percentage, while the Y-axis lists "
                 "the individual wireless client devices.")
        self.report.build_objective()
        self._build_dropped_frames_percentage_graph(self.report, metrics)

        self.report.set_obj_html(
            _obj_title="Video Playback Resolution Distribution Across Devices",
            _obj="Each stacked bar shows the percentage of observed playback time at each resolution. "
                 "Intervals use the resolution at their starting sample; no duration is assumed after the last sample. "
                 "Hover over a segment to inspect its resolution and percentage.")
        self.report.build_objective()
        self._build_resolution_distribution_graph(self.report, metrics)

        table_rows = []
        observation_rows = []
        for index, hostname in enumerate(self.real_sta_hostname):
            item = metrics.get(hostname)
            mac = self.mac_list[index] if index < len(self.mac_list) else "NA"
            ssid = self.ssid_list[index] if index < len(self.ssid_list) else "NA"
            rssi = self.rssi_list[index] if index < len(self.rssi_list) else "NA"
            rssi = re.sub(r"\s*dBm\s*$", "", str(rssi), flags=re.IGNORECASE)
            if not item:
                table_rows.append({"Device Name": hostname, "MAC": mac, "SSID": ssid, "RSSI (dBm)": rssi,
                                   "Avg Buffer Health (s)": "Unavailable", "Dropped Frames (%)": "Unavailable",
                                   "Avg Network Activity (KB)": "Unavailable", "Score": "Unavailable",
                                   "Rating": "No streaming data"})
                observation_rows.append({"Device Name": hostname, "Rating": "No streaming data",
                                         "Observations": "No valid streaming samples were collected; inspect the client log."})
                continue
            network = item["network_activity"] if item["network_activity"] is not None else (
                "Not applicable" if self.real_sta_os_types[index].lower() == "android" else "Unavailable")
            table_rows.append({
                "Device Name": hostname, "MAC": mac, "SSID": ssid, "RSSI (dBm)": rssi,
                "Avg Buffer Health (s)": item["avg_buffer"],
                "Dropped Frames (%)": item["drop_percent"], "Avg Network Activity (KB)": network,
                "Score": item["score"] if item["score"] is not None else "Unavailable", "Rating": item["rating"],
            })
            observations = self._client_observations(hostname, item, rssi)
            observation_rows.append({
                "Device Name": hostname, "Rating": item["rating"],
                "Observations": "<br>\u2022 " + "<br>\u2022 ".join(escape(text) for text in observations),
            })

        if table_rows and self.selected_groups and self.selected_profiles:
            groups_devices_map = self.configobj.get_groups_devices(
                data=self.selected_groups, groupdevmap=True)
            for group in self.selected_groups:
                group_rows = [row for row in table_rows
                              if row["Device Name"] in groups_devices_map.get(group, [])]
                if group_rows:
                    self.report.set_table_title(
                        f"Per-client Streaming Performance Metrics and Ratings - {group}")
                    self.report.build_table_title()
                    self._build_client_metrics_table(group_rows)
        elif table_rows:
            self.report.set_table_title("Per-client Streaming Performance Metrics and Ratings")
            self.report.build_table_title()
            self._build_client_metrics_table(table_rows)
        self.report.set_table_title("Per-client Observations")
        self.report.build_table_title()
        if observation_rows:
            observations_frame = pd.DataFrame(
                observation_rows, columns=["Device Name", "Observations", "Rating"])
            observations_frame["Device Name"] = observations_frame["Device Name"].map(lambda name: escape(str(name)))
            observations_frame["Rating"] = observations_frame["Rating"].map(self._rating_html)
            observations_html = observations_frame.to_html(
                index=False, escape=False, justify="center", classes="data-table youtube-observations")
            self.report.set_custom_html("<div class='table-wrap'>" + observations_html + "</div>")
            self.report.build_custom()
            self.report.set_custom_html("")

        # Match the report specification: connectivity analysis precedes the
        # per-client buffer-health timelines.
        self._add_connectivity_report(self.report)

        for file_path in self.devices_list:
            self.move_files(file_path, self.report_path_date_time)

        original_dir = os.getcwd()

        csv_files = [f for f in os.listdir(self.report_path_date_time) if f.endswith('_youtube_stats_report.csv')]
        os.chdir(self.report_path_date_time)

        for file_name in csv_files:
            data = pd.read_csv(file_name)
            report_device_name = file_name.removesuffix('_youtube_stats_report.csv')
            if "Instance Name" in data.columns and not data.empty:
                instance_names = data["Instance Name"].dropna().astype(str)
                if not instance_names.empty:
                    report_device_name = instance_names.iloc[0]
            if (self.scoring and file_name.endswith("_youtube_stats_report.csv")
                    and metrics.get(report_device_name)
                    and metrics[report_device_name]["score"] is not None):
                device_name = report_device_name
                if device_name not in self.real_sta_hostname:
                    device_name = file_name.split('_youtube_stats_report.csv')[0]

                if device_name in self.real_sta_hostname:
                    os_type = self.real_sta_os_types[
                        self.real_sta_hostname.index(device_name)
                    ]

                    score_data = self.calculate_device_score(
                        data,
                        os_type=os_type
                    )

                    weights = score_data["weights"]

                    rows = [
                        [
                            "Average Connection Speed",
                            score_data["avg_speed"],
                            score_data["speed_score"],
                            round(weights["speed"], 2),
                            round(score_data["speed_score"] * weights["speed"], 2),
                        ],
                        [
                            "Average Buffer Health",
                            score_data["avg_buffer"],
                            score_data["buffer_score"],
                            round(weights["buffer"], 2),
                            round(score_data["buffer_score"] * weights["buffer"], 2),
                        ],
                        [
                            "Dropped Frame %",
                            score_data["drop_percent"],
                            score_data["drop_score"],
                            round(weights["drop"], 2),
                            round(score_data["drop_score"] * weights["drop"], 2),
                        ],
                        [
                            "Resolution Stability %",
                            score_data["stability_percent"],
                            score_data["resolution_score"],
                            round(weights["resolution"], 2),
                            round(score_data["resolution_score"] * weights["resolution"], 2),
                        ],
                        [
                            "Protocol",
                            5,
                            score_data["protocol_score"],
                            round(weights["protocol"], 2),
                            round(score_data["protocol_score"] * weights["protocol"], 2),
                        ],
                    ]

                    if score_data["network_score"] is not None:
                        rows.append(
                            [
                                "Network Activity (Fluctuation %)",
                                score_data["fluctuation"],
                                score_data["network_score"],
                                round(weights["network"], 2),
                                round(
                                    score_data["network_score"] * weights["network"],
                                    2
                                ),
                            ]
                        )

                    score_df = pd.DataFrame(
                        rows,
                        columns=[
                            "Metric",
                            "Achieved Value",
                            "Calculated Score",
                            "Weightage",
                            "Weighted Score",
                        ],
                    )

                    score_df.loc[len(score_df)] = [
                        "Overall Weighted Score",
                        "",
                        "",
                        "",
                        score_data["overall_score"],
                    ]

                    score_df.to_csv(
                        f"{file_name.split('.')[0]}_score.csv",
                        index=False
                    )
                else:
                    logging.warning(
                        f"Skipping scoring for {file_name}: device not found in configured hostnames"
                    )
            timestamps = self._elapsed_seconds(data['TimeStamp'])
            buffer_health = pd.to_numeric(data['BufferHealth'], errors='coerce')
            valid_samples = buffer_health.notna() & timestamps.notna()
            timestamps = timestamps[valid_samples]
            buffer_health = buffer_health[valid_samples]
            if buffer_health.empty:
                logging.warning("No valid buffer-health samples found in %s", file_name)
                continue

            self._build_buffer_health_graph(
                self.report, report_device_name, timestamps, buffer_health, clock_times=data['TimeStamp'])

        os.chdir(original_dir)
        if iot_summary:
            add_iot_report_section(self.report, iot_summary)

        if self.do_bandsteering:
            self.add_bandsteering_report_section(report=self.report)

        # Keep configuration last, matching the approved report sequence.
        self._build_configuration_card(self.report, test_setup_info)

        # Closing
        self.report.build_footer()
        self.report.write_html()
        self.report.write_pdf(_page_width="420mm", _page_height="420mm")

    def json_get_with_retry(self, url, wait_time=40, poll_interval=5):
        """
        Calls self.json_get(url), retrying every poll_interval seconds for up
        to wait_time seconds if LANforge returns no response. Aborts the test
        if it still hasn't responded once wait_time has elapsed.
        """
        start_time = time.time()
        response = self.json_get(url)
        while response is None and (time.time() - start_time) < wait_time:
            logger.warning(f"GET {url} returned no response from LANforge; retrying...")
            time.sleep(poll_interval)
            response = self.json_get(url)

        if response is None:
            logger.error(
                f"GET {url} returned no response from LANforge after waiting "
                f"{wait_time} seconds. Aborting test."
            )
            exit(1)

        return response

    def write_endpoint_status_csv(self, csv_file, endpoint_name, status,
                                  api_response=None):
        """Append an endpoint status change to the monitoring CSV."""
        file_exists = os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0
        with open(csv_file, mode="a", newline="") as csv_handle:
            writer = csv.writer(csv_handle)
            if not file_exists:
                writer.writerow([
                    "timestamp", "endpoint_name", "status", "api_response"
                ])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                endpoint_name,
                status,
                json.dumps(api_response, default=str, sort_keys=True),
            ])

    def monitor_endpoint_status_changes(self, wait_time=40, poll_interval=5):
        """
        Record endpoint status changes.  If every endpoint disappears, retry
        for ``wait_time`` seconds and then unwind to report generation.
        """
        current_path = self.ui_report_dir if self.do_webUI else os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(current_path, "endpoint_status_changes.csv")
        if csv_file not in self.devices_list:
            self.devices_list.append(csv_file)
        created_endp = self.generic_endps_profile.created_endp
        start_time = time.time()
        while True:
            if self.stop_signal:
                logger.info(
                    "WebUI stop requested while waiting for endpoint data; "
                    "unwinding directly to report generation."
                )
                raise WebUIStopRequested

            endpoint_data = {}
            endpoint_responses = {}
            for gen_endp in created_endp:
                if self.stop_signal:
                    logger.info(
                        "WebUI stop requested during endpoint polling; "
                        "unwinding directly to report generation."
                    )
                    raise WebUIStopRequested
                generic_endpoint = self.json_get(f"/generic/{gen_endp}")
                endpoint_responses[gen_endp] = generic_endpoint
                if generic_endpoint and "endpoint" in generic_endpoint:
                    endpoint_data[gen_endp] = generic_endpoint

            newly_missing = [
                gen_endp for gen_endp in created_endp
                if gen_endp not in endpoint_data
                and self.endpoint_last_status.get(gen_endp) != "MISSING"
            ]
            missing_url = f"/generic/{','.join(sorted(set(created_endp)))}"
            present_keys = []
            if newly_missing:
                try:
                    combined_response = self.json_get(missing_url)
                    if combined_response and "endpoints" in combined_response:
                        present_keys = [
                            name for endpoint in combined_response["endpoints"]
                            for name in endpoint
                        ]
                    elif combined_response and "endpoint" in combined_response:
                        present_keys = list(endpoint_data)
                except Exception:
                    logger.exception(
                        "Unable to retrieve combined endpoint status from %s",
                        missing_url,
                    )

            for gen_endp in created_endp:
                generic_endpoint = endpoint_data.get(gen_endp)
                current_status = (
                    generic_endpoint["endpoint"].get("status", "")
                    if generic_endpoint else "MISSING"
                )
                if self.endpoint_last_status.get(gen_endp) != current_status:
                    if current_status == "MISSING":
                        logger.info(
                            "Endpoint '%s' is unavailable (endpoint_present=False). "
                            "It may have been deleted, may not have been created, "
                            "or may be temporarily disconnected. Continuing to "
                            "monitor it.\nURL: %s\nEndpoint keys present: %s",
                            gen_endp,
                            missing_url,
                            present_keys,
                        )
                    else:
                        logger.info(
                            "Endpoint %s status changed to: %s",
                            gen_endp,
                            current_status,
                        )
                    self.write_endpoint_status_csv(
                        csv_file,
                        gen_endp,
                        current_status,
                        (present_keys if current_status == "MISSING" else
                         endpoint_responses.get(gen_endp)),
                    )
                    self.endpoint_last_status[gen_endp] = current_status

            if endpoint_data:
                return True

            missing_for = time.time() - start_time
            if missing_for >= wait_time:
                logger.error(
                    "All %s generic endpoint(s) have been unreachable for %.0fs "
                    "(limit %ss) - stopping the test.",
                    len(created_endp),
                    missing_for,
                    wait_time,
                )
                self.write_endpoint_status_csv(
                    csv_file,
                    "ALL",
                    "ALL_ENDPOINTS_UNREACHABLE",
                    endpoint_responses,
                )
                raise AllEndpointsUnreachable(
                    f"All generic endpoints were unreachable for {wait_time} seconds"
                )

            logger.warning(
                "All %s generic endpoint(s) are unreachable - retrying... "
                "%.0fs/%ss before giving up and stopping the test.",
                len(created_endp),
                missing_for,
                wait_time,
            )
            # Sleep in short intervals so a WebUI stop is acted on promptly,
            # even while this method is in its missing-endpoint retry window.
            retry_deadline = time.monotonic() + poll_interval
            while time.monotonic() < retry_deadline:
                if self.stop_signal:
                    logger.info(
                        "WebUI stop requested while waiting for endpoint data; "
                        "unwinding directly to report generation."
                    )
                    raise WebUIStopRequested
                remaining = retry_deadline - time.monotonic()
                if remaining <= 0:
                    break
                time.sleep(min(0.25, remaining))

    def check_gen_cx(self, stall_timeout=300):
        """Check whether all generic endpoints have reached an idle state.
        Treat unresponsive or stalled endpoints as resolved after stall_timeout.
        """
        if not hasattr(self, "_gen_cx_stall_since"):
            self._gen_cx_stall_since = {}
        if not hasattr(self, "_gen_cx_timed_out"):
            self._gen_cx_timed_out = set()

        idle_statuses = {"Stopped", "WAITING", "NO-CX", "PHANTOM", "FTM_WAIT"}
        now = time.monotonic()
        ready = True

        try:
            for gen_endp in set(self.generic_endps_profile.created_endp):
                generic_endpoint = self.json_get(f"/generic/{gen_endp}")

                if not generic_endpoint or "endpoint" not in generic_endpoint:
                    endp_status = None
                else:
                    endp_status = generic_endpoint["endpoint"].get("status", "")

                if endp_status in idle_statuses:
                    self._gen_cx_stall_since.pop(gen_endp, None)
                    self._gen_cx_timed_out.discard(gen_endp)
                    continue

                if gen_endp in self._gen_cx_timed_out:
                    continue

                stall_start = self._gen_cx_stall_since.setdefault(gen_endp, now)
                stalled_for = now - stall_start
                if stalled_for >= stall_timeout:
                    logger.warning(
                        "Endpoint %s remained unresolved with status %r for %.0f "
                        "seconds (limit: %s); continuing without waiting for it",
                        gen_endp,
                        endp_status,
                        stalled_for,
                        stall_timeout,
                    )
                    self._gen_cx_timed_out.add(gen_endp)
                    continue

                ready = False

            return ready
        except Exception:
            logger.exception("Error while checking generic endpoint status")
            return False

    def change_port_to_ip(self, upstream_port):
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
        if upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            response = self.json_get_with_retry(f'/port/{shelf}/{resource}/{port}?fields=ip')
            try:
                target_port_ip = response['interface']['ip']
                upstream_port = target_port_ip
            except KeyError as e:
                logger.error(
                    "/port/%s/%s/%s/?fields=ip response is not in the expected format, missing key %s. "
                    "Data received:\n%s",
                    shelf,
                    resource,
                    port,
                    e,
                    json.dumps(response, indent=2, default=str),
                )
                exit(1)
            except Exception as e:
                logging.warning(f'Could not resolve IP for port {upstream_port}: {e}. Proceeding with the given upstream_port {upstream_port}.')
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        self.upstream_port = upstream_port

        return upstream_port

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
                    filtered_list.append(device)

            except Exception as e:
                logger.exception(f"Error processing device {device}: {e}")
                continue

        if isinstance(device_list, str):
            filtered_list = ','.join(filtered_list)

        self.device_list = filtered_list
        return filtered_list

    def get_android_device_data(self):
        """
        Fetch and process Android device information from the ADB interop API.

        This method queries the '/adb' endpoint to retrieve connected Android
        device details, matches devices against the configured user list,
        and extracts relevant metadata for test execution.

        Behavior:
        - Supports both dictionary and list response formats from the API
        - Filters devices based on matching 'user-name' entries
        - Extracts device serial numbers and LANforge resource IDs
        - Builds LANforge port identifiers in the format: 1.<resource>.eth0
        - Populates internal lists used for endpoint and test setup

        Side Effects:
        - Updates self.serial_list with Android device serial numbers
        - Updates self.lanforge_port_list with LANforge port identifiers
        - Sets self.lanforge_os_type to 'Linux' for all discovered devices
        - Generates a comma-separated serial string in self.serial_list_str

        Returns:
            None
        """
        interop_data = self.json_get_with_retry('/adb')
        try:
            interop_mobile_data = interop_data.get('devices', {})

            if isinstance(interop_mobile_data, dict):
                for user in self.user_list:
                    if user != '':
                        if interop_mobile_data.get('user-name') == user:

                            serial = interop_mobile_data.get('name', '')
                            resource = serial.split('.')[1]
                            serial_no = serial.split('.')[2]
                            self.serial_list.append(serial_no)
                            lanforge_port = f"1.{resource}.eth0"
                            self.lanforge_port_list.add(lanforge_port)

            else:
                for user in self.user_list:
                    if user != '':
                        for mobile_device in interop_mobile_data:
                            for serial, device_data in mobile_device.items():
                                if device_data.get('user-name') == user:
                                    resource = serial.split('.')[1]
                                    serial_no = serial.split('.')[2]
                                    self.serial_list.append(serial_no)
                                    lanforge_port = f"1.{resource}.eth0"
                                    self.lanforge_port_list.add(lanforge_port)
                                    break

            self.lanforge_port_list = list(self.lanforge_port_list)
            self.lanforge_os_type = ["Linux"] * len(self.lanforge_port_list)
            self.serial_list_str = ','.join(self.serial_list)
        except KeyError as e:
            logger.error(
                "/adb response is not in the expected format, missing key %s. "
                "Data received:\n%s",
                e,
                json.dumps(interop_data, indent=2, default=str),
            )
            exit(1)
        except Exception as e:
            logger.error(
                f"Unexpected error while parsing /adb response: {e}",
                exc_info=True,
            )
            exit(1)

    def get_device_data(self):
        """
        Collect and correlate device, resource, and port information for real stations.

        This method gathers metadata for devices listed in `self.real_sta_list` by:
        1. Extracting user-specified resource identifiers from real station entries.
        2. Querying the '/resource/all' API to map resources to device names,
        controller IPs, EIDs, and associated users.
        3. Querying the '/port/all' API to locate ports belonging to the matched
        resources, preserving the order defined by the real station list.
        4. Extracting wireless-specific attributes for ports associated with
        the 'wiphy0' parent device.

        The method builds several internal lists that are later used for endpoint
        creation, test execution, and result processing.

        Side Effects:
        - Populates self.device_names with matched device hostnames
        - Populates self.user_list with users associated with each resource
        - Populates self.mac_list with MAC addresses for wireless ports
        - Populates self.rssi_list with signal strength values
        - Populates self.link_rate_list with RX link rates
        - Populates self.ssid_list with SSID values
        - Populates self.wifi_interface_list with wireless interface names for Linux endpoint commands

        Notes:
        - The method preserves the order of devices as specified in
        `self.real_sta_list`.
        - Only ports whose parent device is 'wiphy0' are considered wireless
        and used to collect RSSI, MAC, link rate, and SSID information.
        - This method does not return any value; all results are stored as
        instance attributes.

        Returns:
            None
        """

        ports_list = []
        user_resources = ['.'.join(item.split('.')[:2]) for item in self.real_sta_list]
        self.device_names = []
        self.user_list = []

        # Step 1: Retrieve information about all resources
        response = self.json_get_with_retry("/resource/all")
        try:
            resource_data_list = response.get("resources", [])

            # Step 2: Match user-specified resources with available resources in order.
            for user_resource in user_resources:
                for resource_entry in resource_data_list:
                    for resource_key, resource_values in resource_entry.items():
                        if resource_key == user_resource:
                            self.device_names.append(resource_values['hostname'])
                            ports_list.append({
                                'eid': resource_values['eid'],
                                'ctrl-ip': resource_values['ctrl-ip']
                            })
                            self.user_list.append(resource_values['user'])
                            break
                    else:
                        continue
                    break
                else:
                    logger.error(
                        f"Resource {user_resource} not found in LANforge response. Aborting test."
                    )
                    logger.info(
                        "LANforge resources fetched from /resource/all:\n%s",
                        json.dumps(resource_data_list, indent=2, default=str),
                    )
                    exit(1)
        except KeyError as e:
            logger.error(
                f"/resource/all response is not in the expected format, missing key {e}. "
                "Data received:\n%s",
                json.dumps(response, indent=2, default=str),
            )
            exit(1)
        except Exception as e:
            logger.error(
                f"Unexpected error while parsing /resource/all response: {e}",
                exc_info=True,
            )
            exit(1)

        self.mac_list = []
        self.rssi_list = []
        self.link_rate_list = []
        self.ssid_list = []
        self.wifi_interface_list = []

        # Step 3: Retrieve port information
        response_port = self.json_get_with_retry("/port/all")
        try:
            interfaces_list = response_port.get('interfaces', [])

            # Step 4: Match ports associated with retrieved resources in the order of ports_list
            for port_entry in ports_list:
                expected_eid = port_entry['eid']
                matched_ports = []
                mac = "NA"
                rssi = "NA"
                link_rate = "NA"
                ssid = "NA"
                wifi_interface = "NA"

                for interface in interfaces_list:
                    for port, port_data in interface.items():
                        if '.'.join(port.split('.')[:2]) == expected_eid:
                            matched_ports.append((port, port_data))

                for port_name, port_data in matched_ports:
                    if port_data.get("parent dev") == 'wiphy0' and not port_data.get('down') and port_data.get('ip') != '0.0.0.0':
                        mac = port_data.get("mac") or "NA"
                        rssi = port_data.get("signal")
                        if rssi is None or str(rssi).strip().upper() in ("", "NA"):
                            rssi = "NA"
                        else:
                            rssi_text = str(rssi).strip()
                            rssi = rssi_text if "dbm" in rssi_text.lower() else f"{rssi_text} dBm"
                        link_rate = port_data.get("rx-rate") if port_data.get("rx-rate") is not None else "NA"
                        ssid = port_data.get("ssid") or "NA"
                        port_parts = port_name.split('.')
                        wifi_interface = port_parts[2] if len(port_parts) > 2 else "NA"
                        break

                self.mac_list.append(mac)
                self.rssi_list.append(rssi)
                self.link_rate_list.append(link_rate)
                self.ssid_list.append(ssid)
                self.wifi_interface_list.append(wifi_interface)

                if wifi_interface == "NA":
                    logger.warning(
                        "No active wiphy0 interface with a valid IP was found for "
                        "resource %s; network details will be reported as NA",
                        expected_eid,
                    )
        except KeyError as e:
            logger.error(
                f"/port/all response is not in the expected format, missing key {e}. "
                "Data received:\n%s",
                json.dumps(response_port, indent=2, default=str),
            )
            exit(1)
        except Exception as e:
            logger.error(
                f"Unexpected error while parsing /port/all response: {e}",
                exc_info=True,
            )
            exit(1)

    def perform_robo_test(self):
        if self.do_webUI:
            base_dir = os.path.dirname(os.path.dirname(self.ui_report_dir))
            nav_data = os.path.join(base_dir, 'nav_data.json')  # To generate nav_data.json in webgui folder
            self.robo_obj.nav_data_path = nav_data
        for coordinate in self.coordinates_list:
            if self.stop_signal:
                break
            self.robo_obj.wait_for_battery()
            matched, aborted = self.robo_obj.move_to_coordinate(coord=coordinate)
            if self.stop_signal:
                raise WebUIStopRequested
            if not matched:
                continue
            self.current_cord = coordinate
            if self.rotations_enabled:
                for angle in self.angles_list:
                    if self.stop_signal:
                        break
                    self.robo_obj.wait_for_battery()
                    self.robo_obj.rotate_angle(angle_degree=angle)
                    self.current_angle = angle
                    self.start_generic()
                    duration = self.duration
                    end_time = datetime.now() + timedelta(minutes=duration)
                    logging.info(
                        "Starting data collection for coordinate %s and angle %s at %s",
                        coordinate,
                        angle,
                        datetime.now().astimezone().isoformat(timespec="seconds"),
                    )
                    while (datetime.now() < end_time or not self.check_gen_cx()) and not self.stop_signal:
                        pause, _ = self.robo_obj.wait_for_battery()
                        if pause:
                            self.delete_existing_csvs_for_current_point()
                            self.generic_endps_profile.stop_cx()
                            self.start_generic()
                            end_time = datetime.now() + timedelta(minutes=self.duration)

                        self.monitor_endpoint_status_changes()
                        time.sleep(5)

                    if self.stop_signal:
                        logging.info(
                            "Robot YouTube stop requested; deferring CX shutdown "
                            "to common finalization so clients can upload logs."
                        )
                        return
                    self.generic_endps_profile.stop_cx()
                    logging.info(
                        "Finished data collection for coordinate %s and angle %s at %s",
                        coordinate,
                        angle,
                        datetime.now().astimezone().isoformat(timespec="seconds"),
                    )

            else:
                self.start_generic()
                duration = self.duration
                end_time = datetime.now() + timedelta(minutes=duration)
                logging.info(
                    "Starting data collection for coordinate %s at %s",
                    coordinate,
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )

                while (datetime.now() < end_time or not self.check_gen_cx()) and not self.stop_signal:
                    pause, _ = self.robo_obj.wait_for_battery()
                    if pause:
                        self.delete_existing_csvs_for_current_point()
                        self.generic_endps_profile.stop_cx()
                        self.start_generic()
                        end_time = datetime.now() + timedelta(minutes=self.duration)

                    self.monitor_endpoint_status_changes()
                    time.sleep(5)

                if self.stop_signal:
                    logging.info(
                        "Robot YouTube stop requested; deferring CX shutdown to "
                        "common finalization so clients can upload logs."
                    )
                    return
                self.generic_endps_profile.stop_cx()
                logging.info(
                    "Finished data collection for coordinate %s at %s",
                    coordinate,
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )

    def perform_robo_bandsteering_test(self):
        # Continuous robot run: band steering keeps its own wording, otherwise it is a continuous measurement
        if self.do_bandsteering:
            logging.info(
                "Starting band-steering robot YouTube test at %s",
                datetime.now().astimezone().isoformat(timespec="seconds"),
            )
        else:
            logging.info(
                "Starting robot YouTube test with continuous measurement at %s",
                datetime.now().astimezone().isoformat(timespec="seconds"),
            )

        self.robo_obj.total_cycles = self.cycles
        self.robo_obj.coordinate_list = self.coordinates_list
        coordinate_list_with_robo = self.robo_obj.get_coordinates_list()
        self.wait_stop_aware(5, "before coordinate traversal")
        curr_cycle = 1
        logger.info("Starting cycle {} of {}".format(curr_cycle, self.cycles))
        for coordinate in coordinate_list_with_robo:
            if self.stop_signal:
                break
            logging.info(f"Moving robot to coordinate: {coordinate}")
            if self.to_coordinate == "":
                self.to_coordinate = coordinate
                self.start_generic()
            else:
                self.from_coordinate = self.to_coordinate
                self.to_coordinate = coordinate

            self.robo_obj.wait_for_battery(
                monitor_function=self.check_robo_stop
            )

            matched, abort = self.robo_obj.move_to_coordinate(
                coord=coordinate,
                monitor_function=self.check_robo_stop,
            )
            if self.stop_signal:
                raise WebUIStopRequested
            if matched:
                logger.info("Reached the coordinate {}".format(coordinate))
            if abort:
                break
            if coordinate == self.coordinates_list[0]:
                logger.info("Completed cycle {} of {}".format(curr_cycle, self.cycles))
                curr_cycle += 1
                if curr_cycle > int(self.cycles):
                    logger.info("Completed all {} cycles".format(self.cycles))
                else:
                    logger.info("Starting cycle {} of {}".format(curr_cycle, self.cycles))
            if not matched:
                continue
            self.current_cord = coordinate

            # Monitor endpoints during the existing dwell so band-steering
            # follows the same stop and reporting behavior as other modes.
            coordinate_dwell_deadline = time.monotonic() + 10
            while time.monotonic() < coordinate_dwell_deadline:
                self.monitor_endpoint_status_changes()
                remaining = coordinate_dwell_deadline - time.monotonic()
                if remaining <= 0:
                    break
                dwell_poll_deadline = time.monotonic() + min(1, remaining)
                while time.monotonic() < dwell_poll_deadline:
                    if self.stop_signal:
                        logger.info(
                            "WebUI stop requested during endpoint "
                            "monitoring; unwinding directly to report generation."
                        )
                        raise WebUIStopRequested
                    sleep_remaining = dwell_poll_deadline - time.monotonic()
                    if sleep_remaining <= 0:
                        break
                    time.sleep(min(0.25, sleep_remaining))

        if self.stop_signal:
            if self.do_bandsteering:
                logging.info(
                    "Band-steering test stopped before all coordinates completed at %s",
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )
            else:
                logging.info(
                    "Robot YouTube test with continuous measurement stopped before all coordinates completed at %s",
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )
        else:
            if self.do_bandsteering:
                logging.info(
                    "All band-steering coordinates completed at %s; stopping the test",
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )
            else:
                logging.info(
                    "All coordinates completed for continuous measurement at %s; stopping the test",
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )
        self.stop_bandsteering_test()

    def stop_bandsteering_test(self):
        if self.do_bandsteering:
            logging.info("Stopping Band-Steering YouTube Test")
        else:
            logging.info("Stopping robot YouTube test with continuous measurement")

        # Common finalization waits for client uploads and cleans endpoints once.
        self.stop_signal = True

        if self.do_bandsteering:
            logging.info("Band-Steering Test stopped")
        else:
            logging.info("Robot YouTube test with continuous measurement stopped")

    def remove_angle_data_from_csv(self, csv_file_path):
        if self.rotations_enabled:
            if not os.path.exists(csv_file_path):
                logging.info(f"CSV not found: {csv_file_path}")
                return

            try:
                df = pd.read_csv(csv_file_path)
            except Exception as e:
                logging.info(f"Unable to read CSV {csv_file_path}: {e}")
                return

            if "Angle" not in df.columns:
                logging.info(f"No Angle column in CSV: {csv_file_path}")
                return

            df["Angle"] = pd.to_numeric(df["Angle"], errors="coerce")
            df_filtered = df[df["Angle"] != float(self.current_angle)]
            df_filtered.to_csv(csv_file_path, index=False)

            logging.info(f"Removed all rows for angle {self.current_angle} from {csv_file_path}.")

    def delete_existing_csvs_for_current_point(self):
        """
        Deletes existing CSV files for the current coordinate and angle.

        This method constructs the expected CSV file names based on the current
        coordinate and angle, checks if they exist in the appropriate directory,
        and deletes them if found. It handles both web UI and non-web UI scenarios.

        """
        for device_name, _ in self.stats_api_response.items():
            if self.do_webUI:
                csv_file_path = os.path.join(self.ui_report_dir, f"{self.current_cord}_{device_name}_youtube_stats_report.csv")
                if self.rotations_enabled:
                    self.remove_angle_data_from_csv(csv_file_path)
                else:
                    if os.path.isfile(csv_file_path):
                        os.remove(csv_file_path)
                        logging.info(f"Deleted existing CSV file: {csv_file_path}")

            else:
                current_path = os.path.dirname(os.path.abspath(__file__))
                csv_file_path = os.path.join(current_path, f"{self.current_cord}_{device_name}_youtube_stats_report.csv")
                if self.rotations_enabled:
                    self.remove_angle_data_from_csv(csv_file_path)
                else:
                    if os.path.isfile(csv_file_path):
                        os.remove(csv_file_path)
                        logging.info(f"Deleted existing CSV file: {csv_file_path}")

    def create_robo_report(self):
        if self.do_webUI:
            self.report = lf_report(_output_pdf='youtube_streaming.pdf',
                                    _output_html='youtube_streaming.html',
                                    _results_dir_name="youtube_streaming_report",
                                    _path=self.ui_report_dir)
        else:
            self.report = lf_report(_output_pdf='youtube_streaming.pdf',
                                    _output_html='youtube_streaming.html',
                                    _results_dir_name="youtube_streaming_report",
                                    _path='')
        self.report_path = self.report.path
        self.report_path_date_time = self.report.path_date_time

        self.report.set_title('Youtube Streaming Report')
        self.report.build_banner()
        self._add_youtube_report_style(self.report)

        self.report.set_obj_html(_obj_title='Objective',
                                 _obj='''The Objective is to conduct automated Youtube Video Streaming test across multiple laptops to gather statistics. The test
                            will collect these statistics. Additionally,automated graphs will be generated using the collected data.
                            ''')
        self.report.build_objective()

        if self.config:
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration if not self.is_continuous_run else "NA",
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,
                "SSID": self.ssid,
                "Security": self.security,

            }

        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            gp_pairs = zip(self.selected_groups, self.selected_profiles)
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration if not self.is_continuous_run else "NA",
                'Resolution': self.resolution,
                "Configuration": gp_map,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,

            }
        else:
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration if not self.is_continuous_run else "NA",
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})',
                "Video URL": self.url,

            }

        if self.do_webUI:
            for file_name in os.listdir(self.ui_report_dir):
                if file_name.endswith('.csv'):
                    source_file = os.path.join(self.ui_report_dir, file_name)
                    self.move_files(source_file, self.report_path_date_time)
        else:
            for file_name in os.listdir('.'):
                if file_name.endswith('.csv'):
                    self.move_files(file_name, self.report_path_date_time)

        # Connectivity precedes playback timelines in the report specification.
        self._add_connectivity_report(self.report)

        original_dir = os.getcwd()
        os.chdir(self.report_path_date_time)

        for coordinate in self.coordinates_list:
            if self.rotations_enabled:
                for angle in self.angles_list:
                    self.add_frames_graphs_to_report(coordinate, angle)
            else:
                self.add_frames_graphs_to_report(coordinate, "NA")

        for hostname in self.real_sta_hostname:
            self.add_buffer_health_graphs_to_report(hostname)
        if self.do_webUI:
            self.add_live_view_images_to_report()

        os.chdir(original_dir)

        self._build_configuration_card(self.report, test_setup_info)

        self.report.build_custom()
        self.report.build_footer()
        self.report.write_html()
        self.report.write_pdf(_page_width="420mm", _page_height="420mm")

    def add_buffer_health_graphs_to_report(self, hostname):
        all_csv_files = glob.glob("*.csv")
        filtered_csv_files = [f for f in all_csv_files if f.endswith(f"{hostname}_youtube_stats_report.csv")]

        if not filtered_csv_files:
            logging.warning(f"No CSV files found for hostname {hostname} to create buffer health graph")
            return

        frames = []

        for coord in self.coordinates_list:
            for file_name in filtered_csv_files:
                if file_name.startswith(f"{coord}_"):
                    try:
                        df = pd.read_csv(file_name)
                        df["SourceFile"] = file_name
                        frames.append(df)
                    except Exception as e:
                        logging.error(f"Error reading {file_name}: {e}")
                        continue

        combined_data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

        try:
            combined_data['TimeStamp'] = pd.to_datetime(combined_data['TimeStamp'], format="%H:%M:%S").dt.time
        except Exception as e:
            logging.error(f"Error converting timestamps for hostname {hostname} while creating buffer health graph: {e}")
            return

        combined_data = combined_data.drop_duplicates(subset='TimeStamp', keep='first')

        timestamps = combined_data['TimeStamp'].apply(lambda time_value: time_value.strftime('%H:%M:%S'))
        buffer_health = combined_data['BufferHealth']

        self._build_buffer_health_graph(
            self.report, hostname, self._elapsed_seconds(timestamps), buffer_health,
            suffix="-combined", clock_times=timestamps)

    def add_frames_graphs_to_report(self, current_cord, current_angle):
        """
            Reads all CSV files in the current directory that start with '<current_cord>_',
            filters rows up to current_angle, and collects stats:
            - Instance Name
            - Reset-aware Total Frames
            - Reset-aware Dropped Frames
            - Viewport
            - Current Resolution
            - Optimal Resolution
            - Max Buffer Health
            - Min Buffer Health
        """
        prefix = f"{current_cord}_"
        all_csv_files = glob.glob("*.csv")

        filtered_csv_files = [f for f in all_csv_files if f.startswith(prefix)]
        if not filtered_csv_files:
            logging.info(f"No CSV files found starting with '{prefix}'.")
            return {}

        result_dict = {}

        for csv_file in filtered_csv_files:
            try:
                try:
                    df = pd.read_csv(csv_file)
                except FileNotFoundError:
                    logging.info(f"CSV file not found: {csv_file}")
                    continue

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

                instance_name = df_filtered["Instance Name"].iloc[0]
                viewport = df_filtered["Viewport"].iloc[-1]
                current_res = df_filtered["CurrentRes"].iloc[-1]
                optimal_res = df_filtered["OptimalRes"].iloc[-1]
                total_frames = self.sum_reset_counter(df_filtered["TotalFrames"])
                dropped_frames = self.sum_reset_counter(df_filtered["DroppedFrames"])
                max_buffer_health = df_filtered["BufferHealth"].max()
                min_buffer_health = df_filtered["BufferHealth"].min()

                result_dict[instance_name] = {
                    "Viewport": viewport,
                    "Current Resolution": current_res,
                    "Optimal Resolution": optimal_res,
                    "Total Frames": total_frames,
                    "Dropped Frames": dropped_frames,
                    "Max Buffer Health": round(float(max_buffer_health), 2),
                    "Min Buffer Health": round(float(min_buffer_health), 2),
                }
                logging.info(f"Processed {csv_file}: {instance_name}")

            except Exception as e:
                logging.info(f"Error reading {csv_file}: {e}")

        graph_title = (
            f"Total Frames vs Dropped Frames at coordinate: {current_cord}"
            if current_angle == "NA" else
            f"Total Frames vs Dropped Frames at coordinate: {current_cord} and angle: {current_angle}°")
        if not result_dict:
            if self.rotations_enabled:
                logging.info(f"No valid data found for coordinate: {current_cord} and angle: {current_angle}. Skipping Frames graph generation.")
            else:
                logging.info(f"No valid data found for coordinate: {current_cord}. Skipping Frames graph generation.")
            return
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
                                        _graph_title=graph_title,
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
        self.report.set_graph_image(graph_image)
        self.report.build_graph()
        if self.rotations_enabled:
            self.report.set_table_title(f'Test Results for coordinate: {current_cord} and angle: {current_angle}°')
        else:
            self.report.set_table_title(f'Test Results for coordinate: {current_cord}')
        self.report.build_table_title()

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
        self.report.set_table_dataframe(test_results_df)
        self.report.build_table()

        logging.info("\nSummary for all devices:")
        for key, value in result_dict.items():
            logging.info(f"{key}: {value}")

    def add_live_view_images_to_report(self):
        """
        This function looks for live view images for each floor
        in the 'live_view_images' folder within `self.ui_report_dir`.
        It waits up to 60 seconds for each image. If an image is found,
        it's added to the report on a new page; otherwise, it's skipped.
        """
        url_image_path = os.path.join(self.ui_report_dir, "live_view_images", f"yt_{self.test_name}_1.png")
        timeout = 120  # seconds
        start_time = time.time()

        while not os.path.exists(url_image_path):
            if time.time() - start_time > timeout:
                logging.info(f"Live view Images not found in the respective folder {url_image_path} within 120 seconds. Skipping live view image addition to the report.")
                break
            time.sleep(1)
        if os.path.exists(url_image_path):
            html_content = (
                '<div style="page-break-before: always;"></div>'
                f'<img src="file://{url_image_path}" style="width:1200px; height:800px;"></img>'
            )

            self.report.set_custom_html(html_content)

    def stop_webui_test(self):
        try:
            file = f"{self.ui_report_dir}/running_status.json"
            with open(file, 'r') as file_handle:
                data = json.load(file_handle)
            data['status'] = "Completed"
            with open(file, 'w') as file_handle:
                json.dump(data, file_handle, indent=4)
            logging.info("WebUI test status updated to Completed.")
        except Exception as e:
            logging.error(f"Error in stop_webui_test function {e}", exc_info=True)


def main():
    iot_summary = None
    args = None
    youtube = None
    try:
        help_summary = '''\
        Youtube streaming automation
    '''
        parser = argparse.ArgumentParser(
            prog='lf_interop_youtube.py',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='''
            Allows user to run the youtube streaming test on a target resource for the given duration.
        ''',
            description="""
NAME: lf_interop_youtube.py

PURPOSE: lf_interop_youtube.py provides the available devices and allows the user to run YouTube on selected devices by specifying the video URL and duration.

EXAMPLE-1:
Command Line Interface to run YouTube with the specified URL and duration:
python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1 --res 1080p --upstream_port 1.1.eth1

    CASE-1:
    If the given duration is longer than the actual video duration, the video will loop.

    CASE-2:
    If the given duration is shorter than the actual video duration, the video will stop after the specified duration.

EXAMPLE-2:
Command Line Interface to run YouTube on multiple devices:
python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 2 --res 1080p --upstream_port 1.1.eth1 --resources 1.13,1.14


EXAMPLE-3:
Command Line Interface to run YouTube without post-cleanup of cross-connections:
python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 2 --res 1080p
--upstream_port 1.1.eth1 --resources 1.13,1.14 --no_post_cleanup

EXAMPLE-4:
Command Line Interface to run YouTube with multiple groups and profiles:
python3 lf_interop_youtube.py --mgr 192.168.204.74 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1
--group_name group1,group2 --profile_name netgear5g,netgear2g --file_name grplaptops.csv --upstream_port 1.1.eth1

EXAMPLE-5:
Command Line Interface to run YouTube with Device Configuration:
python3 lf_interop_youtube.py --mgr 192.168.204.74 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1
--ssid NETGEAR_2g_wpa2 --passwd Password@123 --encryp wpa2 --upstream_port 1.1.eth1 --config

Example-6:
Command Line Interface to run the new Test at each coordinate with Robo

python3 lf_interop_youtube.py \
--mgr 192.168.214.219 \
--upstream_port 1.1.eth1 \
--url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
--duration 1 \
--res 1080p \
--resources 1.13,1.14 \
--do_robo \
--robo_ip 192.168.50.10 \
--coordinates c1,c2,c3


Example-7:
Command Line Interface to run the new Test with Robo and rotating to user specified angles at each coordinate

python3 py-scripts/real_application_tests/youtube/lf_interop_youtube.py \
--mgr 192.168.214.219 \
--upstream_port 1.1.eth1 \
--url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" \
--duration 1 \
--res 1080p \
--resources 1.13,1.14 \
--do_robo \
--robo_ip 192.168.50.10 \
--coordinates c1,c2,c3 \
--rotations 0,90,180,270


SCRIPT CLASSIFICATION: Test

NOTES:
1. Use './lf_interop_youtube.py --help' to see command line usage and options.
2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
3. If --resources are not given after passing the CLI, a list of available devices (laptops) will be displayed on the terminal.
4. Enter the resource numbers separated by commas (,) in the resource argument.
5. For --url, you can specify the YouTube URL (e.g., https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1).

"""
        )

        # Define required arguments group
        required = parser.add_argument_group('Required arguments')
        # Define optional arguments group
        optional = parser.add_argument_group('Optional arguments')
        # Define webUI specific arguments group
        webUI_args = parser.add_argument_group('webUI arguments')
        # Define robo specific arguments group
        robo = parser.add_argument_group('robo arguments')

        # Add required arguments
        required.add_argument('--mgr', type=str, help="hostname where LANforge GUI is running", required=True)
        required.add_argument('--url', type=str, help='youtube url', required=True)
        required.add_argument('--duration', type=int, help='duration to run the test in sec (not needed for a continuous robot run)')
        required.add_argument('--ap_name', type=str, default="TIP", help="Name of the AP in which we run the test")
        required.add_argument('--sec', type=str, default="wpa2", help="security type used")
        required.add_argument('--band', type=str, default="5GHZ", help="Name of the Frequency band used")
        required.add_argument('--test_name', type=str, help="Test name while running through webgui")
        required.add_argument('--upstream_port', type=str, help='Specify The Upstream Port name or IP address', required=True)

        # Add optional arguments
        optional.add_argument('--resources', help='Specify the real device ports seperated by comma')
        optional.add_argument('--no_pre_cleanup', action="store_true", help='specify this flag to stop cleaning up generic cxs before the test')
        optional.add_argument('--no_post_cleanup', action="store_true", help='specify this flag to stop cleaning up generic cxs after the test')
        optional.add_argument('--debug', action="store_true", help='Enable debugging')
        optional.add_argument('--mgr_port', type=str, default=8080, help='port on which LANforge HTTP service is running')
        optional.add_argument('--windows_dir', default=WINDOWS_REAL_APP_DIR,
                              help='YouTube application directory on Windows clients')
        optional.add_argument('--linux_dir', default=LINUX_REAL_APP_DIR,
                              help='YouTube application directory on Linux clients')
        optional.add_argument('--mac_dir', default=MACOS_REAL_APP_DIR,
                              help='YouTube application directory on macOS clients')
        parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
        parser.add_argument('--res', default='Auto', help="to set resolution to  144p,240p,720p")
        parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

        # Add webUI specific arguments
        webUI_args.add_argument('--ui_report_dir', default=None, help='Specify the results directory to store the reports for webUI')
        webUI_args.add_argument('--do_webUI', action='store_true', help='specify this flag when triggering a test from webUI')

        # Arguments Related to Device Configurations
        parser.add_argument('--file_name', help="File name for DeviceConfig")
        parser.add_argument('--group_name', type=str, help='specify the group name')
        parser.add_argument('--profile_name', type=str, help='specify the profile name')
        parser.add_argument("--ssid", default=None, help='specify ssid on which the test will be running')
        parser.add_argument("--passwd", default=None, help='specify encryption password  on which the test will '
                            'be running')
        parser.add_argument("--encryp", default=None, help='specify the encryption type  on which the test will be '
                            'running eg :open|psk|psk2|sae|psk2jsae')

        parser.add_argument("--eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
        parser.add_argument("--eap_identity", type=str, default='DEFAULT', help="Specify the EAP identity for authentication.")
        parser.add_argument("--ieee8021x", action="store_true", help='Enables IEEE 802.1x support.')
        parser.add_argument("--ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
        parser.add_argument("--ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
        parser.add_argument("--enable_pkc", action="store_true", help='Enables pkc support.')
        parser.add_argument("--bss_transition", action="store_true", help='Enables BSS transition support.')
        parser.add_argument("--power_save", action="store_true", help='Enables power-saving features.')
        parser.add_argument("--disable_ofdma", action="store_true", help='Disables OFDMA support.')
        parser.add_argument("--roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
        parser.add_argument("--key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP)')
        parser.add_argument("--pairwise", type=str, default='NA', help='Specify the pairwise cipher')
        parser.add_argument("--private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
        parser.add_argument("--ca_cert", type=str, default='NA', help='Specify the CA certificate file name')
        parser.add_argument("--client_cert", type=str, default='NA', help='Specify the client certificate file name')
        parser.add_argument("--pk_passwd", type=str, default='NA', help='Specify the password for the private key')
        parser.add_argument("--pac_file", type=str, default='NA', help='Specify the pac file name')
        parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)
        parser.add_argument("--expected_passfail_value", help="Specify the expected urlcount value for pass/fail")
        parser.add_argument("--device_csv_name", type=str, help="Specify the device csv name for pass/fail", default=None)
        parser.add_argument('--config', action='store_true', help='specify this flag whether to config devices or not')
        parser.add_argument('--scoring', action='store_true', help='Generate per-device YouTube scoring CSV files')
        parser.add_argument("--wait_time", type=int, help="Specify the time for configuration", default=60)
        # IOT ARGS
        parser.add_argument('--iot_test', help="If true will execute script for iot", action='store_true')

        optional.add_argument('--iot_ip', default='127.0.0.1', help='IP of the server')

        optional.add_argument('--iot_port', default='8000', help='Port of the server')

        optional.add_argument('--iot_iterations', type=int, default=1, help='Iterations to run the test')

        optional.add_argument('--iot_delay', type=int, default=5, help='Delay in seconds between iterations (min. 5 seconds)')

        optional.add_argument('--iot_device_list', type=str, default='', help='Entity IDs of the devices to include in testing (comma separated)')

        optional.add_argument('--iot_testname', type=str, default='', help='Testname for reporting')

        optional.add_argument('--iot_increment', type=str, default='', help='Comma-separated list of device counts to incrementally test (e.g., "1,3,5")')

        robo.add_argument('--robot_wait_duration', help='Robot wait duration in seconds at obstacle', default="1")
        robo.add_argument('--robo_ip', type=str, help='Specify the robo ip')
        robo.add_argument('--coordinates', help='Comma-separated list of coordinate point names')
        robo.add_argument('--rotations', help='Comma-separated list of rotation angles (in degrees)')
        robo.add_argument('--do_robo', help='Specify this flag to perform the test with robo', action='store_true')
        robo.add_argument('--do_bandsteering', help='Specify this flag to perform Bandsteering Scenario', action='store_true')
        robo.add_argument('--bssids', type=str, help='Comma-separated list of BSSIDs for bandsteering test')
        robo.add_argument('--measurement_mode', choices=['per_point', 'continuous'], default='per_point',
                          help="Robot measurement mode: 'per_point' plays the video at each point (and angle), "
                               "'continuous' keeps the video playing while the robot moves through the points --cycles times "
                               "(--duration is not used)")
        robo.add_argument('--cycles', type=int, default=1,
                          help='Number of times the robot goes through the points in a continuous or bandsteering run')

        parser.add_argument(
            '--wifi_analysis', action='store_true',
            help='Analyze real-client Wi-Fi connection, disconnection, scan, and association '
                 'rejection events during streaming and include them in the report')
        background_ping = parser.add_argument_group('Background ping')
        background_ping.add_argument(
            '--enable_bg_ping', action='store_true',
            help='Run a ping on the real clients in the background while the test runs and report its statistics')
        background_ping.add_argument(
            '--bg_ping_target', type=str, default=None,
            help='IP, domain name or LANforge port to ping; defaults to the upstream port')
        background_ping.add_argument(
            '--bg_ping_interval', type=float, default=1,
            help='Background ping packet interval in seconds; defaults to 1')
        args = parser.parse_args()

        if args.help_summary:
            logging.info(help_summary)
            exit(0)

        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        rotations_enabled = False
        if args.do_robo:
            args.coordinates = args.coordinates.split(',') if args.coordinates else []
            args.rotations = [float(angle) for angle in args.rotations.split(',')] if args.rotations else []
            if args.rotations:
                rotations_enabled = True

        mgr_ip = args.mgr
        mgr_port = args.mgr_port
        url = args.url
        # continuous robot run (band steering or measurement mode 'continuous'): the video plays until the robot finishes its laps
        is_continuous_run = args.do_bandsteering or (args.do_robo and args.measurement_mode == "continuous")
        if args.duration is None and not is_continuous_run:
            parser.error("--duration is required unless the robot runs continuously")
        duration = args.duration
        bssids = None
        if is_continuous_run:
            args.duration = 999999
        if args.do_bandsteering:
            bssids = args.bssids.split(',') if args.bssids else []

        do_webUI = args.do_webUI
        ui_report_dir = args.ui_report_dir
        debug = args.debug

        # Print debug information if debugging is enabled
        if debug:
            logging.info('''Specified configuration:
            ip:                       {}
            port:                     {}
            Duration:                 {}
            debug:                    {}
            '''.format(mgr_ip, mgr_port, duration, debug))

        if True:

            if args.expected_passfail_value is not None and args.device_csv_name is not None:
                logging.error("Specify either expected_passfail_value or device_csv_name")
                exit(1)

            if args.group_name is not None:
                args.group_name = args.group_name.strip()
                selected_groups = args.group_name.split(',')
            else:
                selected_groups = []

            if args.profile_name is not None:
                args.profile_name = args.profile_name.strip()
                selected_profiles = args.profile_name.split(',')
            else:
                selected_profiles = []

            if len(selected_groups) != len(selected_profiles):
                logging.error("Number of groups should match number of profiles")
                exit(0)

            elif args.group_name is not None and args.profile_name is not None and args.file_name is not None and args.resources is not None:
                logging.error("Either group name or device list should be entered not both")
                exit(0)
            elif args.ssid is not None and args.profile_name is not None:
                logging.error("Either ssid or profile name should be given")
                exit(0)
            elif args.file_name is not None and (args.group_name is None or args.profile_name is None):
                logging.error("Please enter the correct set of arguments")
                exit(0)
            elif args.config and ((args.ssid is None or (args.passwd is None and args.security.lower() != 'open') or (args.passwd is None and args.security is None))):
                logging.error("Please provide ssid password and security for configuration of devices")
                exit(0)

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

            # Create a YouTube object with the specified parameters

            youtube = Youtube(
                host=mgr_ip,
                port=mgr_port,
                url=url,
                duration=args.duration,
                lanforge_password='lanforge',
                sta_list=[],
                do_webUI=args.do_webUI,
                ui_report_dir=ui_report_dir,
                debug=debug,
                resolution=args.res,
                ap_name=args.ap_name,
                ssid=args.ssid,
                security=args.encryp,
                band=args.band,
                test_name=args.test_name,
                upstream_port=args.upstream_port,
                config=args.config,
                selected_groups=selected_groups,
                selected_profiles=selected_profiles,
                robo_ip=args.robo_ip,
                coordinates_list=args.coordinates,
                angles_list=args.rotations,
                do_robo=args.do_robo,
                cycles=args.cycles,
                do_bandsteering=args.do_bandsteering,
                measurement_mode=args.measurement_mode,
                bssids=bssids,
                rotations_enabled=rotations_enabled,
                scoring=args.scoring,
                windows_dir=args.windows_dir,
                linux_dir=args.linux_dir,
                mac_dir=args.mac_dir)
            youtube.handle_flask_server()
            args.upstream_port = youtube.change_port_to_ip(args.upstream_port)

            resources = []
            youtube.Devices = Devices
            if args.file_name:
                new_filename = args.file_name.removesuffix(".csv")
            else:
                new_filename = args.file_name
            config_obj = DeviceConfig.DeviceConfig(lanforge_ip=args.mgr, file_name=new_filename, wait_time=args.wait_time)
            youtube.configobj = config_obj
            if not args.expected_passfail_value and args.device_csv_name is None:
                config_obj.device_csv_file(csv_name="device.csv")
            if args.group_name is not None and args.file_name is not None and args.profile_name is not None:
                selected_groups = args.group_name.split(',')
                selected_profiles = args.profile_name.split(',')
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
                args.resources = ",".join(id for id in eid_list)
            else:
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
                    'server_ip': args.upstream_port,
                }
                if args.resources:
                    all_devices = config_obj.get_all_devices()
                    if args.group_name is None and args.file_name is None and args.profile_name is None:
                        dev_list = args.resources.split(',')
                        if args.config:
                            asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                else:
                    all_devices = config_obj.get_all_devices()
                    device_list = []
                    for device in all_devices:
                        if device["type"] != 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                        elif device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])

                    print("Available devices:")
                    for device in device_list:
                        print(device)

                    args.resources = input("Enter the desired resources to run the test:")
                    dev1_list = args.resources.split(',')
                    if args.config:
                        asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

            if not do_webUI:
                if args.resources:
                    resources = [r.strip() for r in args.resources.split(',')]
                    resources = [r for r in resources if len(r.split('.')) > 1]

                    youtube.select_real_devices(real_devices=Devices, real_sta_list=resources, base_interop_obj=Devices)

                else:
                    youtube.select_real_devices(real_devices=Devices)
            else:
                resources = [r.strip() for r in args.resources.split(',')]

                extracted_parts = [res.split('.')[:2] for res in resources]
                formatted_parts = ['.'.join(parts) for parts in extracted_parts]
                youtube.select_real_devices(real_devices=Devices, real_sta_list=formatted_parts, base_interop_obj=Devices)

            if args.iot_test:
                start_iot_thread(args)

            # Perform pre-test cleanup if not skipped
            if not args.no_pre_cleanup:
                youtube.cleanup()

            # Check if the required tab exists, and exit if not
            if not youtube.check_tab_exists():
                logging.error('Generic Tab is not available.\nAborting the test.')
                exit(0)

            if len(youtube.real_sta_list) > 0:
                logging.info(
                    "Creating YouTube endpoints for selected interfaces: %s",
                    ", ".join(youtube.real_sta_list),
                )
                youtube.create_generic_endp()
            else:
                logging.error("No usable real devices are available")
                exit(0)

            if args.do_webUI:
                youtube.update_webui()

            if is_continuous_run:
                logging.info("YouTube streaming will run until all robot cycles finish")
            else:
                logging.info(
                    "YouTube streaming is configured to run for %d minute(s)",
                    duration,
                )

            logging.info("Waiting 10 seconds before starting YouTube streaming")
            youtube.wait_stop_aware(10, "before YouTube streaming started")

            # Start only the optional monitoring requested for this test.
            youtube.start_connectivity_monitoring(args)

            youtube.start_time = datetime.now()
            if args.do_robo:
                if is_continuous_run:
                    youtube.perform_robo_bandsteering_test()
                else:
                    youtube.perform_robo_test()
            else:
                youtube.start_generic()

                duration = args.duration
                end_time = datetime.now() + timedelta(minutes=duration)

                while (datetime.now() < end_time or not youtube.check_gen_cx()) and not youtube.stop_signal:
                    youtube.monitor_endpoint_status_changes()
                    time.sleep(1)

                if not youtube.stop_signal:
                    youtube.generic_endps_profile.stop_cx()
                logging.info(
                    "YouTube streaming finished at %s",
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                )

            if args.iot_test and args.iot_testname:
                base = os.path.join("results", args.iot_testname)
                p = os.path.join(base, "iot_summary.json")
                if os.path.exists(p):
                    with open(p) as f:
                        iot_summary = json.load(f)

            logging.info("Stopping the YouTube test")
    except WebUIStopRequested:
        logging.info(
            "WebUI stop acknowledged during endpoint retry; entering report generation."
        )
    except AllEndpointsUnreachable as exc:
        logging.error("%s; entering report generation.", exc)
    except Exception as e:
        logging.error(f"Error occured {e}")
        tb_str = traceback.format_exc()  # capture traceback as string
        logger.error("An exception occurred:\n%s", tb_str)
    finally:
        if (
            args is not None
            and youtube is not None
            and not ('--help' in sys.argv or '-h' in sys.argv)
        ):
            youtube.finalize_test_run(args, iot_summary=iot_summary)
            logging.info(
                "YouTube test and report generation completed at %s",
                datetime.now().astimezone().isoformat(timespec="seconds"),
            )


if __name__ == "__main__":
    main()
