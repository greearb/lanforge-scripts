#!/usr/bin/env python3
'''
    NAME: lf_interop_ping_plotter.py

    PURPOSE: lf_interop_ping_plotter.py will let the user select real devices, virtual devices or both and then allows them to run
    ping plotter test for user given duration and packet interval on the given target IP or domain name and generates realtime ping status and line charts for every device.

    EXAMPLE-1:
    Command Line Interface to run ping plotter test with only virtual clients with eth1 as the default target
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61 --debug

    EXAMPLE-2:
    Command Line Interface to stop cleaning up stations after the test
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61 --debug --no_cleanup

    EXAMPLE-3:
    Command Line Interface to run ping plotter test with only real clients
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61

    EXAMPLE-4:
    Command Line Interface to run ping plotter test with both real and virtual clients
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61

    EXAMPLE-5:
    Command Line Interface to run ping plotter test with a different target
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --ping_interval 5 --ping_duration 1m --target 192.168.1.61

    EXAMPLE-6:
    Command Line Interface to run ping plotter with existing real stations instead of giving input after starting the test
    python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --ping_interval 5 --ping_duration 1m --target 192.168.1.61 --resources 1.10,1.11

    EXAMPLE-7:
    Command Line Interface to run ping plotter test by setting the same expected Pass/Fail value for all devices
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m --expected_passfail_value 3
    --use_default_config

    EXAMPLE-8:
    Command Line Interface to run ping plotter test by setting device specific Pass/Fail values in the csv file
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m --device_csv_name device.csv
    --use_default_config

    EXAMPLE-9:
    Command Line Interface to run ping plotter test by configuring Real Devices with SSID, Password, and Security
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --ssid NETGEAR_2G_wpa2
     --security wpa2 --passwd Password@123 --server_ip 192.168.204.74 --wait_time 30

    EXAMPLE-10:
    Command Line Interface to run ping plotter test by setting device specific Pass/Fail values in the csv file
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --ssid NETGEAR_2G_wpa2
     --security wpa2 --passwd Password@123 --server_ip 192.168.204.74 --wait_time 30 --device_csv_name device.csv

    EXAMPLE-11:
    Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4
     --profile_name Openz --file_name g219 --server_ip 192.168.204.74

    EXAMPLE-12:
    Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles with expected Pass/Fail values
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4,grp5
     --profile_name Openz,Openz --file_name g219 --expected_passfail_value 22 --server_ip 192.168.204.74

    EXAMPLE-13:
    Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles with device_csv_name
    python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4,grp5
     --profile_name Openz,Openz --file_name g219 --device_csv_name device.csv --server_ip 192.168.204.74

    SCRIPT_CLASSIFICATION : Test

    SCRIPT_CATEGORIES: Performance, Functional, Report Generation

    NOTES:
    1.Use './lf_interop_ping.py --help' to see command line usage and options
    2.Use 's','m','h' as suffixes for ping_duration in seconds, minutes and hours respectively
    3.After passing the cli, if --real flag is selected, then a list of available real devices will be displayed on the terminal
    4.Enter the real device resource numbers seperated by commas (,)
    5.For --target, you can specify it as eth1, IP address or domain name (e.g., google.com)

    STATUS: BETA RELEASE

    VERIFIED_ON:
    Working date    - 06/12/2023
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
import asyncio
import json
import shutil
import requests

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

if 'py-scripts' not in sys.path:
    sys.path.append('/home/lanforge/lanforge-scripts/py-scripts')

from lf_base_interop_profile import RealDevice
from datetime import datetime, timedelta
from lf_graph import lf_bar_graph_horizontal
from lf_report import lf_report
from station_profile import StationProfile
from typing import List, Optional
# Importing DeviceConfig to apply device configurations for ADB devices and laptops
DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")
from LANforge import LFUtils  # noqa: E402

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
                 do_webUI=False,
                 ui_report_dir=None,
                 debug=False,
                 file_name=None,
                 profile_name=None,
                 group_name=None,
                 server_ip=None,
                 expected_passfail_val=None,
                 csv_name=None,
                 wait_time=60):
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
        self.do_webUI = do_webUI
        self.ui_report_dir = ui_report_dir
        self.api_url = 'http://{}:{}'.format(self.host, self.port)
        self.profile_name = profile_name
        self.file_name = file_name
        self.group_name = group_name
        self.server_ip = server_ip
        self.real = real
        self.expected_passfail_val = expected_passfail_val
        self.csv_name = csv_name
        self.wait_time = wait_time

    def change_target_to_ip(self):

        # checking if target is an IP or a port
        if self.target.count('.') != 3 and self.target.split('.')[-2].isnumeric():
            # checking if target is eth1 or 1.1.eth1
            target_port_list = self.name_to_eid(self.target)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get('/port/{}/{}/{}?fields=ip'.format(shelf, resource, port))['interface']['ip']
                self.target = target_port_ip
            except BaseException:
                logging.warning('The target is not an ethernet port. Proceeding with the given target {}.'.format(self.target))
            logging.info(self.target)
        else:
            logging.info(self.target)
        return self.target

    def api_get(self, endp: str):
        """
        Sends a GET request to fetch data

        Args:
            endp (str): API endpoint

        Returns:
            response: response code for the request
            data: data returned in the response
        """
        if endp[0] != '/':
            endp = '/' + endp
        response = requests.get(url=self.api_url + endp)
        data = response.json()
        return response, data

    def filter_iOS_devices(self, device_list):
        modified_device_list = device_list
        if isinstance(device_list, str):
            modified_device_list = device_list.split(',')
        filtered_list = []
        for device in modified_device_list:
            if device.count('.') == 1:
                shelf, resource = device.split('.')
            elif device.count('.') == 2:
                shelf, resource, port = device.split('.')
            elif device.count('.') == 0:
                shelf, resource = 1, device
            response_code, device_data = self.api_get('/resource/{}/{}'.format(shelf, resource))
            if 'status' in device_data and device_data['status'] == 'NOT_FOUND':
                logger.info('Device {} is not found.'.format(device))
                continue
            device_data = device_data['resource']
            if 'Apple' in device_data['hw version'] and (device_data['app-id'] != '') and (device_data['app-id'] != '0' or device_data['kernel'] == ''):
                logger.info('{} is an iOS device. Currently we do not support iOS devices.'.format(device))
            else:
                filtered_list.append(device)
        if isinstance(device_list, str):
            filtered_list = ','.join(filtered_list)
        self.device_list = filtered_list
        return filtered_list

    def cleanup(self):

        if self.enable_virtual:
            # removing virtual stations if existing
            for station in self.sta_list:
                logging.info('Removing the station {} if exists'.format(station))
                self.generic_endps_profile.created_cx.append(
                    'CX_generic-{}'.format(station.split('.')[2]))
                self.generic_endps_profile.created_endp.append(
                    'generic-{}'.format(station.split('.')[2]))
                self.rm_port(station, check_exists=True)

            if not LFUtils.wait_until_ports_disappear(base_url=self.host, port_list=self.sta_list, debug=self.debug):
                logging.info('All stations are not removed or a timeout occured.')
                logging.error('Aborting the test.')
                exit(0)

        if self.enable_real:
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
    def select_real_devices(self, real_devices, real_sta_list=None, base_interop_obj=None, device_list=""):
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_devices.query_user(device_list=device_list)
        else:
            if real_sta_list == ['all']:
                self.real_sta_list, _, _ = real_devices.query_user(dowebgui=True, device_list='all')
            else:
                real_list = []
                for i in range(len(real_sta_list)):
                    real_list.append(real_sta_list[i].split('.')[0] + '.' + real_sta_list[i].split('.')[1])
                self.real_sta_list, _, _ = real_devices.query_user(dowebgui=True, device_list=','.join(real_list))
        if base_interop_obj is not None:
            self.Devices = base_interop_obj

        # Need real stations to run interop test
        if len(self.real_sta_list) == 0:
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        self.real_sta_list = self.filter_iOS_devices(self.real_sta_list)
        logging.info('{}'.format(*self.real_sta_list))

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logger.error('Real station not in devices data, ignoring it from testing')
                continue
                # raise ValueError('Real station not in devices data')

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        # Track number of selected devices
        if not self.do_webUI:
            self.android = self.Devices.android
            self.windows = self.Devices.windows
            self.mac = self.Devices.mac
            self.linux = self.Devices.linux
        d_list = []
        for i in self.real_sta_list:
            device = i.split('.')
            d_list.append(device[0] + '.' + device[1])
        return d_list

    def buildstation(self):
        logging.info('Creating Virtual Stations: {}'.format(self.sta_list))
        station_object = StationProfile(lfclient_url='http://{}:{}'.format(self.host, self.port), local_realm=self,
                                        ssid=self.ssid, ssid_pass=self.password, security=self.security,
                                        number_template_='00')
        station_object.use_security(self.security, self.ssid, self.password)
        station_object.set_command_flag("add_sta", "create_admin_down", 1)
        station_object.set_command_param("set_port", "report_timer", 1500)
        station_object.set_command_flag("set_port", "rpt_timer", 1)
        station_object.create(radio=self.radio, sta_names_=self.sta_list)
        station_object.admin_up()
        if Realm.wait_for_ip(self=self, station_list=self.sta_list, timeout_sec=-1):
            self._pass("All stations got IPs", print_=True)
        else:
            self._fail("Stations failed to get IPs", print_=True)
            logger.info("Please re-check the configuration applied")

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

        if self.enable_virtual:
            if self.generic_endps_profile.create(ports=virtual_stations, sleep_time=.5):
                logging.info('Virtual client generic endpoint creation completed.')
            else:
                logging.error('Virtual client generic endpoint creation failed.')
                exit(0)

        if self.enable_real:
            real_sta_os_types = [self.real_sta_data_dict[real_sta_name]['ostype'] for real_sta_name in self.real_sta_data_dict]

            if self.generic_endps_profile.create(ports=self.real_sta_list, sleep_time=.5, real_client_os_types=real_sta_os_types):
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
        overallres = self.json_get("/generic/all")
        if len(self.generic_endps_profile.created_endp) > 1 and 'endpoints' in results.keys():
            results = results['endpoints']
        else:
            try:
                results = results['endpoint']
            except Exception as e:
                logger.info(overallres)
                logger.error(f"Endpoint not found {e}")
        return (results)

    def generate_remarks(self, station_ping_data):
        remarks = []

        # NOTE if there are any more ping failure cases that are missed, add them here.

        # checking if ping output is not empty
        if station_ping_data['last_result'] == "":
            remarks.append('No output for ping')

        # illegal division by zero error. Issue with arguments.
        if 'Illegal division by zero' in station_ping_data['last_result']:
            remarks.append('Illegal division by zero error. Please re-check the arguments passed.')

        # unknown host
        if 'Totals:  *** dropped: 0  received: 0  failed: 0  bytes: 0' in station_ping_data['last_result'] or 'unknown host' in station_ping_data['last_result']:
            remarks.append('Unknown host. Please re-check the target')

        # checking if IP is existing in the ping command or not for Windows device
        if station_ping_data['os'] == 'Windows':
            if 'None' in station_ping_data['command'] or station_ping_data['command'].split('-n')[0].split('-S')[-1] == "  ":
                remarks.append('Station has no IP')

        # network buffer overflow
        if 'ping: sendmsg: No buffer space available' in station_ping_data['last_result']:
            remarks.append('Network buffer overlow')

        # checking for no ping states
        if float(station_ping_data['min_rtt'].replace(',', '')) == 0 and float(station_ping_data['max_rtt'].replace(',', '')) == 0 and float(station_ping_data['avg_rtt'].replace(',', '')) == 0:

            # Destination Host Unreachable state
            if 'Destination Host Unreachable' in station_ping_data['last_result']:
                remarks.append('Destination Host Unrechable')

            # Name or service not known state
            if 'Name or service not known' in station_ping_data['last_result']:
                remarks.append('Name or service not known')

            # network buffer overflow
            if 'ping: sendmsg: No buffer space available' in station_ping_data['last_result']:
                remarks.append('Network buffer overlow')

        return (remarks)

    def generate_uptime_graph(self):
        json_data = {}
        for station in self.result_json:
            json_data[station] = {
                'rtts': {},
                'sent': "",
                'dropped': ""
            }
            # print('------------',json_data)
            # for seq in self.result_json[station]['rtts']:
            json_data[station]['rtts'] = self.result_json[station]['rtts']
            json_data[station]['sent'] = self.result_json[station]['sent']
            json_data[station]['dropped'] = self.result_json[station]['dropped']
        self.graph_values = json_data
        device_names = list(json_data.keys())
        sequence_numbers = list(set(seq for device_data in json_data.values() for seq in device_data.get("rtts", {})))
        # print(sequence_numbers)
        rtt_values = {}
        for seq in sequence_numbers:
            rtt_values[seq] = []
            for device_data in json_data.values():
                if "rtts" in device_data.keys():
                    if seq in device_data['rtts'].keys():
                        rtt_values[seq].append(device_data['rtts'][seq])
                    else:
                        if device_data['sent'] == device_data['dropped']:
                            rtt_values[seq].append(0)
                        elif len(device_data['rtts'].keys()) != 0:
                            rtt_values[seq].append(1)
                        else:
                            rtt_values[seq].append(0)
        # rtt_values = {seq: [device_data.get("rtts", {}).get(seq, 0) for device_data in json_data.values()] for seq in sequence_numbers}
        # print(rtt_values)
        # Set different colors based on RTT values
        colors = [['red' if rtt == 0 else 'green' for rtt in rtt_values[seq]] for seq in sequence_numbers]

        # Create a stacked horizontal bar graph
        fig, ax = plt.subplots(figsize=(20, len(device_names) * .5 + 10))
        # y_positions = np.arange(len(device_names)) * (bar_width + 1)  # Adjust the 0.1 to control the gap
        for i, device_name in enumerate(self.report_names):
            # plt.barh(device_name, 1, color='white', height=0.5)
            for j, seq in enumerate(sequence_numbers):
                plt.barh(device_name, 1, left=int(seq) - 1, color=colors[j][i], height=0.3)

        # Customize the plot
        plt.xlabel('Time', fontweight='bold', fontsize=15)
        plt.ylabel('Client Status', fontweight='bold', fontsize=15)
        plt.title('Client Status vs Time')
        # plt.legend(sequence_numbers, title='Sequence Numbers', loc='upper right')

        # Remove y-axis labels
        # plt.yticks([])

        # building timestamps
        start_time = self.start_time
        interval = timedelta(seconds=int(self.interval))

        timestamps = []
        for seq_num in sequence_numbers:
            timestamp = ((int(seq_num) - 1) * interval + start_time).strftime("%d/%m/%Y %H:%M:%S")
            timestamps.append(timestamp)

        # settings labels for x-axis
        # print(list(map(int,sequence_numbers)))
        # print(list(map(int,sequence_numbers))[0::10])
        # print(timestamps)

        # ticks_sequence_numbers =  list(map(int,sequence_numbers))
        # ticks_sequence_numbers.sort()
        sequence_numbers.sort()
        timestamps.sort()
        # print('--------------')
        # print(ticks_sequence_numbers[0::10])
        # print(timestamps[0::10])
        # settings labels for x-axis
        if len(sequence_numbers) > 30:
            temp_sequence_numbers = sequence_numbers[:len(sequence_numbers):max(round(len(timestamps) / 30), len(timestamps) // 30)]
            temp_timestamps = timestamps[:len(timestamps):max(round(len(timestamps) / 30), len(timestamps) // 30)]

            if len(temp_sequence_numbers) != len(temp_timestamps):
                temp_sequence_numbers.pop(0)
            # plt.xticks(temp_sequence_numbers, temp_timestamps, rotation=45)
            ax.set_xticks(temp_sequence_numbers)
            ax.set_xticklabels(temp_timestamps, rotation=45, ha='right')
        else:
            # plt.xticks(sequence_numbers, timestamps, rotation=45)
            ax.set_xticks(sequence_numbers)
            ax.set_xticklabels(timestamps, rotation=45, ha='right')
        # plt.xlim(0, max([max(rtt_values[seq]) for seq in sequence_numbers]))

        if len(sequence_numbers) != 0:
            plt.xlim(0, max(sequence_numbers))

        # print('working xlim', max([max(rtt_values[seq]) for seq in sequence_numbers]))

        # fixing the number of ticks to 30 in x-axis
        # plt.locator_params(axis='x', nbins=30)

        # Show the plot
        # plt.show()
        plt.savefig("%s.png" % "uptime_graph", dpi=96)
        plt.close()

        logger.debug("{}.png".format("uptime_graph"))
        return ("%s.png" % "uptime_graph")

    def build_area_graphs(self, report_obj=None):
        json_data = self.graph_values
        device_names = list(json_data.keys())

        # Plot line graphs for each device
        for device_name, device_data in json_data.items():
            rtts = []
            # dropped_seqs = []
            sequence_numbers = []
            if 'rtts' in device_data.keys():
                for seq in sorted(list(device_data['rtts'].keys())):
                    if device_data['rtts'][seq] == 0.11:
                        continue
                    rtts.append(device_data['rtts'][seq])
                    sequence_numbers.append(seq)
            fig, ax = plt.subplots(figsize=(15, len(device_names) * .5 + 10))
            # plt.plot(sequence_numbers, rtts, label=device_name, color="Slateblue", alpha=0.6)

            # for area chart
            ax.fill_between(sequence_numbers, rtts, color="skyblue", alpha=1)
            ax.set_xlabel('Time', fontweight='bold', fontsize=15)
            ax.set_ylabel('RTT (ms)', fontweight='bold', fontsize=15)

            # Customize the plot
            # plt.xlabel('Time')
            # plt.ylabel('RTT (ms)')
            # plt.title('RTT vs Time for {}'.format(device_name))
            # plt.legend(loc='upper right')
            # plt.grid(True)
            # building timestamps
            start_time = self.start_time
            interval = timedelta(seconds=int(self.interval))

            timestamps = []
            for seq_num in sequence_numbers:
                timestamp = ((int(seq_num) - 1) * interval + start_time).strftime("%d/%m/%Y %H:%M:%S")
                timestamps.append(timestamp)

            # generating csv
            with open('{}/{}.csv'.format(report_obj.path_date_time, device_name), 'w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(['Time', 'RTT (ms)', 'Sent', 'Received', 'Dropped'])
                for index in range(len(self.result_json[device_name]['ping_stats']['sent']), len(timestamps)):
                    self.result_json[device_name]['ping_stats']['sent'].append(str(int(self.result_json[device_name]['ping_stats']['sent'][-1]) + 1))
                    if rtts[index] == 0:
                        self.result_json[device_name]['ping_stats']['dropped'].append(str(int(self.result_json[device_name]['ping_stats']['dropped'][-1]) + 1))
                        self.result_json[device_name]['ping_stats']['received'].append(str(int(self.result_json[device_name]['ping_stats']['received'][-1])))
                    else:
                        self.result_json[device_name]['ping_stats']['received'].append(str(int(self.result_json[device_name]['ping_stats']['received'][-1]) + 1))
                        self.result_json[device_name]['ping_stats']['dropped'].append(str(int(self.result_json[device_name]['ping_stats']['dropped'][-1])))
                for row in range(len(timestamps)):
                    writer.writerow([timestamps[row], rtts[row], self.result_json[device_name]['ping_stats']['sent'][row], self.result_json[device_name]
                                    ['ping_stats']['received'][row], self.result_json[device_name]['ping_stats']['dropped'][row]])
                # writer.writerows([timestamps, rtts])
            sequence_numbers.sort()
            timestamps.sort()

            # settings labels for x-axis
            if len(sequence_numbers) > 30:
                temp_sequence_numbers = sequence_numbers[:len(sequence_numbers):max(round(len(timestamps) / 30), len(timestamps) // 30)]
                temp_timestamps = timestamps[:len(timestamps):max(round(len(timestamps) / 30), len(timestamps) // 30)]

                if len(temp_sequence_numbers) != len(temp_timestamps):
                    temp_sequence_numbers.pop(0)
                # plt.xticks(temp_sequence_numbers, temp_timestamps, rotation=45)
                ax.set_xticks(temp_sequence_numbers)
                ax.set_xticklabels(temp_timestamps, rotation=45, ha='right')
            else:
                # plt.xticks(sequence_numbers, timestamps, rotation=45)
                ax.set_xticks(sequence_numbers)
                ax.set_xticklabels(timestamps, rotation=45, ha='right')

            # ax.set_xticks(sequence_numbers)
            # ax.set_xticklabels(timestamps, rotation=45, ha='right')

            # ax.xaxis.set_major_locator(plt.MaxNLocator(30))
            # print(sequence_numbers)
            # print(rtts)
            # plt.xlim(0, max(rtts))
            # plt.xlim(0, max(list(map(int, sequence_numbers))))
            if len(sequence_numbers) != 0:
                plt.xlim(0, max(sequence_numbers))

            # Show the plot
            # plt.show()

            # set origin on x-axis
            if rtts != []:
                plt.ylim(0, max(rtts))
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

    def store_csv(self, data=None):
        if data is None:
            data = self.result_json

        if 'status' in data.keys() and data['status'] == 'Aborted':
            return False
        else:
            data['status'] = 'Running'
            interval = timedelta(seconds=int(self.interval))
            for device, device_data in data.items():
                if device == 'status':
                    continue
                new_dict = {}
                sequence_numbers = {}
                for seq in device_data['rtts'].keys():
                    sequence_numbers[int(seq)] = ((int(seq) - 1) * interval + self.start_time).strftime("%d/%m/%Y %H:%M:%S")
                for seq in sorted(list(sequence_numbers.keys())):
                    new_dict[sequence_numbers[seq]] = device_data['rtts'][seq]
                # for seq,rtt in device_data['rtts'].items():
                #     new_dict[((int(seq) -1) * interval + self.start_time).strftime("%d/%m/%Y %H:%M:%S")] = rtt
                data[device]['webui_rtts'] = new_dict
        with open(self.ui_report_dir + '/runtime_ping_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        test_name = self.ui_report_dir.split("/")[-1]
        with open(self.ui_report_dir + '/../../Running_instances/{}_{}_running.json'.format(self.host, test_name), 'r') as f:
            run_status = json.load(f)
            if run_status["status"] != "Running":
                logging.info('Test is stopped by the user')
                return False
        return True

    def set_webUI_stop(self):
        with open(self.ui_report_dir + '/runtime_ping_data.json', 'r') as f:
            data = json.load(f)

        if 'status' in data.keys() and data['status'] != 'Aborted':
            data['status'] = 'Completed'

            with open(self.ui_report_dir + '/runtime_ping_data.json', 'w') as f:
                json.dump(data, f, indent=4)

    def copy_reports(self, report_path):
        logging.info('Copying PDF report and CSVs to webUI result directory')
        for file in os.listdir(report_path):
            if file.endswith('.csv') or file.endswith('.pdf'):
                shutil.copy2(report_path + '/' + file, self.ui_report_dir)

    def get_pass_fail_list(self):
        # When csv_name is provided, for pass/fail criteria, respective values for each client will be used
        if not self.expected_passfail_val:
            res_list = []
            test_input_list = []
            pass_fail_list = []
            for client in self.report_names:
                # Check if the client type (second word in "1.15 android samsungmob") is 'android'
                if client.split(' ')[1] != 'Android':
                    res_list.append(client.split(' ')[2])
                else:
                    interop_tab_data = self.json_get('/adb/')["devices"]
                    for dev in interop_tab_data:
                        for item in dev.values():
                            # Extract the username from the client string (e.g., 'samsungmob' from "1.15 android samsungmob")
                            if item['user-name'] == client.split(' ')[2]:
                                res_list.append(item['name'].split('.')[2])
            with open(self.csv_name, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            for device in res_list:
                found = False
                for row in rows:
                    if row['DeviceList'] == device and row['PingPacketLoss %'].strip() != '':
                        test_input_list.append(row['PingPacketLoss %'])
                        found = True
                        break
                if not found:
                    logging.info(f"Ping result for device {device} not found in CSV. Using default packet loss = 10%")
                    test_input_list.append(10)
            for i in range(len(test_input_list)):
                if self.packets_sent[i] == 0.0:
                    pass_fail_list.append('FAIL')
                elif float(test_input_list[i]) >= self.packet_loss_percent[i]:
                    pass_fail_list.append('PASS')
                else:
                    pass_fail_list.append('FAIL')
        # When expected_passfail_val is provided, for pass/fail criteria, the same value will be used for all clients
        else:
            test_input_list = [self.expected_passfail_val for val in range(len(self.report_names))]
            pass_fail_list = []
            for i in range(len(test_input_list)):
                if self.packets_sent[i] == 0:
                    pass_fail_list.append('FAIL')
                elif float(self.expected_passfail_val) >= self.packet_loss_percent[i]:
                    pass_fail_list.append("PASS")
                else:
                    pass_fail_list.append("FAIL")
        return pass_fail_list, test_input_list

    def generate_report(self, result_json=None, result_dir='Ping_Plotter_Test_Report', report_path='', config_devices='', group_device_map=None):
        if group_device_map is None:
            group_device_map = {}
        if result_json is not None:
            self.result_json = result_json
        logging.info('Generating Report')
        # graph for the above
        self.packets_sent = []
        self.packets_received = []
        self.packets_dropped = []
        self.packet_loss_percent = []
        # self.client_unrechability_percent = []
        self.device_names = []
        self.device_modes = []
        self.device_channels = []
        self.device_min = []
        self.device_max = []
        self.device_avg = []
        self.device_mac = []
        self.device_ips = []
        self.device_bssid = []
        self.device_ssid = []
        self.device_names_with_errors = []
        self.devices_with_errors = []
        self.report_names = []
        self.remarks = []
        # packet_count_data = {}
        if self.do_webUI and 'status' in self.result_json.keys():
            del self.result_json['status']

        for device, device_data in self.result_json.items():
            self.packets_sent.append(int(device_data['ping_stats']['sent'][-1]))
            self.packets_received.append(int(device_data['ping_stats']['received'][-1]))
            self.packets_dropped.append(int(device_data['ping_stats']['dropped'][-1]))
            self.device_names.append(device_data['name'])
            self.device_modes.append(device_data['mode'])
            self.device_channels.append(device_data['channel'])
            self.device_mac.append(device_data['mac'])
            self.device_ips.append(device_data['ip'])
            self.device_bssid.append(device_data['bssid'])
            self.device_ssid.append(device_data['ssid'])
            if float(device_data['sent']) == 0:
                self.packet_loss_percent.append(0)
                # self.client_unrechability_percent.append(0)
            else:
                if device_data['ping_stats']['sent'] == [] or float(device_data['ping_stats']['sent'][-1]) == 0:
                    self.packet_loss_percent.append(0)
                else:
                    self.packet_loss_percent.append(float(device_data['ping_stats']['dropped'][-1]) / float(device_data['ping_stats']['sent'][-1]) * 100)
                # self.client_unrechability_percent.append(float(device_data['dropped']) / (float(self.duration) * 60) * 100)
            t_rtt_values = sorted(list(device_data['rtts'].values()))
            if t_rtt_values != []:
                while (0.11 in t_rtt_values):
                    t_rtt_values.remove(0.11)
                self.device_avg.append(float(sum(t_rtt_values) / len(t_rtt_values)))
                self.device_min.append(float(min(t_rtt_values)))
                self.device_max.append(float(max(t_rtt_values)))
            else:
                self.device_avg.append(0)
                self.device_min.append(0)
                self.device_max.append(0)
            # self.device_avg.append(float(sum(t_rtt_values) / len(t_rtt_values)))
            # self.device_min.append(float(device_data['min_rtt'].replace(',', '')))
            # self.device_max.append(float(device_data['max_rtt'].replace(',', '')))
            # self.device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
            if device_data['os'] == 'Virtual':
                self.report_names.append('{} {}'.format(device, device_data['os'])[0:25])
            else:
                self.report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name']))
            if device_data['remarks'] != []:
                self.device_names_with_errors.append(device_data['name'])
                self.devices_with_errors.append(device)
                self.remarks.append(','.join(device_data['remarks']))
            logging.info('{} {} {}'.format(*self.packets_sent,
                                           *self.packets_received,
                                           *self.packets_dropped))
            logging.info('{} {} {}'.format(*self.device_min,
                                           *self.device_max,
                                           *self.device_avg))

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
        report.set_title('Ping Plotter Test Report')
        report.build_banner()

        # test setup info
        if self.do_webUI:
            self.real_sta_list = self.sta_list
            for resource in self.real_sta_list:
                shelf, r_id, _ = resource.split('.')
                url = 'http://{}:{}/resource/{}/{}?fields=hw version'.format(self.host, self.port, shelf, r_id)
                hw_version = requests.get(url)
                hw_version = hw_version.json()
                if 'resource' in hw_version.keys():
                    hw_version = hw_version['resource']
                    if 'hw version' in hw_version.keys():
                        hw_version = hw_version['hw version']
                        print(hw_version)
                        if 'Win' in hw_version:
                            self.windows += 1
                        elif 'Lin' in hw_version:
                            self.linux += 1
                        elif 'Apple' in hw_version:
                            self.mac += 1
                        else:
                            self.android += 1
                    else:
                        logging.warning('Malformed response for hw version query on resource manager.')
                else:
                    logging.warning('Malformed response for hw version query on resource manager.')
        # Test setup information table for devices in device list
        if config_devices == '':
            test_setup_info = {
                'SSID': [self.ssid if self.ssid else 'TEST CONFIGURED'][0],
                'Security': [self.security if self.ssid else 'TEST CONFIGURED'][0],
                'Website / IP': self.target,
                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.sta_list), len(self.sta_list) - len(self.real_sta_list), self.android, self.windows, self.linux, self.mac),
                'Duration': self.duration
            }
        # Test setup information table for devices in groups
        else:
            group_names = ', '.join(config_devices.keys())
            profile_names = ', '.join(config_devices.values())
            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
            test_setup_info = {
                'Configuration': configmap,
                'Website / IP': self.target,
                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.sta_list), len(self.sta_list) - len(self.real_sta_list), self.android, self.windows, self.linux, self.mac),
                'Duration': self.duration
            }
        report.test_setup_table(
            test_setup_data=test_setup_info, value='Test Setup Information')

        # objective and description
        report.set_obj_html(_obj_title='Objective',
                            _obj='''Candela Ping Plotter Test assesses the network connectivity for specified clients by measuring Round
                            Trip data packet Travel time. It also detects issues like packet loss, delays, and
                            response time variations, ensuring effective device communication and identifying
                            connectivity problems.
                            ''')
        report.build_objective()

        # uptime and downtime
        report.set_table_title(
            'Individual Ping Plotter Graph for {} duration:'.format(self.duration)
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

        # individual client report table
        report.set_table_title(
            'Individual client table report:'
        )
        report.build_table_title()
        if self.real:
            # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
            if self.expected_passfail_val or self.csv_name:
                pass_fail_list, test_input_list = self.get_pass_fail_list()
            # When groups are provided a seperate table will be generated for each group using generate_dataframe
            if self.group_name:
                for key, val in group_device_map.items():
                    if self.expected_passfail_val or self.csv_name:
                        dataframe = self.generate_dataframe(
                            val,
                            self.report_names,
                            self.device_ips,
                            self.device_mac,
                            self.device_bssid,
                            self.device_ssid,
                            self.device_channels,
                            self.packets_sent,
                            self.packets_received,
                            self.packet_loss_percent,
                            test_input_list,
                            self.device_avg,
                            pass_fail_list)
                    else:
                        dataframe = self.generate_dataframe(
                            val,
                            self.report_names,
                            self.device_ips,
                            self.device_mac,
                            self.device_bssid,
                            self.device_ssid,
                            self.device_channels,
                            self.packets_sent,
                            self.packets_received,
                            self.packet_loss_percent,
                            [],
                            self.device_avg,
                            [])
                    if dataframe:
                        report.set_obj_html("", "Group: {}".format(key))
                        report.build_objective()
                        dataframe1 = pd.DataFrame(dataframe)
                        report.set_table_dataframe(dataframe1)
                        report.build_table()
            else:
                individual_report_df = pd.DataFrame({
                    'Wireless Client': self.report_names,
                    'IP Address': self.device_ips,
                    'MAC': self.device_mac,
                    'BSSID': self.device_bssid,
                    'SSID': self.device_ssid,
                    'Channel': self.device_channels,
                    'Packets Sent': self.packets_sent,
                    'Packets Received': self.packets_received,
                    'Packet Loss %': self.packet_loss_percent,
                    'AVG RTT (ms)': self.device_avg,
                })
                if self.expected_passfail_val or self.csv_name:
                    individual_report_df['Expected Packet loss %'] = test_input_list
                    individual_report_df['Status '] = pass_fail_list
                report.set_table_dataframe(individual_report_df)
                report.build_table()
        else:
            individual_report_df = pd.DataFrame({
                'Wireless Client': self.report_names,
                'IP Address': self.device_ips,
                'MAC': self.device_mac,
                'BSSID': self.device_bssid,
                'SSID': self.device_ssid,
                'Channel': self.device_channels,
                'Packets Sent': self.packets_sent,
                'Packets Received': self.packets_received,
                'Packet Loss %': self.packet_loss_percent,
                'AVG RTT (ms)': self.device_avg,
                # 'Client Unrechability %': self.client_unrechability_percent
            })
            report.set_table_dataframe(individual_report_df)
            report.build_table()

        # packets sent vs received vs dropped
        report.set_table_title(
            'Packets sent vs packets received vs packets dropped')
        report.build_table_title()
        x_fig_size = 20
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

        # packets rtt graph
        report.set_table_title('Ping RTT Graph')
        report.build_table_title()

        graph = lf_bar_graph_horizontal(_data_set=[self.device_min, self.device_avg, self.device_max],
                                        _xaxis_name='Time (ms)',
                                        _yaxis_name='Wireless Clients',
                                        _label=[
                                            'Min RTT (ms)', 'Average RTT (ms)', 'Max RTT (ms)'],
                                        _graph_image_name='Ping RTT per client',
                                        _yaxis_label=self.report_names,
                                        _yaxis_categories=self.report_names,
                                        _yaxis_step=1,
                                        _yticks_font=8,
                                        _graph_title='Ping RTT per client',
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
            'Min RTT (ms)': self.device_min,
            'Average RTT (ms)': self.device_avg,
            'Max RTT (ms)': self.device_max
        })
        report.set_table_dataframe(dataframe2)
        report.build_table()

        # realtime ping graphs
        report.set_table_title('Individual RTT vs Time Plots:')
        report.build_table_title()

        # graphs for above

        self.build_area_graphs(report_obj=report)

        # check if there are remarks for any device. If there are remarks, build table else don't
        if self.remarks != []:
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

        if self.do_webUI:
            self.copy_reports(report_path_date_time)

    def copy_reports_to_home_dir(self):
        curr_path = self.ui_report_dir
        home_dir = os.path.expanduser("~")
        out_folder_name = "WebGui_Reports"
        new_path = os.path.join(home_dir, out_folder_name)
        # webgui directory creation
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        test_name = self.ui_report_dir.split("/")[-1]
        test_name_dir = os.path.join(new_path, test_name)
        # in webgui-reports DIR creating a directory with test name
        if not os.path.exists(test_name_dir):
            os.makedirs(test_name_dir)
        shutil.copytree(curr_path, test_name_dir, dirs_exist_ok=True)

    def generate_dataframe(self, groupdevlist: List[str], report_names: List[str], device_ips: List[str], device_mac: List[str], device_bssid: List[str], device_ssid: List[str],
                           device_channels: List[str], packets_sent: List[int], packets_received: List[int], packet_loss_percent: List[float], test_input_list: List[str],
                           device_avg: List[float], status: List[str]) -> Optional[pd.DataFrame]:
        """
        Creates a separate DataFrame for each group of devices.

        Returns:
            DataFrame: A DataFrame for each device group.
            Returns None if neither device in a group is configured.
        """

        report_name = []
        macids = []
        device_ip = []
        bssid = []
        dev_ssid = []
        dev_channels = []
        packet_sent = []
        packet_received = []
        loss_percent = []
        input_test_list = []
        dev_avg = []
        statuslist = []
        interop_tab_data = self.json_get('/adb/')["devices"]
        for i in range(len(report_names)):
            for j in groupdevlist:
                # For a string like "1.360 Lin test3":
                # - report_names[i].split(" ")[2] gives 'test3' (device name)
                # - report_names[i].split(" ")[1] gives 'Lin' (OS type)
                # This condition filters out Android clients and matches device name with j
                if j == report_names[i].split(" ")[2] and report_names[i].split(" ")[1] != 'android':
                    report_name.append(report_names[i])
                    macids.append(device_mac[i])
                    device_ip.append(device_ips[i])
                    bssid.append(device_bssid[i])
                    dev_ssid.append(device_ssid[i])
                    dev_channels.append(device_channels[i])
                    packet_sent.append(packets_sent[i])
                    packet_received.append(packets_received[i])
                    loss_percent.append(packet_loss_percent[i])
                    dev_avg.append(device_avg[i])
                    if self.expected_passfail_val or self.csv_name:
                        input_test_list.append(test_input_list[i])
                        statuslist.append(status[i])
                # For a string like 1.15 android samsungmob:
                # - report_names[i].split(' ')[2] (e.g., 'samsungmob') matches item['user-name']
                # - The group name (e.g., 'RZCTA09CTXF') matches with item['name'].split('.')[2]
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] == report_names[i].split(' ')[2] and j == item['name'].split('.')[2]:
                                report_name.append(report_names[i])
                                macids.append(device_mac[i])
                                device_ip.append(device_ips[i])
                                bssid.append(device_bssid[i])
                                dev_ssid.append(device_ssid[i])
                                dev_channels.append(device_channels[i])
                                packet_sent.append(packets_sent[i])
                                packet_received.append(packets_received[i])
                                loss_percent.append(packet_loss_percent[i])
                                dev_avg.append(device_avg[i])
                                if self.expected_passfail_val or self.csv_name:
                                    input_test_list.append(test_input_list[i])
                                    statuslist.append(status[i])
        if len(report_name) != 0:
            dataframe = {
                'Wireless Client': report_name,
                'IP Address': macids,
                'MAC': device_ip,
                'BSSID': bssid,
                'SSID': dev_ssid,
                'Channel': dev_channels,
                'Packets Sent': packet_sent,
                'Packets Received': packet_received,
                'Packet Loss %': loss_percent,
                'AVG RTT (ms)': dev_avg,
            }
            if self.expected_passfail_val or self.csv_name:
                dataframe['Expected Packet loss %'] = input_test_list
                dataframe['Status'] = statuslist
            return dataframe
        else:
            return None


def validate_args(args):
    # input sanity
    if args.virtual is False and args.real is False:
        logger.error('Atleast one of --real or --virtual is required')
        exit(1)
    if args.virtual is True and args.radio is None:
        logger.error('--radio required')
        exit(1)
    if args.virtual is True and args.ssid is None:
        logger.error('--ssid required for virtual stations')
        exit(1)
    if args.security != 'open' and args.passwd == '[BLANK]':
        logger.error('--passwd required')
        exit(1)

    if args.device_csv_name and args.expected_passfail_value:
        logger.error("Enter either --device_csv_name or --expected_passfail_value")
        exit(1)
    if args.ssid and args.passwd and args.group_name and args.profile_name:
        logger.error('either --ssid,--password or --profile_name,--group_name should be given')
        exit(1)
    if args.use_default_config is False and args.group_name is None and args.file_name is None and args.profile_name is None:
        if args.ssid is None:
            logger.error('--ssid required for Wi-Fi configuration')
            exit(1)

        if args.security.lower() != 'open' and args.passwd == '[BLANK]':
            logger.error('--passwd required for Wi-Fi configuration')
            exit(1)

        if args.server_ip is None:
            logger.error('--server_ip or upstream ip required for Wi-fi configuration')
            exit(1)
    elif args.use_default_config is False and args.resources and (args.ssid is None or args.passwd is None or args.security is None):
        logger.error("Please provide ssid password and security when device list is given")
        exit(1)

    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []
    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)


def main():

    help_summary = '''\
The Candela Tech ping plotter test assesses the network connectivity for specified clients by measuring Round
Trip data packet travel time. It also detects issues like packet loss, delays, and
response time variations, ensuring effective device communication and identifying
connectivity problems.
    '''
    parser = argparse.ArgumentParser(
        prog='interop_ping.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
            Allows user to run the ping plotter test on a target IP for the given duration and packet interval
            with either selected number of virtual stations or provides the list of available real devices
            and allows the user to select the real devices and run ping plotter test on them.
        ''',
        description='''
        NAME: lf_interop_ping_plotter.py

        PURPOSE: lf_interop_ping_plotter.py will let the user select real devices, virtual devices or both and then allows them to run
        ping plotter test for user given duration and packet interval on the given target IP or domain name and generates realtime ping status and line charts for every device.

        EXAMPLE-1:
        Command Line Interface to run ping plotter test with only virtual clients with eth1 as the default target
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61 --debug

        EXAMPLE-2:
        Command Line Interface to stop cleaning up stations after the test
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61 --debug --no_cleanup

        EXAMPLE-3:
        Command Line Interface to run ping plotter test with only real clients
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61

        EXAMPLE-4:
        Command Line Interface to run ping plotter test with both real and virtual clients
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.103 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1m --server_ip 192.168.1.61

        EXAMPLE-5:
        Command Line Interface to run ping plotter test with a different target
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --ping_interval 5 --ping_duration 1m --target 192.168.1.61

        EXAMPLE-6:
        Command Line Interface to run ping plotter with existing real stations instead of giving input after starting the test
        python3 lf_interop_ping_plotter.py --mgr 192.168.200.63 --real --ping_interval 5 --ping_duration 1m --target 192.168.1.61 --resources 1.10,1.11

        EXAMPLE-7:
        Command Line Interface to run ping plotter test by setting the same expected Pass/Fail value for all devices
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m --expected_passfail_value 3
        --use_default_config

        EXAMPLE-8:
        Command Line Interface to run ping plotter test by setting device specific Pass/Fail values in the csv file
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m --device_csv_name device.csv
        --use_default_config

        EXAMPLE-9:
        Command Line Interface to run ping plotter test by configuring Real Devices with SSID, Password, and Security
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --ssid NETGEAR_2G_wpa2
        --security wpa2 --passwd Password@123 --server_ip 192.168.204.74 --wait_time 30

        EXAMPLE-10:
        Command Line Interface to run ping plotter test by setting device specific Pass/Fail values in the csv file
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --ssid NETGEAR_2G_wpa2
        --security wpa2 --passwd Password@123 --server_ip 192.168.204.74 --wait_time 30 --device_csv_name device.csv

        EXAMPLE-11:
        Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4
        --profile_name Openz --file_name g219 --server_ip 192.168.204.74

        EXAMPLE-12:
        Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles with expected Pass/Fail values
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4,grp5
        --profile_name Openz,Openz --file_name g219 --expected_passfail_value 22 --server_ip 192.168.204.74

        EXAMPLE-13:
        Command Line Interface to run ping plotter test by Configuring Devices in Groups with Specific Profiles with device_csv_name
        python3 lf_interop_ping_plotter.py --mgr 192.168.204.74 --real --target 192.168.204.66 --ping_interval 1 --ping_duration 1m  --group_name grp4,grp5
        --profile_name Openz,Openz --file_name g219 --device_csv_name device.csv --server_ip 192.168.204.74

        SCRIPT_CLASSIFICATION : Test

        SCRIPT_CATEGORIES: Performance, Functional, Report Generation

        NOTES:
        1.Use './lf_interop_ping.py --help' to see command line usage and options
        2.Use 's','m','h' as suffixes for ping_duration in seconds, minutes and hours respectively
        3.After passing the cli, if --real flag is selected, then a list of available real devices will be displayed on the terminal
        4.Enter the real device resource numbers seperated by commas (,)
        5.For --target, you can specify it as eth1, IP address or domain name (e.g., google.com)

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date    - 06/12/2023
        Build version   - 5.4.7
        kernel version  - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.
        '''
    )
    optional = parser.add_argument_group('Optional arguments')
    webUI_args = parser.add_argument_group('webUI arguments')\

    # optional arguments
    optional.add_argument('--mgr',
                          type=str,
                          help='hostname where LANforge GUI is running',
                          default='localhost')

    optional.add_argument('--target',
                          type=str,
                          help='Target URL or port for ping plotter test',
                          default='1.1.eth1')

    optional.add_argument('--ping_interval',
                          type=str,
                          help='Interval (in seconds) between the echo requests',
                          default='1')

    optional.add_argument('--ping_duration',
                          type=str,
                          help='Duration to run the ping plotter test',
                          default='1m')

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

    optional.add_argument('--no_cleanup',
                          action="store_true",
                          help='specify this flag to stop cleaning up generic cxs after the test')

    # webUI arguments
    webUI_args.add_argument('--do_webUI',
                            action='store_true',
                            help='specify this flag when triggering a test from webUI')

    webUI_args.add_argument('--resources',
                            help='Specify the real device ports seperated by comma')

    webUI_args.add_argument('--ui_report_dir',
                            help='Specify the results directory to store the reports for webUI')

    # local report directory used by lf_report
    parser.add_argument('--local_lf_report_dir',
                        help='--local_lf_report_dir override the report path (lanforge/html-reports), primary used when making another directory lanforge/html-report/<test_rig>',
                        default="")

    # logging configuration:
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')
    parser.add_argument('--group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument('--file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument("--eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--pairwise", type=str, default='[BLANK]')
    parser.add_argument("--private_key", type=str, default='[BLANK]', help='Specify EAP private key certificate file.')
    parser.add_argument("--ca_cert", type=str, default='[BLANK]', help='Specifiy the CA certificate file name')
    parser.add_argument("--client_cert", type=str, default='[BLANK]', help='Specify the client certificate file name')
    parser.add_argument("--pk_passwd", type=str, default='[BLANK]', help='Specify the password for the private key')
    parser.add_argument("--pac_file", type=str, default='[BLANK]', help='Specify the pac file name')
    parser.add_argument('--expected_passfail_value', help='Enter the expected packet loss', default=None)
    parser.add_argument('--device_csv_name', type=str, help='Enter the csv name to store expected values', default=None)
    parser.add_argument('--wait_time', type=int, help='Enter the maximum wait time for configurations to apply', default=60)

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    validate_args(args)
    # set the logger level to debug
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    configure = not args.use_default_config

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
    group_name = args.group_name
    file_name = args.file_name
    profile_name = args.profile_name
    eap_method = args.eap_method
    eap_identity = args.eap_identity
    ieee8021x = args.ieee8021x
    ieee80211u = args.ieee80211u
    ieee80211w = args.ieee80211w
    enable_pkc = args.enable_pkc
    bss_transition = args.bss_transition
    power_save = args.power_save
    disable_ofdma = args.disable_ofdma
    roam_ft_ds = args.roam_ft_ds
    key_management = args.key_management
    pairwise = args.pairwise
    private_key = args.private_key
    ca_cert = args.ca_cert
    client_cert = args.client_cert
    pk_passwd = args.pk_passwd
    pac_file = args.pac_file

    if 's' in duration or 'S' in duration:
        if 's' in duration:
            duration = float(duration.replace('s', '')) / 60
            report_duration = '00:00:{:02}'.format(int(args.ping_duration.replace('s', '')))
        else:
            duration = float(duration.replace('S', '')) / 60
            report_duration = '00:00:{:02}'.format(int(args.ping_duration.replace('S', '')))
    elif 'm' in duration or 'M' in duration:
        if 'm' in duration:
            duration = float(duration.replace('m', ''))
            report_duration = '00:{:02}:00'.format(int(args.ping_duration.replace('m', '')))
        else:
            duration = float(duration.replace('M', ''))
            report_duration = '00:{:02}:00'.format(int(args.ping_duration.replace('M', '')))
    elif 'h' in duration or 'H' in duration:
        if 'H' in duration:
            duration = float(duration.replace('h', '')) * 60
            report_duration = '{:02}:00:00'.format(int(args.ping_duration.replace('h', '')))
        else:
            duration = float(duration.replace('H', '')) * 60
            report_duration = '{:02}:00:00'.format(int(args.ping_duration.replace('H', '')))

    # webUI argument check
    do_webUI = args.do_webUI
    webUI_resources = args.resources
    ui_report_dir = args.ui_report_dir
    if do_webUI and webUI_resources is None and group_name is None:
        print('--resources argument is required when --do_webUI is specified')
        exit(0)
    if do_webUI and ui_report_dir is None:
        print('--ui_report_dir argument is required when --do_webUI is specified')
        exit(0)

    debug = args.debug

    if debug:
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
                lanforge_password=mgr_password, target=target, interval=interval, sta_list=[], virtual=args.virtual, real=args.real, duration=report_duration, do_webUI=do_webUI, debug=debug,
                ui_report_dir=ui_report_dir, csv_name=args.device_csv_name, expected_passfail_val=args.expected_passfail_value, wait_time=args.wait_time, group_name=group_name)

    # creating virtual stations if --virtual flag is specified
    if args.virtual:

        logging.info('Proceeding to create {} virtual stations on {}'.format(num_sta, radio))
        station_list = LFUtils.portNameSeries(
            prefix_='sta', start_id_=0, end_id_=num_sta - 1, padding_number_=100000, radio=radio)
        ping.sta_list = station_list
        if debug:
            logging.info('Virtual Stations: {}'.format(station_list).replace(
                '[', '').replace(']', '').replace('\'', ''))

    # selecting real clients if --real flag is specified
    if args.real:
        Devices = RealDevice(manager_ip=mgr_ip, selected_bands=[])
        Devices.get_devices()
        ping.Devices = Devices
        # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
        if configure:
            config_devices = {}
            obj = DeviceConfig.DeviceConfig(lanforge_ip=mgr_ip, file_name=file_name, wait_time=args.wait_time)
            # Case 1: Group name, file name, and profile name are provided
            if group_name and file_name and profile_name:
                selected_groups = group_name.split(',')
                selected_profiles = profile_name.split(',')
                for i in range(len(selected_groups)):
                    config_devices[selected_groups[i]] = selected_profiles[i]
                obj.initiate_group()
                group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
                # Configure devices in the selected group with the selected profile
                eid_list = asyncio.run(obj.connectivity(config=config_devices, upstream=server_ip))
                ping.select_real_devices(real_devices=Devices, device_list=eid_list)
            # Case 2: Device list is empty but config flag is True — prompt the user to input device details for configuration
            else:
                all_devices = obj.get_all_devices()
                device_list = []
                config_dict = {
                    'ssid': ssid,
                    'passwd': password,
                    'enc': security,
                    'eap_method': eap_method,
                    'eap_identity': eap_identity,
                    'ieee80211': ieee8021x,
                    'ieee80211u': ieee80211u,
                    'ieee80211w': ieee80211w,
                    'enable_pkc': enable_pkc,
                    'bss_transition': bss_transition,
                    'power_save': power_save,
                    'disable_ofdma': disable_ofdma,
                    'roam_ft_ds': roam_ft_ds,
                    'key_management': key_management,
                    'pairwise': pairwise,
                    'private_key': private_key,
                    'ca_cert': ca_cert,
                    'client_cert': client_cert,
                    'pk_passwd': pk_passwd,
                    'pac_file': pac_file,
                    'server_ip': server_ip,
                }
                # If the test is triggered from the webUI, use the provided resources
                if webUI_resources is not None:
                    webUI_resources = webUI_resources.split(',')
                    print(f"WebUI resources: {webUI_resources}")
                    devices_list = []
                    for device in webUI_resources:
                        devices_list.append(device.split('.')[0] + '.' + device.split('.')[1])
                    dev_list = asyncio.run(obj.connectivity(device_list=devices_list, wifi_config=config_dict))
                else:
                    # print(f"Available devices: {all_devices}")
                    for device in all_devices:
                        if device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                        else:
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])

                    logger.info(f"Available devices: {device_list}")
                    dev_list = input("Enter the desired resources to run the test:").split(',')
                    dev_list = asyncio.run(obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                ping.select_real_devices(real_devices=Devices, device_list=dev_list)
        # Case 3: Config is False, no device list is provided, and no group is selected
        else:
            Devices.get_devices()
            ping.Devices = Devices
            if webUI_resources is not None:
                # webUI_resources = ping.filter_iOS_devices(webUI_resources)
                if len(webUI_resources) == 0:
                    logger.info("There are no devices available")
                    exit(0)
            if not do_webUI and webUI_resources is None:
                device_list = ping.Devices.get_devices()
                logger.info(f"Available devices: {device_list}")
                dev_list = input("Enter the desired resources to run the test:").split(',')
                ping.select_real_devices(real_devices=Devices, device_list=dev_list)
            else:
                webUI_resources = webUI_resources.split(',')
                ping.select_real_devices(real_devices=Devices, real_sta_list=webUI_resources, base_interop_obj=Devices)

    # station precleanup
    ping.cleanup()

    # building station if virtual
    if args.virtual:
        ping.buildstation()

    # check if generic tab is enabled or not
    if not ping.check_tab_exists():
        logging.error('Generic Tab is not available.\nAborting the test.')
        exit(0)

    ping.sta_list += ping.real_sta_list

    # creating generic endpoints
    ping.create_generic_endp()

    logging.info('{}'.format(*ping.generic_endps_profile.created_cx))

    # run the test for the given duration
    logging.info('Running the ping plotter test for {} minutes'.format(duration))

    ping.start_time = datetime.now()

    # start generate endpoint
    ping.start_generic()
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
    ping_stats = {}
    for station in ping.sta_list:
        rtts[station] = {}
        ping_stats[station] = {
            'sent': [],
            'received': [],
            'dropped': []
        }
    while (loop_timer <= duration):
        t_init = datetime.now()
        try:
            result_data = ping.get_results()
            if isinstance(result_data, dict):
                if 'UNKNOWN' in result_data['name']:
                    raise ValueError("There are no valid generic endpoints to run the test")
            else:
                keys = [list(d.keys())[0] for d in result_data]
                keys = [key for key in keys if 'UNKNOWN' not in key]
                if len(keys) == 0:
                    raise ValueError("There are no valid generic endpoints to run the test")
        except ValueError as e:
            logger.info(result_data)
            logger.error(e)
            exit(0)
        # logging.info(result_data)
        if args.virtual:
            ports_data_dict = ping.json_get('/ports/all/')['interfaces']
            ports_data = {}
            for ports in ports_data_dict:
                port, port_data = list(ports.keys())[0], list(ports.values())[0]
                ports_data[port] = port_data
            if isinstance(result_data, dict):
                for station in ping.sta_list:
                    if station not in ping.real_sta_list:
                        current_device_data = ports_data[station]
                        if station.split('.')[2] in result_data['name']:
                            ping.result_json[station] = {
                                'command': result_data['command'],
                                'sent': result_data['tx pkts'],
                                'recv': result_data['rx pkts'],
                                'dropped': result_data['dropped'],
                                'mac': current_device_data['mac'],
                                'ip': current_device_data['ip'],
                                'bssid': current_device_data['ap'],
                                'ssid': current_device_data['ssid'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': station,
                                'os': 'Virtual',
                                'remarks': [],
                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                            }
                            ping_stats[station]['sent'].append(result_data['tx pkts'])
                            ping_stats[station]['received'].append(result_data['rx pkts'])
                            ping_stats[station]['dropped'].append(result_data['dropped'])
                            ping.result_json[station]['ping_stats'] = ping_stats[station]
                            if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results']:
                                temp_last_results = result_data['last results'].split('\n')[0: len(result_data['last results']) - 1]
                                drop_count = 0  # let dropped = 0 initially
                                dropped_packets = []
                                # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                for result in temp_last_results:
                                    try:
                                        # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                        t_result, t_fail = result.split('***')
                                    except BaseException:
                                        continue
                                    t_result = t_result.split()
                                    if 'icmp_seq=' not in result and 'time=' not in result:
                                        continue
                                    for t_data in t_result:
                                        if 'icmp_seq=' in t_data:
                                            seq_number = int(t_data.strip('icmp_seq='))
                                        if 'time=' in t_data:
                                            rtt = float(t_data.strip('time='))
                                    rtts[station][seq_number] = rtt
                                    rtts_list.append(rtt)

                                    # finding dropped packets
                                    t_fail = t_fail.split()  # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                    t_drop_val = t_fail[1]  # t_drop_val = '0'
                                    t_drop_val = int(t_drop_val)  # type cast string to int
                                    if t_drop_val != drop_count:
                                        current_drop_packets = t_drop_val - drop_count
                                        drop_count = t_drop_val
                                        for drop_packet in range(1, current_drop_packets + 1):
                                            dropped_packets.append(seq_number - drop_packet)

                            if rtts_list == []:
                                rtts_list = [0]
                            min_rtt = str(min(rtts_list))
                            avg_rtt = str(sum(rtts_list) / len(rtts_list))
                            max_rtt = str(max(rtts_list))
                            ping.result_json[station]['min_rtt'] = min_rtt
                            ping.result_json[station]['avg_rtt'] = avg_rtt
                            ping.result_json[station]['max_rtt'] = max_rtt
                            if list(rtts[station].keys()) != []:
                                required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                                for seq in required_sequence_numbers:
                                    if seq not in rtts[station].keys():
                                        if seq in dropped_packets:
                                            rtts[station][seq] = 0
                                        else:
                                            rtts[station][seq] = 0.11
                            else:
                                ping.result_json[station]['rtts'] = {}
                            ping.result_json[station]['rtts'] = rtts[station]
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                            # ping.result_json[station]['dropped_packets'] = dropped_packets

            else:
                for station in ping.sta_list:
                    if station not in ping.real_sta_list:
                        current_device_data = ports_data[station]
                        for ping_device in result_data:
                            ping_endp, ping_data = list(ping_device.keys())[
                                0], list(ping_device.values())[0]
                            if station.split('.')[2] in ping_endp:
                                ping.result_json[station] = {
                                    'command': ping_data['command'],
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    'mac': current_device_data['mac'],
                                    'ip': current_device_data['ip'],
                                    'bssid': current_device_data['ap'],
                                    'ssid': current_device_data['ssid'],
                                    'channel': current_device_data['channel'],
                                    'mode': current_device_data['mode'],
                                    'name': station,
                                    'os': 'Virtual',
                                    'remarks': [],
                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                }
                                ping_stats[station]['sent'].append(ping_data['tx pkts'])
                                ping_stats[station]['received'].append(ping_data['rx pkts'])
                                ping_stats[station]['dropped'].append(ping_data['dropped'])
                                ping.result_json[station]['ping_stats'] = ping_stats[station]
                                if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results']:
                                    temp_last_results = ping_data['last results'].split('\n')[0: len(ping_data['last results']) - 1]
                                    drop_count = 0  # let dropped = 0 initially
                                    dropped_packets = []
                                    # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                    for result in temp_last_results:
                                        try:
                                            # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                            t_result, t_fail = result.split('***')
                                        except BaseException:
                                            continue  # first line of ping result
                                        t_result = t_result.split()
                                        if 'icmp_seq=' not in result and 'time=' not in result:
                                            continue
                                        for t_data in t_result:
                                            if 'icmp_seq=' in t_data:
                                                seq_number = int(t_data.strip('icmp_seq='))
                                            if 'time=' in t_data:
                                                rtt = float(t_data.strip('time='))
                                        rtts[station][seq_number] = rtt
                                        rtts_list.append(rtt)

                                        # finding dropped packets
                                        t_fail = t_fail.split()  # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                        t_drop_val = t_fail[1]  # t_drop_val = '0'
                                        t_drop_val = int(t_drop_val)  # type cast string to int
                                        if t_drop_val != drop_count:
                                            current_drop_packets = t_drop_val - drop_count
                                            drop_count = t_drop_val
                                            for drop_packet in range(1, current_drop_packets + 1):
                                                dropped_packets.append(seq_number - drop_packet)

                                if rtts_list == []:
                                    rtts_list = [0]
                                min_rtt = str(min(rtts_list))
                                avg_rtt = str(sum(rtts_list) / len(rtts_list))
                                max_rtt = str(max(rtts_list))
                                ping.result_json[station]['min_rtt'] = min_rtt
                                ping.result_json[station]['avg_rtt'] = avg_rtt
                                ping.result_json[station]['max_rtt'] = max_rtt
                                if list(rtts[station].keys()) != []:
                                    required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                                    for seq in required_sequence_numbers:
                                        if seq not in rtts[station].keys():
                                            if seq in dropped_packets:
                                                rtts[station][seq] = 0
                                            else:
                                                rtts[station][seq] = 0.11
                                else:
                                    ping.result_json[station]['rtts'] = {}
                                ping.result_json[station]['rtts'] = rtts[station]
                                ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                                # ping.result_json[station]['dropped_packets'] = dropped_packets

        if args.real:
            if isinstance(result_data, dict):
                for station in ping.real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    # logging.info(current_device_data)
                    if station in result_data['name']:
                        # logging.info(result_data['last results'].split('\n'))
                        if len(result_data['last results']) != 0:
                            result = result_data['last results'].split('\n')
                            if len(result) > 1:
                                last_result = result[-2]
                            else:
                                last_result = result[-1]
                        else:
                            last_result = ""

                        hw_version = current_device_data['hw version']
                        if "Win" in hw_version:
                            os = "Windows"
                        elif "Linux" in hw_version:
                            os = "Linux"
                        elif "Apple" in hw_version:
                            os = "Mac"
                        else:
                            os = "Android"

                        ping.result_json[station] = {
                            'command': result_data['command'],
                            'sent': result_data['tx pkts'],
                            'recv': result_data['rx pkts'],
                            'dropped': result_data['dropped'],
                            'mac': current_device_data['mac'],
                            'ip': current_device_data['ip'],
                            'bssid': current_device_data['ap'],
                            'ssid': current_device_data['ssid'],
                            'channel': current_device_data['channel'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                            'os': os,
                            'remarks': [],
                            'last_result': [last_result][0]
                        }
                        ping_stats[station]['sent'].append(result_data['tx pkts'])
                        ping_stats[station]['received'].append(result_data['rx pkts'])
                        ping_stats[station]['dropped'].append(result_data['dropped'])
                        ping.result_json[station]['ping_stats'] = ping_stats[station]
                        if len(result_data['last results']) != 0:
                            temp_last_results = result_data['last results'].split('\n')[0: len(result_data['last results']) - 1]
                            drop_count = 0  # let dropped = 0 initially
                            dropped_packets = []
                            # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                            for result in temp_last_results:
                                try:
                                    # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                    t_result, t_fail = result.split('***')
                                except BaseException:
                                    continue
                                t_result = t_result.split()
                                if 'icmp_seq=' not in result and 'time=' not in result:
                                    continue
                                for t_data in t_result:
                                    if 'icmp_seq=' in t_data:
                                        seq_number = int(t_data.strip('icmp_seq='))
                                    if 'time=' in t_data:
                                        rtt = float(t_data.strip('time='))
                                rtts[station][seq_number] = rtt
                                rtts_list.append(rtt)

                                # finding dropped packets
                                t_fail = t_fail.split()  # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                t_drop_val = t_fail[1]  # t_drop_val = '0'
                                t_drop_val = int(t_drop_val)  # type cast string to int
                                if t_drop_val != drop_count:
                                    current_drop_packets = t_drop_val - drop_count
                                    drop_count = t_drop_val
                                    for drop_packet in range(1, current_drop_packets + 1):
                                        dropped_packets.append(seq_number - drop_packet)

                        if rtts_list == []:
                            rtts_list = [0]
                        min_rtt = str(min(rtts_list))
                        avg_rtt = str(sum(rtts_list) / len(rtts_list))
                        max_rtt = str(max(rtts_list))
                        ping.result_json[station]['min_rtt'] = min_rtt
                        ping.result_json[station]['avg_rtt'] = avg_rtt
                        ping.result_json[station]['max_rtt'] = max_rtt
                        if ping.result_json[station]['os'] == 'Android' and isinstance(rtts, dict) and rtts != {}:
                            if list(rtts[station].keys()) == []:
                                ping.result_json[station]['sent'] = str(0)
                                ping.result_json[station]['recv'] = str(0)
                                ping.result_json[station]['dropped'] = str(0)
                            else:
                                ping.result_json[station]['sent'] = str(max(list(rtts[station].keys())))
                                ping.result_json[station]['recv'] = str(len(rtts[station].keys()))
                                ping.result_json[station]['dropped'] = str(int(ping.result_json[station]['sent']) - int(ping.result_json[station]['recv']))
                        if len(rtts[station].keys()) != 0:
                            required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                            for seq in required_sequence_numbers:
                                if seq not in rtts[station].keys():
                                    if seq in dropped_packets:
                                        rtts[station][seq] = 0
                                    else:
                                        rtts[station][seq] = 0.11
                        ping.result_json[station]['rtts'] = rtts[station]
                        ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])

            else:
                for station in ping.real_sta_list:
                    current_device_data = Devices.devices_data[station]
                    # print('<<<<<<<<<<<<<<<<<<<', current_device_data)
                    for ping_device in result_data:
                        ping_endp, ping_data = list(ping_device.keys())[
                            0], list(ping_device.values())[0]
                        eid = str(ping_data['eid'])
                        ping.sta_list = list(ping.sta_list)
                        # Removing devices with UNKNOWN CX
                        if 'UNKNOWN' in ping_endp:
                            device_id = eid.split('.')[0] + '.' + eid.split('.')[1]
                            if device_id == station.split('.')[0] + '.' + station.split('.')[1]:
                                ping.sta_list.remove(station)
                                ping.real_sta_list.remove(station)
                            logger.info(result_data)
                            logger.info("Excluding {} from report as there is no valid generic endpoint creation during the test(UNKNOWN CX)".format(device_id))
                            continue
                        if station in ping_endp:
                            if len(ping_data['last results']) != 0:
                                result = ping_data['last results'].split('\n')
                                if len(result) > 1:
                                    last_result = result[-2]
                                else:
                                    last_result = result[-1]
                            else:
                                last_result = ""

                            hw_version = current_device_data['hw version']
                            if "Win" in hw_version:
                                os = "Windows"
                            elif "Linux" in hw_version:
                                os = "Linux"
                            elif "Apple" in hw_version:
                                os = "Mac"
                            else:
                                os = "Android"

                            ping.result_json[station] = {
                                'command': ping_data['command'],
                                'sent': ping_data['tx pkts'],
                                'recv': ping_data['rx pkts'],
                                'dropped': ping_data['dropped'],
                                'mac': current_device_data['mac'],
                                'ip': current_device_data['ip'],
                                'bssid': current_device_data['ap'],
                                'ssid': current_device_data['ssid'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                'os': os,
                                'remarks': [],
                                'last_result': [last_result][0]
                            }
                            ping_stats[station]['sent'].append(ping_data['tx pkts'])
                            ping_stats[station]['received'].append(ping_data['rx pkts'])
                            ping_stats[station]['dropped'].append(ping_data['dropped'])
                            ping.result_json[station]['ping_stats'] = ping_stats[station]
                            if len(ping_data['last results']) != 0:
                                temp_last_results = ping_data['last results'].split('\n')[0: len(ping_data['last results']) - 1]
                                drop_count = 0  # let dropped = 0 initially
                                dropped_packets = []
                                for result in temp_last_results:
                                    # sample result - 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms *** drop: 0 (0, 0.000)  rx: 28  fail: 0  bytes: 1792 min/avg/max: 2.160/3.422/5.190
                                    if 'time=' in result:
                                        try:
                                            # fetching the first part of the last result e.g., 64 bytes from 192.168.1.61: icmp_seq=28 time=3.66 ms into t_result and the remaining part into t_fail
                                            t_result, t_fail = result.split('***')
                                        except BaseException:
                                            continue
                                        t_result = t_result.split()
                                        if 'icmp_seq=' not in result and 'time=' not in result:
                                            continue
                                        for t_data in t_result:
                                            if 'icmp_seq=' in t_data:
                                                seq_number = int(t_data.strip('icmp_seq='))
                                            if 'time=' in t_data:
                                                rtt = float(t_data.strip('time='))
                                        rtts[station][seq_number] = rtt
                                        rtts_list.append(rtt)

                                        # finding dropped packets
                                        t_fail = t_fail.split()  # [' drop:', '0', '(0, 0.000)', 'rx:', '28', 'fail:', '0', 'bytes:', '1792', 'min/avg/max:', '2.160/3.422/5.190']
                                        t_drop_val = t_fail[1]  # t_drop_val = '0'
                                        t_drop_val = int(t_drop_val)  # type cast string to int
                                        if t_drop_val != drop_count:
                                            current_drop_packets = t_drop_val - drop_count
                                            drop_count = t_drop_val
                                            for drop_packet in range(1, current_drop_packets + 1):
                                                dropped_packets.append(seq_number - drop_packet)

                            if rtts_list == []:
                                rtts_list = [0]
                            min_rtt = str(min(rtts_list))
                            avg_rtt = str(sum(rtts_list) / len(rtts_list))
                            max_rtt = str(max(rtts_list))
                            ping.result_json[station]['min_rtt'] = min_rtt
                            ping.result_json[station]['avg_rtt'] = avg_rtt
                            ping.result_json[station]['max_rtt'] = max_rtt
                            if ping.result_json[station]['os'] == 'Android' and isinstance(rtts, dict) and rtts != {}:
                                if list(rtts[station].keys()) == []:
                                    ping.result_json[station]['sent'] = str(0)
                                    ping.result_json[station]['recv'] = str(0)
                                    ping.result_json[station]['dropped'] = str(0)
                                else:
                                    ping.result_json[station]['sent'] = str(max(list(rtts[station].keys())))
                                    ping.result_json[station]['recv'] = str(len(rtts[station].keys()))
                                    ping.result_json[station]['dropped'] = str(int(ping.result_json[station]['sent']) - int(ping.result_json[station]['recv']))
                            if len(rtts[station].keys()) != 0:
                                required_sequence_numbers = list(range(1, max(rtts[station].keys())))
                                for seq in required_sequence_numbers:
                                    if seq not in rtts[station].keys():
                                        if seq in dropped_packets:
                                            rtts[station][seq] = 0
                                        else:
                                            rtts[station][seq] = 0.11
                                    # print(station, rtts[station])
                            ping.result_json[station]['rtts'] = rtts[station]
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                            # ping.result_json[station]['dropped_packets'] = dropped_packets

        if ping.do_webUI:
            if not ping.store_csv():
                logging.info('Aborted test from webUI')
                break

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

    if args.local_lf_report_dir == "":
        if args.group_name:
            ping.generate_report(config_devices=config_devices, group_device_map=group_device_map)
        else:
            ping.generate_report()
    else:
        if args.group_name:
            ping.generate_report(config_devices=config_devices, group_device_map=group_device_map, report_path=args.local_lf_report_dir)
        else:
            ping.generate_report(report_path=args.local_lf_report_dir)

    if ping.do_webUI:
        # copying to home directory i.e home/user_name
        ping.copy_reports_to_home_dir()
    if ping.do_webUI:
        ping.set_webUI_stop()
    # print('----',rtts)
    # station post cleanup
    if not args.no_cleanup:
        ping.cleanup()


if __name__ == "__main__":
    main()
