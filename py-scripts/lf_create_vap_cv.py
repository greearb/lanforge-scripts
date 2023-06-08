#!/usr/bin/env python3
"""
NAME: lf_create_vap_cv.py

PURPOSE:
    This script will create a vap using chamberview based upon a user defined frequency.

EXAMPLE:
    Use './lf_create_vap_cv.py --help' to see command line usage and options

    ./lf_create_vap_cv.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --delete_old_scenario --scenario_name "Automation" --vap_radio "wiphy0"
        --vap_freq "2437" --vap_ssid "routed-AP" --vap_passwd "something" --vap_security "wpa2" --vap_bw 20

    JSON example:
    "args": ["--mgr","localhost",
             "--port","8080",
             "--lf_user","lanforge",
             "--lf_password","lanforge",
             "--vap_radio","1.1.wiphy0",
             "--vap_freq","2437",
             "--vap_ssid","test_vap",
             "--vap_passwd","password",
             "--vap_security","wpa2",
             "--vap_upstream_port","1.1.eth1"
            ]
SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES: Functional

NOTES:
This script creates
1. Chamber view scenario for vap
2. Vap profile with given parameters

STATUS:  BETA RELEASE

VERIFIED_ON:
Working date : 16/05/2023
Build version: 5.4.6
Kernel version: 6.2.14+

LICENSE:

        Copyright 2023 Candela Technologies Inc
        License: Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README: False

"""
import subprocess
import sys
import os
import importlib
import argparse
import time
import logging
import requests

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test

create_chamberview = importlib.import_module("py-scripts.create_chamberview")
create_chamber = create_chamberview.CreateChamberview

add_profile = importlib.import_module("py-scripts.lf_add_profile")
lf_add_profile = add_profile.lf_add_profile

cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
set_port = importlib.import_module("py-json.LANforge.set_port")

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFRequest = importlib.import_module("py-json.LANforge.LFRequest")

ipvt = importlib.import_module("py-scripts.test_ip_variable_time")
IPVariableTime = ipvt.IPVariableTime

logger = logging.getLogger(__name__)


class create_vap_cv(cv_test):
    def __init__(self,
                 lfclient_host="192.168.200.36",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 vap_upstream_port="1.1.eth2",
                 vap_bw=None,
                 vap_mode=None
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        self.lfclient_host = lfclient_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_password
        self.COMMANDS = ["set_port"]
        self.desired_set_port_cmd_flags = []
        self.desired_set_port_current_flags = ["use_dhcp", "dhcp"]  # do not default down, "if_down"
        self.desired_set_port_interest_flags = ["current_flags"]  # do not default down, "ifdown"
        # set_port 1 1 NA NA NA NA NA 2147483648 NA NA NA vap0000
        self.profile_name = None
        self.vap_radio = None
        self.freq = None
        self.set_upstream = True
        self.vap_bw = vap_bw
        self.vap_mode = vap_mode

    def setup_vap(self, scenario_name="Automation", radio="wiphy0", frequency="-1", name=None, vap_ssid=None, vap_pawd="[BLANK]", vap_security=None):

        profile_flag = {"wep": "2", "wpa": "4", "wpa2": "8", "wpa3": "20", "open": None}
        mode = {"AUTO": "0", "a": "1", "aAX": "15", "abg": "4", "abgn": "5", "abgnAC": "8", "abgnAX": "12", "an": "10",
                "anAC": "9", "anAX": "14", "b": "2", "bg": "7", "bgn": "6", "bgnAC": "11", "bgnAX": "13"}
        profile = lf_add_profile(lf_mgr=self.lfclient_host,
                                 lf_port=self.lf_port,
                                 lf_user=self.lf_user,
                                 lf_passwd=self.lf_passwd,
                                 )

        # enables security(like wpa,wpa2,wpa3,wep etc..) along with DHCP_SERVER flags for vap.
        prof_flag = str(int(profile_flag[vap_security], 16) + int("1", 16))

        # for more flags please refer below
        # http://<mgr_ip>:8080/help/add_profile

        profile.add_profile(
            _antenna=None,  # Antenna count for this profile.
            _bandwidth=self.vap_bw,  # 0 (auto), 20, 40, 80 or 160
            _eap_id=None,  # EAP Identifier
            _flags_mask=None,  # Specify what flags to set.
            _freq=frequency,  # WiFi frequency to be used, 0 means default.
            _instance_count=1,  # Number of devices (stations, vdevs, etc)
            _mac_pattern=None,  # Optional MAC-Address pattern, for instance: xx:xx:xx:*:*:xx
            _name=scenario_name,  # Profile Name. [R]
            _passwd=vap_pawd,  # WiFi Password to be used (AP Mode), [BLANK] means no password.
            _profile_flags=prof_flag,  # Flags for this profile, see above.
            _profile_type="routed_ap",  # Profile type: See above. [W]
            _ssid=vap_ssid,  # WiFi SSID to be used, [BLANK] means any.
            _vid=None,  # Vlan-ID (only valid for vlan profiles).
            _wifi_mode=mode[str(self.vap_mode)]  # WiFi Mode for this profile.
        )

    def setup_chamberview(self, delete_scenario=True,
                          scenario_name="Automation",
                          vap_radio="wiphy1",
                          vap_upstream_port="1.1.eth2",
                          profile_name=None,
                          freq=-1,
                          line=None):

        self.profile_name = profile_name
        self.vap_radio = vap_radio
        self.freq = freq

        chamber = create_chamber(lfmgr=self.lfclient_host,
                                 port=self.lf_port)

        if delete_scenario:
            chamber.clean_cv_scenario(
                cv_type="Network-Connectivity",
                scenario_name=scenario_name)
        # TODO

        vap_shelf, vap_resource, vap_radio_name, *nil = LFUtils.name_to_eid(vap_radio)
        upstream_shelf, upstream_resource, upstream_name, *nil = LFUtils.name_to_eid(vap_upstream_port)
        if self.set_upstream:
            # TODO VAP needs to have ability to enable dhcp on the vap as compared to the upstream port.
            self.raw_line_l1 = [[f'profile_link {vap_shelf}.{vap_resource} {self.profile_name} 1 NA NA {vap_radio_name},AUTO {self.freq} NA'],
                                [f'resource {vap_shelf}.{vap_resource}.0 0'],
                                [f'profile_link {upstream_shelf}.{upstream_resource} upstream-dhcp 1 NA NA {upstream_name},AUTO -1 NA']]
        else:
            self.raw_line_l1 = [[f'profile_link 1.1 {self.profile_name} 1 NA NA {self.vap_radio},AUTO {self.freq} NA'],
                                ["resource 1.1.0 0"]]

        logger.info(self.raw_line_l1)

        chamber.setup(create_scenario=scenario_name,
                      line=line,
                      raw_line=self.raw_line_l1)

        return chamber

    def build_chamberview(self, chamber, scenario_name):
        chamber.build(scenario_name)        # self.apply_and_build_scenario("Sushant1")

    def build_and_setup_vap(self, args, delete_old_scenario=True, scenario_name="Automation", radio="wiphy0", vap_upstream_port="1.1.eth2",
                            frequency=-1, vap_ssid=None, vap_pawd="[BLANK]", vap_security=None):
        self.setup_vap(scenario_name=scenario_name,
                       radio=radio,
                       frequency=frequency,
                       name=scenario_name,
                       vap_ssid=vap_ssid,
                       vap_pawd=vap_pawd,
                       vap_security=vap_security)

        chamber = self.setup_chamberview(delete_scenario=delete_old_scenario,
                                         scenario_name=scenario_name,
                                         vap_radio=radio,
                                         vap_upstream_port=vap_upstream_port,
                                         profile_name=scenario_name,
                                         freq=frequency,
                                         line=None)

        self.build_chamberview(chamber=chamber, scenario_name=scenario_name)
        c = args.vap_radio.split(".")
        m = requests.get("http://" + self.lfclient_host + ":" + str(self.lf_port) + "/port/all")
        n = m.json()
        for i in n["interfaces"]:
            for a, b in i.items():
                if c[2] in b["parent dev"]:
                    if "vap" in b["alias"]:
                        vap = c[0] + "." + c[1] + "." + b["alias"]
        self.wait_for_ip(station_list=[vap])


def main():
    parser = argparse.ArgumentParser(
        prog="lf_create_vap_cv.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""

NAME: lf_create_vap_cv.py

PURPOSE:
    This script will create a vap using chamberview based upon a user defined frequency.

EXAMPLE:
    Use './lf_create_vap_cv.py --help' to see command line usage and options

    ./lf_create_vap_cv.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --delete_old_scenario --scenario_name "Automation" --vap_radio "wiphy0"
        --vap_freq "2437" --vap_ssid "routed-AP" --vap_passwd "something" --vap_security "wpa2" --vap_bw 20

    vs_code launch.json example:
    "args": ["--mgr","localhost",
             "--port","8080",
             "--lf_user","lanforge",
             "--lf_password","lanforge",
             "--vap_radio","wiphy0",
             "--vap_freq","36",
             "--vap_ssid","test_vap",
             "--vap_passwd","password",
             "--vap_security","wpa2",
             "--vap_upstream_port","1.1.eth1"
            ]

            "args": ["--mgr","192.168.0.104",
            "--port","8080",
            "--lf_user","lanforge",
            "--lf_password","lanforge",
            "--delete_old_scenario",
            "--scenario_name","dfs",
            "--vap_radio","wiphy3",
            "--vap_freq","5660",
            "--vap_ssid","mtk7915_5g",
            "--vap_passwd","lf_mtk7915_5g",
            "--vap_security","wpa2",
            "--vap_bw","20",
            "--vap_upstream_port","1.1.eth2"
            ]

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES: Functional


NOTES:

This script creates
1. Chamber view scenario for vap
2. Vap profile with given parameters

STATUS:   BETA RELEASE

VERIFIED_ON:
Working date : 16/05/2023
Build version: 5.4.6
Kernel version: 6.2.14+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

        """)

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("--local_lf_report_dir",
                        help="--local_lf_report_dir <where to pull reports to>  default '' put where dataplane script run from",
                        default="")
    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("-dos", "--delete_old_scenario", default=True,
                        action='store_true',
                        help="To delete old scenarios (by default: True)")
    parser.add_argument("-sn", "--scenario_name", default="Automation",
                        help="Chamberview scenario name (by default: Automation")
    parser.add_argument("-vr", "--vap_radio", default="wiphy0",
                        help="vap radio name (by default: wiphy0")
    parser.add_argument("-vf", "--vap_freq", default="2437",
                        help="vap frequency (by default: 2437")
    parser.add_argument("-vs", "--vap_ssid", default="routed-AP",
                        help="vap ssid (by default: routed-AP")
    parser.add_argument("-vp", "--vap_passwd", default="something",
                        help="vap password (by default: something")
    parser.add_argument("-vse", "--vap_security", default="wpa2",
                        help="vap security like wep ,wpa, wpa2, wpa3 (by default: wpa2")
    parser.add_argument("--vap_upstream_port", default="1.1.eth2",
                        help="vap upstream_port (by default: 1.1.eth2")
    parser.add_argument("--vap_bw", type=str, default=None, help="vap bw like 20, 40, 80, 160(by default: None")
    parser.add_argument("--vap_mode", type=str, default="AUTO",
                        help="vap mode can be selected from these"
                             '"AUTO", "a", "aAX", "abg", "abgn", "abgnAC", "abgnAX", "an","anAC", "anAX", "b", "bg", "bgn", "bgnAC"", "bgnAX"')

    args = parser.parse_args()
    cv_base_adjust_parser(args)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)


    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    lf_create_vap_cv = create_vap_cv(lfclient_host=args.mgr, lf_port=args.port, lf_user=args.lf_user,
                                     lf_password=args.lf_password, vap_upstream_port=args.vap_upstream_port,
                                     vap_bw=args.vap_bw, vap_mode=args.vap_mode)

    delete_old_scenario = args.delete_old_scenario
    vap_scenario_name = args.scenario_name
    vap_radio = args.vap_radio
    vap_upstream_port = args.vap_upstream_port
    vap_freq = args.vap_freq
    vap_ssid = args.vap_ssid
    vap_passwd = args.vap_passwd
    vap_security = args.vap_security

    lf_create_vap_cv.build_and_setup_vap(args, delete_old_scenario=delete_old_scenario, scenario_name=vap_scenario_name, radio=vap_radio,
                                         vap_upstream_port=vap_upstream_port, frequency=vap_freq, vap_ssid=vap_ssid, vap_pawd=vap_passwd, vap_security=vap_security)


if __name__ == "__main__":
    main()
