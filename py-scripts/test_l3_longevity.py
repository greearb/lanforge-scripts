#!/usr/bin/env python3

import sys
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
import time
import datetime

class L3VariableTimeLongevity(LFCliBase):
    def __init__(self, host, port, endp_type, side_b, radios, radio_name_list, number_of_stations_per_radio_list,
                 ssid_list, ssid_password_list, security, station_lists, name_prefix, resource=1,
                 side_a_min_rate=56, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00", test_duration="256s",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.endp_type = endp_type
        self.side_b = side_b
        self.ssid_list = ssid_list
        self.ssid_password_list = ssid_password_list
        self.station_lists = station_lists       
        self.security = security
        self.number_template = number_template
        self.resource = resource
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.cx_stations_lists = station_lists
        self.radios = radios # from the command line
        self.radio_list = radio_name_list
        self.number_of_stations_per_radio_list =  number_of_stations_per_radio_list
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.station_profiles = []
       
        index = 0
        for radio in radios:
            self.station_profile = self.local_realm.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_list[index]
            self.station_profile.ssid_pass = ssid_password_list[index]
            self.station_profile.security = self.security
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = 0
            self.station_profiles.append(self.station_profile)
            index += 1
        
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def __get_rx_values(self):
        cx_list = self.json_get("endp?fields=name,rx+bytes", debug_=True)
        cx_rx_map = {}
        for cx_name in cx_list['endpoint']:
            if cx_name != 'uri' and cx_name != 'handler':
                for item, value in cx_name.items():
                    for value_name, value_rx in value.items():
                      if value_name == 'rx bytes':
                        cx_rx_map[item] = value_rx
        return cx_rx_map

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes += 1
                if new_list[item] > old_list[item]:
                    passes += 1
            if passes == expected_passes:
                return True
            else:
                return False
        else:
            return False

    def start(self, print_pass=False, print_fail=False):
        print("Bringing up stations")
        for station_profile in self.station_profiles:
            print("Bringing up station {}".format(station_profile))
            station_profile.admin_up(self.resource)

        temp_stations_list = []
        for station_list in self.station_lists:     
            temp_station_list = station_list.copy()
            temp_stations_list.append(temp_station_list)
            temp_stations_list.append(self.side_b)
            self.local_realm.wait_for_ip(self.resource, temp_station_list)

        cur_time = datetime.datetime.now()
        old_cx_rx_values = self.__get_rx_values()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.cx_profile.start_cx()
        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_cx_rx_values = self.__get_rx_values()
            expected_passes += 1
            if self.__compare_vals(old_cx_rx_values, new_cx_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
                break
            old_cx_rx_values = new_cx_rx_values
            cur_time = datetime.datetime.now()

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        for station_list in self.station_lists:
            for station_name in station_list:
                data = LFUtils.portDownRequest(1, station_name)
                url = "json-cli/set_port"
                self.json_post(url, data)

    def cleanup(self, resource):
        resource = 1
        remove_all_endpoints = True
        self.local_realm.remove_all_cxs(remove_all_endpoints)
        self.local_realm.remove_all_stations(resource)
                                        
    def build(self):
        resource = 1
        try:
            data = LFUtils.port_dhcp_up_request(resource, self.side_b)
            self.json_post("/cli-json/set_port", data)
        except:
            print("LFUtils.port_dhcp_up_request didn't complete ")
            print("or the json_post failed either way {} did not set up dhcp so test may no pass ".format(self.side_b))
        
        resource = 1
        index = 0 
        for station_profile in self.station_profiles:
            station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            print("Creating stations")
            station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            station_profile.set_command_param("set_port", "report_timer", 1500)
            station_profile.set_command_flag("set_port", "rpt_timer", 1)
            temp_station_list = []

            index = 0 
            for station_list in self.station_lists: 
                for station in range(len(station_list)):
                    temp_station_list.append(str(self.resource) + "." + station_list[station])
                station_profile.create(resource=1, radio=self.radio_list[index], sta_names_=station_list, debug=False )
                index += 1
            self.cx_profile.create(endp_type=self.endp_type, side_a=temp_station_list, side_b='1.'+self.side_b, sleep_time=.5)
        self._pass("PASS: Stations build finished")

def valid_endp_type(endp_type):
    valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6']
    if str(endp_type) in valid_endp_type:
        return endp_type
    else:
        print('invalid endp_type. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6')    
        exit(1)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = argparse.ArgumentParser(
        description='L3 longevity script for multiple stations on multiple radios  sample command (note remove carriage returns if copy from help): python3 .\\test_l3_longevity.py --test_duration 125s --endp_type lf_tcp --side_b eth1 --radio wiphy0 2 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 --radio wiphy1 3 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 ',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m')
    parser.add_argument('-t', '--endp_type', help='--endp_type <type of traffic> example --endp_type lf_udp, default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6',
                        default='lf_udp',type=valid_endp_type)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
    parser.add_argument('-r','--radio', action='append', nargs=4, metavar=('<wiphyX>', '<number of stations>','<ssid>','<ssid password>'),
                         help ='--radio  <number_of_wiphy> <number_of_stations> <ssid>  <ssid password> ',required=True)
    args = parser.parse_args()

    if args.test_duration:
        test_duration = args.test_duration

    if args.endp_type:
        endp_type = args.endp_type   

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio
    
    radio_offset = 0
    number_of_stations_offset = 1
    ssid_offset = 2
    ssid_password_offset = 3

    MAX_NUMBER_OF_STATIONS = 64
    
    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []

    index = 0
    for radio in radios:
        radio_name = radio[radio_offset]
        radio_name_list.append(radio_name)
        number_of_stations_per_radio = radio[number_of_stations_offset]
        number_of_stations_per_radio_list.append(number_of_stations_per_radio)
        ssid = radio[ssid_offset]
        ssid_list.append(ssid)
        ssid_password = radio[ssid_password_offset]
        ssid_password_list.append(ssid_password)
        index += 1

    index = 0
    station_lists = []
    for radio in radios:
        number_of_stations = int(number_of_stations_per_radio_list[index])
        if number_of_stations > MAX_NUMBER_OF_STATIONS:
            print("number of stations per radio exceeded")
            quit(1)
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= index*1000, end_id_= number_of_stations + index*1000, padding_number_=10000)
        station_lists.append(station_list)
        index += 1
    ip_var_test = L3VariableTimeLongevity(lfjson_host, 
                                   lfjson_port, 
                                   number_template="00", 
                                   station_lists= station_lists,
                                   name_prefix="var_time",
                                   endp_type=endp_type,
                                   side_b=side_b,
                                   radios=radios,
                                   radio_name_list=radio_name_list,
                                   number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                   ssid_list=ssid_list,
                                   ssid_password_list=ssid_password_list,
                                   resource=1,
                                   security="wpa2", test_duration=test_duration,
                                   side_a_min_rate=256000, side_b_min_rate=256000)

    ip_var_test.cleanup(station_list)
    ip_var_test.build()
    if not ip_var_test.passes():
        print(ip_var_test.get_fail_message())
        exit(1) 
    ip_var_test.start(False, False)
    ip_var_test.stop()
    if not ip_var_test.passes():
        print(ip_var_test.get_fail_message())
        exit(1) 
    time.sleep(30)
    ip_var_test.cleanup(station_list)
    if ip_var_test.passes():
        print("Full test passed, all connections increased rx bytes")


if __name__ == "__main__":
    main()
