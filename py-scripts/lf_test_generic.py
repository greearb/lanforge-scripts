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

#stand-alone (not dependent on realm)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
lf_json_api = importlib.import_module("py-scripts.lf_json_api")
lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
# create name_to_eid


logger = logging.getLogger(__name__)


if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

class GenTest():
    def __init__(self, lf_user, lf_passwd, ssid, security, passwd, sta_list, 
                name_prefix, upstream, client=None, _client_port = None,_server_port=None,
                 host="localhost", port=8080, number_template="000", csv_outfile=None,
                 use_existing_eid=None, test_duration="5m",test_type="lfping", dest=None, cmd=None, interval=1, 
                 radio=None, speedtest_min_up=None, speedtest_min_dl=None, 
                 speedtest_max_ping=None, file_output_lfcurl=None, loop_count=None, 
                 _debug_on=False, _exit_on_error=False, _exit_on_fail=False):
        self.host=host
        self.port=port
        self.lf_user=lf_user
        self.lf_passwd=lf_passwd
        self.ssid = ssid
        self.radio = radio
        self.upstream = upstream
        self.sta_list = sta_list
        self.security = security
        self.passwd = passwd
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.debug = _debug_on
        self.csv_outfile = csv_outfile
        self.lfclient_url = "http://%s:%s" % (self.lfclient_host, self.lfclient_port)
        if client:
            self.client_name = client
        # create api_json
        self.json_api = lf_json_api.lf_json_api(lf_mgr=self.lf_mgr,
                                                    lf_port=self.lf_port,
                                                    lf_user=self.lf_user,
                                                    lf_passwd=self.lf_passwd)

        # create a session
        # self.session = LFSession(lfclient_url="http://{lf_mgr}:{lf_port}".format(lf_mgr=self.lf_mgr, lf_port=self.lf_port),
        # session to use lanforge_api
        self.session = LFSession(lfclient_url="http://%s:8080" % self.lf_mgr,
                                 debug=_debug_on,
                                 connection_timeout_sec=4.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=True)
        if _debug_on:
            Logg.register_method_name("json_post")
            Logg.register_method_name("json_get")
            Logg.register_method_name("get_as_json")

        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    def check_tab_exists(self):
        response = self.json_get("generic")
        if response is None:
            return False
        else:
            return True

""" def generate_report(self, test_rig, test_tag, dut_hw_version, dut_sw_version, 
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
 """
def start(self):
        self.station_profile.admin_up()
        temp_stas = []
        for station in self.sta_list.copy():
            temp_stas.append(self.name_to_eid(station)[2])
        if self.debug:
            pprint.pprint(self.station_profile.station_names)

        if LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                             port_list=self.station_profile.station_names,
                                             debug_=self.debug):
            self._pass("All stations went admin up.")
        else:
            self._fail("All stations did NOT go admin up.")

        if self.wait_for_ip(station_list=temp_stas, ipv4=True, debug=self.debug, timeout_sec=-1):
            self._pass("All stations got IPs")
        else:
            self._fail("Stations failed to get IPs")
            self.exit_fail()

        self.generic_endps_profile.start_cx()

def stop(self):
        logger.info("Stopping Test...")
        self.generic_endps_profile.stop_cx()
        self.station_profile.admin_down()

def build(self):
        self.station_profile.use_security(self.security, self.ssid, self.passwd)
        self.station_profile.set_number_template(self.number_template)
        logger.info("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)

        if self.station_profile.create(radio=self.radio, sleep_time=0, sta_names_=self.sta_list, debug=self.debug):
            self._pass("Station creation completed.")
        else:
            self._fail("Station creation failed.")

        if self.generic_endps_profile.create(ports=self.station_profile.station_names, sleep_time=.5):
            self._pass("Generic endpoints creation completed.")
        else:
            self._fail("Generic endpoints NOT completed.")

def cleanup(self, sta_list):
        #self.generic_endps_profile.cleanup()
        #self.station_profile.cleanup(sta_list)

        if LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=sta_list, debug=self.debug):
            self._pass("Ports successfully cleaned up.")
        else:
            self._fail("Ports NOT successfully cleaned up.")


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
    --security {open | wep | wpa | wpa2 | wpa3} (required)
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
        --num_stations 2 --ssid Logan-Test-Net --passwd Logan-Test-Net --security wpa2 --type lfcurl --dest 192.168.1.1
    GENERIC:
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio 1.1.wiphy0 --num_stations 2 --ssid Logan-Test-Net 
        --report_file /home/lanforge/reports/GENERIC.csv --passwd Logan-Test-Net --security wpa2 --type generic
    SPEEDTEST:
        ./test_generic.py --radio 1.1.wiphy0 --num_stations 2 --report_file /home/lanforge/reports/SPEEDTEST.csv 
        --ssid Logan-Test-Net --passwd Logan-Test-Net --type speedtest --speedtest_min_up 20 --speedtest_min_dl 20 --speedtest_max_ping 150 --security wpa2
    IPERF3 (under construction):
        ./test_generic.py --mgr localhost --mgr_port 4122 --radio wiphy1 --num_stations 3 --ssid jedway-wpa2-x2048-4-1 --passwd jedway-wpa2-x2048-4-1 --security wpa2 --type iperf3
''',
    )
    required = parser.add_argument_group('Arguments that must be defined by user:')
    optional = parser.add_argument_group('Arguements that do not need to be defined by user:')

    required.add_argument('--type', type=str, help='type of command to run: generic, lfping, iperf3-client, iperf3-server, iperf, lfcurl. Iperf option will create both iperf client and server.', required=True)
    required.add_argument("--lf_user", type=str, help="user: lanforge", default=None)
    required.add_argument("--lf_passwd", type=str, help="passwd: lanforge", default=None)

    optional.add_argument('--mgr', help='specifies command to be run by generic type endp', default=None)
    optional.add_argument('--mgr_port', help='specifies command to be run by generic type endp', default=8080)
    optional.add_argument('--cmd', help='specifies command to be run by generic type endp', default='')
    optional.add_argument('--csv_outfile', help="output file for csv data", default="test_generic_kpi")
    optional.add_argument('--test_duration', help='duration of the test eg: 30s, 2m, 4h', default="2m")
    optional.add_argument('--interval', help='interval to use when running lfping (1s, 1m)', default=1)
    optional.add_argument('--speedtest_min_up', help='sets the minimum upload threshold for the speedtest type', default=None)
    optional.add_argument('--speedtest_min_dl', help='sets the minimum download threshold for the speedtest type', default=None)
    optional.add_argument('--speedtest_max_ping', help='sets the minimum ping threshold for the speedtest type', default=None)
    optional.add_argument('--client', help='client (sta alias) to the iperf3 server', default=None)
    optional.add_argument('--file_output_lfcurl', help='location to output results of lf_curl, absolute path preferred', default=None)
    optional.add_argument('--loop_count', help='determines the number of loops to use in lf_curl', default=None)
    optional.add_argument("--test_rig", help="test rig for kpi.csv, testbed that the tests are run on", default="")
    optional.add_argument("--test_tag", help="test tag for kpi.csv,  test specific information to differentiate the test", default="")
    optional.add_argument("--dut_hw_version", help="dut hw version for kpi.csv, hardware version of the device under test", default="")
    optional.add_argument("--dut_sw_version", help="dut sw version for kpi.csv, software version of the device under test", default="")
    optional.add_argument("--dut_model_num", help="dut model for kpi.csv,  model number / name of the device under test", default="")
    optional.add_argument("--dut_serial_num", help="dut serial for kpi.csv, serial number of the device under test", default="")
    optional.add_argument('--dest', help='destination IP for command', default=None)
    optional.add_argument('--client_port', help="the port number of the iperf client endpoint",default=None)
    optional.add_argument('--server_port', help="the port number of the iperf server endpoint",default=None)

    optional.add_argument('--use_existing_eid', help="EID of port we want to use",default=None)
    optional.add_argument('--radio', help="radio that stations should be created on",default=None)
    optional.add_argument('--num_stations', help="number of stations that are to be made, defaults to 1",default=1)
    optional.add_argument('--ssid', help="ssid for stations to connect to",default=None)
    optional.add_argument('--passwd', help="password to ssid for stations to connect to",default=None)
    optional.add_argument('--mode', help='Used to force mode of stations')
    optional.add_argument('--ap', help='Used to force a connection to a particular AP')
    optional.add_argument('--output_format', help= 'choose either csv or xlsx',default='csv')
    optional.add_argument('--report_file', help='where you want to store results', default=None)
    optional.add_argument( '--a_min', help= '--a_min bps rate minimum for side_a', default=256000)
    optional.add_argument('--b_min', help= '--b_min bps rate minimum for side_b', default= 256000)
    optional.add_argument( '--gen_cols', help='Columns wished to be monitored from layer 3 endpoint tab',default= ['name', 'tx bytes', 'rx bytes'])
    optional.add_argument( '--port_mgr_cols', help='Columns wished to be monitored from port manager tab',default= ['ap', 'ip', 'parent dev'])
    optional.add_argument('--compared_report', help='report path and file which is wished to be compared with new report',default= None)
    optional.add_argument('--monitor_interval',help='how frequently do you want your monitor function to take measurements; 250ms, 35s, 2h',default='2s')

    
    if not sys.argv:
        print("This python file needs the minimum required args. See add the --help flag to check out required arguments.")
        exit(1)
        
    args = parser.parse_args()
    print(args)
    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    # TODO either use Realm or create a port to IP method in realm
    if args.dest is None:
        # get ip upstream port
        rv = LFUtils.name_to_eid(args.upstream_port)
        shelf = rv[0]
        resource = rv[1]
        port_name = rv[2]
        request_command = 'http://{lfmgr}:{lfport}/port/1/{resource}/{port_name}'.format(
        lfmgr=args.mgr, lfport=args.mgr_port, resource=resource, port_name=port_name)
        logger.info("port request command: {request_command}".format(request_command=request_command))

        request = requests.get(request_command, auth=(args.lf_user, args.lf_passwd))
        logger.info("port request status_code {status}".format(status=request.status_code))

        lanforge_json = request.json()
        lanforge_json_formatted = json.dumps(lanforge_json, indent=4)        
        try: 
            key = 'interface'
            df = json_normalize(lanforge_json[key])
            args.dest = df['ip'].iloc[0]
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.error("json returned : {lanforge_json_formatted}".format(lanforge_json_formatted=lanforge_json_formatted))


        # Create directory

        # if file path with output file extension is not given...
        # check if home/lanforge/report-data exists. if not, save
        # in new folder based in current file's directory


    systeminfopath = None
    if args.report_file is None:
        new_file_path = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%M-m-%S-s")).replace(':',
                                                                                                 '-') + '-test_generic'  # create path name
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
    if (int(args.num_stations) > 0): 
        station_list = LFUtils.portNameSeries(radio=args.radio,
                                          prefix_="sta",
                                          start_id_=0,
                                          end_id_= int(args.num_stations) - 1,
                                          padding_number_=100)
    else:
        station_list = []

    generic_test = GenTest(host=args.mgr, port=args.mgr_port,
                           lf_user=args.lf_user, lf_passwd=args.lf_passwd,
                           number_template="00",
                           radio=args.radio,
                           sta_list=station_list,
                           use_existing_eid=args.use_existing_eid,
                           name_prefix="GT",
                           test_type=args.type,
                           dest=args.dest,
                           cmd=args.cmd,
                           interval=args.interval,
                           ssid=args.ssid,
                           upstream=args.upstream_port,
                           passwd=args.passwd,
                           security=args.security,
                           test_duration=args.test_duration,
                           speedtest_min_up=args.speedtest_min_up,
                           speedtest_min_dl=args.speedtest_min_dl,
                           speedtest_max_ping=args.speedtest_max_ping,
                           file_output_lfcurl=args.file_output_lfcurl,
                           csv_outfile=args.csv_outfile,
                           loop_count=args.loop_count,
                           client=args.client,
                           _client_port=args.client_port,
                           _server_port=args.server_port,
                           _debug_on=args.debug)

    if not generic_test.check_tab_exists():
        raise ValueError("Error received from GUI, please ensure generic tab is enabled")
    generic_test.cleanup(station_list)
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

    resource_id = LFUtils.name_to_eid(args.radio)[1]

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
    #                                            sta_list=station_list,
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

    generic_test.cleanup(station_list)


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