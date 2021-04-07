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
                 _influx_host="localhost",
                 _port=8080,
                 _influx_user=None,
                 _influx_passwd=None,
                 _influx_db=None,
                 _debug_on=False,
                 _exit_on_fail=False):
        super().__init__(_influx_host,
                         _port,
                         _debug=_debug_on,
                         _exit_on_fail=_exit_on_fail)
        self.host = _influx_host
        self.port = _port
        self.influx_user = _influx_user
        self.influx_passwd = _influx_passwd
        self.influx_db = _influx_db

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

    def getdata(self,
                devices=None,
                target_kpi=None,
                longevity=None,
                monitor_interval=None):
        url = 'http://'+self.host+':8080/port/1/1/'
        client = InfluxDBClient(self.host,
                                8086,
                                self.influx_user,
                                self.influx_passwd,
                                self.influx_db)
        end = datetime.datetime.now() + datetime.timedelta(0, longevity)
        while datetime.datetime.now() < end:
            for station in devices:
                url1 = url + station
                response = json.loads(requests.get(url1).text)
                if target_kpi is None:
                    for key in response['interface'].keys():
                        self.posttoinflux(station, key, response, client)
                else:
                    targets = target_kpi+['ip','ipv6 address','alias','mac']
                    response['interface']={your_key: response['interface'][your_key] for your_key in targets}
                    for key in  response['interface'].keys():
                        self.posttoinflux(station, key, response, client)

            time.sleep(monitor_interval)
