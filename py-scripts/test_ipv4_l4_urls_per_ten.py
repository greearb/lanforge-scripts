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
    def __init__(self, host, port, ssid, security, password, url, requests_per_ten, station_list,
                 target_requests_per_ten=600, prefix="00000", resource=1, num_tests=1,
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
        self.num_tests = num_tests
        self.target_requests_per_ten = target_requests_per_ten

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

    def __check_request_rate(self):
        endp_list = self.json_get("layer4/list?fields=urls/s")
        expected_passes = 0
        passes = 0
        if endp_list is not None and endp_list['endpoint'] is not None:
            endp_list = endp_list['endpoint']
            for item in endp_list:
                expected_passes += 1
                for name, info in item.items():
                    if info['urls/s'] * 600 > 600 * .9:
                        passes += 1

        return passes == expected_passes

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
        print("Starting test")
        cur_time = datetime.datetime.now()
        interval_time = cur_time + datetime.timedelta(minutes=10)
        passes = 0
        expected_passes = 0
        self.profile.admin_up(1)
        self.local_realm.wait_for_ip()
        self.cx_profile.start_cx()
        for test in range(self.num_tests):
            expected_passes += 1
            while cur_time < interval_time:
                time.sleep(1)
                cur_time = datetime.datetime.now()

            if self.cx_profile.check_errors(self.debug):
                if self.__check_request_rate():
                    passes += 1
                else:
                    self._fail("FAIL: Request rate did not exceed 90% target rate", print_fail)
                    break
            else:
                self._fail("FAIL: Errors found getting to %s " % self.url, print_fail)
                break
            interval_time = cur_time + datetime.timedelta(minutes=10)
        if passes == expected_passes:
            self._pass("PASS: All tests passes", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
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
                     security="open", station_list=station_list, url="dl http://10.40.0.1 /dev/null", num_tests=1,
                     target_requests_per_ten=600,
                     requests_per_ten=600)
    ip_test.local_realm.remove_all_stations(ip_test.resource)
    ip_test.local_realm.remove_all_cxs()
    ip_test.local_realm.remove_all_endps()
    ip_test.build()
    ip_test.start()
    ip_test.stop()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        exit(1)
    time.sleep(30)
    ip_test.cleanup(station_list)
    if ip_test.passes():
        print("Full test passed, all endpoints met or exceeded 90% of the target rate")


if __name__ == "__main__":
    main()
