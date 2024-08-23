import asyncio
import importlib
import datetime
from datetime import datetime
import time
import requests
import logging
import pandas as pd
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
import lf_webpage as http_test
import lf_interop_qos as qos_test
import lf_interop_ping as ping_test
import lf_cleanup
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
        test_start_time = datetime.now()
        print("Traffic started running at ", test_start_time)
        obj.start(False, False)
        time.sleep(traffic_duration)
        obj.stop()
        print("Traffic stopped running")
        obj.my_monitor()
        obj.postcleanup()
        test_end_time = datetime.now()
        print("Test ended at", test_end_time)
        return test_start_time, test_end_time

    def start_http_test(self, ssid, password, security, http_file_size, device_list, report_labels, device_macs,
                  target_per_ten, upstream='eth1', ap_name='', http_test=http_test, all_bands=False, windows_ports=[],
                  band='5G', lf_username='lanforge', lf_password='lanforge', 
                  test_duration=60):
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
        client_type = ""
        http_sta_list = []
        num_stations = 0
        client_type = "Real"
        http_sta_list = device_list
        num_stations = len(device_list)
        http_obj = http_test.HttpDownload(lfclient_host=self.lanforge_ip, lfclient_port=self.port,
                                               upstream=upstream,
                                               num_sta=num_stations,
                                               ap_name=ap_name, ssid=ssid, password=password, security=security,
                                               target_per_ten=target_per_ten, file_size=http_file_size, bands=band,
                                               client_type=client_type, lf_username=lf_username,
                                               lf_password=lf_password)
        http_obj.data = {}
        http_obj.port_list = device_list
        http_obj.devices_list = report_labels
        http_obj.macid_list = device_macs
        http_obj.user_query = [device_list, report_labels, device_macs]
        http_obj.windows_ports = windows_ports
        http_obj.file_create(ssh_port=22)
        http_obj.set_values()
        http_obj.precleanup()
        http_obj.build()
        test_time = datetime.now().strftime("%b %d %H:%M:%S")
        logger.info("HTTP Test started at {}".format(test_time))
        http_obj.start()
        time.sleep(http_test_duration)
        http_obj.stop()
        uc_avg_val = http_obj.my_monitor('uc-avg')
        url_times = http_obj.my_monitor('total-urls')
        rx_bytes_val = http_obj.my_monitor('bytes-rd')
        rx_rate_val = http_obj.my_monitor('rx rate')

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
            print(list5G, list5G_bytes, list5G_speed, list5G_urltimes)
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
        test_end = datetime.now().strftime("%b %d %H:%M:%S")
        logger.info("HTTP Test Finished at {}".format(test_end))
        s1 = test_time
        s2 = test_end  # for example
        FMT = '%b %d %H:%M:%S'
        test_duration = datetime.strptime(
            s2, FMT) - datetime.strptime(s1, FMT)
        logger.info("Total HTTP test duration: {}".format(test_duration))
        date = str(datetime.now()).split(
            ",")[0].replace(" ", "-").split(".")[0]

        test_setup_info = {
            "AP Name": ap_name,
            "SSID": ssid,
            "Security": security,
            "No of Devices": len(http_sta_list),
            "File size": http_file_size,
            "File location": "/usr/local/lanforge/nginx/html",
            "Traffic Direction": "Download",
            "Traffic Duration ": http_test_duration
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
        if all_bands:
            band = ''
        else:
            band = '_' + band
        self.cleanup.layer4_endp_clean()
        return result_data

    def start_qos_test(self, ssid, password, security,
                 ap_name, upstream, tos, traffic_type='lf_udp',
                 side_a_min=6200000, side_b_min=6200000, side_a_max=0, side_b_max=0, 
                 test_duration=5, qos_serial_run=True, device_list=[],
                 report_labels=[], device_macs=[]):
        if test_duration:
            qos_test_duration = test_duration
        test_results = {'test_results': []}
        data = {}
        # qos test for real clients
        def qos_test_overall_real(qos_tos_real=None):
            qos_test_obj = qos_test.ThroughputQOS(host=self.lanforge_ip,
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
            qos_test_obj.input_devices_list = device_list
            qos_test_obj.real_client_list = report_labels
            qos_test_obj.real_client_list1 = report_labels
            qos_test_obj.mac_id_list = device_macs
            qos_test_obj.build()
            qos_test_obj.start()
            time.sleep(10)
            try:
                connections_download, connections_upload, drop_a_per, drop_b_per = qos_test_obj.monitor()
            except Exception as e:
                print(f"Failed at Monitoring the CX... {e}")
            qos_test_obj.stop()
            time.sleep(5)
            test_results['test_results'].append(
                qos_test_obj.evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
            data.update(test_results)
            test_end_time = datetime.now().strftime("%b %d %H:%M:%S")
            logger.info("QOS Test ended at: {}".format(test_end_time))


            qos_test_obj.cleanup()
            logging.debug('data:{}'.format(data))

            if qos_serial_run:
                result1, result2, result3, result4 = {}, {}, {}, {}
                # separating dictionaries for each value in the list
                result_dicts = []
                for item in data['test_results']:
                    result_dict = {'test_results': [item]}
                    result_dicts.append(result_dict)

                if len(result_dicts) == 1:
                    print("yes - 1")
                    result1 = result_dicts[0]
                    data1 = result1
                if len(result_dicts) == 2:
                    print("yes - 2")
                    result1, result2 = result_dicts[0], result_dicts[1]
                    data1 = result2
                if len(result_dicts) == 3:
                    print("yes - 3")
                    result1, result2, result3 = result_dicts[0], result_dicts[1], result_dicts[2]
                    data1 = result3
                if len(result_dicts) == 4:
                    print("yes - 4")
                    result1, result2, result3, result4 = result_dicts[0], result_dicts[1], result_dicts[2], result_dicts[3]
                    data1 = result4
                data = data1
            data_set, load, res = qos_test_obj.generate_graph_data_set(data)
        if qos_serial_run:
            for qos_tos in tos:
                print(qos_tos)
                qos_test_overall_real(qos_tos)
        else:
            qos_test_overall_real()

    def start_ping_test(self, ssid, password, encryption, target,
                        interval=1, ping_test_duration=60, device_list=[]):
        target = target
        interval = interval
        # starting part of the ping test
        ping_test_obj = ping_test.Ping(host=self.lanforge_ip, port=self.port, ssid=ssid, security=encryption,
                                            password=password, lanforge_password="lanforge", target=target,
                                            interval=interval, sta_list=[], duration=ping_test_duration)
        ping_test_obj.enable_real = True
        if not ping_test_obj.check_tab_exists():
            print('Generic Tab is not available for Ping Test.\nAborting the test.')
            exit(0)
        base_interop_profile = RealDevice(manager_ip=self.lanforge_ip,
                                        ssid_5g=ssid,
                                        passwd_5g=password,
                                        encryption_5g=encryption)
        base_interop_profile.get_devices()
        ping_test_obj.select_real_devices(real_devices=base_interop_profile,
                                            real_sta_list=device_list,
                                            base_interop_obj=base_interop_profile)
        # removing the existing generic endpoints & cxs
        ping_test_obj.cleanup()
        ping_test_obj.sta_list = device_list
        # creating generic endpoints
        ping_test_obj.create_generic_endp()
        print("Generic Cross-Connection List: {}".format(ping_test_obj.generic_endps_profile.created_cx))
        print('Starting Running the Ping Test for {} seconds'.format(ping_test_duration))
        # start generate endpoint
        ping_test_obj.start_generic()
        ports_data_dict = ping_test_obj.json_get('/ports/all/')['interfaces']
        ports_data = {}
        for ports in ports_data_dict:
            port, port_data = list(ports.keys())[0], list(ports.values())[0]
            ports_data[port] = port_data
        time.sleep(ping_test_duration)
        print('Stopping the PING Test...')
        ping_test_obj.stop_generic()
        # getting result dict
        result_data = ping_test_obj.get_results()
        result_json = {}
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
        print("Final Result Json For Ping Test: {}".format(result_json))
        return result_json



candela_apis = Candela(ip='192.168.214.61', port=8080)

# device_list, report_labels, device_macs = candela_apis.start_connectivity(
#     manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]', device_list=['RZ8N10FFTKE', 'RZ8NB1KWXLB'])
# logger.info(device_list, report_labels, device_macs)
# 
# device_list, report_labels, device_macs = candela_apis.start_connectivity(manager_ip='192.168.214.61', port=8080, server_ip='192.168.1.61', ssid_5g='Walkin_open', encryption_5g='open', passwd_5g='[BLANK]')
# 
# candela_apis.start_ftp_test(ssid='Walkin_open', password='[BLANK]', security='open', bands=[
#                             '5G'], directions=['Download'], file_sizes=['10MB'], device_list=','.join(device_list))

# candela_apis.start_http_test(ssid='Walkin_open', password='[BLANK]',
#                              security='open', http_file_size='10MB',
#                              device_list=['1.342.wlan0'], report_labels=['1.342 linux test41'],
#                              device_macs=['48:e7:da:fe:0d:ed'], target_per_ten=1000,
#                              band='5G', ap_name='Netgear')
# candela_apis.start_qos_test(ssid='Walkin_open', password='[BLANK]', security='open',
#                             ap_name='Netgear', upstream='eth1', tos=['VI', 'VO', 'BE', 'BK'],
#                             traffic_type='lf_tcp', device_list=['1.342.wlan0'], report_labels=['1.342 linux test41'],
#                             device_macs=['48:e7:da:fe:0d:ed'], qos_serial_run=False)
# candela_apis.start_ping_test(ssid='Walkin_open', password='[BLANK]', encryption='open',
#                              target='192.168.1.61', device_list=['1.342.wlan0'])