#!/usr/bin/env python3
"""
NAME: lf_test_generic.py

PURPOSE:
lf_test_generic.py will create stations and endpoints to generate traffic based on a command-line specified command type.

This script will create a variable number of stations to test generic endpoints. Multiple command types can be tested
including ping, speedtest, lfcurl, iperf, generic types. The test will check the last-result attribute for different things
depending on what test is being run. Ping will test for successful pings, speedtest will test for download
speed, upload speed, and ping time, generic will test for successful generic commands.

This script also *does not* use any other file except lanforge_api.py. 

SETUP:
Make sure the generic tab is enabled in the GUI by going to the Port Manager, clicking the '+' tab, checking the 'generic' tab. 

EXAMPLES:
    LFPING :
        ./lf_test_generic.py --mgr 192.168.102.211 --test_type ping --lf_user lanforge --lf_passwd lanforge --num_stations 3 --log_level debug
                    --ssid eero-mesh-lanforge --passwd lanforge --security wpa2 --radio wiphy1 --target www.google.com --test_duration", "4s", "--create_report",
                    --report_file_path "/home/diptidhond/test_generic_1"
    LFCURL :
        ./lf_test_generic.py --mgr 192.168.102.211 --test_type lfcurl --lf_user lanforge --lf_passwd lanforge --num_stations 3 --log_level debug 
                    --ssid eero-mesh-lanforge --passwd lanforge --security wpa2 --radio wiphy1  --test_duration", "4s", "--create_report",
                    --report_file_path "/home/lanforge/test_generic_1"
    SPEEDTEST :
        ./lf_test_generic.py --mgr 192.168.102.211 --test_type speedtest --lf_user lanforge --lf_passwd lanforge --num_stations 3 --log_level debug
                    --ssid mesh-lanforge --passwd lanforge --security wpa2 --radio wiphy1  --test_duration", "4s", "--create_report", "--no_upload", "--single_connection",
                    --report_file_path "/home/lanforge/test_generic_1"
        
    IPERF3 :
        iperf -- client only: creates 3 client : 2 clients on sta, 1 on eth port (with existing eid):

            ./lf_test_generic.py: --mgr 192.168.102.211 --test_type iperf3-client --lf_user lanforge --lf_passwd lanforge --num_stations 2 --log_level debug --test_duration 20s
                --ssid mesh-lanforge --passwd lanforge --security wpa2 --radio wiphy1 --target 192.168.3.3 --use_existing_eid 1.1.eth2 --client_port 9191 --server_port 9191 --create_report --report_file_path "/home/lanforge/iperf3_reports"

        iperf -- server only: creates 3 servers : 2 servers on sta, 1 on eth port (with existing eid):

            ./lf_test_generic.py --mgr 192.168.102.211 --test_type iperf3-server --lf_user lanforge --lf_passwd lanforge --num_stations 2 --log_level debug --test_duration 20s
                --ssid mesh-lanforge --passwd lanforge --security wpa2 --radio wiphy1 --target --use_existing_eid 1.1.eth2 --client_port 9191 --server_port 9191 --create_report --report_file_path "/home/lanforge/iperf3_reports"

Use './test_generic.py --help' to see command line usage and options.

Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
import os
import importlib
import pprint
import argparse
import time
import datetime
import logging
import re
import csv
import pandas as pd
import numpy as np

from pandas import json_normalize
from lf_json_util import standardize_json_results


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
from lanforge_client.logg import Logg

#stand-alone (not dependent on realm)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")

from lf_graph import lf_bar_graph_horizontal
from lf_graph import lf_bar_graph
from lf_report import lf_report

lf_bar_graph = lf_graph.lf_bar_graph
lf_scatter_graph = lf_graph.lf_scatter_graph
lf_stacked_graph = lf_graph.lf_stacked_graph
lf_horizontal_stacked_graph = lf_graph.lf_horizontal_stacked_graph

logger = logging.getLogger(__name__)


if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

class GenTest():
    def __init__(self, lf_user, lf_passwd, ssid, security, passwd,
                name_prefix, num_stations, port_mgr_cols, gen_tab_cols, report_file_path, output_format = "csv", client_port = None,server_port=None,
                 host="localhost", port=8080, create_report = False, use_existing_eid=None, monitor_interval = "2s",
                 test_duration="20s",test_type="ping", target=None, cmd=None, spdtest_no_download = False, spdtest_no_upload = False, spdtest_single_connection = False, 
                 spdtest_enable_debug = False, spdtest_enable_report= False, spdtest_ookla = False, interval=0.1, destination_url_lfcurl = None,
                 radio=None, file_output_lfcurl=None, lf_logger_json = None, log_level = "debug", loop_count=None,
                 _debug_on=False, _exit_on_error=False, die_on_error = False,_exit_on_fail=False):
        self.host=host
        self.port=port
        self.lf_user=lf_user
        self.lf_passwd=lf_passwd
        self.ssid = ssid
        self.radio = radio
        self.num_stations = num_stations
        self.security = security
        self.passwd = passwd
        self.name_prefix = name_prefix

        #Generic test args
        self.cmd = cmd
        self.test_type = test_type
        self.file_output_lfcurl = file_output_lfcurl
        self.destination_url_lfcurl = destination_url_lfcurl

        #speedtest specific
        self.spdtest_no_download = spdtest_no_download
        self.spdtest_no_upload = spdtest_no_upload
        self.spdtest_single_connection = spdtest_single_connection
        self.spdtest_enable_debug = spdtest_enable_debug
        self.spdtest_enable_report = spdtest_enable_report
        self.spdtest_ookla = spdtest_ookla

        self.loop_count = loop_count
        self.target = target
        self.interval = interval
        self.client_port = client_port
        self.server_port = server_port

        #Test duration, sleep interval for monitoring/data collection, logging/debugging
        self.monitor_interval = monitor_interval
        self.lfclient_url = "http://%s:%s" % (self.host, self.port)
        self.test_duration = test_duration
        self.debug = _debug_on
        self.report_timer = 1500
        self.log_level = log_level
        self.lf_logger_json = lf_logger_json

        #TODO currently un-used args. Add to test below.
        self.exit_on_error = _exit_on_error
        self.exit_on_fail = _exit_on_fail
        self.die_on_error = die_on_error

        #reporting
        self.output_format = output_format
        self.report_file_path = report_file_path
        self.create_report = create_report
        self.gen_tab_cols = gen_tab_cols
        self.port_mgr_cols = port_mgr_cols

        # create a session
        self.session = LFSession(lfclient_url="http://%s:8080" % self.host,
                                 debug=_debug_on,
                                 connection_timeout_sec=4.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=self.exit_on_error)
        if _debug_on:
            Logg.register_method_name("json_post")
            Logg.register_method_name("json_get")
            Logg.register_method_name("get_as_json")

        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

        self.created_endp = []
        self.created_cx = []

        #CSV data collection, add files and writers
        self.port_csv_files = {}
        self.port_csv_writers = {}

        self.gen_csv_files = {}
        self.gen_csv_writers = {}

        if self.create_report:
            # create csv results writer and open results file to be written to
            #TODO add to results.csv as a 'combined' results.
            results = self.report_file_path + "/results." + self.output_format
            self.csv_results_file = open(results, "w")
            self.csv_results_writer = csv.writer(self.csv_results_file, delimiter=",")

        number_template = "000"
        if (int(self.num_stations) > 0):
            self.sta_list = self.port_name_series(prefix="sta",
                                                  start_id=int(number_template),
                                                  end_id= int(self.num_stations) + int(number_template) - 1,
                                                  padding_number=10000,
                                                  radio=self.radio)
        if (use_existing_eid):
            #split list given into a functional list used in script.
            self.use_existing_eid = use_existing_eid.split(",")
        else:
            self.use_existing_eid = use_existing_eid

        # evaluate if iperf3-server on lanforge
        if (self.target):
            if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', self.target) == None:
                #not an ip address
                self.iperf3_target_lanforge = True
            else:
                #TODO add check to self.target. ip address of lanforge port may be given by user, 
                # which specifies if lanforge server is wanted. 
                self.iperf3_target_lanforge = False

    def check_tab_exists(self):
        json_response = self.command.json_get(self.lfclient_url+"/generic/")
        if json_response is None:
            return False
        return True

    # Write initial headers to port csv file (all ports used, created & existing ports)
    def csv_add_port_column_headers(self, port_eid):
        #create file name
        file_name = self.report_file_path + "/port-" + port_eid + "." + self.outpu_format

        #open file in write mode, returns TextIOWrapper
        txt_strm = open(file_name, "w")

        #create writer
        port_csv_writer = csv.writer(txt_strm, delimiter=",")

        #save writer and TextIOWrapper
        self.port_csv_files[port_eid] = txt_strm
        self.port_csv_writers[port_eid] = port_csv_writer

        #write headers
        port_csv_writer.writerow(self.port_mgr_cols)

        #flush stream
        txt_strm.flush()

    # write initial headers to gen cx files
    def csv_add_gen_column_headers(self, gen_endp):
        #create file name
        file_name = self.report_file_path + "/gen-endp-" + gen_endp + "." + self.output_format

        #open file in write mode, returns TextIOWrapper
        txt_strm = open(file_name, "w")

        #create writer
        gen_csv_writer = csv.writer(txt_strm, delimiter=",")

        #save writer and TextIOWrapper
        self.gen_csv_files[gen_endp] = txt_strm
        self.gen_csv_writers[gen_endp] = gen_csv_writer

        #write headers
        gen_csv_writer.writerow(self.gen_tab_cols)

        #flush stream
        txt_strm.flush()
    
    def write_port_csv(self, eid):
        port_shelf, port_resource, port_name, *nil = self.name_to_eid(eid)
        # get writer
        port_csv_writer = self.port_csv_writers[eid]
        port_csv_file = self.port_csv_files[eid]

        #write fields to string, to add to json_get command
        fields_str = "fields="
        for cols in self.port_mgr_cols[:-1]:
            fields_str = fields_str + "" + cols +","
        fields_str = fields_str + self.port_mgr_cols[-1] #add last field

        # fetch data w/json
        json_url = "%s/ports/%s/%s/%s?%s" % (self.lfclient_url, port_shelf, port_resource, port_name, fields_str)
        json_response = self.query.json_get(url=json_url,
                                            debug=self.debug)
        
        #append fetched data to row, to add to csv file
        row = []
        if (json_response is not None):
            json_re_intf = json_response['interface']
            for field in self.port_mgr_cols:
                row.append(json_re_intf[field])

        # post data to csv file on disk
        port_csv_writer.writerow(row)
        port_csv_file.flush()

    def write_gen_csv(self, endp):
        # get writer
        gen_csv_writer = self.gen_csv_writers[endp]
        gen_csv_file = self.gen_csv_files[endp]

        #write fields to string, to add to json_get command
        fields_str = "fields="
        for cols in self.gen_tab_cols[:-1]:
            fields_str = fields_str + "" + cols +","
        fields_str = fields_str + self.gen_tab_cols[-1] #add last field
        # fetch data w/json
        json_url = "%s/generic/%s?%s" % (self.lfclient_url, endp, fields_str)
        json_response = self.query.json_get(url=json_url,
                                            debug=self.debug)
        
        #append fetched data to row, to add to csv file
        row = []
        if (json_response is not None):
            json_re_intf = json_response['endpoint']
            for field in self.gen_tab_cols:
                row.append(json_re_intf[field])

        # post data to csv file on disk
        gen_csv_writer.writerow(row)
        gen_csv_file.flush()

    #TODO: This is an example and is only configured for ping currently.
    # This can be edited and added to if the user wants reporting and the test they are running is not ping.
    def generate_report(self, result_dir='Generic_Test_Report', report_path=''):
        print('Generating Report for lf_test_generic...')
        report = lf_report(_output_pdf='lf_test_generic.pdf',
                           _output_html='lf_test_generic.html',
                           _results_dir_name='lf_test_generic_report',
                           _path=self.report_file_path)
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        print('path: {}'.format(report_path))
        print('path_date_time: {}'.format(report_path_date_time))

        # setting report title
        report.set_title('Generic Test Report: Ping')
        report.build_banner()

        total_devices = 0
        if (self.sta_list):
            total_devices += len(self.sta_list)
        if (self.use_existing_eid):
            total_devices += len(self.use_existing_eid)

        # test setup info
        test_setup_info = {
            'SSID': self.ssid,
            'Security': self.security,
            'Website / IP': self.target,
            'Number of clients (virtual and real)': total_devices,
            'Duration': self.test_duration
        }

        report.test_setup_table(test_setup_data=test_setup_info, value='Test Setup Information')

        # objective and description
        report.set_obj_html(_obj_title='Objective',
                            _obj='''The objective of the Generic Ping Test is to evaluate network connectivity and measure the round-trip time taken for
                            data packets to travel from the source to the destination and back. This test helps assess the reliability and latency of the network,
                            packet loss, packet delays, or variations in response times to ensure that devices can communicate
                            effectively over the network and pinpoint potential issues affecting connectivity.
                            ''')
        report.build_objective()
        
        #TODO make graph creation customizable via command line
        #get data from saved csv.
        gen_endp_names = []
        dataset = []
        for endp_name in self.created_endp:
            gen_endp_names.append(endp_name)
            io_file = self.gen_csv_files[endp_name]
            #get csv and convert to pandas, take last row of pandas.
            #csv_df = pd.read_csv("/home/diptidhond/test_generic_1/gen-endp-ping-3.csv")
            csv_df = pd.read_csv(io_file.name)
            #edit df with columns & rows we want
            #take last row
            last_row_df = csv_df.tail(1)
            #take out all other un-necessary columns if needed
            #last_row = last_row_df[["tx pkts", "rx pkts", "dropped"]]

            #convert dataframe to 1 dimensional array, to reg list, take idx 0, append to dataset array
            array = last_row_df.to_numpy().tolist()[0]
            array_but_first = array[1:]
            dataset.append(array_but_first)

        graph = lf_bar_graph(_data_set=dataset,
                            _xaxis_name="Generic Cross-Connects",
                            _yaxis_name="Pkt Count",
                            _xaxis_categories=gen_endp_names,
                            _graph_image_name="Rx vs Tx Vs Dropped",
                            _label=["rx pkts", "tx pkts", "dropped pkts"],
                            _color=['darkorange', 'forestgreen', 'blueviolet'],
                            _color_edge='red',
                            _grp_title="Rx Pkts vs Tx Pkts vs Dropped Pkts",
                            _xaxis_step=1,
                            _show_bar_value=True,
                            _text_font=7,
                            _text_rotation=45,
                            _xticks_font=7,
                            _legend_loc="best",
                            _legend_box=(1, 1),
                            _legend_ncol=1,
                            _legend_fontsize=None,
                            _enable_csv=True)

        graph_png = graph.build_bar_graph()

        print("graph name {}".format(graph_png))

        report.set_graph_image(graph_png)
        report.move_graph_image()
        report.build_graph()

        # close report, add final touches
        report.build_custom()
        report.build_footer()
        report.write_html()
        report.write_pdf()

    def monitor_test(self):
        print("Starting monitoring")
        #TODO: add checking if stations have disconnected, try to reconnect
        #TODO: add checking if cross-connects have stopped. figure out why (if due to test being done, or if just randomly stopped.)
        #TODO: add reporting-- save data at same intervals as sleeping?
        monitor_interval = self.duration_time_to_seconds(self.monitor_interval)
        end_time = datetime.datetime.now().timestamp() + self.duration_time_to_seconds(self.test_duration)

        while (datetime.datetime.now().timestamp() < end_time):
            #write to all csv files
            if (self.create_report):
                if (self.sta_list and self.port_mgr_cols):
                    for sta_alias in self.sta_list:
                        self.write_port_csv(sta_alias)
                if (self.use_existing_eid and self.port_mgr_cols):
                    for eid in self.use_existing_eid:
                        self.write_port_csv(eid)
                if (self.created_endp and self.gen_tab_cols):
                    for endp in self.created_endp:
                        self.write_gen_csv(endp)
            time.sleep(monitor_interval)

    def start(self):
        #admin up all created stations & existing stations
        interest_flags_list = ['ifdown']
        set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= interest_flags_list)
        if self.sta_list:
            for sta_alias in self.sta_list:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                #write headers to csv
                self.csv_add_port_column_headers(sta_alias)
                self.command.post_set_port(shelf = port_shelf,
                                           resource = port_resource,
                                           port = port_name,
                                           netmask= "255.255.255.0", #sometimes the cli complains about the netmask being NA, so set it to a random netmask (netmask is overriden anyways with dhcp)
                                           current_flags= 0,
                                           interest=set_port_interest_rslt,
                                           report_timer= self.report_timer)
        
        if self.use_existing_eid:
            for eid in self.use_existing_eid:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(eid)
                #write headers to csv
                self.csv_add_port_column_headers(eid)
                self.command.post_set_port(shelf = port_shelf ,
                                        resource = port_resource,
                                        port = port_name,
                                        netmask= "255.255.255.0", #sometimes the cli complains about the netmask being NA, so set it to a random netmask(netmask is overriden anyways with dhcp)
                                        current_flags= 0,
                                        interest=set_port_interest_rslt,
                                        report_timer= self.report_timer)

        #Check if created stations admin-up and have ips
        if (self.sta_list):
            if self.wait_for_action("port", self.sta_list, "up", 3000):
                print("All created stations went admin up.")
            else:
                print("All creation stations  did not admin up.")

            if self.wait_for_action("port", self.sta_list, "ip", 3000):
                print("All creation stations got IPs")
            else:
                self.print("Stations failed to get IPs")

        #Check if existing ports admin-up and got ips
        if (self.use_existing_eid):
            if self.wait_for_action("port", self.use_existing_eid, "up", 3000):
                print("All exiting ports went admin up.")
            else:
                print("All existing ports did not admin up.")

            if self.wait_for_action("port", self.use_existing_eid, "ip", 3000):
                print("All existing ports got IPs")
            else:
                self.print("All existing ports failed to get IPs")

        #at this point, all endpoints have been created, start all endpoints
        if self.created_cx:
            for cx in self.created_cx:
                self.command.post_set_cx_state(cx_name= cx,
                                               cx_state="RUNNING",
                                               test_mgr="default_tm",
                                               debug=self.debug)

    def stop(self):
        logger.info("Stopping Test...")
        # set_cx_state default_tm CX_ping-hi STOPPED
        if self.created_cx:
            for cx in self.created_cx:
                self.command.post_set_cx_state(cx_name= cx,
                                               cx_state="STOPPED",
                                               test_mgr="default_tm",
                                               debug=self.debug)
        #admin stations down
        if self.sta_list:
            for sta_alias in self.sta_list:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                self.command.post_set_port(shelf = port_shelf,
                                           resource = port_resource,
                                           port = port_name,
                                           current_flags= 1,  # vs 0x0 = interface up
                                           interest=8388610, # = current_flags + ifdown
                                           report_timer= self.report_timer)
        #admin stations down
        if self.use_existing_eid:
            for eid in self.use_existing_eid:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(eid)
                self.command.post_set_port(shelf = port_shelf,
                                           resource = port_resource,
                                           port = port_name,
                                           current_flags= 1, # vs 0x0 = interface up
                                           interest=8388610, # = current_flags + ifdown
                                           report_timer= self.report_timer)

    def build(self):
        #create stations
        if self.sta_list:
            logger.info("Creating stations")
            types = {"wep": "wep_enable", "wpa": "wpa_enable", "wpa2": "wpa2_enable", "wpa3": "use-wpa3", "open": "[BLANK]"}
            if self.security in types.keys():
                add_sta_flags = []
                set_port_interest = ['rpt_timer','current_flags', 'dhcp']
                set_port_current=['use_dhcp']
                #add appropriate flags for security
                if self.security != "open":
                    add_sta_flags.extend([types[self.security], "create_admin_down"])

                #go through each test-created station and create station in lanforge
                for sta_alias in self.sta_list:
                    port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                    sta_flags_rslt = self.command.set_flags(LFJsonCommand.AddStaFlags, starting_value=0, flag_names= add_sta_flags)
                    set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= set_port_interest)
                    set_port_current_rslt=self.command.set_flags(LFJsonCommand.SetPortCurrentFlags, starting_value=0, flag_names= set_port_current)
                    if self.security == "wpa3":
                        self.command.post_add_sta(flags=sta_flags_rslt,
                                                flags_mask=sta_flags_rslt,
                                                radio=self.radio,
                                                resource=port_resource,
                                                shelf=port_shelf,
                                                sta_name=port_name,
                                                ieee80211w=2,
                                                mode=0,
                                                mac="xx:xx:xx:*:*:xx",
                                                ssid=self.ssid,
                                                key=self.passwd,
                                                debug=self.debug)

                    else:
                        self.command.post_add_sta(flags=sta_flags_rslt,
                                                flags_mask=sta_flags_rslt,
                                                radio=self.radio,
                                                resource=port_resource,
                                                shelf=port_shelf,
                                                mac="xx:xx:xx:*:*:xx",
                                                key=self.passwd,
                                                mode=0,
                                                ssid=self.ssid,
                                                sta_name=port_name,
                                                debug=self.debug)
                    #tell lanforge to show ports
                    self.command.post_nc_show_ports(port=port_name,
                                                    resource=port_resource,
                                                    shelf=port_shelf)

                    #wait until port appears
                    wfa_list = [sta_alias]
                    self.wait_for_action("port", wfa_list, "appear", 3000)

                    # set use_dhcp and rpt_timer
                    self.command.post_set_port(alias=port_name,
                                               port=port_name,
                                               shelf=port_shelf,
                                               interest=set_port_interest_rslt,
                                               current_flags=set_port_current_rslt,
                                               report_timer=self.report_timer,
                                               debug=self.debug,
                                               resource=port_resource)
                    
            else:
                raise ValueError("security type given: %s : is invalid. Please set security type as wep, wpa, wpa2, wpa3, or open." % self.security)
        if (self.test_type == 'iperf3'):
            #admin up server port, we need IP for client generic endp creation.
            # This code is only executed if we are NOT given a target ip address. (e.g. given 1.1.eth2 instead of 192.168.101.3)
            if (self.iperf3_target_lanforge):
                server_shelf, server_resource, server_port_name, *nil = self.name_to_eid(self.target)
                set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= ['ifdown'])
                self.command.post_set_port(shelf = server_shelf,
                                            resource = server_resource,
                                            port = server_port_name,
                                            netmask= "255.255.255.0", #sometimes the cli complains about the netmask being NA, so set it to a random netmask(netmask is overriden anyways with dhcp)
                                            current_flags= 0,
                                            interest=set_port_interest_rslt,
                                            report_timer= self.report_timer)
                self.wait_for_action("port", [self.target], "up", 3000)
                self.wait_for_action("port", [self.target], "ip", 3000)


        #create endpoints
        #create 1 endp for each eid.
        unique_alias = 0
        if self.sta_list:
            unique_alias += len(self.sta_list)
        if self.use_existing_eid:
            unique_alias += len(self.use_existing_eid)

        #these cannot be interop clients
        if self.sta_list:
            for sta_alias in self.sta_list:
                sta_eid = self.name_to_eid(sta_alias)
                self.create_generic_endp(sta_eid, self.test_type, unique_alias, interop_device=False)
                unique_alias-=1

        #check if these are interop devices..
        if self.use_existing_eid: #use existing eid will have iperf3-server eid, if we are using lanforge iperf3-server.
            for eid_alias in self.use_existing_eid:
                eid_list = self.name_to_eid(eid_alias)
                is_interop = self.is_device_interop(eid_list)
                self.create_generic_endp(eid_list, self.test_type, unique_alias, interop_device = is_interop)
                unique_alias-=1

        #show all endps
        self.command.post_nc_show_endpoints(endpoint= 'all', extra ='history')

        #create cross-connects
        if self.created_endp is not None:
            for endp in self.created_endp:
                endp_cx_name = "CX_" + endp
                self.command.post_add_cx(alias= endp_cx_name,
                                         test_mgr="default_tm",
                                         rx_endp= "D_"+endp,
                                         tx_endp= endp,
                                         debug=self.debug)
                self.created_cx.append(endp_cx_name)

        #wait for cross-connects to appear
        if self.wait_for_action("cx", self.created_endp, "appear", 3000):
            print("Generic cx creation completed.")
        else:
            print("Generic cx creation was not completed.")
    
    #This function takes an eid list and returns an ip address.
    def eid_to_ip(self, eid_list):
        device_shelf, device_resource, device_port_name, *nil = eid_list
        json_url = "%s/ports/%s/%s/%s?fields=device,ip" % (self.lfclient_url, device_shelf, device_resource, device_port_name)
        json_response = self.query.json_get(url=json_url,
                                            debug=self.debug)
        if json_response is not None and (json_response['interface']['ip'] != "0.0.0.0"):
            return json_response['interface']['ip']
        else:
            return None

    #This function takes eid_list and returns interop device type or False.
    def is_device_interop(self, eid_list):
        device_shelf, device_resource, device_port_name, *nil = eid_list
        json_url = "%s/ports/%s/%s/%s?fields=hw version" % (self.lfclient_url, device_shelf, device_resource, device_port_name)
        json_response = self.query.json_get(url=json_url,
                                            debug=self.debug)
        if json_response is not None:
            return json_response['hw version']
        else:
            return False
                    
    def create_generic_endp(self, eid_list, type, unique_num, interop_device):
        """
        :param eid: list format of eid. example: ['1', '1', 'sta0010']
        :param type: takes type of generic test: 'ping', 'iperf3-client', 'iperf3-server', 'lfcurl', 'speedtest', 'iperf'
        :param unique_num: takes in unique ending prefix. example: 3
        :param interop device: is this station interop?
        :return: no return
        """
        unique_alias = type + "-" + str(unique_num)
        #construct generic endp command

        cmd = ""
        eid_shelf, eid_resource, eid_name, *nil = eid_list
        if (self.cmd):
            cmd=self.cmd
        elif (type == 'iperf3'):
            if (self.iperf3_target_lanforge):
                if (eid_list == self.name_to_eid(self.target)):
                    unique_alias = "server-" + unique_alias
                    cmd = self.do_iperf('server', unique_alias, eid_list)
                else:
                    unique_alias = "client-" + unique_alias
                    cmd = self.do_iperf('client', unique_alias, eid_list)
            else:
                #the case that user chose to not to use and create lanforge iperf server 
                unique_alias = "client-" + unique_alias
                cmd = self.do_iperf('client', unique_alias, eid_list)

        elif (type == 'ping'):
            standard_ping = True
            if (interop_device):
                standard_ping = False
                os_type = interop_device
                #construct ping command based on interop device type
                if 'Win/x86' in os_type:
                    cmd = "py lfping.py -S %s -n -1 -dest_ip %s" % (self.eid_to_ip(eid_name), self.target)
                elif 'Apple/x86' in os_type:
                    cmd = "lfping -b %s -i %s %s" % (eid_name, self.interval, self.target)
                elif 'Linux/x86' in os_type:
                    standard_ping = True
                else:
                    #Android
                    cmd = "ping -i %s %s" % (self.interval, self.target)

            if (standard_ping):
                # lfping  -s 128 -i 0.1 -c 10000 -I sta0000 www.google.com
                cmd = "lfping"
                if (self.interval):
                    cmd = cmd + " -i %d" % self.interval
                if (self.loop_count):
                    cmd = cmd + " -c %d" % self.loop_count
                cmd = cmd + " -I %s " % eid_name
                if (self.target):
                    cmd = cmd + str(self.target)
  
        elif (type == 'iperf3-client'):
            #  iperf3 --forceflush --format k --precision 4 -c 192.168.10.1 -t 60 --tos 0 -b 1K --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
            cmd = self.do_iperf('client', unique_alias, eid_list)

        elif (self.test_type == 'iperf3-server'):
            # iperf3 --forceflush --format k --precision 4 -s --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
            cmd = self.do_iperf('server', unique_alias, eid_list)

        elif (self.test_type == 'lfcurl'):
            # ./scripts/lf_curl.sh  -p sta0000 -i 192.168.50.167 -o /dev/null -n 1 -d 8.8.8.8
            cmd = cmd + str("./scripts/lf_curl.sh -p %s" % eid_name)
            #TODO: get ip address of -i (sta0000) if i is a station, but not if eth port.
            if (self.file_output_lfcurl):
                cmd = cmd + " -o %s" % self.file_output_lfcurl
            if (self.loop_count):
                cmd = cmd + " -n %i" % self.loop_count
            if (self.destination_url_lfcurl):
                cmd = cmd + " -d %s" % self.destination_url_lfcurl
        elif (self.test_type == 'speedtest'):
            if (self.spdtest_ookla):
                cmd = "speedtest --interface=%s --format=csv" % eid_name
            else:
                #do lanforge speedtest
                # vrf_exec.bash eth3 speedtest-cli --csv --share --single --debug
                # vrf_exec.bash eth3 speedtest-cli --csv --no-upload
                # vrf_exec.bash eth3 speedtest-cli --csv
                cmd = cmd + "vrf_exec.bash %s speedtest-cli --csv" % eid_name # bas command
                if (self.spdtest_enable_report):
                    cmd = cmd + " --share"
                if (self.spdtest_no_download):
                    cmd = cmd + " --no_download"
                if (self.spdtest_no_upload):
                    cmd = cmd + " --no_upload"
                if (self.spdtest_single_connection):
                    cmd = cmd + " --single"
                if (self.spdtest_enable_debug):
                    cmd = cmd + " --debug"
        else:
            raise ValueError("Was not able to identify type given in arguments.")

        #create initial generic endp
        #  add_gen_endp testing 1 1 sta0000 gen_generic
        self.command.post_add_gen_endp(alias = unique_alias,
                                       shelf=eid_shelf,
                                       resource=eid_resource,
                                       port=eid_name,
                                       p_type="gen_generic")

        self.created_endp.append(unique_alias)
        
        #did generic endp appear in port manager?
        if self.wait_for_action("endp", self.created_endp, "appear", 3000):
            print("Generic endp creation completed.")
        else:
            print("Generic endps were not created.")

        print("This is the generic cmd we are sending to server...:   " + cmd)
        self.command.post_set_gen_cmd(name = unique_alias,
                                      command= cmd)

        #add headers to endp file if user asks to create report
        if (self.create_report):
            self.csv_add_gen_column_headers(unique_alias)

        
    def do_iperf (self, type, alias, eid):
        """
        :param type: takes in options 'client' or 'server'
        :param alias: takes in alias. example: 'sta0000'
        :param eid: takes in eid list. ['1','1','sta0000']
        :return: returns constructed iperf command
        """
        #TODO: allow for multiple ports to be passed in for multiple servers on 1 eth port or 1 virt sta (for example).
        #TODO: allow for multiple targets to be passed in for multiple servers.
        cmd = "iperf3 --forceflush --format k --precision 4"
        #TODO check if dest, client_port and server_port are not empty
        eid_shelf, eid_resource, eid_name, *nil = self.name_to_eid(eid)
        if (type == 'client'):
            if (self.iperf3_target_lanforge):
                server_ip_addr = self.eid_to_ip(self.name_to_eid(self.target))
            else:
                server_ip_addr = self.target
            cmd = cmd + str(" -c %s" % server_ip_addr) + " -t 60 --tos 0 -b 1K " + str("--bind_dev %s" % eid_name)
            cmd = cmd + " -i 3 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            if (self.client_port):
                #add port that should match server_port
                cmd = cmd + " -p %s" % self.client_port
        #server
        else:
            #iperf3 --forceflush --format k --precision 4 -s --bind_dev eth2 -i 5 --pidfile /tmp/lf_helper_iperf3_server_iperf_1.pid eth2
            cmd = cmd + " -s" + str(" --bind_dev %s" % eid_name) + " -i 3 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            if (self.server_port):
                #add port that should match client port
                cmd = cmd + " -p %s" % self.server_port
        return cmd

    def cleanup(self):
        #delete all created endps, cross-connects and created stations
        logger.info("Cleaning up all cxs, endpoints, and created stations")
        if self.created_cx:
            for cx_name in self.created_cx:
                self.command.post_rm_cx(cx_name=cx_name, test_mgr="default_tm", debug=self.debug)
        if self.created_endp:
            for endp_name in self.created_endp:
                self.command.post_rm_endp(endp_name=endp_name, debug=self.debug)
        if self.sta_list:
            for sta_name in self.sta_list:
                if self.port_exists(sta_name, self.debug):
                    port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_name)
                    self.command.post_rm_vlan(port= port_name,
                                              resource= port_resource,
                                              shelf= port_shelf,
                                              debug=self.debug)

        if self.wait_for_action("port", self.sta_list, "disappear", 3000):
            print("Ports successfully cleaned up.")
        else:
            print("Ports were not successfully cleaned up.")

    def duration_time_to_seconds(self, time_string):
        #this function is used to convert self.test_duration to seconds
        if isinstance(time_string, str):
            pattern = re.compile("^(\d+)([dhms]$)")
            td = pattern.match(time_string)
            if td:
                dur_time = int(td.group(1))
                dur_measure = str(td.group(2))
                if dur_measure == "d":
                    duration_sec = dur_time * 24 * 60 * 60
                elif dur_measure == "h":
                    duration_sec = dur_time * 60 * 60
                elif dur_measure == "m":
                    duration_sec = dur_time * 60
                else:
                    duration_sec = dur_time * 1
            else:
                raise ValueError("Unknown value for time_string: %s" % time_string)
        else:
            raise ValueError("time_string must be of type str. Type %s provided" % type(time_string))
        return duration_sec
    
    def port_name_series(self, prefix="sta", start_id=0, end_id=1, padding_number=10000, radio=None):
        """
        This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
        the padding_number is added to the start and end numbers and the resulting sum
        has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
        :param radio:
        :param prefix: defaults to 'sta'
        :param start_id: beginning id
        :param end_id: ending_id
        :param padding_number: used for width of resulting station number
        :return: list of stations
        """

        if radio is not None:
            radio_shelf, radio_resource, radio_name, *nil = self.name_to_eid(radio) 

        name_list = []
        for i in range((padding_number + start_id), (padding_number + end_id + 1)):
            sta_name = "%s%s" % (prefix, str(i)[1:])
            name_list.append("%i.%i.%s" % (radio_shelf, radio_resource, sta_name))
        return name_list

    # This function takes in eid '1.1.sta0000' and returns a boolean (true or false)
    def port_exists(self, port_eid, debug=None):
        if port_eid:
            current_stations = self.query.get_port(port_eid, debug=debug)
        if current_stations:
            return True
        return False
    
    def wait_for_action(self, lf_type, type_list, action, secs_to_wait):
        """
        :param lf_type: type of object given in object list.
        :param type_list: object list that needs to be iterated through to check for attributes.
                          E.g. : (station list, port list, cx list, etc.)
        :param action: what function is waiting for, example: IP, appear, disappear.
        :param secs_to_wait: secs to wait until "wait" fails
        :return: no returns

        """
        #TODO allow test config of secs_to_wait
        if type(type_list) is not list:
            raise Exception("wait_for_action: type_list is not a list")
        else: 
            compared_pass = len(type_list)
            for attempt in range(0, int(secs_to_wait / 2)):
                passed = set()

                # Port Manager Actions
                if lf_type == "port":
                    for sta_alias in type_list:
                        port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)        
                        if action == "appear":
                            #http://192.168.102.211:8080/ports/1/1/sta0000?fields=device,down
                            json_url = "%s/ports/%s/%s/%s?fields=device,down" % (self.lfclient_url, port_resource, port_shelf, port_name)
                            json_response = self.query.json_get(url=json_url,
                                                                debug=self.debug)
                            #if sta is found by json response & not phantom
                            if json_response is not None and (json_response['interface']['down'] == True):
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))

                        elif action == "up":
                            json_url = "%s/ports/%s/%s/%s?fields=device,down" % (self.lfclient_url, port_resource, port_shelf, port_name)
                            json_response = self.query.json_get(url=json_url,
                                                                debug=self.debug)
                            #if sta is up
                            if json_response is not None and (json_response['interface']['down'] == False):
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))

                        elif action == "disappear":
                            json_url = "%s/ports/%s/%s/%s?fields=device" % (self.lfclient_url, port_resource, port_shelf, port_name)
                            json_response = self.query.json_get(url=json_url,
                                                                debug=self.debug)
                            #if device is not found
                            if json_response is None:
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))
                        elif action == "ip":
                            json_url = "%s/ports/%s/%s/%s?fields=device,ip" % (self.lfclient_url, port_resource, port_shelf, port_name)
                            json_response = self.query.json_get(url=json_url,
                                                                debug=self.debug)
                            #if device is not found
                            if json_response is not None and (json_response['interface']['ip'] != "0.0.0.0"):
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))


                # Generic Tab Actions
                else:
                    compared_pass = len(self.created_endp)
                    if action == "appear":
                        for endp_name in type_list:
                            json_url = "%s/generic/%s" % (self.lfclient_url, endp_name)
                            json_response = self.query.json_get(url=json_url,
                                                                debug=self.debug)
                            if (lf_type == "endp"):
                                if json_response is not None:
                                    passed.add(endp_name)

                            #check if cross-connect appears
                            else:
                                if json_response is not None and (json_response['endpoint']['status'] != "NO-CX"):
                                    passed.add(endp_name)

                if len(passed) < compared_pass:
                    time.sleep(2)
                    logger.info('Found %s out of %s %ss in %s out of %s tries in wait_until_%s_%s' % (len(passed), compared_pass, lf_type, attempt, int(secs_to_wait / 2), lf_type, action))
                else:
                    logger.info('All %s %ss appeared' % (len(passed), lf_type))
                    return True
        return False

    def check_args(self):
        print("Checking args passed into test")
        #TODO validate all args, depending on which test is used.
        #TODO: in args, check if file_out_lfcurl and destination_url_lfcurl is None. then state that defaults are being used and apply defaults
        if self.security != "open":
            if (self.passwd is None) or (self.passwd == ""):
                raise ValueError("use_security: %s requires passphrase or [BLANK]" % self.security)
        if ((self.test_type == "iperf3" or self.test_type == "iperf3-client") and self.target is None):
            raise ValueError ("To execute test type 'iperf3' or 'iperf3-client', a target must be specified as an IP address or port eid.")
        
    #This takes in a eid string (e.g. '1.1.sta000') and returns an eid list in list order of [shelf, resource, port name]
    def name_to_eid(self, eid_input, non_port=False):
        rv = [1, 1, "", ""]
        if (eid_input is None) or (eid_input == ""):
            logger.critical("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid_input)
            raise ValueError("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid_input)
        if type(eid_input) is not str:
            logger.critical(
                "name_to_eid wants string formatted like '1.2.name', not a tuple or list or [%s]" % type(eid_input))
            raise ValueError(
                "name_to_eid wants string formatted like '1.2.name', not a tuple or list or [%s]" % type(eid_input))

        info = eid_input.split('.')
        if len(info) == 1:
            rv[2] = info[0]  # just port name
            return rv

        if (len(info) == 2) and info[0].isnumeric() and not info[1].isnumeric():  # resource.port-name
            rv[1] = int(info[0])
            rv[2] = info[1]
            return rv

        elif (len(info) == 2) and not info[0].isnumeric():  # port-name.qvlan
            rv[2] = info[0] + "." + info[1]
            return rv

        if (len(info) == 3) and info[0].isnumeric() and info[1].isnumeric():  # shelf.resource.port-name
            rv[0] = int(info[0])
            rv[1] = int(info[1])
            rv[2] = info[2]
            return rv

        elif (len(info) == 3) and info[0].isnumeric() and not info[1].isnumeric():  # resource.port-name.qvlan
            rv[1] = int(info[0])
            rv[2] = info[1] + "." + info[2]
            return rv

        if non_port:
            # Maybe attenuator or similar shelf.card.atten.index
            rv[0] = int(info[0])
            rv[1] = int(info[1])
            rv[2] = int(info[2])
            if len(info) >= 4:
                rv[3] = int(info[3])
            return rv

        if len(info) == 4:  # shelf.resource.port-name.qvlan
            rv[0] = int(info[0])
            rv[1] = int(info[1])
            rv[2] = info[2] + "." + info[3]

        return rv

def main():

    # definition of create_basic_argparse  in lanforge-scripts/py-json/LANforge/lfcli_base.py around line 700
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Create generic endpoints and test for their ability to execute chosen commands\n''',
        description='''
        lf_test_generic.py
        --------------------
        Generic command example:
        python3 ./lf_test_generic.py
            --mgr localhost (optional)
            --mgr_port 4122 (optional)
            --upstream_port eth1 (optional)
            --radio wiphy0 (required)
            --num_stations 3 (optional)
            --security {open | wep | wpa | wpa2 | wpa3}
            --ssid netgear (required)
            --passwd admin123 (required)
            --type lfping  {generic | lfping | iperf3-client | speedtest | lf_curl} (required)
            --dest 10.40.0.1 (required - also target for iperf3)
            --test_duration 2m 
            --interval 1s 
            --debug 


            Example commands: 
            LFPING:
                ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --ssid Logan-Test-Net --passwd Logan-Test-Net 
                --security wpa2 --num_stations 4 --type lfping --dest 192.168.1.1 --debug --log_level info 
                --report_file /home/lanforge/reports/LFPING.csv --test_duration 20s --upstream_port 1.1.eth2
            LFCURL:
                ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --file_output /home/lanforge/reports/LFCURL.csv 
            IPERF:
                ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3
            SPEEDTEST:

            Port Mgr Cols available to be reported:
                4way time (us)'
                'activity'
                'alias'
                'anqp time (us)'
                'ap'
                'beacon'
                'bps rx'
                'bps rx ll'
                'bps tx'
                'bps tx ll'
                'bytes rx ll'
                'bytes tx ll'
                'channel'
                'collisions'
                'connections'
                'crypt'
                'cx ago'
                'cx time (us)'
                'device'
                'dhcp (ms)'
                'down'
                'entity id'
                'gateway ip'
                'ip'
                'ipv6 address'
                'ipv6 gateway'
                'key/phrase'
                'login-fail'
                'login-ok'
                'logout-fail'
                'logout-ok'
                'mac'
                'mask'
                'misc'
                'mode'
                'mtu'
                'no cx (us)'
                'noise'
                'parent dev'
                'phantom'
                'port'
                'port type'
                'pps rx'
                'pps tx'
                'qlen'
                'reset'
                'retry failed'
                'rx bytes'
                'rx crc'
                'rx drop'
                'rx errors'
                'rx fifo'
                'rx frame'
                'rx length'
                'rx miss'
                'rx over'
                'rx pkts'
                'rx-rate'
                'sec'
                'signal'
                'ssid'
                'status'
                'time-stamp'
                'tx abort'
                'tx bytes'
                'tx crr'
                'tx errors'
                'tx fifo'
                'tx hb'
                'tx pkts'
                'tx wind'
                'tx-failed %'
                'tx-rate'
                'wifi retries'

            Generic Tab Cols available to be reported:
                'bps rx'
                'bps tx'
                'command'
                'dropped'
                'eid'
                'elapsed'
                'entity id'
                'last results'
                'name'
                'pdu/s rx'
                'pdu/s tx'
                'rpt timer'
                'rpt#'
                'rx bytes'
                'rx pkts'
                'status'
                'tx bytes'
                'tx pkts'
                'type'
        ''',
    )
    required = parser.add_argument_group('Arguments that must be defined by user:')
    optional = parser.add_argument_group('Arguments that do not need to be defined by user:')

    required.add_argument("--lf_user", type=str, help="user: lanforge", default=None)
    required.add_argument("--lf_passwd", type=str, help="passwd: lanforge", default=None)
    required.add_argument('--test_type', type=str, help='type of command to run. Options: ping, iperf3-client, iperf3-server, iperf3, lfcurl', required=True)

    optional.add_argument('--mgr', help='ip address of lanforge script should be run on. example: 192.168.102.211', default=None)
    optional.add_argument('--mgr_port', help='port which lanforge is running on, on lanforge machine script should be run on. example: 8080', default=8080)
    optional.add_argument('--cmd', help='specifies command to be run by generic type endp', default=None)

    #generic endpoint configurations
    optional.add_argument('--spdtest_enable_debug', action="store_true", help='check enable debug box for speedtest cross connect(s)')
    optional.add_argument('--spdtest_enable_report', action="store_true", help='check enable report box for speedtest cross connect(s)')
    optional.add_argument('--spdtest_no_download', action="store_true", help='do not run download for speedtest cross connect')
    optional.add_argument('--spdtest_no_upload', action="store_true", help='do not run upload for speedtest cross connect')
    optional.add_argument('--spdtest_single_connection', action="store_true", help='run speedtest single connection')
    optional.add_argument('--spdtest_ookla', action="store_true", help='run ookla speedtest. ookla license must be on machine in order for this test to run.')
    optional.add_argument('--file_output_lfcurl', help='location to output results of lf_curl, absolute path preferred', default=None)
    optional.add_argument('--destination_url_lfcurl', help='destination url for lfcurl', default=None)
    optional.add_argument('--loop_count', help='determines the number of loops to use in lf_curl and lfping', default=None)
    optional.add_argument('--target',
                          help='Target for lfping (ex: www.google.com). ALSO ip address or LANforge eid of iperf3 server used for iperf3-client target . Example: 192.168.1.151 OR 1.1.eth2', default=None)
    optional.add_argument('--client_port', help="the port number of the iperf client endpoint. example: -p 5011",default=None)
    optional.add_argument('--server_port', help="the port number of the iperf server endpoint. example: -p 5011",default=None)

    # args for creating stations or using existing eid
    optional.add_argument('--use_existing_eid', help="EID of ports we want to use. Example: '1.1.sta000, 1.1.eth1, 1.1.eth2' ",default=None)
    optional.add_argument('--radio', help="radio that stations should be created on",default=None)
    optional.add_argument('--num_stations', help="number of stations that are to be made, defaults to 1",default=1)
    optional.add_argument('--ssid', help="ssid for stations to connect to",default=None)
    optional.add_argument('--passwd', '-p', help="password to ssid for stations to connect to",default=None)
    optional.add_argument('--mode', help='Used to force mode of stations', default=None)
    optional.add_argument('--ap', help='Used to force a connection to a particular AP, bssid of specific AP', default=None)
    optional.add_argument('--security', help='security for station ssids. options: {open | wep | wpa | wpa2 | wpa3}'  )

    # dut info
    optional.add_argument("--dut_hw_version", help="dut hw version for kpi.csv, hardware version of the device under test", default="")
    optional.add_argument("--dut_sw_version", help="dut sw version for kpi.csv, software version of the device under test", default="")
    optional.add_argument("--dut_model_num", help="dut model for kpi.csv,  model number / name of the device under test", default="")
    optional.add_argument("--dut_serial_num", help="dut serial for kpi.csv, serial number of the device under test", default="")

    # test tag info
    optional.add_argument("--test_rig", help="test rig for kpi.csv, testbed that the tests are run on", default="")
    optional.add_argument("--test_tag", help="test tag for kpi.csv,  test specific information to differentiate the test", default="")

    # args for reporting
    optional.add_argument('--output_format', help= 'choose either csv or xlsx. currently xlsx is under construction.',default='csv')
    optional.add_argument('--report_file_path', help='directory to store results in. example: /home/lanforge/reporting/file_name_wanted', default=None)
    optional.add_argument( '--gen_tab_cols', help='Columns wished to be monitored from generic endpoint tab',default= ['name', 'tx pkts', 'rx pkts', 'dropped'])
    optional.add_argument( '--port_mgr_cols', help='Columns wished to be monitored from port manager tab',default= ['ap', 'ip', 'parent dev'])
    optional.add_argument('--compared_report', help='report path and file which is wished to be compared with new report',default= None)
    optional.add_argument('--create_report',action="store_true", help='specify this flag if test should create report. This means that html, pdf, and csv data is saved and created.')

    # args for test duration & monitor interval
    optional.add_argument('--monitor_interval',help='frequency of monitors measurements;example: 250ms, 35s, 2h',default='2s')
    optional.add_argument('--test_duration', help='duration of the test eg: 30s, 2m, 4h', default="2m")

    #debug and logger
    optional.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    optional.add_argument('--lf_logger_json', help="--lf_logger_config_json <json file> , json configuration of logger")
    optional.add_argument('--debug', '-d', default=False, action="store_true", help='Enable debugging')

    #check if the arguments are empty?
    if (len(sys.argv) <= 2 and not sys.argv[1]):
        print("This python file needs the minimum required args. See add the --help flag to check out all possible arguments.")
        sys.exit(1)
        
    args = parser.parse_args()
    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_json)
    if args.create_report:
        if args.report_file_path is None:
            new_file_path = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%M-m-%S-s")).replace(':',
                                                                                                    '-') + '-lf_test_generic'  # create path name
            if os.path.exists('/home/lanforge/report-data/'):
                rpt_file_path = os.path.join('/home/lanforge/report-data/', new_file_path)
                os.mkdir(rpt_file_path)
            else:
                curr_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                rpt_file_path = os.path.join(curr_dir_path, new_file_path)
                os.mkdir(rpt_file_path)
                #create correct file path
        else:
            if not os.path.exists(args.report_file_path):
                os.mkdir(args.report_file_path)
            rpt_file_path = args.report_file_path

        if args.output_format in ['csv', 'json', 'html', 'hdf', 'stata', 'pickle', 'pdf', 'png', 'xlsx']:
            output = args.output_format
        else:
            logger.info('Not supporting report format: %s. Defaulting to csv data file output type, naming it data.csv.' % args.output_format)
            output = 'csv'

    #TODO edit name_prefix
    lf_generic_test = GenTest(host=args.mgr, port=args.mgr_port,
                             lf_user=args.lf_user, lf_passwd=args.lf_passwd,
                             radio=args.radio,
                             num_stations = args.num_stations,
                             use_existing_eid=args.use_existing_eid,
                             name_prefix="GT",
                             test_type=args.test_type,
                             target=args.target,
                             cmd=args.cmd,
                             interval=args.interval,
                             ssid=args.ssid,
                             passwd=args.passwd,
                             create_report=args.create_report,
                             port_mgr_cols=args.port_mgr_cols,
                             gen_tab_cols=args.gen_tab_cols,
                             security=args.security,
                             test_duration=args.test_duration,
                             monitor_interval=args.monitor_interval,
                             file_output_lfcurl=args.file_output_lfcurl,
                             destination_url_lfcurl = args.destination_url_lfcurl,
                             spdtest_enable_debug= args.spdtest_enable_debug,
                             spdtest_enable_report= args.spdtest_enable_report,
                             spdtest_no_download= args.spdtest_no_download,
                             spdtest_no_upload= args.spdtest_no_upload,
                             spdtest_single_connection= args.spdtest_single_connection,
                             spdtest_ookla= args.spdtest_ookla,
                             report_file_path = rpt_file_path,
                             output_format = output,
                             loop_count=args.loop_count,
                             client_port=args.client_port,
                             server_port=args.server_port,
                             _debug_on=args.debug,
                             log_level=args.log_level,
                             lf_logger_json = args.lf_logger_json)

    if not lf_generic_test.check_tab_exists():
        raise ValueError("Error received from GUI when trying to request generic tab information, please ensure generic tab is enabled")
    
    lf_generic_test.check_args()
    
    lf_generic_test.build()

    lf_generic_test.start()

    logger.info("Starting connections with 5 second settle time.")
    lf_generic_test.start()
    time.sleep(5) # give traffic a chance to get started.

    lf_generic_test.monitor_test()
    print("Done with connection monitoring")
    
    lf_generic_test.stop()
    lf_generic_test.generate_report()
    lf_generic_test.cleanup()

if __name__ == "__main__":
    main()