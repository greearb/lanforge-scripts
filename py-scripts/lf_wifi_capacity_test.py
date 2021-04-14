#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

Note: This is a test file which will run a wifi capacity test.
    ex. on how to run this script (if stations are available in lanforge):
    ./lf_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
    --instance_name this_inst --config_name test_con --upstream 1.1.eth1 --batch_size 1 --loop_iter 1
    --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0002

    ex. on how to run this script (to create new stations):
    ./lf_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
             --instance_name wct_instance --config_name wifi_config --upstream 1.1.eth1 --batch_size 1 --loop_iter 1
             --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0001
             --create_stations --radio "wiphy0" --ssid "" --security "open" --paswd "[BLANK]"

Note:
    --pull_report == If specified, this will pull reports from lanforge to your code directory,
                    from where you are running this code

    --stations == Enter stations to use for wifi capacity
"""

import sys
import os
import argparse
import time
import json
from os import path

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_test_manager import cv_test as cvtest
from cv_commands import chamberview as cv
from cv_test_reports import lanforge_reports as lf_rpt


class WiFiCapacityTest(cvtest):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="wct_instance",
                 config_name="wifi_config",
                 upstream="eth1",
                 batch_size="1",
                 loop_iter="1",
                 protocol="UDP-IPv4",
                 duration="5000",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_rate="10Mbps",
                 download_rate="1Gbps",
                 sort="interleave",
                 stations="",
                 create_stations=False,
                 radio="wiphy0",
                 security="open",
                 paswd="[BLANK]",
                 ssid=""
                 ):
        super().__init__(lfclient_host=lf_host, lfclient_port=lf_port)

        self.lf_host = lf_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password =lf_password
        self.createCV = cv(lf_host, lf_port);
        self.station_profile = self.new_station_profile()
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "WiFi Capacity"
        self.batch_size = batch_size
        self.loop_iter = loop_iter
        self.protocol = protocol
        self.duration = duration
        self.upload_rate = upload_rate
        self.download_rate = download_rate
        self.upstream = upstream
        self.sort = sort
        self.stations = stations
        self.create_stations =create_stations
        self.security = security
        self.ssid = ssid
        self.paswd = paswd
        self.radio = radio

    def setup(self):
        if self.create_stations and self.stations != "":
            sta = self.stations.split(",")
            self.station_profile.cleanup(sta)
            self.station_profile.use_security(self.security, self.ssid, self.paswd)
            self.station_profile.create(radio=self.radio, sta_names_=sta, debug=self.debug)
            self.station_profile.admin_up()
            self.wait_for_ip(station_list=sta)
            print("stations created")


    def run(self):
        self.createCV.sync_cv()
        time.sleep(2)

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = ["batch_size: " + str(self.batch_size),
                       "loop_iter: " + str(self.loop_iter),
                       "protocol: " + str(self.protocol),
                       "duration: " + str(self.duration),
                       "ul_rate: " + self.upload_rate,
                       "dl_rate: " + self.download_rate,
                       ]

        port_list = [self.upstream]
        if self.stations == "":
            stas = self.station_map()  # See realm
            for eid in stas.keys():
                port_list.append(eid)
        else:
            stas = self.stations.split(",")
            for s in stas:
                port_list.append(s)

        idx = 0
        for eid in port_list:
            add_port = "sel_port-" + str(idx) + ": " + eid
            self.create_test_config(self.config_name, "Wifi-Capacity-", add_port)
            idx += 1

        for value in cfg_options:
            self.create_test_config(self.config_name, "Wifi-Capacity-", value)

        # Request GUI update its text blob listing.
        self.show_text_blob(self.config_name, "Wifi-Capacity-", False)

        # Hack, not certain if the above show returns before the action has been completed
        # or not, so we sleep here until we have better idea how to query if GUI knows about
        # the text blob.
        time.sleep(5)

        load_old = "false"
        if self.load_old_cfg:
            load_old = "true"

        for i in range(60):
            response = self.create_test(self.test_name, self.instance_name, load_old)
            d1 = {k: v for e in response for (k, v) in e.items()}
            if d1["LAST"]["response"] == "OK":
                break
            else:
                time.sleep(1)

        self.load_test_config(self.config_name, self.instance_name)
        self.auto_save_report(self.instance_name)

        if self.sort == 'linear':
            cmd = "cv click '%s' 'Linear Sort'" % self.instance_name
            self.run_cv_cmd(cmd)
        if self.sort == 'interleave':
            cmd = "cv click '%s' 'Interleave Sort'" % self.instance_name
            self.run_cv_cmd(cmd)

        response = self.start_test(self.instance_name)
        d1 = {k: v for e in response for (k, v) in e.items()}
        if d1["LAST"]["response"].__contains__("Could not find instance:"):
            print("ERROR:  start_test failed: ", d1["LAST"]["response"], "\n");
            # pprint(response)
            exit(1)

        while (True):
            check = self.get_report_location(self.instance_name)
            location = json.dumps(check[0]["LAST"]["response"])
            if location != "\"Report Location:::\"":
                location = location.replace("Report Location:::", "")
                self.close_instance(self.instance_name)
                self.cancel_instance(self.instance_name)
                location = location.strip("\"")
                report = lf_rpt()
                print(location)
                try:
                    if self.pull_report:
                        report.pull_reports(hostname=self.lf_host, username=self.lf_user, password=self.lf_password,
                                            report_location=location)
                except:
                    raise Exception("Could not find Reports")
                break

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name


def main():

    parser = argparse.ArgumentParser(
        description="""
             ./lf_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge     
             --instance_name wct_instance --config_name wifi_config --upstream 1.1.eth1 --batch_size 1 --loop_iter 1     
             --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0001 
             --create_stations --radio "wiphy0" --ssid "" --security "open" --paswd "[BLANK]"
               """)
    parser.add_argument("-m", "--mgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user", type=str, default="lanforge",
                        help="Lanforge username to pull reports")
    parser.add_argument("--lf_password", type=str, default="lanforge",
                        help="Lanforge Password to pull reports")
    parser.add_argument("-i", "--instance_name", type=str,
                        help="create test instance")
    parser.add_argument("-c", "--config_name", type=str,
                        help="Config file name")
    parser.add_argument("-u", "--upstream", type=str, default="1.1.eth1",
                        help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("-b", "--batch_size", type=str, default="1,5,10",
                        help="station increment ex. 1,2,3")
    parser.add_argument("-l", "--loop_iter", type=str, default="1",
                        help="Loop iteration ex. 1")
    parser.add_argument("-p", "--protocol", type=str, default="TCP-IPv4",
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("-d", "--duration", type=str, default="10000",
                        help="duration in ms. ex. 5000")
    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--load_old_cfg", default=False, action='store_true',
                        help="Should we first load defaults from previous run of the capacity test?  Default is False")
    parser.add_argument("--download_rate", type=str, default="1Gbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 1Gbps")
    parser.add_argument("--upload_rate", type=str, default="10Mbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--sort", type=str, default="interleave",
                        help="Select station sorting behaviour:  none | interleave | linear  Default is interleave.")
    parser.add_argument("-s", "--stations", type=str, default="",
                        help="If specified, these stations will be used.  If not specified, all available stations will be selected.  Example: 1.1.sta001,1.1.wlan0,...")
    parser.add_argument("-cs", "--create_stations", default=False, action='store_true',
                        help="create stations in lanforge (by default: False)")
    parser.add_argument("-radio", "--radio", default="wiphy0",
                        help="create stations in lanforge at this radio (by default: wiphy0)")
    parser.add_argument("-ssid", "--ssid", default="",
                        help="ssid name")
    parser.add_argument("-security", "--security", default="open",
                        help="ssid Security type")
    parser.add_argument("-paswd", "--paswd", default="[BLANK]",
                        help="ssid Password")
    args = parser.parse_args()

    WFC_Test = WiFiCapacityTest(lf_host=args.mgr,
                                lf_port=args.port,
                                lf_user=args.lf_user,
                                lf_password=args.lf_password,
                                instance_name=args.instance_name,
                                config_name=args.config_name,
                                upstream=args.upstream,
                                batch_size=args.batch_size,
                                loop_iter=args.loop_iter,
                                protocol=args.protocol,
                                duration=args.duration,
                                pull_report=args.pull_report,
                                load_old_cfg=args.load_old_cfg,
                                download_rate=args.download_rate,
                                upload_rate=args.upload_rate,
                                sort=args.sort,
                                stations=args.stations,
                                create_stations=args.create_stations,
                                radio =args.radio,
                                ssid=args.ssid,
                                security =args.security,
                                paswd =args.paswd ,
                                )
    WFC_Test.setup()
    WFC_Test.run()


if __name__ == "__main__":
    main()
