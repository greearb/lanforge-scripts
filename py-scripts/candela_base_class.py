import asyncio
import importlib
import datetime
from datetime import datetime, timedelta
import time
import requests
import threading
import logging
import pandas as pd
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
import lf_webpage as http_test
import lf_interop_qos as qos_test
import lf_interop_ping as ping_test
from lf_interop_throughput import Throughput
from lf_interop_video_streaming import VideoStreamingTest
from lf_interop_real_browser_test import RealBrowserTest
from test_l3 import L3VariableTime
from lf_kpi_csv import lf_kpi_csv
import lf_cleanup
througput_test=importlib.import_module("py-scripts.lf_interop_throughput")
video_streaming_test=importlib.import_module("py-scripts.lf_interop_video_streaming")
web_browser_test=importlib.import_module("py-scripts.lf_interop_real_browser_test")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
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
        self.cleanup = lf_cleanup.lf_clean(host=self.lanforge_ip, port=self.port, resource='all')
        self.ftp_test = None
        self.http_test = None
        
        self.iterations_before_test_stopped_by_user=None
        self.incremental_capacity_list=None
        self.all_dataframes=None
        self.to_run_cxs_len=None
        self.date=None
        self.test_setup_info=None
        self.individual_df=None
        self.cx_order_list=None
        self.dataset2=None 
        self.dataset = None
        self.lis = None 
        self.bands = None 
        self.total_urls = None
        self.uc_min_value = None  
        self.cx_order_list = None
        self.gave_incremental=None

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
            all_devices (dict): returns both the port data and resource mgr data with shelf.resource as the key
        """
        androids, linux, macbooks, windows, iOS = [], [], [], [], []
        all_devices = {}

        # querying resource manager tab for fetching laptops data
        resource_manager_tab_response, resource_manager_data = self.api_get(
            endp='/resource/all')
        if resource_manager_tab_response.status_code != 200:
            logger.info('Error fetching the data with the {}. Returned {}'.format(
                '/resources/all', resource_manager_tab_response))
            return resource_manager_tab_response
        resources_list = [resource_manager_data['resource']
                          if 'resource' in resource_manager_data else resource_manager_data['resources']][0]
        for resource in resources_list:
            resource_port, resource_data = list(resource.keys())[
                0], list(resource.values())[0]
            if resource_data['phantom']:
                continue
            if resource_data['ct-kernel'] is False:
                if resource_data['app-id'] == '0':
                    if 'Win' in resource_data['hw version']:
                        windows.append(resource_data)
                    elif 'Apple' in resource_data['hw version']:
                        macbooks.append(resource_data)
                    elif 'Linux' in resource_data['hw version']:
                        linux.append(resource_data)
                else:
                    if 'Apple' in resource_data['hw version']:
                        iOS.append(resource_data)
                    else:
                        androids.append(resource_data)
                all_devices[resource_port] = resource_data
                shelf, resource = resource_port.split('.')
                _, port_data = self.api_get(endp='/port/{}/{}'.format(shelf, resource))
                for port_id in port_data['interfaces']:
                    port_id_values = list(port_id.values())[0]
                    _, all_columns = self.api_get(endp=port_id_values['_links'])
                    all_columns = all_columns['interface']
                    if all_columns['parent dev'] == 'wiphy0':
                        all_devices[resource_port].update(all_columns)
        return all_devices

    def get_client_connection_details(self, device_list: list):
        """
        Method to return SSID, BSSID and Signal Strength details of the ports mentioned in the device list argument.

        Args:
            device_list (list): List of all the ports. E.g., ['1.10.wlan0', '1.11.wlan0']

        Returns:
            connection_details (dict): Dictionary containing port number as the key and SSID, BSSID, Signal as the values for each device in the device_list.
        """        
        connection_details = {}
        for device in device_list:
            shelf, resource, port_name = device.split('.')
            _, device_data = self.api_get('/port/{}/{}/{}?fields=ssid,ap,signal,mac'.format(shelf, resource, port_name))
            device_data = device_data['interface']
            connection_details[device] = device_data
        return connection_details

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
                       traffic_duration=None,
                       upstream='eth1',
                       lf_username='lanforge',
                       lf_password='lanforge',
                       ssh_port=22,
                       clients_type='Real',
                       device_list=[]):
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

        Returns:
            data (dict): Test results.
        """
        # for band in bands:
        #     for direction in directions:
        #         for file_size in file_sizes:
        # Start Test
        self.ftp_test = FtpTest(lfclient_host=self.lanforge_ip,
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

        self.ftp_test.data = {}
        self.ftp_test.file_create()
        if clients_type == "Real":
            self.ftp_test.query_realclients()
        self.ftp_test.set_values()
        self.ftp_test.count = 0
        self.ftp_test.radio = '1.1.wiphy0'
        # obj.precleanup()
        self.ftp_test.build()
        if not self.ftp_test.passes():
            logger.info(self.ftp_test.get_fail_message())
            exit(1)

        # First time stamp
        test_start_time = datetime.now()
        logger.info("Traffic started running at {}".format(test_start_time))
        self.ftp_test.start_time = test_start_time
        self.ftp_test.start(False, False)
        if self.ftp_test.traffic_duration:
            time.sleep(int(self.ftp_test.traffic_duration))
            self.stop_ftp_test()
            self.generate_report_ftp_test()
        

    def stop_ftp_test(self):
        self.ftp_test.stop()
        logger.info("Traffic stopped running")
        self.ftp_test.my_monitor()
        self.ftp_test.postcleanup()
        test_end_time = datetime.now()
        logger.info("Test ended at {}".format(test_end_time))
        self.ftp_test.end_time = test_end_time

    def generate_report_ftp_test(self):

        date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
        input_setup_info = {
            "AP": self.ftp_test.ap_name,
            "File Size": self.ftp_test.file_size,
            "Bands": self.ftp_test.band,
            "Direction": self.ftp_test.direction,
            "Stations": len(self.ftp_test.device_list),
            "Upstream": self.ftp_test.upstream,
            "SSID": self.ftp_test.ssid,
            "Security": self.ftp_test.security,
            "Contact": "support@candelatech.com"
        }
        if not self.ftp_test.traffic_duration:
            self.ftp_test.traffic_duration = (self.ftp_test.end_time - self.ftp_test.start_time).seconds
        self.ftp_test.generate_report(self.ftp_test.data, date, input_setup_info, bands=self.ftp_test.band,
                        test_rig="", test_tag="", dut_hw_version="",
                        dut_sw_version="", dut_model_num="",
                        dut_serial_num="", test_id="FTP Data",
                        csv_outfile="",
                        local_lf_report_dir="")
        return self.ftp_test.data

    def start_http_test(self, ssid, password, security, http_file_size, device_list, report_labels, device_macs,
                  target_per_ten, upstream='eth1', ap_name='', http_test=http_test, all_bands=False, windows_ports=[],
                  band='5G', lf_username='lanforge', lf_password='lanforge', 
                  test_duration=None):
        """
        Method to start HTTP test on the given device list

        Args:
            ssid (str): SSID
            password (str): Password for the SSID. [BLANK] in case of open encryption.
            security (str): Security for the SSID.
            http_file_size (str): HTTP file size.
            device_list (list): List of the ports on which the test should be initiated.
            report_labels (list): Report labels of the device list. Naming convention for the reporting.
            device_macs (list): MAC IDs for the given device list.
            target_per_ten (int): 
            upstream (str, optional): Upstream port. Defaults to 'eth1'.
            ap_name (str, optional): AP name. Defaults to ''.
            http_test (http_test_class, optional): Defaults to http_test.
            all_bands (bool, optional): Defaults to False.
            windows_ports (list, optional): Windows port list if Windows devices are included in the test. Defaults to [].
            band (str, optional): Defaults to '5G'.
            lf_username (str, optional): Defaults to 'lanforge'.
            lf_password (str, optional): Defaults to 'lanforge'.
            test_duration (int, optional): Duration to run the test in seconds. Defaults to 60.
        Raises:
            ValueError: If band argument does not contain 2.4G, 5G or 6G.

        Returns:
            result_data (dict): Result data of the test.
        """        
        http_test_duration = test_duration
        # Error checking to prevent case issues
        Bands = [band]
        for bands in range(len(Bands)):
            Bands[bands] = Bands[bands].upper()
            if Bands[bands] == "BOTH":
                Bands[bands] = "Both"

        # Error checking for non-existent bands
        valid_bands = ['2.4G', '5G', '6G', 'Both']
        for bands in Bands:
            if bands not in valid_bands:
                raise ValueError(
                    "Invalid band '%s' used in bands argument!" % bands)

        # Check for Both being used independently
        if len(Bands) > 1 and "Both" in Bands:
            raise ValueError("'Both' test type must be used independently!")

        
        num_stations = 0
        
        num_stations = len(device_list)
        self.http_test = http_test.HttpDownload(lfclient_host=self.lanforge_ip, lfclient_port=self.port,
                                               upstream=upstream,
                                               num_sta=num_stations,
                                               ap_name=ap_name, ssid=ssid, password=password, security=security,
                                               target_per_ten=target_per_ten, file_size=http_file_size, bands=band,
                                               client_type="Real", lf_username=lf_username,
                                               lf_password=lf_password)
        self.http_test.http_test_duration = http_test_duration
        self.http_test.Bands = Bands
        self.http_test.data = {}
        self.http_test.port_list = device_list
        self.http_test.devices_list = report_labels
        self.http_test.macid_list = device_macs
        self.http_test.user_query = [device_list, report_labels, device_macs]
        self.http_test.windows_ports = windows_ports
        self.http_test.file_create(ssh_port=22)
        self.http_test.set_values()
        self.http_test.precleanup()
        self.http_test.build()
        test_time = datetime.now()
        logger.info("HTTP Test started at {}".format(test_time))
        self.http_test.start()
        self.http_test.start_time = test_time
        if test_duration:
            time.sleep(self.http_test.http_test_duration)
            self.stop_http_test()
            self.generate_report_http_test()

    def stop_http_test(self):
        self.http_test.stop()
        self.http_test.end_time = datetime.now()

    def generate_report_http_test(self):

        http_sta_list = self.http_test.port_list
        num_stations = len(http_sta_list)
        Bands = self.http_test.Bands
        bands = self.http_test.bands
        band = bands
        lis = []
        list2G, list2G_bytes, list2G_speed, list2G_urltimes = [], [], [], []
        list5G, list5G_bytes, list5G_speed, list5G_urltimes = [], [], [], []
        list6G, list6G_bytes, list6G_speed, list6G_urltimes = [], [], [], []
        Both, Both_bytes, Both_speed, Both_urltimes = [], [], [], []
        dict_keys = []
        dict_keys.extend(Bands)
        final_dict = dict.fromkeys(dict_keys)
        dict1_keys = ['dl_time', 'min', 'max',
                      'avg', 'bytes_rd', 'speed', 'url_times']
        for i in final_dict:
            final_dict[i] = dict.fromkeys(dict1_keys)
        min2, min5, min6 = [], [], []
        min_both = []
        max2, max5, max6 = [], [], []
        max_both = []
        avg2, avg5, avg6 = [], [], []
        avg_both = []
        test_time = ""

        uc_avg_val = self.http_test.my_monitor('uc-avg')
        url_times = self.http_test.my_monitor('total-urls')
        rx_bytes_val = self.http_test.my_monitor('bytes-rd')
        rx_rate_val = self.http_test.my_monitor('rx rate')

        if bands == "2.4G":
            list2G.extend(uc_avg_val)
            list2G_bytes.extend(rx_bytes_val)
            list2G_speed.extend(rx_rate_val)
            list2G_urltimes.extend(url_times)
            final_dict['2.4G']['dl_time'] = list2G
            min2.append(min(list2G))
            final_dict['2.4G']['min'] = min2
            max2.append(max(list2G))
            final_dict['2.4G']['max'] = max2
            avg2.append((sum(list2G) / num_stations))
            final_dict['2.4G']['avg'] = avg2
            final_dict['2.4G']['bytes_rd'] = list2G_bytes
            final_dict['2.4G']['speed'] = list2G_speed
            final_dict['2.4G']['url_times'] = list2G_urltimes
        elif bands == "5G":
            list5G.extend(uc_avg_val)
            list5G_bytes.extend(rx_bytes_val)
            list5G_speed.extend(rx_rate_val)
            list5G_urltimes.extend(url_times)
            logger.info('{} {} {} {}'.format(list5G, list5G_bytes, list5G_speed, list5G_urltimes))
            final_dict['5G']['dl_time'] = list5G
            min5.append(min(list5G))
            final_dict['5G']['min'] = min5
            max5.append(max(list5G))
            final_dict['5G']['max'] = max5
            avg5.append((sum(list5G) / num_stations))
            final_dict['5G']['avg'] = avg5
            final_dict['5G']['bytes_rd'] = list5G_bytes
            final_dict['5G']['speed'] = list5G_speed
            final_dict['5G']['url_times'] = list5G_urltimes
        elif bands == "6G":
            list6G.extend(uc_avg_val)
            list6G_bytes.extend(rx_bytes_val)
            list6G_speed.extend(rx_rate_val)
            list6G_urltimes.extend(url_times)
            final_dict['6G']['dl_time'] = list6G
            min6.append(min(list6G))
            final_dict['6G']['min'] = min6
            max6.append(max(list6G))
            final_dict['6G']['max'] = max6
            avg6.append((sum(list6G) / num_stations))
            final_dict['6G']['avg'] = avg6
            final_dict['6G']['bytes_rd'] = list6G_bytes
            final_dict['6G']['speed'] = list6G_speed
            final_dict['6G']['url_times'] = list6G_urltimes
        elif bands == "Both":
            Both.extend(uc_avg_val)
            Both_bytes.extend(rx_bytes_val)
            Both_speed.extend(rx_rate_val)
            Both_urltimes.extend(url_times)
            final_dict['Both']['dl_time'] = Both
            min_both.append(min(Both))
            final_dict['Both']['min'] = min_both
            max_both.append(max(Both))
            final_dict['Both']['max'] = max_both
            avg_both.append((sum(Both) / num_stations))
            final_dict['Both']['avg'] = avg_both
            final_dict['Both']['bytes_rd'] = Both_bytes
            final_dict['Both']['speed'] = Both_speed
            final_dict['Both']['url_times'] = Both_urltimes

        result_data = final_dict
        logger.info("HTTP Test Result {}".format(result_data))
        test_end = self.http_test.end_time
        logger.info("HTTP Test Finished at {}".format(test_end))
        test_duration = (self.http_test.end_time - self.http_test.start_time).seconds
        logger.info("Total HTTP test duration: {}".format(test_duration))
        date = str(datetime.now()).split(
            ",")[0].replace(" ", "-").split(".")[0]

        test_setup_info = {
            "AP Name": self.http_test.ap_name,
            "SSID": self.http_test.ssid,
            "Security": self.http_test.security,
            "No of Devices": len(http_sta_list),
            "File size": self.http_test.file_size,
            "File location": "/usr/local/lanforge/nginx/html",
            "Traffic Direction": "Download",
            "Traffic Duration (seconds)": self.http_test.http_test_duration if self.http_test.http_test_duration else test_duration
        }

        for i in result_data:
            dataset = result_data[i]['dl_time']
            dataset2 = result_data[i]['url_times']
            bytes_rd = result_data[i]['bytes_rd']
        dataset1 = [float(f"{(i / 1000000): .4f}") for i in bytes_rd]
        logger.info("data sets {} {}".format(dataset, dataset2))
        if band == "Both":
            for i in range(1, len(http_sta_list) * 2 + 1):
                lis.append(i)
        else:
            for i in range(1, len(http_sta_list) + 1):
                lis.append(i)
        
        band = '_' + band
        self.http_test.generate_report(date, num_stations=len(http_sta_list), duration=self.http_test.http_test_duration,
                                        test_setup_info=test_setup_info, dataset=dataset, lis=lis,
                                        bands=Bands, threshold_2g="", threshold_5g="", threshold_both="",
                                        dataset1=dataset1,
                                        dataset2=dataset2, result_data=result_data, test_rig="", test_tag="",
                                        dut_hw_version="", dut_sw_version="", dut_model_num="", dut_serial_num="",
                                        test_id="", test_input_infor="", csv_outfile="",
                                        _results_dir_name=f'Webpage_Test_Report{band}',
                                        report_path="")
        self.cleanup.layer4_endp_clean()
        return result_data


    def start_qos_test(self,**kwargs):

        """
        Method to start QoS test on the given device list

        Args:
            ssid (str): SSID
            password (str): Password for the SSID. [BLANK] in case of open security.
            security (str): Encryption for the given SSID.
            ap_name (str): AP Name
           tos (list): List of all the TOS to initiate the test.
            upstream (str, optional): Upstream port. Defaults to 'eth1'.
            traffic_type (str, optional): lf_tcp incase of TCP traffic, lf_udp incase of UDP. Defaults to 'lf_udp'.
            side_a_min (int, optional): Min upload rate. Defaults to 6200000.
            side_b_min (int, optional): Min download rate. Defaults to 6200000.
            side_a_max (int, optional): Max upload rate. Use 0 if needs the same value as Min upload rate. Defaults to 0.
            side_b_max (int, optional): Max download rate. Use 0 if needs the same value as Min download rate. Defaults to 0.
            test_duration (int, optional): Duration of the test in seconds. Defaults to 60.
            qos_serial_run (bool, optional): Disable this if wanted to run on parallel. Defaults to True.
            device_list (list, optional): List containing the port names of the selected devices. Defaults to [].
            report_labels (list, optional): Report labels for the selected devices. Defaults to [].
            device_macs (list, optional): MAC IDs for the selected devices. Defaults to [].
            background_run(boolean, optional): To make the test run indefinetley. Default False 
        Returns:
            data (dict): Result data
        """


        background_run = kwargs.get("background_run",False)
        if background_run:
            self.qos_monitoring_thread=threading.Thread(target=self.start_qos,kwargs=kwargs)
            self.qos_monitoring_thread.start()
        else:
            self.start_qos(**kwargs)
    
    def start_qos(self, ssid, password, security,
                 ap_name, tos, upstream='eth1', traffic_type='lf_udp',
                 side_a_min=6200000, side_b_min=6200000, side_a_max=0, side_b_max=0, 
                 test_duration=60, qos_serial_run=False, device_list=[],
                 report_labels=[], device_macs=[],background_run = False):
        if not background_run:
            qos_test_duration = test_duration
        else:
            qos_serial_run=False
            qos_test_duration = 2

        test_results = {'test_results': []}
        data = {}
        # qos test for real clients
        def qos_test_overall_real(qos_tos_real=None):
            self.qos_test = qos_test.ThroughputQOS(host=self.lanforge_ip,
                                                    port=self.port,
                                                    number_template="0000",
                                                    ap_name=ap_name,
                                                    name_prefix="TOS-",
                                                    tos=qos_tos_real if qos_serial_run else ','.join(tos),
                                                    ssid=ssid,
                                                    password=password,
                                                    security=security,
                                                    upstream=upstream,
                                                    test_duration=qos_test_duration,
                                                    use_ht160=False,
                                                    side_a_min_rate=int(side_a_min),
                                                    side_b_min_rate=int(side_b_min),
                                                    side_a_max_rate=int(side_a_max),
                                                    side_b_max_rate=int(side_b_max),
                                                    traffic_type=traffic_type,
                                                    ip=self.lanforge_ip,
                                                    _debug_on=False)

            data = {}
            self.qos_test.background_run = background_run
            self.qos_test.input_devices_list = device_list
            self.qos_test.real_client_list = report_labels
            self.qos_test.real_client_list1 = report_labels
            self.qos_test.mac_id_list = device_macs
            self.qos_test.build()
            self.qos_test.start()
            time.sleep(10)
            try:
                connections_download, connections_upload, drop_a_per, drop_b_per = self.qos_test.monitor()
            except Exception as e:
                logger.info(f"Failed at Monitoring the CX... {e}")    
            if not background_run:
                self.qos_test.stop()
                time.sleep(5)
                test_results['test_results'].append(
                    self.qos_test.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
                data.update(test_results)
                test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
                logger.info("QOS Test ended at: {}".format(test_end_time))


                self.qos_test.cleanup()
                logging.debug('data:{}'.format(data))

                if qos_serial_run:
                    result1, result2, result3, result4 = {}, {}, {}, {}
                    # separating dictionaries for each value in the list
                    result_dicts = []
                    for item in data['test_results']:
                        result_dict = {'test_results': [item]}
                        result_dicts.append(result_dict)

                    if len(result_dicts) == 1:
                        logger.info("yes - 1")
                        result1 = result_dicts[0]
                        data1 = result1
                    if len(result_dicts) == 2:
                        logger.info("yes - 2")
                        result1, result2 = result_dicts[0], result_dicts[1]
                        data1 = result2
                    if len(result_dicts) == 3:
                        logger.info("yes - 3")
                        result1, result2, result3 = result_dicts[0], result_dicts[1], result_dicts[2]
                        data1 = result3
                    if len(result_dicts) == 4:
                        logger.info("yes - 4")
                        result1, result2, result3, result4 = result_dicts[0], result_dicts[1], result_dicts[2], result_dicts[3]
                        data1 = result4
                    data = data1
                self.qos_test.generate_report(data=data,
                                                input_setup_info={"contact": "support@candelatech.com"},
                                                report_path="",
                                                result_dir_name=f"Qos_Test_Report")
                data_set, load, res = self.qos_test.generate_graph_data_set(data)
                return data
                
        
        if qos_serial_run:
            for qos_tos in tos:
                logger.info(qos_tos)
                data.update({qos_tos: qos_test_overall_real(qos_tos)})
        else:
            data = qos_test_overall_real()
        return data
    def stop_qos_test(self):
        if getattr(self.qos_test,"background_run",None):
            print("setting the flag to false")
            self.qos_test.background_run = False
        print("setting throughput test to stop")
        self.qos_monitoring_thread.join()
        self.qos_test.stop()

    def generate_qos_report(self):
        data = {}
        test_results = {'test_results': []}
        time.sleep(5)
        test_results['test_results'].append(
            self.qos_test.evaluate_qos(self.qos_test.connections_download, self.qos_test.connections_upload, self.qos_test.drop_a_per, self.qos_test.drop_b_per))
        data.update(test_results)
        test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
        logger.info("QOS Test ended at: {}".format(test_end_time))


        self.qos_test.cleanup()
        logging.debug('data:{}'.format(data))

        self.qos_test.generate_report(data=data,
                                        input_setup_info={"contact": "support@candelatech.com"},
                                        report_path="",
                                        result_dir_name=f"Qos_Test_Report")
        data_set, load, res = self.qos_test.generate_graph_data_set(data)

    def start_ping_test(self, ssid, password, encryption, target,
                        interval=1, ping_test_duration=60, device_list=[], background=False):
        """
        Method to start and run the ping test on the selected devices.

        Args:
            ssid (str): SSID
            password (str): Password for the given SSID. [BLANK] if encryption is open.
            encryption (str): Encryption for the given SSID.
            target (str): IP or Domain name of the target.
            interval (int, optional): Time interval between two packets in seconds. Defaults to 1.
            ping_test_duration (int, optional): Time duration to run the test in seconds. Defaults to 60.
            device_list (list, optional): List of port names of all the selected devices. Defaults to [].

        Returns:
            result_json (dict): Result for the ping test.
        """        
        target = target
        interval = interval
        # starting part of the ping test
        ping_test_obj = ping_test.Ping(host=self.lanforge_ip, port=self.port, ssid=ssid, security=encryption,
                                            password=password, lanforge_password="lanforge", target=target,
                                            interval=interval, sta_list=[], duration=ping_test_duration)
        ping_test_obj.enable_real = True
        if not ping_test_obj.check_tab_exists():
            logger.info('Generic Tab is not available for Ping Test.\nAborting the test.')
            exit(0)
        base_interop_profile = RealDevice(manager_ip=self.lanforge_ip,
                                        ssid_5g=ssid,
                                        passwd_5g=password,
                                        encryption_5g=encryption)
        self.base_interop_profile = base_interop_profile
        base_interop_profile.get_devices()
        ping_test_obj.select_real_devices(real_devices=base_interop_profile,
                                            real_sta_list=device_list,
                                            base_interop_obj=base_interop_profile)
        # removing the existing generic endpoints & cxs
        ping_test_obj.cleanup()
        # ping_test_obj.sta_list = device_list
        # creating generic endpoints
        ping_test_obj.create_generic_endp()
        logger.info("Generic Cross-Connection List: {}".format(ping_test_obj.generic_endps_profile.created_cx))
        logger.info('Starting Running the Ping Test for {} seconds'.format(ping_test_duration))
        # start generate endpoint
        ping_test_obj.start_generic()
        ports_data_dict = ping_test_obj.json_get('/ports/all/')['interfaces']
        ports_data = {}
        for ports in ports_data_dict:
            port, port_data = list(ports.keys())[0], list(ports.values())[0]
            ports_data[port] = port_data
        if background:
            self.ping_test_obj = ping_test_obj
            return True
        time.sleep(ping_test_duration)
        logger.info('Stopping the PING Test...')
        ping_test_obj.stop_generic()
        # getting result dict
        result_data = ping_test_obj.get_results()
        result_json = {}
        ping_test_obj.sta_list = ping_test_obj.real_sta_list
        if type(result_data) == dict:
            for station in ping_test_obj.sta_list:
                current_device_data = base_interop_profile.devices_data[station]
                if station in result_data['name']:
                    result_json[station] = {
                        'command': result_data['command'],
                        'sent': result_data['tx pkts'],
                        'recv': result_data['rx pkts'],
                        'dropped': result_data['dropped'],
                        'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'mac': current_device_data['mac'],
                        'channel': current_device_data['channel'],
                        'ssid': current_device_data['ssid'],
                        'mode': current_device_data['mode'],
                        'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                        'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                        'remarks': [],
                        'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]}
                    result_json[station]['remarks'] = ping_test_obj.generate_remarks(result_json[station])
        else:
            for station in ping_test_obj.sta_list:
                current_device_data = base_interop_profile.devices_data[station]
                for ping_device in result_data:
                    ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                    if station in ping_endp:
                        result_json[station] = {
                            'command': ping_data['command'],
                            'sent': ping_data['tx pkts'],
                            'recv': ping_data['rx pkts'],
                            'dropped': ping_data['dropped'],
                            'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'mac': current_device_data['mac'],
                            'channel': current_device_data['channel'],
                            'ssid': current_device_data['ssid'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                            'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                            'remarks': [],
                            'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]}
                        result_json[station]['remarks'] = ping_test_obj.generate_remarks(result_json[station])
        logger.info("Final Result Json For Ping Test: {}".format(result_json))
        ping_test_obj.generate_report(result_json=result_json, result_dir=f'Ping_Test_Report',
                                        report_path="")
        return result_json
 
    def stop_ping_test(self):
        self.ping_test_obj.stop_generic()
        # getting result dict
        result_data = self.ping_test_obj.get_results()
        result_json = {}
        self.ping_test_obj.sta_list = self.ping_test_obj.real_sta_list
        if type(result_data) == dict:
            for station in self.ping_test_obj.sta_list:
                current_device_data = self.base_interop_profile.devices_data[station]
                if station in result_data['name']:
                    result_json[station] = {
                        'command': result_data['command'],
                        'sent': result_data['tx pkts'],
                        'recv': result_data['rx pkts'],
                        'dropped': result_data['dropped'],
                        'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],
                        'mac': current_device_data['mac'],
                        'channel': current_device_data['channel'],
                        'ssid': current_device_data['ssid'],
                        'mode': current_device_data['mode'],
                        'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                        'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                        'remarks': [],
                        'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]}
                    result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
        else:
            for station in self.ping_test_obj.sta_list:
                current_device_data = self.base_interop_profile.devices_data[station]
                for ping_device in result_data:
                    ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                    if station in ping_endp:
                        result_json[station] = {
                            'command': ping_data['command'],
                            'sent': ping_data['tx pkts'],
                            'recv': ping_data['rx pkts'],
                            'dropped': ping_data['dropped'],
                            'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],
                            'mac': current_device_data['mac'],
                            'channel': current_device_data['channel'],
                            'ssid': current_device_data['ssid'],
                            'mode': current_device_data['mode'],
                            'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                            'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],
                            'remarks': [],
                            'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]}
                        result_json[station]['remarks'] = self.ping_test_obj.generate_remarks(result_json[station])
        logger.info("Final Result Json For Ping Test: {}".format(result_json))
        self.ping_test_obj.generate_report(result_json=result_json, result_dir=f'Ping_Test_Report',
                                        report_path="")
        return result_json

    def start_th_test(self,**kwargs):
        background_run = kwargs.get("background_run",False)
        incremental_capacity=kwargs.get("incremental_capacity",None)
        do_interopability=kwargs.get("do_interopability",None)
        if background_run or incremental_capacity or do_interopability:
            self.monitoring_thread=threading.Thread(target=self.start_throughput_test,kwargs=kwargs)
            self.monitoring_thread.start()
        else:
            self.start_throughput_test(**kwargs)
    def start_throughput_test(self,
                            upstream_port= 'eth0',
                            traffic_type="lf_tcp",
                            device_list=[],
                            test_duration="60s",
                            upload=2560,
                            download=2560,
                            packet_size="-1",
                            incremental_capacity=[],
                            tos="Best_Efforts",
                            report_timer="5s",
                            load_type="wc_per_client_load",
                            do_interopability=False,
                            incremental=[],
                            precleanup=False,
                            postcleanup=False,
                            test_name=None,
                            background_run = False
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
            upload (int): Minimum upload rate per connection in bits per second.
                                    Default is 2560.
            download (int): Minimum download rate per connection in bits per second.
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
        self.throughput_test=Throughput(host=self.lanforge_ip,
                       ip=self.lanforge_ip,
                       port=self.port,
                       test_duration=test_duration,
                       upstream=upstream_port,
                       side_a_min_rate=upload,
                       side_b_min_rate=download,
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
                       test_name=test_name
                       )
        
        self.throughput_test.os_type()
        iterations_before_test_stopped_by_user=[]
        check_condition,clients_to_run=self.throughput_test.phantom_check()
        if check_condition==False:
            return
        check_increment_condition=self.throughput_test.check_incremental_list()
        if check_increment_condition==False:
            logger.info("Incremental values given for selected devices are incorrect")
            return
        elif(len(incremental_capacity)>0 and check_increment_condition==False):
            logger.info("Incremental values given for selected devices are incorrect")
            return
        created_cxs = self.throughput_test.build()
        time.sleep(10)
        created_cxs=list(created_cxs.keys())
        individual_dataframe_column=[]
        to_run_cxs,to_run_cxs_len,created_cx_lists_keys,incremental_capacity_list = self.throughput_test.get_incremental_capacity_list()
        for i in range(len(clients_to_run)):
            # Extend individual_dataframe_column with dynamically generated column names
            individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop A {clients_to_run[i]}', f'Rx % Drop B{clients_to_run[i]}',f'RSSI {clients_to_run[i]} ',f'Link Speed {clients_to_run[i]} '])
        individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop A', 'Overall Rx % Drop B','Iteration','TIMESTAMP','Start_time','End_time','Remaining_Time','Incremental_list','status'])
        individual_df=pd.DataFrame(columns=individual_dataframe_column)
        overall_start_time=datetime.now()
        overall_end_time=overall_start_time + timedelta(seconds=int(test_duration)*len(incremental_capacity_list))
        if background_run :
                logger.info("Start the test and run till stopped")
                self.throughput_test.background_run = True
        
        for i in range(len(to_run_cxs)):
            # Check the load type specified by the user
            if load_type == "wc_intended_load":
                # Perform intended load for the current iteration
                self.throughput_test.perform_intended_load(i,incremental_capacity_list)
                if i!=0:
                    # Stop throughput testing if not the first iteration
                    self.throughput_test.stop()
                # Start specific connections for the current iteration
                self.throughput_test.start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
            else:
                if (do_interopability and i!=0):
                    self.throughput_test.stop_specific(to_run_cxs[i-1])
                    time.sleep(5)
                self.throughput_test.start_specific(to_run_cxs[i])
            # Determine device names based on the current iteration
            device_names=created_cx_lists_keys[:to_run_cxs_len[i][-1]]
            # Monitor throughput and capture all dataframes and test stop status
            all_dataframes,test_stopped_by_user = self.throughput_test.monitor(i,individual_df,device_names,incremental_capacity_list,overall_start_time,overall_end_time)
            # Check if the test was stopped by the user
            if test_stopped_by_user==False:
                # Append current iteration index to iterations_before_test_stopped_by_user
                iterations_before_test_stopped_by_user.append(i)
            else:
                # Append current iteration index to iterations_before_test_stopped_by_user 
                iterations_before_test_stopped_by_user.append(i)
                break
        self.incremental_capacity_list,self.iterations_before_test_stopped_by_user=incremental_capacity_list,iterations_before_test_stopped_by_user
        self.all_dataframes,self.to_run_cxs_len=all_dataframes,to_run_cxs_len
        # if not background_run and self.throughput_test.incremental_capacity is None and  not self.throughput_test.stop_test:
        if not background_run and self.throughput_test.stop_test != True:
            self.throughput_test.stop()
            if postcleanup:
                self.throughput_test.cleanup()
            self.throughput_test.generate_report(list(set(iterations_before_test_stopped_by_user)),incremental_capacity_list,data=all_dataframes,data1=to_run_cxs_len)
            # return individual_df
    def stop_throughput_test(self):
        if getattr(self.throughput_test,"background_run",None):
            print("setting the flag to false")
            self.throughput_test.background_run = False
            self.throughput_test.stop_test=True
        elif self.throughput_test.incremental_capacity:
            print("setting the flag to false")
            # self.throughput_test.background_run = False
            self.throughput_test.stop_test=True
        elif self.throughput_test.do_interopability:
            print("setting the flag to false")
            self.throughput_test.stop_test=True
        print("setting throughput test to stop")
        self.monitoring_thread.join()
        self.throughput_test.stop() 
    def generate_report_throughput_test(self):
        self.throughput_test.generate_report(list(set(self.iterations_before_test_stopped_by_user)),self.incremental_capacity_list,data=self.all_dataframes,data1=self.to_run_cxs_len)


    def start_vs_test(self,**kwargs):
        background_run = kwargs.get("background_run",False)
        incremental_capacity=kwargs.get("incremental_capacity",None)
        if background_run or incremental_capacity:
            self.monitoring_thread=threading.Thread(target=self.start_video_streaming_test,kwargs=kwargs)
            self.monitoring_thread.start()
        else:
            self.start_video_streaming_test(**kwargs)
    def start_video_streaming_test(self, ssid="ssid_wpa_2g", passwd="something", encryp="psk",
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=0,
                        url="www.google.com", urls_per_tenm=100, duration="1m", 
                        device_list=[], media_quality='0',media_source='1',
                        incremental = False,postcleanup=False,
                        precleanup=False,incremental_capacity=None,test_name=None,background_run = False):
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
        media_source_name=media_source=media_source.lower()
        media_quality_name=media_quality=media_quality.lower()


        if any(char.isalpha() for char in media_source):
            media_source=media_source_dict[media_source]

        if any(char.isalpha() for char in media_quality):
            media_quality=media_quality_dict[media_quality]


        self.video_streaming_test = VideoStreamingTest(host=self.lanforge_ip, ssid=ssid, passwd=passwd, encryp=encryp,
                        suporrted_release=["7.0", "10", "11", "12"], max_speed=max_speed,
                        url=url, urls_per_tenm=urls_per_tenm, duration=duration, 
                        resource_ids = device_list, media_quality=media_quality,media_source=media_source,
                        incremental = incremental,postcleanup=postcleanup,
                        precleanup=precleanup)
        resource_ids_sm = []
        resource_set = set()
        resource_list = []
        resource_ids_generated = ""

        self.video_streaming_test.android_devices = self.video_streaming_test.devices.get_devices(only_androids=True)

        if device_list:
            # Extract second part of resource IDs and sort them
            self.video_streaming_test.resource_ids = ",".join(id.split(".")[1] for id in device_list.split(","))
            resource_ids_sm = self.video_streaming_test.resource_ids
            resource_list = resource_ids_sm.split(',')            
            resource_set = set(resource_list)
            resource_list_sorted = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list_sorted)

            # Convert resource IDs into a list of integers
            num_list = list(map(int, self.video_streaming_test.resource_ids.split(',')))

            # Sort the list
            num_list.sort()

            # Join the sorted list back into a string
            sorted_string = ','.join(map(str, num_list))
            self.video_streaming_test.resource_ids = sorted_string

            # Extract the second part of each Android device ID and convert to integers
            modified_list = list(map(lambda item: int(item.split('.')[1]), self.video_streaming_test.android_devices))
            # modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), self.video_streaming_test.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
            new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in self.video_streaming_test.android_devices]

            resources_list = device_list.split(",")
            for element in resources_list:
                if element in new_list_android:
                    for ele in self.video_streaming_test.android_devices:
                        if ele.startswith(element):
                            self.video_streaming_test.android_list.append(ele)
                else:
                    logger.info("{} device is not available".format(element))
            new_android = [int(item.split('.')[1]) for item in self.video_streaming_test.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(set(resource_ids))

        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices,report_labels,selected_macs = self.video_streaming_test.devices.query_user()
            # Handle cases where no devices are selected
            
            if not selected_devices:
                logger.info("devices donot exist..!!")
                return 
                
            self.video_streaming_test.android_list = selected_devices
            if self.video_streaming_test.android_list:
                resource_ids = ",".join([item.split(".")[1] for item in self.video_streaming_test.android_list])

                num_list = list(map(int, resource_ids.split(',')))

                # Sort the list
                num_list.sort()

                # Join the sorted list back into a string
                sorted_string = ','.join(map(str, num_list))

                self.video_streaming_test.resource_ids = sorted_string
                resource_ids1 = list(map(int, sorted_string.split(',')))
                modified_list = list(map(lambda item: int(item.split('.')[1]), self.video_streaming_test.android_devices))
                if not all(x in modified_list for x in resource_ids1):
                    logger.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = self.video_streaming_test.resource_ids
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
            if self.video_streaming_test.resource_ids:
                logger.info("The total available devices are {}".format(len(available_resources)))
                self.video_streaming_test.incremental = input('Specify incremental values as 1,2,3 : ')
                self.video_streaming_test.incremental = [int(x) for x in self.video_streaming_test.incremental.split(',')]
            else:
                logger.info("incremental Values are not needed as Android devices are not selected..")
        elif incremental==False:
            gave_incremental=True
            self.video_streaming_test.incremental=[len(available_resources)]
        
        if webgui_incremental:
            incremental = [int(x) for x in webgui_incremental.split(',')]
            if (len(webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(webgui_incremental) > 1):
                self.video_streaming_test.incremental = incremental
        
        if self.video_streaming_test.incremental and self.video_streaming_test.resource_ids:
            resources_list1 = [str(x) for x in self.video_streaming_test.resource_ids.split(',')]
            if resource_list_sorted:
                resources_list1 = resource_list_sorted
            if self.video_streaming_test.incremental[-1] > len(available_resources):
                logger.info("Exiting the program as incremental values are greater than the resource ids provided")
                exit()
            elif self.video_streaming_test.incremental[-1] < len(available_resources) and len(self.video_streaming_test.incremental) > 1:
                logger.info("Exiting the program as the last incremental value must be equal to selected devices")
                exit()
        
        # To create cx for selected devices
        self.video_streaming_test.build()

        # To set media source and media quality 
        time.sleep(10)

        # self.video_streaming_test.run
        test_time = datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logger.info("Initiating Test...")

        individual_dataframe_columns=[]

        keys = list(self.video_streaming_test.http_profile.created_cx.keys())
    
        #TODO : To create cx for laptop devices
        # if (not no_laptops) and self.video_streaming_test.other_list:
        #     self.video_streaming_test.create_generic_endp(self.video_streaming_test.other_list,os_types_dict)

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

        incremental_capacity_list_values=self.video_streaming_test.get_incremental_capacity_list()
        if incremental_capacity_list_values[-1]!=len(available_resources):
            logger.info("Incremental capacity doesnt match available devices")
            if postcleanup==True:
                self.video_streaming_test.postcleanup()
            exit(1)
        # Process resource IDs and incremental values if specified
        if self.video_streaming_test.resource_ids:
            if self.video_streaming_test.incremental:
                test_setup_info_incremental_values =  ','.join([str(n) for n in incremental_capacity_list_values])
                if len(self.video_streaming_test.incremental) == len(available_resources):
                    test_setup_info_total_duration = duration
                elif len(self.video_streaming_test.incremental) == 1 and len(available_resources) > 1:
                    if self.video_streaming_test.incremental[0] == len(available_resources):
                        test_setup_info_total_duration = duration
                    else:
                        div = len(available_resources)//self.video_streaming_test.incremental[0] 
                        mod = len(available_resources)%self.video_streaming_test.incremental[0] 
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
            self.video_streaming_test.total_duration = test_setup_info_total_duration

        actual_start_time=datetime.now()

        iterations_before_test_stopped_by_user=[]

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        if self.video_streaming_test.resource_ids:
            # Check if incremental  is specified
            if self.video_streaming_test.incremental:

                # Case 1: Incremental list has only one value and it equals the length of keys
                if len(self.video_streaming_test.incremental) == 1 and self.video_streaming_test.incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])

                # Case 2: Incremental list has only one value but length of keys is greater than 1
                elif len(self.video_streaming_test.incremental) == 1 and len(keys) > 1:
                    incremental_value = self.video_streaming_test.incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index

                # Case 3: Incremental list has multiple values and length of keys is greater than 1
                elif len(self.video_streaming_test.incremental) != 1 and len(keys) > 1:
                    
                    index = 0
                    for num in self.video_streaming_test.incremental:
                        
                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])
                        start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if background_run :
                    logger.info("Start the test and run till stopped")
                    self.video_streaming_test.background_run = True
                # Iterate over cx_order_list to start tests incrementally
                for i in range(len(cx_order_list)):
                    if i == 0:
                        self.video_streaming_test.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] 
                        end_time_webGUI = (datetime.now() + timedelta(minutes = self.video_streaming_test.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        self.video_streaming_test.data['end_time_webGUI'] = [end_time_webGUI] 


                    # time.sleep(10)

                    # Start specific devices based on incremental capacity
                    self.video_streaming_test.start_specific(cx_order_list[i])
                    if cx_order_list[i]:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    else:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    
                    file_path = "video_streaming_realtime_data.csv"

                    if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        self.video_streaming_test.data['remaining_time_webGUI'] = ['0:00'] 
                    else:
                        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.video_streaming_test.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] 
                    
                    test_stopped_by_user= self.video_streaming_test.monitor_for_runtime_csv(duration,file_path,individual_df,i,actual_start_time,resource_list_sorted,cx_order_list[i])
                    if test_stopped_by_user==False:
                    # Append current iteration index to iterations_before_test_stopped_by_user
                        iterations_before_test_stopped_by_user.append(i)
                    else:
                        # Append current iteration index to iterations_before_test_stopped_by_user 
                        iterations_before_test_stopped_by_user.append(i)
                        break   
        if not background_run and self.video_streaming_test.stop_test!=True:
            self.video_streaming_test.stop()
            
        if self.video_streaming_test.resource_ids:
            
            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

            # phone_list = self.video_streaming_test.get_resource_data() 

            username = []
            
            try:
                eid_data = self.video_streaming_test.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
            except KeyError:
                logger.info("Error: 'interfaces' key not found in port data")
                exit(1)

            resource_ids = list(map(int, self.video_streaming_test.resource_ids.split(',')))
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.video_streaming_test.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            username.append(resource_hw_data['resource']['user'] )
            device_list_str = ','.join([f"{name} ( Android )" for name in username])

            test_setup_info = {
                "Testname" : test_name,
                "Device List" : device_list_str ,
                "No of Devices" : "Total" + "( " + str(len(keys)) + " ): Android(" +  str(len(keys)) +")",
                "Incremental Values" : "",
                "URL" : url,
                "Media Source":media_source_name.upper(),
                "Media Quality":media_quality_name
            }
            # if self.video_streaming_test.incremental:
            #     if len(incremental_capacity_list_values) != len(available_resources):
            #         test_setup_info['Duration per Iteration (min)']= str(test_setup_info_duration_per_iteration)
            test_setup_info['Incremental Values'] = test_setup_info_incremental_values
            test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration) 
                
            self.date,self.test_setup_info,self.individual_df,self.cx_order_list,self.iterations_before_test_stopped_by_user=date,test_setup_info,individual_df,cx_order_list,list(set(iterations_before_test_stopped_by_user))
            if not background_run and self.video_streaming_test.stop_test!=True:
                if self.video_streaming_test.resource_ids and self.video_streaming_test.incremental :  
                    self.video_streaming_test.generate_report(date, list(set(iterations_before_test_stopped_by_user)),test_setup_info = test_setup_info,realtime_dataset=individual_df, cx_order_list = cx_order_list) 
                elif self.video_streaming_test.resource_ids:
                    self.video_streaming_test.generate_report(date, list(set(iterations_before_test_stopped_by_user)),test_setup_info = test_setup_info,realtime_dataset=individual_df) 
                if postcleanup==True:
                    self.video_streaming_test.postcleanup()
    def stop_video_streaming_test(self):
        if getattr(self.video_streaming_test,"background_run",None):
            print("setting the flag to false")
            self.video_streaming_test.background_run = False
        elif self.video_streaming_test.incremental:
            print("setting the flag to false")
            # self.video_streaming_test.background_run = False
            self.video_streaming_test.stop_test=True
        print("setting video streaming test to stop")
        self.monitoring_thread.join()
        self.video_streaming_test.stop() 
    def generate_report_video_streaming_test(self):
        if self.video_streaming_test.resource_ids and self.video_streaming_test.incremental :  
            self.video_streaming_test.generate_report(self.date, self.iterations_before_test_stopped_by_user,test_setup_info = self.test_setup_info,realtime_dataset=self.individual_df, cx_order_list = self.cx_order_list) 
        elif self.video_streaming_test.resource_ids:
            self.video_streaming_test.generate_report(self.date, self.iterations_before_test_stopped_by_user,test_setup_info = self.test_setup_info,realtime_dataset=self.individual_df) 
        # if postcleanup==True:
        #     self.video_streaming_test.postcleanup()

    def start_wb_test(self,**kwargs):
        background_run = kwargs.get("background_run",False)
        incremental_capacity=kwargs.get("incremental_capacity",None)
        if background_run or incremental_capacity:
            self.monitoring_thread=threading.Thread(target=self.start_web_browser_test,kwargs=kwargs)
            self.monitoring_thread.start()
        else:
            self.start_web_browser_test(**kwargs)

    def start_web_browser_test(self,ssid="ssid_wpa_2g", passwd="something", encryp="psk",
                    suporrted_release=["7.0", "10", "11", "12"], max_speed=0,
                    url="www.google.com", count=1, duration="60s", 
                    device_list="", 
                    incremental = False,incremental_capacity=None,postcleanup=False,
                    precleanup=False,test_name=None,background_run=False):
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
        self.web_browser_test = RealBrowserTest(host=self.lanforge_ip, ssid=ssid, passwd=passwd, encryp=encryp,
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

        self.web_browser_test.android_devices = self.web_browser_test.devices.get_devices(only_androids=True)

        
        # Process resource IDs if provided
        if device_list:
            # Extract second part of resource IDs and sort them
            self.web_browser_test.resource_ids = ",".join(id.split(".")[1] for id in device_list.split(","))
            resource_ids_sm = self.web_browser_test.resource_ids
            resource_list = resource_ids_sm.split(',')            
            resource_set = set(resource_list)
            resource_list_sorted = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list_sorted)

            # Convert resource IDs into a list of integers
            num_list = list(map(int, self.web_browser_test.resource_ids.split(',')))

            # Sort the list
            num_list.sort()

            # Join the sorted list back into a string
            sorted_string = ','.join(map(str, num_list))
            self.web_browser_test.resource_ids = sorted_string

            # Extract the second part of each Android device ID and convert to integers
            modified_list = list(map(lambda item: int(item.split('.')[1]), self.web_browser_test.android_devices))
            modified_other_os_list = list(map(lambda item: int(item.split('.')[1]), self.web_browser_test.other_os_list))
            
            # Verify if all resource IDs are valid for Android devices
            resource_ids = [int(x) for x in sorted_string.split(',')]
            new_list_android = [item.split('.')[0] + '.' + item.split('.')[1] for item in self.web_browser_test.android_devices]

            resources_list = device_list.split(",")
            for element in resources_list:
                if element in new_list_android:
                    for ele in self.web_browser_test.android_devices:
                        if ele.startswith(element):
                            self.web_browser_test.android_list.append(ele)
                else:
                    logger.info("{} device is not available".format(element))
            new_android = [int(item.split('.')[1]) for item in self.web_browser_test.android_list]

            resource_ids = sorted(new_android)
            available_resources=list(set(resource_ids))
            
        else:
            # Query user to select devices if no resource IDs are provided
            selected_devices,report_labels,selected_macs = self.web_browser_test.devices.query_user()
            # Handle cases where no devices are selected
            if not selected_devices:
                logger.info("devices donot exist..!!")
                return 
            
            self.web_browser_test.android_list = selected_devices
            

            
            # Verify if all resource IDs are valid for Android devices
            if self.web_browser_test.android_list:
                resource_ids = ",".join([item.split(".")[1] for item in self.web_browser_test.android_list])

                num_list = list(map(int, resource_ids.split(',')))

                # Sort the list
                num_list.sort()

                # Join the sorted list back into a string
                sorted_string = ','.join(map(str, num_list))

                self.web_browser_test.resource_ids = sorted_string
                resource_ids1 = list(map(int, sorted_string.split(',')))
                modified_list = list(map(lambda item: int(item.split('.')[1]), self.web_browser_test.android_devices))

                # Check for invalid resource IDs
                if not all(x in modified_list for x in resource_ids1):
                    logger.info("Verify Resource ids, as few are invalid...!!")
                    exit()
                resource_ids_sm = self.web_browser_test.resource_ids
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
            if self.web_browser_test.resource_ids:
                self.web_browser_test.incremental = input('Specify incremental values as 1,2,3 : ')
                self.web_browser_test.incremental = [int(x) for x in self.web_browser_test.incremental.split(',')]
            else:
                logger.info("incremental Values are not needed as Android devices are not selected..")
        
        # Handle webgui_incremental argument
        if webgui_incremental:
            incremental = [int(x) for x in webgui_incremental.split(',')]
            # Validate the length and assign incremental values
            if (len(webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(webgui_incremental) > 1):
                self.web_browser_test.incremental = incremental
            elif len(webgui_incremental) == 1:
                self.web_browser_test.incremental = incremental

        # if self.web_browser_test.incremental and (not self.web_browser_test.resource_ids):
        #     logger.info("incremental values are not needed as Android devices are not selected.")
        #     exit()
        
        # Validate incremental and resource IDs combination
        if (self.web_browser_test.incremental and self.web_browser_test.resource_ids) or (webgui_incremental):
            resources_list1 = [str(x) for x in self.web_browser_test.resource_ids.split(',')]
            if resource_list_sorted:
                resources_list1 = resource_list_sorted
            # Check if the last incremental value is greater or less than resources provided
            if self.web_browser_test.incremental[-1] > len(available_resources):
                logger.info("Exiting the program as incremental values are greater than the resource ids provided")
                exit()
            elif self.web_browser_test.incremental[-1] < len(available_resources) and len(self.web_browser_test.incremental) > 1:
                logger.info("Exiting the program as the last incremental value must be equal to selected devices")
                exit()

        # self.web_browser_test.run
        test_time = datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logger.info("Initiating Test...")
        available_resources= [int(n) for n in available_resources]
        available_resources.sort()
        available_resources_string=",".join([str(n) for n in available_resources])
        self.web_browser_test.set_available_resources_ids(available_resources_string)
        # self.web_browser_test.set_available_resources_ids([int(n) for n in available_resources].sort())
        self.web_browser_test.build()
        time.sleep(10)
        #TODO : To create cx for laptop devices
        # Create end-points for devices other than Android if specified
        # if (not no_laptops) and self.web_browser_test.other_list:
        #     self.web_browser_test.create_generic_endp(self.web_browser_test.other_list,os_types_dict)

        keys = list(self.web_browser_test.http_profile.created_cx.keys())
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
            incremental_capacity_list_values=self.web_browser_test.get_incremental_capacity_list()
            if incremental_capacity_list_values[-1]!=len(available_resources):
                logger.info("Incremental capacity doesnt match available devices")
                if postcleanup==True:
                    self.web_browser_test.postcleanup()
                exit(1)
        if background_run :
            logger.info("Start the test and run till stopped")
            self.web_browser_test.background_run = True

        # Process resource IDs and incremental values if specified
        if self.web_browser_test.resource_ids:
            if self.web_browser_test.incremental:
                test_setup_info_incremental_values =  ','.join(map(str, incremental_capacity_list_values))
                if len(self.web_browser_test.incremental) == len(available_resources):
                    test_setup_info_total_duration = duration
                elif len(self.web_browser_test.incremental) == 1 and len(available_resources) > 1:
                    if self.web_browser_test.incremental[0] == len(available_resources):
                        test_setup_info_total_duration = duration
                    else:
                        div = len(available_resources)//self.web_browser_test.incremental[0] 
                        mod = len(available_resources)%self.web_browser_test.incremental[0] 
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
            self.web_browser_test.total_duration = test_setup_info_total_duration

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        gave_incremental,iteration_number=True,0
        if self.web_browser_test.resource_ids:
            if not self.web_browser_test.incremental:
                self.web_browser_test.incremental=[len(keys)]
                gave_incremental=False
            if self.web_browser_test.incremental or not gave_incremental:
                if len(self.web_browser_test.incremental) == 1 and self.web_browser_test.incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])
                elif len(self.web_browser_test.incremental) == 1 and len(keys) > 1:
                    incremental_value = self.web_browser_test.incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index
                elif len(self.web_browser_test.incremental) != 1 and len(keys) > 1:
                    
                    index = 0
                    for num in self.web_browser_test.incremental:
                        
                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])
                        start_time_webGUI = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Update start and end times for webGUI
                
                for i in range(len(cx_order_list)):
                    if i == 0:
                        self.web_browser_test.data["start_time_webGUI"] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(keys)
                        # if len(self.web_browser_test.incremental) == 1 and self.web_browser_test.incremental[0] == len(keys):
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(self.web_browser_test.incremental) == 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(self.web_browser_test.incremental) != 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = duration * len(cx_order_list))).strftime('%Y-%m-%d %H:%M:%S')
                        # if len(self.web_browser_test.incremental) == 1 and self.web_browser_test.incremental[0] == len(keys):
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = self.web_browser_test.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(self.web_browser_test.incremental) == 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = self.web_browser_test.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        # elif len(self.web_browser_test.incremental) != 1 and len(keys) > 1:
                        #     end_time_webGUI = (datetime.now() + timedelta(minutes = self.web_browser_test.total_duration)).strftime('%Y-%m-%d %H:%M:%S')

                        end_time_webGUI = (datetime.now() + timedelta(minutes = self.web_browser_test.total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        self.web_browser_test.data['end_time_webGUI'] = [end_time_webGUI] * len(keys)


                    self.web_browser_test.start_specific(cx_order_list[i])
                    
                    iteration_number+=len(cx_order_list[i])
                    if cx_order_list[i]:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    else:
                        logger.info("Test started on Devices with resource Ids : {selected}".format(selected = cx_order_list[i]))
                    
                    # duration = 60 * duration
                    file_path = "webBrowser.csv"

                    start_time = time.time()
                    df = pd.DataFrame(self.web_browser_test.data)

                    if end_time_webGUI < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        self.web_browser_test.data['remaining_time_webGUI'] = ['0:00'] * len(keys)
                    else:
                        date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.web_browser_test.data['remaining_time_webGUI'] =  [datetime.strptime(end_time_webGUI,"%Y-%m-%d %H:%M:%S") - datetime.strptime(date_time,"%Y-%m-%d %H:%M:%S")] * len(keys)
                    # Monitor runtime and save results
                    
                    self.web_browser_test.monitor_for_runtime_csv(duration,file_path,iteration_number,resource_list_sorted,cx_order_list[i])
                        # time.sleep(duration)
                    if self.web_browser_test.test_stopped_by_user==True:
                        break
        if not background_run and self.web_browser_test.stop_test!=True:
            self.web_browser_test.stop()

        

        # Additional setup for generating reports and post-cleanup
        if self.web_browser_test.resource_ids:
            # uc_avg_val = self.web_browser_test.my_monitor('uc-avg')
            total_urls = self.web_browser_test.my_monitor('total-urls')

            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

            # Retrieve resource data for Android devices
            phone_list = self.web_browser_test.get_resource_data() 

            # Initialize and retrieve username data
            username = []
            eid_data = self.web_browser_test.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")

            resource_ids = list(map(int, self.web_browser_test.resource_ids.split(',')))
            # Extract username information from resource data
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.web_browser_test.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            username.append(resource_hw_data['resource']['user'] )

            # Construct device list string for report
            device_list_str = ','.join([f"{name} ( Android )" for name in username])
            test_setup_info = {
            "Testname" : test_name,
            "Device List" : device_list_str ,
            "No of Devices" : "Total" + "( " + str(len(phone_list)) + " ): Android(" +  str(len(phone_list)) +")" ,
            "Incremental Values" : "",
            "Required URL Count" : count,
            "URL" : url 
            }
            # if self.web_browser_test.incremental:
            #     test_setup_info['Duration per Iteration (min)']= str(test_setup_info_duration_per_iteration)+ " (min)"
            test_setup_info['Incremental Values'] = test_setup_info_incremental_values
            test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration) + " (min)"


            # Retrieve additional monitoring data
            # total_urls = self.web_browser_test.my_monitor('total-urls')
            uc_min_val = self.web_browser_test.my_monitor('uc-min')
            timeout = self.web_browser_test.my_monitor('timeout')
            uc_min_value = uc_min_val
            dataset2 = total_urls
            dataset = timeout
            lis = username
            bands = ['URLs']
            self.web_browser_test.data['total_urls'] = total_urls
            self.web_browser_test.data['uc_min_val'] = uc_min_val 
            self.web_browser_test.data['timeout'] = timeout
        logger.info("Test Completed")

        # Handle incremental values and generate reports accordingly
        prev_inc_value = 0
        if self.web_browser_test.resource_ids and self.web_browser_test.incremental :
            for i in range(len(cx_order_list)):
                df = pd.DataFrame(self.web_browser_test.data)
                names_to_increment = cx_order_list[i] 

                if 'inc_value' not in df.columns:
                    df['inc_value'] = 0
                if i == 0:
                    prev_inc_value = len(cx_order_list[i])
                else:
                    prev_inc_value = prev_inc_value + len(cx_order_list[i])
                    
                self.web_browser_test.data['inc_value'] = df.apply(
                    lambda row: (
                        prev_inc_value  # Accumulate inc_value
                        if row['inc_value'] == 0 and row['name'] in names_to_increment 
                        else row['inc_value']  # Keep existing inc_value
                    ), 
                    axis=1
                )

                df1 = pd.DataFrame(self.web_browser_test.data)

                
                df1.to_csv(file_path, mode='w', index=False)
        self.date,self.test_setup_info,self.dataset2,dataset,self.lis,self.bands,self.total_urls,self.uc_min_value,self.cx_order_list,self.gave_incremental=date,test_setup_info,dataset2,dataset,lis,bands,total_urls,uc_min_value,cx_order_list,gave_incremental
        if not background_run and self.web_browser_test.stop_test!=True:
            self.web_browser_test.generate_report(date,"webBrowser.csv",test_setup_info = test_setup_info, dataset2 = dataset2, dataset = dataset, lis = lis, bands = bands, total_urls = total_urls, uc_min_value = uc_min_value , cx_order_list = cx_order_list,gave_incremental=gave_incremental)      
            if postcleanup:
                self.web_browser_test.postcleanup()
    def stop_web_browser_test(self):
        if getattr(self.web_browser_test,"background_run",None):
            print("setting the flag to false")
            self.web_browser_test.background_run = False
        elif self.web_browser_test.incremental:
            print("setting the flag to false")
            # self.web_browser_test.background_run = False
            self.web_browser_test.stop_test=True
        print("setting web browser test to stop")
        self.monitoring_thread.join()
        self.web_browser_test.stop()

    def generate_report_web_browser_test(self):
        self.web_browser_test.generate_report(self.date,"webBrowser.csv",test_setup_info = self.test_setup_info, dataset2 = self.dataset2, dataset = self.dataset, lis = self.lis, bands = self.bands, total_urls = self.total_urls, uc_min_value = self.uc_min_value , cx_order_list = self.cx_order_list,gave_incremental=self.gave_incremental)      

    def start_mc_test(self,**kwargs):
        background_run = kwargs.get("background_run",False)
        if background_run:
            self.mc_monitoring_thread=threading.Thread(target=self.start_multicast_test,kwargs=kwargs)
            self.mc_monitoring_thread.start()
        else:
            self.start_multicast_test(**kwargs)
    def start_multicast_test(self,
                            endp_types="mc_udp",
                            mc_tos="VO", 
                            side_a_min=0, 
                            side_b_min=0, 
                            side_a_pdu=0, 
                            side_b_pdu=0,
                            upstream_port='eth1',
                            test_duration=5,
                            device_list=[],
                            ssid="",
                            passwd="",
                            encryption="",
                            report_path="",
                            background_run = False
                            ):
            # use for creating multicast dictionary
            """
        Initiates a Multicast test with various configurable parameters.

        Args:
            
            duration (str): Duration to run the multicast test.
                            Default is '60' seconds.
            device_list (str): Provide port IDs of  devices to run the test on, e.g., "1.10.wlan0,1.12.wlan0.
                            Default is an empty list [].
            endp_types (str): Endpoint type to run multicast.
                            Default is 'mc_udp'
            mc_tos (str): Tos values of the endpoints to be created.
                            Default is "VO"

            "side_a_min (int)" Value in bits to be pased on the endpoint side 'A'.
                            Default is 0
            
            "side_b_min (int)" Value in bits to be pased on the endpoint side 'B'.
                            Default is 0

            "upstream_port (str)": Upstrem port name.
                            Default is 'eth1'

        """    
            test_duration = test_duration
            endp_types = endp_types
            mc_tos = mc_tos

               
            
            report = lf_report_pdf.lf_report(_path=report_path, _results_dir_name=f"Multicast_Test",
                                            _output_html=f"multicast_test.html",
                                            _output_pdf=f"multicast_test.pdf")
            
            test_rig = "CT-ID-004"
            test_tag = "test_l3"
            dut_hw_version = "AXE11000"
            dut_sw_version = "3.0.0.4.386_44266"
            dut_model_num = "1.0"
            dut_serial_num = "123456"
            test_id = "test l3"
            
            kpi_path = report_path
            logger.info("Report and kpi_path :{kpi_path}".format(kpi_path=kpi_path))
            kpi_csv = lf_kpi_csv(_kpi_path=kpi_path,
                                            _kpi_test_rig=test_rig,
                                            _kpi_test_tag=test_tag,
                                            _kpi_dut_hw_version=dut_hw_version,
                                            _kpi_dut_sw_version=dut_sw_version,
                                            _kpi_dut_model_num=dut_model_num,
                                            _kpi_dut_serial_num=dut_serial_num,
                                            _kpi_test_id=test_id)
            # TODO: Add try/except if fails
            self.multicast_test = L3VariableTime(endp_types=endp_types,
                                                args="",
                                                tos=mc_tos,
                                                side_b=upstream_port,
                                                ssid_list=ssid,
                                                ssid_password_list=passwd,
                                                ssid_security_list=encryption,
                                                name_prefix="LT-",                                            
                                                side_a_min_rate=[side_a_min],
                                                side_b_min_rate=[side_b_min],
                                                side_a_min_pdu=[side_a_pdu],
                                                side_b_min_pdu=[side_b_pdu],
                                                rates_are_totals=True,
                                                mconn=1,
                                                test_duration=str(test_duration) + "s",
                                                polling_interval="5s",
                                                lfclient_host=self.lanforge_ip,
                                                lfclient_port=self.port,
                                                debug=True,
                                                use_existing_station_lists=True,
                                                existing_station_lists=device_list,                                                                                                                                            
                                                interopt_mode=True,
                                                side_a=None,
                                                radio_name_list=[],
                                                number_of_stations_per_radio_list=[],
                                                wifi_mode_list=[],
                                                enable_flags_list=[],
                                                station_lists=[],
                                                outfile="",
                                                attenuators=[],
                                                atten_vals=[-1],
                                                kpi_csv=kpi_csv,
                                                reset_port_enable_list=[],
                                                reset_port_time_min_list=[],
                                                reset_port_time_max_list=[],
                                                )
            self.multicast_test.set_report_obj(report)
            logger.info("building is going on")
            # building the endpoints
            self.multicast_test.build()
            if not self.multicast_test.passes():
                logger.info("build step failed.")
                logger.info(self.multicast_test.get_fail_message())
                exit(1)
            
            # TODO: Check return value of start()
            if background_run :
                logger.info("Start the test and run till stopped")
                self.multicast_test.background_run = True
                self.multicast_test.start()
            else:
                logger.info("Start the test and run for a duration {} seconds".format(test_duration))
                self.multicast_test.start()
                self.multicast_test.stop()
                self.generate_report_multicast_test()
            
    def stop_multicast_test(self):
        if getattr(self.multicast_test,"background_run",None):
            print("setting the flag to false")
            self.multicast_test.background_run = False
        print("setting multicast test to stop")
        self.mc_monitoring_thread.join()
        self.multicast_test.stop()

    def generate_report_multicast_test(self):
        csv_results_file = self.multicast_test.get_results_csv()
        self.multicast_test.report.set_title("Multicast Test")
        self.multicast_test.report.build_banner_cover()
        self.multicast_test.report.start_content_div2()
        # set dut information for reporting
        self.multicast_test.set_dut_info()
        # generate report
        self.multicast_test.generate_report()
        # generate html and pdf
        self.multicast_test.report.write_report_location()
        self.multicast_test.report.write_html_with_timestamp()
        self.multicast_test.report.write_index_html()
        
        self.multicast_test.report.write_pdf_with_timestamp(_page_size='A3', _orientation='Landscape')


logger_config = lf_logger_config.lf_logger_config()
candela_apis = Candela(ip='192.168.242.2', port=8080)

# candela_apis.get_client_connection_details(['1.208.wlan0', '1.19.wlan0'])

# TO RUN CONNECTIVITY TEST
# device_list, report_labels, device_macs = candela_apis.start_connectivity(
#     manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]', device_list=['test41'])
# logger.info('{} {} {}'.format(device_list, report_labels, device_macs))
 
# TO RUN FTP TEST
# candela_apis.start_ftp_test(ssid='Walkin_open', password='[BLANK]', security='open',
#                                 device_list=','.join(['1.12', '1.13', '1.16']),traffic_duration=10)

# time.sleep(600)
# candela_apis.stop_ftp_test()
# candela_apis.generate_report_ftp_test()
#                                device_list=','.join(['1.16', '1.19']))

# TO RUN HTTP TEST
# candela_apis.start_http_test(ssid='Walkin_open', password='[BLANK]',
#                              security='open', http_file_size='10MB',
#                              device_list=['1.20.wlan0', '1.19.wlan0'], report_labels=['1.16 android test41', '1.19 android test46'],
#                              device_macs=['48:e7:da:fe:0d:ed', '48:e7:da:fe:0d:91'], target_per_ten=1000, upstream='eth3',
#                              band='5G', ap_name='Netgear')
# time.sleep(120)
# candela_apis.stop_http_test()
# candela_apis.generate_report_http_test()

# TO RUN QOS TEST
# candela_apis.start_qos_test(ssid='Walkin_open', password='[BLANK]', security='open',
#                             ap_name='Netgear', upstream='eth3', tos=['VI', 'BK'],
#                             traffic_type='lf_tcp', device_list=['1.12.sta0', '1.19.wlan0'], report_labels=['1.12 Lin test41', '1.19 android test46'],
#                             device_macs=['48:e7:da:fe:0d:ed', '48:e7:da:fe:0d:91'], qos_serial_run=False,background_run=True)
# time.sleep(60)
# candela_apis.stop_qos_test()
# candela_apis.generate_qos_report()

# TO RUN PING TEST
# candela_apis.start_ping_test(ssid='Walkin_open', password='[BLANK]', encryption='open',
#                              target='192.168.1.95', device_list=['1.36.wlan0'], background=True)

# TO RUN THROUGHPUT TEST
# candela_apis.start_th_test(traffic_type="lf_udp",
#                             device_list='1.13,1.18,1.11,1.12,1.14',
#                             upload=1000000,
#                             download=100000,
#                             upstream_port="eth1",
#                             report_timer="5s",
#                             load_type="wc_intended_load",
#                             # incremental_capacity="2",
#                             # test_duration="5m",
#                             # precleanup=True,
#                             # postcleanup=True,
#                             packet_size=18,
#                             test_name="Throughput_test",
#                             background_run=True
#                             )
# print("waiting started")
# time.sleep(60)
# print("waiting finished")
# candela_apis.stop_throughput_test()
# candela_apis.generate_report_throughput_test()



# TO RUN INTEROPERABILITY TEST
# candela_apis.start_th_test(traffic_type="lf_udp",
#                                    device_list='1.13,1.18,1.11,1.12',
#                                    upload=1000000,
#                                    download=100000,
#                                    upstream_port="eth1",
#                                    test_duration="20s",
#                                    do_interopability=True,
#                                    precleanup=True,
#                                    postcleanup=True,
#                                    test_name="Interoperabaility_test"
#                                    )
# print("waiting started")
# time.sleep(60)
# print("waiting finished")
# candela_apis.stop_throughput_test()
# candela_apis.generate_report_throughput_test()

# TO RUN VIDEO STREAMING TEST
# candela_apis.start_vs_test(url="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
#                                         media_source="hls",
#                                         media_quality="4k",
#                                         duration="1m",
#                                         device_list='1.11,1.14,1.15,1.17,1.21',
#                                         precleanup=True,
#                                         postcleanup=True,
#                                         # incremental_capacity="3",
#                                         background_run=True
#                                         )
# print("waiting started")
# time.sleep(60)
# print("waiting finished")
# candela_apis.stop_video_streaming_test()
# candela_apis.generate_report_video_streaming_test()




# TO RUN WEB BROWSER TEST
# candela_apis.start_wb_test(device_list='1.11,1.14,1.15,1.17,1.21', 
#                                         duration="2m",
#                                         url="http://www.google.com",
#                                         background_run=True,
#                                         count=3,
#                                         incremental_capacity='1'
#                                         )
# print("waiting started")
# time.sleep(60)
# print("waiting finished")
# candela_apis.stop_web_browser_test()
# candela_apis.generate_report_web_browser_test()


# To RUN MULTICAST TEST
candela_apis.start_mc_test(mc_tos="VO", endp_types="mc_udp", side_a_min=10000000,
                                  side_b_min=100000000, upstream_port='eth3', test_duration=30, device_list=['1.22.wlan0'], background_run=False)
# time.sleep(60)
# candela_apis.stop_multicast_test()
# candela_apis.generate_report_multicast_test()