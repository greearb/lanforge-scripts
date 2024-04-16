#!/usr/bin/env python3
"""
NAME: lf_webpage.py

PURPOSE:
lf_webpage.py will verify that N clients are connected on a specified band and can download
some amount of file data from the HTTP server while measuring the time taken by clients to download the file and number of 
times the file is downloaded.

EXAMPLE-1:
Command Line Interface to run download scenario for Real clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --ssid Cisco-5g --security wpa2 --passwd sharedsecret 
--upstream_port eth1 --duration 10m --bands 5G --client_type Real --file_size 2MB

EXAMPLE-2:
Command Line Interface to run download scenario on 5GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --fiveg_ssid Cisco-5g --fiveg_security wpa2 --fiveg_passwd sharedsecret 
--fiveg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 5G --client_type Virtual --file_size 2MB --num_stations 3

EXAMPLE-3:
Command Line Interface to run download scenario on 2.4GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --twog_ssid Cisco-2g --twog_security wpa2 --twog_passwd sharedsecret 
--twog_radio wiphy0 --upstream_port eth1 --duration 1h --bands 2.4G --client_type Virtual --file_size 2MB --num_stations 3

EXAMPLE-4:
Command Line Interface to run download scenario on 6GHz band for Virtual clients
python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --sixg_ssid Cisco-6g --sixg_security wpa3 --sixg_passwd sharedsecret 
--sixg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 6G --client_type Virtual --file_size 2MB --num_stations 3

SCRIPT_CLASSIFICATION : Test

SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

NOTES:
1.Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h.
2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
The following sentence will be displayed
Enter the desired resources to run the test:
Please enter the port numbers seperated by commas ','.
Example: 
Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

STATUS : Functional

VERIFIED_ON: 
07-SEPTEMBER-2023,
GUI Version:  5.4.6
Kernel Version: 6.2.16+

LICENSE : 
Copyright 2023 Candela Technologies Inc
Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README: False
"""

import sys
import os
import importlib
import time
import argparse
import paramiko
from datetime import datetime, timedelta
import pandas as pd
import logging
import json
from lf_graph import lf_bar_graph_horizontal


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
PortUtils = realm.PortUtils
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
from lf_interop_qos import ThroughputQOS


class HttpDownload(Realm):
    def __init__(self, lfclient_host, lfclient_port, upstream, num_sta, security, ssid, password,ap_name,
                 target_per_ten, file_size, bands, start_id=0, twog_radio=None, fiveg_radio=None,sixg_radio=None, _debug_on=False, _exit_on_error=False,
                 _exit_on_fail=False,client_type="",port_list=[],devices_list=[],macid_list=[],lf_username="lanforge",lf_password="lanforge", result_dir="", dowebgui=False, web_ui_device_list=[], test_name=None):
        self.ssid_list = []
        self.devices = []
        self.mode_list = []
        self.channel_list = []
        self.host = lfclient_host
        self.port = lfclient_port
        self.upstream = upstream
        self.num_sta = num_sta
        self.security = security
        self.ssid = ssid
        self.sta_start_id = start_id
        self.password = password
        self.twog_radio = twog_radio
        self.fiveg_radio = fiveg_radio
        self.sixg_radio = sixg_radio
        self.target_per_ten = target_per_ten
        self.file_size = file_size
        self.bands = bands
        self.debug = _debug_on
        self.port_list = port_list
        self.result_dir = result_dir
        self.test_name = test_name
        self.dowebgui = dowebgui
        self.web_ui_device_list = web_ui_device_list
        self.eid_list = []
        self.devices_list = devices_list
        self.macid_list = []
        self.client_type = client_type
        self.lf_username = lf_username
        self.lf_password = lf_password
        self.ap_name = ap_name
        self.windows_ports = []
        self.windows_eids = []
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.http_profile = self.local_realm.new_http_profile()
        self.http_profile.requests_per_ten = self.target_per_ten
        # self.http_profile.url = self.url
        self.port_util = PortUtils(self.local_realm)
        self.http_profile.debug = _debug_on
        self.created_cx = {}
        self.station_list = []
        self.radio = []

    #Todo- Make use of lf_base_interop_profile.py : Real device class to fetch available devices data
    def get_real_client_list(self):
        object=ThroughputQOS(host=self.host,
                            port=self.port,
                            number_template="0000",
                            ap_name="Netgear",
                            name_prefix="TOS-",
                            upstream=self.upstream,
                            ssid=self.ssid,
                            password=self.password,
                            security=self.security,
                            tos="BK",
                            device_list=self.web_ui_device_list
                            )
        self.port_list,self.devices_list,self.macid_list=object.phantom_check()
        for port in self.port_list:
            eid=self.name_to_eid(port)
            self.eid_list.append(str(eid[0])+'.'+str(eid[1]))
        for eid in self.eid_list:
            for device in self.devices_list:
                if ("Win" in device) and (eid + ' ' in device):
                    self.windows_eids.append(eid)

        for eid in self.windows_eids:
            for port in self.port_list:
                if eid + '.' in port:
                    self.windows_ports.append(port)
        if self.dowebgui == "True":
            if object.device_found == False:
                print("No Device is available to run the test hence aborting the testllmlml")
                df1 = pd.DataFrame([{
                    "client": [],
                    "status": "Stopped",
                    "url_data": 0
                }]
                )
                df1.to_csv('{}/http_datavalues.csv'.format(self.result_dir), index=False)
                raise ValueError("Aborting the test....")
        return self.port_list, self.devices_list, self.macid_list

    def set_values(self):
        # This method will set values according user input
        if self.bands == "5G":
            self.radio = [self.fiveg_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                            end_id_=self.num_sta - 1, padding_number_=10000,
                                                            radio=self.fiveg_radio)]
        elif self.bands == "6G":
            self.radio = [self.sixg_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                            end_id_=self.num_sta - 1, padding_number_=10000,
                                                            radio=self.sixg_radio)]
        elif self.bands == "2.4G":
            self.radio = [self.twog_radio]
            self.station_list = [LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                       end_id_=self.num_sta - 1, padding_number_=10000,
                                                       radio=self.twog_radio)]
        elif self.bands == "Both":
            self.radio = [self.twog_radio, self.fiveg_radio]
            # self.num_sta = self.num_sta // 2
            self.station_list = [
                                 LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                        end_id_=self.num_sta - 1, padding_number_=10000,
                                                        radio=self.twog_radio),
                                 LFUtils.portNameSeries(prefix_="http_sta", start_id_=self.sta_start_id,
                                                        end_id_=self.num_sta - 1, padding_number_=10000,
                                                        radio=self.fiveg_radio)
                                 ]

    def precleanup(self):
        self.count = 0
        for rad in range(len(self.radio)):
            if self.radio[rad] == self.fiveg_radio:
                # select an mode
                self.station_profile.mode = 14
                self.count = self.count + 1
            elif self.radio[rad] == self.sixg_radio:
                # select an mode
                self.station_profile.mode = 15
                self.count = self.count + 1
            elif self.radio[rad] == self.twog_radio:
                # select an mode
                self.station_profile.mode = 13
                self.count = self.count + 1

            if self.count == 2:
                self.sta_start_id = self.num_sta
                self.num_sta = 2 * (self.num_sta)
                self.station_profile.mode = 10
                self.http_profile.cleanup()
                # cleanup station list which started sta_id 20
                self.station_profile.cleanup(self.station_list[rad], debug_=self.local_realm.debug)
                LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                                   port_list=self.station_list[rad],
                                                   debug=self.local_realm.debug)
                return
            # clean dlayer4 ftp traffic
            self.http_profile.cleanup()

            # cleans stations
            self.station_profile.cleanup(self.station_list[rad], delay=1, debug_=self.local_realm.debug)
            LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                               port_list=self.station_list[rad],
                                               debug=self.local_realm.debug)
            time.sleep(1)
        print("precleanup done")

    def build(self):
        # enable http on ethernet
        self.port_util.set_http(port_name=self.local_realm.name_to_eid(self.upstream)[2],
                                resource=self.local_realm.name_to_eid(self.upstream)[1], on=True)
        if self.client_type == "Virtual":
            if self.bands == "2.4G":
                self.station_profile.mode = 13
            elif self.bands == "5G":
                self.station_profile.mode = 14
            elif self.bands == "6G":
                self.station_profile.mode = 15
            for rad in range(len(self.radio)):
                self.station_profile.use_security(self.security[rad], self.ssid[rad], self.password[rad])
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                self.station_profile.create(radio=self.radio[rad], sta_names_=self.station_list[rad], debug=self.local_realm.debug)
                self.local_realm.wait_until_ports_appear(sta_list=self.station_list[rad])
                self.station_profile.admin_up()
                if self.local_realm.wait_for_ip(self.station_list[rad], timeout_sec=60):
                    self.local_realm._pass("All stations got IPs")
                else:
                    self.local_realm._fail("Stations failed to get IPs")
                # building layer4
                self.http_profile.direction = 'dl'
                self.http_profile.dest = '/dev/null'
                data = self.local_realm.json_get("ports/list?fields=IP")

                # getting eth ip
                eid = self.local_realm.name_to_eid(self.upstream)
                for i in data["interfaces"]:
                    for j in i:
                        if "{shelf}.{resource}.{port}".format(shelf=eid[0], resource=eid[1], port=eid[2]) == j:
                            ip_upstream = i["{shelf}.{resource}.{port}".format(
                                shelf=eid[0], resource=eid[1], port=eid[2])]['ip']

                # create http profile
                self.http_profile.create(ports=self.station_profile.station_names, sleep_time=.5,
                                        suppress_related_commands_=None, http=True,user=self.lf_username, passwd=self.lf_password,
                                        http_ip=ip_upstream + "/webpage.html",proxy_auth_type=0x200,timeout = 1000)
                if self.count == 2:
                    self.station_profile.mode = 6
        else:
            if self.client_type == "Real": 
                self.http_profile.direction = 'dl'
                data = self.local_realm.json_get("ports/list?fields=IP")

                    # getting eth ip
                eid = self.local_realm.name_to_eid(self.upstream)
                for i in data["interfaces"]:
                    for j in i:
                        if "{shelf}.{resource}.{port}".format(shelf=eid[0], resource=eid[1], port=eid[2]) == j:
                            ip_upstream = i["{shelf}.{resource}.{port}".format(
                                shelf=eid[0], resource=eid[1], port=eid[2])]['ip']

                self.http_profile.create(ports=self.port_list, sleep_time=.5,
                                    suppress_related_commands_=None, http=True,interop=True,
                                    user=self.lf_username, passwd=self.lf_password,
                                    http_ip=ip_upstream + "/webpage.html",proxy_auth_type=0x200,timeout = 1000,windows_list=self.windows_ports)
                    
        print("Test Build done")

    def start(self):
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    def stop(self):
        self.http_profile.stop_cx()

    def monitor_for_runtime_csv(self, duration):

        time_now = datetime.now()
        starttime = time_now.strftime("%d/%m %I:%M:%S %p")
        # duration = self.traffic_duration
        endtime = time_now + timedelta(seconds=duration)
        end_time = endtime
        endtime = endtime.isoformat()[0:19]
        current_time = datetime.now().isoformat()[0:19]
        self.data = {}
        self.data["client"] = self.devices_list
        # self.data["url_data"] = []
        self.data_for_webui = {}
        self.data_for_webui["client"] = self.devices_list

        while (current_time < endtime):

            # data in json format
            # data = self.json_get("layer4/list?fields=bytes-rd")
            # uc_avg_data = self.json_get("layer4/list?fields=uc-avg")
            # uc_max_data = self.json_get("layer4/list?fields=uc-max")
            # uc_min_data = self.json_get("layer4/list?fields=uc-min")
            # total_url_data = self.json_get("layer4/list?fields=total-urls")
            # bytes_rd = self.json_get("layer4/list?fields=bytes-rd")

            url_times = self.my_monitor('total-urls')

            if len(url_times) == len(self.devices_list):

                self.data["status"] = ["RUNNING"] * len(self.devices_list)
                self.data["url_data"] = url_times
            else:
                self.data["status"] = ["RUNNING"] * len(self.devices_list)
                self.data["url_data"] = [0] * len(self.devices_list)
            time_difference = abs(end_time - datetime.now())
            total_hours = time_difference.total_seconds() / 3600
            remaining_minutes = (total_hours % 1) * 60
            self.data["start_time"] = [starttime] * len(self.devices_list)
            self.data["end_time"] = [end_time.strftime("%d/%m %I:%M:%S %p")] * len(self.devices_list)
            self.data["remaining_time"] = [[str(int(total_hours)) + " hr and " + str(
                int(remaining_minutes)) + " min" if int(total_hours) != 0 or int(remaining_minutes) != 0 else '<1 min'][
                                               0]] * len(self.devices_list)
            df1 = pd.DataFrame(self.data)
            df1.to_csv('{}/http_datavalues.csv'.format(self.result_dir), index=False)
            time.sleep(5)
            if self.dowebgui == "True":
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host,
                                                                                                 self.test_name),
                          'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        print('Test is stopped by the user')
                        self.data["end_time"] = [datetime.now().strftime("%d/%m %I:%M:%S %p")] * len(self.devices_list)
                        break

            current_time = datetime.now().isoformat()[0:19]

    def my_monitor(self, data_mon):
        # data in json format
        data = self.local_realm.json_get("layer4/%s/list?fields=%s" %
                                         (','.join(self.http_profile.created_cx.keys()), data_mon.replace(' ', '+')))
        # print(data)
        data1 = []
        data = data['endpoint']
        if self.client_type == "Real":
            self.num_sta = len(self.port_list)
        if self.num_sta == 1:
            data1.append(data[data_mon])
        else:
            for cx in self.http_profile.created_cx.keys():
                for info in data:
                    if cx in info:
                        data1.append(info[cx][data_mon])
        return data1

    def postcleanup(self):
        self.http_profile.cleanup()
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def file_create(self, ssh_port):
        ip = self.host
        user = "root"
        pswd = "lanforge"
        port = ssh_port
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=port, username=user, password=pswd, banner_timeout=600)
        cmd = '[ -f /usr/local/lanforge/nginx/html/webpage.html ] && echo "True" || echo "False"'
        stdin, stdout, stderr = ssh.exec_command(str(cmd))
        output = stdout.readlines()
        if output == ["True\n"]:
            cmd1 = "rm /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd1))
            output = stdout.readlines()
            time.sleep(10)
            cmd2 = "sudo fallocate -l " + self.file_size + " /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            print("File creation done", self.file_size)
            output = stdout.readlines()
        else:
            cmd2 = "sudo fallocate -l " + self.file_size + " /usr/local/lanforge/nginx/html/webpage.html"
            stdin, stdout, stderr = ssh.exec_command(str(cmd2))
            print("File creation done", self.file_size)
            output = stdout.readlines()
        ssh.close()
        time.sleep(1)
        return output

    def download_time_in_sec(self, result_data):
        self.result_data = result_data
        download_time = dict.fromkeys(result_data.keys())
        for i in download_time:
            try:
                download_time[i] = result_data[i]['dl_time']
            except BaseException:
                download_time[i] = []
        print("dl_times: ", download_time)
        lst = []
        lst1 = []
        lst2 = []
        lst3 = []
        dwnld_time = dict.fromkeys(result_data.keys())
        dataset = []
        for i in download_time:
            if i == "6G":
                print("download time[i]",download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst3.append(y)
                dwnld_time["6G"] = lst3
                dataset.append(dwnld_time["6G"])
            if i == "5G":
                print("download time[i]",download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst.append(y)
                dwnld_time["5G"] = lst
                dataset.append(dwnld_time["5G"])
            if i == "2.4G":
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst1.append(y)
                dwnld_time["2.4G"] = lst1
                dataset.append(dwnld_time["2.4G"])
            if i == "Both":
                # print("yes", download_time[i])
                for j in download_time[i]:
                    x = (j / 1000)
                    y = round(x, 1)
                    lst2.append(y)
                # print(lst2)
                dwnld_time["Both"] = lst2
                dataset.append(dwnld_time["Both"])
        return dataset

    def speed_in_Mbps(self, result_data):
        self.result_data = result_data
        speed = dict.fromkeys(result_data.keys())
        for i in speed:
            try:
                speed[i] = result_data[i]['speed']
            except BaseException:
                speed[i] = []
        lst = []
        lst1 = []
        lst2 = []
        speed_ = dict.fromkeys(result_data.keys())
        dataset = []
        for i in speed:
            if i == "5G":
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst.append(y)
                speed_["5G"] = lst
                dataset.append(speed_["5G"])
            if i == "2.4G":
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst1.append(y)
                speed_["2.4G"] = lst1
                dataset.append(speed_["2.4G"])
            if i == "Both":
                # print("yes", speed[i])
                for j in speed[i]:
                    x = (j / 1000000)
                    y = round(x, 1)
                    lst2.append(y)
                speed_["Both"] = lst2
                dataset.append(speed_["Both"])
        return dataset

    def summary_calculation(self, result_data, bands, threshold_5g, threshold_2g, threshold_both):
        self.result_data = result_data

        avg_dl_time = []
        html_struct = dict.fromkeys(list(result_data.keys()))
        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["avg"]
            for i in fcc_type:
                avg_dl_time.append(i)

        avg_dl_time_per_thou = []
        for i in avg_dl_time:
            i = i / 1000
            avg_dl_time_per_thou.append(i)

        avg_time_rounded = []
        for i in avg_dl_time_per_thou:
            i = str(round(i, 1))
            avg_time_rounded.append(i)

        pass_fail_list = []
        sumry2 = []
        sumry5 = []
        sumryB = []
        data = []

        for band in range(len(bands)):
            if bands[band] == "2.4G":
                # 2.4G
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_2g):
                    var = "FAIL"
                    pass_fail_list.append(var)
                    sumry2.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_2g):
                    pass_fail_list.append("PASS")
                    sumry2.append("PASS")
                data.append(','.join(sumry2))

            elif bands[band] == "5G":
                # 5G
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_5g):
                    print("FAIL")
                    pass_fail_list.append("FAIL")
                    sumry5.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_5g):
                    print("PASS")
                    pass_fail_list.append("PASS")
                    sumry5.append("PASS")
                data.append(','.join(sumry5))

            elif bands[band] == "Both":
                # BOTH
                if float(avg_time_rounded[band]) == 0.0 or float(avg_time_rounded[band]) > float(threshold_both):
                    var = "FAIL"
                    pass_fail_list.append(var)
                    sumryB.append("FAIL")
                elif float(avg_time_rounded[band]) < float(threshold_both):
                    pass_fail_list.append("PASS")
                    sumryB.append("PASS")
                data.append(','.join(sumryB))

        return data

    def check_station_ip(self):
        pass

    def generate_graph(self, dataset, lis, bands):
        if self.client_type == "Real":
            lis=self.devices_list
        elif self.client_type == "Virtual":
            lis=self.station_list[0]
        print(dataset,lis)
        x_fig_size = 18
        y_fig_size = len(lis)*.5 + 4
        # graph = lf_graph.lf_bar_graph(_data_set=dataset, _xaxis_name="Stations", _yaxis_name="Time in Seconds",
        #                               _xaxis_categories=lis, _label=bands, _xticks_font=8,
        #                               _graph_image_name="webpage download time graph",
        #                               _color=['forestgreen', 'darkorange', 'blueviolet'], _color_edge='black', _figsize=(14, 5),
        #                               _grp_title="Download time taken by each client", _xaxis_step=1, _show_bar_value=True,
        #                               _text_font=6, _text_rotation=60,
        #                               _legend_loc="upper right",
        #                               _legend_box=(1, 1.15),
        #                               _enable_csv=True
        #                               )
        graph = lf_bar_graph_horizontal(_data_set=[dataset], _xaxis_name="Average time taken to Download file in ms",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in lis],
                                            _yaxis_label=[i for i in lis],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="Average time taken to Download file",
                                            _title_size=16,
                                            _figsize= (x_fig_size,y_fig_size),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['steelblue'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="ucg-avg", _color_edge=['black'],
                                            _color=['steelblue'],
                                            _label=bands)
        graph_png = graph.build_bar_graph_horizontal()
        print("graph name {}".format(graph_png))
        return graph_png

    def graph_2(self, dataset2, lis, bands):
        if self.client_type == "Real":
            lis = self.devices_list
        elif self.client_type == "Virtual":
            lis = self.station_list[0]
        print(dataset2)
        print(lis)
        x_fig_size = 18
        y_fig_size = len(lis)*.5 + 4
        graph_2 = lf_bar_graph_horizontal(_data_set=[dataset2], _xaxis_name="No of times file Download",
                                            _yaxis_name="Client names",
                                            _yaxis_categories=[i for i in lis],
                                            _yaxis_label=[i for i in lis],
                                            _yaxis_step=1,
                                            _yticks_font=8,
                                            _yticks_rotation=None,
                                            _graph_title="No of times file Download (Count)",
                                            _title_size=16,
                                            _figsize= (x_fig_size,y_fig_size),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _color_name=['orange'],
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _graph_image_name="Total-url", _color_edge=['black'],
                                            _color=['orange'],
                                            _label=bands)
        graph_png = graph_2.build_bar_graph_horizontal()
        return graph_png

    def generate_report(self, date, num_stations, duration, test_setup_info, dataset, lis, bands, threshold_2g,
                        threshold_5g, threshold_both, dataset2,dataset1, #summary_table_value,
                        result_data, test_rig,
                        test_tag, dut_hw_version, dut_sw_version, dut_model_num, dut_serial_num, test_id,
                        test_input_infor, csv_outfile, _results_dir_name='webpage_test', report_path=''):
        if self.dowebgui == "True" and report_path == '':
            report = lf_report.lf_report(_results_dir_name="webpage_test", _output_html="Webpage.html",
                                         _output_pdf="Webpage.pdf", _path=self.result_dir)
        else:
            report = lf_report.lf_report(_results_dir_name="webpage_test", _output_html="Webpage.html",
                                         _output_pdf="Webpage.pdf", _path=report_path)

        if bands == "Both":
            num_stations = num_stations * 2
        report.set_title("HTTP DOWNLOAD TEST")
        report.set_date(date)
        report.build_banner()
        report.set_table_title("Test Setup Information")
        report.build_table_title()

        report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        report.set_obj_html("Objective", "The Webpage Download Test is designed to verify that N clients connected on specified band can "
                                 "download some amount of file from HTTP server and measures the "
                                 "time taken by the client to Download the file.")
        report.build_objective()
        report.set_obj_html("No of times file Downloads","The below graph represents number of times a file downloads for each client"
                            ". X- axis shows “No of times file downloads and Y-axis shows "
                            "Client names.")
        report.build_objective()
        graph2 = self.graph_2(dataset2, lis=lis, bands=bands)
        print("graph name {}".format(graph2))
        report.set_graph_image(graph2)
        report.set_csv_filename(graph2)
        report.move_csv_file()
        report.move_graph_image()
        report.build_graph()
        report.set_obj_html("Average time taken to download file ","The below graph represents average time taken to download for each client  "
                            ".  X- axis shows “Average time taken to download a file ” and Y-axis shows "
                            "Client names.")
        report.build_objective()
        graph = self.generate_graph(dataset=dataset, lis=lis, bands=bands)
        report.set_graph_image(graph)
        report.set_csv_filename(graph)
        report.move_csv_file()
        report.move_graph_image()
        report.build_graph()

        # report.set_obj_html("Summary Table Description", "This Table shows you the summary "
        #                     "result of Webpage Download Test as PASS or FAIL criteria. If the average time taken by " +
        #                     str(num_stations) + " clients to access the webpage is less than " + str( threshold_2g) +
        #                     "s it's a PASS criteria for 2.4 ghz clients, If the average time taken by " + "" +
        #                     str( num_stations) + " clients to access the webpage is less than " + str( threshold_5g) +
        #                     "s it's a PASS criteria for 5 ghz clients and If the average time taken by " + str( num_stations) +
        #                     " clients to access the webpage is less than " + str(threshold_both) +
        #                     "s it's a PASS criteria for 2.4 ghz and 5ghz clients")

        # report.build_objective()
        #test_setup1 = pd.DataFrame(summary_table_value)
        #report.set_table_dataframe(test_setup1)
        #report.build_table()

        report.set_obj_html("Download Time Table Description", "This Table will provide you information of the "
                             "minimum, maximum and the average time taken by clients to download a webpage in seconds")

        report.build_objective()
        self.response_port = self.local_realm.json_get("/port/all")
        #print(response_port)
        print("port list",self.port_list)
        if self.client_type == "Real":
            self.devices = self.devices_list
            for interface in self.response_port['interfaces']:
                for port,port_data in interface.items():
                    if port in self.port_list:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.ssid_list.append(str(port_data['ssid']))
        elif self.client_type == "Virtual":
            self.devices = self.station_list[0]
            for interface in self.response_port['interfaces']:
                for port, port_data in interface.items():
                    if port in self.station_list[0]:
                        self.channel_list.append(str(port_data['channel']))
                        self.mode_list.append(str(port_data['mode']))
                        self.macid_list.append(str(port_data['mac']))
                        self.ssid_list.append(str(port_data['ssid']))

        x = []
        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["min"]
            # print(fcc_type)
            for i in fcc_type:
                x.append(i)
            # print(x)
        y = []
        for i in x:
            i = i / 1000
            y.append(i)
        z = []
        for i in y:
            i = str(round(i, 1))
            z.append(i)
        # rint(z)
        x1 = []

        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["max"]
            # print(fcc_type)
            for i in fcc_type:
                x1.append(i)
            # print(x1)
        y1 = []
        for i in x1:
            i = i / 1000
            y1.append(i)
        z1 = []
        for i in y1:
            i = str(round(i, 1))
            z1.append(i)
        # print(z1)
        x2 = []

        for fcc in list(result_data.keys()):
            fcc_type = result_data[fcc]["avg"]
            # print(fcc_type)
            for i in fcc_type:
                x2.append(i)
            # print(x2)
        y2 = []
        for i in x2:
            i = i / 1000
            y2.append(i)
        z2 = []
        for i in y2:
            i = str(round(i, 1))
            z2.append(i)

        download_table_value = {
            "Band": bands,
            "Minimum": z,
            "Maximum": z1,
            "Average": z2
        }

        # Get the report path to create the kpi.csv path
        kpi_path = report.get_report_path()
        print("kpi_path :{kpi_path}".format(kpi_path=kpi_path))

        kpi_csv = lf_kpi_csv.lf_kpi_csv(
            _kpi_path=kpi_path,
            _kpi_test_rig=test_rig,
            _kpi_test_tag=test_tag,
            _kpi_dut_hw_version=dut_hw_version,
            _kpi_dut_sw_version=dut_sw_version,
            _kpi_dut_model_num=dut_model_num,
            _kpi_dut_serial_num=dut_serial_num,
            _kpi_test_id=test_id)
        kpi_csv.kpi_dict['Units'] = "Mbps"
        for band in range(len(download_table_value["Band"])):
            kpi_csv.kpi_csv_get_dict_update_time()
            kpi_csv.kpi_dict['Graph-Group'] = "Webpage Download {band}".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Minimum".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=download_table_value['Minimum'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Maximum".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=download_table_value['Maximum'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)
            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Average".format(
                band=download_table_value['Band'][band])
            kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=download_table_value['Average'][band])
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

        if csv_outfile is not None:
            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            csv_outfile = "{}_{}-test_l3_longevity.csv".format(
                csv_outfile, current_time)
            csv_outfile = report.file_add_path(csv_outfile)
            print("csv output file : {}".format(csv_outfile))

        test_setup = pd.DataFrame(download_table_value)
        report.set_table_dataframe(test_setup)
        report.build_table()
        report.set_table_title("Overall Results")
        report.build_table_title()
        dataframe = {
                        " Clients" : self.devices,
                        " MAC " : self.macid_list,
                        " Channel" : self.channel_list,
                        " SSID " : self.ssid_list,
                        " Mode" : self.mode_list,
                        " No of times File downloaded " : dataset2,
                        " Average time taken to Download file (ms)" : dataset,
                        " Bytes-rd (Mega Bytes) " : dataset1
                    }
        dataframe1 = pd.DataFrame(dataframe)
        report.set_table_dataframe(dataframe1)
        report.build_table()
        report.build_footer()
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)
        report.write_pdf()


def main():
    # set up logger
    logger_config = lf_logger_config.lf_logger_config()
    parser = argparse.ArgumentParser(
        prog="lf_webpage.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
    NAME: lf_webpage.py

    PURPOSE:
    lf_webpage.py will verify that N clients are connected on a specified band and can download
    some amount of file data from the HTTP server while measuring the time taken by clients to download the file and number of 
    times the file is downloaded.

    EXAMPLE-1:
    Command Line Interface to run download scenario for Real clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --ssid Cisco-5g --security wpa2 --passwd sharedsecret 
    --upstream_port eth1 --duration 10m --bands 5G --client_type Real --file_size 2MB

    EXAMPLE-2:
    Command Line Interface to run download scenario on 5GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --fiveg_ssid Cisco-5g --fiveg_security wpa2 --fiveg_passwd sharedsecret 
    --fiveg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 5G --client_type Virtual --file_size 2MB --num_stations 3

    EXAMPLE-3:
    Command Line Interface to run download scenario on 2.4GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --twog_ssid Cisco-2g --twog_security wpa2 --twog_passwd sharedsecret 
    --twog_radio wiphy0 --upstream_port eth1 --duration 1h --bands 2.4G --client_type Virtual --file_size 2MB --num_stations 3

    EXAMPLE-4:
    Command Line Interface to run download scenario on 6GHz band for Virtual clients
    python3 lf_webpage.py --ap_name "Cisco" --mgr 192.168.200.165 --sixg_ssid Cisco-6g --sixg_security wpa3 --sixg_passwd sharedsecret 
    --sixg_radio wiphy0 --upstream_port eth1 --duration 1h --bands 6G --client_type Virtual --file_size 2MB --num_stations 3

    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

    NOTES:
    1.Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h.
    2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
    The following sentence will be displayed
    Enter the desired resources to run the test:
    Please enter the port numbers seperated by commas ','.
    Example: 
    Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

    STATUS : Functional

    VERIFIED_ON: 
    07-SEPTEMBER-2023,
    GUI Version:  5.4.6
    Kernel Version: 6.2.16+

    LICENSE : 
    Copyright 2023 Candela Technologies Inc
    Free to distribute and modify. LANforge systems must be licensed.

    INCLUDE_IN_README: False   
        
        ''')
    required = parser.add_argument_group('Required arguments to run lf_webpage.py')
    optional = parser.add_argument_group('Optional arguments to run lf_webpage.py')

    required.add_argument('--mgr', help='hostname for where LANforge GUI is running', default='localhost')
    required.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on', default=8080)
    required.add_argument('--upstream_port', help='non-station port that generates traffic: eg: eth1', default='eth2')
    optional.add_argument('--num_stations', type=int, help='number of stations to create for virtual clients', default=0)
    optional.add_argument('--twog_radio', help='specify radio for 2.4G clients', default='wiphy3')
    optional.add_argument('--fiveg_radio', help='specify radio for 5 GHz client', default='wiphy0')
    optional.add_argument('--sixg_radio', help='Specify radio for 6GHz client',default='wiphy2')
    optional.add_argument('--twog_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 2.4G clients')
    optional.add_argument('--twog_ssid', help='WiFi SSID for script object to associate for 2.4G clients')
    optional.add_argument('--twog_passwd', help='WiFi passphrase/password/key for 2.4G clients')
    optional.add_argument('--fiveg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 5G clients')
    optional.add_argument('--fiveg_ssid', help='WiFi SSID for script object to associate for 5G clients')
    optional.add_argument('--fiveg_passwd', help='WiFi passphrase/password/key for 5G clients')
    optional.add_argument('--sixg_security', help='WiFi Security protocol: {open|wep|wpa2|wpa3} for 2.4G clients')
    optional.add_argument('--sixg_ssid', help='WiFi SSID for script object to associate for 2.4G clients')
    optional.add_argument('--sixg_passwd', help='WiFi passphrase/password/key for 2.4G clients')
    optional.add_argument('--target_per_ten', help='number of request per 10 minutes', default=100)
    required.add_argument('--file_size', type=str, help='specify the size of file you want to download', default='5MB')
    required.add_argument('--bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                        default=["5G", "2.4G", "6G"])
    required.add_argument('--duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    required.add_argument('--client_type', help='Enter the type of client. Example:"Real","Virtual"')
    optional.add_argument('--threshold_5g', help="Enter the threshold value for 5G Pass/Fail criteria", default="60")
    optional.add_argument('--threshold_2g', help="Enter the threshold value for 2.4G Pass/Fail criteria", default="90")
    optional.add_argument('--threshold_both', help="Enter the threshold value for Both Pass/Fail criteria", default="50")
    required.add_argument('--ap_name', help="specify the ap model ", default="TestAP")
    optional.add_argument('--lf_username',help="Enter the lanforge user name. Example : 'lanforge' ", default= "lanforge")
    optional.add_argument('--lf_password',help="Enter the lanforge password. Example : 'lanforge' ",default="lanforge")
    optional.add_argument('--ssh_port', type=int, help="specify the ssh port eg 22", default=22)
    optional.add_argument("--test_rig", default="", help="test rig for kpi.csv, testbed that the tests are run on")
    optional.add_argument("--test_tag", default="",
                        help="test tag for kpi.csv,  test specific information to differentiate the test")
    optional.add_argument("--dut_hw_version", default="",
                        help="dut hw version for kpi.csv, hardware version of the device under test")
    optional.add_argument("--dut_sw_version", default="",
                        help="dut sw version for kpi.csv, software version of the device under test")
    optional.add_argument("--dut_model_num", default="",
                        help="dut model for kpi.csv,  model number / name of the device under test")
    optional.add_argument("--dut_serial_num", default="",
                        help="dut serial for kpi.csv, serial number / serial number of the device under test")
    optional.add_argument("--test_priority", default="", help="dut model for kpi.csv,  test-priority is arbitrary number")
    optional.add_argument("--test_id", default="lf_webpage", help="test-id for kpi.csv,  script or test name")
    optional.add_argument('--csv_outfile', help="--csv_outfile <Output file for csv data>", default="")
    #ARGS for webGUI
    required.add_argument('--dowebgui', help="If true will execute script for webgui", default=False)  # FOR WEBGUI
    optional.add_argument('--result_dir',
                          help='Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>',
                          default='')
    optional.add_argument('--web_ui_device_list',
                          help='Enter the devices on which the test should be run <Do not use in CLI,--used by webui>',
                          default=[])
    optional.add_argument('--test_name',
                          help='Specify test name to store the runtime csv results <Do not use in CLI, --used by webui>',
                          default=None)
    args = parser.parse_args()
    args.bands.sort()

    # Error checking to prevent case issues
    for band in range(len(args.bands)):
        args.bands[band] = args.bands[band].upper()
        if args.bands[band] == "BOTH":
            args.bands[band] = "Both"

    # Error checking for non-existent bands
    valid_bands = ['2.4G', '5G', '6G', 'Both']
    for band in args.bands:
        if band not in valid_bands:
            raise ValueError("Invalid band '%s' used in bands argument!" % band)

    # Check for Both being used independently
    if len(args.bands) > 1 and "Both" in args.bands:
        raise ValueError("'Both' test type must be used independently!")

    if args.duration.endswith('s') or args.duration.endswith('S'):
        args.duration = int(args.duration[0:-1])
    elif args.duration.endswith('m') or args.duration.endswith('M'):
        args.duration = int(args.duration[0:-1]) * 60
    elif args.duration.endswith('h') or args.duration.endswith('H'):
        args.duration = int(args.duration[0:-1]) * 60 * 60
    elif args.duration.endswith(''):
        args.duration = int(args.duration)

    list6G,list6G_bytes,list6G_speed,list6G_urltimes = [],[],[],[]
    list5G,list5G_bytes,list5G_speed,list5G_urltimes = [],[],[],[]
    list2G,list2G_bytes,list2G_speed,list2G_urltimes = [],[],[],[]
    Both,Both_bytes,Both_speed,Both_urltimes = [],[],[],[]
    real_data=[]
    dict_keys = []
    dict_keys.extend(args.bands)
    # print(dict_keys)
    final_dict = dict.fromkeys(dict_keys)
    # print(final_dict)
    dict1_keys = ['dl_time', 'min', 'max', 'avg', 'bytes_rd', 'speed','url_times']
    for i in final_dict:
        final_dict[i] = dict.fromkeys(dict1_keys)
    print(final_dict)
    min6 = []
    min5 = []
    min2 = []
    min_both = []
    max6 = []
    max5 = []
    max2 = []
    max_both = []
    avg6 = []
    avg2 = []
    avg5 = []
    avg_both = []
    port_list,device_list,macid_list = [],[],[]
    for bands in args.bands:
        if bands == "2.4G":
            security = [args.twog_security]
            ssid = [args.twog_ssid]
            passwd = [args.twog_passwd]
        elif bands == "5G":
            security = [args.fiveg_security]
            ssid = [args.fiveg_ssid]
            passwd = [args.fiveg_passwd]
        elif bands == "6G":
            security = [args.sixg_security]
            ssid = [args.sixg_ssid]
            passwd = [args.sixg_passwd]
        elif bands == "Both":
            security = [args.twog_security, args.fiveg_security]
            ssid = [args.twog_ssid, args.fiveg_ssid]
            passwd = [args.twog_passwd, args.fiveg_passwd]
        http = HttpDownload(lfclient_host=args.mgr, lfclient_port=args.mgr_port,
                            upstream=args.upstream_port, num_sta=args.num_stations,
                            security=security,ap_name=args.ap_name,
                            ssid=ssid, password=passwd,
                            target_per_ten=args.target_per_ten,
                            file_size=args.file_size, bands=bands,
                            twog_radio=args.twog_radio,
                            fiveg_radio=args.fiveg_radio,
                            sixg_radio=args.sixg_radio,
                            client_type=args.client_type,
                            lf_username=args.lf_username,lf_password=args.lf_password,
                            result_dir=args.result_dir,  # FOR WEBGUI
                            dowebgui=args.dowebgui,  # FOR WEBGUI
                            web_ui_device_list=args.web_ui_device_list,  # FOR WEBGUI
                            test_name=args.test_name,  # FOR WEBGUI
                            )
        if args.client_type == "Real":
            port_list,device_list,macid_list = http.get_real_client_list()
            args.num_stations = len(port_list)
        http.file_create(ssh_port=args.ssh_port)
        http.set_values()
        http.precleanup()
        http.build()
        test_time = datetime.now()
        #Solution For Leap Year conflict changed it to %Y
        test_time = test_time.strftime("%Y %d %H:%M:%S")
        print("Test started at ", test_time)
        http.start()
        if args.dowebgui:
            # FOR WEBGUI, -This fumction is called to fetch the runtime data from layer-4
            http.monitor_for_runtime_csv(args.duration)
        else:
            time.sleep(args.duration)
        http.stop()
        uc_avg_val = http.my_monitor('uc-avg')
        url_times = http.my_monitor('total-urls')
        rx_bytes_val = http.my_monitor('bytes-rd')
        rx_rate_val = http.my_monitor('rx rate')
        if args.dowebgui:
            http.data_for_webui["url_data"] = url_times  # storing the layer-4 url data at the end of test

        if bands == "5G":
            list5G.extend(uc_avg_val)
            list5G_bytes.extend(rx_bytes_val)
            list5G_speed.extend(rx_rate_val)
            list5G_urltimes.extend(url_times)
            print(list5G,list5G_bytes,list5G_speed,list5G_urltimes)
            final_dict['5G']['dl_time'] = list5G
            min5.append(min(list5G))
            final_dict['5G']['min'] = min5
            max5.append(max(list5G))
            final_dict['5G']['max'] = max5
            avg5.append((sum(list5G) / args.num_stations))
            final_dict['5G']['avg'] = avg5
            final_dict['5G']['bytes_rd'] = list5G_bytes
            final_dict['5G']['speed'] = list5G_speed
            final_dict['5G']['url_times'] = list5G_urltimes
        elif bands == "6G":
            list6G.extend(uc_avg_val)
            list6G_bytes.extend(rx_bytes_val)
            list6G_speed.extend(rx_rate_val)
            list6G_urltimes.extend(url_times)
            final_dict['6G']['dl_time'] = list6G
            min6.append(min(list6G))
            final_dict['6G']['min'] = min6
            max6.append(max(list6G))
            final_dict['6G']['max'] = max6
            avg6.append((sum(list6G) / args.num_stations))
            final_dict['6G']['avg'] = avg6
            final_dict['6G']['bytes_rd'] = list6G_bytes
            final_dict['6G']['speed'] = list6G_speed
            final_dict['6G']['url_times'] = list6G_urltimes
        elif bands == "2.4G":
            list2G.extend(uc_avg_val)
            list2G_bytes.extend(rx_bytes_val)
            list2G_speed.extend(rx_rate_val)
            list2G_urltimes.extend(url_times)
            print(list2G,list2G_bytes,list2G_speed)
            final_dict['2.4G']['dl_time'] = list2G
            min2.append(min(list2G))
            final_dict['2.4G']['min'] = min2
            max2.append(max(list2G))
            final_dict['2.4G']['max'] = max2
            avg2.append((sum(list2G) / args.num_stations))
            final_dict['2.4G']['avg'] = avg2
            final_dict['2.4G']['bytes_rd'] = list2G_bytes
            final_dict['2.4G']['speed'] = list2G_speed
            final_dict['2.4G']['url_times'] = list2G_urltimes
        elif bands == "Both":
            Both.extend(uc_avg_val)
            Both_bytes.extend(rx_bytes_val)
            Both_speed.extend(rx_rate_val)
            Both_urltimes.extend(url_times)
            final_dict['Both']['dl_time'] = Both
            min_both.append(min(Both))
            final_dict['Both']['min'] = min_both
            max_both.append(max(Both))
            final_dict['Both']['max'] = max_both
            avg_both.append((sum(Both) / args.num_stations))
            final_dict['Both']['avg'] = avg_both
            final_dict['Both']['bytes_rd'] = Both_bytes
            final_dict['Both']['speed'] = Both_speed
            final_dict['Both']['url_times'] = Both_urltimes

    result_data = final_dict
    print("result", result_data)
    print("Test Finished")
    test_end = datetime.now()
    test_end = test_end.strftime("%Y %d %H:%M:%S")
    print("Test ended at ", test_end)
    s1 = test_time
    s2 = test_end  # for example
    FMT = '%Y %d %H:%M:%S'
    test_duration = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

    info_ssid = []
    info_security = []
    for band in args.bands:
        if band == "2.4G":
            info_ssid.append(args.twog_ssid)
            info_security.append(args.twog_security)
        elif band == "5G":
            info_ssid.append(args.fiveg_ssid)
            info_security.append(args.fiveg_security)
        elif band == "6G":
            info_ssid.append(args.sixg_ssid)
            info_security.append(args.sixg_security)
        elif band == "Both":
            info_ssid.append(args.fiveg_ssid)
            info_security.append(args.fiveg_security)
            info_ssid.append(args.twog_ssid)
            info_security.append(args.twog_security)

    print("total test duration ", test_duration)
    date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    duration = args.duration
    if int(duration) < 60 :
        duration = str(duration) + "s"
    elif int(duration == 60) or (int(duration) > 60 and int(duration) < 3600) :
        duration = str(duration/60) + "m"
    else:
        if int(duration == 3600) or (int(duration) > 3600):
            duration = str(duration/3600) + "h"

    test_setup_info = {
        "AP Name": args.ap_name,
        "SSID": ssid,
        "Security" : security,
        "No of Devices" : args.num_stations,
        "File size" : args.file_size,
        "File location" : "/usr/local/lanforge/nginx/html",
        "Traffic Direction" : "Download",
        "Traffic Duration ": duration
    }
    test_input_infor = {
        "LANforge ip": args.mgr,
        "File Size": args.file_size,
        "Bands": args.bands,
        "Upstream": args.upstream_port,
        "Stations": args.num_stations,
        "SSID": ','.join(info_ssid),
        "Security": ', '.join(info_security),
        "Duration": args.duration,
        "Contact": "support@candelatech.com"
    }

    #dataset = http.download_time_in_sec(result_data=result_data)
    for i in result_data:
        dataset = result_data[i]['dl_time']
        dataset2 = result_data[i]['url_times']
        bytes_rd = result_data[i]['bytes_rd']
    dataset1 = [float(f"{(i / 1000000): .4f}") for i in bytes_rd]
    lis = []
    if bands == "Both":
        for i in range(1, args.num_stations*2 + 1):
            lis.append(i)
    else:
        for i in range(1, args.num_stations + 1):
            lis.append(i)

    #dataset2 = http.speed_in_Mbps(result_data=result_data)

    #data = http.summary_calculation(
        # result_data=result_data,
        # bands=args.bands,
        # threshold_5g=args.threshold_5g,
        # threshold_2g=args.threshold_2g,
        # threshold_both=args.threshold_both)
    #summary_table_value = {
        #"": args.bands,
        #"PASS/FAIL": data
    #}
    http.generate_report(date, num_stations=args.num_stations,
                          duration=args.duration, test_setup_info=test_setup_info, dataset=dataset, lis=lis,
                          bands=args.bands, threshold_2g=args.threshold_2g, threshold_5g=args.threshold_5g,
                          threshold_both=args.threshold_both, dataset2=dataset2,dataset1=dataset1,
                          #summary_table_value=summary_table_value, 
                          result_data=result_data,
                          test_rig=args.test_rig, test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                          dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                          dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                          test_input_infor=test_input_infor, csv_outfile=args.csv_outfile)
    http.postcleanup()
    # FOR WEBGUI, filling csv at the end to get the last terminal logs
    if args.dowebgui:
        http.data_for_webui["status"] = ["STOPPED"] * len(http.devices_list)
        http.data_for_webui["start_time"] = http.data["start_time"]
        http.data_for_webui["end_time"] = http.data["end_time"]
        http.data_for_webui["remaining_time"] = http.data["remaining_time"]
        df1 = pd.DataFrame(http.data_for_webui)
        df1.to_csv('{}/http_datavalues.csv'.format(http.result_dir), index=False)

if __name__ == '__main__':
    main()