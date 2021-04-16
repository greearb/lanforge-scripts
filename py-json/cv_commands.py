"""
Note: This is a library file used to create a chamber view scenario.
    import this file as showed in create_chamberview.py to create a scenario
"""

import time

# !/usr/bin/env python3
# ---- ---- ---- ---- LANforge Base Imports ---- ---- ---- ----
from LANforge.lfcli_base import LFCliBase


class chamberview(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)

    #behaves same as chamberview manage scenario
    def manage_cv_scenario(self,
                            scenario_name="Automation",
                            Resources="1.1",
                            Profile="STA-AC",
                            Amount="1",
                            DUT="DUT",
                            Dut_Radio="Radio-1" ,
                            Uses1="wiphy0",
                            Uses2="AUTO",
                            Traffic="http",
                            Freq="-1",
                            VLAN=""):
        req_url = "/cli-json/add_text_blob"

        text_blob = "profile_link" + " " + Resources + " " + Profile + " " + Amount + " " + "\'DUT:" + " " + DUT\
                    + " " + Dut_Radio + "\' " + Traffic + " " + Uses1 + ","+Uses2 + " " + Freq + " " + VLAN

        print(text_blob)
        data = {
            "type": "Network-Connectivity",
            "name": scenario_name,
            "text": text_blob
        }

        rsp = self.json_post(req_url, data)
        time.sleep(2)


    def pass_raw_lines_to_cv(self,
                            scenario_name="Automation",
                            Rawline=""):
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Network-Connectivity",
            "name": scenario_name,
            "text": Rawline
        }
        print("data: ",data)
        rsp = self.json_post(req_url, data)
        time.sleep(2)

    def show_text_blob(self, config_name, blob_test_name, brief):
        req_url = "/cli-json/show_text_blob"
        data = {"type": "Plugin-Settings"}
        if config_name and blob_test_name:
            data["name"] = "%s%s" % (blob_test_name, config_name)  # config name
        else:
            data["name"] = "ALL"
        if brief:
            data["brief"] = "brief"
        return self.json_post(req_url, data)

    #This is for chamber view buttons
    def apply_cv_scenario(self, cv_scenario):
        cmd = "cv apply '%s'" % cv_scenario  #To apply scenario
        self.run_cv_cmd(cmd)
        print("Apply scenario")

    def build_cv_scenario(self):#build chamber view scenario
        cmd = "cv build"
        self.run_cv_cmd(cmd)
        print("Build scenario")

    def is_cv_build(self):#check if scenario is build
        cmd = "cv is_build"
        self.run_cv_cmd(cmd)

    def sync_cv(self):#sync
        cmd = "cv sync"
        self.run_cv_cmd(cmd)

    def run_cv_cmd(self, command):#Send chamber view commands
        req_url = "/gui-json/cmd"
        data = {
            "cmd": command
        }
        rsp = self.json_post(req_url, data)
        print(rsp)


