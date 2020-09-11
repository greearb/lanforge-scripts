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


class IPV4FIO(LFCliBase):
    def __init__(self, host, port, ssid, security, password, station_list,
                 number_template="00000", radio="wiphy0", fio_type="fe_nfs4", min_read=0, max_read=0, min_write=10000000000,
                 max_write=0, directory="AUTO", test_duration="5m", upstream_port="eth1", server_mount="10.40.0.1:/var/tmp/test",
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
        self.number_template = number_template
        self.sta_list = station_list
        self.test_duration = test_duration

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.cx_profile = self.local_realm.new_fio_cx_profile()

        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0

        self.cx_profile.fio_type = fio_type
        self.cx_profile.min_read = min_read
        self.cx_profile.max_read = max_read
        self.cx_profile.min_write = min_write
        self.cx_profile.max_write = max_write
        self.cx_profile.directory = directory
        self.cx_profile.server_mount = server_mount

        self.ro_profile = self.cx_profile.create_ro_profile()

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        for item in old_list:
            expected_passes += 2
            if item not in new_list:
                raise ValueError("%s not found. Have the stations changed?" % item)
            else:
                if old_list[item]['bps rx'] < new_list[item]['bps rx']:
                    passes += 1
                if old_list[item]['bps tx'] < new_list[item]['bps tx']:
                    passes += 1

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            return False

    def __get_values(self):
        time.sleep(3)
        names = ""
        for name in self.station_profile.station_names:
            names += self.local_realm.name_to_eid(name)[2] + ","
        names = names[0:len(names)-1]
        cx_list = self.json_get("port/1/1/%s?fields=alias,port,bps+tx,bps+rx" % names, debug_=self.debug)
        # print("==============\n", cx_list, "\n==============")
        cx_map = {}
        if cx_list is not None:
            cx_list = cx_list['interfaces']
            for i in cx_list:
                for item, value in i.items():
                    # print(item, value)
                    cx_map[self.local_realm.name_to_eid(item)[2]] = {"bps rx": value['bps rx'], "bps tx": value['bps tx']}
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
        self.ro_profile.create(ports=self.station_profile.station_names, sleep_time=.5, debug_=self.debug,
                               suppress_related_commands_=None)


    def start(self, print_pass=False, print_fail=False):
        temp_stas = self.sta_list.copy()
        temp_stas.append(self.local_realm.name_to_eid(self.upstream_port)[2])
        self.station_profile.admin_up()
        if self.local_realm.wait_for_ip(temp_stas):
            self._pass("All stations got IPs", print_pass)
        else:
            self._fail("Stations failed to get IPs", print_fail)
            exit(1)
        cur_time = datetime.datetime.now()
        old_rx_values = self.__get_values()
        # print("Got Values")
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.cx_profile.start_cx()
        time.sleep(2)
        self.ro_profile.start_cx()
        passes = 0
        expected_passes = 0
        print("Starting Test...")
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(seconds=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_rx_values = self.__get_values()
            # exit(1)
            print(old_rx_values, new_rx_values)
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
        self.ro_profile.stop_cx()
        self.station_profile.admin_down()

    def cleanup(self, sta_list):
        self.cx_profile.cleanup()
        self.ro_profile.cleanup()
        self.station_profile.cleanup(sta_list)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list, debug=self.debug)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = LFCliBase.create_basic_argparse(
        prog='test_fileio.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Useful Information:
                1. TBD
                ''',

        description='''\
    test_fileio.py:
    --------------------
    TBD

    Generic command layout:
    python ./test_fileio.py --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password> <security type: wpa2, open, wpa3> --debug

    Note:   multiple --radio switches may be entered up to the number of radios available:
                     --radio <radio 0> <stations> <ssid> <ssid password>  --radio <radio 01> <number of last station> <ssid> <ssid password>

     python3 ./test_fileio.py --upstream_port eth1 --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 wpa2 --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 wpa2
                    ''')

    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="5m")
    parser.add_argument('--fio_type', help='--fio_type endpoint type', default="fe_nfs4")
    parser.add_argument('--min_read', help='--min_read sets the minimum bps read rate', default=0)
    parser.add_argument('--max_read', help='--max_read sets the maximum bps read rate', default=0)
    parser.add_argument('--min_write', help='--min_write sets the minimum bps write rate', default=10000000000)
    parser.add_argument('--max_write', help='--max_write sets the maximum bps write rate', default=0)
    parser.add_argument('--directory', help='--directory directory to read/write in. Absolute path suggested', default="AUTO")
    parser.add_argument('--server_mount', help='--server_mount The server to mount, ex: 192.168.100.5/exports/test1',
                        default="10.40.0.1:/var/tmp/test")
    args = parser.parse_args()

    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000,
                                          radio=args.radio)

    ip_test = IPV4FIO(args.mgr, lfjson_port, ssid=args.ssid, password=args.passwd,
                     security=args.security, station_list=station_list,
                     test_duration=args.test_duration, upstream_port=args.upstream_port,
                     _debug_on=args.debug, fio_type=args.fio_type, min_read=args.min_read,
                      max_read=args.max_read, min_write=args.min_write, max_write=args.max_write,
                      directory=args.directory)
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
