import asyncio
import importlib
import datetime
import time
import requests
import logging
import pandas as pd
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
from lf_webpage import HttpDownload
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
from lf_interop_throughput import Throughput
from lf_interop_video_streaming import VideoStreamingTest
from lf_interop_real_browser_test import RealBrowserTest
from datetime import datetime, timedelta
http_test = importlib.import_module("py-scripts.lf_webpage")
througput_test=importlib.import_module("py-scripts.lf_interop_throughput")
video_streaming_test=importlib.import_module("py-scripts.lf_interop_video_streaming")
web_browser_test=importlib.import_module("py-scripts.lf_interop_real_browser_test")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
logger = logging.getLogger(__name__)


class Candela:
    """
    Candela Class file to invoke different scripts from py-scripts.
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
        response = requests.get(url=self.api_url + endp)
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
            logger.info('Invalid endpoint specified.')
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
            logger.info('Error fetching the data with the {}. Returned {}'.format(
                '/adb', interop_tab_response))
            return interop_tab_response
        for mobile in interop_tab_data['devices']:
            mobile_serial, mobile_data = list(
                mobile.keys())[0], list(mobile.values())[0]
            if mobile_data['phantom']:
                continue
            if mobile_data['device-type'] == 'Android':
                androids.append(mobile_data)
            elif mobile_data['device-type'] == 'iOS':
                iOS.append(mobile_data)

        # querying resource manager tab for fetching laptops data
        resource_manager_tab_response, resource_manager_data = self.api_get(
            endp='/resource/all')
        if resource_manager_tab_response.status_code != 200:
            logger.info('Error fetching the data with the {}. Returned {}'.format(
                '/resources/all', interop_tab_response))
            return interop_tab_response
        resources_list = [resource_manager_data['resource']
                          if 'resource' in resource_manager_data else resource_manager_data['resources']][0]
        for resource in resources_list:
            resource_port, resource_data = list(resource.keys())[
                0], list(resource.values())[0]
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
                           selected_bands=['5g'],
                           groups=False,
                           _debug_on=False,
                           _exit_on_error=False,
                           all_android=None,
                           all_laptops=None,
                           device_list=None):
        """
        Method to attempt devices to connect to the given SSID.

        Args:
            manager_ip (str, optional): LANforge IP. Defaults to None.
            port (int, optional): LANforge port. Defaults to 8080.
            server_ip (str, optional): Upstream IP for LANforge Interop App in androids. Defaults to None.
            ssid_2g (str, optional): 2G SSID. Defaults to None.
            passwd_2g (str, optional): Password for 2G SSID. Use [BLANK] incase of Open security. Defaults to None.
            encryption_2g (str, optional): Security for 2G SSID. Defaults to None.
            eap_method_2g (str, optional): Defaults to None.
            eap_identity_2g (str, optional): Defaults to None.
            ieee80211_2g (str, optional): Defaults to None.
            ieee80211u_2g (str, optional): Defaults to None.
            ieee80211w_2g (str, optional): Defaults to None.
            enable_pkc_2g (str, optional): Defaults to None.
            bss_transition_2g (str, optional): Defaults to None.
            power_save_2g (str, optional): Defaults to None.
            disable_ofdma_2g (str, optional): Defaults to None.
            roam_ft_ds_2g (str, optional): Defaults to None.
            key_management_2g (str, optional): Defaults to None.
            pairwise_2g (str, optional): Defaults to None.
            private_key_2g (str, optional): Defaults to None.
            ca_cert_2g (str, optional): Defaults to None.
            client_cert_2g (str, optional): Defaults to None.
            pk_passwd_2g (str, optional): Defaults to None.
            pac_file_2g (str, optional): Defaults to None.
            ssid_5g (str, optional): 5G SSID. Defaults to None.
            passwd_5g (str, optional): Password for 5G SSID. Use [BLANK] incase of Open Security. Defaults to None.
            encryption_5g (str, optional): Encryption for 5G SSID. Defaults to None.
            eap_method_5g (str, optional): Defaults to None.
            eap_identity_5g (str, optional): Defaults to None.
            ieee80211_5g (str, optional): Defaults to None.
            ieee80211u_5g (str, optional): Defaults to None.
            ieee80211w_5g (str, optional): Defaults to None.
            enable_pkc_5g (str, optional): Defaults to None.
            bss_transition_5g (str, optional): Defaults to None.
            power_save_5g (str, optional): Defaults to None.
            disable_ofdma_5g (str, optional): Defaults to None.
            roam_ft_ds_5g (str, optional): Defaults to None.
            key_management_5g (str, optional): Defaults to None.
            pairwise_5g (str, optional): Defaults to None.
            private_key_5g (str, optional): Defaults to None.
            ca_cert_5g (str, optional): Defaults to None.
            client_cert_5g (str, optional): Defaults to None.
            pk_passwd_5g (str, optional): Defaults to None.
            pac_file_5g (str, optional): Defaults to None.
            ssid_6g (str, optional): 6G SSID. Defaults to None.
            passwd_6g (str, optional): Password for 6G SSID. Use [BLANK] incase of Open Security. Defaults to None.
            encryption_6g (str, optional): Encryption for 6G SSID. Defaults to None.
            eap_method_6g (str, optional): Defaults to None.
            eap_identity_6g (str, optional): Defaults to None.
            ieee80211_6g (str, optional): Defaults to None.
            ieee80211u_6g (str, optional): Defaults to None.
            ieee80211w_6g (str, optional): Defaults to None.
            enable_pkc_6g (str, optional): Defaults to None.
            bss_transition_6g (str, optional): Defaults to None.
            power_save_6g (str, optional): Defaults to None.
            disable_ofdma_6g (str, optional): Defaults to None.
            roam_ft_ds_6g (str, optional): Defaults to None.
            key_management_6g (str, optional): Defaults to None.
            pairwise_6g (str, optional): Defaults to None.
            private_key_6g (str, optional): Defaults to None.
            ca_cert_6g (str, optional): Defaults to None.
            client_cert_6g (str, optional): Defaults to None.
            pk_passwd_6g (str, optional): Defaults to None.
            pac_file_6g (str, optional): Defaults to None.
            selected_bands (list, optional): Specify '2g', '5g', '6g' in a list to connect devices on multiple SSIDS. Defaults to ['5g'].
            groups (bool, optional): Defaults to False.
            _debug_on (bool, optional): Defaults to False.
            _exit_on_error (bool, optional): Defaults to False.
            all_android (_type_, optional): Defaults to None.
            all_laptops (_type_, optional): Defaults to None.
            device_list (list, optional): List of serial numbers for Mobiles, and port numbers for Laptops. Defaults to None.

        Returns:
            (device_list, report_labels, device_macs) (tuple):    *device_list* (list): Port numbers of all the devices that are successfully connected to the given SSID.\n
            *report_labels* (list): Report Labels of all the devices that are successfully connected to the given SSID.\n
            Format: "Port_number OS-type hostname" trimmed to 25 characters.\n
            *device_macs* (list): MAC IDs of all the devices that are successfully connected to the given SSID.
        """
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
                                            selected_bands=['5g'],
                                            groups=groups,
                                            _debug_on=_debug_on,
                                            _exit_on_error=_exit_on_error,
                                            all_android=all_android,
                                            all_laptops=all_laptops)
        d = self.real_device_class.query_all_devices_to_configure_wifi(
            device_list=device_list)
        device_list, report_labels, device_macs = asyncio.run(
            self.real_device_class.configure_wifi())
        return device_list, report_labels, device_macs

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
        """
        Method to start FTP test on the given device list

        Args:
            ssid (str): SSID of the DUT
            password (str): Password for the SSID. [BLANK] if encryption is open.
            security (str): Encryption for the SSID.
            ap_name (str, optional): Name of the AP. Defaults to ''.
            band (str, optional): 2g, 5g or 6g. Defaults to '5g'.
            direction (str, optional): Download or Upload. Defaults to 'Download'.
            file_size (str, optional): File Size. Defaults to '12MB'.
            traffic_duration (int, optional): Duration of the test in seconds. Defaults to 60.
            upstream (str, optional): Upstream port. Defaults to 'eth1'.
            lf_username (str, optional): Username of LANforge. Defaults to 'lanforge'.
            lf_password (str, optional): Password of LANforge. Defaults to 'lanforge'.
            ssh_port (int, optional): SSH port. Defaults to 22.
            clients_type (str, optional): Clients type. Defaults to 'Real'.
            device_list (list, optional): List of port numbers of the devices in shelf.resource format. Defaults to [].
            background (bool, optional): Enable this to just start the test. Disabling background makes the test to run for the given duration and then stop. Defaults to False.

        Returns:
            (test_start_time, ftp_object) (tuple): Test start time and ftp test object if background argument is set to True.\n

            *(test_start_time, test_end_time) (tuple)*: Test start time and end time if background is set to False.
        """
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
            logger.info(obj.get_fail_message())
            exit(1)

        # First time stamp
        test_start_time = datetime.datetime.now()
        logger.info("Traffic started running at ", test_start_time)
        obj.start(False, False)
        if (background):
            return test_start_time, obj
        time.sleep(traffic_duration)
        obj.stop()
        logger.info("Traffic stopped running")
        obj.my_monitor()
        obj.postcleanup()
        test_end_time = datetime.datetime.now()
        logger.info("Test ended at", test_end_time)
        return test_start_time, test_end_time

    def stop_ftp_test(self, ftp_object):
        """
        Method to stop the ftp test.

        Args:
            ftp_object (object): FTP test object returned from *start_ftp_test* method.

        Returns:
            test_end_time (datetime_object): FTP test end time.
        """
        ftp_object.stop()
        logger.info("Traffic stopped running")
        ftp_object.my_monitor()
        ftp_object.postcleanup()
        test_end_time = datetime.datetime.now()
        logger.info("FTP test ended at", test_end_time)
        return test_end_time
    
    def start_http_test(self):
        pass

    def stop_http_test(self):
        pass
    
    def start_throughput_test(self,
                            upstream_port= 'eth0',
                            traffic_type="lf_tcp",
                            device_list=[],
                            test_duration="60s",
                            upload_min_rate_bps=2560,
                            download_min_rate_bps=2560,
                            packet_size="-1",
                            incremental_capacity=[],
                            tos="Best_Efforts",
                            report_timer="5s",
                            load_type="wc_per_client_load",
                            do_interopability=False,
                            incremental=[],
                            precleanup=False,
                            postcleanup=False,
                              ):
        """
        Initiates a throughput test with various configurable parameters.

        Args:
            upstream_port (str): Specifies the port that generates traffic. 
                                Format should be <resource>.<port>, e.g., '1.eth1'.
                                Default is 'eth0'.
            traffic_type (str): Select the traffic type, e.g., 'lf_tcp' or 'lf_udp'.
                                Default is 'lf_tcp'.
            device_list (list): Enter the devices on which the test should be run.
                                Default is an empty list [].
            test_duration (str): Duration of the test, e.g., '60s'.
                                Default is '60s'.
            upload_min_rate_bps (int): Minimum upload rate per connection in bits per second.
                                    Default is 2560.
            download_min_rate_bps (int): Minimum download rate per connection in bits per second.
                                        Default is 2560.
            packet_size (str): Size of the packet in bytes. Should be greater than 16B and 
                            less than 64KB (65507). Default is '-1'.
            incremental_capacity (list): Incremental values for network load testing as a 
                                        comma-separated list, e.g., [10, 20, 30]. 
                                        Default is an empty list [].
            report_timer (int): Duration to collect data in seconds. Default is 5 seconds.
            load_type (str): Type of load, e.g., 'wc_intended_load' or 'wc_per_client_load'.
                            Default is 'wc_per_client_load'.
            do_interopability (bool): If true, will execute script for interoperability testing.
                                    Default is False.
            incremental (list): Allows user to enter incremental values for specific testing scenarios.
                                Default is an empty list [].
            precleanup (bool): If true, cleans up the cross-connections before starting the test.
                            Default is False.
            postcleanup (bool): If true, cleans up the cross-connections after stopping the test.
                                Default is False.
        Returns:
            returns individual_df: A DataFrame containing the test results.
        """
        if do_interopability:
            incremental_capacity='1'
        if test_duration.endswith('s') or test_duration.endswith('S'):
            test_duration = int(test_duration[0:-1])
    
        elif test_duration.endswith('m') or test_duration.endswith('M'):
            test_duration = int(test_duration[0:-1]) * 60 
    
        elif test_duration.endswith('h') or test_duration.endswith('H'):
            test_duration = int(test_duration[0:-1]) * 60 * 60 
        
        elif test_duration.endswith(''):
            test_duration = int(test_duration)

        # Parsing report_timer
        if report_timer.endswith('s') or report_timer.endswith('S') :
            report_timer=int(report_timer[0:-1]) 

        elif report_timer.endswith('m') or report_timer.endswith('M')   :
            report_timer=int(report_timer[0:-1]) * 60

        elif report_timer.endswith('h') or report_timer.endswith('H')  :
            report_timer=int(report_timer[0:-1]) * 60 * 60

        elif test_duration.endswith(''):        
            report_timer=int(report_timer)

        
        if (int(packet_size)<16 or int(packet_size)>65507) and int(packet_size)!=-1:
            logger.info("Packet size should be greater than 16 bytes and less than 65507 bytes incorrect")
            return
        obj=Throughput(host=self.lanforge_ip,
                       ip=self.lanforge_ip,
                       port=self.port,
                       test_duration=test_duration,
                       upstream=upstream_port,
                       side_a_min_rate=upload_min_rate_bps,
                       side_b_min_rate=download_min_rate_bps,
                       side_a_min_pdu=int(packet_size),
                       side_b_min_pdu=int(packet_size),
                       traffic_type=traffic_type,
                       incremental_capacity=incremental_capacity,
                       tos=tos,
                       device_list=device_list,
                       report_timer=report_timer,
                       load_type=load_type,
                       do_interopability=do_interopability,
                       incremental=incremental,
                       precleanup=precleanup,
                       )
        
        obj.os_type()
        iterations_before_test_stopped_by_user=[]
        check_condition,clients_to_run=obj.phantom_check()
        if check_condition==False:
            return
        check_increment_condition=obj.check_incremental_list()
        if check_increment_condition==False:
            logger.info("Incremental values given for selected devices are incorrect")
            return
        elif(len(incremental_capacity)>0 and check_increment_condition==False):
            logger.info("Incremental values given for selected devices are incorrect")
            return
        created_cxs = obj.build()
        time.sleep(10)
        created_cxs=list(created_cxs.keys())
        individual_dataframe_column=[]
        to_run_cxs,to_run_cxs_len,created_cx_lists_keys,incremental_capacity_list = obj.get_incremental_capacity_list()
        for i in range(len(clients_to_run)):
            # Extend individual_dataframe_column with dynamically generated column names
            individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop A {clients_to_run[i]}', f'Rx % Drop B{clients_to_run[i]}',f'RSSI {clients_to_run[i]} ',f'Link Speed {clients_to_run[i]} '])
        individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop A', 'Overall Rx % Drop B','Iteration','TIMESTAMP','Start_time','End_time','Remaining_Time','Incremental_list','status'])
        individual_df=pd.DataFrame(columns=individual_dataframe_column)
        overall_start_time=datetime.now()
        overall_end_time=overall_start_time + timedelta(seconds=int(test_duration)*len(incremental_capacity_list))
        for i in range(len(to_run_cxs)):
            # Check the load type specified by the user
            if load_type == "wc_intended_load":
                # Perform intended load for the current iteration
                obj.perform_intended_load(i,incremental_capacity_list)
                if i!=0:
                    # Stop throughput testing if not the first iteration
                    obj.stop()
                # Start specific connections for the current iteration
                obj.start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
            else:
                if (do_interopability and i!=0):
                    obj.stop_specific(to_run_cxs[i-1])
                    time.sleep(5)
                obj.start_specific(to_run_cxs[i])
            # Determine device names based on the current iteration
            device_names=created_cx_lists_keys[:to_run_cxs_len[i][-1]]
            # Monitor throughput and capture all dataframes and test stop status
            all_dataframes,test_stopped_by_user = obj.monitor(i,individual_df,device_names,incremental_capacity_list,overall_start_time,overall_end_time)
            # Check if the test was stopped by the user
            if test_stopped_by_user==False:
                # Append current iteration index to iterations_before_test_stopped_by_user
                iterations_before_test_stopped_by_user.append(i)
            else:
                # Append current iteration index to iterations_before_test_stopped_by_user 
                iterations_before_test_stopped_by_user.append(i)
                break
        obj.stop()
        if postcleanup:
            obj.cleanup()
        return individual_df

    def start_video_streaming_test(self, ssid="ssid_wpa_2g", passwd="something", encryp="psk",
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=0,
                        url="www.google.com", urls_per_tenm=100, duration="60", 
                        device_list=[], media_quality='0',media_source='1',
                        incremental = False,postcleanup=False,
                        precleanup=False,incremental_capacity=None):
        """
        Initiates a video streaming test with various configurable parameters.

        Args:
            ssid (str): Specify the SSID on which the test will be running.
                        Default is 'ssid_wpa_2g'.
            passwd (str): Specify the encryption password on which the test will be running.
                        Default is 'something'.
            encryp (str): Specify the encryption type for the network, e.g., 'open', 'psk', 'psk2', 'sae', 'psk2jsae'.
                        Default is 'psk'.
            suporrted_release (list): List of supported Android releases for the test. 
                                    Default is ["7.0", "10", "11", "12"].
            max_speed (int): Specify the maximum speed in bytes. 
                            Default is 0 (unlimited).
            url (str): Specify the URL to test the video streaming on.
                    Default is 'www.google.com'.
            urls_per_tenm (int): Number of URLs to test per ten minutes. 
                                Default is 100.
            duration (str): Duration to run the video streaming test. 
                            Default is '60'.
            device_list (list): Provide resource IDs of Android devices to run the test on, e.g., ["10", "12", "14"].
                                Default is an empty list [].
            media_quality (str): Specify the quality of the media for the test, e.g., '0' (low), '1' (medium), '2' (high).
                                Default is '0'.
            media_source (str): Specify the media source for the test, e.g., '1' (local), '2' (remote).
                                Default is '1'.
            incremental (bool): Enables incremental testing with specified values. 
                                Default is False.
            postcleanup (bool): If true, cleans up the connections after the test is stopped.
                                Default is False.
            precleanup (bool): If true, cleans up the connections before the test is started.
                            Default is False.
            incremental_capacity (str): Specify the incremental values for load testing, e.g., "1,2,3".
                                        Default is None.
        Returns:
            returns individual_df: A DataFrame containing the test results.
        """
        media_source_dict={
                       'dash':'1',
                       'smooth_streaming':'2',
                       'hls':'3',
                       'progressive':'4',
                       'rtsp':'5'
                       }
        media_quality_dict={
                            '4k':'0',
                            '8k':'1',
                            '1080p':'2',
                            '720p':'3',
                            '360p':'4'
                            }
        webgui_incremental=incremental_capacity

        media_source,media_quality=media_source.capitalize(),media_quality
        media_source=media_source.lower()
        media_quality=media_quality.lower()

        if any(char.isalpha() for char in media_source):
            media_source=media_source_dict[media_source]

        if any(char.isalpha() for char in media_quality):
            media_quality=media_quality_dict[media_quality]


        obj = VideoStreamingTest(host=self.lanforge_ip, ssid=ssid, passwd=passwd, encryp=encryp,
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=max_speed,
                        url=url, urls_per_tenm=urls_per_tenm, duration=duration, 
                        resource_ids = device_list, media_quality=media_quality,media_source=media_source,
                        incremental = incremental,postcleanup=postcleanup,
                        precleanup=precleanup)
        resource_ids_sm = []
        resource_set = set()
        resource_list = []
        resource_ids_generated = ""

        obj.android_devices = obj.devices.get_devices(only_androids=True)

        if device_list:
            # Extract second part of resource IDs and sort them
            obj.resource_ids = ",".join(id.split(".")[1] for id in device_list.split(","))
            resource_ids_sm = obj.resource_ids
            resource_list = resource_ids_sm.split(',')            
            resource_set = set(resource_list)
            resource_list_sorted = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list_sorted)

            # Convert resource IDs into a list of integers
            num_list = list(map(int, obj.resource_ids.split(',')))

            # Sort the list
            num_list.sort()

            # Join the sorted list back into a string
            sorted_string = ','.join(map(str, num_list))
            obj.resource_ids = sorted_string

            # Extract the second part of each Android device ID and convert to integers
            modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))
            # modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), obj.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
            new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in obj.android_devices]

            resources_list = device_list.split(",")
            for element in resources_list:
                if element in new_list_android:
                    for ele in obj.android_devices:
                        if ele.startswith(element):
                            obj.android_list.append(ele)
                else:
                    logger.info("{} device is not available".format(element))
            new_android = [int(item.split('.')[1]) for item in obj.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(set(resource_ids))

        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices,report_labels,selected_macs = obj.devices.query_user()
            # Handle cases where no devices are selected
            
            if not selected_devices:
                logger.info("devices donot exist..!!")
                return 
                
            obj.android_list = selected_devices
            if obj.android_list:
                resource_ids = ",".join([item.split(".")[1] for item in obj.android_list])

                num_list = list(map(int, resource_ids.split(',')))

                # Sort the list
                num_list.sort()

                # Join the sorted list back into a string
                sorted_string = ','.join(map(str, num_list))

                obj.resource_ids = sorted_string
                resource_ids1 = list(map(int, sorted_string.split(',')))
                modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))
                if not all(x in modified_list for x in resource_ids1):
                    logger.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = obj.resource_ids
                resource_list = resource_ids_sm.split(',')            
                resource_set = set(resource_list)
                resource_list_sorted = sorted(resource_set)
                resource_ids_generated = ','.join(resource_list_sorted)
                available_resources=list(resource_set)
    
        if len(available_resources)==0:
            logger.info("No devices which are selected are available in the lanforge")
            exit()
        gave_incremental=False
        if len(resource_list_sorted)==0:
            logger.info("Selected Devices are not available in the lanforge")
            exit(1)
        if incremental and not webgui_incremental :
            if obj.resource_ids:
                logger.info("The total available devices are {}".format(len(available_resources)))
                obj.incremental = input('Specify incremental values as 1,2,3 : ')
                obj.incremental = [int(x) for x in obj.incremental.split(',')]
            else:
                logger.info("incremental Values are not needed as Android devices are not selected..")
        elif incremental==False:
            gave_incremental=True
            obj.incremental=[len(available_resources)]
        
        if webgui_incremental:
            incremental = [int(x) for x in webgui_incremental.split(',')]
            if (len(webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(webgui_incremental) > 1):
                obj.incremental = incremental
        
        if obj.incremental and obj.resource_ids:
            resources_list1 = [str(x) for x in obj.resource_ids.split(',')]
            if resource_list_sorted:
                resources_list1 = resource_list_sorted
            if obj.incremental[-1] > len(available_resources):
                logger.info("Exiting the program as incremental values are greater than the resource ids provided")
                exit()
            elif obj.incremental[-1] < len(available_resources) and len(obj.incremental) > 1:
                logger.info("Exiting the program as the last incremental value must be equal to selected devices")
                exit()
        
        # To create cx for selected devices
        obj.build()

        # To set media source and media quality 
        time.sleep(10)

        # obj.run
        test_time = datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logger.info("Initiating Test...")

        individual_dataframe_columns=[]

        keys = list(obj.http_profile.created_cx.keys())
    
        #TODO : To create cx for laptop devices
        # if (not no_laptops) and obj.other_list:
        #     obj.create_generic_endp(obj.other_list,os_types_dict)

        # Extend individual_dataframe_column with dynamically generated column names
        for i in range(len(keys)):
            individual_dataframe_columns.extend([f'video_format_bitrate{keys[i]}', f'total_wait_time{keys[i]}',f'total_urls{keys[i]}',f'RSSI{keys[i]}',f'Link Speed{keys[i]}',f'Total Buffer {keys[i]}',f'Total Errors {keys[i]}',f'Min_Video_Rate{keys[i]}',f'Max_Video_Rate{keys[i]}',f'Avg_Video_Rate{keys[i]}'])
        individual_dataframe_columns.extend(['overall_video_format_bitrate','timestamp','iteration','start_time','end_time','remaining_Time','status'])
        individual_df=pd.DataFrame(columns=individual_dataframe_columns)
        
        cx_order_list = []
        index = 0
        file_path = ""

        # Parsing test_duration
        if duration.endswith('s') or duration.endswith('S'):
            duration = round(int(duration[0:-1])/60,2)
        
        elif duration.endswith('m') or duration.endswith('M'):
            duration = int(duration[0:-1]) 
    
        elif duration.endswith('h') or duration.endswith('H'):
            duration = int(duration[0:-1]) * 60  
        
        elif duration.endswith(''):
            duration = int(duration)

        incremental_capacity_list_values=obj.get_incremental_capacity_list()
        if incremental_capacity_list_values[-1]!=len(available_resources):
            logger.info("Incremental capacity doesnt match available devices")
            if postcleanup==True:
                obj.postcleanup()
            exit(1)
        # Process resource IDs and incremental values if specified
        if obj.resource_ids:
            if obj.incremental:
                test_setup_info_incremental_values =  ','.join([str(n) for n in incremental_capacity_list_values])
                if len(obj.incremental) == len(available_resources):
                    test_setup_info_total_duration = duration
                elif len(obj.incremental) == 1 and len(available_resources) > 1:
                    if obj.incremental[0] == len(available_resources):
                        test_setup_info_total_duration = duration
                    else:
                        div = len(available_resources)//obj.incremental[0] 
                        mod = len(available_resources)%obj.incremental[0] 
                        if mod == 0:
                            test_setup_info_total_duration = duration * (div )
                        else:
                            test_setup_info_total_duration = duration * (div + 1)
                else:
                    test_setup_info_total_duration = duration * len(incremental_capacity_list_values)
                # if incremental_capacity_list_values[-1] != len(available_resources):
                #     test_setup_info_duration_per_iteration= duration 
            else:
                test_setup_info_total_duration = duration
                
            if webgui_incremental:
                test_setup_info_incremental_values =  ','.join([str(n) for n in incremental_capacity_list_values])
            elif gave_incremental:
                test_setup_info_incremental_values = "No Incremental Value provided"
            obj.total_duration = test_setup_info_total_duration

        actual_start_time=datetime.now()

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        if obj.resource_ids:
            # Check if incremental  is specified
            if obj.incremental:

                # Case 1: Incremental list has only one value and it equals the length of keys
                if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])

                # Case 2: Incremental list has only one value but length of keys is greater than 1
                elif len(obj.incremental) == 1 and len(keys) > 1:
                    incremental_value = obj.incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index

                # Case 3: Incremental list has multiple values and length of keys is greater than 1
                elif len(obj.incremental) != 1 and len(keys) > 1:
                    
                    index = 0
                    for num in obj.incremental:
                        
                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])
                        start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Iterate over cx_order_list to start tests incrementally
                for i in range(len(cx_order_list)):
                    if i == 0:
                        obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] 
                        end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        obj.data['end_time_webGUI'] = [end_time_webGUI] 


                    # time.sleep(10)

                    # Start specific devices based on incremental capacity
                    obj.start_specific(cx_order_list[i])
                    if cx_order_list[i]:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    else:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    
                    file_path = "video_streaming_realtime_data.csv"

                    if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        obj.data['remaining_time_webGUI'] = ['0:00'] 
                    else:
                        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        obj.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] 
                    
                    obj.monitor_for_runtime_csv(duration,file_path,individual_df,i,actual_start_time,resource_list_sorted,cx_order_list[i])
        obj.stop()

        if obj.resource_ids:
            
            # date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

            # phone_list = obj.get_resource_data() 

            username = []
            
            try:
                eid_data = obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
            except KeyError:
                logger.info("Error: 'interfaces' key not found in port data")
                exit(1)

            resource_ids = list(map(int, obj.resource_ids.split(',')))
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            username.append(resource_hw_data['resource']['user'] )

            logger.info("Test Stopped")
            if postcleanup==True:
                obj.postcleanup()

        return individual_df

    def start_web_browser_test(self,ssid="ssid_wpa_2g", passwd="something", encryp="psk",
                    suporrted_release=["7.0", "10", "11", "12"], max_speed=0,
                    url="www.google.com", count=1, duration="60s", 
                    device_list="", 
                    incremental = False,incremental_capacity=None,postcleanup=False,
                    precleanup=False):
        """
        Initiates a web browser test with various configurable parameters.

        Args:
            ssid (str): Specify the SSID on which the test will be running.
                        Default is 'ssid_wpa_2g'.
            passwd (str): Specify the encryption password on which the test will be running.
                        Default is 'something'.
            encryp (str): Specify the encryption type for the network, e.g., 'open', 'psk', 'psk2', 'sae', 'psk2jsae'.
                        Default is 'psk'.
            suporrted_release (list): List of supported Android releases for the test.
                                    Default is ["7.0", "10", "11", "12"].
            max_speed (int): Specify the maximum speed in bytes. 
                            Default is 0 (unlimited).
            url (str): Specify the URL to test the web browser on.
                    Default is 'www.google.com'.
            count (int): Specify the number of URLs to calculate the time taken to reach them.
                        Default is 1.
            duration (str): Duration to run the web browser test.
                            Default is '60s'.
            device_list (str): Provide resource IDs of Android devices to run the test on, e.g., "10,12,14".
                            Default is an empty string "".
            incremental (bool): Enables incremental testing with specified values.
                                Default is False.
            incremental_capacity (str): Specify the incremental values for load testing, e.g., "1,2,3".
                                        Default is None.
            postcleanup (bool): If true, cleans up the connections after the test is stopped.
                                Default is False.
            precleanup (bool): If true, cleans up the connections before the test is started.
                            Default is False.
        Returns:
            returns obj.data: A DataFrame containing the test results.
        """
        webgui_incremental=incremental_capacity
        obj = RealBrowserTest(host=self.lanforge_ip, ssid=ssid, passwd=passwd, encryp=encryp,
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=max_speed,
                        url=url, count=count, duration=duration, 
                        resource_ids = device_list,
                        incremental = incremental,postcleanup=postcleanup,
                        precleanup=precleanup)
        resource_ids_sm = []
        resource_set = set()
        resource_list = []
        os_types_dict = {}

        resource_ids_generated = ""
        #  Process resource IDs when web GUI is enabled

        obj.android_devices = obj.devices.get_devices(only_androids=True)

        
        # Process resource IDs if provided
        if device_list:
            # Extract second part of resource IDs and sort them
            obj.resource_ids = ",".join(id.split(".")[1] for id in device_list.split(","))
            resource_ids_sm = obj.resource_ids
            resource_list = resource_ids_sm.split(',')            
            resource_set = set(resource_list)
            resource_list_sorted = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list_sorted)

            # Convert resource IDs into a list of integers
            num_list = list(map(int, obj.resource_ids.split(',')))

            # Sort the list
            num_list.sort()

            # Join the sorted list back into a string
            sorted_string = ','.join(map(str, num_list))
            obj.resource_ids = sorted_string

            # Extract the second part of each Android device ID and convert to integers
            modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))
            modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), obj.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
            new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in obj.android_devices]

            resources_list = device_list.split(",")
            for element in resources_list:
                if element in new_list_android:
                    for ele in obj.android_devices:
                        if ele.startswith(element):
                            obj.android_list.append(ele)
                else:
                    logger.info("{} device is not available".format(element))
            new_android = [int(item.split('.')[1]) for item in obj.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(set(resource_ids))
            
        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices,report_labels,selected_macs = obj.devices.query_user()
            # Handle cases where no devices are selected
            if not selected_devices:
                logger.info("devices donot exist..!!")
                return 
            
            obj.android_list = selected_devices
            

            
            # Verify if all resource IDs are valid for Android devices
            if obj.android_list:
                resource_ids = ",".join([item.split(".")[1] for item in obj.android_list])

                num_list = list(map(int, resource_ids.split(',')))

                # Sort the list
                num_list.sort()

                # Join the sorted list back into a string
                sorted_string = ','.join(map(str, num_list))

                obj.resource_ids = sorted_string
                resource_ids1 = list(map(int, sorted_string.split(',')))
                modified_list = list(map(lambda item: int(item.split('.')[1]), obj.android_devices))

                # Check for invalid resource IDs
                if not all(x in modified_list for x in resource_ids1):
                    logger.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = obj.resource_ids
                resource_list = resource_ids_sm.split(',')            
                resource_set = set(resource_list)
                resource_list_sorted = sorted(resource_set)
                resource_ids_generated = ','.join(resource_list_sorted)
                available_resources=list(resource_set)

        logger.info("Devices available: {}".format(available_resources))
        if len(available_resources)==0:
            logger.info("There no devices available which are selected")
            exit()
        # Handle incremental values input if resource IDs are specified and in not specified case.
        if incremental and not webgui_incremental :
            if obj.resource_ids:
                obj.incremental = input('Specify incremental values as 1,2,3 : ')
                obj.incremental = [int(x) for x in obj.incremental.split(',')]
            else:
                logger.info("incremental Values are not needed as Android devices are not selected..")
        
        # Handle webgui_incremental argument
        if webgui_incremental:
            incremental = [int(x) for x in webgui_incremental.split(',')]
            # Validate the length and assign incremental values
            if (len(webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(webgui_incremental) > 1):
                obj.incremental = incremental
            elif len(webgui_incremental) == 1:
                obj.incremental = incremental

        # if obj.incremental and (not obj.resource_ids):
        #     logger.info("incremental values are not needed as Android devices are not selected.")
        #     exit()
        
        # Validate incremental and resource IDs combination
        if (obj.incremental and obj.resource_ids) or (webgui_incremental):
            resources_list1 = [str(x) for x in obj.resource_ids.split(',')]
            if resource_list_sorted:
                resources_list1 = resource_list_sorted
            # Check if the last incremental value is greater or less than resources provided
            if obj.incremental[-1] > len(available_resources):
                logger.info("Exiting the program as incremental values are greater than the resource ids provided")
                exit()
            elif obj.incremental[-1] < len(available_resources) and len(obj.incremental) > 1:
                logger.info("Exiting the program as the last incremental value must be equal to selected devices")
                exit()

        # obj.run
        test_time = datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logger.info("Initiating Test...")
        available_resources= [int(n) for n in available_resources]
        available_resources.sort()
        available_resources_string=",".join([str(n) for n in available_resources])
        obj.set_available_resources_ids(available_resources_string)
        # obj.set_available_resources_ids([int(n) for n in available_resources].sort())
        obj.build()
        time.sleep(10)
        #TODO : To create cx for laptop devices
        # Create end-points for devices other than Android if specified
        # if (not no_laptops) and obj.other_list:
        #     obj.create_generic_endp(obj.other_list,os_types_dict)

        keys = list(obj.http_profile.created_cx.keys())
        if len(keys)==0:
            logger.info("Selected Devices are not available in the lanforge")
            exit(1)
        cx_order_list = []
        index = 0
        file_path = ""

        if duration.endswith('s') or duration.endswith('S'):
            duration = round(int(duration[0:-1])/60,2)
        
        elif duration.endswith('m') or duration.endswith('M'):
            duration = int(duration[0:-1]) 
    
        elif duration.endswith('h') or duration.endswith('H'):
            duration = int(duration[0:-1]) * 60  
        
        elif duration.endswith(''):
            duration = int(duration)

        if incremental or webgui_incremental:
            incremental_capacity_list_values=obj.get_incremental_capacity_list()
            if incremental_capacity_list_values[-1]!=len(available_resources):
                logger.info("Incremental capacity doesnt match available devices")
                if postcleanup==True:
                    obj.postcleanup()
                exit(1)

        # Process resource IDs and incremental values if specified
        if obj.resource_ids:
            if obj.incremental:
                test_setup_info_incremental_values =  ','.join(map(str, incremental_capacity_list_values))
                if len(obj.incremental) == len(available_resources):
                    test_setup_info_total_duration = duration
                elif len(obj.incremental) == 1 and len(available_resources) > 1:
                    if obj.incremental[0] == len(available_resources):
                        test_setup_info_total_duration = duration
                    else:
                        div = len(available_resources)//obj.incremental[0] 
                        mod = len(available_resources)%obj.incremental[0] 
                        if mod == 0:
                            test_setup_info_total_duration = duration * (div )
                        else:
                            test_setup_info_total_duration = duration * (div + 1)
                else:
                    test_setup_info_total_duration = duration * len(incremental_capacity_list_values)
                # test_setup_info_duration_per_iteration= duration 
            elif webgui_incremental:
                test_setup_info_incremental_values = ','.join(map(str, incremental_capacity_list_values))
                test_setup_info_total_duration = duration * len(incremental_capacity_list_values)
            else:
                test_setup_info_incremental_values = "No Incremental Value provided"
                test_setup_info_total_duration = duration
            obj.total_duration = test_setup_info_total_duration

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        gave_incremental,iteration_number=True,0
        if obj.resource_ids:
            if not obj.incremental:
                obj.incremental=[len(keys)]
                gave_incremental=False
            if obj.incremental or not gave_incremental:
                if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])
                elif len(obj.incremental) == 1 and len(keys) > 1:
                    incremental_value = obj.incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index
                elif len(obj.incremental) != 1 and len(keys) > 1:
                    
                    index = 0
                    for num in obj.incremental:
                        
                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])
                        start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Update start and end times for webGUI
                for i in range(len(cx_order_list)):
                    if i == 0:
                        obj.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(keys)
                        # if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(obj.incremental) == 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(obj.incremental) != 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                        # if len(obj.incremental) == 1 and obj.incremental[0] == len(keys):
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(obj.incremental) == 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(obj.incremental) != 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')

                        end_time_webGUI = (datetime.now() + timedelta(minutes = obj.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        obj.data['end_time_webGUI'] = [end_time_webGUI] * len(keys)


                    obj.start_specific(cx_order_list[i])
                    
                    iteration_number+=len(cx_order_list[i])
                    if cx_order_list[i]:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    else:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    
                    # duration = 60 * duration
                    file_path = "webBrowser.csv"

                    start_time = time.time()
                    df = pd.DataFrame(obj.data)

                    if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        obj.data['remaining_time_webGUI'] = ['0:00'] * len(keys)
                    else:
                        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        obj.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] * len(keys)
                    # Monitor runtime and save results
                    
                    obj.monitor_for_runtime_csv(duration,file_path,iteration_number,resource_list_sorted,cx_order_list[i])
                        # time.sleep(duration)
                
        obj.stop()

        

        # Additional setup for generating reports and post-cleanup
        if obj.resource_ids:
            # uc_avg_val = obj.my_monitor('uc-avg')
            total_urls = obj.my_monitor('total-urls')

            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

            # Retrieve resource data for Android devices
            phone_list = obj.get_resource_data() 

            # Initialize and retrieve username data
            username = []
            eid_data = obj.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")

            resource_ids = list(map(int, obj.resource_ids.split(',')))
            # Extract username information from resource data
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = obj.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            username.append(resource_hw_data['resource']['user'] )

            # Construct device list string for report
            device_list_str = ','.join([f"{name} ( Android )" for name in username])



            # Retrieve additional monitoring data
            # total_urls = obj.my_monitor('total-urls')
            uc_min_val = obj.my_monitor('uc-min')
            timeout = obj.my_monitor('timeout')
            uc_min_value = uc_min_val
            dataset2 = total_urls
            dataset = timeout
            lis = username
            bands = ['URLs']
            obj.data['total_urls'] = total_urls
            obj.data['uc_min_val'] = uc_min_val 
            obj.data['timeout'] = timeout
        logger.info("Test Completed")

        # Handle incremental values and generate reports accordingly
        prev_inc_value = 0
        if obj.resource_ids and obj.incremental :
            for i in range(len(cx_order_list)):
                df = pd.DataFrame(obj.data)
                names_to_increment = cx_order_list[i] 

                if 'inc_value' not in df.columns:
                    df['inc_value'] = 0
                if i == 0:
                    prev_inc_value = len(cx_order_list[i])
                else:
                    prev_inc_value = prev_inc_value + len(cx_order_list[i])
                    
                obj.data['inc_value'] = df.apply(
                    lambda row: (
                        prev_inc_value  # Accumulate inc_value
                        if row['inc_value'] == 0 and row['name'] in names_to_increment 
                        else row['inc_value']  # Keep existing inc_value
                    ), 
                    axis=1
                )

                df1 = pd.DataFrame(obj.data)

                
                df1.to_csv(file_path, mode='w', index=False)     
        if postcleanup:
            obj.postcleanup()
        logger.info("Test Stopped")


        return obj.data


logger_config = lf_logger_config.lf_logger_config()

candela_apis = Candela(ip='192.168.214.61', port=8080)
# device_list, report_labels, device_macs = candela_apis.start_connectivity(
#     manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]', device_list=['RZ8N10FFTKE', 'RZ8NB1KWXLB'])
# logger.info(device_list, report_labels, device_macs)
# # device_list, report_labels, device_macs = candela_apis.start_connectivity(manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]')
# candela_apis.start_ftp_test(ssid='Walkin_open', password='[BLANK]', security='open', bands=[
#                             '5G'], directions=['Download'], file_sizes=['10MB'], device_list=','.join(device_list))

# print(candela_apis.start_throughput_test(traffic_type="lf_udp",
#                                    device_list='1.13,1.18,1.19,1.20,1.21',
#                                     upload_min_rate_bps=1000000,
#                                     download_min_rate_bps=100000,
#                                     upstream_port="eth1",
#                                     # packet_size="-1",
#                                     # incremental_capacity=[],
#                                     report_timer="5s",
#                                     load_type="wc_intended_load",
#                                     # incremental_capacity="1",
#                                     test_duration="30s",
#                                     precleanup=True,
#                                     postcleanup=True,
#                                     packet_size=18
#                                    ))

# candela_apis.start_throughput_test(traffic_type="lf_udp",
#                                    device_list="1.13,1.18",
#                                    upload_min_rate_bps=1000000,
#                                     download_min_rate_bps=100000,
#                                     upstream_port="eth1",
#                                     # packet_size="-1",
#                                     report_timer="5s",
#                                     test_duration="30s",
#                                     do_interopability=True,
#                                     precleanup=True,
#                                     postcleanup=True
#                                    )

# print(candela_apis.start_video_streaming_test(url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
#                                         media_source="hls",
#                                         media_quality="4k",
#                                         duration="1m",
#                                         device_list='1.13,1.18,1.19,1.20,1.21',
#                                         precleanup=True,
#                                         postcleanup=True,
#                                         # incremental_capacity="1"
#                                         ))

# print(candela_apis.start_web_browser_test(device_list="1.13,1.18,1.22,1.23,1.24,1.25,1.26,1.27", 
#                                           incremental_capacity="5",
#                                           duration="30s",
#                                           url="http://www.google.com",
#                                             count=6))