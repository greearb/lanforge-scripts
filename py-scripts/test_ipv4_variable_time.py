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
import datetime


class IPV4VariableTime(LFCliBase):
    def __init__(self, host, port, ssid, security, password, num_stations, prefix="00000", test_duration="5m",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.prefix = prefix
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                                    security=self.security, prefix=self.prefix, mode=0, up=True,
                                                    dhcp=True,
                                                    debug_=False)
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.test_duration = test_duration

    def run_test(self):
        cur_time = datetime.datetime.now()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        while cur_time != end_time:
            cur_time = datetime.datetime.now()
            # Run test
            time.sleep(1)

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

        self.station_profile.use_wpa2(True, self.ssid, self.password)
        self.station_profile.set_prefix(self.prefix)
        print("Creating stations")
        self.station_profile.create(resource=1, radio="wiphy0", num_stations=self.num_stations, debug=False)

        for name in list(self.local_realm.station_list()):
            if "sta" in list(name)[0]:
                sta_list.append(list(name)[0])

        print("sta_list", sta_list)
        self.cx_profile.create(endp_type="lf_udp", side_a=sta_list, side_b="1.eth1", sleep_time=.5)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    ip_var_test = IPV4VariableTime(lfjson_host, lfjson_port, prefix="00", ssid="jedway-wpa2-x2048-4-4",
                                   password="jedway-wpa2-x2048-4-4",
                                   security="open", num_stations=1)
    ip_var_test.run()
    ip_var_test.cleanup()


if __name__ == "__main__":
    main()
