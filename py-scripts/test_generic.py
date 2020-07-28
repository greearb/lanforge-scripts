#!/usr/bin/env python3

import sys
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
import time
import datetime


class GenTest(LFCliBase):
    def __init__(self, host, port, ssid, security, password, sta_list, name_prefix, resource=1,
                 number_template="00000", test_duration="5m", type="lfping", dest="127.0.0.1",
                 interval=1,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.number_template = number_template
        self.resource = resource
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.cx_profile = self.local_realm.new_generic_cx_profile()

        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0

        self.cx_profile.type = type
        self.cx_profile.dest = dest
        self.cx_profile.interval = interval

    def start(self, print_pass=False, print_fail=False):
        self.station_profile.admin_up(self.resource)
        temp_stas = self.sta_list.copy()
        temp_stas.append("eth1")
        self.local_realm.wait_for_ip(self.resource, temp_stas)
        cur_time = datetime.datetime.now()
        passes = 0
        expected_passes = 0
        self.cx_profile.start_cx()
        time.sleep(15)
        end_time = self.local_realm.parse_time("30s") + cur_time
        print("Starting Test...")
        while cur_time < end_time:
            cur_time = datetime.datetime.now()
            gen_results = self.json_get("generic/list?fields=name,last+results", debug_=self.debug)
            if gen_results['endpoints'] is not None:
                for name in gen_results['endpoints']:
                    for k, v in name.items():
                        if v['name'] in self.cx_profile.created_endp and not v['name'].endswith('1'):
                            expected_passes += 1
                            if v['last results'] != "" and "Unreachable" not in v['last results']:
                                passes += 1
                            else:
                                self._fail("%s Failed to ping %s " % (v['name'], self.cx_profile.dest), print_fail)
                                break
            # print(cur_time)
            # print(end_time)
            time.sleep(1)

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)


    def stop(self):
        self.cx_profile.stop_cx()
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            self.json_post(url, data)

    def build(self):
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        temp_sta_list = []
        for station in range(len(self.sta_list)):
            temp_sta_list.append(str(self.resource) + "." + self.sta_list[station])
        self.station_profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)
        self.cx_profile.create(ports=temp_sta_list, sleep_time=.5)
        self._pass("PASS: Station build finished")

    def cleanup(self, sta_list):
        self.cx_profile.cleanup()
        self.station_profile.cleanup(self.resource, sta_list)
        LFUtils.wait_until_ports_disappear(resource_id=self.resource, base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)
    generic_test = GenTest(lfjson_host, lfjson_port, number_template="00", sta_list=station_list,
                           name_prefix="var_time", type="lfping", dest="10.40.0.1", interval=1,
                           ssid="jedway-wpa2-x2048-4-4",
                           password="jedway-wpa2-x2048-4-4",
                           resource=1,
                           security="wpa2", test_duration="5m", )

    generic_test.cleanup(station_list)
    generic_test.build()
    if not generic_test.passes():
        print(generic_test.get_fail_message())
        exit(1)
    generic_test.start()
    if not generic_test.passes():
        print(generic_test.get_fail_message())
        exit(1)
    generic_test.stop()
    time.sleep(30)
    generic_test.cleanup(station_list)
    if generic_test.passes():
        print("Full test passed, all connections increased rx bytes")



if __name__ == "__main__":
    main()
