#!/usr/bin/env python3
"""
NAME: lf_cleanup.py

PURPOSE: clean up stations, cross connects and endpoints

EXAMPLE:  ./lf_cleanup.py --mgr <lanforge ip>

Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
import os
import importlib
import argparse
from pprint import pprint
import time
import datetime

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm


class lf_clean(Realm):
    def __init__(self,
            host="localhost",
            port=8080):
        super().__init__(lfclient_host=host,
                 lfclient_port=port),
        self.host = host
        self.port = port
        #self.cx_profile = self.new_l3_cx_profile()

    def cleanup(self):
        try:
            sta_json = super().json_get("port/1/1/list?field=alias")['interfaces']
        except TypeError:
            sta_json = None
        cx_json = super().json_get("cx")
        endp_json = super().json_get("endp")

        # get and remove current stations
        if sta_json is not None:
            print("Removing old stations")
            for name in list(sta_json):
                for alias in list(name):
                    if 'sta' in alias:
                        #print(alias)
                        info = self.name_to_eid(alias)
                        req_url = "cli-json/rm_vlan"
                        data = {
                            "shelf": info[0],
                            "resource": info[1],
                            "port": info[2]
                        }
                        #print(data)
                        super().json_post(req_url, data)
                        time.sleep(.5)
                    if 'wlan' in alias:                        
                        info = self.name_to_eid(alias)
                        req_url = "cli-json/rm_vlan"
                        data = {
                            "shelf": info[0],
                            "resource": info[1],
                            "port": info[2]
                        }
                        #print(data)
                        super().json_post(req_url, data)
                        time.sleep(.5)
                    if 'Unknown' in alias:                        
                        info = self.name_to_eid(alias)
                        req_url = "cli-json/rm_vlan"
                        data = {
                            "shelf": info[0],
                            "resource": info[1],
                            "port": info[2]
                        }
                        #print(data)
                        super().json_post(req_url, data)
                        time.sleep(.5)

        else:
            print("No stations found to cleanup")

        # get and remove current cxs
        if cx_json is not None:
            print("Removing old cross connects")
            for name in list(cx_json):
                if name != 'handler' and name != 'uri':
                    #print(name)
                    req_url = "cli-json/rm_cx"
                    data = {
                        "test_mgr": "default_tm",
                        "cx_name": name
                    }
                    super().json_post(req_url, data)
                    time.sleep(.5)
        else:
            print("No cross connects found to cleanup")

        # get and remove current endps
        if endp_json is not None:
            print("Removing old endpoints")
            for name in list(endp_json['endpoint']):
                #print(list(name)[0])
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": list(name)[0]
                }
                #print(data)
                super().json_post(req_url, data)
                time.sleep(.5)
        else:
            print("No endpoints found to cleanup")


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug = False

    parser = argparse.ArgumentParser(
        prog='lf_cleanup.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Clean up cxs and endpoints
            ''',
        description='''\
lf_cleanup.py:
--------------------
Generic command layout:

python3 ./lf_clean.py --mgr MGR 

    default port is 8080
         
    clean up stations, cxs and enspoints.
    NOTE: will only cleanup what is present in the GUI so need to iterate multiple times with lf_clean.py
            ''')
    parser.add_argument('--mgr','--lfmgr', help='--mgr <hostname for where LANforge GUI is running>', default='localhost')


    args = parser.parse_args()

    clean = lf_clean(host=args.mgr)
    print("cleaning up stations, cxs and endpoints: start")
    clean.cleanup()
    print("cleaning up stations, cxs and endpoints: done with current pass may need to iterate multiple times")

if __name__ == "__main__":
    main()
