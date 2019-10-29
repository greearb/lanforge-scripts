# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# example of how to create a LANforge station                                       -
#                                                                                   -
# two examples, first using the URL-Encoded POST
# second using JSON POST data
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import json
import pprint
import time
from time import sleep

from LANforge import LFRequest
from LANforge import LFUtils

def gen_mac(parent_mac, random_octet):
    print("************ random_octet: %s **************"%(random_octet))
    my_oct = random_octet
    if (len(random_octet) == 4):
        my_oct = random_octet[2:]
    octets = parent_mac.split(":")
    octets[4] = my_oct
    return ":".join(octets)

def main():
    base_url = "http://localhost:8080"
    resource_id = 1     # typically you're using resource 1 in stand alone realm
    radio = "wiphy0"
    start_id = 200
    end_id = 202
    padding_number = 10000 # the first digit of this will be deleted
    ssid = "jedway-wpa2-x2048-4-1"
    passphrase = "jedway-wpa2-x2048-4-1"
    j_printer = pprint.PrettyPrinter(indent=2)
    json_post = ""
    json_response = ""

    lf_r = LFRequest.LFRequest(base_url+"/port/1/1/wiphy0")
    wiphy0_json = lf_r.getAsJson()
    if (wiphy0_json is None) or (wiphy0_json['interface'] is None):
        print("Unable to find radio. Are we connected?")
        exit(1)

    print("# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("# radio wiphy0                                              -")
    print("# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    LFUtils.debug_printer.pprint(wiphy0_json['interface']['alias'])
    #parent_radio_mac = wiphy0_json['interface']['mac']
    print("# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    found_stations = []


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # example 1                                                 -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # This section uses URLs /cli-form/rm_vlan, /cli-form/add_sta
    # The /cli-form URIs take URL-encoded form posts
    #
    # For each of the station names, delete them if they exist. It
    # takes a few milliseconds to delete them, so after deleting them
    # you need to poll until they don't appear.
    #
    # NOTE: the ID field of the EID is ephemeral, so best stick to
    # requesting the station name. The station name can be formatted
    # with leading zeros, sta00001 is legal
    # and != {sta0001, sta001, sta01, or sta1}

    desired_stations = LFUtils.portNameSeries("sta", start_id, end_id, padding_number)

    for sta_name in desired_stations:
        url = base_url+"/port/1/%s/%s" % (resource_id, sta_name)
        print("Example 1: Checking for station : "+url)
        lf_r = LFRequest.LFRequest(url)
        json_response = lf_r.getAsJson()
        if (json_response != None):
            found_stations.append(sta_name)

    for sta_name in found_stations:
        print("Ex 1: Deleting station %s ...."%sta_name)
        lf_r = LFRequest.LFRequest(base_url+"/cli-form/rm_vlan")
        lf_r.addPostData( {
            "shelf":1,
            "resource": resource_id,
            "port": sta_name
        })
        json_response = lf_r.formPost()
        sleep(0.05) # best to give LANforge a few millis between rm_vlan commands

    LFUtils.waitUntilPortsDisappear(resource_id, found_stations)

    print("Example 1: Next we create stations...")
    for sta_name in desired_stations:
        print("Example 1: Next we create station %s"%sta_name)
        lf_r = LFRequest.LFRequest(base_url+"/cli-form/add_sta")
        # flags are a decimal equivalent of a hexadecimal bitfield
        # you can submit as either 0x(hex) or (dec)
        # a helper page is available at http://localhost:8080/help/add_sta
        #
        # You can watch console output of the LANforge GUI client when you
        # get errors to this command, and you can also watch the websocket
        # output for a response to this command at ws://localhost:8081
        # Use wsdump ws://localhost:8081/
        #
        # modes are listed at http://<YOUR_LANFORGE>/LANforgeDocs-5.4.1/lfcli_ug.html
        # or at https://www.candelatech.com/lfcli_ug.html
        #
        # mac address field is a pattern for creation: entirely random mac addresses
        # do not take advantage of address mask matchin in Ath10k hardware, so we developed
        # this pattern to randomize a section of octets. XX: keep parent, *: randomize, and
        # chars [0-9a-f]: use this digit
        #
        # If you get errors like "X is invalid hex character", this indicates a previous
        # rm_vlan call has not removed your station yet: you cannot rewrite mac addresses
        # with this call, just create new stations
        lf_r.addPostData( {
            "shelf":1,
            "resource": resource_id,
            "radio": radio,
            "sta_name": sta_name,
            "flags":68727874560,
            "ssid": ssid,
            "key": passphrase,
            "mac": "xx:xx:xx:xx:*:xx", # "NA", #gen_mac(parent_radio_mac, random_hex.pop(0))
            "mode": 0,
            "rate": "DEFAULT"
        })
        json_response = lf_r.formPost()
        print(json_response)
        sleep(1)

    LFUtils.waitUntilPortsAppear()
    print("...done with example 1\n\n")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Example 2                                                 -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # uses URLs /cli-json/rm_vlan, /cli-json/add_sta
    # and those accept POST in json formatted text
    desired_stations = []
    found_stations = []
    for i in range((padding_number+start_id), (padding_number+end_id)):
        desired_stations.append("sta"+str(i)[1:])

    print("Example 2: using port list to find stations")
    url = base_url+"/port/1/%s/list?fields=alias" % (resource_id)
    lf_r = LFRequest.LFRequest(url)
    json_response = lf_r.getAsJson()
    if json_response == None:
        raise Exception("no reponse to: "+url)

    port_map = LFUtils.portAliasesInList(json_response)
    #LFUtils.debug_printer.pprint(port_map)
    for sta_name in desired_stations:
        print("Example 2: checking for station : "+sta_name)
        #LFUtils.debug_printer.pprint(port_map.keys())
        if sta_name in port_map.keys():
            print("found station : "+sta_name)
            found_stations.append(sta_name)

    for sta_name in found_stations:
        print("Example 2: delete station %s ..."%sta_name)
        lf_r = LFRequest.LFRequest(base_url+"/cli-json/rm_vlan")
        lf_r.addPostData({
                "shelf":1,
                "resource": resource_id,
                "port": sta_name
            })
        lf_r.jsonPost()
        sleep(0.05)

    LFUtils.waitUntilPortsDisappear(resource_id, found_stations)

    for sta_name in desired_stations:
        print("Example 2: create station %s"%sta_name)
        lf_r = LFRequest.LFRequest(base_url+"/cli-json/add_sta")
        # see notes from example 1 on flags and mac address patterns
        #octet = random_hex.pop(0)[2:] is a method
        #gen_mac(parent_radio_mac, octet)
        lf_r.addPostData( {
            "shelf":1,
            "resource": resource_id,
            "radio": radio,
            "sta_name": sta_name,
            "flags":68727874560,
            "ssid": ssid,
            "key": passphrase,
            "mac": "xx:xx:xx:xx:*:xx",
            "mode": 0,
            "rate": "DEFAULT"
        })
        lf_r.jsonPost()
    print("...done with Example 2")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
   main()