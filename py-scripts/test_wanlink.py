#!/usr/bin/env python3
# Create and modify WAN Links from the command line.
# Written by Candela Technologies Inc.
# Updated by: Erin Grimes
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
import create_wanlink

class LANtoWAN(Realm):
    def __init__(self, args):
        super().__init__(args['host'], args['port'])
        self.args = args
        self.lan_port="eth2"
        self.wan_port="eth3"
        # self.prefix='sta'
        # self.number_template="00000"
        self.radio="wiphy0"
        # self.sta_list = []
        # self.side_a_min_rate=0
        # self.side_a_max_rate=56
        # self.side_b_min_rate=0
        # self.side_b_max_rate=56
        self._debug_on=False
        self._exit_on_error=False
        self._exit_on_fail=False

    def create_wanlinks(self, shelf=1, resource=1, max_rate=1544000):
        print("Creating wanlinks")
        # print("the latency is {laten}\n".format(laten=self.latency))

        # create redirects for wanlink
        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rd0a",            
            "peer_ifname": "rd1a"
        }
        self.json_post(url, data)

        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rd1a",         
            "peer_ifname": "rd0a"
        }
        self.json_post(url, data)
        time.sleep(.05)

        # create wanlink endpoints
        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan1",
            "shelf": shelf,
            "resource": resource,
            "port": "rd0a",
            "latency": self.args['latency_A'],
            "max_rate": self.args['rate_A']
        }
        self.json_post(url, data)

        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan2",
            "shelf": shelf,
            "resource": resource,
            "port": "rd1a",
            "latency": self.args['latency_B'],
            "max_rate": self.args['rate_B']
        }
        self.json_post(url, data)
        create_wanlink.main('http://'+self.args['host']+':8080', self.args)
    
    def cleanup(self): pass

def main():
    parser = LFCliBase.create_basic_argparse(
        prog='test_wanlink.py',
        formatter_class=argparse.RawTextHelpFormatter)
    for group in parser._action_groups:
        if group.title == "required arguments":
            required_args=group
            break

    optional_args=None
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    if optional_args is not None:
        # optional_args.add_argument('--lanport', help='Select the port you want for lanport', default='wiphy0')
        # optional_args.add_argument('--wanport', help='Select the port you want for wanport', default='wiphy1'
        optional_args.add_argument('--rate', help='The maximum rate of transfer at both endpoints (bits/s)', default=1000000)
        optional_args.add_argument('--rate_A', help='The max rate of transfer at endpoint A (bits/s)', default=None)
        optional_args.add_argument('--rate_B', help='The maximum rate of transfer (bits/s)', default=None)
        optional_args.add_argument('--latency', help='The delay of both ports', default=20)
        optional_args.add_argument('--latency_A', help='The delay of port A', default=None)
        optional_args.add_argument('--latency_B', help='The delay of port B', default=None)
        # todo: packet loss A and B
        # todo: jitter A and B
        for group in parser._action_groups:
            if group.title == "optional arguments":
                optional_args=group
                break
    parseargs  = parser.parse_args()
    args = {
        "host": parseargs.mgr,
        "port": parseargs.mgr_port,
        "ssid": parseargs.ssid,
        "security": parseargs.security,
        "password": parseargs.passwd,
        "latency": parseargs.latency,
        "latency_A": (parseargs.latency_A if parseargs.latency_A is not None else parseargs.latency),
        "latency_B": (parseargs.latency_B if parseargs.latency_B is not None else parseargs.latency),
        "rate": (parseargs.rate),
        "rate_A": (parseargs.rate_A if parseargs.rate_A is not None else parseargs.rate),
        "rate_B": (parseargs.rate_B if parseargs.rate_B is not None else parseargs.rate)
    }
    ltw=LANtoWAN(args)
    ltw.create_wanlinks()
    ltw.cleanup()

if __name__ == "__main__":
    main()
