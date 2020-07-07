#!/usr/bin/env python3
import sys
import pprint
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import LFUtils
import realm
import time
import datetime

#Currently, this test can only be applied to UDP connections
class L3PowersaveTraffic(LFCliBase):

    #attributes: station list, side_a_min_rate (and max_rate), side_b_min_rate (and max_rate),
    def __init__(self, host, port, ssid, security, password, station_list, side_a_min_rate=56, side_b_min_rate=56, side_a_max_rate=0,
                 side_b_max_rate=0, prefix="00000", test_duration="5m",
                _debug_on=False, _exit_on_error=False, _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.sta_list = station_list
        self.prefix = prefix
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        #upload
        self.cx_prof_upload = realm.L3CXProfile(self.host, self.port, self.local_realm, side_a_min_bps=side_a_min_rate,
                                            side_b_min_bps=0, side_a_max_bps=side_a_max_rate,
                                            side_b_max_bps=0, debug_=True)
        #download
        self.cx_prof_download = realm.L3CXProfile(self.host, self.port, self.local_realm, side_a_min_bps=0,
                                            side_b_min_bps=side_b_min_rate, side_a_max_bps=0,
                                            side_b_max_bps=side_b_max_rate, debug_=True)
        self.test_duration = test_duration
        self.station_profile = realm.StationProfile(self.lfclient_url, ssid=self.ssid, ssid_pass=self.password,
                                                    security=self.security, number_template_=self.prefix, mode=0, up=True,
                                                    dhcp=True,
                                                    debug_=False)



    def build(self,UorD):
        #upload would set TXBPs on A side of endpoint
        #download would set TXBps on B side of endpoint
        #build 
        print("Creating stations for" + UorD +  "traffic") 
        self.station_profile.use_wpa2(True, self.ssid, self.password)
        self.station_profile.set_number_template(self.prefix)
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.set_command_flag("add_sta", "power_save_enable", 1)
        self.station_profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)
        self._pass("PASS: Station build for" + UorD + "finished")
        temp_sta_list = []
        for name in list(self.local_realm.station_list()):
            if "sta" in list(name)[0]:
                temp_sta_list.append(list(name)[0])
        print("temp_sta_list", temp_sta_list)
        self.cx_prof_upload.name_prefix = "UDP_up"
        self.cx_prof_download.name_prefix = "UDP_down"
        print("Beginning create upload")
        self.cx_prof_upload.create(endp_type="lf_udp", side_a=temp_sta_list, side_b="1.eth1", sleep_time=.05)  #create 2 cx profiles
        print("Beginning create download")
        self.cx_prof_download.create(endp_type="lf_udp", side_a=temp_sta_list, side_b="1.eth1", sleep_time=.05)                          

    def start(self):
        #start one test, measure
        #start second test, measure
        pass

    def stop(self):
        pass
        
    
    def cleanup(self):
        """print("Cleaning up stations")
        port_list = self.local_realm.station_list()
        sta_list = []
        for item in list(port_list):
            # print(list(item))
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
            self.json_post(req_url, data)

        cx_list = list(self.local_realm.cx_list())
        if cx_list is not None:
            print("Cleaning up cxs")
            for cx_name in cx_list:
                if cx_name != 'handler' or cx_name != 'uri':
                    req_url = "cli-json/rm_cx"
                    data = {
                        "test_mgr": "default_tm",
                        "cx_name": cx_name
                    }
                    self.json_post(req_url, data)

        print("Cleaning up endps")
        endp_list = self.json_get("/endp")
        if endp_list is not None:
            endp_list = list(endp_list['endpoint'])
            for endp_name in range(len(endp_list)):
                name = list(endp_list[endp_name])[0]
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": name
                }
                self.json_post(req_url, data) """
        pass
        
        

def main():
    #param for TCP or UDP for tests
    lfjson_host = "localhost"
    lfjson_port = 8080
    #creates object of class L3PowersaveTraffic, inputs rates for upload and download
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)
    ip_powersave_test = L3PowersaveTraffic(lfjson_host, lfjson_port, ssid = "jedway-open" , security = "open", 
                        password ="[BLANK]", station_list = station_list , side_a_min_rate=56, side_b_min_rate=56, side_a_max_rate=0,
                        side_b_max_rate=0, prefix="00000", test_duration="5m",
                        _debug_on=True, _exit_on_error=True, _exit_on_fail=True)
    #ip_powersave_test.cleanup()
    ip_powersave_test.build("upload")
    # ip_powersave_test.start("upload")
    #ip_powersave_test.start("download")
    #ip_powersave_test.cleanup()

if __name__ == "__main__":
    #main(sys.argv[1:])
    main()

