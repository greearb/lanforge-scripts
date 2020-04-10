#!/usr/bin/env python3
import os
import time
import sys
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()


def jsonReq(mgrURL,reqURL,postData,debug=False):
        lf_r = LFRequest.LFRequest(mgrURL + reqURL)
        lf_r.addPostData(postData)

        if debug:
                json_response = lf_r.jsonPost(True)
                LFUtils.debug_printer.pprint(json_response)
                sys.exit(1)
        else:
             	lf_r.jsonPost()

def createGenEndp(alias, shelf, rsrc, port, type):
	mgrURL = "http://localhost:8080/"
	reqURL = "cli-json/add_gen_endp"
	data = {
	"alias":alias,
	"shelf":shelf,
	"resource":rsrc,
	"port":port,
	"type":type
	}
	jsonReq(mgrURL,reqURL,data)

def setFlags(endpName, flagName,val):
	mgrURL = "http://localhost:8080/"
	reqURL = "cli-json/set_endp_flag"
	data = {
	"name":endpName,
	"flag":flagName,
	"val":val
	}
	jsonReq(mgrURL,reqURL,data)

def setCmd(endpName,cmd):
	mgrURL = "http://localhost:8080/"
	reqURL = "cli-json/set_gen_cmd"
	data = {
	"name":endpName,
	"command":cmd
	}
	jsonReq(mgrURL,reqURL,data)

