#!/usr/bin/env python3
"""
NAME: lf_interop_zoom.py

PURPOSE: lf_interop_zoom.py provides the available devices and allows the user to start Zoom call conference meeting for the user-specified duration

EXAMPLE-1:
Command Line Interface to run Zoom with specified duration:
python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video --upstream_port 192.168.214.123

EXAMPLE-2:
Command Line Interface to run Zoom on multiple devices:
python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video
  --resources 1.400,1.375 --zoom_host 1.95 --upstream_port 192.168.214.123

Example-3:
Command Line Interface to run Zoom on multiple devices with Device Configuration
python3 lf_interop_zoom.py --duration 1 --lanforge_ip "192.168.204.74" --signin_email "Demo@gmail.com" --signin_passwd "Demo@10203000" --participants 2 --audio --video
--upstream_port 1.1.eth1 --zoom_host 1.95 --resources 1.400,1.360 --ssid NETGEAR_2G_wpa2 --passwd Password@123 --encryp wpa2 --config

Example-4:
Command Line Interface to run Zoom on multiple devices with Groups and Profiles
python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.204.74" --signin_email "Demo@gmail.com" --signin_passwd "Demo@10203000" --participants 2 --audio --video
--wait_time 30  --group_name group1,group2 --profile_name netgear5g,netgear2g --file_name grplaptops.csv --zoom_host 1.95 --upstream_port 1.1.eth1

Example-5:
Command Line Interface to run Zoom test with robo feature
python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video --upstream_port 192.168.214.123 --robo_ip 192.168.200.131 --coordinates 1,2 --rotations 30,40 --do_robo

Example-6:
Command Line Interface to get Mos Score in the report:
python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video
--resources 1.400,1.375 --zoom_host 1.95 --upstream_port 1.1.eth1 --api_stats_collection --env_file .env --download_csv


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
import asyncio
import sys
import traceback
import textwrap
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import re
import glob
from collections import Counter
import signal
import platform
import subprocess

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
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
flask_server_logger = logging.getLogger(__name__)
flask_server_log = logging.getLogger("werkzeug")
flask_server_log.setLevel(logging.ERROR)

# 1. Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("lf_interop_zoom.log", mode="w"),  # Writes to file
        logging.StreamHandler(sys.stdout),  # Writes to terminal
    ],
)

# 2. Create the logger instance
logger = logging.getLogger(__name__)

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

robo_base_class = importlib.import_module("py-scripts.lf_base_robo")


class ZoomAutomation(Realm):
    def __init__(
        self,
        ssid="SSID",
        band="5G",
        security="wpa2",
        apname="AP Name",
        audio=True,
        video=True,
        lanforge_ip=None,
        upstream_port="0.0.0.0",
        wait_time=30,
        devices=None,
        testname=None,
        config=None,
        selected_groups=None,
        selected_profiles=None,
        robo_ip="127.0.0.1",
        coordinates_list=None,
        angles_list=None,
        do_robo=False,
        current_cord="",
        current_angle="",
        rotations_enabled=False,
        signin_email="",
        signin_passwd="",
        duration=None,
        participants_req=None,
        env_file=None,
        do_bs=False,
        api_stats_collection=False,
        do_webui=False,
        cycles=1,
        bssids=None,
        wait_at_point=30,
        resource_ip=None,
    ):

        super().__init__(lfclient_host=lanforge_ip)
        self.upstream_port = upstream_port
        self.mgr_ip = lanforge_ip
        self.app = Flask(__name__)
        self.devices = devices
        self.windows = 0
        self.linux = 0
        self.mac = 0
        self.android = 0
        self.real_sta_os_type = []
        self.real_sta_hostname = []
        self.real_sta_list = []
        self.real_sta_data = {}
        self.password_status = False  # Initially set to False
        self.login_completed = False  # Initially set to False
        self.remote_login_url = ""  # Initialize remote login URL
        self.remote_login_passwd = ""  # Initialize remote login password
        self.signin_email = signin_email
        self.signin_passwd = signin_passwd
        self.test_start = False
        self.start_time = None
        self.end_time = None
        self.participants_joined = 0
        self.participants_req = participants_req
        self.ap_name = apname
        self.ssid = ssid
        self.band = band
        self.security = security
        self.tz = pytz.timezone("Asia/Kolkata")
        self.meet_link = None
        self.zoom_host = None
        self.testname = testname
        self.stop_signal = False
        self.download_csv = False
        self.csv_file_name = "csvdata.csv"
        self.path = os.path.join(os.getcwd(), "zoom_test_results")
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.device_names = []
        self.hostname_os_combination = None

        self.clients_disconnected = False
        self.audio = audio
        self.video = video
        self.wait_time = wait_time
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.name_prefix = "zoom"
        self.generic_endps_profile.type = "zoom"
        self.data_store = {}
        self.header = [
            "timestamp",
            "Sent Audio Frequency (khz)",
            "Sent Audio Latency (ms)",
            "Sent Audio Jitter (ms)",
            "Sent Audio Packet loss (%)",
            "Receive Audio Frequency (khz)",
            "Receive Audio Latency (ms)",
            "Receive Audio Jitter (ms)",
            "Receive Audio Packet loss (%)",
            "Sent Video Latency (ms)",
            "Sent Video Jitter (ms)",
            "Sent Video Packet loss (%)",
            "Sent Video Resolution (khz)",
            "Sent Video Frames ps (khz)",
            "Receive Video Latency (ms)",
            "Receive Video Jitter (ms)",
            "Receive Video Packet loss (%)",
            "Receive Video Resolution (khz)",
            "Receive Video Frames ps (khz)",
        ]
        self.config = config
        self.selected_groups = list(selected_groups or [])
        self.selected_profiles = list(selected_profiles or [])
        self.duration = duration
        # Single container for raw Zoom QoS and summarized report data.
        self.zoom_stats_data = {"raw_qos": [], "summary": {}}
        self.env_file = env_file

        self.do_robo = do_robo
        self.do_bs = do_bs
        if self.do_robo or self.do_bs:
            self.robo_ip = robo_ip
            self.robo_obj = robo_base_class.RobotClass(
                robo_ip=self.robo_ip, angle_list=angles_list
            )
            self.coordinates_list = coordinates_list
            self.angles_list = angles_list
            self.current_cord = current_cord
            self.current_angle = current_angle
            self.rotations_enabled = rotations_enabled
            self.robo_csv_files = []

        self.account_id = None
        self.client_id = None
        self.client_secret = None
        self.api_stats_collection = api_stats_collection
        self.do_webui = do_webui
        self.cycles = cycles
        self.from_cord = None
        self.to_cord = None
        self.bssids = bssids or []
        logger.info("Zoom Automation Initialized with the following parameters:")
        if self.do_bs:
            self.robo_obj.coordinate_list = self.coordinates_list
            self.robo_obj.total_cycles = self.cycles
            logger.info(
                f"User mentioned coordinates list: {self.robo_obj.coordinate_list}"
            )
        self.successful_coords = []
        self.failed_coords = []
        self.is_csv_available = False
        self.wait_at_point = int(wait_at_point)
        self.resource_ip = resource_ip

    def stop_previous_flask_server(self):
        """
        Forcefully kills any process currently listening on port 5000 (Linux/Darwin only).
        """
        port = 5000
        logger.info(
            f"Checking for processes using port {port} to forcefully kill them..."
        )

        current_os = platform.system()

        try:
            if current_os in ["Linux", "Darwin"]:
                # Find PID on Linux/Mac using lsof
                command = f"lsof -t -i:{port}"
                try:
                    output = subprocess.check_output(command, shell=True, text=True)
                    pids = output.strip().split("\n")
                    for pid in pids:
                        if pid.strip():
                            logger.info(
                                f"Killing process {pid} on port {port} ({current_os})..."
                            )
                            os.kill(int(pid.strip()), signal.SIGKILL)
                except subprocess.CalledProcessError:
                    logger.info(f"No process found using port {port} on {current_os}.")
                    logger.info(f"Port {port} is clear, ready to start Flask server.")
                    pass
            else:
                logger.warning(
                    f"Unsupported OS: {current_os}. Expected Linux or Darwin. Cannot automatically clear port {port}."
                )

        except Exception as e:
            logger.warning(f"Error while trying to clear port {port}: {e}")

    def move_ping_logs(self):
        source_dir = os.path.join(self.path, "ping_logs")
        if not os.path.isdir(source_dir):
            logger.info(f"No ping_logs directory found at {source_dir}")
            return

        destination_dir = os.path.join(self.report_path_date_time, "ping_logs")
        os.makedirs(self.report_path_date_time, exist_ok=True)

        # If destination exists, merge files and remove source
        if os.path.exists(destination_dir):
            for file_name in os.listdir(source_dir):
                src_file = os.path.join(source_dir, file_name)
                dst_file = os.path.join(destination_dir, file_name)
                if os.path.isfile(src_file):
                    shutil.move(src_file, dst_file)
            shutil.rmtree(source_dir, ignore_errors=True)
            logger.info(f"Merged ping logs into {destination_dir}")
        else:
            shutil.move(source_dir, destination_dir)
            logger.info(f"Moved ping logs folder to {destination_dir}")

    def handle_flask_server(self):
        self.stop_previous_flask_server()
        time.sleep(5)  # Ensure the port is released before starting the server
        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        self.wait_for_flask()

    def start_flask_server(self):
        @self.app.route("/login_url", methods=["GET", "POST"])
        def login_url():
            if request.method == "GET":
                return jsonify({"login_url": self.remote_login_url})
            elif request.method == "POST":
                data = request.json
                self.remote_login_url = data.get("login_url", "")
                return jsonify(
                    {"message": f"Updated login_url to {self.remote_login_url}"}
                )

        @self.app.route("/login_passwd", methods=["GET", "POST"])
        def login_passwd():
            if request.method == "GET":
                return jsonify({"login_passwd": self.remote_login_passwd})
            elif request.method == "POST":
                data = request.json
                self.remote_login_passwd = data.get("login_passwd", "")
                return jsonify({"message": "Password updated successfully."})

        @self.app.route("/meeting_link", methods=["GET", "POST"])
        def meeting_link():
            if request.method == "GET":
                return jsonify({"meet_link": self.meet_link})
            elif request.method == "POST":
                data = request.json
                self.meet_link = data.get("meet_link", "")
                self.meet_link = self.meet_link.rsplit(".", 1)[0] + ".1"

                logger.info(f"Zoom host Updated Meet link: {self.meet_link}")
                return jsonify({"message": "Meeting Link Updated sucessfully"})

        @self.app.route("/login_completed", methods=["GET"])
        def login_completed():
            if request.method == "GET":
                self.login_completed = True
                return jsonify({"status": "login_completed"}), 200

        @self.app.route("/get_host_email", methods=["GET"])
        def get_host_email():
            return jsonify({"host_email": self.signin_email})

        @self.app.route("/get_host_passwd", methods=["GET"])
        def get_host_passwd():
            return jsonify({"host_passwd": self.signin_passwd})

        @self.app.route("/get_participants_joined", methods=["GET"])
        def get_participants_joined():
            return jsonify({"participants": self.participants_joined})

        @self.app.route("/set_participants_joined", methods=["POST"])
        def set_participants_joined():
            data = request.json
            self.participants_joined = data.get("participants_joined", None)
            return jsonify(
                {
                    "message": f"Updated participants joined status to {self.participants_joined}"
                }
            )

        @self.app.route("/get_participants_req", methods=["GET"])
        def get_participants_req():
            return jsonify({"participants": self.participants_req})

        @self.app.route("/test_started", methods=["GET", "POST"])
        def test_started():
            if request.method == "GET":
                return jsonify({"test_started": self.test_start})
            elif request.method == "POST":
                data = request.json
                self.test_start = data.get("test_started", False)
                return jsonify(
                    {"message": f"Updated test_start status to {self.test_start}"}
                )

        @self.app.route("/clients_disconnected", methods=["POST"])
        def client_disconnected():
            data = request.json
            self.clients_disconnected = data.get("clients_disconnected", False)
            return jsonify(
                {
                    "message": f"Updated clients_disconnected status to {self.clients_disconnected}"
                }
            )

        @self.app.route("/get_start_end_time", methods=["GET"])
        def get_start_end_time():
            return jsonify(
                {
                    "start_time": (
                        self.start_time.isoformat()
                        if self.start_time is not None
                        else None
                    ),
                    "end_time": (
                        self.end_time.isoformat() if self.end_time is not None else None
                    ),
                }
            )

        @self.app.route("/stats_opt", methods=["GET"])
        def stats_to_be_collected():
            return jsonify({"audio_stats": self.audio, "video_stats": self.video})

        @self.app.route("/check_stop", methods=["GET"])
        def check_stop():
            return jsonify({"stop": self.stop_signal})

        @self.app.route("/upload_stats", methods=["POST", "GET"])
        def upload_stats():
            if self.do_robo or self.do_bs or self.api_stats_collection:
                self.get_live_data()
                summary_data = self._get_summary_zoom_stats()
                if summary_data:
                    if self.do_bs:
                        lf_wifi_data = self.get_signal_and_channel_data_dict()
                    for hostname, stats in summary_data.items():
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        stats["timestamp"] = timestamp

                        if self.do_bs:
                            x, y, _, _ = self.robo_obj.get_robot_pose()
                            stats["X"] = x
                            stats["Y"] = y
                            stats["From_Coord"] = self.from_cord
                            stats["To_Coord"] = self.to_cord
                            sta_id = self.hostname_to_station_map.get(
                                hostname, None
                            )

                            if sta_id in lf_wifi_data:
                                stats.update(lf_wifi_data[sta_id])
                            else:
                                stats.update(
                                    {
                                        "signal": "-",
                                        "channel": "-",
                                        "mode": "-",
                                        "tx_rate": "-",
                                        "rx_rate": "-",
                                        "bssid": "-",
                                    }
                                )

                        if self.do_robo or self.do_bs:
                            stats["current_cord"] = self.current_cord
                            if self.rotations_enabled:
                                stats["rotations_enabled"] = self.rotations_enabled
                                stats["current_angle"] = self.current_angle
                            else:
                                stats["rotations_enabled"] = False

                        # --- CSV FILE PATH GENERATION ---
                        if self.do_robo:
                            if self.rotations_enabled:
                                csv_name = f"{hostname}_{self.current_cord}_{self.current_angle}.csv"
                            else:
                                csv_name = f"{hostname}_{self.current_cord}.csv"
                        else:
                            csv_name = f"{hostname}.csv"

                        csv_file = os.path.join(self.path, csv_name)

                        # --- WRITING DATA TO CSV ---
                        file_exists = (
                            os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0
                        )

                        with open(csv_file, mode="a", newline="") as file:
                            headers = list(stats.keys())
                            writer = csv.DictWriter(file, fieldnames=headers)

                            if not file_exists:
                                writer.writeheader()

                            writer.writerow(stats)

                return "Live Data Processed", 200
            else:
                data = request.json
                for hostname, stats in data.items():
                    self.data_store[hostname] = stats
                for hostname, stats in data.items():
                    if self.do_robo:
                        if self.rotations_enabled:
                            csv_file = os.path.join(
                                self.path,
                                f"{hostname}_{self.current_cord}_{self.current_angle}.csv",
                            )
                        else:
                            csv_file = os.path.join(
                                self.path, f"{hostname}_{self.current_cord}.csv"
                            )
                    else:
                        csv_file = os.path.join(self.path, f"{hostname}.csv")
                    with open(csv_file, mode="a", newline="") as file:
                        writer = csv.writer(file)

                        if os.path.getsize(csv_file) == 0:
                            writer.writerow(self.header)

                        timestamp = stats.get("timestamp", "")
                        audio = stats.get("audio_stats", {})
                        video = stats.get("video_stats", {})

                        row = [
                            timestamp,
                            audio.get("frequency_sent", "0"),
                            audio.get("latency_sent", "0"),
                            audio.get("jitter_sent", "0"),
                            audio.get("packet_loss_sent", "0"),
                            audio.get("frequency_received", "0"),
                            audio.get("latency_received", "0"),
                            audio.get("jitter_received", "0"),
                            audio.get("packet_loss_received", "0"),
                            video.get("latency_sent", "0"),
                            video.get("jitter_sent", "0"),
                            video.get("packet_loss_sent", "0"),
                            video.get("resolution_sent", "0"),
                            video.get("frames_per_second_sent", "0"),
                            video.get("latency_received", "0"),
                            video.get("jitter_received", "0"),
                            video.get("packet_loss_received", "0"),
                            video.get("resolution_received", "0"),
                            video.get("frames_per_second_received", "0"),
                        ]
                        writer.writerow(row)

                return jsonify({"status": "success"}), 200

        @self.app.route("/get_latest_stats", methods=["GET"])
        def get_latest_stats():
            # Return the latest data for all hostnames
            return jsonify(self._get_summary_zoom_stats()), 200

        @self.app.route("/stop_zoom", methods=["GET"])
        def stop_zoom():
            """
            Endpoint to stop the Zoom test and trigger a graceful application shutdown.
            """
            logger.info("Stopping the test through web UI")
            self.stop_signal = True  # Signal to stop the application
            # Respond to the client
            response = jsonify({"message": "Stopping Zoom Test"})
            response.status_code = 200
            # Trigger shutdown in a separate thread to avoid blocking
            shutdown_thread = threading.Thread(target=self.shutdown)
            shutdown_thread.start()
            return response

        @self.app.route("/download_csv", methods=["GET"])
        def download_csv_flag():
            return jsonify({"download_csv": self.download_csv})

        @self.app.route("/upload_csv", methods=["POST"])
        def upload_csv_data():
            try:
                data = request.json

                if not data:
                    return (
                        jsonify({"status": "error", "message": "No JSON received"}),
                        400,
                    )

                filename = data.get("filename", "csvdata.csv")
                self.csv_file_name = f"received_{filename}"
                rows = data.get("rows", [])
                if not rows:
                    return (
                        jsonify({"status": "error", "message": "No rows received"}),
                        400,
                    )

                filepath = f"received_{filename}"
                logger.info(
                    f"Data Received from Zoom dashboard is stored at: {filepath}"
                )
                with open(filepath, "w", newline="") as f:
                    writer = csv.writer(f)
                    if rows:
                        writer.writerows(rows)
                self.is_csv_available = True

                return (
                    jsonify(
                        {
                            "status": "success",
                            "message": f"Received {len(rows)} rows from {filename}",
                            "saved_as": filepath,
                        }
                    ),
                    200,
                )

            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        @self.app.route("/upload_ping_log", methods=["POST"])
        def upload_ping_log():
            try:
                if "file" not in request.files:
                    return jsonify({"status": "error", "message": "Missing file"}), 400

                f = request.files["file"]
                participant_name = request.form.get(
                    "participant_name", "unknown_participant"
                )

                if not f.filename:
                    return (
                        jsonify({"status": "error", "message": "Empty filename"}),
                        400,
                    )

                ping_dir = os.path.join(self.path, "ping_logs")
                os.makedirs(ping_dir, exist_ok=True)

                # Force controlled filename format to avoid unsafe names from client
                save_name = f"{participant_name}_ping.log"
                save_path = os.path.join(ping_dir, save_name)
                f.save(save_path)

                return (
                    jsonify(
                        {
                            "status": "success",
                            "message": "Ping log uploaded",
                            "saved_as": save_path,
                        }
                    ),
                    200,
                )
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        try:
            self.app.run(
                host="0.0.0.0", port=5000, debug=True, threaded=True, use_reloader=False
            )
        except Exception as e:
            logger.info(f"Error starting Flask server: {e}")
            sys.exit(0)

    def shutdown(self):
        """
        Gracefully shut down the application.
        """
        if self.do_robo and self.api_stats_collection:
            self.generate_report_from_data()
        elif self.api_stats_collection:
            self.generate_report_from_api()
        self.generic_endps_profile.cleanup()
        logger.info("Initiating graceful shutdown...")
        os._exit(0)

    def set_start_time(self):
        self.start_time = datetime.now(self.tz) + timedelta(seconds=60)
        if self.do_bs:
            self.end_time = self.start_time + timedelta(minutes=300000)
        else:
            self.end_time = self.start_time + timedelta(minutes=self.duration)
        return [self.start_time, self.end_time]

    def check_gen_cx(self):
        try:

            for gen_endp in self.generic_endps_profile.created_endp:
                generic_endpoint = self.json_get(f"/generic/{gen_endp}")

                if not generic_endpoint or "endpoint" not in generic_endpoint:
                    logger.info(f"Error fetching endpoint data for {gen_endp}")
                    return False

                endp_status = generic_endpoint["endpoint"].get("status", "")

                if endp_status not in ["Stopped", "WAITING", "NO-CX"]:
                    return False

            return True
        except Exception as e:
            logger.error(f"Error in check_gen_cx function {e}", exc_info=True)
            logger.info(f"generic endpoint data {generic_endpoint}")

    def wait_for_flask(self, url="http://127.0.0.1:5000/get_latest_stats", timeout=10):
        """Wait until the Flask server is up, but exit if it takes longer than `timeout` seconds."""
        start_time = time.time()  # Record the start time
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

    def create_android(
        self,
        lanforge_res,
        ports=None,
        sleep_time=0.5,
        debug_=False,
        suppress_related_commands_=None,
        real_client_os_types=None,
    ):
        if ports and real_client_os_types and len(real_client_os_types) == 0:
            logger.error("Real client operating systems types is empty list")
            raise ValueError("Real client operating systems types is empty list")
        created_cx = []
        created_endp = []

        if not ports:
            ports = []

        if self.debug:
            debug_ = True

        post_data = []
        endp_tpls = []
        for port_name in ports:
            port_info = self.name_to_eid(port_name)
            resource = port_info[1]
            shelf = port_info[0]
            if real_client_os_types:
                name = port_name
            else:
                name = port_info[2]

            gen_name_a = "%s-%s" % ("zoom", "_".join(port_name.split(".")))
            endp_tpls.append((shelf, resource, name, gen_name_a))

        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            if real_client_os_types:
                name = endp_tpl[2].split(".")[2]
            else:
                name = endp_tpl[2]
            gen_name_a = endp_tpl[3]

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": lanforge_res.split(".")[1],
                "port": "eth0",
                "type": "gen_generic",
            }
            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        if sleep_time:
            time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            gen_name_a = endp_tpl[3]
            self.generic_endps_profile.set_flags(gen_name_a, "ClearPortOnStart", 1)

        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            cx_name = "CX_%s-%s" % ("generic", gen_name_a)
            data = {"alias": cx_name, "test_mgr": "default_tm", "tx_endp": gen_name_a}
            post_data.append(data)
            created_cx.append(cx_name)
            created_endp.append(gen_name_a)

        for data in post_data:
            url = "/cli-json/add_cx"
            self.json_post(
                url,
                data,
                debug_=debug_,
                suppress_related_commands_=suppress_related_commands_,
            )
        if sleep_time:
            time.sleep(sleep_time)

        for data in post_data:
            self.json_post(
                "/cli-json/show_cx",
                {"test_mgr": "default_tm", "cross_connect": data["alias"]},
            )
        return True, created_cx, created_endp

    def get_resource_data(self):
        self.ports_list = []
        self.user_list = []
        self.serial_list = []
        self.lanforge_port_list = []
        self.device_names = []
        self.user_resources = [
            ".".join(item.split(".")[:2]) for item in self.real_sta_list
        ]

        # Step 1: Retrieve information about all resources
        response = self.json_get("/resource/all")

        # Step 2: Match user-specified resources with available resources sequentially
        if self.user_resources:
            resources = response.get("resources", [])
            for user_resource in self.user_resources:
                found = False
                for element in resources:
                    if user_resource in element:
                        resource_values = element[user_resource]
                        eid = resource_values["eid"]
                        resource_ip = resource_values["ctrl-ip"]
                        hostname = resource_values["hostname"]
                        user = resource_values["user"]

                        self.device_names.append(hostname)
                        self.ports_list.append({"eid": eid, "ctrl-ip": resource_ip})
                        self.user_list.append(user)

                        found = True
                        break

                if not found:
                    logger.warning(
                        f"Resource {user_resource} not found in LANforge response"
                    )

    def get_ports_data(self):
        self.gen_ports_list = []
        self.mac_list = []
        self.rssi_list = []
        self.link_rate_list = []
        self.ssid_list = []

        # Step 3: Retrieve port information
        response_port = self.json_get("/port/all")

        # Step 4: Match ports associated with retrieved resources in the order of ports_list
        for port_entry in self.ports_list:
            # Extract the eid and ctrl-ip from the current ports_list entry
            expected_eid = port_entry["eid"]

            # Iterate over the port interfaces to find a matching port
            for interface in response_port["interfaces"]:
                for port, port_data in interface.items():
                    # Extract the first two segments of the port identifier to match with expected_eid
                    result = ".".join(port.split(".")[:2])

                    # Check if the result matches the current expected eid from ports_list
                    if result == expected_eid:
                        self.gen_ports_list.append(port.split(".")[-1])
                        break
                else:
                    continue
                break

        for port_entry in self.ports_list:
            # Extract the eid and ctrl-ip from the current ports_list entry
            expected_eid = port_entry["eid"]

            # Iterate over the port interfaces to find a matching port
            for interface in response_port["interfaces"]:
                for port, port_data in interface.items():
                    # Extract the first two segments of the port identifier to match with expected_eid
                    result = ".".join(port.split(".")[:2])

                    # Check if the result matches the current expected eid from ports_list
                    if result == expected_eid and port_data["parent dev"] == "wiphy0":
                        self.mac_list.append(port_data["mac"])
                        self.rssi_list.append(port_data["signal"])
                        self.link_rate_list.append(port_data["rx-rate"])
                        self.ssid_list.append(port_data["ssid"])

                        break
                else:
                    continue
                break
        self.wifi_interface_list = [item.split(".")[2] for item in self.real_sta_list]

    def get_interop_data(self):
        interop_data = self.json_get("/adb")
        interop_mobile_data = interop_data.get("devices", {})
        self.serial_list = []
        self.lanforge_port_list = []
        for user in self.user_list:
            if user == "":
                self.serial_list.append("")
                self.lanforge_port_list.append("")
            else:
                user_found = False
                # 1. Handle Single Device (Flat Dictionary)
                if isinstance(interop_mobile_data, dict):
                    if interop_mobile_data.get("user-name") == user:
                        # Extract details from 'name' (e.g., '1.1.3200f8664a91a5e9')
                        full_name = interop_mobile_data.get("name")
                        if full_name and full_name.count(".") >= 2:
                            resource = full_name.split(".")[1]
                            serial_no = full_name.split(".")[2]
                            self.serial_list.append(serial_no)
                            self.lanforge_port_list.append(f"1.{resource}.eth0")
                            user_found = True
                else:
                    for mobile_device in interop_mobile_data:
                        for serial, device_data in mobile_device.items():
                            if device_data.get("user-name") == user:
                                resource = serial.split(".")[1]
                                serial_no = serial.split(".")[2]
                                self.serial_list.append(serial_no)
                                lanforge_port = f"1.{resource}.eth0"
                                self.lanforge_port_list.append(lanforge_port)
                                user_found = True
                                break
                        if user_found:
                            break

                if not user_found:
                    self.serial_list.append("")
                    self.lanforge_port_list.append("")

        logger.debug(f"Checking serial list {self.serial_list}")

    def delete_current_csv_files(self):
        filename_pattern = (
            f"*_{self.current_cord}_{self.current_angle}.csv"
            if self.rotations_enabled
            else f"*_{self.current_cord}.csv"
        )
        csv_files_pattern = os.path.join(self.path, filename_pattern)
        csv_files = glob.glob(csv_files_pattern)

        for file_path in csv_files:
            try:
                os.remove(file_path)
                logger.info(f"Deleted CSV file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")

    def create_host(self):
        if self.generic_endps_profile.create(
            ports=[self.real_sta_list[0]],
            real_client_os_types=[self.real_sta_os_type[0]],
        ):
            logger.info("Real client generic endpoint creation completed.")
        else:
            logger.error("Real client generic endpoint creation failed.")
            exit(0)

        if self.real_sta_os_type[0] == "windows":
            cmd = f"py zoom_host.py --ip {self.upstream_port}"
            self.generic_endps_profile.set_cmd(
                self.generic_endps_profile.created_endp[0], cmd
            )
        elif self.real_sta_os_type[0] == "linux":
            cmd = "su -l lanforge ctzoom.bash %s %s %s" % (
                self.wifi_interface_list[0],
                self.upstream_port,
                "host",
            )
            self.generic_endps_profile.set_cmd(
                self.generic_endps_profile.created_endp[0], cmd
            )
        elif self.real_sta_os_type[0] == "macos":
            cmd = "sudo bash ctzoom.bash %s %s" % (self.upstream_port, "host")
            self.generic_endps_profile.set_cmd(
                self.generic_endps_profile.created_endp[0], cmd
            )
        self.generic_endps_profile.start_cx()
        time.sleep(5)

        logger.debug(f"checking real sta list {self.real_sta_list}")
        logger.debug(f"checking real sta os type {self.real_sta_os_type}")

    def wait_for_host_ready(self):
        while not self.login_completed:
            try:
                generic_endpoint = self.json_get(
                    f"/generic/{self.generic_endps_profile.created_endp[0]}"
                )
                endp_status = generic_endpoint["endpoint"]["status"]
                if endp_status == "Stopped":
                    logger.error("Failed to Start the Host Device")
                    self.generic_endps_profile.cleanup()
                    sys.exit(1)
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error while checking login_completed status: {e}")
                time.sleep(5)

        self.meet_link = f"https://us04web.zoom.us/j/{self.remote_login_url}?pwd={self.remote_login_passwd}"
        logger.info(f"Meet link for android devices: {self.meet_link}")

        # Save meet link in a text file under self.path
        try:
            meet_link_file = os.path.join(self.path, "meet_link.txt")
            with open(meet_link_file, "w") as f:
                f.write(self.meet_link + "\n")
            logger.info(f"Meet link saved to: {meet_link_file}")
        except Exception as e:
            logger.error(f"Failed to save meet link file: {e}")

        self.login_completed = False

    def create_participants(self):
        for i in range(1, len(self.real_sta_os_type)):
            if self.real_sta_os_type[i] == "android":
                status, created_cx, created_endp = self.create_android(
                    lanforge_res=self.lanforge_port_list[i],
                    ports=[self.real_sta_list[i]],
                    real_client_os_types=["Linux"],
                )
                self.generic_endps_profile.created_endp.extend(created_endp)
                self.generic_endps_profile.created_cx.extend(created_cx)
                cmd = (
                    f"python3 /home/lanforge/lanforge-scripts/py-scripts/real_application_tests/zoom_automation/android_zoom.py "
                    f"--serial {self.serial_list[i]} "
                    f"--meeting_url '{self.meet_link}' "
                    f"--participant_name '{self.real_sta_hostname[i]}' "
                    f"--server_host {self.mgr_ip} "
                    f"--server_port 5000"
                )
                self.generic_endps_profile.set_cmd(
                    self.generic_endps_profile.created_endp[i], cmd
                )

            else:
                self.generic_endps_profile.create(
                    ports=[self.real_sta_list[i]],
                    real_client_os_types=[self.real_sta_os_type[i]],
                )

        for i in range(1, len(self.real_sta_os_type)):
            if self.real_sta_os_type[i] == "windows":
                cmd = f"py zoom_client.py --ip {self.upstream_port}"
                self.generic_endps_profile.set_cmd(
                    self.generic_endps_profile.created_endp[i], cmd
                )
            elif self.real_sta_os_type[i] == "linux":
                cmd = "su -l lanforge ctzoom.bash %s %s %s" % (
                    self.wifi_interface_list[i],
                    self.upstream_port,
                    "client",
                )
                self.generic_endps_profile.set_cmd(
                    self.generic_endps_profile.created_endp[i], cmd
                )
            elif self.real_sta_os_type[i] == "macos":
                cmd = "sudo bash ctzoom.bash %s %s" % (self.upstream_port, "client")
                self.generic_endps_profile.set_cmd(
                    self.generic_endps_profile.created_endp[i], cmd
                )

            cx_name = self.generic_endps_profile.created_cx[i]
            self.json_post(
                "/cli-json/set_cx_state",
                {"test_mgr": "default_tm", "cx_name": cx_name, "cx_state": "RUNNING"},
                debug_=True,
            )
            logger.info(f"Sending running state to.. {cx_name}")

    def wait_for_test_start(self):
        # Wait for the test to be started
        count = 0
        while not self.test_start:
            logger.info("WAITING FOR THE TEST TO BE STARTED")
            time.sleep(5)
            count += 1
            if count > 36:
                logger.error(
                    "Unable to get the Test Start signal Even after 3 minutes. Exiting."
                )
                sys.exit(1)
        self.test_start = False
        if self.do_bs:
            self.bs_coord_result = self.robo_obj.get_coordinates_list()
            logger.info(f"Total Coordinates to be Visited: {self.bs_coord_result}")
            if self.bs_coord_result:
                self.from_cord = self.coordinates_list[0]
                self.successful_coords.append(self.from_cord)
                self.current_cord = self.from_cord
        self.set_start_time()
        logger.info("TEST WILL BE STARTING")

    def run(self):
        self.create_host()
        self.wait_for_host_ready()
        self.create_participants()
        self.wait_for_test_start()

        if self.do_bs:
            time.sleep(60)

            try:
                logger.info(
                    f"Band-Steering Test coordinates to be visited: {self.bs_coord_result}"
                )

                if not self.bs_coord_result:
                    logger.error(
                        "No coordinates available (bs_coord_result is empty). Skipping BS test."
                    )
                    self.stop_signal = True
                    return

                for idx, coordinate in enumerate(self.bs_coord_result):
                    logger.info(f"Moving robot to coordinate: {coordinate}")
                    self.from_cord = self.to_cord
                    self.to_cord = coordinate

                    # Battery safety
                    self.robo_obj.wait_for_battery()

                    matched, aborted = self.robo_obj.move_to_coordinate(
                        coord=coordinate
                    )
                    if matched:
                        self.current_cord = coordinate
                        self.successful_coords.append(coordinate)
                    else:
                        self.failed_coords.append(coordinate)
                    if aborted:
                        logger.error(f"Failed to reach the {coordinate}")
                        self.failed_coords.append(coordinate)
                        sys.exit()

                logger.info(
                    "All coordinates completed — stopping Band-Steering Test"
                )
                self.stop_signal = True
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error during band-steering operation: {e}", exc_info=True)

            finally:
                count = 0
                if self.download_csv:
                    while not self.is_csv_available:
                        count += 1
                        if count > 60:
                            logger.warning(
                                "CSV data from Zoom dashboard is not available after waiting for 5 minutes. Proceeding with report generation without CSV data."
                            )
                            break
                        logger.info(
                            "Waiting for CSV data from Zoom dashboard to be available before proceeding with the Report generation and cleanup"
                        )
                        time.sleep(5)

        else:
            while datetime.now(self.tz) < self.end_time or not self.check_gen_cx():
                if self.do_robo:
                    pause, _ = self.robo_obj.wait_for_battery()
                    if pause:
                        self.stop_signal = True
                        self.generic_endps_profile.stop_cx()
                        self.generic_endps_profile.cleanup()
                        self.delete_current_csv_files()
                        self.start_time = None
                        self.end_time = None
                        time.sleep(20)
                        self.stop_signal = False
                        self.participants_joined = 0
                        self.create_host()
                        self.wait_for_host_ready()
                        self.create_participants()
                        self.wait_for_test_start()
                logger.info("Monitoring the Test")
                time.sleep(5)
        if self.do_robo:
            self.generic_endps_profile.stop_cx()
            self.generic_endps_profile.cleanup()
            self.start_time = None
            self.end_time = None

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

            for (
                device
            ) in (
                real_sta_list
            ):  # Iterate over devices in `real_sta_list` to preserve order
                device_found = False
                for interface_dict in interfaces:  # Iterate through `interfaces`
                    for (
                        key,
                        value,
                    ) in (
                        interface_dict.items()
                    ):  # Iterate through items of each interface dictionary
                        # Check conditions for adding the device
                        key_parts = key.split(".")
                        extracted_key = ".".join(key_parts[:2])
                        if (
                            extracted_key == device
                            and not value["phantom"]
                            and not value["down"]
                            and value["parent dev"] != ""
                        ):
                            final_device_list.append(
                                key
                            )  # Add to final_device_list in order
                            device_found = True
                            break  # Stop after finding the first match for the current device to maintain order
                    if device_found:
                        break

            self.real_sta_list = final_device_list

        # Log an error and exit if no real stations are selected for testing
        if len(self.real_sta_list) == 0:
            logger.error("There are no real devices in this testbed. Aborting test")
            exit(0)
        # Filter out iOS devices from the real_sta_list before proceeding
        self.real_sta_list = self.filter_ios_devices(self.real_sta_list)

        # Rebuild a clean, ordered and unique station list (avoid mutating while iterating)
        self.real_sta_data = {}
        cleaned_sta_list = []
        seen_sta = set()

        for sta_name in self.real_sta_list:
            if sta_name in seen_sta:
                continue
            if sta_name not in real_device_obj.devices_data:
                logger.error(
                    "Real station not in devices data, ignoring it from testing"
                )
                continue

            seen_sta.add(sta_name)
            cleaned_sta_list.append(sta_name)
            self.real_sta_data[sta_name] = real_device_obj.devices_data[sta_name]

        self.real_sta_list = cleaned_sta_list
        self.real_sta_os_type = [
            self.real_sta_data[real_sta_name]["ostype"]
            for real_sta_name in self.real_sta_data
        ]
        self.real_sta_hostname = [
            (
                self.real_sta_data[real_sta_name]["hostname"]
                if self.real_sta_data[real_sta_name]["ostype"] != "android"
                else self.real_sta_data[real_sta_name]["user"]
            )
            for real_sta_name in self.real_sta_data
        ]

        self.zoom_host = self.real_sta_list[0]
        self.hostname_os_combination = [
            f"{hostname} ({os_type})"
            for hostname, os_type in zip(self.real_sta_hostname, self.real_sta_os_type)
        ]

        for key, value in self.real_sta_data.items():
            if value["ostype"] == "windows":
                self.windows = self.windows + 1
            elif value["ostype"] == "macos":
                self.mac = self.mac + 1
            elif value["ostype"] == "linux":
                self.linux = self.linux + 1
            elif value["ostype"] == "android":
                self.android = self.android + 1

        # Create mapping: { 'Hostname': 'Station_ID' }
        self.hostname_to_station_map = dict(
            zip(self.real_sta_hostname, self.real_sta_list)
        )

        # Return the sorted list of selected real station names
        return self.real_sta_list

    def get_signal_and_channel_data_dict(self):
        """
        Returns a dictionary of LANforge stats keyed by station name.
        Example: {'sta001': {'lf_signal': -55, 'lf_channel': 36, ...}}
        """
        lf_stats_map = {}
        interfaces_dict = dict()

        try:
            # Get raw data from LANforge API
            port_data = self.json_get("/ports/all/")["interfaces"]
            for port in port_data:
                interfaces_dict.update(port)
        except Exception as e:
            logger.error(f"Error fetching port data: {e}")
            return {}

        # Loop through your managed stations (e.g., sta001, sta002)
        for sta in self.real_sta_list:
            # Default values if station is missing
            lf_stats_map[sta] = {
                "signal": "-",
                "channel": "-",
                "mode": "-",
                "tx_rate": "-",
                "rx_rate": "-",
                "bssid": "-",
            }

            if sta in interfaces_dict:
                data = interfaces_dict[sta]

                # --- Signal Parsing ---
                sig = data.get("signal", "-")
                if "dBm" in str(sig):
                    lf_stats_map[sta]["signal"] = sig.split(" ")[0]
                else:
                    lf_stats_map[sta]["signal"] = sig

                # --- Other Fields ---
                lf_stats_map[sta]["channel"] = data.get("channel", "-")
                lf_stats_map[sta]["mode"] = data.get("mode", "-")
                lf_stats_map[sta]["tx_rate"] = data.get("tx-rate", "-")
                lf_stats_map[sta]["rx_rate"] = data.get("rx-rate", "-")
                lf_stats_map[sta]["bssid"] = data.get(
                    "ap", "-"
                )  # 'ap' is usually BSSID

        return lf_stats_map

    def get_access_token(self, account_id, client_id, client_secret):
        token_url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
        response = requests.post(
            token_url, auth=HTTPBasicAuth(client_id, client_secret)
        )
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            return access_token
        else:
            raise Exception(
                f"Failed to get access token: {response.status_code} {response.text}"
            )

    def get_participants_qos(self, meeting_id, access_token, test_type="past"):
        url = f"https://api.zoom.us/v2/metrics/meetings/{meeting_id}/participants/qos"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"type": test_type}
        all_participants = []
        next_page_token = None

        try:
            while True:
                if next_page_token:
                    params["next_page_token"] = next_page_token

                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    participants = data.get("participants", [])
                    all_participants.extend(participants)
                    next_page_token = data.get("next_page_token")
                    if not next_page_token:
                        break
                else:
                    raise Exception(
                        f"Failed to get participants QoS: {response.status_code} {response.text}"
                    )
        except Exception as e:
            cached_qos = self._get_raw_zoom_stats()
            if cached_qos:
                logger.warning(
                    f"Failed to get participants QoS for {test_type}. Using last cached participant QoS data: {e}"
                )
                return cached_qos
            raise

        if all_participants:
            return self._set_raw_zoom_stats(all_participants)

        cached_qos = self._get_raw_zoom_stats()
        if cached_qos:
            logger.warning(
                f"Zoom API returned no participant QoS data for {test_type}. Using last cached participant QoS data."
            )
            return cached_qos

        logger.warning(
            f"Zoom API returned no participant QoS data for {test_type} and no cached data is available."
        )
        return []

    def save_json(self, data, filename):
        os.makedirs("zoom_api_responses", exist_ok=True)
        path = os.path.join("zoom_api_responses", filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def get_live_data(self):
        try:
            # retrieving with past meetings
            token = self.get_access_token(
                self.account_id, self.client_id, self.client_secret
            )
            self._set_raw_zoom_stats(
                self.get_participants_qos(self.remote_login_url, token, "live")
            )
            self.summarize_audio_video(self._get_raw_zoom_stats())

        except Exception as e:
            logger.info(
                f"Unable to fetch live meeting data...retrying in 5 seconds {e}"
            )

    def get_final_qos_data(self):
        # 1. Check Credentials (using instance variables)
        if not all([self.account_id, self.client_id, self.client_secret]):
            logger.error("Exiting test due to missing credentials.")
            raise ValueError(
                "Missing Zoom credentials (self.account_id, self.client_id, self.client_secret)"
            )

        meeting_id = self.remote_login_url
        logger.info(f"Meeting ID: {meeting_id}")

        # 2. Get Token & Wait for Data Indexing
        token = self.get_access_token(
            self.account_id, self.client_id, self.client_secret
        )

        # Zoom QoS data is typically available ~20 seconds after meeting end.
        # We wait 150 seconds to be safe and simplify the logic.
        wait_time = 150
        logger.info(
            f"Waiting {wait_time} seconds for Zoom servers to index past meeting QoS data..."
        )
        time.sleep(wait_time)

        # 3. Fetch Data (Try 'Past' first, fallback to 'Live')
        try:
            logger.info("Attempting to fetch 'past' meeting data...")
            past_qos_data = self.get_participants_qos(meeting_id, token, "past")

            # If past data is empty, raise error to trigger fallback
            if not past_qos_data:
                raise ValueError("Zoom API returned empty data for past meeting.")

        except Exception as e:
            logger.warning(
                f"Could not fetch 'past' data ({e}). Falling back to 'live' meeting data..."
            )
            try:
                self.get_participants_qos(meeting_id, token, "live")
            except Exception as e_live:
                logger.error(f"Failed to fetch both past and live data: {e_live}")

        # 4. Summarize and Save JSON
        raw_qos_data = self._get_raw_zoom_stats()
        summary_data = self.summarize_audio_video(raw_qos_data)

        # Construct JSON filename
        if self.do_robo:
            json_name = (
                f"{meeting_id}_{self.current_cord}_{self.current_angle}_qos.json"
            )
        else:
            json_name = f"{meeting_id}_qos.json"

        self.save_json(raw_qos_data, json_name)

        # 5. Write to CSV (Integrated Logic)
        if self.do_robo or self.do_bs or self.api_stats_collection:
            if summary_data:
                logger.info("Writing final QoS data to CSV...")

                # Fetch Wifi Data if needed
                lf_wifi_data = {}
                if self.do_bs:
                    try:
                        lf_wifi_data = self.get_signal_and_channel_data_dict()
                    except Exception as e:
                        logger.warning(f"Could not fetch WiFi data for CSV: {e}")

                for hostname, stats in summary_data.items():
                    final_filename = hostname
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    stats["timestamp"] = timestamp

                    # Add Robot/BS specific data
                    if self.do_bs:
                        x, y, _, _ = self.robo_obj.get_robot_pose()
                        stats["X"] = x
                        stats["Y"] = y
                        stats["From_Coord"] = self.from_cord
                        stats["To_Coord"] = self.to_cord

                        sta_id = self.hostname_to_station_map.get(final_filename, None)
                        if sta_id in lf_wifi_data:
                            stats.update(lf_wifi_data[sta_id])
                        else:
                            stats.update(
                                {
                                    "signal": "-",
                                    "channel": "-",
                                    "mode": "-",
                                    "tx_rate": "-",
                                    "rx_rate": "-",
                                    "bssid": "-",
                                }
                            )

                    # Add Coordinate/Angle data
                    if self.do_robo or self.do_bs:
                        stats["current_cord"] = self.current_cord
                        if self.rotations_enabled:
                            stats["rotations_enabled"] = self.rotations_enabled
                            stats["current_angle"] = self.current_angle
                        else:
                            stats["rotations_enabled"] = False

                    # Generate CSV Filename
                    if self.do_robo:
                        if self.rotations_enabled:
                            csv_name = f"{final_filename}_{self.current_cord}_{self.current_angle}.csv"
                        else:
                            csv_name = f"{final_filename}_{self.current_cord}.csv"
                    else:
                        csv_name = f"{final_filename}.csv"

                    csv_file = os.path.join(self.path, csv_name)

                    # Write to File
                    try:
                        file_exists = (
                            os.path.isfile(csv_file) and os.path.getsize(csv_file) > 0
                        )

                        with open(csv_file, mode="a", newline="") as file:
                            headers = list(stats.keys())
                            writer = csv.DictWriter(file, fieldnames=headers)

                            if not file_exists:
                                writer.writeheader()

                            writer.writerow(stats)
                    except Exception as e:
                        logger.error(f"Failed to write CSV for {hostname}: {e}")

    def parse_value(self, value):
        """Convert Zoom string values to float. Handles kbps, ms, and %."""
        if not value or value in ["-", ""]:
            return None
        try:
            return float(value.split()[0].replace("%", ""))
        except Exception as e:
            logger.error(f"Error parsing value '{value}': {e}")
            return None

    def parse_zoom_value(self, value):
        """
        Convert Zoom string metrics into a float.
        Handles cases like:
        - "123 kbps"
        - "21 ms"
        - "5.6 %"
        - "21 ms/40 ms"
        - "Good(4.41)"
        - "-" or empty values
        """
        if not value or str(value).strip() in ["-", ""]:
            return None

        value = str(value).strip()

        # Handle formats like "Good(4.41)"
        if re.match(r"^[A-Za-z]+\([\d.]+\)$", value):
            return value

        # Handle "21 ms/40 ms" (avg/max -> take avg only)
        if "/" in value:
            avg_part = value.split("/", 1)[0].strip()

            # Missing avg like "-/3.9 %" should not use max
            if avg_part in ["", "-"]:
                return None

            nums = re.findall(r"[\d.]+", avg_part)
            return float(nums[0]) if nums else None

        # General case: "123 kbps", "45 ms", "6.7 %"
        try:
            return float(value.split()[0].replace("%", ""))
        except Exception:
            return None

    def _clean_zoom_participant_name(self, participant_name):
        if participant_name is None:
            return None

        return str(participant_name).replace("(Guest)", "").strip()

    def _get_raw_zoom_stats(self):
        raw_qos = self.zoom_stats_data.get("raw_qos", [])
        return raw_qos if isinstance(raw_qos, list) else []

    def _set_raw_zoom_stats(self, raw_qos):
        self.zoom_stats_data["raw_qos"] = list(raw_qos) if raw_qos else []
        return self.zoom_stats_data["raw_qos"]

    def _get_summary_zoom_stats(self):
        summary = self.zoom_stats_data.get("summary", {})
        return summary if isinstance(summary, dict) else {}

    def _set_summary_zoom_stats(self, summary):
        self.zoom_stats_data["summary"] = summary if isinstance(summary, dict) else {}
        return self.zoom_stats_data["summary"]

    def _get_report_device_data(self, source_data=None):
        if source_data is not None:
            if isinstance(source_data, dict):
                return source_data
            if isinstance(source_data, list):
                return self.summarize_audio_video(source_data) if source_data else {}
            return {}

        summary_data = self._get_summary_zoom_stats()
        if summary_data:
            return summary_data

        raw_qos_data = self._get_raw_zoom_stats()
        if raw_qos_data:
            return self.summarize_audio_video(raw_qos_data)

        return {}

    def _match_summary_data_to_hostnames(self, summary, host_key=None):
        if not summary or not self.real_sta_hostname:
            return summary

        normalized_summary = {}
        used_source_keys = set()
        target_host_key = self.real_sta_hostname[0]

        if host_key in summary:
            host_stats = dict(summary[host_key])
            host_stats["is_host"] = True
            normalized_summary[target_host_key] = host_stats
            used_source_keys.add(host_key)

        remaining_source_keys = [
            key for key in summary.keys() if key not in used_source_keys
        ]
        remaining_target_keys = [
            hostname
            for hostname in self.real_sta_hostname
            if hostname not in normalized_summary
        ]

        for hostname in list(remaining_target_keys):
            cleaned_hostname = self._clean_zoom_participant_name(hostname)
            matched_source_key = next(
                (
                    source_key
                    for source_key in remaining_source_keys
                    if self._clean_zoom_participant_name(source_key)
                    and cleaned_hostname
                    and self._clean_zoom_participant_name(source_key)
                    == cleaned_hostname
                ),
                None,
            )
            if matched_source_key is None:
                continue

            normalized_summary[hostname] = dict(summary[matched_source_key])
            used_source_keys.add(matched_source_key)
            remaining_source_keys.remove(matched_source_key)

        for source_key, stats in summary.items():
            if source_key not in used_source_keys:
                normalized_summary[source_key] = dict(stats)
        self._set_summary_zoom_stats(normalized_summary)
        if self.do_robo:
            self.save_json(
                self._get_summary_zoom_stats(),
                f"{self.remote_login_url}_{self.current_cord}_{self.current_angle}_qos.json",
            )
            self.save_json(
                self._get_raw_zoom_stats(),
                f"{self.remote_login_url}_{self.current_cord}_{self.current_angle}_raw_qos.json",
            )
        else:
            self.save_json(
                self._get_summary_zoom_stats(), f"{self.remote_login_url}_qos.json"
            )
            self.save_json(
                self._get_raw_zoom_stats(), f"{self.remote_login_url}_raw_qos.json"
            )
        return normalized_summary

    def summarize_csv_audio_video(self, csv_path):
        # Step 1: Find the correct header line
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        meeting_summary = pd.read_csv(csv_path, nrows=1, encoding="utf-8-sig")
        csv_host_name = None
        if not meeting_summary.empty and "Host" in meeting_summary.columns:
            host_value = meeting_summary.iloc[0].get("Host")
            if pd.notna(host_value):
                csv_host_name = self._clean_zoom_participant_name(host_value)

        # Step 2: Find the line index where real participant data header starts
        header_line_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("Participant,"):
                header_line_idx = i
                break

        if header_line_idx is None:
            raise ValueError(
                "Could not find the participant metrics section in the CSV."
            )

        # Step 3: Read only the participant section
        df = pd.read_csv(csv_path, skiprows=header_line_idx, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()

        # Mapping from JSON-style keys to CSV columns
        metric_map = {
            # Audio
            "audio_output_bitrate_avg": "Audio (Sending) Bitrate",
            "audio_input_bitrate_avg": "Audio (Receiving) Bitrate",
            "audio_output_latency_avg": "Audio (Sending) Latency-Avg/Max",
            "audio_input_latency_avg": "Audio (Receiving) Latency-Avg/Max",
            "audio_output_jitter_avg": "Audio (Sending) Jitter-Avg/Max",
            "audio_input_jitter_avg": "Audio (Receiving) Jitter-Avg/Max",
            "audio_output_avg_loss_avg": "Audio (Sending) Packet Loss-Avg/Max",
            "audio_input_avg_loss_avg": "Audio (Receiving) Packet Loss-Avg/Max",
            "audio_mos_avg": "Audio Quality",
            # Video
            "video_output_bitrate_avg": "Video (Sending) Bitrate",
            "video_input_bitrate_avg": "Video (Receiving) Bitrate",
            "video_output_latency_avg": "Video (Sending) Latency-Avg/Max",
            "video_input_latency_avg": "Video (Receiving) Latency-Avg/Max",
            "video_output_jitter_avg": "Video (Sending) Jitter-Avg/Max",
            "video_input_jitter_avg": "Video (Receiving) Jitter-Avg/Max",
            "video_output_avg_loss_avg": "Video (Sending) Packet Loss-Avg/Max",
            "video_input_avg_loss_avg": "Video (Receiving) Packet Loss-Avg/Max",
            "video_output_frame_rate_avg": "Video (Sending) Frame Rate",
            "video_input_frame_rate_avg": "Video (Receiving) Frame Rate",
            "video_mos_avg": "Video Quality",
        }

        summary = {}
        host_device_key = None

        for index, row in df.iterrows():
            participant_value = row.get("Participant")
            if pd.isna(participant_value):
                continue

            device = self._clean_zoom_participant_name(participant_value)
            if not device:
                continue

            summary[device] = {key: None for key in metric_map}
            summary[device]["is_host"] = False

            for metric_key, csv_column in metric_map.items():
                raw_value = row.get(csv_column)
                parsed_value = self.parse_zoom_value(raw_value)
                if isinstance(parsed_value, float):
                    summary[device][metric_key] = round(parsed_value, 2)
                else:
                    summary[device][metric_key] = parsed_value

            if (
                csv_host_name
                and self._clean_zoom_participant_name(device)
                and self._clean_zoom_participant_name(device) == csv_host_name
            ):
                summary[device]["is_host"] = True
                host_device_key = device
            elif index == 0 and host_device_key is None:
                host_device_key = device

        if not summary:
            return summary

        if host_device_key not in summary:
            host_device_key = next(iter(summary))

        summary[host_device_key]["is_host"] = True
        return self._match_summary_data_to_hostnames(summary, host_device_key)

    def summarize_audio_video(self, json_data):
        """
        Summarize per-device audio and video stats: avg/max of bitrate, jitter, latency, packet loss.

        Args:
            json_data (list): Zoom JSON as list of participants.

        Returns:
            dict: {device_name: {metric_field_avg/max: value, ...}}
        """
        if not json_data:
            summary_data = self._get_summary_zoom_stats()
            return summary_data if summary_data else {}

        metrics = ["audio_input", "audio_output", "video_input", "video_output"]
        fields = ["bitrate", "latency", "jitter", "avg_loss", "frame_rate"]

        summary = {}
        count = 0
        host_device_key = None
        for index, participant in enumerate(json_data):
            participant_name = participant.get(
                "user_name"
            ) or "Unknown Device {count}".format(count=count + 1)
            device = self._clean_zoom_participant_name(participant_name)
            if device not in summary:
                summary[device] = {
                    f"{m}_{f}_avg": None for m in metrics for f in fields
                }
                summary[device].update(
                    {"is_host": participant.get("is_original_host", False)}
                )
                if participant.get("is_original_host", False):
                    host_device_key = device

            temp_values = {m: {f: [] for f in fields} for m in metrics}

            for sample in participant.get("user_qos", []):
                for m in metrics:
                    data = sample.get(m, {})
                    for f in fields:
                        val = self.parse_value(data.get(f))
                        if val is not None:
                            temp_values[m][f].append(val)

            # calculate avg and max
            for m in metrics:
                for f in fields:
                    vals = temp_values[m][f]
                    if vals:
                        summary[device][f"{m}_{f}_avg"] = round(
                            sum(vals) / len(vals), 2
                        )

        if summary and host_device_key not in summary:
            host_device_key = next(iter(summary))
            summary[host_device_key]["is_host"] = True

        return self._match_summary_data_to_hostnames(summary, host_device_key)

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
                if not os.path.exists(file_path):
                    logging.warning(f"File not found: {file_path}, skipping...")
                    continue

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
                logging.error(f"Error in reading data in client {self.device_names[i]} {e}")
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
            audio_test_results_dict = {
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
            }
            # If both groups and profiles are selected, generate separate audio results tables per group; otherwise show a single combined results table.
            if self.selected_groups and self.selected_profiles:
                for group in self.selected_groups:
                    group_specific_audio_test_results = self.get_test_results_data(audio_test_results_dict, group)
                    if not group_specific_audio_test_results['Device Name']:
                        continue
                    report.set_table_title(f"{group} Test Audio Results:")
                    report.build_table_title()
                    test_results_df = pd.DataFrame(group_specific_audio_test_results)
                    report.set_table_dataframe(test_results_df)
                    report.html += report.dataframe.to_html(index=False, justify='center', render_links=True, escape=False)

            else:
                report.set_table_title("Test Audio Results:")
                report.build_table_title()
                audio_test_details = pd.DataFrame(audio_test_results_dict)
                report.set_table_dataframe(audio_test_details)
                report.html += report.dataframe.to_html(index=False,
                                                        justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
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
            video_test_results_dict = {
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
            }
            # If both groups and profiles are selected, generate separate video results tables per group; otherwise show a single combined results table.
            if self.selected_groups and self.selected_profiles:
                for group in self.selected_groups:
                    group_specific_video_test_results = self.get_test_results_data(video_test_results_dict, group)
                    if not group_specific_video_test_results['Device Name']:
                        continue
                    report.set_table_title(f"{group} Test Video Results:")
                    report.build_table_title()
                    test_results_df = pd.DataFrame(group_specific_video_test_results)
                    report.set_table_dataframe(test_results_df)
                    report.html += report.dataframe.to_html(index=False, justify='center', render_links=True, escape=False)

            else:
                report.set_table_title("Test Video Results:")
                report.build_table_title()
                video_test_details = pd.DataFrame(video_test_results_dict)
                report.set_table_dataframe(video_test_details)
                report.html += report.dataframe.to_html(index=False,
                                                        justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
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
            except Exception as e:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}. Exception: {e}')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def get_test_results_data(self, test_results, group):
        """
        Filters the overall test results to include only the data belonging to a specific group.

        This function maps hostnames to their respective groups using the configuration object
        (`self.configobj.get_groups_devices`). It then filters the input `test_results` dictionary
        so that only entries corresponding to devices in the specified `group` are retained.

        Args:
            test_results (dict): A dictionary containing lists of test result values for all devices.
                Example:
                    {
                        "Hostname": ["Device1", "Device2"],
                        "RSSI": [-45, -50],
                        "Link Rate": [300, 150],
                        ...
                    }
            group (str): The name of the group whose test result data needs to be extracted.

        Returns:
            dict: A dictionary in the same structure as `test_results`, but filtered to include
            only entries for hostnames that belong to the given `group`.

        Example:
            >>> test_results = {
            ...     "Hostname": ["D1", "D2", "D3"],
            ...     "RSSI": [-40, -50, -55]
            ... }
            >>> self.get_test_results_data(test_results, "GroupA")
            {
                "Hostname": ["D1", "D3"],
                "RSSI": [-40, -55]
            }

        Notes:
            - Relies on `self.configobj.get_groups_devices()` to retrieve the mapping of
            groups to device hostnames.
            - Returns an empty dictionary if no hostnames from the group are found.
        """
        groups_devices_map = self.config_obj.get_groups_devices(data=self.selected_groups, groupdevmap=True)
        group_hostnames = groups_devices_map.get(group, [])
        group_test_results = {}

        for key in test_results:
            group_test_results[key] = []

        for idx, hostname in enumerate(test_results["Device Name"]):
            if hostname in group_hostnames:
                for key in test_results:
                    group_test_results[key].append(test_results[key][idx])

        return group_test_results

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

    def add_bandsteering_report_section(self, report=None):
        try:

            """
            Bandsteering reporting (Robo-style):
            Reads all zoom stats CSVs from report directory (self.path) and builds:
            - BSSID change count graph per device
            - Table of BSSID change events
            """
            if report is None:
                logger.error("Bandsteering report: report object is None")
                return

            report_dir = self.path

            if not report_dir or not os.path.isdir(report_dir):
                logger.error(f"Bandsteering report: invalid report dir: {report_dir}")
                return

            logger.info(f"Bandsteering report dir: {report_dir}")

            # Search for CSV files in self.path
            csv_files = glob.glob(os.path.join(report_dir, "*.csv"))
            logger.info(f"Bandsteering CSV files found: {csv_files}")

            if not csv_files:
                logger.warning("No CSVs found in report dir for bandsteering")
                return

            report.set_obj_html(
                _obj_title="Band Steering Statistics",
                _obj="This section summarizes BSSID changes observed while the robot moved between coordinates.",
            )
            report.build_objective()

            allowed_bssids = set(self.bssids) if self.bssids else set()

            for csv_file_path in csv_files:
                try:
                    df = pd.read_csv(csv_file_path)
                except Exception as e:
                    logger.error(
                        f"Unable to read CSV {csv_file_path}: {e}", exc_info=True
                    )
                    continue

                # Rename columns to match the specific capitalization expected by this logic
                df.rename(
                    columns={
                        "timestamp": "TimeStamp",
                        "bssid": "BSSID",
                        "channel": "Channel",
                    },
                    inplace=True,
                )

                required_cols = {
                    "TimeStamp",
                    "BSSID",
                    "From_Coord",
                    "To_Coord",
                    "Channel",
                }

                # Check if this CSV actually contains bandsteering data (skip summary/other CSVs)
                if not required_cols.issubset(df.columns):
                    continue

                device_name = os.path.basename(csv_file_path).replace(".csv", "")

                # Clean columns
                df["BSSID"] = df["BSSID"].fillna("NA").astype(str)
                df["TimeStamp"] = df["TimeStamp"].fillna("NA").astype(str)
                df["From_Coord"] = df["From_Coord"].fillna("NA").astype(str)
                df["To_Coord"] = df["To_Coord"].fillna("NA").astype(str)
                df["Channel"] = df["Channel"].fillna("NA").astype(str)

                # Filter only configured BSSIDs (if provided)
                if allowed_bssids:
                    df = df[df["BSSID"].isin(allowed_bssids)]

                if df.empty:
                    logging.info(f"No matching BSSID rows for {device_name}")

                # Detect change points
                df["prev_bssid"] = df["BSSID"].shift()

                mask = (
                    (df["BSSID"] != df["prev_bssid"])
                    & (df["BSSID"] != "NA")
                    & (df["prev_bssid"] != "NA")
                    & (df["prev_bssid"].notnull())
                )

                bssid_list = df.loc[mask, "BSSID"].tolist()
                timestamp_list = df.loc[mask, "TimeStamp"].tolist()
                from_coordinate_list = df.loc[mask, "From_Coord"].tolist()
                to_coordinate_list = df.loc[mask, "To_Coord"].tolist()
                channel_list = df.loc[mask, "Channel"].tolist()

                skip_table = not mask.any()

                # Count BSSID switches
                if skip_table:
                    # Ensure all expected BSSIDs show zero
                    bssid_counts = {bssid: 0 for bssid in self.bssids}
                else:
                    bssid_counts = Counter(bssid_list)

                # Ensure consistent graph ordering
                if self.bssids:
                    final_bssid_counts = {
                        bssid: bssid_counts.get(bssid, 0) for bssid in self.bssids
                    }
                else:
                    final_bssid_counts = bssid_counts

                x_axis = list(final_bssid_counts.keys())
                y_axis = [[float(v)] for v in final_bssid_counts.values()]

                report.set_obj_html(
                    _obj_title=f"BSSID Change Count Of The Client {device_name}",
                    _obj=" ",
                )
                report.build_objective()

                graph = lf_bar_graph(
                    _data_set=y_axis,
                    _xaxis_name="BSSID",
                    _yaxis_name="Number of Changes",
                    _xaxis_categories=[""],
                    _xaxis_label=x_axis,
                    _graph_image_name=f"zoom_bssid_change_count_{device_name}",
                    _label=x_axis,
                    _xaxis_step=1,
                    _graph_title=f"Zoom Bandsteering: BSSID change count for device : {device_name}",
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
                report.set_csv_filename(graph_png)
                report.move_csv_file()
                report.build_graph()

                if skip_table:
                    report.set_obj_html(
                        _obj_title=f"Band Steering Results for {device_name}",
                        _obj="No band steering events observed for the configured BSSID list.",
                    )
                    report.build_objective()
                    continue

                report.set_obj_html(
                    _obj_title=f"Band Steering Results for {device_name}", _obj=" "
                )
                report.build_objective()

                table_df = pd.DataFrame(
                    {
                        "TimeStamp": timestamp_list,
                        "BSSID": bssid_list,
                        "Channel": channel_list,
                        "From Coordinate": from_coordinate_list,
                        "To Coordinate": to_coordinate_list,
                    }
                )

                report.set_table_dataframe(table_df)
                report.build_table()

            # Handle Charging Timestamps (Check if robo_obj exists first)
            if (
                hasattr(self, "robo_obj")
                and hasattr(self.robo_obj, "charging_timestamps")
                and len(self.robo_obj.charging_timestamps) != 0
            ):
                report.set_obj_html(_obj_title="Charging Timestamps", _obj="")
                report.build_objective()
                df = pd.DataFrame(
                    self.robo_obj.charging_timestamps,
                    columns=[
                        "charge_dock_arrival_timestamp",
                        "charging_completion_timestamp",
                    ],
                )
                # Add S.No column
                df.insert(0, "S.No", range(1, len(df) + 1))
                report.set_table_dataframe(df)
                report.build_table()
            else:
                report.set_obj_html(
                    _obj_title="Charging Timestamps",
                    _obj="Robot did not go to charge during this test",
                )
                report.build_objective()
        except Exception as e:
            logger.error(f"Exeception Occured {e}")
            logger.error("Error Occured ", exc_info=True)

    def add_live_view_images_to_report(self):
        """
        Waits for and adds the Video and Audio heatmap images for Floor 1.
        """
        live_view_dir = os.path.join(self.path, "live_view_images")

        # Define the specific filenames for Floor 1
        video_img_name = f"zoom_video_{self.testname}_floor1.png"
        audio_img_name = f"zoom_audio_{self.testname}_floor1.png"

        video_path = os.path.join(live_view_dir, video_img_name)
        audio_path = os.path.join(live_view_dir, audio_img_name)

        timeout = 90  # seconds
        start_time = time.time()

        # 1. Wait for the Video image (Primary trigger)
        while not (os.path.exists(video_path) and os.path.exists(audio_path)):
            if time.time() - start_time > timeout:
                logger.error(f"Timeout: {video_img_name} not found within 60 seconds.")
                break
            time.sleep(1)

        if os.path.exists(video_path):
            logger.info(f"Found video heatmap image: {video_path}")
        else:
            logger.warning(f"Video heatmap image not found: {video_path}")

        if os.path.exists(audio_path):
            logger.info(f"Found audio heatmap image: {audio_path}")
        else:
            logger.warning(f"Audio heatmap image not found: {audio_path}")

        # 2. Build the HTML Report Content
        html_content = ""

        # Add Video Map (if found)
        if os.path.exists(video_path):
            html_content += (
                '<div style="page-break-before: always;"></div>'
                '<h3 style="text-align:center;">Video Heatmap</h3>'
                f'<div style="text-align:center;"><img src="file://{video_path}" style="width:1200px; height:800px;"></img></div>'
            )

        # Add Audio Map (if found)
        if os.path.exists(audio_path):
            html_content += (
                '<div style="page-break-before: always;"></div>'
                '<h3 style="text-align:center;">Audio Heatmap</h3>'
                f'<div style="text-align:center;"><img src="file://{audio_path}" style="width:1200px; height:800px;"></img></div>'
            )

        # 3. Inject into Report
        if html_content:
            self.report.set_custom_html(html_content)

    def generate_report_from_api(self):
        self.report = lf_report(
            _output_pdf="zoom_call_report.pdf",
            _output_html="zoom_call_report.html",
            _results_dir_name="zoom_call_report",
            _path=self.path,
        )
        self.report_path_date_time = self.report.get_path_date_time()
        self.report.set_title("Zoom Call Automated Report")
        self.report.build_banner()
        self.report.set_table_title("Objective:")
        self.report.build_table_title()
        self.report.set_text(
            """The Zoom Conference Test is designed to evaluate an Access Point ability
                to handle real-time conferencing workloads when multiple clients, including Windows,
                Linux, macOS, and Android devices, participate in a Zoom meeting. The test measures
                the AP's efficiency in managing audio, video, and screen share traffic while maintaining
                acceptable latency, jitter, packet loss, and bitrate. Additional observations include client
                connection stability, airtime fairness, and MOS Score. The expected behavior is for the
                Access Point to sustain consistent Zoom performance as the client load increases,
                ensuring reliable conferencing quality without significant degradation across upstream
                and downstream traffic
            """
        )
        self.report.build_text_simple()
        self.report.set_table_title("Test Parameters:")
        self.report.build_table_title()
        testtype = ""
        if self.audio and self.video:
            testtype = "AUDIO & VIDEO"
        elif self.audio:
            testtype = "AUDIO"
        elif self.video:
            testtype = "VIDEO"

        # lambda function to convert min to HH:MM:SS
        to_hms = (
            lambda mins: f"{int(mins * 60 // 3600):02}:{int((mins * 60 % 3600) // 60):02}:{int(mins * 60 % 60):02}"
        )

        if self.config:
            test_parameters = pd.DataFrame(
                [
                    {
                        "Test Name": "Zoom Conference Call Test",
                        "Date": time.strftime("%d-%m-%Y", time.localtime()),
                        "Configured Devices": self.hostname_os_combination,
                        "Zoom Meeting ID": self.remote_login_url,
                        "Devices Used": f"W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})",
                        "Test Duration": to_hms(self.duration),
                        "EMAIL ID": self.signin_email,
                        "PASSWORD": self.signin_passwd,
                        "HOST": self.real_sta_list[0],
                        "TEST TYPE": testtype,
                        "SSID": self.ssid,
                        "Security": self.security,
                    }
                ]
            )
        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            gp_pairs = zip(self.selected_groups, self.selected_profiles)
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

            test_parameters = pd.DataFrame(
                [
                    {
                        "Test Name": "Zoom Conference Call Test",
                        "Date": time.strftime("%d-%m-%Y", time.localtime()),
                        "Configuration": gp_map,
                        "Configured Devices": self.hostname_os_combination,
                        "Zoom Meeting ID": self.remote_login_url,
                        "Devices Used": f"W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})",
                        "Test Duration": to_hms(self.duration),
                        "EMAIL ID": self.signin_email,
                        "PASSWORD": self.signin_passwd,
                        "HOST": self.real_sta_list[0],
                        "TEST TYPE": testtype,
                        "Iterations": self.cycles,
                    }
                ]
            )
        else:
            test_params_list = [
                {
                    "Test Name": "Zoom Conference Call Test",
                    "Date": time.strftime("%d-%m-%Y", time.localtime()),
                    "Devices Used": f"W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})",
                    "EMAIL ID": self.signin_email,
                    "PASSWORD": self.signin_passwd,
                    "HOST": self.real_sta_list[0],
                    "TEST TYPE": testtype,
                }
            ]
            if self.do_robo or self.do_bs:
                test_params_list[0].update(
                    {
                        "Coordinates": self.coordinates_list,
                    }
                )
                if self.do_bs:
                    test_params_list[0].update(
                        {
                            "Iterations": self.cycles,
                        }
                    )
            test_parameters = pd.DataFrame(test_params_list)
        self.report.set_table_dataframe(test_parameters)
        self.report.build_table()

        device_data = self._get_report_device_data()

        if not self.download_csv:
            self.report.set_table_title("Test Devices:")
            self.report.build_table_title()
            device_details = pd.DataFrame(
                {
                    "Hostname": self.real_sta_hostname,
                    "OS Type": self.real_sta_os_type,
                    "MAC": self.mac_list,
                    "RSSI": self.rssi_list,
                    "Link Rate": self.link_rate_list,
                    "SSID": self.ssid_list,
                    "Role in call": [
                        "Host" if index == 0 else "Participant"
                        for index, hostname in enumerate(self.real_sta_hostname)
                    ],
                }
            )
        else:
            csv_device_data = {}
            try:
                if not os.path.exists(os.path.join(os.getcwd(), self.csv_file_name)):
                    logger.error(f"File not found: {self.csv_file_name}")
                    self.report.set_table_title("Test Devices:")
                    self.report.build_table_title()
                    device_details = pd.DataFrame(
                        {
                            "Hostname": self.real_sta_hostname,
                            "OS Type": self.real_sta_os_type,
                            "MAC": self.mac_list,
                            "SSID": self.ssid_list,
                            "Role in call": [
                                "Host" if index == 0 else "Participant"
                                for index, hostname in enumerate(self.real_sta_hostname)
                            ],
                        }
                    )
                else:
                    csv_device_data = self.summarize_csv_audio_video(self.csv_file_name)
                    device_data = csv_device_data
                    self.report.set_table_title("Test Devices:")
                    self.report.build_table_title()
                    device_details = pd.DataFrame(
                        {
                            "Hostname": self.real_sta_hostname,
                            "OS Type": self.real_sta_os_type,
                            "MAC": self.mac_list,
                            "SSID": self.ssid_list,
                            "Role in call": [
                                "Host" if index == 0 else "Participant"
                                for index, hostname in enumerate(self.real_sta_hostname)
                            ],
                            "Overall Audio MOS": [
                                csv_device_data.get(client, {}).get("audio_mos_avg")
                                or 0
                                for client in self.real_sta_hostname
                            ],
                            "Overall Video MOS": [
                                csv_device_data.get(client, {}).get("video_mos_avg")
                                or 0
                                for client in self.real_sta_hostname
                            ],
                        }
                    )
            except Exception as e:
                logger.error(f"Error while getting/reading: {self.csv_file_name}: {e}")
                device_data = self._get_report_device_data()
                self.report.set_table_title("Test Devices:")
                self.report.build_table_title()
                device_details = pd.DataFrame(
                    {
                        "Hostname": self.real_sta_hostname,
                        "OS Type": self.real_sta_os_type,
                        "MAC": self.mac_list,
                        "SSID": self.ssid_list,
                        "Role in call": [
                            "Host" if index == 0 else "Participant"
                            for index, hostname in enumerate(self.real_sta_hostname)
                        ],
                    }
                )
        self.report.set_table_dataframe(device_details)
        self.report.build_table()

        if self.audio:
            self.report.set_table_title("1. Audio Performance")
            self.report.build_table_title()

            self.report.set_text(
                """Audio quality is evaluated through latency, jitter, bitrate, and packet loss, ensuring clear communication and consistent voice transmission."""
            )
            self.report.build_text_simple()

            # audio bitrate graph
            self.report.set_graph_title("a. Audio Bitrate (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("audio_input_bitrate_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("audio_output_bitrate_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname

            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Bitrate (Kbps)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Audio Bitrate(Recevied/Sent)",
                _graph_image_name="Audio Bitrate(Recevied and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # audio latency graph
            self.report.set_graph_title("b. Audio Latency (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("audio_input_latency_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("audio_output_latency_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Latency (ms)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Audio Latency(received/sent)",
                _graph_image_name="Audio Latency(received and sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # audio jitter graph
            self.report.set_graph_title("c. Audio Jitter (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("audio_input_jitter_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("audio_output_jitter_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Jitter (ms)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Audio Jitter(Received/Sent)",
                _graph_image_name="Audio Jitter(received and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # audio packet loss graph
            self.report.set_graph_title("d. Audio Packet Loss (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("audio_input_avg_loss_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("audio_output_avg_loss_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Packet Loss (%)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Audio Packet Loss(Recevied/Sent)",
                _graph_image_name="Audio Packet Loss(Recevied and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            self.report.set_table_title("Test Audio Results Table:")
            self.report.build_table_title()
            audio_test_details = pd.DataFrame(
                {
                    "Device Name": [client for client in self.real_sta_hostname],
                    "Avg Bitrate (kbps) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "audio_input_bitrate_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "audio_output_bitrate_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Latency (ms) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "audio_input_latency_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "audio_output_latency_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Jitter (ms) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "audio_input_jitter_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "audio_output_jitter_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Pkt Loss (%) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "audio_input_avg_loss_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "audio_output_avg_loss_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                }
            )
            self.report.set_table_dataframe(audio_test_details)
            self.report.dataframe_html = self.report.dataframe.to_html(
                index=False, justify="center", render_links=True, escape=False
            )
            self.report.html += self.report.dataframe_html
        if self.video:
            self.report.set_table_title("2. Video Performance")
            self.report.build_table_title()

            self.report.set_text(
                "Video traffic stresses the Access Point with higher bandwidth demand. "
                "Performance is validated by maintaining resolution, frame rate, "
                "and minimal loss under increasing client loads."
            )
            self.report.build_text_simple()

            # video bitrate graph
            self.report.set_graph_title("a. Video Bitrate (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("video_input_bitrate_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("video_output_bitrate_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Bitrate (kbps)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Video Bitrate(Recevied/Sent)",
                _graph_image_name="Video Bitrate(Recevied and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # video latency graph
            self.report.set_graph_title("b. Video Latency (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("video_input_latency_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("video_output_latency_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Latency (ms)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Video Latency(Recevied/Sent)",
                _graph_image_name="Video Latency(Recevied and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # video jitter graph
            self.report.set_graph_title("c. Video Jitter (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("video_input_jitter_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("video_output_jitter_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Jitter (ms)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Video Jitter(Recevied/Sent)",
                _graph_image_name="Video Jitter(Recevied and sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            # video packet loss graph
            self.report.set_graph_title("d. Video Packet Loss (Recevied/Sent)")
            self.report.build_graph_title()
            x_data_set = [
                [
                    (device_data.get(client, {}).get("video_input_avg_loss_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
                [
                    (device_data.get(client, {}).get("video_output_avg_loss_avg") or 0)
                    for index, client in enumerate(self.real_sta_hostname)
                ],
            ]
            y_data_set = self.real_sta_hostname
            x_fig_size = 18
            y_fig_size = len(self.real_sta_hostname) * 1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Packet Loss (%)",
                _yaxis_name="Devices",
                _yaxis_label=y_data_set,
                _yaxis_categories=y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=0.20,
                _color_name=["blue", "orange"],
                _show_bar_value=True,
                _figsize=(x_fig_size, y_fig_size),
                _graph_title="Video Packet Loss(Recevied/Sent)",
                _graph_image_name="Video Packet Loss(Recevied and Sent)",
                _label=["Avg Recv", "Avg Sent"],
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            self.report.set_graph_image(graph_image)
            self.report.move_graph_image()
            self.report.build_graph()

            self.report.set_table_title("Test Video Results Table:")
            self.report.build_table_title()
            video_test_details = pd.DataFrame(
                {
                    "Device Name": [client for client in self.real_sta_hostname],
                    "Avg Bitrate (kbps) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "video_input_bitrate_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "video_output_bitrate_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Latency (ms) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "video_input_latency_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "video_output_latency_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Jitter (ms) [Received/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "video_input_jitter_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "video_output_jitter_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                    "Avg Pkt Loss (%) [Recevied/Sent]": [
                        "{}/{}".format(
                            (
                                device_data.get(client, {}).get(
                                    "video_input_avg_loss_avg"
                                )
                                or 0
                            ),
                            (
                                device_data.get(client, {}).get(
                                    "video_output_avg_loss_avg"
                                )
                                or 0
                            ),
                        )
                        for index, client in enumerate(self.real_sta_hostname)
                    ],
                }
            )
            self.report.set_table_dataframe(video_test_details)
            self.report.dataframe_html = self.report.dataframe.to_html(
                index=False, justify="center", render_links=True, escape=False
            )
            self.report.html += self.report.dataframe_html
        if self.do_bs:
            self.add_bandsteering_report_section(report=self.report)
        self.report.write_html()
        self.report.write_pdf(_page_size="Legal", _orientation="Landscape")
        for client in self.real_sta_hostname:
            file_to_move_path = os.path.join(self.path, f"{client}.csv")
            self.move_files(file_to_move_path, self.report_path_date_time)
        if self.download_csv:
            self.move_files(
                os.path.join(os.getcwd(), self.csv_file_name),
                self.report_path_date_time,
            )
        self.move_files(
            os.path.join(
                os.getcwd(), "zoom_api_responses", f"{self.remote_login_url}_qos.json"
            ),
            self.report_path_date_time,
        )
        self.move_files(
            os.path.join(
                os.getcwd(),
                "zoom_api_responses",
                f"{self.remote_login_url}_raw_qos.json",
            ),
            self.report_path_date_time,
        )

    def generate_report_from_data(self):
        """
        Main function to generate report from API data.
        """
        # --- Initialize Report ---
        self.report = lf_report(
            _output_pdf="zoom_call_report.pdf",
            _output_html="zoom_call_report.html",
            _results_dir_name="zoom_call_report",
            _path=self.path,
        )
        report_path_date_time = self.report.get_path_date_time()
        self.report.set_title("Zoom Call Automated Report")
        self.report.build_banner()

        # --- Objective Section ---
        self.report.set_table_title("Objective:")
        self.report.build_table_title()
        self.report.set_text(
            """The Zoom Conference Test is designed to evaluate an Access Point ability
                to handle real-time conferencing workloads when multiple clients, including Windows,
                Linux, macOS, and Android devices, participate in a Zoom meeting...
            """
        )
        self.report.build_text_simple()

        # --- Test Parameters Table ---
        self.report.set_table_title("Test Parameters:")
        self.report.build_table_title()

        testtype = (
            "AUDIO & VIDEO"
            if (self.audio and self.video)
            else ("AUDIO" if self.audio else "VIDEO")
        )
        to_hms = (
            lambda mins: f"{int(mins * 60 // 3600):02}:{int((mins * 60 % 3600) // 60):02}:{int(mins * 60 % 60):02}"
        )

        param_data = {
            "Test Name": "Zoom Conference Call Test",
            "Date": time.strftime("%d-%m-%Y", time.localtime()),
            "Devices Used": f"W({self.windows}),L({self.linux}),M({self.mac}),A({self.android})",
            "Zoom Meeting ID": (
                self.remote_login_url if not self.do_robo else "Robo-Multi-Location"
            ),
            "Test Duration": to_hms(self.duration),
            "TEST TYPE": testtype,
            "Mode": "Robo Motion" if self.do_robo else "Static",
        }

        # Add conditional fields
        if self.config:
            param_data["Configured Devices"] = self.hostname_os_combination
            param_data["SSID"] = self.ssid
            param_data["Security"] = self.security
        elif len(self.selected_groups) > 0 and len(self.selected_profiles) > 0:
            gp_pairs = zip(self.selected_groups, self.selected_profiles)
            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)
            param_data["Configuration"] = gp_map
            param_data["Configured Devices"] = self.hostname_os_combination

        self.report.set_table_dataframe(pd.DataFrame([param_data]))
        self.report.build_table()

        # ROBO MODE: Iterate through Coords/Angles and generate device graphs for each
        self._generate_robo_per_location_report()

        if self.do_webui:
            self.add_live_view_images_to_report()

        # --- Finalize Report ---
        self.report.build_custom()
        self.report.write_html()
        self.report.write_pdf(_page_size="Legal", _orientation="Landscape")
        self._move_report_files(report_path_date_time)

    def _generate_robo_per_location_report(self):
        """
        Iterates through every coordinate and angle, loads the specific JSON,
        and generates Device-Specific Bar Graphs (Device Name on Y-Axis).
        """
        coords = self.coordinates_list if self.coordinates_list else ["0,0,0"]

        for coord in coords:
            # Determine angles loop
            if self.rotations_enabled and self.angles_list:
                angles_loop = self.angles_list
            else:
                angles_loop = [self.current_angle]

            for angle in angles_loop:
                # 1. Heading for this Location
                if self.rotations_enabled:
                    heading = f"Audio and Video graphs at coordinate {coord} and angle {angle}"
                else:
                    heading = f"Audio and Video graphs at coordinate {coord}"
                self.report.set_table_title(heading)
                self.report.build_table_title()

                # 2. Load Data
                json_pattern = f"*_{coord}_{angle}_qos.json"
                file_path = os.path.join("zoom_api_responses", json_pattern)
                found_files = glob.glob(file_path)
                device_data = {}
                if found_files:
                    try:
                        with open(found_files[0], "r") as f:
                            raw_data = json.load(f)
                        device_data = self._get_report_device_data(raw_data)
                    except Exception as e:
                        logger.error(f"Error reading {found_files[0]}: {e}")
                        self.report.set_text(f"Error loading data for {coord}/{angle}")
                        self.report.build_text_simple()
                        continue
                else:
                    self.report.set_text(f"No data found for {coord}/{angle}")
                    self.report.build_text_simple()
                    continue

                # 3. Generate Audio Graphs (Device on Y-Axis)
                if self.audio:
                    suffix = f"_{coord}_{angle}"
                    self._build_metric_graph(
                        "Audio", "Bitrate", "Kbps", device_data,
                        "audio_input_bitrate_avg", "audio_output_bitrate_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Audio", "Latency", "ms", device_data,
                        "audio_input_latency_avg", "audio_output_latency_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Audio", "Jitter", "ms", device_data,
                        "audio_input_jitter_avg", "audio_output_jitter_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Audio", "Packet Loss", "%", device_data,
                        "audio_input_avg_loss_avg", "audio_output_avg_loss_avg", suffix,
                    )
                    self._build_results_table(device_data, "audio")

                # 4. Generate Video Graphs (Device on Y-Axis)
                if self.video:
                    suffix = f"_{coord}_{angle}"
                    self._build_metric_graph(
                        "Video", "Bitrate", "Kbps", device_data,
                        "video_input_bitrate_avg", "video_output_bitrate_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Video", "Latency", "ms", device_data,
                        "video_input_latency_avg", "video_output_latency_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Video", "Jitter", "ms", device_data,
                        "video_input_jitter_avg", "video_output_jitter_avg", suffix,
                    )
                    self._build_metric_graph(
                        "Video", "Packet Loss", "%", device_data,
                        "video_input_avg_loss_avg", "video_output_avg_loss_avg", suffix,
                    )
                    self._build_results_table(device_data, "video")

                # Add a separator between coordinates
                self.report.set_custom_html("<hr>")
                self.report.build_custom()

    def _build_metric_graph(
        self, media_type, metric_name, unit, data, input_key, output_key, suffix=""
    ):
        """
        Helper to build standard horizontal bar graphs with Device Names on Y-Axis.
        """
        self.report.set_graph_title(f"{media_type} {metric_name} (Sent/Received)")
        self.report.build_graph_title()

        sent_vals = []
        recv_vals = []

        for client in self.real_sta_hostname:
            device_key = client

            def get_val(key):
                val = data.get(device_key, {}).get(key)
                return val if val is not None else 0

            sent_vals.append(get_val(output_key))
            recv_vals.append(get_val(input_key))

        bar_graph = lf_bar_graph_horizontal(
            _data_set=[sent_vals, recv_vals],
            _xaxis_name=f"{metric_name} ({unit})",
            _yaxis_name="Devices",
            _yaxis_categories=self.real_sta_hostname,
            _graph_title=f"{media_type} {metric_name}",
            _graph_image_name=f"{media_type}_{metric_name}{suffix}",
            _label=["Avg Sent", "Avg Recv"],
            _figsize=(18, len(self.real_sta_hostname) * 1 + 4),
            _color_name=["blue", "orange"],
        )
        self.report.set_graph_image(bar_graph.build_bar_graph_horizontal())
        self.report.move_graph_image()
        self.report.build_graph()

    def _build_results_table(self, data, media_type):
        """Helper for Summary Table"""

        def fmt_val(client, key):
            val = data.get(client, {}).get(key)
            return val if val is not None else 0

        p = media_type

        details = pd.DataFrame(
            {
                "Device Name": self.real_sta_hostname,
                "Avg Bitrate (kbps) [S/R]": [
                    f"{fmt_val(c, f'{p}_output_bitrate_avg')}/{fmt_val(c, f'{p}_input_bitrate_avg')}"
                    for c in self.real_sta_hostname
                ],
                "Avg Latency (ms) [S/R]": [
                    f"{fmt_val(c, f'{p}_output_latency_avg')}/{fmt_val(c, f'{p}_input_latency_avg')}"
                    for c in self.real_sta_hostname
                ],
                "Avg Jitter (ms) [S/R]": [
                    f"{fmt_val(c, f'{p}_output_jitter_avg')}/{fmt_val(c, f'{p}_input_jitter_avg')}"
                    for c in self.real_sta_hostname
                ],
                "Avg Pkt Loss (%) [S/R]": [
                    f"{fmt_val(c, f'{p}_output_avg_loss_avg')}/{fmt_val(c, f'{p}_input_avg_loss_avg')}"
                    for c in self.real_sta_hostname
                ],
            }
        )
        self.report.set_table_dataframe(details)
        self.report.dataframe_html = self.report.dataframe.to_html(
            index=False, justify="center", render_links=True, escape=False
        )
        self.report.html += self.report.dataframe_html

    def _move_report_files(self, report_path_date_time):
        """
        Helper to move CSVs, and Robo JSONs to the report folder.
        """
        # 1. Move Client CSV files
        if self.do_robo:
            for coord in self.coordinates_list:
                if self.rotations_enabled:
                    for angle in self.angles_list:
                        for client in self.real_sta_hostname:
                            csv_path = os.path.join(
                                self.path,
                                f"{client}_{coord}_{angle}.csv",
                            )
                            if os.path.exists(csv_path):
                                self.move_files(csv_path, report_path_date_time)
                else:
                    for client in self.real_sta_hostname:
                        csv_path = os.path.join(self.path, f"{client}_{coord}.csv")
                        if os.path.exists(csv_path):
                            self.move_files(csv_path, report_path_date_time)

        # 2. Move Robo JSONs (Wildcard search for Multi-Location files)
        if self.do_robo:
            pattern = os.path.join(os.getcwd(), "zoom_api_responses", "*_qos.json")
            for f in glob.glob(pattern):
                self.move_files(f, report_path_date_time)

    def stop_webui(self):
        """
        Updates the running_status.json file to mark the test as Completed.
        """
        try:
            json_path = os.path.join(self.path, "running_status.json")

            # 1. Load existing data or create new dict
            data = {}
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}

            # 2. Update status
            data["status"] = "Completed"

            # 3. Write back to file
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Updated running_status.json at {json_path}")

        except Exception as e:
            logger.error(f"Error updating running_status.json: {e}")

    def run_robo_test(self):
        for coordinate in self.coordinates_list:
            self.robo_obj.wait_for_battery()
            matched, aborted = self.robo_obj.move_to_coordinate(coord=coordinate)
            if matched:
                self.current_cord = coordinate
                self.successful_coords.append(coordinate)
            else:
                self.failed_coords.append(coordinate)
            if aborted:
                logger.error(f"Failed to Reach the coordinate {self.current_cord}")
                self.failed_coords.append(coordinate)
                sys.exit()
            if self.rotations_enabled:
                for angle in self.angles_list:
                    self.robo_obj.wait_for_battery()
                    rotated = self.robo_obj.rotate_angle(angle_degree=angle)
                    if rotated:
                        self.current_angle = angle
                    else:
                        logger.error(f"Failed to Rotate the Angle {self.current_angle}")
                        sys.exit()
                    self.run()
                    self.participants_joined = 0

            else:
                self.run()
                self.participants_joined = 0


def main():
    try:
        parser = argparse.ArgumentParser(
            prog=__file__,
            formatter_class=argparse.RawTextHelpFormatter,
            description=textwrap.dedent("""
                Zoom Automation Script
                PURPOSE: lf_interop_zoom.py provides the available devices and allows the user to start Zoom call conference meeting for the user-specified duration

                EXAMPLE-1:
                Command Line Interface to run Zoom with specified duration:
                python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video
                --upstream_port 1.1.eth1

                EXAMPLE-2:
                Command Line Interface to run Zoom on multiple devices:
                python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.214.219" --signin_email "demo@gmail.com" --signin_passwd "Demo@123" --participants 3 --audio --video
                --resources 1.400,1.375 --zoom_host 1.95 --upstream_port 1.1.eth1

                EXAMPLE-3:
                Command Line Interface to run Zoom on multiple devices with Device Configuration:
                python3 lf_interop_zoom.py --duration 1 --lanforge_ip "192.168.204.74" --signin_email "demo@gmail.com" --signin_passwd "Demo@10203000" --participants 2 --audio --video
                --upstream_port 1.1.eth1 --zoom_host 1.95 --resources 1.400,1.360 --ssid NETGEAR_2G_wpa2 --passwd Password@123 --encryp wpa2 --config

                EXAMPLE-4:
                Command Line Interface to run Zoom with Groups and Profiles:
                python3 lf_interop_zoom.py --duration 1  --lanforge_ip "192.168.204.74" --signin_email "demo@gmail.com" --signin_passwd "Demo@10203000" --participants 2 --audio --video
                --wait_time 30 --group_name group1,group2 --profile_name netgear5g,netgear2g --file_name grplaptops.csv --zoom_host 1.95 --upstream_port 1.1.eth1
            """),
        )
        parser.add_argument(
            "--duration",
            type=int,
            required=True,
            help="Duration of the Zoom meeting in minutes",
        )
        parser.add_argument(
            "--lanforge_ip", type=str, required=True, help="LANforge IP address"
        )
        parser.add_argument(
            "--signin_email", type=str, required=True, help="Sign-in email"
        )
        parser.add_argument(
            "--signin_passwd", type=str, required=True, help="Sign-in password"
        )
        parser.add_argument(
            "--participants", type=int, required=True, help="no of participanrs"
        )
        parser.add_argument("--audio", action="store_true")
        parser.add_argument("--video", action="store_true")
        parser.add_argument(
            "--wait_time",
            type=int,
            default=30,
            help="time set to wait for the csv files",
        )
        parser.add_argument("--log_level", help="Level of the logs to be dispalyed")
        parser.add_argument("--lf_logger_config_json", help="lf_logger config json")
        parser.add_argument("--resources", help="resources participated in the test")
        parser.add_argument(
            "--do_webUI",
            action="store_true",
            help="useful to specify whether we are running through webui or cli",
        )
        parser.add_argument(
            "--report_dir", help="report directory while running test through web ui"
        )
        parser.add_argument(
            "--testname", help="report directory while running test through web ui"
        )
        parser.add_argument("--zoom_host", help="Host of the test")

        # Arguments Related to Device Configurations
        parser.add_argument("--file_name", help="File name for DeviceConfig")

        parser.add_argument("--group_name", type=str, help="specify the group name")
        parser.add_argument("--profile_name", type=str, help="specify the profile name")

        parser.add_argument(
            "--ssid",
            default=None,
            help="specify ssid on which the test will be running",
        )
        parser.add_argument(
            "--passwd",
            default=None,
            help="specify encryption password  on which the test will " "be running",
        )
        parser.add_argument(
            "--encryp",
            default=None,
            help="specify the encryption type  on which the test will be "
            "running eg :open|psk|psk2|sae|psk2jsae",
        )

        parser.add_argument(
            "--eap_method",
            type=str,
            default="DEFAULT",
            help="Specify the EAP method for authentication.",
        )
        parser.add_argument(
            "--eap_identity",
            type=str,
            default="DEFAULT",
            help="Specify the EAP identity for authentication.",
        )
        parser.add_argument(
            "--ieee8021x", action="store_true", help="Enables IEEE 802.1x support."
        )
        parser.add_argument(
            "--ieee80211u",
            action="store_true",
            help="Enables IEEE 802.11u (Hotspot 2.0) support.",
        )
        parser.add_argument(
            "--ieee80211w",
            type=int,
            default=1,
            help="Enables IEEE 802.11w (Management Frame Protection) support.",
        )
        parser.add_argument(
            "--enable_pkc", action="store_true", help="Enables pkc support."
        )
        parser.add_argument(
            "--bss_transition",
            action="store_true",
            help="Enables BSS transition support.",
        )
        parser.add_argument(
            "--power_save", action="store_true", help="Enables power-saving features."
        )
        parser.add_argument(
            "--disable_ofdma", action="store_true", help="Disables OFDMA support."
        )
        parser.add_argument(
            "--roam_ft_ds",
            action="store_true",
            help="Enables fast BSS transition (FT) support",
        )
        parser.add_argument(
            "--key_management",
            type=str,
            default="DEFAULT",
            help="Specify the key management method (e.g., WPA-PSK, WPA-EAP)",
        )
        parser.add_argument(
            "--pairwise", type=str, default="NA", help="Specify the pairwise cipher"
        )
        parser.add_argument(
            "--private_key",
            type=str,
            default="NA",
            help="Specify EAP private key certificate file.",
        )
        parser.add_argument(
            "--ca_cert",
            type=str,
            default="NA",
            help="Specify the CA certificate file name",
        )
        parser.add_argument(
            "--client_cert",
            type=str,
            default="NA",
            help="Specify the client certificate file name",
        )
        parser.add_argument(
            "--pk_passwd",
            type=str,
            default="NA",
            help="Specify the password for the private key",
        )
        parser.add_argument(
            "--pac_file", type=str, default="NA", help="Specify the pac file name"
        )
        parser.add_argument(
            "--upstream_port",
            type=str,
            default="NA",
            help="Specify the upstream port",
            required=True,
        )
        parser.add_argument(
            "--help_summary", help="Show summary of what this script does", default=None
        )
        parser.add_argument(
            "--expected_passfail_value",
            help="Specify the expected urlcount value for pass/fail",
        )
        parser.add_argument(
            "--device_csv_name",
            type=str,
            help="Specify the device csv name for pass/fail",
            default=None,
        )
        parser.add_argument(
            "--config",
            action="store_true",
            help="specify this flag whether to config devices or not",
        )

        # argument related to api stats collection
        parser.add_argument(
            "--api_stats_collection",
            action="store_true",
            help="Specify if using business account to get the stats using api",
        )
        parser.add_argument("--account_id", help="Zoom Account ID")
        parser.add_argument("--client_id", help="Zoom Client ID")
        parser.add_argument("--client_secret", help="Zoom Client Secret")
        parser.add_argument(
            "--env_file", default=".env", help="Path to .env file for credentials"
        )
        parser.add_argument(
            "--download_csv",
            action="store_true",
            help="Specify if wanted to collect csv from dashboard. Only works with business account",
        )

        # Arguments related to robo feature
        robo_group = parser.add_argument_group(
            "Robo Arguments", "Arguments related to robot movement and coordinates"
        )
        robo_group.add_argument("--robo_ip", type=str, help="Specify the robo ip")
        robo_group.add_argument(
            "--coordinates",
            help="Comma-separated list of coordinate point names (e.g. 1,2,3), each mapping to x and y values",
        )
        robo_group.add_argument(
            "--rotations",
            help="Comma-separated list of rotation angles (in degrees) to apply at respective points",
        )
        robo_group.add_argument(
            "--do_robo",
            help="Specify this flag to perform the test with robo",
            action="store_true",
        )

        # Arguments related to band steering
        bandsteering_group = parser.add_argument_group(
            "Band Steering Arguments", "Arguments related to band steering tests"
        )
        bandsteering_group.add_argument(
            "--bssids",
            type=str,
            help="Comma-separated list of BSSIDs for bandsteering test",
        )
        bandsteering_group.add_argument(
            "--do_bs",
            help="Specify this flag to perform the test with robo for band steering",
            action="store_true",
        )

        # Arguments related to roaming
        roaming_group = parser.add_argument_group(
            "Roaming Arguments",
            "Arguments related to roaming, sniffing, and cycle configuration",
        )
        roaming_group.add_argument(
            "--do_roam",
            help="Specify this flag to perform the test with robo for Roaming",
            action="store_true",
        )
        roaming_group.add_argument(
            "--cycles", type=int, default=1, help="Number of cycles to run the test"
        )
        roaming_group.add_argument(
            "--wait_at_point",
            type=int,
            help="Robot wait duration in seconds before sniffing starts and stops",
            default=30,
        )
        roaming_group.add_argument(
            "--res_lf_ip", help="Resource manager IP address", default="10.17.1.208"
        )
        roaming_group.add_argument(
            "--sniff_radio_2g", help="Sniffer Radio", default="1.2.wiphy0"
        )
        roaming_group.add_argument(
            "--sniff_radio_5g", help="Sniffer Radio", default="1.2.wiphy1"
        )
        roaming_group.add_argument(
            "--sniff_radio_6g", help="Sniffer Radio", default="1.2.wiphy2"
        )
        roaming_group.add_argument(
            "--sniff_channel_2g", help="Channel", type=str, default="11"
        )
        roaming_group.add_argument(
            "--sniff_channel_5g", help="Channel", type=str, default="44"
        )
        roaming_group.add_argument(
            "--sniff_channel_6g", help="Channel", type=str, default="239"
        )
        roaming_group.add_argument(
            "--ap_coordinates",
            help="Comma-separated list of AP coordinates for start/stop sniffing",
            default="",
        )

        args = parser.parse_args()

        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        if (
            args.expected_passfail_value is not None
            and args.device_csv_name is not None
        ):
            logger.error("Specify either expected_passfail_value or device_csv_name")
            exit(1)

        if args.group_name is not None:
            args.group_name = args.group_name.strip()
            selected_groups = args.group_name.split(",")
        else:
            selected_groups = []

        if args.profile_name is not None:
            args.profile_name = args.profile_name.strip()
            selected_profiles = args.profile_name.split(",")
        else:
            selected_profiles = []

        if len(selected_groups) != len(selected_profiles):
            logger.error("Number of groups should match number of profiles")
            exit(0)
        elif (
            args.group_name is not None
            and args.profile_name is not None
            and args.file_name is not None
            and args.resources is not None
        ):
            logger.error("Either group name or device list should be entered not both")
            exit(0)
        elif args.ssid is not None and args.profile_name is not None:
            logger.error("Either ssid or profile name should be given")
            exit(0)
        elif args.file_name is not None and (
            args.group_name is None or args.profile_name is None
        ):
            logger.error("Please enter the correct set of arguments")
            exit(0)
        elif args.config and (
            (
                args.ssid is None
                or args.encryp is None
                or (args.passwd is None and args.encryp.lower() != "open")
            )
        ):
            logger.error(
                "Please provide ssid password and security for configuration of devices"
            )
            exit(0)

        rotations_enabled = False
        bssids = []
        if args.do_robo or args.do_bs or args.do_roam:
            args.coordinates = args.coordinates.split(",") if args.coordinates else []
            args.rotations = (
                [float(angle) for angle in args.rotations.split(",")]
                if args.rotations
                else []
            )
            if args.rotations:
                rotations_enabled = True

            if args.bssids:
                bssids = args.bssids.split(",") if args.bssids else []

        zoom_automation = ZoomAutomation(
            audio=args.audio,
            video=args.video,
            lanforge_ip=args.lanforge_ip,
            wait_time=args.wait_time,
            testname=args.testname,
            upstream_port=args.upstream_port,
            config=args.config,
            selected_groups=selected_groups,
            selected_profiles=selected_profiles,
            robo_ip=args.robo_ip,
            coordinates_list=args.coordinates,
            angles_list=args.rotations,
            do_robo=args.do_robo,
            rotations_enabled=rotations_enabled,
            signin_email=args.signin_email,
            signin_passwd=args.signin_passwd,
            duration=args.duration,
            participants_req=args.participants,
            env_file=args.env_file,
            do_bs=args.do_bs,
            api_stats_collection=args.api_stats_collection,
            do_webui=args.do_webUI,
            cycles=args.cycles,
            bssids=bssids,
            do_roam=args.do_roam,
            sniff_radio_2g=args.sniff_radio_2g,
            sniff_radio_5g=args.sniff_radio_5g,
            sniff_radio_6g=args.sniff_radio_6g,
            sniff_channel_2g=args.sniff_channel_2g,
            sniff_channel_5g=args.sniff_channel_5g,
            sniff_channel_6g=args.sniff_channel_6g,
            wait_at_point=args.wait_at_point,
            resource_ip=args.res_lf_ip,
            ap_coordinates=args.ap_coordinates,
        )
        if args.download_csv:
            zoom_automation.download_csv = True
        args.upstream_port = zoom_automation.change_port_to_ip(args.upstream_port)
        realdevice = RealDevice(
            manager_ip=args.lanforge_ip,
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
        laptops = realdevice.get_devices()

        if args.file_name:
            new_filename = args.file_name.removesuffix(".csv")
        else:
            new_filename = args.file_name
        config_obj = DeviceConfig.DeviceConfig(
            lanforge_ip=args.lanforge_ip, file_name=new_filename
        )

        if not args.expected_passfail_value and args.device_csv_name is None:
            config_obj.device_csv_file(csv_name="device.csv")
        if (
            args.group_name is not None
            and args.file_name is not None
            and args.profile_name is not None
        ):
            selected_groups = args.group_name.split(",")
            selected_profiles = args.profile_name.split(",")
            config_devices = {}
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]

            config_obj.initiate_group()
            asyncio.run(config_obj.connectivity(config_devices))

            adbresponse = config_obj.adb_obj.get_devices()
            resource_manager = config_obj.laptop_obj.get_devices()
            all_res = {}
            df1 = config_obj.display_groups(config_obj.groups)
            groups_list = df1.to_dict(orient="list")
            group_devices = {}

            for adb in adbresponse:
                group_devices[adb["serial"]] = adb["eid"]
            for res in resource_manager:
                all_res[res["hostname"]] = res["shelf"] + "." + res["resource"]
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
                "ssid": args.ssid,
                "passwd": args.passwd,
                "enc": args.encryp,
                "eap_method": args.eap_method,
                "eap_identity": args.eap_identity,
                "ieee80211": args.ieee8021x,
                "ieee80211u": args.ieee80211u,
                "ieee80211w": args.ieee80211w,
                "enable_pkc": args.enable_pkc,
                "bss_transition": args.bss_transition,
                "power_save": args.power_save,
                "disable_ofdma": args.disable_ofdma,
                "roam_ft_ds": args.roam_ft_ds,
                "key_management": args.key_management,
                "pairwise": args.pairwise,
                "private_key": args.private_key,
                "ca_cert": args.ca_cert,
                "client_cert": args.client_cert,
                "pk_passwd": args.pk_passwd,
                "pac_file": args.pac_file,
                "server_ip": args.upstream_port,
            }
            if args.resources:
                all_devices = config_obj.get_all_devices()
                if (
                    args.group_name is None
                    and args.file_name is None
                    and args.profile_name is None
                ):
                    dev_list = args.resources.split(",")
                    if not args.do_webUI:
                        args.zoom_host = args.zoom_host.strip()
                        if args.zoom_host in dev_list:
                            dev_list.remove(args.zoom_host)
                        dev_list.insert(0, args.zoom_host)
                    if args.config:
                        asyncio.run(
                            config_obj.connectivity(
                                device_list=dev_list, wifi_config=config_dict
                            )
                        )
                    args.resources = ",".join(id for id in dev_list)
            else:
                # If no resources provided, prompt user to select devices manually
                if args.config:
                    all_devices = config_obj.get_all_devices()
                    device_list = []
                    for device in all_devices:
                        if device["type"] != "laptop":
                            device_list.append(
                                device["shelf"]
                                + "."
                                + device["resource"]
                                + " "
                                + device["serial"]
                            )
                        elif device["type"] == "laptop":
                            device_list.append(
                                device["shelf"]
                                + "."
                                + device["resource"]
                                + " "
                                + device["hostname"]
                            )
                    print("Available Devices For Testing")
                    for device in device_list:
                        print(device)
                    zm_host = input("Enter Host Resource for the Test : ")
                    zm_host = zm_host.strip()
                    args.resources = input("Enter client Resources to run the test :")
                    args.resources = zm_host + "," + args.resources
                    dev1_list = args.resources.split(",")
                    asyncio.run(
                        config_obj.connectivity(
                            device_list=dev1_list, wifi_config=config_dict
                        )
                    )

        result_list = []
        if not args.do_webUI:
            if args.resources:
                resources = args.resources.split(",")
                resources = [r for r in resources if len(r.split(".")) > 1]
                # resources = sorted(resources, key=lambda x: int(x.split('.')[1]))
                get_data = zoom_automation.select_real_devices(
                    real_device_obj=realdevice, real_sta_list=resources
                )
                for item in get_data:
                    item = item.strip()
                    # Find and append the matching lap to result_list
                    matching_laps = [lap for lap in laptops if lap.startswith(item)]
                    result_list.extend(matching_laps)
                if not result_list:
                    logger.info("Resources donot exist hence Terminating the test.")
                    return
                if len(result_list) != len(get_data):
                    logger.info("Few Resources donot exist")
            else:
                resources = zoom_automation.select_real_devices(
                    real_device_obj=realdevice
                )
        else:
            if args.do_webUI:
                zoom_automation.path = args.report_dir
            resources = args.resources.split(",")
            extracted_parts = [res.split(".")[:2] for res in resources]
            formatted_parts = [".".join(parts) for parts in extracted_parts]

            zoom_automation.select_real_devices(
                real_device_obj=realdevice, real_sta_list=formatted_parts
            )
            if args.do_webUI:

                if len(zoom_automation.real_sta_hostname) == 0:
                    logger.info("No device is available to run the test")
                    obj = {
                        "status": "Stopped",
                        "configuration_status": "configured",
                    }
                    zoom_automation.updating_webui_runningjson(obj)
                    return
                else:
                    obj = {
                        "configured_devices": zoom_automation.real_sta_hostname,
                        "configuration_status": "configured",
                        "no_of_devices": f" Total({len(zoom_automation.real_sta_os_type)}) : W({zoom_automation.windows}),L({zoom_automation.linux}),M({zoom_automation.mac})",
                        "device_list": zoom_automation.hostname_os_combination,
                    }
                    zoom_automation.updating_webui_runningjson(obj)

        if not zoom_automation.check_tab_exists():
            logger.error("Generic Tab is not available.\nAborting the test.")
            exit(0)

        zoom_automation.handle_flask_server()
        zoom_automation.get_resource_data()
        zoom_automation.get_ports_data()
        zoom_automation.get_interop_data()

        if args.api_stats_collection:
            # load environment file if specified
            if args.env_file:
                if os.path.exists(args.env_file):
                    load_dotenv(args.env_file)
                    logger.info(f"Loaded environment variables from {args.env_file}")
                else:
                    raise FileNotFoundError(f".env file '{args.env_file}' not found")

            # Fetching zoom credentials for account
            zoom_automation.account_id = args.account_id or os.environ.get("ACCOUNT_ID")
            zoom_automation.client_id = args.client_id or os.environ.get("CLIENT_ID")
            zoom_automation.client_secret = args.client_secret or os.environ.get(
                "CLIENT_SECRET"
            )

            if not all(
                [
                    zoom_automation.account_id,
                    zoom_automation.client_id,
                    zoom_automation.client_secret,
                ]
            ):
                logger.info("Exiting test.")
                raise ValueError(
                    "Missing Zoom credentials (account_id, client_id, client_secret)"
                )

        if args.do_robo:
            zoom_automation.run_robo_test()
        else:
            zoom_automation.run()
        zoom_automation.data_store.clear()
        if not args.api_stats_collection:
            zoom_automation.generate_report()
        logger.info("Test Completed Sucessfully")
    except Exception as e:
        logger.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
        traceback.print_exc()
    finally:
        if not ("--help" in sys.argv or "-h" in sys.argv):
            zoom_automation.stop_signal = True
            logger.info("Waiting for Browser Cleanup in Laptops")
            time.sleep(10)

            if args.do_robo and args.api_stats_collection:
                zoom_automation.generate_report_from_data()
            elif args.api_stats_collection:
                zoom_automation.generate_report_from_api()
            time.sleep(5)
            if zoom_automation.do_webui:
                zoom_automation.stop_webui()
            zoom_automation.generic_endps_profile.cleanup()
            zoom_automation.move_ping_logs()
            logger.info("Done.")


if __name__ == "__main__":
    main()
