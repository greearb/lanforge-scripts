#!/usr/bin/env python3
# flake8: noqa
'''
NAME: lf_create_ap_auto_json.py

PURPOSE:
     This script will create a lf_wc.json file that is used as a input --json_test to the lf_check.py script
     This script helps to store the of the information on LANforge
EXAMPLE:
    # For creating wifi capacity test json file according to the Tests present:



SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:

STATUS: Development

VERIFIED_ON:

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc


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


class lf_create_ap_auto_json():
    def __init__(self,
                 _file_2g,
                 _file_5g,
                 _file_6g,
                 _ap_auto_duration,
                 _use_radio_dict,
                 _radio_dict,
                 _radio_type_dict,
                 _radio_max_sta_dict,
                 _use_radio_var_dict,
                 _use_radio_2g_var_dict,
                 _use_radio_5g_var_dict,
                 _use_radio_6g_var_dict,
                 _suite_radios_2g,
                 _suite_radios_5g,
                 _suite_radios_6g,
                 _suite_test_name_2g_dict,
                 _suite_test_name_5g_dict,
                 _suite_test_name_6g_dict,
                 _radio_count,
                 _radio_batch_dict,
                 _lf_ap_auto_basic_client_connectivity,
                 _lf_ap_auto_multi_band_performance,
                 _lf_ap_auto_multi_station_throughput_vs_pkt_size,
                 _lf_ap_auto_stability,
                 _lf_ap_auto_channel_switching_test,
                 _lf_ap_auto_throughput_vs_pkt_size,
                 _lf_ap_auto_capacity,
                 _lf_ap_auto_band_steering,
                 _lf_ap_auto_long_term,
                 _lf_ap_auto_use_qa_var,
                 _lf_ap_auto_use_inspect_var
                 ):
        self.test_suite_band = ""
        self.use_radio_dict = _use_radio_dict
        self.radio_dict = _radio_dict
        self.radio_dict_size = len(self.radio_dict)
        self.radio_type_dict = _radio_type_dict
        self.radio_max_sta_dict = _radio_max_sta_dict
        self.use_radio_var_dict = _use_radio_var_dict
        self.radio_count = _radio_count
        self.radio_batch_dict = _radio_batch_dict

        self.lf_ap_auto_basic_client_connectivity = _lf_ap_auto_basic_client_connectivity
        self.lf_ap_auto_multi_band_performance = _lf_ap_auto_multi_band_performance
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size = _lf_ap_auto_multi_station_throughput_vs_pkt_size
        self.lf_ap_auto_stability = _lf_ap_auto_stability
        self.lf_ap_auto_channel_switching_test = _lf_ap_auto_channel_switching_test
        self.lf_ap_auto_throughput_vs_pkt_size = _lf_ap_auto_throughput_vs_pkt_size
        self.lf_ap_auto_capacity = _lf_ap_auto_capacity
        self.lf_ap_auto_band_steering = _lf_ap_auto_band_steering
        self.lf_ap_auto_long_term = _lf_ap_auto_long_term

        self.lf_ap_auto_use_qa_var = _lf_ap_auto_use_qa_var
        self.lf_ap_auto_use_inspect_var = _lf_ap_auto_use_inspect_var
        self.radio_index = ""

        # TODO Future copy generated file to alternate file (low priority until requeste)

        self.file_2g = "ct_perf_ap_auto_2g" + _suite_radios_2g + ".json"
        self.file_5g = "ct_perf_ap_auto_5g" + _suite_radios_5g + ".json"
        self.file_6g = "ct_perf_ap_auto_6g" + _suite_radios_6g + ".json"

        if _ap_auto_duration == "":
            self.ap_auto_duration = '20000'
        else:
            self.ap_auto_duration = _ap_auto_duration

        self.use_radio_2g_var_dict = _use_radio_2g_var_dict
        self.use_radio_5g_var_dict = _use_radio_5g_var_dict
        self.use_radio_6g_var_dict = _use_radio_6g_var_dict

        self.suite_radios_2g = "ct_perf_ap_auto_2g" + _suite_radios_2g
        self.suite_radios_5g = "ct_perf_ap_auto_5g" + _suite_radios_5g
        self.suite_radios_6g = "ct_perf_ap_auto_6g" + _suite_radios_6g

        self.suite_test_name_2g_dict = _suite_test_name_2g_dict
        self.suite_test_name_5g_dict = _suite_test_name_5g_dict
        self.suite_test_name_6g_dict = _suite_test_name_6g_dict

        self.ap_auto_2g_json = ""
        self.ap_auto_5g_json = ""
        self.ap_auto_6g_json = ""

        self.last_2g_radio = 0

    def get_file_2g(self):
        return self.file_2g

    def get_file_5g(self):
        return self.file_5g

    def get_file_6g(self):
        return self.file_6g

    # Helper methods

    def create_suite(self):

        if self.test_suite_band == "2g":
            file_band_fd = open(self.file_2g, 'w')
            self.use_radio_band_var_dict = self.use_radio_2g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_2g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_2g
            self.radio_index = "Radio-1"
            radio_index = self.radio_index

        elif self.test_suite_band == "5g":
            file_band_fd = open(self.file_5g, 'w')
            self.use_radio_band_var_dict = self.use_radio_5g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_5g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_5g
            self.radio_index = "Radio-2"
            radio_index = self.radio_index

        elif self.test_suite_band == "6g":
            file_band_fd = open(self.file_6g, 'w')
            self.use_radio_band_var_dict = self.use_radio_6g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_6g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_6g
            self.radio_index = "Radio-3"
            radio_index = self.radio_index

        self.ap_auto_band_json = """
{{
    "{wifi}":{{
        "Notes":[
            "This json file describes tests to be run by LANforge system",
            "When doing a create_chamberview.py --create_scenario <name> ",
            "has no correlation to the --instance_name , instance name is used ",
            "as a unique identifier for tha chamber-view test run"
        ]
    }},
    "test_suites":{{
    """.format(wifi="ct_ap_auto_tests_scripts")
        self.ap_auto_band_json += """
        "{test_suite}":{{
    """.format(test_suite=self.suite_radios_band)

        # find the last radio to include in test
        count_band_radios = 0
        for radio in range(0, self.radio_dict_size):
            if self.use_radio_var_dict[radio].get() == "Use" and self.use_radio_band_var_dict[radio].get() == "Use":
                self.last_band_radio = radio
                count_band_radios += 1

        if count_band_radios > 0:

            for radio in range(0, self.radio_dict_size):
                if self.use_radio_var_dict[radio].get() == "Use" and self.use_radio_band_var_dict[radio].get() == "Use":
                    ap_auto_test_name = str(self.suite_test_name_band_dict[radio].get()) + f"_{band}_W{radio}"
                    ap_auto_batch_size = str(self.radio_batch_dict[radio].get())
                    ap_auto_sta_max = ap_auto_batch_size.rsplit(',', 1)
                    if len(ap_auto_sta_max) == 1:
                        ap_auto_sta_max_int = int(ap_auto_sta_max[0])
                    else:
                        ap_auto_sta_max_int = int(ap_auto_sta_max[1])
                    ap_auto_duration = self.ap_auto_duration
                    self.ap_auto_band_json += f"""
            "CC_DUT_{ap_auto_test_name}":{{
                "enabled":"TRUE",
                "load_db":"skip",
                "command":"create_chamberview_dut.py",
                "args":"",
                "args_list":[
                    " --lfmgr LF_MGR_IP --port LF_MGR_PORT --dut_name USE_DUT_NAME",
                    " --ssid 'ssid_idx=0 ssid=SSID_USED security=SECURITY_USED password=SSID_PW_USED bssid=BSSID_TO_USE'",
                    " --ssid 'ssid_idx=1 ssid=SSID_USED security=SECURITY_USED password=SSID_PW_USED bssid=BSSID_TO_USE'",
                    " --ssid 'ssid_idx=2 ssid=SSID_USED security=SECURITY_USED password=SSID_PW_USED bssid=BSSID_TO_USE'",
                    " --sw_version DUT_SW --hw_version DUT_HW --serial_num DUT_SERIAL --model_num USE_DUT_NAME",
                    " --dut_flag DHCPD-LAN"
                ]
                }},
            "CC_{ap_auto_test_name}":{{
                "enabled":"TRUE",
                "load_db":"skip",
                "command":"create_chamberview.py",
                "args":"",
                "args_list":[
                    " --lfmgr LF_MGR_IP --port LF_MGR_PORT --delete_scenario",
                    " --create_scenario {ap_auto_test_name} ",
                    " --raw_line \\"profile_link 1.1 STA-AUTO {ap_auto_sta_max_int} 'DUT: USE_DUT_NAME {radio_index}' NA wiphy{radio},AUTO -1 NA\\" ",
                    " --raw_line \\"profile_link 1.1 upstream 1 'DUT: USE_DUT_NAME LAN'  NA UPSTREAM_ALIAS,AUTO -1 NA\\""
                ]
            }},
            "ap_auto_{ap_auto_test_name}":{{
                "enabled":"TRUE",
                "timeout":"600",
                "iterations":"1",
                "load_db":"skip",
                "command":"lf_ap_auto_test.py",
                "args":"",
                "args_list":[
                    " --mgr LF_MGR_IP --port LF_MGR_PORT --lf_user LF_MGR_USER --lf_password LF_MGR_PASS --instance_name {ap_auto_test_name}",
                    " --upstream UPSTREAM_PORT --batch_size {ap_auto_batch_size} --loop_iter 1 --protocol UDP-IPv4 --duration {ap_auto_duration}",
                    " use_ssid_idx=0 --dut2_0 'USE_DUT_NAME lanforge BSSID_TO_USE (1)'",
                    " use_ssid_idx=1 --dut5_0 'USE_DUT_NAME lanforge BSSID_TO_USE (2)'",
                    " --max_stations_2 4 --max_stations_5 8 --max_stations_dual 1",
                    " --radio2 1.1.wiphy4 --radio2 1.1.wiphy5 --radio2 1.1.wiphy6 --radio2 1.1.wiphy7",
                    " --radio5 1.1.wiphy0 --radio5 1.1.wiphy1 --radio5 1.1.wiphy2 --radio5 1.1.wiphy3 --radio5 1.1.wiphy4 --radio5 1.1.wiphy5 --radio5 1.1.wiphy6 --radio5 1.1.wiphy7",
                    " --set 'Basic Client Connectivity' 0",
                    " --set 'Multi Band Performance' 0",
                    " --set 'Stability' 1",
                    " --set 'Multi-Station Throughput vs Pkt Size'  0,",
                    " --set 'Throughput vs Pkt Size' 0",
                    " --set 'Capacity' 0",
                    " --set 'Band-Steering' 0",
                    " --set 'Skip 2.4Ghz Tests' 0",
                    " --raw_line 'cx_psk_thresh: 500'",
                    " --pull_report --local_lf_report_dir REPORT_PATH --test_tag '{ap_auto_test_name}'",
                    " --test_rig TEST_RIG ",
                    " --set DUT_SET_NAME",
                    " --verbosity 11"
                ]
            }}
            """
                    if radio != self.last_band_radio:
                        self.ap_auto_band_json += ""","""

                    if radio == self.last_band_radio:
                        if self.lf_ap_auto_use_qa_var.get() == "Use":
                            self.ap_auto_band_json += """,
            "lf_qa":{
                "enabled":"TRUE",
                "timeout":"600",
                "load_db":"skip",
                "command":"./tools/lf_qa.py",
                "args":"",
                "args_list":[
                    " --server TEST_SERVER --path REPORT_PATH --store --png --database DATABASE_SQLITE --test_suite  TEST_SUITE"
                ]
            }"""
                        if self.lf_ap_auto_use_inspect_var.get() == "Use":
                            self.ap_auto_band_json += """,
            "lf_inspect":{
                "enabled":"TRUE",
                "timeout":"600",
                "load_db":"skip",
                "command":"./tools/lf_inspect.py",
                "args":"",
                "args_list":[
                    " --path REPORT_PATH --database DATABASE_SQLITE --test_suite  TEST_SUITE --db_index 1,0"
                ]
            }"""
        self.ap_auto_band_json += """
        }
    }
}
    """

        file_band_fd.write(self.ap_auto_band_json)
        file_band_fd.close()


def main():

    parser = argparse.ArgumentParser(
        prog='lf_create_ap_auto_json.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_create_ap_auto_json.py creates
        NOTE: cannot have extra blank lines at the end of the json to work properly

            ''',
        description='''\
NAME: lf_create_ap_auto_json.py

PURPOSE:
EXAMPLE:


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
          Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: False
''')

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


if __name__ == '__main__':
    main()
