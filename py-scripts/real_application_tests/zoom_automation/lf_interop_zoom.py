"""
    NAME: lf_interop_zoom.py

    PURPOSE: lf_interop_zoom.py provides the available devices and allows the user to start Zoom call conference meeting for the user-specified duration

    EXAMPLE-1:
    Command Line Interface to run Zoom with specified duration:
    python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video --server_ip 192.168.214.123



    EXAMPLE-2:
    Command Line Interface to run Zoom on multiple devices:
    python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video
      --resources 1.400,1.375 --zoom_host 1.95 --server_ip 192.168.214.123



    NOTES:
    1. Use './lf_interop_zoom.py --help' to see command line usage and options.
    2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
    3. If --resources are not given after passing the CLI, a list of available devices (laptops) will be displayed on the terminal.
    4. Enter the resource numbers separated by commas (,) in the resource argument.

"""
import os
import csv
import time
import requests
import threading
import argparse
import pytz
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import importlib
import pandas as pd
import shutil
import logging
import json
import secrets
import asyncio
from flask_cors import CORS
import redis
import sys
import traceback

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
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
lf_base_interop_profile = importlib.import_module("py-scripts.lf_base_interop_profile")
RealDevice = lf_base_interop_profile.RealDevice

# Set up logging
logger = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Import LF logger configuration module
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class ZoomAutomation(Realm):
    def __init__(self, ssid="SSID", band="5G", security="wpa2", apname="AP Name", audio=True, video=True, lanforge_ip=None,
                 upstream_port='0.0.0.0', wait_time=30, devices=None, testname=None, config=None, selected_groups=None, selected_profiles=None):

        super().__init__(lfclient_host=lanforge_ip)
        self.upstream_port = upstream_port
        self.mgr_ip = lanforge_ip
        self.app = Flask(__name__)
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.redis_client.set('login_completed', 0)
        self.secret_key = secrets.token_hex(32)
        self.app.config['SECRET_KEY'] = self.secret_key
        CORS(self.app)
        self.devices = devices
        self.windows = 0
        self.linux = 0
        self.mac = 0
        self.real_sta_os_type = []
        self.real_sta_hostname = []
        self.real_sta_list = []
        self.real_sta_data = {}
        self.password_status = False  # Initially set to False
        self.login_completed = False  # Initially set to False
        self.remote_login_url = ""  # Initialize remote login URL
        self.remote_login_passwd = ""  # Initialize remote login password
        self.signin_email = ""
        self.signin_passwd = ""
        self.test_start = False
        self.start_time = None
        self.end_time = None
        self.participants_joined = 0
        self.participants_req = None
        self.ap_name = apname
        self.ssid = ssid
        self.band = band
        self.security = security
        self.tz = pytz.timezone('Asia/Kolkata')
        self.meet_link = None
        self.zoom_host = None
        self.testname = testname
        self.stop_signal = False

        # self.path = "/home/lanforge/lanforge-scripts/py-scripts/zoom_automation/test_results"
        self.path = os.path.join(os.getcwd(), "zoom_test_results")
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # self.path =  '/home/laxmi/Documents/lanforge-scripts/py-scripts/zoom_automation/test_results'
        self.device_names = []
        self.hostname_os_combination = None

        self.clients_disconnected = False
        self.audio = audio
        self.video = video
        self.wait_time = wait_time
        # os.makedirs(self.path, exist_ok=True)
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.name_prefix = "zoom"
        self.generic_endps_profile.type = "zoom"
        self.data_store = {}
        self.header = ["timestamp",
                       "Sent Audio Frequency (khz)", "Sent Audio Latency (ms)", "Sent Audio Jitter (ms)", "Sent Audio Packet loss (%)",
                       "Receive Audio Frequency (khz)", "Receive Audio Latency (ms)", "Receive Audio Jitter (ms)", "Receive Audio Packet loss (%)",
                       "Sent Video Latency (ms)", "Sent Video Jitter (ms)", "Sent Video Packet loss (%)", "Sent Video Resolution (khz)",
                       "Sent Video Frames ps (khz)", "Receive Video Latency (ms)", "Receive Video Jitter (ms)", "Receive Video Packet loss (%)",
                       "Receive Video Resolution (khz)", "Receive Video Frames ps (khz)"
                       ]
        self.config = config
        self.selected_groups = selected_groups
        self.selected_profiles = selected_profiles

    def start_flask_server(self):
        @self.app.route('/login_url', methods=['GET', 'POST'])
        def login_url():
            if request.method == 'GET':
                return jsonify({"login_url": self.remote_login_url})
            elif request.method == 'POST':
                data = request.json
                self.remote_login_url = data.get('login_url', '')
                return jsonify({"message": f"Updated login_url to {self.remote_login_url}"})

        @self.app.route('/login_passwd', methods=['GET', 'POST'])
        def login_passwd():
            if request.method == 'GET':
                return jsonify({"login_passwd": self.remote_login_passwd})
            elif request.method == 'POST':
                data = request.json
                self.remote_login_passwd = data.get('login_passwd', '')
                return jsonify({"message": "Password updated successfully."})

        @self.app.route('/meeting_link', methods=['GET', 'POST'])
        def meeting_link():
            if request.method == 'GET':
                return jsonify({"meet_link": self.meet_link})
            elif request.method == 'POST':
                data = request.json
                self.meet_link = data.get('meet_link', '')
                # "checking self.meet_link",self.meet_link)
                return jsonify({"message": "Meeting Link Updated sucessfully"})

        @self.app.route('/login_completed', methods=['GET', 'POST'])
        def login_completed():
            if request.method == 'GET':
                login_completed_status = self.redis_client.get('login_completed')
                return jsonify({"login_completed": bool(int(login_completed_status)) if login_completed_status else False})

            elif request.method == 'POST':
                data = request.json
                login_completed_status = int(data.get('login_completed', 0))
                self.redis_client.set('login_completed', login_completed_status)
                return jsonify({"message": f"Updated login_completed status to {bool(login_completed_status)}"})

        @self.app.route('/get_host_email', methods=['GET'])
        def get_host_email():
            return jsonify({"host_email": self.signin_email})

        @self.app.route('/get_host_passwd', methods=['GET'])
        def get_host_passwd():
            return jsonify({"host_passwd": self.signin_passwd})

        @self.app.route('/get_participants_joined', methods=['GET'])
        def get_participants_joined():
            return jsonify({"participants": self.participants_joined})

        @self.app.route('/set_participants_joined', methods=['POST'])
        def set_participants_joined():
            data = request.json
            self.participants_joined = data.get('participants_joined', None)
            return jsonify({"message": f"Updated participants jopind status to {self.participants_joined}"})

        @self.app.route('/get_participants_req', methods=['GET'])
        def get_participants_req():
            return jsonify({"participants": self.participants_req})

        @self.app.route('/test_started', methods=['GET', 'POST'])
        def test_started():
            if request.method == 'GET':
                return jsonify({"test_started": self.test_start})
            elif request.method == 'POST':
                data = request.json
                self.test_start = data.get('test_started', False)
                return jsonify({"message": f"Updated test_start status to {self.test_start}"})

        @self.app.route('/clients_disconnected', methods=['POST'])
        def client_disconnected():
            data = request.json
            self.clients_disconnected = data.get('clients_disconnected', False)
            return jsonify({"message": f"Updated clients_disconnected status to {self.clients_disconnected}"})

        @self.app.route('/get_start_end_time', methods=['GET'])
        def get_start_end_time():
            return jsonify({
                "start_time": self.start_time.isoformat() if self.start_time is not None else None,
                "end_time": self.end_time.isoformat() if self.end_time is not None else None
            })

        @self.app.route('/stats_opt', methods=['GET'])
        def stats_to_be_collected():
            return jsonify({
                'audio_stats': self.audio,
                "video_stats": self.video
            })

        @self.app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        @self.app.route('/upload_stats', methods=['POST'])
        def upload_stats():
            data = request.json
            for hostname, stats in data.items():
                self.data_store[hostname] = stats
            for hostname, stats in data.items():

                csv_file = os.path.join(self.path, f'{hostname}.csv')
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)

                    if os.path.getsize(csv_file) == 0:
                        writer.writerow(self.header)

                    timestamp = stats.get('timestamp', '')
                    audio = stats.get('audio_stats', {})
                    video = stats.get('video_stats', {})

                    row = [
                        timestamp,
                        audio.get('frequency_sent', '0'), audio.get('latency_sent', '0'), audio.get('jitter_sent', '0'), audio.get('packet_loss_sent', '0'),
                        audio.get('frequency_received', '0'), audio.get('latency_received', '0'), audio.get('jitter_received', '0'), audio.get('packet_loss_received', '0'),
                        video.get('latency_sent', '0'), video.get('jitter_sent', '0'), video.get('packet_loss_sent', '0'),
                        video.get('resolution_sent', '0'), video.get('frames_per_second_sent', '0'),
                        video.get('latency_received', '0'), video.get('jitter_received', '0'), video.get('packet_loss_received', '0'),
                        video.get('resolution_received', '0'), video.get('frames_per_second_received', '0')
                    ]
                    writer.writerow(row)

            return jsonify({"status": "success"}), 200

        @self.app.route('/get_latest_stats', methods=['GET'])
        def get_latest_stats():
            # Return the latest data for all hostnames
            return jsonify(self.data_store), 200

        @self.app.route('/stop_zoom', methods=['GET'])
        def stop_zoom():
            """
            Endpoint to stop the Zoom test and trigger a graceful application shutdown.
            """
            logging.info("Stopping the test through web UI")
            self.stop_signal = True  # Signal to stop the application
            # Respond to the client
            response = jsonify({"message": "Stopping Zoom Test"})
            response.status_code = 200
            # Trigger shutdown in a separate thread to avoid blocking
            shutdown_thread = threading.Thread(target=self.shutdown)
            shutdown_thread.start()
            return response

        try:
            self.app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)
        except Exception as e:
            logging.info(f"Error starting Flask server: {e}")
            sys.exit(0)

    def shutdown(self):
        """
        Gracefully shut down the application.
        """
        logging.info("Initiating graceful shutdown...")

        self.stop_signal = True
        time.sleep(10)
        logging.info("Exiting the application.")
        os._exit(0)

    def set_start_time(self):
        self.start_time = datetime.now(self.tz) + timedelta(seconds=30)
        self.end_time = self.start_time + timedelta(minutes=self.duration)
        return [self.start_time, self.end_time]

    def check_gen_cx(self):
        try:

            for gen_endp in self.generic_endps_profile.created_endp:
                generic_endpoint = self.json_get(f'/generic/{gen_endp}')

                if not generic_endpoint or "endpoint" not in generic_endpoint:
                    logging.info(f"Error fetching endpoint data for {gen_endp}")
                    return False

                endp_status = generic_endpoint["endpoint"].get("status", "")

                if endp_status not in ["Stopped", "WAITING", "NO-CX"]:
                    return False

            return True
        except Exception as e:
            logging.error(f"Error in check_gen_cx function {e}", exc_info=True)
            logging.info(f"generic endpoint data {generic_endpoint}")

    def wait_for_flask(self, url="http://127.0.0.1:5000/get_latest_stats", timeout=10):
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

    def run(self, duration, upstream_port, signin_email, signin_passwd, participants):
        # Store the email and password in the instance
        self.signin_email = signin_email
        self.signin_passwd = signin_passwd
        self.duration = duration
        self.upstream_port = upstream_port
        self.participants_req = participants
        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        self.wait_for_flask()
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

        if self.generic_endps_profile.create(ports=[self.real_sta_list[0]], real_client_os_types=[self.real_sta_os_type[0]]):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        if self.real_sta_os_type[0] == "windows":
            cmd = f"py zoom_host.py --ip {self.upstream_port}"
            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        elif self.real_sta_os_type[0] == 'linux':

            cmd = "su -l lanforge ctzoom.bash %s %s %s" % (self.new_port_list[0], self.upstream_port, "host")

            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        elif self.real_sta_os_type[0] == 'macos':
            cmd = "sudo bash ctzoom.bash %s %s" % (self.upstream_port, "host")
            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        self.generic_endps_profile.start_cx()
        time.sleep(5)

        while not self.login_completed:
            try:
                self.login_completed = bool(int(self.redis_client.get('login_completed') or 0))

                generic_endpoint = self.json_get(f'/generic/{self.generic_endps_profile.created_endp[0]}')
                endp_status = generic_endpoint["endpoint"]["status"]
                if endp_status == "Stopped":
                    logging.info("Failed to Start the Host Device")
                    self.generic_endps_profile.cleanup()
                    sys.exit(1)
                time.sleep(5)
            except Exception as e:
                logging.info(f"Error while checking login_completed status: {e}")
                time.sleep(5)

        if self.generic_endps_profile.create(ports=self.real_sta_list[1:], real_client_os_types=self.real_sta_os_type[1:]):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)
        for i in range(1, len(self.real_sta_os_type)):

            if self.real_sta_os_type[i] == "windows":
                cmd = f"py zoom_client.py --ip {self.upstream_port}"
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_type[i] == 'linux':
                cmd = "su -l lanforge ctzoom.bash %s %s %s" % (self.new_port_list[i], self.upstream_port, "client")
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_type[i] == 'macos':
                cmd = "sudo bash ctzoom.bash %s %s" % (self.upstream_port, "client")
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

        self.generic_endps_profile.start_cx()

        while not self.test_start:

            logging.info("WAITING FOR THE TEST TO BE STARTED")
            time.sleep(5)

        self.set_start_time()
        logging.info("TEST WILL BE STARTING")

        while datetime.now(self.tz) < self.end_time or not self.check_gen_cx():

            time.sleep(5)

    def select_real_devices(self, real_device_obj, real_sta_list=None):
        final_device_list = []
        """
        Selects real devices for testing.

        Args:
        - real_devices (RealDevice): Instance of RealDevice containing devices information.
        - real_sta_list (list, optional): List of specific real station names to select for testing.
        - base_interop_obj (object, optional): Base interop object to set for Devices.

        Returns:
        - list: Sorted list of selected real station names for testing.

        Steps:
        1. If `real_sta_list` is not provided, queries and retrieves all user-defined real stations from `real_devices`.
        2. Otherwise, assigns the provided `real_sta_list` to `self.real_sta_list`.
        3. If `base_interop_obj` is provided, assigns it to `self.Devices`.
        4. Sorts `self.real_sta_list` based on the second part of each station name.
        5. Logs an error and exits if no real stations are selected for testing.
        6. Logs the selected real station names.
        7. Adds real station data to `self.real_sta_data_dict`.
        8. Tracks the number of selected devices (`android`, `windows`, `mac`, `linux`).
        9. Returns the sorted list of selected real station names.

        """
        # Query and retrieve all user-defined real stations if `real_sta_list` is not provided
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_device_obj.query_user()
        else:
            interface_data = self.json_get("/port/all")
            interfaces = interface_data["interfaces"]
            final_device_list = []  # Initialize the list

            for device in real_sta_list:  # Iterate over devices in `real_sta_list` to preserve order
                for interface_dict in interfaces:  # Iterate through `interfaces`
                    for key, value in interface_dict.items():  # Iterate through items of each interface dictionary
                        # Check conditions for adding the device
                        key_parts = key.split(".")
                        extracted_key = ".".join(key_parts[:2])
                        if extracted_key == device and not value["phantom"] and not value["down"] and value["parent dev"] != "":
                            final_device_list.append(key)  # Add to final_device_list in order
                            break  # Stop after finding the first match for the current device to maintain order

            self.real_sta_list = final_device_list

        # Log an error and exit if no real stations are selected for testing
        if len(self.real_sta_list) == 0:
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)
        # Filter out iOS devices from the real_sta_list before proceeding
        self.real_sta_list = self.filter_ios_devices(self.real_sta_list)
        # # Add real station data to `self.real_sta_data_dict`
        for sta_name in self.real_sta_list:
            if sta_name not in real_device_obj.devices_data:
                self.real_sta_list.remove(sta_name)
                logger.error('Real station not in devices data, ignoring it from testing')
                continue

            self.real_sta_data[sta_name] = real_device_obj.devices_data[sta_name]

        self.real_sta_os_type = [self.real_sta_data[real_sta_name]['ostype'] for real_sta_name in self.real_sta_data]
        self.real_sta_hostname = [self.real_sta_data[real_sta_name]['hostname'] for real_sta_name in self.real_sta_data]

        self.zoom_host = self.real_sta_list[0]
        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_type)
        ]

        for key, value in self.real_sta_data.items():
            if value['ostype'] == 'windows':
                self.windows = self.windows + 1
            elif value['ostype'] == 'macos':
                self.mac = self.mac + 1
            elif value['ostype'] == 'linux':
                self.linux = self.linux + 1

        # Return the sorted list of selected real station names
        return self.real_sta_list

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

    def move_files(self, source_file, dest_dir):
        # Ensure the source file exists
        if not os.path.isfile(source_file):
            logging.error(f"Source file '{source_file}' does not exist or is not a regular file.")
            return

        # Ensure the destination directory exists
        if not os.path.exists(dest_dir):
            logging.error(f"Destination directory '{dest_dir}' does not exist.")
            return

        try:
            # Extract the filename from the source file path
            filename = os.path.basename(source_file)

            # Construct the destination file path
            dest_file = os.path.join(dest_dir, filename)

            # Move the file
            shutil.move(source_file, dest_file)

            logging.info(f"Successfully moved '{source_file}' to '{dest_file}'.")
        except Exception as e:
            logging.error(f"Failed to move '{source_file}' to '{dest_dir}': {e}")

    def updating_webui_runningjson(self, obj):
        data = {}
        file_path = self.path + "/../../Running_instances/{}_{}_running.json".format(self.mgr_ip, self.testname)

        # Wait until the file exists
        while not os.path.exists(file_path):
            logging.info("Waiting for the running json file to be created")
            time.sleep(1)
        logging.info("Running Json file found")
        with open(file_path, 'r') as file:
            data = json.load(file)

        for key in obj:
            data[key] = obj[key]

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def generate_report(self):
        report = lf_report(_output_pdf='zoom_call_report.pdf',
                           _output_html='zoom_call_report.html',
                           _results_dir_name="zoom_call_report",
                           _path=self.path)
        report_path_date_time = report.get_path_date_time()

        report.set_title("Zoom Call Automated Report")
        report.build_banner()

        report.set_table_title("Objective:")
        report.build_table_title()
        report.set_text("The objective is to conduct automated Zoom call tests across multiple laptops to gather statistics on sent audio, video, and received audio, video performance." +
                        "The test will collect these statistics and store them in a CSV file. Additionally, automated graphs will be generated using the collected data.")
        report.build_text_simple()

        report.set_table_title("Test Parameters:")
        report.build_table_title()
        testtype = ""
        if self.audio and self.video:
            testtype = "AUDIO & VIDEO"
        elif self.audio:
            testtype = "AUDIO"
        elif self.video:
            testtype = "VIDEO"

        if self.config:
            test_parameters = pd.DataFrame([{
                "Configured Devices": self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
                'Test Duration(min)': self.duration,
                'EMAIL ID': self.signin_email,
                "PASSWORD": self.signin_passwd,
                "HOST": self.real_sta_list[0],
                "TEST TYPE": testtype,
                "SSID": self.ssid,
                "Security": self.security

            }])
        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            # Map each group with a profile
            gp_pairs = zip(self.selected_groups, self.selected_profiles)

            # Create a string by joining the mapped pairs
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

            test_parameters = pd.DataFrame([{
                "Configuration": gp_map,
                "Configured Devices": self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
                'Test Duration(min)': self.duration,
                'EMAIL ID': self.signin_email,
                "PASSWORD": self.signin_passwd,
                "HOST": self.real_sta_list[0],
                "TEST TYPE": testtype,

            }])
        else:

            test_parameters = pd.DataFrame([{
                "Configured Devices": self.hostname_os_combination,
                'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
                'Test Duration(min)': self.duration,
                'EMAIL ID': self.signin_email,
                "PASSWORD": self.signin_passwd,
                "HOST": self.real_sta_list[0],
                "TEST TYPE": testtype,

            }])

        test_parameters = pd.DataFrame([{

            'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
            'Test Duration(min)': self.duration,
            'EMAIL ID': self.signin_email,
            "PASSWORD": self.signin_passwd,
            "HOST": self.real_sta_list[0],
            "TEST TYPE": testtype

        }])
        report.set_table_dataframe(test_parameters)
        report.build_table()

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
        for i in range(0, len(self.device_names)):
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
                file_path = os.path.join(self.path, f'{self.device_names[i]}.csv')
                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:

                        per_client_data["audio_jitter_s"].append(float(row["Sent Audio Jitter (ms)"]))
                        per_client_data["audio_jitter_r"].append(float(row["Receive Audio Jitter (ms)"]))
                        per_client_data["audio_latency_s"].append(float(row["Sent Audio Latency (ms)"]))
                        per_client_data["audio_latency_r"].append(float(row["Receive Audio Latency (ms)"]))
                        per_client_data["audio_pktloss_s"].append(float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                        per_client_data["audio_pktloss_r"].append(float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                        per_client_data["video_jitter_s"].append(float(row["Sent Video Jitter (ms)"]))
                        per_client_data["video_jitter_r"].append(float(row["Receive Video Jitter (ms)"]))
                        per_client_data["video_latency_s"].append(float(row["Sent Video Latency (ms)"]))
                        per_client_data["video_latency_r"].append(float(row["Receive Video Latency (ms)"]))
                        per_client_data["video_pktloss_s"].append(float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%", "")))
                        per_client_data["video_pktloss_r"].append(float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%", "")))

                        temp_max_audio_jitter_s = max(temp_max_audio_jitter_s, float(row["Sent Audio Jitter (ms)"]))
                        temp_max_audio_jitter_r = max(temp_max_audio_jitter_r, float(row["Receive Audio Jitter (ms)"]))
                        temp_max_audio_latency_s = max(temp_max_audio_latency_s, float(row["Sent Audio Latency (ms)"]))
                        temp_max_audio_latency_r = max(temp_max_audio_latency_r, float(row["Receive Audio Latency (ms)"]))
                        temp_max_audio_pktloss_s = max(temp_max_audio_pktloss_s, float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                        temp_max_audio_pktloss_r = max(temp_max_audio_pktloss_r, float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))

                        temp_max_video_jitter_s = max(temp_max_video_jitter_s, float(row["Sent Video Jitter (ms)"]))
                        temp_max_video_jitter_r = max(temp_max_video_jitter_r, float(row["Receive Video Jitter (ms)"]))
                        temp_max_video_latency_s = max(temp_max_video_latency_s, float(row["Sent Video Latency (ms)"]))
                        temp_max_video_latency_r = max(temp_max_video_latency_r, float(row["Receive Video Latency (ms)"]))
                        temp_max_video_pktloss_s = max(temp_max_video_pktloss_s, float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%", "")))
                        temp_max_video_pktloss_r = max(temp_max_video_pktloss_r, float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%", "")))

                        temp_min_audio_jitter_s = min(
                            temp_min_audio_jitter_s,
                            float(
                                row["Sent Audio Jitter (ms)"])) if temp_min_audio_jitter_s > 0 and float(
                            row["Sent Audio Jitter (ms)"]) > 0 else (
                            float(
                                row["Sent Audio Jitter (ms)"]) if float(
                                row["Sent Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_s)
                        temp_min_audio_jitter_r = min(
                            temp_min_audio_jitter_r, float(
                                row["Receive Audio Jitter (ms)"])) if temp_min_audio_jitter_r > 0 and float(
                            row["Receive Audio Jitter (ms)"]) > 0 else (
                            float(
                                row["Receive Audio Jitter (ms)"]) if float(
                                row["Receive Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_r)
                        temp_min_audio_latency_s = min(
                            temp_min_audio_latency_s, float(
                                row["Sent Audio Latency (ms)"])) if temp_min_audio_latency_s > 0 and float(
                            row["Sent Audio Latency (ms)"]) > 0 else (
                            float(
                                row["Sent Audio Latency (ms)"]) if float(
                                row["Sent Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_s)
                        temp_min_audio_latency_r = min(
                            temp_min_audio_latency_r, float(
                                row["Receive Audio Latency (ms)"])) if temp_min_audio_latency_r > 0 and float(
                            row["Receive Audio Latency (ms)"]) > 0 else (
                            float(
                                row["Receive Audio Latency (ms)"]) if float(
                                row["Receive Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_r)

                        temp_min_audio_pktloss_s = min(
                            temp_min_audio_pktloss_s, float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", ""))) if temp_min_audio_pktloss_s > 0 and float(
                            (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                "%", "")) > 0 else (
                            float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) if float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) > 0 else temp_min_audio_pktloss_s)
                        temp_min_audio_pktloss_r = min(
                            temp_min_audio_pktloss_r, float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", ""))) if temp_min_audio_pktloss_r > 0 and float(
                            (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                "%", "")) > 0 else (
                            float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) if float(
                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) > 0 else temp_min_audio_pktloss_r)

                        temp_min_video_jitter_s = min(
                            temp_min_video_jitter_s,
                            float(
                                row["Sent Video Jitter (ms)"])) if temp_min_video_jitter_s > 0 and float(
                            row["Sent Video Jitter (ms)"]) > 0 else (
                            float(
                                row["Sent Video Jitter (ms)"]) if float(
                                row["Sent Video Jitter (ms)"]) > 0 else temp_min_video_jitter_s)
                        temp_min_video_jitter_r = min(
                            temp_min_video_jitter_r, float(
                                row["Receive Video Jitter (ms)"])) if temp_min_video_jitter_r > 0 and float(
                            row["Receive Video Jitter (ms)"]) > 0 else (
                            float(
                                row["Receive Video Jitter (ms)"]) if float(
                                row["Receive Video Jitter (ms)"]) > 0 else temp_min_video_jitter_r)
                        temp_min_video_latency_s = min(
                            temp_min_video_latency_s, float(
                                row["Sent Video Latency (ms)"])) if temp_min_video_latency_s > 0 and float(
                            row["Sent Video Latency (ms)"]) > 0 else (
                            float(
                                row["Sent Video Latency (ms)"]) if float(
                                row["Sent Video Latency (ms)"]) > 0 else temp_min_video_latency_s)
                        temp_min_video_latency_r = min(
                            temp_min_video_latency_r, float(
                                row["Receive Video Latency (ms)"])) if temp_min_video_latency_r > 0 and float(
                            row["Receive Video Latency (ms)"]) > 0 else (
                            float(
                                row["Receive Video Latency (ms)"]) if float(
                                row["Receive Video Latency (ms)"]) > 0 else temp_min_video_latency_r)

                        temp_min_video_pktloss_s = min(
                            temp_min_video_pktloss_s, float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", ""))) if temp_min_video_pktloss_s > 0 and float(
                            (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                "%", "")) > 0 else (
                            float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) if float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) > 0 else temp_min_video_pktloss_s)
                        temp_min_video_pktloss_r = min(
                            temp_min_video_pktloss_r, float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", ""))) if temp_min_video_pktloss_r > 0 and float(
                            (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                "%", "")) > 0 else (
                            float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) if float(
                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                    "%", "")) > 0 else temp_min_video_pktloss_r)

            except Exception as e:
                logging.error(f"Error in reading data in client {self.device_names[i]}", e)
                no_csv_client.append(self.device_names[i])
                rejected_clients.append(self.device_names[i])
            if self.device_names[i] not in no_csv_client:
                client_array.append(self.device_names[i])
                accepted_clients.append(self.device_names[i])
                accepted_ostypes.append(self.real_sta_os_type[i])
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

        report.set_table_title("Test Devices:")
        report.build_table_title()

        device_details = pd.DataFrame({
            'Hostname': self.real_sta_hostname,
            'OS Type': self.real_sta_os_type,
            "MAC": self.mac_list,
            "RSSI": self.rssi_list,
            "Link Rate": self.link_rate_list,
            "SSID": self.ssid_list,

        })
        report.set_table_dataframe(device_details)
        report.build_table()

        if self.audio:
            report.set_graph_title("Audio Latency (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Audio Latency(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Audio Jitter (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Audio Jitter(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Audio Packet Loss (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Audio Packet Loss(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_table_title("Test Audio Results Table:")
            report.build_table_title()
            audio_test_details = pd.DataFrame({
                'Device Name': [client for client in accepted_clients],
                'Avg Latency Sent (ms)': [round(sum(data["audio_latency_s"]) / len(data["audio_latency_s"]), 2) if len(data["audio_latency_s"]) != 0 else 0 for data in final_dataset],
                'Avg Latency Recv (ms)': [round(sum(data["audio_latency_r"]) / len(data["audio_latency_r"]), 2) if len(data["audio_latency_r"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Sent (ms)': [round(sum(data["audio_jitter_s"]) / len(data["audio_jitter_s"]), 2) if len(data["audio_jitter_s"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Recv (ms)': [round(sum(data["audio_jitter_r"]) / len(data["audio_jitter_r"]), 2) if len(data["audio_jitter_r"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Sent': [round(sum(data["audio_pktloss_s"]) / len(data["audio_pktloss_s"]), 2) if len(data["audio_pktloss_s"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Recv': [round(sum(data["audio_pktloss_r"]) / len(data["audio_pktloss_r"]), 2) if len(data["audio_pktloss_r"]) != 0 else 0 for data in final_dataset],
                'CSV link': ['<a href="{}.csv" target="_blank">csv data</a>'.format(client) for client in accepted_clients]

            })
            report.set_table_dataframe(audio_test_details)
            report.dataframe_html = report.dataframe.to_html(index=False,
                                                             justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
            report.html += report.dataframe_html
        if self.video:
            report.set_graph_title("Video Latency (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Video Latency(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Video Jitter (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Video Jitter(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Video Packet Loss (Sent/Received)")
            report.build_graph_title()
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
                _graph_image_name="Video Packet Loss(sent and received)",
                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_table_title("Test Video Results Table:")
            report.build_table_title()
            video_test_details = pd.DataFrame({
                'Device Name': [client for client in accepted_clients],
                'Avg Latency Sent (ms)': [round(sum(data["video_latency_s"]) / len(data["video_latency_s"]), 2) if len(data["video_latency_s"]) != 0 else 0 for data in final_dataset],
                'Avg Latency Recv (ms)': [round(sum(data["video_latency_r"]) / len(data["video_latency_r"]), 2) if len(data["video_latency_r"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Sent (ms)': [round(sum(data["video_jitter_s"]) / len(data["video_jitter_s"]), 2) if len(data["video_jitter_s"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Recv (ms)': [round(sum(data["video_jitter_r"]) / len(data["video_jitter_r"]), 2) if len(data["video_jitter_r"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Sent': [round(sum(data["video_pktloss_s"]) / len(data["video_pktloss_s"]), 2) if len(data["video_pktloss_s"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Recv': [round(sum(data["video_pktloss_r"]) / len(data["video_pktloss_r"]), 2) if len(data["video_pktloss_r"]) != 0 else 0 for data in final_dataset],
                'CSV link': ['<a href="{}.csv" target="_blank">csv data</a>'.format(client) for client in accepted_clients]
            })
            report.set_table_dataframe(video_test_details)

            report.dataframe_html = report.dataframe.to_html(index=False,
                                                             justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
            report.html += report.dataframe_html
        report.set_custom_html("<br/><hr/>")
        report.build_custom()

        report.write_html()
        report.write_pdf(_page_size='Legal', _orientation='Landscape')
        for client in accepted_clients:
            file_to_move_path = os.path.join(self.path, f'{client}.csv')
            self.move_files(file_to_move_path, report_path_date_time)

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
        parser = argparse.ArgumentParser(description="Zoom Automation Script")
        parser.add_argument('--duration', type=int, required=True, help="Duration of the Zoom meeting in minutes")
        parser.add_argument('--lanforge_ip', type=str, required=True, help="LANforge IP address")
        parser.add_argument('--signin_email', type=str, required=True, help="Sign-in email")
        parser.add_argument('--signin_passwd', type=str, required=True, help="Sign-in password")
        parser.add_argument('--participants', type=int, required=True, help="no of participanrs")
        parser.add_argument('--audio', action='store_true')
        parser.add_argument('--video', action='store_true')
        parser.add_argument("--wait_time", type=int, default=30, help='time set to wait for the csv files')
        parser.add_argument('--log_level', help='Level of the logs to be dispalyed')
        parser.add_argument('--lf_logger_config_json', help='lf_logger config json')
        parser.add_argument('--resources', help="resources participated in the test")
        parser.add_argument('--do_webUI', action='store_true', help='useful to specify whether we are running through webui or cli')
        parser.add_argument('--report_dir', help="report directory while running test through web ui")
        parser.add_argument('--testname', help="report directory while running test through web ui")
        parser.add_argument('--zoom_host', help="Host of the test")

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
        parser.add_argument("--upstream_port", type=str, default=None)
        parser.add_argument('--help_summary', help='Show summary of what this script does', default=None)
        parser.add_argument("--expected_passfail_value", help="Specify the expected urlcount value for pass/fail")
        parser.add_argument("--device_csv_name", type=str, help="Specify the device csv name for pass/fail", default=None)
        parser.add_argument('--config', action='store_true', help='specify this flag whether to config devices or not')

        args = parser.parse_args()

        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

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

            zoom_automation = ZoomAutomation(audio=args.audio, video=args.video, lanforge_ip=args.lanforge_ip, wait_time=args.wait_time, testname=args.testname,
                                             upstream_port=args.upstream_port, config=args.config, selected_groups=selected_groups, selected_profiles=selected_profiles)
            args.upstream_port = zoom_automation.change_port_to_ip(args.upstream_port)
            realdevice = RealDevice(manager_ip=args.lanforge_ip,
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

            if args.file_name and args.do_webUI:
                new_filename = args.removesuffix(".csv")
            else:
                new_filename = args.file_name
            config_obj = DeviceConfig.DeviceConfig(lanforge_ip=args.lanforge_ip, file_name=new_filename)

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
                if args.zoom_host in eid_list:
                    # Remove the existing instance of args.zoom_host from the list
                    eid_list.remove(args.zoom_host)
                    # Insert args.zoom_host at the beginning of the list
                    eid_list.insert(0, args.zoom_host)

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
                        if not args.do_webUI:
                            args.zoom_host = args.zoom_host.strip()
                            if args.zoom_host in dev_list:
                                dev_list.remove(args.zoom_host)
                            dev_list.insert(0, args.zoom_host)
                        if args.config:
                            asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                        args.resources = ",".join(id for id in dev_list)
                else:
                    # If no resources provided, prompt user to select devices manually
                    if args.config:
                        all_devices = config_obj.get_all_devices()
                        device_list = []
                        for device in all_devices:
                            if device["type"] != 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                            elif device["type"] == 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                        print("Available Devices For Testing")
                        for device in device_list:
                            print(device)
                        zm_host = input("Enter Host Resource for the Test : ")
                        zm_host = zm_host.strip()
                        args.resources = input("Enter client Resources to run the test :")
                        args.resources = zm_host + "," + args.resources
                        dev1_list = args.resources.split(',')
                        asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

            result_list = []
            if not args.do_webUI:
                if args.resources:
                    resources = args.resources.split(',')
                    resources = [r for r in resources if len(r.split('.')) > 1]
                    # resources = sorted(resources, key=lambda x: int(x.split('.')[1]))
                    get_data = zoom_automation.select_real_devices(real_device_obj=realdevice, real_sta_list=resources)
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
                    resources = zoom_automation.select_real_devices(real_device_obj=realdevice)
            else:
                if args.do_webUI:
                    zoom_automation.path = args.report_dir
                resources = args.resources.split(',')
                extracted_parts = [res.split('.')[:2] for res in resources]
                formatted_parts = ['.'.join(parts) for parts in extracted_parts]

                zoom_automation.select_real_devices(real_device_obj=realdevice, real_sta_list=formatted_parts)
                if args.do_webUI:

                    if len(zoom_automation.real_sta_hostname) == 0:
                        logging.info("No device is available to run the test")
                        obj = {
                            "status": "Stopped",
                            "configuration_status": "configured"
                        }
                        zoom_automation.updating_webui_runningjson(obj)
                        return
                    else:
                        obj = {
                            "configured_devices": zoom_automation.real_sta_hostname,
                            "configuration_status": "configured",
                            "no_of_devices": f' Total({len(zoom_automation.real_sta_os_type)}) : W({zoom_automation.windows}),L({zoom_automation.linux}),M({zoom_automation.mac})',
                            "device_list": zoom_automation.hostname_os_combination,
                            # "zoom_host":zoom_automation.zoom_host

                        }
                        zoom_automation.updating_webui_runningjson(obj)

            if not zoom_automation.check_tab_exists():
                logging.error('Generic Tab is not available.\nAborting the test.')
                exit(0)

            zoom_automation.run(args.duration, args.upstream_port, args.signin_email, args.signin_passwd, args.participants)
            zoom_automation.data_store.clear()
            zoom_automation.generate_report()
            logging.info("Test Completed Sucessfully")
    except Exception as e:
        logging.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
        traceback.print_exc()
    finally:
        if args.do_webUI:
            try:
                url = f"http://{args.lanforge_ip}:5454/update_status_yt"
                headers = {
                    'Content-Type': 'application/json',
                }

                data = {
                    'status': 'Completed',
                    'name': args.testname
                }

                response = requests.post(url, json=data, headers=headers)

                if response.status_code == 200:
                    logging.info("Successfully updated STOP status to 'Completed'")
                    pass
                else:
                    logging.error(f"Failed to update STOP status: {response.status_code} - {response.text}")

            except Exception as e:
                # Print an error message if an exception occurs during the request
                logging.error(f"An error occurred while updating status: {e}")

        zoom_automation.redis_client.set('login_completed', 0)
        zoom_automation.stop_signal = True
        logging.info("Waiting for Browser Cleanup in Laptops")
        time.sleep(10)
        zoom_automation.generic_endps_profile.cleanup()


if __name__ == "__main__":
    main()
