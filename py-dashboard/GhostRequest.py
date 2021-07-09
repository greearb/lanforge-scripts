#!/usr/bin/env python3

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests to Ghost     -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import requests

import jwt
from datetime import datetime
import json
import subprocess
from scp import SCPClient
import paramiko
from GrafanaRequest import GrafanaRequest
from influx2 import RecordInflux
import time
from collections import Counter
import shutil


class CSVReader:
    def read_csv(self,
                 file,
                 sep=','):
        df = open(file).read().split('\n')
        rows = list()
        for x in df:
            if len(x) > 0:
                rows.append(x.split(sep))
        length = list(range(0, len(df[0])))
        columns = dict(zip(df[0], length))
        return rows

    def get_column(self,
                   df,
                   value):
        index = df[0].index(value)
        values = []
        for row in df[1:]:
            values.append(row[index])
        return values

    def get_columns(self, df, targets):
        target_index = []
        for item in targets:
            target_index.append(df[0].index(item))
        results = []
        for row in df:
            row_data = []
            for x in target_index:
                row_data.append(row[x])
            results.append(row_data)
        return results

    def to_html(self, df):
        html = ''
        html = html + ('<table style="border:1px solid #ddd">'
                       '<colgroup>'
                       '<col style="width:25%">'
                       '<col style="width:25%">'
                       '<col style="width:50%">'
                       '</colgroup>'
                       '<tbody>'
                       '<tr>')
        for row in df:
            for item in row:
                html = html + ('<td style="border:1px solid #ddd">%s</td>' % item)
            html = html + ('</tr>\n<tr>')
        html = html + ('</tbody>'
                       '</table>')
        return html

    def filter_df(self, df, column, expression, target):
        target_index = df[0].index(column)
        counter = 0
        targets = [0]
        for row in df:
            try:
                if expression == 'less than':
                    if float(row[target_index]) < target:
                        targets.append(counter)
                        counter += 1
                    else:
                        counter += 1
                if expression == 'greater than':
                    if float(row[target_index]) > target:
                        targets.append(counter)
                        counter += 1
                    else:
                        counter += 1
                if expression == 'greater than or equal to':
                    if float(row[target_index]) >= target:
                        targets.append(counter)
                        counter += 1
                    else:
                        counter += 1
            except:
                counter += 1
        return list(map(df.__getitem__, targets))

    def concat(self, dfs):
        final_df = dfs[0]
        for df in dfs[1:]:
            final_df = final_df + df[1:]
        return final_df


class GhostRequest:
    def __init__(self,
                 _ghost_json_host,
                 _ghost_json_port,
                 _api_token=None,
                 _overwrite='false',
                 debug_=False,
                 die_on_error_=False,
                 influx_host=None,
                 influx_port=8086,
                 influx_org=None,
                 influx_token=None,
                 influx_bucket=None):
        self.debug = debug_
        self.die_on_error = die_on_error_
        self.ghost_json_host = _ghost_json_host
        self.ghost_json_port = _ghost_json_port
        self.ghost_json_url = "http://%s:%s/ghost/api/v3" % (_ghost_json_host, _ghost_json_port)
        self.data = dict()
        self.data['overwrite'] = _overwrite
        self.ghost_json_login = self.ghost_json_url + '/admin/session/'
        self.api_token = _api_token
        self.images = list()
        self.pdfs = list()
        self.influx_host = influx_host
        self.influx_port = influx_port
        self.influx_org = influx_org
        self.influx_token = influx_token
        self.influx_bucket = influx_bucket

    def encode_token(self):

        # Split the key into ID and SECRET
        key_id, secret = self.api_token.split(':')

        # Prepare header and payload
        iat = int(datetime.now().timestamp())

        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/v3/admin/'
        }
        token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
        return token

    def create_post(self,
                    title=None,
                    text=None,
                    tags=None,
                    authors=None,
                    status="published"):
        ghost_json_url = self.ghost_json_url + '/admin/posts/?source=html'
        post = dict()
        posts = list()
        datastore = dict()
        datastore['html'] = text
        datastore['title'] = title
        datastore['status'] = status
        posts.append(datastore)
        post['posts'] = posts

        headers = dict()

        token = self.encode_token()
        headers['Authorization'] = 'Ghost {}'.format(token)
        response = requests.post(ghost_json_url, json=post, headers=headers)
        if self.debug:
            print(datastore)
            print(ghost_json_url)
            print('\n')
            print(post)
            print('\n')
            print(headers)
            print(response.headers)

    def upload_image(self,
                     image):
        print(image)
        ghost_json_url = self.ghost_json_url + '/admin/images/upload/'

        token = self.encode_token()
        bashCommand = "curl -X POST -F 'file=@%s' -H \"Authorization: Ghost %s\" %s" % (image, token, ghost_json_url)

        proc = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE)
        output = proc.stdout.read().decode('utf-8')
        print(output)
        self.images.append(json.loads(output)['images'][0]['url'])

    def upload_images(self,
                      folder):
        for image in os.listdir(folder):
            if 'kpi' in image:
                if 'png' in image:
                    self.upload_image(folder + '/' + image)
        print('images %s' % self.images)

    def custom_post(self,
                    folder,
                    authors,
                    title='custom'):
        self.upload_images(folder)
        head = '''<p>This is a custom post created via a script</p>'''
        for picture in self.images:
            head = head + '<img src="%s"></img>' % picture
        head = head + '''<p>This is the end of the example</p>'''
        self.create_post(title=title,
                         text=head,
                         tags='custom',
                         authors=authors)

    def list_append(self, list_1, value):
        list_1.append(value)

    def kpi_to_ghost(self,
                     authors,
                     folders,
                     parent_folder=None,
                     title=None,
                     server_pull=None,
                     ghost_host=None,
                     port=22,
                     user_push=None,
                     password_push=None,
                     customer=None,
                     testbed='Unknown Testbed',
                     test_run=None,
                     target_folders=list(),
                     grafana_token=None,
                     grafana_host=None,
                     grafana_port=3000,
                     grafana_datasource='InfluxDB',
                     grafana_bucket=None):
        global dut_hw, dut_sw, dut_model, dut_serial
        text = ''
        csvreader = CSVReader()
        if grafana_token is not None:
            grafana = GrafanaRequest(grafana_token,
                                     grafana_host,
                                     grafanajson_port=grafana_port
                                     )
        if self.debug:
            print('Folders: %s' % folders)

        ssh_push = paramiko.SSHClient()
        ssh_push.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh_push.connect(ghost_host,
                         port,
                         username=user_push,
                         password=password_push,
                         allow_agent=False,
                         look_for_keys=False)
        scp_push = SCPClient(ssh_push.get_transport())

        if parent_folder is not None:
            print("parent_folder %s" % parent_folder)
            files = os.listdir(parent_folder)
            print(files)
            for file in files:
                if os.path.isdir(parent_folder + '/' + file) is True:
                    if os.path.exists(file):
                        shutil.rmtree(file)
                    shutil.copytree(parent_folder + '/' + file, file)
                    target_folders.append(file)
            print('Target folders: %s' % target_folders)
        else:
            for folder in folders:
                if self.debug:
                    print(folder)
                target_folders.append(folder)

        testbeds = list()
        pdfs = list()
        high_priority_list = list()
        low_priority_list = list()
        images = list()
        times = list()
        test_pass_fail = list()
        devices = dict()

        for target_folder in target_folders:
            try:
                target_file = '%s/kpi.csv' % target_folder
                df = csvreader.read_csv(file=target_file, sep='\t')
                csv_testbed = csvreader.get_column(df, 'test-rig')[0]
                pass_fail = Counter(csvreader.get_column(df, 'pass/fail'))
                test_pass_fail.append(pass_fail)
                dut_hw = csvreader.get_column(df, 'dut-hw-version')[0]
                dut_sw = csvreader.get_column(df, 'dut-sw-version')[0]
                dut_model = csvreader.get_column(df, 'dut-model-num')[0]
                dut_serial = csvreader.get_column(df, 'dut-serial-num')[0]
                devices[csv_testbed] = [dut_hw, dut_sw, dut_model, dut_serial]
                times_append = csvreader.get_column(df, 'Date')
                for target_time in times_append:
                    times.append(float(target_time) / 1000)
                if pass_fail['PASS'] + pass_fail['FAIL'] > 0:
                    text = text + 'Tests passed: %s<br />' % pass_fail['PASS']
                    text = text + 'Tests failed: %s<br />' % pass_fail['FAIL']
                    text = text + 'Percentage of tests passed: %s<br />' % (
                            pass_fail['PASS'] / (pass_fail['PASS'] + pass_fail['FAIL']))
                else:
                    text = text + 'Tests passed: 0<br />' \
                                  'Tests failed : 0<br />' \
                                  'Percentage of tests passed: Not Applicable<br />'

            except:
                print("Failure")
                target_folders.remove(target_folder)
                break
            testbeds.append(csv_testbed)
            if testbed == 'Unknown Testbed':
                raise UserWarning('Please define your testbed')

            local_path = '/home/%s/%s/%s' % (user_push, customer, testbed)

            transport = paramiko.Transport(ghost_host, port)
            transport.connect(None, user_push, password_push)
            sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)

            if self.debug:
                print(local_path)
                print(target_folder)
            scp_push.put(target_folder, local_path, recursive=True)
            files = sftp.listdir(local_path + '/' + target_folder)
            for file in files:
                if 'pdf' in file:
                    url = 'http://%s/%s/%s/%s/%s' % (
                        ghost_host, customer.strip('/'), testbed, target_folder, file)
                    pdfs.append('PDF of results: <a href="%s">%s</a><br />' % (url, file))
            scp_push.close()
            self.upload_images(target_folder)
            for image in self.images:
                if 'kpi-' in image:
                    if '-print' not in image:
                        images.append('<img src="%s"></img>' % image)
            self.images = []

            results = csvreader.get_columns(df, ['short-description', 'numeric-score', 'test details', 'pass/fail',
                                                 'test-priority'])

            results[0] = ['Short Description', 'Score', 'Test Details', 'Pass or Fail', 'test-priority']

            low_priority = csvreader.filter_df(results, 'test-priority', 'less than', 94)
            high_priority = csvreader.filter_df(results, 'test-priority', 'greater than or equal to', 95)
            high_priority_list.append(high_priority)

            low_priority_list.append(low_priority)

        now = datetime.now()

        test_pass_fail_results = sum((Counter(test) for test in test_pass_fail), Counter())

        end_time = max(times)
        start_time = '2021-07-01'
        end_time = datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

        high_priority = csvreader.concat(high_priority_list)
        low_priority = csvreader.concat(low_priority_list)

        high_priority = csvreader.get_columns(high_priority,
                                              ['Short Description', 'Score', 'Test Details'])
        low_priority = csvreader.get_columns(low_priority,
                                             ['Short Description', 'Score', 'Test Details'])
        high_priority.append(['Total Passed', test_pass_fail_results['PASS'], 'Total subtests passed during this run'])
        high_priority.append(['Total Failed', test_pass_fail_results['FAIL'], 'Total subtests failed during this run'])

        if title is None:
            title = now.strftime('%B %d, %Y %I:%M %p report')

        # create Grafana Dashboard
        target_files = []
        for folder in target_folders:
            target_files.append(folder.split('/')[-1] + '/kpi.csv')
        if self.debug:
            print('Target files: %s' % target_files)
        grafana.create_custom_dashboard(target_csvs=target_files,
                                        title=title,
                                        datasource=grafana_datasource,
                                        bucket=grafana_bucket,
                                        from_date=start_time,
                                        to_date=end_time,
                                        pass_fail='GhostRequest',
                                        testbed=testbeds[0])

        if self.influx_token is not None:
            influxdb = RecordInflux(_influx_host=self.influx_host,
                                    _influx_port=self.influx_port,
                                    _influx_org=self.influx_org,
                                    _influx_token=self.influx_token,
                                    _influx_bucket=self.influx_bucket)
            short_description = 'Ghost Post Tests passed'  # variable name
            numeric_score = test_pass_fail_results['PASS']  # value
            tags = dict()
            print(datetime.utcfromtimestamp(max(times)))
            tags['testbed'] = testbeds[0]
            tags['script'] = 'GhostRequest'
            tags['Graph-Group'] = 'PASS'
            date = datetime.utcfromtimestamp(max(times)).isoformat()
            influxdb.post_to_influx(short_description, numeric_score, tags, date)

            short_description = 'Ghost Post Tests failed'  # variable name
            numeric_score = test_pass_fail_results['FAIL']  # value
            tags = dict()
            tags['testbed'] = testbeds[0]
            tags['script'] = 'GhostRequest'
            tags['Graph-Group'] = 'FAIL'
            date = datetime.utcfromtimestamp(max(times)).isoformat()
            influxdb.post_to_influx(short_description, numeric_score, tags, date)

        text = 'Testbed: %s<br />' % testbeds[0]
        dut_table = '<table style="border:1px solid #ddd"><tr>' \
                    '<td>Device</td>' \
                    '<td>DUT_HW</td>' \
                    '<td>DUT_SW</td>' \
                    '<td>DUT model</td>' \
                    '<td>DUT Serial</td>' \
                    '<td>Tests passed</td>' \
                    '<td>Tests failed</td></tr>'
        for device, data in devices.items():
            dut_table = dut_table + '<tr><td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td>' \
                                    '<td style="white-space:nowrap; border:1px solid #ddd">%s</td></tr></table>' % (
                    device, data[0], data[1], data[2], data[3], test_pass_fail_results['PASS'],
                    test_pass_fail_results['FAIL'])
        text = text + dut_table

        for pdf in pdfs:
            text = text + pdf

        for image in images:
            text = text + image

        text = text + 'High priority results: %s' % csvreader.to_html(high_priority)

        if grafana_token is not None:
            # get the details of the dashboard through the API, and set the end date to the youngest KPI
            grafana.list_dashboards()

            grafana.create_snapshot(title='Testbed: ' + title)
            time.sleep(3)
            snapshot = grafana.list_snapshots()[-1]
            text = text + '<iframe src="http://%s:3000/dashboard/snapshot/%s" width="100%s" height=1500></iframe><br />' % (
                grafana_host, snapshot['key'], '%')

        text = text + 'Low priority results: %s' % csvreader.to_html(low_priority)

        self.create_post(title=title,
                         text=text,
                         tags='custom',
                         authors=authors)
