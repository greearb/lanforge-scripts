#!/usr/bin/env python3
'''
NAME: jbr_create_wanlink.py

PURPOSE: create a wanlink

EXAMPLE:
$ ./jbr_create_wanlink.py --host ct521a-jana --wl_name snail

To enable using lf_json_autogen in other parts of the codebase, set LF_USE_AUTOGEN=1:
$ LF_USE_AUTOGEN=1 ./jbr_jag_test.py --test set_port --host ct521a-lion

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


# import LANforge.lfcli_base
# from LANforge.lfcli_base import LFCliBase

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating wanlink')
    parser.add_argument("--host", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--wl_name", help='name of the wanlink to create')
    parser.add_argument("--resource", help='LANforge resource')

    args = parser.parse_args()
    if not args.wl_name:
        print("No wanlink name provided")
        exit(1)
    post_rq = lf_json_autogen.LFJsonPost(lfclient_host=args.host,
                                              lfclient_port=8080,
                                              debug_=False,
                                              _exit_on_error=True)
    get_request = LFG(lfclient_host=args.host,
                      lfclient_port=8080,
                      debug_=False,
                      _exit_on_error=True)

    post_rq.post_add_rdd(resource=args.resource,
                         port="rd0a",
                         peer_ifname="rd0b",
                         report_timer=1000,
                         shelf=1,
                         debug_=False)
    post_rq.post_add_rdd(resource=args.resource,
                         port="rd1a",
                         peer_ifname="rd1b",
                         report_timer=1000,
                         shelf=1,
                         debug_=False)
    endp_a = args.wl_name + "-A"
    endp_b = args.wl_name + "-B"
    post_rq.post_add_wl_endp(alias=endp_a,
                             resource=args.resource,
                             port="rd0a",
                             shelf=1,
                             debug_=False)
    post_rq.post_add_wl_endp(alias=endp_b,
                             resource=args.resource,
                             port="rd1a",
                             shelf=1,
                             debug_=True)
    post_rq.post_add_cx(alias=args.wl_name,
                        rx_endp=endp_a,
                        tx_endp=endp_b,
                        test_mgr="default_tm",
                        debug_=True)

    result = get_request.get_wl(eid_list=(args.wl_name))
    pprint.pprint(result)
    result = get_request.get_wl_endp(eid_list=(args.wl_name+"-A", args.wl_name+"-B"))
    pprint.pprint(result)


if __name__ == "__main__":
    main()
#
