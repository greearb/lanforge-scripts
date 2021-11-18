#!/usr/bin/env python3
import sys
import os
import importlib
import time

 
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFRequest = importlib.import_module("py-json.LANforge.LFRequest")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")


class ATTENUATORProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_)
        self.lfclient_host = lfclient_host
        self.COMMANDS = ["show_attenuators", "set_attenuator"]
        self.atten_serno = None
        self.atten_idx = None
        self.atten_val = None
        self.atten_data = {
            "shelf": 1,
            "resource": 1,
            "serno": self.atten_serno,
            "atten_idx": self.atten_idx,
            "val": self.atten_val,
            "mode": None,
            "pulse_width_us5": None,
            "pulse_interval_ms": None,
            "pulse_count": None,
            "pulse_time_ms": None
        }
        self.debug = debug_

    def set_command_param(self, command_name, param_name, param_value):
        # we have to check what the param name is
        if not command_name:
            raise ValueError("Command Name is required")
        if not param_name:
            raise ValueError("Paramater is required")
        if command_name not in self.COMMANDS:
            raise ValueError("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
        if command_name == "set_attenuator":
            self.atten_data[param_name] = param_value

    def show(self):
        print("Show Attenuators.........")
        response = self.json_get("/attenuators/")
        time.sleep(0.01)
        if response is None:
            print(response)
            raise ValueError("Cannot find any endpoints")
        elif 'attenuator' or 'attenuators' in response.keys():
            try:
                attenuator_resp = response["attenuators"]
            except KeyError:
                attenuator_resp = [response["attenuator"]]
            for attenuator in attenuator_resp:
                for key, val in attenuator.items():
                    if key == "entity id":
                        serial_num = val.split(".")
                        print("Serial-num : %s" % serial_num[-1])
                    print("%s : %s" % (key, val))
                    print('\n')

        else:
            raise ValueError('No attenuators in response')

    def create(self):
        if int(self.atten_val) > 955:
            raise ValueError("Attenuation ddB value must be 955 or less")
        if int(self.atten_idx) > 7:
            raise ValueError("Attenuation ddB value must be 7 or less")
        print("Setting Attenuator...")
        self.set_command_param("set_attenuator", "serno", self.atten_serno)
        self.set_command_param("set_attenuator", "atten_idx", self.atten_idx)
        self.set_command_param("set_attenuator", "val", self.atten_val)
        set_attenuators = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_attenuator", debug_=self.debug)
        set_attenuators.addPostData(self.atten_data)
        time.sleep(0.01)
        set_attenuators.jsonPost(self.debug)
        time.sleep(10)
        print("\n")
