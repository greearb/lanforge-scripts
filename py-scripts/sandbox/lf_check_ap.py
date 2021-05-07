#!/usr/bin/python3

'''
NAME:
lf_check.py

PURPOSE:
Script to verify connectivity to an AP

EXAMPLE:

./lf_check_ap.py --ap_port '/dev/ttyUSB0' --ap_baud '115200' --ap_cmd "wl -i wl0 bs_data"
ap_stats wl -i wl0 bs_data

NOTES:

Script is in the sandbox
run /py-scripts/update_dependencies.py 

'''

import sys
if sys.version_info[0]  != 3:
    print("This script requires Python3")
    exit()

import logging
import time
from time import sleep
import argparse
import pexpect
import serial
from serial import Serial
from pexpect_serial import SerialSpawn
import json
from json import load
from pprint import *
    

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
    def __init__(self, 
                 _ap_port, 
                 _ap_baud, 
                 _ap_cmd):
        self.ap_port = _ap_port
        self.ap_baud = _ap_baud
        self.ap_cmd = _ap_cmd
    

    def read_ap_stats(self):
        #  5ghz:  wl -i wl1 bs_data  2.4ghz# wl -i wl0 bs_data
        ap_data = ""
        ap_stats = []
        #command = stats_5ghz
        '''if band == "5ghz":
            command = stats_5ghz
        else:
            command = stats_24ghz'''
        # /dev/ttyUSB0 baud 115200
        # configure the serial interface
        #ser = serial.Serial(self.args.tty, int(self.args.baud), timeout=5)
        ser = serial.Serial(self.ap_port, int(self.ap_baud), timeout=5)
        ss = SerialSpawn(ser)
        ss.sendline(str(self.ap_cmd))
        ss.expect([pexpect.TIMEOUT], timeout=2) # do not detete line, waits for output
        ap_stats = ss.before.decode('utf-8','ignore')
        print("ap_stats {}".format(ap_stats))
        '''ap_stats = "\
           \
" 
        ap_stats.append("root@Docsis-Gateway:~# wl -i wl1 bs_data")
        ap_stats.append("Station Address   PHY Mbps  Data Mbps    Air Use   Data Use    Retries   bw   mcs   Nss   ofdma mu-mimo")
        ap_stats.append("50:E0:85:87:AA:19     1016.6       48.9       6.5%      24.4%      16.6%   80   9.7     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:84:7A:E7      880.9       52.2       7.7%      26.1%      20.0%   80   8.5     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:89:5D:00      840.0       47.6       6.4%      23.8%       2.3%   80   8.0     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:87:5B:F4      960.7       51.5       5.9%      25.7%       0.0%   80     9     2    0.0%    0.0%")
        ap_stats.append("(overall)          -      200.2      26.5%         -         -")
        # TODO:  Read real stats, comment out the example above.

        '''
        return ap_stats

        '''root@Docsis-Gateway:~# wl -i wl1 bs_data
        Station Address   PHY Mbps  Data Mbps    Air Use   Data Use    Retries   bw   mcs   Nss   ofdma mu-mimo
        50:E0:85:87:AA:19     1064.5       52.8       6.0%      25.0%       1.5%   80  10.0     2    0.0%    0.0%
        50:E0:85:84:7A:E7      927.1       53.6       7.0%      25.4%       5.7%   80   8.8     2    0.0%    0.0%
        50:E0:85:89:5D:00      857.5       51.8       6.8%      24.6%       0.8%   80     8     2    0.0%    0.0%
        50:E0:85:87:5B:F4     1071.7       52.8       6.0%      25.0%       1.3%   80    10     2    0.0%    0.0%
        (overall)          -      210.9      25.8%         -         -'''

        '''I have some un-tested code that is starting point for querying Comcast AP in the l3_longevity script.  
        When still needs doing:  query the data from the AP, and test that my parsing and CSV logic is working, 
        also add cmd-line arg to enable this or not.  Would you have time to work on this and coordinate test time on 
        customer's system to test against their AP?  Access to AP is probably ssh, possibly serial or telnet. 
        Firas @ Comcast can help clarify that.'''

    def parse_ap_stats(self):
            # Query AP for its stats.  Result for /ax bcm APs looks something like this:
            ap_stats = self.read_ap_stats()
            ap_stats_rows = [] # Array of Arrays

            for line in ap_stats:
                stats_row = line.split()
                ap_stats_rows.append(stats_row)
            # - is this needed ?m = re.search((r'(\S+)\s+(\S+)\s+(Data Mbps)\s+(Air Use)+'ap_stats[0]

            # Query all of our ports
            #port_eids = self.gather_port_eids()
            #for eid_name in port_eids:
            #    eid = self.name_to_eid(eid_name)
            #    url = "/port/%s/%s/%s"%(eid[0], eid[1], eid[2])
            #    response = self.json_get(url)
            #    if (response is None) or ("interface" not in response):
            #        print("query-port: %s: incomplete response:"%(url))
            #        pprint(response)
            #    else:
            # note changed the indent
            #p = response['interface']

            mac = ["50:E0:85:87:AA:19","50:E0:85:84:7A:E7","50:E0:85:89:5D:00","50:E0:85:87:5B:F4"]
            #mac = "50:E0:85:87:AA:19"
            #mac = "50:E0:85:84:7A:E7" 
            #mac = "50:E0:85:89:5D:00"
            #mac = "50:E0:85:87:5B:F4"

            ap_row = []
            i = 0
            for row in ap_stats_rows:
                if row[0] in mac:
                #if row[0].lower == mac.lower():
                    ap_row = row
                    print("ap_row: {}".format(ap_row))

            # p is map of key/values for this port
            #print("ap_row : {}".format(ap_row))
            #pprint(ap_row)
            # Find latency, jitter for connections using this port.
            #latency, jitter, tput = self.get_endp_stats_for_port(p["port"], endps)
                    
            #        ap_stats_col_titles = ['Station Address','PHY Mbps','Data Mbps','Air Use','Data Use','Retries','bw','mcs','Nss','ofdma','mu-mimo'
            #        self.write_port_csv(len(temp_stations_list), ul, dl, ul_pdu_str, dl_pdu_str, atten_val, eid_name, p,
            #                            latency, jitter, tput, ap_row, ap_stats_col_titles

def main():

    parser = argparse.ArgumentParser(
        prog='lf_check.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Verification
            ''',
        
        description='''\
lf_check.py:
--------------------
#ssid TCH-XB7
#ssidpw comcats123
Summary : 
----------
This file is used for verification

Generic command layout:
-----------------------

        ''')
    parser.add_argument('--ap_port', help='--ap_port \'/dev/ttyUSB0\'',default='/dev/ttyUSB0')
    parser.add_argument('--ap_baud', help='--ap_baud  \'115200\'',default='115200')
    parser.add_argument('--ap_cmd', help='--ap_cmd \'wl -i wl1 bs_data\'',default="wl -i wl1 bs_data")
    
    args = parser.parse_args()
    

    __ap_port = args.ap_port
    __ap_baud = args.ap_baud
    __ap_cmd  = args.ap_cmd

    check = lf_check(
                _ap_port = __ap_port,
                _ap_baud = __ap_baud,
                _ap_cmd = __ap_cmd )
    #check.parse_ap_stats()
    check.read_ap_stats()
    #check.run_test()


if __name__ == '__main__':
    main()


