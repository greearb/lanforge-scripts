#!/usr/bin/python3

'''
NAME:
lf_check.py

PURPOSE:
Script is used to run a series of tests to verifiy realm changes.

EXAMPLE:

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
import pexpect
import serial
from pexpect_serial import SerialSpawn
import json
from json import load
import configparser
from pprint import *
    

CONFIG_FILE = os.getcwd() + '/py-scripts/sandbox/config.ini'    

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
        self.ssid =""
        self.passwd =""
        self.security =""
    
    # Functions in this section are/can be overridden by descendants
    def readConfigContents(self):
        config_file = configparser.ConfigParser()
        success = True
        success = config_file.read(CONFIG_FILE)
        print("{}".format(success))
        print("{}".format(config_file))

        if 'AP_CONFIG' in config_file.sections():
            config_instance = config_file['AP_CONFIG']
            try:
                self.ssid = config_instance.get('SSID')
                self.passwd = config_instance.get('PASSWD')
                self.security = config_instance.get('SECURITY')

                print("AP_CONFIG retrieved")
                print("ssid {}".format(self.ssid))
                print("passwd {}".format(self.passwd))
                print("security {}".format(self.security))
            except:
                print("no test list")


    def read_ap_stats(self):
        #  5ghz:  wl -i wl1 bs_data  2.4ghz# wl -i wl0 bs_data
        stats_5ghz  = "wl -i wl1 bs_data"
        stats_24ghz = "w1 -i wl0 bs_data"
        ap_data = ""
        ap_stats = []
        command = stats_5ghz
        '''if band == "5ghz":
            command = stats_5ghz
        else:
            command = stats_24ghz'''
    
        #try:
            # configure the serial interface
        ser = serial.Serial("/dev/ttyUSB0", int(115200), timeout=5)
        egg = SerialSpawn(ser)
        egg.sendline(str(command))
        egg.expect([pexpect.TIMEOUT], timeout=2) # do not detete line, waits for output
        ap_data = egg.before.decode('utf-8','ignore')
        #except:
        #    print("WARNING unable to read AP")
        
        '''ap_stats = "\
           \
" '''
        ap_stats.append("root@Docsis-Gateway:~# wl -i wl1 bs_data")
        ap_stats.append("Station Address   PHY Mbps  Data Mbps    Air Use   Data Use    Retries   bw   mcs   Nss   ofdma mu-mimo")
        ap_stats.append("50:E0:85:87:AA:19     1016.6       48.9       6.5%      24.4%      16.6%   80   9.7     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:84:7A:E7      880.9       52.2       7.7%      26.1%      20.0%   80   8.5     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:89:5D:00      840.0       47.6       6.4%      23.8%       2.3%   80   8.0     2    0.0%    0.0%")
        ap_stats.append("50:E0:85:87:5B:F4      960.7       51.5       5.9%      25.7%       0.0%   80     9     2    0.0%    0.0%")
        ap_stats.append("(overall)          -      200.2      26.5%         -         -")
        # TODO:  Read real stats, comment out the example above.

        
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
    check = lf_check()
    #check.parse_ap_stats()
    check.readConfigContents()


if __name__ == '__main__':
    main()


