#!/usr/bin/env python3
import os
import sys
import time
sys.path.append('py-json')
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils

def jsonReq(mgrURL, reqURL, data, debug=False):
        lf_r = LFRequest.LFRequest(mgrURL + reqURL)
        lf_r.addPostData(data)

        if debug:
                json_response = lf_r.jsonPost(True)
                LFUtils.debug_printer.pprint(json_response)
                sys.exit(1)
        else:
             	lf_r.jsonPost()


def execWrap(cmd):
        if os.system(cmd) != 0:
                print("\nError with " + cmd + ",bye\n")
                exit(1)

def getJsonInfo(mgrURL, reqURL):
        lf_r = LFRequest.LFRequest(mgrURL + reqURL)
        json_response = lf_r.getAsJson()
        return json_response

stations = []
radios = {"wiphy0":5, "wiphy1":5, "wiphy2":5, "wiphy3":5} #radioName:numStations

paddingNum = 1000 #uses all but the first number to create names for stations

mgrURL = "http://localhost:8080/"

#create stations
print("Creating Stations")
reqURL = "cli-json/add_sta"
for radio, numStations in radios.items():
	for i in range(0,numStations):
		staName = "sta" + radio[-1:] + str(paddingNum + i)[1:]
		stations.append(staName)
		data = {
		"shelf":1,
		"resource":1,
		"radio":radio,
		"sta_name":staName,
		"ssid":"jedway-wpa2-roam",
		"key":"jedway-wpa2-roam",
		"mode":1,
		"mac":"xx:xx:xx:xx:*:xx",
		"flags":0x400
		}
		#print("Creating station {}".format(staName))
		jsonReq(mgrURL, reqURL, data)

		time.sleep(0.5)

		#LFUtils.portDhcpUpRequest(1, staName)


time.sleep(10)

#check eth1 for ip
eth1IP = getJsonInfo(mgrURL, "port/1/1/eth1")
if eth1IP['interface']['ip'] == "0.0.0.0":
	print("Switching eth1 to dhcp")
	LFUtils.portDownRequest(1,"eth1")
	time.sleep(1)
	reqURL = "cli-json/set_port"
	data = {
	"shelf":1,
	"resource":1,
	"port":"eth1",
	"current_flags":0x80000000,
	"interest":0x4002
	}

	jsonReq(mgrURL,reqURL,data)
	#LFUtils.portDhcpUpRequest(1,"eth1")
	time.sleep(5)
	LFUtils.portUpRequest(1,"eth1")


time.sleep(10)

#create cross connects
print("Creating cross connects")
for staName in stations:
	cmd = ("./lf_firemod.pl --action create_cx --cx_name " + staName + " --use_ports eth1," + staName + " --use_speeds  56000,56000 --endp_type udp > sst.log")
	execWrap(cmd)

#set stations to dchp up
print("Turning on DHCP for stations")
for staName in stations:
	#print("Setting {} flags".format(staName))
	reqURL = "cli-json/set_port"
	data = {
	"shelf":1,
	"resource":1,
	"port":staName,
	"current_flags":0x80000000,
	"interest":0x4002
	}

	jsonReq(mgrURL,reqURL,data)
	#LFUtils.portDhcpUpRequest(1,staName)


time.sleep(15)

#start traffic through cxs
print("Starting CX Traffic")
for name in stations:
        cmd = ("./lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm " + name + " RUNNING\" >> sst.log")
        execWrap(cmd)

time.sleep(30)

print("Stopping CX Traffic")
for name in stations:
        cmd = ("./lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm " + name + " STOPPED\" >> sst.log")
        execWrap(cmd)

time.sleep(10)

#remove all created stations and cross connects
print("Cleaning Up...")
for staName in stations:
	reqURL = "cli-json/rm_vlan"

	data = {
	"shelf":1,
	"resource":1,
	"port":staName
	}

	jsonReq(mgrURL, reqURL, data)

	reqURL = "cli-json/rm_cx"

	data = {
	"test_mgr":"default_tm",
	"cx_name":staName
	}
	jsonReq(mgrURL, reqURL, data)

	reqURL = "cli-json/rm_endp"

	data = {
	"endp_name":staName + "-A"
	}
	jsonReq(mgrURL, reqURL, data)

	reqURL = "cli-json/rm_endp"
	data = {
	"endp_name":staName + "-B"
	}

	jsonReq(mgrURL, reqURL, data)
