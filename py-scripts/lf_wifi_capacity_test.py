#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

Note: This is a test file which will run a wifi capacity test.
    ex. on how to run this script:
    ./lf_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge
    --instance_name this_inst --config_name test_con --upstream 1.1.eth1 --batch_size 1 --loop_iter 1
    --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0002

Note:
    --pull_report == If specified, this will pull reports from lanforge to your code directory,
                    from where you are running this code

    --stations == Enter stations to use for wifi capacity
"""

import sys
import os
import argparse
import time
import json
from os import path

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_test_manager import cv_test as cvtest
from cv_commands import chamberview as cv
from cv_test_reports import lanforge_reports as lf_rpt


def main():
    global lf_host, lf_hostport, config_name, instance_name
    parser = argparse.ArgumentParser(
        description="""
             ./lf_wifi_capacity_test.py --lfgui localhost --port 8080 --lf_user lanforge --lf_password lanforge     
             --instance_name wct_instance --config_name wifi_config --upstream 1.1.eth1 --batch_size 1 --loop_iter 1     
             --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0001
               """)
    parser.add_argument("-m", "--mgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user", type=str, default="lanforge",
                        help="Lanforge username to pull reports")
    parser.add_argument("--lf_password", type=str, default="lanforge",
                        help="Lanforge Password to pull reports")
    parser.add_argument("-i", "--instance_name", type=str,
                        help="create test instance")
    parser.add_argument("-c", "--config_name", type=str,
                        help="Config file name")
    parser.add_argument("-u", "--upstream", type=str, default="1.1.eth1",
                        help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("-b", "--batch_size", type=str, default="1,5,10",
                        help="station increment ex. 1,2,3")
    parser.add_argument("-l", "--loop_iter", type=str, default="1",
                        help="Loop iteration ex. 1")
    parser.add_argument("-p", "--protocol", type=str, default="TCP-IPv4",
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("-d", "--duration", type=str, default="10000",
                        help="duration in ms. ex. 5000")
    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--download_rate", type=str, default="1Gbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 1Gbps")
    parser.add_argument("--upload_rate", type=str, default="10Mbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--sort", type=str, default="interleave",
                        help="Select station sorting behaviour:  none | interleave | linear  Default is interleave.")
    parser.add_argument("-s", "--stations", type=str, default="",
                        help="If specified, these stations will be used.  If not specified, all available stations will be selected.  Example: 1.1.sta001,1.1.wlan0,...")


    args = parser.parse_args()

    lf_host = args.mgr
    lf_hostport = args.port

    instance_name = args.instance_name
    config_name = args.config_name

    test_name = "WiFi Capacity"

    run_test = cvtest(lf_host, lf_hostport)
    createCV = cv(lf_host, lf_hostport);  # Create a object

    available_ports = []
    stripped_ports = []

    run_test.rm_text_blob(config_name, "Wifi-Capacity-")  # To delete old config with same name

    # Test related settings
    cfg_options = ["batch_size: " + str(args.batch_size),
                   "loop_iter: " + str(args.loop_iter),
                   "protocol: " + str(args.protocol),
                   "duration: " + str(args.duration),
                   "ul_rate: " + args.upload_rate,
                   "dl_rate: " + args.download_rate,
                   ]

    port_list = [args.upstream]
    if args.stations == "":
        stas = run_test.station_map()  # See realm
        for eid in stas.keys():
            port_list.append(eid)
    else:
        stas = args.stations.split(",")
        for s in stas:
            port_list.append(s)

    idx = 0
    for eid in port_list:
        add_port = "sel_port-" + str(idx) + ": " + eid
        run_test.create_test_config(config_name,"Wifi-Capacity-",add_port)
        idx += 1

    for value in cfg_options:
        run_test.create_test_config(config_name, "Wifi-Capacity-", value)

    for i in range(60):
        response = run_test.create_test(test_name, instance_name)
        d1 = {k: v for e in response for (k, v) in e.items()}
        if d1["LAST"]["response"] == "OK":
            break
        else:
            time.sleep(1)

    createCV.sync_cv()
    time.sleep(2)
    run_test.load_test_config(config_name, instance_name)
    run_test.auto_save_report(instance_name)

    if args.sort == 'linear':
        cmd = "cv click '%s' 'Linear Sort'" % instance_name
        run_test.run_cv_cmd(cmd)
    if args.sort == 'interleave':
        cmd = "cv click '%s' 'Interleave Sort'" % instance_name
        run_test.run_cv_cmd(cmd)


    response = run_test.start_test(instance_name)
    d1 = {k: v for e in response for (k, v) in e.items()}
    if d1["LAST"]["response"].__contains__("Could not find instance:"):
        exit(1)

    while (True):
        check = run_test.get_report_location(instance_name)
        location = json.dumps(check[0]["LAST"]["response"])
        if location != "\"Report Location:::\"":
            location = location.replace("Report Location:::", "")
            run_test.close_instance(instance_name)
            run_test.cancel_instance(instance_name)
            location = location.strip("\"")
            report = lf_rpt()
            print(location)
            try:
                if args.pull_report:
                    report.pull_reports(hostname=lf_host, username=args.lf_user, password=args.lf_password,
                                        report_location=location)
            except:
                raise Exception("Could not find Reports")
            break

    run_test.rm_text_blob(config_name, "Wifi-Capacity-")  # To delete old config with same name


if __name__ == "__main__":
    main()
