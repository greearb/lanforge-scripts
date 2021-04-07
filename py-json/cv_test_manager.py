from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.lfcli_base import LFCliBase
import datetime
import time
import json

from chamberview import chamberview as cv


class cv_test(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)

    def create_test_config(self,config_name,text):
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": "Wifi-Capacity-"+config_name,
            "text": text
        }
        print(data)
        rsp = self.json_post(req_url, data)
        time.sleep(1)

    def create_test(self, test_name, instance):
        cmd = "cv create '{0}' '{1}'".format(test_name, instance)
        self.run_cv_cmd(cmd)

    def load_test_scenario(self, instance, scenario):
        cmd = "cv load '{0}' '{1}'".format(instance, scenario)
        print("cmd: ",cmd)
        self.run_cv_cmd(cmd)

    def load_test_config(self, test_config, instance):
        cmd = "cv load '{0}' '{1}'".format(instance, test_config)
        print("cmd: ", cmd)
        self.run_cv_cmd(cmd)

    def start_test(self, instance):
        cmd = "cv click '%s' Start" % instance
        print("cmd: ",cmd)
        self.run_cv_cmd(cmd)

    def close_test(self, instance):
        cmd = "cv click '%s' 'Close'" % instance
        print(cmd)
        self.run_cv_cmd(cmd)

    def cancel_test(self, instance):
        cmd = "cv click '%s' Cancel" % instance
        print(cmd)
        self.run_cv_cmd(cmd)

    def run_cv_cmd(self, command):  # Send chamber view commands
        print(command)
        req_url = "/gui-json/cmd"
        data = {
            "cmd": command
        }
        rsp = self.json_post(req_url, data)
        print(rsp)
        print(data)

    def check_ports(self):
        response=self.json_get("/ports/")
        return response

    def show_changes(self,config_name):
        req_url = "/cli-json/show_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": "Wifi-Capacity-"+config_name,
            "brief": "brief"
        }
        rsp = self.json_post(req_url, data)