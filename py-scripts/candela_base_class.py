import asyncio
import importlib
import datetime
import time
import requests
# echo Performing POST cleanup of browser processes... & taskkill /F /IM chrome.exe /T >nul 2>&1 & taskkill /F /IM chromedriver.exe /T >nul 2>&1 & echo Browser processes terminated.
# cmd /c "echo Performing POST cleanup of browser processes... && taskkill /F /IM chrome.exe /T >nul 2>&1 && taskkill /F /IM chromedriver.exe /T >nul 2>&1 && echo Browser processes terminated."
import paramiko
import threading
from collections import OrderedDict
from os import path
import shutil
import logging
from tabulate import tabulate
from lf_graph import lf_bar_graph_horizontal,lf_bar_graph,lf_line_graph
import pandas as pd
from lf_base_interop_profile import RealDevice
from lf_ftp import FtpTest
import lf_webpage as http_test
import multiprocessing
# import lf_interop_qos as qos_test
# import lf_interop_ping as ping_test
# from lf_interop_throughput import Throughput
# from lf_interop_video_streaming import VideoStreamingTest
# from lf_interop_vlc import VLCStream
# from lf_interop_real_browser_test import RealBrowserTest
# from test_l3 import L3VariableTime,change_port_to_ip,configure_reporting,query_real_clients,valid_endp_types
from lf_kpi_csv import lf_kpi_csv
import lf_cleanup
import os
import sys
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
import argparse
import json
import traceback
from types import SimpleNamespace
import matplotlib
# from dotenv import load_dotenv
import csv
import matplotlib.pyplot as plt
from pathlib import Path
import subprocess
# from interop_configuration import Configuration
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
error_logs = ""
# objj = "obj" 
test_results_df = pd.DataFrame(columns=['test_name', 'status'])
matplotlib.use('Agg')  # Before importing pyplot
base_path = os.getcwd()
print('base path',base_path)
sys.path.insert(0, os.path.join(base_path, 'py-json'))     # for interop_connectivity, LANforge
sys.path.insert(0, os.path.join(base_path, 'py-json', 'LANforge'))  # for LFUtils
sys.path.insert(0, os.path.join(base_path, 'py-scripts'))  # for lf_logger_config
# througput_test=importlib.import_module("py-scripts.lf_interop_throughput")
# video_streaming_test=importlib.import_module("py-scripts.lf_interop_video_streaming")
# web_browser_test=importlib.import_module("py-scripts.real_application_tests.real_browser.lf_interop_real_browser_test")
# zoom_test=importlib.import_module("py-scripts.real_application_tests.zoom_automation.lf_interop_zoom")
# yt_test=importlib.import_module("py-scripts.real_application_tests.youtube.lf_interop_youtube")
# teams_test=importlib.import_module("py-scripts.real_application_tests.teams_automation.lf_interop_teams")
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
logger = logging.getLogger(__name__)
# RealBrowserTest = getattr(web_browser_test, "RealBrowserTest")
# Youtube = getattr(yt_test, "Youtube")
# ZoomAutomation = getattr(zoom_test, "ZoomAutomation")
# TeamsAutomation = getattr(teams_test, "TeamsAutomation")
DeviceConfig=importlib.import_module("py-scripts.DeviceConfig")
# from py_scripts import lf_logger_config, interop_connectivity
# Saved working directory and index state WIP on test_base_class: 3f3a21f5 minor change
# from lf_interop_ping import Ping
# from LANforge.LFUtils import LFUtils
import sys
import os
import posixpath
import stat
import ntpath
from multiprocessing import Manager
manager = Manager()
test_results_list = manager.list()
# BASE PATH: /home/sidartha/project/lanforge-scripts
# base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# # Add py-json and LANforge to sys.path
# sys.path.insert(0, os.path.join(base_path, 'py-json'))               # for interop_connectivity
# sys.path.insert(0, os.path.join(base_path, 'py-json', 'LANforge'))   # for LFUtils
# sys.path.insert(0, os.path.join(base_path, 'py-scripts'))            # for lf_logger_config

# import LFUtils
# import lf_logger_config
# import interop_connectivity
if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))


if 'py-scripts' not in sys.path:
    sys.path.append('/home/lanforge/lanforge-scripts/py-scripts')
lf_report = importlib.import_module("py-scripts.lf_report")
# from station_profile import StationProfile
# import interop_connectivity
# from LANforge import LFUtils

# iot_scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../local/interop-webGUI/IoT/scripts/"))
# if os.path.exists(iot_scripts_path):
#     sys.path.insert(0, iot_scripts_path)
#     from test_automation import Automation 

# class RemoteSniffer:
#     def __init__(self, hostname, username, password=None, key_filename=None, moni_name='eth0', pcap_name='capture.pcap', test_name = "sample"):
#         self.hostname = hostname
#         self.username = username
#         self.password = password
#         self.key_filename = key_filename
#         self.moni_name = moni_name
#         self.pcap_name = pcap_name
#         self.ssh_client = None
#         self.sftp = None
#         self.remote_process_pid = None
#         self.testname = test_name
#     def create_remote_test_folder(self, remote_base="/home/lanforge"):
#         try:
#             remote_path = f"{remote_base}/{self.testname}"

#             # Check if folder exists
#             try:
#                 self.sftp.stat(remote_path)
#             except FileNotFoundError:
#                 self.sftp.mkdir(remote_path)

#             return remote_path

#         except Exception as e:
#             print(f"Failed to create remote folder: {e}")
#             return None
#     def connect(self):
#         self.ssh_client = paramiko.SSHClient()
#         self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         self.ssh_client.connect(
#             self.hostname,
#             username=self.username,
#             password=self.password,
#             key_filename=self.key_filename
#         )
#         self.sftp = self.ssh_client.open_sftp()
#     def start_sniff(self, remote_dir="/tmp"):
#         """Start remote tshark capture in background on remote system."""
#         remote_pcap_path = os.path.join(remote_dir, self.pcap_name)
#         cmd = f'nohup tshark -i {self.moni_name} -w {remote_pcap_path} -f "(type mgt and not subtype beacon and not subtype probe-req and not subtype probe-resp) or ether proto 0x888e" > /dev/null 2>&1 & echo $!'        
#         print(f"Starting remote sniffing: {cmd}")
#         stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
#         pid = stdout.read().decode().strip()
#         self.remote_process_pid = pid
#         print(f"tshark started with PID {pid} on remote host")
#         return remote_pcap_path

#     def start_sniff_for_triband(self, remote_dir="/tmp",moni2g="",moni5g="",moni6g=""):
#         """Start remote tshark capture in background on remote system."""
#         remote_pcap_path = os.path.join(remote_dir, self.pcap_name)
#         cmd = f'nohup tshark -i {moni2g} -i {moni5g} -i {moni6g} -w {remote_pcap_path} -f "" > /dev/null 2>&1 & echo $!'        
#         print(f"Starting remote sniffing: {cmd}")
#         stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
#         pid = stdout.read().decode().strip()
#         self.remote_process_pid = pid
#         print(f"tshark started with PID {pid} on remote host")
#         return remote_pcap_path


#     def stop_sniff(self):
#         """Stop remote tshark capture using stored PID."""
#         if not self.remote_process_pid:
#             print("No remote process PID available — sniff not started or already stopped.")
#             return
#         cmd = f"kill -2 {self.remote_process_pid}"
#         print(f"Stopping remote sniffing with: {cmd}")
#         self.ssh_client.exec_command(cmd)
#         time.sleep(1)
#         print("Sniffing stopped.")
#     def fetch_pcap(self, remote_path, local_path):
#         """Download the pcap file from remote system."""
#         print(f"Fetching PCAP from {remote_path} -> {local_path}")
#         self.sftp.get(remote_path, local_path)
#         print("Download complete:", local_path)
#     def close(self):
#         if self.sftp:
#             self.sftp.close()
#         if self.ssh_client:
#             self.ssh_client.close()

import paramiko
import time

class RemoteSniffer:
    def __init__(self, hostname, username, password=None,
                 key_filename=None, pcap_name='capture.pcap',
                 test_name="sample"):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.pcap_name = pcap_name
        self.testname = test_name

        self.ssh_client = None
        self.sftp = None
        self.remote_process_pid = None
    

    def fetch_combined_roaming_zip(self, remote_folder, local_folder=None):
        """
        Finds a subfolder starting with 'pcap_batch' inside remote_folder, then zips the 'combined_roaming_clients' folder inside it,
        downloads the zip to the local system, and places it in a local folder named after remote_folder's basename.
        """
        if not hasattr(self, 'ssh_client') or self.ssh_client is None:
            raise Exception("SSH connection not established.")
        if not hasattr(self, 'sftp') or self.sftp is None:
            self.sftp = self.ssh_client.open_sftp()

        # 1. Find pcap_batch* subfolder
        stdin, stdout, stderr = self.ssh_client.exec_command(f"ls -d {remote_folder}/pcap_batch* 2>/dev/null | head -n 1")
        pcap_batch_dir = stdout.read().decode().strip()
        if not pcap_batch_dir:
            raise Exception(f"No pcap_batch* folder found in {remote_folder}")

        # 2. Check for combined_roaming_clients inside pcap_batch_dir
        combined_dir = posixpath.join(pcap_batch_dir, "combined_roaming_clients")
        try:
            self.sftp.stat(combined_dir)
        except FileNotFoundError:
            raise Exception(f"combined_roaming_clients folder not found in {pcap_batch_dir}")

        # 3. Zip the combined_roaming_clients folder on remote
        zip_name = "combined_roaming_clients.zip"
        remote_zip_path = posixpath.join(pcap_batch_dir, zip_name)
        zip_cmd = f"cd {pcap_batch_dir} && zip -r {zip_name} combined_roaming_clients >/dev/null"
        stdin, stdout, stderr = self.ssh_client.exec_command(zip_cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error_msg = stderr.read().decode()
            raise Exception(f"Failed to zip combined_roaming_clients: {error_msg}")

        # 4. Prepare local folder
        remote_folder_basename = os.path.basename(remote_folder.rstrip('/'))
        if local_folder is None:
            local_folder = remote_folder_basename
        else:
            local_folder = os.path.join(local_folder, remote_folder_basename)

        os.makedirs(local_folder, exist_ok=True)
        local_zip_path = os.path.join(local_folder, zip_name)

        # 5. Download the zip file
        self.sftp.get(remote_zip_path, local_zip_path)
        print(f"Downloaded {zip_name} to {local_zip_path}")

        # 6. (Optional) Remove the zip file from remote
        self.ssh_client.exec_command(f"rm -f {remote_zip_path}")

        return local_zip_path
    

    def sftp_get_dir(self, remote_dir, local_dir):
        os.makedirs(local_dir, exist_ok=True)
        for entry in self.sftp.listdir_attr(remote_dir):
            remote_path = posixpath.join(remote_dir, entry.filename)
            local_path = os.path.join(local_dir, entry.filename)
            if stat.S_ISDIR(entry.st_mode):
                self.sftp_get_dir(remote_path, local_path)
            else:
                self.sftp.get(remote_path, local_path)

    def fetch_combined_roaming_folder(self, remote_folder, local_folder=None):
        if not hasattr(self, 'ssh_client') or self.ssh_client is None:
            raise Exception("SSH connection not established.")
        if not hasattr(self, 'sftp') or self.sftp is None:
            self.sftp = self.ssh_client.open_sftp()

        stdin, stdout, stderr = self.ssh_client.exec_command(
            f"ls -d {remote_folder}/pcap_batch* 2>/dev/null | head -n 1")
        pcap_batch_dir = stdout.read().decode().strip()
        if not pcap_batch_dir:
            raise Exception(f"No pcap_batch* folder found in {remote_folder}")

        remote_folder_basename = os.path.basename(remote_folder.rstrip('/'))
        if local_folder is None:
            local_folder = remote_folder_basename
        else:
            local_folder = os.path.join(local_folder, remote_folder_basename)
        os.makedirs(local_folder, exist_ok=True)

        # 3. Download entire pcap_batch folder
        local_pcap_dir = os.path.join(local_folder, os.path.basename(pcap_batch_dir))

        self.sftp_get_dir(pcap_batch_dir, local_pcap_dir)

        print(f"Downloaded {pcap_batch_dir} to {local_pcap_dir}")

        return local_pcap_dir

    # def fetch_combined_roaming_folder(self, remote_folder, local_folder=None):
    #     """
    #     Finds a subfolder starting with 'pcap_batch' inside remote_folder, then fetches the
    #     'combined_roaming_clients' folder inside it, downloading it recursively to the local system,
    #     and places it in a local folder named after remote_folder's basename.
    #     """
    #     if not hasattr(self, 'ssh_client') or self.ssh_client is None:
    #         raise Exception("SSH connection not established.")
    #     if not hasattr(self, 'sftp') or self.sftp is None:
    #         self.sftp = self.ssh_client.open_sftp()

    #     # 1. Find pcap_batch* subfolder
    #     stdin, stdout, stderr = self.ssh_client.exec_command(
    #         f"ls -d {remote_folder}/pcap_batch* 2>/dev/null | head -n 1")
    #     pcap_batch_dir = stdout.read().decode().strip()
    #     if not pcap_batch_dir:
    #         raise Exception(f"No pcap_batch* folder found in {remote_folder}")

    #     # 2. Check for combined_roaming_clients inside pcap_batch_dir
    #     combined_dir = posixpath.join(pcap_batch_dir, "combined_roaming_clients")
    #     try:
    #         self.sftp.stat(combined_dir)
    #     except FileNotFoundError:
    #         raise Exception(f"combined_roaming_clients folder not found in {pcap_batch_dir}")

    #     # 3. Prepare local folder
    #     remote_folder_basename = os.path.basename(remote_folder.rstrip('/'))
    #     if local_folder is None:
    #         local_folder = remote_folder_basename
    #     else:
    #         local_folder = os.path.join(local_folder, remote_folder_basename)
    #     os.makedirs(local_folder, exist_ok=True)

    #     # 4. Download the combined_roaming_clients folder recursively
    #     local_combined_dir = os.path.join(local_folder, "combined_roaming_clients")
    #     self.sftp_get_dir(combined_dir, local_combined_dir)
    #     print(f"Downloaded {combined_dir} to {local_combined_dir}")

    #     return local_combined_dir
    

    def run_command_and_fetch_folder(self, remote_folder, local_folder=None, mgmt_roam_time=500, data_roam_time=500, test_type='Zoom Call'):
        """
        Runs a command on the remote server using the existing SSH connection.
        If the command succeeds (exit status 0), fetches the specified remote folder to the local system.

        :param remote_folder: Path to the remote folder to fetch (str)
        :param local_folder: Path to the local folder where files will be saved (str)
        """
        if not hasattr(self, 'ssh_client') or self.ssh_client is None:
            raise Exception("SSH connection not established.")
        if not hasattr(self, 'sftp') or self.sftp is None:
            self.sftp = self.ssh_client.open_sftp()
        # command = f"python3 ~/roaming_development/wifi_roaming_cli.py --mode parallel --pcap-dir {remote_folder} --ap-alias Controller=06:03:7f:41:15:07,02:03:7f:01:53:51,06:03:7f:85:63:65 --ap-alias Agent1=06:03:7f:41:10:73,06:03:7f:85:69:89,02:03:7f:41:12:2d --ap-alias Agent2=06:03:7f:19:01:09,06:03:7f:12:1d:1d,02:03:7f:01:52:3f --client-alias SamsungS25Ultra=a0:1b:9e:13:99:5f,a2:1b:9e:13:99:e5,a2:1b:9e:13:99:e4 --client-alias iPhone17=5c:ad:ba:bd:92:2a,ce:b5:82:f8:cb:9b,c6:4a:a8:67:c6:ba --client-alias iPhone15Pro=d0:6b:78:5a:bf:ff --client-alias Pixel8Pro=5c:33:7b:f1:d9:1a,5e:33:7b:f1:d9:1b"
        # command = f"python3 ~/roaming_development/wifi_roaming_cli.py --mode parallel --pcap-dir {remote_folder} --all-clients"
        command = f"python3 ~/roaming_development/wifi_roaming_cli.py --mode parallel --pcap-dir {remote_folder} --alias-file ./roaming_development/ap_client_aliases.json --report-image ./roaming_development/floor_plan.jpeg --workers 6 --packets-per-chunk 15000 --pcap-batch-workers 3 --traffic-test '{test_type}' --auth-pass-ms {mgmt_roam_time} --gap-pass-ms {data_roam_time}"
        print(f"Running remote command: {command}")
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        # Read all output and error
        out = stdout.read().decode()
        err = stderr.read().decode()
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Remote command executed successfully. Fetching folder...")
            if out:
                print("--- STDOUT ---\n" + out)
            if err:
                print("--- STDERR ---\n" + err)
            self.fetch_combined_roaming_folder(remote_folder, local_folder)
        else:
            print(f"Command failed with exit status {exit_status}.")
            print("--- STDOUT ---\n" + out)
            print("--- STDERR ---\n" + err)
            # raise Exception(f"Remote command failed with exit status {exit_status}. See output above.")

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(
            self.hostname,
            username=self.username,
            password=self.password,
            key_filename=self.key_filename
        )

        self.sftp = self.ssh_client.open_sftp()

    def create_remote_test_folder(self, remote_base="/home/lanforge"):
        remote_path = f"{remote_base}/{self.testname}"

        try:
            self.sftp.stat(remote_path)
        except FileNotFoundError:
            self.sftp.mkdir(remote_path)

        print(f"Remote folder ready: {remote_path}")
        return remote_path

    def start_sniff_for_triband(self, remote_dir, moni2g=None, moni5g=None, moni6g=None):

        remote_pcap_path = f"{remote_dir}/{self.pcap_name}"
        filter_str = '(type mgt and not subtype beacon and not subtype probe-req) or ether proto 0x888e'

        # -----------------------------
        # Build interface list
        # -----------------------------
        interfaces = []

        if moni2g:
            interfaces.append(moni2g)
        if moni5g:
            interfaces.append(moni5g)
        if moni6g:
            interfaces.append(moni6g)

        # ❌ No interfaces → fail
        if not interfaces:
            raise Exception("No monitor interfaces provided")

        # -----------------------------
        # Build tshark command
        # -----------------------------
        iface_str = " ".join([f"-i {iface}" for iface in interfaces])

        cmd = (
            f'nohup tshark {iface_str} '
            f'-w {remote_pcap_path} '
            f'> /dev/null 2>&1 & echo $!'
        )
        print("=================",cmd)

        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        pid = stdout.read().decode().strip()

        if not pid:
            err = stderr.read().decode()
            raise Exception(f"Failed to start tshark: {err}")

        self.remote_process_pid = pid

        print(f"Started sniffing on: {interfaces}")
        print(f"PID: {pid}")

        return remote_pcap_path
    def stop_sniff(self):
        if not self.remote_process_pid:
            return

        self.ssh_client.exec_command(f"kill -2 {self.remote_process_pid}")
        time.sleep(2)

    def fetch_pcap(self, remote_path, local_path):
        self.sftp.get(remote_path, local_path)
        print(f"Downloaded: {local_path}")

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.ssh_client:
            self.ssh_client.close()


class Candela(Realm):
    """
    Candela Class file to invoke different scripts from py-scripts.
    """

    def __init__(self, ip='localhost', port=8080,order_priority="series",result_dir="",dowebgui=False,test_name='',no_cleanup=False,do_mix_exec=False,result_path=None,
                 config_wait_time=60,device_list=None,
                 file_name=None,
                 profile_name=None,
                 group_name=None,
                 eap_method=None,
                 eap_identity=None,
                 ieee80211=None,
                 ieee80211u=None,
                 ieee80211w=None,
                 enable_pkc=None,
                 bss_transition=None,
                 power_save=None,
                 disable_ofdma=None,
                 roam_ft_ds=None,
                 key_management=None,
                 pairwise=None,
                 private_key=None,
                 ca_cert=None,
                 client_cert=None,
                 pk_passwd=None,
                 pac_file=None,
                 config=False,
                 expected_passfail_val=None,
                 csv_name=None,
                 wait_time=60,
                 upstream_port="eth1",
                 ssid=None,
                 passwd=None,
                 security=None,
                 sniff_radio='1.1.wiphy0',
                 sniff_duration=300,
                 sniff=False,
                 sniff_frequency=-1,
                 sniff_channel='AUTO',
                 pcap_name=None,
                 moni_name=None,
                 args=None):

        """
        Constructor to initialize the LANforge IP and port
        Args:
            ip (str, optional): LANforge IP. Defaults to 'localhost'.
            port (int, optional): LANforge port. Defaults to 8080.
        """
        super().__init__(lfclient_host=ip,
                         lfclient_port=port)
        self.lanforge_ip = ip
        self.port = port
        self.api_url = 'http://{}:{}'.format(self.lanforge_ip, self.port)
        self.cleanup = lf_cleanup.lf_clean(host=self.lanforge_ip, port=self.port, resource='all')
        self.ftp_test = None
        self.http_test = None
        self.generic_endps_profile = self.new_generic_endp_profile()
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
        self.result_path = os.getcwd() if result_path is None else result_path  
        self.test_count_dict = {}
        self.current_exec = "series"
        self.order_priority = order_priority
        self.dowebgui = dowebgui
        self.result_dir = result_dir
        self.test_name = test_name
        self.overall_csv = []
        self.overall_status = {}
        self.obj_dict = {}
        self.test_stopped = False
        self.no_cleanup = no_cleanup
        self.duration_dict = {}
        self.config_wait_time = config_wait_time
        self.ssid = ssid
        self.password = passwd
        self.security = security
        self.upstream_port = upstream_port
        self.device_list = device_list if device_list else []
        self.http_obj_dict = {"parallel":{},"series":{}}
        self.ftp_obj_dict = {"parallel":{},"series":{}}
        self.thput_obj_dict = {"parallel":{},"series":{}}
        self.qos_obj_dict = {"parallel":{},"series":{}}
        self.ping_obj_dict = {"parallel":{},"series":{}}
        self.mcast_obj_dict = {"parallel":{},"series":{}}
        self.rb_obj_dict = {"parallel":{},"series":{}}
        self.yt_obj_dict = {"parallel":{},"series":{}}
        self.teams_obj_dict = {"parallel":{},"series":{}}
        self.zoom_obj_dict = {"parallel":{},"series":{}}
        self.vs_obj_dict = {"parallel":{},"series":{}}
        self.vlc_obj_dict = {"parallel":{},"series":{}}
        self.rb_obj_dict = manager.dict({
            "parallel": manager.dict(),
            "series": manager.dict()
        })
        # self.rb_obj_dict = manager.dict({
        #     "parallel": manager.dict(),
        #     "series": manager.dict()
        # })
        # self.rb_pipe_dict = {"parallel":{},"series":{}}
        # self.yt_obj_dict = manager.dict({"parallel": {}, "series": {}})
        # self.zoom_obj_dict = manager.dict({"parallel": {}, "series": {}})
        self.parallel_connect = {}
        self.series_connect = {}
        self.parallel_index = 0
        self.series_index = 0
        self.do_mix_exec = do_mix_exec
        self.stop_all_tests = False
        self.names_duration = {}
        self.profile_name = profile_name
        self.file_name = file_name
        self.group_name = group_name
        self.eap_method = eap_method
        self.eap_identity = eap_identity
        self.ieee80211 = ieee80211
        self.ieee80211u = ieee80211u
        self.ieee80211w = ieee80211w
        self.enable_pkc = enable_pkc
        self.bss_transition = bss_transition
        self.power_save = power_save
        self.disable_ofdma = disable_ofdma
        self.roam_ft_ds = roam_ft_ds
        self.key_management = key_management
        self.pairwise = pairwise
        self.private_key = private_key
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.pk_passwd = pk_passwd
        self.pac_file = pac_file
        self.resource_stats = DeviceConfig.DeviceConfig(lanforge_ip=self.lanforge_ip,port=self.port,wait_time=self.config_wait_time,file_name=self.file_name)
        # self.upstream_ip = self.resource_stats.change_port_to_ip(self.upstream_port)
        # self.resource_stats.get_all_devices()
        self.expected_passfail_val = expected_passfail_val
        self.csv_name = csv_name
        self.wait_time = wait_time
        self.group_device_map = {}
        self.config = config
        if moni_name:
            self.moni_name = moni_name
        else:
            wiphy_eid = self.name_to_eid(sniff_radio)
            radio_num = ""
            #wiphy_eid = [1,1,wiphy12,""]
            # wiphy_eid[2] = wiphy12 the below extacts 12 from it
            for ch in wiphy_eid[2]:
                if ch.isdigit():
                    radio_num += ch
            # for unique default names moni11w12
            self.moni_name = "moni{}{}w{}".format(wiphy_eid[0],wiphy_eid[1],radio_num)
        self.sniff_radio = sniff_radio
        self.sniff_duration = sniff_duration
        self.sniff_channel = sniff_channel
        self.pcap_name = pcap_name
        self.tshark_process = None
        self.args = args
        self.test_map = {
        "ping_test":   (run_ping_test, "PING TEST"),
        "http_test":   (run_http_test, "HTTP TEST"),
        "ftp_test":    (run_ftp_test, "FTP TEST"),
        "qos_test":    (run_qos_test, "QoS TEST"),
        "vs_test":     (run_vs_test, "VIDEO STREAMING TEST"),
        "thput_test":  (run_thput_test, "THROUGHPUT TEST"),
        "mcast_test":  (run_mcast_test, "MULTICAST TEST"),
        "yt_test":     (run_yt_test, "YOUTUBE TEST"),
        "rb_test":     (run_rb_test, "REAL BROWSER TEST"),
        "zoom_test":   (run_zoom_test, "ZOOM TEST"),
        "teams_test":  (run_teams_test, "TEAMS TEST"),
        "vlc_test":     (run_vlc_test, "VLC TEST")
        }

# only for sniffer 

    def channel_switch(self,radio="wiphy0",channel='',ap_data=None):
        eid = self.name_to_eid(radio)
        shelf = eid[0]
        resource_id = eid[1]
        port_name = eid[2]
        print(eid)
        # exit(0)
        port_up_data = self.port_up_request(resource_id=resource_id,port_name=port_name)
        self.json_post("cli-json/set_port", port_up_data)
        time.sleep(10)
        channel_change_data = {"shelf":shelf,
                                "resource":resource_id,
                                "radio":port_name,
                                "channel":channel}
        channel_change_url = "cli-json/set_wifi_radio"
        self.json_post(channel_change_url,channel_change_data)
        total_retries = 10
        current_retries = 1
        created = False
        print("Waiting until {} radio switches the channel to {}".format(radio,channel))
        query = '.'.join([str(shelf), str(resource_id), str(port_name)])
        while current_retries <= total_retries:
            logger.debug(f'retrying for {query}')
            logger.debug(f"Waiting for station {query} to appear in port list...")
            # ports_all_data = self.json_get('/ports')
            ports_data = self.json_get("/port/{}/{}/{}?fields=phantom,channel".format(shelf, resource_id, port_name))
            logger.debug(ports_data)
            if ports_data is not None and ports_data['interface']['phantom'] == False and str(ports_data['interface']['channel']) == str(channel):
                created = True
                break
            time.sleep(1)
        if created:
            logger.info("{} successfully switched to channel {}".format(radio,channel))
            return True
        else:
            return False

    def setup_monitor_interface(self,port,mon_iface_name="moni0"):
        """Create monitor interface via LANforge API"""
        url = "/cli-json/add_monitor"
        eid = self.name_to_eid(port)
        payload = {
            "shelf": eid[0],
            "resource": eid[1],
            "radio": eid[2],
            "ap_name": mon_iface_name
        }
        try:
            self.json_post(url,payload)
            print("waiting until moniter interface getting UP")
            retries = 1
            total_retries = 60
            created = False
            while retries <= total_retries:
                mon_data = self.json_get("/ports/{}/{}/{}?fields=down".format(eid[0],eid[1],mon_iface_name))
                if mon_data is not None and "interface" in mon_data and "down" in mon_data["interface"] and not mon_data["interface"]["down"]:
                    created = True
                    break
                retries += 1
                time.sleep(1)
            return created

        except Exception as e:
            logger.info(f"[LANforge EXCEPTION] {e}", "ERROR")
            return False

    def clear_monitor_interfaces(self):
        self.cleanup.sta_clean()


    def create_monitor(self):
        
        # to switch channel in wiphy radio
        channel_switched = self.channel_switch(radio=self.sniff_radio,channel=self.sniff_channel)
        if not channel_switched:
            logger.info("Radio : {} failed to shift channel to {}".format(self.sniff_radio,self.sniff_channel))
            return False
        monitor_created = self.setup_monitor_interface(port=self.sniff_radio,mon_iface_name=self.moni_name)
        if not monitor_created:
            logger.info("Failed to create monitor {}".format(self.moni_name))
            return False
        return True
    def start_sniff(self,pcap_path=None):
        capname = self.pcap_name
        if pcap_path is None:
            base_dir = os.getcwd()
            pcap_path = os.path.join(base_dir, capname)
        else:
            ensure_path(pcap_path,True)
            pcap_path = os.path.join(pcap_path,capname)
        print("PCAP PATH",pcap_path)
        cmd = f"tshark -i {self.moni_name} -w {pcap_path}"
        try:
            print("RUNNING TSHARK")
            self.tshark_process = subprocess.Popen(cmd, shell=True)
        except Exception as e:
            print(e, "In start_sniff Exception")
    
    def stop_sniff(self):
        try:
            self.tshark_process.terminate()
        except Exception as e:
            print(e, "In stop_sniff Exception")
        try:
            return_code = self.tshark_process.returncode
            print("RETURN CODE", return_code)

        except BaseException as err:
            print(err, "ERRORR")



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

    def port_up_request(self, resource_id, port_name, debug_on=False):
        """
        Prepare JSON payload for admin-up port request.

        Args:
            resource_id (int): Resource ID.
            port_name (str): Port name.
            debug_on (bool): Enable debug output.

        Returns:
            dict: JSON request body for set_port API.
        """

        if port_name:
            eid = self.resource_stats.name_to_eid(port_name)
            # print('eid inside')
            if resource_id is None:
                resource_id = eid[1]
                port_name = eid[2]
        REPORT_TIMER_MS_FAST = 1500
        data = {
            "shelf": 1,
            "resource": resource_id,
            "port": port_name,
            "current_flags": 0,  # vs 0x1 = interface down
            "interest": 8388610,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
            "report_timer": REPORT_TIMER_MS_FAST,
        }
        if debug_on:
            logger.debug("Port up request")
        return data

    def admin_up(self, port_eid):
        """
        Bring a LANforge port/admin interface UP.

        Args:
            port_eid (str): EID format, e.g., "1.1.sta0000".
        """
        # print("admin up called")
        # logger.info("186 admin_up port_eid: "+port_eid)
        eid = self.resource_stats.name_to_eid(port_eid)
        resource = eid[1]
        port = eid[2]
        logger.debug("ADMIN UP")
        logger.debug('eid : {}'.format(eid))
        request = self.port_up_request(resource_id=resource, port_name=port)
        logger.debug("request: {}".format(request))
        # logger.info("192.admin_up request: resource: %s port_name %s"%(resource, port))
        dbg_param = ""
        if logger.getEffectiveLevel() == logging.DEBUG:
            # logger.info("enabling url debugging")
            dbg_param = "?__debug=1"
        collected_responses = list()
        self.resource_stats.json_post("/cli-json/set_port%s" % dbg_param, request,
                       response_json_list_=collected_responses)
        # TODO: when doing admin-up ath10k radios, want a LF complaint about a license exception
        # if len(collected_responses) > 0: ...

    def admin_down(self, port_eid):
        eid = self.resource_stats.name_to_eid(port_eid)
        print("eid",eid)
        shelf = eid[0]
        resource_id = eid[1]
        port_name = eid[2]
        port_down_data = self.port_down_request(resource_id=resource_id,port_name=port_name)
        self.resource_stats.json_post("cli-json/set_port",port_down_data)

    def port_down_request(self,resource_id, port_name, debug_on=False):
        """
        Does not change the use_dhcp flag
        See http://localhost:8080/help/set_port
        :param debug_on:
        :param resource_id:
        :param port_name:
        :return: json payload
        """
        REPORT_TIMER_MS_FAST = 1500
        data = {
            "shelf": 1,
            "resource": resource_id,
            "port": port_name,
            "current_flags": 1,  # vs 0x0 = interface up
            "interest": 8388610,  # = current_flags + ifdown
            "report_timer": REPORT_TIMER_MS_FAST,
        }
        logger.debug("PORT DOWN REQUEST")
        logger.debug("With data {}".format(data))
        if debug_on:
            logger.debug("Port down request")
        return data

    def webgui_stop_check(self,test_name):
        try:
            print("ENTERED STOP CHECKKK")
            with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name), 'r') as file:
                data = json.load(file)
                if data["status"] != "Running":
                    logging.info('Test is stopped by the user')
                    self.test_stopped = True
            if not self.test_stopped:
                print("ENTERED NOT STOPPED")
                self.overall_status[test_name] = "started"
                self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                self.overall_status["current_mode"] = self.current_exec
                self.overall_status["current_test_name"] = test_name
                self.overall_csv.append(self.overall_status.copy())
                df1 = pd.DataFrame(self.overall_csv)
                df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
        except BaseException:
            logger.info(f"Error while running for webui during {test_name} execution")
        if self.test_stopped:
            logger.info("test has been stopped by the user")
            return False
        return True

    def webgui_test_done(self, test_name):
        try:
            self.overall_status[test_name] = "stopped"
            self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
            self.overall_csv.append(self.overall_status.copy())
            df1 = pd.DataFrame(self.overall_csv)
            df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
        except Exception as e:
            logger.info(e)

    def port_clean_up(self,port_no):
        print('port cleanup......')
        time.sleep(5)
        hostname = self.lanforge_ip
        username = "root"
        password = "lanforge"
        ports = []
        ports.append(port_no)
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.connect(hostname, username=username, password=password)

        # for cmd in commands:
        #     print(f"--- Running: {cmd} ---")
        #     stdin, stdout, stderr = ssh.exec_command(cmd)
        #     print("Output:\n", stdout.read().decode())
        #     print("Errors:\n", stderr.read().decode())
        # ssh.close()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # for port in ports:
        #     print(f"\n--- Checking port {port} ---")

        #     try:
        #         check_cmd = f"lsof -i :{port}"
        #         stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)  # ⬅ timeout added
        #         output = stdout.read().decode().strip()
        #         error = stderr.read().decode().strip()

        #         if output:
        #             print(f"Processes using port {port}:\n{output}")

        #             # kill_cmd = f"fuser -kv {port}/tcp"
        #             # kill_cmd = f"fuser -k {port}/tcp"
        #             kill_cmd = f"fuser -k {port}/tcp || true"
        #             stdin, stdout, stderr = ssh.exec_command(kill_cmd, timeout=10)
        #             print("Kill Output:\n", stdout.read().decode())
        #             print("Kill Errors:\n", stderr.read().decode())
        #         else:
        #             print(f"No process found on port {port}")

        #     except Exception as e:
        #         print(f"Error checking port {port}: {e}")

        for port in ports:
            print(f"\n--- Checking port {port} ---")

            try:
                # Get only the PIDs of processes using this port
                check_cmd = f"lsof -t -i:{port}"
                stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)
                pids = stdout.read().decode().strip().splitlines()

                if pids:
                    print(f"Processes using port {port}: {', '.join(pids)}")

                    # Kill each PID safely
                    for pid in pids:
                        kill_cmd = f"kill -9 {pid}"
                        ssh.exec_command(kill_cmd, timeout=10)
                        print(f"Killed PID {pid} on port {port}")
                else:
                    print(f"No process found on port {port}")

            except Exception as e:
                print(f"Error checking port {port}: {e}")

        ssh.close()


    def misc_clean_up(self,layer3=False,layer4=False,generic=False,port_5000=False,port_5002=False,port_5003=False,port_5005=False):
        """
        Use for the cleanup of cross connections
        arguments:
        layer3: (Boolean : optional) Default : False To Delete all layer3 connections
        layer4: (Boolean : optional) Default : False To Delete all layer4 connections
        """
        if self.no_cleanup:
            return
        if layer3:
            self.cleanup.cxs_clean()
            self.cleanup.layer3_endp_clean()
        if layer4:
            self.cleanup.layer4_endp_clean()
        if generic:
            resp = self.json_get('/generic?fields=name')
            if 'endpoints' in resp:
                for i in resp['endpoints']:
                    if list(i.values())[0]['name']:
                        self.generic_endps_profile.created_cx.append('CX_' + list(i.values())[0]['name'])
                        self.generic_endps_profile.created_endp.append(list(i.values())[0]['name'])
            self.generic_endps_profile.cleanup()
        # if port_5000 or port_5002 or port_5003 or port_5005:
        #     print('port cleanup......')
        #     time.sleep(5)
        #     hostname = self.lanforge_ip
        #     username = "root"
        #     password = "lanforge"
        #     ports = []
        #     if port_5003:
        #         ports.append(5003)
        #     if port_5000:
        #         ports.append(5000)
        #     if port_5002:
        #         ports.append(5002)
        #     if port_5005:
        #         ports.append(5005)
        
        #     # ssh = paramiko.SSHClient()
        #     # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #     # ssh.connect(hostname, username=username, password=password)

        #     # for cmd in commands:
        #     #     print(f"--- Running: {cmd} ---")
        #     #     stdin, stdout, stderr = ssh.exec_command(cmd)
        #     #     print("Output:\n", stdout.read().decode())
        #     #     print("Errors:\n", stderr.read().decode())
        #     # ssh.close()

        #     ssh = paramiko.SSHClient()
        #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #     ssh.connect(hostname, username=username, password=password)

        #     # for port in ports:
        #     #     print(f"\n--- Checking port {port} ---")

        #     #     try:
        #     #         check_cmd = f"lsof -i :{port}"
        #     #         stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)  # ⬅ timeout added
        #     #         output = stdout.read().decode().strip()
        #     #         error = stderr.read().decode().strip()

        #     #         if output:
        #     #             print(f"Processes using port {port}:\n{output}")

        #     #             # kill_cmd = f"fuser -kv {port}/tcp"
        #     #             # kill_cmd = f"fuser -k {port}/tcp"
        #     #             kill_cmd = f"fuser -k {port}/tcp || true"
        #     #             stdin, stdout, stderr = ssh.exec_command(kill_cmd, timeout=10)
        #     #             print("Kill Output:\n", stdout.read().decode())
        #     #             print("Kill Errors:\n", stderr.read().decode())
        #     #         else:
        #     #             print(f"No process found on port {port}")

        #     #     except Exception as e:
        #     #         print(f"Error checking port {port}: {e}")

        #     for port in ports:
        #         print(f"\n--- Checking port {port} ---")

        #         try:
        #             # Get only the PIDs of processes using this port
        #             check_cmd = f"lsof -t -i:{port}"
        #             stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=10)
        #             pids = stdout.read().decode().strip().splitlines()

        #             if pids:
        #                 print(f"Processes using port {port}: {', '.join(pids)}")

        #                 # Kill each PID safely
        #                 for pid in pids:
        #                     kill_cmd = f"kill -9 {pid}"
        #                     ssh.exec_command(kill_cmd, timeout=10)
        #                     print(f"Killed PID {pid} on port {port}")
        #             else:
        #                 print(f"No process found on port {port}")

        #         except Exception as e:
        #             print(f"Error checking port {port}: {e}")

        #     ssh.close()

    def use_device_list(self,device_list=None):
        device_list = device_list if device_list else []
        self.device_list = device_list

    
    def filter_tests(self):
        args = self.args
        if not args.series_tests and not args.parallel_tests:
            logger.error("Please provide tests cases --parallel_tests or --series_tests")
            logger.info(f"availbe tests are {self.test_map.keys()}")
            exit(0)
        if args.do_mix_exec:
            if "ping_test" not in args.parallel_tests:
                logger.error("With --do_mix_exec true, ping_test should be in parallel_tests")
                exit(0)
        flag=1
        tests_to_run_series = []
        tests_to_run_parallel = []
        if args.series_tests:
            tests_to_run_series = args.series_tests.split(',')
            for test in tests_to_run_series:
                if test not in self.test_map:
                    logger.error(f"{test} is not availble in test suite")
                    flag = 0
        if args.parallel_tests:
            tests_to_run_parallel = args.parallel_tests.split(',')
            for test in tests_to_run_parallel:
                if test not in self.test_map:
                    logger.error(f"{test} is not availble in test suite")
                    flag = 0


        if not flag:
            logger.info(f"availble tests are {self.test_map.keys()}")
            exit(0)
        if args.parallel_tests and (len(tests_to_run_parallel) != len(set(tests_to_run_parallel))):
            logger.error("in --parallel dont specify duplicate tests")
            exit(0)
        return tests_to_run_series,tests_to_run_parallel

    def start_scenario(self):
        test_map = self.test_map.copy()
        tests_to_run_series,tests_to_run_parallel = self.filter_tests()

        duration_dict = self.create_duration_dict_and_validate()
        

        self.duration_dict = duration_dict.copy()
        # args.current = "series"
        self.start_tests(tests_to_run_parallel, tests_to_run_series,duration_dict)

    def start_tests(self,tests_to_run_parallel, tests_to_run_series,duration_dict):
        args = self.args
        iszoom = 'zoom_test' in tests_to_run_parallel or 'zoom_test' in tests_to_run_series
        isrb = 'rb_test' in tests_to_run_parallel or 'rb_test' in tests_to_run_series
        isyt = 'yt_test' in tests_to_run_parallel or 'yt_test' in tests_to_run_series
        isteams = 'teams_test' in tests_to_run_parallel or 'teams_test' in tests_to_run_series
        self.series_tests = tests_to_run_series
        self.parallel_tests = tests_to_run_parallel
        self.misc_clean_up(layer3=True,layer4=True,generic=True,port_5000=iszoom,port_5002=isyt,port_5003=isrb,port_5005=isteams)
        if args.series_tests or args.parallel_tests:
            series_threads = []
            parallel_threads = []
            parallel_connect = []
            series_connect = []
            rb_test = 'rb_test' in tests_to_run_parallel
            yt_test = 'yt_test' in tests_to_run_parallel
            zoom_test = 'zoom_test' in tests_to_run_parallel
            # Process series tests
            if args.series_tests:
                ordered_series_tests = args.series_tests.split(',')
                if args.device_list or (args.file_name and args.group_name and args.profile_name):
                    args = update_device_list(args,ordered_series_tests,self)
                    # print("Args",args)
                    # exit(0)
                # ordered_parallel_tests = args.parallel_tests.split(',')
                # phase 1
                if args.dowebgui:
                    gen_order = ["ping_test","qos_test","ftp_test","http_test","mcast_test","vs_test","thput_test","yt_test","rb_test","zoom_test","teams_test"]
                    temp_ord_list = []
                    for test_name in gen_order:
                        if test_name in ordered_series_tests:
                            temp_ord_list.append(test_name)
                    ordered_series_tests = temp_ord_list.copy()
                for idx, test_name in enumerate(ordered_series_tests):
                    test_name = test_name.strip().lower()
                    if test_name in self.test_map:
                        func, label = self.test_map[test_name]
                        args.current = "series"
                        if test_name in ['rb_test','zoom_test','yt_test','teams_test', 'vlc_test']:
                            if test_name == "rb_test":
                                obj_no = 1
                                while f"rb_test_{obj_no}" in self.rb_obj_dict["series"]:
                                    obj_no+=1
                                obj_name = f"rb_test_{obj_no}"
                                self.rb_obj_dict["series"][obj_name] = manager.dict({"obj":None,"data":None})
                                print('hiii data',self.rb_obj_dict)
                            elif test_name == "yt_test":
                                obj_no = 1
                                while f"yt_test_{obj_no}" in self.yt_obj_dict["series"]:
                                    obj_no+=1
                                obj_name = f"yt_test_{obj_no}"
                                self.yt_obj_dict["series"][obj_name] = manager.dict({"obj":None,"data":None})
                            elif test_name == "zoom_test":
                                obj_no = 1
                                while f"zoom_test_{obj_no}" in self.zoom_obj_dict["series"]:
                                    obj_no+=1
                                obj_name = f"zoom_test_{obj_no}"
                                self.zoom_obj_dict["series"][obj_name] = manager.dict({"obj":None,"data":None})
                                print('hiii data',self.zoom_obj_dict)
                            elif test_name == "teams_test":
                                obj_no = 1
                                while f"teams_test_{obj_no}" in self.teams_obj_dict["series"]:
                                    obj_no+=1
                                obj_name = f"teams_test_{obj_no}"
                                self.teams_obj_dict["series"][obj_name] = manager.dict({"obj":None,"data":None})
                            elif test_name == "vlc_test":
                                obj_no = 1
                                while f"vlc_test_{obj_no}" in self.vlc_obj_dict["series"]:
                                    obj_no+=1
                                obj_name = f"vlc_test_{obj_no}"
                                self.vlc_obj_dict["series"][obj_name] = manager.dict({"obj":None,"data":None})
                                print('hiii data',self.vlc_obj_dict)
                            series_threads.append(multiprocessing.Process(target=run_test_safe(func, f"{label} [Series {idx+1}]", args, self,duration_dict[test_name])))
                        else:                 
                            series_threads.append(threading.Thread(
                                target=run_test_safe(func, f"{label} [Series {idx+1}]", args, self,duration_dict[test_name])
                            ))
                    else:
                        print(f"Warning: Unknown test '{test_name}' in --series_tests")
            
            # Process parallel tests
            if args.parallel_tests:
                ordered_parallel_tests = args.parallel_tests.split(',')
                #phase 1
                if args.dowebgui:
                    gen_order = ["ping_test","qos_test","ftp_test","http_test","mcast_test","vs_test","thput_test","yt_test","rb_test","zoom_test","teams_test"]
                    temp_ord_list = []
                    for test_name in gen_order:
                        if test_name in ordered_parallel_tests:
                            temp_ord_list.append(test_name)
                    ordered_parallel_tests = temp_ord_list.copy()
                if args.device_list or (args.file_name and args.group_name and args.profile_name):
                    args = update_device_list(args,ordered_parallel_tests,self)
                    # print("Args",args)
                    # exit(0)
                for idx, test_name in enumerate(ordered_parallel_tests):
                    test_name = test_name.strip().lower()
                    if test_name in self.test_map:
                        func, label = self.test_map[test_name]
                        args.current = "parallel"
                        if test_name in ['rb_test','zoom_test','yt_test','teams_test', 'vlc_test']:
                            # if test_name == "rb_test":
                                # self.rb_pipe_dict["parallel"][len(self.rb_pipe_dict["parallel"])] = {}
                                # self.rb_pipe_dict["parallel"][len(self.rb_pipe_dict["parallel"])]["parent"],self.rb_pipe_dict["parallel"][len(self.rb_pipe_dict["parallel"])]["child"] = multiprocessing.Pipe()
                            # parent_conn, child_conn = multiprocessing.Pipe()
                            # self.parallel_connect[idx] = [test_name,parent_conn,child_conn]
                            if test_name == "rb_test":
                                self.rb_obj_dict["parallel"]["rb_test"] = manager.dict({"obj": None, "data": None})
                            elif test_name == "yt_test":
                                self.yt_obj_dict["parallel"]["yt_test"] = manager.dict({"obj": None, "data": None})
                            elif test_name == "zoom_test":
                                self.zoom_obj_dict["parallel"]["zoom_test"] = manager.dict({"obj": None, "data": None})
                            elif test_name == "teams_test":
                                self.teams_obj_dict["parallel"]["teams_test"] = manager.dict({"obj": None, "data": None})
                            elif test_name == "vlc_test":
                                self.vlc_obj_dict["parallel"]["vlc_test"] = manager.dict({"obj": None, "data": None})
                            parallel_threads.append(multiprocessing.Process(target=run_test_safe(func, f"{label} [Parallel {idx+1}]", args, self,duration_dict[test_name])))
                        else:                 
                            parallel_threads.append(threading.Thread(
                                target=run_test_safe(func, f"{label} [Parallel {idx+1}]", args, self,duration_dict[test_name])
                            ))
                    else:
                        print(f"Warning: Unknown test '{test_name}' in --parallel_tests")
        
            logging.info(f"Series Threads: {series_threads}")
            logging.info(f"Parallel Threads: {parallel_threads}")
            logging.info(f"connections parallel {self.parallel_connect}")
            logging.info(f"connections series{self.series_connect}")
            # time.sleep(20)
            if args.dowebgui:
                # overall_path = os.path.join(args.result_dir, directory)
                self.overall_status = {"ping": "notstarted", "qos": "notstarted", "ftp": "notstarted", "http": "notstarted",
                                "mc": "notstarted", "vs": "notstarted", "thput": "notstarted","rb": "notstarted","vs": "notstarted","zoom": "notstarted","yt": "notstarted","teams": "notstarted", "time": datetime.datetime.now().strftime("%Y %d %H:%M:%S"), "status": "running", "current_mode":"tbd" , "current_test_name": "tbd"}
                self.overall_csv.append(self.overall_status.copy())
                df1 = pd.DataFrame(self.overall_csv)
                df1.to_csv('{}/overall_status.csv'.format(args.result_dir), index=False)
            if args.iot_test:
                iot_ip = args.iot_ip
                iot_port = args.iot_port
                iot_iterations = args.iot_iterations
                iot_delay = args.iot_delay
                iot_device_list = args.iot_device_list
                iot_testname = args.iot_testname
                iot_increment = args.iot_increment
                if args.iot_iterations > 1:
                    thread = threading.Thread(target=trigger_iot, args=(iot_ip, iot_port, iot_iterations, iot_delay, iot_device_list, iot_testname, iot_increment))
                    thread.start()
                else:
                    total_secs = 9999
                    iot_iterations = max(1, total_secs // args.iot_delay)
                    iot_thread = threading.Thread(
                        target=trigger_iot,
                        args=(
                            args.iot_ip,
                            args.iot_port,
                            iot_iterations,
                            args.iot_delay,
                            args.iot_device_list,
                            args.iot_testname,
                            args.iot_increment
                        ),
                        daemon=True
                    )
                    iot_thread.start()
            if args.do_mix_exec:
                series_runner = threading.Thread(target=self.run_series, args=(series_threads,))
                parallel_runner = threading.Thread(target=self.run_parallel, args=(parallel_threads,))

                series_runner.start()
                parallel_runner.start()

                series_runner.join()
                parallel_runner.join()      
            elif args.order_priority == 'series':
                self.current_exec="series"
                for t in series_threads:
                    t.start()
                    t.join()
                    self.series_index += 1
                # Then run parallel tests
                if len(parallel_threads) != 0:
                    # self.misc_clean_up(layer3=False,layer4=False,generic=True)
                    self.misc_clean_up(layer3=True,layer4=True,generic=True,port_5000=iszoom,port_5002=isyt,port_5003=isrb,port_5005=isteams)
                    print('starting parallel tests.......')
                    time.sleep(10)
                self.current_exec = "parallel"
                for t in parallel_threads:
                    t.start()

                self.parallel_index = 0
                for t in parallel_threads:
                    t.join()
                    self.parallel_index += 1
            
            else:
                self.current_exec="parallel"
                for t in parallel_threads:
                    t.start()
                # for p in parallel_processes:
                #     p.start()

                for t in parallel_threads:
                    t.join()

                if len(series_threads) != 0:
                    rb_test = 'rb_test' in tests_to_run_parallel
                    yt_test = 'yt_test' in tests_to_run_parallel
                    self.misc_clean_up(layer3=True,layer4=True,generic=True,port_5000=iszoom,port_5002=isyt,port_5003=isrb,port_5005=isteams)
                    print('starting Series tests.......')
                    time.sleep(5)
                self.current_exec="series"
                for t in series_threads:
                    t.start()
                    t.join()
        else:
            logger.error("provide either --paralell_tests or --series_tests")
            exit(1)
        rb_test = 'rb_test' in tests_to_run_parallel
        yt_test = 'yt_test' in tests_to_run_parallel
        self.misc_clean_up(layer3=True,layer4=True,generic=True,port_5000=iszoom,port_5002=isyt,port_5003=isrb,port_5005=isteams)
        log_file = save_logs()
        print(f"Logs saved to: {log_file}")
        test_results_df = pd.DataFrame(list(test_results_list))
        iot_summary = None
        if args.iot_test and args.iot_testname:
            base = path.join("results", args.iot_testname)
            p = path.join(base, "iot_summary.json")
            if path.exists(p):
                with open(p) as f:
                    iot_summary = json.load(f)
        args_dict = vars(args)
        self.generate_overall_report(test_results_df=test_results_df,args_dict=args_dict,iot_summary=iot_summary)
        if self.dowebgui:
            try:
                self.overall_status["status"] = "completed"
                self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                self.overall_csv.append(self.overall_status.copy())
                df1 = pd.DataFrame(self.overall_csv)
                df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
            except Exception as e:
                logging.info("Error while wrinting status file for webui", e)

        print("\nTest Results Summary:")
        print(test_results_df)
    def create_duration_dict_and_validate(self):
        args=self.args
        duration_flag = False
        duration_dict = {}
        args_dict = vars(args)
        if args.series_tests:
            for test in args.series_tests.split(','):
                if test == "thput_test":
                    duration_dict[test] = validate_time(args_dict[f"{test}_duration"])
                elif test == "mcast_test":
                    duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_test_duration"])
                elif test == "ping_test" or test == "zoom_test" or test == "teams_test":
                    duration_dict[test] = "{} mins".format(args_dict["{}_duration".format(test.split('_')[0])])
                else:
                    duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_duration"])
        if args.parallel_tests:
            for test in args.parallel_tests.split(','):
                if test == "thput_test":
                    duration_dict[test] = validate_time(args_dict[f"{test}_duration"])
                elif test == "mcast_test":
                    duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_test_duration"])
                elif test == "ping_test" or test == "zoom_test" or test == "teams_test":
                    duration_dict[test] = "{} mins".format(args_dict["{}_duration".format(test.split('_')[0])])
                else:
                    duration_dict[test] = validate_time(args_dict[f"{test.split('_')[0]}_duration"])
        for test_name,duration in duration_dict.items():
            if duration == "wrong type":
                duration_flag = True
                print(f"wrong duration type for {test_name}")
        if duration_flag:
            exit(1)
        return duration_dict

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
                if 'interface' in port_data.keys():
                    port_data['interfaces'] = [port_data['interface']]
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
            _, device_data = self.api_get('/port/{}/{}/{}?fields=phantom,down,ssid,ap,signal,mac'.format(shelf, resource, port_name))
            device_data = device_data['interface']
            if device_data['phantom'] or device_data['down']:
                print('{} is in phantom state or down state, data may not be accurate.'.format(device))
            connection_details[device] = device_data
        return connection_details

    def filter_iOS_devices(self, device_list):
        modified_device_list = device_list
        if type(device_list) is str:
            modified_device_list = device_list.split(',')
        filtered_list = []
        for device in modified_device_list:
            if device.count('.') == 1:
                shelf, resource = device.split('.')
            elif device.count('.') == 2:
                shelf, resource, port = device.split('.')
            elif device.count('.') == 0:
                shelf, resource = 1, device
            response_code, device_data = self.api_get('/resource/{}/{}'.format(shelf, resource))
            if 'status' in device_data and device_data['status'] == 'NOT_FOUND':
                print('Device {} is not found.'.format(device))
                continue
            device_data = device_data['resource']
            # print(device_data)
            if 'Apple' in device_data['hw version'] and (device_data['app-id'] != '') and (device_data['app-id'] != '0' or device_data['kernel'] == ''):
                print('{} is an iOS device. Currently we do not support iOS devices.'.format(device))
            else:
                filtered_list.append(device)
        if type(device_list) is str:
            filtered_list = ','.join(filtered_list)
        return filtered_list

    def render_overall_report(self,test_name=""):
        if test_name == "http_test":
            if test_name not in self.test_count_dict:
                self.test_count_dict[test_name] = 1



    def run_ping_test(
        self,
        target: str = '1.1.eth1',
        ping_interval: str = '1',
        ping_duration: float = 1,
        ssid: str = None,
        mgr_passwd: str = 'lanforge',
        server_ip: str = None,
        security: str = 'open',
        passwd: str = '[BLANK]',
        virtual: bool = False,
        num_sta: int = 1,
        radio: str = None,
        real: bool = True,
        use_default_config: bool = True,
        debug: bool = False,
        local_lf_report_dir: str = "",
        log_level: str = None,
        lf_logger_config_json: str = None,
        help_summary: bool = False,
        group_name: str = None,
        profile_name: str = None,
        file_name: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = '',
        ieee8021x: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = '[BLANK]',
        private_key: str = '[BLANK]',
        ca_cert: str = '[BLANK]',
        client_cert: str = '[BLANK]',
        pk_passwd: str = '[BLANK]',
        pac_file: str = '[BLANK]',
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        wait_time: int = 60,
        dev_list: str = None,
        sta_to_res = None,
        sta_port="eth1",
        res_ip=None

    ):
        sta_to_res = sta_to_res if sta_to_res else []
        res_ip = res_ip if res_ip else []

        # set the logger level to debug
        logger_config = lf_logger_config.lf_logger_config()

        if log_level:
            logger_config.set_level(level=log_level)

        if lf_logger_config_json:
            # logger_config.lf_logger_config_json = "lf_logger_config.json"
            logger_config.lf_logger_config_json = lf_logger_config_json
            logger_config.load_lf_logger_config()
        # validate_args(args)

        mgr_ip = self.lanforge_ip
        mgr_password = mgr_passwd
        mgr_port = self.port
        server_ip = server_ip
        ssid = ssid
        security = security
        password = passwd
        num_sta = num_sta
        radio = radio
        target = target
        interval = ping_interval
        duration = ping_duration
        configure = not use_default_config
        debug = debug
        group_name = group_name
        file_name = file_name
        profile_name = profile_name
        eap_method = eap_method
        eap_identity = eap_identity
        ieee80211 = ieee8021x
        ieee80211u = ieee80211u
        ieee80211w = ieee80211w
        enable_pkc = enable_pkc
        bss_transition = bss_transition
        power_save = power_save
        disable_ofdma = disable_ofdma
        roam_ft_ds = roam_ft_ds
        key_management = key_management
        pairwise = pairwise
        private_key = private_key
        ca_cert = ca_cert
        client_cert = client_cert
        pk_passwd = pk_passwd
        pac_file = pac_file
        if (debug):
            print('''Specified configuration:
                ip:                       {}
                port:                     {}
                ssid:                     {}
                security:                 {}
                password:                 {}
                target:                   {}
                Ping interval:            {}
                Packet Duration (in min): {}
                virtual:                  {}
                num of virtual stations:  {}
                radio:                    {}
                real:                     {}
                debug:                    {}
                '''.format(mgr_ip, mgr_port, ssid, security, password, target, interval, duration, virtual, num_sta, radio, real, debug))

        ce = self.current_exec #seires
        if self.do_mix_exec:
            ce = "parallel"
        if ce == "parallel" or self.do_mix_exec:
            obj_name = "ping_test"
        else:
            obj_no = 1
            while f"ping_test_{obj_no}" in self.ping_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"ping_test_{obj_no}" 
        self.ping_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        # ping object creation
        self.ping_obj_dict[ce][obj_name]["obj"] = Ping(host=mgr_ip, port=mgr_port, ssid=ssid, security=security, password=password, radio=radio,
                    lanforge_password=mgr_password, target=target, interval=interval, sta_list=[], virtual=virtual, real=real, duration=duration, debug=debug, csv_name=device_csv_name,
                    expected_passfail_val=expected_passfail_value, wait_time=wait_time, group_name=group_name,sta_to_res=sta_to_res,sta_port=sta_port,res_ip=res_ip)

        # changing the target from port to IP
        self.ping_obj_dict[ce][obj_name]["obj"].change_target_to_ip()

        # creating virtual stations if --virtual flag is specified
        if (virtual):

            logging.info('Proceeding to create {} virtual stations on {}'.format(num_sta, radio))
            station_list = LFUtils.portNameSeries(
                prefix_='sta', start_id_=0, end_id_=num_sta - 1, padding_number_=100000, radio=radio)
            self.ping_obj_dict[ce][obj_name]["obj"].sta_list = station_list
            if (debug):
                logging.info('Virtual Stations: {}'.format(station_list).replace(
                    '[', '').replace(']', '').replace('\'', ''))

        # selecting real clients if --real flag is specified
        if (real):
            Devices = RealDevice(manager_ip=mgr_ip, selected_bands=[])
            Devices.get_devices()
            self.ping_obj_dict[ce][obj_name]["obj"].Devices = Devices
            # self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices)
            # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
            if (configure):
                config_devices = {}
                obj = DeviceConfig.DeviceConfig(lanforge_ip=mgr_ip, file_name=file_name, wait_time=wait_time)
                # Case 1: Group name, file name, and profile name are provided
                if group_name and file_name and profile_name:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]
                    obj.initiate_group()
                    group_device_map = obj.get_groups_devices(data=selected_groups, groupdevmap=True)
                    # Configure devices in the selected group with the selected profile
                    eid_list = asyncio.run(obj.connectivity(config=config_devices, upstream=server_ip))
                    Devices.get_devices()
                    self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=eid_list)
                # Case 2: Device list is empty but config flag is True — prompt the user to input device details for configuration
                else:
                    all_devices = obj.get_all_devices()
                    device_list = []
                    config_dict = {
                        'ssid': ssid,
                        'passwd': password,
                        'enc': security,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee80211,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': server_ip,
                    }
                    for device in all_devices:
                        if device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                        else:
                            device_list.append(device["eid"] + " " + device["serial"])
                    logger.info(f"Available devices: {device_list}")
                    if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res and not dev_list:
                        dev_list = []
                    elif not dev_list:
                        dev_list = input("Enter the desired resources to run the test:").split(',')
                    else:
                        dev_list = dev_list.split(",")
                    dev_list = asyncio.run(obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                    Devices.get_devices()
                    self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=dev_list)
            # Case 3: Config is False, no device list is provided, and no group is selected
            # Prompt the user to manually input devices for running the test
            else:
                device_list = self.ping_obj_dict[ce][obj_name]["obj"].Devices.get_devices()
                logger.info(f"Available devices: {device_list}")
                if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res and not dev_list:
                    dev_list = []
                elif not dev_list:
                    dev_list = input("Enter the desired resources to run the test:").split(',')
                else:
                    dev_list = dev_list.split(",")
                # dev_list = input("Enter the desired resources to run the test:").split(',')
                self.ping_obj_dict[ce][obj_name]["obj"].select_real_devices(real_devices=Devices, device_list=dev_list)

        # station precleanup
        if not sta_to_res:
            self.ping_obj_dict[ce][obj_name]["obj"].cleanup() #11 change
        else:
            self.ping_obj_dict[ce][obj_name]["obj"].clear_cx_startswith("GENERIC")

        # building station if virtual
        if (virtual):
            self.ping_obj_dict[ce][obj_name]["obj"].buildstation()

        # check if generic tab is enabled or not
        if (not self.ping_obj_dict[ce][obj_name]["obj"].check_tab_exists()):
            logging.error('Generic Tab is not available.\nAborting the test.')
            return False

        self.ping_obj_dict[ce][obj_name]["obj"].sta_list += self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list

        # creating generic endpoints
        self.ping_obj_dict[ce][obj_name]["obj"].create_generic_endp()

        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].generic_endps_profile.created_cx)

        # run the test for the given duration
        if not self.do_mix_exec:
            logging.info('Running the ping test for {} minutes'.format(duration))

        # start generate endpoint
        self.ping_obj_dict[ce][obj_name]["obj"].start_generic()
        # time_counter = 0
        ports_data_dict = self.ping_obj_dict[ce][obj_name]["obj"].json_get('/ports/all/')['interfaces']
        ports_data = {}
        for ports in ports_data_dict:
            port, port_data = list(ports.keys())[0], list(ports.values())[0]
            ports_data[port] = port_data
        ping_duration = duration
        
        if self.dowebgui:
            try:
                with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.lanforge_ip, self.test_name), 'r') as file:
                    data = json.load(file)
                    if data["status"] != "Running":
                        logging.info('Test is stopped by the user')
                        self.test_stopped = True
                if not self.test_stopped:
                    self.overall_status['ping'] = "started"
                    self.overall_status["time"] = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
                    self.overall_status["current_mode"] = ce
                    self.overall_status["current_test_name"] = "ping"
                    self.overall_csv.append(self.overall_status.copy())
                    df1 = pd.DataFrame(self.overall_csv)
                    df1.to_csv('{}/overall_status.csv'.format(self.result_dir), index=False)
            except BaseException:
                logger.info("Error while running for webui during ping execution")
            if self.test_stopped:
                logger.info("test has been stopped by the user")
                return False
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(seconds=ping_duration * 60)
            temp_json = []
            while (datetime.datetime.now() < end_time) or self.do_mix_exec:
                temp_json = []
                temp_checked_sta = []
                temp_result_data = self.ping_obj_dict[ce][obj_name]["obj"].get_results()
                if isinstance(temp_result_data, dict):
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                        current_device_data = ports_data[station]
                        if (station in temp_result_data['name']):
                            temp_json.append({
                                'device': station,
                                'sent': temp_result_data['tx pkts'],
                                'recv': temp_result_data['rx pkts'],
                                'dropped': temp_result_data['dropped'],
                                'status': "Running",
                                'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                "remaining_time": ""
                            })
                else:
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                        current_device_data = ports_data[station]
                        for ping_device in temp_result_data:
                            ping_endp, ping_data = list(ping_device.keys())[0], list(ping_device.values())[0]
                            if station.split('-')[-1] in ping_endp and station not in temp_checked_sta:
                                temp_checked_sta.append(station)
                                temp_json.append({
                                    'device': station,
                                    'sent': ping_data['tx pkts'],
                                    'recv': ping_data['rx pkts'],
                                    'dropped': ping_data['dropped'],
                                    'status': "Running",
                                    'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                    'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                    "remaining_time": ""
                                })
                df1 = pd.DataFrame(temp_json)
                df1.to_csv('{}/ping_datavalues.csv'.format(self.result_dir), index=False)
                # try:
                #     with open(self.result_dir + "/../../Running_instances/{}_{}_running.json".format(self.host, self.test_name), 'r') as file:
                #         data = json.load(file)
                #         if data["status"] != "Running":
                #             logging.info('Test is stopped by the user')
                #             break
                # except BaseException:
                #     logging.info("execption while reading running json in ping")
                time.sleep(3)
                if self.stop_all_tests:
                    break
        else:
            if self.do_mix_exec:
                start_time = datetime.datetime.now()
                while not self.stop_all_tests:
                    time.sleep(1)
                end_time = datetime.datetime.now()
                formatted_time = validate_time(int((datetime.datetime.now() - start_time).total_seconds()))
                print("Ping test duration: {}".format(formatted_time))
                self.names_duration["ping"] = formatted_time

            else:
                time.sleep(ping_duration * 60)

        logging.info('Stopping the test')
        self.ping_obj_dict[ce][obj_name]["obj"].stop_generic()

        result_data = self.ping_obj_dict[ce][obj_name]["obj"].get_results()
        # logging.info(result_data)
        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].result_json)
        
        if sta_to_res:
            if isinstance(result_data, dict):
                # Check if it is Type 2 (single device raw dict)
                if 'last results' in result_data:
                    result_data = [{self.ping_obj_dict[ce][obj_name]["obj"].generic_endps_profile.created_endp[0]: result_data}]
                else:
                    result_data = [result_data]
            if isinstance(result_data, list):
                print("yesss")
                self.ping_obj_dict[ce][obj_name]["obj"].result_json = {}

                for item in result_data:
                    # Each item is like {'GENERIC_0-eth1': {...}}
                    endpoint = list(item.keys())[0]
                    data = list(item.values())[0]

                    try:
                        last_results = data.get('last results', '')
                        last_line = ''

                        if last_results:
                            lines = last_results.strip().split('\n')
                            if len(lines) >= 2:
                                last_line = lines[-2]

                        # Default RTT values
                        min_rtt = avg_rtt = max_rtt = '0'

                        if last_line and 'min/avg/max' in last_line:
                            rtt_section = last_line.split('min/avg/max:')[-1].strip()
                            rtt_values = rtt_section.split('/')

                            if len(rtt_values) == 3:
                                min_rtt = rtt_values[0]
                                avg_rtt = rtt_values[1]
                                max_rtt = rtt_values[2]

                        self.ping_obj_dict[ce][obj_name]["obj"].result_json[endpoint] = {
                            'command': data.get('command', ''),
                            'sent': data.get('tx pkts', '0'),
                            'recv': data.get('rx pkts', '0'),
                            'dropped': data.get('dropped', '0'),
                            'min_rtt': min_rtt,
                            'avg_rtt': avg_rtt,
                            'max_rtt': max_rtt,
                            'name': endpoint,
                            'last_result': last_line,
                            'remarks': []
                        }

                    except Exception as e:
                        logging.error(f"Failed parsing result for {endpoint}: {e}")

        else:
            if (virtual):
                ports_data_dict = self.ping_obj_dict[ce][obj_name]["obj"].json_get('/ports/all/')['interfaces']
                ports_data = {}
                for ports in ports_data_dict:
                    port, port_data = list(ports.keys())[0], list(ports.values())[0]
                    ports_data[port] = port_data
                if (isinstance(result_data, dict)):
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].sta_list:
                        if (station not in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list):
                            current_device_data = ports_data[station]
                            if (station.split('.')[2] in result_data['name']):
                                try:
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                        'command': result_data['command'],
                                        'sent': result_data['tx pkts'],
                                        'recv': result_data['rx pkts'],
                                        'dropped': result_data['dropped'],
                                        'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'mac': current_device_data['mac'],
                                        'channel': current_device_data['channel'],
                                        'ssid': current_device_data['ssid'],
                                        'mode': current_device_data['mode'],
                                        'name': station,
                                        'os': 'Virtual',
                                        'remarks': [],
                                        'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                                    }
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                except BaseException:
                                    logging.error('Failed parsing the result for the station {}'.format(station))

                else:
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].sta_list:
                        if (station not in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list):
                            current_device_data = ports_data[station]
                            for ping_device in result_data:
                                ping_endp, ping_data = list(ping_device.keys())[
                                    0], list(ping_device.values())[0]
                                if (station.split('.')[2] in ping_endp):
                                    try:
                                        self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                            'command': ping_data['command'],
                                            'sent': ping_data['tx pkts'],
                                            'recv': ping_data['rx pkts'],
                                            'dropped': ping_data['dropped'],
                                            'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                            'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                            'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                            'mac': current_device_data['mac'],
                                            'ssid': current_device_data['ssid'],
                                            'channel': current_device_data['channel'],
                                            'mode': current_device_data['mode'],
                                            'name': station,
                                            'os': 'Virtual',
                                            'remarks': [],
                                            'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                        }
                                        self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                    except BaseException:
                                        logging.error('Failed parsing the result for the station {}'.format(station))

            if (real):
                if (isinstance(result_data, dict)):
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                        current_device_data = Devices.devices_data[station]
                        # logging.info(current_device_data)
                        if (station in result_data['name']):
                            try:
                                # logging.info(result_data['last results'].split('\n'))
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                    'command': result_data['command'],
                                    'sent': result_data['tx pkts'],
                                    'recv': result_data['rx pkts'],
                                    'dropped': result_data['dropped'],
                                    'min_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'avg_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'max_rtt': [result_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(result_data['last results']) != 0 and 'min/avg/max' in result_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                    'mac': current_device_data['mac'],
                                    'ssid': current_device_data['ssid'],
                                    'channel': current_device_data['channel'],
                                    'mode': current_device_data['mode'],
                                    'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                    'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                    'remarks': [],
                                    'last_result': [result_data['last results'].split('\n')[-2] if len(result_data['last results']) != 0 else ""][0]
                                }
                                self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                            except BaseException:
                                logging.error('Failed parsing the result for the station {}'.format(station))
                else:
                    for station in self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list:
                        current_device_data = Devices.devices_data[station]
                        for ping_device in result_data:
                            ping_endp, ping_data = list(ping_device.keys())[
                                0], list(ping_device.values())[0]
                            if (station in ping_endp):
                                try:
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station] = {
                                        'command': ping_data['command'],
                                        'sent': ping_data['tx pkts'],
                                        'recv': ping_data['rx pkts'],
                                        'dropped': ping_data['dropped'],
                                        'min_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[0] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'avg_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[1] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'max_rtt': [ping_data['last results'].split('\n')[-2].split()[-1].split(':')[-1].split('/')[2] if len(ping_data['last results']) != 0 and 'min/avg/max' in ping_data['last results'].split('\n')[-2] else '0'][0],  # noqa E501
                                        'mac': current_device_data['mac'],
                                        'ssid': current_device_data['ssid'],
                                        'channel': current_device_data['channel'],
                                        'mode': current_device_data['mode'],
                                        'name': [current_device_data['user'] if current_device_data['user'] != '' else current_device_data['hostname']][0],
                                        'os': ['Windows' if 'Win' in current_device_data['hw version'] else 'Linux' if 'Linux' in current_device_data['hw version'] else 'Mac' if 'Apple' in current_device_data['hw version'] else 'Android'][0],  # noqa E501
                                        'remarks': [],
                                        'last_result': [ping_data['last results'].split('\n')[-2] if len(ping_data['last results']) != 0 else ""][0]
                                    }
                                    self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['remarks'] = self.ping_obj_dict[ce][obj_name]["obj"].generate_remarks(self.ping_obj_dict[ce][obj_name]["obj"].result_json[station])
                                except BaseException:
                                    logging.error('Failed parsing the result for the station {}'.format(station))

        logging.info(self.ping_obj_dict[ce][obj_name]["obj"].result_json)

        # station post cleanup
        self.ping_obj_dict[ce][obj_name]["obj"].cleanup() #12 change
        if self.dowebgui:
            temp_json = []
            for station in self.ping_obj_dict[ce][obj_name]["obj"].result_json:
                logging.debug('{} {}'.format(station, self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]))
                temp_json.append({'device': station,
                                    'sent': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['sent'],
                                    'recv': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['recv'],
                                    'dropped': self.ping_obj_dict[ce][obj_name]["obj"].result_json[station]['dropped'],
                                    'status': "Stopped",
                                    'start_time': start_time.strftime("%d/%m %I:%M:%S %p"),
                                    'end_time': end_time.strftime("%d/%m %I:%M:%S %p"),
                                    "remaining_time": ""})
            df1 = pd.DataFrame(temp_json)
            df1.to_csv('{}/ping_datavalues.csv'.format(self.result_dir), index=False)
        if local_lf_report_dir == "":
            # Report generation when groups are specified but no custom report path is provided
            if group_name:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(config_devices=config_devices, group_device_map=group_device_map)
            # Report generation when no group is specified and no custom report path is provided
            else:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report()
        else:
            # Report generation when groups are specified and a custom report path is provided
            if group_name:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(config_devices=config_devices, group_device_map=group_device_map, report_path=local_lf_report_dir)
            # Report generation when no group is specified but a custom report path is provided
            else:
                self.ping_obj_dict[ce][obj_name]["obj"].generate_report(report_path=local_lf_report_dir)
        params = {
            "result_json": None,
            "result_dir": "Ping_Test_Report",
            "report_path": "",
            "config_devices": "",
            "group_device_map": {}
        }
        
        if local_lf_report_dir != "":
            params["report_path"] = local_lf_report_dir

        if group_name:
            params["config_devices"] = config_devices
            params["group_device_map"] = group_device_map
        self.ping_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("ping")
        return True

    def run_http_test(
        self,
        upstream_port='eth2',
        num_stations=0,
        twog_radio='wiphy3',
        fiveg_radio='wiphy0',
        sixg_radio='wiphy2',
        twog_security=None,
        twog_ssid=None,
        twog_passwd=None,
        fiveg_security=None,
        fiveg_ssid=None,
        fiveg_passwd=None,
        sixg_security=None,
        sixg_ssid=None,
        sixg_passwd=None,
        target_per_ten=100,
        file_size='5MB',
        bands=["5G", "2.4G", "6G"],
        duration=None,
        client_type="Real",
        threshold_5g="60",
        threshold_2g="90",
        threshold_both="50",
        ap_name="TestAP",
        lf_username="lanforge",
        lf_password="lanforge",
        ssh_port=22,
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="lf_webpage",
        csv_outfile="",
        dowebgui=False,
        result_dir='',
        device_list=[],
        test_name=None,
        get_url_from_file=False,
        file_path=None,
        help_summary=False,
        ssid=None,
        passwd='',
        security=None,
        file_name=None,
        group_name=None,
        profile_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        get_live_view=False,
        total_floors="0"
    ):
            if self.dowebgui:
                if not self.webgui_stop_check("http"):
                    return False
            bands.sort()

            # Error checking to prevent case issues
            for band in range(len(bands)):
                bands[band] = bands[band].upper()
                if bands[band] == "BOTH":
                    bands[band] = "Both"

            # Error checking for non-existent bands
            valid_bands = ['2.4G', '5G', '6G', 'Both']
            for band in bands:
                if band not in valid_bands:
                    raise ValueError("Invalid band '%s' used in bands argument!" % band)

            # Check for Both being used independently
            if len(bands) > 1 and "Both" in bands:
                raise ValueError("'Both' test type must be used independently!")

            # validate_args(args)
            if duration.endswith('s') or duration.endswith('S'):
                duration = int(duration[0:-1])
            elif duration.endswith('m') or duration.endswith('M'):
                duration = int(duration[0:-1]) * 60
            elif duration.endswith('h') or duration.endswith('H'):
                duration = int(duration[0:-1]) * 60 * 60
            elif duration.endswith(''):
                duration = int(duration)

            list6G, list6G_bytes, list6G_speed, list6G_urltimes = [], [], [], []
            list5G, list5G_bytes, list5G_speed, list5G_urltimes = [], [], [], []
            list2G, list2G_bytes, list2G_speed, list2G_urltimes = [], [], [], []
            Both, Both_bytes, Both_speed, Both_urltimes = [], [], [], []
            listReal, listReal_bytes, listReal_speed, listReal_urltimes = [], [], [], []  # For real devices (not band specific)
            dict_keys = []
            dict_keys.extend(bands)
            # print(dict_keys)
            final_dict = dict.fromkeys(dict_keys)
            # print(final_dict)
            dict1_keys = ['dl_time', 'min', 'max', 'avg', 'bytes_rd', 'speed', 'url_times']
            for i in final_dict:
                final_dict[i] = dict.fromkeys(dict1_keys)
            print(final_dict)
            min6 = []
            min5 = []
            min2 = []
            min_both = []
            max6 = []
            max5 = []
            max2 = []
            max_both = []
            avg6 = []
            avg2 = []
            avg5 = []
            avg_both = []
            port_list, dev_list, macid_list = [], [], []
            for band in bands:
                # For real devices while ensuring no blocker for Virtual devices
                if client_type == 'Real':
                    ssid = ssid
                    passwd = passwd
                    security = security
                elif band == "2.4G":
                    security = [twog_security]
                    ssid = [twog_ssid]
                    passwd = [twog_passwd]
                elif band == "5G":
                    security = [fiveg_security]
                    ssid = [fiveg_ssid]
                    passwd = [fiveg_passwd]
                elif band == "6G":
                    security = [sixg_security]
                    ssid = [sixg_ssid]
                    passwd = [sixg_passwd]
                elif band == "Both":
                    security = [twog_security, fiveg_security]
                    ssid = [twog_ssid, fiveg_ssid]
                    passwd = [twog_passwd, fiveg_passwd]
                ce = self.current_exec #seires
                if ce == "parallel":
                    obj_name = "http_test"
                else:
                    obj_no = 1
                    while f"http_test_{obj_no}" in self.http_obj_dict[ce]:
                        obj_no+=1 
                    obj_name = f"http_test_{obj_no}" 
                self.http_obj_dict[ce][obj_name] = {"obj":None,"data":None}
                
                self.http_obj_dict[ce][obj_name]["obj"] = http_test.HttpDownload(lfclient_host=self.lanforge_ip, lfclient_port=self.port,
                                    upstream=upstream_port, num_sta=num_stations,
                                    security=security, ap_name=ap_name,
                                    ssid=ssid, password=passwd,
                                    target_per_ten=target_per_ten,
                                    file_size=file_size, bands=band,
                                    twog_radio=twog_radio,
                                    fiveg_radio=fiveg_radio,
                                    sixg_radio=sixg_radio,
                                    client_type=client_type,
                                    lf_username=lf_username, lf_password=lf_password,
                                    result_dir=result_dir,  # FOR WEBGUI
                                    dowebgui=dowebgui,  # FOR WEBGUI
                                    device_list=device_list,
                                    test_name=test_name,  # FOR WEBGUI
                                    get_url_from_file=get_url_from_file,
                                    file_path=file_path,
                                    file_name=file_name,
                                    group_name=group_name,
                                    profile_name=profile_name,
                                    eap_method=eap_method,
                                    eap_identity=eap_identity,
                                    ieee80211=ieee8021x,
                                    ieee80211u=ieee80211u,
                                    ieee80211w=ieee80211w,
                                    enable_pkc=enable_pkc,
                                    bss_transition=bss_transition,
                                    power_save=power_save,
                                    disable_ofdma=disable_ofdma,
                                    roam_ft_ds=roam_ft_ds,
                                    key_management=key_management,
                                    pairwise=pairwise,
                                    private_key=private_key,
                                    ca_cert=ca_cert,
                                    client_cert=client_cert,
                                    pk_passwd=pk_passwd,
                                    pac_file=pac_file,
                                    expected_passfail_value=expected_passfail_value,
                                    device_csv_name=device_csv_name,
                                    wait_time=wait_time,
                                    config=config,
                                    get_live_view= get_live_view,
                                    total_floors = total_floors
                                    )
                if client_type == "Real":
                    if not isinstance(device_list, list):
                        self.http_obj_dict[ce][obj_name]["obj"].device_list = self.http_obj_dict[ce][obj_name]["obj"].filter_iOS_devices(device_list)
                        if len(self.http_obj_dict[ce][obj_name]["obj"].device_list) == 0:
                            logger.info("There are no devices available")
                            return False
                    port_list, dev_list, macid_list, configuration = self.http_obj_dict[ce][obj_name]["obj"].get_real_client_list()
                    if dowebgui and group_name:
                        if len(dev_list) == 0:
                            logger.info("No device is available to run the test")
                            obj = {
                                "status": "Stopped",
                                "configuration_status": "configured"
                            }
                            self.http_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj)
                            return
                        else:
                            obj = {
                                "configured_devices": dev_list,
                                "configuration_status": "configured"
                            }
                            self.http_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj)
                    num_stations = len(port_list)
                if not get_url_from_file:
                    self.http_obj_dict[ce][obj_name]["obj"].file_create(ssh_port=ssh_port)
                else:
                    if file_path is None:
                        print("WARNING: Please Specify the path of the file, if you select the --get_url_from_file")
                        return False
                self.http_obj_dict[ce][obj_name]["obj"].set_values()
                self.http_obj_dict[ce][obj_name]["obj"].precleanup()
                self.http_obj_dict[ce][obj_name]["obj"].build()
                if client_type == 'Real':
                    self.http_obj_dict[ce][obj_name]["obj"].monitor_cx()
                    logger.info(f'Test started on the devices : {self.http_obj_dict[ce][obj_name]["obj"].port_list}')
                test_time = datetime.datetime.now()
                # Solution For Leap Year conflict changed it to %Y
                test_time = test_time.strftime("%Y %d %H:%M:%S")
                print("Test started at ", test_time)
                self.http_obj_dict[ce][obj_name]["obj"].start()
                if dowebgui:
                    # FOR WEBGUI, -This fumction is called to fetch the runtime data from layer-4
                    self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(duration)
                elif client_type == 'Real':
                    # To fetch runtime csv during runtime
                    self.http_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(duration)
                else:
                    time.sleep(duration)
                self.http_obj_dict[ce][obj_name]["obj"].stop()
                # taking self.http_obj_dict[ce][obj_name]["obj"].data, which got updated in the monitor_for_runtime_csv method
                if client_type == 'Real':
                    uc_avg_val = self.http_obj_dict[ce][obj_name]["obj"].data['uc_avg']
                    url_times = self.http_obj_dict[ce][obj_name]["obj"].data['url_data']
                    rx_bytes_val = self.http_obj_dict[ce][obj_name]["obj"].data['bytes_rd']
                    print('rx_rate_Val',self.http_obj_dict[ce][obj_name]["obj"].data['rx rate (1m)'])
                    rx_rate_val = list(self.http_obj_dict[ce][obj_name]["obj"].data['rx rate (1m)'])
                else:
                    uc_avg_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('uc-avg')
                    url_times = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('total-urls')
                    rx_bytes_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('bytes-rd')
                    rx_rate_val = self.http_obj_dict[ce][obj_name]["obj"].my_monitor('rx rate')
                if dowebgui:
                    self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["url_data"] = url_times  # storing the layer-4 url data at the end of test
                if client_type == 'Real':  # for real clients
                    listReal.extend(uc_avg_val)
                    listReal_bytes.extend(rx_bytes_val)
                    listReal_speed.extend(rx_rate_val)
                    listReal_urltimes.extend(url_times)
                    logger.info("%s %s %s", listReal, listReal_bytes, listReal_speed)
                    final_dict[band]['dl_time'] = listReal
                    min2.append(min(listReal))
                    final_dict[band]['min'] = min2
                    max2.append(max(listReal))
                    final_dict[band]['max'] = max2
                    avg2.append((sum(listReal) / num_stations))
                    final_dict[band]['avg'] = avg2
                    final_dict[band]['bytes_rd'] = listReal_bytes
                    final_dict[band]['speed'] = listReal_speed
                    final_dict[band]['url_times'] = listReal_urltimes
                else:
                    if band == "5G":
                        list5G.extend(uc_avg_val)
                        list5G_bytes.extend(rx_bytes_val)
                        list5G_speed.extend(rx_rate_val)
                        list5G_urltimes.extend(url_times)
                        logger.info("%s %s %s %s", list5G, list5G_bytes, list5G_speed, list5G_urltimes)
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
                    elif band == "6G":
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
                    elif band == "2.4G":
                        list2G.extend(uc_avg_val)
                        list2G_bytes.extend(rx_bytes_val)
                        list2G_speed.extend(rx_rate_val)
                        list2G_urltimes.extend(url_times)
                        logger.info("%s %s %s", list2G, list2G_bytes, list2G_speed)
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
            print("result", result_data)
            print("Test Finished")
            test_end = datetime.datetime.now()
            test_end = test_end.strftime("%Y %d %H:%M:%S")
            print("Test ended at ", test_end)
            s1 = test_time
            s2 = test_end  # for example
            FMT = '%Y %d %H:%M:%S'
            test_duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)

            info_ssid = []
            info_security = []
            # For real clients
            if client_type == 'Real':
                info_ssid.append(ssid)
                info_security.append(security)
            else:
                for band in bands:
                    if band == "2.4G":
                        info_ssid.append(twog_ssid)
                        info_security.append(twog_security)
                    elif band == "5G":
                        info_ssid.append(fiveg_ssid)
                        info_security.append(fiveg_security)
                    elif band == "6G":
                        info_ssid.append(sixg_ssid)
                        info_security.append(sixg_security)
                    elif band == "Both":
                        info_ssid.append(fiveg_ssid)
                        info_security.append(fiveg_security)
                        info_ssid.append(twog_ssid)
                        info_security.append(twog_security)

            print("total test duration ", test_duration)
            date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            duration = duration
            if int(duration) < 60:
                duration = str(duration) + "s"
            elif int(duration == 60) or (int(duration) > 60 and int(duration) < 3600):
                duration = str(duration / 60) + "m"
            else:
                if int(duration == 3600) or (int(duration) > 3600):
                    duration = str(duration / 3600) + "h"

            android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
            all_devices_names = []
            device_type = []
            total_devices = ""
            for i in self.http_obj_dict[ce][obj_name]["obj"].devices_list:
                split_device_name = i.split(" ")
                if 'android' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Android)"))
                    device_type.append("Android")
                    android_devices += 1
                elif 'Win' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                    device_type.append("Windows")
                    windows_devices += 1
                elif 'Lin' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                    device_type.append("Linux")
                    linux_devices += 1
                elif 'Mac' in split_device_name:
                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                    device_type.append("Mac")
                    mac_devices += 1

            # Build total_devices string based on counts
            if android_devices > 0:
                total_devices += f" Android({android_devices})"
            if windows_devices > 0:
                total_devices += f" Windows({windows_devices})"
            if linux_devices > 0:
                total_devices += f" Linux({linux_devices})"
            if mac_devices > 0:
                total_devices += f" Mac({mac_devices})"
            if client_type == "Real":
                if group_name:
                    group_names = ', '.join(configuration.keys())
                    profile_names = ', '.join(configuration.values())
                    configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                    test_setup_info = {
                        "AP name": ap_name,
                        "Configuration": configmap,
                        "Configured Devices": ", ".join(all_devices_names),
                        "No of Devices": "Total" + f"({len(all_devices_names)})" + total_devices,
                        "Traffic Direction": "Download",
                        "Traffic Duration ": duration
                    }
                else:
                    test_setup_info = {
                        "AP Name": ap_name,
                        "SSID": ssid,
                        "Device List": ", ".join(all_devices_names),
                        "Security": security,
                        "No of Devices": "Total" + f"({len(all_devices_names)})" + total_devices,
                        "Traffic Direction": "Download",
                        "Traffic Duration ": duration
                    }
            else:
                test_setup_info = {
                    "AP Name": ap_name,
                    "SSID": ssid,
                    "Security": security,
                    "No of Devices": num_stations,
                    "Traffic Direction": "Download",
                    "Traffic Duration ": duration
                }
            test_input_infor = {
                "LANforge ip": self.lanforge_ip,
                "Bands": bands,
                "Upstream": upstream_port,
                "Stations": num_stations,
                "SSID": ','.join(filter(None, info_ssid)) if info_ssid else "",
                "Security": ', '.join(filter(None, info_security)) if info_security else "",
                "Duration": duration,
                "Contact": "support@candelatech.com"
            }
            if not file_path:
                test_setup_info["File size"] = file_size
                test_setup_info["File location"] = "/usr/local/lanforge/nginx/html"
                test_input_infor["File size"] = file_size
            else:
                test_setup_info["File location (URLs from the File)"] = file_path
            if client_type == "Real":
                test_setup_info["failed_cx's"] = self.http_obj_dict[ce][obj_name]["obj"].failed_cx if self.http_obj_dict[ce][obj_name]["obj"].failed_cx else "NONE"
            # dataset = self.http_obj_dict[ce][obj_name]["obj"].download_time_in_sec(result_data=result_data)
            rx_rate = []
            for i in result_data:
                dataset = result_data[i]['dl_time']
                dataset2 = result_data[i]['url_times']
                bytes_rd = result_data[i]['bytes_rd']
                rx_rate = result_data[i]['speed']
            dataset1 = [round(x / 1000000, 4) for x in bytes_rd]
            rx_rate = [round(x / 1000000, 4) for x in rx_rate]  # converting bps to mbps

            lis = []
            if band == "Both":
                for i in range(1, num_stations * 2 + 1):
                    lis.append(i)
            else:
                for i in range(1, num_stations + 1):
                    lis.append(i)

            if dowebgui:
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["status"] = ["STOPPED"] * len(self.http_obj_dict[ce][obj_name]["obj"].devices_list)
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui['rx rate (1m)'] = self.http_obj_dict[ce][obj_name]["obj"].data['rx rate (1m)']
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui['total_err'] = self.http_obj_dict[ce][obj_name]["obj"].data['total_err']
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["start_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["start_time"]
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["end_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["end_time"]
                self.http_obj_dict[ce][obj_name]["obj"].data_for_webui["remaining_time"] = self.http_obj_dict[ce][obj_name]["obj"].data["remaining_time"]
                df1 = pd.DataFrame(self.http_obj_dict[ce][obj_name]["obj"].data_for_webui)
                df1.to_csv('{}/http_datavalues.csv'.format(self.http_obj_dict[ce][obj_name]["obj"].result_dir), index=False)

            self.http_obj_dict[ce][obj_name]["obj"].generate_report(date, num_stations=num_stations,
                                duration=duration, test_setup_info=test_setup_info, dataset=dataset, lis=lis,
                                bands=bands, threshold_2g=threshold_2g, threshold_5g=threshold_5g,
                                threshold_both=threshold_both, dataset2=dataset2, dataset1=dataset1,
                                # summary_table_value=summary_table_value,
                                result_data=result_data, rx_rate=rx_rate,
                                test_rig=test_rig, test_tag=test_tag, dut_hw_version=dut_hw_version,
                                dut_sw_version=dut_sw_version, dut_model_num=dut_model_num,
                                dut_serial_num=dut_serial_num, test_id=test_id,
                                test_input_infor=test_input_infor, csv_outfile=csv_outfile,report_path=self.result_path if not self.dowebgui else self.result_dir)
            params = {
                        "date": date,
                        "num_stations": num_stations,
                        "duration": duration,
                        "test_setup_info": test_setup_info,
                        "dataset": dataset,
                        "lis": lis,
                        "bands": bands,
                        "threshold_2g": threshold_2g,
                        "threshold_5g": threshold_5g,
                        "threshold_both": threshold_both,
                        "dataset2": dataset2,
                        "dataset1": dataset1,
                        # "summary_table_value": summary_table_value,  # optional
                        "result_data": result_data,
                        "rx_rate": rx_rate,
                        "test_rig": test_rig,
                        "test_tag": test_tag,
                        "dut_hw_version": dut_hw_version,
                        "dut_sw_version": dut_sw_version,
                        "dut_model_num": dut_model_num,
                        "dut_serial_num": dut_serial_num,
                        "test_id": test_id,
                        "test_input_infor": test_input_infor,
                        "csv_outfile": csv_outfile,
                        "report_path": self.result_path
                    }
            self.http_obj_dict[ce][obj_name]["data"] = params.copy()
            if self.dowebgui:
                self.webgui_test_done("http")

            self.http_obj_dict[ce][obj_name]["obj"].postcleanup()
            if dowebgui:
                self.http_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
            return True


    def run_ftp_test(
        self,
        mgr='localhost',
        mgr_port=8080,
        upstream_port='eth1',
        ssid=None,
        passwd=None,
        security=None,
        group_name=None,
        profile_name=None,
        file_name=None,
        ap_name=None,
        traffic_duration=None,
        clients_type="Real",
        dowebgui=False,
        directions=["Download"],
        file_sizes=["2MB", "500MB", "1000MB"],
        local_lf_report_dir="",
        ap_ip=None,
        twog_radio='wiphy1',
        fiveg_radio='wiphy0',
        sixg_radio='wiphy2',
        lf_username='lanforge',
        lf_password='lanforge',
        ssh_port=22,
        bands=["5G", "2.4G", "6G", "Both"],
        num_stations=0,
        result_dir='',
        device_list=[],
        test_name=None,
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="FTP Data",
        csv_outfile="",
        eap_method="DEFAULT",
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management="DEFAULT",
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        get_live_view=False,
        total_floors="0",
        lf_logger_config_json=None,
        help_summary=False
    ):
        args = SimpleNamespace(**locals())
        args.mgr = self.lanforge_ip
        args.mgr_port = int(self.port)
        return self.run_ftp_test1(args)

    def run_ftp_test1(self,args):
        if self.dowebgui:
            if not self.webgui_stop_check("ftp"):
                return False
        # 1st time stamp for test duration
        time_stamp1 = datetime.datetime.now()
        # use for creating ftp_test dictionary
        interation_num = 0

        # empty dictionary for whole test data
        ftp_data = {}

        # validate_args(args)
        if args.traffic_duration.endswith('s') or args.traffic_duration.endswith('S'):
            args.traffic_duration = int(args.traffic_duration[0:-1])
        elif args.traffic_duration.endswith('m') or args.traffic_duration.endswith('M'):
            args.traffic_duration = int(args.traffic_duration[0:-1]) * 60
        elif args.traffic_duration.endswith('h') or args.traffic_duration.endswith('H'):
            args.traffic_duration = int(args.traffic_duration[0:-1]) * 60 * 60
        elif args.traffic_duration.endswith(''):
            args.traffic_duration = int(args.traffic_duration)
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "ftp_test"
        else:
            obj_no = 1
            while f"ftp_test_{obj_no}" in self.ftp_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"ftp_test_{obj_no}" 
        self.ftp_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        # For all combinations ftp_data of directions, file size and client counts, run the test
        for band in args.bands:
            for direction in args.directions:
                for file_size in args.file_sizes:
                    # Start Test
                    self.ftp_obj_dict[ce][obj_name]["obj"] = FtpTest(lfclient_host=args.mgr,
                                lfclient_port=args.mgr_port,
                                result_dir=args.result_dir,
                                upstream=args.upstream_port,
                                dut_ssid=args.ssid,
                                group_name=args.group_name,
                                profile_name=args.profile_name,
                                file_name=args.file_name,
                                dut_passwd=args.passwd,
                                dut_security=args.security,
                                num_sta=args.num_stations,
                                band=band,
                                ap_name=args.ap_name,
                                file_size=file_size,
                                direction=direction,
                                twog_radio=args.twog_radio,
                                fiveg_radio=args.fiveg_radio,
                                sixg_radio=args.sixg_radio,
                                lf_username=args.lf_username,
                                lf_password=args.lf_password,
                                # duration=pass_fail_duration(band, file_size),
                                traffic_duration=args.traffic_duration,
                                ssh_port=args.ssh_port,
                                clients_type=args.clients_type,
                                dowebgui=args.dowebgui,
                                device_list=args.device_list,
                                test_name=args.test_name,
                                eap_method=args.eap_method,
                                eap_identity=args.eap_identity,
                                ieee80211=args.ieee8021x,
                                ieee80211u=args.ieee80211u,
                                ieee80211w=args.ieee80211w,
                                enable_pkc=args.enable_pkc,
                                bss_transition=args.bss_transition,
                                power_save=args.power_save,
                                disable_ofdma=args.disable_ofdma,
                                roam_ft_ds=args.roam_ft_ds,
                                key_management=args.key_management,
                                pairwise=args.pairwise,
                                private_key=args.private_key,
                                ca_cert=args.ca_cert,
                                client_cert=args.client_cert,
                                pk_passwd=args.pk_passwd,
                                pac_file=args.pac_file,
                                expected_passfail_val=args.expected_passfail_value,
                                csv_name=args.device_csv_name,
                                wait_time=args.wait_time,
                                config=args.config,
                                get_live_view= args.get_live_view,
                                total_floors = args.total_floors
                                )

                    interation_num = interation_num + 1
                    self.ftp_obj_dict[ce][obj_name]["obj"].file_create()
                    if args.clients_type == "Real":
                        if not isinstance(args.device_list, list):
                            self.ftp_obj_dict[ce][obj_name]["obj"].device_list = self.ftp_obj_dict[ce][obj_name]["obj"].filter_iOS_devices(args.device_list)
                            if len(self.ftp_obj_dict[ce][obj_name]["obj"].device_list) == 0:
                                logger.info("There are no devices available")
                                return False
                        configured_device, configuration = self.ftp_obj_dict[ce][obj_name]["obj"].query_realclients()

                    if args.dowebgui and args.group_name:
                        # If no devices are configured,update the Web UI with "Stopped" status
                        if len(configured_device) == 0:
                            logger.warning("No device is available to run the test")
                            obj1 = {
                                "status": "Stopped",
                                "configuration_status": "configured"
                            }
                            self.ftp_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                            return
                        # If devices are configured, update the Web UI with the list of configured devices
                        else:
                            obj1 = {
                                "configured_devices": configured_device,
                                "configuration_status": "configured"
                            }
                            self.ftp_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                    self.ftp_obj_dict[ce][obj_name]["obj"].set_values()
                    self.ftp_obj_dict[ce][obj_name]["obj"].precleanup()
                    self.ftp_obj_dict[ce][obj_name]["obj"].build()
                    if not self.ftp_obj_dict[ce][obj_name]["obj"].passes():
                        logger.info(self.ftp_obj_dict[ce][obj_name]["obj"].get_fail_message())
                        return False

                    if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == 'Real':
                        self.ftp_obj_dict[ce][obj_name]["obj"].monitor_cx()
                        logger.info(f'Test started on the devices : {self.ftp_obj_dict[ce][obj_name]["obj"].input_devices_list}')
                    # First time stamp
                    time1 = datetime.datetime.now()
                    logger.info("Traffic started running at %s", time1)
                    self.ftp_obj_dict[ce][obj_name]["obj"].start(False, False)
                    # to fetch runtime values during the execution and fill the csv.
                    if args.dowebgui or args.clients_type == "Real":
                        self.ftp_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv()
                        self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor_for_real_devices()
                    else:
                        time.sleep(args.traffic_duration)
                        self.ftp_obj_dict[ce][obj_name]["obj"].my_monitor()
                    self.ftp_obj_dict[ce][obj_name]["obj"].stop()
                    print("Traffic stopped running")

                    self.ftp_obj_dict[ce][obj_name]["obj"].postcleanup()
                    time2 = datetime.datetime.now()
                    logger.info("Test ended at %s", time2)

        # 2nd time stamp for test duration
        time_stamp2 = datetime.datetime.now()

        # total time for test duration
        # test_duration = str(time_stamp2 - time_stamp1)[:-7]

        date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]

        # print(ftp_data)

        input_setup_info = {
            "AP IP": args.ap_ip,
            "File Size": args.file_sizes,
            "Bands": args.bands,
            "Direction": args.directions,
            "Stations": args.num_stations,
            "Upstream": args.upstream_port,
            "SSID": args.ssid,
            "Security": args.security,
            "Contact": "support@candelatech.com"
        }
        if args.dowebgui:
            self.ftp_obj_dict[ce][obj_name]["obj"].data_for_webui["status"] = ["STOPPED"] * len(self.ftp_obj_dict[ce][obj_name]["obj"].url_data)

            df1 = pd.DataFrame(self.ftp_obj_dict[ce][obj_name]["obj"].data_for_webui)
            df1.to_csv('{}/ftp_datavalues.csv'.format(self.ftp_obj_dict[ce][obj_name]["obj"].result_dir), index=False)
            # copying to home directory i.e home/user_name
            # self.ftp_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        # Report generation when groups are specified
        if args.group_name:
            self.ftp_obj_dict[ce][obj_name]["obj"].generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                                test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                                dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                                dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                                bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir, config_devices=configuration,report_path=self.result_path if not self.dowebgui else self.result_dir)
        # Generating report without group-specific device configuration
        else:
            self.ftp_obj_dict[ce][obj_name]["obj"].generate_report(ftp_data, date, input_setup_info, test_rig=args.test_rig,
                                test_tag=args.test_tag, dut_hw_version=args.dut_hw_version,
                                dut_sw_version=args.dut_sw_version, dut_model_num=args.dut_model_num,
                                dut_serial_num=args.dut_serial_num, test_id=args.test_id,
                                bands=args.bands, csv_outfile=args.csv_outfile, local_lf_report_dir=args.local_lf_report_dir,report_path=self.result_path if not self.dowebgui else self.result_dir)

        params = {
            "ftp_data": ftp_data,
            "date": date,
            "input_setup_info": input_setup_info,
            "test_rig": args.test_rig,
            "test_tag": args.test_tag,
            "dut_hw_version": args.dut_hw_version,
            "dut_sw_version": args.dut_sw_version,
            "dut_model_num": args.dut_model_num,
            "dut_serial_num": args.dut_serial_num,
            "test_id": args.test_id,
            "bands": args.bands,
            "csv_outfile": args.csv_outfile,
            "local_lf_report_dir": args.local_lf_report_dir,
            "report_path": self.result_path
        }

        if args.group_name:
            params["config_devices"] = configuration
        self.ftp_obj_dict[ce][obj_name]["data"] = params.copy()

        # if args.group_name:
        #     config_devices = configuration
        # else:
        #     config_devices = ""

        # ftp_data = ftp_data
        # date = date
        # input_setup_info = input_setup_info
        # test_rig = args.test_rig
        # test_tag = args.test_tag
        # dut_hw_version = args.dut_hw_version
        # dut_sw_version = args.dut_sw_version
        # dut_model_num = args.dut_model_num
        # dut_serial_num = args.dut_serial_num
        # test_id = args.test_id
        # bands = args.bands
        # csv_outfile = args.csv_outfile
        # local_lf_report_dir = args.local_lf_report_dir
        # report_path = self.result_path

        # no_of_stations = ""
        # duration = ""
        # x_fig_size = 18
        # y_fig_size = len(obj.real_client_list1) * .5 + 4

        # if int(obj.traffic_duration) < 60:
        #     duration = str(obj.traffic_duration) + "s"
        # elif int(obj.traffic_duration == 60) or (int(obj.traffic_duration) > 60 and int(obj.traffic_duration) < 3600):
        #     duration = str(obj.traffic_duration / 60) + "m"
        # else:
        #     if int(obj.traffic_duration == 3600) or (int(obj.traffic_duration) > 3600):
        #         duration = str(obj.traffic_duration / 3600) + "h"

        # client_list = []
        # if obj.clients_type == "Real":
        #     client_list = obj.real_client_list1
        #     android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
        #     all_devices_names = []
        #     device_type = []
        #     total_devices = ""
        #     for i in obj.real_client_list:
        #         split_device_name = i.split(" ")
        #         if 'android' in split_device_name:
        #             all_devices_names.append(split_device_name[2] + ("(Android)"))
        #             device_type.append("Android")
        #             android_devices += 1
        #         elif 'Win' in split_device_name:
        #             all_devices_names.append(split_device_name[2] + ("(Windows)"))
        #             device_type.append("Windows")
        #             windows_devices += 1
        #         elif 'Lin' in split_device_name:
        #             all_devices_names.append(split_device_name[2] + ("(Linux)"))
        #             device_type.append("Linux")
        #             linux_devices += 1
        #         elif 'Mac' in split_device_name:
        #             all_devices_names.append(split_device_name[2] + ("(Mac)"))
        #             device_type.append("Mac")
        #             mac_devices += 1

        #     if android_devices > 0:
        #         total_devices += f" Android({android_devices})"
        #     if windows_devices > 0:
        #         total_devices += f" Windows({windows_devices})"
        #     if linux_devices > 0:
        #         total_devices += f" Linux({linux_devices})"
        #     if mac_devices > 0:
        #         total_devices += f" Mac({mac_devices})"
        # else:
        #     if obj.clients_type == "Virtual":
        #         client_list = obj.station_list
        # if 'ftp_test' not in self.test_count_dict:
        #     self.test_count_dict['ftp_test']=0
        # self.test_count_dict['ftp_test']+=1
        # self.overall_report.set_obj_html(_obj_title=f'FTP Test ', _obj="")
        # self.overall_report.build_objective()
        # self.overall_report.set_table_title("Test Setup Information")
        # self.overall_report.build_table_title()

        # if obj.clients_type == "Virtual":
        #     no_of_stations = str(len(obj.station_list))
        # else:
        #     no_of_stations = str(len(obj.input_devices_list))

        # if obj.clients_type == "Real":
        #     if config_devices == "":
        #         test_setup_info = {
        #             "AP Name": obj.ap_name,
        #             "SSID": obj.ssid,
        #             "Security": obj.security,
        #             "Device List": ", ".join(all_devices_names),
        #             "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
        #             "Failed CXs": obj.failed_cx if obj.failed_cx else "NONE",
        #             "File size": obj.file_size,
        #             "File location": "/home/lanforge",
        #             "Traffic Direction": obj.direction,
        #             "Traffic Duration ": duration
        #         }
        #     else:
        #         group_names = ', '.join(config_devices.keys())
        #         profile_names = ', '.join(config_devices.values())
        #         configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
        #         test_setup_info = {
        #             "AP Name": obj.ap_name,
        #             'Configuration': configmap,
        #             "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
        #             "File size": obj.file_size,
        #             "File location": "/home/lanforge",
        #             "Traffic Direction": obj.direction,
        #             "Traffic Duration ": duration
        #         }
        # else:
        #     test_setup_info = {
        #         "AP Name": obj.ap_name,
        #         "SSID": obj.ssid,
        #         "Security": obj.security,
        #         "No of Devices": no_of_stations,
        #         "File size": obj.file_size,
        #         "File location": "/home/lanforge",
        #         "Traffic Direction": obj.direction,
        #         "Traffic Duration ": duration
        #     }

        # self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        # self.overall_report.set_obj_html(
        #     _obj_title=f"No of times file {obj.direction}",
        #     _obj=f"The below graph represents number of times a file {obj.direction} for each client"
        #     f"(WiFi) traffic.  X- axis shows “No of times file {obj.direction}” and Y-axis shows "
        #     f"Client names.")

        # self.overall_report.build_objective()
        # graph = lf_bar_graph_horizontal(_data_set=[obj.url_data], _xaxis_name=f"No of times file {obj.direction}",
        #                                 _yaxis_name="Client names",
        #                                 _yaxis_categories=[i for i in client_list],
        #                                 _yaxis_label=[i for i in client_list],
        #                                 _yaxis_step=1,
        #                                 _yticks_font=8,
        #                                 _yticks_rotation=None,
        #                                 _graph_title=f"No of times file {obj.direction} (Count)",
        #                                 _title_size=16,
        #                                 _figsize=(x_fig_size, y_fig_size),
        #                                 _legend_loc="best",
        #                                 _legend_box=(1.0, 1.0),
        #                                 _color_name=['orange'],
        #                                 _show_bar_value=True,
        #                                 _enable_csv=True,
        #                                 _graph_image_name="Total-url_ftp", _color_edge=['black'],
        #                                 _color=['orange'],
        #                                 _label=[obj.direction])
        # graph_png = graph.build_bar_graph_horizontal()
        # print("graph name {}".format(graph_png))
        # self.overall_report.set_graph_image(graph_png)
        # # need to move the graph image to the results
        # self.overall_report.move_graph_image()
        # self.overall_report.set_csv_filename(graph_png)
        # self.overall_report.move_csv_file()
        # self.overall_report.build_graph()
        # self.overall_report.set_obj_html(
        #     _obj_title=f"Average time taken to {obj.direction} file ",
        #     _obj=f"The below graph represents average time taken to {obj.direction} for each client  "
        #     f"(WiFi) traffic.  X- axis shows “Average time taken to {obj.direction} a file ” and Y-axis shows "
        #     f"Client names.")

        # self.overall_report.build_objective()
        # graph = lf_bar_graph_horizontal(_data_set=[obj.uc_avg], _xaxis_name=f"Average time taken to {obj.direction} file in ms",
        #                                 _yaxis_name="Client names",
        #                                 _yaxis_categories=[i for i in client_list],
        #                                 _yaxis_label=[i for i in client_list],
        #                                 _yaxis_step=1,
        #                                 _yticks_font=8,
        #                                 _yticks_rotation=None,
        #                                 _graph_title=f"Average time taken to {obj.direction} file",
        #                                 _title_size=16,
        #                                 _figsize=(x_fig_size, y_fig_size),
        #                                 _legend_loc="best",
        #                                 _legend_box=(1.0, 1.0),
        #                                 _color_name=['steelblue'],
        #                                 _show_bar_value=True,
        #                                 _enable_csv=True,
        #                                 _graph_image_name="ucg-avg_ftp", _color_edge=['black'],
        #                                 _color=['steelblue'],
        #                                 _label=[obj.direction])
        # graph_png = graph.build_bar_graph_horizontal()
        # print("graph name {}".format(graph_png))
        # self.overall_report.set_graph_image(graph_png)
        # self.overall_report.move_graph_image()
        # # need to move the graph image to the results
        # self.overall_report.set_csv_filename(graph_png)
        # self.overall_report.move_csv_file()
        # self.overall_report.build_graph()
        # if(obj.dowebgui and obj.get_live_view):
        #     for floor in range(0,int(obj.total_floors)):
        #         script_dir = os.path.dirname(os.path.abspath(__file__))
        #         throughput_image_path = os.path.join(script_dir, "heatmap_images", f"ftp_{obj.test_name}_{floor+1}.png")
        #         # rssi_image_path = os.path.join(script_dir, "heatmap_images", f"{self.test_name}_rssi_{floor+1}.png")
        #         timeout = 60  # seconds
        #         start_time = time.time()

        #         while not (os.path.exists(throughput_image_path)):
        #             if time.time() - start_time > timeout:
        #                 print("Timeout: Images not found within 60 seconds.")
        #                 break
        #             time.sleep(1)
        #         while not os.path.exists(throughput_image_path):
        #             if os.path.exists(throughput_image_path):
        #                 break
        #             # time.sleep(10)
        #         if os.path.exists(throughput_image_path):
        #             self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
        #             self.overall_report.build_custom()
        #             # self.overall_report.set_custom_html("<h2>Average Throughput Heatmap: </h2>")
        #             # self.overall_report.build_custom()
        #             self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
        #             self.overall_report.build_custom()
        #             # os.remove(throughput_image_path)
        # self.overall_report.set_obj_html("File Download Time (sec)", "The below table will provide information of "
        #                          "minimum, maximum and the average time taken by clients to download a file in seconds")
        # self.overall_report.build_objective()
        # dataframe2 = {
        #     "Minimum": [str(round(min(obj.uc_min) / 1000, 1))],
        #     "Maximum": [str(round(max(obj.uc_max) / 1000, 1))],
        #     "Average": [str(round((sum(obj.uc_avg) / len(client_list)) / 1000, 1))]
        # }
        # dataframe3 = pd.DataFrame(dataframe2)
        # self.overall_report.set_table_dataframe(dataframe3)
        # self.overall_report.build_table()
        # self.overall_report.set_table_title("Overall Results")
        # self.overall_report.build_table_title()
        # if obj.clients_type == 'Real':
        #     # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
        #     if obj.expected_passfail_val or obj.csv_name:
        #         obj.get_pass_fail_list(client_list)
        #     # When groups are provided a seperate table will be generated for each group using generate_dataframe
        #     if obj.group_name:
        #         for key, val in obj.group_device_map.items():
        #             if obj.expected_passfail_val or obj.csv_name:
        #                 dataframe = obj.generate_dataframe(val, client_list, obj.mac_id_list, obj.channel_list, obj.ssid_list, obj.mode_list,
        #                                                     obj.url_data, obj.test_input_list, obj.uc_avg, obj.bytes_rd, obj.rx_rate, obj.pass_fail_list)
        #             else:
        #                 dataframe = obj.generate_dataframe(val, client_list, obj.mac_id_list, obj.channel_list, obj.ssid_list,
        #                                                     obj.mode_list, obj.url_data, [], obj.uc_avg, obj.bytes_rd, obj.rx_rate, [])

        #             if dataframe:
        #                 self.overall_report.set_obj_html("", "Group: {}".format(key))
        #                 self.overall_report.build_objective()
        #                 dataframe1 = pd.DataFrame(dataframe)
        #                 self.overall_report.set_table_dataframe(dataframe1)
        #                 self.overall_report.build_table()
        #     else:
        #         dataframe = {
        #             " Clients": client_list,
        #             " MAC ": obj.mac_id_list,
        #             " Channel": obj.channel_list,
        #             " SSID ": obj.ssid_list,
        #             " Mode": obj.mode_list,
        #             " No of times File downloaded ": obj.url_data,
        #             " Time Taken to Download file (ms)": obj.uc_avg,
        #             " Bytes-rd (Mega Bytes)": obj.bytes_rd,
        #             " RX RATE (Mbps) ": obj.rx_rate,
        #             "Failed Urls": obj.total_err
        #         }
        #         if obj.expected_passfail_val or obj.csv_name:
        #             dataframe[" Expected output "] = obj.test_input_list
        #             dataframe[" Status "] = obj.pass_fail_list

        #         dataframe1 = pd.DataFrame(dataframe)
        #         self.overall_report.set_table_dataframe(dataframe1)
        #         self.overall_report.build_table()

        # else:
        #     dataframe = {
        #         " Clients": client_list,
        #         " MAC ": obj.mac_id_list,
        #         " Channel": obj.channel_list,
        #         " SSID ": obj.ssid_list,
        #         " Mode": obj.mode_list,
        #         " No of times File downloaded ": obj.url_data,
        #         " Time Taken to Download file (ms)": obj.uc_avg,
        #         " Bytes-rd (Mega Bytes)": obj.bytes_rd,
        #     }
        #     dataframe1 = pd.DataFrame(dataframe)
        #     self.overall_report.set_table_dataframe(dataframe1)
        #     self.overall_report.build_table()
        # # self.overall_report.build_footer()
        # # html_file = self.overall_report.write_html()
        # # logger.info("returned file {}".format(html_file))
        # # logger.info(html_file)
        # # self.overall_report.write_pdf()

        # if csv_outfile is not None:
        #     current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        #     csv_outfile = "{}_{}-test_l4_ftp.csv".format(
        #         csv_outfile, current_time)
        #     csv_outfile = self.overall_report.file_add_path(csv_outfile)
        #     logger.info("csv output file : {}".format(csv_outfile))




        # if args.dowebgui:
        #     obj.copy_reports_to_home_dir()
        if self.dowebgui:
            self.webgui_test_done("ftp")
        return True

        
    def run_qos_test(
        self,
        device_list=None,
        test_name=None,
        result_dir='',
        upstream_port='eth1',
        security="open",
        ssid=None,
        passwd='[BLANK]',
        traffic_type=None,
        upload=None,
        download=None,
        test_duration="2m",
        ap_name="Test-AP",
        tos=None,
        dowebgui=False,
        debug=False,
        help_summary=False,
        group_name=None,
        profile_name=None,
        file_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        expected_passfail_value=None,
        device_csv_name=None,
        wait_time=60,
        config=False,
        get_live_view=False,
        total_floors="0"
    ):
        if self.dowebgui:
            if not self.webgui_stop_check("qos"):
                return False
        test_results = {'test_results': []}
        loads = {}
        data = {}
        if download and upload:
            loads = {'upload': str(upload).split(","), 'download': str(download).split(",")}
            loads_data = loads["download"]
        elif download:
            loads = {'upload': [], 'download': str(download).split(",")}
            for i in range(len(download)):
                loads['upload'].append(0)
            loads_data = loads["download"]
        else:
            if upload:
                loads = {'upload': str(upload).split(","), 'download': []}
                for i in range(len(upload)):
                    loads['download'].append(0)
                loads_data = loads["upload"]
        if download and upload:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_BiDi'
        elif upload:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_UL'
        else:
            direction = 'L3_' + traffic_type.split('_')[1].upper() + '_DL'

        # validate_args(args)
        if test_duration.endswith('s') or test_duration.endswith('S'):
            test_duration = int(test_duration[0:-1])
        elif test_duration.endswith('m') or test_duration.endswith('M'):
            test_duration = int(test_duration[0:-1]) * 60
        elif test_duration.endswith('h') or test_duration.endswith('H'):
            test_duration = int(test_duration[0:-1]) * 60 * 60
        elif test_duration.endswith(''):
            test_duration = int(test_duration)
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "qos_test"
        else:
            obj_no = 1
            while f"qos_test_{obj_no}" in self.qos_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"qos_test_{obj_no}" 
        self.qos_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        for index in range(len(loads_data)):
            self.qos_obj_dict[ce][obj_name]["obj"] = qos_test.ThroughputQOS(host=self.lanforge_ip,
                                            ip=self.lanforge_ip,
                                            port=self.port,
                                            number_template="0000",
                                            ap_name=ap_name,
                                            name_prefix="TOS-",
                                            upstream=upstream_port,
                                            ssid=ssid,
                                            password=passwd,
                                            security=security,
                                            test_duration=test_duration,
                                            use_ht160=False,
                                            side_a_min_rate=int(loads['upload'][index]),
                                            side_b_min_rate=int(loads['download'][index]),
                                            traffic_type=traffic_type,
                                            tos=tos,
                                            csv_direction=direction,
                                            dowebgui=dowebgui,
                                            test_name=test_name,
                                            result_dir=result_dir,
                                            device_list=device_list,
                                            _debug_on=debug,
                                            group_name=group_name,
                                            profile_name=profile_name,
                                            file_name=file_name,
                                            eap_method=eap_method,
                                            eap_identity=eap_identity,
                                            ieee80211=ieee8021x,
                                            ieee80211u=ieee80211u,
                                            ieee80211w=ieee80211w,
                                            enable_pkc=enable_pkc,
                                            bss_transition=bss_transition,
                                            power_save=power_save,
                                            disable_ofdma=disable_ofdma,
                                            roam_ft_ds=roam_ft_ds,
                                            key_management=key_management,
                                            pairwise=pairwise,
                                            private_key=private_key,
                                            ca_cert=ca_cert,
                                            client_cert=client_cert,
                                            pk_passwd=pk_passwd,
                                            pac_file=pac_file,
                                            expected_passfail_val=expected_passfail_value,
                                            csv_name=device_csv_name,
                                            wait_time=wait_time,
                                            config=config,
                                            get_live_view=get_live_view,
                                            total_floors=total_floors
                                            )
            self.qos_obj_dict[ce][obj_name]["obj"].os_type()
            _, configured_device, _, configuration = self.qos_obj_dict[ce][obj_name]["obj"].phantom_check()
            if dowebgui and group_name:
                if len(configured_device) == 0:
                    logger.warning("No device is available to run the test")
                    obj1 = {
                        "status": "Stopped",
                        "configuration_status": "configured"
                    }
                    self.qos_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
                    return
                else:
                    obj1 = {
                        "configured_devices": configured_device,
                        "configuration_status": "configured"
                    }
                    self.qos_obj_dict[ce][obj_name]["obj"].updating_webui_runningjson(obj1)
            # checking if we have atleast one device available for running test
            if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui == "True":
                if self.qos_obj_dict[ce][obj_name]["obj"].device_found is False:
                    logger.warning("No Device is available to run the test hence aborting the test")
                    df1 = pd.DataFrame([{
                        "BE_dl": 0,
                        "BE_ul": 0,
                        "BK_dl": 0,
                        "BK_ul": 0,
                        "VI_dl": 0,
                        "VI_ul": 0,
                        "VO_dl": 0,
                        "VO_ul": 0,
                        "timestamp": datetime.datetime.now().strftime('%H:%M:%S'),
                        'status': 'Stopped'
                    }]
                    )
                    df1.to_csv('{}/overall_throughput.csv'.format(self.qos_obj_dict[ce][obj_name]["obj"].result_dir), index=False)
                    raise ValueError("Aborting the test....")
            self.qos_obj_dict[ce][obj_name]["obj"].build()
            self.qos_obj_dict[ce][obj_name]["obj"].monitor_cx()
            self.qos_obj_dict[ce][obj_name]["obj"].start(False, False)
            time.sleep(10)
            connections_download, connections_upload, drop_a_per, drop_b_per, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b = self.qos_obj_dict[ce][obj_name]["obj"].monitor()
            logger.info("connections download {}".format(connections_download))
            logger.info("connections upload {}".format(connections_upload))
            self.qos_obj_dict[ce][obj_name]["obj"].stop()
            time.sleep(5)
            test_results['test_results'].append(self.qos_obj_dict[ce][obj_name]["obj"].evaluate_qos(connections_download, connections_upload, drop_a_per, drop_b_per))
            data.update(test_results)
        test_end_time = datetime.datetime.now().strftime("%Y %d %H:%M:%S")
        print("Test ended at: ", test_end_time)

        input_setup_info = {
            "contact": "support@candelatech.com"
        }
        self.qos_obj_dict[ce][obj_name]["obj"].cleanup()

        # Update webgui running json with latest entry and test status completed
        if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui == "True":
            last_entry = self.qos_obj_dict[ce][obj_name]["obj"].overall[len(self.qos_obj_dict[ce][obj_name]["obj"].overall) - 1]
            last_entry["status"] = "Stopped"
            last_entry["timestamp"] = datetime.datetime.now().strftime("%d/%m %I:%M:%S %p")
            last_entry["remaining_time"] = "0"
            last_entry["end_time"] = last_entry["timestamp"]
            self.qos_obj_dict[ce][obj_name]["obj"].df_for_webui.append(
                last_entry
            )
            df1 = pd.DataFrame(self.qos_obj_dict[ce][obj_name]["obj"].df_for_webui)
            df1.to_csv('{}/overall_throughput.csv'.format(result_dir, ), index=False)

            # copying to home directory i.e home/user_name
            self.qos_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        if group_name:
            self.qos_obj_dict[ce][obj_name]["obj"].generate_report(
                data=data,
                input_setup_info=input_setup_info,
                report_path=self.qos_obj_dict[ce][obj_name]["obj"].result_dir if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path,
                connections_upload_avg=connections_upload_avg,
                connections_download_avg=connections_download_avg,
                avg_drop_a=avg_drop_a,
                avg_drop_b=avg_drop_b, config_devices=configuration)
        else:
            self.qos_obj_dict[ce][obj_name]["obj"].generate_report(
                data=data,
                input_setup_info=input_setup_info,
                report_path=self.qos_obj_dict[ce][obj_name]["obj"].result_dir if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path,
                connections_upload_avg=connections_upload_avg,
                connections_download_avg=connections_download_avg,
                avg_drop_a=avg_drop_a,
                avg_drop_b=avg_drop_b)
        params = {
            "data": None,
            "input_setup_info": None,
            "connections_download_avg": None,
            "connections_upload_avg": None,
            "avg_drop_a": None,
            "avg_drop_b": None,
            "report_path": "",
            "result_dir_name": "Qos_Test_report",
            "selected_real_clients_names": None,
            "config_devices": ""
        }

        params.update({
            "data": data,
            "input_setup_info": input_setup_info,
            "report_path": (
                self.qos_obj_dict[ce][obj_name]["obj"].result_dir
                if self.qos_obj_dict[ce][obj_name]["obj"].dowebgui else self.result_path
            ),
            "connections_upload_avg": connections_upload_avg,
            "connections_download_avg": connections_download_avg,
            "avg_drop_a": avg_drop_a,
            "avg_drop_b": avg_drop_b
        })

        if group_name:
            params["config_devices"] = configuration
        self.qos_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("qos")
        return True

    def run_vs_test(self,args):
        if self.dowebgui:
            if not self.webgui_stop_check("vs"):
                return False
        media_source_dict = {
            'dash': '1',
            'smooth_streaming': '2',
            'hls': '3',
            'progressive': '4',
            'rtsp': '5'
        }
        media_quality_dict = {
            '4k': '0',
            '8k': '1',
            '1080p': '2',
            '720p': '3',
            '360p': '4'
        }

        if args.file_name:
            args.file_name = args.file_name.removesuffix('.csv')

        media_source, media_quality = args.media_source.capitalize(), args.media_quality
        args.media_source = args.media_source.lower()
        args.media_quality = args.media_quality.lower()

        if any(char.isalpha() for char in args.media_source):
            args.media_source = media_source_dict[args.media_source]

        if any(char.isalpha() for char in args.media_quality):
            args.media_quality = media_quality_dict[args.media_quality]

        logger_config = lf_logger_config.lf_logger_config()

        if args.log_level:
            logger_config.set_level(level=args.log_level)

        if args.lf_logger_config_json:
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        logger = logging.getLogger(__name__)
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "vs_test"
        else:
            obj_no = 1
            while f"vs_test_{obj_no}" in self.vs_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"vs_test_{obj_no}" 
        self.vs_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        self.vs_obj_dict[ce][obj_name]["obj"] = VideoStreamingTest(host=args.host, ssid=args.ssid, passwd=args.passwd, encryp=args.encryp,
                                suporrted_release=["7.0", "10", "11", "12"], max_speed=args.max_speed,
                                url=args.url, urls_per_tenm=args.urls_per_tenm, duration=args.duration,
                                resource_ids=args.device_list, dowebgui=args.dowebgui, media_quality=args.media_quality, media_source=args.media_source,
                                result_dir=args.result_dir, test_name=args.test_name, incremental=args.incremental, postcleanup=args.postcleanup,
                                precleanup=args.precleanup,
                                pass_fail_val=args.expected_passfail_value,
                                csv_name=args.device_csv_name,
                                groups=args.group_name,
                                profiles=args.profile_name,
                                config=args.config,
                                file_name=args.file_name,
                                floors=args.floors,
                                get_live_view=args.get_live_view
                                )
        args.upstream_port = self.vs_obj_dict[ce][obj_name]["obj"].change_port_to_ip(args.upstream_port)
        self.vs_obj_dict[ce][obj_name]["obj"].validate_args()
        config_obj = DeviceConfig.DeviceConfig(lanforge_ip=args.host, file_name=args.file_name)
        # if not args.expected_passfail_value and args.device_csv_name is None:
        #     config_obj.device_csv_file(csv_name="device.csv")

        resource_ids_sm = []
        resource_set = set()
        resource_list = []
        resource_ids_generated = ""

        if args.group_name and args.file_name and args.profile_name:
            selected_groups = args.group_name.split(',')
            selected_profiles = args.profile_name.split(',')
            config_devices = {}
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]
            config_obj.initiate_group()
            asyncio.run(config_obj.connectivity(config_devices, upstream=args.upstream_port))

            adbresponse = config_obj.adb_obj.get_devices()
            resource_manager = config_obj.laptop_obj.get_devices()
            all_res = {}
            df1 = config_obj.display_groups(config_obj.groups)
            groups_list = df1.to_dict(orient='list')
            group_devices = {}
            for adb in adbresponse:
                group_devices[adb['serial']] = adb['eid']
            for res in resource_manager:
                all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
            eid_list = []
            for grp_name in groups_list.keys():
                for g_name in selected_groups:
                    if grp_name == g_name:
                        for j in groups_list[grp_name]:
                            if j in group_devices.keys():
                                eid_list.append(group_devices[j])
                            elif j in all_res.keys():
                                eid_list.append(all_res[j])
            args.device_list = ",".join(id for id in eid_list)
        else:
            # When group/profile are not provided
            config_dict = {
                'ssid': args.ssid,
                'passwd': args.passwd,
                'enc': args.encryp,
                'eap_method': args.eap_method,
                'eap_identity': args.eap_identity,
                'ieee80211': args.ieee8021x,
                'ieee80211u': args.ieee80211u,
                'ieee80211w': args.ieee80211w,
                'enable_pkc': args.enable_pkc,
                'bss_transition': args.bss_transition,
                'power_save': args.power_save,
                'disable_ofdma': args.disable_ofdma,
                'roam_ft_ds': args.roam_ft_ds,
                'key_management': args.key_management,
                'pairwise': args.pairwise,
                'private_key': args.private_key,
                'ca_cert': args.ca_cert,
                'client_cert': args.client_cert,
                'pk_passwd': args.pk_passwd,
                'pac_file': args.pac_file,
                'server_ip': args.upstream_port
            }
            if args.device_list:
                all_devices = config_obj.get_all_devices()
                if args.group_name is None and args.file_name is None and args.profile_name is None:
                    dev_list = args.device_list.split(',')
                    if args.config:
                        asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
            else:
                if args.config:
                    all_devices = config_obj.get_all_devices()
                    device_list = []
                    for device in all_devices:
                        if device["type"] != 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                        elif device["type"] == 'laptop':
                            device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                    print("Available devices:")
                    for device in device_list:
                        print(device)
                    args.device_list = input("Enter the desired resources to run the test:")
                    dev1_list = args.device_list.split(',')
                    asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))
                else:
                    self.vs_obj_dict[ce][obj_name]["obj"].android_devices = self.vs_obj_dict[ce][obj_name]["obj"].devices.get_devices(only_androids=True)
                    selected_devices, report_labels, selected_macs = self.vs_obj_dict[ce][obj_name]["obj"].devices.query_user()
                    if not selected_devices:
                        logging.info("devices donot exist..!!")
                        return

                    self.vs_obj_dict[ce][obj_name]["obj"].android_list = selected_devices
                    # Verify if all resource IDs are valid for Android devices
                    if self.vs_obj_dict[ce][obj_name]["obj"].android_list:
                        resource_ids = ",".join([item.split(".")[1] for item in self.vs_obj_dict[ce][obj_name]["obj"].android_list])

                        num_list = list(map(int, resource_ids.split(',')))

                        # Sort the list
                        num_list.sort()

                        # Join the sorted list back into a string
                        sorted_string = ','.join(map(str, num_list))

                        self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = sorted_string
                        resource_ids1 = list(map(int, sorted_string.split(',')))
                        modified_list = list(map(lambda item: int(item.split('.')[1]), self.vs_obj_dict[ce][obj_name]["obj"].android_devices))
                        if not all(x in modified_list for x in resource_ids1):
                            logging.info("Verify Resource ids, as few are invalid...!!")
                            return False
                        resource_ids_sm = self.vs_obj_dict[ce][obj_name]["obj"].resource_ids
                        resource_list = resource_ids_sm.split(',')
                        resource_set = set(resource_list)
                        resource_list_sorted = sorted(resource_set)
                        resource_ids_generated = ','.join(resource_list_sorted)
                        available_resources = list(resource_set)

        if args.dowebgui:
            resource_ids_sm = args.device_list.split(',')
            resource_set = set(resource_ids_sm)
            resource_list = sorted(resource_set)
            resource_ids_generated = ','.join(resource_list)
            resource_list_sorted = resource_list
            selected_devices, report_labels, selected_macs = self.vs_obj_dict[ce][obj_name]["obj"].devices.query_user(dowebgui=args.dowebgui, device_list=resource_ids_generated)
            self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = ",".join(id.split(".")[1] for id in args.device_list.split(","))
            available_resources = [int(num) for num in self.vs_obj_dict[ce][obj_name]["obj"].resource_ids.split(',')]
        else:
            self.vs_obj_dict[ce][obj_name]["obj"].android_devices = self.vs_obj_dict[ce][obj_name]["obj"].devices.get_devices(only_androids=True)
            if args.device_list:
                device_list = args.device_list.split(',')
                # Extract resource IDs (after the dot), remove duplicates, and sort them
                resource_ids = sorted(set(int(item.split('.')[1]) for item in device_list if '.' in item))
                resource_list_sorted = resource_ids
                self.vs_obj_dict[ce][obj_name]["obj"].resource_ids = ','.join(map(str, resource_ids))
                # Create a set of Android device IDs (e.g., "resource.123")
                android_device_ids = set(self.vs_obj_dict[ce][obj_name]["obj"].android_devices)
                android_device_short_ids = {device.split('.')[0] + '.' + device.split('.')[1] for device in android_device_ids}
                self.vs_obj_dict[ce][obj_name]["obj"].android_list = [dev for dev in android_device_short_ids if dev in device_list]
                # Log any devices in the list that are not available
                for dev in device_list:
                    if dev not in android_device_short_ids:
                        logger.info(f"{dev} device is not available")
                # Final list of available Android resource IDs
                available_resources = sorted(set(int(dev.split('.')[1]) for dev in self.vs_obj_dict[ce][obj_name]["obj"].android_list))
                logger.info(f"Available devices: {available_resources}")
        if len(available_resources) != 0:
            available_resources = self.vs_obj_dict[ce][obj_name]["obj"].filter_ios_devices(available_resources)
        if len(available_resources) == 0:
            logger.info("No devices which are selected are available in the lanforge")
            return False
        gave_incremental = False
        if args.incremental and not args.webgui_incremental:
            if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
                logging.info("The total available devices are {}".format(len(available_resources)))
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = input('Specify incremental values as 1,2,3 : ')
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = [int(x) for x in self.vs_obj_dict[ce][obj_name]["obj"].incremental.split(',')]
            else:
                logging.info("incremental Values are not needed as Android devices are not selected..")
        elif not args.incremental:
            gave_incremental = True
            self.vs_obj_dict[ce][obj_name]["obj"].incremental = [len(available_resources)]

        if args.webgui_incremental:
            incremental = [int(x) for x in args.webgui_incremental.split(',')]
            if (len(args.webgui_incremental) == 1 and incremental[0] != len(resource_list_sorted)) or (len(args.webgui_incremental) > 1):
                self.vs_obj_dict[ce][obj_name]["obj"].incremental = incremental

        if self.vs_obj_dict[ce][obj_name]["obj"].incremental and self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental[-1] > len(available_resources):
                logging.info("Exiting the program as incremental values are greater than the resource ids provided")
                return False
            elif self.vs_obj_dict[ce][obj_name]["obj"].incremental[-1] < len(available_resources) and len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) > 1:
                logging.info("Exiting the program as the last incremental value must be equal to selected devices")
                return False

        # To create cx for selected devices
        self.vs_obj_dict[ce][obj_name]["obj"].build()

        # To set media source and media quality
        time.sleep(10)

        # self.vs_obj_dict[ce][obj_name]["obj"].run
        test_time = datetime.datetime.now()
        test_time = test_time.strftime("%b %d %H:%M:%S")

        logging.info("Initiating Test...")

        individual_dataframe_columns = []

        keys = list(self.vs_obj_dict[ce][obj_name]["obj"].http_profile.created_cx.keys())

        # Extend individual_dataframe_column with dynamically generated column names
        for i in range(len(keys)):
            individual_dataframe_columns.extend([
                f'video_format_bitrate_{keys[i]}',
                f'total_wait_time_{keys[i]}',
                f'total_urls_{keys[i]}',
                f'RSSI_{keys[i]}',
                f'Link Speed_{keys[i]}',
                f'Total Buffer_{keys[i]}',
                f'Total Errors_{keys[i]}',
                f'Min_Video_Rate_{keys[i]}',
                f'Max_Video_Rate_{keys[i]}',
                f'Avg_Video_Rate_{keys[i]}',
                f'bytes_rd_{keys[i]}',
                f'rx rate_{keys[i]} bps',
                f'frame_rate_{keys[i]}',
                f'Video Quality_{keys[i]}'
            ])

        individual_dataframe_columns.extend(['overall_video_format_bitrate', 'timestamp', 'iteration', 'start_time', 'end_time', 'remaining_Time', 'status'])
        individual_df = pd.DataFrame(columns=individual_dataframe_columns)

        cx_order_list = []
        index = 0
        file_path = ""

        # Parsing test_duration
        if args.duration.endswith('s') or args.duration.endswith('S'):
            args.duration = round(int(args.duration[0:-1]) / 60, 2)

        elif args.duration.endswith('m') or args.duration.endswith('M'):
            args.duration = int(args.duration[0:-1])

        elif args.duration.endswith('h') or args.duration.endswith('H'):
            args.duration = int(args.duration[0:-1]) * 60

        elif args.duration.endswith(''):
            args.duration = int(args.duration)

        incremental_capacity_list_values = self.vs_obj_dict[ce][obj_name]["obj"].get_incremental_capacity_list()
        if incremental_capacity_list_values[-1] != len(available_resources):
            logger.error("Incremental capacity doesnt match available devices")
            if args.postcleanup:
                self.vs_obj_dict[ce][obj_name]["obj"].postcleanup()
            return False
        # Process resource IDs and incremental values if specified
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental:
                test_setup_info_incremental_values = ','.join([str(n) for n in incremental_capacity_list_values])
                if len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == len(available_resources):
                    test_setup_info_total_duration = args.duration
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and len(available_resources) > 1:
                    if self.vs_obj_dict[ce][obj_name]["obj"].incremental[0] == len(available_resources):
                        test_setup_info_total_duration = args.duration
                    else:
                        div = len(available_resources) // self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
                        mod = len(available_resources) % self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
                        if mod == 0:
                            test_setup_info_total_duration = args.duration * (div)
                        else:
                            test_setup_info_total_duration = args.duration * (div + 1)
                else:
                    test_setup_info_total_duration = args.duration * len(incremental_capacity_list_values)
            else:
                test_setup_info_total_duration = args.duration

            if args.webgui_incremental:
                test_setup_info_incremental_values = ','.join([str(n) for n in incremental_capacity_list_values])
            elif gave_incremental:
                test_setup_info_incremental_values = "No Incremental Value provided"
            self.vs_obj_dict[ce][obj_name]["obj"].total_duration = test_setup_info_total_duration

        actual_start_time = datetime.datetime.now()

        iterations_before_test_stopped_by_user = []

        # Calculate and manage cx_order_list ( list of cross connections to run ) based on incremental values
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            # Check if incremental  is specified
            if self.vs_obj_dict[ce][obj_name]["obj"].incremental:

                # Case 1: Incremental list has only one value and it equals the length of keys
                if len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and self.vs_obj_dict[ce][obj_name]["obj"].incremental[0] == len(keys):
                    cx_order_list.append(keys[index:])

                # Case 2: Incremental list has only one value but length of keys is greater than 1
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) == 1 and len(keys) > 1:
                    incremental_value = self.vs_obj_dict[ce][obj_name]["obj"].incremental[0]
                    max_index = len(keys)
                    index = 0

                    while index < max_index:
                        next_index = min(index + incremental_value, max_index)
                        cx_order_list.append(keys[index:next_index])
                        index = next_index

                # Case 3: Incremental list has multiple values and length of keys is greater than 1
                elif len(self.vs_obj_dict[ce][obj_name]["obj"].incremental) != 1 and len(keys) > 1:

                    index = 0
                    for num in self.vs_obj_dict[ce][obj_name]["obj"].incremental:

                        cx_order_list.append(keys[index: num])
                        index = num

                    if index < len(keys):
                        cx_order_list.append(keys[index:])

                # Iterate over cx_order_list to start tests incrementally
                for i in range(len(cx_order_list)):
                    if i == 0:
                        self.vs_obj_dict[ce][obj_name]["obj"].data["start_time_webGUI"] = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        end_time_webGUI = (datetime.datetime.now() + datetime.timedelta(minutes=self.vs_obj_dict[ce][obj_name]["obj"].total_duration)).strftime('%Y-%m-%d %H:%M:%S')
                        self.vs_obj_dict[ce][obj_name]["obj"].data['end_time_webGUI'] = [end_time_webGUI]

                    # time.sleep(10)

                    # Start specific devices based on incremental capacity
                    self.vs_obj_dict[ce][obj_name]["obj"].start_specific(cx_order_list[i])
                    if cx_order_list[i]:
                        logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                    else:
                        logging.info("Test started on Devices with resource Ids : {selected}".format(selected=cx_order_list[i]))
                    file_path = "video_streaming_realtime_data.csv"
                    if end_time_webGUI < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                        self.vs_obj_dict[ce][obj_name]["obj"].data['remaining_time_webGUI'] = ['0:00']
                    else:
                        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.vs_obj_dict[ce][obj_name]["obj"].data['remaining_time_webGUI'] = [datetime.datetime.strptime(end_time_webGUI, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")]

                    if args.dowebgui:
                        file_path = os.path.join(self.vs_obj_dict[ce][obj_name]["obj"].result_dir, "../../Running_instances/{}_{}_running.json".format(self.vs_obj_dict[ce][obj_name]["obj"].host, self.vs_obj_dict[ce][obj_name]["obj"].test_name))
                        if os.path.exists(file_path):
                            with open(file_path, 'r') as file:
                                data = json.load(file)
                                if data["status"] != "Running":
                                    break
                        test_stopped_by_user = self.vs_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                    else:
                        test_stopped_by_user = self.vs_obj_dict[ce][obj_name]["obj"].monitor_for_runtime_csv(args.duration, file_path, individual_df, i, actual_start_time, resource_list_sorted, cx_order_list[i])
                    if not test_stopped_by_user:
                        # Append current iteration index to iterations_before_test_stopped_by_user
                        iterations_before_test_stopped_by_user.append(i)
                    else:
                        # Append current iteration index to iterations_before_test_stopped_by_user
                        iterations_before_test_stopped_by_user.append(i)
                        break
        self.vs_obj_dict[ce][obj_name]["obj"].stop()

        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:

            date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            username = []

            try:
                eid_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal")
            except KeyError:
                logger.error("Error: 'interfaces' key not found in port data")
                return False

            resource_ids = list(map(int, self.vs_obj_dict[ce][obj_name]["obj"].resource_ids.split(',')))
            for alias in eid_data["interfaces"]:
                for i in alias:
                    if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                        resource_hw_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                        hw_version = resource_hw_data['resource']['hw version']
                        if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                            username.append(resource_hw_data['resource']['user'])

            device_list_str = ','.join([f"{name} ( Android )" for name in username])

            test_setup_info = {
                "Testname": args.test_name,
                "Device List": device_list_str,
                "No of Devices": "Total" + "( " + str(len(keys)) + " ): Android(" + str(len(keys)) + ")",
                "Incremental Values": "",
                "URL": args.url,
                "Media Source": media_source.upper(),
                "Media Quality": media_quality
            }
            test_setup_info['Incremental Values'] = test_setup_info_incremental_values
            test_setup_info['Total Duration (min)'] = str(test_setup_info_total_duration)

        logging.info("Test Completed")

        # prev_inc_value = 0
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids and self.vs_obj_dict[ce][obj_name]["obj"].incremental:
            self.vs_obj_dict[ce][obj_name]["obj"].generate_report(date, list(set(iterations_before_test_stopped_by_user)), test_setup_info=test_setup_info, realtime_dataset=individual_df,report_path=self.result_path if not self.dowebgui else self.result_dir)
        elif self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            self.vs_obj_dict[ce][obj_name]["obj"].generate_report(date, list(set(iterations_before_test_stopped_by_user)), test_setup_info=test_setup_info, realtime_dataset=individual_df,report_path=self.result_path if not self.dowebgui else self.result_dir)

        params = {
            "date": None,
            "iterations_before_test_stopped_by_user": None,
            "test_setup_info": None,
            "realtime_dataset": None,
            "report_path": "",
            "cx_order_list": []
        }
        if self.vs_obj_dict[ce][obj_name]["obj"].resource_ids and self.vs_obj_dict[ce][obj_name]["obj"].incremental:
            params.update({
                "date": date,
                "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
                "test_setup_info": test_setup_info,
                "realtime_dataset": individual_df,
                "report_path": self.result_path,
                "cx_order_list": cx_order_list
            })
        elif self.vs_obj_dict[ce][obj_name]["obj"].resource_ids:
            params.update({
                "date": date,
                "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
                "test_setup_info": test_setup_info,
                "realtime_dataset": individual_df,
                "report_path": self.result_path
            })
        self.vs_obj_dict[ce][obj_name]["data"] = params.copy()
        # Perform post-cleanup operations
        if args.postcleanup:
            self.vs_obj_dict[ce][obj_name]["obj"].postcleanup()

        if args.dowebgui:
            self.vs_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
            self.webgui_test_done("vs")
        return True


    def run_vs_test1(
        self,
        ssid=None,
        passwd="something",
        encryp="psk",
        url="www.google.com",
        max_speed=0,
        urls_per_tenm=100,
        duration=None,
        test_name="video_streaming_test",
        dowebgui=False,
        result_dir='',
        lf_logger_config_json=None,
        log_level=None,
        debug=False,
        media_source='1',
        media_quality='0',
        device_list=None,
        webgui_incremental=None,
        incremental=False,
        no_laptops=True,
        postcleanup=False,
        precleanup=False,
        help_summary=False,
        group_name=None,
        profile_name=None,
        file_name=None,
        eap_method='DEFAULT',
        eap_identity='DEFAULT',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        upstream_port='NA',
        expected_passfail_value=None,
        csv_name=None,
        wait_time=60,
        config=False,
        device_csv_name=None,
        get_live_view=False,
        floors=0
    ):
        args = SimpleNamespace(**locals())
        args.host = self.lanforge_ip
        return self.run_vs_test(args)

    def run_throughput_test(
        self,
        device_list=[],
        upstream_port='eth1',
        ssid=None,
        passwd='[BLANK]',
        traffic_type=None,
        upload='2560',
        download='2560',
        test_duration='',
        report_timer='1s',
        ap_name='Test-AP',
        dowebgui=False,
        tos='Best_Efforts',
        packet_size='-1',
        incremental_capacity=[],
        load_type='wc_per_client_load',
        do_interopability=False,
        postcleanup=False,
        precleanup=False,
        incremental=False,
        security='open',
        test_name=None,
        result_dir='',
        get_live_view=False,
        total_floors='0',
        expected_passfail_value=None,
        device_csv_name=None,
        eap_method='DEFAULT',
        eap_identity='',
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management='DEFAULT',
        pairwise='NA',
        private_key='NA',
        ca_cert='NA',
        client_cert='NA',
        pk_passwd='NA',
        pac_file='NA',
        file_name=None,
        group_name=None,
        profile_name=None,
        wait_time=60,
        config=False,
        default_config=True,
        tput_mbps=False,
        help_summary=False
    ):

        if dowebgui:
            if (upload == '0'):
                upload = '2560'
            if (download == '0'):
                download = '2560'
        if self.dowebgui:
            if not self.webgui_stop_check("thput"):
                return False

        logger_config = lf_logger_config.lf_logger_config()

        if(tput_mbps):
            if download != '2560' and download != '0' and upload != '0' and upload != '2560':
                download = str(int(download) * 1000000)
                upload = str(int(upload) * 1000000)
            elif upload != '2560' and upload != '0':
                upload = str(int(upload) * 1000000)
            else:
                download = str(int(download) * 1000000)
        loads = {}
        iterations_before_test_stopped_by_user = []
        gave_incremental = False
        # Case based on download and upload arguments are provided
        if download and upload:
            loads = {'upload': str(upload).split(","), 'download': str(download).split(",")}
            loads_data = loads["download"]
        elif download:
            loads = {'upload': [], 'download': str(download).split(",")}
            for i in range(len(download)):
                loads['upload'].append(2560)
            loads_data = loads["download"]
        else:
            if upload:
                loads = {'upload': str(upload).split(","), 'download': []}
                for i in range(len(upload)):
                    loads['download'].append(2560)
                loads_data = loads["upload"]

        if download != '2560' and download != '0' and upload != '0' and upload != '2560':
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_BiDi'
        elif upload != '2560' and upload != '0':
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_UL'
        else:
            csv_direction = 'L3_' + traffic_type.split('_')[1].upper() + '_DL'

        # validate_args(args)
        if incremental_capacity == 'no_increment' and dowebgui:
            incremental_capacity = str(len(device_list.split(",")))
            gave_incremental = True

        if do_interopability:
            incremental_capacity = "1"

        # Parsing test_duration
        if test_duration.endswith('s') or test_duration.endswith('S'):
            test_duration = int(test_duration[0:-1])

        elif test_duration.endswith('m') or test_duration.endswith('M'):
            test_duration = int(test_duration[0:-1]) * 60

        elif test_duration.endswith('h') or test_duration.endswith('H'):
            test_duration = int(test_duration[0:-1]) * 60 * 60

        elif test_duration.endswith(''):
            test_duration = int(test_duration)

        # Parsing report_timer
        if report_timer.endswith('s') or report_timer.endswith('S'):
            report_timer = int(report_timer[0:-1])

        elif report_timer.endswith('m') or report_timer.endswith('M'):
            report_timer = int(report_timer[0:-1]) * 60

        elif report_timer.endswith('h') or report_timer.endswith('H'):
            report_timer = int(report_timer[0:-1]) * 60 * 60

        elif test_duration.endswith(''):
            report_timer = int(report_timer)
        if (int(packet_size) < 16 or int(packet_size) > 65507) and int(packet_size) != -1:
            logger.error("Packet size should be greater than 16 bytes and less than 65507 bytes incorrect")
            return
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "thput_test"
        else:
            obj_no = 1
            while f"thput_test_{obj_no}" in self.thput_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"thput_test_{obj_no}" 
        self.thput_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        for index in range(len(loads_data)):
            self.thput_obj_dict[ce][obj_name]["obj"] = Throughput(host=self.lanforge_ip,
                                    ip=self.lanforge_ip,
                                    port=self.port,
                                    number_template="0000",
                                    ap_name=ap_name,
                                    name_prefix="TOS-",
                                    upstream=upstream_port,
                                    ssid=ssid,
                                    password=passwd,
                                    security=security,
                                    test_duration=test_duration,
                                    use_ht160=False,
                                    side_a_min_rate=int(loads['upload'][index]),
                                    side_b_min_rate=int(loads['download'][index]),
                                    side_a_min_pdu=int(packet_size),
                                    side_b_min_pdu=int(packet_size),
                                    traffic_type=traffic_type,
                                    tos=tos,
                                    dowebgui=dowebgui,
                                    test_name=test_name,
                                    result_dir=result_dir,
                                    device_list=device_list,
                                    incremental_capacity=incremental_capacity,
                                    report_timer=report_timer,
                                    load_type=load_type,
                                    do_interopability=do_interopability,
                                    incremental=incremental,
                                    precleanup=precleanup,
                                    get_live_view= get_live_view,
                                    total_floors = total_floors,
                                    csv_direction=csv_direction,
                                    expected_passfail_value=expected_passfail_value,
                                    device_csv_name=device_csv_name,
                                    file_name=file_name,
                                    group_name=group_name,
                                    profile_name=profile_name,
                                    eap_method=eap_method,
                                    eap_identity=eap_identity,
                                    ieee80211=ieee8021x,
                                    ieee80211u=ieee80211u,
                                    ieee80211w=ieee80211w,
                                    enable_pkc=enable_pkc,
                                    bss_transition=bss_transition,
                                    power_save=power_save,
                                    disable_ofdma=disable_ofdma,
                                    roam_ft_ds=roam_ft_ds,
                                    key_management=key_management,
                                    pairwise=pairwise,
                                    private_key=private_key,
                                    ca_cert=ca_cert,
                                    client_cert=client_cert,
                                    pk_passwd=pk_passwd,
                                    pac_file=pac_file,
                                    wait_time=wait_time,
                                    config=config,
                                    interopability_config = default_config
                                    )

            if gave_incremental:
                self.thput_obj_dict[ce][obj_name]["obj"].gave_incremental = True
            self.thput_obj_dict[ce][obj_name]["obj"].os_type()

            check_condition, clients_to_run = self.thput_obj_dict[ce][obj_name]["obj"].phantom_check()

            if check_condition == False:
                return

            check_increment_condition = self.thput_obj_dict[ce][obj_name]["obj"].check_incremental_list()

            if check_increment_condition == False:
                logger.error("Incremental values given for selected devices are incorrect")
                return

            elif (len(incremental_capacity) > 0 and check_increment_condition == False):
                logger.error("Incremental values given for selected devices are incorrect")
                return

            created_cxs = self.thput_obj_dict[ce][obj_name]["obj"].build()
            time.sleep(10)
            created_cxs = list(created_cxs.keys())
            individual_dataframe_column = []

            to_run_cxs, to_run_cxs_len, created_cx_lists_keys, incremental_capacity_list = self.thput_obj_dict[ce][obj_name]["obj"].get_incremental_capacity_list()

            for i in range(len(clients_to_run)):

                # Extend individual_dataframe_column with dynamically generated column names
                individual_dataframe_column.extend([f'Download{clients_to_run[i]}', f'Upload{clients_to_run[i]}', f'Rx % Drop  {clients_to_run[i]}',
                                                f'Tx % Drop{clients_to_run[i]}', f'Average RTT {clients_to_run[i]} ', f'RSSI {clients_to_run[i]} ', f'Tx-Rate {clients_to_run[i]} ', f'Rx-Rate {clients_to_run[i]} '])

            individual_dataframe_column.extend(['Overall Download', 'Overall Upload', 'Overall Rx % Drop ', 'Overall Tx % Drop', 'Iteration',
                                            'TIMESTAMP', 'Start_time', 'End_time', 'Remaining_Time', 'Incremental_list', 'status'])
            individual_df = pd.DataFrame(columns=individual_dataframe_column)

            overall_start_time = datetime.datetime.now()
            overall_end_time = overall_start_time + datetime.timedelta(seconds=int(test_duration) * len(incremental_capacity_list))

            for i in range(len(to_run_cxs)):
                is_device_configured = True
                if do_interopability:
                    # To get resource of device under test in interopability
                    device_to_run_resource = self.thput_obj_dict[ce][obj_name]["obj"].extract_digits_until_alpha(to_run_cxs[i][0])

                # Check the load type specified by the user
                if load_type == "wc_intended_load":
                    # Perform intended load for the current iteration
                    self.thput_obj_dict[ce][obj_name]["obj"].perform_intended_load(i, incremental_capacity_list)
                    if i != 0:

                        # Stop throughput testing if not the first iteration
                        self.thput_obj_dict[ce][obj_name]["obj"].stop()

                    # Start specific connections for the current iteration
                    self.thput_obj_dict[ce][obj_name]["obj"].start_specific(created_cx_lists_keys[:incremental_capacity_list[i]])
                else:
                    if (do_interopability and i != 0):
                        self.thput_obj_dict[ce][obj_name]["obj"].stop_specific(to_run_cxs[i - 1])
                        time.sleep(5)
                    if not default_config:
                        if (do_interopability and i == 0):
                            self.thput_obj_dict[ce][obj_name]["obj"].disconnect_all_devices()
                        if do_interopability and "iOS" not in to_run_cxs[i][0]:
                            logger.info("Configuring device of resource{}".format(to_run_cxs[i][0]))
                            is_device_configured = self.thput_obj_dict[ce][obj_name]["obj"].configure_specific([device_to_run_resource])
                    if is_device_configured:
                        self.thput_obj_dict[ce][obj_name]["obj"].start_specific(to_run_cxs[i])

                # Determine device names based on the current iteration
                device_names = created_cx_lists_keys[:to_run_cxs_len[i][-1]]

                # Monitor throughput and capture all dataframes and test stop status
                all_dataframes, test_stopped_by_user = self.thput_obj_dict[ce][obj_name]["obj"].monitor(i, individual_df, device_names, incremental_capacity_list, overall_start_time, overall_end_time, is_device_configured)
                if do_interopability and "iOS" not in to_run_cxs[i][0] and not default_config:
                    # logger.info("Disconnecting device of resource{}".format(to_run_cxs[i][0]))
                    self.thput_obj_dict[ce][obj_name]["obj"].disconnect_all_devices([device_to_run_resource])
                # Check if the test was stopped by the user
                if test_stopped_by_user == False:

                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                else:

                    # Append current iteration index to iterations_before_test_stopped_by_user
                    iterations_before_test_stopped_by_user.append(i)
                    break

        #     logger.info("connections download {}".format(connections_download))
        #     logger.info("connections upload {}".format(connections_upload))
        self.thput_obj_dict[ce][obj_name]["obj"].stop()
        if postcleanup:
            self.thput_obj_dict[ce][obj_name]["obj"].cleanup()
        self.thput_obj_dict[ce][obj_name]["obj"].generate_report(list(set(iterations_before_test_stopped_by_user)), incremental_capacity_list, data=all_dataframes, data1=to_run_cxs_len, report_path=self.result_path if not self.thput_obj_dict[ce][obj_name]["obj"].dowebgui else self.thput_obj_dict[ce][obj_name]["obj"].result_dir)
        if self.thput_obj_dict[ce][obj_name]["obj"].dowebgui:
            # copying to home directory i.e home/user_name
            self.thput_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()
        params = {
            "iterations_before_test_stopped_by_user": list(set(iterations_before_test_stopped_by_user)),
            "incremental_capacity_list": incremental_capacity_list,
            "data": all_dataframes,
            "data1": to_run_cxs_len,
            "report_path": self.result_path if not self.thput_obj_dict[ce][obj_name]["obj"].dowebgui else self.thput_obj_dict[ce][obj_name]["obj"].result_dir
        }
        self.thput_obj_dict[ce][obj_name]["data"] = params.copy()
        if self.dowebgui:
            self.webgui_test_done("thput")
        return True

    def run_mc_test(self,args):
        endp_types = "lf_udp"

        help_summary = '''\
    The Layer 3 Traffic Generation Test is designed to test the performance of the
    Access Point by running layer 3 TCP and/or UDP Traffic.  Layer-3 Cross-Connects represent a stream
    of data flowing through the system under test. A Cross-Connect (CX) is composed of two Endpoints,
    each of which is associated with a particular Port (physical or virtual interface).

    The test will create stations, create CX traffic between upstream port and stations, run traffic
    and generate a report.
    '''
        # args = parse_args()
        if self.dowebgui:
            if not self.webgui_stop_check("mc"):
                return False
        test_name = ""
        ip = ""
        # print('newww',args.local_lf_report_dir)
        # exit(0)
        if args.dowebgui:
            logger.info("In webGUI execution")
            if args.dowebgui:
                test_name = args.test_name
                ip = args.lfmgr
                logger.info(" dowebgui %s %s %s", args.dowebgui, test_name, ip)

        # initialize pass / fail
        test_passed = False

        # Configure logging
        logger_config = lf_logger_config.lf_logger_config()

        # set the logger level to debug
        if args.log_level:
            logger_config.set_level(level=args.log_level)

        # lf_logger_config_json will take presidence to changing debug levels
        if args.lf_logger_config_json:
            # logger_config.lf_logger_config_json = "lf_logger_config.json"
            logger_config.lf_logger_config_json = args.lf_logger_config_json
            logger_config.load_lf_logger_config()

        # validate_args(args)
        endp_input_list = []
        graph_input_list = []
        if args.real:
            endp_input_list, graph_input_list, config_devices, group_device_map = query_real_clients(args)
        # Validate existing station list configuration if specified before starting test
        if not args.use_existing_station_list and args.existing_station_list:
            logger.error("Existing stations specified, but argument \'--use_existing_station_list\' not specified")
            return False
        elif args.use_existing_station_list and not args.existing_station_list:
            logger.error(
                "Argument \'--use_existing_station_list\' specified, but no existing stations provided. See \'--existing_station_list\'")
            return False

        # Gather data for test reporting and KPI generation
        logger.info("Read in command line paramaters")
        interopt_mode = args.interopt_mode

        if args.endp_type:
            endp_types = args.endp_type

        if args.radio:
            radios = args.radio
        else:
            radios = None

        MAX_NUMBER_OF_STATIONS = 1000

        # Lists to help with station creation
        radio_name_list = []
        number_of_stations_per_radio_list = []
        ssid_list = []
        ssid_password_list = []
        ssid_security_list = []
        station_lists = []
        existing_station_lists = []

        # wifi settings configuration
        wifi_mode_list = []
        wifi_enable_flags_list = []

        # optional radio configuration
        reset_port_enable_list = []
        reset_port_time_min_list = []
        reset_port_time_max_list = []

        # wifi extra configuration
        key_mgmt_list = []
        pairwise_list = []
        group_list = []
        psk_list = []
        wep_key_list = []
        ca_cert_list = []
        eap_list = []
        identity_list = []
        anonymous_identity_list = []
        phase1_list = []
        phase2_list = []
        passwd_list = []
        pin_list = []
        pac_file_list = []
        private_key_list = []
        pk_password_list = []
        hessid_list = []
        realm_list = []
        client_cert_list = []
        imsi_list = []
        milenage_list = []
        domain_list = []
        roaming_consortium_list = []
        venue_group_list = []
        network_type_list = []
        ipaddr_type_avail_list = []
        network_auth_type_list = []
        anqp_3gpp_cell_net_list = []
        ieee80211w_list = []

        logger.debug("Parse radio arguments used for station configuration")
        if radios is not None:
            logger.info("radios {}".format(radios))
            for radio_ in radios:
                radio_keys = ['radio', 'stations', 'ssid', 'ssid_pw', 'security']
                logger.info("radio_dict before format {}".format(radio_))
                radio_info_dict = dict(
                    map(
                        lambda x: x.split('=='),
                        str(radio_).replace(
                            '"',
                            '').replace(
                            '[',
                            '').replace(
                            ']',
                            '').replace(
                            "'",
                            "").replace(
                                ",",
                            " ").split()))

                logger.debug("radio_dict {}".format(radio_info_dict))

                for key in radio_keys:
                    if key not in radio_info_dict:
                        logger.critical(
                            "missing config, for the {}, all of the following need to be present {} ".format(
                                key, radio_keys))
                        return False

                radio_name_list.append(radio_info_dict['radio'])
                number_of_stations_per_radio_list.append(
                    radio_info_dict['stations'])
                ssid_list.append(radio_info_dict['ssid'])
                ssid_password_list.append(radio_info_dict['ssid_pw'])
                ssid_security_list.append(radio_info_dict['security'])

                # check for set_wifi_extra
                # check for wifi_settings
                wifi_extra_keys = ['wifi_extra']
                wifi_extra_found = False
                for wifi_extra_key in wifi_extra_keys:
                    if wifi_extra_key in radio_info_dict:
                        logger.info("wifi_extra_keys found")
                        wifi_extra_found = True
                        break

                if wifi_extra_found:
                    logger.debug("wifi_extra: {extra}".format(
                        extra=radio_info_dict['wifi_extra']))

                    wifi_extra_dict = dict(
                        map(
                            lambda x: x.split('&&'),
                            str(radio_info_dict['wifi_extra']).replace(
                                '"',
                                '').replace(
                                '[',
                                '').replace(
                                ']',
                                '').replace(
                                "'",
                                "").replace(
                                ",",
                                " ").replace(
                                "!!",
                                " "
                            )
                            .split()))

                    logger.info("wifi_extra_dict: {wifi_extra}".format(
                        wifi_extra=wifi_extra_dict))

                    if 'key_mgmt' in wifi_extra_dict:
                        key_mgmt_list.append(wifi_extra_dict['key_mgmt'])
                    else:
                        key_mgmt_list.append('[BLANK]')

                    if 'pairwise' in wifi_extra_dict:
                        pairwise_list.append(wifi_extra_dict['pairwise'])
                    else:
                        pairwise_list.append('[BLANK]')

                    if 'group' in wifi_extra_dict:
                        group_list.append(wifi_extra_dict['group'])
                    else:
                        group_list.append('[BLANK]')

                    if 'psk' in wifi_extra_dict:
                        psk_list.append(wifi_extra_dict['psk'])
                    else:
                        psk_list.append('[BLANK]')

                    if 'wep_key' in wifi_extra_dict:
                        wep_key_list.append(wifi_extra_dict['wep_key'])
                    else:
                        wep_key_list.append('[BLANK]')

                    if 'ca_cert' in wifi_extra_dict:
                        ca_cert_list.append(wifi_extra_dict['ca_cert'])
                    else:
                        ca_cert_list.append('[BLANK]')

                    if 'eap' in wifi_extra_dict:
                        eap_list.append(wifi_extra_dict['eap'])
                    else:
                        eap_list.append('[BLANK]')

                    if 'identity' in wifi_extra_dict:
                        identity_list.append(wifi_extra_dict['identity'])
                    else:
                        identity_list.append('[BLANK]')

                    if 'anonymous' in wifi_extra_dict:
                        anonymous_identity_list.append(
                            wifi_extra_dict['anonymous'])
                    else:
                        anonymous_identity_list.append('[BLANK]')

                    if 'phase1' in wifi_extra_dict:
                        phase1_list.append(wifi_extra_dict['phase1'])
                    else:
                        phase1_list.append('[BLANK]')

                    if 'phase2' in wifi_extra_dict:
                        phase2_list.append(wifi_extra_dict['phase2'])
                    else:
                        phase2_list.append('[BLANK]')

                    if 'passwd' in wifi_extra_dict:
                        passwd_list.append(wifi_extra_dict['passwd'])
                    else:
                        passwd_list.append('[BLANK]')

                    if 'pin' in wifi_extra_dict:
                        pin_list.append(wifi_extra_dict['pin'])
                    else:
                        pin_list.append('[BLANK]')

                    if 'pac_file' in wifi_extra_dict:
                        pac_file_list.append(wifi_extra_dict['pac_file'])
                    else:
                        pac_file_list.append('[BLANK]')

                    if 'private_key' in wifi_extra_dict:
                        private_key_list.append(wifi_extra_dict['private_key'])
                    else:
                        private_key_list.append('[BLANK]')

                    if 'pk_password' in wifi_extra_dict:
                        pk_password_list.append(wifi_extra_dict['pk_password'])
                    else:
                        pk_password_list.append('[BLANK]')

                    if 'hessid' in wifi_extra_dict:
                        hessid_list.append(wifi_extra_dict['hessid'])
                    else:
                        hessid_list.append("00:00:00:00:00:00")

                    if 'realm' in wifi_extra_dict:
                        realm_list.append(wifi_extra_dict['realm'])
                    else:
                        realm_list.append('[BLANK]')

                    if 'client_cert' in wifi_extra_dict:
                        client_cert_list.append(wifi_extra_dict['client_cert'])
                    else:
                        client_cert_list.append('[BLANK]')

                    if 'imsi' in wifi_extra_dict:
                        imsi_list.append(wifi_extra_dict['imsi'])
                    else:
                        imsi_list.append('[BLANK]')

                    if 'milenage' in wifi_extra_dict:
                        milenage_list.append(wifi_extra_dict['milenage'])
                    else:
                        milenage_list.append('[BLANK]')

                    if 'domain' in wifi_extra_dict:
                        domain_list.append(wifi_extra_dict['domain'])
                    else:
                        domain_list.append('[BLANK]')

                    if 'roaming_consortium' in wifi_extra_dict:
                        roaming_consortium_list.append(
                            wifi_extra_dict['roaming_consortium'])
                    else:
                        roaming_consortium_list.append('[BLANK]')

                    if 'venue_group' in wifi_extra_dict:
                        venue_group_list.append(wifi_extra_dict['venue_group'])
                    else:
                        venue_group_list.append('[BLANK]')

                    if 'network_type' in wifi_extra_dict:
                        network_type_list.append(wifi_extra_dict['network_type'])
                    else:
                        network_type_list.append('[BLANK]')

                    if 'ipaddr_type_avail' in wifi_extra_dict:
                        ipaddr_type_avail_list.append(
                            wifi_extra_dict['ipaddr_type_avail'])
                    else:
                        ipaddr_type_avail_list.append('[BLANK]')

                    if 'network_auth_type' in wifi_extra_dict:
                        network_auth_type_list.append(
                            wifi_extra_dict['network_auth_type'])
                    else:
                        network_auth_type_list.append('[BLANK]')

                    if 'anqp_3gpp_cell_net' in wifi_extra_dict:
                        anqp_3gpp_cell_net_list.append(
                            wifi_extra_dict['anqp_3gpp_cell_net'])
                    else:
                        anqp_3gpp_cell_net_list.append('[BLANK]')

                    if 'ieee80211w' in wifi_extra_dict:
                        ieee80211w_list.append(wifi_extra_dict['ieee80211w'])
                    else:
                        ieee80211w_list.append('Optional')

                    '''
                    # wifi extra configuration
                    key_mgmt_list.append(key_mgmt)
                    pairwise_list.append(pairwise)
                    group_list.append(group)
                    psk_list.append(psk)
                    eap_list.append(eap)
                    identity_list.append(identity)
                    anonymous_identity_list.append(anonymous_identity)
                    phase1_list.append(phase1)
                    phase2_list.append(phase2)
                    passwd_list.append(passwd)
                    pin_list.append(pin)
                    pac_file_list.append(pac_file)
                    private_key_list.append(private)
                    pk_password_list.append(pk_password)
                    hessid_list.append(hssid)
                    realm_list.append(realm)
                    client_cert_list.append(client_cert)
                    imsi_list.append(imsi)
                    milenage_list.append(milenage)
                    domain_list.append(domain)
                    roaming_consortium_list.append(roaming_consortium)
                    venue_group_list.append(venue_group)
                    network_type_list.append(network_type)
                    ipaddr_type_avail_list.append(ipaddr_type_avail)
                    network_auth_type_list.append(network_ath_type)
                    anqp_3gpp_cell_net_list.append(anqp_3gpp_cell_net)

                    '''
                # no wifi extra for this station
                else:
                    key_mgmt_list.append('[BLANK]')
                    pairwise_list.append('[BLANK]')
                    group_list.append('[BLANK]')
                    psk_list.append('[BLANK]')
                    # for testing
                    # psk_list.append(radio_info_dict['ssid_pw'])
                    wep_key_list.append('[BLANK]')
                    ca_cert_list.append('[BLANK]')
                    eap_list.append('[BLANK]')
                    identity_list.append('[BLANK]')
                    anonymous_identity_list.append('[BLANK]')
                    phase1_list.append('[BLANK]')
                    phase2_list.append('[BLANK]')
                    passwd_list.append('[BLANK]')
                    pin_list.append('[BLANK]')
                    pac_file_list.append('[BLANK]')
                    private_key_list.append('[BLANK]')
                    pk_password_list.append('[BLANK]')
                    hessid_list.append("00:00:00:00:00:00")
                    realm_list.append('[BLANK]')
                    client_cert_list.append('[BLANK]')
                    imsi_list.append('[BLANK]')
                    milenage_list.append('[BLANK]')
                    domain_list.append('[BLANK]')
                    roaming_consortium_list.append('[BLANK]')
                    venue_group_list.append('[BLANK]')
                    network_type_list.append('[BLANK]')
                    ipaddr_type_avail_list.append('[BLANK]')
                    network_auth_type_list.append('[BLANK]')
                    anqp_3gpp_cell_net_list.append('[BLANK]')
                    ieee80211w_list.append('Optional')

                # check for wifi_settings
                wifi_settings_keys = ['wifi_settings']
                wifi_settings_found = True
                for key in wifi_settings_keys:
                    if key not in radio_info_dict:
                        logger.debug("wifi_settings_keys not enabled")
                        wifi_settings_found = False
                        break

                if wifi_settings_found:
                    # Check for additional flags
                    if {'wifi_mode', 'enable_flags'}.issubset(
                            radio_info_dict.keys()):
                        logger.debug("wifi_settings flags set")
                    else:
                        logger.debug("wifi_settings is present wifi_mode, enable_flags need to be set "
                                    "or remove the wifi_settings or set wifi_settings==False flag on "
                                    "the radio for defaults")
                        return False
                    wifi_mode_list.append(radio_info_dict['wifi_mode'])
                    enable_flags_str = radio_info_dict['enable_flags'].replace(
                        '(', '').replace(')', '').replace('|', ',').replace('&&', ',')
                    enable_flags_list = list(enable_flags_str.split(","))
                    wifi_enable_flags_list.append(enable_flags_list)
                else:
                    wifi_mode_list.append(0)
                    wifi_enable_flags_list.append(
                        ["wpa2_enable", "80211u_enable", "create_admin_down"])
                    # 8021x_radius is the same as Advanced/8021x on the gui

                # check for optional radio key , currently only reset is enabled
                # update for checking for reset_port_time_min, reset_port_time_max
                optional_radio_reset_keys = ['reset_port_enable']
                radio_reset_found = True
                for key in optional_radio_reset_keys:
                    if key not in radio_info_dict:
                        # logger.debug("port reset test not enabled")
                        radio_reset_found = False
                        break

                if radio_reset_found:
                    reset_port_enable_list.append(
                        radio_info_dict['reset_port_enable'])
                    reset_port_time_min_list.append(
                        radio_info_dict['reset_port_time_min'])
                    reset_port_time_max_list.append(
                        radio_info_dict['reset_port_time_max'])
                else:
                    reset_port_enable_list.append(False)
                    reset_port_time_min_list.append('0s')
                    reset_port_time_max_list.append('0s')

            index = 0
            for (radio_name_, number_of_stations_per_radio_) in zip(
                    radio_name_list, number_of_stations_per_radio_list):
                number_of_stations = int(number_of_stations_per_radio_)
                if number_of_stations > MAX_NUMBER_OF_STATIONS:
                    logger.critical("number of stations per radio exceeded max of : {}".format(
                        MAX_NUMBER_OF_STATIONS))
                    quit(1)
                station_list = LFUtils.portNameSeries(
                    prefix_="sta",
                    start_id_=0 + index * 1000 + int(args.sta_start_offset),
                    end_id_=number_of_stations - 1 + index *
                    1000 + int(args.sta_start_offset),
                    padding_number_=10000,
                    radio=radio_name_)
                station_lists.append(station_list)
                index += 1

        # create a secondary station_list
        if args.use_existing_station_list:
            if args.existing_station_list is not None:
                # these are entered stations
                for existing_sta_list in args.existing_station_list:
                    existing_stations = str(existing_sta_list).replace(
                        '"',
                        '').replace(
                        '[',
                        '').replace(
                        ']',
                        '').replace(
                        "'",
                        "").replace(
                            ",",
                        " ").split()

                    for existing_sta in existing_stations:
                        existing_station_lists.append(existing_sta)
            else:
                logger.error(
                    "--use_station_list set true, --station_list is None Exiting")
                raise Exception(
                    "--use_station_list is used in conjunction with a --station_list")

        logger.info("existing_station_lists: {sta}".format(
            sta=existing_station_lists))

        # logger.info("endp-types: %s"%(endp_types))
        ul_rates = args.side_a_min_bps.replace(',', ' ').split()
        dl_rates = args.side_b_min_bps.replace(',', ' ').split()
        ul_pdus = args.side_a_min_pdu.replace(',', ' ').split()
        dl_pdus = args.side_b_min_pdu.replace(',', ' ').split()
        if args.attenuators == "":
            attenuators = []
        else:
            attenuators = args.attenuators.split(",")
        if args.atten_vals == "":
            atten_vals = [-1]
        else:
            atten_vals = args.atten_vals.split(",")

        if len(ul_rates) != len(dl_rates):
            # todo make fill assignable
            logger.info(
                "ul_rates %s and dl_rates %s arrays are of different length will fill shorter list with 256000\n" %
                (len(ul_rates), len(dl_rates)))
        if len(ul_pdus) != len(dl_pdus):
            logger.info(
                "ul_pdus %s and dl_pdus %s arrays are of different lengths will fill shorter list with size AUTO \n" %
                (len(ul_pdus), len(dl_pdus)))

        # Configure reporting
        logger.info("Configuring report")
        report, kpi_csv, csv_outfile = configure_reporting(**vars(args))
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "mcast_test"
        else:
            obj_no = 1
            while f"mcast_test_{obj_no}" in self.mcast_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"mcast_test_{obj_no}" 
        self.mcast_obj_dict[ce][obj_name] = {"obj":None,"data":None}
        logger.debug("Configure test object")
        self.mcast_obj_dict[ce][obj_name]["obj"] = L3VariableTime(
            endp_types=endp_types,
            args=args,
            tos=args.tos,
            side_b=args.upstream_port,
            side_a=args.downstream_port,
            radio_name_list=radio_name_list,
            number_of_stations_per_radio_list=number_of_stations_per_radio_list,
            ssid_list=ssid_list,
            ssid_password_list=ssid_password_list,
            ssid_security_list=ssid_security_list,
            wifi_mode_list=wifi_mode_list,
            enable_flags_list=wifi_enable_flags_list,
            station_lists=station_lists,
            name_prefix="LT-",
            outfile=csv_outfile,
            reset_port_enable_list=reset_port_enable_list,
            reset_port_time_min_list=reset_port_time_min_list,
            reset_port_time_max_list=reset_port_time_max_list,
            side_a_min_rate=ul_rates,
            side_b_min_rate=dl_rates,
            side_a_min_pdu=ul_pdus,
            side_b_min_pdu=dl_pdus,
            rates_are_totals=args.rates_are_totals,
            mconn=args.multiconn,
            attenuators=attenuators,
            atten_vals=atten_vals,
            number_template="00",
            test_duration=args.test_duration,
            polling_interval=args.polling_interval,
            lfclient_host=args.lfmgr,
            lfclient_port=args.lfmgr_port,
            debug=args.debug,
            kpi_csv=kpi_csv,
            no_cleanup=args.no_cleanup,
            use_existing_station_lists=args.use_existing_station_list,
            existing_station_lists=existing_station_lists,
            wait_for_ip_sec=args.wait_for_ip_sec,
            exit_on_ip_acquired=args.exit_on_ip_acquired,
            ap_read=args.ap_read,
            ap_module=args.ap_module,
            ap_test_mode=args.ap_test_mode,
            ap_ip=args.ap_ip,
            ap_user=args.ap_user,
            ap_passwd=args.ap_passwd,
            ap_scheme=args.ap_scheme,
            ap_serial_port=args.ap_serial_port,
            ap_ssh_port=args.ap_ssh_port,
            ap_telnet_port=args.ap_telnet_port,
            ap_serial_baud=args.ap_serial_baud,
            ap_if_2g=args.ap_if_2g,
            ap_if_5g=args.ap_if_5g,
            ap_if_6g=args.ap_if_6g,
            ap_report_dir="",
            ap_file=args.ap_file,
            ap_band_list=args.ap_band_list.split(','),

            # for webgui execution
            test_name=test_name,
            dowebgui=args.dowebgui,
            ip=ip,
            get_live_view= args.get_live_view,
            total_floors = args.total_floors,
            # for uniformity from webGUI result_dir as variable is used insead of local_lf_report_dir
            result_dir=args.local_lf_report_dir,

            # wifi extra configuration
            key_mgmt_list=key_mgmt_list,
            pairwise_list=pairwise_list,
            group_list=group_list,
            psk_list=psk_list,
            wep_key_list=wep_key_list,
            ca_cert_list=ca_cert_list,
            eap_list=eap_list,
            identity_list=identity_list,
            anonymous_identity_list=anonymous_identity_list,
            phase1_list=phase1_list,
            phase2_list=phase2_list,
            passwd_list=passwd_list,
            pin_list=pin_list,
            pac_file_list=pac_file_list,
            private_key_list=private_key_list,
            pk_password_list=pk_password_list,
            hessid_list=hessid_list,
            realm_list=realm_list,
            client_cert_list=client_cert_list,
            imsi_list=imsi_list,
            milenage_list=milenage_list,
            domain_list=domain_list,
            roaming_consortium_list=roaming_consortium_list,
            venue_group_list=venue_group_list,
            network_type_list=network_type_list,
            ipaddr_type_avail_list=ipaddr_type_avail_list,
            network_auth_type_list=network_auth_type_list,
            anqp_3gpp_cell_net_list=anqp_3gpp_cell_net_list,
            ieee80211w_list=ieee80211w_list,
            interopt_mode=interopt_mode,
            endp_input_list=endp_input_list,
            graph_input_list=graph_input_list,
            real=args.real,
            expected_passfail_value=args.expected_passfail_value,
            device_csv_name=args.device_csv_name,
            group_name=args.group_name
        )

        # Perform pre-test cleanup, if configured to do so
        if args.no_pre_cleanup:
            logger.info("Skipping pre-test cleanup, '--no_pre_cleanup' specified")
        elif args.use_existing_station_list:
            logger.info("Skipping pre-test cleanup, '--use_existing_station_list' specified")
        else:
            logger.info("Performing pre-test cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].pre_cleanup()

        # Build test configuration
        logger.info("Building test configuration")
        self.mcast_obj_dict[ce][obj_name]["obj"].build()
        if not self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            logger.critical("Test configuration build failed")
            logger.critical(self.mcast_obj_dict[ce][obj_name]["obj"].get_fail_message())
            return False

        # Run test
        logger.info("Starting test")
        self.mcast_obj_dict[ce][obj_name]["obj"].start(False)

        if args.wait > 0:
            logger.info(f"Pausing {args.wait} seconds for manual inspection before test conclusion and "
                        "possible traffic stop/post-test cleanup")
            time.sleep(args.wait)

        # Admin down the stations
        if args.no_stop_traffic:
            logger.info("Test complete, '--no_stop_traffic' specified, traffic continues to run")
        else:
            if args.quiesce_cx:
                logger.info("Test complete, quiescing traffic")
                self.mcast_obj_dict[ce][obj_name]["obj"].quiesce_cx()
                time.sleep(3)
            else:
                logger.info("Test complete, stopping traffic")
                self.mcast_obj_dict[ce][obj_name]["obj"].stop()

        # Set DUT information for reporting
        self.mcast_obj_dict[ce][obj_name]["obj"].set_dut_info(
            dut_model_num=args.dut_model_num,
            dut_hw_version=args.dut_hw_version,
            dut_sw_version=args.dut_sw_version,
            dut_serial_num=args.dut_serial_num)
        self.mcast_obj_dict[ce][obj_name]["obj"].set_report_obj(report=report)
        if args.dowebgui:
            self.mcast_obj_dict[ce][obj_name]["obj"].webgui_finalize()
        # Generate and write out test report
        logger.info("Generating test report")
        if args.real:
            self.mcast_obj_dict[ce][obj_name]["obj"].generate_report(config_devices, group_device_map)
        else:
            self.mcast_obj_dict[ce][obj_name]["obj"].generate_report()
        params = {
            "config_devices" : None,
            "group_device_map": None
        }
        params["group_device_map"] = group_device_map
        params["config_devices"] = config_devices
        self.mcast_obj_dict[ce][obj_name]["data"] = params.copy()
        self.mcast_obj_dict[ce][obj_name]["obj"].write_report()

        # TODO move to after reporting
        if not self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            logger.warning("Test Ended: There were Failures")
            logger.warning(self.mcast_obj_dict[ce][obj_name]["obj"].get_fail_message())

        if args.no_cleanup:
            logger.info("Skipping post-test cleanup, '--no_cleanup' specified")
        elif args.no_stop_traffic:
            logger.info("Skipping post-test cleanup, '--no_stop_traffic' specified")
        else:
            logger.info("Performing post-test cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].cleanup()

        # TODO: This is redundant if '--no_cleanup' is not specified (already taken care of there)
        if args.cleanup_cx:
            logger.info("Performing post-test CX traffic pair cleanup")
            self.mcast_obj_dict[ce][obj_name]["obj"].cleanup_cx()

        if self.mcast_obj_dict[ce][obj_name]["obj"].passes():
            test_passed = True
            logger.info("Full test passed, all connections increased rx bytes")

        # Run WebGUI-specific post test logic
        if args.dowebgui:
            self.mcast_obj_dict[ce][obj_name]["obj"].copy_reports_to_home_dir()

        if test_passed:
            self.mcast_obj_dict[ce][obj_name]["obj"].exit_success()
        else:
            self.mcast_obj_dict[ce][obj_name]["obj"].exit_fail()
        if self.dowebgui:
            self.webgui_test_done("mc")
        return True


    def run_mc_test1(
        self,
        local_lf_report_dir="",
        results_dir_name="test_l3",
        test_rig="",
        test_tag="",
        dut_hw_version="",
        dut_sw_version="",
        dut_model_num="",
        dut_serial_num="",
        test_priority="",
        test_id="test l3",
        csv_outfile="",
        tty="",
        baud="9600",
        test_duration="3m",
        tos="BE",
        debug=False,
        log_level=None,
        interopt_mode=False,
        endp_type="mc_udp",
        upstream_port="eth1",
        downstream_port=None,
        polling_interval="5s",
        radio=None,
        side_a_min_bps="0",
        side_a_min_pdu="MTU",
        side_b_min_bps="256000",
        side_b_min_pdu="MTU",
        rates_are_totals=True,
        multiconn=1,
        attenuators="",
        atten_vals="",
        wait=0,
        sta_start_offset="0",
        no_pre_cleanup=False,
        no_cleanup=True,
        cleanup_cx=False,
        csv_data_to_report=False,
        no_stop_traffic=False,
        quiesce_cx=False,
        use_existing_station_list=False,
        existing_station_list=None,
        wait_for_ip_sec="120s",
        exit_on_ip_acquired=False,
        lf_logger_config_json=None,
        ap_read=False,
        ap_module=None,
        ap_test_mode=True,
        ap_scheme="serial",
        ap_serial_port="/dev/ttyUSB0",
        ap_serial_baud="115200",
        ap_ip="192.168.50.1",
        ap_ssh_port="1025",
        ap_telnet_port="23",
        ap_user="lanforge",
        ap_passwd="lanforge",
        ap_if_2g="wl0",
        ap_if_5g="wl1",
        ap_if_6g="wl2",
        ap_file=None,
        ap_band_list="2g,5g,6g",
        dowebgui=False,
        test_name=None,
        ssid=None,
        passwd=None,
        security=None,
        device_list=None,
        expected_passfail_value=None,
        device_csv_name=None,
        file_name=None,
        group_name=None,
        profile_name=None,
        eap_method="DEFAULT",
        eap_identity="",
        ieee8021x=False,
        ieee80211u=False,
        ieee80211w=1,
        enable_pkc=False,
        bss_transition=False,
        power_save=False,
        disable_ofdma=False,
        roam_ft_ds=False,
        key_management="DEFAULT",
        pairwise="NA",
        private_key="NA",
        ca_cert="NA",
        client_cert="NA",
        pk_passwd="NA",
        pac_file="NA",
        config=False,
        wait_time=60,
        real=True,
        get_live_view=False,
        total_floors="0",
        help_summary=False,
        result_dir = ''
    ):
        args = SimpleNamespace(**locals())
        args.lfmgr_port = self.port
        args.lfmgr = self.lanforge_ip
        args.local_lf_report_dir = os.getcwd() if not args.dowebgui else result_dir
        return self.run_mc_test(args)


    def run_yt_test(
            self,
            url=None,
            duration=None,
            ap_name="TIP",
            sec="wpa2",
            band="5GHZ",
            test_name=None,
            upstream_port=None,
            resource_list=None,
            no_pre_cleanup=False,
            no_post_cleanup=False,
            debug=False,
            log_level=None,
            res="Auto",
            lf_logger_config_json=None,
            ui_report_dir=None,
            do_webUI=False,
            file_name=None,
            group_name=None,
            profile_name=None,
            ssid=None,
            passwd=None,
            encryp=None,
            eap_method="DEFAULT",
            eap_identity="DEFAULT",
            ieee8021x=False,
            ieee80211u=False,
            ieee80211w=1,
            enable_pkc=False,
            bss_transition=False,
            power_save=False,
            disable_ofdma=False,
            roam_ft_ds=False,
            key_management="DEFAULT",
            pairwise="NA",
            private_key="NA",
            ca_cert="NA",
            pac_file="NA",
            client_cert="NA",
            pk_passwd="NA",
            help_summary=None,
            expected_passfail_value=None,
            device_csv_name=None,
            config=False,
            exec_type=None
    ):
        try:
            print('duration',duration)
            if self.dowebgui:
                if not self.webgui_stop_check("yt"):
                    return False
            if type(duration) == int:
                pass
            elif duration.endswith('s') or duration.endswith('S'):
                duration = int(duration[0:-1])/60
            elif duration.endswith('m') or duration.endswith('M'):
                duration = int(duration[0:-1])
            elif duration.endswith('h') or duration.endswith('H'):
                duration = int(duration[0:-1])*60
            else:
                duration = int(duration)

            # set the logger level to debug
            logger_config = lf_logger_config.lf_logger_config()

            if log_level:
                logger_config.set_level(level=log_level)

            if lf_logger_config_json:
                logger_config.lf_logger_config_json = lf_logger_config_json
                logger_config.load_lf_logger_config()

            mgr_ip = self.lanforge_ip
            mgr_port = self.port
            url = url
            duration = duration

            do_webUI = do_webUI
            ui_report_dir = ui_report_dir
            debug = debug
            # Print debug information if debugging is enabled
            if debug:
                logging.info('''Specified configuration:
                ip:                       {}
                port:                     {}
                Duration:                 {}
                debug:                    {}
                '''.format(mgr_ip, mgr_port, duration, debug))

            if True:
                if group_name is not None:
                    group_name = group_name.strip()
                    selected_groups = group_name.split(',')
                else:
                    selected_groups = []

                if profile_name is not None:
                    profile_name = profile_name.strip()
                    selected_profiles = profile_name.split(',')
                else:
                    selected_profiles = []


                Devices = RealDevice(manager_ip=mgr_ip,
                                    server_ip='192.168.1.61',
                                    ssid_2g='Test Configured',
                                    passwd_2g='',
                                    encryption_2g='',
                                    ssid_5g='Test Configured',
                                    passwd_5g='',
                                    encryption_5g='',
                                    ssid_6g='Test Configured',
                                    passwd_6g='',
                                    encryption_6g='',
                                    selected_bands=['5G'])
                Devices.get_devices()

                # Create a YouTube object with the specified parameters
                # upstream_port = "10.253.8.126"
                self.yt_test_obj = Youtube(
                    host=mgr_ip,
                    port=mgr_port,
                    url=url,
                    duration=duration,
                    lanforge_password='lanforge',
                    sta_list=[],
                    do_webUI=do_webUI,
                    ui_report_dir=ui_report_dir,
                    debug=debug,
                    resolution=res,
                    ap_name=ap_name,
                    ssid=ssid,
                    security=encryp,
                    band=band,
                    test_name=test_name,
                    upstream_port=upstream_port,
                    config=config,
                    selected_groups=selected_groups,
                    selected_profiles=selected_profiles,
                    )

                print('CHECKING PORT AVAILBILITY for YT TEST')
                self.port_clean_up(5002)
                self.yt_test_obj.start_flask_server()
                upstream_port = self.yt_test_obj.change_port_to_ip(upstream_port)

                resources = []
                self.yt_test_obj.Devices = Devices
                if file_name:
                    new_filename = file_name.removesuffix(".csv")
                else:
                    new_filename = file_name
                config_obj = DeviceConfig.DeviceConfig(lanforge_ip=self.lanforge_ip, file_name=new_filename)
                # if not expected_passfail_value and device_csv_name is None:
                #     config_obj.device_csv_file(csv_name="device.csv")
                if group_name is not None and file_name is not None and profile_name is not None:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    config_devices = {}
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]

                    config_obj.initiate_group()

                    asyncio.run(config_obj.connectivity(config_devices))

                    adbresponse = config_obj.adb_obj.get_devices()
                    resource_manager = config_obj.laptop_obj.get_devices()
                    all_res = {}
                    df1 = config_obj.display_groups(config_obj.groups)
                    groups_list = df1.to_dict(orient='list')
                    group_devices = {}

                    for adb in adbresponse:
                        group_devices[adb['serial']] = adb['eid']
                    for res in resource_manager:
                        all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
                    eid_list = []
                    for grp_name in groups_list.keys():
                        for g_name in selected_groups:
                            if grp_name == g_name:
                                for j in groups_list[grp_name]:
                                    if j in group_devices.keys():
                                        eid_list.append(group_devices[j])
                                    elif j in all_res.keys():
                                        eid_list.append(all_res[j])
                    resource_list = ",".join(id for id in eid_list)
                else:
                    config_dict = {
                        'ssid': ssid,
                        'passwd': passwd,
                        'enc': encryp,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee8021x,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': upstream_port,
                    }
                    if resource_list:
                        all_devices = config_obj.get_all_devices()
                        if group_name is None and file_name is None and profile_name is None:
                            dev_list = resource_list.split(',')
                            if config:
                                asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                    else:
                        all_devices = config_obj.get_all_devices()
                        device_list = []
                        for device in all_devices:
                            if device["type"] != 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                            elif device["type"] == 'laptop':
                                device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])

                        print("Available devices:")
                        for device in device_list:
                            print(device)

                        resource_list = input("Enter the desired resources to run the test:")
                        dev1_list = resource_list.split(',')
                        if config:
                            asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

                if not do_webUI:
                    if resource_list:
                        resources = [r.strip() for r in resource_list.split(',')]
                        resources = [r for r in resources if len(r.split('.')) > 1]

                        self.yt_test_obj.select_real_devices(real_devices=Devices, real_sta_list=resources, base_interop_obj=Devices)

                    else:
                        self.yt_test_obj.select_real_devices(real_devices=Devices)
                else:
                    resources = [r.strip() for r in resource_list.split(',')]

                    extracted_parts = [res.split('.')[:2] for res in resources]
                    formatted_parts = ['.'.join(parts) for parts in extracted_parts]
                    self.yt_test_obj.select_real_devices(real_devices=Devices, real_sta_list=formatted_parts, base_interop_obj=Devices)

                # Perform pre-test cleanup if not skipped
                if not no_pre_cleanup:
                    self.yt_test_obj.cleanup()

                # Check if the required tab exists, and exit if not
                if not self.yt_test_obj.check_tab_exists():
                    logging.error('Generic Tab is not available.\nAborting the test.')
                    return False

                if len(self.yt_test_obj.real_sta_list) > 0:
                    logging.info(f"checking real sta list while creating endpionts {self.yt_test_obj.real_sta_list}")
                    print('HII',self.yt_test_obj.real_sta_list)
                    self.yt_test_obj.create_generic_endp()
                else:
                    logging.info(f"checking real sta list while creating endpionts {self.yt_test_obj.real_sta_list}")
                    logging.error("No Real Devies Available")
                    return False

                if do_webUI:
                    self.yt_test_obj.update_webui()
                logging.info("TEST STARTED")
                logging.info('Running the youtube Streaming test for {} minutes'.format(duration))

                time.sleep(10)

                self.yt_test_obj.start_time = datetime.datetime.now()
                self.yt_test_obj.start_generic()
                logging.info(f"yt_test_obj: {self.yt_test_obj}")
                logging.info(f"generic_endps_profile: {getattr(self.yt_test_obj, 'generic_endps_profile', None)}")
                logging.info(f"device_names: {getattr(self.yt_test_obj, 'device_names', None)}")
                logging.info(f"stats_api_response: {getattr(self.yt_test_obj, 'stats_api_response', None)}")

                # duration = duration
                end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)
                initial_data = self.yt_test_obj.get_data_from_api()

                while not initial_data or len(initial_data) == 0:
                    initial_data = self.yt_test_obj.get_data_from_api()
                    time.sleep(1)
                if initial_data:
                    end_time_webgui = []
                    for i in range(len(self.yt_test_obj.device_names)):
                        end_time_webgui.append(initial_data['result'].get(self.yt_test_obj.device_names[i], {}).get('stop', False))
                else:
                    for i in range(len(self.yt_test_obj.device_names)):
                        end_time_webgui.append("")

                end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)

                while datetime.datetime.now() < end_time or not self.yt_test_obj.check_gen_cx():
                    self.yt_test_obj.get_data_from_api()
                    time.sleep(1)

                if getattr(self.yt_test_obj, "generic_endps_profile", None):
                    logger.info("Stopping all the endpoints")
                    self.yt_test_obj.generic_endps_profile.stop_cx()
                else:
                    logging.warning("⚠️ generic_endps_profile is None — skipping stop_cx()")
                logging.info("Duration ended")

                logging.info('Stopping the test')
                if do_webUI:
                    print("hii here data",self.yt_test_obj.stats_api_response)
                    self.yt_test_obj.create_report(self.yt_test_obj.stats_api_response, self.yt_test_obj.ui_report_dir)
                else:

                    self.yt_test_obj.create_report(self.yt_test_obj.stats_api_response, '')

                # Perform post-test cleanup if not skipped
                # if not no_post_cleanup:
                #     self.yt_test_obj.generic_endps_profile.cleanup()
        except Exception as e:
            logging.error(f"Error occured {e}")
            # traceback.print_exc()
        finally:
            if not ('--help' in sys.argv or '-h' in sys.argv):
                # traceback.print_exc()
                self.yt_test_obj.stop()
                if self.current_exec == "parallel":
                    self.yt_obj_dict["parallel"]["yt_test"]["obj"] =self.yt_test_obj
                else:
                    for i in range(len(self.yt_obj_dict["series"])):
                        if self.yt_obj_dict["series"][f"yt_test_{i+1}"]["obj"] is None:
                            self.yt_obj_dict["series"][f"yt_test_{i+1}"]["obj"] = self.yt_test_obj
                            break
                # Stopping the Youtube test
                if do_webUI:
                    self.yt_test_obj.stop_test_yt()
                if self.dowebgui:
                    self.webgui_test_done("yt")
                logging.info("Waiting for Cleanup of Browsers in Devices")
                time.sleep(10)
        return True

    def run_zoom_test(
            self,
        duration: int,
        signin_email: str,
        signin_passwd: str,
        participants: int,
        audio: bool = False,
        video: bool = False,
        wait_time: int = 30,
        log_level: str = None,
        lf_logger_config_json: str = None,
        resource_list: str = None,
        do_webUI: bool = False,
        report_dir: str = None,
        testname: str = None,
        zoom_host: str = None,
        file_name: str = None,
        group_name: str = None,
        profile_name: str = None,
        ssid: str = None,
        passwd: str = None,
        encryp: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = 'DEFAULT',
        ieee8021x: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = 'NA',
        private_key: str = 'NA',
        ca_cert: str = 'NA',
        client_cert: str = 'NA',
        pk_passwd: str = 'NA',
        pac_file: str = 'NA',
        upstream_port: str = 'NA',
        help_summary: str = None,
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        config: bool = False,
        exec_type: str = None,
        api_stats_collection: bool = False,
        env_file: str = None,
        account_id: str = None,
        client_id: str = None,
        client_secret: str = None
    ):
        try:
            lanforge_ip = self.lanforge_ip
            if self.dowebgui:
                if not self.webgui_stop_check("zoom"):
                    return False
            if True:

                if group_name is not None:
                    group_name = group_name.strip()
                    selected_groups = group_name.split(',')
                else:
                    selected_groups = []

                if profile_name is not None:
                    profile_name = profile_name.strip()
                    selected_profiles = profile_name.split(',')
                else:
                    selected_profiles = []

                # upstream_port = "10.253.8.126"
                self.zoom_test_obj = ZoomAutomation(audio=audio, video=video, lanforge_ip=lanforge_ip, wait_time=wait_time, testname=testname,
                                                upstream_port=upstream_port, config=config, selected_groups=selected_groups, selected_profiles=selected_profiles,
                                                api_stats_collection=api_stats_collection,participants_req=participants,
                                                signin_email=signin_email,signin_passwd=signin_passwd,duration=duration)
                upstream_port = self.zoom_test_obj.change_port_to_ip(upstream_port)
                realdevice = RealDevice(manager_ip=lanforge_ip,
                                        server_ip="192.168.1.61",
                                        ssid_2g='Test Configured',
                                        passwd_2g='',
                                        encryption_2g='',
                                        ssid_5g='Test Configured',
                                        passwd_5g='',
                                        encryption_5g='',
                                        ssid_6g='Test Configured',
                                        passwd_6g='',
                                        encryption_6g='',
                                        selected_bands=['5G'])
                laptops = realdevice.get_devices()
                print('CHECKING PORT AVAILBILITY for ZOOM TEST')
                self.port_clean_up(5000)

                if file_name:
                    new_filename = file_name.removesuffix(".csv")
                else:
                    new_filename = file_name
                config_obj = DeviceConfig.DeviceConfig(lanforge_ip=lanforge_ip, file_name=new_filename)

                # if not expected_passfail_value and device_csv_name is None:
                #     config_obj.device_csv_file(csv_name="device.csv")
                if group_name is not None and file_name is not None and profile_name is not None:
                    selected_groups = group_name.split(',')
                    selected_profiles = profile_name.split(',')
                    config_devices = {}
                    for i in range(len(selected_groups)):
                        config_devices[selected_groups[i]] = selected_profiles[i]

                    config_obj.initiate_group()
                    asyncio.run(config_obj.connectivity(config_devices))

                    adbresponse = config_obj.adb_obj.get_devices()
                    resource_manager = config_obj.laptop_obj.get_devices()
                    all_res = {}
                    df1 = config_obj.display_groups(config_obj.groups)
                    groups_list = df1.to_dict(orient='list')
                    group_devices = {}

                    for adb in adbresponse:
                        group_devices[adb['serial']] = adb['eid']
                    for res in resource_manager:
                        all_res[res['hostname']] = res['shelf'] + '.' + res['resource']
                    eid_list = []
                    for grp_name in groups_list.keys():
                        for g_name in selected_groups:
                            if grp_name == g_name:
                                for j in groups_list[grp_name]:
                                    if j in group_devices.keys():
                                        eid_list.append(group_devices[j])
                                    elif j in all_res.keys():
                                        eid_list.append(all_res[j])
                    if zoom_host in eid_list:
                        # Remove the existing instance of zoom_host from the list
                        eid_list.remove(zoom_host)
                        # Insert zoom_host at the beginning of the list
                        eid_list.insert(0, zoom_host)

                    resource_list = ",".join(id for id in eid_list)
                else:
                    config_dict = {
                        'ssid': ssid,
                        'passwd': passwd,
                        'enc': encryp,
                        'eap_method': eap_method,
                        'eap_identity': eap_identity,
                        'ieee80211': ieee8021x,
                        'ieee80211u': ieee80211u,
                        'ieee80211w': ieee80211w,
                        'enable_pkc': enable_pkc,
                        'bss_transition': bss_transition,
                        'power_save': power_save,
                        'disable_ofdma': disable_ofdma,
                        'roam_ft_ds': roam_ft_ds,
                        'key_management': key_management,
                        'pairwise': pairwise,
                        'private_key': private_key,
                        'ca_cert': ca_cert,
                        'client_cert': client_cert,
                        'pk_passwd': pk_passwd,
                        'pac_file': pac_file,
                        'server_ip': upstream_port,

                    }
                    if resource_list:
                        all_devices = config_obj.get_all_devices()
                        if group_name is None and file_name is None and profile_name is None:
                            dev_list = resource_list.split(',')
                            if not do_webUI:
                                zoom_host = zoom_host.strip()
                                if zoom_host in dev_list:
                                    dev_list.remove(zoom_host)
                                dev_list.insert(0, zoom_host)
                            if config:
                                asyncio.run(config_obj.connectivity(device_list=dev_list, wifi_config=config_dict))
                            resource_list = ",".join(id for id in dev_list)
                    else:
                        # If no resources provided, prompt user to select devices manually
                        if config:
                            all_devices = config_obj.get_all_devices()
                            device_list = []
                            for device in all_devices:
                                if device["type"] != 'laptop':
                                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["serial"])
                                elif device["type"] == 'laptop':
                                    device_list.append(device["shelf"] + '.' + device["resource"] + " " + device["hostname"])
                            print("Available Devices For Testing")
                            for device in device_list:
                                print(device)
                            zm_host = input("Enter Host Resource for the Test : ")
                            zm_host = zm_host.strip()
                            resource_list = input("Enter client Resources to run the test :")
                            resource_list = zm_host + "," + resource_list
                            dev1_list = resource_list.split(',')
                            asyncio.run(config_obj.connectivity(device_list=dev1_list, wifi_config=config_dict))

                result_list = []
                if not do_webUI:
                    if resource_list:
                        resources = resource_list.split(',')
                        resources = [r for r in resources if len(r.split('.')) > 1]
                        # resources = sorted(resources, key=lambda x: int(x.split('.')[1]))
                        get_data = self.zoom_test_obj.select_real_devices(real_device_obj=realdevice, real_sta_list=resources)
                        for item in get_data:
                            item = item.strip()
                            # Find and append the matching lap to result_list
                            matching_laps = [lap for lap in laptops if lap.startswith(item)]
                            result_list.extend(matching_laps)
                        if not result_list:
                            logging.info("Resources donot exist hence Terminating the test.")
                            return
                        if len(result_list) != len(get_data):
                            logging.info("Few Resources donot exist")
                    else:
                        resources = self.zoom_test_obj.select_real_devices(real_device_obj=realdevice)
                else:
                    if do_webUI:
                        self.zoom_test_obj.path = report_dir
                    resources = resource_list.split(',')
                    extracted_parts = [res.split('.')[:2] for res in resources]
                    formatted_parts = ['.'.join(parts) for parts in extracted_parts]

                    self.zoom_test_obj.select_real_devices(real_device_obj=realdevice, real_sta_list=formatted_parts)
                    if do_webUI:

                        if len(self.zoom_test_obj.real_sta_hostname) == 0:
                            logging.info("No device is available to run the test")
                            obj = {
                                "status": "Stopped",
                                "configuration_status": "configured"
                            }
                            self.zoom_test_obj.updating_webui_runningjson(obj)
                            return False
                        else:
                            obj = {
                                "configured_devices": self.zoom_test_obj.real_sta_hostname,
                                "configuration_status": "configured",
                                "no_of_devices": f' Total({len(self.zoom_test_obj.real_sta_os_type)}) : W({self.zoom_test_obj.windows}),L({self.zoom_test_obj.linux}),M({self.zoom_test_obj.mac})',
                                "device_list": self.zoom_test_obj.hostname_os_combination,
                                # "zoom_host":self.zoom_test_obj.zoom_host

                            }
                            self.zoom_test_obj.updating_webui_runningjson(obj)

                if not self.zoom_test_obj.check_tab_exists():
                    logging.error('Generic Tab is not available.\nAborting the test.')
                    return False

                self.zoom_test_obj.handle_flask_server()
                self.zoom_test_obj.get_resource_data()
                self.zoom_test_obj.get_ports_data()
                self.zoom_test_obj.get_interop_data()

                if api_stats_collection:
                    if env_file:
                        if os.path.exists(env_file):
                            load_dotenv(env_file)
                            print(f"Loaded environment variables from {env_file}")
                        else:
                            raise FileNotFoundError(f"Environment file {env_file} not found.")

                    # Fetching zoom credentials for account
                    self.zoom_test_obj.account_id = account_id or os.environ.get(
                        "ACCOUNT_ID"
                    )
                    self.zoom_test_obj.client_id = client_id or os.environ.get(
                        "CLIENT_ID"
                    )
                    self.zoom_test_obj.client_secret = client_secret or os.environ.get(
                        "CLIENT_SECRET"
                    )

                    if not all(
                        [
                            self.zoom_test_obj.account_id,
                            self.zoom_test_obj.client_id,
                            self.zoom_test_obj.client_secret,
                        ]
                    ):
                        logger.info("Exiting test.")
                        raise ValueError(
                            "Missing Zoom API credentials. Please provide ACCOUNT_ID, CLIENT_ID, and CLIENT_SECRET as environment variables or through function arguments."
                        )
                if self.robot_test:
                    self.zoom_test_obj.report_path_date_time = os.path.join(os.getcwd() , "zoom_test_results")
                    self.zoom_test_obj.run_robo_test()
                else:
                    self.zoom_test_obj.run()
                    # self.zoom_test_obj.run(duration, upstream_port, signin_email, signin_passwd, participants)

                self.zoom_test_obj.data_store.clear()
                if not api_stats_collection:
                    self.zoom_test_obj.generate_report()
                logging.info("Test Completed Sucessfully")
        except Exception as e:
            logging.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
            # traceback.print_exc()
        finally:
            if not ('--help' in sys.argv or '-h' in sys.argv):
                
                # self.zoom_test_obj.redis_client.set('login_completed', 0)
                self.zoom_test_obj.stop_signal = True
                logger.info("Waiting for Browser Cleanup in Laptops")
                time.sleep(10)
                self.zoom_test_obj.app = None
                if self.zoom_test_obj.do_webui:
                    self.zoom_test_obj.stop_webui()
                
                if self.robot_test and api_stats_collection:
                    self.zoom_test_obj.generate_report_from_data()
                elif api_stats_collection:
                    self.zoom_test_obj.generate_report_from_api()
                # self.zoom_test_obj.redis_client = None
                if self.dowebgui:
                    self.webgui_test_done("zoom")
                if self.current_exec == "parallel":
                    self.zoom_obj_dict["parallel"]["zoom_test"]["obj"] =self.zoom_test_obj
                else:
                    for i in range(len(self.zoom_obj_dict["series"])):
                        if self.zoom_obj_dict["series"][f"zoom_test_{i+1}"]["obj"] is None:
                            self.zoom_obj_dict["series"][f"zoom_test_{i+1}"]["obj"] = self.zoom_test_obj
                            break
                logging.info("Waiting for Browser Cleanup in Laptops")
                self.zoom_test_obj.generic_endps_profile.cleanup()
                # self.zoom_test_obj.generic_endps_profile.cleanup()
                time.sleep(10)

        return True

    def run_teams_test(
            self,
        duration: int,
        participants_req: int,
        audio: bool = False,
        video: bool = False,
        upstream_port: str = 'NA',
        resource_list: str = None,
        do_webUI: bool = False,
        report_dir: str = None,
        testname: str = None
    ):
        try:
            lanforge_ip = self.lanforge_ip
            if self.dowebgui:
                if not self.webgui_stop_check("teams"):
                    return False
            if True:
                self.teams_test_obj = TeamsAutomation(audio=audio, video=video, lanforge_ip=lanforge_ip, test_name=testname, duration=duration,participants_req=participants_req, upstream_port=upstream_port, do_webui=do_webUI, report_dir=report_dir)
                self.port_clean_up(5005)
                upstream_port_teams=self.teams_test_obj.change_port_to_ip(upstream_port)
                self.teams_test_obj.upstream_port=upstream_port_teams
                self.teams_test_obj.realdevice = RealDevice(manager_ip=lanforge_ip,
                                                            server_ip="",
                                                            ssid_2g='Test Configured',
                                                            passwd_2g='',
                                                            encryption_2g='',
                                                            ssid_5g='Test Configured',
                                                            passwd_5g='',
                                                            encryption_5g='',
                                                            ssid_6g='Test Configured',
                                                            passwd_6g='',
                                                            encryption_6g='',
                                                            selected_bands=['5G'])
                self.teams_test_obj.select_real_devices(real_sta_list=resource_list)
                if do_webUI:
                    self.teams_test_obj.path = report_dir
                    self.teams_test_obj.update_webui_data()
                self.teams_test_obj.load_credentials()
                self.teams_test_obj.run()
                time.sleep(10)
                self.teams_test_obj.create_avg_data()
                self.teams_test_obj.execute_finally = True
            
        except Exception as e:
            logging.error(f"AN ERROR OCCURED WHILE RUNNING TEST {e}")
            traceback.print_exc()
        finally:
            if not ("--help" in sys.argv or "-h" in sys.argv):
                if self.teams_test_obj.execute_finally:
                    self.teams_test_obj.app = None
                    self.teams_test_obj.stop_signal = True
                    self.teams_test_obj.generate_report()
                    self.teams_test_obj.move_csv_files()
                    if do_webUI:
                        self.webgui_test_done("teams")
                        self.teams_test_obj.stop_test_in_webui()
                    if self.current_exec == "parallel":
                        self.teams_obj_dict["parallel"]["teams_test"]["obj"] =self.teams_test_obj
                    else:
                        for i in range(len(self.teams_obj_dict["series"])):
                            if self.teams_obj_dict["series"][f"teams_test_{i+1}"]["obj"] is None:
                                self.teams_obj_dict["series"][f"teams_test_{i+1}"]["obj"] = self.teams_test_obj
                                break
                    logger.info("Waiting for Browser Cleanup at Client Side")
                    if not self.teams_test_obj.no_post_cleanup:
                        self.teams_test_obj.generic_endps_profile.cleanup()
                    time.sleep(10)
                    logger.info("Browser Cleanup Completed")
                    logger.info("Test Completed")
        return True
                


    def run_rb_test1(self,args):
        try:
            if self.dowebgui:
                if not self.webgui_stop_check("rb"):
                    return False
            logger_config = lf_logger_config.lf_logger_config()

            if args.log_level:
                logger_config.set_level(level=args.log_level)

            if args.lf_logger_config_json:
                logger_config.lf_logger_config_json = args.lf_logger_config_json
                logger_config.load_lf_logger_config()
            if args.url.lower().startswith("www."):
                args.url = "https://" + args.url
            if args.url.lower().startswith("http://"):
                args.url = "https://" + args.url.removeprefix("http://")
            self.rb_test = RealBrowserTest(host=args.host,
                                ssid=args.ssid,
                                passwd=args.passwd,
                                encryp=args.encryp,
                                suporrted_release=["7.0", "10", "11", "12"],
                                max_speed=args.max_speed,
                                url=args.url, count=args.count,
                                duration=args.duration,
                                resource_ids=args.device_list,
                                dowebgui=args.dowebgui,
                                result_dir=args.result_dir,
                                test_name=args.test_name,
                                incremental=args.incremental,
                                no_postcleanup=args.no_postcleanup,
                                no_precleanup=args.no_precleanup,
                                file_name=args.file_name,
                                group_name=args.group_name,
                                profile_name=args.profile_name,
                                eap_method=args.eap_method,
                                eap_identity=args.eap_identity,
                                ieee80211=args.ieee80211,
                                ieee80211u=args.ieee80211u,
                                ieee80211w=args.ieee80211w,
                                enable_pkc=args.enable_pkc,
                                bss_transition=args.bss_transition,
                                power_save=args.power_save,
                                disable_ofdma=args.disable_ofdma,
                                roam_ft_ds=args.roam_ft_ds,
                                key_management=args.key_management,
                                pairwise=args.pairwise,
                                private_key=args.private_key,
                                ca_cert=args.ca_cert,
                                client_cert=args.client_cert,
                                pk_passwd=args.pk_passwd,
                                pac_file=args.pac_file,
                                upstream_port=args.upstream_port,
                                expected_passfail_value=args.expected_passfail_value,
                                device_csv_name=args.device_csv_name,
                                wait_time=args.wait_time,
                                config=args.config,
                                selected_groups=args.group_name,
                                selected_profiles=args.profile_name,
                                )
            print('CHECKING PORT AVAILBILITY for RB TEST')
            self.port_clean_up(5003)
            self.rb_test.change_port_to_ip()
            self.rb_test.validate_and_process_args()
            self.rb_test.config_obj = DeviceConfig.DeviceConfig(lanforge_ip=self.rb_test.host, file_name=self.rb_test.file_name, wait_time=self.rb_test.wait_time)
            # if not self.rb_test.expected_passfail_value and self.rb_test.device_csv_name is None:
            #     self.rb_test.config_self.rb_test.device_csv_file(csv_name="device.csv")
            self.rb_test.run_flask_server()
            if self.rb_test.group_name and self.rb_test.profile_name and self.rb_test.file_name:
                available_resources = self.rb_test.process_group_profiles()
            else:
                # --- Build configuration dictionary for WiFi parameters ---
                config_dict = {
                    'ssid': args.ssid,
                    'passwd': args.passwd,
                    'enc': args.encryp,
                    'eap_method': args.eap_method,
                    'eap_identity': args.eap_identity,
                    'ieee80211': args.ieee80211,
                    'ieee80211u': args.ieee80211u,
                    'ieee80211w': args.ieee80211w,
                    'enable_pkc': args.enable_pkc,
                    'bss_transition': args.bss_transition,
                    'power_save': args.power_save,
                    'disable_ofdma': args.disable_ofdma,
                    'roam_ft_ds': args.roam_ft_ds,
                    'key_management': args.key_management,
                    'pairwise': args.pairwise,
                    'private_key': args.private_key,
                    'ca_cert': args.ca_cert,
                    'client_cert': args.client_cert,
                    'pk_passwd': args.pk_passwd,
                    'pac_file': args.pac_file,
                    'server_ip': self.rb_test.upstream_port,
                }
                available_resources = self.rb_test.process_resources(config_dict)
            if len(available_resources) != 0:
                available_resources = self.rb_test.filter_ios_devices(available_resources)
            if len(available_resources) == 0:
                logging.error("No devices available to run the test. Exiting...")
                return False

            # --- Print available resources ---
            logging.info("Devices available: {}".format(available_resources))
            if self.rb_test.expected_passfail_value or self.rb_test.device_csv_name:
                self.rb_test.update_passfail_value(available_resources)
            # --- Handle incremental values ---
            self.rb_test.handle_incremental(args, self.rb_test, available_resources, available_resources)
            self.rb_test.handle_duration()
            self.rb_test.run_test(available_resources)

        except Exception as e:
            logging.error("Error occured", e)
            # traceback.print_exc()
        finally:
            if '--help' not in sys.argv and '-h' not in sys.argv:
                self.rb_test.create_report()
                if self.rb_test.dowebgui:
                    self.rb_test.webui_stop()
                self.rb_test.stop()

                # if not args.no_postcleanup:
                #     self.rb_test_obj.postcleanup()
            if self.dowebgui:
                self.webgui_test_done("rb")
            self.rb_test.app = None
            if self.current_exec == "parallel":
                self.rb_obj_dict["parallel"]["rb_test"]["obj"] =self.rb_test
            else:
                for i in range(len(self.rb_obj_dict["series"])):
                    if self.rb_obj_dict["series"][f"rb_test_{i+1}"]["obj"] is None:
                        self.rb_obj_dict["series"][f"rb_test_{i+1}"]["obj"] = self.rb_test
                        break



        return True


    def run_rb_test(
        self,
        ssid: str = None,
        passwd: str = None,
        encryp: str = None,
        url: str = "https://google.com",
        max_speed: int = 0,
        count: int = 1,
        duration: str = None,
        test_name: str = None,
        dowebgui: bool = False,
        result_dir: str = '',
        lf_logger_config_json: str = None,
        log_level: str = None,
        debug: bool = False,
        device_list: str = None,
        webgui_incremental: str = None,
        incremental: bool = False,
        no_laptops: bool = False,
        no_postcleanup: bool = False,
        no_precleanup: bool = False,
        file_name: str = None,
        group_name: str = None,
        profile_name: str = None,
        eap_method: str = 'DEFAULT',
        eap_identity: str = 'DEFAULT',
        ieee80211: bool = False,
        ieee80211u: bool = False,
        ieee80211w: int = 1,
        enable_pkc: bool = False,
        bss_transition: bool = False,
        power_save: bool = False,
        disable_ofdma: bool = False,
        roam_ft_ds: bool = False,
        key_management: str = 'DEFAULT',
        pairwise: str = 'NA',
        private_key: str = 'NA',
        ca_cert: str = 'NA',
        client_cert: str = 'NA',
        pk_passwd: str = 'NA',
        pac_file: str = 'NA',
        upstream_port: str = 'NA',
        help_summary: str = None,
        expected_passfail_value: str = None,
        device_csv_name: str = None,
        wait_time: int = 60,
        config: bool = False,
        exec_type: str = None,
    ):
        args = SimpleNamespace(**locals())
        args.host = self.lanforge_ip
        return self.run_rb_test1(args)
    
    def run_vlc_test(
        self,
        mcast_addr="239.255.0.1",
        mcast_port="1234",
        host_res=None,
        video_name=None,
        duration=60,
        server_ip="0.0.0.0",
        server_port=5959,
        help_summary=None,
        device_list=None
    ):
        device_list = device_list if device_list else []
        ce = self.current_exec #seires
        if ce == "parallel":
            obj_name = "vlc_test"
        else:
            obj_no = 1
            while f"vlc_test_{obj_no}" in self.vlc_obj_dict[ce]:
                obj_no+=1 
            obj_name = f"vlc_test_{obj_no}" 
        mgr = self.lanforge_ip
        vlc_stream_obj = VLCStream(manager_ip=mgr,mcast_addr=mcast_addr,mcast_port=mcast_port,video_name=video_name,host_res=host_res,duration=duration,fserver=server_ip,fport=server_port,device_list=device_list)
        vlc_stream_obj.run_flask_server()
        vlc_stream_obj.get_resource_data()
        vlc_stream_obj.create()
        vlc_stream_obj.start_generic()
        print("starting test")
        print(vlc_stream_obj.start_time)
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=duration)
        while datetime.datetime.now()<end:
            time.sleep(1)
        time.sleep(20)

        vlc_stream_obj.stop_generic()
        print(vlc_stream_obj.stats)
        vlc_stream_obj.app = None
        if self.current_exec == "parallel":
            self.vlc_obj_dict["parallel"]["vlc_test"]["obj"] =vlc_stream_obj
        else:
            for i in range(len(self.vlc_obj_dict["series"])):
                if self.vlc_obj_dict["series"][f"vlc_test_{i+1}"]["obj"] is None:
                    self.vlc_obj_dict["series"][f"vlc_test_{i+1}"]["obj"] = vlc_stream_obj
                    break
        vlc_stream_obj.create_report()
        return True


    def browser_cleanup(self,rb_test=False,yt_test=False):
        # count = 0
        # series_tests = args.series_tests.split(',') if args.series_tests else None
        # parallel_tests = args.parallel_tests.split(',') if args.parallel_tests else None
        # zoom_test = False
        # yt_test = False
        # rb_test = False
        # if 'zoom_test' in parallel_tests:
        #     count += 1
        # if 'yt_test' in parallel_tests:
        #     count += 1
        # if 'rb_test' in parallel_tests:
        #     count += 1
        # if count <=1:
        #     self.browser_kill = True
        # if args.series_test and not parallel_tests:
        #     self.browser_kill = True
        #     return True
        # if rb_test:
        #     cnt = 0
        #     flag = False 
        #     while not self.rb_build_done:
        #         time.sleep(1)
        #         cnt+=1
        #         if cnt >= 30:
        #             flag = True 
        #             break
        #     if flag:
        #         return False
        print('calledddddd')
        # time.sleep(20)
        if rb_test:
            print('inn000')
            print('laptop_os_types',self.rb_test_obj.laptop_os_types)
            print('endpsss',self.rb_test_obj.generic_endps_profile.created_endp)
            for i in range(0, len(self.rb_test_obj.laptop_os_types)):
                print('inn1111')
                if self.rb_test_obj.laptop_os_types[i] == 'windows':
                    cmd = "echo Performing POST cleanup of browser processes... & taskkill /F /IM chrome.exe /T >nul 2>&1 & taskkill /F /IM chromedriver.exe /T >nul 2>&1 & echo Browser processes terminated."
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.rb_test_obj.laptop_os_types[i] == 'linux':
                    # cmd = "su -l lanforge  ctrb.bash %s %s %s %s" % (self.rb_test_obj.new_port_list[i], self.rb_test_obj.url, self.rb_test_obj.upstream_port, self.rb_test_obj.duration)
                    cmd = "pkill -f chrome; pkill -f chromedriver"
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.rb_test_obj.laptop_os_types[i] == 'macos':
                    cmd = "pkill -f Google Chrome; pkill -f chromedriver;"
                    self.rb_test_obj.generic_endps_profile.set_cmd(self.rb_test_obj.generic_endps_profile.created_endp[i], cmd)
                    if self.rb_test_obj.browser_precleanup:
                        cmd+=" precleanup"
                    if self.rb_test_obj.browser_postcleanup:
                        cmd+=" postcleanup"

            for i, cx_batch in enumerate(self.rb_test_obj.cx_order_list):
                self.rb_test_obj.start_specific(cx_batch)
                logging.info(f"browser cleanup on {cx_batch}")
            print('realbrowser test laptop cleaing.....')
            time.sleep(20)  
            
        
        if yt_test:
            for i in range(0, len(self.yt_test_obj.real_sta_os_types)):
                if self.yt_test_obj.real_sta_os_types[i] == 'windows':
                    cmd = "echo Performing POST cleanup of browser processes... & taskkill /F /IM chrome.exe /T >nul 2>&1 & taskkill /F /IM chromedriver.exe /T >nul 2>&1 & echo Browser processes terminated."
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)
                elif self.yt_test_obj.real_sta_os_types[i] == 'linux':
                    cmd = "pkill -f chrome; pkill -f chromedriver"
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)

                elif self.yt_test_obj.real_sta_os_types[i] == 'macos':
                    cmd = "pkill -f Google Chrome; pkill -f chromedriver;"
                    self.yt_test_obj.generic_endps_profile.set_cmd(self.yt_test_obj.generic_endps_profile.created_endp[i], cmd)

            self.yt_test_obj.generic_endps_profile.start_cx()
            print('youtube test laptop cleaing.....')
            time.sleep(20)  

        # if zoom_test:
        #     for i in range(len(self.zoom_test_obj.real_sta_os_type)):
        #         if self.zoom_test_obj.real_sta_os_type[i] == "windows":
        #             cmd = f"py zoom_client.py --ip {self.zoom_test_obj.upstream_port}"
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)
        #         elif self.zoom_test_obj.real_sta_os_type[i] == 'linux':
        #             cmd = "su -l lanforge ctzoom.bash %s %s %s" % (self.zoom_test_obj.new_port_list[i], self.zoom_test_obj.upstream_port, "client")
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)
        #         elif self.zoom_test_obj.real_sta_os_type[i] == 'macos':
        #             cmd = "sudo bash ctzoom.bash %s %s" % (self.zoom_test_obj.upstream_port, "client")
        #             self.zoom_test_obj.generic_endps_profile.set_cmd(self.zoom_test_obj.generic_endps_profile.created_endp[i], cmd)

        #     self.zoom_test_obj.generic_endps_profile.start_cx()
    
    def build_iot_report_section(self, report, iot_summary):
        """
        Handles all IoT-related charts, tables, and increment-wise reports.
        """
        outdir = report.path_date_time
        os.makedirs(outdir, exist_ok=True)

        def copy_into_report(raw_path, new_name):
            """Resolve and copy image into report dir."""
            if not raw_path:
                return None

            abs_src = os.path.abspath(raw_path)
            if not os.path.exists(abs_src):
                # Search recursively under 'results' if absolute path missing
                for root, _, files in os.walk(os.path.join(os.getcwd(), "results")):
                    if os.path.basename(raw_path) in files:
                        abs_src = os.path.join(root, os.path.basename(raw_path))
                        break
                else:
                    return None

            dst = os.path.join(outdir, new_name)
            if os.path.abspath(abs_src) != os.path.abspath(dst):
                shutil.copy2(abs_src, dst)
            return new_name

        # section header
        report.set_custom_html('<div style="page-break-before: always;"></div>')
        report.build_custom()
        report.set_custom_html('<h2><u>IoT Results</u></h2>')
        report.build_custom()

        # Statistics
        stats_png = copy_into_report(iot_summary.get("statistics_img"), "iot_statistics.png")
        if stats_png:
            report.build_chart_title("Test Statistics")
            report.set_custom_html(f'<img src="{stats_png}" style="width:100%; height:auto;">')
            report.build_custom()

        # Request vs Latency
        rvl_png = copy_into_report(iot_summary.get("req_vs_latency_img"), "iot_request_vs_latency.png")
        if rvl_png:
            report.build_chart_title("Request vs Average Latency")
            report.set_custom_html(f'<img src="{rvl_png}" style="width:100%;">')
            report.build_custom()

        # Overall results table
        ort = iot_summary.get("overall_result_table") or {}
        if ort:
            rows = [{
                "Device": dev,
                "Min Latency (ms)": stats.get("min_latency"),
                "Avg Latency (ms)": stats.get("avg_latency"),
                "Max Latency (ms)": stats.get("max_latency"),
                "Total Iterations": stats.get("total_iterations"),
                "Success Iters": stats.get("success_iterations"),
                "Failed Iters": stats.get("failed_iterations"),
                "No-Response Iters": stats.get("no_response_iterations"),
            } for dev, stats in ort.items()]

            df_overall = pd.DataFrame(rows).round(2)

            report.set_custom_html('<div style="page-break-inside: avoid;">')
            report.build_custom()
            report.set_obj_html(_obj_title="Overall IoT Result Table", _obj=" ")
            report.build_objective()
            report.set_table_dataframe(df_overall)
            report.build_table()
            report.set_custom_html('</div>')
            report.build_custom()

        # Increment reports
        inc = iot_summary.get("increment_reports") or {}
        if inc:
            report.set_custom_html('<h3>Reports by Increment Steps</h3>')
            report.build_custom()

            for step_name, rep in inc.items():

                report.set_custom_html(f'<h4><u>{step_name.replace("_", " ")}</u></h4>')
                report.build_custom()

                # Latency graph
                lat_png = copy_into_report(rep.get("latency_graph"), f"iot_{step_name}_latency.png")
                if lat_png:
                    report.build_chart_title("Average Latency")
                    report.set_custom_html(f'<img src="{lat_png}" style="width:100%; height:auto;">')
                    report.build_custom()

                # Success count graph
                res_png = copy_into_report(rep.get("result_graph"), f"iot_{step_name}_results.png")
                if res_png:
                    report.build_chart_title("Success Count")
                    report.set_custom_html(f'<img src="{res_png}" style="width:100%; height:auto;">')
                    report.build_custom()

                # Tabular data for detailed iteration-level results
                data_rows = rep.get("data") or []
                if data_rows:
                    df = pd.DataFrame(data_rows).rename(
                        columns={"latency__ms": "Latency_ms", "latency_ms": "Latency_ms"}
                    )
                    if "Latency_ms" in df.columns:
                        df["Latency_ms"] = pd.to_numeric(df["Latency_ms"], errors="coerce").round(3)
                    if "Result" in df.columns:
                        df["Result"] = df["Result"].map(lambda x: "Success" if bool(x) else "Failure")

                    desired_cols = ["Iteration", "Device", "Current State", "Latency_ms", "Result"]
                    df = df[[c for c in desired_cols if c in df.columns]]

                    report.set_table_dataframe(df)
                    report.build_table()

                report.set_custom_html('<hr>')
                report.build_custom()

    def render_each_test(self,ce):
        # ce = "series"
        unq_tests = []
        test_map = {}
        print('self.rb_obj_dict',self.rb_obj_dict)
        print('self.yt_obj_dict',self.yt_obj_dict)
        if ce == "series":
            series_tests = self.series_tests.copy()
            print("series tests",series_tests)
            for test in series_tests:
                if test not in test_map:
                    test_map[test] = 1
                    unq_tests.append(test)
                else:
                    test_map[test] += 1
        else:
            unq_tests = self.parallel_tests.copy()
        print('self.series_tests',self.series_tests)
        print('test_map',test_map)
        print('unq_tests',unq_tests)
        print("self parallel tests",self.parallel_tests)
        print("ping obj dict",self.ping_obj_dict)

        for test_name in unq_tests:
            try:
                if test_name == "http_test":
                    # obj = []
                    obj_no = 1
                    obj_name = 'http_test'
                    if ce == "series":
                        obj_name += "_1" 
                    while obj_name in self.http_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        # report_path = self.result_path
                        # print("Current working directory:", os.getcwd())
                        http_data = self.http_obj_dict[ce][obj_name]["data"]
                        if http_data["bands"] == "Both":
                            num_stations = num_stations * 2

                        self.overall_report.set_obj_html(_obj_title=f'HTTP Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Setup Information")
                        self.overall_report.build_table_title()
                        self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=http_data["test_setup_info"])

                        graph2 = self.http_obj_dict[ce][obj_name]["obj"].graph_2(http_data["dataset2"], lis=http_data["lis"], bands=http_data["bands"],graph_name=obj_no)
                        print("graph name {}".format(graph2))
                        self.overall_report.set_graph_image(graph2)
                        self.overall_report.set_csv_filename(graph2)
                        self.overall_report.move_csv_file()
                        self.overall_report.move_graph_image()
                        self.overall_report.build_graph()

                        self.overall_report.set_obj_html(
                            "Average time taken to download file ",
                            "The below graph represents average time taken to download for each client  "
                            ".  X- axis shows “Average time taken to download a file ” and Y-axis shows "
                            "Client names."
                        )
                        self.overall_report.build_objective()

                        graph = self.http_obj_dict[ce][obj_name]["obj"].generate_graph(dataset=http_data["dataset"], lis=http_data["lis"], bands=http_data["bands"],graph_image_name=obj_no)
                        self.overall_report.set_graph_image(graph)
                        self.overall_report.set_csv_filename(graph)
                        self.overall_report.move_csv_file()
                        self.overall_report.move_graph_image()
                        self.overall_report.build_graph()

                        self.overall_report.set_obj_html(
                            "Download Time Table Description",
                            "This Table will provide you information of the "
                            "minimum, maximum and the average time taken by clients to download a webpage in seconds"
                        )
                        self.overall_report.build_objective()

                        self.http_obj_dict[ce][obj_name]["obj"].response_port = self.http_obj_dict[ce][obj_name]["obj"].local_realm.json_get("/port/all")
                        self.http_obj_dict[ce][obj_name]["obj"].channel_list, self.http_obj_dict[ce][obj_name]["obj"].mode_list, self.http_obj_dict[ce][obj_name]["obj"].ssid_list = [], [], []

                        if self.http_obj_dict[ce][obj_name]["obj"].client_type == "Real":
                            self.http_obj_dict[ce][obj_name]["obj"].devices = self.http_obj_dict[ce][obj_name]["obj"].devices_list
                            for interface in self.http_obj_dict[ce][obj_name]["obj"].response_port['interfaces']:
                                for port, port_data in interface.items():
                                    if port in self.http_obj_dict[ce][obj_name]["obj"].port_list:
                                        self.http_obj_dict[ce][obj_name]["obj"].channel_list.append(str(port_data['channel']))
                                        self.http_obj_dict[ce][obj_name]["obj"].mode_list.append(str(port_data['mode']))
                                        self.http_obj_dict[ce][obj_name]["obj"].ssid_list.append(str(port_data['ssid']))
                        elif self.http_obj_dict[ce][obj_name]["obj"].client_type == "Virtual":
                            self.http_obj_dict[ce][obj_name]["obj"].devices = self.http_obj_dict[ce][obj_name]["obj"].station_list[0]
                            for interface in self.http_obj_dict[ce][obj_name]["obj"].response_port['interfaces']:
                                for port, port_data in interface.items():
                                    if port in self.http_obj_dict[ce][obj_name]["obj"].station_list[0]:
                                        self.http_obj_dict[ce][obj_name]["obj"].channel_list.append(str(port_data['channel']))
                                        self.http_obj_dict[ce][obj_name]["obj"].mode_list.append(str(port_data['mode']))
                                        self.http_obj_dict[ce][obj_name]["obj"].macid_list.append(str(port_data['mac']))
                                        self.http_obj_dict[ce][obj_name]["obj"].ssid_list.append(str(port_data['ssid']))

                        # Processing result_data
                        z, z1, z2 = [], [], []
                        for fcc in list(http_data["result_data"].keys()):
                            z.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["min"]])
                            z1.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["max"]])
                            z2.extend([str(round(i / 1000, 1)) for i in http_data["result_data"][fcc]["avg"]])

                        download_table_value_dup = {"Minimum": z, "Maximum": z1, "Average": z2}
                        download_table_value = {"Band": http_data["bands"], "Minimum": z, "Maximum": z1, "Average": z2}

                        # KPI reporting
                        kpi_path = self.overall_report.get_report_path()
                        print("kpi_path :{kpi_path}".format(kpi_path=kpi_path))

                        kpi_csv = lf_kpi_csv.lf_kpi_csv(
                            _kpi_path=kpi_path,
                            _kpi_test_rig=http_data["test_rig"],
                            _kpi_test_tag=http_data["test_tag"],
                            _kpi_dut_hw_version=http_data["dut_hw_version"],
                            _kpi_dut_sw_version=http_data["dut_sw_version"],
                            _kpi_dut_model_num=http_data["dut_model_num"],
                            _kpi_dut_serial_num=http_data["dut_serial_num"],
                            _kpi_test_id=http_data["test_id"]
                        )
                        kpi_csv.kpi_dict['Units'] = "Mbps"
                        for band in range(len(download_table_value["Band"])):
                            kpi_csv.kpi_csv_get_dict_update_time()
                            kpi_csv.kpi_dict['Graph-Group'] = "Webpage Download {band}".format(
                                band=download_table_value['Band'][band])
                            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Minimum".format(
                                band=download_table_value['Band'][band])
                            kpi_csv.kpi_dict['numeric-score'] = "{min}".format(min=download_table_value['Minimum'][band])
                            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

                            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Maximum".format(
                                band=download_table_value['Band'][band])
                            kpi_csv.kpi_dict['numeric-score'] = "{max}".format(max=download_table_value['Maximum'][band])
                            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

                            kpi_csv.kpi_dict['short-description'] = "Webpage download {band} Average".format(
                                band=download_table_value['Band'][band])
                            kpi_csv.kpi_dict['numeric-score'] = "{avg}".format(avg=download_table_value['Average'][band])
                            kpi_csv.kpi_csv_write_dict(kpi_csv.kpi_dict)

                        if http_data["csv_outfile"] is not None:
                            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                            http_data["csv_outfile"] = "{}_{}-test_l3_longevity.csv".format(http_data["csv_outfile"], current_time)
                            http_data["csv_outfile"] = self.overall_report.file_add_path(http_data["csv_outfile"])
                            print("csv output file : {}".format(http_data["csv_outfile"]))

                        test_setup = pd.DataFrame(download_table_value_dup)
                        self.overall_report.set_table_dataframe(test_setup)
                        self.overall_report.build_table()

                        if self.http_obj_dict[ce][obj_name]["obj"].group_name:
                            self.overall_report.set_table_title("Overall Results for Groups")
                        else:
                            self.overall_report.set_table_title("Overall Results")
                        self.overall_report.build_table_title()

                        if self.http_obj_dict[ce][obj_name]["obj"].client_type == "Real":
                            if self.http_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.http_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                test_input_list, pass_fail_list = self.http_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(http_data["dataset2"])

                            if self.http_obj_dict[ce][obj_name]["obj"].group_name:
                                for key, val in self.http_obj_dict[ce][obj_name]["obj"].group_device_map.items():
                                    if self.http_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.http_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                        dataframe = self.http_obj_dict[ce][obj_name]["obj"].generate_dataframe(
                                            val, self.http_obj_dict[ce][obj_name]["obj"].devices, self.http_obj_dict[ce][obj_name]["obj"].macid_list, self.http_obj_dict[ce][obj_name]["obj"].channel_list,
                                            self.http_obj_dict[ce][obj_name]["obj"].ssid_list, self.http_obj_dict[ce][obj_name]["obj"].mode_list, http_data["dataset2"], test_input_list,
                                            http_data["dataset"], http_data["dataset1"], http_data["rx_rate"], pass_fail_list, self.http_obj_dict[ce][obj_name]["obj"].data["total_err"]
                                        )
                                    else:
                                        dataframe = self.http_obj_dict[ce][obj_name]["obj"].generate_dataframe(
                                            val, self.http_obj_dict[ce][obj_name]["obj"].devices, self.http_obj_dict[ce][obj_name]["obj"].macid_list, self.http_obj_dict[ce][obj_name]["obj"].channel_list,
                                            self.http_obj_dict[ce][obj_name]["obj"].ssid_list, self.http_obj_dict[ce][obj_name]["obj"].mode_list, http_data["dataset2"], [], http_data["dataset"],
                                            http_data["dataset1"], http_data["rx_rate"], [], self.http_obj_dict[ce][obj_name]["obj"].data["total_err"]
                                        )
                                    if dataframe:
                                        self.overall_report.set_obj_html("", "Group: {}".format(key))
                                        self.overall_report.build_objective()
                                        dataframe1 = pd.DataFrame(dataframe)
                                        self.overall_report.set_table_dataframe(dataframe1)
                                        self.overall_report.build_table()
                            else:
                                dataframe = {
                                    " Clients": self.http_obj_dict[ce][obj_name]["obj"].devices,
                                    " MAC ": self.http_obj_dict[ce][obj_name]["obj"].macid_list,
                                    " Channel": self.http_obj_dict[ce][obj_name]["obj"].channel_list,
                                    " SSID ": self.http_obj_dict[ce][obj_name]["obj"].ssid_list,
                                    " Mode": self.http_obj_dict[ce][obj_name]["obj"].mode_list,
                                    " No of times File downloaded ": http_data["dataset2"],
                                    " Average time taken to Download file (ms)": http_data["dataset"],
                                    " Bytes-rd (Mega Bytes) ": http_data["dataset1"],
                                    "Rx Rate (Mbps)": http_data["rx_rate"],
                                    "Failed url's": self.http_obj_dict[ce][obj_name]["obj"].data["total_err"]
                                }
                                if self.http_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.http_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                    dataframe[" Expected value of no of times file downloaded"] = test_input_list
                                    dataframe["Status"] = pass_fail_list
                                dataframe1 = pd.DataFrame(dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()
                        else:
                            dataframe = {
                                " Clients": self.http_obj_dict[ce][obj_name]["obj"].devices,
                                " MAC ": self.http_obj_dict[ce][obj_name]["obj"].macid_list,
                                " Channel": self.http_obj_dict[ce][obj_name]["obj"].channel_list,
                                " SSID ": self.http_obj_dict[ce][obj_name]["obj"].ssid_list,
                                " Mode": self.http_obj_dict[ce][obj_name]["obj"].mode_list,
                                " No of times File downloaded ": http_data["dataset2"],
                                " Average time taken to Download file (ms)": http_data["dataset"],
                                " Bytes-rd (Mega Bytes) ": http_data["dataset1"]
                            }
                            dataframe1 = pd.DataFrame(dataframe)
                            self.overall_report.set_table_dataframe(dataframe1)
                            self.overall_report.build_table()

                        # self.http_obj_dict[ce]
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"http_test_{obj_no}"
                        else:
                            break

                elif test_name == "ftp_test":
                    obj_no=1
                    obj_name = "ftp_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.ftp_obj_dict[ce]:
                        # obj_name = f"ftp_test_{obj_no}"
                        if ce == "parallel":
                            obj_no = ''
                        params = self.ftp_obj_dict[ce][obj_name]["data"].copy()
                        ftp_data = params["ftp_data"].copy() if isinstance(params["ftp_data"], (list, dict, set)) else params["ftp_data"]
                        date = params["date"].copy() if isinstance(params["date"], (list, dict, set)) else params["date"]
                        input_setup_info = params["input_setup_info"].copy() if isinstance(params["input_setup_info"], (list, dict, set)) else params["input_setup_info"]
                        test_rig = params["test_rig"].copy() if isinstance(params["test_rig"], (list, dict, set)) else params["test_rig"]
                        test_tag = params["test_tag"].copy() if isinstance(params["test_tag"], (list, dict, set)) else params["test_tag"]
                        dut_hw_version = params["dut_hw_version"].copy() if isinstance(params["dut_hw_version"], (list, dict, set)) else params["dut_hw_version"]
                        dut_sw_version = params["dut_sw_version"].copy() if isinstance(params["dut_sw_version"], (list, dict, set)) else params["dut_sw_version"]
                        dut_model_num = params["dut_model_num"].copy() if isinstance(params["dut_model_num"], (list, dict, set)) else params["dut_model_num"]
                        dut_serial_num = params["dut_serial_num"].copy() if isinstance(params["dut_serial_num"], (list, dict, set)) else params["dut_serial_num"]
                        test_id = params["test_id"].copy() if isinstance(params["test_id"], (list, dict, set)) else params["test_id"]
                        bands = params["bands"].copy() if isinstance(params["bands"], (list, dict, set)) else params["bands"]
                        csv_outfile = params["csv_outfile"].copy() if isinstance(params["csv_outfile"], (list, dict, set)) else params["csv_outfile"]
                        local_lf_report_dir = params["local_lf_report_dir"].copy() if isinstance(params["local_lf_report_dir"], (list, dict, set)) else params["local_lf_report_dir"]
                        report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]

                        # Optional parameter
                        config_devices = ""
                        if "config_devices" in params:
                            config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]

                        no_of_stations = ""
                        duration = ""
                        x_fig_size = 18
                        y_fig_size = len(self.ftp_obj_dict[ce][obj_name]["obj"].real_client_list1) * .5 + 4

                        if int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration) < 60:
                            duration = str(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration) + "s"
                        elif int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration == 60) or (int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration) > 60 and int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration) < 3600):
                            duration = str(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration / 60) + "m"
                        else:
                            if int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration == 3600) or (int(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration) > 3600):
                                duration = str(self.ftp_obj_dict[ce][obj_name]["obj"].traffic_duration / 3600) + "h"

                        client_list = []
                        if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == "Real":
                            client_list = self.ftp_obj_dict[ce][obj_name]["obj"].real_client_list1
                            android_devices, windows_devices, linux_devices, mac_devices = 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            total_devices = ""
                            for i in self.ftp_obj_dict[ce][obj_name]["obj"].real_client_list:
                                split_device_name = i.split(" ")
                                if 'android' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Android)"))
                                    device_type.append("Android")
                                    android_devices += 1
                                elif 'Win' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                                    device_type.append("Windows")
                                    windows_devices += 1
                                elif 'Lin' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                                    device_type.append("Linux")
                                    linux_devices += 1
                                elif 'Mac' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                                    device_type.append("Mac")
                                    mac_devices += 1

                            if android_devices > 0:
                                total_devices += f" Android({android_devices})"
                            if windows_devices > 0:
                                total_devices += f" Windows({windows_devices})"
                            if linux_devices > 0:
                                total_devices += f" Linux({linux_devices})"
                            if mac_devices > 0:
                                total_devices += f" Mac({mac_devices})"
                        else:
                            if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == "Virtual":
                                client_list = self.ftp_obj_dict[ce][obj_name]["obj"].station_list
                        if 'ftp_test' not in self.test_count_dict:
                            self.test_count_dict['ftp_test']=0
                        self.test_count_dict['ftp_test']+=1
                        self.overall_report.set_obj_html(_obj_title=f'FTP Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Setup Information")
                        self.overall_report.build_table_title()

                        if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == "Virtual":
                            no_of_stations = str(len(self.ftp_obj_dict[ce][obj_name]["obj"].station_list))
                        else:
                            no_of_stations = str(len(self.ftp_obj_dict[ce][obj_name]["obj"].input_devices_list))

                        if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == "Real":
                            if config_devices == "":
                                test_setup_info = {
                                    "AP Name": self.ftp_obj_dict[ce][obj_name]["obj"].ap_name,
                                    "SSID": self.ftp_obj_dict[ce][obj_name]["obj"].ssid,
                                    "Security": self.ftp_obj_dict[ce][obj_name]["obj"].security,
                                    "Device List": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                                    "Failed CXs": self.ftp_obj_dict[ce][obj_name]["obj"].failed_cx if self.ftp_obj_dict[ce][obj_name]["obj"].failed_cx else "NONE",
                                    "File size": self.ftp_obj_dict[ce][obj_name]["obj"].file_size,
                                    "File location": "/home/lanforge",
                                    "Traffic Direction": self.ftp_obj_dict[ce][obj_name]["obj"].direction,
                                    "Traffic Duration ": duration
                                }
                            else:
                                group_names = ', '.join(config_devices.keys())
                                profile_names = ', '.join(config_devices.values())
                                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                                test_setup_info = {
                                    "AP Name": self.ftp_obj_dict[ce][obj_name]["obj"].ap_name,
                                    'Configuration': configmap,
                                    "No of Devices": "Total" + f"({no_of_stations})" + total_devices,
                                    "File size": self.ftp_obj_dict[ce][obj_name]["obj"].file_size,
                                    "File location": "/home/lanforge",
                                    "Traffic Direction": self.ftp_obj_dict[ce][obj_name]["obj"].direction,
                                    "Traffic Duration ": duration
                                }
                        else:
                            test_setup_info = {
                                "AP Name": self.ftp_obj_dict[ce][obj_name]["obj"].ap_name,
                                "SSID": self.ftp_obj_dict[ce][obj_name]["obj"].ssid,
                                "Security": self.ftp_obj_dict[ce][obj_name]["obj"].security,
                                "No of Devices": no_of_stations,
                                "File size": self.ftp_obj_dict[ce][obj_name]["obj"].file_size,
                                "File location": "/home/lanforge",
                                "Traffic Direction": self.ftp_obj_dict[ce][obj_name]["obj"].direction,
                                "Traffic Duration ": duration
                            }

                        self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

                        self.overall_report.set_obj_html(
                            _obj_title=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}",
                            _obj=f"The below graph represents number of times a file {self.ftp_obj_dict[ce][obj_name]['obj'].direction} for each client"
                            f"(WiFi) traffic.  X- axis shows “No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}” and Y-axis shows "
                            f"Client names.")

                        self.overall_report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[self.ftp_obj_dict[ce][obj_name]["obj"].url_data], _xaxis_name=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction}",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in client_list],
                                                        _yaxis_label=[i for i in client_list],
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _yticks_rotation=None,
                                                        _graph_title=f"No of times file {self.ftp_obj_dict[ce][obj_name]['obj'].direction} (Count)",
                                                        _title_size=16,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _color_name=['orange'],
                                                        _show_bar_value=True,
                                                        _enable_csv=True,
                                                        _graph_image_name=f"Total-url_ftp_{obj_no}", _color_edge=['black'],
                                                        _color=['orange'],
                                                        _label=[self.ftp_obj_dict[ce][obj_name]["obj"].direction])
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        self.overall_report.set_graph_image(graph_png)
                        # need to move the graph image to the results
                        self.overall_report.move_graph_image()
                        self.overall_report.set_csv_filename(graph_png)
                        self.overall_report.move_csv_file()
                        self.overall_report.build_graph()
                        self.overall_report.set_obj_html(
                            _obj_title=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file ",
                            _obj=f"The below graph represents average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} for each client  "
                            f"(WiFi) traffic.  X- axis shows “Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} a file ” and Y-axis shows "
                            f"Client names.")

                        self.overall_report.build_objective()
                        graph = lf_bar_graph_horizontal(_data_set=[self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg], _xaxis_name=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file in ms",
                                                        _yaxis_name="Client names",
                                                        _yaxis_categories=[i for i in client_list],
                                                        _yaxis_label=[i for i in client_list],
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _yticks_rotation=None,
                                                        _graph_title=f"Average time taken to {self.ftp_obj_dict[ce][obj_name]['obj'].direction} file",
                                                        _title_size=16,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _color_name=['steelblue'],
                                                        _show_bar_value=True,
                                                        _enable_csv=True,
                                                        _graph_image_name=f"ucg-avg_ftp_{obj_no}", _color_edge=['black'],
                                                        _color=['steelblue'],
                                                        _label=[self.ftp_obj_dict[ce][obj_name]["obj"].direction])
                        graph_png = graph.build_bar_graph_horizontal()
                        print("graph name {}".format(graph_png))
                        self.overall_report.set_graph_image(graph_png)
                        self.overall_report.move_graph_image()
                        # need to move the graph image to the results
                        self.overall_report.set_csv_filename(graph_png)
                        self.overall_report.move_csv_file()
                        self.overall_report.build_graph()
                        if(self.ftp_obj_dict[ce][obj_name]["obj"].dowebgui and self.ftp_obj_dict[ce][obj_name]["obj"].get_live_view):
                            for floor in range(0,int(self.ftp_obj_dict[ce][obj_name]["obj"].total_floors)):
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                throughput_image_path = os.path.join(script_dir, "heatmap_images", f"ftp_{self.ftp_obj_dict[ce][obj_name]['obj'].test_name}_{floor+1}.png")
                                # rssi_image_path = os.path.join(script_dir, "heatmap_images", f"{self.test_name}_rssi_{floor+1}.png")
                                timeout = 60  # seconds
                                start_time = time.time()

                                while not (os.path.exists(throughput_image_path)):
                                    if time.time() - start_time > timeout:
                                        print("Timeout: Images not found within 60 seconds.")
                                        break
                                    time.sleep(1)
                                while not os.path.exists(throughput_image_path):
                                    if os.path.exists(throughput_image_path):
                                        break
                                    # time.sleep(10)
                                if os.path.exists(throughput_image_path):
                                    self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                    self.overall_report.build_custom()
                                    # self.overall_report.set_custom_html("<h2>Average Throughput Heatmap: </h2>")
                                    # self.overall_report.build_custom()
                                    self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
                                    self.overall_report.build_custom()
                                    # os.remove(throughput_image_path)
                        self.overall_report.set_obj_html("File Download Time (sec)", "The below table will provide information of "
                                                "minimum, maximum and the average time taken by clients to download a file in seconds")
                        self.overall_report.build_objective()
                        dataframe2 = {
                            "Minimum": [str(round(min(self.ftp_obj_dict[ce][obj_name]["obj"].uc_min) / 1000, 1))],
                            "Maximum": [str(round(max(self.ftp_obj_dict[ce][obj_name]["obj"].uc_max) / 1000, 1))],
                            "Average": [str(round((sum(self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg) / len(client_list)) / 1000, 1))]
                        }
                        dataframe3 = pd.DataFrame(dataframe2)
                        self.overall_report.set_table_dataframe(dataframe3)
                        self.overall_report.build_table()
                        self.overall_report.set_table_title("Overall Results")
                        self.overall_report.build_table_title()
                        if self.ftp_obj_dict[ce][obj_name]["obj"].clients_type == 'Real':
                            # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
                            if self.ftp_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ftp_obj_dict[ce][obj_name]["obj"].csv_name:
                                self.ftp_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(client_list)
                            # When groups are provided a seperate table will be generated for each group using generate_dataframe
                            if self.ftp_obj_dict[ce][obj_name]["obj"].group_name:
                                for key, val in self.ftp_obj_dict[ce][obj_name]["obj"].group_device_map.items():
                                    if self.ftp_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ftp_obj_dict[ce][obj_name]["obj"].csv_name:
                                        dataframe = self.ftp_obj_dict[ce][obj_name]["obj"].generate_dataframe(val, client_list, self.ftp_obj_dict[ce][obj_name]["obj"].mac_id_list, self.ftp_obj_dict[ce][obj_name]["obj"].channel_list, self.ftp_obj_dict[ce][obj_name]["obj"].ssid_list, self.ftp_obj_dict[ce][obj_name]["obj"].mode_list,
                                                                            self.ftp_obj_dict[ce][obj_name]["obj"].url_data, self.ftp_obj_dict[ce][obj_name]["obj"].test_input_list, self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg, self.ftp_obj_dict[ce][obj_name]["obj"].bytes_rd, self.ftp_obj_dict[ce][obj_name]["obj"].rx_rate, self.ftp_obj_dict[ce][obj_name]["obj"].pass_fail_list,self.ftp_obj_dict[ce][obj_name]["obj"].total_err)
                                    else:
                                        dataframe = self.ftp_obj_dict[ce][obj_name]["obj"].generate_dataframe(val, client_list, self.ftp_obj_dict[ce][obj_name]["obj"].mac_id_list, self.ftp_obj_dict[ce][obj_name]["obj"].channel_list, self.ftp_obj_dict[ce][obj_name]["obj"].ssid_list,
                                                                            self.ftp_obj_dict[ce][obj_name]["obj"].mode_list, self.ftp_obj_dict[ce][obj_name]["obj"].url_data, [], self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg, self.ftp_obj_dict[ce][obj_name]["obj"].bytes_rd, self.ftp_obj_dict[ce][obj_name]["obj"].rx_rate, [], self.ftp_obj_dict[ce][obj_name]["obj"].total_err)

                                    if dataframe:
                                        self.overall_report.set_obj_html("", "Group: {}".format(key))
                                        self.overall_report.build_objective()
                                        dataframe1 = pd.DataFrame(dataframe)
                                        self.overall_report.set_table_dataframe(dataframe1)
                                        self.overall_report.build_table()
                            else:
                                dataframe = {
                                    " Clients": client_list,
                                    " MAC ": self.ftp_obj_dict[ce][obj_name]["obj"].mac_id_list,
                                    " Channel": self.ftp_obj_dict[ce][obj_name]["obj"].channel_list,
                                    " SSID ": self.ftp_obj_dict[ce][obj_name]["obj"].ssid_list,
                                    " Mode": self.ftp_obj_dict[ce][obj_name]["obj"].mode_list,
                                    " No of times File downloaded ": self.ftp_obj_dict[ce][obj_name]["obj"].url_data,
                                    " Time Taken to Download file (ms)": self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg,
                                    " Bytes-rd (Mega Bytes)": self.ftp_obj_dict[ce][obj_name]["obj"].bytes_rd,
                                    " RX RATE (Mbps) ": self.ftp_obj_dict[ce][obj_name]["obj"].rx_rate,
                                    "Failed Urls": self.ftp_obj_dict[ce][obj_name]["obj"].total_err
                                }
                                if self.ftp_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ftp_obj_dict[ce][obj_name]["obj"].csv_name:
                                    dataframe[" Expected output "] = self.ftp_obj_dict[ce][obj_name]["obj"].test_input_list
                                    dataframe[" Status "] = self.ftp_obj_dict[ce][obj_name]["obj"].pass_fail_list

                                dataframe1 = pd.DataFrame(dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                        else:
                            dataframe = {
                                " Clients": client_list,
                                " MAC ": self.ftp_obj_dict[ce][obj_name]["obj"].mac_id_list,
                                " Channel": self.ftp_obj_dict[ce][obj_name]["obj"].channel_list,
                                " SSID ": self.ftp_obj_dict[ce][obj_name]["obj"].ssid_list,
                                " Mode": self.ftp_obj_dict[ce][obj_name]["obj"].mode_list,
                                " No of times File downloaded ": self.ftp_obj_dict[ce][obj_name]["obj"].url_data,
                                " Time Taken to Download file (ms)": self.ftp_obj_dict[ce][obj_name]["obj"].uc_avg,
                                " Bytes-rd (Mega Bytes)": self.ftp_obj_dict[ce][obj_name]["obj"].bytes_rd,
                            }
                            dataframe1 = pd.DataFrame(dataframe)
                            self.overall_report.set_table_dataframe(dataframe1)
                            self.overall_report.build_table()
                        # self.overall_report.build_footer()
                        # html_file = self.overall_report.write_html()
                        # logger.info("returned file {}".format(html_file))
                        # logger.info(html_file)
                        # self.overall_report.write_pdf()

                        if csv_outfile is not None:
                            current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                            csv_outfile = "{}_{}-test_l4_ftp.csv".format(
                                csv_outfile, current_time)
                            csv_outfile = self.overall_report.file_add_path(csv_outfile)
                            logger.info("csv output file : {}".format(csv_outfile))
                        if ce == "series":
                            obj_no+=1
                            obj_name = f"ftp_test_{obj_no}"
                        else:
                            break

                elif test_name == "thput_test":
                    obj_no=1
                    obj_name = "thput_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.thput_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'THROUGHPUT Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        # obj_name = f"thput_test_{obj_no}"
                        params = self.thput_obj_dict[ce][obj_name]["data"].copy()
                        iterations_before_test_stopped_by_user = params["iterations_before_test_stopped_by_user"].copy() if isinstance(params["iterations_before_test_stopped_by_user"], (list, dict, set)) else params["iterations_before_test_stopped_by_user"]
                        incremental_capacity_list = params["incremental_capacity_list"].copy() if isinstance(params["incremental_capacity_list"], (list, dict, set)) else params["incremental_capacity_list"]
                        data = params["data"].copy() if isinstance(params["data"], (list, dict, set)) else params["data"]
                        data1 = params["data1"].copy() if isinstance(params["data1"], (list, dict, set)) else params["data1"]
                        report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]

                        self.thput_obj_dict[ce][obj_name]["obj"].ssid_list = self.thput_obj_dict[ce][obj_name]["obj"].get_ssid_list(self.thput_obj_dict[ce][obj_name]["obj"].input_devices_list)
                        self.thput_obj_dict[ce][obj_name]["obj"].signal_list, self.thput_obj_dict[ce][obj_name]["obj"].channel_list, self.thput_obj_dict[ce][obj_name]["obj"].mode_list, self.thput_obj_dict[ce][obj_name]["obj"].link_speed_list, rx_rate_list = self.thput_obj_dict[ce][obj_name]["obj"].get_signal_and_channel_data(self.thput_obj_dict[ce][obj_name]["obj"].input_devices_list)
                        selected_real_clients_names = params["selected_real_clients_names"] if "selected_real_clients_names" in params else None 
                        if selected_real_clients_names is not None:
                            self.thput_obj_dict[ce][obj_name]["obj"].num_stations = selected_real_clients_names

                        # Initialize the report object
                        if self.thput_obj_dict[ce][obj_name]["obj"].do_interopability == False:
                            # df.to_csv(os.path.join(report_path_date_time, 'throughput_data.csv'))
                            # For groups and profiles configuration through webgui

                            self.overall_report.set_obj_html(_obj_title="Input Parameters",
                                                _obj="The below tables provides the input parameters for the test")
                            self.overall_report.build_objective()

                            # Initialize counts and lists for device types
                            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            packet_size_text = ''
                            total_devices = ""
                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                packet_size_text = 'AUTO'
                            else:
                                packet_size_text = str(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu) + ' Bytes'
                            # Determine load type name based on self.thput_obj_dict[ce][obj_name]["obj"].load_type
                            if self.thput_obj_dict[ce][obj_name]["obj"].load_type == "wc_intended_load":
                                load_type_name = "Intended Load"
                            else:
                                load_type_name = "Per Client Load"
                            for i in self.thput_obj_dict[ce][obj_name]["obj"].real_client_list:
                                split_device_name = i.split(" ")
                                if 'android' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Android)"))
                                    device_type.append("Android")
                                    android_devices += 1
                                elif 'Win' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                                    device_type.append("Windows")
                                    windows_devices += 1
                                elif 'Lin' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                                    device_type.append("Linux")
                                    linux_devices += 1
                                elif 'Mac' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                                    device_type.append("Mac")
                                    mac_devices += 1
                                elif 'iOS' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                                    device_type.append("iOS")
                                    ios_devices += 1

                            # Build total_devices string based on counts
                            if android_devices > 0:
                                total_devices += f" Android({android_devices})"
                            if windows_devices > 0:
                                total_devices += f" Windows({windows_devices})"
                            if linux_devices > 0:
                                total_devices += f" Linux({linux_devices})"
                            if mac_devices > 0:
                                total_devices += f" Mac({mac_devices})"
                            if ios_devices > 0:
                                total_devices += f" iOS({ios_devices})"

                            # Determine incremental_capacity_data based on self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity
                            if self.thput_obj_dict[ce][obj_name]["obj"].gave_incremental:
                                incremental_capacity_data = "No Incremental values provided"
                            elif len(self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity) == 1:
                                if len(incremental_capacity_list) == 1:
                                    incremental_capacity_data = str(self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity[0])
                                else:
                                    incremental_capacity_data = ','.join(map(str, incremental_capacity_list))
                            elif (len(self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity) > 1):
                                self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity = self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity.split(',')
                                incremental_capacity_data = ', '.join(self.thput_obj_dict[ce][obj_name]["obj"].incremental_capacity)
                            else:
                                incremental_capacity_data = "None"

                            # Construct test_setup_info dictionary for test setup table
                            if self.thput_obj_dict[ce][obj_name]["obj"].group_name:
                                group_names = ', '.join(self.thput_obj_dict[ce][obj_name]["obj"].configdevices.keys())
                                profile_names = ', '.join(self.thput_obj_dict[ce][obj_name]["obj"].configdevices.values())
                                configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                                test_setup_info = {
                                    "Test name": self.thput_obj_dict[ce][obj_name]["obj"].test_name,
                                    "Configuration": configmap,
                                    "Configured Devices": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                    "Increment": incremental_capacity_data,
                                    "Traffic Duration in minutes": round(int(self.thput_obj_dict[ce][obj_name]["obj"].test_duration) * len(incremental_capacity_list) / 60, 2),
                                    "Traffic Type": (self.thput_obj_dict[ce][obj_name]["obj"].traffic_type.strip("lf_")).upper(),
                                    "Traffic Direction": self.thput_obj_dict[ce][obj_name]["obj"].direction,
                                    "Upload Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                    "Download Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                    "Load Type": load_type_name,
                                    "Packet Size": packet_size_text
                                }
                            else:
                                test_setup_info = {
                                    "Test name": self.thput_obj_dict[ce][obj_name]["obj"].test_name,
                                    "Device List": ", ".join(all_devices_names),
                                    "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                    "Increment": incremental_capacity_data,
                                    "Traffic Duration in minutes": round(int(self.thput_obj_dict[ce][obj_name]["obj"].test_duration) * len(incremental_capacity_list) / 60, 2),
                                    "Traffic Type": (self.thput_obj_dict[ce][obj_name]["obj"].traffic_type.strip("lf_")).upper(),
                                    "Traffic Direction": self.thput_obj_dict[ce][obj_name]["obj"].direction,
                                    "Upload Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                    "Download Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                    "Load Type": load_type_name,
                                    "Packet Size": packet_size_text
                                }
                            self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

                            # Loop through iterations and build graphs, tables for each iteration
                            for i in range(len(iterations_before_test_stopped_by_user)):
                                # rssi_signal_data=[]
                                devices_on_running = []
                                download_data = []
                                upload_data = []
                                upload_drop = []
                                download_drop = []
                                devices_data_to_create_bar_graph = []
                                # signal_data=[]
                                direction_in_table = []
                                packet_size_in_table = []
                                upload_list, download_list = [], []
                                rssi_data = []
                                data_iter = data[data['Iteration'] == i + 1]
                                avg_rtt_data = []

                                # for sig in self.thput_obj_dict[ce][obj_name]["obj"].signal_list[0:int(incremental_capacity_list[i])]:
                                #     signal_data.append(int(sig)*(-1))
                                # rssi_signal_data.append(signal_data)

                                # Fetch devices_on_running from real_client_list
                                for j in range(data1[i][-1]):
                                    devices_on_running.append(self.thput_obj_dict[ce][obj_name]["obj"].real_client_list[j].split(" ")[-1])

                                # Fetch download_data and upload_data based on load_type and direction
                                for k in devices_on_running:
                                    # individual_device_data=[]

                                    # Checking individual device download and upload rate by searching device name in dataframe
                                    columns_with_substring = [col for col in data_iter.columns if k in col]
                                    filtered_df = data_iter[columns_with_substring]
                                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()
                                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()
                                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                                    if self.thput_obj_dict[ce][obj_name]["obj"].load_type == "wc_intended_load":
                                        if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":

                                            # Append average download and upload data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append average upload and download drop from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)

                                        elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':

                                            # Append average download data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))

                                            # Append 0 for upload data
                                            upload_data.append(0)

                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                            # Append average download drop data from filtered dataframe

                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)

                                        elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Upload':

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))
                                            download_list.append(str(round((int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000) / int(incremental_capacity_list[i]), 2)))

                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))

                                            # Append Average upload data from filtered dataframe
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append 0 for download data
                                            download_data.append(0)
                                            # Append average upload drop data from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                    
                                    else:

                                        if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":
                                            # Append average download and upload data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append average download and upload drop data from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))
                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            # upload_data.append(filtered_df[[col for col in  filtered_df.columns if "Upload" in col][0]].values.tolist()[-1])
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)))
                                            download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)))

                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                        elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':

                                            # Append average download data from filtered dataframe
                                            download_data.append(round(sum(download_col) / len(download_col), 2))
                                            # Append 0 for upload data
                                            upload_data.append(0)
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)))
                                            download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)))
                                            # Append average download drop data from filtered dataframe
                                            download_drop.append(round(sum(download_drop_col) / len(download_drop_col), 2))
                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                        elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Upload':

                                            # Calculate and append upload and download throughput to lists
                                            upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps")
                                            download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps")
                                            rssi_data.append(int(round(sum(rssi_col) / len(rssi_col), 2) * -1))
                                            avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])

                                            # Append average upload data from filtered dataframe
                                            upload_data.append(round(sum(upload_col) / len(upload_col), 2))
                                            # Append average upload drop data from filtered dataframe
                                            upload_drop.append(round(sum(upload_drop_col) / len(upload_drop_col), 2))

                                            # Append 0 for download data
                                            download_data.append(0)

                                            if self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu == -1:
                                                packet_size_in_table.append('AUTO')
                                            else:
                                                packet_size_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu)
                                            direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                data_set_in_graph = []

                                # Depending on the test direction, retrieve corresponding throughput data,
                                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                                if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Download', 'Upload']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Download: {round(sum(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "
                                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    label_data = ['Download']
                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Download : {round(((sum(download_data[0:int(incremental_capacity_list[i])]))), 2)} Mbps"

                                elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Upload':
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Upload']
                                    real_time_data = f"Real Time Throughput: Achieved Throughput: Upload : {round((sum(upload_data[0:int(incremental_capacity_list[i])])), 2)} Mbps"

                                if len(incremental_capacity_list) > 1:
                                    self.overall_report.set_custom_html(f"<h2><u>Iteration-{i + 1}: Number of Devices Running : {len(devices_on_running)}</u></h2>")
                                    self.overall_report.build_custom()

                                self.overall_report.set_obj_html(
                                    _obj_title=f"{real_time_data}",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph_png = self.thput_obj_dict[ce][obj_name]["obj"].build_line_graph(
                                    data_set=data_set_in_graph,
                                    xaxis_name="Time",
                                    yaxis_name="Throughput (Mbps)",
                                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                                    label=label_data,
                                    graph_image_name=f"line_graph{i}"
                                )
                                logger.info("graph name {}".format(graph_png))
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()

                                self.overall_report.build_graph()
                                x_fig_size = 15
                                y_fig_size = len(devices_on_running) * .5 + 4
                                self.overall_report.set_obj_html(
                                    _obj_title="Per Client Avg-Throughput",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                                _xaxis_name="Avg Throughput(Mbps)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"image_name{i}_{obj_no}",
                                                                _label=label_data,
                                                                _yaxis_categories=devices_on_running_trimmed,
                                                                _legend_loc="best",
                                                                _legend_box=(1.0, 1.0),
                                                                _show_bar_value=True,
                                                                _figsize=(x_fig_size, y_fig_size)
                                                                )

                                graph_png = graph.build_bar_graph_horizontal()
                                logger.info("graph name {}".format(graph_png))
                                graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_obj_html(
                                    _obj_title="RSSI Of The Clients Connected",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                                _xaxis_name="Signal(-dBm)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"signal_image_name{i}_{obj_no}",
                                                                _label=['RSSI'],
                                                                _yaxis_categories=devices_on_running_trimmed,
                                                                _legend_loc="best",
                                                                _legend_box=(1.0, 1.0),
                                                                _show_bar_value=True,
                                                                _figsize=(x_fig_size, y_fig_size)
                                                                #    _color=['lightcoral']
                                                                )
                                graph_png = graph.build_bar_graph_horizontal()
                                logger.info("graph name {}".format(graph_png))
                                graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                if(self.thput_obj_dict[ce][obj_name]["obj"].dowebgui and self.thput_obj_dict[ce][obj_name]["obj"].get_live_view):
                                    self.thput_obj_dict[ce][obj_name]["obj"].add_live_view_images_to_report(self.overall_report)
                                    
                                if self.thput_obj_dict[ce][obj_name]["obj"].group_name:
                                    self.overall_report.set_obj_html(
                                        _obj_title="Detailed Result Table For Groups ",
                                        _obj="The below tables provides detailed information for the throughput test on each group.")
                                else:

                                    self.overall_report.set_obj_html(
                                        _obj_title="Detailed Result Table ",
                                        _obj="The below tables provides detailed information for the throughput test on each device.")
                                self.overall_report.build_objective()
                                self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list = [item.split()[-1] if ' ' in item else item for item in self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list]
                                if self.thput_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.thput_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                    test_input_list, pass_fail_list = self.thput_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                                if self.thput_obj_dict[ce][obj_name]["obj"].group_name:
                                    for key, val in self.thput_obj_dict[ce][obj_name]["obj"].group_device_map.items():
                                        if self.thput_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.thput_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                            # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                                            dataframe = self.thput_obj_dict[ce][obj_name]["obj"].generate_dataframe(val,
                                                                                device_type[0:int(incremental_capacity_list[i])],
                                                                                devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].ssid_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].channel_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].mode_list[0:int(incremental_capacity_list[i])],
                                                                                direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                download_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                upload_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                test_input_list,
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].link_speed_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                pass_fail_list,
                                                                                upload_drop,
                                                                                download_drop)
                                        # Generating Dataframe for groups when pass_fail case is not specified
                                        else:
                                            dataframe = self.thput_obj_dict[ce][obj_name]["obj"].generate_dataframe(val,
                                                                                device_type[0:int(incremental_capacity_list[i])],
                                                                                devices_on_running[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].ssid_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].channel_list[0:int(incremental_capacity_list[i])],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].mode_list[0:int(incremental_capacity_list[i])],
                                                                                direction_in_table[0:int(incremental_capacity_list[i])],
                                                                                download_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) for n in avg_rtt_data[0:int(incremental_capacity_list[i])]],
                                                                                [str(n) + " Mbps" for n in download_data[0:int(incremental_capacity_list[i])]],
                                                                                upload_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) + " Mbps" for n in upload_data[0:int(incremental_capacity_list[i])]],
                                                                                ['' if n == 0 else '-' + str(n) + " dbm" for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                                                                [],
                                                                                self.thput_obj_dict[ce][obj_name]["obj"].link_speed_list[0:int(incremental_capacity_list[i])],
                                                                                [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                                                                [],
                                                                                upload_drop,
                                                                                download_drop)
                                        if dataframe:
                                            self.overall_report.set_obj_html("", "Group: {}".format(key))
                                            self.overall_report.build_objective()
                                            dataframe1 = pd.DataFrame(dataframe)
                                            self.overall_report.set_table_dataframe(dataframe1)
                                            self.overall_report.build_table()
                                else:
                                    bk_dataframe = {
                                        " Device Type ": device_type[0:int(incremental_capacity_list[i])],
                                        " Username": devices_on_running[0:int(incremental_capacity_list[i])],
                                        " SSID ": self.thput_obj_dict[ce][obj_name]["obj"].ssid_list[0:int(incremental_capacity_list[i])],
                                        " MAC ": self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list[0:int(incremental_capacity_list[i])],
                                        " Channel ": self.thput_obj_dict[ce][obj_name]["obj"].channel_list[0:int(incremental_capacity_list[i])],
                                        " Mode": self.thput_obj_dict[ce][obj_name]["obj"].mode_list[0:int(incremental_capacity_list[i])],
                                        # " Direction":direction_in_table[0:int(incremental_capacity_list[i])],
                                        " Offered download rate (Mbps) ": download_list[0:int(incremental_capacity_list[i])],
                                        " Observed Average download rate (Mbps) ": [str(n)  for n in download_data[0:int(incremental_capacity_list[i])]],
                                        " Offered upload rate (Mbps) ": upload_list[0:int(incremental_capacity_list[i])],
                                        " Observed Average upload rate (Mbps) ": [str(n)  for n in upload_data[0:int(incremental_capacity_list[i])]],
                                        " RSSI (dBm) ": ['' if n == 0 else '-' + str(n)  for n in rssi_data[0:int(incremental_capacity_list[i])]],
                                        # " Link Speed ":self.thput_obj_dict[ce][obj_name]["obj"].link_speed_list[0:int(incremental_capacity_list[i])],
                                        " Average RTT (ms)" : avg_rtt_data[0:int(incremental_capacity_list[i])],
                                        " Packet Size(Bytes) ": [str(n) for n in packet_size_in_table[0:int(incremental_capacity_list[i])]],
                                    }
                                    if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":
                                        bk_dataframe[" Average Tx Drop % "] = upload_drop
                                        bk_dataframe[" Average Rx Drop % "] = download_drop
                                    elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':
                                        bk_dataframe[" Average Rx Drop % "] = download_drop
                                        # adding rx drop while uploading as 0
                                        bk_dataframe[" Average Tx Drop % "] = [0.0] * len(download_drop)

                                    else:
                                        bk_dataframe[" Average Tx Drop % "] = upload_drop
                                        # adding rx drop while downloading as 0
                                        bk_dataframe[" Average Rx Drop % "] = [0.0] * len(upload_drop)
                                    if self.thput_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.thput_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                        bk_dataframe[" Expected " + self.thput_obj_dict[ce][obj_name]["obj"].direction + " rate "] = [str(n) + " Mbps" for n in test_input_list]
                                        bk_dataframe[" Status "] = pass_fail_list
                                    dataframe1 = pd.DataFrame(bk_dataframe)
                                    self.overall_report.set_table_dataframe(dataframe1)
                                    self.overall_report.build_table()

                                self.overall_report.set_custom_html('<hr>')
                                self.overall_report.build_custom()

                        elif self.thput_obj_dict[ce][obj_name]["obj"].do_interopability:

                            self.overall_report.set_obj_html(_obj_title="Input Parameters",
                                                _obj="The below tables provides the input parameters for the test")
                            self.overall_report.build_objective()

                            # Initialize counts and lists for device types
                            android_devices, windows_devices, linux_devices, mac_devices, ios_devices = 0, 0, 0, 0, 0
                            all_devices_names = []
                            device_type = []
                            total_devices = ""

                            for i in self.thput_obj_dict[ce][obj_name]["obj"].real_client_list:
                                split_device_name = i.split(" ")
                                if 'android' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Android)"))
                                    device_type.append("Android")
                                    android_devices += 1
                                elif 'Win' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Windows)"))
                                    device_type.append("Windows")
                                    windows_devices += 1
                                elif 'Lin' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Linux)"))
                                    device_type.append("Linux")
                                    linux_devices += 1
                                elif 'Mac' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(Mac)"))
                                    device_type.append("Mac")
                                    mac_devices += 1
                                elif 'iOS' in split_device_name:
                                    all_devices_names.append(split_device_name[2] + ("(iOS)"))
                                    device_type.append("iOS")
                                    ios_devices += 1

                            # Build total_devices string based on counts
                            if android_devices > 0:
                                total_devices += f" Android({android_devices})"
                            if windows_devices > 0:
                                total_devices += f" Windows({windows_devices})"
                            if linux_devices > 0:
                                total_devices += f" Linux({linux_devices})"
                            if mac_devices > 0:
                                total_devices += f" Mac({mac_devices})"
                            if ios_devices > 0:
                                total_devices += f" iOS({ios_devices})"

                            # Construct test_setup_info dictionary for test setup table
                            test_setup_info = {
                                "Test name": self.thput_obj_dict[ce][obj_name]["obj"].test_name,
                                "Device List": ", ".join(all_devices_names),
                                "No of Devices": "Total" + f"({str(self.thput_obj_dict[ce][obj_name]['obj'].num_stations)})" + total_devices,
                                "Traffic Duration in minutes": round(int(self.thput_obj_dict[ce][obj_name]["obj"].test_duration) * len(incremental_capacity_list) / 60, 2),
                                "Traffic Type": (self.thput_obj_dict[ce][obj_name]["obj"].traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": self.thput_obj_dict[ce][obj_name]["obj"].direction,
                                "Upload Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)) + "Mbps",
                                "Download Rate(Mbps)": str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)) + "Mbps",
                                # "Packet Size" : str(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_pdu) + " Bytes"
                            }
                            self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")

                            if( self.thput_obj_dict[ce][obj_name]["obj"].interopability_config):

                                self.overall_report.set_obj_html(_obj_title="Configuration Status of Devices",
                                                    _obj="The table below shows the configuration status of each device (except iOS) with respect to the SSID connection.")
                                self.overall_report.build_objective()

                                configured_dataframe = self.thput_obj_dict[ce][obj_name]["obj"].convert_to_table(self.thput_obj_dict[ce][obj_name]["obj"].configured_devices_check)
                                dataframe1 = pd.DataFrame(configured_dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                            # Loop through iterations and build graphs, tables for each device
                            for i in range(len(iterations_before_test_stopped_by_user)):
                                # rssi_signal_data = []
                                devices_on_running = []
                                download_data = []
                                upload_data = []
                                devices_data_to_create_bar_graph = []
                                # signal_data = []
                                upload_drop = []
                                download_drop = []
                                direction_in_table = []
                                # packet_size_in_table=[]
                                upload_list, download_list = [], []
                                rssi_data = []
                                data_iter = data[data['Iteration'] == i + 1]
                                avg_rtt_data = []

                                # Fetch devices_on_running from real_client_list
                                devices_on_running.append(self.thput_obj_dict[ce][obj_name]["obj"].real_client_list[data1[i][-1] - 1].split(" ")[-1])

                                if self.thput_obj_dict[ce][obj_name]["obj"].interopability_config and devices_on_running[0] in self.thput_obj_dict[ce][obj_name]["obj"].configured_devices_check and not self.thput_obj_dict[ce][obj_name]["obj"].configured_devices_check[devices_on_running[0]]:
                                    continue

                                for k in devices_on_running:
                                    # individual_device_data=[]

                                    # Checking individual device download and upload rate by searching device name in dataframe
                                    columns_with_substring = [col for col in data_iter.columns if k in col]
                                    filtered_df = data_iter[columns_with_substring]
                                    download_col = filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()
                                    upload_col = filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()
                                    upload_drop_col = filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()
                                    download_drop_col = filtered_df[[col for col in filtered_df.columns if "Rx % Drop" in col][0]].values.tolist()
                                    rssi_col = filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()
                                    if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":

                                        # Append download and upload data from filtered dataframe
                                        download_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        upload_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        upload_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        download_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                            len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)))

                                        direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                    elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':

                                        # Append download data from filtered dataframe
                                        download_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Download" in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))

                                        # Append 0 for upload data
                                        upload_data.append(0)
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                            len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        download_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Rx % Drop " in col][0]].values.tolist()[1:dl_len]) / (dl_len - 1)), 2))
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)))

                                        direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                    elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Upload':

                                        # Calculate and append upload and download throughput to lists
                                        upload_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_a_min_bps) / 1000000, 2)))
                                        download_list.append(str(round(int(self.thput_obj_dict[ce][obj_name]["obj"].cx_profile.side_b_min_bps) / 1000000, 2)))
                                        rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                            len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                        upload_drop.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Tx % Drop" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))
                                        avg_rtt_data.append(filtered_df[[col for col in filtered_df.columns if "Average RTT " in col][0]].values.tolist()[-1])
                                        # Append upload data from filtered dataframe
                                        upload_data.append(round((sum(filtered_df[[col for col in filtered_df.columns if "Upload" in col][0]].values.tolist()[1:ul_len]) / (ul_len - 1)), 2))

                                        # Append 0 for download data
                                        download_data.append(0)

                                        direction_in_table.append(self.thput_obj_dict[ce][obj_name]["obj"].direction)
                                data_set_in_graph = []

                                # Depending on the test direction, retrieve corresponding throughput data,
                                # organize it into datasets for graphing, and calculate real-time average throughput values accordingly.
                                if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Download', 'Upload']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Download: "
                                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]) / len(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps, "
                                        f"Upload: {round(sum(upload_data[0:int(incremental_capacity_list[i])]) / len(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':
                                    download_values_list = data['Overall Download'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(download_values_list)
                                    devices_data_to_create_bar_graph.append(download_data)
                                    label_data = ['Download']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Download: "
                                        f"{round(sum(download_data[0:int(incremental_capacity_list[i])]) / len(download_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Upload':
                                    upload_values_list = data['Overall Upload'][data['Iteration'] == i + 1].values.tolist()
                                    data_set_in_graph.append(upload_values_list)
                                    devices_data_to_create_bar_graph.append(upload_data)
                                    label_data = ['Upload']
                                    real_time_data = (
                                        f"Real Time Throughput: Achieved Throughput: Upload: "
                                        f"{round(sum(upload_data[0:int(incremental_capacity_list[i])]) / len(upload_data[0:int(incremental_capacity_list[i])]), 2)} Mbps"
                                    )

                                self.overall_report.set_custom_html(f"<h2><u>{i + 1}. Test On Device {', '.join(devices_on_running)}:</u></h2>")
                                self.overall_report.build_custom()

                                self.overall_report.set_obj_html(
                                    _obj_title=f"{real_time_data}",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph_png = self.thput_obj_dict[ce][obj_name]["obj"].build_line_graph(
                                    data_set=data_set_in_graph,
                                    xaxis_name="Time",
                                    yaxis_name="Throughput (Mbps)",
                                    xaxis_categories=data['TIMESTAMP'][data['Iteration'] == i + 1].values.tolist(),
                                    label=label_data,
                                    graph_image_name=f"line_graph{i}"
                                )
                                logger.info("graph name {}".format(graph_png))
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()

                                self.overall_report.build_graph()
                                x_fig_size = 15
                                y_fig_size = len(devices_on_running) * .5 + 4
                                self.overall_report.set_obj_html(
                                    _obj_title="Per Client Avg-Throughput",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                devices_on_running_trimmed = [n[:17] if len(n) > 17 else n for n in devices_on_running]
                                graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_bar_graph,
                                                                _xaxis_name="Avg Throughput(Mbps)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"image_name{i}_{obj_no}",
                                                                _label=label_data,
                                                                _yaxis_categories=devices_on_running_trimmed,
                                                                _legend_loc="best",
                                                                _legend_box=(1.0, 1.0),
                                                                _show_bar_value=True,
                                                                _figsize=(x_fig_size, y_fig_size)
                                                                )

                                graph_png = graph.build_bar_graph_horizontal()
                                logger.info("graph name {}".format(graph_png))
                                graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_obj_html(
                                    _obj_title="RSSI Of The Clients Connected",
                                    _obj=" ")
                                self.overall_report.build_objective()
                                graph = lf_bar_graph_horizontal(_data_set=[rssi_data],
                                                                _xaxis_name="Signal(-dBm)",
                                                                _yaxis_name="Devices",
                                                                _graph_image_name=f"signal_image_name{i}_{obj_no}",
                                                                _label=['RSSI'],
                                                                _yaxis_categories=devices_on_running_trimmed,
                                                                _legend_loc="best",
                                                                _legend_box=(1.0, 1.0),
                                                                _show_bar_value=True,
                                                                _figsize=(x_fig_size, y_fig_size)
                                                                #    _color=['lightcoral']
                                                                )
                                graph_png = graph.build_bar_graph_horizontal()
                                logger.info("graph name {}".format(graph_png))
                                graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()

                                self.overall_report.set_obj_html(
                                    _obj_title="Detailed Result Table ",
                                    _obj="The below tables provides detailed information for the throughput test on each device.")
                                self.overall_report.build_objective()
                                self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list = [item.split()[-1] if ' ' in item else item for item in self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list]
                                if self.thput_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.thput_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                    test_input_list, pass_fail_list = self.thput_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(device_type, incremental_capacity_list[i], devices_on_running, download_data, upload_data)
                                bk_dataframe = {}

                                # Dataframe changes with respect to groups and profiles in case of interopability
                                if self.thput_obj_dict[ce][obj_name]["obj"].group_name:
                                    interop_tab_data = self.thput_obj_dict[ce][obj_name]["obj"].json_get('/adb/')["devices"]
                                    res_list = []
                                    grp_name = []
                                    if device_type[int(incremental_capacity_list[i]) - 1] != 'Android':
                                        res_list.append(devices_on_running[-1])
                                    else:
                                        for dev in interop_tab_data:
                                            for item in dev.values():
                                                if item['user-name'] == devices_on_running[-1]:
                                                    res_list.append(item['name'].split('.')[2])
                                                    break
                                    for key, value in self.thput_obj_dict[ce][obj_name]["obj"].group_device_map.items():
                                        if res_list[-1] in value:
                                            grp_name.append(key)
                                            break
                                    bk_dataframe["Group Name"] = grp_name[-1]

                                bk_dataframe[" Device Type "] = device_type[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Username"] = devices_on_running[-1]
                                bk_dataframe[" SSID "] = self.thput_obj_dict[ce][obj_name]["obj"].ssid_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" MAC "] = self.thput_obj_dict[ce][obj_name]["obj"].mac_id_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Channel "] = self.thput_obj_dict[ce][obj_name]["obj"].channel_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Mode"] = self.thput_obj_dict[ce][obj_name]["obj"].mode_list[int(incremental_capacity_list[i]) - 1]
                                bk_dataframe[" Offered download rate (Mbps)"] = download_list[-1]
                                bk_dataframe[" Observed Average download rate (Mbps)"] = [str(download_data[-1])]
                                bk_dataframe[" Offered upload rate (Mbps)"] = upload_list[-1]
                                bk_dataframe[" Observed Average upload rate (Mbps)"] = [str(upload_data[-1])]
                                bk_dataframe[" Average RTT (ms) "] = avg_rtt_data[-1]
                                bk_dataframe[" RSSI (dBm)"] = ['' if rssi_data[-1] == 0 else '-' + str(rssi_data[-1])]
                                if self.thput_obj_dict[ce][obj_name]["obj"].direction == "Bi-direction":
                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                elif self.thput_obj_dict[ce][obj_name]["obj"].direction == 'Download':
                                    bk_dataframe[" Average Rx Drop % "] = download_drop
                                    bk_dataframe[" Average Tx Drop % "] = [0.0] * len(download_drop)
                                else:
                                    bk_dataframe[" Average Tx Drop % "] = upload_drop
                                    bk_dataframe[" Average Rx Drop % "] = [0.0] * len(upload_drop)
                                # When pass fail criteria is specified
                                if self.thput_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.thput_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                    bk_dataframe[" Expected " + self.thput_obj_dict[ce][obj_name]["obj"].direction + " rate "] = test_input_list
                                    bk_dataframe[" Status "] = pass_fail_list
                                dataframe1 = pd.DataFrame(bk_dataframe)
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()

                                self.overall_report.set_custom_html('<hr>')
                                self.overall_report.build_custom()

                            if(self.thput_obj_dict[ce][obj_name]["obj"].dowebgui and self.thput_obj_dict[ce][obj_name]["obj"].get_live_view and self.thput_obj_dict[ce][obj_name]["obj"].do_interopability):
                                self.thput_obj_dict[ce][obj_name]["obj"].add_live_view_images_to_report(self.overall_report)
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"ftp_test_{obj_no}"
                        else:
                            break
                
                elif test_name == "ping_test":
                    obj_no = 1
                    obj_name = 'ping_test'
                    if ce == "series":
                        obj_name += "_1" 
                    while obj_name in self.ping_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        params = self.ping_obj_dict[ce][obj_name]["data"].copy()
                        result_json = params["result_json"]
                        result_dir = params["result_dir"]
                        report_path = params["report_path"]
                        config_devices = params["config_devices"]
                        group_device_map = params["group_device_map"]
                        if result_json is not None:
                            self.ping_obj_dict[ce][obj_name]["obj"].result_json = result_json
                        self.overall_report.set_obj_html(_obj_title=f'PING Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        # Test setup information table for devices in device list
                        if config_devices == '':
                            test_setup_info = {
                                'SSID': self.ping_obj_dict[ce][obj_name]["obj"].ssid,
                                'Security': self.ping_obj_dict[ce][obj_name]["obj"].security,
                                'Website / IP': self.ping_obj_dict[ce][obj_name]["obj"].target,
                                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.ping_obj_dict[ce][obj_name]["obj"].sta_list), len(self.ping_obj_dict[ce][obj_name]["obj"].sta_list) - len(self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list), self.ping_obj_dict[ce][obj_name]["obj"].android, self.ping_obj_dict[ce][obj_name]["obj"].windows, self.ping_obj_dict[ce][obj_name]["obj"].linux, self.ping_obj_dict[ce][obj_name]["obj"].mac),
                                'Duration (in minutes)': self.ping_obj_dict[ce][obj_name]["obj"].duration
                            }
                        # Test setup information table for devices in groups
                        else:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_setup_info = {
                                'Configuration': configmap,
                                'Website / IP': self.ping_obj_dict[ce][obj_name]["obj"].target,
                                'No of Devices': '{} (V:{}, A:{}, W:{}, L:{}, M:{})'.format(len(self.ping_obj_dict[ce][obj_name]["obj"].sta_list), len(self.ping_obj_dict[ce][obj_name]["obj"].sta_list) - len(self.ping_obj_dict[ce][obj_name]["obj"].real_sta_list), self.ping_obj_dict[ce][obj_name]["obj"].android, self.ping_obj_dict[ce][obj_name]["obj"].windows, self.ping_obj_dict[ce][obj_name]["obj"].linux, self.ping_obj_dict[ce][obj_name]["obj"].mac),
                                'Duration (in minutes)': self.ping_obj_dict[ce][obj_name]["obj"].duration
                            }
                        if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res:
                            del test_setup_info["Website / IP"]
                            test_setup_info["Ips"] = self.ping_obj_dict[ce][obj_name]["obj"].res_ip_list
                        self.overall_report.test_setup_table(
                            test_setup_data=test_setup_info, value='Test Setup Information')

                        # packets sent vs received vs dropped
                        self.overall_report.set_table_title(
                            'Packets sent vs packets received vs packets dropped')
                        self.overall_report.build_table_title()
                        # graph for the above
                        self.ping_obj_dict[ce][obj_name]["obj"].packets_sent = []
                        self.ping_obj_dict[ce][obj_name]["obj"].packets_received = []
                        self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_names = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_modes = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_channels = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_min = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_max = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_avg = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_mac = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_names_with_errors = []
                        self.ping_obj_dict[ce][obj_name]["obj"].devices_with_errors = []
                        self.ping_obj_dict[ce][obj_name]["obj"].report_names = []
                        self.ping_obj_dict[ce][obj_name]["obj"].remarks = []
                        self.ping_obj_dict[ce][obj_name]["obj"].device_ssid = []
                        # packet_count_data = {}
                        os_type = []
                        for device, device_data in self.ping_obj_dict[ce][obj_name]["obj"].result_json.items():
                            logging.info('Device data: {} {}'.format(device, device_data))
                            if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res:
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_sent.append(int(device_data['sent']))
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_received.append(int(device_data['recv']))
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped.append(int(device_data['dropped']))

                                self.ping_obj_dict[ce][obj_name]["obj"].device_min.append(float(device_data['min_rtt']))
                                self.ping_obj_dict[ce][obj_name]["obj"].device_avg.append(float(device_data['avg_rtt']))
                                self.ping_obj_dict[ce][obj_name]["obj"].device_max.append(float(device_data['max_rtt']))
                                # print("device",device)
                                # device_key = device.split('-')[0]
                                print(self.ping_obj_dict[ce][obj_name]["obj"].cx_dev_map)
                                print(self.ping_obj_dict[ce][obj_name]["obj"].cx_ip_map)
                                if device in self.ping_obj_dict[ce][obj_name]["obj"].cx_dev_map and self.ping_obj_dict[ce][obj_name]["obj"].cx_dev_map[device] != "":
                                    device_name = "{}/{}".format(self.ping_obj_dict[ce][obj_name]["obj"].cx_dev_map[device],self.ping_obj_dict[ce][obj_name]["obj"].cx_ip_map[device])
                                else:
                                    device_name = self.ping_obj_dict[ce][obj_name]["obj"].cx_ip_map[device]
                                self.ping_obj_dict[ce][obj_name]["obj"].device_names.append(device_name)      # endpoint key only
                                self.ping_obj_dict[ce][obj_name]["obj"].report_names.append(device_name)
                            else:
                                os_type.append(device_data['os'])
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_sent.append(int(device_data['sent']))
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_received.append(int(device_data['recv']))
                                self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped.append(int(device_data['dropped']))
                                self.ping_obj_dict[ce][obj_name]["obj"].device_names.append(device_data['name'] + ' ' + device_data['os'])
                                self.ping_obj_dict[ce][obj_name]["obj"].device_modes.append(device_data['mode'])
                                self.ping_obj_dict[ce][obj_name]["obj"].device_channels.append(device_data['channel'])
                                self.ping_obj_dict[ce][obj_name]["obj"].device_mac.append(device_data['mac'])
                                self.ping_obj_dict[ce][obj_name]["obj"].device_ssid.append(device_data['ssid'])
                                self.ping_obj_dict[ce][obj_name]["obj"].device_min.append(float(device_data['min_rtt'].replace(',', '')))
                                self.ping_obj_dict[ce][obj_name]["obj"].device_max.append(float(device_data['max_rtt'].replace(',', '')))
                                self.ping_obj_dict[ce][obj_name]["obj"].device_avg.append(float(device_data['avg_rtt'].replace(',', '')))
                                if (device_data['os'] == 'Virtual'):
                                    self.ping_obj_dict[ce][obj_name]["obj"].report_names.append('{} {}'.format(device, device_data['os'])[0:25])
                                else:
                                    self.ping_obj_dict[ce][obj_name]["obj"].report_names.append('{} {} {}'.format(device, device_data['os'], device_data['name']))
                                if (device_data['remarks'] != []):
                                    self.ping_obj_dict[ce][obj_name]["obj"].device_names_with_errors.append(device_data['name'])
                                    self.ping_obj_dict[ce][obj_name]["obj"].devices_with_errors.append(device)
                                    self.ping_obj_dict[ce][obj_name]["obj"].remarks.append(','.join(device_data['remarks']))
                        x_fig_size = 15
                        y_fig_size = len(self.ping_obj_dict[ce][obj_name]["obj"].device_names) * .5 + 4
                        graph = lf_bar_graph_horizontal(_data_set=[self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped, self.ping_obj_dict[ce][obj_name]["obj"].packets_received, self.ping_obj_dict[ce][obj_name]["obj"].packets_sent],
                                                        _xaxis_name='Packets Count',
                                                        _yaxis_name='Wireless Clients',
                                                        _label=[
                                                            'Packets Loss', 'Packets Received', 'Packets Sent'],
                                                        _graph_image_name=f'Packets sent vs received vs dropped {obj_no}',
                                                        _yaxis_label=self.ping_obj_dict[ce][obj_name]["obj"].report_names,
                                                        _yaxis_categories=self.ping_obj_dict[ce][obj_name]["obj"].report_names,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _graph_title='Packets sent vs received vs dropped',
                                                        _title_size=16,
                                                        _color=['lightgrey',
                                                                'orange', 'steelblue'],
                                                        _color_edge=['black'],
                                                        _bar_height=0.15,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _dpi=96,
                                                        _show_bar_value=False,
                                                        _enable_csv=True,
                                                        _color_name=['lightgrey', 'orange', 'steelblue'])

                        graph_png = graph.build_bar_graph_horizontal()
                        logging.info('graph name {}'.format(graph_png))
                        self.overall_report.set_graph_image(graph_png)
                        # need to move the graph image to the results directory
                        self.overall_report.move_graph_image()
                        self.overall_report.set_csv_filename(graph_png)
                        self.overall_report.move_csv_file()
                        self.overall_report.build_graph()
                        if self.ping_obj_dict[ce][obj_name]["obj"].real:
                            # Calculating the pass/fail criteria when either expected_passfail_val or csv_name is provided
                            if self.ping_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ping_obj_dict[ce][obj_name]["obj"].csv_name:
                                self.ping_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(os_type)
                            # When groups are provided a seperate table will be generated for each group using generate_dataframe
                            if self.ping_obj_dict[ce][obj_name]["obj"].group_name:
                                for key, val in group_device_map.items():
                                    if self.ping_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ping_obj_dict[ce][obj_name]["obj"].csv_name:
                                        dataframe = self.ping_obj_dict[ce][obj_name]["obj"].generate_dataframe(
                                            val,
                                            self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                                            self.ping_obj_dict[ce][obj_name]["obj"].device_mac,
                                            self.ping_obj_dict[ce][obj_name]["obj"].device_channels,
                                            self.ping_obj_dict[ce][obj_name]["obj"].device_ssid,
                                            self.ping_obj_dict[ce][obj_name]["obj"].device_modes,
                                            self.ping_obj_dict[ce][obj_name]["obj"].packets_sent,
                                            self.ping_obj_dict[ce][obj_name]["obj"].packets_received,
                                            self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped,
                                            self.ping_obj_dict[ce][obj_name]["obj"].percent_pac_loss,
                                            self.ping_obj_dict[ce][obj_name]["obj"].test_input_list,
                                            self.ping_obj_dict[ce][obj_name]["obj"].pass_fail_list)
                                    else:
                                        dataframe = self.ping_obj_dict[ce][obj_name]["obj"].generate_dataframe(val, self.ping_obj_dict[ce][obj_name]["obj"].device_names, self.ping_obj_dict[ce][obj_name]["obj"].device_mac, self.ping_obj_dict[ce][obj_name]["obj"].device_channels, self.ping_obj_dict[ce][obj_name]["obj"].device_ssid,
                                                                            self.ping_obj_dict[ce][obj_name]["obj"].device_modes, self.ping_obj_dict[ce][obj_name]["obj"].packets_sent, self.ping_obj_dict[ce][obj_name]["obj"].packets_received, self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped, [], [], [])
                                    if dataframe:
                                        self.overall_report.set_obj_html("", "Group: {}".format(key))
                                        self.overall_report.build_objective()
                                        dataframe1 = pd.DataFrame(dataframe)
                                        self.overall_report.set_table_dataframe(dataframe1)
                                        self.overall_report.build_table()

                            else:
                                if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res:
                                    dataframe1 = pd.DataFrame({
                                        'Endpoint': self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                                        'Packets Sent': self.ping_obj_dict[ce][obj_name]["obj"].packets_sent,
                                        'Packets Received': self.ping_obj_dict[ce][obj_name]["obj"].packets_received,
                                        'Packets Loss': self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped,
                                    })
                                else:
                                    dataframe1 = pd.DataFrame({
                                        'Wireless Client': self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                                        'MAC': self.ping_obj_dict[ce][obj_name]["obj"].device_mac,
                                        'Channel': self.ping_obj_dict[ce][obj_name]["obj"].device_channels,
                                        'SSID ': self.ping_obj_dict[ce][obj_name]["obj"].device_ssid,
                                        'Mode': self.ping_obj_dict[ce][obj_name]["obj"].device_modes,
                                        'Packets Sent': self.ping_obj_dict[ce][obj_name]["obj"].packets_sent,
                                        'Packets Received': self.ping_obj_dict[ce][obj_name]["obj"].packets_received,
                                        'Packets Loss': self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped,
                                    })
                                if self.ping_obj_dict[ce][obj_name]["obj"].expected_passfail_val or self.ping_obj_dict[ce][obj_name]["obj"].csv_name:
                                    dataframe1[" Percentage of Packet loss %"] = self.ping_obj_dict[ce][obj_name]["obj"].percent_pac_loss
                                    dataframe1['Expected Packet loss %'] = self.ping_obj_dict[ce][obj_name]["obj"].test_input_list
                                    dataframe1['Status'] = self.ping_obj_dict[ce][obj_name]["obj"].pass_fail_list
                                self.overall_report.set_table_dataframe(dataframe1)
                                self.overall_report.build_table()
                        else:
                            dataframe1 = pd.DataFrame({
                                'Wireless Client': self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                                'MAC': self.ping_obj_dict[ce][obj_name]["obj"].device_mac,
                                'Channel': self.ping_obj_dict[ce][obj_name]["obj"].device_channels,
                                'SSID ': self.ping_obj_dict[ce][obj_name]["obj"].device_ssid,
                                'Mode': self.ping_obj_dict[ce][obj_name]["obj"].device_modes,
                                'Packets Sent': self.ping_obj_dict[ce][obj_name]["obj"].packets_sent,
                                'Packets Received': self.ping_obj_dict[ce][obj_name]["obj"].packets_received,
                                'Packets Loss': self.ping_obj_dict[ce][obj_name]["obj"].packets_dropped,
                            })
                            self.overall_report.set_table_dataframe(dataframe1)
                            self.overall_report.build_table()

                        # packets latency graph
                        self.overall_report.set_table_title('Ping Latency Graph')
                        self.overall_report.build_table_title()

                        graph = lf_bar_graph_horizontal(_data_set=[self.ping_obj_dict[ce][obj_name]["obj"].device_min, self.ping_obj_dict[ce][obj_name]["obj"].device_avg, self.ping_obj_dict[ce][obj_name]["obj"].device_max],
                                                        _xaxis_name='Time (ms)',
                                                        _yaxis_name='Wireless Clients',
                                                        _label=[
                                                            'Min Latency (ms)', 'Average Latency (ms)', 'Max Latency (ms)'],
                                                        _graph_image_name=f'Ping Latency per client {obj_no}',
                                                        _yaxis_label=self.ping_obj_dict[ce][obj_name]["obj"].report_names,
                                                        _yaxis_categories=self.ping_obj_dict[ce][obj_name]["obj"].report_names,
                                                        _yaxis_step=1,
                                                        _yticks_font=8,
                                                        _graph_title='Ping Latency per client',
                                                        _title_size=16,
                                                        _color=['lightgrey',
                                                                'orange', 'steelblue'],
                                                        _color_edge='black',
                                                        _bar_height=0.15,
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _legend_loc="best",
                                                        _legend_box=(1.0, 1.0),
                                                        _dpi=96,
                                                        _show_bar_value=False,
                                                        _enable_csv=True,
                                                        _color_name=['lightgrey', 'orange', 'steelblue'])

                        graph_png = graph.build_bar_graph_horizontal()
                        logging.info('graph name {}'.format(graph_png))
                        self.overall_report.set_graph_image(graph_png)
                        # need to move the graph image to the results directory
                        self.overall_report.move_graph_image()
                        self.overall_report.set_csv_filename(graph_png)
                        self.overall_report.move_csv_file()
                        self.overall_report.build_graph()

                        if self.ping_obj_dict[ce][obj_name]["obj"].sta_to_res:
                            dataframe2 = pd.DataFrame({
                            'Endpoint': self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                            'Min Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_min,
                            'Average Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_avg,
                            'Max Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_max
                        })
                        else:
                            dataframe2 = pd.DataFrame({
                                'Wireless Client': self.ping_obj_dict[ce][obj_name]["obj"].device_names,
                                'MAC': self.ping_obj_dict[ce][obj_name]["obj"].device_mac,
                                'Channel': self.ping_obj_dict[ce][obj_name]["obj"].device_channels,
                                'SSID ': self.ping_obj_dict[ce][obj_name]["obj"].device_ssid,
                                'Mode': self.ping_obj_dict[ce][obj_name]["obj"].device_modes,
                                'Min Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_min,
                                'Average Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_avg,
                                'Max Latency (ms)': self.ping_obj_dict[ce][obj_name]["obj"].device_max
                            })
                        self.overall_report.set_table_dataframe(dataframe2)
                        self.overall_report.build_table()

                        # check if there are remarks for any device. If there are remarks, build table else don't
                        if (self.ping_obj_dict[ce][obj_name]["obj"].remarks != []):
                            self.overall_report.set_table_title('Notes')
                            self.overall_report.build_table_title()
                            dataframe3 = pd.DataFrame({
                                'Wireless Client': self.ping_obj_dict[ce][obj_name]["obj"].device_names_with_errors,
                                'Port': self.ping_obj_dict[ce][obj_name]["obj"].devices_with_errors,
                                'Remarks': self.ping_obj_dict[ce][obj_name]["obj"].remarks
                            })
                            self.overall_report.set_table_dataframe(dataframe3)
                            self.overall_report.build_table()

                        # closing
                        # self.overall_report.build_custom()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"ping_test_{obj_no}"
                        else:
                            break
                
                elif test_name == "qos_test":
                    obj_no = 1
                    obj_name = 'qos_test'
                    if ce == "series":
                        obj_name += "_1" 
                    while obj_name in self.qos_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        params = self.qos_obj_dict[ce][obj_name]["data"]
                        data = params["data"].copy() if isinstance(params["data"], (list, dict, set)) else params["data"]
                        input_setup_info = params["input_setup_info"].copy() if isinstance(params["input_setup_info"], (list, dict, set)) else params["input_setup_info"]
                        connections_download_avg = params["connections_download_avg"].copy() if isinstance(params["connections_download_avg"], (list, dict, set)) else params["connections_download_avg"]
                        connections_upload_avg = params["connections_upload_avg"].copy() if isinstance(params["connections_upload_avg"], (list, dict, set)) else params["connections_upload_avg"]
                        avg_drop_a = params["avg_drop_a"].copy() if isinstance(params["avg_drop_a"], (list, dict, set)) else params["avg_drop_a"]
                        avg_drop_b = params["avg_drop_b"].copy() if isinstance(params["avg_drop_b"], (list, dict, set)) else params["avg_drop_b"]
                        report_path = params["report_path"].copy() if isinstance(params["report_path"], (list, dict, set)) else params["report_path"]
                        result_dir_name = params["result_dir_name"].copy() if isinstance(params["result_dir_name"], (list, dict, set)) else params["result_dir_name"]
                        selected_real_clients_names = params["selected_real_clients_names"].copy() if isinstance(params["selected_real_clients_names"], (list, dict, set)) else params["selected_real_clients_names"]
                        config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]
                        self.qos_obj_dict[ce][obj_name]["obj"].ssid_list = self.qos_obj_dict[ce][obj_name]["obj"].get_ssid_list(self.qos_obj_dict[ce][obj_name]["obj"].input_devices_list)
                        if selected_real_clients_names is not None:
                            self.qos_obj_dict[ce][obj_name]["obj"].num_stations = selected_real_clients_names
                        data_set, load, res = self.qos_obj_dict[ce][obj_name]["obj"].generate_graph_data_set(data)
                        # Initialize counts and lists for device types
                        android_devices, windows_devices, linux_devices, ios_devices, ios_mob_devices = 0, 0, 0, 0, 0
                        all_devices_names = []
                        device_type = []
                        total_devices = ""
                        for i in self.qos_obj_dict[ce][obj_name]["obj"].real_client_list:
                            split_device_name = i.split(" ")
                            if 'android' in split_device_name:
                                all_devices_names.append(split_device_name[2] + ("(Android)"))
                                device_type.append("Android")
                                android_devices += 1
                            elif 'Win' in split_device_name:
                                all_devices_names.append(split_device_name[2] + ("(Windows)"))
                                device_type.append("Windows")
                                windows_devices += 1
                            elif 'Lin' in split_device_name:
                                all_devices_names.append(split_device_name[2] + ("(Linux)"))
                                device_type.append("Linux")
                                linux_devices += 1
                            elif 'Mac' in split_device_name:
                                all_devices_names.append(split_device_name[2] + ("(Mac)"))
                                device_type.append("Mac")
                                ios_devices += 1
                            elif 'iOS' in split_device_name:
                                all_devices_names.append(split_device_name[2] + ("(iOS)"))
                                device_type.append("iOS")
                                ios_mob_devices += 1

                        # Build total_devices string based on counts
                        if android_devices > 0:
                            total_devices += f" Android({android_devices})"
                        if windows_devices > 0:
                            total_devices += f" Windows({windows_devices})"
                        if linux_devices > 0:
                            total_devices += f" Linux({linux_devices})"
                        if ios_devices > 0:
                            total_devices += f" Mac({ios_devices})"
                        if ios_mob_devices > 0:
                            total_devices += f" iOS({ios_mob_devices})"

                        # Test setup information table for devices in device list
                        if config_devices == "":
                            test_setup_info = {
                                "Device List": ", ".join(all_devices_names),
                                "Number of Stations": "Total" + f"({self.qos_obj_dict[ce][obj_name]['obj'].num_stations})" + total_devices,
                                "AP Model": self.qos_obj_dict[ce][obj_name]["obj"].ap_name,
                                "SSID": self.qos_obj_dict[ce][obj_name]["obj"].ssid,
                                "Traffic Duration in hours": round(int(self.qos_obj_dict[ce][obj_name]["obj"].test_duration) / 3600, 2),
                                "Security": self.qos_obj_dict[ce][obj_name]["obj"].security,
                                "Protocol": (self.qos_obj_dict[ce][obj_name]["obj"].traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": self.qos_obj_dict[ce][obj_name]["obj"].direction,
                                "TOS": self.qos_obj_dict[ce][obj_name]["obj"].tos,
                                "Per TOS Load in Mbps": load
                            }
                        # Test setup information table for devices in groups
                        else:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_setup_info = {
                                "AP Model": self.qos_obj_dict[ce][obj_name]["obj"].ap_name,
                                'Configuration': configmap,
                                "Traffic Duration in hours": round(int(self.qos_obj_dict[ce][obj_name]["obj"].test_duration) / 3600, 2),
                                "Security": self.qos_obj_dict[ce][obj_name]["obj"].security,
                                "Protocol": (self.qos_obj_dict[ce][obj_name]["obj"].traffic_type.strip("lf_")).upper(),
                                "Traffic Direction": self.qos_obj_dict[ce][obj_name]["obj"].direction,
                                "TOS": self.qos_obj_dict[ce][obj_name]["obj"].tos,
                                "Per TOS Load in Mbps": load
                            }
                        print(res["throughput_table_df"])
                        self.overall_report.set_obj_html(_obj_title=f'QOS Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
                        self.overall_report.set_table_title(
                            f"Overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} Throughput for all TOS i.e BK | BE | Video (VI) | Voice (VO)")
                        self.overall_report.build_table_title()
                        df_throughput = pd.DataFrame(res["throughput_table_df"])
                        self.overall_report.set_table_dataframe(df_throughput)
                        self.overall_report.build_table()
                        for key in res["graph_df"]:
                            self.overall_report.set_obj_html(
                                _obj_title=f"Overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput for {len(self.qos_obj_dict[ce][obj_name]['obj'].input_devices_list)} clients with different TOS.",
                                _obj=f"The below graph represents overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput for all "
                                    "connected stations running BK, BE, VO, VI traffic with different "
                                    f"intended loads{load} per tos")
                        self.overall_report.build_objective()
                        graph = lf_bar_graph(_data_set=data_set,
                                            _xaxis_name="Load per Type of Service",
                                            _yaxis_name="Throughput (Mbps)",
                                            _xaxis_categories=["BK,BE,VI,VO"],
                                            _xaxis_label=['1 Mbps', '2 Mbps', '3 Mbps', '4 Mbps', '5 Mbps'],
                                            _graph_image_name=f"tos_download_{key}Hz {obj_no}",
                                            _label=["BK", "BE", "VI", "VO"],
                                            _xaxis_step=1,
                                            _graph_title=f"Overall {self.qos_obj_dict[ce][obj_name]['obj'].direction} throughput – BK,BE,VO,VI traffic streams",
                                            _title_size=16,
                                            _color=['orange', 'lightcoral', 'steelblue', 'lightgrey'],
                                            _color_edge='black',
                                            _bar_width=0.15,
                                            _figsize=(18, 6),
                                            _legend_loc="best",
                                            _legend_box=(1.0, 1.0),
                                            _dpi=96,
                                            _show_bar_value=True,
                                            _enable_csv=True,
                                            _color_name=['orange', 'lightcoral', 'steelblue', 'lightgrey'])
                        graph_png = graph.build_bar_graph()
                        print("graph name {}".format(graph_png))
                        self.overall_report.set_graph_image(graph_png)
                        # need to move the graph image to the results directory
                        self.overall_report.move_graph_image()
                        self.overall_report.set_csv_filename(graph_png)
                        self.overall_report.move_csv_file()
                        self.overall_report.build_graph()
                        self.qos_obj_dict[ce][obj_name]["obj"].generate_individual_graph(res, self.overall_report, connections_download_avg, connections_upload_avg, avg_drop_a, avg_drop_b,obj_no)
                        self.overall_report.test_setup_table(test_setup_data=input_setup_info, value="Information")
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"qos_test_{obj_no}"
                        else:
                            break
                
                elif test_name == "mcast_test":
                    obj_no=1
                    obj_name = "mcast_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.mcast_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        print('is error',self.mcast_obj_dict)
                        params = self.mcast_obj_dict[ce][obj_name]["data"].copy()
                        config_devices = params["config_devices"].copy() if isinstance(params["config_devices"], (list, dict, set)) else params["config_devices"]
                        group_device_map = params["group_device_map"].copy() if isinstance(params["group_device_map"], (list, dict, set)) else params["group_device_map"]

                        # self.mcast_obj_dict[ce][obj_name]["obj"].update_a()
                        # self.mcast_obj_dict[ce][obj_name]["obj"].update_b()
                        test_setup_info = {
                            "DUT Name": self.mcast_obj_dict[ce][obj_name]["obj"].dut_model_num,
                            "DUT Hardware Version": self.mcast_obj_dict[ce][obj_name]["obj"].dut_hw_version,
                            "DUT Software Version": self.mcast_obj_dict[ce][obj_name]["obj"].dut_sw_version,
                            "DUT Serial Number": self.mcast_obj_dict[ce][obj_name]["obj"].dut_serial_num,
                        }
                        self.overall_report.set_obj_html(_obj_title=f'MULTICAST Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Device Under Test Information")
                        self.overall_report.build_table_title()
                        self.overall_report.test_setup_table(value="Device Under Test",
                                                    test_setup_data=test_setup_info)
                        # For real devices when groups specified for configuration
                        if self.mcast_obj_dict[ce][obj_name]["obj"].real and self.mcast_obj_dict[ce][obj_name]["obj"].group_name:
                            group_names = ', '.join(config_devices.keys())
                            profile_names = ', '.join(config_devices.values())
                            configmap = "Groups:" + group_names + " -> Profiles:" + profile_names
                            test_input_info = {
                                "LANforge ip": self.mcast_obj_dict[ce][obj_name]["obj"].lfmgr,
                                "LANforge port": self.mcast_obj_dict[ce][obj_name]["obj"].lfmgr_port,
                                "Upstream": self.mcast_obj_dict[ce][obj_name]["obj"].upstream_port,
                                "Test Duration": self.mcast_obj_dict[ce][obj_name]["obj"].test_duration,
                                "Test Configuration": configmap,
                                "Polling Interval": self.mcast_obj_dict[ce][obj_name]["obj"].polling_interval,
                                "Total No. of Devices": self.mcast_obj_dict[ce][obj_name]["obj"].station_count,
                            }
                        else:
                            test_input_info = {
                                "LANforge ip": self.mcast_obj_dict[ce][obj_name]["obj"].lfmgr,
                                "LANforge port": self.mcast_obj_dict[ce][obj_name]["obj"].lfmgr_port,
                                "Upstream": self.mcast_obj_dict[ce][obj_name]["obj"].upstream_port,
                                "Test Duration": self.mcast_obj_dict[ce][obj_name]["obj"].test_duration,
                                "Polling Interval": self.mcast_obj_dict[ce][obj_name]["obj"].polling_interval,
                                "Total No. of Devices": self.mcast_obj_dict[ce][obj_name]["obj"].station_count,
                            }

                        self.overall_report.set_table_title("Test Configuration")
                        self.overall_report.build_table_title()
                        self.overall_report.test_setup_table(value="Test Configuration",
                                                    test_setup_data=test_input_info)

                        self.overall_report.set_table_title("Radio Configuration")
                        self.overall_report.build_table_title()

                        wifi_mode_dict = {
                            0: 'AUTO',  # 802.11g
                            1: '802.11a',  # 802.11a
                            2: '802.11b',  # 802.11b
                            3: '802.11g',  # 802.11g
                            4: '802.11abg',  # 802.11abg
                            5: '802.11abgn',  # 802.11abgn
                            6: '802.11bgn',  # 802.11bgn
                            7: '802.11bg',  # 802.11bg
                            8: '802.11abgnAC',  # 802.11abgn-AC
                            9: '802.11anAC',  # 802.11an-AC
                            10: '802.11an',  # 802.11an
                            11: '802.11bgnAC',  # 802.11bgn-AC
                            12: '802.11abgnAX',  # 802.11abgn-A+
                            #     a/b/g/n/AC/AX (dual-band AX) support
                            13: '802.11bgnAX',  # 802.11bgn-AX
                            14: '802.11anAX',  # 802.11an-AX
                            15: '802.11aAX',  # 802.11a-AX (6E disables /n and /ac)
                            16: '802.11abgnEHT',  # 802.11abgn-EHT  a/b/g/n/AC/AX/EHT (dual-band AX) support
                            17: '802.11bgnEHT',  # 802.11bgn-EHT
                            18: '802.11anEHT',  # 802.11an-ETH
                            19: '802.11aBE',  # 802.11a-EHT (6E disables /n and /ac)
                        }

                        for (
                                radio_,
                                ssid_,
                                _ssid_password_,  # do not print password
                                ssid_security_,
                                mode_,
                                wifi_enable_flags_list_,
                                _reset_port_enable_,
                                _reset_port_time_min_,
                                _reset_port_time_max_) in zip(
                                self.mcast_obj_dict[ce][obj_name]["obj"].radio_name_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].ssid_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].ssid_password_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].ssid_security_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].wifi_mode_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].enable_flags_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].reset_port_enable_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].reset_port_time_min_list,
                                self.mcast_obj_dict[ce][obj_name]["obj"].reset_port_time_max_list):

                            mode_value = wifi_mode_dict[int(mode_)]

                            radio_info = {
                                "SSID": ssid_,
                                "Security": ssid_security_,
                                "Wifi mode set": mode_value,
                                'Wifi Enable Flags': wifi_enable_flags_list_
                            }
                            self.overall_report.test_setup_table(value=radio_, test_setup_data=radio_info)

                        # TODO move the graphing to the class so it may be called as a service

                        # Graph TOS data
                        # Once the data is stopped can collect the data for the cx's both multi cast and uni cast
                        # if the traffic is still running will gather the running traffic
                        # self.mcast_obj_dict[ce][obj_name]["obj"].evaluate_qos()

                        # graph BK A
                        # try to do as a loop
                        logger.info(f"BEFORE REAL A {self.mcast_obj_dict[ce][obj_name]['obj'].client_dict_A}")
                        tos_list = ['BK', 'BE', 'VI', 'VO']
                        if self.mcast_obj_dict[ce][obj_name]["obj"].real:
                            tos_types = ['BE', 'BK', 'VI', 'VO']
                            print("BOOLLLLL",self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B is self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A)
                            for tos_key in tos_types:
                                if tos_key in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A:
                                    tos_data = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos_key]

                                    # Filter A side
                                    traffic_proto_A = tos_data.get("traffic_protocol_A", [])
                                    indices_to_keep_A = [i for i, proto in enumerate(traffic_proto_A) if proto == "Mcast"]

                                    # Filter B side
                                    traffic_proto_B = tos_data.get("traffic_protocol_B", [])
                                    indices_to_keep_B = [i for i, proto in enumerate(traffic_proto_B) if proto == "Mcast"]

                                    for key in list(tos_data.keys()):
                                        if key in ["colors", "labels"]:
                                            continue  # Keep as-is

                                        if key.endswith('_A'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_A if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list

                                        elif key.endswith('_B'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_B if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list
                            for tos_key in tos_types:
                                if tos_key in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B:
                                    tos_data = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos_key]

                                    # Filter A side
                                    traffic_proto_A = tos_data.get("traffic_protocol_A", [])
                                    indices_to_keep_A = [i for i, proto in enumerate(traffic_proto_A) if proto == "Mcast"]

                                    # Filter B side
                                    traffic_proto_B = tos_data.get("traffic_protocol_B", [])
                                    indices_to_keep_B = [i for i, proto in enumerate(traffic_proto_B) if proto == "Mcast"]

                                    for key in list(tos_data.keys()):
                                        if key in ["colors", "labels"]:
                                            continue  # Keep as-is

                                        if key.endswith('_A'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_A if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list

                                        elif key.endswith('_B'):
                                            filtered_list = [tos_data[key][i] for i in indices_to_keep_B if i < len(tos_data[key])]
                                            tos_data[key] = filtered_list
                        # logger.info(f"AFTER REAL A {self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A}")
                        for tos in tos_list:
                            print(self.mcast_obj_dict[ce][obj_name]["obj"].tos)
                            if tos not in self.mcast_obj_dict[ce][obj_name]["obj"].tos:
                                continue
                            if (self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["ul_A"] and self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["dl_A"]):
                                min_bps_a = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A["min_bps_a"]
                                min_bps_b = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A["min_bps_b"]

                                dataset_list = [self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["ul_A"], self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["dl_A"]]
                                # TODO possibly explain the wording for upload and download
                                dataset_length = len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["ul_A"])
                                x_fig_size = 20
                                y_fig_size = len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"]) * .4 + 5
                                logger.debug("length of clients_A {clients} resource_alias_A {alias_A}".format(
                                    clients=len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"]), alias_A=len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["resource_alias_A"])))
                                logger.debug("clients_A {clients}".format(clients=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"]))
                                logger.debug("resource_alias_A {alias_A}".format(alias_A=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["resource_alias_A"]))

                                if int(min_bps_a) != 0:
                                    self.overall_report.set_obj_html(
                                        _obj_title=f"Individual throughput measured  upload tcp or udp bps: {min_bps_a},  download tcp, udp, or mcast  bps: {min_bps_b} station for traffic {tos} (WiFi).",
                                        _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                        f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                        f"Throughput in Mbps”.")
                                else:
                                    self.overall_report.set_obj_html(
                                        _obj_title=f"Individual throughput mcast download bps: {min_bps_b} traffic {tos} (WiFi).",
                                        _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                        f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                        f"Throughput in Mbps”.")

                                self.overall_report.build_objective()

                                graph = lf_bar_graph_horizontal(_data_set=dataset_list,
                                                                        _xaxis_name="Throughput in bps",
                                                                        _yaxis_name="Client names",
                                                                        # _yaxis_categories=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"],
                                                                        _yaxis_categories=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["resource_alias_A"],
                                                                        _graph_image_name=f"{tos}_A{obj_no}",
                                                                        _label=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['labels'],
                                                                        _color_name=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['colors'],
                                                                        _color_edge=['black'],
                                                                        # traditional station side -A
                                                                        _graph_title=f"Individual {tos} client side traffic measurement - side a (downstream)",
                                                                        _title_size=10,
                                                                        _figsize=(x_fig_size, y_fig_size),
                                                                        _show_bar_value=True,
                                                                        _enable_csv=True,
                                                                        _text_font=8,
                                                                        _legend_loc="best",
                                                                        _legend_box=(1.0, 1.0)
                                                                        )
                                graph_png = graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_csv_filename(graph_png)
                                self.overall_report.move_csv_file()
                                if(self.mcast_obj_dict[ce][obj_name]["obj"].dowebgui and self.mcast_obj_dict[ce][obj_name]["obj"].get_live_view):
                                    for floor in range(0,int(self.mcast_obj_dict[ce][obj_name]["obj"].total_floors)):
                                        script_dir = os.path.dirname(os.path.abspath(__file__))
                                        throughput_image_path = os.path.join(script_dir, "heatmap_images", f"{self.mcast_obj_dict[ce][obj_name]['obj'].test_name}_throughput_{floor+1}.png")
                                        rssi_image_path = os.path.join(script_dir, "heatmap_images", f"{self.mcast_obj_dict[ce][obj_name]['obj'].test_name}_rssi_{floor+1}.png")
                                        timeout = 60  # seconds
                                        start_time = time.time()

                                        while not (os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path)):
                                            if time.time() - start_time > timeout:
                                                print("Timeout: Images not found within 60 seconds.")
                                                break
                                            time.sleep(1)
                                        while not os.path.exists(throughput_image_path) and not os.path.exists(rssi_image_path):
                                            if os.path.exists(throughput_image_path) and os.path.exists(rssi_image_path):
                                                break
                                            # time.sleep(10)
                                        if os.path.exists(throughput_image_path):
                                            self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                            self.overall_report.build_custom()
                                            # self.overall_report.set_custom_html("<h2>Average Throughput Heatmap: </h2>")
                                            # self.overall_report.build_custom()
                                            self.overall_report.set_custom_html(f'<img src="file://{throughput_image_path}"></img>')
                                            self.overall_report.build_custom()
                                            # os.remove(throughput_image_path)

                                        if os.path.exists(rssi_image_path):
                                            self.overall_report.set_custom_html('<div style="page-break-before: always;"></div>')
                                            self.overall_report.build_custom()
                                            # self.overall_report.set_custom_html("<h2>Average RSSI Heatmap: </h2>")
                                            # self.overall_report.build_custom()
                                            self.overall_report.set_custom_html(f'<img src="file://{rssi_image_path}"></img>')
                                            self.overall_report.build_custom()
                                            # os.remove(rssi_image_path)

                                # For real devices appending the required data for pass fail criteria
                                if self.mcast_obj_dict[ce][obj_name]["obj"].real:
                                    up, down, off_up, off_down = [], [], [], []
                                    for i in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ul_A']:
                                        up.append(int(i) / 1000000)
                                    for i in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['dl_A']:
                                        down.append(int(i) / 1000000)
                                    for i in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_upload_rate_A']:
                                        off_up.append(int(i) / 1_000_000)
                                    for i in self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_download_rate_A']:
                                        off_down.append(int(i) / 1000000)
                                    # if either 'expected_passfail_value' or 'device_csv_name' is provided for pass/fail evaluation
                                    if self.mcast_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.mcast_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                        test_input_list, pass_fail_list = self.mcast_obj_dict[ce][obj_name]["obj"].get_pass_fail_list(tos, up, down)

                                if self.mcast_obj_dict[ce][obj_name]["obj"].real:
                                    # When groups and profiles specifed for configuration
                                    if self.mcast_obj_dict[ce][obj_name]["obj"].group_name:
                                        for key, val in group_device_map.items():
                                            # Generating Dataframe when Groups with their profiles and pass_fail case is specified
                                            if self.mcast_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.mcast_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                                dataframe = self.mcast_obj_dict[ce][obj_name]["obj"].generate_dataframe(
                                                    val,
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_alias_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_eid_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_host_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_hw_ver_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['port_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mode_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mac_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ssid_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['channel_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_type_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_protocol_A'],
                                                    off_up,
                                                    off_down,
                                                    up,
                                                    down,
                                                    test_input_list,
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['download_rx_drop_percent_A'],
                                                    pass_fail_list)
                                            # Generating Dataframe for groups when pass_fail case is not specified
                                            else:
                                                dataframe = self.mcast_obj_dict[ce][obj_name]["obj"].generate_dataframe(
                                                    val,
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_alias_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_eid_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_host_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_hw_ver_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['port_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mode_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mac_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ssid_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['channel_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_type_A'],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_protocol_A'],
                                                    off_up,
                                                    off_down,
                                                    up,
                                                    down,
                                                    [],
                                                    self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['download_rx_drop_percent_A'],
                                                    [],)
                                            # When the client exists in either group.
                                            if dataframe:
                                                self.overall_report.set_obj_html("", "Group: {}".format(key))
                                                self.overall_report.build_objective()
                                                dataframe1 = pd.DataFrame(dataframe)
                                                self.overall_report.set_table_dataframe(dataframe1)
                                                self.overall_report.build_table()
                                    else:
                                        tos_dataframe_A = {
                                            " Client Alias ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_alias_A'],
                                            " Host eid ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_eid_A'],
                                            " Host Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_host_A'],
                                            " Device Type / Hw Ver ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_hw_ver_A'],
                                            " Endp Name": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"],
                                            # TODO : port A being set to many times
                                            " Port Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['port_A'],
                                            " Mode ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mode_A'],
                                            " Mac ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mac_A'],
                                            " SSID ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ssid_A'],
                                            " Channel ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['channel_A'],
                                            " Type of traffic ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_type_A'],
                                            " Traffic Protocol ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_protocol_A'],
                                            " Offered Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_upload_rate_A'],
                                            " Offered Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_download_rate_A'],
                                            " Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ul_A'],
                                            " Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['dl_A'],
                                            " Drop Percentage (%)": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['download_rx_drop_percent_A'],
                                        }
                                        # When pass_Fail criteria specified
                                        if self.mcast_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.mcast_obj_dict[ce][obj_name]["obj"].device_csv_name:
                                            tos_dataframe_A[" Expected " + 'Download' + " Rate"] = [float(x) * 10**6 for x in test_input_list]
                                            tos_dataframe_A[" Status "] = pass_fail_list

                                        dataframe3 = pd.DataFrame(tos_dataframe_A)
                                        self.overall_report.set_table_dataframe(dataframe3)
                                        self.overall_report.build_table()

                                # For virtual clients
                                else:
                                    tos_dataframe_A = {
                                        " Client Alias ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_alias_A'],
                                        " Host eid ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_eid_A'],
                                        " Host Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_host_A'],
                                        " Device Type / Hw Ver ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['resource_hw_ver_A'],
                                        " Endp Name": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]["clients_A"],
                                        " Port Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['port_A'],
                                        " Mode ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mode_A'],
                                        " Mac ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['mac_A'],
                                        " SSID ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ssid_A'],
                                        " Channel ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['channel_A'],
                                        " Type of traffic ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_type_A'],
                                        " Traffic Protocol ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['traffic_protocol_A'],
                                        " Offered Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_upload_rate_A'],
                                        " Offered Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['offered_download_rate_A'],
                                        " Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['ul_A'],
                                        " Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['dl_A'],
                                        " Drop Percentage (%)": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_A[tos]['download_rx_drop_percent_A'],
                                    }
                                    dataframe3 = pd.DataFrame(tos_dataframe_A)
                                    self.overall_report.set_table_dataframe(dataframe3)
                                    self.overall_report.build_table()

                        # TODO both client_dict_A and client_dict_B contains the same information
                        for tos in tos_list:
                            if (self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["ul_B"] and self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["dl_B"]):
                                min_bps_a = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B["min_bps_a"]
                                min_bps_b = self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B["min_bps_b"]

                                dataset_list = [self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["ul_B"], self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["dl_B"]]
                                dataset_length = len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["ul_B"])

                                x_fig_size = 20
                                y_fig_size = len(self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["clients_B"]) * .4 + 5

                                self.overall_report.set_obj_html(
                                    _obj_title=f"Individual throughput upstream endp,  offered upload bps: {min_bps_a} offered download bps: {min_bps_b} /station for traffic {tos} (WiFi).",
                                    _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                                    f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                                    f"Throughput in Mbps”.")
                                self.overall_report.build_objective()

                                graph = lf_bar_graph_horizontal(_data_set=dataset_list,
                                                                        _xaxis_name="Throughput in bps",
                                                                        _yaxis_name="Client names",
                                                                        # _yaxis_categories=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["clients_B"],
                                                                        _yaxis_categories=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["resource_alias_B"],
                                                                        _graph_image_name=f"{tos}_B{obj_no}",
                                                                        _label=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['labels'],
                                                                        _color_name=self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['colors'],
                                                                        _color_edge=['black'],
                                                                        _graph_title=f"Individual {tos} upstream side traffic measurement - side b (WIFI) traffic",
                                                                        _title_size=10,
                                                                        _figsize=(x_fig_size, y_fig_size),
                                                                        _show_bar_value=True,
                                                                        _enable_csv=True,
                                                                        _text_font=8,
                                                                        _legend_loc="best",
                                                                        _legend_box=(1.0, 1.0)
                                                                        )
                                graph_png = graph.build_bar_graph_horizontal()
                                self.overall_report.set_graph_image(graph_png)
                                self.overall_report.move_graph_image()
                                self.overall_report.build_graph()
                                self.overall_report.set_csv_filename(graph_png)
                                self.overall_report.move_csv_file()

                                tos_dataframe_B = {
                                    " Client Alias ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['resource_alias_B'],
                                    " Host eid ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['resource_eid_B'],
                                    " Host Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['resource_host_B'],
                                    " Device Type / HW Ver ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['resource_hw_ver_B'],
                                    " Endp Name": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]["clients_B"],
                                    # TODO get correct size
                                    " Port Name ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['port_B'],
                                    " Mode ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['mode_B'],
                                    " Mac ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['mac_B'],
                                    " SSID ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['ssid_B'],
                                    " Channel ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['channel_B'],
                                    " Type of traffic ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['traffic_type_B'],
                                    " Traffic Protocol ": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['traffic_protocol_B'],
                                    " Offered Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['offered_upload_rate_B'],
                                    " Offered Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['offered_download_rate_B'],
                                    " Upload Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['ul_B'],
                                    " Download Rate Per Client": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['dl_B'],
                                    " Drop Percentage (%)": self.mcast_obj_dict[ce][obj_name]["obj"].client_dict_B[tos]['download_rx_drop_percent_B']
                                }

                                dataframe3 = pd.DataFrame(tos_dataframe_B)
                                self.overall_report.set_table_dataframe(dataframe3)
                                self.overall_report.build_table()

                        # L3 total traffic # TODO csv_results_file present yet not readable
                        # self.overall_report.set_table_title("Total Layer 3 Cross-Connect Traffic across all Stations")
                        # self.overall_report.build_table_title()
                        # self.overall_report.set_table_dataframe_from_csv(self.mcast_obj_dict[ce][obj_name]["obj"].csv_results_file)
                        # self.overall_report.build_table()

                        # empty dictionarys evaluate to false , placing tables in output
                        if bool(self.mcast_obj_dict[ce][obj_name]["obj"].dl_port_csv_files):
                            for key, value in self.mcast_obj_dict[ce][obj_name]["obj"].dl_port_csv_files.items():
                                if self.mcast_obj_dict[ce][obj_name]["obj"].csv_data_to_report:
                                    # read the csv file
                                    self.overall_report.set_table_title("Layer 3 Cx Traffic  {key}".format(key=key))
                                    self.overall_report.build_table_title()
                                    self.overall_report.set_table_dataframe_from_csv(value.name)
                                    self.overall_report.build_table()

                                # read in column heading and last line
                                df = pd.read_csv(value.name)
                                last_row = df.tail(1)
                                self.overall_report.set_table_title(
                                    "Layer 3 Cx Traffic Last Reporting Interval {key}".format(key=key))
                                self.overall_report.build_table_title()
                                self.overall_report.set_table_dataframe(last_row)
                                self.overall_report.build_table()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"mcast_test_{obj_no}"
                        else:
                            break        
                
                elif test_name == "vs_test":
                    obj_no=1
                    obj_name = "vs_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.vs_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        params = self.vs_obj_dict[ce][obj_name]["data"].copy()
                        date = params["date"]

                        iterations_before_test_stopped_by_user = (
                            params["iterations_before_test_stopped_by_user"].copy()
                            if isinstance(params["iterations_before_test_stopped_by_user"], (list, dict, set))
                            else params["iterations_before_test_stopped_by_user"]
                        )

                        test_setup_info = (
                            params["test_setup_info"].copy()
                            if isinstance(params["test_setup_info"], (list, dict, set))
                            else params["test_setup_info"]
                        )

                        realtime_dataset = (
                            params["realtime_dataset"].copy()
                            if isinstance(params["realtime_dataset"], (list, dict, set))
                            else params["realtime_dataset"]
                        )

                        report_path = (
                            params["report_path"].copy()
                            if isinstance(params["report_path"], (list, dict, set))
                            else params["report_path"]
                        )

                        cx_order_list = (
                            params["cx_order_list"].copy()
                            if isinstance(params["cx_order_list"], (list, dict, set))
                            else params["cx_order_list"]
                        )
                        self.overall_report.set_obj_html(_obj_title=f'Video Streaming Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        created_incremental_values = self.vs_obj_dict[ce][obj_name]["obj"].get_incremental_capacity_list()
                        keys = list(self.vs_obj_dict[ce][obj_name]["obj"].http_profile.created_cx.keys())

                        self.overall_report.set_table_title("Input Parameters")
                        self.overall_report.build_table_title()
                        if self.vs_obj_dict[ce][obj_name]["obj"].config:
                            test_setup_info["SSID"] = self.vs_obj_dict[ce][obj_name]["obj"].ssid
                            test_setup_info["Password"] = self.vs_obj_dict[ce][obj_name]["obj"].passwd
                            test_setup_info["ENCRYPTION"] = self.vs_obj_dict[ce][obj_name]["obj"].encryp
                        elif len(self.vs_obj_dict[ce][obj_name]["obj"].selected_groups) > 0 and len(self.vs_obj_dict[ce][obj_name]["obj"].selected_profiles) > 0:
                            # Map each group with a profile
                            gp_pairs = zip(self.vs_obj_dict[ce][obj_name]["obj"].selected_groups, self.vs_obj_dict[ce][obj_name]["obj"].selected_profiles)
                            # Create a string by joining the mapped pairs
                            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)
                            test_setup_info["Configuration"] = gp_map

                        self.overall_report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

                        device_type = []
                        username = []
                        ssid = []
                        mac = []
                        channel = []
                        mode = []
                        rssi = []
                        channel = []
                        tx_rate = []
                        resource_ids = list(map(int, self.vs_obj_dict[ce][obj_name]["obj"].resource_ids.split(',')))
                        try:
                            eid_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate,ssid,signal,channel")
                        except KeyError:
                            logger.error("Error: 'interfaces' key not found in port data")
                            exit(1)

                        # Loop through interfaces
                        for alias in eid_data["interfaces"]:
                            for i in alias:
                                # Check interface index and alias
                                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':

                                    # Get resource data for specific interface
                                    resource_hw_data = self.vs_obj_dict[ce][obj_name]["obj"].json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                                    hw_version = resource_hw_data['resource']['hw version']

                                    # Filter based on OS and resource ID
                                    if not hw_version.startswith(('Win', 'Linux', 'Apple')) and int(resource_hw_data['resource']['eid'].split('.')[1]) in resource_ids:
                                        device_type.append('Android')
                                        username.append(resource_hw_data['resource']['user'])
                                        ssid.append(alias[i]['ssid'])
                                        mac.append(alias[i]['mac'])
                                        mode.append(alias[i]['mode'])
                                        rssi.append(alias[i]['signal'])
                                        channel.append(alias[i]['channel'])
                                        tx_rate.append(alias[i]['tx-rate'])
                        total_urls = self.vs_obj_dict[ce][obj_name]["obj"].data["total_urls"]
                        total_err = self.vs_obj_dict[ce][obj_name]["obj"].data["total_err"]
                        total_buffer = self.vs_obj_dict[ce][obj_name]["obj"].data["total_buffer"]
                        max_bytes_rd_list = []
                        avg_rx_rate_list = []
                        # Iterate through the length of cx_order_list
                        for iter in range(len(iterations_before_test_stopped_by_user)):
                            data_set_in_graph, wait_time_data, devices_on_running_state, device_names_on_running = [], [], [], []
                            devices_data_to_create_wait_time_bar_graph = []
                            max_video_rate, min_video_rate, avg_video_rate = [], [], []
                            total_url_data, rssi_data = [], []
                            trimmed_data_set_in_graph = []
                            max_bytes_rd_list = []
                            avg_rx_rate_list = []
                            # Retrieve data for the previous iteration, if it's not the first iteration
                            if iter != 0:
                                before_data_iter = realtime_dataset[realtime_dataset['iteration'] == iter]
                            # Retrieve data for the current iteration
                            data_iter = realtime_dataset[realtime_dataset['iteration'] == iter + 1]

                            # Populate the list of devices on running state and their corresponding usernames
                            for j in range(created_incremental_values[iter]):
                                devices_on_running_state.append(keys[j])
                                device_names_on_running.append(username[j])

                            # Iterate through each device currently running
                            for k in devices_on_running_state:
                                # Filter columns related to the current device
                                columns_with_substring = [col for col in data_iter.columns if k in col]
                                filtered_df = data_iter[columns_with_substring]
                                min_val = self.vs_obj_dict[ce][obj_name]["obj"].process_list(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist())
                                if iter != 0:
                                    # Filter columns related to the current device from the previous iteration
                                    before_iter_columns_with_substring = [col for col in before_data_iter.columns if k in col]
                                    before_filtered_df = before_data_iter[before_iter_columns_with_substring]

                                # Extract and compute max, min, and average video rates
                                max_video_rate.append(max(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()))
                                min_video_rate.append(min_val)
                                avg_video_rate.append(round(sum(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()) /
                                                    len(filtered_df[[col for col in filtered_df.columns if "video_format_bitrate" in col][0]].values.tolist()), 2))
                                wait_time_data.append(filtered_df[[col for col in filtered_df.columns if "total_wait_time" in col][0]].values.tolist()[-1])
                                rssi_data.append(int(round(sum(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()) /
                                                len(filtered_df[[col for col in filtered_df.columns if "RSSI" in col][0]].values.tolist()), 2)) * -1)
                                # Extract maximum bytes read for the device
                                max_bytes_rd = max(filtered_df[[col for col in filtered_df.columns if "bytes_rd" in col][0]].values.tolist())
                                max_bytes_rd_list.append(max_bytes_rd)

                                # Calculate and append the average RX rate in Mbps
                                rx_rate_values = filtered_df[[col for col in filtered_df.columns if "rx rate" in col][0]].values.tolist()
                                avg_rx_rate_list.append(round((sum(rx_rate_values) / len(rx_rate_values)) / 1_000_000, 2))  # Convert bps to Mbps

                                if iter != 0:
                                    # Calculate the difference in total URLs between the current and previous iterations
                                    total_url_data.append(abs(filtered_df[[col for col in filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1] -
                                                        before_filtered_df[[col for col in before_filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1]))
                                else:
                                    # Append the total URLs for the first iteration
                                    total_url_data.append(filtered_df[[col for col in filtered_df.columns if "total_urls" in col][0]].values.tolist()[-1])

                            # Append the wait time data to the list for creating the wait time bar graph
                            devices_data_to_create_wait_time_bar_graph.append(wait_time_data)

                            # Extract overall video format bitrate values for the current iteration and append to data_set_in_graph
                            video_streaming_values_list = realtime_dataset['overall_video_format_bitrate'][realtime_dataset['iteration'] == iter + 1].values.tolist()
                            data_set_in_graph.append(video_streaming_values_list)

                            # Trim the data in data_set_in_graph and append to trimmed_data_set_in_graph
                            for _ in range(len(data_set_in_graph)):
                                trimmed_data_set_in_graph.append(self.vs_obj_dict[ce][obj_name]["obj"].trim_data(len(data_set_in_graph[_]), data_set_in_graph[_]))

                            # If there are multiple incremental values, add custom HTML content to the report for the current iteration
                            if len(created_incremental_values) > 1:
                                self.overall_report.set_custom_html(f"<h2><u>Iteration-{iter + 1}</u></h2>")
                                self.overall_report.build_custom()

                            self.overall_report.set_obj_html(
                                _obj_title=f"Realtime Video Rate: Number of devices running: {len(device_names_on_running)}",
                                _obj="")
                            self.overall_report.build_objective()

                            # Create a line graph for video rate over time
                            graph = lf_line_graph(_data_set=trimmed_data_set_in_graph,
                                                _xaxis_name="Time",
                                                _yaxis_name="Video Rate (Mbps)",
                                                _xaxis_categories=self.vs_obj_dict[ce][obj_name]["obj"].trim_data(len(realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
                                                                                realtime_dataset['timestamp'][realtime_dataset['iteration'] == iter + 1].values.tolist()),
                                                _label=['Rate'],
                                                _graph_image_name=f"vs_line_graph{iter}{obj_no}"
                                                )
                            graph_png = graph.build_line_graph()
                            logger.info("graph name {}".format(graph_png))
                            self.overall_report.set_graph_image(graph_png)
                            self.overall_report.move_graph_image()

                            self.overall_report.build_graph()

                            # Define figure size for horizontal bar graphs
                            x_fig_size = 15
                            y_fig_size = len(devices_on_running_state) * .5 + 4

                            self.overall_report.set_obj_html(
                                _obj_title="Total Urls Per Device",
                                _obj="")
                            self.overall_report.build_objective()
                            # Create a horizontal bar graph for total URLs per device
                            graph = lf_bar_graph_horizontal(_data_set=[total_urls[:created_incremental_values[iter]]],
                                                            _xaxis_name="Total Urls",
                                                            _yaxis_name="Devices",
                                                            _graph_image_name=f"total_urls_image_name{iter}{obj_no}",
                                                            _label=["Total Urls"],
                                                            _yaxis_categories=device_names_on_running,
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _show_bar_value=True,
                                                            _figsize=(x_fig_size, y_fig_size)
                                                            #    _color=['lightcoral']
                                                            )
                            graph_png = graph.build_bar_graph_horizontal()
                            logger.info("wait time graph name {}".format(graph_png))
                            graph.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_png)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_obj_html(
                                _obj_title="Max/Min Video Rate Per Device",
                                _obj="")
                            self.overall_report.build_objective()

                            # Create a horizontal bar graph for max and min video rates per device
                            graph = lf_bar_graph_horizontal(_data_set=[max_video_rate, min_video_rate],
                                                            _xaxis_name="Max/Min Video Rate(Mbps)",
                                                            _yaxis_name="Devices",
                                                            _graph_image_name=f"max-min-video-rate_image_name{iter}{obj_no}",
                                                            _label=['Max Video Rate', 'Min Video Rate'],
                                                            _yaxis_categories=device_names_on_running,
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _show_bar_value=True,
                                                            _figsize=(x_fig_size, y_fig_size)
                                                            #    _color=['lightcoral']
                                                            )
                            graph_png = graph.build_bar_graph_horizontal()
                            logger.info("max/min graph name {}".format(graph_png))
                            graph.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_png)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_obj_html(
                                _obj_title="Wait Time Per Device",
                                _obj="")
                            self.overall_report.build_objective()

                            # Create a horizontal bar graph for wait time per device
                            graph = lf_bar_graph_horizontal(_data_set=devices_data_to_create_wait_time_bar_graph,
                                                            _xaxis_name="Wait Time(seconds)",
                                                            _yaxis_name="Devices",
                                                            _graph_image_name=f"wait_time_image_name{iter}{obj_no}",
                                                            _label=['Wait Time'],
                                                            _yaxis_categories=device_names_on_running,
                                                            _legend_loc="best",
                                                            _legend_box=(1.0, 1.0),
                                                            _show_bar_value=True,
                                                            _figsize=(x_fig_size, y_fig_size)
                                                            #    _color=['lightcoral']
                                                            )
                            graph_png = graph.build_bar_graph_horizontal()
                            logger.info("wait time graph name {}".format(graph_png))
                            graph.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_png)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            if self.vs_obj_dict[ce][obj_name]["obj"].dowebgui and self.vs_obj_dict[ce][obj_name]["obj"].get_live_view:
                                script_dir = os.path.dirname(os.path.abspath(__file__))

                                self.overall_report.set_custom_html("<h2>No of Buffers and Wait Time %</h2>")
                                self.overall_report.build_custom()

                                for floor in range(int(self.vs_obj_dict[ce][obj_name]["obj"].floors)):
                                    # Construct expected image paths
                                    vs_buffer_image = os.path.join(script_dir, "heatmap_images", f"{self.vs_obj_dict[ce][obj_name]['obj'].test_name}_vs_buffer_{floor+1}.png")
                                    vs_wait_time_image = os.path.join(script_dir, "heatmap_images", f"{self.vs_obj_dict[ce][obj_name]['obj'].test_name}_vs_wait_time_{floor+1}.png")


                                    # Wait for all required images to be generated (up to timeout)
                                    timeout = 60  # seconds
                                    start_time = time.time()

                                    while not (os.path.exists(vs_buffer_image) and os.path.exists(vs_wait_time_image)):
                                        if time.time() - start_time > timeout:
                                            print(f"Timeout: Heatmap images for floor {floor + 1} not found within {timeout} seconds.")
                                            break
                                        time.sleep(1)

                                    # Generate report sections for each image if it exists
                                    for image_path in [vs_buffer_image, vs_wait_time_image,]:
                                        if os.path.exists(image_path):
                                            self.overall_report.set_custom_html(f'<img src="file://{image_path}"  style="width:1200px; height:800px;"></img>')
                                            self.overall_report.build_custom()

                            # Table 1
                            self.overall_report.set_obj_html("Overall - Detailed Result Table", "The below tables provides detailed information for the Video Streaming test.")
                            self.overall_report.build_objective()
                            test_data = {
                                "iter": iter,
                                "created_incremental_values": created_incremental_values,
                                "device_type": device_type,
                                "username": username,
                                "ssid": ssid,
                                "mac": mac,
                                "channel": channel,
                                "mode": mode,
                                "total_buffer": total_buffer,
                                "wait_time_data": wait_time_data,
                                "min_video_rate": min_video_rate,
                                "avg_video_rate": avg_video_rate,
                                "max_video_rate": max_video_rate,
                                "total_urls": total_urls,
                                "total_err": total_err,
                                "rssi_data": rssi_data,
                                "tx_rate": tx_rate,
                                "max_bytes_rd_list": max_bytes_rd_list,
                                "avg_rx_rate_list": avg_rx_rate_list
                            }

                            dataframe = self.vs_obj_dict[ce][obj_name]["obj"].handle_passfail_criteria(test_data)

                            dataframe1 = pd.DataFrame(dataframe)
                            self.overall_report.set_table_dataframe(dataframe1)
                            self.overall_report.build_table()

                            # Set and build title for the overall results table
                            self.overall_report.set_obj_html("Detailed Total Errors Table", "The below tables provides detailed information of total errors for the web browsing test.")
                            self.overall_report.build_objective()
                            dataframe2 = {
                                " DEVICE": username[:created_incremental_values[iter]],
                                " TOTAL ERRORS ": total_err[:created_incremental_values[iter]],
                            }
                            dataframe3 = pd.DataFrame(dataframe2)
                            self.overall_report.set_table_dataframe(dataframe3)
                            self.overall_report.build_table()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"vs_test_{obj_no}"
                        else:
                            break
                
                elif test_name =="rb_test":
                    obj_no=1
                    obj_name = "rb_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.rb_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'Real Browser Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()

                        final_eid_data = []
                        mac_data = []
                        channel_data = []
                        signal_data = []
                        ssid_data = []
                        tx_rate_data = []
                        device_type_data = []
                        device_names = []
                        total_urls = []
                        time_to_target_urls = []
                        uc_min_data = []
                        uc_max_data = []
                        uc_avg_data = []
                        total_err_data = []

                        csv_paths = self.rb_obj_dict[ce][obj_name]["obj"].report_path_date_time if not self.dowebgui else self.result_dir
                        final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = self.rb_obj_dict[ce][obj_name]["obj"].extract_device_data('{}/real_time_data.csv'.format(csv_paths))

                        test_setup_info = self.rb_obj_dict[ce][obj_name]["obj"].generate_test_setup_info()
                        self.overall_report.test_setup_table(
                            test_setup_data=test_setup_info, value='Test Parameters')
                        self.rb_obj_dict[ce][obj_name]["obj"].csv_file_names
                        for i in range(0, len(self.rb_obj_dict[ce][obj_name]["obj"].csv_file_names)):
                            if self.rb_obj_dict[ce][obj_name]["obj"].csv_file_names[i].startswith("real_time_data.csv"):
                                continue

                            final_eid_data, mac_data, channel_data, signal_data, ssid_data, tx_rate_data, device_names, device_type_data = self.rb_obj_dict[ce][obj_name]["obj"].extract_device_data("{}/{}".format(csv_paths,self.rb_obj_dict[ce][obj_name]["obj"].csv_file_names[i]))
                            self.overall_report.set_graph_title("Successful URL's per Device")
                            self.overall_report.build_graph_title()

                            data = pd.read_csv("{}/{}".format(csv_paths,self.rb_obj_dict[ce][obj_name]["obj"].csv_file_names[i]))

                            # Extract device names from CSV
                            if 'total_urls' in data.columns:
                                total_urls = data['total_urls'].tolist()
                            else:
                                raise ValueError("The 'total_urls' column was not found in the CSV file.")

                            x_fig_size = 18
                            y_fig_size = len(device_type_data) * 1 + 4
                            print('DEVICE NAMES',device_names)
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=[total_urls],
                                _xaxis_name="URL",
                                _yaxis_name="Devices",
                                _yaxis_label=device_names,
                                _yaxis_categories=device_names,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="URLs",
                                _graph_image_name=f"{self.rb_obj_dict[ce][obj_name]['obj'].csv_file_names[i]}_urls_per_device{obj_no}",
                                _label=["URLs"]
                            )
                            # print('yaxssss)
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title(f"Time Taken Vs Device For Completing {self.rb_obj_dict[ce][obj_name]['obj'].count} RealTime URLs")
                            self.overall_report.build_graph_title()

                            # Extract device names from CSV
                            if 'time_to_target_urls' in data.columns:
                                time_to_target_urls = data['time_to_target_urls'].tolist()
                            else:
                                raise ValueError("The 'time_to_target_urls' column was not found in the CSV file.")

                            x_fig_size = 18
                            y_fig_size = len(device_type_data) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=[time_to_target_urls],
                                _xaxis_name="Time (in Seconds)",
                                _yaxis_name="Devices",
                                _yaxis_label=device_names,
                                _yaxis_categories=device_names,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Time Taken",
                                _graph_image_name=f"{self.rb_obj_dict[ce][obj_name]['obj'].csv_file_names[i]}_time_taken_for_urls{obj_no}",
                                _label=["Time (in sec)"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            if 'uc_min' in data.columns:
                                uc_min_data = data['uc_min'].tolist()
                            else:
                                raise ValueError("The 'uc_min' column was not found in the CSV file.")

                            if 'uc_max' in data.columns:
                                uc_max_data = data['uc_max'].tolist()
                            else:
                                raise ValueError("The 'uc_max' column was not found in the CSV file.")

                            if 'uc_avg' in data.columns:
                                uc_avg_data = data['uc_avg'].tolist()
                            else:
                                raise ValueError("The 'uc_avg' column was not found in the CSV file.")

                            if 'total_err' in data.columns:
                                total_err_data = data['total_err'].tolist()
                            else:
                                raise ValueError("The 'total_err' column was not found in the CSV file.")

                        self.overall_report.set_table_title("Final Test Results")
                        self.overall_report.build_table_title()
                        if self.rb_obj_dict[ce][obj_name]["obj"].expected_passfail_value or self.rb_obj_dict[ce][obj_name]["obj"].device_csv_name:
                            pass_fail_list, test_input_list = self.rb_obj_dict[ce][obj_name]["obj"].generate_pass_fail_list(device_type_data, device_names, total_urls)

                            final_test_results = {

                                "Device Type": device_type_data,
                                "Hostname": device_names,
                                "SSID": ssid_data,
                                "MAC": mac_data,
                                "Channel": channel_data,
                                "UC-MIN (ms)": uc_min_data,
                                "UC-MAX (ms)": uc_max_data,
                                "UC-AVG (ms)": uc_avg_data,
                                "Total Successful URLs": total_urls,
                                "Expected URLS": test_input_list,
                                "Total Erros": total_err_data,
                                "RSSI": signal_data,
                                "Link Speed": tx_rate_data,
                                "Status ": pass_fail_list

                            }
                        else:
                            final_test_results = {

                                "Device Type": device_type_data,
                                "Hostname": device_names,
                                "SSID": ssid_data,
                                "MAC": mac_data,
                                "Channel": channel_data,
                                "UC-MIN (ms)": uc_min_data,
                                "UC-MAX (ms)": uc_max_data,
                                "UC-AVG (ms)": uc_avg_data,
                                "Total Successful URLs": total_urls,
                                "Total Erros": total_err_data,
                                "RSSI": signal_data,
                                "Link Speed": tx_rate_data,

                            }
                        logger.info(f"dataframe realbrowser {final_test_results}")
                        test_results_df = pd.DataFrame(final_test_results)
                        self.overall_report.set_table_dataframe(test_results_df)
                        self.overall_report.build_table()

                        if self.rb_obj_dict[ce][obj_name]["obj"].dowebgui:

                            os.chdir(self.rb_obj_dict[ce][obj_name]["obj"].original_dir)

                        # self.overall_report.build_custom()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"rb_test_{obj_no}"
                        else:
                            break                    

                elif test_name == "yt_test":
                    obj_no=1
                    obj_name = "yt_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.yt_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        result_data = self.yt_obj_dict[ce][obj_name]["obj"].stats_api_response
                        for device, stats in result_data.items():
                            self.yt_obj_dict[ce][obj_name]["obj"].mydatajson.setdefault(device, {}).update({
                                "Viewport": stats.get("Viewport", ""),
                                "DroppedFrames": stats.get("DroppedFrames", "0"),
                                "TotalFrames": stats.get("TotalFrames", "0"),
                                "CurrentRes": stats.get("CurrentRes", ""),
                                "OptimalRes": stats.get("OptimalRes", ""),
                                "BufferHealth": stats.get("BufferHealth", "0.0"),
                                "Timestamp": stats.get("Timestamp", ""),
                            })

                        if self.yt_obj_dict[ce][obj_name]["obj"].config:

                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': self.yt_obj_dict[ce][obj_name]["obj"].duration,
                                'Resolution': self.yt_obj_dict[ce][obj_name]["obj"].resolution,
                                'Configured Devices': self.yt_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Devices :': f' Total({len(self.yt_obj_dict[ce][obj_name]["obj"].real_sta_os_types)}) : W({self.yt_obj_dict[ce][obj_name]["obj"].windows}),L({self.yt_obj_dict[ce][obj_name]["obj"].linux}),M({self.yt_obj_dict[ce][obj_name]["obj"].mac})',
                                "Video URL": self.yt_obj_dict[ce][obj_name]["obj"].url,
                                "SSID": self.yt_obj_dict[ce][obj_name]["obj"].ssid,
                                "Security": self.yt_obj_dict[ce][obj_name]["obj"].security,

                            }

                        elif len(self.yt_obj_dict[ce][obj_name]["obj"].selected_groups) > 0 and len(self.yt_obj_dict[ce][obj_name]["obj"].selected_profiles) > 0:
                            gp_pairs = zip(self.yt_obj_dict[ce][obj_name]["obj"].selected_groups, self.yt_obj_dict[ce][obj_name]["obj"].selected_profiles)
                            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': self.yt_obj_dict[ce][obj_name]["obj"].duration,
                                'Resolution': self.yt_obj_dict[ce][obj_name]["obj"].resolution,
                                "Configuration": gp_map,
                                'Configured Devices': self.yt_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Devices :': f' Total({len(self.yt_obj_dict[ce][obj_name]["obj"].real_sta_os_types)}) : W({self.yt_obj_dict[ce][obj_name]["obj"].windows}),L({self.yt_obj_dict[ce][obj_name]["obj"].linux}),M({self.yt_obj_dict[ce][obj_name]["obj"].mac})',
                                "Video URL": self.yt_obj_dict[ce][obj_name]["obj"].url,

                            }
                        else:
                            # Test setup info
                            test_setup_info = {
                                'Test Name': 'YouTube Streaming Test',
                                'Duration (in Minutes)': self.yt_obj_dict[ce][obj_name]["obj"].duration,
                                'Resolution': self.yt_obj_dict[ce][obj_name]["obj"].resolution,
                                'Configured Devices': self.yt_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Devices :': f' Total({len(self.yt_obj_dict[ce][obj_name]["obj"].real_sta_os_types)}) : W({self.yt_obj_dict[ce][obj_name]["obj"].windows}),L({self.yt_obj_dict[ce][obj_name]["obj"].linux}),M({self.yt_obj_dict[ce][obj_name]["obj"].mac})',
                                "Video URL": self.yt_obj_dict[ce][obj_name]["obj"].url,

                            }
                        self.overall_report.set_obj_html(_obj_title=f'Youtube Streaming Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.test_setup_table(
                            test_setup_data=test_setup_info, value='Test Parameters')

                        viewport_list = []
                        current_res_list = []
                        optimal_res_list = []

                        dropped_frames_list = []
                        total_frames_list = []
                        max_buffer_health_list = []
                        min_buffer_health_list = []

                        for hostname in self.yt_obj_dict[ce][obj_name]["obj"].real_sta_hostname:
                            if hostname in self.yt_obj_dict[ce][obj_name]["obj"].mydatajson:
                                stats = self.yt_obj_dict[ce][obj_name]["obj"].mydatajson[hostname]
                                viewport_list.append(stats.get("Viewport", ""))
                                current_res_list.append(stats.get("CurrentRes", ""))
                                optimal_res_list.append(stats.get("OptimalRes", ""))

                                dropped_frames = stats.get("DroppedFrames", "0")
                                total_frames = stats.get("TotalFrames", "0")
                                max_buffer_health = stats.get("maxbufferhealth", "0,0")
                                min_buffer_health = stats.get("minbufferhealth", "0.0")
                                try:
                                    dropped_frames_list.append(int(dropped_frames))
                                except ValueError:
                                    dropped_frames_list.append(0)

                                try:
                                    total_frames_list.append(int(total_frames))
                                except ValueError:
                                    total_frames_list.append(0)
                                try:
                                    max_buffer_health_list.append(float(max_buffer_health))
                                except ValueError:
                                    max_buffer_health_list.append(0.0)

                                try:
                                    min_buffer_health_list.append(float(min_buffer_health))
                                except ValueError:
                                    min_buffer_health_list.append(0.0)

                            else:
                                viewport_list.append("NA")
                                current_res_list.append("NA")
                                optimal_res_list.append("NA")
                                dropped_frames_list.append(0)
                                total_frames_list.append(0)
                                max_buffer_health_list.append(0.0)
                                min_buffer_health_list.append(0.0)

                        # graph of frames dropped
                        self.overall_report.set_graph_title("Total Frames vs Frames dropped")
                        self.overall_report.build_graph_title()
                        x_fig_size = 25
                        y_fig_size = len(self.yt_obj_dict[ce][obj_name]["obj"].device_names) * .5 + 4

                        graph = lf_bar_graph_horizontal(_data_set=[dropped_frames_list, total_frames_list],
                                                        _xaxis_name="No of Frames",
                                                        _yaxis_name="Devices",
                                                        _yaxis_categories=self.yt_obj_dict[ce][obj_name]["obj"].real_sta_hostname,
                                                        _graph_image_name=f"Dropped Frames vs Total Frames{obj_no}",
                                                        _label=["dropped Frames", "Total Frames"],
                                                        _color=None,
                                                        _color_edge='red',
                                                        _figsize=(x_fig_size, y_fig_size),
                                                        _show_bar_value=True,
                                                        _text_font=6,
                                                        _text_rotation=True,
                                                        _enable_csv=True,
                                                        _legend_loc="upper right",
                                                        _legend_box=(1.1, 1),
                                                        )
                        graph_image = graph.build_bar_graph_horizontal()
                        self.overall_report.set_graph_image(graph_image)
                        self.overall_report.move_graph_image()
                        self.overall_report.build_graph()

                        self.overall_report.set_table_title('Test Results')
                        self.overall_report.build_table_title()

                        test_results = {
                            "Hostname": self.yt_obj_dict[ce][obj_name]["obj"].real_sta_hostname,
                            "OS Type": self.yt_obj_dict[ce][obj_name]["obj"].real_sta_os_types,
                            "MAC": self.yt_obj_dict[ce][obj_name]["obj"].mac_list,
                            "RSSI": self.yt_obj_dict[ce][obj_name]["obj"].rssi_list,
                            "Link Rate": self.yt_obj_dict[ce][obj_name]["obj"].link_rate_list,
                            "ViewPort": viewport_list,
                            "SSID": self.yt_obj_dict[ce][obj_name]["obj"].ssid_list,
                            "Video Resoultion": current_res_list,
                            "Max Buffer Health (Seconds)": max_buffer_health_list,
                            "Min Buffer health (Seconds)": min_buffer_health_list,
                            "Total Frames": total_frames_list,
                            "Dropped Frames": dropped_frames_list,


                        }

                        test_results_df = pd.DataFrame(test_results)
                        self.overall_report.set_table_dataframe(test_results_df)
                        self.overall_report.build_table()

                        # for file_path in self.yt_obj_dict[ce][obj_name]["obj"].devices_list:
                        #         self.yt_obj_dict[ce][obj_name]["obj"].move_files(file_path, self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time)

                        original_dir = os.getcwd()

                        if self.yt_obj_dict[ce][obj_name]["obj"].do_webUI:
                            csv_files = [f for f in os.listdir(self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time) if f.endswith('.csv')]
                            os.chdir(self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time)
                        else:
                            csv_files = [f for f in os.listdir(self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time) if f.endswith('.csv')]
                            os.chdir(self.yt_obj_dict[ce][obj_name]["obj"].report_path_date_time)
                        print("CSV FILES",csv_files)
                        print("Script Directory:", os.path.dirname(os.path.abspath(__file__)))
                        scp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),self.report_path_date_time)
                        for file_name in csv_files:
                            data = pd.read_csv(file_name)
                            print('dataaaaaaaaaaaaa',data)
                            self.overall_report.set_graph_title('Buffer Health vs Time Graph for {}'.format(file_name.split('_')[0]))
                            self.overall_report.build_graph_title()

                            try:
                                data['TimeStamp'] = pd.to_datetime(data['TimeStamp'], format="%H:%M:%S").dt.time
                            except Exception as e:
                                logging.error(f"Error in timestamp conversion for {file_name}: {e}")
                                continue

                            data = data.drop_duplicates(subset='TimeStamp', keep='first')

                            data = data.sort_values(by='TimeStamp')

                            timestamps = data['TimeStamp'].apply(lambda t: t.strftime('%H:%M:%S'))
                            buffer_health = data['BufferHealth']

                            fig, ax = plt.subplots(figsize=(20, 10))
                            plt.plot(timestamps, buffer_health, color='blue', linewidth=2)

                            # Customize the plot
                            plt.xlabel('Time', fontweight='bold', fontsize=15)
                            plt.ylabel('Buffer Health', fontweight='bold', fontsize=15)
                            plt.title('Buffer Health vs Time Graph for {}'.format(file_name.split('_')[0]), fontsize=18)

                            if len(timestamps) > 30:
                                tick_interval = len(timestamps) // 30
                                selected_ticks = timestamps[::tick_interval]
                                ax.set_xticks(selected_ticks)
                            else:
                                ax.set_xticks(timestamps)

                            plt.xticks(rotation=45, ha='right')

                            # output_file = '{}'.format(file_name.split('_')[0]) + 'buffer_health_vs_time.png'
                            output_file = os.path.join(scp_path,f"{file_name.split('_')[0]}buffer_health_vs_time{obj_no}.png")
                            plt.tight_layout()
                            plt.savefig(output_file, dpi=96)
                            plt.close()
                            abs_path = os.path.abspath(output_file)
                            logging.info(f"Graph saved PATH {file_name}: {abs_path}")

                            logging.info(f"Graph saved for {file_name}: {output_file}")

                            self.overall_report.set_graph_image(output_file)

                            self.overall_report.build_graph()

                        os.chdir(original_dir)
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"yt_test_{obj_no}"
                        else:
                            break

                elif test_name == "zoom_test":
                    obj_no=1
                    obj_name = "zoom_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.zoom_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'ZOOM Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()
                        testtype = ""
                        if self.zoom_obj_dict[ce][obj_name]["obj"].audio and self.zoom_obj_dict[ce][obj_name]["obj"].video:
                            testtype = "AUDIO & VIDEO"
                        elif self.zoom_obj_dict[ce][obj_name]["obj"].audio:
                            testtype = "AUDIO"
                        elif self.zoom_obj_dict[ce][obj_name]["obj"].video:
                            testtype = "VIDEO"

                        if self.zoom_obj_dict[ce][obj_name]["obj"].config:
                            test_parameters = pd.DataFrame([{
                                "Configured Devices": self.zoom_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Clients': f'W({self.zoom_obj_dict[ce][obj_name]["obj"].windows}),L({self.zoom_obj_dict[ce][obj_name]["obj"].linux}),M({self.zoom_obj_dict[ce][obj_name]["obj"].mac})',
                                'Test Duration(min)': self.zoom_obj_dict[ce][obj_name]["obj"].duration,
                                'EMAIL ID': self.zoom_obj_dict[ce][obj_name]["obj"].signin_email,
                                "PASSWORD": self.zoom_obj_dict[ce][obj_name]["obj"].signin_passwd,
                                "HOST": self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_list[0],
                                "TEST TYPE": testtype,
                                "SSID": self.zoom_obj_dict[ce][obj_name]["obj"].ssid,
                                "Security": self.zoom_obj_dict[ce][obj_name]["obj"].security

                            }])
                        elif len(self.zoom_obj_dict[ce][obj_name]["obj"].selected_groups) > 0 and len(self.zoom_obj_dict[ce][obj_name]["obj"].selected_profiles) > 0:
                            # Map each group with a profile
                            gp_pairs = zip(self.zoom_obj_dict[ce][obj_name]["obj"].selected_groups, self.zoom_obj_dict[ce][obj_name]["obj"].selected_profiles)

                            # Create a string by joining the mapped pairs
                            gp_map = ", ".join(f"{group} -> {profile}" for group, profile in gp_pairs)

                            test_parameters = pd.DataFrame([{
                                "Configuration": gp_map,
                                "Configured Devices": self.zoom_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Clients': f'W({self.zoom_obj_dict[ce][obj_name]["obj"].windows}),L({self.zoom_obj_dict[ce][obj_name]["obj"].linux}),M({self.zoom_obj_dict[ce][obj_name]["obj"].mac})',
                                'Test Duration(min)': self.zoom_obj_dict[ce][obj_name]["obj"].duration,
                                'EMAIL ID': self.zoom_obj_dict[ce][obj_name]["obj"].signin_email,
                                "PASSWORD": self.zoom_obj_dict[ce][obj_name]["obj"].signin_passwd,
                                "HOST": self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_list[0],
                                "TEST TYPE": testtype,

                            }])
                        else:

                            test_parameters = pd.DataFrame([{
                                "Configured Devices": self.zoom_obj_dict[ce][obj_name]["obj"].hostname_os_combination,
                                'No of Clients': f'W({self.zoom_obj_dict[ce][obj_name]["obj"].windows}),L({self.zoom_obj_dict[ce][obj_name]["obj"].linux}),M({self.zoom_obj_dict[ce][obj_name]["obj"].mac})',
                                'Test Duration(min)': self.zoom_obj_dict[ce][obj_name]["obj"].duration,
                                'EMAIL ID': self.zoom_obj_dict[ce][obj_name]["obj"].signin_email,
                                "PASSWORD": self.zoom_obj_dict[ce][obj_name]["obj"].signin_passwd,
                                "HOST": self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_list[0],
                                "TEST TYPE": testtype,

                            }])

                        test_parameters = pd.DataFrame([{

                            'No of Clients': f'W({self.zoom_obj_dict[ce][obj_name]["obj"].windows}),L({self.zoom_obj_dict[ce][obj_name]["obj"].linux}),M({self.zoom_obj_dict[ce][obj_name]["obj"].mac})',
                            'Test Duration(min)': self.zoom_obj_dict[ce][obj_name]["obj"].duration,
                            'EMAIL ID': self.zoom_obj_dict[ce][obj_name]["obj"].signin_email,
                            "PASSWORD": self.zoom_obj_dict[ce][obj_name]["obj"].signin_passwd,
                            "HOST": self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_list[0],
                            "TEST TYPE": testtype

                        }])
                        self.overall_report.set_table_dataframe(test_parameters)
                        self.overall_report.build_table()

                        client_array = []
                        accepted_clients = []
                        no_csv_client = []
                        rejected_clients = []
                        final_dataset = []
                        accepted_ostypes = []
                        max_audio_jitter_s, min_audio_jitter_s = [], []
                        max_audio_jitter_r, min_audio_jitter_r = [], []
                        max_audio_latency_s, min_audio_latency_s = [], []
                        max_audio_latency_r, min_audio_latency_r = [], []
                        max_audio_pktloss_s, min_audio_pktloss_s = [], []
                        max_audio_pktloss_r, min_audio_pktloss_r = [], []

                        max_video_jitter_s, min_video_jitter_s = [], []
                        max_video_jitter_r, min_video_jitter_r = [], []
                        max_video_latency_s, min_video_latency_s = [], []
                        max_video_latency_r, min_video_latency_r = [], []
                        max_video_pktloss_s, min_video_pktloss_s = [], []
                        max_video_pktloss_r, min_video_pktloss_r = [], []
                        for i in range(0, len(self.zoom_obj_dict[ce][obj_name]["obj"].device_names)):
                            temp_max_audio_jitter_s, temp_min_audio_jitter_s = 0.0, 0.0
                            temp_max_audio_jitter_r, temp_min_audio_jitter_r = 0.0, 0.0
                            temp_max_audio_latency_s, temp_min_audio_latency_s = 0.0, 0.0
                            temp_max_audio_latency_r, temp_min_audio_latency_r = 0.0, 0.0
                            temp_max_audio_pktloss_s, temp_min_audio_pktloss_s = 0.0, 0.0
                            temp_max_audio_pktloss_r, temp_min_audio_pktloss_r = 0.0, 0.0

                            temp_max_video_jitter_s, temp_min_video_jitter_s = 0.0, 0.0
                            temp_max_video_jitter_r, temp_min_video_jitter_r = 0.0, 0.0
                            temp_max_video_latency_s, temp_min_video_latency_s = 0.0, 0.0
                            temp_max_video_latency_r, temp_min_video_latency_r = 0.0, 0.0
                            temp_max_video_pktloss_s, temp_min_video_pktloss_s = 0.0, 0.0
                            temp_max_video_pktloss_r, temp_min_video_pktloss_r = 0.0, 0.0
                            per_client_data = {
                                "audio_jitter_s": [],
                                "audio_jitter_r": [],
                                "audio_latency_s": [],
                                "audio_latency_r": [],
                                "audio_pktloss_s": [],
                                "audio_pktloss_r": [],
                                "video_jitter_s": [],
                                "video_jitter_r": [],
                                "video_latency_s": [],
                                "video_latency_r": [],
                                "video_pktloss_s": [],
                                "video_pktloss_r": [],
                            }
                            try:
                                file_path = os.path.join(self.zoom_obj_dict[ce][obj_name]["obj"].report_path_date_time, f'{self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i]}.csv')
                                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as file:
                                    csv_reader = csv.DictReader(file)
                                    for row in csv_reader:

                                        per_client_data["audio_jitter_s"].append(float(row["Sent Audio Jitter (ms)"]))
                                        per_client_data["audio_jitter_r"].append(float(row["Receive Audio Jitter (ms)"]))
                                        per_client_data["audio_latency_s"].append(float(row["Sent Audio Latency (ms)"]))
                                        per_client_data["audio_latency_r"].append(float(row["Receive Audio Latency (ms)"]))
                                        per_client_data["audio_pktloss_s"].append(float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                                        per_client_data["audio_pktloss_r"].append(float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                                        per_client_data["video_jitter_s"].append(float(row["Sent Video Jitter (ms)"]))
                                        per_client_data["video_jitter_r"].append(float(row["Receive Video Jitter (ms)"]))
                                        per_client_data["video_latency_s"].append(float(row["Sent Video Latency (ms)"]))
                                        per_client_data["video_latency_r"].append(float(row["Receive Video Latency (ms)"]))
                                        per_client_data["video_pktloss_s"].append(float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%", "")))
                                        per_client_data["video_pktloss_r"].append(float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%", "")))

                                        temp_max_audio_jitter_s = max(temp_max_audio_jitter_s, float(row["Sent Audio Jitter (ms)"]))
                                        temp_max_audio_jitter_r = max(temp_max_audio_jitter_r, float(row["Receive Audio Jitter (ms)"]))
                                        temp_max_audio_latency_s = max(temp_max_audio_latency_s, float(row["Sent Audio Latency (ms)"]))
                                        temp_max_audio_latency_r = max(temp_max_audio_latency_r, float(row["Receive Audio Latency (ms)"]))
                                        temp_max_audio_pktloss_s = max(temp_max_audio_pktloss_s, float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))
                                        temp_max_audio_pktloss_r = max(temp_max_audio_pktloss_r, float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%", "")))

                                        temp_max_video_jitter_s = max(temp_max_video_jitter_s, float(row["Sent Video Jitter (ms)"]))
                                        temp_max_video_jitter_r = max(temp_max_video_jitter_r, float(row["Receive Video Jitter (ms)"]))
                                        temp_max_video_latency_s = max(temp_max_video_latency_s, float(row["Sent Video Latency (ms)"]))
                                        temp_max_video_latency_r = max(temp_max_video_latency_r, float(row["Receive Video Latency (ms)"]))
                                        temp_max_video_pktloss_s = max(temp_max_video_pktloss_s, float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%", "")))
                                        temp_max_video_pktloss_r = max(temp_max_video_pktloss_r, float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%", "")))

                                        temp_min_audio_jitter_s = min(
                                            temp_min_audio_jitter_s,
                                            float(
                                                row["Sent Audio Jitter (ms)"])) if temp_min_audio_jitter_s > 0 and float(
                                            row["Sent Audio Jitter (ms)"]) > 0 else (
                                            float(
                                                row["Sent Audio Jitter (ms)"]) if float(
                                                row["Sent Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_s)
                                        temp_min_audio_jitter_r = min(
                                            temp_min_audio_jitter_r, float(
                                                row["Receive Audio Jitter (ms)"])) if temp_min_audio_jitter_r > 0 and float(
                                            row["Receive Audio Jitter (ms)"]) > 0 else (
                                            float(
                                                row["Receive Audio Jitter (ms)"]) if float(
                                                row["Receive Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_r)
                                        temp_min_audio_latency_s = min(
                                            temp_min_audio_latency_s, float(
                                                row["Sent Audio Latency (ms)"])) if temp_min_audio_latency_s > 0 and float(
                                            row["Sent Audio Latency (ms)"]) > 0 else (
                                            float(
                                                row["Sent Audio Latency (ms)"]) if float(
                                                row["Sent Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_s)
                                        temp_min_audio_latency_r = min(
                                            temp_min_audio_latency_r, float(
                                                row["Receive Audio Latency (ms)"])) if temp_min_audio_latency_r > 0 and float(
                                            row["Receive Audio Latency (ms)"]) > 0 else (
                                            float(
                                                row["Receive Audio Latency (ms)"]) if float(
                                                row["Receive Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_r)

                                        temp_min_audio_pktloss_s = min(
                                            temp_min_audio_pktloss_s, float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", ""))) if temp_min_audio_pktloss_s > 0 and float(
                                            (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                "%", "")) > 0 else (
                                            float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) if float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) > 0 else temp_min_audio_pktloss_s)
                                        temp_min_audio_pktloss_r = min(
                                            temp_min_audio_pktloss_r, float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", ""))) if temp_min_audio_pktloss_r > 0 and float(
                                            (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                "%", "")) > 0 else (
                                            float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) if float(
                                                (row["Sent Audio Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) > 0 else temp_min_audio_pktloss_r)

                                        temp_min_video_jitter_s = min(
                                            temp_min_video_jitter_s,
                                            float(
                                                row["Sent Video Jitter (ms)"])) if temp_min_video_jitter_s > 0 and float(
                                            row["Sent Video Jitter (ms)"]) > 0 else (
                                            float(
                                                row["Sent Video Jitter (ms)"]) if float(
                                                row["Sent Video Jitter (ms)"]) > 0 else temp_min_video_jitter_s)
                                        temp_min_video_jitter_r = min(
                                            temp_min_video_jitter_r, float(
                                                row["Receive Video Jitter (ms)"])) if temp_min_video_jitter_r > 0 and float(
                                            row["Receive Video Jitter (ms)"]) > 0 else (
                                            float(
                                                row["Receive Video Jitter (ms)"]) if float(
                                                row["Receive Video Jitter (ms)"]) > 0 else temp_min_video_jitter_r)
                                        temp_min_video_latency_s = min(
                                            temp_min_video_latency_s, float(
                                                row["Sent Video Latency (ms)"])) if temp_min_video_latency_s > 0 and float(
                                            row["Sent Video Latency (ms)"]) > 0 else (
                                            float(
                                                row["Sent Video Latency (ms)"]) if float(
                                                row["Sent Video Latency (ms)"]) > 0 else temp_min_video_latency_s)
                                        temp_min_video_latency_r = min(
                                            temp_min_video_latency_r, float(
                                                row["Receive Video Latency (ms)"])) if temp_min_video_latency_r > 0 and float(
                                            row["Receive Video Latency (ms)"]) > 0 else (
                                            float(
                                                row["Receive Video Latency (ms)"]) if float(
                                                row["Receive Video Latency (ms)"]) > 0 else temp_min_video_latency_r)

                                        temp_min_video_pktloss_s = min(
                                            temp_min_video_pktloss_s, float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", ""))) if temp_min_video_pktloss_s > 0 and float(
                                            (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                "%", "")) > 0 else (
                                            float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) if float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) > 0 else temp_min_video_pktloss_s)
                                        temp_min_video_pktloss_r = min(
                                            temp_min_video_pktloss_r, float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", ""))) if temp_min_video_pktloss_r > 0 and float(
                                            (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                "%", "")) > 0 else (
                                            float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) if float(
                                                (row["Sent Video Packet loss (%)"]).split(" ")[0].replace(
                                                    "%", "")) > 0 else temp_min_video_pktloss_r)

                            except Exception as e:
                                logging.error(f"Error in reading data in client {self.zoom_obj_dict[ce][obj_name]['obj'].device_names[i]}", e)
                                no_csv_client.append(self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i])
                                rejected_clients.append(self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i])
                            if self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i] not in no_csv_client:
                                client_array.append(self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i])
                                accepted_clients.append(self.zoom_obj_dict[ce][obj_name]["obj"].device_names[i])
                                accepted_ostypes.append(self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_os_type[i])
                                max_audio_jitter_s.append(temp_max_audio_jitter_s)
                                min_audio_jitter_s.append(temp_min_audio_jitter_s)
                                max_audio_jitter_r.append(temp_max_audio_jitter_r)
                                min_audio_jitter_r.append(temp_min_audio_jitter_r)
                                max_audio_latency_s.append(temp_max_audio_latency_s)
                                min_audio_latency_s.append(temp_min_audio_latency_s)
                                max_audio_latency_r.append(temp_max_audio_latency_r)
                                min_audio_latency_r.append(temp_min_audio_latency_r)
                                max_video_jitter_s.append(temp_max_video_jitter_s)
                                min_video_jitter_s.append(temp_min_video_jitter_s)
                                max_video_jitter_r.append(temp_max_video_jitter_r)
                                min_video_jitter_r.append(temp_min_video_jitter_r)
                                max_video_latency_s.append(temp_max_video_latency_s)
                                min_video_latency_s.append(temp_min_video_latency_s)
                                max_video_latency_r.append(temp_max_video_latency_r)
                                min_video_latency_r.append(temp_min_video_latency_r)

                                max_audio_pktloss_s.append(temp_max_audio_pktloss_s)
                                min_audio_pktloss_s.append(temp_min_audio_pktloss_s)
                                max_audio_pktloss_r.append(temp_max_audio_pktloss_r)
                                min_audio_pktloss_r.append(temp_min_audio_pktloss_r)
                                max_video_pktloss_s.append(temp_max_video_pktloss_s)
                                min_video_pktloss_s.append(temp_min_video_pktloss_s)
                                max_video_pktloss_r.append(temp_max_video_pktloss_r)
                                min_video_pktloss_r.append(temp_min_video_pktloss_r)

                                final_dataset.append(per_client_data.copy())

                        self.overall_report.set_table_title("Test Devices:")
                        self.overall_report.build_table_title()

                        device_details = pd.DataFrame({
                            'Hostname': self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_hostname,
                            'OS Type': self.zoom_obj_dict[ce][obj_name]["obj"].real_sta_os_type,
                            "MAC": self.zoom_obj_dict[ce][obj_name]["obj"].mac_list,
                            "RSSI": self.zoom_obj_dict[ce][obj_name]["obj"].rssi_list,
                            "Link Rate": self.zoom_obj_dict[ce][obj_name]["obj"].link_rate_list,
                            "SSID": self.zoom_obj_dict[ce][obj_name]["obj"].ssid_list,

                        })
                        self.overall_report.set_table_dataframe(device_details)
                        self.overall_report.build_table()

                        if self.zoom_obj_dict[ce][obj_name]["obj"].audio:
                            self.overall_report.set_graph_title("Audio Latency (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_audio_latency_s.copy(), min_audio_latency_s.copy(), max_audio_latency_r.copy(), min_audio_latency_r.copy()]
                            y_data_set = client_array

                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Latency (ms)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Audio Latency(sent/received)",
                                _graph_image_name=f"Audio Latency(sent and received){obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title("Audio Jitter (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_audio_jitter_s.copy(), min_audio_jitter_s.copy(), max_audio_jitter_r.copy(), min_audio_jitter_r.copy()]
                            y_data_set = client_array

                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Jitter (ms)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Audio Jitter(sent/received)",
                                _graph_image_name=f"Audio Jitter(sent and received) {obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title("Audio Packet Loss (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_audio_pktloss_s.copy(), min_audio_pktloss_s.copy(), max_audio_pktloss_r.copy(), min_audio_pktloss_r.copy()]
                            y_data_set = client_array

                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Packet Loss (%)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Audio Packet Loss(sent/received)",
                                _graph_image_name=f"Audio Packet Loss(sent and received){obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_table_title("Test Audio Results Table:")
                            self.overall_report.build_table_title()
                            audio_test_results_dict = {
                                'Device Name': [client for client in accepted_clients],
                                'Avg Latency Sent (ms)': [
                                    round(sum(data["audio_latency_s"]) / len(data["audio_latency_s"]), 2) if len(data["audio_latency_s"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'Avg Latency Recv (ms)': [
                                    round(sum(data["audio_latency_r"]) / len(data["audio_latency_r"]), 2) if len(data["audio_latency_r"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'Avg Jitter Sent (ms)': [
                                    round(sum(data["audio_jitter_s"]) / len(data["audio_jitter_s"]), 2) if len(data["audio_jitter_s"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'Avg Jitter Recv (ms)': [
                                    round(sum(data["audio_jitter_r"]) / len(data["audio_jitter_r"]), 2) if len(data["audio_jitter_r"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'Avg Pkt Loss Sent': [
                                    round(sum(data["audio_pktloss_s"]) / len(data["audio_pktloss_s"]), 2) if len(data["audio_pktloss_s"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'Avg Pkt Loss Recv': [
                                    round(sum(data["audio_pktloss_r"]) / len(data["audio_pktloss_r"]), 2) if len(data["audio_pktloss_r"]) != 0 else 0
                                    for data in final_dataset
                                ],
                                'CSV link': [
                                    '<a href="{}.csv" target="_blank">csv data</a>'.format(client)
                                    for client in accepted_clients
                                ]
                            }
                            self.overall_report.set_table_dataframe(audio_test_results_dict)
                            self.overall_report.dataframe_html = self.overall_report.dataframe.to_html(index=False,
                                                                            justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
                            self.overall_report.html += self.overall_report.dataframe_html
                        if self.zoom_obj_dict[ce][obj_name]["obj"].video:
                            self.overall_report.set_graph_title("Video Latency (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_video_latency_s.copy(), min_video_latency_s.copy(), max_video_latency_r.copy(), min_video_latency_r.copy()]
                            y_data_set = client_array
                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Latency (ms)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Video Latency(sent/received)",
                                _graph_image_name=f"Video Latency(sent and received){obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title("Video Jitter (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_video_jitter_s.copy(), min_video_jitter_s.copy(), max_video_jitter_r.copy(), min_video_jitter_r.copy()]
                            y_data_set = client_array
                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Jitter (ms)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Video Jitter(sent/received)",
                                _graph_image_name=f"Video Jitter(sent and received){obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title("Video Packet Loss (Sent/Received)")
                            self.overall_report.build_graph_title()
                            x_data_set = [max_video_pktloss_s.copy(), min_video_pktloss_s.copy(), max_video_pktloss_r.copy(), min_video_pktloss_r.copy()]
                            y_data_set = client_array
                            x_fig_size = 18
                            y_fig_size = len(client_array) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=x_data_set,
                                _xaxis_name="Packet Loss (%)",
                                _yaxis_name="Devices",
                                _yaxis_label=y_data_set,
                                _yaxis_categories=y_data_set,
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _color_name=["yellow", "blue", "orange", "grey"],
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Video Packet Loss(sent/received)",
                                _graph_image_name=f"Video Packet Loss(sent and received){obj_no}",
                                _label=["Max Sent", "Min Sent", "Max Recv", "Min Recv"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_table_title("Test Video Results Table:")
                            self.overall_report.build_table_title()
                            video_test_results_dict = {
                            'Device Name': [client for client in accepted_clients],
                            'Avg Latency Sent (ms)': [
                                round(sum(data["video_latency_s"]) / len(data["video_latency_s"]), 2) if len(data["video_latency_s"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'Avg Latency Recv (ms)': [
                                round(sum(data["video_latency_r"]) / len(data["video_latency_r"]), 2) if len(data["video_latency_r"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'Avg Jitter Sent (ms)': [
                                round(sum(data["video_jitter_s"]) / len(data["video_jitter_s"]), 2) if len(data["video_jitter_s"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'Avg Jitter Recv (ms)': [
                                round(sum(data["video_jitter_r"]) / len(data["video_jitter_r"]), 2) if len(data["video_jitter_r"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'Avg Pkt Loss Sent': [
                                round(sum(data["video_pktloss_s"]) / len(data["video_pktloss_s"]), 2) if len(data["video_pktloss_s"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'Avg Pkt Loss Recv': [
                                round(sum(data["video_pktloss_r"]) / len(data["video_pktloss_r"]), 2) if len(data["video_pktloss_r"]) != 0 else 0
                                for data in final_dataset
                            ],
                            'CSV link': [
                                '<a href="{}.csv" target="_blank">csv data</a>'.format(client)
                                for client in accepted_clients
                            ]
                        }
                            self.overall_report.set_table_dataframe(video_test_results_dict)

                            self.overall_report.dataframe_html = self.overall_report.dataframe.to_html(index=False,
                                                                            justify='center', render_links=True, escape=False)  # have the index be able to be passed in.
                            self.overall_report.html += self.overall_report.dataframe_html
                        self.overall_report.set_custom_html("<br/><hr/>")
                        self.overall_report.build_custom()

                        if ce == "series":
                            obj_no += 1
                            obj_name = f"zoom_test_{obj_no}"
                        else:
                            break
                        
                elif test_name == "vlc_test":
                    obj_no=1
                    obj_name = "vlc_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.vlc_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'VLC Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        test_setup_info = self.vlc_obj_dict[ce][obj_name]["obj"].generate_test_setup_info()
                        self.overall_report.test_setup_table(test_setup_data=test_setup_info, value='Input Parameters')

                        final_data = self.vlc_obj_dict[ce][obj_name]["obj"].extract_data_for_reporting_for_laptop_clients()
                        android_data = self.vlc_obj_dict[ce][obj_name]["obj"].extract_data_for_reporting_for_android_clients()
                        if len(final_data["hostnames"]) == 0:
                            logging.info("No client data available for report generation.Continuing without client data.")
                        else:
                            self.overall_report.set_graph_title("Video Frames per Device")
                            self.overall_report.build_graph_title()

                            x_fig_size = 18
                            y_fig_size = len(final_data["hostnames"]) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=[[int(float(x)) for x in final_data["frames_lost"]],[int(float(x)) for x in final_data["frames_displayed"]]],
                                _xaxis_name="No of Frames",
                                _yaxis_name="Device Name",
                                _yaxis_label=final_data["hostnames"],
                                _yaxis_categories=final_data["hostnames"],
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _show_bar_value=True,
                                _dpi=96,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Video Frames Displayed/Lost per Device",
                                _graph_image_name=f"video_frames_per_device",
                                _label=["Frames Lost", "Frames Displayed"]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()

                            self.overall_report.set_graph_title("Audio Buffers Per Device")
                            self.overall_report.build_graph_title()

                            x_fig_size = 18
                            y_fig_size = len(final_data["hostnames"]) * 1 + 4
                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=[[int(float(x)) for x in final_data["buffers_lost"]],[int(float(x)) for x in final_data["buffers_played"]]],
                                _xaxis_name="No of Buffers",
                                _yaxis_name="Device Name",
                                _yaxis_label=final_data["hostnames"],
                                _yaxis_categories=final_data["hostnames"],
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.20,
                                _show_bar_value=True,
                                _figsize=(x_fig_size, y_fig_size),
                                _graph_title="Audio Buffers Played/Lost Per Device",
                                _graph_image_name=f"audio_buffers_per_device",
                                _label=["Buffers Lost","Buffers Played",]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()


                            self.overall_report.set_table_title("Test Results For Clients(Laptops)")
                            self.overall_report.build_table_title()
                            self.overall_report.set_text("The table below provides detailed information of both the Audio and Video Playback statistics of laptop device acting as clients.")
                            self.overall_report.build_text_simple()
                            final_test_results = {

                                "Device Name": final_data["hostnames"],
                                "Device Type": final_data["device_types"],
                                "MAC Address": final_data["mac"],
                                "Channel": final_data["channel"],
                                "RSSI": final_data["rssi"],
                                "Link Rate": final_data["link"],
                                "Video Decoded ": final_data["video_decoded"],
                                "Frames Displayed ": final_data["frames_displayed"],
                                "Frames Lost ": final_data["frames_lost"],
                                "Audio Decoded ": final_data["audio_decoded"],
                                "Buffers Played ": final_data["buffers_played"],
                                "Buffers Lost ": final_data["buffers_lost"],
                            }

                            test_results_df = pd.DataFrame(final_test_results)
                            self.overall_report.set_table_dataframe(test_results_df)
                            self.overall_report.build_table()
                        if len(android_data["hostnames"]) == 0:
                            logging.info("No Android client data available for report generation.Continuing without Android client data.")
                        else:    
                            self.overall_report.set_table_title("Test Results For Clients(Androids)")
                            self.overall_report.build_table_title()
                            
                            android_test_results = {

                                "Device Name": android_data["hostnames"],
                                "Device Type": android_data["device_types"],
                                "MAC Address": android_data["mac"],
                                "Channel": android_data["channel"],
                                "RSSI": android_data["rssi"],
                                "Link Rate": android_data["link"],
                                "Video Codec": android_data["video_codec"],
                                "Audio Codec": android_data["audio_codec"],
                                "Audio Channels": android_data["audio_channels"],
                                "Audio Sample Rate (Hz)": android_data["audio_sample_rate"],
                                "Demux Bitrate (kb/s)": android_data["demux_bitrate"],
                                "Input Bitrate (kb/s)": android_data["input_bitrate"],
                            }

                            android_test_results_df = pd.DataFrame(android_test_results)
                            android_test_results_df = android_test_results_df.fillna("None")

                            self.overall_report.set_table_dataframe(android_test_results_df)
                            self.overall_report.build_table()

                            self.overall_report.set_text("NOTE: VLC statistics on Android devices show audio parameters such as channel count and" +
                            " sample rate as zero due to Media Codec limitations in Android. This behavior is application-specific and " +
                            "does not indicate an issue with audio decoding or streaming quality.")
                            self.overall_report.build_text_simple()
                        if self.vlc_obj_dict[ce][obj_name]["obj"].host_res:
                            self.overall_report.set_table_title("Test Result For Host")
                            self.overall_report.build_table_title()
                            report_data = self.vlc_obj_dict[ce][obj_name]["obj"].extract_data_for_reporting_for_host()

                            for i in range(len(report_data["hostnames"])):
                                device_info = {
                                    "Device Name": report_data["hostnames"][i],
                                    "Device Type": report_data["device_types"][i],
                                    "Mac Address": report_data["mac"][i],
                                    "Channel": report_data["channel"][i],
                                    "RSSI (dBm)": report_data["rssi"][i],
                                }
                                metrics = [
                                    ("Input bytes read", report_data["input_bytes_read"][i]),
                                    ("Input bitrate", report_data["input_bitrate"][i]),
                                    ("Demux bytes read", report_data["demux_bytes_read"][i]),
                                    ("Demux bitrate", report_data["demux_bitrate"][i]),
                                    ("Discontinuities", report_data["discontinuities"][i]),
                                ]
                                self.vlc_obj_dict[ce][obj_name]["obj"].build_device_metrics_table(self.overall_report,device_info, metrics)
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"vlc_test_{obj_no}"
                        else:
                            break
                
                elif test_name == "teams_test":
                    obj_no = 1
                    obj_name = "teams_test"
                    if ce == "series":
                        obj_name += "_1"
                    while obj_name in self.teams_obj_dict[ce]:
                        if ce == "parallel":
                            obj_no = ''
                        self.overall_report.set_obj_html(_obj_title=f'TEAMS Test {obj_no}', _obj="")
                        self.overall_report.build_objective()
                        self.overall_report.set_table_title("Test Parameters:")
                        self.overall_report.build_table_title()
                        testtype = ""
                        if self.teams_obj_dict[ce][obj_name]["obj"].audio and self.teams_obj_dict[ce][obj_name]["obj"].video:
                            testtype = "AUDIO & VIDEO"
                        elif self.teams_obj_dict[ce][obj_name]["obj"].audio:
                            testtype = "AUDIO"
                        elif self.teams_obj_dict[ce][obj_name]["obj"].video:
                            testtype = "VIDEO"
                        test_parameters = pd.DataFrame([{

                            'No of Clients': f'W({self.teams_obj_dict[ce][obj_name]["obj"].windows}),L({self.teams_obj_dict[ce][obj_name]["obj"].linux}),M({self.teams_obj_dict[ce][obj_name]["obj"].mac})',
                            'Test Duration(min)': self.teams_obj_dict[ce][obj_name]["obj"].duration,
                            "HOST": self.teams_obj_dict[ce][obj_name]["obj"].real_sta_list[0],
                            "TEST TYPE": testtype

                        }])
                        self.overall_report.set_table_dataframe(test_parameters)
                        self.overall_report.build_table()

                        # Read per-device average metrics
                        print("Reading teams_call_avg_data.csv",os.getcwd())
                        df = pd.read_csv(os.path.join(self.teams_obj_dict[ce][obj_name]["obj"].report_path_date_time,"teams_call_avg_data.csv"))
                        df.columns = df.columns.str.strip()

                        self.overall_report.set_table_title("Test Devices:")
                        self.overall_report.build_table_title()

                        device_details = pd.DataFrame({
                            'Hostname': self.teams_obj_dict[ce][obj_name]["obj"].real_sta_hostname,
                            'OS Type': self.teams_obj_dict[ce][obj_name]["obj"].real_sta_os_types,
                        })
                        self.overall_report.set_table_dataframe(device_details)
                        self.overall_report.build_table()
                        if self.teams_obj_dict[ce][obj_name]["obj"].audio:
                            metrics = [
                                ("Audio RTT(ms)", "Audio RTT (ms)"),
                                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                                ("Sent Audio bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
                            ]

                        if self.teams_obj_dict[ce][obj_name]["obj"].video:
                            # Create bar graphs for each metric
                            metrics = [
                                ("Sent video bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                                ("Received video bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                                ("sent video packets", "Sent Video Packets"),
                            ]
                        if self.teams_obj_dict[ce][obj_name]["obj"].audio and self.teams_obj_dict[ce][obj_name]["obj"].video:
                            # Create bar graphs for each metric
                            metrics = [
                                ("Audio RTT(ms)", "Audio RTT (ms)"),
                                ("Received Audio Jitter(ms)", "Received Audio Jitter (ms)"),
                                ("Sent Audio bitrate(Kbps)", "Sent Audio Bitrate (Kbps)"),
                                ("Sent video bitrate(Mbps)", "Sent Video Bitrate (Mbps)"),
                                ("Received video bitrate(Mbps)", "Received Video Bitrate (Mbps)"),
                                ("sent video packets", "Sent Video Packets"),
                            ]
                        for column, title in metrics:
                            self.overall_report.set_graph_title(f"Average {title}")
                            self.overall_report.build_graph_title()

                            bar_graph_horizontal = lf_bar_graph_horizontal(
                                _data_set=[df[column].tolist()],
                                _xaxis_name=f"AVG {title}",
                                _yaxis_name="Devices",
                                _yaxis_label=df["Device Name"].tolist(),
                                _yaxis_categories=df["Device Name"].tolist(),
                                _yaxis_step=1,
                                _yticks_font=8,
                                _bar_height=.25,
                                _color_name=["orange"],
                                _show_bar_value=True,
                                _figsize=(16, len(df) * 1 + 4),
                                _graph_title=f"AVG {title} Per Device",
                                _graph_image_name=title.replace(" ", "_"),
                                _label=[title]
                            )
                            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
                            self.overall_report.set_graph_image(graph_image)
                            self.overall_report.move_graph_image()
                            self.overall_report.build_graph()
                        if self.teams_obj_dict[ce][obj_name]["obj"].audio:
                            selected_columns = [
                                "Device Name",
                                "Sent Audio bitrate(Kbps)",
                                "Sent Audio Packets",
                                "Audio RTT(ms)",
                                "Received Audio Jitter(ms)",
                                "Receievd Audio Packet Loss(%)",
                            ]

                            column_headings = {
                                "Device Name": "Device Name",
                                "Sent Audio bitrate(Kbps)": "AVG Sent Audio Bitrate (Kbps)",
                                "Sent Audio Packets": "AVG Sent Audio Packets",
                                "Audio RTT(ms)": "AVG Audio RTT (ms)",
                                "Received Audio Jitter(ms)": "AVG Received Audio Jitter (ms)",
                                "Receievd Audio Packet Loss(%)": "AVG Received Audio Packet Loss (%)",
                            }

                            filtered_df = df[selected_columns].rename(columns=column_headings)

                            self.overall_report.set_table_title("Test Audio Results Table")
                            self.overall_report.build_table_title()
                            self.overall_report.set_table_dataframe(filtered_df)
                            self.overall_report.build_table()

                        if self.teams_obj_dict[ce][obj_name]["obj"].video:
                            selected_columns = [
                                "Device Name",
                                "Sent video bitrate(Mbps)",
                                "Received video bitrate(Mbps)",
                                "Sent video frame rate(fps)",
                                "video RTT (ms)",
                                "sent video packets",
                            ]

                            column_headings = {
                                "Device Name": "Device Name",
                                "Sent video bitrate(Mbps)": "AVG Sent Video Bitrate (Mbps)",
                                "Received video bitrate(Mbps)": "AVG Received Video Bitrate (Mbps)",
                                "Sent video frame rate(fps)": "AVG Sent Video Frame Rate (fps)",
                                "video RTT (ms)": "AVG Video RTT (ms)",
                                "sent video packets": "AVG Sent Video Packets",
                            }

                            filtered_df = df[selected_columns].rename(columns=column_headings)

                            self.overall_report.set_table_title("Test Video Results Table")
                            self.overall_report.build_table_title()
                            self.overall_report.set_table_dataframe(filtered_df)
                            self.overall_report.build_table()
                        
                        self.overall_report.write_html()
                        self.overall_report.write_pdf()
                        if ce == "series":
                            obj_no += 1
                            obj_name = f"zoom_test_{obj_no}"
                        else:
                            break

            except Exception as e:
                logger.info(f"failed to generate report for {test_name} {e}")
                import traceback
                traceback.print_exc()

    def update_duration(self,df):
        if not df.empty and hasattr(self, "names_duration") and self.names_duration:
            for name, duration in self.names_duration.items():
                mask = df["test_name"].str.contains(name, case=False, na=False)
                df.loc[mask, "Duration"] = duration
        return df
    def generate_test_exc_df(self,test_results_df,args_dict):
        series_df = {}
        parallel_df = {}
        if self.order_priority == "series":
            if len(self.series_tests) != 0:
                series_df = test_results_df[:len(self.series_tests)].copy()
                series_df["s/no"] = range(1, len(series_df) + 1)
                series_df = series_df[["s/no", "test_name", "Duration", "status"]]
                # if self.do_mix_exec:
                #     serial_df = self.update_duration(serial_df)
            if len(self.parallel_tests) != 0:
                parallel_df = test_results_df[len(self.series_tests):].copy()
                parallel_df["s/no"] = range(1, len(parallel_df) + 1)
                parallel_df = parallel_df[["s/no", "test_name", "Duration", "status"]]
                # if self.do_mix_exec:
                #     parallel_df = self.update_duration(parallel_df)
        else:
            if len(self.parallel_tests) != 0:
                parallel_df = test_results_df[:len(self.parallel_tests)].copy()
                parallel_df["s/no"] = range(1, len(parallel_df) + 1)
                parallel_df = parallel_df[["s/no", "test_name", "Duration", "status"]]
                # if self.do_mix_exec:
                #     parallel_df = self.update_duration(parallel_df)
            
            if len(self.series_tests) != 0:
                series_df = test_results_df[len(self.parallel_tests):].copy()
                series_df["s/no"] = range(1, len(series_df) + 1)
                series_df = series_df[["s/no", "test_name", "Duration", "status"]]
                # if self.do_mix_exec:
                #     series_df = self.update_duration(series_df)

        return series_df,parallel_df

    def run_series(self,series_threads):
        for t in series_threads:
            t.start()
            t.join()   # sequential execution
        self.stop_all_tests = True  # signal to stop all tests after series execution is done

    def run_parallel(self,parallel_threads):
        for t in parallel_threads:
            t.start()
        for t in parallel_threads:
            t.join()

    def query_devices(self):
        # device_list = device_list if device_list else []
        all_devices = self.resource_stats.get_all_devices()
        # self.resource_stats.display_available_devices(all_devices)
        available_df = self.resource_stats.display_available_devices(all_devices)
        print(tabulate(available_df, headers='keys', tablefmt='fancy_grid'))
        
        if len(self.device_list) != 0:
            dev_list = self.device_list.copy()
        else:
            dev_list = input("Enter the desired resources to run the test: (for androids enter serial/resource id for other enter only resource id)").split(',')
        name_to_res = {}
        res_to_name = {}
        for device in all_devices:
            if device["type"] == 'laptop':
                name_to_res[device["hostname"]] = device["shelf"] + '.' + device["resource"]
                res_to_name[device["shelf"] + '.' + device["resource"]] = device["hostname"]
            else:
                name_to_res[device["serial"]] =  device["shelf"] + '.' + device["resource"]
                res_to_name[device["shelf"] + '.' + device["resource"]] = device["serial"]
        filtered_dev_list,remarks_df = self.resource_stats.filter_device_list(dev_list, name_to_res, res_to_name)
        print("Entered device list:", dev_list)
        print(tabulate(remarks_df, headers='keys', tablefmt='fancy_grid'))
        print("filtered",filtered_dev_list)
        return filtered_dev_list        
    
    async def disconnect_devices(self,device_list=None,query=False):
        device_list = device_list if device_list else []
        if not self.device_list and not device_list:
            logger.error("No device list found")
            return
        elif device_list:
            device_list = device_list
        elif self.device_list:
            device_list = self.device_list
        selected_laptop_devices = []
        selected_adb_devices = []
        for device_obj in self.resource_stats.all_devices:
            if device_obj.get("serial") in device_list or device_obj.get("hostname") in device_list or (device_obj.get(
                    "shelf") + '.' + device_obj.get("resource")) in device_list or device_obj.get("eid") in device_list:

                # For laptops, set enterprise parameters
                if device_obj["type"] == "laptop":
                    selected_laptop_devices.append(device_obj)
                # For androids, set server_ip to start the app
                else:
                    selected_adb_devices.append(device_obj)
        if (selected_adb_devices != []):
            await self.resource_stats.adb_obj.forget_all_networks(port_list=selected_adb_devices)
            time.sleep(10)
        if (selected_laptop_devices != []):
            await self.resource_stats.laptop_obj.disconnect_wifi(port_list=selected_laptop_devices)
            time.sleep(10)
    

    def configure_devices(self):
        device_list = []
        if self.config:
            device_list = self.query_devices()
        config_devices = {}
        config_dict = {
            'ssid': self.ssid,
            'passwd': self.password,
            'enc': self.security,
            'eap_method': self.eap_method,
            'eap_identity': self.eap_identity,
            'ieee80211': self.ieee80211,
            'ieee80211u': self.ieee80211u,
            'ieee80211w': self.ieee80211w,
            'enable_pkc': self.enable_pkc,
            'bss_transition': self.bss_transition,
            'power_save': self.power_save,
            'disable_ofdma': self.disable_ofdma,
            'roam_ft_ds': self.roam_ft_ds,
            'key_management': self.key_management,
            'pairwise': self.pairwise,
            'private_key': self.private_key,
            'ca_cert': self.ca_cert,
            'client_cert': self.client_cert,
            'pk_passwd': self.pk_passwd,
            'pac_file': self.pac_file,
            'server_ip': self.upstream_ip,
        }
        print(config_dict)
        if self.group_name and self.file_name and device_list == [] and self.profile_name:
            selected_groups = self.group_name.split(',')
            selected_profiles = self.profile_name.split(',')
            for i in range(len(selected_groups)):
                config_devices[selected_groups[i]] = selected_profiles[i]
            self.resource_stats.initiate_group()
            self.group_device_map = self.resource_stats.get_groups_devices(data=selected_groups, groupdevmap=True)

            # Configure devices in the selected group with the selected profile
            device_list = asyncio.run(self.resource_stats.connectivity(config=config_devices, upstream=self.upstream_ip))
        # Case 2: Device list is already provided
        elif device_list != []:
            all_devices = self.resource_stats.get_all_devices()
            # self.device_list = self.device_list.split(',')
            # If config is false, the test will exclude all inactive devices
            if self.config:
                # If config is True, attempt to bring up all devices in the list and perform tests on those that become active
                # Configure devices in the device list with the provided SSID, Password and Security
                device_list = asyncio.run(self.resource_stats.connectivity(device_list=self.device_list, wifi_config=config_dict))
        else:
            logger.error("give correct set of configurations")
        return device_list

    def generate_overall_report(self,test_results_df='',args_dict={},iot_summary=None):
        self.overall_report = lf_report.lf_report(_results_dir_name="Base_Class_Test_Overall_report", _output_html="base_class_overall.html",
                                         _output_pdf="base_class_overall.pdf", _path=self.result_path if not self.dowebgui else self.result_dir)
        self.report_path_date_time = self.overall_report.get_path_date_time()
        self.overall_report.set_title("Candela Base Class")
        self.overall_report.set_date(datetime.datetime.now())
        self.overall_report.build_banner()
        # self.overall_report.set_custom_html(test_results_df.to_html(index=False, justify='center'))
        # self.overall_report.build_custom()
        if not self.do_mix_exec:
            try:
                series_df,parallel_df = self.generate_test_exc_df(test_results_df,args_dict)
            except Exception:
                # traceback.print_exc()
                print('exception failed dataframe')
        else:
            self.overall_report.set_table_title("Traffic Details")
            self.overall_report.build_table_title()
            test_results_df.insert(0, "s/no", range(1, len(test_results_df) + 1))
            test_results_df = self.update_duration(test_results_df)
            self.overall_report.set_custom_html(test_results_df.to_html(index=False, justify='center'))
            self.overall_report.build_custom()


        if self.order_priority == "series":
            if len(self.series_tests) != 0:
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Series Tests</h1>')
                    self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html(series_df.to_html(index=False, justify='center'))
                    self.overall_report.build_custom()
                self.render_each_test(ce="series")
            if len(self.parallel_tests) != 0:
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Parallel Tests</h1>')
                    self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html(parallel_df.to_html(index=False, justify='center'))
                    self.overall_report.build_custom()
                self.render_each_test(ce="parallel")
        else:
            if len(self.parallel_tests) != 0:
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Parallel Tests</h1>')
                    self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html(parallel_df.to_html(index=False, justify='center'))
                    self.overall_report.build_custom()
                self.render_each_test(ce="parallel")
            if len(self.series_tests) != 0:
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html('<h1 style="color:darkgreen; border-bottom: 2px solid darkgreen; padding-bottom: 5px; font-weight: bold; font-size: 40px;">Series Tests</h1>')
                    self.overall_report.build_custom()
                self.overall_report.set_table_title("Traffic Details")
                self.overall_report.build_table_title()
                if not self.do_mix_exec:
                    self.overall_report.set_custom_html(series_df.to_html(index=False, justify='center'))
                    self.overall_report.build_custom()
                self.render_each_test(ce="series")
        if iot_summary:
            self.build_iot_report_section(self.overall_report,iot_summary)
        # self.overall_report.insert_table_at_marker(test_results_df,"for_table")
        self.overall_report.build_footer()
        html_file = self.overall_report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)
        self.overall_report.write_pdf()

def validate_individual_args(args,test_name):
    if test_name == 'ping_test':
        return True
    elif test_name =='http_test':
        return True
    elif test_name =='ftp_test':
        return True
    elif test_name =='thput_test':
        return True
    elif test_name =='qos_test':
        return True
    elif test_name =='vs_test':
        return True
    elif test_name =="zoom_test":
        if args["zoom_signin_email"] is None:
            return False
        if args["zoom_signin_passwd"] is None:
            return False
        if args["zoom_participants"] is None:
            return False
        return True
    elif test_name =="yt_test":
        if args["yt_url"] is None:
            return False
    elif test_name == "rb_test":
        return True







def validate_time(n: str) -> str:
    try:
        if type(n) == int or type(n) == str and n.isdigit():  # just a number, default seconds
            seconds = int(n)
        elif n.endswith("s"):
            seconds = int(n[:-1])
        elif n.endswith("m"):
            seconds = int(n[:-1]) * 60
        elif n.endswith("h"):
            seconds = int(n[:-1]) * 3600
        else:
            return "wrong type"

        # Now normalize
        if seconds < 60:
            return f"{seconds} secs"
        elif seconds < 3600:
            return f"{seconds // 60} mins"
        else:
            return f"{seconds // 3600} hours"
    except ValueError:
        return "wrong type"

def validate_args(args):
    # pass/fail , config , groups-profiles arg validation
    tests = ["http_test","ping_test","ftp_test","thput_test","qos_test","vs_test","mcast_test","yt_test","rb_test","zoom_test"]
    if args[series_tests]:
        series_tests = args[series_tests].split(',')
    if args[parallel_tests]:
        parallel_tests = args[parallel_tests].split(',')
    for test in tests:
        flag_test = True
        if test in series_tests or test in parallel_tests:
            logger.info(f"validating args for {test}...")
            flag_test = validate_individual_args(args,test)
            test = test.split('_')[0]
            if args[f'{test}_expected_passfail_value'] and args[f'{test}_device_csv_name']:
                logger.error(f"Specify either --{test}_expected_passfail_value or --{test}_device_csv_name")
                flag_test = False
            if args[f'{test}_group_name']:
                selected_groups = args[f'{test}_group_name'].split(',')
            else:
                selected_groups = []
            if args[f'{test}_profile_name']:
                selected_profiles = args['profile_name'].split(',')
            else:
                selected_profiles = []

            if len(selected_groups) != len(selected_profiles):
                logger.error(f"Number of groups should match number of profiles")
                flag_test = False
            elif args[f'{test}_group_name'] and args[f'{test}_profile_name'] and args[f'{test}_file_name'] and args[f'{test}_device_list'] != []:
                logger.error(f"Either --{test}_group_name or --{test}_device_list should be entered not both")
                flag_test = False
            elif args[f'{test}_ssid'] and args[f'{test}_profile_name']:
                logger.error(f"Either --{test}_ssid or --{test}_profile_name should be given")
                flag_test = False

            elif args[f'{test}_file_name'] and (args.get(f'{test}_group_name') is None or args.get(f'{test}_profile_name') is None):
                logger.error(f"Please enter the correct set of arguments for configuration")
                flag_test = False

            if args[f'{test}_config'] and args.get(f'{test}_group_name') is None:
                if args.get(f'{test}_ssid') and args.get(f'{test}_security') and args[f'{test}_security'].lower() == 'open' and (args.get(f'{test}_passwd') is None or args[f'{test}_passwd'] == ''):
                    args[f'{test}_passwd'] = '[BLANK]'

                if args.get(f'{test}_ssid') is None or args.get(f'{test}_passwd') is None or args[f'{test}_passwd'] == '':
                    logger.error(f'For configuration need to Specify --{test}_ssid , --{test}_passwd (Optional for "open" type security) , --{test}_security')
                    flag_test = False

                elif args.get(f'{test}_ssid') and args[f'{test}_passwd'] == '[BLANK]' and args.get(f'{test}_security') and args[f'{test}_security'].lower() != 'open':
                    logger.error(f'Please provide valid --{test}_passwd and --{test}_security configuration')
                    flag_test = False

                elif args.get(f'{test}_ssid') and args.get(f'{test}_passwd'):
                    if args.get(f'{test}_security') is None:
                        logger.error(f'Security must be provided when --{test}_ssid and --{test}_password specified')
                        flag_test = False
                    elif args[f'{test}_passwd'] == '[BLANK]' and args[f'{test}_security'].lower() != 'open':
                        logger.error(f'Please provide valid passwd and security configuration')
                        flag_test = False
                    elif args[f'{test}_security'].lower() == 'open' and args[f'{test}_passwd'] != '[BLANK]':
                        logger.error(f"For an open type security, the password should be left blank (i.e., set to '' or [BLANK]).")
                        flag_test = False
            if flag_test:
                logger.info(f"Arg validation check done for {test}")

def return_valid_grp_list(grp_res_dict,test_grps,candela_apis):
    dev_list = []
    valid_grps = test_grps.split(',')
    for key,value in grp_res_dict.items():
        if test_grps == "all" or key in valid_grps:
            for dev in value:
                if dev in candela_apis.device_list:
                    dev_list.append(dev)
    print("Group Dict:", grp_res_dict)
    print("Valid Groups:", valid_grps)
    print("Device List:", candela_apis.device_list)
    print("device_list",dev_list)
    print("test grps",test_grps)
    return dev_list


def update_device_list(args,tests,candela_apis):
    groups = False
    if args.file_name and args.group_name and args.profile_name:
        groups = True
    # print(group_device_map)
    all_devices = candela_apis.resource_stats.get_all_devices()
    name_to_res = {}
    res_to_name = {}
    include_tests = []
    for device in all_devices:
        if device["type"] == 'laptop':
            name_to_res[device["hostname"]] = device["shelf"] + '.' + device["resource"]
            res_to_name[device["shelf"] + '.' + device["resource"]] = device["hostname"]
        else:
            name_to_res[device["serial"]] =  device["shelf"] + '.' + device["resource"]
            res_to_name[device["shelf"] + '.' + device["resource"]] = device["serial"]
    group_resource_list = {}
    for key,value in candela_apis.group_device_map.copy().items():
        r_list = [name_to_res[val] for val in value]
        group_resource_list[key] = r_list.copy()
    print(group_resource_list)
    for test in tests:

        if test == "http_test":
            if not groups:
                args.http_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.http_groups, candela_apis)
                args.http_device_list = ','.join(val_list)

        elif test == "ping_test":
            if not groups:
                args.ping_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.ping_groups, candela_apis)
                args.ping_device_list = ','.join(val_list)

        elif test == "ftp_test":
            if not groups:
                args.ftp_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.ftp_groups, candela_apis)
                args.ftp_device_list = ','.join(val_list)

        elif test == "thput_test":
            if not groups:
                args.thput_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.thput_groups, candela_apis)
                args.thput_device_list = ','.join(val_list)

        elif test == "qos_test":
            if not groups:
                args.qos_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.qos_groups, candela_apis)
                args.qos_device_list = ','.join(val_list)

        elif test == "vs_test":
            if not groups:
                args.vs_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.vs_groups, candela_apis)
                args.vs_device_list = ','.join(val_list)

        elif test == "mcast_test":
            if not groups:
                args.mcast_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.mcast_groups, candela_apis)
                args.mcast_device_list = ','.join(val_list)

        elif test == "yt_test":
            if not groups:
                args.yt_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.yt_groups, candela_apis)
                args.yt_device_list = ','.join(val_list)

        elif test == "rb_test":
            if not groups:
                args.rb_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.rb_groups, candela_apis)
                args.rb_device_list = ','.join(val_list)

        elif test == "zoom_test":
            if not groups:
                args.zoom_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.zoom_groups, candela_apis)
                args.zoom_device_list = ','.join(val_list)
        elif test == "teams_test":
            if not groups:
                args.teams_device_list = ','.join(candela_apis.device_list.copy())
            else:
                val_list = return_valid_grp_list(group_resource_list, args.teams_groups, candela_apis)
                args.teams_device_list = ','.join(val_list)
        elif test == "vlc_test":
            if not groups:
                vlc_list = []
                if args.vlc_host_res in candela_apis.device_list:
                    vlc_list.append(args.vlc_host_res)
                for dev in candela_apis.device_list:
                    if dev != args.vlc_host_res:
                        vlc_list.append(dev)

                args.vlc_device_list = ','.join(vlc_list)
            else:
                val_list = return_valid_grp_list(group_resource_list, args.vlc_groups, candela_apis)
                vlc_list = []
                if args.vlc_host_res in val_list:
                    vlc_list.append(args.vlc_host_res)
                for dev in candela_apis.device_list:
                    if dev != args.vlc_host_res:
                        vlc_list.append(dev)
                args.vlc_device_list = ','.join(vlc_list) 

    return args

def validate_args_config(args):
    if args.group_name:
        selected_groups = args.group_name.split(',')
    else:
        selected_groups = []
    if args.profile_name:
        selected_profiles = args.profile_name.split(',')
    else:
        selected_profiles = []
    if args.config and args.group_name is None:
        if args.ssid is None:
            logger.error('Specify SSID for confiuration, Password(Optional for "open" type security) , Security')
            exit(1)
        elif args.ssid and args.passwd == '[BLANK]' and args.security.lower() != 'open':
            logger.error('Please provide valid passwd and security configuration')
            exit(1)
        elif args.ssid and args.passwd:
            if args.security is None:
                logger.error('Security must be provided when SSID and Password specified')
                exit(1)
    if args.device_csv_name and args.expected_passfail_value:
        logger.error("Enter either --device_csv_name or --expected_passfail_value")
        exit(1)
    if args.group_name and (args.file_name is None or args.profile_name is None):
        logger.error("Please provide file name and profile name for group configuration")
        exit(1)
    elif args.file_name and (args.group_name is None or args.profile_name is None):
        logger.error("Please provide group name and profile name for file configuration")
        exit(1)
    elif args.profile_name and (args.group_name is None or args.file_name is None):
        logger.error("Please provide group name and file name for profile configuration")
        exit(1)

    if len(selected_groups) != len(selected_profiles):
        logger.error("Number of groups should match number of profiles")
        exit(1)
    elif args.group_name and args.profile_name and args.file_name and args.device_list != []:
        logger.error("Either group name or device list should be entered, not both")
        exit(1)
    elif args.ssid and args.profile_name:
        logger.error("Either SSID or profile name should be given")
        exit(1)
    elif args.config and args.device_list != [] and (args.ssid is None or args.passwd is None or args.security is None):
        logger.error("Please provide ssid password and security when device list is given")
        exit(1)
    elif args.file_name and (args.group_name is None or args.profile_name is None):
        logger.error("Please enter the correct set of arguments")
        exit(1)
    elif args.config and args.group_name is None and (args.ssid is None or (args.passwd is None and args.security is None) or (args.passwd is None and args.security.lower() != 'open')):
        logger.error("Please provide ssid password and security for configuring devices")
        exit(1)
def ensure_path(path_str, create_if_missing=False):
    if os.path.exists(path_str):
        logger.info(f"Path exists: {path_str}")
        return True

    if create_if_missing:
        try:
            os.makedirs(path_str, exist_ok=True)
            logger.info(f"Path created: {path_str}")
            return True
        except Exception as e:
            logger.error(f"Failed to create path: {e}")
            return False

    logger.error("Path does not exist, add arg --auto_create to create if doesn't exists")
    return False
def parse_the_args():
    parser = argparse.ArgumentParser(
    prog="candela_base_class.py",
    formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = argparse.ArgumentParser(description="Run Candela API Tests")
    optional = parser.add_argument_group('Optional arguments')

    #Always Common
    parser.add_argument('--mgr', '--lfmgr', default='localhost', help='hostname for where LANforge GUI is running')
    parser.add_argument('--mgr_port', '--port', default=8080, help='port LANforge GUI HTTP service is running on')
    parser.add_argument('--upstream_port', '-u', default='eth1', help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    #Common
    parser.add_argument('--device_list', help="Enter the devices on which the test should be run", default=[])
    parser.add_argument('--duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--parallel',
                          action="store_true",
                          help='to run in parallel')
    parser.add_argument("--tests",type=str,help="Comma-separated ordered list of tests to run (e.g., ping_test,http_test,ping_test)")
    parser.add_argument('--series_tests', help='Comma-separated list of tests to run in series')
    parser.add_argument('--parallel_tests', help='Comma-separated list of tests to run in parallel')
    parser.add_argument('--order_priority', choices=['series', 'parallel'], default='series',
                    help='Which tests to run first: series or parallel')
    parser.add_argument('--test_name', help='Name of the Test')
    parser.add_argument('--dowebgui', help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--result_dir', help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default='')
    parser.add_argument('--no_cleanup', help='Do not cleanup before exit',action='store_true')
    #NOt common
    #ping
    #without config
    parser.add_argument('--ping_test',
                          action="store_true",
                          help='ping_test consists')
    parser.add_argument('--ping_target',
                          type=str,
                          help='Target URL or port for ping test',
                          default='1.1.eth1')
    parser.add_argument('--ping_interval',
                          type=str,
                          help='Interval (in seconds) between the echo requests',
                          default='1')

    parser.add_argument('--ping_duration',
                          type=float,
                          help='Duration (in minutes) to run the ping test',
                          default=1)
    parser.add_argument('--ping_use_default_config',
                          action='store_true',
                          help='specify this flag if wanted to proceed with existing Wi-Fi configuration of the devices')
    parser.add_argument('--ping_device_list', help="Enter the devices on which the ping test should be run", default=[])
    parser.add_argument("--ping_sta_to_res", action="store_true", help='Enables pinging from sta port to multiple')
    parser.add_argument("--ping_sta_port", type=str,default="eth1" , help='station that uses to multiple clients')
    parser.add_argument('--ping_res_ip', help='resources IPs to ping from station, comma seperated', default=[])
    #ping pass fail value
    parser.add_argument("--ping_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--ping_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #ping with groups and profile configuration
    parser.add_argument('--ping_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--ping_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--ping_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #ping configuration with --config
    parser.add_argument("--ping_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--ping_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--ping_passwd', '--ping_password', '--ping_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--ping_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--ping_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--ping_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ping_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ping_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ping_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--ping_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--ping_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--ping_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--ping_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--ping_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--ping_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--ping_pairwise", type=str, default='NA')
    parser.add_argument("--ping_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--ping_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--ping_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--ping_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--ping_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--ping_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--ping_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--ping_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--ping_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    #http
    parser.add_argument('--http_test',
                          action="store_true",
                          help='http consists')
    parser.add_argument('--http_bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                          default=["5G", "2.4G", "6G"])
    parser.add_argument('--http_duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--http_file_size', type=str, help='specify the size of file you want to download', default='5MB')
    parser.add_argument('--http_device_list', help="Enter the devices on which the ping test should be run", default=[])
    #http pass fail value
    parser.add_argument("--http_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--http_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #http with groups and profile configuration
    parser.add_argument('--http_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--http_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--http_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #http configuration with --config
    parser.add_argument("--http_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--http_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--http_passwd', '--http_password', '--http_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--http_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--http_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--http_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--http_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--http_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--http_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--http_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--http_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--http_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--http_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--http_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--http_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--http_pairwise", type=str, default='NA')
    parser.add_argument("--http_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--http_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--http_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--http_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--http_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--http_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--http_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--http_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--http_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    #ftp
    parser.add_argument('--ftp_test',
                          action="store_true",
                          help='ftp_test consists')
    parser.add_argument('--ftp_bands', nargs="+", help='specify which band testing you want to run eg 5G, 2.4G, 6G',
                          default=["5G", "2.4G", "6G"])
    parser.add_argument('--ftp_duration', help='Please enter the duration in s,m,h (seconds or minutes or hours).Eg: 30s,5m,48h')
    parser.add_argument('--ftp_file_size', type=str, help='specify the size of file you want to download', default='5MB')
    parser.add_argument('--ftp_device_list', help="Enter the devices on which the ping test should be run", default=[])
    #ftp pass fail value
    parser.add_argument("--ftp_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--ftp_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #ftp with groups and profile configuration
    parser.add_argument('--ftp_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--ftp_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--ftp_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #ftp configuration with --config
    parser.add_argument("--ftp_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--ftp_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--ftp_passwd', '--ftp_password', '--ftp_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--ftp_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--ftp_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--ftp_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ftp_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ftp_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ftp_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--ftp_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--ftp_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--ftp_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--ftp_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--ftp_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--ftp_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--ftp_pairwise", type=str, default='NA')
    parser.add_argument("--ftp_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--ftp_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--ftp_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--ftp_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--ftp_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--ftp_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--ftp_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--ftp_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--ftp_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    #qos
    parser.add_argument('--qos_test',
                          action="store_true",
                          help='qos_test consists')
    parser.add_argument('--qos_duration', help='--qos_duration sets the duration of the test', default="2m")
    parser.add_argument('--qos_upload', help='--upload traffic load per connection (upload rate)')
    parser.add_argument('--qos_download', help='--download traffic load per connection (download rate)')
    parser.add_argument('--qos_traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    parser.add_argument('--qos_tos', help='Enter the tos. Example1 : "BK,BE,VI,VO" , Example2 : "BK,VO", Example3 : "VI" ')
    parser.add_argument('--qos_device_list', help="Enter the devices on which the ping test should be run", default=[])
    #qos pass fail value
    parser.add_argument("--qos_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--qos_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #qos with groups and profile configuration
    parser.add_argument('--qos_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--qos_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--qos_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #qos configuration with --config
    parser.add_argument("--qos_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--qos_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--qos_passwd', '--qos_password', '--qos_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--qos_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional qos config args
    parser.add_argument("--qos_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--qos_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--qos_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--qos_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--qos_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--qos_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--qos_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--qos_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--qos_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--qos_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--qos_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--qos_pairwise", type=str, default='NA')
    parser.add_argument("--qos_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--qos_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--qos_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--qos_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--qos_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--qos_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--qos_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--qos_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--qos_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)


    #vs
    parser.add_argument('--vs_test',
                          action="store_true",
                          help='vs_test consists')
    parser.add_argument("--vs_url", default="www.google.com", help='specify the url you want to test on')
    parser.add_argument("--vs_media_source", type=str, default='1')
    parser.add_argument("--vs_media_quality", type=str, default='0')
    parser.add_argument('--vs_duration', type=str, help='time to run traffic')
    parser.add_argument('--vs_device_list', help="Enter the devices on which the ping test should be run", default=[])
    #vs pass fail value
    parser.add_argument("--vs_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--vs_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #vs with groups and profile configuration
    parser.add_argument('--vs_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--vs_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--vs_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #vs configuration with --config
    parser.add_argument("--vs_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--vs_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--vs_passwd', '--vs_password', '--vs_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--vs_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional vs config args
    parser.add_argument("--vs_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--vs_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--vs_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--vs_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--vs_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--vs_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--vs_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--vs_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--vs_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--vs_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--vs_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--vs_pairwise", type=str, default='NA')
    parser.add_argument("--vs_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--vs_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--vs_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--vs_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--vs_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--vs_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--vs_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--vs_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--vs_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    #thput
    parser.add_argument('--thput_test',
                          action="store_true",
                          help='thput_test consists')
    parser.add_argument('--thput_test_duration', help='--thput_test_duration sets the duration of the test', default="")
    parser.add_argument('--thput_download', help='--thput_download traffic load per connection (download rate)', default='2560')
    parser.add_argument('--thput_traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False)
    parser.add_argument('--thput_upload', help='--thput_download traffic load per connection (download rate)', default='2560')
    parser.add_argument('--thput_device_list', help="Enter the devices on which the test should be run", default=[])
    parser.add_argument('--thput_do_interopability', action='store_true', help='Ensures test on devices run sequentially, capturing each device’s data individually for plotting in the final report.')
    parser.add_argument("--thput_default_config", action="store_true", help="To stop configuring the devices in interoperability")
    #thput pass fail value
    parser.add_argument("--thput_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--thput_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #thput with groups and profile configuration
    parser.add_argument('--thput_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--thput_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--thput_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument('--thput_load_type', help="Determine the type of load: < wc_intended_load | wc_per_client_load >", default="wc_per_client_load")
    parser.add_argument('--thput_packet_size', help='Determine the size of the packet in which Packet Size Should be Greater than 16B or less than 64KB(65507)', default="-1")

    #thput configuration with --config
    parser.add_argument("--thput_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--thput_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--thput_passwd', '--thput_password', '--thput_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--thput_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional thput config args
    parser.add_argument("--thput_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--thput_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--thput_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--thput_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--thput_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--thput_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--thput_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--thput_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--thput_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--thput_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--thput_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--thput_pairwise", type=str, default='NA')
    parser.add_argument("--thput_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--thput_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--thput_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--thput_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--thput_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--thput_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--thput_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--thput_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--thput_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    #mcast
    parser.add_argument('--mcast_test',
                          action="store_true",
                          help='mcast_test consists')
    parser.add_argument(
        '--mcast_test_duration',
        help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',
        default='3m')
    parser.add_argument(
        '--mcast_endp_type',
        help=(
            '--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\" '
            ' Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6'),
        default='lf_udp',
        type=valid_endp_types)
    parser.add_argument(
        '--mcast_upstream_port',
        help='--mcast_upstream_port <cross connect upstream_port> example: --mcast_upstream_port eth1',
        default='eth1')
    parser.add_argument(
        '--mcast_side_b_min_bps',
        help='''--side_b_min_bps or --download_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000
                When runnign with tcp/udp and mcast will use this value''',
        default="256000")
    parser.add_argument(
        '--mcast_tos',
        help='--tos:  Support different ToS settings: BK,BE,VI,VO,numeric',
        default="BE")
    parser.add_argument(
        '--mcast_device_list',
        action='append',
        help='Specify the Resource IDs for real clients. Accepts a comma-separated list (e.g., 1.11,1.95,1.360).'
    )
    #mcast pass fail value
    parser.add_argument("--mcast_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--mcast_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #mcast with groups and profile configuration
    parser.add_argument('--mcast_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--mcast_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--mcast_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #mcast configuration with --config
    parser.add_argument("--mcast_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--mcast_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--mcast_passwd', '--mcast_password', '--mcast_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--mcast_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional mcast config args
    parser.add_argument("--mcast_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--mcast_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--mcast_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--mcast_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--mcast_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--mcast_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--mcast_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--mcast_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--mcast_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--mcast_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--mcast_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--mcast_pairwise", type=str, default='NA')
    parser.add_argument("--mcast_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--mcast_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--mcast_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--mcast_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--mcast_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--mcast_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--mcast_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--mcast_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--mcast_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    #YOUTUBE
    parser.add_argument('--yt_test',
                          action="store_true",
                          help='mcast_test consists')
    parser.add_argument('--yt_url', type=str, help='youtube url')
    parser.add_argument('--yt_duration', help='duration to run the test in sec')
    parser.add_argument('--yt_res', default='Auto', help="to set resolution to  144p,240p,720p")
    # parser.add_argument('--yt_upstream_port', type=str, help='Specify The Upstream Port name or IP address', required=True)
    parser.add_argument('--yt_device_list', help='Specify the real device ports seperated by comma')
    #mcast pass fail value
    parser.add_argument("--yt_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--yt_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #yt with groups and profile configuration
    parser.add_argument('--yt_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--yt_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--yt_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #yt configuration with --config
    parser.add_argument("--yt_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--yt_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--yt_passwd', '--yt_password', '--yt_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--yt_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional yt config args
    parser.add_argument("--yt_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--yt_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--yt_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--yt_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--yt_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--yt_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--yt_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--yt_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--yt_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--yt_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--yt_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--yt_pairwise", type=str, default='NA')
    parser.add_argument("--yt_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--yt_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--yt_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--yt_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--yt_pac_file", type=str, default='NA', help='Specify the pac file name')
    # parser.add_argument('--yt_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    # parser.add_argument('--yt_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    # parser.add_argument('--yt_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument("--yt_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    #real browser
    parser.add_argument('--rb_test',
                          action="store_true",
                          help='mcast_test consists')
    parser.add_argument("--rb_url", default="https://google.com", help='specify the url you want to test on')
    parser.add_argument('--rb_duration', type=str, help='time to run traffic')
    parser.add_argument('--rb_device_list', type=str, help='provide resource_ids of android devices. for instance: "10,12,14"')
    parser.add_argument('--rb_webgui_incremental', '--rb_incremental_capacity', help="Specify the incremental values <1,2,3..>", dest='rb_webgui_incremental', type=str)
    parser.add_argument('--rb_incremental', help="to add incremental capacity to run the test", action='store_true')
    parser.add_argument("--rb_count", type=int, default=100, help='specify the number of url you want to test on '
                                                                    'per minute')
    #mcast pass fail value
    parser.add_argument("--rb_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--rb_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #rb with groups and profile configuration
    parser.add_argument('--rb_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--rb_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--rb_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #rb configuration with --config
    parser.add_argument("--rb_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--rb_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--rb_passwd', '--rb_password', '--rb_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--rb_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional rb config args
    parser.add_argument("--rb_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--rb_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--rb_ieee80211", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--rb_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--rb_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--rb_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--rb_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--rb_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--rb_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--rb_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--rb_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--rb_pairwise", type=str, default='NA')
    parser.add_argument("--rb_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--rb_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--rb_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--rb_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--rb_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--rb_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    #zoom
    parser.add_argument('--zoom_test',
                          action="store_true",
                          help='mcast_test consists')
    parser.add_argument('--zoom_duration', type=int, help="Duration of the Zoom meeting in minutes")
    parser.add_argument('--zoom_signin_email', type=str, help="Sign-in email")
    parser.add_argument('--zoom_signin_passwd', type=str, help="Sign-in password")
    parser.add_argument('--zoom_participants', type=int, help="no of participanrs")
    parser.add_argument('--zoom_audio', action='store_true')
    parser.add_argument('--zoom_video', action='store_true')
    parser.add_argument('--zoom_device_list', help="resources participated in the test")
    parser.add_argument('--zoom_host', help="Host of the test")
    #zoom config args
    parser.add_argument("--zoom_expected_passfail_value", help="Specify the expected number of urls", default=None)
    parser.add_argument("--zoom_device_csv_name", type=str, help='Specify the csv name to store expected url values', default=None)
    #zoom with groups and profile configuration
    parser.add_argument('--zoom_file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument('--zoom_group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--zoom_profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')

    #zoom configuration with --config
    parser.add_argument("--zoom_config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--zoom_ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--zoom_passwd', '--zoom_password', '--zoom_key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--zoom_security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    #Optional zoom config args
    parser.add_argument("--zoom_eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--zoom_eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--zoom_ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--zoom_ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--zoom_ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--zoom_enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--zoom_bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--zoom_power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--zoom_disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--zoom_roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--zoom_key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--zoom_pairwise", type=str, default='NA')
    parser.add_argument("--zoom_private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--zoom_ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--zoom_client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--zoom_pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--zoom_pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument("--zoom_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)
    parser.add_argument("--api_stats_collection", action="store_true", help='Specify if using business account to get the stats using api')
    parser.add_argument("--account_id", help="Zoom Account ID")
    parser.add_argument("--client_id", help="Zoom Client ID")
    parser.add_argument("--client_secret", help="Zoom Client Secret")
    parser.add_argument("--env_file", type=str, default='.env', help='Path to .env file for credentials')
    

    parser.add_argument('--vlc_mcast_addr',
                          type=str,
                          help='IP for streaming video on host',
                          default='239.255.0.1')
    parser.add_argument('--vlc_mcast_port',
                          type=str,
                          help='Port for streaming video on host',
                          default='1234')
    parser.add_argument('--vlc_host_res',
                          type=str,
                          help='host resource id to broadcast the video the video',
                          default=None)
    parser.add_argument('--vlc_video_name',
                          type=str,
                          help='Video file name to strema on host',
                          default=None)
    parser.add_argument('--vlc_duration',
                          type=str,
                          help='duration of test',
                          default='60')
    parser.add_argument('--vlc_server_ip',
                          type=str,
                          help='server ip on which client will request',
                          default="0.0.0.0")
    parser.add_argument('--vlc_server_port',
                          type=int,
                          help='port of flask server',
                          default=5959)       
    parser.add_argument('--vlc_help_summary', default=None, action="store_true", help='Show summary of what this script does')
    parser.add_argument('--vlc_device_list', help="Enter the devices on which the ping test should be run", default=[])
    parser.add_argument('--iot_test', help="If true will execute script for iot", action='store_true')
    optional.add_argument('--iot_ip',
                          default='127.0.0.1',
                          help='IP of the server')

    optional.add_argument('--iot_port',
                          default='8000',
                          help='Port of the server')
    optional.add_argument('--iot_iterations',
                          type=int,
                          default=1,
                          help='Iterations to run the test')

    optional.add_argument('--iot_delay',
                          type=int,
                          default=5,
                          help='Delay in seconds between iterations (min. 5 seconds)')

    optional.add_argument('--iot_device_list',
                          type=str,
                          default='',
                          help='Entity IDs of the devices to include in testing (comma separated)')

    optional.add_argument('--iot_testname',
                          type=str,
                          default='',
                          help='Testname for reporting')

    optional.add_argument('--iot_increment',
                          type=str,
                          default='',
                          help='Comma-separated list of device counts to incrementally test (e.g., "1,3,5")')
    # parser.add_argument('--do_mix_exec', help='Comma-separated list of tests to run in parallel')
    # parser.add_argument('--do_mix_exec', help="If true will execute script for webgui", default=False, type=bool)
    parser.add_argument('--do_mix_exec', action="store_true",  help='mcast_test consists')
    parser.add_argument('--query_devices', action="store_true",  help='mcast_test consists')
    parser.add_argument("--config_wait_time", type=int, help='Specify the maximum time to wait for Configuration', default=60)

    # Teams Automation
    parser.add_argument('--teams_test',
                          action="store_true",
                          help='teams_test consists')
    parser.add_argument('--teams_duration', type=int, help='duration to run the test in min')
    parser.add_argument('--teams_participants', type=int, help='No of Devices in the test')
    parser.add_argument('--teams_device_list', help='Specify the real device ports seperated by comma')
    parser.add_argument('--teams_audio', action='store_true')
    parser.add_argument('--teams_video', action='store_true')

    #whole config
    parser.add_argument('--group_name', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2')
    parser.add_argument('--profile_name', type=str, help='Specify the profile name to apply configurations to the devices.')
    parser.add_argument('--file_name', type=str, help='Specify the file name containing group details. Example:file1')
    parser.add_argument("--eap_method", type=str, default='DEFAULT', help="Specify the EAP method for authentication.")
    parser.add_argument("--eap_identity", type=str, default='', help="Specify the EAP identity for authentication.")
    parser.add_argument("--ieee8021x", action="store_true", help='Enables 802.1X enterprise authentication for test stations.')
    parser.add_argument("--ieee80211u", action="store_true", help='Enables IEEE 802.11u (Hotspot 2.0) support.')
    parser.add_argument("--ieee80211w", type=int, default=1, help='Enables IEEE 802.11w (Management Frame Protection) support.')
    parser.add_argument("--enable_pkc", action="store_true", help='Enables pkc support.')
    parser.add_argument("--bss_transition", action="store_true", help='Enables BSS transition support.')
    parser.add_argument("--power_save", action="store_true", help='Enables power-saving features.')
    parser.add_argument("--disable_ofdma", action="store_true", help='Disables OFDMA support.')
    parser.add_argument("--roam_ft_ds", action="store_true", help='Enables fast BSS transition (FT) support')
    parser.add_argument("--key_management", type=str, default='DEFAULT', help='Specify the key management method (e.g., WPA-PSK, WPA-EAP')
    parser.add_argument("--pairwise", type=str, default='NA')
    parser.add_argument("--private_key", type=str, default='NA', help='Specify EAP private key certificate file.')
    parser.add_argument("--ca_cert", type=str, default='NA', help='Specifiy the CA certificate file name')
    parser.add_argument("--client_cert", type=str, default='NA', help='Specify the client certificate file name')
    parser.add_argument("--pk_passwd", type=str, default='NA', help='Specify the password for the private key')
    parser.add_argument("--pac_file", type=str, default='NA', help='Specify the pac file name')
    parser.add_argument('--expected_passfail_value', help='Enter the expected throughput ', default=None)
    parser.add_argument('--device_csv_name', type=str, help='Enter the csv name to store expected values', default=None)
    parser.add_argument("--wait_time", type=int, help="Enter the maximum wait time for configurations to apply", default=60)
    parser.add_argument("--config", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--ssid', help='WiFi SSID for script objects to associate to')
    parser.add_argument('--passwd', '--password', '--key', default="[BLANK]", help='WiFi passphrase/password/key')
    parser.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default="open")
    parser.add_argument("--common", action="store_true", help="Specify for configuring the devices")
    parser.add_argument('--result_path', help="Specify the result dir to store the runtime logs <Do not use in CLI, --used by webui>", default=None)
    parser.add_argument("--auto_create", action="store_true", help="used to auto create result path id doesn't exist when --result_path given")
    
    parser.add_argument('--ping_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--http_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--ftp_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--qos_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--thpt_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--mcast_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--rb_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--zoom_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--teams_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--yt_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--vs_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")
    parser.add_argument('--vlc_groups', type=str, help='Specify the groups name that contains a list of devices. Example: group1,group2',default="all")

    return parser

def validation_args_before_obj(args):
    if args.vlc_duration.endswith('s') or args.vlc_duration.endswith('S'):
        args.vlc_duration = int(args.vlc_duration[0:-1])

    elif args.vlc_duration.endswith('m') or args.vlc_duration.endswith('M'):
        args.vlc_duration = int(args.vlc_duration[0:-1]) * 60

    elif args.vlc_duration.endswith('h') or args.vlc_duration.endswith('H'):
        args.vlc_duration = int(args.vlc_duration[0:-1]) * 60 * 60

    elif args.vlc_duration.endswith(''):
        args.vlc_duration = int(args.vlc_duration)
    if args.iot_test:
        iot_ip = args.iot_ip
        iot_port = args.iot_port
        iot_iterations = args.iot_iterations
        iot_delay = args.iot_delay
        iot_device_list = args.iot_device_list
        iot_testname = args.iot_testname
        iot_increment = args.iot_increment
    print(args)
    if args.result_path:
        if not ensure_path(args.result_path,args.auto_create):
            exit(0)
        
    if args.common and args.device_list or (args.file_name and args.group_name and args.profile_name):
        validate_args_config(args)
    elif args.common:
        logger.error("please give proper set of arguments for device selection, either provide --device_list or provide --file_name, --group_name and --profile_name for device selection")
        exit(0)
    if args.query_devices:
        # resource_stats = DeviceConfig.DeviceConfig(args.mgr,args.mgr_port,args.config_wait_time,file_name=args.file_name)
        resource_stats = DeviceConfig.DeviceConfig(lanforge_ip=args.mgr,port=args.mgr_port,wait_time=args.config_wait_time,file_name="grp61")
        all_devices = resource_stats.get_all_devices()
        # resource_stats.display_available_devices(all_devices)
        available_df = resource_stats.display_available_devices(all_devices)
        print(tabulate(available_df, headers='keys', tablefmt='fancy_grid'))
        if len(args.device_list) != 0:
            dev_list = args.device_list.split(',')
            name_to_res = {}
            res_to_name = {}
            for device in all_devices:
                if device["type"] == 'laptop':
                    name_to_res[device["hostname"]] = device["shelf"] + '.' + device["resource"]
                    res_to_name[device["shelf"] + '.' + device["resource"]] = device["hostname"]
                else:
                    name_to_res[device["serial"]] =  device["shelf"] + '.' + device["resource"]
                    res_to_name[device["shelf"] + '.' + device["resource"]] = device["serial"]
            print("name to res",name_to_res)
            print("res to name",res_to_name)
            filtered_dev_list,remarks_df = resource_stats.filter_device_list(dev_list, name_to_res, res_to_name)
            print(tabulate(remarks_df, headers='keys', tablefmt='fancy_grid'))
        exit(0)
    return args



def main():
    parser = parse_the_args()
    args = parser.parse_args()
    args = validation_args_before_obj(args)
    
    
    candela_apis = Candela(ip=args.mgr, port=args.mgr_port,order_priority=args.order_priority,test_name=args.test_name,result_dir=args.result_dir,dowebgui=args.dowebgui,no_cleanup=args.no_cleanup,do_mix_exec=args.do_mix_exec,config_wait_time=args.config_wait_time,device_list=args.device_list.split(',') if args.device_list else [],
                            group_name=args.group_name,
                            profile_name=args.profile_name,
                            file_name=args.file_name,
                            eap_method=args.eap_method,
                            eap_identity=args.eap_identity,
                            ieee80211=args.ieee8021x,
                            ieee80211u=args.ieee80211u,
                            ieee80211w=args.ieee80211w,
                            enable_pkc=args.enable_pkc,
                            bss_transition=args.bss_transition,
                            power_save=args.power_save,
                            disable_ofdma=args.disable_ofdma,
                            roam_ft_ds=args.roam_ft_ds,
                            key_management=args.key_management,
                            pairwise=args.pairwise,
                            private_key=args.private_key,
                            ca_cert=args.ca_cert,
                            client_cert=args.client_cert,
                            pk_passwd=args.pk_passwd,
                            pac_file=args.pac_file,
                            expected_passfail_val=args.expected_passfail_value,
                            csv_name=args.device_csv_name,
                            wait_time=args.wait_time,
                            config=args.config,
                            upstream_port=args.upstream_port,
                            ssid=args.ssid,
                            passwd=args.passwd,
                            security=args.security,
                            result_path=args.result_path,
                            args=args)

    if (args.config and args.device_list) or (args.file_name and args.group_name and args.profile_name):
        device_list = candela_apis.configure_devices()
        logger.info("Devices configured are {}".format(device_list))
        if not args.series_tests and not args.parallel_tests:
            exit(0)
        else:
            candela_apis.use_device_list(device_list)

    test_map = candela_apis.test_map.copy()
    tests_to_run_series,tests_to_run_parallel = candela_apis.filter_tests()

    duration_dict = candela_apis.create_duration_dict_and_validate()
    

    candela_apis.duration_dict = duration_dict.copy()
    # args.current = "series"
    candela_apis.start_tests(tests_to_run_parallel, tests_to_run_series,duration_dict)

def initialize_sniffer_obj(mgr="localhost",port="8080",sniff_radio='1.1.wiphy0',sniff_channel='AUTO',moni_name=None,pcap_name=None):
    print("CREATING sniffer object")
    if pcap_name is None:
        pcap_name = ("sniff_{}_channel_{}".format(sniff_radio,sniff_channel)).replace(".","_")
        pcap_name += ".pcap"
    sniffer_obj = Candela(ip=mgr,port=port,sniff_radio=sniff_radio,sniff_channel=sniff_channel,
                          moni_name=moni_name,pcap_name=pcap_name)
    return sniffer_obj

def convert_kwargs_to_cli_list(kwargs):
    cli_list = []
    for key,value in kwargs.items():
        if type(value) == bool:
            if value:
                cli_list.append("--{}".format(str(key)))
        else:
            cli_list.append("--{}".format(key))
            cli_list.append(str(value))
    return cli_list
    


def intialize_base_class_obj(**kwargs):
    cli_list = None
    cli = False
    print("kwargs",kwargs)
    if "cli" in kwargs:
        cli = kwargs["cli"]
    if "cli_list" in kwargs:
        cli_list = kwargs["cli_list"]
    if cli and cli_list:
        #TODO directly placing cli_list and validation
        pass
    else:
        cli_list = convert_kwargs_to_cli_list(kwargs)
    print("cli list",cli_list)
    parser = parse_the_args()
    args = parser.parse_args(cli_list)
    args = validation_args_before_obj(args)
    candela_apis = Candela(ip=args.mgr, port=args.mgr_port,order_priority=args.order_priority,test_name=args.test_name,result_dir=args.result_dir,dowebgui=args.dowebgui,no_cleanup=args.no_cleanup,do_mix_exec=args.do_mix_exec,config_wait_time=args.config_wait_time,device_list=args.device_list.split(',') if args.device_list else [],
                            group_name=args.group_name,
                            profile_name=args.profile_name,
                            file_name=args.file_name,
                            eap_method=args.eap_method,
                            eap_identity=args.eap_identity,
                            ieee80211=args.ieee8021x,
                            ieee80211u=args.ieee80211u,
                            ieee80211w=args.ieee80211w,
                            enable_pkc=args.enable_pkc,
                            bss_transition=args.bss_transition,
                            power_save=args.power_save,
                            disable_ofdma=args.disable_ofdma,
                            roam_ft_ds=args.roam_ft_ds,
                            key_management=args.key_management,
                            pairwise=args.pairwise,
                            private_key=args.private_key,
                            ca_cert=args.ca_cert,
                            client_cert=args.client_cert,
                            pk_passwd=args.pk_passwd,
                            pac_file=args.pac_file,
                            expected_passfail_val=args.expected_passfail_value,
                            csv_name=args.device_csv_name,
                            wait_time=args.wait_time,
                            config=args.config,
                            upstream_port=args.upstream_port,
                            ssid=args.ssid,
                            passwd=args.passwd,
                            security=args.security,
                            result_path=args.result_path,
                            args=args)
    return candela_apis
    
    



def run_test_safe(test_func, test_name, args, candela_apis,duration):
    global error_logs
    def wrapper():
        global error_logs
        
        try:
            result = test_func(args, candela_apis)
            if not result:
                status = "NOT EXECUTED"
                logger.error(f"{test_name} NOT EXECUTED")
            else:
                status = "EXECUTED"
                logger.info(f"{test_name} EXECUTED")
            # Update the dataframe with test result
            # test_results_df.loc[len(test_results_df)] = [test_name, status]
            test_results_list.append({"test_name": test_name, "Duration":duration, "status": status})
            
        except SystemExit as e:
            if e.code != 0:
                status = "NOT EXECUTED"
            else:
                status = "EXECUTED"
            tb = traceback.format_exc()
            print(tb)
            error_msg = f"{test_name} exited with code {e.code}\n"
            logger.error(error_msg)
            error_logs += error_msg
            # test_results_df.loc[len(test_results_df)] = [test_name, status]
            test_results_list.append({"test_name": test_name,"Duration":duration, "status": status})
            
        except Exception as e:
            status = "NOT EXECUTED"
            error_msg = f"{test_name} crashed unexpectedly\n"
            logger.exception(error_msg)
            tb_str = traceback.format_exc()
            logger.info("sussss")
            # traceback.print_exc()
            full_error = error_msg + tb_str + "\n"
            error_logs += full_error
            # test_results_df.loc[len(test_results_df)] = [test_name, status]
            test_results_list.append({"test_name": test_name,"Duration":duration, "status": status})
            
    return wrapper

def save_logs():
    """Save accumulated error logs to a timestamped file in base_class_logs directory"""
    global error_logs
    
        
    # Create directory if it doesn't exist
    log_dir = "base_class_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_dir}/test_logs_{timestamp}.txt"
    
    # Write logs to file
    with open(log_filename, 'w') as f:
        f.write(error_logs)
        
    logger.info(f"Test logs saved to {log_filename}")
    return log_filename

def trigger_iot(ip, port, iterations, delay, device_list, testname, increment):
    """
    Entry point to start the IoT test in a separate thread.
    This function is called from the throughput test script when IoT testing
    is enabled. It wraps the asynchronous `run_iot()`.
    """
    asyncio.run(run_iot(ip, port, iterations, delay, device_list, testname, increment))


async def run_iot(ip: str = '127.0.0.1',
                  port: str = '8000',
                  iterations: int = 1,
                  delay: int = 5,
                  device_list: str = '',
                  testname: str = '',
                  increment: str = ''):
    try:

        if delay < 5:
            logger.error('The minimum delay should be 5 seconds.')
            exit(1)

        if device_list != '':
            device_list = device_list.split(',')
        else:
            device_list = None
        # Parse and validate increment pattern if provided
        if increment:
            print("the increment is : ", increment)
            try:
                increment = list(map(int, increment.split(',')))
                if any(i < 1 for i in increment):
                    logger.error('Increment values must be positive integers')
                    exit(1)
            except ValueError:
                logger.error('Invalid increment format. Please provide comma-separated integers (e.g., "1,3,5")')
                exit(1)

        testname = testname

        # Ensure test name is unique (avoid overwriting previous results)
        if testname in os.listdir('../../local/interop-webGUI/IoT/scripts/results/'):
            logger.error('Test with same name already existing. Please give a different testname.')
            exit(1)
        automation = Automation(ip=ip,
                                port=port,
                                iterations=iterations,
                                delay=delay,
                                device_list=device_list,
                                testname=testname,
                                increment=increment)

        # fetch the available iot devices
        automation.devices = await automation.fetch_iot_devices()

        # select the iot devices for testing
        automation.select_iot_devices()

        # run the iot test on selected devices
        automation.run_test()

        # generate the iot report
        automation.generate_report()

    except Exception as e:
        logger.error(f"Iot Test failed: {str(e)}")
        raise

    await automation.session.close()

    logger.info('Iot Test Completed.')

def run_ping_test(args, candela_apis):
    return candela_apis.run_ping_test(
        real=True,
        target=args.ping_target,
        ping_interval=args.ping_interval,
        ping_duration=args.ping_duration,
        use_default_config=False if args.ping_config else True,
        dev_list=args.ping_device_list,
        expected_passfail_value=args.ping_expected_passfail_value,
        device_csv_name=args.ping_device_csv_name,
        file_name=args.ping_file_name,
        group_name=args.ping_group_name,
        profile_name=args.ping_profile_name,
        ssid=args.ping_ssid,
        passwd=args.ping_passwd,
        security=args.ping_security,
        eap_method=args.ping_eap_method,
        eap_identity=args.ping_eap_identity,
        ieee8021x=args.ping_ieee8021x,
        ieee80211u=args.ping_ieee80211u,
        ieee80211w=args.ping_ieee80211w,
        enable_pkc=args.ping_enable_pkc,
        bss_transition=args.ping_bss_transition,
        power_save=args.ping_power_save,
        disable_ofdma=args.ping_disable_ofdma,
        roam_ft_ds=args.ping_roam_ft_ds,
        key_management=args.ping_key_management,
        pairwise=args.ping_pairwise,
        private_key=args.ping_private_key,
        ca_cert=args.ping_ca_cert,
        client_cert=args.ping_client_cert,
        pk_passwd=args.ping_pk_passwd,
        pac_file=args.ping_pac_file,
        wait_time=args.ping_wait_time,
        local_lf_report_dir = candela_apis.result_path if not args.dowebgui else args.result_dir,
        sta_to_res=args.ping_sta_to_res,
        sta_port=args.ping_sta_port,
        res_ip=args.ping_res_ip
    )

def run_http_test(args, candela_apis):
    return candela_apis.run_http_test(
        upstream_port=args.upstream_port,
        bands=args.http_bands,
        duration=args.http_duration,
        file_size=args.http_file_size,
        device_list=args.http_device_list,
        expected_passfail_value=args.http_expected_passfail_value,
        device_csv_name=args.http_device_csv_name,
        file_name=args.http_file_name,
        group_name=args.http_group_name,
        profile_name=args.http_profile_name,
        config=args.http_config,
        ssid=args.http_ssid,
        passwd=args.http_passwd,
        security=args.http_security,
        eap_method=args.http_eap_method,
        eap_identity=args.http_eap_identity,
        ieee8021x=args.http_ieee8021x,
        ieee80211u=args.http_ieee80211u,
        ieee80211w=args.http_ieee80211w,
        enable_pkc=args.http_enable_pkc,
        bss_transition=args.http_bss_transition,
        power_save=args.http_power_save,
        disable_ofdma=args.http_disable_ofdma,
        roam_ft_ds=args.http_roam_ft_ds,
        key_management=args.http_key_management,
        pairwise=args.http_pairwise,
        private_key=args.http_private_key,
        ca_cert=args.http_ca_cert,
        client_cert=args.http_client_cert,
        pk_passwd=args.http_pk_passwd,
        pac_file=args.http_pac_file,
        wait_time=args.http_wait_time,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir
    )

def run_ftp_test(args, candela_apis):
    return candela_apis.run_ftp_test(
        device_list=args.ftp_device_list,
        file_sizes=[args.ftp_file_size],
        traffic_duration=args.ftp_duration,
        bands=args.ftp_bands,
        expected_passfail_value=args.ftp_expected_passfail_value,
        device_csv_name=args.ftp_device_csv_name,
        file_name=args.ftp_file_name,
        group_name=args.ftp_group_name,
        profile_name=args.ftp_profile_name,
        config=args.ftp_config,
        ssid=args.ftp_ssid,
        passwd=args.ftp_passwd,
        security=args.ftp_security,
        eap_method=args.ftp_eap_method,
        eap_identity=args.ftp_eap_identity,
        ieee8021x=args.ftp_ieee8021x,
        ieee80211u=args.ftp_ieee80211u,
        ieee80211w=args.ftp_ieee80211w,
        enable_pkc=args.ftp_enable_pkc,
        bss_transition=args.ftp_bss_transition,
        power_save=args.ftp_power_save,
        disable_ofdma=args.ftp_disable_ofdma,
        roam_ft_ds=args.ftp_roam_ft_ds,
        key_management=args.ftp_key_management,
        pairwise=args.ftp_pairwise,
        private_key=args.ftp_private_key,
        ca_cert=args.ftp_ca_cert,
        client_cert=args.ftp_client_cert,
        pk_passwd=args.ftp_pk_passwd,
        pac_file=args.ftp_pac_file,
        wait_time=args.ftp_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir,
        upstream_port=args.upstream_port,
    )

def run_qos_test(args, candela_apis):
    print("QOS_LIST",args.qos_device_list)
    return candela_apis.run_qos_test(
        upstream_port=args.upstream_port,
        test_duration=args.qos_duration,
        download=args.qos_download,
        upload=args.qos_upload,
        traffic_type=args.qos_traffic_type,
        tos=args.qos_tos,
        device_list=args.qos_device_list,
        expected_passfail_value=args.qos_expected_passfail_value,
        device_csv_name=args.qos_device_csv_name,
        file_name=args.qos_file_name,
        group_name=args.qos_group_name,
        profile_name=args.qos_profile_name,
        config=args.qos_config,
        ssid=args.qos_ssid,
        passwd=args.qos_passwd,
        security=args.qos_security,
        eap_method=args.qos_eap_method,
        eap_identity=args.qos_eap_identity,
        ieee8021x=args.qos_ieee8021x,
        ieee80211u=args.qos_ieee80211u,
        ieee80211w=args.qos_ieee80211w,
        enable_pkc=args.qos_enable_pkc,
        bss_transition=args.qos_bss_transition,
        power_save=args.qos_power_save,
        disable_ofdma=args.qos_disable_ofdma,
        roam_ft_ds=args.qos_roam_ft_ds,
        key_management=args.qos_key_management,
        pairwise=args.qos_pairwise,
        private_key=args.qos_private_key,
        ca_cert=args.qos_ca_cert,
        client_cert=args.qos_client_cert,
        pk_passwd=args.qos_pk_passwd,
        pac_file=args.qos_pac_file,
        wait_time=args.qos_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir
    )

def run_vs_test(args, candela_apis):
    return candela_apis.run_vs_test1(
        url=args.vs_url,
        media_source=args.vs_media_source,
        media_quality=args.vs_media_quality,
        duration=args.vs_duration,
        device_list=args.vs_device_list,
        expected_passfail_value=args.vs_expected_passfail_value,
        device_csv_name=args.vs_device_csv_name,
        file_name=args.vs_file_name,
        group_name=args.vs_group_name,
        profile_name=args.vs_profile_name,
        config=args.vs_config,
        ssid=args.vs_ssid,
        passwd=args.vs_passwd,
        encryp=args.vs_security,
        eap_method=args.vs_eap_method,
        eap_identity=args.vs_eap_identity,
        ieee8021x=args.vs_ieee8021x,
        ieee80211u=args.vs_ieee80211u,
        ieee80211w=args.vs_ieee80211w,
        enable_pkc=args.vs_enable_pkc,
        bss_transition=args.vs_bss_transition,
        power_save=args.vs_power_save,
        disable_ofdma=args.vs_disable_ofdma,
        roam_ft_ds=args.vs_roam_ft_ds,
        key_management=args.vs_key_management,
        pairwise=args.vs_pairwise,
        private_key=args.vs_private_key,
        ca_cert=args.vs_ca_cert,
        client_cert=args.vs_client_cert,
        pk_passwd=args.vs_pk_passwd,
        pac_file=args.vs_pac_file,
        wait_time=args.vs_wait_time,
        upstream_port=args.upstream_port,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir
    )

def run_thput_test(args, candela_apis):
    if args.thput_do_interopability and args.thput_config:
        args.thput_default_config = False
        args.thput_config = False
    elif args.thput_do_interopability:
        args.thput_default_config = True
    return candela_apis.run_throughput_test(
        upstream_port=args.upstream_port,
        test_duration=args.thput_test_duration,
        download=args.thput_download,
        upload=args.thput_upload,
        traffic_type=args.thput_traffic_type,
        device_list=args.thput_device_list,
        do_interopability=args.thput_do_interopability,
        default_config=args.thput_default_config,
        expected_passfail_value=args.thput_expected_passfail_value,
        device_csv_name=args.thput_device_csv_name,
        file_name=args.thput_file_name,
        group_name=args.thput_group_name,
        profile_name=args.thput_profile_name,
        config=args.thput_config,
        ssid=args.thput_ssid,
        passwd=args.thput_passwd,
        security=args.thput_security,
        eap_method=args.thput_eap_method,
        eap_identity=args.thput_eap_identity,
        ieee8021x=args.thput_ieee8021x,
        ieee80211u=args.thput_ieee80211u,
        ieee80211w=args.thput_ieee80211w,
        enable_pkc=args.thput_enable_pkc,
        bss_transition=args.thput_bss_transition,
        power_save=args.thput_power_save,
        disable_ofdma=args.thput_disable_ofdma,
        roam_ft_ds=args.thput_roam_ft_ds,
        key_management=args.thput_key_management,
        pairwise=args.thput_pairwise,
        private_key=args.thput_private_key,
        ca_cert=args.thput_ca_cert,
        client_cert=args.thput_client_cert,
        pk_passwd=args.thput_pk_passwd,
        pac_file=args.thput_pac_file,
        wait_time=args.thput_wait_time,
        load_type=args.thput_load_type,
        packet_size=args.thput_packet_size,
        dowebgui=args.dowebgui,
        test_name=args.test_name,
        result_dir=args.result_dir
    )

def run_mcast_test(args, candela_apis):
    return candela_apis.run_mc_test1(
        test_duration=args.mcast_test_duration,
        upstream_port=args.upstream_port,
        endp_type=args.mcast_endp_type,
        side_b_min_bps=args.mcast_side_b_min_bps,
        tos=args.mcast_tos,
        device_list=args.mcast_device_list,
        expected_passfail_value=args.mcast_expected_passfail_value,
        device_csv_name=args.mcast_device_csv_name,
        file_name=args.mcast_file_name,
        group_name=args.mcast_group_name,
        profile_name=args.mcast_profile_name,
        config=args.mcast_config,
        ssid=args.mcast_ssid,
        passwd=args.mcast_passwd,
        security=args.mcast_security,
        eap_method=args.mcast_eap_method,
        eap_identity=args.mcast_eap_identity,
        ieee8021x=args.mcast_ieee8021x,
        ieee80211u=args.mcast_ieee80211u,
        ieee80211w=args.mcast_ieee80211w,
        enable_pkc=args.mcast_enable_pkc,
        bss_transition=args.mcast_bss_transition,
        power_save=args.mcast_ieee8021x,
        disable_ofdma=args.mcast_disable_ofdma,
        roam_ft_ds=args.mcast_roam_ft_ds,
        key_management=args.mcast_key_management,
        pairwise=args.mcast_pairwise,
        private_key=args.mcast_private_key,
        ca_cert=args.mcast_ca_cert,
        client_cert=args.mcast_client_cert,
        pk_passwd=args.mcast_pk_passwd,
        pac_file=args.mcast_pac_file,
        wait_time=args.mcast_wait_time,
        dowebgui="True" if args.dowebgui else False,
        test_name=args.test_name,
        result_dir=args.result_dir
    )

def run_yt_test(args, candela_apis):
    return candela_apis.run_yt_test(
        url=args.yt_url,
        duration=args.yt_duration,
        res=args.yt_res,
        upstream_port=args.upstream_port,
        resource_list=args.yt_device_list,
        expected_passfail_value=args.yt_expected_passfail_value,
        device_csv_name=args.yt_device_csv_name,
        file_name=args.yt_file_name,
        group_name=args.yt_group_name,
        profile_name=args.yt_profile_name,
        config=args.yt_config,
        ssid=args.yt_ssid,
        passwd=args.yt_passwd,
        encryp=args.yt_security,
        eap_method=args.yt_eap_method,
        eap_identity=args.yt_eap_identity,
        ieee8021x=args.yt_ieee8021x,
        ieee80211u=args.yt_ieee80211u,
        ieee80211w=args.yt_ieee80211w,
        enable_pkc=args.yt_enable_pkc,
        bss_transition=args.yt_bss_transition,
        power_save=args.yt_ieee8021x,
        disable_ofdma=args.yt_disable_ofdma,
        roam_ft_ds=args.yt_roam_ft_ds,
        key_management=args.yt_key_management,
        pairwise=args.yt_pairwise,
        private_key=args.yt_private_key,
        ca_cert=args.yt_ca_cert,
        client_cert=args.yt_client_cert,
        pk_passwd=args.yt_pk_passwd,
        pac_file=args.yt_pac_file,
        exec_type=args.current,
        do_webUI="True" if args.dowebgui else False,
        ui_report_dir = args.result_dir,
        test_name=args.test_name
    )

def run_rb_test(args, candela_apis):
    return candela_apis.run_rb_test(
        url=args.rb_url,
        upstream_port=args.upstream_port,
        device_list=args.rb_device_list,
        expected_passfail_value=args.rb_expected_passfail_value,
        device_csv_name=args.rb_device_csv_name,
        file_name=args.rb_file_name,
        group_name=args.rb_group_name,
        profile_name=args.rb_profile_name,
        config=args.rb_config,
        ssid=args.rb_ssid,
        passwd=args.rb_passwd,
        encryp=args.rb_security,
        eap_method=args.rb_eap_method,
        eap_identity=args.rb_eap_identity,
        ieee80211=args.rb_ieee80211,
        ieee80211u=args.rb_ieee80211u,
        ieee80211w=args.rb_ieee80211w,
        enable_pkc=args.rb_enable_pkc,
        bss_transition=args.rb_bss_transition,
        power_save=args.rb_power_save,
        disable_ofdma=args.rb_disable_ofdma,
        roam_ft_ds=args.rb_roam_ft_ds,
        key_management=args.rb_key_management,
        pairwise=args.rb_pairwise,
        private_key=args.rb_private_key,
        ca_cert=args.rb_ca_cert,
        client_cert=args.rb_client_cert,
        pk_passwd=args.rb_pk_passwd,
        pac_file=args.rb_pac_file,
        wait_time=args.rb_wait_time,
        duration=args.rb_duration,
        exec_type=args.current,
        count = args.rb_count,
        dowebgui = args.dowebgui,
        result_dir=args.result_dir,
        test_name=args.test_name,
        webgui_incremental=args.rb_webgui_incremental
    )

def run_zoom_test(args, candela_apis):
    return candela_apis.run_zoom_test(
        duration=args.zoom_duration,
        signin_email=args.zoom_signin_email,
        signin_passwd=args.zoom_signin_passwd,
        participants=args.zoom_participants,
        audio=args.zoom_audio,
        video=args.zoom_video,
        upstream_port=args.upstream_port,
        resource_list=args.zoom_device_list,
        zoom_host=args.zoom_host,
        expected_passfail_value=args.zoom_expected_passfail_value,
        device_csv_name=args.zoom_device_csv_name,
        file_name=args.zoom_file_name,
        group_name=args.zoom_group_name,
        profile_name=args.zoom_profile_name,
        config=args.zoom_config,
        ssid=args.zoom_ssid,
        passwd=args.zoom_passwd,
        encryp=args.zoom_security,
        eap_method=args.zoom_eap_method,
        eap_identity=args.zoom_eap_identity,
        ieee8021x=args.zoom_ieee8021x,
        ieee80211u=args.zoom_ieee80211u,
        ieee80211w=args.zoom_ieee80211w,
        enable_pkc=args.zoom_enable_pkc,
        bss_transition=args.zoom_bss_transition,
        power_save=args.zoom_power_save,
        disable_ofdma=args.zoom_disable_ofdma,
        roam_ft_ds=args.zoom_roam_ft_ds,
        key_management=args.zoom_key_management,
        pairwise=args.zoom_pairwise,
        private_key=args.zoom_private_key,
        ca_cert=args.zoom_ca_cert,
        client_cert=args.zoom_client_cert,
        pk_passwd=args.zoom_pk_passwd,
        pac_file=args.zoom_pac_file,
        wait_time=args.zoom_wait_time,
        exec_type=args.current,
        do_webUI= args.dowebgui,
        report_dir= args.result_dir,
        testname= args.test_name,
        env_file=args.env_file,
        api_stats_collection=args.api_stats_collection,
        client_id=args.client_id,
        client_secret=args.client_secret,
        account_id=args.account_id,
    )

def run_vlc_test(args,candela_apis):
    return candela_apis.run_vlc_test(
        mcast_addr=args.vlc_mcast_addr,
        mcast_port=args.vlc_mcast_port,
        host_res=args.vlc_host_res,
        video_name=args.vlc_video_name,
        duration=args.vlc_duration,
        server_ip=args.vlc_server_ip,
        server_port=args.vlc_server_port,
        help_summary=args.vlc_help_summary,
        device_list=args.vlc_device_list
    )
def run_teams_test(args, candela_apis):
    return candela_apis.run_teams_test(
        upstream_port=args.upstream_port,
        duration=args.teams_duration,
        participants_req=args.teams_participants,
        audio=args.teams_audio,
        video=args.teams_video,
        resource_list=args.teams_device_list,
        do_webUI=args.dowebgui,
        report_dir=args.result_dir,
        testname=args.test_name   
    )
# def browser_cleanup(args,candela_apis):
#     return candela_apis.browser_cleanup(args)
if __name__ == "__main__":
    main()