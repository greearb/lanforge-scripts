#!/usr/bin/env python3
"""
NAME: lf_interop_port_reset_test.py

PURPOSE:The LANforge interop port reset test allows user to use lots of real Wi-Fi stations and connect them the AP
 under test and then disconnect and reconnect a random number of
stations at random intervals

EXAMPLE:
$ ./ python3 lf_interop_port_reset_test.py  --host 192.168.1.31 --mgr_ip 192.168.1.31  --dut TestDut --ssid Airtel_9755718444_5GHz
--passwd air29723 --encryp psk2 --band 5G --reset 1 --time_int 60 --wait_time 60 --release 11 12 --clients 1

NOTES:
#Currently this script will forget all network and then apply batch modify on real devices connected to LANforge
and in the end generates report

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
import numpy as np
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


class InteropPortReset(Realm):
    def __init__(self, host,
                 dut=None,
                 ssid=None,
                 passwd=None,
                 encryp=None,
                 reset=None,
                 clients= None,
                 mgr_ip=None,
                 time_int=None,
                 wait_time=None,
                 suporrted_release=None
                 ):
        super().__init__(lfclient_host=host,
                         lfclient_port=8080)
        self.adb_device_list = None
        self.host = host
        self.phn_name = []
        self.dut_name = dut
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        # self.band = band
        self.clients = clients
        self.mgr_ip = mgr_ip
        self.reset = reset
        self.time_int = time_int
        self.wait_time = wait_time
        self.supported_release = suporrted_release
        self.device_name = []
        self.lf_report = lf_report_pdf.lf_report(_path="", _results_dir_name="Interop_port_reset_test",
                                                 _output_html="port_reset_test.html",
                                                 _output_pdf="port_reset_test.pdf")
        self.report_path = self.lf_report.get_report_path()

        # self.hw_list = []
        # self.windows_list = []
        # self.linux_list = []
        # self.mac_list = []
        # self.android_list = []
        # #######################
        # self.working_resources_list = []
        # self.eid_list = []
        # self.username_list = []
        # self.devices_available = []
        # self.hostname_list = []
        # self.user_list = []
        # self.input_devices_list = []
        # self.real_client_list = []

        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=8080,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt = 0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)

        self.utility = base.UtilityInteropWifi(host_ip=self.host)
        logging.basicConfig(filename='overall_reset_test.log', filemode='w', level=logging.INFO, force=True)

    # def list_out_resource(self):
    #     response = self.json_get("/resource/all")
    #     for key, value in response.items():
    #         if key == "resources":
    #             for element in value:
    #                 for a, b in element.items():
    #                     self.hw_list.append(b['hw version'])
    #     for hw_version in self.hw_list:
    #         if "Win" in hw_version:
    #             self.windows_list.append(hw_version)
    #         elif "Linux" in hw_version:
    #             self.linux_list.append(hw_version)
    #         elif "Apple" in hw_version:
    #             self.mac_list.append(hw_version)
    #         else:
    #             if hw_version != "":
    #                 self.android_list.append(hw_version)
    #     self.laptop_list = self.windows_list + self.linux_list + self.mac_list
    #     print("Laptop list :", self.laptop_list)
    #     print("Android list :", self.android_list)
    #
    # def phantom_check_for_resource_and_portmgr(self):
    #     port_eid_list = []
    #     same_eid_list = []
    #     original_port_list = []
    #     # Querying resource manger
    #     response = self.json_get("/resource/all")
    #     for key, value in response.items():
    #         if key == "resources":
    #             for element in value:
    #                 for a, b in element.items():
    #                     if b['phantom'] == False:
    #                         self.working_resources_list.append(b["hw version"])
    #                         if "Win" in b['hw version']:
    #                             self.eid_list.append(b['eid'])
    #                             self.windows_list.append(b['hw version'])
    #                             self.hostname_list.append(b['eid'] + " " + b['hostname'])
    #                             self.devices_available.append(b['eid'] + " " + b['hw version'] + " " + 'laptop')
    #                         elif "Linux" in b['hw version']:
    #                             if 'ct' not in b['hostname']:
    #                                 self.eid_list.append(b['eid'])
    #                                 self.linux_list.append(b['hw version'])
    #                                 self.hostname_list.append(b['eid'] + " " + b['hostname'])
    #                                 self.devices_available.append(b['eid'] + " " + b['hw version'] + " " + 'laptop')
    #                         elif "Apple" in b['hw version']:
    #                             self.eid_list.append(b['eid'])
    #                             self.mac_list.append(b['hw version'])
    #                             self.hostname_list.append(b['eid'] + " " + b['hostname'])
    #                             self.devices_available.append(b['eid'] + " " + b['hw version'] + " " + 'laptop')
    #                         else:
    #                             self.eid_list.append(b['eid'])
    #                             self.android_list.append(b['hw version'])
    #                             self.username_list.append(b['eid'] + " " + b['user'])
    #                             self.devices_available.append(b['eid'] + " " + b['hw version'] + " " + 'android')
    #     print("Hostname list :", self.hostname_list)
    #     print("Username list :", self.username_list)
    #     print("Available resources in resource tab :", self.devices_available)
    #     print("Eid_list : ", self.eid_list)
    #
    #     # Querying port manger
    #     response_port = self.json_get("/port/all")
    #     for interface in response_port['interfaces']:
    #         for port, port_data in interface.items():
    #             if (not port_data['phantom'] and not port_data['down'] and port_data['parent dev'] == "wiphy0"):
    #                 for id in self.eid_list:
    #                     if (id + '.' in port):
    #                         original_port_list.append(port)
    #                         port_eid_list.append(str(self.name_to_eid(port)[0]) + '.' + str(self.name_to_eid(port)[1]))
    #     print("port eid list", port_eid_list)
    #     for i in range(len(self.eid_list)):
    #         for j in range(len(port_eid_list)):
    #             if self.eid_list[i] == port_eid_list[j]:
    #                 same_eid_list.append(self.eid_list[i])
    #     same_eid_list = [_eid + ' ' for _eid in same_eid_list]
    #     print("same eid list", same_eid_list)
    #     # All the available ports from port manager are fetched from port manager tab ---
    #
    #     for eid in same_eid_list:
    #         for device in self.devices_available:
    #             if eid in device:
    #                 print(eid + ' ' + device)
    #                 self.user_list.append(device)
    #     print("Available resources to run test : ", self.user_list)
    #
    #     devices_list = input("Enter the desired resources to run the test:")
    #     print("devices list", devices_list)
    #     resource_eid_list = devices_list.split(',')
    #     resource_eid_list2 = [eid + ' ' for eid in resource_eid_list]
    #     resource_eid_list1 = [resource + '.' for resource in resource_eid_list]
    #     print("Resource eid list", resource_eid_list)
    #
    #     # User desired eids are fetched ---
    #
    #     for eid in resource_eid_list1:
    #         for ports_m in original_port_list:
    #             if eid in ports_m:
    #                 self.input_devices_list.append(ports_m)
    #     print("input devices list", self.input_devices_list)
    #
    #     # user desired real client list 1.1 wlan0 ---
    #
    #     for i in resource_eid_list2:
    #         for j in range(len(self.hostname_list)):
    #             if i in self.hostname_list[j]:
    #                 self.real_client_list.append(self.hostname_list[j])
    #         for k in range(len(self.username_list)):
    #             if i in self.username_list[k]:
    #                 self.real_client_list.append(self.username_list[k])
    #     print("real client list", self.real_client_list)
    #     self.num_stations = len(self.real_client_list)

    def create_log_file(self, json_list, file_name="empty.json"):
        # Convert the list of JSON values to a JSON-formatted string
        json_string = json.dumps(json_list)
        new_folder = os.path.join(self.report_path, "Wifi_Messages")
        if os.path.exists(new_folder) and os.path.isdir(new_folder):
            pass
            # print(f"The folder 'Wifi_Messages' is already existed in '{self.report_path}' report folder.")
        else:
            # print(f"The folder 'Wifi_Messages' does not exist in '{self.report_path}' report folder.")
            os.makedirs(new_folder)

        file_path = f"{self.report_path}/Wifi_Messages/{file_name}"
        # print("log file saved in Wifi_Message directory path:", file_path)

        # Write the JSON-formatted string to the .json file
        with open(file_path, 'w') as file:
            file.write(json_string)

    def remove_files_with_duplicate_names(self, folder_path):
        # Create a dictionary to store filenames and their paths
        file_names = {}

        # Walk through the folder and its subdirectories
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                if file_name in file_names:
                    # Remove the duplicate file
                    os.remove(file_path)
                    print(f"Removed duplicate file: {file_path}")
                else:
                    # Add the file name to the dictionary
                    file_names[file_name] = file_path

    def get_last_wifi_msg(self):
        a = self.json_get("/wifi-msgs/last/1", debug_=True)
        last = a['wifi-messages']['time-stamp']
        logging.info(str(a))
        print("Last WiFi Message Time Stamp:", last)
        logging.info(str(last))
        return last

    def get_count(self, value=None, keys_list=None, device=None, filter=None):
        count_ = []
        device = device.split(".")[2]
        for i, y in zip(keys_list, range(len(keys_list))):
            # print("Time stamp :-", i)
            wifi_msg_text = value[y][i]['text']
            if type(wifi_msg_text) == str:
                wifi_msg_text_keyword_list = value[y][i]['text'].split(" ")
                # print("#Wifi Message Text list:", wifi_msg_text_keyword_list)
                if device is None:
                    print(f"Device name is {device} None device name not existed in wifi messages...")
                else:
                    # print("#Device", device)
                    if device in wifi_msg_text_keyword_list:
                        if filter in wifi_msg_text_keyword_list:
                            print(f"The filter {filter} is present in the wifi message for device {device}.")
                            count_.append("YES")
                    else:
                        pass
                        # print(f"The device {device} not present in wifi_msg, so Skipping",
                        #       wifi_msg_text_keyword_list)
            else:
                for item in wifi_msg_text:
                    wifi_msg_text_keyword_list = item.split(" ")
                    # print("$Wifi Message Text list:", wifi_msg_text_keyword_list)
                    if device is None:
                        print(f"Device name is {device} None device name not existed in wifi messages... , ...")
                    else:
                        # print("$Device", device)
                        if device in wifi_msg_text_keyword_list:
                            if filter in wifi_msg_text_keyword_list:
                                print(f"The filter {filter} is present in the wifi message test list.")
                                count_.append("YES")
                        else:
                            pass
                            # print(f"The device {device} not present in wifi_msg, so Skipping",
                            #       wifi_msg_text_keyword_list)
        # print("Filter Present Count list:", count_)
        logging.info(str(count_))
        counting = count_.count("YES")
        # print("Total Counting:", counting)
        logging.info(str(counting))
        return counting

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None, timee=None, file_name="dummy.json"):
        # print("Waiting for 20 sec to fetch the logs...")
        # time.sleep(20)
        a = self.json_get("/wifi-msgs/since=time/" + str(timee), debug_=True)
        values = a['wifi-messages']
        # print("Wifi msgs Response : ", values)
        print(f"Counting the DISCONNECTIONS, SCANNING, ASSOC ATTEMPTS, ASSOC RECJECTIONS, CONNECTS for device {phn_name}")
        self.create_log_file(json_list=values, file_name=file_name)
        self.remove_files_with_duplicate_names(folder_path=f"{self.report_path}/Wifi_Messages/")
        # logging.info("values" + str(values))
        keys_list = []

        for i in range(len(values)):
            keys_list.append(list(values[i].keys())[0])
        # print("Key list", keys_list)

        # print("Before updating the disconnect count:", local_dict[phn_name])

        disconnect_count = self.get_count(value=values, keys_list=keys_list, device=phn_name,
                                          filter="Terminating...")  #Todo: need to rename the method
        print("Disconnect count:", disconnect_count)
        local_dict[phn_name]["Disconnected"] = disconnect_count
        scan_count = self.get_count(value=values, keys_list=keys_list, device=phn_name, filter="SCAN_STARTED")
        print("Scanning Count:", scan_count)
        local_dict[str(phn_name)]["Scanning"] = scan_count
        association_attempt = self.get_count(value=values, keys_list=keys_list, device=phn_name, filter="ASSOCIATING")
        print("Association Attempts Count:", association_attempt)
        local_dict[str(phn_name)]["ConnectAttempt"] = association_attempt
        association_rejection = self.get_count(value=values, keys_list=keys_list, device=phn_name, filter="ASSOC_REJECT")
        print("Association Rejection Count:", association_rejection)
        local_dict[str(phn_name)]["Association Rejection"] = association_rejection
        connected_count = self.get_count(value=values, keys_list=keys_list, device=phn_name, filter="CTRL-EVENT-CONNECTED")
        print("Connected Count", connected_count)
        if connected_count > 1 or connected_count == 0:
            ssid = self.utility.get_device_ssid(device=phn_name)
            if ssid == self.ssid:
                print("ssid:", ssid)
                print("The Device %s is connected to expected ssid" % phn_name)
                connected_count = 1
            else:
                print("**** The Device is not connected to the expected ssid ****")
                connected_count = 0
            print("Connected Count", connected_count)
        local_dict[str(phn_name)]["Connected"] = connected_count

        # print("Final dictionary for phones with updated CONNECTIONS,DISCONNECTIONS,SCANNING,ASSOCIATE ATTEMPTS,REJECTION count :", local_dict)
        logging.info("local_dict " + str(local_dict))

        return local_dict

    @property
    def run(self):
        try:
            # start timer
            present_time = datetime.now()
            test_start_time = present_time.strftime("%b %d %H:%M:%S")
            print("Test Started at ", present_time)
            logging.info("Test started at " + str(present_time))
            # get the list of adb devices
            self.adb_device_list = self.interop.check_sdk_release()
            print("Final ADB Active Devices List Which support user specified release & not in phantom :",
                  self.adb_device_list)
            logging.info(self.adb_device_list)
            print("The total number of available active devices are: ", len(self.adb_device_list))
            # Checking and selecting the number of available clients are grater than or equal to given number of clients
            if self.clients:
                if len(self.adb_device_list) >= self.clients:
                    print("No of available clients is greater than or equal to provided clients")
                    logging.info("No of available clients is greater than or equal to provided clients")
                    print("*** Now choosing no of clients provided from available list randomly ***")
                    logging.info("now choosing no of clients provided from available list randomly")
                    new_device = []
                    for i, x in zip(self.adb_device_list, range(int(self.clients))):
                        if x < self.clients:
                            new_device.append(i)
                    print("Selected Devices List: ", new_device)
                    logging.info(new_device)
                    self.adb_device_list = new_device
                else:
                    print("No of available clients is less than provided clients to be tested, Please check it.")
                    logging.info("no of available clients is less then provided clients to be tested, Please check it.")
                    exit(1)
            else:  # if not mentioned the number of clients then, select all client to run the port-reset.
                if self.adb_device_list:
                    print("Selected All Active Devices: ", self.adb_device_list)
                else:
                    print("No active adb devices list found.", self.adb_device_list)
                    exit(1)
            # Fetching Name of the devices in a list if the active devices are available
            print("Final selected device list, after chosen from available device list:", self.adb_device_list)
            logging.info("Final selected device list, after chosen from available device list:" + str(self.adb_device_list))

            #############
            if len(self.adb_device_list) == 0:
                print("There is no active adb devices please check system")
                logging.warning("there is no active adb devices please check system")
                exit(1)
            else:
                for i in range(len(self.adb_device_list)):
                    self.phn_name.append(self.adb_device_list[i].split(".")[2])
                print("Separated device names from the full name:", self.phn_name)
                logging.info("phn_name" + str(self.phn_name))

            ####################

            # check status of devices
            phantom = []
            for i in self.adb_device_list:
                phantom.append(self.interop.get_device_details(device=i, query="phantom"))
            # print("Device Phantom State List", phantom)
            # logging.info(phantom)
            state = None
            for i, j in zip(phantom, self.adb_device_list):
                if str(i) == "False":
                    print("Device %s is in active state." % j)
                    logging.info("device are up")
                    state = "UP"
                else:
                    print("Devices %s is in phantom state" % j)
                    logging.info("all devices are not up")
                    exit(1)
            if state == "UP":
                # setting / modify user name
                # self.interop.set_user_name(device=self.adb_device_list)
                for i in self.adb_device_list:
                    self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
                print("ADB user-names for selected devices:", self.device_name)
                logging.info("device name " + str(self.device_name))
                # print("waiting for 5 sec...")
                # time.sleep(5)

                print("List out the network id's")
                for i in self.phn_name:
                    connected_network_info = self.utility.list_networks_info(device_name=i)
                    if connected_network_info == 'No networks':
                        print("No exiting networks found for %s device" % i)
                    else:
                        # Forget already existing network base on the network id
                        print("The %s device is already having %s saved networks" % (i, connected_network_info['SSID']))
                        print("Existing and Saved Network ids :", connected_network_info['Network Id'])
                        print("Existing and Saved SSIDs :", connected_network_info['SSID'])
                        print("Existing and Saved Security Types:", connected_network_info['Security type'])
                        print("Forgetting all Saved networks for %s device..." % i)
                        logging.info("forget all previous connected networks")
                        self.utility.forget_netwrk(device=i, network_id=connected_network_info['Network Id'])
                        # print("Waiting for 2 sec")
                        # time.sleep(2)

                print("Stopping the APP")
                for i in self.adb_device_list:
                    self.interop.stop(device=i)

                print("Apply SSID configuring using batch modify")
                logging.info("apply ssid using batch modify")
                self.interop.batch_modify_apply(device=self.adb_device_list, manager_ip=self.mgr_ip)
                print("Check heath data")
                logging.info("check heath data")
                health = dict.fromkeys(self.adb_device_list)
                print("Initial Health Data:", health)
                logging.info(str(health))

                for i in self.adb_device_list:
                    dev_state = self.utility.get_device_state(device=i)
                    # print("State of the Device:", dev_state)
                    # logging.info("device state" + dev_state)
                    if dev_state == "COMPLETED,":
                        print("Phone %s is in connected state" % i)
                        logging.info("phone is in connected state")
                        ssid = self.utility.get_device_ssid(device=i)
                        if ssid == self.ssid:
                            print("The Device %s is connected to expected ssid" % i)
                            logging.info("device is connected to expected ssid")
                            health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            print("**** The Device is not connected to the expected ssid ****")
                    else:
                        print(f"Waiting for {self.wait_time} sec & Checking again the status of the device")
                        logging.info(f"Waiting for {self.wait_time} & Checking again")
                        time.sleep(int(self.wait_time))
                        dev_state = self.utility.get_device_state(device=i)
                        print("Device state", dev_state)
                        logging.info("device state" + str(dev_state))
                        if dev_state == "COMPLETED,":
                            print("Phone is in connected state")
                            logging.info("phone is in connected state")
                            ssid = self.utility.get_device_ssid(device=i)
                            if ssid == self.ssid:
                                print("Device is connected to expected ssid")
                                logging.info("device is connected to expected ssid")
                                health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                        else:
                            print("device state", dev_state)
                            logging.info("device state" + str(dev_state))
                            health[i] = {'ConnectAttempt': '0', 'ConnectFailure': '0', 'AssocRej': '0', 'AssocTimeout': '0'}
                # print("Health Status for the Devices:", health)
                logging.info("health" + str(health))

                # Resting Starts from here
                reset_list = []
                for i in range(self.reset):
                    reset_list.append(i)
                print("Given No.of iterations for Reset :", len(reset_list))
                logging.info("reset list" + str(reset_list))
                reset_dict = dict.fromkeys(reset_list)
                for r, final in zip(range(self.reset), reset_dict):
                    print("Waiting until given %s sec time intervel to finish..." % self.time_int)
                    time.sleep(int(self.time_int))  # sleeping until time interval finish
                    print("Iteration :-", r)
                    logging.info("r " + str(r))
                    local_dict = dict.fromkeys(self.adb_device_list)
                    # print("local dict", local_dict)

                    list_ = ["ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected"]
                    sec_dict = dict.fromkeys(list_)
                    # print("sec_dict", sec_dict)
                    for i in self.adb_device_list:
                        local_dict[i] = sec_dict.copy()
                    # print("Final Outcome", local_dict)
                    logging.info(str(local_dict))

                    # note last  log time
                    timee = self.get_last_wifi_msg()  # Todo : need to rename the method

                    for i in self.adb_device_list:
                        self.interop.stop(device=i)
                    for i in self.adb_device_list:
                        print("**** Disable wifi")
                        logging.info("disable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="disable")
                        # time.sleep(5)
                    for i in self.adb_device_list:
                        print("*** Enable wifi")
                        logging.info("enable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="enable")
                    for i in self.adb_device_list:
                        print("Starting APP for ", i)
                        self.interop.start(device=i)
                    print("Waiting until given %s sec waiting time to finish..." % self.wait_time)
                    time.sleep(int(self.wait_time))

                    # log reading
                    for i in self.adb_device_list:
                        get_dicct = self.get_time_from_wifi_msgs(local_dict=local_dict, phn_name=i, timee=timee,
                                                                 file_name=f"reset_{r}_log.json")  #Todo : need to rename the method
                        reset_dict[r] = get_dicct
                print("Final Reset Count Dictionary for all clients: ", reset_dict)
                logging.info("reset dict " + str(reset_dict))
                test_end = datetime.now()
                test_end_time = test_end.strftime("%b %d %H:%M:%S")
                print("Test Ended at ", test_end)
                logging.info("Test ended at " + test_end_time)
                s1 = test_start_time
                s2 = test_end_time
                FMT = '%b %d %H:%M:%S'
                test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                print("Total Test Duration:", test_duration)
                print("Name of the Report Folder : ", self.report_path)
                return reset_dict, test_duration
        except Exception as e:
            print(e)

    # def generate_per_station_graph(self, device_names=None, dataset=None, labels=None):
    #     # device_names = ['1.1.RZ8N70TVABP', '1.1.RZ8RA1053HJ']
    #     print("dataset", dataset)
    #     print(labels)
    #     print(device_names)
    #     # dataset = [[1, 1], [1, 1]]
    #     labels = ["Connected", "Disconnected"]
    #     graph = lf_graph.lf_bar_graph(_data_set=dataset, _xaxis_name="Device Name",
    #                                   _yaxis_name="Reset = " + str(self.reset), _xaxis_categories=device_names,
    #                                   _label=labels, _xticks_font=8, _graph_image_name="per_station_graph",
    #                                   _color=['forestgreen', 'red'], _color_edge='black', _figsize=(13, 5),
    #                                   _grp_title="Per station graph ", _xaxis_step=1, _show_bar_value=True,
    #                                   _text_font=12, _text_rotation=45, _enable_csv=True, _legend_loc="upper right",
    #                                   _legend_fontsize=12, _legend_box=(1.12, 1.01),
    #                                   _remove_border=['top', 'right', 'left'], _alignment={"left": 0.011})
    #     graph_png = graph.build_bar_graph()
    #     print("graph name {}".format(graph_png))
    #     return graph_png

    def generate_overall_graph(self, reset_dict=None, figsize=(13, 5), _alignmen=None, remove_border=None,
                               bar_width=0.7, _legend_handles=None, _legend_loc="best", _legend_box=None, _legend_ncol=1,
                               _legend_fontsize=None, text_font=12, bar_text_rotation=45,
                               ):
        dict_ = ['Port Resets', 'Disconnected', 'Scans', 'Assoc Attempts', "Association Rejection", 'Connected']
        data = dict.fromkeys(dict_)
        data['Port Resets'] = self.reset

        conected_list = []
        disconnected_list = []
        scan_state = []
        asso_attempt = []
        asso_rej = []

        # self.adb_device_list = ['1.1.RZ8RA1053HJ']

        for j in self.adb_device_list:
            # print(j)
            local = []
            local_2, local_3, local_4, local_5, local_6 = [], [], [], [], []
            for i in reset_dict:
                # print(i)
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

        # print("list ", conected_list, disconnected_list, scan_state, asso_attempt, asso_rej)

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

        # print("scan", scan)
        # print(ass_atmpt)
        # print(conects)
        # print(disconnects)
        # print(assorej)

        # print("Before count the dictionary data for overall data: ", data)
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
        # print(courses)
        # print(values)

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
        plt.bar(courses, values, color=('#f56122', '#00FF00', '#f5ea22', '#3D85C6', '#fa4d4d', "forestgreen"),
                width=bar_width)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', rotation=bar_text_rotation, fontsize=text_font)

        plt.xlabel("", fontweight='bold', fontsize=15)
        plt.ylabel("Count", fontweight='bold', fontsize=15)
        # plt.title("Overall Graph for Port Reset Test")
        # plt.legend(
        #     handles=_legend_handles,
        #     loc=_legend_loc,
        #     bbox_to_anchor=(1.0, 1.0),
        #     ncol=_legend_ncol,
        #     fontsize=_legend_fontsize)
        plt.suptitle("Overall Graph for Port Reset Test", fontsize=16)
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        # plt.show()
        return "%s.png" % self.graph_image_name

    def per_client_graph(self, data=None, name=None, figsize=(13, 5), _alignmen=None, remove_border=None, bar_width=0.5,
                         _legend_handles=None, _legend_loc="best", _legend_box=None, _legend_ncol=1,
                         _legend_fontsize=None, text_font=12, bar_text_rotation=45, xaxis_name="", yaxis_name="",
                         graph_title="Client %s Performance Port Reset Totals", graph_title_size=16):
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
        plt.bar(courses, values, color=('#f56122', '#00FF00', '#f5ea22', '#3D85C6', '#fa4d4d', "forestgreen"),
                edgecolor="black", width=bar_width)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', va='bottom', rotation=bar_text_rotation,
                     fontsize=text_font)

        plt.xlabel(xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(yaxis_name, fontweight='bold', fontsize=15)
        plt.legend(
            handles=_legend_handles,
            loc=_legend_loc,
            # bbox_to_anchor=(1.0, 1.0),
            ncol=_legend_ncol,
            fontsize=_legend_fontsize)
        plt.suptitle(graph_title, fontsize=graph_title_size)
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        # plt.show()
        return "%s.png" % self.graph_image_name

    def generate_report(self, reset_dict=None, test_dur=None):
        try:
            # print("reset dict", reset_dict)
            # print("Test Duration", test_dur)
            # logging.info("reset dict " + str(reset_dict))

            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            self.lf_report.move_data(_file_name="overall_reset_test.log")
            test_setup_info = {
                "DUT Name": self.dut_name,
                "LANforge ip": self.host,
                "SSID": self.ssid,
                "Total Reset Count": self.reset,
                "No of Clients": self.clients,
                "Wait Time": str(self.wait_time) + " sec",
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
                                                 _legend_handles=None, _legend_loc="best", _legend_ncol=1, _legend_fontsize=None,
                                                 _legend_box=(1.9, 1.0), text_font=12)
            # graph1 = self.generate_per_station_graph()
            self.lf_report.set_graph_image(graph1)
            self.lf_report.move_graph_image()
            self.lf_report.build_graph()

            # per client table and graphs
            for y, z in zip(self.adb_device_list, range(len(self.adb_device_list))):
                reset_count_ = list(reset_dict.keys())
                reset_count = []
                for i in reset_count_:
                    reset_count.append(int(i) + 1)
                asso_attempts, disconnected, scanning, connected, assorej = [], [], [], [], []

                for i in reset_dict:
                    asso_attempts.append(reset_dict[i][y]["ConnectAttempt"])
                    disconnected.append(reset_dict[i][y]["Disconnected"])
                    scanning.append(reset_dict[i][y]["Scanning"])
                    connected.append(reset_dict[i][y]["Connected"])
                    assorej.append(reset_dict[i][y]["Association Rejection"])

                # graph calculation
                dict_ = ['Port Resets', 'Disconnects', 'Scans', 'Association Attempts', "Association Rejections", 'Connects']
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
                adb_user_name = self.interop.get_device_details(device=y, query="user-name")

                # setting the title for per client graph and table represent title.
                self.lf_report.set_obj_html("Port Resets for Client " + str(adb_user_name) + " (" + str(y.split(".")[2] + ")"),
                                            "The below table & graph displays details of " + str(adb_user_name) + "device."
                                            # "The below graph provides information regarding per station behaviour for every reset count"
                                            # " where"
                                            # "Port resets=Total resets provided as test input, Disconnected=It is the total number "
                                            # "of disconnects happened for a client  during every reset when WiFi was disabled , Scans=It is the"
                                            # "total number of scanning state achieved by a client during the test when network is enabled back for "
                                            # "every reset"
                                            # " again, Association attempts=It is the total number of association attempts(Associating state) achieved  by"
                                            # " a client after the WiFi is enabled back again in full test, Connected=It is the total number"
                                            # "of connection(Associated state) achieved by a client during the test when Wifi is enabled back again."
                                            )
                self.lf_report.build_objective()

                # per client graph generation
                graph2 = self.per_client_graph(data=data, name="per_client_" + str(z), figsize=(13, 5),
                                               _alignmen={"left": 0.1}, remove_border=['top', 'right'],
                                               _legend_loc="upper right", _legend_fontsize=12, _legend_box=(1.2, 1.01),
                                               yaxis_name="COUNT",
                                               graph_title="Client " + str(adb_user_name) + " Total Reset Performance Graph")
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
                }
                test_setup = pd.DataFrame(table_1)
                self.lf_report.set_table_dataframe(test_setup)
                self.lf_report.build_table()
                # self.per_client_graph(data=data, name="per_client_" + str(z))

                # Table 1
                # self.lf_report.set_obj_html("Real Client " + y.split(".")[2] + " Reset Observations",
                #                     "The below table shows actual behaviour of real devices for every reset value")
                # self.lf_report.build_objective()
                # table_1 = {
                #     "Reset Count": reset_count,
                #     "Association attempts": asso_attempts,
                #     "Disconnected": disconnected,
                #     "Scanning": scanning,
                #     "Association Rejection" : assorej,
                #     "Connected": connected,
                # }
                # test_setup = pd.DataFrame(table_1)
                # self.lf_report.set_table_dataframe(test_setup)
                # self.lf_report.build_table()

            self.lf_report.set_obj_html("Tested Clients Information:",
                                        "The table displays details of real clients which are involved in the test.")
            self.lf_report.build_objective()
            d_name, device_type, model, user_name, release = [], [], [], [], []
            for y in self.adb_device_list:
                # print(self.adb_device_list)
                # print("Device :", y)
                d_name.append(self.interop.get_device_details(device=y, query="name"))
                device_type.append(self.interop.get_device_details(device=y, query="device-type"))
                model.append(self.interop.get_device_details(device=y, query="model"))
                user_name.append(self.interop.get_device_details(device=y, query="user-name"))
                release.append(self.interop.get_device_details(device=y, query="release"))

            s_no = []
            for i in range(len(d_name)):
                s_no.append(i + 1)

            # self.clients = len(self.adb_device_list)

            table_2 = {
                "S.No": s_no,
                "Serial Number": d_name,
                "User Name": user_name,
                "Model": model,
                "SDK Release": release,
                "Device Type": device_type
            }
            test_setup = pd.DataFrame(table_2)
            self.lf_report.set_table_dataframe(test_setup)
            self.lf_report.build_table()

            # self.lf_report.set_obj_html("Real Client Detail Info",
            #                             "The below table shows detail information of real clients")
            # self.lf_report.build_objective()
            # d_name, device, model, user_name, release = [], [], [], [], []
            # for y in self.adb_device_list:
            #     print("ins", y)
            #     print(self.adb_device_list)
            #     d_name.append(self.interop.get_device_details(device=y, query="name"))
            #     device.append(self.interop.get_device_details(device=y, query="device"))
            #     model.append(self.interop.get_device_details(device=y, query="model"))
            #     user_name.append(self.interop.get_device_details(device=y, query="user-name"))
            #     release.append(self.interop.get_device_details(device=y, query="release"))
            #
            # s_no = []
            # for i in range(len(d_name)):
            #     s_no.append(i + 1)
            #
            # # self.clients = len(self.adb_device_list)
            #
            # table_2 = {
            #     "S.No": s_no,
            #     "Name": d_name,
            #     "device": device,
            #     "user-name": user_name,
            #     "model": model,
            #     "release": release
            # }
            # test_setup = pd.DataFrame(table_2)
            # self.lf_report.set_table_dataframe(test_setup)
            # self.lf_report.build_table()

            # test_input_infor = {
            #     "LANforge ip": self.host,
            #     "LANforge port": "8080",
            #     "ssid": self.ssid,
            #     # "band": self.band,
            #     "reset count": self.reset,
            #     "time interval between every reset(sec)": self.time_int,
            #     "No of Clients": self.clients,
            #     "Wait Time": self.wait_time,
            #     "Contact": "support@candelatech.com"
            # }
            # self.lf_report.set_table_title("Test basic Input Information")
            # self.lf_report.build_table_title()
            # self.lf_report.test_setup_table(value="Information", test_setup_data=test_input_infor)

            self.lf_report.build_footer()
            self.lf_report.write_html()
            self.lf_report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
        except Exception as e:
            print(str(e))
            logging.warning(str(e))


def main():
    desc = """ port reset test 
    run: 
    python3 ./lf_interop_port_reset_test.py --host 192.168.200.83 --mgr_ip 192.168.200.109  --dut TestDut --ssid Netgear5g
     --passwd lanforge --encryp psk2 --reset 10 --time_int 5 --wait_time 5 --release 11 --clients 1
                                            OR
    python3 ./lf_interop_port_reset_test.py --host 192.168.200.83 --mgr_ip 192.168.200.109  --dut TestDut --ssid Netgear5g
     --passwd lanforge --encryp psk2 --reset 10 --time_int 5 --wait_time 5 --release 11
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--host", "--mgr", default='192.168.1.31',
                        help='specify the GUI to connect to, assumes port 8080')

    parser.add_argument("--mgr_ip", default='192.168.1.31',
                        help='specify the interop manager ip')

    parser.add_argument("--dut", default="TestDut",
                        help='specify DUT name on which the test will be running')

    parser.add_argument("--ssid", default="Airtel_9755718444_5GHz",
                        help='specify ssid on which the test will be running')

    parser.add_argument("--passwd", default="air29723",
                        help='specify encryption password  on which the test will be running')

    parser.add_argument("--encryp", default="psk2",
                        help='specify the encryption type  on which the test will be running eg :open|psk|psk2|sae|psk2jsae')

    # parser.add_argument("--band", default="5G",
    #                     help='specify the type of band you want to perform testing eg 5G|2G|Dual')

    parser.add_argument("--clients", type=int, default=2,
                        help='specify no of clients you want to perform test on')

    parser.add_argument("--reset", type=int, default=2,
                        help='specify the number of time you want to reset eg 2')

    parser.add_argument("--time_int", type=int, default=2,
                        help='specify the time interval in secs after which reset should happen')

    parser.add_argument("--wait_time", type=int, default=60,
                        help='specify the time interval or wait time in secs after enabling wifi')

    parser.add_argument("--release", nargs='+', default=["12"],
                        help='specify the sdk release version of real clients to be supported in test')

    args = parser.parse_args()
    obj = InteropPortReset(host=args.host,
                           dut=args.dut,
                           ssid=args.ssid,
                           passwd=args.passwd,
                           encryp=args.encryp,
                           reset=args.reset,
                           clients=args.clients,
                           time_int=args.time_int,
                           wait_time=args.wait_time,
                           suporrted_release=args.release,
                           mgr_ip=args.mgr_ip
                           )
    # obj.list_out_resource()
    # print("OS TYPE DONE!!!")
    # obj.phantom_check_for_resource_and_portmgr()
    reset_dict, duration = obj.run
    # reset_dict = {0: {'1.1.RZ8RA1053HJ': {'ConnectAttempt': 2, 'Disconnected': 1, 'Scanning': 2, 'Connected': 1}}, 1: {'1.1.RZ8RA1053HJ': {'ConnectAttempt': 2, 'Disconnected': 1, 'Scanning': 3, 'Connected': 1}}}
    # duration = "xyz"
    obj.generate_report(reset_dict=reset_dict, test_dur=duration)


if __name__ == '__main__':
    main()
