#!/usr/bin/env python3

# from contextlib import contextmanager

import os
import sys
import importlib
import argparse
# import logging
import time
from pprint import pformat


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession                      # noqa E402
from lanforge_client.lanforge_api import LFJsonCommand                  # noqa E402
from lanforge_client.lanforge_api import LFJsonQuery                    # noqa E402
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

# cli commands used
# add_sta 1 1 wiphy3 sta60105 33686528 ax1800_5g NA NA DEFAULT NA xx:xx:xx:*:*:xx 15
# set_wifi_extra 1 1 sta60105 WPA-PSK DEFAULT DEFAULT lf_ax1800_5g NA NA DEFAULT
# set_port 1 1 sta60105 NA NA NA NA 2147483648 NA NA NA NA 16384


class lf_create_client():
    def __init__(self,
                 **kwargs
                 ):
        if "lf_mgr" in kwargs:
            self.lf_mgr = kwargs["lf_mgr"]

        if "lf_mgr_port" in kwargs:
            self.lf_mgr_port = kwargs["lf_mgr_port"]

        if "lf_user" in kwargs:
            self.lf_user = kwargs["lf_user"]

        if "lf_passwd" in kwargs:
            self.lf_passwd = kwargs["lf_passwd"]

        self.session = None
        self.debug = True

        if not self.session:
            self.session = LFSession(lfclient_url=f"http://{self.lf_mgr}:{self.lf_mgr_port}",
                                     debug=self.debug,
                                     connection_timeout_sec=4.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    def create_client(self, admin_up=False):
        sta_flags = 0

        station_name = "sta60101"  # TODO: check exising stations and add up
        security = 'wpa2'
        # bssid = kwargs.get('bssid', 'DEFAULT')
        # bssid = '[BLANK]'
        data = {
            "radio": 'wiphy3',
            "resource": 1,
            "shelf": 1,
            "sta_name": station_name,
            "mode": 0,
            # "mac": None, # if mac is not provided in yaml, it will take the default value
            "mac": 'xx:xx:xx:*:*:xx',  # if mac is not provided in yaml, it will take the default value
            "ssid": "ax88u_5g",
            "ap": "[BLANK]",  # bssid, #if bssid is not provided in yaml, it will take the default value
            # "key": "lf_ax1800_5g",
            "debug": True,
            "flags": 0
        }
        self.AddStaFlags: LFJsonCommand.AddStaFlags = self.command.AddStaFlags
        if 'wpa3' in security:
            data['ieee80211w'] = 2  # mfp required
            if security.endswith('sae'):
                sta_flags += self.AddStaFlags.use_wpa3.value  # add_sta_flags['use-wpa3']
            if security.endswith('owe'):  # wifi7
                sta_flags += self.AddStaFlags.use_owe.value  # add_sta_flags['use-owe']
            if security.endswith('enterprise'):
                sta_flags += self.AddStaFlags.use_wpa3.value  # add_sta_flags['use-wpa3']
        # for testing
        if 'wpa2' in security:
            data['ieee80211w'] = 1  # mfp optional
            sta_flags += self.AddStaFlags.wpa2_enable.value  # add_sta_flags['wpa2_enable']
            sta_flags += self.AddStaFlags.p_80211u_enable.value
            sta_flags += self.AddStaFlags.p_8021x_radius.value

        if 'enterprise' in security:
            sta_flags += self.AddStaFlags.p_8021x_radius.value

        # disable auto roam
        sta_flags += self.AddStaFlags.disable_roam.value  # no auto ess roaming
        sta_flags += self.AddStaFlags.disable_mlo.value  # for roaming to work

        data['flags'] = sta_flags

        # mfp = kwargs.get('11w', 'optional')
        mfp = 'optional'
        if mfp == 'optional':  # PMF
            data['ieee80211w'] = 1
        elif mfp == 'disabled':
            data['ieee80211w'] = 0

        print(pformat(data))
        # TODO:
        #     "flags_mask": kwargs.get('sta_flags'),
        response = []
        result = self.command.post_add_sta(response_json_list=response, **data)
        print(pformat(result))

        # port_name = '1.1.{}'.format(station_name)
        # wait for port created
        time.sleep(1)
        # if not self.check_port_ready(port_name):
        #     raise ValueError(f"port {port_name} not created")
        # print('port {} ready'.format(port_name))

        # check bssid if provided
        # if bssid and bssid != 'DEFAULT':
        #    response = Response(interval=5, max_delay=120)
        #    response.wait(expected_result=True,
        #                  exit_on_results=[],
        #                  funct=self.check_bssid_exists,
        #                  port_name=station_name,
        #                  bssid=bssid)
        #    if response.test['result'] == 'Failed':
        #        m_RaiseError("Candela is not seeing BSSID {}".format(kwargs.get('bssid')), True)

        if 'wpa2' in security:
            # Set RADIUS server for WPA2-Enterprise
            # Retrieve values from kwargs, using default hardcoded values as fallbacks
            # eap_method = 'DEFAULT'
            # key_management = "WPA-PSK"
            # psk = "lf_ax1800_5g"
            # pairwise_ciphers = "DEFAULT"
            # group_ciphers = "DEFAULT"

            eap_method = '[BLANK]'
            key_management = "WPA-PSK"
            psk = "lf_ax88u_5g"
            pairwise_ciphers = "[BLANK]"
            group_ciphers = "[BLANK]"

        # if security.endswith('enterprise'):
        #     # Set RADIUS server for WPA2-Enterprise
        #     # Retrieve values from kwargs, using default hardcoded values as fallbacks
        #     eap_method = kwargs.get('eap_method', "PEAP")
        #     key_management = kwargs.get('key_management', "WPA-EAP")
        #     pairwise_ciphers = kwargs.get('pairwise_cipher', "DEFAULT")
        #     group_ciphers = kwargs.get('group_cipher', "DEFAULT")
        #     anon_identity = kwargs.get('anonymous_identity', "")
        #     identity = kwargs.get('identity', "wnbu@meraki.net")
        #     enterprise_password = kwargs.get('enterprise_password', "Wnbu+123")  # Use the new key name from YAML

        #    self.command.post_set_wifi_extra(port=station_name, resource=1, shelf=1,
        #                                     eap=eap_method,
        #                                     key_mgmt=key_management,
        #                                     pairwise=pairwise_ciphers,
        #                                     group=group_ciphers,
        #                                     anonymous_identity=anon_identity,
        #                                     identity=identity,
        #                                     password=enterprise_password)
            self.command.post_set_wifi_extra(port=station_name,
                                             resource=1,
                                             shelf=1,
                                             eap=eap_method,
                                             key_mgmt=key_management,
                                             psk=psk,
                                             pairwise=pairwise_ciphers,
                                             group=group_ciphers)
            time.sleep(1)

        # enable DHCP so as to get an address

        data = {
            "resource": 1,
            "shelf": 1,
            "port": station_name
        }

        port_current_flags = 0
        self.SetPortCurrentFlags: LFJsonCommand.SetPortCurrentFlags = self.command.SetPortCurrentFlags
        port_current_flags += self.SetPortCurrentFlags.use_dhcp
        data['current_flags'] = port_current_flags

        self.SetPortInterestFlags: LFJsonCommand.SetPortInterest = self.command.SetPortInterest
        port_interest_flags = 0
        port_interest_flags += self.SetPortInterestFlags.dhcp.value

        data['interest'] = port_interest_flags
        response = []
        result = self.command.post_set_port(response_json_list=response, **data)

        # Bring up client/port
        if admin_up:
            self.bring_up_client(station_name)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='create_client.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            ''',

        description='''none'''
    )
    parser.add_argument("--host", "--lf_mgr", "--mgr", dest='lf_mgr',
                        help='specify the GUI to connect to', default='192.168.50.104')
    parser.add_argument("--mgr_port", "--lf_mgr_port", dest='lf_mgr_port',
                        help="specify the GUI to connect to, default 8080", default="8080")
    parser.add_argument("--lf_user", dest='lf_user',
                        help="lanforge user name, default : lanforge", default="lanforge")
    parser.add_argument("--lf_passwd", dest='lf_passwd',
                        help="lanforge password, default : lanforge", default="lanforge")

    return parser.parse_args()


def main():
    args = parse_args()
    lf = lf_create_client(**vars(args))
    lf.create_client()


if __name__ == "__main__":
    main()
