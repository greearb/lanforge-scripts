#!/usr/bin/env python3

"""
NAME: sta_scan_test.py

PURPOSE:
Creates a station with specified ssid info (can be real or fake ssid, if fake use open for security), then
starts a scan and waits 15 seconds, finally scan results are printed to console

Use './sta_scan_test.py --help' to see command line usage and options
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""

import sys
import os
import importlib
import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import argparse
import time

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")


class StaScan(Realm):
    def __init__(self,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=None,
                 upstream=None,
                 radio=None,
                 host="localhost",
                 port=8080,
                 mode=0,
                 number_template="00000",
                 csv_output=False,
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        if sta_list is None:
            sta_list = []
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.radio = radio
        self.mode = mode
        self.number_template = number_template
        self.csv_output = csv_output
        self.debug = _debug_on
        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.debug = self.debug

        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 9
        self.station_profile.mode = mode

    def start(self):
        self.station_profile.admin_up()
        print(self.sta_list)
        LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                          debug_=self.debug)
        stations = [LFUtils.name_to_eid(x) for x in self.sta_list]
        stations = pd.DataFrame(stations)
        resources = stations[1].unique()
        interfaces = list()
        for resource in resources:
            shelf = stations[0][0]
            resource_station = list(stations[stations[1] == resource][2])
            url = '/port/%s/%s/%s' % (shelf, resource, ','.join(resource_station))
            response = self.json_get(url)
            if 'interface' in response.keys():
                interface = response['interface']
                interfaces.append(interface)
            elif 'interfaces' in response.keys():
                response_interfaces = response['interfaces']
                for interface in response_interfaces:
                    for item in interface.values():
                        interfaces.append(item)
        df = pd.DataFrame(interfaces)
        stations = df[df['port type'] == 'WIFI-STA']
        stations = list(stations.drop_duplicates('parent dev')['alias'])
        stations = [station for station in stations if station in self.sta_list]

        for port in stations:
            port = LFUtils.name_to_eid(port)
            data = {
                "shelf": port[0],
                "resource": port[1],
                "port": port[2]
            }
            self.json_post("/cli-json/scan_wifi", data)
            time.sleep(15)
            scan_results = self.json_get("scanresults/%s/%s/%s" % (port[0], port[1], port[2]))
            if self.csv_output:
                results = scan_results['scan-results']
                df = pd.DataFrame([list(result.values())[0] for result in results])
                df.to_csv(self.csv_output)
                print('CSV output saved at %s' % self.csv_output)
            else:
                print("{0:<23}".format("BSS"), "{0:<7}".format("Signal"), "{0:<5}".format("SSID"))
                for result in scan_results['scan-results']:
                    for name, info in result.items():
                        print("%s\t%s\t%s" % (info['bss'], info['signal'], info['ssid']))

    def pre_cleanup(self):
        for sta in self.sta_list:
            self.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def build(self):
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, num_stations=1, debug=self.debug)
        self._pass("PASS: Station build finished")
        LFUtils.wait_until_ports_appear(','.join(self.sta_list))


def main():
    parser = Realm.create_basic_argparse(
        prog='sta_scan_test.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Used to scan for ssids after creating a station
            ''',
        description='''\
        Creates a station with specified ssid info (can be real or fake ssid, if fake use open for security), then 
        starts a scan and waits 15 seconds, finally scan results are printed to console 
        
        Example:
        ./sta_scan_test.py --ssid test_name --security open --radio wiphy0
        ''')

    parser.add_argument('--mode', help='Used to force mode of stations')
    parser.add_argument('--sta_name', help='Optional: User defined station names, can be a comma or space separated list', nargs='+',
                        default=["sta0000"])
    parser.add_argument('--csv_output', help='create CSV from scan results, otherwise print it in the terminal', default=None)

    args = parser.parse_args()

    station_list = args.sta_name
    sta_scan_test = StaScan(host=args.mgr,
                            port=args.mgr_port,
                            number_template="0000",
                            sta_list=station_list,
                            upstream=args.upstream_port,
                            ssid=args.ssid,
                            password=args.passwd,
                            radio=args.radio,
                            security=args.security,
                            use_ht160=False,
                            csv_output=args.csv_output,
                            mode=args.mode,
                            _debug_on=args.debug)

    sta_scan_test.pre_cleanup()

    sta_scan_test.build()
    # exit()
    if not sta_scan_test.passes():
        print(sta_scan_test.get_fail_message())
        sta_scan_test.exit_fail()

    sta_scan_test.start()
    sta_scan_test.cleanup()


if __name__ == "__main__":
    main()
