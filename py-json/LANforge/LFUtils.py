# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define useful common methods                                  -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import pprint
import json
import time
from time import sleep
from random import seed
seed( int(round(time.time() * 1000)))
from random import randint
from LANforge import LFRequest

debug_printer = pprint.PrettyPrinter(indent=2)
base_url = "http://localhost:8080"

class PortEID:
    shelf: 1
    resource: 1
    port_id: 0
    port_name: ""

    def __init__(self, p_resource=1, p_port_id=0, p_port_name=""):
        resource = p_resource
        port_id = p_port_id
        port_name = p_port_name

    def __init__(self, json_response):
        if json_response == None:
            raise Exception("No json input")
        json_s = json_response
        if json_response['interface'] != None:
            json_s = json_response['interface']

        debug_printer(json_s)
        resource = json_s['resource']
        port_id = json_s['id']
        port_name = json_s['name']
# end class PortEID


def portNameSeries(prefix="sta", start_id=0, end_id=1, padding_number=1000):
    name_list = []
    for i in range((padding_number+start_id), (padding_number+end_id)):
        sta_name = prefix+str(i)[1:]
        name_list.append(sta_name)
    return name_list


# generate random hex if you need it for mac addresses
def generateRandomHex():
    # generate a few random numbers and convert them into hex:
    random_hex = []
    for rn in range(0, 254):
        random_dec = randint(0, 254)
        random_hex.append(hex(random_dec))
    return random_hex

# return reverse map of aliases to port records
def portAliasesInList(json_list):
    if len(json_list) < 1:
        raise Exception("empty list")
    reverse_map = {}
    json_interfaces = json_list
    if 'interfaces' in json_list:
        json_interfaces = json_list['interfaces']

    # expect nested records, which is an artifact of some ORM
    # that other customers expect:
    # [
    #   {
    #       "1.1.eth0": {
    #           "alias":"eth0"
    #       }
    #   },
    #   { ... }

    for record in json_interfaces:
        if len(record.keys()) < 1:
            continue
        record_keys = record.keys()
        #debug_printer.pprint(record_keys)
        k2 = ""
        for k in record_keys:
            k2 = k

        if k2.__contains__("Unknown"):
            #debug_printer.pprint("skipping: "+k2)
            continue

        port_json = record[k2]
        reverse_map[port_json['alias']] = record
    #print("resulting map: ")
    #debug_printer.pprint(reverse_map)
    return reverse_map


def findPortEids(resource_id=1, port_names=(), base_url="http://localhost:8080"):
    port_eids = []
    if len(port_names) < 0:
        return []
    for port_name in port_names:
        url = "/port/1/%s/%s"%(resource_id,port_name)
        lf_r = LFRequest.LFRequest(url)
        try:
            response = lf_r.getAsJson()
            if response == None:
                continue
            port_eids.append(PortEID(response))
        except:
            print("Not found: "+port_name)
    return None


def waitUntilPortsDisappear(resource_id=1, port_list=()):
    found_stations = port_list.copy()
    sleep(1)
    while len(found_stations) > 0:
        found_stations = []
        for port_name in port_list:
            sleep(1)
            url = base_url+"/port/1/%s/%s" % (resource_id, port_name)
            print("Example 2: checking for station : "+url)
            lf_r = LFRequest.LFRequest(url)
            json_response = lf_r.getAsJson()
            if (json_response != None):
                found_stations.append(port_name)
    return None

###
def waitUntilPortsAppear(resource_id=1, port_list=()):
    found_stations = []
    sleep(1)
    while len(found_stations) < len(port_list):
        found_stations = []
        for port_name in port_list:
            sleep(1)
            url = base_url+"/port/1/%s/%s" % (resource_id, port_name)
            print("Example 2: checking for station : "+url)
            lf_r = LFRequest.LFRequest(url)
            json_response = lf_r.getAsJson()
            if (json_response != None):
                found_stations.append(port_name)
    return None