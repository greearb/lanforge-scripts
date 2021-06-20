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
                 _grafana_token,
                 _grafanajson_host,
                 grafanajson_port=3000,
                 _folderID=0,
                 _headers=dict(),
                 _overwrite='false',
                 debug_=False,
                 die_on_error_=False):
        self.debug = debug_
        self.die_on_error = die_on_error_
        self.headers = _headers
        self.headers['Authorization'] = 'Bearer ' + _grafana_token
        self.headers['Content-Type'] = 'application/json'
        self.grafanajson_host = _grafanajson_host
        self.grafanajson_port = grafanajson_port
        self.grafanajson_token = _grafana_token
        self.grafanajson_url = "http://%s:%s" % (_grafanajson_host, grafanajson_port)
        self.data = dict()
        self.data['overwrite'] = _overwrite

    def create_bucket(self,
                      bucket_name=None):
        # Create a bucket in Grafana
        if bucket_name is not None:
            pass

    def list_dashboards(self):
        url = self.grafanajson_url + '/api/search'
        print(url)
        return json.loads(requests.get(url,headers=self.headers).text)

    def create_dashboard(self,
                         dashboard_name=None,
                         ):
        grafanajson_url = self.grafanajson_url + "/api/dashboards/db"
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
        return requests.post(grafanajson_url, headers=self.headers, data=data, verify=False)

    def delete_dashboard(self,
                         dashboard_uid=None):
        grafanajson_url = self.grafanajson_url + "/api/dashboards/uid/" + dashboard_uid
        return requests.post(grafanajson_url, headers=self.headers, verify=False)

    def create_dashboard_from_data(self,
                                   json_file=None):
        grafanajson_url = self.grafanajson_url + '/api/dashboards/db'
        datastore = dict()
        dashboard = dict(json.loads(open(json_file).read()))
        datastore['dashboard'] = dashboard
        datastore['overwrite'] = False
        data = json.dumps(datastore, indent=4)
        #return print(data)
        return requests.post(grafanajson_url, headers=self.headers, data=data, verify=False)

    def create_dashboard_from_dict(self,
                                   dictionary=None):
        grafanajson_url = self.grafanajson_url + '/api/dashboards/db'
        datastore = dict()
        dashboard = dict(json.loads(dictionary))
        datastore['dashboard'] = dashboard
        datastore['overwrite'] = False
        data = json.dumps(datastore, indent=4)
        #return print(data)
        return requests.post(grafanajson_url, headers=self.headers, data=data, verify=False)


    def create_custom_dashboard(self,
                                datastore=None):
        data = json.dumps(datastore, indent=4)
        return requests.post(self.grafanajson_url, headers=self.headers, data=data, verify=False)

    def create_snapshot(self, title):
        grafanajson_url = self.grafanajson_url + '/api/snapshots'
        data=self.get_dashboard(title)
        data['expires'] = 3600
        data['external'] = True
        print(data)
        return requests.post(grafanajson_url, headers=self.headers, json=data, verify=False).text

    def list_snapshots(self):
        grafanajson_url = self.grafanajson_url + '/api/dashboard/snapshots'
        print(grafanajson_url)
        return json.loads(requests.get(grafanajson_url, headers=self.headers, verify=False).text)

    def get_dashboard(self, target):
        dashboards = self.list_dashboards()
        for dashboard in dashboards:
            if dashboard['title'] == target:
                uid = dashboard['uid']
        grafanajson_url = self.grafanajson_url + '/api/dashboards/uid/' + uid
        print(grafanajson_url)
        return json.loads(requests.get(grafanajson_url, headers=self.headers, verify=False).text)