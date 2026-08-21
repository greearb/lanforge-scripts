#!/usr/bin/env python3
"""
NAME: lf_interop_port_reset_test.py

PURPOSE:
         The LANforge interop port reset test enables users to use real Wi-Fi stations and connect them to the
         Access Point (AP) being tested. It then disconnects and reconnects a given number of stations at
         different time intervals. This test helps evaluate how well the AP handles a dynamic and busy network environment
         with devices joining and leaving the network at random times.

EXAMPLE:
        # To run port-reset test on specified real devices (android, laptops)

            ./lf_interop_port_reset_test.py --lanforge_ip 192.168.200.192 --upstream_port 192.168.1.161 --dut TestDut --ssid OpenWifi
            --passwd OpenWifi --encryp psk2 --iterations 10 --reset_interval 5 --android_releases 11

        # To run port-reset test on specified real devices with only coordinates

            ./lf_interop_port_reset_test.py --lanforge_ip 192.168.207.78 --upstream_port eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --iterations 2 --reset_interval 5 --robot_test --coordinate 4,3  --robot_ip 192.168.200.169 --device_list ubuntu24

        # To run port-reset test on specified real devices with only coordinates and rotations

            ./lf_interop_port_reset_test.py --lanforge_ip 192.168.207.78 --upstream_port eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --iterations 2 --reset_interval 5 --robot_test --coordinate 4,3 --rotation 30,45 --robot_ip 192.168.200.169 --device_list ubuntu24

SCRIPT_CLASSIFICATION:  Toggling, Report Generation, Each Reset Wi-Fi Messages

SCRIPT_CATEGORIES: Interop Port-Reset Test

NOTES:
        The primary objective of this script is to automate the process of toggling Wi-Fi on real devices with the
       InterOp Application, evaluating their performance with an access point. It achieves this by simulating multiple
       Wi-Fi resets as specified by the user.

      * Currently the script will work for the REAL CLIENTS (android with version 11+, laptop devices).

STATUS: Functional

VERIFIED_ON:   28-OCT-2023,
             GUI Version:  5.4.7
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README: False
"""
import json
import sys
import os
import importlib
import argparse
import time
import datetime
# When you use from datetime import datetime, you are making the
# datetime class directly accessible in your code without
# having to prefix it with the module name
from datetime import datetime  # noqa: F811
import pandas as pd
import matplotlib.pyplot as plt
import logging
from lf_base_robo import RobotClass
import asyncio

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
base = importlib.import_module('py-scripts.lf_base_interop_profile')
lf_csv = importlib.import_module("py-scripts.lf_csv")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class InteropPortReset(Realm):
    def __init__(self, lanforge_ip,
                 lanforge_port=8080,
                 dut=None,
                 ssid=None,
                 passwd=None,
                 encryption=None,
                 iterations=None,
                 upstream_port=None,
                 reset_interval_sec=None,
                 device_list=None,
                 android_releases=None,
                 forget_network=True,
                 dowebgui=False,
                 result_dir=None,
                 test_name=None,
                 robot_test=False,
                 robot_ip=None,
                 robot_port=None,
                 coordinate=None,
                 rotation=None,
                 get_live_view=False,
                 total_floors=0,
                 ):
        super().__init__(lfclient_host=lanforge_ip,
                         lfclient_port=8080)
        self.total_connects = []
        self.total_assoc_rejections = []
        self.total_assoc_attempts = []
        self.total_scans = []
        self.total_disconnects = []
        self.total_resets = []
        self.graph_image_name = ""
        self.all_selected_devices = []
        self.all_laptops = []
        self.user_query = []
        self.available_device_list = []
        self.final_selected_android_list = []
        self.adb_device_list = []
        self.windows_list = []
        self.linux_list = []
        self.mac_list = []
        self.encrypt_value = 0
        self.lanforge_ip = lanforge_ip
        self.lanforge_port = lanforge_port
        self.android_serials = []
        self.dut_name = dut
        self.ssid = ssid
        self.passwd = passwd
        self.encryption = encryption
        self.upstream_port = upstream_port
        self.iterations = iterations
        self.reset_interval_sec = reset_interval_sec
        self.device_list = device_list
        self.forget_network = forget_network
        self.result_dir = result_dir
        self.dowebgui = dowebgui
        self.test_name = test_name
        self.result_df = {}
        self.port_reset_data = {}
        self.robot_test = robot_test
        self.coordinate_df = {}
        self.get_live_view = get_live_view
        self.total_floors = total_floors
        self.robo_test_stopped = False
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.coordinate = coordinate
        self.rotation = rotation
        self.rotation_enabled = False
        self.coordinate_list = coordinate.split(',')
        self.rotation_list = rotation.split(',')
        self.current_coordinate = None
        self.current_angle = None
        self.android_releases = android_releases
        self.android_user_names = []
        self.lf_report = lf_report_pdf.lf_report(_path="" if not self.dowebgui else self.result_dir, _results_dir_name="Interop_port_reset_test",
                                                 _output_html="port_reset_test.html",
                                                 _output_pdf="port_reset_test.pdf")
        self.report_path = self.lf_report.get_report_path()

        self.base_interop_profile = base.RealDevice(manager_ip=self.lanforge_ip, server_ip=self.upstream_port, ssid_5g=self.ssid,
                                                    encryption_5g=self.encryption, passwd_5g=self.passwd, disconnect_devices=self.forget_network, reboot=False, selected_bands=["5g"])

        self.utility = base.UtilityInteropWifi(host_ip=self.lanforge_ip)
        # logging.basicConfig(filename='port_reset.log', filemode='w', format='%(asctime)s - %(message)s',
        #                     level=logging.INFO, force=True)

    def json_get_with_retry(self, url, wait_time=40, poll_interval=5, debug_=False):
        """
        Calls self.json_get(url), retrying every poll_interval seconds for up
        to wait_time seconds if LANforge returns no response.
        """
        start_time = time.time()
        response = self.json_get(url, debug_=debug_)
        while response is None and (time.time() - start_time) < wait_time:
            logging.warning(f"GET {url} returned no response from LANforge; retrying...")
            time.sleep(poll_interval)
            response = self.json_get(url, debug_=debug_)

        if response is None:
            logging.error(
                f"GET {url} returned no response from LANforge after waiting "
                f"{wait_time} seconds."
            )

        return response

    def change_port_to_ip(self, upstream_port):
        # Resolves an ethernet port name (e.g. "eth1") to its IP via LANforge, used
        # for --upstream_port. This is only called once, at test start, and we cannot
        # proceed without a resolved manager IP, so retry for a while and then
        # abort instead of silently continuing with an unresolved port name.
        if upstream_port.count('.') != 3:
            shelf, resource, port_name, _ = self.name_to_eid(upstream_port)
            response = self.json_get_with_retry(f'/port/{shelf}/{resource}/{port_name}?fields=ip')
            try:
                upstream_port = response['interface']['ip']
            except (TypeError, KeyError) as e:
                logging.error(
                    f"change_port_to_ip: could not resolve upstream port '{upstream_port}' to an IP; LANforge "
                    f"response is not in expected format ({e}). Data received: {response}")
                logging.critical("Aborting the test: a valid manager IP is required to proceed.")
                exit(1)
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")

        return upstream_port

    def selecting_devices_from_available(self):
        # If device list is not provided by user, then it shows the available devices to choose from
        if self.device_list is None:
            configurable_devices = self.base_interop_profile.query_all_devices_to_configure_wifi()
        else:
            configurable_devices = self.base_interop_profile.query_all_devices_to_configure_wifi(device_list=self.device_list.split(','))
        asyncio.run(self.base_interop_profile.configure_wifi(
            configurable_devices[0] + configurable_devices[1] + configurable_devices[2]))
        self.real_station_list = self.base_interop_profile.station_list
        logger.info(self.real_station_list)
        device_details = self.base_interop_profile.devices_data
        if len(self.real_station_list) == 0:
            logging.error('There are no real devices in this testbed. Aborting the test.')
            # Added for the purpose to stop webui test when there are no selected devices available in lanforge.
            raise RuntimeError("There are no real devices in this testbed. Aborting the test.")
        logging.info(f"{self.real_station_list}")

        for station_name in self.real_station_list:
            if station_name not in device_details:
                logger.error('Real Station not in devices data')
                raise ValueError('Real station not in devices data')
        android_list = self.base_interop_profile.android_list

        self.interop = base.BaseInteropWifi(manager_ip=self.lanforge_ip,
                                            port=self.lanforge_port,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryption,
                                            release=self.android_releases,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        supported_resource_ids = self.interop.supported_devices_resource_id
        print("Supported dict", supported_resource_ids)
        self.final_selected_android_list = []
        for device_name in supported_resource_ids.keys():
            if device_name != "":
                if any(device_name in item for item in android_list):
                    self.final_selected_android_list.append(supported_resource_ids[device_name])
        logging.info(f"Final Android Serial Numbers List: {self.final_selected_android_list}")

    def create_log_file(self, json_list, file_name="empty.json"):
        # Convert the list of JSON values to a JSON-formatted string
        json_string = json.dumps(json_list)
        new_folder = os.path.join(self.report_path, "Wifi_Messages")
        if not (os.path.exists(new_folder) and os.path.isdir(new_folder)):
            os.makedirs(new_folder)
        file_path = f"{self.report_path}/Wifi_Messages/{file_name}"
        # Write the JSON-formatted string to the .json file
        with open(file_path, 'w') as file:
            file.write(json_string)

    def remove_files_with_duplicate_names(self, folder_path):
        file_names = {}
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                if file_name in file_names:
                    # Removing the duplicate file
                    os.remove(file_path)
                    logging.info(f"Removed duplicate file: {file_path}")
                else:
                    # Adding the file name to the dictionary
                    file_names[file_name] = file_path

    def get_last_wifi_msg(self):
        a = self.json_get_with_retry("/wifi-msgs/last/1", debug_=True)
        try:
            last = a['wifi-messages']['time-stamp']
        except (TypeError, KeyError) as e:
            logging.error(
                f"get_last_wifi_msg: LANforge response is not in expected format ({e}). Data received: {a}")
            logging.warning("Could not establish a wifi-msgs baseline timestamp; falling back to 'NA' for this reset.")
            return "NA"
        logging.info(f"Last WiFi Message Time Stamp: {last}")
        return last

    def count_wifi_msg_matches(self, wifi_messages=None, message_keys=None, device_eid=None, match_text=None):
        matches = []
        eid_parts = device_eid.split(".")
        port_name = eid_parts[2]
        resource_id = eid_parts[0] + "." + eid_parts[1]
        for message_key, index in zip(message_keys, range(len(message_keys))):
            wifi_msg_text = wifi_messages[index][message_key]['text']
            message_resource = wifi_messages[index][message_key]['resource']
            if type(wifi_msg_text) is str:
                message_tokens = wifi_messages[index][message_key]['text'].split(" ")
                if port_name is None:
                    logging.info(f"Device {port_name} is None device name not existed in wifi messages...")
                else:
                    if message_resource == resource_id:
                        if port_name in message_tokens:
                            if match_text in message_tokens:
                                # logging.info(f"The filter '{match_text}' is present in the Wi-Fi message test list.")
                                matches.append("YES")
                            else:
                                match_tokens = match_text.split(" ")
                                if all(token in message_tokens for token in match_tokens):
                                    # logging.info(f"The filter {match_tokens} sequence is present in Wi-Fi msg.")
                                    matches.append("YES")
                        else:
                            if f"IFNAME={port_name}" in message_tokens:  # for linux
                                if match_text in message_tokens:
                                    # logging.info(f"The filter '{match_text}' is present in the Wi-Fi message test list.")
                                    matches.append("YES")
                                else:
                                    match_tokens = match_text.split(" ")
                                    if all(token in message_tokens for token in match_tokens):
                                        # logging.info(f"The filter {match_tokens} sequence is present in Wi-Fi msg.")
                                        matches.append("YES")
            else:  # if wifi_msg_text is list
                for message_line in wifi_msg_text:
                    message_tokens = message_line.split(" ")
                    # print("$Wifi Message Text list:", message_tokens)
                    if port_name is not None:
                        if message_resource == resource_id:
                            if port_name in message_tokens:  # for android
                                if match_text in message_tokens:
                                    # logging.info(f"The filter '{match_text}' is present in the Wi-Fi message test list.")
                                    matches.append("YES")
                                else:
                                    match_tokens = match_text.split(" ")
                                    if all(token in message_tokens for token in match_tokens):
                                        # logging.info(f"The filter {match_tokens} sequence is present in Wi-Fi msg.")
                                        matches.append("YES")
                            else:
                                if f"IFNAME={port_name}" in message_tokens:  # for linux
                                    if match_text in message_tokens:
                                        # logging.info(f"The filter '{match_text}' is present in the Wi-Fi message test list.")
                                        matches.append("YES")
                                    else:
                                        match_tokens = match_text.split(" ")
                                        if all(token in message_tokens for token in match_tokens):
                                            # logging.info(f"The filter {match_tokens} sequence is present in Wi-Fi msg.")
                                            matches.append("YES")
        match_count = matches.count("YES")
        return match_count

    def collect_device_metrics(self, device_metrics=None, device_eid=None, since_time=None, file_name="dummy.json", iteration=None):
        # print("Waiting for 20 sec to fetch the logs...")
        # time.sleep(20)
        wifi_msgs_response = self.json_get_with_retry("/wifi-msgs/since=time/" + str(since_time), debug_=True)
        try:
            wifi_messages = wifi_msgs_response['wifi-messages']
        except (TypeError, KeyError) as e:
            logging.error(
                f"collect_device_metrics: LANforge response is not in expected format ({e}) while fetching "
                f"wifi-msgs for device {device_eid}. Data received: {wifi_msgs_response}")
            logging.warning(f"Defaulting device {device_eid} stats to 0 for this reset and continuing.")
            for metric_name in ("ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected"):
                device_metrics[str(device_eid)][metric_name] = 0
            device_metrics[str(device_eid)]["Remarks"] = "Data unavailable - LANforge API error, stats defaulted to 0"
            device_metrics[str(device_eid)]["cx time (us)"] = "NA"
            self.write_iteration_csvs(device_metrics, iteration)
            return device_metrics
        # print("Wifi msgs Response : ", wifi_messages)
        logging.info(
            f"Counting the DISCONNECTIONS, SCANNING, ASSOC ATTEMPTS, ASSOC RECJECTIONS, CONNECTS for device {device_eid}")
        if type(wifi_messages) is not list:
            logging.info(f"Device {device_eid} : Getting wifi messages for only single time-stamp. Converting into List.")
            wifi_messages = [{f"{wifi_messages['resource']}.{wifi_messages['time-stamp']}": wifi_messages}]
        # print("After Updating Wi-Fi msgs Response : ", wifi_messages)
        self.create_log_file(json_list=wifi_messages, file_name=file_name)
        self.remove_files_with_duplicate_names(folder_path=f"{self.report_path}/Wifi_Messages/")
        message_keys = []

        for index in range(len(wifi_messages)):
            message_keys.append(list(wifi_messages[index].keys())[0])
        # print("Key list", message_keys)
        # android (flag) check for clustered lanforge cases
        is_android = False
        adb_response = self.json_get_with_retry('/adb/')
        try:
            adb_devices = adb_response['devices']
        except (TypeError, KeyError) as e:
            logging.error(
                f"collect_device_metrics: LANforge response is not in expected format ({e}) while fetching "
                f"/adb/ devices. Data received: {adb_response}")
            logging.warning(
                f"Could not fetch adb device list; relying only on the '1.1.' prefix heuristic for {device_eid}.")
            adb_devices = []
        for device_data in adb_devices:
            device_name, _ = list(device_data.keys())[0], list(device_data.values())[0]
            if device_eid in device_name:
                is_android = True
                break
        if "1.1." in device_eid or is_android:
            # disconnects
            android_disconnect_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                   device_eid=device_eid, match_text="Terminating...")
            if android_disconnect_count > 1 or android_disconnect_count == 0:
                device_state = self.utility.get_device_state(device=device_eid)
                if device_state == 'COMPLETED':
                    logging.info("The Device %s is in connected state." % device_eid)
                    android_disconnect_count = 0
                else:
                    logging.info("The Device %s is not in connected state." % device_eid)
                    android_disconnect_count = 1
                logging.info(f"Disconnect Count For Android: {android_disconnect_count}")
            # Updating the dict with disconnects for android
            logging.info("Final Disconnect count for %s: %s" % (device_eid, android_disconnect_count))
            device_metrics[device_eid]["Disconnected"] = android_disconnect_count
            # scanning count
            android_scan_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                             device_eid=device_eid, match_text="SCAN-STARTED")
            logging.info("Final Scanning Count for %s: %s" % (device_eid, android_scan_count))
            device_metrics[str(device_eid)]["Scanning"] = android_scan_count
            # association attempts
            android_association_attempt = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                      device_eid=device_eid, match_text="ASSOCIATING")
            logging.info("Final Association Attempts Count for %s: %s" % (device_eid, android_association_attempt))
            device_metrics[str(device_eid)]["ConnectAttempt"] = android_association_attempt
            # association rejections
            android_association_rejection = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                        device_eid=device_eid, match_text="ASSOC_REJECT")
            logging.info("Final Association Rejection Count for %s: %s" % (device_eid, android_association_rejection))
            device_metrics[str(device_eid)]["Association Rejection"] = android_association_rejection
            # connections
            android_connected_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                  device_eid=device_eid, match_text="CTRL-EVENT-CONNECTED")
            # Double-checking & adding remarks if any
            if android_connected_count > 1 or android_connected_count == 0:
                device_ssid = self.utility.get_device_ssid(device=device_eid)
                if device_ssid == self.ssid:
                    logging.info("The Device %s is connected to expected ssid" % device_eid)
                    android_connected_count = 1
                else:
                    logging.info("**** The Device is not connected to the expected ssid ****")
                    android_connected_count = 0
                logging.info(f"Connected Count for Android: {android_connected_count}")
            # Updating the dict with connects for android
            logging.info("Final Connected Count for %s: %s" % (device_eid, android_connected_count))
            device_metrics[str(device_eid)]["Connected"] = android_connected_count
            # Adding remarks
            remarks = "NA"
            device_metrics[str(device_eid)]["Remarks"] = remarks
            # Updating the association-rejections
            if android_association_attempt > android_connected_count:
                android_association_rejection = android_association_attempt - android_connected_count
            device_metrics[str(device_eid)]["Association Rejection"] = android_association_rejection
            if android_connected_count > 0:
                _, resource, serial = device_eid.split('.')
                resource_id_response = self.json_get_with_retry('/adb/1/{}/{}?fields=resource-id'.format(resource, serial))
                port_response = None
                try:
                    resource_id = resource_id_response['devices']['resource-id']
                    port_response = self.json_get_with_retry('port/1/{}/wlan0?fields=cx time (us)'.format(resource_id.split('.')[1]))
                    cx_time_us = port_response['interface']['cx time (us)']
                    device_metrics[str(device_eid)]['cx time (us)'] = cx_time_us
                except (TypeError, KeyError) as e:
                    logging.error(
                        f"collect_device_metrics: could not fetch cx time (us) for device {device_eid}; LANforge "
                        f"response is not in expected format ({e}). resource-id response: {resource_id_response}, "
                        f"port response: {port_response}")
                    device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
            else:
                device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
        else:
            if device_eid in self.windows_list:  # for windows
                win_disconnect_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                   device_eid=device_eid, match_text="Wireless security stopped.")
                # Double-checking the disconnect count with another key msg
                if win_disconnect_count == 0:
                    win_disconnect_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                       device_eid=device_eid,
                                                                       match_text="WLAN AutoConfig service has successfully disconnected from a wireless network")
                logging.info("Final Disconnect count for %s: %s" % (device_eid, win_disconnect_count))
                device_metrics[device_eid]["Disconnected"] = win_disconnect_count
                win_scan_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                             device_eid=device_eid, match_text="service started")
                logging.info("Final Scanning Count for %s: %s" % (device_eid, win_scan_count))
                device_metrics[str(device_eid)]["Scanning"] = win_scan_count
                win_association_attempt = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                      device_eid=device_eid, match_text="association started.")
                logging.info("Final Association Attempts Count for %s: %s" % (device_eid, win_association_attempt))
                device_metrics[str(device_eid)]["ConnectAttempt"] = win_association_attempt
                win_association_rejection = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                        device_eid=device_eid, match_text="failed to connect")
                logging.info("Final Association Rejection Count for %s: %s" % (device_eid, win_association_rejection))
                device_metrics[str(device_eid)]["Association Rejection"] = win_association_rejection
                win_connected_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                  device_eid=device_eid, match_text="connected")
                win_connection_state_unverified = False
                # assoc-rejection based logic
                if win_association_rejection:
                    # Updating the connects
                    actual_connects = win_association_attempt - win_association_rejection
                    if actual_connects == win_connected_count:
                        win_connected_count = win_connected_count
                    else:
                        win_connected_count = actual_connects
                else:
                    if win_association_attempt == win_connected_count:
                        win_connected_count = win_connected_count
                    else:
                        # Double-checking
                        if win_connected_count > 1 or win_connected_count == 0:
                            eid_parts = device_eid.split(".")
                            port_response = self.json_get_with_retry(f"port/{eid_parts[0]}/{eid_parts[1]}/{eid_parts[2]}?fields=ssid,ip")
                            try:
                                if port_response['interface']['ssid'] == self.ssid and port_response['interface']['ip'] != "0.0.0.0":
                                    win_connected_count = 1
                                else:
                                    win_connected_count = 0
                            except (TypeError, KeyError) as e:
                                logging.error(
                                    f"collect_device_metrics: could not verify connection state for device "
                                    f"{device_eid}; LANforge response is not in expected format ({e}). Data "
                                    f"received: {port_response}")
                                win_connected_count = 0
                                win_connection_state_unverified = True
                logging.info("Final Connected Count for %s: %s" % (device_eid, win_connected_count))
                device_metrics[str(device_eid)]["Connected"] = win_connected_count
                # Updating the association-rejections
                if win_association_attempt > win_connected_count:
                    win_association_rejection = win_association_attempt - win_connected_count
                device_metrics[str(device_eid)]["Association Rejection"] = win_association_rejection
                # Adding re-marks
                remarks = "NA"
                if win_disconnect_count == 0 and win_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif win_disconnect_count >= 1 and win_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                if win_connection_state_unverified:
                    remarks = "Connection state unverified - LANforge API error while double-checking connect count"
                device_metrics[str(device_eid)]["Remarks"] = remarks
                if win_connected_count > 0:
                    eid_parts = device_eid.split(".")
                    port_response = self.json_get_with_retry(f"port/{eid_parts[0]}/{eid_parts[1]}/{eid_parts[2]}?fields=cx time (us)")
                    try:
                        cx_time_us = port_response['interface']['cx time (us)']
                        device_metrics[str(device_eid)]['cx time (us)'] = cx_time_us
                    except (TypeError, KeyError) as e:
                        logging.error(
                            f"collect_device_metrics: could not fetch cx time (us) for device {device_eid}; "
                            f"LANforge response is not in expected format ({e}). Data received: {port_response}")
                        device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
                else:
                    device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
            else:  # other means (for linux, mac)
                linux_mac_disconnect_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                         device_eid=device_eid, match_text="disconnected")
                # Double-checking the disconnect count with another key msg
                if linux_mac_disconnect_count == 0:
                    linux_mac_disconnect_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                             device_eid=device_eid,
                                                                             match_text="<3>CTRL-EVENT-DSCP-POLICY clear_all")
                logging.info("Final Disconnect count for %s: %s" % (device_eid, linux_mac_disconnect_count))
                device_metrics[device_eid]["Disconnected"] = linux_mac_disconnect_count
                linux_mac_scan_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                   device_eid=device_eid, match_text="<3>CTRL-EVENT-SCAN-STARTED")
                logging.info("Final Scanning Count for %s: %s" % (device_eid, linux_mac_scan_count))
                device_metrics[str(device_eid)]["Scanning"] = linux_mac_scan_count
                linux_mac_association_attempt = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                            device_eid=device_eid, match_text="<3>Trying to associate with")
                logging.info("Final Association Attempts Count for %s: %s" % (device_eid, linux_mac_association_attempt))
                device_metrics[str(device_eid)]["ConnectAttempt"] = linux_mac_association_attempt
                linux_mac_association_rejection = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                              device_eid=device_eid, match_text="NoneValue")
                logging.info("Final Association Rejection Count for %s: %s" % (device_eid, linux_mac_association_rejection))
                device_metrics[str(device_eid)]["Association Rejection"] = linux_mac_association_rejection

                linux_mac_connected_count = self.count_wifi_msg_matches(wifi_messages=wifi_messages, message_keys=message_keys,
                                                                        device_eid=device_eid, match_text="<3>CTRL-EVENT-CONNECTED")
                linux_mac_connection_state_unverified = False
                # assoc-rejection based logic
                if linux_mac_association_rejection:
                    # Updating the connects
                    actual_connects = linux_mac_association_attempt - linux_mac_association_rejection
                    if actual_connects == linux_mac_connected_count:
                        linux_mac_connected_count = linux_mac_connected_count
                    else:
                        linux_mac_connected_count = actual_connects
                else:
                    if linux_mac_association_attempt == linux_mac_connected_count:
                        linux_mac_connected_count = linux_mac_connected_count
                    else:
                        # Double-checking & adding remarks if any
                        if linux_mac_connected_count > 1 or linux_mac_connected_count == 0:
                            eid_parts = device_eid.split(".")
                            port_response = self.json_get_with_retry(f"port/{eid_parts[0]}/{eid_parts[1]}/{eid_parts[2]}?fields=ssid,ip")
                            try:
                                if port_response['interface']['ssid'] == self.ssid and port_response['interface']['ip'] != "0.0.0.0":
                                    linux_mac_connected_count = 1
                                else:
                                    linux_mac_connected_count = 0
                            except (TypeError, KeyError) as e:
                                logging.error(
                                    f"collect_device_metrics: could not verify connection state for device "
                                    f"{device_eid}; LANforge response is not in expected format ({e}). Data "
                                    f"received: {port_response}")
                                linux_mac_connected_count = 0
                                linux_mac_connection_state_unverified = True
                logging.info("Final Connected Count for %s: %s" % (device_eid, linux_mac_connected_count))
                device_metrics[str(device_eid)]["Connected"] = linux_mac_connected_count
                # Updating the association-rejections
                if linux_mac_association_attempt > linux_mac_connected_count:
                    linux_mac_association_rejection = linux_mac_association_attempt - linux_mac_connected_count
                device_metrics[str(device_eid)]["Association Rejection"] = linux_mac_association_rejection
                # Adding remarks
                remarks = "NA"
                if linux_mac_disconnect_count == 0 and linux_mac_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif linux_mac_disconnect_count >= 1 and linux_mac_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                if linux_mac_connection_state_unverified:
                    remarks = "Connection state unverified - LANforge API error while double-checking connect count"
                device_metrics[str(device_eid)]["Remarks"] = remarks
                if linux_mac_connected_count > 0:
                    eid_parts = device_eid.split(".")
                    port_response = self.json_get_with_retry(f"port/{eid_parts[0]}/{eid_parts[1]}/{eid_parts[2]}?fields=cx time (us)")
                    try:
                        cx_time_us = port_response['interface']['cx time (us)']
                        device_metrics[str(device_eid)]['cx time (us)'] = cx_time_us
                    except (TypeError, KeyError) as e:
                        logging.error(
                            f"collect_device_metrics: could not fetch cx time (us) for device {device_eid}; "
                            f"LANforge response is not in expected format ({e}). Data received: {port_response}")
                        device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
                else:
                    device_metrics[str(device_eid)]['cx time (us)'] = 'NA'
        logging.info("device_metrics " + str(device_metrics))
        self.write_iteration_csvs(device_metrics, iteration)

        return device_metrics

    def write_iteration_csvs(self, device_metrics, iteration):
        # storing results in csv file for each reset
        for device_eid, metrics in device_metrics.items():
            df = pd.DataFrame([metrics])
            filename = f"{self.report_path}/{device_eid}_{iteration}.csv"
            df.to_csv(filename, index=False)

    def aggregate_reset_dict(self, reset_dict):
        aggregated = {}
        for reset_id in sorted(reset_dict.keys()):
            if reset_dict[reset_id] is None:
                continue
            devices = reset_dict[reset_id]
            for device, stats in devices.items():
                if device not in aggregated:
                    aggregated[device] = {}
                for key, value in stats.items():
                    if key in ("Remarks", "cx time (us)"):
                        aggregated[device][key] = value
                    else:
                        if key not in aggregated[device]:
                            aggregated[device][key] = 0
                        aggregated[device][key] += int(value) if str(value).isdigit() else 0
        return dict(aggregated)

    def generate_coordinate_csv(self, reset_dict, r):
        cols = ['Client', 'ConnectAttempt', 'Disconnected', 'Scanning', 'Association Rejection', 'Connected', 'Iterations', 'Status', 'coordinate']
        if self.rotation_enabled:
            cols.append('angle')
        if self.rotation_enabled:
            suffix = f"_{self.current_coordinate}_{self.current_angle}"
        else:
            suffix = f"_{self.current_coordinate}"
        aggregated_dict = self.aggregate_reset_dict(reset_dict=reset_dict)
        if self.current_coordinate not in self.coordinate_df:
            self.coordinate_df[self.current_coordinate] = {}
        df = pd.DataFrame(columns=cols)
        for client, stats in aggregated_dict.items():
            client_name = f"{client}{suffix}"
            self.coordinate_df[self.current_coordinate][client_name] = stats.copy()
            self.coordinate_df[self.current_coordinate][client_name]["coordinate"] = self.current_coordinate
            self.coordinate_df[self.current_coordinate][client_name]["Status"] = "running"

            if self.rotation_enabled:
                self.coordinate_df[self.current_coordinate][client_name]["angle"] = self.current_angle
        rows = []
        for client, stats in self.coordinate_df[self.current_coordinate].items():
            row = {
                'Client': client,
                'ConnectAttempt': stats.get('ConnectAttempt', 0),
                'Disconnected': stats.get('Disconnected', 0),
                'Scanning': stats.get('Scanning', 0),
                'Association Rejection': stats.get('Association Rejection', 0),
                'Connected': stats.get('Connected', 0),
                'Iterations': r + 1,
                'Status': stats.get('Status', 'NA'),
                'coordinate': stats.get('coordinate', 'NA')
            }
            if self.rotation_enabled:
                row['angle'] = stats.get('angle', 'NA')
            rows.append(row)

        df = pd.DataFrame(rows, columns=cols)
        self.result_df = df.copy()

        df.to_csv(f"{self.report_path}/overall_reset_{self.current_coordinate}.csv", index=False)
        if self.dowebgui:
            df.to_csv(f"{self.result_dir}/overall_reset_{self.current_coordinate}.csv", index=False)

    def performing_resets(self, test_start_time=None):
        iteration_indexes = []
        for index in range(self.iterations):
            iteration_indexes.append(index)
        logging.info(f"Given No.of iterations for Reset : {len(iteration_indexes)}")
        logging.info("Reset list:" + str(iteration_indexes))
        per_iteration_results = dict.fromkeys(iteration_indexes)
        test_stopped = False
        battery_check_interval_sec = 300
        test_stopped_by_user = False
        next_battery_check = time.time() + battery_check_interval_sec
        for iteration, _ in zip(range(self.iterations), per_iteration_results):
            if self.robot_test:
                current_time = time.time()
                if current_time >= next_battery_check:
                    if test_stopped_by_user or self.robo_test_stopped:
                        break
                    paused, test_stopped_by_user = self.robot_obj.wait_for_battery()
                    if test_stopped_by_user:
                        break
                    if paused:
                        # After charging, return to the last coordinate
                        reached, abort = self.robot_obj.move_to_coordinate(self.current_coordinate)
                        # If user stopped the test during movement
                        if abort:
                            test_stopped_by_user = True
                            break
                        if not reached:
                            break
                        # Restore orientation if rotation is enabled
                        if self.rotation_enabled:
                            rotated = self.robot_obj.rotate_angle(self.current_angle)
                            if not rotated:
                                test_stopped_by_user = True
                                break
                    next_battery_check = current_time + battery_check_interval_sec
            logging.info(f"Waiting until given {self.reset_interval_sec} sec time interval to finish...")
            time.sleep(int(self.reset_interval_sec))  # sleeping until time interval finish
            logging.info(f"Iteration :- {iteration}")
            logging.info("Reset -" + str(iteration))
            device_metrics = dict.fromkeys(self.adb_device_list)
            logging.info(f"local dict for android :{device_metrics}")
            laptop_metrics = dict.fromkeys(self.all_laptops)
            logging.info(f"local dict for laptops : {laptop_metrics}")
            device_metrics.update(laptop_metrics)

            metric_names = ["ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected"]
            empty_metrics = dict.fromkeys(metric_names)

            for device_eid in self.adb_device_list:
                device_metrics[device_eid] = empty_metrics.copy()  # for android devices dict
            for device_eid in self.all_laptops:
                laptop_metrics[device_eid] = empty_metrics.copy()  # for laptop devices dict
            logging.info(f"Final Outcome dict for android devices: {device_metrics}")
            logging.info(f"Final Outcome dict for laptop devices: {laptop_metrics}")
            logging.info(str(device_metrics))

            device_metrics.update(laptop_metrics)
            logging.info(f"Final dict: {device_metrics}")

            # note last log time
            since_time = self.get_last_wifi_msg()

            for device_eid in self.adb_device_list:
                self.interop.stop(device=device_eid)
            for device_eid in self.all_laptops:  # laptop admin down
                logging.info(f"**** Disable wifi for laptop {device_eid}")
                self.admin_down(port_eid=device_eid)
            for device_eid in self.adb_device_list:
                logging.info(f"**** Disable wifi for android {device_eid}")
                logging.info("disable wifi")
                self.interop.enable_or_disable_wifi(device=device_eid, wifi="disable")
            for device_eid in self.all_laptops:  # laptop admin up
                logging.info(f"**** Enable wifi for laptop {device_eid}")
                self.admin_up(port_eid=device_eid)
            for device_eid in self.adb_device_list:
                logging.info(f"*** Enable wifi for laptop {device_eid}")
                logging.info("enable wifi")
                self.interop.enable_or_disable_wifi(device=device_eid, wifi="enable")
            for device_eid in self.adb_device_list:
                logging.info(f"Starting APP for {device_eid}")
                self.interop.start(device=device_eid)
            if self.all_laptops:
                if self.wait_for_ip(station_list=self.all_laptops, timeout_sec=60):
                    logging.info("PASSED : ALL STATIONS GOT IP")
                else:
                    logging.info("FAILED : MAY BE NOT ALL STATIONS ACQUIRED IP'S")
            time.sleep(30)
            for device_eid in self.all_selected_devices:
                iteration_metrics = self.collect_device_metrics(device_metrics=device_metrics, device_eid=device_eid,
                                                                since_time=since_time,
                                                                file_name=f"reset_{iteration}_log.json",
                                                                iteration=iteration)
                per_iteration_results[iteration] = iteration_metrics
                if self.robot_test:
                    self.generate_coordinate_csv(reset_dict=per_iteration_results, r=iteration)
                else:
                    self.create_dict_csv(per_iteration_results)
                if self.dowebgui:
                    with open(self.result_dir + f"/../../Running_instances/{self.lanforge_ip}_{self.test_name}_running.json",
                              'r') as file:
                        run_status = json.load(file)
                        if run_status["status"] != "Running":
                            logging.info('Test is stopped by the user')
                            test_stopped = True
                            self.robo_test_stopped = True
                            break
            logging.info('{}'.format(per_iteration_results))
            if test_stopped:
                stopped_metrics = {
                    'ConnectAttempt': 0,
                    'Disconnected': 0,
                    'Scanning': 0,
                    'Association Rejection': 0,
                    'Connected': 0,
                    'Remarks': "Test stopped by user",
                    'cx time (us)': 0
                }
                empty_iterations = []
                for iteration_index in range(self.iterations):
                    if per_iteration_results.get(iteration_index) is None:
                        empty_iterations.append(iteration_index)
                    else:
                        for device_eid, metrics in per_iteration_results[iteration_index].items():
                            if any(value is None for value in metrics.values()):
                                per_iteration_results[iteration_index][device_eid] = stopped_metrics.copy()

                for iteration_index in empty_iterations:
                    del per_iteration_results[iteration_index]

                break
        logging.info(f"Final Reset Count Dictionary for all clients: {per_iteration_results}")
        logging.info("reset dict " + str(per_iteration_results))
        test_end = datetime.now()
        test_end_time = test_end.strftime("%b %d %H:%M:%S")
        if self.robot_test:
            if self.rotation_enabled:
                logging.info(f"At coordinate {self.current_coordinate} on Angle {self.current_angle} Test Ended at {test_end}")
            else:
                logging.info(f"At coordinate {self.current_coordinate} Test Ended at {test_end}")
        else:
            logging.info(f"Test Ended at {test_end}")
        # logging.info("Test ended at " + test_end_time)
        time_format = '%b %d %H:%M:%S'
        test_duration = datetime.strptime(test_end_time, time_format) - datetime.strptime(test_start_time, time_format)
        if self.robot_test:
            if self.rotation_enabled:
                logging.info(f"Total Test Duration taken to complete port resets at coordinate {self.current_coordinate} on angle {self.current_angle}: {test_duration}")
            else:
                logging.info(f"Total Test Duration taken to complete port resets at coordinate {self.current_coordinate} : {test_duration}")
        else:
            logging.info(f"Total Test Duration: {test_duration}")

        return per_iteration_results, test_duration

    # @property
    def run(self):
        try:
            # start timer
            test_start = datetime.now()
            test_start_time = test_start.strftime("%b %d %H:%M:%S")
            logging.info(f"Test Started at {test_start}")
            self.adb_device_list = self.interop.check_sdk_release(selected_android_devices=self.final_selected_android_list)
            self.windows_list = self.base_interop_profile.windows_list
            self.linux_list = self.base_interop_profile.linux_list
            self.mac_list = self.base_interop_profile.mac_list
            logging.info(f"Final Active Devices List (Android, Windows, Linux, Mac) Which support user specified release & not in phantom : {self.adb_device_list, self.base_interop_profile.windows_list, self.base_interop_profile.linux_list, self.base_interop_profile.mac_list}")  # noqa: E501
            self.all_selected_devices = self.adb_device_list + self.windows_list + self.linux_list + self.mac_list
            self.all_laptops = self.windows_list + self.linux_list + self.mac_list
            logging.info(f"All Selected Devices: {self.all_selected_devices}")
            logging.info(f"All Active Laptop Devices {self.all_laptops}")
            logging.info(
                f"The total number of available active & supported sdk release android devices are:  {len(self.adb_device_list)}")
            logging.info(
                f"The total number of available active windows devices are: {len(self.base_interop_profile.windows_list)}")
            logging.info(
                f"The total number of available active Linux devices are: {len(self.base_interop_profile.linux_list)}")
            logging.info(
                f"The total number of available active Mac devices are: {len(self.base_interop_profile.mac_list)}")

            if len(self.adb_device_list) == 0 and len(self.base_interop_profile.windows_list) == 0 and len(self.base_interop_profile.linux_list) == 0 and len(self.base_interop_profile.mac_list) == 0:
                logging.info("There is no active devices please check system.")
                logging.info('Aborting the test.')
                # Added for the purpose to stop webui test when there are no selected devices availble in lanforge.
                raise RuntimeError("There is no active devices please check system.")
            else:
                for index in range(len(self.adb_device_list)):
                    self.android_serials.append(self.adb_device_list[index].split(".")[2])
                logging.info(f"Separated device names from the full name: {self.android_serials}")

            # check status of devices
            phantom_states = []
            for device_eid in self.adb_device_list:
                phantom_states.append(self.interop.get_device_details(device=device_eid, query="phantom"))
            if self.adb_device_list or self.windows_list or self.linux_list or self.mac_list:
                for device_eid in self.adb_device_list:
                    self.android_user_names.append(self.interop.get_device_details(device=device_eid, query="user-name"))
                logging.info(f"ADB user-names for selected devices: {self.android_user_names}")
                logging.info("Checking heath data...")
                android_health = dict.fromkeys(self.adb_device_list)
                logging.info(f"Initial Health Data For Android Clients: {android_health}")
                laptop_health = dict.fromkeys(self.all_laptops)
                logging.info(f"Initial Health Data For Laptops Clients: {laptop_health}")

                # pre-checking whether the adb device connected to given ssid or not
                for device_eid in self.adb_device_list:
                    device_state = self.utility.get_device_state(device=device_eid)
                    if device_state == "COMPLETED,":
                        logging.info("Phone %s is in connected state." % device_eid)
                        device_ssid = self.utility.get_device_ssid(device=device_eid)
                        if device_ssid == self.ssid:
                            logging.info("The Device %s is connected to expected ssid (%s)" % (device_eid, device_ssid))
                            android_health[device_eid] = self.utility.get_wifi_health_monitor(device=device_eid, ssid=self.ssid)
                        else:
                            logging.info("**** The Device is not connected to the expected ssid ****")
                    else:
                        logging.info("Waiting for 30 sec & Checking again")
                        time.sleep(30)
                        device_state = self.utility.get_device_state(device=device_eid)
                        logging.info("Checking Device Status Again..." + str(device_state))
                        logging.info(f"Device state {device_state}")
                        if device_state == "COMPLETED,":
                            logging.info("Phone is in connected state")
                            device_ssid = self.utility.get_device_ssid(device=device_eid)
                            if device_ssid == self.ssid:
                                logging.info("The Device %s is connected to expected ssid (%s)" % (device_eid, device_ssid))
                                android_health[device_eid] = self.utility.get_wifi_health_monitor(device=device_eid, ssid=self.ssid)
                        else:
                            logging.info(f"device state {device_state}")
                            android_health[device_eid] = {'ConnectAttempt': '0', 'ConnectFailure': '0', 'AssocRej': '0',
                                                          'AssocTimeout': '0'}
                logging.info(f"Health Status for the Android Devices: {android_health}")

                logging.info(f"Health Status for the Laptop Devices: {laptop_health}")
                # Resting Starts from here
                if not self.robot_test:
                    per_iteration_results, test_duration = self.performing_resets(test_start_time=test_start_time)
                    return per_iteration_results, test_duration

                # For robot Scenario
                if (self.rotation_list[0] != ""):
                    self.rotation_enabled = True
                self.robot_obj = RobotClass()
                self.robot_obj.robo_ip = self.robot_ip
                base_dir = os.path.dirname(os.path.dirname(self.result_dir))
                nav_data = os.path.join(base_dir, 'nav_data.json')  # To generate nav_data.json in webgui folder
                self.robot_obj.nav_data_path = nav_data
                self.robot_obj.create_waypointlist()
                self.robot_obj.ip = self.lanforge_ip
                self.robot_obj.testname = self.test_name
                self.robot_obj.runtime_dir = self.result_dir
                test_stopped_by_user = False
                for coordinate_index in range(len(self.coordinate_list)):
                    if test_stopped_by_user or self.robo_test_stopped:
                        break
                    # Check for battery status before moving to next coordinate
                    _, test_stopped_by_user = self.robot_obj.wait_for_battery()
                    # If test is stopped by user during battery wait
                    if test_stopped_by_user:
                        break
                    reached_coordinate, abort = self.robot_obj.move_to_coordinate(self.coordinate_list[coordinate_index])
                    # If robot failed to reach the coordinate
                    if abort:
                        break
                    if reached_coordinate:
                        self.current_coordinate = self.coordinate_list[coordinate_index]
                        if not self.rotation_enabled:
                            per_iteration_results, test_duration = self.performing_resets(test_start_time=test_start_time)
                            self.port_reset_data[self.coordinate_list[coordinate_index]] = {'reset_dict': per_iteration_results, 'test_duration': test_duration}
                            time.sleep(10)
                        else:
                            for angle_index in range(len(self.rotation_list)):
                                # If test is stopped by user during battery wait
                                if self.robo_test_stopped or test_stopped_by_user:
                                    break
                                # Check for battery status before rotating to next angle
                                _, test_stopped_by_user = self.robot_obj.wait_for_battery()
                                rotated = self.robot_obj.rotate_angle(self.rotation_list[angle_index])
                                if rotated:
                                    self.current_angle = self.rotation_list[angle_index]
                                    per_iteration_results, test_duration = self.performing_resets(test_start_time=test_start_time)
                                if self.coordinate_list[coordinate_index] not in self.port_reset_data:
                                    self.port_reset_data[self.coordinate_list[coordinate_index]] = {}
                                self.port_reset_data[self.coordinate_list[coordinate_index]][self.rotation_list[angle_index]] = {'reset_dict': per_iteration_results, 'test_duration': test_duration}

                                time.sleep(10)
                                if test_stopped_by_user or self.robo_test_stopped:
                                    break

        except Exception as e:
            logger.error(str(e))

    def generate_overall_graph(self, reset_dict=None, figsize=(13, 5), _alignmen=None, remove_border=None,
                               bar_width=0.7, _legend_handles=None, _legend_loc="best", _legend_box=None,
                               _legend_ncol=1,
                               _legend_fontsize=None, text_font=12, bar_text_rotation=45, graph_suffix=""):
        dict_ = ['Port Resets', 'Disconnected', 'Scans', 'Assoc Attempts', "Association Rejection", 'Connected']
        data = dict.fromkeys(dict_)
        data['Port Resets'] = self.iterations * len(self.all_selected_devices)

        conected_list, laptop_conected_list = [], []
        disconnected_list, laptop_disconnected_list = [], []
        scan_state, laptop_scan_state = [], []
        asso_attempt, laptop_asso_attempt = [], []
        asso_rej, laptop_asso_rej = [], []

        for j in self.adb_device_list:
            local = []
            local_2, local_3, local_4, local_5, local_6 = [], [], [], [], []
            for i in reset_dict:
                if j in list(reset_dict[i].keys()):
                    local.append(reset_dict[i][j]['Connected'])
                    local_2.append(reset_dict[i][j]['Disconnected'])
                    local_3.append(reset_dict[i][j]['Scanning'])
                    local_4.append(reset_dict[i][j]['ConnectAttempt'])
                    local_5.append(reset_dict[i][j]["Association Rejection"])

            conected_list.append(local)
            disconnected_list.append(local_2)
            scan_state.append(local_3)
            asso_attempt.append(local_4)
            asso_rej.append(local_5)

        for j in self.all_laptops:
            local = []
            local_2, local_3, local_4, local_5, local_6 = [], [], [], [], []  # noqa: F841
            for i in reset_dict:
                if j in list(reset_dict[i].keys()):
                    local.append(reset_dict[i][j]['Connected'])
                    local_2.append(reset_dict[i][j]['Disconnected'])
                    local_3.append(reset_dict[i][j]['Scanning'])
                    local_4.append(reset_dict[i][j]['ConnectAttempt'])
                    local_5.append(reset_dict[i][j]["Association Rejection"])

            conected_list.append(local)
            disconnected_list.append(local_2)
            scan_state.append(local_3)
            asso_attempt.append(local_4)
            asso_rej.append(local_5)
        conected_list = conected_list + laptop_conected_list
        disconnected_list = disconnected_list + laptop_disconnected_list
        scan_state = scan_state + laptop_scan_state
        asso_attempt = asso_attempt + laptop_asso_attempt
        asso_rej = asso_rej + laptop_asso_rej

        # count connects and disconnects
        scan, ass_atmpt = 0, 0
        for i, _ in zip(range(len(scan_state)), range(len(asso_attempt))):
            for m in scan_state[i]:
                scan = scan + m
            for n in asso_attempt[i]:
                ass_atmpt = ass_atmpt + int(n)

        conects, disconnects = 0, 0
        for i, _ in zip(range(len(conected_list)), range(len(disconnected_list))):
            for m in conected_list[i]:
                conects = conects + m
            for n in disconnected_list[i]:
                disconnects = disconnects + n

        assorej = 0
        for i in (range(len(asso_rej))):
            for m in asso_rej[i]:
                assorej = assorej + m

        data['Disconnected'] = disconnects
        data['Scans'] = scan
        data['Assoc Attempts'] = ass_atmpt
        data['Connected'] = conects
        data["Association Rejection"] = assorej
        # print("Final data for overall graph: ", data)

        # creating the dataset
        self.graph_image_name = f"overall_graph{graph_suffix}"
        courses = list(data.keys())
        values = list(data.values())

        fig_size, ax = plt.subplots(figsize=figsize, gridspec_kw=_alignmen)
        # to remove the borders
        if remove_border is not None:
            for border in remove_border:
                ax.spines[border].set_color(None)
                if 'left' in remove_border:  # to remove the y-axis labeling
                    yaxis_visable = False
                else:
                    yaxis_visable = True
                ax.yaxis.set_visible(yaxis_visable)

        # creating the bar plot
        colors = ('#f56122', '#00FF00', '#f5ea22', '#3D85C6', '#fa4d4d', "forestgreen")
        for bar_values, color, i in zip(values, colors, range(len(courses))):
            plt.bar(courses[i], bar_values, color=color, width=bar_width)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', rotation=bar_text_rotation,
                     fontsize=text_font)

        plt.xlabel("", fontweight='bold', fontsize=15)
        plt.ylabel("Count", fontweight='bold', fontsize=15)

        plt.xticks(color='white')
        plt.legend(
            ['Port Resets', 'Disconnects', 'Scans', 'Assoc Attempts', "Assoc Rejections", 'Connects'],
            loc=_legend_loc,
            bbox_to_anchor=_legend_box,
            ncol=_legend_ncol,
            fontsize=_legend_fontsize)
        plt.suptitle("Overall Graph for Port Reset Test", fontsize=16)
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        return "%s.png" % self.graph_image_name

    def per_client_graph(self, data=None, name=None, figsize=(13, 5), _alignmen=None, remove_border=None, bar_width=0.5,
                         _legend_loc="best", _legend_box=None, _legend_fontsize=None, text_font=12,
                         bar_text_rotation=45, xaxis_name="", yaxis_name="", graph_title_size=16,
                         graph_title="Client %s Performance Port Reset Totals"):
        self.graph_image_name = name
        courses = list(data.keys())
        values = list(data.values())

        # fig = plt.figure(figsize=(12, 4))
        fig_size, ax = plt.subplots(figsize=figsize, gridspec_kw=_alignmen)
        # to remove the borders
        if remove_border is not None:
            for border in remove_border:
                ax.spines[border].set_color(None)
                if 'left' in remove_border:  # to remove the y-axis labeling
                    yaxis_visable = False
                else:
                    yaxis_visable = True
                ax.yaxis.set_visible(yaxis_visable)

        # creating the bar plot
        colors = ('#f56122', '#00FF00', '#f5ea22', '#3D85C6', '#fa4d4d', "forestgreen")
        for bar_values, color, i in zip(values, colors, range(len(courses))):
            plt.bar(courses[i], bar_values, color=color, width=bar_width)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', va='bottom', rotation=bar_text_rotation,
                     fontsize=text_font)

        plt.xlabel(xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(yaxis_name, fontweight='bold', fontsize=15)
        plt.legend(
            ['Port Resets', 'Disconnects', 'Scans', 'Assoc Attempts', "Assoc Rejections", 'Connects'],
            loc=_legend_loc,
            bbox_to_anchor=_legend_box,
            frameon=False,
            fontsize=_legend_fontsize)
        plt.suptitle(graph_title, fontsize=graph_title_size)
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        # generate csv
        print(data)
        df = pd.DataFrame(data=data, index=[1])
        print(df)
        df.to_csv('{}/{}.csv'.format(self.report_path, name))
        return "%s.png" % self.graph_image_name

    def generate_overall_graph_table(self, reset_dict, device_list):
        if self.robot_test:
            self.total_resets, self.total_disconnects, self.total_scans, self.total_assoc_attempts, self.total_assoc_rejections, self.total_connects = [], [], [], [], [], []
        for y, _ in zip(device_list, range(len(device_list))):
            reset_count_ = list(reset_dict.keys())
            reset_count = []
            for i in reset_count_:
                reset_count.append(int(i) + 1)
            asso_attempts, disconnected, scanning, connected, assorej, remarks = [], [], [], [], [], []

            for i in reset_dict:
                asso_attempts.append(reset_dict[i][y]["ConnectAttempt"])
                disconnected.append(reset_dict[i][y]["Disconnected"])
                scanning.append(reset_dict[i][y]["Scanning"])
                connected.append(reset_dict[i][y]["Connected"])
                assorej.append(reset_dict[i][y]["Association Rejection"])
                remarks.append(reset_dict[i][y]["Remarks"])

            # graph calculation
            dict_ = ['Port Resets', 'Disconnects', 'Scans', 'Association Attempts', "Association Rejections",
                     'Connects']
            data = dict.fromkeys(dict_)
            data['Port Resets'] = self.iterations

            dis = 0
            for i in disconnected:
                dis = dis + i
            data['Disconnects'] = dis

            scan = 0
            for i in scanning:
                scan = scan + i
            data['Scans'] = scan

            asso = 0
            for i in asso_attempts:
                asso = asso + i
            data['Association Attempts'] = asso

            asso_rej = 0
            for i in assorej:
                asso_rej = asso_rej + i
            data["Association Rejections"] = asso_rej

            con = 0
            for i in connected:
                con = con + i
            data['Connects'] = con

            # print(f"Final data for per client graph for {y}: {data}")

            # fetching the total dissconnects, connects, ass_attemsts, ass_rejections, scans
            self.total_resets.append(self.iterations)
            self.total_disconnects.append(sum(disconnected))
            self.total_scans.append(sum(scanning))
            self.total_assoc_attempts.append(sum(asso_attempts))
            self.total_assoc_rejections.append(sum(assorej))
            self.total_connects.append(sum(connected))

    def individual_client_info(self, reset_dict, device_list):
        # per client table and graphs
        # self.total_resets, self.total_disconnects, self.total_scans, self.total_assoc_attempts, self.total_assoc_rejections, self.total_connects = [], [], [], [], [], []
        for y, z in zip(device_list, range(len(device_list))):
            reset_count_ = list(reset_dict.keys())
            reset_count = []
            for i in reset_count_:
                reset_count.append(int(i) + 1)
            asso_attempts, disconnected, scanning, connected, assorej, remarks, cx_times = [], [], [], [], [], [], []

            for i in reset_dict:
                asso_attempts.append(reset_dict[i][y]["ConnectAttempt"])
                disconnected.append(reset_dict[i][y]["Disconnected"])
                scanning.append(reset_dict[i][y]["Scanning"])
                connected.append(reset_dict[i][y]["Connected"])
                assorej.append(reset_dict[i][y]["Association Rejection"])
                remarks.append(reset_dict[i][y]["Remarks"])
                cx_times.append(reset_dict[i][y]["cx time (us)"])

            # graph calculation
            dict_ = ['Port Resets', 'Disconnects', 'Scans', 'Association Attempts', "Association Rejections",
                     'Connects']
            data = dict.fromkeys(dict_)
            data['Port Resets'] = self.iterations

            dis = 0
            for i in disconnected:
                dis = dis + i
            data['Disconnects'] = dis

            scan = 0
            for i in scanning:
                scan = scan + i
            data['Scans'] = scan

            asso = 0
            for i in asso_attempts:
                asso = asso + i
            data['Association Attempts'] = asso

            asso_rej = 0
            for i in assorej:
                asso_rej = asso_rej + i
            data["Association Rejections"] = asso_rej

            con = 0
            for i in connected:
                con = con + i
            data['Connects'] = con

            # print(f"Final data for per client graph for {y}: {data}")

            if "1.1." in y:
                # setting the title for per client graph and table represent title.
                adb_user_name = self.interop.get_device_details(device=y, query="user-name")
                self.lf_report.set_obj_html(
                    "Port Resets for Client " + str(adb_user_name) + " (" + str(y.split(".")[2]) + ")",
                    "The below table & graph displays details of " + str(adb_user_name) + " device.")
                self.lf_report.build_objective()
            else:
                # setting the title for per client graph and table represent title.
                self.lf_report.set_obj_html(
                    "Port Resets for Client " + str(y) + ".",
                    "The below table & graph displays details of " + str(y) + " device.")
                self.lf_report.build_objective()

            # per client graph generation
            graph2 = self.per_client_graph(data=data, name="per_client_" + str(z), figsize=(13, 5),
                                           _alignmen={"left": 0.1}, remove_border=['top', 'right'],
                                           _legend_loc="upper left", _legend_fontsize=9, _legend_box=(1, 1),
                                           yaxis_name="COUNT",
                                           graph_title="Client " + str(y) + " Total Reset Performance Graph")
            # graph1 = self.generate_per_station_graph()
            self.lf_report.set_graph_image(graph2)
            self.lf_report.move_graph_image()
            self.lf_report.build_graph()

            # per client table data
            table_1 = {
                "Reset Count": reset_count,
                "Disconnected": disconnected,
                "Scanning": scanning,
                "Association attempts": asso_attempts,
                "Association Rejection": assorej,
                "Connected": connected,
                "Connection Time (us)": cx_times,
                "Remarks": remarks
            }
            test_setup = pd.DataFrame(table_1)
            self.lf_report.set_table_dataframe(test_setup)
            self.lf_report.build_table()
            self.lf_report.save_csv('overall_report.csv', test_setup)

    def generate_report(self, reset_dict=None, test_dur=None):
        try:
            # print("reset dict", reset_dict)
            # print("Test Duration", test_dur)
            # logging.info("reset dict " + str(reset_dict))

            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            security = ""
            if self.encryption == "psk2":
                security = "wpa2"
            elif self.encryption == "psk3":
                security = "wpa3"
            elif self.encryption == "psk":
                security = "wpa"
            else:
                security = "open"
            test_setup_info = {
                "DUT Name": self.dut_name,
                "LANforge ip": self.lanforge_ip,
                "SSID": self.ssid,
                "Security": security,
                "Total Reset Count": self.iterations,
                "No of Clients": f"{len(self.all_selected_devices)} (Windows: {len(self.windows_list)}, Linux: {len(self.linux_list)}, Mac: {len(self.mac_list)}, Android: {len(self.adb_device_list)})",  # noqa: E501
                # "Wait Time": str(self.wait_time) + " sec",
                "Time interval between resets": str(self.reset_interval_sec) + " sec",
                "Test Duration": test_dur,
            }
            self.lf_report.set_title("Port Reset Test")
            self.lf_report.set_date(date)
            self.lf_report.build_banner_cover()

            self.lf_report.set_obj_html("Objective",
                                        "The Port Reset Test simulates a scenario where multiple WiFi stations are created "
                                        "and connected to the Access Point (AP) under test. These stations are then randomly "
                                        "disconnected and reconnected at varying intervals, mimicking a busy enterprise or "
                                        "large public venue environment with frequent station arrivals and departures. "
                                        "The primary objective of this test is to thoroughly assess the core Access Point "
                                        "functions' control and management aspects under stress.<br><br>"
                                        )
            self.lf_report.build_objective()

            self.lf_report.set_table_title("Test Setup Information")
            self.lf_report.build_table_title()

            self.lf_report.test_setup_table(value="Basic Test Information", test_setup_data=test_setup_info)

            self.lf_report.set_obj_html("Overall Port Resets Graph",
                                        "The following graph presents an overview of different events during the test, "
                                        "including Port Resets, Disconnects, Scans, Association Attempts, Association Rejections and Connections. "
                                        "Each category represents the total count achieved by all clients.<br><br>"
                                        "1.  Port Resets: Total number of reset occurrences provided as test input.<br>"
                                        "2.  Disconnects: Total number of disconnects that happened for all clients during the test when WiFi was disabled.<br>"
                                        "3.  Scans: Total number of scanning states achieved by all clients during the test when the network is re-enabled.<br>"
                                        "4.  Association Attempts: Total number of association attempts (Associating state) made by all clients after WiFi is re-enabled in the full test.<br>"
                                        "4.  Association Rejections: Total number of association rejections made by all clients after WiFi is re-enabled in the full test.<br>"
                                        "6.  Connected: Total number of successful connections (Associated state) achieved by all clients during the test when WiFi is re-enabled.<br>"
                                        # " Here real clients used is "+ str(self.clients) + "and number of resets provided is " + str(self.iterations)
                                        )
            self.lf_report.build_objective()
            graph1 = self.generate_overall_graph(reset_dict=reset_dict, figsize=(13, 5), _alignmen=None, bar_width=0.5,
                                                 _legend_loc="upper center", _legend_ncol=6, _legend_fontsize=10,
                                                 _legend_box=(0.5, -0.06), text_font=12)
            # graph1 = self.generate_per_station_graph()
            self.lf_report.set_graph_image(graph1)
            self.lf_report.move_graph_image()
            self.lf_report.build_graph()

            all_devices = self.adb_device_list + self.all_laptops

            self.generate_overall_graph_table(reset_dict=reset_dict, device_list=all_devices)

            d_name, device_type, model, user_name, release = [], [], [], [], []  # noqa: F841
            for dev in self.adb_device_list:
                d_name.append(self.interop.get_device_details(device=dev, query="name"))
                device_type.append(self.interop.get_device_details(device=dev, query="device-type"))
                user_name.append(self.interop.get_device_details(device=dev, query="user-name"))
            for dev in self.all_laptops:
                d_name.append(dev)
                user_name.append(self.interop.get_laptop_devices_details(device=dev, query="host_name"))
                hw_version = self.interop.get_laptop_devices_details(device=dev, query="hw_version")
                if "Linux" in hw_version:
                    dev_type = "Linux"
                elif "Win" in hw_version:
                    dev_type = "Windows"
                elif "Apple" in hw_version:
                    dev_type = "Apple"
                else:
                    dev_type = ""
                device_type.append(dev_type)
            s_no = []
            for i in range(len(d_name)):
                s_no.append(i + 1)

            table_2 = {
                "S.No": s_no,
                "Name of the Devices": d_name,
                "Hardware Version": user_name,
                "Device Type": device_type,
                # "Model": model,
                # "SDK Release": release,
                "Port Resets": self.total_resets,
                "Disconnects": self.total_disconnects,
                "Scans": self.total_scans,
                "Assoc Attemts": self.total_assoc_attempts,
                "Assoc Rejects": self.total_assoc_rejections,
                "Connects": self.total_connects
            }
            test_setup = pd.DataFrame(table_2)
            self.lf_report.set_table_dataframe(test_setup)
            self.lf_report.build_table()
            self.individual_client_info(reset_dict=reset_dict, device_list=all_devices)
            # self.lf_report.set_obj_html("Tested Clients Information:",
            #                             "The table displays details of real clients which are involved in the test.")
            # self.lf_report.build_objective()

            self.lf_report.build_footer()
            self.lf_report.write_html()
            if self.dowebgui:
                self.lf_report.write_pdf(_page_size='A4', _orientation='Portrait')
            else:
                self.lf_report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')

            # self.lf_report.move_data(directory="log", _file_name="port_reset.log")
        except Exception as e:
            logging.warning(str(e))

    def add_live_view_images_to_report(self):
        """
        This function looks for throughput and RSSI images for each floor
        in the 'live_view_images' folder within `self.result_dir`.
        It waits up to **60 seconds** for each image. If an image is found,
        it's added to the `report` on a new page; otherwise, it's skipped.
        """
        for floor in range(0, int(self.total_floors)):
            port_reset_img_path = os.path.join(self.result_dir, "live_view_images", f"port_reset_{self.test_name}_{floor + 1}.png")
            timeout = 60  # seconds
            start_time = time.time()

            while not (os.path.exists(port_reset_img_path)):
                if time.time() - start_time > timeout:
                    logging.info("Timeout: Images not found within 60 seconds.")
                    break
                time.sleep(1)
            if os.path.exists(port_reset_img_path):
                self.lf_report.set_custom_html('<div style="page-break-before: always;"></div>')
                self.lf_report.build_custom()
                self.lf_report.set_custom_html(f'<img src="file://{port_reset_img_path}"></img>')
                self.lf_report.build_custom()

    def generate_report_for_robo(self):
        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
        # self.lf_report.move_data(_file_name="overall_reset_test.log")
        security = ""
        if self.encryption == "psk2":
            security = "wpa2"
        elif self.encryption == "psk3":
            security = "wpa3"
        elif self.encryption == "psk":
            security = "wpa"
        else:
            security = "open"
        test_setup_info = {
            "DUT Name": self.dut_name,
            "LANforge ip": self.lanforge_ip,
            "SSID": self.ssid,
            "Security": security,
            "Total Reset Count": self.iterations,
            "No of Clients": f"{len(self.all_selected_devices)} (Windows: {len(self.windows_list)}, Linux: {len(self.linux_list)}, Mac: {len(self.mac_list)}, Android: {len(self.adb_device_list)})",  # noqa: E501
            # "Wait Time": str(self.wait_time) + " sec",
            "Time interval between resets": str(self.reset_interval_sec) + " sec",
        }
        test_setup_info["Selected Coordinates"] = self.coordinate
        if self.rotation_enabled:
            test_setup_info["Selected Angles"] = self.rotation
        self.lf_report.set_title("Port Reset Test")
        self.lf_report.set_date(date)
        self.lf_report.build_banner_cover()

        self.lf_report.set_obj_html("Objective",
                                    "The Port Reset Test simulates a scenario where multiple WiFi stations are created "
                                    "and connected to the Access Point (AP) under test. These stations are then randomly "
                                    "disconnected and reconnected at varying intervals, mimicking a busy enterprise or "
                                    "large public venue environment with frequent station arrivals and departures. "
                                    "The primary objective of this test is to thoroughly assess the core Access Point "
                                    "functions' control and management aspects under stress.<br><br>"
                                    )
        self.lf_report.build_objective()

        self.lf_report.set_table_title("Test Setup Information")
        self.lf_report.build_table_title()
        self.lf_report.test_setup_table(value="Basic Test Information", test_setup_data=test_setup_info)

        if (self.dowebgui and self.get_live_view):
            self.lf_report.set_custom_html("<h2>Overall Port reset's Heatmap: </h2>")
            self.lf_report.build_custom()
            self.add_live_view_images_to_report()
        self.lf_report.set_obj_html("Overall Port Resets Graphs",
                                    "The following graph presents an overview of different events during the test, "
                                    "including Port Resets, Disconnects, Scans, Association Attempts, Association Rejections and Connections. "
                                    "Each category represents the total count achieved by all clients.<br><br>"
                                    "1.  Port Resets: Total number of reset occurrences provided as test input.<br>"
                                    "2.  Disconnects: Total number of disconnects that happened for all clients during the test when WiFi was disabled.<br>"
                                    "3.  Scans: Total number of scanning states achieved by all clients during the test when the network is re-enabled.<br>"
                                    "4.  Association Attempts: Total number of association attempts (Associating state) made by all clients after WiFi is re-enabled in the full test.<br>"
                                    "4.  Association Rejections: Total number of association rejections made by all clients after WiFi is re-enabled in the full test.<br>"
                                    "6.  Connected: Total number of successful connections (Associated state) achieved by all clients during the test when WiFi is re-enabled.<br>"
                                    # " Here real clients used is "+ str(self.clients) + "and number of resets provided is " + str(self.iterations)
                                    )
        self.lf_report.build_objective()
        for coordinate in range(len(self.coordinate_list)):
            if self.rotation_enabled:
                for angle in range(len(self.rotation_list)):
                    coord_key = self.coordinate_list[coordinate]
                    angle_key = self.rotation_list[angle]

                    if (
                        coord_key not in self.port_reset_data or
                        angle_key not in self.port_reset_data[coord_key] or
                        'reset_dict' not in self.port_reset_data[coord_key][angle_key]
                    ):
                        continue
                    reset_dict = self.port_reset_data[coord_key][angle_key]['reset_dict']
                    self.lf_report.set_obj_html(_obj_title=f"Overall Port reset stats at Coordinate: {self.coordinate_list[coordinate]} | Rotation Angle: {self.rotation_list[angle]}°",
                                                _obj="")
                    self.lf_report.build_objective()

                    graph_suffix = f"{self.coordinate_list[coordinate]}_{self.rotation_list[angle]}"
                    graph1 = self.generate_overall_graph(reset_dict=reset_dict, figsize=(13, 5), _alignmen=None, bar_width=0.5,
                                                         _legend_loc="upper center", _legend_ncol=6, _legend_fontsize=10,
                                                         _legend_box=(0.5, -0.06), text_font=12, graph_suffix=graph_suffix)
                    # graph1 = self.generate_per_station_graph()
                    self.lf_report.set_graph_image(graph1)
                    self.lf_report.move_graph_image()
                    self.lf_report.build_graph()
                    all_devices = self.adb_device_list + self.all_laptops

                    self.generate_overall_graph_table(reset_dict=reset_dict, device_list=all_devices)

                    d_name, device_type, model, user_name, release = [], [], [], [], []  # noqa: F841

                    for dev in self.adb_device_list:
                        d_name.append(self.interop.get_device_details(device=dev, query="name"))
                        device_type.append(self.interop.get_device_details(device=dev, query="device-type"))
                        user_name.append(self.interop.get_device_details(device=dev, query="user-name"))
                    for dev in self.all_laptops:
                        d_name.append(dev)
                        user_name.append(self.interop.get_laptop_devices_details(device=dev, query="host_name"))
                        hw_version = self.interop.get_laptop_devices_details(device=dev, query="hw_version")
                        if "Linux" in hw_version:
                            dev_type = "Linux"
                        elif "Win" in hw_version:
                            dev_type = "Windows"
                        elif "Apple" in hw_version:
                            dev_type = "Apple"
                        else:
                            dev_type = ""
                        device_type.append(dev_type)
                    s_no = []
                    for i in range(len(d_name)):
                        s_no.append(i + 1)

                    table_2 = {
                        "S.No": s_no,
                        "Name of the Devices": d_name,
                        "Hardware Version": user_name,
                        "Device Type": device_type,
                        # "Model": model,
                        # "SDK Release": release,
                        "Port Resets": self.total_resets,
                        "Disconnects": self.total_disconnects,
                        "Scans": self.total_scans,
                        "Assoc Attemts": self.total_assoc_attempts,
                        "Assoc Rejects": self.total_assoc_rejections,
                        "Connects": self.total_connects
                    }
                    test_setup = pd.DataFrame(table_2)
                    self.lf_report.set_table_dataframe(test_setup)
                    self.lf_report.build_table()
            else:
                coord_key = self.coordinate_list[coordinate]

                if (
                    coord_key not in self.port_reset_data or
                    'reset_dict' not in self.port_reset_data[coord_key]
                ):
                    continue
                reset_dict = self.port_reset_data[coord_key]['reset_dict']
                self.lf_report.set_obj_html(_obj_title=f"Overall Port reset stats at Coordinate: {self.coordinate_list[coordinate]}",
                                            _obj="")
                self.lf_report.build_objective()
                graph_suffix = f"{self.coordinate_list[coordinate]}"
                graph1 = self.generate_overall_graph(reset_dict=reset_dict, figsize=(13, 5), _alignmen=None, bar_width=0.5,
                                                     _legend_loc="upper center", _legend_ncol=6, _legend_fontsize=10,
                                                     _legend_box=(0.5, -0.06), text_font=12, graph_suffix=graph_suffix)
                # graph1 = self.generate_per_station_graph()
                self.lf_report.set_graph_image(graph1)
                self.lf_report.move_graph_image()
                self.lf_report.build_graph()
                all_devices = self.adb_device_list + self.all_laptops

                self.generate_overall_graph_table(reset_dict=reset_dict, device_list=all_devices)

                d_name, device_type, model, user_name, release = [], [], [], [], []  # noqa: F841

                for dev in self.adb_device_list:
                    d_name.append(self.interop.get_device_details(device=dev, query="name"))
                    device_type.append(self.interop.get_device_details(device=dev, query="device-type"))
                    user_name.append(self.interop.get_device_details(device=dev, query="user-name"))
                for dev in self.all_laptops:
                    d_name.append(dev)
                    user_name.append(self.interop.get_laptop_devices_details(device=dev, query="host_name"))
                    hw_version = self.interop.get_laptop_devices_details(device=dev, query="hw_version")
                    if "Linux" in hw_version:
                        dev_type = "Linux"
                    elif "Win" in hw_version:
                        dev_type = "Windows"
                    elif "Apple" in hw_version:
                        dev_type = "Apple"
                    else:
                        dev_type = ""
                    device_type.append(dev_type)
                s_no = []
                for i in range(len(d_name)):
                    s_no.append(i + 1)

                table_2 = {
                    "S.No": s_no,
                    "Name of the Devices": d_name,
                    "Hardware Version": user_name,
                    "Device Type": device_type,
                    # "Model": model,
                    # "SDK Release": release,
                    "Port Resets": self.total_resets,
                    "Disconnects": self.total_disconnects,
                    "Scans": self.total_scans,
                    "Assoc Attemts": self.total_assoc_attempts,
                    "Assoc Rejects": self.total_assoc_rejections,
                    "Connects": self.total_connects
                }
                test_setup = pd.DataFrame(table_2)
                self.lf_report.set_table_dataframe(test_setup)
                self.lf_report.build_table()
        self.lf_report.build_footer()
        self.lf_report.write_html()
        if self.dowebgui:
            self.lf_report.write_pdf(_page_size='A4', _orientation='Portrait')
        else:
            self.lf_report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')

    def create_dict_csv(self, port_reset_dict):
        """
        Aggregate client connection stats from all iterations and save a summary CSV (overall_reset.csv).
        """
        i_df = {}

        for _, devices in port_reset_dict.items():
            if devices is None:
                continue
            for client, stats in devices.items():
                if client not in i_df:
                    i_df[client] = {
                        'ConnectAttempt': 0,
                        'Disconnected': 0,
                        'Scanning': 0,
                        'Association Rejection': 0,
                        'Connected': 0,
                        'Iterations': 0,
                        'Status': 'running'
                    }

                # Use safe addition (handles None and missing keys)
                i_df[client]['ConnectAttempt'] += stats.get('ConnectAttempt', 0) or 0
                i_df[client]['Disconnected'] += stats.get('Disconnected', 0) or 0
                i_df[client]['Scanning'] += stats.get('Scanning', 0) or 0
                i_df[client]['Association Rejection'] += stats.get('Association Rejection', 0) or 0
                i_df[client]['Connected'] += stats.get('Connected', 0) or 0
                i_df[client]['Iterations'] += 1

        # Create DataFrame
        df_summary = pd.DataFrame.from_dict(i_df, orient='index').reset_index()
        df_summary = df_summary.rename(columns={'index': 'Client'})
        self.result_df = df_summary.copy()
        # Save and print
        df_summary.to_csv(f"{self.report_path}/overall_reset.csv", index=False)
        if self.dowebgui:
            df_summary.to_csv(f"{self.result_dir}/overall_reset.csv", index=False)
        print(df_summary)


def main():
    help_summary = '''\
    The LANforge interop port reset test enables users to use real Wi-Fi stations and connect them to the Access Point
    being tested. It then disconnects and reconnects a given number of stations at different time intervals.
    This test helps evaluate how well the AP handles a dynamic and busy network environment with devices joining and
    leaving the network at random times.

    The test will basically disconnect & reconnect to the same network with real devices such as android, linux, windows
    and generate a report.
        '''
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        allow_abbrev=False,
        description='''
NAME: lf_interop_port_reset_test.py

PURPOSE:
         The LANforge interop port reset test enables users to use real Wi-Fi stations and connect them to the
         Access Point (AP) being tested. It then disconnects and reconnects a given number of stations at
         different time intervals. This test helps evaluate how well the AP handles a dynamic and busy network environment
         with devices joining and leaving the network at random times.

EXAMPLE:
        # To run port-reset test on specified real devices (android, laptops)

            python3 lf_interop_port_reset_test.py --lanforge_ip 192.168.200.63 --upstream_port 192.168.1.61 --dut Test_Dut
            --ssid RDT_wpa2 --passwd OpenWifi --encryp psk2 --iterations 1 --reset_interval 5 --android_releases 11

        # To run port-reset test on specified real devices with only coordinates

            python3 lf_interop_port_reset_test.py --lanforge_ip 192.168.207.78 --upstream_port eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --iterations 2 --reset_interval 5 --robot_test --coordinate 4,3  --robot_ip 192.168.200.169 --device_list ubuntu24

         # To run port-reset test on specified real devices with only coordinates and rotations

            python3 lf_interop_port_reset_test.py --lanforge_ip 192.168.207.78 --upstream_port eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --iterations 2 --reset_interval 5 --robot_test --coordinate 4,3 --rotation 30,45 --robot_ip 192.168.200.169 --device_list ubuntu24

SCRIPT_CLASSIFICATION:  Interop Port-Reset Test

SCRIPT_CATEGORIES: Toggling, Report Generation, Each Reset Wifi Messages

NOTES:
        The primary objective of this script is to automate the process of toggling WiFi on real devices with the
       InterOp Application, evaluating their performance with an access point. It achieves this by simulating multiple
       WiFi resets as specified by the user.

      * Currently the script will work for the REAL CLIENTS (android with version 11+, laptop devices).

STATUS: Functional

VERIFIED_ON:   28-OCT-2023,
             GUI Version:  5.4.7
             Kernel Version: 6.2.16+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README: False
''')

    parser.add_argument("--lanforge_ip", default='192.168.1.31',
                        help='Specify the LANforge GUI to connect to, assumes port 8080')

    parser.add_argument("--lanforge_port", default='8080', help='Specify the LANforge manager HTTP port')

    parser.add_argument("--upstream_port", default='192.168.1.31',
                        help='Specify the upstream port feeding the DUT, either as a port name '
                             '(e.g. eth1) or as its IP')

    parser.add_argument("--dut", default="TestDut",
                        help='Specify DUT name on which the test will be running.')

    parser.add_argument("--ssid", default="Netgear2g",
                        help='Specify ssid on which the test will be running.')

    parser.add_argument("--passwd", default="Password@123",
                        help='Specify encryption password  on which the test will be running.')

    parser.add_argument("--encryp", default="psk2",
                        help='Specify the encryption type  on which the test will be running eg :open|psk|psk2|sae|psk2jsae')

    parser.add_argument("--iterations", type=int, default=2,
                        help='Specify how many reset iterations to run. eg: 2')

    parser.add_argument("--reset_interval", type=int, default=5,
                        help='Specify the time interval in seconds to wait between reset iterations.')

    parser.add_argument('--device_list', help='Enter the devices on which the test should be run', default=None)

    parser.add_argument('--no_forget_networks',
                        help='Currently enterprise authentication does not support forget all networks.'
                        'So, mention this argument when enterprise securities are selected.', default=None,
                        action="store_true")
    # parser.add_argument("--wait_time", type=int, default=20,
    #                     help='Specify the wait time in seconds for WIFI Supplicant Logs.')

    parser.add_argument("--android_releases", nargs='*', default=["12"],
                        help='Specify which Android releases (SDK versions) may take part in the test; android '
                             'devices on any other release are skipped. Laptops are unaffected. '
                             'eg:- --android_releases 11 12 13')
    # logging configuration:
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    parser.add_argument('--dowebgui', help="If true will execute script for webgui", action='store_true')

    parser.add_argument('--result_dir', help='Specify the result dir to store the runtime logs', default='')
    parser.add_argument('--test_name', help='Specify test name to store the runtime csv results', default=None)
    parser.add_argument("--robot_test", help='to trigger robot test', action='store_true')
    parser.add_argument('--robot_ip', type=str, default='localhost', help='hostname for where Robot server is running')
    parser.add_argument('--robot_port', type=str, default=5000, help='port Robot HTTP service is running on')
    parser.add_argument('--coordinate', type=str, default='', help="The coordinate contains list of coordinates to be ")
    parser.add_argument('--rotation', type=str, default='', help="The set of angles to rotate at a particular point")
    parser.add_argument('--get_live_view', help="If true will heatmap will be generated from testhouse automation WebGui ", action='store_true')
    parser.add_argument('--total_floors', help="Total floors from testhouse automation WebGui ", default="0")
    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set the logger level to debug
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    port_reset_test = InteropPortReset(lanforge_ip=args.lanforge_ip,
                                       lanforge_port=args.lanforge_port,
                                       dut=args.dut,
                                       ssid=args.ssid,
                                       passwd=args.passwd,
                                       encryption=args.encryp,
                                       iterations=args.iterations,
                                       # clients=args.clients,
                                       reset_interval_sec=args.reset_interval,
                                       android_releases=args.android_releases,
                                       upstream_port=args.upstream_port,
                                       device_list=args.device_list,
                                       forget_network=not args.no_forget_networks,
                                       dowebgui=args.dowebgui,
                                       result_dir=args.result_dir,
                                       test_name=args.test_name,
                                       robot_test=args.robot_test,
                                       robot_ip=args.robot_ip,
                                       robot_port=args.robot_port,
                                       coordinate=args.coordinate,
                                       rotation=args.rotation,
                                       get_live_view=args.get_live_view,
                                       total_floors=args.total_floors
                                       )

    port_reset_test.upstream_port = port_reset_test.change_port_to_ip(port_reset_test.upstream_port)
    port_reset_test.base_interop_profile.server_ip = port_reset_test.upstream_port
    print(port_reset_test.upstream_port)

    port_reset_test.selecting_devices_from_available()
    if port_reset_test.robot_test:
        port_reset_test.run()
    else:
        per_iteration_results, test_duration = port_reset_test.run()
    if args.dowebgui:
        port_reset_test.result_df['Status'] = 'stopped'
        if port_reset_test.robot_test:
            port_reset_test.result_df.to_csv(f"{port_reset_test.report_path}/overall_reset_{port_reset_test.current_coordinate}.csv", index=False)
            port_reset_test.result_df.to_csv(f"{port_reset_test.result_dir}/overall_reset_{port_reset_test.current_coordinate}.csv", index=False)
        else:
            port_reset_test.result_df.to_csv(f"{port_reset_test.report_path}/overall_reset.csv", index=False)
            port_reset_test.result_df.to_csv(f"{port_reset_test.result_dir}/overall_reset.csv", index=False)
    if port_reset_test.robot_test:
        port_reset_test.generate_report_for_robo()
    else:
        port_reset_test.generate_report(reset_dict=per_iteration_results, test_dur=test_duration)


if __name__ == '__main__':
    main()
