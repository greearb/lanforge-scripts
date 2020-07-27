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

#The valid ways to have multiple TX would be if they were on different ports. 
# I don't think that we need to add that complexity for now.

#In fact, it occurs to me that a multicast TX profile might actually already 
# know the right amount of information from which to generate it's RX endpoints

#So if we create a TX endpoint, it has a multicast ip and port. 
# Those two pieces of information are also useful for creating RXes. 
# I suggest one profile class.


#multicast_profile.createTx(port) and multicast_profile.createRX(port_list)

#the ports have no knowledge of the protocols they will interact with, 
#the ports are layer-1 devices with some layer2 and layer3 features (mac addresses, IP addresses)
#so anything you can legally assign an IP to can take a Layer3 connection or better


class L3VariableTimeLongevity(LFCliBase):
    def __init__(self, host, port, endp_type, is_multicast, side_b, radios, radio_name_list, number_of_stations_per_radio_list,
                 ssid_list, ssid_password_list, security, station_lists, name_prefix, resource=1,
                 side_a_min_rate=56000, side_a_max_rate=0,
                 side_b_min_rate=56000, side_b_max_rate=0,
                 number_template="00", test_duration="256s",
                 _debug_on=True,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.endp_type = endp_type
        self.is_multicast = is_multicast
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
        self.multicast_profile = self.local_realm.new_multicast_profile()
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
        
        if is_multicast:
            self.multicast_profile.host = self.host
            self.cx_profile.host = self.host
            self.cx_profile.port = self.port
            self.cx_profile.name_prefix = self.name_prefix
            self.cx_profile.side_a_min_bps = 0
            self.cx_profile.side_a_max_bps = 0
            self.cx_profile.side_b_min_bps = side_b_min_rate
            self.cx_profile.side_b_max_bps = side_b_max_rate


        else:
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
                    print(item, new_list[item], old_list[item], passes, expected_passes)

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


        temp_station_list = []
        if self.is_multicast:
            for station_list in self.station_lists:     
                for station in range(len(station_list)):
                    temp_station_list.append(str(self.resource) + "." + station_list[station])

                # start recievers
                self.multicast_profile.start_mc_rx(side_a=temp_station_list)

            # right now the multicast is hard coded,  need to pass in station
            self.multicast_profile.start_mc_tx(side_b=self.side_b)
                
        else:
            self.cx_profile.start_cx()

        cur_time = datetime.datetime.now()
        old_rx_values = self.__get_rx_values()
        filtered_old_rx_values = []
        if self.is_multicast:
            for rx_value in old_rx_values:
                for station in self.station_lists:
                    if rx_value in station:
                        filtered_old_rx_values += rx_value
        else:
            filtered_old_rx_values = old_rx_values

        
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time

        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)
            
            new_rx_values = self.__get_rx_values()
            filtered_new_rx_values = []
            if self.is_multicast:
                for rx_value in new_rx_values:
                    for station in self.station_lists:
                        if rx_value in station:
                            filtered_new_rx_values += rx_value
            else:
                filtered_new_rx_values = new_rx_values

            expected_passes += 1
            if self.__compare_vals(filtered_old_rx_values, filtered_new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
                break
            old_rx_values = new_rx_values
            cur_time = datetime.datetime.now()

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        for station_list in self.station_lists:
            for station_name in station_list:
                data = LFUtils.portDownRequest(1, station_name)
                url = "cli-json/set_port"
                self.json_post(url, data)

    def cleanup(self, resource):
        resource = 1
        data = {
                    "name":"BLANK",
                    "action":"overwrite"
        }
        url = "cli-json/load"
        self.json_post(url, data)
        #remove_all_endpoints = True
        #self.local_realm.remove_all_cxs(remove_all_endpoints)
        #self.local_realm.remove_all_stations(resource)
        
                                        
    def build(self):
        # refactor in LFUtils.port_zero_request()
        resource = 1
        data ={
                'shelf':1,
                'resource':1,
                'port':'eth1',
                'ip_addr':'0.0.0.0',
                'netmask':'0.0.0.0',
                'gateway':'0.0.0.0',
                'current_flags':0,
                'interest':402653212
                }

        url = "cli-json/set_port"
        self.json_post(url, data)
    
        # refactor into LFUtils
        data ={
                "shelf":1,
                "resource": resource,
                "port":"br0",
                "network_devs":"eth1",
                "br_flags":1
        }
        url = "cli-json/add_br"
        self.json_post(url, data)

        #refactor later

        try:
            data = LFUtils.port_dhcp_up_request(resource, self.side_b)
            self.json_post("/cli-json/set_port", data)
        except:
            print("LFUtils.port_dhcp_up_request didn't complete ")
            print("or the json_post failed either way {} did not set up dhcp so test may no pass ".format(self.side_b))
        
        #exit(1)

        resource = 1
        index = 0 
        for station_profile in self.station_profiles:
            station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            print("Creating stations")
            #station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            #station_profile.set_command_param("set_port", "report_timer", 1500)
            #station_profile.set_command_flag("set_port", "rpt_timer", 1)
            temp_station_list = []

            index = 0 
            for station_list in self.station_lists: 
                for station in range(len(station_list)):
                    temp_station_list.append(str(self.resource) + "." + station_list[station])
                station_profile.create(resource=1, radio=self.radio_list[index], sta_names_=station_list, debug=True )
                index += 1
            if self.is_multicast:
                self.multicast_profile.create_mc_tx(self.side_b)
                self.multicast_profile.create_mc_rx(side_a=temp_station_list)
            else:
                self.cx_profile.create(endp_type=self.endp_type, side_a=temp_station_list, side_b='1.'+self.side_b, sleep_time=.5)
        self._pass("PASS: Stations build finished")

def valid_endp_type(endp_type):
    valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
    if str(endp_type) in valid_endp_type:
        return endp_type
    else:
        print('invalid endp_type. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6')    
        exit(1)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = argparse.ArgumentParser(
        prog='test_l3_longevity.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will exit when traffic has not changed on a station for 1 minute
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Security is fixed at WPA2
            5. Maximum stations per radio is 64
            ''',
        
        description='''\
test_l3_longevity.py:
--------------------
Basic Idea: create stations, create traffic between upstream port and stations,  run traffic. 
            The traffic on the stations will be checked once per minute to verify that traffic is transmitted
            and recieved.

            Test will exit on failure of not recieving traffice for one minute on any station.

            Scripts are executed from: ./lanforge/py-scripts  

             Stations start counting form zero,  thus stations count from zero - number of las 

Generic command layout:
python .\\test_l3_longevity.py --test_duration <duration> --endp_type <traffic type> --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password>

Note:   multiple --radio switches may be entered up to the number of radios available:
                 --radio <radio 0> <stations> <ssid> <ssid password>  --radio <radio 01> <number of last station> <ssid> <ssid password>

<duration>: number followed by one of the following 
            d - days
            h - hours
            m - minutes
            s - seconds

<traffic type>: 
            lf_udp  : IPv4 UDP traffic
            lf_tcp  : IPv4 TCP traffic
            lf_udp6 : IPv6 UDP traffic
            lf_tcp6 : IPv6 TCP traffic

            mc_udp  : IPv4 multi cast UDP traffic
            mc_udp6 : IPv6 multi cast UDP traffic

        Example:
            1. Test duration 4 minutes
            2. Traffic IPv4 TCP
            3. Upstream-port eth1
            4. Radio #1 wiphy0 has 32 stations, ssid = candelaTech-wpa2-x2048-4-1, ssid password = candelaTech-wpa2-x2048-4-1
            5. Radio #2 wiphy1 has 64 stations, ssid = candelaTech-wpa2-x2048-5-3, ssid password = candelaTech-wpa2-x2048-5-3

            Command: 
            python3 .\\test_l3_longevity.py --test_duration 4m --endp_type lf_tcp --upstream_port eth1 --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 

        ''')

   
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m')
    parser.add_argument('-t', '--endp_type', help='--endp_type <type of traffic> example --endp_type lf_udp, default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6',
                        default='lf_udp',type=valid_endp_type)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')

    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-r','--radio', action='append', nargs=4, metavar=('<wiphyX>', '<number last station>','<ssid>','<ssid password>'),
                         help ='--radio  <number_of_wiphy> <number of last station> <ssid>  <ssid password> ',required=True)
    args = parser.parse_args()

    if args.test_duration:
        test_duration = args.test_duration

    if args.endp_type:
        endp_type = args.endp_type   

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio
    
    is_multicast = False

    radio_offset = 0
    number_of_stations_offset = 1
    ssid_offset = 2
    ssid_password_offset = 3

    MAX_NUMBER_OF_STATIONS = 64
    
    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []

    if endp_type in ['mc_udp','mc_udp6']:
        is_multicast = True

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
            print("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
            quit(1)
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= 1 + index*1000, end_id_= number_of_stations + index*1000, padding_number_=10000)
        station_lists.append(station_list)
        index += 1
    ip_var_test = L3VariableTimeLongevity(lfjson_host, 
                                   lfjson_port, 
                                   number_template="00", 
                                   station_lists= station_lists,
                                   name_prefix="var_time",
                                   endp_type=endp_type,
                                   is_multicast=is_multicast,
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
