#!/usr/bin/env python3

"""
Note: Script for creating a chamberview scenario.
    Run this script to set/create a chamber view scenario.
    ex. on how to run this script:
    ./create_chamberview.py -m "localhost" -o "8080" -cs "scenario_name" \
    --line "Resource=1.1 Profile=STA-AC Amount=1 Uses-1=wiphy0 Uses-2=AUTO Freq=-1 \
        DUT=test DUT_Radio=Radio-1 Traffic=http VLAN=vlan" \
    --line "Resource=1.1 Profile=STA-AC Amount=1 Uses-1=wiphy1 Uses-2=AUTO Freq=-1 \
        DUT=test DUT_Radio=Radio-2 Traffic=http VLAN=vlan"

"""            
import sys
import os
import argparse
import time
import re

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_commands import chamberview as cv

def main():
    global Resource, Amount, DUT, DUT_Radio, Profile, Uses1, Uses2, Traffic, Freq, VLAN


    parser = argparse.ArgumentParser(
        description="""
        For Two line scenario use --line twice as shown in example, for multi line scenario
        use --line argument to create multiple lines
        \n
           create_chamberview.py -m "localhost" -o "8080" -cs "scenario_name" 
             --line "Resource=1.1 Profile=STA-AC Amount=1 Uses-1=wiphy0 Uses-2=AUTO Freq=-1 
                    DUT=Test DUT_Radio=Radio-1 Traffic=http VLAN=VLAN" 
             --line "Resource=1.1 Profile=upstream Amount=1 Uses-1=wiphy1 Uses-2=AUTO Freq=-1 
                    DUT=Test DUT_Radio=Radio-2 Traffic=http VLAN=VLAN"
           """)
    parser.add_argument("-m", "--lfmgr", type=str,
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-cs", "--create_scenario", "--create_lf_scenario", type=str,
                        help="name of scenario to be created")
    parser.add_argument("-l", "--line", action='append', nargs='+', type=str, required=True,
                        help="line number")

    args = parser.parse_args()

    if args.lfmgr is not None:
        lfjson_host = args.lfmgr
    if args.port is not None:
        lfjson_port = args.port

    createCV = cv(lfjson_host, lfjson_port);  # Create a object
    scenario_name = args.create_scenario
    line = args.line

    Resource = "1.1"
    Profile = "STA-AC"
    Amount = "1"
    DUT = "DUT"
    DUT_Radio = "Radio-1"
    Uses1 = "wiphy0"
    Uses2 = "AUTO"
    Traffic = "http"
    Freq = "-1"
    VLAN = ""

    for i in range(len(line)):
        if " " in line[i][0]:
            line[i][0] = (re.split(' ', line[i][0]))
        elif "," in line[i][0]:
            line[i][0] = (re.split(',', line[i][0]))
            print("in second")
        elif ", " in line[i][0]:
            line[i][0] = (re.split(',', line[i][0]))
            print("in third")
        elif " ," in line[i][0]:
            line[i][0] = (re.split(',', line[i][0]))
            print("in forth")
        else:
            print("Wrong arguments entered !")
            exit(1)

        for j in range(len(line[i][0])):
            line[i][0][j] = line[i][0][j].split("=")
            for k in range(len(line[i][0][j])):
                name = line[i][0][j][k]
                if str(name) == "Resource" or str(name) == "Res" or str(name) == "R":
                    Resource = line[i][0][j][k + 1]
                elif str(name) == "Profile" or str(name) == "Prof" or str(name) == "P":
                    Profile = line[i][0][j][k + 1]
                elif str(name) == "Amount" or str(name) == "Sta" or str(name) == "A":
                    Amount = line[i][0][j][k + 1]
                elif str(name) == "Uses-1" or str(name) == "U1" or str(name) == "U-1":
                    Uses1 = line[i][0][j][k + 1]
                elif str(name) == "Uses-2" or str(name) == "U2" or str(name) == "U-2":
                    Uses2 = line[i][0][j][k + 1]
                elif str(name) == "Freq" or str(name) == "Freq" or str(name) == "F":
                    Freq = line[i][0][j][k + 1]
                elif str(name) == "DUT" or str(name) == "dut" or str(name) == "D":
                    DUT = line[i][0][j][k + 1]
                elif str(name) == "DUT_Radio" or str(name) == "dr" or str(name) == "DR":
                    DUT_Radio = line[i][0][j][k + 1]
                elif str(name) == "Traffic" or str(name) == "Traf" or str(name) == "T":
                    Traffic = line[i][0][j][k + 1]
                elif str(name) == "VLAN" or str(name) == "Vlan" or str(name) == "V":
                    VLAN = line[i][0][j][k + 1]
                else:
                    continue

        createCV.manage_cv_scenario(scenario_name,
                                    Resource,
                                    Profile,
                                    Amount,
                                    DUT,
                                    DUT_Radio,
                                    Uses1,
                                    Uses2,
                                    Traffic,
                                    Freq,
                                    VLAN
                                    );  # To manage scenario


    createCV.sync_cv() #chamberview sync
    time.sleep(2)
    createCV.apply_cv_scenario(scenario_name) #Apply scenario
    time.sleep(2)
    createCV.sync_cv()
    time.sleep(2)
    createCV.apply_cv_scenario(scenario_name)  # Apply scenario

    time.sleep(2)
    createCV.build_cv_scenario() #build scenario
    print("End")


if __name__ == "__main__":
    main()
