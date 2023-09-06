#!/usr/bin/env python3
"""
NAME: lf_test_generic.py

PURPOSE:
test_generic.py will create stations and endpoints to generate traffic based on a command-line specified command type.

This script will create a variable number of stations to test generic endpoints. Multiple command types can be tested
including ping, speedtest, generic types. The test will check the last-result attribute for different things
depending on what test is being run. Ping will test for successful pings, speedtest will test for download
speed, upload speed, and ping time, generic will test for successful generic commands

SETUP:
Enable the generic tab in LANforge GUI

STATUS: UNDER DEVELOPMENT

EXAMPLE:

    LFPING:
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --ssid Logan-Test-Net --passwd Logan-Test-Net 
        --security wpa2 --num_stations 4 --type lfping --dest 192.168.1.1 --debug --log_level info 
        --report_file /home/lanforge/reports/LFPING.csv --test_duration 20s --upstream_port 1.1.eth2
    LFCURL (under construction):
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --file_output /home/lanforge/reports/LFCURL.csv 
        --num_stations 2 --ssid Logan-Test-Net --passwd Logan-Test-Net --security wpa2 --type lfcurl --dest 192.168.1.1
    GENERIC:
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --num_stations 2 --ssid Logan-Test-Net 
        --report_file /home/lanforge/reports/GENERIC.csv --passwd Logan-Test-Net --security wpa2 --type generic
    SPEEDTEST:
        ./test_generic.py --radio 1.1.wiphy0 --num_stations 2 --report_file /home/lanforge/reports/SPEEDTEST.csv 
        --ssid Logan-Test-Net --passwd Logan-Test-Net --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security wpa2
    IPERF3 (under construction):
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3

Use './test_generic.py --help' to see command line usage and options
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

import requests
from pandas import json_normalize
import json
import traceback
from lf_json_util import standardize_json_results


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
from lanforge_client.logg import Logg

#to be deleted after using name_to_eid
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

#stand-alone (not dependent on realm)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")


logger = logging.getLogger(__name__)


if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

class GenTest():
    def __init__(self, lf_user, lf_passwd, ssid, security, passwd,
                name_prefix, num_stations, upstream=None, client_port = None,server_port=None,
                 host="localhost", port=8080, csv_outfile=None,use_existing_eid=None,
                 test_duration="5m",test_type="lfping", target=None, cmd=None, interval=1,
                 radio=None, speedtest_min_up=None, speedtest_min_dl=None, speedtest_max_ping=None,
                 file_output_lfcurl=None, lf_logger_json = None, log_level = "debug", loop_count=None,
                 _debug_on=False, _exit_on_error=False, die_on_error = False,_exit_on_fail=False):
        self.host=host
        self.port=port
        self.lf_user=lf_user
        self.lf_passwd=lf_passwd
        self.ssid = ssid
        self.radio = radio
        self.num_stations = num_stations
        self.security = security
        self.use_existing_eid= use_existing_eid
        self.speedtest_min_up = speedtest_min_up
        self.speedtest_min_dl = speedtest_min_dl
        self.speedtest_max_ping = speedtest_max_ping
        self.file_output_lfcurl = file_output_lfcurl
        self.loop_count = loop_count
        self.test_type = test_type
        self.target = target
        self.cmd = cmd
        self.interval = interval
        self.client_port = client_port
        self.server_port = server_port
        self.passwd = passwd
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.debug = _debug_on
        self.exit_on_error = _exit_on_error
        self.exit_on_fail = _exit_on_fail
        self.csv_outfile = csv_outfile
        self.lfclient_url = "http://%s:%s" % (self.host, self.port)
        self.report_timer = 1500
        self.log_level = log_level
        self.lf_logger_json = lf_logger_json

        # create a session
        # self.session = LFSession(lfclient_url="http://{lf_mgr}:{lf_port}".format(lf_mgr=self.lf_mgr, lf_port=self.lf_port),
        # session to use lanforge_api
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
        #TODO add this to args
        self.die_on_error = die_on_error

        self.created_endp = []

        number_template = "000"
        if (int(self.num_stations) > 0):
            self.sta_list = self.port_name_series(prefix="sta",
                                                  start_id=int(number_template),
                                                  end_id= int(self.num_stations) + int(number_template) - 1,
                                                  padding_number=10000,
                                                  radio=self.radio)

    def check_tab_exists(self):
        json_response = self.command.json_get(self.lfclient_url+"/generic/")
        if json_response is None:
            return False
        return True
 
    def generate_report(self, test_rig, test_tag, dut_hw_version, dut_sw_version, 
                        dut_model_num, dut_serial_num, test_id, csv_outfile,
                        monitor_endps, generic_cols):
        report = lf_report.lf_report(_results_dir_name="test_generic_test")
        kpi_path = report.get_report_path()
        print("kpi_path :{kpi_path}".format(kpi_path=kpi_path))
        kpi_csv = lf_kpi_csv.lf_kpi_csv(
            _kpi_path=kpi_path,
            _kpi_test_rig=test_rig,
            _kpi_test_tag=test_tag,
            _kpi_dut_hw_version=dut_hw_version,
            _kpi_dut_sw_version=dut_sw_version,
            _kpi_dut_model_num=dut_model_num,
            _kpi_dut_serial_num=dut_serial_num,
            _kpi_test_id=test_id)
        kpi_csv.kpi_dict['Units'] = "Mbps"

        generic_cols = [self.replace_special_char(x) for x in generic_cols]
        generic_cols.append('last results')
        generic_fields = ",".join(generic_cols)
        
        gen_url = "/generic/%s?fields=%s" % (",".join(monitor_endps), generic_fields)
        endps = standardize_json_results(self.json_get(gen_url))

        data = {}
        for endp in endps:
            data[list(endp.keys())[0]] = list(endp.values())[0]
        for endpoint in data:
            kpi_csv.kpi_csv_get_dict_update_time()
            kpi_csv.kpi_dict['short-description'] = "{endp_name}".format(
                endp_name=data[endpoint]['name'])
            kpi_csv.kpi_dict['numeric-score'] = "{endp_tx}".format(
                endp_tx=data[endpoint]['tx bytes'])
            kpi_csv.kpi_dict['Units'] = "bps"
            kpi_csv.kpi_dict['Graph-Group'] = "Endpoint TX bytes"
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

            kpi_csv.kpi_dict['short-description'] = "{endp_name}".format(
                endp_name=data[endpoint]['name'])
            kpi_csv.kpi_dict['numeric-score'] = "{endp_rx}".format(
                endp_rx=data[endpoint]['rx bytes'])
            kpi_csv.kpi_dict['Units'] = "bps"
            kpi_csv.kpi_dict['Graph-Group'] = "Endpoint RX bytes"

            kpi_csv.kpi_dict['short-description'] = "{endp_name}".format(
                endp_name=data[endpoint]['name'])
            kpi_csv.kpi_dict['numeric-score'] = "{last_results}".format(
                last_results=data[endpoint]['last results'])
            kpi_csv.kpi_dict['Units'] = ""
            kpi_csv.kpi_dict['Graph-Group'] = "Endpoint Last Results"
            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)      

        if csv_outfile is not None:
            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            csv_outfile = "{}_{}-sta_connect.csv".format(
                csv_outfile, current_time)
            csv_outfile = report.file_add_path(csv_outfile)
        print("csv output file : {}".format(csv_outfile))

    def start(self):
        #admin up all created stations & existing stations
        if self.sta_list:
            for sta_alias in self.sta_list:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                self.command.post_set_port(shelf = port_shelf,
                                           resource = port_resource,
                                           port = port_name,
                                           current_flags= 0, # vs 0x1 = interface down
                                           interest=3833610, # includes use_current_flags + dhcp + dhcp_rls + ifdown
                                           report_timer= self.report_timer)
        
        if self.use_existing_eid:
            for eid in self.sta_list:
                self.command.post_set_port(shelf = eid[0],
                                           resource = eid[1],
                                           port = eid[2],
                                           current_flags= 0, # vs 0x1 = interface down
                                           interest=3833610, # includes use_current_flags + dhcp + dhcp_rls + ifdown
                                           report_timer= self.report_timer)

        if self.wait_for_action("port", "up", 30):
            self._pass("All stations went admin up.")
        else:
            self._fail("All stations did NOT go admin up.")

        if self.wait_for_action("port", "ip", 30):
            self._pass("All stations got IPs")
        else:
            self._fail("Stations failed to get IPs")
            self.exit_fail()

        #at this point, all endpoints have been created, start all endpoints
        if self.created_endp:
            for endp_name in self.created_endp:
                self.command.post_set_cx_state(cx_name= "CX_" + endp_name,
                                               cx_state="RUNNING",
                                               test_mgr="default_tm",
                                               debug=self.debug)

    def stop(self):
        # set_cx_state default_tm CX_ping-hi STOPPED
        logger.info("Stopping Test...")
        if self.created_endp:
            for endp_name in self.created_endp:
                self.command.post_set_cx_state(cx_name= "CX_" + endp_name,
                                               cx_state="STOPPED",
                                               test_mgr="default_tm",
                                               debug=self.debug)

        if self.sta_list:
            for sta_alias in self.sta_list:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                self.command.post_set_port(shelf = port_shelf,
                                           resource = port_resource,
                                           port = port_name,
                                           current_flags= 1,  # vs 0x0 = interface up
                                           interest=8388610, # = current_flags + ifdown
                                           report_timer= self.report_timer)

        if self.use_existing_eid:
            for eid in self.sta_list:
                self.command.post_set_port(shelf = eid[0],
                                           resource = eid[1],
                                           port = eid[2],
                                           current_flags= 1, # vs 0x0 = interface up
                                           interest=8388610, # = current_flags + ifdown
                                           report_timer= self.report_timer)

    def build(self):
        #TODO move arg validation to validate_sort_args
        #create stations
        if self.sta_list:
            logger.info("Creating stations")
            types = {"wep": "wep_enable", "wpa": "wpa_enable", "wpa2": "wpa2_enable", "wpa3": "use-wpa3", "open": "[BLANK]"}
            if self.security in types.keys():
                add_sta_flags = []
                set_port_interest = []
                set_port_interest.append('rpt_timer')
                if self.security != "open":
                    if (self.passwd is None) or (self.passwd == ""):
                        raise ValueError("use_security: %s requires passphrase or [BLANK]" % self.security)
                    else:
                        add_sta_flags.extend([types[self.security], "create_admin_down"])
                for sta_alias in self.sta_list:
                    port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                    sta_flags_rslt = self.command.set_flags(LFJsonCommand.AddStaFlags, starting_value=0, flag_names= add_sta_flags)
                    set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= set_port_interest)
                    if self.security == "wpa3":
                        self.command.post_add_sta(flags=sta_flags_rslt,
                                                  flags_mask=sta_flags_rslt,
                                                  radio=self.radio,
                                                  resource=port_resource,
                                                  shelf=port_shelf,
                                                  sta_name=port_name,
                                                  ieee80211w=2,
                                                  mac="xx:xx:xx:*:*:xx",
                                                  ssid=self.ssid,
                                                  password=self.passwd,
                                                  debug=self.debug)

                    else:
                        self.command.post_add_sta(flags=sta_flags_rslt,
                                                  flags_mask=sta_flags_rslt,
                                                  radio=self.radio,
                                                  resource=port_resource,
                                                  shelf=port_shelf,
                                                  mac="xx:xx:xx:*:*:xx",
                                                  ssid=self.ssid,
                                                  password=self.passwd,
                                                  sta_name=port_name,
                                                  debug=self.debug)
                    self.command.post_set_port(alias=sta_alias,
                                               interest=set_port_interest_rslt,
                                               report_timer=self.report_timer,
                                               debug=self.debug)
            else:
                raise ValueError("security type given: %s : is invalid. Please set security type as wep, wpa, wpa2, wpa3, or open." % self.security)
        self.wait_for_action(self, "port", "appear", 30)

        #create endpoints
        #this is how many endps need to be created : 1 for each eid.
        unique_alias = len(self.sta_list) + len(self.use_existing_eid)
        if self.sta_list:
            for sta_alias in self.sta_list:
                sta_eid = self.name_to_eid(sta_alias)
                self.create_generic_endp(sta_eid, self.type, unique_alias)
                unique_alias=-1

        if self.use_existing_eid:
            for eid in self.use_existing_eid:
                self.create_generic_endp(eid, self.type, unique_alias)
                unique_alias=-1

        if self.wait_for_action("endp", "appear", 30):
            print("Generic endp creation completed.")
        else:
            print("Generic endps were not created.")
                    
    def create_generic_endp(self, eid, type, unique_num):
        #create initial generic endp
        #  add_gen_endp testing 1 1 sta0000 gen_generic
        unique_alias = type + "-" + str(unique_num)
        self.command.post_add_gen_endp(alias = unique_alias,
                                       shelf=eid[0],
                                       resource=eid[1],
                                       port=eid[2],
                                       p_type="gen_generic")
        self.created_endp.add(unique_alias)

        #edit generic endp with type we actually want to run - construct  cmd 
        cmd = ""
        cmd_iperf_server = ""
        if (self.cmd):
            cmd=self.cmd
        elif (self.type == 'ping'):
            # lfping  -s 128 -i 0.1 -c 10000 -I sta0000 www.google.com
            cmd="lfping"
            if (self.interval):
                cmd = cmd + " -i %d" % self.interval
            if (self.loop_count):
                cmd = cmd + " -c %d" % self.loop_count
            cmd = cmd + " -I %s " % eid[2]
            if (self.target):
                cmd = cmd + str(self.target)
  
        elif (self.type == 'iperf3-client'):
            #  iperf3 --forceflush --format k --precision 4 -c 192.168.10.1 -t 60 --tos 0 -b 1K --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
            cmd = self.do_iperf(self, 'client', unique_alias, eid)
        elif (self.type == 'iperf3-server'):
            # iperf3 --forceflush --format k --precision 4 -s --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
            cmd = self.do_iperf(self, 'server', unique_alias, eid)

        elif (self.type == 'iperf'):
            #TODO server part of 'iperf'
            #cmd_iperf_server = self.do_iperf(self, 'server', self.server_port, eid)
            cmd = self.do_iperf(self, 'client', unique_alias, eid)
            #self.command.post_set_gen_cmd(name = self.,
                                          #command= cmd_iperf_server)

        elif (self.type == 'lfcurl'):
            # ./scripts/lf_curl.sh  -p sta0000 -i 192.168.50.167 -o /dev/null -n 1 -d 8.8.8.8
            cmd = cmd + str("./scripts/lf_curl.sh -p %s" % eid[2])
            # cmd = cmd + "-i %s" % str(self.target) TODO: get ip address of -i (sta0000) if i is a station, but not if eth port.
            #TODO add -o
            cmd = cmd + "-o /dev/null -n 1 -d %s" % str(self.target)

        else:
            raise ValueError("Was not able to identify type given in arguments.")
        self.command.post_set_gen_cmd(name = unique_alias,
                                      command= cmd)
        
    def do_iperf (self, type, alias, eid):
        cmd = "iperf3 --forceflush --format k --precision 4"
        #TODO check if dest, client_port and server_port are not empty
        if (type == 'client'):
            cmd = cmd + str("-c %s" % self.target) + " -t 60 --tos 0 -b 1K" + str("--bind_dev %s" % eid[2])
            cmd = cmd + " -i 5 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            cmd = cmd + " -p %d" % self.client_port
        else:
            cmd = cmd + str("--bind_dev %s" % eid[2])
            cmd = cmd + " -i 5 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            cmd = cmd + " -p %d" % self.server_port
        return cmd

    def cleanup(self):
        logger.info("Cleaning up all cxs and endpoints.")
        #if self.created_cx:
            #for cx_name in self.created_cx:
                #self.command.post_rm_cx(cx_name=cx_name, test_mgr="default_tm", debug=self.debug)
        if self.created_endp:
            for endp_name in self.created_endp:
                self.command.post_rm_endp(endp_name=endp_name, debug=self.debug)
        if self.sta_list:
            for sta_name in self.sta_list:
                if self.port_exists(self, self.name_to_eid(sta_name), self.debug):
                    self.command.post_rm_vlan(port=sta_name, debug=self.debug)

        if self.wait_for_action(self, "port", "disappear", 30):
            self._pass("Ports successfully cleaned up.")
        else:
            self._fail("Ports NOT successfully cleaned up.")
    
    def port_name_series(self, prefix="sta", start_id=0, end_id=1, padding_number=10000, radio=None):
        """
        This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
        the padding_number is added to the start and end numbers and the resulting sum
        has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
        @deprecated -- please use port_name_series
        :param radio:
        :param prefix: defaults to 'sta'
        :param start_id: beginning id
        :param end_id: ending_id
        :param padding_number: used for width of resulting station number
        :return: list of stations
        """

        eid = None
        if radio is not None:
            eid = self.name_to_eid(radio)

        name_list = []
        for i in range((padding_number + start_id), (padding_number + end_id + 1)):
            sta_name = "%s%s" % (prefix, str(i)[1:])
            if eid is None:
                name_list.append(sta_name)
            else:
                name_list.append("%i.%i.%s" % (eid[0], eid[1], sta_name))
        return name_list

    def port_exists(self, port_eid, debug=None):
        if port_eid:
            current_stations = self.query.get_port(list(port_eid), debug=debug)
        if current_stations:
            return True
        return False
    
    def wait_for_action(self, object, action, secs_to_wait):
        for attempt in range(0, int(secs_to_wait / 2)):
            passed = set()

            # Port Manager Actions
            if object == "port":
                if self.sta_list:
                    for sta_alias in self.sta_list:
                        port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                        if action == "appear":
                            compared_pass = len(self.sta_list)
                            json_response = self.command.post_show_ports(port= port_name,
                                                                        resource=port_resource,
                                                                        shelf=port_shelf,
                                                                        debug=self.debug
                                                                        )
                            #if sta is found by json response
                            if ((json_response is not None)
                            and (not json_response['interface']['phantom'])
                            and (not json_response['status']['NOT_FOUND'])):
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))
                        elif action == "up":
                            compared_pass = len(self.sta_list)
                            json_response = self.command.post_show_ports(port= port_name,
                                                resource=port_resource,
                                                shelf=port_shelf,
                                                debug=self.debug
                                                )
                            #if sta is NOT down
                            if (json_response is not None) and not json_response['interface']['down'] and not json_response['status']['NOT_FOUND']:
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))

                        elif action == "disappear":
                            compared_pass = len(self.sta_list)
                            json_response = self.command.post_show_ports(port= port_name,
                                                resource=port_resource,
                                                shelf=port_shelf,
                                                debug=self.debug
                                                )
                            if (json_response is not None) and json_response['status']['NOT_FOUND']:
                                passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))

                #loop for existing eids
                if self.use_existing_eid and action == "up":
                    for sta_alias in self.use_existing_eid :
                        compared_pass += len(self.use_existing_eid)
                        port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
                        json_response = self.command.post_show_ports(port= port_name,
                                            resource=port_resource,
                                            shelf=port_shelf,
                                            debug=self.debug
                                            )
                                                #our station interface is NOT down
                        if (json_response is not None) and not json_response['interface']['down'] and not json_response['status']['NOT_FOUND']:
                            passed.add("%s.%s.%s" % (port_shelf, port_resource, port_name))
    
                if len(passed) < compared_pass:
                    time.sleep(2)
                    logger.info('Found %s out of %s ports in %s out of %s tries in wait_until_ports_appear' % (len(passed), len(self.sta_list), attempt, timeout/2))
                    return False
                else:
                    logger.info('All %s ports appeared' % len(passed))
                    return True

            # Generic Tab Actions
            else:
                if action == "appear":
                    if self.created_endp:
                        for endp_name in self.created_endp:
                            compared_pass = len(self.created_endp)
                            json_response = self.command.post_nc_show_endpoints(endpoint=endp_name,
                                                                                    extra ='history')
                        if (json_response['endpoint']['name'] == endp_name):
                                passed.add(endp_name)
                if len(passed) < compared_pass:
                    time.sleep(2)
                    logger.info('Found %s out of %s ports in %s out of %s tries in wait_until_ports_appear' % (len(found_stations), len(self.sta_list), attempt, timeout/2))
                    return False
                else:
                    logger.info('All %s ports appeared' % len(passed))
                    return True

    def validate_sort_args(self, args):
        print(args)
        #TODO validate all args, depending on which test is used.
        # if (args.target):
        #     # get ip upstream port
        #     rv = self.name_to_eid(args.upstream_port)
        #     shelf = rv[0]
        #     resource = rv[1]
        #     port_name = rv[2]
        #     request_command = 'http://{lfmgr}:{lfport}/port/1/{resource}/{port_name}'.format(
        #     lfmgr=args.mgr, lfport=args.mgr_port, resource=resource, port_name=port_name)
        #     logger.info("port request command: {request_command}".format(request_command=request_command))

        #     request = requests.get(request_command, auth=(args.lf_user, args.lf_passwd))
        #     logger.info("port request status_code {status}".format(status=request.status_code))

        #     lanforge_json = request.json()
        #     lanforge_json_formatted = json.dumps(lanforge_json, indent=4)        
        #     try: 
        #         key = 'interface'
        #         df = json_normalize(lanforge_json[key])
        #         args.dest = df['ip'].iloc[0]
        #     except Exception as x:
        #         traceback.print_exception(Exception, x, x.__traceback__, chain=True)
        #         logger.error("json returned : {lanforge_json_formatted}".format(lanforge_json_formatted=lanforge_json_formatted))

            # if file path with output file extension is not given...
            # check if home/lanforge/report-data exists. if not, save
            # in new folder based in current file's directory

        systeminfopath = None
        if args.report_file is None:
            new_file_path = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%M-m-%S-s")).replace(':','-') + '-test_generic'  # create path name
            if os.path.exists('/home/lanforge/report-data/'):
                path = os.path.join('/home/lanforge/report-data/', new_file_path)
                os.mkdir(path)
            else:
                curr_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(curr_dir_path, new_file_path)
                os.mkdir(path)
            systeminfopath = str(path) + '/systeminfo.txt'

            if args.output_format in ['csv', 'json', 'html', 'hdf', 'stata', 'pickle', 'pdf', 'png', 'xlsx']:
                report_f = str(path) + '/data.' + args.output_format
                output = args.output_format
            else:
                logger.info('Not supporting report format: %s. Defaulting to csv data file output type, naming it data.csv.' % args.output_format)
                report_f = str(path) + '/data.csv'
                output = 'csv'
        else:
            systeminfopath = str(args.report_file).split('/')[-1]
            report_f = args.report_file
            if args.output_format is None:
                output = str(args.report_file).split('.')[-1]
            else:
                output = args.output_format
        logger.warning("Saving final report data in: " + report_f)

        # Retrieve last data file
        compared_rept = None
        if args.compared_report:
            compared_report_format = args.compared_report.split('.')[-1]
            # if compared_report_format not in ['csv', 'json', 'dta', 'pkl','html','xlsx','h5']:
            if compared_report_format != 'csv':
                raise ValueError("Cannot process this file type. Please select a different file and re-run script.")
            else:
                compared_rept = args.compared_report

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
        test_generic.py
        --------------------
        Generic command example:
        python3 ./test_generic.py 
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
                ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --ssid Logan-Test-Net --passwd Logan-Test-Net 
                --security wpa2 --num_stations 4 --type lfping --dest 192.168.1.1 --debug --log_level info 
                --report_file /home/lanforge/reports/LFPING.csv --test_duration 20s --upstream_port 1.1.eth2
            LFCURL:
                ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --file_output /home/lanforge/reports/LFCURL.csv 
                --num_stations 2 --ssid Logan-Test-Net --passwd Log
                sta_names_ = LFUtils.portNameSeries(prefix_="sta",
                                                start_id_=int(self.number_template),
                                                end_id_=num_stations + int(self.number_template) - 1,
                                                padding_number_=10000,
                                                radio=radio)e speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security wpa2
            IPERF3 (under construction):
                ./test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3
        ''',
    )
    required = parser.add_argument_group('Arguments that must be defined by user:')
    optional = parser.add_argument_group('Arguements that do not need to be defined by user:')

    required.add_argument("--lf_user", type=str, help="user: lanforge", default=None)
    required.add_argument("--lf_passwd", type=str, help="passwd: lanforge", default=None)
    required.add_argument('--type', type=str, help='type of command to run: ping, iperf3-client, iperf3-server, iperf, lfcurl', required=True)

    optional.add_argument('--mgr', help='specifies command to be run by generic type endp', default=None)
    optional.add_argument('--mgr_port', help='specifies command to be run by generic type endp', default=8080)
    optional.add_argument('--cmd', help='specifies command to be run by generic type endp', default=None)

    #generic endpoint configurations
    optional.add_argument('--interval', help='interval to use when running lfping. in seconds', default=1)
    optional.add_argument('--speedtest_min_up', help='sets the minimum upload threshold for the speedtest type', default=None)
    optional.add_argument('--speedtest_min_dl', help='sets the minimum download threshold for the speedtest type', default=None)
    optional.add_argument('--speedtest_max_ping', help='sets the minimum ping threshold for the speedtest type', default=None)
    optional.add_argument('--file_output_lfcurl', help='location to output results of lf_curl, absolute path preferred', default=None)
    optional.add_argument('--loop_count', help='determines the number of loops to use in lf_curl and lfping', default=None)
    optional.add_argument('--target', help='Target for lfping and iperf-client', default=None)
    optional.add_argument('--client_port', help="the port number of the iperf client endpoint",default=None)
    optional.add_argument('--server_port', help="the port number of the iperf server endpoint",default=None)

    # args for creating stations or using existing eid
    optional.add_argument('--use_existing_eid', help="EID of ports we want to use (in list form)",default=None)
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
    optional.add_argument('--output_format', help= 'choose either csv or xlsx',default='csv')
    optional.add_argument('--csv_outfile', help="output file for csv data", default="test_generic_kpi")
    optional.add_argument('--report_file', help='where you want to store results', default=None)
    optional.add_argument( '--a_min', help= '--a_min bps rate minimum for side_a', default=256000)
    optional.add_argument('--b_min', help= '--b_min bps rate minimum for side_b', default= 256000)
    optional.add_argument( '--gen_cols', help='Columns wished to be monitored from layer 3 endpoint tab',default= ['name', 'tx bytes', 'rx bytes'])
    optional.add_argument( '--port_mgr_cols', help='Columns wished to be monitored from port manager tab',default= ['ap', 'ip', 'parent dev'])
    optional.add_argument('--compared_report', help='report path and file which is wished to be compared with new report',default= None)
    optional.add_argument('--monitor_interval',help='how frequently do you want your monitor function to take measurements; 250ms, 35s, 2h',default='2s')
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


    #TODO edit name_prefix
    generic_test = GenTest(host=args.mgr, port=args.mgr_port,
                           lf_user=args.lf_user, lf_passwd=args.lf_passwd,
                           radio=args.radio,
                           num_stations = args.num_stations,
                           use_existing_eid=args.use_existing_eid,
                           name_prefix="GT",
                           test_type=args.type,
                           target=args.target,
                           cmd=args.cmd,
                           interval=args.interval,
                           ssid=args.ssid,
                           passwd=args.passwd,
                           security=args.security,
                           test_duration=args.test_duration,
                           speedtest_min_up=args.speedtest_min_up,
                           speedtest_min_dl=args.speedtest_min_dl,
                           speedtest_max_ping=args.speedtest_max_ping,
                           file_output_lfcurl=args.file_output_lfcurl,
                           csv_outfile=args.csv_outfile,
                           loop_count=args.loop_count,
                           client_port=args.client_port,
                           server_port=args.server_port,
                           _debug_on=args.debug,
                           log_level=args.log_level,
                           lf_logger_json = args.lf_logger_json)

    if not generic_test.check_tab_exists():
        raise ValueError("Error received from GUI when trying to request generic tab information, please ensure generic tab is enabled")
    
    generic_test.validate_sort_args(args)
    #generic_test.cleanup(sta_list)
    generic_test.build()
    if not generic_test.passes():
        logger.error(generic_test.get_fail_message())
        generic_test.exit_fail()
    generic_test.start()
    if not generic_test.passes():
        logger.error(generic_test.get_fail_message())
        generic_test.exit_fail()

    if type(args.gen_cols) is not list:
        generic_cols = list(args.gen_cols.split(","))
        # send col names here to file to reformat
    else:
        generic_cols = args.gen_cols
        # send col names here to file to reformat
    if type(args.port_mgr_cols) is not list:
        port_mgr_cols = list(args.port_mgr_cols.split(","))
        # send col names here to file to reformat
    else:
        port_mgr_cols = args.port_mgr_cols
        # send col names here to file to reformat
    logger.info("Generic Endp column names are...")
    logger.info(generic_cols)
    logger.info("Port Manager column names are...")
    logger.info(port_mgr_cols)
    # try:
    #     monitor_interval = Realm.parse_time(args.monitor_interval).total_seconds()
    # except ValueError as error:
    #     raise ValueError("The time string provided for monitor_interval argument is invalid. Please see supported time stamp increments and inputs for monitor_interval in --help. %s" % error)

    logger.info("Starting connections with 5 second settle time.")
    generic_test.start()
    time.sleep(5) # give traffic a chance to get started.

    must_increase_cols = None
    if args.type == "lfping":
        must_increase_cols = ["rx bytes"]
    mon_endp = generic_test.generic_endps_profile.created_endp
    generic_test.generate_report(test_rig=args.test_rig, test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                               dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                               dut_serial_num=args.dut_serial_num, test_id=args.test_id, csv_outfile=args.csv_outfile,
                               monitor_endps=mon_endp, generic_cols=generic_cols)
    # generic_test.generic_endps_profile.monitor(generic_cols=generic_cols,
    #                                            must_increase_cols=must_increase_cols,
    #                                            sta_list=sta_list,
    #                                            resource_id=resource_id,
    #                                            # port_mgr_cols=port_mgr_cols,
    #                                            report_file=report_f,
    #                                            systeminfopath=systeminfopath,
    #                                            duration_sec=Realm.parse_time(args.test_duration).total_seconds(),
    #                                            monitor_interval=monitor_interval,
    #                                            monitor_endps=mon_endp,
    #                                            output_format=output,
    #                                            compared_report=compared_rept,
    #                                            script_name='test_generic',
    #                                            arguments=args,
    #                                            debug=args.debug)

    logger.info("Done with connection monitoring")
    generic_test.stop()

    generic_test.cleanup()


    if len(generic_test.get_passed_result_list()) > 0:
        logger.info("Test-Generic Passing results:\n%s" % "\n".join(generic_test.get_passed_result_list()))
    if len(generic_test.generic_endps_profile.get_passed_result_list()) > 0:
        logger.info("Test-Generic Monitor Passing results:\n%s" % "\n".join(generic_test.generic_endps_profile.get_passed_result_list()))
    if len(generic_test.get_failed_result_list()) > 0:
        logger.warning("Test-Generic Failing results:\n%s" % "\n".join(generic_test.get_failed_result_list()))
    if len(generic_test.generic_endps_profile.get_failed_result_list()) > 0:
        logger.warning("Test-Generic Monitor Failing results:\n%s" % "\n".join(generic_test.generic_endps_profile.get_failed_result_list()))

    generic_test.generic_endps_profile.print_pass_fail()
    if generic_test.passes() and generic_test.generic_endps_profile.passes():
        generic_test.exit_success()
    else:
        generic_test.exit_fail()

if __name__ == "__main__":
    main()