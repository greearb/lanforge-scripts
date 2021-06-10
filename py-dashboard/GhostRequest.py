#!/usr/bin/env python3

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests to Ghost     -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import ast
import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import requests

import jwt
from datetime import datetime as date
import json
import subprocess
from scp import SCPClient
import paramiko


class CSVReader:
    def read_csv(self,
                 file,
                 sep=','):
        csv = open(file).read().split('\n')
        rows = list()
        for x in csv:
            if len(x) > 0:
                rows.append(x.split(sep))
        length = list(range(0, len(df[0])))
        columns = dict(zip(df[0], length))
        return rows

    def get_column(df, value):
        index = df[0].index(value)
        values = []
        for row in df[1:]:
            values.append(row[index])
        return values


class GhostRequest:
    def __init__(self,
                 _ghost_json_host,
                 _ghost_json_port,
                 _api_token=None,
                 _overwrite='false',
                 debug_=False,
                 die_on_error_=False):
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

    def encode_token(self):

        # Split the key into ID and SECRET
        key_id, secret = self.api_token.split(':')

        # Prepare header and payload
        iat = int(date.now().timestamp())

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

    def wifi_capacity_to_ghost(self,
                               authors,
                               folders,
                               title='Wifi Capacity',
                               server_pull=None,
                               ghost_host=None,
                               port='22',
                               user_pull='lanforge',
                               password_pull='lanforge',
                               user_push=None,
                               password_push=None,
                               customer=None,
                               testbed=None,
                               test_run=None):
        text = '''The Candela WiFi Capacity test is designed to measure performance of an Access Point when handling 
        different amounts of WiFi Stations. The test allows the user to increase the number of stations in user 
        defined steps for each test iteration and measure the per station and the overall throughput for each trial. 
        Along with throughput other measurements made are client connection times, Fairness, % packet loss, 
        DHCP times and more. The expected behavior is for the AP to be able to handle several stations (within the 
        limitations of the AP specs) and make sure all stations get a fair amount of airtime both in the upstream and 
        downstream. An AP that scales well will not show a significant over-all throughput decrease as more stations 
        are added. 
        Realtime Graph shows summary download and upload RX bps of connections created by this test.<br />'''

        if test_run is None:
            test_run = sorted(folders)[0].split('/')[-1]
        for folder in folders:
            ssh_pull = paramiko.SSHClient()
            ssh_pull.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
            ssh_pull.connect(server_pull,
                             port,
                             username=user_pull,
                             password=password_pull,
                             allow_agent=False,
                             look_for_keys=False)
            scp_pull = SCPClient(ssh_pull.get_transport())
            scp_pull.get(folder, recursive=True)
            ssh_push = paramiko.SSHClient()
            ssh_push.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
            ssh_push.connect(ghost_host,
                             port,
                             username=user_push,
                             password=password_push,
                             allow_agent=False,
                             look_for_keys=False)
            scp_push = SCPClient(ssh_push.get_transport())
            local_path = '/home/%s/%s/%s/%s' % (user_push, customer, testbed, test_run)
            transport = paramiko.Transport((ghost_host, port))
            transport.connect(None, user_push, password_push)
            sftp = paramiko.sftp_client.SFTPClient.from_transport(transport)
            print(local_path)
            sftp.mkdir(local_path)
            target_folder = folder.split('/')[-1]
            print(target_folder)
            scp_push.put(target_folder, recursive=True, remote_path=local_path)
            files = sftp.listdir(local_path + '/' + target_folder)
            print('Files: %s' % files)
            for file in files:
                if 'pdf' in file:
                    self.pdfs.append(file)

            #df = CSVReader.read_csv(local_path + '/' + target_folder + '/' + 'kpi.csv')
            #testbed = CSVReader.get_column(df, 'test-rig')[0]

            print('PDFs %s' % self.pdfs)
            scp_pull.close()
            scp_push.close()
            self.upload_images(target_folder)

        for pdf in self.pdfs:
            url = 'http://%s/%s/%s/%s/%s/%s' % (ghost_host, customer, testbed, test_run, target_folder, pdf)
            text = text + 'PDF of results: <a href="%s">%s</a>' % (url, url)

        for image in self.images:
            if 'kpi-' in image:
                if '-print' not in image:
                    text = text + '<img src="%s"></img>' % image

        self.create_post(title=title,
                         text=text,
                         tags='custom',
                         authors=authors)
