#!/usr/bin/env python3

"""
    Script for creating a chamberview scenario.
"""

import sys
import os
import argparse
import time

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from chamberview import chamberview as cv

def main():

    parser = argparse.ArgumentParser(
        description="""use build_chamberview to create a lanforge chamberview scenario

    """)
    parser.add_argument("-m", "--lfmgr", type=str,
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-cs", "--create_scenario", "--create_lf_scenario", type=str,
                        help="name of scenario to be created")
    parser.add_argument("-p", "--profile", type=str, required=True,
                        help="name of profile")
    parser.add_argument("-n", "--no_stations", type=str, required=True,
                        help="Number of stations")
    parser.add_argument("-d", "--dut", "--DUT", type=str, required=True,
                        help="Name of the DUT")
    parser.add_argument("-dr", "--dr", "--dut_radio", type=str, required=True,
                        help="Select DUT Radio ex. \"Radio-1\", \"Radio-2\"")
    parser.add_argument("-t", "--t", "--traffic", type=str, required=True,
                        help="Select traffic ex. \"tcp-dl-6m-vi\"")
    parser.add_argument("-r", "--r", "--radio", type=str, required=True,
                        help="Select traffic ex. \"wiphy0\"")


    args = parser.parse_args()
    if args.lfmgr is not None:
        lfjson_host = args.lfmgr
    if args.port is not None:
        lfjson_port = args.port

    scenario_name = args.create_scenario
    profile_name = args.profile
    create_stations = args.no_stations
    dut_name = args.dut
    dut_radio = args.dr
    traffic_type = args.t
    radio = args.r

    createCV = cv(lfjson_host, lfjson_port); #Create a object
    createCV.manage_cv_scenario(scenario_name, profile_name, create_stations, dut_name, dut_radio
                                , traffic_type, radio); #To manage scenario
    createCV.sync_cv() #chamberview sync

    time.sleep(2)
    createCV.apply_cv_scenario(scenario_name) #Apply scenario
    createCV.apply_cv_scenario(scenario_name)
    createCV.apply_cv_scenario(scenario_name)
    createCV.apply_cv_scenario(scenario_name)
    createCV.apply_cv_scenario(scenario_name)
    createCV.apply_cv_scenario(scenario_name)

    time.sleep(2)
    createCV.build_cv_scenario() #build scenario
    print("End")


if __name__ == "__main__":
    main()
