#!/usr/bin/env python3
'''
NAME: lf_create_rig_json.py

PURPOSE:
     This script will create a lf_rig.json file that is used as a input --json_rig to the lf_check.py script
     This script helps to store the of the information on LANforge
EXAMPLE:
    # For creating dut.json file according to the DUT present:
    lf_create_rig_json.py --file rig.json --lf_mgr 192.168.200.93 --lf_mgr_port 8080 --lf_user lanforge --lf_passwd lanforge
    --test_rig lanforge --test_bed lisp_lanforge --test_server 192.168.200.93 --test_db lf_test.db --upstream_port 1.1eth1
    --test_timeout 500



SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        This will create a file with the name specified in the CLI  [ --json_rig example_name.json ]
        * Helps to store the data related to the LANforge

STATUS: BETA RELEASE

VERIFIED_ON:   23-MAY-2023,
             Build Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

'''

import argparse
import logging
import importlib
import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


# sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../../")))


logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")



class lf_create_rig_json():
    def __init__(self,
                 _file,
                 _lf_mgr,
                 _lf_mgr_port,
                 _lf_user,
                 _lf_passwd,
                 _test_rig,
                 _test_bed,
                 _test_server,
                 _test_db,
                 _upstream_port,
                 _test_timeout,
                 _lf_atten_1_entry,
                 _lf_atten_2_entry,
                 _lf_atten_3_entry,
                 _lf_email_entry,
                 _lf_email_production_entry
                 ):
        self.file = _file
        self.lf_mgr = _lf_mgr
        self.lf_mgr_port = _lf_mgr_port
        self.lf_user = _lf_user
        self.lf_passwd = _lf_passwd
        self.test_rig = _test_rig
        self.test_bed = _test_bed
        self.test_server = _test_server
        self.test_db = _test_db
        self.upstream_port = _upstream_port
        self.test_timeout = _test_timeout
        self.lf_atten_1 = _lf_atten_1_entry
        self.lf_atten_2 = _lf_atten_2_entry
        self.lf_atten_3 = _lf_atten_3_entry
        self.lf_email_entry = _lf_email_entry
        self.lf_email_production_entry = _lf_email_production_entry


    # Helper methods
    def create(self):
        file_name = self.file
        file_fd = open(self.file, 'w')
        test_bed = self.test_bed
        test_rig = self.test_rig
        test_server = self.test_server
        test_db = self.test_db
        lf_mgr = self.lf_mgr
        lf_mgr_port = self.lf_mgr_port
        lf_user = self.lf_user
        lf_passwd = self.lf_passwd
        upstream_port = self.upstream_port
        test_timeout = self.test_timeout
        lf_atten_1 = self.lf_atten_1
        lf_atten_2 = self.lf_atten_2
        lf_atten_3 = self.lf_atten_3
        lf_email_entry = self.lf_email_entry
        lf_email_production_entry = self.lf_email_production_entry
        
        rig_json = f"""
{{
    "{file_name}":{{
        "Notes":[
            "This json file describes LANforge system used as input for --dut_json for lf_check.py"
        ]
    }},
    "test_rig_parameters":{{
        "TEST_BED": "{test_bed}",
        "TEST_RIG": "{test_rig}",
        "TEST_SERVER": "http://{test_server}/",
        "DATABASE_SQLITE": "./tools/{test_db}",
        "LF_MGR_IP": "{lf_mgr}",
        "LF_MGR_PORT": "{lf_mgr_port}",
        "LF_MGR_USER": "{lf_user}",
        "LF_MGR_PASS": "{lf_passwd}",
        "UPSTREAM_PORT":"{upstream_port}",
        "TEST_TIMEOUT":"{test_timeout}",
        "ATTENUATOR_1":"{lf_atten_1}",
        "ATTENUATOR_2":"{lf_atten_2}",
        "ATTENUATOR_3":"{lf_atten_3}", 
        "EMAIL_LIST_TEST": "{lf_email_entry}",
        "EMAIL_LIST_PRODUCTION":"{lf_email_production_entry}",
        "EMAIL_TITLE_TXT": "",
        "EMAIL_TXT": ""
    }}
}}"""


        file_fd.write(rig_json)
        file_fd.close()

# Feature, Sum up the subtests passed/failed from the kpi files for each run, poke those into the database, and generate a kpi graph for them.


def main():

    parser = argparse.ArgumentParser(
        prog='lf_create_rig_json.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_create_rig_json.py creates lf_rig.json file for --json_rig input to lf_check.py , LANforge traffic generation system
        NOTE: cannot have extra blank lines at the end of the json to work properly

            ''',
        description='''\
NAME: lf_create_rig_json.py

PURPOSE:
     This script will create a lf_rig.json file that is used as a input --json_rig to the lf_check.py script
     This script helps to store the of the information on LANforge
EXAMPLE:
    # For creating dut.json file according to the DUT present:
    lf_create_rig_json.py --file rig.json --lf_mgr 192.168.200.93 --lf_mgr_port 8080 --lf_user lanforge --lf_passwd lanforge
    --test_rig lanforge --test_bed lisp_lanforge --test_server 192.168.200.93 --test_db lf_test.db --upstream_port 1.1eth1
    --test_timeout 500



SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        This will create a file with the name specified in the CLI  [ --json_rig example_name.json ]
        * Helps to store the data related to the LANforge

STATUS: BETA RELEASE

VERIFIED_ON:   23-MAY-2023,
             Build Version:  5.4.6
             Kernel Version: 6.2.14+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False
''')
    parser.add_argument('--file', help='--file lf_rig.json , required', required=True)
    parser.add_argument('--lf_mgr', help='--lf_mgr <lanforge ip> required', required=True)
    parser.add_argument('--lf_mgr_port', help='--lf_mgr_port <lanforge port> ', default='8080')
    parser.add_argument('--lf_user', help='--lf_user <lanforge> ', default='lanforge')
    parser.add_argument('--lf_passwd', help='--lf_password <lanforge password> ', default='lanforge')

    parser.add_argument('--test_rig', help='--test_rig <test_rig> ', default='lanforge')
    parser.add_argument('--test_bed', help='--test_bed <test_bed> ', default='lanforge')
    parser.add_argument('--test_server', help='--test_server <test_server_ip> , ip of test reports server can be lanforge ip, default set to lanforge ip input')
    parser.add_argument('--test_db', help='--test_db <test_db> sqlite database,', default='lf_test.db')
    parser.add_argument('--upstream_port', help='--upstream_port <1.1.eth2> need to include self and resource', default='1.1.eth2')
    parser.add_argument('--test_timeout', help='--test_timeout 600', default='600')

    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    # logging configuration
    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")


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


    if args.test_server is None:
        _test_server = args.lf_mgr
    else:
        _test_server = args.test_server        
    _file=args.file
    _lf_mgr=args.lf_mgr
    _lf_mgr_port=args.lf_mgr_port
    _lf_user=args.lf_user
    _lf_passwd=args.lf_passwd
    _test_rig=args.test_rig
    _test_bed=args.test_bed
    _test_db=args.test_db
    _upstream_port=args.upstream_port
    _test_timeout=args.test_timeout
    

    rig_json = lf_create_rig_json(_file=_file,
                                  _lf_mgr=_lf_mgr,
                                  _lf_mgr_port=_lf_mgr_port,
                                  _lf_user=_lf_user,
                                  _lf_passwd=_lf_passwd,
                                  _test_rig=_test_rig,
                                  _test_bed=_test_bed,
                                  _test_server=_test_server,
                                  _test_db=_test_db,
                                  _upstream_port=_upstream_port,
                                  _test_timeout=_test_timeout)
    rig_json.create()

    logger.info("created {file}".format(file=_file))


if __name__ == '__main__':
    main()
