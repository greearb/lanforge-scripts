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


class IPv4Test(LFCliBase):
    def __init__(self, host, port, ssid, security, password, num_stations, prefix="00000", _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.timeout = 120
        self.prefix = prefix
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, prefix=self.prefix, mode=0, up=True, dhcp=True,
                                            debug_=False)

    def run_test(self, sta_list, print_pass=False, print_fail=False):
        for sta_name in sta_list:
            sta_status = super().json_get("port/1/1/" + sta_name)
            if sta_status['interface']['ap'] == '' or len(sta_status['interface']['ap']) != 18 and \
                    sta_status['interface']['ap'][-3] != ':':
                self._fail("%s failed to associate" % sta_name, print_fail)
            elif sta_status['interface']['ip'] == "0.0.0.0":
                self._fail("%s failed to get ip" % sta_name, print_fail)
            else:
                self._pass("%s associated with ip" % sta_name, print_pass)

    def cleanup(self):
        port_list = self.local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            # print(list(item))
            if "sta" in list(item)[0]:
                sta_list.append(self.local_realm.name_to_eid(list(item)[0])[2])

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
        print("Cleaning up old stations")
        self.cleanup()
        sta_list = []

        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.set_prefix(self.prefix)
        self.profile.create(resource=1, radio="wiphy0", num_stations=self.num_stations)
        for sta_name in list(self.local_realm.find_ports_like("sta[%s..%s]" % (self.prefix[:-1], str(self.prefix[:-2]) + str(self.num_stations - 1)))):
            sta_list.append(self.local_realm.name_to_eid(sta_name)[2])
        print(sta_list)
        time.sleep(self.timeout)
        self.run_test(sta_list, True, True)
        print("Cleaning up")
        self.cleanup()


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    ip_test = IPv4Test(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                       security="open", num_stations=5)
    ip_test.timeout = 120
    ip_test.run()


if __name__ == "__main__":
    main()
