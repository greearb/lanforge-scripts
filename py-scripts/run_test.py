import sys
import os
import argparse
import time
import json

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_test_manager import cv_test as cvtest

def main():

    #Test related settings
    batch_size = "3"
    loop_iter = "3"
    protocol = "UDP-IPv4"
    duration = " 7000"
    dict = {"batch_size": "batch_size:"+" "+str(batch_size),
            "loop_iter": "loop_iter:"+" "+str(loop_iter),
            "protocol": "protocol:"+" "+str(protocol),
            "duration": "duration:"+" "+str(duration)}

    config_name = "Test_29" #Test Config Name (new)
    instance_name = "wifi_capacity_instance" #Test Instance name
    test_name = "WiFi Capacity" #Test name

    run_test = cvtest("192.168.200.15","8080")

    port_list = []

    response = run_test.check_ports();
    print(response)
    port_size = json.dumps(len(response["interfaces"]))

    print(port_size)
    print(response)
    print((int(port_size)))

    for i in range(int(port_size)):
        list_val = json.dumps(response["interfaces"][i])
        list_val_ = json.loads(list_val).keys()
        list_val_ = str(list_val_).replace("dict_keys(['", "")
        list_val_ = str(list_val_).replace("'])", "")
        if (list_val_.__contains__("sta") or list_val_.__contains__("eth1")):
            print(list_val_)
            port_list.append(list_val_)
    print("54",port_list)

    for i in range(len(port_list)):
        add_port = "sel_port-" + str(i) + ":" + " " + port_list[i]
        run_test.create_test_config(config_name, add_port)
        time.sleep(0.2)

    for key, value in dict.items():
        run_test.create_test_config(config_name, value)
        time.sleep(0.2)

    run_test.create_test(test_name,instance_name)
    run_test.load_test_config("DEFAULT",instance_name)
    time.sleep(1)
    run_test.load_test_config(config_name, instance_name)
    time.sleep(1)
    run_test.load_test_config(config_name, instance_name)
    time.sleep(1)
    run_test.load_test_config("DEFAULT", instance_name)
    time.sleep(2)
    run_test.load_test_config(config_name, instance_name)
    run_test.start_test(instance_name)


    print(port_list)
if __name__ == "__main__":
    main()
