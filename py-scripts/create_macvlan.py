#!/usr/bin/env python3
"""
NAME: create_macvlan.py

PURPOSE:  This script will create a variable number of macvlans on a specified ethernet port.

EXAMPLE:
        # Sample CLI Formate:

            ./create_macvlan.py --mgr localhost --macvlan_parent <port> --num_ports <num ports>
            --first_mvlan_ip <first ip in series> --netmask <netmask to use> --gateway <gateway ip addr> --cleanup

        # For creating the variable number of macvlan's

            ./create_macvlan.py --mgr localhost --macvlan_parent eth2 --num_ports 3 --first_mvlan_ip 192.168.92.13
            --netmask 255.255.255.0 --gateway 192.168.92.1

        # For creating the macvlan's with user-defined port names

            ./create_macvlan.py --mgr localhost --macvlan_parent eth1 --num_ports 3 --use_ports eth1#0,eth1#1,eth1#2

        # For creating the macvlan's with first defiende port name

            ./create_macvlan.py --mgr localhost --macvlan_parent eth1 --num_ports 3 --first_port eth1#143

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:  Functional 

NOTES:
        You can only add MAC-VLANs to Ethernet, Bonding, Redir, and 802.1Q VLAN devices.

STATUS: Functional

VERIFIED_ON:   09-JUN-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

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
    def __init__(self, host, port,
                 num_ports=1,
                 macvlan_parent=None,
                 first_mvlan_ip=None,
                 netmask=None,
                 gateway=None,
                 dhcp=True,
                 port_list=None,
                 ip_list=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, debug_=_debug_on,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail)
        self.port = port
        self.port_list = []
        self.ip_list = ip_list
        self.netmask = netmask
        self.gateway = gateway
        self.dhcp = dhcp
        if macvlan_parent is not None:
            self.macvlan_parent = macvlan_parent
            self.port_list = port_list

        self.mvlan_profile = self.new_mvlan_profile()

        self.mvlan_profile.num_macvlans = int(num_ports)
        self.mvlan_profile.desired_macvlans = self.port_list
        self.mvlan_profile.macvlan_parent = self.macvlan_parent[2]
        self.mvlan_profile.shelf = self.macvlan_parent[0]
        self.mvlan_profile.resource = self.macvlan_parent[1]
        self.mvlan_profile.dhcp = dhcp
        self.mvlan_profile.netmask = netmask
        self.mvlan_profile.first_ip_addr = first_mvlan_ip
        self.mvlan_profile.gateway = gateway

        self.created_ports = []

    def cleanup(self):
        print("Cleaning up")
        self.mvlan_profile.cleanup()

    def build(self):
        # Build MACVLANs
        logger.info("Creating MACVLANs")
        if self.mvlan_profile.create(
            admin_down=False,
            sleep_time=0,
            debug=self.debug):
            self._pass("MACVLAN build finished")
            self.created_ports += self.mvlan_profile.created_macvlans
        else:
            self._fail("MACVLAN port build failed.")


def main():
    help_summary = '''\
    This script will create a variable number of macvlans on a specified ethernet port(eth1/eth2). It's important to 
    note that the script can only add MAC-VLANs to Ethernet, Bonding and 802.1Q VLAN devices. The script has the 
    feasibility to create the macvlan interfaces based on user-specified numbers.
            '''
    parser = LFCliBase.create_bare_argparse(
        prog='create_macvlan.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Creates MACVLAN endpoints.''',

        description='''\
NAME: create_macvlan.py

PURPOSE:  This script will create a variable number of macvlans on a specified ethernet port.

EXAMPLE:
        # Sample CLI Formate:

            ./create_macvlan.py --mgr localhost --macvlan_parent <port> --num_ports <num ports>
            --first_mvlan_ip <first ip in series> --netmask <netmask to use> --gateway <gateway ip addr> --cleanup

        # For creating the variable number of macvlan's

            ./create_macvlan.py --mgr localhost --macvlan_parent eth2 --num_ports 3 --first_mvlan_ip 192.168.92.13
            --netmask 255.255.255.0 --gateway 192.168.92.1

        # For creating the macvlan's with user-defined port names

            ./create_macvlan.py --mgr localhost --macvlan_parent eth1 --num_ports 3 --use_ports eth1#0,eth1#1,eth1#2

        # For creating the macvlan's with first defined port name

            ./create_macvlan.py --mgr localhost --macvlan_parent eth1 --num_ports 3 --first_port eth1#143

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:  Functional 

NOTES:
        You can only add MAC-VLANs to Ethernet, Bonding, Redir, and 802.1Q VLAN devices.

STATUS: Functional

VERIFIED_ON:   09-JUN-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

''')
    parser.add_argument(
        '--macvlan_parent',
        help='specifies parent port for macvlan creation',
        required=False)
    parser.add_argument(
        '--first_port',
        help='specifies name of first port to be used',
        default=None)
    parser.add_argument(
        '--num_ports',
        help='number of ports to create',
        default=1)
    parser.add_argument(
        '--use_ports',
        help='List of comma separated ports to use with ips, \'=\' separates name and ip'
        '{ port_name1=ip_addr1, port_name1=ip_addr2 }. \n'
        'Ports without ips will be left alone',
        default=None)
    parser.add_argument(
        '--first_mvlan_ip',
        help='specifies first static ip address to be used or dhcp',
        default=None)
    parser.add_argument(
        '--netmask',
        help='specifies netmask to be used with static ip addresses',
        default=None)
    parser.add_argument(
        '--gateway',
        help='specifies default gateway to be used with static addressing',
        default=None)
    parser.add_argument(
        '--cleanup',
        help='Cleaning Up the created MAC VLANs if we want to cleanup.',
        action='store_true')

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    args.macvlan_parent = LFUtils.name_to_eid(args.macvlan_parent)
    port_list = []
    ip_list = []
    if args.first_port is not None:
        if args.first_port.startswith("sta"):
            if (args.num_ports is not None) and (int(args.num_ports) > 0):
                start_num = int(args.first_port[3:])
                num_ports = int(args.num_ports)
                port_list = LFUtils.port_name_series(
                    prefix="sta",
                    start_id=start_num,
                    end_id=start_num + num_ports - 1,
                    padding_number=10000)
        else:
            if (args.num_ports is not None) and args.macvlan_parent is not None and (
                    int(args.num_ports) > 0) and args.macvlan_parent[2] in args.first_port:
                start_num = int(
                    args.first_port[args.first_port.index('#') + 1:])
                num_ports = int(args.num_ports)
                port_list = LFUtils.port_name_series(
                    prefix=args.macvlan_parent[2] + "#",
                    start_id=start_num,
                    end_id=start_num + num_ports - 1,
                    padding_number=100000)
            else:
                raise ValueError(
                    "Invalid values for num_ports [%s], macvlan_parent [%s], and/or first_port [%s].\n"
                    "first_port must contain parent port and num_ports must be greater than 0" %
                    (args.num_ports, args.macvlan_parent, args.first_port))
    else:
        if args.use_ports is None:
            num_ports = int(args.num_ports)
            port_list = LFUtils.port_name_series(
                prefix=args.macvlan_parent[2] + "#",
                start_id=0,
                end_id=num_ports - 1,
                padding_number=100000)
        else:
            temp_list = args.use_ports.split(',')
            for port in temp_list:
                port_list.append(port.split('=')[0])
                if '=' in port:
                    ip_list.append(port.split('=')[1])
                else:
                    ip_list.append(0)

            if len(port_list) != len(ip_list):
                raise ValueError(
                    temp_list, " ports must have matching ip addresses!")

    if args.first_mvlan_ip is not None:
        if args.first_mvlan_ip.lower() == "dhcp":
            dhcp = True
        else:
            dhcp = False
    else:
        dhcp = True

    ip_test = CreateMacVlan(args.mgr,
                            args.mgr_port,
                            port_list=port_list,
                            ip_list=ip_list,
                            _debug_on=args.debug,
                            macvlan_parent=args.macvlan_parent,
                            first_mvlan_ip=args.first_mvlan_ip,
                            netmask=args.netmask,
                            gateway=args.gateway,
                            dhcp=dhcp,
                            num_ports=args.num_ports,
                            # want a mount options param
                            )

    ip_test.build()

    if args.cleanup:
        time.sleep(5)
        ip_test.cleanup()

    # TODO:  Cleanup by default, add --no_cleanup option to not do cleanup.

    if ip_test.passes():
        logging.info('Created %s MacVlan connections' % args.num_ports)
        ip_test.exit_success()
    else:
        ip_test.exit_fail()


if __name__ == "__main__":
    main()
