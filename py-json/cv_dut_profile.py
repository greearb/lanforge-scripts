
import time

# !/usr/bin/env python3
# ---- ---- ---- ---- LANforge Base Imports ---- ---- ---- ----
from LANforge.lfcli_base import LFCliBase

class cv_dut(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 ):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port)

    def create_dut(self,
                   dut_name="DUT",
                   flags="4098",
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
                   eap_id="[BLANK]"):
        response_json = []
        req_url = "/cli-json/add_dut"
        data = {
            "name": dut_name,
            "flags": flags,
            "img_file": "NONE",
            "sw_version": "[BLANK]",
            "hw_version": "[BLANK]",
            "model_num": "[BLANK]",
            "serial_num": "[BLANK]",
            "serial_port": "[BLANK]",
            "wan_port": "[BLANK]",
            "lan_port": "[BLANK]",
            "ssid1": ssid1,
            "passwd1": pass1,
            "ssid2": ssid2,
            "passwd2": pass2,
            "ssid3": ssid3,
            "passwd3": pass3,
            "mgt_ip": mgt_ip,
            "api_id": "0",
            "flags_mask": "NA",
            "antenna_count1": "0",
            "antenna_count2": "0",
            "antenna_count3": "0",
            "bssid1": bssid1,
            "bssid2": bssid2,
            "bssid3": bssid3,
            "top_left_x": "0",
            "top_left_y": "0",
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
        print( "name:" + dut_name,
            "ssid_idx:"+ ssid_idx,
            "ssid:"+ ssid,
            "passwd:" + passwd,
            "bssid:" + bssid,
            "ssid_flags:" + str(ssid_flags),
            "ssid_flags_mask:"+ str(ssid_flags_mask))

        self.json_post(req_url, {
            "name": dut_name,
            "ssid_idx": ssid_idx,
            "ssid": ssid,
            "passwd": passwd,
            "bssid": bssid,
            "ssid_flags": ssid_flags,
            "ssid_flags_mask": ssid_flags_mask,
        })
