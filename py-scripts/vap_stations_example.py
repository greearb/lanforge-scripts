#!/usr/bin/env python3
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)
if 'py-json' not in sys.path:
    sys.path.append('../py-json')
import traceback

from LANforge import LFUtils
from LANforge.LFUtils import *
from LANforge.lfcli_base import LFCliBase
from generic_cx import GenericCx

mgrURL = "http://localhost:8080/"
staName = "sta0"
staNameUri = "port/1/1/" + staName


class VapStations(LFCliBase):
    def __init__(self, lfhost, lfport):
        super().__init__(lfhost, lfport, _debug=False)
        super().check_connect()

    def run(self):
        list_resp = self.json_get("/stations/list")
        list_map = self.response_list_to_map(list_resp, 'stations')
        # pprint.pprint(list_map)

        attribs = ["ap", "capabilities", "tx rate", "rx rate", "signal"]
        for eid,record in list_map.items():
            # print("mac: %s" % mac)
            mac = record["station bssid"]
            station_resp = self.json_get("/stations/%s?fields=capabilities,tx+rate,rx+rate,signal,ap" % mac)
            print("Station %s:" %mac)
            #pprint.pprint(station_resp)
            for attrib in attribs:
                print("     %s:    %s" % (attrib, station_resp["station"][attrib]))


def main():
    vapsta_test = VapStations("localhost", 8080)
    vapsta_test.run()

if __name__ == '__main__':
    main()
