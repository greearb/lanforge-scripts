#!/usr/bin/env python3
# flake8: noqa
import sys
import os
import importlib
import time
import json
from pprint import pprint
import logging
import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
logger = logging.getLogger(__name__)

class cv_test_tool(Realm):
    def __init__(self,
                 lf_mgr="localhost",
                 lf_port=8080,
                 lf_report_dir=None,
                 debug=False,
                 lf_user='lanforge',
                 lf_passwd='lanforge'
                 ):
        super().__init__(lfclient_host=lf_mgr,
                         lfclient_port=lf_port,
                         debug_=debug
                         )

        self.host = lf_mgr
        self.port = lf_port

    # To get if test is running or not
    def get_is_running(self, instance):
        cmd = "cv get %s 'StartStop'" % instance
        val = self.run_cv_cmd(cmd)
        # pprint(val)
        return val[0]["LAST"]["response"] == 'StartStop::Stop'


    def run_cv_cmd(self, command):  # Send chamber view commands
        response_json = []
        req_url = "/gui-json/cmd"
        data = {"cmd": command}
        self.json_post(req_url, data, debug_=False, response_json_list_=response_json)
        return response_json


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''\
            Chamberview Tool to check if chamberview test is running

            ''')
    parser.add_argument("--host", "--mgr", "--lf_mgr", dest='mgr', help='specify the GUI to connect to',default='localhost')
    parser.add_argument("--mgr_port", help="specify the GUI to connect to, default 8080", default="8080")
    parser.add_argument("--lf_user", help="lanforge user name default: lanforge", default="lanforge")
    parser.add_argument("--lf_passwd", help="lanforge password default: lanforge", default="lanforge")

    parser.add_argument("--instance", "--scenario", dest='instance', help='chamber view instance to query')
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--debug', help='Legacy debug flag', action='store_true')
    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')


    args = parser.parse_args()
    help_summary = '''\
This script will check if chamberview test is running
'''

    if args.help_summary:
        print(help_summary)
        exit(0)

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

    cv_tool = cv_test_tool(lf_mgr=args.mgr,
                             lf_port=args.mgr_port,
                             lf_user=args.lf_user,
                             lf_passwd=args.lf_passwd,
                             debug=args.debug)

    logger.debug("Instance {instance}".format(instance=args.instance))

    is_test_running = cv_tool.get_is_running(args.instance)

    logger.info("is test running {is_test_running}".format(is_test_running=is_test_running))

if __name__ == "__main__":
    main()
