#!/usr/bin/env python3
"""
NAME: lf_rssi_check.py

PURPOSE: Validate RSSI for specific radios


EXAMPLE:
    Usage something like:  rssi_check.py --channels “6 36” --nss “1 2 3 4” --bw “20 40 80” --vap 1.1.vap0 --stas “1.2.wlan0 1.2.wlan1” --attenuator 1.1.xxxx --attenuation_step 1  --step_duration 
    Skip bw that does not match selected channels.


Implementation should be something like:
Select LF VAP on one system
Bring up STA on other radios on second system.
Start 1Mbps bi-directional UDP traffic between STA(s) and the AP.
Ensure report-timer on stations is 1 second for prompt RSSI updates.
for selected channels
  for selected bandwidths
   for selected nss
     Set VAP to selected mode.  Gracefully skip invalid modes (80Mhz on 2.4, for instance).
     Wait until all STAs connect.
     for attenuation 0 until all STAs are disconnected
       wait 5 seconds
       for each stations
         If STA is disconnected, then do not record RSSI.  Else record RSSI.
         Record theoretical RSSI (txpower minus calibrated path-loss minus attenuation)

 


NOTES:

COPYRIGHT:
Copyright 2021 Candela Technologies Inc

INCLUDE_IN_README
"""

import subprocess
import sys
import os
import importlib
import argparse
import time
import logging

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test

create_chamberview = importlib.import_module("py-scripts.create_chamberview")
create_chamber = create_chamberview.CreateChamberview

add_profile = importlib.import_module("py-scripts.lf_add_profile")
lf_add_profile = add_profile.lf_add_profile

cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
set_port = importlib.import_module("py-json.LANforge.set_port")

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFRequest = importlib.import_module("py-json.LANforge.LFRequest")

ipvt = importlib.import_module("py-scripts.test_ip_variable_time")
IPVariableTime = ipvt.IPVariableTime

logger = logging.getLogger(__name__)



class lf_rssi_check(cv_test):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 lf_report_dir=None,
                 debug_=False,
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)


        pass

    def add_vap_policy(self, scenario_name="Automation", radio="1.1.wiphy0", frequency="-1",name=None, vap_ssid=None, vap_passwd="[BLANK]", vap_security=None):

        profile = lf_add_profile(lf_mgr=self.lfclient_host,
                                 lf_port=self.lf_port,
                                 lf_user=self.lf_user,
                                 lf_passwd=self.lf_passwd,
                                 )


        profile.add_profile(
            _antenna=None,  # Antenna count for this profile.
            _bandwidth=None,  # 0 (auto), 20, 40, 80 or 160
            _eap_id=None,  # EAP Identifier
            _flags_mask=None,  # Specify what flags to set.
            _freq=frequency,  # WiFi frequency to be used, 0 means default.
            _instance_count=1,  # Number of devices (stations, vdevs, etc)
            _mac_pattern=None,  # Optional MAC-Address pattern, for instance: xx:xx:xx:*:*:xx
            _name=scenario_name,  # Profile Name. [R]
            _passwd=vap_pawd,  # WiFi Password to be used (AP Mode), [BLANK] means no password.
            _profile_flags="0x1009",  # Flags for this profile, see above.
            _profile_type="routed_ap",  # Profile type: See above. [W]
            _ssid=vap_ssid,  # WiFi SSID to be used, [BLANK] means any.
            _vid=None,  # Vlan-ID (only valid for vlan profiles).
            _wifi_mode=None  # WiFi Mode for this profile.
        )


    def setup_chamberview(self, delete_scenario=True,
                          scenario_name="Automation",
                          vap_radio="1.1.wiphy1",
                          profile_name=None,
                          freq=-1,
                          line=None):

        shelf, resource, vap_radio_name, *nil = LFUtils.name_to_eid(vap_radio)


        self.profile_name = profile_name
        self.vap_radio = vap_radio_name
        self.freq = freq

        chamber = create_chamber(lfmgr=self.lfclient_host,
                 port=self.lf_port)

        if delete_scenario:
            chamber.clean_cv_scenario(
                cv_type="Network-Connectivity",
                scenario_name=scenario_name)

        if self.set_upstream:
            self.raw_line_l1 = [[f'profile_link 1.1 {self.profile_name} 1 NA NA {self.vap_radio},AUTO {self.freq} NA'],
                                ["resource 1.1.0 0"],
                                ["profile_link 1.1 upstream-dhcp 1 NA NA eth1,AUTO -1 NA"]]
        else:
            self.raw_line_l1 = [[f'profile_link 1.1 {self.profile_name} 1 NA NA {self.vap_radio},AUTO {self.freq} NA'],
                                ["resource 1.1.0 0"]]

        logger.info(self.raw_line_l1)

        chamber.setup(create_scenario=scenario_name,
                                 line=line,
                                 raw_line=self.raw_line_l1)


        return chamber



def valid_endp_types(_endp_type):
    etypes = _endp_type.split(',')
    for endp_type in etypes:
        valid_endp_type = [
            'lf',
            'lf_udp',
            'lf_udp6',
            'lf_tcp',
            'lf_tcp6',
            'mc_udp',
            'mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            logger.error(
                'invalid endp_type: %s. Valid types lf, lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' %
                endp_type)
            exit(1)
    return _endp_type


def main():
    parser = argparse.ArgumentParser(
        prog='lf_rssi_check.py',
        formatter_class=argparse.RawTexthelpFormatter,
        epilog='''
            RSSI calculation
        ''',
        description='''
            Validate RSSI for specific radios
        '''
    )
    parser.add_argument('--local_lf_report_dir', help='--local_lf_report_dir override the report path, primary use when running test in test suite', default="")
    parser.add_argument("--test_rig", default="", help="test rig for kpi.csv, testbed that the tests are run on")
    parser.add_argument("--test_tag", default="", help="test tag for kpi.csv,  test specific information to differenciate the test")
    parser.add_argument("--dut_hw_version", default="", help="dut hw version for kpi.csv, hardware version of the device under test")
    parser.add_argument("--dut_sw_version", default="", help="dut sw version for kpi.csv, software version of the device under test")
    parser.add_argument("--dut_model_num", default="", help="dut model for kpi.csv,  model number / name of the device under test")
    parser.add_argument("--dut_serial_num", default="", help="dut serial for kpi.csv, serial number / serial number of the device under test")
    parser.add_argument("--test_priority", default="", help="dut model for kpi.csv,  test-priority is arbitrary number")
    parser.add_argument("--test_id", default="lf_rssi_check", help="test-id for kpi.csv,  script or test name")
    '''
    Other values that are included in the kpi.csv row.
    short-description : short description of the test
    pass/fail : set blank for performance tests
    numeric-score : this is the value for the y-axis (x-axis is a timestamp),  numeric value of what was measured
    test details : what was measured in the numeric-score,  e.g. bits per second, bytes per second, upload speed, minimum cx time (ms)
    Units : units used for the numeric-scort
    Graph-Group - For the lf_qa.py dashboard

    '''

    # LANforge Configuration station
    parser.add_argument("--lfmgr_sta", help="--lfmgr_sta <lanforge with stations>  default: localhost", default="localhost")
    parser.add_argument("--lfmgr_port_sta", help="--lfmgr_port_sta <lanforge port with stations> default: 8080", default=8080)
    parser.add_argument("--sta_radio", help="To set station radio example 1.1.wiphy2 required",required=True)
    parser.add_argument("--sta_radio", help="To set station radio example 1.1.wiphy2 required",required=True)


    # LANforge Configuration vAP
    parser.add_argument("--lfmgr_vap", help="--lfmgr_vap <lanforge with vap> ", default="localhost")
    parser.add_argument("--lfmgr_port_vap", help="--lfmgr_port_vap (lanforge port with vap)>", default=8080)
    parser.app_argument("--delete_old_scenario", action='store_true', help="To delete old scenarios")
    parser.add_argument("--scenario_name", default="rssi_check",help="Chamberview scenario name (default: rssi_check)")
    parser.add_argument("--vap_radio", help="vap radio name  example 1.1.wiphy1, required",default="1.1.wiphy0")
    parser.add_argument("--vap_frequency", help="vap radio frequency", required=True)
    parser.add_argument("--vap_ssid", help="vap ssid (default: vap_ssid", default="vap_ssid")
    parser.add_argument("--vap_passwd", help="vap password (default: vap_pass", default="vap_pass")
    parser.add_argument("--vap_security", help="vap security (default: wpa2", default="wpa2")
    parser.add_argument("--vap_no_cleanup", help="To not delete the vap after default: False",action=store_true)



    # LANforge Configruation station 
    parser.add_argument("--sta_radio", help="To set station radio default: 1.1.wiphy1", default= "1.1.wiphy1")
    parser.add_argument("--sta_number", help="To set station radio (default:1)", default=1)
    parser.add_argument("--sta_name", help="To set the station name default: sta0000",default="sta0000")
    parser.add_argument("--sta_ssid", help="To set the station ssid default: vap_ssid",default="vap_ssid")
    parser.add_argument("--sta_passwd", help="To set the station ssid password default: vap_pass",default="vap_pass")
    parser.add_argument("--sta_security", help="To set the station security default: wpa2",default="wpa2")
    parser.add_argument("--sta_name", help="To set the station name default: sta0000",default="sta0000")
    parser.add_argument("--sta_no_cleanup", help="To not delete the station after default: False",action=store_true)

    # Test Configuration 



    # import of AP module

    parser.add_argument('--test_duration', help='--test_duration <how long to run> interation example --time 5s (5 seconds) default: 5s options: number followed by d, h, m or s', default='5s')
    parser.add_argument('--debug', help='--debug this will enable debugging in py-json method', action='store_true')
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument('--endp_type', help='''
            --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp
            Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6'
            ''', default='lf_udp', type=valid_endp_types)

    parser.add_argument('--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth2', default='eth2')

    # Used for station creation 
    parser.add_argument('--radio', action='append',
        nargs=1,
        help=(' --radio'
              ' "radio==<number_of_wiphy stations==<number of stations>'
              ' ssid==<ssid> ssid_pw==<ssid password> security==<security> '
              ' wifi_settings==True wifi_mode==<wifi_mode>'
              ' enable_flags==<enable_flags> '
              ' reset_port_enable==True reset_port_time_min==<min>s'
              ' reset_port_time_max==<max>s" ')
    )
    

