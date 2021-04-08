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
from chamberview import chamberview as cv
from cvtest_reports import lanforge_reports as lf_rpt

def main():
    config_name = "WFC_scenario1"  # Test Config Name (new)
    instance_name = "wfc_instance"  # Test Instance name
    test_name = "WiFi Capacity"  # Test name

    # Test related settings
    batch_size = "5"
    loop_iter = "1"
    protocol = "TCP-IPv4"
    duration = " 5000"
    dict = {"batch_size": "batch_size:" + " " + str(batch_size),
            "loop_iter": "loop_iter:" + " " + str(loop_iter),
            "protocol": "protocol:" + " " + str(protocol),
            "duration": "duration:" + " " + str(duration)}



    run_test = cvtest("192.168.200.21", "8080")
    createCV = cv("192.168.200.21", "8080");  # Create a object


    port_list = []

    response = run_test.check_ports();
    port_size = json.dumps(len(response["interfaces"]))

    for i in range(int(port_size)):
        list_val = json.dumps(response["interfaces"][i])
        list_val_ = json.loads(list_val).keys()
        list_val_ = str(list_val_).replace("dict_keys(['", "")
        list_val_ = str(list_val_).replace("'])", "")
        if (list_val_.__contains__("sta") or list_val_.__contains__("eth1")):
            port_list.append(list_val_)

    for i in range(len(port_list)):
        add_port = "sel_port-" + str(i) + ":" + " " + port_list[i]
        run_test.create_test_config(config_name, add_port)
        time.sleep(0.2)

    for key, value in dict.items():
        run_test.create_test_config(config_name, value)
        time.sleep(0.2)


    run_test.create_test(test_name, instance_name)
    time.sleep(5)
    createCV.sync_cv()
    time.sleep(2)
    run_test.load_test_config(config_name, instance_name)
    time.sleep(2)
    run_test.auto_save_report(instance_name)
    time.sleep(4)
    run_test.start_test(instance_name)

    while (True):
        check = run_test.get_report_location(instance_name)
        location = json.dumps(check[0]["LAST"]["response"])
        print("WiFi Capacity Test Running...")
        if location != "\"Report Location:::\"":
            location = location.replace("Report Location:::","")
            print(location)
            time.sleep(1)
            run_test.close_instance(instance_name)
            time.sleep(1)
            run_test.cancel_instance(instance_name)
            time.sleep(4)
            break

    time.sleep(60)
    report = lf_rpt()
    report.pull_reports(hostname="192.168.200.21", username="lanforge", password="lanforge",
                        report_location=location)

if __name__ == "__main__":
    main()
