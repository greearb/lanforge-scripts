#!/usr/bin/env python3

"""
    This script is to run check Band Steering.
"""

import sys
import os
import argparse
import time

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
from realm import Realm
import realm
import pprint

from lf_report import lf_report
from lf_graph import lf_bar_graph


class BandSteering(Realm):
    def __init__(self,
                 _ssid=None,
                 _security=None,
                 _password=None,
                 _host=None,
                 _port=None,
                 _sta_list=None,
                 _side_a_min_rate=56,
                 _side_a_max_rate=0,
                 _side_b_min_rate=56,
                 _side_b_max_rate=0,
                 _num_sta=1,
                 _iter=10,
                 _number_template="00000",
                 _radio="wiphy0",
                 _radio_2g="wiphy1",
                 _radio_5g="wiphy2",
                 _proxy_str=None,
                 _debug_on=False,
                 _up=True,
                 _name_prefix='',
                 _set_txo_data=None,
                 _traffic_type="lf_udp",
                 _upstream="eth1",
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=_host,
                         lfclient_port=_port)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.security = _security
        self.password = _password
        self.sta_list = _sta_list
        self.side_a_min_rate = _side_a_min_rate
        self.side_a_max_rate = _side_a_max_rate
        self.side_b_min_rate = _side_b_min_rate
        self.side_b_max_rate = _side_b_max_rate
        self.name_prefix = _name_prefix
        self.num_sta = _num_sta
        self.iter = _iter
        self.upstream = _upstream
        self.radio = _radio
        self.radio_2g = _radio_2g
        self.radio_5g = _radio_5g
        self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.up = _up
        self.traffic_type=_traffic_type
        self.set_txo_data = _set_txo_data
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0
        if self.debug:
            print("----- Station List ----- ----- ----- ----- ----- ----- \n")
            pprint.pprint(self.sta_list)
            print("---- ~Station List ----- ----- ----- ----- ----- ----- \n")
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = self.side_a_min_rate
        self.cx_profile.side_a_max_bps = self.side_a_max_rate
        self.cx_profile.side_b_min_bps = self.side_b_min_rate
        self.cx_profile.side_b_max_bps = self.side_b_max_rate

    def precleanup(self):

        self.station_profile.cleanup(desired_stations=self.station_list, delay=1, debug_=self.debug)

        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,
                                           port_list=self.station_list,
                                           debug=self.debug)

        time.sleep(1)
        self.remove_all_cxs(remove_all_endpoints=True)

    print("precleanup done")

    def build(self):
        if not self.port_exists("sta0000"):
        # Build stations
            self.station_profile.use_security(self.security, self.ssid, self.password)
            self.station_profile.set_number_template(self.number_template)

            print("Creating stations")
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            if self.set_txo_data is not None:
                self.station_profile.set_wifi_txo(txo_ena=self.set_txo_data["txo_enable"],
                                                  tx_power=self.set_txo_data["txpower"],
                                                  pream=self.set_txo_data["pream"],
                                                  mcs=self.set_txo_data["mcs"],
                                                  nss=self.set_txo_data["nss"],
                                                  bw=self.set_txo_data["bw"],
                                                  retries=self.set_txo_data["retries"],
                                                  sgi=self.set_txo_data["sgi"], )
            self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
            if self.up:
                self.station_profile.admin_up()

            self._pass("PASS: Station build finished")
        # else:
        #     print("Port already exists...")
        #     self.admin_down("sta0000")
        #     time.sleep(1)
        #     self.admin_up("sta0000")

    def run(self):
        if self.wait_for_ip(self.sta_list):
             print("Stations got IP")
             url = "/port/1/1/sta0000/channel?fields=channel"
             channel = self.json_get(url, debug_=False)['interface']
        else:
          raise Exception("failed to get ip for stations")
        # Build stations
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        if int(channel['channel']) in range(1, 15):
            station_list = LFUtils.port_name_series(prefix="sta",
                                                    start_id=self.num_sta,
                                                    end_id=self.num_sta,
                                                    padding_number=10000,
                                                    radio=self.radio_2g)
            print("Creating %s station" % self.num_sta)
            self.station_profile.create(radio=self.radio_2g, sta_names_=station_list,
                                        debug=self.debug)
            if self.up:
                self.station_profile.admin_up()
            self.cx_profile.create(endp_type=self.traffic_type,
                                   side_a=self.upstream,
                                   side_b=station_list,
                                   sleep_time=0)
            if self.wait_for_ip(station_list):
                self.cx_profile.start_cx()

        elif int(channel['channel']) in range(34, 174):
            station_list = LFUtils.port_name_series(prefix="sta",
                                                    start_id=self.num_sta,
                                                    end_id=self.num_sta,
                                                    padding_number=10000,
                                                    radio=self.radio_5g)
            print("Creating %s station" % self.num_sta)
            self.station_profile.create(radio=self.radio_5g, sta_names_=station_list,
                                        debug=self.debug)
            if self.up:
                self.station_profile.admin_up()
            self.cx_profile.create(endp_type=self.traffic_type,
                                   side_a=self.upstream,
                                   side_b=station_list,
                                   sleep_time=0)
            if self.wait_for_ip(station_list):
                self.cx_profile.start_cx()

        time.sleep(5)
        self.admin_down("sta0000")
        time.sleep(1)
        self.admin_up("sta0000")
        if self.wait_for_ip(self.sta_list):
            print("Stations got IP")
        else:
            raise Exception("failed to get ip for station sta0000")

        # self.rm_port("sta0000", check_exists=True)

    def get_data(self):
        # x-axis iterations, y-axis station mode
        mode = []
        iterations = self.iter
        sta_names = self.get_station_names()  
        for sta in sta_names:
            channel = self.json_get("/port/1/1/%s/channel?fields=channel" % sta)['interface']
            if int(channel['channel']) in range(1, 15):
                mode.append('2.4GHz')
            elif int(channel['channel']) in range(34, 174):
                mode.append('5GHz')
        return mode

    def get_station_names(self):
        sta_names = []
        port_data = self.json_get("/port/1/1?fields=alias")['interfaces']
        print(port_data)
        for port in port_data:
            for key, value in port.items():
                if 'sta' in value['alias']:
                    sta_names.append(value['alias'])
        # sta_names.pop(0)
        return sta_names

    def cleanup(self):
        # self.cx_profile.cleanup()
        self.remove_all_cxs(remove_all_endpoints=True)
        self.station_profile.station_names = self.get_station_names()
        self.station_profile.cleanup()

    def generate_report(self):
        report = lf_report(_output_pdf="band_steering.pdf", _output_html="band_steering.html")

        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()

        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))

        report.set_title("Band Steering")
        report.build_banner()

        # report.set_table_title("Title One")
        # report.build_table_title()

        # report.set_table_dataframe(dataframe)
        # report.build_table()

        data = self.get_data()
        y_5g = []
        y_2g = []
        x_axis_values = []
        for i in range(len(data)):
            if data[i] == '5GHz':
                y_5g.append(5)
            else:
                y_5g.append(0)
            if data[i] == '2.4GHz':
                y_2g.append(2.4)
            else:
                y_2g.append(0)

        for i in range(1, int(self.iter)+1):
            x_axis_values.append(i)

        # test lf_graph in report
        dataset = [y_5g, y_2g]

        report.set_graph_title("Band vs Stations")
        report.build_graph_title()

        graph = lf_bar_graph(_data_set=dataset,
                             _xaxis_name="stations",
                             _yaxis_name="Frequency in (GHz)",
                             _xaxis_categories=x_axis_values,
                             _graph_image_name="band-steering-stations",
                             _label=["5GHz", "2.4GHz"],
                             _color=['darkorange', 'forestgreen'],
                             _color_edge='black',
                             _grp_title="Band Steering vs Stations",
                             _xaxis_step=1,
                             _show_bar_value=False,
                             _text_font=7,
                             _text_rotation=45,
                             _xticks_font=8)

        graph_png = graph.build_bar_graph()

        report.set_graph_image(graph_png)
        # need to move the graph image to the results
        report.move_graph_image()

        report.build_graph()
        report.build_footer_no_png()

        html_file = report.write_html()
        print("returned file ")
        print(html_file)
        report.write_pdf()

        print("report path {}".format(report.get_path()))


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='bs_obj.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Create stations
            ''',

        description='''\
        bs_obj.py
--------------------
Command example:
./bs_obj.py
    --radio wiphy0
    --radio_2g wiphy1
    --radio_5g wiphy2
    --num_stations 3
    --security open
    --ssid netgear
    --passwd BLANK
    --debug
            ''')
    required = parser.add_argument_group('required arguments')
    # required.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', required=True)
    parser.add_argument("--radio_2g", help="radio for 2.4 Ghz")
    parser.add_argument("--radio_5g", help="radio for 5 Ghz")
    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)
    parser.add_argument('--iter', help="--iter is used to provide number of iterations", default=10)
    parser.add_argument('--traffic_type',help="traffic type tcp or udp,for tcp lf_tcp and udp lf_udp",default="lf_udp")
    args = parser.parse_args()
    print(args)
    # if args.debug:
    #    pprint.pprint(args)
    #    time.sleep(5)
    if args.radio is None:
        raise ValueError("--radio required")

    num_sta = 1
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_stations_converted = int(args.num_stations)
        num_sta = num_stations_converted

    station_list = LFUtils.port_name_series(prefix="sta",
                                            start_id=0,
                                            end_id=num_sta - 1,
                                            padding_number=10000,
                                            radio=args.radio)
    created_cx=[]

    for i in range(int(args.iter)):
        bs_obj = BandSteering(_host=args.mgr,
                              _port=args.mgr_port,
                              _ssid=args.ssid,
                              _password=args.passwd,
                              _security=args.security,
                              _sta_list=station_list,
                              _radio=args.radio,
                              _radio_2g=args.radio_2g,
                              _radio_5g=args.radio_5g,
                              _set_txo_data=None,
                              _traffic_type=args.traffic_type,
                              _proxy_str=args.proxy,
                              _side_a_min_rate=args.a_min,
                              _side_b_min_rate=args.b_min,
                              _num_sta=num_sta,
                              _iter=args.iter,
                              _debug_on=args.debug)
        if i == 0:
            bs_obj.cleanup()
        bs_obj.build()
        print('Created %s stations' % num_sta)
        bs_obj.run()
        num_sta += 1
        created_cx.append(bs_obj.cx_profile.created_cx)
    for cx in created_cx:
        for cx_val in cx.keys():
            bs_obj.stop_cx(cx_val)

    # bs_obj.cx_profile.stop_cx()

    bs_obj.generate_report()


if __name__ == "__main__":
    main()
