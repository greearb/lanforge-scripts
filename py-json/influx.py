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


class RecordInflux(LFCliBase):
    def __init__(self,
                 _host="localhost",
                 _port=8080,
                 _influx_user=None,
                 _influx_passwd=None,
                 _influx_db=None,
                 _longevity=None,
                 _monitor_interval=None,
                 _target_kpi=None,
                 _devices=None,
                 _debug_on=False,
                 _exit_on_fail=False
                 ):
        super().__init__(_host,
                         _port,
                         _debug=_debug_on,
                         _exit_on_fail=_exit_on_fail)
        self.host = _host
        self.port = _port
        self.influx_user = _influx_user
        self.influx_passwd = _influx_passwd
        self.influx_db = _influx_db
        self.longevity = _longevity
        self.stations = _devices
        self.monitor_interval = _monitor_interval
        self.target_kpi = _target_kpi

    def posttoinflux(self,station,key,response,client):
        json_body = [
            {
                "measurement": station + ' ' + key,
                "tags": {
                    "host": self.host,
                    "region": "us-west"
                },
                "time": str(datetime.datetime.utcnow().isoformat()),
                "fields": {
                    "value": response['interface'][key]
                }
            }
        ]
        client.write_points(json_body)

    def getdata(self):
        url = 'http://'+self.host+':8080/port/1/1/'
        client = InfluxDBClient(self.host,
                                8086,
                                self.influx_user,
                                self.influx_passwd,
                                self.influx_db)
        end = datetime.datetime.now() + datetime.timedelta(0, self.longevity)
        while datetime.datetime.now() < end:
            stations = self.stations
            for station in stations:
                url1 = url + station
                response = json.loads(requests.get(url1).text)
                if self.target_kpi is None:
                    for key in response['interface'].keys():
                        self.posttoinflux(station, key, response, client)
                else:
                    targets=self.target_kpi+['ip','ipv6 address','alias','mac']
                    response['interface']={your_key: response['interface'][your_key] for your_key in targets}
                    for key in  response['interface'].keys():
                        self.posttoinflux(station, key, response, client)

            time.sleep(self.monitor_interval)
