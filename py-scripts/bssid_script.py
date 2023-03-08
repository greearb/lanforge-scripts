#!/usr/bin/env python3
import importlib
import argparse
import sta_scan_test
import pandas as pd
import subprocess
import sys
import os

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

def main():
    parser = Realm.create_basic_argparse(
        prog='bssid_script.py',
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
    parser.add_argument('--dut_name', help='Specify the name the new DUT should be called. Default name is bssid_dut.', default="bssid_dut")
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
        sta_scan.pre_cleanup()

        sta_scan.build()
        # exit()
        if not sta_scan.passes():
            print(sta_scan.get_fail_message())
            sta_scan.exit_fail()

    df = sta_scan.start()

    if (not args.use_existing_station):
        sta_scan.cleanup()

    #do dataframe manipulation
    if not isinstance(df, pd.DataFrame):
        print("Scan results are not in dataframe form.")
    else:
        ssid_df = df[df["ssid"] == args.ssid]
        if not ssid_df.empty:
            bssid_list = []
            for bss in ssid_df["bss"]:
                bssid_list.append(bss)

    #run create_chamberview_dut script. (WIP) This section is a bit hardcoded at the moment, 
    # can be edited to create num ssid lines based on bssids in list, and then concat those lines to python command

    ssid_line_1 = "ssid_idx=0 ssid=Dut-SSID security=WPA2 password=lanforge123 bssid=" + bssid_list[0]
    ssid_line_2 = "ssid_idx=1 ssid=Dut-SSID-5G security=WPA2 password=lanforge123 bssid=" + bssid_list[1]
    full_dut_command = "./create_chamberview_dut.py --lfmgr localhost -o 8080 --dut_name" + args.dut_name + "--dut_flag='DHCPD-LAN' --dut_flag='DHCPD-WAN' --ssid '" + ssid_line_1 + "' --ssid '" + ssid_line_2 + "'"
    if (args.debug):
        print(ssid_line_1)
        print(ssid_line_2)
        print(full_dut_command)
    subprocess.run(full_dut_command, shell=True)


if __name__ == "__main__":
    main()