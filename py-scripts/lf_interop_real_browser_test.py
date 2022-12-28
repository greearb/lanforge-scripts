#!/usr/bin/env python3
"""
Purpose: To be generic script for LANforge-Interop devices(Real clients) which runs layer4-7 traffic
    For now the test script supports Real Browser test. In the future it should support webpage test, Video streaming also

Pre-requisites: Real should be connected to the LANforge MGR and WE-CAN app should be open on the real clients which are connected to Lanforge

Future request/TO-DO: Configuring the real clients also should be done based on the SSID provided, Reporting is pending

Example: (python3 or ./)lf_interop_real_browser_test.py --mgr 192.168.219.125 --duration 1 --url "www.amazon.com"

Prints the list of data from layer4-7 such as uc-avg time, total url's, url's per sec
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


class RealBrowserTest(Realm):
    def __init__(self, host, ssid, passwd, encryp, suporrted_release=None, max_speed=None, url=None,
                 urls_per_tenm=None, duration=None):
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
        self.max_speed = max_speed
        self.url = url
        self.urls_per_tenm = urls_per_tenm
        self.duration = duration
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=8080)
        self.http_profile = self.local_realm.new_http_profile()
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
        # Checks various configuration things on Interop tab, Uses lf_base_interop_profile.py library
        self.adb_device_list = self.interop.check_sdk_release()
        for i in self.adb_device_list:
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
                    print("Launching Interop UI")
                    self.interop.launch_interop_ui(device=i)
        self.health = health
        print("Health:: ", health)

        self.phone_data = self.get_resource_data()
        print("Phone List : ", self.phone_data)
        time.sleep(5)

    def build(self):
        """If the Pre-requisites are satisfied then this function gets the list of Real devices connected to LANforge
        and processes them for Layer 4-7 traffic profile creation
        """
        self.phone_data = self.get_resource_data()
        print("Phone List : ", self.phone_data)
        time.sleep(5)
        self.http_profile.direction = 'dl'
        self.http_profile.dest = '/dev/null'
        self.http_profile.max_speed = self.max_speed
        self.http_profile.requests_per_ten = self.urls_per_tenm
        # create http profile
        # for i in self.phone_data:
        # self.phone_data = ['1.16.wlan0', '1.17.xlan0', '1.20.ylan0']
        self.http_profile.create(ports=self.phone_data, sleep_time=.5,
                                 suppress_related_commands_=None, http=True,
                                 http_ip=self.url, interop=True)

    def start(self):
        # Starts the layer 4-7 traffic for created CX end points
        print("Test Started")
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    def stop(self):
        # Stops the layer 4-7 traffic for created CX end points
        self.http_profile.stop_cx()
        print("Test Stopped")

    def postcleanup(self):
        # Cleans the layer 4-7 traffic for created CX end points
        self.http_profile.cleanup()

    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        # print(data)
        data1 = []
        data = data['endpoint']
        for cx in self.http_profile.created_cx.keys():
            for info in data:
                if cx in info:
                    data1.append(info[cx][data_mon])
        # print(data_mon, data1)
        return data1

    def get_resource_data(self):
        # Gets the list of Real devices connected to LANforge
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
        return station_name


def main():
    desc = """ Real browser test 
            run: lf_interop_webpage.py --host 192.168.200.69
            """

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--host", "--mgr", default='192.168.200.69', help='specify the GUI to connect to, assumes port '
                                                                        '8080')
    parser.add_argument("--ssid", default="ssid_wpa_2g", help='specify ssid on which the test will be running')
    parser.add_argument("--passwd", default="something", help='specify encryption password  on which the test will '
                                                           'be running')
    parser.add_argument("--encryp", default="psk", help='specify the encryption type  on which the test will be '
                                                         'running eg :open|psk|psk2|sae|psk2jsae')
    parser.add_argument("--url", default="www.google.com", help='specify the url you want to test on')
    parser.add_argument("--max_speed", type=int, default=0, help='specify the max speed you want in bytes')
    parser.add_argument("--urls_per_tenm", type=int, default=60, help='specify the number of url you want to test on '
                                                                      'per minute')
    parser.add_argument('--duration', type=int, help='time to run traffic')
    args = parser.parse_args()
    obj = RealBrowserTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                          suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                          url=args.url, urls_per_tenm=args.urls_per_tenm, duration=args.duration)
    test_time = datetime.now()
    test_time = test_time.strftime("%b %d %H:%M:%S")
    print("Test started at ", test_time)
    # obj.run
    obj.build()
    obj.start()
    duration = args.duration
    duration = 60 * duration
    print("time in seconds ", duration)
    time.sleep(duration)
    obj.stop()
    uc_avg_val = obj.my_monitor('uc-avg')
    total_urls = obj.my_monitor('total-urls')
    urls_per_sec = obj.my_monitor('urls/s')
    print(uc_avg_val, total_urls, urls_per_sec) # Prints the list of values from layer4-7
    obj.postcleanup()
    # test_end = datetime.now()
    # test_end = test_end.strftime("%b %d %H:%M:%S")
    # print("Test ended at ", test_end)
    # s1 = test_time
    # s2 = test_end  # for example
    # FMT = '%b %d %H:%M:%S'
    # test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
    # print("total test duration ", test_duration)
    # date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    # test_setup_info = {
    #     "DUT Name": args.ap_name,
    #     "SSID": ', '.join(info_ssid),
    #     "Test Duration": test_duration,
    # }
    # test_input_infor = {
    #     "LANforge ip": args.host,
    #     "URL": args.url,
    #     # "Bands": args.bands,
    #     # "Upstream": args.upstream_port,
    #     "Clients": args.clients,
    #     "SSID": args.ssid,
    #     "Security": args.encryp,
    #     "Duration": args.duration,
    #     "Contact": "support@candelatech.com"
    # }
    # obj.generate_report(date, )

if __name__ == '__main__':
    main()