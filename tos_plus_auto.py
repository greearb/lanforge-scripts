#!/usr/bin/python3
'''

make sure pexpect is installed:
$ sudo yum install python3-pexpect

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial

./tos_plus_auto.py
'''


import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import os
import re
import logging
import time
from time import sleep
import pprint
import telnetlib
import argparse
import pexpect

ptype="QCA"

def usage():
   print("$0 used connect to automated a test case using cisco controller and LANforge tos-plus script:")
   print("-p|--ptype:  AP Hardware type")
   print("-h|--help")

def main():
   global ptype


   parser = argparse.ArgumentParser(description="TOS Plus automation script")
   parser.add_argument("-p", "--ptype",    type=str, help="AP Hardware type")
   
   args = None
   try:
      args = parser.parse_args()
      if (args.ptype != None):
         ptype = args.ptype
      
   except Exception as e:
      logging.exception(e);
      usage()
      exit(2);

   # Set up cisco controller.  For now, variables are hard-coded.
   dest = 172.19.27.95
   port = 2013
   ap = AxelMain
   user = cisco
   passwd = Cisco123
   
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -w wlan_open -i 6 --action wlan"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -w wlan_open -i 6 --action wlan_qos --value platinum"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s --action show --value \"wlan summary\""%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -b b --action disable"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -b a --action disable"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -b a --action channel --value 149"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -b a --action bandwidth --value 80"%(dest, port, ap, user, passwd))
   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -b a --action enable"%(dest, port, ap, user, passwd))

   
   # Run the tos plus script to generate traffic and grab capture files.
   # You may edit this command as needed for different behaviour.
   subprocess.run("./lf_tos_plus_test.py --dur 1 --lfmgr localhost --ssid 11ax-open --radio \"1.wiphy0 2 0\" --txpkts 10000 --wait_sniffer 1   --cx \"1.wiphy0 1.wlan0 anAX 1.eth2 udp 1024 10000 50000000 184\" --sniffer_radios \"1.wiphy2\"")

   file1 = open('TOS_PLUS.sh', 'r') 
   lines = file1.readlines()

   csv_file = ""
   capture_dir = ""
   # Strips the newline character 
   for line in lines:
       tok_val = line.split("=", 1)
       if tok_val[0] == "CAPTURE_DIR":
           capture_dir = tok_val[1]
       else if tok_val[0] == "CSV_FILE":
           capture_dir = tok_val[1]

   # Remove  third-party tool's tmp file tmp file
   os.unlink("stormbreaker.log")

   # Run third-party tool to process the capture files.
   subprocess.run("python3 sb -p %s -subdir %s"%(ptype, capture_dir))

   # Print out one-way latency reported by LANforge
   file2 = open(csv_file, 'r')
   lines = file2.readlines()

   # Strips the newline character 
   for line in lines:
       cols = line.split("\t")
       # Print out endp-name and avg latency
       print("%s\t%s"%(cols[1], cols[15]))


   subprocess.run("python3 cisco_wifi_ctl.py -d %s  -o %s -s telnet -l stdout -a %s -u %s -p %s -w wlan_open -i 6 --action delete_wlan"%(dest, port, ap, user, passwd))

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()

####
####
####
