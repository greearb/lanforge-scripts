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
  --station sta00000 --bandwidth "20" --channel "36" --nss 4 --txpower "1 2 3 4 5 6 7 8" --pathloss 64 \
  --band a --upstream_port eth2 --lfresource2 2

# Per-channel path-loss example
./lf_cisco_power.py -d 192.168.100.112 -u admin -p Cisco123 -s ssh --port 22 -a VC --lfmgr 192.168.100.178 \
  --station sta00000 --bandwidth "20 40 80 160" --channel "36:64 149:60" --nss 4 --txpower "1 2 3 4 5 6 7 8" --pathloss 64 \
  --band a --upstream_port eth2 --lfresource2 2

# To create a station run test against station create open-wlan 
./lf_cisco_power.py -d <router IP> -u admin -p Cisco123 -port 2043 --scheme telnet --ap AP6C71.0DE6.45D0 \
--station sta2222 --bandwidth "20" --channel "36" --nss 4 --txpower "1 2 3 4 5 6 7 8" --pathloss 54 --band a \
--upstream_port eth2 --series 9800 --wlan open-wlan --wlanID 1 --create_station sta2222 --radio wiphy1 --ssid open-wlan \
--ssidpw [BLANK] --security open

# station already present
./lf_cisco_power.py -d <router IP> -u admin -p Cisco123 -port 2043 --scheme telnet --ap AP6C71.0DE6.45D0 \
--station sta0000 --bandwidth "20" --channel "36" --nss 4 --txpower "1 2 3 4 5 6 7 8" --pathloss 64 --band a \
--upstream_port eth2 --series 9800 --wlan open-wlan --wlanID 1 

# to create a station 
./lf_associate_ap.pl --radio wiphy1 --ssid open-wlan --passphrase [BLANK] ssecurity open --upstream eth1\
--first_ip DHCP --first_sta sta0001 --duration 5 --cxtype udp


Changing regulatory domain should happen outside of this script.  See cisco_ap_ctl.py

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
full_outfile = "cisco_power_results_full.txt"
outfile_xlsx = "cisco_power_results.xlsx"
upstream_port = "eth1"
pf_dbm = 6
# Allow one chain to have a lower signal, since customer's DUT has
# lower tx-power on one chain when doing high MCS at 4x4.
pf_a4_dropoff = 3

# This below is only used when --adjust_nf is used.
# Noise floor on ch 36 where we calibrated -54 path loss (based on hard-coded -95 noise-floor in driver)
nf_at_calibration = -105
# older ath10k driver hard-codes noise-floor to -95 when calculating RSSI
# RSSI = NF + reported_power
# Shift RSSI by difference in actual vs calibrated noise-floor since driver hard-codes
# the noise floor.

# rssi_adjust = (current_nf - nf_at_calibration)

def usage():
   print("$0 used connect to controller:")
   print("-a|--ap:  AP to act upon")
   print("-d|--dest:  destination host")
   print("-o|--port:  destination port")
   print("-u|--user:  login name")
   print("-p|--passwd:  password")
   print("-s|--scheme (serial|telnet|ssh): connect via serial, ssh or telnet")
   print("-t|--tty tty serial device")
   print("-l|--log file: log messages here ,stdout means output to console")
   print("-a|--ap select AP")
   print("-b|--bandwidth: List of bandwidths to test: 20 40 80 160")
   print("-c|--channel: List of channels, with optional path-loss to test: 36:64 100:60")
   print("-n|--nss: List of spatial streams to test: 1 2 3 4")
   print("-T|--txpower: List of TX power values to test: 1 2 3 4 5 6 7 8")
   print("--series:  9800 the default is 3504")
   print("-k|--keep_state  keep the state, no configuration change at the end of the test, store true flage present ")
   print("--outfile: Write results here.")
   print("--station: LANforge station name for test(sta00000)")
   print("--upstream_port: LANforge upstream port name (eth1)")
   print("--lfmgr: LANforge manager IP address")
   print("--lfresource: LANforge resource ID for station")
   print("--lfresource2: LANforge resource ID for upstream port")
   print("--outfile: Output file for csv data")
   print("--pathloss:  Calculated path-loss between LANforge station and AP")
   print("--band:  Select band (a | b | abgn), a means 5Ghz, b means 2.4, abgn means 2.4 on dual-band AP")
   print("--pf_dbm: Pass/Fail range, default is 6")
   print("--pf_a4_dropoff: Allow one chain to use lower tx-power and still pass when doing 4x4.  Default is 3")
   print("--wait_forever: Wait forever for station to associate, may aid debugging if STA cannot associate properly")
   print("--adjust_nf: Adjust RSSI based on noise-floor.  ath10k without the use-real-noise-floor fix needs this option")
   print("--wlan: for 9800, wlan identifier defaults to wlan-open")
   print("--wlanID: wlanID  for 9800 , defaults to 1")
   print("--series: controller series  9800 , defaults to 3504")
   print("--create_station", "create LANforge station at the beginning of the test")
   print("--radio", "radio to create LANforge station on at the beginning of the test")
   print("--ssid", "ssid default open-wlan")
   print("--ssidpw", "ssidpw default [BLANK]")
   print("--security", "security default open")
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
   global pf_dbm
   global pf_a4_dropoff

   scheme = "ssh"

   parser = argparse.ArgumentParser(description="Cisco TX Power report Script")
   parser.add_argument("-d", "--dest",    type=str, help="address of the cisco controller")
   parser.add_argument("-o", "--port",    type=str, help="control port on the controller", default=23)
   parser.add_argument("-u", "--user",    type=str, help="credential login/username")
   parser.add_argument("-p", "--passwd",  type=str, help="credential password")
   parser.add_argument("-s", "--scheme",  type=str, choices=["serial", "ssh", "telnet"], help="Connect via serial, ssh or telnet")
   parser.add_argument("-t", "--tty",     type=str, help="tty serial device")
   parser.add_argument("-l", "--log",     type=str, help="logfile for messages, stdout means output to console")
   #parser.add_argument("-r", "--radio",   type=str, help="select radio")
   parser.add_argument("-a", "--ap",       type=str, help="select AP")
   parser.add_argument("-b", "--bandwidth",  type=str, help="List of bandwidths to test. NA means no change")
   parser.add_argument("-c", "--channel",    type=str, help="List of channels to test, with optional path-loss, 36:64 149:60. NA means no change")
   parser.add_argument("-n", "--nss",        type=str, help="List of spatial streams to test.  NA means no change")
   parser.add_argument("-T", "--txpower",    type=str, help="List of txpowers to test.  NA means no change")

   parser.add_argument("-k","--keep_state", help="keep the state, no configuration change at the end of the test",action="store_true")

   parser.add_argument("--station",        type=str, help="LANforge station to use (sta0000, etc)")
   parser.add_argument("--upstream_port",  type=str, help="LANforge upsteram-port to use (eth1, etc)")

   parser.add_argument("--lfmgr",        type=str, help="LANforge Manager IP address")
   parser.add_argument("--lfresource",        type=str, help="LANforge resource ID for the station")
   parser.add_argument("--lfresource2", type=str, help="LANforge resource ID for the upstream port system")
   parser.add_argument("--outfile",     type=str, help="Output file for csv data",default="cisco_power_results")
   parser.add_argument("--pathloss",     type=str, help="Calculated pathloss between LANforge Station and AP")
   parser.add_argument("--band",    type=str, help="Select band (a | b), a means 5Ghz, b means 2.4Ghz.  Default is a",
                       choices=["a", "b", "abgn"])
   parser.add_argument("--pf_dbm",        type=str, help="Pass/Fail threshold.  Default is 6")
   parser.add_argument("--pf_a4_dropoff", type=str, help="Allow one chain to use lower tx-power and still pass when doing 4x4.  Default is 3")
   parser.add_argument("--wait_forever", action='store_true', help="Wait forever for station to associate, may aid debugging if STA cannot associate properly")
   parser.add_argument("--adjust_nf", action='store_true', help="Adjust RSSI based on noise-floor.  ath10k without the use-real-noise-floor fix needs this option")

   parser.add_argument("--wlan",        type=str, help="--wlan  9800, wlan identifier defaults to wlan-open",default="wlan-open")
   parser.add_argument("--wlanID",      type=str, help="--wlanID  9800 , defaults to 1",default="1")
   parser.add_argument("--series",        type=str, help="--series  9800 , defaults to 3504",default="3504")
   parser.add_argument("--slot",        type=str, help="--slot 1 , 9800 AP slot defaults to 1",default="1")

   parser.add_argument("--rssi",    type=str, help="Select rssi to use for calculation (combined | beacon) Default is beacon",choices=["beacon","combined"])

   parser.add_argument("--create_station",       type=str, help="create LANforge station at the beginning of the test")
   parser.add_argument("--radio",       type=str, help="radio to create LANforge station on at the beginning of the test")
   parser.add_argument("--ssid",       type=str, help="ssid default open-wlan",default="open-wlan")
   parser.add_argument("--ssidpw",       type=str, help="ssidpw default [BLANK]",default="[BLANK]")
   parser.add_argument("--security",       type=str, help="security default open",default="open")

   parser.add_argument("--verbose",    help="--verbose , switch present will have verbose logging", action='store_true')


   args = None
   try:
      args = parser.parse_args()
      host = args.dest
      if (args.scheme != None):
         scheme = args.scheme
      user = args.user
      passwd = args.passwd
      logfile = args.log
      port = args.port
      if (args.station != None):
          lfstation = args.station
      if (args.create_station != None):
          lfstation = args.create_station
          if (args.station != None):
              print("NOTE: both station: {} and create_station: {} on command line, test will use create_station {} ".format(args.station, args.create_station, args.create_station))
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
      if(args.rssi != None):
          rssi_to_use = args.rssi 
      else:
          rssi_to_use = "combined"
      if (args.pf_dbm != None):
          pf_dbm = args.pf_dbm
      if (args.pf_a4_dropoff != None):
          pf_a4_dropoff = args.pf_p4_dropoff
      if (args.verbose):
          # capture the controller output , thus won't got to stdout some output always present
          cap_ctl_out = False
      else:
          cap_ctl_out = True        

      if args.outfile != None:
        current_time = time.strftime("%m_%d_%Y_%H_%M_%S", time.localtime())
        outfile = "{}_{}.txt".format(args.outfile,current_time)
        full_outfile = "{}_full_{}.txt".format(args.outfile,current_time)
        outfile_xlsx = "{}_{}.xlsx".format(args.outfile,current_time)
        print("output file: {}".format(outfile))
        print("output file full: {}".format(full_outfile))
        print("output file xlsx: {}".format(outfile_xlsx))

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

   if (rssi_to_use == "beacon"):
       use_beacon   = "-USED"
       use_combined = ""
   else:
       use_beacon   = ""
       use_combined = "-USED"

        
   # Full spread-sheet data
   csv = open(full_outfile, "w")
   csv.write("Regulatory Domain\tCabling Pathloss\tCfg-Channel\tCfg-NSS\tCfg-AP-BW\tTx Power\tBeacon-Signal%s\tCombined-Signal%s\tRSSI 1\tRSSI 2\tRSSI 3\tRSSI 4\tAP-BSSID\tRpt-BW\tRpt-Channel\tRpt-Mode\tRpt-NSS\tRpt-Noise\tRpt-Rxrate\tCtrl-AP-MAC\tCtrl-Channel\tCtrl-Power\tCtrl-dBm\tCalc-dBm-Combined\tDiff-dBm-Combined\tAnt-1\tAnt-2\tAnt-3\tAnt-4\tOffset-1\tOffset-2\tOffset-3\tOffset-4\tPASS/FAIL(+-%sdB)\tWarnings-and-Errors"%(use_beacon,use_combined,pf_dbm))
   csv.write("\n");
   csv.flush()

   # Summary spread-sheet data
   csvs = open(outfile, "w")
   csvs.write("Regulatory Domain\tCabling Pathloss\tAP Channel\tNSS\tAP BW\tTx Power\tAllowed Per-Path\tRSSI 1\tRSSI 2\tRSSI 3\tRSSI 4\tAnt-1\tAnt-2\tAnt-3\tAnt-4\tOffset-1\tOffset-2\tOffset-3\tOffset-4\tPASS/FAIL(+-%sdB)\tWarnings-and-Errors"%(pf_dbm))
   csvs.write("\n");
   csvs.flush()

   # XLSX file
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
   center_yel_red = workbook.add_format({'align': 'center', 'color': 'red'})
   center_yel_red.set_bg_color("#fdf2cc")
   center_yel_red.set_border(1)
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
   worksheet.set_column(0, 0, 10) # Set width

   col = 0
   row = 0
   worksheet.write(row, col, 'Regulatory\nDomain', dblue_bold); col += 1
   worksheet.write(row, col, 'AP\nChannel', dblue_bold); col += 1
   worksheet.write(row, col, 'NSS', dblue_bold); col += 1
   worksheet.set_column(col, col, 10) # Set width
   worksheet.write(row, col, 'Controller\nBW', dblue_bold); col += 1
   worksheet.write(row, col, 'STA\nRpt\nBW', dblue_bold); col += 1
   worksheet.write(row, col, 'Tx\nPower', dtan_bold); col += 1
   worksheet.write(row, col, 'Allowed\nPer\nPath', dtan_bold); col += 1
   worksheet.write(row, col, 'Cabling\nPathloss', dtan_bold); col += 1
   worksheet.write(row, col, 'Noise\n', dpeach_bold); col += 1
   if (args.adjust_nf):
       worksheet.write(row, col, 'Noise\nAdjust\n(vs -105)', dpeach_bold); col += 1

   worksheet.set_column(col, col, 15) # Set width
   worksheet.write(row, col, 'Last\nMCS\n', dpeach_bold); col += 1
   if(rssi_to_use == "beacon"):
       worksheet.set_column(col, col, 10) # Set width
       worksheet.write(row, col, 'Beacon\nRSSI USED\n', dpeach_bold); col += 1
       worksheet.set_column(col, col, 10) # Set width
       worksheet.write(row, col, 'Combined\nRSSI\n', dpeach_bold); col += 1
   else:
       worksheet.set_column(col, col, 10) # Set width
       worksheet.write(row, col, 'Beacon\nRSSI\n', dpeach_bold); col += 1
       worksheet.set_column(col, col, 10) # Set width
       worksheet.write(row, col, 'Combined\nRSSI USED\n', dpeach_bold); col += 1
   worksheet.write(row, col, 'RSSI\n1', dpeach_bold); col += 1
   worksheet.write(row, col, 'RSSI\n2', dpeach_bold); col += 1
   worksheet.write(row, col, 'RSSI\n3', dpeach_bold); col += 1
   worksheet.write(row, col, 'RSSI\n4', dpeach_bold); col += 1
   worksheet.write(row, col, 'Ant\n1', dpink_bold); col += 1
   worksheet.write(row, col, 'Ant\n2', dpink_bold); col += 1
   worksheet.write(row, col, 'Ant\n3', dpink_bold); col += 1
   worksheet.write(row, col, 'Ant\n4', dpink_bold); col += 1
   worksheet.write(row, col, 'Offset\n1', dyel_bold); col += 1
   worksheet.write(row, col, 'Offset\n2', dyel_bold); col += 1
   worksheet.write(row, col, 'Offset\n3', dyel_bold); col += 1
   worksheet.write(row, col, 'Offset\n4', dyel_bold); col += 1
   worksheet.set_column(col, col, 12) # Set width
   worksheet.write(row, col, "PASS /\nFAIL\n( += %s dBm)"%(pf_dbm), dgreen_bold); col += 1
   worksheet.set_column(col, col, 100) # Set width
   worksheet.write(row, col, 'Warnings and Errors', dgreen_bold_left); col += 1
   row += 1

   bandwidths = args.bandwidth.split()
   channels = args.channel.split()
   nss = args.nss.split()
   txpowers = args.txpower.split()
       
   if (args.create_station != None):
       if (args.radio == None):
           print("WARNING --create needs a radio")
           exit(1)
       else:
           print("creating station: {} on radio {}".format(args.create_station,args.radio))
           subprocess.run(["./lf_associate_ap.pl", "--radio", args.radio, "--ssid", args.ssid , "--passphrase", args.ssidpw,
                   "security", args.security, "--upstream", args.upstream_port, "--first_ip", "DHCP",
                   "--first_sta",args.create_station,"--duration","1","--cxtype","udp","--action","add"], timeout=20, capture_output=True)
           sleep(3)


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

   myrd = ""
   try:
      advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                 "--action", "summary","--series",args.series,"--port",args.port], capture_output=True, check=True)
      pss = advanced.stdout.decode('utf-8', 'ignore');
      print(pss)
   except subprocess.CalledProcessError as process_error:
      print("error code {}  output {}".format(process_error.returncode, process_error.output))
      exit(1)
         
   # Find our current regulatory domain so we can report it properly
   searchap = False
   for line in pss.splitlines():
       if (line.startswith("---------")):
           searchap = True
           continue

       if (searchap):
           if args.series == "9800":
               pat = "%s\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)"%(args.ap)
           else:
               pat = "%s\s+\S+\s+\S+\s+\S+\s+\S+.*  (\S+)\s+\S+\s*\S+\s+\["%(args.ap)
           m = re.search(pat, line)
           if (m != None):
               myrd = m.group(1)

   # Loop through all iterations and run txpower tests.
   for ch in channels:
       pathloss = args.pathloss
       ch_colon = ch.count(":")
       if (ch_colon == 1):
           cha = ch.split(":")
           pathloss = cha[1]
           ch = cha[0]
       for n in nss:
           for bw in bandwidths:
               if (n != "NA"):
                   ni = int(n);
                   if (parent == None):
                       print("ERROR:  Skipping setting the spatial streams because cannot find Parent radio for station: %s."%(lfstation))
                   else:
                       # Set nss on LANforge Station, not sure it can be done on AP
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

                   e_tot = ""

                   # Stop traffic
                   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                                   "--cmd", "set_cx_state all c-udp-power STOPPED"], capture_output=True);

                   # TODO:  Down station
                   port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                "--set_ifstate", "down"]);
                   
                   # Disable AP, apply settings, enable AP
                   print("3504/9800 cisco_wifi_ctl.py: disable")
                   subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)

                   if args.series == "9800": 
                       # 9800 series need to  "Configure radio for manual channel assignment"
                       print("9800 Configure radio for manual channel assignment")
                       print("9800 cisco_wifi_ctl.py: disable_network_5ghz")

                       print("9800  cisco_wifi_ctl.py: disable_wlan")

                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable_wlan","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)

                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable_network_5ghz","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True) 
                          
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("9800 cisco_wifi_ctl.py: disable_network_24ghz")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable_network_24ghz","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)    
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("9800 cisco_wifi_ctl.py: manual")

                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "manual","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)
                   else:
                       print("3504 cisco_wifi_ctl.py: onfig 802.11a disable network")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "cmd", "--value", "config 802.11a disable network","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                         print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                         exit(1)
                         
                       print("3504 cisco_wifi_ctl.py: config 802.11b disable network")
 
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "cmd", "--value", "config 802.11b disable network","--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output))
                          exit(1) 

                   print("9800 test_parameters_summary: set : tx: {} ch: {} bw: {}".format(tx,ch,bw))
                   if (tx != "NA"):
                       print("9800 test_parameters: set txPower: {}".format(tx))
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                       "--action", "txPower", "--value", tx, "--series" , args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                   if (bw != "NA"):
                       print("9800 test_parameters bandwidth: set : {}".format(bw))
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                       "--action", "bandwidth", "--value", bw, "--series" , args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output))
                          exit(1) 

                   # NSS is set on the station earlier...
                       
                   if (ch != "NA"):
                       print("9800 test_parameters set channel: {}".format(ch))
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                       "--action", "channel", "--value", ch, "--series" , args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                   if args.series == "9800":
                       #print("9800 cisco_wifi_ctl.py: delete_wlan")
                       #subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                       #            "--action", "delete_wlan","--series",args.series, "--wlan", args.wlan, "--wlanID", args.wlanID], capture_output=True, check=True)    

                       print("9800  cisco_wifi_ctl.py: create_wlan")
                       try:
                           subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "create_wlan","--series",args.series, "--wlan", args.wlan, "--wlanID", args.wlanID,"--port", args.port], capture_output=cap_ctl_out, check=True)    
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("9800  cisco_wifi_ctl.py: wireless_tag_policy")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "wireless_tag_policy","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True) 
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("9800  cisco_wifi_ctl.py: enable_wlan")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable_wlan","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)                 
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                   # enable transmission for the entier 802.11z network
                   if args.series == "9800":
                       print("9800  cisco_wifi_ctl.py: enable_network_5ghz")
                       try:                       
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable_network_5ghz","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)   
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("9800  cisco_wifi_ctl.py: enable_network_24ghz")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable_network_24ghz","--series",args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)                 
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)
                   else:    
                       print("3504  cisco_wifi_ctl.py: config 802.11a enable network")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "cmd", "--value", "config 802.11a enable network","--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       print("3504  cisco_wifi_ctl.py: config 802.11a enable network")
                       try:
                          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "cmd", "--value", "config 802.11b enable network","--port", args.port], capture_output=cap_ctl_out, check=True)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                   print("9800/3504  cisco_wifi_ctl.py: enable")
                   try: 
                      subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable", "--series" , args.series,"--port", args.port], capture_output=cap_ctl_out, check=True)
                   except subprocess.CalledProcessError as process_error:
                      print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                      exit(1)

                   # Wait a bit for AP to come back up
                   time.sleep(1)
                   if args.series == "9800":
                       print("9800  cisco_wifi_ctl.py: advanced")
                       try:
                          advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                              "--action", "advanced","--series" , args.series,"--port", args.port], capture_output=True, check=True)
                          pss = advanced.stdout.decode('utf-8', 'ignore')
                          print(pss)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                          exit(1)

                       searchap = False
                       cc_mac = ""
                       cc_ch = ""
                       cc_bw = ""
                       cc_power = ""
                       cc_dbm = ""
                       for line in pss.splitlines():
                           if (line.startswith("---------")):
                               searchap = True
                               continue

                           if (searchap):
                               pat = "%s\s+(\S+)\s+(%s)\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+dBm\)+\s+(\S+)+\s"%(args.ap,args.slot)
                               m = re.search(pat, line)
                               if (m != None):
                                   if(m.group(2) == args.slot):
                                       cc_mac = m.group(1)
                                       cc_slot = m.group(2)
                                       cc_ch = m.group(6);  # (132,136,140,144)
                                       cc_power = m.group(4)
                                       cc_power = cc_power.replace("/", " of ") # spread-sheets turn 1/8 into a date
                                       cc_dbm = m.group(5)
                                       cc_dbm = cc_dbm.replace("(","")

                                       cc_ch_count = cc_ch.count(",") + 1
                                       cc_bw = m.group(3)
                                       print("group 1: {} 2: {} 3: {} 4: {} 5: {} 6: {}".format(m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)))
                                       print("9800 test_parameters_summary:  read: tx: {} ch: {} bw: {}".format(tx,ch,bw))

                                       print("9800 test_parameters cc_mac: read : {}".format(cc_mac))
                                       print("9800 test_parameters cc_slot: read : {}".format(cc_slot))
                                       print("9800 test_parameters cc_count: read : {}".format(cc_ch_count))
                                       print("9800 test_parameters cc_bw: read : {}".format(cc_bw))
                                       print("9800 test_parameters cc_power: read : {}".format(cc_power))
                                       print("9800 test_parameters cc_dbm: read : {}".format(cc_dbm))
                                       print("9800 test_parameters cc_ch: read : {}".format(cc_ch))
                                       break

                       if (cc_dbm == ""):
                          # Could not talk to controller?
                          err = "ERROR:  Could not query dBm from controller, maybe controller died?"
                          print(err)
                          print("Exiting:  check controller and AP , Command on AP to erase the config: capwap ap erase all")
                          exit(1)
                          e_tot += err
                          e_tot += "  "
                       try:
                          wlan_summary = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                              "--action", "show_wlan_summary","--series" , args.series,"--port", args.port], capture_output=True, check=True)
                          pss = wlan_summary.stdout.decode('utf-8', 'ignore')
                          print(pss)
                       except subprocess.CalledProcessError as process_error:
                          print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                   else:
                       print("3504 cisco_wifi_ctl.py: advanced")
                       try:
                           advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                              "--action", "advanced","--port", args.port], capture_output=True, check=True)
                           pss = advanced.stdout.decode('utf-8', 'ignore')
                           print(pss)
                       except subprocess.CalledProcessError as process_error:
                           print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                           exit(1)

                       searchap = False
                       cc_mac = ""
                       cc_ch = ""
                       cc_bw = ""
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
                                   cc_ch = m.group(2);  # (132,136,140,144)
                                   cc_power = m.group(3)
                                   cc_power = cc_power.replace("/", " of ", 1) # spread-sheets turn 1/8 into a date
                                   cc_dbm = m.group(4)

                                   ch_count = cc_ch.count(",")
                                   cc_bw = 20 * (ch_count + 1)
                                   
                                   break
                                
                       if (cc_dbm == ""):
                          # Could not talk to controller?
                          err = "ERROR:  Could not query dBm from controller, maybe controller died?"
                          print(err)
                          e_tot += err
                          e_tot += "  "

                   # Up station
                   subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                   "--set_ifstate", "up"]);

                   i = 0
                   wait_ip_print = False;
                   wait_assoc_print = False;
                   # Wait untill LANforge station connects
                   while True:
                       port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                    "--show_port", "AP,IP,Mode,NSS,Bandwidth,Channel,Signal,Noise,Status,RX-Rate"],capture_output=True, check=True)
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
                               print("Waiting up to 180s for station to associate.")
                               wait_assoc_print = True

                       i += 1
                       # We wait a fairly long time since AP will take a long time to start on a CAC channel.
                       if (i > 180):
                           err = "ERROR:  Station did not connect within 180 seconds."
                           print(err)
                           e_tot += err
                           e_tot += "  "
                           if args.series == "9800":
                               print("9800  resending cisco_wifi_ctl.py: advanced")
                               try:
                                  advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                              "--action", "advanced","--series" , args.series,"--port", args.port], capture_output=True, check=True)
                                  pss = advanced.stdout.decode('utf-8', 'ignore')
                                  print(pss)
                               except subprocess.CalledProcessError as process_error:
                                  print("error code: {} output {}".format(process_error.returncode, process_error.output)) 
                                  exit(1)

                           if (args.wait_forever):
                               print("Will continue waiting, you may wish to debug the system...")
                               i = 0
                           else:
                               break

                       time.sleep(1)

                   # Start traffic
                   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                                   "--cmd", "set_cx_state all c-udp-power RUNNING"], capture_output=True, check=True)

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
                                                    "--cli_cmd", "probe_port 1 %s %s"%(lfresource, lfstation)],capture_output=True, check=True)
                       pss = port_stats.stdout.decode('utf-8', 'ignore')

                       foundit = False
                       for line in pss.splitlines():
                           #print("probe-line: %s"%(line))
                           m = re.search('signal avg:\s+(\S+)\s+\[(.*)\]\s+dBm', line)
                           if (m != None):
                               sig = m.group(1)
                               ants = m.group(2).split()
                               q = 0
                               for a in ants:
                                   ants[q] = ants[q].replace(",", "", 1)
                                   q += 1

                               print("sig: %s  ants: %s ants-len: %s n: %s"%(sig, m.group(2), len(ants), n))

                               if (len(ants) == int(n)):
                                   foundit = True
                               else:
                                   print("Looking for %s spatial streams, signal avg reported fewer: %s"%(n, m.group(1)))

                           m = re.search('beacon signal avg:\s+(\S+)\s+dBm', line)
                           if (m != None):
                               beacon_sig = m.group(1)
                               print("beacon_sig: %s "%(beacon_sig))
                               
                       if (foundit):
                           break

                       i += 1
                       if (i > 10):
                           err = "Tried and failed 10 times to find correct spatial streams, continuing."
                           print(err)
                           e_tot += err
                           e_tot += "  "
                           while (len(ants) < int(n)):
                               ants.append("")
                           break

                   endp_stats = subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--endp_vals", "rx_bps",
                                                "--cx_name", "c-udp-power"],capture_output=True, check=True)

                   pss = endp_stats.stdout.decode('utf-8', 'ignore');

                   for line in pss.splitlines():
                       #print("probe-line: %s"%(line))
                       m = re.search('Rx Bytes:\s+(\d+)', line)
                       if (m != None):
                           rx_bytes = int(m.group(1))
                           if (rx_bytes == 0):
                               err = "ERROR:  No bytes received by data connection, test results may not be valid."
                               e_tot += err
                               e_tot += "  "

                   # Stop traffic
                   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                                   "--cmd", "set_cx_state all c-udp-power STOPPED"],capture_output=True, check=True)

                   antstr = ""
                   for x in range(4):
                       if (x < int(n)):
                           #print("x: %s n: %s  len(ants): %s"%(x, n, len(ants)))
                           antstr += ants[x]
                       else:
                           antstr += " "
                       antstr += "\t"

                   port_stats = subprocess.run(["./lf_portmod.pl", "--manager", lfmgr, "--card",  lfresource, "--port_name", lfstation,
                                                "--show_port", "AP,IP,Mode,NSS,Bandwidth,Channel,Signal,Noise,Status,RX-Rate"], capture_output=True, check=True)
                   pss = port_stats.stdout.decode('utf-8', 'ignore');

                   _ap = None
                   _bw = None
                   _ch = None
                   _mode = None
                   _nss = None
                   _noise = None
                   _rxrate = None
                   _noise_bare = None

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
                       m = re.search('Noise:\s+(.*)dBm', line)
                       if (m != None):
                           _noise_bare = m.group(1)
                       m = re.search('RX-Rate:\s+(.*)', line)
                       if (m != None):
                           _rxrate = m.group(1)

                   rssi_adj = 0
                   if (args.adjust_nf and _noise_bare != None):
                       _noise_i = int(_noise_bare)
                       if (_noise_i == 0):
                           # Guess we could not detect noise properly?
                           e_tot += "WARNING:  Invalid noise-floor, calculations may be inaccurate.  "
                       else:
                           rssi_adj = (_noise_i - nf_at_calibration)

                   if (sig == None):
                       e_tot += "ERROR:  Could not detect signal level.  "
                       sig = -100

                   if (beacon_sig == None):   
                       e_tot += "ERROR:  Could not detect beacon signal level.  "
                       beacon_sig = -100

                   pi = int(pathloss)   
                   if(rssi_to_use == "beacon"):
                       print("rssi_to_use == beacon: beacon_sig: %s "%(beacon_sig))
                       calc_dbm = int(beacon_sig) + pi + rssi_adj
                   else:
                       print("rssi_to_use == combined: sig: %s"%sig)
                       calc_dbm = int(sig) + pi + rssi_adj
                   print("calc_dbm %s"%(calc_dbm))
                   calc_ant1 = 0
                   if (ants[0] != ""):
                       calc_ant1 = int(ants[0]) + pi + rssi_adj
                   calc_ant2 = 0
                   calc_ant3 = 0
                   calc_ant4 = 0
                   if (len(ants) > 1 and ants[1] != ""):
                       calc_ant2 = int(ants[1]) + pi + rssi_adj
                   if (len(ants) > 2 and ants[2] != ""):
                       calc_ant3 = int(ants[2]) + pi + rssi_adj
                   if (len(ants) > 3 and ants[3] != ""):
                       calc_ant4 = int(ants[3]) + pi + rssi_adj

                   diff_a1 = ""
                   diff_a2 = ""
                   diff_a3 = ""
                   diff_a4 = ""

                   if (cc_dbm == ""):
                      cc_dbmi = 0
                   else:
                      cc_dbmi = int(cc_dbm)
                   diff_dbm = calc_dbm - cc_dbmi
                   pf = 1
                   pfs = "PASS"
                   pfrange = pf_dbm;
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
                       # DUT transmits one chain at lower power when using higher MCS, so allow
                       # for that as passing result.
                       failed_low = 0
                       least = 0
                       if (diff_a1 < -pfrange):
                           failed_low += 1
                           least = diff_a1
                       if (diff_a2 < -pfrange):
                           failed_low += 1
                           least = min(least, diff_a2)
                       if (diff_a3 < -pfrange):
                           failed_low += 1
                           least = min(least, diff_a3)
                       if (diff_a4 < -pfrange):
                           failed_low += 1
                           least = min(least, diff_a4)

                       if ((least < (-pfrange - pf_a4_dropoff)) or (failed_low > 1)):
                           pf = 0

                       if (diff_a1 > pfrange):
                           pf = 0
                       if (diff_a2 > pfrange):
                           pf = 0
                       if (diff_a3 > pfrange):
                           pf = 0
                       if (diff_a4 > pfrange):
                           pf = 0

                   if (pf == 0):
                       pfs = "FAIL"
                       
                   ln = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(
                       myrd, pathloss, ch, n, bw, tx, beacon_sig, sig,
                       antstr, _ap, _bw, _ch, _mode, _nss, _noise, _rxrate,
                       cc_mac, cc_ch, cc_power, cc_dbm,
                       calc_dbm, diff_dbm, calc_ant1, calc_ant2, calc_ant3, calc_ant4,
                       diff_a1, diff_a2, diff_a3, diff_a4, pfs
                     )

                   #print("RESULT: %s"%(ln))
                   csv.write(ln)
                   csv.write("\t")

                   ln = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(
                       myrd, pathloss, _ch, _nss, _bw, tx, allowed_per_path,
                       antstr,
                       calc_ant1, calc_ant2, calc_ant3, calc_ant4,
                       diff_a1, diff_a2, diff_a3, diff_a4, pfs
                       )
                   csvs.write(ln)
                   csvs.write("\t")

                   col = 0
                   worksheet.write(row, col, myrd, center_blue); col += 1
                   worksheet.write(row, col, _ch, center_blue); col += 1
                   worksheet.write(row, col, _nss, center_blue); col += 1
                   worksheet.write(row, col, cc_bw, center_blue); col += 1
                   worksheet.write(row, col, _bw, center_blue); col += 1
                   worksheet.write(row, col, tx, center_tan); col += 1
                   worksheet.write(row, col, allowed_per_path, center_tan); col += 1
                   worksheet.write(row, col, pathloss, center_tan); col += 1
                   worksheet.write(row, col, _noise, center_tan); col += 1
                   if (args.adjust_nf):
                       worksheet.write(row, col, rssi_adj, center_tan); col += 1
                   worksheet.write(row, col, _rxrate, center_tan); col += 1
                   worksheet.write(row, col, beacon_sig, center_tan); col += 1
                   worksheet.write(row, col, sig, center_tan); col += 1
                   for x in range(4):
                       if (x < int(n)):
                           worksheet.write(row, col, ants[x], center_peach); col += 1
                       else:
                           worksheet.write(row, col, " ", center_peach); col += 1
                   worksheet.write(row, col, calc_ant1, center_pink); col += 1
                   worksheet.write(row, col, calc_ant2, center_pink); col += 1
                   worksheet.write(row, col, calc_ant3, center_pink); col += 1
                   worksheet.write(row, col, calc_ant4, center_pink); col += 1

                   if (diff_a1 != "" and abs(diff_a1) > pfrange):
                       worksheet.write(row, col, diff_a1, center_yel_red); col += 1
                   else:
                       worksheet.write(row, col, diff_a1, center_yel); col += 1
                   if (diff_a2 != "" and abs(diff_a2) > pfrange):
                       worksheet.write(row, col, diff_a2, center_yel_red); col += 1
                   else:
                       worksheet.write(row, col, diff_a2, center_yel); col += 1
                   if (diff_a3 != "" and abs(diff_a3) > pfrange):
                       worksheet.write(row, col, diff_a3, center_yel_red); col += 1
                   else:
                       worksheet.write(row, col, diff_a3, center_yel); col += 1
                   if (diff_a4 != "" and abs(diff_a4) > pfrange):
                       worksheet.write(row, col, diff_a4, center_yel_red); col += 1
                   else:
                       worksheet.write(row, col, diff_a4, center_yel); col += 1
                       
                   if (pfs == "FAIL"):
                       worksheet.write(row, col, pfs, red); col += 1
                   else:
                       worksheet.write(row, col, pfs, green); col += 1

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

   # check if keeping the existing state
   if(args.keep_state):
       print("9800/3504 flag --keep_state set thus keeping state")
       try:
          advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
             "--action", "advanced","--series" , args.series,"--port", args.port], capture_output=True, check=True)
          pss = advanced.stdout.decode('utf-8', 'ignore')
          print(pss)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 
       try:
          advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
             "--action", "summary","--series" , args.series,"--port", args.port], capture_output=True, check=True)
          pss = advanced.stdout.decode('utf-8', 'ignore')
          print(pss)
       except subprocess.CalledProcessError as process_error:
           print("error code: {} output {}".format(process_error.returncode, process_error.output))
           exit(1) 

       exit(1)
  
   # Set things back to defaults
   # Disable AP, apply settings, enable AP
   print("9800/3504  cisco_wifi_ctl.py: disable")
   try:
      subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "disable", "--series" , args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
   except subprocess.CalledProcessError as process_error:
      print("error code: {} output {}".format(process_error.returncode, process_error.output))
      exit(1) 

   if args.series == "9800":
       print("9800  cisco_wifi_ctl.py: disable_network_5ghz")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable_network_5ghz","--series",args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)      
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

       print("9800  cisco_wifi_ctl.py: disable_network_24ghz")
       try:        
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "disable_network_24ghz","--series",args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)                 
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   else:
       print("3504  cisco_wifi_ctl.py: config 802.11a disable network")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "cmd", "--value", "config 802.11a disable network","--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

       print("3504  cisco_wifi_ctl.py: config 802.11b disable network")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "cmd", "--value", "config 802.11b disable network","--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   if (tx != "NA"):
       print("9800/3504  cisco_wifi_ctl.py: txPower")
       try: 
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                       "--action", "txPower", "--value", "1", "--series" , args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   if (bw != "NA"):
       print("9800/3504  cisco_wifi_ctl.py: bandwidth")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                       "--action", "bandwidth", "--value", "20", "--series" , args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1)
   # NSS is set on the station earlier...
                       
   if (ch != "NA"):
       print("9800/3504  cisco_wifi_ctl.py: channel")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                       "--action", "channel", "--value", "36", "--series" , args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   if args.series == "9800":
       print("9800  cisco_wifi_ctl.py: enable_network_5ghz")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable_network_5ghz","--series",args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)         
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

       print("9800  cisco_wifi_ctl.py: enable_network_24ghz")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "enable_network_24ghz","--series",args.series,"--port", args.port],capture_output=cap_ctl_out, check=True) 
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

       print("9800  cisco_wifi_ctl.py: auto")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                                   "--action", "auto","--series",args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   else:     
       print("3504  cisco_wifi_ctl.py: config 802.11a enable network")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "cmd", "--value", "config 802.11a enable network","--port", args.port])
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

       print("3504  cisco_wifi_ctl.py: config 802.11b enable network")
       try:
          subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "cmd", "--value", "config 802.11b enable network","--port", args.port])
       except subprocess.CalledProcessError as process_error:
          print("error code: {} output {}".format(process_error.returncode, process_error.output))
          exit(1) 

   print("9800/3504  cisco_wifi_ctl.py: enable")
   try:
      subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                   "--action", "enable", "--series" , args.series,"--port", args.port],capture_output=cap_ctl_out, check=True)
   except subprocess.CalledProcessError as process_error:
      print("error code: {} output {}".format(process_error.returncode, process_error.output))
      exit(1) 

   # Remove LANforge traffic connection
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "set_cx_state all c-udp-power DELETED"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "rm_endp c-udp-power-A"], capture_output=True);
   subprocess.run(["./lf_firemod.pl", "--manager", lfmgr, "--resource",  lfresource, "--action", "do_cmd",
                   "--cmd", "rm_endp c-udp-power-B"], capture_output=True);

   # Show controller status
   print("9800/3504  cisco_wifi_ctl.py: advanced")

   try:
      advanced = subprocess.run(["./cisco_wifi_ctl.py", "--scheme", scheme, "-d", args.dest, "-u", args.user, "-p", args.passwd, "-a", args.ap, "--band", band,
                              "--action", "advanced", "--series" , args.series,"--port", args.port], capture_output=True, check=True)
      pss = advanced.stdout.decode('utf-8', 'ignore');
      print(pss)
   except subprocess.CalledProcessError as process_error:
      print("error code: {} output {}".format(process_error.returncode, process_error.output))
      exit(1) 


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()
    print("Summary results stored in %s, full results in %s, xlsx file in %s"%(outfile, full_outfile, outfile_xlsx))

####
####
####
