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

if sys.version_info[0]  != 3:
    print("This script requires Python3")
    exit()

sys.path.insert(1, "../../py-json")
import argparse
import pprint

from LANforge import lf_json_autogen
from LANforge.lf_json_autogen import LFJsonGet
from LANforge.lf_json_autogen import LFJsonPost

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
    get_request = LFJsonGet(lfclient_host=args.host,
                                            lfclient_port=8080,
                                            debug_=True,
                                            _exit_on_error=True)

    result = get_request.get_port(eid_list="1.1.eth2",
                                  requested_col_names='list',
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
    # my_cmd_flags        = LFJsonPost.set_port_cmd_flags(0x0)
    my_current_flags    = LFJsonPost.set_port_current_flags(LFJsonPost.set_port_current_flags.use_dhcp)
    my_interest_flags   = LFJsonPost.set_port_interest(LFJsonPost.set_port_interest.dhcp)

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
    pprint.pprint(post_request)
    my_current_flags.clear_flags(flag_names=LFJsonPost.set_port_current_flags.use_dhcp)
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
    get_request = LFJsonGet(lfclient_host=args.host,
                                        lfclient_port=8080,
                                        debug_=True,
                                        _exit_on_error=True)

    result = get_request.get_port(eid_list="1.1.eth2", requested_col_names=['all'], debug_=True)
    pprint.pprint(result)

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #


if __name__ == "__main__":
    main()
#