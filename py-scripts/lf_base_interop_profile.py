#!/usr/bin/env python3
# flake8: noqa
"""
NAME: lf_base_interop_profile.py

PURPOSE: To use various functionality of LANforge Interop at function level

EXAMPLE-1:
$ ./lf_base_interop_profile.py --host 192.168.1.31 --ssid Airtel_9755718444_5GHz --passwd xyz --crypt psk2

EXAMPLE-2:
Command Line Interface for Wi-Fi Connectivity on all kinds of real devices
python3 lf_base_interop_profile.py --host 192.168.200.63 --ssid RDT_wpa2 --crypt psk2 --passwd OpenWifi --server_ip 192.168.1.61 --config_wifi

NOTES:

#@TODO more functionality need to be added


STATUS: BETA RELEASE

SCRIPT_CLASSIFICATION: Connectivity

SCRIPT_CATEGORIES: Configuration

VERIFIED_ON:
Working date    - 29/01/2024
Build version   - 5.4.7
kernel version  - 6.2.16+

License: Free to distribute and modify. LANforge systems must be licensed.
Copyright 2023 Candela Technologies Inc.

"""

import sys
import os
import importlib
import shlex
import subprocess
import json
import argparse
import time
import logging
import pandas as pd
import asyncio

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
interop_connectivity = importlib.import_module("py-json.interop_connectivity")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery


class BaseInteropWifi(Realm):
    def __init__(self, manager_ip=None,
                 port=8080,
                 ssid=None,
                 passwd=None,
                 encryption=None,
                 release=None,
                 screen_size_prcnt=0.4,
                 log_dur=0,
                 log_destination=None,
                 _debug_on=False,
                 _exit_on_error=False, ):
        super().__init__(lfclient_host=manager_ip,
                         debug_=_debug_on)
        if release is None:
            release = ["11", "12", "13"]
        self.manager_ip = manager_ip
        self.manager_port = port
        self.ssid = ssid
        self.passwd = passwd
        self.encryp = encryption
        self.release = release
        self.debug = _debug_on
        self.screen_size_prcnt = screen_size_prcnt
        self.supported_sdk = ["11", "12", "13"]
        self.supported_devices_names = []
        self.supported_devices_resource_id = None
        self.log_dur = log_dur
        self.log_destination = log_destination
        self.session = LFSession(lfclient_url=self.manager_ip,
                                 debug=_debug_on,
                                 connection_timeout_sec=2.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=_exit_on_error)
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.manager_ip) + ''':8080/adb/'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = (stdout.decode("utf-8"))
        out = json.loads(output)
        final = out["devices"]
        value, resource_id = [], {}
        if type(final) == list:
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            for i, j in zip(range(len(keys_lst)), keys_lst):
                value.append(final[i][j]["name"])
                resource_id[final[i][j]["resource-id"]] = final[i][j]["name"]
        else:
            #  only one device is present
            value.append(final["name"])
            resource_id[final["resource-id"]] = final["name"]
        self.supported_devices_names = value
        self.supported_devices_resource_id = resource_id
        logging.info(
            "List of all Available Devices Serial Numbers in Interop Tab:".format(self.supported_devices_names))
        logging.info(self.supported_devices_names)

    def get_device_details(self, query="name", device="1.1.RZ8N70TVABP"):
        # query device related details like name, phantom, model name etc
        value = None
        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.manager_ip) + ''':8080/adb/'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = (stdout.decode("utf-8"))
        out = json.loads(output)
        final = out["devices"]
        if type(final) == list:
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            for i, j in zip(range(len(keys_lst)), keys_lst):
                if j == device:
                    logging.info("Getting " + str(query) + " details for " + str(device) + " device.")
                    value = final[i][j][query]
        else:
            #  only one device is present
            value = final[query]
        return value

    def get_laptop_devices_details(self, query, device):
        lf_query_resource = self.json_get("/resource/all")
        keys = list(lf_query_resource.keys())
        if "resources" in keys:
            res = lf_query_resource["resources"]
            if type(res) is list:
                sec_key = []
                for i in res:
                    sec_key.append(list(i.keys()))
                new_list = []
                for z in sec_key:
                    for y in z:
                        new_list.append(y)
                loc_dict = dict.fromkeys(new_list)
                for i in loc_dict:
                    lst = ["host_name", "hw_version"]  # you can add the keys to the loc_dict if you want in feature.
                    loc_dict[i] = dict.fromkeys(lst)
                for n, m in zip(range(len(new_list)), new_list):
                    loc_dict[m]['host_name'] = res[n][m]['hostname']
                    loc_dict[m]['hw_version'] = res[n][m]['hw version']
                value = ""
                for i in loc_dict:
                    if i + "." in device:
                        value = loc_dict[i][query]
                return value
        else:
            logging.info("No resources present")

    # check list of adb devices are in phantom state or not if not return list of active devices
    def check_phantom(self):
        active_device = []
        for i in self.supported_devices_names:
            phantom = self.get_device_details(query="phantom", device=i)
            if not phantom:
                logging.info("Device " + str(i) + " is active")
                logging.info("Device " + str(i) + " is active")
                active_device.append(i)
            else:
                logging.info("Device " + str(i) + " is in phantom state")
                logging.info("Device " + str(i) + " is in phantom state")
        self.supported_devices_names = active_device
        return self.supported_devices_names

    # check if active devices are of expected release and return list of devices
    def check_sdk_release(self, selected_android_devices=None):
        if selected_android_devices is None:
            selected_android_devices = []
        if selected_android_devices:
            devices = selected_android_devices
        elif not selected_android_devices:
            devices = []
        else:
            devices = self.check_phantom()  # will take the available devices list
        rel_dev = []
        logging.info(f"Active Device list: {devices}")
        for i in devices:
            release_ver = self.get_device_details(query="release", device=i)
            for j in self.release:
                if release_ver == j:
                    # check if the release is supported in supported sdk  version
                    if release_ver in self.supported_sdk:
                        logging.info("The Device " + str(
                            i) + " has " + j + " sdk release, which is in available sdk versions list: %s" % self.supported_sdk)
                        # logging.info("device " + str(i) + " has " + j + " sdk release")
                        rel_dev.append(i)
                else:
                    logging.info("The Device " + str(
                        i) + " has different sdk release, which is not in available sdk versions list: %s" % self.supported_sdk)
                    # logging.info("Device " + str(i) + " has different sdk release")
        self.supported_devices_names = rel_dev
        return self.supported_devices_names

    # launch ui
    def launch_interop_ui(self, device=None):
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            devices = [device]
        if not devices:
            logging.warning("device EID is required")
            raise ValueError("device EID is required")
        for i in devices:
            # print(i)
            eid = self.name_to_eid(i)
            self.command.post_adb_gui(shelf=eid[0],
                                      resource=eid[1],
                                      adb_id=eid[2],
                                      display=self.manager_ip + ":10.0",
                                      screen_size_prcnt=self.screen_size_prcnt,
                                      debug=self.debug)

    def post_adb_(self, device=None, cmd=None):
        response_list = []
        errors_warnings = []

        adb_key = self.session.get_session_based_key()
        # self.session.logger.error("adb_key: " + adb_key)
        eid = self.name_to_eid(device)
        # print("ADB POST....")
        self.command.post_adb(shelf=eid[0],
                              resource=eid[1],
                              adb_id=eid[2],
                              key=adb_key,
                              adb_cmd=cmd,
                              debug=self.debug,
                              response_json_list=response_list,
                              errors_warnings=errors_warnings,
                              suppress_related_commands=True)
        # print(["Response", response_list])
        # logging.info("Response " + str(response_list))
        return response_list

    # enable Wi-Fi or disable Wi-Fi
    def enable_or_disable_wifi(self, wifi=None, device=None):
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            devices = [device]
        if not (wifi == "enable" or wifi == "disable"):
            logging.warning("wifi arg value must either be enable or disable")
            raise ValueError("wifi arg value must either be enable or disable")
        cmd = "shell svc wifi " + wifi
        for i in devices:
            logging.info(wifi + " wifi for " + i)
            self.post_adb_(device=i, cmd=cmd)

    # set username
    def set_user_name(self, device=None, user_name=None):
        logging.info(f"Name of the device: {device}")
        logging.info("device " + str(device))
        user_name_ = []
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            if type(device) is list:
                devices = device
            else:
                devices = [device]
            if user_name is None:
                for i in range(len(devices)):
                    user_name = "device_" + str(i)
                    # print(user_name)
                    logging.info(user_name)
                    user_name_.append(user_name)
                logging.info(f"Modified adb device user-name: {user_name}")
                logging.info(user_name)
            else:
                user_name_.append(user_name)
        logging.info(f"Available Devices List: {devices}")
        logging.info(f"Modified USER-NAME List: {user_name_}")
        logging.info(user_name_)

        for i, x in zip(devices, range(len(devices))):
            eid = self.name_to_eid(i)
            self.command.post_add_adb(adb_device=None,
                                      adb_id=eid[2],
                                      adb_model=None,
                                      adb_product=None,
                                      lf_username=user_name_[x],
                                      resource=eid[1],
                                      shelf=eid[0],
                                      debug=True)

    # apk apply
    def batch_modify_apply(self, device=None, manager_ip=None):
        if manager_ip is None:
            mgr_ip = self.manager_ip
        else:
            mgr_ip = manager_ip
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
            self.set_user_name()
        else:
            if type(device) is list:
                devices = device
            else:
                devices = [device]
                self.set_user_name(device=device)

        user_list = []
        for i in devices:
            name = self.get_device_details(query='user-name', device=i)
            user_list.append(name)

        for i, x in zip(user_list, devices):
            user_name = i
            if not user_name:
                logging.warning("please specify a user-name when configuring this Interop device")
                raise ValueError("please specify a user-name when configuring this Interop device")
            cmd = "shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity "
            cmd += "--es auto_start 1 --es username " + user_name
            if self.manager_ip:
                cmd += " --es serverip " + mgr_ip
            if self.ssid:
                cmd += " --es ssid " + self.ssid
            if self.passwd:
                cmd += " --es password " + self.passwd
            if self.encryp:
                cmd += " --es encryption " + self.encryp
            # print("ADB BATCH MODIFY CMD :", cmd)
            self.post_adb_(device=x, cmd=cmd)

    # start
    def start(self, device=None):
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            devices = [device]
        for i in devices:
            cmd = "shell am start --es auto_start 1 -n com.candela.wecan/com.candela.wecan.StartupActivity"
            self.post_adb_(device=i, cmd=cmd)

    # stop
    def stop(self, device=None):
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            devices = [device]
        for i in devices:
            cmd = "shell am force-stop com.candela.wecan"
            self.post_adb_(device=i, cmd=cmd)

    # scan results
    def scan_results(self, device=None):
        if device is None:
            devices = self.check_sdk_release()
            logging.info(devices)
        else:
            devices = [device]
        scan_dict = dict.fromkeys(devices)
        for i in devices:
            # start scan
            cmd = "shell cmd -w wifi start-scan"
            self.post_adb_(device=i, cmd=cmd)
            time.sleep(10)
            cmd = "shell cmd -w wifi list-scan-results"
            result = self.post_adb_(device=i, cmd=cmd)
            scan_dict[i] = result
        return scan_dict

    def clean_phantom_resources(self):
        lf_query_resource = self.json_get("/resource/all")
        logging.info("\n Now validating Resource manager ports \n")
        if 'resources' in list(lf_query_resource):
            for i in range(len(list(lf_query_resource['resources']))):
                id = (list(list(lf_query_resource['resources'])[i])[0])
                resource = list(lf_query_resource['resources'])[i].get(id)["phantom"]
                logging.info(f"The {id} port is in PHANTOM:- {resource}")
                while resource:
                    logging.info('Deleting the resource', id)
                    info = id.split('.')
                    req_url = "cli-json/rm_resource"
                    data = {
                        "shelf": int(info[0]),
                        "resource": int(info[1])
                    }
                    self.json_post(req_url, data)
                    break
        else:
            logging.info("No phantom resources")

        lf_query_resource = self.json_get("/resource/all")
        # time.sleep(1)

    # get eid username and phantom state of resources from resource manager
    # output {'1.1': {'user_name': '', 'phantom': False}, '1.16': {'user_name': 'device_0', 'phantom': True}}
    def get_resource_id_phantom_user_name(self):
        lf_query_resource = self.json_get("/resource/all")
        keys = list(lf_query_resource.keys())
        if "resources" in keys:
            res = lf_query_resource["resources"]
            if type(res) is list:
                sec_key = []
                for i in res:
                    sec_key.append(list(i.keys()))
                new_list = []
                for z in sec_key:
                    for y in z:
                        new_list.append(y)
                loc_dict = dict.fromkeys(new_list)
                for i in loc_dict:
                    lst = ["user_name", "phantom"]
                    loc_dict[i] = dict.fromkeys(lst)
                for n, m in zip(range(len(new_list)), new_list):
                    loc_dict[m]['user_name'] = res[n][m]['user']
                    loc_dict[m]['phantom'] = res[n][m]['phantom']
                return loc_dict
        else:
            logging.info("No resources present")

    def get_mac_address_from_port_mgr(self, eid="1.16.wlan0"):
        resources = self.json_get("port/all")
        keys = []
        if "interfaces" in list(resources.keys()):
            if type(resources['interfaces']) is list:
                for i in resources['interfaces']:
                    keys.append(list(i.keys()))
            new_keys = []
            for i in keys:
                for z in i:
                    new_keys.append(z)
            for i, z in zip(range(len(new_keys)), new_keys):
                if z == eid:
                    mac = resources['interfaces'][i][z]['ap']
                    return mac
        else:
            logging.info("interfaces is not present")
        # print(resources["interfaces"].key())

    def get_log_batch_modify(self, device=None):
        eid = self.name_to_eid(device)
        if self.log_dur > 0:
            if not self.log_destination:
                raise ValueError("adb log capture requires log_destination")
        user_key = self.session.get_session_based_key()
        if self.debug:
            logging.info("Destination [%s] dur[%s] user_key[%s] " % (self.log_destination, self.log_dur, user_key))
            # self.session.logger.register_method_name("json_post")
        json_response = []
        self.command.post_log_capture(shelf=eid[0],
                                      resource=eid[1],
                                      p_type="adb",
                                      identifier=eid[2],
                                      duration=self.log_dur,
                                      destination=self.log_destination,
                                      user_key=self.session.get_session_based_key(),
                                      response_json_list=json_response,
                                      debug=True)


class UtilityInteropWifi(BaseInteropWifi):
    def __init__(self, host_ip=None):
        super().__init__(manager_ip=host_ip)
        self.host = host_ip

    def get_device_state(self, device=None):
        cmd = 'shell dumpsys wifi | grep "mWifiInfo SSID"'
        # print("Get device Status CMD :", cmd)
        x = self.post_adb_(device=device, cmd=cmd)
        y = x[0]['LAST']['callback_message']
        z = y.split(" ")
        # print(z)
        # state = None
        if 'state:' in z:
            # print("yes")
            ind = z.index("state:")
            # print(ind)
            st = z[(int(ind) + 1)]
            # print("state", st)
            logging.info("state" + st)
            state = st

        else:
            logging.info("state is not present")
            state = "NA"
        return state

    def get_device_ssid(self, device=None):
        cmd = 'shell dumpsys wifi | grep "mWifiInfo SSID"'
        x = self.post_adb_(device=device, cmd=cmd)
        y = x[0]['LAST']['callback_message']
        z = y.split(" ")
        # print(z)
        # ssid = None
        if 'SSID:' in z:
            # print("yes")
            ind = z.index("SSID:")
            ssid = z[(int(ind) + 1)]
            ssid_ = ssid.strip()
            ssid_1 = ssid_.replace('"', "")
            ssid_2 = ssid_1.replace(",", "")
            # print("ssid", ssid_2)
            logging.info("ssid " + ssid_2)
            ssid = ssid_2
        else:
            logging.info("ssid is not present")
            ssid = "NA"
        return ssid

    def get_wifi_health_monitor(self, device=None, ssid=None):
        cmd = "shell dumpsys wifi | sed -n '/^WifiHealthMonitor - Log Begin ----$/,/^WifiHealthMonitor - Log End ----$/{/^WifiHealthMonitor - Log End ----$/!p;}'"
        # print("Wifi Health monitor CMD:", cmd)
        x = self.post_adb_(device=device, cmd=cmd)
        y = x[0]["LAST"]["callback_message"]
        z = y.split(" ")
        # print(z)
        value = ["ConnectAttempt", "ConnectFailure", "AssocRej", "AssocTimeout"]
        return_dict = dict.fromkeys(value)
        if '"' + ssid + '"' + "\n" in z:
            # print("yes")
            # logging.info("yes")
            ind = z.index('"' + ssid + '"' + "\n")
            # print(z[271])
            m = z[ind:]
            # logging.info(m)
            if "ConnectAttempt:" in m:
                connect_ind = m.index("ConnectAttempt:")
                connect_attempt = m[connect_ind + 1]
                # logging.info("connection attempts " + connect_attempt)
                return_dict["ConnectAttempt"] = connect_attempt
            if 'ConnectFailure:' in m:
                connect_fail_ind = m.index('ConnectFailure:')
                connect_failure = m[connect_fail_ind + 1]
                # logging.info("connection failure " + connect_failure)
                return_dict["ConnectFailure"] = connect_failure
            if 'AssocRej:' in m:
                ass_rej_ind = m.index('AssocRej:')
                assocrej = m[ass_rej_ind + 1]
                # logging.info("association rejection " + assocrej)
                return_dict["AssocRej"] = assocrej
            if 'AssocTimeout:' in m:
                ass_ind = m.index('AssocTimeout:')
                asso_timeout = m[ass_ind + 1]
                # logging.info("association timeout " + asso_timeout)
                return_dict["AssocTimeout"] = asso_timeout
        else:
            logging.info(
                f"Given {ssid} ssid is not present in the 'ConnectAttempt', 'ConnectFailure', 'AssocRej', 'AssocTimeout' States")
            logging.info("ssid is not present")
        return return_dict

    # forget network based on the network id
    def forget_netwrk(self, device=None, network_id=None):
        separating_device_name = device.split(".")
        if network_id is None:
            network_id = ['0']
        else:
            network_id = network_id
        for ntwk_id in network_id:
            logging.info(f"Forgetting network for {device} with network id : {ntwk_id}")
            cmd = f"-s {separating_device_name[2]} shell cmd -w wifi forget-network " + ntwk_id
            # print("CMD", cmd)
            self.post_adb_(device=device, cmd=cmd)

    # list out the saved/already connected network id, ssid, security
    def list_networks_info(self, device_name="1.1.RZ8NB1JNGDT"):
        # device_name should have the self, resource
        separating_device_name = device_name.split(".")

        cmd = f'-s {separating_device_name[2]} shell cmd -w wifi list-networks'
        # print("CMD for fetching the saved network pofile ids:", cmd)
        resp = self.post_adb_(device=device_name, cmd=cmd)
        network_details = resp[0]['LAST']['callback_message']
        # print("List of the saved profiles for %s device:" % device_name)
        # print(resp[0]['LAST']['callback_message'])
        if 'No networks' in network_details:
            network_info_dict = "No networks"
        else:
            values = resp[0]['LAST']['callback_message'].split('\n')[1:]
            # print("The Saved Profiles List:", values)
            print(f"Number of saved profiles:  {len(values)}")
            network_ids, saved_ssid, saved_security = [], [], []
            for i in range(len(values)):
                network_info = values[i].split()
                network_id, ssid, security_type = network_info
                network_ids.append(network_id)
                saved_ssid.append(ssid)
                saved_security.append(security_type)
            # Creating a dictionary 'network_info_dict' with the extracted values
            network_info_dict = {
                'Network Id': network_ids,
                'SSID': saved_ssid,
                'Security type': saved_security
            }
            # print("Network info:", network_info_dict)
        return network_info_dict


class RealDevice(Realm):
    def __init__(self,
                 manager_ip=None,
                 port=8080,
                 server_ip=None,
                 ssid_2g=None,
                 passwd_2g=None,
                 encryption_2g=None,
                 eap_method_2g=None,
                 eap_identity_2g=None,
                 ssid_5g=None,
                 passwd_5g=None,
                 encryption_5g=None,
                 eap_method_5g=None,
                 eap_identity_5g=None,
                 ssid_6g=None,
                 passwd_6g=None,
                 encryption_6g=None,
                 eap_method_6g=None,
                 eap_identity_6g=None,
                 selected_bands=['5g'],
                 groups=False,
                 _debug_on=False,
                 _exit_on_error=False):
        super().__init__(lfclient_host=manager_ip,
                         debug_=_debug_on)
        self.manager_ip = manager_ip
        self.manager_port = port
        self.server_ip = server_ip

        self.ssid_2g = ssid_2g
        self.passwd_2g = passwd_2g
        self.encryption_2g = encryption_2g

        self.ssid_5g = ssid_5g
        self.passwd_5g = passwd_5g
        self.encryption_5g = encryption_5g

        self.ssid_6g = ssid_6g
        self.passwd_6g = passwd_6g
        self.encryption_6g = encryption_6g

        # for enterprise authentication
        self.eap_method_2g = eap_method_2g
        self.eap_identity_2g = eap_identity_2g

        self.eap_method_5g = eap_method_5g
        self.eap_identity_5g = eap_identity_5g

        self.eap_method_6g = eap_method_6g
        self.eap_identity_6g = eap_identity_6g

        self.selected_bands = selected_bands

        self.devices = []
        self.devices_data = {}
        self.selected_device_eids = []
        self.selected_devices = []
        self.selected_macs = []
        self.report_labels = []
        self.windows_list = []
        self.linux_list = []
        self.mac_list = []
        self.android_list = []
        self.station_list = []
        self.android = 0
        self.linux = 0
        self.windows = 0
        self.mac = 0
        self.groups=groups

        if self.groups is False:
            for band in selected_bands:
                if (band.lower() == '2g' and None in [self.ssid_2g, self.encryption_2g, self.passwd_2g]):
                    logging.critical(
                        '2G band is selected for connectivity for required ssid, encryption and password are not properly provided. Aborting the test')
                    exit(1)
                elif (band.lower() == '5g' and None in [self.ssid_5g, self.encryption_5g, self.passwd_5g]):
                    logging.critical(
                        '5G band is selected for connectivity for required ssid, encryption and password are not properly provided. Aborting the test')
                    exit(1)
                elif (band.lower() == '6g' and None in [self.ssid_6g, self.encryption_6g, self.passwd_6g]):
                    logging.critical(
                        '6G band is selected for connectivity for required ssid, encryption and password are not properly provided. Aborting the test')
                    exit(1)

    def query_all_devices_to_configure_wifi(self,device_list=None):
        self.all_devices = {}
        self.selected_2g_serials = []
        self.selected_5g_serials = []
        self.selected_6g_serials = []

        index = 1 # serial number for selection of devices
        
        # fetch all androids
        self.androids_obj = interop_connectivity.Android(
            lanforge_ip=self.manager_ip,
            port=self.manager_port,
            server_ip=self.server_ip,
            ssid_2g=self.ssid_2g,
            passwd_2g=self.passwd_2g,
            encryption_2g=self.encryption_2g,
            eap_method_2g=self.eap_method_2g,
            eap_identity_2g=self.eap_identity_2g,
            ssid_5g=self.ssid_5g,
            passwd_5g=self.passwd_5g,
            encryption_5g=self.encryption_5g,
            eap_method_5g=self.eap_method_5g,
            eap_identity_5g=self.eap_identity_5g,
            ssid_6g=self.ssid_6g,
            passwd_6g=self.passwd_6g,
            encryption_6g=self.encryption_6g,
            eap_method_6g=self.eap_method_6g,
            eap_identity_6g=self.eap_identity_6g)
        self.androids = self.androids_obj.get_devices()
        for android in self.androids:
            shelf, resource, serial = android
            self.all_devices[index] = {
                'port': '{}.{}'.format(shelf, resource),
                'username': serial,
                'os': 'Android'
            }
            index += 1

        # fetch all laptops
        self.laptops_obj = interop_connectivity.Laptop(lanforge_ip=self.manager_ip,
                                                       port=self.manager_port,
                                                       server_ip=self.server_ip,
                                                       ssid_2g=self.ssid_2g,
                                                       passwd_2g=self.passwd_2g,
                                                       encryption_2g=self.encryption_2g,
                                                       eap_method_2g=self.eap_method_2g,
                                                       eap_identity_2g=self.eap_identity_2g,
                                                       ssid_5g=self.ssid_5g,
                                                       passwd_5g=self.passwd_5g,
                                                       encryption_5g=self.encryption_5g,
                                                       eap_method_5g=self.eap_method_5g,
                                                       eap_identity_5g=self.eap_identity_5g,
                                                       ssid_6g=self.ssid_6g,
                                                       passwd_6g=self.passwd_6g,
                                                       encryption_6g=self.encryption_6g,
                                                       eap_method_6g=self.eap_method_6g,
                                                       eap_identity_6g=self.eap_identity_6g)
        self.laptops = self.laptops_obj.get_resources_data()
        for laptop in self.laptops:
            self.all_devices[index] = {
                'port': '{}.{}'.format(laptop['shelf'], laptop['resource']),
                'username': laptop['hostname'],
                'os': laptop['os']
            }
            index += 1

        pd.set_option('display.max_rows', None)
        df = pd.DataFrame(data=self.all_devices).transpose()
        print(df)
        if device_list is None:
            select_serials = input(
                'Select the serial numbers of devices to run the test(e.g. 2G=1,2,3:5G=4,5,6:6G=7,8,9): ').lower()
        else:
            selected = '5g='
            device_serials = []
            for device in device_list:
                for idx in self.all_devices:
                    if self.all_devices[idx]['username'] == device:
                        device_serials.append(str(idx))
                        break
            select_serials = selected + (",").join(device_serials)
        for band in select_serials.split(':'):
            if ('2g' in band) and ('2g' in self.selected_bands or '2G' in self.selected_bands or '2.4G' in self.selected_bands):
                if ('all' in band):
                    self.selected_2g_serials = list(range(1, index))
                else:
                    self.selected_2g_serials = list(map(int, band.replace('2g=','').strip().split(',')))
            elif ('5g' in band) and ('5g' in self.selected_bands or '5G' in self.selected_bands):
                if ('all' in band):
                    self.selected_5g_serials = list(range(1, index))
                else:
                    self.selected_5g_serials = list(map(int, band.replace('5g=','').strip().split(',')))
            elif ('6g' in band):
                if ('all' in band and '6g' in self.selected_bands or '6G' in self.selected_bands):
                    self.selected_6g_serials = list(range(1, index))
                else:
                    self.selected_6g_serials = list(map(int, band.replace('6g=','').strip().split(',')))

        print(self.selected_2g_serials, self.selected_5g_serials, self.selected_6g_serials)
        return [self.selected_2g_serials, self.selected_5g_serials, self.selected_6g_serials]

    # To configure interop devices to an ssid at the time of device selection for testing
    # Step 1: queries all interop devices from both interop tab and resource manager
    # Step 2: displays port, username and os details of all real devices
    # Step 3: the user then should select the devices from the list using serial numbers
    # Step 4: the devices get configured and then the script waits for 2 minutes for the configuration to apply
    # Step 5: then it checks both android and laptops for the expected configuration. If the configuration is not as expected, then the respective device is eliminated from the test
    # Step 6: The script then proceeds for the test
    async def configure_wifi(self, select_serials=None):
        self.station_list = []
        selected_androids = []
        selected_laptops = []
        selected_t_devices = {}
        if(select_serials is None):
            if (len(set(self.selected_2g_serials).intersection(self.selected_5g_serials)) == len(
                    set(self.selected_2g_serials).intersection(self.selected_6g_serials)) == len(
                    set(self.selected_5g_serials).intersection(self.selected_6g_serials)) == 0):
                select_serials = self.selected_2g_serials + self.selected_5g_serials + self.selected_6g_serials
            else:
                logging.critical(
                    'While performing connectivity, found one or more devices selected are in common between different bands. Aborting the test')
                exit(1)
        for selected_serial in select_serials:
            selected_username = self.all_devices[selected_serial]['username']
            selected_os = self.all_devices[selected_serial]['os']
            if(selected_os == 'Android'):
                for android in self.androids:
                    if (android[2] == selected_username):
                        if (selected_serial in self.selected_2g_serials):
                            if '2g' not in android:
                                android.append('2g')
                        elif (selected_serial in self.selected_5g_serials):
                            if '5g' not in android:
                                android.append('5g')
                        elif (selected_serial in self.selected_6g_serials):
                            if '6g' not in android:
                                android.append('6g')
                        selected_androids.append(android)
                        break
            else:
                for laptop in self.laptops:
                    if (laptop['hostname'] == selected_username):
                        if (selected_serial in self.selected_2g_serials):
                            if '2g' not in laptop:
                                laptop['band'] = '2g'
                        elif (selected_serial in self.selected_5g_serials):
                            if '5g' not in laptop:
                                laptop['band'] = '5g'
                        elif (selected_serial in self.selected_6g_serials):
                            if '6g' not in laptop:
                                laptop['band'] = '6g'
                        selected_laptops.append(laptop)
                        break

        if(selected_androids != []):
            await self.androids_obj.stop_app(port_list=selected_androids)
            await self.androids_obj.configure_wifi(port_list=selected_androids)

        if(selected_laptops != []):
            await self.laptops_obj.rm_station(port_list=selected_laptops)
            await self.laptops_obj.add_station(port_list=selected_laptops)
            await self.laptops_obj.set_port(port_list=selected_laptops)

        logging.info('Applying the new Wi-Fi configuration. Waiting for 2 minutes for the new configuration to apply.')
        time.sleep(120)

        # selecting devices only those connected to given SSID and contains IP
        # for androids
        exclude_androids = []
        for android in selected_androids:    

            if (android[3] == '2g'):
                curr_ssid = self.ssid_2g
            elif (android[3] == '5g'):
                curr_ssid = self.ssid_5g
            elif (android[3] == '6g'):
                curr_ssid = self.ssid_6g

            # get resource id for the android device from interop tab
            resource_id = self.json_get('/adb/1/1/{}'.format(android[2]))['devices']['resource-id']

            # if there is no resource id in interop tab
            if(resource_id == ''):
                logging.warning(
                    'The android with serial {} is missing resource id. Excluding it from testing'.format(android[2]))
                exclude_androids.append(android)
                continue

            # fetching resource data for android device
            current_android_resource_data = \
            self.json_get('/resource/{}/{}/'.format(resource_id.split('.')[0], resource_id.split('.')[1]))['resource']

            if(current_android_resource_data['phantom']):
                logging.warning(
                    'The android with serial {} is in phantom state in resource manager. Excluding it from testing'.format(android[2]))
                exclude_androids.append(android)
                continue

            # fetching port data for the android device
            current_android_port_data = \
            self.json_get('/port/{}/{}/wlan0'.format(resource_id.split('.')[0], resource_id.split('.')[1]))['interface']


            current_android_port_data.update(current_android_resource_data)
            
            # checking if the android is connected to the desired ssid
            if (current_android_port_data['ssid'] != curr_ssid):
                logging.warning(
                    'The android with serial {} is not conneted to the given SSID {}. Excluding it from testing'.format(
                        android[2], curr_ssid))
                exclude_androids.append(android)
                continue

            # checking if the android is active or down
            if(current_android_port_data['ip'] == '0.0.0.0'):
                logging.warning('The android with serial {} is down. Excluding it from testing'.format(android[2]))
                exclude_androids.append(android)
                continue

            username = \
            self.json_get('resource/{}/{}?fields=user'.format(resource_id.split('.')[0], resource_id.split('.')[1]))[
                'resource']['user']

            self.selected_devices.append(resource_id)
            self.selected_macs.append(current_android_port_data['mac'])
            self.report_labels.append('{} android {}'.format(resource_id, username)[:25])
            self.android += 1
            self.android_list.append(resource_id)
            
            current_sta_name = resource_id + '.wlan0'
            self.station_list.append(current_sta_name)

            self.devices_data[current_sta_name] = current_android_port_data
            self.devices_data[current_sta_name]['ostype'] = 'android'

            selected_t_devices[resource_id] = {
                'hw version': 'Android',
                'MAC': current_android_port_data['mac']
            }
            
            
        for android in exclude_androids:
            selected_androids.remove(android)

        # for laptops
        exclude_laptops = []
        for laptop in selected_laptops:

            if (laptop['band'] == '2g'):
                curr_ssid = self.ssid_2g
            elif (laptop['band'] == '5g'):
                curr_ssid = self.ssid_5g
            elif (laptop['band'] == '6g'):
                curr_ssid = self.ssid_6g

            # check SSID and IP values from port manager
            current_laptop_port_data = self.json_get(
                '/port/{}/{}/{}'.format(laptop['shelf'], laptop['resource'], laptop['sta_name']))
            if(current_laptop_port_data is None):
                logging.warning(
                    'The laptop with port {}.{}.{} not found. Excluding it from testing'.format(laptop['shelf'],
                                                                                                laptop['resource'],
                                                                                                laptop['sta_name']))
                exclude_laptops.append(laptop)
                continue

            current_laptop_port_data = current_laptop_port_data['interface']

            # checking if the laptop is connected to the desired ssid
            if (current_laptop_port_data['ssid'] != curr_ssid):
                logging.warning(
                    'The laptop with port {}.{}.{} is not conneted to the given SSID {}. Excluding it from testing'.format(
                        laptop['shelf'], laptop['resource'], laptop['sta_name'], curr_ssid))
                exclude_laptops.append(laptop)
                continue

            # checking if the laptop is active or down
            if(current_laptop_port_data['ip'] == '0.0.0.0'):
                logging.warning(
                    'The laptop with port {}.{}.{} is down. Excluding it from testing'.format(laptop['shelf'],
                                                                                              laptop['resource'],
                                                                                              laptop['sta_name']))
                exclude_laptops.append(laptop)
                continue

            current_laptop_resource_data = self.json_get('resource/{}/{}'.format(laptop['shelf'], laptop['resource']))[
                'resource']
            hostname = current_laptop_resource_data['hostname']

            current_laptop_port_data.update(current_laptop_resource_data)

            # adding port id to selected_device_eids
            current_resource_id = '{}.{}.{}'.format(laptop['shelf'], laptop['resource'], laptop['sta_name'])
            self.selected_devices.append(current_resource_id)
            self.selected_macs.append(current_laptop_port_data['mac'])
            self.report_labels.append('{} {} {}'.format(current_resource_id, laptop['os'], hostname)[:25])

            selected_t_devices[current_resource_id] = {
                'MAC': current_laptop_port_data['mac']
            }
            if(laptop['os'] == 'Win'):
                self.windows += 1
                self.windows_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Win'
                current_laptop_port_data['ostype'] = 'windows'
            elif(laptop['os'] == 'Lin'):
                self.linux += 1
                self.linux_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Lin'
                current_laptop_port_data['ostype'] = 'linux'
            elif(laptop['os'] == 'Apple'):
                self.mac += 1
                self.mac_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Mac'
                current_laptop_port_data['ostype'] = 'macos'
            
            current_sta_name = current_resource_id
            self.station_list.append(current_sta_name)

            self.devices_data[current_sta_name] = current_laptop_port_data

        for laptop in exclude_laptops:
            selected_laptops.remove(laptop)

        df = pd.DataFrame(data=selected_t_devices).transpose()
        print(df)
        return [self.selected_devices, self.report_labels, self.selected_macs]

    async def configure_wifi_groups(self,select_serials,serials_input,ssid_input,passwd_input,enc_input,eap_method_input,eap_identity_input):
        self.station_list = []
        selected_androids = []
        selected_androids_temp = [] 
        selected_laptops = []
        selected_t_devices = {}
        print(serials_input,passwd_input)
        for selected_serial in select_serials:
            selected_username = self.all_devices[selected_serial]['username']
            selected_os = self.all_devices[selected_serial]['os']
            if(selected_os == 'Android'):
                for android in self.androids:
                    if (android[2] == selected_username):
                        temp = android.copy()
                        temp.append("5g")
                        selected_androids_temp.append(temp)
                        idx = serials_input.index(selected_username)
                        android.append(ssid_input[idx])
                        android.append(passwd_input[idx])
                        android.append(enc_input[idx])
                        android.append(eap_method_input[idx])
                        android.append(eap_identity_input[idx])
                        selected_androids.append(android)
                        break
            else:
                for laptop in self.laptops:
                    if (laptop['hostname'] == selected_username):
                        idx = serials_input.index(selected_username)
                        laptop['ssid'] = ssid_input[idx]
                        laptop['passwd'] = passwd_input[idx]
                        laptop['enc'] = enc_input[idx]
                        laptop['eap_method'] = eap_method_input[idx]
                        laptop['eap_identity'] = eap_identity_input[idx]
                        laptop['band'] = '5g'
                        selected_laptops.append(laptop)
                        break
        if(selected_androids != []):
            await self.androids_obj.stop_app(port_list=selected_androids_temp)
            await self.androids_obj.configure_wifi(port_list=selected_androids)

        if(selected_laptops != []):
            await self.laptops_obj.rm_station(port_list=selected_laptops)
            await self.laptops_obj.add_station(port_list=selected_laptops)
            await self.laptops_obj.set_port(port_list=selected_laptops)

        logging.info('Applying the new Wi-Fi configuration. Waiting.......')
        # selecting devices only those connected to given SSID and contains IP
        # for androids
        
        return [selected_androids, selected_laptops]
    
    def monitor_connection(self,selected_androids,selected_laptops):
        station_list = []
        selected_t_devices = {}
        selected_devices = []
        selected_macs = []
        report_labels= []
        androids = 0
        android_list = []
        linuxs = 0
        linux_list = []
        macs = 0
        mac_list = []
        
        # selecting devices only those connected to given SSID and contains IP
        # for androids
        exclude_androids = []
        for android in selected_androids:    

            curr_ssid = android[3]


            # get resource id for the android device from interop tab
            resource_id = self.json_get('/adb/1/1/{}'.format(android[2]))['devices']['resource-id']

            # if there is no resource id in interop tab
            if(resource_id == ''):
                exclude_androids.append(android)
                continue

            # fetching port data for the android device
            current_android_port_data = \
            self.json_get('/port/{}/{}/wlan0'.format(resource_id.split('.')[0], resource_id.split('.')[1]))['interface']

            # fetching resource data for android device
            current_android_resource_data = \
            self.json_get('/resource/{}/{}/'.format(resource_id.split('.')[0], resource_id.split('.')[1]))['resource']

            current_android_port_data.update(current_android_resource_data)
            
            # checking if the android is connected to the desired ssid
            if (current_android_port_data['ssid'] != curr_ssid):
                exclude_androids.append(android)
                continue

            # checking if the android is active or down
            if(current_android_port_data['ip'] == '0.0.0.0'):
                exclude_androids.append(android)
                continue

            username = \
            self.json_get('resource/{}/{}?fields=user'.format(resource_id.split('.')[0], resource_id.split('.')[1]))[
                'resource']['user']

            selected_devices.append(resource_id)
            selected_macs.append(current_android_port_data['mac'])
            report_labels.append('{} android {}'.format(resource_id, username))
            androids += 1
            android_list.append(resource_id)
            
            current_sta_name = resource_id + '.wlan0'
            station_list.append(current_sta_name)

            self.devices_data[current_sta_name] = current_android_port_data
            self.devices_data[current_sta_name]['ostype'] = 'android'

            selected_t_devices[resource_id] = {
                'hw version': 'Android',
                'MAC': current_android_port_data['mac']
            }
            
        for android in exclude_androids:
            selected_androids.remove(android)
    
        # for laptops
        exclude_laptops = []
        for laptop in selected_laptops:
            
            curr_ssid = laptop["ssid"]

            # check SSID and IP values from port manager
            current_laptop_port_data = self.json_get(
                '/port/{}/{}/{}'.format(laptop['shelf'], laptop['resource'], laptop['sta_name']))
            if(current_laptop_port_data is None):
                exclude_laptops.append(laptop)
                continue

            current_laptop_port_data = current_laptop_port_data['interface']

            # checking if the laptop is connected to the desired ssid
            if (current_laptop_port_data['ssid'] != curr_ssid):
                exclude_laptops.append(laptop)
                continue

            # checking if the laptop is active or down
            if(current_laptop_port_data['ip'] == '0.0.0.0'):
                exclude_laptops.append(laptop)
                continue

            current_laptop_resource_data = self.json_get('resource/{}/{}'.format(laptop['shelf'], laptop['resource']))[
                'resource']
            hostname = current_laptop_resource_data['hostname']

            current_laptop_port_data.update(current_laptop_resource_data)

            # adding port id to selected_device_eids
            current_resource_id = '{}.{}.{}'.format(laptop['shelf'], laptop['resource'], laptop['sta_name'])
            selected_devices.append(current_resource_id)
            selected_macs.append(current_laptop_port_data['mac'])
            report_labels.append('{} {} {}'.format(current_resource_id, laptop['os'], hostname))

            selected_t_devices[current_resource_id] = {
                'MAC': current_laptop_port_data['mac']
            }
            if(laptop['os'] == 'Win'):
                self.windows += 1
                self.windows_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Win'
                current_laptop_port_data['ostype'] = 'windows'
            elif(laptop['os'] == 'Lin'):
                linuxs += 1
                linux_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Lin'
                current_laptop_port_data['ostype'] = 'linux'
            elif(laptop['os'] == 'Apple'):
                macs += 1
                mac_list.append(current_resource_id)
                selected_t_devices[current_resource_id]['hw version'] = 'Mac'
                current_laptop_port_data['ostype'] = 'macos'
            
            current_sta_name = current_resource_id
            station_list.append(current_sta_name)

            self.devices_data[current_sta_name] = current_laptop_port_data

        for laptop in exclude_laptops:
            selected_laptops.remove(laptop)

        df = pd.DataFrame(data=selected_t_devices).transpose()
        print(df)
        return [selected_devices, report_labels, selected_macs]
    
    # getting data of all real devices already configured to an SSID
    def get_devices(self, only_androids = False):
        devices            = []
        devices_data       = {}
        resources          = []
        resources_os_types = {}
        resources_data     = {}

        # Get resources and OS types
        resources_list = self.json_get("/resource/all")["resources"]
        for resource_data_dict in resources_list:
            # Need to unpack resource data dict of encapsulating dict that contains it
            resource_id = list(resource_data_dict.keys())[0]
            resource_data_dict = resource_data_dict[resource_id]

            if 'ct-kernel' not in resource_data_dict or 'hw version' not in resource_data_dict or 'eid' not in resource_data_dict:
                logging.error('Malformed json response for endpoint /resource/all')
                raise ValueError('Malformed json response for endpoint /resource/all')

            if resource_data_dict['ct-kernel'] == True:
                # Custom kernel indicates not a real device, so do not track this resource
                continue

            # TODO: iOS, Add OS version field to output (we keep track of that info already in the GUI)
            # Get OS version based on 'hw version' field
            hw_ver = resource_data_dict['hw version']
            phantom = resource_data_dict['phantom']
            # It appends only non-phantom  androids into resources list 
            if only_androids :
                if not hw_ver.startswith(('Win', 'Linux', 'Apple')) and phantom == False:
                    os_type = 'android'
                    resources.append(resource_id)
                    resources_os_types[resource_id] = os_type
                    resources_data[resource_id]   = resource_data_dict

            # It appends both androids and laptops into resources list when laptops and android arguments are not passed
            else:
                if 'Win/x86' in hw_ver:
                    os_type = 'windows'
                elif 'Apple/x86' in hw_ver:
                    os_type = 'macos'
                elif 'Linux/x86' in hw_ver:
                    os_type = 'linux'
                else:
                    os_type = 'android'

                resources.append(resource_id)
                resources_os_types[resource_id] = os_type
                resources_data[resource_id]     = resource_data_dict


        # Get ports
        # TODO: Add optional argument to function to allow the detection of down ports.
        #       Currently only returns real device ports which are not phantom and are up
        ports = self.json_get('/ports/all')['interfaces']
        for port_data_dict in ports:
            port_id = list(port_data_dict.keys())[0]

            # Assume three components to port ID, each separated by a period (e.g. '1.1.wlan0')
            # First two components is the resource ID (e.g. '1.1' for '1.1.wlan0')
            port_id_parts = port_id.split('.')
            resource_id   = port_id_parts[0] + '.' + port_id_parts[1]

            # Skip any non-real devices we have decided to not track
            if resource_id not in resources:
                continue

            # Need to unpack resource data dict of encapsulating dict that contains it
            port_data_dict = port_data_dict[port_id]

            if 'phantom' not in port_data_dict or 'down' not in port_data_dict or 'parent dev' not in port_data_dict:
                logging.error('Malformed json response for endpoint /ports/all')
                raise ValueError('Malformed json response for endpoint /ports/all')

            # Skip phantom or down ports
            if port_data_dict['phantom'] or port_data_dict['down']:
                continue

            # TODO: Support more than one station per real device
            # print(port_data_dict['parent dev'])
            if port_data_dict['parent dev'] != 'wiphy0':
                continue

            # Sneak resource data into the port data dict
            # This is smelly code, though. We should just keep track of the resource data instead
            port_data_dict.update(resources_data[resource_id])

            devices.append(port_id)
            port_data_dict['ostype']  = resources_os_types[resource_id]
            devices_data[port_id]     = port_data_dict

        self.devices          = devices
        self.devices_data     = devices_data

        return self.devices
    
    # querying the user the required mobiles to test
    def query_user(self, dowebgui=False, device_list=""):
        print('The available real devices are:')
        # print('Port\t\thw version\t\t\tMAC')
        t_devices = {}
        all_devices_list = []
        for device, device_details in self.devices_data.items():
            # 'eid' and 'hw version' originally comes from resource data. Snuck into port data to make life easier
            t_devices[device_details['eid']] = {
                'Port Name': device,
                'hw version': device_details['hw version'],
                'MAC': device_details['mac']
            }
            all_devices_list.append(device_details['eid'])
            # print('{}\t{}\t\t\t{}'.format(device, device_details['hw version'], device_details['mac']))
        pd.set_option('display.max_rows', None)
        df = pd.DataFrame(data=t_devices).transpose()
        print(df)

        if dowebgui:
            self.selected_device_eids=device_list.split(",")
        else:
            self.selected_device_eids = input('Select the devices to run the test(e.g. 1.10,1.11 or all to run the test on all devices): ').split(',')

        # if all is seleceted making the list as empty string so that it would consider all devices
        if(self.selected_device_eids == ['all']):
            self.selected_device_eids = all_devices_list
        print('You have selected the below devices for testing')
        # print('Port\t\thw version\t\t\tMAC')
        selected_t_devices = {}
        for selected_device in self.selected_device_eids:
            for device, device_details in self.devices_data.items():
                if(selected_device + '.' in device):
                    # filtering interfaces other than wlan0 for android
                    if('Apple' not in self.devices_data[device]['hw version'] and 'Linux' not in self.devices_data[device]['hw version'] and 'Win' not in self.devices_data[device]['hw version']):
                        if('wlan0' not in device):
                            continue
                    selected_t_devices[device] = {
                        'Eid': selected_device,
                        'hw version': self.devices_data[device]['hw version'],
                        'MAC': self.devices_data[device]['mac']
                    }
                    self.selected_devices.append(device)
                    self.selected_macs.append(self.devices_data[device]['mac'])
                    self.report_labels.append('{} {} {}'.format(selected_device, [
                        'Win' if 'Win' in self.devices_data[device]['hw version'] else 'Lin' if 'Lin' in
                                                                                                self.devices_data[
                                                                                                    device][
                                                                                                    'hw version'] else 'Mac' if 'Mac' in
                                                                                                                                self.devices_data[
                                                                                                                                    device][
                                                                                                                                    'hw version'] else 'android'][
                        0], [self.devices_data[device]['user'] if self.devices_data[device]['user'] != '' else
                             self.devices_data[device]['hostname']][0])[:25])
                    if('Win' in 'Win' in self.devices_data[device]['hw version']):
                        self.windows += 1
                        self.windows_list.append(device)
                    elif('Lin' in 'Lin' in self.devices_data[device]['hw version']):
                        self.linux += 1
                        self.linux_list.append(device)
                    elif('Apple' in self.devices_data[device]['hw version']):
                        self.mac += 1
                        self.mac_list.append(device)
                    else:
                        self.android += 1
                        self.android_list.append(device)
        df = pd.DataFrame(data=selected_t_devices).transpose()
        print(df)
        return [self.selected_devices, self.report_labels, self.selected_macs]


def main():
    help_summary='''\
This script is a standard library which support different functionality of interop including wi-fi connectivity on all kinds of real clients.
    '''
    desc = """standard library which supports different functionality of interop
        Operations:

        EXAMPLE-1: 
        *    Example of scan results: 
        lf_base_interop_profile.py --host 192.168.1.31 --ssid Airtel_9755718444_5GHz --passwd xyz --crypt psk2

        EXAMPLE-2:
        For Wi-Fi Connectivity on all kinds of real devices
        python3 lf_base_interop_profile.py --host 192.168.200.63 --ssid RDT_wpa2 --crypt psk2 --passwd OpenWifi --server_ip 192.168.1.61 --config_wifi

        NAME: lf_base_interop_profile.py

        STATUS: BETA RELEASE

        SCRIPT_CLASSIFICATION: Connectivity

        SCRIPT_CATEGORIES: Configuration

        VERIFIED_ON:
        Working date    - 29/01/2024
        Build version   - 5.4.7
        kernel version  - 6.2.16+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright 2023 Candela Technologies Inc.
        """

    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=desc)

    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--host", "--mgr", default='localhost',
                        help='specify the GUI to connect to, assumes port 8080')

    parser.add_argument('--ssid', type=str, default='',
                        help='APPLY: SSID for Interop device WiFi connection')

    parser.add_argument('--crypt', '--enc', type=str, default='',
                        help='APPLY: Encryption for Interop device WiFi connection')

    parser.add_argument('--passwd', '--pw', type=str, default='',
                        help='APPLY: Password for Interop device WiFi connection')

    parser.add_argument('--ssid_2g', type=str, default='',
                        help='APPLY: 2G SSID for Interop device WiFi connection')

    parser.add_argument('--encryption_2g', type=str, default='',
                        help='APPLY: 2G Encryption for Interop device WiFi connection')

    parser.add_argument('--passwd_2g', type=str, default='',
                        help='APPLY: 2G Password for Interop device WiFi connection')

    parser.add_argument('--ssid_5g', type=str, default='',
                        help='APPLY: 5G SSID for Interop device WiFi connection')

    parser.add_argument('--encryption_5g', type=str, default='',
                        help='APPLY: 5G Encryption for Interop device WiFi connection')

    parser.add_argument('--passwd_5g', type=str, default='',
                        help='APPLY: 5G Password for Interop device WiFi connection')

    parser.add_argument('--ssid_6g', type=str, default='',
                        help='APPLY: 6G SSID for Interop device WiFi connection')

    parser.add_argument('--encryption_6g', type=str, default='',
                        help='APPLY: 6G Encryption for Interop device WiFi connection')

    parser.add_argument('--passwd_6g', type=str, default='',
                        help='APPLY: 6G Password for Interop device WiFi connection')

    parser.add_argument('--log_dur', '--ld', type=float, default=0,
                        help='LOG: Gather ADB logs for a duration of this many minutes')
    
    parser.add_argument('--config_wifi', action="store_true",
                        help='Specific this flag to do Wi-Fi connectivity on real devices')

    parser.add_argument('--server_ip', type=str, default='192.168.1.61',
                        help='Specific the server IP for the Interop App')

    parser.add_argument('--log_destination', '--log_dest',
                        help='LOG: the filename destination on the LF device where the log file should be stored'
                             'Give "stdout" to receive content as keyed text message')

    parser.add_argument('--help_summary', default=None, action="store_true",
                        help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    if(args.config_wifi):
        real_devices = RealDevice(manager_ip=args.host,
                                  server_ip=args.server_ip,
                                  ssid_2g=args.ssid_2g,
                                  passwd_2g=args.passwd_2g,
                                  encryption_2g=args.encryption_2g,
                                  ssid_5g=args.ssid_5g,
                                  passwd_5g=args.passwd_5g,
                                  encryption_5g=args.encryption_5g,
                                  ssid_6g=args.ssid_6g,
                                  passwd_6g=args.passwd_6g,
                                  encryption_6g=args.encryption_6g)
        asyncio.run(real_devices.query_all_devices_to_configure_wifi())
    else:
        obj = BaseInteropWifi(manager_ip=args.host,
                            port=8080,
                            ssid=args.ssid,
                            passwd=args.passwd,
                            encryption=args.crypt,
                            release="12",
                            screen_size_prcnt=0.4,
                            _debug_on=False,
                            _exit_on_error=False)
        z = obj.scan_results()
        print(z)


if __name__ == '__main__':
    main()