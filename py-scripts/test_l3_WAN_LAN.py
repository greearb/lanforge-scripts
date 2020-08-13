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
import pprint
import datetime

class L3LANtoWAN(LFCliBase):
    def __init__(self, host, port, ssid, security, password, resource=1, sta_list=None, number_template="00000", _debug_on=True,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.sta_list = sta_list
        self.resource = resource
        self.timeout = 120
        self.number_template = number_template
        self.debug = _debug_on
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
    
    #build bridge and rdd pair
    def build(self):
        # Build bridge
        req_url_br = "cli-json/add_br"
        data_br = {
            "shelf": 1,
            "resource": 1,
            "port": 'br0',
            "network_devs": 'rd0a',
            "br_flags": 0,
            "br_priority": 65535,
            "br_aging_time": -1,
            "br_max_age": -1,
            "br_hello_time": -1,
            "br_forwarding_delay":-1

        } 
        
        super().json_post(req_url_br, data_br, debug_ = self.debug)

        #set port json post
        req_url_set_port = "cli-json/set_port"
        data_set_port = {
            "shelf": 1,
            "resource": 1,
            "port": 'br0',
            "current_flags": 131072,
            "interest": 8548171804,
            "report_timer": 3000,
            "br_priority": 65535,
            "br_aging_time": -1,
            "br_max_age": -1,
            "br_hello_time": -1,
            "br_forwarding_delay":-1,
            "br_port_cost": -1,
            "br_port_priority":255,
            "current_flags_msk": 135107988821114880
        }   
        super().json_post(req_url_set_port, data_set_port, debug_ = self.debug)

        #add_vrcx
        req_url_add_vrcx= "cli-json/add_vcrx"
        data_add_vrcx = {
            "shelf": 1,
            "resource": 1,
            "vr_name": 'Router-0',
            "local_dev": 'br-0',
            "x": 583,
            "y": 117,
            "width": 10,
            "height": 10,
            "flags": 257,
            "subnets": '5.0.0.0/16',
            "nexthop":'10.40.11.202',
            "dhcp_lease_time": 43200,
            "dhcp_dns":'0.0.0.0',
            "interface_cost": 1,
            "rip_metric": 1,
            "vrrp_ip_prefix": 25,
            "vrrp_id":1,
            "vrrp_priority":100,
            "vrrp_interval":1
        }   
        super().json_post(req_url_add_vrcx, data_add_vrcx, debug_ = self.debug)

        #add_vrcx2
        req_url_add_vrcx2= "cli-json/add_vrcx2"
        data_add_vrcx2 = {
            "shelf": 1,
            "resource": 1,
            "vr_name": 'Router-0',
            "local_dev": 'br-0',
        }   
        super().json_post(req_url_add_vrcx2, data_add_vrcx2, debug_ = self.debug)
        


    def start(self, sta_list, print_pass, print_fail):
        self.station_profile.admin_up(1)
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
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "cli-json/set_port"
            # print(sta_name)
            self.json_post(url, data)

    def cleanup(self, sta_list):
        self.station_profile.cleanup(self.resource, sta_list)
        LFUtils.wait_until_ports_disappear(resource_id=self.resource, base_url=self.lfclient_url, port_list=sta_list,
                                           debug=self.debug)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000)
    ip_test = L3LANtoWAN(lfjson_host, lfjson_port, ssid="jedway-open-1", password="[BLANK]",
                       security="open", sta_list=station_list,_debug_on=False)
    #ip_test.cleanup(station_list)
    ip_test.timeout = 60
    ip_test.build()
    if not ip_test.passes():
        print(ip_test.get_fail_message())
        exit(1)
    #ip_test.start(station_list, False, False)
    #ip_test.stop()
    #if not ip_test.passes():
    #    print(ip_test.get_fail_message())
    #    exit(1)
    #time.sleep(30)
    #ip_test.cleanup(station_list)
    #if ip_test.passes():
     #   print("Full test passed, all stations associated and got IP")


if __name__ == "__main__":
    main()