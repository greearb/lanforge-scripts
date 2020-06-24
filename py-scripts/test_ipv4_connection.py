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

    def run_test_full(self, print_pass=False, print_fail=False):
        print("Testing all stations for association")
        port_list = self.local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            # print(list(item))
            if "sta" in list(item)[0]:
                sta_list.append(self.local_realm.name_to_eid(list(item)[0])[2])

        return self._run_test(sta_list, print_pass, print_fail)

    def run_test_custom(self, range_start="000", range_end="000", sta_list=[], print_pass=False, print_fail=False):
        if len(sta_list) == 0:
            print("Testing range of stations from sta%s to sta%s" % (range_start, range_end))
            if range_start != "000" and range_end != "000":
                found_stations = self.local_realm.find_ports_like("sta[%s..%s]" % (range_start, range_end))
                for sta_name in list(found_stations):
                    sta_list.append(self.local_realm.name_to_eid(sta_name)[2])
            else:
                raise ValueError("range_start and range_end not specified")
        else:
            print("Testing stations in specified list")
        return self._run_test(sta_list, print_pass, print_fail)

    def _run_test(self, sta_list, print_pass, print_fail):
        for sec in range(self.timeout):
            associated_map = []
            ip_map = []
            for sta_name in sta_list:
                sta_status = super().json_get("port/1/1/" + sta_name)
                # print(sta_status)
                if len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':' \
                        and sta_status['interface']['ip'] == '0.0.0.0':

                    # print("Associated", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map.append(sta_name)

                elif len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':' \
                        and sta_status['interface']['ip'] != '0.0.0.0':

                    # print("IP", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map.append(sta_name)
                    ip_map.append(sta_name)


            time.sleep(1)
        # print(len(sta_list), sta_list)
        # print(len(ip_map), ip_map)
        # print(len(associated_map), associated_map)
        if len(sta_list) == len(ip_map) and len(sta_list) == len(associated_map):
            self._pass("PASS: All stations associated with IP", print_pass)
        else:
            self._fail("FAIL: Not all stations able to associate/get IP", print_fail)

        return self.passes()

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
        print("Creating stations")
        self.profile.create(resource=1, radio="wiphy0", num_stations=self.num_stations, debug=False)

        for sta_name in list(self.local_realm.find_ports_like("sta[%s..%s]" % (
                self.prefix, str(self.prefix[:-len(str(self.num_stations))]) + str(self.num_stations - 1)))):
            sta_list.append(self.local_realm.name_to_eid(sta_name)[2])


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    ip_test = IPv4Test(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                       security="open", num_stations=10)
    ip_test.cleanup()
    ip_test.timeout = 60
    ip_test.run()
    print("Full Test Passed: %s" % ip_test.run_test_full())
    print("Range Test Passed: %s" % ip_test.run_test_custom("00005", "00009"))
    print("Custom Test Passed: %s" % ip_test.run_test_custom(sta_list=["sta00001", "sta00003", "sta00009", "sta00002"]))

    ip_test.cleanup()


if __name__ == "__main__":
    main()
