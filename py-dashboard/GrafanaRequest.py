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
        datastore = dict()
        dashboard = dict()
        dashboard['id'] = None
        dashboard['title'] = dashboard_name
        dashboard['tags'] = ['templated']
        dashboard['timezone'] = 'browser'
        dashboard['schemaVersion'] = 27
        dashboard['version'] = 4
        datastore['dashboard'] = dashboard
        datastore['overwrite'] = False
        data = json.dumps(datastore, indent=4)
        return requests.post(self.grafanajson_url, headers=self.headers, data=data, verify=False)

    def delete_dashboard(self,
                         dashboard_uid=None):
        self.grafanajson_url = self.grafanajson_url + "/api/dashboards/uid/" + dashboard_uid
        return requests.post(self.grafanajson_url, headers=self.headers, verify=False)

    def create_dashboard_from_data(self,
                                   json_file=None):
        self.grafanajson_url = self.grafanajson_url + '/api/dashboards/db'
        datastore = dict()
        dashboard = dict(json.loads(open(json_file).read()))
        datastore['dashboard'] = dashboard
        datastore['overwrite'] = False
        data = json.dumps(datastore, indent=4)
        #return print(data)
        return requests.post(self.grafanajson_url, headers=self.headers, data=data, verify=False)

    def create_dashboard_from_dict(self,
                                   dictionary=None):
        self.grafanajson_url = self.grafanajson_url + '/api/dashboards/db'
        datastore = dict()
        dashboard = dict(json.loads(dictionary))
        datastore['dashboard'] = dashboard
        datastore['overwrite'] = False
        data = json.dumps(datastore, indent=4)
        #return print(data)
        return requests.post(self.grafanajson_url, headers=self.headers, data=data, verify=False)


    def create_custom_dashboard(self,
                                datastore=None):
        data = json.dumps(datastore, indent=4)
        return requests.post(self.grafanajson_url, headers=self.headers, data=data, verify=False)