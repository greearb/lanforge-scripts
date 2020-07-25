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
class TIPStationPowersave(LFCliBase):
    def __init__(self, host, port, ssid, security, password,
                 normal_station_list_=None,
                 powersave_station_list_=None,
                 side_a_min_rate=56000,
                 side_b_min_rate=56000,
                 side_a_max_rate=0,
                 side_b_max_rate=0,
                 pdu_size = 1000,
                 prefix="00000",
                 traffic_duration_="5m",
                 pause_duration_="2s",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.normal_sta_list = normal_station_list_
        self.powersave_sta_list = powersave_station_list_
        self.prefix = prefix
        self.debug = _debug_on
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=False, halt_on_error_=True)
        #upload
        self.cx_prof_upload = realm.L3CXProfile(self.host, self.port, self.local_realm, 
                                                side_a_min_bps=side_a_min_rate,
                                                side_b_min_bps=0,
                                                side_a_max_bps=side_a_max_rate,
                                                side_b_max_bps=0,
                                                side_a_min_pdu=pdu_size,
                                                side_a_max_pdu=pdu_size,
                                                side_b_min_pdu=pdu_size,
                                                side_b_max_pdu=pdu_size,
                                                debug_=False)
        
        #download
        self.cx_prof_download = realm.L3CXProfile(self.host, self.port, self.local_realm,
                                                  side_a_min_bps=0,
                                                  side_b_min_bps=side_b_min_rate,
                                                  side_a_max_bps=0,
                                                  side_b_max_bps=side_b_max_rate,
                                                  side_a_min_pdu=pdu_size,
                                                  side_a_max_pdu=pdu_size,
                                                  side_b_min_pdu=pdu_size,
                                                  side_b_max_pdu=pdu_size,
                                                  debug_=False)
        self.test_duration = traffic_duration_
        self.pause_duration = pause_duration_
        self.sta_powersave_enabled_profile = realm.StationProfile(self.lfclient_url, self.local_realm,
                                                                  ssid=self.ssid,
                                                                  ssid_pass=self.password,
                                                                  security=self.security,
                                                                  number_template_=self.prefix,
                                                                  mode=0,
                                                                  up=True,
                                                                  dhcp=True,
                                                                  debug_=False)
        self.sta_powersave_disabled_profile = realm.StationProfile(self.lfclient_url, self.local_realm,
                                                                   ssid=self.ssid,
                                                                   ssid_pass=self.password,
                                                                   security=self.security,
                                                                   number_template_=self.prefix,
                                                                   mode=0,
                                                                   up=True,
                                                                   dhcp=True,
                                                                   debug_=False)
        self.new_monitor = realm.WifiMonitor(self.lfclient_url, self.local_realm,debug_= _debug_on)


    def build(self):
        self.sta_powersave_disabled_profile.use_security("open", ssid=self.ssid, passwd=self.password)
        self.sta_powersave_disabled_profile.set_number_template(self.prefix)
        self.sta_powersave_disabled_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.sta_powersave_disabled_profile.set_command_param("set_port", "report_timer", 5000)
        self.sta_powersave_disabled_profile.set_command_flag("set_port", "rpt_timer", 1)

        self.sta_powersave_enabled_profile.use_security("open", ssid=self.ssid, passwd=self.password)
        self.sta_powersave_enabled_profile.set_number_template(self.prefix)
        self.sta_powersave_enabled_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.sta_powersave_enabled_profile.set_command_param("set_port", "report_timer", 5000)
        self.sta_powersave_enabled_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.sta_powersave_enabled_profile.set_command_flag("add_sta", "power_save_enable", 1)

        self.new_monitor.create(resource_=1, channel=157, radio_= "wiphy1", name_="moni0")
        self.sta_powersave_disabled_profile.create(resource=1, radio="wiphy0", sta_names_=self.normal_sta_list, debug=False)
       # station_channel = self.json_get("/port/1/%s/%s")
       # pprint.pprint(station_channel)

        self._pass("PASS: Stations created")
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
        cx_list = self.json_get("/endp/list?fields=name,rx+bytes", debug_=False)
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
        """
        This method is intended to start the monitor, the normal station (without powersave),
        and the remaining power save stations. The powersave stations will transmit for tx duration,
        pause, then the AP will pass along upstream traffic. This upstream traffic (download) should
        express a beacon before actually delivering a buffer full of traffic in order to alert the
        station it should wake up for incomming traffic.
        :param print_pass:
        :param print_fail:
        :return:
        """
        cur_time = datetime.datetime.now()
        end_time = self.local_realm.parse_time(self.test_duration) + cur_time
        #admin up on new monitor
        self.new_monitor.admin_up()
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d-%H%M%S")
        curr_mon_name = self.new_monitor.monitor_name
        #("date and time: ",date_time)	
        self.new_monitor.start_sniff("/home/lanforge/Documents/"+curr_mon_name+"-"+date_time+".cap")
        time.sleep(0.05)
        self.sta_powersave_disabled_profile.admin_up(resource=1)
        self.sta_powersave_enabled_profile.admin_up(resource=1)

        self.cx_prof_download.
        # self.__set_all_cx_state("RUNNING")
        # while cur_time < end_time:
        #     #DOUBLE CHECK
        #     interval_time = cur_time + datetime.timedelta(minutes=1)
        #     while cur_time < interval_time:
        #         cur_time = datetime.datetime.now()
        #         time.sleep(1)


    def stop(self):
        #switch off new monitor
        self.new_monitor.admin_down()
        self.__set_all_cx_state("STOPPED")
        for sta_name in self.normal_sta_list:
            data = LFUtils.portDownRequest(1, sta_name)
            url = "json-cli/set_port"
            self.json_post(url, data)

   
    def cleanup(self):
        self.new_monitor.cleanup()
        self.cx_prof_download.cleanup()
        self.cx_prof_upload.cleanup()
        self.sta_powersave_disabled_profile.cleanup(resource=1, desired_stations=self.normal_sta_list)
            

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    #station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)    
    normal_station_list = ["sta0000" ]
    powersave_station_list = ["sta0001","sta0002","sta0003","sta0004"]
    ip_powersave_test = TIPStationPowersave(lfjson_host, lfjson_port,
                                            ssid="jedway-open",
                                            security="open",
                                            password="[BLANK]",
                                            normal_station_list_=normal_station_list,
                                            powersave_station_list_=powersave_station_list,
                                            side_a_min_rate=20000,
                                            side_b_min_rate=20000,
                                            side_a_max_rate=0,
                                            side_b_max_rate=0,
                                            prefix="00000",
                                            traffic_duration_="5s",
                                            _debug_on=False,
                                            _exit_on_error=True,
                                            _exit_on_fail=True)
    ip_powersave_test.cleanup()       
    ip_powersave_test.build()
    ip_powersave_test.start()
    ip_powersave_test.stop()
    ip_powersave_test.cleanup()

if __name__ == "__main__":
    
    main()

