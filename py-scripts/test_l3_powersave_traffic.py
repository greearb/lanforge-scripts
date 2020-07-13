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
                 side_b_max_rate=0, pdu_size = 1000, prefix="00000", test_duration="5m",
                _debug_on=False, _exit_on_error=False, _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.sta_list = station_list
        self.prefix = prefix
        self.debug = _debug_on
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=False, halt_on_error_=True)
        #upload
        self.cx_prof_upload = realm.L3CXProfile(self.host, self.port, self.local_realm, 
                                            side_a_min_bps=side_a_min_rate,side_b_min_bps=0, 
                                            side_a_max_bps=side_a_max_rate,side_b_max_bps=0, 
                                            side_a_min_pdu=pdu_size, side_a_max_pdu=pdu_size, 
                                            side_b_min_pdu=0, side_b_max_pdu=0, debug_=False)
        
        #download
        self.cx_prof_download = realm.L3CXProfile(self.host, self.port, self.local_realm, 
                                            side_a_min_bps=0, side_b_min_bps=side_b_min_rate, 
                                            side_a_max_bps=0,side_b_max_bps=side_b_max_rate, 
                                            side_a_min_pdu=0, side_a_max_pdu=0,
                                            side_b_min_pdu=pdu_size,side_b_max_pdu=pdu_size, debug_=False)
        self.test_duration = test_duration
        self.station_profile = realm.StationProfile(self.lfclient_url, self.local_realm, ssid=self.ssid, ssid_pass=self.password,
                                                    security=self.security, number_template_=self.prefix, mode=0, up=True,
                                                    dhcp=True,
                                                    debug_=False)
        self.newMonitor = realm.WifiMonitor(self.lfclient_url, self.local_realm,debug_= _debug_on)
        self.station_profile.admin_up(resource=1)



    def build(self):
 
        self.station_profile.use_wpa2(False, self.ssid, self.password)
        self.station_profile.set_number_template(self.prefix)
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.set_command_flag("add_sta", "power_save_enable", 1)

        self.station_profile.create(resource=1, radio="wiphy0", sta_names_=self.sta_list, debug=False)
        self.newMonitor.create(resource_=1, radio_= "wiphy1", name_="moni_powersave")
        
        self._pass("PASS: Station builds finished")
        temp_sta_list = []
        for name in list(self.local_realm.station_list()):
            if "sta" in list(name)[0]:
                temp_sta_list.append(list(name)[0])

        #print("temp_sta_list", temp_sta_list)
        self.cx_prof_upload.name_prefix = "UDP_up"
        self.cx_prof_download.name_prefix = "UDP_down"
        print("Creating upload cx profile ")
        self.cx_prof_upload.create(endp_type="lf_udp", side_a=temp_sta_list, side_b="1.eth1", sleep_time=.05)
        print("Creating download cx profile")
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


    def start(self, print_pass=False, print_fail = False):
        #start one test, measure
        #start second test, measure
        cur_time = datetime.datetime.now()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        #admin up on new monitor
        self.newMonitor.admin_up()
        self.__set_all_cx_state("RUNNING")

        while cur_time < end_time:
            #DOUBLE CHECK  
            interval_time = cur_time + datetime.timedelta(minutes=1)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                time.sleep(1)


    def stop(self):
        #switch off new monitor
        self.newMonitor.admin_down()
        self.__set_all_cx_state("STOPPED")
        for sta_name in self.sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            self.json_post(url, data)

   
    def cleanup(self):
        self.newMonitor.cleanup()
        self.cx_prof_download.cleanup()
        self.cx_prof_upload.cleanup()
        self.station_profile.cleanup(resource=1,desired_stations=self.sta_list)     
            

def main():

    lfjson_host = "localhost"
    lfjson_port = 8080
    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)    
    ip_powersave_test = L3PowersaveTraffic(lfjson_host, lfjson_port, ssid = "jedway-open" , security = "open", 
                        password ="[BLANK]", station_list = station_list , side_a_min_rate=2000, side_b_min_rate=2000, side_a_max_rate=0,
                        side_b_max_rate=0, prefix="00000", test_duration="30s",
                        _debug_on=False, _exit_on_error=True, _exit_on_fail=True)
    ip_powersave_test.cleanup()       
    ip_powersave_test.build()
    ip_powersave_test.start()
    ip_powersave_test.stop()
    ip_powersave_test.cleanup()

if __name__ == "__main__":
    #main(sys.argv[1:])
    main()

