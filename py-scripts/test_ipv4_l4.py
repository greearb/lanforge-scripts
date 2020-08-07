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
import argparse
import realm
import time
import datetime


class IPV4L4(LFCliBase):
    def __init__(self, host, port, ssid, security, password, url, requests_per_ten, station_list,
                 number_template="00000", radio="wiphy0",
                 test_duration="5m", upstream_port="eth1",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.radio = radio
        self.upstream_port = upstream_port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.url = url
        self.requests_per_ten = requests_per_ten
        self.number_template = number_template
        self.sta_list = station_list
        self.test_duration = test_duration

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.cx_profile = self.local_realm.new_l4_cx_profile()

        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0

        self.cx_profile.url = self.url
        self.cx_profile.requests_per_ten = self.requests_per_ten

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes += 1
                if new_list[item] > old_list[item]:
                    passes += 1
                # print(item, old_list[item], new_list[item], passes, expected_passes)

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            return False

    def __get_values(self):
        time.sleep(1)
        cx_list = self.json_get("layer4/list?fields=name,bytes-rd", debug_=self.debug)
        # print("==============\n", cx_list, "\n==============")
        cx_map = {}
        for cx_name in cx_list['endpoint']:
            if cx_name != 'uri' and cx_name != 'handler':
                for item, value in cx_name.items():
                    for value_name, value_rx in value.items():
                        if item in self.cx_profile.created_cx.keys() and value_name == 'bytes-rd':
                            cx_map[item] = value_rx
        return cx_map

    def build(self):
        # Build stations
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        self._pass("PASS: Station build finished")

        self.cx_profile.create(ports=self.station_profile.station_names, sleep_time=.5, debug_=self.debug,
                               suppress_related_commands_=None)

    def start(self, print_pass=False, print_fail=False):
        temp_stas = self.sta_list.copy()
        temp_stas.append(self.local_realm.name_to_eid(self.upstream_port)[2])
        if self.local_realm.wait_for_ip(temp_stas):
            self._pass("All stations got IPs", print_pass)
        else:
            self._fail("Stations failed to get IPs", print_fail)
            exit(1)
        cur_time = datetime.datetime.now()
        old_rx_values = self.__get_values()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.station_profile.admin_up()
        self.cx_profile.start_cx()
        passes = 0
        expected_passes = 0
        print("Starting Test...")
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
        if passes == expected_passes:
            self._pass("PASS: All tests passes", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        for sta_name in self.sta_list:
            data = LFUtils.port_down_request(1, self.local_realm.name_to_eid(sta_name)[2])
            url = "cli-json/set_port"
            self.json_post(url, data)

    def cleanup(self, sta_list):
        self.cx_profile.cleanup()
        self.station_profile.cleanup(sta_list)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = LFCliBase.create_basic_argparse(
        prog='test_generic.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Useful Information:
                1. TBD
                ''',

        description='''\
    test_generic.py:
    --------------------
    TBD

    Generic command layout:
    python ./test_ipv4_l4.py --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password> <security type: wpa2, open, wpa3> --debug

    Note:   multiple --radio switches may be entered up to the number of radios available:
                     --radio <radio 0> <stations> <ssid> <ssid password>  --radio <radio 01> <number of last station> <ssid> <ssid password>

     python3 ./test_ipv4_l4.py --upstream_port eth1 --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 wpa2 --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 wpa2

            ''')

    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="5m")
    parser.add_argument('--requests_per_ten', help='--requests_per_ten number of request per ten minutes', default=600)
    parser.add_argument('--url', help='--url specifies upload/download, address, and dest', default="dl http://10.40.0.1 /dev/null")

    args = parser.parse_args()

    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000,
                                          radio=args.radio)

    ip_test = IPV4L4(args.mgr, lfjson_port, ssid=args.ssid, password=args.passwd,
                     security=args.security, station_list=station_list, url=args.url,
                     test_duration=args.test_duration, upstream_port=args.upstream_port,
                     requests_per_ten=args.requests_per_ten, _debug_on=args.debug)
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
