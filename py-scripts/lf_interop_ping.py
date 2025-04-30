#!/usr/bin/env python3

'''
    NAME: lf_interop_ping.py

    PURPOSE: lf_interop_ping.py will let the user select real devices, virtual devices or both and then allows them to run
    ping test for user given duration and packet interval on the given target IP or domain name.

    EXAMPLE-1:
    Command Line Interface to run ping test with only virtual clients
    python3 lf_interop_ping.py --mgr 192.168.200.103  --target 192.168.1.3 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --debug

    EXAMPLE-2:
    Command Line Interface to run ping test with only real clients
    python3 lf_interop_ping.py --mgr 192.168.200.103 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --ssid RDT_wpa2 --security wpa2_personal
    --passwd OpenWifi

    EXAMPLE-3:
    Command Line Interface to run ping test with both real and virtual clients
    python3 lf_interop_ping.py --mgr 192.168.200.103 --target 192.168.1.3 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61

    EXAMPLE-4:
    Command Line Interface to run ping test with existing Wi-Fi configuration on the real devices
    python3 lf_interop_ping.py --mgr 192.168.200.63 --real --target 192.168.1.61 --ping_interval 5 --ping_duration 1 --passwd OpenWifi --use_default_config

    EXAMPLE-5:
    Command Line Interface to run ping test by setting device specific Pass/Fail values in the csv file 
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --device_csv_name device.csv
     --use_default_config

    EXAMPLE-6:
    Command Line Interface to run ping test by setting the same expected Pass/Fail value for all devices
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --expected_passfail_value 3
     --use_default_config

    EXAMPLE-7:
    Command Line Interface to run ping test by configuring Real Devices with SSID, Password, and Security
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1  --ssid RDT_wpa2 --security wpa2
    --passwd OpenWifi --server_ip 192.168.244.97 --wait_time 30

    EXAMPLE-8:
    Command Line Interface to run ping test by Configuring Devices in Groups with Specific Profiles
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
     --server_ip 192.168.204.60

    EXAMPLE-9:
    Command Line Interface to run ping test by Configuring Devices in Groups with Specific Profiles with expected Pass/Fail values
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
     --expected_passfail_value 3 --server_ip 192.168.204.60

    EXAMPLE-10:
    Command Line Interface for Configuring Devices in Groups with Specific Profiles with device_csv_name
    python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
     --device_csv_name device.csv --server_ip 192.168.204.60

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
    Working date    - 20/09/2023
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
import traceback
import asyncio
import csv

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

if 'py-scripts' not in sys.path:
    sys.path.append('/home/lanforge/lanforge-scripts/py-scripts')

from lf_base_interop_profile import RealDevice
from lf_graph import lf_bar_graph_horizontal
from lf_report import lf_report
from station_profile import StationProfile
from typing import List, Optional
from LANforge import LFUtils
# Importing DeviceConfig to apply device configurations for ADB devices and laptops
DeviceConfig = importlib.import_module("py-scripts.DeviceConfig")

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
                 debug=False, file_name=None,
                 profile_name=None,
                 group_name=None,
                 eap_method=None,
                 eap_identity=None,
                 ieee80211=None,
                 ieee80211u=None,
                 ieee80211w=None,
                 enable_pkc=None,
                 bss_transition=None,
                 power_save=None,
                 disable_ofdma=None,
                 roam_ft_ds=None,
                 key_management=None,
                 pairwise=None,
                 private_key=None,
                 ca_cert=None,
                 client_cert=None,
                 pk_passwd=None,
                 pac_file=None,
                 server_ip=None,
                 expected_passfail_val=None,
                 csv_name=None,
                 wait_time=60):
        super().__init__(lfclient_host=host,
                         lfclient_port=port)
        self.ssid_list = []
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
        self.generic_endps_profile.dest = self.target
        self.generic_endps_profile.interval = self.interval
        self.Devices = None
        self.eap_method = eap_method
        self.eap_identity = eap_identity
        self.ieee80211 = ieee80211
        self.ieee80211u = ieee80211u
        self.ieee80211w = ieee80211w
        self.enable_pkc = enable_pkc
        self.bss_transition = bss_transition
        self.power_save = power_save
        self.disable_ofdma = disable_ofdma
        self.roam_ft_ds = roam_ft_ds
        self.key_management = key_management
        self.pairwise = pairwise
        self.private_key = private_key
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.pk_passwd = pk_passwd
        self.pac_file = pac_file
        self.profile_name = profile_name
        self.file_name = file_name
        self.group_name = group_name
        self.server_ip = server_ip
        self.real = real
        self.expected_passfail_val = expected_passfail_val
        self.csv_name = csv_name
        self.pass_fail_list = []
        self.test_input_list = []
        self.percent_pac_loss = []
        self.wait_time = wait_time

    def change_target_to_ip(self):

        # checking if target is an IP or a port
        if (self.target.count('.') != 3 and self.target.split('.')[-2].isnumeric()):
            # checking if target is eth1 or 1.1.eth1
            target_port_list = self.name_to_eid(self.target)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get('/port/{}/{}/{}?fields=ip'.format(shelf, resource, port))['interface']['ip']
            except Exception as x:
                traceback.print_exception(Exception, x, x.__traceback__, chain=True)
                logging.error('The target port {} not found on the LANforge. Please change the target.'.format(self.target))
                exit(0)
            self.target = target_port_ip
            print(self.target)
        else:
            print(self.target)

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
    def select_real_devices(self, real_devices, real_sta_list=None, base_interop_obj=None, device_list=None):
        if real_sta_list is None:
            self.real_sta_list, _, _ = real_devices.query_user(device_list=device_list)
        else:
            self.real_sta_list = real_sta_list
        if base_interop_obj is not None:
            self.Devices = base_interop_obj

        # Need real stations to run interop test
        if (len(self.real_sta_list) == 0):
            logger.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        logging.info(self.real_sta_list)

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logger.error('Real station not in devices data, ignoring it from testing')
                continue
                # raise ValueError('Real station not in devices data')

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        # Track number of selected devices
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

    def start_generic(self):
        self.generic_endps_profile.start_cx()

    def stop_generic(self):
        self.generic_endps_profile.stop_cx()

    def get_results(self):
        logging.debug(self.generic_endps_profile.created_endp)
        results = self.json_get(
            "/generic/{}".format(','.join(self.generic_endps_profile.created_endp)))
        if (len(self.generic_endps_profile.created_endp) > 1):
            results = results['endpoints']
        else:
            results = results['endpoint']
        return (results)

    def generate_remarks(self, station_ping_data):
        remarks = []

        # NOTE if there are any more ping failure cases that are missed, add them here.

        # checking if ping output is not empty
        if (station_ping_data['last_result'] == ""):
            remarks.append('No output for ping')

        # illegal division by zero error. Issue with arguments.
        if ('Illegal division by zero' in station_ping_data['last_result']):
            remarks.append('Illegal division by zero error. Please re-check the arguments passed.')

        # unknown host
        if ('Totals:  *** dropped: 0  received: 0  failed: 0  bytes: 0' in station_ping_data['last_result'] or 'unknown host' in station_ping_data['last_result']):
            remarks.append('Unknown host. Please re-check the target')

        # checking if IP is existing in the ping command or not for Windows device
        if (station_ping_data['os'] == 'Windows'):
            if ('None' in station_ping_data['command'] or station_ping_data['command'].split('-n')[0].split('-S')[-1] == "  "):
                remarks.append('Station has no IP')

        # network buffer overflow
        if ('ping: sendmsg: No buffer space available' in station_ping_data['last_result']):
            remarks.append('Network buffer overlow')

        # checking for no ping states
        if (float(station_ping_data['min_rtt']) == 0 and float(station_ping_data['max_rtt']) == 0 and float(station_ping_data['avg_rtt']) == 0):

            # Destination Host Unreachable state
            if ('Destination Host Unreachable' in station_ping_data['last_result']):
                remarks.append('Destination Host Unrechable')

            # Name or service not known state
            if ('Name or service not known' in station_ping_data['last_result']):
                remarks.append('Name or service not known')

            # network buffer overflow
            if ('ping: sendmsg: No buffer space available' in station_ping_data['last_result']):
                remarks.append('Network buffer overlow')

        return (remarks)

    # Converts an upstream port name to its corresponding IP address if it's not already in IP format.
    def change_port_to_ip(self, upstream_port):
        if upstream_port.count('.') != 3:
            target_port_list = self.name_to_eid(upstream_port)
            shelf, resource, port, _ = target_port_list
            try:
                target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                upstream_port = target_port_ip
            except BaseException:
                logging.warning(f'The upstream port is not an ethernet port. Proceeding with the given upstream_port {upstream_port}.')
            logging.info(f"Upstream port IP {upstream_port}")
        else:
            logging.info(f"Upstream port IP {upstream_port}")
        return upstream_port

    # Calculates pass/fail status for each client based on their result compared to the expected value.
    def get_pass_fail_list(self, os_type):
        # When csv_name is provided, for pass/fail criteria, respective values for each client will be used
        if not self.expected_passfail_val:
            res_list = []
            test_input_list = []
            pass_fail_list = []
            interop_tab_data = self.json_get('/adb/')["devices"]
            for client in range(len(os_type)):
                if os_type[client] != 'Android':
                    # Example: From "DESKTOP-DDPI3HE Windows", extract "DESKTOP-DDPI3HE"
                    res_list.append(self.device_names[client].split(' ')[0:-1][0])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            if item['user-name'] == self.device_names[client].split(' ')[0:-1][0]:
                                res_list.append(item['name'].split('.')[2])
            with open(self.csv_name, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                # fieldnames = reader.fieldnames
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
            self.percent_pac_loss = []
            for i in range(len(self.packets_sent)):
                if self.packets_sent[i] != 0:
                    self.percent_pac_loss.append(((self.packets_sent[i] - self.packets_received[i]) / self.packets_sent[i]) * 100)
                else:
                    self.percent_pac_loss.append(0)
            for i in range(len(test_input_list)):
                if self.packets_sent[i] == 0:
                    pass_fail_list.append('FAIL')
                elif float(test_input_list[i]) >= self.percent_pac_loss[i]:
                    pass_fail_list.append('PASS')
                else:
                    pass_fail_list.append('FAIL')
            self.pass_fail_list = pass_fail_list
            self.test_input_list = test_input_list
        # When expected_passfail_val is provided, for pass/fail criteria, the same value will be used for all clients
        else:
            self.test_input_list = [self.expected_passfail_val for val in range(len(self.device_names))]
            self.percent_pac_loss = []
            for i in range(len(self.packets_sent)):
                if self.packets_sent[i] != 0:
                    self.percent_pac_loss.append(((self.packets_sent[i] - self.packets_received[i]) / self.packets_sent[i]) * 100)
                else:
                    self.percent_pac_loss.append(0)
            pass_fail_list = []
            for i in range(len(self.test_input_list)):
                if self.packets_sent[i] == 0:
                    pass_fail_list.append('FAIL')
                elif float(self.expected_passfail_val) >= self.percent_pac_loss[i]:
                    pass_fail_list.append("PASS")
                else:
                    pass_fail_list.append("FAIL")
            self.pass_fail_list = pass_fail_list

    def generate_report(self, result_json=None, result_dir='Ping_Test_Report', report_path='', config_devices='', group_device_map={}):
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
        report.set_title('Ping Test Report')
        report.build_banner()

        # Test setup information table for devices in device list
        if config_devices == '':
            test_setup_info = {
                'SSID': self.ssid,
                'Security': self.security,
                'Website / IP': self.target,
                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.sta_list), len(self.sta_list) - len(self.real_sta_list), self.android, self.windows, self.linux, self.mac),
                'Duration (in minutes)': self.duration
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
        self.device_ssid = []
        # packet_count_data = {}
        os_type = []
        for device, device_data in self.result_json.items():
            logging.info('Device data: {} {}'.format(device, device_data))
            os_type.append(device_data['os'])
            self.packets_sent.append(int(device_data['sent']))
            self.packets_received.append(int(device_data['recv']))
            self.packets_dropped.append(int(device_data['dropped']))
            self.device_names.append(device_data['name'] + ' ' + device_data['os'])
            self.device_modes.append(device_data['mode'])
            self.device_channels.append(device_data['channel'])
            self.device_mac.append(device_data['mac'])
            self.device_ssid.append(device_data['ssid'])
            self.device_min.append(float(device_data['min_rtt'].replace(',', '')))
            self.device_max.append(float(device_data['max_rtt'].replace(',', '')))
            self.device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
            if (device_data['os'] == 'Virtual'):
                self.report_names.append('{} {}'.format(device, device_data['os'])[0:25])
            else:
                self.report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name']))
            if (device_data['remarks'] != []):
                self.device_names_with_errors.append(device_data['name'])
                self.devices_with_errors.append(device)
                self.remarks.append(','.join(device_data['remarks']))
            # logging.info(self.packets_sent,
            #       self.packets_received,
            #       self.packets_dropped)
            # logging.info(self.device_min,
            #       self.device_max,
            #       self.device_avg)

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

        if self.real:
            # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
            if self.expected_passfail_val or self.csv_name:
                self.get_pass_fail_list(os_type)
            # When groups are provided a seperate table will be generated for each group using generate_dataframe
            if self.group_name:
                for key, val in group_device_map.items():
                    if self.expected_passfail_val or self.csv_name:
                        dataframe = self.generate_dataframe(
                            val,
                            self.device_names,
                            self.device_mac,
                            self.device_channels,
                            self.device_ssid,
                            self.device_modes,
                            self.packets_sent,
                            self.packets_received,
                            self.packets_dropped,
                            self.percent_pac_loss,
                            self.test_input_list,
                            self.pass_fail_list)
                    else:
                        dataframe = self.generate_dataframe(val, self.device_names, self.device_mac, self.device_channels, self.device_ssid,
                                                            self.device_modes, self.packets_sent, self.packets_received, self.packets_dropped, [], [], [])
                    if dataframe:
                        report.set_obj_html("", "Group: {}".format(key))
                        report.build_objective()
                        dataframe1 = pd.DataFrame(dataframe)
                        report.set_table_dataframe(dataframe1)
                        report.build_table()

            else:
                dataframe1 = pd.DataFrame({
                    'Wireless Client': self.device_names,
                    'MAC': self.device_mac,
                    'Channel': self.device_channels,
                    'SSID ': self.device_ssid,
                    'Mode': self.device_modes,
                    'Packets Sent': self.packets_sent,
                    'Packets Received': self.packets_received,
                    'Packets Loss': self.packets_dropped,
                })
                if self.expected_passfail_val or self.csv_name:
                    dataframe1[" Percentage of Packet loss %"] = self.percent_pac_loss
                    dataframe1['Expected Packet loss %'] = self.test_input_list
                    dataframe1['Status'] = self.pass_fail_list
                report.set_table_dataframe(dataframe1)
                report.build_table()
        else:
            dataframe1 = pd.DataFrame({
                'Wireless Client': self.device_names,
                'MAC': self.device_mac,
                'Channel': self.device_channels,
                'SSID ': self.device_ssid,
                'Mode': self.device_modes,
                'Packets Sent': self.packets_sent,
                'Packets Received': self.packets_received,
                'Packets Loss': self.packets_dropped,
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
            'SSID ': self.device_ssid,
            'Mode': self.device_modes,
            'Min Latency (ms)': self.device_min,
            'Average Latency (ms)': self.device_avg,
            'Max Latency (ms)': self.device_max
        })
        report.set_table_dataframe(dataframe2)
        report.build_table()

        # check if there are remarks for any device. If there are remarks, build table else don't
        if (self.remarks != []):
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

    def generate_dataframe(self,groupdevlist: List[str],device_names: List[str],device_mac: List[str],device_channels: List[str],device_ssid: List[str],device_modes: List[str],packets_sent: List[int],packets_received: List[int],packets_dropped: List[int],percent_pac_loss: List[float],test_input_list: List[str],pass_fail_list: List[str]) -> Optional[pd.DataFrame]:
        """
        Creates a separate DataFrame for each group of devices.

        Returns:
            DataFrame: A DataFrame for each device group.
            Returns None if neither device in a group is configured.
        """
        dev_names = []
        dev_mac = []
        dev_channels = []
        dev_ssid = []
        dev_modes = []
        pack_sent = []
        pack_received = []
        pac_dropped = []
        pac_loss = []
        input_list = []
        pass_fail = []
        interop_tab_data = self.json_get('/adb/')["devices"]
        for i in range(len(device_names)):
            for j in groupdevlist:
                # For a string like "1.360 Lin test3":
                # - device_names[i].split(" ")[0:-1][0] gives 'test3' (device name)
                # - device_names[i].split(" ")[-1] gives 'Lin' (OS type)
                # This condition filters out Android clients and matches device name with j
                if j == device_names[i].split(" ")[0:-1][0] and device_names[i].split(" ")[-1] != 'Android':
                    dev_names.append(device_names[i])
                    dev_mac.append(device_mac[i])
                    dev_channels.append(device_channels[i])
                    dev_ssid.append(device_ssid[i])
                    dev_modes.append(device_modes[i])
                    pack_sent.append(packets_sent[i])
                    pack_received.append(packets_received[i])
                    pac_dropped.append(packets_dropped[i])
                    if self.expected_passfail_val or self.csv_name:
                        pac_loss.append(percent_pac_loss[i])
                        input_list.append(test_input_list[i])
                        pass_fail.append(pass_fail_list[i])
                else:
                    for dev in interop_tab_data:
                        for item in dev.values():
                            # For a string like 1.15 android samsungmob:
                            # - device_names[i].split(' ')[0:-1][0] (e.g., 'samsungmob') matches item['user-name']
                            # - The group name (e.g., 'RZCTA09CTXF') matches with item['name'].split('.')[-1]
                            if item['user-name'] == device_names[i].split(' ')[0:-1][0] and j == item['name'].split('.')[-1]:
                                dev_names.append(device_names[i])
                                dev_mac.append(device_mac[i])
                                dev_channels.append(device_channels[i])
                                dev_ssid.append(device_ssid[i])
                                dev_modes.append(device_modes[i])
                                pack_sent.append(packets_sent[i])
                                pack_received.append(packets_received[i])
                                pac_dropped.append(packets_dropped[i])
                                if self.expected_passfail_val or self.csv_name:
                                    pac_loss.append(percent_pac_loss[i])
                                    input_list.append(test_input_list[i])
                                    pass_fail.append(pass_fail_list[i])
        if len(dev_names) != 0:
            dataframe = {
                'Wireless Client': dev_names,
                'MAC': dev_mac,
                'Channel': dev_channels,
                'SSID ': dev_ssid,
                'Mode': dev_modes,
                'Packets Sent': pack_sent,
                'Packets Received': pack_received,
                'Packets Loss': pac_dropped,
            }
            if self.expected_passfail_val or self.csv_name:
                dataframe[' Percentage of Packet loss %'] = pac_loss
                dataframe['Expected Packet loss %'] = input_list
                dataframe['Status '] = pass_fail
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
    if args.ssid and args.passwd and args.group_name and args.profile_name:
        logger.error('either --ssid,--password,--security or --profile_name,--group_name should be given')
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
        if args.group_name and (args.file_name is None or args.profile_name is None):
            logger.error("Please provide file name and profile name for group configuration")
            exit(1)
        elif args.file_name and (args.group_name is None or args.profile_name is None):
            logger.error("Please provide group name and profile name for file configuration")
            exit(1)
        elif args.profile_name and (args.group_name is None or args.file_name is None):
            logger.error("Please provide group name and file name for profile configuration")
            exit(1)
    # Get group and profile values from arguments and convert comma-separated strings into lists
    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []  # Default to empty list if group name is not provided
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []  # Default to empty list if profile name is not provided
    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)
    if args.device_csv_name and args.expected_passfail_value:
        logger.error("Enter either --device_csv_name or --expected_passfail_value")
        exit(1)


def main():

    help_summary = '''\
The Candela Tech ping test is to evaluate network connectivity and measure the round-trip time taken for
data packets to travel from the source to the destination and back. It helps assess the reliability and latency of the network,
identifying any packet loss, delays, or variations in response times. The test aims to ensure that devices can communicate
effectively over the network and pinpoint potential issues affecting connectivity.
    '''

    parser = argparse.ArgumentParser(
        prog='interop_ping.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
            Allows user to run the ping test on a target IP or port for the given duration and packet interval
            with either selected number of virtual stations or provides the list of available real devices
            and allows the user to select the real devices and run ping test on them.
        ''',
        description='''
        NAME: lf_interop_ping.py

        PURPOSE: lf_interop_ping.py will let the user select real devices, virtual devices or both and then allows them to run
        ping test for user given duration and packet interval on the given target IP or domain name.

        EXAMPLE-1:
        Command Line Interface to run ping test with only virtual clients
        python3 lf_interop_ping.py --mgr 192.168.200.103  --target 192.168.1.3 --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --debug

        EXAMPLE-2:
        Command Line Interface to run ping test with only real clients
        python3 lf_interop_ping.py --mgr 192.168.200.103 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61 --ssid RDT_wpa2
        --security wpa2_personal --passwd OpenWifi

        EXAMPLE-3:
        Command Line Interface to run ping test with both real and virtual clients
        python3 lf_interop_ping.py --mgr 192.168.200.103 --target 192.168.1.3 --real --virtual --num_sta 1 --radio 1.1.wiphy2 --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --ping_interval 1 --ping_duration 1 --server_ip 192.168.1.61

        EXAMPLE-4:
        Command Line Interface to run ping test with existing Wi-Fi configuration on the real devices
        python3 lf_interop_ping.py --mgr 192.168.200.63 --real --target 192.168.1.61 --ping_interval 5 --ping_duration 1 --passwd OpenWifi --use_default_config

        EXAMPLE-5:
        Command Line Interface to run ping test by setting device specific Pass/Fail values in the csv file 
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --device_csv_name device.csv
        --use_default_config

        EXAMPLE-6:
        Command Line Interface to run ping test by setting the same expected Pass/Fail value for all devices
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1 --expected_passfail_value 3
        --use_default_config

        EXAMPLE-7:
        Command Line Interface to run ping test by configuring Real Devices with SSID, Password, and Security
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1  --ssid RDT_wpa2 --security wpa2
        --passwd OpenWifi --server_ip 192.168.244.97 --wait_time 30

        EXAMPLE-8:
        Command Line Interface to run ping test by Configuring Devices in Groups with Specific Profiles
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
        --server_ip 192.168.204.60

        EXAMPLE-9:
        Command Line Interface to run ping test by Configuring Devices in Groups with Specific Profiles with expected Pass/Fail values
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
        --expected_passfail_value 3 --server_ip 192.168.204.60

        EXAMPLE-10:
        Command Line Interface for Configuring Devices in Groups with Specific Profiles with device_csv_name
        python3 lf_interop_ping.py --mgr 192.168.244.97 --real --target 192.168.1.3 --ping_interval 1 --ping_duration 1   --group_name grp3 --file_name g219 --profile_name Open5
        --device_csv_name device.csv --server_ip 192.168.204.60

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
        Working date    - 20/09/2023
        Build version   - 5.4.7
        kernel version  - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.
        '''
    )
    # required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    # optional arguments
    optional.add_argument('--mgr',
                          type=str,
                          help='hostname where LANforge GUI is running',
                          default='localhost')

    optional.add_argument('--target',
                          type=str,
                          help='Target URL or port for ping test',
                          default='1.1.eth1')

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
    parser.add_argument('--wait_time', type=int, help="Enter the maximum wait time for configurations to apply", default=60)

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
    validate_args(args)

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
    group_name = args.group_name
    file_name = args.file_name
    profile_name = args.profile_name
    eap_method = args.eap_method
    eap_identity = args.eap_identity
    ieee80211 = args.ieee8021x
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
                lanforge_password=mgr_password, target=target, interval=interval, sta_list=[], virtual=args.virtual, real=args.real, duration=duration, debug=debug, csv_name=args.device_csv_name,
                expected_passfail_val=args.expected_passfail_value, wait_time=args.wait_time, group_name=group_name)

    # changing the target from port to IP
    ping.change_target_to_ip()

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
        Devices = RealDevice(manager_ip=mgr_ip, selected_bands=[])
        Devices.get_devices()
        ping.Devices = Devices
        # ping.select_real_devices(real_devices=Devices)
        # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
        if (configure):
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
                Devices.get_devices()
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
                    'ieee80211': ieee80211,
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
                for device in all_devices:
                    if device["type"] == 'laptop':
                        device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                    else:
                        device_list.append(device["eid"] + " " + device["serial"])
                logger.info(f"Available devices: {device_list}")
                dev_list = input("Enter the desired resources to run the test:").split(',')
                dev_list = asyncio.run(obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                Devices.get_devices()
                ping.select_real_devices(real_devices=Devices, device_list=dev_list)
        # Case 3: Config is False, no device list is provided, and no group is selected
        # Prompt the user to manually input devices for running the test
        else:
            device_list = ping.Devices.get_devices()
            logger.info(f"Available devices: {device_list}")
            dev_list = input("Enter the desired resources to run the test:").split(',')
            ping.select_real_devices(real_devices=Devices, device_list=dev_list)

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

    logging.info(ping.generic_endps_profile.created_cx)

    # run the test for the given duration
    logging.info('Running the ping test for {} minutes'.format(duration))

    # start generate endpoint
    ping.start_generic()
    # time_counter = 0
    ports_data_dict = ping.json_get('/ports/all/')['interfaces']
    ports_data = {}
    for ports in ports_data_dict:
        port, port_data = list(ports.keys())[0], list(ports.values())[0]
        ports_data[port] = port_data

    time.sleep(duration * 60)

    logging.info('Stopping the test')
    ping.stop_generic()

    result_data = ping.get_results()
    # logging.info(result_data)
    logging.info(ping.result_json)
    if (args.virtual):
        ports_data_dict = ping.json_get('/ports/all/')['interfaces']
        ports_data = {}
        for ports in ports_data_dict:
            port, port_data = list(ports.keys())[0], list(ports.values())[0]
            ports_data[port] = port_data
        if (isinstance(result_data, dict)):
            for station in ping.sta_list:
                if (station not in ping.real_sta_list):
                    current_device_data = ports_data[station]
                    if (station.split('.')[2] in result_data['name']):
                        # t_rtt = 0
                        # min_rtt = 10000
                        # max_rtt = 0
                        # for result in result_data['last results'].split('\n'):
                        #     # logging.info(result)
                        #     if (result == ''):
                        #         continue
                        #     rt_time = result.split()[6]
                        #     logging.info(rt_time.split('time='))
                        #     time_value = float(rt_time.split('time=')[1])
                        #     t_rtt += time_value
                        #     if (time_value < min_rtt):
                        #         min_rtt = time_value
                        #     if (max_rtt < time_value):
                        #         max_rtt = time_value
                        # avg_rtt = t_rtt / float(result_data['rx pkts'])
                        # logging.info(t_rtt, min_rtt, max_rtt, avg_rtt)
                        try:
                            ping.result_json[station] = {
                                'command': result_data['command'],
                                'sent': result_data['tx pkts'],
                                'recv': result_data['rx pkts'],
                                'dropped': result_data['dropped'],
                                'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'mac': current_device_data['mac'],
                                'channel': current_device_data['channel'],
                                'ssid': current_device_data['ssid'],
                                'mode': current_device_data['mode'],
                                'name': station,
                                'os': 'Virtual',
                                'remarks': [],
                                'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                            }
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                        except BaseException:
                            logging.error('Failed parsing the result for the station {}'.format(station))

        else:
            for station in ping.sta_list:
                if (station not in ping.real_sta_list):
                    current_device_data = ports_data[station]
                    for ping_device in result_data:
                        ping_endp, ping_data = list(ping_device.keys())[
                            0], list(ping_device.values())[0]
                        if (station.split('.')[2] in ping_endp):
                            # t_rtt = 0
                            # min_rtt = 10000
                            # max_rtt = 0
                            # for result in ping_data['last results'].split('\n'):
                            #     if (result == ''):
                            #         continue
                            #     rt_time = result.split()[6]
                            #     time_value = float(rt_time.split('time=')[1])
                            #     t_rtt += time_value
                            #     if (time_value < min_rtt):
                            #         min_rtt = time_value
                            #     if (max_rtt < time_value):
                            #         max_rtt = time_value
                            # avg_rtt = t_rtt / float(ping_data['rx pkts'])
                            # logging.info(t_rtt, min_rtt, max_rtt, avg_rtt)
                            try:
                                ping.result_json[station] = {
                                    'command': ping_data['command'],
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                    'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                    'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                    'mac': current_device_data['mac'],
                                    'ssid': current_device_data['ssid'],
                                    'channel': current_device_data['channel'],
                                    'mode': current_device_data['mode'],
                                    'name': station,
                                    'os': 'Virtual',
                                    'remarks': [],
                                    'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                }
                                ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                            except BaseException:
                                logging.error('Failed parsing the result for the station {}'.format(station))

    if (args.real):
        if (isinstance(result_data, dict)):
            for station in ping.real_sta_list:
                current_device_data = Devices.devices_data[station]
                # logging.info(current_device_data)
                if (station in result_data['name']):
                    try:
                        # logging.info(result_data['last results'].split('\n'))
                        ping.result_json[station] = {
                            'command': result_data['command'],
                            'sent': result_data['tx pkts'],
                            'recv': result_data['rx pkts'],
                            'dropped': result_data['dropped'],
                            'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                            'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                            'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                            'mac': current_device_data['mac'],
                            'ssid': current_device_data['ssid'],
                            'channel': current_device_data['channel'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                            'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0], # noqa E501
                            'remarks': [],
                            'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                        }
                        ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                    except BaseException:
                        logging.error('Failed parsing the result for the station {}'.format(station))
        else:
            for station in ping.real_sta_list:
                current_device_data = Devices.devices_data[station]
                for ping_device in result_data:
                    ping_endp, ping_data = list(ping_device.keys())[
                        0], list(ping_device.values())[0]
                    if (station in ping_endp):
                        try:
                            ping.result_json[station] = {
                                'command': ping_data['command'],
                                'sent': ping_data['tx pkts'],
                                'recv': ping_data['rx pkts'],
                                'dropped': ping_data['dropped'],
                                'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0], # noqa E501
                                'mac': current_device_data['mac'],
                                'ssid': current_device_data['ssid'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0], # noqa E501
                                'remarks': [],
                                'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                            }
                            ping.result_json[station]['remarks'] = ping.generate_remarks(ping.result_json[station])
                        except BaseException:
                            logging.error('Failed parsing the result for the station {}'.format(station))

    logging.info(ping.result_json)

    # station post cleanup
    ping.cleanup()

    if args.local_lf_report_dir == "":
        # Report generation when groups are specified but no custom report path is provided
        if args.group_name:
            ping.generate_report(config_devices=config_devices, group_device_map=group_device_map)
        # Report generation when no group is specified and no custom report path is provided
        else:
            ping.generate_report()
    else:
        # Report generation when groups are specified and a custom report path is provided
        if args.group_name:
            ping.generate_report(config_devices=config_devices, group_device_map=group_device_map, report_path=args.local_lf_report_dir)
        # Report generation when no group is specified but a custom report path is provided
        else:
            ping.generate_report(report_path=args.local_lf_report_dir)


if __name__ == "__main__":
    main()
