import re
import sys
import os
import importlib
import json
import argparse
import time
import logging
import numpy
import pandas as pd
import asyncio
import csv
import requests

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

logger = logging.getLogger(__name__)

class ADB_DEVICES(Realm):
    def __init__(self, lanforge_ip=None,
                 port=8080,
                 _debug_on=False,
                 ):
        super().__init__(lfclient_host=lanforge_ip,
                         debug_=_debug_on)
        
        self.lanforge_ip =lanforge_ip
        self.port = port
        # adb post url
        self.adb_post_url = '/cli-json/adb/'

        # adb get url
        self.adb_url = '/adb/'

    # stop app
    async def stop_app(self, port_list=[]):
        if (port_list == []):
            logger.info('Device list is empty')
            return

        data_list = []

        command = 'shell am force-stop com.candela.wecan'
        for port_data in port_list:

            data = {
                'shelf': 1,
                'resource': port_data["shelf"],
                'adb_id': port_data["serial"],
                'key':8,
                'adb_cmd': command
            }
            data_list.append(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, self.adb_post_url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # toggle wifi
    def set_wifi_state(self, port_list=[], state='enable'):
        if (port_list == []):
            logger.info('Port list is empty')
            return

        state = state.lower()
        if (state != 'enable' and state != 'disable'):
            logger.warning('State argument should be either enable or disable')
            return

        command = 'shell svc wifi {}'.format(state)

        data_list = []
        for port_data in port_list:
            
            data = {
                'shelf': 1,
                'resource': port_data["shelf"],
                'adb_id': port_data["serial"],
                'key':8,
                'adb_cmd': command
            }
            data_list.append(data)
                        
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, self.adb_post_url, data) for data in data_list]

    # Forget Networks
    async def forget_all_networks(self, port_list=[]):
        print("FORGET ALL NETWORKS ANDROID")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        url = 'http://{}:{}/cli-json/clear_wifi_profiles'.format(self.lanforge_ip, self.port)

        data_list = []
        for port_data in port_list:

            data = {
                'shelf': 1,
                'resource': port_data["shelf"],
                'id': port_data["serial"],
                'type': 'adb'
            }
            data_list.append(data)
        print("DATA LIST: ",data_list)
        print("URL: ",url)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, url, data) for data in data_list]
        results = await asyncio.gather(*tasks)
    
    # Configure Wifi ADB
    async def configure_wifi(self, port_list=[]):
        print("CONFIGURE ANDROIDS")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        data_list_1 = []

        for port_data in port_list:
            print(port_data)
            curr_ssid, curr_passwd, curr_encryption, curr_eap_method, curr_eap_identity , server_ip = port_data["ssid"], port_data["passwd"], port_data["enc"], port_data["eap_method"], port_data["eap_identity"], port_data["server_ip"]
            
            username = port_data["user-name"]
            # adding enable wifi option for android clients as a prerequisite step by-default
            command = 'shell svc wifi enable'
            data = {
                        'shelf': 1,
                        'resource': port_data["shelf"],
                        'adb_id': port_data["serial"],
                        'key':8,
                        'adb_cmd': command
                    }
            data_list_1.append(data)

            if (username is None):
                # logger.warning('The device with serial {} not found'.format(serial))
                username = \
                self.get('http://{}:{}/adb/1/1/{}'.format(self.lanforge_ip, self.port, port_data["serial"])).json()['devices'][
                    'user-name']
            # check if the encryption is personal
            
            # if the encryption is enterprise
            if (port_data["ieee80211"]==True):
                if curr_encryption=="wpa_enterprise":
                    curr_encryption="wpa-ent"
                if curr_encryption=="wpa2_enterprise":
                    curr_encryption="wpa2-ent"
                if curr_encryption=="wpa3_enterprise":
                    curr_encryption="wpa3-ent"
                data = {
                    'shelf': 1,
                    'resource': port_data["shelf"],
                    'adb_id': port_data["serial"],
                    'key':8,
                    'adb_cmd': 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {} --es eap_method {} --es eap_user {} --es eap_passwd {}'.format(
                        username, server_ip, curr_ssid, curr_passwd, curr_encryption , curr_eap_method,
                        curr_eap_identity, curr_passwd)
                }
            else:
                data = {
                    'shelf': 1,
                    'resource': port_data["shelf"],
                    'adb_id': port_data["serial"],
                    'key':8,
                    'adb_cmd': 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {}'.format(
                        username, server_ip, curr_ssid, curr_passwd, curr_encryption)
                }
            data_list.append(data)
        print("DATA LIST: ",data_list)
        print("DATA-----------: ",data_list_1)
        print("URL: ",self.adb_post_url)
        # execution for enabling wifi
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, self.adb_post_url, data) for data in data_list_1]
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, self.adb_post_url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)
    
    # Reboot ADB Devices
    async def reboot_android(self, port_list=[], state='enable'):
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
    
            data = {
                'shelf': 1,
                'resource': port_data["shelf"],
                'adb_id': port_data["serial"],
                'key':8,
                'adb_cmd': "reboot"
            }
            data_list.append(data)
                        
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.json_post, self.adb_post_url, data) for data in data_list]
        results = await asyncio.gather(*tasks)

    # fetch all android devices
    def get_devices(self):

        # fetching all devices from interop tab
        interop_tab_data = self.json_get(self.adb_url)["devices"]
        devices_data = []
        #print("interop data",interop_tab_data)
        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if (type(interop_tab_data) is dict):
            device = {}

            name = interop_tab_data['name']

            if (interop_tab_data['phantom']):
                logger.warning(
                    '{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(name))

            else:

                _, clustered_res, serial = name.split('.')

                # parameters for adb post request
                try:
                    shelf, resource = interop_tab_data['resource-id'].split('.')
                except:
                    # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                    shelf, resource = '', ''
                device["serial"] = serial
                device["shelf"] = clustered_res
                device["eid"] = interop_tab_data['resource-id']
                device["resource"] = resource
                device["os"] = interop_tab_data['device-type']
                device["user-name"] = interop_tab_data['user-name']
                device['type'] = 'adb'
                devices_data.append(device)

        else:
            for device_data in interop_tab_data:
                device = {}
                for name, data in device_data.items():
                    if (data['phantom']):
                        logger.warning(
                            '{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(
                                name))
                        continue

                    _, clustered_res, serial = name.split('.')

                    try:
                        shelf, resource = data['resource-id'].split('.')
                    except:
                        # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                        shelf, resource = '', ''
                    device["serial"] = serial
                    device["shelf"] = clustered_res
                    device["eid"] = data['resource-id']
                    device["resource"] = resource
                    device["os"] = data["device-type"]
                    device["user-name"] = data["user-name"]
                    device['type'] = 'adb'
                    
                    devices_data.append(device)
        return (devices_data)

    def get_serial_from_port(self, port_list=[]):

        if (port_list == []):
            logger.info('Androids list is empty')
            return

        devices_data = []
        url = 'http://{}:{}/adb/'.format(self.lanforge_ip, self.port)
        resource_response = requests.get(url)
        android_devices = resource_response.json()['devices']

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if (type(android_devices) is dict):
            for port_id in port_list:
                shelf, resource, port = port_id.split('.')
                resource_id = '{}.{}'.format(shelf, resource)
                device_name = android_devices['name']
                if (resource_id == android_devices['resource-id']):
                    device_serial = device_name.split('.')[2]
                    devices_data.append((shelf, resource, device_serial))
                    break
        else:
            for port_id in port_list:
                shelf, resource, port = port_id.split('.')
                resource_id = '{}.{}'.format(shelf, resource)
                for android_device in android_devices:
                    device_name, device_data = list(android_device.keys())[0], list(android_device.values())[0]
                    if (resource_id == device_data['resource-id']):
                        device_serial = device_name.split('.')[2]
                        devices_data.append((shelf, resource, device_serial))
                        continue
        return (devices_data)



class LAPTOPS(Realm):
    def __init__(self, lanforge_ip=None,
                 port=8080,
                 _debug_on=False,
                 ):
        super().__init__(lfclient_host=lanforge_ip,
                         debug_=_debug_on)
        
        self.lanforge_ip =lanforge_ip
        self.port = port

    def post_data(self, url, data):
        try:
            logger.info(data)
            response=requests.post(url, json=data)
            # response.raise_for_status()  # Raise an HTTPError for bad responses
            # print(response.status_code)
            # print(response.json())
        except Exception as e:
            print(e,data)
            # logger.error('Request failed for port {}'.format(data['port']))
            # method to get the station name from port manager
            # print("STOPPPP",url,data)

    # set encoding value
    def get_encoding(self,obj):
        encryption = obj.get("enc")
        print("SET ENCODING FOR LAPTOP")
        enc = 0
        if (encryption == 'open'):
            enc = 0
        elif (encryption=="owe"):
            enc = 562949953421312
        elif (encryption == 'wpa_personal' or encryption == 'psk' or encryption == 'wpa'):
            enc = 16
        elif (encryption == "wpa2_personal" or encryption == 'psk2' or encryption == 'wpa2'):
            enc = 1024
        elif (encryption == "wpa3_personal" or encryption == 'psk3' or encryption == 'wpa3'):
            enc = 1099511627776
        elif (encryption == "wpa_enterprise"):
            enc = 33554448
        elif (encryption == "wpa2_enterprise"):
            enc = 33555456
        elif (encryption == "wpa3_enterprise"):
            enc = 1099545182208
        elif (encryption=="owe_advanced"):
            enc = 564049498603520
        if encryption == "wpa_enterprise" or encryption == "wpa2_enterprise" or encryption == "wpa3_enterprise" or encryption=="owe_advanced":
            if obj.get("ieee80211u")==True:
                enc=enc+131072
            if obj.get("enable_pkc")==True:
                enc=enc+67108864
            if obj.get("bss_transition")==True:
                enc=enc+8796093022208
            if obj.get("power_save")==True:
                enc=enc+34359738368
            if obj.get("disable_ofdma")==True:
                enc=enc+35184372088832
            if obj.get("roam_ft_ds")==True:
                enc=enc+140737488355328

        return enc
    
    # remove station
    # NOTE this is only for Linux Laptops
    async def rm_station(self, port_list=[]):
        print("REMOVE STATION LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            if ('Lin' == port_data['os']):
                shelf, resource, sta_name = port_data['shelf'], port_data['resource'], port_data['sta_name']
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': sta_name
                }
                data_list.append(data)

        url = 'http://{}:{}/cli-json/rm_vlan'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)
        time.sleep(2)
    
    # add station
    async def add_station(self, port_list=[]): 
        print("ADD STATION LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            sta_name = port_data['sta_name']
            
            os = port_data['os']
            
            curr_ssid = port_data["ssid"]
            curr_passwd = port_data["passwd"]
            curr_enc = self.get_encoding(port_data)
            enterprise_status = port_data["ieee80211"]
            enable_80211w = port_data["ieee80211w"]

            if (os in ['Apple', 'Lin']):
                if enterprise_status==True:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        'mac': 'xx:xx:xx:::xx',
                        "ieee80211w" : enable_80211w,
                        'key': curr_passwd,

                    }
                else:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        'mac':'xx:xx:xx:::xx',
                        'key': curr_passwd,
                        "ieee80211w" : 1,

                    }
            else:
                if enterprise_status==True:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        "ieee80211w" : enable_80211w,
                        'key': curr_passwd,

                    }
                else:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        'key': curr_passwd,
                        "ieee80211w" : 1,
                    }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/add_sta'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)
        print(results)
        time.sleep(2)   
    # Set Wifi Extra
    async def set_wifi_extra(self, port_list=[]):
        print("SET WIFI EXTRA LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return        
        data_list = []
        
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            sta_name = port_data['sta_name']
            os = port_data['os']
            curr_passwd = port_data["passwd"]
            enterprise_status = port_data["ieee80211"]
            key_management = port_data["key_management"]
            pairwise = port_data["pairwise"]
            eap_method = port_data["eap_method"]
            eap_identity = port_data["eap_identity"]
            private_key = port_data["private_key"]
            ca_cert = port_data["ca_cert"]
            client_cert = port_data["client_cert"]
            pk_passwd = port_data["pk_passwd"]
            pac_file = port_data["pac_file"]
            # ieee80211u=port_data["ieee80211u"]
            # ieee80211w=port_data["ieee80211w"]
            # enable_pkc=port_data["enable_pkc"]
            # bss_transition=port_data["bss_transition"]
            # power_save=port_data["power_save"]
            # disable_ofdma=port_data["disable_ofdma"]
            # roam_ft_ds=port_data["roam_ft_ds"]



           
            if eap_method=="EAP-TTLS":
                eap_method="TTLS"
            if eap_method=="EAP-TLS":
                eap_method="TLS" 
            if eap_method=="EAP-PEAP":
                eap_method="PEAP"
            if eap_method=="EAP-PEAP":
                eap_method="PEAP" 
            if (enterprise_status==True and (os=='Win' or os=='Lin' or os=='Apple')):
                # os = port_data['os']
                # if (os in ['Lin']):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    "port":"wlan0",
                    "key_mgmt":key_management,
                    "pairwise":pairwise,
                    "group":pairwise,
                    "eap": eap_method,
                    "identity": eap_identity,
                    "password": curr_passwd,
                    "private_key" : private_key,
                    "ca_cert" : ca_cert,
                    "client_cert" : client_cert,
                    "pk_passwd": pk_passwd,
                    "pac_file" : pac_file,

                    # "ieee80211u":ieee80211u,
                    # "ieee80211w":ieee80211w,
                    # "enable_pkc":enable_pkc,
                    # "bss_transition":bss_transition,
                    # "power_save":power_save,
                    # "disable_ofdma":disable_ofdma,
                    #  "roam_ft_ds":roam_ft_ds
                }
            else:
                 data = {
                    'shelf': shelf,
                    'resource': resource,
                    "port":"wlan0",
                    "key_mgmt":"[BLANK]",
                    "pairwise":"[BLANK]",
                    "group":"[BLANK]",
                    "eap": "[BLANK]",
                    "identity": "[BLANK]",
                    "password": "[BLANK]",
                    "private_key" : "[BLANK]",
                    "ca_cert" : "[BLANK]",
                    "client_cert" : "[BLANK]",
                    "pk_passwd": "[BLANK]",
                    "pac_file" : "[BLANK]",
                    "phase1":"[BLANK]",  # outter auth
                    "phase2":"[BLANK]",  # inner aut
                     "pin":"[BLANK]",
                 }

            data_list.append(data)
                
        url = 'http://{}:{}/cli-json/set_wifi_extra'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        if len(data_list) < 1:
            print("No devices for set wifi extra")
            return
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]
        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)
    
    async def set_port_1(self, port_list=[]):
        print("SET PORT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': 0,
                    'interest': 8388610,
                    'mac': 'xx:xx:xx:*:*:xx'
                }
            else:
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    "report_timer": 1,
                    'current_flags': 0,
                    'interest': 92291074,
                }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/set_port'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # set port (enable DHCP)
    async def set_port(self, port_list=[]):
        print("SET PORT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    "report_timer": 1,
                    'current_flags': 2147483648,
                    'interest': 92291074,
                    'mac': 'xx:xx:xx:*:*:xx'
                }
            else:
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    "report_timer": 1,
                    'current_flags': 2147483648,
                    'interest': 92291074,
                }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/set_port'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # Reboot Laptops
    async def reboot_laptop(self, port_list=[]):
        print("REBOOT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']

            
            data = {
                    'shelf': shelf,
                    'resource': resource
                }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/reboot_os'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # Disconnect Wifi Laptops
    async def disconnect_wifi(self, port_list=[]):
        print("SET PORT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': 1,
                    'interest': 8388610,
                    'mac': 'xx:xx:xx:*:*:xx'
                }
            else:
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    "report_timer": 1,
                    'current_flags': 1,
                    'interest': 8388608,
                }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/set_port'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # Get all laptops devices
    def get_devices(self):

        # fetching all devices from Resource Manager tab
        response = self.json_get("/resource/all")

        resources = response['resources']

        # if there are no resources except LANforge in resource manager tab
        if (type(resources) is dict):
            return ([])

        resources_list = []
        for resource_data in resources:
            #print("resource_data",resource_data)
            port, resource = list(resource_data.keys())[0], list(resource_data.values())[0]

            # filtering LANforges from resources
            if (resource['ct-kernel']):
                continue

            # filtering Androids from resources
            if (resource['user'] != ''):
                continue

            # filtering phantom resources
            if (resource['phantom']):
                logger.info('The laptop on port {} is in phantom state.'.format(port))
                continue
            
            shelf, resource_id = port.split('.')
            hostname = resource_data[port]['hostname']
            #print("shelf=",shelf,"resource=",resource_id)
            sta_details = self.get_station_name(shelf=shelf, resource=resource_id)
            if not sta_details["radio_up"]:
                logger.info('The laptop on port {} has no wiphy port available.'.format(port))
                continue
            hw_version = resource['hw version']

            # fetching data for Windows
            if ('Win' in hw_version):
                resources_list.append({
                    'os': 'Win',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': sta_details['station_name'],
                    'sta_down' : sta_details['sta_down'],
                    'hostname': hostname,
                    'type':'laptop',
                    'report_timer': 1500,
                    'current_flags': 2147483648,
                    'interest': 16384
                })

            # fetching data for Linux
            elif ('Lin' in hw_version):
                resources_list.append({
                    'os': 'Lin',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': sta_details['station_name'] if sta_details['station_name'] else "sta0" ,
                    'sta_down' : sta_details['sta_down'] if sta_details['sta_down'] is not None else True,
                    'hostname': hostname,
                    'type':'laptop',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

            # fetching data for Mac
            elif ('Apple' in hw_version):
                resources_list.append({
                    'os': 'Apple',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': sta_details['station_name'],
                    'sta_down' : sta_details['sta_down'],
                    'hostname': hostname,
                    'type':'laptop',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

        return (resources_list)

    # Get laptops station names
    def get_station_name(self, shelf, resource):
        #shelf=1
        #resource=503
        url = '/ports/{}/{}/?fields=parent dev,phantom,down,alias'.format( shelf, resource)
        station_response = self.json_get(url)
        wiphy_non_phantom_found = False
        #print("+++++",station_response)
        if ('interfaces' in station_response.keys()):
            stations = station_response['interfaces']
            for station in stations:
                station_name, station_details = list(station.keys())[0], list(station.values())[0]
                if (station_details['parent dev'] != '' and not station_details['phantom']):
                    wiphy_non_phantom_found = True
                    return {"station_name":station_name.split('.')[2],"sta_down":station_details['down'],"radio_up":True}
                
            if not wiphy_non_phantom_found:
                for station in stations:
                    station_name, station_details = list(station.keys())[0], list(station.values())[0]
                    if (station_details['parent dev'] == '' and not station_details['phantom'] and station_details['alias'] == 'wiphy0'):
                        return {"station_name":None,"sta_down":None,"radio_up":True}
                return {"station_name":None,"sta_down":None,"radio_up":False}
        else:
            logging.error(
                'Malformed response. Response does not have interfaces data. Setting the station name to default i.e., wlan0')
            return {"station_name":"wlan0","sta_down":None,"radio_up":False}


class DeviceConfig(Realm):
    def __init__(self, lanforge_ip=None,
                 port=8080,file_name=None,
                 _debug_on=False,
                 
                 ):
        super().__init__(lfclient_host=lanforge_ip,
                         debug_=_debug_on)
        self.lanforge_ip=lanforge_ip
        self.port=port
        self.file_name=file_name
       

        # Objects for alptops and adb class  
        self.adb_obj = ADB_DEVICES(lanforge_ip=self.lanforge_ip)
        self.laptop_obj = LAPTOPS(lanforge_ip=self.lanforge_ip)
        
        # available devices
        self.all_available_devices = {}
        self.all_mapped_devices = {}
        
        # groups
        self.groups = {}
        
        # selected
        self.already_added = {}
        self.selected_devices = []

        # wifi profiles
        self.profile_data = []

    def get_all_devices(self,adb=True,laptops=True):
        adb_devices = []
        laptop_devices = []
        if adb:
            adb_devices = self.adb_obj.get_devices()
        if laptops:
            laptop_devices = self.laptop_obj.get_devices()
        self.all_devices = adb_devices+laptop_devices
        print("All devices",self.all_devices)
        return(adb_devices+laptop_devices)
    
    def map_all_devices(self):
        if not self.all_devices:
            return self.all_mapped_devices
        for index, device in enumerate(self.all_devices):
            map_device = {}
            if device["type"] == 'adb':
                map_device["serial"] = device["serial"]
            elif device["type"] == 'laptop':
                map_device["serial"] = device["hostname"]

            map_device["os"] = device["os"]
            map_device["resource"] = device["resource"]
            self.all_mapped_devices[str(index)] = map_device
        #print("MAPPED",self.all_mapped_devices)
        return self.all_mapped_devices

    def read_groups_file(self,flag=0):
        # Read CSV file into DataFrame
        if(flag==1):
            file_name='groups_demo.csv'
        else:
            file_name=self.file_name+'.csv'
        try:
            df = pd.read_csv(file_name)
        except:
            print("csv is empty or malformed")
            return {}
        df = df.where(pd.notna(df), None)
        data = {col: df[col].dropna().apply(lambda x: str(int(x)) if isinstance(x, float) else str(x)).tolist() for col in df.columns}
        print("==============================================")
        return data
    
    def get_all_available_devices(self):
        dataset = self.groups
        already_added = {}
        not_added_mapped_devices = {}
        for g_name,g_values in dataset.items():
            for val in g_values:
                if not already_added.get(val):
                    already_added[val] = [g_name]
                else:
                    already_added[val].append()
        
        idx = 1
        for obj in self.all_mapped_devices.values():
            if obj["serial"] not in already_added:
                not_added_mapped_devices[str(idx)] = obj
                idx += 1
        self.already_added = already_added
        self.all_available_devices = not_added_mapped_devices
        return self.all_available_devices
    
    def take_input(self,type = "add"):
        if type == "add":
            group_data_indexed = {}
            msg="Enter the groups to created ex(gro1=1,2,3 gro2=6,7):"
            group_input = input(msg)
            group_input = group_input.strip().split(" ")
            for groupinfo in group_input:
                temp_group = groupinfo.split("=")
                g_name= temp_group[0]
                g_values=temp_group[1].split(",")
                group_data_indexed[g_name]=g_values
            return group_data_indexed
        elif type == "remove":
            msg="Enter the groups to delete ex(gro1,grop2  or 'all' to delete all groups):"
            remove_input = input(msg)
            remove_input = remove_input.strip().split(",")
            return remove_input
        elif type == "edit":
            msg="Enter the edit config ex(grooup1:add=1,2,3 rem=7,9,6):"
            edit_input = input(msg)
            edit_input = edit_input.strip().split(":")
            edit_obj = {}
            g_name= edit_input[0]
            edit_obj[g_name]={"additions":[],"deletions":[]}
            edit_config = edit_input[1].split(" ")
            for operation in edit_config:
                if "add=" in operation:
                    edit_obj[g_name]["additions"] = operation.split("=")[1].split(",")
                elif "rem=" in operation:
                    edit_obj[g_name]["deletions"] = operation.split("=")[1].split(",")

            return edit_obj

    def device_csv_file(self):
        file_name = 'device.csv'
        columns = ['DeviceList', 'PingPacketLoss', 'L3_TCP_UL','L3_TCP_DL','L3_TCP_BiDi','L3_UDP_UL','L3_UDP_DL','L3_UDP_BiDi','Videostreaming','RealBrowser','HTTP','FTP','PortReset','Roaming']

        if not os.path.exists(file_name):
           
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(columns)
            print(f'{file_name} created with columns: {columns}')
        else:
            print(f'{file_name} already exists, no need to create.')
        
        adbresponse=self.adb_obj.get_devices()
        resource_manager=self.laptop_obj.get_devices()
        device_csv_list=[]
        for adb in adbresponse:
            device_csv_list.append(adb['serial'])
        for lap in resource_manager:
            device_csv_list.append(lap['hostname']) 
        #print("adb+laptop",adbresponse,resource_manager,device_csv_list)
        with open(file_name, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)  # Read all the rows

        # Get the header and the existing data
        header = rows[0]
        existing_data = rows[1:]
            
        existing_devices = {row[0] for row in existing_data}  
        for device in device_csv_list:
            if device not in existing_devices: 
                new_row = [device] + [''] * (len(header) - 1)  
                existing_data.append(new_row)
     
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write the header first
            writer.writerow(header)
            
            # Write all existing rows plus the new rows
            writer.writerows(existing_data)
        # input()

    def update_device_csv(self,test='',device_dict={}):
        adbresponse=self.adb_obj.get_devices()
        resource_manager=self.laptop_obj.get_devices()
        device_csv={}
        #print("11111111111111",adbresponse,"22222222222222",resource_manager)
        for adb in adbresponse:
            if(adb['eid'] in device_dict.keys()):
                device_csv[adb['serial']]=device_dict[adb['eid']]
        for lap in resource_manager:
            if(lap['shelf']+'.'+lap['resource'] in device_dict.keys()):
                device_csv[lap['hostname']]=device_dict[lap['shelf']+'.'+lap['resource']]
       # print("dfopikJHGFDkl;",device_csv)
                
        file_name = 'device.csv'
        #print(test,device_csv)
        # Read the CSV file
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            fieldnames = reader.fieldnames
        for row in rows:
            device = row['DeviceList']
            #print(row)  
            if device in device_csv.keys():
                row[test] = device_csv[device]  
        with open(file_name, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(rows) 

        print("CSV updated successfully.")

    def update_groups_file(self,input_obj,type = "add",extra_obj = None):
        file_name = args.file_name+'.csv'
        final_data_set = self.groups
        already_added = self.already_added
        inserted = []
        notinserted = []
        if type == "add":
            group_data_indexed = input_obj
            print(group_data_indexed)
            for g_name,g_values in group_data_indexed.items():
                print(g_name,g_values)
                final_data_set[g_name] = []
                for index in g_values:
                    if index in self.all_available_devices:
                        if index not in inserted:
                            final_data_set[g_name].append(self.all_available_devices[index]['serial'])
                            inserted.append(index)
                            already_added[self.all_available_devices[index]['serial']] = [g_name]
                        else:
                            print("{} is already inserted in {} hence not inculded in group {}".format(index,already_added[self.all_available_devices[index]['serial']],g_name))
                    else:
                        print("{} S.No is not found in the list.Excluding it from group {}".format(index,g_name))
                        notinserted.append(index)
        elif type == "remove":
            removal_groups_list = input_obj
            if 'all' in removal_groups_list:
                final_data_set = {}
                already_added = {}
                print("Deleted all groups")
            else:
                for g_name in removal_groups_list:
                    rem=final_data_set.pop(g_name,None)
                    if rem:
                        for val in rem:
                            if val in already_added:
                                already_added.pop(val,None)

                        print('{} group is removed.'.format(g_name))
                    else:
                        print('Unable to remove {} group.'.format(g_name))

        elif type == "edit":
            edit = input_obj
            df = extra_obj
            for edit_obj in edit:
                g_name = edit_obj
                add_idx = edit[edit_obj]["additions"]
                rem_idx = edit[edit_obj]["deletions"]
                
                # removal
                for index in rem_idx:
                    index=int(index)
                    if df.loc[index][g_name]:
                        serial = df.loc[index][g_name]
                        final_data_set[g_name].remove(serial)
                        already_added.pop(serial,None)
                        print("{} is removed from group {}".format(serial,g_name))
                    else:
                        print("{} index is not found in group {}".format(index,g_name))
                # addition
                for index in add_idx:
                    if index in self.all_available_devices:
                        if index not in inserted:
                            final_data_set[g_name].append(self.all_available_devices[index]['serial'])
                            inserted.append(index)
                            already_added[self.all_available_devices[index]['serial']] = [g_name]
                        else:
                            print("{} is already inserted in {} hence not inculded in group {}".format(index,already_added[self.all_available_devices[index]['serial']],g_name))
                    else:
                        print("{} S.No is not found in the list.Excluding it from group {}".format(index,g_name))
                        notinserted.append(index)

        print("====================================================")
        self.groups = final_data_set
        df=pd.DataFrame.from_dict(final_data_set, orient='index').transpose()
        df.to_csv(file_name, index=False)

    def display_groups(self,data):
        if len(data)==0:
            print("No groups to display")
            return None
        # Find the maximum length of lists
        max_length = max(len(v) for v in data.values())
        # Create a DataFrame with empty strings for missing values
        df = pd.DataFrame({k: v + [''] * (max_length - len(v)) for k, v in data.items()})
        # Display the DataFrame
        print(df)
        return df

    def initiate_group(self,flag=0):
        self.get_all_devices() #all devices
        self.map_all_devices() #map all devices
        self.groups=self.read_groups_file(flag) # get all created groups
        self.get_all_available_devices() #map all not added deviecs
    
    def get_groups_devices(self,data=None):
        data_object = []
        if data:
            selected_group = {}
            print("===",self.groups)

            for g_name,g_values in self.groups.items():
                if g_name in data:
                    print(g_name,data)
                    selected_group[g_name] = g_values
                    print("Selected group",selected_group)
                    for obj in self.all_devices:
                        if obj["type"] == "adb" and obj["serial"] in g_values:
                            temp = obj.copy()
                            temp["group_name"] = g_name
                            data_object.append(temp)
                            print("DO",data_object)
                        elif obj["type"] == "laptop" and obj["hostname"] in g_values:
                            temp = obj.copy()
                            temp["group_name"] = g_name
                            data_object.append(temp)
                    print("Data object",data_object)
            print("Following are the selected groups : ")
            self.display_groups(data=selected_group)
        else:
            print("Following are the groups available") 
            self.display_groups(data=self.groups)
            print("groups",self.groups)
            for g_name,g_values in self.groups.items():
                for obj in self.all_devices:
                    if obj["type"] == "adb" and obj["serial"] in g_values:
                        temp = obj.copy()
                        temp["group_name"] = g_name
                        data_object.append(temp)
                    elif obj["type"] == "laptop" and obj["hostname"] in g_values:
                        temp = obj.copy()
                        temp["group_name"] = g_name
                        data_object.append(temp)
        self.selected_devices = data_object
        print("SELECTED",self.selected_devices)
        return self.selected_devices
  
    def create_profile(self,data=None,delete_profiles=None):
        profile_conf = []
        if data:
            # Regular expression to match each profile
            profile_pattern = re.compile(r'(\w+)=<([^>>]*[^,]+)>')

            # Regular expression to extract key-value pairs
            kv_pattern = re.compile(r'(\w+)=([^><]+)')
            # Extract all profiles
            
            pass_pattern = re.compile(r'><passwd\s(\w+)')
            encrypt_pattern=re.compile(r'><enc\s(\w+)')
            eap_method_pattern = re.compile(r'><eap_method\s([A-Za-z0-9_-]+)')
            eap_identity_pattern=re.compile(r'><eap_identity\s(\w+)')
            ieee80211w_pattern=re.compile(r'><ieee80211w\s(\w+)')
            key_management_pattern=re.compile(r'><key_management\s(\w+)')
            pairwise_pattern=re.compile(r'><pairwise\s(\w+)')
            private_key_pattern=re.compile(r'><private_key\s(\w+)')
            ca_cert_pattern=re.compile(r'><ca_cert\s(\w+)')
            client_cert_pattern=re.compile(r'><client_cert\s(\w+)')
            pk_passwd_pattern=re.compile(r'><pk_passwd\s(\w+)')
            pac_file_pattern=re.compile(r'><pac_file\s(\w+)')

            


# Use re.search to find the first match
            profile_matches = profile_pattern.findall(data)
            print("MATCH",profile_matches)
            for profile_name, profile_details in profile_matches:
                # Extract key-value pairs for each profile
                match = pass_pattern.findall(profile_details)[0]
                encrypt_match=encrypt_pattern.findall(profile_details)[0]
                eap_method_match=eap_method_pattern.findall(profile_details)
                eap_identity_match=eap_identity_pattern.findall(profile_details)
                ieee80211w_match=ieee80211w_pattern.findall(profile_details)
                key_management_match=key_management_pattern.findall(profile_details)
                pairwise_match=pairwise_pattern.findall(profile_details)
                private_key_match=private_key_pattern.findall(profile_details)
                ca_cert_match=ca_cert_pattern.findall(profile_details)
                client_cert_match=client_cert_pattern.findall(profile_details)
                pk_passwd_match=pk_passwd_pattern.findall(profile_details)
                pac_file_match=pac_file_pattern.findall(profile_details)
                

                
                details = dict(kv_pattern.findall(profile_details))

                print("details",details)
                details["ieee80211u"]=True if("<ieee80211u>" in profile_details+'>') else False
                details["ieee80211"]=True if("<ieee80211>" in profile_details+'>') else False
                details["enable_pkc"]=True if("<enable_pkc>" in profile_details+'>') else False
                details["bss_transition"]=True if("<bss_transition>" in profile_details+'>') else False
                details["power_save"]=True if("<power_save>" in profile_details+'>') else False
                details["disable_ofdma"]=True if("<disable_ofdma>" in profile_details+'>') else False
                details["roam_ft_ds"]=True if("<roam_ft_ds>" in profile_details+'>') else False
                details["pairwise"]=pairwise_match[0] if("<pairwise " in profile_details) else ''
                details["private_key"]=private_key_match[0] if("<private_key " in profile_details) else ''
                details["ca_cert"]=ca_cert_match[0] if("<ca_cert " in profile_details) else ''
                details["client_cert"]=client_cert_match[0] if("<client_cert " in profile_details) else ''
                details["pk_passwd"]=pk_passwd_match[0] if("<pk_passwd " in profile_details) else ''
                details["pac_file"]=pac_file_match[0] if("<pac_file " in profile_details) else ''

                details["key_management"]=key_management_match[0] if("<key_management " in profile_details) else 'DEFAULT'
                details["ieee80211w"]=ieee80211w_match[0] if("<ieee80211w " in profile_details) else int(1)
                details["eap_identity"]=eap_identity_match[0] if("<eap_identity " in profile_details) else ''
                details["eap_method"]=eap_method_match[0] if("<eap_method " in profile_details) else 'DEFAULT'
                details["server_ip"]=self.lanforge_ip
                details["enc"]=encrypt_match
                details["passwd"]=match
                details["Profile"] = profile_name
                profile_conf.append(details)
                print(profile_conf)
        elif delete_profiles:
            print("Deleting profiles")
        else:
            print("No Profile data is provided")
            return
        self.create_profile_file(profile_conf,key_field='Profile',delete_key=delete_profiles)   

    def create_profile_file(self,new_data, key_field, delete_key=None):
        
        file_path = "profile.csv"
        # Convert new_data to DataFrame
        try:
            df_new = pd.DataFrame(new_data)
        except ValueError as e:
            raise ValueError("Invalid data format for new_data. Expected a list of dictionaries.") from e
        
        # Check if the file exists and read the existing data
        if os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
        else:
            # Create an empty DataFrame with the same columns as new_data
            df_existing = pd.DataFrame(columns=df_new.columns)
        
        # Handle deletion if delete_key is provided
        if delete_key is not None:
            if key_field not in df_existing.columns:
                raise ValueError(f"The specified key field '{key_field}' does not exist in the existing data.")
            df_existing = df_existing[~df_existing[key_field].isin(delete_key)]
         
        if len(new_data)>0:
            # Update existing data with new data
            df_existing = df_new.set_index(key_field).combine_first(df_existing.set_index(key_field)).reset_index()

        # Write the updated DataFrame to CSV
        df_existing.to_csv(file_path, index=False)
        return df_existing
    def display_profiles(self):
        file_path = "profile.csv"
        headers = ['Profile', 'ssid', 'enc', 'passwd' ]
        if not os.path.isfile(file_path):
            print(f"{file_path} does not exist")
        else:
            df = pd.read_csv(file_path)
            df = df.where(pd.notnull(df), None)
            df = df.applymap(lambda x: None if x == "" else x)
            json_data = df.set_index('Profile').to_dict(orient='index')
            self.profile_data = json_data
            data = [{key: json_data[key]['ssid']} for key in json_data.keys()]
            df = pd.DataFrame(data)
            combined_row = df.apply(lambda x: x.dropna().iloc[0], axis=0)
            result_df = pd.DataFrame([combined_row])
            print(result_df)
            return result_df
    def get_profiles(self,data=[],flag=0):
        if(flag==1):
            print("IN get profilesss")
            file_path = "profile_demo.csv"
        else:
            file_path="profile.csv"
        # Initialize the CSV file with headers if it does not exist
        headers = ['Profile', 'ssid', 'enc', 'passwd' ]
        # Check if the CSV file exists
        if not os.path.isfile(file_path):
            # Create the CSV file with predefined headers
            df = pd.DataFrame(columns=headers)
            df.to_csv(file_path, index=False)
            print(f"Created CSV file {file_path} with headers {headers}")
        else:
            print(f"CSV file {file_path} already exists.")
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Convert NaN to None
        df = df.where(pd.notnull(df), None)
    
        # Replace empty strings with None
        df = df.applymap(lambda x: None if x == "" else x)

        json_data = df.set_index('Profile').to_dict(orient='index')
        
        self.profile_data = json_data
        print("proffff data",self.profile_data)
        if not data:
            return json_data
        else:
            print("--------",data)
            filtered_profiles = {key: json_data[key] for key in data if key in json_data}
            print("FPPPP",filtered_profiles)
            return filtered_profiles or None    

   

    async def connectivity(self,config=None,disconnect=False,reboot=False,device_list=None,wifi_config=None,flag=0):
        group_device = []
        selected_adb_devices = []
        selected_laptop_devices = []

        configured_devices = []
        not_configured_devices = []

        if config:
            group_names = list(config.keys())
            profile_names = list(config.values())
            
            print("CONFIG",group_names,profile_names)
            if len(group_names) != len(profile_names):
                print("Wrong config for connecticity")
                return
            
            group_device = self.get_groups_devices(group_names)
            if(flag==1):
                profiles = self.get_profiles(profile_names,flag)
            else:
                profiles=self.get_profiles(profile_names)
            print("+++++",group_device,profiles)
            
            for device_obj in group_device:
                # TODO : to check if device is available in system or not
                maped_group = device_obj["group_name"]
            
                device_obj["ssid"] = profiles[config[maped_group]].get("ssid")
                device_obj["passwd"] = profiles[config[maped_group]].get("passwd")
                device_obj["enc"] = profiles[config[maped_group]].get("enc")
                device_obj["eap_method"] = profiles[config[maped_group]].get("eap_method")
                device_obj["eap_identity"] = profiles[config[maped_group]].get("eap_identity")
                device_obj["ieee80211"] = profiles[config[maped_group]].get("ieee80211")
                if device_obj["type"] == "laptop":
                    device_obj["ieee80211u"] = profiles[config[maped_group]].get("ieee80211u")
                    device_obj["ieee80211w"] = profiles[config[maped_group]].get("ieee80211w")
                    device_obj["enable_pkc"] = profiles[config[maped_group]].get("enable_pkc")
                    device_obj["bss_transition"] = profiles[config[maped_group]].get("bss_transition")
                    device_obj["power_save"] = profiles[config[maped_group]].get("power_save")
                    device_obj["disable_ofdma"] = profiles[config[maped_group]].get("disable_ofdma")
                    device_obj["roam_ft_ds"] = profiles[config[maped_group]].get("roam_ft_ds")
                    device_obj["key_management"] = profiles[config[maped_group]].get("key_management")
                    device_obj["pairwise"] = profiles[config[maped_group]].get("pairwise")
                    device_obj["private_key"] = profiles[config[maped_group]].get("private_key")
                    device_obj["ca_cert"] = profiles[config[maped_group]].get("ca_cert")
                    device_obj["client_cert"] = profiles[config[maped_group]].get("client_cert")
                    device_obj["pk_passwd"] = profiles[config[maped_group]].get("pk_passwd")
                    device_obj["pac_file"] = profiles[config[maped_group]].get("pac_file")

                    selected_laptop_devices.append(device_obj)
                else:
                    device_obj["server_ip"] = profiles[config[maped_group]].get("server_ip")
                    selected_adb_devices.append(device_obj)
        elif device_list and wifi_config:
            # based on the basis of just device list
            for device_obj in self.all_devices:
                #print("device obj",device_obj)
                device_obj["ssid"] = wifi_config.get("ssid")
                device_obj["passwd"] = wifi_config.get("passwd")
                device_obj["enc"] = wifi_config.get("enc")
                print("after",device_obj)
                if device_obj.get("serial") in device_list or device_obj.get("hostname") in device_list or (device_obj.get("shelf")+'.'+device_obj.get("resource")) in device_list:
                    
                    device_obj["ieee80211"] = wifi_config.get("ieee80211")
                    device_obj["eap_method"] = wifi_config.get("eap_method")
                    device_obj["eap_identity"] = wifi_config.get("eap_identity")
                    if device_obj["type"] == "laptop":
                        
                        device_obj["ieee80211u"] = wifi_config.get("ieee80211u")
                        device_obj["ieee80211w"] = wifi_config.get("ieee80211w")
                        device_obj["enable_pkc"] = wifi_config.get("enable_pkc")
                        device_obj["bss_transition"] = wifi_config.get("bss_transition")
                        device_obj["power_save"] = wifi_config.get("power_save")
                        device_obj["disable_ofdma"] = wifi_config.get("disable_ofdma")
                        device_obj["roam_ft_ds"] = wifi_config.get("roam_ft_ds")
                        device_obj["key_management"] = wifi_config.get("key_management")
                        device_obj["pairwise"] = wifi_config.get("pairwise")
                        device_obj["private_key"] = wifi_config.get("private_key")
                        device_obj["ca_cert"] = wifi_config.get("ca_cert")
                        device_obj["client_cert"] = wifi_config.get("client_cert")
                        device_obj["pk_passwd"] = wifi_config.get("pk_passwd")
                        device_obj["pac_file"] = wifi_config.get("pac_file")

                        selected_laptop_devices.append(device_obj)
                    else:
                        print("CONSFGFFWDGIY",wifi_config)
                        device_obj["server_ip"] = wifi_config.get("server_ip")
                        selected_adb_devices.append(device_obj)
        else:
            print("No devices are slected for operation")
            return
        print("=====================available adb devices for config==============")
        print(selected_adb_devices)
        print("=========================available laptops for config=============")
        print(selected_laptop_devices)
        print("Following are the devices available for configuration")
        for device_obj in selected_adb_devices + selected_laptop_devices:
            print(device_obj.get("serial")) if device_obj["type"] == "adb" else print(device_obj.get("hostname"))
            
        if reboot==True:
            if(selected_adb_devices != []):
                await self.adb_obj.reboot_android(port_list=selected_adb_devices)
                time.sleep(5)
                
            if(selected_laptop_devices != []):
                await self.laptop_obj.reboot_laptop(port_list=selected_laptop_devices)
                time.sleep(5)
        if disconnect ==True:
            if(selected_adb_devices != []):
                await self.adb_obj.forget_all_networks(port_list=selected_adb_devices)
                time.sleep(10)
            if(selected_laptop_devices != []):
                await self.laptop_obj.disconnect_wifi(port_list=selected_laptop_devices)
                time.sleep(10)
        if reboot==False and disconnect ==False:
            if(selected_adb_devices != []):
                await self.adb_obj.stop_app(port_list=selected_adb_devices)
                #await self.adb_obj.forget_all_networks(port_list=selected_adb_devices)
                await self.adb_obj.configure_wifi(port_list=selected_adb_devices)
                
                if(selected_laptop_devices == []):  
                    print("WAITING FOR 120 seconds")
                    time.sleep(120)
            if(selected_laptop_devices != []):
                # if laptop['eap_method']!="" or laptop['eap_method']!= None or laptop['eap_method']!="NA":
                await self.laptop_obj.rm_station(port_list=selected_laptop_devices)
                time.sleep(10)
                #trial for making port up before configuration
                await self.laptop_obj.set_port_1(port_list=selected_laptop_devices)
                time.sleep(10)
                await self.laptop_obj.add_station(port_list=selected_laptop_devices)
                time.sleep(30)
                #check for enterprise for enterprise configuration

                await self.laptop_obj.set_wifi_extra(port_list=selected_laptop_devices)
                time.sleep(10)
                await self.laptop_obj.set_port(port_list=selected_laptop_devices)
                
                print("WAITING TOTAL 120 SECONDS FOR CONFIGURATION TO APPLY")
                time.sleep(120)
            self.monitor_connection(selected_adb_devices,selected_laptop_devices)
            


    def monitor_connection(self,selected_androids,selected_laptops):
        
        print("=====================berfore monitoring=========================")
        print(selected_androids,selected_laptops)
        def get_device_data(port_key,resource_key,port_data,resource_data):
            curr_device_data = {}
            for port_obj in port_data:
                if port_key in port_obj:
                    curr_device_data = port_obj[port_key]
                    for res_obj in resource_data:
                        if resource_key in res_obj:
                            curr_device_data.update(res_obj[resource_key])
                            return curr_device_data
        
        selected_t_devices = {}
        selected_devices = []
        
        adb_resources = self.json_get('/adb/')
        all_resources = self.json_get('/resource/all')["resources"]
        all_ports = self.json_get('/ports/all')["interfaces"]
        
        exclude_androids = []
        for android in selected_androids:
            res_empty=False
            device_id = android["serial"]
            resource_id = ""
            for device in adb_resources['devices']:
                device_key = list(device.values())[0]["_links"]
                resource_id = list(device.values())[0]["resource-id"]
                if "/adb/"+device_id == device_key:
                    if resource_id == "":
                        exclude_androids.append(android)
                        res_empty = True
                    break
            if res_empty:
                continue        
        
            curr_ssid = android["ssid"]


           # fetching port data for the android device
            current_android_port_data = get_device_data(port_data=all_ports,port_key=resource_id+".wlan0",resource_data=all_resources,resource_key=resource_id)
            
            if (current_android_port_data is None):
                exclude_androids.append(android)
                continue
            # checking if the android is connected to the desired ssid
            if (current_android_port_data['ssid'] != curr_ssid):
                logging.warning(
                    'The android with serial {} is not conneted to the given SSID {}. Excluding it from testing'.format(
                        android["serial"], curr_ssid))
                exclude_androids.append(android)
                continue
            if (current_android_port_data['down'] or current_android_port_data['phantom']):
                exclude_androids.append(android)
                continue
            # checking if the android is active or down
            if(current_android_port_data['ip'] == '0.0.0.0'):
                logging.warning('The android with serial {} is down. Excluding it from testing'.format(android["serial"]))
                exclude_androids.append(android)
                continue

            username = current_android_port_data["user"]

            temp = {}            
            temp["eid"] = resource_id
            temp["resource"] = resource_id.split(".")[1]
            temp["port_id"] = resource_id+".wlan0"
            temp["channel"] = current_android_port_data["channel"]
            temp["rssi"] = current_android_port_data["signal"]
            temp["mac"] = current_android_port_data['mac']
            temp["report_labels"] = '{} android {}'.format(resource_id+".wlan0", username)
            selected_devices.append(temp.copy())


            selected_t_devices[resource_id+".wlan0"] = {
                'hw version': android["os"],
                'MAC': current_android_port_data['mac']
            }
            
        # for android in exclude_androids:
        #     selected_androids.remove(android)
    
        # for laptops
        exclude_laptops = []
        for laptop in selected_laptops:
            
            curr_ssid = laptop["ssid"]

            # check SSID and IP values from port manager
            current_laptop_port_data = get_device_data(port_data=all_ports,port_key=f"{laptop['shelf']}.{laptop['resource']}.{laptop['sta_name']}",resource_data=all_resources,resource_key=f"{laptop['shelf']}.{laptop['resource']}")
            
            if(current_laptop_port_data is None):
                logging.warning(
                    'The laptop with port {}.{}.{} not found. Excluding it from testing'.format(laptop['shelf'],
                                                                                                laptop['resource'],
                                                                                                laptop['sta_name']))
                exclude_laptops.append(laptop)
                continue

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
            
            if (current_laptop_port_data['down'] or current_laptop_port_data['phantom']):
                exclude_laptops.append(laptop)
                continue
            if(laptop['os'] == 'Win') and current_laptop_port_data["gateway ip"] == "0.0.0.0":
                exclude_laptops.append(laptop)
                
            hostname = current_laptop_port_data['hostname']


            # adding port id to selected_device_eids
            current_resource_id = '{}.{}.{}'.format(laptop['shelf'], laptop['resource'], laptop['sta_name'])
            temp = {}
            temp["eid"] =  '{}.{}'.format(laptop['shelf'], laptop['resource'])
            temp["resource"] = laptop['resource']
            temp["port_id"]  =   current_resource_id    
            temp["report_labels"] = '{} {} {}'.format(current_resource_id, laptop['os'], hostname)
            temp["channel"] = current_laptop_port_data["channel"]
            temp["rssi"] = current_laptop_port_data["signal"]
            temp["mac"] =current_laptop_port_data["mac"]

            selected_devices.append(temp)

            selected_t_devices[current_resource_id] = {
                'MAC': current_laptop_port_data['mac']
            }
            if(laptop['os'] == 'Win'):
                selected_t_devices[current_resource_id]['hw version'] = 'Win'
            elif(laptop['os'] == 'Lin'):
                selected_t_devices[current_resource_id]['hw version'] = 'Lin'
            elif(laptop['os'] == 'Apple'):
                selected_t_devices[current_resource_id]['hw version'] = 'Mac'
            

        # for laptop in exclude_laptops:
        #     selected_laptops.remove(laptop)

        df = pd.DataFrame(data=selected_t_devices).transpose()
        print("dF--",df)
        print(selected_devices)
        return selected_devices
    
            



            


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        )
    
    parser.add_argument('--lanforge_ip', type=str, default='localhost',help='')
    parser.add_argument("--create_file",action="store_true")
    parser.add_argument('--file_name',type=str,default='',help='')
    parser.add_argument("--create_group", help='flag to use script to create a group', action="store_true")
    parser.add_argument("--get_groups", help='flag to use script to get the groups created', action="store_true")
    parser.add_argument('--remove_group',help='flags to use script to remove form groups',action="store_true")
    parser.add_argument("--update_group", help='flag to use script to update a group in group file', action="store_true")

    parser.add_argument("--profile_config",help="flag to use script to create a ssid profile file example\
                        'profilename1=<ssid=candela tech><passwd Openwiff><enc wpa2>',profilename2<ssid=Client_Connectivity><passwd=Something><enc=wpa3><eap_method=PEAP><eap_passwd=something>" ,type=str)
    parser.add_argument("--delete_profiles",type=str,help="To mention if any profile needs to be deleted, Ex=> --delete_profiles p1,p2,p3",default="")
    parser.add_argument("--create_profile",action="store_true")
    parser.add_argument("--connect_profile",action="store_true")
    args = parser.parse_args()
    obj = DeviceConfig(lanforge_ip=args.lanforge_ip,file_name=args.file_name)

    

    if args.create_file:
        #print(args.group_name+'.csv')
        if not os.path.exists(args.file_name+'.csv'):
            if args.file_name=='':
                print("--file_name argument is required")
            else:
                obj.initiate_group()
                displayed_dataframe=obj.display_groups(obj.groups)
                print(pd.DataFrame(obj.all_available_devices).T)
                edit_inp=obj.take_input("add")
                obj.update_groups_file(edit_inp,"add",extra_obj=displayed_dataframe)
        else:
            print(f"'{args.file_name}'The name already exists.")
    elif args.create_group:
        if args.file_name=='':
                print("--file_name argument is required")
        else:
            obj.initiate_group()
            displayed_dataframe=obj.display_groups(obj.groups)
            print(pd.DataFrame(obj.all_available_devices).T)
            edit_inp=obj.take_input("add")
            obj.update_groups_file(edit_inp,"add",extra_obj=displayed_dataframe)
    elif args.remove_group:
        obj.initiate_group()
        displayed_dataframe=obj.display_groups(obj.groups)
        edit_inp=obj.take_input("remove")
        obj.update_groups_file(edit_inp,"remove",extra_obj=displayed_dataframe)
    elif args.update_group:
        obj.initiate_group()
        print(pd.DataFrame(obj.all_available_devices).T)
        displayed_dataframe=obj.display_groups(obj.groups)
        edit_inp=obj.take_input("edit")
        obj.update_groups_file(edit_inp,"edit",extra_obj=displayed_dataframe)
    elif args.get_groups:
        obj.initiate_group()
        obj.display_groups(obj.groups)
    elif args.create_profile:
        print("creating groups")
        obj.create_profile(data=args.profile_config,delete_profiles=args.delete_profiles.strip().split(","))
    elif args.connect_profile:
        input_dict={}
        obj.initiate_group()
        grp_data=obj.display_groups(obj.groups)
        prof_data=obj.display_profiles()
        grp_profile=input("Enter the group and profile ex(group_name:profile_name,group2:prof2) :")
        group_names=grp_profile.split(',')
        for i in group_names:
            key,value=i.split(':')
            input_dict[key]=value
        asyncio.run(obj.connectivity(input_dict))
    
    

    print("=================================================================")
   
