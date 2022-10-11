#!/usr/bin/env python3
"""
NAME: lf_interop_port_reset_test.py

PURPOSE: for port reset test i.e getting cx time after disabling Wi-Fi from devices

EXAMPLE:
$ ./lf_interop_port_reset_test.py --host 192.168.1.31

NOTES:
#Currently this script will forget all network and then apply batch modify on real devices connected to LANforge
and in the end generates report which mentions cx time taken by each real client
#@TODO more script logics need to be added
"""
import sys
import os
import importlib
import argparse
import shlex
import subprocess
import json
import time
import datetime
from datetime import datetime
import pandas as pd


if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
interop_modify = importlib.import_module("py-scripts.lf_interop_modify")
lf_csv = importlib.import_module("py-scripts.lf_csv")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")


class InteropPortReset(Realm):
    def __init__(self, host,
                 dut=None,
                 ssid=None,
                 passwd=None,
                 encryp=None):
        super().__init__(lfclient_host=host,
                         lfclient_port=8080)
        self.host = host
        self.phn_name = []
        self.dut_name = dut
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryp

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
        # print("response", final)
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

    def get_last_wifi_msg(self):
        a = self.json_get("/wifi-msgs/last/1", debug_=True)
        last = a['wifi-messages']['time-stamp']
        # print(last)
        return last

    def get_time_from_wifi_msgs(self, phn_name=None, timee=None):
        # timee = self.get_last_wifi_msg()
        time.sleep(20)
        a = self.json_get("/wifi-msgs/since=time/" + str(timee), debug_=True)
        values = a['wifi-messages']
        print("values", values)
        keys_list = []
        # print(phn_name)
        # print(timee)
        # phn_name = ['RZ8RA1053HJ']

        for i in range(len(values)):
            keys_list.append(list(values[i].keys())[0])

        # print("keys_list", keys_list)
        main_dict = dict.fromkeys(phn_name)
        # print("main dict", main_dict)

        for x in phn_name:
            main_dict[x] = []
            for i, y in zip(range(len(values)), keys_list):
                b = values[i][y]['text']
                if type(b) == str:
                    variable = values[i][y]['text'].split(" ")
                    # print("variable", variable)

                    if 'Considering' in variable:
                        print("considering is present")
                        print(x)
                        if variable[0] == x:
                            dis_time = variable[2]
                            print("disconnect time ", dis_time)
                            main_dict[x].append(dis_time)
                    elif 'Trying' in variable:
                        print("trying is present")
                        print(x)
                        if variable[0] == x:
                            dis_time = variable[2]
                            print("disconnect time ", dis_time)
                            main_dict[x].append(dis_time)
                    if 'CTRL-EVENT-CONNECTED' in variable:
                        print("connect log present")
                        print(x)
                        if variable[0] == x:
                            connect_time = variable[2]
                            print("connect time", connect_time)
                            main_dict[x].append(connect_time)
                else:
                    for a in b:
                        y = a.split(" ")
                        # print(y)
                        if 'Considering' in y:
                            print("considering is present")
                            print(x)
                            if y[0] == x:
                                dis_time = y[2]
                                print("disconnect time ", dis_time)
                                main_dict[x].append(dis_time)
                        elif 'Trying' in y:
                            print("Trying is present")
                            print(x)
                            if y[0] == x:
                                dis_time = y[2]
                                print("disconnect time ", dis_time)
                                main_dict[x].append(dis_time)
                        if 'CTRL-EVENT-CONNECTED' in y:
                            print("connect log present")
                            print(x)
                            if y[0] == x:
                                connect_time = y[2]
                                print("connect time", connect_time)
                                main_dict[x].append(connect_time)




        print(main_dict)
        cx_dict = dict.fromkeys(phn_name)
        for i in phn_name:
            start_time = main_dict[i][0]
            end_time = main_dict[i][1]

            # convert time string to datetime
            t1 = datetime.strptime(start_time, "%H:%M:%S.%f")
            print('Start time:', t1.time())

            t2 = datetime.strptime(end_time, "%H:%M:%S.%f")
            print('End time:', t2.time())

            # get difference
            delta = t2 - t1

            # time difference in seconds
            print(f"Time difference is {delta.total_seconds()} seconds")
            cx_dict[i] = delta.total_seconds()
        print("cx_dict", cx_dict)
        # final cx_dict {'RZ8N70TVABP': 75.79, 'RZ8RA1053HJ': 73.554}
        return cx_dict

    def run(self):
        # start timer
        test_time = datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")
        print("Test started at ", test_time)

        # get the list of adb devices
        adb_device_list = self.get_device_details(query="name")
        print(adb_device_list)


        for i in range(len(adb_device_list)):
            self.phn_name.append(adb_device_list[i].split(".")[2])
        print("phn_name", self.phn_name)

        # check status of devices
        phantom = self.get_device_details(query="phantom")
        print(phantom)
        state = None
        for i in phantom:
            if str(i) == "False":
                print("device are up")
                state = "up"
            else:
                print("all devices are not up")
                exit(1)
        if state == "up":
            device_name = []
            # provide device name
            for i, j in zip(adb_device_list, range(len(adb_device_list))):
                device_name.append("device_" + str(int(j+1)))
                modify = interop_modify.InteropCommands(_host=self.host,
                                                        _port=8080,
                                                        device_eid=i,
                                                        set_adb_user_name=True,
                                                        adb_username="device_" + str(int(j+1)))

                modify.run()
            print("device name", device_name)
            last_time = self.get_last_wifi_msg()
            print("last_time", last_time)

            # forget network from all adb devices
            for i in adb_device_list:
                for x in range(15):
                    modify_a = interop_modify.InteropCommands(_host=self.host,
                                                              _port=8080,
                                                              device_eid=i,
                                                              ntwk_id=x,
                                                              forget_netwrk=True)
                    modify_a.run()

            for i, y in zip(adb_device_list, device_name):
                # enable and disable Wi-Fi
                print("disable wifi")
                modify_1 = interop_modify.InteropCommands(_host=self.host,
                                                          _port=8080,
                                                          device_eid=i,
                                                          wifi="disable")
                modify_1.run()

                time.sleep(5)



                # using batch modify apply ssid
                print("apply ssid using batch modify")
                modify_2 = interop_modify.InteropCommands(_host=self.host,
                                                          _port=8080,
                                                          device_eid=i,
                                                          user_name=y,
                                                          mgr_ip=self.host,
                                                          ssid=self.ssid,
                                                          passwd=self.passwd,
                                                          crypt=self.encryp,
                                                          apply=True)
                modify_2.run()

                print("enable wifi")
                modify_3 = interop_modify.InteropCommands(_host=self.host,
                                                          _port=8080,
                                                          device_eid=i,
                                                          wifi="enable")
                modify_3.run()




            time.sleep(60)
            cx_time = self.get_time_from_wifi_msgs(timee=last_time, phn_name=self.phn_name)
            print("final cx_dict", cx_time)

            test_end = datetime.now()
            test_end = test_end.strftime("%b %d %H:%M:%S")
            print("Test ended at ", test_end)
            s1 = test_time
            s2 = test_end  # for example
            FMT = '%b %d %H:%M:%S'
            test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
            return cx_time, test_duration

    def generate_report(self, cx_time=None, test_dur=None):
        report = lf_report_pdf.lf_report(_path="", _results_dir_name="Interop_port_reset_test",
                                         _output_html="port_reset_test.html",
                                         _output_pdf="port_reset_test.pdf")
        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
        test_setup_info = {
            "DUT Name": self.dut_name,
            "SSID": self.ssid,
            "Test Duration": test_dur,
        }
        report.set_title("LANforge Interop Port Reset Test")
        report.set_date(date)
        report.build_banner()
        report.set_table_title("Test Setup Information")
        report.build_table_title()

        report.test_setup_table(value="Device under test", test_setup_data=test_setup_info)
        # report.test_setup_table(value="Information", test_setup_data=test_input_info)
        # objective
        report.set_obj_html("Objective",
                            "LANforge Interop Port Reset Test is to designed to get the connection time taken by real clients after connecting to a Wi-Fi Network")
        report.build_objective()

        report.set_obj_html("Connection Time Table",
                            "The below table shows the cx time taken by real devices once after reconnecting to Wi-Fi Network")
        report.build_objective()

        user_name = self.get_device_details(query="user-name")
        cx = []
        for i in cx_time:
            cx.append(cx_time[i])

        table_1 = {
            "User Name": user_name,
            "Real Client id": self.phn_name,
            "cx time (secs)": cx,
        }
        test_setup = pd.DataFrame(table_1)
        report.set_table_dataframe(test_setup)
        report.build_table()

        test_input_infor = {
            "LANforge ip": self.host,
            "LANforge port": "8080",
            "Contact": "support@candelatech.com"
        }
        report.set_table_title("Test basic Input Information")
        report.build_table_title()
        report.test_setup_table(value="Information", test_setup_data=test_input_infor)

        report.build_footer()
        report.write_html()
        report.write_pdf_with_timestamp(_page_size='A4', _orientation='Landscape')


def main():
    desc = """ port reset test 
    run: lf_interop_port_reset_test.py --host 192.168.1.31
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--host", "--mgr", default='localhost',
                        help='specify the GUI to connect to, assumes port 8080')

    parser.add_argument("--dut", default="TestDut",
                        help='specify DUT name on which the test will be running')

    parser.add_argument("--ssid", default="Airtel_9755718444_5GHz",
                        help='specify ssid on which the test will be running')

    parser.add_argument("--passwd", default="air29723",
                        help='specify encryption password  on which the test will be running')

    parser.add_argument("--encryp", default="psk2",
                        help='specify the encryption type  on which the test will be running eg :open|psk|psk2|sae|psk2jsae')

    args = parser.parse_args()

    obj = InteropPortReset(host=args.host,
                           dut=args.dut,
                           ssid=args.ssid,
                           passwd=args.passwd,
                           encryp=args.encryp)
    cx, duration = obj.run()
    obj.generate_report(cx_time= cx, test_dur=duration)


if __name__ == '__main__':
    main()