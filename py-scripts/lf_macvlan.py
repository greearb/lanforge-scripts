#!/usr/bin/env python3
"""
NAME: lf_macvlan.py

PURPOSE: create and operate macvlan ports using the lanforge_api.

EXAMPLES:
=========
    Creating two macvlan ports with static IPs:
    -------------------------------------------
$ ./lf_macvlan.py --new_macvlan --qty 2 --parent_port 1.1.eth2 --ip DHCP --state up

$ ./lf_macvlan.py --new_macvlan --qty 2 --parent_port 1.1.eth2 --ip 192.168.1.9/24,gw=192.168.1.1 --state down

$ ./lf_macvlan.py --new_macvlan --qty 2 --mac_pattern 'xx:xx:xx:*:*:xx' --ip DHCP --state up

$ ./lf_macvlan.py --set_state down --port 1.1.eth2#0 --port 1.1.eth2#1

$ ./lf_macvlan.py --set_state up --port 1.1.eth2#0 --port 1.1.eth2#1

$ ./lf_macvlan.py --rm_macvlan --port 1.1.eth2#0 --port 1.1.eth2#1

$ ./lf_macvlan.py --set_ip --port 1.1.eth2#0,DHCP --port 1.1.eth2#1,ip=192.168.1.9/24,gw=192.168.1.1

$ ./lf_macvlan.py --list --parent_port 1.1.eth2

STATUS: in development

NOTES:
======


LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: True

TO DO NOTES:

"""
import logging
import os
import sys
import time

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
#import ipaddress

sys.path.insert(1, "../")
# lanforge_client = importlib.import_module("lanforge_client")
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

NA: str = "NA"
DHCP: str = "DHCP"
NO_GATEWAY = "0.0.0.0"

class macvlan:
    ADD_MVLAN_FLAGS: dict = {
        "up": NA,
        "down": 1
    }
    DEFAULT_MAC_PATTERN: str = "xx:xx:xx:*:*:xx"

    def __init__(self,
                 session: LFSession = None,
                 parent_port: str = None,
                 num_ports: int = None,
                 mac_pattern: str = None,
                 ip_addr: str = None,
                 debug: bool = False,
                 state: str = None):
        self.session: LFSession = session
        self.lfcommand: LFJsonCommand = session.get_command()
        self.lfquery: LFJsonQuery = session.get_query()

        self.SetPortCurrentFlags: LFJsonCommand.SetPortCurrentFlags = self.lfcommand.SetPortCurrentFlags
        self.SetPortInterest: LFJsonCommand.SetPortInterest = self.lfcommand.SetPortInterest

        self.parent_port: str = parent_port
        self.num_ports: int = num_ports
        self.mac_pattern: str = mac_pattern
        self.ip_addr: str = ip_addr
        self.state: str = state
        self.errors_warnings = []
        self.debug = debug
        self.port_columns = ["port",
                             "parent+dev",
                             "alias",
                             "phantom",
                             "down",
                             "ip",
                             "port+type"]

    def new_macvlan(self,
                    parent_port: str = None,
                    qty: int = None,
                    mac_pattern: str = None,
                    debug: bool = False):
        debug = self.debug or debug
        print(f"would create new macvlan debug:{debug}")
        if not parent_port:
            parent_port = self.parent_port
        if not qty:
            qty = self.num_ports
        if not mac_pattern:
            mac_pattern = self.mac_pattern
        if not mac_pattern:
            mac_pattern = self.DEFAULT_MAC_PATTERN
        state = self.state
        if not state:
            state = "up"
        if not qty:
            raise ValueError("new_macvlan: no quantity provided")
        if not parent_port:
            raise ValueError("new_macvlan: no parent port provided")

        port_hunks: list = parent_port.split(".")
        if len(port_hunks) < 3:
            raise ValueError(f"new_macvlan: parent_port has insufficient decimals:{parent_port}")

        print("Finding existing macvlans on parent port...")
        existing_mvlans: list = self.list_ports(parent_port=parent_port)
        maximum_vlan_num: int = 0
        if existing_mvlans is None:
            logging.warning("* * existing vlans is None")
        elif len(existing_mvlans) < 1:
            logging.warning("* * existing vlans is empty")
        else:
            logging.debug(["matching-vlans:", pprint.pformat(existing_mvlans)])
            substr_start: int = len(parent_port) + 1
            for item in existing_mvlans:
                item_key = list(item.keys())[0]
                # print(f"ITEM KEY:{item_key}")
                if item_key == parent_port:
                    continue
                trailing_num: int = int(item_key[substr_start:])
                if trailing_num > maximum_vlan_num:
                    maximum_vlan_num = trailing_num
            print(f"MAX VLAN NUM: {maximum_vlan_num}")

        port_cmd_flags: str = NA
        port_current_flags: int = 0

        if state is "down":
            port_current_flags |= self.SetPortCurrentFlags.if_down

        if self.ip_addr == DHCP:
            port_current_flags |= self.SetPortCurrentFlags.use_dhcp
        else:
            raise ValueError("DHCP NOT SUPPORTED")

        port_interest_flags: int = self.SetPortInterest.dhcp \
                                   | self.SetPortInterest.dhcpv6 \
                                   | self.SetPortInterest.ifdown
        if port_current_flags > 0:
            port_interest_flags |= self.SetPortInterest.current_flags

        ip_str = NA
        if self.ip_addr == DHCP:
            ip_str = DHCP
        elif "." in self.ip_addr:
            ip_str = self.ip_addr
        else:
            raise ValueError(f"hard to determine value for ip:{self.ip_addr}")

        parent_port_hunks: list = parent_port.split(".")
        netmask = 24
        if '/' in ip_str:
            slashix = ip_str.find('/')
            netmask = int(ip_str[slashix+1:])
            ip_str[0:slashix-1]
            pprint.pprint(["ip_str", ip_str, "slashix", slashix, "netmask", netmask])
        gateway = NO_GATEWAY
        if ip_str == DHCP:
            gateway = NA
        for portnum in range(maximum_vlan_num, maximum_vlan_num + int(qty)):
            self.lfcommand.post_add_mvlan(flags=self.ADD_MVLAN_FLAGS[state],
                                          # ignore index, kernel assigns this usually
                                          mac=mac_pattern,
                                          port=port_hunks[2],
                                          resource=port_hunks[1],
                                          shelf=port_hunks[0],
                                          debug=debug,
                                          errors_warnings=self.errors_warnings,
                                          suppress_related_commands=True)
            self.lfcommand.post_set_port(shelf=1,
                                         resource=port_hunks[1],
                                         port=f"{parent_port_hunks[2]}#{portnum}",
                                         ip_addr=ip_str,
                                         netmask=netmask,
                                         gateway=gateway,
                                         cmd_flags=NA,
                                         current_flags=int(port_current_flags),
                                         current_flags_msk=int(port_current_flags),
                                         mac=mac_pattern,
                                         interest=int(port_interest_flags),
                                         dns_servers=NA,
                                         debug=True)
            raise ValueError("UNFINISHED")

    def list_ports(self,
                   eid_list: list = None,
                   parent_port: str = None):
        if not eid_list:
            eid_list = ["list"]
        if not parent_port:
            if self.parent_port:
                parent_port = self.parent_port
        if not parent_port:
            response = self.lfquery.get_port(eid_list=eid_list,
                                             requested_col_names=self.port_columns,
                                             errors_warnings=self.errors_warnings,
                                             debug=self.debug)
        else:
            hunks = parent_port.split('.')
            resource = f"{hunks[0]}.{hunks[1]}"
            resource_list = f"{hunks[0]}.{hunks[1]}.list"
            response: list = self.lfquery.get_port(eid_list=[resource_list],
                                                   requested_col_names=self.port_columns,
                                                   errors_warnings=self.errors_warnings,
                                                   debug=self.debug)
            filtered_response: list = []
            for entry in response:
                # print(f"KEYS:{list(entry.keys())[0]}")
                eid: str = list(entry.keys())[0]
                if eid.startswith(parent_port):
                    # pprint.pprint(entry)
                    filtered_response.append(entry)
            response = filtered_response
        if not response:
            logging.error("no response")
        return response


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
#   M A I N
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    help_summary = """Utility script for creating MAC vlans and setting them up and down.
    Can create multiple mac vlans.
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating raw command')
    parser.add_argument("--help_summary", action='store_true',
                        help="print out help summary")
    parser.add_argument("--host", "--mgr",
                        default='127.0.0.1',
                        help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--parent_port",
                        help='parent port to base macvlans from')
    parser.add_argument("--new_macvlan",
                        action='store_true',
                        help="create a new macvlan on a parent port")
    parser.add_argument("--mac_pattern",
                        help="MAC address pattern, such as xx:xx:xx:*:*:xx where xx = keep parent, * = random")
    parser.add_argument("--qty",
                        help="number of macvlans to create")
    parser.add_argument("--ip",
                        help="specify the first IP address with 'ip=<CIDR>,gw=<gateway>' or 'DHCP'")
    parser.add_argument("--state",
                        help="specify if the port is admin 'up' or admin 'down'")
    parser.add_argument("--set_state",
                        action='store_true',
                        help="Do not create a macvlan but change the state. Specify if the port is admin 'up' or admin 'down'")
    parser.add_argument("--port",
                        help="specify the EID of the port to change or remove (1.1.eth2#1)")
    parser.add_argument("--rm_macvlan",
                        action='store_true',
                        help="remove macvlans using --port <EID> arguments")
    parser.add_argument("--set_ip",
                        action='store_true',
                        help="Just set IP for a port with --port <EID>,DHCP or --port <EID>,ip=<CIDR>,gw=<IP> ")
    parser.add_argument("--list",
                        action='store_true',
                        help="prints a list of ports, or child ports from --parent_port <EID>")
    parser.add_argument("--debug",
                        action='store_true',
                        help="turn on debug output")
    parser.add_argument("--log_level",
                        help="specify logging level")
    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    if not (args.new_macvlan or args.set_state or args.rm_macvlan or args.set_ip or args.list):
        print("Please choose one action: --list, --new_macvlan, --set_state, --rm_macvlan, or --set_ip")
        exit(1)

    lfsession: LFSession = LFSession(lfclient_url=f"http://{args.host}:8080",
                                     debug=args.debug,
                                     stream_warnings=True,
                                     exit_on_error=True)

    logger = logging.getLogger(__name__)
    if args.log_level:
        logger.setLevel(args.log_level)

    my_macvlan: macvlan = macvlan(session=lfsession,
                                  parent_port=args.parent_port,
                                  num_ports=args.qty,
                                  mac_pattern=args.mac_pattern,
                                  ip_addr=args.ip,
                                  state=args.state)
    if args.new_macvlan:
        print("creating new macvlan")
        my_macvlan.new_macvlan(parent_port=args.parent_port,
                               qty=args.qty,
                               mac_pattern=args.mac_pattern,
                               debug=args.debug)
    elif args.set_state:
        print("setting state on ports")
    elif args.rm_macvlan:
        print("removing macvlan or port")
    elif args.set_ip:
        print("setting IP on port")
    elif args.list:
        print("List of ports:")
        list_of_ports: list = []
        if args.parent_port:
            list_of_ports = my_macvlan.list_ports(parent_port=args.parent_port)
        else:
            list_of_ports = my_macvlan.list_ports()
        pprint.pprint(list_of_ports)
    else:
        print("* * Unable to determine action, bye.")
        exit(1)


if __name__ == "__main__":
    main()
