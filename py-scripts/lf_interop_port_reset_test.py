#!/usr/bin/env python3
"""
NAME: lf_interop_port_reset_test.py

PURPOSE: for port reset test i.e getting cx time after disabling Wi-Fi from devices

EXAMPLE:
$ ./lf_interop_port_reset_test.py --host 192.168.1.31

NOTES:
#Currently this script will enable and disable WI-FI on devices connected to LANforge
#@TODO finish logic for calculating cx time from logs
"""
import sys
import os
import importlib
import argparse
import shlex
import subprocess
import json
import time


if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
lf_csv = importlib.import_module("py-scripts.lf_csv")


class InteropPortReset:
    def __init__(self, host):
        self.host = host

    def get_device_details(self, query="name"):
        # query device related details like name, phantom, model name etc
        value = []
        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.host) + ''':8080/adb/'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = (stdout.decode("utf-8"))
        out = json.loads(output)
        final = out["devices"]
        print("response", final)
        if type(final) == list:
            # print(len(final))
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            # print(keys_lst)

            for i, j in zip(range(len(keys_lst)), keys_lst):
                value.append(final[i][j][query])

        else:
            #  only one device is present
            value.append(final[query])
        return value

    def run(self):
        # get the list of adb devices
        adb_device_list = self.get_device_details(query="name")
        print(adb_device_list)

        # check status of devices
        phantom = self.get_device_details(query="phantom")
        print(phantom)
        state = None
        for i in phantom:
            if str(i) == "False":
                print("all devices are up")
                state = "up"
            else:
                print("all devices are not up")
                exit(1)
        if state == "up":
            # provide device name
            for i, j in zip(adb_device_list, range(len(adb_device_list))):
                print(i)
                modify = interop_modify.InteropCommands(_host=self.host,
                                                        _port=8080,
                                                        device_eid=i,
                                                        set_adb_user_name=True,
                                                        adb_username="device_" + str(int(j+1)))
                modify.run()

                # enable and disable Wi-Fi
                modify_1 = interop_modify.InteropCommands(_host=self.host,
                                                          _port=8080,
                                                          device_eid=i,
                                                          wifi="enable")
                modify_1.run()

                time.sleep(10)

                modify_1 = interop_modify.InteropCommands(_host=self.host,
                                                          _port=8080,
                                                          device_eid=i,
                                                          wifi="disable")
                modify_1.run()


def main():
    desc = """ port reset test """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--host", "--mgr", default='localhost',
                        help='specify the GUI to connect to, assumes port 8080')
    args = parser.parse_args()

    obj = InteropPortReset(host=args.host)
    obj.run()


if __name__ == '__main__':
    main()