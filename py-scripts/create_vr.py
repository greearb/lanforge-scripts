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

class CreateVR(Realm):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 debug=False,
                 # resource=1, # USE name=1.2.vr0 convention instead
                 vr_names=None,
                 ports_list=[],
                 services_list=[],
                 _halt_on_error=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _proxy_str=None,
                 _capture_signal_list=[]):
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug,
                         halt_on_error_=_halt_on_error,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)
        self.vr_names = vr_names
        self.ports_list = ports_list
        self.services_list = services_list
        self.vr_profile = self.new_vr_profile()
        self.vr_profile.resource=self.resource


    def build(self):
        self.vr_profile.create(resource=self.resource,
                               vr_id=self.vr_id,
                               upstream_port="up0",
                               upstream_subnets="10.0.0.0/24",
                               upstream_nexthop="10.0.0.1",
                               local_nexthop="10.1.0.1",
                               local_subnets="10.1.0.0/24",
                               debug=self.debug)


def main():
    parser = LFCliBase.create_bare_argparse(
        prog=__file__,
        description="""\
%s
--------------------
Command example:
%s --vr_name 1.vr0 --ports 1.br0,1.rdd0a --services 1.br0=dhcp,nat --services 1.vr0=radvd
%s --vr_name 2.vr0 --ports 2.br0,2.vap2 --services 
    
    --debug
""")
    required = parser.add_argument_group('required arguments')
    required.add_argument('--vr_name', '--vr_names', help='ID of virtual router', default="1.1.vr0", required=False)

    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--resource', help='Resource number to create virtual router on', default=1, required=False)
    optional.add_argument('--ports', help='Comma separated list of ports to add to virtual router', default=None, required=False)
    optional.add_argument('--services', help='Add router services to a port, "br0=nat,dhcp"', default=None, required=False)

    args = parser.parse_args()


    create_vr = CreateVR(lfclient_host=args.mgr,
                         lfclient_port=args.mgr_port,
                         vr_names=args.vr_names,
                         ports_list=args.ports,
                         services_list=args.services,
                         debug=args.debug,
                         _halt_on_error=True,
                         _exit_on_error=True,
                         _exit_on_fail=True)

    create_vr.build()

if __name__ == "__main__":
    main()

#