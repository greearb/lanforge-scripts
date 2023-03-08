#!/usr/bin/env python3
import sys
import os
import importlib
import argparse
import time
import json
from os import path
import sta_scan_test
import pandas as pd
import subprocess

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

#def get_bssid_from_df(self, dataframe):
#    run_dut_bash_command=""
#    subprocess.run

def main():
    parser = Realm.create_basic_argparse(
        prog='sta_scan_test.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Used to scan for ssids after creating a station
            ''',
        description='''\
        Optionally creates a station with specified ssid info (can be real or fake ssid, if fake use open for security).
        If not creating a station, it can use existing station.
        Then starts a scan and waits 15 seconds, finally scan results are printed to console.
        
        Example:
        ./sta_scan_test.py --ssid test_name --security open --radio wiphy0
        ./sta_scan_test.py --sta_name 1.14.wlan0 1.1.wlan0 --use_existing_station --scan_time 5
        ''')

    parser.add_argument('--use_existing_station', action='store_true', help='Use existing station instead of trying to create stations.')
    parser.add_argument('--mode', help='Used to force mode of stations')
    parser.add_argument('--sta_name', help='Optional: User defined station names: 1.2.wlan0 1.3.wlan0', nargs='+',
                        default=["sta0000"])
    parser.add_argument('--csv_output', help='Specify file to which csv output will be saved, otherwise print it in the terminal',
                        default=None)
    parser.add_argument('--scan_time', help='Specify time in seconds to wait for scan to complete.  Default is 15',
                        default=15, type=int)

    args = parser.parse_args()

    station_list = args.sta_name
    print("about to create StaScan object...")
    sta_scan = sta_scan_test.StaScan(host=args.mgr,
                            port=args.mgr_port,
                            number_template="0000",
                            sta_list=station_list,
                            upstream=args.upstream_port,
                            ssid=args.ssid,
                            password=args.passwd,
                            radio=args.radio,
                            security=args.security,
                            use_ht160=False,
                            use_existing_station=args.use_existing_station,
                            scan_time=args.scan_time,
                            csv_output=args.csv_output,
                            mode=args.mode,
                            _debug_on=args.debug)

    if (not args.use_existing_station):
        sta_scan.sta_scan_test.pre_cleanup()

        sta_scan.sta_scan_test.build()
        # exit()
        if not sta_scan.sta_scan_test.passes():
            print(sta_scan.sta_scan_test.get_fail_message())
            sta_scan.sta_scan_test.exit_fail()

    dataframe = sta_scan.sta_scan_test.start()
    if dataframe is not None:
        print("we got our dataframe")
        print(dataframe)

    if (not args.use_existing_station):
        sta_scan_test.cleanup()

    #get_bssid_from_df(dataframe)

if __name__ == "__main__":
    main()