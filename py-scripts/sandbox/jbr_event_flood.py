#!/usr/bin/env python3
# flake8: noqa
import os
import sys
import time
"""
    This script is a simple event creation loop intended to stress the event insertion logic of the GUI.
    To parallelize this script, use GNU Parallel: 
    
    for i in `seq 100 150`; do touch /tmp/a_$i ; done
    parallel ./jbr_event_flood.py --mgr localhost --msg {} ::: /tmp/a_*
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
    This is really just a simple loop

    :return: void
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating wanlink')
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--msg", help="add a message")

    args = parser.parse_args()

    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    command: LFJsonCommand
    command = session.get_command()
    e_w : list= []
    for index in range(0, 30000):
        msg="dflt"
        if args.msg:
            msg=args.msg
        detail_str : str = "[%s] up at %d" % (msg, lanforge_api._now_ms())
        result = command.post_add_event(name="1.1.2",
                                        priority=command.SetEventPriorityPriority.INFO.value,
                                        debug=args.debug,
                                        errors_warnings=e_w,
                                        details=detail_str)

if __name__ == "__main__":
    main()
