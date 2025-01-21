#!/usr/bin/env python3
# flake8: noqa
"""
NAME: create_chamberview_dut.py

PURPOSE: This script creates a dut with given parameters like dut name,ssid,security,bssid in chamber view.

EXAMPLE:
        ./create_chamberview_dut --lfmgr localhost --mgr_port 8080 --dut_name dut_name
        --ssid "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP|open bssid=78:d2:94:bf:16:41"
        --ssid "ssid_idx=1 ssid=NET1 security=WPA password=test bssid=78:d2:94:bf:16:40"

SCRIPT_CLASSIFICATION :  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        To Run this script gui should be opened with

            path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                  pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                  ./lfclient.bash -cli-socket 3990

        This script is used to create a DUT in chamber view.
                Manual steps:
                    1. open GUI
                    2. click Chamber View
                    3. right click on empty space in Scenario configuration  select "New DUT"
                    4. Enter Name (DUT Name), SSID , Security type, BSsid (if available)
                    5. click on apply and OK
                    6. you will see a DUT created in chamber view under scenario configuration

        If entered DUT name is already created in lanforge,
        it will overwrite on to that DUT ( All information will be overwritten )
        Which means it will "Update the DUT".

        If entered DUT name is not already in lanforge,
        then new DUT will be created will all the provided information

        The contents of '--ssid' argument are split with shlex, so you can do commands like this as well:
        ./create_chamberview_dut.py --lfmgr localhost --dut_name regression_dut
            --ssid "ssid_idx=0 ssid='j-wpa2-153 space' security='wpa2' password=j-wpa2-153 bssid=04:f0:21:cb:01:8b"

        --lfmgr = IP of lanforge
        --mgr_port = Default 8080
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

STATUS: Functional

VERIFIED_ON: 31-JULY-2023
            Build version - 5.4.6
            kernel version - 6.2.16+

LICENSE:
        Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

"""
import sys
import os
import importlib
import argparse
import time
import shlex
import logging

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

# from cv_dut_profile import cv_dut as dut
cv_dut_profile = importlib.import_module("py-json.cv_dut_profile")
dut = cv_dut_profile.cv_dut
# from cv_test_manager import cv_test as cvtest
cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cvtest = cv_test_manager.cv_test
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class DUT(dut):
    def __init__(self,
                 lfmgr="localhost",
                 port="8080",
                 dut_name="DUT",
                 ssid=None,
                 sw_version="NA",
                 hw_version="NA",
                 serial_num="NA",
                 model_num="NA",
                 dut_flags=None,
                 ):
        super().__init__(
            lfclient_host=lfmgr,
            lfclient_port=port,
            sw_version=sw_version,
            hw_version=hw_version,
            serial_num=serial_num,
            model_num=model_num,
            desired_dut_flags=dut_flags,
            desired_dut_flags_mask=dut_flags
        )
        if ssid is None:
            ssid = []
        self.cv_dut_name = dut_name
        self.cv_test = cvtest(lfmgr, port)
        self.dut_name = dut_name
        self.ssid = ssid

    def setup(self):
        self.create_dut()

    def add_ssids(self):
        flags = dict()
        flags['wep'] = 0x8
        flags['wpa'] = 0x10
        flags['wpa2'] = 0x20
        flags['wpa3'] = 0x100
        flags['11r'] = 0x200
        flags['eap-ttls'] = 0x400
        flags['eap-peap'] = 0x800
        flags['open'] = 0x0
        if self.ssid:
            for j in range(len(self.ssid)):
                self.ssid[j] = shlex.split(self.ssid[j][0])
                for k in range(len(self.ssid[j])):
                    kvp = self.ssid[j][k].split('=')
                    # print("key -:%s:-  val -:%s:-" % (kvp[0], kvp[1]))
                    self.ssid[j][k] = kvp

                d = dict()
                for item in self.ssid[j]:
                    d[item[0].lower()] = item[1]
                self.ssid[j] = d
                self.ssid[j]['flag'] = []

                flag = 0x0
                if 'security' in self.ssid[j].keys():
                    self.ssid[j]['security'] = self.ssid[j]['security'].split('|')
                    for security in self.ssid[j]['security']:
                        # print("security: %s  flags: %s  keys: %s" % (security, flags, flags.keys()))
                        if security.lower() in flags:
                            flag |= flags[security.lower()]
                            # print("updated flag: %s" % (flag))
                        else:
                            emsg = "ERROR:  Un-supported security flag: %s" % (security)
                            logger.critical(emsg)
                            raise ValueError("Un-supported security flag")  # Bad user input, terminate script.

                self.ssid[j]['flag'] = flag

                if 'bssid' not in self.ssid[j].keys():
                    self.ssid[j]['bssid'] = '00:00:00:00:00:00'

                if 'password' not in self.ssid[j].keys():
                    self.ssid[j]['password'] = '[BLANK]'

                self.add_ssid(dut_name=self.dut_name,
                              ssid_idx=self.ssid[j]['ssid_idx'],
                              ssid=self.ssid[j]['ssid'],
                              passwd=self.ssid[j]['password'],
                              bssid=self.ssid[j]['bssid'],
                              ssid_flags=self.ssid[j]['flag'],
                              ssid_flags_mask=0xFFFFFFFF
                              )

    def add_notes(self, dut_name="DUT", text="[BLANK]"):
        self.add_note(dut_name=dut_name, text=text)


def main():
    help_summary = '''\
    This script create chamberview dut script is designed to configure DUT using chamberview scenario.
    This script allows the user to configure DUT with the parameters like ssid, password,security and BSSID.
    The DUT created can be seen in the chamber view under scenario configuration.
    '''
    parser = argparse.ArgumentParser(
        prog='create_chamberview_dut.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description="""

NAME: create_chamberview_dut.py

PURPOSE: This script creates a dut with given parameters like dut name,ssid,security,bssid in chamber view.

EXAMPLE:
        ./create_chamberview_dut --lfmgr localhost --mgr_port 8080 --dut_name dut_name
        --ssid "ssid_idx=0 ssid=NET1 security=WPA|WEP|11r|EAP-PEAP|open bssid=78:d2:94:bf:16:41"
        --ssid "ssid_idx=1 ssid=NET1 security=WPA password=test bssid=78:d2:94:bf:16:40"

SCRIPT_CLASSIFICATION :  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        To Run this script gui should be opened with

            path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
                  pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
                  ./lfclient.bash -cli-socket 3990

        This script is used to create a DUT in chamber view.
                Manual steps:
                    1. open GUI
                    2. click Chamber View
                    3. right click on empty space in Scenario configuration  select "New DUT"
                    4. Enter Name (DUT Name), SSID , Security type, BSsid (if available)
                    5. click on apply and OK
                    6. you will see a DUT created in chamber view under scenario configuration

        If entered DUT name is already created in lanforge,
        it will overwrite on to that DUT ( All information will be overwritten )
        Which means it will "Update the DUT".

        If entered DUT name is not already in lanforge,
        then new DUT will be created will all the provided information

        The contents of '--ssid' argument are split with shlex, so you can do commands like this as well:
        ./create_chamberview_dut.py --lfmgr localhost --dut_name regression_dut
            --ssid "ssid_idx=0 ssid='j-wpa2-153 space' security='wpa2' password=j-wpa2-153 bssid=04:f0:21:cb:01:8b"

        --lfmgr = IP of lanforge
        --mgr_port = Default 8080
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

STATUS: Functional

VERIFIED_ON: 31-JULY-2023
            Build version - 5.4.6
            kernel version - 6.2.16+

LICENSE:
        Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

""")
    parser.add_argument(
        "-m",
        "--lfmgr",
        "--mgr",
        dest="lfmgr",
        type=str,
        default="localhost",
        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument(
        "-o",
        "--port",
        "--mgr_port",
        dest="port",
        type=str,
        default="8080",
        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-d", "--dut_name", type=str, default="DUT",
                        help="set dut name")
    parser.add_argument("-s", "--ssid", action='append', nargs=1,
                        help="SSID", default=[])

    parser.add_argument(
        "--sw_version",
        default="NA",
        help="DUT Software version.")
    parser.add_argument(
        "--hw_version",
        default="NA",
        help="DUT Hardware version.")
    parser.add_argument(
        "--serial_num",
        default="NA",
        help="DUT Serial number.")
    parser.add_argument("--model_num", default="NA", help="DUT Model Number.")

    # TODO:  Add example flag options from py-json/LANforge/add_dut.py somehow.
    parser.add_argument(
        '--dut_flag',
        help='DUT flags to add',
        default=None,
        action='append')

    parser.add_argument("--dut_notes", default="[BLANK]", help="Add Notes to Chamberview Test, may want to use --dut_notes_clear prior")
    parser.add_argument("--dut_notes_clear", help="Clear out older notes, used prior to adding new notes will set '[BLANK]'", action="store_true")

    # TODO:  Use lfcli_base for common arguments.
    parser.add_argument('--debug', help='Enable debugging', default=False, action="store_true")
    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument('--lf_logger_config_json',
                        help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    new_dut = DUT(lfmgr=args.lfmgr,
                  port=args.port,
                  dut_name=args.dut_name,
                  ssid=args.ssid,
                  sw_version=args.sw_version,
                  hw_version=args.hw_version,
                  serial_num=args.serial_num,
                  model_num=args.model_num,
                  dut_flags=args.dut_flag
                  )

    new_dut.setup()
    new_dut.add_ssids()
    if args.dut_notes_clear:
        new_dut.add_notes(dut_name=args.dut_name, text='[BLANK]')
    if args.dut_notes != '[BLANK]':
        new_dut.add_notes(dut_name=args.dut_name, text=args.dut_notes)
    new_dut.cv_test.show_text_blob(None, None, True)  # Show changes on GUI
    new_dut.cv_test.sync_cv()
    time.sleep(2)
    new_dut.cv_test.sync_cv()


if __name__ == "__main__":
    main()
