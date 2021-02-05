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
import realm
import time

class LANtoWAN(LFCliBase):
    def __init__(self, host, port, ssid, security, password, lan_port="eth2", wan_port="eth3", _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.timeout = 120
        self.lan_port = lan_port
        self.wan_port = wan_port
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, number_template_=self.prefix, mode=0, up=True, dhcp=True,
                                            debug_=False)
        self.cxProfile = realm.new_l3_cx_profile()

    def run_test(self): pass

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
        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.create(resource=1, radio="wiphy0", num_stations=3, debug=False)

    def cleanup(self): pass


def main():
    if __name__ == "__main__":
        main()