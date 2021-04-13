"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

Note: This is a test file which will run a wifi capacity test.
    ex. on how to run this script:
    ./lf_wifi_capacity.py --lfmgr "localhost" --port 8080 --lf_usr lanforge --lf_pswd lanforge
    --instance_name "this_inst" --config_name "test_con" --upstream eth1 --batch_size 1 --loop_iter 1
    --protocol "UDP-IPv4" --duration 6000 --pull_report y --auto_add n --stations sta0000

Note:
    --pull_report == keep it to y, if you want wifi capacity reports at end of the test.
                    This will pull reports from lanforge to your code directory,
                    from where you are running this code
                    keep this to n, if you are running this from lanforge

    --auto_add == if you dont want to add stations manually to wifi capacity test.
                keep this as y: This will automatically add all the stations to test
                if selected as n: Give station names in --stations argument
    --stations == if --auto_add is n, enter stations to use for wifi capacity

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
    global batch_size, loop_iter, protocol, duration, lf_host, lf_hostport, config_name, auto_add, upstream, stations, instance_name, pull_report, lf_usr, lf_pswd
    parser = argparse.ArgumentParser(
        description="""
             ./lf_wifi_capacity.py --lfmgr "localhost" --port 8080 --lf_usr lanforge --lf_pswd lanforge     
             --instance_name "instance" --config_name "wifi_config" --upstream eth1 --batch_size 1 --loop_iter 1     
             --protocol "UDP-IPv4" --duration 6000 --pull_report y --auto_add n --stations sta0000
               """)
    parser.add_argument("-m", "--lfmgr", type=str,
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-lf", "--lf_usr", type=str,
                        help="Lanforge username to pull reports")
    parser.add_argument("-lf_pw", "--lf_pswd", type=str,
                        help="Lanforge Password to pull reports")
    parser.add_argument("-i", "--instance_name", type=str,
                        help="create test instance")
    parser.add_argument("-c", "--config_name", type=str,
                        help="Config file name")
    parser.add_argument("-u", "--upstream", type=str,
                        help="Upstream port for wifi capacity test ex. eth1")
    parser.add_argument("-b", "--batch_size", type=str,
                        help="station increment ex. 1,2,3")
    parser.add_argument("-l", "--loop_iter", type=str,
                        help="Loop iteration ex. 1")
    parser.add_argument("-p", "--protocol", type=str,
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("-d", "--duration", type=str,
                        help="duration in ms. ex. 5000")
    parser.add_argument("-r", "--pull_report", type=str,
                        help="Enter y if test reports are need to be pulled from lanforge after test")
    parser.add_argument("-a", "--auto_add", type=str,
                        help="Enter y if all available stations are needs to be added , "
                             "Enter n if you want to give stations manually in stations argument")
    parser.add_argument("-s", "--stations", type=str,
                        help="in case if you selected n in auto_add enter stations name here ex.sta0000,sta0001")


    args = parser.parse_args()

    if args.lfmgr is not None:
        lf_host = args.lfmgr
    if args.port is not None:
        lf_hostport = args.port

    try:
        lf_usr = args.lf_usr
        lf_pswd = args.lf_pswd
        instance_name = args.instance_name
        config_name = args.config_name
        batch_size = args.batch_size
        loop_iter = args.loop_iter
        protocol = args.protocol
        duration = args.duration
        pull_report = args.pull_report
        upstream = args.upstream
        stations = args.stations
        auto_add = args.auto_add
    except:
        raise Exception("Wrong argument entered")

    test_name = "WiFi Capacity"

    # Test related settings
    dict = {"batch_size": "batch_size:" + " " + str(batch_size),
            "loop_iter": "loop_iter:" + " " + str(loop_iter),
            "protocol": "protocol:" + " " + str(protocol),
            "duration": "duration:" + " " + str(duration)}

    run_test = cvtest(lf_host, lf_hostport)
    createCV = cv(lf_host, lf_hostport);  # Create a object

    available_ports = []
    stripped_ports = []

    run_test.rm_text_blob(config_name, "Wifi-Capacity-")  # To delete old config with same name
    response = run_test.get_ports();

    ports = response["interfaces"]
    d1 = {k: v for e in ports for (k, v) in e.items()}
    all_ports = list(d1.keys())

    if auto_add == "yes" or auto_add == "y" or auto_add == "Y":
        for port in d1.keys():
            if port.__contains__("sta") or port.__contains__(upstream):
                available_ports.append(port)

        for i in range(len(available_ports)):
            add_port = "sel_port-" + str(i) + ":" + " " + available_ports[i]
            run_test.create_test_config(config_name, "Wifi-Capacity-", add_port)
    else:
        available_ports = []
        stations = stations.split(",")
        for str_port in all_ports:
            stripped_ports.append(str_port[4:])  # removing Resource from names

        if upstream in stripped_ports:
            available_ports.append(all_ports[stripped_ports.index(upstream)])
        else:
            raise Exception("Could not find upstream port")

        for sta in range(len(stations)):
            if stations[sta] in stripped_ports:
                available_ports.append(all_ports[stripped_ports.index(stations[sta])])
            else:
                raise Exception("%s not available" % stations[sta])

        if len(available_ports) == 0:
            print("No stations are given")
            exit(1)

        for count in range(len(available_ports)):
            add_port = "sel_port-" + str(count) + ":" + " " + available_ports[count]
            run_test.create_test_config(config_name, "Wifi-Capacity-", add_port)

    for key, value in dict.items():
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
                if (pull_report == "yes") or (pull_report == "y") or (pull_report == "Y"):
                    report.pull_reports(hostname=lf_host, username=lf_usr, password=lf_pswd,
                                        report_location=location)
            except:
                raise Exception("Could not find Reports")
            break

    run_test.rm_text_blob(config_name, "Wifi-Capacity-")  # To delete old config with same name


if __name__ == "__main__":
    main()
