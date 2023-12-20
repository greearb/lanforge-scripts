#!/usr/bin/env python3

import logging
import sys
import asyncio
import requests
import time

if(sys.version_info[0] != 3):
    logging.critical('This script requires Python3')
    exit()

logger = logging.getLogger(__name__)

# connectivity for Androids
class Android():
    def __init__(self,
                 lanforge_ip=None,
                 port=8080,
                 server_ip=None,
                 ssid=None,
                 passwd=None,
                 encryption=None,
                 eap_method=None,
                 eap_identity=None,
                 debug=False):
        self.lanforge_ip = lanforge_ip
        self.port = port
        self.server_ip = server_ip  #upstream IP
        self.ssid = ssid
        self.passwd = passwd
        self.encryption = encryption

        # for enterprise authentication
        self.eap_method = eap_method
        self.eap_identity = eap_identity

        self.min_supported_android_version = 10

        # adb post url
        self.post_url = 'http://{}:{}/cli-json/adb'.format(self.lanforge_ip, self.port)

        # adb get url
        self.adb_url = 'http://{}:{}/adb'.format(self.lanforge_ip, self.port)

    # request function to send json post request to the adb api
    def post_data(self, url, data):
        try:
            print(data)
            logger.info(data)
            requests.post(url, json=data)
        except:
            logger.error('Request failed for port {}'.format(data['adb_id']))

    # stop app
    def stop_app(self, port_list = []):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        data_list = []

        command = 'shell am force-stop com.candela.wecan'
        for port_data in port_list:
            shelf, resource, serial = port_data
            data = {
                'shelf'     : 1,
                'resource'  : 1,
                'adb_id'    : serial,
                'adb_cmd'   : command
            }
            data_list.append(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

    # toggle wifi
    def set_wifi_state(self, port_list = [], state='enable'):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        state = state.lower()
        if(state != 'enable' and state != 'disable'):
            logger.warning('State argument should be either enable or disable')
            return
        
        command = 'shell svc wifi {}'.format(state)

        data_list = []
        for port_data in port_list:
            shelf, resource, serial = port_data

            data = {
                'shelf'     : 1,
                'resource'  : 1,
                'adb_id'    : serial,
                'adb_cmd'   : command
            }
            data_list.append(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

    def forget_all_networks(self, port_list = []):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        url = 'http://{}:{}/cli-json/clear_wifi_profiles'.format(self.lanforge_ip, self.port)

        data_list = []
        for port_data in port_list:
            shelf, resource, serial = port_data

            data = {
                'shelf'     : 1,
                'resource'  : 1,
                'id'        : serial,
                'type'      : 'adb'
            }
            data_list.append(data)
        
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

    # fetching the username from the interop tab
    def get_username(self, shelf, resource):

        port = '{}.{}'.format(shelf, resource)
        # fetching all devices data from interop tab
        interop_tab_data = requests.get(self.adb_url).json()['devices']

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if(type(interop_tab_data) is dict):
            name = interop_tab_data['name']
            if(interop_tab_data['resource-id'] == port):
                if(int(interop_tab_data['release'].split('.')[0]) < self.min_supported_android_version):
                    logger.warning('Android device {} having android version less {}. Some functions may not be supported.'.format(interop_tab_data['user-name'], self.min_supported_android_version))
                return(interop_tab_data['user-name'])
        else:
            for interop_device in interop_tab_data:
                for name, data in interop_device.items():
                    if(data['resource-id'] == port):
                        if(int(data['release'].split('.')[0]) < self.min_supported_android_version):
                            logger.warning('Android device {} having android version less {}. Some functions may not be supported.'.format(data['user-name'], self.min_supported_android_version))
                        return(data['user-name'])

    def configure_wifi(self, port_list = []):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        data_list = []

        for port_data in port_list:
            shelf, resource, serial = port_data

            username = self.get_username(shelf, resource)

            if(username is None):
                # logger.warning('The device with serial {} not found'.format(serial))
                username = requests.get('http://{}:{}/adb/1/1/{}'.format(self.lanforge_ip, self.port, serial)).json()['devices']['user-name']

            # check if the encryption is personal
            if(self.eap_method is None):
                data = {
                    'shelf'     : 1,
                    'resource'  : 1,
                    'adb_id'    : serial,
                    'adb_cmd'   : 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {}'.format(username, self.server_ip, self.ssid, self.passwd, self.encryption)
                }
            # if the encryption is enterprise
            else:
                data = {
                    'shelf'     : 1,
                    'resource'  : 1,
                    'adb_id'    : serial,
                    'adb_cmd'   : 'shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity --es auto_start 1 --es username {} --es serverip {} --es ssid {} --es password {} --es encryption {} --es eap_method {} --es eap_user {} --es eap_passwd {}'.format(username, self.server_ip, self.ssid, self.passwd, self.encryption+"-ent", self.eap_method, self.eap_identity, self.passwd)
                }
            data_list.append(data)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, self.post_url, data) for data in data_list]

    # fetch all android devices  
    def get_devices(self):
        
        # fetching all devices from interop tab
        interop_tab_data = requests.get(self.adb_url).json()['devices']

        devices_data = []

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if(type(interop_tab_data) is dict):

            name = interop_tab_data['name']

            if(interop_tab_data['phantom']):
                logger.warning('{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(name))

            else:
                _, _, serial = name.split('.')

                # parameters for adb post request
                try:
                    shelf, resource = interop_tab_data['resource-id'].split('.')
                except:
                    # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                    shelf, resource = '', ''

                devices_data.append((shelf, resource, serial))

        else:
            for device_data in interop_tab_data:
                for name, data in device_data.items():
                    if(data['phantom']):
                        logger.warning('{} is in phantom state. Please make sure debugging is enabled in developer settings.'.format(name))
                        continue

                    _, _, serial = name.split('.')

                    try:
                        shelf, resource = data['resource-id'].split('.')
                    except:
                        # logger.warning('Resource id is missing for the device {} therefore skipping the device from usage'.format(name))
                        shelf, resource = '', ''

                    devices_data.append((shelf, resource, serial))

        return(devices_data)
    
    # get serial number from port name
    def get_serial_from_port(self, port_list=[]):

        if(port_list == []):
            logger.info('Androids list is empty')
            return
        
        devices_data = []
        url = 'http://{}:{}/adb/'.format(self.lanforge_ip, self.port)
        resource_response = requests.get(url)
        android_devices = resource_response.json()['devices']

        # checking if there is only one device in interop tab. The value would be a dictionary instead of a list
        if(type(android_devices) is dict):
            for port_id in port_list:
                shelf, resource, port = port_id.split('.')
                resource_id = '{}.{}'.format(shelf, resource)
                device_name = android_devices['name']
                if(resource_id == android_devices['resource-id']):
                    device_serial = device_name.split('.')[2]
                    devices_data.append((shelf, resource, device_serial))
                    break
        else:
            for port_id in port_list:
                shelf, resource, port = port_id.split('.')
                resource_id = '{}.{}'.format(shelf, resource)
                for android_device in android_devices:
                    device_name, device_data = list(android_device.keys())[0], list(android_device.values())[0]
                    if(resource_id == device_data['resource-id']):
                        device_serial = device_name.split('.')[2]
                        devices_data.append((shelf, resource, device_serial))
                        continue
        return(devices_data)


# connectivity for laptops
class Laptop():
    def __init__(self,
                 lanforge_ip=None,
                 port=8080,
                 server_ip=None,
                 ssid=None,
                 passwd=None,
                 encryption=None,
                 eap_method=None,
                 eap_identity=None):
        self.lanforge_ip = lanforge_ip
        self.port = port
        self.server_ip = server_ip  # upstream IP
        self.ssid = ssid
        self.passwd = passwd
        self.encryption = encryption.lower()

        # for enterprise authentication
        self.eap_method = eap_method
        self.eap_identity = eap_identity
        self.enc = 0

        if(self.encryption == 'open'):
            self.enc = 0
            self.passwd = 'NA'
        elif(self.encryption == 'wpa_personal' or self.encryption == 'psk' or self.encryption == 'wpa'):
            self.enc = 16
        elif(self.encryption == "wpa2_personal" or self.encryption == 'psk2' or self.encryption == 'wpa2'):
            self.enc=1024
        elif(self.encryption == "wpa3_personal" or self.encryption == 'psk3' or self.encryption == 'wpa3'):
            self.enc=1099511627776
        elif(self.encryption == "wpa_enterprise"):
            self.enc=33554448
        elif(self.encryption == "wpa2_enterprise"):
            self.enc=33555456
        elif(self.encryption == "wpa3_enterprise"):
            self.enc=1099545182208

        # mac format for creating station
        self.mac = 'xx:xx:xx:*:*:xx'
    
    # request function to send json post request to the given url
    def post_data(self, url, data):
        try:
            logger.info(data)
            requests.post(url, json=data)
        except:
            logger.error('Request failed for port {}'.format(data['port'])) 
    
    # remove station
    # NOTE this is only for Linux Laptops
    def rm_station(self, port_list=[]):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        data_list = []
        for port_data in port_list:
            if('Lin' == port_data['os']):
                shelf, resource, sta_name = port_data['shelf'], port_data['resource'], port_data['sta_name']

                get_station_name = requests.get('http://{}:{}/ports/{}/{}/?fields=parent dev'.format(self.lanforge_ip, self.port, shelf, resource))
                station_response = get_station_name.json()
                stations = station_response['interfaces']

                if(type(stations) == list):
                    for station in stations:
                        station_name, station_details = list(station.keys())[0], list(station.values())[0]
                        if(station_details['parent dev'] != ''):

                            data = {
                                'shelf'     : shelf,
                                'resource'  : resource,
                                'port'      : sta_name
                            }
                            data_list.append(data)
                            break
                elif(type(stations) == dict):
                    logger.warning('The port {}.{} does not have the required interfaces'.format(shelf, resource))
        
        url = 'http://{}:{}/cli-json/rm_vlan'.format(self.lanforge_ip, self.port)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

    # add station
    def add_station(self, port_list=[]):
        if(port_list == []):
            logger.info('Port list is empty')
            return
        
        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            sta_name = port_data['sta_name']
            data = {
                'shelf'     : shelf,
                'resource'  : resource,
                'radio'     : 'wiphy0',
                'sta_name'  : sta_name,
                'flags'     : self.enc,
                'ssid'      : self.ssid,
                'key'       : self.passwd,
                'mac'       : self.mac
            }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/add_sta'.format(self.lanforge_ip, self.port)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

    # set port (enable DHCP)
    def set_port(self, port_list=[]):
        if(port_list == []):
            logger.info('Port list is empty')
            return

        data_list = []
        for port_data in port_list:
            shelf = port_data['shelf']
            resource = port_data['resource']
            port = port_data['sta_name']
            interest = port_data['interest']

            os = port_data['os']
            if(os in ['Apple', 'Lin']):
                current_flags = port_data['current_flags']
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'current_flags': current_flags,
                    'interest': interest,
                    'mac': self.mac
                }
            elif(os == 'Win'):
                report_timer = port_data['report_timer']
                data = {
                    'shelf': shelf,
                    'resource': resource,
                    'port': port,
                    'report_timer': report_timer,
                    'interest': interest
                }
            data_list.append(data)

        url = 'http://{}:{}/cli-json/set_port'.format(self.lanforge_ip, self.port)

        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self.post_data, url, data) for data in data_list]

    # fetch all laptops
    def get_resources_data(self):

        # fetching all devices from Resource Manager tab
        url = 'http://{}:{}/resource/all'.format(self.lanforge_ip, self.port)
        response = requests.get(url).json()

        resources = response['resources']
        
        # if there are no resources except LANforge in resource manager tab
        if(type(resources) is dict):
            return([])

        resources_list = []
        for resource_data in resources:
            port, resource = list(resource_data.keys())[0], list(resource_data.values())[0]
            shelf, resource_id = port.split('.')
            hostname = resource_data[port]['hostname']
            # filtering LANforges from resources
            if(resource['ct-kernel']):
                continue

            # filtering Androids from resources
            if(resource['user'] != ''):
                continue
            
            # filtering phantom resources
            if(resource['phantom']):
                logger.info('The laptop on port {} is in phantom state.'.format(port))
                continue

            hw_version = resource['hw version']

            # fetching data for Windows
            if('Win' in hw_version):
                resources_list.append({
                    'os': 'Win',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': 'ad1',
                    'hostname': hostname,
                    'report_timer': 1500,
                    'current_flags': 2147483648,
                    'interest': 16384
                })
            
            # fetching data for Linux
            elif('Lin' in hw_version):
                resources_list.append({
                    'os': 'Lin',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': 'sta{}'.format(resource_id),
                    'hostname': hostname,
                    # 'sta_name': 'en0',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

            # fetching data for Mac
            elif('Apple' in hw_version):
                resources_list.append({
                    'os': 'Apple',
                    'shelf': shelf,
                    'resource': resource_id,
                    'sta_name': 'en0',
                    'hostname': hostname,
                    'current_flags': 2147483648,
                    'interest': 16384
                })

        return(resources_list)
    
    # fetching selected laptops from ports list
    def get_laptop_from_port(self, port_list=[]):
        if(port_list == []):
            logger.info('There are no laptops')
            return
 
        resources_list = []
        for port in port_list:
            shelf, resource, _ = port.split('.')
            url = 'http://{}:{}/resource/{}/{}'.format(self.lanforge_ip, self.port, shelf, resource)
            laptop_response = requests.get(url)
            laptop_response = laptop_response.json()
            if('resource' not in laptop_response.keys()):
                raise ValueError('Malformed response for resource request. "Resource" key missing.')

            laptop_data = laptop_response['resource']

            # checking if laptop is phantom            
            if(laptop_data['phantom']):
                logger.info('The selected laptop on port {}.{} is in phantom state.'.format(shelf, resource))

            hw_version = laptop_data['hw version']

            # fetching data for Windows
            if('Win' in hw_version):
                resources_list.append({
                    'os': 'Win',
                    'shelf': shelf,
                    'resource': resource,
                    'sta_name': 'ad1',
                    'report_timer': 1500,
                    'interest': 8388610
                })

            # fetching data for Linux
            elif('Lin' in hw_version):
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
            elif('Apple' in hw_version):
                resources_list.append({
                    'os': 'Apple',
                    'shelf': shelf,
                    'resource': resource,
                    'sta_name': 'en0',
                    'current_flags': 2147483648,
                    'interest': 16384
                })

        return(resources_list)
        

'''
# Sample Usage

# Testing Laptops

laptops = Laptop('192.168.200.63', 8080, '192.168.68.53', ssid='TPLink', passwd='Password@123', encryption='psk2')

# laptops = Laptop('192.168.200.192', 8080, '192.168.1.61', ssid='OpenWifi_nat1', passwd='OpenWifi', encryption='psk2')

laptops_list = laptops.get_resources_data()
print(laptops_list)

# works only for Linux laptops
# NOTE: Ignore this function call if there are no Linux Laptops included.
laptops.rm_station(port_list=laptops_list)

time.sleep(2)

laptops.add_station(port_list=laptops_list)

time.sleep(2)

laptops.set_port(port_list=laptops_list)


# Testing Androids 

android = Android('192.168.200.165', 8080, '192.168.1.15', ssid='OpenWifi_wpa2', passwd='OpenWifi', encryption='psk2')

ports_list = android.get_devices()

print(ports_list)

android.stop_app(port_list=ports_list)

android.set_wifi_state(port_list=ports_list, state='disable')

time.sleep(5)

android.set_wifi_state(port_list=ports_list, state='enable')

# time.sleep(10)

# android.forget_all_networks(port_list=ports_list)

android.configure_wifi(port_list=ports_list)

'''