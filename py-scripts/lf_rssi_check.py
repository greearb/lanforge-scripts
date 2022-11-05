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

class lf_rssi_check:
    def __init__(self):
        pass


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

    # LANforge Configuration
    parser.add_argument('--lfmgr_sta', help='--lfmgr_sta <lanforge with stations>', default='localhost')
    parser.add_argument('--lfmgr_port_sta', help='--lfmgr_port_sta <lanforge port with stations>', default=8080)

    # 
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
    

