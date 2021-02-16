#!/usr/bin/env python3

"""
    Script for creating a variable number of bridges.
"""

import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
from LANforge.lfcli_base import LFCliBase
from realm import Realm
import time

class CreateVR(Realm):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 debug=False,
                 # resource=1, # USE name=1.2.vr0 convention instead
                 vr_name=None,
                 ports_list=(),
                 services_list=(),
                 _halt_on_error=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _proxy_str=None,
                 _capture_signal_list=()):
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)

        eid_name = self.name_to_eid(vr_name)
        self.vr_name = eid_name
        self.ports_list = ports_list
        self.services_list = services_list
        self.vr_profile = self.new_vr_profile()

    def clean(self):
        if (self.vr_name is None) or (self.vr_profile.vr_eid is None) and (self.vr_profile.vr_eid) == "":
            print("No vr_eid to clean")
            return

        if (self.vr_profile.vr_eid is not None) \
            and (self.vr_profile.vr_eid[1] is not None) \
            and (self.vr_profile.vr_eid[2] is not None):
            data = {
                "shelf": 1,
                "resource": self.vr_profile.vr_eid[1],
                "router_name": self.vr_profile.vr_eid[2]
            }
            self.json_post("/cli-json/rm_vr", data, debug_=self.debug)

        if (self.vr_name is not None) \
            and (self.vr_name[1] is not None) \
            and (self.vr_name[2] is not None):
            data = {
                "shelf": 1,
                "resource": self.vr_name[1],
                "router_name": self.vr_name[2]
            }
            self.json_post("/cli-json/rm_vr", data, debug_=self.debug)
            time.sleep(1)
            self.json_post("/cli-json/nc_show_vr", {
                "shelf": 1,
                "resource": self.vr_name[1],
                "router": "all"
            }, debug_=self.debug)
            self.json_post("/cli-json/nc_show_vrcx", {
                "shelf": 1,
                "resource": self.vr_name[1],
                "cx_name": "all"
            }, debug_=self.debug)



    def build(self):
        self.vr_profile.create(
            vr_name=self.vr_name,
            # upstream_port="up0",
            # upstream_subnets="10.0.0.0/24",
            # upstream_nexthop="10.0.0.1",
            # local_nexthop="10.1.0.1",
            # local_subnets="10.1.0.0/24",
            debug=self.debug)


def main():
    parser = LFCliBase.create_bare_argparse(
        prog=__file__,
        description="""\
{f}
--------------------
Command example:
{f} --vr_name 1.vr0 --ports 1.br0,1.rdd0a --services 1.br0=dhcp,nat --services 1.vr0=radvd
{f} --vr_name 2.vr0 --ports 2.br0,2.vap2 --services 
    
    --debug
""".format(f=__file__))
    required = parser.add_argument_group('required arguments')
    required.add_argument('--vr_name', '--vr_names', default="1.1.vr0", required=False,
                          help='EID of virtual router, like 1.2.vr0')

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('--ports', default=None, required=False,
                          help='Comma separated list of ports to add to virtual router')
    optional.add_argument('--services', default=None, required=False,
                          help='Add router services to a port, "br0=nat,dhcp"')

    args = parser.parse_args()

    create_vr = CreateVR(lfclient_host=args.mgr,
                         lfclient_port=args.mgr_port,
                         vr_name=args.vr_name,
                         ports_list=args.ports,
                         services_list=args.services,
                         debug=args.debug,
                         _halt_on_error=True,
                         _exit_on_error=True,
                         _exit_on_fail=True)
    create_vr.clean()
    create_vr.build()
    # create_vr.start()
    # create_vr.monitor()
    # create_vr.stop()
    # create_vr.clean()
    print('Created Virtual Router')

if __name__ == "__main__":
    main()

#
