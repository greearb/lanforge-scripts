import time

# !/usr/bin/env python3
# ---- ---- ---- ---- LANforge Base Imports ---- ---- ---- ----
from LANforge.lfcli_base import LFCliBase


class cv_dut(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 sw_version="NA",
                 hw_version="NA",
                 serial_num="NA",
                 model_num="NA",
                 ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)
        self.cv_dut_name = "DUT"
        self.flags = "4098"
        self.sw_version = sw_version
        self.hw_version = hw_version
        self.model_num = model_num
        self.serial_num = serial_num
        self.serial_port = "[BLANK]"
        self.wan_port = "[BLANK]"
        self.lan_port = "[BLANK]"
        self.api_id = "0"
        self.flags_mask = "NA"

    def create_dut(self,
                   ssid1="[BLANK]",
                   pass1="[BLANK]",
                   ssid2="[BLANK]",
                   pass2="[BLANK]",
                   ssid3="[BLANK]",
                   pass3="[BLANK]",
                   bssid1="00:00:00:00:00:00",
                   bssid2="00:00:00:00:00:00",
                   bssid3="00:00:00:00:00:00",
                   mgt_ip="0.0.0.0",
                   eap_id="[BLANK]",
                   top_left_x="NA",
                   top_left_y="NA",
                   ):
        response_json = []
        req_url = "/cli-json/add_dut"
        data = {
            "name": self.cv_dut_name,
            "flags": self.flags,
            "img_file": "NONE",
            "sw_version": self.sw_version,
            "hw_version": self.hw_version,
            "model_num": self.model_num,
            "serial_num": self.serial_num,
            "serial_port": self.serial_port,
            "wan_port": self.wan_port,
            "lan_port": self.lan_port,
            "ssid1": ssid1,
            "passwd1": pass1,
            "ssid2": ssid2,
            "passwd2": pass2,
            "ssid3": ssid3,
            "passwd3": pass3,
            "mgt_ip": mgt_ip,
            "api_id": self.api_id,
            "flags_mask": self.flags_mask,
            "antenna_count1": "0",
            "antenna_count2": "0",
            "antenna_count3": "0",
            "bssid1": bssid1,
            "bssid2": bssid2,
            "bssid3": bssid3,
            "top_left_x": top_left_x,
            "top_left_y": top_left_y,
            "eap_id": eap_id,
        }
        rsp = self.json_post(req_url, data, debug_=False, response_json_list_=response_json)
        return rsp

    def add_ssid(self,
                 dut_name="DUT",
                 ssid_idx=0,
                 ssid='[BLANK]',
                 passwd='[BLANK]',
                 bssid='00:00:00:00:00:00',
                 ssid_flags=0,
                 ssid_flags_mask=0xFFFFFFFF):
        req_url = "/cli-json/add_dut_ssid"
        print("name:" + dut_name,
              "ssid_idx:" + ssid_idx,
              "ssid:" + ssid,
              "passwd:" + passwd,
              "bssid:" + bssid,
              "ssid_flags:" + str(ssid_flags),
              "ssid_flags_mask:" + str(ssid_flags_mask))

        self.json_post(req_url, {
            "name": dut_name,
            "ssid_idx": ssid_idx,
            "ssid": ssid,
            "passwd": passwd,
            "bssid": bssid,
            "ssid_flags": ssid_flags,
            "ssid_flags_mask": ssid_flags_mask,
        })
