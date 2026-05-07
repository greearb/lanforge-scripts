#!/usr/bin/env python3
"""
NAME: lf_roam_test.py

PURPOSE: lf_hard_rome_test.py works on both roaming methods i.e. hard/forced roaming and also attenuation based roaming
        (soft roam)  specific or purely based  to 11r.
       - By default, this script executes a hard roaming process and provides the results of the 11r roam test pdf,
         as well as all the packet captures generated after the roam test. However, to perform a soft roam, the soft_roam
         parameter must be set to true.

Hard Roam
EXAMPLE: For a single station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For a single station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For multiple station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For multiple station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For  multiple station and multiple iteration with multicast traffic enable
   python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "10:f9:20:fd:f3:4b" --ap2_bssid "14:16:9d:53:58:cb"
   --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 2 --ssid_name "RoamAP5g" --security "wpa2"
     --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "36" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --sta_type normal --multicast True

Soft Roam
EXAMPLE: For a single station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For a single station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For multiple station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For multiple station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

SCRIPT_CLASSIFICATION:  Test
NOTES:

The primary focus of this script is to enable seamless roaming of clients/stations between two access points (APs).
The test can be conducted with a single or multiple stations, with single or multiple iterations.

The script will create stations/clients with advanced/802.1x and 11r key management. By default, it will create a
single station/client. Once the stations are created, the script will generate CX traffic between the upstream port and
 the stations and run the traffic before roam.

Packet captures will be taken for each station/client in two scenarios:

    (i)  While the station/client is connected to an AP
    (ii) While the station/client roams from one AP to another AP

These packet captures will be used to analyze the performance and stability of the roaming process.

Overall, this script is designed to provide a comprehensive test of the roaming functionality of the APs and the
stability of the network when clients move between APs.

 The following are the criteria for PASS the test:

    1. The BSSID of the station should change after roaming from one AP to another
    2  The station should not experience any disconnections during/after the roaming process.
    3. The duration of the roaming process should be less than 50 ms.

 The following are the criteria for FAIL the test:

    1. The BSSID of the station remains unchanged after roaming from one AP to another.
    2. No roaming occurs, as all stations are connected to the same AP.
    3. The captured packet does not contain a Reassociation Response Frame.
    4. The station experiences disconnection during/after the roaming process.
    5. The duration of the roaming process exceeds 50 ms.

STATUS: BETA RELEASE (MORE TESTING ONLY WITH MULTICAST)

VERIFIED_ON: 15-MAY-2023, Underdevelopment

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README: False
"""

import sys
import os
import importlib
import logging
import time
import datetime
from datetime import datetime  # noqa: F811
import pandas as pd
import paramiko
from itertools import chain
import argparse

logger = logging.getLogger(__name__)
if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
cv_test_reports = importlib.import_module("py-json.cv_test_reports")
lf_report = cv_test_reports.lanforge_reports
lf_report_pdf = importlib.import_module("py-scripts.lf_report")
lf_csv = importlib.import_module("py-scripts.lf_csv")
lf_pcap = importlib.import_module("py-scripts.lf_pcap")
lf_graph = importlib.import_module("py-scripts.lf_graph")
sniff_radio = importlib.import_module("py-scripts.lf_sniff_radio")
sta_connect = importlib.import_module("py-scripts.sta_connect2")
lf_clean = importlib.import_module("py-scripts.lf_cleanup")
series = importlib.import_module("cc_module_9800_3504")
attenuator = importlib.import_module("py-scripts.attenuator_serial")
modify = importlib.import_module("py-scripts.lf_atten_mod_test")
multicast_profile = importlib.import_module("py-json.multicast_profile")


TIME_FORMAT = '%y %b %d %H:%M:%S'


class HardRoam(Realm):
    def __init__(self, lanforge_ip=None,
                 lanforge_port=None,
                 lanforge_ssh_port=None,
                 c1_bssid=None,
                 c2_bssid=None,
                 fiveg_radio=None,
                 twog_radio=None,
                 sixg_radio=None,
                 band=None,
                 sniff_radio_=None,
                 num_sta=None,
                 security=None,
                 security_key=None,
                 ssid=None,
                 upstream=None,
                 duration=None,
                 iteration=None,
                 channel=None,
                 option=None,
                 duration_based=None,
                 iteration_based=None,
                 dut_name=None,
                 traffic_type="lf_udp",
                 roaming_delay=None,
                 path="../",
                 scheme="ssh",
                 dest="localhost",
                 user="admin",
                 passwd="Cisco123",
                 prompt="WLC2",
                 series_cc="9800",
                 ap="AP687D.B45C.1D1C",
                 port="8888",
                 band_cc="5g",
                 timeout="10",
                 identity=None,
                 ttls_pass=None,
                 log_file=False,
                 debug=False,
                 soft_roam=False,
                 sta_type=None,
                 multicast=None,
                 **kwargs):
        super().__init__(lanforge_ip,
                         lanforge_port)
        self.lanforge_ip = lanforge_ip
        self.lanforge_port = lanforge_port
        self.lanforge_ssh_port = lanforge_ssh_port
        self.c1_bssid = c1_bssid
        self.c2_bssid = c2_bssid
        self.fiveg_radios = fiveg_radio
        self.twog_radios = twog_radio
        self.sixg_radios = sixg_radio
        self.band = band
        self.sniff_radio = sniff_radio_
        self.num_sta = num_sta
        self.ssid_name = ssid
        self.security = security
        self.security_key = security_key
        self.upstream = upstream
        self.duration = duration
        self.iteration = iteration
        self.channel = channel
        self.option = option
        self.iteration_based = iteration_based
        self.duration_based = duration_based
        self.local_realm = realm.Realm(lfclient_host=self.lanforge_ip, lfclient_port=self.lanforge_port)
        self.staConnect = sta_connect.StaConnect2(host=self.lanforge_ip, port=self.lanforge_port,
                                                  outfile="sta_connect2.csv")
        self.final_bssid = []
        self.pcap_obj_2 = None
        self.pcap_name = None
        self.test_duration = None
        self.client_list = []
        self.dut_name = dut_name
        self.pcap_obj = lf_pcap.LfPcap()
        self.lf_csv_obj = lf_csv.lf_csv()
        self.traffic_type = traffic_type
        self.roam_delay = roaming_delay
        self.sta_type = sta_type
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.cc = None
        self.cc = series.create_controller_series_object(
            scheme=scheme,
            dest=dest,
            user=user,
            passwd=passwd,
            prompt=prompt,
            series=series_cc,
            ap=ap,
            port=port,
            band=band_cc,
            timeout=timeout)
        self.cc.pwd = path
        self.start_time = None
        self.end_time = None
        self.identity = identity
        self.ttls_pass = ttls_pass
        self.log_file = log_file
        self.debug = debug
        self.mac_data = None
        self.soft_roam = soft_roam
        self.multicast = multicast
        # logging.basicConfig(filename='roam.log', filemode='w', level=logging.INFO, force=True)
        self.multi_cast_profile = multicast_profile.MULTICASTProfile(self.lanforge_ip, self.lanforge_port,
                                                                     local_realm=self)

    # Start debugger of controller
    def start_debug_(self, mac_list):
        mac = mac_list
        for i in mac:
            y = self.cc.debug_wireless_mac_cc(mac=str(i))
            print(y)

    # Stop debugger of controller
    def stop_debug_(self, mac_list):
        mac = mac_list
        for i in mac:
            y = self.cc.no_debug_wireless_mac_cc(mac=str(i))
            print(y)

    # Get trace file names from controller
    def get_ra_trace_file(self):
        ra = self.cc.get_ra_trace_files__cc()
        print(ra)
        ele_list = [y for y in (x.strip() for x in ra.splitlines()) if y]
        print(ele_list)
        return ele_list

    # Get trace file names from controller with respect to number of clients
    def get_file_name(self, client):
        file_name = []
        if not self.debug:
            for i in range(client):
                file_name.append("debug disabled")
        else:
            file = self.get_ra_trace_file()
            indices = [i for i, s in enumerate(file) if 'dir bootflash: | i ra_trace' in s]
            # print(indices)
            y = indices[-1]
            if client == 1:
                z = file[y + 1]
                list_ = [z]
                m = list_[0].split(" ")
                print(m)
                print(len(m))
                print(m[-1])
                if m[-1].isnumeric():
                    print("Log file not Available")
                    file_name.append("file not found")
                file_name.append(m[-1])
            else:
                z = file[y + (int(0) + 1)]
                list_ = [z]
                m = list_[0].split(" ")
                print(m)
                print(len(m))
                print(m[-1])
                if m[-1].isnumeric():
                    print("Log file not Available")
                    for i in range(client):
                        file_name.append("file not found")
                else:
                    for i in range(client):
                        z = file[y + (int(i) + 1)]
                        list_ = [z]
                        m = list_[0].split(" ")
                        print(m)
                        print(len(m))
                        print(m[-1])
                        if m[-1].isnumeric():
                            print("Log file not Available")
                            file_name.append("file not found")
                        file_name.append(m[-1])
            print("File_name", file_name)
            file_name.reverse()
        return file_name

    # delete trace file from controller
    def delete_trace_file(self, file):
        # file = self.get_file_name()
        self.cc.del_ra_trace_file_cc(file=file)

    # get station list from lf
    def get_station_list(self):
        sta = self.staConnect.station_list()
        if sta == "no response":
            return "no response"
        sta_list = []
        for i in sta:
            for j in i:
                sta_list.append(j)
        return sta_list

    # Create N - number of clients of advanced configuration on lf
    def create_n_clients(self, start_id=0, sta_prefix=None, num_sta=None, dut_ssid=None,
                         dut_security=None, dut_passwd=None, radio=None):

        local_realm = realm.Realm(lfclient_host=self.lanforge_ip, lfclient_port=self.lanforge_port)
        station_profile = local_realm.new_station_profile()
        if self.band == "fiveg":
            radio = self.fiveg_radios
        if self.band == "twog":
            radio = self.twog_radios
        if self.band == "sixg":
            radio = self.sixg_radios

        logger.info("Creating stations.")
        station_list = LFUtils.portNameSeries(prefix_=sta_prefix, start_id_=start_id,
                                              end_id_=num_sta - 1, padding_number_=10000,
                                              radio=radio)
        if self.sta_type == "normal":
            if not self.soft_roam:
                station_profile.set_command_flag("add_sta", "disable_roam", 1)
            if self.soft_roam:
                logger.info("Soft roam true")
                if self.option == "otds":
                    print("OTDS present")
                    station_profile.set_command_flag("add_sta", "ft-roam-over-ds", 1)

        if self.sta_type == "11r-sae-802.1x":
            dut_passwd = "[BLANK]"
        station_profile.use_security(dut_security, dut_ssid, dut_passwd)
        station_profile.set_number_template("00")

        station_profile.set_command_flag("add_sta", "create_admin_down", 1)

        station_profile.set_command_param("set_port", "report_timer", 1500)

        # connect station to particular bssid
        # self.station_profile.set_command_param("add_sta", "ap", self.bssid[0])

        station_profile.set_command_flag("set_port", "rpt_timer", 1)
        if self.sta_type == "11r":
            station_profile.set_command_flag("add_sta", "80211u_enable", 0)
            station_profile.set_command_flag("add_sta", "8021x_radius", 1)
            if not self.soft_roam:
                # station_profile.ssid_pass = self.security_key
                station_profile.set_command_flag("add_sta", "disable_roam", 1)
            if self.soft_roam:
                logger.info("Soft roam true")
                if self.option == "otds":
                    print("OTDS present")
                    station_profile.set_command_flag("add_sta", "ft-roam-over-ds", 1)
            station_profile.set_wifi_extra(key_mgmt="FT-PSK     ",
                                           pairwise="",
                                           group="",
                                           psk="",
                                           eap="",
                                           identity="",
                                           passwd="",
                                           pin="",
                                           phase1="NA",
                                           phase2="NA",
                                           pac_file="NA",
                                           private_key="NA",
                                           pk_password="NA",
                                           hessid="00:00:00:00:00:01",
                                           realm="localhost.localdomain",
                                           client_cert="NA",
                                           imsi="NA",
                                           milenage="NA",
                                           domain="localhost.localdomain",
                                           roaming_consortium="NA",
                                           venue_group="NA",
                                           network_type="NA",
                                           ipaddr_type_avail="NA",
                                           network_auth_type="NA",
                                           anqp_3gpp_cell_net="NA")
        if self.sta_type == "11r-sae":
            station_profile.set_command_flag("add_sta", "ieee80211w", 2)
            station_profile.set_command_flag("add_sta", "80211u_enable", 0)
            station_profile.set_command_flag("add_sta", "8021x_radius", 1)
            # station_profile.set_command_flag("add_sta", "disable_roam", 1)
            if not self.soft_roam:
                station_profile.set_command_flag("add_sta", "disable_roam", 1)
            if self.soft_roam:
                if self.option == "otds":
                    station_profile.set_command_flag("add_sta", "ft-roam-over-ds", 1)
            station_profile.set_wifi_extra(key_mgmt="FT-SAE     ",
                                           pairwise="",
                                           group="",
                                           psk="",
                                           eap="",
                                           identity="",
                                           passwd="",
                                           pin="",
                                           phase1="NA",
                                           phase2="NA",
                                           pac_file="NA",
                                           private_key="NA",
                                           pk_password="NA",
                                           hessid="00:00:00:00:00:01",
                                           realm="localhost.localdomain",
                                           client_cert="NA",
                                           imsi="NA",
                                           milenage="NA",
                                           domain="localhost.localdomain",
                                           roaming_consortium="NA",
                                           venue_group="NA",
                                           network_type="NA",
                                           ipaddr_type_avail="NA",
                                           network_auth_type="NA",
                                           anqp_3gpp_cell_net="NA")
        if self.sta_type == "11r-sae-802.1x":
            station_profile.set_command_flag("set_port", "rpt_timer", 1)
            station_profile.set_command_flag("add_sta", "ieee80211w", 2)
            station_profile.set_command_flag("add_sta", "80211u_enable", 0)
            station_profile.set_command_flag("add_sta", "8021x_radius", 1)
            if not self.soft_roam:
                station_profile.set_command_flag("add_sta", "disable_roam", 1)
            if self.soft_roam:
                if self.option == "otds":
                    station_profile.set_command_flag("add_sta", "ft-roam-over-ds", 1)
            # station_profile.set_command_flag("add_sta", "disable_roam", 1)
            # station_profile.set_command_flag("add_sta", "ap", "68:7d:b4:5f:5c:3f")
            station_profile.set_wifi_extra(key_mgmt="FT-EAP     ",
                                           pairwise="[BLANK]",
                                           group="[BLANK]",
                                           psk="[BLANK]",
                                           eap="TTLS",
                                           identity=self.identity,
                                           passwd=self.ttls_pass,
                                           pin="",
                                           phase1="NA",
                                           phase2="NA",
                                           pac_file="NA",
                                           private_key="NA",
                                           pk_password="NA",
                                           hessid="00:00:00:00:00:01",
                                           realm="localhost.localdomain",
                                           client_cert="NA",
                                           imsi="NA",
                                           milenage="NA",
                                           domain="localhost.localdomain",
                                           roaming_consortium="NA",
                                           venue_group="NA",
                                           network_type="NA",
                                           ipaddr_type_avail="NA",
                                           network_auth_type="NA",
                                           anqp_3gpp_cell_net="NA")
        station_profile.create(radio=radio, sta_names_=station_list)
        logger.info("Waiting for ports to appear")
        local_realm.wait_until_ports_appear(sta_list=station_list)

        if self.soft_roam:
            for sta_name in station_list:
                sta = sta_name.split(".")[2]  # TODO:  Use name_to_eid
                # wpa_cmd = "roam " + str(checker2)

                bgscan = {
                    "shelf": 1,
                    "resource": 1,  # TODO:  Do not hard-code resource, get it from radio eid I think.
                    "port": str(sta),
                    "type": 'NA',
                    "text": 'bgscan="simple:30:-65:300"'
                }

                logger.info(str(bgscan))
                self.local_realm.json_post("/cli-json/set_wifi_custom", bgscan)
                # time.sleep(2)

        station_profile.admin_up()
        logger.info("Waiting for ports to admin up")
        if local_realm.wait_for_ip(station_list):
            logger.info("All stations got IPs")
            # exit()
            return True
        else:
            logger.info("Stations failed to get IPs")
            return False

    # create a multicast profile
    def mcast_tx(self):
        # set 1mbps tx rate
        self.multi_cast_profile.side_b_min_bps = 1000000
        self.multi_cast_profile.create_mc_tx("mc_udp", self.upstream)

    def mcast_rx(self, sta_list):
        self.multi_cast_profile.side_a_min_bps = 0
        print("Station List :", sta_list)
        self.multi_cast_profile.create_mc_rx("mc_udp", sta_list)

    def mcast_start(self):
        self.multi_cast_profile.start_mc()

    def mcast_stop(self):
        self.multi_cast_profile.stop_mc()

    # Create layer-3 traffic on clients
    def create_layer3(self, side_a_min_rate, side_a_max_rate, side_b_min_rate, side_b_max_rate, side_a_min_pdu,
                      side_b_min_pdu, traffic_type, sta_list):
        logger.info("Station List : ", str(sta_list))
        logger.info(str(self.upstream))
        self.cx_profile.host = self.lanforge_ip
        self.cx_profile.port = self.lanforge_port
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate
        self.cx_profile.side_a_min_pdu = side_a_min_pdu,
        self.cx_profile.side_b_min_pdu = side_b_min_pdu,
        # Create layer3 end points & run traffic
        logger.info("Creating Endpoints")
        self.cx_profile.create(endp_type=traffic_type, side_a=sta_list, side_b=self.upstream, sleep_time=0)
        self.cx_profile.start_cx()

    # Get layer3 values
    def get_layer3_values(self, cx_name=None, query=None):
        url = f"/cx/{cx_name}"
        response = self.json_get(_req_url=url)
        result = response[str(cx_name)][str(query)]
        return result

    # Get cross-connect names
    def get_cx_list(self):
        layer3_result = self.local_realm.cx_list()
        layer3_names = [item["name"] for item in layer3_result.values() if "_links" in item]
        print("Layer-3 Names :", layer3_names)
        return layer3_names

    # Get Endpoint values
    def get_endp_values(self, endp="A", cx_name="niki", query="tx bytes"):
        # self.get_cx_list()
        # self.json_get("http://192.168.100.131:8080/endp/Unsetwlan000-0-B?fields=rx%20rate")
        url = f"/endp/{cx_name}-{endp}?fields={query}"
        response = self.json_get(_req_url=url)
        if (response is None) or ("endpoint" not in response):
            print("Incomplete response:")
            exit(1)
        final = response["endpoint"][query]
        return final

    # Pre-Cleanup on lanforge
    def precleanup(self):
        obj = lf_clean.lf_clean(host=self.lanforge_ip, port=self.lanforge_port, clean_cxs=True, clean_endp=True)
        obj.resource = "all"
        obj.sta_clean()
        obj.cxs_clean()
        obj.layer3_endp_clean()

    # Get client data from lf
    def station_data_query(self, station_name="wlan0", query="channel"):
        url = f"/port/{1}/{1}/{station_name}?fields={query}"
        response = self.local_realm.json_get(_req_url=url)
        if (response is None) or ("interface" not in response):
            print("Station_list: incomplete response:")
            # pprint(response)
            exit(1)
        y = response["interface"][query]
        return y

    # Start packet capture on lf
    # TODO:  Check if other monitor ports exist on this radio already.  If so, delete those
    # before adding new monitor port (or) just use the existing monitor port without creating
    # a new one. --Ben
    def start_sniffer(self, radio_channel=None, radio=None, test_name="sniff_radio", duration=60):
        self.pcap_name = test_name + str(datetime.now().strftime("%Y-%m-%d-%H-%M")).replace(':', '-') + ".pcap"
        self.pcap_obj_2 = sniff_radio.SniffRadio(lfclient_host=self.lanforge_ip, lfclient_port=self.lanforge_port,
                                                 radio=radio, channel=radio_channel, monitor_name="monitor",
                                                 channel_bw="20")
        self.pcap_obj_2.setup(0, 0, 0)
        time.sleep(5)
        self.pcap_obj_2.monitor.admin_up()
        time.sleep(5)
        self.pcap_obj_2.monitor.start_sniff(capname=self.pcap_name, duration_sec=duration)

    # Stop packet capture and get file name
    def stop_sniffer(self):
        print("In Stop Sniffer")
        directory = None
        directory_name = "pcap"
        if directory_name:
            directory = os.path.join("", str(directory_name))
        try:
            if not os.path.exists(directory):
                os.mkdir(directory)
        except Exception as x:
            print(x)

        self.pcap_obj_2.monitor.admin_down()
        self.pcap_obj_2.cleanup()
        lf_report.pull_reports(hostname=self.lanforge_ip, port=self.lanforge_ssh_port, username="lanforge",
                               password="lanforge", report_location="/home/lanforge/" + self.pcap_name,
                               report_dir="pcap")
        return self.pcap_name

    # Generate csv files at the beginning
    def generate_csv(self):
        file_name = []
        for i in range(self.num_sta):
            file = 'test_client_' + str(i) + '.csv'
            if self.multicast == "True":
                lf_csv_obj = lf_csv.lf_csv(_columns=['Iterations', 'bssid1', 'bssid2', "PASS/FAIL", "Remark"], _rows=[],
                                           _filename=file)
            else:
                lf_csv_obj = lf_csv.lf_csv(_columns=['Iterations', 'bssid1', 'bssid2', "Roam Time(ms)", "PASS/FAIL",
                                                     "Pcap file Name", "Log File", "Remark"], _rows=[], _filename=file)
            # "Packet loss",
            file_name.append(file)
            lf_csv_obj.generate_csv()
        return file_name

    # Get journal ctl logs/ kernel logs
    def journal_ctl_logs(self, file):
        jor_lst = []
        name = "kernel_log" + file + ".txt"
        jor_lst.append(name)
        try:
            ssh = paramiko.SSHClient()
            command = "journalctl --since '5 minutes ago' > kernel_log" + file + ".txt"
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.lanforge_ip, port=self.lanforge_ssh_port, username="lanforge",
                        password="lanforge", banner_timeout=600)
            stdin, stdout, stderr = ssh.exec_command(str(command))
            stdout.readlines()
            ssh.close()
            kernel_log = "/home/lanforge/kernel_log" + file + ".txt"
            lf_report.pull_reports(hostname=self.lanforge_ip, port=self.lanforge_ssh_port, username="lanforge",
                                   password="lanforge", report_location=kernel_log, report_dir=".")
        except Exception as e:
            print(e)
        return jor_lst

    # Gives wlan management status of pcap file
    def get_wlan_mgt_status(self, file_name,
                            pyshark_filter="(wlan.fc.type_subtype eq 3 && wlan.fixed.status_code == 0x0000 && wlan.tag.number == 55)"):
        query_reasso_response = self.pcap_obj.get_wlan_mgt_status_code(pcap_file=str(file_name), filter=pyshark_filter)
        print("Query", query_reasso_response)
        return query_reasso_response

    # Get attenuator serial number
    def attenuator_serial(self):
        obj = attenuator.AttenuatorSerial(lfclient_host=self.lanforge_ip, lfclient_port=self.lanforge_port)
        val = obj.show()
        return val

    # To modify the attenuators
    def attenuator_modify(self, serno, idx, val):
        atten_obj = modify.CreateAttenuator(self.lanforge_ip, self.lanforge_port, serno, idx, val)
        atten_obj.build()

    # This is where the main roaming functionality begins
    def run(self, file_n=None):
        try:
            logger.info("Setting both attenuators to zero attenuation at the beginning.")
            ser_no = self.attenuator_serial()
            logger.info("Available attenuators :" + str(ser_no[0]) + " , " + str(ser_no[1]))
            ser_1 = ser_no[0].split(".")[2]
            ser_2 = ser_no[1].split(".")[2]
            self.attenuator_modify(ser_1, "all", 0)
            self.attenuator_modify(ser_2, "all", 0)
        except Exception as e:
            logger.warning(str(e))
        finally:
            kernel_log = []
            message = None, None

            # Start Timer
            self.start_time = datetime.now().strftime(TIME_FORMAT)
            logger.debug(f"Test start time: {self.start_time}")

            # Getting two BSSID's for roam
            self.final_bssid.extend([self.c1_bssid, self.c2_bssid])
            logger.info(f"Roaming target BSSIDs: {self.final_bssid}")

            # If 'Soft Roam' is selected, initially set the attenuator to zero.
            if self.soft_roam:
                logger.info("Setting both attenuators to zero attenuation at the beginning for 'soft roam'")
                ser_no = self.attenuator_serial()
                logger.info("Available attenuators :" + str(ser_no[0]) + " , " + str(ser_no[1]))
                ser_1 = ser_no[0].split(".")[2]
                ser_2 = ser_no[1].split(".")[2]
                self.attenuator_modify(ser_1, "all", 0)
                self.attenuator_modify(ser_2, "all", 0)

            # Start sniffer & Create clients with respect to bands
            logger.info("Begin sniffing to establish the initial connection.")
            self.start_sniffer(radio_channel=self.channel, radio=self.sniff_radio,
                               test_name="roam_" + str(self.sta_type) + "_" + str(self.option) + "start" + "_",
                               duration=3600)
            if self.band == "twog":
                self.local_realm.reset_port(self.twog_radios)
                self.create_n_clients(sta_prefix="wlan1", num_sta=self.num_sta, dut_ssid=self.ssid_name,
                                      dut_security=self.security, dut_passwd=self.security_key, radio=self.twog_radios)
            if self.band == "fiveg":
                self.local_realm.reset_port(self.fiveg_radios)
                self.create_n_clients(sta_prefix="wlan", num_sta=self.num_sta, dut_ssid=self.ssid_name,
                                      dut_security=self.security, dut_passwd=self.security_key, radio=self.fiveg_radios)
            if self.band == "sixg":
                self.local_realm.reset_port(self.sixg_radios)
                self.create_n_clients(sta_prefix="wlan", num_sta=self.num_sta, dut_ssid=self.ssid_name,
                                      dut_security=self.security, dut_passwd=self.security_key, radio=self.sixg_radios)

            # Check if all stations have ip or not
            sta_list = self.get_station_list()
            logger.info("Checking for IP and station list :" + str(sta_list))
            if sta_list == "no response":
                logger.info("No response from station")
            else:  # if all stations got ip check mac address for stations
                val = self.wait_for_ip(sta_list)
                mac_list = []
                for sta_name in sta_list:
                    sta = sta_name.split(".")[2]  # use name_to_eid
                    mac = self.station_data_query(station_name=str(sta), query="mac")
                    mac_list.append(mac)
                logger.info("List of MAC addresses for all stations :" + str(mac_list))
                self.mac_data = mac_list
                logger.info("Stop Sniffer")
                file_name_ = self.stop_sniffer()
                file_name = "./pcap/" + str(file_name_)
                logger.info("pcap file name : " + str(file_name))

                if val:  # if all station got an ip, then check all station are connected to single AP
                    logger.info("All stations got ip")
                    logger.info("Check if all stations are connected single ap")
                    # get BSSID'S of all stations
                    logger.info("Get BSSID's of all stations")
                    check = []
                    for sta_name in sta_list:
                        sta = sta_name.split(".")[2]
                        bssid = self.station_data_query(station_name=str(sta), query="ap")
                        logger.info(str(bssid))
                        check.append(bssid)
                    logger.info(str(check))

                    # Check if all the stations in the BSSID list have the same BSSID.
                    logger.info("Verifying whether all BSSID's are identical or not.")
                    result = all(element == check[0] for element in check)

                    #  if all BSSID's are identical / same, run layer3 traffic b/w station to upstream
                    if result:
                        if self.multicast == "True":
                            print("multicast is true")
                            self.mcast_tx()
                            self.mcast_rx(sta_list=sta_list)
                            self.mcast_start()
                        else:
                            self.create_layer3(side_a_min_rate=1000000, side_a_max_rate=0, side_b_min_rate=1000000,
                                               side_b_max_rate=0, sta_list=sta_list, traffic_type=self.traffic_type,
                                               side_a_min_pdu=1250, side_b_min_pdu=1250)
                    else:
                        #  if BSSID's are not identical / same, try to move all clients to one ap
                        logger.info("Attempt to ensure that all clients are connected to the same AP before "
                                    "initiating a roaming process.")
                        count1 = check.count(self.c1_bssid.upper())
                        count2 = check.count(self.c2_bssid.upper())
                        checker, new_sta_list, checker2 = None, [], None
                        if count1 > count2:
                            logger.info("Station connected mostly to ap1")
                            checker = self.c2_bssid.upper()
                            checker2 = self.c1_bssid.upper()
                        else:
                            checker = self.c1_bssid.upper()
                            checker2 = self.c2_bssid.upper()
                        index_count = [i for i, x in enumerate(check) if x == checker]
                        logger.info(str(index_count))
                        for i in index_count:
                            new_sta_list.append(sta_list[i])
                        logger.info("new_sta_list " + str(new_sta_list))

                        for sta_name in new_sta_list:
                            eid = self.name_to_eid(sta_name)
                            # sta = sta_name.split(".")[2]  # TODO: use name-to-eid
                            sta = eid[2]
                            logger.info(sta)
                            wpa_cmd = "roam " + str(checker2)
                            wifi_cli_cmd_data1 = {
                                "shelf": eid[0],
                                "resource": eid[1],  # TODO: do not hard-code
                                "port": str(sta),
                                "wpa_cli_cmd": 'scan trigger freq 5180 5300'
                            }
                            wifi_cli_cmd_data = {
                                "shelf": eid[0],
                                "resource": eid[1],
                                "port": str(sta),
                                "wpa_cli_cmd": wpa_cmd
                            }
                            logger.info(str(wifi_cli_cmd_data))
                            self.local_realm.json_post("/cli-json/wifi_cli_cmd", wifi_cli_cmd_data1)
                            # TODO:  LANforge sta on same radio will share scan results, so you only need to scan on one STA per
                            # radio, and then sleep should be 5 seconds, then roam every station that needs to roam.
                            # You do not need this sleep and scan for each STA.
                            self.local_realm.json_post("/cli-json/wifi_cli_cmd", wifi_cli_cmd_data)
                        if self.multicast == "True":
                            print("multicast is true")
                            self.mcast_tx()
                            self.mcast_rx(sta_list=sta_list)
                            self.mcast_start()
                        else:
                            self.create_layer3(side_a_min_rate=1000000, side_a_max_rate=0, side_b_min_rate=1000000,
                                               side_b_max_rate=0, sta_list=sta_list, traffic_type=self.traffic_type,
                                               side_a_min_pdu=1250, side_b_min_pdu=1250)
                    timeout, variable, iterable_var = None, None, None
                    if self.duration_based is True:
                        timeout = time.time() + 60 * float(self.duration)
                        # iteration_dur = 50000000
                        iterable_var = 50000000
                        variable = -1
                    if self.iteration_based:
                        variable = self.iteration
                        iterable_var = self.iteration
                    # post_bssid = None

                    while variable:  # The iteration loop for roaming begins at this point.
                        if self.multicast == "True":
                            if variable == 1:
                                print("ignore")
                            else:
                                print("wait for 5 mins for next roam process")
                                time.sleep(120)
                        logger.info("Value of the Variable :" + str(variable))
                        iterations, number, ser_1, ser_2 = self.iteration, None, None, None
                        if variable != -1:
                            iterations = iterable_var - variable
                            variable = variable - 1
                        if variable == -1:
                            # need to write duration iteration logic
                            # iterations = iterable_var - iteration_dur
                            if self.duration is not None:
                                if time.time() > timeout:
                                    break
                        #  Get the serial number of attenuators from lf
                        ser_no = self.attenuator_serial()
                        logger.info(str(ser_no[0]))
                        ser_1 = ser_no[0].split(".")[2]
                        ser_2 = ser_no[1].split(".")[2]
                        if self.soft_roam:
                            if iterations % 2 == 0:
                                logger.info("even set c1 to lowest and c2 to highest attenuation ")
                                number = "even"
                                logger.info("number " + str(number))

                                # set attenuation to zero in first attenuator and high in second attenuator
                                self.attenuator_modify(ser_1, "all", 700)
                                self.attenuator_modify(ser_2, "all", 0)
                            else:
                                logger.info("odd,  c1 is already at  highest and c2 is at  lowest")
                                self.attenuator_modify(ser_1, "all", 0)
                                self.attenuator_modify(ser_2, "all", 700)  # 700 == 300/400 bgscan 15:-70:300
                                number = "odd"
                                logger.info("number " + str(number))
                        try:
                            # Define row list per iteration
                            row_list = []
                            sta_list = self.get_station_list()
                            logger.info("Station list :" + str(sta_list))
                            if sta_list == "no response":
                                logger.info("No response")
                                pass
                            else:
                                station = self.wait_for_ip(sta_list)
                                if self.debug:
                                    logger.info("Start debug")
                                    self.start_debug_(mac_list=mac_list)
                                if station:
                                    logger.info("All stations got ip")
                                    # Get bssid's of all stations currently connected
                                    bssid_list = []
                                    for sta_name in sta_list:
                                        sta = sta_name.split(".")[2]
                                        bssid = self.station_data_query(station_name=str(sta), query="ap")
                                        bssid_list.append(bssid)
                                    print("BSSID of the current connected stations : ", bssid_list)
                                    logger.info(str(bssid_list))
                                    pass_fail_list = []
                                    pcap_file_list = []
                                    roam_time1 = []
                                    # packet_loss_lst = []
                                    remark = []
                                    log_file = []

                                    # Check if all element of bssid list has same bssid's
                                    result = all(element == bssid_list[0] for element in bssid_list)

                                    if not result:
                                        #  Attempt to connect the client to the same AP for each iteration
                                        logger.info("Giving a try to connect")
                                        logger.info("Move all clients to one AP")
                                        count3 = bssid_list.count(self.c1_bssid.upper())
                                        count4 = bssid_list.count(self.c2_bssid.upper())
                                        logger.info("Count3 " + str(count3))
                                        logger.info("Count4 " + str(count4))
                                        checker, new_sta_list, checker2 = None, [], None
                                        if count3 > count4:
                                            logger.info("Station connected mostly to AP-1")
                                            checker = self.c2_bssid.upper()
                                            checker2 = self.c1_bssid.upper()
                                        else:
                                            checker = self.c1_bssid.upper()
                                            checker2 = self.c2_bssid.upper()
                                        index_count = [i for i, x in enumerate(bssid_list) if x == checker]
                                        logger.info(str(index_count))
                                        for i in index_count:
                                            new_sta_list.append(sta_list[i])
                                        logger.info("new_sta_list " + str(new_sta_list))

                                        for sta_name in new_sta_list:
                                            # sta = sta_name.split(".")[2]
                                            eid = self.name_to_eid(sta_name)
                                            sta = eid[2]
                                            logger.info(str(sta))
                                            wpa_cmd = "roam " + str(checker2)

                                            wifi_cli_cmd_data1 = {
                                                "shelf": eid[0],
                                                "resource": eid[1],
                                                "port": str(sta),
                                                "wpa_cli_cmd": 'scan trigger freq 5180 5300'
                                            }
                                            wifi_cli_cmd_data = {
                                                "shelf": eid[0],
                                                "resource": eid[1],
                                                "port": str(sta),
                                                "wpa_cli_cmd": wpa_cmd
                                            }
                                            logger.info(str(wifi_cli_cmd_data))
                                            self.local_realm.json_post("/cli-json/wifi_cli_cmd", wifi_cli_cmd_data1)
                                            self.local_realm.json_post("/cli-json/wifi_cli_cmd", wifi_cli_cmd_data)

                                    # check bssid before
                                    before_bssid = []
                                    for sta_name in sta_list:
                                        sta = sta_name.split(".")[2]
                                        before_bss = self.station_data_query(station_name=str(sta), query="ap")
                                        logger.info(str(before_bss))
                                        before_bssid.append(before_bss)
                                    logger.info("BSSID of the current connected stations : " + str(before_bssid))

                                    if before_bssid[0] == str(self.c1_bssid.upper()):
                                        post_bssid = self.c2_bssid.upper()
                                    else:
                                        post_bssid = self.c1_bssid.upper()
                                    logger.info(
                                        "After roaming, the stations will connect to " + str(post_bssid) + "the BSSID")
                                    result1 = all(element == before_bssid[0] for element in before_bssid)

                                    if result1:
                                        logger.info("All stations connected to same AP")
                                        for i in before_bssid:
                                            local_row_list = [str(iterations + 1), i]
                                            logger.info(str(local_row_list))
                                            row_list.append(local_row_list)
                                        logger.info(str(row_list))
                                        #  if all bssid are equal then do check to which ap it is connected
                                        formated_bssid = before_bssid[0].lower()
                                        station_before = ""
                                        if formated_bssid == self.c1_bssid:
                                            logger.info("Station connected to chamber1 AP")
                                            station_before = formated_bssid
                                        elif formated_bssid == self.c2_bssid:
                                            logger.info("Station connected to chamber 2 AP")
                                            station_before = formated_bssid
                                        logger.info(str(station_before))
                                        # After checking all conditions start roam and start snifffer
                                        logger.info("Starting sniffer")
                                        self.start_sniffer(radio_channel=self.channel, radio=self.sniff_radio,
                                                           test_name="roam_" + str(self.sta_type) + "_" + str(
                                                               self.option) + "_iteration_" + str(
                                                               iterations) + "_", duration=3600)
                                        if self.soft_roam:
                                            ser_num = None
                                            ser_num2 = None
                                            if number == "even":
                                                ser_num = ser_1
                                                ser_num2 = ser_2
                                                logger.info("even " + str(ser_num))
                                            elif number == "odd":
                                                ser_num = ser_2
                                                ser_num2 = ser_1
                                                logger.info("odd " + str(ser_num))
                                            # logic to decrease c2 attenuation till 10 db using 1dbm steps
                                            status = None
                                            logger.info("checking attenuation")
                                            logger.info("ser num " + str(ser_num))
                                            for atten_val2 in range(700, -10, -10):
                                                self.attenuator_modify(int(ser_num), "all", atten_val2)
                                                # TODO:  You are changing in 1db increments.  So, sleep for only 4 seconds
                                                # should be enough.
                                                logger.info("wait for 4  secs")
                                                #  query bssid's of all stations
                                                bssid_check = []
                                                for sta_name in sta_list:
                                                    sta = sta_name.split(".")[2]
                                                    bssid = self.station_data_query(station_name=str(sta), query="ap")
                                                    # if bssid == "NA":
                                                    #     time.sleep(10)
                                                    bssid_check.append(bssid)
                                                logger.info(str(bssid_check))

                                                # check if all are equal
                                                resulta = all(element == bssid_check[0] for element in bssid_check)
                                                if resulta:
                                                    station_after = bssid_check[0].lower()
                                                    if station_after == "N/A" or station_after == "na":
                                                        status = "station did not roamed"
                                                        logger.info("station did not roamed")
                                                        continue
                                                    if station_after == station_before:
                                                        status = "station did not roamed"
                                                        logger.info("station did not roamed")
                                                        continue
                                                    elif station_after != station_before:
                                                        logger.info("client performed roam")
                                                        break

                                            if status == "station did not roamed":
                                                # set c1 to high
                                                for atten_val1 in (range(0, 700, 10)):
                                                    logger.info(str(atten_val1))
                                                    self.attenuator_modify(int(ser_num2), "all", atten_val1)
                                                    # TODO:  You are changing in 1db increments.  So, sleep for only 4 seconds
                                                    # should be enough.
                                                    # TODO:  Add attenuation step to logs to make it more obvious what script is doing.
                                                    logger.info("wait for 4  secs")
                                                    bssid_check2 = []
                                                    for sta_name in sta_list:
                                                        sta = sta_name.split(".")[2]
                                                        bssid = self.station_data_query(station_name=str(sta),
                                                                                        query="ap")
                                                        # if bssid == "NA":
                                                        #     time.sleep(10)
                                                        bssid_check2.append(bssid)
                                                    logger.info(str(bssid_check2))
                                                    # check if all are equal
                                                    result = all(element == bssid_check2[0] for element in bssid_check2)
                                                    if result:
                                                        station_after = bssid_check2[0].lower()
                                                        if station_after == "N/A" or station_after == "na":
                                                            # status = "station did not roamed"
                                                            logger.info("station did not roamed")
                                                            continue
                                                        if station_after == station_before:
                                                            # status = "station did not roamed"
                                                            logger.info("station did not roamed")
                                                            continue
                                                        else:
                                                            logger.info('station roamed')
                                                            break
                                        else:
                                            if station_before == self.final_bssid[0]:
                                                logger.info(
                                                    "Connected stations bssid is same to bssid list first element")
                                                for sta_name in sta_list:
                                                    sta = sta_name.split(".")[2]
                                                    logger.info(str(sta))
                                                    wpa_cmd = ""
                                                    if self.option == "ota":
                                                        wpa_cmd = "roam " + str(self.final_bssid[1])
                                                    if self.option == "otds":
                                                        wpa_cmd = "ft_ds " + str(self.final_bssid[1])
                                                    # wpa_cmd = "roam " + str(self.final_bssid[1])
                                                    wifi_cli_cmd_data1 = {
                                                        "shelf": 1,
                                                        "resource": 1,
                                                        "port": str(sta),
                                                        "wpa_cli_cmd": 'scan trigger freq 5180 5300'
                                                    }
                                                    wifi_cli_cmd_data = {
                                                        "shelf": 1,
                                                        "resource": 1,
                                                        "port": str(sta),
                                                        "wpa_cli_cmd": wpa_cmd
                                                    }
                                                    logger.info("Roam Command : " + str(wifi_cli_cmd_data))
                                                    self.local_realm.json_post("/cli-json/wifi_cli_cmd",
                                                                               wifi_cli_cmd_data1)
                                                    # TODO:  See note in similar code above about only needing to scan once per radio
                                                    self.local_realm.json_post("/cli-json/wifi_cli_cmd",
                                                                               wifi_cli_cmd_data)
                                            else:
                                                logger.info(
                                                    "Connected stations bssid is same to bssid list second  element")
                                                for sta_name in sta_list:
                                                    sta = sta_name.split(".")[2]
                                                    wifi_cmd = ""
                                                    if self.option == "ota":
                                                        wifi_cmd = "roam " + str(self.final_bssid[0])
                                                    if self.option == "otds":
                                                        wifi_cmd = "ft_ds " + str(self.final_bssid[0])
                                                    logger.info(str(sta))
                                                    wifi_cli_cmd_data1 = {
                                                        "shelf": 1,
                                                        "resource": 1,
                                                        "port": str(sta),
                                                        "wpa_cli_cmd": 'scan trigger freq 5180 5300'
                                                    }
                                                    wifi_cli_cmd_data = {
                                                        "shelf": 1,
                                                        "resource": 1,
                                                        "port": str(sta),
                                                        "wpa_cli_cmd": wifi_cmd
                                                    }
                                                    logger.info("Roam Command : " + str(wifi_cli_cmd_data))
                                                    self.local_realm.json_post("/cli-json/wifi_cli_cmd",
                                                                               wifi_cli_cmd_data1)
                                                    # TODO:  See note in similar code above about only needing to scan once per radio
                                                    self.local_realm.json_post("/cli-json/wifi_cli_cmd",
                                                                               wifi_cli_cmd_data)
                                        # Kernel logs
                                        kernel = self.journal_ctl_logs(file=str(iterations))
                                        print("Name of the Kernel logs file :", kernel)
                                        for i in kernel:
                                            kernel_log.append(i)
                                        # Stop sniff & Attach data
                                        logger.info("Stop sniffer")
                                        file_name_ = self.stop_sniffer()
                                        file_name = "./pcap/" + str(file_name_)
                                        logger.info("pcap file name " + str(file_name))
                                        if self.debug:
                                            logger.info("Stop debugger")
                                            self.stop_debug_(mac_list=mac_list)
                                        else:
                                            logger.info("Debug is  disabled")
                                        self.wait_for_ip(sta_list)
                                        bssid_list_1 = []
                                        for sta_name in sta_list:
                                            sta = sta_name.split(".")[2]
                                            bssid = self.station_data_query(station_name=str(sta), query="ap")
                                            bssid_list_1.append(bssid)
                                        logger.info("The stations are romed to another AP " + str(bssid_list_1))
                                        for i, x in zip(row_list, bssid_list_1):
                                            i.append(x)
                                        logger.info("Row list, after roam :" + str(row_list))
                                        trace = self.get_file_name(client=self.num_sta)
                                        print("Trace file :", trace)
                                        log_file.append(trace)
                                        print("Log file :", log_file)

                                        # Check if all are equal
                                        all(element == bssid_list_1[0] for element in bssid_list_1)
                                        res = ""
                                        station_before_ = before_bssid
                                        logger.info("The BSSID of the station before roamed : " + str(station_before_))
                                        # For each mac address query data from pcap
                                        for i, x in zip(mac_list, range(len(station_before_))):
                                            logger.info("MAC address :" + str(i))
                                            logger.info(str(bssid_list_1))
                                            query_action_frame_time, auth_time = None, None
                                            station_after = bssid_list_1[x]
                                            logger.info(
                                                "The connected BSSID for stations, after rome : " + str(station_after))
                                            if station_after == station_before_[x] or station_after == "na":
                                                logger.info("Station did not roamed")
                                                res = "FAIL"
                                            elif station_after != station_before_[x]:
                                                logger.info("Client has performed a roaming operation.")
                                                res = "PASS"
                                            if res == "FAIL":
                                                res = "FAIL"
                                            if self.multicast == "True":
                                                print("multicast function")
                                                if res == "PASS":
                                                    print("roam success")
                                                    print("check for multicast traffic resumed or not")
                                                    endp_list = self.json_get(
                                                        "endp?fields=name,eid,rx rate (last)",
                                                        debug_=False)
                                                    local_list, local_list1, final_list = [], [], []
                                                    if "endpoint" in endp_list:
                                                        for i in range(1, len(endp_list["endpoint"])):
                                                            local_list.append(endp_list['endpoint'][i])
                                                        new_lst = []
                                                        for i in range(len(local_list)):
                                                            local_list1 = list(local_list[i].keys())
                                                            new_lst.append(local_list1[0])
                                                        for i in range(len(new_lst)):
                                                            final_list.append(
                                                                endp_list['endpoint'][i + 1][new_lst[i]][
                                                                    'rx rate (last)'])
                                                        if 0 in final_list:
                                                            print("try to start multicast few times")
                                                            print("start multicast once again")
                                                            self.mcast_start()
                                                            time.sleep(60)
                                                            self.mcast_start()
                                                            print("check for multicast resumed or not  ")
                                                            endp_list = self.json_get(
                                                                "endp?fields=name,eid,rx rate (last)",
                                                                debug_=False)
                                                            local_list, local_list1, final_list = [], [], []
                                                            if "endpoint" in endp_list:

                                                                for i in range(1, len(endp_list["endpoint"])):
                                                                    local_list.append(endp_list['endpoint'][i])
                                                                new_lst = []
                                                                for i in range(len(local_list)):
                                                                    local_list1 = list(local_list[i].keys())
                                                                    new_lst.append(local_list1[0])
                                                                for i in range(len(new_lst)):
                                                                    final_list.append(
                                                                        endp_list['endpoint'][i + 1][new_lst[i]][
                                                                            'rx rate (last)'])
                                                                if 0 in final_list:
                                                                    print("multicast did not resumed after few trials")
                                                                    pass_fail_list.append("FAIL")
                                                                    remark.append(
                                                                        "bssid switched but multicast did not resumed after few trials")
                                                                else:
                                                                    pass_fail_list.append("PASS")
                                                                    remark.append(
                                                                        "bssid switched and multicast resumed after few trials ")
                                                        else:
                                                            pass_fail_list.append("PASS")
                                                            remark.append("multicast resumed after roam")
                                                else:
                                                    pass_fail_list.append("FAIL")
                                                    remark.append("bssid does not switched")
                                            else:
                                                if res == "PASS":
                                                    if self.sta_type == "normal":
                                                        query_reasso_response = self.get_wlan_mgt_status(
                                                            file_name=file_name,
                                                            pyshark_filter="wlan.da eq %s and wlan.fc.type_subtype eq 3" % (
                                                                str(i)))
                                                    else:
                                                        query_reasso_response = self.get_wlan_mgt_status(
                                                            file_name=file_name,
                                                            pyshark_filter="(wlan.fc.type_subtype eq 3 && wlan.fixed.status_code == 0x0000 && wlan.tag.number == 55) && (wlan.da == %s)" % (
                                                                str(i)))
                                                    logger.info(str(query_reasso_response))
                                                    if len(query_reasso_response) != 0 and query_reasso_response != "empty":
                                                        if query_reasso_response == "Successful":
                                                            logger.info("Re-association status is successful")
                                                            if self.sta_type == "normal":
                                                                reasso_t = self.pcap_obj.read_time(
                                                                    pcap_file=str(file_name),
                                                                    filter="wlan.da eq %s and wlan.fc.type_subtype eq 3" % (
                                                                        str(i)))
                                                            else:
                                                                reasso_t = self.pcap_obj.read_time(
                                                                    pcap_file=str(file_name),
                                                                    filter="(wlan.fc.type_subtype eq 3 && wlan.fixed.status_code == 0x0000 && wlan.tag.number == 55) && (wlan.da == %s)" % (
                                                                        str(i)))
                                                            logger.info("Re-association time is " + str(reasso_t))
                                                            if self.option == "otds":
                                                                logger.info("Checking for Action Frame")

                                                                # Action frame check
                                                                query_action_frame = self.pcap_obj.check_frame_present(
                                                                    pcap_file=str(file_name),
                                                                    filter="(wlan.fixed.category_code == 6)  && (wlan.sa == %s)" % (
                                                                        str(i)))
                                                                print("Action Frame", query_action_frame)
                                                                if len(query_action_frame) != 0 and query_action_frame != "empty":
                                                                    logger.info("Action frame is present")
                                                                    query_action_frame_time = self.pcap_obj.read_time(
                                                                        pcap_file=str(file_name),
                                                                        filter="(wlan.fixed.category_code == 6)  && (wlan.sa == %s)" % (
                                                                            str(i)))
                                                                    logger.info(
                                                                        "Action frame time is " + str(reasso_t))
                                                                else:
                                                                    roam_time1.append("No Action frame")
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("No Action Frame")
                                                                    logger.info("Row list " + str(row_list))
                                                            else:
                                                                logger.info("Checking for Authentication Frame")
                                                                if self.sta_type == "normal":
                                                                    query_auth_response = self.pcap_obj.get_wlan_mgt_status_code(
                                                                        pcap_file=str(file_name),
                                                                        filter="(wlan.fixed.auth.alg == 0 &&  wlan.sa == %s)" % (
                                                                            str(i)))
                                                                else:
                                                                    query_auth_response = self.pcap_obj.get_wlan_mgt_status_code(
                                                                        pcap_file=str(file_name),
                                                                        filter="(wlan.fixed.auth.alg == 2 && wlan.fixed.status_code == 0x0000 && wlan.fixed.auth_seq == 0x0001) && (wlan.sa == %s)" % (
                                                                            str(i)))
                                                                print("Authentication Frames response is",
                                                                      query_auth_response)
                                                                if len(query_auth_response) != 0 and query_auth_response != "empty":
                                                                    if query_auth_response == "Successful":
                                                                        logger.info(
                                                                            "Authentication Request Frame is present")
                                                                        if self.sta_type == "normal":
                                                                            auth_time = self.pcap_obj.read_time(
                                                                                pcap_file=str(file_name),
                                                                                filter="(wlan.fixed.auth.alg == 0 &&  wlan.sa == %s)" % (
                                                                                    str(i)))
                                                                        else:
                                                                            auth_time = self.pcap_obj.read_time(
                                                                                pcap_file=str(file_name),
                                                                                filter="(wlan.fixed.auth.alg == 2 && wlan.fixed.status_code == 0x0000 && wlan.fixed.auth_seq == 0x0001)  && (wlan.sa == %s)" % (  # noqa: E501
                                                                                    str(i)))
                                                                        logger.info(
                                                                            "Authentication Request Frame time is" + str(
                                                                                auth_time))
                                                                    else:
                                                                        roam_time1.append('Auth Fail')
                                                                        pass_fail_list.append("FAIL")
                                                                        pcap_file_list.append(str(file_name))
                                                                        remark.append(" auth failure")
                                                                else:
                                                                    roam_time1.append("No Auth frame")
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("No Auth frame")
                                                                    logger.info("row list " + str(row_list))
                                                            # roam_time = None
                                                            if self.option == "otds":
                                                                roam_time = reasso_t - query_action_frame_time
                                                            else:
                                                                roam_time = reasso_t - auth_time
                                                            logger.info("Roam Time (ms)" + str(roam_time))
                                                            roam_time1.append(roam_time)
                                                            if self.option == "ota":
                                                                if roam_time < 50:
                                                                    pass_fail_list.append("PASS")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("Passed all criteria")
                                                                else:
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("Roam time is greater then 50 ms")
                                                            else:
                                                                pass_fail_list.append("PASS")
                                                                pcap_file_list.append(str(file_name))
                                                                remark.append("Passed all criteria")
                                                        else:
                                                            roam_time1.append('Reassociation Fail')
                                                            pass_fail_list.append("FAIL")
                                                            pcap_file_list.append(str(file_name))
                                                            remark.append("Reassociation failure")
                                                            logger.info(
                                                                "pcap_file name for fail instance of iteration value ")
                                                    else:
                                                        roam_time1.append("No Reassociation")
                                                        pass_fail_list.append("FAIL")
                                                        pcap_file_list.append(str(file_name))
                                                        remark.append("No Reasso response")
                                                        logger.info("row list " + str(row_list))
                                                else:
                                                    query_reasso_response = self.get_wlan_mgt_status(
                                                        file_name=file_name,
                                                        pyshark_filter="(wlan.fc.type_subtype eq 3 && wlan.fixed.status_code == 0x0000 && wlan.tag.number == 55) && (wlan.da == %s)" % (
                                                            str(i)))
                                                    print("Query_reasso_response:", query_reasso_response)
                                                    logger.info(str(query_reasso_response))
                                                    if len(query_reasso_response) != 0 and query_reasso_response != 'empty':
                                                        if query_reasso_response == "Successful":
                                                            logger.info("Re-Association status is successful")
                                                            reasso_t = self.pcap_obj.read_time(pcap_file=str(file_name),
                                                                                               filter="(wlan.fc.type_subtype eq 3 && wlan.fixed.status_code == 0x0000 && wlan.tag.number == 55) && (wlan.da == %s)" % (  # noqa: E501
                                                                                                   str(i)))
                                                            logger.info("Re-Association time is " + str(reasso_t))
                                                            if self.option == "otds":
                                                                logger.info("Check for Action Frame")

                                                                # action frame check
                                                                query_action_frame = self.pcap_obj.check_frame_present(
                                                                    pcap_file=str(file_name),
                                                                    filter="(wlan.fixed.category_code == 6)  && (wlan.sa == %s)" % (
                                                                        str(i)))
                                                                if len(query_action_frame) != 0 and query_action_frame != "empty":
                                                                    logger.info("Action Frame is present")
                                                                    query_action_frame_time = self.pcap_obj.read_time(
                                                                        pcap_file=str(file_name),
                                                                        filter="(wlan.fixed.category_code == 6)  && (wlan.sa == %s)" % (
                                                                            str(i)))
                                                                    logger.info(
                                                                        "Action Frame) time is " + str(reasso_t))
                                                                else:
                                                                    roam_time1.append("No Action frame")
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("bssid miNo Action Frame")
                                                                    logger.info("Row list :" + str(row_list))
                                                            else:
                                                                logger.info("Check for Authentication Frame")
                                                                query_auth_response = self.pcap_obj.get_wlan_mgt_status_code(
                                                                    pcap_file=str(file_name),
                                                                    filter="(wlan.fixed.auth.alg == 2 && wlan.fixed.status_code == 0x0000 && wlan.fixed.auth_seq == 0x0001) && (wlan.sa == %s)" % (
                                                                        str(i)))
                                                                if len(query_auth_response) != 0 and query_auth_response != "empty":
                                                                    if query_auth_response == "Successful":
                                                                        logger.info(
                                                                            "Authentication Request is present")
                                                                        auth_time = self.pcap_obj.read_time(
                                                                            pcap_file=str(file_name),
                                                                            filter="(wlan.fixed.auth.alg == 2 && wlan.fixed.status_code == 0x0000 && wlan.fixed.auth_seq == 0x0001)  && (wlan.sa == %s)" % (  # noqa: E501
                                                                                str(i)))
                                                                        logger.info(
                                                                            "Authentication time is " + str(auth_time))
                                                                    else:
                                                                        roam_time1.append('Auth Fail')
                                                                        pass_fail_list.append("FAIL")
                                                                        pcap_file_list.append(str(file_name))
                                                                        remark.append("bssid mismatch  auth failure")
                                                                else:
                                                                    roam_time1.append("No Auth frame")
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append("bssid mismatched No Auth frame")
                                                                    logger.info("Row list :" + str(row_list))
                                                            # roam_time = None
                                                            if self.option == "otds":
                                                                roam_time = reasso_t - query_action_frame_time
                                                            else:
                                                                roam_time = reasso_t - auth_time
                                                            logger.info("Roam time (ms) " + str(roam_time))
                                                            roam_time1.append(roam_time)
                                                            if self.option == "ota":
                                                                if roam_time < 50:
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append(
                                                                        "(BSSID mismatched)Client disconnected after roaming")
                                                                else:
                                                                    pass_fail_list.append("FAIL")
                                                                    pcap_file_list.append(str(file_name))
                                                                    remark.append(
                                                                        "(BSSID mismatched)Roam time is greater then 50 ms,")
                                                            else:
                                                                pass_fail_list.append("FAIL")
                                                                pcap_file_list.append(str(file_name))
                                                                remark.append("BSSID mismatched")
                                                        else:
                                                            roam_time1.append('Reassociation Fail')
                                                            pass_fail_list.append("FAIL")
                                                            pcap_file_list.append(str(file_name))
                                                            remark.append("BSSID mismatched  Reassociation failure")
                                                    else:
                                                        roam_time1.append("No Reassociation")
                                                        pass_fail_list.append("FAIL")
                                                        pcap_file_list.append(str(file_name))
                                                        remark.append("BSSID mismatched , No Reasso response")
                                                        logger.info("row list " + str(row_list))
                                        if self.multicast == "True":
                                            for i, x in zip(row_list, pass_fail_list):
                                                i.append(x)
                                            for i, x in zip(row_list, remark):
                                                i.append(x)
                                            for i, x in zip(file_n, row_list):
                                                self.lf_csv_obj.open_csv_append(fields=x, name=i)

                                        else:
                                            for i, x in zip(row_list, roam_time1):
                                                i.append(x)
                                            logger.info("Row list : " + str(row_list))
                                            # for i, x in zip(row_list, packet_loss_lst):
                                            #     i.append(x)
                                            for i, x in zip(row_list, pass_fail_list):
                                                i.append(x)
                                            logger.info("Row list : " + str(row_list))
                                            for i, x in zip(row_list, pcap_file_list):
                                                i.append(x)
                                            logger.info("Log file : " + str(log_file))
                                            my_unnested_list = list(chain(*log_file))
                                            logger.info(str(my_unnested_list))
                                            for i, x in zip(row_list, my_unnested_list):
                                                i.append(x)
                                            for i, x in zip(row_list, remark):
                                                i.append(x)
                                            logger.info("row list " + str(row_list))
                                            for i, x in zip(file_n, row_list):
                                                self.lf_csv_obj.open_csv_append(fields=x, name=i)
                                    else:
                                        message = "all stations are not connected to same ap for iteration " + str(
                                            iterations)
                                        logger.info("All stations are not connected to same ap")
                                        logger.info("Starting Sniffer")
                                        self.start_sniffer(radio_channel=self.channel, radio=self.sniff_radio,
                                                           test_name="roam_" + str(self.sta_type) + "_" + str(
                                                               self.option) + "_iteration_" + str(
                                                               iterations) + "_", duration=3600)
                                        logger.info("Stop Sniffer")
                                        self.stop_sniffer()
                                        kernel = self.journal_ctl_logs(file=str(iterations))
                                        for i in kernel:
                                            kernel_log.append(i)
                                        bssid_list2 = []
                                        for sta_name in sta_list:
                                            # local_row_list = [0, "68"]
                                            local_row_list = [str(iterations)]
                                            sta = sta_name.split(".")[2]
                                            before_bssid_ = self.station_data_query(station_name=str(sta), query="ap")
                                            logger.info(str(before_bssid_))
                                            bssid_list2.append(before_bssid_)
                                            local_row_list.append(before_bssid_)
                                            logger.info(str(local_row_list))
                                            row_list.append(local_row_list)
                                        logger.info(str(row_list))
                                        for i, x in zip(row_list, bssid_list2):
                                            i.append(x)
                                        logger.info("Row list : " + str(row_list))
                                        if self.multicast == "True":
                                            for a in row_list:
                                                a.append("FAIL")
                                        else:
                                            for i in row_list:
                                                i.append("No Roam Time")
                                            logger.info("Row list : " + str(row_list))
                                            for a in row_list:
                                                a.append("FAIL")
                                            logger.info("Row list : " + str(row_list))
                                            # pcap
                                            for i in row_list:
                                                i.append("N/A")
                                            logger.info("Row list : " + str(row_list))
                                            if self.debug:
                                                logger.info("Stop Debugger")
                                                self.stop_debug_(mac_list=mac_list)
                                            else:
                                                logger.info("Debug is  disabled")

                                            trace = self.get_file_name(client=self.num_sta)
                                            log_file.append(trace)
                                            logger.info("Log file : " + str(log_file))
                                            my_unnested_list = list(chain(*log_file))
                                            logger.info(str(my_unnested_list))
                                            for i, x in zip(row_list, my_unnested_list):
                                                i.append(x)
                                            logger.info("Row list : " + str(row_list))
                                        for i in row_list:
                                            i.append("No roam performed all stations are not connected to same ap")
                                        logger.info("Row list : " + str(row_list))
                                        for i, x in zip(file_n, row_list):
                                            self.lf_csv_obj.open_csv_append(fields=x, name=i)
                                else:
                                    message = "station's failed to get ip  after the test start"
                                    logger.info("Station's failed to get ip after test starts")
                                if self.duration_based is True:
                                    if time.time() > timeout:
                                        break
                        except Exception as e:
                            logger.warning(str(e))
                            pass
                    else:
                        message = "station's failed to get ip  at the beginning"
                        logger.info("Station's failed to get associate at the beginning")
                else:
                    logger.info("Stations failed to get ip")

            self.end_time = datetime.now().strftime(TIME_FORMAT)
            self.test_duration = datetime.strptime(self.end_time, TIME_FORMAT) - datetime.strptime(self.start_time, TIME_FORMAT)

            logger.info("Test complete")

            return kernel_log, message

    # except Exception as e:
    #     logger.warning(str(e))

    # Graph generation function
    def generate_client_pass_fail_graph(self, csv_list=None):
        try:
            logger.info("CSV list " + str(csv_list))
            x_axis_category = []
            for i in range(self.num_sta):
                x_axis_category.append(i + 1)
            logger.info(str(x_axis_category))
            pass_list = []
            fail_list = []
            dataset = []
            for i in csv_list:
                logger.info("i, " + i)
                lf_csv_obj = lf_csv.lf_csv()
                h = lf_csv_obj.read_csv(file_name=i, column="PASS/FAIL")
                count = h.count("PASS")
                logger.info(str(count))
                count_ = h.count("FAIL")
                logger.info(str(count_))
                pass_list.append(count)
                fail_list.append(count_)
            dataset.append(pass_list)
            dataset.append(fail_list)
            logger.info(str(dataset))
            # It will contain per station pass and fail number eg [[9, 7], [3, 4]] here 9, 7 are pass number for clients  3 and 4 are fail number
            # dataset = [[9, 7 , 4], [1, 3, 4]]
            graph = lf_graph.lf_bar_graph(_data_set=dataset,
                                          _xaxis_name="Total Number Of Stations = " + str(self.num_sta),
                                          _yaxis_name="Total Number of Iterations = " + str(self.iteration),
                                          _xaxis_categories=x_axis_category, _label=["Pass", "Fail"], _xticks_font=8,
                                          _graph_image_name="11r roam client per iteration graph",
                                          _color=['forestgreen', 'red', 'blueviolet'], _color_edge='black',
                                          _figsize=(13, 5), _xaxis_step=1,
                                          _graph_title="Client Roaming Performance Over %s Iteration(s)" % (str(self.iteration)),
                                          _show_bar_value=True, _text_font=12, _text_rotation=45, _enable_csv=True,
                                          _legend_loc="upper right", _legend_fontsize=12, _legend_box=(1.12, 1.01),
                                          _remove_border=['top', 'right', 'left'], _alignment={"left": 0.011}, )
            graph_png = graph.build_bar_graph()
            logger.info(str("graph name {}".format(graph_png)))
            return graph_png
        except Exception as e:
            logger.info(str(e))

    def generate_report(self, csv_list, kernel_lst, current_path=None):
        try:
            option, band_, station_, iteration__ = None, None, None, None

            if self.option == 'ota':
                option = "OTA"
            else:
                option = "OTD"

            if self.band == "fiveg":
                band_ = "5 GHz"
            elif self.band == "twog":
                band_ = "2 GHz"
            elif self.band == "sixg":
                band_ = "6 GHz"

            if int(self.num_sta) > 1:
                station_ = "Multi"
            else:
                station_ = "Single"

            if int(self.iteration) > 1:
                iteration__ = "Multi"
            else:
                iteration__ = "Single"

            if self.soft_roam:
                dir_name = "Soft_Roam_Test_" + str(band_) + "_" + str(option) + "_" + str(station_) + "Client_" + str(
                    iteration__) + "_Iteration"
                out_html = "soft_roam.html"
                pdf_name = "soft_roam_test.pdf"
            else:
                dir_name = "Hard_Roam_Test_" + str(band_) + "_" + str(option) + "_" + str(station_) + "Client_" + str(
                    iteration__) + "_Iteration"
                out_html = "hard_roam.html"
                pdf_name = "Hard_roam_test.pdf"

            # Initialize report object
            report = lf_report_pdf.lf_report(_path="",
                                             _results_dir_name=dir_name,
                                             _output_html=out_html,
                                             _output_pdf=pdf_name)

            if current_path is not None:
                report.current_path = os.path.dirname(os.path.abspath(current_path))
            report_path = report.get_report_path()
            report.build_x_directory(directory_name="csv_data")
            report.build_x_directory(directory_name="kernel_log")
            for i in kernel_lst:
                report.move_data(directory="kernel_log", _file_name=str(i))
            date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
            test_setup_info = {
                "Name(s)": self.dut_name,
                "SSID": self.ssid_name,
            }

            # Report title
            if self.soft_roam:
                report.set_title("Soft Roam (11r) Test")
            else:
                if self.sta_type == "normal":
                    report.set_title("Hard Roam Test")
                else:
                    report.set_title("Hard Roam (11r) Test")
            report.set_date(date)
            report.build_banner_cover()
            report.set_table_title("Test Setup Information")
            report.build_table_title()
            report.test_setup_table(value="Device Under Test", test_setup_data=test_setup_info)
            report.set_obj_html("Objective",
                                "The Roaming test is a type of performance test that is performed on wireless Access Points (APs)"
                                " to evaluate their ability to support 802.11r (Fast BSS Transition) standard for fast and seamless"
                                " roaming of wireless clients between APs within the same network. This standard helps minimize the"
                                " handoff time when a client moves from one AP to another, resulting in a more stable and consistent wireless experience.<br>"
                                "<br>"
                                "<b>Hard Roaming:</b><br>"
                                "This happens when a wireless device completely disconnects from the current Access Point before "
                                "connecting to a new one. However, with the 802.11r standard, the authentication and key negotiation"
                                " process can be expedited, reducing the time it takes to connect to the new Access Point. This results"
                                " in a faster and more seamless handoff between Access Points.<br>"
                                "<br>"
                                "<b>Soft Roaming:</b><br>"
                                "This happens when a wireless device maintains a connection with both the current and new Access Points"
                                " during the transition. With 802.11r, the device can maintain its security context during the handoff,"
                                " allowing for a faster and more secure transition. Soft roaming with 11r is designed to be seamless,"
                                " allowing the device to move from one Access Point to another without any interruption in connectivity.")
            report.build_objective()
            report.set_obj_html("Client Per-Iteration Graph",
                                "The below graph provides information about out of total iterations how many times each client got Pass or Fail")
            report.build_objective()
            graph = self.generate_client_pass_fail_graph(csv_list=csv_list)
            report.set_graph_image(graph)
            report.set_csv_filename(graph)
            report.move_csv_file()
            report.move_graph_image()
            report.build_graph_without_border()
            if self.multicast == "True":
                report.set_obj_html("Pass/Fail Criteria:",
                                    "<b>The following are the criteria for PASS the test:</b><br><br>"
                                    "1. The BSSID of the station should change after roaming from one AP to another.<br>"
                                    "2. multicast traffic should resume after the client roams.<br>"
                                    "<br>"
                                    "<b>The following are the criteria for FAIL the test:</b><br><br>"
                                    "1. The BSSID of the station remains unchanged after roaming from one AP to another.<br>"
                                    "2. No roaming occurs, as all stations are connected to the same AP.<br>")
            else:
                report.set_obj_html("Pass/Fail Criteria:",
                                    "<b>The following are the criteria for PASS the test:</b><br><br>"
                                    "1. The BSSID of the station should change after roaming from one AP to another.<br>"
                                    "2. The station should not experience any disconnections during/after the roaming process.<br>"
                                    "3. The duration of the roaming process should be less than 50 ms.<br>"
                                    "<br>"
                                    "<b>The following are the criteria for FAIL the test:</b><br><br>"
                                    "1. The BSSID of the station remains unchanged after roaming from one AP to another.<br>"
                                    "2. No roaming occurs, as all stations are connected to the same AP.<br>"
                                    "3. The captured packet does not contain a Reassociation Response Frame.<br>"
                                    "4. The station experiences disconnection during/after the roaming process.<br>"
                                    "5. The duration of the roaming process exceeds 50 ms.<br>")
            report.build_objective()
            for i in csv_list:
                report.move_data(directory="csv_data", _file_name=str(i))
            report.move_data(directory_name="pcap")
            for i, x in zip(range(self.num_sta), csv_list):
                # report.set_table_title("Client information  " + str(i))
                # report.build_table_title()
                if self.multicast == "True":
                    report.set_obj_html("Client " + str(i + 1) + "  Information",
                                        "The table below presents comprehensive information regarding Client " + str(
                                            i + 1) +
                                        ", including its BSSID before and after roaming, PASS/FAIL criteria and Remark")
                else:
                    report.set_obj_html("Client " + str(i + 1) + "  Information",
                                        "The table below presents comprehensive information regarding Client " + str(
                                            i + 1) +
                                        ", including its BSSID before and after roaming, the time of roaming, the name of "
                                        "the capture file, and any relevant remarks.")
                report.build_objective()
                lf_csv_obj = lf_csv.lf_csv()
                if self.multicast == "True":
                    y = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Iterations")
                    z = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="bssid1")
                    u = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="bssid2")
                    h = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="PASS/FAIL")
                    r = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Remark")
                else:
                    y = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Iterations")
                    z = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="bssid1")
                    u = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="bssid2")
                    t = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Roam Time(ms)")
                    # l = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Packet loss")
                    h = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="PASS/FAIL")
                    p = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Pcap file Name")
                    lf = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Log File")
                    r = lf_csv_obj.read_csv(file_name=str(report_path) + "/csv_data/" + str(x), column="Remark")

                if self.multicast == "True":
                    table = {
                        "Iteration": y,
                        "BSSID Before Roam": z,
                        "BSSID After Roam": u,
                        "Pass/Fail": h,
                        "Remark": r
                    }
                else:
                    table = {
                        "Iteration": y,
                        "BSSID Before Roam": z,
                        "BSSID After Roam": u,
                        "Roam Time (ms)": t,
                        "Pass/Fail": h,
                        "Packet Capture File": p,
                        "Log File": lf,
                        "Remark": r
                    }
                if self.multicast != "True":
                    if not self.log_file:
                        del table["Log File"]

                logger.debug("Report table data:", table)
                test_setup = pd.DataFrame(table)
                report.set_table_dataframe(test_setup)
                report.build_table()

            if self.option == 'ota':
                testname = "Over the air"
            else:
                testname = "Over the DS"

            test_input_infor = {
                "LANforge IP": self.lanforge_ip,
                "LANforge API Port": self.lanforge_port,
                "Test Start": self.start_time,
                "Test End": self.end_time,
                "Bands": self.band,
                "Iterations": self.iteration,
                "Upstream Port": self.upstream,
                "Stations Count": self.num_sta,
                "SSID": self.ssid_name,
                "Security": self.security,
                "Client MACs": self.mac_data,
                "Test": testname,
            }

            report.set_table_title("Test Basic Information")
            report.build_table_title()
            report.test_setup_table(value="Information", test_setup_data=test_input_infor)
            report.build_footer()
            report.write_html()
            report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
            return report_path

        except Exception as e:
            logger.info(str(e))


def parse_args():
    parser = argparse.ArgumentParser(
        prog='lf_roam_test.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
                lf_roam_test.py
        ''',
        description='''\
lf_roam_test.py :
--------------------

Summary :
----------
The primary focus of this script is to enable seamless roaming of clients/stations between two access points (APs).
The test can be conducted with a single or multiple stations, with single or multiple iterations.

The script will create stations/clients with advanced/802.1x and 11r key management. By default, it will create a
single station/client. Once the stations are created, the script will generate CX traffic between the upstream port and
 the stations and run the traffic before roam.

Packet captures will be taken for each station/client in two scenarios:

    (i)  While the station/client is connected to an AP
    (ii) While the station/client roams from one AP to another AP

These packet captures will be used to analyze the performance and stability of the roaming process.

Overall, this script is designed to provide a comprehensive test of the roaming functionality of the APs and the
stability of the network when clients move between APs.

 The following are the criteria for PASS the test:

    1. The BSSID of the station should change after roaming from one AP to another
    2  The station should not experience any disconnections during/after the roaming process.
    3. The duration of the roaming process should be less than 50 ms.

 The following are the criteria for FAIL the test:

    1. The BSSID of the station remains unchanged after roaming from one AP to another.
    2. No roaming occurs, as all stations are connected to the same AP.
    3. The captured packet does not contain a Reassociation Response Frame.
    4. The station experiences disconnection during/after the roaming process.
    5. The duration of the roaming process exceeds 50 ms.


############################################
# Examples Commands for different scenarios
############################################

Hard Roam

EXAMPLE: For a single station and a single iteration
    python3 lf__roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For a single station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For multiple station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For multiple station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based

EXAMPLE: For  multiple station and multiple iteration with multicast traffic enable
   python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "10:f9:20:fd:f3:4b" --ap2_bssid "14:16:9d:53:58:cb"
   --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 2 --ssid_name "RoamAP5g" --security "wpa2"
     --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "36" --option "ota"
     --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --sta_type normal --multicast True


Soft Roam
EXAMPLE: For a single station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For a single station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 1 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For multiple station and a single iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 1 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True

EXAMPLE: For multiple station and multiple iteration
    python3 lf_roam_test.py --mgr 192.168.100.221 --ap1_bssid "68:7d:b4:5f:5c:3b" --ap2_bssid "14:16:9d:53:58:cb"
     --fiveg_radios "1.1.wiphy1" --band "fiveg" --sniff_radio "wiphy2" --num_sta 10 --ssid_name "RoamAP5g" --security "wpa2"
      --security_key "something" --duration None --upstream "eth2" --iteration 10 --channel "40" --option "ota"
      --dut_name ["AP1","AP2"] --traffic_type "lf_udp" --log_file False --debug False --iteration_based --soft_roam True


===============================================================================

            ''')
    required = parser.add_argument_group('Required arguments')

    # LANforge connection settings
    parser.add_argument("-m", "--mgr",
                        dest="lanforge_ip",
                        type=str,
                        default="localhost",
                        help="Hostname or IP address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port", "--lanforge_port",
                        dest="lanforge_port",
                        type=int,
                        default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_ssh_port", "--lanforge_ssh_port",
                        dest="lanforge_ssh_port",
                        type=int,
                        default=22,
                        help="LANforge system SSH port used to SSH in and pull reports")

    # Test settings
    required.add_argument('--band',
                          default="fiveg",
                          help="Band in which to run test (e.g. 'fiveg')")
    required.add_argument("--iters", "--iteration", "--iterations",
                          dest="iteration",
                          type=int,
                          default=1,
                          help="Number of test iterations")

    required.add_argument('--ap1_bssid',
                          dest="c1_bssid",
                          type=str,
                          default="68:7d:b4:5f:5c:3b",
                          help='AP1 bssid')
    required.add_argument('--ap2_bssid',
                          dest="c2_bssid",
                          type=str,
                          default="14:16:9d:53:58:cb",
                          help='AP2 bssid')

    # Packet capture settings
    required.add_argument('--sniff_radio',
                          default="wiphy2",
                          help="Radio used for packet capture")

    # Station creation settings
    required.add_argument('--num_sta',
                          type=int,
                          default=1,
                          help="Number of stations to create")

    required.add_argument('--twog_radios',
                          dest="twog_radio",
                          default=None,
                          help="2.4 GHz radios (used for station creation)")
    required.add_argument('--fiveg_radios',
                          dest="fiveg_radio",
                          default="1.1.wiphy1",
                          help="5 GHz radios (used for station creation)")
    required.add_argument('--sixg_radios',
                          dest="sixg_radio",
                          default="1.1.wiphy1",
                          help="6 GHz radios (used for station creation)")

    required.add_argument("--ssid", "--ssid_name",
                          type=str,
                          default="RoamAP5g",
                          help="Common SSID for AP DUTs (used for station creation)")
    required.add_argument('--security',
                          type=str,
                          default="wpa2",
                          help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >')
    required.add_argument("--password", "--security_key",
                          dest="security_key",
                          type=str,
                          default="something")

    required.add_argument('--upstream',
                          type=str,
                          default="eth2",
                          help="Upstream port for traffic generation")

    # TODO: Cleanup and move to respective sections
    required.add_argument('--duration', help='duration', default=None)
    required.add_argument('--channel', help='Channel', type=str, default="40")
    required.add_argument('--option', help='eg. --option "ota', default="ota")
    required.add_argument('--iteration_based', help='Iteration based', default=False, action='store_true')
    required.add_argument('--duration_based', help='Duration based', default=False, action='store_true')
    required.add_argument('--dut_name', help='', default=["AP1", "AP2"])  # ["AP687D.B45C.1D1C", "AP2C57.4152.385C"]
    required.add_argument('--traffic_type', help='To chose the traffic type', default="lf_udp")
    required.add_argument('--identity', help='Radius server identity', default="testuser")
    required.add_argument('--ttls_pass', help='Radius Server passwd', default="testpasswd")
    required.add_argument('--log_file', help='To get the log file, need to pass the True', default=False)
    required.add_argument('--debug', help='To enable/disable debugger, need to pass the True/False', default=False)
    required.add_argument('--soft_roam', help='To enable soft rome eg. --soft_rome True', default=False)
    required.add_argument('--sta_type', type=str, help="provide the type of"
                                                       " client you want to creatE i.e 11r,11r-sae,"
                                                       " 11r-sae-802.1x or simple as none", default="11r")
    required.add_argument('--multicast', default=False, help="set to true only if we want multicast "
                                                             "traffic run along the hard roam process")

    optional = parser.add_argument_group('Optional arguments')

    # AP controller parameters
    optional.add_argument('--scheme', help='', default="ssh")
    optional.add_argument('--dest', help='', default="localhost")
    optional.add_argument('--user', help='', default="admin")
    optional.add_argument('--passwd', help='', default="Cisco123")
    optional.add_argument('--prompt', help='', default="WLC2")
    optional.add_argument('--series_cc', help='', default="9800")
    optional.add_argument('--ap', help='', default="AP687D.B45C.1D1C")
    optional.add_argument('--ap_ssh_port', help='', default="8888")
    optional.add_argument('--band_cc', help='', default="5g")
    optional.add_argument('--timeout', help='', default="10")

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    help_summary = "This script will test station roaming, both hard (forced) and soft (attenuation-based)" \
                   "and generate a report upon completion. Support for packet capture is also included."

    if args.help_summary:
        print(help_summary)
        exit(0)

    obj = HardRoam(**vars(args), sniff_radio_=args.sniff_radio)

    x = os.getcwd()
    print("Current Working Directory :", x)
    file = obj.generate_csv()
    print("CSV File :", file)
    obj.precleanup()
    kernel, message = obj.run(file_n=file)
    report_dir_name = obj.generate_report(csv_list=file, kernel_lst=kernel, current_path=str(x) + "/tests")
    print(report_dir_name)


if __name__ == '__main__':
    main()
