#!/usr/bin/env python3


# Example of how to instantiate StaConnect and run the test

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)
if 'py-json' not in sys.path:
    sys.path.append('../py-json')

# if you lack __init__.py in this directory you will not find sta_connect module
import sta_connect
from sta_connect import *
import realm
from realm import Realm
import LANforge
from LANforge import LFUtils

def main():
    # create multiple open stations
    station_names = LFUtils.port_name_series(start_id=0, end_id=1)
    test = StaConnect("localhost", 8080, _debugOn=False)
    test.sta_mode = sta_connect.MODE_AUTO
    test.upstream_resource = 1
    test.upstream_port = "eth1"
    test.radio = "wiphy0"
    test.resource = 1
    test.dut_security = sta_connect.OPEN
    test.dut_ssid = "jedway-open"
    test.dut_passwd = "NA"
    test.name_list = station_names
    test.run()
    is_passing = test.passes()
    if is_passing == False:
        # run_results = staConnect.get_failed_result_list()
        fail_message = test.get_fail_message()
        print("Some tests failed:\n" + fail_message)
    else:
        print("Tests pass")
    test.remove_stations()

    test.dut_security = sta_connect.WPA2
    test.dut_ssid = "jedway-wpa2-x2048-5-1"
    test.dut_passwd = "jedway-wpa2-x2048-5-1"
    test.run()
    is_passing = test.passes()
    if is_passing == False:
        # run_results = staConnect.get_failed_result_list()
        fail_message = test.get_fail_message()
        print("Some tests failed:\n" + fail_message)
    else:
        print("Tests pass")
    test.remove_stations()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == '__main__':
    main()

#
