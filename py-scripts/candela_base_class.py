import asyncio
import importlib
import datetime
import time
import requests
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
http_test = importlib.import_module("py-scripts.lf_webpage")


class Candela:
    """_summary_
    """

    def __init__(self, ip='localhost', port=8080):
        """
        Constructor to initialize the LANforge IP and port
        Args:
            ip (str, optional): LANforge IP. Defaults to 'localhost'.
            port (int, optional): LANforge port. Defaults to 8080.
        """
        self.lanforge_ip = ip
        self.port = port
        self.api_url = 'http://{}:{}'.format(self.lanforge_ip, self.port)

    def api_get(self, endp: str):
        """
        Sends a GET request to fetch data

        Args:
            endp (str): API endpoint

        Returns:
            response: response code for the request
            data: data returned in the response
        """        
        if endp[0] != '/':
            endp = '/' + endp
        response = requests.get(url= self.api_url + endp)
        data = response.json()
        return response, data
    
    def api_post(self, endp: str, payload: dict):
        """
        Sends POST request

        Args:
            endp (str): API endpoint
            payload (dict): Endpoint data in JSON format

        Returns:
            response: response code for the request
                      None if endpoint is invalid
        """        
        if endp == '' or endp is None:
            print('Invalid endpoint specified.')
            return False
        if endp[0] != '/':
            endp = '/' + endp
        response = requests.post(url=self.api_url + endp, json=payload)
        return response
    
    def get_device_info(self):
        """
        Fetches all the real devices clustered to the LANforge

        Returns:
            interop_tab_response: if invalid response code. Response code other than 200.
            androids: Android serials. Defaults to [].
            linux: Linux device hostnames. Defaults to [].
            macbooks: Mac Book hostnames. Defaults to [].
            windows: Windows hostnames. Defaults to [].
            iOS: iOS serials. Defaults to [].
        """        
        androids, linux, macbooks, windows, iOS = [], [], [], [], []

        # querying interop tab for fetching android and iOS data
        interop_tab_response, interop_tab_data = self.api_get(endp='/adb')
        if interop_tab_response.status_code != 200:
            print('Error fetching the data with the {}. Returned {}'.format('/adb', interop_tab_response))
            return interop_tab_response
        for mobile in interop_tab_data['devices']:
            mobile_serial, mobile_data = list(mobile.keys())[0], list(mobile.values())[0]
            if mobile_data['phantom']:
                continue
            if mobile_data['device-type'] == 'Android':
                androids.append(mobile_data)
            elif mobile_data['device-type'] == 'iOS':
                iOS.append(mobile_data)
        
        # querying resource manager tab for fetching laptops data
        resource_manager_tab_response, resource_manager_data = self.api_get(endp='/resource/all')
        if resource_manager_tab_response.status_code != 200:
            print('Error fetching the data with the {}. Returned {}'.format('/resources/all', interop_tab_response))
            return interop_tab_response
        resources_list = [resource_manager_data['resource'] if 'resource' in resource_manager_data else resource_manager_data['resources']][0]
        for resource in resources_list:
            resource_port, resource_data = list(resource.keys())[0], list(resource.values())[0]
            if resource_data['phantom']:
                continue
            if resource_data['app-id'] == '0' and resource_data['ct-kernel'] is False:
                if 'Win' in resource_data['hw version']:
                    windows.append(resource_data)
                elif 'Apple' in resource_data['hw version']:
                    macbooks.append(resource_data)
                elif 'Linux' in resource_data['hw version']:
                    linux.append(resource_data)

        return androids, linux, macbooks, windows, iOS
    
    def start_connectivity(self,
                           manager_ip=None,
                           port=8080,
                           server_ip=None,
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
                           enable_wifi=None,
                           disable_wifi=None,
                           selected_bands=['5g'],
                           groups=False,
                           _debug_on=False,
                           _exit_on_error=False,
                           all_android=None,
                           all_laptops=None,
                           device_list=None):
        self.real_device_class = RealDevice(manager_ip=manager_ip,
                                            port=port,
                                            server_ip=server_ip,
                                            ssid_2g=ssid_2g,
                                            passwd_2g=passwd_2g,
                                            encryption_2g=encryption_2g,
                                            eap_method_2g=eap_method_2g,
                                            eap_identity_2g=eap_identity_2g,
                                            ieee80211_2g=ieee80211_2g,
                                            ieee80211u_2g=ieee80211u_2g,
                                            ieee80211w_2g=ieee80211w_2g,
                                            enable_pkc_2g=enable_pkc_2g,
                                            bss_transition_2g=bss_transition_2g,
                                            power_save_2g=power_save_2g,
                                            disable_ofdma_2g=disable_ofdma_2g,
                                            roam_ft_ds_2g=roam_ft_ds_2g,
                                            key_management_2g=key_management_2g,
                                            pairwise_2g=pairwise_2g,
                                            private_key_2g=private_key_2g,
                                            ca_cert_2g=ca_cert_2g,
                                            client_cert_2g=client_cert_2g,
                                            pk_passwd_2g=pk_passwd_2g,
                                            pac_file_2g=pac_file_2g,
                                            ssid_5g=ssid_5g,
                                            passwd_5g=passwd_5g,
                                            encryption_5g=encryption_5g,
                                            eap_method_5g=eap_method_5g,
                                            eap_identity_5g=eap_identity_5g,
                                            ieee80211_5g=ieee80211_5g,
                                            ieee80211u_5g=ieee80211u_5g,
                                            ieee80211w_5g=ieee80211w_5g,
                                            enable_pkc_5g=enable_pkc_5g,
                                            bss_transition_5g=bss_transition_5g,
                                            power_save_5g=power_save_5g,
                                            disable_ofdma_5g=disable_ofdma_5g,
                                            roam_ft_ds_5g=roam_ft_ds_5g,
                                            key_management_5g=key_management_5g,
                                            pairwise_5g=pairwise_5g,
                                            private_key_5g=private_key_5g,
                                            ca_cert_5g=ca_cert_5g,
                                            client_cert_5g=client_cert_5g,
                                            pk_passwd_5g=pk_passwd_5g,
                                            pac_file_5g=pac_file_5g,
                                            ssid_6g=ssid_6g,
                                            passwd_6g=passwd_6g,
                                            encryption_6g=encryption_6g,
                                            eap_method_6g=eap_method_6g,
                                            eap_identity_6g=eap_identity_6g,
                                            ieee80211_6g=ieee80211_6g,
                                            ieee80211u_6g=ieee80211u_6g,
                                            ieee80211w_6g=ieee80211w_6g,
                                            enable_pkc_6g=enable_pkc_6g,
                                            bss_transition_6g=bss_transition_6g,
                                            power_save_6g=power_save_6g,
                                            disable_ofdma_6g=disable_ofdma_6g,
                                            roam_ft_ds_6g=roam_ft_ds_6g,
                                            key_management_6g=key_management_6g,
                                            pairwise_6g=pairwise_6g,
                                            private_key_6g=private_key_6g,
                                            ca_cert_6g=ca_cert_6g,
                                            client_cert_6g=client_cert_6g,
                                            pk_passwd_6g=pk_passwd_6g,
                                            pac_file_6g=pac_file_6g,
                                            enable_wifi=enable_wifi,
                                            disable_wifi=disable_wifi,
                                            selected_bands=['5g'],
                                            groups=groups,
                                            _debug_on=_debug_on,
                                            _exit_on_error=_exit_on_error,
                                            all_android=all_android,
                                            all_laptops=all_laptops)
        d = self.real_device_class.query_all_devices_to_configure_wifi(
            device_list=device_list)
        return asyncio.run(self.real_device_class.configure_wifi())

    def start_ftp_test(self,
                       ssid,
                       password,
                       security,
                       ap_name='',
                       band='5g',
                       direction='Download',
                       file_size='12MB',
                       traffic_duration=60,
                       upstream='eth1',
                       lf_username='lanforge',
                       lf_password='lanforge',
                       ssh_port=22,
                       clients_type='Real',
                       device_list=[],
                       background=False):
        # for band in bands:
        #     for direction in directions:
        #         for file_size in file_sizes:
        # Start Test
        obj = FtpTest(lfclient_host=self.lanforge_ip,
                        lfclient_port=self.port,
                        upstream=upstream,
                        dut_ssid=ssid,
                        dut_passwd=password,
                        dut_security=security,
                        band=band,
                        ap_name=ap_name,
                        file_size=file_size,
                        direction=direction,
                        lf_username=lf_username,
                        lf_password=lf_password,
                        # duration=pass_fail_duration(band, file_size),
                        traffic_duration=traffic_duration,
                        ssh_port=ssh_port,
                        clients_type=clients_type,
                        device_list=device_list
                        )

        obj.data = {}
        obj.file_create()
        if clients_type == "Real":
            obj.query_realclients()
        obj.set_values()
        obj.count = 0
        # obj.precleanup()
        obj.build()
        if not obj.passes():
            print(obj.get_fail_message())
            exit(1)

        # First time stamp
        test_start_time = datetime.datetime.now()
        print("Traffic started running at ", test_start_time)
        obj.start(False, False)
        if(background):
            return test_start_time, obj
        time.sleep(traffic_duration)
        obj.stop()
        print("Traffic stopped running")
        obj.my_monitor()
        obj.postcleanup()
        test_end_time = datetime.datetime.now()
        print("Test ended at", test_end_time)
        return test_start_time, test_end_time

    def stop_ftp_test(self, ftp_object):
        ftp_object.stop()
        print("Traffic stopped running")
        ftp_object.my_monitor()
        ftp_object.postcleanup()
        test_end_time = datetime.datetime.now()
        print("FTP test ended at", test_end_time)
        return test_end_time


candela_apis = Candela(ip='192.168.214.61', port=8080)
device_list, report_labels, device_macs = candela_apis.start_connectivity(
    manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]', device_list=['RZ8N10FFTKE', 'RZ8NB1KWXLB'])
print(device_list, report_labels, device_macs)
# device_list, report_labels, device_macs = candela_apis.start_connectivity(manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]')
# candela_apis.start_ftp_test(ssid='Walkin_open', password='[BLANK]', security='open', bands=[
#                             '5G'], directions=['Download'], file_sizes=['10MB'], device_list=','.join(device_list))
