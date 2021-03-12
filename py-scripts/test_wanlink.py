#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from realm import Realm
import time

class LANtoWAN(Realm):
    def __init__(self, host, port, ssid, security, password,
                 lan_port="eth2",
                 wan_port="eth3",
                 prefix='sta',
                 number_template="00000",
                 radio="wiphy0",
                 sta_list = [],
                 side_a_min_rate=56, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 upstream = None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port)
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.radio = radio
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.timeout = 120
        self.lan_port = lan_port
        self.wan_port = wan_port
        self.prefix = prefix
        self.number_template = number_template
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()


        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def create_wanlinks(self, shelf=1, resource=1, latency=20, max_rate=1544000):
        print("Creating wanlinks")
        # create redirects for wanlink
        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rdd0",
            "peer_ifname": "rdd1"
        }
        self.json_post(url, data)

        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        self.json_post(url, data)
        time.sleep(.05)

        # create wanlink endpoints
        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan0",
            "shelf": shelf,
            "resource": resource,
            "port": "rdd0",
            "latency": latency,
            "max_rate": max_rate
        }
        self.json_post(url, data)

        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan1",
            "shelf": shelf,
            "resource": resource,
            "port": "rdd1",
            "latency": latency,
            "max_rate": max_rate
        }
        self.json_post(url, data)
        time.sleep(.05)

    def run(self):
        self.cx_profile.use_wpa2(True, self.ssid, self.password)
        self.station_profile.create(radio="wiphy0", num_stations=3, debug=False)

    def cleanup(self): pass


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='test_wanlink.py',
        formatter_class=argparse.RawTextHelpFormatter)
    for group in parser._action_groups:
        if group.title == "required arguments":
            required_args=group
            break
    #if required_args is not None:

    optional_args=None
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    if optional_args is not None:
        optional_args.add_argument('--lanport', help='Select the port you want for lanport', default='wiphy0')
        optional_args.add_argument('--wanport', help='Select the port you want for wanport', default='wiphy1')
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    #if optional_args is not None:
    args = parser.parse_args()
    num_sta=4
    station_list = portNameSeries(prefix_="sta", start_id_=0, end_id_=num_sta - 1, padding_number_=10000,
                                          radio=args.radio)
    ltw=LANtoWAN(host=args.mgr,
                 port=args.mgr_port,
                 ssid=args.ssid,
                 sta_list=station_list,
                 security=args.security,
                 password=args.passwd,
                 lan_port=args.lanport,
                 wan_port=args.wanport)
    ltw.create_wanlinks()
    ltw.run()
    ltw.cleanup()

if __name__ == "__main__":
    main()