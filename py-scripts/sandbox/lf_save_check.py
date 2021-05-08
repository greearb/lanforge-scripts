#!/usr/bin/python3

'''
NAME:
lf_check.py

PURPOSE:
Configuration for lf_check.py , runs various tests

EXAMPLE:
lf_check.py

NOTES:

'''

import sys
if sys.version_info[0]  != 3:
    print("This script requires Python3")
    exit()

import os
import logging
import time
from time import sleep
import argparse
import json
from json import load
import configparser
from pprint import *
    

CONFIG_FILE = os.getcwd() + '/py-scripts/sandbox/lf_check_config.ini'    
RUN_CONDITION = 'ENABLE'

# see https://stackoverflow.com/a/13306095/11014343
class FileAdapter(object):
    def __init__(self, logger):
        self.logger = logger
    def write(self, data):
        # NOTE: data can be a partial line, multiple lines
        data = data.strip() # ignore leading/trailing whitespace
        if data: # non-blank
           self.logger.info(data)
    def flush(self):
        pass  # leave it to logging to flush properly


class lf_check():
    def __init__(self):
        self.radio_dict = {}
        self.test_dict = {}
    
    # Functions in this section are/can be overridden by descendants
    def read_config_contents(self):
        config_file = configparser.ConfigParser()
        success = True
        success = config_file.read(CONFIG_FILE)
        print("{}".format(success))
        print("{}".format(config_file))

        # NOTE: this may need to be a list for ssi 
        if 'RADIO_DICTIONARY' in config_file.sections():
            section = config_file['RADIO_DICTIONARY']
            self.radio_dict = json.loads(section.get('RADIO_DICT', self.radio_dict))

        if 'TEST_DICTIONARY' in config_file.sections():
            section = config_file['TEST_DICTIONARY']
            self.test_dict = json.loads(section.get('TEST_DICT', self.test_dict))
            #print("test_dict {}".format(self.test_dict))

    def run_script_test(self):
        for test in self.test_dict:
            if self.test_dict[test]['enabled'] == "TRUE":
                # print("test: {} enable: {} command: {} args: {}".format(self.test_dict[test],self.test_dict[test]['enabled'],self.test_dict[test]['command'],self.test_dict[test]['args']))

                # Note: do not replace with a lambda function  or (k), v for k, v in ... , 
                # loop through radios
                for radio in self.radio_dict:
                    # Replace RADIO, SSID, PASSWD, SECURITY with actual config values (e.g. RADIO_0_CFG to values)
                    if self.radio_dict[radio]["KEY"] in self.test_dict[test]['args']:
                        self.test_dict[test]['args'] = self.test_dict[test]['args'].replace(self.radio_dict[radio]["KEY"],'--radio {} --ssid {} --passwd {} --security {}'
                        .format(self.radio_dict[radio]['RADIO'],self.radio_dict[radio]['SSID'],self.radio_dict[radio]['PASSWD'],self.radio_dict[radio]['SECURITY']))
                                            

                #print("test: {} enable: {} command: {} args: {}".format(self.test_dict[test],self.test_dict[test]['enabled'],self.test_dict[test]['command'],self.test_dict[test]['args']))
                #print("enable: {} command: {} args: {}".format(self.test_dict[test]['enabled'],self.test_dict[test]['command'],self.test_dict[test]['args']))
                command = "./{} {}".format(self.test_dict[test]['command'],self.test_dict[test]['args'])
                print("command: {}".format(command))
def main():
    check = lf_check()
    #check.parse_ap_stats()
    check.read_config_contents() # CMR need mode to just print out the test config and not run 

    check.run_script_test()


if __name__ == '__main__':
    main()


