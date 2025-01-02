#!/usr/bin/env python3
# flake8: noqa
import logging
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

from time import sleep
from contextlib import contextmanager
import json

import scrapli
from scrapli.driver import GenericDriver, Driver
from scrapli.response import Response

from typing import Generator, Optional, Union

def get_jump_function(params:dict):
    def jump_through_vrf(conn: Driver):
        jump_cmd = f'sudo /home/lanforge/vrf_exec.bash eth1 "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {params["auth_username"]}@{params["host"]}"'

        # This happens after login completes
        conn.channel.send_input(jump_cmd,eager=True,strip_prompt=False)
        conn.channel._read_until_explicit_prompt(prompts=["Password:"])
        conn.channel.send_inputs_interact(
            interact_events=[
                (params['auth_password'],"Password:", True)
            ],
            interaction_complete_patterns=[
                "#"
            ]
        )
        # At this point we should be logged into the dut and need to change the prompt pattern
        conn.comms_prompt_pattern = params['comms_prompt_pattern']

    return jump_through_vrf

def is_cac_done(channel, list):
    good_things = ['{"state": "cac_completed"}', '{"state":"allowed"}']
    for status in list:
        if status[0] == channel and status[1] in good_things:
            return True
    else:
        return False
    
def is_channel_allowed(channel, list):
    for _channel in list:
        if int(_channel) == channel:
            return True
    else:
        return False 

class create_controller_series_object:
    def __init__(self,
                 dest,
                 user,
                 passwd,
                 band = None,
                 ap = None,
                 series = None,
                 scheme = None,
                 prompt = None,
                 ap_band_slot_24g=0,
                 ap_band_slot_5g=1,
                 ap_band_slot_6g=2,
                 ap_dual_band_slot_5g=2,
                 ap_dual_band_slot_6g=2,
                 port=22,
                 timeout=3,
                 pwd=None
                 ):
        
        self.dest = dest
        self.user = user
        self.passwd = passwd
        
        
        self.radio_name_24g = "phy0"
        self.ap_name_24g = "wifi2g"

        self.radio_name_5g = "phy1"
        self.ap_name_5g = "wifi5g"

        self.radio_name_u5g = "phy2"
        self.ap_name_u5g = "wifi5g"

        self.bandwidth = None
        self.tx_power = None
        self.channel = None

        self.band = band
        if band in ['5g','l5g']:
            self.radio_name_5g = self.radio_name_5g
            self.ap_name = self.ap_name_5g
        elif band in ['u5g']:
            self.radio_name_5g = self.radio_name_u5g
            self.ap_name = self.ap_name_u5g
        elif band in ['24g']:
            self.radio_name = self.radio_name_24g
            self.ap_name = self.ap_name_24g
        else:
            raise Exception("Missing band type")

        self.info = "Adtran PlumeOS Device"

        self.ap_config_radio_role = "Manual"
        self.ap_num_power_levels = 1

    def __del__(self) -> None:
        self.tear_down_mgmt()

    def tear_down_mgmt(self) -> None:
        if getattr(self, "conn", None) != None:
            self.conn.close()
            self.conn = None

    def show_ap_summary(self):
        pass

    def console_setup(self):
        pass

    def read_ap_config_radio_role(self):
        pass

    def read_country_code_and_regulatory_domain(self):
        r = self._show_ap_dot11_summary(self.radio_name, self.ap_name)
        self.regulatory_domain = r["country"]
        self.country_code =r["country"]

    def wlan_shutdown(self):
        pass

    def show_wlan_summary(self):
        pass

    def config_enable_wlan_send_no_shutdown(self):
        pass

    def config_no_ap_dot11_5ghz_shutdown(self):
        pass

    def config_ap_no_dot11_5ghz_shutdown(self):
        pass

    def config_no_ap_dot11_24ghz_shutdown(self):
        pass

    def config_ap_no_dot11_24ghz_shutdown(self):
        pass

    def ap_name_shutdown(self):
        pass

    def ap_name_no_shutdown(self):
        pass

    def show_ap_dot11_5gz_shutdown(self):
        pass

    def show_ap_dot11_24gz_shutdown(self):
        pass

    def ap_dot11_5ghz_radio_role_manual_client_serving(self):
        pass

    def ap_dot11_24ghz_radio_role_manual_client_serving(self):
        pass

    def ap_dot11_5ghz_shutdown(self):
        pass

    def ap_dot11_24ghz_shutdown(self):
        pass

    def _config_dot11_tx_power(self, radio:str, ap:str, wait_for_done:bool):
        if self.tx_power == None:
            raise Exception("Missing tx-power")

        r = self.ovsh("update","Wifi_Radio_Config",f"tx_power:={self.tx_power}", f"if_name=={radio}")
        # sleep(10)
        if r.failed:
            raise Exception(r.result)

    def config_dot11_5ghz_tx_power(self, wait_for_done=True):
        self._config_dot11_tx_power(self.radio_name_5g, self.ap_name_5g, wait_for_done)

    def config_dot11_24ghz_tx_power(self, wait_for_done=True):
        self._config_dot11_tx_power(self.radio_name_24g, self.ap_name_24g, wait_for_done)

    def get_ap_tx_power_config(self):
        self.ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary(self.radio_name, self.ap_name)["tx_power"]

    def _config_dot11_channel(self, radio:str, ap:str):
        if self.channel == None:
            raise Exception("Missing channel")
        r = self._show_ap_dot11_summary(radio,ap)
        if is_channel_allowed(int(self.channel), r["allowed_channels"][1]) == False:
            raise Exception("Channel not allowed")

        # Channel:
        r = self.ovsh("update", "Wifi_Radio_Config", f"channel:={self.channel}", f"if_name=={radio}")
        if r.failed:
            raise Exception(r.result)

        for _ in range(120):
            r = self._show_ap_dot11_summary(radio,ap)
            if is_cac_done(self.channel, r["channels"][1]) == True:
                return
            sleep(1)
        else:
            raise Exception("CAC is not okay")


    def config_dot11_5ghz_channel(self):
        self._config_dot11_channel(self.radio_name_5g, self.ap_name_5g)

    def config_dot11_24ghz_channel(self):
        self._config_dot11_channel(self.radio_name_24g, self.ap_name_24g)

    def _config_dot11_channel_width(self, radio:str, ap:str):
        if self.bandwidth == None:
            raise Exception("Missing bandwidth")

        r = self.ovsh("update", "Wifi_Radio_Config", f"ht_mode:={self.bandwidth}", f"if_name=={radio}")
        if r.failed:
            raise Exception(r.result)

    def config_dot11_5ghz_channel_width(self):
        self._config_dot11_channel_width(self.radio_name_5g, self.ap_name_5g)

    def config_dot11_24ghz_channel_width(self):
        self._config_dot11_channel_width(self.radio_name_24g, self.ap_name_24g)

    def _show_ap_dot11_summary(self, radio:"str", ap:"str") -> "dict[str]":
        for _ in range(300):
            r = self.ovsh("select", "Wifi_Radio_State", where=f"if_name=={radio}")
            if isinstance(r.result[0]["tx_power"], int):
                break
            print(r.result[0]["tx_power"])
            sleep(.5)
        else:
            raise Exception("TX power isn't an INT")

        if r.failed:
            logging.info(f"{radio} radio not configured, Skipping summery")
            return
        
        return r.result[0]


    def show_ap_dot11_5gz_summary(self) -> str:
        return self._show_ap_dot11_summary(self.radio_name_5g, self.ap_name_5g)

    def show_ap_dot11_24gz_summary(self) -> str:
        return self._show_ap_dot11_summary(self.radio_name_24g, self.ap_name_24g)

    def show_ap_bssid_5ghz(self) -> str:
        return self._show_ap_dot11_summary(self.radio_name_5g, self.ap_name_5g)["mac"]

    def show_ap_bssid_24ghz(self) -> str:
        return self._show_ap_dot11_summary(self.radio_name_24g, self.ap_name_24g)["mac"]

    @contextmanager
    def get_mgmt(self) -> "Generator[GenericDriver]":
        if getattr(self, "conn", None) == None:
            c = {
                "host":self.dest,
                "auth_username":self.user,
                "auth_password":self.passwd,
                "ssh_config_file": True,
                "comms_prompt_pattern":"^\S+\s\S+\s[#>$]\s*$",
                "timeout_ops": 120,
                "timeout_transport": 240
            }

            if not getattr(self, "jump_host", None) == None:
                    jump_function = get_jump_function(c)
                    c = {
                        "host": self.jump_host["host"],
                        "auth_username": self.jump_host["auth_username"],
                        "auth_password": self.jump_host["auth_password"],
                        "auth_strict_key": False,
                        "comms_prompt_pattern": r"^[\S\7\x1b]*\[.*\]\$",
                        "on_open": jump_function,
                    }

            self.conn = GenericDriver(**c)
            try:
                self.conn.open()
            except scrapli.exceptions.ScrapliAuthenticationFailed as e:
                raise Exception(
                    f"Failed to open connection to {self.dest} ({e.message})"
                ) from e
        yield self.conn

    def ovsh(self, command:"str", table:"str", value:"Union[str,list[str]]"=None, where:"Optional[Union[str,list[str]]]"=None) -> "Response":
        if value == None:
            value_clause = ""
        elif isinstance(value, list):
            value_clause = " ".join(value)
        else:
            value_clause = value

        if where == None:
            where_clause = ""
        elif isinstance(where, list):
            where_clause = " ".join([f"-w {w}" for w in where])
        else:
            where_clause = f"-w {where}"

        with self.get_mgmt() as console: 
            r = console.send_command(f"ovsh --json {command} {table} {value_clause} {where_clause}", failed_when_contains=["ERROR: .*"])

            if command in ["update"] and not r.failed:
                console.send_command(f"osvsh wait {table} {value_clause} {where_clause} --timeout=500", failed_when_contains=["ERROR: .*"])

        if not r.failed:
            r.result = json.loads(r.result)
        return r
       

    def no_logging_console(self):
        pass

    def line_console_0(self):
        pass

    def summary(self):
        pass

    def disable_operation_status(self):
        pass

    def noop(self):
        return "\n\n"
