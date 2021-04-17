"""
Note: This script is working as library for chamberview tests.
    It holds different commands to automate test.
"""

import time

from LANforge.lfcli_base import LFCliBase
from realm import Realm
import json
from pprint import pprint
import argparse
from cv_test_reports import lanforge_reports as lf_rpt

def cv_add_base_parser(parser):
    parser.add_argument("-m", "--mgr", type=str, default="localhost",
                        help="address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", type=int, default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user", type=str, default="lanforge",
                        help="LANforge username to pull reports")
    parser.add_argument("--lf_password", type=str, default="lanforge",
                        help="LANforge Password to pull reports")
    parser.add_argument("-i", "--instance_name", type=str,
                        help="create test instance")
    parser.add_argument("-c", "--config_name", type=str,
                        help="Config file name")

    parser.add_argument("-r", "--pull_report", default=False, action='store_true',
                        help="pull reports from lanforge (by default: False)")
    parser.add_argument("--load_old_cfg", default=False, action='store_true',
                        help="Should we first load defaults from previous run of the capacity test?  Default is False")

    parser.add_argument("--enable", action='append', nargs=1, default=[],
                        help="Specify options to enable (set cfg-file value to 1).  See example raw text config for possible options.  May be specified multiple times.  Most tests are enabled by default, except: longterm")
    parser.add_argument("--disable", action='append', nargs=1, default=[],
                        help="Specify options to disable (set value to 0).  See example raw text config for possible options.  May be specified multiple times.")
    parser.add_argument("--set", action='append', nargs=2, default=[],
                        help="Specify options to set values based on their label in the GUI. Example: --set 'Basic Client Connectivity' 1  May be specified multiple times.")
    parser.add_argument("--raw_line", action='append', nargs=1, default=[],
                        help="Specify lines of the raw config file.  Example: --raw_line 'test_rig: Ferndale-01-Basic'  See example raw text config for possible options.  This is catch-all for any options not available to be specified elsewhere.  May be specified multiple times.")

    parser.add_argument("--raw_lines_file", default="",
                        help="Specify a file of raw lines to apply.")


class cv_test(Realm):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 ):
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port)

    # Add a config line to a text blob.  Will create new text blob
    # if none exists already.
    def create_test_config(self, config_name, blob_test_name, text):
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": str(blob_test_name + config_name),
            "text": text
        }

        print("adding- " + text + " " + "to test config")

        rsp = self.json_post(req_url, data)
        # time.sleep(1)

    # Tell LANforge GUI Chamber View to launch a test
    def create_test(self, test_name, instance, load_old_cfg):
        cmd = "cv create '{0}' '{1}' '{2}'".format(test_name, instance, load_old_cfg)
        return self.run_cv_cmd(str(cmd))


    # Tell LANforge chamber view to load a scenario.
    def load_test_scenario(self, instance, scenario):
        cmd = "cv load '{0}' '{1}'".format(instance, scenario)
        self.run_cv_cmd(cmd)

    #load test config for a chamber view test instance.
    def load_test_config(self, test_config, instance):
        cmd = "cv load '{0}' '{1}'".format(instance, test_config)
        self.run_cv_cmd(cmd)

    #start the test
    def start_test(self, instance):
        cmd = "cv click '%s' Start" % instance
        return self.run_cv_cmd(cmd)

    #close test
    def close_test(self, instance):
        cmd = "cv click '%s' 'Close'" % instance
        self.run_cv_cmd(cmd)

    #Cancel
    def cancel_test(self, instance):
        cmd = "cv click '%s' Cancel" % instance
        self.run_cv_cmd(cmd)

    # Send chamber view commands to the LANforge GUI
    def run_cv_cmd(self, command):
        response_json = []
        req_url = "/gui-json/cmd"
        data = {
            "cmd": command
        }
        debug_par = ""
        rsp = self.json_post("/gui-json/cmd%s" % debug_par, data, debug_=False, response_json_list_=response_json)
        return response_json

    #For auto save report
    def auto_save_report(self, instance):
        cmd = "cv click %s 'Auto Save Report'" % instance
        self.run_cv_cmd(cmd)

    #To get the report location
    def get_report_location(self, instance):
        cmd = "cv get %s 'Report Location:'" % instance
        location = self.run_cv_cmd(cmd)
        return location

    #To save to html
    def save_html(self, instance):
        cmd = "cv click %s 'Save HTML'" % instance
        self.run_cv_cmd(cmd)

    #close the test instance
    def close_instance(self, instance):
        cmd = "cv click %s 'Close'" % instance
        self.run_cv_cmd(cmd)

    #To cancel instance
    def cancel_instance(self, instance):
        cmd = "cv click %s 'Cancel'" % instance
        self.run_cv_cmd(cmd)

    #Get port listing
    def get_ports(self):
        response = self.json_get("/ports/")
        return response

    def show_text_blob(self, config_name, blob_test_name, brief):
        req_url = "/cli-json/show_text_blob"
        data = {"type": "Plugin-Settings"}
        if config_name and blob_test_name:
            data["name"] = "%s%s"%(blob_test_name, config_name)  # config name
        else:
            data["name"] = "ALL"
        if brief:
            data["brief"] = "brief"
        return self.json_post(req_url, data)

    def rm_text_blob(self, config_name, blob_test_name):
        req_url = "/cli-json/rm_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": str(blob_test_name + config_name),  # config name
        }
        rsp = self.json_post(req_url, data)


    def apply_cfg_options(self, cfg_options, enables, disables, raw_lines, raw_lines_file):

        # Read in calibration data and whatever else.
        if raw_lines_file != "":
            with open(raw_lines_file) as fp:
                line = fp.readline()
                while line:
                    cfg_options.append(line)
                    line = fp.readline()
            fp.close()

        for en in enables:
            cfg_options.append("%s: 1"%(en[0]))

        for en in disables:
            cfg_options.append("%s: 0"%(en[0]))

        for r in raw_lines:
            cfg_options.append(r[0])

    def build_cfg(self, config_name, blob_test, cfg_options):
        for value in cfg_options:
            self.create_test_config(config_name, blob_test, value)

        # Request GUI update its text blob listing.
        self.show_text_blob(config_name, blob_test, False)

        # Hack, not certain if the above show returns before the action has been completed
        # or not, so we sleep here until we have better idea how to query if GUI knows about
        # the text blob.
        time.sleep(5)

    def create_and_run_test(self, load_old_cfg, test_name, instance_name, config_name, sets,
                            pull_report, lf_host, lf_user, lf_password):
        load_old = "false"
        if load_old_cfg:
            load_old = "true"

        for i in range(60):
            response = self.create_test(test_name, instance_name, load_old)
            d1 = {k: v for e in response for (k, v) in e.items()}
            if d1["LAST"]["response"] == "OK":
                break
            else:
                time.sleep(1)

        self.load_test_config(config_name, instance_name)
        self.auto_save_report(instance_name)

        # Apply 'sets'
        for kv in sets:
            cmd = "cv set '%s' '%s' '%s'" % (instance_name, kv[0], kv[1])
            print("Running CV command: ", cmd)
            self.run_cv_cmd(cmd)

        response = self.start_test(instance_name)
        d1 = {k: v for e in response for (k, v) in e.items()}
        if d1["LAST"]["response"].__contains__("Could not find instance:"):
            print("ERROR:  start_test failed: ", d1["LAST"]["response"], "\n");
            # pprint(response)
            exit(1)

        while (True):
            cmd = "cv get_and_close_dialog"
            dialog = self.run_cv_cmd(cmd);
            if dialog[0]["LAST"]["response"] != "NO-DIALOG":
                print("Popup Dialog:\n")
                print(dialog[0]["LAST"]["response"])
            
            check = self.get_report_location(instance_name)
            location = json.dumps(check[0]["LAST"]["response"])
            if location != "\"Report Location:::\"":
                location = location.replace("Report Location:::", "")
                self.close_instance(instance_name)
                self.cancel_instance(instance_name)
                location = location.strip("\"")
                report = lf_rpt()
                print(location)
                try:
                    if pull_report:
                        report.pull_reports(hostname=lf_host, username=lf_user, password=lf_password,
                                            report_location=location)
                except:
                    raise Exception("Could not find Reports")
                break
            time.sleep(1)

