#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge import LFUtils
# from LANforge import LFCliBase
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from realm import Realm

"""
TODO:
initialize with sta create values
set time for test duration
create cx for traffic test
start cx, run for specified time
stop cx
run test; validate ip, look for change in traffic, other?
log test values

"""

class IPv4Test(LFCliBase):
    def __init__(self):

    def set_duration(self, duration):
        if duration is not None:
            pattern = re.compile("^(\d+)([dhms]$)")
            td = pattern.match(duration)
            if td is not None:
                dur_time = int(td.group(1))
                dur_measure = str(td.group(2))
                now = datetime.datetime.now()
                if dur_measure == "d":
                    duration_time = datetime.timedelta(days=dur_time)
                elif dur_measure == "h":
                    duration_time = datetime.timedelta(hours=dur_time)
                elif dur_measure == "m":
                    duration_time = datetime.timedelta(minutes=dur_time)
                else:
                    duration_time = datetime.timedelta(seconds=dur_time)
            else:
                raise ValueError("Test duration invalid ")

    def compare_vals(self, name, postVal, print_pass=False, print_fail=True):
        # print(f"Comparing {name}")
        if postVal > 0:
            self._pass("%s %s" % (name, postVal), print_pass)
        else:
            self._fail("%s did not report traffic: %s" % (name, postVal), print_fail)
    def cleanup(self):

    def run(self):

def main():
    #get cli arguments
    #init sta and cx
    #run tests
    #determine pass/fail
    #log results
    #cleanup, exit

if __name__ == "__main__":
    main()