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

            ./lf_interop_port_reset_test.py --host 192.168.200.192 --mgr_ip 192.168.1.161 --dut TestDut --ssid OpenWifi
            --passwd OpenWifi --encryp psk2 --reset 10 --time_int 5 --release 11

        # To run port-reset test on specified real devices with only coordinates

            ./lf_interop_port_reset_test.py --host 192.168.207.78 --mgr_ip eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --reset 2 --time_int 5 --robot_test --coordinate 4,3  --robot_ip 192.168.200.169 --device_list ubuntu24

        # To run port-reset test on specified real devices with only coordinates and rotations

            ./lf_interop_port_reset_test.py --host 192.168.207.78 --mgr_ip eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --reset 2 --time_int 5 --robot_test --coordinate 4,3 --rotation 30,45 --robot_ip 192.168.200.169 --device_list ubuntu24

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
          Copyright 2023 Candela Technologies Inc

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
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class InteropPortReset(Realm):
    def __init__(self, host,
                 port=8080,
                 dut=None,
                 ssid=None,
                 passwd=None,
                 encryp=None,
                 reset=None,
                 mgr_ip=None,
                 time_int=None,
                 wait_time=None,
                 device_list=None,
                 suporrted_release=None,
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
        super().__init__(lfclient_host=host,
                         lfclient_port=8080)
        self.total_connects = []
        self.total_ass_rejects = []
        self.total_ass_attemst = []
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
        self.host = host
        self.port = port
        self.phn_name = []
        self.dut_name = dut
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        self.mgr_ip = mgr_ip
        self.reset = reset
        self.time_int = time_int
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
        # self.wait_time = wait_time
        self.supported_release = suporrted_release
        self.device_name = []
        self.lf_report = lf_report_pdf.lf_report(_path="" if not self.dowebgui else self.result_dir, _results_dir_name="Interop_port_reset_test",
                                                 _output_html="port_reset_test.html",
                                                 _output_pdf="port_reset_test.pdf")
        self.report_path = self.lf_report.get_report_path()

        self.base_interop_profile = base.RealDevice(manager_ip=self.host, server_ip=self.mgr_ip, ssid_5g=self.ssid,
                                                    encryption_5g=self.encryp, passwd_5g=self.passwd, disconnect_devices=self.forget_network, reboot=False, selected_bands=["5g"])

        self.utility = base.UtilityInteropWifi(host_ip=self.host)
        # logging.basicConfig(filename='port_reset.log', filemode='w', format='%(asctime)s - %(message)s',
        #                     level=logging.INFO, force=True)

    def selecting_devices_from_available(self):
        # If device list is not provided by user, then it shows the available devices to choose from
        if self.device_list is None:
            devices = self.base_interop_profile.query_all_devices_to_configure_wifi()
        else:
            devices = self.base_interop_profile.query_all_devices_to_configure_wifi(device_list=self.device_list.split(','))
        asyncio.run(self.base_interop_profile.configure_wifi(devices[0] + devices[1] + devices[2]))
        self.real_sta_list = self.base_interop_profile.station_list
        logger.info(self.real_sta_list)
        real_device_data = self.base_interop_profile.devices_data
        if len(self.real_sta_list) == 0:
            logging.error('There are no real devices in this testbed. Aborting the test.')
            # Added for the purpose to stop webui test when there are no selected devices availble in lanforge.
            raise RuntimeError("here are no real devices in this testbed. Aborting the test.")
        logging.info(f"{self.real_sta_list}")

        for sta_name in self.real_sta_list:
            if sta_name not in real_device_data:
                logger.error('Real Station not in devices data')
                raise ValueError('Real station not in devices data')
        android_list = self.base_interop_profile.android_list

        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=self.port,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        supported_dict = self.interop.supported_devices_resource_id
        print("Supported dict", supported_dict)
        self.final_selected_android_list = []
        for key in supported_dict.keys():
            if key != "":
                if any(key in item for item in android_list):
                    self.final_selected_android_list.append(supported_dict[key])
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
        a = self.json_get("/wifi-msgs/last/1", debug_=True)
        last = a['wifi-messages']['time-stamp']
        logging.info(f"Last WiFi Message Time Stamp: {last}")
        return last

    def get_count(self, value=None, keys_list=None, device=None, filter=None):
        count_ = []
        device_split = device.split(".")
        device = device_split[2]
        resource_id = device_split[0] + "." + device_split[1]
        for i, y in zip(keys_list, range(len(keys_list))):
            wifi_msg_text = value[y][i]['text']
            resource = value[y][i]['resource']
            if type(wifi_msg_text) is str:
                wifi_msg_text_keyword_list = value[y][i]['text'].split(" ")
                if device is None:
                    logging.info(f"Device {device} is None device name not existed in wifi messages...")
                else:
                    if resource == resource_id:
                        if device in wifi_msg_text_keyword_list:
                            if filter in wifi_msg_text_keyword_list:
                                # logging.info(f"The filter '{filter}' is present in the Wi-Fi message test list.")
                                count_.append("YES")
                            else:
                                with_empty_filter = filter.split(" ")
                                if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                                    # logging.info(f"The filter {with_empty_filter} sequence is present in Wi-Fi msg.")
                                    count_.append("YES")
                        else:
                            if f"IFNAME={device}" in wifi_msg_text_keyword_list:  # for linux
                                if filter in wifi_msg_text_keyword_list:
                                    # logging.info(f"The filter '{filter}' is present in the Wi-Fi message test list.")
                                    count_.append("YES")
                                else:
                                    with_empty_filter = filter.split(" ")
                                    if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                                        # logging.info(f"The filter {with_empty_filter} sequence is present in Wi-Fi msg.")
                                        count_.append("YES")
            else:  # if wifi_msg_test is list
                for item in wifi_msg_text:
                    wifi_msg_text_keyword_list = item.split(" ")
                    # print("$Wifi Message Text list:", wifi_msg_text_keyword_list)
                    if device is not None:
                        if resource == resource_id:
                            if device in wifi_msg_text_keyword_list:  # for android
                                if filter in wifi_msg_text_keyword_list:
                                    # logging.info(f"The filter '{filter}' is present in the Wi-Fi message test list.")
                                    count_.append("YES")
                                else:
                                    with_empty_filter = filter.split(" ")
                                    if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                                        # logging.info(f"The filter {with_empty_filter} sequence is present in Wi-Fi msg.")
                                        count_.append("YES")
                            else:
                                if f"IFNAME={device}" in wifi_msg_text_keyword_list:  # for linux
                                    if filter in wifi_msg_text_keyword_list:
                                        # logging.info(f"The filter '{filter}' is present in the Wi-Fi message test list.")
                                        count_.append("YES")
                                    else:
                                        with_empty_filter = filter.split(" ")
                                        if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                                            # logging.info(f"The filter {with_empty_filter} sequence is present in Wi-Fi msg.")
                                            count_.append("YES")
        counting = count_.count("YES")
        return counting

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None, timee=None, file_name="dummy.json", reset_cnt=None):
        # print("Waiting for 20 sec to fetch the logs...")
        # time.sleep(20)
        a = self.json_get("/wifi-msgs/since=time/" + str(timee), debug_=True)
        values = a['wifi-messages']
        # print("Wifi msgs Response : ", values)
        logging.info(
            f"Counting the DISCONNECTIONS, SCANNING, ASSOC ATTEMPTS, ASSOC RECJECTIONS, CONNECTS for device {phn_name}")
        if type(values) is not list:
            logging.info(f"Device {phn_name} : Getting wifi messages for only single time-stamp. Converting into List.")
            values = [{f"{values['resource']}.{values['time-stamp']}": values}]
        # print("After Updating Wi-Fi msgs Response : ", values)
        self.create_log_file(json_list=values, file_name=file_name)
        self.remove_files_with_duplicate_names(folder_path=f"{self.report_path}/Wifi_Messages/")
        keys_list = []

        for i in range(len(values)):
            keys_list.append(list(values[i].keys())[0])
        # print("Key list", keys_list)
        # android (flag) check for clustered lanforge cases
        android = False
        for device_data in self.json_get('/adb/')['devices']:
            device_name, _ = list(device_data.keys())[0], list(device_data.values())[0]
            if phn_name in device_name:
                android = True
                break
        if "1.1." in phn_name or android:
            # disconnects
            adb_disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                  filter="Terminating...")  # Todo: need to rename the method
            if adb_disconnect_count > 1 or adb_disconnect_count == 0:
                disconnection = self.utility.get_device_state(device=phn_name)
                if disconnection == 'COMPLETED':
                    logging.info("The Device %s is in connected state." % phn_name)
                    adb_disconnect_count = 0
                else:
                    logging.info("The Device %s is not in connected state." % phn_name)
                    adb_disconnect_count = 1
                logging.info(f"Disconnect Count For Android: {adb_disconnect_count}")
            # Updating the dict with disconnects for android
            logging.info("Final Disconnect count for %s: %s" % (phn_name, adb_disconnect_count))
            local_dict[phn_name]["Disconnected"] = adb_disconnect_count
            # scanning count
            adb_scan_count = self.get_count(value=values, keys_list=keys_list, device=phn_name, filter="SCAN-STARTED")
            logging.info("Final Scanning Count for %s: %s" % (phn_name, adb_scan_count))
            local_dict[str(phn_name)]["Scanning"] = adb_scan_count
            # association attempts
            adb_association_attempt = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                     filter="ASSOCIATING")
            logging.info("Final Association Attempts Count for %s: %s" % (phn_name, adb_association_attempt))
            local_dict[str(phn_name)]["ConnectAttempt"] = adb_association_attempt
            # association rejections
            adb_association_rejection = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                       filter="ASSOC_REJECT")
            logging.info("Final Association Rejection Count for %s: %s" % (phn_name, adb_association_rejection))
            local_dict[str(phn_name)]["Association Rejection"] = adb_association_rejection
            # connections
            adb_connected_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                 filter="CTRL-EVENT-CONNECTED")
            # Double-checking & adding remarks if any
            if adb_connected_count > 1 or adb_connected_count == 0:
                ssid = self.utility.get_device_ssid(device=phn_name)
                if ssid == self.ssid:
                    logging.info("The Device %s is connected to expected ssid" % phn_name)
                    adb_connected_count = 1
                else:
                    logging.info("**** The Device is not connected to the expected ssid ****")
                    adb_connected_count = 0
                logging.info(f"Connected Count for Android: {adb_connected_count}")
            # Updating the dict with connects for android
            logging.info("Final Connected Count for %s: %s" % (phn_name, adb_connected_count))
            local_dict[str(phn_name)]["Connected"] = adb_connected_count
            # Adding remarks
            remarks = "NA"
            local_dict[str(phn_name)]["Remarks"] = remarks
            # Updating the association-rejections
            if adb_association_attempt > adb_connected_count:
                adb_association_rejection = adb_association_attempt - adb_connected_count
            local_dict[str(phn_name)]["Association Rejection"] = adb_association_rejection
            if adb_connected_count > 0:
                _, shelf, serial = phn_name.split('.')
                resource_id = self.json_get('/adb/1/{}/{}?fields=resource-id'.format(shelf, serial))
                resource_id = resource_id['devices']['resource-id']

                port_ssid_query = self.json_get('port/1/{}/wlan0?fields=cx time (us)'.format(resource_id.split('.')[1]))
                uptime = port_ssid_query['interface']['cx time (us)']
                local_dict[str(phn_name)]['cx time (us)'] = uptime
            else:
                local_dict[str(phn_name)]['cx time (us)'] = 'NA'
        else:
            if phn_name in self.windows_list:  # for windows
                win_disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                      filter="Wireless security stopped.")
                # Double-checking the disconnect count with another key msg
                if win_disconnect_count == 0:
                    win_disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                          filter="WLAN AutoConfig service has successfully disconnected from a wireless network")
                logging.info("Final Disconnect count for %s: %s" % (phn_name, win_disconnect_count))
                local_dict[phn_name]["Disconnected"] = win_disconnect_count
                win_scan_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                filter="service started")
                logging.info("Final Scanning Count for %s: %s" % (phn_name, win_scan_count))
                local_dict[str(phn_name)]["Scanning"] = win_scan_count
                win_association_attempt = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                         filter="association started.")
                logging.info("Final Association Attempts Count for %s: %s" % (phn_name, win_association_attempt))
                local_dict[str(phn_name)]["ConnectAttempt"] = win_association_attempt
                win_association_rejection = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                           filter="failed to connect")
                logging.info("Final Association Rejection Count for %s: %s" % (phn_name, win_association_rejection))
                local_dict[str(phn_name)]["Association Rejection"] = win_association_rejection
                win_connected_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                     filter="connected")
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
                            port_name = phn_name.split(".")
                            port_ssid_query = self.json_get(f"port/{port_name[0]}/{port_name[1]}/{port_name[2]}?fields=ssid,ip")
                            if port_ssid_query['interface']['ssid'] == self.ssid and port_ssid_query['interface']['ip'] != "0.0.0.0":
                                win_connected_count = 1
                            else:
                                win_connected_count = 0
                logging.info("Final Connected Count for %s: %s" % (phn_name, win_connected_count))
                local_dict[str(phn_name)]["Connected"] = win_connected_count
                # Updating the association-rejections
                if win_association_attempt > win_connected_count:
                    win_association_rejection = win_association_attempt - win_connected_count
                local_dict[str(phn_name)]["Association Rejection"] = win_association_rejection
                # Adding re-marks
                remarks = "NA"
                if win_disconnect_count == 0 and win_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif win_disconnect_count >= 1 and win_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                local_dict[str(phn_name)]["Remarks"] = remarks
                if win_connected_count > 0:
                    port_name = phn_name.split(".")
                    port_ssid_query = self.json_get(f"port/{port_name[0]}/{port_name[1]}/{port_name[2]}?fields=cx time (us)")
                    uptime = port_ssid_query['interface']['cx time (us)']
                    local_dict[str(phn_name)]['cx time (us)'] = uptime
                else:
                    local_dict[str(phn_name)]['cx time (us)'] = 'NA'
            else:  # other means (for linux, mac)
                other_disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                        filter="disconnected")
                # Double-checking the disconnect count with another key msg
                if other_disconnect_count == 0:
                    other_disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                            filter="<3>CTRL-EVENT-DSCP-POLICY clear_all")
                logging.info("Final Disconnect count for %s: %s" % (phn_name, other_disconnect_count))
                local_dict[phn_name]["Disconnected"] = other_disconnect_count
                other_scan_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                  filter="<3>CTRL-EVENT-SCAN-STARTED")
                logging.info("Final Scanning Count for %s: %s" % (phn_name, other_scan_count))
                local_dict[str(phn_name)]["Scanning"] = other_scan_count
                other_association_attempt = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                           filter="<3>Trying to associate with")
                logging.info("Final Association Attempts Count for %s: %s" % (phn_name, other_association_attempt))
                local_dict[str(phn_name)]["ConnectAttempt"] = other_association_attempt
                other_association_rejection = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                             filter="NoneValue")
                logging.info("Final Association Rejection Count for %s: %s" % (phn_name, other_association_rejection))
                local_dict[str(phn_name)]["Association Rejection"] = other_association_rejection

                other_connected_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                                       filter="<3>CTRL-EVENT-CONNECTED")
                # assoc-rejection based logic
                if other_association_rejection:
                    # Updating the connects
                    actual_connects = other_association_attempt - other_association_rejection
                    if actual_connects == other_connected_count:
                        other_connected_count = other_connected_count
                    else:
                        other_connected_count = actual_connects
                else:
                    if other_association_attempt == other_connected_count:
                        other_connected_count = other_connected_count
                    else:
                        # Double-checking & adding remarks if any
                        if other_connected_count > 1 or other_connected_count == 0:
                            port_name = phn_name.split(".")
                            port_ssid_query = self.json_get(f"port/{port_name[0]}/{port_name[1]}/{port_name[2]}?fields=ssid,ip")
                            if port_ssid_query['interface']['ssid'] == self.ssid and port_ssid_query['interface']['ip'] != "0.0.0.0":
                                other_connected_count = 1
                            else:
                                other_connected_count = 0
                logging.info("Final Connected Count for %s: %s" % (phn_name, other_connected_count))
                local_dict[str(phn_name)]["Connected"] = other_connected_count
                # Updating the association-rejections
                if other_association_attempt > other_connected_count:
                    other_association_rejection = other_association_attempt - other_connected_count
                local_dict[str(phn_name)]["Association Rejection"] = other_association_rejection
                # Adding remarks
                remarks = "NA"
                if other_disconnect_count == 0 and other_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif other_disconnect_count >= 1 and other_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                local_dict[str(phn_name)]["Remarks"] = remarks
                if other_connected_count > 0:
                    port_name = phn_name.split(".")
                    port_ssid_query = self.json_get(f"port/{port_name[0]}/{port_name[1]}/{port_name[2]}?fields=cx time (us)")
                    uptime = port_ssid_query['interface']['cx time (us)']
                    local_dict[str(phn_name)]['cx time (us)'] = uptime
                else:
                    local_dict[str(phn_name)]['cx time (us)'] = 'NA'
        logging.info("local_dict " + str(local_dict))
        # storing results in csv file for each reset
        for interface_name, metrics in local_dict.items():
            df = pd.DataFrame([metrics])
            filename = f"{self.report_path}/{interface_name}_{reset_cnt}.csv"
            df.to_csv(filename, index=False)

        return local_dict

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
        reset_list = []
        for i in range(self.reset):
            reset_list.append(i)
        logging.info(f"Given No.of iterations for Reset : {len(reset_list)}")
        logging.info("Reset list:" + str(reset_list))
        reset_dict = dict.fromkeys(reset_list)
        test_stopped = False
        interval = 300
        test_stopped_by_user = False
        charge_check = time.time() + interval
        for r, _ in zip(range(self.reset), reset_dict):
            if self.robot_test:
                current_time = time.time()
                if current_time >= charge_check:
                    if test_stopped_by_user or self.robo_test_stopped:
                        break
                    pause, test_stopped_by_user = self.robot_obj.wait_for_battery()
                    if test_stopped_by_user:
                        break
                    if pause:
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
                            rotation_moni = self.robot_obj.rotate_angle(self.current_angle)
                            if not rotation_moni:
                                test_stopped_by_user = True
                                break
                    charge_check = current_time + interval
            logging.info(f"Waiting until given {self.time_int} sec time intervel to finish...")
            time.sleep(int(self.time_int))  # sleeping until time interval finish
            logging.info(f"Iteration :- {r}")
            logging.info("Reset -" + str(r))
            local_dict = dict.fromkeys(self.adb_device_list)
            logging.info(f"local dict for android :{local_dict}")
            laptop_local_dict = dict.fromkeys(self.all_laptops)
            logging.info(f"local dict for laptops : {laptop_local_dict}")
            local_dict.update(laptop_local_dict)

            list_ = ["ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected"]
            sec_dict = dict.fromkeys(list_)

            for i in self.adb_device_list:
                local_dict[i] = sec_dict.copy()  # for android devices dict
            for i in self.all_laptops:
                laptop_local_dict[i] = sec_dict.copy()  # for laptop devices dict
            logging.info(f"Final Outcome dict for android devices: {local_dict}")
            logging.info(f"Final Outcome dict for laptop devices: {laptop_local_dict}")
            logging.info(str(local_dict))

            local_dict.update(laptop_local_dict)
            logging.info(f"Final dict: {local_dict}")

            # note last log time
            timee = self.get_last_wifi_msg()

            for i in self.adb_device_list:
                self.interop.stop(device=i)
            for i in self.all_laptops:  # laptop admin down
                logging.info(f"**** Disable wifi for laptop {i}")
                self.admin_down(port_eid=i)
            for i in self.adb_device_list:
                logging.info(f"**** Disable wifi for android {i}")
                logging.info("disable wifi")
                self.interop.enable_or_disable_wifi(device=i, wifi="disable")
            for i in self.all_laptops:  # laptop admin up
                logging.info(f"**** Enable wifi for laptop {i}")
                self.admin_up(port_eid=i)
            for i in self.adb_device_list:
                logging.info(f"*** Enable wifi for laptop {i}")
                logging.info("enable wifi")
                self.interop.enable_or_disable_wifi(device=i, wifi="enable")
            for i in self.adb_device_list:
                logging.info(f"Starting APP for {i}")
                self.interop.start(device=i)
            if self.all_laptops:
                if self.wait_for_ip(station_list=self.all_laptops, timeout_sec=60):
                    logging.info("PASSED : ALL STATIONS GOT IP")
                else:
                    logging.info("FAILED : MAY BE NOT ALL STATIONS ACQUIRED IP'S")
            time.sleep(30)
            for i in self.all_selected_devices:
                get_dicct = self.get_time_from_wifi_msgs(local_dict=local_dict, phn_name=i, timee=timee,
                                                         file_name=f"reset_{r}_log.json", reset_cnt=r)
                reset_dict[r] = get_dicct
                if self.robot_test:
                    self.generate_coordinate_csv(reset_dict=reset_dict, r=r)
                else:
                    self.create_dict_csv(reset_dict)
                if self.dowebgui:
                    with open(self.result_dir + f"/../../Running_instances/{self.host}_{self.test_name}_running.json",
                              'r') as file:
                        data = json.load(file)
                        if data["status"] != "Running":
                            logging.info('Test is stopped by the user')
                            test_stopped = True
                            self.robo_test_stopped = True
                            break
            logging.info('{}'.format(reset_dict))
            if test_stopped:
                temp_data = {
                    'ConnectAttempt': 0,
                    'Disconnected': 0,
                    'Scanning': 0,
                    'Association Rejection': 0,
                    'Connected': 0,
                    'Remarks': "Test stopped by user",
                    'cx time (us)': 0
                }
                keys_to_delete = []
                for i in range(self.reset):
                    if reset_dict.get(i) is None:
                        keys_to_delete.append(i)
                    else:
                        for dev, data in reset_dict[i].items():
                            if any(v is None for v in data.values()):
                                reset_dict[i][dev] = temp_data.copy()

                for key in keys_to_delete:
                    del reset_dict[key]

                break
        logging.info(f"Final Reset Count Dictionary for all clients: {reset_dict}")
        logging.info("reset dict " + str(reset_dict))
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
        s1 = test_start_time
        s2 = test_end_time
        FMT = '%b %d %H:%M:%S'
        test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
        if self.robot_test:
            if self.rotation_enabled:
                logging.info(f"Total Test Duration taken to complete port resets at coordinate {self.current_coordinate} on angle {self.current_angle}: {test_duration}")
            else:
                logging.info(f"Total Test Duration taken to complete port resets at coordinate {self.current_coordinate} : {test_duration}")
        else:
            logging.info(f"Total Test Duration: {test_duration}")

        return reset_dict, test_duration

    # @property
    def run(self):
        try:
            # start timer
            present_time = datetime.now()
            test_start_time = present_time.strftime("%b %d %H:%M:%S")
            logging.info(f"Test Started at {present_time}")
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
                for i in range(len(self.adb_device_list)):
                    self.phn_name.append(self.adb_device_list[i].split(".")[2])
                logging.info(f"Separated device names from the full name: {self.phn_name}")

            # check status of devices
            phantom = []
            for i in self.adb_device_list:
                phantom.append(self.interop.get_device_details(device=i, query="phantom"))
            if self.adb_device_list or self.windows_list or self.linux_list or self.mac_list:
                for i in self.adb_device_list:
                    self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
                logging.info(f"ADB user-names for selected devices: {self.device_name}")
                logging.info("Checking heath data...")
                health = dict.fromkeys(self.adb_device_list)
                logging.info(f"Initial Health Data For Android Clients: {health}")
                health_for_laptops = dict.fromkeys(self.all_laptops)
                logging.info(f"Initial Health Data For Laptops Clients: {health_for_laptops}")

                # pre-checking whether the adb device connected to given ssid or not
                for i in self.adb_device_list:
                    dev_state = self.utility.get_device_state(device=i)
                    if dev_state == "COMPLETED,":
                        logging.info("Phone %s is in connected state." % i)
                        ssid = self.utility.get_device_ssid(device=i)
                        if ssid == self.ssid:
                            logging.info("The Device %s is connected to expected ssid (%s)" % (i, ssid))
                            health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            logging.info("**** The Device is not connected to the expected ssid ****")
                    else:
                        # logging.info(f"Waiting for {self.wait_time} sec & Checking again the status of the device")
                        logging.info("Waiting for 30 sec & Checking again")
                        time.sleep(30)
                        dev_state = self.utility.get_device_state(device=i)
                        logging.info("Checking Device Status Again..." + str(dev_state))
                        logging.info(f"Device state {dev_state}")
                        if dev_state == "COMPLETED,":
                            logging.info("Phone is in connected state")
                            ssid = self.utility.get_device_ssid(device=i)
                            if ssid == self.ssid:
                                logging.info("The Device %s is connected to expected ssid (%s)" % (i, ssid))
                                health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            logging.info(f"device state {dev_state}")
                            health[i] = {'ConnectAttempt': '0', 'ConnectFailure': '0', 'AssocRej': '0',
                                         'AssocTimeout': '0'}
                logging.info(f"Health Status for the Android Devices: {health}")

                logging.info(f"Health Status for the Laptop Devices: {health_for_laptops}")
                # Resting Starts from here
                if not self.robot_test:
                    reset_dict, test_duration = self.performing_resets(test_start_time=test_start_time)
                    return reset_dict, test_duration

                # For robot Scenario
                if (self.rotation_list[0] != ""):
                    self.rotation_enabled = True
                self.robot_obj = RobotClass()
                self.robot_obj.robo_ip = self.robot_ip
                base_dir = os.path.dirname(os.path.dirname(self.result_dir))
                nav_data = os.path.join(base_dir, 'nav_data.json')  # To generate nav_data.json in webgui folder
                self.robot_obj.nav_data_path = nav_data
                self.robot_obj.create_waypointlist()
                self.robot_obj.ip = self.host
                self.robot_obj.testname = self.test_name
                self.robot_obj.runtime_dir = self.result_dir
                test_stopped_by_user = False
                for coordinate in range(len(self.coordinate_list)):
                    if test_stopped_by_user or self.robo_test_stopped:
                        break
                    # Check for battery status before moving to next coordinate
                    if_paused, test_stopped_by_user = self.robot_obj.wait_for_battery()
                    # If test is stopped by user during battery wait
                    if test_stopped_by_user:
                        break
                    robo_moved, abort = self.robot_obj.move_to_coordinate(self.coordinate_list[coordinate])
                    # If robot failed to reach the coordinate
                    if abort:
                        break
                    if robo_moved:
                        self.current_coordinate = self.coordinate_list[coordinate]
                        if not self.rotation_enabled:
                            reset_dict, test_duration = self.performing_resets(test_start_time=test_start_time)
                            self.port_reset_data[self.coordinate_list[coordinate]] = {'reset_dict': reset_dict, 'test_duration': test_duration}
                            time.sleep(10)
                        else:
                            for angle in range(len(self.rotation_list)):
                                # If test is stopped by user during battery wait
                                if self.robo_test_stopped or test_stopped_by_user:
                                    break
                                # Check for battery status before rotating to next angle
                                is_paused, test_stopped_by_user = self.robot_obj.wait_for_battery()
                                robo_rotated = self.robot_obj.rotate_angle(self.rotation_list[angle])
                                if robo_rotated:
                                    self.current_angle = self.rotation_list[angle]
                                    reset_dict, test_duration = self.performing_resets(test_start_time=test_start_time)
                                if self.coordinate_list[coordinate] not in self.port_reset_data:
                                    self.port_reset_data[self.coordinate_list[coordinate]] = {}
                                self.port_reset_data[self.coordinate_list[coordinate]][self.rotation_list[angle]] = {'reset_dict': reset_dict, 'test_duration': test_duration}

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
        data['Port Resets'] = self.reset * len(self.all_selected_devices)

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
            self.total_resets, self.total_disconnects, self.total_scans, self.total_ass_attemst, self.total_ass_rejects, self.total_connects = [], [], [], [], [], []
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
            data['Port Resets'] = self.reset

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
            self.total_resets.append(self.reset)
            self.total_disconnects.append(sum(disconnected))
            self.total_scans.append(sum(scanning))
            self.total_ass_attemst.append(sum(asso_attempts))
            self.total_ass_rejects.append(sum(assorej))
            self.total_connects.append(sum(connected))

    def individual_client_info(self, reset_dict, device_list):
        # per client table and graphs
        # self.total_resets, self.total_disconnects, self.total_scans, self.total_ass_attemst, self.total_ass_rejects, self.total_connects = [], [], [], [], [], []
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
            data['Port Resets'] = self.reset

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
            if self.encryp == "psk2":
                security = "wpa2"
            elif self.encryp == "psk3":
                security = "wpa3"
            elif self.encryp == "psk":
                security = "wpa"
            else:
                security = "open"
            test_setup_info = {
                "DUT Name": self.dut_name,
                "LANforge ip": self.host,
                "SSID": self.ssid,
                "Security": security,
                "Total Reset Count": self.reset,
                "No of Clients": f"{len(self.all_selected_devices)} (Windows: {len(self.windows_list)}, Linux: {len(self.linux_list)}, Mac: {len(self.mac_list)}, Android: {len(self.adb_device_list)})",  # noqa: E501
                # "Wait Time": str(self.wait_time) + " sec",
                "Time intervel between resets": str(self.time_int) + " sec",
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
                                        # " Here real clients used is "+ str(self.clients) + "and number of resets provided is " + str(self.reset)
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

            for y in all_devices:
                if "1.1." in y:
                    d_name.append(self.interop.get_device_details(device=y, query="name"))
                    device_type.append(self.interop.get_device_details(device=y, query="device-type"))
                    # model.append(self.interop.get_device_details(device=y, query="model"))
                    user_name.append(self.interop.get_device_details(device=y, query="user-name"))
                    # release.append(self.interop.get_device_details(device=y, query="release"))
                else:
                    d_name.append(y)
                    user_name.append(self.interop.get_laptop_devices_details(device=y, query="host_name"))
                    hw_version = self.interop.get_laptop_devices_details(device=y, query="hw_version")
                    if "Linux" in hw_version:
                        dev_type = "Linux"
                    elif "Win" in hw_version:
                        dev_type = "Windows"
                    elif "Apple" in hw_version:
                        dev_type = "Apple"
                    else:
                        dev_type = ""
                    device_type.append(dev_type)
                    # release.append("")
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
                "Assoc Attemts": self.total_ass_attemst,
                "Assoc Rejects": self.total_ass_rejects,
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
        if self.encryp == "psk2":
            security = "wpa2"
        elif self.encryp == "psk3":
            security = "wpa3"
        elif self.encryp == "psk":
            security = "wpa"
        else:
            security = "open"
        test_setup_info = {
            "DUT Name": self.dut_name,
            "LANforge ip": self.host,
            "SSID": self.ssid,
            "Security": security,
            "Total Reset Count": self.reset,
            "No of Clients": f"{len(self.all_selected_devices)} (Windows: {len(self.windows_list)}, Linux: {len(self.linux_list)}, Mac: {len(self.mac_list)}, Android: {len(self.adb_device_list)})",  # noqa: E501
            # "Wait Time": str(self.wait_time) + " sec",
            "Time intervel between resets": str(self.time_int) + " sec",
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
                                    # " Here real clients used is "+ str(self.clients) + "and number of resets provided is " + str(self.reset)
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

                    for y in all_devices:
                        if "1.1." in y:
                            d_name.append(self.interop.get_device_details(device=y, query="name"))
                            device_type.append(self.interop.get_device_details(device=y, query="device-type"))
                            # model.append(self.interop.get_device_details(device=y, query="model"))
                            user_name.append(self.interop.get_device_details(device=y, query="user-name"))
                            # release.append(self.interop.get_device_details(device=y, query="release"))
                        else:
                            d_name.append(y)
                            user_name.append(self.interop.get_laptop_devices_details(device=y, query="host_name"))
                            hw_version = self.interop.get_laptop_devices_details(device=y, query="hw_version")
                            if "Linux" in hw_version:
                                dev_type = "Linux"
                            elif "Win" in hw_version:
                                dev_type = "Windows"
                            elif "Apple" in hw_version:
                                dev_type = "Apple"
                            else:
                                dev_type = ""
                            device_type.append(dev_type)
                            # release.append("")
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
                        "Assoc Attemts": self.total_ass_attemst,
                        "Assoc Rejects": self.total_ass_rejects,
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

                for y in all_devices:
                    if "1.1." in y:
                        d_name.append(self.interop.get_device_details(device=y, query="name"))
                        device_type.append(self.interop.get_device_details(device=y, query="device-type"))
                        # model.append(self.interop.get_device_details(device=y, query="model"))
                        user_name.append(self.interop.get_device_details(device=y, query="user-name"))
                        # release.append(self.interop.get_device_details(device=y, query="release"))
                    else:
                        d_name.append(y)
                        user_name.append(self.interop.get_laptop_devices_details(device=y, query="host_name"))
                        hw_version = self.interop.get_laptop_devices_details(device=y, query="hw_version")
                        if "Linux" in hw_version:
                            dev_type = "Linux"
                        elif "Win" in hw_version:
                            dev_type = "Windows"
                        elif "Apple" in hw_version:
                            dev_type = "Apple"
                        else:
                            dev_type = ""
                        device_type.append(dev_type)
                        # release.append("")
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
                    "Assoc Attemts": self.total_ass_attemst,
                    "Assoc Rejects": self.total_ass_rejects,
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


def change_port_to_ip(upstream_port, lfclient_host, lfclient_port):
    if upstream_port.count('.') != 3:
        target_port_list = LFUtils.name_to_eid(upstream_port)
        shelf, resource, port, _ = target_port_list
        try:
            realm_obj = Realm(lfclient_host=lfclient_host, lfclient_port=lfclient_port)
            target_port_ip = realm_obj.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
            upstream_port = target_port_ip
        except Exception:
            logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
        logging.info(f"Upstream port IP {upstream_port}")
    else:
        logging.info(f"Upstream port IP {upstream_port}")

    return upstream_port


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
        description='''
NAME: lf_interop_port_reset_test.py

PURPOSE:
         The LANforge interop port reset test enables users to use real Wi-Fi stations and connect them to the
         Access Point (AP) being tested. It then disconnects and reconnects a given number of stations at
         different time intervals. This test helps evaluate how well the AP handles a dynamic and busy network environment
         with devices joining and leaving the network at random times.

EXAMPLE:
        # To run port-reset test on specified real devices (android, laptops)

            python3 lf_interop_port_reset_test.py --host 192.168.200.63 --mgr_ip 192.168.1.61 --dut Test_Dut
            --ssid RDT_wpa2 --passwd OpenWifi --encryp psk2 --reset 1 --time_int 5 --release 11

        # To run port-reset test on specified real devices with only coordinates

            python3 lf_interop_port_reset_test.py --host 192.168.207.78 --mgr_ip eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --reset 2 --time_int 5 --robot_test --coordinate 4,3  --robot_ip 192.168.200.169 --device_list ubuntu24

         # To run port-reset test on specified real devices with only coordinates and rotations

            python3 lf_interop_port_reset_test.py --host 192.168.207.78 --mgr_ip eth1 --dut AP --ssid "NETGEAR_2G_wpa2" --encryp psk2 --passwd Password@123
            --reset 2 --time_int 5 --robot_test --coordinate 4,3 --rotation 30,45 --robot_ip 192.168.200.169 --device_list ubuntu24

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
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
''')

    parser.add_argument("--host", default='192.168.1.31',
                        help='Specify the GUI to connect to, assumes port 8080')

    parser.add_argument("--port", default='8080', help='Specify the manager port')

    parser.add_argument("--mgr_ip", default='192.168.1.31',
                        help='Specify the interop manager ip')

    parser.add_argument("--dut", default="TestDut",
                        help='Specify DUT name on which the test will be running.')

    parser.add_argument("--ssid", default="Netgear2g",
                        help='Specify ssid on which the test will be running.')

    parser.add_argument("--passwd", default="Password@123",
                        help='Specify encryption password  on which the test will be running.')

    parser.add_argument("--encryp", default="psk2",
                        help='Specify the encryption type  on which the test will be running eg :open|psk|psk2|sae|psk2jsae')

    parser.add_argument("--reset", type=int, default=2,
                        help='Specify the number of time you want to reset. eg: 2')

    parser.add_argument("--time_int", type=int, default=5,
                        help='Specify the time interval in seconds after which reset should happen.')

    parser.add_argument('--device_list', help='Enter the devices on which the test should be run', default=None)

    parser.add_argument('--no_forget_networks',
                        help='Currently enterprise authentication does not support forget all networks.'
                        'So, mention this argument when enterprise securities are selected.', default=None,
                        action="store_true")
    # parser.add_argument("--wait_time", type=int, default=20,
    #                     help='Specify the wait time in seconds for WIFI Supplicant Logs.')

    parser.add_argument("--release", nargs='*', default=["12"],
                        help='Specify the SDK release version (Android Version) of real clients to be supported in test.'
                             'eg:- --release 11 12 13')
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
    args.mgr_ip = change_port_to_ip(args.mgr_ip, args.host, args.port)
    print(args.mgr_ip)
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    obj = InteropPortReset(host=args.host,
                           port=args.port,
                           dut=args.dut,
                           ssid=args.ssid,
                           passwd=args.passwd,
                           encryp=args.encryp,
                           reset=args.reset,
                           # clients=args.clients,
                           time_int=args.time_int,
                           # wait_time=args.wait_time,
                           suporrted_release=args.release,
                           mgr_ip=args.mgr_ip,
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
    obj.selecting_devices_from_available()
    if obj.robot_test:
        obj.run()
    else:
        reset_dict, duration = obj.run()
    if args.dowebgui:
        obj.result_df['Status'] = 'stopped'
        if obj.robot_test:
            obj.result_df.to_csv(f"{obj.report_path}/overall_reset_{obj.current_coordinate}.csv", index=False)
            obj.result_df.to_csv(f"{obj.result_dir}/overall_reset_{obj.current_coordinate}.csv", index=False)
        else:
            obj.result_df.to_csv(f"{obj.report_path}/overall_reset.csv", index=False)
            obj.result_df.to_csv(f"{obj.result_dir}/overall_reset.csv", index=False)
    if obj.robot_test:
        obj.generate_report_for_robo()
    else:
        obj.generate_report(reset_dict=reset_dict, test_dur=duration)


if __name__ == '__main__':
    main()
