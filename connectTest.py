#!/usr/bin/env python3
import os
import time
import sys

if 'py-json' not in sys.path:
	sys.path.append('py-json')

import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils
import create_genlink as genl



if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

mgrURL = "http://localhost:8080/"

def execWrap(cmd):
	if os.system(cmd) != 0:
		print("\nError with " + cmd + ",bye\n")
		exit(1)


def jsonReq(mgrURL, reqURL, data, debug=False):
	lf_r = LFRequest.LFRequest(mgrURL + reqURL)
	lf_r.addPostData(data)

	if debug:
		json_response = lf_r.jsonPost(True)
		LFUtils.debug_printer.pprint(json_response)
		sys.exit(1)
	else:
		lf_r.jsonPost()

def getJsonInfo(mgrURL, reqURL, name):
	lf_r = LFRequest.LFRequest(mgrURL + reqURL)
	json_response = lf_r.getAsJson()
	return json_response
	#print(name)
	#j_printer = pprint.PrettyPrinter(indent=2)
	#j_printer.pprint(json_response)
	#for record in json_response[key]:
	#	j_printer.pprint(record)

def removeEndps(mgrURL, endpNames):
	for name in endpNames:
		#print(f"Removing endp {name}")
		data = {
		"endp_name":name
		}
		jsonReq(mgrURL, "cli-json/rm_endp", data)

def removeCX(mgrURL, cxNames):
	for name in cxNames:
		#print(f"Removing CX {name}")
		data = {
		"test_mgr":"all",
		"cx_name":name
		}
		jsonReq(mgrURL,"cli-json/rm_cx", data)

print("See home/lanforge/Documents/connectTestLogs/connectTestLatest for specific values on latest test")

print("Creating endpoints and cross connects")

#create cx for tcp and udp
cmd = ("./lf_firemod.pl --action create_cx --cx_name testTCP --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type tcp > /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
cmd = ("./lf_firemod.pl --action create_cx --cx_name testUDP --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type udp >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
time.sleep(.5)

#create l4 endpoint
url = "cli-json/add_l4_endp"
data = {
"alias":"l4Test",
"shelf":1,
"resource":1,
"port":"sta00000",
"type":"l4_generic",
"timeout":1000,
"url_rate":600,
"url":"dl http://10.40.0.1/ /dev/null"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

#create cx for l4_endp
url = "cli-json/add_cx"
data = {
"alias":"CX_l4Test",
"test_mgr":"default_tm",
"tx_endp":"l4Test",
"rx_endp":"NA"
}

jsonReq(mgrURL, url, data)
time.sleep(.5)

#create fileio endpoint
url = "cli-json/add_file_endp"
data = {
"alias":"fioTest",
"shelf":1,
"resource":1,
"port":"sta00000",
"type":"fe_nfs",
"directory":"/mnt/fe-test"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)

#create fileio cx
url = "cli-json/add_cx"
data = {
"alias":"CX_fioTest",
"test_mgr":"default_tm",
"tx_endp":"fioTest",
"rx_endp":"NA"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)

#create generic endpoints
genl.createGenEndp("genTest1",1,1,"sta00000","gen_generic")
genl.createGenEndp("genTest2",1,1,"sta00000","gen_generic")
genl.setFlags("genTest1","ClearPortOnStart",1)
genl.setFlags("genTest2","ClearPortOnStart",1)
genl.setFlags("genTest2","Unmanaged",1)
genl.setCmd("genTest1","lfping  -i 0.1 -I sta00000 10.40.0.1")
time.sleep(.5)

#create generic cx
url = "cli-json/add_cx"
data = {
"alias":"CX_genTest1",
"test_mgr":"default_tm",
"tx_endp":"genTest1",
"rx_endp":"genTest2"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)

#create redirects for wanlink
url = "cli-json/add_rdd"
data = {
"shelf":1,
"resource":1,
"port":"rdd0",
"peer_ifname":"rdd1"
}

jsonReq(mgrURL,url,data)

url = "cli-json/add_rdd"
data = {
"shelf":1,
"resource":1,
"port":"rdd1",
"peer_ifname":"rdd0"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)

#reset redirect ports
url = "cli-json/reset_port"
data = {
"shelf":1,
"resource":1,
"port":"rdd0"
}

jsonReq(mgrURL,url,data)

url = "cli-json/reset_port"
data = {
"shelf":1,
"resource":1,
"port":"rdd1"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)


#create wanlink endpoints
url = "cli-json/add_wl_endp"
data = {
"alias":"wlTest1",
"shelf":1,
"resource":1,
"port":"rdd0",
"latency":20,
"max_rate":1544000
}

jsonReq(mgrURL,url,data)

url = "cli-json/add_wl_endp"
data = {
"alias":"wlTest2",
"shelf":1,
"resource":1,
"port":"rdd1",
"latency":30,
"max_rate":1544000
}

jsonReq(mgrURL,url,data)
time.sleep(.5)

#create wanlink cx
url = "cli-json/add_cx"
data = {
"alias":"CX_wlTest1",
"test_mgr":"default_tm",
"tx_endp":"wlTest1",
"rx_endp":"wlTest2"
}

jsonReq(mgrURL,url,data)
time.sleep(.5)



#get data before running traffic
testTCPA = getJsonInfo(mgrURL, "endp/testTCP-A?fields=tx+bytes,rx+bytes", "testTCP-A")
testTCPATX = testTCPA['endpoint']['tx bytes']
testTCPARX = testTCPA['endpoint']['rx bytes']

testTCPB = getJsonInfo(mgrURL, "endp/testTCP-B?fields=tx+bytes,rx+bytes", "testTCP-B")
testTCPBTX = testTCPB['endpoint']['tx bytes']
testTCPBRX = testTCPB['endpoint']['rx bytes']

testUDPA = getJsonInfo(mgrURL, "endp/testUDP-A?fields=tx+bytes,rx+bytes", "testUDP-A")
testUDPATX = testUDPA['endpoint']['tx bytes']
testUDPARX = testUDPA['endpoint']['rx bytes']

testUDPB = getJsonInfo(mgrURL, "endp/testUDP-B?fields=tx+bytes,rx+bytes", "testUDP-B")
testUDPBTX = testUDPB['endpoint']['tx bytes']
testUDPBRX = testUDPB['endpoint']['rx bytes']

l4Test = getJsonInfo(mgrURL, "layer4/l4Test?fields=bytes-rd", "l4Test")
l4TestBR = l4Test['endpoint']['bytes-rd']

genTest1 = getJsonInfo(mgrURL, "generic/genTest1?fields=last+results", "genTest1")
genTest1LR = genTest1['endpoint']['last results']

wlTest1 = getJsonInfo(mgrURL,"wl_ep/wlTest1","wlTest1")
wlTest1TXB = wlTest1['endpoint']['tx bytes']
wlTest1RXP = wlTest1['endpoint']['rx pkts']
wlTest2 = getJsonInfo(mgrURL,"wl_ep/wlTest2","wlTest2")
wlTest2TXB = wlTest2['endpoint']['tx bytes']
wlTest2RXP = wlTest2['endpoint']['rx pkts']


#start cx traffic
print("\nStarting CX Traffic")
cxNames = ["testTCP","testUDP", "CX_l4Test", "CX_fioTest", "CX_genTest1", "CX_wlTest1"]
for name in range(len(cxNames)):
	cmd = (f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} RUNNING\" >> /tmp/connectTest.log")
	execWrap(cmd)

#print("Sleeping for 5 seconds")
time.sleep(5)

#show tx and rx bytes for ports

os.system("echo  eth1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_portmod.pl --quiet 1 --manager localhost --port_name eth1 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  sta00000 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_portmod.pl --quiet 1 --manager localhost --port_name sta00000 --show_port \"Txb,Rxb\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)


#show tx and rx for endpoints PERL
os.system("echo  TestTCP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name testTCP-A --endp_vals \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestTCP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name testTCP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestUDP-A >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name testUDP-A --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  TestUDP-B >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name testUDP-B --endp_vals  \"Tx Bytes,Rx Bytes\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  l4Test >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name l4Test --endp_vals Bytes-Read-Total >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  fioTest >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name fioTest --endp_vals \"Bytes Written,Bytes Read\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name genTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  wlTest1 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name wlTest1 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)
os.system("echo  wlTest2 >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
cmd = ("./lf_firemod.pl --action show_endp --endp_name wlTest2 --endp_vals \"Rx Pkts,Tx Bytes,Cur-Backlog,Dump File,Tx3s\" >> /home/lanforge/Documents/connectTestLogs/connectTestLatest.log")
execWrap(cmd)



#stop cx traffic
print("Stopping CX Traffic")
for name in range(len(cxNames)):
	cmd = (f"./lf_firemod.pl --mgr localhost --quiet yes --action do_cmd --cmd \"set_cx_state default_tm {cxNames[name]} STOPPED\"  >> /tmp/connectTest.log")
	execWrap(cmd)
#print("Sleeping for 15 seconds")
time.sleep(15)

#get data for endpoints JSON
print("Collecting Data")
ptestTCPA = getJsonInfo(mgrURL, "endp/testTCP-A?fields=tx+bytes,rx+bytes", "testTCP-A")
ptestTCPATX = ptestTCPA['endpoint']['tx bytes']
ptestTCPARX = ptestTCPA['endpoint']['rx bytes']

ptestTCPB = getJsonInfo(mgrURL, "endp/testTCP-B?fields=tx+bytes,rx+bytes", "testTCP-B")
ptestTCPBTX = ptestTCPB['endpoint']['tx bytes']
ptestTCPBRX = ptestTCPB['endpoint']['rx bytes']

ptestUDPA = getJsonInfo(mgrURL, "endp/testUDP-A?fields=tx+bytes,rx+bytes", "testUDP-A")
ptestUDPATX = ptestUDPA['endpoint']['tx bytes']
ptestUDPARX = ptestUDPA['endpoint']['rx bytes']

ptestUDPB = getJsonInfo(mgrURL, "endp/testUDP-B?fields=tx+bytes,rx+bytes", "testUDP-B")
ptestUDPBTX = ptestUDPB['endpoint']['tx bytes']
ptestUDPBRX = ptestUDPB['endpoint']['rx bytes']

pl4Test = getJsonInfo(mgrURL, "layer4/l4Test?fields=bytes-rd", "l4Test")
pl4TestBR = pl4Test['endpoint']['bytes-rd']

pgenTest1 = getJsonInfo(mgrURL, "generic/genTest1?fields=last+results", "genTest1")
pgenTest1LR = pgenTest1['endpoint']['last results']

pwlTest1 = getJsonInfo(mgrURL,"wl_ep/wlTest1","wlTest1")
pwlTest1TXB = pwlTest1['endpoint']['tx bytes']
pwlTest1RXP = pwlTest1['endpoint']['rx pkts']
pwlTest2 = getJsonInfo(mgrURL,"wl_ep/wlTest2","wlTest2")
pwlTest2TXB = pwlTest2['endpoint']['tx bytes']
pwlTest2RXP = pwlTest2['endpoint']['rx pkts']

#print("Sleeping for 5 seconds")
time.sleep(5)



#compare pre-test values to post-test values

def compareVals(name, preVal, postVal):
	print(f"Comparing {name}")
	if postVal > preVal:
		print("		Test Passed")
	else:
		print(f"	Test Failed: {name} did not increase after 5 seconds")

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

compareVals("wlTest1 TX Bytes", wlTest1TXB, pwlTest1TXB)
compareVals("wlTest1 RX Pkts", wlTest1RXP, pwlTest1RXP)

compareVals("wlTest2 TX Bytes", wlTest2TXB, pwlTest2TXB)
compareVals("wlTest2 RX Pkts", wlTest2RXP, pwlTest2RXP)

print("\n")



#remove all endpoints and cxs
print("Cleaning up...")
endpNames = ["testTCP-A", "testTCP-B",
	     "testUDP-A", "testUDP-B",
	     "l4Test", "fioTest",
	     "genTest1", "genTest2",
	     "wlTest1","wlTest2"]
removeCX(mgrURL, cxNames)
removeEndps(mgrURL, endpNames)
