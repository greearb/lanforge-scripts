#!/usr/bin/env python3
"""
NAME: lf_interop_modify.py

PURPOSE: Call commands/modifications to Interop Devices

EXAMPLE:
$ ./lf_interop_modify.py gui 1 1 KEBE2021070849 --display 192.168.100.220 --screensize 0.4

NOTES:
#Currently these commands are broken due to an error in the Adb cli command handling.
#@TODO finish logic for MODIFY (batch modify) commands


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

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    desc = 'modifies interop device\n' \
           '\nCommands:' \
           '\n--> gui' \
           '\n\t-loads gui' \
           '\n\t-ex command: lf_interop_modify.py gui 1 1 KEBE2021070849 --display 192.168.100.220 --screensize 0.4' \
           '\n-->install' \
           '\n\t-installs apk' \
           '\n\t-ex command: lf_interop_modify.py install 1 1 0123456789ABCDEF -g -filename interop-new.apk' \
           '\n-->log' \
           '\n\t-capture logs' \
           '\n\t-ex command: lf_interop_modify.py log 1 1 KEBE2021070849 --duration 5' \
           '\n-->modify' \
           '\n\t-change other LF device settings' \
           '\n\tex command: lf_interop_modify.py modify log 1 1 KEBE2021070849'

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)
    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--host", "--mgr", default='localhost', help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument('operation', type=str, default='gui', help='specify the operation to be performed '
                                                                   '( gui | install | log | modify )')
    parser.add_argument('shelf', type=int, default='1', help='specify the shelf of the interop device')
    parser.add_argument('resource', type=int, default='1', help='specify the card of the interop device')
    parser.add_argument('serno', type=str, default='', help='specify the serial number of the interop device')

    parser.add_argument('--display', type=str, default='192.168.100.220:0',
                        help='GUI: specify the X-windows display to '
                             'which the Android GUI will be '
                             'connected Ex: 192.168.100.264:0.0')
    parser.add_argument('--screensize', type=float, default='0.4', help='GUI: specify the Android screen size when '
                                                                        'launching the Android GUI (percent as float)')

    parser.add_argument('--g', action='store_true', help='INSTALL: install with -g')
    parser.add_argument('--filename', type=str, default='interop-5.4.5.apk',
                        help='INSTALL: filename of apk to be installed')

    parser.add_argument('--duration', type=float, default=5, help='LOG: the amount of time for logs to be gathered (in '
                                                                  'minutes)')
    parser.add_argument('--username', type=str, default="", help='MODIFY: device username')
    parser.add_argument('--manager', type=str, help='MODIFY: LANForge Manager IP')
    parser.add_argument('--ssid', type=str, help='MODIFY: SSID')
    parser.add_argument('--password', type=str, help='MODIFY: password')
    parser.add_argument('--encryption', type=str, help='MODIFY: encryption (open, psk, psk2)')

    args = parser.parse_args()

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

    # different commands

    match args.operation:
        case 'gui':
            command.post_adb_gui(shelf=args.shelf,
                                 resource=args.resource,
                                 adb_id=args.serno,
                                 display=args.display,
                                 screen_size_prcnt=args.screensize,
                                 debug=args.debug)
        case 'install':
            cmd = "install -r -t "
            if args.g:
                cmd += "-g "
            cmd += "-d " + args.filename.strip()

            command.post_adb(shelf=args.shelf,
                             resource=args.resource,
                             adb_id=args.serno,
                             adb_cmd=cmd,
                             debug=args.debug)
            print(cmd)

        case 'log':
            command.post_log_capture(shelf=args.shelf,
                                     resource=args.resource,
                                     p_type="adb",
                                     identifier=args.serno,
                                     duration=args.duration,
                                     destination="stdout",
                                     user_key="adb-log-" + args.serno,
                                     debug=args.debug)
        #@TODO put modify logic here


if __name__ == "__main__":
    main()
