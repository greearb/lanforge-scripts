#!/usr/bin/env python3

"""
NAME: ghost_profile.py
PURPOSE: modify ghost database from the command line.
SETUP: A Ghost installation which the user has admin access to.
EXAMPLE: ./ghost_profile.py --article_text_file text.txt --title Test --authors Matthew --ghost_token SECRET_KEY --host 192.168.1.1

There is a specific class for uploading wifi capacity graphs called wifi_capacity.

EXAMPLE: ./ghost_profile.py --ghost_token TOKEN --ghost_host 192.168.100.147
--folders /home/lanforge/html-reports/wifi-capacity-2021-06-04-02-51-07
--wifi_capacity appl --authors Matthew --title 'wifi capacity 2021 06 04 02 51 07' --server 192.168.93.51
--user_pull lanforge --password_pull lanforge --customer candela --testbed heather --test_run test-run-6
--user_push matt --password_push PASSWORD

 Matthew Stidham
 Copyright 2021 Candela Technologies Inc
    License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-dashboard'))

from GhostRequest import GhostRequest


class UseGhost:
    def __init__(self,
                 _ghost_token=None,
                 host="localhost",
                 port=8080,
                 _debug_on=False,
                 _exit_on_fail=False,
                 _ghost_host="localhost",
                 _ghost_port=2368, ):
        self.ghost_host = _ghost_host
        self.ghost_port = _ghost_port
        self.ghost_token = _ghost_token
        self.GP = GhostRequest(self.ghost_host,
                               str(self.ghost_port),
                               _api_token=self.ghost_token,
                               debug_=_debug_on)

    def create_post(self, title, text, tags, authors):
        return self.GP.create_post(title=title, text=text, tags=tags, authors=authors)

    def create_post_from_file(self, title, file, tags, authors):
        text = open(file).read()
        return self.GP.create_post(title=title, text=text, tags=tags, authors=authors)

    def upload_image(self, image):
        return self.GP.upload_image(image)

    def upload_images(self, folder):
        return self.GP.upload_images(folder)

    def custom_post(self, folder, authors):
        return self.GP.custom_post(folder, authors)

    def wifi_capacity(self,
                      authors,
                      folders,
                      title,
                      server_pull,
                      ghost_host,
                      port,
                      user_pull,
                      password_pull,
                      user_push,
                      password_push,
                      customer,
                      testbed,
                      test_run,
                      grafana_dashboard,
                      grafana_token,
                      grafana_host,
                      grafana_port):
        target_folders = list()
        return self.GP.wifi_capacity_to_ghost(authors,
                                              folders,
                                              title,
                                              server_pull,
                                              ghost_host,
                                              port,
                                              user_pull,
                                              password_pull,
                                              user_push,
                                              password_push,
                                              customer,
                                              testbed,
                                              test_run,
                                              target_folders,
                                              grafana_dashboard,
                                              grafana_token,
                                              grafana_host,
                                              grafana_port)


def main():
    parser = argparse.ArgumentParser(
        prog='ghost_profile.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''Manage Ghost Website''',
        description='''
        ghost_profile.py
        ----------------
        Command example:
        ./ghost_profile.py
            --ghost_token'''
    )
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--ghost_token', default=None)
    optional.add_argument('--create_post', default=None)
    optional.add_argument('--article_text_file', default=None)

    optional.add_argument('--ghost_port', help='Ghost port if different from 2368', default=2368)
    optional.add_argument('--ghost_host', help='Ghost host if different from localhost', default='localhost')
    optional.add_argument('--article_text')
    optional.add_argument('--article_tags', action='append')
    optional.add_argument('--authors', action='append')
    optional.add_argument('--title', default=None)
    optional.add_argument('--image', default=None)
    optional.add_argument('--folder', default=None)
    optional.add_argument('--custom_post', default=None)
    optional.add_argument('--wifi_capacity', default=None)
    optional.add_argument('--folders', action='append', default=None)
    optional.add_argument('--server_pull')
    optional.add_argument('--port', default=22)
    optional.add_argument('--user_pull', default='lanforge')
    optional.add_argument('--password_pull', default='lanforge')
    optional.add_argument('--user_push')
    optional.add_argument('--password_push')
    optional.add_argument('--customer')
    optional.add_argument('--testbed')
    optional.add_argument('--test_run', default=None)
    optional.add_argument('--grafana_dashboard')
    optional.add_argument('--grafana_token', default=None)
    optional.add_argument('--grafana_host', default=None)
    optional.add_argument('--grafana_port', default=3000)
    optional.add_argument('--debug')
    args = parser.parse_args()

    Ghost = UseGhost(_ghost_token=args.ghost_token,
                     _ghost_port=args.ghost_port,
                     _ghost_host=args.ghost_host,
                     _debug_on=args.debug)

    if args.create_post is not None:
        Ghost.create_post(args.title, args.article_text, args.article_tags, args.authors)
    if args.article_text_file is not None:
        Ghost.create_post_from_file(args.title, args.article_text_file, args.article_tags, args.authors)

    if args.image is not None:
        Ghost.upload_image(args.image)

    if args.custom_post is not None:
        if args.folders is not None:
            Ghost.custom_post(args.folders, args.authors)
        else:
            Ghost.custom_post(args.folder, args.authors)
    else:
        if args.folder is not None:
            Ghost.upload_images(args.folder)

    if args.wifi_capacity is not None:
        Ghost.wifi_capacity(args.authors,
                            args.folders,
                            args.title,
                            args.server_pull,
                            args.ghost_host,
                            args.port,
                            args.user_pull,
                            args.password_pull,
                            args.user_push,
                            args.password_push,
                            args.customer,
                            args.testbed,
                            args.test_run,
                            args.grafana_dashboard,
                            args.grafana_token,
                            args.grafana_host,
                            args.grafana_port)


if __name__ == "__main__":
    main()
