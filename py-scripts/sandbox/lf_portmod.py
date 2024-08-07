#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_portmod.py

PURPOSE: manipulate ports in a manner similar to lf_portmod.py, using the lanforge_api.

EXAMPLES:
=========

Examples:
./lf_portmod.py --manager 192.168.1.101 --resource 1 --list_ports
./lf_portmod.py --mgr 192.168.1.101 --resource 1 --port_name eth2 --show_port
./lf_portmod.py -m 192.168.1.101 -r 1 --port_name sta1 --show_port AP,ESSID,bps_rx,bps_tx
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name sta1 --stats_from_file /tmp/ports.txt --show_port AP,ESSID,bps_rx,bps_tx
./lf_portmod.py -m 192.168.1.101 --scan 1.1.wlan0
./lf_portmod.py - 192.168.1.101 --resource 1 --port_name eth2 --cmd reset
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name eth2 --set_ifstate down
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name eth2 --ip DHCP
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name eth2 --ip 10.1.1.1 --netmask 255.255.0.0 --gw 10.1.1.254
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name sta0 --wifi_mode 2 --set_speed "1 Mbps /b" \\
                --ssid fast-ap --passwd "secret passwd" --ap DEFAULT
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name wiphy0 --set_channel "36" --set_nss 2
./lf_portmod.py --load my_db
./lf_portmod.py -m 192.168.100.138 --cmd reset --port_name 2 --amt_resets 5 --max_port_name 8 --resource 1 --min_sleep 10 --max_sleep 20
./lf_portmod.py -m 192.168.1.101 --resource 1 --port_name sta11 --cmd set_wifi_extra --eap_identity 'adams' --eap_passwd 'family'

# Set wlan0 to /a/b/g mode, 1Mbps encoding rate
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 4 --set_speed "1 Mbps /b"

# Set wlan0 to /a/b/g mode, default encoding rates
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 4 --set_speed "DEFAULT"

# Set wlan0 to /a/b/g/n mode, default encoding rates for 1 antenna stations (1x1)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 5 --set_speed "1 Stream  /n"

# Set wlan0 to /a/b/g/n mode, default encoding rates for 2 antenna stations (2x2)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 5 --set_speed "2 Streams /n"

# Set wlan0 to /a/b/g/n mode, default encoding rates for 3 antenna stations (3x3)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 5 --set_speed "DEFAULT"

# Set wlan0 to /a/b/g/n/AC mode, default encoding rates for 1 antenna stations (1x1)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 8 --set_speed "v-1 Stream  /AC"

# Set wlan0 to /a/b/g/n/AC mode, default encoding rates for 2 antenna stations (2x2)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 8 --set_speed "v-2 Streams /AC"

# Set wlan0 to /a/b/g/n/AC mode, default encoding rates for 3 antenna stations (3x3)
./lf_portmod.py --manager localhost --resource 1 --port_name wlan0 --wifi_mode 8 --set_speed "DEFAULT"
STATUS: in development

NOTES:
======


LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: True

TO DO NOTES:

"""
import ipaddress
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
import urllib

# import ipaddress

sys.path.insert(1, "../")
# lanforge_client = importlib.import_module("lanforge_client")
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

NA: str = "NA"
DHCP: str = "DHCP"
NO_GATEWAY = "0.0.0.0"
MAC_VLAN = "MAC-VLAN"
logger = logging.getLogger(__name__)


class portmod:
    def __init__(self,
                 session: LFSession = None,
                 debug: bool = False,
                 state: str = None):
        self.session: LFSession = session
        if not session.logger:
            session.logger = logging
        self.lfcommand: LFJsonCommand = session.get_command()
        self.lfquery: LFJsonQuery = session.get_query()
        self.errors_warnings: list = []
        self.response_list: list = []
        self.debug = debug
        self.port_columns: list = ["port",
                                   "parent+dev",
                                   "alias",
                                   "phantom",
                                   "down",
                                   "ip",
                                   "port+type"]
        self.all_port_columns: list = []
        tmp_all_cols: list = [
            "4way time (us)",
            "activity",
            "alias",
            "anqp time (us)",
            "ap",
            "avg chain rssi",
            "beacon",
            "bps rx ll",
            "bps rx",
            "bps tx ll",
            "bps tx",
            "bytes rx ll",
            "bytes tx ll",
            "chain rssi",
            "channel",
            "collisions",
            "connections",
            "crypt",
            "cx ago",
            "cx time (us)",
            "device",
            "dhcp (ms)",
            "down",
            "entity id",
            "gateway ip",
            "hardware",
            "ip",
            "ipv6 address",
            "ipv6 gateway",
            "key/phrase",
            "login-fail",
            "login-ok",
            "logout-fail",
            "logout-ok",
            "mac",
            "mask",
            "misc",
            "mode",
            "mtu",
            "no cx (us)",
            "noise",
            "parent dev",
            "phantom",
            "port type",
            "port",
            "pps rx",
            "pps tx",
            "qlen",
            "reset",
            "retry failed",
            "rx bytes",
            "rx crc",
            "rx drop",
            "rx errors",
            "rx fifo",
            "rx frame",
            "rx length",
            "rx miss",
            "rx over",
            "rx pkts",
            "rx-rate",
            "sec",
            "signal",
            "ssid",
            "status",
            "time-stamp",
            "tx abort",
            "tx bytes",
            "tx crr",
            "tx errors",
            "tx fifo",
            "tx hb",
            "tx pkts",
            "tx wind",
            "tx-failed %",
            "tx-rate",
            "wifi retries"
        ]
        self.all_port_columns = list(map(urllib.parse.quote_plus, tmp_all_cols))
        # pprint.pprint(["result of map:", self.all_port_columns])


    def list_ports(self,
                   eid_list: list = None,
                   filter: str = None,
                   columns: list = None,
                   debug: bool = False):
        debug |= self.debug
        if not eid_list:
            eid_list = ["list"]
        #pprint.pprint(["list_ports columns", columns])
        response = self.lfquery.get_port(eid_list=eid_list,
                                         requested_col_names=columns,
                                         errors_warnings=self.errors_warnings,
                                         debug=self.debug)
        if not response:
            logger.error(f"* * unable to get a port list:")
            pprint.pprint(self.errors_warnings)
        if filter:
            filtered_list: list = []
            for port_entry in response:
                port_eid = list(port_entry.keys())[0]
                if port_eid.startswith(filter):
                    filtered_list.append(port_entry)
                else:
                    logger.debug(f"filtering out {port_eid}")
            response = filtered_list
        return response

    def modify_station(self):
        pass

    def modify_radio(self):
        pass

    def modify_port(self):
        pass


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
    parser.add_argument("--host", "--mgr", "-m",
                        default='127.0.0.1',
                        help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--list",
                        action='store_true',
                        help="prints a list of ports or ports matching --filter")
    parser.add_argument("--columns", "--cols",
                        nargs="+",
                        help="list of port columns to display, or ALL")
    parser.add_argument("--filter",
                        help="EID prefix to filter ports: --filter 1.2.sta\n"
                             "This is a startswith() match check on port EID")
    parser.add_argument("--port_name", "--port",
                        help='port to query in EID format (1.1.wlan0)')
    parser.add_argument("--set_state", "--set_ifstate", "--state",
                        help="Change the state: 'up' or 'down'")
    # parser.add_argument("--set_speed", "--speed",
    #                    help="MOAR HELP")
    parser.add_argument("--set_channel", "--channel", "--ch",
                        help="set channel on radio, requires --port_name to be a radio")
    parser.add_argument("--set_nss", "--num_spatial_streams",
                        help="Set number of spatial streams on radio, requires --port_name to be radio")
    parser.add_argument("--set_ssid", "--ssid",
                        help="set station SSID")
    parser.add_argument("--set_bssid", "--bssid",
                        help="set station's target BSSID, requires APs BSSID ")
    parser.add_argument("--set_eap_identity", "--eap_identity", "--eap_id",
                        help="set station WPA enterprise id")
    parser.add_argument("--set_eap_password", "--set_eap_passwd", "--eap_passwd",
                        help="set eap password")
    parser.add_argument("--set_ip", "--ip",
                        help="Set IP for a port/station with --port_name <EID> --set_ip DHCP"
                             " or --port <EID> --ip <CIDR> ")
    parser.add_argument("--set_netmask", "--netmask",
                        help="set port netmask, --port_name <EID> --set_ip <IP> --set_netmask <MASK> --set_gatway <IP>")
    parser.add_argument("--set_gateway", "--set_gw", "--gw",
                        help="set port gateway: --port_name <EID> --set_ip <IP> --set_gateway <IP>")
    parser.add_argument("--set_wifi_mode", "--wifi_mode", "--mode",
                        help="set station wifi mode")
    parser.add_argument("--debug",
                        action='store_true',
                        help="turn on debug output")
    parser.add_argument("--log_level",
                        help="specify logging level")
    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    if not (args.list
            or args.port_name
            or args.filter
            or args.set_bssid
            or args.set_channel
            or args.set_eap_identity
            or args.set_eap_password
            or args.set_gateway
            or args.set_ip
            or args.set_netmask
            or args.set_speed
            or args.set_ssid
            or args.set_state
            or args.set_wifi_mode):
        print("""Please choose one action: 
    --list
    --filter
    --port
    --set_bssid
    --set_channel
    --set_eap_identity
    --set_eap_password
    --set_gateway
    --set_ip
    --set_netmask
    --set_speed
    --set_ssid
    --set_state
    --set_wifi_mode
        """)
        exit(1)

    lfclient_url = f"http://{args.host}:8080"
    lfsession: LFSession = LFSession(lfclient_url=lfclient_url,
                                     debug=args.debug,
                                     stream_warnings=True,
                                     exit_on_error=True)
    if args.log_level:
        logger.setLevel(args.log_level)

    my_portmod: portmod = portmod(session=lfsession,
                                  debug=args.debug)
    response: dict = {}
    if args.list:
        col_list: list = my_portmod.port_columns
        if args.columns:
            if isinstance(args.columns, str):
                pprint.pprint(["args.columns", args.columns])
                if str(args.columns).find(',') > 0:
                    col_list = str(args.columns).split(",")
                elif str(args.columns) == "all":
                    col_list = my_portmod.all_port_columns
            elif isinstance(args.columns, list):
                if args.columns[0] == "all":
                    col_list = my_portmod.all_port_columns
                else:
                    col_list = args.columns
        if args.filter:
            response = my_portmod.list_ports(filter=args.filter,
                                             columns=col_list)
        elif args.port_name:
            response = my_portmod.list_ports(filter=args.port_name,
                                             columns=col_list)
        else:
            response = my_portmod.list_ports(columns=col_list)
        pprint.pprint(response)
        exit(0)

    if not args.port_name:
        logger.error("Missing --port_name, cannot continue")
        exit(1)

    my_portmod.set_port(eid=args.port_name)

    if args.set_bssid:
        my_portmod.set_bssid(bssid=args.set_bssid)
    if args.set_channel:
        my_portmod.set_channel(channel=args.set_channel)
    if args.set_eap_identity:
        if not args.set_eap_password:
            raise ValueError("--set_eap_identity requires --set_eap_password")
        my_portmod.set_eap_identity(eap_id=args.set_eap_identity,
                                    eap_passwd=args.set_eap_passwd)
    if args.set_gateway:
        my_portmod.set_gateway(gateway=args.set_gateway)
    if args.set_ip:
        my_portmod.set_ip(ip=args.set_ip)
    if args.set_netmask:
        my_portmod.set_netmask(netmask=args.set_netmask)
    if args.set_speed:
        raise ValueError("set_speed not yet implemented")
    if args.set_ssid:
        my_portmod.set_ssid(ssid=args.set_ssid)
    if args.set_state:
        my_portmod.set_state(state=args.set_state)
    if args.set_wifi_mode:
        my_portmod.set_wifi_mode(mode=args.set_wifi_mode)

    my_portmod.commit(debug=args.debug)


if __name__ == "__main__":
    main()
