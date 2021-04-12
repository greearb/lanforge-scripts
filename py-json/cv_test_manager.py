"""
Note: This script is working as library for chamberview tests.
    It holds different commands to automate test.
"""

import time

from LANforge.lfcli_base import LFCliBase


class cv_test(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)

    #To create a test config
    def create_test_config(self, config_name, blob_test_name, text):
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": str(blob_test_name + config_name),
            "text": text
        }

        print("adding- " + text + " " + "to test config")
        rsp = self.json_post(req_url, data)
        time.sleep(1)

    #create a test
    def create_test(self, test_name, instance):
        cmd = "cv create '{0}' '{1}'".format(test_name, instance)
        self.run_cv_cmd(str(cmd))

    #load test scenario
    def load_test_scenario(self, instance, scenario):
        cmd = "cv load '{0}' '{1}'".format(instance, scenario)
        self.run_cv_cmd(cmd)

    #load test config
    def load_test_config(self, test_config, instance):
        cmd = "cv load '{0}' '{1}'".format(instance, test_config)
        self.run_cv_cmd(cmd)

    #start the test
    def start_test(self, instance):
        cmd = "cv click '%s' Start" % instance
        self.run_cv_cmd(cmd)

    #close test
    def close_test(self, instance):
        cmd = "cv click '%s' 'Close'" % instance
        self.run_cv_cmd(cmd)

    #Cancel
    def cancel_test(self, instance):
        cmd = "cv click '%s' Cancel" % instance
        self.run_cv_cmd(cmd)

    # Send chamber view commands
    def run_cv_cmd(self, command):
        print(command)
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
        print(cmd)
        self.run_cv_cmd(cmd)

    #To cancel instance
    def cancel_instance(self, instance):
        cmd = "cv click %s 'Cancel'" % instance
        print(cmd)
        self.run_cv_cmd(cmd)

    #Check total ports
    def check_ports(self):
        response = self.json_get("/ports/")
        return response

    def show_changes(self, config_name):
        req_url = "/cli-json/show_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": config_name,  # config name
            "brief": "brief"
        }
        rsp = self.json_post(req_url, data)
        print(rsp)
