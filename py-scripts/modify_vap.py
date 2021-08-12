#!/usr/bin/env python3

"""
    Script for modifying VAPs.
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
import realm
from realm import Realm
import time
import pprint


class ModifyVAP(Realm):
    def __init__(self,
                 _ssid="NA",
                 _security="NA",
                 _password="NA",
                 _mac="NA",
                 _host=None,
                 _port=None,
                 _vap_list=None,
                 _enable_flags=None,
                 _disable_flags=None,
                 _number_template="00000",
                 _radio=None,
                 _proxy_str=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _dhcp=True):
        super().__init__(_host,
                         _port)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.security = _security
        self.password = _password
        self.mac = _mac
        self.vap_list = _vap_list
        self.enable_flags = _enable_flags
        self.disable_flags = _disable_flags
        self.radio = _radio
        self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.dhcp = _dhcp
        self.vap_profile = self.new_vap_profile()
        self.vap_profile.vap_name = self.vap_list
        self.vap_profile.ssid = self.ssid
        self.vap_profile.security = self.security
        self.vap_profile.ssid_pass = self.password
        self.vap_profile.mac = self.mac
        self.vap_profile.dhcp = self.dhcp
        self.vap_profile.debug = self.debug
        self.vap_profile.desired_add_vap_flags = self.enable_flags
        self.vap_profile.desired_add_vap_flags_mask = self.enable_flags + self.disable_flags

    def set_vap(self):
        return self.vap_profile.modify(resource=1,
                                       radio=self.radio)


def main():
    parser = LFCliBase.create_basic_argparse(
        prog='modify_vap.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Modify VAPs on a system. Use the enable_flag to create a flag on a VAP. Turn off a flag with \
         the disable_flag option. A list of available flags are available in the add_vap.py file in \
         py-json/LANforge.
            ''',

        description='''\
        modify_vap.py
        --------------------
        Command example:
        ./modify_vap.py
            --radio wiphy0
            --vap 1.1.vap0000
            --security open
            --ssid netgear
            --passwd BLANK
            --enable_flag osen_enable
            --disable_flag ht160_enable
            --debug
                    ''')

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--enable_flag', help='VAP flags to add', default=list(), action='append')
    optional.add_argument('--disable_flag', help='VAP flags to disable', default=list(), action='append')
    optional.add_argument('--vap', help='VAP to modify', required=True)
    optional.add_argument('--mac', default="NA")

    args = parser.parse_args()

    modify_vap = ModifyVAP(_host=args.mgr,
                           _port=args.mgr_port,
                           _ssid=args.ssid,
                           _password=args.passwd,
                           _security=args.security,
                           _mac=args.mac,
                           _vap_list=args.vap,
                           _enable_flags=args.enable_flag,
                           _disable_flags=args.disable_flag,
                           _radio=args.radio,
                           _proxy_str=args.proxy,
                           _debug_on=args.debug)
    modify_vap.set_vap()


if __name__ == "__main__":
    main()
