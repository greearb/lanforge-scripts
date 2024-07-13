#!/usr/bin/env python3
"""
NAME:       create_qvlan.py

PURPOSE:    Create one ore more QVLAN port on the specified parent port.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The selected IPv4 configuration method will be applied to all created QVLAN ports
            created by this script.

EXAMPLE:
            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. No IPv4 configuration specified.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10

            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 \
                    --dhcpv4

            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. Static IPv4 configuration.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 \
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

            # Four QVLANs with QVLAN IDs 10, 20, 30, and 40 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 20 30 40 \
                    --dhcpv4

            # Two QVLANs with QVLAN IDs 10 and 20 on parent port '1.1.eth3'. Static IPv4 configuration
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 20 \
                    --ipv4_address  172.16.0.10 172.10.0.20 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1
"""
import sys
import os
import importlib
import argparse
import logging

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


class CreateQVlan(Realm):
    def __init__(self,
                 mgr: str,
                 mgr_port: int,
                 parent_port: str,
                 qvlan_ids: list,
                 dhcpv4: bool,
                 ipv4_addresses: list,
                 ipv4_netmasks: list,
                 ipv4_gateways: list,
                 exit_on_error: bool = False,
                 debug: bool = False,
                 **kwargs):
        super().__init__(lfclient_host=mgr,
                         lfclient_port=mgr_port)

        self.host = mgr
        self.port = mgr_port

        self.qvlan_profiles = []
        for ix, qvlan_id in enumerate(qvlan_ids):
            # Defaults to one QVLAN port created per profile
            # This script assumes the same parent port for all created QVLAN ports
            qvlan_profile = self.new_qvlan_profile()
            self.qvlan_profiles.append(qvlan_profile)

            qvlan_profile.qvlan_parent = parent_port
            qvlan_profile.desired_qvlans = [qvlan_id]  # Workaround for QVLAN profile quirk

            if dhcpv4:
                qvlan_profile.dhcp = True
            elif ipv4_addresses:
                qvlan_profile.dhcp = False
                qvlan_profile.first_ip_addr = ipv4_addresses[ix]

                # Either apply same subnet mask to all or one specified for each
                if len(ipv4_netmasks) == 1:
                    qvlan_profile.netmask = ipv4_netmasks[0]
                else:
                    qvlan_profile.netmask = ipv4_netmasks[ix]

                # Either apply same gateway to all or on especified for each
                if len(ipv4_gateways) == 1:
                    qvlan_profile.gateway = ipv4_gateways[0]
                else:
                    qvlan_profile.gateway = ipv4_gateways[ix]

    def build(self):
        logger.info("Creating QVLAN port(s)")
        for qvlan_profile in self.qvlan_profiles:
            ret = qvlan_profile.create(debug=self.debug, sleep_time=0)

            if not ret:
                logger.error(
                    f"Failed to create QVLAN port with QVLAN ID: {qvlan_profile.desired_qvlans}")
                exit(1)

        logger.info("Successfully created QVLAN port(s)")


def parse_args():
    parser = LFCliBase.create_bare_argparse(
        prog='create_qvlan.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
NAME:       create_qvlan.py

PURPOSE:    Create one ore more QVLAN port on the specified parent port.

            This script will optionally set IPv4 configuration (static or dynamic), if specified.
            The selected IPv4 configuration method will be applied to all created QVLAN ports
            created by this script.

EXAMPLE:
            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. No IPv4 configuration specified.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10

            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 \
                    --dhcpv4

            # Single QVLAN with QVLAN ID 10 on parent port '1.1.eth3'. Static IPv4 configuration.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 \
                    --ipv4_address  172.16.0.10 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1

            # Four QVLANs with QVLAN IDs 10, 20, 30, and 40 on parent port '1.1.eth3'. DHCPv4 enabled.
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 20 30 40 \
                    --dhcpv4

            # Two QVLANs with QVLAN IDs 10 and 20 on parent port '1.1.eth3'. Static IPv4 configuration
                ./create_qvlan.py \
                    --parent        1.1.eth3 \
                    --qvlan_ids     10 20 \
                    --ipv4_address  172.16.0.10 172.10.0.20 \
                    --ipv4_netmask  255.255.255.0 \
                    --ipv4_gateway  172.16.0.1
""")
    # Required arguments
    parser.add_argument('--parent', '--parent_port', '--qvlan_parent',
                        dest='parent_port',
                        help='Parent port used by created QVLAN port(s)',
                        default=None,
                        required=True)
    parser.add_argument('--qvlan_ids',
                        dest='qvlan_ids',
                        nargs='+',
                        help='QVLAN ID(s) used in creation. '
                             'One QVLAN port is created per ID. For static IP configuration, '
                             'the number of IDs specified in this argument must match the number '
                             'of static IP addresses specified in the \'--ipv4_addresses\'.',
                        default=None,
                        required=True)

    # Optional IPv4 configuration
    #
    # Limit users to only one of static or DHCP IPv4 configuration.
    # Allow users to specify no L3 configuration.
    #
    # If static IPv4 configuration, argument validation must check that
    # number of static IPv4 addresses matches either number of ports or
    # number of specified QVLAN IDs
    ipv4_cfg = parser.add_mutually_exclusive_group(required=False)
    ipv4_cfg.add_argument('--dhcp', '--dhcpv4', '--use_dhcp',
                          dest='dhcpv4',
                          help='Enable DHCPv4 on created QVLAN ports',
                          action='store_true')
    ipv4_cfg.add_argument('--ip', '--ips', '--ipv4_address', '--ipv4_addresses',
                          dest='ipv4_addresses',
                          type=str,
                          nargs='+',
                          help='List of static IPv4 addresses. The number of IPv4 addresses '
                               'specified must match the number of QVLAN ports specified in '
                               '\'--num_ports\'',
                          default=None)

    # Only checked when static configuration specified
    parser.add_argument('--netmask', '--netmasks', '--ipv4_netmask', '--ipv4_netmasks',
                        dest='ipv4_netmasks',
                        type=str,
                        nargs='+',
                        help='IPv4 subnet mask to apply to all created QVLAN ports '
                             'when static IPv4 configuration requested',
                        default=None)
    parser.add_argument('--gateway', '--gateways', '--ipv4_gateway', '--ipv4_gateways',
                        dest='ipv4_gateways',
                        type=str,
                        nargs='+',
                        help='IPv4 gateway to apply to all created QVLAN ports '
                             'when static IPv4 configuration requested',
                        default=None)

    return parser.parse_args()


def validate_args(args):
    # User either specifies DHCPv4, static IPv4 configuration, or no IPv4 configuration
    if args.ipv4_addresses:
        num_addresses = len(args.ipv4_addresses)

        # If multiple static IPv4 addresses specified, then must match number
        # of QVLAN IDs specified
        if args.qvlan_ids and num_addresses != len(args.qvlan_ids):
            logger.error("Number of static IPv4 addresses does not match \'--qvlan_ids\'")
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
            # QVLANProfile code if so
            logger.error("No IPv4 gateway specified")
            exit(1)
        elif len(args.ipv4_gateways) != 1 and num_addresses != len(args.ipv4_gateways):
            logger.error("Number of IPv4 gateways does not match number of IPv4 addresses.")
            exit(1)


def main():
    args = parse_args()

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    validate_args(args)

    create_qvlan = CreateQVlan(**vars(args))
    create_qvlan.build()


if __name__ == "__main__":
    main()
