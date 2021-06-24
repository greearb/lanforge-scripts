#!/usr/bin/env python3

"""
NAME: throughput_qos.py

PURPOSE: throughput_qos.py will create stations and endpoints which evaluates  l3 traffic for a particular type of service.

EXAMPLE:
python3 throughput_qos.py --mgr 192.168.200.240 --mgr_port 8080 -u eth1 --num_stations 1
--radio wiphy1 --ssid TestAP5-71 --passwd lanforge --security wpa2 --mode 11 --a_min 1000000 --b_min 1000000 --traffic_type lf_udp

python3 throughput_qos.py --num_stations 1 --radio wiphy1 --ssid ct523c-vap --passwd ct523c-vap --security wpa2 --mode 11 --a_min 1000000 --b_min 1000000 --traffic_type lf_udp


Use './throughput_qos.py --help' to see command line usage and options
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import pdfkit
from lf_report import lf_report
from lf_graph import lf_bar_graph

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge import LFUtils
from realm import Realm
import time
import datetime


class ThroughputQOS(Realm):
    def __init__(self,
                 tos,
                 ssid=None,
                 security=None,
                 password=None,
                 ssid_2g=None,
                 security_2g=None,
                 password_2g=None,
                 ssid_5g=None,
                 security_5g=None,
                 password_5g=None,
                 sta_list=[],
                 create_sta=True,
                 name_prefix=None,
                 upstream=None,
                 radio="wiphy0",
                 host="localhost",
                 port=8080,
                 mode=0,
                 ap=None,
                 traffic_type=None,
                 side_a_min_rate=56, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="2m",
                 bands="2.4G, 5G, BOTH",
                 radios="",
                 test_case={},
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.ssid_2g = ssid_2g
        self.security_2g = security_2g
        self.password_2g = password_2g
        self.ssid_5g = ssid_5g
        self.security_5g = security_5g
        self.password_5g = password_5g
        self.radio = radio.split(",")
        self.sta_list = sta_list
        self.create_sta = create_sta
        self.mode = mode
        self.ap = ap
        self.traffic_type = traffic_type
        self.tos = tos.split(",")
        self.bands = bands.split(",")
        self.radios = radios
        self.test_case = test_case
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 9
        self.station_profile.mode = mode
        if self.ap is not None:
            self.station_profile.set_command_param("add_sta", "ap", self.ap)
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def start(self, print_pass=False, print_fail=False):
        if self.create_sta:
            self.station_profile.admin_up()
            # check here if upstream port got IP
            temp_stations = self.station_profile.station_names.copy()
            if self.wait_for_ip(temp_stations):
                self._pass("All stations got IPs")
            else:
                self._fail("Stations failed to get IPs")
                self.exit_fail()
        self.cx_profile.start_cx()

    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        if self.create_sta:
            for sta in self.sta_list:
                self.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.cx_profile.cleanup()
        if self.create_sta:
            self.station_profile.cleanup()
            LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                               debug=self.debug)

    def build(self):
        for key in self.bands:
            if self.create_sta:
                if key == "2.4G" or key == "2.4g":
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)

                if key == "5G" or key == "5g":
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)

                self.station_profile.set_number_template(self.number_template)
                print("Creating stations")
                self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                self.station_profile.set_command_param("set_port", "report_timer", 1500)
                self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

                if key == "BOTH" or key == "both":
                    keys = list(self.test_case.keys())
                    if "BOTH" in self.test_case:
                        self.radios = self.test_case["BOTH"].split(",")
                    elif "both" in self.test_case:
                        self.radios = self.test_case["both"].split(",")
                    split = len(self.sta_list) // 2
                    if keys[0] == "2.4G" or keys[0] == "2.4g":
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 11
                        self.station_profile.create(radio=self.radios[0], sta_names_=self.sta_list[:split],
                                                    debug=self.debug)
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 9
                        self.station_profile.create(radio=self.radios[1], sta_names_=self.sta_list[split:],
                                                    debug=self.debug)
                    elif keys[0] == "5G" or keys[0] == "5g":
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 9
                        self.station_profile.create(radio=self.radios[0], sta_names_=self.sta_list[:split],
                                                    debug=self.debug)
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 11
                        self.station_profile.create(radio=self.radios[1], sta_names_=self.sta_list[split:],
                                                    debug=self.debug)
                    else:
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 11
                        self.station_profile.create(radio=self.radios[0], sta_names_=self.sta_list[:split],
                                                    debug=self.debug)
                        if self.ssid is None:
                            self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                        else:
                            self.station_profile.use_security(self.security, self.ssid, self.password)
                        self.station_profile.mode = 9
                        self.station_profile.create(radio=self.radios[1], sta_names_=self.sta_list[split:],
                                                    debug=self.debug)

                else:
                    self.station_profile.create(radio=self.radio[0], sta_names_=self.sta_list, debug=self.debug)
                self._pass("PASS: Station build finished")
            self.create_cx()
            print("cx build finished")

    def create_cx(self):
        _tos = "BK,BE,VI,VO"
        self.tos = _tos.split(",")
        print("tos: {}".format(self.tos))
        for ip_tos in self.tos:
            print("## ip_tos: {}".format(ip_tos))
            print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s" % (
                self.traffic_type, ip_tos, self.cx_profile.get_cx_count()))
            self.cx_profile.create(endp_type=self.traffic_type, side_a=self.sta_list,
                                   side_b=self.upstream,
                                   sleep_time=0, tos=ip_tos)
        print("cross connections with TOS type created.")

    def evaluate_throughput(self):
        global case
        tos_download = {'video': [], 'voice': [], 'bk': [], 'be': []}
        tx_b = {'bk': [], 'be': [], 'video': [], 'voice': []}
        rx_a = {'bk': [], 'be': [], 'video': [], 'voice': []}
        pkt_loss = {}
        tx_endps = {}
        rx_endps = {}
        if int(self.cx_profile.side_b_min_bps) != 0:
            case = str(int(self.cx_profile.side_b_min_bps) // 1000000)
        elif int(self.cx_profile.side_a_min_bps) != 0:
            case = str(int(self.cx_profile.side_a_min_bps) // 1000000)
        if len(self.cx_profile.created_cx.keys()) > 0:
            endp_data = self.json_get('endp/all?fields=name,tx+pkts+ll,rx+pkts+ll')
            endp_data.pop("handler")
            endp_data.pop("uri")
            print(endp_data)
            endps = endp_data['endpoint']
            for i in range(len(endps)):
                if i < len(endps) // 2:
                    tx_endps.update(endps[i])
                if i >= len(endps) // 2:
                    rx_endps.update(endps[i])
            for sta in self.cx_profile.created_cx.keys():
                temp = int(sta[12:])
                if temp % 4 == 0:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['bk'].append(float(
                            f"{list((self.json_get('/cx/%s?fields=bps+rx+a' % sta)).values())[2]['bps rx a'] / 1000000:.2f}"))
                        tx_b['bk'].append(int(f"{tx_endps['%s-B' %sta]['tx pkts ll']}"))
                        rx_a['bk'].append(int(f"{rx_endps['%s-A' %sta]['rx pkts ll']}"))
                    else:
                        tos_download['bk'].append(float(0))
                        tx_b['bk'].append(int(0))
                        rx_a['bk'].append(int(0))
                elif temp % 4 == 1:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['be'].append(float(
                            f"{list((self.json_get('/cx/%s?fields=bps+rx+a' % sta)).values())[2]['bps rx a'] / 1000000:.2f}"))
                        tx_b['be'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['be'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                    else:
                        tos_download['be'].append(float(0))
                        tx_b['be'].append(int(0))
                        rx_a['be'].append(int(0))
                elif temp % 4 == 2:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['voice'].append(float(
                            f"{list((self.json_get('/cx/%s?fields=bps+rx+a' % sta)).values())[2]['bps rx a'] / 1000000:.2f}"))
                        tx_b['voice'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['voice'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                    else:
                        tos_download['voice'].append(float(0))
                        tx_b['voice'].append(int(0))
                        rx_a['voice'].append(int(0))
                elif temp % 4 == 3:
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['video'].append(float(
                            f"{list((self.json_get('/cx/%s?fields=bps+rx+a' % sta)).values())[2]['bps rx a'] / 1000000:.2f}"))
                        tx_b['video'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['video'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                    else:
                        tos_download['video'].append(float(0))
                        tx_b['video'].append(int(0))
                        rx_a['video'].append(int(0))
            tos_download.update({"bkQOS": float(f"{sum(tos_download['bk']):.2f}")})
            tos_download.update({"beQOS": float(f"{sum(tos_download['be']):.2f}")})
            tos_download.update({"videoQOS": float(f"{sum(tos_download['video']):.2f}")})
            tos_download.update({"voiceQOS": float(f"{sum(tos_download['voice']):.2f}")})
            if sum(tx_b['bk']) != 0 or sum(tx_b['be']) != 0 or sum(tx_b['video']) != 0 or sum(tx_b['voice']) != 0:
                pkt_loss.update({"bkLOSS": float(f"{((sum(tx_b['bk']) - sum(rx_a['bk']))/sum(tx_b['bk']))*100:.2f}")})
                pkt_loss.update({"beLOSS": float(f"{((sum(tx_b['be']) - sum(rx_a['be']))/sum(tx_b['be']))*100:.2f}")})
                pkt_loss.update({"videoLOSS": float(f"{((sum(tx_b['video']) - sum(rx_a['video']))/sum(tx_b['video']))*100:.2f}")})
                pkt_loss.update({"voiceLOSS": float(f"{((sum(tx_b['voice']) - sum(rx_a['voice']))/sum(tx_b['voice']))*100:.2f}")})
        else:
            print("no RX values available to evaluate QOS")
        key = case + " " + "Mbps"
        print(tos_download)
        print(pkt_loss)
        return {key: tos_download}, pkt_loss

    def generate_report(self, data):
        print(data)
        res = {}
        if data is not None:
            for i in range(len(data)):
                res.update(data[i])
        else:
            print("No Data found to generate report!")
            exit(1)
        report = lf_report()
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))
        report.set_title("Throughput QOS")
        report.build_banner()
        # objective title and description
        report.set_obj_html(_obj_title="Objective",
                            _obj="Through this test we can evaluate the throughput for given number of clients which"
                                 " runs the traffic with a particular Type of Service i.e BK,BE,VI,VO")
        report.build_objective()

        report.set_table_title(
            "Overall download Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO) in 2.4Ghz")
        report.build_table_title()

        t_1mb = []
        t_2mb = []
        t_3mb = []
        t_4mb = []
        t_5mb = []

        table_df = [t_1mb, t_2mb, t_3mb, t_4mb, t_5mb]

        for key in res:
            if key == '1 Mbps':
                table_df[0].append(res[key]['bkQOS'])
                table_df[0].append(res[key]['beQOS'])
                table_df[0].append(res[key]['videoQOS'])
                table_df[0].append(res[key]['voiceQOS'])
            if key == '2 Mbps':
                table_df[1].append(res[key]['bkQOS'])
                table_df[1].append(res[key]['beQOS'])
                table_df[1].append(res[key]['videoQOS'])
                table_df[1].append(res[key]['voiceQOS'])
            if key == '3 Mbps':
                table_df[2].append(res[key]['bkQOS'])
                table_df[2].append(res[key]['beQOS'])
                table_df[2].append(res[key]['videoQOS'])
                table_df[2].append(res[key]['voiceQOS'])
            if key == '4 Mbps':
                table_df[3].append(res[key]['bkQOS'])
                table_df[3].append(res[key]['beQOS'])
                table_df[3].append(res[key]['videoQOS'])
                table_df[3].append(res[key]['voiceQOS'])
            if key == '5 Mbps':
                table_df[4].append(res[key]['bkQOS'])
                table_df[4].append(res[key]['beQOS'])
                table_df[4].append(res[key]['videoQOS'])
                table_df[4].append(res[key]['voiceQOS'])
        table_df2 = []
        for i in range(len(table_df)):
            table_df2.append(
                f'BK: {table_df[i][0]} | BE: {table_df[i][1]} | VI: {table_df[i][2]} | VO: {table_df[i][3]}')

        df_throughput = pd.DataFrame({
            'Mode': ['bgn-AC'], "No.of.clients": [len(self.sta_list)],
            'Throughput for Load (1 Mbps)': [table_df2[0]],
            'Throughput for Load (2 Mbps)': [table_df2[1]],
            'Throughput for Load (3 Mbps)': [table_df2[2]],
            'Throughput for Load (4 Mbps)': [table_df2[3]],
            'Throughput for Load (5 Mbps)': [table_df2[4]],
        })
        report.set_table_dataframe(df_throughput)
        report.build_table()

        report.set_graph_title("Overall download Throughput for all 2.4G clients with different TOS.")
        report.set_obj_html(_obj_title="", _obj="This graph represents the download throughput for Bk, BE, Video, Voice"
                                                " services when stations are running the traffic with load 1 Mbps, "
                                                "2 Mbps, 3 Mbps, 4 Mbps")
        report.build_graph_title()
        report.build_objective()

        y_bk = []
        y_be = []
        y_vi = []
        y_vo = []

        graph_df = [y_bk, y_be, y_vi, y_vo]
        for key in res:
            if key == '1 Mbps':
                graph_df[0].append(res[key]['bkQOS'])
                graph_df[1].append(res[key]['beQOS'])
                graph_df[2].append(res[key]['videoQOS'])
                graph_df[3].append(res[key]['voiceQOS'])
            if key == '2 Mbps':
                graph_df[0].append(res[key]['bkQOS'])
                graph_df[1].append(res[key]['beQOS'])
                graph_df[2].append(res[key]['videoQOS'])
                graph_df[3].append(res[key]['voiceQOS'])
            if key == '3 Mbps':
                graph_df[0].append(res[key]['bkQOS'])
                graph_df[1].append(res[key]['beQOS'])
                graph_df[2].append(res[key]['videoQOS'])
                graph_df[3].append(res[key]['voiceQOS'])
            if key == '4 Mbps':
                graph_df[0].append(res[key]['bkQOS'])
                graph_df[1].append(res[key]['beQOS'])
                graph_df[2].append(res[key]['videoQOS'])
                graph_df[3].append(res[key]['voiceQOS'])
            if key == '5 Mbps':
                graph_df[0].append(res[key]['bkQOS'])
                graph_df[1].append(res[key]['beQOS'])
                graph_df[2].append(res[key]['videoQOS'])
                graph_df[3].append(res[key]['voiceQOS'])

        graph = lf_bar_graph(_data_set=graph_df,
                             _xaxis_name="Load per Type of Service",
                             _yaxis_name="Throughput (Mbps)",
                             _xaxis_categories=[1, 2, 3, 4, 5, 6],
                             _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                             _graph_image_name="tos_download_2.4GHz",
                             _label=["BE", "BK", "VI", "VO"],
                             _step_size=1,
                             _color=['orangered', 'greenyellow', 'steelblue', 'blueviolet'],
                             _color_edge='black',
                             _bar_width=0.15,
                             _dpi=96,
                             _color_name=['orangered', 'greenyellow', 'steelblue', 'blueviolet'])
        graph_png = graph.build_bar_graph()

        print("graph name {}".format(graph_png))

        report.set_graph_image(graph_png)
        # need to move the graph image to the results
        report.move_graph_image()
        report.build_graph()
        self.generate_individual_graph(data, report)
        report.write_html()
        report.write_pdf()

    def generate_individual_graph(self, data, report):
        if data is not None:
            res = {}
            for i in range(len(data)):
                res.update(data[i])
        if len(res.keys()) > 0:
            count = 1
            for key in res:
                report.set_graph_title(_graph_title="Individual stations Download Throughput for the service Bk(WIFI) of load {}.".format(key))
                report.set_obj_html(_obj_title="",
                                    _obj="This is the individual throughput for {} number of clients running service BK".format(
                                        len(self.sta_list)))
                report.build_graph_title()
                report.build_objective()
                graph = lf_bar_graph(_data_set=[res[key]['bk']], _xaxis_name="Clients running - BK",
                                     _yaxis_name="Throughput in Mbps",
                                     _xaxis_categories=[i for i in range(len(self.sta_list))],
                                     _xaxis_label=[i for i in range(len(self.sta_list))],
                                     _label=["BK"],
                                     _step_size=1,
                                     _bar_width=0.15, _color_name=['orangered'],
                                     _graph_image_name="{}_bk_{}".format(self.bands[0], count), _color_edge=['black'],
                                     _color=['orangered'])
                graph_png = graph.build_bar_graph()
                print("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                # need to move the graph image to the results
                report.move_graph_image()
                report.build_graph()
                report.set_graph_title(_graph_title="Individual stations Download Throughput for the service BE(WIFI) of load {}.".format(key))
                report.set_obj_html(_obj_title="",
                                    _obj="This is the individual throughput for {} number of clients running service BE".format(
                                        len(self.sta_list)))
                report.build_graph_title()
                report.build_objective()
                graph = lf_bar_graph(_data_set=[res[key]['be']], _xaxis_name="Clients running - BE",
                                     _yaxis_name="Throughput in Mbps",
                                     _xaxis_categories=[i for i in range(len(self.sta_list))],
                                     _xaxis_label=[i for i in range(len(self.sta_list))],
                                     _label=["BE"],
                                     _step_size=1,
                                     _bar_width=0.15, _color_name=['greenyellow'],
                                     _graph_image_name="{}_be_{}".format(self.bands[0], count), _color_edge=['black'],
                                     _color=['greenyellow'])
                graph_png = graph.build_bar_graph()
                print("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                # need to move the graph image to the results
                report.move_graph_image()
                report.build_graph()
                report.set_graph_title(_graph_title="Individual stations Download Throughput for the service VI(WIFI) of load {}.".format(key))
                report.set_obj_html(_obj_title="",
                                    _obj="This is the individual throughput for {} number of clients running service VI".format(
                                        len(self.sta_list)))
                report.build_graph_title()
                report.build_objective()
                graph = lf_bar_graph(_data_set=[res[key]['video']], _xaxis_name="Clients running - VI",
                                     _yaxis_name="Throughput in Mbps",
                                     _xaxis_categories=[i for i in range(len(self.sta_list))],
                                     _xaxis_label=[i for i in range(len(self.sta_list))],
                                     _label=["Video"],
                                     _step_size=1,
                                     _bar_width=0.15, _color_name=['steelblue'],
                                     _graph_image_name="{}_video_{}".format(self.bands[0], count), _color_edge=['black'],
                                     _color=['steelblue'])
                graph_png = graph.build_bar_graph()
                print("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                # need to move the graph image to the results
                report.move_graph_image()
                report.build_graph()
                report.set_graph_title(_graph_title="Individual stations Download Throughput for the service VO(WIFI) of load {}.".format(key))
                report.set_obj_html(_obj_title="",
                                    _obj="This is the individual throughput for {} number of clients running service VO".format(
                                        len(self.sta_list)))
                report.build_graph_title()
                report.build_objective()
                graph = lf_bar_graph(_data_set=[res[key]['voice']], _xaxis_name="Clients running - VO",
                                     _yaxis_name="Throughput in Mbps",
                                     _xaxis_categories=[i for i in range(len(self.sta_list))],
                                     _xaxis_label=[i for i in range(len(self.sta_list))],
                                     _label=['Voice'],
                                     _step_size=1,
                                     _bar_width=0.15, _color_name=['blueviolet'],
                                     _graph_image_name="{}_voice_{}".format(self.bands[0], count), _color_edge=['black'],
                                     _color=['blueviolet'])
                graph_png = graph.build_bar_graph()
                print("graph name {}".format(graph_png))
                report.set_graph_image(graph_png)
                # need to move the graph image to the results
                report.move_graph_image()
                report.build_graph()
                count += 1
        else:
            print("No individual graph to generate.")


def main():
    parser = Realm.create_basic_argparse(
        prog='throughput_QOS.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations and endpoints and runs L3 traffic with various IP type of service(BK |  BE | Video | Voice)
            ''',
        description='''\
throughput_QOS.py:
--------------------
Generic command layout:

python3 ./throughput_QOS.py
    --upstream_port eth1
    --radio wiphy0
    --num_stations 32
    --security {open|wep|wpa|wpa2|wpa3}
    --mode   1
        {"auto"   : "0",
        "a"      : "1",
        "b"      : "2",
        "g"      : "3",
        "abg"    : "4",
        "abgn"   : "5",
        "bgn"    : "6",
        "bg"     : "7",
        "abgnAC" : "8",
        "anAC"   : "9", 
        "an"     : "10",
        "bgnAC"  : "11",
        "abgnAX" : "12",
        "bgnAX"  : "13"}
    --ssid netgear
    --password admin123
    --test_duration 2m (default)
    --monitor_interval_ms 
    --a_min 3000
    --b_min 1000
    --ap "00:0e:8e:78:e1:76"
    --debug
    --upstream_port eth1        (upstream Port)
    --traffic_type lf_udp       (traffic type, lf_udp | lf_tcp)
    --test_duration 5m          (duration to run traffic 5m --> 5 Minutes)
    --create_sta False          (False, means it will not create stations and use the sta_names specified below)
    --sta_names sta000,sta001,sta002 (used if --create_sta False, comma separated names of stations)
    ''')

    parser.add_argument('--mode', help='Used to force mode of stations', default="0")
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=True)
    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    parser.add_argument('--create_sta', help='Used to force a connection to a particular AP', default=True)
    parser.add_argument('--sta_names', help='Used to force a connection to a particular AP', default="sta0000")
    parser.add_argument('--tos', help='used to provide different ToS settings: BK | BE | VI | VO | numeric',
                        default="Best Effort")
    parser.add_argument('--bands', help='used to run on multiple radio bands,can be used with multiple stations',
                        default="2,4G, 5G, BOTH", required=True)
    parser.add_argument('--ssid_2g', help="ssid for  2.4Ghz band")
    parser.add_argument('--security_2g', help="security type for  2.4Ghz band")
    parser.add_argument('--passwd_2g', help="password for 2.4Ghz band")
    parser.add_argument('--ssid_5g', help="ssid for  5Ghz band")
    parser.add_argument('--security_5g', help="security type  for  5Ghz band")
    parser.add_argument('--passwd_5g', help="password for  5Ghz band")
    args = parser.parse_args()
    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    args.test_case = {}
    test_results = []
    loads = {}
    bands = []
    radios = []
    station_list = []
    if (args.a_min is not None) and (args.b_min is not None):
        if (type(args.a_min) is not int) and (type(args.b_min) is not int):
            args.a_min = args.a_min.split(',')
            args.b_min = args.b_min.split(',')
            loads = {"a_min": args.a_min, "b_min": args.b_min}
        else:
            args.a_min = str(args.a_min).split(",")
            args.b_min = str(args.b_min).split(",")
            loads = {"a_min": args.a_min, "b_min": args.b_min}

    if args.bands is not None:
        bands = args.bands.split(',')

    if args.radio is not None:
        radios = args.radio.split(',')
        if len(radios) < 2:
            radios.extend(radios[0])

    if args.test_duration is not None:
        args.test_duration = args.test_duration.strip('m')

    for i in range(len(bands)):
        if bands[i] == "2.4G" or bands[i] == "2.4g":
            args.bands = bands[i]
            if args.mode is not None:
                args.mode = 11
            if i == 0:
                args.radio = radios[0]
                args.test_case.update({bands[i]: radios[0]})
            else:
                args.radio = radios[1]
                args.test_case.update({bands[i]: radios[1]})
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000, radio=args.radio)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "5G" or bands[i] == "5g":
            args.bands = bands[i]
            args.mode = 9
            if i == 0:
                args.radio = radios[0]
                args.test_case.update({bands[i]: radios[0]})
            else:
                args.radio = radios[1]
                args.test_case.update({bands[i]: radios[1]})
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "BOTH" or bands[i] == "both":
            args.bands = bands[i]
            args.radio = str(radios[0] + "," + radios[1])
            args.test_case.update({bands[i]: radios[0] + "," + radios[1]})
            mid = int(args.num_stations) // 2
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=mid - 1,
                                                      padding_number_=10000,
                                                      radio=radios[0])
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=mid,
                                                           end_id_=int(args.num_stations) - 1,
                                                           padding_number_=10000,
                                                           radio=radios[1]))
            else:
                station_list = args.sta_names.split(",")
        else:
            print("Band " + bands[i] + " Not Exist")
            exit(1)
        print("-----------------")
        # print(bands[i])
        print(args.radio)
        # print(args.mode)
        # print(station_list)
        print(args.test_case)
        print("-----------------")
        # ---------------------------------------#
        for index in range(len(loads["b_min"])):
            throughput_qos = ThroughputQOS(host=args.mgr,
                                           port=args.mgr_port,
                                           number_template="0000",
                                           sta_list=station_list,
                                           create_sta=args.create_sta,
                                           name_prefix="TOS-",
                                           upstream=args.upstream_port,
                                           ssid=args.ssid,
                                           password=args.passwd,
                                           security=args.security,
                                           ssid_2g=args.ssid_2g,
                                           password_2g=args.passwd_2g,
                                           security_2g=args.security_2g,
                                           ssid_5g=args.ssid_5g,
                                           password_5g=args.passwd_5g,
                                           security_5g=args.security_5g,
                                           radio=args.radio,
                                           test_duration=args.test_duration,
                                           use_ht160=False,
                                           side_a_min_rate=loads['a_min'][index],
                                           side_b_min_rate=loads['b_min'][index],
                                           mode=args.mode,
                                           bands=args.bands,
                                           ap=args.ap,
                                           traffic_type=args.traffic_type,
                                           tos=args.tos,
                                           test_case=args.test_case,
                                           _debug_on=args.debug)
            throughput_qos.pre_cleanup()
            throughput_qos.build()

            if args.create_sta:
                if not throughput_qos.passes():
                    print(throughput_qos.get_fail_message())
                    throughput_qos.exit_fail()
            # try:
            #     layer3connections = ','.join([[*x.keys()][0] for x in throughput_qos.json_get('endp')['endpoint']])
            # except:
            #     raise ValueError('Try setting the upstream port flag if your device does not have an eth1 port')

            throughput_qos.start(False, False)
            time.sleep(int(args.test_duration) * 60)
            throughput_qos.stop()
            test_results.append(throughput_qos.evaluate_throughput())
            if args.create_sta:
                if not throughput_qos.passes():
                    print(throughput_qos.get_fail_message())
                    throughput_qos.exit_fail()
                LFUtils.wait_until_ports_admin_up(port_list=station_list)
                if throughput_qos.passes():
                    throughput_qos.success()
            throughput_qos.cleanup()

    data = test_results
    #throughput_qos.generate_report(data=data)


if __name__ == "__main__":
    main()
