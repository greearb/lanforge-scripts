#!/usr/bin/env python3

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests to Grafana     -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import requests

import jwt
from datetime import datetime as date


class GhostRequest:
    def __init__(self,
                 _ghostjson_host,
                 _ghostjson_port,
                 _api_token=None,
                 _headers=dict(),
                 _overwrite='false',
                 debug_=False,
                 die_on_error_=False):
        self.debug = debug_
        self.die_on_error = die_on_error_
        self.ghostjson_url = "http://%s:%s/ghost/api/v3" % (_ghostjson_host, _ghostjson_port)
        self.data = dict()
        self.data['overwrite'] = _overwrite
        self.ghostjson_login = self.ghostjson_url + '/admin/session/'
        self.api_token = _api_token


    def create_post(self,
                    title=None,
                    text=None,
                    tags=None,
                    authors=None,
                    status="published"):
        ghostjson_url = self.ghostjson_url + '/admin/posts/'
        datastore = dict()
        datastore['title'] = title
        if tags is not None:
            datastore['tags'] = tags
        if authors is not None:
            datastore['authors'] = authors
        datastore['html'] = text
        datastore['status'] = status
        post = dict()
        posts = list()
        datastore = dict()
        datastore['html'] = text
        datastore['title'] = title
        datastore['status'] = status
        posts.append(datastore)
        post['posts'] = posts

        headers = dict()

        # Split the key into ID and SECRET
        id, secret = self.api_token.split(':')

        # Prepare header and payload
        iat = int(date.now().timestamp())

        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/v3/admin/'
        }
        token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
        headers['Authorization'] = 'Ghost {}'.format(token)
        requests.post(ghostjson_url, json=post, headers=headers)
