#!/usr/bin/env python3
# flake8: noqa
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
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

if "SHELL" in os.environ.keys():
    # pyjson = importlib.import_module("..py-json")
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
                 duration_sec: int = None,
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
        :param duration_sec:
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
            #print("extending port_patterns")
            self.port_patterns.extend(port_pattern)
        elif (isinstance(port_pattern, str)):
            if (port_pattern.find(",") > 0):  # patterns beginning with "," are nonsense
                #print("using split")
                self.port_patterns.extend(port_pattern.split(","))
            else:
                #print(f"appending {port_pattern}")
                self.port_patterns.append(port_pattern)
        else:
            raise ValueError("no port pattern specified")
        #pprint(["self.port_patterns:", self.port_patterns])

        # collect a list of ports
        self.command = self.lfapi.get_command()
        self.query = self.lfapi.get_query()
        self.port_to_cxaliases: dict = {}
        self.test_duration_sec = args.duration_sec
        self.generic_script = args.generic_script

    # ~DnsTest::init

    def create_generics(self, eid_list: list = None):
        if not eid_list:
            raise ValueError("create_generics needs entries in eid_list")
        seen_eids: list = []
        api_command = self.lfapi.get_command()
        cmd_i: int = 0

        e_w: list[str] = []
        responsez: list = []
        for eidstr in eid_list:
            if not eidstr:
                #print(f"eidstr[{eidstr}]")
                #pprint(["eidstrs:", eid_list])
                raise ValueError("create_generic will not parse empty eidstr values")

            eid = self.name_to_eid(eidstr)
            if eid in seen_eids:
                # call the create_generics method twice to create two connections per port
                print(f"create_generics: eid seen before[{eid}], not creating twice")
                continue
            seen_eids.append(eid)
            alias: str = f"dns{cmd_i:03d}"
            api_command.post_add_gen_endp(alias=alias,
                                          shelf=eid[0],
                                          resource=eid[1],
                                          port=eid[2],
                                          p_type="gen_generic",
                                          response_json_list=responsez,
                                          debug=self.debug,
                                          errors_warnings=e_w,
                                          suppress_related_commands=True)
            cmd_i += 1
            self.port_to_cxaliases[eidstr] = alias
        #time.sleep(1)

        # we want to run a command that runs for a duration, not a single call
        # cmd: str = f"./vrf_exec.bash %s /usr/bin/dig %s host %s | grep 'Query time:'"
        cmd: str = f"./vrf_exec.bash %s {self.generic_script} %s nameserver=192.168.92.1 duration={self.test_duration_sec}"
        responsez = []
        #pprint(["cxaliases:", self.port_to_cxaliases])
        for (eidstr, alias) in self.port_to_cxaliases.items():
            eid = self.name_to_eid(eidstr)
            #pprint(["eidstr:", eidstr, "eid", eid])
            formatted_cmd = cmd % (eid[2], eid[2])
            print(f"formatted command: {formatted_cmd}")
            api_command.post_set_gen_cmd(name=alias,
                                         command=formatted_cmd,
                                         response_json_list=responsez,
                                         errors_warnings=e_w,
                                         suppress_related_commands=True,
                                         debug=self.debug)

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
            for pat in self.port_patterns:
                #pprint(["pat:", pat, self.port_patterns, "record:",record])
                #time.sleep(2)
                key = list(record.keys())[0]
                #pprint(["pat:", pat, "key:", key, " record:", record, " alias:", record[key]['alias']])
                if key == pat:
                    #print(f"adding key {key}")
                    self.eid_list.append(key)
                    continue
                if not record[key]['alias']:
                    continue
                p_alias = record[key]['alias']
                # pprint(["key:", key, "p_alias:", p_alias, "pat:", pat, "patterns:", self.port_patterns])
                if str(p_alias).find(pat) >= 0:
                    #print(f"adding key {key}")
                    self.eid_list.append(key)


        pprint(["self.eid_list:", self.eid_list])
        print(f"Matching eids: " + str(self.eid_list))

        # GenCXProfile is not useful for ad-hoc commands. Ad hoc commands are
        # better expressed thru the lanforge_api structure
        # generics : Realm.GenCXProfile = Realm.new_generic_endp_profile()
        self.create_generics(eid_list=self.eid_list)

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
                        default="localhost",
                        help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--port_pattern",
                        required=True,
                        help='comma-separated prefix of ports or port prefixes to use for generic connections')
    parser.add_argument("--duration_sec", "--duration",
                        required=True,
                        help='text-blob body')
    parser.add_argument("--generic_script", "--script",
                        required=True,
                        help="script to invoke on the station which starts DNS queries")
    parser.add_argument("--debug",
                        help='turn on debugging',
                        action="store_true")

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
    pprint(["args.port_pattern:", args.port_pattern])
    dnstest = DnsTest(host=args.host,
                      debug=args.debug,
                      lfapi_session=session,
                      port_pattern=args.port_pattern,
                      args=args)

    dnstest.start();

    dnstest.stop();


if __name__ == "__main__":
    main()

#
