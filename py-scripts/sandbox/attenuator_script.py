#!/usr/bin/env python3
"""
NAME: attenuator_example.py

PURPOSE: example of creating traffic over an attenator with a script component

EXAMPLE:

NOTES:


"""
import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.insert(1, "../../py-json")
import argparse
import importlib
import os
import time
from os.path import exists
import pprint
from time import sleep

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))
lfcli_base = importlib.import_module('py-json.LANforge.lfcli_base')
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module('py-json.LANforge.LFUtils')
realm = importlib.import_module('py-json.realm')
Realm = realm.Realm

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase


class AttenExample(Realm):
    def __init__(self,
                 host=None,
                 port=None,
                 attenuator=None,
                 interval_sec: float = 1.0,
                 sta_eid=None,
                 desired_bps=10000000,
                 _deep_clean=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host,
                         port,
                         debug_=_debug_on,
                         _exit_on_fail=_exit_on_fail)
        self.attenuator = attenuator
        self.interval_sec = interval_sec
        self.sta_eid = sta_eid
        self.desired_bps = desired_bps

    def start(self):
        sta_profile = Realm.new_station_profile()
        # set the station profile up and create a station later

        # set up the upstream later

        # create the layer or generic traffic later

        # load the attenuator script:
        self.attenuator = "1.1.1005"
        self.json_post("/cli-json/set_atten",
                       data={
                           "shelf": 1,
                           "resource": 1,
                           "serno": 1005,
                           "atten_idx": "all",
                           "val": 0,
                           "mode": 0
                       },
                       debug=True)

        self.json_post("/cli-json/set-script",
                       data={
                           "endp": "1005",
                           "name": "my-script",
                           "flags": 0x4000,
                           "type": "ScriptAtten",
                           "private": "30000 50,100,150,200,250,300,350"
                       },
                       debug=True)
        self.json_post("/cli-json/set_atten",
                       data={
                           "self": 1,
                           "resource": 1,
                           "serno": 1005,
                           "atten_idx": "all",
                           "val": "START"
                       },
                       debug=True)

    time.sleep(30)
    self.json_post("/cli-json/set_atten",
                   data={
                       "self": 1,
                       "resource": 1,
                       "serno": 1005,
                       "atten_idx": "all",
                       "val": "STOP"
                   },
                   debug=True)


def main():
    parser = LFCliBase.create_bare_argparse(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description="""Example showing how to load a script option into an attenuator
""")
    parser.add_argument('--station', help="command to execute when attenuator changes levels")
    parser.add_argument('--upstream', help="When True, do an action for every channel that changes")
    parser.add_argument('--attenuator', help="attenuator entity id to watch; E.G.: 1.1.323")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
