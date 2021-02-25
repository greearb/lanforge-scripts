#!/usr/bin/env python3

"""
    Script for creating a variable number of stations.
"""

import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
from realm import Realm
import datetime
import pprint
import pandas as pd
import time


class MeasureTimeUp(Realm):
    def __init__(self,
                 _ssid=None,
                 _security=None,
                 _password=None,
                 _host=None,
                 _port=None,
                 _sta_list=None,
                 _number_template="00000",
                 _radio="wiphy0",
                 _proxy_str=None,
                 _debug_on=False,
                 _up=True,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _load=None,
                 _action="overwrite",
                 _clean_chambers="store_true",
                 _start=None,
                 _quiesce=None,
                 _stop=None,
                 _clean_dut="no"):
        super().__init__(_host,
                         _port)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.security = _security
        self.password = _password
        self.sta_list = _sta_list
        self.radio = _radio
        #self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.up = _up
        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password,
        self.station_profile.security = self.security
        self.station_profile.number_template_ = self.number_template
        self.station_profile.mode = 0
        self.load=_load
        self.action=_action
        self.clean_chambers=_clean_chambers
        self.start=_start
        self.quiesce=_quiesce
        self.stop=_stop
        self.clean_dut=_clean_dut
        if self.debug:
            print("----- Station List ----- ----- ----- ----- ----- ----- \n")
            pprint.pprint(self.sta_list)
            print("---- ~Station List ----- ----- ----- ----- ----- ----- \n")


    def build(self):
        # Build stations
        self.station_profile.use_security(self.security, self.ssid, self.password)
        self.station_profile.set_number_template(self.number_template)

        print("Creating stations")
        self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        self.station_profile.set_command_param("set_port", "report_timer", 1500)
        self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        if self.up:
            self.station_profile.admin_up()
        self._pass("PASS: Station build finished")

    def scenario(self):
        if self.load is not None:
            data = {
                "name": self.load,
                "action": self.action,
                "clean_dut": "no",
                "clean_chambers": "no"
            }
            if self.clean_dut:
                data['clean_dut'] = "yes"
            if self.clean_chambers:
                data['clean_chambers'] = "yes"
            print("Loading database %s" % self.load)
            self.json_post("/cli-json/load", data)

        elif self.start is not None:
            print("Starting test group %s..." % self.start)
            self.json_post("/cli-json/start_group", {"name": self.start})
        elif self.stop is not None:
            print("Stopping test group %s..." % self.stop)
            self.json_post("/cli-json/stop_group", {"name": self.stop})
        elif self.quiesce is not None:
            print("Quiescing test group %s..." % self.quiesce)
            self.json_post("/cli-json/quiesce_group", {"name": self.quiesce})




def main():
    parser = LFCliBase.create_basic_argparse(
        prog='measure_station_time_up.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Measure how long it takes to up stations
            ''',

        description='''\
        measure_station_time_up.py
--------------------
Command example:
./measure_station_time_up.py
    --radio wiphy0
    --num_stations 3
    --security open
    --ssid netgear
    --passwd BLANK
    --debug
    --outfile
            ''')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--report_file', help='where you want to store results', required=True)

    args = parser.parse_args()
    #if args.debug:
    #    pprint.pprint(args)
    #    time.sleep(5)
    if (args.radio is None):
       raise ValueError("--radio required")

    dictionary=dict()
    for num_sta in [2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]:
        print(num_sta)
        try:
            station_list = LFUtils.port_name_series(prefix="sta",
                                   start_id=0,
                                   end_id=num_sta-1,
                                   padding_number=10000,
                                   radio=args.radio)
            create_station = MeasureTimeUp(_host=args.mgr,
                                           _port=args.mgr_port,
                                           _ssid=args.ssid,
                                           _password=args.passwd,
                                           _security=args.security,
                                           _sta_list=station_list,
                                           _radio=args.radio,
                                           _proxy_str=args.proxy,
                                           _debug_on=args.debug,
                                           _load='FACTORY_DFLT')
            create_station.scenario()
            time.sleep(5)
            start=datetime.datetime.now()
            create_station.build()
            built=datetime.datetime.now()
            create_station.wait_for_ip(station_list,timeout_sec=400)
            end=datetime.datetime.now()
            dictionary[num_sta]=[start,built,end]
        except:
            pass
    df=pd.DataFrame.from_dict(dictionary).transpose()
    df.columns=['Start','Built','End']
    df['built duration']=df['Built']-df['Start']
    df['IP Addresses']=df['End']-df['Built']
    df['duration']=df['End']-df['Start']
    for variable in ['built duration','IP Addresses','duration']:
        df[variable]=[x.total_seconds() for x in df[variable]]
    df.to_pickle(args.report_file)

if __name__ == "__main__":
    main()
