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
    ssid = "jedway-wpa2-x2048-4-1"
    passwd = "jedway-wpa2-x2048-4-1"
    j_printer = pprint.PrettyPrinter(indent=2)

    # example 1, /cli-form/rm_vlan
    # for each of the station IDs, delete them if they exist

    for i in range(start_id, end_id):
        url = base_url+"/port/%s/%s/%s" % (shelf_id, resource_id, i)
        print("checking for station : "+url)
        lf_r = LFRequest.LFRequest(url)
        json_response = lf_r.getAsJson()
        if (json_response != None):
            print("I would delete station %s now"%i)

        print("Next we create station %s"%i)

    print("done")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
   main()