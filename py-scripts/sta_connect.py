#!/usr/bin/env python3

#  This will create a station, create TCP and UDP traffic, run it a short amount of time,
#  and verify whether traffic was sent and received.  It also verifies the station connected
#  to the requested BSSID if bssid is specified as an argument.
#  The script will clean up the station and connections at the end of the test.

import os
import time
import sys
import argparse

if 'py-json' not in sys.path:
   sys.path.append('../py-json')

import subprocess
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.LFUtils import *

import create_genlink as genl

debugOn = True
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

dest = "localhost";
port = "8080";
dut_ssid = "MyAP"
dut_passwd = "NA"
dut_bssid = ""
user = ""
passwd = ""
sta_mode = "0" # See add_sta LANforge CLI users guide entry
radio = "wiphy0"
resource = "1"
upstream_resource = "1"
upstream_port = "eth2"
sta_name = "sta001"

parser = argparse.ArgumentParser(description="LANforge Unit Test:  Connect Station to AP\nExample:\n./sta_connect.py --dest 192.168.100.209 --dut_ssid OpenWrt-2 --dut_bssid 24:F5:A2:08:21:6C")
parser.add_argument("-d", "--dest",    type=str, help="address of the LANforge GUI machine (localhost is default)")
parser.add_argument("-o", "--port",    type=int, help="IP Port the LANforge GUI is listening on (8080 is default)")
parser.add_argument("-u", "--user",    type=str, help="TBD: credential login/username")
parser.add_argument("-p", "--passwd",  type=str, help="TBD: credential password")
parser.add_argument("--resource",      type=str, help="LANforge Station resource ID to use, default is 1")
parser.add_argument("--upstream_resource", type=str, help="LANforge Ethernet port resource ID to use, default is 1")
parser.add_argument("--upstream_port", type=str, help="LANforge Ethernet port name, default is eth2")
parser.add_argument("--radio",         type=str, help="LANforge radio to use, default is wiphy0")
parser.add_argument("--sta_mode",      type=str, help="LANforge station-mode setting (see add_sta LANforge CLI documentation, default is 0 (auto))")
parser.add_argument("--dut_ssid",      type=str, help="DUT SSID")
parser.add_argument("--dut_passwd",    type=str, help="DUT PSK password.  Do not set for OPEN auth")
parser.add_argument("--dut_bssid",     type=str, help="DUT BSSID to which we expect to connect.")

args = None

args = parser.parse_args()
if (args.dest != None):
   dest = args.dest
if (args.port != None):
   port = args.port
if (args.user != None):
   user = args.user
if (args.passwd != None):
   passwd = args.passwd
if (args.sta_mode != None):
   sta_mode = args.sta_mode
if (args.upstream_resource != None):
   upstream_resource = args.upstream_resource
if (args.upstream_port != None):
   upstream_port = args.upstream_port
if (args.radio != None):
   radio = args.radio
if (args.resource != None):
   resource = args.resource
if (args.dut_passwd != None):
   dut_passwd = args.dut_passwd
if (args.dut_bssid != None):
   dut_bssid = args.dut_bssid
if (args.dut_ssid != None):
   dut_ssid = args.dut_ssid

mgrURL = "http://%s:%s/"%(dest, port)
radio_url = "port/1/%s/%s"%(resource, radio)
sta_url = "port/1/%s/%s"%(resource, sta_name)
upstream_url = "port/1/%s/%s"%(upstream_resource, upstream_port)

def jsonReq(mgrURL, reqURL, data, exitWhenCalled=False):
   lf_r = LFRequest.LFRequest(mgrURL + reqURL)

   data['suppress_preexec_cli'] = True
   data['suppress_preexec_method'] = True

   lf_r.addPostData(data)

   json_response = lf_r.jsonPost(True)
   # Debugging
   #if (json_response != None):
   #   print("jsonReq: response: ")
   #   LFUtils.debug_printer.pprint(vars(json_response))
   if exitWhenCalled:
      print("jsonReq: bye")
      sys.exit(1)

def getJsonInfo(mgrURL, reqURL, debug=False):
   lf_r = LFRequest.LFRequest(mgrURL + reqURL)
   json_response = lf_r.getAsJson(debug)
   return json_response
   #print(name)
   #j_printer = pprint.PrettyPrinter(indent=2)
   #j_printer.pprint(json_response)
   #for record in json_response[key]:
   #  j_printer.pprint(record)


print("Checking for LANforge GUI connection: %s"%(mgrURL))
response = getJsonInfo(mgrURL, radio_url);
duration = 0
while ((response == None) and (duration < 300)):
   print("LANforge GUI connection not found sleeping 5 seconds, tried: %s"%(mgrURL))
   duration += 2
   time.sleep(2)
   response = getJsonInfo(mgrURL, radio_url)

if duration >= 300:
   print("Could not connect to LANforge GUI")
   sys.exit(1)


#Create stations and turn dhcp on
print("Creating station and turning on dhcp")

url = sta_url
debugOn = True
response = getJsonInfo(mgrURL, url)
if (response is not None):
   if (response["interface"] is not None):
      print("removing old station")
      LFUtils.removePort(resource, sta_name, mgrURL)
      time.sleep(5)

# See add_sta in LANforge CLI user guide
url = "cli-json/add_sta"
data = {
   "shelf":1,
   "resource":resource,
   "radio":radio,
   "sta_name":sta_name,
   "ssid":dut_ssid,
   "key":dut_passwd,
   "mode":sta_mode,
   "mac":"xx:xx:xx:xx:*:xx",
   "flags":0x10000 # verbose, open
}
print("adding new station")
jsonReq(mgrURL, url, data)

reqURL = "cli-json/set_port"
data = {
   "shelf":1,
   "resource":resource,
   "port":sta_name,
   "current_flags": 0x80000000, # use DHCP, not down
   "interest":0x4002 # set dhcp, current flags
}
print("configuring port")
jsonReq(mgrURL, reqURL, data)

time.sleep(5)

eth1IP = getJsonInfo(mgrURL, upstream_url)
if eth1IP['interface']['ip'] == "0.0.0.0":
   print("Warning: %s lacks ip address"%(upstream_url))

reqURL = "cli-json/nc_show_ports"
data = { "shelf":1,
    "resource":resource,
    "port":sta_name,
    "probe_flags":1 }
jsonReq(mgrURL, reqURL, data)

station_info = getJsonInfo(mgrURL, "%s?fields=port,ip,ap"%(sta_url))
duration = 0
maxTime = 300
ip = "0.0.0.0"
ap = ""
while ((ip == "0.0.0.0") and (duration < maxTime)):
      
   duration += 2
   time.sleep(2)

   station_info = getJsonInfo(mgrURL, "%s?fields=port,ip,ap"%(sta_url))

   #LFUtils.debug_printer.pprint(station_info)
   if ((station_info is not None) and ("interface" in station_info)):
      if ("ip" in station_info["interface"]):
         ip = station_info["interface"]["ip"]
      if ("ap" in station_info["interface"]):
         ap = station_info["interface"]["ap"]

   if ((ap == "Not-Associated") or (ap == "")):
      print("Station waiting to associate...")
   else:
      if (ip == "0.0.0.0"):
         print("Station waiting for IP ...")

if ((ap != "") and (ap != "Not-Associated")):
   print("Connected to AP: %s"%(ap))
   if (dut_bssid != ""):
      if (dut_bssid.lower() == ap.lower()):
         print("PASSED: Connected to BSSID: %s"%(ap))
      else:
         print("FAILED: Connected to wrong BSSID, requested: %s  Actual: %s"%(dut_bssid, ap))
else:
   print("FAILED:  Did not connect to AP");
   sys.exit(3)
   
if (ip is "0.0.0.0"):
   print("FAILED: %s did not get an ip. Ending test"%(sta_name))
   print("Cleaning up...")
   removePort(resource, sta_name, mgrURL)
   sys.exit(1)
else:
   print("PASSED: Connected to AP: %s  With IP: %s"%(ap, ip))

#create endpoints and cxs
# Create UDP endpoints
reqURL = "cli-json/add_endp"
data = {
   "alias":"testUDP-A",
   "shelf":1,
   "resource":resource,
   "port":sta_name,
   "type":"lf_udp",
   "ip_port":"-1",
   "min_rate":1000000
    }
jsonReq(mgrURL, reqURL, data)

reqURL = "cli-json/add_endp"
data = {
   "alias":"testUDP-B",
   "shelf":1,
   "resource":upstream_resource,
   "port":upstream_port,
   "type":"lf_udp",
   "ip_port":"-1",
   "min_rate":1000000
   }
jsonReq(mgrURL, reqURL, data)

# Create CX
reqURL = "cli-json/add_cx"
data = {
   "alias":"testUDP",
   "test_mgr":"default_tm",
   "tx_endp":"testUDP-A",
   "rx_endp":"testUDP-B",
   }
jsonReq(mgrURL, reqURL, data)

# Create TCP endpoints
reqURL = "cli-json/add_endp"
data = {
   "alias":"testTCP-A",
   "shelf":1,
   "resource":resource,
   "port":sta_name,
   "type":"lf_tcp",
   "ip_port":"0",
   "min_rate":1000000
   }
jsonReq(mgrURL, reqURL, data)

reqURL = "cli-json/add_endp"
data = {
   "alias":"testTCP-B",
   "shelf":1,
   "resource":upstream_resource,
   "port":upstream_port,
   "type":"lf_tcp",
   "ip_port":"-1",
   "min_rate":1000000
   }
jsonReq(mgrURL, reqURL, data)

# Create CX
reqURL = "cli-json/add_cx"
data = {
   "alias":"testTCP",
   "test_mgr":"default_tm",
   "tx_endp":"testTCP-A",
   "rx_endp":"testTCP-B",
   }
jsonReq(mgrURL, reqURL, data)

cxNames = ["testTCP","testUDP"]
endpNames = ["testTCP-A", "testTCP-B",
             "testUDP-A", "testUDP-B"]

#start cx traffic
print("\nStarting CX Traffic")
for name in range(len(cxNames)):
    reqURL = "cli-json/set_cx_state"
    data = {
        "test_mgr":"ALL",
        "cx_name":cxNames[name],
        "cx_state":"RUNNING"
        }
    jsonReq(mgrURL, reqURL, data)

# Refresh stats
print("\nRefresh CX stats")
for name in range(len(cxNames)):
    reqURL = "cli-json/show_cxe"
    data = {
        "test_mgr":"ALL",
        "cross_connect":cxNames[name]
        }
    jsonReq(mgrURL, reqURL, data)

#print("Sleeping for 15 seconds")
time.sleep(15)

#stop cx traffic
print("\nStopping CX Traffic")
for name in range(len(cxNames)):
    reqURL = "cli-json/set_cx_state"
    data = {
        "test_mgr":"ALL",
        "cx_name":cxNames[name],
        "cx_state":"STOPPED"
        }
    jsonReq(mgrURL, reqURL, data)

# Refresh stats
print("\nRefresh CX stats")
for name in range(len(cxNames)):
    reqURL = "cli-json/show_cxe"
    data = {
        "test_mgr":"ALL",
        "cross_connect":cxNames[name]
        }
    jsonReq(mgrURL, reqURL, data)

#print("Sleeping for 5 seconds")
time.sleep(5)

#get data for endpoints JSON
print("Collecting Data")
try:
   ptestTCPA = getJsonInfo(mgrURL, "endp/testTCP-A?fields=tx+bytes,rx+bytes")
   ptestTCPATX = ptestTCPA['endpoint']['tx bytes']
   ptestTCPARX = ptestTCPA['endpoint']['rx bytes']

   ptestTCPB = getJsonInfo(mgrURL, "endp/testTCP-B?fields=tx+bytes,rx+bytes")
   ptestTCPBTX = ptestTCPB['endpoint']['tx bytes']
   ptestTCPBRX = ptestTCPB['endpoint']['rx bytes']

   ptestUDPA = getJsonInfo(mgrURL, "endp/testUDP-A?fields=tx+bytes,rx+bytes")
   ptestUDPATX = ptestUDPA['endpoint']['tx bytes']
   ptestUDPARX = ptestUDPA['endpoint']['rx bytes']

   ptestUDPB = getJsonInfo(mgrURL, "endp/testUDP-B?fields=tx+bytes,rx+bytes")
   ptestUDPBTX = ptestUDPB['endpoint']['tx bytes']
   ptestUDPBRX = ptestUDPB['endpoint']['rx bytes']
except Exception as e:
   print("Something went wrong")
   print(e)
   print("Cleaning up...")
   reqURL = "cli-json/rm_vlan"
   data = {
       "shelf":1,
       "resource":resource,
       "port":sta_name
   }

   jsonReq(mgrURL, reqURL, data)

   removeCX(mgrURL, cxNames)
   removeEndps(mgrURL, endpNames)
   sys.exit(1)

#compare pre-test values to post-test values

def compareVals(name, postVal):
   #print(f"Comparing {name}")
   if postVal > 0:
      print("PASSED: %s %s"%(name, postVal))
   else:
      print("FAILED: %s did not report traffic: %s"%(name, postVal))

print("\n")
compareVals("testTCP-A TX", ptestTCPATX)
compareVals("testTCP-A RX", ptestTCPARX)

compareVals("testTCP-B TX", ptestTCPBTX)
compareVals("testTCP-B RX", ptestTCPBRX)

compareVals("testUDP-A TX", ptestUDPATX)
compareVals("testUDP-A RX", ptestUDPARX)

compareVals("testUDP-B TX", ptestUDPBTX)
compareVals("testUDP-B RX", ptestUDPBRX)
print("\n")



#remove all endpoints and cxs
LFUtils.removePort(resource, sta_name, mgrURL)

removeCX(mgrURL, cxNames)
removeEndps(mgrURL, endpNames)
