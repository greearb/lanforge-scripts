#!/usr/bin/env python3

# Supports creating user-specified amount stations on multiple radios
# Supports configuring upload and download requested rates and PDU sizes.
# Supports generating KPI data for storing in influxdb (used by Graphana)
# Supports generating connections with different ToS values.
# Supports generating tcp and/or UDP traffic types.

# Supports iterating over different PDU sizes
# Supports iterating over different requested tx rates (configurable as total or per-connection value)
# Supports iterating over attenuation values.
#
# Example config
#
# 10 stations on wiphy0, 1 station on wiphy2.  open-auth to ASUS_70 SSID
# Configured to submit KPI info to influxdb-version2.
#./test_l3_longevity.py --mgr localhost --endp_type 'lf_udp lf_tcp' --upstream_port 1.1.eth1 \
#  --radio "radio==1.1.wiphy0 stations==10 ssid==ASUS_70 ssid_pw==[BLANK] security==open" \
#  --radio "radio==1.1.wiphy2 stations==1 ssid==ASUS_70 ssid_pw==[BLANK] security==open" \
#  --test_duration 5s --influx_host c7-graphana --influx_port 8086 --influx_org Candela \
#  --influx_token=-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ== \
#  --influx_bucket ben --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000 \
#  --influx_tag testbed ath11k --influx_tag DUT ROG -o longevity.csv


import sys
import os
from pprint import pprint
from csv_to_influx import *
import re
import serial
import pexpect
from pexpect_serial import SerialSpawn

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
#from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
#import realm
from realm import Realm
import time
import datetime
import subprocess
import csv
import random

# This class handles running the test and generating reports.
class L3VariableTime(Realm):
    def __init__(self, 
                 endp_types, 
                 args, 
                 tos, 
                 side_b, 
                 radio_name_list, 
                 number_of_stations_per_radio_list,
                 ssid_list, 
                 ssid_password_list, 
                 ssid_security_list, 
                 station_lists, 
                 name_prefix, 
                 outfile,
                 reset_port_enable_list,
                 reset_port_time_min_list,
                 reset_port_time_max_list,
                 side_a_min_rate=[56000], 
                 side_a_max_rate=[0],
                 side_b_min_rate=[56000],
                 side_b_max_rate=[0],
                 side_a_min_pdu=["MTU"],
                 side_a_max_pdu=[0],
                 side_b_min_pdu=["MTU"],
                 side_b_max_pdu=[0],
                 user_tags=[],
                 rates_are_totals=False,
                 mconn=1,
                 attenuators=[],
                 atten_vals=[],
                 number_template="00", 
                 test_duration="256s",
                 polling_interval="60s",
                 lfclient_host="localhost", 
                 lfclient_port=8080, 
                 debug=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _proxy_str=None,
                 influxdb=None,
                 show_least_most_csv=False,
                 _capture_signal_list=[]):
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)
        self.influxdb = influxdb
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
        #self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.polling_interval_seconds = self.duration_time_to_seconds(polling_interval)
        self.cx_profile = self.new_l3_cx_profile()
        self.multicast_profile = self.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-";
        self.station_profiles = []
        self.args = args
        self.outfile = outfile
        self.csv_started = False
        self.epoch_time = int(time.time())
        self.debug = debug
        self.show_least_most_csv = show_least_most_csv
        self.mconn = mconn
        self.user_tags = user_tags
        

        self.side_a_min_rate = side_a_min_rate
        self.side_a_max_rate = side_a_max_rate
        self.side_b_min_rate = side_b_min_rate
        self.side_b_max_rate = side_b_max_rate

        self.side_a_min_pdu = side_a_min_pdu
        self.side_a_max_pdu = side_a_max_pdu
        self.side_b_min_pdu = side_b_min_pdu
        self.side_b_max_pdu = side_b_max_pdu

        self.rates_are_totals = rates_are_totals
        self.cx_count = 0
        self.station_count = 0

        self.attenuators = attenuators
        self.atten_vals = atten_vals
        if ((len(self.atten_vals) > 0) and (self.atten_vals[0] != -1) and (len(self.attenuators) == 0)):
            print("ERROR:  Attenuation values configured, but no Attenuator EIDs specified.\n")
            exit(1)

        self.cx_profile.mconn = mconn
        self.cx_profile.side_a_min_bps = side_a_min_rate[0]
        self.cx_profile.side_a_max_bps = side_a_max_rate[0]
        self.cx_profile.side_b_min_bps = side_b_min_rate[0]
        self.cx_profile.side_b_max_bps = side_b_max_rate[0]

        # Lookup key is port-eid name
        self.port_csv_files = {}
        self.port_csv_writers = {}

        # TODO:  cmd-line arg to enable/disable these stats.
        self.ap_stats_col_titles = ["Station Address", "PHY Mbps", "Data Mbps", "Air Use", "Data Use",
                                    "Retries", "bw", "mcs", "Nss", "ofdma", "mu-mimo"]

        dur = self.duration_time_to_seconds(self.test_duration)
                                                            
        if (self.polling_interval_seconds > dur + 1):
            self.polling_interval_seconds = dur - 1

        # Some checking on the duration
        #self.parse_time(self.test_duration)
        #if (    (radio_info_dict['reset_port_time_min'] >= args.test_duration)  
        #    or  (radio_info_dict['reset_port_time_max'] >= args.test_duration)):
        #    print("port reset times min {} max {} mismatched with test duration {}"\
        #        .format(radio_info_dict['reset_port_time_min'],radio_info_dict['reset_port_time_max'],args.test_duration)))
        #    exit(1)


        # Full spread-sheet data
        if self.outfile is not None:
            self.csv_file = open(self.outfile, "w") 
            self.csv_writer = csv.writer(self.csv_file, delimiter=",")
            kpi = self.outfile[:-4]
            kpi = kpi + "-kpi.csv"
            self.csv_kpi_file = open(kpi, "w")
            self.csv_kpi_writer = csv.writer(self.csv_kpi_file, delimiter=",")
        
        for (radio_, ssid_, ssid_password_, ssid_security_,\
            reset_port_enable_, reset_port_time_min_, reset_port_time_max_) \
            in zip(radio_name_list, ssid_list, ssid_password_list, ssid_security_list,\
            reset_port_enable_list, reset_port_time_min_list, reset_port_time_max_list):
            self.station_profile = self.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_
            self.station_profile.ssid_pass = ssid_password_
            self.station_profile.security = ssid_security_
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = 0
            self.station_profile.set_reset_extra(reset_port_enable=reset_port_enable_,\
                test_duration=self.duration_time_to_seconds(self.test_duration),\
                reset_port_min_time=self.duration_time_to_seconds(reset_port_time_min_),\
                reset_port_max_time=self.duration_time_to_seconds(reset_port_time_max_))
            self.station_profiles.append(self.station_profile)
        
        self.multicast_profile.host = self.lfclient_host
        self.cx_profile.host = self.lfclient_host
        self.cx_profile.port = self.lfclient_port
        self.cx_profile.name_prefix = self.name_prefix

    # Find avg latency, jitter for connections using specified port.
    def get_endp_stats_for_port(self, eid_name, endps):
        lat = 0
        jit = 0
        tput = 0
        count = 0

        #print("endp-stats-for-port, port-eid: ", eid_name)
        eid = self.name_to_eid(eid_name)

        # Convert all eid elements to strings
        eid[0] = str(eid[0])
        eid[1] = str(eid[1])
        eid[2] = str(eid[2])

        for e in endps:
            #pprint(e)
            eid_endp = e["eid"].split(".")
            print("Comparing eid: ", eid, " to endp-id: ", eid_endp)
            if eid[0] == eid_endp[0] and eid[1] == eid_endp[1] and eid[2] == eid_endp[2]:
                lat += int(e["delay"])
                jit += int(e["jitter"])
                tput += int(e["rx rate"])
                count += 1
                print("matched: ")
            else:
                print("Did not match")

        if count > 1:
            lat = int(lat / count)
            jit = int(jit / count)

        return lat, jit, tput

    # Query all endpoints to generate rx and other stats, returned
    # as an array of objects.
    def __get_rx_values(self):
        endp_list = self.json_get("endp?fields=name,eid,delay,jitter,rx+rate,rx+bytes,rx+drop+%25", debug_=False)
        endp_rx_drop_map = {}
        endp_rx_map = {}
        our_endps = {}
        endps = []

        total_ul = 0
        total_dl = 0

        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e;
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e;
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, value in endp_name.items():
                    if item in our_endps:
                        endps.append(value)
                        print("endpoint: ", item, " value:\n")
                        pprint(value)
                    
                        for value_name, value in value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value
                            if value_name == 'rx drop %':
                                endp_rx_drop_map[item] = value
                            if value_name == 'rx rate':
                                # This hack breaks for mcast or if someone names endpoints weirdly.
                                #print("item: ", item, " rx-bps: ", value_rx_bps)
                                if item.endswith("-A"):
                                    total_dl += int(value)
                                else:
                                    total_ul += int(value)

        #print("total-dl: ", total_dl, " total-ul: ", total_ul, "\n")
        return endp_rx_map, endp_rx_drop_map, endps, total_dl, total_ul

    # Common code to generate timestamp for CSV files.
    def time_stamp(self):
        return time.strftime('%m_%d_%Y_%H_%M_%S', time.localtime(self.epoch_time))

    # Generate rx-dropped csv data
    def __record_rx_dropped_percent(self,rx_drop_percent):

        csv_rx_drop_percent_data = self.get_row_data_start('rx_drop_percent')

        # Honestly, I don't understand this code. --Ben
        for key in [key for key in rx_drop_percent if "mtx" in key]: del rx_drop_percent[key]

        filtered_values = [v for _, v in rx_drop_percent.items() if v !=0]
        average_rx_drop_percent = sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        if self.show_least_most_csv:
            csv_performance_rx_drop_percent_values=sorted(rx_drop_percent.items(), key=lambda x: (x[1],x[0]), reverse=False)
            csv_performance_rx_drop_percent_values=self.csv_validate_list(csv_performance_rx_drop_percent_values,5)
            for i in range(5):
                csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))
            for i in range(-1,-6,-1):
                csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))

        csv_rx_drop_percent_data.append(average_rx_drop_percent)

        for item, value in rx_drop_percent.items():
            #print(item, "rx drop percent: ", rx_drop_percent[item])
            csv_rx_drop_percent_data.append(rx_drop_percent[item])

        self.csv_add_row(csv_rx_drop_percent_data, self.csv_writer, self.csv_file)

    def get_row_data_start(self, third_row):
        return [self.epoch_time, self.time_stamp(), third_row,
                self.cx_profile.side_a_min_bps, self.cx_profile.side_a_max_bps,
                self.cx_profile.side_b_min_bps, self.cx_profile.side_b_max_bps,
                self.cx_profile.side_a_min_pdu, self.cx_profile.side_a_max_pdu,
                self.cx_profile.side_b_min_pdu, self.cx_profile.side_b_max_pdu,
            ]
        
    # Compare last stats report with current stats report.  Generate CSV data lines
    # for the various csv output files this test supports.
    # old-list and new list holds 'rx-bytes' counters.
    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        csv_performance_values = []
        csv_rx_headers = []
        csv_rx_delta_dict = {}

        # this may need to be a list as more monitoring takes place.
        csv_rx_row_data = self.get_row_data_start("rx-bytes")
        
        csv_rx_delta_row_data = self.get_row_data_start("rx-bytes_delta")

        for key in [key for key in old_list if "mtx" in key]: del old_list[key]
        for key in [key for key in new_list if "mtx" in key]: del new_list[key]

        filtered_values = [v for _, v in new_list.items() if v !=0]
        average_rx= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        if self.show_least_most_csv:
            csv_performance_values=sorted(new_list.items(), key=lambda x: (x[1],x[0]), reverse=False)
            csv_performance_values=self.csv_validate_list(csv_performance_values,5)
            for i in range(5):
                csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))
            for i in range(-1,-6,-1):
                csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))

        csv_rx_row_data.append(average_rx)

        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    #if self.debug: print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                    fail_msg = "Failed to increase rx data: station: {} rx_new: {} rx_old: {}".format(item, new_list[item], old_list[item])
                    self._fail(fail_msg, True)
                if not self.csv_started:
                    csv_rx_headers.append(item) # column header is endp name
                csv_rx_delta_dict.update({item:(new_list[item] - old_list[item])})
                

            if not self.csv_started:
                csv_header = self.csv_generate_column_headers()
                csv_header += csv_rx_headers
                #print(csv_header)
                self.csv_add_column_headers(csv_header)
                port_eids = self.gather_port_eids()
                for eid_name in port_eids:
                    self.csv_add_port_column_headers(eid_name, self.csv_generate_port_column_headers())
                self.csv_started = True

            # need to generate list first to determine worst and best
            filtered_values = [v for _, v in csv_rx_delta_dict.items() if v !=0]
            average_rx_delta= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

            if self.show_least_most_csv:
                csv_performance_delta_values=sorted(csv_rx_delta_dict.items(), key=lambda x: (x[1],x[0]), reverse=False)
                csv_performance_delta_values=self.csv_validate_list(csv_performance_delta_values,5)
                for i in range(5):
                    csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))
                for i in range(-1,-6,-1):
                    csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))

            csv_rx_delta_row_data.append(average_rx_delta)
            
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    #if self.debug: print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_row_data.append(new_list[item])
                csv_rx_delta_row_data.append(new_list[item] - old_list[item])

            self.csv_add_row(csv_rx_row_data, self.csv_writer, self.csv_file)
            self.csv_add_row(csv_rx_delta_row_data, self.csv_writer, self.csv_file)

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            print("Old-list length: %i  new: %i does not match in compare-vals."%(len(old_list), len(new_list)))
            print("old-list:",old_list)
            print("new-list:",new_list)
            return False

    # Verify communication to cisco controller is as expected.
    # Can add support for different controllers by editing this
    # or creating similar methods for different controllers.
    def verify_controller(self):
        if self.args == None:
            return

        if self.args.cisco_ctlr == None:
            return

        try:
            print("scheme {} ctlr {} user {} passwd {} AP {} series {} band {} action {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"summary"))

            ctl_output = subprocess.run(["../wifi_ctl_9800_3504.py", "--scheme", self.args.cisco_scheme, "-d", self.args.cisco_ctlr, "-u",
                                       self.args.cisco_user, "-p", self.args.cisco_passwd,
                                       "-a", self.args.cisco_ap,"--series", self.args.cisco_series,"--action", "summary"], capture_output=True)
            pss = ctl_output.stdout.decode('utf-8', 'ignore')
            print(pss)
        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}"
                 .format(process_error.returncode, process_error.output))
            time.sleep(1)
            exit(1)
    

        # Find our station count
        searchap = False
        for line in pss.splitlines():
            if (line.startswith("---------")):
                searchap = True
                continue
            #TODO need to test with 9800 series to chelck the values
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


            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

    

    #advanced (showes summary)
    #./wifi_ctl_9800_3504.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action advanced --series 9800
    def controller_show_ap_channel(self):
        advanced = subprocess.run(["../wifi_ctl_9800_3504.py", "--scheme", self.args.cisco_scheme, "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--action", "ap_channel"], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)

        if self.args.cisco_series == "9800":
            for line in pss.splitlines():
                search_str = self.args.cisco_ap
                print("line {}".format(line))
                element_list = line.lstrip().split()
                print("element_list {}".format(element_list))
                if (line.lstrip().startswith(search_str)):
                    print("line {}".format(line))
                    element_list = line.lstrip().split()
                    print("element_list {}".format(element_list))
                    # AP Name (0) mac (1) slot (2) Admin State [enable/disable] (3) Oper State [Up/Down] (4) Width (5) Txpwr (6,7) channel (8) mode (9)
                    print("ap: {} slof {} channel {}  chan_width {}".format(element_list[0],element_list[2],element_list[8],element_list[5]))
                    if (str(self.args.cisco_channel) in str(element_list[8])) and (str(self.args.cisco_chan_width) in str(element_list[5])):
                        print("ap {} configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],self.args.cisco_channel,element_list[8],self.args.cisco_chan_width,element_list[5])) 
                    else:
                        print("WARNING ap {} configuration: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],self.args.cisco_channel,element_list[8],self.args.cisco_chan_width,element_list[5])) 
                    break
        else:
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


    # This script supports resetting ports, allowing one to test AP/controller under data load
    # while bouncing wifi stations.  Check here to see if we should reset ports.
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
                    print("on radio {} seconds_till_reset {}".format(station_profile.add_sta_data['radio'],station_profile.reset_port_extra_data['seconds_till_reset']))
                else:
                    station_profile.reset_port_extra_data['seconds_till_reset'] = station_profile.reset_port_extra_data['seconds_till_reset'] - 1
                    if self.debug: print("radio: {} countdown seconds_till_reset {}".format(station_profile.add_sta_data['radio']  ,station_profile.reset_port_extra_data['seconds_till_reset']))
                    if ((station_profile.reset_port_extra_data['seconds_till_reset']  <= 0)):
                        station_profile.reset_port_extra_data['reset_port_timer_started'] = False
                        port_to_reset = random.randint(0,len(station_profile.station_names)-1)
                        print("reset on radio {} station: {}".format(station_profile.add_sta_data['radio'],station_profile.station_names[port_to_reset]))
                        self.reset_port(station_profile.station_names[port_to_reset])

    # Cleanup any older config that a previous run of this test may have created.
    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.rm_port(sta, check_exists=True)
                self.total_stas += 1

        # Make sure they are gone
        count = 0
        while (count < 10):
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.rm_port(sta, check_exists=True)
                    if (rv):
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)

    def gather_port_eids(self):
        rv = [self.side_b]
        
        for station_profile in self.station_profiles:
            rv = rv + station_profile.station_names

        return rv;

    # Create stations and connections/endpoints.  If rebuild is true, then
    # only update connections/endpoints.
    def build(self, rebuild=False):
        index = 0
        self.station_count = 0
        self.udp_endps = []
        self.tcp_endps = []

        if rebuild:
            # if we are just re-applying new cx values, then no need to rebuild
            # stations, so allow skipping it.
            # Do clean cx lists so that when we re-apply them we get same endp name
            # as we had previously
            #print("rebuild: Clearing cx profile lists.\n")
            self.cx_profile.clean_cx_lists()
            self.multicast_profile.clean_mc_lists()

        for station_profile in self.station_profiles:
            if not rebuild:
                station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
                station_profile.set_number_template(station_profile.number_template)
                print("Creating stations on radio %s"%(self.radio_name_list[index]))

                station_profile.create(radio=self.radio_name_list[index], sta_names_=self.station_lists[index], debug=self.debug, sleep_time=0)
                index += 1

            self.station_count += len(station_profile.station_names)

            # Build/update connection types
            for etype in self.endp_types:
                if etype == "mc_udp" or etype == "mc_udp6":
                    print("Creating Multicast connections for endpoint type: %s"%(etype))
                    self.multicast_profile.create_mc_tx(etype, self.side_b, etype)
                    self.multicast_profile.create_mc_rx(etype, side_rx=station_profile.station_names)
                else:
                    for _tos in self.tos:
                        print("Creating connections for endpoint type: %s TOS: %s  cx-count: %s"%(etype, _tos, self.cx_profile.get_cx_count()))
                        these_cx, these_endp = self.cx_profile.create(endp_type=etype, side_a=station_profile.station_names,
                                                                      side_b=self.side_b, sleep_time=0, tos=_tos)
                        if (etype == "lf_udp" or etype == "lf_udp6"):
                            self.udp_endps = self.udp_endps + these_endp;
                        else:
                            self.tcp_endps = self.tcp_endps + these_endp;

        self.cx_count = self.cx_profile.get_cx_count()

        self._pass("PASS: Stations & CX build finished: created/updated: %s stations and %s connections."%(self.station_count, self.cx_count))        

    def read_ap_stats(self,band):
        #  5ghz:  wl -i wl1 bs_data  2.4ghz# wl -i wl0 bs_data
        stats_5ghz  = "wl -i wl1 bs_data"
        stats_24ghz = "w1 -i wl0 bs_data"
        ap_data = ""
        command = stats_5ghz
        '''if band == "5ghz":
            command = stats_5ghz
        else:
            command = stats_24ghz'''
    
        try:
            # configure the serial interface
            ser = serial.Serial(self.args.tty, int(self.args.baud), timeout=5)
            egg = SerialSpawn(ser)
            egg.sendline(str(command))
            egg.expect([pexpect.TIMEOUT], timeout=2) # do not detete line, waits for output
            ap_data = egg.before.decode('utf-8','ignore')
        except:
            print("WARNING unable to read AP")
        
        return ap_data

    # Run the main body of the test logic.
    def start(self, print_pass=False, print_fail=False):
        print("Bringing up stations")
        self.admin_up(self.side_b) 
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                print("Bringing up station %s"%(sta))
                self.admin_up(sta)

        temp_stations_list = []
        temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())

        if self.wait_for_ip(temp_stations_list, timeout_sec=120):
            print("ip's acquired")
        else:
            # TODO:  Allow fail and abort at this point.
            print("print failed to get IP's")

        # For each rate
        rate_idx = 0
        for ul in self.side_a_min_rate:
            dl = self.side_b_min_rate[rate_idx]
            rate_idx += 1

            # For each pdu size
            pdu_idx = 0
            for ul_pdu in self.side_a_min_pdu:
                dl_pdu = self.side_b_min_pdu[pdu_idx]
                pdu_idx += 1

                # Adjust rate to take into account the number of connections we have.
                if self.cx_count > 1 and self.rates_are_totals:
                    # Convert from string to int to do math, then back to string
                    # as that is what the cx_profile wants.
                    ul = str(int(int(ul) / self.cx_count))
                    dl = str(int(int(dl) / self.cx_count))

                dl_pdu_str = dl_pdu
                ul_pdu_str = ul_pdu

                if (ul_pdu == "AUTO" or ul_pdu == "MTU"):
                    ul_pdu = "-1"

                if (dl_pdu == "AUTO" or dl_pdu == "MTU"):
                    dl_pdu = "-1"

                print("ul: %s  dl: %s  cx-count: %s  rates-are-totals: %s\n"%(ul, dl, self.cx_count, self.rates_are_totals))
                
                # Set rate and pdu size config
                self.cx_profile.side_a_min_bps = ul
                self.cx_profile.side_a_max_bps = ul
                self.cx_profile.side_b_min_bps = dl
                self.cx_profile.side_b_max_bps = dl

                self.cx_profile.side_a_min_pdu = ul_pdu
                self.cx_profile.side_a_max_pdu = ul_pdu
                self.cx_profile.side_b_min_pdu = dl_pdu
                self.cx_profile.side_b_max_pdu = dl_pdu

                # Update connections with the new rate and pdu size config.
                self.build(rebuild=True)

                for atten_val in self.atten_vals:
                    if atten_val != -1:
                        for atten_idx in self.attenuators:
                            self.set_atten(atten_idx, atten_val)

                    self.verify_controller()
                    print("Starting multicast traffic (if any configured)")
                    self.multicast_profile.start_mc(debug_=self.debug)
                    self.multicast_profile.refresh_mc(debug_=self.debug)
                    print("Starting layer-3 traffic (if any configured)")
                    self.cx_profile.start_cx()
                    self.cx_profile.refresh_cx()

                    cur_time = datetime.datetime.now()
                    print("Getting initial values.")
                    old_rx_values, rx_drop_percent, endps, total_dl_bps, total_ul_bps = self.__get_rx_values()

                    end_time = self.parse_time(self.test_duration) + cur_time

                    print("Monitoring throughput for duration: %s"%(self.test_duration))

                    # Monitor test for the interval duration.
                    passes = 0
                    expected_passes = 0
                    total_dl_bps = 0
                    total_ul_bps = 0
                    endps = []

                    while cur_time < end_time:
                        #interval_time = cur_time + datetime.timedelta(seconds=5)
                        interval_time = cur_time + datetime.timedelta(seconds=self.polling_interval_seconds)
                        #print("polling_interval_seconds {}".format(self.polling_interval_seconds))
                        while cur_time < interval_time:
                            cur_time = datetime.datetime.now()
                            self.reset_port_check()
                            time.sleep(1)

                        self.epoch_time = int(time.time())
                        new_rx_values, rx_drop_percent, endps, total_dl_bps, total_ul_bps = self.__get_rx_values()

                        #print("main loop, total-dl: ", total_dl_bps, " total-ul: ", total_ul_bps)

                        expected_passes += 1
                        if self.__compare_vals(old_rx_values, new_rx_values):
                            passes += 1
                        else:
                            fail_msg = "FAIL: TIME: {} EPOCH: {} Not all stations increased traffic".format(cur_time, self.epoch_time) 
                            self._fail(fail_msg, print_fail)
                        old_rx_values = new_rx_values

                        self.__record_rx_dropped_percent(rx_drop_percent)

                    # At end of test step, record KPI information.
                    if self.influxdb is not None:
                        self.record_kpi(len(temp_stations_list), ul, dl, ul_pdu_str, dl_pdu_str, atten_val, total_dl_bps, total_ul_bps)
                    # RAW OUTPUT
                    '''
                    root@Docsis-Gateway:~# wl -i wl1 bs_data
Station Address   PHY Mbps  Data Mbps    Air Use   Data Use    Retries   bw   mcs   Nss   ofdma mu-mimo
50:E0:85:87:AA:19     1064.5       52.8       6.0%      25.0%       1.5%   80  10.0     2    0.0%    0.0%
50:E0:85:84:7A:E7      927.1       53.6       7.0%      25.4%       5.7%   80   8.8     2    0.0%    0.0%
50:E0:85:89:5D:00      857.5       51.8       6.8%      24.6%       0.8%   80     8     2    0.0%    0.0%
50:E0:85:87:5B:F4     1071.7       52.8       6.0%      25.0%       1.3%   80    10     2    0.0%    0.0%
        (overall)          -      210.9      25.8%         -         -
'''        

                    # Query AP for its stats.  Result for /ax bcm APs looks something like this:
                    # '''
                    ap_stats = [];
                    ap_stats.append("root@Docsis-Gateway:~# wl -i wl1 bs_data")
                    ap_stats.append("Station Address   PHY Mbps  Data Mbps    Air Use   Data Use    Retries   bw   mcs   Nss   ofdma mu-mimo")
                    ap_stats.append("50:E0:85:87:AA:19     1016.6       48.9       6.5%      24.4%      16.6%   80   9.7     2    0.0%    0.0%")
                    ap_stats.append("50:E0:85:84:7A:E7      880.9       52.2       7.7%      26.1%      20.0%   80   8.5     2    0.0%    0.0%")
                    ap_stats.append("50:E0:85:89:5D:00      840.0       47.6       6.4%      23.8%       2.3%   80   8.0     2    0.0%    0.0%")
                    ap_stats.append("50:E0:85:87:5B:F4      960.7       51.5       5.9%      25.7%       0.0%   80     9     2    0.0%    0.0%")
                    ap_stats.append("(overall)          -      200.2      26.5%         -         -")
                    # '''
                    # TODO:  Read real stats, comment out the example above.
                    # ap_stats = self.read_ap_stats()

                    ap_stats_rows = [] # Array of Arrays
                    for line in ap_stats:
                        stats_row = line.split()
                        ap_stats_rows.append(stats_row)

                    try:
                        m = re.search(r'(\S+)\s+(\S+)\s+(Data Mbps)\s+(Air Use)',str(ap_stats_rows[0]))
                    except:
                        print("regedit had issue with re.search ")

                    # Query all of our ports
                    port_eids = self.gather_port_eids()
                    for eid_name in port_eids:
                        eid = self.name_to_eid(eid_name)
                        url = "/port/%s/%s/%s"%(eid[0], eid[1], eid[2])
                        response = self.json_get(url)
                        if (response is None) or ("interface" not in response):
                            print("query-port: %s: incomplete response:"%(url))
                            pprint(response)
                        else:
                            p = response['interface']
                            mac = response['mac']

                            ap_row = []
                            for row in ap_stats_rows:
                                if row[0].lower() == mac.lower():
                                    ap_row = row;

                            # p is map of key/values for this port
                            print("port: ")
                            pprint(p)

                            # Find latency, jitter for connections using this port.
                            latency, jitter, tput = self.get_endp_stats_for_port(p["port"], endps)
                            
                            ap_stats_col_titles = ['Station Address','PHY Mbps','Data Mbps','Air Use','Data Use','Retries','bw','mcs','Nss','ofdma','mu-mimo']

                            self.write_port_csv(len(temp_stations_list), ul, dl, ul_pdu_str, dl_pdu_str, atten_val, eid_name, p,
                                                latency, jitter, tput, ap_row, ap_stats_col_titles)

                    # Stop connections.
                    self.cx_profile.stop_cx();
                    self.multicast_profile.stop_mc();

                    cur_time = datetime.datetime.now()

                    if passes == expected_passes:
                            self._pass("PASS: Requested-Rate: %s <-> %s  PDU: %s <-> %s   All tests passed" % (ul, dl, ul_pdu, dl_pdu), print_pass)

    def write_port_csv(self, sta_count, ul, dl, ul_pdu, dl_pdu, atten, eid_name, port_data, latency, jitter, tput,
                       ap_row, ap_stats_col_titles):
        row = [self.epoch_time, self.time_stamp(), sta_count,
               ul, ul, dl, dl, dl_pdu, dl_pdu, ul_pdu, ul_pdu,
               atten, eid_name
               ]

        row = row + [port_data['bps rx'], port_data['bps tx'], port_data['rx-rate'], port_data['tx-rate'],
                     port_data['signal'], port_data['ap'], port_data['mode'], latency, jitter, tput]

        #Add in info queried from AP.
        if len(ap_row) == len(self.ap_stats_col_titles):
            i = 0
            for col in ap_row:
                row.append(col)

        writer = self.port_csv_writers[eid_name]
        writer.writerow(row)
        self.port_csv_files[eid_name].flush()


    # Submit data to the influx db if configured to do so.
    def record_kpi(self, sta_count, ul, dl, ul_pdu, dl_pdu, atten, total_dl_bps, total_ul_bps):

        tags = dict()
        tags['requested-ul-bps'] = ul
        tags['requested-dl-bps'] = dl
        tags['ul-pdu-size'] = ul_pdu
        tags['dl-pdu-size'] = dl_pdu
        tags['station-count'] = sta_count
        tags['attenuation'] = atten
        tags["script"] = 'test_l3_longevity'

        # Add user specified tags
        for k in self.user_tags:
            tags[k[0]] = k[1]

        now = str(datetime.datetime.utcnow().isoformat())

        print("NOTE:  Adding kpi to influx, total-download-bps: %s  upload: %s  bi-directional: %s\n"%(total_dl_bps, total_ul_bps, (total_ul_bps + total_dl_bps)))

        self.influxdb.post_to_influx("total-download-bps", total_dl_bps, tags, now)
        self.influxdb.post_to_influx("total-upload-bps", total_ul_bps, tags, now)
        self.influxdb.post_to_influx("total-bi-directional-bps", total_ul_bps + total_dl_bps, tags, now)

        if self.csv_kpi_file:
            row = [self.epoch_time, self.time_stamp(), sta_count,
                   ul, ul, dl, dl, dl_pdu, dl_pdu, ul_pdu, ul_pdu,
                   atten,
                   total_dl_bps, total_ul_bps, (total_ul_bps + total_dl_bps)
                   ]
            # Add values for any user specified tags
            for k in self.user_tags:
                row.append(k[1])

            self.csv_kpi_writer.writerow(row)
            self.csv_kpi_file.flush()

    # Stop traffic and admin down stations.
    def stop(self):
        self.cx_profile.stop_cx()
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.admin_down(station_name)

    # Remove traffic connections and stations.
    def cleanup(self):
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()

    def csv_generate_column_headers(self):
        csv_rx_headers = ['Time epoch','Time','Monitor',
                          'UL-Min-Requested','UL-Max-Requested','DL-Min-Requested','DL-Max-Requested',
                          'UL-Min-PDU','UL-Max-PDU','DL-Min-PDU','DL-Max-PDU',
                          ]
        if self.show_least_most_csv:
            for i in range(1,6):
                csv_rx_headers.append("least_rx_data_bytes_{}".format(i))
            for i in range(1,6):
                csv_rx_headers.append("most_rx_data_bytes_{}".format(i))

        csv_rx_headers.append("average_rx_data_bytes")
        return csv_rx_headers

    def csv_generate_port_column_headers(self):
        csv_rx_headers = ['Time epoch', 'Time', 'Station-Count',
                          'UL-Min-Requested','UL-Max-Requested','DL-Min-Requested','DL-Max-Requested',
                          'UL-Min-PDU','UL-Max-PDU','DL-Min-PDU','DL-Max-PDU','Attenuation',
                          'Name', 'Rx-Bps', 'Tx-Bps', 'Rx-Link-Rate', 'Tx-Link-Rate', 'RSSI', 'AP', 'Mode',
                          'Rx-Latency', 'Rx-Jitter', 'Rx-Goodput-Bps'
                          ]
        # Add in columns we are going to query from the AP
        for col in self.ap_stats_col_titles:
            csv_rx_headers.append(col)

        return csv_rx_headers

    def csv_generate_kpi_column_headers(self):
        csv_rx_headers = ['Time epoch', 'Time', 'Station-Count',
                          'UL-Min-Requested','UL-Max-Requested','DL-Min-Requested','DL-Max-Requested',
                          'UL-Min-PDU','UL-Max-PDU','DL-Min-PDU','DL-Max-PDU','Attenuation',
                          'Total-Download-Bps', 'Total-Upload-Bps', 'Total-UL/DL-Bps'
                          ]
        for k in self.user_tags:
            csv_rx_headers.append(k[0])

        return csv_rx_headers

    # Write initial headers to csv file.
    def csv_add_column_headers(self,headers):
        if self.csv_file is not None:
            self.csv_writer.writerow(headers)
            self.csv_file.flush()
        if self.csv_kpi_file is not None:
            self.csv_kpi_writer.writerow(self.csv_generate_kpi_column_headers())
            self.csv_kpi_file.flush()

    # Write initial headers to port csv file.
    def csv_add_port_column_headers(self, eid_name, headers):
        if self.csv_file is not None:
            fname = self.outfile[:-4]  # Strip '.csv' from file name
            fname = fname + "-" + eid_name + ".csv"
            pfile = open(fname, "w")
            port_csv_writer = csv.writer(pfile, delimiter=",")
            self.port_csv_files[eid_name] = pfile
            self.port_csv_writers[eid_name] = port_csv_writer
            
            port_csv_writer.writerow(headers)
            pfile.flush()

    def csv_validate_list(self, csv_list, length):
        if len(csv_list) < length:
            csv_list = csv_list + [('no data','no data')] * (length - len(csv_list))
        return csv_list

    def csv_add_row(self,row,writer,csv_file):
        if csv_file is not None:
            writer.writerow(row)
            csv_file.flush()

    # End of the main class.

# Check some input values.
def valid_endp_types(_endp_type):
    etypes = _endp_type.split()
    for endp_type in etypes:
        valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            print('invalid endp_type: %s. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' % endp_type)
            exit(1)
    return _endp_type


# Starting point for running this from cmd line.
def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug = False

    parser = argparse.ArgumentParser(
        prog='test_l3_longevity.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will generate csv file 
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Maximum stations per radio based on radio
            ''',
        
        description='''\
test_l3_longevity.py:
--------------------

Summary : 
----------
create stations, create traffic between upstream port and stations,  run traffic. 
The traffic on the stations will be checked once per minute to verify that traffic is transmitted
and received.

Generic command layout:
-----------------------
python .\\test_l3_longevity.py --test_duration <duration> --endp_type <traffic types> --upstream_port <port> 
        --radio "radio==<radio> stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<security type: wpa2, open, wpa3>" --debug
Multiple radios may be entered with individual --radio switches

generic command with controller setting channel and channel width test duration 5 min
python3 test_l3_longevity.py --cisco_ctlr <IP> --cisco_dfs True/False --mgr <Lanforge IP> 
    --cisco_channel <channel> --cisco_chan_width <20,40,80,120> --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port <1.ethX> 
    --radio "radio==<radio 0 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open>" 
    --radio "radio==<radio 1 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open>" 
    --test_duration 5m

# UDP bi-directional test, no use of controller.
/test_l3_longevity.py --mgr localhost --endp_type 'lf_udp lf_tcp' --upstream_port 1.1.eth1 \
  --radio "radio==1.1.wiphy0 stations==10 ssid==ASUS_70 ssid_pw==[BLANK] security==open" \
  --radio "radio==1.1.wiphy2 stations==1 ssid==ASUS_70 ssid_pw==[BLANK] security==open" \
  --test_duration 30s

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
    parser.add_argument('--cisco_series', help='--cisco_series <9800 | 3504>',default="3504",choices=["9800","3504"])
    parser.add_argument('--cisco_scheme', help='--cisco_scheme (serial|telnet|ssh): connect via serial, ssh or telnet',default="ssh",choices=["serial","telnet","ssh"])

    parser.add_argument('--cisco_wlan', help='--cisco_wlan <wlan name> default: NA, NA means no change',default="NA")
    parser.add_argument('--cisco_wlanID', help='--cisco_wlanID <wlanID> default: NA , NA means not change',default="NA")
    parser.add_argument('--cisco_tx_power', help='--cisco_tx_power <1 | 2 | 3 | 4 | 5 | 6 | 7 | 8>  1 is highest power default NA NA means no change',default="NA"
                        ,choices=["1","2","3","4","5","6","7","8","NA"])


    parser.add_argument('--tty', help='--tty \"/dev/ttyUSB2\" the serial interface to the AP')
    parser.add_argument('--baud', help='--baud \"9600\"   baud rate for the serial interface',default="9600")
    parser.add_argument('--amount_ports_to_reset', help='--amount_ports_to_reset \"<min amount ports> <max amount ports>\" ', default=None)
    parser.add_argument('--port_reset_seconds', help='--ports_reset_seconds \"<min seconds> <max seconds>\" ', default="10 30")

    parser.add_argument('--mgr', help='--mgr <hostname for where LANforge GUI is running>',default='localhost')
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m')
    parser.add_argument('--tos', help='--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE")
    parser.add_argument('--debug', help='--debug flag present debug on  enable debugging',action='store_true')
    parser.add_argument('-t', '--endp_type', help='--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
    parser.add_argument('-o','--csv_outfile', help="--csv_outfile <Output file for csv data>", default="")
    parser.add_argument('--polling_interval', help="--polling_interval <seconds>", default='60s')

    parser.add_argument('-r','--radio', action='append', nargs=1, help='--radio  \
                        \"radio==<number_of_wiphy stations=<=number of stations> ssid==<ssid> ssid_pw==<ssid password> security==<security>\" ',
                        required=True)

    parser.add_argument('-tty',  help='-tty <port> serial interface to AP -tty \"/dev/ttyUSB2\"',default="")
    parser.add_argument('-baud', help='-baud <rate> serial interface baud rate to AP -baud ',default='9600')

    parser.add_argument('-amr','--side_a_min_bps',
                        help='--side_a_min_bps, requested downstream min tx rate, comma separated list for multiple iterations.  Default 256k', default="256000")
    parser.add_argument('-amp','--side_a_min_pdu',
                        help='--side_a_min_pdu, downstream pdu size, comma separated list for multiple iterations.  Default MTU', default="MTU")
    parser.add_argument('-bmr','--side_b_min_bps',
                        help='--side_b_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000', default="256000")
    parser.add_argument('-bmp','--side_b_min_pdu',
                        help='--side_b_min_pdu, upstream pdu size, comma separated list for multiple iterations. Default MTU', default="MTU")
    parser.add_argument("--rates_are_totals", default=False,
                        help="Treat configured rates as totals instead of using the un-modified rate for every connection.", action='store_true')
    parser.add_argument("--multiconn", default=1,
                        help="Configure multi-conn setting for endpoints.  Default is 1 (auto-helper is enabled by default as well).")

    parser.add_argument('--attenuators', help='--attenuators,  comma separated list of attenuator module eids:  shelf.resource.atten-serno.atten-idx', default="")
    parser.add_argument('--atten_vals', help='--atten_vals,  comma separated list of attenuator settings in ddb units (1/10 of db)', default="")

    influx_add_parser_args(parser)

    parser.add_argument("--cap_ctl_out",  help="--cap_ctl_out, switch the cisco controller output will be captured", action='store_true')
    parser.add_argument("--wait",  help="--wait <time> , time to wait at the end of the test", default='0')

    parser.add_argument("--show_least_most_csv",  help="Should we show the least/most csv column data in reports?", action='store_true', default=False)

    args = parser.parse_args()

    #print("args: {}".format(args))
    debug = args.debug
 
    if args.test_duration:
        test_duration = args.test_duration

    if args.polling_interval:
        polling_interval = args.polling_interval

    if args.endp_type:
        endp_types = args.endp_type

    if args.mgr:
        lfjson_host = args.mgr

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio

    if args.csv_outfile == "":
        current_time = time.strftime("%m_%d_%Y_%H_%M_%S", time.localtime())
        csv_outfile = "longevity_{}.csv".format(current_time)
        print("csv output file : {}".format(csv_outfile))
    else:
        csv_outfile = args.csv_outfile

    influxdb = None
    if args.influx_bucket is not None:
        from influx2 import RecordInflux
        influxdb = RecordInflux(_lfjson_host=lfjson_host,
                                _lfjson_port=lfjson_port,
                                _influx_host=args.influx_host,
                                _influx_port=args.influx_port,
                                _influx_org=args.influx_org,
                                _influx_token=args.influx_token,
                                _influx_bucket=args.influx_bucket)


    MAX_NUMBER_OF_STATIONS = 1000
    
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
                #print("port reset test not enabled")
                radio_reset_found = False
                break

        if radio_reset_found:
            reset_port_enable_list.append(True)
            reset_port_time_min_list.append(radio_info_dict['reset_port_time_min'])
            reset_port_time_max_list.append(radio_info_dict['reset_port_time_max'])
        else:
            reset_port_enable_list.append(False)
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

    ul_rates = args.side_a_min_bps.split(",")
    dl_rates = args.side_b_min_bps.split(",")
    ul_pdus = args.side_a_min_pdu.split(",")
    dl_pdus = args.side_b_min_pdu.split(",")
    if args.attenuators == "":
        attenuators = []
    else:
        attenuators = args.attenuators.split(",")
    if (args.atten_vals == ""):
        atten_vals = [-1]
    else:
        atten_vals = args.atten_vals.split(",")

    if (len(ul_rates) != len(dl_rates)):
        print("ERROR:  ul_rates %s and dl_rates %s arrays must be same length\n" %(len(ul_rates), len(dl_rates)))
    if (len(ul_pdus) != len(dl_pdus)):
        print("ERROR:  ul_pdus %s and dl_pdus %s arrays must be same length\n" %(len(ul_rates), len(dl_rates)))

    ip_var_test = L3VariableTime(
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
                                    polling_interval= polling_interval,
                                    lfclient_host=lfjson_host,
                                    lfclient_port=lfjson_port,
                                    reset_port_enable_list=reset_port_enable_list,
                                    reset_port_time_min_list=reset_port_time_min_list,
                                    reset_port_time_max_list=reset_port_time_max_list,
                                    side_a_min_rate=ul_rates,
                                    side_b_min_rate=dl_rates,
                                    side_a_min_pdu=ul_pdus,
                                    side_b_min_pdu=dl_pdus,
                                    rates_are_totals=args.rates_are_totals,
                                    mconn=args.multiconn,
                                    attenuators=attenuators,
                                    atten_vals=atten_vals,
                                    user_tags=args.influx_tag,
                                    debug=debug,
                                    outfile=csv_outfile,
                                    show_least_most_csv=args.show_least_most_csv,
                                    influxdb=influxdb)

    ip_var_test.pre_cleanup()

    ip_var_test.build()
    if not ip_var_test.passes():
        print("build step failed.")
        print(ip_var_test.get_fail_message())
        exit(1) 
    ip_var_test.start(False, False)
    ip_var_test.stop()
    if not ip_var_test.passes():
        print("Test Ended: There were Failures")
        print(ip_var_test.get_fail_message())
         
    try: 
        sub_output = subprocess.run(["./csv_processor.py", "--infile",csv_outfile],capture_output=True, check=True)
        pss = sub_output.stdout.decode('utf-8', 'ignore')
        print(pss)
    except Exception as e:
        print("Exception: {} failed creating summary and raw for {}, are all packages installed , pandas?".format(e,csv_outfile))

    print("Pausing {} seconds after run for manual inspection before we clean up.".format(args.wait))
    time.sleep(int(args.wait))
    ip_var_test.cleanup()
    if ip_var_test.passes():
        print("Full test passed, all connections increased rx bytes")

if __name__ == "__main__":
    main()
