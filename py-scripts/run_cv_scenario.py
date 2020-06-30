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
    def __init__(self, lfhost="localhost", lfport=8080, debug_=True, lanforge_db_=None, cv_scenario_=None, cv_test_=None, test_scenario_=None):
        super().__init__( _lfjson_host=lfhost, _lfjson_port=lfport, _debug=debug_, _halt_on_error=True, _exit_on_error=True, _exit_on_fail=True)
        self.lanforge_db = lanforge_db_
        self.cv_scenario = cv_scenario_
        self.cv_test = cv_test_
        self.test_profile = test_scenario_
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
            print("looking for ports like vap+")
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
            "name": self.lanforge_db,
            "action":"overwrite",
            "clean_dut":"yes",
            "clean_chambers": "yes"
        }
        self.json_post("/cli-json/load", data)
        sleep(1)
        self._pass("Loaded scenario %s" % self.lanforge_db, True)
        return True

    def start(self, debug_=False):
        # /gui_cli takes commands keyed on 'cmd', so we create an array of commands
        commands = [
            "cv apply '%s'" % self.cv_scenario,
            "sleep 2",
            "cv build",
            "sleep 2",
            "cv is_built",
            "sleep 2",
            "cv create '%s' test_ref" % self.cv_test,
            "sleep 2",
            "cv load test_ref '%s'" % self.test_profile,
            "sleep 2",
            # "cv click test_ref 'Auto Save Report'",
            # "cv click test_ref Start"
            # "cv get rvr_instance 'Report Location:'"
            "cv click test_ref Cancel"
        ]
        response_json = []
        for command in commands:
            data = {
                "cmd": command
            }
            try:
                debug_par = ""
                if debug_:
                    debug_par="?_debug=1"
                if command.endswith("is_built"):
                    self.localrealm.wait_while_building(debug_=debug_)
                elif command.startswith("sleep "):
                    nap = int(command.split(" ")[1])
                    sleep(nap)
                else:
                    response_json = []
                    response = self.json_post("/gui-json/cmd%s" % debug_par, data, debug_=True, response_json_list_=response_json)
                    if debug_:
                        LFUtils.debug_printer.pprint(response_json)


            except Exception as x:
                print(x)

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
    parser.add_argument("-d", "--lanforge_db", type=str, help="Name of test scenario database (see Status Tab)")
    parser.add_argument("-c", "--cv_scenario", type=str, help="Name of Chamber View test scenario (see CV Manage Scenarios)")
    parser.add_argument("-n", "--cv_test", type=str, help="Chamber View test")
    parser.add_argument("-s", "--test_profile", type=str, help="Name of the saved CV test profile")

    args = parser.parse_args()
    if args.lfmgr is not None:
        lfjson_host = args.lfmgr
    if args.port is not None:
        lfjson_port = args.port

    run_cv_scenario = RunCvScenario(lfjson_host, lfjson_port)

    if args.lanforge_db is not None:
        run_cv_scenario.lanforge_db = args.lanforge_db
    if args.cv_scenario is not None:
        run_cv_scenario.cv_scenario = args.cv_scenario
    if args.cv_test is not None:
        run_cv_scenario.cv_test = args.cv_test
    if args.test_profile is not None:
        run_cv_scenario.test_profile = args.test_profile

    if (run_cv_scenario.lanforge_db is None) or (run_cv_scenario.lanforge_db == ""):
        raise ValueError("Please specificy scenario database name with --scenario_db")


    if not (run_cv_scenario.build() and run_cv_scenario.passes()):
        print("scenario failed to build.")
        print(run_cv_scenario.get_fail_message())
        exit(1)

    if not (run_cv_scenario.start() and run_cv_scenario.passes()):
        print("scenario failed to start.")
        print(run_cv_scenario.get_fail_message())
        exit(1)

    if not (run_cv_scenario.stop() and run_cv_scenario.passes()):
        print("scenario failed to stop:")
        print(run_cv_scenario.get_fail_message())
        exit(1)

    if not (run_cv_scenario.cleanup() and run_cv_scenario.passes()):
        print("scenario failed to clean up:")
        print(run_cv_scenario.get_fail_message())
        exit(1)

    report_file = run_cv_scenario.get_report_file_name()
    print("Report file saved to "+report_file)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
    main()
