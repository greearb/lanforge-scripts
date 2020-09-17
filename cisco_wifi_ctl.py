#!/usr/bin/python3
'''
LANforge 172.19.27.91
Controller at 172.19.27.95 2013 cisco/Cisco123
Controller is 192.1.0.10
AP is 172.19.27.95 2014

make sure pexpect is installed:
$ sudo yum install python3-pexpect

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial

./cisco_wifi_ctl.py -d 172.19.27.95 -o 2013 -l stdout -a AxelMain -u cisco -p Cisco123 -s telnet

# For LANforge lab system.
./cisco_wifi_ctl.py --scheme ssh -d 192.168.100.112 -u admin -p Cisco123 --action summary --prompt "\(Cisco Controller\) >"
./cisco_wifi_ctl.py --scheme ssh -d 192.168.100.112 -u admin -p Cisco123 --action cmd --value "show ap config general APA453.0E7B.CF9C"

telnet 172.19.36.168(Pwd:Wnbulab@123), go to the privileged mode and execute the command “clear line 43”.
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
   print("--prompt:   prompt to expect, ie \"\\(Cisco Controller\\) >\"")
   print("--series: cisco controller series, ie \"9800\"")

   print("-u|--user:  login name")
   print("-p|--pass:  password")
   print("-s|--scheme (serial|telnet|ssh): connect via serial, ssh or telnet")
   print("-l|--log file: log messages here ")
   print("-b|--band:  a (5Ghz) or b (2.4Ghz) or abgn for dual-band 2.4Ghz AP")
   print("-w|--wlan:  WLAN name")
   print("-i|--wlanID:  WLAN ID")

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
   parser.add_argument("-o", "--port",    type=int, help="control port on the controller", default=2043)
   parser.add_argument("--prompt",        type=str, help="Prompt to expect", default="\(Cisco Controller\) >")
   parser.add_argument("--series",        type=str, help="cisco controller series",default="3504")
   parser.add_argument("-u", "--user",    type=str, help="credential login/username")
   parser.add_argument("-p", "--passwd",  type=str, help="credential password")
   parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
   parser.add_argument("-t", "--tty",     type=str, help="tty serial device")
   parser.add_argument("-l", "--log",     type=str, help="logfile for messages, stdout means output to console",default="stdout")
   #parser.add_argument("-r", "--radio",   type=str, help="select radio")
   parser.add_argument("-w", "--wlan",    type=str, help="wlan name")
   parser.add_argument("-i", "--wlanID",  type=str, help="wlan ID")
   parser.add_argument("-a", "--ap",      type=str, help="select AP", default="APA453.0E7B.CF9C")
   parser.add_argument("-b", "--band",    type=str, help="Select band (a | b | abgn)",
                       choices=["a", "b", "abgn"])
   parser.add_argument("--action",        type=str, help="perform action",
      choices=["config", "country", "ap_country", "enable", "disable", "summary", "advanced",
      "cmd", "txPower", "bandwidth", "manual", "auto","no_wlan","show_wlan_summary",
      "ap_channel", "channel", "show", "wlan", "enable_wlan", "delete_wlan", "wlan_qos",
      "disable_network_5ghz","disable_network_24ghz","enable_network_5ghz","enable_network_24ghz",
      "wireless_tag_policy"])
   parser.add_argument("--value",       type=str, help="set value")

   args = None
   try:
      args = parser.parse_args()
      host = args.dest
      scheme = args.scheme
      port = args.port
      #port = (default_ports[scheme], args.port)[args.port != None]
      user = args.user
      passwd = args.passwd
      logfile = args.log
      if (args.band != None):
          band = args.band
          if (band == "abgn"):
              band = "-abgn"
      else:
          band = "a"
      filehandler = None
   except Exception as e:
      logging.exception(e)
      usage()
      exit(2)

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

   print("cisco series {}".format(args.series))
   print("scheme {}".format(args.scheme))

   egg = None # think "eggpect"
   try:
      if (scheme == "serial"):
         #eggspect = pexpect.fdpexpect.fdspan(telcon, logfile=sys.stdout.buffer)
         import serial
         from pexpect_serial import SerialSpawn
         with serial.Serial('/dev/ttyUSB0', 115200, timeout=5) as ser:
            egg = SerialSpawn(ser);
            egg.logfile = FileAdapter(logg)
            print("logg {}".format(logg))
            egg.sendline(NL)
            time.sleep(0.1)
            egg.expect('login:', timeout=3)
            time.sleep(0.1)
            egg.sendline(user)
            time.sleep(0.1)
            egg.expect('ssword:')

      elif (scheme == "ssh"):
         if (port is None):
            port = 22
         cmd = "ssh -p%d %s@%s"%(port, user, host)
         logg.info("Spawn: "+cmd+NL)
         egg = pexpect.spawn(cmd)
         #egg.logfile_read = sys.stdout.buffer
         egg.logfile = FileAdapter(logg)
         print("logg {}".format(logg))
         time.sleep(0.1)
         logged_in_9800 = False
         loop_count = 0
         found_escape = False
         if args.series == "9800":
            while logged_in_9800 == False and loop_count <= 2:
               #egg.sendline(CR)
               i = egg.expect_exact(["Escape character is '^]'.",">","#",":","ssword\:",pexpect.TIMEOUT],timeout=2)
               if i == 0:
                  print("9800 found Escape charter is sending carriage return i: {} before: {} after: {}".format(i,egg.before,egg.after))
                  #egg.sendline(CR)
                  found_escape = True
                  sleep(1)
                  j = egg.expect([">","#","ser\:","ssword\:",pexpect.TIMEOUT],timeout=3)
                  if j == 0:
                     print("9800 found >  will elevate loging j: {} before {} after {}".format(j,egg.before,egg.after))
                     egg.sendline("en")
                     sleep(1)
                     k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                     if k == 0:
                        print("9800 received password prompt will send password: {}  k: {} before {} after {}".format(args.passwd, k,egg.before,egg.after))
                        egg.sendline(args.passwd)
                        sleep(1)
                        l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                        if l == 0:
                           print("9800 Successfully received # prompt l {}".format(l))
                           logged_in_9800 = True
                        if l == 1:
                           print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                     if k == 1:
                        print("9800 received timeout after looking for password: prompt k {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 1:
                     print("9800 found # so logged in can start sending commands j {}".format(j))
                     logged_in_9800 = True
                  if j == 2:
                     print("9800 found User\: will put in args.user {}  j: {}".format(args.user,j))
                     egg.sendline(args.user)
                     sleep(1)
                     k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                     if k == 0:
                        print("9800 received password prompt after sending User, sending password: {} k: {}".format(args.passwd,k))
                        egg.sendline(args.passwd)
                        sleep(1)
                        l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                        if l == 0:
                           print("8900 Successfully received # prompt l: {}".format(l))
                           logged_in_9800 = True
                        if l == 1:
                           print("9800 Timed out waiting for # prompt l: {} before {} after {}".format(l,egg.before,egg.after))
                     if k == 1:
                        print("9800 received timeout after looking for password after sending user k: {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 3:
                     print("9800 received Password prompt will send password {} j: {} before {} after {}".format(args.passwd,j,egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(1)
                     k = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if k == 0:
                        print("8900 Successfully received # prompt k: {} before {} after {}".format(k,egg.before,egg.after))
                        logged_in_9800 = True
                     if k == 1:
                        print("9800 Timed out waiting for # prompt k: {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 4:
                     print("9800 timed out looking for >, #, User, Password j: {}  before {} after {}".format(j,egg.before,egg.after))
                     egg.sendline(CR)
               
               if i == 1:
                  print("9800 found >  will elevate loging i: {} before {} after {}".format(i,egg.before,egg.after))
                  egg.sendline("en")
                  sleep(1)
                  k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                  if k == 0:
                     print("9800 received password prompt will send password: {}  k: {} before {} after {}".format(args.passwd, k, egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(1)
                     l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if l == 0:
                        print("9800 Successfully received # prompt l {} before {} after {}".format(l, egg.before,egg.after))
                        logged_in_9800 = True
                     if l == 1:
                        print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                  if k == 1:
                     print("8900 received timeout after looking for password: prompt k {} before {} after {}".format(k,egg.before,egg.after))
               
               if i == 2:
                  print("9800 found # so logged in can start sending commands i {} before {} after {}".format(i,egg.before,egg.after))
                  logged_in_9800 = True

               if i == 3:
                  print("9800 found User will put in args.user {}  i: {} before {} after {}".format(args.user,i, egg.before,egg.after))
                  #egg.sendline(args.user)
                  sleep(1)
                  k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                  if k == 0:
                     print("9800 received password prompt after sending User, sending password: {} k: {} before {} after {}".format(args.passwd,k, egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(0.1)
                     l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if l == 0:
                        print("8900 Successfully received # prompt l: {}".format(l))
                        logged_in_9800 = True
                     if l == 1:
                        print("9800 Timed out waiting for # prompt l: {} before {} after {}".format(l,egg.before,egg.after))
                  if k == 1:
                     print("9800 received timeout after looking for password after sending user k: {} before {} after {}".format(k, egg.before,egg.after))

               if i == 4:
                  print("9800 received password prompt will send password: {}  i: {}  before {} after {}".format(args.passwd, k, egg.before,egg.after))
                  egg.sendline(args.passwd)
                  sleep(1)
                  l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                  if l == 0:
                     print("9800 Successfully received # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                     logged_in_9800 = True
                  if l == 1:
                     print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))

               #if i == 5:
               #   print("9800 pexpect found end of line i {} before {} after {}".format(i,egg.before,egg.after))
               #   egg.sendline(CR)

               if i == 5:
                  print("9800 Timed out waiting for intial prompt will send carriage return and line feed i: {} before {} after {}".format(i, egg.before,egg.after))
                  egg.sendline(CR)
                  sleep(2)
               loop_count += 1

            if loop_count >= 3:
               print("could not log into 9800 exiting")
               exit(1)

         # 3504 series
         else:
            i = egg.expect(["ssword:", "continue connecting (yes/no)?"], timeout=3)
            time.sleep(0.1)
            if i == 1:
               egg.sendline('yes')
               egg.expect('ssword:')
            sleep(0.1)
            egg.sendline(passwd)

      elif (scheme == "telnet"):
         sleep(1)
         if (port is None):
            port = 23
         cmd = "telnet %s %d"%(host, port)
         logg.info("Spawn: "+cmd+NL)
         egg = pexpect.spawn(cmd)
         egg.logfile = FileAdapter(logg)
         time.sleep(0.1)
         logged_in_9800 = False
         loop_count = 0
         found_escape = False
         if args.series == "9800":
            while logged_in_9800 == False and loop_count <= 2:
               #egg.sendline(CR)
               try:
                  i = egg.expect_exact(["Escape character is '^]'.",">","#","ser\:","ssword\:",pexpect.TIMEOUT],timeout=2)
               except pexpect.EOF as e:
                  print('connection failed. or refused')
                  exit(1)
               except:
                  print('unknown exception on initial pexpect after login')
                  exit(1)
               
               if i == 0:
                  print("9800 found Escape charter is sending carriage return i: {} before: {} after: {}".format(i,egg.before,egg.after))
                  #egg.sendline(CR)
                  found_escape = True
                  sleep(1)
                  j = egg.expect([">","#","ser\:","ssword\:",pexpect.TIMEOUT],timeout=3)
                  sleep(1)
                  if j == 0:
                     print("9800 found >  will elevate loging j: {} before {} after {}".format(j,egg.before,egg.after))
                     egg.sendline("en")
                     sleep(1)
                     k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                     if k == 0:
                        print("9800 received password prompt will send password: {}  k: {} before {} after {}".format(args.passwd, k,egg.before,egg.after))
                        egg.sendline(args.passwd)
                        sleep(1)
                        l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                        if l == 0:
                           print("9800 Successfully received # prompt l {}".format(l))
                           logged_in_9800 = True
                        if l == 1:
                           print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                     if k == 1:
                        print("8900 received timeout after looking for password: prompt k {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 1:
                     print("9800 found # so logged in can start sending commands j {}".format(j))
                     logged_in_9800 = True
                  if j == 2:
                     print("9800 found User\: will put in args.user {}  j: {}".format(args.user,j))
                     egg.sendline(args.user)
                     sleep(1)
                     k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                     if k == 0:
                        print("9800 received password prompt after sending User, sending password: {} k: {}".format(args.passwd,k))
                        egg.sendline(args.passwd)
                        sleep(1)
                        l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                        if l == 0:
                           print("8900 Successfully received # prompt l: {}".format(l))
                           logged_in_9800 = True
                        if l == 1:
                           print("9800 Timed out waiting for # prompt l: {} before {} after {}".format(l,egg.before,egg.after))
                     if k == 1:
                        print("9800 received timeout after looking for password after sending user k: {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 3:
                     sleep(1)
                     print("9800 received Password prompt will send password {} j: {} before {} after {}".format(args.passwd,j,egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(1)
                     k = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if k == 0:
                        print("8900 Successfully received # prompt k: {} before {} after {}".format(k,egg.before,egg.after))
                        logged_in_9800 = True
                     if k == 1:
                        print("9800 Timed out waiting for # prompt k: {} before {} after {}".format(k,egg.before,egg.after))
                  if j == 4:
                     print("9800 timed out looking for >, #, User, Password j: {}  before {} after {}".format(j,egg.before,egg.after))
                     egg.sendline(CR)
               
               if i == 1:
                  print("9800 found >  will elevate loging i: {} before {} after {}".format(i,egg.before,egg.after))
                  egg.sendline("en")
                  sleep(1)
                  k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                  if k == 0:
                     print("9800 received password prompt will send password: {}  k: {} before {} after {}".format(args.passwd, k, egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(1)
                     l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if l == 0:
                        print("9800 Successfully received # prompt l {} before {} after {}".format(l, egg.before,egg.after))
                        logged_in_9800 = True
                     if l == 1:
                        print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                  if k == 1:
                     print("8900 received timeout after looking for password: prompt k {} before {} after {}".format(k,egg.before,egg.after))
               
               if i == 2:
                  print("9800 found # so logged in can start sending commands i {} before {} after {}".format(i,egg.before,egg.after))
                  logged_in_9800 = True

               if i == 3:
                  print("9800 found User will put in args.user {}  j: {} before {} after {}".format(args.user,j, egg.before,egg.after))
                  egg.sendline(args.user)
                  sleep(1)
                  k = egg.expect(["ssword\:",pexpect.TIMEOUT], timeout=2)
                  if k == 0:
                     print("9800 received password prompt after sending User, sending password: {} k: {} before {} after {}".format(args.passwd,k, egg.before,egg.after))
                     egg.sendline(args.passwd)
                     sleep(0.1)
                     l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                     if l == 0:
                        print("8900 Successfully received # prompt l: {}".format(l))
                        logged_in_9800 = True
                     if l == 1:
                        print("9800 Timed out waiting for # prompt l: {} before {} after {}".format(l,egg.before,egg.after))
                  if k == 1:
                     print("9800 received timeout after looking for password after sending user k: {} before {} after {}".format(k, egg.before,egg.after))

               if i == 4:
                  print("9800 received password prompt will send password: {}  k: {}  before {} after {}".format(args.passwd, k, egg.before,egg.after))
                  egg.sendline(args.passwd)
                  sleep(1)
                  l = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
                  if l == 0:
                     print("9800 Successfully received # prompt l {} before {} after {}".format(l,egg.before,egg.after))
                     logged_in_9800 = True
                  if l == 1:
                     print("9800 Timed out waiting for # prompt l {} before {} after {}".format(l,egg.before,egg.after))

               #if i == 5:
               #   print("9800 pexpect found end of line i {} before {} after {}".format(i,egg.before,egg.after))
               #   egg.sendline(CR)

               if i == 5:
                  print("9800 Timed out waiting for intial prompt will send carriage return and line feed i: {} before {} after {}".format(i, egg.before,egg.after))
                  egg.sendline(CR)
                  sleep(2)


               loop_count += 1

            if loop_count >= 3:
               if found_escape == True:
                  print("9800 there may be another prompt present that not aware of")
                  print("9800 the excape was found see if we can send command")
               else:
                  print("9800 did not find the initial escape will try the command anyway")

         # 3504 series
         else:
            egg.sendline(' ')
            egg.expect('User\:',timeout=3)
            egg.sendline(user)
            egg.expect('Password\:',timeout=3)
            egg.sendline(passwd)
            #if args.prompt in "WLC#" or args.prompt in "WLC>":
            #   egg.sendline("enable")
            #   time.sleep(0.1)
            egg.sendline('config paging disable')
            #egg.expect('(Voice-Talwar) >', timeout=3)
            #time.sleep(0.1)
            #egg.sendline(user)
            #time.sleep(0.1)
            #egg.expect('ssword:')
            #time.sleep(0.1)
            #egg.sendline(passwd)
      else:
         usage()
         exit(1)
   except Exception as e:
      logging.exception(e);

   command = None
   time.sleep(0.1)
   CCPROMPT = args.prompt  #'\(Voice-Talwar\) >'
   LOGOUTPROMPT = 'User:'
   EXITPROMPT = "Would you like to save them now\? \(y/N\)"
   AREYOUSURE = "Are you sure you want to continue\? \(y/n\)"
   CLOSEDBYREMOTE = "closed by remote host."
   CLOSEDCX = "Connection to .* closed."

   sleep(0.1)
   if args.series == "9800":
      pass
   else:
      logg.info("waiting for prompt: %s"%(CCPROMPT))
      egg.expect(">", timeout=3)

   logg.info("Ap[%s] Action[%s] Value[%s] "%(args.ap, args.action, args.value))
   print("Ap[%s] Action[%s] Value[%s]"%(args.ap, args.action, args.value))

   if ((args.action == "show") and (args.value is None)):
      raise Exception("show requires value, like 'country' or 'ap summary'")

   if (args.action == "show"):
      command = "show "+args.value

   if (args.action == "cmd"):
       if (args.value is None):
           raise Exception("cmd requires value to be set.")
       command = "%s"%(args.value)

   if (args.action == "summary"):
      if args.series == "9800":
         if band == "a":
            command = "show ap summary"
         else:
            command = "show ap summary"
      else:
         command = "show ap summary"

   if (args.action == "advanced"):
      if args.series == "9800":
         if band == "a":
            command = "show ap dot11 5ghz summary"
         else:
            command = "show ap dot11 24ghz summary"
      else:
         command = "show advanced 802.11%s summary"%(band)

   if ((args.action == "ap_country") and ((args.value is None) or (args.ap is None))):
      raise  Exception("ap_country requires country and AP name")

   if (args.action == "ap_country"):
      command = "config ap country %s %s"%(args.value, args.ap)

   if ((args.action == "country") and ((args.value is None))):
      raise  Exception("country requires country value")

   if (args.action == "country"):
      command = "config country %s"%(args.value)

   if (args.action == "manual" and args.ap is None):
      raise Exception("action requires AP name")
   if (args.action == "manual"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz radio role manual client-serving"%(args.ap)
         else:
            command = "ap name %s dot11 24ghz radio role manual client-serving"%(args.ap)

   if (args.action == "auto" and args.ap is None):
      raise Exception("action requires AP name")
   if (args.action == "auto"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz radio role auto"%(args.ap)
         else:
            command = "ap name %s dot11 24ghz radio role auto"%(args.ap)

   if (args.action == "disable_network_5ghz"):
      if args.series == "9800":
         egg.sendline("config t")
         sleep(0.1)
         i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
         if i == 0:
            egg.sendline("ap dot11 5ghz shutdown")
            i = egg.expect_exact(["Are you sure you wan to continue? (y/n) [y]:",pexpect.TIMEOUT],timeout=2)
            if j == 0:
               egg.sendline(CR)
            if j == 1:
               print("did not get Are you sure you wan to continue? (y/n) [y]:")
         if i == 1:
            print("timed out on (config)# disable_network_5ghz")

   if (args.action == "disable_network_24ghz"):
      if args.series == "9800":
         egg.sendline("config t")
         sleep(0.1)
         i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
         if i == 0:
            egg.sendline("ap dot11 24ghz shutdown")
            i = egg.expect_exact(["Are you sure you wan to continue? (y/n) [y]:",pexpect.TIMEOUT],timeout=2)
            if j == 0:
               egg.sendline(CR)
            if j == 1:
               print("did not get Are you sure you wan to continue? (y/n) [y]:")
         if i == 1:
            print("timed out on (config)# disable_network_24ghz")

   if (args.action == "enable_network_5ghz"):
      if args.series == "9800":
         egg.sendline("config t")
         i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
         if i == 0:
            command = "no ap dot11 5ghz shutdown"
         else:
            print("timed out (config)# on no ap dot11 5ghz shutdown")

   if (args.action == "enable_network_24ghz"):
      if args.series == "9800":
         egg.sendline("config t")
         i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
         if i == 0:
            command = "no ap dot11 24ghz shutdown"
         else:
            print("timed out on (config)# no ap dot11 24ghz shutdown")      


   if (args.action in ["enable", "disable" ] and (args.ap is None)):
      raise Exception("action requires AP name")
   if (args.action == "enable"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s no dot11 5ghz shutdown"%(args.ap)
         else:
            command = "ap name %s no dot11 24ghz shutdown"%(args.ap)
      else:
         command = "config 802.11%s enable %s"%(band, args.ap)
   if (args.action == "disable"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz shutdown"%(args.ap)
         else:
            command = "ap name %s dot11 24ghz shutdown"%(args.ap)
      else:
         command = "config 802.11%s disable %s"%(band, args.ap)

   if (args.action == "txPower" and ((args.ap is None) or (args.value is None))):
      raise Exception("txPower requires ap and value")
   if (args.action == "txPower"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz txpower %s"%(args.ap, args.value)
         else:
            command = "ap name %s dot11 24ghz txpower %s"%(args.ap, args.value)
      else:
         command = "config 802.11%s txPower ap %s %s"%(band, args.ap, args.value)

   if (args.action == "bandwidth" and ((args.ap is None) or (args.value is None))):
      raise Exception("bandwidth requires ap and value (20, 40, 80, 160)")
   if (args.action == "bandwidth"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz channel width %s"%(args.ap, args.value)
         else:
            command = "ap name %s dot11 24ghz channel width %s"%(args.ap, args.value)
      else:
         command = "config 802.11%s chan_width %s %s"%(band, args.ap, args.value)

   if (args.action == "channel" and ((args.ap is None) or (args.value is None))):
      raise Exception("channel requires ap and value 5Ghz ")
   if (args.action == "channel"):
      if args.series == "9800":
         if band == "a":
            command = "ap name %s dot11 5ghz channel %s"%(args.ap, args.value)
         else:
            command = "ap name %s dot11 24ghz channel %s"%(args.ap, args.value)
      else:
         command = "config 802.11%s channel ap %s %s"%(band, args.ap, args.value)

   if (args.action == "ap_channel" and (args.ap is None)):
      raise Exception("ap_channel requires ap")
   if (args.action == "ap_channel"):
      if args.series == "9800":
         if band == "a":
            command = "show ap dot11 5ghz summary"
         else:
            command = "show ap dot11 24ghz summary"
      else:
         command = "show ap channel %s"%(args.ap)

   if (args.action == "wireless_tag_policy"):
      print("send wireless tag policy")
      egg.sendline("config t")
      sleep(0.1)
      i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
      if i == 0:
         for command in ["wireless tag policy default-policy-tag","wlan open-wlan policy default-policy-profile","end"]:
            egg.sendline(command)
            sleep(0.1)
            j = egg.expect_exact(["(config-policy-tag)#",pexpect.TIMEOUT],timeout=2)
            if j == 0:
               print("command sent: {}".format(command))
            if j == 1:
               print("command time out: {}".format(command))
      if i == 1:
         print("did not get the (config)# prompt")

   if (args.action == "no_wlan" and (args.wlan is None)):
      raise Exception("wlan is required")
   if (args.action == "no_wlan"):
      egg.sendline("config t")
      sleep(0.1)
      i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
      if i == 0:
         command = "no wlan %s"%(args.wlan)
         egg.sendline(command)
         sleep(0.1)
         j = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
         if j == 0:
            print("command sent: {}".format(command))
         if j == 1:
            print("command timed out {}".format(command))
      if i == 1:
         print("did not get the (config)# prompt")

   if (args.action == "show_wlan_summary"):
      egg.sendline("show wlan summary")
      sleep(0.1)
      i = egg.expect(["#",pexpect.TIMEOUT],timeout=2)
      if i == 0:
         print("show wlan summary sent")
      if i == 1:
         print("show wlan summary timed out")

   if (args.action == "wlan" and (args.wlanID is None)):
      raise Exception("wlan ID is required")
   if (args.action == "wlan"):
      if args.series == "9800":
          egg.sendline("config t")
          i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
          if i == 0:
             print("elevated to (config)#")
             command = "wlan %s %s %s"%(args.wlan, args.wlanID, args.wlan)
             egg.sendline(command)
             j = egg.expect_exact(["(config-wlan)#",pexpect.TIMEOUT],timeout=2)
             if j == 0:
                 for command in ["shutdown","no security wpa","no security wpa wpa2","no security wpa wpa2 ciphers aes",
                        "no security wpa akm dot1x","no shutdown","end"]:
                    egg.sendline(command)
                    sleep(0.1)
                    k = egg.expect_exact(["(config-wlan)#",pexpect.TIMEOUT],timeout=2)
                    if k == 0:
                       print("command sent: {}".format(command))
                    if k == 1:
                         print("command time out: {}".format(command))
             if j == 1:
                print("did not get the (config-wlan)# prompt")
          if i == 0:
             print("did not get the (config)# prompt")
      else:   
         command = "config wlan create %s %s %s"%(args.wlanID, args.wlan, args.wlan)

   if (args.action == ["enable_wlan","disble_wlan"]):
      if args.series == "9800":
         if (args.wlan is None):
            raise Exception("9800 series wlan is required")
         else:
            egg.sendline("config t")
            i = egg.expect_exact(["(config)#",pexpect.TIMEOUT],timeout=2)
            if i == 0:
               print("elevated to (config)#")
               command = "wlan %s"%(args.wlan)
               egg.sendline(command)
               j = egg.expect_exact(["(config-wlan)#",pexpect.TIMEOUT],timeout=2)
               if j == 0:
                  if (args.action == "enable_wlan"):
                      command = "no shutdown"
                  else:
                      command = "shutdown"
                  egg.sendline(command)
                  sleep(0.1)
                  k = egg.expect_exact(["(config-wlan)#",pexpect.TIMEOUT],timeout=2)
                  if k == 0:
                      print("command sent: {}".format(command))
                  if k == 1:
                      print("command timed out: {}".format(command))
               if j == 1:
                  print("did not get the (config-wlan)# prompt")
            if i == 1:
               print("did not get the (config)# prompt")
      else:
         if (args.action == ["enable_wlan","disable_wlan"] and (args.wlanID is None)):
            raise Exception("wlan ID is required")
         if (args.action == "enable_wlan"):
            command = "config wlan enable %s"%(args.wlanID)
         else:   
            command = "config wlan disable %s"%(args.wlanID) 

   if (args.action == "wlan_qos" and (args.wlanID is None)):
      raise Exception("wlan ID is required")
   if (args.action == "wlan_qos"):
      command = "config wlan qos %s %s"%(args.wlanID, args.value)

   if (command is None):
      logg.info("No command specified, going to log out.")
   else:
      logg.info("Command[%s]"%command)
      egg.sendline(command)
      print("command sent {}".format(command))

      sleep(1)
      while True:
         i = egg.expect([">","#", AREYOUSURE, '--More-- or',pexpect.TIMEOUT],timeout=3)
         print (egg.before.decode('utf-8', 'ignore'))
         if i == 0:
            print("> prompt received after command sent")
            break
         if i == 1:
            print("# prompt received after command sent")
            try:
               print("9800 send exit")
               egg.sendline("exit")
            except:
               print("9800 exception on exit")
            sleep(1)
            try:
               print("9800 send carriage return and linefeed")
               egg.sendline("\r\n")
            except:
               print("9800 exception on carriage return and linefeed")
            break
         if i == 2:
            print("are you sure received after command sent")
            egg.sendline("y")
            break
         if i == 3:
            print("--More-- or received")
            egg.sendline(NL)
         if i == 4:
            print("expect timeout")
            break


   if args.series == "9800":
      pass     
   else:
      egg.sendline("logout")
      print("logout")
      i = egg.expect([LOGOUTPROMPT, EXITPROMPT, CLOSEDBYREMOTE, CLOSEDCX,pexpect.TIMEOUT],timeout=3)
      if i == 0:
         egg.sendline("y")
      if i == 4:
         print("pexpect timeout on logout")



# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()

####
####
####
