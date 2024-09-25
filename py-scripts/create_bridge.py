#!/usr/bin/env python3
"""
NAME:       create_bridge.py

PURPOSE:    Create a bridge port using specified child bridge ports.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The specified IPv4 configuration will be set for the bridge port when specified.
            Child bridge port IPv4 configuration will always be cleared (TODO).

EXAMPLE:
            # Bridge with two child bridge ports. No IPv4 configuration specified.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3

            # Bridge with two child bridge ports. No IPv4 configuration specified.
            # Assumes bridge created on resource 1 (assumed from bridge child ports).
                ./create_bridge.py \
                    --bridge_name   br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3

            # Bridge with two child bridge ports created in down state. No IPv4 configuration specified.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --create_admin_down

            # Bridge with two child bridge ports created. DHCPv4 enabled.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --dhcpv4

            # Bridge with two child bridge ports created. Static IPv4 configuration.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc
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

lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFJsonCommand # noqa


class CreateBridge(Realm):
    def __init__(self,
                 mgr: str,
                 mgr_port: int,
                 bridge_eid: str,
                 bridge_ports: str,
                 dhcpv4: bool,
                 ipv4_address: list,
                 ipv4_netmask: list,
                 ipv4_gateway: list,
                 create_admin_down: bool,
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

        # No bridge profile in py-json, so do everything
        # basic configuration by hand in this script
        self.dhcpv4 = dhcpv4
        self.ipv4_address = ipv4_address
        self.ipv4_netmask = ipv4_netmask
        self.ipv4_gateway = ipv4_gateway

        self.create_admin_down = create_admin_down

    def build(self):
        """Create bridge port as specified."""
        logger.info(f"Creating bridge port \'{self.bridge_eid}\'")

        # TODO: Clear IP configuration for bridged ports
        # TODO: Validate bridged ports exist
        # TODO: Ensure bridge devices set up? Require at least one bridge device up for bridge to go up
        bridge_port_names = [LFUtils.name_to_eid(port)[2] for port in self.bridge_ports]

        # 1. Create bridge port
        #
        # The 'add_br' command doesn't support creating ports admin down,
        # so must admin them down in subsequent 'set_port' command
        data = {
            "shelf": self.shelf,
            "resource": self.resource,
            "port": self.bridge_name,
            "network_devs": ",".join(bridge_port_names)
        }
        self.json_post("cli-json/add_br", data)

        # 2. Verify bridge port created
        ret = LFUtils.wait_until_ports_appear(base_url=self.lfclient_url,
                                              port_list=[self.bridge_eid],
                                              debug=self.debug)
        if not ret:
            logger.error(f"Failed to create bridge port \'{self.bridge_eid}\'")
            exit(1)

        # 3. Configure bridge port as user specifies
        set_port_interest_flags = 0
        set_port_cur_flags = 0
        set_port_cur_flags_mask = 0

        # Admin up/down setting
        set_port_interest_flags |= LFJsonCommand.SetPortInterest.ifdown.value
        if self.create_admin_down:
            set_port_cur_flags_mask |= LFJsonCommand.SetPortCurrentFlags.if_down.value
            set_port_cur_flags |= LFJsonCommand.SetPortCurrentFlags.if_down.value

        # IPv4 configuration. Either DHCPv4, static, or none
        #
        # Always set DHCPv4 in current flags mask, as this ensures
        # DHCPv4 setting is alwasy modified whether we turn it on or not
        set_port_cur_flags_mask |= LFJsonCommand.SetPortCurrentFlags.use_dhcp.value

        if self.dhcpv4:
            set_port_cur_flags |= LFJsonCommand.SetPortCurrentFlags.use_dhcp.value
            set_port_interest_flags |= LFJsonCommand.SetPortInterest.dhcp.value
        elif self.ipv4_address:
            set_port_interest_flags |= LFJsonCommand.SetPortInterest.ip_address.value \
                | LFJsonCommand.SetPortInterest.ip_Mask.value \
                | LFJsonCommand.SetPortInterest.ip_gateway.value

        bridge_set_port = {
            "shelf": self.shelf,
            "resource": self.resource,
            "port": self.bridge_name,
            "current_flags_msk": set_port_cur_flags_mask,
            "current_flags": set_port_cur_flags,
            "interest": set_port_interest_flags,
            "ip_addr": self.ipv4_address,
            "netmask": self.ipv4_netmask,
            "gateway": self.ipv4_gateway,
        }
        self.json_post("cli-json/set_port", bridge_set_port)

        # 4. Check goes admin up, unless '--create_admin_down' specified
        if not self.create_admin_down:
            ret = LFUtils.wait_until_ports_admin_up(base_url=self.lfclient_url,
                                                    port_list=[self.bridge_eid],
                                                    debug_=self.debug)
            if not ret:
                logger.error(f"Bridge port \'{self.bridge_eid}\' did not go admin up")
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

        description='''
NAME:       create_bridge.py

PURPOSE:    Create a bridge port using specified child bridge ports.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The specified IPv4 configuration will be set for the bridge port when specified.
            Child bridge port IPv4 configuration will always be cleared (TODO).

EXAMPLE:
            # Bridge with two child bridge ports. No IPv4 configuration specified.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3

            # Bridge with two child bridge ports. No IPv4 configuration specified.
            # Assumes bridge created on resource 1 (assumed from bridge child ports).
                ./create_bridge.py \
                    --bridge_name   br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3

            # Bridge with two child bridge ports created in down state. No IPv4 configuration specified.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --create_admin_down

            # Bridge with two child bridge ports created. DHCPv4 enabled.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --dhcpv4

            # Bridge with two child bridge ports created. Static IPv4 configuration.
                ./create_bridge.py \
                    --bridge_name   1.1.br0 \
                    --bridge_ports  1.1.eth2,1.1.eth3
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc
            ''')

    parser.add_argument('--bridge_name',
                        dest='bridge_eid',
                        required=True,
                        help='Name of the bridge port to create. This can be either the name only '
                             'or the full EID. If not the full EID, the desired resource will be '
                             'inferred from specified child ports')
    parser.add_argument('--bridge_ports', '--target_device',
                        dest='bridge_ports',
                        nargs="+",
                        help='Ports to bridge together. If not specified, in the \'--bridge_name\' '
                             'argument, the resource ID will be inferred from the bridged ports. '
                             'Note that all bridged ports and bridge port itself must exist on '
                             'the same resource.')

    # Optional arguments
    parser.add_argument('--cleanup',
                        help='Clean up any created ports before exiting.',
                        action='store_true')
    parser.add_argument("--create_admin_down",
                        help='Create bridge port in admin down state. '
                             'Will not attempt to admin up bridged ports.',
                        action='store_true')

    # Optional IPv4 configuration
    #
    # Limit users to only one of static or DHCP IPv4 configuration.
    # Allow users to specify no L3 configuration.
    #
    # As this script only creates a single bridge,
    # only accept a single static IPv4 configuration for the bridge
    ipv4_cfg = parser.add_mutually_exclusive_group(required=False)
    ipv4_cfg.add_argument('--dhcp', '--dhcpv4', '--use_dhcp',
                          dest='dhcpv4',
                          help='Enable DHCPv4 on created bridge port',
                          action='store_true')
    ipv4_cfg.add_argument('--ip', '--ipv4_address',
                          dest='ipv4_address',
                          type=str,
                          help='Set static IPv4 address for the created bridge port',
                          default=None)

    # Only checked when static configuration specified
    parser.add_argument('--netmask', '--ipv4_netmask',
                        dest='ipv4_netmask',
                        type=str,
                        help='IPv4 subnet mask to apply to created bridge port '
                             'when static IPv4 configuration requested',
                        default=None)
    parser.add_argument('--gateway', '--ipv4_gateway',
                        dest='ipv4_gateway',
                        type=str,
                        help='IPv4 gateway to apply to created bridge port '
                             'when static IPv4 configuration requested',
                        default=None)

    return parser.parse_args()


def validate_args(args):
    # Ensure the bridge resource ID is specified,
    # either in the '--bridge_name' argument itself or in the
    # specified ports to bridge ('--bridge_ports' argument)
    #
    # If specified in bridge name, then assume same resource ID
    # for all bridged ports. If not specified in bridge name,
    # resource ID must be specified in bridged ports
    #
    # First check for resource ID in bridge name
    bridge_eid = LFUtils.name_to_eid(args.bridge_eid)
    resource_id = bridge_eid[1]

    # Hack to check if user did not specify full bridge EID
    # in the '--bridge_name' argument
    #
    # If don't check this, then when only name specified,
    # resource ID 1 is always assumed
    if len(args.bridge_eid.split(".")) < 2:
        resource_id = None

    # Check for/validate resource ID in bridged ports
    for bridge_port in args.bridge_ports:
        port_eid = LFUtils.name_to_eid(bridge_port)

        if resource_id is None:
            resource_id = port_eid[1]
        elif resource_id != port_eid[1]:
            logger.error("Cannot specify bridge ports on separate resources")
            exit(1)

    if args.ipv4_address:
        # IPv4 subnet mask required if static IPv4 configuration specified
        if not args.ipv4_netmasks:
            logger.error("No IPv4 subnet mask specified")
            exit(1)

        # IPv4 gateway required if static IPv4 configuration specified
        if not args.ipv4_gateways:
            # TODO: Should we make this a warn and continue?
            logger.error("No IPv4 gateway specified")
            exit(1)


def main():
    args = parse_args()

    help_summary = "This script will create a single LANforge bridge port "\
                   "using the specified bridge port interfaces."
    if args.help_summary:
        print(help_summary)
        exit(0)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    validate_args(args)

    create_bridge = CreateBridge(**vars(args))
    create_bridge.build()

    if args.cleanup:
        sleep(5)
        create_bridge.cleanup()


if __name__ == "__main__":
    main()
