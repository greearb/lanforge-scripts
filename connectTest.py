#!/usr/bin/env python3
import os
import time
import sys

if 'py-json' not in sys.path:
    sys.path.append('py-json')

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

mgrURL = "http://localhost:8080/"


def jsonReq(mgrURL, reqURL, data, exitWhenCalled=False):
    lf_r = LFRequest.LFRequest(mgrURL + reqURL)
    lf_r.addPostData(data)

    if exitWhenCalled:
        json_response = lf_r.jsonPost(True)
        print("jsonReq: debugdie Response: ")
        LFUtils.debug_printer.pprint(vars(json_response))
        print("jsonReq: bye")
        sys.exit(1)
    else:
        lf_r.jsonPost(False)  # False means don't print info on errors


def getJsonInfo(mgrURL, reqURL, debug=False):
    lf_r = LFRequest.LFRequest(mgrURL + reqURL)
    json_response = lf_r.getAsJson(debug)
    return json_response
    # print(name)
    # j_printer = pprint.PrettyPrinter(indent=2)
    # j_printer.pprint(json_response)
    # for record in json_response[key]:
    #  j_printer.pprint(record)


print("Checking for LANforge Client")
response = getJsonInfo(mgrURL, 'port/1/1/wiphy0')
duration = 0
while ((response == None) and (duration < 300)):
    print("LANforge Client not found sleeping 5 seconds")
    duration += 2
    time.sleep(2)
    response = getJsonInfo(mgrURL, 'port/1/1/wiphy0')

if duration >= 300:
    print("Could not connect to LANforge Client")
    sys.exit(1)

print("See home/lanforge/Documents/connectTestLogs/connectTestLatest for specific values on latest test")
# Create stations and turn dhcp on
print("Creating station and turning on dhcp")

url = "port/1/1/sta00000"
debugOn = True
response = getJsonInfo(mgrURL, url)
if (response is not None):
    if (response["interface"] is not None):
        print("removing old station")
        LFUtils.removePort("1", "sta00000", mgrURL)
        time.sleep(1)

url = "cli-json/add_sta"
data = {
    "shelf": 1,
    "resource": 1,
    "radio": "wiphy0",
    "sta_name": "sta00000",
    "ssid": "jedway-wpa2-x2048-5-1",
    "key": "jedway-wpa2-x2048-5-1",
    "mode": 1,
    "mac": "xx:xx:xx:xx:*:xx",
    "flags": 1024  # 0x400 | 1024
}
print("adding new station")
jsonReq(mgrURL, url, data)

time.sleep(1)

reqURL = "cli-json/set_port"
data = {
    "shelf": 1,
    "resource": 1,
    "port": "sta00000",
    "current_flags": 2147483648,  # 0x80000000 | 2147483648
    "interest": 16386  # 0x4002 | 16386
}
print("configuring port")
jsonReq(mgrURL, reqURL, data)

time.sleep(5)

eth1IP = getJsonInfo(mgrURL, "port/1/1/eth1")
if eth1IP['interface']['ip'] == "0.0.0.0":
    print("Warning: Eth1 lacks ip address")

reqURL = "cli-json/nc_show_ports"
data = {"shelf": 1,
        "resource": 1,
        "port": "sta0000",
        "probe_flags": 1}
jsonReq(mgrURL, reqURL, data)

station_info = getJsonInfo(mgrURL, "port/1/1/sta00000?fields=port,ip")
duration = 0
maxTime = 300
ip = "0.0.0.0"
while ((ip == "0.0.0.0") and (duration < maxTime)):
    print("Station failed to get IP. Waiting 10 seconds...")
    station_info = getJsonInfo(mgrURL, "port/1/1/sta00000?fields=port,ip")

    # LFUtils.debug_printer.pprint(station_info)
    if ((station_info is not None) and ("interface" in station_info) and ("ip" in station_info["interface"])):
        ip = station_info["interface"]["ip"]
    duration += 2
    time.sleep(2)

if duration >= maxTime:
    print("sta00000 failed to get an ip. Ending test")
    print("Cleaning up...")
    removePort("1", "sta00000", mgrURL)
    sys.exit(1)

# create endpoints and cxs


print("Creating endpoints and cross connects")
# create cx for tcp and udp
cmd = (
    "./lf_firemod.pl --action create_cx --cx_name testTCP --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type tcp > ~/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
cmd = (
    "./lf_firemod.pl --action create_cx --cx_name testUDP --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type udp >> ~/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
time.sleep(.5)

# create l4 endpoint
url = "cli-json/add_l4_endp"
data = {
    "alias": "l4Test",
    "shelf": 1,
    "resource": 1,
    "port": "sta00000",
    "type": "l4_generic",
    "timeout": 1000,
    "url_rate": 600,
    "url": "dl http://10.40.0.1/ /dev/null"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create cx for l4_endp
url = "cli-json/add_cx"
data = {
    "alias": "CX_l4Test",
    "test_mgr": "default_tm",
    "tx_endp": "l4Test",
    "rx_endp": "NA"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create fileio endpoint
url = "cli-json/add_file_endp"
data = {
    "alias": "fioTest",
    "shelf": 1,
    "resource": 1,
    "port": "sta00000",
    "type": "fe_nfs",
    "directory": "/mnt/fe-test"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create fileio cx
url = "cli-json/add_cx"
data = {
    "alias": "CX_fioTest",
    "test_mgr": "default_tm",
    "tx_endp": "fioTest",
    "rx_endp": "NA"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create generic endpoints
genl.createGenEndp("genTest1", 1, 1, "sta00000", "gen_generic")
genl.createGenEndp("genTest2", 1, 1, "sta00000", "gen_generic")
genl.setFlags("genTest1", "ClearPortOnStart", 1)
genl.setFlags("genTest2", "ClearPortOnStart", 1)
genl.setFlags("genTest2", "Unmanaged", 1)
genl.setCmd("genTest1", "lfping  -i 0.1 -I sta00000 10.40.0.1")
time.sleep(.5)

# create generic cx
url = "cli-json/add_cx"
data = {
    "alias": "CX_genTest1",
    "test_mgr": "default_tm",
    "tx_endp": "genTest1",
    "rx_endp": "genTest2"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create redirects for wanlink
url = "cli-json/add_rdd"
data = {
    "shelf": 1,
    "resource": 1,
    "port": "rdd0",
    "peer_ifname": "rdd1"
}

jsonReq(mgrURL, url, data)

url = "cli-json/add_rdd"
data = {
    "shelf": 1,
    "resource": 1,
    "port": "rdd1",
    "peer_ifname": "rdd0"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# reset redirect ports
url = "cli-json/reset_port"
data = {
    "shelf": 1,
    "resource": 1,
    "port": "rdd0"
}

jsonReq(mgrURL, url, data)

url = "cli-json/reset_port"
data = {
    "shelf": 1,
    "resource": 1,
    "port": "rdd1"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create wanlink endpoints
url = "cli-json/add_wl_endp"
data = {
    "alias": "wlan0",
    "shelf": 1,
    "resource": 1,
    "port": "rdd0",
    "latency": 20,
    "max_rate": 1544000
}

jsonReq(mgrURL, url, data)

url = "cli-json/add_wl_endp"
data = {
    "alias": "wlan1",
    "shelf": 1,
    "resource": 1,
    "port": "rdd1",
    "latency": 30,
    "max_rate": 1544000
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

# create wanlink cx
url = "cli-json/add_cx"
data = {
    "alias": "CX_wlan0",
    "test_mgr": "default_tm",
    "tx_endp": "wlan0",
    "rx_endp": "wlan1"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

cxNames = ["testTCP", "testUDP", "CX_l4Test", "CX_fioTest", "CX_genTest1", "CX_wlan0"]

# get data before running traffic
try:
    testTCPA = getJsonInfo(mgrURL, "endp/testTCP-A?fields=tx+bytes,rx+bytes")
    testTCPATX = testTCPA['endpoint']['tx bytes']
    testTCPARX = testTCPA['endpoint']['rx bytes']

    testTCPB = getJsonInfo(mgrURL, "endp/testTCP-B?fields=tx+bytes,rx+bytes")
    testTCPBTX = testTCPB['endpoint']['tx bytes']
    testTCPBRX = testTCPB['endpoint']['rx bytes']

    testUDPA = getJsonInfo(mgrURL, "endp/testUDP-A?fields=tx+bytes,rx+bytes")
    testUDPATX = testUDPA['endpoint']['tx bytes']
    testUDPARX = testUDPA['endpoint']['rx bytes']

    testUDPB = getJsonInfo(mgrURL, "endp/testUDP-B?fields=tx+bytes,rx+bytes")
    testUDPBTX = testUDPB['endpoint']['tx bytes']
    testUDPBRX = testUDPB['endpoint']['rx bytes']

    l4Test = getJsonInfo(mgrURL, "layer4/l4Test?fields=bytes-rd")
    l4TestBR = l4Test['endpoint']['bytes-rd']

    genTest1 = getJsonInfo(mgrURL, "generic/genTest1?fields=last+results")
    genTest1LR = genTest1['endpoint']['last results']

    wlan0 = getJsonInfo(mgrURL, "wl_ep/wlan0")
    wlan0TXB = wlan0['endpoint']['tx bytes']
    wlan0RXP = wlan0['endpoint']['rx pkts']
    wlan1 = getJsonInfo(mgrURL, "wl_ep/wlan1")
    wlan1TXB = wlan1['endpoint']['tx bytes']
    wlan1RXP = wlan1['endpoint']['rx pkts']
except Exception as e:
    print("Something went wrong")
    print(e)
    print("Cleaning up...")
    LFUtils.removePort("1", "sta00000", mgrURL)

    endpNames = ["testTCP-A", "testTCP-B",
                 "testUDP-A", "testUDP-B",
                 "l4Test", "fioTest",
                 "genTest1", "genTest2",
                 "wlan0", "wlan1"]
    removeCX(mgrURL, cxNames)
    removeEndps(mgrURL, endpNames)
    sys.exit(1)

# start cx traffic
print("\nStarting CX Traffic")
for name in range(len(cxNames)):
    cmd = (
        f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} RUNNING\" >> /tmp/connectTest.log")
    execWrap(cmd)

# print("Sleeping for 5 seconds")
time.sleep(5)

# show tx and rx bytes for ports

os.system("echo  eth1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_portmod.pl --quiet 1 --manager localhost --port_name eth1 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  sta00000 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_portmod.pl --quiet 1 --manager localhost --port_name sta00000 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)

# show tx and rx for endpoints PERL
os.system("echo  TestTCP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name testTCP-A --endp_vals \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestTCP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name testTCP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestUDP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name testUDP-A --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestUDP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name testUDP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  l4Test >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name l4Test --endp_vals Bytes-Read-Total >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  fioTest >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name fioTest --endp_vals \"Bytes Written,Bytes Read\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  wlan0 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name wlan0 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  wlan1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = (
    "./lf_firemod.pl --action show_endp --endp_name wlan1 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)

# stop cx traffic
print("Stopping CX Traffic")
for name in range(len(cxNames)):
    cmd = (
        f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} STOPPED\"  >> /tmp/connectTest.log")
    execWrap(cmd)
# print("Sleeping for 15 seconds")
time.sleep(15)

# get data for endpoints JSON
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

    pl4Test = getJsonInfo(mgrURL, "layer4/l4Test?fields=bytes-rd")
    pl4TestBR = pl4Test['endpoint']['bytes-rd']

    pgenTest1 = getJsonInfo(mgrURL, "generic/genTest1?fields=last+results")
    pgenTest1LR = pgenTest1['endpoint']['last results']

    pwlan0 = getJsonInfo(mgrURL, "wl_ep/wlan0")
    pwlan0TXB = pwlan0['endpoint']['tx bytes']
    pwlan0RXP = pwlan0['endpoint']['rx pkts']
    pwlan1 = getJsonInfo(mgrURL, "wl_ep/wlan1")
    pwlan1TXB = pwlan1['endpoint']['tx bytes']
    pwlan1RXP = pwlan1['endpoint']['rx pkts']
except Exception as e:
    print("Something went wrong")
    print(e)
    print("Cleaning up...")
    reqURL = "cli-json/rm_vlan"
    data = {
        "shelf": 1,
        "resource": 1,
        "port": "sta00000"
    }

    jsonReq(mgrURL, reqURL, data)

    endpNames = ["testTCP-A", "testTCP-B",
                 "testUDP-A", "testUDP-B",
                 "l4Test", "fioTest",
                 "genTest1", "genTest2",
                 "wlan0", "wlan1"]
    removeCX(mgrURL, cxNames)
    removeEndps(mgrURL, endpNames)
    sys.exit(1)

# print("Sleeping for 5 seconds")
time.sleep(5)


# compare pre-test values to post-test values

def compareVals(name, preVal, postVal):
    print(f"Comparing {name}")
    if postVal > preVal:
        print("     Test Passed")
    else:
        print(f" Test Failed: {name} did not increase after 5 seconds")


print("\n")
compareVals("testTCP-A TX", testTCPATX, ptestTCPATX)
compareVals("testTCP-A RX", testTCPARX, ptestTCPARX)

compareVals("testTCP-B TX", testTCPBTX, ptestTCPBTX)
compareVals("testTCP-B RX", testTCPBRX, ptestTCPBRX)

compareVals("testUDP-A TX", testUDPATX, ptestUDPATX)
compareVals("testUDP-A RX", testUDPARX, ptestUDPARX)

compareVals("testUDP-B TX", testUDPBTX, ptestUDPBTX)
compareVals("testUDP-B RX", testUDPBRX, ptestUDPBRX)

compareVals("l4Test Bytes Read", l4TestBR, pl4TestBR)

compareVals("genTest1 Last Results", genTest1LR, pgenTest1LR)

compareVals("wlan0 TX Bytes", wlan0TXB, pwlan0TXB)
compareVals("wlan0 RX Pkts", wlan0RXP, pwlan0RXP)

compareVals("wlan1 TX Bytes", wlan1TXB, pwlan1TXB)
compareVals("wlan1 RX Pkts", wlan1RXP, pwlan1RXP)

print("\n")

# remove all endpoints and cxs
print("Cleaning up...")

LFUtils.removePort("1", "sta00000", mgrURL)

endpNames = ["testTCP-A", "testTCP-B",
             "testUDP-A", "testUDP-B",
             "l4Test", "fioTest",
             "genTest1", "genTest2",
             "wlan0", "wlan1"]
removeCX(mgrURL, cxNames)
removeEndps(mgrURL, endpNames)
