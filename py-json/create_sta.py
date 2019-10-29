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
from LANforge import LFRequest

def main():
    base_url = "http://localhost:8080"
    shelf_id = 1        # typicaly assume Shelf 1
    resource_id = 1     # typically you're using resource 1 in stand alone realm
    radio = "wiphy0"
    start_id = 200
    end_id = 202
    padding_number = 10000 # the first digit of this will be deleted
    ssid = "jedway-wpa2-x2048-4-1"
    passphrase = "jedway-wpa2-x2048-4-1"
    j_printer = pprint.PrettyPrinter(indent=2)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # example 2                                                 -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # uses URL /cli-form/rm_vlan
    # for each of the station names, delete them if they exist
    # NOTE: the ID field of the EID is ephemeral, so best stick to
    # requesting the station name. The station name can be formatted
    # with leading zeros, sta00001 is legal and != {sta0001, sta001, sta01, or sta1}

    for i in range((padding_number+start_id), (padding_number+end_id)):
        sta_name = "sta"+str(i)[1:]
        url = base_url+"/port/%s/%s/%s" % (shelf_id, resource_id, sta_name)
        print("checking for station : "+url)
        lf_r = LFRequest.LFRequest(url)
        json_response = lf_r.getAsJson()
        if (json_response != None):
            print("I would delete station %s now"%sta_name)
            lf_r = LFRequest.LFRequest(base_url+"/cli-form/rm_vlan")
            lf_r.addPostData( {
                "shelf":1,
                "resource": resource_id,
                "port": "sta%s"%i
            })
            json_response = lf_r.formPost()
            print(json_response)

        print("Next we create station %s"%sta_name)
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
        lf_r.addPostData( {
            "shelf":1,
            "resource": resource_id,
            "radio": radio,
            "sta_name": "sta%s"%i,
            "flags":68727874560,
            "ssid": ssid,
            "key": passphrase,
            "mac": "xx:xx:xx:*:xx",
            "mode": 0,
            "rate": "DEFAULT"
        })
        json_response = lf_r.formPost()
        print(json_response)
    print("done")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # example 2                                                 -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # uses URL /cli-jsoin/rm_vlan
    # and that accepts json formatted POSTS

    for i in range((padding_number+start_id), (padding_number+end_id)):
        sta_name = "sta"+str(i)[1:]
        url = base_url+"/port/%s/%s/%s" % (shelf_id, resource_id, sta_name)
        print("checking for station : "+url)
        lf_r = LFRequest.LFRequest(url)
        json_response = lf_r.getAsJson()
        if (json_response != None):
            print("I would delete station %s now"%sta_name)
            lf_r = LFRequest.LFRequest(base_url+"/cli-json/rm_vlan")
            lf_r.addPostData( {
                "shelf":1,
                "resource": resource_id,
                "port": "sta%s"%i
            })
            json_response = lf_r.jsonPost()
            print(json_response)

        print("Next we create station %s"%sta_name)
        lf_r = LFRequest.LFRequest(base_url+"/cli-form/add_sta")

        # see notes from example 1 on flags and mac address patterns
        lf_r.addPostData( {
            "shelf":1,
            "resource": resource_id,
            "radio": radio,
            "sta_name": "sta%s"%i,
            "flags":68727874560,
            "ssid": ssid,
            "key": passphrase,
            "mac": "xx:xx:xx:*:xx",
            "mode": 0,
            "rate": "DEFAULT"
        })
        json_response = lf_r.jsonPost()
        print(json_response)


    print("done")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
   main()