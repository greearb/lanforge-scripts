#!/usr/bin/env python3
"""
NAME: test_l3.py

PURPOSE: The Layer 3 Traffic Generation Test is designed to test the performance of the Access Point by running layer-3
         Cross-Connect Traffic.  Layer-3 Cross-Connects represent a stream of data flowing through the system under test.
         A Cross-Connect (CX) is composed of two Endpoints, each of which is associated with a particular Port (physical or virtual interface).

         The test will create stations, create cx traffic between upstream port and stations,  run traffic. Verify
         the traffic is being transmitted and received

         * Supports creating user-specified amount stations on multiple radios
         * Supports configuring upload and download requested rates and PDU sizes.
         * Supports generating connections with different ToS values.
         * Supports generating tcp and/or UDP traffic types.
         * Supports iterating over different PDU sizes
         * Supports iterating over different requested tx rates (configurable as total or per-connection value)
         * Supports iterating over attenuation values.
         * Supports testing connection between two ethernet connection - L3 dataplane

         Generic command layout:
         -----------------------
         ./test_l3.py --mgr <ip_address> --test_duration <duration> --endp_type <traffic types> --upstream_port <port>
         --radio "radio==<radio> stations==<number stations> ssid==<ssid> ssid_pw==<ssid password>
         security==<security type: wpa2, open, wpa3>" --debug

EXAMPLE:

#########################################
# Examples
#########################################
Example running traffic with two radios
1. Test duration 30 minutes
2. Traffic IPv4 TCP, UDP
3. Upstream-port eth2
4. Radio #0 wiphy0 has 1 station, ssid = ssid_2g, ssid password = ssid_pw_2g  security = wpa2
5. Radio #1 wiphy1 has 2 stations, ssid = ssid_5g, ssid password = BLANK security = open
6. Create connections with TOS of BK and VI

         # The script now supports multiple radios, each specified with an individual --radio switch.

           * UDP and TCP bi-directional test, no use of controller.
             ./test_l3.py --mgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --upstream_port 1.1.eth1
             --radio "radio==1.1.wiphy0 stations==5 ssid==Netgear2g ssid_pw==lanforge security==wpa2"
             --radio "radio==1.1.wiphy1 stations==1 ssid==Netgear5g ssid_pw==lanforge security==wpa2"
             --test_duration 60s

           * Port resets, chooses random value between min and max
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 90s --polling_interval 10s --upstream_port eth1
             --radio 'radio==wiphy0,stations==4,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,reset_port_enable==TRUE,
             reset_port_time_min==10s,reset_port_time_max==20s' --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000
             --side_b_min_bps=300000000

         # Command: (remove carriage returns)
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 30s --endp_type "lf_tcp,lf_udp" --tos "BK VI" --upstream_port 1.1.eth1
             --radio "radio==1.1.wiphy0 stations==1 ssid==Netgear2g ssid_pw==lanforge security==wpa2"

         # Have the stations continue to run after the completion of the script
             ./test_l3.py --lfmgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --tos BK --upstream_port 1.1.eth1
             --radio 'radio==wiphy0 stations==2 ssid==Netgear2g ssid_pw==lanforge security==wpa2' --test_duration 30s
             --polling_interval 5s --side_a_min_bps 256000 --side_b_min_bps 102400000 --no_stop_traffic

         #  Have script use existing stations from previous run where traffic was not stopped and also create new stations and leave traffic running [ NOT WORKING AS EXPECTED ]
             ./test_l3.py --lfmgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --tos BK --upstream_port 1.1.eth1
             --radio 'radio==wiphy0 stations==2 ssid==Netgear2g ssid_pw==lanforge security==wpa2' --sta_start_offset 1000
             --test_duration 30s --polling_interval 5s --side_a_min_bps 256000 --side_b_min_bps 102400000 --use_existing_station_list
             --existing_station_list '1.1.sta0000,1.1.sta0001,1.1.sta0002' --no_stop_traffic

         # Have script use wifi_settings enable flages  ::  wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 20s --polling_interval 5s --upstream_port 1.1.eth1
             --radio 'radio==1.1.wiphy0,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy1,stations==1,ssid==Netgear5g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy2,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000 --test_rig ID_003 --test_tag 'l3_longevity' --dut_model_num GT-AXE11000 --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0 --dut_serial_num 12345678 --log_level debug

         # Setting wifi_settings per radio
            ./test_l3.py
            --lfmgr 192.168.100.116
            --local_lf_report_dir /home/lanforge/html-reports/
            --test_duration 15s
            --polling_interval 5s
            --upstream_port eth2
            --radio "radio==wiphy1 stations==4 ssid==asus11ax-5 ssid_pw==hello123 security==wpa2  mode==0 wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down&&ht160_enable) "
            --endp_type lf_udp
            --rates_are_totals
            --side_a_min_bps=20000
            --side_b_min_bps=300000000
            --test_rig CT-US-001
            --test_tag 'test_l3'

         # Example : LAN-1927  WPA2-TLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Disabled'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

        # Example : LAN-1927  WPA2-TTLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Disabled'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug


        # Example : LAN-1927  WPA3-TTLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Required'
             --endp_type lf_ud
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

        # Example : LAN-1927  WPA3-TLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Required'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

SCRIPT_CLASSIFICATION:  Creation & Runs Traffic

SCRIPT_CATEGORIES:  Performance, Functional,  KPI Generation,  Report Generation

NOTES:

#################################
# Command switches
#################################

--mgr <hostname for where LANforge GUI is running>',default='localhost'
-d  / --test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m'
--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE"
--debug:  Enable debugging',default=False
-t  / --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types
-u / --upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
-o / --outfile <Output file for csv data>", default='longevity_results'

<duration>: number followed by one of the following
d - days
h - hours
m - minutes
s - seconds

<traffic type>:
lf_udp  : IPv4 UDP traffic
lf_tcp  : IPv4 TCP traffic
lf_udp6 : IPv6 UDP traffic
lf_tcp6 : IPv6 TCP traffic
mc_udp  : IPv4 multi cast UDP traffic
mc_udp6 : IPv6 multi cast UDP traffic

<tos>:
BK, BE, VI, VO:  Optional wifi related Tos Settings.  Or, use your preferred numeric values. Cross connects type of service

    * Data 0 (Best Effort, BE): Medium priority queue, medium throughput and delay.
             Most traditional IP data is sent to this queue.
    * Data 1 (Background, BK): Lowest priority queue, high throughput. Bulk data that requires maximum throughput and
             is not time-sensitive is sent to this queue (FTP data, for example).
    * Data 2 (Video, VI): High priority queue, minimum delay. Time-sensitive data such as Video and other streaming
             media are automatically sent to this queue.
    * Data 3 (Voice, VO): Highest priority queue, minimum delay. Time-sensitive data such as Voice over IP (VoIP)
             is automatically sent to this Queue.

<wifi_mode>:
    Input       : Enum Val  : Shown by nc_show_ports

    AUTO        |  0        #  802.11
    802.11a     |  1        #  802.11a
    b           |  2        #  802.11b
    g           |  3        #  802.11g
    abg         |  4        #  802.11abg
    abgn        |  5        #  802.11abgn
    bgn         |  6        #  802.11bgn
    bg          |  7        #  802.11bg
    abgnAC      |  8        #  802.11abgn-AC
    anAC        |  9        #  802.11an-AC
    an          | 10        #  802.11an
    bgnAC       | 11        #  802.11bgn-AC
    abgnAX      | 12        #  802.11abgn-AX
                            #     a/b/g/n/AC/AX (dual-band AX) support
    bgnAX       | 13        #  802.11bgn-AX
    anAX        | 14        #  802.11an-AX
    aAX         | 15        #  802.11a-AX (6E disables /n and /ac)

wifi_settings flags are currently defined as:
    wpa_enable           | 0x10         # Enable WPA
    custom_conf          | 0x20         # Use Custom wpa_supplicant config file.
    wep_enable           | 0x200        # Use wpa_supplicant configured for WEP encryption.
    wpa2_enable          | 0x400        # Use wpa_supplicant configured for WPA2 encryption.
    ht40_disable         | 0x800        # Disable HT-40 even if hardware and AP support it.
    scan_ssid            | 0x1000       # Enable SCAN-SSID flag in wpa_supplicant.
    passive_scan         | 0x2000       # Use passive scanning (don't send probe requests).
    disable_sgi          | 0x4000       # Disable SGI (Short Guard Interval).
    lf_sta_migrate       | 0x8000       # OK-To-Migrate (Allow station migration between LANforge radios)
    verbose              | 0x10000      # Verbose-Debug:  Increase debug info in wpa-supplicant and hostapd logs.
    80211u_enable        | 0x20000      # Enable 802.11u (Interworking) feature.
    80211u_auto          | 0x40000      # Enable 802.11u (Interworking) Auto-internetworking feature.  Always enabled currently.
    80211u_gw            | 0x80000      # AP Provides access to internet (802.11u Interworking)
    80211u_additional    | 0x100000     # AP requires additional step for access (802.11u Interworking)
    80211u_e911          | 0x200000     # AP claims emergency services reachable (802.11u Interworking)
    80211u_e911_unauth   | 0x400000     # AP provides Unauthenticated emergency services (802.11u Interworking)
    hs20_enable          | 0x800000     # Enable Hotspot 2.0 (HS20) feature.  Requires WPA-2.
    disable_gdaf         | 0x1000000    # AP:  Disable DGAF (used by HotSpot 2.0).
    8021x_radius         | 0x2000000    # Use 802.1x (RADIUS for AP).
    80211r_pmska_cache   | 0x4000000    # Enable oportunistic PMSKA caching for WPA2 (Related to 802.11r).
    disable_ht80         | 0x8000000    # Disable HT80 (for AC chipset NICs only)
    ibss_mode            | 0x20000000   # Station should be in IBSS mode.
    osen_enable          | 0x40000000   # Enable OSEN protocol (OSU Server-only Authentication)
    disable_roam         | 0x80000000   # Disable automatic station roaming based on scan results.
    ht160_enable         | 0x100000000  # Enable HT160 mode.
    disable_fast_reauth  | 0x200000000  # Disable fast_reauth option for virtual stations.
    mesh_mode            | 0x400000000  # Station should be in MESH mode.
    power_save_enable    | 0x800000000  # Station should enable power-save.  May not work in all drivers/configurations.
    create_admin_down    | 0x1000000000 # Station should be created admin-down.
    wds-mode             | 0x2000000000 # WDS station (sort of like a lame mesh), not supported on ath10k
    no-supp-op-class-ie  | 0x4000000000 # Do not include supported-oper-class-IE in assoc requests.  May work around AP bugs.
    txo-enable           | 0x8000000000 # Enable/disable tx-offloads, typically managed by set_wifi_txo command
    use-wpa3             | 0x10000000000 # Enable WPA-3 (SAE Personal) mode.
    use-bss-transition   | 0x80000000000 # Enable BSS transition.
    disable-twt          | 0x100000000000 # Disable TWT mode

For wifi_extra_keys syntax :
    telnet <lanforge ip> 4001
    type: help set_wifi_extra
wifi_extra keys:
                key_mgmt  (Key Mangement)
                pairwise  (Pairwise Ciphers)
                group   (Group Ciphers)
                psk     (WPA PSK)
                wep_key
                ca_cert (CA Cert File)
                eap     (EAP Methods) EAP method: MD5, MSCHAPV2, OTP, GTC, TLS, PEAP, TTLS. (note different the GUI no appended EAP-)
                identity    (EAP Identity)
                anonymous_identity  (EAP Anon Identity)
                phase1  (Phase-1)
                phase2  (Phase-2)
                passwd  (EAP Password)
                pin (EAP Pin)
                pac_file    (PAC file)
                private_key (Private Key)
                pk_password (PK Password)
                hessid="00:00:00:00:00:00"
                realm   (Realm)
                client_cert (Client Cert)
                imsi    (IMSI)
                milenage    (Milenage)
                domain  (Domain)
                roaming_consortium  (Consortium)
                venue_group ()
                network_type    (Network Auth)
                ipaddr_type_avail   ()
                network_auth_type ()
                anqp_3gpp_cell_net ()

                ieee80211w :   0,1,2

Multicast traffic :
        Multicast traffic default IGMP Address in the range of 224.0.0.0 to 239.255.255.255,
        so I have provided 224.9.9.9 as IGMP address and IGMP Dest port as 9999 and MIN-IP PORT as 9999.
        these values must be same on the eth1(server side) and client side, then the traffic will run.

===============================================================================
 ** FURTHER INFORMATION **
    Using the layer3_cols flag:

    Currently the output function does not support inputting the columns in layer3_cols the way they are displayed in the GUI. This quirk is under construction. To output
    certain columns in the GUI in your final report, please match the according GUI column display to it's counterpart to have the columns correctly displayed in
    your report.

    GUI Column Display       Layer3_cols argument to type in (to print in report)

    Name                |  'name'
    EID                 |  'eid'
    Run                 |  'run'
    Mng                 |  'mng'
    Script              |  'script'
    Tx Rate             |  'tx rate'
    Tx Rate (1 min)     |  'tx rate (1&nbsp;min)'
    Tx Rate (last)      |  'tx rate (last)'
    Tx Rate LL          |  'tx rate ll'
    Rx Rate             |  'rx rate'
    Rx Rate (1 min)     |  'rx rate (1&nbsp;min)'
    Rx Rate (last)      |  'rx rate (last)'
    Rx Rate LL          |  'rx rate ll'
    Rx Drop %           |  'rx drop %'
    Tx PDUs             |  'tx pdus'
    Tx Pkts LL          |  'tx pkts ll'
    PDU/s TX            |  'pdu/s tx'
    Pps TX LL           |  'pps tx ll'
    Rx PDUs             |  'rx pdus'
    Rx Pkts LL          |  'pps rx ll'
    PDU/s RX            |  'pdu/s tx'
    Pps RX LL           |  'pps rx ll'
    Delay               |  'delay'
    Dropped             |  'dropped'
    Jitter              |  'jitter'
    Tx Bytes            |  'tx bytes'
    Rx Bytes            |  'rx bytes'
    Replays             |  'replays'
    TCP Rtx             |  'tcp rtx'
    Dup Pkts            |  'dup pkts'
    Rx Dup %            |  'rx dup %'
    OOO Pkts            |  'ooo pkts'
    Rx OOO %            |  'rx ooo %'
    RX Wrong Dev        |  'rx wrong dev'
    CRC Fail            |  'crc fail'
    RX BER              |  'rx ber'
    CX Active           |  'cx active'
    CX Estab/s          |  'cx estab/s'
    1st RX              |  '1st rx'
    CX TO               |  'cx to'
    Pattern             |  'pattern'
    Min PDU             |  'min pdu'
    Max PDU             |  'max pdu'
    Min Rate            |  'min rate'
    Max Rate            |  'max rate'
    Send Buf            |  'send buf'
    Rcv Buf             |  'rcv buf'
    CWND                |  'cwnd'
    TCP MSS             |  'tcp mss'
    Bursty              |  'bursty'
    A/B                 |  'a/b'
    Elapsed             |  'elapsed'
    Destination Addr    |  'destination addr'
    Source Addr         |  'source addr'

    Using the port_mgr_cols flag:
         '4way time (us)'
         'activity'
         'alias'
         'anqp time (us)'
         'ap'
         'beacon'
         'bps rx'
         'bps rx ll'
         'bps tx'
         'bps tx ll'
         'bytes rx ll'
         'bytes tx ll'
         'channel'
         'collisions'
         'connections'
         'crypt'
         'cx ago'
         'cx time (us)'
         'device'
         'dhcp (ms)'
         'down'
         'entity id'
         'gateway ip'
         'ip'
         'ipv6 address'
         'ipv6 gateway'
         'key/phrase'
         'login-fail'
         'login-ok'
         'logout-fail'
         'logout-ok'
         'mac'
         'mask'
         'misc'
         'mode'
         'mtu'
         'no cx (us)'
         'noise'
         'parent dev'
         'phantom'
         'port'
         'port type'
         'pps rx'
         'pps tx'
         'qlen'
         'reset'
         'retry failed'
         'rx bytes'
         'rx crc'
         'rx drop'
         'rx errors'
         'rx fifo'
         'rx frame'
         'rx length'
         'rx miss'
         'rx over'
         'rx pkts'
         'rx-rate'
         'sec'
         'signal'
         'ssid'
         'status'
         'time-stamp'
         'tx abort'
         'tx bytes'
         'tx crr'
         'tx errors'
         'tx fifo'
         'tx hb'
         'tx pkts'
         'tx wind'
         'tx-failed %'
         'tx-rate'
         'wifi retries'

    Can't decide what columns to use? You can just use 'all' to select all available columns from both tables.

STATUS: Functional

VERIFIED_ON:   18-JULY-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

"""
import argparse
import csv
import datetime
import importlib
import os
import random
import sys
import time
from pprint import pprint
from pprint import pformat
import logging
import platform
import itertools
import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_kpi_csv = importlib.import_module("py-scripts.lf_kpi_csv")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")

# from lf_graph import lf_bar_graph_horizontal
# from lf_graph import lf_bar_graph


# additional imports for testing with vap
lf_attenuator = importlib.import_module("py-scripts.lf_atten_mod_test")
modify_vap = importlib.import_module("py-scripts.modify_vap")
lf_modify_radio = importlib.import_module("py-scripts.lf_modify_radio")

# cleanup library
lf_cleanup = importlib.import_module("py-scripts.lf_cleanup")


Realm = realm.Realm

logger = logging.getLogger(__name__)


# This class handles running the test and generating reports.
class L3VariableTime(Realm):
    def __init__(self,
                 endp_types,
                 args,
                 tos,
                 side_b,
                 side_a,
                 radio_name_list,
                 number_of_stations_per_radio_list,
                 ssid_list,
                 ssid_password_list,
                 ssid_security_list,
                 wifi_mode_list,
                 enable_flags_list,
                 station_lists,
                 name_prefix,
                 outfile,
                 reset_port_enable_list,
                 reset_port_time_min_list,
                 reset_port_time_max_list,
                 side_a_min_rate=None,
                 side_a_max_rate=None,
                 side_b_min_rate=None,
                 side_b_max_rate=None,
                 side_a_min_pdu=None,
                 side_a_max_pdu=None,
                 side_b_min_pdu=None,
                 side_b_max_pdu=None,
                 user_tags=None,
                 rates_are_totals=False,
                 mconn=1,
                 attenuators=None,
                 atten_vals=None,
                 number_template="00",
                 test_duration="256s",
                 polling_interval="60s",
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 debug=False,
                 db=None,
                 kpi_csv=None,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _proxy_str=None,
                 _capture_signal_list=None,
                 no_cleanup=False,
                 use_existing_station_lists=False,
                 existing_station_lists=None,
                 wait_for_ip_sec="120s",

                 # ap module
                 ap_read=False,
                 ap_module=None,
                 ap_test_mode=False,
                 ap_ip=None,
                 ap_user=None,
                 ap_passwd=None,
                 ap_scheme='ssh',
                 ap_serial_port='/dev/ttyUSB0',
                 ap_ssh_port="22",
                 ap_telnet_port="23",
                 ap_serial_baud='115200',
                 ap_if_2g="eth6",
                 ap_if_5g="eth7",
                 ap_if_6g="eth8",
                 ap_report_dir="",
                 ap_file="",
                 ap_band_list=['2g', '5g', '6g'],

                 # wifi extra configuration
                 key_mgmt_list=[],
                 pairwise_list=[],
                 group_list=[],
                 psk_list=[],
                 wep_key_list=[],
                 ca_cert_list=[],
                 eap_list=[],
                 identity_list=[],
                 anonymous_identity_list=[],
                 phase1_list=[],
                 phase2_list=[],
                 passwd_list=[],
                 pin_list=[],
                 pac_file_list=[],
                 private_key_list=[],
                 pk_password_list=[],
                 hessid_list=[],
                 realm_list=[],
                 client_cert_list=[],
                 imsi_list=[],
                 milenage_list=[],
                 domain_list=[],
                 roaming_consortium_list=[],
                 venue_group_list=[],
                 network_type_list=[],
                 ipaddr_type_avail_list=[],
                 network_auth_type_list=[],
                 anqp_3gpp_cell_net_list=[],
                 ieee80211w_list=[]
                 ):

        self.eth_endps = []
        self.cx_names = []
        self.total_stas = 0
        if side_a_min_rate is None:
            side_a_min_rate = [56000]
        if side_a_max_rate is None:
            side_a_max_rate = [0]
        if side_b_min_rate is None:
            side_b_min_rate = [56000]
        if side_b_max_rate is None:
            side_b_max_rate = [0]
        if side_a_min_pdu is None:
            side_a_min_pdu = ["MTU"]
        if side_a_max_pdu is None:
            side_a_max_pdu = [0]
        if side_b_min_pdu is None:
            side_b_min_pdu = ["MTU"]
        if side_b_max_pdu is None:
            side_b_max_pdu = [0]
        if user_tags is None:
            user_tags = []
        if attenuators is None:
            attenuators = []
        if atten_vals is None:
            atten_vals = []
        if _capture_signal_list is None:
            _capture_signal_list = []
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)
        self.kpi_csv = kpi_csv
        self.tos = tos.split(",")
        self.endp_types = endp_types.split(",")
        self.side_b = side_b
        self.side_a = side_a
        # if it is a dataplane test the side_a is not none and an ethernet port
        if self.side_a is not None:
            self.dataplane = True
        else:
            self.dataplane = False
        self.ssid_list = ssid_list
        self.ssid_password_list = ssid_password_list
        self.wifi_mode_list = wifi_mode_list
        self.enable_flags_list = enable_flags_list
        self.station_lists = station_lists
        self.ssid_security_list = ssid_security_list
        self.reset_port_enable_list = reset_port_enable_list
        self.reset_port_time_min_list = reset_port_time_min_list
        self.reset_port_time_max_list = reset_port_time_max_list
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.radio_name_list = radio_name_list
        self.number_of_stations_per_radio_list = number_of_stations_per_radio_list
        # self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.polling_interval_seconds = self.duration_time_to_seconds(
            polling_interval)
        self.cx_profile = self.new_l3_cx_profile()
        self.multicast_profile = self.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-"
        self.station_profiles = []
        self.args = args
        self.outfile = outfile
        self.csv_started = False
        self.epoch_time = int(time.time())
        self.debug = debug
        self.mconn = mconn
        self.user_tags = user_tags

        self.side_a_min_rate = side_a_min_rate
        self.side_a_max_rate = side_a_max_rate
        self.side_b_min_rate = side_b_min_rate
        self.side_b_max_rate = side_b_max_rate

        self.side_a_min_pdu = side_a_min_pdu
        self.side_a_max_pdu = side_a_max_pdu
        self.side_b_min_pdu = side_b_min_pdu
        self.side_b_max_pdu = side_b_max_pdu

        self.rates_are_totals = rates_are_totals
        self.cx_count = 0
        self.station_count = 0

        self.no_cleanup = no_cleanup
        self.use_existing_station_lists = use_existing_station_lists
        self.existing_station_lists = existing_station_lists

        self.wait_for_ip_sec = self.duration_time_to_seconds(wait_for_ip_sec)

        self.attenuators = attenuators
        self.atten_vals = atten_vals
        if ((len(self.atten_vals) > 0) and (
                self.atten_vals[0] != -1) and (len(self.attenuators) == 0)):
            logger.error(
                "ERROR:  Attenuation values configured, but no Attenuator EIDs specified.\n")
            exit(1)

        self.cx_profile.mconn = mconn
        self.cx_profile.side_a_min_bps = side_a_min_rate[0]
        self.cx_profile.side_a_max_bps = side_a_max_rate[0]
        self.cx_profile.side_b_min_bps = side_b_min_rate[0]
        self.cx_profile.side_b_max_bps = side_b_max_rate[0]

        # Lookup key is port-eid name
        self.dl_port_csv_files = {}
        self.dl_port_csv_writers = {}

        self.dl_port_total_csv_files = {}
        self.dl_port_total_csv_writers = {}

        self.ul_port_csv_files = {}
        self.ul_port_csv_writers = {}

        # Interopt graphs
        # Data used for graphing the TOS bar graphs
        # currently place all types of traffic together.
        # TODO separate out Multi cast and Uni cast
        self.side_b_min_bps = 0
        self.ride_a_min_bps = 0

        self.endp_data = {}
        self.port_response = {}
        self.endpoint_data = {}

        self.port_data = {}
        self.resourse_data = {}


        # endp data BK -A
        self.bk_clients_A = []
        self.bk_tos_ul_A = []
        self.bk_tos_dl_A = []
        self.bk_endp_eid_A = []

        # port data BK -A
        self.bk_port_eid_A = []
        self.bk_port_mac_A = []
        self.bk_port_channel_A = []
        self.bk_port_mode_A = []
        self.bk_port_observed_rx_rate_A = []
        self.bk_port_observed_tx_rate_A = []
        self.bk_port_traffic_type_A = []
        self.bk_port_protocol_A = []
        self.bk_port_offered_rx_rate_A = []
        self.bk_port_offered_tx_rate_A = []

        # resource data BK -A
        self.bk_resourse_host_A = []
        self.bk_resourse_hw_ver_A = []

        self.bk_request_dl_A = []
        self.bk_request_ul_A = []

        # dataframe BK -A
        self.bk_dataframe_A = pd.DataFrame()

        # endp data BK -B
        self.bk_clients_B = []
        self.bk_tos_ul_B = []
        self.bk_tos_dl_B = []
        self.bk_endp_eid_B = []

        # port data BK -B
        self.bk_port_eid_B = []
        self.bk_port_mac_B = []
        self.bk_port_channel_B = []
        self.bk_port_mode_B = []
        self.bk_port_observed_rx_rate_B = []
        self.bk_port_observed_tx_rate_B = []
        self.bk_port_traffic_type_B = []
        self.bk_port_protocol_B = []
        self.bk_port_offered_rx_rate_B = []
        self.bk_port_offered_tx_rate_B = []

        # resource data BK -B
        self.bk_resourse_host_B = []
        self.bk_resourse_hw_ver_B = []

        self.bk_request_dl_B = []
        self.bk_request_ul_B = []

        # dataframe BK -B
        self.bk_dataframe_B = pd.DataFrame()

        # endp data BE -A
        self.be_clients_A = []
        self.be_tos_ul_A = []
        self.be_tos_dl_A = []
        self.be_endp_eid_dl_A = []


        # port data BE -A
        self.be_port_eid_dl_A = []
        self.be_port_mac_dl_A = []
        self.be_port_channel_dl_A = []
        self.be_port_mode_A = []
        self.be_port_observed_rx_rate_A = []
        self.be_port_observed_tx_rate_A = []
        self.be_port_traffic_type_A = []
        self.be_port_protocol_A = []
        self.be_port_offered_rx_rate_A = []
        self.be_port_offered_tx_rate_A = []


        # resource data BE -A
        self.be_resourse_host_A = []
        self.be_resourse_hw_ver_A = []

        self.be_request_dl_A = []
        self.be_request_ul_A = []


        # dataframe BE -A
        self.be_dataframe_A = pd.DataFrame()

        # endp data BE -B
        self.be_clients_B = []
        self.be_tos_ul_B = []
        self.be_tos_dl_B = []
        self.be_endp_eid_dl_B = []

        # port data BE -B
        self.be_port_eid_dl_B = []
        self.be_port_mac_dl_B = []
        self.be_port_channel_dl_B = []
        self.be_port_mode_B = []
        self.be_port_observed_rx_rate_B = []
        self.be_port_observed_tx_rate_B = []
        self.be_port_traffic_type_B = []
        self.be_port_protocol_B = []
        self.be_port_offered_rx_rate_B = []
        self.be_port_offered_tx_rate_B = []


        # resource data BE -B
        self.be_resourse_host_B = []
        self.be_resourse_hw_ver_B = []

        self.be_request_dl_B = []
        self.be_request_ul_B = []

        # dataframe BE -B
        self.be_dataframe_B = pd.DataFrame()

        # endp data VI -A
        self.vi_clients_A = []
        self.vi_tos_ul_A = []
        self.vi_tos_dl_A = []
        self.vi_endp_eid_dl_A = []

        # port data VI -A
        self.vi_port_eid_dl_A = []
        self.vi_port_mac_dl_A = []
        self.vi_port_channel_dl_A = []
        self.vi_port_mode_A = []
        self.vi_port_observed_rx_rate_A = []
        self.vi_port_observed_tx_rate_A = []
        self.vi_port_traffic_type_A = []
        self.vi_port_protocol_A = []
        self.vi_port_offered_rx_rate_A = []
        self.vi_port_offered_tx_rate_A = []

        # resource data VI -A
        self.be_resourse_host_A = []
        self.be_resourse_hw_ver_A = []


        self.vi_request_dl_A = []
        self.vi_request_ul_A = []

        # dataframe resource data VI -A
        self.vi_dataframe_A = pd.DataFrame()

        # endp data VI -B
        self.vi_clients_B = []
        self.vi_tos_ul_B = []
        self.vi_tos_dl_B = []
        self.vi_endp_eid_dl_B = []

        # port data  VI -B
        self.vi_port_eid_dl_B = []
        self.vi_port_mac_dl_B = []
        self.vi_port_channel_dl_B = []
        self.vi_port_mode_B = []
        self.vi_port_observed_rx_rate_B = []
        self.vi_port_observed_tx_rate_B = []
        self.vi_port_traffic_type_B = []
        self.vi_port_protocol_B = []
        self.vi_port_offered_rx_rate_B = []
        self.vi_port_offered_tx_rate_B = []


        # resource data VI -B
        self.vi_resourse_host_B = []
        self.vi_resourse_hw_ver_B = []

        self.vi_request_dl_B = []
        self.vi_request_ul_B = []

        # dataframe  VI -B
        self.vi_dataframe_B = pd.DataFrame()

        # endp data VO -A
        self.vo_clients_A = []
        self.vo_tos_ul_A = []
        self.vo_tos_dl_A = []
        self.vo_endp_eid_dl_A = []
        self.vo_port_mode_A = []
        self.vo_port_observed_rx_rate_A = []
        self.vo_port_observed_tx_rate_A = []
        self.vo_port_traffic_type_A = []
        self.vo_port_protocol_A = []
        self.vo_port_offered_rx_rate_A = []
        self.vo_port_offered_tx_rate_A = []

        # port data VO -A
        self.vo_port_eid_dl_A = []
        self.vo_port_mac_dl_A = []
        self.vo_port_channel_dl_A = []
        self.vo_port_mode_A = []
        self.vo_port_observed_rx_rate_A = []
        self.vo_port_observed_tx_rate_A = []
        self.vo_port_traffic_type_A = []
        self.vo_port_protocol_A = []
        self.vo_port_offered_rx_rate_A = []
        self.vo_port_offered_tx_rate_A = []


        # resource data VO -A
        self.vo_resourse_host_B = []
        self.vo_resourse_hw_ver_B = []


        self.vo_request_dl_A = []
        self.vo_request_ul_A = []

        # dataframe VO -A
        self.vo_dataframe_A = pd.DataFrame()

        #endp data VO -B
        self.vo_clients_B = []
        self.vo_tos_ul_B = []
        self.vo_tos_dl_B = []
        self.vo_endp_eid_dl_B = []

        # port data VO -B
        self.vo_port_eid_dl_B = []
        self.vo_port_mac_dl_B = []
        self.vo_port_channel_dl_B = []
        self.vo_port_mode_B = []
        self.vo_port_observed_rx_rate_B = []
        self.vo_port_observed_tx_rate_B = []
        self.vo_port_traffic_type_B = []
        self.vo_port_protocol_B = []
        self.vo_port_offered_rx_rate_B = []
        self.vo_port_offered_tx_rate_B = []

        # resource data VO -B
        self.vo_resourse_host_B = []
        self.vo_resourse_hw_ver_B = []


        self.vo_request_dl_B = []
        self.vo_request_ul_B = []

        
        # dataframe VO -B
        self.vo_dataframe_B = pd.DataFrame()

        self.client_dict = {}
        self.client_table_dict = {}

        # AP information
        self.ap = None
        self.ap_obj = None
        self.ap_read = ap_read
        self.ap_module = ap_module
        self.ap_test_mode = ap_test_mode
        self.ap_ip = ap_ip
        self.ap_user = ap_user
        self.ap_passwd = ap_passwd
        self.ap_scheme = ap_scheme
        self.ap_serial_port = ap_serial_port
        self.ap_ssh_port = ap_ssh_port
        self.ap_telnet_port = ap_telnet_port
        self.ap_serial_baud = ap_serial_baud
        self.ap_if_2g = ap_if_2g
        self.ap_if_5g = ap_if_5g
        self.ap_if_6g = ap_if_6g
        self.ap_report_dir = ap_report_dir
        self.ap_file = ap_file
        self.ap_band_list = ap_band_list

        # wifi extra configuration
        self.key_mgmt_list = key_mgmt_list
        self.pairwise_list = pairwise_list
        self.group_list = group_list
        self.psk_list = psk_list
        self.wep_key_list = wep_key_list
        self.ca_cert_list = ca_cert_list
        self.eap_list = eap_list
        self.identity_list = identity_list
        self.anonymous_identity_list = anonymous_identity_list
        self.phase1_list = phase1_list
        self.phase2_list = phase2_list
        self.passwd_list = passwd_list
        self.pin_list = pin_list
        self.pac_file_list = pac_file_list
        self.private_key_list = private_key_list
        self.pk_password_list = pk_password_list
        self.hessid_list = hessid_list
        self.realm_list = realm_list
        self.client_cert_list = client_cert_list
        self.imsi_list = imsi_list
        self.milenage_list = milenage_list
        self.domain_list = domain_list
        self.roaming_consortium_list = roaming_consortium_list
        self.venue_group_list = venue_group_list
        self.network_type_list = network_type_list
        self.ipaddr_type_avail_list = ipaddr_type_avail_list
        self.network_auth_type_list = network_auth_type_list
        self.anqp_3gpp_cell_net_list = anqp_3gpp_cell_net_list
        self.ieee80211w_list = ieee80211w_list

        # AP information import the module
        if self.ap_read and self.ap_module is not None:
            ap_module = importlib.import_module(self.ap_module)
            self.ap = ap_module.create_ap_obj(
                ap_test_mode=self.ap_test_mode,
                ap_ip=self.ap_ip,
                ap_user=self.ap_user,
                ap_passwd=self.ap_passwd,
                ap_scheme=self.ap_scheme,
                ap_serial_port=self.ap_serial_port,
                ap_ssh_port=self.ap_ssh_port,
                ap_telnet_port=self.ap_telnet_port,
                ap_serial_baud=self.ap_serial_baud,
                ap_if_2g=self.ap_if_2g,
                ap_if_5g=self.ap_if_5g,
                ap_if_6g=self.ap_if_6g,
                ap_report_dir=self.ap_report_dir,
                ap_file=self.ap_file,
                ap_band_list=self.ap_band_list)

            # this is needed to access the methods of the imported object
            self.ap.say_hi()

        else:
            logger.info(
                "self.ap_read set to True and self.module is None,  will set self.ap_read to False")
            self.ap_read = False

        dur = self.duration_time_to_seconds(self.test_duration)

        if self.polling_interval_seconds > dur + 1:
            self.polling_interval_seconds = dur - 1

        # Full spread-sheet data
        if self.outfile is not None:
            results = self.outfile[:-4]
            results = results + "-results.csv"
            self.csv_results_file = open(results, "w")
            self.csv_results_writer = csv.writer(
                self.csv_results_file, delimiter=",")

        # if it is a dataplane test the side_a is not None and an ethernet port
        # if side_a is None then side_a is radios
        if not self.dataplane:
            for (
                    radio_,
                    ssid_,
                    ssid_password_,
                    ssid_security_,
                    mode_,
                    enable_flags_,
                    reset_port_enable_,
                    reset_port_time_min_,
                    reset_port_time_max_,
                    key_mgmt_,
                    pairwise_,
                    group_,
                    psk_,
                    wep_key_,
                    ca_cert_,
                    eap_,
                    identity_,
                    anonymous_identity_,
                    phase1_,
                    phase2_,
                    passwd_,
                    pin_,
                    pac_file_,
                    private_key_,
                    pk_password_,
                    hessid_,
                    realm_,
                    client_cert_,
                    imsi_,
                    milenage_,
                    domain_,
                    roaming_consortium_,
                    venue_group_,
                    network_type_,
                    ipaddr_type_avail_,
                    network_auth_type_,
                    anqp_3gpp_cell_net_,
                    ieee80211w_) in zip(
                    self.radio_name_list,
                    self.ssid_list,
                    self.ssid_password_list,
                    self.ssid_security_list,
                    self.wifi_mode_list,
                    self.enable_flags_list,
                    self.reset_port_enable_list,
                    self.reset_port_time_min_list,
                    self.reset_port_time_max_list,
                    self.key_mgmt_list,
                    self.pairwise_list,
                    self.group_list,
                    self.psk_list,
                    self.wep_key_list,
                    self.ca_cert_list,
                    self.eap_list,
                    self.identity_list,
                    self.anonymous_identity_list,
                    self.phase1_list,
                    self.phase2_list,
                    self.passwd_list,
                    self.pin_list,
                    self.pac_file_list,
                    self.private_key_list,
                    self.pk_password_list,
                    self.hessid_list,
                    self.realm_list,
                    self.client_cert_list,
                    self.imsi_list,
                    self.milenage_list,
                    self.domain_list,
                    self.roaming_consortium_list,
                    self.venue_group_list,
                    self.network_type_list,
                    self.ipaddr_type_avail_list,
                    self.network_auth_type_list,
                    self.anqp_3gpp_cell_net_list,
                    self.ieee80211w_list
            ):
                self.station_profile = self.new_station_profile()
                self.station_profile.lfclient_url = self.lfclient_url
                self.station_profile.ssid = ssid_
                self.station_profile.ssid_pass = ssid_password_
                self.station_profile.security = ssid_security_
                self.station_profile.number_template = self.number_template
                self.station_profile.mode = mode_
                self.station_profile.desired_add_sta_flags = enable_flags_.copy()
                self.station_profile.desired_add_sta_flags_mask = enable_flags_.copy()

                # set_wifi_extra
                if key_mgmt_ != '[BLANK]':
                    # for teesting
                    # if key_mgmt_ == '[BLANK]':
                    self.station_profile.set_wifi_extra(key_mgmt=key_mgmt_,
                                                        pairwise=pairwise_,
                                                        group=group_,
                                                        psk=psk_,
                                                        wep_key=wep_key_,
                                                        ca_cert=ca_cert_,
                                                        eap=eap_,
                                                        identity=identity_,
                                                        anonymous_identity=anonymous_identity_,
                                                        phase1=phase1_,
                                                        phase2=phase2_,
                                                        passwd=passwd_,
                                                        pin=pin_,
                                                        pac_file=pac_file_,
                                                        private_key=private_key_,
                                                        pk_password=pk_password_,
                                                        hessid=hessid_,
                                                        realm=realm_,
                                                        client_cert=client_cert_,
                                                        imsi=imsi_,
                                                        milenage=milenage_,
                                                        domain=domain_,
                                                        roaming_consortium=roaming_consortium_,
                                                        venue_group=venue_group_,
                                                        network_type=network_type_,
                                                        ipaddr_type_avail=ipaddr_type_avail_,
                                                        network_auth_type=network_auth_type_,
                                                        anqp_3gpp_cell_net=anqp_3gpp_cell_net_
                                                        )
                    if ieee80211w_.lower() == 'disabled':
                        self.station_profile.set_command_param(
                            "add_sta", "ieee80211w", 0)
                    elif ieee80211w_.lower() == 'required':
                        self.station_profile.set_command_param(
                            "add_sta", "ieee80211w", 2)
                    # may want to set an error if not optional yet for now default to optional
                    else:
                        self.station_profile.set_command_param(
                            "add_sta", "ieee80211w", 1)

                # place the enable and disable flags
                # self.station_profile.desired_add_sta_flags = self.enable_flags
                # self.station_profile.desired_add_sta_flags_mask = self.enable_flags
                self.station_profile.set_reset_extra(
                    reset_port_enable=reset_port_enable_,
                    test_duration=self.duration_time_to_seconds(
                        self.test_duration),
                    reset_port_min_time=self.duration_time_to_seconds(
                        reset_port_time_min_),
                    reset_port_max_time=self.duration_time_to_seconds(reset_port_time_max_))
                self.station_profiles.append(self.station_profile)
            # Use existing station list is similiar to no rebuild
            if self.use_existing_station_lists:
                for existing_station_list in self.existing_station_lists:
                    self.station_profile = self.new_station_profile()
                    self.station_profile.station_names.append(
                        existing_station_list)
                    self.station_profiles.append(self.station_profile)
        else:
            pass

        self.multicast_profile.host = self.lfclient_host
        self.cx_profile.host = self.lfclient_host
        self.cx_profile.port = self.lfclient_port
        self.cx_profile.name_prefix = self.name_prefix

        self.lf_endps = None
        self.udp_endps = None
        self.tcp_endps = None

    def get_results_csv(self):
        # print("self.csv_results_file {}".format(self.csv_results_file.name))
        return self.csv_results_file.name

    # Find avg latency, jitter for connections using specified port.
    def get_endp_stats_for_port(self, port_eid, endps):
        lat = 0
        jit = 0
        total_dl_rate = 0
        total_dl_rate_ll = 0
        total_dl_pkts_ll = 0
        dl_rx_drop_percent = 0
        total_ul_rate = 0
        total_ul_rate_ll = 0
        total_ul_pkts_ll = 0
        ul_rx_drop_percent = 0
        count = 0
        sta_name = 'no_station'

        eid = port_eid
        logger.info("endp-stats-for-port, port-eid: {}".format(port_eid))
        eid = self.name_to_eid(port_eid)
        logger.debug(
            "eid: {eid}".format(eid=eid))

        # Convert all eid elements to strings
        eid[0] = str(eid[0])
        eid[1] = str(eid[1])
        eid[2] = str(eid[2])

        for endp in endps:
            # pprint(endp)
            logger.info(endp)
            eid_endp = endp["eid"].split(".")
            logger.debug(
                "Comparing eid:{eid} to endp-id {eid_endp}".format(eid=eid, eid_endp=eid_endp))
            # Look through all the endpoints (endps), to find the port the port_eid is using.
            # The port_eid that has the same Shelf, Resource, and Port as the eid_endp (looking at all the endps)
            # Then read the eid_endp to get the delay, jitter and rx rate
            # Note: the endp eid is shelf.resource.port.endp-id, the eid can be treated somewhat as
            # child class of port-eid , and look up the port the eid is using.
            if eid[0] == eid_endp[0] and eid[1] == eid_endp[1] and eid[2] == eid_endp[2]:
                lat += int(endp["delay"])
                jit += int(endp["jitter"])
                name = endp["name"]
                logger.debug("endp name {name}".format(name=name))
                sta_name = name.replace('-A', '')
                # only the -A endpoint will be found

                count += 1
                logger.debug(
                    "Matched: name: {name} eid:{eid} to endp-id {eid_endp}".format(
                        name=name, eid=eid, eid_endp=eid_endp))
            else:
                name = endp["name"]
                logger.debug(
                    "No Match: name: {name} eid:{eid} to endp-id {eid_endp}".format(
                        name=name, eid=eid, eid_endp=eid_endp))

        if count > 1:
            lat = int(lat / count)
            jit = int(jit / count)

        # need to loop though again to find the upload and download per station
        # if the name matched
        for endp in endps:
            if sta_name in endp["name"]:
                name = endp["name"]
                if name.endswith("-A"):
                    logger.info("name has -A")
                    total_dl_rate += int(endp["rx rate"])
                    total_dl_rate_ll += int(endp["rx rate ll"])
                    total_dl_pkts_ll += int(endp["rx pkts ll"])
                    dl_tx_drop_percent = round(endp["rx drop %"], 2)

                # -B upload side
                else:
                    total_ul_rate += int(endp["rx rate"])
                    total_ul_rate_ll += int(endp["rx rate ll"])
                    total_ul_pkts_ll += int(endp["rx pkts ll"])
                    ul_rx_drop_percent = round(endp["rx drop %"], 2)

        return lat, jit, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll, dl_rx_drop_percent, total_ul_rate, total_ul_rate_ll, total_ul_pkts_ll, ul_rx_drop_percent

    # Query all endpoints to generate rx and other stats, returned
    # as an array of objects.
    def __get_rx_values(self):
        endp_list = self.json_get(
            "endp?fields=name,eid,delay,jitter,rx+rate,rx+rate+ll,rx+bytes,rx+drop+%25,rx+pkts+ll",
            debug_=False)
        # multicast only shows tx rates
        # endp_list = self.json_get(
        #    "endp?fields=name,eid,delay,jitter,tx+rate,tx+rate+ll,tx+bytes,tx+drop+%25,tx+pkts+ll",
        #    debug_=False)

        endp_rx_drop_map = {}
        endp_rx_map = {}
        our_endps = {}
        endps = []

        total_ul = 0
        total_ul_ll = 0
        total_dl = 0
        total_dl_ll = 0

        # Multicast endpoints
        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e
        for endp_name in endp_list['endpoint']:
            logger.debug("endpoint: {}".format(endp_name))
            if endp_name != 'uri' and endp_name != 'handler':
                for item, endp_value in endp_name.items():
                    # multicast does not support use existing: or self.use_existing_station_lists:
                    if item in our_endps:
                        # endps.append(endp_value) need to see how to affect
                        # NOTE: during each monitor period the rates are added to get the totals
                        # this is done so that if there is an issue the rate information will be in
                        # the csv for the individual polling period
                        logger.debug(
                            "multicast endpoint: {item} value:\n".format(item=item))
                        logger.debug(endp_value)
                        for value_name, value in endp_value.items():
                            if value_name == 'rx rate':
                                # This hack breaks for mcast or if someone names endpoints weirdly.
                                # logger.info("item: ", item, " rx-bps: ", value_rx_bps)
                                if "-mrx-" in item:
                                    total_dl += int(value)
                                else:
                                    total_ul += int(value)
                            if value_name == 'rx rate ll':
                                # This hack breaks for mcast or if someone
                                # names endpoints weirdly.
                                if "-mrx-" in item:
                                    total_dl_ll += int(value)
                                else:
                                    total_ul_ll += int(value)

                            # TODO need a way to report rates

        # Unicast endpoints
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, endp_value in endp_name.items():
                    if item in our_endps or self.use_existing_station_lists:
                        endps.append(endp_value)
                        logger.debug(
                            "endpoint: {item} value:\n".format(item=item))
                        logger.debug(endp_value)

                        for value_name, value in endp_value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value
                            if value_name == 'rx rate':
                                endp_rx_map[item] = value
                            if value_name == 'rx rate ll':
                                endp_rx_map[item] = value
                            if value_name == 'rx pkts ll':
                                endp_rx_map[item] = value
                            if value_name == 'rx drop %':
                                endp_rx_drop_map[item] = value
                            if value_name == 'rx rate':
                                # This hack breaks for mcast or if someone names endpoints weirdly.
                                # logger.info("item: ", item, " rx-bps: ", value_rx_bps)
                                if item.endswith("-A"):
                                    total_dl += int(value)
                                elif item.endswith("-B"):
                                    total_ul += int(value)
                            if value_name == 'rx rate ll':
                                # This hack breaks for mcast or if someone
                                # names endpoints weirdly.
                                if item.endswith("-A"):
                                    total_dl_ll += int(value)
                                elif item.endswith("-B"):
                                    total_ul_ll += int(value)

        # logger.debug("total-dl: ", total_dl, " total-ul: ", total_ul, "\n")
        return endp_rx_map, endp_rx_drop_map, endps, total_dl, total_ul, total_dl_ll, total_ul_ll
    # This script supports resetting ports, allowing one to test AP/controller under data load
    # while bouncing wifi stations.  Check here to see if we should reset
    # ports.

    def reset_port_check(self):
        for station_profile in self.station_profiles:
            if station_profile.reset_port_extra_data['reset_port_enable']:
                if not station_profile.reset_port_extra_data['reset_port_timer_started']:
                    logger.debug(
                        "reset_port_timer_started {}".format(
                            station_profile.reset_port_extra_data['reset_port_timer_started']))
                    logger.debug(
                        "reset_port_time_min: {}".format(
                            station_profile.reset_port_extra_data['reset_port_time_min']))
                    logger.debug(
                        "reset_port_time_max: {}".format(
                            station_profile.reset_port_extra_data['reset_port_time_max']))
                    station_profile.reset_port_extra_data['seconds_till_reset'] = random.randint(
                        station_profile.reset_port_extra_data['reset_port_time_min'],
                        station_profile.reset_port_extra_data['reset_port_time_max'])
                    station_profile.reset_port_extra_data['reset_port_timer_started'] = True
                    logger.debug(
                        "on radio {} seconds_till_reset {}".format(
                            station_profile.add_sta_data['radio'],
                            station_profile.reset_port_extra_data['seconds_till_reset']))
                else:
                    station_profile.reset_port_extra_data[
                        'seconds_till_reset'] = station_profile.reset_port_extra_data['seconds_till_reset'] - 1
                    logger.debug(
                        "radio: {} countdown seconds_till_reset {}".format(
                            station_profile.add_sta_data['radio'],
                            station_profile.reset_port_extra_data['seconds_till_reset']))
                    if ((
                            station_profile.reset_port_extra_data['seconds_till_reset'] <= 0)):
                        station_profile.reset_port_extra_data['reset_port_timer_started'] = False
                        port_to_reset = random.randint(
                            0, len(station_profile.station_names) - 1)
                        logger.debug(
                            "reset on radio {} station: {}".format(
                                station_profile.add_sta_data['radio'],
                                station_profile.station_names[port_to_reset]))
                        self.reset_port(
                            station_profile.station_names[port_to_reset])

    # Common code to generate timestamp for CSV files.
    def time_stamp(self):
        return time.strftime('%m_%d_%Y_%H_%M_%S',
                             time.localtime(self.epoch_time))

    # Cleanup any older config that a previous run of this test may have
    # created.
    def pre_cleanup(self):
        '''
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.rm_port(sta, check_exists=True)
                self.total_stas += 1
        '''
        cleanup = lf_cleanup.lf_clean(
            host=self.lfclient_host, port=self.lfclient_port, resource='all')
        cleanup.sanitize_all()
        # Make sure they are gone
        count = 0
        while count < 10:
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.rm_port(sta, check_exists=True)
                    if rv:
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)

    def gather_port_eids(self):
        rv = [self.side_b]

        for station_profile in self.station_profiles:
            rv = rv + station_profile.station_names

        return rv

    # Create stations and connections/endpoints.  If rebuild is true, then
    # only update connections/endpoints.
    def build(self, rebuild=False):
        index = 0
        self.station_count = 0
        self.udp_endps = []
        self.tcp_endps = []
        self.eth_endps = []

        if rebuild:
            # if we are just re-applying new cx values, then no need to rebuild
            # stations, so allow skipping it.
            # Do clean cx lists so that when we re-apply them we get same endp name
            # as we had previously
            # logger.info("rebuild: Clearing cx profile lists.\n")
            self.cx_profile.clean_cx_lists()
            self.multicast_profile.clean_mc_lists()

        if self.dataplane:
            for etype in self.endp_types:
                for _tos in self.tos:
                    logger.info(
                        "Creating connections for endpoint type: %s TOS: %s  cx-count: %s" %
                        (etype, _tos, self.cx_profile.get_cx_count()))
                    # use brackes on [self.side_a] to make it a list
                    these_cx, these_endp = self.cx_profile.create(
                        endp_type=etype, side_a=[
                            self.side_a], side_b=self.side_b, sleep_time=0, tos=_tos)
                    if etype == "lf_udp" or etype == "lf_udp6":
                        self.udp_endps = self.udp_endps + these_endp
                    elif etype == "lf":
                        self.lf_endps = self.eth_endps + these_endp
                    else:
                        self.tcp_endps = self.tcp_endps + these_endp
                    # after we create cxs, append to global variable
                    self.cx_names.append(these_cx)

        else:
            for station_profile in self.station_profiles:
                if not rebuild and not self.use_existing_station_lists:
                    station_profile.use_security(
                        station_profile.security,
                        station_profile.ssid,
                        station_profile.ssid_pass)
                    station_profile.set_number_template(
                        station_profile.number_template)
                    logger.info(
                        "Creating stations on radio %s" %
                        (self.radio_name_list[index]))

                    station_profile.create(
                        radio=self.radio_name_list[index],
                        sta_names_=self.station_lists[index],
                        debug=self.debug,
                        sleep_time=0)
                    index += 1

                self.station_count += len(station_profile.station_names)

                # Build/update connection types
                for etype in self.endp_types:
                    # TODO multi cast does not work
                    if etype == "mc_udp" or etype == "mc_udp6":
                        # TODO add multicast to name be passed in 
                        for _tos in self.tos:
                            logger.info("Creating Multicast connections for endpoint type:  {etype} TOS: {tos}".format(
                                etype=etype, tos=_tos))
                            self.multicast_profile.create_mc_tx(
                                etype, self.side_b, tos=_tos, add_tos_to_name=True)
                            self.multicast_profile.create_mc_rx(
                                etype, side_rx=station_profile.station_names, tos=_tos, add_tos_to_name=True)
                    else:
                        for _tos in self.tos:
                            logger.info("Creating connections for endpoint type: {etype} TOS: {tos}  cx-count: {cx_count}".format(
                                etype=etype, tos=_tos, cx_count=self.cx_profile.get_cx_count()))
                            these_cx, these_endp = self.cx_profile.create(
                                endp_type=etype, side_a=station_profile.station_names, side_b=self.side_b, sleep_time=0, tos=_tos, add_tos_to_name=True)
                            if etype == "lf_udp" or etype == "lf_udp6":
                                self.udp_endps = self.udp_endps + these_endp
                            else:
                                self.tcp_endps = self.tcp_endps + these_endp
                            # after we create the cxs, append to global
                            self.cx_names.append(these_cx)

        self.cx_count = self.cx_profile.get_cx_count()

        if self.dataplane:
            self._pass(
                "PASS: CX build finished: created/updated:  %s connections." %
                self.cx_count)
        else:
            self._pass(
                "PASS: Stations & CX build finished: created/updated: %s stations and %s connections." %
                (self.station_count, self.cx_count))

    # Run the main body of the test logic.
    # todo there may be a need to start all existing stations on lanforge
    # sta_json = super().json_get(
    #   "port/1/{resource}/list?field=alias".format(resource=self.resource))['interfaces']

    def start(self, print_pass=False):
        logger.info("Bringing up stations")
        self.admin_up(self.side_b)
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                logger.info("Bringing up station %s" % sta)
                self.admin_up(sta)
        # TODO - Admin up existing stations
        if self.use_existing_station_lists:
            for existing_station in self.existing_station_lists:
                logger.info("Bringing up existing stations %s" %
                            existing_station)
                self.admin_up(existing_station)

        temp_stations_list = []
        # temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())

        # if self.use_existing_station_lists:
        #    # for existing_station in self.existing_station_lists:
        #    temp_stations_list.extend(self.existing_station_lists.copy())

        temp_stations_list_with_side_b = temp_stations_list.copy()
        # wait for b side to get IP
        temp_stations_list_with_side_b.append(self.side_b)
        logger.debug("temp_stations_list {temp_stations_list}".format(
            temp_stations_list=temp_stations_list))
        logger.debug("temp_stations_list_with_side_b {temp_stations_list_with_side_b}".format(
            temp_stations_list_with_side_b=temp_stations_list_with_side_b))

        if self.wait_for_ip(temp_stations_list_with_side_b, timeout_sec=self.wait_for_ip_sec):
            logger.info("ip's acquired")
        else:
            # No reason to continue
            logger.critical(
                "ERROR: print failed to get IP's Check station configuration SSID, Security, Is DHCP enabled exiting")
            exit(1)

        # self.csv_generate_column_headers()
        # logger.debug(csv_header)
        self.csv_add_column_headers()

        # dl - ports
        port_eids = self.gather_port_eids()
        # if self.use_existing_station_lists:
        #    port_eids.extend(self.existing_station_lists.copy())
        for port_eid in port_eids:
            self.csv_add_port_column_headers(
                port_eid, self.csv_generate_dl_port_column_headers())

        # ul -ports the csv will only be filled out if the
        # ap is read
        if self.ap_read:
            port_eids = self.gather_port_eids()
            # if self.use_existing_station_lists:
            #    port_eids.extend(self.existing_station_lists.copy())

            for port_eid in port_eids:
                self.csv_add_ul_port_column_headers(
                    port_eid, self.csv_generate_ul_port_column_headers())

        # looping though both A and B together,  upload direction will select A, download direction will select B
        # For each rate
        for ul, dl in itertools.zip_longest(
                self.side_a_min_rate,
                self.side_b_min_rate, fillvalue=256000):

            # For each pdu size
            for ul_pdu, dl_pdu in itertools.zip_longest(
                self.side_a_min_pdu,
                self.side_b_min_pdu, fillvalue='AUTO'
            ):

                # Adjust rate to take into account the number of connections we
                # have.
                if self.cx_count > 1 and self.rates_are_totals:
                    # Convert from string to int to do math, then back to string
                    # as that is what the cx_profile wants.
                    ul = str(int(int(ul) / self.cx_count))
                    dl = str(int(int(dl) / self.cx_count))

                dl_pdu_str = dl_pdu
                ul_pdu_str = ul_pdu

                if ul_pdu == "AUTO" or ul_pdu == "MTU":
                    ul_pdu = "-1"

                if dl_pdu == "AUTO" or dl_pdu == "MTU":
                    dl_pdu = "-1"

                logger.debug(
                    "ul: %s  dl: %s  cx-count: %s  rates-are-totals: %s\n" %
                    (ul, dl, self.cx_count, self.rates_are_totals))

                # Set rate and pdu size config
                self.cx_profile.side_a_min_bps = ul
                self.cx_profile.side_a_max_bps = ul
                self.cx_profile.side_b_min_bps = dl
                self.cx_profile.side_b_max_bps = dl

                self.cx_profile.side_a_min_pdu = ul_pdu
                self.cx_profile.side_a_max_pdu = ul_pdu
                self.cx_profile.side_b_min_pdu = dl_pdu
                self.cx_profile.side_b_max_pdu = dl_pdu

                # Multicast need to flow the same rates and pdu settings
                # the Min Tx Rate for the station needs to be zero
                self.multicast_profile.side_a_min_bps = 0
                self.multicast_profile.side_a_max_bps = 0

                self.multicast_profile.side_b_min_bps = dl
                self.multicast_profile.side_b_max_bps = dl

                self.multicast_profile.side_a_min_pdu = ul_pdu
                self.multicast_profile.side_a_max_pdu = ul_pdu
                self.multicast_profile.side_b_min_pdu = dl_pdu
                self.multicast_profile.side_b_max_pdu = dl_pdu

                self

                # Update connections with the new rate and pdu size config.
                self.build(rebuild=True)

                if self.ap_read:
                    for band in self.ap_band_list:
                        self.ap.clear_stats(band)

                for atten_val in self.atten_vals:
                    if atten_val != -1:
                        for atten_idx in self.attenuators:
                            atten_mod_test = lf_attenuator.CreateAttenuator(
                                host=self.lfclient_host, port=self.lfclient_port, serno='all', idx='all', val=atten_val, _debug_on=self.debug)
                            atten_mod_test.build()

                    logger.info(
                        "Starting multicast traffic (if any configured)")
                    self.multicast_profile.start_mc(debug_=self.debug)
                    self.multicast_profile.refresh_mc(debug_=self.debug)
                    logger.info("Starting layer-3 traffic (if any configured)")
                    self.cx_profile.start_cx()
                    self.cx_profile.refresh_cx()

                    cur_time = datetime.datetime.now()
                    logger.info("Getting initial values.")
                    self.__get_rx_values()

                    end_time = self.parse_time(self.test_duration) + cur_time

                    logger.info(
                        "Monitoring throughput for duration: %s" %
                        self.test_duration)

                    # Monitor test for the interval duration.
                    passes = 0
                    expected_passes = 0
                    warnings = 0
                    total_dl_bps = 0
                    total_ul_bps = 0
                    total_dl_ll_bps = 0
                    total_ul_ll_bps = 0
                    reset_timer = 0

                    while cur_time < end_time:
                        # interval_time = cur_time + datetime.timedelta(seconds=5)
                        interval_time = cur_time + \
                            datetime.timedelta(
                                seconds=self.polling_interval_seconds)
                        # logger.info("polling_interval_seconds {}".format(self.polling_interval_seconds))

                        while cur_time < interval_time:
                            cur_time = datetime.datetime.now()
                            time.sleep(.2)
                            reset_timer += 1
                            if reset_timer % 5 == 0:
                                self.reset_port_check()

                        self.epoch_time = int(time.time())
                        endp_rx_map, endp_rx_drop_map, endps, total_dl_bps, total_ul_bps, total_dl_ll_bps, total_ul_ll_bps = self.__get_rx_values()

                        log_msg = "main loop, total-dl: {total_dl_bps} total-ul: {total_ul_bps} total-dl-ll: {total_dl_ll_bps}".format(
                            total_dl_bps=total_dl_bps, total_ul_bps=total_ul_bps, total_dl_ll_bps=total_dl_ll_bps)

                        logger.debug(log_msg)

                        # AP OUTPUT
                        # call to AP to return values
                        # Query all of our ports
                        # Note: the endp eid is the
                        # shelf.resource.port.endp-id
                        if self.ap_read:
                            for band in self.ap_band_list:
                                # request the data to be read
                                self.ap.read_tx_dl_stats(band)
                                self.ap.read_rx_ul_stats(band)
                                self.ap.read_chanim_stats(band)

                            # Query all of ports
                            # Note: the endp eid is : shelf.resource.port.endp-id
                            port_eids = self.gather_port_eids()

                            for port_eid in port_eids:
                                eid = self.name_to_eid(port_eid)
                                url = "/port/%s/%s/%s" % (eid[0],
                                                          eid[1], eid[2])

                                # read LANforge to get the mac
                                response = self.json_get(url)
                                if (response is None) or ("interface" not in response):
                                    logger.info(
                                        "query-port: %s: incomplete response:" % url)
                                    logger.info(pformat(response))
                                else:
                                    # print("response".format(response))
                                    logger.info(pformat(response))
                                    port_data = response['interface']
                                    logger.info(
                                        "From LANforge: port_data, response['insterface']:{}".format(port_data))
                                    mac = port_data['mac']
                                    logger.debug("mac : {mac}".format(mac=mac))

                                    # search for data fro the port mac
                                    tx_dl_mac_found, ap_row_tx_dl = self.ap.tx_dl_stats(
                                        mac)
                                    rx_ul_mac_found, ap_row_rx_ul = self.ap.rx_ul_stats(
                                        mac)
                                    xtop_reported, ap_row_chanim = self.ap.chanim_stats(
                                        mac)

                                    self.get_endp_stats_for_port(
                                        port_data["port"], endps)

                                if tx_dl_mac_found:
                                    logger.info("mac {mac} ap_row_tx_dl {ap_row_tx_dl}".format(
                                        mac=mac, ap_row_tx_dl=ap_row_tx_dl))
                                    # Find latency, jitter for connections
                                    # using this port.
                                    latency, jitter, total_ul_rate, total_ul_rate_ll, total_ul_pkts_ll, ul_rx_drop_percent, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll, dl_rx_drop_percent = self.get_endp_stats_for_port(
                                        port_data["port"], endps)

                                    ap_row_tx_dl.append(ap_row_chanim)

                                    self.write_dl_port_csv(
                                        len(temp_stations_list),
                                        ul,
                                        dl,
                                        ul_pdu_str,
                                        dl_pdu_str,
                                        atten_val,
                                        port_eid,
                                        port_data,
                                        latency,
                                        jitter,
                                        total_ul_rate,
                                        total_ul_rate_ll,
                                        total_ul_pkts_ll,
                                        ul_rx_drop_percent,
                                        total_dl_rate,
                                        total_dl_rate_ll,
                                        total_dl_pkts_ll,
                                        dl_rx_drop_percent,
                                        ap_row_tx_dl)  # this is where the AP data is added

                                    # now report the ap_chanim_stats

                                if rx_ul_mac_found:
                                    # Find latency, jitter for connections
                                    # using this port.
                                    # latency, jitter, total_ul_rate, total_ul_rate_ll, total_ul_pkts_ll, ul_rx_drop_percent, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll, dl_tx_drop_percent = self.get_endp_stats_for_port(
                                    #    port_data["port"], endps)
                                    self.write_ul_port_csv(
                                        len(temp_stations_list),
                                        ul,
                                        dl,
                                        ul_pdu_str,
                                        dl_pdu_str,
                                        atten_val,
                                        port_eid,
                                        port_data,
                                        latency,
                                        jitter,
                                        total_ul_rate,
                                        total_ul_rate_ll,
                                        total_ul_pkts_ll,
                                        ul_rx_drop_percent,
                                        total_dl_rate,
                                        total_dl_rate_ll,
                                        total_dl_pkts_ll,
                                        dl_tx_drop_percent,
                                        ap_row_rx_ul)  # ap_ul_row added

                                logger.info("ap_row_rx_ul {ap_row_rx_ul}".format(
                                    ap_row_rx_ul=ap_row_rx_ul))

                        ####################################
                        else:
                            # NOT Reading the AP
                            port_eids = self.gather_port_eids()
                            if self.use_existing_station_lists:
                                port_eids.extend(
                                    self.existing_station_lists.copy())
                                # for existing_station in self.existing_station_lists:
                                #    port_eids.append(self.existing_station)
                            for port_eid in port_eids:
                                eid = self.name_to_eid(port_eid)
                                url = "/port/%s/%s/%s" % (eid[0],
                                                          eid[1], eid[2])
                                response = self.json_get(url)
                                if (response is None) or (
                                         "interface" not in response):
                                    logger.info(
                                        "query-port: %s: incomplete response:" % url)
                                    pprint(response)
                                else:
                                    port_data = response['interface']
                                    latency, jitter, total_ul_rate, total_ul_rate_ll, total_ul_pkts_ll, ul_rx_drop_percent, total_dl_rate, total_dl_rate_ll, total_dl_pkts_ll, dl_rx_drop_percent = self.get_endp_stats_for_port(
                                        port_data["port"], endps)
                                    self.write_dl_port_csv(
                                        len(temp_stations_list),
                                        ul,
                                        dl,
                                        ul_pdu_str,
                                        dl_pdu_str,
                                        atten_val,
                                        port_eid,
                                        port_data,
                                        latency,
                                        jitter,
                                        total_ul_rate,
                                        total_ul_rate_ll,
                                        total_ul_pkts_ll,
                                        ul_rx_drop_percent,
                                        total_dl_rate,
                                        total_dl_rate_ll,
                                        total_dl_pkts_ll,
                                        dl_rx_drop_percent)

                            # TODO add collect layer 3 data

                    # Write out download totals for each station
                    # port_eids= self.gather_port_eids()
                    # for port_eid in port_eids
                    # Collecting Totals of all stations for all intervals for each collection period
                    # TODO make all port csv files into one concatinated csv files
                    # Create empty dataframe
                    all_dl_ports_df = pd.DataFrame()
                    port_eids = self.gather_port_eids()
                    # if self.use_existing_station_lists:
                    #    port_eids.extend(self.existing_station_lists.copy())

                    for port_eid in port_eids:
                        logger.debug("port files: {port_file}".format(
                            port_file=self.dl_port_csv_files[port_eid]))
                        name = self.dl_port_csv_files[port_eid].name
                        logger.debug("name : {name}".format(name=name))
                        df_dl_tmp = pd.read_csv(name)
                        all_dl_ports_df = pd.concat(
                            [all_dl_ports_df, df_dl_tmp], axis=0)

                    all_dl_ports_file_name = self.outfile[:-4]
                    all_dl_port_file_name = all_dl_ports_file_name + "-dl-all-eids.csv"
                    all_dl_ports_df.to_csv(all_dl_port_file_name)

                    # process "-dl-all-eids.csv to have per iteration loops deltas"
                    all_dl_ports_df.to_csv(all_dl_port_file_name)

                    # copy the above pandas dataframe (all_dl_ports_df)
                    all_dl_ports_stations_df = all_dl_ports_df.copy(deep=True)
                    # drop rows that have eth
                    all_dl_ports_stations_df = all_dl_ports_stations_df[~all_dl_ports_stations_df['Name'].str.contains(
                        'eth')]
                    logger.info(pformat(all_dl_ports_stations_df))

                    # save to csv file
                    all_dl_ports_stations_file_name = self.outfile[:-4]
                    all_dl_port_stations_file_name = all_dl_ports_stations_file_name + \
                        "-dl-all-eids-stations.csv"
                    all_dl_ports_stations_df.to_csv(
                        all_dl_port_stations_file_name)

                    # we should be able to add the values for each eid
                    # FutureWarning: Indexing with multiple keys need to make single [] to double [[]]
                    # https://stackoverflow.com/questions/60999753/pandas-future-warning-indexing-with-multiple-keys
                    all_dl_ports_stations_sum_df = all_dl_ports_stations_df.groupby(['Time epoch'])[['Rx-Bps', 'Tx-Bps', 'Rx-Latency', 'Rx-Jitter',
                                                                                                    'Ul-Rx-Goodput-bps', 'Ul-Rx-Rate-ll', 'Ul-Rx-Pkts-ll', 'Dl-Rx-Goodput-bps', 'Dl-Rx-Rate-ll', 'Dl-Rx-Pkts-ll']].sum()
                    all_dl_ports_stations_sum_file_name = self.outfile[:-4]
                    all_dl_port_stations_sum_file_name = all_dl_ports_stations_sum_file_name + \
                        "-dl-all-eids-sum-per-interval.csv"

                    # add some calculations, will need some selectable graphs
                    logger.info("all_dl_ports_stations_sum_df : {df}".format(
                        df=all_dl_ports_stations_sum_df))

                    if all_dl_ports_stations_sum_df.empty:
                        logger.warning(
                            "The dl (download) has no data check the AP connection or configuration")
                        warnings += 1

                    else:
                        all_dl_ports_stations_sum_df['Rx-Bps-Diff'] = all_dl_ports_stations_sum_df['Rx-Bps'].diff(
                        )
                        all_dl_ports_stations_sum_df['Tx-Bps-Diff'] = all_dl_ports_stations_sum_df['Tx-Bps'].diff(
                        )
                        all_dl_ports_stations_sum_df['Rx-Latency-Diff'] = all_dl_ports_stations_sum_df['Rx-Latency'].diff()
                        all_dl_ports_stations_sum_df['Rx-Jitter-Diff'] = all_dl_ports_stations_sum_df['Rx-Jitter'].diff(
                        )
                        all_dl_ports_stations_sum_df['Ul-Rx-Goodput-bps-Diff'] = all_dl_ports_stations_sum_df['Ul-Rx-Goodput-bps'].diff()
                        all_dl_ports_stations_sum_df['Ul-Rx-Rate-ll-Diff'] = all_dl_ports_stations_sum_df['Ul-Rx-Rate-ll'].diff()
                        all_dl_ports_stations_sum_df['Ul-Rx-Pkts-ll-Diff'] = all_dl_ports_stations_sum_df['Ul-Rx-Pkts-ll'].diff()
                        all_dl_ports_stations_sum_df['Dl-Rx-Goodput-bps-Diff'] = all_dl_ports_stations_sum_df['Dl-Rx-Goodput-bps'].diff()
                        all_dl_ports_stations_sum_df['Dl-Rx-Rate-ll-Diff'] = all_dl_ports_stations_sum_df['Dl-Rx-Rate-ll'].diff()
                        all_dl_ports_stations_sum_df['Dl-Rx-Pkts-ll-Diff'] = all_dl_ports_stations_sum_df['Dl-Rx-Pkts-ll'].diff()

                    # write out the data
                    all_dl_ports_stations_sum_df.to_csv(
                        all_dl_port_stations_sum_file_name)

                    # if there are multiple loops then delete the df
                    del all_dl_ports_df

                    if self.ap_read:
                        # Consolidate all the ul ports into one file
                        # Create empty dataframe
                        all_ul_ports_df = pd.DataFrame()
                        port_eids = self.gather_port_eids()

                        for port_eid in port_eids:
                            logger.debug("ul port files: {port_file}".format(
                                port_file=self.ul_port_csv_files[port_eid]))
                            name = self.ul_port_csv_files[port_eid].name
                            logger.debug("name : {name}".format(name=name))
                            df_ul_tmp = pd.read_csv(name)
                            all_ul_ports_df = pd.concat(
                                [all_ul_ports_df, df_ul_tmp], axis=0)

                        all_ul_ports_file_name = self.outfile[:-4]
                        all_ul_port_file_name = all_ul_ports_file_name + "-ul-all-eids.csv"
                        all_ul_ports_df.to_csv(all_ul_port_file_name)

                        # copy over all_ul_ports_df so as create a dataframe summ of the data for each iteration
                        all_ul_ports_stations_df = all_ul_ports_df.copy(
                            deep=True)
                        # drop rows that have eth
                        all_ul_ports_stations_df = all_ul_ports_stations_df[~all_ul_ports_stations_df['Name'].str.contains(
                            'eth')]
                        logger.info(pformat(all_ul_ports_stations_df))

                        # save to csv
                        all_ul_ports_stations_file_name = self.outfile[:-4]
                        all_ul_ports_stations_file_name = all_ul_ports_stations_file_name + \
                            "-ul-all-eids-stations.csv"
                        all_ul_ports_stations_df.to_csv(
                            all_ul_ports_stations_file_name)

                        # we add all the values based on the epoch time
                        # FutureWarning: Indexing with multiple keys need to make single [] to double [[]]
                        # https://stackoverflow.com/questions/60999753/pandas-future-warning-indexing-with-multiple-keys
                        all_ul_ports_stations_sum_df = all_dl_ports_stations_df.groupby(['Time epoch'])[['Rx-Bps', 'Tx-Bps', 'Rx-Latency', 'Rx-Jitter',
                                                                                                        'Ul-Rx-Goodput-bps', 'Ul-Rx-Rate-ll', 'Ul-Rx-Pkts-ll', 'Dl-Rx-Goodput-bps', 'Dl-Rx-Rate-ll', 'Dl-Rx-Pkts-ll']].sum()
                        all_ul_ports_stations_sum_file_name = self.outfile[:-4]
                        all_ul_port_stations_sum_file_name = all_ul_ports_stations_sum_file_name + \
                            "-ul-all-eids-sum-per-interval.csv"

                        # add some calculations, will need some selectable graphs
                        if all_ul_ports_stations_sum_df.empty:
                            logger.warning(
                                "The ul (upload) has no data check the AP connection or configuration")
                            warnings += 1
                        else:
                            all_ul_ports_stations_sum_df['Rx-Bps-Diff'] = all_ul_ports_stations_sum_df['Rx-Bps'].diff(
                            )
                            all_ul_ports_stations_sum_df['Tx-Bps-Diff'] = all_ul_ports_stations_sum_df['Tx-Bps'].diff(
                            )
                            all_ul_ports_stations_sum_df['Rx-Latency-Diff'] = all_ul_ports_stations_sum_df['Rx-Latency'].diff(
                            )
                            all_ul_ports_stations_sum_df['Rx-Jitter-Diff'] = all_ul_ports_stations_sum_df['Rx-Jitter'].diff(
                            )
                            all_ul_ports_stations_sum_df['Ul-Rx-Goodput-bps-Diff'] = all_ul_ports_stations_sum_df['Ul-Rx-Goodput-bps'].diff(
                            )
                            all_ul_ports_stations_sum_df['Ul-Rx-Rate-ll-Diff'] = all_ul_ports_stations_sum_df['Ul-Rx-Rate-ll'].diff(
                            )
                            all_ul_ports_stations_sum_df['Ul-Rx-Pkts-ll-Diff'] = all_ul_ports_stations_sum_df['Ul-Rx-Pkts-ll'].diff(
                            )
                            all_ul_ports_stations_sum_df['Dl-Rx-Goodput-bps-Diff'] = all_ul_ports_stations_sum_df['Dl-Rx-Goodput-bps'].diff(
                            )
                            all_ul_ports_stations_sum_df['Dl-Rx-Rate-ll-Diff'] = all_ul_ports_stations_sum_df['Dl-Rx-Rate-ll'].diff(
                            )
                            all_ul_ports_stations_sum_df['Dl-Rx-Pkts-ll-Diff'] = all_ul_ports_stations_sum_df['Dl-Rx-Pkts-ll'].diff(
                            )

                        # write out the data
                        all_ul_ports_stations_sum_df.to_csv(
                            all_ul_port_stations_sum_file_name)

                        # if there are multiple loops then delete the df
                        del all_ul_ports_df

                    # At end of test step, record KPI into kpi.csv
                    self.record_kpi_csv(
                        len(temp_stations_list),
                        ul,
                        dl,
                        ul_pdu_str,
                        dl_pdu_str,
                        atten_val,
                        total_dl_bps,
                        total_ul_bps,
                        total_dl_ll_bps,
                        total_ul_ll_bps)

                    # At end of test step, record results information. This is
                    self.record_results_total(
                        len(temp_stations_list),
                        ul,
                        dl,
                        ul_pdu_str,
                        dl_pdu_str,
                        atten_val,
                        total_dl_bps,
                        total_ul_bps,
                        total_dl_ll_bps,
                        total_ul_ll_bps)

                    # At end of test if requested store upload and download
                    # stats  TODO add for AP
                    # there is a specifi stop() method
                    # Stop connections.
                    # There is a specific stop
                    # self.cx_profile.stop_cx()
                    # self.multicast_profile.stop_mc()
                    # TODO the passes and expected_passes are not checking anything
                    if warnings > 0:
                        self._fail(" Total warnings:  {warnings}.   Check logs for warnings,  check AP connection ".format(
                            warnings=str(warnings)))

                    if passes == expected_passes:
                        # Sets the pass indication
                        self._pass(
                            "PASS: Requested-Rate: %s <-> %s  PDU: %s <-> %s   All tests passed" %
                            (ul, dl, ul_pdu, dl_pdu), print_pass)

    def write_dl_port_csv(
            self,
            sta_count,
            ul,
            dl,
            ul_pdu,
            dl_pdu,
            atten,
            port_eid,
            port_data,
            latency,
            jitter,
            total_ul_rate,
            total_ul_rate_ll,
            total_ul_pkts_ll,
            ul_rx_drop_percent,
            total_dl_rate,
            total_dl_rate_ll,
            total_dl_pkts_ll,
            dl_rx_drop_percent,
            ap_row_tx_dl=''):
        row = [self.epoch_time, self.time_stamp(), sta_count,
               ul, ul, dl, dl, dl_pdu, dl_pdu, ul_pdu, ul_pdu,
               atten, port_eid
               ]

        row = row + [port_data['bps rx'],
                     port_data['bps tx'],
                     port_data['rx-rate'],
                     port_data['tx-rate'],
                     port_data['signal'],
                     port_data['ap'],
                     port_data['mode'],
                     port_data['mac'],
                     port_data['channel'],
                     latency,
                     jitter,
                     total_ul_rate,
                     total_ul_rate_ll,
                     total_ul_pkts_ll,
                     ul_rx_drop_percent,
                     total_dl_rate,
                     total_dl_rate_ll,
                     total_dl_pkts_ll,
                     dl_rx_drop_percent]

        # Add in info queried from AP.
        if self.ap_read:
            if len(ap_row_tx_dl) == len(self.ap_stats_dl_col_titles):
                # print("ap_row {}".format(ap_row))
                for col in ap_row_tx_dl:
                    # print("col {}".format(col))
                    row.append(col)

        writer = self.dl_port_csv_writers[port_eid]
        writer.writerow(row)
        self.dl_port_csv_files[port_eid].flush()

    def write_ul_port_csv(
            self,
            sta_count,
            ul,
            dl,
            ul_pdu,
            dl_pdu,
            atten,
            port_eid,
            port_data,
            latency,
            jitter,
            total_ul_rate,
            total_ul_rate_ll,
            total_ul_pkts_ll,
            ul_rx_drop_percent,
            total_dl_rate,
            total_dl_rate_ll,
            total_dl_pkts_ll,
            dl_tx_drop_percent,
            ap_row_rx_ul):
        row = [self.epoch_time, self.time_stamp(), sta_count,
               ul, ul, dl, dl, dl_pdu, dl_pdu, ul_pdu, ul_pdu,
               atten, port_eid
               ]

        row = row + [port_data['bps rx'],
                     port_data['bps tx'],
                     port_data['rx-rate'],
                     port_data['tx-rate'],
                     port_data['signal'],
                     port_data['ap'],
                     port_data['mode'],
                     port_data['mac'],
                     port_data['channel'],
                     latency,
                     jitter,
                     total_ul_rate,
                     total_ul_rate_ll,
                     total_ul_pkts_ll,
                     ul_rx_drop_percent,
                     total_dl_rate,
                     total_dl_rate_ll,
                     total_dl_pkts_ll,
                     dl_tx_drop_percent]

        # print("ap_row length {} col_titles length {}".format(len(ap_row),len(self.ap_stats_col_titles)))
        # print("self.ap_stats_col_titles {} ap_stats_col_titles {}".format(self.ap_stats_col_titles,ap_stats_col_titles))
        # Add in info queried from AP.
        if self.ap_read:
            logger.debug("ap_row_rx_ul len {ap_row_rx_ul_len} ap_stats_ul_col_titles len {rx_col_len} ap_ul_row {ap_ul_row}".format(
                ap_row_rx_ul_len=len(ap_row_rx_ul), rx_col_len=len(self.ap_stats_ul_col_titles), ap_ul_row=ap_row_rx_ul))
            if len(ap_row_rx_ul) == len(self.ap_stats_ul_col_titles):
                logger.debug("ap_row_rx_ul {}".format(ap_row_rx_ul))
                for col in ap_row_rx_ul:
                    logger.debug("col {}".format(col))
                    row.append(col)

        writer = self.ul_port_csv_writers[port_eid]
        writer.writerow(row)
        self.ul_port_csv_files[port_eid].flush()

    def record_kpi_csv(
            self,
            sta_count,
            ul,
            dl,
            ul_pdu,
            dl_pdu,
            atten,
            total_dl_bps,
            total_ul_bps,
            total_dl_ll_bps,
            total_ul_ll_bps):

        logger.debug("NOTE:  Adding kpi to kpi.csv, sta_count {sta_count}  total-download-bps:{total_dl_bps}  upload: {total_ul_bps}  bi-directional: {total}\n".format(
            sta_count=sta_count, total_dl_bps=total_dl_bps, total_ul_bps=total_ul_bps, total=(total_ul_bps + total_dl_bps)))

        logger.debug("NOTE:  Adding kpi to kpi.csv, sta_count {sta_count}  total-download-bps:{total_dl_ll_bps}  upload: {total_ul_ll_bps}  bi-directional: {total_ll}\n".format(
            sta_count=sta_count, total_dl_ll_bps=total_dl_ll_bps, total_ul_ll_bps=total_ul_ll_bps, total_ll=(total_ul_ll_bps + total_dl_ll_bps)))

        # the short description will all for more data to show up in one
        # test-tag graph

        results_dict = self.kpi_csv.kpi_csv_get_dict_update_time()
        results_dict['Graph-Group'] = "Per Stations Rate DL"
        results_dict['short-description'] = "DL {dl} bps  pdu {dl_pdu}  {sta_count} STA".format(
            dl=dl, dl_pdu=dl_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(total_dl_bps)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        results_dict['Graph-Group'] = "Per Stations Rate UL"
        results_dict['short-description'] = "UL {ul} bps pdu {ul_pdu} {sta_count} STA".format(
            ul=ul, ul_pdu=ul_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(total_ul_bps)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        results_dict['Graph-Group'] = "Per Stations Rate UL+DL"
        results_dict['short-description'] = "UL {ul} bps pdu {ul_pdu} + DL {dl} bps pud {dl_pdu}- {sta_count} STA".format(
            ul=ul, ul_pdu=ul_pdu, dl=dl, dl_pdu=dl_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(
            (total_ul_bps + total_dl_bps))
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        results_dict['Graph-Group'] = "Per Stations Rate DL"
        results_dict['short-description'] = "DL LL {dl} bps  pdu {dl_pdu}  {sta_count} STA".format(
            dl=dl, dl_pdu=dl_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(total_dl_ll_bps)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        results_dict['Graph-Group'] = "Per Stations Rate UL"
        results_dict['short-description'] = "UL LL {ul} bps pdu {ul_pdu} {sta_count} STA".format(
            ul=ul, ul_pdu=ul_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(total_ul_ll_bps)
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

        results_dict['Graph-Group'] = "Per Stations Rate UL+DL"
        results_dict['short-description'] = "UL LL {ul} bps pdu {ul_pdu} + DL LL {dl} bps pud {dl_pdu}- {sta_count} STA".format(
            ul=ul, ul_pdu=ul_pdu, dl=dl, dl_pdu=dl_pdu, sta_count=sta_count)
        results_dict['numeric-score'] = "{}".format(
            (total_ul_ll_bps + total_dl_ll_bps))
        results_dict['Units'] = "bps"
        self.kpi_csv.kpi_csv_write_dict(results_dict)

    # Results csv
    def record_results_total(
            self,
            sta_count,
            ul,
            dl,
            ul_pdu,
            dl_pdu,
            atten,
            total_dl_bps,
            total_ul_bps,
            total_dl_ll_bps,
            total_ul_ll_bps):

        tags = dict()
        tags['requested-ul-bps'] = ul
        tags['requested-dl-bps'] = dl
        tags['ul-pdu-size'] = ul_pdu
        tags['dl-pdu-size'] = dl_pdu
        tags['station-count'] = sta_count
        tags['attenuation'] = atten
        tags["script"] = 'test_l3'

        # Add user specified tags
        for k in self.user_tags:
            tags[k[0]] = k[1]

        if self.csv_results_file:
            row = [self.epoch_time, self.time_stamp(), sta_count,
                   ul, ul, dl, dl, dl_pdu, dl_pdu, ul_pdu, ul_pdu,
                   atten,
                   total_dl_bps, total_ul_bps, (total_ul_bps + total_dl_bps),
                   total_dl_ll_bps, total_ul_ll_bps, (
                       total_ul_ll_bps + total_dl_ll_bps)
                   ]
            # Add values for any user specified tags
            for k in self.user_tags:
                row.append(k[1])

            self.csv_results_writer.writerow(row)
            self.csv_results_file.flush()


    def evaluate_qos(self):
        # for port: 
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.104:8080/port/all | json_pp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.103:8080/port/all?fields=alias,mac,channel,bps+rx,rx-rate,bps+tx,tx-rate | json_pp

        # for endp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.104:8080/endp/all | json_pp
        # curl --user "lanforge:lanforge" -H 'Accept: application/json' http://192.168.0.104:8080/endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,tos | json_pp

        # gather port data
        # TODO 
        self.port_data = self.json_get('port/all?fields=alias,port,mac,channel,mode,bps+rx,rx-rate,bps+tx,tx-rate')
        #self.port_data = self.json_get('port/all')
        self.port_data.pop("handler")
        self.port_data.pop("uri")
        self.port_data.pop("warnings")
        logger.info("self.port_data type: {dtype} data: {data}".format(dtype=type(self.port_data), data=self.port_data))


        self.resourse_data = self.json_get('resource/all?fields=hostname,hw+version')
        # self.resourse_data = self.json_get('resource/all')
        self.resourse_data.pop("handler")
        self.resourse_data.pop("uri")
        # self.resourse_data.pop("warnings")
        logger.info("self.port_data type: {dtype} data: {data}".format(dtype=type(self.port_data), data=self.port_data))


        # Note will type will only work for 5.4.7
        # gather endp data
        endp_type_present = False
        try:
            self.endp_data = self.json_get('endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,tos,eid,type')
            endp_type_present = True
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.info("Consider upgrading to 5.4.7 + endp field type not supported in LANforge GUI version results for Multicast reversed in graphs and tables")
            self.endp_data = self.json_get('endp/all?fields=name,tx+rate+ll,tx+rate,rx+rate+ll,rx+rate,a/b,tos,eid')

        self.endp_data.pop("handler")
        self.endp_data.pop("uri")
        logger.info("self.endpoint_data type: {dtype} data: {data}".format(
            dtype=type(self.endp_data), data=self.endp_data))
        # self.side_b_min_bps= str(str(int(self.cx_profile.side_b_min_bps) / 1000000) +' '+'Mbps')
        # self.side_a_min_bps= str(str(int(self.cx_profile.side_a_min_bps) / 1000000) +' '+'Mbps')

        self.side_b_min_bps = self.cx_profile.side_b_min_bps
        self.side_a_min_bps = self.cx_profile.side_a_min_bps

        for endp_data in self.endp_data['endpoint']:
            logger.info("endp_data type {endp_type} endp_data {endp_data}".format(
                endp_type=type(endp_data), endp_data=endp_data))
            # The dictionary only has one key
            endp_data_key = list(endp_data.keys())[0]
            logger.info("endpoint_data key: {key}  name: {name} a/b {ab} rx rate {rx_rate}".format(
                key=endp_data_key, tos=endp_data[endp_data_key]['tos'], name=endp_data[endp_data_key]['name'], ab=endp_data[endp_data_key]['a/b'], rx_rate=endp_data[endp_data_key]['rx rate']))

            # Gather data for upload , download for the four data types BK, BE, VI, VO, place the
            # the data_set will be the upload and download rates for each client
            # the y_axis values are the clients
            # TODO how many data sets
            # for multicast upstream is A
            # for unicast the upstream is B

            
            # multi cast A side is upstream  Being explicite with code coudl have been done with arrays, yet wanted the code to be
            # maintainable
            if endp_type_present:
                if endp_data[endp_data_key]['type'] == 'Mcast':
                    if endp_data[endp_data_key]['tos'] == 'BK':
                        # for multicast the logic is reversed. A is upstream, B is downstream
                        # for stations the B is upstream and A is downstream
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_A.append(endp_data[endp_data_key]['type'])

                            # use the eid to get the hostname and channel
                            # todo eid_temp shows 1.1;
                            eid_tmp_resourse = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[0])+'.'+str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resourse
                            resource_found = False
                            for resource_data in self.resourse_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resourse:
                                    resource_found = True
                                    self.bk_resourse_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resourse_hw_ver_A.append(resource_data[resource_data_key]['hw version'])

                            if resource_found is False:
                                self.bk_resourse_host_A.append('NA')
                                self.bk_resourse_hw_ver_A.append('NA')

                            # look up port information
                            eid_info =  endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resourse+'.'+eid_info[3]
                            
                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append(endp_data[endp_data_key]['tos'] )
                                    self.bk_port_offered_rx_rate_A.append("NA")
                                    self.bk_port_offered_tx_rate_A.append("NA")
                                    
                                    try:
                                        self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    except:                                        
                                        #self.bk_port_channel_A.append(port_data[port_data_key]['channel'])
                                        self.bk_port_channel_A.append('NA')

                                    port_found = True

                            if port_found is False:
                                    self.bk_port_mac_A.append('NA')
                                    self.bk_port_mode_A.append('NA')
                                    # self.bk_port_observed_rx_rate_A.append("NA")
                                    # self.bk_port_observed_tx_rate_A.append("NA")
                                    self.bk_port_traffic_type_A.append("NA")
                                    self.bk_port_protocol_A.append("NA")
                                    self.bk_port_offered_rx_rate_A.append("NA")
                                    self.bk_port_offered_tx_rate_A.append("NA")



                        # for multicast the logic is reversed. A is upstream, B is downstream
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_B.append(endp_data[endp_data_key]['type'])


                    elif endp_data[endp_data_key]['tos'] == 'BE':
                        # for multicast the logic is reversed. A is upstream
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                    elif endp_data[endp_data_key]['tos'] == 'VI':
                        # for multicast the logic is reversed. A is upstream, B is downstream
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])


                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                    elif endp_data[endp_data_key]['tos'] == 'VO':
                        # for multicast the logic is reversed. A is upstream, B is downstream
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
                # for unicast the upstream is B and downstream is A 
                # note for B tx is download and rx is uploat
                elif endp_data[endp_data_key]['type'] == 'LF/TCP' or endp_data[endp_data_key]['type'] == 'LF/UDP' :
                    if endp_data[endp_data_key]['tos'] == 'BK':
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                            self.bk_port_protocol_A.append(endp_data[endp_data_key]['type'])


                            eid_tmp_resourse = str(self.name_to_eid(endp_data[endp_data_key]['eid'])[0])+'.'+str(self.name_to_eid(endp_data[endp_data_key]['eid'])[1])
                            # look up the resourse may need to have try except to handle cases where there is an issue getting data
                            resource_found = False
                            for resource_data in self.resourse_data['resources']:
                                resource_data_key = list(resource_data.keys())[0]
                                if resource_data_key == eid_tmp_resourse:
                                    resource_found = True
                                    self.bk_resourse_host_A.append(resource_data[resource_data_key]['hostname'])
                                    self.bk_resourse_hw_ver_A.append(resource_data[resource_data_key]['hw version'])

                            if resource_found is False:
                                self.bk_resourse_host_A.append('NA')
                                self.bk_resourse_hw_ver_A.append('NA')

                            # look up port information
                            eid_info =  endp_data[endp_data_key]['name'].split('-')
                            eid_tmp_port = eid_tmp_resourse+'.'+eid_info[1]
                            
                            port_found = False
                            self.bk_port_eid_A.append(eid_tmp_port)
                            for port_data in self.port_data['interfaces']:
                                port_data_key = list(port_data.keys())[0]
                                if port_data_key == eid_tmp_port:
                                    self.bk_port_mac_A.append(port_data[port_data_key]['mac'])
                                    self.bk_port_mode_A.append(port_data[port_data_key]['mode'])
                                    self.bk_port_traffic_type_A.append(endp_data[endp_data_key]['tos'] )
                                    self.bk_port_offered_rx_rate_A.append("NA")
                                    self.bk_port_offered_tx_rate_A.append("NA")
                                    
                                    try:
                                        self.bk_port_channel_A.append(port_data[port_data_key]["channel"])
                                    except:                                        
                                        #self.bk_port_channel_A.append(port_data[port_data_key]['channel'])
                                        self.bk_port_channel_A.append('NA')


                                    port_found = True
                            if port_found is False:
                                    self.bk_port_mac_A.append('NA')
                                    self.bk_port_mode_A.append('NA')
                                    # self.bk_port_observed_rx_rate_A.append("NA")
                                    # self.bk_port_observed_tx_rate_A.append("NA")
                                    self.bk_port_traffic_type_A.append("NA")
                                    self.bk_port_protocol_A.append("NA")
                                    self.bk_port_offered_rx_rate_A.append("NA")
                                    self.bk_port_offered_tx_rate_A.append("NA")


                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                            self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                    elif endp_data[endp_data_key]['tos'] == 'BE':
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.be_clients_A.append(endp_data[endp_data_key]['name'])
                            self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.be_clients_B.append(endp_data[endp_data_key]['name'])
                            self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                    elif endp_data[endp_data_key]['tos'] == 'VI':
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                    elif endp_data[endp_data_key]['tos'] == 'VO':
                        if endp_data[endp_data_key]['a/b'] == "A":
                            self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                        if endp_data[endp_data_key]['a/b'] == "B":
                            self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                            self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                            self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])
            else:
                if endp_data[endp_data_key]['tos'] == 'BK':
                    if endp_data[endp_data_key]['a/b'] == "A":
                        self.bk_clients_A.append(endp_data[endp_data_key]['name'])
                        self.bk_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                        self.bk_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                    if endp_data[endp_data_key]['a/b'] == "B":
                        self.bk_clients_B.append(endp_data[endp_data_key]['name'])
                        self.bk_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                        self.bk_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                elif endp_data[endp_data_key]['tos'] == 'BE':
                    if endp_data[endp_data_key]['a/b'] == "A":
                        self.be_clients_A.append(endp_data[endp_data_key]['name'])
                        self.be_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                        self.be_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                    if endp_data[endp_data_key]['a/b'] == "B":
                        self.be_clients_B.append(endp_data[endp_data_key]['name'])
                        self.be_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                        self.be_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                elif endp_data[endp_data_key]['tos'] == 'VI':
                    if endp_data[endp_data_key]['a/b'] == "A":
                        self.vi_clients_A.append(endp_data[endp_data_key]['name'])
                        self.vi_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                        self.vi_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                    if endp_data[endp_data_key]['a/b'] == "B":
                        self.vi_clients_B.append(endp_data[endp_data_key]['name'])
                        self.vi_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                        self.vi_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])

                elif endp_data[endp_data_key]['tos'] == 'VO':
                    if endp_data[endp_data_key]['a/b'] == "A":
                        self.vo_clients_A.append(endp_data[endp_data_key]['name'])
                        self.vo_tos_ul_A.append(endp_data[endp_data_key]["tx rate"])
                        self.vo_tos_dl_A.append(endp_data[endp_data_key]["rx rate"])
                    if endp_data[endp_data_key]['a/b'] == "B":
                        self.vo_clients_B.append(endp_data[endp_data_key]['name'])
                        self.vo_tos_dl_B.append(endp_data[endp_data_key]["tx rate"])
                        self.vo_tos_ul_B.append(endp_data[endp_data_key]["rx rate"])



        self.client_dict_A = {
            "y_axis_name": "Client names",
            "x_axis_name": "Throughput in Mbps",
            "min_bps_a": self.side_a_min_bps,
            "min_bps_b": self.side_b_min_bps,
            "BK": {
                "colors": ['orange', 'wheat'],
                "labels": ['Upload','Download'],

                # A side
                "clients_A": self.bk_clients_A,
                "ul_A": self.bk_tos_ul_A,
                "dl_A": self.bk_tos_dl_A,
                "resourse_A": self.bk_resourse_host_A,
                "port_A": self.bk_port_eid_A,
                "mac_A": self.bk_port_mac_A,
                "channel_A": self.bk_port_channel_A,
                "mode_A": self.bk_port_mode_A,
                "traffic_type_A": self.bk_port_traffic_type_A,
                "traffic_protocol_A": self.bk_port_protocol_A,
                "offered_download_rate_A" : self.bk_port_offered_rx_rate_A,
                "offered_upload_rate_A" : self.bk_port_offered_tx_rate_A,

                # B side
                "clients_B": self.bk_clients_B,
                "ul_B": self.bk_tos_ul_B,
                "dl_B": self.bk_tos_dl_B,
                "resourse_B": self.bk_resourse_host_B,
                "port_B": self.bk_port_eid_B,
                "mac_B": self.bk_port_mac_B,
                "channel_B": self.bk_port_channel_B,
                "mode_B": self.bk_port_mode_B,
                "traffic_type_B": self.bk_port_traffic_type_B,
                "traffic_protocol_B": self.bk_port_protocol_B,
                "offered_download_rate_B" : self.bk_port_offered_rx_rate_B,
                "offered_upload_rate_B" : self.bk_port_offered_tx_rate_B,

            },
            "BE": {
                "colors": ['lightcoral', 'mistyrose'],
                "labels": ['Upload','Download'],

                # A side
                "clients_A": self.be_clients_A,
                "ul_A": self.be_tos_ul_A,
                "dl_A": self.be_tos_dl_A,
                "resourse_A": self.be_resourse_host_A,
                "port_A": self.be_port_eid_A,
                "mac_A": self.be_port_mac_A,
                "channel_A": self.be_port_channel_A,
                "mode_A": self.be_port_mode_A,
                "traffic_type_A": self.be_port_traffic_type_A,
                "traffic_protocol_A": self.be_port_protocol_A,
                "offered_download_rate_A" : self.be_port_offered_rx_rate_A,
                "offered_upload_rate_A" : self.be_port_offered_tx_rate_A,

                # B side
                "clients_B": self.be_clients_B,
                "ul_B": self.be_tos_ul_B,
                "dl_B": self.be_tos_dl_B,
                "resourse_B": self.be_resourse_host_B,
                "port_B": self.be_port_eid_B,
                "mac_B": self.be_port_mac_B,
                "channel_B": self.be_port_channel_B,
                "mode_B": self.be_port_mode_B,
                "traffic_type_B": self.be_port_traffic_type_B,
                "traffic_protocol_B": self.be_port_protocol_B,
                "offered_download_rate_B" : self.be_port_offered_rx_rate_B,
                "offered_upload_rate_B" : self.be_port_offered_tx_rate_B,

            },
            "VI": {
                "colors": ['steelblue', 'lightskyblue'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vi_clients_A,
                "ul_A": self.vi_tos_ul_A,
                "dl_A": self.vi_tos_dl_A,
                "resourse_A": self.vi_resourse_host_A,
                "port_A": self.vi_port_eid_A,
                "mac_A": self.vi_port_mac_A,
                "channel": self.vi_port_channel_A,
                "mode": self.vi_port_mode_A,
                "traffic_type": self.vi_port_traffic_type_A,
                "traffic_protocol": self.vi_port_protocol_A,
                "offered_download_rate" : self.vi_port_offered_rx_rate_A,
                "offered_upload_rate" : self.vi_port_offered_tx_rate_A,

                # B side
                "clients_B": self.vi_clients_B,
                "ul_B": self.vi_tos_ul_B,
                "dl_B": self.vi_tos_dl_B,
                "resourse": self.vi_resourse_host_B,
                "port": self.vi_port_eid_B,
                "mac": self.vi_port_mac_B,
                "channel": self.vi_port_channel_B,
                "mode": self.vi_port_mode_B,
                "traffic_type": self.vi_port_traffic_type_B,
                "traffic_protocol": self.vi_port_protocol_B,
                "offered_download_rate" : self.vi_port_offered_rx_rate_B,
                "offered_upload_rate" : self.vi_port_offered_tx_rate_B,

            },
            "VO": {
                "colors": ['green', 'lightgreen'],
                "labels": ['Upload', 'Download'],

                # A side
                "clients_A": self.vo_clients_A,
                "ul_A": self.vo_tos_ul_A,
                "dl_A": self.vo_tos_dl_A,
                "resourse": self.vo_resourse_host_A,
                "port": self.vo_port_eid_A,
                "mac": self.vo_port_mac_A,
                "channel": self.vo_port_channel_A,
                "mode": self.vo_port_mode_A,
                "traffic_type": self.vo_port_traffic_type_A,
                "traffic_protocol": self.vo_port_protocol_A,
                "offered_download_rate" : self.vo_port_offered_rx_rate_A,
                "offered_upload_rate" : self.vo_port_offered_tx_rate_A,

                # B side
                "clients_B": self.vo_clients_B,
                "ul_B": self.vo_tos_ul_B,
                "dl_B": self.vo_tos_dl_B,
                "resourse": self.vo_resourse_host_B,
                "port": self.vo_port_eid_B,
                "mac": self.vo_port_mac_B,
                "channel": self.vo_port_channel_B,
                "mode": self.vo_port_mode_B,
                "traffic_type": self.vo_port_traffic_type_B,
                "traffic_protocol": self.vo_port_protocol_B,
                "offered_download_rate" : self.vo_port_offered_rx_rate_B,
                "offered_upload_rate" : self.vo_port_offered_tx_rate_B,

            }
        }

        '''        
        self.client_table_dict = {
            "y_axis_name": "Client names",
            "x_axis_name": "Throughput in Mbps",
            "min_bps_a": self.side_a_min_bps,
            "min_bps_b": self.side_b_min_bps,
            "BK": {
                "colors": ['orange', 'wheat'],
                "labels": ['Upload','Download'],

                # side A
                "clients_A": self.bk_clients_A,
                "ul_A": self.bk_tos_ul_A,
                "dl_A": self.bk_tos_dl_A,
                "ports_A": self.bk_port_eid_A,
                "mac_A":   self.bk_port_mac_A,
                "channel_A": self.bk_port_channel_A,
                "mode_A": self.bk_port_mode_A,
                "traffic_type_A": self.bk_port_traffic_type_A,
                "traffic_protocol_A": self.bk_port_protocol_A,

                # side B
                "clients_B": self.bk_clients_B,
                "ul_B": self.bk_tos_ul_B,
                "dl_B": self.bk_tos_dl_B,
                "ports_B": self.bk_port_eid_B,
                "mac_B":   self.bk_port_mac_B,
                "channel_B": self.bk_port_channel_B,
                "mode_B": self.bk_port_mode_B,
                "traffic_type_B": self.bk_port_traffic_type_B,
                "traffic_protocol_B": self.bk_port_protocol_B
            },
            "BE": {
                "colors": ['lightcoral', 'mistyrose'],
                "labels": ['Upload','Download'],

                # side A
                "clients_A": self.be_clients_A,
                "ul_A": self.be_tos_ul_A,
                "dl_A": self.be_tos_dl_A,
                "ports_A": self.be_port_eid_A,
                "mac_A":   self.be_port_mac_A,
                "channel_A": self.be_port_channel_A,
                "mode_A": self.be_port_mode_A,
                "traffic_type_A": self.be_port_traffic_type_A,
                "traffic_protocol_A": self.be_port_protocol_A,

                # side B
                "clients_B": self.be_clients_B,
                "ul_B": self.be_tos_ul_B,
                "dl_B": self.be_tos_dl_B,
                "ports_B": self.be_port_eid_B,
                "mac_B":   self.be_port_mac_B,
                "channel_B": self.be_port_channel_B,
                "mode_B": self.be_port_mode_B,
                "traffic_type_B": self.be_port_traffic_type_B,
                "traffic_protocol_B": self.be_port_protocol_B

            },
            "VI": {
                "colors": ['steelblue', 'lightskyblue'],
                "labels": ['Upload', 'Download'],

                # side A
                "clients_A": self.vi_clients_A,
                "ul_A": self.vi_tos_ul_A,
                "dl_A": self.vi_tos_dl_A,
                "ports_A": self.vi_port_eid_A,
                "mac_A":   self.vi_port_mac_A,
                "channel_A": self.vi_port_channel_A,
                "mode_A": self.vi_port_mode_A,
                "traffic_type_A": self.vi_port_traffic_type_A,
                "traffic_protocol_A": self.vi_port_protocol_A,

                # side B
                "clients_B": self.vi_clients_B,
                "ul_B": self.vi_tos_ul_B,
                "dl_B": self.vi_tos_dl_B,
                "ports_B": self.vi_port_eid_B,
                "mac_B":   self.vi_port_mac_B,
                "channel_B": self.vi_port_channel_B,
                "mode_B": self.vi_port_mode_B,
                "traffic_type_B": self.vi_port_traffic_type_B,
                "traffic_protocol_B": self.vi_port_protocol_B
            },
            "VO": {
                "colors": ['green', 'lightgreen'],
                "labels": ['Upload', 'Download'],

                # side A
                "clients_A": self.vo_clients_A,
                "ul_A": self.vo_tos_ul_A,
                "dl_A": self.vo_tos_dl_A,
                "ports_A": self.vo_port_eid_A,
                "mac_A":   self.vo_port_mac_A,
                "channel_A": self.vo_port_channel_A,
                "mode_A": self.vo_port_mode_A,
                "traffic_type_A": self.vo_port_traffic_type_A,
                "traffic_protocol_A": self.vo_port_protocol_A,

                # side B
                "clients_B": self.vo_clients_B,
                "ul_B": self.vo_tos_ul_B,
                "dl_B": self.vo_tos_dl_B,
                "ports_B": self.vo_port_eid_B,
                "mac_B":   self.vo_port_mac_B,
                "channel_B": self.vo_port_channel_B,
                "mode_B": self.vo_port_mode_B,
                "traffic_type_B": self.vo_port_traffic_type_B,
                "traffic_protocol_B": self.vo_port_protocol_B

                
            }
        }
        '''




        logger.info("printed the collected data")

    # quiesce the cx : quiesce a test at the end, which means stop transmitter
    # but leave received going to drain packets from the network and get better drop% calculations.
    # Stopping a test would record packets in flight at the moment it is stopped as dropped.

    def quiesce_cx(self):
        self.cx_profile.quiesce_cx()

    # Stop traffic and admin down stations.
    def stop(self):
        self.cx_profile.stop_cx()
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.admin_down(station_name)

    # clean up cx
    def cleanup_cx(self):
        cleanup = lf_cleanup.lf_clean(
            host=self.lfclient_host, port=self.lfclient_port, resource='all')
        cleanup.cxs_clean()

    # Remove traffic connections and stations.

    def cleanup(self):
        cleanup = lf_cleanup.lf_clean(
            host=self.lfclient_host, port=self.lfclient_port, resource='all')
        cleanup.sanitize_all()

        # Make sure they are gone
        count = 0
        while count < 10:
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.rm_port(sta, check_exists=True)
                    if rv:
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)
        '''
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()
        '''

    @staticmethod
    def csv_generate_column_headers():
        csv_rx_headers = ['Time epoch', 'Time', 'Monitor', 'UL-Min-Requested', 'UL-Max-Requested', 'DL-Min-Requested',
                          'DL-Max-Requested', 'UL-Min-PDU', 'UL-Max-PDU', 'DL-Min-PDU', 'DL-Max-PDU',
                          "average_rx_data_bytes"]
        return csv_rx_headers

    def csv_generate_dl_port_column_headers(self):
        csv_rx_headers = [
            'Time epoch',
            'Time',
            'Total-Station-Count',
            'UL-Min-Requested',
            'UL-Max-Requested',
            'DL-Min-Requested',
            'DL-Max-Requested',
            'UL-Min-PDU',
            'UL-Max-PDU',
            'DL-Min-PDU',
            'DL-Max-PDU',
            'Attenuation',
            'Name',
            'Rx-Bps',
            'Tx-Bps',
            'Rx-Link-Rate',
            'Tx-Link-Rate',
            'RSSI',
            'AP',
            'Mode',
            'MAC',
            'Channel',
            'Rx-Latency',
            'Rx-Jitter',
            'Ul-Rx-Goodput-bps',
            'Ul-Rx-Rate-ll',
            'Ul-Rx-Pkts-ll',
            'UL-Rx-Drop-Percent',
            'Dl-Rx-Goodput-bps',
            'Dl-Rx-Rate-ll',
            'Dl-Rx-Pkts-ll',
            'Dl-Rx-Drop_Percent']

        # Add in columns we are going to query from the AP
        if self.ap_read:
            self.ap_stats_dl_col_titles = self.ap.get_dl_col_titles()
            logger.debug("ap_stats_dl_col_titles : {col}".format(
                col=self.ap_stats_dl_col_titles))
            for col in self.ap_stats_dl_col_titles:
                csv_rx_headers.append(col)

        return csv_rx_headers

    def csv_generate_ul_port_column_headers(self):
        csv_ul_rx_headers = [
            'Time epoch',
            'Time',
            'Total-Station-Count',
            'UL-Min-Requested',
            'UL-Max-Requested',
            'DL-Min-Requested',
            'DL-Max-Requested',
            'UL-Min-PDU',
            'UL-Max-PDU',
            'DL-Min-PDU',
            'DL-Max-PDU',
            'Attenuation',
            'Name',
            'Rx-Bps',
            'Tx-Bps',
            'Rx-Link-Rate',
            'Tx-Link-Rate',
            'RSSI',
            'AP',
            'Mode',
            'Mac',
            'Channel',
            'Rx-Latency',
            'Rx-Jitter',
            'Ul-Rx-Goodput-bps',
            'Ul-Rx-Rate-ll',
            'Ul-Rx-Pkts-ll',
            'UL-Rx-Drop-Percent',
            'Dl-Rx-Goodput-bps',
            'Dl-Rx-Rate-ll',
            'Dl-Rx-Pkts-ll',
            'Dl-Rx-Drop_Percent']
        # Add in columns we are going to query from the AP
        if self.ap_read:
            self.ap_stats_ul_col_titles = self.ap.get_ul_col_titles()
            logger.debug("ap_stats_ul_col_titles : {col}".format(
                col=self.ap_stats_ul_col_titles))
            for col in self.ap_stats_ul_col_titles:
                csv_ul_rx_headers.append(col)

        return csv_ul_rx_headers

    def csv_generate_results_column_headers(self):
        csv_rx_headers = [
            'Time epoch',
            'Time',
            'Station-Count',
            'UL-Min-Requested',
            'UL-Max-Requested',
            'DL-Min-Requested',
            'DL-Max-Requested',
            'UL-Min-PDU',
            'UL-Max-PDU',
            'DL-Min-PDU',
            'DL-Max-PDU',
            'Attenuation',
            'Total-Download-Bps',
            'Total-Upload-Bps',
            'Total-UL/DL-Bps',
            'Total-Download-LL-Bps',
            'Total-Upload-LL-Bps',
            'Total-UL/DL-LL-Bps']
        for k in self.user_tags:
            csv_rx_headers.append(k[0])

        return csv_rx_headers

    # Write initial headers to csv file.
    def csv_add_column_headers(self):
        if self.csv_results_file is not None:
            self.csv_results_writer.writerow(
                self.csv_generate_results_column_headers())
            self.csv_results_file.flush()

    # Write initial headers to port csv file.
    def csv_add_port_column_headers(self, port_eid, headers):
        # if self.csv_file is not None:
        fname = self.outfile[:-4]  # Strip '.csv' from file name
        fname = fname + "-dl-" + port_eid + ".csv"
        pfile = open(fname, "w")
        port_csv_writer = csv.writer(pfile, delimiter=",")
        self.dl_port_csv_files[port_eid] = pfile
        self.dl_port_csv_writers[port_eid] = port_csv_writer

        port_csv_writer.writerow(headers)
        pfile.flush()

    def csv_add_ul_port_column_headers(self, port_eid, headers):
        # if self.csv_file is not None:
        fname = self.outfile[:-4]  # Strip '.csv' from file name
        fname = fname + "-ul-" + port_eid + ".csv"
        pfile = open(fname, "w")
        ul_port_csv_writer = csv.writer(pfile, delimiter=",")
        self.ul_port_csv_files[port_eid] = pfile
        self.ul_port_csv_writers[port_eid] = ul_port_csv_writer

        ul_port_csv_writer.writerow(headers)
        pfile.flush()

    @staticmethod
    def csv_validate_list(csv_list, length):
        if len(csv_list) < length:
            csv_list = csv_list + [('no data', 'no data')] * \
                (length - len(csv_list))
        return csv_list

    @staticmethod
    def csv_add_row(row, writer, csv_file):
        if csv_file is not None:
            writer.writerow(row)
            csv_file.flush()

    # End of the main class.

# Check some input values.


def valid_endp_types(_endp_type):
    etypes = _endp_type.split(',')
    for endp_type in etypes:
        valid_endp_type = [
            'lf',
            'lf_udp',
            'lf_udp6',
            'lf_tcp',
            'lf_tcp6',
            'mc_udp',
            'mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            logger.error(
                'invalid endp_type: %s. Valid types lf, lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' %
                endp_type)
            exit(1)
    return _endp_type


# Starting point for running this from cmd line.
# note: when adding command line delimiters : +,=@
# https://stackoverflow.com/questions/37304799/cross-platform-safe-to-use-command-line-string-separator
def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"

    parser = argparse.ArgumentParser(
        prog='test_l3.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will generate csv file
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Maximum stations per radio based on radio
            ''',

        description='''\

NAME: test_l3.py

PURPOSE: The Layer 3 Traffic Generation Test is designed to test the performance of the Access Point by running layer-3
         Cross-Connect Traffic.  Layer-3 Cross-Connects represent a stream of data flowing through the system under test.
         A Cross-Connect (CX) is composed of two Endpoints, each of which is associated with a particular Port (physical or virtual interface).

         The test will create stations, create cx traffic between upstream port and stations,  run traffic. Verify
         the traffic is being transmitted and received

         * Supports creating user-specified amount stations on multiple radios
         * Supports configuring upload and download requested rates and PDU sizes.
         * Supports generating connections with different ToS values.
         * Supports generating tcp and/or UDP traffic types.
         * Supports iterating over different PDU sizes
         * Supports iterating over different requested tx rates (configurable as total or per-connection value)
         * Supports iterating over attenuation values.
         * Supports testing connection between two ethernet connection - L3 dataplane

         Generic command layout:
         -----------------------
         ./test_l3.py --mgr <ip_address> --test_duration <duration> --endp_type <traffic types> --upstream_port <port>
         --radio "radio==<radio> stations==<number stations> ssid==<ssid> ssid_pw==<ssid password>
         security==<security type: wpa2, open, wpa3>" --debug

EXAMPLE:

#########################################
# Examples
#########################################
Example running traffic with two radios
1. Test duration 30 minutes
2. Traffic IPv4 TCP, UDP
3. Upstream-port eth2
4. Radio #0 wiphy0 has 1 station, ssid = ssid_2g, ssid password = ssid_pw_2g  security = wpa2
5. Radio #1 wiphy1 has 2 stations, ssid = ssid_5g, ssid password = BLANK security = open
6. Create connections with TOS of BK and VI

         # The script now supports multiple radios, each specified with an individual --radio switch.

           * UDP and TCP bi-directional test, no use of controller.
             ./test_l3.py --mgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --upstream_port 1.1.eth1
             --radio "radio==1.1.wiphy0 stations==5 ssid==Netgear2g ssid_pw==lanforge security==wpa2"
             --radio "radio==1.1.wiphy1 stations==1 ssid==Netgear5g ssid_pw==lanforge security==wpa2"
             --test_duration 60s

           * Port resets, chooses random value between min and max
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 90s --polling_interval 10s --upstream_port eth1
             --radio 'radio==wiphy0,stations==4,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,reset_port_enable==TRUE,
             reset_port_time_min==10s,reset_port_time_max==20s' --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000
             --side_b_min_bps=300000000

         # Command: (remove carriage returns)
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 30s --endp_type "lf_tcp,lf_udp" --tos "BK VI" --upstream_port 1.1.eth1
             --radio "radio==1.1.wiphy0 stations==1 ssid==Netgear2g ssid_pw==lanforge security==wpa2"

         # Have the stations continue to run after the completion of the script
             ./test_l3.py --lfmgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --tos BK --upstream_port 1.1.eth1
             --radio 'radio==wiphy0 stations==2 ssid==Netgear2g ssid_pw==lanforge security==wpa2' --test_duration 30s
             --polling_interval 5s --side_a_min_bps 256000 --side_b_min_bps 102400000 --no_stop_traffic

         #  Have script use existing stations from previous run where traffic was not stopped and also create new stations and leave traffic running
             ./test_l3.py --lfmgr 192.168.200.83 --endp_type 'lf_udp,lf_tcp' --tos BK --upstream_port 1.1.eth1
             --radio 'radio==wiphy0 stations==2 ssid==Netgear2g ssid_pw==lanforge security==wpa2' --sta_start_offset 1000
             --test_duration 30s --polling_interval 5s --side_a_min_bps 256000 --side_b_min_bps 102400000 --use_existing_station_list
             --existing_station_list '1.1.sta0000,1.1.sta0001,1.1.sta0002' --no_stop_traffic

         # Have script use wifi_settings enable flages  ::  wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)
             ./test_l3.py --lfmgr 192.168.200.83 --test_duration 20s --polling_interval 5s --upstream_port 1.1.eth1
             --radio 'radio==1.1.wiphy0,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy1,stations==1,ssid==Netgear5g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --radio 'radio==1.1.wiphy2,stations==1,ssid==Netgear2g,ssid_pw==lanforge,security==wpa2,wifi_mode==0,wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down)'
             --endp_type lf_udp --rates_are_totals --side_a_min_bps=20000 --side_b_min_bps=300000000 --test_rig ID_003 --test_tag 'l3_longevity' --dut_model_num GT-AXE11000 --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0 --dut_serial_num 12345678 --log_level debug

         # Setting wifi_settings per radio
            ./test_l3.py
            --lfmgr 192.168.100.116
            --local_lf_report_dir /home/lanforge/html-reports/
            --test_duration 15s
            --polling_interval 5s
            --upstream_port eth2
            --radio "radio==wiphy1 stations==4 ssid==asus11ax-5 ssid_pw==hello123 security==wpa2  mode==0 wifi_settings==wifi_settings,enable_flags==(ht160_enable&&wpa2_enable&&80211u_enable&&create_admin_down&&ht160_enable) "
            --endp_type lf_udp
            --rates_are_totals
            --side_a_min_bps=20000
            --side_b_min_bps=300000000
            --test_rig CT-US-001
            --test_tag 'test_l3'

         # Example : LAN-1927  WPA2-TLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Disabled'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

        # Example : LAN-1927  WPA2-TTLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa2,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Disabled'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug


        # Example : LAN-1927  WPA3-TTLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TTLS!!identity&&testuser!!passwd&&testpasswd!!ieee80211w&&Required'
             --endp_type lf_ud
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

        # Example : LAN-1927  WPA3-TLS-Configuration
            ./test_l3.py
             --lfmgr 192.168.0.103
             --test_duration 20s
             --polling_interval 5s
             --upstream_port 1.1.eth2
             --radio 'radio==wiphy1,stations==1,ssid==ax88u_5g,ssid_pw==[BLANK],security==wpa3,wifi_settings==wifi_settings,wifi_mode==0,enable_flags==8021x_radius&&80211r_pmska_cache,wifi_extra==key_mgmt&&WPA-EAP!!pairwise&&GCMP-256!!group&&GCMP-256!!eap&&TLS!!identity&&testuser!!passwd&&testpasswd!!private_key&&/home/lanforge/client.p12!!ca_cert&&/home/lanforge/ca.pem!!pk_password&&lanforge!!ieee80211w&&Required'
             --endp_type lf_udp
             --rates_are_totals
             --side_a_min_bps=256000
             --side_b_min_bps=300000000
             --test_rig ID_003
             --test_tag 'test_l3'
             --dut_model_num GT-AXE11000
             --dut_sw_version 3.0.0.4.386_44266
             --dut_hw_version 1.0
             --dut_serial_num 12345678
             --log_level debug

SCRIPT_CLASSIFICATION:  Creation & Runs Traffic

SCRIPT_CATEGORIES:  Performance, Functional,  KPI Generation,  Report Generation

NOTES:

#################################
# Command switches
#################################

--mgr <hostname for where LANforge GUI is running>',default='localhost'
-d  / --test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m'
--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE"
--debug:  Enable debugging',default=False
-t  / --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types
-u / --upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
-o / --outfile <Output file for csv data>", default='longevity_results'

<duration>: number followed by one of the following
d - days
h - hours
m - minutes
s - seconds

<traffic type>:
lf_udp  : IPv4 UDP traffic
lf_tcp  : IPv4 TCP traffic
lf_udp6 : IPv6 UDP traffic
lf_tcp6 : IPv6 TCP traffic
mc_udp  : IPv4 multi cast UDP traffic
mc_udp6 : IPv6 multi cast UDP traffic

<tos>:
BK, BE, VI, VO:  Optional wifi related Tos Settings.  Or, use your preferred numeric values. Cross connects type of service

    * Data 0 (Best Effort, BE): Medium priority queue, medium throughput and delay.
             Most traditional IP data is sent to this queue.
    * Data 1 (Background, BK): Lowest priority queue, high throughput. Bulk data that requires maximum throughput and
             is not time-sensitive is sent to this queue (FTP data, for example).
    * Data 2 (Video, VI): High priority queue, minimum delay. Time-sensitive data such as Video and other streaming
             media are automatically sent to this queue.
    * Data 3 (Voice, VO): Highest priority queue, minimum delay. Time-sensitive data such as Voice over IP (VoIP)
             is automatically sent to this Queue.

<wifi_mode>:
    Input       : Enum Val  : Shown by nc_show_ports

    AUTO        |  0        #  802.11
    802.11a     |  1        #  802.11a
    b           |  2        #  802.11b
    g           |  3        #  802.11g
    abg         |  4        #  802.11abg
    abgn        |  5        #  802.11abgn
    bgn         |  6        #  802.11bgn
    bg          |  7        #  802.11bg
    abgnAC      |  8        #  802.11abgn-AC
    anAC        |  9        #  802.11an-AC
    an          | 10        #  802.11an
    bgnAC       | 11        #  802.11bgn-AC
    abgnAX      | 12        #  802.11abgn-AX
                            #     a/b/g/n/AC/AX (dual-band AX) support
    bgnAX       | 13        #  802.11bgn-AX
    anAX        | 14        #  802.11an-AX
    aAX         | 15        #  802.11a-AX (6E disables /n and /ac)

wifi_settings flags are currently defined as:
    wpa_enable           | 0x10         # Enable WPA
    # Use Custom wpa_supplicant config file.
    custom_conf          | 0x20
    # Use wpa_supplicant configured for WEP encryption.
    wep_enable           | 0x200
    # Use wpa_supplicant configured for WPA2 encryption.
    wpa2_enable          | 0x400
    # Disable HT-40 even if hardware and AP support it.
    ht40_disable         | 0x800
    # Enable SCAN-SSID flag in wpa_supplicant.
    scan_ssid            | 0x1000
    # Use passive scanning (don't send probe requests).
    passive_scan         | 0x2000
    disable_sgi          | 0x4000       # Disable SGI (Short Guard Interval).
    # OK-To-Migrate (Allow station migration between LANforge radios)
    lf_sta_migrate       | 0x8000
    # Verbose-Debug:  Increase debug info in wpa-supplicant and hostapd logs.
    verbose              | 0x10000
    # Enable 802.11u (Interworking) feature.
    80211u_enable        | 0x20000
    # Enable 802.11u (Interworking) Auto-internetworking feature.  Always enabled currently.
    80211u_auto          | 0x40000
    # AP Provides access to internet (802.11u Interworking)
    80211u_gw            | 0x80000
    # AP requires additional step for access (802.11u Interworking)
    80211u_additional    | 0x100000
    # AP claims emergency services reachable (802.11u Interworking)
    80211u_e911          | 0x200000
    # AP provides Unauthenticated emergency services (802.11u Interworking)
    80211u_e911_unauth   | 0x400000
    # Enable Hotspot 2.0 (HS20) feature.  Requires WPA-2.
    hs20_enable          | 0x800000
    # AP:  Disable DGAF (used by HotSpot 2.0).
    disable_gdaf         | 0x1000000
    8021x_radius         | 0x2000000    # Use 802.1x (RADIUS for AP).
    # Enable oportunistic PMSKA caching for WPA2 (Related to 802.11r).
    80211r_pmska_cache   | 0x4000000
    # Disable HT80 (for AC chipset NICs only)
    disable_ht80         | 0x8000000
    ibss_mode            | 0x20000000   # Station should be in IBSS mode.
    # Enable OSEN protocol (OSU Server-only Authentication)
    osen_enable          | 0x40000000
    # Disable automatic station roaming based on scan results.
    disable_roam         | 0x80000000
    ht160_enable         | 0x100000000  # Enable HT160 mode.
    # Disable fast_reauth option for virtual stations.
    disable_fast_reauth  | 0x200000000
    mesh_mode            | 0x400000000  # Station should be in MESH mode.
    # Station should enable power-save.  May not work in all drivers/configurations.
    power_save_enable    | 0x800000000
    create_admin_down    | 0x1000000000 # Station should be created admin-down.
    # WDS station (sort of like a lame mesh), not supported on ath10k
    wds-mode             | 0x2000000000
    # Do not include supported-oper-class-IE in assoc requests.  May work around AP bugs.
    no-supp-op-class-ie  | 0x4000000000
    # Enable/disable tx-offloads, typically managed by set_wifi_txo command
    txo-enable           | 0x8000000000
    use-wpa3             | 0x10000000000 # Enable WPA-3 (SAE Personal) mode.
    use-bss-transition   | 0x80000000000 # Enable BSS transition.
    disable-twt          | 0x100000000000 # Disable TWT mode

For wifi_extra_keys syntax :
    telnet <lanforge ip> 4001
    type: help set_wifi_extra
wifi_extra keys:
                key_mgmt  (Key Mangement)
                pairwise  (Pairwise Ciphers)
                group   (Group Ciphers)
                psk     (WPA PSK)
                wep_key
                ca_cert (CA Cert File)
                eap     (EAP Methods) EAP method: MD5, MSCHAPV2, OTP, GTC, TLS, PEAP, TTLS. (note different the GUI no appended EAP-)
                identity    (EAP Identity)
                anonymous_identity  (EAP Anon Identity)
                phase1  (Phase-1)
                phase2  (Phase-2)
                passwd  (EAP Password)
                pin (EAP Pin)
                pac_file    (PAC file)
                private_key (Private Key)
                pk_password (PK Password)
                hessid="00:00:00:00:00:00"
                realm   (Realm)
                client_cert (Client Cert)
                imsi    (IMSI)
                milenage    (Milenage)
                domain  (Domain)
                roaming_consortium  (Consortium)
                venue_group ()
                network_type    (Network Auth)
                ipaddr_type_avail   ()
                network_auth_type ()
                anqp_3gpp_cell_net ()

                ieee80211w :   0,1,2

Multicast traffic :
        Multicast traffic default IGMP Address in the range of 224.0.0.0 to 239.255.255.255,
        so I have provided 224.9.9.9 as IGMP address and IGMP Dest port as 9999 and MIN-IP PORT as 9999.
        these values must be same on the eth1(server side) and client side, then the traffic will run.

===============================================================================
 ** FURTHER INFORMATION **
    Using the layer3_cols flag:

    Currently the output function does not support inputting the columns in layer3_cols the way they are displayed in the GUI. This quirk is under construction. To output
    certain columns in the GUI in your final report, please match the according GUI column display to it's counterpart to have the columns correctly displayed in
    your report.

    GUI Column Display       Layer3_cols argument to type in (to print in report)

    Name                |  'name'
    EID                 |  'eid'
    Run                 |  'run'
    Mng                 |  'mng'
    Script              |  'script'
    Tx Rate             |  'tx rate'
    Tx Rate (1 min)     |  'tx rate (1&nbsp;min)'
    Tx Rate (last)      |  'tx rate (last)'
    Tx Rate LL          |  'tx rate ll'
    Rx Rate             |  'rx rate'
    Rx Rate (1 min)     |  'rx rate (1&nbsp;min)'
    Rx Rate (last)      |  'rx rate (last)'
    Rx Rate LL          |  'rx rate ll'
    Rx Drop %           |  'rx drop %'
    Tx PDUs             |  'tx pdus'
    Tx Pkts LL          |  'tx pkts ll'
    PDU/s TX            |  'pdu/s tx'
    Pps TX LL           |  'pps tx ll'
    Rx PDUs             |  'rx pdus'
    Rx Pkts LL          |  'pps rx ll'
    PDU/s RX            |  'pdu/s tx'
    Pps RX LL           |  'pps rx ll'
    Delay               |  'delay'
    Dropped             |  'dropped'
    Jitter              |  'jitter'
    Tx Bytes            |  'tx bytes'
    Rx Bytes            |  'rx bytes'
    Replays             |  'replays'
    TCP Rtx             |  'tcp rtx'
    Dup Pkts            |  'dup pkts'
    Rx Dup %            |  'rx dup %'
    OOO Pkts            |  'ooo pkts'
    Rx OOO %            |  'rx ooo %'
    RX Wrong Dev        |  'rx wrong dev'
    CRC Fail            |  'crc fail'
    RX BER              |  'rx ber'
    CX Active           |  'cx active'
    CX Estab/s          |  'cx estab/s'
    1st RX              |  '1st rx'
    CX TO               |  'cx to'
    Pattern             |  'pattern'
    Min PDU             |  'min pdu'
    Max PDU             |  'max pdu'
    Min Rate            |  'min rate'
    Max Rate            |  'max rate'
    Send Buf            |  'send buf'
    Rcv Buf             |  'rcv buf'
    CWND                |  'cwnd'
    TCP MSS             |  'tcp mss'
    Bursty              |  'bursty'
    A/B                 |  'a/b'
    Elapsed             |  'elapsed'
    Destination Addr    |  'destination addr'
    Source Addr         |  'source addr'

    Using the port_mgr_cols flag:
         '4way time (us)'
         'activity'
         'alias'
         'anqp time (us)'
         'ap'
         'beacon'
         'bps rx'
         'bps rx ll'
         'bps tx'
         'bps tx ll'
         'bytes rx ll'
         'bytes tx ll'
         'channel'
         'collisions'
         'connections'
         'crypt'
         'cx ago'
         'cx time (us)'
         'device'
         'dhcp (ms)'
         'down'
         'entity id'
         'gateway ip'
         'ip'
         'ipv6 address'
         'ipv6 gateway'
         'key/phrase'
         'login-fail'
         'login-ok'
         'logout-fail'
         'logout-ok'
         'mac'
         'mask'
         'misc'
         'mode'
         'mtu'
         'no cx (us)'
         'noise'
         'parent dev'
         'phantom'
         'port'
         'port type'
         'pps rx'
         'pps tx'
         'qlen'
         'reset'
         'retry failed'
         'rx bytes'
         'rx crc'
         'rx drop'
         'rx errors'
         'rx fifo'
         'rx frame'
         'rx length'
         'rx miss'
         'rx over'
         'rx pkts'
         'rx-rate'
         'sec'
         'signal'
         'ssid'
         'status'
         'time-stamp'
         'tx abort'
         'tx bytes'
         'tx crr'
         'tx errors'
         'tx fifo'
         'tx hb'
         'tx pkts'
         'tx wind'
         'tx-failed %'
         'tx-rate'
         'wifi retries'

    Can't decide what columns to use? You can just use 'all' to select all available columns from both tables.

STATUS: Functional

VERIFIED_ON:   18-JULY-2023,
             GUI Version:  5.4.6
             Kernel Version: 5.19.17+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: False

        ''')
    test_l3_parser = parser.add_argument_group(
        'arguments defined in test_l3.py file')
    # add argument group
    # the local_lf_report_dir is the parent directory of where the results are used with lf_check.py
    test_l3_parser.add_argument('--local_lf_report_dir',
                                help='--local_lf_report_dir override the report path (lanforge/html-reports), primary used when making another directory lanforge/html-report/<test_rig>',
                                default="")
    test_l3_parser.add_argument(
        "--results_dir_name",
        default="test_l3",
        help="the name of the directory that contains the output from the test /lanforge/html-reports/<results_dir_name> default: test_l3")

    test_l3_parser.add_argument(
        "--test_rig",
        default="",
        help="test rig for kpi.csv, testbed that the tests are run on")
    test_l3_parser.add_argument(
        "--test_tag",
        default="",
        help="test tag for kpi.csv,  test specific information to differenciate the test")
    test_l3_parser.add_argument(
        "--dut_hw_version",
        default="",
        help="dut hw version for kpi.csv, hardware version of the device under test")
    test_l3_parser.add_argument(
        "--dut_sw_version",
        default="",
        help="dut sw version for kpi.csv, software version of the device under test")
    test_l3_parser.add_argument(
        "--dut_model_num",
        default="",
        help="dut model for kpi.csv,  model number / name of the device under test")
    test_l3_parser.add_argument(
        "--dut_serial_num",
        default="",
        help="dut serial for kpi.csv, serial number / serial number of the device under test")
    test_l3_parser.add_argument(
        "--test_priority",
        default="",
        help="dut model for kpi.csv,  test-priority is arbitrary number")
    test_l3_parser.add_argument(
        "--test_id",
        default="test l3",
        help="test-id for kpi.csv,  script or test name")
    '''
    Other values that are included in the kpi.csv row.
    short-description : short description of the test
    pass/fail : set blank for performance tests
    numeric-score : this is the value for the y-axis (x-axis is a timestamp),  numeric value of what was measured
    test details : what was measured in the numeric-score,  e.g. bits per second, bytes per second, upload speed, minimum cx time (ms)
    Units : units used for the numeric-scort
    Graph-Group - For the lf_qa.py dashboard

    '''
    test_l3_parser.add_argument(
        '-o',
        '--csv_outfile',
        help="--csv_outfile <Output file for csv data>",
        default="")

    test_l3_parser.add_argument(
        '--tty',
        help='--tty \"/dev/ttyUSB2\" the serial interface to the AP',
        default="")
    test_l3_parser.add_argument(
        '--baud',
        help='--baud \"9600\"  AP baud rate for the serial interface',
        default="9600")
    test_l3_parser.add_argument(
        '--mgr',
        '--lfmgr',
        dest='lfmgr',
        help='--lfmgr <hostname for where LANforge GUI is running>',
        default='localhost')
    test_l3_parser.add_argument(
        '--mgr_port',
        '--lfmgr_port',
        dest='lfmgr_port',
        help='--lfmgr_port <port LANforge GUI HTTP service is running on>',
        default=8080)

    test_l3_parser.add_argument(
        '--test_duration',
        help='--test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',
        default='3m')
    test_l3_parser.add_argument(
        '--tos',
        help='--tos:  Support different ToS settings: BK,BE,VI,VO,numeric',
        default="BE")
    test_l3_parser.add_argument(
        '--debug',
        help='--debug this will enable debugging in py-json method',
        action='store_true')
    test_l3_parser.add_argument('--log_level',
                                default=None,
                                help='Set logging level: debug | info | warning | error | critical')
    test_l3_parser.add_argument(
        '-t',
        '--endp_type',
        help=(
            '--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\" '
            ' Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6'),
        default='lf_udp',
        type=valid_endp_types)
    test_l3_parser.add_argument(
        '-u',
        '--upstream_port',
        help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',
        default='eth1')
    test_l3_parser.add_argument(
        '--downstream_port',
        help='--downstream_port <cross connect downstream_port>  for use when downstream is ethernet (eth to eth connection) do not use with wifi stations example: --downstream_port eth2', default=None)
    test_l3_parser.add_argument(
        '--polling_interval',
        help="--polling_interval <seconds>",
        default='60s')

    test_l3_parser.add_argument(
        '-r', '--radio',
        action='append',
        nargs=1,
        help=(' --radio'
              ' "radio==<number_of_wiphy stations==<number of stations>'
              ' ssid==<ssid> ssid_pw==<ssid password> security==<security> '
              ' wifi_settings==True wifi_mode==<wifi_mode>'
              ' enable_flags==<enable_flags> '
              ' reset_port_enable==True reset_port_time_min==<min>s'
              ' reset_port_time_max==<max>s" ')
    )
    test_l3_parser.add_argument(
        '-amr',
        '--side_a_min_bps',
        help='--side_a_min_bps, requested downstream min tx rate, comma separated list for multiple iterations.  Default 256k',
        default="256000")
    test_l3_parser.add_argument(
        '-amp',
        '--side_a_min_pdu',
        help='--side_a_min_pdu, downstream pdu size, comma separated list for multiple iterations.  Default MTU',
        default="MTU")
    test_l3_parser.add_argument(
        '-bmr',
        '--side_b_min_bps',
        help='--side_b_min_bps, requested upstream min tx rate, comma separated list for multiple iterations.  Default 256000',
        default="256000")
    test_l3_parser.add_argument(
        '-bmp',
        '--side_b_min_pdu',
        help='--side_b_min_pdu, upstream pdu size, comma separated list for multiple iterations. Default MTU',
        default="MTU")
    test_l3_parser.add_argument(
        "--rates_are_totals",
        default=False,
        help="Treat configured rates as totals instead of using the un-modified rate for every connection.",
        action='store_true')
    test_l3_parser.add_argument(
        "--multiconn",
        default=1,
        help="Configure multi-conn setting for endpoints.  Default is 1 (auto-helper is enabled by default as well).")

    test_l3_parser.add_argument(
        '--attenuators',
        help='--attenuators,  comma separated list of attenuator module eids:  shelf.resource.atten-serno.atten-idx',
        default="")
    test_l3_parser.add_argument(
        '--atten_vals',
        help='--atten_vals,  comma separated list of attenuator settings in ddb units (1/10 of db)',
        default="")

    test_l3_parser.add_argument(
        "--wait",
        help="--wait <time> , time to wait at the end of the test",
        default='0')

    test_l3_parser.add_argument('--sta_start_offset', help='Station start offset for building stations',
                                default='0')

    test_l3_parser.add_argument('--no_pre_cleanup', help='Do not pre cleanup stations on start',
                                action='store_true')

    test_l3_parser.add_argument('--no_cleanup', help='Do not cleanup before exit',
                                action='store_true')

    test_l3_parser.add_argument(
        '--cleanup_cx', help='cleanup cx before exit', action='store_true')

    test_l3_parser.add_argument(
        '--csv_data_to_report', help='collected interval data in csv for each cx will be put in report', action='store_true')

    test_l3_parser.add_argument('--no_stop_traffic', help='leave traffic running',
                                action='store_true')

    test_l3_parser.add_argument('--quiesce_cx', help='--quiesce store true,  allow the cx to drain then stop so as to not have rx drop pkts',
                                action='store_true')

    test_l3_parser.add_argument('--use_existing_station_list', help='--use_station_list ,full eid must be given,'
                                'the script will use stations from the list, no configuration on the list, also prevents pre_cleanup',
                                action='store_true')

    # TODO pass in the station list
    test_l3_parser.add_argument('--existing_station_list',
                                action='append',
                                nargs=1,
                                help='--station_list [list of stations] , use the stations in the list , multiple station lists may be entered')

    # Wait for IP made configurable
    test_l3_parser.add_argument(
        '--wait_for_ip_sec', help='--wait_for_ip_sec <seconds>  default : 120s ', default="120s")

    # logging configuration
    test_l3_parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")

    test_l3_parser.add_argument(
        '--ap_read', help='--ap_read  flag present enable reading ap', action='store_true')
    test_l3_parser.add_argument("--ap_module", type=str, help="series module")

    test_l3_parser.add_argument(
        '--ap_test_mode', help='--ap_mode ', default=True)

    test_l3_parser.add_argument('--ap_scheme', help="--ap_scheme '/dev/ttyUSB0'", choices=[
                                'serial', 'telnet', 'ssh', 'mux_serial'], default='serial')
    test_l3_parser.add_argument(
        '--ap_serial_port', help="--ap_serial_port '/dev/ttyUSB0'", default='/dev/ttyUSB0')
    test_l3_parser.add_argument(
        '--ap_serial_baud', help="--ap_baud '115200'',  default='115200", default="115200")
    test_l3_parser.add_argument(
        '--ap_ip', help='--ap_ip', default='192.168.50.1')
    test_l3_parser.add_argument(
        '--ap_ssh_port', help='--ap_ssh_port', default='1025')
    test_l3_parser.add_argument(
        '--ap_telnet_port', help='--ap_telnet_port', default='23')
    test_l3_parser.add_argument(
        '--ap_user', help='--ap_user , the user name for the ap, default = lanforge', default='lanforge')
    test_l3_parser.add_argument(
        '--ap_passwd', help='--ap_passwd, the password for the ap default = lanforge', default='lanforge')
    # ASUS interfaces
    test_l3_parser.add_argument(
        '--ap_if_2g', help='--ap_if_2g eth6', default='wl0')
    test_l3_parser.add_argument(
        '--ap_if_5g', help='--ap_if_5g eth7', default='wl1')
    test_l3_parser.add_argument(
        '--ap_if_6g', help='--ap_if_6g eth8', default='wl2')
    test_l3_parser.add_argument(
        '--ap_file', help="--ap_file 'ap_file.txt'", default=None)
    test_l3_parser.add_argument(
        '--ap_band_list', help="--ap_band_list '2g,5g,6g' supported bands", default='2g,5g,6g')

    args = parser.parse_args()

    # initialize pass / fail
    test_passed = False

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    debug = args.debug

    # Gather data for test reporting
    # for kpi.csv generation
    logger.info("read in command line paramaters")
    local_lf_report_dir = args.local_lf_report_dir
    test_rig = args.test_rig
    test_tag = args.test_tag
    dut_hw_version = args.dut_hw_version
    dut_sw_version = args.dut_sw_version
    dut_model_num = args.dut_model_num
    dut_serial_num = args.dut_serial_num
    # test_priority = args.test_priority  # this may need to be set per test
    test_id = args.test_id

    if args.test_duration:
        test_duration = args.test_duration

    if args.polling_interval:
        polling_interval = args.polling_interval

    if args.endp_type:
        endp_types = args.endp_type

    if args.lfmgr:
        lfjson_host = args.lfmgr

    if args.lfmgr_port:
        lfjson_port = args.lfmgr_port

    if args.upstream_port:
        side_b = args.upstream_port

    if args.downstream_port:
        side_a = args.downstream_port
    else:
        side_a = None

    if args.radio:
        radios = args.radio
    else:
        radios = None

    # Create report, when running with the test framework (lf_check.py)
    # results need to be in the same directory
    logger.info("configure reporting")
    if local_lf_report_dir != "":
        report = lf_report.lf_report(
            _path=local_lf_report_dir,
            _results_dir_name=args.results_dir_name,
            _output_html="{results_dir_name}.html".format(
                results_dir_name=args.results_dir_name),
            _output_pdf="{results_dir_name}.pdf".format(results_dir_name=args.results_dir_name))
    else:
        report = lf_report.lf_report(
            _results_dir_name=args.results_dir_name,
            _output_html="{results_dir_name}.html".format(
                results_dir_name=args.results_dir_name),
            _output_pdf="{results_dir_name}.pdf".format(results_dir_name=args.results_dir_name))

    kpi_path = report.get_report_path()
    logger.info("Report and kpi_path :{kpi_path}".format(kpi_path=kpi_path))

    kpi_csv = lf_kpi_csv.lf_kpi_csv(
        _kpi_path=kpi_path,
        _kpi_test_rig=test_rig,
        _kpi_test_tag=test_tag,
        _kpi_dut_hw_version=dut_hw_version,
        _kpi_dut_sw_version=dut_sw_version,
        _kpi_dut_model_num=dut_model_num,
        _kpi_dut_serial_num=dut_serial_num,
        _kpi_test_id=test_id)

    if args.csv_outfile is not None:
        current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        csv_outfile = "{}_{}-test_l3.csv".format(
            args.csv_outfile, current_time)
        csv_outfile = report.file_add_path(csv_outfile)
        logger.info("csv output file : {}".format(csv_outfile))

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

    #
    logger.info("parse radio arguments used for station configuration")
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
            # radio_info_dict = dict(map(lambda x: x.split('=='), str(radio_).replace('"', '').split()))

            logger.debug("radio_dict {}".format(radio_info_dict))

            for key in radio_keys:
                if key not in radio_info_dict:
                    logger.critical(
                        "missing config, for the {}, all of the following need to be present {} ".format(
                            key, radio_keys))
                    exit(1)

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

                key_mgmt = '[BLANK]'
                pairwise = '[BLANK]'
                group = '[BLANK]'
                psk = '[BLANK]'
                eap = '[BLANK]'
                identity = '[BLANK]'
                anonymous_identity = "[BLANK]"
                phase1 = "[BLANK]"
                phase2 = "[BLANK]"
                passwd = '[BLANK]'
                pin = '[BLANK]'
                pac_file = '[BLANK]'
                private_key = '[BLANK]'
                pk_password = '[BLANK]'
                hessid = "00:00:00:00:00:00"
                realm = "[BLANK]"
                client_cert = "[BLANK]"
                imsi = "[BLANK]"
                milenage = "[BLANK]"
                domain = "[BLANK]"
                roaming_consortium = "[BLANK]"
                venue_group = "[BLANK]"
                network_type = "[BLANK]"
                ipaddr_type_avail = "[BLANK]"
                network_auth_type = "[BLANK]"
                anqp_3gpp_cell_net = "[BLANK]"

                ieee80211w = 'Optional'

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
                    logger.info("wifi_settings_keys not enabled")
                    wifi_settings_found = False
                    break

            if wifi_settings_found:
                # Check for additional flags
                if {'wifi_mode', 'enable_flags'}.issubset(
                        radio_info_dict.keys()):
                    logger.info("wifi_settings flags set")
                else:
                    logger.info(
                        "wifi_settings is present wifi_mode, enable_flags need to be set")
                    logger.info(
                        "or remove the wifi_settings or set wifi_settings==False flag on the radio for defaults")
                    exit(1)
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

    logger.info("configure and create test object")
    ip_var_test = L3VariableTime(
        endp_types=endp_types,
        args=args,
        tos=args.tos,
        side_b=side_b,
        side_a=side_a,
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
        test_duration=test_duration,
        polling_interval=polling_interval,
        lfclient_host=lfjson_host,
        lfclient_port=lfjson_port,
        debug=debug,
        kpi_csv=kpi_csv,
        no_cleanup=args.no_cleanup,
        use_existing_station_lists=args.use_existing_station_list,
        existing_station_lists=existing_station_lists,
        wait_for_ip_sec=args.wait_for_ip_sec,
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
        ieee80211w_list=ieee80211w_list
    )

    if args.no_pre_cleanup or args.use_existing_station_list:
        logger.info("No station pre clean up any existing cxs on LANforge")
    else:
        logger.info("clean up any existing cxs on LANforge")
        ip_var_test.pre_cleanup()

    logger.info("create stations or use passed in station_list, build the test")
    ip_var_test.build()
    if not ip_var_test.passes():
        logger.critical("build step failed.")
        logger.critical(ip_var_test.get_fail_message())
        exit(1)

    logger.info("Start the test and run for a duration")
    ip_var_test.start(False)

    logger.info(
        "Pausing {wait} seconds for manual inspection before conclusion of test and possible stopping of traffic and station cleanup".format(
            wait=args.wait))
    time.sleep(int(args.wait))

    # Admin down the stations
    if args.no_stop_traffic:
        logger.info("--no_stop_traffic set leave traffic running")
    else:
        if args.quiesce_cx:
            ip_var_test.quiesce_cx()
            time.sleep(3)
        # Quisce cx
        else:
            ip_var_test.stop()

    # Results
    csv_results_file = ip_var_test.get_results_csv()
    report.set_title("Test Layer 3 Cross-Connect Traffic: test_l3.py ")
    report.build_banner_left()
    report.start_content_div2()

    report.set_obj_html("Objective", "The Layer 3 Traffic Generation Test is designed to test the performance of the "
                        "Access Point by running layer 3 Cross-Connect Traffic.  Layer-3 Cross-Connects represent a stream "
                        "of data flowing through the system under test. A Cross-Connect (CX) is composed of two Endpoints, "
                        "each of which is associated with a particular Port (physical or virtual interface).")

    report.build_objective()

    test_setup_info = {
        "DUT Name": args.dut_model_num,
        "DUT Hardware Version": args.dut_hw_version,
        "DUT Software Version": args.dut_sw_version,
        "DUT Serial Number": args.dut_serial_num,
    }

    report.set_table_title("Device Under Test Information")
    report.build_table_title()
    report.test_setup_table(value="Device Under Test",
                            test_setup_data=test_setup_info)

    test_input_info = {
        "LANforge ip": args.lfmgr,
        "LANforge port": args.lfmgr_port,
        "Upstream": args.upstream_port,
        "Test Duration": args.test_duration,
        "Polling Interval": args.polling_interval,
    }

    report.set_table_title("Test Configuration")
    report.build_table_title()
    report.test_setup_table(value="Test Configuration",
                            test_setup_data=test_input_info)

    report.set_table_title("Radio Configuration")
    report.build_table_title()

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
        15: '802.11aAX'  # 802.11a-AX (6E disables /n and /ac)
    }

    for (
            radio_,
            ssid_,
            ssid_password_,  # do not print password
            ssid_security_,
            mode_,
            wifi_enable_flags_list_,
            reset_port_enable_,
            reset_port_time_min_,
            reset_port_time_max_) in zip(
            radio_name_list,
            ssid_list,
            ssid_password_list,
            ssid_security_list,
            wifi_mode_list,
            wifi_enable_flags_list,
            reset_port_enable_list,
            reset_port_time_min_list,
            reset_port_time_max_list):

        mode_value = wifi_mode_dict[int(mode_)]

        radio_info = {
            "SSID": ssid_,
            "Security": ssid_security_,
            "Wifi mode set": mode_value,
            'Wifi Enable Flags': wifi_enable_flags_list_
        }
        report.test_setup_table(value=radio_, test_setup_data=radio_info)

    # TODO move the graphing to the class so it may be called as a service

    # Graph TOS data
    # Once the data is stopped can collect the data for the cx's both multi cast and uni cast
    # if the traffic is still running will gather the running traffic
    ip_var_test.evaluate_qos()

    # graph BK A
    # try to do as a loop
    tos_list = ['BK','BE','VI','VO']

    for tos in tos_list:
        if (ip_var_test.client_dict[tos]["ul_A"]  and ip_var_test.client_dict[tos]["dl_A"]):
            min_bps_a = ip_var_test.client_dict["min_bps_a"]
            min_bps_b = ip_var_test.client_dict["min_bps_b"]

            dataset_list = [ip_var_test.client_dict[tos]["ul_A"], ip_var_test.client_dict[tos]["dl_A"]]
            # TODO possibly explain the wording for upload and download
            dataset_length = len(ip_var_test.client_dict[tos]["ul_A"])
            x_fig_size = 15
            y_fig_size = len(ip_var_test.client_dict[tos]["clients_A"]) * .4 + 3


            report.set_obj_html(
                _obj_title=f"Individual throughput measured at download endpoint with intended load upload bps: {min_bps_a} download bps: {min_bps_b} station for traffic {tos} (WiFi).",
                _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                    f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                    f"Throughput in Mbps”.")
            report.build_objective()


            graph= lf_graph.lf_bar_graph_horizontal(_data_set=dataset_list,
                                _xaxis_name="Throughput in bps",
                                _yaxis_name="Client names",
                                _yaxis_categories=ip_var_test.client_dict[tos]["clients_A"],
                                _graph_image_name=f"{tos}_A",
                                _label=ip_var_test.client_dict[tos]['labels'],
                                _color_name=ip_var_test.client_dict[tos]['colors'],
                                _color_edge=['black'],
                                _graph_title=f"Individual {tos} client side traffic measurement - side a (downstream)", # traditional station side -A
                                _title_size=10,
                                _figsize=(x_fig_size,y_fig_size),
                                _show_bar_value= True,
                                _enable_csv=True,
                                _text_font=8,
                                _legend_loc="best",
                                _legend_box=(1.0,1.0)
                                )
            graph_png = graph.build_bar_graph_horizontal()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()



            bk_dataframe = {
                " Client Name " : ip_var_test.client_dict['BK']['resourse'],
                " Mode " : ip_var_test.client_dict['BK']['mode'],
                " Mac " : ip_var_test.client_dict['BK']['mac'],
                " Channel " : ip_var_test.client_dict['BK']['channel'],
                " Type of traffic " : ip_var_test.client_dict['BK']['traffic_type']
                #" Traffic Protocol " : 
            }

            '''
            bk_dataframe = {
                " Client Name " : self.sta_list,
                " Mac " : self.mac_list,
                " Channel " : self.channel_list,
                " Type of traffic " : bk_tos_list,
                " Traffic Direction " : traffic_direction_list,
                " Traffic Protocol " : traffic_type_list,
                " Offered upload rate(Mbps) " : upload_list,
                " Offered download rate(Mbps) " : download_list,
                " Observed upload rate(Mbps) " : individual_upload_list,
                " Observed download rate(Mbps)" : individual_download_list
            }
        '''

            dataframe3 = pd.DataFrame(bk_dataframe)
            report.set_table_dataframe(dataframe3)
            report.build_table()



    for tos in tos_list:
        if (ip_var_test.client_dict[tos]["ul_B"] and ip_var_test.client_dict[tos]["dl_B"]):
            min_bps_a = ip_var_test.client_dict["min_bps_a"]
            min_bps_b = ip_var_test.client_dict["min_bps_b"]

            dataset_list = [ip_var_test.client_dict[tos]["ul_B"], ip_var_test.client_dict[tos]["dl_B"]]
            dataset_length = len(ip_var_test.client_dict[tos]["ul_B"])

            x_fig_size = 15
            y_fig_size = len(ip_var_test.client_dict[tos]["clients_B"]) * .4 + 3

            report.set_obj_html(
                _obj_title=f"Individual throughput upstream endp,  offered upload bps: {min_bps_a} offered download bps: {min_bps_b} /station for traffic {tos} (WiFi).",
                _obj=f"The below graph represents individual throughput for {dataset_length} clients running {tos} "
                    f"(WiFi) traffic.  Y- axis shows “Client names“ and X-axis shows “"
                    f"Throughput in Mbps”.")
            report.build_objective()


            graph= lf_graph.lf_bar_graph_horizontal(_data_set=dataset_list,
                                _xaxis_name="Throughput in bps",
                                _yaxis_name="Client names",
                                _yaxis_categories=ip_var_test.client_dict[tos]["clients_B"],
                                _graph_image_name=f"{tos}_B",
                                _label=ip_var_test.client_dict[tos]['labels'],
                                _color_name=ip_var_test.client_dict[tos]['colors'],
                                _color_edge=['black'],
                                _graph_title=f"Individual {tos} upstream side traffic measurement - side b (WIFI) traffic",
                                _title_size=10,
                                _figsize=(x_fig_size,y_fig_size),
                                _show_bar_value= True,
                                _enable_csv=True,
                                _text_font=8,
                                _legend_loc="best",
                                _legend_box=(1.0,1.0)
                                )
            graph_png = graph.build_bar_graph_horizontal()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()


    # create graph


    # L3 total traffic
    report.set_table_title(
        "Total Layer 3 Cross-Connect Traffic across all Stations")
    report.build_table_title()
    report.set_table_dataframe_from_csv(csv_results_file)
    report.build_table()

    # empty dictionarys evaluate to false , placing tables in output
    if bool(ip_var_test.dl_port_csv_files):
        for key, value in ip_var_test.dl_port_csv_files.items():
            if args.csv_data_to_report:
                # read the csv file
                report.set_table_title("Layer 3 Cx Traffic  {key}".format(key=key))
                report.build_table_title()
                report.set_table_dataframe_from_csv(value.name)
                report.build_table()

            # read in column heading and last line
            df = pd.read_csv(value.name)
            last_row = df.tail(1)
            report.set_table_title(
                "Layer 3 Cx Traffic Last Reporting Interval {key}".format(key=key))
            report.build_table_title()
            report.set_table_dataframe(last_row)
            report.build_table()
    report.write_report_location()
    report.write_html_with_timestamp()
    report.write_index_html()
    # report.write_pdf(_page_size = 'A3', _orientation='Landscape')
    # report.write_pdf_with_timestamp(_page_size='A4', _orientation='Portrait')
    if platform.system() == 'Linux':
        report.write_pdf_with_timestamp(
            _page_size='A3', _orientation='Landscape')

    # TODO move to after reporting
    if not ip_var_test.passes():
        logger.warning("Test Ended: There were Failures")
        logger.warning(ip_var_test.get_fail_message())

    if args.no_cleanup or args.no_stop_traffic:
        logger.info(
            "--no_cleanup or --no_stop_traffic set stations will be left intack")
    else:
        ip_var_test.cleanup()

    if args.cleanup_cx:
        logger.info("cleaning layer 3 cx")
        ip_var_test.cleanup_cx()

    if ip_var_test.passes():
        test_passed = True
        logger.info("Full test passed, all connections increased rx bytes")


    if test_passed:
        ip_var_test.exit_success()
    else:
        ip_var_test.exit_fail()


if __name__ == "__main__":
    main()
