#!/usr/bin/env python3

import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-dashboard'))

from GrafanaRequest import GrafanaRequest
from LANforge.lfcli_base import LFCliBase
import json

class UseGrafana(LFCliBase):
    def __init__(self,
                 _grafana_token,
                 host="localhost",
                 _grafana_host="localhost",
                 port=8080,
                 _debug_on=False,
                 _exit_on_fail=False,
                 _grafana_port=3000):
        super().__init__(host, port, _debug=_debug_on, _exit_on_fail=_exit_on_fail)
        self.grafana_token = _grafana_token
        self.grafana_port = _grafana_port
        self.grafana_host = _grafana_host
        self.GR = GrafanaRequest(self.grafana_host, str(self.grafana_port), _folderID=0, _api_token=self.grafana_token)

    def create_dashboard(self,
                         dashboard_name):
        return self.GR.create_dashboard(dashboard_name)

    def delete_dashboard(self,
                         dashboard_uid):
        return self.GR.delete_dashboard(dashboard_uid)

    def list_dashboards(self):
        return self.GR.list_dashboards()

    def create_dashboard_from_data(self,
                                   json_file):
        return self.GR.create_dashboard_from_data(json_file=json_file)

    def create_custom_dashboard(self):
        name = input('Name of your dashboard: ')
        number = input('Number of panels on dashboard: ')
        dashboards = dict()
        dashboards['title'] = name
        dashboards['panels'] = list()
        input1 = dict()
        input1['name'] = "DS_INFLUXDB"
        input1['label'] = "InfluxDB"
        input1['description'] = ""
        input1['type'] = "datasource"
        input1['pluginId'] = "influxdb"
        input1['pluginName'] = "InfluxDB"
        inputs = list()
        inputs.append(input1)
        dashboards['__inputs'] = inputs

        for dashboard in range(0,int(number)):
            title = input('Title of dashboard # %s ' % dashboard)
            lines = input('Lines on your graph? Y or N: ')
            target_number = input('How many targets on your graph? ')
            if lines == 'Y':
                lines = True
                linewidth = 1
            else:
                lines = False
                linewidth = 0
            panel = dict()
            panel['aliasColors'] = dict()
            panel['bars'] = False
            panel['dashLength'] = 10
            fieldConfig = dict()
            fieldConfig['defaults'] = dict()
            fieldConfig['overrides'] = list()
            panel['fieldConfig'] = fieldConfig
            panel['fill'] = 1
            panel['fieldGradient'] = 0
            panel['hiddenSeries'] = False
            panel['id'] = dashboard
            panel['lines'] = lines
            panel['linewidth'] = linewidth
            panel['nullPointMode'] = None
            panel['percentage'] = False
            panel['pluginVersion'] = "7.5.4"
            panel['stack'] = False
            targets = list()
            for target in range(0,int(target_number)):
                measurement = input('Name of  your first measurement')
                target_item = dict()
                target_item['delimiter'] = ','
                target_item['header'] = True
                target_item['ignoreUnknown'] = False
                target_item['measurement'] = measurement
                target_item['orderByTime'] = "ASC"
                target_item['policy'] = "default"
                target_item['skipRows'] = 0
                targets.append(target_item)
            panel['targets'] = targets
            panel['title'] = title
            xaxis=dict()
            xaxis['buckets'] = None
            xaxis['mode'] = "time"
            xaxis['name'] = None
            xaxis['show'] = True
            xaxis['values'] = list()
            panel['xaxis'] = xaxis
            yaxis = dict()
            yaxis['align'] = False
            yaxis['alignLevel'] = None
            panel['yaxis'] = yaxis
            dashboards['panels'].append(panel)
        print(json.dumps(dashboards, indent=2))
        return self.GR.create_dashboard_from_dict(dictionary=json.dumps(dashboards))

def main():
    parser = LFCliBase.create_basic_argparse(
        prog='grafana_profile.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Manage Grafana database''',
        description='''\
        grafana_profile.py
        ------------------
        Command example:
        ./grafana_profile.py
            --grafana_token 
            --''')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--grafana_token', help='token to access your Grafana database', required=True)

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--dashboard_name', help='name of dashboard to create', default=None)
    optional.add_argument('--dashboard_uid', help='UID of dashboard to modify', default=None)
    optional.add_argument('--delete_dashboard',
                          help='Call this flag to delete the dashboard defined by UID',
                          default=None)
    optional.add_argument('--grafana_port', help='Grafana port if different from 3000', default=3000)
    optional.add_argument('--grafana_host', help='Grafana host', default='localhost')
    optional.add_argument('--list_dashboards', help='List dashboards on Grafana server', default=None)
    optional.add_argument('--dashboard_json', help='JSON of existing Grafana dashboard to import', default=None)
    optional.add_argument('--create_custom', help='Guided Dashboard creation', default=None)
    args = parser.parse_args()

    Grafana = UseGrafana(args.grafana_token,
                         args.grafana_port,
                         args.grafana_host
                         )
    if args.dashboard_name is not None:
        Grafana.create_dashboard(args.dashboard_name)

    if args.delete_dashboard is not None:
        Grafana.delete_dashboard(args.dashboard_uid)

    if args.list_dashboards is not None:
        Grafana.list_dashboards()

    if args.dashboard_json is not None:
        Grafana.create_dashboard_from_data(args.dashboard_json)

    if args.create_custom is not None:
        Grafana.create_custom_dashboard()

if __name__ == "__main__":
    main()
