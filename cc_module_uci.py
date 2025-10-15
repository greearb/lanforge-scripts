# openwrt https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html
import logging
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

# from time import sleep
from contextlib import contextmanager
import json
import time

import scrapli
from scrapli.driver import GenericDriver, Driver

# from scrapli.response import Response

# from typing import Generator, Optional, Union


def get_jump_function(params: dict):
    def jump_through_vrf(conn: Driver):
        # ./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113

        # jump_cmd = f'./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.198'
        # jump_cmd = f'./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113'
        jump_cmd = f"./vrf_exec.bash {params['upstream_port']} ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa {params['auth_username']}@{params['host']}"

        # This happens after login completes
        conn.channel.send_input(jump_cmd, eager=True, strip_prompt=False)
        conn.channel._read_until_explicit_prompt(prompts=["password:"])
        conn.channel.send_inputs_interact(
            interact_events=[
                (params['auth_password'], "Password:", True)
            ],
            interaction_complete_patterns=[
                "#"
            ]
        )
        # At this point we should be logged into the dut and need to change the prompt pattern
        conn.comms_prompt_pattern = params['comms_prompt_pattern']

    return jump_through_vrf


def is_cac_done(result):
    good_things = "get_cac_state:0"
    if good_things in result:
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
                 band=None,
                 ap=None,
                 series=None,
                 scheme=None,
                 prompt=None,
                 ap_band_slot_24g=0,
                 ap_band_slot_5g=1,
                 ap_band_slot_6g=2,
                 ap_dual_band_slot_5g=2,
                 ap_dual_band_slot_6g=2,
                 port=22,
                 timeout=3,
                 pwd=None,
                 lfmgr=None,
                 lfuser=None,
                 lfpasswd=None,
                 upstream_port=None
                 ):

        if lfmgr is None:
            self.lfmgr = "127.0.0.1"
        else:
            self.lfmgr = lfmgr

        if lfuser is None:
            self.lfuser = "lanforge"
        else:
            self.lfuser = lfuser

        if lfpasswd is None:
            self.lfpasswd = "lanforge"
        else:
            self.lfpasswd = lfpasswd

        if upstream_port is None:
            print("upstream_port not set, exiting")
            exit(0)
        else:
            self.upstream_port = upstream_port

        self.dest = dest
        self.user = user
        self.passwd = passwd

        self.phy_24g = 'phy#1'
        self.radio_name_24g = "wifi1"  # phy#1"
        self.ap_name_24g = "ath16"

        self.phy_5g = 'phy#0'
        self.radio_name_5g = "wifi0"  # "phy#0"
        self.ap_name_5g = "ath04"

        self.radio_name_u5g = "phy#2"
        self.ap_name_u5g = "wifi5g"

        self.bandwidth = None
        self.tx_power = None
        self.channel = None

        self.band = band
        if band in ['5g', 'l5g']:
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

        self.mac = ""
        self.channel = ""
        self.tx_power = ""
        self.tx_power_dbm = ""
        self.channel_count = ""
        self.bandwidth = ""

    def __del__(self) -> None:
        self.tear_down_mgmt()

    def tear_down_mgmt(self) -> None:
        pass
        # if getattr(self, "conn", None) != None:
        #     self.conn.close()
        #     self.conn = None

    def parse_network_interfaces(self, text):
        # Initialize the main dictionary
        result = {}
        current_phy = None

        # Split the text into lines
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for phy section
            if line.startswith('phy#'):
                current_phy = line
                result[current_phy] = {}
            # Check for Interface section
            elif line.startswith('Interface'):
                current_interface = line.split()[1]
                if current_phy:
                    result[current_phy][current_interface] = {}
            # Parse key-value pairs
            elif current_phy and current_interface:
                # Handle special case for channel line
                if line.startswith('channel'):
                    parts = line.split(', ')
                    channel_info = {}
                    # Parse main channel info
                    channel_parts = parts[0].split()
                    channel_info['number'] = int(channel_parts[1])
                    channel_info['frequency'] = channel_parts[2].strip('()')

                    # Parse additional channel attributes
                    for part in parts[1:]:
                        key, value = part.split(': ', 1)
                        channel_info[key.strip()] = value.strip()

                    result[current_phy][current_interface]['channel'] = channel_info
                else:
                    # Handle other key-value pairs
                    if ' ' in line:
                        key, value = line.split(' ', 1)
                        result[current_phy][current_interface][key] = value.strip()
            print(json.dumps(result, indent=2))
        return result

    def get_config_summary(self):

        config_summary = self._show_ap_dot11_summary()
        if '2g' in self.band or '24g' in self.band:
            self.mac = config_summary[self.phy_24g][self.ap_name_24g]['addr']
            self.channel = config_summary[self.phy_24g][self.ap_name_24g]['channel']['number']
            self.tx_power = config_summary[self.phy_24g][self.ap_name_24g]['txpower'].split('.')[0]
            self.tx_power_dbm = self.tx_power
            self.channel_count = config_summary[self.phy_24g][self.ap_name_24g]['ifindex']
            self.bandwidth = config_summary[self.phy_24g][self.ap_name_24g]['channel']['width']
            # ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary()[self.phy_24g][self.ap_name_24g]['txpower']
        elif '5g' in self.band:
            # ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary()[self.phy_5g][self.ap_name_5g]['txpower']
            self.mac = config_summary[self.phy_5g][self.ap_name_5g]['addr']
            self.channel = config_summary[self.phy_5g][self.ap_name_5g]['channel']['number']
            self.tx_power = config_summary[self.phy_5g][self.ap_name_5g]['txpower'].split('.')[0]
            self.tx_power_dbm = self.tx_power
            self.channel_count = config_summary[self.phy_5g][self.ap_name_5g]['ifindex']
            self.bandwidth = config_summary[self.phy_5g][self.ap_name_5g]['channel']['width']

    def show_ap_summary(self):
        pass

    def console_setup(self):
        pass

    def read_ap_config_radio_role(self):
        pass

    def read_country_code_and_regulatory_domain(self):
        # need to have the
        command = f"uci get wireless.{self.radio_name_5g}.country"
        r = self.send_ap_command(command)

        self.regulatory_domain = r.result
        self.country_code = r.result

    def wlan_shutdown(self):
        pass

    def show_wlan_summary(self):
        return " "

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

    def _config_dot11_tx_power(self, radio: str, ap: str, wait_for_done: bool):
        if self.tx_power is None:
            raise Exception("Missing tx-power")
        #     def send_ap_command(self, command: "str", action: "str", radio: "str",  attribute:"str", value: "str") :
        command = f"uci set wireless.{radio}.txpower={self.tx_power}"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)

        command = "wifi"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)

        command = f"uci get wireless.{radio}.txpower"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"txpower setting: {r.result}")

    def config_dot11_5ghz_tx_power(self, wait_for_done=True):
        self._config_dot11_tx_power(self.radio_name_5g, self.ap_name_5g, wait_for_done)

    def config_dot11_24ghz_tx_power(self, wait_for_done=True):
        self._config_dot11_tx_power(self.radio_name_24g, self.ap_name_24g, wait_for_done)

    # TODO
    def get_ap_tx_power_config(self):
        # TODO need to separate out the 2g and 5g power
        if '2g' in self.band:
            ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary()[self.phy_24g][self.ap_name_24g]['txpower']
        elif '5g' in self.band:
            ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary()[self.phy_5g][self.ap_name_5g]['txpower']
            # self._show_ap_dot11_summary()['phy#0']['ath04']['txpower']

        ap_tx_power_dbm = ap_tx_power_dbm.split('.')[0]
        # self.ap_tx_power_dbm = self.ap_current_tx_power_level = self._show_ap_dot11_summary()
        self.ap_tx_power_dbm = self.ap_current_tx_power_level = ap_tx_power_dbm

    def _config_dot11_channel(self, radio: str, ap: str):
        if self.channel is None:
            raise Exception("Missing channel")

        # Channel:
        command = f"uci set wireless.{radio}.channel={self.channel}"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)

        command = "wifi"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)

        command = f"uci get wireless.{radio}.channel"
        r = self.send_ap_command(command)
        if r.failed:
            raise Exception(r.result)

        print(f"Channel set {r.result}")

        # need to wait for cac to be done
        for _ in range(120):
            r = self.get_cac_state()
            if is_cac_done(r.result):
                return
            time.sleep(1)
        else:
            raise Exception("CAC is not okay")

    def config_dot11_5ghz_channel(self):
        self._config_dot11_channel(self.radio_name_5g, self.ap_name_5g)

    def config_dot11_24ghz_channel(self):
        self._config_dot11_channel(self.radio_name_24g, self.ap_name_24g)

    def _config_dot11_channel_width(self, radio: str, ap: str):
        pass

    def config_dot11_5ghz_channel_width(self):
        self._config_dot11_channel_width(self.radio_name_5g, self.ap_name_5g)

    def config_dot11_24ghz_channel_width(self):
        self._config_dot11_channel_width(self.radio_name_24g, self.ap_name_24g)

    def _show_ap_dot11_summary(self) -> "dict[str]":
        command = "iw dev"
        r = self.send_ap_command(command)

        if r.failed:
            logging.info("radio not configured, Skipping summery")
            return

        results = self.parse_network_interfaces(r.result)

        return results

    def get_cac_state(self) -> "dict[str]":
        command = "cfg80211tool ath04 get_cac_state"
        results = self.send_ap_command(command)

        if results.failed:
            logging.info("error checking cac timer")
            return

        return results

    def show_ap_dot11_5gz_summary(self) -> str:
        return self._show_ap_dot11_summary()

    def show_ap_dot11_24gz_summary(self) -> str:
        return self._show_ap_dot11_summary()

    def show_ap_bssid_5ghz(self) -> str:
        # result = self._show_ap_dot11_summary()
        # bssid = result['phy#1']['ath16']['addr']
        return self._show_ap_dot11_summary()['phy#1'][self.ap_name_5g]['addr']

    def show_ap_bssid_24ghz(self) -> str:
        return self._show_ap_dot11_summary()['phy#0'][self.ap_name_24g]['addr']

    @contextmanager
    def get_mgmt(self) -> "Generator[GenericDriver]":  # noqa:
        if getattr(self, "conn", None) == None:  # noqa:
            #  ./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113
            # Jump Host config
            c = {
                # "host":'192.168.215.198',  # noqa:
                "host": self.dest,  # noqa:
                "auth_username":self.user,  # noqa:
                "auth_password":self.passwd,  # noqa:
                "ssh_config_file": True,
                "comms_prompt_pattern":"^root@HFCL:~\\#", # noqa: 231
                "timeout_ops": 120,
                "timeout_transport": 240,
                "upstream_port": self.upstream_port
            }

            # if not getattr(self, "jump_host", None) == None:
            jump_function = get_jump_function(c)
            # LANforge config
            c = {
                # "host": '192.168.212.55',
                "host": self.lfmgr,
                "auth_username": self.lfuser,
                "auth_password": self.lfpasswd,
                "auth_strict_key": False,
                "comms_prompt_pattern": "^[\\S\\7\\x1b]*\\[.*\\]\\$",
                "on_open": jump_function,  # on logging into LANforge will run the jump_function
                "timeout_ops": 40,
                "timeout_transport": 40,
                "ssh_config_file": True,
            }

            self.conn = GenericDriver(**c)
            try:
                self.conn.open()
            except scrapli.exceptions.ScrapliAuthenticationFailed as e:
                raise Exception(
                    f"Failed to open connection to {self.dest} ({e})")
        yield self.conn

    def send_ap_command(self, command: "str"):

        print(f"command sent: {command}")
        with self.get_mgmt() as console:

            r = console.send_command(command, failed_when_contains=["ERROR: .*"])

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
