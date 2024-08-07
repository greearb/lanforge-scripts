#!/usr/bin/env python3
# flake8: noqa
import os
import sys
import time
"""
   This script is intended to exercise cx groups: create, start, stop, delete
"""
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
sys.path.insert(1, "../../")

if "SHELL" in os.environ.keys():
    lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
    from lanforge_client.lanforge_api import LFSession
    from lanforge_client.lanforge_api import LFJsonCommand
    from lanforge_client.lanforge_api import LFJsonQuery
else:
    import lanforge_api
    from lanforge_api import LFJsonCommand
    from lanforge_api import LFJsonQuery


def main():
    """
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--host", "--mgr", help='specify the GUI to connect to, assumes port 8080', default='127.0.0.1')
    parser.add_argument("--debug", help='turn on debugging',
                        action="store_true")
    parser.add_argument(
        "--a_side_eid", help="left side port", default="1.1.wlan0")
    parser.add_argument(
        "--b_side_eid", help="right side port", default="1.1.eth1")
    parser.add_argument("--num_cx", help="number of connections", default=10)
    parser.add_argument("--group", help="group name", default="testing-group")

    args = parser.parse_args()
    left_eid: list = args.a_side_eid.split('.')
    right_eid: list = args.b_side_eid.split('.')

    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    command: LFJsonCommand
    command = session.get_command()
    query: LFJsonQuery
    query = session.get_query()

    result = query.get_test_group(eid_list=["list"], debug=True)
    pprint.pprint(result)
    if (result):
        command.post_rm_group(name=args.group, suppress_related_commands=True)

    e_w: list = []
    for index in range(0, int(args.num_cx)):
        result = command.post_add_endp(alias="tcp_%d-A" % index,
                                       shelf=1,
                                       resource=left_eid[1],
                                       port=left_eid[2],
                                       p_type='lf_tcp',
                                       min_rate='9600',
                                       multi_conn=1,
                                       payload_pattern='increasing',
                                       ip_port=-1)

        result = command.post_add_endp(alias="tcp_%d-B" % index,
                                       shelf=1,
                                       resource=right_eid[1],
                                       port=right_eid[2],
                                       p_type='lf_tcp',
                                       min_rate='9600',
                                       multi_conn=1,
                                       payload_pattern='increasing',
                                       ip_port=-1)
    for index in range(0, int(args.num_cx)):
        time.sleep(1)
        print(".", end='')
        result = command.post_set_endp_flag(name="tcp_%d-A" % index,
                                            flag="AutoHelper",
                                            val=1)
        result = command.post_set_endp_flag(name="tcp_%d-B" % index,
                                            flag="AutoHelper",
                                            val=1)

    for index in range(0, int(args.num_cx)):
        result = command.post_add_cx(alias="tcp_%d" % index,
                                     test_mgr='default_tm',
                                     tx_endp="tcp_%d-A" % index,
                                     rx_endp="tcp_%d-B" % index)
    command.post_add_group(name=args.group)

    for index in range(0, int(args.num_cx)):
        result = command.post_add_tgcx(tgname=args.group, 
                                       cxname="tcp_%d" % index)
    command.post_show_group(group='all', suppress_related_commands=True)
    time.sleep(1)
    result = query.get_test_group(eid_list=["list"], debug=True)

    pprint.pprint(("groups:", result))
    print("starting group...")
    command.post_start_group(name=args.group, suppress_related_commands=True)
    for index in range(0, 10 + int(args.num_cx)):
        time.sleep(1)
        print(".", end='')
    print("stopping group")
    command.post_quiesce_group(name=args.group, suppress_related_commands=True)
    time.sleep(3)
    response = query.get_test_group(eid_list=[args.group], debug=True)
    print("removing group")
    for cx in response:
        command.post_rm_tgcx(tgname=args.group, 
                             cxname=cx,
                             suppress_related_commands=True)
    command.post_rm_group(name=args.group,
                          suppress_related_commands=True)


if __name__ == "__main__":
    main()
