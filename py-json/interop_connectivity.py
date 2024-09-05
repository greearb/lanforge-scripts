#!/usr/bin/env python3

import logging
import sys
import asyncio
import requests
import time
from datetime import datetime
if (sys.version_info[0] != 3):
    logging.critical('This script requires Python3')
    exit()

logger = logging.getLogger(__name__)


# connectivity for Androids
class Android():
    def __init__(self,
                 lanforge_ip=None,
                 port=8080,
                 server_ip=None,
                 enable_wifi=None,
                 disconnect_devices=None,
                 reboot=None,
                 disable_wifi=None,
                 ssid_2g=None,
                 passwd_2g=None,
                 encryption_2g=None,
                 eap_method_2g=None,
                 eap_identity_2g=None,
                 ieee80211_2g=None,
                 key_management_2g=None,
                 pairwise_2g=None,
                 private_key_2g=None,
                 ca_cert_2g=None,
                 client_cert_2g=None,
                 pk_passwd_2g=None,
                 pac_file_2g=None,
                 ssid_5g=None,
                 passwd_5g=None,
                 encryption_5g=None,
                 eap_method_5g=None,
                 eap_identity_5g=None,
                 ieee80211_5g=None,
                 key_management_5g=None,
                 pairwise_5g=None,
                 private_key_5g=None,
                 ca_cert_5g=None,
                 client_cert_5g=None,
                 pk_passwd_5g=None,
                 pac_file_5g=None,
                 ssid_6g=None,
                 passwd_6g=None,
                 encryption_6g=None,
                 eap_method_6g=None,
                 eap_identity_6g=None,
                 ieee80211_6g=None,
                 key_management_6g=None,
                 pairwise_6g=None,
                 private_key_6g=None,
                 ca_cert_6g=None,
                 client_cert_6g=None,
                 pk_passwd_6g=None,
                 pac_file_6g=None,
                 debug=False):
        self.lanforge_ip = lanforge_ip
        self.port = port
        self.server_ip = server_ip  # upstream IP
        self.enable_wifi = enable_wifi
        self.disconnect_devices=disconnect_devices
        self.reboot=reboot
        self.disable_wifi = disable_wifi

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
        self.ieee80211_2g = ieee80211_2g
        self.key_management_2g = key_management_2g
        self.pairwise_2g = pairwise_2g
        self.private_key_2g = private_key_2g
        self.ca_cert_2g = ca_cert_2g
        self.client_cert_2g = client_cert_2g
        self.pk_passwd_2g = pk_passwd_2g
        self.pac_file_2g = pac_file_2g

        self.eap_method_5g = eap_method_5g
        self.eap_identity_5g = eap_identity_5g
        self.ieee80211_5g = ieee80211_5g
        self.key_management_5g = key_management_5g
        self.pairwise_5g = pairwise_5g
        self.private_key_5g = private_key_5g
        self.ca_cert_5g = ca_cert_5g
        self.client_cert_5g = client_cert_5g
        self.pk_passwd_5g = pk_passwd_5g
        self.pac_file_5g = pac_file_5g

        self.eap_method_6g = eap_method_6g
        self.eap_identity_6g = eap_identity_6g
        self.ieee80211_6g = ieee80211_6g
        self.key_management_6g = key_management_6g
        self.ieee80211_6g = ieee80211_6g
        self.pairwise_6g = pairwise_6g
        self.private_key_6g = private_key_6g
        self.ca_cert_6g = ca_cert_6g
        self.client_cert_6g = client_cert_6g
        self.pk_passwd_6g = pk_passwd_6g
        self.pac_file_6g = pac_file_6g

        

        self.min_supported_android_version = 10

        # adb post url
        self.post_url = 'http://{}:{}/cli-json/adb'.format(self.lanforge_ip, self.port)

        # adb get url
        self.adb_url = 'http://{}:{}/adb'.format(self.lanforge_ip, self.port)

    # request function to send json post request to the adb api
    def post_data(self, url, data):
        print("ANDROID API",url,data,datetime.now())
        try:
            # print(data)
            logger.info(data)
            response=requests.post(url, json=data)
            # response.raise_for_status()  # Raise an HTTPError for bad responses
            # print(response.status_code)
            # print(response.json())
        except Exception as e:
            print(e,data)
            # logger.error('Request failed for port {}'.format(data['adb_id']))
        # print("ANDROID API STOP",url,data,datetime.now())
    # stop app
    async def stop_app(self, port_list=[]):
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []

        command = 'shell am force-stop com.candela.wecan'
        for port_data in port_list:
            shelf, resource, serial, band = port_data
            data = {
                'shelf': 1,
                'resource': 1,
                'adb_id': serial,
                'key':8,
                'adb_cmd': command
            }
            data_list.append(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

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
            shelf, resource, serial, *extra  = port_data

    
            data = {
                'shelf': 1,
                'resource': 1,
                'adb_id': serial,
                'key':8,
                'adb_cmd': command
            }
            data_list.append(data)
                        
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

    async def reboot_android(self, port_list=[], state='enable'):
        if (port_list == []):
            logger.info('Port list is empty')
            return

        # state = state.lower()
        # if (state != 'enable' and state != 'disable'):
        #     logger.warning('State argument should be either enable or disable')
        #     return

        # command = 'shell svc wifi {}'.format(state)

        data_list = []
        for port_data in port_list:
            shelf, resource, serial, *extra  = port_data

    
            data = {
                'shelf': 1,
                'resource': 1,
                'adb_id': serial,
                'key':8,
                'adb_cmd': "reboot"
            }
            data_list.append(data)
                        
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]
        results = await asyncio.gather(*tasks)

    async def forget_all_networks(self, port_list=[]):
        print("FORGET ALL NETWORKS ANDROID")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        url = 'http://{}:{}/cli-json/clear_wifi_profiles'.format(self.lanforge_ip, self.port)

        data_list = []
        for port_data in port_list:
            shelf, resource, serial, *extra = port_data

            data = {
                'shelf': 1,
                'resource': 1,
                'id': serial,
                'type': 'adb'
            }
            data_list.append(data)
        print("DATA LIST: ",data_list)
        print("URL: ",url)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]
        results = await asyncio.gather(*tasks)
    # fetching the username from the interop tab
    def get_username(self, shelf, resource):

        port = '{}.{}'.format(shelf, resource)
        # fetching all devices data from interop tab
        interop_tab_data = requests.get(self.adb_url).json()['devices']

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if (type(interop_tab_data) is dict):
            name = interop_tab_data['name']
            if (interop_tab_data['resource-id'] == port):
                if (int(interop_tab_data['release'].split('.')[0]) < self.min_supported_android_version):
                    logger.warning(
                        'Android device {} having android version less {}. Some functions may not be supported.'.format(
                            interop_tab_data['user-name'], self.min_supported_android_version))
                return (interop_tab_data['user-name'])
        else:
            for interop_device in interop_tab_data:
                for name, data in interop_device.items():
                    if (data['resource-id'] == port):
                        # print(data,"LLLLLLLLLLLLLLLLLLLLLLl")
                        # if (int(data['release'].split('.')[0]) < self.min_supported_android_version):
                        #     logger.warning(
                        #         'Android device {} having android version less {}. Some functions may not be supported.'.format(
                        #             data['user-name'], self.min_supported_android_version))
                        return (data['user-name'])
    #configuring wifi for androids
    async def configure_wifi(self, port_list=[]):
        print("CONFIGURE ANDROIDS")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        data_list_1 = []

        for port_data in port_list:
            if len(port_data) == 4:
                shelf, resource, serial, band = port_data

                if (band == '2g'):
                    curr_ssid, curr_passwd, curr_encryption, curr_eap_method, curr_eap_identity = self.ssid_2g, self.passwd_2g, self.encryption_2g, self.eap_method_2g, self.eap_identity_2g
                elif (band == '5g'):
                    curr_ssid, curr_passwd, curr_encryption, curr_eap_method, curr_eap_identity = self.ssid_5g, self.passwd_5g, self.encryption_5g, self.eap_method_5g, self.eap_identity_5g
                elif (band == '6g'):
                    curr_ssid, curr_passwd, curr_encryption, curr_eap_method, curr_eap_identity = self.ssid_6g, self.passwd_6g, self.encryption_6g, self.eap_method_6g, self.eap_identity_6g
            else:
                shelf, resource, serial, ssid, passwd, enc, eap_method, eap_identity = port_data
                curr_ssid, curr_passwd, curr_encryption, curr_eap_method, curr_eap_identity = ssid, passwd, enc, eap_method, eap_identity
            
            username = self.get_username(shelf, resource)
            # adding enable wifi option for android clients as a prerequisite step by-default
            command = 'shell svc wifi enable'
            data = {
                        'shelf': 1,
                        'resource': 1,
                        'adb_id': serial,
                        'key':8,
                        'adb_cmd': command
                    }
            data_list_1.append(data)

            if (username is None):
                # logger.warning('The device with serial {} not found'.format(serial))
                username = \
                requests.get('http://{}:{}/adb/1/1/{}'.format(self.lanforge_ip, self.port, serial)).json()['devices'][
                    'user-name']
            # check if the encryption is personal
            
            # if the encryption is enterprise
            if (self.ieee80211_2g==True or self.ieee80211_5g==True or self.ieee80211_6g==True):
                if curr_encryption=="wpa_enterprise":
                    curr_encryption="wpa-ent"
                if curr_encryption=="wpa2_enterprise":
                    curr_encryption="wpa2-ent"
                if curr_encryption=="wpa3_enterprise":
                    curr_encryption="wpa3-ent"
                data = {
                    'shelf': 1,
                    'resource': 1,
                    'adb_id': serial,
                    'key':8,
                    'adb_cmd': 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {} --es eap_method {} --es eap_user {} --es eap_passwd {}'.format(
                        username, self.server_ip, curr_ssid, curr_passwd, curr_encryption , curr_eap_method,
                        curr_eap_identity, curr_passwd)
                }
            else:
                data = {
                    'shelf': 1,
                    'resource': 1,
                    'adb_id': serial,
                    'key':8,
                    'adb_cmd': 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {}'.format(
                        username, self.server_ip, curr_ssid, curr_passwd, curr_encryption)
                }
            data_list.append(data)
        print("DATA LIST: ",data_list)
        print("URL: ",self.post_url)
        # execution for enabling wifi
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list_1]
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)

    # fetch all android devices
    def get_devices(self):

        # fetching all devices from interop tab
        interop_tab_data = requests.get(self.adb_url).json()['devices']

        devices_data = []

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if (type(interop_tab_data) is dict):

            name = interop_tab_data['name']

            if (interop_tab_data['phantom']):
                logger.warning(
                    '{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(name))

            else:
                _, _, serial = name.split('.')

                # parameters for adb post request
                try:
                    shelf, resource = interop_tab_data['resource-id'].split('.')
                except:
                    # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                    shelf, resource = '', ''

                if data['device-type']!='iOS':
                    devices_data.append([shelf, resource, serial])

        else:
            for device_data in interop_tab_data:
                for name, data in device_data.items():
                    if (data['phantom']):
                        logger.warning(
                            '{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(
                                name))
                        continue

                    _, _, serial = name.split('.')

                    try:
                        shelf, resource = data['resource-id'].split('.')
                    except:
                        # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                        shelf, resource = '', ''
                    if data['device-type']!='iOS':
                        devices_data.append([shelf, resource, serial])
                    


        return (devices_data)

    # get serial number from port name
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


# connectivity for laptops
class Laptop():
    def __init__(self,
                 lanforge_ip=None,
                 port=8080,
                 server_ip=None,
                 enable_wifi=None,
                 disconnect_devices=None,
                 reboot=None,
                 disable_wifi=None,
                 ssid_2g=None,
                 passwd_2g=None,
                 encryption_2g=None,
                 eap_method_2g=None,
                 eap_identity_2g=None,
                 ieee80211_2g=None,
                 ieee80211u_2g=None,
                 ieee80211w_2g=None,
                 enable_pkc_2g=None,
                 bss_transition_2g=None,
                 power_save_2g=None,
                 disable_ofdma_2g=None,
                 roam_ft_ds_2g=None,
                 key_management_2g=None,
                 pairwise_2g=None,
                 private_key_2g=None,
                 ca_cert_2g=None,
                 client_cert_2g=None,
                 pk_passwd_2g=None,
                 pac_file_2g=None,
                 ssid_5g=None,
                 passwd_5g=None,
                 encryption_5g=None,
                 eap_method_5g=None,
                 eap_identity_5g=None,
                 ieee80211_5g=None,
                 ieee80211u_5g=None,
                 ieee80211w_5g=None,
                 enable_pkc_5g=None,
                 bss_transition_5g=None,
                 power_save_5g=None,
                 disable_ofdma_5g=None,
                 roam_ft_ds_5g=None,
                 key_management_5g=None,
                 pairwise_5g=None,
                 private_key_5g=None,
                 ca_cert_5g=None,
                 client_cert_5g=None,
                 pk_passwd_5g=None,
                 pac_file_5g=None,
                 ssid_6g=None,
                 passwd_6g=None,
                 encryption_6g=None,
                 eap_method_6g=None,
                 eap_identity_6g=None,
                 ieee80211_6g=None,
                 ieee80211u_6g=None,
                 ieee80211w_6g=None,
                 enable_pkc_6g=None,
                 bss_transition_6g=None,
                 power_save_6g=None,
                 disable_ofdma_6g=None,
                 roam_ft_ds_6g=None,
                 key_management_6g=None,
                 pairwise_6g=None,
                 private_key_6g=None,
                 ca_cert_6g=None,
                 client_cert_6g=None,
                 pk_passwd_6g=None,
                 pac_file_6g=None,
                 debug=False):
        self.lanforge_ip = lanforge_ip
        self.port = port
        self.server_ip = server_ip  # upstream IP
        self.enable_wifi = enable_wifi
        self.disconnect_devices = disconnect_devices
        self.reboot = reboot
        self.disable_wifi = disable_wifi

        self.ssid_2g = ssid_2g
        self.encryption_2g = encryption_2g
        if (encryption_2g == 'open'):
            self.passwd_2g = 'NA'
        else:
            self.passwd_2g = passwd_2g

        self.ssid_5g = ssid_5g
        self.encryption_5g = encryption_5g
        if (encryption_5g == 'open'):
            self.passwd_5g = 'NA'
        else:
            self.passwd_5g = passwd_5g

        self.ssid_6g = ssid_6g
        self.encryption_6g = encryption_6g
        if (encryption_6g == 'open'):
            self.passwd_6g = 'NA'
        else:
            self.passwd_6g = passwd_6g

        # for enterprise authentication
        self.eap_method_2g = eap_method_2g
        self.eap_identity_2g = eap_identity_2g
        self.ieee80211_2g = ieee80211_2g
        self.ieee80211u_2g= ieee80211u_2g
        self.ieee80211w_2g= ieee80211w_2g
        self.enable_pkc_2g= enable_pkc_2g
        self.bss_transition_2g= bss_transition_2g
        self.power_save_2g= power_save_2g
        self.disable_ofdma_2g= disable_ofdma_2g
        self.roam_ft_ds_2g= roam_ft_ds_2g
        self.key_management_2g = key_management_2g
        self.pairwise_2g = pairwise_2g
        self.private_key_2g = private_key_2g
        self.ca_cert_2g = ca_cert_2g
        self.client_cert_2g = client_cert_2g
        self.pk_passwd_2g = pk_passwd_2g
        self.pac_file_2g = pac_file_2g

        self.eap_method_5g = eap_method_5g
        self.eap_identity_5g = eap_identity_5g
        self.ieee80211_5g = ieee80211_5g
        self.ieee80211u_5g= ieee80211u_5g
        self.ieee80211w_5g= ieee80211w_5g
        self.enable_pkc_5g= enable_pkc_5g
        self.bss_transition_5g= bss_transition_5g
        self.power_save_5g= power_save_5g
        self.disable_ofdma_5g= disable_ofdma_5g
        self.roam_ft_ds_5g= roam_ft_ds_5g
        self.key_management_5g = key_management_5g
        self.pairwise_5g = pairwise_5g
        self.private_key_5g = private_key_5g
        self.ca_cert_5g = ca_cert_5g
        self.client_cert_5g = client_cert_5g
        self.pk_passwd_5g = pk_passwd_5g
        self.pac_file_5g = pac_file_5g

        self.eap_method_6g = eap_method_6g
        self.eap_identity_6g = eap_identity_6g
        self.ieee80211_6g = ieee80211_6g
        self.ieee80211u_6g= ieee80211u_6g
        self.ieee80211w_6g= ieee80211w_6g
        self.enable_pkc_6g= enable_pkc_6g
        self.bss_transition_6g= bss_transition_6g
        self.power_save_6g= power_save_6g
        self.disable_ofdma_6g= disable_ofdma_6g
        self.roam_ft_ds_6g= roam_ft_ds_6g
        self.key_management_6g = key_management_6g
        self.pairwise_6g = pairwise_6g
        self.private_key_6g = private_key_6g
        self.ca_cert_6g = ca_cert_6g
        self.client_cert_6g = client_cert_6g
        self.pk_passwd_6g = pk_passwd_6g
        self.pac_file_6g = pac_file_6g

        # encryption encoding values for station creation
        self.enc_2g = self.set_encoding(self.encryption_2g, ieee80211u_2g, ieee80211w_2g, enable_pkc_2g, bss_transition_2g, power_save_2g, disable_ofdma_2g, roam_ft_ds_2g, key_management_2g, pairwise_2g, private_key_2g, ca_cert_2g, client_cert_2g, pk_passwd_2g, pac_file_2g)
        self.enc_5g = self.set_encoding(self.encryption_5g, ieee80211u_5g, ieee80211w_5g, enable_pkc_5g, bss_transition_5g, power_save_5g, disable_ofdma_5g, roam_ft_ds_5g, key_management_5g, pairwise_5g, private_key_5g, ca_cert_5g, client_cert_5g, pk_passwd_5g, pac_file_5g)
        self.enc_6g = self.set_encoding(self.encryption_2g, ieee80211u_6g, ieee80211w_6g, enable_pkc_6g, bss_transition_6g, power_save_6g, disable_ofdma_6g, roam_ft_ds_6g, key_management_6g, pairwise_6g, private_key_6g, ca_cert_6g, client_cert_6g, pk_passwd_6g, pac_file_6g)

        # mac format for creating station
        self.mac = 'xx:xx:xx:*:*:xx'

    # set encoding value
    def set_encoding(self, encryption, ieee80211u, ieee80211w, enable_pkc, bss_transition, power_save, disable_ofdma, roam_ft_ds, key_management, pairwise, private_key, ca_cert, client_cert, pk_passwd, pac_file):
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
            if ieee80211u==True:
                enc=enc+131072
            if enable_pkc==True:
                enc=enc+67108864
            if bss_transition==True:
                enc=enc+8796093022208
            if power_save==True:
                enc=enc+34359738368
            if disable_ofdma==True:
                enc=enc+35184372088832
            if roam_ft_ds==True:
                enc=enc+140737488355328

        return enc

    # request function to send json post request to the given url
    def post_data(self, url, data):
        try:
            print("LAPTOP API",url,data,datetime.now())
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

    def get_station_name(self, shelf, resource):
        url = 'http://{}:{}/ports/{}/{}/?fields=parent dev'.format(self.lanforge_ip, self.port, shelf, resource)
        station_response = requests.get(url)
        station_response = station_response.json()
        if ('interfaces' in station_response.keys()):
            stations = station_response['interfaces']
            for station in stations:
                station_name, station_details = list(station.keys())[0], list(station.values())[0]
                if (station_details['parent dev'] != ''):
                    return station_name.split('.')[2]
            return 'wlan0'
        else:
            logging.error(
                'Malformed response. Response does not have interfaces data. Setting the station name to default i.e., wlan0')
            return 'wlan0'
        
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
                sta_name = self.get_station_name(shelf, resource)
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
            band = port_data['band']
            os = port_data['os']
            if (band == '2g'):
                if ("ssid" in port_data):
                    curr_ssid = port_data['ssid']
                    curr_enc = self.set_encoding(port_data['enc'])
                    curr_passwd = port_data['passwd']
                    enterprise_status = self.ieee80211w_2g
                    enable_80211w = self.ieee80211w_2g
                else:
                    curr_ssid = self.ssid_2g
                    curr_passwd = self.passwd_2g
                    curr_enc = self.enc_2g
                    enterprise_status = self.ieee80211_2g
                    enable_80211w = self.ieee80211w_2g
                    
            elif (band == '5g'):
                if ("ssid" in port_data):
                    curr_ssid = port_data['ssid']
                    curr_enc = self.set_encoding(port_data['enc'])
                    curr_passwd = port_data['passwd']
                    enterprise_status = self.ieee80211_5g
                    enable_80211w = self.ieee80211w_5g
                else:
                    curr_ssid = self.ssid_5g
                    curr_passwd = self.passwd_5g
                    curr_enc = self.enc_5g
                    enterprise_status = self.ieee80211_5g
                    enable_80211w = self.ieee80211w_5g
            elif (band == '6g'):
                if ("ssid" in port_data):
                    curr_ssid = port_data['ssid']
                    curr_enc = self.set_encoding(port_data['enc'])
                    curr_passwd = port_data['passwd']
                    enterprise_status = self.ieee80211w_6g
                    enable_80211w = self.ieee80211w_6g
                else:
                    curr_ssid = self.ssid_6g
                    curr_passwd = self.passwd_6g
                    curr_enc = self.enc_6g
                    enterprise_status = self.ieee80211_6g
                    enable_80211w = self.ieee80211w_6g
            if (os in ['Apple', 'Lin']):
                if enterprise_status==True:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        'mac': 'xx:xx:xx:*:*:xx',
                        "ieee80211w" : enable_80211w
                    }
                else:
                    data = {
                        'shelf': shelf,
                        'resource': resource,
                        'radio': 'wiphy0',
                        'sta_name': sta_name,
                        'flags': curr_enc,
                        'ssid': curr_ssid,
                        'mac':'xx:xx:xx:*:*:xx',
                        'key': curr_passwd,
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
                        "ieee80211w" : enable_80211w
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
                    }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/add_sta'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

        # Use asyncio.gather to await the completion of all tasks
        results = await asyncio.gather(*tasks)
        time.sleep(2)
    
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
            band = port_data['band']
            os = port_data['os']
            if (band == '2g'):
                curr_passwd = self.passwd_2g
                enterprise_status = self.ieee80211_2g
                key_management = self.key_management_2g
                pairwise = self.pairwise_2g
                eap_method = self.eap_method_2g
                eap_identity = self.eap_identity_2g
                private_key = self.private_key_2g
                ca_cert = self.ca_cert_2g
                client_cert = self.ca_cert_2g
                pk_passwd = self.pk_passwd_2g
                pac_file = self.pac_file_2g
            elif (band == '5g'):
                curr_passwd = self.passwd_5g
                enterprise_status = self.ieee80211_5g
                key_management = self.key_management_5g
                pairwise = self.pairwise_5g
                eap_method = self.eap_method_5g
                eap_identity = self.eap_identity_5g
                private_key = self.private_key_5g
                ca_cert = self.ca_cert_5g
                client_cert = self.ca_cert_5g
                pk_passwd = self.pk_passwd_5g
                pac_file = self.pac_file_5g
            elif (band == '6g'):
                curr_passwd = self.passwd_6g
                enterprise_status = self.ieee80211_6g
                key_management = self.key_management_6g
                pairwise = self.pairwise_6g
                eap_method = self.eap_method_6g
                eap_identity = self.eap_identity_6g
                private_key = self.private_key_6g
                ca_cert = self.ca_cert_6g
                client_cert = self.ca_cert_6g
                pk_passwd = self.pk_passwd_6g
                pac_file = self.pac_file_6g
            if eap_method=="EAP-TTLS":
                eap_method="TTLS"
            if eap_method=="EAP-TLS":
                eap_method="TLS" 
            if eap_method=="EAP-PEAP":
                eap_method="PEAP"
            if eap_method=="EAP-PEAP":
                eap_method="PEAP" 
            if (enterprise_status==True and os=='Lin'):
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
                    "pac_file" : pac_file
                }
                data_list.append(data)
        url = 'http://{}:{}/cli-json/set_wifi_extra'.format(self.lanforge_ip, self.port)
        print("DATA LIST: ",data_list)
        print("URL: ",url)
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
            interest = port_data['interest']
            # report_timer = port_data['report_timer']
            current_flags = port_data['current_flags']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': 0,
                    'interest': 8388610,
                    'mac': self.mac
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
            interest = port_data['interest']
            # report_timer = port_data['report_timer']
            current_flags = port_data['current_flags']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': 1,
                    'interest': 8388610,
                    'mac': self.mac
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

    async def reboot_laptop(self, port_list=[]):
        print("REBOOT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            interest = port_data['interest']
            # report_timer = port_data['report_timer']
            current_flags = port_data['current_flags']
            os = port_data['os']
            
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
            interest = port_data['interest']
            # report_timer = port_data['report_timer']
            current_flags = port_data['current_flags']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    "report_timer": 1,
                    'current_flags': 2147483648,
                    'interest': 92291074,
                    'mac': self.mac
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

    async def set_radio(self, port_list=[]):
        print("SET PORT LAPTOP")
        if (port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            interest = port_data['interest']
            # report_timer = port_data['report_timer']
            current_flags = port_data['current_flags']
            os = port_data['os']
            if (os == 'Lin'):
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': 'wiphy0',
                    "report_timer": 1,
                    'current_flags': 0,
                    'interest': 92291074,
                    'mac': self.mac
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

    
    # fetch all laptops
    def get_resources_data(self):

        # fetching all devices from Resource Manager tab
        url = 'http://{}:{}/resource/all'.format(self.lanforge_ip, self.port)
        response = requests.get(url).json()

        resources = response['resources']

        # if there are no resources except LANforge in resource manager tab
        if (type(resources) is dict):
            return ([])

        resources_list = []
        for resource_data in resources:
            port, resource = list(resource_data.keys())[0], list(resource_data.values())[0]

            # filtering LANforges from resources
            if (resource['ct-kernel']):
                continue

            # filtering Androids from resources
            if (resource['user'] != ''):
                continue

            #filtering ios from resource manager
            if (resource['kernel']==''):
                continue

            # filtering phantom resources
            if (resource['phantom']):
                logger.info('The laptop on port {} is in phantom state.'.format(port))
                continue

            shelf, resource_id = port.split('.')
            hostname = resource_data[port]['hostname']
            sta_name = self.get_station_name(shelf=shelf, resource=resource_id)

            hw_version = resource['hw version']

            # fetching data for Windows
            if ('Win' in hw_version):
                resources_list.append({
                    'os': 'Win',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': sta_name,
                    'hostname': hostname,
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
                    'sta_name': sta_name,
                    'hostname': hostname,
                    # 'sta_name': 'en0',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

            # fetching data for Mac
            elif ('Apple' in hw_version):
                resources_list.append({
                    'os': 'Apple',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': sta_name,
                    'hostname': hostname,
                    'current_flags': 2147483648,
                    'interest': 16384
                })

        return (resources_list)

    # fetching selected laptops from ports list
    def get_laptop_from_port(self, port_list=[]):
        if (port_list == []):
            logger.info('There are no laptops')
            return

        resources_list = []
        for port in port_list:
            shelf, resource, _ = port.split('.')
            url = 'http://{}:{}/resource/{}/{}'.format(self.lanforge_ip, self.port, shelf, resource)
            laptop_response = requests.get(url)
            laptop_response = laptop_response.json()
            if ('resource' not in laptop_response.keys()):
                raise ValueError('Malformed response for resource request. "Resource" key missing.')

            laptop_data = laptop_response['resource']

            # checking if laptop is phantom
            if (laptop_data['phantom']):
                logger.info('The selected laptop on port {}.{} is in phantom state.'.format(shelf, resource))

            hw_version = laptop_data['hw version']

            # fetching data for Windows
            if ('Win' in hw_version):
                resources_list.append({
                    'os': 'Win',
                    'shelf': shelf,
                    'resource': resource,
                    'sta_name': 'wlan0',
                    'report_timer': 1500,
                    'interest': 8388610
                })

            # fetching data for Linux
            elif ('Lin' in hw_version):
                resources_list.append({
                    'os': 'Lin',
                    'shelf': shelf,
                    'resource': resource,
                    'sta_name': 'sta{}'.format(resource),
                    # 'sta_name': 'en0',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

            # fetching data for Mac
            elif ('Apple' in hw_version):
                resources_list.append({
                    'os': 'Apple',
                    'shelf': shelf,
                    'resource': resource,
                    'sta_name': 'en0',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

        return (resources_list)