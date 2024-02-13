#!/usr/bin/env python3
"""
NAME: lf_interop_port_reset_test.py

PURPOSE: for port reset test i.e getting cx time after disabling Wi-Fi from devices

EXAMPLE:
$ ./lf_interop_port_reset_test.py --host 192.168.1.31

NOTES:
#Currently this script will forget all network and then apply batch modify on real devices connected to LANforge
and in the end generates report which mentions cx time taken by each real client
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
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")


class ClientConnectivity(Realm):
    def __init__(self, host, ssid, passwd, encryp, suporrted_release=None):
        super().__init__(lfclient_host=host, lfclient_port=8080)
        self.adb_device_list = None
        self.host = host
        self.phn_name = []
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp
        self.supported_release = suporrted_release
        self.device_name = []
        self.health = None
        self.phone_data = None

        self.interop = base.BaseInteropWifi(manager_ip=self.host,
                                            port=8080,
                                            ssid=self.ssid,
                                            passwd=self.passwd,
                                            encryption=self.encryp,
                                            release=self.supported_release,
                                            screen_size_prcnt=0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)
        self.utility = base.UtilityInteropWifi(host_ip=self.host)
        logging.basicConfig(filename='reset.log', filemode='w', level=logging.INFO, force=True)

    @property
    def run(self):
        self.adb_device_list = self.interop.check_sdk_release()
        for i in self.adb_device_list: \
                self.device_name.append(self.interop.get_device_details(device=i, query="user-name"))
        print(self.device_name)

        self.interop.stop()
        for i in self.adb_device_list:
            self.interop.batch_modify_apply(i)
            time.sleep(5)
        self.interop.set_user_name(device=self.adb_device_list)

        for i in self.adb_device_list:
            self.utility.forget_netwrk(i)

        health = dict.fromkeys(self.adb_device_list)
        # Getting Health for each device
        for i in self.adb_device_list:
            # post = self.utility.post_adb_(device=i,cmd="shell ip addr show wlan0  | grep 'inet ' | cut -d ' ' -f 6 | cut -d / -f 1")
            # print("POST IP ", post)
            dev_state = self.utility.get_device_state(device=i)
            print("device state", dev_state)
            logging.info("device state" + dev_state)
            if dev_state == "COMPLETED,":
                print("phone is in connected state")
                logging.info("phone is in connected state")
                ssid = self.utility.get_device_ssid(device=i)
                if ssid == self.ssid:
                    print("device is connected to expected ssid")
                    logging.info("device is connected to expected ssid")
                    health[i] = self.utility.get_wifi_health_monitor(device=i, ssid=self.ssid)
                    print("health health:: ", health)
        self.health = health
        print("Health:: ", health)

        self.phone_data = self.get_resource_data()
        print("Phone List : ", self.phone_data)
        time.sleep(5)

    def generate_report(self):
        report = lf_report(_output_html="lf_interop_client_connectivity.html",
                           _output_pdf="lf_interop_client_connectivity.pdf",
                           _results_dir_name="Interop_Client_Connectivity")

        # report_path = report.get_path()
        # report_path_date_time = report.get_path_date_time()

        report.set_title("LANforge InterOp Client Connectivity")
        report.build_banner()
        report.set_obj_html(_obj_title="Objective", _obj="This connectivity LANforge InterOp measures the client "
                                                         "performances of each real devices ")
        report.build_objective()
        report.end_content_div()

        test_setup_info = pd.DataFrame({
            "Server IP": [self.host],
            "Target SSID": [self.ssid],
            "Security": [self.encryp],
            "Password": [self.passwd],
        })

        report.start_content_div()
        report.test_setup_table(test_setup_data=test_setup_info, value="Test Setup Information")
        report.end_content_div()

        phone_info = pd.DataFrame({
            "Resource Id": self.phone_data[0],
            "Phone Name": self.phone_data[1],
            "MAC Address": self.phone_data[2],
            "User Name": self.phone_data[3],
            "Radio": self.phone_data[4],
            "Rx Rate": self.phone_data[6],
            "Tx Rate": self.phone_data[7],
            "SSID Connected": self.phone_data[8],
        })

        report.start_content_div()
        report.set_table_title("<h3>Real Devices Details")
        report.build_table_title()
        report.set_table_dataframe(phone_info)
        report.build_table()

        phone_serial = []
        connectAttempt = []
        connectFailure = []
        assocRej = []
        assocTimeout = []
        print(self.health)
        for k, v in self.health.items():
            phone_serial.append(k)
            if v is None:
                connectAttempt.append('NA')
                connectFailure.append('NA')
                assocRej.append('NA')
                assocTimeout.append('NA')
            else:
                connectAttempt.append(v['ConnectAttempt'])
                connectFailure.append(v['ConnectFailure'])
                assocRej.append(v['AssocRej'])
                assocTimeout.append(v['AssocTimeout'])

        health = pd.DataFrame({
            "Phone Serial": phone_serial,
            "Connection Attempt": connectAttempt,
            "Connection Failure": connectFailure,
            "Association Rejection": assocRej,
            "Association Timeout": assocTimeout,
            "User Name": self.device_name,
        })

        report.start_content_div()
        report.set_table_title("<h3>Supported devices health details")
        report.build_table_title()
        report.set_table_dataframe(health)
        report.build_table()

        report.build_footer()
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)

        report.write_pdf(_page_size='Legal', _orientation='Portrait')

    def get_resource_data(self):
        resource_id_list = []
        phone_name_list = []
        mac_address = []
        user_name = []
        phone_radio = []
        rx_rate = []
        tx_rate = []
        station_name = []
        ssid = []
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    station_name.append(i)
                    resource_id_list.append(i.split(".")[1])
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    # Getting MAC address
                    mac = alias[i]["mac"]

                    rx = "Unknown" if (alias[i]["rx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["rx-rate"]
                    tx = "Unknown" if (alias[i]["tx-rate"] == 0 or alias[i]["rx-rate"] == '') else alias[i]["tx-rate"]
                    ssid.append(alias[i]["ssid"])
                    rx_rate.append(rx)
                    tx_rate.append(tx)
                    # Getting username
                    user = resource_hw_data['resource']['user']
                    user_name.append(user)
                    # Getting user Hardware details/Name
                    hw_name = resource_hw_data['resource']['hw version'].split(" ")
                    name = " ".join(hw_name[0:2])
                    phone_name_list.append(name)
                    mac_address.append(mac)
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and alias[i]["parent dev"] == 'wiphy0':
                    # phone_radio.append(alias[i]['mode'])
                    # Mapping Radio Name in human readable format
                    if 'a' not in alias[i]['mode'] or "20" in alias[i]['mode']:
                        phone_radio.append('2G')
                    elif 'AUTO' in alias[i]['mode']:
                        phone_radio.append("AUTO")
                    else:
                        phone_radio.append('2G/5G')
        return [resource_id_list, phone_name_list, mac_address, user_name, phone_radio, station_name, rx_rate, tx_rate,
                ssid]


def main():
    desc = """ Client Connectivity test 
        run: lf_interop_client_connectivity_test.py --host 192.168.200.232
        """

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--host", "--mgr", default='192.168.1.31', help='specify the GUI to connect to, assumes port '
                                                                        '8080')
    parser.add_argument("--ssid", default="NETGEAR65_5GHz", help='specify ssid on which the test will be running')
    parser.add_argument("--passwd", default="NETG23", help='specify encryption password  on which the test will '
                                                           'be running')
    parser.add_argument("--encryp", default="psk2", help='specify the encryption type  on which the test will be '
                                                         'running eg :open|psk|psk2|sae|psk2jsae')

    args = parser.parse_args()
    obj = ClientConnectivity(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                             suporrted_release=["7.0", "10", "11", "12"])
    obj.run
    obj.generate_report()


if __name__ == '__main__':
    main()