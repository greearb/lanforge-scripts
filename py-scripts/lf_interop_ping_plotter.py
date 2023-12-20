#!/usr/bin/env python3

'''
    NAME: lf_interop_ping_plotter.py

    PURPOSE: lf_interop_ping_plotter.py will let the user select real devices, virtual devices or both and then allows them to run
    ping test for user given duration and packet interval on the given target IP or domain name and generates realtime ping status and line charts for every device.

    EXAMPLE-1:
    Command Line Interface to run ping test with only virtual clients
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103  --target 192.168.1.3 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2 
    --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --debug

    EXAMPLE-2:
    Command Line Interface to run ping test with only real clients
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --ssid RDT_wpa2 --security wpa2_personal
    --passwd OpenWifi

    EXAMPLE-3:
    Command Line Interface to run ping test with both real and virtual clients
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --target 192.168.1.3 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61

    EXAMPLE-4:
    Command Line Interface to run ping test with existing Wi-Fi configuration on the real devices
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --target 192.168.1.61 --ping_interval 5 --ping_duration 1 --passwd OpenWifi --use_default_config
    
    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES: Performance, Functional, Report Generation

    NOTES:
    1.Use './lf_interop_ping.py --help' to see command line usage and options
    2.Please pass ping_duration in minutes
    3.Please pass ping_interval in seconds
    4.After passing the cli, if --real flag is selected, then a list of available real devices will be displayed on the terminal.
    5.Enter the real device resource numbers seperated by commas (,)

    STATUS: BETA RELEASE

    VERIFIED_ON:
    Working date    - 19/12/2023
    Build version   - 5.4.7
    kernel version  - 6.2.16+

    License: Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc.
'''

import argparse
import time
import sys
import os
import pandas as pd
import importlib
import logging
import matplotlib.pyplot as plt
import csv

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

if 'py-scripts' not in sys.path:
    sys.path.append('/home/agent11/Desktop/lanforge-scripts/py-scripts')
    # sys.path.append('/home/lanforge/lanforge-scripts/py-scripts')

from lf_base_interop_profile import RealDevice
from datetime import datetime, timedelta
from lf_graph import lf_bar_graph_horizontal
from lf_graph import lf_bar_graph
from lf_report import lf_report
from station_profile import StationProfile
import interop_connectivity
from LANforge import LFUtils

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm


class Ping(Realm):
    def __init__(self,
                 host=None,
                 port=None,
                 ssid=None,
                 security=None,
                 password=None,
                 radio=None,
                 target=None,
                 interval=None,
                 lanforge_password='lanforge',
                 sta_list=None,
                 virtual=None,
                 duration=1,
                 real=None,
                 debug=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port)
        self.host = host
        self.lanforge_password = lanforge_password
        self.port = port
        self.lfclient_host = host
        self.lfclient_port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.radio = radio
        self.target = target
        self.interval = interval
        self.debug = debug
        self.sta_list = sta_list
        self.real_sta_list = []
        self.real_sta_data_dict = {}
        self.enable_virtual = virtual
        self.enable_real = real
        self.duration = duration
        self.android = 0
        self.virtual = 0
        self.linux = 0
        self.windows = 0
        self.mac = 0
        self.result_json = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'lfping'
        self.generic_endps_profile.dest = self.change_target_to_ip()
        self.generic_endps_profile.interval = self.interval
        self.Devices = None
        self.start_time = ""
        self.stop_time = ""

    def change_target_to_ip(self):

        # checking if target is an IP or a port
        if(self.target.count('.') != 3):
            # checking if target is eth1 or 1.1.eth1
            target_port_list = self.name_to_eid(self.target)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get('/port/{}/{}/{}?fields=ip'.format(shelf, resource, port))['interface']['ip']
            except:
                logging.error('The target port {} not found on the LANforge. Please change the target.'.format(self.target))
                exit(0)
            self.target = target_port_ip
            print(self.target)
        else:
            print(self.target)
        return self.target

    def cleanup(self):

        if (self.enable_virtual):
            # removing virtual stations if existing
            for station in self.sta_list:
                logging.info('Removing the station {} if exists'.format(station))
                self.generic_endps_profile.created_cx.append(
                    'CX_generic-{}'.format(station.split('.')[2]))
                self.generic_endps_profile.created_endp.append(
                    'generic-{}'.format(station.split('.')[2]))
                self.rm_port(station, check_exists=True)

            if (not LFUtils.wait_until_ports_disappear(base_url=self.host, port_list=self.sta_list, debug=self.debug)):
                logging.info('All stations are not removed or a timeout occured.')
                logging.error('Aborting the test.')
                exit(0)

        if (self.enable_real):
            # removing generic endpoints for real devices if existing
            for station in self.real_sta_list:
                self.generic_endps_profile.created_cx.append(
                    'CX_generic-{}'.format(station))
                self.generic_endps_profile.created_endp.append(
                    'generic-{}'.format(station))

        logging.info('Cleaning up generic endpoints if exists')
        self.generic_endps_profile.cleanup()
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []
        logging.info('Cleanup Successful')

    # Args:
    #   devices: Connected RealDevice object which has already populated tracked real device
    #            resources through call to get_devices()
    def select_real_devices(self, real_devices, real_sta_list=None, base_interop_obj=None):
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_devices.query_user()
        else:
            self.real_sta_list = real_sta_list
        if base_interop_obj is not None:
            self.Devices = base_interop_obj

        # Need real stations to run interop test
        if (len(self.real_sta_list) == 0):
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        logging.info('{}'.format(*self.real_sta_list))

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logger.error('Real station not in devices data')
                raise ValueError('Real station not in devices data')

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        # Track number of selected devices
        self.android = self.Devices.android
        self.windows = self.Devices.windows
        self.mac = self.Devices.mac
        self.linux = self.Devices.linux

    def buildstation(self):
        logging.info('Creating Stations {}'.format(self.sta_list))
        for station_index in range(len(self.sta_list)):
            shelf, resource, port = self.sta_list[station_index].split('.')
            logging.info('{} {} {}'.format(shelf, resource, port))
            station_object = StationProfile(lfclient_url='http://{}:{}'.format(self.host, self.port), local_realm=self, ssid=self.ssid,
                                            ssid_pass=self.password, security=self.security, number_template_='00', up=True, resource=resource, shelf=shelf)
            station_object.use_security(
                security_type=self.security, ssid=self.ssid, passwd=self.password)

            station_object.create(radio=self.radio, sta_names_=[
                self.sta_list[station_index]])
        station_object.admin_up()
        if self.wait_for_ip([self.sta_list[station_index]]):
            self._pass("All stations got IPs", print_=True)
        else:
            self._fail(
                "Stations failed to get IPs", print_=True)

    def check_tab_exists(self):
        response = self.json_get("generic")
        if response is None:
            return False
        else:
            return True

    def create_generic_endp(self):
        # Virtual stations are tracked in same list as real stations, so need to separate them
        # in order to create generic endpoints for just the virtual stations
        virtual_stations = list(set(self.sta_list).difference(set(self.real_sta_list)))

        if (self.enable_virtual):
            if (self.generic_endps_profile.create(ports=virtual_stations, sleep_time=.5)):
                logging.info('Virtual client generic endpoint creation completed.')
            else:
                logging.error('Virtual client generic endpoint creation failed.')
                exit(0)

        if (self.enable_real):
            real_sta_os_types = [self.real_sta_data_dict[real_sta_name]['ostype'] for real_sta_name in self.real_sta_data_dict]

            if (self.generic_endps_profile.create(ports=self.real_sta_list, sleep_time=.5, real_client_os_types=real_sta_os_types)):
                logging.info('Real client generic endpoint creation completed.')
            else:
                logging.error('Real client generic endpoint creation failed.')
                exit(0)
        
        # setting endpoint report time to ping packet interval
        for endpoint in self.generic_endps_profile.created_endp:
            self.generic_endps_profile.set_report_timer(endp_name=endpoint, timer=250)

    def start_generic(self):
        self.generic_endps_profile.start_cx()
        self.start_time = datetime.now()

    def stop_generic(self):
        self.generic_endps_profile.stop_cx()        
        self.stop_time = datetime.now()

    def get_results(self):
        # logging.info(self.generic_endps_profile.created_endp)
        results = self.json_get(
            "/generic/{}".format(','.join(self.generic_endps_profile.created_endp)))
        if (len(self.generic_endps_profile.created_endp) > 1):
            results = results['endpoints']
        else:
            results = results['endpoint']
        return (results)

    def generate_remarks(self, station_ping_data):
        remarks = []

        #NOTE if there are any more ping failure cases that are missed, add them here.

        # checking if ping output is not empty
        if(station_ping_data['last_result'] == ""):
            remarks.append('No output for ping')

        # illegal division by zero error. Issue with arguments.
        if('Illegal division by zero' in station_ping_data['last_result']):
            remarks.append('Illegal division by zero error. Please re-check the arguments passed.')

        # unknown host
        if('Totals:  *** dropped: 0  received: 0  failed: 0  bytes: 0' in station_ping_data['last_result'] or 'unknown host' in station_ping_data['last_result']):
            remarks.append('Unknown host. Please re-check the target')

        # checking if IP is existing in the ping command or not for Windows device
        if(station_ping_data['os'] == 'Windows'):
            if('None' in station_ping_data['command'] or station_ping_data['command'].split('-n')[0].split('-S')[-1] == "  "):
                remarks.append('Station has no IP')

        # network buffer overflow
        if('ping: sendmsg: No buffer space available' in station_ping_data['last_result']):
            remarks.append('Network buffer overlow')

        # checking for no ping states
        if(float(station_ping_data['min_rtt'].replace(',','')) == 0 and float(station_ping_data['max_rtt'].replace(',','')) == 0 and float(station_ping_data['avg_rtt'].replace(',','')) == 0):

            # Destination Host Unreachable state
            if('Destination Host Unreachable' in station_ping_data['last_result']):
                remarks.append('Destination Host Unrechable')

            # Name or service not known state
            if('Name or service not known' in station_ping_data['last_result']):
                remarks.append('Name or service not known')

            # network buffer overflow
            if('ping: sendmsg: No buffer space available' in station_ping_data['last_result']):
                remarks.append('Network buffer overlow')

        return(remarks)

    def generate_uptime_graph(self):
        json_data = {}
        for station in self.result_json:
            json_data[station] = {
                'rtts': {}
            }
            # print('------------',json_data)
            for seq in self.result_json[station]['rtts']:
                json_data[station]['rtts'][str(seq)] = self.result_json[station]['rtts'][seq]
        self.graph_values = json_data
        device_names = list(json_data.keys())
        sequence_numbers = list(set(seq for device_data in json_data.values() for seq in device_data.get("rtts", {})))
        # print(sequence_numbers)
        rtt_values = {}
        for seq in sequence_numbers:
            rtt_values[seq] = []
            for device_data in json_data.values():
                if("rtts" in device_data.keys()):
                    if(seq in device_data['rtts'].keys()):
                        rtt_values[seq].append(device_data['rtts'][seq])
                    else:
                        rtt_values[seq].append(1)
        # rtt_values = {seq: [device_data.get("rtts", {}).get(seq, 0) for device_data in json_data.values()] for seq in sequence_numbers}
        # print(rtt_values)
        # Set different colors based on RTT values
        colors = [['red' if rtt == 0 else 'green' for rtt in rtt_values[seq]] for seq in sequence_numbers]

        # Create a stacked horizontal bar graph
        bar_width = 1
        plt.figure(figsize=(15, len(device_names) * .5 + 4))
        # y_positions = np.arange(len(device_names)) * (bar_width + 1)  # Adjust the 0.1 to control the gap
        for i, device_name in enumerate(device_names):
            # plt.barh(device_name, 1, color='white', height=0.5)
            for j, seq in enumerate(sequence_numbers):
                plt.barh(device_name, 1, left=int(seq) - 1, color=colors[j][i], height=0.1)

        # Customize the plot
        plt.xlabel('Sequence Number')
        plt.title('Client Status vs Time')
        # plt.legend(sequence_numbers, title='Sequence Numbers', loc='upper right')

        # Remove y-axis labels
        # plt.yticks([])

        # building timestamps
        start_time = self.start_time
        interval = timedelta(seconds=int(self.interval))

        timestamps = []
        for seq_num in sequence_numbers:
            timestamp = ((int(seq_num) -1) * interval + start_time).strftime("%H:%M:%S")
            timestamps.append(timestamp)

        # settings labels for x-axis
        # print(list(map(int,sequence_numbers)))
        # print(list(map(int,sequence_numbers))[0::10])
        # print(timestamps)

        ticks_sequence_numbers =  list(map(int,sequence_numbers))
        ticks_sequence_numbers.sort()
        timestamps.sort()
        # print('--------------')
        # print(ticks_sequence_numbers[0::10])
        # print(timestamps[0::10])
        plt.xticks(range(0, len(sequence_numbers), max(round(len(sequence_numbers) / 30), len(sequence_numbers) // 30)), timestamps[::max(round(len(sequence_numbers) / 30), len(sequence_numbers) // 30)], rotation=45)

        # plt.xlim(0, max([max(rtt_values[seq]) for seq in sequence_numbers]))

        plt.xlim(0, max(list(map(int, sequence_numbers))))

        # print('working xlim', max([max(rtt_values[seq]) for seq in sequence_numbers]))

        # fixing the number of ticks to 30 in x-axis
        # plt.locator_params(axis='x', nbins=30)

        # Show the plot
        # plt.show()
        plt.savefig("%s.png" % "uptime_graph", dpi=96)
        plt.close()

        logger.debug("{}.png".format("uptime_graph"))
        return("%s.png" % "uptime_graph")
    
    def build_area_graphs(self, report_obj=None):
        json_data = self.graph_values
        device_names = list(json_data.keys())
        sequence_numbers = []
        for device_data in json_data.values():
            for seq in device_data.get('rtts', {}):
                if(seq not in sequence_numbers and device_data['rtts'][seq] != 0.11):
                    sequence_numbers.append(seq)
        sequence_numbers = list(set(seq for device_data in json_data.values() for seq in device_data.get("rtts", {})))

        # Plot line graphs for each device
        for device_name, device_data in json_data.items():
            rtts = []
            dropped_seqs = []
            for seq in sequence_numbers:
                if('rtts' in device_data.keys()):
                    if(seq in device_data['rtts'].keys()):
                            rtts.append(device_data['rtts'][seq])
            # rtts = [device_data.get("rtts", {}).get(seq, 0) for seq in sequence_numbers]
            plt.figure(figsize=(15, len(device_names) * .5 + 4))
            plt.plot(sequence_numbers, rtts, label=device_name, color="Slateblue", alpha=0.6)

            # for area chart
            plt.fill_between(sequence_numbers, rtts, color="skyblue", alpha=0.2)

            # Customize the plot
            plt.xlabel('Time')
            plt.ylabel('RTT (ms)')
            plt.title('RTT vs Time for {}'.format(device_name))
            plt.legend(loc='upper right')
            # plt.grid(True)
            # building timestamps
            start_time = self.start_time
            interval = timedelta(seconds=int(self.interval))

            timestamps = []
            for seq_num in sequence_numbers:
                timestamp = ((int(seq_num) -1) * interval + start_time).strftime("%H:%M:%S")
                timestamps.append(timestamp)

            # generating csv
            with open('{}/{}.csv'.format(report_obj.path_date_time,device_name), 'w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(['Time', 'RTT (ms)'])
                for row in range(len(timestamps)):
                    writer.writerow([timestamps[row], rtts[row]])
                # writer.writerows([timestamps, rtts])

            ticks_sequence_numbers =  list(map(int,sequence_numbers))
            ticks_sequence_numbers.sort()
            timestamps.sort()

            # settings labels for x-axis
            plt.xticks(range(0, len(sequence_numbers), max(round(len(sequence_numbers) / 30), len(sequence_numbers) // 30)), timestamps[::max(round(len(sequence_numbers) / 30), len(sequence_numbers) // 30)], rotation=45)

            # print(sequence_numbers)
            # print(rtts)
            # plt.xlim(0, max(rtts))
            plt.xlim(0, max(list(map(int, sequence_numbers))))

            # Show the plot
            # plt.show()
            plt.savefig("%s.png" % device_name, dpi=96)
            graph_name = "%s.png" % device_name
            plt.close()
            logger.debug("{}.png".format(device_name))

            # generating individual table titles and line graphs
            report_obj.set_table_title(device_name)
            report_obj.build_table_title()

            report_obj.set_graph_image(graph_name)

            # need to move the graph image to the results directory
            report_obj.move_graph_image()

            # report.set_csv_filename(uptime_graph)
            # report.move_csv_file()
            report_obj.build_graph()


    def generate_report(self, result_json=None, result_dir='Ping_Test_Report', report_path=''):
        if result_json is not None:
            self.result_json = result_json
        logging.info('Generating Report')

        report = lf_report(_output_pdf='interop_ping.pdf',
                           _output_html='interop_ping.html',
                           _results_dir_name=result_dir,
                           _path=report_path)
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        logging.info('path: {}'.format(report_path))
        logging.info('path_date_time: {}'.format(report_path_date_time))

        # setting report title
        report.set_title('Ping Plotter Report')
        report.build_banner()

        # test setup info
        test_setup_info = {
            'SSID': self.ssid,
            'Security': self.security,
            'Website / IP': self.target,
            'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.sta_list), len(self.sta_list) - len(self.real_sta_list), self.android, self.windows, self.linux, self.mac),
            'Duration (in minutes)': self.duration
        }
        report.test_setup_table(
            test_setup_data=test_setup_info, value='Test Setup Information')

        # objective and description
        report.set_obj_html(_obj_title='Objective',
                            _obj='''The objective of the ping test is to evaluate network connectivity and measure the round-trip time taken for 
                            data packets to travel from the source to the destination and back. It helps assess the reliability and latency of the network, 
                            identifying any packet loss, delays, or variations in response times. The test aims to ensure that devices can communicate 
                            effectively over the network and pinpoint potential issues affecting connectivity.
                            ''')
        report.build_objective()

        # uptime and downtime
        report.set_table_title(
            'Ping Status'
        )
        report.build_table_title()
        # graph for above
        uptime_graph = self.generate_uptime_graph()
        logging.info('uptime graph name {}'.format(uptime_graph))
        report.set_graph_image(uptime_graph)

        # need to move the graph image to the results directory
        report.move_graph_image()

        # report.set_csv_filename(uptime_graph)
        # report.move_csv_file()
        report.build_graph()

        # realtime ping graphs
        report.set_table_title('Ping graphs')
        report.build_table_title()

        # graphs for above

        self.build_area_graphs(report_obj=report)

        # packets sent vs received vs dropped
        report.set_table_title(
            'Packets sent vs packets received vs packets dropped')
        report.build_table_title()
        # graph for the above
        self.packets_sent = []
        self.packets_received = []
        self.packets_dropped = []
        self.device_names = []
        self.device_modes = []
        self.device_channels = []
        self.device_min = []
        self.device_max = []
        self.device_avg = []
        self.device_mac = []
        self.device_names_with_errors = []
        self.devices_with_errors = []
        self.report_names = []
        self.remarks = []
        # packet_count_data = {}
        for device, device_data in self.result_json.items():
            self.packets_sent.append(device_data['sent'])
            self.packets_received.append(device_data['recv'])
            self.packets_dropped.append(device_data['dropped'])
            self.device_names.append(device_data['name'])
            self.device_modes.append(device_data['mode'])
            self.device_channels.append(device_data['channel'])
            self.device_mac.append(device_data['mac'])
            t_rtt_values = sorted(list(device_data['rtts'].values()))
            self.device_avg.append(float(sum(t_rtt_values) / len(t_rtt_values)))
            while(0.11 in t_rtt_values):
                t_rtt_values.remove(0.11)
            self.device_min.append(float(min(t_rtt_values)))
            self.device_max.append(float(max(t_rtt_values)))
            # self.device_avg.append(float(sum(t_rtt_values) / len(t_rtt_values)))
            # self.device_min.append(float(device_data['min_rtt'].replace(',', '')))
            # self.device_max.append(float(device_data['max_rtt'].replace(',', '')))
            # self.device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
            if(device_data['os'] == 'Virtual'):
                self.report_names.append('{} {}'.format(device, device_data['os'])[0:25])
            else:
                self.report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name'])[0:25])
            if (device_data['remarks'] != []):
                self.device_names_with_errors.append(device_data['name'])
                self.devices_with_errors.append(device)
                self.remarks.append(','.join(device_data['remarks']))
            logging.info('{} {} {}'.format(*self.packets_sent,
                  *self.packets_received,
                  *self.packets_dropped))
            logging.info('{} {} {}'.format(*self.device_min,
                  *self.device_max,
                  *self.device_avg))

            # packet_count_data[device] = {
            #     'MAC': device_data['mac'],
            #     'Channel': device_data['channel'],
            #     'Mode': device_data['mode'],
            #     'Packets Sent': device_data['sent'],
            #     'Packets Received': device_data['recv'],
            #     'Packets Loss': device_data['dropped'],
            # }
        x_fig_size = 15
        y_fig_size = len(self.device_names) * .5 + 4
        graph = lf_bar_graph_horizontal(_data_set=[self.packets_dropped, self.packets_received, self.packets_sent],
                                        _xaxis_name='Packets Count',
                                        _yaxis_name='Wireless Clients',
                                        _label=[
                                            'Packets Loss', 'Packets Received', 'Packets Sent'],
                                        _graph_image_name='Packets sent vs received vs dropped',
                                        _yaxis_label=self.report_names,
                                        _yaxis_categories=self.report_names,
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _graph_title='Packets sent vs received vs dropped',
                                        _title_size=16,
                                        _color=['lightgrey',
                                                'orange', 'steelblue'],
                                        _color_edge=['black'],
                                        _bar_height=0.15,
                                        _figsize=(x_fig_size, y_fig_size),
                                        _legend_loc="best",
                                        _legend_box=(1.0, 1.0),
                                        _dpi=96,
                                        _show_bar_value=False,
                                        _enable_csv=True,
                                        _color_name=['lightgrey', 'orange', 'steelblue'])

        graph_png = graph.build_bar_graph_horizontal()
        logging.info('graph name {}'.format(graph_png))
        report.set_graph_image(graph_png)
        # need to move the graph image to the results directory
        report.move_graph_image()
        report.set_csv_filename(graph_png)
        report.move_csv_file()
        report.build_graph()

        dataframe1 = pd.DataFrame({
            'Wireless Client': self.device_names,
            'MAC': self.device_mac,
            'Channel': self.device_channels,
            'Mode': self.device_modes,
            'Packets Sent': self.packets_sent,
            'Packets Received': self.packets_received,
            'Packets Loss': self.packets_dropped
        })
        report.set_table_dataframe(dataframe1)
        report.build_table()

        # packets latency graph
        report.set_table_title('Ping Latency Graph')
        report.build_table_title()

        graph = lf_bar_graph_horizontal(_data_set=[self.device_min, self.device_avg, self.device_max],
                                        _xaxis_name='Time (ms)',
                                        _yaxis_name='Wireless Clients',
                                        _label=[
                                            'Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                                        _graph_image_name='Ping Latency per client',
                                        _yaxis_label=self.report_names,
                                        _yaxis_categories=self.report_names,
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _graph_title='Ping Latency per client',
                                        _title_size=16,
                                        _color=['lightgrey',
                                                'orange', 'steelblue'],
                                        _color_edge='black',
                                        _bar_height=0.15,
                                        _figsize=(x_fig_size, y_fig_size),
                                        _legend_loc="best",
                                        _legend_box=(1.0, 1.0),
                                        _dpi=96,
                                        _show_bar_value=False,
                                        _enable_csv=True,
                                        _color_name=['lightgrey', 'orange', 'steelblue'])

        graph_png = graph.build_bar_graph_horizontal()
        logging.info('graph name {}'.format(graph_png))
        report.set_graph_image(graph_png)
        # need to move the graph image to the results directory
        report.move_graph_image()
        report.set_csv_filename(graph_png)
        report.move_csv_file()
        report.build_graph()

        dataframe2 = pd.DataFrame({
            'Wireless Client': self.device_names,
            'MAC': self.device_mac,
            'Channel': self.device_channels,
            'Mode': self.device_modes,
            'Min Latency (ms)': self.device_min,
            'Average Latency (ms)': self.device_avg,
            'Max Latency (ms)': self.device_max
        })
        report.set_table_dataframe(dataframe2)
        report.build_table()

        # check if there are remarks for any device. If there are remarks, build table else don't
        if(self.remarks != []):
            report.set_table_title('Notes')
            report.build_table_title()
            dataframe3 = pd.DataFrame({
                'Wireless Client': self.device_names_with_errors,
                'Port': self.devices_with_errors,
                'Remarks': self.remarks
            })
            report.set_table_dataframe(dataframe3)
            report.build_table()

        # closing
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()


def main():

    help_summary='''\
The Candela Tech ping plotter test assesses the network connectivity for specified clients by measuring Round
Trip data packet travel time. It also detects issues like packet loss, delays, and
response time variations, ensuring effective device communication and identifying
connectivity problems.
    '''
    parser = argparse.ArgumentParser(
        prog='interop_ping.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
            Allows user to run the ping test on a target IP for the given duration and packet interval
            with either selected number of virtual stations or provides the list of available real devices
            and allows the user to select the real devices and run ping test on them.
        ''',
        description='''
        NAME: lf_interop_ping_plotter.py

        PURPOSE: lf_interop_ping_plotter.py will let the user select real devices, virtual devices or both and then allows them to run
        ping test for user given duration and packet interval on the given target IP or domain name and generates realtime ping status and line charts for every device.

        EXAMPLE-1:
        Command Line Interface to run ping test with only virtual clients
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103  --target 192.168.1.3 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2 
        --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --debug

        EXAMPLE-2:
        Command Line Interface to run ping test with only real clients
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --ssid RDT_wpa2 --security wpa2_personal
        --passwd OpenWifi

        EXAMPLE-3:
        Command Line Interface to run ping test with both real and virtual clients
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --target 192.168.1.3 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61

        EXAMPLE-4:
        Command Line Interface to run ping test with existing Wi-Fi configuration on the real devices
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --target 192.168.1.61 --ping_interval 5 --ping_duration 1 --passwd OpenWifi --use_default_config
        
        SCRIPT_CLASSIFICATION : Test

        SCRIPT_CATEGORIES: Performance, Functional, Report Generation

        NOTES:
        1.Use './lf_interop_ping.py --help' to see command line usage and options
        2.Please pass ping_duration in minutes
        3.Please pass ping_interval in seconds
        4.After passing the cli, if --real flag is selected, then a list of available real devices will be displayed on the terminal.
        5.Enter the real device resource numbers seperated by commas (,)

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date    - 06/12/2023
        Build version   - 5.4.7
        kernel version  - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.
        '''
    )
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    # optional arguments
    optional.add_argument('--mgr',
                          type=str,
                          help='hostname where LANforge GUI is running',
                          default='localhost')


    optional.add_argument('--target',
                          type=str,
                          help='Target URL or port for ping test',
                          default='eth1')
    
    optional.add_argument('--ping_interval',
                          type=str,
                          help='Interval (in seconds) between the echo requests',
                          default='1')

    optional.add_argument('--ping_duration',
                          type=float,
                          help='Duration (in minutes) to run the ping test',
                          default=1)

    optional.add_argument('--ssid',
                          type=str,
                          help='SSID for connecting the stations')
    
    optional.add_argument('--mgr_port',
                          type=str,
                          default=8080,
                          help='port on which LANforge HTTP service is running'
                          )

    optional.add_argument('--mgr_passwd',
                          type=str,
                          default='lanforge',
                          help='Password to connect to LANforge GUI')

    optional.add_argument('--server_ip',
                          type=str,
                          help='Upstream for configuring the Interop App')

    optional.add_argument('--security',
                          type=str,
                          default='open',
                          help='Security protocol for the specified SSID: <open | wep | wpa | wpa2 | wpa3>')

    optional.add_argument('--passwd',
                          type=str,
                          default='[BLANK]',
                          help='passphrase for the specified SSID')

    optional.add_argument('--virtual',
                          action="store_true",
                          help='specify this flag if the test should run on virtual clients')

    optional.add_argument('--num_sta',
                          type=int,
                          default=1,
                          help='specify the number of virtual stations to be created.')

    optional.add_argument('--radio',
                          type=str,
                          help='specify the radio to create the virtual stations')

    optional.add_argument('--real',
                          action="store_true",
                          help='specify this flag if the test should run on real clients')

    optional.add_argument('--use_default_config',
                          action='store_true',
                          help='specify this flag if wanted to proceed with existing Wi-Fi configuration of the devices')

    optional.add_argument('--debug',
                          action="store_true",
                          help='Enable debugging')
    
    # logging configuration:
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")
    
    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    # set the logger level to debug
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    # input sanity
    if(args.virtual is False and args.real is False):
        print('Atleast one of --real or --virtual is required')
        exit(0)
    if (args.virtual is True and args.radio is None):
        print('--radio required')
        exit(0)
    if (args.virtual is True and args.ssid is None):
        print('--ssid required for virtual stations')
        exit(0)
    if (args.security != 'open' and args.passwd == '[BLANK]'):
        print('--passwd required')
        exit(0)
    if(args.use_default_config == False):
        if(args.ssid is None):
            print('--ssid required for Wi-Fi configuration')
            exit(0)

        if(args.security.lower() != 'open' and args.passwd == '[BLANK]'):
            print('--passwd required for Wi-Fi configuration')
            exit(0)

        if(args.server_ip is None):
            print('--server_ip or upstream ip required for Wi-fi configuration')
            exit(0)

    mgr_ip = args.mgr
    mgr_password = args.mgr_passwd
    mgr_port = args.mgr_port
    server_ip = args.server_ip
    ssid = args.ssid
    security = args.security
    password = args.passwd
    num_sta = args.num_sta
    radio = args.radio
    target = args.target
    interval = args.ping_interval
    duration = args.ping_duration
    configure = not args.use_default_config
    debug = args.debug

    if (debug):
        print('''Specified configuration:
              ip:                       {}
              port:                     {}
              ssid:                     {}
              security:                 {}
              password:                 {}
              target:                   {}
              Ping interval:            {}
              Packet Duration (in min): {}
              virtual:                  {}
              num of virtual stations:  {}
              radio:                    {}
              real:                     {}
              debug:                    {}
              '''.format(mgr_ip, mgr_port, ssid, security, password, target, interval, duration, args.virtual, num_sta, radio, args.real, debug))

    # ping object creation
    ping = Ping(host=mgr_ip, port=mgr_port, ssid=ssid, security=security, password=password, radio=radio,
                lanforge_password=mgr_password, target=target, interval=interval, sta_list=[], virtual=args.virtual, real=args.real, duration=duration, debug=debug)

    # changing the target from port to IP
    # ping.change_target_to_ip()
    
    # creating virtual stations if --virtual flag is specified
    if (args.virtual):

        logging.info('Proceeding to create {} virtual stations on {}'.format(num_sta, radio))
        station_list = LFUtils.portNameSeries(
            prefix_='sta', start_id_=0, end_id_=num_sta-1, padding_number_=100000, radio=radio)
        ping.sta_list = station_list
        if (debug):
            logging.info('Virtual Stations: {}'.format(station_list).replace(
                '[', '').replace(']', '').replace('\'', ''))

    # selecting real clients if --real flag is specified
    if (args.real):
        Devices = RealDevice(manager_ip=mgr_ip, server_ip=server_ip, ssid=ssid, encryption=security, passwd=password)
        if(configure):
            Devices.query_all_devices_to_configure_wifi()
            logging.info('{}'.format(*Devices.station_list))
            ping.select_real_devices(real_devices=Devices, real_sta_list=Devices.station_list, base_interop_obj=Devices)
        else:
            Devices.get_devices()
            ping.Devices = Devices
            ping.select_real_devices(real_devices=Devices)

            # if(configure):

            #     # for androids
            #     logger.info('Configuring Wi-Fi on the selected devices')
            #     if(Devices.android_list == []):
            #         logging.info('There are no Androids to configure Wi-Fi')
            #     else:
            #         androids = interop_connectivity.Android(lanforge_ip=mgr_ip, port=mgr_port, server_ip=server_ip, ssid=ssid, passwd=password, encryption=security)
            #         androids_data = androids.get_serial_from_port(port_list=Devices.android_list)

            #         androids.stop_app(port_list = androids_data)

            #         # androids.set_wifi_state(port_list=androids_data, state='disable')

            #         # time.sleep(5)

            #         androids.set_wifi_state(port_list=androids_data, state='enable')

            #         androids.configure_wifi(port_list=androids_data)

            #     # for laptops
            #     laptops = interop_connectivity.Laptop(lanforge_ip=mgr_ip, port=8080, server_ip=server_ip, ssid=ssid, passwd=password, encryption=security)
            #     all_laptops = Devices.windows_list + Devices.linux_list + Devices.mac_list

            #     if(all_laptops == []):
            #         logging.info('There are no laptops selected to configure Wi-Fi')
            #     else:

            #         laptops_data = laptops.get_laptop_from_port(port_list=all_laptops)

            #         # works only for linux
            #         laptops.rm_station(port_list=laptops_data)
            #         time.sleep(2)

            #         laptops.add_station(port_list=laptops_data)
            #         time.sleep(2)

            #         laptops.set_port(port_list=laptops_data)

            #     if(Devices.android_list != [] or all_laptops != []):
            #         logging.info('Waiting 20s for the devices to configure to Wi-Fi')
            #         time.sleep(120)

    # station precleanup
    ping.cleanup()

    # building station if virtual
    if (args.virtual):
        ping.buildstation()

    # check if generic tab is enabled or not
    if (not ping.check_tab_exists()):
        logging.error('Generic Tab is not available.\nAborting the test.')
        exit(0)

    ping.sta_list += ping.real_sta_list

    # creating generic endpoints
    ping.create_generic_endp()

    logging.info('{}'.format(*ping.generic_endps_profile.created_cx))

    # run the test for the given duration
    logging.info('Running the ping test for {} minutes'.format(duration))

    ping.start_time = datetime.now()

    # start generate endpoint
    ping.start_generic()
    time_counter = 0
    ports_data_dict = ping.json_get('/ports/all/')['interfaces']
    ports_data = {}
    for ports in ports_data_dict:
        port, port_data = list(ports.keys())[0], list(ports.values())[0]
        ports_data[port] = port_data

    duration = duration * 60

    loop_timer = 0
    logging.info(ping.result_json)
    rtts = {}
    rtts_list = []
    for station in ping.sta_list:
        rtts[station] = {}
    while(loop_timer <= duration):
        t_init = datetime.now()
        result_data = ping.get_results()
        # logging.info(result_data)
        if (args.virtual):
            ports_data_dict = ping.json_get('/ports/all/')['interfaces']
            ports_data = {}
            for ports in ports_data_dict:
                port, port_data = list(ports.keys())[0], list(ports.values())[0]
                ports_data[port] = port_data
            if (type(result_data) == dict):
                for station in ping.sta_list:
                    if (station not in ping.real_sta_list):
                        current_device_data = ports_data[station]
                        if (station.split('.')[2] in result_data['name']):
                            ping.result_json[station] = {
                                'command': result_data['command'],
                                'sent': result_data['tx pkts'],
                                'recv': result_data['rx pkts'],
                                'dropped': result_data['dropped'],
                                # 'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                                # 'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                                # 'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                                'mac': current_device_data['mac'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': station,
                                'os': 'Virtual',
                                'remarks': [],
                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                            }
                            if(len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results']):
                                temp_last_results = result_data['last results'].split('\n')[0: len(result_data['last results']) -1 ]
                                drop_count = 0 # let dropped = 0 initially
                                dropped_packets = []
                                for result in temp_last_results: # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                    try:
                                        t_result, t_fail = result.split('***') # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                    except:
                                        continue
                                    t_result = t_result.split()
                                    if('icmp_seq=' not in result and 'time=' not in result):
                                        continue
                                    for t_data in t_result:
                                        if('icmp_seq=' in t_data):
                                            seq_number = int(t_data.strip('icmp_seq='))
                                        if('time=' in t_data):
                                            rtt = float(t_data.strip('time='))
                                    rtts[station][seq_number] = rtt
                                    rtts_list.append(rtt)

                                    # finding dropped packets
                                    t_fail = t_fail.split() # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                    t_drop_val = t_fail[1] # t_drop_val = '0'
                                    t_drop_val = int(t_drop_val) # type cast string to int
                                    if(t_drop_val != drop_count):
                                        current_drop_packets = t_drop_val - drop_count
                                        drop_count = t_drop_val
                                        for drop_packet in range(1, current_drop_packets + 1):
                                            dropped_packets.append(seq_number - drop_packet)
                            else:
                                # rtts = [0] * 60 * int(ping.duration)
                                for seq in range(1, 60 * int(ping.duration) + 1):
                                    rtts[station][seq] = 0
                            if(rtts_list == []):
                                rtts_list = [0]
                            min_rtt = str(min(rtts_list))
                            avg_rtt = str(sum(rtts_list) / len(rtts_list))
                            max_rtt = str(max(rtts_list))
                            ping.result_json[station]['min_rtt'] = min_rtt
                            ping.result_json[station]['avg_rtt'] = avg_rtt
                            ping.result_json[station]['max_rtt'] = max_rtt
                            required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                            for seq in required_sequence_numbers:
                                if(seq not in rtts[station].keys()):
                                    if(seq in dropped_packets):
                                        rtts[station][seq] = 0
                                    else:
                                        rtts[station][seq] = 0.11
                            ping.result_json[station]['rtts'] = rtts[station]
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                            # ping.result_json[station]['dropped_packets'] = dropped_packets

            else:
                for station in ping.sta_list:
                    if (station not in ping.real_sta_list):
                        current_device_data = ports_data[station]
                        for ping_device in result_data:
                            ping_endp, ping_data = list(ping_device.keys())[
                                0], list(ping_device.values())[0]
                            if (station.split('.')[2] in ping_endp):
                                ping.result_json[station] = {
                                    'command': ping_data['command'],
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    # 'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                    # 'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                    # 'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                    'mac': current_device_data['mac'],
                                    'channel': current_device_data['channel'],
                                    'mode': current_device_data['mode'],
                                    'name': station,
                                    'os': 'Virtual',
                                    'remarks': [],
                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                }
                                if(len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results']):
                                    temp_last_results = ping_data['last results'].split('\n')[0: len(ping_data['last results']) -1 ]
                                    drop_count = 0 # let dropped = 0 initially
                                    dropped_packets = []
                                    for result in temp_last_results: # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                        try:
                                            t_result, t_fail = result.split('***') # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                        except:
                                            continue # first line of ping result
                                        t_result = t_result.split()
                                        if('icmp_seq=' not in result and 'time=' not in result):
                                            continue
                                        for t_data in t_result:
                                            if('icmp_seq=' in t_data):
                                                seq_number = int(t_data.strip('icmp_seq='))
                                            if('time=' in t_data):
                                                rtt = float(t_data.strip('time='))
                                        rtts[station][seq_number] = rtt
                                        rtts_list.append(rtt)

                                        # finding dropped packets
                                        t_fail = t_fail.split() # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                        t_drop_val = t_fail[1] # t_drop_val = '0'
                                        t_drop_val = int(t_drop_val) # type cast string to int
                                        if(t_drop_val != drop_count):
                                            current_drop_packets = t_drop_val - drop_count
                                            drop_count = t_drop_val
                                            for drop_packet in range(1, current_drop_packets + 1):
                                                dropped_packets.append(seq_number - drop_packet)
                                else:
                                    # rtts = [0] * 60 * int(ping.duration)
                                    for seq in range(1, 60 * int(ping.duration) + 1):
                                        rtts[station][seq] = 0
                                if(rtts_list == []):
                                    rtts_list = [0]
                                min_rtt = str(min(rtts_list))
                                avg_rtt = str(sum(rtts_list) / len(rtts_list))
                                max_rtt = str(max(rtts_list))
                                ping.result_json[station]['min_rtt'] = min_rtt
                                ping.result_json[station]['avg_rtt'] = avg_rtt
                                ping.result_json[station]['max_rtt'] = max_rtt
                                required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                                for seq in required_sequence_numbers:
                                    if(seq not in rtts[station].keys()):
                                        if(seq in dropped_packets):
                                            rtts[station][seq] = 0
                                        else:
                                            rtts[station][seq] = 0.11
                                ping.result_json[station]['rtts'] = rtts[station]
                                ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                                # ping.result_json[station]['dropped_packets'] = dropped_packets


        if (args.real):
            if (type(result_data) == dict):
                for station in ping.real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    # logging.info(current_device_data)
                    if (station in result_data['name']):
                        # logging.info(result_data['last results'].split('\n'))
                        ping.result_json[station] = {
                            'command': result_data['command'],
                            'sent': result_data['tx pkts'],
                            'recv': result_data['rx pkts'],
                            'dropped': result_data['dropped'],
                            # 'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                            # 'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                            # 'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'] else '0'][0],
                            'mac': current_device_data['mac'],
                            'channel': current_device_data['channel'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                            'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                            'remarks': [],
                            'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                        }
                        if(len(result_data['last results']) != 0):
                            temp_last_results = result_data['last results'].split('\n')[0: len(result_data['last results']) -1 ]
                            drop_count = 0 # let dropped = 0 initially
                            dropped_packets = []
                            for result in temp_last_results: # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                try:
                                    t_result, t_fail = result.split('***') # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                except:
                                    continue
                                t_result = t_result.split()
                                if('icmp_seq=' not in result and 'time=' not in result):
                                    continue
                                for t_data in t_result:
                                    if('icmp_seq=' in t_data):
                                        seq_number = int(t_data.strip('icmp_seq='))
                                    if('time=' in t_data):
                                        rtt = float(t_data.strip('time='))
                                rtts[station][seq_number] = rtt
                                rtts_list.append(rtt)

                                # finding dropped packets
                                t_fail = t_fail.split() # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                t_drop_val = t_fail[1] # t_drop_val = '0'
                                t_drop_val = int(t_drop_val) # type cast string to int
                                if(t_drop_val != drop_count):
                                    current_drop_packets = t_drop_val - drop_count
                                    drop_count = t_drop_val
                                    for drop_packet in range(1, current_drop_packets + 1):
                                        dropped_packets.append(seq_number - drop_packet)
                        else:
                            # rtts = [0] * 60 * int(ping.duration)
                            for seq in range(1, 60 * int(ping.duration) + 1):
                                rtts[station][seq] = 0
                        if(rtts_list == []):
                            rtts_list = [0]
                        min_rtt = str(min(rtts_list))
                        avg_rtt = str(sum(rtts_list) / len(rtts_list))
                        max_rtt = str(max(rtts_list))
                        ping.result_json[station]['min_rtt'] = min_rtt
                        ping.result_json[station]['avg_rtt'] = avg_rtt
                        ping.result_json[station]['max_rtt'] = max_rtt
                        if(ping.result_json[station]['os'] == 'Android' and type(rtts) is dict and rtts != {}):
                            if(list(rtts[station].keys()) == []):
                                ping.result_json[station]['sent'] = str(0)
                                ping.result_json[station]['recv'] = str(0)
                                ping.result_json[station]['dropped'] = str(0)
                            else:
                                ping.result_json[station]['sent'] = str(max(list(rtts[station].keys())))
                                ping.result_json[station]['recv'] = str(len(rtts[station].keys()))
                                ping.result_json[station]['dropped'] = str(int(ping.result_json[station]['sent']) - int(ping.result_json[station]['recv']))
                        required_sequence_numbers = list(range(1, max(rtts.keys())))
                        for seq in required_sequence_numbers:
                            if(seq not in rtts[station].keys()):
                                if(seq in dropped_packets):
                                    rtts[station][seq] = 0
                                else:
                                    rtts[station][seq] = 0.11
                        ping.result_json[station]['rtts'] = rtts[station]
                        ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                        # ping.result_json[station]['dropped_packets'] = dropped_packets
            else:
                for station in ping.real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    # print('<<<<<<<<<<<<<<<<<<<', current_device_data)
                    for ping_device in result_data:
                        ping_endp, ping_data = list(ping_device.keys())[
                            0], list(ping_device.values())[0]
                        if (station in ping_endp):
                            ping.result_json[station] = {
                                'command': ping_data['command'],
                                'sent': ping_data['tx pkts'],
                                'recv': ping_data['rx pkts'],
                                'dropped': ping_data['dropped'],
                                # 'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                # 'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                # 'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'] else '0'][0],
                                'mac': current_device_data['mac'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                                'remarks': [],
                                'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                            }
                            if(len(ping_data['last results']) != 0):
                                temp_last_results = ping_data['last results'].split('\n')[0: len(ping_data['last results']) -1 ]
                                drop_count = 0 # let dropped = 0 initially
                                dropped_packets = []
                                for result in temp_last_results:
                                    if('time=' in result): # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                        try:
                                            t_result, t_fail = result.split('***') # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                        except:
                                            continue
                                        t_result = t_result.split()
                                        if('icmp_seq=' not in result and 'time=' not in result):
                                            continue
                                        for t_data in t_result:
                                            if('icmp_seq=' in t_data):
                                                seq_number = int(t_data.strip('icmp_seq='))
                                            if('time=' in t_data):
                                                rtt = float(t_data.strip('time='))
                                        rtts[station][seq_number] = rtt
                                        rtts_list.append(rtt)
                                        
                                        # finding dropped packets
                                        t_fail = t_fail.split() # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                        t_drop_val = t_fail[1] # t_drop_val = '0'
                                        t_drop_val = int(t_drop_val) # type cast string to int
                                        if(t_drop_val != drop_count):
                                            current_drop_packets = t_drop_val - drop_count
                                            drop_count = t_drop_val
                                            for drop_packet in range(1, current_drop_packets + 1):
                                                dropped_packets.append(seq_number - drop_packet)
                                                
                            else:
                                # rtts = [0] * 60 * int(ping.duration)
                                for seq in range(1, 60 * int(ping.duration) + 1):
                                    rtts[station][seq] = 0
                            if(rtts_list == []):
                                rtts_list = [0]
                            min_rtt = str(min(rtts_list))
                            avg_rtt = str(sum(rtts_list) / len(rtts_list))
                            max_rtt = str(max(rtts_list))
                            ping.result_json[station]['min_rtt'] = min_rtt
                            ping.result_json[station]['avg_rtt'] = avg_rtt
                            ping.result_json[station]['max_rtt'] = max_rtt
                            if(ping.result_json[station]['os'] == 'Android' and type(rtts) is dict and rtts != {}):
                                if(list(rtts[station].keys()) == []):
                                    ping.result_json[station]['sent'] = str(0)
                                    ping.result_json[station]['recv'] = str(0)
                                    ping.result_json[station]['dropped'] = str(0)
                                else:
                                    ping.result_json[station]['sent'] = str(max(list(rtts[station].keys())))
                                    ping.result_json[station]['recv'] = str(len(rtts[station].keys()))
                                    ping.result_json[station]['dropped'] = str(int(ping.result_json[station]['sent']) - int(ping.result_json[station]['recv']))
                            if(len(rtts[station].keys()) != 0):
                                required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                                for seq in required_sequence_numbers:
                                    if(seq not in rtts[station].keys()):
                                        if(seq in dropped_packets):
                                            rtts[station][seq] = 0
                                        else:
                                            rtts[station][seq] = 0.11
                                    # print(station, rtts[station])
                            ping.result_json[station]['rtts'] = rtts[station]
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                            # ping.result_json[station]['dropped_packets'] = dropped_packets

        time.sleep(1)
        # loop_timer += 1
        # print(loop_timer)
        t_end = datetime.now()
        # print(t_end, abs(t_init - t_end).total_seconds())
        loop_timer += abs(t_init - t_end).total_seconds()
    # time.sleep(duration * 60)

    logging.info('Stopping the test')
    ping.stop_generic()

    logging.info(ping.result_json)

    # print('----',rtts)
    # station post cleanup
    # ping.cleanup()

    ping.generate_report()

if __name__ == "__main__":
    main()