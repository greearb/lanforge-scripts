#!/usr/bin/env python3

"""
NAME: ghost_profile.py
PURPOSE: modify ghost database from the command line.
SETUP: A Ghost installation which the user has admin access to.
EXAMPLE: ./ghost_profile.py --article_text_file text.txt --title Test --authors Matthew --ghost_token SECRET_KEY --host 192.168.1.1

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
from LANforge.lfcli_base import LFCliBase

class UseGhost(LFCliBase):
    def __init__(self,
                 _ghost_token=None,
                 host="localhost",
                 port=8080,
                 _debug_on=False,
                 _exit_on_fail=False,
                 _ghost_host="localhost",
                 _ghost_port=2368, ):
        super().__init__(host, port, _debug=_debug_on, _exit_on_fail=_exit_on_fail)
        self.ghost_host = _ghost_host
        self.ghost_port = _ghost_port
        self.ghost_token = _ghost_token
        self.GP = GhostRequest(self.ghost_host, str(self.ghost_port), _api_token=self.ghost_token)

    def create_post(self, title, text, tags, authors):
        return self.GP.create_post(title=title, text=text, tags=tags, authors=authors)

    def create_post_from_file(self, title, file, tags, authors):
        text = open(file).read()
        return self.GP.create_post(title=title, text=text, tags=tags, authors=authors)


def main():
    parser = LFCliBase.create_basic_argparse(
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
    args = parser.parse_args()

    Ghost = UseGhost(_ghost_token=args.ghost_token,
                     _ghost_port=args.ghost_port,
                     _ghost_host=args.ghost_host)

    if args.create_post is not None:
        Ghost.create_post(args.title, args.article_text, args.article_tags, args.authors)
    if args.article_text_file is not None:
        Ghost.create_post_from_file(args.title, args.article_text_file, args.article_tags, args.authors)


if __name__ == "__main__":
    main()
