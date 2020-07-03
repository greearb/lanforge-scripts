#!/usr/bin/env python3

import sys
import pprint
import os


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('.'),'py-json'))

pprint.pprint(sys.path)
import argparse
#import LANforge
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm 
from realm import Realm
import time


class IPv4Test(LFCliBase):
    def __init__(self, host, port, ssid, security, password, num_stations=0, prefix="00000", _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        #initializes LFCliBase init 
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.num_stations = num_stations
        self.timeout = 120
        self.prefix = prefix
        self.debug = _debug_on
        self.local_realm = Realm(lfclient_host=host,lfclient_port=port) 
        self.profile = self.local_realm.new_station_profile()


    def check_association(self, sta_list, print_pass, print_fail):
        """
        Usage:

        Args:

        Returns:

        TODO: Currently N/A
        """
     
        associated_map = {}
        ip_map = {}

        for sec in range(self.timeout):
                      
            for sta_name in sta_list:

                sta_status = self.json_get("port/1/1/" + sta_name+"?fields=port,alias,ip,ap")
                pprint.pprint(sta_status)
                
                if (sta_status is None) or (sta_status['interface'] is None) or (sta_status['interface']['ap'] is None):
                    continue

                if len(sta_status['interface']['ap']) == 17 and sta_status['interface']['ap'][-3] == ':' :
                    #print("Associated", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map[sta_name] = 1

                if sta_status['interface']['ip'] != '0.0.0.0':
                    #print("IP", sta_name, sta_status['interface']['ap'], sta_status['interface']['ip'])
                    associated_map[sta_name] = 1
                    ip_map[sta_name] = 1
            if len(sta_list) == len(ip_map) and len(sta_list) == len(associated_map):
                break
            
            time.sleep(1)
        
        if len(sta_list) == len(ip_map) and len(sta_list) == len(associated_map):
            self._pass("PASS: All stations associated with IP", print_pass)
        else:
            self._fail("FAIL: Not all stations able to associate/get IP", print_fail)

        return self.passes()

    def cleanup(self):
        """
        Usage:

        Args:

        Returns:

        TODO: Currently N/A
        """
        port_list = self.local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            #print(list(item))
            if "sta" in list(item)[0]:
                sta_list.append(self.local_realm.name_to_eid(list(item)[0])[2])

        for sta_name in sta_list:
            req_url = "cli-json/rm_vlan"
            data = {
                "shelf": 1,
                "resource": 1,
                "port": sta_name
            }
            # print(data)
            super().json_post(req_url, data)

    def start(self):
        self.profile.admin_up(resource=1)
        LFUtils.waitUntilPortsAdminUp(resource_id=1, base_url=self.lfclient_url, port_list = self.profile.station_names)
        self.check_association(sta_list = self.profile.station_names, print_pass = True, print_fail = True)

    def stop(self):
        pass        

    def build(self):
        """
        Usage:

        Args:

        Returns:

        TODO: Currently N/A

        """
        super().clear_test_results()
        print("Cleaning up old stations")
        self.cleanup()
        sta_list = []
        self.profile.use_wpa2(False, self.ssid)

        print("Creating stations")
        self.profile.create(resource=1, radio="wiphy0", num_stations=self.num_stations, debug=True)
        LFUtils.wait_until_ports_appear(resource_id=1, base_url=self.lfclient_url, port_list=self.profile.station_names, debug=False)
        self._pass("stations created")

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    ip_test = IPv4Test(lfjson_host, lfjson_port, ssid="jedway-open", password="[BLANK]", num_stations=1,
                       security="open")
    ip_test.cleanup()
    ip_test.timeout = 60
    ip_test.build()

    if not ip_test.passes() : 
        print(ip_test.get_fail_message())
        exit(1)
    ip_test.start()

    if not ip_test.passes() : 
        print(ip_test.get_fail_message())
        exit(1)
    sleep(ip_test.timeout)
    ip_test.stop()

    if not ip_test.passes() : 
        print(ip_test.get_fail_message())
        exit(1)


    ip_test.run()
    print("Full Test Passed: %s" % ip_test.run_test_full())
    print("Range Test Passed: %s" % ip_test.run_test_custom("00005", "00009"))
    print("Custom Test Passed: %s" % ip_test.run_test_custom(sta_list=["sta00001", "sta00003", "sta00009", "sta00002"]))

    ip_test.cleanup()


if __name__ == "__main__":
    main()
