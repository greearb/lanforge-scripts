#!/usr/bin/env python3
"""
NAME:       create_macvlan.py

PURPOSE:    Create and configure one or more MACVLAN ports using the specified parent port.

NOTES:      MACVLAN ports can only be created with a Ethernet, Bond, Redir, or 802.1Q VLAN port
            as the parent port.

            MACVLAN ports are different than 802.1Q VLAN ports.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The selected IPv4 configuration method will be applied to all ports created by this script.

EXAMPLE:    # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. No IPv4 configuration specified.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10

            # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 \
                    --dhcpv4

            # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. Static IPv4 configuration.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 \
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

            # Four MACVLANs with MACVLAN IDs 10, 20, 30, and 40 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 20 30 40 \
                    --dhcpv4

            # Two MACVLANs with MACVLAN IDs 10 and 20 on parent port '1.1.eth3'. Static IPv4 configuration
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 20 \
                    --ipv4_address  172.16.0.10 172.10.0.20 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

SCRIPT_CLASSIFICATION:
            Creation

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            09-JUN-2023,
            GUI Version:  5.4.6
            Kernel Version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.

INCLUDE_IN_README:
            False
"""

import sys
import os
import importlib
import argparse
import logging
import time

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
add_file_endp = importlib.import_module("py-json.LANforge.add_file_endp")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class CreateMacVlan(Realm):
    def __init__(self,
                 mgr: str,
                 mgr_port: int,
                 parent_port: str,
                 macvlan_ids: list,
                 dhcpv4: bool,
                 ipv4_addresses: list,
                 ipv4_netmasks: list,
                 ipv4_gateways: list,
                 exit_on_error: bool = False,
                 debug: bool = False,
                 **kwargs):
        super().__init__(mgr, mgr_port, debug_=debug, _exit_on_error=exit_on_error)

        self.host = mgr
        self.port = mgr_port

        self.macvlan_profiles = []
        for ix, macvlan_id in enumerate(macvlan_ids):
            # Defaults to one MACVLAN port created per profile
            # This script assumes the same parent port for all created MACVLAN ports
            macvlan_profile = self.new_mvlan_profile()
            self.macvlan_profiles.append(macvlan_profile)

            # Workaround for MACVLAN profile quirks
            shelf, resource, parent, _ = self.name_to_eid(parent_port)
            macvlan_profile.shelf = shelf
            macvlan_profile.resource = resource
            macvlan_profile.macvlan_parent = parent
            macvlan_profile.desired_macvlans = ["#" + macvlan_id]

            if dhcpv4:
                macvlan_profile.dhcp = True
            elif ipv4_addresses:
                macvlan_profile.dhcp = False
                macvlan_profile.first_ip_addr = ipv4_addresses[ix]

                # Either apply same subnet mask to all or one specified for each
                if len(ipv4_netmasks) == 1:
                    macvlan_profile.netmask = ipv4_netmasks[0]
                else:
                    macvlan_profile.netmask = ipv4_netmasks[ix]

                # Either apply same gateway to all or on especified for each
                if len(ipv4_gateways) == 1:
                    macvlan_profile.gateway = ipv4_gateways[0]
                else:
                    macvlan_profile.gateway = ipv4_gateways[ix]

    def cleanup(self):
        logger.info("Cleaning up any created or conflicting MACVLAN ports")
        for macvlan_profile in self.macvlan_profiles:
            macvlan_profile.cleanup()

    def build(self):
        logger.info("Creating MACVLAN port(s)")
        for macvlan_profile in self.macvlan_profiles:
            ret = macvlan_profile.create(debug=self.debug, sleep_time=0)

            if not ret:
                logger.error(
                    f"Failed to create MACVLAN port with MACVLAN ID: {macvlan_profile.desired_macvlans}")
                exit(1)

        logger.info("Successfully created MACVLAN port(s)")


def parse_args():
    parser = LFCliBase.create_bare_argparse(
        prog='create_macvlan.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Creates MACVLAN endpoints.''',

        description='''\
NAME:       create_macvlan.py

PURPOSE:    Create and configure one or more MACVLAN ports using the specified parent port.

NOTES:      MACVLAN ports can only be created with a Ethernet, Bond, Redir, or 802.1Q VLAN port
            as the parent port.

            MACVLAN ports are different than 802.1Q VLAN ports.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The selected IPv4 configuration method will be applied to all ports created by this script.

EXAMPLE:    # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. No IPv4 configuration specified.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10

            # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 \
                    --dhcpv4

            # Single MACVLAN with MACVLAN ID 10 on parent port '1.1.eth3'. Static IPv4 configuration.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 \
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

            # Four MACVLANs with MACVLAN IDs 10, 20, 30, and 40 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 20 30 40 \
                    --dhcpv4

            # Two MACVLANs with MACVLAN IDs 10 and 20 on parent port '1.1.eth3'. Static IPv4 configuration
                ./create_macvlan.py \
                    --parent        1.1.eth3 \
                    --macvlan_ids   10 20 \
                    --ipv4_address  172.16.0.10 172.10.0.20 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

SCRIPT_CLASSIFICATION:
            Creation

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            09-JUN-2023,
            GUI Version:  5.4.6
            Kernel Version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.

INCLUDE_IN_README:
            False
''')
    # Required arguments
    parser.add_argument('--parent', '--parent_port', '--macvlan_parent',
                        dest='parent_port',
                        help='Parent port used by created MACVLAN port(s)',
                        default=None,
                        required=True)
    parser.add_argument('--macvlan_ids',
                        dest='macvlan_ids',
                        nargs='+',
                        help='MACVLAN ID(s) used in creation. '
                             'One MACVLAN port is created per ID. For static IP configuration, '
                             'the number of IDs specified in this argument must match the number '
                             'of static IP addresses specified in the \'--ipv4_addresses\'.',
                        default=None,
                        required=True)

    # Optional arguments
    parser.add_argument('--cleanup',
                        help='Clean up any created ports before exiting.',
                        action='store_true')

    # Optional IPv4 configuration
    #
    # Limit users to only one of static or DHCP IPv4 configuration.
    # Allow users to specify no L3 configuration.
    #
    # If static IPv4 configuration, argument validation must check that
    # number of static IPv4 addresses matches either number of ports or
    # number of specified MACVLAN IDs
    ipv4_cfg = parser.add_mutually_exclusive_group(required=False)
    ipv4_cfg.add_argument('--dhcp', '--dhcpv4', '--use_dhcp',
                          dest='dhcpv4',
                          help='Enable DHCPv4 on created ports',
                          action='store_true')
    ipv4_cfg.add_argument('--ip', '--ips', '--ipv4_address', '--ipv4_addresses',
                          dest='ipv4_addresses',
                          type=str,
                          nargs='+',
                          help='List of static IPv4 addresses. The number of IPv4 addresses '
                               'specified must match the number of ports specified in '
                               '\'--num_ports\'',
                          default=None)

    # Only checked when static configuration specified
    parser.add_argument('--netmask', '--netmasks', '--ipv4_netmask', '--ipv4_netmasks',
                        dest='ipv4_netmasks',
                        type=str,
                        nargs='+',
                        help='IPv4 subnet mask to apply to all created MACVLAN ports '
                             'when static IPv4 configuration requested',
                        default=None)
    parser.add_argument('--gateway', '--gateways', '--ipv4_gateway', '--ipv4_gateways',
                        dest='ipv4_gateways',
                        type=str,
                        nargs='+',
                        help='IPv4 gateway to apply to all created MACVLAN ports '
                             'when static IPv4 configuration requested',
                        default=None)

    return parser.parse_args()


def validate_args(args):
    # User either specifies DHCPv4, static IPv4 configuration, or no IPv4 configuration
    #
    # If user specified static configuration, ensure that number of specified ports
    # to create matches number of static IPv4 configurations specified
    if args.ipv4_addresses:
        num_addresses = len(args.ipv4_addresses)

        # If multiple static IPv4 addresses specified, then must match number
        # of MACVLAN IDs specified
        if args.macvlan_ids and num_addresses != len(args.macvlan_ids):
            logger.error("Number of static IPv4 addresses does not match \'--macvlan_ids\'")
            exit(1)

        # IPv4 subnet mask required if static IPv4 configuration specified
        # If more than one subnet mask specified, must match number of IPv4 addresses
        # If only one, then apply that to all created ports
        if not args.ipv4_netmasks:
            logger.error("No IPv4 subnet mask specified")
            exit(1)
        elif len(args.ipv4_netmasks) != 1 and num_addresses != len(args.ipv4_netmasks):
            logger.error("Number of IPv4 subnet masks does not match number of IPv4 addresses.")
            exit(1)

        # IPv4 gateway required if static IPv4 configuration specified
        # If more than one gateway specified, must match number of IPv4 addresses
        # If only one, then apply that to all created ports
        if not args.ipv4_gateways:
            # TODO: Should we make this a warn and continue? Will need to fix
            # MACVLANProfile code if so
            logger.error("No IPv4 gateway specified")
            exit(1)
        elif len(args.ipv4_gateways) != 1 and num_addresses != len(args.ipv4_gateways):
            logger.error("Number of IPv4 gateways does not match number of IPv4 addresses.")
            exit(1)


def main():
    args = parse_args()

    help_summary = "This script will create and configure one or more MACVLAN ports " \
                   "using the specified single parent port. Note that MACVLAN ports " \
                   "are different than 802.1Q VLAN ports."
    if args.help_summary:
        print(help_summary)
        exit(0)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    validate_args(args)

    ip_test = CreateMacVlan(**vars(args))
    ip_test.build()

    if args.cleanup:
        time.sleep(5)
        ip_test.cleanup()


if __name__ == "__main__":
    main()
