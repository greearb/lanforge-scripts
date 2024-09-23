#!/usr/bin/env python3
"""
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
import os
import importlib
import argparse
import logging
from time import sleep

logger = logging.getLogger(__name__)
if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

class CreateBridge(Realm):
    def __init__(self,
                 mgr: str,
                 mgr_port: int,
                 bridge_eid: str,
                 bridge_ports: str,
                 debug: bool = False,
                 exit_on_error: bool = False,
                 **kwargs):
        super().__init__(lfclient_host=mgr,
                         lfclient_port=mgr_port,
                         debug_=debug,
                         _exit_on_error=exit_on_error)

        self.bridge_eid = bridge_eid
        self.bridge_ports = bridge_ports

        eid = self.name_to_eid(self.bridge_eid)
        self.shelf = eid[0]
        self.resource = eid[1]
        self.bridge_name = eid[2]

    def build(self):
        """Create bridge port as specified."""
        logger.info(f"Creating bridge port \'{self.bridge_eid}\'")

        nd = False
        for td in self.bridge_ports.split(","):
            eid = self.name_to_eid(td)
            if not nd:
                nd = eid[2]
            else:
                nd += ","
                nd += eid[2]

        data = {
            "shelf": self.shelf,
            "resource": self.resource,
            "port": self.bridge_name,
            "network_devs": nd # eth1,eth2
        }
        self.json_post("cli-json/add_br", data)

        bridge_set_port = {
            "shelf": self.shelf,
            "resource": self.resource,
            "port": self.bridge_name,
            "current_flags": 0x80000000,
            # (0x2 + 0x4000 + 0x800000)  # current, dhcp, down
            "interest": 0x4000
        }
        self.json_post("cli-json/set_port", bridge_set_port)

        # Verify bridge port created
        ret = LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                                port_list=[self.bridge_eid],
                                                debug_=self.debug)
        if not ret:
            logger.error(f"Failed to create bridge port \'{self.bridge_eid}\'")
            exit(1)

        logger.info(f"Successfully created bridge port \'{self.bridge_eid}\'")

    def cleanup(self):
        """Remove specified bridge port."""
        logger.info("Removing any created or conflicting bridge port(s)")

        self.rm_port(self.bridge_eid, check_exists=False, debug_=self.debug)

        if LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,
                                              port_list=[self.bridge_eid],
                                              debug=self.debug):
            self._pass("Ports successfully cleaned up.")
        else:
            self._fail("Ports NOT successfully cleaned up.")


def parse_args():
    parser = LFCliBase.create_basic_argparse(
        prog='create_bridge.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
         Create bridges
            ''',

        description='''''')

    parser.add_argument('--bridge_name',
                        dest='bridge_eid',
                        required=True,
                        help='Name of the bridge port to create. This can be either the name only '
                             'or the full EID. If not the full EID, the desired resource will be '
                             'inferred from specified child ports')
    parser.add_argument('--bridge_ports', '--target_device',
                        dest='bridge_ports',
                        required=True,
                        help='Ports to bridge together. If not specified, in the \'--bridge_name\' '
                             'argument, the resource ID will be inferred from the bridged ports. '
                             'Note that all bridged ports and bridge port itself must exist on '
                             'the same resource.')

    return parser.parse_args()


def main():
    help_summary = "This script will create a single LANforge bridge port "\
                   "using the specified bridge port interfaces."

    args = parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    create_bridge = CreateBridge(**vars(args))
    create_bridge.build()

    if not args.no_cleanup:
        sleep(5)
        create_bridge.cleanup()


if __name__ == "__main__":
    main()