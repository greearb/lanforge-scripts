#!/usr/bin/env python3
"""
    NAME: lf_interop_teams.py

    PURPOSE: lf_interop_teams.py provides the available devices and allows the user to start Microsoft Teams call conference meeting for the user-specified duration

    EXAMPLE-1:
    Command Line Interface to run Teams:
    python3 lf_interop_teams.py --mgr 192.168.204.75 --upstream_port 1.1.eth1 --participants 3 --duration 1 --audio --video

    EXAMPLE-2:
    Command Line Interface to run Teams on Specified Resources:
    python3 lf_interop_teams.py --mgr 192.168.204.75 --upstream_port 1.1.eth1 --participants 3 --duration 1 --audio --video --resources 1.95,1.400,1.300


    NOTES:
    1. Use 'python3 lf_interop_teams.py --help' to see command line usage and options.
    2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
    3. If --resources are not given after passing the CLI, a list of available devices will be displayed on the terminal.
    4. Enter the resource numbers separated by commas (,) in the resource argument Eg: (1.95,1.200).

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
import sys
import traceback
import glob

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))


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


class TeamsAutomation(Realm):
    def __init__(self,
                 lanforge_ip=None,
                 duration=None,
                 upstream_port=None,
                 no_pre_cleanup=None,
                 no_post_cleanup=None,
                 participants_req=None,
                 audio=None,
                 video=None,
                 do_webui=None,
                 test_name=None,
                 report_dir=None

                 ):
        super().__init__(lfclient_host=lanforge_ip)
        self.app = Flask(__name__)
        self.lanforge_ip = lanforge_ip
        self.duration = duration
        self.upstream_port = upstream_port
        self.no_pre_cleanup = no_pre_cleanup
        self.no_post_cleanup = no_post_cleanup
        self.realdevice = None
        self.real_sta_list = []
        self.real_sta_data_dict = {}
        self.real_sta_os_types = []
        self.real_sta_hostname = []
        self.hostname_os_combination = []
        self.wifi_interfaces = []
        self.windows = 0
        self.linux = 0
        self.mac = 0
        self.meet_link = None
        self.participants_joined = None
        self.participants_req = participants_req
        self.test_start = False
        self.start_time = None
        self.end_time = None
        self.audio = None
        self.video = None
        self.login_completed = False
        self.credentials = []
        self.cred_index = 0
        self.tz = pytz.timezone('Asia/Kolkata')
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.name_prefix = "zoom"
        self.generic_endps_profile.type = "zoom"
        self.audio = audio
        self.video = video
        self.audio_stats_header = [
            'Sent Audio bitrate(Kbps)',
            'Sent Audio Packets',
            'Audio RTT(ms)',
            'sent Audio codec',
            'Received Audio Jitter(ms)',
            'Receievd Audio Packet Loss(%)',
            'Received Audio Packets',
            'Recevied Audio Codec'
        ]

        self.video_stats_header = [
            'Sent video bitrate(Mbps)',
            'Received video bitrate(Mbps)',
            'Sent video frame rate(fps)',
            'Sent video resolution(px)',
            'video RTT (ms)',
            'sent video packets',
            'sent video codec',
            'video processing'
        ]

        if self.audio:
            self.header = ['timestamp'] + self.audio_stats_header
        if self.video:
            if self.audio:
                self.header += self.video_stats_header
            else:
                self.header = ['timestamp'] + self.video_stats_header
        self.data_store = {}
        self.stop_signal = False
        self.path = os.path.join(os.getcwd(), "teams_test_results")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.do_webui = do_webui
        self.test_name = test_name
        self.report_dir = report_dir
        self.execute_finally = False

    def updating_webui_runningjson(self, obj):
        data = {}
        file_path = self.path + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name)

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

    def update_webui_data(self):
        if len(self.real_sta_hostname) == 0:
            logging.info("No device is available to run the test")
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
                "device_list": self.hostname_os_combination,
            }
            self.updating_webui_runningjson(obj)

    def wait_for_flask(self, url="http://127.0.0.1:5005/test_server", timeout=10):
        """Wait until the Flask server is up, but exit if it takes longer than `timeout` seconds."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    logging.info("Flask server is up and running!")
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        logging.error("Flask server did not start within 10 seconds. Exiting.")
        sys.exit(1)

    def run(self):
        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        self.wait_for_flask()

        if self.generic_endps_profile.create(ports=[self.real_sta_list[0]], real_client_os_types=[self.real_sta_os_types[0]]):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)

        if self.real_sta_os_types[0] == "windows":
            cmd = f"py teams_host.py --ip {self.upstream_port}"
            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        elif self.real_sta_os_types[0] == 'linux':

            cmd = "su -l lanforge ctteams.bash %s %s %s" % (self.wifi_interfaces[0], self.upstream_port, "host")

            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        elif self.real_sta_os_types[0] == 'macos':
            cmd = "sudo bash ctteams.bash %s %s" % (self.upstream_port, "host")
            self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[0], cmd)
        self.generic_endps_profile.start_cx()
        time.sleep(5)

        while not self.login_completed:
            try:

                generic_endpoint = self.json_get(f'/generic/{self.generic_endps_profile.created_endp[0]}')
                endp_status = generic_endpoint["endpoint"]["status"]
                if endp_status == "Stopped":
                    logging.error("Failed to Start the Host Device")
                    self.generic_endps_profile.cleanup()
                    os._exit(1)
                time.sleep(5)
            except Exception as e:
                logging.info(f"Error while checking login_completed status: {e}")
                time.sleep(5)

        if self.generic_endps_profile.create(ports=self.real_sta_list[1:], real_client_os_types=self.real_sta_os_types[1:]):
            logging.info('Real client generic endpoint creation completed.')
        else:
            logging.error('Real client generic endpoint creation failed.')
            exit(0)
        for i in range(1, len(self.real_sta_os_types)):

            if self.real_sta_os_types[i] == "windows":
                cmd = f"py teams_client.py --ip {self.upstream_port}"
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_types[i] == 'linux':
                cmd = "su -l lanforge ctteams.bash %s %s %s" % (self.wifi_interfaces[i], self.upstream_port, "client")
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)
            elif self.real_sta_os_types[i] == 'macos':
                cmd = "sudo bash ctteams.bash %s %s" % (self.upstream_port, "client")
                self.generic_endps_profile.set_cmd(self.generic_endps_profile.created_endp[i], cmd)

        self.generic_endps_profile.start_cx()

        while not self.test_start:

            logging.info("WAITING FOR THE TEST TO BE STARTED")
            time.sleep(5)

        self.set_start_time()
        logging.info("TEST WILL BE STARTING")

        while datetime.now(self.tz) < self.end_time or not self.check_gen_cx():
            if self.stop_signal:
                break

            time.sleep(5)

    def generate_report(self):
        report = lf_report(_output_pdf='teams_call_report.pdf',
                           _output_html='teams_call_report.html',
                           _results_dir_name="teams_call_report",
                           _path=self.path)
        self.report_path_date_time = report.get_path_date_time()

        report.set_title("Teams Call Automated Report")
        report.build_banner()

        report.set_table_title("Objective:")
        report.build_table_title()
        report.set_text("The objective is to conduct automated Teams call tests across multiple laptops to gather statistics on sent audio, video, and received audio, video performance." +
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

        test_parameters = pd.DataFrame([{

            'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
            'Test Duration(min)': self.duration,
            "HOST": self.real_sta_list[0],
            "TEST TYPE": testtype

        }])
        report.set_table_dataframe(test_parameters)
        report.build_table()

        # Read per-device average metrics
        df = pd.read_csv(os.path.join(self.path, "teams_call_avg_data.csv"))
        df.columns = df.columns.str.strip()

        report.set_table_title("Test Devices:")
        report.build_table_title()

        device_details = pd.DataFrame({
            'Hostname': self.real_sta_hostname,
            'OS Type': self.real_sta_os_types,
        })
        report.set_table_dataframe(device_details)
        report.build_table()

        if self.audio:
            metrics = [
                ("Audio RTT(ms)", "Audio RTT (ms)"),
                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                ("Sent Audio bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
            ]

        if self.video:
            # Create bar graphs for each metric
            metrics = [
                ("Sent video bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                ("Received video bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                ("sent video packets", "Sent Video Packets"),
            ]
        if self.audio and self.video:
            # Create bar graphs for each metric
            metrics = [
                ("Audio RTT(ms)", "Audio RTT (ms)"),
                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                ("Sent Audio bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
                ("Sent video bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                ("Received video bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                ("sent video packets", "Sent Video Packets"),
            ]

        for column, title in metrics:
            report.set_graph_title(f"Average {title}")
            report.build_graph_title()

            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=[df[column].tolist()],
                _xaxis_name=f"AVG {title}",
                _yaxis_name="Devices",
                _yaxis_label=df["Device Name"].tolist(),
                _yaxis_categories=df["Device Name"].tolist(),
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.25,
                _color_name=["orange"],
                _show_bar_value=True,
                _figsize=(16, len(df) * 1 + 4),
                _graph_title=f"AVG {title} Per Device",
                _graph_image_name=title.replace(" ", "_"),
                _label=[title]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

        if self.audio:
            selected_columns = [
                "Device Name",
                "Sent Audio bitrate(Kbps)",
                "Sent Audio Packets",
                "Audio RTT(ms)",
                "Received Audio Jitter(ms)",
                "Receievd Audio Packet Loss(%)",
            ]

            column_headings = {
                "Device Name": "Device Name",
                "Sent Audio bitrate(Kbps)": "AVG Sent Audio Bitrate (Kbps)",
                "Sent Audio Packets": "AVG Sent Audio Packets",
                "Audio RTT(ms)": "AVG Audio RTT (ms)",
                "Received Audio Jitter(ms)": "AVG Received Audio Jitter (ms)",
                "Receievd Audio Packet Loss(%)": "AVG Received Audio Packet Loss (%)",
            }

            filtered_df = df[selected_columns].rename(columns=column_headings)

            report.set_table_title("Test Audio Results Table")
            report.build_table_title()
            report.set_table_dataframe(filtered_df)
            report.build_table()

        if self.video:
            selected_columns = [
                "Device Name",
                "Sent video bitrate(Mbps)",
                "Received video bitrate(Mbps)",
                "Sent video frame rate(fps)",
                "video RTT (ms)",
                "sent video packets",
            ]

            column_headings = {
                "Device Name": "Device Name",
                "Sent video bitrate(Mbps)": "AVG Sent Video Bitrate (Mbps)",
                "Received video bitrate(Mbps)": "AVG Received Video Bitrate (Mbps)",
                "Sent video frame rate(fps)": "AVG Sent Video Frame Rate (fps)",
                "video RTT (ms)": "AVG Video RTT (ms)",
                "sent video packets": "AVG Sent Video Packets",
            }

            filtered_df = df[selected_columns].rename(columns=column_headings)

            report.set_table_title("Test Video Results Table")
            report.build_table_title()
            report.set_table_dataframe(filtered_df)
            report.build_table()

        report.write_html()
        report.write_pdf()

    def check_gen_cx(self):
        try:

            for gen_endp in self.generic_endps_profile.created_endp:
                generic_endpoint = self.json_get(f'/generic/{gen_endp}')

                if not generic_endpoint or "endpoint" not in generic_endpoint:
                    logging.info(f"Error fetching endpoint data for {gen_endp}")
                    return False

                endp_status = generic_endpoint["endpoint"].get("status", "")

                if endp_status not in ["Stopped", "WAITING", "NO-CX", "PHANTOM", "FTM_WAIT"]:
                    return False

            return True
        except Exception as e:
            logging.error(f"Error in check_gen_cx function {e}", exc_info=True)
            logging.info(f"generic endpoint data {generic_endpoint}")

    def set_start_time(self):
        self.start_time = datetime.now(self.tz) + timedelta(seconds=30)
        self.end_time = self.start_time + timedelta(minutes=self.duration)
        return [self.start_time, self.end_time]

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

    def select_real_devices(self, real_sta_list=None):
        """
        Selects real devices for testing.

        Args:
        - real_sta_list (list, optional): List of specific real station names to select for testing.

        Returns:
        - list: List of selected real station names for testing.
        """
        final_device_list = []
        self.realdevice.get_devices()

        # Retrieve real station list
        if real_sta_list is None:
            self.real_sta_list, _, _ = self.realdevice.query_user()
        else:
            if not self.do_webui:
                interface_data = self.json_get("/port/all")
                interfaces = interface_data["interfaces"]
                real_sta_list = [sta.strip() for sta in real_sta_list.split(',') if sta.strip()]
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
            else:
                self.real_sta_list = real_sta_list.split(',')

        # Abort if no stations
        if len(self.real_sta_list) == 0:
            logger.error("There are no real devices in this testbed. Aborting test")
            exit(0)

        self.realdevice.get_devices()
        self.real_sta_list = self.filter_ios_devices(self.real_sta_list)

        if len(self.real_sta_list) == 0:
            logger.error("There are no real devices in this testbed. Aborting test")
            exit(0)

        # Filter and store device data
        for sta_name in self.real_sta_list[:]:
            if sta_name not in self.realdevice.devices_data:
                logger.error(f"Real station '{sta_name}' not in devices data, ignoring it from testing")
                self.real_sta_list.remove(sta_name)
                continue
            self.real_sta_data_dict[sta_name] = self.realdevice.devices_data[sta_name]

        # Populate OS types and hostnames
        self.real_sta_os_types = [
            self.real_sta_data_dict[name]['ostype'] for name in self.real_sta_data_dict
        ]
        self.real_sta_hostname = [
            self.real_sta_data_dict[name]['hostname'] for name in self.real_sta_data_dict
        ]
        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_types)
        ]
        self.wifi_interfaces = [item.split('.')[2] for item in self.real_sta_list]

        # Count OS types
        for os_type in self.real_sta_os_types:
            if os_type == 'windows':
                self.windows += 1
            elif os_type == 'linux':
                self.linux += 1
            elif os_type == 'macos':
                self.mac += 1
        logger.info(f"Selected Real Devices: {self.real_sta_list}")

        return self.real_sta_list

    # Load the credentials on server startup
    def load_credentials(self):
        with open('teams_cred.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.credentials = list(reader)

    def move_csv_files(self):
        for file in os.listdir(self.path):
            if file.endswith(".csv"):
                src = os.path.join(self.path, file)
                dest = os.path.join(self.report_path_date_time, file)
                shutil.move(src, dest)

    def shutdown(self):
        """
        Gracefully shut down the application.
        """
        logging.info("Initiating graceful shutdown...")

        self.stop_signal = True
        time.sleep(10)
        logging.info("Exiting the application.")
        os._exit(0)

    def start_flask_server(self):

        @self.app.route('/check_stop', methods=['GET'])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        @self.app.route('/get_credentials', methods=['GET'])
        def get_credentials():
            if self.cred_index < len(self.credentials):
                row = self.credentials[self.cred_index]
                self.cred_index += 1
                return jsonify({
                    "email": row['email'],
                    "password": row['password']
                })
            else:
                logging.error("Not enough credentials for devices")
                return jsonify({"log": "Not enough credentials for devices"}), 404

        @self.app.route('/test_server', methods=['GET'])
        def test_server_status():
            return jsonify({"status": "Server is running"}), 200

        @self.app.route('/meeting_link', methods=['GET', 'POST'])
        def meeting_link():
            if request.method == 'GET':
                return jsonify({"meet_link": self.meet_link})
            elif request.method == 'POST':
                data = request.json
                self.meet_link = data.get('meet_link', '')
                logger.info(f"Meeting Link Updated: {self.meet_link}")
                return jsonify({"message": "Meeting Link Updated sucessfully"})

        @self.app.route('/login_completed', methods=['POST'])
        def login_completed():
            if request.method == 'POST':
                data = request.json
                login_completed_status = int(data.get('login_completed', 0))
                self.login_completed = bool(login_completed_status)
                return jsonify({"message": f"Updated login_completed status to {bool(login_completed_status)}"})

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

        @self.app.route('/stop_teams', methods=['GET'])
        def stop_teams():
            """
            Endpoint to stop the Zoom test and trigger a graceful application shutdown.
            """
            logging.info("Stopping the test through web UI")
            self.stop_signal = True
            # Respond to the client
            response = jsonify({"message": "Stopping Teams Test"})
            response.status_code = 200
            # Trigger shutdown in a separate thread to avoid blocking
            shutdown_thread = threading.Thread(target=self.shutdown)
            shutdown_thread.start()
            return response

        @self.app.route('/upload_stats', methods=['POST'])
        def upload_stats():
            data = request.json

            for hostname, stats in data.items():
                self.data_store[hostname] = stats

                csv_file = os.path.join(self.path, f'{hostname}.csv')
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)

                    if os.path.getsize(csv_file) == 0:
                        writer.writerow(
                            self.header
                        )
                    timestamp = stats.get('timestamp', '')
                    if self.audio and self.video:
                        audio = stats.get('audio_stats', {})
                        video = stats.get('video_stats', {})
                        row = [
                            timestamp,
                            audio.get("au_sent_bitrate", 0),
                            audio.get("au_sent_pkts", 0),
                            audio.get("au_rtt", 0),
                            audio.get("au_sent_codec", "NA"),
                            audio.get("au_recv_jitter", 0),
                            audio.get("au_recv_pkt_loss", 0),
                            audio.get("au_recv_pkts", 0),
                            audio.get("au_recv_codec", "NA"),
                            video.get("vi_sent_bitrate", 0),
                            video.get("vi_recv_bitrate", 0),
                            video.get("vi_sent_frame_rate", 0),
                            video.get("vi_sent_res", "NA"),
                            video.get("vi_rtt", 0),
                            video.get("vi_sent_pkts", 0),
                            video.get("vi_sent_codec", "NA"),
                            video.get("vi_processing", "NA"),
                        ]
                    elif self.audio:
                        audio = stats.get('audio_stats', {})
                        row = [
                            timestamp,
                            audio.get("au_sent_bitrate", 0),
                            audio.get("au_sent_pkts", 0),
                            audio.get("au_rtt", 0),
                            audio.get("au_sent_codec", "NA"),
                            audio.get("au_recv_jitter", 0),
                            audio.get("au_recv_pkt_loss", 0),
                            audio.get("au_recv_pkts", 0),
                            audio.get("au_recv_codec", "NA"),
                        ]

                    elif self.video:
                        video = stats.get('video_stats', {})
                        row = [
                            timestamp,
                            video.get("vi_sent_bitrate", 0),
                            video.get("vi_recv_bitrate", 0),
                            video.get("vi_sent_frame_rate", 0),
                            video.get("vi_sent_res", "NA"),
                            video.get("vi_rtt", 0),
                            video.get("vi_sent_pkts", 0),
                            video.get("vi_sent_codec", "NA"),
                            video.get("vi_processing", "NA"),
                        ]
                    writer.writerow(row)

            return jsonify({"status": "success"}), 200

        try:
            self.app.run(host='0.0.0.0', port=5005, debug=True, threaded=True, use_reloader=False)
        except Exception as e:
            logging.info(f"Error starting Flask server: {e}")
            sys.exit(0)

    def create_avg_data(self):
        output_file = os.path.join(self.path, "teams_call_avg_data.csv")
        summary_rows = []

        for csv_path in glob.glob(os.path.join(self.path, "*.csv")):
            if csv_path.endswith("teams_cred.csv"):
                continue
            df = pd.read_csv(csv_path)

            device_name = os.path.splitext(os.path.basename(csv_path))[0]
            df = df.drop(columns=["timestamp"], errors="ignore")

            numeric_cols = df.select_dtypes(include="number").columns
            averages = df[numeric_cols].mean().round(2)

            row = averages.to_dict()
            row["Device Name"] = device_name
            summary_rows.append(row)

        summary_df = pd.DataFrame(summary_rows)

        cols = ["Device Name"] + [col for col in summary_df.columns if col != "Device Name"]
        summary_df = summary_df[cols]

        summary_df.to_csv(output_file, index=False)
        logger.info(f"Avg data saved to {output_file}")

    def stop_test_in_webui(self):
        try:
            url = f"http://{self.lanforge_ip}:5454/update_status_yt"
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


def main():
    try:

        parser = argparse.ArgumentParser(
            prog='lf_interop_teams.py',
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=''' Allows user to run the Microsoft Teams Call test on a target resource for the given duration. ''',
            description="""
                NAME: lf_interop_teams.py

                PURPOSE: lf_interop_teams.py provides the available devices and allows the user to start Microsoft Teams call conference meeting for the user-specified duration

                EXAMPLE-1:
                Command Line Interface to run Teams:
                python3 lf_interop_teams.py --mgr 192.168.204.75 --upstream_port 1.1.eth1 --participants 3 --duration 1 --audio --video

                EXAMPLE-2:
                Command Line Interface to run Teams on Specified Resources:
                python3 lf_interop_teams.py --mgr 192.168.204.75 --upstream_port 1.1.eth1 --participants 3 --duration 1 --audio --video --resources 1.95,1.400,1.300


                NOTES:
                1. Use 'python3 lf_interop_teams.py --help' to see command line usage and options.
                2. Always specify the duration in minutes (for example: --duration 3 indicates a duration of 3 minutes).
                3. If --resources are not given after passing the CLI, a list of available devices will be displayed on the terminal.
                4. Enter the resource numbers separated by commas (,) in the resource argument Eg: (1.95,1.200).


        """)

        # Define required arguments group
        required = parser.add_argument_group('Required arguments')
        # Define optional arguments group
        optional = parser.add_argument_group('Optional arguments')

        required.add_argument('--mgr', type=str, help="hostname where LANforge GUI is running", required=True)
        required.add_argument('--duration', type=int, help='duration to run the test in min', required=True)
        required.add_argument('--upstream_port', type=str, help='Specify The Upstream Port name or IP address', required=True)
        required.add_argument('--participants', type=int, help='No of Devices in the test', required=True)

        # Add optional arguments
        optional.add_argument('--resources', help='Specify the real device ports seperated by comma')
        optional.add_argument('--no_pre_cleanup', action="store_true", help='specify this flag to stop cleaning up generic cxs before the test')
        optional.add_argument('--no_post_cleanup', action="store_true", help='specify this flag to stop cleaning up generic cxs after the test')
        optional.add_argument('--log_level', help='Level of the logs to be dispalyed', default='info')
        optional.add_argument('--lf_logger_config_json', help='lf_logger config json')
        optional.add_argument('--audio', action='store_true')
        optional.add_argument('--video', action='store_true')
        optional.add_argument('--do_webUI', action='store_true', help='useful to specify whether we are running through webui or cli')
        optional.add_argument('--testname', help="report directory while running test through web ui")
        optional.add_argument('--report_dir', help="report directory while running test through web ui")

        args = parser.parse_args()

        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        teams = TeamsAutomation(
            lanforge_ip=args.mgr,
            duration=args.duration,
            upstream_port=args.upstream_port,
            no_pre_cleanup=args.no_pre_cleanup,
            no_post_cleanup=args.no_post_cleanup,
            participants_req=args.participants,
            audio=args.audio,
            video=args.video,
            do_webui=args.do_webUI,
            test_name=args.testname,
            report_dir=args.report_dir

        )

        teams.realdevice = RealDevice(manager_ip=args.mgr,
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

        teams.select_real_devices(real_sta_list=args.resources)
        if args.do_webUI:
            teams.path = args.report_dir
            teams.update_webui_data()
        teams.load_credentials()
        teams.run()
        time.sleep(10)
        teams.create_avg_data()
        teams.execute_finally = True

    except Exception as e:
        logging.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
        traceback.print_exc()

    finally:
        if not ('--help' in sys.argv or '-h' in sys.argv):
            if teams.execute_finally:
                teams.stop_signal = True
                teams.generate_report()
                teams.move_csv_files()
                if args.do_webUI:
                    teams.stop_test_in_webui()
                logger.info("Waiting for Browser Cleanup at Client Side")
                time.sleep(10)
                logger.info("Browser Cleanup Completed")
                if not teams.no_post_cleanup:
                    teams.generic_endps_profile.cleanup()
                logger.info("Test Completed")


if __name__ == "__main__":
    main()
