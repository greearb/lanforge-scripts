#!/usr/bin/env python3

# This script will set the LANforge to a BLANK database then it will load the specified database
# and start a graphical report

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
from realm import Realm

"""
        cvScenario.scenario_db = args.scenario_db
    if args.cv_test is not None:
        cvScenario.cv_test = args.cv_test
    if args.test_scenario is not None:
        cvScenario.test_scenario = args.test_scenario
"""

class RunCvScenario(LFCliBase):
    def __init__(self, lfhost="localhost", lfport=8080, debug_=True, scenario_db_=None, cv_test_=None, test_scenario_=None):
        super().__init__( _lfjson_host=lfhost, _lfjson_port=lfport, _debug=debug_, _halt_on_error=True, _exit_on_error=True, _exit_on_fail=True)
        self.scenario_db = scenario_db_
        self.cv_test = cv_test_
        self.test_scenario = test_scenario_
        self.localrealm = Realm(lfclient_host=lfhost, lfclient_port=lfport, debug_=debug_)
        self.report_name = None

    def get_report_file_name(self):
        return self.report_name

    def build(self):
        data = {
            "name": "BLANK",
            "action":"overwrite",
            "clean_dut":"yes",
            "clean_chambers": "yes"
        }
        self.json_post("/cli-json/load", data)
        sleep(1)
        port_counter = 0;
        attempts = 6
        while (attempts > 0) and (port_counter > 0):
            sleep(1)
            attempts -= 1
            port_list = self.localrealm.find_ports_like("vap+")
            alias_map = LFUtils.portListToAliasMap(port_list)
            port_counter = len(alias_map)

            port_list = self.localrealm.find_ports_like("sta+")
            alias_map = LFUtils.portListToAliasMap(port_list)
            port_counter += len(alias_map)
            if port_counter == 0:
                break

        if (port_counter != 0) and (attempts == 0):
            print("There appears to be a vAP in this database, quitting.")
            pprint(alias_map);
            exit(1)

        data = {
            "name": self.scenario_db,
            "action":"overwrite",
            "clean_dut":"yes",
            "clean_chambers": "yes"
        }
        self.json_post("/cli-json/load", data)
        self._pass("Loaded scenario %s" % self.scenario_db, True)

    def start(self):
        # /gui_cli takes commands keyed on 'cmd', so we create an array of commands
        commands = [

            "cv apply s1101",
            "cv create 'Rate vs Range' rvr_instance"
            "cv click rvr_instance Start",
            "cv get rvr_instance 'Report Location:'"
        ]
        self.use_preexec = False
        for command in commands:
            data = {
                "cmd": command
            }
            self.json_post("/gui-cli", data)
            sleep(1)

        self._fail("start unfinished", print_=True)


    def stop(self):
        self._fail("stop unfinished", print_=True)

    def cleanup(self):
        self._fail("cleanup unfinished", print_=True)


def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    parser = argparse.ArgumentParser(
        description="""LANforge Reporting Script:  Load a scenario and run a RvR report
Example:
./load_ap_scenario.py --lfmgr 127.0.0.1 --scenario_db 'handsets' --cv_test  --test_scenario 'test-20'
""")
    parser.add_argument("-m", "--lfmgr", type=str, help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("-d", "--scenario_db", type=str, help="Name of test scenario database (see Status Tab)")
    parser.add_argument("-t", "--cv_test", type=str, help="Chamber View test")
    parser.add_argument("-s", "--test_scenario", type=str, help="Scenario name of the CV test")

    args = parser.parse_args()
    if args.lfmgr is not None:
        lfjson_host = args.lfmgr
    if args.port is not None:
        lfjson_port = args.port

    cvScenario = RunCvScenario(lfjson_host, lfjson_port)

    if args.scenario_db is not None:
        cvScenario.scenario_db = args.scenario_db
    if args.cv_test is not None:
        cvScenario.cv_test = args.cv_test
    if args.test_scenario is not None:
        cvScenario.test_scenario = args.test_scenario

    if (cvScenario.scenario_db is None) or (cvScenario.scenario_db == ""):
        raise ValueError("Please specificy scenario database name with --scenario_db")

    cvScenario.build()
    if cvScenario.passes() != True:
        print(cvScenario.get_fail_message())
        exit(1)
    cvScenario.start()
    if cvScenario.passes() != True:
        print(cvScenario.get_fail_message())
        exit(1)
    cvScenario.stop()
    if cvScenario.passes() != True:
        print(cvScenario.get_fail_message())
        exit(1)
    cvScenario.cleanup()
    if cvScenario.passes() != True:
        print(cvScenario.get_fail_message())
        exit(1)

    report_file = cvScenario.get_report_file_name()
    print("Report file saved to "+report_file)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
