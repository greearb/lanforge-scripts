'''
    NAME: lf_interop_speedtest.py

    PURPOSE:
        The lf_interop_speedtest.py script enables real-world WiFi speed testing for laptop-based clients
        (Linux, Windows, macOS) and Android mobile devices. iOS is not supported.

        Instead, it focuses on measuring actual end-user experience by capturing metrics such as download/upload speed,
        latency (ping). The script uses the Speedtest.net service (via browser automation for laptops) to run the tests.

    TO PERFORM SPEED TEST:

        EXAMPLE-1:
            Run a default speed test using browser-based automation (Selenium)
            ./lf_interop_speedtest.py \
                --mgr 192.168.204.74 \
                --device_list 1.10,1.12 \
                --instance_name SAMPLE_TEST \
                --iteration 1 \
                --upstream_port eth2 \
                --cleanup

        EXAMPLE-2:
            Run speed test on robot with each coordinate and rotation
            ./lf_interop_speedtest.py \
                --mgr 192.168.204.75 \
                --device_list 1.10,1.12 \
                --instance_name SAMPLE_TEST \
                --iteration 1 \
                --robot_test \
                --coordinate 1,2 \
                --rotation 0,90 \
                --robot_ip 127.0.0.1:5000 \
                --upstream_port eth2 \
                --cleanup

        EXAMPLE-3:
            Run speed test on robot with each coordinate without rotation
            ./lf_interop_speedtest.py \
                --mgr 192.168.204.75 \
                --device_list 1.10,1.12 \
                --instance_name SAMPLE_TEST \
                --iteration 1 \
                --robot_test \
                --coordinate 1,2 \
                --robot_ip 127.0.0.1:5000 \
                --upstream_port eth2 \
                --cleanup

'''
import json
import sys
import os
import csv
import time
import shutil
import importlib
import logging
import paramiko
import argparse
import pandas as pd
from datetime import datetime
import threading
try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from lf_graph import lf_bar_graph
from lf_report import lf_report
try:
    pass
    from lf_base_robo import RobotClass  # REAL
except ImportError:
    print("[WARN] lf_base_robo not found")

# from lf_robo_base_class import RobotClass  # Fake

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()


realm = importlib.import_module("py-json.realm")
Realm = realm.Realm


class SpeedTest(Realm):
    def __init__(
            self,
            manager_ip=None,
            port=8080,
            device_list=None,
            instance="Speed_Test_Report",
            iteration=1,
            do_interopability=False,
            type='ookla',
            result_dir=None,
            _debug_on=False,
            robot_test=False,
            robot_ip=None,
            coordinate=None,
            rotation=None,
            upstream_port=None):
        super().__init__(
            lfclient_host=manager_ip,
            debug_=_debug_on)
        self.manager_ip = manager_ip
        self.manager_port = port
        self.upstream_port = upstream_port

        self.device_list = device_list
        self.instance = instance
        self.iteration = iteration
        self.do_interopability = do_interopability
        self.result_dir = result_dir
        self.type = type
        self.devices_data = {}
        self.android_data = {}
        self.laptop_data = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'generic'
        self.generic_endps_profile.cmd = ' '
        self.result_json = {}
        self.stop_time = None
        self.start_time = None
        self.device_info = {}

        self._ingest_lock = threading.Lock()
        self._flask_thread = None
        self._post_url = None

        self.robot_test = robot_test
        self.robot_ip = robot_ip
        self.robot_port = 5000
        self.coordinate = coordinate
        self.rotation = rotation

        self.coordinate_list = coordinate.split(',') if coordinate else []
        if self.rotation is not None:
            self.rotation_list = rotation.split(',') if rotation else []
        else:
            self.rotation_list = None

        self.current_coordinate = None
        self.current_rotation = None
        self.robot_iteration_count = 0
        self.total_robot_tests = 0
        if self.robot_test:
            if self.rotation_list and self.rotation_list[0] != "":
                self.total_robot_tests = len(self.coordinate_list) * len(self.rotation_list)
            else:
                self.total_robot_tests = len(self.coordinate_list)

        if self.coordinate is not None:
            base_dir = os.path.dirname(os.path.dirname(self.result_dir))
            nav_data = os.path.join(base_dir, 'nav_data.json')
            with open(nav_data, "w") as file:
                json.dump({}, file)

            self.robot_obj = RobotClass(robo_ip=self.robot_ip)  # REAL
            self.robot_obj.nav_data_path = nav_data  # REAL

            # self.robot_obj = RobotClass() # Fake
            # self.robot_obj.result_directory=os.path.dirname(nav_data) # Fake
            # self.robot_obj.robo_ip = f"{self.robot_ip}"  # Fake
            self.robot_obj.runtime_dir = self.result_dir
            self.robot_obj.testname = self.instance

        else:
            self.robot_test = False
        if self.upstream_port:
            self.upstream_port = self.change_port_to_ip(self.upstream_port)
            self._post_url = f"http://{self.upstream_port}:5050/api/speedtest"
        else:
            self._post_url = f"http://{self.manager_ip}:5050/api/speedtest"

        self._start_ingest_server()

        # reporting variable
        self.selected_device_type = set()
        self.selected_resources = None
        self.ip_hostname = {}
        self.result_dict = {
            'ip': [],
            'hostname': [],
            'download_speed': [],
            'upload_speed': [],
            'download_lat': [],
            'upload_lat': []
        }
        self.iteration_dict = {}

    def get_expected_post_ips(self):
        """Get list of IP addresses expected to POST speed test results to the ingest server.

        Returns:
            list: List of IP addresses configured with --post_url in their test commands
        """
        want = []
        for info in self.devices_data.values():
            cmd = (info.get('cmd') or '')
            ip = (info.get('ip') or '')
            if ip and '--post_url' in cmd:
                want.append(ip)
        # de-dup (stable)
        seen, out = set(), []
        for ip in want:
            if ip not in seen:
                seen.add(ip)
                out.append(ip)
        return out

    def has_post_for(self, ip):
        """Check if speed test results have been received from a specific IP address.

        Args:
            ip (str): IP address to check for received results

        Returns:
            bool: True if results have been received, False otherwise
        """
        k = ip.replace('.', '_')
        return (k in self.result_json) or (ip in self.result_json)

    def write_results_to_csv(self, current_iter, csv_file):
        """Write speed test results to CSV file for a specific iteration.
        Args:
            current_iter (int): Current iteration number
            csv_file (str): Path to CSV file for storing results
        """

        csv_exists = os.path.isfile(csv_file)

        csv_data = []
        table_data = []

        received = {}
        for raw_ip, data in self.result_json.items():
            ip = raw_ip.replace('_', '.')
            received[ip] = {
                "download": data.get("download", "N/A"),
                "upload": data.get("upload", "N/A"),
                "Idle Latency": data.get("Idle Latency", "N/A"),
                "Download Latency": data.get("Download Latency", "N/A"),
                "Upload Latency": data.get("Upload Latency", "N/A"),
            }

        expected_ips = list(self.ip_hostname.keys()) or list(self.device_info.keys())

        for ip, data in received.items():
            dev_type = self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)

            download = data["download"]
            upload = data["upload"]
            idle_latency = data["Idle Latency"]
            down_latency = data["Download Latency"]
            up_latency = data["Upload Latency"]
            csv_data.append([
                current_iter, self.iteration, ip, dev_type,
                download, upload, idle_latency, down_latency, up_latency
            ])
            table_data.append([
                current_iter, self.iteration, ip, dev_type,
                download, upload, idle_latency, down_latency, up_latency
            ])

            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)

            def _num(x):
                try:
                    return float(str(x).split()[0])
                except Exception:
                    return 0.0

            self.result_dict['download_speed'].append(_num(download))
            self.result_dict['upload_speed'].append(_num(upload))
            self.result_dict['download_lat'].append(_num(down_latency))
            self.result_dict['upload_lat'].append(_num(up_latency))

        missing_ips = [ip for ip in expected_ips if ip not in received]
        for ip in missing_ips:
            dev_type = self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)
            csv_data.append([
                current_iter, self.iteration, ip, dev_type,
                "N/A", "N/A", "N/A", "N/A", "N/A"
            ])
            table_data.append([
                current_iter, self.iteration, ip, dev_type,
                "N/A", "N/A", "N/A", "N/A", "N/A"
            ])

            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)
            self.result_dict['download_speed'].append(0.0)
            self.result_dict['upload_speed'].append(0.0)
            self.result_dict['download_lat'].append(0.0)
            self.result_dict['upload_lat'].append(0.0)

        self.iteration_dict[current_iter] = self.result_dict
        self.result_dict = {
            'ip': [],
            'hostname': [],
            'download_speed': [],
            'upload_speed': [],
            'download_lat': [],
            'upload_lat': []
        }

        with open(csv_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not csv_exists:
                writer.writerow([
                    "Iteration", "Total Iterations", "IP", "Device Type",
                    "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"
                ])
            writer.writerows(csv_data)

        print(f"\n Speedtest Results for Iteration {current_iter}")

        if tabulate:
            print(tabulate(
                table_data,
                headers=[
                    "Iteration", "Total Iterations", "IP", "Device Type",
                    "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"],
                tablefmt="fancy_grid",
                disable_numparse=True
            ))
        else:
            headers = [
                "Iteration", "Total Iterations", "IP", "Device Type",
                "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"]
            print("\t".join(headers))
            for row in table_data:
                print("\t".join(str(item) for item in row))

        if missing_ips:
            print(f"[NOTE] No data received for iteration {current_iter} from: {', '.join(missing_ips)} (filled with N/A)")
        print("=" * 158)

    def write_robot_results_to_csv(self, test_number, csv_file):
        """Write robot-assisted test results to CSV file with robot metadata.

        Args:
            test_number (int): Current robot test iteration number
            csv_file (str): Path to CSV file for storing results
        """

        csv_exists = os.path.isfile(csv_file)
        csv_data = []
        table_data = []

        # Normalize keys we received this test
        received = {}
        for raw_ip, data in self.result_json.items():
            ip = raw_ip.replace('_', '.')
            received[ip] = {
                "download": data.get("download", "N/A"),
                "upload": data.get("upload", "N/A"),
                "Idle Latency": data.get("Idle Latency", "N/A"),
                "Download Latency": data.get("Download Latency", "N/A"),
                "Upload Latency": data.get("Upload Latency", "N/A"),
            }

        # Expected devices
        expected_ips = list(self.ip_hostname.keys()) or list(self.device_info.keys())

        # Emit rows for devices
        for ip, data in received.items():
            dev_type = self.device_info.get(ip, "N/A")

            download = data["download"]
            upload = data["upload"]
            idle_latency = data["Idle Latency"]
            down_latency = data["Download Latency"]
            up_latency = data["Upload Latency"]

            # Add robot-specific columns
            csv_data.append([
                test_number,
                self.total_robot_tests,
                self.current_coordinate,
                self.current_rotation,
                ip,
                dev_type,
                download,
                upload,
                idle_latency,
                down_latency,
                up_latency,
                "RUNNING"
            ])

            # Add to table data
            table_data.append([
                test_number,
                self.total_robot_tests,
                self.current_coordinate,
                self.current_rotation,
                ip,
                dev_type,
                download,
                upload,
                idle_latency,
                down_latency,
                up_latency,
                "RUNNING"
            ])

        # Handle missing devices
        missing_ips = [ip for ip in expected_ips if ip not in received]
        for ip in missing_ips:
            dev_type = self.device_info.get(ip, "N/A")

            csv_data.append([
                test_number,
                self.total_robot_tests,
                self.current_coordinate,
                self.current_rotation,
                ip,
                dev_type,
                "N/A", "N/A", "N/A", "N/A", "N/A",
                "RUNNING"
            ])
            table_data.append([
                test_number,
                self.total_robot_tests,
                self.current_coordinate,
                self.current_rotation,
                ip,
                dev_type,
                "N/A", "N/A", "N/A", "N/A", "N/A",
                "RUNNING"
            ])

        # Append to CSV
        with open(csv_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not csv_exists:
                writer.writerow([
                    "Robot Test Number", "Total Robot Tests", "Coordinate", "Rotation",
                    "IP", "Device Type", "Download", "Upload",
                    "Idle Latency", "Download Latency", "Upload Latency",
                    "Status"
                ])
            writer.writerows(csv_data)

        # Print table
        print(f"\n Robot Speedtest Results for Test #{test_number}")

        if tabulate:
            print(tabulate(
                table_data,
                headers=[
                    "Test#", "Total", "Coordinate", "Rotation", "IP", "Device Type",
                    "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency",
                    "Status"
                ],
                tablefmt="fancy_grid",
                disable_numparse=True
            ))
        else:
            headers = [
                "Test#", "Total", "Coordinate", "Rotation", "IP", "Device Type",
                "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency",
                "Status"
            ]
            print("\t".join(headers))
            for row in table_data:
                print("\t".join(str(item) for item in row))

        if missing_ips:
            print(f"[NOTE] No data received for robot test {test_number} from: {', '.join(missing_ips)}")
        print("=" * 158)

    def store_robot_results_in_iteration_dict(self, test_number):
        """Store robot test results in iteration dictionary for report generation.

        Args:
            test_number (int): Current robot test iteration number
        """

        # Initialize the result_dict for this test
        self.result_dict = {
            'ip': [],
            'hostname': [],
            'download_speed': [],
            'upload_speed': [],
            'download_lat': [],
            'upload_lat': []
        }

        # Process received results
        received = {}
        for raw_ip, data in self.result_json.items():
            ip = raw_ip.replace('_', '.')
            received[ip] = {
                "download": data.get("download", "N/A"),
                "upload": data.get("upload", "N/A"),
                "Idle Latency": data.get("Idle Latency", "N/A"),
                "Download Latency": data.get("Download Latency", "N/A"),
                "Upload Latency": data.get("Upload Latency", "N/A"),
            }

        # Expected devices
        expected_ips = list(self.ip_hostname.keys()) or list(self.device_info.keys())

        # Store data for devices that reported
        for ip, data in received.items():
            # dev_type = self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)

            download = data["download"]
            upload = data["upload"]
            # idle_latency = data["Idle Latency"]
            down_latency = data["Download Latency"]
            up_latency = data["Upload Latency"]

            # Accumulate into per-iter dicts for graphs/tables
            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)

            def _num(x):
                try:
                    # Handles values like "24.2 Mbps" or "114 ms" or "N/A"
                    return float(str(x).split()[0])
                except Exception:
                    return 0.0

            self.result_dict['download_speed'].append(_num(download))
            self.result_dict['upload_speed'].append(_num(upload))
            self.result_dict['download_lat'].append(_num(down_latency))
            self.result_dict['upload_lat'].append(_num(up_latency))

        # Handle missing devices
        missing_ips = [ip for ip in expected_ips if ip not in received]
        for ip in missing_ips:
            self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)

            # For graphs: use zeros so categories & lengths stay aligned
            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)
            self.result_dict['download_speed'].append(0.0)
            self.result_dict['upload_speed'].append(0.0)
            self.result_dict['download_lat'].append(0.0)
            self.result_dict['upload_lat'].append(0.0)

        # Store in iteration_dict using test_number as key
        self.iteration_dict[test_number] = self.result_dict.copy()

    def perform_single_robot_test(self, test_number, csv_file):
        """Execute a single speed test iteration for robot-assisted testing.

        Args:
            test_number (int): Current robot test iteration number
            csv_file (str): Path to CSV file for storing results
        """

        print(f"Starting speed test for robot test #{test_number}")

        self.start_generic()
        print(f"Test started at {self.start_time}")
        time.sleep(50)  # Speedtest duration wait time
        self.stop_generic()
        # time.sleep(20)

        # Wait for posts from all expected devices
        expected_ips = self.get_expected_post_ips()
        deadline = time.time() + 120
        while time.time() < deadline:
            got = [ip for ip in expected_ips if self.has_post_for(ip)]
            if len(got) >= len(expected_ips):
                break
            time.sleep(1)

        # Store results in iteration_dict for report generation
        self.store_robot_results_in_iteration_dict(test_number)

        # Write results with robot metadata
        self.write_robot_results_to_csv(test_number, csv_file)
        self.result_json = {}

    def perform_robot_testing(self, csv_file):
        """Execute robot-assisted testing across all coordinates and rotations.

        Args:
            csv_file (str): Path to CSV file for storing robot test results
        """
        test_count = 0
        # Condition 1: Both coordinates and rotations provided
        if self.rotation_list and self.rotation_list[0] != "":
            for coord in self.coordinate_list:
                coord = coord.strip()
                print(f"Moving to coordinate: {coord}")
                robo_moved, abort = self.robot_obj.move_to_coordinate(coord)

                if robo_moved:
                    for angle in self.rotation_list:
                        pause_coord, test_stopped_by_user = self.robot_obj.wait_for_battery(self.cleanup)
                        if pause_coord:
                            print("Robot battery low. Pausing at current location to charge.")
                            exit(0)

                        # angle = angle.strip()
                        print(f"Rotating to angle: {angle}")
                        robo_rotated = self.robot_obj.rotate_angle(angle)

                        if robo_rotated:
                            test_count += 1
                            self.current_coordinate = coord
                            self.current_rotation = angle
                            self.robot_iteration_count = test_count

                            print(f"Starting robot test {test_count}/{self.total_robot_tests}")
                            print(f"Coordinate: {coord}, Rotation: {angle}")

                            # Perform the speed test
                            self.perform_single_robot_test(test_count, csv_file)
                        else:
                            print(f"Failed to rotate to angle {angle}")
                else:
                    print(f"Failed to move to coordinate {coord}")

        # Condition 2: Only coordinates provided (no rotations)
        else:
            for coord in self.coordinate_list:
                pause_coord, test_stopped_by_user = self.robot_obj.wait_for_battery(self.cleanup)
                if pause_coord:
                    print("Robot battery low. Pausing at current location to charge.")
                    exit(0)

                coord = coord.strip()
                print(f"Moving to coordinate: {coord}")
                robo_moved = self.robot_obj.move_to_coordinate(coord)
                if robo_moved:
                    test_count += 1
                    self.current_coordinate = coord
                    self.current_rotation = "None"  # No rotation
                    self.robot_iteration_count = test_count

                    print(f"Starting robot test {test_count}/{self.total_robot_tests}")
                    print(f"Coordinate: {coord}, Rotation: None")

                    # Perform the speed test
                    self.perform_single_robot_test(test_count, csv_file)
                else:
                    print(f"Failed to move to coordinate {coord}")

        print(f"Completed {test_count} robot tests")

    def change_port_to_ip(self, upstream_port):
        if upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except Exception:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def _start_ingest_server(self):
        """Start Flask server for ingesting speed test results via HTTP POST.

        Creates a local server on port 5050 to receive test results from clients.
        """
        try:
            from flask import Flask, request, jsonify
        except Exception:
            print("[WARN] Flask not installed; ingest disabled.")
            return

        app = Flask(__name__)
        parent = self

        @app.get("/api/health")
        def health():
            return jsonify({"ok": True, "ts": time.time()}), 200

        @app.route("/api/speedtest", methods=["POST"])
        def _ingest():
            try:
                payload = request.get_json(force=True) or {}
                ip = (payload.get("ip") or "").strip()
                host = payload.get("hostname")
                key = ip.replace('.', '_') if ip else (payload.get("device_id") or payload.get("serial"))
                rec = {
                    "download": f"{payload.get('download_mbps', '0')} Mbps",
                    "upload": f"{payload.get('upload_mbps', '0')} Mbps",
                    "Idle Latency": f"{payload.get('idle_ms', '0')} ms",
                    "Download Latency": f"{payload.get('download_latency_ms', '0')} ms",
                    "Upload Latency": f"{payload.get('upload_latency_ms', '0')} ms",
                    "source": "ingest"
                }

                print('[POST] got payload for key:', key, rec)
                with parent._ingest_lock:
                    parent.result_json[key] = rec
                    if ip and host:
                        parent.ip_hostname[ip] = host
                print("[INGEST] stored under key:", key)
                print('Current result_json:', parent.result_json)
                return jsonify({"stored": True}), 200
            except Exception as e:
                return jsonify({"stored": False, "error": str(e)}), 400

        @app.get("/api/data")
        def data():
            return jsonify(parent.result_json), 200

        def run():
            # IMPORTANT: bind to all interfaces
            app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)

        import threading
        self._flask_thread = threading.Thread(target=run, daemon=True)
        self._flask_thread.start()

    def _ssh_connect(self, host, username, password):
        """Establish SSH connection to remote host.

        Args:
            host (str): Remote host IP address or hostname
            username (str): SSH username
            password (str): SSH password

        Returns:
            paramiko.SSHClient: Connected SSH client object
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        return ssh

    def get_device_data(self, resource_data):
        """
        get_devices_data: Properly collect device data for all compatible devices
        """
        resource_ids = set(resource_data.keys())
        ports = self.json_get('/ports/all').get('interfaces', [])
        adb_devices_list = self.json_get('/adb/all')

        adb_by_resource = {}
        devices = adb_devices_list.get("devices", {})

        # Process ADB devices
        if isinstance(devices, list):
            for dev in devices:
                if not isinstance(dev, dict):
                    continue
                key = next(iter(dev))
                info = dev[key]
                rid = info.get("resource-id")
                if rid:
                    adb_by_resource[rid] = {
                        'name': info.get('name'),
                        'serial': info.get('name') or '',
                        'shelf_resource': (info.get('name') or '').rsplit('.', 1)[0] if '.' in (info.get('name') or '') else '',
                        'user_name': info.get('user-name'),
                        'wifi_mac': info.get('wifi mac'),
                        'device_type': info.get('device-type', 'Android'),
                        # 'ssid': info.get('ssid_rpt') or info.get('ssid', ''),
                        # 'channel': info.get('freq', '')
                    }
        elif isinstance(devices, dict):
            rid = devices.get("resource-id")
            if rid:
                adb_by_resource[rid] = {
                    'name': devices.get('name'),
                    'serial': devices.get('name') or '',
                    'shelf_resource': (devices.get('name') or '').rsplit('.', 1)[0] if '.' in (devices.get('name') or '') else '',
                    'user_name': devices.get('user-name'),
                    'wifi_mac': devices.get('wifi mac'),
                    'device_type': devices.get('device-type', 'Android'),
                    # 'ssid': devices.get('ssid_rpt') or devices.get('ssid', ''),
                    # 'channel': devices.get('freq', '')
                }

        devices_data = {}

        # First, collect all ports for each resource to find the best port for each device
        resource_ports = {}
        for pds in ports:
            port_id = next(iter(pds))
            pdata = pds[port_id]

            parts = port_id.split('.')
            if len(parts) < 3:
                continue

            resource = '.'.join(parts[:2])  # e.g., '1.5'

            # Only process ports belonging to selected resources
            if resource not in resource_ids:
                continue

            if resource not in resource_ports:
                resource_ports[resource] = []

            resource_ports[resource].append((port_id, pdata))

        # Now process each selected resource
        for resource_id in resource_ids:
            res = resource_data.get(resource_id, {})
            if not res:
                continue

            dev_type = res.get('device type', '').strip()
            ctrl_ip = res.get('ctrl-ip')
            box_hostname = res.get('hostname')

            # Skip if no control IP
            if not ctrl_ip:
                continue

            # Determine if this is a compatible device
            compatible_devices = ['Linux/Interop', 'Windows', 'Mac OS', 'Android']
            if dev_type not in compatible_devices:
                continue

            # For Android devices
            if dev_type == 'Android':
                adb_info = adb_by_resource.get(resource_id)
                if adb_info:
                    serial_key = adb_info.get('serial', '').split('.')[-1] if '.' in adb_info.get('serial', '') else adb_info.get('serial', '')
                    if serial_key:
                        devices_data[serial_key] = {
                            'device type': 'Android',
                            'cmd': None,
                            'ip': ctrl_ip,
                            'port': adb_info.get('shelf_resource', resource_id),
                            'serial': serial_key,
                            'hostname': adb_info.get('user_name') or res.get('hostname') or box_hostname,
                            # 'ssid': adb_info.get('ssid', ''),
                            # 'channel': str(adb_info.get('channel', '')),
                            'mac': adb_info.get('wifi_mac', ''),
                        }

                        if ctrl_ip and adb_info.get('user_name'):
                            self.ip_hostname[ctrl_ip] = adb_info['user_name']

            # For laptop devices
            else:
                # Find the best port for this device
                best_port = None
                best_port_data = None

                if resource_id in resource_ports:
                    for port_id, pdata in resource_ports[resource_id]:
                        # Skip phantom or down ports
                        if pdata.get('phantom', True) or pdata.get('down', True):
                            continue

                        # Check if port has IP
                        interface_ip = pdata.get('ip')
                        if not interface_ip or interface_ip == '0.0.0.0':
                            continue

                        # Prefer WLAN ports for laptops
                        port_type = pdata.get('port type', '')
                        if 'WIFI' in port_type or 'wlan' in port_id.lower():
                            best_port = port_id
                            best_port_data = pdata
                            break  # Prefer WiFi over Ethernet
                        elif not best_port:  # If no WiFi found, take first Ethernet
                            best_port = port_id
                            best_port_data = pdata

                if best_port and best_port_data:
                    interface_ip = best_port_data.get('ip')

                    # Extract SSID and channel
                    # ssid = best_port_data.get('ssid', '')
                    # channel_raw = best_port_data.get('channel', '')

                    devices_data[best_port] = {
                        'device type': dev_type,
                        'cmd': None,
                        'ip': interface_ip,
                        'serial': None,
                        'hostname': box_hostname,
                        # 'ssid': ssid,
                        # 'channel': channel,
                        'mac': best_port_data.get('mac', ''),
                        'port': resource_id,
                    }

                    # For reporting lookups
                    # if ctrl_ip and box_hostname:
                    #     self.ip_hostname[ctrl_ip] = box_hostname
                    if interface_ip and box_hostname:
                        self.ip_hostname[interface_ip] = box_hostname

                    # Store device info for reporting
                    self.device_info[interface_ip] = dev_type

        self.devices_data = devices_data
        # print(f"DEBUG: Found {len(devices_data)} devices in devices_data")
        for key, value in devices_data.items():
            print(f" {key}: {value}", end="\n\n")

        return devices_data

    def filter_devices(self, resources_list):
        """Filter LANforge resources to include only compatible device types."""
        resource_data = {}
        for resource_data_dict in resources_list:
            resource_id = list(resource_data_dict.keys())[0]
            resource_data_dict = resource_data_dict[resource_id]

            # More flexible device type matching
            dev_type = resource_data_dict.get('device type', '').strip()
            compatible_types = ['Linux/Interop', 'Windows', 'Mac OS', 'Android',
                                'Linux', 'Mac', 'Ubuntu', 'Windows 10', 'Windows 11']

            # Check if device type contains any compatible string
            if any(compat_type in dev_type for compat_type in compatible_types):
                resource_data[resource_id] = resource_data_dict

        return resource_data

    def get_resource_data(self):
        """Retrieve and select device resources from LANforge controller.

        Prompts user for device selection if device_list is not pre-configured.
        """
        resources_list = self.json_get("/resource/all")["resources"]
        resource_data = self.filter_devices(resources_list)

        headers = ["Index", "Resource ID", "Hostname", "IP", "Device Type"]
        rows = []
        resource_keys = list(resource_data.keys())

        for i, res_id in enumerate(resource_keys):
            res = resource_data[res_id]
            self.device_info[res.get("ctrl-ip", "N/A")] = res.get("device type", "N/A")
            rows.append([
                i,
                res_id,
                res.get("hostname", "N/A"),
                res.get("ctrl-ip", "N/A"),
                res.get("device type", "N/A"),
            ])

        if self.device_list:
            selected_ids = [x.strip() for x in self.device_list.split(',') if x.strip()]
        else:
            print("\n Available Devices:")
            if tabulate:
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid", disable_numparse=True))
            else:
                # Print table without using tabulate
                print("\t".join(headers))
                for row in rows:
                    print("\t".join(str(item) for item in row))

            selection = input("\n> Enter ports of devices to run speedtest on (comma-separated): ")
            selected_ids = [str(i.strip()) for i in selection.split(',')]

        self.selected_resources = {res_id: resource_data[res_id] for res_id in selected_ids}

        for eid, dev in self.selected_resources.items():
            if dev.get("phantom") is True:
                print(f"ERROR: Selected device {eid} ({dev.get('hostname', 'unknown')}) is in PHANTOM state")
                sys.exit(1)

        # Collect device data for selected resources
        self.get_device_data(self.selected_resources)

        if self.devices_data:
            for device_key, dev in self.devices_data.items():
                dev_type = dev.get('device type', '').strip()
                ip_address = dev.get('ip', '')

                if not ip_address:
                    print(f"Warning: No IP address for device {device_key}")
                    continue

                # Build command based on device type
                if dev_type == 'Android':
                    serial = dev.get('serial')
                    if serial:
                        dev['cmd'] = (
                            f"python3 ookla.py --type adb --adb_devices {serial}"
                            # f"{' --post_url ' + self._post_url if self._post_url else ''}"
                            f" --post_url http://{self.manager_ip}:5050/api/speedtest"
                            f" --ip {ip_address}"
                        )
                else:
                    # For laptop devices
                    if 'Linux' in dev_type:
                        port_name = device_key.split('.')[-1] if '.' in device_key else device_key
                        dev['cmd'] = (
                            f"DISPLAY=:1 ./vrf_exec.bash {port_name} python3 ookla.py --type {self.type}"
                            f"{' --post_url ' + self._post_url if self._post_url else ''}"
                            f" --ip {ip_address}"
                        )
                    elif 'Windows' in dev_type:
                        dev['cmd'] = (
                            f"py ookla.py --type {self.type}"
                            f"{' --post_url ' + self._post_url if self._post_url else ''}"
                            f" --ip {ip_address}"
                        )
                    elif 'Mac' in dev_type:
                        dev['cmd'] = (
                            f"python3 ookla.py --type {self.type}"
                            f"{' --post_url ' + self._post_url if self._post_url else ''}"
                            f" --ip {ip_address}"
                        )
                    else:
                        # Default command for other devices
                        dev['cmd'] = (
                            f"python3 ookla.py --type {self.type}"
                            f"{' --post_url ' + self._post_url if self._post_url else ''}"
                            f" --ip {ip_address}"
                        )
        else:
            print(" No compatible devices found.")

        print("\n Final Device Commands for Speedtest")
        self.android_data = {
            k: v
            for k, v in self.devices_data.items()
            if v.get('device type', '').lower() == 'android'
        }

        self.laptop_data = {
            k: v
            for k, v in self.devices_data.items()
            if v.get('device type', '').lower() != 'android'
        }

        print('android_data :=', self.android_data)
        print('laptop_data :=', self.laptop_data)

    def start_generic(self):
        """Start all generic endpoint connections for speed testing."""
        print(f'genCX started at : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.generic_endps_profile.start_cx()
        self.start_time = datetime.now()

    def stop_generic(self):
        """Stop all generic endpoint connections for speed testing."""
        self.generic_endps_profile.stop_cx()
        self.stop_time = datetime.now()

    def get_results(self):
        """Retrieve speed test results from LANforge generic endpoints.

        Returns:
            dict: Speed test results from all endpoints
        """
        logging.debug(self.generic_endps_profile.created_endp)
        results = self.json_get(
            "/generic/{}".format(','.join(self.generic_endps_profile.created_endp)))
        if (len(self.generic_endps_profile.created_endp) > 1):
            results = results['endpoints']
        else:
            results = results['endpoint']
        return (results)

    def start_specific(self, cx_list):
        """Start specific endpoint connections for testing.

        Args:
            cx_list (list): List of connection names to start
        """
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if len(cx_list) > 0:
            for cx in cx_list:
                req_url = "cli-json/set_cx_report_timer"
                data = {
                    "test_mgr": "all",
                    "cx_name": cx,
                    "milliseconds": 1000
                }
                self.json_post(req_url, data)
        for cx_name in cx_list:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=True)

    def stop_specific(self, cx_list):
        """Stop specific endpoint connections.

        Args:
            cx_list (list): List of connection names to stop
        """
        logging.info("Stopping specific CXs...")
        for cx_name in cx_list:
            if self.debug:
                logging.debug("cx-name: {cx_name}".format(cx_name=cx_name))
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }, debug_=self.debug)

    def create(self):
        """Create generic endpoints and connections for all selected devices.

        Configures both laptop and Android devices for speed testing.
        """
        # Determine device types for all selected devices
        device_types = [device['device type'] for device in self.laptop_data.values()]

        # Create generic endpoints for laptop devices
        if self.laptop_data:
            self.generic_endps_profile.create(ports=list(self.laptop_data.keys()), real_client_os_types=device_types)

        for endp_name in self.generic_endps_profile.created_endp:
            self.generic_endps_profile.set_cmd(endp_name, cmd=self.laptop_data[endp_name.split('-')[1]]['cmd'])

        # Create generic endpoints for Android devices
        if self.android_data:
            self.android_data = {
                f"{v['port']}.{k}": v
                for k, v in self.android_data.items()
            }
            status, created_cx, created_endp = self.create_android(ports=list(self.android_data.keys()), real_client_os_types=device_types)
            self.generic_endps_profile.created_endp.extend(created_endp)
            self.generic_endps_profile.created_cx.extend(created_cx)

            for endp_name in created_endp:
                self.generic_endps_profile.set_cmd(endp_name, cmd=self.android_data[(endp_name.split('-')[1]).replace('_', '.')]['cmd'])

        print(self.generic_endps_profile.created_endp)
        print(self.generic_endps_profile.created_cx)

    def create_android(self, ports=None, sleep_time=.5, debug_=False, suppress_related_commands_=None, real_client_os_types=None):
        """Create generic endpoints specifically for Android devices.

        Args:
            ports (list, optional): List of Android port names
            sleep_time (float, optional): Delay between operations in seconds
            debug_ (bool, optional): Enable debug mode
            suppress_related_commands_ (bool, optional): Suppress command output
            real_client_os_types (list, optional): List of client OS types

        Returns:
            tuple: (success, created_cx_list, created_endp_list)
        """
        if ports and real_client_os_types and len(real_client_os_types) == 0:
            logging.error('Real client operating systems types is empty list')
            raise ValueError('Real client operating systems types is empty list')
        created_cx = []
        created_endp = []

        if not ports:
            ports = []

        if self.debug:
            debug_ = True

        post_data = []
        endp_tpls = []
        # Create endpoint templates
        for port_name in ports:
            port_info = self.name_to_eid(port_name)
            resource = port_info[1]
            shelf = port_info[0]
            if real_client_os_types:
                name = port_name
            else:
                name = port_info[2]

            gen_name_a = "%s-%s" % ('generic', '_'.join(port_name.split('.')))
            endp_tpls.append((shelf, resource, name, gen_name_a))

        print('endp_tpls', endp_tpls)
        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            if real_client_os_types:
                name = endp_tpl[2].split('.')[2]
            else:
                name = endp_tpl[2]
            gen_name_a = endp_tpl[3]

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": resource,
                "port": 'eth0',
                "type": "gen_generic"
            }
            # print('Adding endpoint ', data)
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
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a
            }
            post_data.append(data)
            created_cx.append(cx_name)
            created_endp.append(gen_name_a)

        for data in post_data:
            url = "/cli-json/add_cx"
            # print('Adding cx', data)
            self.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            # time.sleep(2)
        if sleep_time:
            time.sleep(sleep_time)

        for data in post_data:
            self.json_post("/cli-json/show_cx", {
                "test_mgr": "default_tm",
                "cross_connect": data["alias"]
            })
        return True, created_cx, created_endp

    def add_live_view_images_to_report(self, report):
        """Add live view heatmap images to the test report.

        Args:
            report (lf_report): Report object to add images to
        """
        if self.robot_test:
            self.total_floors = 1

        for floor in range(0, int(self.total_floors)):

            image_paths = {
                'download_speed': os.path.join(self.result_dir, "live_view_images", f"{self.instance}_download_speed_floor_{floor + 1}.png"),
                'upload_speed': os.path.join(self.result_dir, "live_view_images", f"{self.instance}_upload_speed_floor_{floor + 1}.png"),
                'download_latency': os.path.join(self.result_dir, "live_view_images", f"{self.instance}_download_latency_floor_{floor + 1}.png"),
                'upload_latency': os.path.join(self.result_dir, "live_view_images", f"{self.instance}_upload_latency_floor_{floor + 1}.png")
            }

            # Titles for each heatmap type
            titles = {
                'download_speed': f'Floor {floor + 1} - Download Speed Heatmap',
                'upload_speed': f'Floor {floor + 1} - Upload Speed Heatmap',
                'download_latency': f'Floor {floor + 1} - Download Latency Heatmap',
                'upload_latency': f'Floor {floor + 1} - Upload Latency Heatmap'
            }

            # Wait for all images to be available (with timeout)
            timeout = 150  # seconds
            start_time = time.time()

            print(f"Looking for images for floor {floor + 1}:")
            for img_type, path in image_paths.items():
                print(f"  {img_type}: {path}")

            # Wait for ALL images for this floor to be available
            while True:
                all_exist = all(os.path.exists(path) for path in image_paths.values())
                if all_exist:
                    print(f"All images for floor {floor + 1} found")
                    break

                if time.time() - start_time > timeout:
                    print(f"Timeout: Not all images found for floor {floor + 1} within {timeout} seconds")
                    for img_type, path in image_paths.items():
                        if not os.path.exists(path):
                            print(f"  Missing: {img_type} - {path}")
                    break

                time.sleep(5)

            for img_type, image_path in image_paths.items():
                if os.path.exists(image_path):
                    # Add page break before each image (except first)
                    report.set_custom_html('<div style="page-break-before: always;"></div>')
                    report.build_custom()

                    # Add title for the heatmap
                    if img_type in titles:
                        report.set_custom_html(f'<h4>{titles[img_type]}</h4>')
                        report.build_custom()

                    # Add the image
                    report.set_custom_html(f'<img src="file://{image_path}" style="max-width: 100%; height: auto;"></img>')
                    report.build_custom()
                    print(f"Added {img_type} heatmap for floor {floor + 1} to report")
                else:
                    print(f"Warning: {img_type} image not found for floor {floor + 1}: {image_path}")

    def cleanup(self):
        """Clean up all created endpoints and connections."""
        self.generic_endps_profile.cleanup()
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []

    def generate_report(self, result_dir_name, do_webgui=False, per_post_timeout=120, poll_interval=2):
        """Generate comprehensive speed test report with graphs and tables.

        Args:
            result_dir_name (str): Directory name for report output
            do_webgui (bool): Whether the test is triggered from WEBGUI
            per_post_timeout (int): Timeout for POST operations in seconds
            poll_interval (int): Interval for polling operations in seconds
        """
        report = lf_report(
            _output_pdf="speedtest.pdf",
            _output_html="speedtest.html",
            _results_dir_name=result_dir_name,
            _path=self.result_dir if self.result_dir is not None else "/home/lanforge/html-reports"
        )
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        os.makedirs(report_path, exist_ok=True)
        os.makedirs(report_path_date_time, exist_ok=True)

        all_ips = set()
        for iter_data in self.iteration_dict.values():
            all_ips.update(iter_data.get("ip", []))

        # build roster with fallback info
        roster = []
        devices_by_ip = {}
        for _key, dev in (self.devices_data or {}).items():
            ip = dev.get("ip")
            if not ip:
                continue
            devices_by_ip[ip] = dev

        for ip in sorted(all_ips):
            d = devices_by_ip.get(ip, {})
            roster.append({
                "ip": ip,
                "hostname": d.get("hostname") or self.ip_hostname.get(ip, ip),
                "device_type": d.get("device type", ""),
                "mac": d.get("mac", ""),
                # "ssid": d.get("ssid", ""),
                # "channel": d.get("channel", "")
            })

        roster.sort(key=lambda r: (str(r["hostname"]), str(r["ip"])))
        device_count = len(roster)

        def wait_for_iteration_posts(iter_idx, expected, timeout_s=per_post_timeout, sleep_s=poll_interval):
            start = time.time()
            while True:
                # how many rows do we have recorded for this iteration?
                iter_block = self.iteration_dict.get(iter_idx, None)
                have = len(iter_block["ip"]) if iter_block and "ip" in iter_block else 0
                if have >= expected:
                    print(f"[WAIT] Iteration {iter_idx}: received {have}/{expected} posts continuing.")
                    return True
                if time.time() - start >= timeout_s:
                    print(f"[WAIT] Iteration {iter_idx}: timed out at {have}/{expected} posts after {timeout_s}s.")
                    return False
                time.sleep(sleep_s)

        try:
            if self.robot_test:
                robot_csv = f'speedtest_results_{self.instance}.csv'
                if os.path.exists(robot_csv):
                    df = pd.read_csv(robot_csv)

                    if 'Status' in df.columns:
                        max_test = df['Robot Test Number'].max()
                        df.loc[df['Robot Test Number'] == max_test, 'Status'] = 'STOPPED'

                    df.to_csv(robot_csv, index=False)
                    shutil.copy(robot_csv, report_path_date_time)
                    print(f"Moved robot CSV: {robot_csv}")
                else:
                    print(f"Robot CSV not found: {robot_csv}")
            else:
                regular_csv = f'speedtest_results_{self.instance}.csv'
                if os.path.exists(regular_csv):
                    shutil.move(regular_csv, report_path_date_time)
                    print(f"Moved regular CSV: {regular_csv}")
                else:
                    print(f"Regular CSV not found: {regular_csv}")
        except Exception as e:
            print(f"[WARN] could not move CSV: {e}")

        if self.robot_test:
            iteration_range = sorted(self.iteration_dict.keys())
        else:
            iteration_range = list(range(1, self.iteration + 1))

        total_iterations = len(iteration_range)

        report_title = "Robot Speed Test" if self.robot_test else "Speed Test"
        report.set_title(report_title)
        report.build_banner()

        report.set_obj_html(
            _obj_title="Objective",
            _obj=(
                "The Candela Speed Test measures Download/Upload speeds and network latency "
                "to reflect real-world client performance."
            )
        )
        report.build_objective()

        config_data = {
            "Test Name": report_title,
            "Number of Iterations": total_iterations,
            "Number of Devices": device_count,
        }

        if self.robot_test:
            config_data["Coordinates"] = ", ".join(self.coordinate_list)
            config_data["Rotations"] = (
                ", ".join(self.rotation_list)
                if self.rotation_list and self.rotation_list[0] != ""
                else "None"
            )

        report.test_setup_table(config_data, "Configuration")

        if do_webgui:
            self.add_live_view_images_to_report(report)

        per_iter = {}
        rotation_summary = {}
        missing_notes = []

        for iter_idx in iteration_range:

            block = self.iteration_dict.get(iter_idx, {})
            ip_to_idx = {ip: i for i, ip in enumerate(block.get("ip", []))}

            host_list = []
            dls = []
            uls = []
            dlat = []
            ulat = []
            meta = []

            for dev in roster:
                ip = dev["ip"]
                hostname = dev["hostname"]
                meta.append(dev)

                if ip in ip_to_idx:
                    j = ip_to_idx[ip]
                    host_list.append(hostname)
                    dls.append(block["download_speed"][j])
                    uls.append(block["upload_speed"][j])
                    dlat.append(block["download_lat"][j])
                    ulat.append(block["upload_lat"][j])
                else:
                    host_list.append(hostname)
                    dls.append(0.0)
                    uls.append(0.0)
                    dlat.append(0.0)
                    ulat.append(0.0)
                    missing_notes.append(f"Iteration {iter_idx}: No data received for {hostname} (IP {ip}).")

            # store clean iteration data
            per_iter[iter_idx] = {
                "hostnames": host_list,
                "download": dls,
                "upload": uls,
                "download_lat": dlat,
                "upload_lat": ulat,
                "meta": meta
            }
            print('DEBUG', per_iter)

            # robot-only aggregation
            if self.robot_test:
                if self.rotation_list and self.rotation_list[0] != "":
                    coord_idx = (iter_idx - 1) // len(self.rotation_list)
                    rot_idx = (iter_idx - 1) % len(self.rotation_list)
                    coord = self.coordinate_list[coord_idx]
                    rotation = self.rotation_list[rot_idx]
                else:
                    coord_idx = (iter_idx - 1)
                    coord = self.coordinate_list[coord_idx]
                    rotation = "0"

                if rotation not in rotation_summary:
                    rotation_summary[rotation] = {
                        "coords": [],
                        "download": [],
                        "upload": [],
                        "download_lat": [],
                        "upload_lat": []
                    }

                # aggregate averages per iteration
                rotation_summary[rotation]["coords"].append(coord)
                rotation_summary[rotation]["download"].append(sum(dls) / len(dls))
                rotation_summary[rotation]["upload"].append(sum(uls) / len(uls))
                rotation_summary[rotation]["download_lat"].append(sum(dlat) / len(dlat))
                rotation_summary[rotation]["upload_lat"].append(sum(ulat) / len(ulat))

        if self.robot_test:
            # TODO NEED to add heading of rotation
            for rotation, data in rotation_summary.items():
                coords = data["coords"]

                # SPEED GRAPH
                bar = lf_bar_graph(
                    _data_set=[data["download"], data["upload"]],
                    _xaxis_categories=coords,
                    _xaxis_name="Coordinates",
                    _yaxis_name="Speed (Mbps)",
                    _graph_image_name=f"rotation_{rotation}_speed",
                    _label=["Download", "Upload"],
                    _show_bar_value=True,
                )
                png = bar.build_bar_graph()
                if png:
                    report.set_graph_image(png)
                    report.move_graph_image()
                    report.build_graph()

                # LATENCY GRAPH
                bar2 = lf_bar_graph(
                    _data_set=[data["download_lat"], data["upload_lat"]],
                    _xaxis_categories=coords,
                    _xaxis_name="Coordinates",
                    _yaxis_name="Latency (ms)",
                    _graph_image_name=f"rotation_{rotation}_latency",
                    _label=["Download Latency", "Upload Latency"],
                    _show_bar_value=True,
                )
                png2 = bar2.build_bar_graph()
                if png2:
                    report.set_graph_image(png2)
                    report.move_graph_image()
                    report.build_graph()

            for iter_idx in iteration_range:

                block = per_iter[iter_idx]

                if not self.robot_test:
                    report.set_table_title(f"Iteration {iter_idx} - Per-Client Speed")
                    report.build_table_title()

                g = lf_bar_graph(
                    _data_set=[block["download"], block["upload"]],
                    _xaxis_categories=block["hostnames"],
                    _xaxis_name="Device",
                    _yaxis_name="Speed (Mbps)",
                    _graph_image_name=f"iter_{iter_idx}_speed",
                    _label=["Download", "Upload"],
                    _show_bar_value=True
                )
                png = g.build_bar_graph()
                if png:
                    report.set_graph_image(png)
                    report.move_graph_image()
                    report.build_graph()

                report.set_table_title(f"Iteration {iter_idx} - Per-Client Latency")
                report.build_table_title()

                g2 = lf_bar_graph(
                    _data_set=[block["download_lat"], block["upload_lat"]],
                    _xaxis_categories=block["hostnames"],
                    _xaxis_name="Device",
                    _yaxis_name="Latency (ms)",
                    _graph_image_name=f"iter_{iter_idx}_latency",
                    _label=["Download Latency", "Upload Latency"],
                    _show_bar_value=True
                )
                png2 = g2.build_bar_graph()
                if png2:
                    report.set_graph_image(png2)
                    report.move_graph_image()
                    report.build_graph()

                # Table
                table_df = pd.DataFrame({
                    "Hostname": block["hostnames"],
                    "Download (Mbps)": block["download"],
                    "Upload (Mbps)": block["upload"],
                    "Download Lat (ms)": block["download_lat"],
                    "Upload Lat (ms)": block["upload_lat"],
                })

                report.set_table_title(f"Iteration {iter_idx} - Device Data")
                report.build_table_title()
                report.set_table_dataframe(table_df)
                report.build_table()

        else:
            missing_notes_all = []
            print('ROSTER:', roster)
            for iter_idx in iteration_range:
                print('Iteration DATA:', self.iteration_dict)

                # Wait until we have m rows or timing out
                wait_for_iteration_posts(iter_idx, expected=device_count)

                iter_block = self.iteration_dict.get(iter_idx, {
                    'ip': [], 'hostname': [], 'download_speed': [], 'upload_speed': [], 'download_lat': [], 'upload_lat': []
                })

                ip_to_idx = {ip: i for i, ip in enumerate(iter_block.get('ip', []))}

                hostnames = []
                dls = []
                uls = []
                dlat = []
                ulat = []

                t_hostname = []
                t_mac = []
                # t_ssid = []
                # t_channel = []
                t_type = []

                for dev in roster:
                    ip = dev["ip"]
                    host = dev["hostname"]
                    t_hostname.append(host)
                    t_mac.append(dev["mac"])
                    # t_ssid.append(dev["ssid"])
                    # t_channel.append(dev["channel"])
                    t_type.append(dev["device_type"])

                    if ip in ip_to_idx:
                        j = ip_to_idx[ip]
                        hostnames.append(host or ip)
                        dls.append(iter_block['download_speed'][j])
                        uls.append(iter_block['upload_speed'][j])
                        dlat.append(iter_block['download_lat'][j])
                        ulat.append(iter_block['upload_lat'][j])
                    else:
                        host_label = host or ip or "(unknown)"
                        hostnames.append(host_label)
                        dls.append(0.0)
                        uls.append(0.0)
                        dlat.append(0.0)
                        ulat.append(0.0)
                        missing_notes_all.append(
                            f"Iteration {iter_idx}: no POST received for device {host_label} (IP {ip or 'N/A'}); row filled with NA/0."
                        )

                if not hostnames or not dls:
                    print(f"Warning: No data for iteration {iter_idx}, skipping graphs")
                    continue

                # ---- Graphs ----
                report.set_table_title('Per-Client Speed (Download & Upload)')
                report.build_table_title()
                if hostnames and dls and uls:
                    graph = lf_bar_graph(
                        _data_set=[dls, uls],
                        _xaxis_name="Device Name",
                        _yaxis_name="Speed (in Mbps)",
                        _xaxis_categories=hostnames,
                        _graph_image_name=f"Download_upload_speed_iter_{iter_idx}",
                        _label=["Download", "Upload"],
                        _color=None,
                        _color_edge='red',
                        _show_bar_value=True,
                        _text_font=7,
                        _text_rotation=None,
                        _figsize=(12, 10),
                        _xticks_rotation=30,
                        _enable_csv=True
                    )
                    report.set_graph_image(graph.build_bar_graph())
                    report.move_graph_image()
                    report.build_graph()

                    report.set_table_title('Per-Client Latency (Download & Upload)')
                    report.build_table_title()
                    graph2 = lf_bar_graph(
                        _data_set=[dlat, ulat],
                        _xaxis_name="Device Name",
                        _yaxis_name="Latency (in ms)",
                        _xaxis_categories=hostnames,
                        _graph_image_name=f"Download_upload_Latency_iter_{iter_idx}",
                        _label=["Download", "Upload"],
                        _color=None,
                        _color_edge='red',
                        _show_bar_value=True,
                        _text_font=7,
                        _text_rotation=None,
                        _figsize=(12, 10),
                        _xticks_rotation=30,
                        _enable_csv=True
                    )
                    report.set_graph_image(graph2.build_bar_graph())
                    report.move_graph_image()
                    report.build_graph()

                test_input_info = {
                    # "IP": [dev["ip"] for dev in roster],  # Uncomment for IP column
                    "hostname": t_hostname,
                    "MAC": t_mac,
                    "Device Type": t_type,
                    # "SSID": t_ssid,
                    # "Channel": t_channel,
                    "Download Speed (Mbps)": dls,
                    "Upload Speed (Mbps)": uls,
                    "Download Latency (ms)": dlat,
                    "Upload Latency (ms)": ulat,
                }

                report.set_table_title(f'<b>Device Data (Iteration {iter_idx})</b>')
                report.build_table_title()
                for k, v in test_input_info.items():
                    print(f" {k}  : {v} ")

                report.set_table_dataframe(pd.DataFrame(test_input_info))
                report.build_table()

        if missing_notes:
            report.set_obj_html("Notes", "<br>".join(missing_notes))
            report.build_objective()

        # DONE
        report.build_footer()
        report.write_html()
        report.write_pdf(_orientation="Landscape")
        print(f"[REPORT COMPLETE] Files stored in: {report_path_date_time}")


def main():
    help_summary = '''\
        The Candela Speed Test evaluates Access Point (AP) performance under real-world conditions by measuring key network metrics such as latency, download speed, and upload speed.
        This test reflects true end-user experience in typical deployment environments.

        Supported platforms and test methods:
        - Laptops (Linux, Windows, macOS): Browser-based automation (Selenium)
        - Android devices: ADB/app-based automation

        Key metrics collected:
        - Download Speed
        - Upload Speed
        - Download Latency
        - Upload Latency

    '''

    parser = argparse.ArgumentParser(
        prog="lf_interop_speedtest.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Provides the list of available client devices and allows the user to perform speed testing
            on selected devices.
        ''',
        description='''\
            NAME: lf_interop_speedtest.py

            PURPOSE:
                The lf_interop_speedtest.py script enables real-world WiFi speed testing for laptop-based clients
                (Linux, Windows, macOS) and Android mobile devices. iOS is not supported.

                Instead, it focuses on measuring actual end-user experience by capturing metrics such as download/upload speed,
                latency (ping). The script uses the Speedtest.net service (via browser automation for laptops) to run the tests.

            TO PERFORM SPEED TEST:

                EXAMPLE-1:
                    Run a default speed test using browser-based automation (Selenium)
                    ./lf_interop_speedtest.py \
                        --mgr 192.168.204.74 \
                        --device_list 1.10,1.12 \
                        --instance_name SAMPLE_TEST \
                        --iteration 1 \
                        --upstream_port eth2 \
                        --cleanup

                EXAMPLE-2:
                    Run speed test on robot with each coordinate and rotation
                    ./lf_interop_speedtest.py \
                        --mgr 192.168.204.75 \
                        --device_list 1.10,1.12 \
                        --instance_name SAMPLE_TEST \
                        --iteration 1 \
                        --robot_test \
                        --coordinate 1,2 \
                        --rotation 0,90 \
                        --robot_ip 127.0.0.1:5000 \
                        --upstream_port eth2 \
                        --cleanup

                EXAMPLE-3:
                    Run speed test on robot with each coordinate without rotation
                    ./lf_interop_speedtest.py \
                        --mgr 192.168.204.75 \
                        --device_list 1.10,1.12 \
                        --instance_name SAMPLE_TEST \
                        --iteration 1 \
                        --robot_test \
                        --coordinate 1,2 \
                        --robot_ip 127.0.0.1:5000 \
                        --upstream_port eth2 \
                        --cleanup
            '''
    )

    parser = argparse.ArgumentParser(
        prog='interop_speedtest.py',
        formatter_class=argparse.RawTextHelpFormatter)
    optional = parser.add_argument_group('Optional arguments')

    # optional arguments
    optional.add_argument(
        '--mgr',
        type=str,
        help='hostname where LANforge GUI is running',
        default='localhost')

    optional.add_argument(
        '--device_list',
        type=str,
        help='Mention device list (comma seperated)',
    )

    optional.add_argument(
        '--instance_name',
        type=str,
        default='Speed_Test_report',
        help='Mention Test Instance name (report folder name)',
    )

    optional.add_argument(
        '--upstream_port',
        type=str,
        help='Upstream port IP for clients to POST results (e.g., AP/router IP)',
        default=None
    )

    optional.add_argument(
        '--iteration',
        type=int,
        default=1,
        help='Mention number of iterations for the test.',
    )

    optional.add_argument(
        '--do_interopability',
        action='store_true',
        help='Ensures test on devices run sequentially')

    optional.add_argument(
        '--result_dir',
        type=str,
        default='results',
        help='Directory to store test results')

    optional.add_argument(
        '--type',
        choices=['cli', 'ookla'],
        default='ookla',
        help='Type of speed test to perform (cli, ookla)')

    optional.add_argument(
        '--cleanup',
        action='store_true',
        help='cleans up generic cx after completion of the test')

    optional.add_argument(
        '--robot_test',
        help='to trigger robot test',
        action='store_true')

    optional.add_argument(
        '--do_webgui',
        help='mention if the test is triggered from WEBGUI',
        action='store_true')

    optional.add_argument(
        '--robot_ip',
        type=str,
        default='localhost',
        help='hostname for where Robot server is running')

    optional.add_argument(
        '--coordinate',
        type=str,
        default=None,
        help="The coordinate contains list of coordinates to be ")

    optional.add_argument(
        '--rotation',
        type=str,
        default=None,
        help="The set of angles to rotate at a particular point")

    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    csv_file = f"speedtest_results_{args.instance_name}.csv"

    speedtest_obj = SpeedTest(
        manager_ip=args.mgr,
        device_list=args.device_list,
        instance=args.instance_name,
        iteration=args.iteration,
        do_interopability=args.do_interopability,
        result_dir=args.result_dir,
        type=args.type,
        robot_test=args.robot_test,
        robot_ip=args.robot_ip,
        coordinate=args.coordinate,
        rotation=args.rotation,
        upstream_port=args.upstream_port)

    speedtest_obj.get_resource_data()
    speedtest_obj.create()

    if args.robot_test:
        csv_file = f"speedtest_results_{args.instance_name}.csv"
        print(f"Starting robot testing with {speedtest_obj.total_robot_tests} total tests")
        speedtest_obj.perform_robot_testing(csv_file)

    else:
        for iter in range(1, args.iteration + 1):
            print(f"\n Starting Iteration {iter} of {args.iteration}")

            speedtest_obj.start_generic()
            print(f"Test started at {speedtest_obj.start_time}")
            time.sleep(50)  # Speedtest duration wait time.
            speedtest_obj.stop_generic()
            time.sleep(20)

            # Wait until we have received posts from all expected devices (or timeout)
            def expected_post_ips(devices):
                want = []
                for info in devices.values():
                    cmd = (info.get('cmd') or '')
                    ip = (info.get('ip') or '')
                    if ip and '--post_url' in cmd:
                        want.append(ip)
                # de-dup (stable)
                seen, out = set(), []
                for ip in want:
                    if ip not in seen:
                        seen.add(ip)
                        out.append(ip)
                return out

            def has_post_for(ip):
                k = ip.replace('.', '_')
                # ookla.py posts using this exact key format
                return (k in speedtest_obj.result_json) or (ip in speedtest_obj.result_json)

            expected_ips = expected_post_ips(speedtest_obj.devices_data)
            deadline = time.time() + 120
            while time.time() < deadline:
                got = [ip for ip in expected_ips if has_post_for(ip)]
                if len(got) >= len(expected_ips):
                    break
                time.sleep(1)

            # Finally, write results for this iteration
            speedtest_obj.write_results_to_csv(iter, csv_file)

            time.sleep(5)   # TODO: Hardcoded wait time to allow all devices to be ready for next iteration.
            speedtest_obj.result_json = {}

    if args.cleanup:
        speedtest_obj.cleanup()

    speedtest_obj.generate_report(result_dir_name=args.instance_name, do_webgui=args.do_webgui)


if __name__ == "__main__":
    main()
