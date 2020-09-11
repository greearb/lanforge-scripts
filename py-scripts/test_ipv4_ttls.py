#!/usr/bin/env python3


import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
import LANforge
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
import time
import pprint


class TTLSTest(LFCliBase):
    def __init__(self, host, port, ssid, security, password, sta_list=None, number_template="00000", _debug_on=False,
                 _exit_on_error=False, radio="wiphy0", key_mgmt="WPA-EAP", eap="TTLS", identity="testuser",
                 ttls_passwd="testpasswd", ttls_realm="localhost.localdomain", domain="localhost.localdomain",
                 hessid="00:00:00:00:00:01", _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.radio = radio
        self.security = security
        self.password = password
        self.sta_list = sta_list
        self.key_mgmt = key_mgmt
        self.eap = eap
        self.identity = identity
        self.ttls_passwd = ttls_passwd
        self.ttls_realm = ttls_realm
        self.domain = domain
        self.hessid = hessid
        self.timeout = 120
        self.number_template = number_template
        self.debug = _debug_on
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.vap_profile = self.local_realm.new_vap_profile()
        self.vap_profile.vap_name = "TestNet"

        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0

    def build(self):
        # Build stations
        self.station_profile.use_security(self.security, self.ssid, passwd="[BLANK]")
        self.vap_profile.use_security(self.security, self.ssid, passwd="[BLANK]")
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.set_wifi_extra(key_mgmt=self.key_mgmt, eap=self.eap, identity=self.identity, passwd=self.ttls_passwd,
                                            realm=self.ttls_realm, domain=self.domain,
                                            hessid=self.hessid)
        self.vap_profile.set_wifi_extra(key_mgmt=self.key_mgmt, eap=self.eap, identity=self.identity, passwd=self.ttls_passwd,
                                            realm=self.ttls_realm, domain=self.domain,
                                            hessid=self.hessid)
        self.vap_profile.create(resource=1, radio=self.radio, channel=36, up_=True, debug=False, suppress_related_commands_=True, wifi_extra=True)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug, wifi_extra=True)
        self._pass("PASS: Station build finished")

    def start(self, sta_list, print_pass, print_fail):
        self.station_profile.admin_up()
        self.vap_profile.admin_up(1)
        associated_map = {}
        ip_map = {}
        print("Starting test...")
        for sec in range(self.timeout):
            for sta_name in sta_list:
                sta_status = self.json_get("port/1/1/" + sta_name + "?fields=port,alias,ip,ap", debug_=self.debug)
                # print(sta_status)
                if sta_status is None or sta_status['interface'] is None or sta_status['interface']['ap'] is None:
                    continue
                if len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':':
                    # print("Associated", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map[sta_name] = 1
                if sta_status['interface']['ip'] != '0.0.0.0':
                    # print("IP", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    ip_map[sta_name] = 1
            if (len(sta_list) == len(ip_map)) and (len(sta_list) == len(associated_map)):
                break
            else:
                time.sleep(1)

        if self.debug:
            print("sta_list", len(sta_list), sta_list)
            print("ip_map", len(ip_map), ip_map)
            print("associated_map", len(associated_map), associated_map)
        if (len(sta_list) == len(ip_map)) and (len(sta_list) == len(associated_map)):
            self._pass("PASS: All stations associated with IP", print_pass)
        else:
            self._fail("FAIL: Not all stations able to associate/get IP", print_fail)
            print("sta_list", sta_list)
            print("ip_map", ip_map)
            print("associated_map", associated_map)

        return self.passes()

    def stop(self):
        # Bring stations down
        self.station_profile.admin_down()
        self.vap_profile.admin_down(1)

    def cleanup(self, sta_list):
        self.station_profile.cleanup(sta_list)
        self.vap_profile.cleanup(1)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    parser = LFCliBase.create_basic_argparse(
        prog='test_ipv4_connection.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. TBD
            ''',

        description='''\
        test_ipv4_variable_time.py:
         --------------------
         TBD

         Generic command layout:
         python ./test_ipv4_variable_time.py --upstream_port <port> --radio <radio 0> <stations> <ssid> <ssid password> <security type: wpa2, open, wpa3> --debug

         Note:   multiple --radio switches may be entered up to the number of radios available:
                  --radio <radio 0> <stations> <ssid> <ssid password>  --radio <radio 01> <number of last station> <ssid> <ssid password>

         python3 ./test_ipv4_variable_time.py --upstream_port eth1 --radio wiphy0 32 candelaTech-wpa2-x2048-4-1 candelaTech-wpa2-x2048-4-1 wpa2 --radio wiphy1 64 candelaTech-wpa2-x2048-5-3 candelaTech-wpa2-x2048-5-3 wpa2

        ''')

    parser.add_argument('--a_min', help='--a_min bps rate minimum for side_a', default=256000)
    parser.add_argument('--b_min', help='--b_min bps rate minimum for side_b', default=256000)
    parser.add_argument('--test_duration', help='--test_duration sets the duration of the test', default="5m")
    parser.add_argument('--key_mgmt', help='--key_mgmt key management type to use', default="WPA-EAP")
    parser.add_argument('--eap', help='--eap eap method to use', default="TTLS")
    parser.add_argument('--identity', help='--identity eap identity string', default="testuser")
    parser.add_argument('--ttls_passwd', help='--ttls_passwd eap password string', default="testpasswd")
    parser.add_argument('--ttls_realm', help='--ttls_realm 802.11u realm to use', default="localhost.localdomain")
    parser.add_argument('--domain', help='--domain 802.11 domain to use', default="localhost.localdomain")
    parser.add_argument('--hessid', help='--hessid 802.11u HESSID (MAC address format) (or peer for WDS stations)',
                        default="00:00:00:00:00:01")

    args = parser.parse_args()
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000)
    ttls_test = TTLSTest(lfjson_host, lfjson_port, ssid=args.ssid, password=args.passwd,
                         security=args.security, sta_list=station_list, radio=args.radio, key_mgmt=args.key_mgmt,
                         eap=args.eap, identity=args.identity, ttls_passwd=args.ttls_passwd, ttls_realm=args.ttls_realm,
                         domain=args.domain, hessid=args.hessid)
    ttls_test.cleanup(station_list)
    #ttls_test.timeout = 60
    ttls_test.build()
    if not ttls_test.passes():
        print(ttls_test.get_fail_message())
        exit(1)
    ttls_test.start(station_list, False, False)
    ttls_test.stop()
    if not ttls_test.passes():
        print(ttls_test.get_fail_message())
        exit(1)
    time.sleep(30)
    ttls_test.cleanup(station_list)
    if ttls_test.passes():
        print("Full test passed, all stations associated and got IP")


if __name__ == "__main__":
    main()
