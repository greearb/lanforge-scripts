#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_create_dut_json.py

PURPOSE:
     This script will create a lf_dut.json file that is used as a input --json_dut to the lf_check.py script
     This script helps to store the of the information on DUT under use
EXAMPLE:
    # For creating dut.json file according to the DUT present:
    lf_create_dut_json.py --file dut.json --dut_name TIP_AP --dut_hw A1.1 --dut_sw 3.0.0.4.3 --dut_model ESP101
    --dut_serial 128765387 --log_level debug --ssid_idx "ssid_idx==0,SSID_USED==OpenWifi-psk21,SSID_PW_USED==OpenWifi,
    BSSID_TO_USE==00:0a:52:7b:37:fe,SECURITY_USED==wpa2"

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        This will create a file with the name specified in the CLI  [ --json_dut example_name.json ]
        * Helps to store the data related to the DUT being used

STATUS: BETA RELEASE

VERIFIED_ON:   23-MAY-2023,
             Build Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc


INCLUDE_IN_README: False


"""

import argparse
import logging
import importlib
import os
import sys
import traceback

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../../")))

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class lf_create_dut_json():
    def __init__(self,
                 _file,
                 _dut_name,
                 _dut_hw,
                 _dut_sw,
                 _dut_model,
                 _dut_serial,
                 _ssid_idx_dict_dict_str,
                 _dut_upstream_port,
                 _dut_upstream_alias,
                 _dut_database
                 ):
        self.file = _file
        self.dut_name = _dut_name
        self.dut_hw = _dut_hw
        self.dut_sw = _dut_sw
        self.dut_model = _dut_model
        self.dut_serial = _dut_serial
        self.ssid_idx_dict_dict_str = _ssid_idx_dict_dict_str
        self.dut_upstream_port = _dut_upstream_port
        self.dut_upstream_alias = _dut_upstream_alias
        self.dut_database = _dut_database

    # Helper methods
    def create(self):
        file_fd = open(self.file, 'w')
        dut_json = """
{{
    "{file}":{{
        "Notes":[
            "This json file describes device under test run configuration used as input for --dut_json for lf_check.py"

        ]
    }},
    "test_dut":{{
        "DUT_SET_NAME": "DUT_NAME {dut_name}",
        "USE_DUT_NAME": "{dut_name}",
        "DUT_HW":"{dut_hw}",
        "DUT_SW":"{dut_sw}",
        "DUT_MODEL":"{dut_model}",
        "DUT_SERIAL":"{dut_serial}",
        "wireless_network_dict":{{\n{ssid_idx_dict_dict_str} \t\t}},
        "UPSTREAM_PORT":"{dut_upstream_port}",
        "UPSTREAM_ALIAS":"{dut_upstream_alias}",
        "DATABASE_SQLITE":"{dut_database}"
    }}
}}

        """.format(file=self.file, dut_name=self.dut_name, dut_hw=self.dut_hw, dut_sw=self.dut_sw,
                   dut_model=self.dut_model, dut_serial=self.dut_serial,
                   ssid_idx_dict_dict_str=self.ssid_idx_dict_dict_str,
                   dut_upstream_port=self.dut_upstream_port,
                   dut_upstream_alias=self.dut_upstream_alias,
                   dut_database=self.dut_database
                   )

        file_fd.write(dut_json)
        file_fd.close()

# Feature, Sum up the subtests passed/failed from the kpi files for each run, poke those into the database, and generate a kpi graph for them.


def main():
    parser = argparse.ArgumentParser(
        prog='lf_create_dut_json.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_create_dut_json.py creates lf_dut.json file for --json_dut input to lf_check.py 
        The lf_dut.json file contains dut configuration information
        NOTE: cannot have extra blank lines at the end of the json to work properly

            ''',
        description='''\
NAME: lf_create_dut_json.py

PURPOSE:
     This script will create a lf_dut.json file that is used as a input --json_dut to the lf_check.py script
     This script helps to store the of the information on DUT under use
EXAMPLE:
    # For creating dut.json file according to the DUT present:
    lf_create_dut_json.py --file dut.json --dut_name TIP_AP --dut_hw A1.1 --dut_sw 3.0.0.4.3 --dut_model ESP101
    --dut_serial 128765387 --log_level debug --ssid_idx "ssid_idx==0,SSID_USED==OpenWifi-psk21,SSID_PW_USED==OpenWifi,
    BSSID_TO_USE==00:0a:52:7b:37:fe,SECURITY_USED==wpa2"

SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        This will create a file with the name specified in the CLI  [ --json example_name.json ]
        * Helps to store the data related to the DUT being used

STATUS: BETA RELEASE

VERIFIED_ON:   23-MAY-2023,
             Build Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc


INCLUDE_IN_README: False


'''
    )
    parser.add_argument('--file', help='--file lf_dut.json , required', required=True)
    parser.add_argument('--dut_name', help='--dut_name <device under test> required', required=True)
    parser.add_argument('--dut_hw', help='--dut_hw <dut hardware version> ', default='dut_hw')
    parser.add_argument('--dut_sw', help='--dut_sw <dut software version> ', default='dut_sw')
    parser.add_argument('--dut_model', help='--dut_model <dut model> ', default='dut_model')
    parser.add_argument('--dut_serial', help='--dut_serial <dut_serial_num> ', default='123456578')
    parser.add_argument('--dut_upstream_port', help='--dut_upstream_port shelf.resource.<port>  example 1.1.eth3 default eth1',default='1.1.eth2')
    parser.add_argument('--dut_upstream_alias', help='--dut_upstream_alias <port>  example eth3 ', default='eth2')
    parser.add_argument('--dut_database', help='--dut_database <db location>   example ./tools/CT_007_AXE160000_2_5_Gbps_eth1.db default ./tools/DUT_DB',default='./tools/DUT_DB')

    parser.add_argument(
        '--ssid_idx',
        action='append',
        nargs=1,
        required=True,
        help='''
            The ssid_idx is used to enter multiple ssid, ssid password, bssid, security types 

        Example:
        --ssid_idx ssid_idx==0,SSID_USED==<ssid>,SSID_PW_USED==<ssid password>,BSSID_TO_USE==<bssid>,SECURITY_USED==<security>'
        --ssid_idx ssid_idx==1,SSID_USED==<ssid>,SSID_PW_USED==<ssid password>,BSSID_TO_USE==<bssid>,SECURITY_USED==<security>'
        --ssid_idx ssid_idx==2,SSID_USED==<ssid>,SSID_PW_USED==<ssid password>,BSSID_TO_USE==<bssid>,SECURITY_USED==<security>'

            The ssid_idx will be used in the test json,  there can be as many combinations of ssid, ssid passwork , bssid and security used
            The bssid is entered as there are usesers that have the same ssid for 24g, 5g, 6g

            NOTE: SSID_USE , SSID_PW_USED , BSSID_TO_USE, SECUITY_USED are keys used by l    m9f_check.py so that test json files may
                    be reused between test setups and only the dut json needs to change.

            '''
    )
    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    # logging configuration
    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger, optional")

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

    _file = args.file
    _dut_name = args.dut_name
    _dut_hw = args.dut_hw
    _dut_sw = args.dut_sw
    _dut_model = args.dut_model
    _dut_serial = args.dut_serial
    _ssid_idx = args.ssid_idx
    _dut_upstream_port = args.dut_upstream_port
    _dut_upstream_alias = args.dut_upstream_alias
    _dut_database = args.dut_database

    # create wifi dictionary, ssid indx
    ssid_idx_dict_dict_str = ""

    logger.debug("_ssid_idx len {len_ssid_idx}".format(len_ssid_idx=len(_ssid_idx)))

    ssid_idx_lengh = len(_ssid_idx)
    for ssid_idx_ in _ssid_idx:
        ssid_idx_keys = ['ssid_idx', 'SSID_USED', 'SSID_PW_USED', 'BSSID_TO_USE', 'SECURITY_USED']
        try:
            _ssid_idx_dict_element = dict(
                map(
                    lambda x: x.split('=='),
                    str(ssid_idx_).replace(
                        '"',
                        '').replace(
                        '[',
                        '').replace(
                        ']',
                        '').replace(
                        "'",
                        "").replace(
                        ",",
                        " ").split()))
        except  Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.error(
                "Check the format of the --ssid_idx , verify there is == between keys and values in ssid_idx {ssid_idx_}".format(
                    ssid_idx_=ssid_idx_))
            exit(1)

        _ssid_idx_dict_element_keys = list(_ssid_idx_dict_element)

        if len(ssid_idx_keys) != len(_ssid_idx_dict_element_keys):
            logger.critical(
                "missing ssid_idx keys  , keys needed: {needed} keys input {input}".format(needed=ssid_idx_keys,
                                                                                           input=_ssid_idx_dict_element))
        for key in _ssid_idx_dict_element_keys:
            if key not in ssid_idx_keys:
                logger.critical(
                    "missing ssid_idx keys, for the {key}, all of the following need to be present {ssid_idx_keys} ".format(
                        key=key, ssid_idx_keys=ssid_idx_keys))

                exit(1)

        # create the index string with index
        ssid_idx = _ssid_idx_dict_element['ssid_idx']
        ssid_idx_str = "\"ssid_idx={idx}\":".format(idx=_ssid_idx_dict_element['ssid_idx'])

        # convert a dictionary to a string
        ssid_idx_dict_element_str = str(_ssid_idx_dict_element)  # .strip() # may not needed
        logger.debug("ssid_idx_dict_element {dict}".format(dict=_ssid_idx_dict_element))

        # convert string to json
        ssid_idx_dict_element_str = str(_ssid_idx_dict_element).replace(
            '\'',
            '\"'
        )
        logger.debug("ssid_idx_dict_element_str {dict}".format(dict=ssid_idx_dict_element_str))

        if ((ssid_idx_lengh - 1) != int(ssid_idx)):
            ssid_idx_dict_dict_str += "\t\t\t" + ssid_idx_str + ssid_idx_dict_element_str + ",\n"
        else:
            # last element does not have comma at the end
            ssid_idx_dict_dict_str += "\t\t\t" + ssid_idx_str + ssid_idx_dict_element_str + "\n"

    dut_json = lf_create_dut_json(_file=_file,
                                  _dut_name=_dut_name,
                                  _dut_hw=_dut_hw,
                                  _dut_sw=_dut_sw,
                                  _dut_model=_dut_model,
                                  _dut_serial=_dut_serial,
                                  _ssid_idx_dict_dict_str=ssid_idx_dict_dict_str,
                                  _dut_upstream_port=_dut_upstream_port,
                                  _dut_upstream_alias=_dut_upstream_alias,
                                  _dut_database=_dut_database)
    dut_json.create()

    logger.info("Device under test json created {file}".format(file=_file))


if __name__ == '__main__':
    main()
