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
                 band=None,
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
        self.band = band
        self.clients = clients
        self.mgr_ip = mgr_ip
        self.reset = reset
        self.time_int = time_int
        self.wait_time = wait_time
        self.supported_release = suporrted_release
        self.device_name = []

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
        logging.basicConfig(filename='reset.log', filemode='w', level=logging.INFO, force=True)

    def get_last_wifi_msg(self):
        a = self.json_get("/wifi-msgs/last/1", debug_=True)
        last = a['wifi-messages']['time-stamp']
        print("Wifi Message resonance:", a)
        logging.info(str(a))
        print("Time Stamp:", last)
        logging.info(str(last))
        return last

    def get_count(self, filter=None, value=None, keys_list=None):
        count_ = []
        for i, y in zip(keys_list, range(len(keys_list))):
            b = value[y][i]['text']
            if type(b) == str:
                variable = value[y][i]['text'].split(" ")
                # print("variable", variable)
                if filter in variable:
                    # print("yes")
                    count_.append("yes")
            else:
                for a in b:
                    y = a.split(" ")
                    # print("y", y)
                    if filter in y:
                        count_.append("yes")
        print("Count:", count_)
        logging.info(str(count_))
        counting = count_.count("yes")
        print("Counting:", counting)
        logging.info(str(counting))
        return counting

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None, timee=None):
        time.sleep(20)
        a = self.json_get("/wifi-msgs/since=time/" + str(timee), debug_=True)
        values = a['wifi-messages']
        print("Wifi msg values:", values)
        logging.info("values" + str(values))
        keys_list = []

        for i in range(len(values)):
            keys_list.append(list(values[i].keys())[0])

        disconnect_count = self.get_count(value=values, keys_list=keys_list, filter="Terminating...")
        print("Disconnect count:", disconnect_count)

        print(local_dict[phn_name])
        local_dict[phn_name]["Disconnected"] = disconnect_count
        print(local_dict[phn_name])
        print(local_dict)

        scan_count = self.get_count(value=values, keys_list=keys_list, filter="SCAN_STARTED")
        print(scan_count)
        local_dict[str(phn_name)]["Scanning"] = scan_count
        association_attempt = self.get_count(value=values, keys_list=keys_list, filter="ASSOCIATING")
        print(association_attempt)
        local_dict[str(phn_name)]["ConnectAttempt"] = association_attempt
        conected_count = self.get_count(value=values, keys_list=keys_list, filter="CTRL-EVENT-CONNECTED")
        print("conected_count", conected_count)
        local_dict[str(phn_name)]["Connected"] = conected_count
        assorej_count = self.get_count(value=values, keys_list=keys_list, filter="ASSOC_REJECT")
        print("asso rej", assorej_count)
        local_dict[str(phn_name)][ "Association Rejection"] = assorej_count
        print("local_dict", local_dict)
        logging.info("local_dict " + str(local_dict))

        return local_dict

    @property
    def run(self):
        try:
            # start timer
            test_time = datetime.now()
            test_time = test_time.strftime("%b %d %H:%M:%S")
            print("Test started at ", test_time)
            logging.info("Test started at " + str(test_time))
            # get the list of adb devices
            self.adb_device_list = self.interop.check_sdk_release()
            print("ADB Device List Which support SDK & not in phantom : ", self.adb_device_list)
            logging.info(self.adb_device_list)
            # Checking and selecting the number of available clients are equal to given clients
            if len(self.adb_device_list) == self.clients:  #TODO: NEED TO MODIFY THIS CHECKING LOGIC
                print("No of available clients is equal to provided clients")
                logging.info("No of available clients is equal to provided clients")
                print("*** Now choosing no of clients provided from available list randomly ***")
                logging.info("now choosing no of clients provided from available list randomly")
                new_device = []
                for i, x in zip(self.adb_device_list, range(int(self.clients))):
                    if x < self.clients:
                        new_device.append(i)
                print("New Device List", new_device)
                logging.info(new_device)
                self.adb_device_list = new_device
            else:
                print("No of available clients is less then provided clients to be tested, Please check it!")
                logging.info("no of available clients is less then provided clients to be tested, Please check it!")
                exit(1)
            # Fetching Name of the devices in a list if the active devices are available
            print("New device list, after chosen from random list", self.adb_device_list)
            logging.info("new device list " + str(self.adb_device_list))
            if len(self.adb_device_list) == 0:
                print("There is no active adb devices please check system")
                logging.warning("there is no active adb devices please check system")
                exit(1)
            else:
                for i in range(len(self.adb_device_list)):
                    self.phn_name.append(self.adb_device_list[i].split(".")[2])
                    print("Name of the Device:", self.phn_name)
                    logging.info("phn_name" + str(self.phn_name))

            # check status of devices
            phantom = []
            for i in self.adb_device_list:
                phantom.append(self.interop.get_device_details(device=i, query="phantom"))
            print("Device Phantom State List", phantom)
            logging.info(phantom)
            state = None
            for i in phantom:
                if str(i) == "False":
                    print("Devices are up")
                    logging.info("device are up")
                    state = "up"
                else:
                    print("Devices are not up")
                    logging.info("all devices are not up")
                    exit(1)
            if state == "up":
                # setting / modify user name
                self.interop.set_user_name(device=self.adb_device_list)
                for i in self.adb_device_list:
                    self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
                print("Updated Device Name", self.device_name)
                logging.info("device name " + str(self.device_name))
                print("waiting for 5 sec...")
                time.sleep(5)

                print("List out the network id's")
                Network_Id, Connected_ssid, Security = [], [], []
                for i in self.phn_name:
                    connected_network_info = self.utility.list_networks_info(device_name=i)
                    print(connected_network_info)
                    if connected_network_info == 'No networks':
                        print("No exiting networks found for %s device" % i)
                    else:
                        # Forget already existing network base on the network id
                        print("The %s device is already connected to %s SSID" % (i, connected_network_info['SSID']))
                        Network_Id.append(connected_network_info['Network Id'])
                        Connected_ssid.append(connected_network_info['SSID'])
                        Security.append(connected_network_info['Security type'])
                        print("Existing network id:", Network_Id)
                        print("Existing connected ssid:", Connected_ssid)
                        print("Existing connected network:", Security)
                        print("Forgetting already connected network")
                        logging.info("forget all previous connected networks")
                        for j in self.adb_device_list:
                            self.utility.forget_netwrk(device=j, network_id=Network_Id)
                        print("Waiting for 2 sec")
                        time.sleep(2)

                print("Stopping the APP")
                for i in self.adb_device_list:
                    self.interop.stop(device=i)

                print("Apply SSID configuring using batch modify")
                logging.info("apply ssid using batch modify")
                self.interop.batch_modify_apply(device=self.adb_device_list, manager_ip=self.mgr_ip)
                print("Check heath data")
                logging.info("check heath data")
                health = dict.fromkeys(self.adb_device_list)
                print("Health Data:", health)
                logging.info(str(health))

                for i in self.adb_device_list:
                    dev_state = self.utility.get_device_state(device=i)
                    print("State of the Device:", dev_state)
                    logging.info("device state" + dev_state)
                    if dev_state == "COMPLETED,":
                        print("Phone is in connected state")
                        logging.info("phone is in connected state")
                        ssid = self.utility.get_device_ssid(device=i)
                        if ssid == self.ssid:
                            print("The Device is connected to expected ssid")
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
                print("Health Status for the Device:", health)
                logging.info("health" + str(health))

                # Resting Starts from here
                reset_list = []
                for i in range(self.reset):
                    reset_list.append(i)
                print("Given No.of iterations for Reset :", len(reset_list))
                logging.info("reset list" + str(reset_list))
                reset_dict = dict.fromkeys(reset_list)
                for r, final in zip(range(self.reset), reset_dict):
                    time.sleep(int(self.time_int))  # sleeping until time interval finish
                    print("r", r)
                    logging.info("r " + str(r))
                    local_dict = dict.fromkeys(self.adb_device_list)
                    print("local dict", local_dict)

                    list_ = ["ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected"]
                    sec_dict = dict.fromkeys(list_)
                    for i in self.adb_device_list:
                        local_dict[i] = sec_dict.copy()
                    print(local_dict)
                    logging.info(str(local_dict))
                    for i, y in zip(self.adb_device_list, self.device_name):
                        # note last  log time
                        timee = self.get_last_wifi_msg()
                        # enable and disable Wi-Fi
                        print("**** Disable wifi")
                        logging.info("disable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="disable")
                        time.sleep(5)

                        print("*** Enable wifi")
                        logging.info("enable wifi")
                        self.interop.enable_or_disable_wifi(device=i, wifi="enable")
                        time.sleep(int(self.wait_time))
                        # log reading
                        get_dicct = self.get_time_from_wifi_msgs(local_dict=local_dict, phn_name=i, timee=timee)
                        reset_dict[r] = get_dicct
                print("reset_dict", reset_dict)
                logging.info("reset dict " +  str(reset_dict))
                logging.info("reset dict" + str(reset_dict))
                test_end = datetime.now()
                test_end = test_end.strftime("%b %d %H:%M:%S")
                print("Test ended at ", test_end)
                logging.info("Test ended at " + test_end)
                s1 = test_time
                s2 = test_end  # for example
                FMT = '%b %d %H:%M:%S'
                test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                return reset_dict, test_duration
        except Exception as e:
            print(e)

    def generate_per_station_graph(self, device_names=None, dataset=None, labels=None):
        # device_names = ['1.1.RZ8N70TVABP', '1.1.RZ8RA1053HJ']
        print("dataset", dataset)
        print(labels)
        print(device_names)
        # dataset = [[1, 1], [1, 1]]
        labels = ["Connected", "Disconnected"]
        graph = lf_graph.lf_bar_graph(_data_set=dataset, _xaxis_name="Device Name",
                                      _yaxis_name="Reset = " + str(self.reset),
                                      _xaxis_categories=device_names,
                                      _label=labels, _xticks_font=8,
                                      _graph_image_name="per_station_graph",
                                      _color=['g', 'r'], _color_edge='black',
                                      _figsize=(12, 4),
                                      _grp_title="Per station graph ",
                                      _xaxis_step=1,
                                      _show_bar_value=True,
                                      _text_font=6, _text_rotation=30,
                                      _legend_loc="upper right",
                                      _legend_box=(1, 1.15),
                                      _enable_csv=True
                                      )
        graph_png = graph.build_bar_graph()
        print("graph name {}".format(graph_png))
        return graph_png

    def generate_overall_graph(self, reset_dict=None):
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
            print(j)
            local = []
            local_2, local_3, local_4, local_5, local_6 = [], [], [], [], []
            for i in reset_dict:
                print(i)
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

        print("list ", conected_list, disconnected_list, scan_state, asso_attempt, asso_rej)

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

        print("scan", scan)
        print(ass_atmpt)
        print(conects)
        print(disconnects)
        print(assorej)

        # print("hi")
        print(data)
        data['Disconnected'] = disconnects
        data['Scans'] = scan
        data['Assoc Attempts'] = ass_atmpt
        data['Connected'] = conects
        data["Association Rejection"] = assorej
        print(data)

        # creating the dataset
        self.graph_image_name = "overall"
        courses = list(data.keys())
        values = list(data.values())
        print(courses)
        print(values)

        fig = plt.figure(figsize=(12, 4))

        # creating the bar plot
        plt.bar(courses, values, color=('plum', 'lawngreen', 'skyblue', 'pink', 'yellow', "cyan"),
                width=0.4)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', rotation=30, fontsize=8)

        plt.xlabel("Total", fontweight='bold', fontsize=15)
        plt.ylabel("Number", fontweight='bold', fontsize=15)
        plt.title("Port Reset Totals")
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        # plt.show()
        return "%s.png" % self.graph_image_name

    def per_client_graph(self, data=None, name=None):
        self.graph_image_name = name
        courses = list(data.keys())
        values = list(data.values())

        fig = plt.figure(figsize=(12, 4))

        # creating the bar plot
        plt.bar(courses, values, color=('plum', 'lawngreen', 'skyblue', 'pink', 'yellow', "cyan"),
                width=0.4)
        for item, value in enumerate(values):
            plt.text(item, value, "{value}".format(value=value), ha='center', rotation=30, fontsize=8)

        plt.xlabel("Total", fontweight='bold', fontsize=15)
        plt.ylabel("Number", fontweight='bold', fontsize=15)
        plt.title("Port Reset Totals")
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        # plt.show()
        return "%s.png" % self.graph_image_name

    def generate_report(self, reset_dict=None, test_dur=None):
        try:
            print("reset dict", reset_dict)
            print("Test Duration", test_dur)
            logging.info("reset dict " + str(reset_dict))
            report = lf_report_pdf.lf_report(_path="", _results_dir_name="Interop_port_reset_test",
                                             _output_html="port_reset_test.html",
                                             _output_pdf="port_reset_test.pdf")
            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            report_path = report.get_report_path()
            print(report_path)
            logging.info(report_path)
            report.move_data(_file_name="reset.log")
            test_setup_info = {
                "DUT Name": self.dut_name,
                "SSID": self.ssid,
                "Test Duration": test_dur,
            }
            report.set_title("LANforge Interop Port Reset Test")
            report.set_date(date)
            report.build_banner()
            report.set_table_title("Test Setup Information")
            report.build_table_title()

            report.test_setup_table(value="Device under test", test_setup_data=test_setup_info)
            report.set_obj_html("Objective",
                                "The LANforge interop port reset test allows user to use lots of real WiFi stations and"
                                " connect them the AP under test and then disconnect and reconnect a random number of"
                                " stations at random intervals. The objective of this test is to "
                                "mimic a enterprise/large public venue scenario where a number of stations arrive,"
                                " connect and depart in quick succession. A successful test result would be that "
                                "AP remains stable over the duration of the test and that stations can continue to reconnect to the AP.")
            report.build_objective()

            report.set_obj_html("Port Reset Total Graph",
                                "The below graph provides overall information regarding all the reset count where"
                                "Port resets=Total resets provided as test input, Disconnected=It is the total number "
                                "of disconnects happened for all clients during the test when WiFi was disabled , Scans=It is the"
                                "total number of scanning state achieved by all clients during the test when network is enabled back"
                                " again, Association attempts=It is the total number of association attempts(Associating state) achieved  by"
                                " all client after the WiFi is enabled back again in full test, Connected=It is the total number"
                                "of connection(Associated state) achieved by all clients during the test when Wifi is enabled back again."
                                " Here real clients used is "+ str(self.clients) + "and number of resets provided is " + str(self.reset))
            report.build_objective()
            graph2 = self.generate_overall_graph(reset_dict=reset_dict)
            # graph1 = self.generate_per_station_graph()
            report.set_graph_image(graph2)
            report.move_graph_image()
            report.build_graph()

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
                dict_ = ['Port Resets', 'Disconnected', 'Scans', 'Assoc Attempts', "Association Rejection", 'Connected']
                data = dict.fromkeys(dict_)
                data['Port Resets'] = self.reset
                dis = 0
                for i in disconnected:
                    dis = dis + i

                data['Disconnected'] = dis
                scan = 0
                for i in scanning:
                    scan = scan + i

                data['Scans'] = scan
                asso = 0
                for i in asso_attempts:
                    asso = asso + i
                data['Assoc Attempts'] = asso

                con = 0
                for i in connected:
                    con = con + i

                # data['Disconnected'] = dis
                data['Connected'] = con
                asso_rej = 0
                for i in assorej:
                    asso_rej = asso_rej + i

                data["Association Rejection"] = asso_rej
                print("data ", data)
                report.set_obj_html("Per Client Graph for client " + str(y.split(".")[2]),
                                    "The below graph provides information regarding per station behaviour for every reset count"
                                    " where"
                                    "Port resets=Total resets provided as test input, Disconnected=It is the total number "
                                    "of disconnects happened for a client  during every reset when WiFi was disabled , Scans=It is the"
                                    "total number of scanning state achieved by a client during the test when network is enabled back for "
                                    "every reset"
                                    " again, Association attempts=It is the total number of association attempts(Associating state) achieved  by"
                                    " a client after the WiFi is enabled back again in full test, Connected=It is the total number"
                                    "of connection(Associated state) achieved by a client during the test when Wifi is enabled back again.")
                report.build_objective()
                graph1 = self.per_client_graph(data=data, name="per_client_" + str(z))
                # graph1 = self.generate_per_station_graph()
                report.set_graph_image(graph1)
                report.move_graph_image()
                report.build_graph()
                # self.per_client_graph(data=data, name="per_client_" + str(z))

                # Table 1
                report.set_obj_html("Real Client " + y.split(".")[2] + " Reset Observations",
                                    "The below table shows actual behaviour of real devices for every reset value")
                report.build_objective()
                table_1 = {
                    "Reset Count": reset_count,
                    "Association attempts": asso_attempts,
                    "Disconnected": disconnected,
                    "Scanning": scanning,
                    "Association Rejection" : assorej,
                    "Connected": connected,
                }
                test_setup = pd.DataFrame(table_1)
                report.set_table_dataframe(test_setup)
                report.build_table()

            report.set_obj_html("Real Client Detail Info",
                                "The below table shows detail information of real clients")
            report.build_objective()
            d_name, device, model, user_name, release = [], [], [], [], []
            for y in self.adb_device_list:
                print("ins", y)
                print(self.adb_device_list)
                d_name.append(self.interop.get_device_details(device=y, query="name"))
                device.append(self.interop.get_device_details(device=y, query="device"))
                model.append(self.interop.get_device_details(device=y, query="model"))
                user_name.append(self.interop.get_device_details(device=y, query="user-name"))
                release.append(self.interop.get_device_details(device=y, query="release"))

            s_no = []
            for i in range(len(d_name)):
                s_no.append(i + 1)

            # self.clients = len(self.adb_device_list)

            table_2 = {
                "S.No": s_no,
                "Name": d_name,
                "device": device,
                "user-name": user_name,
                "model": model,
                "release": release
            }
            test_setup = pd.DataFrame(table_2)
            report.set_table_dataframe(test_setup)
            report.build_table()

            test_input_infor = {
                "LANforge ip": self.host,
                "LANforge port": "8080",
                "ssid": self.ssid,
                "band": self.band,
                "reset count": self.reset,
                "time interval between every reset(sec)": self.time_int,
                "No of Clients": self.clients,
                "Wait Time": self.wait_time,
                "Contact": "support@candelatech.com"
            }
            report.set_table_title("Test basic Input Information")
            report.build_table_title()
            report.test_setup_table(value="Information", test_setup_data=test_input_infor)

            report.build_footer()
            report.write_html()
            report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
        except Exception as e:
            print(str(e))
            logging.warning(str(e))


def main():
    desc = """ port reset test 
    run: lf_interop_port_reset_test.py --host 192.168.1.31
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

    parser.add_argument("--band", default="5G",
                        help='specify the type of band you want to perform testing eg 5G|2G|Dual')

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
                           band=args.band,
                           reset=args.reset,
                           clients=args.clients,
                           time_int=args.time_int,
                           wait_time=args.wait_time,
                           suporrted_release=args.release,
                           mgr_ip=args.mgr_ip
                           )
    reset_dict, duration = obj.run
    # reset_dict = {0: {'1.1.RZ8RA1053HJ': {'ConnectAttempt': 2, 'Disconnected': 1, 'Scanning': 2, 'Connected': 1}}, 1: {'1.1.RZ8RA1053HJ': {'ConnectAttempt': 2, 'Disconnected': 1, 'Scanning': 3, 'Connected': 1}}}
    # duration = "xyz"
    obj.generate_report(reset_dict=reset_dict, test_dur=duration)


if __name__ == '__main__':
    main()
