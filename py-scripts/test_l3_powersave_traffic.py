#!/usr/bin/env python3
import sys
import pprint
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'),'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import LFUtils
import realm
import time
import datetime

#Currently, this test can only be applied to UDP connections
class L3PowersaveTraffic(LFCliBase):

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
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=True, halt_on_error_=True)
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
        self.station_profile.admin_up(resource=1)



    def build(self):
        #upload would set TXBPs on A side of endpoint
        #download would set TXBps on B side of endpoint
        #build 
        self.station_profile.use_wpa2(False, self.ssid, self.password)
        self.station_profile.set_number_template(self.prefix)
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.set_command_flag("add_sta", "power_save_enable", 1)

        self.station_profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)
        
        self._pass("PASS: Station builds finished")
        temp_sta_list = []
        for name in list(self.local_realm.station_list()):
            if "sta" in list(name)[0]:
                temp_sta_list.append(list(name)[0])

        print("temp_sta_list", temp_sta_list)
        self.cx_prof_upload.name_prefix = "UDP_up"
        self.cx_prof_download.name_prefix = "UDP_down"
        print("Beginning create upload")
        self.cx_prof_upload.create(endp_type="lf_udp", side_a=temp_sta_list, side_b="1.eth1", sleep_time=.05)

        print("Beginning create download")
        self.cx_prof_download.create(endp_type="lf_udp", side_a=temp_sta_list, side_b="1.eth1", sleep_time=.05)

    def __set_all_cx_state(self, state, sleep_time=5):
        print("Setting CX States to %s" % state)
        cx_list = list(self.local_realm.cx_list())
        for cx_name in cx_list:
            req_url = "cli-json/set_cx_state"
            data = {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": state
            }
            self.json_post(req_url, data)
        time.sleep(sleep_time)


    def __get_rx_values(self):
        cx_list = self.json_get("/endp/list?fields=name,rx+bytes", debug_=True)
        #print("==============\n", cx_list, "\n==============")
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
            for item in old_list.items():
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



    def start(self, print_pass=False, print_fail = False):
        #start one test, measure
        #start second test, measure
        cur_time = datetime.datetime.now()
        old_cx_rx_values = self.__get_rx_values()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        self.__set_all_cx_state("RUNNING")
        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)

            new_cx_rx_values = self.__get_rx_values()
            print(old_cx_rx_values, new_cx_rx_values)
            print("\n-----------------------------------")
            print(cur_time, end_time, cur_time + datetime.timedelta(minutes=1))
            print("-----------------------------------\n")
            expected_passes += 1
            if self.__compare_vals(old_cx_rx_values, new_cx_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
                break
            old_cx_rx_values = new_cx_rx_values
            cur_time = datetime.datetime.now()

    def stop(self):
        self.__set_all_cx_state("STOPPED")
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            self.json_post(url, data)


    def cleanup(self):
        print("Cleaning up stations")
        port_list = self.local_realm.station_list()
        sta_list = []
        if sta_list is not None:
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
        not_cx = ['warnings', 'errors', 'handler', 'uri','items']
        if cx_list is not None:
            print("Cleaning up cxs")
            for cx_name in cx_list:
                if cx_name in not_cx:
                    continue
                req_url = "cli-json/rm_cx"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": cx_name
                }
                self.json_post(req_url, data)

        print("Cleaning up endps")
        endp_list = self.json_get("/endp")
        print("The endpoint list about to be printed")
        print(endp_list)
        print("The endpoint list was just printed")
        if endp_list is not None:
            endp_list = list(endp_list['endpoint'])
            for endp_name in range(len(endp_list)):
                name = list(endp_list[endp_name])[0]
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": name
                }
                self.json_post(req_url, data)


        LFUtils.wait_until_ports_disappear(resource=1,base_url=self.lfclient_url, port_list=self.local_realm.station_list(), debug=self.local_realm.debug)
             

def main():
    #param for TCP or UDP for tests
    lfjson_host = "localhost"
    lfjson_port = 8080
    #creates object of class L3PowersaveTraffic, inputs rates for upload and download
    #station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)    
    ip_powersave_test = L3PowersaveTraffic(lfjson_host, lfjson_port, ssid = "jedway-open" , security = "open", 
                        password ="[BLANK]", station_list = ["sta01", "sta02"] , side_a_min_rate=2000, side_b_min_rate=2000, side_a_max_rate=0,
                        side_b_max_rate=0, prefix="00000", test_duration="30s",
                        _debug_on=True, _exit_on_error=True, _exit_on_fail=True)
   # ip_powersave_test.cleanup()               
    ip_powersave_test.build()
    if not ip_powersave_test.passes():
        print(ip_powersave_test.get_fail_message())
        exit(1)
    print("we've passed the build test")
    ip_powersave_test.start(True, True)
    #ip_powersave_test.stop()
    if not ip_powersave_test.passes():
        print(ip_powersave_test.get_fail_message())
        exit(1)
    time.sleep(30)
    if ip_powersave_test.passes():
        print("Full test passed, all endpoints had increased bytes-rd throughout test duration")
    ip_powersave_test.cleanup()

if __name__ == "__main__":
    #main(sys.argv[1:])
    main()

