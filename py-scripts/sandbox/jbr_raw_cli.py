#!/usr/bin/env python3
"""
NAME: jbr_raw_cli.py

PURPOSE: test the functionality of passing raw commands thru JSON API

EXAMPLE:
$ ./jbr_raw_cli.py --mgr localhost --debug --cmd "reset_port 1 1 sta00500"
$ echo watch that station reset

$ ./jbr_raw_cli.py --host ct521a-jana --cmd "add_text_blob category type it takes a village to raise a child"
$ Krl /text/spicy.takes
$ echo that created a text blob

NOTES:
This method of executing CLI commands does NOT report errors presently.

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
import inspect
import collections
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

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
#   M A I N
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating raw command')
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')

    parser.add_argument("--raw", help='full CLI command to execute, including all arguments')
    parser.add_argument("--cmd", help='CLI command, where arguments to the command are provided using --arg parameters')
    parser.add_argument("--arg", action='append', nargs='+',
                        help='paramets with value, eg: --arg "alias bartleby" --arg "max-txbps 1000000" ')
    parser.add_argument("--debug", "-d", help='turn on debugging', action="store_true")

    args = parser.parse_args()
    if not (args.cmd or args.raw):
        print("No --raw or --cmd command provided")
        exit(1)

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

    txt_cmd = args.cmd
    if args.raw:
        if args.arg:
            raise ValueError("do not use --args with --raw");
        if not (" " in args.raw):
            logging.info("Unlikely use of --raw argument without spaces")
        txt_cmd = args.raw
        data={
            "cmd": txt_cmd
        }

        # command.json_post(url="/cli-json/raw",
        #                  post_data=data,
        #                  debug=args.debug,
        #                  suppress_related_commands=True)
        command.json_post_raw(post_data=data,
                              debug=args.debug,
                              suppress_related_commands=True)
        exit(0)

    if not args.cmd:
        raise ValueError("--cmd required, please use a CLI command, followed by --args 'parameter value' as necessary")
    if not args.arg:
        raise ValueError("There appear to be no --arg parameters provided.")

    # compose the dict of args to pass into the eval
    # print( f"typeof args.arg:{type(args.arg)}")
    response_json_list = []
    errors_warnings = []
    cli_data_params : dict = {}
    print(" ----- 107 cmd ----- ----- ----- ----- ----- ----- ----- ----- -----")
    for parameter in args.arg:
        k_v : list = []
        if isinstance(parameter[0], list):
            k_v = (parameter)
        elif isinstance(parameter[0], str):
            k_v = parameter[0].split(' ', 1)
        else:
            raise ValueError("Unable to handle value of 'parameter' from args.arg")
        # pprint.pprint(["k_v", k_v, "parameter", parameter])
        cli_data_params[k_v[0]] = k_v[1]

    # look up the cmd from the session method_map
    if not (session.find_method(args.cmd)):
        print(f"Unable to find cmd[{args.cmd}] in method_map:\n")
        print("    method_map keys:")
        session.print_method_map();
        exit(1)
    method_ref = session.method_map[args.cmd];
    # print(f"cmd[{args.cmd}] has reference: [{dir(method_ref) }]")
    # pprint.pprint(["CliDataPrams", cli_data_params])
    method_ref(**cli_data_params,
               response_json_list=response_json_list,
               errors_warnings=errors_warnings,
               debug=args.debug,
               suppress_related_commands=False)


if __name__ == "__main__":
    main()
