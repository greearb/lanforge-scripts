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
import string
import random


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

    def groupby(self, params, grouptype):
        dic = dict()
        dic['params'] = list()
        dic['params'].append(params)
        dic['type'] = grouptype
        return dic

    def maketargets(self,
                    bucket,
                    scriptname,
                    groupBy,
                    index,
                    graph_group):
        targets = dict()
        targets['delimiter'] = ','
        targets['groupBy'] = groupBy
        targets['header'] = True
        targets['ignoreUnknown'] = False
        targets['orderByTime'] = 'ASC'
        targets['policy'] = 'default'
        targets['query'] = (
                'from(bucket: "%s")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r["script"] == "%s")\n  |> filter(fn: (r) => r["Graph-Group"] == "%s")\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\n  |> yield(name: "mean")\n  ' % (
            bucket, scriptname, graph_group))
        targets['refId'] = dict(enumerate(string.ascii_uppercase, 1))[index + 1]
        targets['resultFormat'] = "time_series"
        targets['schema'] = list()
        targets['skipRows'] = 0
        targets['tags'] = list()
        return targets

    def create_custom_dashboard(self,
                                scripts=None,
                                title=None,
                                bucket=None):
        options = string.ascii_lowercase + string.ascii_uppercase + string.digits
        uid = ''.join(random.choice(options) for i in range(9))
        input1 = dict()
        annotations = dict()
        annotations['builtIn'] = 1
        annotations['datasource'] = '-- Grafana --'
        annotations['enable'] = True
        annotations['hide'] = True
        annotations['iconColor'] = 'rgba(0, 211, 255, 1)'
        annotations['name'] = 'Annotations & Alerts'
        annotations['type'] = 'dashboard'
        annot = dict()
        annot['list'] = list()
        annot['list'].append(annotations)

        templating = dict()
        templating['list'] = list()

        timedict = dict()
        timedict['from'] = 'now-1y'
        timedict['to'] = 'now'

        panels = list()
        index = 1
        for scriptname in scripts:
            graph_groups = ['Per Stations Rate DL',
                            'Per Stations Rate UL',
                            'Per Stations Rate UL+DL']
            for graph_group in graph_groups:
                panel = dict()

                gridpos = dict()
                gridpos['h'] = 8
                gridpos['w'] = 12
                gridpos['x'] = 0
                gridpos['y'] = 0

                legend = dict()
                legend['avg'] = False
                legend['current'] = False
                legend['max'] = False
                legend['min'] = False
                legend['show'] = True
                legend['total'] = False
                legend['values'] = False

                options = dict()
                options['alertThreshold'] = True

                groupBy = list()
                groupBy.append(self.groupby('$__interval', 'time'))
                groupBy.append(self.groupby('null', 'fill'))

                targets = list()
                counter = 0
                new_target = self.maketargets(bucket, scriptname, groupBy, counter, graph_group)
                targets.append(new_target)

                fieldConfig = dict()
                fieldConfig['defaults'] = dict()
                fieldConfig['overrides'] = list()

                transformation = dict()
                transformation['id'] = "renameByRegex"
                transformation_options = dict()
                transformation_options['regex'] = "(.*) value.*"
                transformation_options['renamePattern'] = "$1"
                transformation['options'] = transformation_options

                xaxis = dict()
                xaxis['buckets'] = None
                xaxis['mode'] = "time"
                xaxis['name'] = None
                xaxis['show'] = True
                xaxis['values'] = list()

                yaxis = dict()
                yaxis['format'] = 'short'
                yaxis['label'] = None
                yaxis['logBase'] = 1
                yaxis['max'] = None
                yaxis['min'] = None
                yaxis['show'] = True

                yaxis1 = dict()
                yaxis1['align'] = False
                yaxis1['alignLevel'] = None

                panel['aliasColors'] = dict()
                panel['bars'] = False
                panel['dashes'] = False
                panel['dashLength'] = 10
                panel['datasource'] = 'InfluxDB'
                panel['fieldConfig'] = fieldConfig
                panel['fill'] = 0
                panel['fillGradient'] = 0
                panel['gridPos'] = gridpos
                panel['hiddenSeries'] = False
                panel['id'] = index
                panel['legend'] = legend
                panel['lines'] = True
                panel['linewidth'] = 1
                panel['nullPointMode'] = 'null'
                panel['options'] = options
                panel['percentage'] = False
                panel['pluginVersion'] = '7.5.4'
                panel['pointradius'] = 2
                panel['points'] = True
                panel['renderer'] = 'flot'
                panel['seriesOverrides'] = list()
                panel['spaceLength'] = 10
                panel['stack'] = False
                panel['steppedLine'] = False
                panel['targets'] = targets
                panel['thresholds'] = list()
                panel['timeFrom'] = None
                panel['timeRegions'] = list()
                panel['timeShift'] = None
                panel['title'] = scriptname+' '+graph_group
                panel['transformations'] = list()
                panel['transformations'].append(transformation)
                panel['type'] = "graph"
                panel['xaxis'] = xaxis
                panel['yaxes'] = list()
                panel['yaxes'].append(yaxis)
                panel['yaxes'].append(yaxis)
                panel['yaxis'] = yaxis1

                panels.append(panel)
                index = index + 1
        input1['annotations'] = annot
        input1['editable'] = True
        input1['gnetId'] = None
        input1['graphTooltip'] = 0
        input1['links'] = list()
        input1['panels'] = panels
        input1['refresh'] = False
        input1['schemaVersion'] = 27
        input1['style'] = 'dark'
        input1['tags'] = list()
        input1['templating'] = templating
        input1['time'] = timedict
        input1['timepicker'] = dict()
        input1['timezone'] = ''
        input1['title'] = title
        input1['uid'] = uid
        input1['version'] = 11
        # print(json.dumps(input1, indent=2))
        return self.GR.create_dashboard_from_dict(dictionary=json.dumps(input1))


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
    optional.add_argument('--dashboard_title', help='Titles of dashboards', default=None, action='append')
    optional.add_argument('--scripts', help='Scripts to graph in Grafana', default=None, action='append')
    optional.add_argument('--title', help='title of your Grafana Dashboard', default=None)
    optional.add_argument('--grafana_bucket', help='Name of your Grafana Bucket', default=None)
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
        Grafana.create_custom_dashboard(scripts=args.scripts,
                                        title=args.title,
                                        bucket=args.grafana_bucket)


if __name__ == "__main__":
    main()
