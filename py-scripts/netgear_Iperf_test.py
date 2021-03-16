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
import argparse
import realm
import time

class IperfTest(LFCliBase):
    def __init__(self, host, port, _local_realm, ssid, security, passwd, radio="wiphy0", macvlan_type = "iperf3_serv", sta_type = "iperf3", num_ports=1, macvlan_parent=None,
                 dhcp=False,port_list=[], sta_list=[],_debug_on=False,_exit_on_error=False,_exit_on_fail=False):
        super().__init__(host, port,_local_realm=realm.Realm(host,port), _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        #self.port = port
        self.port_list = []
        self.created_cx = []
        self.sta_list = sta_list
        self.dhcp = dhcp
        self.radio = radio
        self.security = security
        self.passwd = passwd
        self.ssid = ssid
        self.created_endp = []
        if macvlan_parent is not None:
            self.macvlan_parent = macvlan_parent
            self.port_list = port_list
        self.mvlan_profile = self.local_realm.new_mvlan_profile()
        self.mvlan_profile.num_macvlans = int(num_ports)
        self.mvlan_profile.desired_macvlans = self.port_list
        self.mvlan_profile.macvlan_parent = self.macvlan_parent
        self.mvlan_profile.dhcp = dhcp
        self.generic_endps_profile = self.local_realm.new_generic_endp_profile()
        self.generic_endps_profile.type = macvlan_type
        self.created_ports = []
        self.station_profile = self.local_realm.new_station_profile()
        self._local_realm = _local_realm
        self.name_prefix = "generic"


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
    def set_flags(self, endp_name, flag_name, val):
        data = {
            "name": endp_name,
            "flag": flag_name,
            "val": val
        }
        self.json_post("cli-json/set_endp_flag", data, debug_=self.debug)
    def create_gen_for_client(self, gen_sta_list, dest, suppress_related_commands_=None):
        server_ip = 0
        endp_tpls = []
        for port_name in gen_sta_list:
            port_info = self.local_realm.name_to_eid(port_name)
            if len(port_info) == 2:
                resource = 1
                shelf = port_info[0]
                name = port_info[-1]
            elif len(port_info) == 3:
                resource = port_info[0]
                shelf = port_info[1]
                name = port_info[-1]
            else:
                raise ValueError("Unexpected name for port_name %s" % port_name)
            gen_name_a = "%s-%s" % (self.name_prefix, name)
            gen_name_b = "D_%s-%s" % (self.name_prefix, name)
            endp_tpls.append((shelf, resource, name, gen_name_a, gen_name_b))

        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            # gen_name_b  = endp_tpl[3]
            # (self, alias=None, shelf=1, resource=1, port=None, type=None)

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": resource,
                "port": name,
                "type": "gen_generic"
            }
            if self.debug:
                pprint(data)

            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.local_realm.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        time.sleep(0.5)

        for endp_tpl in endp_tpls:
            gen_name_a = endp_tpl[3]
            gen_name_b = endp_tpl[4]
            self.set_flags(gen_name_a, "ClearPortOnStart", 1)
        time.sleep(0.5)
        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            self.cmd = "iperf3 --forceflush --format k --precision 4 -c %s -t 60 --tos 0 -b 1K --bind_dev %s -i 1 " \
                       "--pidfile /tmp/lf_helper_iperf3_test.pid" % (dest[server_ip], name)
            data_cmd = {
                "name": gen_name_a,
                "command": self.cmd
            }
            self.json_post("cli-json/set_gen_cmd", data_cmd, debug_=self.debug)
            server_ip = server_ip + 1
        time.sleep(0.5)
        post_data = []
        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            gen_name_b = endp_tpl[4]
            cx_name = "CX_%s-%s" % (self.name_prefix, name)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a,
                "rx_endp": gen_name_b
            }
            post_data.append(data)
            self.created_cx.append(cx_name)
            self.created_endp.append(gen_name_a)
            self.created_endp.append(gen_name_b)

        time.sleep(0.5)

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

    def macwlan_cx(self):
        self.generic_endps_profile.start_cx()
        time.sleep(10)

    def generic_cx(self):
        #self.generic_endps_for_client.start_cx(self.created_ports)
        for cx_name in self.created_cx:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")
        time.sleep(10)

def main():

    parser = LFCliBase.create_bare_argparse(
        prog='create_macvlan.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Creates MACVLAN endpoints.''',

        description='''\
         python netgear_Iperf_test.py --mgr 192.168.200.28 --mgr_port 8080 --macvlan_parent eth1 --num_ports 5 --radio wiphy1 --ssid Captive --passwd [Blank] --security open 

''')
    parser.add_argument('--num_stations', help='Number of stations to create', default=0)
    parser.add_argument('--ssid', help='SSID for stations to associate to')
    parser.add_argument('--passwd', help='Number of stations to create', default=0)
    parser.add_argument('--security', help='security type to use for ssid { wep | wpa | wpa2 | wpa3 | open }')
    parser.add_argument('--radio', help='radio EID, e.g: 1.wiphy2')
    parser.add_argument('--macvlan_parent', help='specifies parent port for macvlan creation', default=None)
    parser.add_argument('--num_ports', help='number of ports to create', default=1)

    args = parser.parse_args()

    port_list = []
    station_list = []


    num_ports = int(args.num_ports)

    port_list = LFUtils.port_name_series(prefix=args.macvlan_parent + "#", start_id=0,
                                         end_id=num_ports - 1, padding_number=100000,
                                         radio=args.radio)
    station_list = LFUtils.port_name_series(prefix="sta" + "#", start_id=0,
                                         end_id=num_ports - 1, padding_number=100000,
                                         radio=args.radio)

    ip_test = IperfTest(args.mgr, args.mgr_port, ssid=args.ssid,_local_realm = None,
                        passwd=args.passwd,
                        security=args.security, port_list=port_list,sta_list=station_list, _debug_on=args.debug, macvlan_parent=args.macvlan_parent,
                        dhcp=True, num_ports=args.num_ports)
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
    ip_test.create_gen_for_client(station_list, all_macvlan_ip)
    time.sleep(10)
    ip_test.macwlan_cx()
    ip_test.generic_cx()
    time.sleep(10)


if __name__ == "__main__":
    main()