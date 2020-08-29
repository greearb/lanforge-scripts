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
import datetime
import subprocess
import re
import csv
import random

class L3VariableTimeLongevity(LFCliBase):
    def __init__(self, host, port, endp_types, args, tos, side_b, radio_name_list, number_of_stations_per_radio_list,
                 ssid_list, ssid_password_list, ssid_security_list, station_lists, name_prefix, debug_on, outfile,
                 reset_port_enable_list,
                 reset_port_time_min_list,
                 reset_port_time_max_list,
                 side_a_min_rate=56000, side_a_max_rate=0,
                 side_b_min_rate=56000, side_b_max_rate=0,
                 number_template="00", test_duration="256s",
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.tos = tos.split()
        self.endp_types = endp_types.split()
        self.side_b = side_b
        self.ssid_list = ssid_list
        self.ssid_password_list = ssid_password_list
        self.station_lists = station_lists       
        self.ssid_security_list = ssid_security_list
        self.reset_port_enable_list = reset_port_enable_list
        self.reset_port_time_min_list = reset_port_time_min_list
        self.reset_port_time_max_list = reset_port_time_max_list
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.radio_name_list = radio_name_list
        self.number_of_stations_per_radio_list =  number_of_stations_per_radio_list
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.multicast_profile = self.local_realm.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-";
        self.station_profiles = []
        self.args = args
        self.outfile = outfile
        self.csv_started = False
        self.ts = int(time.time())

        # Some checking on the duration
        #self.local_realm.parse_time(self.test_duration)
        #if (    (radio_info_dict['reset_port_time_min'] >= args.test_duration)  
        #    or  (radio_info_dict['reset_port_time_max'] >= args.test_duration)):
        #    print("port reset times min {} max {} mismatched with test duration {}"\
        #        .format(radio_info_dict['reset_port_time_min'],radio_info_dict['reset_port_time_max'],args.test_duration)))
        #    exit(1)


        # Full spread-sheet data
        if self.outfile is not None:
            self.csv_file = open(self.outfile, "w") 
            self.csv_writer = csv.writer(self.csv_file, delimiter=",")
        
        for (radio_, ssid_, ssid_password_, ssid_security_,\
            reset_port_enable_, reset_port_time_min_, reset_port_time_max_) \
            in zip(radio_name_list, ssid_list, ssid_password_list, ssid_security_list,\
            reset_port_enable_list, reset_port_time_min_list, reset_port_time_max_list):
            self.station_profile = self.local_realm.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_
            self.station_profile.ssid_pass = ssid_password_
            self.station_profile.security = ssid_security_
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = 0
            self.station_profile.set_reset_extra(reset_port_enable=reset_port_enable_,\
                test_duration=self.local_realm.duration_time_to_seconds(self.test_duration),\
                reset_port_min_time=self.local_realm.duration_time_to_seconds(reset_port_time_min_),\
                reset_port_max_time=self.local_realm.duration_time_to_seconds(reset_port_time_max_))
            self.station_profiles.append(self.station_profile)
        
        self.multicast_profile.host = self.host
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def __get_rx_values(self):
        endp_list = self.json_get("endp?fields=name,rx+bytes,rx+drop+%25", debug_=False)
        endp_rx_drop_map = {}
        endp_rx_map = {}
        our_endps = {}
        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e;
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e;
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, value in endp_name.items():
                    if item in our_endps:
                        for value_name, value_rx in value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value_rx
                        for value_name, value_rx_drop in value.items():
                            if value_name == 'rx drop %':
                                endp_rx_drop_map[item] = value_rx_drop

        return endp_rx_map, endp_rx_drop_map

    def __record_rx_dropped_percent(self,rx_drop_percent):

        csv_rx_drop_percent_data = [self.ts,'rx_drop_percent']
        for key in [key for key in rx_drop_percent if "mtx" in key]: del rx_drop_percent[key]

        filtered_values = [v for _, v in rx_drop_percent.items() if v !=0]
        average_rx_drop_percent = sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        csv_performance_rx_drop_percent_values=sorted(rx_drop_percent.items(), key=lambda x: (x[1],x[0]), reverse=False)
        csv_performance_rx_drop_percent_values=self.csv_validate_list(csv_performance_rx_drop_percent_values,5)
        for i in range(5):
            csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))
        for i in range(-1,-6,-1):
            csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))

        csv_rx_drop_percent_data.append(average_rx_drop_percent)

        for item, value in rx_drop_percent.items():
            print(item, "rx drop percent: ", rx_drop_percent[item])
            csv_rx_drop_percent_data.append(rx_drop_percent[item])

        self.csv_add_row(csv_rx_drop_percent_data,self.csv_writer,self.csv_file)

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        csv_performance_values = []
        csv_rx_headers = []
        csv_rx_delta_dict = {}

        # this may need to be a list as more monitoring takes place.
        csv_rx_row_data = [self.ts,'rx']
        csv_rx_delta_row_data = [self.ts,'rx_delta']

        for key in [key for key in old_list if "mtx" in key]: del old_list[key]
        for key in [key for key in new_list if "mtx" in key]: del new_list[key]

        print("rx (ts:{}): calculating worst, best, average".format(self.ts))
        filtered_values = [v for _, v in new_list.items() if v !=0]
        average_rx= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        csv_performance_values=sorted(new_list.items(), key=lambda x: (x[1],x[0]), reverse=False)
        csv_performance_values=self.csv_validate_list(csv_performance_values,5)
        for i in range(5):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))
        for i in range(-1,-6,-1):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))

        csv_rx_row_data.append(average_rx)
        #print("rx (ts:{}): worst, best, average {}".format(self.ts,csv_rx_row_data))

        if len(old_list) == len(new_list):
            print("rx_delta (ts:{}): calculating worst, best, average".format(self.ts))
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_delta_dict.update({item:(new_list[item] - old_list[item])})
                

            if not self.csv_started:
                csv_header = self.csv_generate_column_headers()
                csv_header += csv_rx_headers
                print(csv_header)
                self.csv_add_column_headers(csv_header)
                self.csv_started = True

            # need to generate list first to determine worst and best
            filtered_values = [v for _, v in csv_rx_delta_dict.items() if v !=0]
            average_rx_delta= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

            csv_performance_delta_values=sorted(csv_rx_delta_dict.items(), key=lambda x: (x[1],x[0]), reverse=False)
            csv_performance_delta_values=self.csv_validate_list(csv_performance_delta_values,5)
            for i in range(5):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))
            for i in range(-1,-6,-1):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))

            csv_rx_delta_row_data.append(average_rx_delta)
            #print("rx_delta (ts:{}): worst, best, average {}".format(self.ts,csv_rx_delta_row_data))
            
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_row_data.append(new_list[item])
                csv_rx_delta_row_data.append(new_list[item] - old_list[item])

            self.csv_add_row(csv_rx_row_data,self.csv_writer,self.csv_file)
            self.csv_add_row(csv_rx_delta_row_data,self.csv_writer,self.csv_file)

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            print("Old-list length: %i  new: %i does not match in compare-vals."%(len(old_list), len(new_list)))
            print("old-list:",old_list)
            print("new-list:",new_list)
            return False

    def verify_controller(self):
        if self.args == None:
            return

        if self.args.cisco_ctlr == None:
            return

        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "summary"], capture_output=True)
        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)

        # Find our station count
        searchap = False
        for line in pss.splitlines():
            if (line.startswith("---------")):
                searchap = True
                continue

            if (searchap):
                pat = "%s\s+\S+\s+\S+\s+\S+\s+\S+.*  \S+\s+\S+\s+(\S+)\s+\["%(self.args.cisco_ap)
                #print("AP line: %s"%(line))
                m = re.search(pat, line)
                if (m != None):
                    sta_count = m.group(1)
                    print("AP line: %s"%(line))
                    print("sta-count: %s"%(sta_count))
                    if (int(sta_count) != int(self.total_stas)):
                        print("WARNING:  Cisco Controller reported %s stations, should be %s"%(sta_count, self.total_stas))

    def controller_show_ap_channel(self):
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "ap_channel"], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)
        print("checking for 802.11{}".format(self.args.cisco_band))

        for line in pss.splitlines():
            #print("line {}".format(line))
            search_str = "802.11{}".format(self.args.cisco_band)
            if (line.lstrip().startswith(search_str)):
                print("line {}".format(line))
                element_list = line.lstrip().split()
                print("element_list {}".format(element_list))
                print("ap: {} channel {}  chan_width {}".format(self.args.cisco_ap,element_list[4],element_list[5]))
                if (str(self.args.cisco_channel) in str(element_list[4])) and (str(self.args.cisco_chan_width) in str(element_list[5])):
                    print("ap configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                    .format(self.args.cisco_channel,element_list[4],self.args.cisco_chan_width,element_list[5])) 
                else:
                    print("AP WARNING: channel {} expected {}  chan_width {} expected {}"
                    .format(element_list[4],self.cisco_channel,element_list[5],self.args.cisco_chan_width)) 
                break
        
        print("configure ap {} channel {} chan_width {}".format(self.args.cisco_ap,self.args.cisco_channel,self.args.cisco_chan_width))
        # Verify channel and channel width. 

    def controller_disable_ap(self):
        #(Cisco Controller) >config 802.11a disable APA453.0E7B.CF9C 
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "disable","--band",self.args.cisco_band], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)

    def controller_set_channel_ap(self):
        #(Cisco Controller) >config 802.11a channel ap APA453.0E7B.CF9C  52
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "channel","--value",self.args.cisco_channel], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)      

    # for testing perposes set channel back to 36
    def controller_set_channel_ap_36(self):
        #(Cisco Controller) >config 802.11a channel ap APA453.0E7B.CF9C  36
        cisco_channel_36 = "36"
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "channel","--value",cisco_channel_36], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)      


    def controller_set_chan_width_ap(self):
        #(Cisco Controller) >config 802.11a chan_width APA453.0E7B.CF9C  20	
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "bandwidth","--value",self.args.cisco_chan_width], capture_output=True)
        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)                                   
                     

    def controller_enable_ap(self):
        #(Cisco Controller) >config 802.11a enable APA453.0E7B.CF9C
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", "ssh", "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap, "--action", "enable","--band",self.args.cisco_band], capture_output=True)
        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)          

    def verify_cac_on_ap(self):
        pass
        # Do this after you get the configuration Verify CAC
        # use pySerial to check if the AP is configured:
        # 1. You can grep for "DFS CAC timer enabled time 60" 
        # 2. and "changed to DFS channel 52, running CAC for 60 seconds
        # Wait for 60 sec and check for this log "CAC_EXPIRY_EVT: CAC finished on DFS channel 52"
        #"make a note of the time and check the CAC timer expired in 60-61 seconds."

        # After CAC expires Verify Traffic. (the loop should start up may want some special detection)

    def lf_hackrf_enable(self):
        # hard coded for now
        # need json and update to realm
        #if os.path.isfile(self.args.hackrf):
        #    print("hack rf file found {}".format(self.args.hackrf))
        #else:
        #    print("WARNING: hack rf file not found at {}".format(self.args.hackrf))

        # look for lf_hackrf.py in local directory the look for in 
        pass

    def verify_radar_detected_on_ap(self):
        pass
        #You will see logs as below in the AP:(show logging will help you getting this info)

        #[*07/07/2020 23:44:27.7630] wcp/dfs :: RadarDetection: radar detected
        #[*07/07/2020 23:44:27.7630] wcp/dfs :: RadarDetection: sending packet out to capwapd, slotId=1, msgLen=386, chanCnt=1 -100
        #[*07/07/2020 23:44:27.7900] DOT11_DRV[1]: DFS CAC timer disabled time 0
        #[*07/07/2020 23:44:27.7960] Enabling Channel and channel width Switch Announcement on current channel 
        #[*07/07/2020 23:44:27.8060] DOT11_DRV[1]: set_dfs Channel set to 36/20, CSA count 10
        #[*07/07/2020 23:44:27.8620] DOT11_DRV[1]: DFS CAC timer enabled time 60

    def verify_black_list_time_ap(self):
        pass

    def lf_hackrf_disable(self):
        pass
        #need to save the process id

    # dfs dynamic frequency selection
    def dfs(self):
        if self.args == None:
            return
        if self.args.cisco_ctlr == None:
            return
        if self.args.cisco_dfs == False:
            return
        if self.args.cisco_channel == None:
            return
        if self.args.cisco_chan_width == None:
            return
        print("testing dfs")
        self.controller_show_ap_channel()
        self.controller_disable_ap()
        self.controller_set_channel_ap()
        self.controller_set_chan_width_ap()
        self.controller_enable_ap()
        self.verify_cac_on_ap()                 
        self.lf_hackrf_enable()
        self.verify_radar_detected_on_ap()
        self.verify_black_list_time_ap()
        self.lf_hackrf_disable()

        # For Testing  only - since hackrf not causing channel changes
        self.controller_disable_ap()
        self.controller_set_channel_ap_36()
        #self.dfs_set_chan_width_ap()
        self.controller_enable_ap()
        #check the AP for 52 is configured or not ,  check the CAC timer 
        # verify the clien can connect back to the AP once the CAC expires (check all connections)

    def controller_channel_chan_width_config(self):
        if self.args == None:
            return
        if self.args.cisco_ctlr == None:
            return
        if self.args.cisco_channel == None:
            return
        self.controller_disable_ap()
        self.controller_set_channel_ap()
        self.controller_set_chan_width_ap()
        self.controller_enable_ap()
        self.controller_show_ap_channel()
        # need to actually check the CAC timer
        time.sleep(60)

    def reset_port_check(self):
        for station_profile in self.station_profiles:
            if station_profile.reset_port_extra_data['reset_port_enable']:
                if station_profile.reset_port_extra_data['reset_port_timer_started'] == False:
                    print("reset_port_time_min: {}".format(station_profile.reset_port_extra_data['reset_port_time_min']))
                    print("reset_port_time_max: {}".format(station_profile.reset_port_extra_data['reset_port_time_max']))
                    station_profile.reset_port_extra_data['seconds_till_reset'] = \
                    random.randint(station_profile.reset_port_extra_data['reset_port_time_min'],\
                                   station_profile.reset_port_extra_data['reset_port_time_max'])
                    station_profile.reset_port_extra_data['reset_port_timer_started'] = True
                    print("seconds_till_reset {}".format(station_profile.reset_port_extra_data['seconds_till_reset']))
                else:
                    station_profile.reset_port_extra_data['seconds_till_reset'] = station_profile.reset_port_extra_data['seconds_till_reset'] - 1
                    print("countdown seconds_till_reset {}".format(station_profile.reset_port_extra_data['seconds_till_reset']))
                    if ((station_profile.reset_port_extra_data['seconds_till_reset']  <= 0)):
                        station_profile.reset_port_extra_data['reset_port_timer_started'] = False
                        port_to_reset = random.randint(0,len(station_profile.station_names)-1)
                        print("reset station number {} station: {}".format(port_to_reset+1,station_profile.station_names[port_to_reset]))
                        self.local_realm.reset_port(station_profile.station_names[port_to_reset])

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.local_realm.rm_port(sta, check_exists=True)
                self.total_stas += 1

        # Make sure they are gone
        count = 0
        while (count < 10):
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.local_realm.rm_port(sta, check_exists=True)
                    if (rv):
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)

    def build(self):
        self.controller_channel_chan_width_config()
        self.dfs()
        index = 0
        for station_profile in self.station_profiles:
            station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            print("Creating stations")

            station_profile.create(radio=self.radio_name_list[index], sta_names_=self.station_lists[index], debug=self.debug, sleep_time=0)
            index += 1

            for etype in self.endp_types:
                if etype == "mc_udp" or etype == "mc_udp6":
                    print("Creating Multicast connections for endpoint type: %s"%(etype))
                    self.multicast_profile.create_mc_tx(etype, self.side_b, etype)
                    self.multicast_profile.create_mc_rx(etype, side_rx=station_profile.station_names)
                else:
                    for _tos in self.tos:
                        print("Creating connections for endpoint type: %s TOS: %s"%(etype, _tos))
                        self.cx_profile.create(endp_type=etype, side_a=station_profile.station_names, side_b=self.side_b, sleep_time=0, tos=_tos)
        self._pass("PASS: Stations build finished")        
        
    def start(self, print_pass=False, print_fail=False):
        print("Bringing up stations")
        self.local_realm.admin_up(self.side_b) 
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                print("Bringing up station %s"%(sta))
                self.local_realm.admin_up(sta)

        temp_stations_list = []
        temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())

        if self.local_realm.wait_for_ip(temp_stations_list, timeout_sec=120):
            print("ip's acquired")
        else:
            print("print failed to get IP's")

        self.verify_controller()
        print("Starting multicast traffic (if any configured)")
        self.multicast_profile.start_mc(debug_=self.debug)
        self.multicast_profile.refresh_mc(debug_=self.debug)
        print("Starting layer-3 traffic (if any configured)")
        self.cx_profile.start_cx()
        self.cx_profile.refresh_cx()

        cur_time = datetime.datetime.now()
        print("Getting initial values.")
        old_rx_values, rx_drop_percent = self.__get_rx_values()

        end_time = self.local_realm.parse_time(self.test_duration) + cur_time

        print("Monitoring throughput for duration: %s"%(self.test_duration))

        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            #interval_time = cur_time + datetime.timedelta(seconds=60)
            interval_time = cur_time + datetime.timedelta(seconds=5)
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                self.reset_port_check()
                time.sleep(1)
            
            self.ts = int(time.time())
            new_rx_values, rx_drop_percent = self.__get_rx_values()

            expected_passes += 1
            if self.__compare_vals(old_rx_values, new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
            old_rx_values = new_rx_values

            self.__record_rx_dropped_percent(rx_drop_percent)

            cur_time = datetime.datetime.now()

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.local_realm.admin_down(station_name)

    def cleanup(self):
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()
                                        
    def csv_generate_column_headers(self):
        csv_rx_headers = ['Time epoch','Monitor']
        for i in range(1,6):
            csv_rx_headers.append("least_rx_data {}".format(i))
        for i in range(1,6):
            csv_rx_headers.append("most_rx_data_{}".format(i))
        csv_rx_headers.append("average_rx_data")
        return csv_rx_headers

    def csv_add_column_headers(self,headers):
        if self.csv_file is not None:
            self.csv_writer.writerow(headers)
            self.csv_file.flush()

    def csv_validate_list(self, csv_list, length):
        if len(csv_list) < length:
            csv_list = csv_list + [('no data','no data')] * (length - len(csv_list))
        return csv_list

    def csv_add_row(self,row,writer,csv_file):
        if self.csv_file is not None:
            writer.writerow(row)
            csv_file.flush()

def valid_endp_types(_endp_type):
    etypes = _endp_type.split()
    for endp_type in etypes:
        valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            print('invalid endp_type: %s. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' % endp_type)
            exit(1)
    return _endp_type

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug_on = False

    parser = argparse.ArgumentParser(
        prog='test_l3_longevity.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will generate csv file 
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Maximum stations per radio is 64
            ''',
        
        description='''\
test_l3_longevity.py:
--------------------

Summary : 
----------
create stations, create traffic between upstream port and stations,  run traffic. 
The traffic on the stations will be checked once per minute to verify that traffic is transmitted
and recieved.

Generic command layout:
-----------------------
python .\\test_l3_longevity.py --test_duration <duration> --endp_type <traffic types> --upstream_port <port> 
        --radio "radio==<radio> stations==<number staions> ssid==<ssid> ssid_pw==<ssid password> security==<security type: wpa2, open, wpa3>" --debug
Multiple radios may be entered with individual --radio switches

generiic command with controller setting channel and channel width test duration 5 min
python3 test_l3_longevity.py --cisco_ctlr <IP> --cisco_dfs True/False --mgr <Lanforge IP> 
    --cisco_channel <channel> --cisco_chan_width <20,40,80,120> --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port <1.ethX> 
    --radio "radio==<radio 0 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open>" 
    --radio "radio==<radio 1 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open>" 
    --duration 5m


<duration>: number followed by one of the following 
d - days
h - hours
m - minutes
s - seconds

<traffic type>: 
lf_udp  : IPv4 UDP traffic
lf_tcp  : IPv4 TCP traffic
lf_udp6 : IPv6 UDP traffic
lf_tcp6 : IPv6 TCP traffic
mc_udp  : IPv4 multi cast UDP traffic
mc_udp6 : IPv6 multi cast UDP traffic

<tos>: 
BK, BE, VI, VO:  Optional wifi related Tos Settings.  Or, use your preferred numeric values.

#################################
#Command switches
#################################
--cisco_ctlr <IP of Cisco Controller>',default=None
--cisco_user <User-name for Cisco Controller>',default="admin"
--cisco_passwd <Password for Cisco Controller>',default="Cisco123
--cisco_prompt <Prompt for Cisco Controller>',default="(Cisco Controller) >
--cisco_ap <Cisco AP in question>',default="APA453.0E7B.CF9C"
    
--cisco_dfs <True/False>',default=False
--cisco_channel <channel>',default=None  , no change
--cisco_chan_width <20 40 80 160>',default="20",choices=["20","40","80","160"]
--cisco_band <a | b | abgn>',default="a",choices=["a", "b", "abgn"]

--mgr <hostname for where LANforge GUI is running>',default='localhost'
-d  / --test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m'
--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE"
--debug:  Enable debugging',default=False
-t  / --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types
-u / --upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
-o / --outfile <Output file for csv data>", default='longevity_results'

#########################################
# Examples
# #######################################            
Example #1  running traffic with two radios
1. Test duration 4 minutes
2. Traffic IPv4 TCP
3. Upstream-port eth1
4. Radio #0 wiphy0 has 32 stations, ssid = candelaTech-wpa2-x2048-4-1, ssid password = candelaTech-wpa2-x2048-4-1
5. Radio #1 wiphy1 has 64 stations, ssid = candelaTech-wpa2-x2048-5-3, ssid password = candelaTech-wpa2-x2048-5-3
6. Create connections with TOS of BK and VI

Command: (remove carriage returns)
python3 .\\test_l3_longevity.py --test_duration 4m --endp_type \"lf_tcp lf_udp mc_udp\" --tos \"BK VI\" --upstream_port eth1 
--radio "radio==wiphy0 stations==32 ssid==candelaTech-wpa2-x2048-4-1 ssid_pw==candelaTech-wpa2-x2048-4-1 security==wpa2"
--radio "radio==wiphy1 stations==64 ssid==candelaTech-wpa2-x2048-5-3 ssid_pw==candelaTech-wpa2-x2048-5-3 security==wpa2"

Example #2 using cisco controller
1.  cisco controller at 192.168.100.112
2.  cisco dfs True
3.  cisco channel 52  
4.  cisco channel width 20
5.  traffic 'lf_udp lf_tcp mc_udp'
6.  upstream port eth3
7.  radio #0 wiphy0 stations  3 ssid test_candela ssid_pw [BLANK] secruity Open
8.  radio #1 wiphy1 stations 16 ssid test_candela ssid_pw [BLANK] security Open
9.  lanforge manager at 192.168.100.178
10. duration 5m

Command:
python3 test_l3_longevity.py --cisco_ctlr 192.168.100.112 --cisco_dfs True --mgr 192.168.100.178 
    --cisco_channel 52 --cisco_chan_width 20 --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port 1.eth3 
    --radio "radio==1.wiphy0 stations==3 ssid==test_candela ssid_pw==[BLANK] security==open" 
    --radio "radio==1.wiphy1 stations==16 ssid==test_candela ssid_pw==[BLANK] security==open"
    --test_duration 5m


        ''')


    parser.add_argument('--cisco_ctlr', help='--cisco_ctlr <IP of Cisco Controller>',default=None)
    parser.add_argument('--cisco_user', help='--cisco_user <User-name for Cisco Controller>',default="admin")
    parser.add_argument('--cisco_passwd', help='--cisco_passwd <Password for Cisco Controller>',default="Cisco123")
    parser.add_argument('--cisco_prompt', help='--cisco_prompt <Prompt for Cisco Controller>',default="\(Cisco Controller\) >")
    parser.add_argument('--cisco_ap', help='--cisco_ap <Cisco AP in question>',default="APA453.0E7B.CF9C")
    
    parser.add_argument('--cisco_dfs', help='--cisco_dfs <True/False>',default=False)

    parser.add_argument('--cisco_channel', help='--cisco_channel <channel>',default=None)
    parser.add_argument('--cisco_chan_width', help='--cisco_chan_width <20 40 80 160>',default="20",choices=["20","40","80","160"])
    parser.add_argument('--cisco_band', help='--cisco_band <a | b | abgn>',default="a",choices=["a", "b", "abgn"])

    parser.add_argument('--amount_ports_to_reset', help='--amount_ports_to_reset \"<min amount ports> <max amount ports>\" ', default=None)
    parser.add_argument('--port_reset_seconds', help='--ports_reset_seconds \"<min seconds> <max seconds>\" ', default="10 30")

    parser.add_argument('--mgr', help='--mgr <hostname for where LANforge GUI is running>',default='localhost')
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m')
    parser.add_argument('--tos', help='--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE")
    parser.add_argument('--debug', help='--debug:  Enable debugging',default=False)
    parser.add_argument('-t', '--endp_type', help='--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
    parser.add_argument('-o','--csv_outfile', help="--csv_outfile <Output file for csv data>", default='longevity_results')
    #parser.add_argument('-c','--csv_output', help="Generate csv output", default=False) 

    parser.add_argument('-r','--radio', action='append', nargs=1, help='--radio  \
                        \"radio==<number_of_wiphy stations=<=number of stations> ssid==<ssid> ssid_pw==<ssid password> security==<security>\" '\
                        , required=True)
    args = parser.parse_args()

    #print("args: {}".format(args))
    
    debug_on = args.debug
 
    if args.test_duration:
        test_duration = args.test_duration

    if args.endp_type:
        endp_types = args.endp_type

    if args.mgr:
        lfjson_host = args.mgr

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio

    if args.csv_outfile != None:
        current_time = time.strftime("%m_%d_%Y_%H_%M", time.localtime())
        csv_outfile = "{}_{}.csv".format(args.csv_outfile,current_time)
        print("csv output file : {}".format(csv_outfile))
        

    MAX_NUMBER_OF_STATIONS = 64
    
    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []
    ssid_security_list = []

    #optional radio configuration
    reset_port_enable_list = []
    reset_port_time_min_list = []
    reset_port_time_max_list = []

    print("radios {}".format(radios))
    for radio_ in radios:
        radio_keys = ['radio','stations','ssid','ssid_pw','security']
        #print("radio_ {}".format(str(radio_).replace('[','').replace(']','').replace("'","")))
        radio_info_dict = dict(map(lambda x: x.split('=='), str(radio_).replace('[','').replace(']','').replace("'","").split()))
        print("radio_dict {}".format(radio_info_dict))

        for key in radio_keys:
            if key not in radio_info_dict:
                print("missing config, for the {}, all of the following need to be present {} ".format(key,radio_keys))
                exit(1)
        
        radio_name_list.append(radio_info_dict['radio'])
        number_of_stations_per_radio_list.append(radio_info_dict['stations'])
        ssid_list.append(radio_info_dict['ssid'])
        ssid_password_list.append(radio_info_dict['ssid_pw'])
        ssid_security_list.append(radio_info_dict['security'])

        optional_radio_reset_keys = ['reset_port_enable']
        radio_reset_found = True
        for key in optional_radio_reset_keys:
            if key not in radio_info_dict:
                print("port reset test not enabled")
                radio_reset_found = False
                break

        if radio_reset_found:
            reset_port_enable_list.append('True')
            reset_port_time_min_list.append(radio_info_dict['reset_port_time_min'])
            reset_port_time_max_list.append(radio_info_dict['reset_port_time_max'])
        else:
            reset_port_enable_list.append('False')
            reset_port_time_min_list.append('0s')
            reset_port_time_max_list.append('0s')



    index = 0
    station_lists = []
    for (radio_name_, number_of_stations_per_radio_) in zip(radio_name_list,number_of_stations_per_radio_list):
        number_of_stations = int(number_of_stations_per_radio_)
        if number_of_stations > MAX_NUMBER_OF_STATIONS:
            print("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
            quit(1)
        station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= 1 + index*1000, end_id_= number_of_stations + index*1000,
                                              padding_number_=10000, radio=radio_name_)
        station_lists.append(station_list)
        index += 1

    #print("endp-types: %s"%(endp_types))

    ip_var_test = L3VariableTimeLongevity(
                                    lfjson_host,
                                    lfjson_port,
                                    args=args,
                                    number_template="00", 
                                    station_lists= station_lists,
                                    name_prefix="LT-",
                                    endp_types=endp_types,
                                    tos=args.tos,
                                    side_b=side_b,
                                    radio_name_list=radio_name_list,
                                    number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                    ssid_list=ssid_list,
                                    ssid_password_list=ssid_password_list,
                                    ssid_security_list=ssid_security_list, 
                                    test_duration=test_duration,
                                    reset_port_enable_list=reset_port_enable_list,
                                    reset_port_time_min_list=reset_port_time_min_list,
                                    reset_port_time_max_list=reset_port_time_max_list,
                                    side_a_min_rate=256000, 
                                    side_b_min_rate=256000, 
                                    debug_on=debug_on, 
                                    outfile=csv_outfile)

    ip_var_test.pre_cleanup()

    ip_var_test.build()
    if not ip_var_test.passes():
        print("build step failed.")
        print(ip_var_test.get_fail_message())
        exit(1) 
    ip_var_test.start(False, False)
    ip_var_test.stop()
    if not ip_var_test.passes():
        print("stop test failed")
        print(ip_var_test.get_fail_message())
         

    print("Pausing 30 seconds after run for manual inspection before we clean up.")
    time.sleep(30)
    ip_var_test.cleanup()
    if ip_var_test.passes():
        print("Full test passed, all connections increased rx bytes")

if __name__ == "__main__":
    main()
