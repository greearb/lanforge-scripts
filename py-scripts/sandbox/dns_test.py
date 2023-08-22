#!/usr/bin/env python3
"""
NAME: dns_test.py

PURPOSE: create a collection of generic endpoints that create random hostnames to query.

EXAMPLE:
$ ./dns_test.py --host ct521a-jana --type 'hot take' --name 'spicy jab' --text stuff .....

NOTES:


TO DO NOTES:

"""
import os
import sys
import time

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
from pprint import pprint

sys.path.insert(1, "../../")

if "SHELL" in os.environ.keys():
    realm = importlib.import_module("py-json.realm")
    lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
    from lanforge_client.lanforge_api import LFSession
    from lanforge_client.lanforge_api import LFJsonCommand
    from lanforge_client.lanforge_api import LFJsonQuery
else:
    realm = importlib.import_module("py-json.realm")
    import lanforge_api
    from lanforge_api import LFJsonCommand
    from lanforge_api import LFJsonQuery

Realm = realm.Realm


class DnsTest(Realm):
    def __init__(self,
                 host: str = "localhost",
                 port: int = 8080,
                 lfapi_session: lanforge_api.LFSession = None,
                 debug: bool = False,
                 port_pattern: str = None,
                 duration_min: int = None,
                 args: argparse = None, ):
        """
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 debug_=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _proxy_str=None,
                 _capture_signal_list=[]
        :param host:
        :param port:
        :param lfapi_session:
        :param debug:
        :param port_pattern:
        :param duration_min:
        :param args:
        """
        super().__init__(lfclient_host=host,
                         lfclient_port=port,
                         debug_=debug,
                         _exit_on_error=True,
                         _exit_on_fail=False)
        self.lfapi: LFSession = lfapi_session
        self.debug = debug;
        # determine port objects
        self.port_patterns: list[str] = []
        self.eid_list: list = []

        if (isinstance(port_pattern, list)):
            self.port_patterns.append(port_pattern)
        elif (isinstance(port_pattern, str)):
            if (port_pattern.find(",") > 0):  # patterns beginning with "," are nonsense
                self.port_patterns.append(port_pattern.split(","))
            else:
                self.port_patterns.append(port_pattern)
        else:
            raise ValueError("no port pattern specified")

        # collect a list of ports
        self.command = self.lfapi.get_command()
        self.query = self.lfapi.get_query()

    # ~DnsTest::init
    def start(self):
        port_list: list[str] = []
        all_ports: list = self.query.get_port(eid_list="list",
                                              requested_col_names="port,alias",
                                              debug=self.debug)
        if not all_ports:
            self.lfapi.logger.error("No port list retrieved.")
            raise ValueError("No port list retrieved")

        for record in all_ports:
            if not record:
                continue
            #print(f"Inspecting record[{record}]")
            for pat in self.port_patterns:
                #pprint(["pat:", pat, ", record:", record])
                key = list(record.keys())[0]
                if record[key]['alias'].find(pat) > -1:
                    #print(f"pat[{pat}] ^= alias[{record[key]['alias']}]")
                    self.eid_list.append(key)

        print(f"Matching eids: {', '.join(self.eid_list)}")

    def stop(self):
        pass


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
#   M A I N
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests dns robustness with random hostnames')
    parser.add_argument("--host", "--mgr",
                        help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--port_pattern",
                        help='comma-separated prefix of ports to use for generic connections')
    parser.add_argument("--duration_min",
                        help='text-blob body')
    parser.add_argument("--debug",
                        help='turn on debugging', action="store_true")

    args = parser.parse_args()
    host_url = args.host
    if not ((args.host.rfind(":") > 6) or (args.host.find("http") == 0)):
        host_url = f"http://{args.host}:8080"
    session = lanforge_api.LFSession(lfclient_url=host_url,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    # command: LFJsonCommand
    # command = session.get_command()
    # query: LFJsonQuery
    # query = session.get_query()

    dnstest = DnsTest(host=args.host,
                      debug=args.debug,
                      lfapi_session=session,
                      port_pattern=args.port_pattern)

    dnstest.start();

    dnstest.stop();


if __name__ == "__main__":
    main()

#
