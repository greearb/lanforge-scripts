#!/usr/bin/env python3

import sys
import pprint
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import LFUtils
#from LANforge.add_file_endp import *
import argparse
#from realm import Realm
import realm
import time
import datetime

#from test_generic import GenTest


class IperfTest(LFCliBase):
    def __init__(self, host, port, _local_realm, ssid, security, passwd,upstream, radio="wiphy0", upstream_port="eth1", macvlan_type = "iperf3_serv", sta_type = "iperf3", num_ports=1, macvlan_parent=None, first_mvlan_ip=None, netmask=None, gateway=None,
                 dhcp=False,port_list=[], sta_list=[], ip_list=None,dest=None, test_duration="5m", interval=1, _debug_on=False,_exit_on_error=False,_exit_on_fail=False):
        super().__init__(host, port,_local_realm=realm.Realm(host,port), _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.port = port
        self.upstream_port = upstream_port
        self.port_list = []
        self.sta_list = sta_list
        self.netmask = netmask
        self.gateway = gateway
        self.dhcp = dhcp
        self.radio = radio
        self.security = security
        self.passwd = passwd
        self.upstream = upstream
        self.ssid = ssid
        self.test_duration = test_duration
        if macvlan_parent is not None:
            self.macvlan_parent = macvlan_parent
            self.port_list = port_list
        self.mvlan_profile = self.local_realm.new_mvlan_profile()
        self.mvlan_profile.num_macvlans = int(num_ports)
        self.mvlan_profile.desired_macvlans = self.port_list
        self.mvlan_profile.macvlan_parent = self.macvlan_parent
        self.mvlan_profile.dhcp = dhcp
        self.mvlan_profile.netmask = netmask
        self.mvlan_profile.first_ip_addr = first_mvlan_ip
        self.mvlan_profile.gateway = gateway
        self.generic_endps_profile = self.local_realm.new_generic_endp_profile()
        self.generic_endps_profile.type = macvlan_type
        self.created_ports = []
        self.station_profile = self.local_realm.new_station_profile()
        self.generic_endps_for_client = self.local_realm.new_generic_endp_profile()
        self.generic_endps_for_client.type = sta_type
        self.generic_endps_for_client.dest = dest
        self.generic_endps_for_client.interval = interval
        self._local_realm = _local_realm


    def build(self):
        print("Creating MACVLANs")
        self.mvlan_profile.create(admin_down=False, sleep_time=.5, debug=self.debug)
        self._pass("PASS: MACVLAN build finished")
        self.created_ports += self.mvlan_profile.created_macvlans
        self.generic_endps_profile.create(ports=self.mvlan_profile.created_macvlans, sleep_time=.5)
        self.station_profile.use_security(self.security, self.ssid, self.passwd)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        self.station_profile.admin_up()
        #self.generic_endps_for_client.create(ports=self.station_profile.station_names, sleep_time=.5)

    def create_gen_for_client(self, gen_sta_list, dest, suppress_related_commands_=None):
        server_ip = 0
        for gen_endp in gen_sta_list:
            port_info = self.local_realm.name_to_eid(gen_endp)
            data = {
                "alias": gen_endp,
                "shelf": 1,
                "resource": 1,
                "port": port_info[-1],
                "type": "gen_generic"
            }
            if self.debug:
                pprint(data)

            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.local_realm.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        time.sleep(0.5)
        for gen_endp in gen_sta_list:
            set_flag = {
                "name": gen_endp,
                "flag": "ClearPortOnStart",
                "val": 1
            }
            self.json_post("cli-json/set_endp_flag", set_flag, debug_=self.debug)
        time.sleep(0.5)

        for gen_endp in gen_sta_list:
            self.cmd = "iperf3 --forceflush --format k --precision 4 -c %s -t 60 --tos 0 -b 1K --bind_dev %s -i 1 " \
                       "--pidfile /tmp/lf_helper_iperf3_test.pid" % (dest[server_ip], gen_endp)

            data_cmd = {
                "name": gen_endp,
                "command": self.cmd
            }
            self.json_post("cli-json/set_gen_cmd", data_cmd, debug_=self.debug)
            server_ip = server_ip + 1
        """post_data = []
        for gen_endp in gen_sta_list:
            cx_name = "CX_generic-%s" % (gen_endp)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_endp,
                "rx_endp": "D_%s" % (gen_endp)
            }
            post_data.append(data)
        for data in post_data:
            url = "/cli-json/add_cx"
            if self.debug:
                pprint(data)
            self.local_realm.json_post(url, data, debug_=self.debug, suppress_related_commands_=suppress_related_commands_)
            time.sleep(2)

        time.sleep(0.5)
        for data in post_data:
            self.local_realm.json_post("/cli-json/show_cx", {
                "test_mgr": "default_tm",
                "cross_connect": data["alias"]
            })
        time.sleep(0.5)
"""
    def sta(self):
        self.station_profile.use_security(self.security, self.ssid, self.passwd)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        self.station_profile.admin_up()

    def start(self):

        self.generic_endps_for_client.create(ports=self.station_profile.station_names, sleep_time=.5)


    def macwlan_cx(self):
        self.generic_endps_profile.start_cx()
        #self.generic_endps_for_client.start_cx()

    def client_cx(self):
        """self.generic_endps_for_client.start_cx()
        time.sleep(20)"""
        temp_stas = []
        for station in self.sta_list.copy():
            temp_stas.append(self.local_realm.name_to_eid(station)[2])
        if self.debug:
            pprint.pprint(self.station_profile.station_names)
        LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url, port_list=self.station_profile.station_names)
        if self.local_realm.wait_for_ip(temp_stas):
            self._pass("All stations got IPs")
        else:
            self._fail("Stations failed to get IPs")
            self.exit_fail()
        cur_time = datetime.datetime.now()
        passes = 0
        expected_passes = 0
        self.generic_endps_for_client.start_cx()
        time.sleep(15)
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        print("Starting Test...")




def main():

    parser = LFCliBase.create_bare_argparse(
        prog='create_macvlan.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Creates MACVLAN endpoints.''',

        description='''\
''')
    parser.add_argument('--num_stations', help='Number of stations to create', default=0)
    parser.add_argument('--ssid', help='SSID for stations to associate to')
    parser.add_argument('--passwd', help='Number of stations to create', default=0)
    parser.add_argument('--security', help='security type to use for ssid { wep | wpa | wpa2 | wpa3 | open }')
    parser.add_argument('--dest', help='destination IP for command', default="10.40.0.1")
    parser.add_argument('--test_duration', help='duration of the test eg: 30s, 2m, 4h', default="2m")
    parser.add_argument('--interval', help='interval to use when running lfping (1s, 1m)', default=1)
    parser.add_argument('--radio', help='radio EID, e.g: 1.wiphy2')
    parser.add_argument('-u', '--upstream_port',
                        help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1',
                        default='1.eth1')
    parser.add_argument('--macvlan_parent', help='specifies parent port for macvlan creation', default=None)
    parser.add_argument('--macvlan_type', help='type of command to run: generic, lfping, iperf3-client, iperf3-server, lfcurl',
                        default="iperf3")
    parser.add_argument('--num_ports', help='number of ports to create', default=1)
    parser.add_argument('--first_mvlan_ip', help='specifies first static ip address to be used or dhcp', default=None)
    parser.add_argument('--netmask', help='specifies netmask to be used with static ip addresses', default=None)
    parser.add_argument('--gateway', help='specifies default gateway to be used with static addressing', default=None)
    parser.add_argument('--cmd', help='specifies command to be run by generic type endp', default='')
    args = parser.parse_args()

    port_list = []
    ip_list = []
    station_list = []


    num_ports = int(args.num_ports)

    port_list = LFUtils.port_name_series(prefix=args.macvlan_parent + "#", start_id=0,
                                         end_id=num_ports - 1, padding_number=100000,
                                         radio=args.radio)
    station_list = LFUtils.port_name_series(prefix="sta" + "#", start_id=0,
                                         end_id=num_ports - 1, padding_number=100000,
                                         radio=args.radio)
    """if args.first_mvlan_ip is not None:
        if args.first_mvlan_ip.lower() == "dhcp":
            dhcp = True
        else:
            dhcp = False
    else:
        dhcp = True"""

    ip_test = IperfTest(args.mgr, args.mgr_port, ssid=args.ssid,_local_realm = None,
                        passwd=args.passwd, upstream=args.upstream_port,
                        security=args.security, port_list=port_list, test_duration=args.test_duration, sta_list=station_list, ip_list=ip_list,
                        upstream_port=args.upstream_port, _debug_on=args.debug, macvlan_parent=args.macvlan_parent,
                        first_mvlan_ip=args.first_mvlan_ip, dest=args.dest, netmask=args.netmask, gateway=args.gateway,
                        dhcp=False, num_ports=args.num_ports, interval=1)
    ip_test.build()
    time.sleep(15)
    num_macvlan = 0
    all_macvlan_ip = []
    while True:
        if(num_macvlan < num_ports):
            macvlan_ip_list = ip_test.json_get("/port/1/1/eth1#%s?field=ip"% (num_macvlan))
            get_ip = (macvlan_ip_list['interface']['ip'])
            num_macvlan = num_macvlan + 1
            all_macvlan_ip.append(get_ip)
        else:
            break
    time.sleep(5)
    i=0
    #ip_test.create_gen_for_client(station_list, all_macvlan_ip)




    """for each in all_macvlan_ip:
        station_list = LFUtils.portNameSeries(radio=args.radio,
                                              prefix_="sta%s#" % (i),
                                              start_id_=0,
                                              end_id_=1 - 1,
                                              padding_number_=100)
        ip_test1 = IperfTest(args.mgr, args.mgr_port, ssid=args.ssid,
                            passwd=args.passwd, upstream=args.upstream_port,
                            security=args.security, port_list=port_list, test_duration=args.test_duration, sta_list=station_list, ip_list=ip_list,
                            upstream_port=args.upstream_port, _debug_on=args.debug, macvlan_parent=args.macvlan_parent,
                            first_mvlan_ip=args.first_mvlan_ip, dest=each, netmask=args.netmask,
                            gateway=args.gateway,
                            dhcp=dhcp, num_ports=args.num_ports, interval=1)
        ip_test1.sta()

        ip_test1.start()
        time.sleep(5)
        i = i + 1
    for gen_end in all_macvlan_ip:
        ip_test.macwlan_cx()
        time.sleep(0.5)
        ip_test1.client_cx()
        time.sleep(0.5)"""


if __name__ == "__main__":
    main()