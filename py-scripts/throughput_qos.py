#!/usr/bin/env python3

"""
NAME: throughput_qos.py

PURPOSE: throughput_qos.py will create stations and endpoints which evaluates  l3 traffic for a particular type of service.

EXAMPLE:
To Test with 2.4GHz clients, use:
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_2g wiphy0 --ssid_2g testqos --passwd_2g [BLANK] --security_2g open --upstream eth1 --test_duration 1m --download 1000000 --bands 2.4g --traffic_type lf_tcp

To Test with 5GHz clients, use:
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_5g wiphy0 --ssid_5g testqos --passwd_5g [BLANK] --security_5g open --upstream eth1 --test_duration 1m --download 1000000 --bands 5g --traffic_type lf_udp

To Test with 2.4GHz & 5GHz clients (BOTH), use:
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_2g wiphy0 --ssid_2g testqos --passwd_2g [BLANK] --security_2g open --radio_5g wiphy0 --ssid_5g testqos --passwd_5g [BLANK] --security_5g open --upstream eth1 --test_duration 1m --download 1000000 --bands both --traffic_type lf_tcp

Use './throughput_qos.py --help' to see command line usage and options
Copyright 2022 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""

import sys
import os
import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import time
import argparse
from LANforge import LFUtils
from realm import Realm
from lf_report import lf_report
from lf_graph import lf_bar_graph
from datetime import datetime, timedelta


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
                 create_sta=True,
                 name_prefix=None,
                 upstream=None,
                 num_stations=1,
                 sta_list=[],
                 radio_2g="wiphy0",
                 radio_5g="wiphy1",
                 host="localhost",
                 port=8080,
                 mode=0,
                 ap_name="",
                 traffic_type=None,
                 side_a_min_rate=0, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000",
                 test_duration="2m",
                 bands="2.4G, 5G, BOTH",
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
        self.radio_2g = radio_2g
        self.radio_5g = radio_5g
        self.num_stations = num_stations
        self.sta_list = sta_list
        self.create_sta = create_sta
        self.mode = mode
        self.ap_name = ap_name
        self.traffic_type = traffic_type
        self.tos = tos.split(",")
        self.bands = bands.split(",")
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
            self.station_profile.mode = 14
        # self.station_profile.mode = mode
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def start(self, print_pass=False, print_fail=False):
        if len(self.cx_profile.created_cx) > 0:
            for cx in self.cx_profile.created_cx.keys():
                req_url = "cli-json/set_cx_report_timer"
                data = {
                    "test_mgr": "all",
                    "cx_name": cx,
                    "milliseconds": 1000
                }
                self.json_post(req_url, data)
        self.cx_profile.start_cx()

    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.cx_profile.cleanup()
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
                    self.station_profile.mode = 13
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    self.station_profile.create(radio=self.radio_2g, sta_names_=self.sta_list, debug=self.debug)
                if key == "5G" or key == "5g":
                    self.station_profile.mode = 14
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list, debug=self.debug)
                if key == "BOTH" or key == "both":
                    split = len(self.sta_list) // 2
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_2g, self.ssid_2g, self.password_2g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 13
                    self.station_profile.set_number_template(self.number_template)
                    print("Creating stations")
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    self.station_profile.create(radio=self.radio_2g, sta_names_=self.sta_list[:split],
                                                debug=self.debug)
                    if self.ssid is None:
                        self.station_profile.use_security(self.security_5g, self.ssid_5g, self.password_5g)
                    else:
                        self.station_profile.use_security(self.security, self.ssid, self.password)
                    self.station_profile.mode = 14
                    self.station_profile.set_number_template(self.number_template)
                    self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
                    self.station_profile.set_command_param("set_port", "report_timer", 1500)
                    self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
                    self.station_profile.create(radio=self.radio_5g, sta_names_=self.sta_list[split:],
                                                debug=self.debug)
                self.station_profile.admin_up()
                # check here if upstream port got IP
                temp_stations = self.station_profile.station_names.copy()
                if self.wait_for_ip(temp_stations):
                    self._pass("All stations got IPs")
                else:
                    self._fail("Stations failed to get IPs")
                    self.exit_fail()
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

    def monitor(self):
        print("Monitoring CXs... & Endpoints...")
        download, throughput, bps_rx_a = {}, [], []
        if (self.test_duration is None) or (int(self.test_duration) <= 1):
            raise ValueError("Monitor test duration should be > 1 second")
        if self.cx_profile.created_cx is None:
            raise ValueError("Monitor needs a list of Layer 3 connections")
        # monitor columns
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=int(self.test_duration))
        index = -1
        connections = dict.fromkeys(list(self.cx_profile.created_cx.keys()), float(0))
        [(bps_rx_a.append([])) for i in range(len(self.cx_profile.created_cx))]
        while datetime.now() < end_time:
            index += 1
            response = list(
                self.json_get('/cx/%s?fields=%s' % (
                    ','.join(self.cx_profile.created_cx.keys()), ",".join(['bps rx a']))).values())[2:]
            download[index] = list(
                map(lambda i: [x for x in i.values()], response))
            time.sleep(1)
        # rx_values captured into a list
        print("rx values are: ", download)
        for index, key in enumerate(download):
            for i in range(len(download[key])):
                bps_rx_a[i].append(download[key][i][0])
        print("overall download throughput values:", bps_rx_a)
        throughput = [float(f"{sum(i) / len(i)}") for i in bps_rx_a]
        keys = list(connections.keys())
        for i in range(len(throughput)):
            connections.update({keys[i]: float(f"{(throughput[i] / 1000000):.2f}")})
        return connections, throughput

    def evaluate_qos(self, connections, throughput):
        case = ""
        tos_download = {'video': [], 'voice': [], 'bk': [], 'be': []}
        tx_b = {'bk': [], 'be': [], 'video': [], 'voice': []}
        rx_a = {'bk': [], 'be': [], 'video': [], 'voice': []}
        delay = {'bk': [], 'be': [], 'video': [], 'voice': []}
        tx_endps = {}
        rx_endps = {}
        if int(self.cx_profile.side_b_min_bps) != 0:
            case = str(int(self.cx_profile.side_b_min_bps) / 1000000)
        elif int(self.cx_profile.side_a_min_bps) != 0:
            case = str(int(self.cx_profile.side_a_min_bps) / 1000000)
        if len(self.cx_profile.created_cx.keys()) > 0:
            endp_data = self.json_get('endp/all?fields=name,tx+pkts+ll,rx+pkts+ll,delay')
            endp_data.pop("handler")
            endp_data.pop("uri")
            endps = endp_data['endpoint']
            for i in range(len(endps)):
                if i < len(endps) // 2:
                    tx_endps.update(endps[i])
                if i >= len(endps) // 2:
                    rx_endps.update(endps[i])
            for sta in self.cx_profile.created_cx.keys():
                temp = sta.rsplit('-', 1)
                temp = int(temp[1])
                if temp in range(0, self.num_stations):
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['bk'].append(connections[sta])
                        tx_b['bk'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['bk'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                        delay['bk'].append(rx_endps['%s-A' % sta]['delay'])
                    else:
                        tos_download['bk'].append(float(0))
                        tx_b['bk'].append(int(0))
                        rx_a['bk'].append(int(0))
                        delay['bk'].append(int(0))
                elif temp in range(self.num_stations, 2 * self.num_stations):
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['be'].append(connections[sta])
                        tx_b['be'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['be'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                        delay['be'].append(rx_endps['%s-A' % sta]['delay'])
                    else:
                        tos_download['be'].append(float(0))
                        tx_b['be'].append(int(0))
                        rx_a['be'].append(int(0))
                        delay['be'].append(int(0))
                elif temp in range(2 * self.num_stations, 3 * self.num_stations):
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['video'].append(connections[sta])
                        tx_b['video'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['video'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                        delay['video'].append(rx_endps['%s-A' % sta]['delay'])
                    else:
                        tos_download['video'].append(float(0))
                        tx_b['video'].append(int(0))
                        rx_a['video'].append(int(0))
                        delay['video'].append(int(0))
                elif temp in range(3 * self.num_stations, 4 * self.num_stations):
                    if int(self.cx_profile.side_b_min_bps) != 0:
                        tos_download['voice'].append(connections[sta])
                        tx_b['voice'].append(int(f"{tx_endps['%s-B' % sta]['tx pkts ll']}"))
                        rx_a['voice'].append(int(f"{rx_endps['%s-A' % sta]['rx pkts ll']}"))
                        delay['voice'].append(rx_endps['%s-A' % sta]['delay'])
                    else:
                        tos_download['voice'].append(float(0))
                        tx_b['voice'].append(int(0))
                        rx_a['voice'].append(int(0))
                        delay['voice'].append(int(0))
            tos_download.update({"bkQOS": float(f"{sum(tos_download['bk']):.2f}")})
            tos_download.update({"beQOS": float(f"{sum(tos_download['be']):.2f}")})
            tos_download.update({"videoQOS": float(f"{sum(tos_download['video']):.2f}")})
            tos_download.update({"voiceQOS": float(f"{sum(tos_download['voice']):.2f}")})
            tos_download.update({"bkDELAY": sum(delay['bk'])})
            tos_download.update({"beDELAY": sum(delay['be'])})
            tos_download.update({"videoDELAY": sum(delay['video'])})
            tos_download.update({"voiceDELAY": sum(delay['voice'])})
            if sum(tx_b['bk']) != 0 or sum(tx_b['be']) != 0 or sum(tx_b['video']) != 0 or sum(tx_b['voice']) != 0:
                if sum(tx_b['bk']) > sum(rx_a['bk']):
                    tos_download.update(
                        {"bkLOSS": float(f"{((sum(tx_b['bk']) - sum(rx_a['bk'])) / sum(tx_b['bk'])) * 100:.2f}")})
                else:
                    if sum(rx_a['bk']) != 0:
                        tos_download.update({"bkLOSS": float(f"{((sum(rx_a['bk']) - sum(tx_b['bk'])) / sum(rx_a['bk'])) * 100:.2f}")})
                    else:
                        tos_download.update({"bkLOSS": float(0)})
                if sum(tx_b['be']) > sum(rx_a['be']):
                    tos_download.update(
                        {"beLOSS": float(f"{((sum(tx_b['be']) - sum(rx_a['be'])) / sum(tx_b['be'])) * 100:.2f}")})
                else:
                    if sum(rx_a['be']) != 0:
                        tos_download.update(
                            {"beLOSS": float(f"{((sum(rx_a['be']) - sum(tx_b['be'])) / sum(rx_a['be'])) * 100:.2f}")})
                    else:
                        tos_download.update({"beLOSS": float(0)})
                if sum(tx_b['video']) > sum(rx_a['video']):
                    tos_download.update(
                        {"videoLOSS": float(f"{((sum(tx_b['video']) - sum(rx_a['video'])) / sum(tx_b['video'])) * 100:.2f}")})
                else:
                    if sum(rx_a['video']) != 0:
                        tos_download.update(
                            {"videoLOSS": float(f"{((sum(rx_a['video']) - sum(tx_b['video'])) / sum(rx_a['video'])) * 100:.2f}")})
                    else:
                        tos_download.update({"videoLOSS": float(0)})
                if sum(tx_b['voice']) > sum(rx_a['voice']):
                    tos_download.update(
                        {"voiceLOSS": float(f"{((sum(tx_b['voice']) - sum(rx_a['voice'])) / sum(tx_b['voice'])) * 100:.2f}")})
                else:
                    if sum(rx_a['voice']) != 0:
                        tos_download.update(
                            {"voiceLOSS": float(
                                f"{((sum(rx_a['voice']) - sum(tx_b['voice'])) / sum(rx_a['voice'])) * 100:.2f}")})
                    else:
                        tos_download.update({"voiceLOSS": float(0)})
            tos_download.update({'tx_b': tx_b})
            tos_download.update({'rx_a': rx_a})
            tos_download.update({'delay': delay})
        else:
            print("no RX values available to evaluate QOS")
        key = case + " " + "Mbps"
        return {key: tos_download}

    def set_report_data(self, data):
        print(data)
        res = {}
        if data is not None:
            res.update(data)
        else:
            print("No Data found to generate report!")
            exit(1)
        if self.test_case is not None:
            table_df = {}
            num_stations = []
            mode = []
            graph_df = {}
            throughput = []
            for case in self.test_case:
                throughput_df = [[], [], [], []]
                pkt_loss_df = [[], [], [], []]
                latency_df = [[], [], [], []]
                if case == "2.4g" or case == "2.4G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("bgn-AX")
                elif case == "5g" or case == "5G":
                    num_stations.append("{}".format(str(len(self.sta_list))))
                    mode.append("an-AX")
                elif case == "both" or case == "BOTH":
                    num_stations.append("{} + {}".format(str(len(self.sta_list) // 2), str(len(self.sta_list) // 2)))
                    mode.append("bgn-AX + an-AX")
                for key in res[case]:
                    # if case == "both" or case == "BOTH":
                    #     key
                    throughput.append(
                        "BK : {}, BE : {}, VI: {}, VO: {}".format(res[case][key]["bkQOS"],
                                                                  res[case][key]["beQOS"],
                                                                  res[case][key][
                                                                      "videoQOS"],
                                                                  res[case][key][
                                                                      "voiceQOS"]))
                    throughput_df[0].append(res[case][key]['bkQOS'])
                    throughput_df[1].append(res[case][key]['beQOS'])
                    throughput_df[2].append(res[case][key]['videoQOS'])
                    throughput_df[3].append(res[case][key]['voiceQOS'])
                    pkt_loss_df[0].append(res[case][key]['bkLOSS'])
                    pkt_loss_df[1].append(res[case][key]['beLOSS'])
                    pkt_loss_df[2].append(res[case][key]['videoLOSS'])
                    pkt_loss_df[3].append(res[case][key]['voiceLOSS'])
                    latency_df[0].append(res[case][key]['bkDELAY'])
                    latency_df[1].append(res[case][key]['beDELAY'])
                    latency_df[2].append(res[case][key]['videoDELAY'])
                    latency_df[3].append(res[case][key]['voiceDELAY'])
                    table_df.update({"No of Stations": []})
                    table_df.update({"Mode": []})
                    table_df.update({"Throughput for Load {}".format(key): []})
                graph_df.update({case: [throughput_df, pkt_loss_df, latency_df]})
            print(throughput)
            table_df.update({"No of Stations": num_stations})
            table_df.update({"Mode": mode})
            for i in self.test_case:
                count = 0
                for key in res[i]:
                    table_df["Throughput for Load {}".format(key)].append(throughput[count])
                    count += 1
            res.update({"throughput_table_df": table_df})
            res.update({"graph_df": graph_df})
        return res

    def generate_report(self, data, test_setup_info, input_setup_info):
        res = self.set_report_data(data)
        report = lf_report(_output_pdf="throughput_qos.pdf", _output_html="throughput_qos.html")
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
        report.test_setup_table(test_setup_data=test_setup_info, value="Device Under Test")
        report.set_table_title(
            "Overall download Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
        report.build_table_title()
        df_throughput = pd.DataFrame(res["throughput_table_df"])
        report.set_table_dataframe(df_throughput)
        report.build_table()
        for key in res["graph_df"]:
            report.set_obj_html(
                _obj_title=f"Overall Download throughput for {len(self.sta_list)} clients for {key} band with different TOS.",
                _obj="The below graph represents overall download throughput for all "
                     "connected stations running BK, BE, VO, VI traffic with different "
                     "intended loads per station – {}".format(
                    "".join(str(key) for key in res[key].keys())))
            report.build_objective()

            graph = lf_bar_graph(_data_set=res["graph_df"][key][0],
                                 _xaxis_name="Load per Type of Service",
                                 _yaxis_name="Throughput (Mbps)",
                                 _xaxis_categories=[str(key) for key in res[key].keys()],
                                 _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                 _graph_image_name=f"tos_download_{key}Hz",
                                 _label=["BK", "BE", "VI", "VO"],
                                 _xaxis_step=1,
                                 _graph_title="Overall download throughput – BK,BE,VO,VI traffic streams",
                                 _title_size=16,
                                 _color=['orangered', 'olivedrab', 'steelblue', 'blueviolet'],
                                 _color_edge='black',
                                 _bar_width=0.15,
                                 _figsize=(18, 6),
                                 _legend_loc="best",
                                 _legend_box=(1.0, 1.0),
                                 _dpi=96,
                                 _show_bar_value=True,
                                 _enable_csv=True,
                                 _color_name=['orangered', 'olivedrab', 'steelblue', 'blueviolet'])
            graph_png = graph.build_bar_graph()

            print("graph name {}".format(graph_png))

            report.set_graph_image(graph_png)
            # need to move the graph image to the results directory
            report.move_graph_image()
            report.set_csv_filename(graph_png)
            report.move_csv_file()
            report.build_graph()
            report.set_obj_html(
                _obj_title=f"Overall Packet loss for {len(self.sta_list)} clients for {key} band with different TOS.",
                _obj="This graph shows the overall packet loss for the connected stations "
                     "for BK,BE,VO,VI traffic with intended load per station – {}".format(
                    "".join(str(key) for key in res[key].keys())))
            report.build_objective()

            graph = lf_bar_graph(_data_set=res["graph_df"][key][1],
                                 _xaxis_name="Load per Type of Service",
                                 _yaxis_name="Packet Loss (%)",
                                 _xaxis_categories=[str(key) for key in res[key].keys()],
                                 _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                 _graph_image_name=f"pkt_loss_{key}Hz",
                                 _label=["BK", "BE", "VI", "VO"],
                                 _xaxis_step=1,
                                 _graph_title="Load vs Packet Loss",
                                 _title_size=16,
                                 _color=['orangered', 'olivedrab', 'steelblue', 'blueviolet'],
                                 _color_edge='black',
                                 _bar_width=0.15,
                                 _dpi=96,
                                 _figsize=(18, 6),
                                 _legend_loc="best",
                                 _legend_box=(1.0, 1.0),
                                 _show_bar_value=True,
                                 _enable_csv=True,
                                 _color_name=['orangered', 'olivedrab', 'steelblue', 'blueviolet'])
            graph_png = graph.build_bar_graph()

            print("graph name {}".format(graph_png))

            report.set_graph_image(graph_png)
            # need to move the graph image to the results directory
            report.move_graph_image()
            report.set_csv_filename(graph_png)
            report.move_csv_file()
            report.build_graph()
            report.set_obj_html(
                _obj_title=f"Overall Latency for {len(self.sta_list)} clients  for {key} band with different TOS.",
                _obj="This graph shows the overall Latency for the connected stations "
                     "for BK,BE,VO,VI traffic with intended load per station – {}".format(
                    "".join(str(key) for key in res[key].keys())))
            report.build_objective()

            graph = lf_bar_graph(_data_set=res["graph_df"][key][2],
                                 _xaxis_name="Load per Type of Service",
                                 _yaxis_name="Average Latency (in milli seconds)",
                                 _xaxis_categories=[str(key) for key in res[key].keys()],
                                 _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                 _graph_image_name=f"latency_{key}Hz",
                                 _label=["BK", "BE", "VI", "VO"],
                                 _xaxis_step=1,
                                 _graph_title="Overall Download Latency – BK,BE,VO,VI traffic streams",
                                 _title_size=16,
                                 _show_bar_value=True,
                                 _color=['orangered', 'olivedrab', 'steelblue', 'blueviolet'],
                                 _color_edge='black',
                                 _bar_width=0.15,
                                 _dpi=96,
                                 _enable_csv=True,
                                 _figsize=(18, 6),
                                 _legend_loc="best",
                                 _legend_box=(1.0, 1.0),
                                 _color_name=['orangered', 'olivedrab', 'steelblue', 'blueviolet'])
            graph_png = graph.build_bar_graph()

            print("graph name {}".format(graph_png))

            report.set_graph_image(graph_png)
            # need to move the graph image to the results directory
            report.move_graph_image()
            report.set_csv_filename(graph_png)
            report.move_csv_file()
            report.build_graph()
        self.generate_individual_graph(res, report)
        report.test_setup_table(test_setup_data=input_setup_info, value="Information")
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()

    def generate_individual_graph(self, res, report):
        if len(res.keys()) > 0:
            if "throughput_table_df" in res:
                res.pop("throughput_table_df")
            if "graph_df" in res:
                res.pop("graph_df")
            for key in res:
                for load in res[key]:
                    report.set_obj_html(
                        _obj_title=f"Individual download throughput with intended load {load}/station for traffic BK(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BK "
                             f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows “"
                             f"Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph(_data_set=[res[key][load]['bk']], _xaxis_name="Number of clients",
                                         _yaxis_name="Throughput in Mbps",
                                         _xaxis_categories=[i + 1 for i in range(len(self.sta_list))],
                                         _xaxis_label=[i + 1 for i in range(len(self.sta_list))],
                                         _label=["BK"],
                                         _xaxis_step=1,
                                         _xticks_font=8,
                                         _graph_title="Individual download throughput for BK(WIFI) traffic - {} clients".format(
                                             key),
                                         _title_size=16,
                                         _bar_width=0.15,
                                         _figsize= (18, 6),
                                         _legend_loc="best",
                                         _legend_box=(1.0, 1.0),
                                         _color_name=['orangered'],
                                         _show_bar_value=True,
                                         _enable_csv=True,
                                         _graph_image_name="{}_bk_{}".format(key, load), _color_edge=['black'],
                                         _color=['orangered'])
                    graph_png = graph.build_bar_graph()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    report.set_obj_html(
                        _obj_title=f"Individual download throughput with intended load {load}/station for traffic BE(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running BE "
                             f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                             f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph(_data_set=[res[key][load]['be']], _xaxis_name="Number of clients",
                                         _yaxis_name="Throughput in Mbps",
                                         _xaxis_categories=[i + 1 for i in range(len(self.sta_list))],
                                         _xaxis_label=[i + 1 for i in range(len(self.sta_list))],
                                         _label=["BE"],
                                         _xaxis_step=1,
                                         _xticks_font=8,
                                         _graph_title="Individual download throughput for BE(WIFI) traffic - {} clients".format(
                                             key),
                                         _title_size=16,
                                         _bar_width=0.15,
                                         _figsize=(18, 6),
                                         _legend_loc="best",
                                         _legend_box=(1.0, 1.0),
                                         _color_name=['olivedrab'],
                                         _show_bar_value=True,
                                         _enable_csv=True,
                                         _graph_image_name="{}_be_{}".format(key, load), _color_edge=['black'],
                                         _color=['olivedrab'])
                    graph_png = graph.build_bar_graph()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    report.set_obj_html(
                        _obj_title=f"Individual download throughput with intended load {load}/station for traffic VI(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VI "
                             f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                             f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph(_data_set=[res[key][load]['video']], _xaxis_name="Number of clients",
                                         _yaxis_name="Throughput in Mbps",
                                         _xaxis_categories=[i + 1 for i in range(len(self.sta_list))],
                                         _xaxis_label=[i + 1 for i in range(len(self.sta_list))],
                                         _label=["Video"],
                                         _xaxis_step=1,
                                         _xticks_font=8,
                                         _graph_title="Individual download throughput for VI(WIFI) traffic - {} clients".format(
                                             key),
                                         _title_size=16,
                                         _bar_width=0.15,
                                         _figsize=(18, 6),
                                         _legend_loc="best",
                                         _legend_box=(1.0, 1.0),
                                         _show_bar_value=True,
                                         _color_name=['steelblue'],
                                         _enable_csv=True,
                                         _graph_image_name="{}_video_{}".format(key, load),
                                         _color_edge=['black'],
                                         _color=['steelblue'])
                    graph_png = graph.build_bar_graph()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    report.set_obj_html(
                        _obj_title=f"Individual download throughput with intended load {load}/station for traffic VO(WiFi).",
                        _obj=f"The below graph represents individual throughput for {len(self.sta_list)} clients running VO "
                             f"(WiFi) traffic.  X- axis shows “number of clients” and Y-axis shows "
                             f"“Throughput in Mbps”.")
                    report.build_objective()
                    graph = lf_bar_graph(_data_set=[res[key][load]['voice']], _xaxis_name="Number of clients",
                                         _yaxis_name="Throughput in Mbps",
                                         _xaxis_categories=[i + 1 for i in range(len(self.sta_list))],
                                         _xaxis_label=[i + 1 for i in range(len(self.sta_list))],
                                         _label=['Voice'],
                                         _xaxis_step=1,
                                         _xticks_font=8,
                                         _graph_title="Individual download throughput for VO(WIFI) traffic - {} clients".format(
                                             key),
                                         _title_size=16,
                                         _bar_width=0.15,
                                         _figsize=(18, 6),
                                         _legend_loc="best",
                                         _legend_box=(1.0, 1.0),
                                         _show_bar_value=True,
                                         _color_name=['blueviolet'],
                                         _enable_csv=True,
                                         _graph_image_name="{}_voice_{}".format(key, load),
                                         _color_edge=['black'],
                                         _color=['blueviolet'])
                    graph_png = graph.build_bar_graph()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
                    report.set_obj_html(
                        _obj_title=f"Individual download average latency with intended load {load}/station for traffic VO(WiFi).",
                        _obj=f"The below graph represents individual avg latency for {len(self.sta_list)} clients running VO "
                             f"(WiFi) traffic.  X- axis shows “Number of Clients” and Y-axis shows "
                             f"“Avg Latency in milli seconds”.")
                    report.build_objective()
                    graph = lf_bar_graph(_data_set=[res[key][load]['delay']['voice']],
                                         _xaxis_name="Number of clients",
                                         _yaxis_name="Average Latency in milli seconds(ms)",
                                         _xaxis_categories=[i + 1 for i in range(len(self.sta_list))],
                                         _xaxis_label=[i + 1 for i in range(len(self.sta_list))],
                                         _label=['Voice'],
                                         _xaxis_step=1,
                                         _xticks_font=8,
                                         _graph_title="Individual download average latency for VO(WIFI) traffic - {} clients".format(
                                             key),
                                         _title_size=16,
                                         _bar_width=0.15,
                                         _figsize=(18, 6),
                                         _legend_loc="best",
                                         _legend_box=(1.0, 1.0),
                                         _show_bar_value=True,
                                         _color_name=['blueviolet'],
                                         _enable_csv=True,
                                         _graph_image_name="{}_latency_voice{}".format(key, load),
                                         _color_edge=['black'],
                                         _color=['blueviolet'])
                    graph_png = graph.build_bar_graph()
                    print("graph name {}".format(graph_png))
                    report.set_graph_image(graph_png)
                    # need to move the graph image to the results
                    report.move_graph_image()
                    report.set_csv_filename(graph_png)
                    report.move_csv_file()
                    report.build_graph()
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
-----------------------
To Test with 2.4GHz clients, use: 
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_2g wiphy0 --ssid_2g testqos --passwd_2g [BLANK] --security_2g open --upstream eth1 --test_duration 1m --download 1000000 --bands 2.4g 

To Test with 5GHz clients, use:
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_5g wiphy0 --ssid_5g testqos --passwd_5g [BLANK] --security_5g open --upstream eth1 --test_duration 1m --download 1000000 --bands 5g 

To Test with 2.4GHz & 5GHz clients (BOTH), use:
python3 throughput_qos.py --ap_name WAX610 --mgr localhost --mgr_port 8080 --num_stations 32 --radio_2g wiphy0 --ssid_2g testqos --passwd_2g [BLANK] --security_2g open --radio_5g wiphy0 --ssid_5g testqos --passwd_5g [BLANK] --security_5g open --radio_5g wiphy1 --ssid_5g testqos --passwd_5g [BLANK] --security_5g open –upstream eth1 --test_duration 1m --download 1000000 --bands both 
''')
    parser.add_argument('--mode', help='Used to force mode of stations', default="0")
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=True)
    parser.add_argument('--download', help='--download traffic load per connection (download rate)', default=256000)
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="2m")
    parser.add_argument('--create_sta', help='Used to force a connection to a particular AP', action='store_true')
    parser.add_argument('--sta_names', help='Used to force a connection to a particular AP', default="sta0000")
    parser.add_argument('--ap_name', help="AP Model Name", default="Test-AP")
    parser.add_argument('--bands', help='used to run on multiple radio bands,can be used with multiple stations',
                        default="2.4G, 5G, BOTH", required=True)
    parser.add_argument('--ssid_2g', help="ssid for  2.4Ghz band")
    parser.add_argument('--security_2g', help="security type for  2.4Ghz band")
    parser.add_argument('--passwd_2g', help="password for 2.4Ghz band")
    parser.add_argument('--ssid_5g', help="ssid for  5Ghz band")
    parser.add_argument('--security_5g', help="security type  for  5Ghz band")
    parser.add_argument('--passwd_5g', help="password for  5Ghz band")
    parser.add_argument('--radio_2g', help="radio which supports 2.4G bandwidth", default="wiphy0")
    parser.add_argument('--radio_5g', help="radio which supports 5G bandwidth", default="wiphy1")
    args = parser.parse_args()
    print("--------------------------------------------")
    print(args)
    print("--------------------------------------------")
    args.test_case = args.bands.split(',')
    test_results = {}
    loads = {}
    bands = []
    station_list = []
    data = {}

    if args.download is not None:
        loads = {'upload': [], 'download': str(args.download).split(",")}
        for i in range(len(args.download)):
            loads['upload'].append(0)
    else:
        raise "Download traffic is required."

    if args.bands is not None:
        bands = args.bands.split(',')

    if args.test_duration.endswith('s') or args.test_duration.endswith('S'):
        args.test_duration = int(args.test_duration[0:-1])
    elif args.test_duration.endswith('m') or args.test_duration.endswith('M'):
        args.test_duration = int(args.test_duration[0:-1]) * 60
    elif args.test_duration.endswith('h') or args.test_duration.endswith('H'):
        args.test_duration = int(args.test_duration[0:-1]) * 60 * 60
    elif args.test_duration.endswith(''):
        args.test_duration = int(args.test_duration)

    test_start_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test started at: ", test_start_time)

    for i in range(len(bands)):
        if bands[i] == "2.4G" or bands[i] == "2.4g":
            args.bands = bands[i]
            args.mode = 13
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000, radio=args.radio_2g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "5G" or bands[i] == "5g":
            args.bands = bands[i]
            args.mode = 14
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=int(args.num_stations) - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_5g)
            else:
                station_list = args.sta_names.split(",")
        elif bands[i] == "BOTH" or bands[i] == "both":
            args.bands = bands[i]
            args.mode = 0
            if (int(args.num_stations) % 2) != 0:
                print("Number of stations for Both Band should be even in number.")
                exit(1)
            mid = int(args.num_stations) // 2
            if args.create_sta:
                station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=mid - 1,
                                                      padding_number_=10000,
                                                      radio=args.radio_2g)
                station_list.extend(LFUtils.portNameSeries(prefix_="sta", start_id_=mid,
                                                           end_id_=int(args.num_stations) - 1,
                                                           padding_number_=10000,
                                                           radio=args.radio_5g))
            else:
                station_list = args.sta_names.split(",")
        else:
            print("Band " + bands[i] + " Not Exist")
            exit(1)
        # ---------------------------------------#
        for index in range(len(loads["download"])):
            throughput_qos = ThroughputQOS(host=args.mgr,
                                           port=args.mgr_port,
                                           number_template="0000",
                                           ap_name=args.ap_name,
                                           num_stations=int(args.num_stations),
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
                                           radio_2g=args.radio_2g,
                                           radio_5g=args.radio_5g,
                                           test_duration=args.test_duration,
                                           use_ht160=False,
                                           side_a_min_rate=int(loads['upload'][index]),
                                           side_b_min_rate=int(loads['download'][index]),
                                           mode=args.mode,
                                           bands=args.bands,
                                           traffic_type=args.traffic_type,
                                           tos="BK,BE,VI,VO",
                                           test_case=args.test_case,
                                           _debug_on=args.debug)
            throughput_qos.pre_cleanup()
            throughput_qos.build()

            # if args.create_sta:
            #     if not throughput_qos.passes():
            #         print(throughput_qos.get_fail_message())
            #         throughput_qos.exit_fail()

            throughput_qos.start(False, False)
            time.sleep(10)
            connections, throughput = throughput_qos.monitor()
            throughput_qos.stop()
            time.sleep(5)
            test_results.update(throughput_qos.evaluate_qos(connections, throughput))
            data.update({bands[i]: test_results})
            if args.create_sta:
                if not throughput_qos.passes():
                    print(throughput_qos.get_fail_message())
                    throughput_qos.exit_fail()
                #LFUtils.wait_until_ports_admin_up(port_list=station_list)
                if throughput_qos.passes():
                    throughput_qos.success()
                throughput_qos.cleanup()

    test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
    print("Test ended at: ", test_end_time)
    test_setup_info = {
        "AP Model": throughput_qos.ap_name,
        "SSID": throughput_qos.ssid,
        "SSID - 2.4 Ghz": throughput_qos.ssid_2g,
        "SSID - 5 Ghz": throughput_qos.ssid_5g,
        "Test Duration": datetime.strptime(test_end_time, "%b %d %H:%M:%S") - datetime.strptime(
            test_start_time, "%b %d %H:%M:%S")
    }
    if throughput_qos.ssid is None:
        test_setup_info.pop("SSID")
    else:
        if throughput_qos.ssid_2g is None:
            test_setup_info.pop("SSID - 2.4 Ghz")
        if throughput_qos.ssid_5g is None:
            test_setup_info.pop("SSID - 5 Ghz")
    input_setup_info = {
        "contact": "support@candelatech.com"
    }
    throughput_qos.generate_report(data=data, test_setup_info=test_setup_info, input_setup_info=input_setup_info)


if __name__ == "__main__":
    main()

