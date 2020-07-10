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
from LANforge import LFUtils
import realm
import time
import datetime


class IPV4L4(LFCliBase):
    def __init__(self, host, port, ssid, security, password, url, requests_per_ten, station_list, prefix="00000",
                 resource=1,
                 test_duration="5m",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.url = url
        self.requests_per_ten = requests_per_ten
        self.prefix = prefix
        self.sta_list = station_list
        self.resource = resource
        self.test_duration = test_duration

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, number_template_=self.prefix, mode=0, up=False,
                                            dhcp=True,
                                            debug_=False, local_realm=self.local_realm)
        self.cx_profile = realm.L4CXProfile(lfclient_host=self.host, lfclient_port=self.port,
                                            local_realm=self.local_realm, debug_=False)
        self.cx_profile.url = self.url
        self.cx_profile.requests_per_ten = self.requests_per_ten

    def __set_all_cx_state(self, state, sleep_time=5):
        print("Setting CX States to %s" % state)
        for sta_name in self.sta_list:
            req_url = "cli-json/set_cx_state"
            data = {
                "test_mgr": "default_tm",
                "cx_name": "CX_" + sta_name + "_l4",
                "cx_state": state
            }
            self.json_post(req_url, data)
        time.sleep(sleep_time)

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes += 1
                if new_list[item] > old_list[item]:
                    passes += 1
                #print(item, new_list[item], old_list[item], passes, expected_passes)

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            return False

    def __get_values(self):
        cx_list = self.json_get("layer4/list?fields=name,bytes-rd", debug_=self.debug)
        # print("==============\n", cx_list, "\n==============")
        cx_map = {}
        for cx_name in cx_list['endpoint']:
            if cx_name != 'uri' and cx_name != 'handler':
                for item, value in cx_name.items():
                    for value_name, value_rx in value.items():
                        if value_name == 'bytes-rd':
                            cx_map[item] = value_rx
        return cx_map

    def build(self):
        # Build stations
        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.set_number_template(self.prefix)
        print("Creating stations")
        self.profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.profile.set_command_param("set_port", "report_timer", 1500)
        self.profile.set_command_flag("set_port", "rpt_timer", 1)
        self.profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=self.debug)
        self._pass("PASS: Station build finished")
        temp_sta_list = []
        for station in range(len(self.sta_list)):
            temp_sta_list.append(str(self.resource) + "." + self.sta_list[station])

        self.cx_profile.create(ports=temp_sta_list, sleep_time=.5, debug_=self.debug, suppress_related_commands_=None)

    def start(self, print_pass=False, print_fail=False):
        cur_time = datetime.datetime.now()
        old_rx_values = self.__get_values()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.profile.admin_up(1)
        self.local_realm.wait_for_ip()
        self.cx_profile.start_cx()
        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_rx_values = self.__get_values()
            # print(old_rx_values, new_rx_values)
            # print("\n-----------------------------------")
            # print(cur_time, end_time, cur_time + datetime.timedelta(minutes=1))
            # print("-----------------------------------\n")
            expected_passes += 1
            if self.__compare_vals(old_rx_values, new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
                break
            old_rx_values = new_rx_values
            cur_time = datetime.datetime.now()

        # test for valid url, no 404s
        # new script; desired minimum urls for 10 min

    def stop(self):
        self.__set_all_cx_state("STOPPED")
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            self.json_post(url, data)

    def cleanup(self, sta_list):
        self.profile.cleanup(self.resource, sta_list)
        self.cx_profile.cleanup()
        LFUtils.wait_until_ports_disappear(resource_id=self.resource, base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000)
    ip_test = IPV4L4(lfjson_host, lfjson_port, ssid="jedway-wpa2-x2048-4-4", password="jedway-wpa2-x2048-4-4",
                     security="open", station_list=station_list, url="dl http://10.40.0.1 /dev/null", test_duration="5m",
                     requests_per_ten=600)
    ip_test.cleanup(station_list)
    ip_test.build()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        exit(1)
    ip_test.start(False, False)
    ip_test.stop()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        exit(1)
    time.sleep(30)
    ip_test.cleanup(station_list)
    if ip_test.passes():
        print("Full test passed, all endpoints had increased bytes-rd throughout test duration")


if __name__ == "__main__":
    main()
