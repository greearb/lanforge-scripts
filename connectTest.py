#!/usr/bin/env python3
import os
import time
import sys
sys.path.append('py-json')
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

mgrURL = "http://localhost:8080/"


def execWrap(cmd):
	if os.system(cmd) != 0:
		print("\nError with " + cmd + ",bye\n")
		exit(1)

#create cx for tcp and udp
cmd = ("perl lf_firemod.pl --action create_cx --cx_name test1 --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type tcp")
execWrap(cmd)
cmd = ("perl lf_firemod.pl --action create_cx --cx_name test2 --use_ports sta00000,eth1 --use_speeds  360000,150000 --endp_type udp")
execWrap(cmd)

#create l4 endpoint
lf_r = LFRequest.LFRequest(mgrURL + "cli-json/add_l4_endp")
lf_r.addPostData(
{
"alias":"l4Test",
"shelf":1,
"resource":1,
"port":"sta00000",
"type":"l4_generic",
"timeout":1000,
"url_rate":600,
"url":"dl http://10.40.0.1/ /dev/null"
})

lf_r.jsonPost()
#json_response = lf_r.jsonPost(True)
#LFUtils.debug_printer.pprint(json_response)
#sys.exit(1)


#create cx for l4_endp
lf_r = LFRequest.LFRequest(mgrURL + "cli-json/add_cx")
lf_r.addPostData(
{
"alias":"CX_l4Test",
"test_mgr":"default_tm",
"tx_endp":"l4Test",
"rx_endp":"NA"
})

lf_r.jsonPost()
json_response = lf_r.jsonPost(True)
LFUtils.debug_printer.pprint(json_response)
#sys.exit(1)


#start cx traffic
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm test1 RUNNING\"")
execWrap(cmd)
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm test2 RUNNING\"")
execWrap(cmd)
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm CX_l4Test RUNNING\"")
execWrap(cmd)

time.sleep(5)


#show tx and rx bytes for ports
time.sleep(5)
print("eth1")
cmd = ("perl ./lf_portmod.pl --quiet 1 --manager localhost --port_name eth1 --show_port \"Txb,Rxb\"")
execWrap(cmd)
print("sta00000")
cmd = ("perl ./lf_portmod.pl --quiet 1 --manager localhost --port_name sta00000 --show_port \"Txb,Rxb\"")
execWrap(cmd)


#show tx and rx for endpoints
time.sleep(5)
print("test1-A")
cmd = ("./lf_firemod.pl --action show_endp --endp_name test1-A --endp_vals tx_bps,rx_bps")
execWrap(cmd)
print("test1-B")
cmd = ("./lf_firemod.pl --action show_endp --endp_name test1-B --endp_vals tx_bps,rx_bps")
execWrap(cmd)
print("test2-A")
cmd = ("./lf_firemod.pl --action show_endp --endp_name test2-A --endp_vals tx_bps,rx_bps")
execWrap(cmd)
print("test2-B")
cmd = ("./lf_firemod.pl --action show_endp --endp_name test2-B --endp_vals tx_bps,rx_bps")
execWrap(cmd)
print("l4Test")
cmd = ("./lf_firemod.pl --action show_endp --endp_name l4Test")
execWrap(cmd)


#stop cx traffic
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm test1 STOPPED\"")
execWrap(cmd)
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm test2 STOPPED\"")
execWrap(cmd)
cmd = ("perl lf_firemod.pl --mgr localhost --quiet 0 --action do_cmd --cmd \"set_cx_state default_tm CX_l4 STOPPED\"")
execWrap(cmd)

#get JSON info from webpage for ports and endps
url = ["port/","endp/"]
timeout = 5 # seconds

for i in range(len(url)):
	lf_r = LFRequest.LFRequest(mgrURL + url[i])
	json_response = lf_r.getAsJson()
	#print(json_response)
	j_printer = pprint.PrettyPrinter(indent=2)
	if not i:
		print("Ports: \n")
		for record in json_response['interfaces']:
			j_printer.pprint(record)
	else:
		print("Endpoints: \n")
		for record in json_response['endpoint']:
                        j_printer.pprint(record)

