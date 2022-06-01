#!/usr/bin/env python3
"""
NAME: lf_modify_radio.py

PURPOSE: modify a radio

EXAMPLE:
$ ./lf_modify_radio.py --host 192.168.100.205 --radio "1.1.wiphy0" --antenna 7 --debug

To enable using lf_json_autogen in other parts of the codebase, set LF_USE_AUTOGEN=1:
$ LF_USE_AUTOGEN=1 ./jbr_jag_test.py --test set_port --host ct521a-lion

NOTES:


TO DO NOTES:

"""
import os
import sys
import importlib
import argparse
import pprint

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating wanlink')
    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--radio", help='name of the radio to modify: e.g. 1.1.wiphy0')
    parser.add_argument("--antenna", help='number of spatial streams: e.g. 7 for 3x3')

    args = parser.parse_args()
    if not args.radio:
        print("No radio name provided")
        exit(1)

    session = LFSession(lfclient_url="http://%s:8080" % args.host,
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

    resource = LFUtils.name_to_eid(args.radio)[0]
    shelf = LFUtils.name_to_eid(args.radio)[1]
    radio = LFUtils.name_to_eid(args.radio)[2]
    print(F'resource: {resource}, shelf: {shelf}, radio: {radio}')
    
    command.post_set_wifi_radio(resource=resource,
                                radio=radio,
                                shelf=shelf,
                                antenna=args.antenna,
                                debug=args.debug)

if __name__ == "__main__":
    main()
#
