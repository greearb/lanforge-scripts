#!/usr/bin/env python3
# flake8: noqa
'''
NAME: test_l3_unicaast_traffic_gen.py

NOTES:  

Looke at lanforge_api.py   EAP-PEAP  # Use EAP-PEAP connection logic on all ssids, deprecated, see add_dut_ssid.

COPYRIGHT:
Copyright 2022 Candela Technoligies Inc

'''
import sys
import os
import importlib
import argparse
import time
import datetime
import logging
import copy

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

logger = logging.getLogger(__name__)



class L3VariableTimeLongevity(Realm):
    def __init__(self, 
                host='localhost',
                port='8080',
                endp_type=None,
                side_b=None,
                radios=None, 
                radio_name_list=None,
                number_of_stations_per_radio_list=None,
                ssid_list=[],
                ssid_password_list=[],
                security_list=[],
                station_lists=[],
                key_mgt_list=[],
                pairwise_list=[],
                group_list=None,
                eap_list=None,
                name_prefix=None,
                resource=None,
                side_a_min_rate=1240000,
                side_a_max_rate=0,
                side_b_min_rate=1240000,
                side_b_max_rate=0,
                number_template="00",
                test_duration="125s",
                _debug_on=False,
                _exit_on_error=False,
                _exit_on_fail=False):
        super().__init__(lfclient_host=host, lfclient_port=port, debug_=_debug_on, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.endp_type = endp_type
        self.side_b = side_b
        self.ssid_list = ssid_list,
        self.ssid_password_list = ssid_password_list
        self.station_lists = station_lists
        self.security_list = security_list
        self.key_mgt_list = key_mgt_list
        self.pairwise_list = pairwise_list
        self.group_list = group_list
        self.eap_list = eap_list
        self.number_template = number_template
        self.resource = resource
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.cx_stations_lists = station_lists
        self.radios = radios  # from the command line
        self.radio_list = radio_name_list
        self.number_of_stations_per_radio_list = number_of_stations_per_radio_list
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profiles = []

        for radio in range(0, len(radios)):
            self.station_profile = self.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_list[radio]
            self.station_profile.ssid_pass = ssid_password_list[radio]
            self.station_profile.security = security_list[radio]
            # self.station_profile.set_wifi_extra(key_mgmt=key_mgt_list[radio],
            #                                     pairwise=pairwise_list[radio],
            #                                     group=group_list[radio],
            #                                     psk="",
            #                                     eap=group_list[radio],
            #                                     identity="",
            #                                     passwd="",
            #                                     pin="")

            if key_mgt_list[radio] != "":
                self.station_profile.set_wifi_extra(key_mgmt=key_mgt_list[radio],
                                                    pairwise=pairwise_list[radio],
                                                    group=group_list[radio],
                                                    psk='[BLANK]',
                                                    eap=group_list[radio],
                                                    identity='[BLANK]',
                                                    anonymous_identity="[BLANK]",
                                                    phase1="[BLANK]",
                                                    phase2="[BLANK]",
                                                    passwd='[BLANK]',
                                                    pin='[BLANK]',
                                                    pac_file='[BLANK]',
                                                    private_key='[BLANK]',
                                                    pk_password='[BLANK]',
                                                    hessid="00:00:00:00:00:00",
                                                    realm="[BLANK]",
                                                    client_cert="[BLANK]",
                                                    imsi="[BLANK]",
                                                    milenage="[BLANK]",
                                                    domain="[BLANK]",
                                                    roaming_consortium="[BLANK]",
                                                    venue_group="[BLANK]",
                                                    network_type="[BLANK]",
                                                    ipaddr_type_avail="[BLANK]",
                                                    network_auth_type="[BLANK]",
                                                    anqp_3gpp_cell_net="[BLANK]"
                                                )
                self.station_profile.set_command_param("add_sta","ieee80211w", 2)
                self.station_profile.set_command_flag("add_sta","80211u_enable", 0)
                self.station_profile.set_command_flag("add_sta","8021x_radius", 1)


            self.station_profile.number_template = self.number_template
            self.station_profile.mode = 0
            self.station_profiles.append(self.station_profile)

        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def __get_rx_values(self):
        cx_list = self.json_get("endp?fields=name,rx+bytes", debug_=self.debug)
        cx_rx_map = {}
        for cx_name in cx_list['endpoint']:
            if cx_name != 'uri' and cx_name != 'handler':
                for item, value in cx_name.items():
                    for value_name, value_rx in value.items():
                        if value_name == 'rx bytes':
                            cx_rx_map[item] = value_rx
        return cx_rx_map

    @staticmethod
    def __compare_vals(old_list, new_list):
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
        up_request = LFUtils.port_up_request(resource_id=self.resource, port_name=self.side_b)
        self.json_post("/cli-json/set_port", up_request)
        for station_profile, station_list in zip(self.station_profiles, self.station_lists):
            if self.debug:
                print("Bringing up station {}".format(station_profile))
            station_profile.admin_up()
            if self.wait_for_ip(station_list=station_list, timeout_sec=10 * len(station_list)):
                if self.debug:
                    logger_info("ips acquired {}".format(station_list))
            else:
                if self.wait_for_ip(station_list=station_list):
                    logger.info("tried again, ip qcquired {}".format(station_list))
                else:
                    logger.error("station failed to get ip {}".format(station_list))

        self.cx_profile.start_cx()

        cur_time = datetime.datetime.now()
        old_rx_values = self.__get_rx_values()
        filtered_old_rx_values = old_rx_values

        end_time = self.parse_time(self.test_duration) + cur_time

        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_rx_values = self.__get_rx_values()
            filtered_new_rx_values = new_rx_values

            expected_passes += 1
            if self.__compare_vals(filtered_old_rx_values, filtered_new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
            cur_time = datetime.datetime.now()

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        for station_list in self.station_lists:
            for station_name in station_list:
                data = LFUtils.portDownRequest(self.resource, station_name)
                url = "cli-json/set_port"
                self.json_post(url, data)

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        # self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.rm_port(sta, check_exists=True)
                self.total_stas += 1

        # Make sure they are gone
        count = 0
        while count < 10:
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.rm_port(sta, check_exists=True)
                    if rv:
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)

    # Remove traffic connections and stations.
    def cleanup(self):
        self.cx_profile.cleanup()
        # self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()

    def build(self):
        # refactor in LFUtils.port_zero_request()
        #resource = 1

        # refactor into LFUtils
        #data = {
        #    "shelf": 1,
        #    "resource": resource,
        #    "port": "br0",
        #    "network_devs": "eth1,"

        #}
        #url = "cli-json/add_br"
        #self.json_post(url, data)

        data = LFUtils.port_dhcp_up_request(self.resource, self.side_b)
        self.json_post("/cli-json/set_port", data)

        temp_station_list = []
        self.station_profile.set_command_param(
            "set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        index = 0
        for station_profile, station_list in zip(self.station_profiles, self.station_lists):
            station_profile.use_security(security_type=station_profile.security,
                                         ssid=station_profile.ssid, passwd=station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            if self.debug:
                print("radio: {} station_profile: {} Creating stations: {} ".format(self.radio_list[index],
                                                                                    station_profile, station_list))

            for station in range(len(station_list)):
                temp_station_list.append(str(self.resource) + "." + station_list[station])
            create = station_profile.create(radio=self.radio_list[index],
                                            sta_names_=temp_station_list,
                                            debug=self.debug)
            if not create:
                raise RuntimeError("Station is phantom")

            index += 1
            self.cx_profile.create(endp_type=self.endp_type, side_a=temp_station_list, side_b='1.' + self.side_b,
                                   sleep_time=.5)
        self._pass("PASS: Stations build finished")


def valid_endp_type(endp_type):
    valid_endp_types = ['lf_udp', 'lf_udp6', 'lf_tcp', 'lf_tcp6']
    if str(endp_type) in valid_endp_types:
        return endp_type
    else:
        print('invalid endp_type. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6')
        exit(1)


def main():
    # create_basic_argsparse /py-json/LANforge/lfcli_base.py
    parser = Realm.create_basic_argparse(
        prog='test_l3_unicast_traffic_gen.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
Useful Information:

1. Polling interval for checking traffic is fixed at 1 minute
2. The test will exit when traffic has not changed on a station for 1 minute
3. The tx/rx rates are fixed at 256000 bits per second
4. Maximum stations per radio is 64

5. radio list order  --radio_list  <number_of_wiphy> <number of last station> <ssid> <ssid password> <security> <key_management> <pairwise_ciphers>  <group_ciphers> <eap_methods>

            ''',

        description='''\
test_l3_unicast_traffic_gen.py:
--------------------
Basic Idea: 

create stations, create traffic between upstream port and stations,  run traffic. 
The traffic on the stations will be checked once per minute to verify that traffic is transmitted
and received.

Test will exit on failure of not receiving traffic for one minute on any station.

Scripts are executed from: ./lanforge/py-scripts  

Stations start counting form zero,  thus stations count from zero - number of las 

Generic command layout:
python ./test_l3_unicast_traffic_gen.py
        --test_duration <duration> 
        --endp_type <traffic type> 
        --upstream_port <port> 
        --radio <radio_name> <num_stations> <ssid> <ssid_password>

Note:   
multiple --radio switches may be entered up to the number of radios available:
--radio <radio 0> <number of stations> <ssid> <ssid password>  --radio <radio 01> <number of stations> <ssid> <ssid password>

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

Example:
    1. Test duration 4 minutes
    2. Traffic IPv4 TCP
    3. Upstream-port eth1
    4. Radio #1 wiphy0 has 32 stations, ssid = candelaTech-wpa2-x2048-4-1, ssid password = candelaTech-wpa2-x2048-4-1
    5. Radio #2 wiphy1 has 64 stations, ssid = candelaTech-wpa2-x2048-5-3, ssid password = candelaTech-wpa2-x2048-5-3

Example: 
Some of the command line switches are in /py-json/lfcli_base.py
python3 .\\test_l3_unicast_traffic_gen.py --lfmgr --test_duration 4m --endp_type lf_tcp --upstream_port eth1 \
                                --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 \
                                --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 

        ''')

    parser.add_argument('--test_duration',
                        help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',
                        default='3m')
    parser.add_argument('-t', '--endp_type',
                        help='--endp_type <type of traffic> example --endp_type lf_udp, default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6',
                        default='lf_udp', type=valid_endp_type)



    requiredNamed = parser.add_argument_group('required arguments')

    requiredNamed.add_argument('--radio_list', action='append', nargs='*',
                                help='''
                                --radio_list  <number_of_wiphy> <number of last station> <ssid> <ssid password> <security> <key_management> <pairwise_ciphers>  <group_ciphers> <eap_methods>
                                if radio list is 4 in length the security defaults to wpa2,  all other parameters are 'DEFAULT'

                                if radio list is 5 in length, security is set, all other parameters are 'DEFAULT' 

                                if radio list is 6 in length, key management is set to OWE, security needs to be set so radio list
                                    key_management = OWE

                                if radio list is 9 then all parameters are set
                                    Key_management = WPA-EAP-SHA256
                                    pairwise_ciphers = CCMP-256
                                    group_cipher = 'GCMP-256'
                                    eap_methods = EAP-PEAP

                                (WPA2 TLS) [14]
                                if radio list is 
                                    Key_management = WPA-EAP
                                    EAP Methods = EAP-TLS
                                    EAP Identity = testuser
                                    EAP Password = testpasswd
                                    Pirvate Key = /home/lanforge/client.p12
                                    CA Cert File = /home/lanforge/ca.pem
                                    PK Passwrod = lanforge
                                    Ieee80211w  = Disabled (0)
                                    Advanced/8021x = checked
                                    Enabled PKC = checked

                                (WPA2 TTLS) [10]
                                if radio list is 
                                    Key_management = WPA-EAP
                                    EAP Methods = EAP-TTLS
                                    EAP Identity = testuser
                                    EAP Password = testpasswd
                                    PK Password = lanforge
                                    Advanced/8021x = checked


                                (WPA3 TLS) [16]
                                if radio list is 
                                    Key_management = WPA-EAP-SUITE-B-192
                                    Pairwise Ciphers = GCMP-256 (wpa3)
                                    Group Ciphers = GCMP - 256 (wpa3)
                                    EAP Methods = EAP-TLS
                                    EAP Identity = testuser
                                    EAP Password = testpasswd
                                    Pirvate Key = /home/lanforge/client.p12
                                    CA Cert File = /home/lanforge/ca.pem
                                    PK Passwrod = lanforge
                                    Ieee80211w  = Required (2)
                                    Advanced/8021x = checked
                                    Enabled PKC = checked


                                (WPA3 TTLS) [12]
                                if radio list is 
                                    Key_management = WPA-EAP
                                    Pairwise Ciphers = GCMP-256 (wpa3)
                                    Group Ciphers = GCMP-256 (wpa3)
                                    EAP Methods = EAP-TLS
                                    EAP Identity = testuser
                                    EAP Password = testpasswd
                                    Ieee80211w  = Required (2)
                                    Advanced/8021x = checked

                                    example:
                                --radio_list wiphy0 1 axe11000_6g lf_axe11000_6g wpa3 WPA-EAP-SHA256 CCMP-256 GCMP-256 PEAP


                                Acceptable lengths are 4,5,6,9, 10 (wpa2 TTLS), 12 (wpa3 TTLS), 14 (wpa2 TLS), 16 (wpa3 TLS)
                                ''',
                               required=True)

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    if (args.log_level):
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


    side_b = LFUtils.name_to_eid(args.upstream_port)
    resource = side_b[1]
    upstream_port =  side_b[2]

    radio_offset = 0
    number_of_stations_offset = 1
    ssid_offset = 2
    ssid_password_offset = 3
    security_offset = 4

    # Original offsets
    key_mgt_offset = 5
    pairwise_offset = 6
    group_offset = 7
    eap_offset = 8

    # WPA2_TLS
    
    
    # WPA2_TTLS
    wpa2_ttls_key_mgt_offset = 5
    wpa2_ttls_eap_methods = 6
    wpa2_ttls_eap_identity = 7
    wpa2_ttls_eap_password = 8
    wpa2_ttls_pk_password = 9


    # WPA3_TTLS
    wpa3_ttls_key_mgt_offset = 5
    wpa3_ttls_pairwise_offset = 6
    wpa3_ttls_group_offset = 7
    wpa3_ttls_eap_methods = 8
    wpa3_ttls_eap_identity = 9
    wpa3_ttls_eap_password = 10
    # Ieee80211w = Required
    # Advanced/8021x = checked

    

    MAX_NUMBER_OF_STATIONS = 64

    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []
    security_list = []
    key_mgt_list = []
    pairwise_list = []
    group_list = []
    eap_list = [] 

    logger.info("radio_list length {radio_list}".format(radio_list=len(args.radio_list)))

    for radio in args.radio_list:
        radio_args_len = len(radio)
        logger.info("radio length {radio}".format(radio=len(radio)))
        radio_name = radio[radio_offset]
        radio_name_list.append(radio_name)
        number_of_stations_per_radio = radio[number_of_stations_offset]
        number_of_stations_per_radio_list.append(number_of_stations_per_radio)
        ssid = radio[ssid_offset]
        ssid_list.append(ssid)
        ssid_password = radio[ssid_password_offset]
        ssid_password_list.append(ssid_password)
        # for backward compatibity previously nargs was on 4 (did not include security)
        key_mgt = ""
        pairwise = ""
        group = ""
        eap = ""

        if radio_args_len == 4:
            security = "wpa2"
            # eap = radio[eap_offset]
        elif radio_args_len == 5:
            security = radio[security_offset]
        elif radio_args_len == 6:
            security = radio[security_offset]
            key_mgt = radio[key_mgt_offset]
        elif radio_args_len == 9:
            security = radio[security_offset]
            key_mgt = radio[key_mgt_offset]
            pairwise = radio[pairwise_offset]
            group = radio[group_offset]
            eap = radio[eap_offset]
        else:
            logger.info('''
            if radio list is 4 in length the security defaults to wpa2,  all other parameters are 'DEFAULT'
            if radio list is 5 in length, security is set, all other parameters are 'DEFAULT' 
            if radio list is 6 in length, key management is set to OWE, security needs to be set so radio list
            if radio list is 9 then all parameters are set
            Acceptable lengths are 4,5,6,9
            ''' )
            exit(2)

        security_list.append(security)
        key_mgt_list.append(key_mgt)
        pairwise_list.append(pairwise)
        group_list.append(group)
        eap_list.append(eap)


    station_lists = []
    for radio_list in range(0, len(args.radio_list)):
        number_of_stations = int(number_of_stations_per_radio_list[radio_list])
        if number_of_stations > MAX_NUMBER_OF_STATIONS:
            logger.error("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
            quit(1)
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=1 + radio_list * 1000,
                                              end_id_=number_of_stations + radio_list * 1000, padding_number_=10000)
        station_lists.append(station_list)

    ip_var_test = L3VariableTimeLongevity(host=args.mgr, 
                                            port=args.mgr_port, 
                                            station_lists=station_lists,
                                            name_prefix="var_time", 
                                            resource=resource,
                                            endp_type=args.endp_type, 
                                            side_b=upstream_port, 
                                            radios=args.radio_list,
                                            radio_name_list=radio_name_list,
                                            number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                            ssid_list=ssid_list, 
                                            ssid_password_list=ssid_password_list, 
                                            security_list=security_list,
                                            key_mgt_list=key_mgt_list,
                                            pairwise_list=pairwise_list,
                                            group_list=group_list,
                                            eap_list=eap_list,
                                            test_duration=args.test_duration, 
                                            _debug_on=args.debug)

    ip_var_test.pre_cleanup()
    ip_var_test.build()
    if not ip_var_test.passes():
        logger.info(ip_var_test.get_fail_message())
        exit(1)
    ip_var_test.start()
    ip_var_test.stop()
    if not ip_var_test.passes():
        print(ip_var_test.get_fail_message())
        exit(1)
    time.sleep(30)
    ip_var_test.cleanup()
    if ip_var_test.passes():
        print("Full test passed, all connections increased rx bytes")


if __name__ == "__main__":
    main()
