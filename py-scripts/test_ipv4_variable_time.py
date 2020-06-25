#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
import time

class IPV4VariableTime(LFCliBase):
    def __init__(self):
        self.local_realm = realm.Realm()
    def run_test(self): pass
    def cleanup(self): pass
    def run(self):
        print(self.local_realm.parse_time("10m"))

def main():
    ip_var_test = IPV4VariableTime()
    ip_var_test.run()
if __name__ == "__main__":
    main()