"""

NAME: lf_multipsk.py

PURPOSE:
        to test the multipsk feature in access point. Multipsk feature states connecting clients using same ssid but different passwords ,
        here we will create two or 3 passwords with different vlan id on single ssid and try to connect client with different passwords.

DESCRIPTION:
            The script will follow basic functionality as:-
            1- create station on input parameters provided
            2- the input parameters consist of list of passwords,upstream,mac address, number of clients and radio as input
            3- will create layer3 cx for tcp and udp
            3- verify layer3 cx
            4- verify the ip for each station is comming from respective vlan id or not.
example :-
        python3 lf_multipsk.py --mgr 192.168.200.29 --mgr_port 8080 --ssid nikita --security wpa2 --passwd password@123 password@123 password@123  --num_sta 2   --radio wiphy1 --input "password@123","eth1","",2,wiphy1   "password@123","eth1","",2,wiphy0

INCLUDE_IN_README
    -Nikita Yadav
    Copyright 2021 Candela Technologies Inc
    License: Free to distribute and modify. LANforge systems must be licensed.
    #in progress
"""
import argparse
import os
import sys
import time

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
from realm import Realm


class MultiPsk(Realm):
    def __init__(self,
                 host=None,
                 port=None,
                 ssid=None,
                 input=None,
                 security=None,
                 passwd=None,
                 radio=None,
                 num_sta=None,
                 start_id=0,
                 resource=1,
                 sta_prefix="sta",
                 debug_=False,
                 ):
        self.host = host
        self.port = port
        self.ssid = ssid
        self.input = input
        self.security = security
        self.passwd = passwd
        self.radio = radio
        self.num_sta = num_sta
        self.start_id = start_id
        self.resource = resource
        self.sta_prefix = sta_prefix
        self.debug = debug_
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()

    def build(self):

        for idex, input in enumerate(self.input):
            input_list = input.split(',')
            if idex == 0:
                number = 10
            elif idex == 1:
                number = 100
            elif idex == 2:
                number = 1000
            elif idex == 3:
                number = 10000
            print("creating stations")
            station_list = LFUtils.portNameSeries(prefix_=self.sta_prefix, start_id_=self.start_id,
                                                  end_id_=int(input_list[3]) - 1, padding_number_=number,
                                                  radio=input_list[4])
            self.station_profile.use_security(self.security, self.ssid, str(input_list[0]))
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            self.station_profile.create(radio=input_list[4], sta_names_=station_list, debug=self.local_realm.debug)
            self.local_realm.wait_until_ports_appear(sta_list=station_list)
            self.station_profile.admin_up()
            if self.local_realm.wait_for_ip(station_list, timeout_sec=60):
                print("All stations got IPs")
            else:
                print("Stations failed to get IPs")

            print("create udp endp")
            self.cx_profile_udp = self.local_realm.new_l3_cx_profile()
            self.cx_profile_udp.side_a_min_bps = 128000
            self.cx_profile_udp.side_b_min_bps = 128000
            self.cx_profile_udp.side_a_min_pdu = 1200
            self.cx_profile_udp.side_b_min_pdu = 1500
            self.cx_profile_udp.report_timer = 1000
            self.cx_profile_udp.name_prefix = "udp"
            port_list = list(self.local_realm.find_ports_like("%s+" % self.sta_prefix))
            print("port list", port_list)
            if (port_list is None) or (len(port_list) < 1):
                raise ValueError("Unable to find ports named '%s'+" % self.sta_prefix)
            self.cx_profile_udp.create(endp_type="lf_udp",
                                       side_a=port_list,
                                       side_b="%d.%s" % (self.resource, input_list[1]),
                                       suppress_related_commands=True)

            # Create TCP endpoints
            print("create tcp endp")
            self.l3_tcp_profile = self.local_realm.new_l3_cx_profile()
            self.l3_tcp_profile.side_a_min_bps = 128000
            self.l3_tcp_profile.side_b_min_bps = 56000
            self.l3_tcp_profile.name_prefix = "tcp"
            self.l3_tcp_profile.report_timer = 1000
            self.l3_tcp_profile.create(endp_type="lf_tcp",
                                       side_a=list(self.local_realm.find_ports_like("%s+" % self.sta_prefix)),
                                       side_b="%d.%s" % (self.resource, input_list[1]),
                                       suppress_related_commands=True)

    def start(self):
        self.cx_profile_udp.start_cx()
        self.l3_tcp_profile.start_cx()

    def monitor_vlan_ip(self):
        data = self.local_realm.json_get("ports/list?fields=IP")
        # print(data)
        for i in data["interfaces"]:
            for j in i:
                if "1.1.eth2.100" == j:
                    ip_upstream = i["1.1.eth2.100"]['ip']
                    # print(ip_upstream)
        return ip_upstream

    def get_sta_ip(self):
        port_list = list(self.local_realm.find_ports_like("%s+" % self.sta_prefix))
        # print("port list", port_list)
        data = self.local_realm.json_get("ports/list?fields=IP")
        # print(data)
        for i in data["interfaces"]:
            # print(i)
            for j in i:
                if j == "1.1.sta0":
                    sta_ip = i["1.1.sta0"]['ip']
        print(sta_ip)
        return sta_ip

    def compare_ip(self):
        vlan_ip = self.monitor_vlan_ip()
        station_ip = self.get_sta_ip()
        vlan_ip_ = vlan_ip.split('.')
        station_ip_ = station_ip.split('.')
        if vlan_ip_[0] == station_ip_[0] and vlan_ip_[1] == station_ip_[1] and vlan_ip_[2] == station_ip_[2]:
            print("station got ip from vlan")
            return "Pass"
        else:
            print("station did not got ip from vlan")
            return "Fail"

    def postcleanup(self):
        self.cx_profile_udp.cleanup()
        self.l3_tcp_profile.cleanup()
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)
        print("Test Completed")


def main():
    parser = argparse.ArgumentParser(description="lanforge webpage download Test Script")
    parser.add_argument('--mgr', help='hostname for where LANforge GUI is running', default='localhost')
    parser.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on', default=8080)
    parser.add_argument('--ssid', help='WiFi SSID for client to associate to')
    parser.add_argument('--security', help='WiFi Security protocol: {open|wep|wpa2|wpa3', default="wpa2")
    parser.add_argument('--input', nargs="+", help="specify list of parameters like passwords,upstream,mac address, number of clients and radio as input, eg password@123,eth2.100,"",1,wiphy0  lanforge@123,eth2.100,"",1,wiphy1")
    args = parser.parse_args()
    multi_obj = MultiPsk(host=args.mgr,
                         port=args.mgr_port,
                         ssid=args.ssid,
                         input=args.input,
                         security=args.security)
    multi_obj.build()
    multi_obj.start()
    time.sleep(60)
    multi_obj.monitor_vlan_ip()
    multi_obj.get_sta_ip()
    result = multi_obj.compare_ip()
    if result == "Pass":
        print("Test pass")
    else:
        print("Test Fail")

    multi_obj.postcleanup()


if __name__ == '__main__':
    main()
