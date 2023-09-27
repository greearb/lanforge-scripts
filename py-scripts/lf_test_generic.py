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

EXAMPLE:

    LFPING :
        ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --ssid Logan-Test-Net --passwd Logan-Test-Net 
        --security wpa2 --num_stations 4 --type lfping --dest 192.168.1.1 --debug --log_level info 
        --report_file /home/lanforge/reports/LFPING.csv --test_duration 20s --upstream_port 1.1.eth2
    LFCURL :
        ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --file_output /home/lanforge/reports/LFCURL.csv 
        --num_stations 2 --ssid Logan-Test-Net --passwd Logan-Test-Net --security wpa2 --type lfcurl --dest 192.168.1.1
    GENERIC :
        ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --num_stations 2 --ssid Logan-Test-Net 
        --report_file /home/lanforge/reports/GENERIC.csv --passwd Logan-Test-Net --security wpa2 --type generic
    SPEEDTEST :
        ./lf_test_generic.py --radio 1.1.wiphy0 --num_stations 2 --report_file /home/lanforge/reports/SPEEDTEST.csv 
        --ssid Logan-Test-Net --passwd Logan-Test-Net --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security wpa2
    IPERF3 :
        ./lf_test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3

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
import re

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


logger = logging.getLogger(__name__)


if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

class GenTest():
    def __init__(self, lf_user, lf_passwd, ssid, security, passwd,
                name_prefix, num_stations, client_port = None,server_port=None,
                 host="localhost", port=8080, csv_outfile=None, use_existing_eid=None, monitor_interval = "2s",
                 test_duration="20s",test_type="ping", target=None, target_port_alias=None, cmd=None, interval=0.1,
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
        self.file_output_lfcurl = file_output_lfcurl
        self.loop_count = loop_count
        self.test_type = test_type
        self.target = target
        self.target_port_alias = target_port_alias
        self.cmd = cmd
        self.monitor_interval = monitor_interval
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
        self.created_cx = []

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

    def monitor_test(self):
        print("Starting monitoring")
        #TODO: add checking if stations have disconnected, try to reconnect
        #TODO: add checking if cross-connects have stopped. figure out why (if due to test being done, or if just randomly stopped.)
        #TODO: add reporting-- save data at same intervals as sleeping?
        monitor_interval = self.duration_time_to_seconds(self.monitor_interval)
        end_time = datetime.datetime.now().timestamp() + self.duration_time_to_seconds(self.test_duration)

        while (datetime.datetime.now().timestamp() < end_time):
            time.sleep(monitor_interval)

    def start(self):
        #admin up all created stations & existing stations
        interest_flags_list = ['ifdown']
        set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= interest_flags_list)
        if self.sta_list:
            for sta_alias in self.sta_list:
                port_shelf, port_resource, port_name, *nil = self.name_to_eid(sta_alias)
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
        #TODO move arg validation to validate_sort_args
        #create stations
        if self.sta_list:
            logger.info("Creating stations")
            types = {"wep": "wep_enable", "wpa": "wpa_enable", "wpa2": "wpa2_enable", "wpa3": "use-wpa3", "open": "[BLANK]"}
            if self.security in types.keys():
                add_sta_flags = []
                set_port_interest = ['rpt_timer','current_flags', 'dhcp']
                set_port_current=['use_dhcp']

                if self.security != "open":
                    if (self.passwd is None) or (self.passwd == ""):
                        raise ValueError("use_security: %s requires passphrase or [BLANK]" % self.security)
                    else:
                        add_sta_flags.extend([types[self.security], "create_admin_down"])
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

                    self.command.post_nc_show_ports(port=port_name,
                                                    resource=port_resource,
                                                    shelf=port_shelf)

                    #wait until port appears, then set use_dhcp and rpt_timer
                    wfa_list = [sta_alias]
                    self.wait_for_action("port", wfa_list, "appear", 3000)

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
        if (self.test_type == 'iperf'):
            #admin up server port, we need IP for client generic endp creation.
            # This code is only executed if we are NOT given a target ip address.
            if (self.target_port_alias and not self.target):
                server_eid = self.name_to_eid(self.target_port_alias)
                set_port_interest_rslt=self.command.set_flags(LFJsonCommand.SetPortInterest, starting_value=0, flag_names= ['ifdown'])
                self.command.post_set_port(shelf = server_eid[0],
                                            resource = server_eid[1],
                                            port = server_eid[2],
                                            netmask= "255.255.255.0", #sometimes the cli complains about the netmask being NA, so set it to a random netmask(netmask is overriden anyways with dhcp)
                                            current_flags= 0,
                                            interest=set_port_interest_rslt,
                                            report_timer= self.report_timer)
                self.wait_for_action("port", [self.target_port_alias], "up", 3000)
                self.wait_for_action("port", [self.target_port_alias], "ip", 3000)


        #create endpoints
        #create 1 endp for each eid.
        unique_alias = 0
        if self.sta_list:
            unique_alias += len(self.sta_list)
        if self.use_existing_eid:
            unique_alias += len(self.use_existing_eid)

        if self.sta_list:
            for sta_alias in self.sta_list:
                sta_eid = self.name_to_eid(sta_alias)
                self.create_generic_endp(sta_eid, self.test_type, unique_alias)
                unique_alias-=1

        if self.use_existing_eid: #use existing eid will have iperf3-server eid, if we are using lanforge iperf3-server.
            for eid_alias in self.use_existing_eid:
                eid_list = self.name_to_eid(eid_alias)
                self.create_generic_endp(eid_list, self.test_type, unique_alias)
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
        
        if self.wait_for_action("cx", self.created_endp, "appear", 3000):
            print("Generic cx creation completed.")
        else:
            print("Generic cx creation was not completed.")

    def get_ip_address(self, eid):
        json_url = "%s/ports/%s/%s/%s?fields=device,ip" % (self.lfclient_url, eid[1], eid[0], eid[2])
        json_response = self.query.json_get(url=json_url,
                                            debug=self.debug)
        if json_response is not None and (json_response['interface']['ip'] != "0.0.0.0"):
            return json_response['interface']['ip']
        else:
            return None
                    
    def create_generic_endp(self, eid, type, unique_num):
        """
        :param eid: list format of eid. example: ['1', '1', 'sta0010']
        :param type: takes type of generic test: 'ping', 'iperf3-client', 'iperf3-server', 'lfcurl', 'speedtest', 'iperf'
        :param unique_num: takes in unique ending prefix. example: 3
        :return: no return
        """
        unique_alias = type + "-" + str(unique_num)

        #construct generic endp command
        cmd = ""
        if (self.cmd):
            cmd=self.cmd
        elif (type == 'iperf'):
            if (self.target_port_alias):
                server_port_eid = self.name_to_eid(self.target_port_alias)
                server_ip = self.get_ip_address(server_port_eid)
                if (eid == server_port_eid):
                    unique_alias = "server-" + unique_alias
                    cmd = self.do_iperf('server', unique_alias, eid, server_ip)
                else:
                    unique_alias = "client-" + unique_alias
                    cmd = self.do_iperf('client', unique_alias, eid, server_ip)
            else:
                #the case that user chooses not to use and create lanforge iperf server.  
                cmd = self.do_iperf('client', unique_alias, eid, self.target)
        elif (type == 'ping'):
            # lfping  -s 128 -i 0.1 -c 10000 -I sta0000 www.google.com
            cmd="lfping"
            if (self.interval):
                cmd = cmd + " -i %d" % self.interval
            if (self.loop_count):
                cmd = cmd + " -c %d" % self.loop_count
            cmd = cmd + " -I %s " % eid[2]
            if (self.target):
                cmd = cmd + str(self.target)
  
        elif (type == 'iperf3-client'):
            #  iperf3 --forceflush --format k --precision 4 -c 192.168.10.1 -t 60 --tos 0 -b 1K --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
                cmd = self.do_iperf('client', unique_alias, eid, server_ip)

        elif (self.test_type == 'iperf3-server'):
            # iperf3 --forceflush --format k --precision 4 -s --bind_dev sta0000 
            # -i 5 --pidfile /tmp/lf_helper_iperf3_testing.pid -p 101
            cmd = self.do_iperf('server', unique_alias, eid, server_ip)

        elif (self.test_type == 'lfcurl'):
            # ./scripts/lf_curl.sh  -p sta0000 -i 192.168.50.167 -o /dev/null -n 1 -d 8.8.8.8
            cmd = cmd + str("./scripts/lf_curl.sh -p %s" % eid[2])
            # cmd = cmd + "-i %s" % str(self.target) TODO: get ip address of -i (sta0000) if i is a station, but not if eth port.
            #TODO add -o
            cmd = cmd + "-o /dev/null -n 1 -d %s" % str(self.target)
        elif (self.test_type == 'speedtest'):
            # vrf_exec.bash eth3 speedtest-cli --csv --share --single --debug
            # vrf_exec.bash eth3 speedtest-cli --csv --no-upload
            # vrf_exec.bash eth3 speedtest-cli --csv
            # Ookla (with license) : # speedtest --interface=eth3 --format=csv
            cmd = cmd + "vrf_exec.bash %s speedtest-cli --csv" % eid[2]
        else:
            raise ValueError("Was not able to identify type given in arguments.")

        #create initial generic endp
        #  add_gen_endp testing 1 1 sta0000 gen_generic
        self.command.post_add_gen_endp(alias = unique_alias,
                                       shelf=eid[0],
                                       resource=eid[1],
                                       port=eid[2],
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

        
    def do_iperf (self, type, alias, eid, server_ip_addr):
        """
        :param type: takes in options 'client' or 'server'
        :param alias: takes in alias. example: 'sta0000'
        :param eid: takes in eid list. ['1','1','sta0000']
        :return: returns constructed iperf command
        """
        cmd = "iperf3 --forceflush --format k --precision 4"
        #TODO check if dest, client_port and server_port are not empty
        if (type == 'client'):
            cmd = cmd + str(" -c %s" % server_ip_addr) + " -t 60 --tos 0 -b 1K " + str("--bind_dev %s" % eid[2])
            cmd = cmd + " -i 3 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            if (self.client_port):
                #add port that should match server_port
                cmd = cmd + " -p %s" % self.client_port
        #server
        else:
            #iperf3 --forceflush --format k --precision 4 -s --bind_dev eth2 -i 5 --pidfile /tmp/lf_helper_iperf3_server_iperf_1.pid eth2
            cmd = cmd + " -s" + str(" --bind_dev %s" % eid[2]) + " -i 3 --pidfile /tmp/lf_helper_iperf3_%s.pid" % alias
            if (self.server_port):
                #add port that should match client port
                cmd = cmd + " -p %s" % self.server_port
        return cmd

    def cleanup(self):
        logger.info("Cleaning up all cxs and endpoints.")
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

    def check_args(self, args):
        print(args)
        #TODO validate all args, depending on which test is used.

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
            IPERF:
                ./test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3
            SPEEDTEST:

        ''',
    )
    required = parser.add_argument_group('Arguments that must be defined by user:')
    optional = parser.add_argument_group('Arguments that do not need to be defined by user:')

    required.add_argument("--lf_user", type=str, help="user: lanforge", default=None)
    required.add_argument("--lf_passwd", type=str, help="passwd: lanforge", default=None)
    required.add_argument('--type', type=str, help='type of command to run: ping, iperf3-client, iperf3-server, iperf, lfcurl', required=True)

    optional.add_argument('--mgr', help='ip address of lanforge script should be run on. example: 192.168.102.211', default=None)
    optional.add_argument('--mgr_port', help='port which lanforge is running on, on lanforge machine script should be run on. example: 8080', default=8080)
    optional.add_argument('--cmd', help='specifies command to be run by generic type endp', default=None)

    #generic endpoint configurations
    optional.add_argument('--interval', help='interval to use when running lfping. in seconds', default=1)
    optional.add_argument('--file_output_lfcurl', help='location to output results of lf_curl, absolute path preferred', default=None)
    optional.add_argument('--loop_count', help='determines the number of loops to use in lf_curl and lfping', default=None)
    optional.add_argument('--target', help='Target for lfping (ex: www.google.com). ALSO used for iperf3-client target IF iperf3-server is NOT on lanforge. Example: 192.168.1.151', default=None)
    optional.add_argument('--target_port_alias', help='Target for iperf-server port alias eid. Use this if iperf_server is on lanforge. Example: 1.1.eth2', default=None)
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
    optional.add_argument('--output_format', help= 'choose either csv or xlsx',default='csv')
    optional.add_argument('--csv_outfile', help="output file for csv data", default="test_generic_kpi")
    optional.add_argument('--report_file', help='where you want to store results', default=None)
    optional.add_argument( '--gen_cols', help='Columns wished to be monitored from layer 3 endpoint tab',default= ['name', 'tx bytes', 'rx bytes'])
    optional.add_argument( '--port_mgr_cols', help='Columns wished to be monitored from port manager tab',default= ['ap', 'ip', 'parent dev'])
    optional.add_argument('--compared_report', help='report path and file which is wished to be compared with new report',default= None)

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


    #TODO edit name_prefix
    generic_test = GenTest(host=args.mgr, port=args.mgr_port,
                           lf_user=args.lf_user, lf_passwd=args.lf_passwd,
                           radio=args.radio,
                           num_stations = args.num_stations,
                           use_existing_eid=args.use_existing_eid,
                           name_prefix="GT",
                           test_type=args.type,
                           target=args.target,
                           target_port_alias=args.target_port_alias,
                           cmd=args.cmd,
                           interval=args.interval,
                           ssid=args.ssid,
                           passwd=args.passwd,
                           security=args.security,
                           test_duration=args.test_duration,
                           monitor_interval=args.monitor_interval,
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
    
    generic_test.check_args(args)
    #generic_test.cleanup()
    generic_test.build()

    generic_test.start()

    logger.info("Starting connections with 5 second settle time.")
    generic_test.start()
    time.sleep(5) # give traffic a chance to get started.

    generic_test.monitor_test()
    print("Done with connection monitoring")
    generic_test.stop()
    generic_test.cleanup()

if __name__ == "__main__":
    main()