#!/usr/bin/env python3
""" 
NAME: lf_cli_to_launchjson.py

PURPOSE: To convert cli command into launch.json format
    
EXAMPLE:
    Use './lf_cli_to_launchjson.py --help' to see command line usage and options

    ./lf_cli_to_launchjson.py --cli 

SCRIPT_CLASSIFICATION: Tool

SCRIPT_CATEGORIES: Creation

NOTES: 
Enter the cli of the script as an input to the script.  --cli "<cli of particular script>"
Eg: --cli '--lfmgr 192.168.100.116 --local_lf_report_dir /home/lanforge/html-reports/ct-us-001/2023-05-21-03-00-06_lf_check_suite_wc_dp_nightly --test_duration 15s --polling_interval 5s --upstream_port 1.1.eth2   --radio 'radio==wiphy4,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy5,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy6,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy7,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)' --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000 --test_rig CT-US-001 --test_tag 'test_l3' --dut_model_num  ASUSRT-AX88U --dut_sw_version 3.0.0.4.386_44266 --dut_hw_version 1.0 --dut_serial_num 12345678" '

STATUS: Functional

VERIFIED_ON:
Working date : 12/07/2023
Build version: 5.4.6
Kernel version: 6.2.16+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

     """

import sys
import os
import argparse
import json

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

class clitojson():
    def __init__(self,

                cli_list=["--mgr 192.168.200.147 --port 8080 --lf_user lanforge --lf_password lanforge --instance_name scenario_wpa2_wc --upstream 1.1.eth1 --batch_size 1,3,5 --loop_iter 1 --protocol TCP-IPv4 --duration 20000 --download_rate 10Mbps --upload_rate 10Mbps --pull_report --delete_old_scenario --local_lf_report_dir /home/lanforge/html-scripts --test_tag WCT_MTK7915_W1_5G_40_UDP_BD_AT --test_rig TEST_RIG --set DUT_SET_NAME"],
                list= [],
                length_of_cli=[]
                 
                 ):

        self.cli_list=cli_list
        self.list1=list
        self.length_of_cli=length_of_cli
        print(self.cli_list)

    def split_cli(self):
        l1=self.cli_list.split(' ')
        self.length_of_cli.append(len(l1))

        for i in range(self.length_of_cli[0]):
            if i+1 == self.length_of_cli[0]:
                break

        for j in range(len(l1)):
            if ("--" or ","  in l1[j]) :
                if ("--" or ","  in l1[j+1]):
                    self.list1.append(l1[j])
                else:
                    self.list1.append(l1[j] +" "+ l1[j+1])

        self.json_dump()

    def json_dump(self):
        s='args_list'
        json_list=json.dumps(self.list1)
        print(s,json_list)
        dict1={s:self.list1}
        out_file=open("test1.json","w")
        json.dump(dict1,out_file,indent=4)
        out_file.close()
    

def main():
    parser = argparse.ArgumentParser(
        prog='lf_cli_to_launchjson.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description= """ 

NAME: lf_cli_to_launchjson.py

PURPOSE: To convert cli command into launch.json format
    
EXAMPLE:
    Use './lf_cli_to_launchjson.py --help' to see command line usage and options

    ./lf_cli_to_launchjson.py --cli 

SCRIPT_CLASSIFICATION: Tool

SCRIPT_CATEGORIES: Creation

NOTES: 
Enter the cli of the script as an input to the script. --cli "<cli of particular script>"
Eg: --cli '--lfmgr 192.168.100.116 --local_lf_report_dir /home/lanforge/html-reports/ct-us-001/2023-05-21-03-00-06_lf_check_suite_wc_dp_nightly --test_duration 15s --polling_interval 5s --upstream_port 1.1.eth2   --radio 'radio==wiphy4,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy5,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy6,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)'  --radio 'radio==wiphy7,stations==1,ssid==asus11ax-2,ssid_pw==hello123,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable|wpa2_enable|80211u_enable|create_admin_down)' --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000 --test_rig CT-US-001 --test_tag 'test_l3' --dut_model_num  ASUSRT-AX88U --dut_sw_version 3.0.0.4.386_44266 --dut_hw_version 1.0 --dut_serial_num 12345678" '

STATUS: Functional

VERIFIED_ON:
Working date : 12/07/2023
Build version: 5.4.6
Kernel version: 6.2.16+

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

     """
    )

    parser.add_argument("--cli",type=str, help="enter the csv file path", required=True)
    
    args = parser.parse_args() 

    conversion=clitojson(cli_list= args.cli
                        )
    
    conversion.split_cli()

if __name__ == "__main__":
    main()


