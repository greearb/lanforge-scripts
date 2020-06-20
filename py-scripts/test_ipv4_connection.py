#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge import LFUtils
# from LANforge import LFCliBase
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
import time

class IPv4Test(LFCliBase):
    def __init__(self, host, port, ssid, security, password, num_stations, _debug_on=False, _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.timeout = 120

    def run_test(self, sta_list, print_pass=False, print_fail=False):
        for sta_name in sta_list:
            sta_status = super().json_get("port/1/1/" + sta_name)
            if len(sta_status['interface']['ap']) != 18 and sta_status['interface']['ap'][-3] != ':':
                self._fail("%s failed to associate" % sta_name, print_fail)
            elif sta_status['interface']['ip'] == "0.0.0.0":
                self._fail("%s failed to get ip" % sta_name, print_fail)
            else:
                self._pass("%s associated with ip" % sta_name, print_pass)

    def cleanup(self, sta_list):
        print("Cleaning up %s " % sta_list)
        for sta_name in sta_list:
            req_url = "cli-json/rm_vlan"
            data = {
                "shelf": 1,
                "resource": 1,
                "port": sta_name
            }
            # print(data)
            super().json_post(req_url, data)

    def run(self):
        super().clear_test_results()
        local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                             security=self.security, prefix="00000", mode=0, up=True, dhcp=True,
                                             debug_=False)
        profile.use_wpa2(True, self.ssid, self.password)
        profile.set_prefix("000")
        profile.create(resource = 1, radio = "wiphy0", num_stations = self.num_stations)
        port_list = local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            if "sta" in item:
                sta_list.append(local_realm.name_to_eid(item)[2])

        for sec in range(self.timeout):
            self.run_test(sta_list, True, True)
            time.sleep(1)
        self.cleanup(sta_list)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    ip_test = IPv4Test(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                       security="open", num_stations=5)
    ip_test.timeout = 120
    ip_test.run()

if __name__ == "__main__":
    main()