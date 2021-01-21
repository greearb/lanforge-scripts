#!/usr/bin/python3
'''
LANforge 192.168.100.178
Controller at 192.168.100.112 admin/Cisco123
Controller is 192.1.0.10
AP is on serial port /dev/ttyUSB1  9600 8 n 1

make sure pexpect is installed:
$ sudo yum install python3-pexpect

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial

./cisco_ap_ctl.py 
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
logfile = "stdout"

# regex101.com  , 
# this will be in the tx_power script
# ^\s+1\s+6\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+) 

def usage():
    print("$0 used connect to Cisco AP:")
    print("-a|--ap:  AP to act upon")
    print("-d|--dest:  destination host")
    print("-o|--port:  destination port")
    print("-u|--user:  AP login name")
    print("-p|--pass:  AP password")
    print("-s|--scheme (serial|telnet|ssh): connect to controller via serial, ssh or telnet")
    print("--tty Serial port for accessing AP")
    print("-l|--log file: log messages here")
    print("-b|--band:  a (5Ghz) or b (2.4Ghz) or abgn for dual-band 2.4Ghz AP")
    print("-z|--action: action")
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

    global logfile
    
    parser = argparse.ArgumentParser(description="Cisco AP Control Script")
    parser.add_argument("-a", "--prompt",  type=str, help="ap prompt")
    parser.add_argument("-d", "--dest",    type=str, help="address of the AP  172.19.27.55")
    parser.add_argument("-o", "--port",    type=int, help="control port on the AP, 2008")
    parser.add_argument("-u", "--user",    type=str, help="credential login/username, admin")
    parser.add_argument("-p", "--passwd",  type=str, help="credential password Wnbulab@123")
    parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
    parser.add_argument("-t", "--tty",     type=str, help="tty serial device for connecting to AP")
    parser.add_argument("-l", "--log",     type=str, help="logfile for messages, stdout means output to console")
    parser.add_argument("-z", "--action",  type=str, help="action,  current action is powercfg")

    args = None
    try:
        args = parser.parse_args()
        host = args.dest
        scheme = args.scheme
        port = (default_ports[scheme], args.port)[args.port != None]
        user = args.user
        passwd = args.passwd
        if (args.log != None):
            logfile = args.log
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
    egg = None # think "eggpect"
    ser = None
    try:
        if (scheme == "serial"):
            #eggspect = pexpect.fdpexpect.fdspan(telcon, logfile=sys.stdout.buffer)
            import serial
            from pexpect_serial import SerialSpawn
            ser = serial.Serial(args.tty, 9600, timeout=5)
            print("Created serial connection on %s, open: %s"%(args.tty, ser.is_open))
            egg = SerialSpawn(ser)
            egg.logfile = FileAdapter(logg)
            time.sleep(1)
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
            egg.sendline(args.passwd)
        elif (scheme == "telnet"):
            if (port is None):
                port = 23
            cmd = "telnet {} {}".format(host, port)
            logg.info("Spawn: "+cmd+NL)
            egg = pexpect.spawn(cmd)
            egg.logfile = FileAdapter(logg)
            # Will login below as needed.
        else:
            usage()
            exit(1)
    except Exception as e:
        logging.exception(e)
    
    ap_prompt = "{}>".format(args.prompt)
    ap_hash = "{}#".format(args.prompt)
    egg.sendline()

    egg.sendline()
    time.sleep(0.1)
    egg.expect('Username:', timeout=3)
    time.sleep(0.1)
    egg.sendline(args.user)
    time.sleep(0.1)
    egg.expect('Password:')
    egg.sendline(args.passwd)
    egg.expect(ap_prompt)
    egg.sendline("en")
    egg.expect("Password:")
    egg.sendline(args.passwd)
    egg.expect("#")
    egg.sendline('show controllers dot11Radio 1 powercfg | g T1')
    egg.expect("--More--")
    egg.sendcontrol('c')
    egg.expect("#",timeout=5)
    egg.sendline("exit")
    egg.expect(">",timeout=5)
    egg.sendline("exit")

    #             ctlr.execute(cn_cmd)
if __name__ == '__main__':
    main()

####
####
####
