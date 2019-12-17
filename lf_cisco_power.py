#!/usr/bin/python3
'''
LANforge 192.168.100.178
Controller at 192.168.100.112 admin/Cisco123
Controller is 192.1.0.10
AP is 192.1.0.2

make sure pexpect is installed:
$ sudo yum install python3-pexpect

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial

./lf_cisco_power.py -d 192.168.100.112 -u admin -p Cisco123 -s ssh --port 22
'''


import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import re
import logging
import time
from time import sleep
import pprint
import argparse
import subprocess

NL = "\n"
CR = "\r\n"
Q = '"'
A = "'"
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'

def usage():
   print("$0 used connect to controller:")
   print("-a|--ap:  AP to act upon")
   print("-d|--dest:  destination host")
   print("-o|--port:  destination port")
   print("-u|--user:  login name")
   print("-p|--pass:  password")
   print("-s|--scheme (serial|telnet|ssh): connect via serial, ssh or telnet")
   print("-l|--log file: log messages here")
   print("-b|--bandwidth: List of bandwidths to test: 20 40 80 160")
   print("-c|--channel: List of channels to test: 36 100")
   print("-n|--nss: List of spatial streams to test: 1 2 3 4")
   print("-h|--help")

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

def main():
   parser = argparse.ArgumentParser(description="Cisco TX Power report Script")
   parser.add_argument("-d", "--dest",    type=str, help="address of the cisco controller")
   parser.add_argument("-o", "--port",    type=int, help="control port on the controller")
   parser.add_argument("-u", "--user",    type=str, help="credential login/username")
   parser.add_argument("-p", "--passwd",  type=str, help="credential password")
   parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
   parser.add_argument("-t", "--tty",     type=str, help="tty serial device")
   parser.add_argument("-l", "--log",     type=str, help="logfile for messages, stdout means output to console")
   #parser.add_argument("-r", "--radio",   type=str, help="select radio")
   parser.add_argument("-a", "--ap",      type=str, help="select AP")
   parser.add_argument("-b", "--bandwidth",        type=str, help="List of bandwidths to test")
   parser.add_argument("-c", "--channel",        type=str, help="List of channels to test")
   parser.add_argument("-n", "--nss",        type=str, help="List of spatial streams to test")
   parser.add_argument("-T", "--txpower",        type=str, help="List of txpowers to test")

   args = None
   try:
      args = parser.parse_args()
      host = args.dest
      scheme = args.scheme
      port = (default_ports[scheme], args.port)[args.port != None]
      user = args.user
      passwd = args.passwd
      logfile = args.log
      filehandler = None
   except Exception as e:
      logging.exception(e);
      usage()
      exit(2);

   console_handler = logging.StreamHandler()
   formatter = logging.Formatter(FORMAT)
   logg = logging.getLogger(__name__)
   logg.setLevel(logging.DEBUG)
   file_handler = None
   if (logfile is not None):
       if (logfile != "stdout"):
           file_handler = logging.FileHandler(logfile, "w")
           file_handler.setLevel(logging.DEBUG)
           file_handler.setFormatter(formatter)
           logg.addHandler(file_handler)
           logging.basicConfig(format=FORMAT, handlers=[file_handler])
       else:
           # stdout logging
           logging.basicConfig(format=FORMAT, handlers=[console_handler])

   bandwidths = args.bandwidth.split()
   channels = args.channel.split()
   nss = args.nss.split()
   txpowers = args.txpower.split()

   for ch in channels:
       for n in nss:
           for bw in bandwidths:
               for tx in txpowers:

                   # TODO:  Down station
                   
                   # Disable AP, apply settings, enable AP
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "disable"])
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11a disable network"])
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11b disable network"])

                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "txPower", "--value", tx])
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "bandwidth", "--value", bw])
                   # TODO:  Set nss
                   # TODO:  Set channel
                   
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11a enable network"])
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11b enable network"])
                   subprocess.run(["cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "-s", "ssh",
                                   "--action", "enable"])

                   # TODO:
                   # Up station
                   # Wait untill LANforge station connects
                   # Wait untill connect starts sending data
                   # Wait 10 more seconds
                   # Gather probe results and record data, verify NSS, BW, Channel


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()

####
####
####
