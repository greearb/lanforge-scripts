#!/usr/bin/env python3

import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-dashboard'))

from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import json
from csv_to_grafana import CSVtoInflux
from create_l3 import CreateL3
from lf_wifi_capacity_test import WiFiCapacityTest
from cv_test_manager import *

def main():
    parser = argparse.ArgumentParser(
        prog='wifi_cap_to_grafana.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Run Wifi Capacity and record results to Grafana''',
        description='''\
        wifi_cap_to_grafana.py
        ------------------
        ./wifi_cap_to_grafana.py
            --num_stations
            --grafana_token
            --influx_host
            --influx_org
            --influx_token
            --influx_bucket
            --target_csv
            --panel_name'''
    )

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("-b", "--batch_size", type=str, default="",
                        help="station increment ex. 1,2,3")
    parser.add_argument("-l", "--loop_iter", type=str, default="",
                        help="Loop iteration ex. 1")
    parser.add_argument("-p", "--protocol", type=str, default="",
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("-d", "--duration", type=str, default="",
                        help="duration in ms. ex. 5000")
    parser.add_argument("--download_rate", type=str, default="1Gbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 1Gbps")
    parser.add_argument("--upload_rate", type=str, default="10Mbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--sort", type=str, default="interleave",
                        help="Select station sorting behaviour:  none | interleave | linear  Default is interleave.")
    parser.add_argument("-s", "--stations", type=str, default="",
                        help="If specified, these stations will be used.  If not specified, all available stations will be selected.  Example: 1.1.sta001,1.1.wlan0,...")
    parser.add_argument("-cs", "--create_stations", default=False, action='store_true',
                        help="create stations in lanforge (by default: False)")
    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)
    parser.add_argument('--number_template', help='Start the station numbering with a particular number. Default is 0000',
                        default=0000)
    parser.add_argument('--mode', help='Used to force mode of stations')
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')
    parser.add_argument("-radio", "--radio", default="wiphy0",
                        help="create stations in lanforge at this radio (by default: wiphy0)")
    parser.add_argument("-ssid", "--ssid", default="",
                        help="ssid name")
    parser.add_argument("-security", "--security", default="open",
                        help="ssid Security type")
    parser.add_argument("-passwd", "--passwd", default="[BLANK]",
                        help="ssid Password")
    parser.add_argument("--num_stations", default=2)
    parser.add_argument("--mgr_port", default=8080)
    parser.add_argument("--upstream_port", default="1.1.eth1")
    parser.add_argument("--debug", default=False)
    parser.add_argument("--scenario", help="", default=None)
    args = parser.parse_args()


    cv_base_adjust_parser(args)

    # Run WiFi Capacity Test
    wifi_capacity = WiFiCapacityTest(lfclient_host=args.mgr,
                                     lf_port=args.mgr_port,
                                     lf_user=args.lf_user,
                                     lf_password=args.lf_password,
                                     instance_name=args.instance_name,
                                     config_name=args.config_name,
                                     upstream=args.upstream_port,
                                     batch_size=args.batch_size,
                                     loop_iter=args.loop_iter,
                                     protocol=args.protocol,
                                     duration=args.duration,
                                     pull_report=args.pull_report,
                                     load_old_cfg=args.load_old_cfg,
                                     download_rate=args.download_rate,
                                     upload_rate=args.upload_rate,
                                     sort=args.sort,
                                     stations=args.stations,
                                     create_stations=args.create_stations,
                                     radio=args.radio,
                                     ssid=args.ssid,
                                     security=args.security,
                                     paswd=args.passwd,
                                     enables=args.enable,
                                     disables=args.disable,
                                     raw_lines=args.raw_line,
                                     raw_lines_file=args.raw_lines_file,
                                     sets=args.set)
    wifi_capacity.apply_cv_scenario(args.scenario)
    wifi_capacity.build_cv_scenario()
    wifi_capacity.setup()
    wifi_capacity.run()
    wifi_capacity.check_influx_kpi(args)

if __name__ == "__main__":
    main()