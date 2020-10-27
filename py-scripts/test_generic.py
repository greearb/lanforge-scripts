#!/usr/bin/env python3
import pprint
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
    def __init__(self, host, port, ssid, security, password, sta_list, name_prefix, upstream,
                 number_template="000", test_duration="5m", type="lfping", dest="127.0.0.1", cmd ="",
                 interval=1, radio="wiphy0",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.radio = radio
        self.upstream = upstream
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.generic_endps_profile = self.local_realm.new_generic_endp_profile()

        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0

        self.generic_endps_profile.name = name_prefix
        self.generic_endps_profile.type = type
        self.generic_endps_profile.dest = dest
        self.generic_endps_profile.cmd = cmd
        self.generic_endps_profile.interval = interval

    def start(self, print_pass=False, print_fail=False):
        self.station_profile.admin_up()
        temp_stas = []
        for station in self.sta_list.copy():
            temp_stas.append(self.local_realm.name_to_eid(station)[2])
        pprint.pprint(self.station_profile.station_names)
        LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url, port_list=self.station_profile.station_names)
        if self.local_realm.wait_for_ip(temp_stas):
            self._pass("All stations got IPs", print_pass)
        else:
            self._fail("Stations failed to get IPs", print_fail)
            exit(1)
        cur_time = datetime.datetime.now()
        passes = 0
        expected_passes = 0
        self.generic_endps_profile.start_cx()
        time.sleep(15)
        end_time = self.local_realm.parse_time("30s") + cur_time
        print("Starting Test...")
        while cur_time < end_time:
            cur_time = datetime.datetime.now()
            gen_results = self.json_get("generic/list?fields=name,last+results", debug_=self.debug)
            if gen_results['endpoints'] is not None:
                for name in gen_results['endpoints']:
                    for k, v in name.items():
                        if v['name'] in self.generic_endps_profile.created_endp and not v['name'].endswith('1'):
                            expected_passes += 1
                            if v['last results'] != "" and "Unreachable" not in v['last results']:
                                passes += 1
                            else:
                                self._fail("%s Failed to ping %s " % (v['name'], self.generic_endps_profile.dest), print_fail)
                                break
            # print(cur_time)
            # print(end_time)
            time.sleep(1)

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.generic_endps_profile.stop_cx()
        self.station_profile.admin_down()

    def build(self):
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)

        self.generic_endps_profile.create(ports=self.station_profile.station_names, sleep_time=.5)
        self._pass("PASS: Station build finished")

    def cleanup(self, sta_list):
        self.generic_endps_profile.cleanup()
        self.station_profile.cleanup(sta_list)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list, debug=self.debug)


def main():
    lfjson_port = 8080

    parser = LFCliBase.create_basic_argparse(
        prog='test_generic.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Create generic endpoints and test for their ability to execute chosen commands\n''',
        description='''test_generic.py
--------------------
Generic command example:
python3 ./test_generic.py --upstream_port eth1 \\
    --radio wiphy0 \\
    --num_stations 3 \\
    --security {open|wep|wpa|wpa2|wpa3} \\
    --ssid netgear \\
    --passwd admin123 \\
    --type lfping # {generic|lfping|iperf3|lf_curl} \\
    --dest 10.40.0.1 \\
    --test_duration 2m \\
    --interval 1s \\
    --debug 
''')

    parser.add_argument('--type', help='type of command to run: generic, lfping, ifperf3, lfcurl', default="lfping")
    parser.add_argument('--cmd', help='specifies command to be run by generic type endp', default='')
    parser.add_argument('--dest', help='destination IP for command', default="10.40.0.1")
    parser.add_argument('--test_duration', help='duration of the test eg: 30s, 2m, 4h', default="2m")
    parser.add_argument('--interval', help='interval to use when running lfping (1s, 1m)', default=1)

    args = parser.parse_args()
    num_sta = 2
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_sta = int(args.num_stations)
    station_list = LFUtils.portNameSeries(radio=args.radio,
                                          prefix_="sta",
                                          start_id_=0,
                                          end_id_=num_sta-1,
                                          padding_number_=100)

    generic_test = GenTest(args.mgr, lfjson_port,
                           number_template="00",
                           radio=args.radio,
                           sta_list=station_list,
                           name_prefix="GT",
                           type=args.type,
                           dest=args.dest,
                           cmd=args.cmd,
                           interval=1,
                           ssid=args.ssid,
                           upstream=args.upstream_port,
                           password=args.passwd,
                           security=args.security,
                           test_duration=args.test_duration,
                           _debug_on=args.debug)

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
        print("Full test passed")



if __name__ == "__main__":
    main()
