#!/usr/bin/env python3
import os
import sys
import time
sys.path.append('py-json')
import json
import pprint
import datetime
from LANforge import LFRequest
from LANforge import LFUtils
import argparse
import re
import math
import string
import emailHelper

debugOn = False

sender = "lanforge@candelatech.com"

def jsonReq(mgrURL, reqURL, data, debug=False):
	lf_r = LFRequest.LFRequest(mgrURL + reqURL)
	lf_r.addPostData(data)

	if debug:
                json_response = lf_r.jsonPost(debug)
                LFUtils.debug_printer.pprint(json_response)
                sys.exit(1)
	else:
             	lf_r.jsonPost(debug)


def execWrap(cmd):
        if os.system(cmd) != 0:
                print("\nError with " + cmd + ",bye\n")
                exit(1)

def getJsonInfo(mgrURL, reqURL):
	lf_r = LFRequest.LFRequest(mgrURL + reqURL)
	json_response = lf_r.getAsJson(debugOn)
	return json_response




parser = argparse.ArgumentParser(description="Create max stations for each radio")
parser.add_argument("--test_duration", type=str, help="Full duration for the test to run. should be specified by a number followed by a character. d for days, h for hours, m for minutes, s for seconds")
parser.add_argument("--report_interval", type=str, help="How often a report is made. should be specified by a number followed by a character. d for days, h for hours, m for minutes, s for seconds")
parser.add_argument("--output_dir", type=str, help="Directory to ouptut to")
parser.add_argument("--output_prefix", type=str, help="Name of the file. Timestamp and .html will be appended to the end")
parser.add_argument("--email", type=str, help="Email address of recipient")

args = None
try:
	args = parser.parse_args()
	if (args.test_duration is not None):
		pattern = re.compile("^(\d+)([dhms]$)")
		td = pattern.match(args.test_duration)
		if td != None:
			durTime = int(td.group(1))
			durMeasure = str(td.group(2))

			if durMeasure == "d":
				durationSec = durTime * 60 * 60 * 24
			elif durMeasure == "h":
				durationSec = durTime * 60 * 60
			elif durMeasure == "m":
				durationSec = durTime * 60
			else:
				durationSec = durTime
		else:
			parser.print_help()
			parser.exit()

	if (args.report_interval is not None):
		pattern = re.compile("^(\d+)([dhms])$")
		ri = pattern.match(args.report_interval)
		if ri != None:
			intTime = int(ri.group(1))
			intMeasure = str(ri.group(2))

			if intMeasure == "d":
                        	intervalSec = intTime * 60 * 60 * 24
			elif intMeasure == "h":
				intervalSec = intTime * 60 * 60
			elif intMeasure == "m":
				intervalSec = intTime * 60
			else:
				intervalSec = intTime
		else:
			parser.print_help()
			parser.exit()

	if (args.output_dir != None):
		outputDir = args.output_dir
	else:
		parser.print_help()
		parser.exit()

	if (args.output_prefix != None):
		outputPrefix = args.output_prefix
	else:
		parser.print_help()
		parser.exit()
	if (args.email != None):
		recipient = args.email
	else:
		parser.print_help()
		parser.exit()


except Exception as e:
      logging.exception(e)
      usage()
      exit(2)


stations = []
radios = {"wiphy0":200, "wiphy1":200, "wiphy2":64, "wiphy3":200} #radioName:numStations
radio_ssid_map = {"wiphy0":"jedway-wpa2-x2048-4-1",
		  "wiphy1":"jedway-wpa2-x2048-5-3",
		  "wiphy2":"jedway-wpa2-x2048-5-1",
		  "wiphy3":"jedway-wpa2-x2048-4-4"}

ssid_passphrase_map = {"jedway-wpa2-x2048-4-1":"jedway-wpa2-x2048-4-1",
		       "jedway-wpa2-x2048-5-3":"jedway-wpa2-x2048-5-3",
		       "jedway-wpa2-x2048-5-1":"jedway-wpa2-x2048-5-1",
		       "jedway-wpa2-x2048-4-4":"jedway-wpa2-x2048-4-4"}

paddingNum = 1000 #uses all but the first number to create names for stations

mgrURL = "http://localhost:8080/"

#clean up old stations
print("Cleaning up old Stations")

for radio, numStations in radios.items():
	for i in range(0,numStations):
		staName = "sta" + radio[-1:] + str(paddingNum + i)[1:]
		if getJsonInfo(mgrURL, "port/1/1/"+staName) != None:
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

#create new stations
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
		"ssid":radio_ssid_map[radio],
		"key":ssid_passphrase_map[radio_ssid_map[radio]],
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
	cmd = ("./lf_firemod.pl --action create_cx --cx_name " + staName + " --use_ports eth1," + staName + " --use_speeds  2600,2600 --endp_type udp > sst.log")
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


#create weblog for monitoring stations
curTime = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
webLog = outputDir + outputPrefix + "{}.html".format(curTime)

try:
	f = open(webLog,"w")

except IOError as err:
	print(err)
	print("Please ensure correct permissions have been assigned in target directory")
	sys.exit()


top = """<html>
<head>
<title>Test report</title>
<style>
body, td, p, div, span { font-size: 8pt; }
h1, h2, h3 { text-align: center; font-family: "Century Gothic",Arial,Helvetica,sans;}
</style>
</head>
<body>
<h1>Long test on %s</h1>
<p2>Key</p2>
<p1 style="background-color:rgb(0,255,0);">All stations associated and with ip</p1>
<p1 style="background-color:rgb(255,200,0);">All stations associated and at least one without ip</p1>
<p1 style="background-color:rgb(255,150,150);">No stations associated and without ip</p1>
<table>
""" % datetime.date.today()


f.write(top)
f.close()

f = open(webLog, "a")
f.write("<tr>\n")

for name in radios:
	f.write("<th>{}</th>\n".format(name))

f.write("</tr>\n")


curTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
subject = "Station Test Begin Report Notification"
body = "Report begun at {}\n See {}".format(curTime, webLog)
email = emailHelper.writeEmail(body)
emailHelper.sendEmail(email, sender, recipient, subject)


print("Logging Info to {}".format(webLog))

timesLoop = math.ceil(durationSec / intervalSec)
#print("Looping {} times".format(timesLoop))
for min in range(timesLoop):
	f.write("<tr>\n")
	for radio, numStations in radios.items():
		withoutIP = 0
		dissociated = 0
		good = 0

		for i in range(0,numStations):
			staName = "sta" + radio[-1:] + str(paddingNum + i)[1:]
			staStatus = getJsonInfo(mgrURL, "port/1/1/" + staName)
			if staStatus['interface']['ip'] == "0.0.0.0":
				withoutIP += 1
				if staStatus['interface']['ap'] == None:
					dissociated += 1
			else:
				good += 1

		if withoutIP and not dissociated:
			f.write("<td style=\"background-color:rgb(255,200,0);\">{}/{}</td>\n".format(good,numStations)) #without IP assigned
		elif dissociated:
			f.write("<td style=\"background-color:rgb(255,150,150);\">{}/{}</td>\n".format(good,numStations)) #dissociated from AP
		else:
			f.write("<td style=\"background-color:rgb(0,255,0);\">{}/{}</td>\n".format(good,numStations)) #with IP and associated

	f.write("<td>{}</td>\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
	f.write("</tr>\n")
	#print("sleeping for {} seconds".format(intervalSec))
	time.sleep(intervalSec) #Sleeps for specified interval in seconds


f.write("</table></body></html>\n")
f.close()


curTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
subject = "Station Test End Report Notification"
body = "Report finished at {} see {}".format(curTime, webLog)
email = emailHelper.writeEmail(body)
emailHelper.sendEmail(email, sender, recipient, subject)


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
