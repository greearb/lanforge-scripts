#!/usr/bin/env python3
# ---- ---- ---- ---- LANforge Base Imports ---- ---- ---- ----
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.lfcli_base import LFCliBase
import datetime
import time

class chamberview(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)

    #behaves same as chamberview manage scenario
    def manage_cv_scenario(self, scenario_name="scenario-python", profile="STA-AC", amount="1", dutname="ASUS", dutradio="Radio-1", traffic="http", uses="wiphy0"):
        req_url = "/cli-json/add_text_blob"

        text_blob = "profile_link 1.1" + " " + profile + " " + amount + " " + "\'DUT:" + " " + dutname + " " + dutradio\
                    + "\' " + traffic + " " + uses + ",AUTO -1"

        print(text_blob)
        data = {
            "type": "Network-Connectivity",
            "name": scenario_name,
            "text": text_blob
        }
        print(data)
        rsp = self.json_post(req_url, data)
        time.sleep(2)


    def show_changes(self,scenario_name):
        req_url = "/cli-json/show_text_blob"

        data = {
            "type": "ALL",
            "name": "ALL",
            "brief": "brief"
        }

        rsp = self.json_post(req_url, data)
        print(rsp)
        print("scenario is pushed")

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


