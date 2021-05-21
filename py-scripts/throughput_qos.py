#!/usr/bin/env python3

"""
NAME: throughput_qos.py

PURPOSE: throughput_qos.py will create stations and endpoints which evaluates  l3 traffic for a particular type of service.

EXAMPLE:
python3 throughput_qos.py --mgr 192.168.200.240 --mgr_port 8080 -u eth1 --num_stations 1
--radio wiphy1 --ssid TestAP5-71 --passwd lanforge --security wpa2 --mode 11 --a_min 1000000 --b_min 1000000 --traffic_type lf_udp

python3 throughput_qos.py --num_stations 1 --radio wiphy1 --ssid ct523c-vap --passwd ct523c-vap --security wpa2 --mode 11 --a_min 1000000 --b_min 1000000 --traffic_type lf_udp


Use './throughput_qos.py --help' to see command line usage and options
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""

import sys
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge import LFUtils
from realm import Realm
import time
import datetime


class ThroughputQOS(Realm):
    def __init__(self,
                 tos,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=[],
                 create_sta=True,
                 name_prefix=None,
                 upstream=None,
                 radio=None,
                 host="localhost",
                 port=8080,
                 mode=0,
                 ap=None,
                 traffic_type=None,
                 side_a_min_rate=56, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="15m",
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.create_sta = create_sta
        self.security = security
        self.password = password
        self.radio = radio
        self.mode = mode
        self.ap = ap
        self.traffic_type = traffic_type
        self.tos = tos.split(",")
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
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
        if self.ap is not None:
            self.station_profile.set_command_param("add_sta", "ap", self.ap)
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def start(self, print_pass=False, print_fail=False):
        if self.create_sta:
            self.station_profile.admin_up()
            # to-do- check here if upstream port got IP
            temp_stas = self.station_profile.station_names.copy()

            if self.wait_for_ip(temp_stas):
                self._pass("All stations got IPs")
            else:
                self._fail("Stations failed to get IPs")
                self.exit_fail()
        self.cx_profile.start_cx()

    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        if self.create_sta:
            for sta in self.sta_list:
                self.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.cx_profile.cleanup()
        if self.create_sta:
            self.station_profile.cleanup()
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                               debug=self.debug)

    def build(self):
        if self.create_sta:
            self.station_profile.use_security(self.security, self.ssid, self.password)
            self.station_profile.set_number_template(self.number_template)
            print("Creating stations")
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
            self._pass("PASS: Station build finished")

        # self.cx_profile.create(endp_type=self.traffic_type, side_a=self.upstream,
        #                        side_b=self.sta_list,
        #                        sleep_time=0, tos=BE)
        self.create_cx()
        print("cx build finished")

    def create_cx(self):
        _tos = "BE,BK,VI,VO"
        self.tos = _tos.split(",")
        print("tos: {}".format(self.tos))
        for ip_tos in self.tos:
            print("## ip_tos: {}".format(ip_tos))
            print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
            self.traffic_type, ip_tos, self.cx_profile.get_cx_count()))
            self.cx_profile.create(endp_type=self.traffic_type, side_a=self.sta_list,
                                   side_b=self.upstream,
                                   sleep_time=0, tos=ip_tos)

        print("cross connections with TOS type created.")

    def evaluate_throughput(self):
        test_bps_rx_a, test_bps_rx_b = [], []
        for sta in self.cx_profile.created_cx.keys():
            if self.cx_profile.side_a_min_bps != '0':
                test_bps_rx_a.append(float(
                    f"{list((self.json_get('/cx/%s?fields=bps+rx+a' % (sta))).values())[2]['bps rx a'] / 10000:.2f}"))
            if self.cx_profile.side_b_min_bps != '0':
                test_bps_rx_b.append(float(
                    f"{list((self.json_get('/cx/%s?fields=bps+rx+b' % (sta))).values())[2]['bps rx b'] / 10000:.2f}"))
        return test_bps_rx_a, test_bps_rx_b


def main():
    parser = Realm.create_basic_argparse(
        prog='throughput_QOS.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open)
            ''',
        description='''\
throughput_QOS.py:
--------------------
Generic command layout:

python3 ./throughput_QOS.py
    --upstream_port eth1
    --radio wiphy0
    --num_stations 32
    --security {open|wep|wpa|wpa2|wpa3}
    --mode   1
        {"auto"   : "0",
        "a"      : "1",
        "b"      : "2",
        "g"      : "3",
        "abg"    : "4",
        "abgn"   : "5",
        "bgn"    : "6",
        "bg"     : "7",
        "abgnAC" : "8",
        "anAC"   : "9",
        "an"     : "10",
        "bgnAC"  : "11",
        "abgnAX" : "12",
        "bgnAX"  : "13"}
    --ssid netgear
    --password admin123
    --test_duration 2m (default)
    --monitor_interval_ms 
    --a_min 3000
    --b_min 1000
    --ap "00:0e:8e:78:e1:76"
    --output_format csv
    --traffic_type lf_udp
    --report_file ~/Documents/results.csv                       (Example of csv file output  - please use another extension for other file formats)
    --compared_report ~/Documents/results_prev.csv              (Example of csv file retrieval - please use another extension for other file formats) - UNDER CONSTRUCTION
    --layer3_cols 'name','tx bytes','rx bytes','dropped'          (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --port_mgr_cols 'ap','ip'                                    (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --debug

    python3 ./throughput_QOS.py
    --upstream_port eth1        (upstream POrt)
    --traffic_type lf_udp       (traffic type, lf_udp | lf_tcp)
    --test_duration 5m          (duration to run traffic 5m --> 5 Minutes)
    --create_sta False          (False, means it will not create stations and use the sta_names specified below)
    --sta_names sta000,sta001,sta002 (used if --create_sta False, comma separated names of stations)
    ''')

    parser.add_argument('--mode', help='Used to force mode of stations')
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=True)
    parser.add_argument('--output_format', help='choose either csv or xlsx')
    parser.add_argument('--report_file', help='where you want to store results', default=None)
    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    parser.add_argument('--create_sta', help='Used to force a connection to a particular AP', default=True)
    parser.add_argument('--sta_names', help='Used to force a connection to a particular AP', default="sta0000")
    parser.add_argument('--tos', help='used to provide different ToS settings: BK | BE | VI | VO | numeric',
                        default="BE")
    args = parser.parse_args()
    create_sta = True
    if args.create_sta == "False":
        create_sta = False

    num_sta = 2
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_sta = int(args.num_stations)

    if create_sta:
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=num_sta - 1, padding_number_=10000,
                                              radio=args.radio)
    else:
        station_list = args.sta_names.split(",")
    throughput_qos_test = ThroughputQOS(host=args.mgr,
                                        port=args.mgr_port,
                                        number_template="0000",
                                        sta_list=station_list,
                                        create_sta=create_sta,
                                        name_prefix="TP",
                                        upstream=args.upstream_port,
                                        ssid=args.ssid,
                                        password=args.passwd,
                                        radio=args.radio,
                                        security=args.security,
                                        test_duration=args.test_duration,
                                        use_ht160=False,
                                        side_a_min_rate=args.a_min,
                                        side_b_min_rate=args.b_min,
                                        mode=args.mode,
                                        ap=args.ap,
                                        traffic_type=args.traffic_type,
                                        tos=args.tos,
                                        _debug_on=args.debug)

    throughput_qos_test.pre_cleanup()

    throughput_qos_test.build()
    # exit()
    if create_sta:
        if not throughput_qos_test.passes():
            print(throughput_qos_test.get_fail_message())
            throughput_qos_test.exit_fail()

    try:
        layer3connections = ','.join([[*x.keys()][0] for x in throughput_qos_test.json_get('endp')['endpoint']])
    except:
        raise ValueError('Try setting the upstream port flag if your device does not have an eth1 port')

    throughput_qos_test.start(False, False)
    # throughput_qos_test.stop()
    if create_sta:
        if not throughput_qos_test.passes():
            print(throughput_qos_test.get_fail_message())
            throughput_qos_test.exit_fail()
        LFUtils.wait_until_ports_admin_up(port_list=station_list)
        if throughput_qos_test.passes():
            throughput_qos_test.success()
    # throughput_qos_test.cleanup()


if __name__ == "__main__":
    main()