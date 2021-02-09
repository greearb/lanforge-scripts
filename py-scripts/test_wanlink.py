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

class LANtoWAN(LFCliBase):
    def __init__(self, host, port, ssid, security, password, lan_port="eth2", wan_port="eth3", _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.timeout = 120
        self.lan_port = lan_port
        self.wan_port = wan_port
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                            security=self.security, number_template_=self.prefix, mode=0, up=True, dhcp=True,
                                            debug_=False)
        self.cxProfile = realm.new_l3_cx_profile()

    def run_test(self): pass

    def create_wanlinks(self, shelf=1, resource=1, latency=20, max_rate=1544000):
        print("Creating wanlinks")
        # create redirects for wanlink
        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rdd0",
            "peer_ifname": "rdd1"
        }
        self.json_post(url, data)

        url = "/cli-json/add_rdd"
        data = {
            "shelf": shelf,
            "resource": resource,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        self.json_post(url, data)
        time.sleep(.05)

        # create wanlink endpoints
        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan0",
            "shelf": shelf,
            "resource": resource,
            "port": "rdd0",
            "latency": latency,
            "max_rate": max_rate
        }
        self.json_post(url, data)

        url = "/cli-json/add_wl_endp"
        data = {
            "alias": "wlan1",
            "shelf": shelf,
            "resource": resource,
            "port": "rdd1",
            "latency": latency,
            "max_rate": max_rate
        }
        self.json_post(url, data)
        time.sleep(.05)

    def run(self):
        self.profile.use_wpa2(True, self.ssid, self.password)
        self.profile.create(resource=1, radio="wiphy0", num_stations=3, debug=False)

    def cleanup(self): pass


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='test_ipv4_variable_time.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open)
            ''',

        description='''\
test_ipv4_variable_time.py:
--------------------
Generic command layout:

python3 ./test_ipv4_variable_time.py
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
    --a_min 3000
    --b_min 1000
    --ap "00:0e:8e:78:e1:76"
    --output_format csv
    --report_file ~/Documents/results.csv                       (Example of csv file output  - please use another extension for other file formats)
    --compared_report ~/Documents/results_prev.csv              (Example of csv file retrieval - please use another extension for other file formats) - UNDER CONSTRUCTION
    --col_names 'name','tx bytes','rx bytes','dropped'          (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --debug
===============================================================================
 ** FURTHER INFORMATION **
    Using the col_names flag:

    Currently the output function does not support inputting the columns in col_names the way they are displayed in the GUI. This quirk is under construction. To output
    certain columns in the GUI in your final report, please match the according GUI column display to it's counterpart to have the columns correctly displayed in
    your report.

    GUI Column Display       Col_names argument to type in (to print in report)

    Name                |  'name'
    EID                 |  'eid'
    Run                 |  'run'
    Mng                 |  'mng'
    Script              |  'script'
    Tx Rate             |  'tx rate'
    Tx Rate (1 min)     |  'tx rate (1&nbsp;min)'
    Tx Rate (last)      |  'tx rate (last)'
    Tx Rate LL          |  'tx rate ll'
    Rx Rate             |  'rx rate'
    Rx Rate (1 min)     |  'rx rate (1&nbsp;min)'
    Rx Rate (last)      |  'rx rate (last)'
    Rx Rate LL          |  'rx rate ll'
    Rx Drop %           |  'rx drop %'
    Tx PDUs             |  'tx pdus'
    Tx Pkts LL          |  'tx pkts ll'
    PDU/s TX            |  'pdu/s tx'
    Pps TX LL           |  'pps tx ll'
    Rx PDUs             |  'rx pdus'
    Rx Pkts LL          |  'pps rx ll'
    PDU/s RX            |  'pdu/s tx'
    Pps RX LL           |  'pps rx ll'
    Delay               |  'delay'
    Dropped             |  'dropped'
    Jitter              |  'jitter'
    Tx Bytes            |  'tx bytes'
    Rx Bytes            |  'rx bytes'
    Replays             |  'replays'
    TCP Rtx             |  'tcp rtx'
    Dup Pkts            |  'dup pkts'
    Rx Dup %            |  'rx dup %'
    OOO Pkts            |  'ooo pkts'
    Rx OOO %            |  'rx ooo %'
    RX Wrong Dev        |  'rx wrong dev'
    CRC Fail            |  'crc fail'
    RX BER              |  'rx ber'
    CX Active           |  'cx active'
    CX Estab/s          |  'cx estab/s'
    1st RX              |  '1st rx'
    CX TO               |  'cx to'
    Pattern             |  'pattern'
    Min PDU             |  'min pdu'
    Max PDU             |  'max pdu'
    Min Rate            |  'min rate'
    Max Rate            |  'max rate'
    Send Buf            |  'send buf'
    Rcv Buf             |  'rcv buf'
    CWND                |  'cwnd'
    TCP MSS             |  'tcp mss'
    Bursty              |  'bursty'
    A/B                 |  'a/b'
    Elapsed             |  'elapsed'
    Destination Addr    |  'destination addr'
    Source Addr         |  'source addr'
            ''')
    for group in parser._action_groups:
        if group.title == "required arguments":
            required_args=group
            break
    #if required_args is not None:

    optional_args=None
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    #if optional_args is not None:
    args = parser.parse_args()
    ltw=LANtoWAN(host=args.mgr,
                 port=args.mgr_port,
                 ssid=args.ssid,
                 security=args.security,
                 password=args.passwd,
                 lan_port=args.lanport,
                 wan_port=args.wanport,)
    ltw.create_wanlinks()
    ltw.run()
    ltw.cleanup()

if __name__ == "__main__":
    main()