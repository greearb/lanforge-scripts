#!/usr/bin/python3
'''
LANforge 192.168.100.178
Controller at 192.168.100.112 admin/Cisco123
Controller is 192.1.0.10
AP is 192.1.0.2

make sure pexpect is installed:
$ sudo yum install python3-pexpect
$ sudo yum install python3-xlsxwriter

You might need to install pexpect-serial using pip:
$ pip3 install pexpect-serial
$ pip3 install XlsxWriter

This script will automatically create and start a layer-3 UDP connection between the
configured upstream port and station.

The user is responsible for setting up the station oustide of this script, however.

# Example run to cycle through all 8 power settings
# See cisco_power_results.txt when complete.

./lf_cisco_power.py -d 192.168.100.112 -u admin -p Cisco123 -s ssh --port 22 -a VC --lfmgr 192.168.100.178 \
  --station sta00000 --bandwidth "20" --channel "36" --nss 4 --txpower "1 2 3 4 5 6 7 8" --pathloss 54 \
  --band a --upstream_port eth2 --lfresource2 2
'''

# TODO:  Maybe HTML output too?
# TODO:  Allow selecting tabs or commas for output files

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
import xlsxwriter

NL = "\n"
CR = "\r\n"
Q = '"'
A = "'"
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'

lfmgr = "127.0.0.1"
lfstation = "sta00000"
lfresource = "1"
lfresource2 = "1"
outfile = "cisco_power_results.txt"
full_outfile = "full_cisco_power_results.txt"
outfile_xlsx = "cisco_power_results.xlsx"
upstream_port = "eth1"

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
   print("--outfile: Write results here.")
   print("--station: LANforge station name")
   print("--lfmgr: LANforge manager IP address")
   print("--lfresource: LANforge resource ID for station")
   print("--lfresource2: LANforge resource ID for upstream port")
   print("--pathloss:  Calculated path-loss between LANforge station and AP")
   print("--band:  Select band (a | b | abgn), a means 5Ghz, b means 2.4, abgn means 2.4 on dual-band AP")
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
   global lfmgr
   global lfstation
   global lfresource
   global lfresource2
   global outfile
   global outfile_xlsx
   global full_outfile
   global upstream_port
    
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
   parser.add_argument("-b", "--bandwidth",        type=str, help="List of bandwidths to test. NA means no change")
   parser.add_argument("-c", "--channel",        type=str, help="List of channels to test. NA means no change")
   parser.add_argument("-n", "--nss",        type=str, help="List of spatial streams to test.  NA means no change")
   parser.add_argument("-T", "--txpower",        type=str, help="List of txpowers to test.  NA means no change")

   parser.add_argument("--upstream_port",  type=str, help="LANforge upsteram-port to use (eth1, etc)")
   parser.add_argument("--station",        type=str, help="LANforge station to use (sta0000, etc)")
   parser.add_argument("--lfmgr",        type=str, help="LANforge Manager IP address")
   parser.add_argument("--lfresource",        type=str, help="LANforge resource ID for the station")
   parser.add_argument("--lfresource2", type=str, help="LANforge resource ID for the upstream port system")
   parser.add_argument("--outfile",     type=str, help="Output file for csv data")
   parser.add_argument("--pathloss",     type=str, help="Calculated pathloss between LANforge Station and AP")
   parser.add_argument("--band",    type=str, help="Select band (a | b), a means 5Ghz, b means 2.4Ghz.  Default is a",
                       choices=["a", "b", "abgn"])
   
   args = None
   try:
      args = parser.parse_args()
      host = args.dest
      scheme = args.scheme
      user = args.user
      passwd = args.passwd
      logfile = args.log
      if (args.station != None):
          lfstation = args.station
      if (args.upstream_port != None):
          upstream_port = args.upstream_port
      if (args.lfmgr != None):
          lfmgr = args.lfmgr
      if (args.lfresource != None):
          lfresource = args.lfresource
      if (args.lfresource2 != None):
          lfresource2 = args.lfresource2
      if (args.outfile != None):
          outfile = args.outfile
          full_outfile = "full-%s"%(outfile)
          outfile_xlsx = "%s.xlsx"%(outfile)
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

   if (args.bandwidth == None):
       print("ERROR:  Must specify bandwidths")
       exit(1)

   if (args.channel == None):
       print("ERROR:  Must specify channels")
       exit(1)

   if (args.nss == None):
       print("ERROR:  Must specify NSS")
       exit(1)

   if (args.txpower == None):
       print("ERROR:  Must specify txpower")
       exit(1)

   if (args.pathloss == None):
       print("ERROR:  Pathloss must be specified.")
       exit(1)

   # Full spread-sheet data
   csv = open(full_outfile, "w")
   csv.write("Cabling Pathloss\tCfg-Channel\tCfg-NSS\tCfg-AP-BW\tTx Power\tBeacon-Signal\tCombined-Signal\tRSSI 1\tRSSI 2\tRSSI 3\tRSSI 4\tAP-BSSID\tRpt-BW\tRpt-Channel\tRpt-Mode\tRpt-NSS\tRpt-Noise\tRpt-Rxrate\tCtrl-AP-MAC\tCtrl-Channel\tCtrl-Power\tCtrl-dBm\tCalc-dBm-Combined\tDiff-dBm-Combined\tAnt-1\tAnt-2\tAnt-3\tAnt-4\tOffset-1\tOffset-2\tOffset-3\tOffset-4\tPASS/FAIL(+-3dB)\tWarnings-and-Errors")
   csv.write("\n");
   csv.flush()

   # Summary spread-sheet data
   csvs = open(outfile, "w")
   csvs.write("Cabling Pathloss\tAP Channel\tNSS\tAP BW\tTx Power\tAllowed Per-Path\tRSSI 1\tRSSI 2\tRSSI 3\tRSSI 4\tAnt-1\tAnt-2\tAnt-3\tAnt-4\tOffset-1\tOffset-2\tOffset-3\tOffset-4\tPASS/FAIL(+-3dB)\tWarnings-and-Errors")
   csvs.write("\n");
   csvs.flush()

   # XLSX file
   row = 1 # Skip header line, we write it below
   workbook = xlsxwriter.Workbook(outfile_xlsx)
   worksheet = workbook.add_worksheet()

   bold = workbook.add_format({'bold': True, 'align': 'center'})
   dblue_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dblue_bold.set_bg_color("#b8cbe4")
   dblue_bold.set_border(1)
   dtan_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dtan_bold.set_bg_color("#dcd8c3")
   dtan_bold.set_border(1)
   dpeach_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dpeach_bold.set_bg_color("#ffd8bb")
   dpeach_bold.set_border(1)
   dpink_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dpink_bold.set_bg_color("#fcc8ca")
   dpink_bold.set_border(1)
   dyel_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dyel_bold.set_bg_color("#ffe699")
   dyel_bold.set_border(1)
   dgreen_bold = workbook.add_format({'bold': True, 'align': 'center'})
   dgreen_bold.set_bg_color("#c6e0b4")
   dgreen_bold.set_border(1)
   dgreen_bold_left = workbook.add_format({'bold': True, 'align': 'left'})
   dgreen_bold_left.set_bg_color("#c6e0b4")
   dgreen_bold_left.set_border(1)
   center = workbook.add_format({'align': 'center'})
   center_blue = workbook.add_format({'align': 'center'})
   center_blue.set_bg_color("#dbe5f1")
   center_blue.set_border(1)
   center_tan = workbook.add_format({'align': 'center'})
   center_tan.set_bg_color("#edede1")
   center_tan.set_border(1)
   center_peach = workbook.add_format({'align': 'center'})
   center_peach.set_bg_color("#fce4d6")
   center_peach.set_border(1)
   center_yel = workbook.add_format({'align': 'center'})
   center_yel.set_bg_color("#fdf2cc")
   center_yel.set_border(1)
   center_pink = workbook.add_format({'align': 'center'})
   center_pink.set_bg_color("ffd2d3")
   center_pink.set_border(1)
   red = workbook.add_format({'color': 'red', 'align': 'center'})
   red.set_bg_color("#e0efda")
   red.set_border(1)
   red_left = workbook.add_format({'color': 'red', 'align': 'left'})
   red_left.set_bg_color("#e0efda")
   red_left.set_border(1)
   green = workbook.add_format({'color': 'green', 'align': 'center'})
   green.set_bg_color("#e0efda")
   green.set_border(1)
   green_left = workbook.add_format({'color': 'green', 'align': 'left'})
   green_left.set_bg_color("#e0efda")
   green_left.set_border(1)

   worksheet.set_row(0, 45) # Set height
   worksheet.set_column(19, 19, 100) # Set width

   worksheet.write('A1', 'AP\nChannel', dblue_bold)
   worksheet.write('B1', 'NSS', dblue_bold)
   worksheet.write('C1', 'AP\nBW', dblue_bold)
   worksheet.write('D1', 'Tx\nPower', dtan_bold)
   worksheet.write('E1', 'Allowed\nPer\nPath', dtan_bold)
   worksheet.write('F1', 'Cabling\nPathloss', dtan_bold)
   worksheet.write('G1', 'RSSI\n1', dpeach_bold)
   worksheet.write('H1', 'RSSI\n2', dpeach_bold)
   worksheet.write('I1', 'RSSI\n3', dpeach_bold)
   worksheet.write('J1', 'RSSI\n4', dpeach_bold)
   worksheet.write('K1', 'Ant\n1', dpink_bold)
   worksheet.write('L1', 'Ant\n2', dpink_bold)
   worksheet.write('M1', 'Ant\n3', dpink_bold)
   worksheet.write('N1', 'Ant\n4', dpink_bold)
   worksheet.write('O1', 'Offset\n1', dyel_bold)
   worksheet.write('P1', 'Offset\n2', dyel_bold)
   worksheet.write('Q1', 'Offset\n3', dyel_bold)
   worksheet.write('R1', 'Offset\n4', dyel_bold)
   worksheet.write('S1', 'PASS\n/\nFAIL', dgreen_bold)
   worksheet.write('T1', 'Warnings and Errors', dgreen_bold_left)

   bandwidths = args.bandwidth.split()
   channels = args.channel.split()
   nss = args.nss.split()
   txpowers = args.txpower.split()

   # Find LANforge station parent radio
   parent = None
   port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                "--show_port", "Parent/Peer"], capture_output=True);
   pss = port_stats.stdout.decode('utf-8', 'ignore');
   for line in pss.splitlines():
       m = re.search('Parent/Peer:\s+(.*)', line)
       if (m != None):
           parent = m.group(1)

   # Create downstream connection
   # First, delete any old one
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "rm_cx all c-udp-power"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "rm_endp c-udp-power-A"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource2, "--action", "do_cmd",
                   "--cmd", "rm_endp c-udp-power-B"], capture_output=True);

   # Now, create the new connection
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "create_endp", "--port_name", lfstation,
                   "--endp_type", "lf_udp", "--endp_name", "c-udp-power-A", "--speed", "0", "--report_timer", "1000"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource2, "--action", "create_endp", "--port_name", upstream_port,
                   "--endp_type", "lf_udp", "--endp_name", "c-udp-power-B", "--speed", "1000000", "--report_timer", "1000"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "create_cx", "--cx_name", "c-udp-power",
                   "--cx_endps", "c-udp-power-A,c-udp-power-B", "--report_timer", "1000"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "set_cx_state all c-udp-power RUNNING"], capture_output=True);

   for ch in channels:
       for n in nss:
           for bw in bandwidths:
               if (n != "NA"):
                   if (parent == None):
                       print("ERROR:  Skipping setting the spatial streams because cannot find Parent radio for station.")
                   else:
                       # Set nss on LANforge Station, not sure it can be done on AP
                       ni = int(n);
                       if (bw == "160"):
                           # 9984 hardware needs 2 chains to do one NSS at 160Mhz
                           if (ni > 2):
                               print("NOTE: Skipping NSS %s for 160Mhz, LANforge radios do not support more than 2NSS at 160Mhz currently."%(n))
                               continue
                           else:
                               # Set radio to 2x requested value for 160Mhz
                               ni *= 2
                   antset = 0 # all available
                   if (ni == 1):
                       antset = 1
                   if (ni == 2):
                       antset = 4
                   if (ni == 3):
                       antset = 7
                   set_cmd = "set_wifi_radio 1 %s %s NA NA NA NA NA NA NA NA NA %s"%(lfresource, parent, antset)
                   print("Setting LANforge radio to %s NSS with command: %s"%(ni, set_cmd))
                   subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", parent,
                                   "--cli_cmd", set_cmd], capture_output=True)
               
               for tx in txpowers:

                   # TODO:  Down station
                   port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                "--set_ifstate", "down"]);
                   
                   # Disable AP, apply settings, enable AP
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "disable"])
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11a disable network"])
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11b disable network"])

                   if (tx != "NA"):
                       subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                       "--action", "txPower", "--value", tx])
                   if (bw != "NA"):
                       subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                       "--action", "bandwidth", "--value", bw])

                   # NSS is set on the station earlier...
                       
                   if (ch != "NA"):
                       subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                       "--action", "channel", "--value", ch])
                   
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11a enable network"])
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "cmd", "--value", "config 802.11b enable network"])
                   subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                   "--action", "enable"])

                   # Wait a bit for AP to come back up
                   time.sleep(1);
                   advanced = subprocess.run(["./cisco_wifi_ctl.py", "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band, "-s", "ssh",
                                              "--action", "advanced"], capture_output=True)
                   pss = advanced.stdout.decode('utf-8', 'ignore');
                   print(pss)

                   searchap = False
                   cc_mac = ""
                   cc_ch = ""
                   cc_power = ""
                   cc_dbm = ""
                   for line in pss.splitlines():
                       if (line.startswith("---------")):
                           searchap = True
                           continue

                       if (searchap):
                           pat = "%s\s+(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+\(\s*(\S+)\s+dBm"%(args.ap)
                           m = re.search(pat, line)
                           if (m != None):
                               cc_mac = m.group(1)
                               cc_ch = m.group(2);
                               cc_power = m.group(3)
                               cc_power = cc_power.replace("/", " of ", 1) # spread-sheets turn 1/8 into a date
                               cc_dbm = m.group(4)
                               break

                   # Up station
                   subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                   "--set_ifstate", "up"]);

                   i = 0
                   wait_ip_print = False;
                   wait_assoc_print = False;
                   # Wait untill LANforge station connects
                   while True:
                       port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                    "--show_port", "AP,IP,Mode,NSS,Bandwidth,Channel,Signal,Noise,Status,RX-Rate"], capture_output=True);
                       pss = port_stats.stdout.decode('utf-8', 'ignore');

                       _status = None
                       _ip = None

                       for line in pss.splitlines():
                           m = re.search('Status:\s+(.*)', line)
                           if (m != None):
                               _status = m.group(1)
                           m = re.search('IP:\s+(.*)', line)
                           if (m != None):
                               _ip = m.group(1)

                       #print("IP %s  Status %s"%(_ip, _status))
                       
                       if (_status == "Authorized"):
                           if ((_ip != None) and (_ip != "0.0.0.0")):
                               print("Station is associated with IP address.")
                               break
                           else:
                               if (not wait_ip_print):
                                   print("Waiting for station to get IP Address.")
                                   wait_ip_print = True
                       else:
                           if (not wait_assoc_print):
                               print("Waiting for station to associate.")
                               wait_assoc_print = True

                       i += 1
                       if (i > 60):
                           print("ERROR:  Station did not connect within 60 seconds.")
                           break

                       time.sleep(1)

                   # Wait 10 more seconds
                   print("Waiting 10 seconds to let traffic run for a bit, Channel %s NSS %s BW %s TX-Power %s"%(ch, n, bw, tx))
                   time.sleep(10)

                   # Gather probe results and record data, verify NSS, BW, Channel
                   i = 0;
                   beacon_sig = None
                   sig = None
                   ants = []
                   while True:                       
                       time.sleep(1)
                       port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                    "--cli_cmd", "probe_port 1 %s %s"%(lfresource, lfstation)], capture_output=True);
                       pss = port_stats.stdout.decode('utf-8', 'ignore');

                       foundit = False
                       for line in pss.splitlines():
                           #print("probe-line: %s"%(line))
                           m = re.search('signal avg:\s+(\S+)\s+\[(.*)\]\s+dBm', line)
                           if (m != None):
                               sig = m.group(1)
                               ants = m.group(2).split();
                               q = 0
                               for a in ants:
                                   ants[q] = ants[q].replace(",", "", 1)
                                   q += 1

                               #print("sig: %s  ants: %s ants-len: %s n: %s"%(sig, m.group(2), len(ants), n))

                               if (len(ants) == int(n)):
                                   foundit = True
                               else:
                                   print("Looking for %s spatial streams, signal avg reported fewer: %s"%(n, m.group(1)))

                           m = re.search('beacon signal avg:\s+(\S+)\s+dBm', line)
                           if (m != None):
                               beacon_sig = m.group(1)
                               
                       if (foundit):
                           break

                       i += 1
                       if (i > 10):
                           print("Tried and failed 10 times to find correct spatial streams, continuing.")
                           while (len(ants) < int(n)):
                               ants.append("")
                               break
                           break

                   antstr = ""
                   for x in range(4):
                       if (x < int(n)):
                           antstr += ants[x]
                       else:
                           antstr += " "
                       antstr += "\t"

                   port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                    "--show_port", "AP,IP,Mode,NSS,Bandwidth,Channel,Signal,Noise,Status,RX-Rate"], capture_output=True);
                   pss = port_stats.stdout.decode('utf-8', 'ignore');

                   _ap = None
                   _bw = None
                   _ch = None
                   _mode = None
                   _nss = None
                   _noise = None
                   _rxrate = None

                   for line in pss.splitlines():
                       m = re.search('AP:\s+(.*)', line)
                       if (m != None):
                           _ap = m.group(1)
                       m = re.search('Bandwidth:\s+(.*)Mhz', line)
                       if (m != None):
                           _bw = m.group(1)
                       m = re.search('Channel:\s+(.*)', line)
                       if (m != None):
                           _ch = m.group(1)
                       m = re.search('Mode:\s+(.*)', line)
                       if (m != None):
                           _mode = m.group(1)
                       m = re.search('NSS:\s+(.*)', line)
                       if (m != None):
                           _nss = m.group(1)
                       m = re.search('Noise:\s+(.*)', line)
                       if (m != None):
                           _noise = m.group(1)
                       m = re.search('RX-Rate:\s+(.*)', line)
                       if (m != None):
                           _rxrate = m.group(1)

                   pi = int(args.pathloss)
                   calc_dbm = int(sig) + pi
                   calc_ant1 = int(ants[0]) + pi
                   calc_ant2 = 0
                   calc_ant3 = 0
                   calc_ant4 = 0
                   if (len(ants) > 1):
                       calc_ant2 = int(ants[1]) + pi
                   if (len(ants) > 2):
                       calc_ant3 = int(ants[2]) + pi
                   if (len(ants) > 3):
                       calc_ant4 = int(ants[3]) + pi

                   diff_a1 = ""
                   diff_a2 = ""
                   diff_a3 = ""
                   diff_a4 = ""

                   cc_dbmi = int(cc_dbm)
                   diff_dbm = calc_dbm - cc_dbmi
                   pf = 1
                   pfs = "PASS"
                   pfrange = 3;
                   allowed_per_path = cc_dbmi
                   if (int(_nss) == 1):
                       diff_a1 = calc_ant1 - cc_dbmi
                       if (abs(diff_a1) > pfrange):
                           pf = 0
                   if (int(_nss) == 2):
                       allowed_per_path = cc_dbmi - 3
                       diff_a1 = calc_ant1 - allowed_per_path
                       diff_a2 = calc_ant2 - allowed_per_path
                       if ((abs(diff_a1) > pfrange) or
                           (abs(diff_a2) > pfrange)):
                           pf = 0
                   if (int(_nss) == 3):
                       allowed_per_path = cc_dbmi - 5
                       diff_a1 = calc_ant1 - allowed_per_path
                       diff_a2 = calc_ant2 - allowed_per_path
                       diff_a3 = calc_ant3 - allowed_per_path
                       if ((abs(diff_a1) > pfrange) or
                           (abs(diff_a2) > pfrange) or
                           (abs(diff_a3) > pfrange)):
                           pf = 0
                   if (int(_nss) == 4):
                       allowed_per_path = cc_dbmi - 6
                       diff_a1 = calc_ant1 - allowed_per_path
                       diff_a2 = calc_ant2 - allowed_per_path
                       diff_a3 = calc_ant3 - allowed_per_path
                       diff_a4 = calc_ant4 - allowed_per_path
                       if ((abs(diff_a1) > pfrange) or
                           (abs(diff_a2) > pfrange) or
                           (abs(diff_a3) > pfrange) or
                           (abs(diff_a4) > pfrange)):
                           pf = 0

                   if (pf == 0):
                       pfs = "FAIL"
                       
                   ln = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(
                       args.pathloss, ch, n, bw, tx, beacon_sig, sig,
                       antstr, _ap, _bw, _ch, _mode, _nss, _noise, _rxrate,
                       cc_mac, cc_ch, cc_power, cc_dbm,
                       calc_dbm, diff_dbm, calc_ant1, calc_ant2, calc_ant3, calc_ant4,
                       diff_a1, diff_a2, diff_a3, diff_a4, pfs
                     )

                   #print("RESULT: %s"%(ln))
                   csv.write(ln)
                   csv.write("\t")

                   ln = "%s\t%s\t%s\t%s\t%s\t%s\t%s%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(
                       args.pathloss, _ch, _nss, _bw, tx, allowed_per_path,
                       antstr,
                       calc_ant1, calc_ant2, calc_ant3, calc_ant4,
                       diff_a1, diff_a2, diff_a3, diff_a4, pfs
                       )
                   csvs.write(ln)
                   csvs.write("\t")

                   col = 0
                   worksheet.write(row, col, _ch, center_blue); col += 1
                   worksheet.write(row, col, _nss, center_blue); col += 1
                   worksheet.write(row, col, _bw, center_blue); col += 1
                   worksheet.write(row, col, tx, center_tan); col += 1
                   worksheet.write(row, col, allowed_per_path, center_tan); col += 1
                   worksheet.write(row, col, args.pathloss, center_tan); col += 1
                   for x in range(4):
                       if (x < int(n), center):
                           worksheet.write(row, col, ants[x], center_peach); col += 1
                       else:
                           worksheet.write(row, col, " ", center_peach); col += 1
                   worksheet.write(row, col, calc_ant1, center_pink); col += 1
                   worksheet.write(row, col, calc_ant2, center_pink); col += 1
                   worksheet.write(row, col, calc_ant3, center_pink); col += 1
                   worksheet.write(row, col, calc_ant4, center_pink); col += 1
                   worksheet.write(row, col, diff_a1, center_yel); col += 1
                   worksheet.write(row, col, diff_a2, center_yel); col += 1
                   worksheet.write(row, col, diff_a3, center_yel); col += 1
                   worksheet.write(row, col, diff_a4, center_yel); col += 1
                   if (pfs == "FAIL"):
                       worksheet.write(row, col, pfs, red); col += 1
                   else:
                       worksheet.write(row, col, pfs, green); col += 1

                   e_tot = ""
                   if (_bw != bw):
                       err = "ERROR:  Requested bandwidth: %s != station's reported bandwidth: %s.  "%(bw, _bw)
                       e_tot += err
                       print(err)
                       csv.write(err)
                       csvs.write(err)
                   if (_nss != n):
                       err = "ERROR:  Station NSS: %s != configured: %s.  "%(_nss, n)
                       print(err)
                       csv.write(err)
                       csvs.write(err)
                       e_tot += err

                   if (e_tot == ""):
                       worksheet.write(row, col, e_tot, green_left); col += 1
                   else:
                       worksheet.write(row, col, e_tot, red_left); col += 1
                   row += 1

                   csv.write("\n");
                   csv.flush()

                   csvs.write("\n");
                   csvs.flush()

   workbook.close()


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()
    print("Summary results stored in %s, full results in %s, xlsx file in %s"%(outfile, full_outfile, outfile_xlsx))

####
####
####
