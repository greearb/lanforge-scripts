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
    # create multiple OPEN stations
    station_names = LFUtils.port_name_series(start_id=10, end_id=19)

    test = StaConnect("localhost", 8080, _debugOn=False, _exit_on_error=True,
                        _cleanup_on_exit=False, _runtime_sec=360, _exit_on_fail=True)
    test.sta_mode = sta_connect.MODE_AUTO
    test.upstream_resource = 1
    test.upstream_port = "eth1"
    test.radio = "wiphy0"
    test.resource = 1
    test.dut_security = sta_connect.OPEN
    test.dut_ssid = "jedway-open"
    test.dut_passwd = "[BLANK]"
    test.station_names = station_names
    test.runtime_secs = 500
    test.cleanup_on_exit = False

    test.run()
    is_passing = test.passes()
    if is_passing == False:
        # run_results = staConnect.get_failed_result_list()
        fail_message = test.get_fail_message()
        print("Some tests failed:\n" + fail_message)
        return
    else:
        print("Tests pass")

    # Stations use WPA2
    test.dut_security = sta_connect.WPA2
    test.dut_ssid = "jedway-wpa2-x2048-5-1"
    test.dut_passwd = "jedway-wpa2-x2048-5-1"
    test.run()
    is_passing = test.passes()
    if is_passing == False:
        # run_results = staConnect.get_failed_result_list()
        fail_message = test.get_fail_message()
        print("Some tests failed:\n" + fail_message)
        return
    else:
        print("Tests pass")

    if test.cleanup_on_exit == True:
        test.remove_stations()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == '__main__':
    main()

#
