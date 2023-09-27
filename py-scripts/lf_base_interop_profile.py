#!/usr/bin/env python3
"""
NAME: lf_base_interop_profile.py

PURPOSE:To use various functionality of LANforge Interop at function level

EXAMPLE:
$ ./lf_base_interop_profile.py --host 192.168.1.31 --ssid Airtel_9755718444_5GHz --passwd xyz --crypt psk2

NOTES:

#@TODO more functionality need to be added


TO DO NOTES:

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

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
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
        # print(out)
        final = out["devices"]
        value = []
        if type(final) == list:
            # print(len(final))
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            # print(keys_lst)
            for i, j in zip(range(len(keys_lst)), keys_lst):
                value.append(final[i][j]["name"])
        else:
            #  only one device is present
            value.append(final["name"])
        self.supported_devices_names = value
        print("List of all Available Devices Serial Numbers in Interop Tab:", self.supported_devices_names)
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
        # print("response", final)
        if type(final) == list:
            # print(len(final))
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            # print(keys_lst)
            for i, j in zip(range(len(keys_lst)), keys_lst):
                if j == device:
                    # print("Getting " + str(query) + " details for " + str(device) + " device.")
                    logging.info("Getting " + str(query) + " details for " + str(device) + " device.")
                    value = final[i][j][query]
        else:
            #  only one device is present
            value = final[query]
        return value

    # check list of adb devices are in phantom state or not if not return list of active devices
    def check_phantom(self):
        active_device = []
        for i in self.supported_devices_names:
            phantom = self.get_device_details(query="phantom", device=i)
            if not phantom:
                print("Device " + str(i) + " is active")
                logging.info("Device " + str(i) + " is active")
                active_device.append(i)
            else:
                print("Device " + str(i) + " is in phantom state")
                logging.info("Device " + str(i) + " is in phantom state")
        self.supported_devices_names = active_device
        return self.supported_devices_names

    # check if active devices are of expected release and return list of devices
    def check_sdk_release(self):
        devices = self.check_phantom()
        rel_dev = []
        print("Active Device list:", devices)
        for i in devices:
            release_ver = self.get_device_details(query="release", device=i)
            for j in self.release:
                if release_ver == j:
                    # check if the release is supported in supported sdk  version
                    if release_ver in self.supported_sdk:
                        print("The Device " + str(
                            i) + " has " + j + " sdk release, which is in available sdk versions list: %s" % self.supported_sdk)
                        # logging.info("device " + str(i) + " has " + j + " sdk release")
                        rel_dev.append(i)
                else:
                    print("The Device " + str(
                        i) + " has different sdk release, which is not in available sdk versions list: %s" % self.supported_sdk)
                    # logging.info("Device " + str(i) + " has different sdk release")
        self.supported_devices_names = rel_dev
        return self.supported_devices_names

    # launch ui
    def launch_interop_ui(self, device=None):
        if device is None:
            devices = self.check_sdk_release()
            print(devices)
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
            print(devices)
            logging.info(devices)
        else:
            devices = [device]
        if not (wifi == "enable" or wifi == "disable"):
            logging.warning("wifi arg value must either be enable or disable")
            raise ValueError("wifi arg value must either be enable or disable")
        cmd = "shell svc wifi " + wifi
        for i in devices:
            print(wifi + " wifi for " + i)
            logging.info(wifi + " wifi  " + i)
            self.post_adb_(device=i, cmd=cmd)

    # set username
    def set_user_name(self, device=None, user_name=None):
        print("Name of the device:", device)
        logging.info("device " + str(device))
        user_name_ = []
        if device is None:
            devices = self.check_sdk_release()
            print(devices)
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
                print("Modified adb device user-name:", user_name)
                logging.info(user_name)
            else:
                user_name_.append(user_name)
        print("Available Devices List:", devices)
        logging.info("devices " + str(devices))
        print("Modified USER-NAME List:", user_name_)
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
            print(devices)
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
            print(devices)
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
            print(devices)
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
            print(devices)
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
        print(lf_query_resource)
        print("\n Now validating Resource manager ports \n")
        if 'resources' in list(lf_query_resource):
            for i in range(len(list(lf_query_resource['resources']))):
                id = (list(list(lf_query_resource['resources'])[i])[0])
                resource = list(lf_query_resource['resources'])[i].get(id)["phantom"]
                print('The', id, 'port is in PHANTOM:-', resource)
                while resource:
                    print('Deleting the resource', id)
                    info = id.split('.')
                    req_url = "cli-json/rm_resource"
                    data = {
                        "shelf": int(info[0]),
                        "resource": int(info[1])
                    }
                    self.json_post(req_url, data)
                    break
        else:
            print("No phantom resources")

        lf_query_resource = self.json_get("/resource/all")
        print(lf_query_resource)
        # time.sleep(1)

    # get eid username and phantom state of resources from resource manager
    # output {'1.1': {'user_name': '', 'phantom': False}, '1.16': {'user_name': 'device_0', 'phantom': True}}
    def get_resource_id_phantom_user_name(self):
        lf_query_resource = self.json_get("/resource/all")
        print(lf_query_resource)
        keys = list(lf_query_resource.keys())
        if "resources" in keys:
            res = lf_query_resource["resources"]
            if type(res) is list:
                sec_key = []
                for i in res:
                    sec_key.append(list(i.keys()))
                new_list =[]
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
                print(loc_dict)
                return loc_dict
        else:
            print("No resources present")

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
            for i,z in zip(range(len(new_keys)), new_keys):
                if z == eid:
                    mac = resources['interfaces'][i][z]['ap']
                    print(mac)
                    return mac
        else:
            print("interfaces is not present")
        # print(resources["interfaces"].key())

    def get_log_batch_modify(self, device=None):
        eid = self.name_to_eid(device)
        if self.log_dur > 0:
            if not self.log_destination:
                raise ValueError("adb log capture requires log_destination")
        user_key = self.session.get_session_based_key()
        if self.debug:
            print("====== ====== destination [%s] dur[%s] user_key[%s] " %
                  (self.log_destination, self.log_dur, user_key))
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
        print(json_response)



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
            print("state is not present")
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
            print("ssid is not present")
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
            logging.info("yes")
            ind = z.index('"' + ssid + '"' + "\n")
            # print(z[271])
            m = z[ind:]
            print(m)
            logging.info(m)
            if "ConnectAttempt:" in m:
                connect_ind = m.index("ConnectAttempt:")
                connect_attempt = m[connect_ind + 1]
                print("connection attempts", connect_attempt)
                logging.info("connection attempts " + connect_attempt)
                return_dict["ConnectAttempt"] = connect_attempt
            if 'ConnectFailure:' in m:
                connect_fail_ind = m.index('ConnectFailure:')
                connect_failure = m[connect_fail_ind + 1]
                print("connection failure ", connect_failure)
                logging.info("connection failure " + connect_failure)
                return_dict["ConnectFailure"] = connect_failure
            if 'AssocRej:' in m:
                ass_rej_ind = m.index('AssocRej:')
                assocrej = m[ass_rej_ind + 1]
                print("association rejection ", assocrej)
                logging.info("association rejection " + assocrej)
                return_dict["AssocRej"] = assocrej
            if 'AssocTimeout:' in m:
                ass_ind = m.index('AssocTimeout:')
                asso_timeout = m[ass_ind + 1]
                print("association timeout ", asso_timeout)
                logging.info("association timeout " +  asso_timeout)
                return_dict["AssocTimeout"] = asso_timeout
        else:
            print(f"Given {ssid} ssid is not present in the 'ConnectAttempt', 'ConnectFailure', 'AssocRej', 'AssocTimeout' States")
            logging.info("ssid is not present")
        # print(return_dict)
        return return_dict

    # forget network based on the network id
    def forget_netwrk(self, device=None, network_id=None):
        separating_device_name = device.split(".")
        if network_id is None:
            network_id = ['0']
        else:
            network_id = network_id
        for ntwk_id in network_id:
            print(f"Forgetting network for {device} with network id : {ntwk_id}")
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
            print("Number of saved profiles:", len(values))
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
                 _debug_on=False,
                 _exit_on_error=False):
        super().__init__(lfclient_host=manager_ip,
                         debug_=_debug_on)
        self.manager_ip = manager_ip
        self.manager_port = port
        self.devices = []
        self.devices_data = {}
        self.selected_device_eids = []
        self.selected_devices = []
        self.selected_macs = []
        self.report_labels = []
        self.android = 0
        self.linux = 0
        self.windows = 0
        self.mac = 0
    
    # getting data of all real devices
    def get_devices(self):
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
    def query_user(self):
        print('The available real devices are:')
        # print('Port\t\thw version\t\t\tMAC')
        t_devices = {}
        for device, device_details in self.devices_data.items():
            # 'eid' and 'hw version' originally comes from resource data. Snuck into port data to make life easier
            t_devices[device_details['eid']] = {
                'Port Name': device,
                'hw version': device_details['hw version'],
                'MAC': device_details['mac']
            }
            # print('{}\t{}\t\t\t{}'.format(device, device_details['hw version'], device_details['mac']))
        df = pd.DataFrame(data=t_devices).transpose()
        print(df)

        self.selected_device_eids = input('Select the devices to run the test(e.g. 1.10,1.11): ').split(',')
        print('You have selected the below devices for testing')
        # print('Port\t\thw version\t\t\tMAC')
        selected_t_devices = {}
        for selected_device in self.selected_device_eids:
            for device, device_details in self.devices_data.items():
                if(selected_device + '.' in device):
                    selected_t_devices[device] = {
                        'Eid': selected_device,
                        'hw version': self.devices_data[device]['hw version'],
                        'MAC': self.devices_data[device]['mac']
                    }
                    self.selected_devices.append(device)
                    self.selected_macs.append(self.devices_data[device]['mac'])
                    self.report_labels.append('{} {} {}'.format(selected_device, [ 'Win' if 'Win' in self.devices_data[device]['hw version'] else 'Lin' if 'Lin' in self.devices_data[device]['hw version'] else 'Mac' if 'Mac' in self.devices_data[device]['hw version'] else 'android'][0], [ self.devices_data[device]['user'] if self.devices_data[device]['user'] != '' else self.devices_data[device]['hostname'] ][0])[:25])
                    if('Win' in 'Win' in self.devices_data[device]['hw version']):
                        self.windows += 1
                    elif('Lin' in 'Lin' in self.devices_data[device]['hw version']):
                        self.linux += 1
                    elif('Apple' in self.devices_data[device]['hw version']):
                        self.mac += 1
                    else:
                        self.android += 1
        df = pd.DataFrame(data=selected_t_devices).transpose()
        print(df)
        return [self.selected_devices, self.report_labels, self.selected_macs]

def main():
    desc = """standard library which supports different functionality of interop
        Operations: 
        *    Example of scan results: 
        lf_base_interop_profile.py --host 192.168.1.31 --ssid Airtel_9755718444_5GHz --passwd xyz --crypt psk2

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

    parser.add_argument('--log_dur', '--ld', type=float, default=0,
                        help='LOG: Gather ADB logs for a duration of this many minutes')

    parser.add_argument('--log_destination', '--log_dest',
                        help='LOG: the filename destination on the LF device where the log file should be stored'
                             'Give "stdout" to receive content as keyed text message')

    args = parser.parse_args()
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
