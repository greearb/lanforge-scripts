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
import datetime

class IPV4L4:
    def __init__(self, host, port, ssid, security, password, num_stations, side_a_min_rate=56, side_b_min_rate=56, side_a_max_rate=0,
                 side_b_max_rate=0, prefix="00000", test_duration="5m",
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)

    def build(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def cleanup(self):
        pass


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080


if __name__ == "__main__":
    main()