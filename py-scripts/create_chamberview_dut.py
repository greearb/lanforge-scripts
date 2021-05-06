#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

Note: This script is used to create a DUT in chamber view.
        Manual steps:
            1. open GUI
            2. click Chamber View
            3. right click on empty space in Scenario configuration  select "New DUT"
            4. Enter Name (DUT Name), SSID , Security type, BSsid (if available)
            5. click on apply and OK
            6. you will see a DUT created in chamber view under scenario configuration

Note : If entered DUT name is already created in lanforge,
    it will overwrite on to that DUT ( All information will be overwritten )
    Which means it will "Update the DUT".

    If entered DUT name is not already in lanforge,
    then new DUT will be created will all the provided information

How to Run this:
    ./create_chamberview_dut --lfmgr "localhost" --port "8080" --dut_name "dut_name"
                --ssid "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP bssid=78:d2:94:bf:16:41"
                --ssid "ssid_idx=1 ssid=NET1 security=WPA password=test bssid=78:d2:94:bf:16:40"

    --lfmgr = IP of lanforge
    --port = Default 8080
    --dut_name = Enter name of DUT ( to update DUT enter same DUT name )
                                ( enter new DUT name to create a new DUT)
    --ssid = "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP bssid=78:d2:94:bf:16:41"

            --ssid will take = ssid_idx (from 0 to 7) : we can add upto 7 ssids to a DUT
                             = ssid : Name of SSID
                             = security : Security type WPA|WEP|11r|EAP-PEAP ( in case of multiple security add "|"
                                        after each type ex. WPA|WEP (this will select WPA and WEP both)
                             = bssid : Enter BSSID
                             (if you dont want to give bssid
                                --ssid "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP"
                                )

Output : DUT will be created in Chamber View
"""


import sys
import os
import argparse
import time
import re

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_dut_profile import cv_dut as dut
from cv_test_manager import cv_test as cvtest

class DUT(dut):
    def __init__(self,
                 lfmgr="localhost",
                 port="8080",
                 dut_name="DUT",
                 ssid=[],
                 password=[],
                 bssid=[],
                 security=[]
                 ):
        super().__init__(
            lfclient_host=lfmgr,
            lfclient_port=port,
        )
        self.cv_test = cvtest(lfmgr, port)
        self.dut_name = dut_name
        self.ssid = ssid
        self.password = password
        self.bssid = bssid
        self.security = security

    def setup(self):
        self.create_dut(dut_name=self.dut_name)

    def add_ssids(self):
        if self.ssid:

            for i in range(len(self.ssid)):

                if " " in self.ssid[i][0]:
                    self.ssid[i][0] = (re.split(' ', self.ssid[i][0]))
                elif "," in self.ssid[i][0]:
                    self.ssid[i][0] = (re.split(',', self.ssid[i][0]))
                elif ", " in self.ssid[i][0]:
                    self.ssid[i][0] = (re.split(',', self.ssid[i][0]))
                elif " ," in self.ssid[i][0]:
                    self.ssid[i][0] = (re.split(',', self.ssid[i][0]))
                else:
                    print("Wrong arguments entered !")
                    exit(1)

                ssid_idx = 0
                ssid = "[BLANK]"
                passwd = "[BLANK]"
                bssid = "00:00:00:00:00:00"
                flag = 0x0

                for j in range(len(self.ssid[i][0])):
                    self.ssid[i][0][j] = self.ssid[i][0][j].split("=")
                    for k in range(len(self.ssid[i][0][j])):
                        name = self.ssid[i][0][j][k]
                        if str(name) == "SSID" or str(name) == "ssid" or str(name) == "s":
                            ssid = self.ssid[i][0][j][k + 1]
                        elif str(name) == "PASSWORD" or str(name) == "password" or str(name) == "pass":
                            passwd = self.ssid[i][0][j][k + 1]
                        elif str(name) == "ssid_idx" or str(name) == "no" or str(name) == "N":
                            ssid_idx = self.ssid[i][0][j][k + 1]
                        elif str(name) == "security" or str(name) == "sec":
                            if self.ssid[i][0][j][k + 1]:
                                all_flags = self.ssid[i][0][j][k + 1].split("|")
                                for flags in all_flags:
                                    if flags == "WEP" or flags == "wep":
                                        flag += 0x8
                                    if flags == "WPA" or flags == "wpa":
                                        flag += 0x10
                                    if flags == "WPA2" or flags == "wpa2":
                                        flag += 0x20
                                    if flags == "WPA3" or flags == "wpa3":
                                        flag += 0x100
                                    if flags == "11r":
                                        flag += 0x200
                                    if flags == "EAP-TTLS":
                                        flag += 0x400
                                    if flags == "EAP-PEAP":
                                        flag += 0x800
                        elif str(name) == "BSSID" or str(name) == "bssid" or str(name) == "B":
                            bssid = self.ssid[i][0][j][k + 1]
                        else:
                            continue

                self.add_ssid(dut_name=self.dut_name,
                          ssid_idx=ssid_idx,
                          ssid=ssid,
                          passwd=passwd,
                          bssid=bssid,
                          ssid_flags=flag,
                          ssid_flags_mask=0xFFFFFFFF
                          )



def main():
    parser = argparse.ArgumentParser(
        description="""
        ./create_chamberview_dut -m "localhost" -o "8080" -d "dut_name" 
                -ssid "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP bssid=78:d2:94:bf:16:41" 
                -ssid "ssid_idx=1 ssid=NET1 security=WPA password=test bssid=78:d2:94:bf:16:40"
               """)
    parser.add_argument("-m", "--lfmgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=str, default="8080",
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-d", "--dut_name", type=str, default="DUT",
                        help="set dut name")
    parser.add_argument("-s", "--ssid", action='append', nargs=1,
                        help="SSID", default=[])


    args = parser.parse_args()
    new_dut = DUT(args.lfmgr,
                  args.port,
                  args.dut_name,
                  args.ssid,
                  )

    new_dut.setup()
    new_dut.add_ssids()
    new_dut.cv_test.show_text_blob(None, None, True)  # Show changes on GUI
    new_dut.cv_test.sync_cv()
    time.sleep(2)
    new_dut.cv_test.sync_cv()

if __name__ == "__main__":
    main()
