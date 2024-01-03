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
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import logging

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
                 suporrted_release=None
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
        # self.wait_time = wait_time
        self.supported_release = suporrted_release
        self.device_name = []
        self.lf_report = lf_report_pdf.lf_report(_path="", _results_dir_name="Interop_port_reset_test",
                                                 _output_html="port_reset_test.html",
                                                 _output_pdf="port_reset_test.pdf")
        self.report_path = self.lf_report.get_report_path()

        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=self.port,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        self.base_interop_profile = base.RealDevice(manager_ip=self.host)

        self.utility = base.UtilityInteropWifi(host_ip=self.host)
        # logging.basicConfig(filename='port_reset.log', filemode='w', format='%(asctime)s - %(message)s',
        #                     level=logging.INFO, force=True)

    def selecting_devices_from_available(self):
        self.available_device_list = self.base_interop_profile.get_devices()
        self.user_query = self.base_interop_profile.query_user()
        logging.info("Available Devices List: {}".format(self.available_device_list))
        logging.info("Query Result: {}".format(self.user_query))
        android_list = self.base_interop_profile.android_list
        supported_dict = self.interop.supported_devices_resource_id
        self.final_selected_android_list = []
        for key in supported_dict.keys():
            if key != "":
                if any(key in item for item in android_list):
                    self.final_selected_android_list.append(supported_dict[key])
        logging.info(f"Final Android Serial Numbers List: {self.final_selected_android_list}")

    def getting_resources_data(self, windows_list, linux_list, mac_list):
        # fetching all devices from Resource Manager tab
        response = self.json_get('/resource/all')
        resources = response['resources']
        resources_list = []
        for resource_data in resources:
            port, resource = list(resource_data.keys())[0], list(resource_data.values())[0]
            shelf, resource_id = port.split('.')
            # filtering LANforges from resources
            if resource['ct-kernel']:
                continue
            # filtering Androids from resources
            if resource['user'] != '':
                continue
            # filtering phantom resources
            if resource['phantom']:
                logging.info('The laptop on port {} is in phantom state.'.format(port))
                continue
            hw_version = resource['hw version']
            # fetching data for Windows
            if windows_list:
                for win_device in windows_list:
                    if 'Win' in hw_version and port in win_device:
                        resources_list.append({
                            'os': 'Win',
                            'shelf': shelf,
                            'resource': resource_id,
                            'sta_name': win_device.split(".")[2],
                            # 'report_timer': 1500,
                            'current_flags': 2147483648,
                            'interest': 16384
                        })
            # fetching data for Linux
            if linux_list:
                for lin_device in linux_list:
                    if 'Lin' in hw_version and port in lin_device:
                        resources_list.append({
                            'os': 'Lin',
                            'shelf': shelf,
                            'resource': resource_id,
                            'sta_name': 'sta{}'.format(resource_id),
                            # 'sta_name': 'en0',
                            'current_flags': 2147483648,
                            'interest': 16384
                        })
            # fetching data for Mac
            if mac_list:
                for mac_device in mac_list:
                    if 'Apple' in hw_version and port in mac_device:
                        resources_list.append({
                            'os': 'Apple',
                            'shelf': shelf,
                            'resource': resource_id,
                            'sta_name': 'en0',
                            'current_flags': 2147483648,
                            'interest': 16384
                        })
        return resources_list

    def rm_stations(self, port_list=None):
        if port_list is None:
            port_list = []
        if not port_list:
            logging.info('Port list is empty')
            return
        data_list = []
        for port_data in port_list:
            if 'Lin' == port_data['os']:
                shelf, resource, sta_name = port_data['shelf'], port_data['resource'], port_data['sta_name']

                get_station_name = self.json_get('/ports/{}/{}/?fields=parent dev'.format(shelf, resource), debug_=True)
                # station_response = get_station_name.json()
                stations = get_station_name['interfaces']

                if type(stations) == list:
                    for station in stations:
                        station_name, station_details = list(station.keys())[0], list(station.values())[0]
                        if station_details['parent dev'] != '':
                            data = {
                                'shelf': shelf,
                                'resource': resource,
                                'port': station_name.split(".")[2]  # taking the exiting station names
                            }
                            data_list.append(data)
                            break
                elif type(stations) == dict:
                    logger.warning('The port {}.{} does not have the required interfaces'.format(shelf, resource))
        for i in data_list:
            self.json_post("/cli-json/rm_vlan", i)

    # add station
    def add_stations(self, port_list=None):
        if port_list is None:
            port_list = []
        if not port_list:
            logging.info('Port list is empty')
            return
        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            sta_name = port_data['sta_name']
            operating_system = port_data['os']
            if self.encryp == 'open':
                self.encrypt_value = 0
                self.passwd = 'NA'
            elif self.encryp == 'wpa' or self.encryp == 'psk':
                self.encrypt_value = 16
            elif self.encryp == "wpa2" or self.encryp == 'psk2':
                self.encrypt_value = 1024
            elif self.encryp == "wpa3" or self.encryp == 'psk3':
                self.encrypt_value = 1099511627776
            if operating_system == 'Lin':
                mac = 'xx:xx:xx:*:*:xx'
            else:
                mac = 'NA'
            data = {
                'shelf': shelf,
                'resource': resource,
                'radio': 'wiphy0',
                'sta_name': sta_name,
                'flags': self.encrypt_value,
                'ssid': self.ssid,
                'key': self.passwd,
                'mac': mac
            }
            data_list.append(data)
        for i in data_list:
            self.json_post("/cli-json/add_sta", i)

    # set port (enable DHCP)
    def set_ports(self, port_list=None):
        if port_list is None:
            port_list = []
        if not port_list:
            logging.info('Port list is empty')
            return
        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            interest = port_data['interest']

            os = port_data['os']
            if os in ['Apple', 'Lin']:
                current_flags = port_data['current_flags']
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': current_flags,
                    'interest': interest,
                    'mac': 'xx:xx:xx:*:*:xx'
                }
            elif os == 'Win':
                # report_timer = port_data['report_timer']
                current_flags = port_data['current_flags']
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    # 'report_timer': report_timer,
                    'current_flags': current_flags,
                    'interest': interest,
                }
            data_list.append(data)
        for i in data_list:
            self.json_post("/cli-json/set_port", i)
            time.sleep(5)

    def real_clients_connectivity(self, windows_list, linux_list, mac_list):
        # for laptops
        all_laptops = windows_list + linux_list + mac_list
        if windows_list or linux_list or mac_list:
            resource_list = self.getting_resources_data(windows_list=windows_list, linux_list=linux_list,
                                                        mac_list=mac_list)
            logging.info(f"Resource List: {resource_list}")
            if linux_list:
                self.rm_stations(port_list=resource_list)
            time.sleep(2)
            self.add_stations(port_list=resource_list)
            time.sleep(2)
            self.set_ports(port_list=resource_list)
            logging.info(f"Waiting {30} sec for authorizing the devices.")
            time.sleep(30)
            # check if the devices (windows, linux, mac) is connected to expected/given ssid or not
            for laptop in all_laptops:
                port_name = laptop.split(".")
                port_query = self.json_get(f"port/{port_name[0]}/{port_name[1]}/{port_name[2]}?fields=ssid,ip")
                ssid = port_query['interface']['ssid']
                ip = port_query['interface']["ip"]
                if ssid == self.ssid and ssid != '':
                    logging.info(f"The Device {laptop} has expected ssid: '{self.ssid}'")
                    if ip != "0.0.0.0" and ip != '':
                        logging.info(f"The Device {laptop} got an ip '{ip}'")
                    else:
                        logging.info(f"Didn't get the ip for device {laptop}, waiting for ip...")
                        if self.wait_for_ip(station_list=[laptop]):
                            logging.info(f"The device {laptop} got the ip.")
                        else:
                            logging.info(
                                f"The device {laptop} didn't get the ip, after waiting for an ip. Please recheck the given ssid/password")
                else:
                    logging.info(f"The Device {laptop} has not expected ssid: {self.ssid}")

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
            if type(wifi_msg_text) == str:
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

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None, timee=None, file_name="dummy.json"):
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

        if "1.1." in phn_name:
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
        logging.info("local_dict " + str(local_dict))

        return local_dict

    # @property
    def run(self):
        # try:
            # start timer
            present_time = datetime.now()
            test_start_time = present_time.strftime("%b %d %H:%M:%S")
            logging.info(f"Test Started at {present_time}")
            logging.info("Test started at " + str(present_time))
            # get the list of adb devices
            self.adb_device_list = self.interop.check_sdk_release(selected_android_devices=self.final_selected_android_list)
            self.windows_list = self.base_interop_profile.windows_list
            self.linux_list = self.base_interop_profile.linux_list
            self.mac_list = self.base_interop_profile.mac_list
            logging.info(
                f"Final Active Devices List (Android, Windows, Linux, Mac) Which support user specified release & not in phantom : {self.adb_device_list, self.base_interop_profile.windows_list, self.base_interop_profile.linux_list, self.base_interop_profile.mac_list}")
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

            if self.adb_device_list:
                logging.info(f"Selected All Active Devices: {self.adb_device_list}")
            else:
                logging.info(f"No active adb devices list found: {self.adb_device_list}")
            logging.info(f"Final selected device list, after chosen from available device list: {self.adb_device_list}")

            if len(self.adb_device_list) == 0:
                logging.info("There is no active adb (Android) devices please check system")
            else:
                for i in range(len(self.adb_device_list)):
                    self.phn_name.append(self.adb_device_list[i].split(".")[2])
                logging.info(f"Separated device names from the full name: {self.phn_name}")
                logging.info("phn_name" + str(self.phn_name))

            # check status of devices
            phantom = []
            for i in self.adb_device_list:
                phantom.append(self.interop.get_device_details(device=i, query="phantom"))
            # print("Device Phantom State List", phantom)
            # logging.info(phantom)
            state = None
            for i, j in zip(phantom, self.adb_device_list):
                if str(i) == "False":
                    logging.info("Device %s is in active state." % j)
                    logging.info("device are up")
                    state = "UP"
                else:
                    logging.info("Devices %s is in phantom state" % j)
                    logging.info("all devices are not up")
                    # exit(1)
            # if state == "UP":
            if self.adb_device_list or self.windows_list or self.linux_list or self.mac_list:
                # setting / modify user name
                # self.interop.set_user_name(device=self.adb_device_list)
                for i in self.adb_device_list:
                    self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
                logging.info(f"ADB user-names for selected devices: {self.device_name}")
                logging.info("device name " + str(self.device_name))
                # print("waiting for 5 sec...")
                # time.sleep(5)

                logging.info("List out the network id's")
                for i in self.adb_device_list:
                    connected_network_info = self.utility.list_networks_info(device_name=i)
                    if connected_network_info == 'No networks':
                        logging.info("No exiting networks found for %s device" % i)
                    else:
                        # Forget already existing network base on the network id
                        logging.info(
                            "The %s device is already having %s saved networks" % (i, connected_network_info['SSID']))
                        logging.info(f"Existing and Saved Network ids : {connected_network_info['Network Id']}")
                        logging.info(f"Existing and Saved SSIDs : {connected_network_info['SSID']}")
                        logging.info(f"Existing and Saved Security Types: {connected_network_info['Security type']}")
                        logging.info("Forgetting all Saved networks for %s device..." % i)
                        logging.info("forget all previous connected networks")
                        self.utility.forget_netwrk(device=i, network_id=connected_network_info['Network Id'])

                logging.info("Stopping the APP")
                for i in self.adb_device_list:
                    self.interop.stop(device=i)
                if self.adb_device_list:
                    logging.info("Apply SSID configuring using batch modify for android devices")
                    logging.info("apply ssid using batch modify")
                    # connecting the android devices to given ssid
                    self.interop.batch_modify_apply(device=self.adb_device_list, manager_ip=self.mgr_ip)
                # connecting the laptops to the given ssid
                if self.all_laptops:
                    self.real_clients_connectivity(windows_list=self.windows_list, linux_list=self.linux_list,
                                                   mac_list=self.mac_list)
                logging.info("Check heath data")
                logging.info("check heath data")
                health = dict.fromkeys(self.adb_device_list)
                logging.info(f"Initial Health Data For Android Clients: {health}")
                health_for_laptops = dict.fromkeys(self.all_laptops)
                logging.info(f"Initial Health Data For Laptops Clients: {health_for_laptops}")

                # checking whether the adb device connected to given ssid or not
                for i in self.adb_device_list:
                    dev_state = self.utility.get_device_state(device=i)
                    if dev_state == "COMPLETED,":
                        logging.info("Phone %s is in connected state" % i)
                        logging.info("phone is in connected state")
                        ssid = self.utility.get_device_ssid(device=i)
                        if ssid == self.ssid:
                            logging.info("The Device %s is connected to expected ssid (%s)" % (i, ssid))
                            logging.info("device is connected to expected ssid")
                            health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            logging.info("**** The Device is not connected to the expected ssid ****")
                    else:
                        # logging.info(f"Waiting for {self.wait_time} sec & Checking again the status of the device")
                        logging.info(f"Waiting for 30 sec & Checking again")
                        time.sleep(30)
                        dev_state = self.utility.get_device_state(device=i)
                        logging.info(f"Device state {dev_state}")
                        logging.info("device state" + str(dev_state))
                        if dev_state == "COMPLETED,":
                            logging.info("Phone is in connected state")
                            logging.info("phone is in connected state")
                            ssid = self.utility.get_device_ssid(device=i)
                            if ssid == self.ssid:
                                logging.info("The Device %s is connected to expected ssid (%s)" % (i, ssid))
                                logging.info("device is connected to expected ssid")
                                health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            logging.info(f"device state {dev_state}")
                            logging.info("device state" + str(dev_state))
                            health[i] = {'ConnectAttempt': '0', 'ConnectFailure': '0', 'AssocRej': '0',
                                         'AssocTimeout': '0'}
                logging.info(f"Health Status for the Android Devices: {health}")
                logging.info("health" + str(health))

                logging.info(f"Health Status for the Laptop Devices: {health_for_laptops}")

                # Resting Starts from here
                reset_list = []
                for i in range(self.reset):
                    reset_list.append(i)
                logging.info(f"Given No.of iterations for Reset : {len(reset_list)}")
                logging.info("reset list" + str(reset_list))
                reset_dict = dict.fromkeys(reset_list)
                for r, final in zip(range(self.reset), reset_dict):
                    logging.info("Waiting until given %s sec time intervel to finish..." % self.time_int)
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
                        logging.info("**** Disable wifi for laptop %s" % i)
                        self.admin_down(port_eid=i)
                    for i in self.adb_device_list:
                        logging.info("**** Disable wifi for android %s" % i)
                        logging.info("disable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="disable")
                    for i in self.all_laptops:  # laptop admin up
                        logging.info("**** Enable wifi for laptop %s" % i)
                        self.admin_up(port_eid=i)
                    for i in self.adb_device_list:
                        logging.info("*** Enable wifi for laptop %s" % i)
                        logging.info("enable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="enable")
                    for i in self.adb_device_list:
                        logging.info("Starting APP for %s" % i)
                        self.interop.start(device=i)
                    if self.all_laptops:
                        if self.wait_for_ip(station_list=self.all_laptops, timeout_sec=-1):
                            logging.info("PASSED : ALL STATIONS GOT IP")
                        else:
                            logging.info("FAILED : MAY BE NOT ALL STATIONS ACQUIRED IP'S")
                        # logging.info("Waiting until given %s sec waiting time to finish..." % self.wait_time)
                    time.sleep(30)
                    for i in self.all_selected_devices:
                        get_dicct = self.get_time_from_wifi_msgs(local_dict=local_dict, phn_name=i, timee=timee,
                                                                 file_name=f"reset_{r}_log.json")
                        reset_dict[r] = get_dicct
                logging.info(f"Final Reset Count Dictionary for all clients: {reset_dict}")
                logging.info("reset dict " + str(reset_dict))
                test_end = datetime.now()
                test_end_time = test_end.strftime("%b %d %H:%M:%S")
                logging.info(f"Test Ended at {test_end}")
                # logging.info("Test ended at " + test_end_time)
                s1 = test_start_time
                s2 = test_end_time
                FMT = '%b %d %H:%M:%S'
                test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                logging.info(f"Total Test Duration: {test_duration}")
                logging.info(f"Name of the Report Folder : {self.report_path}")
                logging.info("Generating the Report...")
                return reset_dict, test_duration
        # except Exception as e:
        #     logger.error(str(e))

    def generate_overall_graph(self, reset_dict=None, figsize=(13, 5), _alignmen=None, remove_border=None,
                               bar_width=0.7, _legend_handles=None, _legend_loc="best", _legend_box=None,
                               _legend_ncol=1,
                               _legend_fontsize=None, text_font=12, bar_text_rotation=45):
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
        conected_list = conected_list + laptop_conected_list
        disconnected_list = disconnected_list + laptop_disconnected_list
        scan_state = scan_state + laptop_scan_state
        asso_attempt = asso_attempt + laptop_asso_attempt
        asso_rej = asso_rej + laptop_asso_rej

        # count connects and disconnects
        scan, ass_atmpt = 0, 0
        for i, y in zip(range(len(scan_state)), range(len(asso_attempt))):
            for m in scan_state[i]:
                scan = scan + m
            for n in asso_attempt[i]:
                ass_atmpt = ass_atmpt + int(n)

        conects, disconnects = 0, 0
        for i, y in zip(range(len(conected_list)), range(len(disconnected_list))):
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
        self.graph_image_name = "overall_graph"
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
        return "%s.png" % self.graph_image_name

    def generate_overall_graph_table(self, reset_dict, device_list):
        # self.total_resets, self.total_disconnects, self.total_scans, self.total_ass_attemst, self.total_ass_rejects, self.total_connects = [], [], [], [], [], []
        for y, z in zip(device_list, range(len(device_list))):
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
                "Remarks": remarks
            }
            test_setup = pd.DataFrame(table_1)
            self.lf_report.set_table_dataframe(test_setup)
            self.lf_report.build_table()

    def generate_report(self, reset_dict=None, test_dur=None):
        # try:
            # print("reset dict", reset_dict)
            # print("Test Duration", test_dur)
            # logging.info("reset dict " + str(reset_dict))

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
                "No of Clients": f"{len(self.all_selected_devices)} (Windows: {len(self.windows_list)}, Linux: {len(self.linux_list)}, Mac: {len(self.mac_list)}, Android: {len(self.adb_device_list)})",
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

            d_name, device_type, model, user_name, release = [], [], [], [], []

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
                    elif "Mac" in hw_version:
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
            self.lf_report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
            # self.lf_report.move_data(directory="log", _file_name="port_reset.log")
        # except Exception as e:
        #     logging.warning(str(e))


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
        description=
        '''
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

    # parser.add_argument("--wait_time", type=int, default=20,
    #                     help='Specify the wait time in seconds for WIFI Supplicant Logs.')

    parser.add_argument("--release", nargs='+', default=["12"],
                        help='Specify the SDK release version (Android Version) of real clients to be supported in test.'
                             'eg:- --release 11 12 13')
    # logging configuration:
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

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
                           mgr_ip=args.mgr_ip
                           )
    obj.selecting_devices_from_available()
    reset_dict, duration = obj.run()
    obj.generate_report(reset_dict=reset_dict, test_dur=duration)


if __name__ == '__main__':
    main()