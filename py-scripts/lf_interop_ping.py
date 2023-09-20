import argparse
import time
import sys
import os
import pandas as pd
import importlib
import copy
import logging

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
from LANforge import LFUtils

logger = logging.getLogger(__name__)

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
        self.generic_endps_profile.dest = self.target
        self.generic_endps_profile.interval = self.interval

    def cleanup(self):

        if (self.enable_virtual):
            # removing virtual stations if existing
            for station in self.sta_list:
                print('Removing the station {} if exists'.format(station))
                self.generic_endps_profile.created_cx.append(
                    'CX_generic-{}'.format(station.split('.')[2]))
                self.generic_endps_profile.created_endp.append(
                    'generic-{}'.format(station.split('.')[2]))
                self.rm_port(station, check_exists=True)

            if (not LFUtils.wait_until_ports_disappear(base_url=self.host, port_list=self.sta_list, debug=self.debug)):
                print('All stations are not removed or a timeout occured.')
                print('Aborting the test.')
                exit(0)

        if (self.enable_real):
            # removing generic endpoints for real devices if existing
            for station in self.real_sta_list:
                self.generic_endps_profile.created_cx.append(
                    'CX_generic-{}'.format(station))
                self.generic_endps_profile.created_endp.append(
                    'generic-{}'.format(station))

        print('Cleaning up generic endpoints if exists')
        self.generic_endps_profile.cleanup()
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []
        print('Cleanup Successful')

    # Args:
    #   devices: Connected RealDevice object which has already populated tracked real device
    #            resources through call to get_devices()
    def select_real_devices(self, real_devices):
        self.real_sta_list, _, _ = real_devices.query_user()

        # Need real stations to run interop test
        if(len(ping.real_sta_list) == 0):
            logging.error('There are no real devices in this testbed. Aborting test')
            exit(0)

        print(self.real_sta_list)

        for sta_name in self.real_sta_list:
            if sta_name not in real_devices.devices_data:
                logging.error('Real station not in devices data')
                raise ValueError('Real station not in devices data')

            self.real_sta_data_dict[sta_name] = real_devices.devices_data[sta_name]

        # Track number of selected devices
        self.android = Devices.android
        self.windows = Devices.windows
        self.mac     = Devices.mac
        self.linux   = Devices.linux

    def buildstation(self):
        print('Creating Stations {}'.format(self.sta_list))
        for station_index in range(len(self.sta_list)):
            shelf, resource, port = self.sta_list[station_index].split('.')
            print(shelf, resource, port)
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
                print('Virtual client generic endpoint creation completed.')
            else:
                print('Virtual client generic endpoint creation failed.')
                exit(0)

        if (self.enable_real):
            real_sta_os_types = [self.real_sta_data_dict[real_sta_name]['ostype'] for real_sta_name in self.real_sta_data_dict]

            if (self.generic_endps_profile.create(ports=self.real_sta_list, sleep_time=.5, real_client_os_types=real_sta_os_types)):
                print('Real client generic endpoint creation completed.')
            else:
                print('Real client generic endpoint creation failed.')
                exit(0)

    def start_generic(self):
        self.generic_endps_profile.start_cx()

    def stop_generic(self):
        self.generic_endps_profile.stop_cx()

    def get_results(self):
        print(self.generic_endps_profile.created_endp)
        results = self.json_get(
            "/generic/{}".format(','.join(self.generic_endps_profile.created_endp)))
        if (len(self.generic_endps_profile.created_endp) > 1):
            results = results['endpoints']
        else:
            results = results['endpoint']
        return (results)

    def generate_report(self):
        print('Generating Report')

        report = lf_report(_output_pdf='interop_ping.pdf',
                           _output_html='interop_ping.html')
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        print('path: {}'.format(report_path))
        print('path_date_time: {}'.format(report_path_date_time))

        # setting report title
        report.set_title('Ping Test Report')
        report.build_banner()

        # test setup info
        test_setup_info = {
            'SSID': self.ssid,
            'Security': self.security,
            'Website': self.target,
            'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.sta_list), len(self.sta_list) - len(self.real_sta_list), self.android, self.windows, self.linux, self.mac),
            'Duration (in minutes)': self.duration
        }
        report.test_setup_table(
            test_setup_data=test_setup_info, value='Test Setup Information')

        # objective and description
        report.set_obj_html(_obj_title='Objective',
                            _obj='Objective')
        report.build_objective()

        # packets sent vs received vs dropped
        report.set_table_title(
            'Packets sent vs packets received vs packets dropped')
        report.build_table_title()
        # graph for the above
        packets_sent = []
        packets_received = []
        packets_dropped = []
        device_names = []
        device_modes = []
        device_channels = []
        device_min = []
        device_max = []
        device_avg = []
        device_mac = []
        # packet_count_data = {}
        for device, device_data in self.result_json.items():
            packets_sent.append(device_data['sent'])
            packets_received.append(device_data['recv'])
            packets_dropped.append(device_data['dropped'])
            device_names.append(device_data['name'])
            device_modes.append(device_data['mode'])
            device_channels.append(device_data['channel'])
            device_mac.append(device_data['mac'])
            device_min.append(float(device_data['min_rtt']))
            device_max.append(float(device_data['max_rtt']))
            device_avg.append(float(device_data['avg_rtt']))
            print(packets_sent,
                  packets_received,
                  packets_dropped)
            print(device_min,
                  device_max,
                  device_avg)

            # packet_count_data[device] = {
            #     'MAC': device_data['mac'],
            #     'Channel': device_data['channel'],
            #     'Mode': device_data['mode'],
            #     'Packets Sent': device_data['sent'],
            #     'Packets Received': device_data['recv'],
            #     'Packets Loss': device_data['dropped'],
            # }
        x_fig_size = 15
        y_fig_size = len(device_names) * .5 + 4
        graph = lf_bar_graph_horizontal(_data_set=[packets_dropped, packets_received, packets_sent],
                                        _xaxis_name='Packets Count',
                                        _yaxis_name='Wireless Clients',
                                        _label=[
                                            'Packets Loss', 'Packets Received', 'Packets Sent'],
                                        _graph_image_name='Packets sent vs received vs dropped',
                                        _yaxis_label=device_names,
                                        _yaxis_categories=device_names,
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
        print('graph name {}'.format(graph_png))
        report.set_graph_image(graph_png)
        # need to move the graph image to the results directory
        report.move_graph_image()
        report.set_csv_filename(graph_png)
        report.move_csv_file()
        report.build_graph()

        dataframe1 = pd.DataFrame({
            'Wireless Client': device_names,
            'MAC': device_mac,
            'Channel': device_channels,
            'Mode': device_modes,
            'Packets Sent': packets_sent,
            'Packets Received': packets_received,
            'Packets Loss': packets_dropped
        })
        report.set_table_dataframe(dataframe1)
        report.build_table()

        # packets latency graph
        report.set_table_title('Ping Latency Graph')
        report.build_table_title()

        graph = lf_bar_graph_horizontal(_data_set=[device_min, device_avg, device_max],
                                        _xaxis_name='Time (ms)',
                                        _yaxis_name='Wireless Clients',
                                        _label=[
                                            'Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                                        _graph_image_name='Ping Latency per client',
                                        _yaxis_label=device_names,
                                        _yaxis_categories=device_names,
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
        print('graph name {}'.format(graph_png))
        report.set_graph_image(graph_png)
        # need to move the graph image to the results directory
        report.move_graph_image()
        report.set_csv_filename(graph_png)
        report.move_csv_file()
        report.build_graph()

        dataframe2 = pd.DataFrame({
            'Wireless Client': device_names,
            'MAC': device_mac,
            'Channel': device_channels,
            'Mode': device_modes,
            'Min Latency (ms)': device_min,
            'Average Latency (ms)': device_avg,
            'Max Latency (ms)': device_max
        })
        report.set_table_dataframe(dataframe2)
        report.build_table()

        # closing
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='interop_ping.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='',
        description=''
    )
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    # required arguments
    required.add_argument('--mgr',
                          type=str,
                          help='hostname where LANforge GUI is running',
                          required=True)

    optional.add_argument('--ssid',
                          type=str,
                          help='SSID for connecting the stations')

    required.add_argument('--target',
                          type=str,
                          help='Target URL for ping test',
                          required=True)

    # optional arguments
    optional.add_argument('--mgr_port',
                          type=str,
                          default=8080,
                          help='port on which LANforge HTTP service is running'
                          )

    optional.add_argument('--mgr_passwd',
                          type=str,
                          default='lanforge',
                          help='Password to connect to LANforge GUI')

    optional.add_argument('--security',
                          type=str,
                          default='open',
                          help='Security protocol for the specified SSID: <open | wep | wpa | wpa2 | wpa3>')

    optional.add_argument('--passwd',
                          type=str,
                          default='[BLANK]',
                          help='passphrase for the specified SSID')

    required.add_argument('--ping_interval',
                          type=str,
                          help='Interval (in seconds) between the echo requests',
                          required=True)

    required.add_argument('--ping_duration',
                          type=float,
                          help='Duration (in minutes) to run the ping test',
                          required=True)

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

    optional.add_argument('--debug',
                          action="store_true",
                          help='Enable debugging')
    args = parser.parse_args()

    # input sanity
    if(args.virtual is False and args.real is False):
        print('Atleast one of --real or --virtual is required')
        exit(0)
    if (args.virtual is True and args.radio is None):
        print('--radio required')
        exit(0)
    if (args.virtual is True and args.ssid is None):
        print('--ssid required')
        exit(0)
    if (args.security != 'open' and args.passwd == '[BLANK]'):
        print('--passwd required')
        exit(0)

    mgr_ip = args.mgr
    mgr_password = args.mgr_passwd
    mgr_port = args.mgr_port
    ssid = args.ssid
    security = args.security
    password = args.passwd
    num_sta = args.num_sta
    radio = args.radio
    target = args.target
    interval = args.ping_interval
    duration = args.ping_duration
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

    # creating virtual stations if --virtual flag is specified
    if (args.virtual):

        print('Proceeding to create {} virtual stations on {}'.format(num_sta, radio))
        station_list = LFUtils.portNameSeries(
            prefix_='sta', start_id_=0, end_id_=num_sta-1, padding_number_=100000, radio=radio)
        ping.sta_list = station_list
        if (debug):
            print('Virtual Stations: {}'.format(station_list).replace(
                '[', '').replace(']', '').replace('\'', ''))

    # selecting real clients if --real flag is specified
    if (args.real):
        Devices = RealDevice(manager_ip=mgr_ip)
        Devices.get_devices()
        ping.select_real_devices(real_devices=Devices)

    # station precleanup
    ping.cleanup()

    # building station if virtual
    if (args.virtual):
        ping.buildstation()

    # check if generic tab is enabled or not
    if (not ping.check_tab_exists()):
        print('Generic Tab is not available.\nAborting the test.')
        exit(0)

    ping.sta_list += ping.real_sta_list

    # creating generic endpoints
    ping.create_generic_endp()

    print(ping.generic_endps_profile.created_cx)

    # run the test for the given duration
    print('Running the ping test for {} minutes'.format(duration))

    # start generate endpoint
    ping.start_generic()
    time_counter = 0
    ports_data_dict = ping.json_get('/ports/all/')['interfaces']
    ports_data = {}
    for ports in ports_data_dict:
        port, port_data = list(ports.keys())[0], list(ports.values())[0]
        ports_data[port] = port_data

    
    time.sleep(duration * 60)

    print('Stopping the test')
    ping.stop_generic()

    result_data = ping.get_results()
    # print(result_data)
    print(ping.result_json)
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
                        # t_rtt = 0
                        # min_rtt = 10000
                        # max_rtt = 0
                        # for result in result_data['last results'].split('\n'):
                        #     # print(result)
                        #     if(result == ''):
                        #         continue
                        #     rt_time = result.split()[6]
                        #     print(rt_time.split('time='))
                        #     time_value = float(rt_time.split('time=')[1])
                        #     t_rtt += time_value
                        #     if(time_value < min_rtt):
                        #         min_rtt = time_value
                        #     if(max_rtt < time_value):
                        #         max_rtt = time_value
                        # avg_rtt = t_rtt / float(result_data['rx pkts'])
                        # print(t_rtt, min_rtt, max_rtt, avg_rtt)
                        ping.result_json[station] = {
                            'command': result_data['command'],
                            'sent': result_data['tx pkts'],
                            'recv': result_data['rx pkts'],
                            'dropped': result_data['dropped'],
                            'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 else '0'][0],
                            'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 else '0'][0],
                            'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 else '0'][0],
                            'mac': current_device_data['mac'],
                            'channel': current_device_data['channel'],
                            'mode': current_device_data['mode'],
                            'name': station
                        }

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
                            #     if(result == ''):
                            #         continue
                            #     rt_time = result.split()[6]
                            #     time_value = float(rt_time.split('time=')[1])
                            #     t_rtt += time_value
                            #     if(time_value < min_rtt):
                            #         min_rtt = time_value
                            #     if(max_rtt < time_value):
                            #         max_rtt = time_value
                            # avg_rtt = t_rtt / float(ping_data['rx pkts'])
                            # print(t_rtt, min_rtt, max_rtt, avg_rtt)
                            ping.result_json[station] = {
                                'command': ping_data['command'],
                                'sent': ping_data['tx pkts'],
                                'recv': ping_data['rx pkts'],
                                'dropped': ping_data['dropped'],
                                'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 else 0][0],
                                'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 else 0][0],
                                'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 else 0][0],
                                'mac': current_device_data['mac'],
                                'channel': current_device_data['channel'],
                                'mode': current_device_data['mode'],
                                'name': station
                            }


    if (args.real):
        if (type(result_data) == dict):
            for station in ping.real_sta_list:
                current_device_data = Devices.devices_data[station]
                # print(current_device_data)
                if (station in result_data['name']):
                    # print(result_data['last results'].split('\n'))
                    ping.result_json[station] = {
                        'command': result_data['command'],
                        'sent': result_data['tx pkts'],
                        'recv': result_data['rx pkts'],
                        'dropped': result_data['dropped'],
                        'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 else '0'][0],
                        'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 else '0'][0],
                        'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 else '0'][0],
                        'mac': current_device_data['mac'],
                        'channel': current_device_data['channel'],
                        'mode': current_device_data['mode'],
                        'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0]
                    }
        else:
            for station in ping.real_sta_list:
                current_device_data = Devices.devices_data[station]
                for ping_device in result_data:
                    ping_endp, ping_data = list(ping_device.keys())[
                        0], list(ping_device.values())[0]
                    if (station in ping_endp):
                        ping.result_json[station] = {
                            'command': ping_data['command'],
                            'sent': ping_data['tx pkts'],
                            'recv': ping_data['rx pkts'],
                            'dropped': ping_data['dropped'],
                            'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 else 0][0],
                            'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 else 0][0],
                            'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 else 0][0],
                            'mac': current_device_data['mac'],
                            'channel': current_device_data['channel'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0]
                        }

    print(ping.result_json)

    # station post cleanup
    # ping.cleanup()

    ping.generate_report()
