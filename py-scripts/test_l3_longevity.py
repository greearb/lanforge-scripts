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
    def __init__(self, host, port, endp_types, tos, side_b, radios, radio_name_list, number_of_stations_per_radio_list,
                 ssid_list, ssid_password_list, ssid_security_list, station_lists, name_prefix, debug_on,
                 side_a_min_rate=56000, side_a_max_rate=0,
                 side_b_min_rate=56000, side_b_max_rate=0,
                 number_template="00", test_duration="256s",
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.tos = tos.split()
        self.endp_types = endp_types.split()
        self.side_b = side_b
        self.ssid_list = ssid_list
        self.ssid_password_list = ssid_password_list
        self.station_lists = station_lists       
        self.ssid_security_list = ssid_security_list
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.radios = radios # from the command line
        self.radio_list = radio_name_list
        self.number_of_stations_per_radio_list =  number_of_stations_per_radio_list
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.multicast_profile = self.local_realm.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-";
        self.station_profiles = []
        
        index = 0
        for radio in radios:
            self.station_profile = self.local_realm.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_list[index]
            self.station_profile.ssid_pass = ssid_password_list[index]
            self.station_profile.security = ssid_security_list[index]
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = 0
            self.station_profiles.append(self.station_profile)
            index += 1
        
        self.multicast_profile.host = self.host
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def __get_rx_values(self):
        endp_list = self.json_get("endp?fields=name,rx+bytes", debug_=True)
        endp_rx_map = {}
        our_endps = {}
        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e;
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e;
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, value in endp_name.items():
                    if item in our_endps:
                        for value_name, value_rx in value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value_rx
        return endp_rx_map

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes +=1
                if item.startswith("mtx"):
                    # We ignore the mcast transmitter.
                    # This is a hack based on naming and could be improved.
                    passes += 1
                else:
                    if new_list[item] > old_list[item]:
                        passes += 1
                        print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                    else:
                        print("Failed to increase rx data: ", item, new_list[item], old_list[item])

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            print("Old-list length: %i  new: %i does not match in compare-vals."%(len(old_list), len(new_list)))
            print("old-list:",old_list)
            print("new-list:",old_list)
            return False

    def start(self, print_pass=False, print_fail=False):
        print("Bringing up stations")
        up_request = self.local_realm.admin_up(self.side_b)
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                print("Bringing up station %s"%(sta))
                up_request = self.local_realm.admin_up(sta)

        temp_stations_list = []
        temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())

        if self.local_realm.wait_for_ip(temp_stations_list, timeout_sec=120):
            print("ip's acquired")
        else:
            print("print failed to get IP's")

        print("Starting multicast traffic (if any configured)")
        self.multicast_profile.start_mc(debug_=self.debug)
        self.multicast_profile.refresh_mc(debug_=self.debug)
        print("Starting layer-3 traffic (if any configured)")
        self.cx_profile.start_cx()
        self.cx_profile.refresh_cx()

        cur_time = datetime.datetime.now()
        print("Getting initial values.")
        old_rx_values = self.__get_rx_values()

        end_time = self.local_realm.parse_time(self.test_duration) + cur_time

        print("Monitoring throughput for duration: %s"%(self.test_duration))

        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)
            
            new_rx_values = self.__get_rx_values()

            expected_passes += 1
            if self.__compare_vals(old_rx_values, new_rx_values):
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
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.local_realm.admin_down(station_name)

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        for station_list in self.station_lists:
            for sta in station_list:
                self.local_realm.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()
                                        
    def build(self):
        # This is too fragile and limitted, let outside logic configure the upstream port as needed.
        #try:
        #    eid = self.local_realm.name_to_eid(self.side_b)
        #    data = LFUtils.port_dhcp_up_request(eid[1], eid[2])
        #    self.json_post("/cli-json/set_port", data)
        #except:
        #    print("LFUtils.port_dhcp_up_request didn't complete ")
        #    print("or the json_post failed either way {} did not set up dhcp so test may not pass data ".format(self.side_b))
        
        index = 0 
        for station_profile in self.station_profiles:
            station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            print("Creating stations")

            station_profile.create(radio=self.radio_list[index], sta_names_=self.station_lists[index], debug=self.debug, sleep_time=0)
            index += 1

            for etype in self.endp_types:
                if etype == "mc_udp" or etype == "mc_udp6":
                    print("Creating Multicast connections for endpoint type: %s"%(etype))
                    self.multicast_profile.create_mc_tx(etype, self.side_b, etype)
                    self.multicast_profile.create_mc_rx(etype, side_rx=station_profile.station_names)
                else:
                    for _tos in self.tos:
                        print("Creating connections for endpoint type: %s TOS: %s"%(etype, _tos))
                        self.cx_profile.create(endp_type=etype, side_a=station_profile.station_names, side_b=self.side_b, sleep_time=0, tos=_tos)

        self._pass("PASS: Stations build finished")

def valid_endp_types(_endp_type):
    etypes = _endp_type.split()
    for endp_type in etypes:
        valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            print('invalid endp_type: %s. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' % endp_type)
            exit(1)
    return _endp_type

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug_on = False

    parser = argparse.ArgumentParser(
        prog='test_l3_longevity.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will exit when traffic has not changed on a station for 1 minute
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Maximum stations per radio is 64
            ''',
        
        description='''\
test_l3_longevity.py:
--------------------
Basic Idea: create stations, create traffic between upstream port and stations,  run traffic. 
            The traffic on the stations will be checked once per minute to verify that traffic is transmitted
            and recieved.

            Test will exit on failure of not recieving traffice for one minute on any station.

            Scripts are executed from: ./lanforge/py-scripts  

            Stations start counting from zero,  thus stations count from zero - number of las

Generic command layout:
python .\\test_l3_longevity.py --test_duration <duration> --endp_type <traffic types> --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password> <security type: wpa2, open, wpa3> --debug

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

<tos>: 
            BK, BE, VI, VO:  Optional wifi related Tos Settings.  Or, use your preferred numeric values.
            

        Example:
            1. Test duration 4 minutes
            2. Traffic IPv4 TCP
            3. Upstream-port eth1
            4. Radio #1 wiphy0 has 32 stations, ssid = candelaTech-wpa2-x2048-4-1, ssid password = candelaTech-wpa2-x2048-4-1
            5. Radio #2 wiphy1 has 64 stations, ssid = candelaTech-wpa2-x2048-5-3, ssid password = candelaTech-wpa2-x2048-5-3
            6. Create connections with TOS of BK and VI

            Command: 
            python3 .\\test_l3_longevity.py --test_duration 4m --endp_type \"lf_tcp lf_udp mc_udp\" --tos \"BK VI\" --upstream_port eth1 --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 wpa2 --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 wpa2

        ''')

   
    parser.add_argument('--mgr', help='--mgr <hostname for where LANforge GUI is running>',default='localhost')
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m')
    parser.add_argument('--tos', help='--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE")
    parser.add_argument('--debug', help='--debug:  Enable debugging',default=False)
    parser.add_argument('-t', '--endp_type', help='--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')

    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-r', '--radio', action='append', nargs=5, metavar=('<wiphyX>', '<number last station>', '<ssid>', '<ssid password>', 'security'),
                         help ='--radio  <number_of_wiphy> <number of last station> <ssid>  <ssid password> <security>', required=True)
    args = parser.parse_args()

    debug_on = args.debug

    if args.test_duration:
        test_duration = args.test_duration

    if args.endp_type:
        endp_types = args.endp_type

    if args.mgr:
        lfjson_host = args.mgr

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio
    
    radio_offset = 0
    number_of_stations_offset = 1
    ssid_offset = 2
    ssid_password_offset = 3
    ssid_security_offset = 4

    MAX_NUMBER_OF_STATIONS = 64
    
    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []
    ssid_security_list = []

    for radio in radios:
        radio_name = radio[radio_offset]
        radio_name_list.append(radio_name)
        number_of_stations_per_radio = radio[number_of_stations_offset]
        number_of_stations_per_radio_list.append(number_of_stations_per_radio)
        ssid = radio[ssid_offset]
        ssid_list.append(ssid)
        if (len(radio) >= (ssid_password_offset - 1)):
            ssid_password_list.append(radio[ssid_password_offset])
            ssid_security_list.append(radio[ssid_security_offset])
        else:
            ssid_password_list.append("NA")
            ssid_security_list.append("open")

    index = 0
    station_lists = []
    for radio in radios:
        number_of_stations = int(number_of_stations_per_radio_list[index])
        if number_of_stations > MAX_NUMBER_OF_STATIONS:
            print("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
            quit(1)
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= 1 + index*1000, end_id_= number_of_stations + index*1000,
                                              padding_number_=10000, radio=radio[index])
        station_lists.append(station_list)
        index += 1

    #print("endp-types: %s"%(endp_types))

    ip_var_test = L3VariableTimeLongevity(lfjson_host, 
                                   lfjson_port, 
                                   number_template="00", 
                                   station_lists= station_lists,
                                   name_prefix="LT-",
                                   endp_types=endp_types,
                                   tos=args.tos,
                                   side_b=side_b,
                                   radios=radios,
                                   radio_name_list=radio_name_list,
                                   number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                   ssid_list=ssid_list,
                                   ssid_password_list=ssid_password_list,
                                   ssid_security_list=ssid_security_list, test_duration=test_duration,
                                   side_a_min_rate=256000, side_b_min_rate=256000, debug_on=debug_on)

    ip_var_test.pre_cleanup()

    ip_var_test.build()
    if not ip_var_test.passes():
        print("build step failed.")
        print(ip_var_test.get_fail_message())
        exit(1) 
    ip_var_test.start(False, False)
    ip_var_test.stop()
    if not ip_var_test.passes():
        print("stop test failed")
        print(ip_var_test.get_fail_message())
        exit(1) 

    print("Pausing 30 seconds after run for manual inspection before we clean up.")
    time.sleep(30)
    ip_var_test.cleanup()
    if ip_var_test.passes():
        print("Full test passed, all connections increased rx bytes")

if __name__ == "__main__":
    main()
