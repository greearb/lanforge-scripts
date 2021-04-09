#!/usr/bin/env python3

# pip3 install influxdb-client

# Version 2.0 influx DB Client

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import requests
import json
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
from LANforge.lfcli_base import LFCliBase
import time


class RecordInflux(LFCliBase):
    def __init__(self,
                 _lfjson_host="lanforge",
                 _lfjson_port=8080,
                 _influx_host="localhost",
                 _influx_port=8086,
                 _influx_org=None,
                 _influx_token=None,
                 _influx_bucket=None,
                 _debug_on=False,
                 _exit_on_fail=False):
        super().__init__(_lfjson_host, _lfjson_port,
                         _debug=_debug_on,
                         _exit_on_fail=_exit_on_fail)
        self.influx_host = _influx_host
        self.influx_port = _influx_port
        self.influx_org = _influx_org
        self.influx_token = _influx_token
        self.influx_bucket = _influx_bucket
        url = "http://%s:%s"%(self.influx_host, self.influx_port)
        self.client = influxdb_client.InfluxDBClient(url=url, token=self.influx_token, org=self.influx_org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        #print("org: ", self.influx_org)
        #print("token: ", self.influx_token)
        #print("bucket: ", self.influx_bucket)
        #exit(0)

    def post_to_influx(self, key, value, tags, time):
        p = influxdb_client.Point(key)
        for tag_key, tag_value in tags.items():
            p.tag(tag_key, tag_value)
        p.time(time)
        p.field("value", value)
        self.write_api.write(bucket=self.influx_bucket, org=self.influx_org, record=p)

    def set_bucket(self, b):
        self.influx_bucket = b

    # Don't use this unless you are sure you want to.
    # More likely you would want to generate KPI in the
    # individual test cases and poke those relatively small bits of
    # info into influxdb.
    # This will not end until the 'longevity' timer has expired.
    # This function pushes data directly into the Influx database and defaults to all columns.
    def monitor_port_data(self,
                          lanforge_host="localhost",
                          devices=None,
                          longevity=None,
                          monitor_interval=None,
                          bucket=None,
                          tags=None):  # dict
        url = 'http://' + lanforge_host + ':8080/port/1/1/'
        end = datetime.datetime.now() + datetime.timedelta(0, longevity)
        while datetime.datetime.now() < end:
            for station in devices:
                url1 = url + station
                response = json.loads(requests.get(url1).text)

                time = str(datetime.datetime.utcnow().isoformat())

                # Poke everything into influx db
                for key in response['interface'].keys():
                    self.posttoinflux(bucket, "%s-%s" % (station, key), response['interface'][key], tags, time)

            time.sleep(monitor_interval)
