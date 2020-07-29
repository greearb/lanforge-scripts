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
    def __init__(self, host, port,
                 ssid=None,
                 security="open",
                 password="[BLANK]",
                 resource_=1,
                 channel_=0,
                 normal_station_list_=None,
                 normal_station_radio_=None,
                 powersave_station_list_=None,
                 powersave_station_radio_=None,
                 monitor_name_=None,
                 monitor_radio_=None,
                 side_a_min_rate_=56000,
                 side_b_min_rate_=56000,
                 side_a_max_rate_=0,
                 side_b_max_rate_=0,
                 pdu_size_=1000,
                 traffic_duration_="5s",
                 pause_duration_="2s",
                 debug_on_=False,
                 exit_on_error_=False,
                 exit_on_fail_=False):
        super().__init__(host, port, _debug=debug_on_, _halt_on_error=exit_on_error_, _exit_on_fail=exit_on_fail_)
        self.resource = resource_
        if (channel_ == 0):
            raise ValueError("Please set your radio channel")
        self.channel = channel_
        self.monitor_name = monitor_name_
        self.monitor_radio = monitor_radio_
        self.host = host
        self.port = port
        self.ssid = ssid
        self.security = security
        self.password = password
        self.normal_sta_list = normal_station_list_
        self.normal_sta_radio = normal_station_radio_
        self.powersave_sta_list = powersave_station_list_
        self.powersave_sta_radio = powersave_station_radio_
        self.debug = debug_on_
        self.local_realm = realm.Realm(lfclient_host=self.host,
                                       lfclient_port=self.port,
                                       debug_=self.debug,
                                       halt_on_error_=self.exit_on_error)

        # background traffic
        self.cx_background = self.local_realm.new_l3_cx_profile()
        self.cx_background.side_a_min_bps = side_a_min_rate_
        self.cx_background.side_b_min_bps = side_a_min_rate_
        self.cx_background.side_a_max_bps = side_a_max_rate_
        self.cx_background.side_b_max_bps = side_a_min_rate_

        #upload
        self.cx_prof_upload = self.local_realm.new_l3_cx_profile()
        self.cx_prof_upload.side_a_min_bps = side_a_min_rate_
        self.cx_prof_upload.side_b_min_bps = 0
        self.cx_prof_upload.side_a_max_bps = side_a_max_rate_
        self.cx_prof_upload.side_b_max_bps = 0

        self.cx_prof_upload.side_a_min_pdu = pdu_size_
        self.cx_prof_upload.side_a_max_pdu = 0
        self.cx_prof_upload.side_b_min_pdu = pdu_size_
        self.cx_prof_upload.side_b_max_pdu = 0,

        #download
        self.cx_prof_download = self.local_realm.new_l3_cx_profile()
        self.cx_prof_download.side_a_min_bps = 0
        self.cx_prof_download.side_b_min_bps = side_b_min_rate_
        self.cx_prof_download.side_a_max_bps = 0
        self.cx_prof_download.side_b_max_bps = side_b_max_rate_

        self.cx_prof_download.side_a_min_pdu = pdu_size_
        self.cx_prof_download.side_a_max_pdu = 0
        self.cx_prof_download.side_b_min_pdu = pdu_size_
        self.cx_prof_download.side_b_max_pdu = 0

        self.test_duration = traffic_duration_
        self.pause_duration = pause_duration_
        self.sta_powersave_enabled_profile = self.local_realm.new_station_profile()
        self.sta_powersave_disabled_profile = self.local_realm.new_station_profile()
        self.wifi_monitor_profile = self.local_realm.new_wifi_monitor_profile()



    def build(self):
        self.sta_powersave_disabled_profile.use_security("open", ssid=self.ssid, passwd=self.password)
        self.sta_powersave_disabled_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.sta_powersave_disabled_profile.set_command_param("set_port", "report_timer", 5000)
        self.sta_powersave_disabled_profile.set_command_flag("set_port", "rpt_timer", 1)

        self.sta_powersave_enabled_profile.use_security("open", ssid=self.ssid, passwd=self.password)
        self.sta_powersave_enabled_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.sta_powersave_enabled_profile.set_command_param("set_port", "report_timer", 5000)
        self.sta_powersave_enabled_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.sta_powersave_enabled_profile.set_command_flag("add_sta", "power_save_enable", 1)

        self.wifi_monitor_profile.create(resource_=self.resource,
                                         channel=self.channel,
                                         radio_=self.monitor_radio,
                                         name_=self.monitor_name)
        LFUtils.wait_until_ports_appear(resource_id=1,
                                        base_url=self.local_realm.lfclient_url,
                                        port_list=[self.monitor_name])
        time.sleep(0.2)
        mon_j = self.json_get("/port/1/%s/%s"%(self.resource, self.monitor_name))
        if ("interface" not in mon_j):
            raise ValueError("No monitor found")

        self.sta_powersave_disabled_profile.create(resource=1,
                                                   radio=self.normal_sta_radio,
                                                   sta_names_=self.normal_sta_list,
                                                   debug=self.debug)

        self.sta_powersave_enabled_profile.create(resource=1,
                                                   radio=self.powersave_sta_radio,
                                                   sta_names_=self.powersave_sta_list,
                                                   debug=self.debug)
        temp_sta_map = {}
        for name in list(self.local_realm.station_list()):
            if (name in self.sta_powersave_disabled_profile.station_names) \
                    or (name in self.sta_powersave_enabled_profile.station_names):
                temp_sta_map[name]=1
        if len(temp_sta_map) == (len(self.sta_powersave_disabled_profile.station_names) + len(self.sta_powersave_enabled_profile.station_names)):
            self._pass("Stations created")
        else:
            self._fail("Not all stations created")

        print("Creating background cx profile ")
        self.cx_background.name_prefix="udp_bg"
        self.cx_background.create(endp_type="lf_udp",
                                  side_a=self.normal_sta_list,
                                  side_b="1.eth1",
                                  sleep_time=.05)

        print("Creating upload cx profile ")
        self.cx_prof_upload.name_prefix = "udp_up"
        self.cx_prof_upload.create(endp_type="lf_udp",
                                   side_a=self.powersave_sta_list,
                                   side_b="1.eth1",
                                   sleep_time=.05)

        print("Creating download cx profile")
        self.cx_prof_download.name_prefix = "udp_down"
        self.cx_prof_download.create(endp_type="lf_udp",
                                     side_a=self.powersave_sta_list,
                                     side_b="1.eth1",
                                     sleep_time=.05)

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

        #admin up on new monitor
        self.wifi_monitor_profile.admin_up()
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d-%H%M%S")
        curr_mon_name = self.wifi_monitor_profile.monitor_name
        pcap_file = "/home/lanforge/Documents/%s-%s.pcap"%(curr_mon_name, date_time)
        self.wifi_monitor_profile.start_sniff(pcap_file)
        time.sleep(0.05)

        self.sta_powersave_disabled_profile.admin_up(resource=1)
        self.sta_powersave_enabled_profile.admin_up(resource=1)

        LFUtils.waitUntilPortsAdminUp(resource_id=self.resource,
                                      base_url=self.local_realm.lfclient_url,
                                      port_list=self.sta_powersave_disabled_profile.station_names + self.sta_powersave_enabled_profile.station_names)
        self.cx_prof_background.start_cx()
        print("Upload starts at: %d"%time.time())
        self.cx_prof_upload.start_cx()
        time.sleep(float(self.test_duration))
        self.cx_prof_upload.stop_cx()
        print("Upload ends at: %d"%time.time())
        time.sleep(float(self.pause_duration))
        # here is where we should sleep long enough for station to go to sleep
        print("Download begins at: %d"%time.time())
        self.cx_prof_download.start_cx()
        time.sleep(float(self.test_duration))
        self.cx_prof_download.stop_cx()


    def stop(self):
        #switch off new monitor
        self.wifi_monitor_profile.admin_down()
        self.cx_prof_download.stop_cx()
        self.cx_prof_upload.stop_cx()
        self.sta_powersave_enabled_profile.admin_down()
        self.sta_powersave_disabled_profile.admin_down()

    def cleanup(self):
        self.wifi_monitor_profile.cleanup(resource_=self.resource, desired_ports=[self.monitor_name])
        self.cx_prof_download.cleanup()
        self.cx_prof_upload.cleanup()
        self.sta_powersave_enabled_profile.cleanup(resource=self.resource, desired_stations=self.powersave_sta_list)
        self.sta_powersave_disabled_profile.cleanup(resource=self.resource, desired_stations=self.normal_sta_list)

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    #station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=4, padding_number_=10000)    
    normal_station_list = ["sta1000" ]
    powersave_station_list = ["sta0001"] #,"sta0002","sta0003","sta0004"]
    ip_powersave_test = TIPStationPowersave(lfjson_host, lfjson_port,
                                            ssid="jedway-open",
                                            channel_=157,
                                            normal_station_list_=normal_station_list,
                                            normal_station_radio_="wiphy0",
                                            powersave_station_list_=powersave_station_list,
                                            powersave_station_radio_="wiphy0",
                                            monitor_name_="moni0",
                                            monitor_radio_="wiphy1",
                                            side_a_min_rate_=56000,
                                            side_b_min_rate_=56000,
                                            traffic_duration_="5s",
                                            pause_duration_="2s",
                                            debug_on_=True,
                                            exit_on_error_=False,
                                            exit_on_fail_=True)
    ip_powersave_test.cleanup()
    ip_powersave_test.build()
    ip_powersave_test.start()
    ip_powersave_test.stop()
    ip_powersave_test.cleanup()

if __name__ == "__main__":
    
    main()

