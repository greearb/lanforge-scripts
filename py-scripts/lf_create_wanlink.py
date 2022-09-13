#!/usr/bin/env python3
"""
NAME: lf_create_wanlink.py

PURPOSE: create a wanlink using the lanforge api

EXAMPLE:
$ ./lf_create_wanlink.py 

NOTES:


TO DO NOTES:

"""
import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
import os
import logging

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)

# add_wanpath
# http://www.candelatech.com/lfcli_ug.php#add_wanpath
class lf_create_wanlink():
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


    def add_wl_endp(self,
                    _alias=None,
                    _shelf=None,
                    _resource=None,
                    _wanlink=None,
                    _speed=None,
                    _port=None,
                    _drop_freq=None,
                    _max_jitter=None,
                    _latency=None,
                    _min_reorder_amt=None,
                    _max_reorder_amt=None,
                    _min_drop_amt=None):

        if _alias is None:
            logger.error("alias in None alias must be set to end point A or end point B. Exiting")
            exit(1)

        self.command.post_add_wl_endp(alias=_alias,
                                shelf=1,
                                resource=_resource,
                                wanlink=_wanlink,
                                speed=56000,
                                port="rd0a",
                                drop_freq="0",
                                max_jitter="10",
                                latency="10ms",
                                min_reorder_amt="1",
                                max_reorder_amt="10",
                                min_drop_amt="1",
                                debug=self.debug)
        self.command.post_add_wl_endp(alias=_alias,
                                shelf=1,
                                resource=_resource,
                                port="rd1a",
                                wanlink=_wanlink,
                                speed=56000,
                                drop_freq="0",
                                max_jitter="10",
                                latency="10ms",
                                min_reorder_amt="1",
                                max_reorder_amt="10",
                                min_drop_amt="1",
                                debug=self.debug)
            

        self.command.post_add_wl_endp(alias=_alias,
                                      shelf=_shelf,
                                      resource=_resource,
                                      wanlink=_wanlink,
                                      speed=_speed,
                                      port=_port,
                                      drop_freq=_drop_freq,
                                      max_jitter=_max_jitter,
                                      latency=_latency,
                                      min_reorder_amt=_min_reorder_amt,
                                      max_reorder_amt=_max_reorder_amt,
                                      min_drop_amt=_min_drop_amt,
                                      debug=self.debug)


    def add_cx(self,
               alias=None,
               rx_endp_a=None, # endp_a
               tx_endp_b=None, # endp_b
               test_mgr="default_tm"):

        self.command.post_add_cx(alias=alias,
                        rx_endp=rx_endp_a,
                        tx_endp=tx_endp_b,
                        test_mgr=test_mgr)

    def get_wl(self,
               eid_list=None,
               wait_sec=None,
               timeout_sec=None,
               errors_warnings=None):
                          
        ewarn_list = []
        result = self.query.get_wl(eid_list=[args.wl_name],
                          wait_sec=0.2,
                          timeout_sec=2.0,
                          errors_warnings=ewarn_list,
                          debug=self.debug)
        pprint.pprint(result)
        return result

    def get_wl_endp(self,
                    eid_list=None,
                    wait_sec=None,
                    timeout_sec=None):

        result = self.query.get_wl_endp(eid_list=eid_list,
                               wait_sec=0.2,
                               timeout_sec=15.0,
                               debug=self.debug)
        pprint.pprint(result)
        return result



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #
def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''\
            tests creating wanlink
            ''')
    parser.add_argument("--host", "--mgr", dest='mgr', help='specify the GUI to connect to')
    parser.add_argument("--mgr_port", help="specify the GUI to connect to, default 8080",default="8080")
    parser.add_argument("--lf_user", help="specify the GUI to connect to, default 8080",default="lanforge")
    parser.add_argument("--lf_passwd", help="specify the GUI to connect to, default 8080",default="lanforge")
    parser.add_argument("--wl_name", help='name of the wanlink to create')
    parser.add_argument("--resource", help='LANforge resource',default=1)
    parser.add_argument('--port_A', help='Endpoint A', default="eth1")
    parser.add_argument('--port_B', help='Endpoint B', default="eth2")
    parser.add_argument('--rate', help='The maximum rate of transfer at both endpoints (bits/s) ', default=1000000)
    parser.add_argument('--rate_A', help='The maximum rate of transfer at endpoint A (bits/s)', default=None)
    parser.add_argument('--rate_B', help='The maximum rate of transfer at endpoint B (bits/s)', default=None)
    parser.add_argument('--latency', help='The delay of both ports', default=20)
    parser.add_argument('--latency_A', help='The delay of port A', default=None)
    parser.add_argument('--latency_B', help='The delay of port B', default=None)
    parser.add_argument('--jitter', help='The max jitter of both ports (ms)', default="10")
    parser.add_argument('--jitter_A', help='The max jitter of port A (ms)', default=None)
    parser.add_argument('--jitter_B', help='The max jitter of port B (ms)', default=None)
    parser.add_argument('--jitter_freq', help='The jitter frequency of both ports (%%)', default="0")
    parser.add_argument('--jitter_freq_A', help='The jitter frequency of port A (%%)', default=None)
    parser.add_argument('--jitter_freq_B', help='The jitter frequency of port B (%%)', default=None)
    parser.add_argument('--drop', help='The drop frequency of both ports (%%)', default="0")
    parser.add_argument('--drop_A', help='The drop frequency of port A (%%)', default=None)
    parser.add_argument('--drop_B', help='The drop frequency of port B (%%)', default=None)
    # todo: packet loss A and B
    # todo: jitter A and B
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


    if not args.wl_name:
        print("No wanlink name provided")
        exit(1)


    wanlink = lf_create_wanlink(lf_mgr=args.mgr,
                                lf_port=8080,
                                lf_user=args.lf_user,
                                lf_passwd=args.lf_passwd,
                                debug=True)

    endp_a = args.wl_name + "-A"
    endp_b = args.wl_name + "-B"

    # work though to see if common 
    rate_A = args.rate_A if args.rate_A is not None else args.rate
    rate_B = args.rate_B if args.rate_B is not None else args.rate

    latency_A = args.latency_A if args.latency_A is not None else args.latency
    latency_B = args.latency_B if args.latency_B is not None else args.latency
    
    jitter_A = args.jitter_A if args.jitter_A is not None else args.jitter
    jitter_B = args.jitter_B if args.jitter_B is not None else args.jitter

    jitter_freq_A = args.jitter_freq_A if args.jitter_freq_A is not None else args.jitter_freq
    jitter_freq_B = args.jitter_freq_B if args.jitter_freq_B is not None else args.jitter_freq

    drop_A = args.drop_A if args.drop_A is not None else args.drop
    drop_B = args.drop_B if args.drop_B is not None else args.drop
    

    endp_a = args.wl_name + "-A"
    endp_b = args.wl_name + "-B"
    # Comment out some parameters like 'max_jitter', 'drop_freq' and 'wanlink'
    # in order to view the X-Errors headers



    # create side A
    wanlink.add_wl_endp(_alias=endp_a,
                        _shelf=1,
                        _resource=args.resource,
                        _wanlink=args.wl_name,
                        _speed=rate_A,
                        _port=args.port_A,
                        _drop_freq=drop_A,
                        _max_jitter=jitter_A,
                        _latency=latency_A,
                        _min_reorder_amt="1",
                        _max_reorder_amt="10",
                        _min_drop_amt="1")


    wanlink.add_wl_endp(_alias=endp_b,
                        _shelf=1,
                        _resource=args.resource,
                        _port="rd1a",
                        _wanlink=args.wl_name,
                        _speed=56000,
                        _drop_freq="0",
                        _max_jitter="10",
                        _latency="10ms",
                        _min_reorder_amt="1",
                        _max_reorder_amt="10",
                        _min_drop_amt="1")

    result = wanlink.add_cx(alias=args.wl_name,
                        rx_endp=endp_a,
                        tx_endp=endp_b,
                        test_mgr="default_tm")

    pprint.pprint(result)

    eid_list = [args.wl_name]
    ewarn_list = []
    result = wanlink.get_wl(eid_list=eid_list,
                          wait_sec=0.2,
                          timeout_sec=2.0,
                          errors_warnings=ewarn_list)
    pprint.pprint(result)

                          

if __name__ == "__main__":
    main()
