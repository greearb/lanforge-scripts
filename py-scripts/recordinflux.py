#!/usr/bin/env python3
"""recordinflux will record data from existing lanforge endpoints to record to an already existing influx database.

This data can then be streamed in Grafana or any other graphing program the user chooses while this script runs.

https://influxdb-python.readthedocs.io/en/latest/include-readme.html


Use './recordinflux.py --help' to see command line usage and options
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

import requests
import json
from influxdb import InfluxDBClient
import datetime
from LANforge.lfcli_base import LFCliBase
import argparse
import time

class graphdata(LFCliBase):
    def __init__(self,
                 _host="localhost",
                 _port=8080,
                 _influx_user=None,
                 _influx_passwd=None,
                 _influx_db=None,
                 _longevity=None,
                 _monitor_interval=None,
                 _devices=None,
                 _debug_on=False,
                 _exit_on_fail=False
                 ):
        super().__init__(_host,
                         _port,
                         _debug=_debug_on,
                         _exit_on_fail=_exit_on_fail)
        self.host=_host
        self.port=_port
        self.influx_user=_influx_user
        self.influx_passwd=_influx_passwd
        self.influx_db=_influx_db
        self.longevity=_longevity
        self.stations=_devices
        self.monitor_interval=_monitor_interval
    def getdata(self):
        url='http://192.168.1.32:8080/port/1/1/'
        client = InfluxDBClient(self.host,
                                8086,
                                self.influx_user,
                                self.influx_passwd,
                                self.influx_db)
        end=datetime.datetime.now()+datetime.timedelta(0, self.longevity)
        while datetime.datetime.now() < end:
            stations=self.stations
            for station in stations:
                url1=url+station
                response = json.loads(requests.get(url1).text)
                for key in response['interface'].keys():
                    json_body = [
                        {
                            "measurement": station+' '+key,
                            "tags": {
                                "host": self.host,
                                "region": "us-west"
                            },
                            "time":str(datetime.datetime.utcnow().isoformat()),
                            "fields": {
                                "value":response['interface'][key]
                            }
                        }
                    ]
                    client.write_points(json_body)
            time.sleep(self.monitor_interval)

def main():
    parser = LFCliBase.create_bare_argparse(
        prog='recordinflux.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
        Record data to an Influx database in order to be able stream to Grafana or other graphing software''',
        description='''
        recordinflux.py:
        ----------------------------
        Generic command example:
        ./recordinflux.py --influx_user  lanforge \\
        --influx_passwd password \\
        --influx_db lanforge \\
        --stations \\
        --longevity 5h'''
    )
    parser.add_argument('--influx_user', help='Username for your Influx database', required=True)
    parser.add_argument('--influx_passwd', help='Password for your Influx database', required=True)
    parser.add_argument('--influx_db', help='Name of your Influx database', required=True)
    parser.add_argument('--longevity', help='How long you want to gather data', default='4h')
    parser.add_argument('--device', help='Device to monitor', action='append', required=True)
    parser.add_argument('--monitor_interval', help='How frequently you want to append to your database', default='5s')
    args = parser.parse_args()
    monitor_interval=LFCliBase.parse_time(args.monitor_interval).total_seconds()
    longevity=LFCliBase.parse_time(args.longevity).total_seconds()
    grapher=graphdata(_host=args.mgr,
                      _port=args.mgr_port,
                      _influx_db=args.influx_db,
                      _influx_user=args.influx_user,
                      _influx_passwd=args.influx_passwd,
                      _longevity=longevity,
                      _devices=args.device,
                      _monitor_interval=monitor_interval)
    grapher.getdata()

if __name__ == "__main__":
    main()
