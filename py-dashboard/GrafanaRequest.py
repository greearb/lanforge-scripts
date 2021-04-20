#!/usr/bin/env python3

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests to Grafana     -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import requests

import json


class GrafanaRequest:
    def __init__(self,
                 _grafanajson_host,
                 _grafanajson_port,
                 _folderID=0,
                 _api_token=None,
                 _headers=dict(),
                 _overwrite='false',
                 debug_=False,
                 die_on_error_=False):
        self.debug = debug_
        self.die_on_error = die_on_error_
        self.headers = _headers
        self.headers['Authorization'] = 'Bearer ' + _api_token
        self.headers['Content-Type'] = 'application/json'
        self.grafanajson_url = "http://%s:%s" % (_grafanajson_host, _grafanajson_port)
        self.data = dict()
        self.data['overwrite'] = _overwrite

    def create_bucket(self,
                      bucket_name=None):
        # Create a bucket in Grafana
        if bucket_name is not None:
            pass

    def list_dashboards(self):
        url = self.grafanajson_url + '/api/search?folderIds=0&query=&starred=false'
        return requests.get(url).text

    def create_dashboard(self,
                         dashboard_name=None,
                         ):
        self.grafanajson_url = self.grafanajson_url + "/api/dashboards/db"

        data = (
                    '{ "dashboard": { "id": null, "title": "%s" , "tags": [ "templated" ], "timezone": "browser", "schemaVersion": 6, "version": 0 }, "overwrite": false }' % dashboard_name)
        return requests.get(self.grafanajson_url, headers=self.headers, data=data, verify=False)

    def delete_dashboard(self,
                         dashboard_uid=None):
        self.grafanajson_url = self.grafanajson_url + "/api/dashboards/uid/" + dashboard_uid
        return requests.post(self.grafanajson_url, headers=self.headers, verify=False)

    def create_dashboard_from_data(self,
                                   json_file=None):
        pass
