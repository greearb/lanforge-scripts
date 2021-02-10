#!/usr/bin/env python3

"""test_ipv4_variable_time.py will create stations and endpoints to generate and verify layer-3 traffic.

This script will create a variable number of stations each with their own set of cross-connects and endpoints.
It will then create layer 3 traffic over a specified amount of time, testing for increased traffic at regular intervals.
This test will pass if all stations increase traffic over the full test duration.

Use './test_ipv4_variable_time.py --help' to see command line usage and options
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""

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
from realm import Realm
import time
import datetime

class IPV4VariableTime(Realm):
    def __init__(self,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=[],
                 name_prefix=None,
                 upstream=None,
                 radio=None,
                 host="localhost",
                 port=8080,
                 mode = 0,
                 ap=None,
                 side_a_min_rate=56, side_a_max_rate=0,
                 side_b_min_rate=56, side_b_max_rate=0,
                 number_template="00000", test_duration="5m", use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.l3cxprofile = self.new_l3_cx_profile()
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.radio = radio
        self.mode= mode
        self.ap=ap
        self.number_template = number_template
        self.debug = _debug_on
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.station_profile = self.new_station_profile()
        self.cx_profile = self.new_l3_cx_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 9
        self.station_profile.mode = mode
        if self.ap is not None:
            self.station_profile.set_command_param("add_sta", "ap",self.ap)


        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def start(self, print_pass=False, print_fail=False):
        self.station_profile.admin_up()
        #to-do- check here if upstream port got IP
        temp_stas = self.station_profile.station_names.copy()

        if self.wait_for_ip(temp_stas):
            self._pass("All stations got IPs")
        else:
            self._fail("Stations failed to get IPs")
            self.exit_fail()
        self.cx_profile.start_cx()


    def stop(self):
        self.cx_profile.stop_cx()
        self.station_profile.admin_down()

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        for sta in self.sta_list:
            self.rm_port(sta, check_exists=True)

    def cleanup(self):
        self.cx_profile.cleanup()
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def build(self):

        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)
        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        self.cx_profile.create(endp_type="lf_udp", side_a=self.station_profile.station_names, side_b=self.upstream, sleep_time=0)
        self._pass("PASS: Station build finished")

def main():
    optional=[]
    optional.append({'name':'--mode','help':'Used to force mode of stations'})
    optional.append({'name':'--ap','help':'Used to force a connection to a particular AP'})
    optional.append({'name':'--output_format','help':'choose either csv or xlsx'})
    optional.append({'name':'--report_file','help':'where you want to store results', 'default':None})
    optional.append({'name':'--a_min','help':'--a_min bps rate minimum for side_a', 'default':256000})
    optional.append({'name':'--b_min','help':'--b_min bps rate minimum for side_b', 'default':256000})
    optional.append({'name':'--test_duration','help':'--test_duration sets the duration of the test', 'default':"2m"})
    optional.append({'name':'--layer3_cols','help':'Columns wished to be monitored from layer 3 endpoint tab', 'default':['name','tx bytes','rx bytes']})
    optional.append({'name':'--port_mgr_cols','help':'Columns wished to be monitored from port manager tab', 'default':['ap','ip','rx bytes']})
    optional.append({'name':'--compared_report','help':'report path and file which is wished to be compared with new report', 'default':None})
    parser = LFCliBase.create_basic_argparse(
        prog='test_ipv4_variable_time.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open)
            ''',
        description='''\
test_ipv4_variable_time.py:
--------------------
Generic command layout:

python3 ./test_ipv4_variable_time.py
    --upstream_port eth1
    --radio wiphy0
    --num_stations 32
    --security {open|wep|wpa|wpa2|wpa3}
    --mode   1
        {"auto"   : "0",
        "a"      : "1",
        "b"      : "2",
        "g"      : "3",
        "abg"    : "4",
        "abgn"   : "5",
        "bgn"    : "6",
        "bg"     : "7",
        "abgnAC" : "8",
        "anAC"   : "9",
        "an"     : "10",
        "bgnAC"  : "11",
        "abgnAX" : "12",
        "bgnAX"  : "13"}
    --ssid netgear
    --password admin123
    --test_duration 2m (default)
    --a_min 3000
    --b_min 1000
    --ap "00:0e:8e:78:e1:76"
    --output_format csv
    --report_file ~/Documents/results.csv                       (Example of csv file output  - please use another extension for other file formats)
    --compared_report ~/Documents/results_prev.csv              (Example of csv file retrieval - please use another extension for other file formats) - UNDER CONSTRUCTION
    --layer3_cols'name','tx bytes','rx bytes','dropped'          (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --port_mgr_cols 'ap','ip'                                    (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --debug
===============================================================================
 ** FURTHER INFORMATION **
    Using the layer3_cols flag:

    Currently the output function does not support inputting the columns in layer3_cols the way they are displayed in the GUI. This quirk is under construction. To output
    certain columns in the GUI in your final report, please match the according GUI column display to it's counterpart to have the columns correctly displayed in
    your report.

    GUI Column Display       Layer3_cols argument to type in (to print in report)

    Name                |  'name'
    EID                 |  'eid'
    Run                 |  'run'
    Mng                 |  'mng'
    Script              |  'script'
    Tx Rate             |  'tx rate'
    Tx Rate (1 min)     |  'tx rate (1&nbsp;min)'
    Tx Rate (last)      |  'tx rate (last)'
    Tx Rate LL          |  'tx rate ll'
    Rx Rate             |  'rx rate'
    Rx Rate (1 min)     |  'rx rate (1&nbsp;min)'
    Rx Rate (last)      |  'rx rate (last)'
    Rx Rate LL          |  'rx rate ll'
    Rx Drop %           |  'rx drop %'
    Tx PDUs             |  'tx pdus'
    Tx Pkts LL          |  'tx pkts ll'
    PDU/s TX            |  'pdu/s tx'
    Pps TX LL           |  'pps tx ll'
    Rx PDUs             |  'rx pdus'
    Rx Pkts LL          |  'pps rx ll'
    PDU/s RX            |  'pdu/s tx'
    Pps RX LL           |  'pps rx ll'
    Delay               |  'delay'
    Dropped             |  'dropped'
    Jitter              |  'jitter'
    Tx Bytes            |  'tx bytes'
    Rx Bytes            |  'rx bytes'
    Replays             |  'replays'
    TCP Rtx             |  'tcp rtx'
    Dup Pkts            |  'dup pkts'
    Rx Dup %            |  'rx dup %'
    OOO Pkts            |  'ooo pkts'
    Rx OOO %            |  'rx ooo %'
    RX Wrong Dev        |  'rx wrong dev'
    CRC Fail            |  'crc fail'
    RX BER              |  'rx ber'
    CX Active           |  'cx active'
    CX Estab/s          |  'cx estab/s'
    1st RX              |  '1st rx'
    CX TO               |  'cx to'
    Pattern             |  'pattern'
    Min PDU             |  'min pdu'
    Max PDU             |  'max pdu'
    Min Rate            |  'min rate'
    Max Rate            |  'max rate'
    Send Buf            |  'send buf'
    Rcv Buf             |  'rcv buf'
    CWND                |  'cwnd'
    TCP MSS             |  'tcp mss'
    Bursty              |  'bursty'
    A/B                 |  'a/b'
    Elapsed             |  'elapsed'
    Destination Addr    |  'destination addr'
    Source Addr         |  'source addr'
            ''',
        more_optional=optional)

    args = parser.parse_args()

    num_sta = 2
    if (args.num_stations is not None) and (int(args.num_stations) > 0):
        num_sta = int(args.num_stations)

    #Create directory

    #if file path with output file extension is not given... 
    # check if home/lanforge/report-data exists. if not, save 
    # in new folder based in current file's directory

    if args.report_file is None:
        new_file_path = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")).replace(':','-')+'test_ipv4_variable_time' #create path name
        try:
            path = os.path.join('/home/lanforge/report-data/',new_file_path)
            os.mkdir(path)
        except:
            curr_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(curr_dir_path, new_file_path)
            os.mkdir(path)        

        if args.output_format in ['csv','json','html','hdf','stata','pickle','pdf','png','df','parquet','xlsx']:
            report_f= str(path) + '/data.' + args.output_format
            output=args.output_format
        else:
            print('Defaulting to csv data file output type, naming it data.csv.')
            report_f= str(path)+'/data.csv'
            output='csv'
        if args.debug:
            print("Saving report data in ... " + report_f)
    else:
        report_f=args.report_file
        if args.output_format is None:
            output=str(args.report_file).split('.')[-1]
        else:
            output=args.output_format

    #Retrieve last data file
    compared_rept=None
    if args.compared_report:
        #check if last report format is same as current rpt format
        last_report_format = args.compared_report.split('.')[-1]
        if output == last_report_format:
            compared_rept = args.compared_report
        else:
            ValueError("Compared report format is not the same as the new report format. Please make sure they are of the same file type.")


    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=0, end_id_=num_sta-1, padding_number_=10000, radio=args.radio)
    ip_var_test = IPV4VariableTime(host=args.mgr,
                                   port=args.mgr_port,
                                   number_template="0000",
                                   sta_list=station_list,
                                   name_prefix="VT",
                                   upstream=args.upstream_port,
                                   ssid=args.ssid,
                                   password=args.passwd,
                                   radio=args.radio,
                                   security=args.security,
                                   test_duration=args.test_duration,
                                   use_ht160=False,
                                   side_a_min_rate=args.a_min,
                                   side_b_min_rate=args.b_min,
                                   mode=args.mode,
                                   ap=args.ap,
                                   _debug_on=args.debug)

    ip_var_test.pre_cleanup()
    ip_var_test.build()
    if not ip_var_test.passes():
        print(ip_var_test.get_fail_message())
        ip_var_test.exit_fail()
    ip_var_test.start(False, False)

    try:
        layer3connections=','.join([[*x.keys()][0] for x in ip_var_test.json_get('endp')['endpoint']])
    except:
        raise ValueError('Try setting the upstream port flag if your device does not have an eth1 port')

    if type(args.layer3_cols) is not list:
        layer3_cols=list(args.layer3_cols.split(","))
        #send col names here to file to reformat
    else:
        layer3_cols = args.layer3_cols
        #send col names here to file to reformat
    if type(args.port_mgr_cols) is not list:
        port_mgr_cols=list(args.port_mgr_cols.split(","))
        #send col names here to file to reformat
    else:
        port_mgr_cols=args.port_mgr_cols
    if args.debug:
        print("Layer 3 Endp column names are...")
        print(layer3_cols)
        print("Port Manager column names are...")
        print(port_mgr_cols)

    ip_var_test.l3cxprofile.monitor(layer3_cols=layer3_cols,
                                    port_mgr_cols=port_mgr_cols,
                                    report_file=report_f,
                                    duration_sec=ip_var_test.parse_time(args.test_duration).total_seconds(),
                                    created_cx= layer3connections,
                                    output_format=output,
                                    compared_report=compared_rept,
                                    script_name='test_ipv4_variable_time',
                                    arguments=args,
                                    debug=args.debug)

    ip_var_test.stop()
    if not ip_var_test.passes():
        print(ip_var_test.get_fail_message())
        ip_var_test.exit_fail()
    time.sleep(30)
    ip_var_test.cleanup()
    if ip_var_test.passes():
        ip_var_test.exit_success()

if __name__ == "__main__":
    main()
