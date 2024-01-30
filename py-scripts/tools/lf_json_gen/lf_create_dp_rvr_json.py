#!/usr/bin/env python3
'''
NAME: lf_create_dp_rvr_json.py

PURPOSE:
     This script will create a lf_dp_rvr.json file that is used as a input --json_test to the lf_check.py script
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



class lf_create_dp_rvr_json():
    def __init__(self,
                _suite_type,
                 _file_2g,
                 _file_5g,
                 _file_6g,
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
                 _lf_dp_rvr_use_qa_var,
                 _lf_dp_rvr_use_inspect_var,
                 _lf_dp_rvr_duration_combobox,
                 _lf_dp_rvr_traffic_type_combobox,
                 _lf_dp_rvr_dut_traffic_direction_combobox,
                 _lf_dp_rvr_pkt_size_combobox,
                 _lf_dp_rvr_pkt_size_custom_combobox,
                 _lf_dp_rvr_download_speed_combobox,
                 _lf_dp_rvr_upload_speed_combobox,
                 _lf_dp_rvr_attenuator_combobox,
                 _lf_dp_rvr_attenuation_2g_combobox,
                 _lf_dp_rvr_attenuation_5g_combobox,
                 _lf_dp_rvr_attenuation_6g_combobox,
                 _lf_radio_2g,
                 _lf_radio_5g,
                 _lf_radio_6g
                 ):
        self.suite_type = _suite_type
        self.suite_band = ""
        self.lf_dp_rvr_use_qa_var = _lf_dp_rvr_use_qa_var
        self.lf_dp_rvr_use_inspect_var = _lf_dp_rvr_use_inspect_var
        self.use_radio_dict = _use_radio_dict
        self.radio_dict = _radio_dict
        self.radio_dict_size = len(self.radio_dict)
        self.radio_type_dict = _radio_type_dict
        self.radio_max_sta_dict = _radio_max_sta_dict
        self.use_radio_var_dict = _use_radio_var_dict
        self.radio_count = _radio_count
        self.radio_batch_dict = _radio_batch_dict
        self.lf_dp_rvr_use_qa_var = _lf_dp_rvr_use_qa_var
        self.lf_dp_rvr_use_inspect_var = _lf_dp_rvr_use_inspect_var

        # configuration 
        self.lf_dp_rvr_duration_combobox = _lf_dp_rvr_duration_combobox
        self.lf_dp_rvr_traffic_type_combobox = _lf_dp_rvr_traffic_type_combobox 
        self.lf_dp_rvr_dut_traffic_direction_combobox = _lf_dp_rvr_dut_traffic_direction_combobox
        self.lf_dp_rvr_pkt_size_combobox = _lf_dp_rvr_pkt_size_combobox
        self.lf_dp_rvr_pkt_custom_size_combobox = _lf_dp_rvr_pkt_size_custom_combobox
        self.lf_dp_rvr_download_speed_combobox = _lf_dp_rvr_download_speed_combobox
        self.lf_dp_rvr_upload_speed_combobox = _lf_dp_rvr_upload_speed_combobox
        self.lf_dp_rvr_attenuator_combobox = _lf_dp_rvr_attenuator_combobox
        self.lf_dp_rvr_attenuation_2g_combobox = _lf_dp_rvr_attenuation_2g_combobox
        self.lf_dp_rvr_attenuation_5g_combobox = _lf_dp_rvr_attenuation_5g_combobox
        self.lf_dp_rvr_attenuation_6g_combobox = _lf_dp_rvr_attenuation_6g_combobox
        self.lf_dp_rvr_use_qa_var = _lf_dp_rvr_use_qa_var
        self.lf_dp_rvr_use_inspect_var = _lf_dp_rvr_use_inspect_var

        self.lf_radio_2g = _lf_radio_2g
        self.lf_radio_5g = _lf_radio_5g
        self.lf_radio_6g = _lf_radio_6g

        self.suite_2d_radios = _suite_radios_2g
        self.suite_5g_radios = _suite_radios_5g
        self.suite_6g_radios = _suite_radios_6g

        self.file_2g = ""
        self.file_5g = ""
        self.file_6g = ""


        self.use_radio_2g_var_dict = _use_radio_2g_var_dict
        self.use_radio_5g_var_dict = _use_radio_5g_var_dict
        self.use_radio_6g_var_dict = _use_radio_6g_var_dict

        self.suite_radios_2g = _suite_radios_2g
        self.suite_radios_5g =  _suite_radios_5g
        self.suite_radios_6g =  _suite_radios_6g

        self.suite_test_name_2g_dict = _suite_test_name_2g_dict
        self.suite_test_name_5g_dict = _suite_test_name_5g_dict
        self.suite_test_name_6g_dict = _suite_test_name_6g_dict

        self.dp_rvr_band_json = ""
        self.dp_rvr_2g_json = ""
        self.dp_rvr_5g_json = ""
        self.dp_rvr_6g_json = ""

        self.last_2g_radio = 0

        # generic defines
        self.use_radio_band_var_dict = {}
        self.suite_radios_band = ""
        self.last_band_radio = 0

    def get_file_2g(self):
        return self.file_2g

    def get_file_5g(self):
        return self.file_5g

    def get_file_6g(self):
        return self.file_6g

    # Helper methods
    def create_suite(self):

        traffic_direction = ''
        lf_dp_rvr_dut_traffic_direction = self.lf_dp_rvr_dut_traffic_direction_combobox.get()
        if "Transmit" in lf_dp_rvr_dut_traffic_direction:
            traffic_direction += "_tx"
        if "Receive" in lf_dp_rvr_dut_traffic_direction:
            traffic_direction += "_rx"

        if self.suite_type == "dp":
            command = "lf_dataplane_test.py"
            prefix = self.suite_type.upper()
            notes_title = "ct_dp_tests_scripts"
            if self.test_suite_band == "2g":
                self.suite_radios_2g = "ct_perf_dp_2g" + self.suite_radios_2g + traffic_direction
            elif self.test_suite_band == '5g':                
                self.suite_radios_5g = "ct_perf_dp_5g" + self.suite_radios_5g + traffic_direction
            elif self.test_suite_band == '6g':
                self.suite_radios_6g = "ct_perf_dp_6g" + self.suite_radios_6g + traffic_direction

        elif self.suite_type == "rvr":
            command = "lf_rvr_test.py"
            prefix = self.suite_type.upper()
            notes_title = "ct_rvr_tests_scripts"
            if self.test_suite_band == "2g":
                self.suite_radios_2g = "ct_perf_rvr_2g" + self.suite_radios_2g + traffic_direction
            elif self.test_suite_band == '5g':                
                self.suite_radios_5g = "ct_perf_rvr_5g" + self.suite_radios_5g + traffic_direction
            elif self.test_suite_band == '6g':
                self.suite_radios_6g = "ct_perf_rvr_6g" + self.suite_radios_6g + traffic_direction

        # this should be an error default to Dataplane
        else:
            command = "lf_dataplane_test.py"
            notes_title = "ct_tests_scripts"

        if self.test_suite_band == "2g":
            self.file_2g = self.suite_radios_2g + ".json"
            file_band_fd = open(self.file_2g, 'w')
            self.use_radio_band_var_dict = self.use_radio_2g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_2g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_2g
            dut_radio = self.lf_radio_2g
            lf_dp_rvr_attenuation = self.lf_dp_rvr_attenuation_2g_combobox.get()


        elif self.test_suite_band == "5g":
            self.file_5g = self.suite_radios_5g + ".json"
            file_band_fd = open(self.file_5g, 'w')
            self.use_radio_band_var_dict = self.use_radio_5g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_5g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_5g
            dut_radio = self.lf_radio_5g
            lf_dp_rvr_attenuation = self.lf_dp_rvr_attenuation_5g_combobox.get()


        elif self.test_suite_band == "6g":
            self.file_6g = self.suite_radios_6g + ".json"
            file_band_fd = open(self.file_6g, 'w')
            self.use_radio_band_var_dict = self.use_radio_6g_var_dict
            self.suite_test_name_band_dict = self.suite_test_name_6g_dict
            band = self.test_suite_band.upper()
            self.suite_radios_band = self.suite_radios_6g
            dut_radio = self.lf_radio_6g
            lf_dp_rvr_attenuation = self.lf_dp_rvr_attenuation_6g_combobox.get()


        # configuration 
        lf_dp_rvr_duration = self.lf_dp_rvr_duration_combobox.get().split(' ', 1)[0]
        lf_dp_rvr_traffic_type = self.lf_dp_rvr_traffic_type_combobox.get()
        lf_dp_rvr_dut_traffic_direction = self.lf_dp_rvr_dut_traffic_direction_combobox.get()
        lf_dp_rvr_pkt_size = self.lf_dp_rvr_pkt_size_combobox.get()
        lf_dp_rvr_pkt_custom_size = self.lf_dp_rvr_pkt_custom_size_combobox.get()
        lf_dp_rvr_download_speed = self.lf_dp_rvr_download_speed_combobox.get()
        lf_dp_rvr_upload_speed = self.lf_dp_rvr_upload_speed_combobox.get()
        lf_dp_rvr_attenuator = self.lf_dp_rvr_attenuator_combobox.get()

        self.dp_rvr_band_json = """
{{
    "{notes}":{{
        "Notes":[
            "This json file describes tests to be run by LANforge system",
            "When doing a create_chamberview.py --create_scenario <name> ",
            "has no correlation to the --instance_name , instance name is used ",
            "as a unique identifier for tha chamber-view test run"
        ]  
    }},
    "test_suites":{{
    """.format(notes=notes_title)
        self.dp_rvr_band_json += """
        "{test_suite}":{{
    """.format(test_suite=self.suite_radios_band)

        
        # find the last radio to include in test
        count_band_radios = 0
        for radio in range(0,self.radio_dict_size):
            if self.use_radio_var_dict[radio].get() == "Use" and self.use_radio_band_var_dict[radio].get() == "Use":
                self.last_band_radio = radio
                count_band_radios += 1

        if count_band_radios > 0:

            for radio in range(0,self.radio_dict_size):
                if self.use_radio_var_dict[radio].get() == "Use" and self.use_radio_band_var_dict[radio].get() == "Use":
                    dp_rvr_test_name = str(self.suite_test_name_band_dict[radio].get()) + f"_{band}_W{radio}" + f"{traffic_direction}"
                    dp_rvr_batch_size = str(self.radio_batch_dict[radio].get())
                    dp_rvr_sta_max = dp_rvr_batch_size.rsplit(',', 1)
                    if len(dp_rvr_sta_max) == 1:
                        dp_rvr_sta_max_int = int(dp_rvr_sta_max[0])
                    else:                        
                        dp_rvr_sta_max_int = int(dp_rvr_sta_max[1])
                    attenuator = ''
                    attenuation = ''
                    if lf_dp_rvr_attenuator != "" and lf_dp_rvr_attenuation != "":
                        attenuator = f"""--raw_line 'attenuator: {lf_dp_rvr_attenuator}'"""
                        attenuation = f"""--raw_line 'attenuations: {lf_dp_rvr_attenuation}'"""
                    else:
                        attenuation = ''
                    self.dp_rvr_band_json += f"""
            "CC_DUT_{dp_rvr_test_name}":{{
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
            "CC_{dp_rvr_test_name}":{{
                "enabled":"TRUE",
                "load_db":"skip",
                "command":"create_chamberview.py",
                "args":"",
                "args_list":[
                    " --lfmgr LF_MGR_IP --port LF_MGR_PORT --delete_scenario",
                    " --create_scenario {dp_rvr_test_name} ",
                    " --raw_line \\"profile_link 1.1 STA-AUTO {dp_rvr_sta_max_int} 'DUT: USE_DUT_NAME {dut_radio}' NA wiphy{radio},AUTO -1 NA\\" ",
                    " --raw_line \\"profile_link 1.1 upstream 1 'DUT: USE_DUT_NAME LAN'  NA UPSTREAM_ALIAS,AUTO -1 NA\\""
                ]
            }},
            "{prefix}_{dp_rvr_test_name}":{{
                "enabled":"TRUE",
                "timeout":"600",
                "iterations":"1",
                "load_db":"skip",
                "command":"{command}",
                "args":"",
                "args_list":[
                    " --mgr LF_MGR_IP --port LF_MGR_PORT --lf_user LF_MGR_USER --lf_password LF_MGR_PASS --instance_name {dp_rvr_test_name}",
                    " --config_name test_con --upstream UPSTREAM_PORT  --dut USE_DUT_NAME --duration {lf_dp_rvr_duration} --station 1.1.wlan{radio}",
                    " --download_speed 85% --upload_speed 0 --raw_line 'pkts: {lf_dp_rvr_pkt_size}' ",
                    " --raw_line 'cust_pkt_sz: {lf_dp_rvr_pkt_custom_size}' ",
                    " --raw_line 'directions: {lf_dp_rvr_dut_traffic_direction}' --raw_line 'traffic_types: {lf_dp_rvr_traffic_type}' --raw_line 'bandw_options: AUTO'",
                    " --raw_line 'spatial_streams: AUTO' --pull_report --local_lf_report_dir REPORT_PATH --test_tag '{dp_rvr_test_name}'",
                    " {attenuator}",
                    " {attenuation}",
                    " --raw_line 'attenuator_mod: 0xf'  ",
                    " --test_rig TEST_RIG ",
                    " --set DUT_SET_NAME",
                    " --verbosity 11"
                ]
            }}
            """
                    if radio != self.last_band_radio:
                        self.dp_rvr_band_json += ""","""

                    if radio == self.last_band_radio:
                        if self.lf_dp_rvr_use_qa_var.get() == "Use":
                            self.dp_rvr_band_json +=""",
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
                        if self.lf_dp_rvr_use_inspect_var.get() == "Use":
                            self.dp_rvr_band_json +=""",            
            "lf_inspect":{
                "enabled":"TRUE",
                "timeout":"600",
                "load_db":"skip",
                "command":"./tools/lf_inspect.py",
                "args":"",
                "args_list":[
                    " --path REPORT_PATH --database DATABASE_SQLITE --test_suite  TEST_SUITE --db_index 0,1"
                ]
            }"""

        self.dp_rvr_band_json += """ 
        }
    } 
}    
    """

            
        file_band_fd.write(self.dp_rvr_band_json)
        file_band_fd.close()



def main():

    parser = argparse.ArgumentParser(
        prog='lf_create_dp_rvr_json.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_create_dp_rvr_json.py creates
        NOTE: cannot have extra blank lines at the end of the json to work properly

            ''',
        description='''\
NAME: lf_create_dp_rvr_json.py

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
          Copyright 2023 Candela Technologies Inc

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
