#!/usr/bin/env python3
"""
NAME: raw_cli.py

PURPOSE: Assemble a single CLI command and execute it over the REST API.
        This includes a raw single line command or a command assembled with named parameters.
        If you are chaining multiple raw_cli.py commands together then you should probably
        be updating an existing script.
        Requires lanforge_api.py.

EXAMPLES:
=========
    Creating a Layer 3 TCP connection:
    ----------------------------------
$ ./raw_cli.py --mgr ct521a-manx.bitratchet.net --cmd rm_endp --arg "endp_name tcp-A"

$ ./raw_cli.py --mgr ct521a-manx.bitratchet.net --cmd add_endp --arg "alias tcp-A" \
    --arg "shelf 1" --arg "resource 1" --arg "port eth1" --arg "p_type lf_tcp" --arg "ip_port ANY" \
    --arg "min_rate 36000" --arg "max_rate 0" --arg "multi_conn 10"

$ ./raw_cli.py --mgr ct521a-manx.bitratchet.net --cmd add_endp --arg "alias tcp-B" \
    --arg "shelf 1" --arg "resource 1" --arg "port eth2" --arg "p_type lf_tcp" --arg "ip_port ANY" \
    --arg "min_rate 36000" --arg "max_rate 0" --arg "multi_conn 10"

$ ./raw_cli.py --mgr ct521a-manx.bitratchet.net --cmd add_cx --arg "alias tcp" \
    --arg "test_mgr default_tm" --arg "tx_endp tcp-B" --arg "rx_endp tcp-A"

    Sending a raw one-line command:
    -------------------------------
$ ./raw_cli.py --mgr localhost --raw "reset_port 1 1 sta00500"

    Submitting a text blob entry:
    -----------------------------
$ ./raw_cli.py --mgr ct521a-jana --raw "add_text_blob category type it takes a village to raise a child"

STATUS: Functional

NOTES:
======
This method of executing CLI commands presently reports errors caught by pre_exec hooks set in the
Http CliCmd handler.

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: True

TO DO NOTES:
    * Add parameter to suppress pre_exec error checking (suppress_related_commands)
"""
import logging
import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
sys.path.insert(1, "../")

lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFJsonCommand  # noqa E402
from lanforge_client.lanforge_api import LFJsonQuery  # noqa E402

logger = logging.getLogger(__name__)


def main():
    help_summary = """Utility script intended to be used from shell scripts in order to send commands
        to a LANforge system through the REST API. This script can send a one-line preformatted command
        like the kind found in a /home/lanforge/DB directory, or can assemble a command using arguments.
        """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating raw command')
    parser.add_argument("--host", "--mgr",
                        default='localhost',
                        help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--help_summary", help="purpose of the script", action="store_true")
    parser.add_argument("--raw", help='full CLI command to execute, including all arguments')
    parser.add_argument("--cmd", help='CLI command, where arguments to the command are provided using --arg parameters')
    parser.add_argument("--arg", "--param", action='append', nargs='+',
                        help='paramets with value, eg: --arg "alias bartleby" --arg "max-txbps 1000000" ')
    parser.add_argument("--debug", "-d", help='turn on debugging', action="store_true")

    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

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

    txt_cmd = args.cmd
    if args.raw:
        if args.arg:
            raise ValueError("do not use --args with --raw")
        if not (" " in args.raw):
            logging.info("Unlikely use of --raw argument without spaces")
        txt_cmd = args.raw
        data = {
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
    cli_data_params: dict = {}

    for parameter in args.arg:
        k_v: list = []
        if isinstance(parameter[0], list):
            k_v = (parameter)
        elif isinstance(parameter[0], str):
            k_v = parameter[0].split(' ', 1)
        else:
            raise ValueError(f"Unable to handle value of '{parameter}' from args.arg")
        # pprint.pprint(["k_v", k_v, "parameter", parameter])
        cli_data_params[k_v[0]] = k_v[1]

    # look up the cmd from the session method_map
    if not (session.find_method(args.cmd)):
        pprint.pprint(["session.find_method:", args.cmd, session.find_method(args.cmd)])
        print(f"raw_cli.py: Unable to find cmd[{args.cmd}] in method_map:\n")
        print("    method_map keys:")
        session.print_method_map()
        exit(1)
    method_ref = session.method_map[args.cmd]
    # print(f"cmd[{args.cmd}] has reference: [{dir(method_ref) }]")
    # pprint.pprint(["CliDataPrams", cli_data_params])
    method_ref(**cli_data_params,
               response_json_list=response_json_list,
               errors_warnings=errors_warnings,
               debug=args.debug,
               suppress_related_commands=False)
    if len(errors_warnings) > 0:
        pprint.pprint(["errors and warnings:", errors_warnings])


if __name__ == "__main__":
    main()
