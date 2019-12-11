#!/usr/bin/python3
'''
LANforge 192.168.100.178
Controller is 192.1.0.10
AP is 192.1.0.2

make sure pexpect is installed:
$ sudo yum install python3-pexpect

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial

'''


import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import logging
import time
from time import sleep
import pprint
import telnetlib
import argparse
import pexpect

default_host = "localhost"
default_ports = {
   "serial": None,
   "ssh":   22,
   "telnet": 23
}
NL = "\n"
CR = "\r\n"
Q = '"'
A = "'"

def usage():
   print("$0 used connect to controller:")
   print("-d|--dest:  destination host")
   print("-o|--port:  destination port")
   print("-u|--user:  login name")
   print("-p|--pass:  password")
   print("-s|--scheme (serial|telnet|ssh): connect via serial, ssh or telnet")
   print("-l|--log file: log messages here")
   print("-h|--help")


def main():
   logg = logging.getLogger(__name__)
   logg.setLevel(logging.DEBUG)
   flog = None; # log file
   parser = argparse.ArgumentParser(description="Ciscos AP Control Script")
   parser.add_argument("-d", "--dest",    type=str, help="address of the cisco controller")
   parser.add_argument("-o", "--port",    type=int, help="control port on the controller")
   parser.add_argument("-u", "--user",    type=str, help="credential login/username")
   parser.add_argument("-p", "--passwd",  type=str, help="credential password")
   parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
   parser.add_argument("-t", "--tty",     type=str, help="tty serial device")
   parser.add_argument("-l", "--log",     type=str, help="logfile for messages")

   try:
      args = parser.parse_args()
      host = args.dest
      scheme = args.scheme
      port = (default_ports[scheme], args.port)[args.port != None]

      user = args.user
      passwd = args.passwd
      logfile = args.log

   except Exception as e:
      logging.exception(e);
      usage()
      exit(2);

   if (logfile is not None):
      flog = logg.FileHandler(logfile);


   #connect = None
   egg = None # think "eggpect"
   try:
      if (scheme == "serial"):
         #eggspect = pexpect.fdpexpect.fdspan(telcon, logfile=sys.stdout.buffer)
         import serial
         from pexpect_serial import SerialSpawn
         with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as ser:
            egg = SerialSpawn(ser);
      elif (scheme == "ssh"):
         if (port is None):
            port = 22
         cmd = "ssh -p%d %s@%s"%(port, user, host)
         print ("Spawn: "+cmd+NL)
         egg = pexpect.spawn(cmd)
      elif (scheme == "telnet"):
         if (port is None):
            port = 23
         cmd = "telnet %s %d"%(host, port)
         print ("Spawn: "+cmd+NL)
         egg = pexpect.spawn()
      else:
         usage()
         exit(1)
   except Exception as e:
      logging.exception(e);

   # print("will %s to %s:%d\n"%(scheme, host, port));
   if (flog is not None):
      egg.logfile = flog

   egg.expect("password:")
   time.sleep(0.1)
   egg.sendline(passwd)
   egg.expect("(Cisco Controller) .*>")
   egg.sendline("show ap summary");
   egg.expect("(Cisco Controller) .*>")
   time.sleep(0.1)
   egg.sendline("logout");
   egg.expect("Would you like to save them now? (y/N)")
   time.sleep(0.1)
   egg.sendline("y");



# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()

####
####
####
