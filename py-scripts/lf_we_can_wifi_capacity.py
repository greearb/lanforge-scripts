#!/usr/bin/env python3

"""
NAME: lf_we_can_wifi_capacity_test.py

PURPOSE:
    This program is used for running Wi-Fi capacity test on real clients (Phones).
    The class will generate an output directory based on date and time in the /home/lanforge/html-reports/ .

example: python3 lf_we_can_wifi_capacity.py --mgr 192.168.200.232 --port 8080 --upstream 1.1.eth1 --batch_size 2
--duration 300000 --download_rate 210Mbps --upload_rate 210Mbps --protocol UDP-IPv4 --dut_model NETGEAR1287
--ssid_dut_2g NETGEAR_2.4G  --ssid_dut_5g NETGEAR_5G --lf_user lanforge --lf_password lanforge

Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

    WE-CAN app should be installed on the phone and should be Connected to lanforge server.

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2021 Candela Technologies Inc

"""
import importlib
import os
import sys
import glob
import shutil
import math
import time
import argparse
import time
import logging

import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import argparse
from lf_report import lf_report

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test
cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph = lf_graph.lf_bar_graph
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
from lf_wifi_capacity_test import WiFiCapacityTest

#Class to trigger Wi-Fi capacity test for real clients
class WeCanWiFiCapacityTest(cv_test):
    def __init__(self,
                 lfclient_host="localhost",
                 lf_port=8080,
                 ssh_port=22,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="wct_instance",
                 config_name="wifi_config",
                 upstream="eth1",
                 batch_size="1",
                 loop_iter="1",
                 protocol="UDP-IPv4",
                 duration="5000",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_rate="10Mbps",
                 download_rate="1Gbps",
                 sort="interleave",
                 stations="",
                 create_stations=False,
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 influx_host="localhost",
                 influx_port=8086,
                 report_dir="",
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 local_lf_report_dir=""
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []
        self.lfclient_host = lfclient_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.station_profile = self.new_station_profile()
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "WiFi Capacity"
        self.batch_size = batch_size
        self.loop_iter = loop_iter
        self.protocol = protocol
        self.duration = duration
        self.upload_rate = upload_rate
        self.download_rate = download_rate
        self.upstream = upstream
        self.sort = sort
        self.stations = stations
        self.create_stations = create_stations
        self.ssh_port = ssh_port
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.influx_host = influx_host,
        self.influx_port = influx_port
        self.report_dir = report_dir
        self.graph_groups = graph_groups
        self.test_rig = test_rig
        self.test_tag = test_tag
        self.local_lf_report_dir = local_lf_report_dir
        self.lf_query_ports = super().json_get("/port/all")

    def setup(self):
        if self.create_stations and self.stations != "":
            sta = self.stations.split(",")
            self.station_profile.cleanup(sta)
            logger.info("stations created")

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = []
        eid = LFUtils.name_to_eid(self.upstream)
        port = "%i.%i.%s" % (eid[0], eid[1], eid[2])
        port_list = [port]
        
        #validating port manager tab to select interop devices only
        print("\n Now validating Port manager ports \n")
        temp=-1
        for i in [self.lf_query_ports['interfaces']]:
            for [j] in i:
                temp+=1
                #print(j)
                #print(i[temp][j])
                if(i[temp][j]["alias"]=='wlan0' or i[temp][j]["alias"]=='wlan1' and i[temp][j]["port type"]=='WIFI-STA' and i[temp][j]["phantom"] is False and i[temp][j]["down"] is False):
                    port_list.append(j)
        idx = 0
        for eid in port_list:
            add_port = "sel_port-" + str(idx) + ": " + eid
            print("add-port",add_port)
            self.create_test_config(self.config_name, "Wifi-Capacity-", add_port)
            idx += 1

        self.apply_cfg_options(cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        if self.batch_size != "":
            cfg_options.append("batch_size: " + self.batch_size)
        if self.loop_iter != "":
            cfg_options.append("loop_iter: " + self.loop_iter)
        if self.protocol != "":
            cfg_options.append("protocol: " + str(self.protocol))
        if self.duration != "":
            cfg_options.append("duration: " + self.duration)
        if self.upload_rate != "":
            cfg_options.append("ul_rate: " + self.upload_rate)
        if self.download_rate != "":
            cfg_options.append("dl_rate: " + self.download_rate)
        if self.test_rig != "":
            cfg_options.append("test_rig: " + self.test_rig)
        if self.test_tag != "":
            cfg_options.append("test_tag: " + self.test_tag)

        cfg_options.append("save_csv: 1")

        blob_test = "Wifi-Capacity-"

        # We deleted the scenario earlier, now re-build new one line at a time.
        self.build_cfg(self.config_name, blob_test, cfg_options)

        cv_cmds = []

        if self.sort == 'linear':
            cmd = "cv click '%s' 'Linear Sort'" % self.instance_name
            cv_cmds.append(cmd)
        if self.sort == 'interleave':
            cmd = "cv click '%s' 'Interleave Sort'" % self.instance_name
            cv_cmds.append(cmd)

        self.create_and_run_test(self.load_old_cfg, self.test_name, self.instance_name,
                                 self.config_name, self.sets,
                                 self.pull_report, self.lfclient_host, self.lf_user, self.lf_password,
                                 cv_cmds, ssh_port=self.ssh_port, graph_groups_file=self.graph_groups, local_lf_report_dir=self.local_lf_report_dir)

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name

        self.rm_text_blob(self.config_name, "Wifi-Capacity-")  # To delete old config with same name



class LfInteropWifiCapacity(Realm):
    def __init__(self,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=None,
                 upstream=None,
                 radio=None,
                 protocol=None,
                 host="localhost",
                 port=8080,
                 inp_download_rate=None,
                 inp_upload_rate=None,
                 batch_size=None,
                 dut_model=None,
                 ssid_dut_2g=None,
                 ssid_dut_5g=None,
                 duration=None,
                 resource=1,
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        if sta_list is None:
            sta_list = []
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.ssid_dut_2g = ssid_dut_2g
        self.ssid_dut_5g = ssid_dut_5g
        self.dut_model = dut_model
        self.protocol = protocol,
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.radio = radio
        self.inp_download_rate = inp_download_rate
        self.inp_upload_rate = inp_upload_rate
        self.batch_size = batch_size
        self.duration = duration
        self.debug = _debug_on
        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160

    def get_folder_name(self):
        cwd = os.getcwd()
        list_of_files = glob.glob(cwd + "/*")  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def get_data(self):
        resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate, signal, ssid, channel, phone_radio_bandwidth \
            = self.get_resource_data()
        folder_directory = self.get_folder_name()
        rx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in rx_rate]
        tx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in tx_rate]
        print(resource_id_real, "\n", phone_name, "\n", mac_address, "\n", user_name, "\n", phone_radio,
              "\n", rx_rate, "\n", tx_rate)
        dataframe = pd.read_csv(folder_directory + "/csv-data/data-Combined_Mbps__60_second_running_average-1.csv",
                                header=1)
        print(dataframe)
        udp_download_rate = []
        tcp_download_rate = []
        udp_upload_rate = []
        tcp_upload_rate = []
        download_rate = []
        upload_rate = []
        resource_id = []
        if self.protocol[0] == "TCP and UDP IPv4":
            for column in dataframe:
                # for each resource id getting upload and Download Data
                resource_id.append(column.split('.')[0])
                if not math.isnan(dataframe[column].loc[0]):
                    udp_download_rate.append(float("{:.2f}".format(dataframe[column].loc[0])))
                    tcp_download_rate.append(float("{:.2f}".format(dataframe[column].loc[1])))
                    udp_upload_rate.append(float("{:.2f}".format(dataframe[column].loc[2])))
                    tcp_upload_rate.append(float("{:.2f}".format(dataframe[column].loc[3])))
            # Plotting Graph 01
            rx_tx_df = pd.DataFrame({
                "udp upload": udp_upload_rate,
                "tcp upload": tcp_upload_rate,
                "udp download": udp_download_rate,
                "tcp download": tcp_download_rate,
            }, index=[i for i in phone_name])

            # Plotting Graph 03
            ap_signal_df = pd.DataFrame({
                "Signal ": signal,
                "Device": phone_name,
            }, index=[str("( " + phone_radio[i] + " )") for i in range(len(phone_name))])

            udp_actual_rate = [float("{:.2f}".format(udp_download_rate[i] + udp_upload_rate[i])) for i in
                               range(len(udp_download_rate))]
            tcp_actual_rate = [float("{:.2f}".format(tcp_download_rate[i] + tcp_upload_rate[i])) for i in
                               range(len(udp_download_rate))]
            print(udp_actual_rate, "\n", tcp_actual_rate, "\n", rx_rate, "\n", tx_rate)
            link_rate_df = pd.DataFrame({
                "Actual UDP": udp_actual_rate,
                "Actual TCP": tcp_actual_rate,
                "Link Rate(rx)": [int(i) for i in rx_rate],
                "Link Rate(tx)": [int(i) for i in tx_rate],
            }, index=[phone_name[i] for i in range(len(phone_name))])

            # Plotting Graph  05 (User Name)
            user_name_df = pd.DataFrame({
                "udp download": udp_download_rate,
                "udp upload": udp_upload_rate,
                "tcp upload": tcp_upload_rate,
                "tcp download": tcp_download_rate,
            }, index=[user_name[i] for i in range(len(tcp_download_rate))])

        elif self.protocol[0] == "TCP-IPv4" or self.protocol[0] == "UDP-IPv4":
            for column in dataframe:
                # for each resource id getting upload and Download Data
                resource_id.append(column.split('.')[0])
                if not math.isnan(dataframe[column].loc[0]):
                    download_rate.append(float("{:.2f}".format(dataframe[column].loc[0])))
                    upload_rate.append(float("{:.2f}".format(dataframe[column].loc[1])))
            rx_tx_df = pd.DataFrame({
                "upload": upload_rate,
                "download": download_rate,
            }, index=[i for i in phone_name])

            print("rx_rate: ", rx_rate, "tx_rate: ",  tx_rate)

            down_rate = float("{:.2f}".format(int("".join([i for i in [i for i in self.inp_download_rate] if i.isdigit()]))/len(phone_name)))
            up_rate = float("{:.2f}".format(int("".join([i for i in [i for i in self.inp_upload_rate] if i.isdigit()]))/len(phone_name)))
            link_rate_df = pd.DataFrame({
                "Expected throughput Rx": [down_rate for i in range(int(self.batch_size))],
                "Expected throughput Tx": [up_rate for i in range(int(self.batch_size))],
                "Achieved throughput Rx": [download_rate[i] for i in range(int(self.batch_size))],
                "Achieved throughput Tx": [upload_rate[i] for i in range(int(self.batch_size))],
            }, index=[phone_name[i] for i in range(int(self.batch_size))])

            link_rate_phone_df = pd.DataFrame({
                "Max Link rate Rx": [int(rx_rate[int(i)]) for i in range(int(self.batch_size))],
                "Max Link rate Tx": [int(tx_rate[int(i)]) for i in range(int(self.batch_size))],
            }, index=[phone_name[i] for i in range(int(self.batch_size))])

        phone_data = [resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate, signal,
                      ssid, channel, phone_radio_bandwidth]
        self.generate_report(folder_directory, phone_data, rx_tx_df, link_rate_df, link_rate_phone_df)

    def generate_report(self, file_derectory, get_data, rx_tx_df, link_rate_df, link_rate_phone_df):

        number_of_devices = len(get_data[1])
        self.batch_size = int(self.batch_size[0])
        if int(self.batch_size) > number_of_devices:
            print("[INPUT] Wrong Batch Size should less than or equal to ", number_of_devices)
            exit(0)
        resource_id = [get_data[0][i] for i in range(self.batch_size)]
        phone_name = [get_data[3][i] for i in range(self.batch_size)]
        mac_address = [get_data[2][i] for i in range(self.batch_size)]
        user_name = [get_data[3][i] for i in range(self.batch_size)]
        phone_radio = [get_data[4][i] for i in range(self.batch_size)]
        rx_rate = [get_data[5][i] for i in range(self.batch_size)]
        tx_rate = [get_data[6][i] for i in range(self.batch_size)]
        signal = [get_data[7][i] for i in range(self.batch_size)]
        ssid = [get_data[8][i] for i in range(self.batch_size)]
        channel = [get_data[9][i] for i in range(self.batch_size)]
        mode = [get_data[10][i] for i in range(self.batch_size)]
        phone_radio_bandwidth = [get_data[10][i].split(" ")[-2] for i in range(self.batch_size)]

        # phone_radio_bandwidth = [i.split(" ")[-1] for i in phone_radio_bandwidth]
        report = lf_report(_output_html="we-can-wifi-capacity.html", _output_pdf="we-can-wifi-capacity.pdf",
                           _results_dir_name="we-can wifi-capacity result")

        report_time_file = report.get_path_date_time()
        shutil.copy(file_derectory + "/chart-0-print.png", report_time_file)
        # shutil.copy(file_derectory + "/kpi-chart-1-print.png", report_time_file)

        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()

        print(report_path_date_time)
        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))

        report.set_title("Lanforge Interop Wi-Fi Capacity Test report for Wi-Fi Client Devices")
        report.build_banner()

        report.start_content_div()
        report.set_text(
            "<h3>Objective:" + "<h5 style='text-align: justify;'>The LANforge Interop Wi-Fi capacity Test is designed "
                               "to measure the performance of an Access Point when handling different types of real "
                               "clients. The test allows the user to increase the number of stations in user defined "
                               "steps for each test iteration  and measure the per station and the overall throughput,"
                               " signal and link rates for each "
                               "trial. The expected behaviour is for the AP to be able to handle several stations "
                               "(within the limitations of the AP specs) and make sure all stations get a fair amount "
                               "of upstream and downstream throughput. An AP that scales well will not show a "
                               "significant over-all throughput decrease as more stations are added.")
        report.build_date_time()
        report.build_text()
        report.end_content_div()
        twog_count = 0
        fiveg_count = 0
        print(phone_radio)
        for i in phone_radio:
            if i == "2G":
                twog_count += 1
            else:
                fiveg_count += 1
        twog_fiveg_count = ("5G - stations = " + str(fiveg_count) + "    :   2G - stations = " + str(twog_count))
        device_data = {
            "No.of stations(2G & 5G)": [twog_fiveg_count],
            "Traffic rate ": ["Total Upload - " + self.inp_upload_rate + ": Total Download - " + self.inp_download_rate],
            "Total connected clients": [len(phone_name)],
            "Failed clients": ["NA"],

        }
        device_data = pd.DataFrame(device_data)
        report.start_content_div()
        report.set_table_title("<h3>Real-Time UDP Throughput Chart\n" + "<h5>Below chart shows the intended and "
                                "achieved throughput for station increments w.r.t time for " + str(self.protocol).
                               replace(')',' ').replace('(',' ').replace("'",' ').strip())
        report.build_table_title()
        report.set_table_dataframe(device_data)
        report.build_table()
        report.end_content_div()

        data = {
            "Resource ID": resource_id,
            "Phone Name": phone_name,
            "MAC Address": mac_address,
            "User Name": user_name,
            "Phone Radio": phone_radio,
            "Rx link Rate (Mbps) ": rx_rate,
            "Tx link Rate (Mbps)": tx_rate,
            "Device type": ["Android" for i in range(len(tx_rate))],
            "Channel": channel,
            "Signal": signal,
            "Mode": mode,

        }
        # Real time chart
        report.start_content_div()
        report.build_chart_title("Real Time Chart")
        report.build_chart_custom("chart-0-print.png", align='left',padding='15px',margin='5px 5px 2em 5px',
                                  width='800px', height='500px')
        report.end_content_div()
        direction = ""
        if self.inp_download_rate == '0Kbps' or self.inp_download_rate == '0Mbps' or self.inp_download_rate == '0Gbps':
            direction = "Upload"
        elif self.inp_upload_rate == '0Kbps' or self.inp_upload_rate == '0Mbps' or self.inp_upload_rate == '0Gbps':
            direction = "Download"
        else:
            direction = "Upload and Download"

        device_performance = {
            "Device Name": phone_name,
            "Signal": signal,
            "Connected SSID": ssid,
            "Security": ["WPA2" for i in range(len(ssid))],
            "Channel": channel,
            "Mode": phone_radio,
            "Rx Rate (Mbps)": rx_rate,
            "Tx Rate (Mbps)": tx_rate,
            "Bandwidth": phone_radio_bandwidth,
            "Direction": [direction for i in range(len(ssid))],
            "Traffic": [str(self.protocol).replace(')','').replace('(','').replace("'",'').strip() for i in range(len(ssid))],

        }
        phone_details_pd = pd.DataFrame(data)
        device_performance_pd = pd.DataFrame(device_performance)

        report.start_content_div()
        report.set_table_title("<h3>Individual Device Performance Chart:")
        report.build_table_title()
        report.set_table_dataframe(device_performance_pd)
        report.build_table()
        report.end_content_div()

        report.save_bar_chart("Real Client", "Rx/Tx (Mbps)", link_rate_df, "link_rate")
        report.start_content_div()
        # report.build_chart_title("Link Rate Chart")
        # report.set_text("<h5> This chart shows that the total Link rate we got during running the script for TCP and "
        #                 "UDP traffic versus the real traffic we got for each phone in Mbps.")
        report.build_chart_custom("link_rate.png", align='left', padding='15px', margin='0px 0px 0px 0px',
                                  width='1200px', height='400px')
        # report.build_text()

        report.build_chart_title("Signal Strength reported by the clients:")
        report.set_text("<h5>Chart shows the individual signal level for each connected device, measured from device to AP.")
        report.build_text()
        graph = lf_graph.lf_line_graph(_data_set=[[int(i) for i in signal]],
                                       _xaxis_name="Phone Names ",
                                       _yaxis_name="Signal(dbm)",
                                       _xaxis_categories=phone_name,
                                       _graph_image_name="rssi_signal",
                                       _label=['RSSI Strength'],
                                       _color=['blue'],
                                       _xaxis_step=1,
                                       _graph_title="Device to AP Signal Values",
                                       _title_size=16,
                                       _figsize=(18, 6),
                                       _marker='o',
                                       _legend_loc="best",
                                       _legend_box=None,
                                       _dpi=200)
        graph_png = graph.build_line_graph()
        report.set_graph_image(graph_png)
        report.move_graph_image()
        report.build_graph()

        report.save_bar_chart("Link Rate", "Rx/Tx (Mbps)", link_rate_phone_df, "link_rate_phone_df")
        report.start_content_div()
        report.build_chart_title("Link Rates (RX)")
        report.set_text("<h5> Chart describing the RX rate for each device model")
        report.build_chart_custom("link_rate_phone_df.png", align='left', padding='15px', margin='0px 0px 0px 0px',
                                  width='800px', height='400px')
        report.build_text()
        # graph1 = lf_graph.lf_bar_graph(_data_set=None,
        #          _xaxis_name="x-axis",
        #          _yaxis_name="y-axis",
        #          _xaxis_categories=None,
        #          _xaxis_label=None,
        #          _graph_title="",
        #          _title_size=16,
        #          _graph_image_name="image_name",
        #          _label=None,
        #          _color=None,
        #          _bar_width=0.25,
        #          _color_edge='grey',
        #          _font_weight='bold',
        #          _color_name=None,
        #          _figsize=(10, 5),
        #          _show_bar_value=False,
        #          _xaxis_step=1,
        #          _xticks_font=None,
        #          _xaxis_value_location=0,
        #          _text_font=None,
        #          _text_rotation=None,
        #          _grp_title="",
        #          _legend_handles=None,
        #          _legend_loc="best",
        #          _legend_box=None,
        #          _legend_ncol=1,
        #          _legend_fontsize=None,
        #          _dpi=96,
        #          _enable_csv=False)
        test_info_df = pd.DataFrame({
            "Data": ["DUT Model", "2.4 Ghz SSID", "2.4 Ghz BSSID", "5 Ghz SSID", "5 Ghz BSSID", "6 Ghz SSID",
                     "6 Ghz BSSID", "Intended Rate", "No of Stations", "No of loops", "Traffic duration",
                     "Test duration"],
            # need to make  the Netgear WAC510 dynamic
            "Value": [self.dut_model, self.ssid_dut_2g, "78:d2:94:4f:20:c5", self.ssid_dut_5g, "78:d2:94:4f:20:f3", "NA",
                      "NA", str(" ".split(self.inp_download_rate)[0] + " ".split(self.inp_upload_rate)[0]) + "Mbps",
                      len(phone_name), self.batch_size, str((int(self.duration) / 1000)) + " Sec", "2 Min"],
        })

        report.start_content_div()
        report.set_table_title("<h3>Test Information:")
        report.build_table_title()
        report.set_table_dataframe(test_info_df)
        report.build_table()
        report.end_content_div()

        report.start_content_div()
        report.set_table_title("<h3>Device Details")
        report.build_table_title()
        report.set_table_dataframe(phone_details_pd)
        report.build_table()
        report.set_text("<h5> The above table shows a list of all the Real clients which are connected to LANForge "
                        "server in the tabular format which also show the various details of the real-client (phones) "
                        "such as phone name, MAC address, Username, Phone Radio, Rx link rate, Tx link rate and "
                        "Resource id.")
        report.build_text()
        report.end_content_div()

        report.build_footer()
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)
        report.write_pdf(_page_size='Legal', _orientation='Portrait')

    def get_resource_data(self):
        resource_id_list = []
        phone_name_list = []
        mac_address = []
        user_name = []
        phone_radio = []
        rx_rate = []
        tx_rate = []
        signal = []
        ssid = []
        channel = []
        phone_radio_bandwidth = []
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,signal,ssid,channel")
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_id_list.append(i.split(".")[1])
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    # Getting MAC address
                    mac = alias[i]["mac"]

                    rx = alias[i]["rx-rate"]
                    tx = alias[i]["tx-rate"]
                    rx_rate.append(rx)
                    tx_rate.append(tx)
                    signal.append(alias[i]["signal"])
                    ssid.append(alias[i]["ssid"])
                    channel.append(alias[i]["channel"])
                    # Getting username
                    user = resource_hw_data['resource']['user']
                    user_name.append(user)
                    # Getting user Hardware details/Name
                    hw_name = resource_hw_data['resource']['hw version'].split(" ")
                    name = " ".join(hw_name[0:2])
                    phone_name_list.append(name)
                    mac_address.append(mac)
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and alias[i]["parent dev"] == 'wiphy0':
                    phone_radio_bandwidth.append(alias[i]['mode'])
                    # Mapping Radio Name in human readable format
                    if 'a' not in alias[i]['mode'] or "20" in alias[i]['mode']:
                        phone_radio.append('2G')
                    elif 'AUTO' in alias[i]['mode']:
                        phone_radio.append("AUTO")
                    else:
                        phone_radio.append('2G/5G')
        return resource_id_list, phone_name_list, mac_address, user_name, phone_radio, rx_rate, tx_rate, signal, ssid, channel, phone_radio_bandwidth


def main():
    parser = argparse.ArgumentParser(
        prog="we_can_wifi_capacity_test.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
            ./we_can_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
                 --instance_name wct_instance --config_name wifi_config --upstream 1.1.eth1 --batch_size 1 --loop_iter 1 \
                 --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0001 \
                 --create_stations --radio wiphy0 --ssid test-ssid --security open --paswd [BLANK] \
                   """)

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser = argparse.ArgumentParser(description="Netgear AP DFS Test Script")
    parser.add_argument('--mgr', type=str, help='host name', default="localhost")
    parser.add_argument('--port', type=str, help='port number', default="8080")
    parser.add_argument("--upstream", type=str, default="",
                        help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("--batch_size", type=str, default="",
                        help="station increment ex. 1,2,3")
    parser.add_argument("--protocol", type=str, default="",
                        help="Protocol ex.TCP-IPv4")
    parser.add_argument("--lf_user", type=str, default="",
                        help="lanforge user name ex. root,lanforge")
    parser.add_argument("--lf_password", type=str, default="",
                        help="lanforge user password ex. root,lanforge")
    parser.add_argument("--duration", type=str, default="60000",
                        help="duration in ms. ex. 5000")
    parser.add_argument("--download_rate", type=str, default="0Kbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 0Kbps")
    parser.add_argument("--upload_rate", type=str, default="0Kbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 0Kbps")
    parser.add_argument("--dut_model", type=str, default="NA",
                        help="AP name and Model ")
    parser.add_argument("--ssid_dut_2g", type=str, default="NA",
                        help="ssid name to be tested Ex. Netgear_2G")
    parser.add_argument("--ssid_dut_5g", type=str, default="NA",
                        help="ssid name to be tested Ex. Netgear_5G")
    parser.add_argument("--influx_host", type=str, default="localhost", help="NA")
    parser.add_argument("--local_lf_report_dir", default="",
                        help="--local_lf_report_dir <where to pull reports to>  default '' put where dataplane script run from")

    args = parser.parse_args()

    WFC_Test = WeCanWiFiCapacityTest(lfclient_host=args.mgr,
                                lf_port=args.port,
                                ssh_port=22,
                                lf_user=args.lf_user,
                                lf_password=args.lf_password,
                                upstream=args.upstream,
                                batch_size=args.batch_size,
                                protocol=args.protocol,
                                duration=args.duration,
                                pull_report=True,
                                download_rate=args.download_rate,
                                upload_rate=args.upload_rate,
                                influx_host=args.mgr,
                                influx_port=8086,
                                local_lf_report_dir=args.local_lf_report_dir,
                                )
    WFC_Test.setup()
    WFC_Test.run()
    wifi_capacity = LfInteropWifiCapacity(host=args.mgr, port=args.port, protocol=args.protocol,
                                          batch_size=args.batch_size, duration=args.duration,dut_model=args.dut_model,
                                          inp_download_rate=args.download_rate, inp_upload_rate=args.upload_rate,
                                          ssid_dut_2g=args.ssid_dut_2g, ssid_dut_5g=args.ssid_dut_5g,)
    wifi_capacity.get_data()
    # WFC_Test.check_influx_kpi(args)


if __name__ == "__main__":
    main()
