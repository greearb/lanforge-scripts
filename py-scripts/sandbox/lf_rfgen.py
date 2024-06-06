#!/usr/bin/env python3
'''
NAME: lf_rfgen.py

PURPOSE: lanforge api interface for rfgen commands

EXAMPLE:

SCRIPT_CLASSIFICATION:  Module

SCRIPT_CATEGORIES: 

NOTES:

STATUS: PROTOTYPE

VERIFIED_ON: Underdevelopment

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: True
'''
import sys
import time

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
from pprint import pformat
import os
import logging

# sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery


lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)

# add_wanpath
# http://www.candelatech.com/lfcli_ug.php#add_wanpath


class lf_rfgen():
    def __init__(self,
                 lf_mgr=None,
                 lf_port=None,
                 lf_user=None,
                 lf_passwd=None,
                 debug=False,
                 ):
        self.lf_mgr = lf_mgr
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_passwd
        self.debug = debug

        self.session = LFSession(lfclient_url="http://%s:8080" % self.lf_mgr,
                                 debug=debug,
                                 connection_timeout_sec=4.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=True)
        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()


    def show(self,
        _p_id: str = None,                         # RF Generator serial number, or 'all'.
        _resource: int = None,                     # Resource number, or 'all'. [W]
        _shelf: int = 1,                           # Shelf number or alias, can be 'all'. [R][D:1]
        _response_json_list: list = None,
        _debug: bool = False,
        _errors_warnings: list = None,
        _suppress_related_commands: bool = False):


        response = self.command.post_show_rfgen(
                p_id = _p_id,                         # RF Generator serial number, or 'all'.
                resource= _resource,                     # Resource number, or 'all'. [W]
                shelf = 1,                           # Shelf number or alias, can be 'all'. [R][D:1]
                response_json_list = _response_json_list,
                debug = _debug,
                errors_warnings = _errors_warnings,
                suppress_related_commands = _suppress_related_commands)

        logger.debug("Response: {response}".format(response=response))
        logger.debug(pformat(_response_json_list))
        return response

    def get(self,
        _eid_list: list = None,
        _requested_col_names: list = None,
        _wait_sec: float = 0.01,
        _timeout_sec: float = 5.0,
        _errors_warnings: list = None,
        _debug: bool = False):


        response = self.command.get_rfgen(
        eid_list = _eid_list,
        requested_col_names = _requested_col_names,
        wait_sec = _wait_sec,
        timeout_sec = _timeout_sec,
        errors_warnings = _errors_warnings,
        debug = _debug)

        logger.debug("Response get rfgen: {response}".format(response=response))
        logger.debug(pformat(_response_json_list))
        return response




# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
#   Main
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''\
NAME: lf_rfgen.py  

PURPOSE: lanforge api interface for rfgen commands

EXAMPLE: Work in progress

CURL command:
curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.19:8080/rfgen/ | json_pp

SCRIPT_CLASSIFICATION:  Module

SCRIPT_CATEGORIES: 

NOTES:

STATUS: PROTOTYPE

VERIFIED_ON: Underdevelopment

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: True
            ''')
    # http://www.candelatech.com/lfcli_ug.php#show_rfgen
    # http://www.candelatech.com/lfcli_ug.php#set_rfgen
    parser.add_argument("--host", "--mgr", dest='mgr', help='specify the GUI to connect to',default="192.168.0.19")
    parser.add_argument("--mgr_port", help="specify the GUI to connect to, default 8080", default="8080")
    parser.add_argument("--lf_user", help="lanforge user name default lanforge", default="lanforge")
    parser.add_argument("--lf_passwd", help="lanforge password defualt lanforge ", default="lanforge")
    parser.add_argument("--resource", help='(add wl endp) LANforge resource Default', default=1)
    parser.add_argument("--shelf", help='(add wl endp) LANforge Shelf name/id', default=1)
   
    parser.add_argument("--id","--lf_hackrf","--sdr_serial_num",dest=id, help='ct712 id  default= all', default='57b068dc22276763')
    parser.add_argument("--one_burst", help='net to one burst', store=True)
    parser.add_argument("--rf_type", help='rf_type', required=True)
    parser.add_argument("--gain", help='gain 14', default=14)
    parser.add_argument("--if_gain", help='(transmit) if_gain 30', default=14)
    parser.add_argument("--bb_gain", help='(receive) bb_gain 20', default=20)





    # Logging Configuration
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--debug', help='Legacy debug flag', action='store_true')

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


    rfgen = lf_rfgen(lf_mgr=args.mgr,
                    lf_port=8080,
                    lf_user=args.lf_user,
                    lf_passwd=args.lf_passwd,
                    debug=args.debug)

    response_json_list = []

    response = rfgen.show(
        _p_id = args.id,                         # RF Generator serial number, or 'all'.
        _resource = args.resource,                     # Resource number, or 'all'. [W]
        _shelf = args.shelf,                           # Shelf number or alias, can be 'all'. [R][D:1]
        _response_json_list = response_json_list,
        _debug = args.debug,
        _errors_warnings = None,
        _suppress_related_commands = False)

    logger.info("Response: {response}".format(response=response))
    logger.info(pformat(response_json_list))
    '''
    response = rfgen.get(
        _eid_list = ['1.1.57b068dc21104e63','1.1.570b8dc22276763'],                         
        _requested_col_names = ,                    
        _shelf = args.shelf,                           # Shelf number or alias, can be 'all'. [R][D:1]
        _response_json_list = response_json_list,
        _debug = args.debug,
        _errors_warnings = None,
        _suppress_related_commands = False)

    logger.info("Response: {response}".format(response=response))
    logger.info(pformat(response_json_list))
    '''

if __name__ == "__main__":
    main()
