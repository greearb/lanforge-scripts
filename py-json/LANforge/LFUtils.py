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

ADD_STA_FLAGS_DOWN_WPA2 = 68719477760

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

# for use with set_port
def portDhcpUpRequest(resource_id, port_name):
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 2147483648, # 0x1 = interface down + 2147483648 use DHCP values
        "interest": 75513859 # includes use_command_flags + use_current_flags + dhcp + dhcp_rls + ifdown
    }
    return data

# for use with set_port
def portDownRequest(resource_id, port_name):
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 1, # 0x0 = interface up

        "interest": 75513859
    }
    return data


def generateMac(parent_mac, random_octet):
    print("************ random_octet: %s **************"%(random_octet))
    my_oct = random_octet
    if (len(random_octet) == 4):
        my_oct = random_octet[2:]
    octets = parent_mac.split(":")
    octets[4] = my_oct
    return ":".join(octets)

# this produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
# the padding_number is added to the start and end numbers and the resulting sum
# has the first digit trimmed, so f(0, 1, 10000) => {0000, 0001}
def portNameSeries(prefix="sta", start_id=0, end_id=1, padding_number=1000):
    name_list = []
    for i in range((padding_number+start_id), (padding_number+end_id+1)):
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