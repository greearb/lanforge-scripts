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

import sys
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
import os
import importlib
import argparse
import pprint
import logging
from pprint import pprint
from urllib.parse import urlparse
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
logger = logging.getLogger(__name__)


LFUtils = importlib.import_module("py-json.LANforge.LFUtils")


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
class InteropCommands(Realm):
    def __init__(self,
                 _host=None,
                 _port=None,
                 device_eid=None,
                 operation=None,
                 display=None,
                 screen_size_prcnt=None,
                 duration=None,
                 log_destination=None,
                 install_g_opt=False,
                 filename=None,
                 _proxy_str=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(lfclient_host=_host,
                         debug_=_debug_on)
        self.device_eid=device_eid
        self.display=display
        self.screen_size_prcnt=screen_size_prcnt
        self.duration=duration
        self.operation=operation
        self.log_destination=log_destination
        self.install_g_opt=install_g_opt
        self.filename=filename
        # we cannot assume port 8080 because some labs use port translation
        self.debug = _debug_on
        self.session = LFSession(lfclient_url=_host,
                                 debug=_debug_on,
                                 connection_timeout_sec=2.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=_exit_on_error)
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    def run(self):
        if not self.device_eid:
            raise ValueError("device EID is required")

        eid = self.name_to_eid(self.device_eid)
        pprint(eid)

        if self.operation == 'gui':
            self.command.post_adb_gui(shelf=eid[0],
                                      resource=eid[1],
                                      adb_id=eid[2],
                                      display=self.display,
                                      screen_size_prcnt=self.screen_size_prcnt,
                                      debug=self.debug)

        elif self.operation == 'install':
            cmd = "install -r -t "
            if self.install_g_opt:
                cmd += "-g "
            cmd += "-d " + self.filename.strip()
            print(self.adb_command)
            self.command.post_adb(shelf=eid[0],
                                  resource=eid[1],
                                  adb_id=eid[2],
                                  adb_cmd=self.adb_command,
                                  debug=self.debug)


        elif self.operation == 'log':
            if not self.log_destination:
                raise ValueError("adb log capture requires log_destination")
            user_key = self.session.get_session_based_key()
            if (self.debug):
                print ("====== ====== destination [%s] dur[%s] user_key[%s] " %
                        (self.log_destination, self.duration, user_key))
                self.session.logger.register_method_name("json_post")
            response = self.command.post_log_capture(shelf=eid[0],
                                          resource=eid[1],
                                          p_type="adb",
                                          identifier=eid[2],
                                          duration=self.duration,
                                          destination=self.log_destination,
                                          user_key=self.session.get_session_based_key(),
                                          debug=True)
            pprint(["RESPONSE", response])
        # @TODO put modify logic here

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    desc = """modifies interop device 
    Operations: 
    *    Example of loading Interop GUI: 
    lf_interop_modify.py --operation gui --device 1.1.KEBE2021070849 --display 192.168.100.220 --screensize 0.4 
    *    Example of installing APK: 
    lf_interop_modify.py --operation install 1.1.0123456789ABCDEF -g -filename interop-new.apk 
    *    Example of capturing logs 
    lf_interop_modify.py --operation log 1.1.KEBE2021070849 --duration 5 
    *    Example of change other LF device settings 
    lf_interop_modify.py --operation modify log 1.1.KEBE2021070849\n"""

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--host", "--mgr", default='localhost',
                        help='specify the GUI to connect to, assumes port 8080')

    parser.add_argument('--operation', '-o', '--op', type=str, default='gui',
                        help='specify the operation to be performed: ( gui | install | log | modify )')

    parser.add_argument('--device', type=str, default='',
                        help='specify the EID (serial number) of the interop device (eg 1.1.91BX93V4')

    parser.add_argument('--display', type=str, default='192.168.100.220:0',
                        help='GUI: X-windows display address (IP:display) that the Android GUI will be '
                             'displayed on. EG: 192.168.100.264:0.0')

    parser.add_argument('--screensize', type=float, default='0.4',
                        help='GUI: specify the Android screen size when launching the Android GUI (percent as float)')

    parser.add_argument('--option_g', action='store_true',
                        help='INSTALL: install apk with -g option')
    parser.add_argument('--filename', type=str, default='interop-5.4.5.apk',
                        help='INSTALL: filename of apk to be installed')

    parser.add_argument('--duration', type=float, default=5,
                        help='LOG: the amount of time for logs to be gathered (in minutes)')
    parser.add_argument('--log_destination',
                        help='LOG: the amount of time for logs to be gathered (in minutes)')
    parser.add_argument('--log_level', default=None)

    args = parser.parse_args()
    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to requested level
    logger_config.set_level(level=args.log_level)

    myhost = args.host
    if not (myhost.startswith("http:") or myhost.startswith("https:")):
        myhost = "http://"+args.host
    parsed_url = urlparse(myhost)
    if not parsed_url.port:
        parsed_url.port = 8080

    interop = InteropCommands(_host=parsed_url.hostname,
                              _port=parsed_url.port,
                              device_eid=args.device,
                              display=args.display,
                              screen_size_prcnt=args.screensize,
                              duration=args.duration,
                              operation=args.operation,
                              log_destination=args.log_destination,
                              install_g_opt=args.option_g,
                              filename=args.filename,
                              _proxy_str=None,
                              _debug_on=False,
                              _exit_on_error=False,
                              _exit_on_fail=False)
    interop.run()

if __name__ == "__main__":
    main()
