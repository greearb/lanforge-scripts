#!/usr/bin/env python3
"""
NAME: lf_create_vap_cv.py

PURPOSE:
    This script will create a vap using chamberview based upon a user defined frequency.

EXAMPLE:
    Use './lf_create_vap_cv.py --help' to see command line usage and options

    ./lf_create_vap_cv.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
        --delete_old_scenario --scenario_name Automation --vap_radio wiphy0 --set_upstream True
        --vap_freq 2437 --vap_ssid routed-AP --vap_passwd something --vap_security wpa2 --vap_bw 20

    # For modify the net-smith dhcp min and max range
    python3 ./lf_create_vap_cv.py --mgr 192.168.200.138 --port 8080 --delete_old_scenario --scenario_name hello
    --vap_radio 1.1.wiphy0 --vap_freq 2437 --vap_ssid testings --vap_passwd Password@123 --vap_security wpa2 --num_vaps 2
    --vap_bw 20 --vap_ip 192.168.0.16 --vap_ip_mask 255.255.0.0 --dhcp_min_range 192.168.0.5 --dhcp_max_range 192.168.0.200 

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

    # for loading existing scenario use
    python3 ./lf_create_vap_cv.py --mgr 192.168.200.222 --port 8080  --load_existing_scenario --old_scenario_name hello --instance_name oldscenario

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES: Functional


NOTES:

This script creates
1. Chamber view scenario for vap
2. Vap profile with given parameters

STATUS:   BETA RELEASE

VERIFIED_ON:
Working date : 05-July-2023
Build version: 5.4.6
Kernel version: 6.2.16+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

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

radio_modify = importlib.import_module("py-scripts.lf_modify_radio")

logger = logging.getLogger(__name__)


class create_vap_cv(cv_test):
    def __init__(self,
                 lfclient_host="192.168.200.36",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 vap_upstream_port="1.1.eth2",
                 vap_ip=None,
                 vap_ip_mask=None,
                 gateway_ip=None,
                 vap_bw=None,
                 vap_mode=None,
                 set_upstream=None,
                 old_scenario_name=None,
                 instance_name=None
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
        self.old_scenario_name = old_scenario_name
        self.instance_name = instance_name
        # set_port 1 1 NA NA NA NA NA 2147483648 NA NA NA vap0000
        self.lf_modify_radio = radio_modify.lf_modify_radio(lf_mgr=lfclient_host,
                                                            lf_port=lf_port,
                                                            lf_user=lf_user,
                                                            lf_passwd=lf_password,
                                                            debug=False,
                                                            static_ip=vap_ip,
                                                            ip_mask = vap_ip_mask,
                                                            gateway_ip=gateway_ip)
        self.profile_name = None
        self.vap_radio = None
        self.freq = None
        self.set_upstream = set_upstream
        self.vap_bw = vap_bw
        self.vap_mode = vap_mode
        self.vaps_list= []

    def remove_profile(self,scenario_name="Automation"):
        post_data = {"name":scenario_name}
        post_url = "http://{}:{}/cli-json/rm_profile".format(self.lfclient_host,self.lf_port)
        profile_data = requests.get(url="http://{}:{}/profile/all".format(self.lfclient_host,self.lf_port))
        data = profile_data.json()
        for profile in data['profiles']:
            for key,value in profile.items():
                if scenario_name in value['name']:
                    requests.post(url=post_url,json=post_data)
                else:
                    logger.info("No existing profile with given scenario name {}".format(scenario_name))
            break
        
    def setup_vap(self, scenario_name="Automation", radio="wiphy0", frequency="-1", name=None, vap_ssid=None, vap_pawd="[BLANK]", vap_security=None):

        profile_flag = {"wep": "2", "wpa": "4", "wpa2": "8", "wpa3": "20", "open": None}
        mode = {"AUTO": "0", "a": "1", "aAX": "15", "abg": "4", "abgn": "5", "abgnAC": "8", "abgnAX": "12", "an": "10",
                "anAC": "9", "anAX": "14", "b": "2", "bg": "7", "bgn": "6", "bgnAC": "11", "bgnAX": "13"}
        profile = lf_add_profile(lf_mgr=self.lfclient_host,
                                 lf_port=self.lf_port,
                                 lf_user=self.lf_user,
                                 lf_passwd=self.lf_passwd,
                                 )
        
        if vap_security == "open":
            prof_flag = "1"
        else:
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
                          amount=1,
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
        if self.set_upstream == "True":
            # TODO VAP needs to have ability to enable dhcp on the vap as compared to the upstream port.
            self.raw_line_l1 = [[f'profile_link {vap_shelf}.{vap_resource} {self.profile_name} {amount} NA NA {vap_radio_name},AUTO {self.freq} NA'],
                                [f'resource {vap_shelf}.{vap_resource}.0 0'],
                                [f'profile_link {upstream_shelf}.{upstream_resource} upstream-dhcp 1 NA NA {upstream_name},AUTO -1 NA']]
        else:
            self.raw_line_l1 = [[f'profile_link {vap_shelf}.{vap_resource} {self.profile_name} {amount} NA NA {vap_radio_name},AUTO {self.freq} NA'],
                                [f'resource {vap_shelf}.{vap_resource}.0 0']]

        logger.info(self.raw_line_l1)

        chamber.setup(create_scenario=scenario_name,
                      line=line,
                      raw_line=self.raw_line_l1)

        return chamber

    def build_chamberview(self, chamber, scenario_name):
        chamber.build(scenario_name)        # self.apply_and_build_scenario("Sushant1")

    def build_and_setup_vap(self,delete_old_scenario=True, scenario_name="Automation", radio="wiphy0", vap_upstream_port="1.1.eth2",
                            frequency=-1, amount=1, vap_ssid=None, vap_pawd="[BLANK]", vap_security=None):
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
                                         amount=amount,
                                         line=None)

        self.build_chamberview(chamber=chamber, scenario_name=scenario_name)
        self.vaps_list=list(self.vap_list()[0].keys())
        self.wait_for_ip(station_list=self.vaps_list)

    def modify_vr_cfg(self, dhcp_min="", dhcp_max=""):  # modify & apply the net-smith vr(virtual router) config settings
        logger.info("Modifying Netsmith Connection...")
        vaps_list = list(self.vap_list()[0].keys())
        self.vaps_list = vaps_list[0].split('.')
        self.lf_modify_radio.disable_dhcp_static(interface=vaps_list[0])
        cv_test.add_vrcx_(self, resource=self.vaps_list[1], vr_name="Router-0", local_dev=self.vaps_list[2],
                          dhcp_min=dhcp_min, dhcp_max=dhcp_max)  # enabling dhcp min & max values
        cv_test.netsmith_apply(self, resource=self.vaps_list[1])  # applying net-smith config

    # load existing scenarios
    def load_old_scenario(self):
        self.load_test_scenario(instance=self.instance_name, scenario=self.old_scenario_name)
        self.apply_cv_scenario(cv_scenario=self.old_scenario_name)  # Apply scenario
        self.build_cv_scenario()


def main():
    help_summary = '''\
    Theis script is designed to create a Virtual Access point (VAP)
    using Chamber view scenario. Through this script, dhcp min, max ranges can be set to the vap and can modify
    vap ip address, vap ip mask, gateway, vap mode, vap bandwidth, vap frequency, security.
    Any existing scenario can be loaded or deleted by providing respective arguments.
    '''
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
        --delete_old_scenario --scenario_name Automation --vap_radio wiphy0 --set_upstream True
        --vap_freq 2437 --vap_ssid routed-AP --vap_passwd something --vap_security wpa2 --vap_bw 20
        
    # For modify the net-smith dhcp min and max range
    python3 ./lf_create_vap_cv.py --mgr 192.168.200.138 --port 8080 --delete_old_scenario --scenario_name hello 
    --vap_radio 1.1.wiphy0 --vap_freq 2437 --vap_ssid testings --vap_passwd Password@123 --vap_security wpa2 --num_vaps 2
    --vap_bw 20 --vap_ip 192.168.0.16 --vap_ip_mask 255.255.0.0 --dhcp_min_range 192.168.0.5 --dhcp_max_range 192.168.0.200 

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
Working date : 05-July-2023
Build version: 5.4.6
Kernel version: 6.2.16+

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
    parser.add_argument("-vp", "--vap_passwd", default=None,
                        help="vap password (by default:None")
    parser.add_argument("-vse", "--vap_security", default="wpa2",
                        help="vap security like wep ,wpa, wpa2, wpa3 (by default: wpa2")
    parser.add_argument("--vap_upstream_port", default="1.1.eth2",
                        help="vap upstream_port (by default: 1.1.eth2")
    parser.add_argument("--num_vaps", default= 1,
                        type=int , help="enter the number of vaps need to be created (by default : 1)")
    parser.add_argument("--vap_bw", type=str, default=None, help="vap bw like 20, 40, 80, 160(by default: None")
    parser.add_argument("--vap_mode", type=str, default="AUTO",
                        help="vap mode can be selected from these"
                             '"AUTO", "a", "aAX", "abg", "abgn", "abgnAC", "abgnAX", "an","anAC", "anAX", "b", "bg", "bgn", "bgnAC"", "bgnAX"')
    parser.add_argument("--set_upstream", default= True, help="Enter True if upstream need to be set else enter False")
    parser.add_argument("--vap_ip", help='Modify the VAP DHCP ip address', default=None)
    parser.add_argument("--vap_ip_mask", help='Modify the VAP ip mask', default=None)
    parser.add_argument("--gateway", help="Modify the VAP Gateway ip")
    parser.add_argument("--dhcp_min_range", help='Modify the VAP DHCP min range', default=None)
    parser.add_argument("--dhcp_max_range", help='Modify the VAP DHCP max range', default=None)
    parser.add_argument("--load_existing_scenario",  default=False,
                        action='store_true', help="select if you want to load existing scenario")
    parser.add_argument("--old_scenario_name", help="provide old scenario name to be loaded")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

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
                                     vap_ip=args.vap_ip, vap_ip_mask=args.vap_ip_mask, gateway_ip=args.gateway,
                                     vap_bw=args.vap_bw, vap_mode=args.vap_mode,set_upstream=args.set_upstream,
                                     old_scenario_name=args.old_scenario_name, instance_name=args.instance_name)

    delete_old_scenario = args.delete_old_scenario
    vap_scenario_name = args.scenario_name
    vap_radio = args.vap_radio
    vap_upstream_port = args.vap_upstream_port
    vap_freq = args.vap_freq
    vap_ssid = args.vap_ssid
    vap_passwd = args.vap_passwd
    vap_security = args.vap_security
    if args.load_existing_scenario is True:
        lf_create_vap_cv.load_old_scenario()
    else:
        lf_create_vap_cv.remove_profile(scenario_name=vap_scenario_name)
        lf_create_vap_cv.build_and_setup_vap(delete_old_scenario=delete_old_scenario, scenario_name=vap_scenario_name, radio=vap_radio,amount=args.num_vaps,
                                             vap_upstream_port=vap_upstream_port, frequency=vap_freq, vap_ssid=vap_ssid, vap_pawd=vap_passwd, vap_security=vap_security)
        if args.dhcp_min_range and args.dhcp_max_range:
            lf_create_vap_cv.modify_vr_cfg(dhcp_min=args.dhcp_min_range, dhcp_max=args.dhcp_max_range)


if __name__ == "__main__":
    main()