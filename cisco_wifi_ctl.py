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

./cisco_wifi_ctl.py -d 192.168.100.112 -u admin -p Cisco123 -s ssh --port 22
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
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'
band = "a"

def usage():
   print("$0 used connect to controller:")
   print("-d|--dest:  destination host")
   print("-o|--port:  destination port")
   print("-u|--user:  login name")
   print("-p|--pass:  password")
   print("-s|--scheme (serial|telnet|ssh): connect via serial, ssh or telnet")
   print("-l|--log file: log messages here")
   print("-b|--band:  a (5Ghz) or b (2.4Ghz)")
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
   parser = argparse.ArgumentParser(description="Cisco AP Control Script")
   parser.add_argument("-d", "--dest",    type=str, help="address of the cisco controller")
   parser.add_argument("-o", "--port",    type=int, help="control port on the controller")
   parser.add_argument("-u", "--user",    type=str, help="credential login/username")
   parser.add_argument("-p", "--passwd",  type=str, help="credential password")
   parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
   parser.add_argument("-t", "--tty",     type=str, help="tty serial device")
   parser.add_argument("-l", "--log",     type=str, help="logfile for messages, stdout means output to console")
   #parser.add_argument("-r", "--radio",   type=str, help="select radio")
   parser.add_argument("-a", "--ap",      type=str, help="select AP")
   parser.add_argument("-b", "--band",    type=str, help="Select band (a | b)",
                       choices=["a", "b"])
   parser.add_argument("--action",        type=str, help="perform action",
      choices=["config", "country", "ap_country", "enable", "disable", "summary", "advanced",
      "cmd", "txPower", "bandwidth", "channel", "show" ])
   parser.add_argument("--value",       type=str, help="set value")

   args = None
   try:
      args = parser.parse_args()
      host = args.dest
      scheme = args.scheme
      port = (default_ports[scheme], args.port)[args.port != None]
      user = args.user
      passwd = args.passwd
      logfile = args.log
      if (args.band != None):
          band = args.band
      else:
          band = "a"
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

   egg = None # think "eggpect"
   try:
      if (scheme == "serial"):
         #eggspect = pexpect.fdpexpect.fdspan(telcon, logfile=sys.stdout.buffer)
         import serial
         from pexpect_serial import SerialSpawn
         with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as ser:
            egg = SerialSpawn(ser);
            egg.logfile = FileAdapter(logg)
            egg.sendline(NL)
            time.sleep(0.1)
            egg.expect('login:', timeout=3)
            time.sleep(0.1)
            egg.sendline(user)
            time.sleep(0.1)
            egg.expect('password:')

      elif (scheme == "ssh"):
         if (port is None):
            port = 22
         cmd = "ssh -p%d %s@%s"%(port, user, host)
         logg.info("Spawn: "+cmd+NL)
         egg = pexpect.spawn(cmd)
         #egg.logfile_read = sys.stdout.buffer
         egg.logfile = FileAdapter(logg)
         i = egg.expect(["password:", "continue connecting (yes/no)?"], timeout=3)
         time.sleep(0.1)
         if i == 1:
            egg.sendline('yes')
            egg.expect('password:')
         sleep(0.1)
         egg.sendline(passwd)

      elif (scheme == "telnet"):
         if (port is None):
            port = 23
         cmd = "telnet %s %d"%(host, port)
         logg.info("Spawn: "+cmd+NL)
         egg = pexpect.spawn(cmd)
         egg.logfile = FileAdapter(logg)
         egg.expect('login:', timeout=3)
         time.sleep(0.1)
         egg.sendline(user)
         time.sleep(0.1)
         egg.expect('password:')
         time.sleep(0.1)
         egg.sendline(passwd)
      else:
         usage()
         exit(1)
   except Exception as e:
      logging.exception(e);

   command = None
   time.sleep(0.1)
   CCPROMPT = '\(Cisco Controller\) >'
   EXITPROMPT = "Would you like to save them now\? \(y/N\)"
   AREYOUSURE = "Are you sure you want to continue\? \(y/n\)"
   CLOSEDBYREMOTE = "closed by remote host."
   CLOSEDCX = "Connection to .* closed."
   egg.expect(CCPROMPT)

   logg.info("Ap[%s] Action[%s] Value[%s] "%(args.ap, args.action, args.value))

   if ((args.action == "show") and (args.value is None)):
      raise Exception("show requires value, like 'country' or 'ap summary'")

   if (args.action == "show"):
      print ("HI")
      command = "show "+args.value

   if (args.action == "cmd"):
       if (args.value is None):
           raise Exception("cmd requires value to be set.")
       command = "%s"%(args.value)

   if (args.action == "summary"):
      command = "show ap summary"

   if (args.action == "advanced"):
      command = "show advanced 802.11%s summary"%(band)

   if ((args.action == "ap_country") and ((args.value is None) or (args.ap is None))):
      raise  Exception("ap_country requires country and AP name")

   if (args.action == "ap_country"):
      command = "config ap country %s %s"%(args.value, args.ap)

   if ((args.action == "country") and ((args.value is None))):
      raise  Exception("country requires country value")

   if (args.action == "country"):
      command = "config country %s"%(args.value)

   if (args.action in ["enable", "disable" ] and (args.ap is None)):
      raise Exception("action requires AP name")
   if (args.action == "enable"):
      command = "config 802.11%s enable %s"%(band, args.ap)
   if (args.action == "disable"):
      command = "config 802.11%s disable %s"%(band, args.ap)

   if (args.action == "txPower" and ((args.ap is None) or (args.value is None))):
      raise Exception("txPower requires ap and value")
   if (args.action == "txPower"):
      command = "config 802.11%s txPower ap %s %s"%(band, args.ap, args.value)

   if (args.action == "bandwidth" and ((args.ap is None) or (args.value is None))):
      raise Exception("bandwidth requires ap and value (20, 40, 80, 160)")
   if (args.action == "bandwidth"):
      command = "config 802.11%s chan_width %s %s"%(band, args.ap, args.value)

   if (args.action == "channel" and ((args.ap is None) or (args.value is None))):
      raise Exception("channel requires ap and value")
   if (args.action == "channel"):
      command = "config 802.11%s channel ap %s %s"%(band, args.ap, args.value)


   if (command is None):
      logg.info("No command specified, going to log out.")
   else:
      logg.info("Command[%s]"%command)
      egg.sendline(command);
      i = egg.expect([CCPROMPT, AREYOUSURE])
      print (egg.before.decode('utf-8', 'ignore'))
      if i == 1:
          egg.sendline("y")

   egg.sendline("logout")
   i = egg.expect([EXITPROMPT, CLOSEDBYREMOTE, CLOSEDCX])
   if i == 0:
       egg.sendline("y")



# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()

####
####
####
