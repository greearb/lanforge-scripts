#!/usr/bin/env python3
'''
NAME: jbr_jag_test.py

PURPOSE: exercises the LANforge/lf_json_autogen.py library

EXAMPLE:
./jbr_jag_test.py --host ct521a-jana --test foo

NOTES:


TO DO NOTES:

'''
import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.insert(1, "../../py-json")
import argparse
import pprint

from LANforge import lf_json_autogen
from LANforge.lf_json_autogen import LFJsonGet as LFG
from LANforge.lf_json_autogen import LFJsonPost as LFP


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests lf_json_autogen')
    parser.add_argument("--host", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--test", help='specify a test to run')

    args = parser.parse_args()
    if not args.test:
        print("No test requested")
        exit(1)

    if args.test.endswith("get_port"):
        test_get_port(args)
    if args.test.endswith("set_port"):
        test_set_port(args)


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def test_get_port(args=None):
    print("test_get_port")
    if not args:
        raise ValueError("test_get_port needs args")
    get_request = LFG(lfclient_host=args.host,
                      lfclient_port=8080,
                      debug_=True,
                      _exit_on_error=True)

    result = get_request.get_port(eid_list=["1.1.eth0", "1.1.eth1", "1.1.eth2"],
                                  requested_col_names=(),
                                  debug_=True)
    pprint.pprint(result)


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def test_set_port(args=None):
    print("test_set_port")
    if not args:
        raise ValueError("test_set_port needs args")
    post_request = lf_json_autogen.LFJsonPost(lfclient_host=args.host,
                                              lfclient_port=8080,
                                              debug_=True,
                                              _exit_on_error=True)
    my_current_flags = 0
    my_interest_flags = 0;
    try:
        my_current_flags = LFP.set_flags(LFP.SetPortCurrentFlags,
                                         0,
                                         ['if_down', 'use_dhcp'])
    except Exception as x:
            import traceback
            traceback.print_tb(x)
            print(x.__repr__())
            exit(1)
    try:
        my_current_flags = LFP.set_flags(LFP.SetPortCurrentFlags,
                                         0,
                                         [
                                             LFP.SetPortCurrentFlags.if_down,
                                             LFP.SetPortCurrentFlags.use_dhcp
                                         ])
    except Exception as x:
            import traceback
            traceback.print_tb(x)
            print(x.__repr__())
            exit(1)
    try:
        my_interest_flags = LFP.set_flags(LFP.SetPortInterest, 0, ['current_flags', 'ifdown', 'mac_address'])

        result = post_request.post_set_port(alias=None,  # A user-defined name for this interface.  Can be BLANK or NA.
                                            current_flags=my_current_flags,  # See above, or NA.
                                            current_flags_msk=my_current_flags,
                                            # This sets 'interest' for flags 'Enable RADIUS service' and higher. See above, or NA.
                                            interest=my_interest_flags,
                                            port='eth2',  # Port number for the port to be modified.
                                            report_timer=2000,
                                            resource=1,  # Resource number for the port to be modified.
                                            shelf=1,  # Shelf number for the port to be modified.
                                            debug_=True)
        my_current_flags = LFP.clear_flags(LFP.SetPortCurrentFlags,
                                   my_current_flags,
                                   flag_names=LFP.SetPortCurrentFlags.use_dhcp)

        result = post_request.post_set_port(alias=None,  # A user-defined name for this interface.  Can be BLANK or NA.
                                            current_flags=my_current_flags,  # See above, or NA.
                                            current_flags_msk=my_current_flags,
                                            # This sets 'interest' for flags 'Enable RADIUS service' and higher. See above, or NA.
                                            interest=my_interest_flags,
                                            port='eth2',  # Port number for the port to be modified.
                                            report_timer=2000,
                                            resource=1,  # Resource number for the port to be modified.
                                            shelf=1,  # Shelf number for the port to be modified.
                                            debug_=True)
        get_request = LFG(lfclient_host=args.host,
                          lfclient_port=8080,
                          debug_=True,
                          _exit_on_error=True)

        result = get_request.get_port(eid_list="1.1.eth2",
                                      requested_col_names=["_links",
                                                           "alias",
                                                           "port",
                                                           "mac",
                                                           "PORT_SUPPORTED_FLAGS_L",
                                                           "PORT_SUPPORTED_FLAGS_H",
                                                           "PORT_CUR_FLAGS_L",
                                                           "PORT_CUR_FLAGS_H" ],
                                      debug_=True)
        pprint.pprint(result)
    except Exception as x:
        import traceback
        traceback.print_tb(x)
        print(x.__repr__())
        exit(1)



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #


if __name__ == "__main__":
    main()
#
