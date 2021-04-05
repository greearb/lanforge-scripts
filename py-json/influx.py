#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import requests
import json
from influxdb import InfluxDBClient
import datetime
from LANforge.lfcli_base import LFCliBase
import time

class Influx(LFCliBase):
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
