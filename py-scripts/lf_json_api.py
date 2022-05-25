#!/usr/bin/env python3
'''
NAME: lf_json_api.py

PURPOSE:

 This script will is an example of using LANforge JSON API to use GET Requests to LANforge. 
 

EXAMPLE:

    This will run through the module test:
    ./lf_json_api.py --lf_mgr 192.168.100.178 --lf_port 8080 --resource 1 --log_level debug --port wlan3 --lf_user lanforge --lf_passwd lanforge --get_request 'port radio

NOTE:
    LANforge GUI , click on info -> API Help  look under GET Requests  use similiar format to what is being done below.
'''

import argparse
import sys
import os
import logging
import importlib
import requests
import pandas as pd
import json
# from pprint import pformat


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class lf_json_api():
    def __init__(self,
                lf_mgr,
                lf_port,
                lf_user,
                lf_passwd,
                resource,
                port):                
        self.lf_mgr = lf_mgr
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_passwd
        self.resource = resource
        self.port = port

    def get_request_port_information(self):
        # https://docs.python-requests.org/en/latest/
        # https://stackoverflow.com/questions/26000336/execute-curl-command-within-a-python-script - use requests
        # station command
        # curl -H 'Accept: application/json' 'http://localhost:8080/port/1/1/wlan3' | json_pp
        # a radio command
        # curl --user "lanforge:lanforge" -H 'Accept: application/json'
        # http://192.168.100.116:8080/port/1/1/wlan3 | json_pp  , where --user
        # "USERNAME:PASSWORD"
        request_command = 'http://{lfmgr}:{lfport}/port/1/{resource}/{port}'.format(
            lfmgr=self.lf_mgr, lfport=self.lf_port, resource=self.resource, port=self.port)
        request = requests.get(
            request_command, auth=(
                self.lf_user, self.lf_passwd))
        logger.info(
            "port request command: {request_command}".format(
                request_command=request_command))
        logger.info(
            "port request status_code {status}".format(
                status=request.status_code))
        lanforge_port_json = request.json()
        logger.debug("port request.json: {json}".format(json=lanforge_port_json))
        lanforge_port_text = request.text
        logger.debug("port request.text: {text}".format(text=lanforge_port_text))
        lanforge_port_json_formatted = json.dumps(lanforge_port_json, indent=4)
        logger.debug("lanforge_port_json_formatted: {json}".format(json=lanforge_port_json_formatted))

        return lanforge_port_json, lanforge_port_text, lanforge_port_json_formatted

    # TODO This method is left in for an example it was taken from
    def get_request_radio_information(self):
        # https://docs.python-requests.org/en/latest/
        # https://stackoverflow.com/questions/26000336/execute-curl-command-within-a-python-script - use requests
        # curl --user "lanforge:lanforge" -H 'Accept: application/json'
        # http://192.168.100.116:8080/radiostatus/all | json_pp  , where --user
        # "USERNAME:PASSWORD"
        request_command = 'http://{lfmgr}:{port}/radiostatus/all'.format(lfmgr=self.lf_mgr, port=self.lf_port)
        request = requests.get(
            request_command, auth=(
                self.lf_user, self.lf_passwd))
        logger.info(
            "radio request command: {request_command}".format(
                request_command=request_command))
        logger.info(
            "radio request status_code {status}".format(
                status=request.status_code))
        lanforge_radio_json = request.json()
        logger.info("radio request.json: {json}".format(json=lanforge_radio_json))
        lanforge_radio_text = request.text
        logger.info("radio request.text: {text}".format(text=lanforge_radio_text))
        return lanforge_radio_json, lanforge_radio_text


# unit test
def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    parser = argparse.ArgumentParser(
        prog="lf_json_api.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
        example
        """)

    parser.add_argument("--lf_mgr", type=str, help="address of the LANforge GUI machine (localhost is default)",
                        default='localhost')
    parser.add_argument("--lf_port", help="IP Port the LANforge GUI is listening on (8080 is default)",
                        default=8080)
    parser.add_argument("--lf_user", type=str, help="user: lanforge")
    parser.add_argument("--lf_passwd", type=str, help="passwd: lanforge")
    parser.add_argument("--port", type=str, help=" port : wlan3")
    parser.add_argument("--resource", type=str, help="LANforge Station resource ID to use, default is 1", default=1)
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    # logging configuration
    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")
    # TODO check command
    parser.add_argument("--get_requests", type=str, help="perform get request may be a list:  port | radio | port_rssi")

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


    lf_json = lf_json_api( args.lf_mgr,
                            args.lf_port,
                            args.lf_user,
                            args.lf_passwd,
                            args.resource,
                            args.port)

    get_requests = args.get_requests.split()

    for get_request in get_requests:
        if get_request == "radio":
            lf_json.get_request_radio_information()

        if get_request == "port":
            lanforge_port_json, lanforge_port_text, lanforge_port_json_formatted = lf_json.get_request_port_information()

            logger.info("lanforge_port_json = {lanforge_port_json}".format(lanforge_port_json=lanforge_port_json))
            logger.info("lanforge_port_text = {lanforge_port_text}".format(lanforge_port_text=lanforge_port_text))
            logger.info("lanforge_port_text = {lanforge_port_text}".format(lanforge_port_text=lanforge_port_text))

        if get_request == "port_rssi":
            lanforge_port_json, lanforge_port_text, lanforge_port_json_formatted = lf_json.get_request_port_information()
            logger.info("lanforge_port_json = {lanforge_port_json}".format(lanforge_port_json=lanforge_port_json))
            logger.info("lanforge_port_json_formatted = {lanforge_port_json_formatted}".format(lanforge_port_json_formatted=lanforge_port_json_formatted))

            for key in lanforge_port_json:
                if 'interface' in key:
                    avg_chain_rssi = lanforge_port_json[key]['avg chain rssi']
                    logger.info("avg chain rssi = {avg_chain_rssi}".format(avg_chain_rssi=avg_chain_rssi))
                    chain_rssi = lanforge_port_json[key]['chain rssi']
                    logger.info("chain rssi = {chain_rssi}".format(chain_rssi=chain_rssi))
                    signal = lanforge_port_json[key]['signal']
                    logger.info("signal = {signal}".format(signal=signal))

        if get_request == "alerts":
            lanforge_alerts_json = lf_json.get_alerts_information()

    # sample of creating layer 3 


if __name__ == '__main__':
    main()
