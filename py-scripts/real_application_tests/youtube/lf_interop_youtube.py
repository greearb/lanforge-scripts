#!/usr/bin/env python3
"""
    NAME: lf_interop_youtube.py

    PURPOSE: lf_interop_youtube.py provides the available devices and allows the user to run YouTube on selected devices by specifying the video URL and duration.

    EXAMPLE-1:
    Command Line Interface to run YouTube with the specified URL and duration:
    python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 1 --res 1080p --flask_ip 192.168.214.131

        CASE-1:
        If the given duration is longer than the actual video duration, the video will loop.

        CASE-2:
        If the given duration is shorter than the actual video duration, the video will stop after the specified duration.

    EXAMPLE-2:
    Command Line Interface to run YouTube on multiple devices:
    python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 2 --res 1080p --flask_ip 192.168.214.131 --resources 1.13,1.14...


    EXAMPLE-4:
    Command Line Interface to run YouTube without post-cleanup of cross-connections:
    python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1" --duration 2 --res 1080p
    --flask_ip 192.168.214.131 --resources 1.13,1.14... --no_post_cleanup
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
import matplotlib.pyplot as plt
import csv
import asyncio
import json
import shutil
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from threading import Thread
import traceback
import threading

logger = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


# Import LANforge-related modules

# Set up logging
logger = logging.getLogger(__name__)

# Import LF logger configuration module
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

# Import realm module
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

# Import base interop profile module
base = importlib.import_module('py-scripts.lf_base_interop_profile')
base_RealDevice = base.RealDevice

DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")

# Importing modules dynamically
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_base_interop_profile = importlib.import_module("py-scripts.lf_base_interop_profile")

# Accessing specific classes
lf_report = lf_report.lf_report
lf_bar_graph_horizontal = lf_graph.lf_bar_graph_horizontal
RealDevice = lf_base_interop_profile.RealDevice


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
                 stats_api_response={},
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
                 selected_profiles=None


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
        self.sta_list = sta_list
        self.real_sta_list = []
        self.real_sta_data_dict = {}
        self.linux = 0
        self.windows = 0
        self.mac = 0
        self.result_json = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'youtube'
        self.generic_endps_profile.name_prefix = "yt"
        self.Devices = None
        self.start_time = ""
        self.stop_time = ""
        self.do_webUI = do_webUI
        self.ui_report_dir = ui_report_dir
        self.devices = base_RealDevice(manager_ip=self.host, selected_bands=[])
        self.device_names = []
        self.resolution = resolution
        self.ap_name = ap_name
        self.ssid = ssid
        self.security = security
        self.band = band
        self.start_time = None,
        self.est_end_time = None,
        self.end_time_webgui = []
        self.all_stop = False
        self.keys = []
        self.hostname_os_combination = None
        if self.do_webUI:
            self.base_dir = os.path.abspath(os.path.join(ui_report_dir, "../../"))
            self.test_name = test_name

        self.mydatajson = {}
        self.final_data = None
        self.stats_api_response = {}
        self.upstream_port = upstream_port
        self.stop_signal = False
        self.config = config
        self.selected_groups = selected_groups
        self.selected_profiles = selected_profiles

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

    def execute_youtube_test(self, duration, do_webUI):
        """
        Execute the YouTube test for monitoring

        Args:
            duration (int): Duration of the test in minutes.
            do_webUI (bool): Flag to determine if the test is triggered from the web UI.
        """
        # Wait for 10 seconds before starting the test
        self.clear_previous_data()

        self.start_generic()
        time.sleep(5)

        # Initialize variables
        self.start_time = datetime.now()
        self.est_end_time = self.start_time + timedelta(minutes=duration, seconds=60)
        self.end_time_webgui = [False] * len(self.device_names)
        self.keys = self.generic_endps_profile.created_cx
        self.all_stop = False

        # Ensure initial data is fetched
        initial_data = self.get_data_from_api()
        while not initial_data:
            initial_data = self.get_data_from_api()
            time.sleep(1)

        # Monitoring loop
        while not self.all_stop:
            if do_webUI:
                stop_value = self.set_webUI_stop()
                if stop_value == "Completed":
                    break

            self._monitor_test(do_webUI)

            time.sleep(1)  # Adjust sleep time as needed

        logging.info("Duration ended. Stopping the test.")

    def _monitor_test(self, do_webUI):
        """
        Monitor the YouTube test execution and handle stop conditions.

        Args:
            do_webUI (bool): Flag to determine if the test is triggered from the web UI.
        """
        initial_data = self.get_data_from_api()
        if initial_data:
            for i in range(len(self.device_names)):
                stop_state = initial_data['result'].get(self.device_names[i], {}).get('stop', False)
                if stop_state:
                    self.end_time_webgui[i] = True
                if all(self.end_time_webgui) or datetime.now() >= self.est_end_time:
                    self.all_stop = True
                    return

            for i in range(len(self.device_names)):
                if not self.end_time_webgui[i]:
                    new_key = self.keys[i]
                    if new_key.startswith("CX_"):
                        new_key = self.keys[i][3:]
                    response = self.json_get(f'/generic/{new_key}')
                    if response['endpoint']['status'] in ['WAITING', 'Stopped']:
                        self.end_time_webgui[i] = True

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

    def create_generic_endp(self, query_resources):
        """
        Creates generic endpoints for the specified resources.
        Args:
        - query_resources (list): List of resources to create endpoints for.
        Steps:
        1. Retrieves information about all resources using a JSON GET request.
        2. Matches user-specified resources with available resources and retrieves necessary details (eid, ctrl-ip, hostname).
        3. Retrieves port information using a JSON GET request.
        4. Matches ports associated with retrieved resources and constructs a list of matching ports.
        5. Creates generic endpoints using the retrieved ports and other parameters.
        """
        ports_list = []
        eid = ""
        resource_ip = ""
        user_resources = ['.'.join(item.split('.')[:2]) for item in self.real_sta_list]

        # Step 1: Retrieve information about all resources
        response = self.json_get("/resource/all")

        # Step 2: Match user-specified resources with available resources sequentially
        if user_resources:
            # Iterate through user_resources sequentially, processing each value only once
            for user_resource in user_resources:
                # Break loop if no more user_resources left to process
                if not user_resources:
                    break

                for key, value in response.items():
                    if key == "resources":
                        for element in value:
                            for resource_key, resource_values in element.items():
                                # Match the current user_resource
                                if resource_key == user_resource:
                                    eid = resource_values["eid"]
                                    resource_ip = resource_values['ctrl-ip']
                                    self.device_names.append(resource_values['hostname'])
                                    ports_list.append({'eid': eid, 'ctrl-ip': resource_ip})
                                    break
                            else:
                                # Continue outer loop only if no break occurred
                                continue
                            # Break if a match was found and processed
                            break
        gen_ports_list = []
        self.mac_list = []
        self.rssi_list = []
        self.link_rate_list = []
        self.ssid_list = []
        # Step 3: Retrieve port information
        response_port = self.json_get("/port/all")

        # Step 4: Match ports associated with retrieved resources in the order of ports_list
        for port_entry in ports_list:
            # Extract the eid and ctrl-ip from the current ports_list entry
            expected_eid = port_entry['eid']

            # Iterate over the port interfaces to find a matching port
            for interface in response_port['interfaces']:
                for port, port_data in interface.items():
                    # Extract the first two segments of the port identifier to match with expected_eid
                    result = '.'.join(port.split('.')[:2])

                    # Check if the result matches the current expected eid from ports_list
                    if result == expected_eid:
                        gen_ports_list.append(port.split('.')[-1])
                        break
                else:
                    continue
                break

        for port_entry in ports_list:
            # Extract the eid and ctrl-ip from the current ports_list entry
            expected_eid = port_entry['eid']

            # Iterate over the port interfaces to find a matching port
            for interface in response_port['interfaces']:
                for port, port_data in interface.items():
                    # Extract the first two segments of the port identifier to match with expected_eid
                    result = '.'.join(port.split('.')[:2])

                    # Check if the result matches the current expected eid from ports_list
                    if result == expected_eid and port_data["parent dev"] == 'wiphy0':
                        self.mac_list.append(port_data["mac"])
                        self.rssi_list.append(port_data["signal"])
                        self.link_rate_list.append(port_data["rx-rate"])
                        self.ssid_list.append(port_data["ssid"])

                        break
                else:
                    continue
                break

        self.new_port_list = [item.split('.')[2] for item in self.real_sta_list]

        if self.generic_endps_profile.create(ports=self.real_sta_list, sleep_time=.5, real_client_os_types=self.real_sta_os_types,):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        for i in range(0, len(self.real_sta_os_types)):
            if self.real_sta_os_types[i] == 'windows':
                cmd = "youtube_stream.bat --url %s --host %s --device_name %s --duration %s --res %s" % (self.url, self.upstream_port, self.real_sta_hostname[i], self.duration, self.resolution)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_types[i] == 'linux':
                cmd = "su -l lanforge  ctyt.bash %s %s %s %s %s %s" % (self.new_port_list[i], self.url, self.upstream_port, self.real_sta_hostname[i], self.duration, self.resolution)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

            elif self.real_sta_os_types[i] == 'macos':
                cmd = "sudo bash ctyt.bash --url %s --host %s --device_name %s --duration %s --res %s" % (self.url, self.upstream_port, self.real_sta_hostname[i], self.duration, self.resolution)
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

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
        8. Tracks the number of selected devices (`android`, `windows`, `mac`, `linux`).


        """
        # Query and retrieve all user-defined real stations if `real_sta_list` is not provided
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_devices.query_user()
        else:
            interface_data = self.json_get("/port/all")
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

        # Retrieve OS types and hostnames
        self.real_sta_os_types = [self.real_sta_data_dict[real_sta_name]['ostype'] for real_sta_name in self.real_sta_data_dict]
        self.real_sta_hostname = [self.real_sta_data_dict[real_sta_name]['hostname'] for real_sta_name in self.real_sta_data_dict]

        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_types)
        ]

        for i in range(0, len(self.real_sta_os_types)):

            if self.real_sta_os_types[i] == 'windows':
                self.windows = self.windows + 1
            elif self.real_sta_os_types[i] == 'linux':
                self.linux = self.linux + 1
            elif self.real_sta_os_types[i] == 'macos':
                self.mac = self.mac + 1

        return self.real_sta_list

    def start_generic(self):
        """
        Starts the generic endpoints' connections and sets the start time.

        Steps:
        1. Starts the connections of generic endpoints using `self.generic_endps_profile.start_cx()`.
        2. Sets the start time (`self.start_time`) to the current datetime.

        """
        # Start the connections of generic endpoints
        self.generic_endps_profile.start_cx()
        # Set the start time to the current datetime
        self.start_time = datetime.now()

    def stop_generic_cx(self,):
        self.generic_endps_profile.stop_cx()
        self.stop_time = datetime.now()


    def get_data_from_api(self):
        """
        Retrieves YouTube streaming statistics from an API endpoint.
        Returns:
            dict or None: The fetched data if successful, None otherwise.
        """
        self.devices_list = []
        url = "http://localhost:5002/youtube_stats"
        response = requests.get(url)
        if response.status_code == 200:
            self.data = response.json()
            result_data = self.data.get("result", {})
            for device_name, device_data in result_data.items():
                stats = {key: value for key, value in device_data.items() if key != "stop"}
                timestamp = stats.get("Timestamp", {})
                if device_name not in self.mydatajson:
                    self.mydatajson[device_name] = {}
                if "maxbufferhealth" not in self.mydatajson[device_name]:
                    self.mydatajson[device_name]["maxbufferhealth"] = "0.0"
                else:
                    if float(stats.get("BufferHealth", "0.0")) > float(self.mydatajson[device_name]["maxbufferhealth"]):
                        self.mydatajson[device_name]["maxbufferhealth"] = stats.get("BufferHealth", "0.0")

                if "minbufferhealth" not in self.mydatajson[device_name]:
                    self.mydatajson[device_name]["minbufferhealth"] = "100000.0"
                else:
                    if float(stats.get("BufferHealth", "100000.0")) < float(self.mydatajson[device_name]["minbufferhealth"]):
                        self.mydatajson[device_name]["minbufferhealth"] = stats.get("BufferHealth", "0.0")

                # Define CSV file path using the device name as the file name
                if self.do_webUI:
                    csv_file_path = os.path.join(self.ui_report_dir, f'{device_name}_youtube_stats_report.csv')
                else:
                    current_path = os.path.dirname(os.path.abspath(__file__))
                    csv_file_path = os.path.join(current_path, f"{device_name}_youtube_stats_report.csv")

                self.devices_list.append(csv_file_path)

                file_exists = os.path.isfile(csv_file_path)
                headers = ["Instance Name", "TimeStamp", "Viewport", "DroppedFrames", "TotalFrames", "CurrentRes", "OptimalRes", "BufferHealth"]

                with open(csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(headers)
                    row = [device_name, timestamp]
                    for header in headers[2:]:
                        row.append(stats.get(header, "NA"))
                    writer.writerow(row)

            return self.data
        else:
            logging.error(f"Failed to fetch data from API. Status code: {response.status_code}")
            return None

    def start_flask_server(self):
        """
        Starts a Flask server with API endpoints for YouTube statistics.
        """
        app = Flask(__name__)

        @app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        @app.route('/stop_yt', methods=['GET'])
        def stop_yt():
            """
            Endpoint to stop the YouTube test and trigger a graceful application shutdown.
            """
            logging.info("Stopping the test through web UI")

            response = jsonify({"message": "Stopping Youtube Test"})
            response.status_code = 200

            # Start shutdown in a separate thread
            shutdown_thread = threading.Thread(target=self.shutdown)
            shutdown_thread.start()

            return response

        @app.route('/youtube_stats', methods=['GET', 'POST'])
        def youtube_stats():
            """
            API endpoint to get or post YouTube statistics.
            - GET: Returns the current YouTube stats.
            - POST: Updates the stats or clears them based on the provided data.
            """
            if request.method == 'POST':
                data = request.json

                # Clear data if requested
                if data.get("clear_data"):
                    self.stats_api_response = {}
                    return jsonify({"message": "Data cleared"}), 200

                for key, value in data.items():
                    if key == "stop":
                        continue
                    device_name = key
                    stats = value
                    stop = data.get("stop", False)

                    if device_name not in self.stats_api_response:
                        self.stats_api_response[device_name] = {}
                    self.stats_api_response[device_name] = {
                        **stats,
                        "stop": stop
                    }

                return jsonify({"message": "Stats updated"}), 200

            elif request.method == 'GET':
                return jsonify({"result": self.stats_api_response}), 200

            return jsonify({"error": "Invalid request"}), 400

        @app.route('/read_youtube_data_from_csv', methods=['GET'])
        def read_youtube_data_from_csv():
            """
            API endpoint to read YouTube data from CSV files and return the last row for each device.
            """
            device_data = {}
            for csv_file_path in self.devices_list:
                if not os.path.isfile(csv_file_path):
                    continue
                df = pd.read_csv(csv_file_path)
                if not df.empty:
                    last_row = df.iloc[-1].to_dict()
                    device_name = os.path.basename(csv_file_path).split('_youtube_stats_report')[0]
                    device_data[device_name] = last_row
            return jsonify({"result": device_data}), 200

        def run_flask():
            app.run(host="0.0.0.0", port=5002, debug=False, use_reloader=False)

        # Run the Flask server in a separate thread to avoid blocking
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

    def stop_test_yt(self,):
        try:
            url = f"http://{self.host}:5454/update_status_yt"
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'status': 'Completed',
                'name': self.test_name,
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                logging.info("Successfully updated STOP status to 'Completed'")
                pass
            else:
                logging.error(f"Failed to update STOP status: {response.status_code} - {response.text}")

        except Exception as e:
            logging.error(f"An error occurred while updating status: {e}")


    def move_files(self, source_file, dest_dir):
        # Ensure the source file exists
        if not os.path.isfile(source_file):
            logging.ERROR(f"Source file '{source_file}' does not exist or is not a regular file.")
            return

        # Ensure the destination directory exists
        if not os.path.exists(dest_dir):
            logging.ERROR(f"Destination directory '{dest_dir}' does not exist.")
            return

        try:
            filename = os.path.basename(source_file)
            dest_file = os.path.join(dest_dir, filename)
            shutil.move(source_file, dest_file)

            logging.info(f"Successfully moved '{source_file}' to '{dest_file}'.")

        except Exception as e:
            logging.ERROR(f"Failed to move '{source_file}' to '{dest_dir}': {e}")

    def shutdown(self):
        """
        Gracefully shut down the application.
        """
        logging.info("Initiating graceful shutdown...")
        self.stop_signal = True
        time.sleep(10)
        self.generic_endps_profile.cleanup()
        logging.info("Application Closed sucessfully")
        os._exit(0)

    def updating_webui_runningjson(self, obj):
        data = {}
        file_path = self.ui_report_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name)

        # Wait until the file exists
        while not os.path.exists(file_path):
            logging.info("Waiting for Running json filed to be created")
            time.sleep(1)
        logging.info("Running Json file created")
        with open(file_path, 'r') as file:
            data = json.load(file)

        for key in obj:
            data[key] = obj[key]

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def create_report(self, data, ui_report_dir):

        result_data = data
        for device, stats in result_data.items():
            self.mydatajson.setdefault(device, {}).update({
                "Viewport": stats.get("Viewport", ""),
                "DroppedFrames": stats.get("DroppedFrames", "0"),
                "TotalFrames": stats.get("TotalFrames", "0"),
                "CurrentRes": stats.get("CurrentRes", ""),
                "OptimalRes": stats.get("OptimalRes", ""),
                "BufferHealth": stats.get("BufferHealth", "0.0"),
                "Timestamp": stats.get("Timestamp", ""),
            })

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
        self.report_path = self.report.get_path()
        self.report_path_date_time = self.report.get_path_date_time()

        # setting report title
        self.report.set_title('Youtube Streaming Report')
        self.report.build_banner()

        # objective and description
        self.report.set_obj_html(_obj_title='Objective',
                                 _obj='''The Objective is to conduct automated Youtube Video Streaming test across multiple laptops to gather statistics. The test
                            will collect these statistics. Additionally,automated graphs will be generated using the collected data.
                            ''')
        self.report.build_objective()

        if self.config:

            # Test setup info
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration,
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac})',
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
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac})',
                "Video URL": self.url,

            }
        else:
            # Test setup info
            test_setup_info = {
                'Test Name': 'YouTube Streaming Test',
                'Duration (in Minutes)': self.duration,
                'Resolution': self.resolution,
                'Configured Devices': self.hostname_os_combination,
                'No of Devices :': f' Total({len(self.real_sta_os_types)}) : W({self.windows}),L({self.linux}),M({self.mac})',
                "Video URL": self.url,

            }

        self.report.test_setup_table(
            test_setup_data=test_setup_info, value='Test Parameters')

        viewport_list = []
        current_res_list = []
        optimal_res_list = []

        dropped_frames_list = []
        total_frames_list = []
        max_buffer_health_list = []
        min_buffer_health_list = []

        for hostname in self.real_sta_hostname:
            if hostname in self.mydatajson:
                stats = self.mydatajson[hostname]
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
        self.report.set_graph_title("Total Frames vs Frames dropped")
        self.report.build_graph_title()
        x_fig_size = 25
        y_fig_size = len(self.device_names) * .5 + 4

        graph = lf_bar_graph_horizontal(_data_set=[dropped_frames_list, total_frames_list],
                                        _xaxis_name="No of Frames",
                                        _yaxis_name="Devices",
                                        _yaxis_categories=self.real_sta_hostname,
                                        _graph_image_name="Dropped Frames vs Total Frames",
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
        self.report.move_graph_image()
        self.report.build_graph()

        self.report.set_table_title('Test Results')
        self.report.build_table_title()

        test_results = {
            "Hostname": self.real_sta_hostname,
            "OS Type": self.real_sta_os_types,
            "MAC": self.mac_list,
            "RSSI": self.rssi_list,
            "Link Rate": self.link_rate_list,
            "ViewPort": viewport_list,
            "SSID": self.ssid_list,
            "Video Resoultion": current_res_list,
            "Max Buffer Health (Seconds)": max_buffer_health_list,
            "Min Buffer health (Seconds)": min_buffer_health_list,
            "Total Frames": total_frames_list,
            "Dropped Frames": dropped_frames_list,


        }

        test_results_df = pd.DataFrame(test_results)
        self.report.set_table_dataframe(test_results_df)
        self.report.build_table()

        for file_path in self.devices_list:
            self.move_files(file_path, self.report_path_date_time)

        original_dir = os.getcwd()

        if self.do_webUI:
            csv_files = [f for f in os.listdir(self.report_path_date_time) if f.endswith('.csv')]
            os.chdir(self.report_path_date_time)
        else:
            csv_files = [f for f in os.listdir(self.report_path_date_time) if f.endswith('.csv')]
            os.chdir(self.report_path_date_time)

        for file_name in csv_files:
            data = pd.read_csv(file_name)

            self.report.set_graph_title('Buffer Health vs Time Graph for {}'.format(file_name.split('_')[0]))
            self.report.build_graph_title()

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

            output_file = '{}'.format(file_name.split('_')[0]) + 'buffer_health_vs_time.png'
            plt.tight_layout()
            plt.savefig(output_file, dpi=96)
            plt.close()

            logging.info(f"Graph saved for {file_name}: {output_file}")

            self.report.set_graph_image(output_file)

            self.report.build_graph()

        os.chdir(original_dir)

        # Closing
        self.report.build_custom()
        self.report.build_footer()
        self.report.write_html()
        self.report.write_pdf()

    def check_gen_cx(self):
        try:

            for gen_endp in self.generic_endps_profile.created_endp:
                generic_endpoint = self.json_get(f'/generic/{gen_endp}')

                if not generic_endpoint or "endpoint" not in generic_endpoint:
                    logging.error(f"Error fetching endpoint data for {gen_endp}")
                    return False

                endp_status = generic_endpoint["endpoint"].get("status", "")

                if endp_status not in ["Stopped", "WAITING", "NO-CX"]:
                    return False

            return True
        except Exception as e:
            logging.error(f"Error in check_gen_cx funtion {e}", exc_info=True)
            logging.info(f"Generic endpoint data {generic_endpoint}")
    
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
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except BaseException:
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


def main():
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
            description=''
            'youtube streaming automation '''
        )

        # Define required arguments group
        required = parser.add_argument_group('Required arguments')
        # Define optional arguments group
        optional = parser.add_argument_group('Optional arguments')
        # Define webUI specific arguments group
        webUI_args = parser.add_argument_group('webUI arguments')

        # Add required arguments
        required.add_argument('--mgr', type=str, help="hostname where LANforge GUI is running", required=True)
        required.add_argument('--url', type=str, help='youtube url', required=True)
        required.add_argument('--duration', type=int, help='duration to run the test in sec', required=True)
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

        parser.add_argument("--eap_method", type=str, default='DEFAULT')
        parser.add_argument("--eap_identity", type=str, default='')
        parser.add_argument("--ieee80211", action="store_true")
        parser.add_argument("--ieee80211u", action="store_true")
        parser.add_argument("--ieee80211w", type=int, default=1)
        parser.add_argument("--enable_pkc", action="store_true")
        parser.add_argument("--bss_transition", action="store_true")
        parser.add_argument("--power_save", action="store_true")
        parser.add_argument("--disable_ofdma", action="store_true")
        parser.add_argument("--roam_ft_ds", action="store_true")
        parser.add_argument("--key_management", type=str, default='DEFAULT')
        parser.add_argument("--pairwise", type=str, default='[BLANK]')
        parser.add_argument("--private_key", type=str, default='[BLANK]')
        parser.add_argument("--ca_cert", type=str, default='[BLANK]')
        parser.add_argument("--client_cert", type=str, default='[BLANK]')
        parser.add_argument("--pk_passwd", type=str, default='[BLANK]')
        parser.add_argument("--pac_file", type=str, default='[BLANK]')
        parser.add_argument("--server_ip", type=str, default=None)
        parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)
        parser.add_argument("--expected_passfail_value", help="Specify the expected urlcount value for pass/fail")
        parser.add_argument("--device_csv_name", type=str, help="Specify the device csv name for pass/fail", default=None)
        parser.add_argument('--config', action='store_true', help='specify this flag whether to config devices or not')

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

        mgr_ip = args.mgr
        mgr_port = args.mgr_port
        url = args.url
        duration = args.duration

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
                selected_profiles=selected_profiles)
            youtube.start_flask_server()
            args.upstream_port = youtube.change_port_to_ip(args.upstream_port)

            resources = []
            youtube.Devices = Devices
            if args.file_name:
                new_filename = args.file_name[:-4]
            else:
                new_filename = None
            config_obj = DeviceConfig.DeviceConfig(lanforge_ip=args.mgr, file_name=new_filename)
            if not args.expected_passfail_value and args.device_csv_name is None:
                config_obj.device_csv_file(csv_name="device.csv")
            if args.group_name is not None and args.file_name is not None and args.profile_name is not None:
                selected_groups = args.group_name.split(',')
                selected_profiles = args.profile_name.split(',')
                config_devices = {}
                for i in range(len(selected_groups)):
                    config_devices[selected_groups[i]] = selected_profiles[i]

                config_obj.initiate_group()

                asyncio.run(config_obj.connectivity(config_devices, upstream_port=args.upstream_port))

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

                if args.do_webUI:

                    if len(youtube.real_sta_hostname) == 0:
                        logging.error("No device is available to run the test")
                        obj = {
                            "status": "Stopped",
                            "configuration_status": "configured"
                        }
                        youtube.updating_webui_runningjson(obj)
                        return
                    else:
                        obj = {
                            "configured_devices": youtube.real_sta_hostname,
                            "configuration_status": "configured",
                            "no_of_devices": f' Total({len(youtube.real_sta_os_types)}) : W({youtube.windows}),L({youtube.linux}),M({youtube.mac})',
                            "device_list": youtube.hostname_os_combination

                        }
                        youtube.updating_webui_runningjson(obj)

            # Perform pre-test cleanup if not skipped
            if not args.no_pre_cleanup:
                youtube.cleanup()

            # Check if the required tab exists, and exit if not
            if not youtube.check_tab_exists():
                logging.error('Generic Tab is not available.\nAborting the test.')
                exit(0)

            if len(youtube.real_sta_list) > 0:
                logging.info(f"checking real sta list while creating endpionts {youtube.real_sta_list}")
                youtube.create_generic_endp(youtube.real_sta_list)
            else:
                logging.info(f"checking real sta list while creating endpionts {youtube.real_sta_list}")
                logging.error("No Real Devies Available")
                exit(0)

            logging.info("TEST STARTED")
            logging.info('Running the Youtube Streaming test for {} minutes'.format(duration))

            time.sleep(10)

            youtube.start_time = datetime.now()
            youtube.start_generic()

            duration = args.duration
            end_time = datetime.now() + timedelta(minutes=duration)
            initial_data = youtube.get_data_from_api()

            while len(initial_data) == 0:
                initial_data = youtube.get_data_from_api()
                time.sleep(1)
            if initial_data:
                end_time_webgui = []
                for i in range(len(youtube.device_names)):
                    end_time_webgui.append(initial_data['result'].get(youtube.device_names[i], {}).get('stop', False))
            else:
                for i in range(len(youtube.device_names)):
                    end_time_webgui.append("")

            end_time = datetime.now() + timedelta(minutes=duration)

            while datetime.now() < end_time or not youtube.check_gen_cx():
                youtube.get_data_from_api()
                time.sleep(1)

            youtube.generic_endps_profile.stop_cx()
            logging.info("Duration ended")

            logging.info('Stopping the test')
            if do_webUI:
                youtube.create_report(youtube.stats_api_response, youtube.ui_report_dir)
            else:

                youtube.create_report(youtube.stats_api_response, '')

            # Perform post-test cleanup if not skipped
            if not args.no_post_cleanup:
                youtube.generic_endps_profile.cleanup()
    except Exception as e:
        logging.error(f"Error occured {e}")
        traceback.print_exc()
    finally:
        youtube.stop()
        # Stopping the Youtube test
        if do_webUI:
            youtube.stop_test_yt()
        logging.info("Waiting for Cleanup of Browsers in Devices")
        time.sleep(10)


if __name__ == "__main__":
    main()
