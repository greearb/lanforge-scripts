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

    def __set_all_cx_state(self, state, sleep_time=5):
        print("Setting CX States to %s" % state)
        cx_list = list(self.local_realm.cx_list())
        for cx_name in cx_list:
            if cx_name != 'handler' or cx_name != 'uri':
                req_url  = "cli-json/set_cx_state"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": cx_name,
                    "cx_state": state
                }

                super().json_post(req_url, data)
        time.sleep(sleep_time)

    def run_test(self):
        cur_time = datetime.datetime.now()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.__set_all_cx_state("RUNNING")
        while cur_time < end_time:
            #print(cur_time, end_time)
            cur_time = datetime.datetime.now()
            # Run test
            time.sleep(1)
        self.__set_all_cx_state("STOPPED")

    def cleanup(self):
        print("Cleaning up stations")
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

        cx_list = list(self.local_realm.cx_list())
        print("Cleaning up cxs")
        for cx_name in cx_list:
            if cx_name != 'handler' or cx_name != 'uri':
                req_url = "cli-json/rm_cx"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": cx_name
                }
                super().json_post(req_url, data)

        print("Cleaning up endps")
        endp_list = super().json_get("/endp")
        if endp_list is not None:
            endp_list = list(endp_list['endpoint'])
            for endp_name in range(len(endp_list)):
                name = list(endp_list[endp_name])[0]
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": name
                }
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
                                   security="open", num_stations=10, test_duration="1m")
    ip_var_test.run()
    ip_var_test.run_test()
    ip_var_test.cleanup()


if __name__ == "__main__":
    main()
