#!/usr/bin/env python3

"""
    Script for creating a variable number of VAPs.
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
import time
import pprint


class CreateVAP(LFCliBase):
    def __init__(self,
                 _ssid=None,
                 _security=None,
                 _password=None,
                 _host=None,
                 _port=None,
                 _vap_list=None,
                 _number_template="00000",
                 _radio="wiphy0",
                 _proxy_str=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(_host,
                         _port,
                         _proxy_str=_proxy_str,
                         _local_realm=realm.Realm(lfclient_host=_host,
                                                  lfclient_port=_port,
                                                  halt_on_error_=_exit_on_error,
                                                  _exit_on_error=_exit_on_error,
                                                  _exit_on_fail=_exit_on_fail,
                                                  _proxy_str=_proxy_str,
                                                  debug_=_debug_on),
                         _debug=_debug_on,
                         _halt_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail)
        self.host = _host
        self.port = _port
        self.ssid = _ssid
        self.security = _security
        self.password = _password
        self.vap_list = _vap_list
        self.radio = _radio
        self.timeout = 120
        self.number_template = _number_template
        self.debug = _debug_on
        self.vap_profile = self.local_realm.new_vap_profile()
        self.vap_profile.vap_name = self.vap_list
        if self.debug:
            print("----- VAP List ----- ----- ----- ----- ----- ----- \n")
            pprint.pprint(self.sta_list)
            print("---- ~VAP List ----- ----- ----- ----- ----- ----- \n")


    def build(self):
        # Build VAPs

        print("Creating VAPs")
        self.vap_profile.create(resource=1,
                                radio=self.radio,
                                channel=36,
                                up_=True,
                                debug=False,
                                suppress_related_commands_=True,
                                use_radius=True,
                                hs20_enable=False)
        self._pass("PASS: VAP build finished")




def main():
    parser = LFCliBase.create_basic_argparse(
        prog='create_vap.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Create VAPs
            ''',

        description='''\
        create_vap.py
--------------------
Command example:
./create_vap.py
    --upstream_port eth1
    --radio wiphy0
    --num_vaps 3
    --security open
    --ssid netgear
    --passwd BLANK
    --debug
            ''')
    required = parser.add_argument_group('required arguments')
    #required.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', required=True)

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--num_vaps', help='Number of VAPs to Create', required=False)
    args = parser.parse_args()
    #if args.debug:
    #    pprint.pprint(args)
    #    time.sleep(5)
    if (args.radio is None):
       raise ValueError("--radio required")

    num_vap = 2
    if (args.num_vaps is not None) and (int(args.num_vaps) > 0):
        num_vaps_converted = int(args.num_vaps)
        num_vap = num_vaps_converted

    vap_list = LFUtils.port_name_series(prefix="vap",
                           start_id=0,
                           end_id=num_vap-1,
                           padding_number=10000,
                           radio=args.radio)

    create_vap = CreateVAP(_host=args.mgr,
                       _port=args.mgr_port,
                       _ssid=args.ssid,
                       _password=args.passwd,
                       _security=args.security,
                       _vap_list=vap_list,
                       _radio=args.radio,
                       _proxy_str=args.proxy,
                       _debug_on=args.debug)

    create_vap.build()

if __name__ == "__main__":
    main()
