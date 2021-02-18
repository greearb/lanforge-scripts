#!/usr/bin/env python3

"""
    Script for creating a variable number of bridges.
"""

import sys
import os
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
import LANforge
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
from realm import Realm
import time
import pprint


class RemoveEndp(Realm):
    def __init__(self,
                 endp_name,
                 _host=1,
                 _debug_on=False):
        super().__init__(_host)
        self.endp_name = endp_name
        self.debug = _debug_on
        if self.debug:
            print("----- Endpoint List ----- ----- ----- ----- ----- ----- \n")
            pprint.pprint(self.endp_name)
            print("---- ~Endpoint List ----- ----- ----- ----- ----- ----- \n")


    def build(self):
        # Build bridges

        data = {
            "endp_name": self.endp_name
        }
        self.json_post("cli-json/rm_endp", data)




def main():
    parser = LFCliBase.create_basic_argparse(
        prog='create_bridge.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Create bridges
            ''',

        description='''\
        create_bridge.py
--------------------
Command example:
./remove_endp.py
    --endp_name br0
            ''')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--endp_name', help='Name of the endpoint you want to remove', required=True)
    args = parser.parse_args()

    if (args.endp_name is None):
       raise ValueError("--endp_name required")

    remove_endp = RemoveEndp(endp_name=args.endp_name,
                       _debug_on=args.debug)

    remove_endp.build()

if __name__ == "__main__":
    main()
